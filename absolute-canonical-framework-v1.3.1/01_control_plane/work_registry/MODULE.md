---
module_id: ABS.MODULE.CONTROL.WORK
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Work packets, tasks, dependencies, and progress
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.WORK_REGISTRY`. It answers: **What bounded outcome is being produced under which permissions?**
## Normative requirements
- **ABS.REQ.WORK_REGISTRY.001 (MUST):** Every work item shall have stable identity, bounded objective, parent goal, scope, dependencies, permissions, rollback, acceptance criteria, checks, evidence, owner, verifier, and truthful status.
- **ABS.REQ.WORK_REGISTRY.002 (MUST):** Progress shall be computed only from weighted work that has passed its required verification; planned or implemented-only work shall not count as verified completion.
- **ABS.REQ.WORK_REGISTRY.003 (MUST):** Duplicate, obsolete, rejected, blocked, deferred, superseded, and rolled-back work shall remain in history with explicit disposition.
## Operating contract
1. Read the latest durable state and version.
2. Validate bounded input, authority, permission, dependency, and rollback.
3. Apply one atomic update.
4. Record checks, findings, evidence, and limitations.
5. Persist exact next action and reject stale writes.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`POOL` → `TRIAGED` → `READY` → `IN_PROGRESS` → `VERIFYING` → `DONE` → `BLOCKED` → `FAILED`
## Interfaces provided
- `ABS.IFACE.WORK.PACKET` — work-packet registration and dependency control
## Interfaces consumed
- `ABS.IFACE.GOAL_LINK.VALIDATE` — goal-link validation
- `ABS.IFACE.LIFECYCLE.TRANSITION` — validated lifecycle transition
- `ABS.IFACE.STATE.ATOMIC_UPDATE` — atomic canonical state update
## Failure and recovery
Primary failure: **work is marked done before acceptance.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
