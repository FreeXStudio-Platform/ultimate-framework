# Quick Reference — Connectors, MCP, plugins, and external systems
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CAPABILITY.CONNECTORS` |
| Path | `02_capabilities/connectors_mcp` |
| Concept | `ABS.CONCEPT.CONNECTORS_MCP` |
| Requirements | `ABS.REQ.CONNECTORS_MCP.001`, `ABS.REQ.CONNECTORS_MCP.002`, `ABS.REQ.CONNECTORS_MCP.003` |
| States | `UNAVAILABLE`, `DISCOVERED`, `READ_ONLY`, `WRITE_SCOPED`, `DEGRADED`, `REVOKED` |
| Primary failure | `connector content or availability is trusted without preflight` |
Provided: `ABS.IFACE.CONNECTOR.INVOKE`. Consumed: `ABS.IFACE.CAPABILITY.SELECT`, `ABS.IFACE.SECURITY.AUTHORIZE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
