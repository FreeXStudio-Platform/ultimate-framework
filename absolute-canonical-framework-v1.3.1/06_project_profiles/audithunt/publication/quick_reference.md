# Quick Reference — AuditHunt downstream installation profile only
| Field | Value |
|---|---|
| Module | `ABS.PROFILE.PROJECT.AUDITHUNT` |
| Path | `06_project_profiles/audithunt` |
| Concept | `ABS.CONCEPT.AUDITHUNT_INSTALLATION_PROFILE` |
| Requirements | `ABS.REQ.AUDITHUNT_INSTALLATION_PROFILE.001`, `ABS.REQ.AUDITHUNT_INSTALLATION_PROFILE.002`, `ABS.REQ.AUDITHUNT_INSTALLATION_PROFILE.003` |
| States | `NOT_INSTALLED`, `DISCOVERY`, `SHADOW_CONFIGURED`, `VALIDATING`, `ACTIVE`, `ROLLBACK_REQUIRED` |
| Primary failure | `profile imports stale project claims or implies certification` |
Provided: none. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
