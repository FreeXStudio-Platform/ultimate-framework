---
module_id: ABS.MODULE.KERNEL.AUTHORITY_TRUTH
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Scoped authority, truth states, and conflict handling
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.AUTHORITY_TRUTH`. It answers: **What is authoritative for this exact claim, scope, and version?**
## Normative requirements
- **ABS.REQ.AUTHORITY_TRUTH.001 (MUST):** Authority shall be scoped by subject, artifact class, representation, version, lifecycle, and evidence; no file is universally authoritative.
- **ABS.REQ.AUTHORITY_TRUTH.002 (MUST):** Material claims shall use explicit truth states that distinguish verified fact, approved requirement/design, inference, plan, unknown, conflict, supersession, and rejection.
- **ABS.REQ.AUTHORITY_TRUTH.003 (MUST):** Equal-rank material conflicts shall be recorded and resolved by evidence-backed decision; vague compromise shall not replace contradictory requirements.
## Operating contract
1. Load identity, mission, scope, and current authority.
2. Evaluate the invariant against the proposed action or claim.
3. Block, permit, or require a governed decision.
4. Record evidence and exact state.
5. Invalidate and rerun when scope, source, policy, or hash changes.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`CANDIDATE` → `APPROVED` → `CONFLICTED` → `SUPERSEDED` → `UNKNOWN`
## Interfaces provided
- `ABS.IFACE.TRUTH.CLASSIFY` — claim truth-state classification
## Interfaces consumed
- `ABS.IFACE.DECISION.RECORD` — decision, risk, unknown, and waiver ledger
- `ABS.IFACE.SOURCE.ADMIT` — safe source admission and reconciliation
## Failure and recovery
Primary failure: **two active authorities compete silently.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
