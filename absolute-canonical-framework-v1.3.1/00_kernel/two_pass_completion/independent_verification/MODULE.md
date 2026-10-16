---
module_id: ABS.MODULE.KERNEL.INDEPENDENT_VERIFICATION
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Fresh and adversarial independent verification
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.INDEPENDENT_VERIFICATION`. It answers: **Has a fresh verifier tried to disprove this exact hash?**
## Normative requirements
- **ABS.REQ.INDEPENDENT_VERIFICATION.001 (MUST):** Final verification shall use a fresh context/role and preferably another provider with direct access to the frozen candidate, original mission, requirements, raw evidence, tests, conflicts, and hashes.
- **ABS.REQ.INDEPENDENT_VERIFICATION.002 (MUST):** The verifier shall attempt to disprove readiness, and repairs shall invalidate affected assurance and require transitive revalidation.
- **ABS.REQ.INDEPENDENT_VERIFICATION.003 (MUST):** A final certified status shall name the exact candidate hash; when independent verification is unavailable, status shall remain release-candidate verification-pending or unverifiable-blocked.
## Operating contract
1. Load identity, mission, scope, and current authority.
2. Evaluate the invariant against the proposed action or claim.
3. Block, permit, or require a governed decision.
4. Record evidence and exact state.
5. Invalidate and rerun when scope, source, policy, or hash changes.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`PENDING` → `IN_REVIEW` → `CERTIFIED` → `CERTIFIED_WITH_ACCEPTED_RISK` → `REJECTED` → `UNVERIFIABLE_BLOCKED`
## Interfaces provided
- `ABS.IFACE.VERIFICATION.INDEPENDENT` — fresh exact-hash independent verification
## Interfaces consumed
- `ABS.IFACE.GATE.EVALUATE` — truthful gate evaluation
## Failure and recovery
Primary failure: **builder self-certifies or review applies to another hash.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
