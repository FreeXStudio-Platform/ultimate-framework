# Quick Reference — Observability, error taxonomy, incidents, and fault-seeking health
| Field | Value |
|---|---|
| Module | `ABS.MODULE.ENFORCEMENT.OBSERVABILITY` |
| Path | `04_enforcement/observability` |
| Concept | `ABS.CONCEPT.OBSERVABILITY_INCIDENT` |
| Requirements | `ABS.REQ.OBSERVABILITY_INCIDENT.001`, `ABS.REQ.OBSERVABILITY_INCIDENT.002`, `ABS.REQ.OBSERVABILITY_INCIDENT.003` |
| States | `HEALTHY`, `DEGRADED`, `PARTIAL`, `DEPENDENCY_FAILED`, `UNKNOWN`, `UNTESTED`, `STALE`, `MISCONFIGURED` |
| Primary failure | `silence or stale probe is labeled healthy` |
Provided: `ABS.IFACE.HEALTH.REPORT`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
