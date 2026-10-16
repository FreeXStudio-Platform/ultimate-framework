# Quick Reference — Lifecycle and two-pass completion
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KERNEL.LIFECYCLE` |
| Path | `00_kernel/lifecycle_state_machine` |
| Concept | `ABS.CONCEPT.LIFECYCLE_TWO_PASS` |
| Requirements | `ABS.REQ.LIFECYCLE_TWO_PASS.001`, `ABS.REQ.LIFECYCLE_TWO_PASS.002`, `ABS.REQ.LIFECYCLE_TWO_PASS.003` |
| States | `DISCOVERY`, `ARCHITECTURE_FROZEN`, `CANDIDATE`, `SECOND_PASS`, `INDEPENDENT_REVIEW`, `RELEASED`, `STALE` |
| Primary failure | `a moving candidate is treated as verified` |
Provided: `ABS.IFACE.LIFECYCLE.TRANSITION`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
