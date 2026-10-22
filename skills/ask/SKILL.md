---
description: Answer a question from the user's indexed documents with Matrix, citing file, page and passage. Use for questions about the content of PDFs, Word or Excel files, scans or charts in an indexed collection, especially large or many documents, questions worded differently from the text, in another language than the documents, or answers spread over several documents.
argument-hint: <question> [collection]
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__list_documents mcp__plugin_matrix_matrix-standalone__search_context mcp__plugin_matrix_matrix-standalone__lookup_exact mcp__plugin_matrix_matrix-standalone__get_chunks mcp__plugin_matrix_matrix-standalone__get_page_image mcp__plugin_matrix_matrix-standalone__verify_citations
---

# Answer from the documents, with citations

Question: $ARGUMENTS

1. `list_contexts` and pick the collection that fits (ask only if several fit equally). No
   collection yet: index the folder first (skill `index`).
2. `search_context` with `context_ids: [<id>]`. Search by meaning, so phrase the query as the
   answer would read in the documents. The search finds best in the language of the documents: if the
   question is in another language, search in theirs as well. Run two or three wordings, and
   one query per sub-question for answers spread over several documents. For an exact term, number
   or paragraph label use `lookup_exact`.
3. Read every passage you will rely on in full with `get_chunks`. A hit marked
   `found_via_page_image` is a chart, diagram or scan: look at the page with `get_page_image` and
   read the values from the picture. Labels too small to read: open that page of the PDF with Read
   (`pages: "<page>"`; the file is in the shared folder), which shows it larger.
4. Write the answer in the user's language. Mark each claim with `[chunk:<chunk_id>]`, then call
   `verify_citations` with the draft and fix what it flags. If the documents do not answer the
   question, say so; do not fill gaps from general knowledge without saying it.
5. End with the sources: document, page, section and chunk id for each citation.

Do not read the PDF files themselves with Read or pdftotext while Matrix can answer: the index is
faster and cheaper, and its citations are checked.
