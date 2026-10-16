# Quick Reference — Scoped authority, truth states, and conflict handling
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.AUTHORITY_TRUTH` |
| Path | `00_kernel/authority_truth_identity/authority_truth` |
| Concept | `ABS.CONCEPT.AUTHORITY_TRUTH` |
| Requirements | `ABS.REQ.AUTHORITY_TRUTH.001`, `ABS.REQ.AUTHORITY_TRUTH.002`, `ABS.REQ.AUTHORITY_TRUTH.003` |
| States | `CANDIDATE`, `APPROVED`, `CONFLICTED`, `SUPERSEDED`, `UNKNOWN` |
| Primary failure | `two active authorities compete silently` |
Provided: `ABS.IFACE.TRUTH.CLASSIFY`. Consumed: `ABS.IFACE.DECISION.RECORD`, `ABS.IFACE.SOURCE.ADMIT`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
