---
module_id: ABS.MODULE.KNOWLEDGE.RECONCILIATION
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Source admission, lineage, no-loss reconciliation, and supersession
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.SOURCE_ADMISSION_RECONCILIATION`. It answers: **Which concepts survive each source, why, and where is every disposition?**
## Normative requirements
- **ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.001 (MUST):** Source admission shall preserve raw bytes, hashes, collection boundaries, provenance, rights, confidentiality, extraction diagnostics, lineage, and explicit artifact disposition.
- **ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.002 (MUST):** Reconciliation shall compare concepts and structured critical differences, preserve unique information, separate candidate discovery from replacement decisions, and build a shadow candidate before promotion.
- **ABS.REQ.SOURCE_ADMISSION_RECONCILIATION.003 (MUST):** Automatic high-impact replacement shall require complete provenance, rights, no unique knowledge loss, no unmapped links, no critical contradiction, calibrated precision, and rollback.
## Operating contract
1. Identify the canonical scope and source evidence.
2. Define or update the narrative meaning.
3. Update applicable machine, blueprint, visual, integration, and test forms.
4. Run parity, link, security, and evidence checks.
5. Publish only governed derivatives and invalidate them on source change.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`RAW` → `ADMITTED` → `CLASSIFIED` → `CONCEPT_MAPPED` → `CANDIDATE_CANONICAL` → `APPROVED` → `SUPERSEDED` → `QUARANTINED`
## Interfaces provided
- `ABS.IFACE.SOURCE.ADMIT` — safe source admission and reconciliation
## Interfaces consumed
- `ABS.IFACE.TRUTH.CLASSIFY` — claim truth-state classification
## Failure and recovery
Primary failure: **unique meaning is silently lost or filename becomes authority.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
