---
module_id: ABS.MODULE.ENFORCEMENT.CORE
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Schemas, validators, hooks, policy, and deterministic enforcement
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.SCHEMAS_VALIDATORS_HOOKS`. It answers: **Which mandatory rule is mechanically enforced, and what does it reject?**
## Normative requirements
- **ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.001 (MUST):** Machine records shall use versioned schemas with explicit identifiers, enums, nullability, references, and compatibility rules.
- **ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.002 (MUST):** Semantic validators shall reject false PASS, missing evidence, superseded authority, broken reciprocal links, unapproved destructive actions, restricted publication leakage, and manifest drift.
- **ABS.REQ.SCHEMAS_VALIDATORS_HOOKS.003 (MUST):** Must-run lifecycle rules shall use hooks, CI, policy, permissions, or runtime gates when supported, with pinned examples and fail-closed behavior for malformed input.
## Operating contract
1. Load the versioned schema or policy.
2. Validate structure, references, and authority.
3. Run semantic, negative, adversarial, and failure checks.
4. Preserve raw outcome and candidate hash.
5. Block the governed event until violations are repaired.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`NOT_RUN` → `PASS` → `FAIL` → `BLOCKED` → `INCONCLUSIVE` → `STALE`
## Interfaces provided
- `ABS.IFACE.SCHEMA.VALIDATE` — schema and semantic policy validation
## Interfaces consumed
- `ABS.IFACE.RELEASE.ASSEMBLE` — allowlist release assembly and manifesting
- `ABS.IFACE.PARITY.VALIDATE` — cross-representation parity validation
## Failure and recovery
Primary failure: **structural validation hides semantic contradiction.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
