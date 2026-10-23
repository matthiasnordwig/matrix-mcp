# Matrix for Claude Code

Claude Code can grep code, but it cannot search PDFs, Word files, scans or charts by meaning. Matrix gives
it a local semantic index over your document folders, with citations to file, page and passage, cross-references
between provisions and tables over many documents — everything runs on your computer, and Claude Code itself is
the language model, so no extra model or API key is needed. [DEMO.md](DEMO.md) compares it with Claude Code
alone on 442 pages of public documents.

## Why use it

Measured on 442 pages of EU regulations and a report (4 questions, 2 runs each, Claude Code alone vs. with the plugin):

- **A fraction of the time on large document sets.** On average 42 s instead of 126 s per question (about 3×; 2–4× depending on the question), with less than half the tool calls (9.5 instead of 21.4) and about a quarter lower cost ($0.40 instead of $0.53; equal for a question about one single provision). The gap grows with the number of documents a question touches.
- **Index once, ask many times.** Indexing runs once on your computer and costs no Claude tokens; the index stays across sessions. Every further question about the same documents is then faster and cheaper — on average 42 s instead of 126 s, about a quarter cheaper (DEMO.md). This pays off when there are many or long documents, further questions about the same set are likely and answers should come with evidence — for example contracts, regulations, project files, technical manuals, studies, minutes or reports. For a one-off question Claude may search the files itself, and says so when an answer has no evidence from your files.
- **Citations with file, page and passage, checked against the text.** Every correct answer in the test cited the right pages.
- **Finds paraphrases, scans and charts.** Search is by meaning, so a question in other words than the text still finds the provision, and a value that exists only in a chart is found on the chart page. In folders that mix languages, search works best in the documents' language; the skills tell Claude to search in it too.
- **Tables over many documents.** One question put to every document or passage, as a table with a source per cell.
- **Everything local, no extra model access.** Index and search run on your computer; Claude Code itself is the language model, so no second model or API key is needed.
- **The full numbers** are in [DEMO.md](DEMO.md). Claude Code alone answered all questions correctly too (8/8); with the plugin one answer in the first runs was wrong (a chart label too small to read), fixed in the `ask` skill, then 4/4 correct. The gain is effort, not correctness.

It brings little for small, well-structured collections that Claude Code reads quickly anyway: one short document is answered just as well without it, and indexing costs minutes once per folder.

## Install

Requires a Mac with Apple silicon (macOS, arm64) and Node.js 18 or later (for `npx`) for now.

```
claude plugin marketplace add matthiasnordwig/matrix-mcp
claude plugin install matrix@matrix-mcp
```

Then start `claude` (best in the folder with your documents) and just ask Claude about your documents — it sets Matrix up with you the first time (or run `/matrix:setup`). You do not need to read anything else.

## How it works

- Documents are split along their own structure — PDF layout, headings, articles, tables — not by a language model (the semantic chunker is not the default).
- Search is by meaning plus keywords, and follows cross-references between provisions; scans and charts are found too.
- Every answer cites file, page and passage, and the citations are checked against the text.
- Tables over many documents hand small model tasks to Claude through a queue (`llm_tasks` / `llm_answer`); they run in your Claude Code session and use your Claude quota.
- Index, models and the list of allowed folders live in `~/Library/Application Support/Matrix MCP`; nothing leaves your computer except the passages Claude reads.
- Matrix reads the folder you started Claude Code in; for any other folder it asks you (Accept / Decline) and remembers your answer.
- `/matrix:status` shows what Matrix holds and does at any time.

## Use

| Command | What it does |
|---|---|
| `/matrix:setup` | Guided first start: folder, search model, indexing, example questions |
| `/matrix:status` | What Matrix holds and does: collections, search model, allowed folders, waiting model tasks, running jobs |
| `/matrix:index <folder>` | Index a folder into a collection (PDF incl. scans and charts, Word, Excel, PowerPoint, Markdown, text, images) |
| `/matrix:ask <question>` | Answer from the documents with citations (file, page, passage), checked against the text |
| `/matrix:table <question>` | The same question over many documents or passages, as a table with a source per cell |
| `/matrix:search-model` | Check the search model against its recommendation date, look for better ones |

You can also just ask; Claude picks the matching skill. The server also offers its own prompts
(type `/` and look for `index_and_ask`, `compare_documents`, …). Tables hand Claude small model tasks
(`llm_tasks`, answered with `llm_answer`); with many tasks Claude can answer them through parallel subagents.
They use your Claude Code session like any other work you ask for; Claude tells you the number first.

## Details

