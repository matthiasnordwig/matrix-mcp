---
description: Check whether Matrix's search model (embedding model) is still a good choice, using its recommendation date, and look for better ONNX models on Hugging Face. Use when the user asks about the search model, search quality across languages, or when Matrix reports that its recommendation is older than six months.
argument-hint: [what the search model should do better]
allowed-tools: mcp__plugin_matrix_matrix-standalone__get_status mcp__plugin_matrix_matrix-standalone__search_embedding_models mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__job_status
---

# Check the search model

Wish (optional): $ARGUMENTS

1. `get_status` (`log_lines: 0`): under `search_model` read the model (`configured`), its `state`,
   `recommended_on` and `recommendation_current` (true = at most six months old). `list_contexts`
   shows which collection uses which model.
2. Recommendation current and no specific wish: say so with the date and stop.
3. Otherwise `search_embedding_models` (`sort: "downloads"` and `"updated"`, `query` for a
   family). It downloads nothing. Compare with the current model: languages, vector size, license,
   download size per variant, image encoder (needed for charts and scans), last change. Recommend
   at most one, or say the current one is still better.
4. Switching downloads the named size from Hugging Face and each collection keeps its old model
   until it is reindexed. Ask the user first. After a yes call `setup_embedding_model`
   (`{repo_id, variant, vision_variant?}`) - the user approves that call too - and poll
   `job_status`. Reindex (`reindex_contexts: true`) only if the user agrees. A running download can be
   stopped with `setup_embedding_model` and `cancel: true`.
