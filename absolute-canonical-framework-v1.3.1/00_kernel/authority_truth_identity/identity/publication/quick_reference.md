# Quick Reference — Project identity and isolation
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.IDENTITY` |
| Path | `00_kernel/authority_truth_identity/identity` |
| Concept | `ABS.CONCEPT.PROJECT_IDENTITY` |
| Requirements | `ABS.REQ.PROJECT_IDENTITY.001`, `ABS.REQ.PROJECT_IDENTITY.002`, `ABS.REQ.PROJECT_IDENTITY.003` |
| States | `PROPOSED`, `REGISTERED`, `ACTIVE`, `SUPERSEDED` |
| Primary failure | `framework and project identities collide` |
Provided: `ABS.IFACE.IDENTITY.ALLOCATE`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
