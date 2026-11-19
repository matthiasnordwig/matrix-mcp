#!/usr/bin/env python3
"""A/B benchmark: Claude Code alone vs. Claude Code with the Matrix plugin.

The measurement behind DEMO.md (method, results, limits: README.md next to this file). Same questions
over the same public PDF corpus (three EU regulations in German, an ENISA report whose numbers sit in
charts), answered
  A  by Claude Code alone (Read, Grep, Glob, Bash only for pdftotext), and
  B  by Claude Code with the plugin.
Corpus sources, questions, gold answers and gold pages: questions.json next to this file.

Each run is `claude -p --output-format stream-json --verbose` (the final line is the same result object
as `--output-format json`; the stream adds the tool calls to count). Recorded per run: tokens, duration,
tool calls, answer; auto-scored against the gold answers (keywords + cited pages; check by hand).

The plugin is the folder given with --plugin (default: the plugin this file belongs to, whose server
is the published npm package `npx -y @matthiasnordwig/matrix-mcp@<version>`). Its server command from
.claude-plugin/plugin.json also indexes and probes, so the index and the runs use the same program;
MATRIX_MCP_BIN replaces it by a program path (e.g. a self-built matrix-mcp-stdio). The program runs with
its own data folder and HOME under --bench. Indexing happens once, before the runs, and is measured
separately. Search model: an existing ONNX folder (--onnx, nothing downloaded) or, without it, the
plugin's default EmbeddingGemma 2 (one-time download of about 1.2 GB into the bench folder).
This script starts `claude` only as the tester, never from the plugin or the program.

Needs: Python 3.9+, Node.js 18+ (npx), Claude Code (logged in), pdftotext (poppler) for config A.

Usage (the corpus folder must be new/empty; the bench folder holds state, index and results):
  python3 bench_claude_plugin.py fetch  --corpus DIR
  python3 bench_claude_plugin.py index  --corpus DIR --bench DIR [--onnx MODEL_DIR] [--plugin DIR]
  python3 bench_claude_plugin.py probe  --bench DIR [--plugin DIR]   # search hits per question, no Claude
  python3 bench_claude_plugin.py run    --bench DIR [--plugin DIR] [--configs A,B] [--runs 2] [--model sonnet] [--questions Q1,Q3]
  python3 bench_claude_plugin.py report --bench DIR | --results FILE  # Markdown table from a results file
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent  # the plugin folder this benchmark ships in
SERVER = "matrix-standalone"  # server name in the plugin (= name in the .mcpb manifest)
TOOL = f"mcp__plugin_matrix_{SERVER}__"
DEFAULT_MODEL = "embeddinggemma-2"  # the plugin's default search model (MATRIX_MCP_EMBEDDING)
DATA = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
COLLECTION, CORPUS, QUESTIONS = DATA["collection"], DATA["corpus"], DATA["questions"]

BASE_TOOLS = ["Read", "Grep", "Glob", "Bash(pdftotext:*)"]
MATRIX_TOOLS = ["list_contexts", "list_documents", "search_context", "lookup_exact", "get_chunks",
                "get_page_image", "get_section", "verify_citations"]
CONFIGS = {
    # --tools limits the built-in tools (same set for both); --allowedTools approves them.
    "A": {"tools": "Read,Grep,Glob,Bash", "allowed": BASE_TOOLS},
    "B": {"tools": "Read,Grep,Glob,Bash,ToolSearch,Skill", "allowed": BASE_TOOLS + [TOOL + t for t in MATRIX_TOOLS]},
}


def fetch(corpus: Path) -> None:
    """Download the corpus (Publications Office content negotiation: eur-lex.europa.eu answers
    scripts with a bot check) and compare each file with the one measured."""
    corpus.mkdir(parents=True, exist_ok=True)
    if any(corpus.iterdir()):
        sys.exit(f"{corpus} is not empty: downloads go into a new, empty folder")
    for name, src in CORPUS.items():
        req = urllib.request.Request(src["url"], headers={"User-Agent": "matrix-bench", **src["headers"]})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if not data.startswith(b"%PDF"):
            sys.exit(f"{name}: not a PDF from {src['url']}")
        (corpus / name).write_bytes(data)
        same = hashlib.sha256(data).hexdigest() == src["sha256"]
        print(f"{name}: {len(data)} bytes, {'same file as measured' if same else 'DIFFERS from the file measured (pages may shift)'}")


def server_cmd(plugin: Path) -> list:
    """The program the plugin starts (MATRIX_MCP_BIN: a program path instead)."""
    if os.environ.get("MATRIX_MCP_BIN"):
        return [os.environ["MATRIX_MCP_BIN"]]
    (srv,) = json.loads((plugin / ".claude-plugin/plugin.json").read_text())["mcpServers"].values()
    return [shutil.which(srv["command"]) or srv["command"], *srv.get("args", [])]


class Server:
    """matrix-mcp-stdio over JSON-RPC lines (the same protocol Claude Code speaks)."""

    def __init__(self, plugin: Path, env: dict):
        self.p = subprocess.Popen(server_cmd(plugin), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, env={**os.environ, **env}, text=True)
        self.n = 0
        init = self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                           "clientInfo": {"name": "bench", "version": "0"}})
        info = init.get("result", {}).get("serverInfo", {})
        self.info = f"{info.get('name', '?')} {info.get('version', '?')}"
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg: dict) -> None:
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                sys.exit("the Matrix program closed its output")
            msg = json.loads(line)
            if msg.get("id") == self.n:
                return msg

    def call(self, tool: str, args: dict):
        res = self.request("tools/call", {"name": tool, "arguments": args})["result"]
        text = self.last_text = res["content"][0]["text"]  # what the client shows the model
        if res.get("isError"):
            raise RuntimeError(f"{tool}: {text}")
        return res.get("structuredContent") or json.loads(text)

    def wait(self, job: str) -> dict:
        while True:
            st = self.call("job_status", {"job_id": job})
            if st.get("state") != "running":
                return st
            time.sleep(2)

    def close(self) -> None:
        self.p.stdin.close()
        self.p.wait(timeout=30)


def program_env(state: dict) -> dict:
    model = f"onnx-folder:{state['onnx']}" if state.get("onnx") else DEFAULT_MODEL
    return {"MATRIX_MCP_DATA_DIR": state["data"], "MATRIX_MCP_HOME": state["home"], "HOME": state["home"],
            "MATRIX_MCP_ALLOWED_DIRS": state["corpus"], "MATRIX_MCP_EMBEDDING": model}


def start(plugin: Path, state: dict) -> Server:
    """The program for index/probe: own HOME instead of MATRIX_MCP_HOME."""
    return Server(plugin, {k: v for k, v in program_env(state).items() if k != "MATRIX_MCP_HOME"})


def load_state(bench: Path) -> dict:
    return json.loads((bench / "state.json").read_text())


def index(corpus: Path, bench: Path, onnx, plugin: Path) -> None:
    """Index the corpus into a fresh data folder under `bench`."""
    bench.mkdir(parents=True, exist_ok=True)
    state = {"corpus": str(corpus.resolve()), "onnx": str(onnx.resolve()) if onnx else None,
             "data": str((bench / "program-data").resolve()), "home": str((bench / "program-home").resolve())}
    for d in ("data", "home"):
        shutil.rmtree(state[d], ignore_errors=True)
        Path(state[d]).mkdir(parents=True)
    s = start(plugin, state)
    print(f"program: {s.info}")
    if not onnx:  # download the default model first; this call is the consent (measured separately)
        t0 = time.time()
        job = s.call("setup_embedding_model", {}).get("job_id")
        print(f"search model: {s.wait(job).get('state') if job else 'already there'}, {time.time() - t0:.0f} s")
    t0 = time.time()
    ctx = s.call("create_context", {"name": COLLECTION, "chunking_strategy": "structural"})
    cid = ctx.get("id") or ctx.get("context_id")
    st = s.wait(s.call("add_files", {"context_id": cid, "path": state["corpus"]})["job_id"])
    state.update(program=s.info, context_id=cid, index_seconds=round(time.time() - t0, 1), index_job=st)
    s.close()
    (bench / "state.json").write_text(json.dumps(state, indent=2))
    print(json.dumps({"seconds": state["index_seconds"], "job": st}, indent=2)[:3000])


def first_page(hit: dict):
    """Start page of a search hit: older programs send `page`, newer ones `pages` (list or "45-46")."""
    if "page" in hit:
        return hit["page"]
    pages = hit.get("pages")
    if isinstance(pages, list):
        return pages[0] if pages else "?"
    return str(pages).split("-")[0] if pages else "?"


def probe(bench: Path, plugin: Path) -> None:
    """Search hits without Claude: the question as asked, then the `probe` queries (worded like the
    documents, as the `ask` skill tells Claude to search). Prints the rank of the first gold page."""
    state = load_state(bench)
    s = start(plugin, state)
    print(f"program: {s.info}")
    out = []
    for q in QUESTIONS:
        gold = {f"{f} p{p}" for f in os.listdir(state["corpus"]) for d, ps in q["pages"].items()
                if f.startswith(d) for p in ps}
        for query in [q["text"], *q["probe"]]:
            t0 = time.time()
            hits = s.call("search_context", {"context_ids": [state["context_id"]], "query": query, "top_k": 8})
            ms = round((time.time() - t0) * 1000)
            found = [f"{h.get('file', '?')} p{first_page(h)}" for h in hits.get("hits") or hits.get("chunks") or []]
            rank = next((i + 1 for i, h in enumerate(found) if h in gold), None)
            out.append({"id": q["id"], "query": query, "ms": ms, "gold_rank": rank, "hits": found})
            print(f"{q['id']} [{query[:50]}] {ms} ms, first gold page at rank {rank}: {', '.join(found[:5])}")
    s.close()
    (bench / "probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


def prompt(config: str, q: dict, state: dict) -> str:
    where = (f"the PDF files in the folder {state['corpus']}" if config == "A" else
             f"the documents indexed in the Matrix collection \"{COLLECTION}\" (the PDF files in {state['corpus']})")
    return (f"Answer this question from {where}.\n\nQuestion: {q['text']}\n\n"
            "Give a short answer and, for every fact, its source as file name and PDF page number "
            "(1 = first page of the file). Do not answer from memory.")


def run_one(config: str, q: dict, state: dict, plugin: Path, model: str, claude: str, work: Path) -> dict:
    cfg = CONFIGS[config]
    cmd = [claude, "-p", prompt(config, q, state), "--output-format", "stream-json", "--verbose",
           "--model", model, "--tools", cfg["tools"], "--allowedTools", *cfg["allowed"],
           "--setting-sources", "project", "--no-session-persistence",
           "--add-dir", state["corpus"]]  # the PDFs are readable for both configurations
    if config == "B":
        cmd += ["--plugin-dir", str(plugin)]
    # Claude Code keeps its own HOME (its login); the program gets its HOME via MATRIX_MCP_HOME.
    env = {**os.environ, **{k: v for k, v in program_env(state).items() if k != "HOME"}}
    t0 = time.time()
    p = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=1800)
    events = [json.loads(line) for line in p.stdout.splitlines() if line.startswith("{")]
    calls = [c["name"] for e in events if e.get("type") == "assistant"
             for c in e["message"].get("content", []) if c.get("type") == "tool_use"]
    queries = [c["input"].get("query") or c["input"].get("term") or c["input"].get("pattern")
               for e in events if e.get("type") == "assistant" for c in e["message"].get("content", [])
               if c.get("type") == "tool_use" and c["name"].split("__")[-1] in ("search_context", "lookup_exact", "Grep")]
    final = next((e for e in reversed(events) if e.get("type") == "result"), {})
    u = final.get("usage", {})
    answer = final.get("result", "") or p.stderr[-2000:]
    return {"config": config, "question": q["id"], "model": model, "wall_s": round(time.time() - t0, 1),
            "duration_ms": final.get("duration_ms"), "cost_usd": final.get("total_cost_usd"),
            "input_tokens": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            + u.get("cache_read_input_tokens", 0), "cache_read_tokens": u.get("cache_read_input_tokens", 0),
            "output_tokens": u.get("output_tokens"), "queries": queries,
            "turns": final.get("num_turns"), "tool_calls": len(calls), "tools": calls,
            "is_error": final.get("is_error", True), **score(q, answer), "answer": answer}


def score(q: dict, answer: str) -> dict:
    """Facts: every `must` regex. Citation: each gold file is named and one of its gold pages appears
    as a page reference ("p. 46", "page 46", "pp. 42-43", "S. 46") anywhere in the answer - a lenient
    rule (answers list sources in many layouts), so the table is checked by hand as well."""
    text = answer.lower()
    hits = [bool(re.search(r, text, re.I)) for r in q["must"]]
    pages = set()
    for a, b in re.findall(r"(?:pp?\.|pages?|seiten?|s\.)\s*(\d+)(?:\s*[-–]\s*(\d+))?", text):
        pages.update(range(int(a), int(b or a) + 1))
    cited = {doc: doc in text and bool(pages & set(ps)) for doc, ps in q["pages"].items()}
    return {"correct": all(hits), "facts": f"{sum(hits)}/{len(hits)}", "cited_ok": all(cited.values())}


def run(bench: Path, plugin: Path, configs: list, runs: int, model: str, claude: str, only: str) -> None:
    state = load_state(bench)
    work = bench / "workdir"  # empty cwd: no project CLAUDE.md, no repo files to grep
    work.mkdir(exist_ok=True)
    with open(bench / "results.jsonl", "a") as f:
        for q in [q for q in QUESTIONS if not only or q["id"].split("-")[0] in only.split(",")]:
            for config in configs:
                for i in range(runs):
                    r = run_one(config, q, state, plugin.resolve(), model, claude, work)
                    r["run"] = i + 1
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f.flush()
                    print(f"{q['id']} {config}#{i + 1}: correct={r['correct']} cited={r['cited_ok']} "
                          f"tokens={r['input_tokens']}/{r['output_tokens']} "
                          f"tools={r['tool_calls']} {r['duration_ms']} ms")


def report(results: Path) -> None:
    rows = [json.loads(line) for line in open(results, encoding="utf-8")]
    by_id = {q["id"]: q for q in QUESTIONS}
    for r in rows:  # re-score with the current rules
        r.update(score(by_id[r["question"]], r["answer"]))
    print("| Question | Config | Runs | Correct (auto) | Citation ok | Ø input tok | Ø output tok | Ø tool calls | Ø time s |")
    print("|---|---|---|---|---|---|---|---|---|")
    for q in QUESTIONS:
        for c in CONFIGS:
            rs = [r for r in rows if r["question"] == q["id"] and r["config"] == c]
            if not rs:
                continue
            avg = lambda k: sum((r[k] or 0) for r in rs) / len(rs)  # noqa: E731
            print(f"| {q['id']} | {c} | {len(rs)} | {sum(r['correct'] for r in rs)}/{len(rs)} | "
                  f"{sum(r['cited_ok'] for r in rs)}/{len(rs)} | {avg('input_tokens'):,.0f} | "
                  f"{avg('output_tokens'):,.0f} | {avg('tool_calls'):.1f} | {avg('duration_ms') / 1000:.0f} |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["fetch", "index", "probe", "run", "report"])
    ap.add_argument("--corpus", type=Path)
    ap.add_argument("--bench", type=Path)
    ap.add_argument("--plugin", type=Path, default=PLUGIN, help="plugin folder (default: %(default)s)")
    ap.add_argument("--onnx", type=Path, help="existing ONNX model folder; default: download EmbeddingGemma 2")
    ap.add_argument("--results", type=Path, help="report: results file (default: BENCH/results.jsonl)")
    ap.add_argument("--configs", default="A,B")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--claude", default="claude")
    ap.add_argument("--questions", default="", help="only these, e.g. Q1,Q3")
    a = ap.parse_args()
    if a.step == "fetch":
        fetch(a.corpus)
    elif a.step == "index":
        index(a.corpus, a.bench, a.onnx, a.plugin)
    elif a.step == "probe":
        probe(a.bench, a.plugin)
    elif a.step == "run":
        run(a.bench, a.plugin, a.configs.split(","), a.runs, a.model, a.claude, a.questions)
    else:
        report(a.results or a.bench / "results.jsonl")


if __name__ == "__main__":
    main()
