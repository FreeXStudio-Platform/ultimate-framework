# Quick Reference — Capability selection, health, permission, and fallback
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CAPABILITY.MANAGER` |
| Path | `02_capabilities/capability_manager` |
| Concept | `ABS.CONCEPT.CAPABILITY_MANAGER` |
| Requirements | `ABS.REQ.CAPABILITY_MANAGER.001`, `ABS.REQ.CAPABILITY_MANAGER.002`, `ABS.REQ.CAPABILITY_MANAGER.003` |
| States | `DISCOVERED`, `ASSESSED`, `APPROVED`, `ENABLED`, `HEALTHY`, `DEGRADED`, `QUARANTINED`, `REMOVED` |
| Primary failure | `enabled capability has unknown health or excessive permission` |
Provided: `ABS.IFACE.CAPABILITY.SELECT`. Consumed: `ABS.IFACE.WORK.PACKET`, `ABS.IFACE.SKILL.EXECUTE`, `ABS.IFACE.MODEL.ROUTE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
