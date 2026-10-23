---
description: Index a folder of documents (PDF incl. scans and charts, Word, Excel, PowerPoint, Markdown, text, images) into a local Matrix collection so it can be searched by meaning with citations. Use it when many or long documents will be searched more than once and answers should come with evidence - whatever the subject, for example contracts, regulations, project files, technical manuals, studies, minutes or reports: offer it BEFORE searching yourself as soon as the set is large (several documents, or one of more than about 50 pages), even for the first question, as one sentence plus the question, then wait (if the user declines, search the files yourself); also right away if the user will clearly keep working with the folder, at the latest at the second question about it (indexing runs once, locally, costs no tokens; every further question is faster and cited), instead of reading the documents one by one. If Matrix is not set up at all (no collection, no search model), use the skill setup. A one-off question about a small set does not need it; page numbers recalled from memory are not a search.
argument-hint: <absolute folder path> [collection name]
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__create_context mcp__plugin_matrix_matrix-standalone__add_files mcp__plugin_matrix_matrix-standalone__job_status mcp__plugin_matrix_matrix-standalone__get_status mcp__plugin_matrix_matrix-standalone__list_allowed_folders
---

# Index a document folder with Matrix

Folder: $0 · collection name (optional): $1

The Matrix tools come from this plugin's MCP server (`mcp__plugin_matrix_matrix-standalone__<tool>`).
Matrix reads the folder Claude Code was started in and folders the user allowed (`list_allowed_folders`).
For any other folder `add_files` asks the user; tell them in a sentence which folder you are about to
read and why before you call it, and never try to get around a refusal.

1. `list_contexts`. If a collection for this folder exists, reuse its `context_id` and call
   `list_documents`: `add_files` twice adds files twice, so add only what is missing.
   Otherwise `create_context` with `{name, chunking_strategy: "structural", description}` (name =
   $1 or the folder name; put "Folder: <absolute path>" into the description, `/matrix:status` shows it).
   Structural chunking needs no language model.
2. If a tool answers that the search model must be downloaded, tell the user the size it names
   (about 1.2 GB from Hugging Face, once) and call `setup_embedding_model`. The user approves that
   call (or answers Matrix's own question); that is the consent. Never call it without telling the user
   first. Poll `job_status` until done, then repeat the step that asked for it.
3. `add_files` with `{context_id, path: "<folder>"}`. A refusal means the user did not allow the folder:
   say so and tell them they can start Claude Code in that folder; do not look for a way around it.
4. Poll `job_status` every few seconds until the job is done (say in words how far it is).
5. **Report to the person in plain words**, not tool output. From the job result and `list_contexts`:
   - how many documents and how many passages (`docs_created`, `chunks_staged`; `list_contexts` for totals);
   - how they were split: `chunking: structural` means along the document's own structure - articles,
     headings, tables and PDF layout - not by a language model;
   - `chunks_from_scanned_pages` > 0: that many passages came from scanned pages read by text recognition
     (on the Mac, locally); 0 means no scanned pages;
   - every skipped file with its reason (`skipped`), in a short list;
   - where the index lives: `~/Library/Application Support/Matrix MCP`, on this computer only.
6. Say the collection stays searchable in later sessions (`/matrix:ask`, `/matrix:table`, `/matrix:status`).
