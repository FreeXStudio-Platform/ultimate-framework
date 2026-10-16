# Quick Reference — Security, privacy, secrets, prompt injection, and least privilege
| Field | Value |
|---|---|
| Module | `ABS.MODULE.ENFORCEMENT.SECURITY` |
| Path | `04_enforcement/security_controls` |
| Concept | `ABS.CONCEPT.SECURITY_PRIVACY_INJECTION` |
| Requirements | `ABS.REQ.SECURITY_PRIVACY_INJECTION.001`, `ABS.REQ.SECURITY_PRIVACY_INJECTION.002`, `ABS.REQ.SECURITY_PRIVACY_INJECTION.003` |
| States | `UNASSESSED`, `PERMITTED_READ`, `PERMITTED_SCOPED_WRITE`, `APPROVAL_REQUIRED`, `DENIED`, `QUARANTINED` |
| Primary failure | `secret, prompt injection, or destructive action crosses boundary` |
Provided: `ABS.IFACE.SECURITY.AUTHORIZE`. Consumed: `ABS.IFACE.RELEASE.ASSEMBLE`, `ABS.IFACE.CONNECTOR.INVOKE`, `ABS.IFACE.PUBLICATION.DERIVE`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
