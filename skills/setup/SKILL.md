---
description: Guided first start of Matrix - walks the user step by step from "nothing set up" to a first answer from their own documents (folder, search model, indexing, example questions). Use it, or offer it in one sentence with the reason, when there are many or long documents, further questions about the same set are likely and answers should come with evidence - whatever the subject, for example contracts, regulations and standards, project files, technical manuals and data sheets, studies and papers, minutes, reports or scans: (a) BEFORE you search or read anything yourself as soon as the set is large (several documents, or one of more than about 50 pages) - even for the first question - as one sentence plus the question, then wait for the answer (if the user declines, search the files yourself), and right away when the user will clearly work with such a set (the project folder holds it, they have to get up to speed on it, several questions are ahead, the work is ongoing), or (b) at the latest at the second question about the same not yet indexed folder ("you are asking about these documents for the second time - if I index them once, locally and without tokens, all further questions are faster and come with citations"), when Matrix has no collection or search model yet; also when the user asks how to start with Matrix or what it does. A single short file, or a one-off question about a small set, you can answer by searching the files yourself - completely: page numbers or provisions recalled from memory are not a search (then add the evidence from the files or say it is missing; never call an answer without evidence "from the documents").
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__create_context mcp__plugin_matrix_matrix-standalone__add_files mcp__plugin_matrix_matrix-standalone__job_status mcp__plugin_matrix_matrix-standalone__get_status mcp__plugin_matrix_matrix-standalone__list_allowed_folders mcp__plugin_matrix_matrix-standalone__search_embedding_models mcp__plugin_matrix_matrix-standalone__search_context mcp__plugin_matrix_matrix-standalone__lookup_exact mcp__plugin_matrix_matrix-standalone__get_chunks mcp__plugin_matrix_matrix-standalone__get_page_image mcp__plugin_matrix_matrix-standalone__verify_citations
---

# Guided start with Matrix

You lead; the person reads and decides, nothing more. Speak their language, in plain words, short.
**One step at a time: say what happens, ask one question, wait for the answer.** No tool names, no JSON, no
technical background unless asked. Never read, index or download anything before they said yes to that step.
Skip steps that are already done (check `list_contexts`, `get_status`, `list_allowed_folders` first; if
Matrix is already set up, say so and offer `/matrix:status` or a question instead).

1. **What Matrix does** (two sentences): it makes their documents - PDFs including scans and charts, Word,
   Excel, PowerPoint, text - searchable by meaning on this computer, so Claude can answer from them with
   file and page as proof. Index and search model stay on this Mac; only the passages Claude reads go to
   Claude like any other file it reads. Ask: "Shall we set it up now? It takes a few minutes."
2. **Which folder?** Suggest candidates, never guess without asking:
   - the folder Claude Code was started in (`list_allowed_folders` shows it as `project`), if it holds documents;
   - typical places with many PDF or Office files, found with your own tools (look at, for example, Documents,
     Desktop, Downloads and sub-folders: count `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx`; do not open files).
   Offer at most three, each with a rough file count, and ask which one (or another path). Large folders:
   say how many files and that indexing takes longer; suggest starting with a subfolder.
3. **Permission to read it.** If the folder is outside what Matrix may read, say in one sentence which folder
   and why, then go on: Matrix will show the person its own question (Accept / Decline) when the folder
   is read. If they decline, accept it and offer another folder or: "start Claude Code in that folder next time".
4. **Search model.** `get_status` -> `search_model`. Name it in plain words and the date it was recommended
   ("recommended October 2026"). If `recommendation_current` is false (older than six months), first check
   alternatives with `search_embedding_models` (nothing is downloaded) and recommend at most one, or say the
   current one is still the better choice; ask which they want. If it is not installed, tell them the size
   (about 1.2 GB once, from Hugging Face, into Matrix's own folder) and ask for a yes. After the yes call
   `setup_embedding_model` (the person approves that call or answers Matrix's question - that is their consent)
   and follow `job_status`, telling them in words how far it is. A running download can be stopped with
   `setup_embedding_model` and `cancel: true`.
   Then `get_status` -> `reranker`: if it needs a download, offer it once in one sentence (it puts the best
   passages first; about 0.6 GB from Hugging Face, license Apache-2.0, sizes from `get_status`) and call `setup_embedding_model` with `reranker: true` only after a yes. Without it the search works as before.
5. **Index.** Follow the steps of `/matrix:index` for that folder (collection with structural splitting, the
   folder written into its description, `add_files`, `job_status`). Tell them about progress in words
   ("12 of 40 files").
6. **Summary in plain words:** how many documents and passages; how it was split (along the documents' own
   structure - articles, headings, tables, PDF layout - not by a language model); whether scanned pages were
   read by text recognition (`chunks_from_scanned_pages`); skipped files with the reason; that the index
   lives in `~/Library/Application Support/Matrix MCP` on this computer only.
7. **Example questions.** Look at the titles (`list_documents`) and read two or three passages (`search_context`
   with a general query, then `get_chunks`) to see what the documents are about. Propose three concrete
   questions that these documents can answer, one line each, in the language of the documents. Ask which one
   to try (or their own). Answer it like `/matrix:ask`: search in the language of the documents with two or
   three wordings, read the passages in full, cite file, page and passage, check with `verify_citations`.
8. **What else there is, briefly:** `/matrix:ask <question>` for further questions; `/matrix:table <question>`
   for one question across many documents as a table (**costs**: every row is one model task in this Claude
   Code session, counted against their Claude quota - name the number before starting); `/matrix:status` to see
   what Matrix holds and does; `/matrix:search-model` to check the search model later.
9. **Last tip, permissions.** Matrix's reading tools can be allowed once so Claude does not ask each time:
   the README of the plugin has a ready list for `settings.json` (reading tools only).
   Never suggest allowing the model download tool (`setup_embedding_model`) or all tools of Matrix: the
   download must stay the person's own decision.
