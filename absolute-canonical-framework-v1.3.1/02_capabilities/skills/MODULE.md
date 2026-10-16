---
module_id: ABS.MODULE.CAPABILITY.SKILLS
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Skills, subagents, and delegation contracts
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.SKILLS_DELEGATION`. It answers: **Is this task bounded enough for a skill, and what stops it?**
## Normative requirements
- **ABS.REQ.SKILLS_DELEGATION.001 (MUST):** A skill shall solve one bounded task class and declare triggers, non-triggers, prerequisites, inputs, workflow, stop conditions, outputs, permissions, validation, failures, fallback, and compatibility.
- **ABS.REQ.SKILLS_DELEGATION.002 (MUST):** Delegation shall specify exact scope, governing IDs, allowed data, prohibited actions, output schema/location, evidence, cost, confidentiality, and return path.
- **ABS.REQ.SKILLS_DELEGATION.003 (MUST):** Delegated self-report shall not be accepted without independent validation of artifacts, behavior, side effects, and evidence identities.
## Operating contract
1. Derive the active packet's exact capability needs.
2. Filter by trust, permission, data boundary, health, cost, and fallback.
3. Activate the minimum sufficient set.
4. Execute only the bounded operation.
5. Record actual identity, revoke temporary grants, and review outcome.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`DRAFT` → `ASSESSED` → `APPROVED` → `ACTIVE` → `DEGRADED` → `DEPRECATED`
## Interfaces provided
- `ABS.IFACE.SKILL.EXECUTE` — bounded skill execution contract
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **skill triggers outside its declared scope.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
