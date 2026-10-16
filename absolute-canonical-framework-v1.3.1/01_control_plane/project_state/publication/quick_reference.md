# Quick Reference — Canonical project state and atomic updates
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CONTROL.STATE` |
| Path | `01_control_plane/project_state` |
| Concept | `ABS.CONCEPT.PROJECT_STATE` |
| Requirements | `ABS.REQ.PROJECT_STATE.001`, `ABS.REQ.PROJECT_STATE.002`, `ABS.REQ.PROJECT_STATE.003` |
| States | `ACTIVE`, `UPDATING`, `CONFLICTED`, `RECOVERING`, `STALE` |
| Primary failure | `stale or partial write overwrites current state` |
Provided: `ABS.IFACE.STATE.ATOMIC_UPDATE`. Consumed: `ABS.IFACE.GOAL_LINK.VALIDATE`, `ABS.IFACE.IDENTITY.ALLOCATE`, `ABS.IFACE.SESSION.HANDOFF`, `ABS.IFACE.HEALTH.REPORT`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
