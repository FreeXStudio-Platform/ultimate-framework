# Quick Reference — Manifests, clean releases, checksums, and migration
| Field | Value |
|---|---|
| Module | `ABS.MODULE.CONTROL.RELEASE` |
| Path | `01_control_plane/manifests_releases` |
| Concept | `ABS.CONCEPT.MANIFEST_RELEASE` |
| Requirements | `ABS.REQ.MANIFEST_RELEASE.001`, `ABS.REQ.MANIFEST_RELEASE.002`, `ABS.REQ.MANIFEST_RELEASE.003` |
| States | `CANDIDATE_FROZEN`, `STAGED`, `VALIDATED`, `PACKAGED`, `EXTRACTED_VERIFIED`, `RELEASED`, `REJECTED` |
| Primary failure | `unexpected or unmanifested file enters release` |
Provided: `ABS.IFACE.RELEASE.ASSEMBLE`. Consumed: `ABS.IFACE.EVIDENCE.RECORD`, `ABS.IFACE.GATE.EVALUATE`, `ABS.IFACE.RECOVERY.CHECKPOINT`, `ABS.IFACE.VERIFICATION.INDEPENDENT`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