**Folders.** Matrix reads the folder where you started Claude Code. For any other folder it asks you first
(Accept / Decline) and keeps your answer until you take it back (ask Claude to revoke it). It never reads `/`, your
whole home folder, system folders, hidden folders in your home folder or `~/Library`, and never changes or
deletes your files. To always allow folders without being asked, set them when installing (several separated by
commas; a folder name must not contain a comma) — Claude Code 2.1.222 has no Configure screen under `/plugin`:

```
claude plugin install matrix@matrix-mcp --config folders=/path/one,/path/two
```

Restart Claude Code after changing settings. The same works for `--config embedding_model=...` and
`--config embedding_api_key=...`. A folder that does not exist or cannot be read is reported by name
(`/matrix:status`); on macOS the privacy protection of Documents, Desktop and Downloads can be the reason —
allow the app that runs Claude Code under System Settings › Privacy & Security › Files & Folders. The index
folder `~/Library/Application Support/Matrix MCP` must exist or be creatable and be readable and writable for
you; do not delete it while Claude Code runs.

**Search model.** Leave `embeddinggemma-2` (multilingual, also searches charts and scans). The first time it is
needed Claude tells you the size (about 1.2 GB, from Hugging Face, once) and asks before downloading.
Alternatives: `embeddinggemma-2-q4` (0.2 GB, text only), `onnx-folder:/path` (a model you already have),
`endpoint:https://host/v1#model` (your own embedding service; the API key is stored in the system keychain).
Claude Code starts the server with `npx -y @matthiasnordwig/matrix-mcp@0.2.2`: npm fetches the program once
(about 21 MB, no install script). For Claude Desktop, each
[release](https://github.com/matthiasnordwig/matrix-mcp/releases) also carries `matrix-standalone.mcpb`,
the same program as a desktop extension.

**Allow the reading tools once.** To stop Claude Code from asking before every read, add this to the
`permissions.allow` list of your `settings.json` (`~/.claude/settings.json`, or `.claude/settings.json` in a project). It lists
only tools that read the index and change nothing; wildcards like `mcp__plugin_matrix_matrix-standalone__*` exist
but would also allow reading folders and the model download, so they are not used here.

```json
{
  "permissions": {
    "allow": [
      "mcp__plugin_matrix_matrix-standalone__find_citing_chunks",
      "mcp__plugin_matrix_matrix-standalone__get_chunks",
      "mcp__plugin_matrix_matrix-standalone__get_page_image",
      "mcp__plugin_matrix_matrix-standalone__get_status",
      "mcp__plugin_matrix_matrix-standalone__grid_results",
      "mcp__plugin_matrix_matrix-standalone__job_status",
      "mcp__plugin_matrix_matrix-standalone__list_allowed_folders",
      "mcp__plugin_matrix_matrix-standalone__list_contexts",
      "mcp__plugin_matrix_matrix-standalone__list_documents",
      "mcp__plugin_matrix_matrix-standalone__list_grid_profiles",
      "mcp__plugin_matrix_matrix-standalone__list_grid_runs",
      "mcp__plugin_matrix_matrix-standalone__list_norm_references",
      "mcp__plugin_matrix_matrix-standalone__list_profiles",
      "mcp__plugin_matrix_matrix-standalone__list_sheet_tables",
      "mcp__plugin_matrix_matrix-standalone__lookup_exact",
      "mcp__plugin_matrix_matrix-standalone__page_image_status",
      "mcp__plugin_matrix_matrix-standalone__query_table",
      "mcp__plugin_matrix_matrix-standalone__search_context",
      "mcp__plugin_matrix_matrix-standalone__verify_citations"
    ]
  }
}
```

Deliberately not on the list: `setup_embedding_model` (the download), `add_files` (reads a folder), `search_embedding_models`
(asks Hugging Face with your search words) and every tool that creates or changes something.

## Terms of use

Matrix never starts `claude`, never reads your Claude credentials and serves no one else: the model tasks
are answered by the Claude Code session that started the program, in that session, by you. This keeps the
plugin within the [Claude Code usage terms](https://code.claude.com/docs/en/legal-and-compliance), which do
not allow routing other requests through your plan's credentials.

**Do not pre-approve the download tool.** Your consent to the search-model download is your approval of the
tool call `setup_embedding_model`. Do not put that tool, or all tools of this server, on the always-allowed
list, and do not run the session in a mode that approves tool calls automatically.

## Privacy Policy

Full text: [PRIVACY.md](PRIVACY.md) (<https://github.com/matthiasnordwig/matrix-mcp/blob/main/PRIVACY.md>).

In short: everything happens on your computer; the developer receives nothing (no telemetry, no update
check). Documents leave your computer only as passages Claude reads through the tools (processed by Claude
like any tool result, under Anthropic's terms), to your own embedding endpoint if you configure one, and
the one download of the search model from Hugging Face after you agree. Contact:
<https://github.com/matthiasnordwig/matrix-mcp/issues>.

## License

See [LICENSE](LICENSE).
