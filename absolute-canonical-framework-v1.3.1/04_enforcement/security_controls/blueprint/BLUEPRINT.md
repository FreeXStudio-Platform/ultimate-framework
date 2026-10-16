# Blueprint — Security, privacy, secrets, prompt injection, and least privilege
**Module:** `ABS.MODULE.ENFORCEMENT.SECURITY`  
**Scope:** `ABS.SCOPE.ABS_MODULE_ENFORCEMENT_SECURITY.OPERATING_CONTRACT`  
**Truth context:** target framework architecture for `1.0.0`
## Reader question
What data and authority can this action expose or change?
## Components
Governed input boundary → identity/authority/permission gate → bounded module operation → evidence and policy evaluation → validated output or finding/repair loop.
## Sequence
1. Load the versioned schema or policy.
2. Validate structure, references, and authority.
3. Run semantic, negative, adversarial, and failure checks.
4. Preserve raw outcome and candidate hash.
5. Block the governed event until violations are repaired.
## Dependencies
- `ABS.MODULE.CAPABILITY.MANAGER`
- `ABS.MODULE.CONTROL.DECISIONS`
- `ABS.MODULE.CONTROL.RELEASE`
- `ABS.MODULE.CONTROL.STATE`
- `ABS.MODULE.CONTROL.WORK`
- `ABS.MODULE.KERNEL.AUTHORITY_TRUTH`
- `ABS.MODULE.KERNEL.CHANGE_RECOVERY`
- `ABS.MODULE.KERNEL.EVIDENCE_GATES`
- `ABS.MODULE.KERNEL.GOAL_LOCK`
- `ABS.MODULE.KERNEL.IDENTITY`
- `ABS.MODULE.KERNEL.LIFECYCLE`
- `ABS.MODULE.KNOWLEDGE.CANONICAL_MODULE`
- `ABS.MODULE.KNOWLEDGE.PARITY`
## Error design
Invalid input, missing authority, permission denial, dependency failure, stale evidence, semantic contradiction, and unknown cause are distinct. The primary adverse case is `secret, prompt injection, or destructive action crosses boundary`. The module fails closed for the affected governed action and preserves restart-safe recovery.
## Quality attributes
Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where possible, and exact-hash verifiable.
## Visual semantics
`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative. The graph shows the authority gate, bounded operation, evidence decision, validated output, and finding loop; interface notes are registry-bound.
