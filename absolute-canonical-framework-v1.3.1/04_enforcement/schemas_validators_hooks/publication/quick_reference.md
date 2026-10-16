# Quick Reference — Schemas, validators, hooks, policy, and deterministic enforcement
| Field | Value |
|---|---|
| Module | `ABS.MODULE.ENFORCEMENT.CORE` |
| Path | `04_enforcement/schemas_validators_hooks` |
| Concept | `ABS.CONCEPT.SCHEMAS_VALIDATORS_HOOKS` |
| Requirements | `ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.001`, `ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.002`, `ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.003` |
| States | `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `INCONCLUSIVE`, `STALE` |
| Primary failure | `structural validation hides semantic contradiction` |
Provided: `ABS.IFACE.SCHEMA.VALIDATE`. Consumed: `ABS.IFACE.RELEASE.ASSEMBLE`, `ABS.IFACE.PARITY.VALIDATE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
