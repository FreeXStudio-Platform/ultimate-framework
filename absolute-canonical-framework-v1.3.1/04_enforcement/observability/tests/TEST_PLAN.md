# Test Plan — Observability, error taxonomy, incidents, and fault-seeking health
## Requirement traceability
- `ABS.REQ.OBSERVABILITY_INCIDENT.001` → narrative + policy + schema/semantic checks + fixtures
- `ABS.REQ.OBSERVABILITY_INCIDENT.002` → narrative + policy + schema/semantic checks + fixtures
- `ABS.REQ.OBSERVABILITY_INCIDENT.003` → narrative + policy + schema/semantic checks + fixtures
## Required behavior
1. Positive fixture validates against `machine/contract.schema.json`.
2. Missing-evidence fixture fails for `minItems`.
3. Authority-override fixture fails because additional properties are forbidden.
4. Manifest paths and provided/consumed interfaces resolve.
5. Requirement IDs appear in narrative, requirements, policy, and this plan.
6. Visual source, output, semantic manifest, and fallback resolve.
7. Candidate status is rejected as independent certification.
