---
module_id: ABS.MODULE.RUNTIME.EXECUTOR
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Runtime execution, rail enforcement, and source-of-truth stamping
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.RUNTIME_EXECUTION`. It answers: **Which single action is permitted right now, and what record proves the last one happened?**
## Normative requirements
- **ABS.REQ.RUNTIME_EXECUTION.001 (MUST):** The runtime shall permit exactly one next action at any project state, and shall refuse any command whose rail step is not that action, naming both the refusing rule and the permitted action.
- **ABS.REQ.RUNTIME_EXECUTION.002 (MUST):** Every governed mutation shall be written to the append-only hash-chained source of truth before project state is updated, so that no state can exist without a prior record of the action that produced it.
- **ABS.REQ.RUNTIME_EXECUTION.003 (MUST):** The runtime shall bind every evidence record, gate decision, document seal, and verification result to the exact tree identity it was computed against, and shall treat any record bound to a superseded identity as stale.
## Operating contract
1. Reconstruct the project state from files only; never trust a cached belief across commands.
2. Authorize the requested command against the rail, or refuse it with the permitted action.
3. Write the artifact, then the ledger entry, then the state — in that order.
4. Bind every observation to the exact tree identity it was computed against.
5. Invalidate and rerun when the identity changes.

Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`UNINSTALLED` → `DISCOVERY` → `ARCHITECTURE_FROZEN` → `CANDIDATE` → `SECOND_PASS` → `INDEPENDENT_REVIEW` → `RELEASED` → `BLOCKED`
## Interfaces provided
- `ABS.IFACE.RUNTIME.EXECUTE`
- `ABS.IFACE.TRUTH.STAMP`
## Interfaces consumed
- `ABS.IFACE.LIFECYCLE.TRANSITION`
- `ABS.IFACE.EVIDENCE.RECORD`
- `ABS.IFACE.GATE.EVALUATE`
- `ABS.IFACE.STATE.ATOMIC_UPDATE`
- `ABS.IFACE.MODULE.PACKAGE`
- `ABS.IFACE.WORK.PACKET`
- `ABS.IFACE.RECOVERY.CHECKPOINT`
- `ABS.IFACE.IDENTITY.ALLOCATE`
## Failure and recovery
Primary failure: **a step is skipped and later asserted as done.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.

The write order is the recovery design. A crash between the ledger entry and the state update leaves a recorded action whose state was not applied — visible, diagnosable, and replayable. The reverse order would leave state with no record, which is indistinguishable from a forged state.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state. The runtime never emits a certification claim about an artifact it produced.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
