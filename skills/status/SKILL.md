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
   - `reranker`: whether the passages are re-ordered by relevance (`state` ready / needs a download of
     `download_gb` GB / off) and its license.
   - `shared_folders`: the folders Matrix may read and where each comes from (`project` = the folder Claude
     Code was started in, `setting` = plugin setting, `granted` = the user allowed it when asked), and
     `problems` (a folder that does not exist or cannot be read, with the reason).
   - `model_task_queue.waiting` / `fetched_not_answered`: tasks Matrix has handed to Claude that are not
     answered yet. Say that they run in this Claude Code session and count against the user's quota.
   - `running_jobs`: what is running now (indexing, download); name it in words with its progress.
   - `index.collections`: per collection whether it matches its folders - `state` current / updating
     (`files_updating` files are being read again) / waiting (`waiting_for`) / not_checked_yet - with the
     time of the last check (`last_check_seconds_ago`, say "2 minutes ago"), `missing_files` (files gone
     from the folder: kept in the collection but no longer searched; name a few from `missing`),
     `unreadable_files` and `problems` (a folder no longer shared or no longer there: not checked).
     Nothing is ever deleted automatically; removing documents of missing files is not possible here.
3. Present it as a short list, for example:

   ```
   Matrix
   Collections
     Contracts - 42 documents, 1,310 passages, split along headings and articles
                 folder /Users/me/Documents/Contracts
                 up to date (checked 2 minutes ago); 1 file no longer in the folder: old-offer.pdf
   Search model   embeddinggemma-2, installed; recommended October 2026 (still current)
   Re-ordering    bge-reranker-v2-m3, installed
   Folders Matrix may read
     /Users/me/Documents/Contracts   (the folder Claude Code was started in)
     /Users/me/Downloads/Papers      (you allowed it)
   Waiting for Claude   no model tasks
   Running now          nothing
   ```

4. Name problems plainly (for example "the folder X no longer exists") and say what to do. Taking back a
   permission: `revoke_folder` removes only the permission, never files or the index; offer it, do it only
   on a yes.
