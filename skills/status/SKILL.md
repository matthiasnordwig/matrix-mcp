---
description: Show the user, in plain words, what Matrix holds and does right now - collections with their folder, documents and passages, the search model, the folders Matrix may read, model tasks waiting for Claude and running jobs. Use when the user asks what Matrix has indexed, what it is doing, whether it is still working, or which folders it can read.
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__get_status mcp__plugin_matrix_matrix-standalone__list_allowed_folders mcp__plugin_matrix_matrix-standalone__job_status
---

# Matrix status

This is for the person, not for you: answer in their language, in short plain sentences, no tool names or JSON.
Use only read-only tools; change nothing.

1. `list_contexts`: for each collection its name, number of documents (`document_count`) and passages
   (`chunk_count`), the way it was split (`chunking_strategy` structural = along articles, headings and tables),
   and its folder. The folder is written in the collection's `description` ("Folder: ...") when it was
   indexed with `/matrix:index` or `/matrix:setup`; if there is none, say the folder is not recorded.
   Add the number of pages from `list_documents` (sum of `page_count`) only when the user asks for detail.
2. `get_status` (`log_lines: 0`) and read from it:
   - `search_model`: the model (`configured`), whether it is installed (`state` ready / needs a download of
     `download_gb` GB), the date of its recommendation (`recommended_on`) and whether that is still current
     (`recommendation_current` false = older than six months: offer `/matrix:search-model`).
   - `shared_folders`: the folders Matrix may read and where each comes from (`project` = the folder Claude
     Code was started in, `setting` = plugin setting, `granted` = the user allowed it when asked), and
     `problems` (a folder that does not exist or cannot be read, with the reason).
   - `model_task_queue.waiting` / `fetched_not_answered`: tasks Matrix has handed to Claude that are not
     answered yet. Say that they run in this Claude Code session and count against the user's quota.
   - `running_jobs`: what is running now (indexing, download); name it in words with its progress.
3. Present it as a short list, for example:

   ```
   Matrix
   Collections
     Contracts - 42 documents, 1,310 passages, split along headings and articles
                 folder /Users/me/Documents/Contracts
   Search model   embeddinggemma-2, installed; recommended October 2026 (still current)
   Folders Matrix may read
     /Users/me/Documents/Contracts   (the folder Claude Code was started in)
     /Users/me/Downloads/Papers      (you allowed it)
   Waiting for Claude   no model tasks
   Running now          nothing
   ```

4. Name problems plainly (for example "the folder X no longer exists") and say what to do. Taking back a
   permission: `revoke_folder` removes only the permission, never files or the index; offer it, do it only
   on a yes.
