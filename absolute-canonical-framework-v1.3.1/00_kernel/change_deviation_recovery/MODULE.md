---
module_id: ABS.MODULE.KERNEL.CHANGE_RECOVERY
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Change, deviation, recovery, and rollback
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.CHANGE_DEVIATION_RECOVERY`. It answers: **Can this change be reversed, and what becomes stale?**
## Normative requirements
- **ABS.REQ.CHANGE_DEVIATION_RECOVERY.001 (MUST):** Material changes shall have an impact set, checkpoint, rollback route, and revalidation plan before execution.
- **ABS.REQ.CHANGE_DEVIATION_RECOVERY.002 (MUST):** A change shall invalidate affected and transitive evidence, parity stamps, derivatives, indexes, and compatibility claims.
- **ABS.REQ.CHANGE_DEVIATION_RECOVERY.003 (MUST):** Detected deviation shall stop the affected route, preserve evidence, restore or re-plan from the last valid point, and revalidate the repaired scope.
## Operating contract
1. Load identity, mission, scope, and current authority.
2. Evaluate the invariant against the proposed action or claim.
3. Block, permit, or require a governed decision.
4. Record evidence and exact state.
5. Invalidate and rerun when scope, source, policy, or hash changes.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`PROPOSED` → `CHECKPOINTED` → `APPLIED` → `VERIFYING` → `ACCEPTED` → `ROLLED_BACK`
## Interfaces provided
- `ABS.IFACE.CHANGE.INVALIDATE` — dependency invalidation and deviation check
- `ABS.IFACE.RECOVERY.CHECKPOINT` — checkpoint, rollback, and resume
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **material change has no rollback.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
