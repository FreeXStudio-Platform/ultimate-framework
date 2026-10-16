# Quick Reference — Source admission, lineage, no-loss reconciliation, and supersession
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KNOWLEDGE.RECONCILIATION` |
| Path | `03_knowledge_and_documentation/source_reconciliation` |
| Concept | `ABS.CONCEPT.SOURCE_ADMISSION_RECONCILIATION` |
| Requirements | `ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.001`, `ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.002`, `ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.003` |
| States | `RAW`, `ADMITTED`, `CLASSIFIED`, `CONCEPT_MAPPED`, `CANDIDATE_CANONICAL`, `APPROVED`, `SUPERSEDED`, `QUARANTINED` |
| Primary failure | `unique meaning is silently lost or filename becomes authority` |
Provided: `ABS.IFACE.SOURCE.ADMIT`. Consumed: `ABS.IFACE.TRUTH.CLASSIFY`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
