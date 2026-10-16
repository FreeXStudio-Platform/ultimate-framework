# Quick Reference — Skills, subagents, and delegation contracts
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CAPABILITY.SKILLS` |
| Path | `02_capabilities/skills` |
| Concept | `ABS.CONCEPT.SKILLS_DELEGATION` |
| Requirements | `ABS.REQ.SKILLS_DELEGATION.001`, `ABS.REQ.SKILLS_DELEGATION.002`, `ABS.REQ.SKILLS_DELEGATION.003` |
| States | `DRAFT`, `ASSESSED`, `APPROVED`, `ACTIVE`, `DEGRADED`, `DEPRECATED` |
| Primary failure | `skill triggers outside its declared scope` |
Provided: `ABS.IFACE.SKILL.EXECUTE`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
