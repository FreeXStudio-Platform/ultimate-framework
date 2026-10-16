# Quick Reference — Modular architecture, dependencies, interfaces, and repository governance
| Field | Value |
|---|---|
| Module | `ABS.MODULE.ARCHITECTURE.MODULARITY` |
| Path | `00_kernel/core_invariants/modularity` |
| Concept | `ABS.CONCEPT.MODULAR_ARCHITECTURE` |
| Requirements | `ABS.REQ.MODULAR_ARCHITECTURE.001`, `ABS.REQ.MODULAR_ARCHITECTURE.002`, `ABS.REQ.MODULAR_ARCHITECTURE.003` |
| States | `PROPOSED`, `PLACED`, `WIRED`, `VALIDATED`, `DEPRECATED` |
| Primary failure | `provider/project specifics contaminate kernel` |
Provided: `ABS.IFACE.DEPENDENCY.REGISTER`. Consumed: none.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
