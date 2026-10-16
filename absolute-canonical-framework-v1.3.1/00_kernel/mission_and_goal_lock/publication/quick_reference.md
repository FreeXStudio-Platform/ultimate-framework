# Quick Reference — Goal lock and mission alignment
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.GOAL_LOCK` |
| Path | `00_kernel/mission_and_goal_lock` |
| Concept | `ABS.CONCEPT.GOAL_LOCK` |
| Requirements | `ABS.REQ.GOAL_LOCK.001`, `ABS.REQ.GOAL_LOCK.002`, `ABS.REQ.GOAL_LOCK.003` |
| States | `LOCKED`, `CHANGE_PROPOSED`, `REVALIDATION_REQUIRED`, `BLOCKED_UNLINKED` |
| Primary failure | `unlinked work displaces the mission` |
Provided: `ABS.IFACE.GOAL_LINK.VALIDATE`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
