# Quick Reference — Publication profiles, confidentiality, and claim sanitization
| Field | Value |
|---|---|
| Module | `ABS.MODULE.KNOWLEDGE.PUBLICATION` |
| Path | `03_knowledge_and_documentation/publication_profiles` |
| Concept | `ABS.CONCEPT.PUBLICATION_CONFIDENTIALITY` |
| Requirements | `ABS.REQ.PUBLICATION_CONFIDENTIALITY.001`, `ABS.REQ.PUBLICATION_CONFIDENTIALITY.002`, `ABS.REQ.PUBLICATION_CONFIDENTIALITY.003` |
| States | `DRAFT`, `SANITIZING`, `REVIEW_REQUIRED`, `APPROVED`, `PUBLISHED`, `STALE`, `REVOKED` |
| Primary failure | `restricted or unsupported claim enters a derivative` |
Provided: `ABS.IFACE.PUBLICATION.DERIVE`. Consumed: `ABS.IFACE.TRUTH.CLASSIFY`, `ABS.IFACE.VISUAL.RENDER`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
