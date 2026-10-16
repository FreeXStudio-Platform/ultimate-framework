# Quick Reference — Evidence, gates, health, and completion claims
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.EVIDENCE_GATES` |
| Path | `00_kernel/evidence_gate_health` |
| Concept | `ABS.CONCEPT.EVIDENCE_GATES_HEALTH` |
| Requirements | `ABS.REQ.EVIDENCE_GATES_HEALTH.001`, `ABS.REQ.EVIDENCE_GATES_HEALTH.002`, `ABS.REQ.EVIDENCE_GATES_HEALTH.003` |
| States | `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `INCONCLUSIVE`, `STALE`, `INVALID_REPORT` |
| Primary failure | `PASS is issued without evidence` |
Provided: `ABS.IFACE.EVIDENCE.RECORD`, `ABS.IFACE.GATE.EVALUATE`. Consumed: `ABS.IFACE.SCHEMA.VALIDATE`, `ABS.IFACE.TEST.EVALUATE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
