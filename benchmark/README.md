# Benchmark: Claude Code alone vs. with Matrix

The test set, script and raw results behind [DEMO.md](../DEMO.md): the same four questions over the same
public documents, answered by Claude Code alone (**A**) and by Claude Code with this plugin (**B**).

| File | Content |
|---|---|
| `bench_claude_plugin.py` | The script: download the corpus, index it, probe the search without Claude, run A/B, print the table |
| `questions.json` | Corpus sources (with SHA-256 of the files measured), the four questions, gold answers, gold pages, scoring patterns |
| `results-2026-11-19.jsonl` | Raw results of the measurement of 2026-11-19, one line per run (16 runs) |
| `probe-2026-11-19.json` | Search hits per question without Claude, same index and day |

## What is measured

- **Corpus** (442 pages, not in this repository; `fetch` downloads it): DORA (Regulation (EU) 2022/2554),
  the AI Act (2024/1689) and the GDPR (2016/679) in their **German** versions from the EU Publications Office,
  and the **English** ENISA Threat Landscape 2024 (CC BY 4.0), whose numbers sit in charts. `fetch` says
  whether each file is the same as the one measured; a new rendering of a PDF can shift pages.
- **Questions** (fixed with their answers and pages before any run): an English paraphrase of German text
  (Q1, DORA), a value that exists only in a chart (Q2, ENISA), an answer spread over three acts (Q3), an
  English paraphrase in a single act (Q4). Pages are PDF pages, 1 = first page of the file.
- **A:** `claude -p` with the tools `Read`, `Grep`, `Glob`, and `Bash` allowed only for `pdftotext`.
  **B:** the same plus the plugin (`--plugin-dir`) with its read tools approved. Same prompt for both: answer
  from the files, short answer, file name and PDF page for every fact, not from memory.
- Every run: `--output-format stream-json --verbose`, empty working directory, the PDF folder added with
  `--add-dir`, only project settings (`--setting-sources project`, so your own settings, plugins and
  CLAUDE.md stay out), no session saved. Indexing runs once before the B runs and is reported separately.

## How the numbers are counted

From the final result object Claude Code prints for each run:

- **Input tokens** = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`. Most are
  cache reads (A 93 %, B 86 % in this measurement); `cache_read_tokens` is kept as its own field.
- **Output tokens** = `output_tokens`.
- **Time** = `duration_ms` (Claude Code's own measure; `wall_s` is the script's clock including start-up).
- **Tool calls** = `tool_use` blocks in the stream (`tools` lists them, `queries` the search terms).
- `cost_usd` is what Claude Code reports at API prices; it is in the raw data but not used in the tables.

## Scoring

The script scores each answer automatically: `correct` = every pattern in `must` matches, `cited_ok` = each
gold file is named together with one of its gold pages. This is a lenient first pass; the published figures
were **checked by hand**. One known difference: the script marks both B answers to Q3 as wrong because its
patterns are English and the answers came in German; their content (72 h, 15 days, 2 and 10 days, DORA
without fixed hours, right pages) is correct. A's first answer to Q2 is wrong in both scorings (15.87 % from
another chart instead of 19.01 %).

## Results of 2026-11-19

Claude Code 2.1.309, model Sonnet, plugin 0.2.9; index 1,745 passages in 277 s on an Apple-silicon Mac;
two runs per question and configuration; mean per run, correctness by hand:

| Config | Correct | Ø input tokens | Ø output tokens | Ø tool calls | Ø time s |
|---|---|---|---|---|---|
| A — Claude Code alone | 7/8 | 1,025 k | 3.9 k | 14.4 | 48 |
| B — with Matrix | 8/8 | 182 k | 1.6 k | 7.9 | 20 |

Per question and with the reading of the results: [DEMO.md](../DEMO.md). The per-question table with the
automatic scores comes straight from the raw data:

```
python3 bench_claude_plugin.py report --results results-2026-11-19.jsonl
```

The raw results contain no local paths or personal data; nothing had to be removed. The earlier measurement
of 2026-10-22 (DEMO.md) was not kept as raw data.

## Run it yourself

Needs Python 3.9+, Node.js 18+ (for `npx`), Claude Code logged in, and `pdftotext` (poppler) for A.
From this folder (the plugin is the folder above it; its server is the published npm package):

```
python3 bench_claude_plugin.py fetch  --corpus ~/matrix-bench/corpus   # new, empty folder
python3 bench_claude_plugin.py index  --corpus ~/matrix-bench/corpus --bench ~/matrix-bench/run
python3 bench_claude_plugin.py probe  --bench ~/matrix-bench/run        # search only, no Claude
python3 bench_claude_plugin.py run    --bench ~/matrix-bench/run        # 16 runs, about 10 min
python3 bench_claude_plugin.py report --bench ~/matrix-bench/run
```

- `index` starts the program the plugin starts (`npx -y @matthiasnordwig/matrix-mcp@<version>`) with its own
  data folder and HOME under `--bench`, so your own Matrix data stay untouched. Without `--onnx` it downloads
  the plugin's default search model, EmbeddingGemma 2 (about 1.2 GB, once per bench folder); with
  `--onnx DIR` it uses an existing ONNX folder (`model.onnx` + `tokenizer.json`) and downloads nothing.
- `run` uses your Claude Code login and counts against your usage. `--runs`, `--configs A`,
  `--questions Q1,Q3` and `--model` narrow or change it; results are appended to `results.jsonl`.
- Another build: `--plugin DIR` takes another plugin folder, and `MATRIX_MCP_BIN=/path/to/matrix-mcp-stdio`
  makes `index` and `probe` start that program instead of the plugin's `npx` command; index and runs should
  use the same program.

## Limits

- Two runs per question and configuration; run-to-run differences of 10–20 % are normal. In the raw file both
  A rounds carry `"run": 1` (two separate invocations); they are the two A runs.
- One model (Sonnet), one Claude Code version (2.1.309), one machine. Claude Code alone got much faster between
  the October measurement (126 s per question) and this one (48 s), so the gap depends on the version.
- The second A round ran on the morning of 2026-11-19 while a website build ran on the same Mac; its times may
  be slightly too high, the tokens are unaffected.
- B used the 0.2.9 npm packages installed from local tarballs shortly before they were published; a `probe`
  with the published 0.2.9 package returns the same hits.
- A first attempt that ran the configurations in parallel was discarded (shared machine, times not
  comparable) and is not included.
- Four questions over 442 pages are a small set, and they are known: after a miss on Q2 in October the
  plugin's `ask` skill was changed. DEMO.md has a second, larger test of the search.
