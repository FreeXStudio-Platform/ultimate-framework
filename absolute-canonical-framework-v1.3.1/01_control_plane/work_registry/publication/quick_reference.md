# Quick Reference — Work packets, tasks, dependencies, and progress
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CONTROL.WORK` |
| Path | `01_control_plane/work_registry` |
| Concept | `ABS.CONCEPT.WORK_REGISTRY` |
| Requirements | `ABS.REQ.WORK_REGISTRY.001`, `ABS.REQ.WORK_REGISTRY.002`, `ABS.REQ.WORK_REGISTRY.003` |
| States | `POOL`, `TRIAGED`, `READY`, `IN_PROGRESS`, `VERIFYING`, `DONE`, `BLOCKED`, `FAILED` |
| Primary failure | `work is marked done before acceptance` |
Provided: `ABS.IFACE.WORK.PACKET`. Consumed: `ABS.IFACE.GOAL_LINK.VALIDATE`, `ABS.IFACE.LIFECYCLE.TRANSITION`, `ABS.IFACE.STATE.ATOMIC_UPDATE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
