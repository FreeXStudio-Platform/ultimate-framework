---
module_id: ABS.MODULE.KERNEL.GOAL_LOCK
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Goal lock and mission alignment
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.GOAL_LOCK`. It answers: **Why is this action allowed, and which approved goal does it advance?**
## Normative requirements
- **ABS.REQ.GOAL_LOCK.001 (MUST):** Every material action shall link to the active mission or to required support, risk reduction, verification, recovery, or maintenance; unrelated work is rejected or deferred.
- **ABS.REQ.GOAL_LOCK.002 (MUST):** The control plane shall record the parent goal for each work packet and reject material actions without a valid upward goal link.
- **ABS.REQ.GOAL_LOCK.003 (MUST):** Goal-lock checks shall be rerun when scope, project identity, mission, or authority changes.
## Operating contract
1. Load identity, mission, scope, and current authority.
2. Evaluate the invariant against the proposed action or claim.
3. Block, permit, or require a governed decision.
4. Record evidence and exact state.
5. Invalidate and rerun when scope, source, policy, or hash changes.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`LOCKED` → `CHANGE_PROPOSED` → `REVALIDATION_REQUIRED` → `BLOCKED_UNLINKED`
## Interfaces provided
- `ABS.IFACE.GOAL_LINK.VALIDATE` — goal-link validation
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **unlinked work displaces the mission.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
