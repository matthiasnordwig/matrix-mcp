---
description: Index a folder of documents (PDF incl. scans and charts, Word, Excel, PowerPoint, Markdown, text, images) into a local Matrix collection so it can be searched by meaning with citations. Use when the user wants to make documents searchable, or before answering questions about a document folder that is not indexed yet.
argument-hint: <absolute folder path> [collection name]
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__create_context mcp__plugin_matrix_matrix-standalone__add_files mcp__plugin_matrix_matrix-standalone__job_status mcp__plugin_matrix_matrix-standalone__get_status
---

# Index a document folder with Matrix

Folder: $0 · collection name (optional): $1

The Matrix tools come from this plugin's MCP server (`mcp__plugin_matrix_matrix-standalone__<tool>`). Matrix reads only folders the
user shared in the plugin settings (`/plugin` → matrix → Configure → "Folders Claude may read").

1. `list_contexts`. If a collection for this folder exists, reuse its `context_id` and call
   `list_documents`: `add_files` twice adds files twice, so add only what is missing.
   Otherwise `create_context` with `{name, chunking_strategy: "structural", description}` (name =
   $1 or the folder name). Structural chunking needs no language model.
2. If a tool answers that the search model must be downloaded, tell the user the size it names
   (about 1.2 GB from Hugging Face, once) and call `setup_embedding_model`. The user approves that
   call; that approval is the consent. Never call it without telling the user first. Poll
   `job_status` until done, then repeat the step that asked for it.
3. `add_files` with `{context_id, path: "<folder>"}`. A refused path means the folder is not
   shared: tell the user which folder to add in the settings; do not look for a way around it.
4. Poll `job_status` every few seconds until the job is done. Report documents, pages and chunks
   indexed, how long it took, and every skipped file with its reason.
5. Tell the user the collection stays searchable in later sessions (`/matrix:ask`,
   `/matrix:table`, `/matrix:graph`).
