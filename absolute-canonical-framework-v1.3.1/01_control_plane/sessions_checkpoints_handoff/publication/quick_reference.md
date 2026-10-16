# Quick Reference — Sessions, checkpoints, context, and handoff
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CONTROL.SESSIONS` |
| Path | `01_control_plane/sessions_checkpoints_handoff` |
| Concept | `ABS.CONCEPT.SESSIONS_HANDOFF` |
| Requirements | `ABS.REQ.SESSIONS_HANDOFF.001`, `ABS.REQ.SESSIONS_HANDOFF.002`, `ABS.REQ.SESSIONS_HANDOFF.003` |
| States | `HEALTHY`, `CHECKPOINT_REQUIRED`, `FRESH_CONTEXT_REQUIRED`, `PAUSED_SAFE`, `RESUMED` |
| Primary failure | `handoff omits identity, hash, or exact next action` |
Provided: `ABS.IFACE.SESSION.HANDOFF`. Consumed: `ABS.IFACE.LIFECYCLE.TRANSITION`, `ABS.IFACE.RECOVERY.CHECKPOINT`, `ABS.IFACE.WORK.PACKET`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
