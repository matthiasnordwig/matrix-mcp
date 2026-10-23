---
description: Answer a question from the user's indexed documents with Matrix, citing file, page and passage. Use for questions about the content of documents in an indexed collection - PDFs, Word or Excel files, scans or charts - especially when there are many or long documents (for example contracts, regulations, project files, manuals, studies, minutes or reports), when the question is worded differently from the text or in another language than the documents, or when the answer is spread over several documents.
argument-hint: <question> [collection]
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__search_context mcp__plugin_matrix_matrix-standalone__lookup_exact mcp__plugin_matrix_matrix-standalone__get_chunks mcp__plugin_matrix_matrix-standalone__get_section mcp__plugin_matrix_matrix-standalone__get_page_image mcp__plugin_matrix_matrix-standalone__verify_citations
---

# Answer from the documents, with citations

Question: $ARGUMENTS

1. `list_contexts` and pick the collection that fits (ask only if several fit equally). No
   collection yet: offer the guided start (skill `setup`), or index the folder first (skill `index`).
2. `search_context` with `context_ids: [<id>]`. Search by meaning, so phrase the query as the
   answer would read in the documents. `list_contexts` names the languages of the collection
   (`languages`, ISO codes) and every hit its own (`language`): if the question is in another language
   than the documents it is about, run each query a second time translated into theirs (a collection
   in several languages: into the language of the documents that likely hold the answer). Run two or
   three wordings, and one query per sub-question for answers spread over several documents. For an
   exact term, number or paragraph label use `lookup_exact`. A hit is an excerpt of about 300
   characters with file, `pages`, `path`, `language` and `chunk_ids` (hits of one article are
   merged): it shows where to look, it is not text to quote. Matrix keeps the collection up to date
   with its folder by itself: if a result says the index is being updated, tell the user that changed
   files are still being read and search again a little later if the answer may be in them; files no
   longer on disk are left out (`missing_files_left_out`) - mention it if the answer may have been there.
3. Cite only what you read: fetch every passage you will rely on in full with `get_chunks` (the
   `chunk_ids` of the hits you need; one call for several). A hit's `path` shows where it sits (for
   example `KAPITEL III › ABSCHNITT 3 › Artikel 18 – … › (1)`); cite that, not page numbers or
   provisions from memory. When the answer is a rule that may have exceptions, conditions
   or special cases (thresholds, "does not apply to", "unless", small entities, deadlines), read the
   whole article or section with `get_section` (chunk id of the hit) instead of only the hit: the
   exception often sits in another paragraph. A hit with
   a `page_image_id` is a chart, diagram or scan: look at the page with `get_page_image` and
   read the values from the picture. Labels too small to read: open that page of the PDF with Read
   (`pages: "<page>"`; the file is in the shared folder), which shows it larger.
4. Write the answer in the user's language. Mark each claim with `[chunk:<chunk_id>]`, then call
   `verify_citations` with the draft and fix what it flags. If the documents do not answer the
   question, say so; do not fill gaps from general knowledge without saying it.
5. End with the sources: document, page, section and chunk id for each citation. A passage can run
   onto the next page: its text then marks the change with a line `[p. N]`, so take the page of the
   sentence you rely on (`verify_citations` reports the page of each verified quote), not only the
   passage's first page.

Do not read the PDF files themselves with Read or pdftotext while Matrix can answer: the index is
faster and cheaper, and its citations are checked.
