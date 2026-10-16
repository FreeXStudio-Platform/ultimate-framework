# Blueprint — Evidence, gates, health, and completion claims
**Module:** `ABS.MODULE.KERNEL.EVIDENCE_GATES`  
**Scope:** `ABS.SCOPE.ABS_MODULE_KERNEL_EVIDENCE_GATES.OPERATING_CONTRACT`  
**Truth context:** target framework architecture for `1.0.0`
## Reader question
What exact evidence supports this status and candidate hash?
## Components
Governed input boundary → identity/authority/permission gate → bounded module operation → evidence and policy evaluation → validated output or finding/repair loop.
## Sequence
1. Load identity, mission, scope, and current authority.
2. Evaluate the invariant against the proposed action or claim.
3. Block, permit, or require a governed decision.
4. Record evidence and exact state.
5. Invalidate and rerun when scope, source, policy, or hash changes.
## Dependencies
- `ABS.MODULE.KERNEL.AUTHORITY_TRUTH`
## Error design
Invalid input, missing authority, permission denial, dependency failure, stale evidence, semantic contradiction, and unknown cause are distinct. The primary adverse case is `PASS is issued without evidence`. The module fails closed for the affected governed action and preserves restart-safe recovery.
## Quality attributes
Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where possible, and exact-hash verifiable.
## Visual semantics
`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative. The graph shows the authority gate, bounded operation, evidence decision, validated output, and finding loop; interface notes are registry-bound.
