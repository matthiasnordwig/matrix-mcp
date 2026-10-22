# Privacy Policy — Matrix MCP

Last updated: 2026-10-22

This policy covers the **Matrix (standalone)** extension and its program `matrix-mcp-stdio`, and the
**Matrix** extension that connects Claude to the Matrix app on the same computer. Developer: Matthias
Nordwig. Contact: the issues of <https://github.com/matthiasnordwig/matrix-mcp/issues>.

## In short

Everything happens on your computer. The developer receives nothing: no documents, no search queries, no
usage data, no crash reports. There is no telemetry and no update check. Your documents leave your
computer only in the ways listed under "Sharing" below, and each of them is something you chose or approved.

## What is collected

Nothing is collected by the developer. The program itself reads only files inside the folders you share
with it (setting "Folders Claude may read"). It never deletes or changes your files.

## How the data is used

- The program reads the shared files, splits them into passages and builds a local search index
  (text, vectors, and for PDFs the pictures of graphics pages) so that Claude can search them and
  quote them with the source.
- Claude (or another MCP client) asks the program for passages, documents, tables and the knowledge
  graph; the program answers from the local index.

## Storage

- The index, the settings and downloaded models are stored only on your computer, in the program's data
  folder: `~/Library/Application Support/Matrix MCP` on macOS (`$XDG_DATA_HOME/matrix-mcp` on Linux).
  The folder is separate from the Matrix app's library.
- If you configure an embedding endpoint with an API key, the key stays on your computer, encrypted in the
  local database with a key file in the same folder, and is sent only to the endpoint you configured. A key
  entered in the plugin's settings in Claude Code is also kept by Claude Code in the system keychain.
- Diagnostic log lines go to the log of the application that started the program (on your computer). They
  contain tool names, counts and durations; long texts appear only as their length.

## Sharing

1. **Search model download (Hugging Face).** The first time search is needed, the program asks for your
   consent and then downloads the search model (EmbeddingGemma 2, about 1.2 GB; a 0.2 GB text-only variant
   exists) from huggingface.co. The download is a plain file download; no document content, account or token
   is sent. Hugging Face sees the request and your IP address and handles it under its own privacy policy.
   The tools that look for other search models (`search_embedding_models` and the model-search tools) also
   contact huggingface.co, with the search words only, and download nothing. A download happens only
   after you agreed.
2. **Optional embedding endpoint.** If you set the search model to `endpoint:…`, the text of your documents
   (and of your search queries) is sent to that service to compute vectors, and its provider's privacy policy
   applies. Without that setting nothing is sent to any embedding service.
3. **Optional language-model endpoints.** If you register a language-model endpoint with an API key, passages
   are sent to that provider when you use the features that call it. By default no such endpoint is used.
4. **Your AI client and its model.** Whatever Claude (or another client) asks the program for — search
   results, passages, table rows, graph entries — is returned to that client and is processed by its model,
   under the privacy terms of the client's provider (for Claude: Anthropic's). This includes the
   language-model tasks of the built-in bridge (`llm_tasks` / `llm_answer`): to build tables or the knowledge
   graph, the program hands passages of your documents to the client as tasks, and the client's model
   answers them. The program starts no model and no other program itself and sends these passages nowhere else.
5. **Program download (npm).** In Claude Code, the plugin starts the program with `npx`, which fetches the
   npm packages `@matthiasnordwig/matrix-mcp` and `@matthiasnordwig/matrix-mcp-darwin-arm64` from
   registry.npmjs.org once per version and keeps them in npm's cache. No document content is sent; npm sees
   the request and your IP address and handles it under its own privacy policy.
6. **Matrix app extension.** The "Matrix" extension only talks to the Matrix app on `127.0.0.1` (your own
   computer); the app's own policy applies to what the app does.

No other data leaves your computer. There are no third-party analytics, advertising or tracking services.

## Your approval of the download

The consent to the model download is the approval of the tool call `setup_embedding_model` (or, in
clients that offer it, an answer to a question dialog). It only counts if you decide on each call. In Claude
Code, do **not** put `setup_embedding_model` — or all tools of this server — on the always-allowed list and
do not run the server in a mode that approves tool calls automatically: that approves the download in
advance, and the tool can then also fetch a different model from Hugging Face without asking you.

## Retention and deletion

Data stays until you remove it. Uninstalling the extension does not delete the data folder; delete the
folder named above (or only its `models` subfolder, or the index file `matrix.db`) to remove the index and
the downloaded models. Removing a shared folder from the settings stops the program from reading it; it
does not delete what was already indexed. Documents are never uploaded for storage, so there is nothing to
delete at the developer.

## Changes and contact

Changes to this policy are published in this file with a new date. Questions, requests and reports:
<https://github.com/matthiasnordwig/matrix-mcp/issues>. Please do not post confidential documents or
personal data in an issue.
