# Matrix for Claude Code

Claude Code can grep code, but it cannot search PDFs, Word files, scans or charts by meaning. Matrix gives
it a local semantic index over your document folders, with citations to file, page and passage, tables
over many documents and a knowledge graph — everything runs on your computer, and Claude Code itself is
the language model, so no extra model or API key is needed. [DEMO.md](DEMO.md) compares it with Claude Code
alone on 442 pages of public documents.

## Install

Requires a Mac with Apple silicon (macOS, arm64) for now.

```
claude plugin marketplace add matthiasnordwig/matrix-mcp
claude plugin install matrix@matrix-mcp
```

Then, in Claude Code, run `/plugin`, select **matrix**, choose **Configure** and set:

- **Folders Claude may read** — the folders with your documents (not your whole home folder). Matrix
  reads only files inside them and never changes or deletes them.
- **Search model** — leave `embeddinggemma-2` (multilingual, also searches charts and scans). The first
  time it is needed Claude tells you the size (about 1.2 GB, from Hugging Face, once) and asks before
  downloading. Alternatives: `embeddinggemma-2-q4` (0.2 GB, text only), `onnx-folder:/path` (a model you
  already have), `endpoint:https://host/v1#model` (your own embedding service).
- **Embedding endpoint API key** — only for an `endpoint:` search model.

The plugin loads the program from the release as `matrix-standalone.mcpb` (about 22 MB). Its index and
models live in `~/Library/Application Support/Matrix MCP`.

## Use

| Command | What it does |
|---|---|
| `/matrix:index <folder>` | Index a folder into a collection (PDF incl. scans and charts, Word, Excel, PowerPoint, Markdown, text, images) |
| `/matrix:ask <question>` | Answer from the documents with citations (file, page, passage), checked against the text |
| `/matrix:table <question>` | The same question over many documents or passages, as a table with a source per cell |
| `/matrix:graph [topic]` | Build or explore the knowledge graph: entities, relations, themes, with evidence |
| `/matrix:search-model` | Check the search model against its recommendation date, look for better ones |

You can also just ask; Claude picks the matching skill. The server also offers its own prompts
(type `/` and look for `index_and_ask`, `compare_documents`, `explore_graph`, …).

For tables and the knowledge graph Matrix hands Claude small model tasks (`llm_tasks`, answered with
`llm_answer`); with many tasks Claude can answer them through parallel subagents. These tasks use your
Claude Code session like any other work you ask for.

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
