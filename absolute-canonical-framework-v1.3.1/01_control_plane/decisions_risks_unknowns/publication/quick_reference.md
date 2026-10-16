# Quick Reference — Decision, risk, assumption, unknown, and waiver control
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CONTROL.DECISIONS` |
| Path | `01_control_plane/decisions_risks_unknowns` |
| Concept | `ABS.CONCEPT.DECISIONS_RISKS_UNKNOWNS` |
| Requirements | `ABS.REQ.DECISIONS_RISKS_UNKNOWNS.001`, `ABS.REQ.DECISIONS_RISKS_UNKNOWNS.002`, `ABS.REQ.DECISIONS_RISKS_UNKNOWNS.003` |
| States | `OPEN`, `PROPOSED`, `APPROVED`, `REJECTED`, `DEFERRED`, `EXPIRED`, `REOPENED` |
| Primary failure | `unknown or waiver is converted into permanent fact` |
Provided: `ABS.IFACE.DECISION.RECORD`. Consumed: `ABS.IFACE.STATE.ATOMIC_UPDATE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
