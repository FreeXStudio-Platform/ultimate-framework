# Quick Reference — Change, deviation, recovery, and rollback
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.CHANGE_RECOVERY` |
| Path | `00_kernel/change_deviation_recovery` |
| Concept | `ABS.CONCEPT.CHANGE_DEVIATION_RECOVERY` |
| Requirements | `ABS.REQ.CHANGE_DEVIATION_RECOVERY.001`, `ABS.REQ.CHANGE_DEVIATION_RECOVERY.002`, `ABS.REQ.CHANGE_DEVIATION_RECOVERY.003` |
| States | `PROPOSED`, `CHECKPOINTED`, `APPLIED`, `VERIFYING`, `ACCEPTED`, `ROLLED_BACK` |
| Primary failure | `material change has no rollback` |
Provided: `ABS.IFACE.CHANGE.INVALIDATE`, `ABS.IFACE.RECOVERY.CHECKPOINT`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
