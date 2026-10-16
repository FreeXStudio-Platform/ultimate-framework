---
module_id: ABS.MODULE.KNOWLEDGE.PUBLICATION
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Publication profiles, confidentiality, and claim sanitization
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.PUBLICATION_CONFIDENTIALITY`. It answers: **Which governed claims may this audience receive?**
## Normative requirements
- **ABS.REQ.PUBLICATION_CONFIDENTIALITY.001 (MUST):** Publication views shall derive from verified internal claims through audience/classification policy, sanitization, unsupported-claim checks, rights checks, secret scanning, freshness review, and required approval.
- **ABS.REQ.PUBLICATION_CONFIDENTIALITY.002 (MUST):** Required publication classes shall include internal exhaustive, restricted engineering, controlled enterprise, public commercial, engineering quick reference, plain English, and machine-consumable.
- **ABS.REQ.PUBLICATION_CONFIDENTIALITY.003 (MUST):** Every derivative claim shall retain source claim ID, version/hash, truth state, allowed audience, sanitization policy, approval, freshness, and invalidation trigger.
## Operating contract
1. Identify the canonical scope and source evidence.
2. Define or update the narrative meaning.
3. Update applicable machine, blueprint, visual, integration, and test forms.
4. Run parity, link, security, and evidence checks.
5. Publish only governed derivatives and invalidate them on source change.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`DRAFT` → `SANITIZING` → `REVIEW_REQUIRED` → `APPROVED` → `PUBLISHED` → `STALE` → `REVOKED`
## Interfaces provided
- `ABS.IFACE.PUBLICATION.DERIVE` — governed publication derivation and sanitization
## Interfaces consumed
- `ABS.IFACE.TRUTH.CLASSIFY` — claim truth-state classification
- `ABS.IFACE.VISUAL.RENDER` — semantic visual routing and render validation
## Failure and recovery
Primary failure: **restricted or unsupported claim enters a derivative.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
