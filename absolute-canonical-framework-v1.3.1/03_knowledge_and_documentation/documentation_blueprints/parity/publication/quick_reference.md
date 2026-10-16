# Quick Reference — Narrative, blueprint, machine, visual, and test parity
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KNOWLEDGE.PARITY` |
| Path | `03_knowledge_and_documentation/documentation_blueprints/parity` |
| Concept | `ABS.CONCEPT.DOCUMENT_BLUEPRINT_PARITY` |
| Requirements | `ABS.REQ.DOCUMENT_BLUEPRINT_PARITY.001`, `ABS.REQ.DOCUMENT_BLUEPRINT_PARITY.002`, `ABS.REQ.DOCUMENT_BLUEPRINT_PARITY.003` |
| States | `ALIGNED`, `STALE`, `CONFLICTED`, `N_A_JUSTIFIED`, `REVALIDATED` |
| Primary failure | `narrative, machine, visual, or test meaning drifts` |
Provided: `ABS.IFACE.PARITY.VALIDATE`. Consumed: `ABS.IFACE.CHANGE.INVALIDATE`, `ABS.IFACE.MODULE.PACKAGE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
