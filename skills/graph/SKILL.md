---
description: Build or explore the knowledge graph of an indexed Matrix collection - entities, relations and themes with evidence passages. Use when the user asks how things in their documents relate, who or what is connected, or for an overview of the main themes.
argument-hint: [topic]
allowed-tools: mcp__plugin_matrix_matrix-standalone__list_contexts mcp__plugin_matrix_matrix-standalone__graph_overview mcp__plugin_matrix_matrix-standalone__list_graph_communities mcp__plugin_matrix_matrix-standalone__list_graph_lenses mcp__plugin_matrix_matrix-standalone__search_graph_nodes mcp__plugin_matrix_matrix-standalone__get_graph_node mcp__plugin_matrix_matrix-standalone__get_chunks mcp__plugin_matrix_matrix-standalone__job_status mcp__plugin_matrix_matrix-standalone__llm_tasks mcp__plugin_matrix_matrix-standalone__llm_answer
---

# Knowledge graph

Topic (optional): $ARGUMENTS

1. `list_contexts`, then `graph_overview` for the collection: nodes, edges, communities and
   passages not yet extracted.
2. No graph yet and the user wants one: the collection's primary LLM must be the endpoint
   `client` (`list_llm_endpoints`, set it with `update_context` `llm_id`) and it needs an
   ontology profile (`list_profiles`). Tell the user it costs one model task per passage, then
   `start_graph_extraction` and serve its tasks exactly as in the `table` skill (`llm_tasks` /
   `llm_answer`, subagents in parallel for many tasks) until `job_status` is done. Then
   `recompute_communities` if `graph_overview` shows none.
3. Explore: `list_graph_communities` (themes), `search_graph_nodes` for the topic,
   `get_graph_node` for neighbours, relations and their evidence; follow at most two hops.
4. Read the evidence passages you rely on with `get_chunks`; the graph is a map, the passage is
   the source. Mark claims with `[chunk:<chunk_id>]`. `export_graph_graphml` gives a file for
   Gephi, yEd or Cytoscape.
