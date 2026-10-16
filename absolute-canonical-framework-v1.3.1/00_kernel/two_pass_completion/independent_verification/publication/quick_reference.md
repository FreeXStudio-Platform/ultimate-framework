# Quick Reference — Fresh and adversarial independent verification
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.INDEPENDENT_VERIFICATION` |
| Path | `00_kernel/two_pass_completion/independent_verification` |
| Concept | `ABS.CONCEPT.INDEPENDENT_VERIFICATION` |
| Requirements | `ABS.REQ.INDEPENDENT_VERIFICATION.001`, `ABS.REQ.INDEPENDENT_VERIFICATION.002`, `ABS.REQ.INDEPENDENT_VERIFICATION.003` |
| States | `PENDING`, `IN_REVIEW`, `CERTIFIED`, `CERTIFIED_WITH_ACCEPTED_RISK`, `REJECTED`, `UNVERIFIABLE_BLOCKED` |
| Primary failure | `builder self-certifies or review applies to another hash` |
Provided: `ABS.IFACE.VERIFICATION.INDEPENDENT`. Consumed: `ABS.IFACE.GATE.EVALUATE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
