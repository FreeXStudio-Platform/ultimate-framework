# Quick Reference — Minimal, standard, enterprise, and downstream profiles
| Field | Value |
|---|---|
| Module | `ABS.MODULE.PROFILES.PROJECT` |
| Path | `06_project_profiles` |
| Concept | `ABS.CONCEPT.PROJECT_PROFILES` |
| Requirements | `ABS.REQ.PROJECT_PROFILES.001`, `ABS.REQ.PROJECT_PROFILES.002`, `ABS.REQ.PROJECT_PROFILES.003` |
| States | `SELECTED`, `CONFIGURED`, `INSTALLED`, `VALIDATED`, `DEGRADED`, `MIGRATION_REQUIRED` |
| Primary failure | `profile silently weakens a mandatory invariant` |
Provided: none. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
