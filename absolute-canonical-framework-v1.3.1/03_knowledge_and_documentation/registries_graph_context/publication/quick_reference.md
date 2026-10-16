# Quick Reference — Registries, graph, indexes, context packs, and retrieval
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KNOWLEDGE.GRAPH` |
| Path | `03_knowledge_and_documentation/registries_graph_context` |
| Concept | `ABS.CONCEPT.REGISTRIES_GRAPH_CONTEXT` |
| Requirements | `ABS.REQ.REGISTRIES_GRAPH_CONTEXT.001`, `ABS.REQ.REGISTRIES_GRAPH_CONTEXT.002`, `ABS.REQ.REGISTRIES_GRAPH_CONTEXT.003` |
| States | `REGISTERED`, `INDEXED`, `QUERYABLE`, `STALE`, `REBUILDING`, `QUARANTINED` |
| Primary failure | `dangling or stale projection is treated as authority` |
Provided: `ABS.IFACE.GRAPH.QUERY`. Consumed: `ABS.IFACE.CHANGE.INVALIDATE`, `ABS.IFACE.DEPENDENCY.REGISTER`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
