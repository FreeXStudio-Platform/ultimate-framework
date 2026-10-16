# Quick Reference — Provider-independent model and execution routing
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CAPABILITY.ROUTING` |
| Path | `02_capabilities/execution_profiles` |
| Concept | `ABS.CONCEPT.MODEL_ROUTING` |
| Requirements | `ABS.REQ.MODEL_ROUTING.001`, `ABS.REQ.MODEL_ROUTING.002`, `ABS.REQ.MODEL_ROUTING.003` |
| States | `CLASSIFIED`, `ROUTED`, `EXECUTING`, `FALLBACK`, `CHECKPOINTED`, `VERIFIED` |
| Primary failure | `routing lowers assurance or violates confidentiality` |
Provided: `ABS.IFACE.MODEL.ROUTE`. Consumed: `ABS.IFACE.CAPABILITY.SELECT`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
