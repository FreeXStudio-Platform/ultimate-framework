# Blueprint — Decision, risk, assumption, unknown, and waiver control
**Module:** `ABS.MODULE.CONTROL.DECISIONS`  
**Scope:** `ABS.SCOPE.ABS_MODULE_CONTROL_DECISIONS.OPERATING_CONTRACT`  
**Truth context:** target framework architecture for `1.0.0`
## Reader question
Who may decide this issue, and what reopens it?
## Components
Governed input boundary → identity/authority/permission gate → bounded module operation → evidence and policy evaluation → validated output or finding/repair loop.
## Sequence
1. Read the latest durable state and version.
2. Validate bounded input, authority, permission, dependency, and rollback.
3. Apply one atomic update.
4. Record checks, findings, evidence, and limitations.
5. Persist exact next action and reject stale writes.
## Dependencies
- `ABS.MODULE.KERNEL.AUTHORITY_TRUTH`
- `ABS.MODULE.KERNEL.CHANGE_RECOVERY`
- `ABS.MODULE.KERNEL.EVIDENCE_GATES`
- `ABS.MODULE.KERNEL.GOAL_LOCK`
- `ABS.MODULE.KERNEL.IDENTITY`
- `ABS.MODULE.KERNEL.LIFECYCLE`
## Error design
Invalid input, missing authority, permission denial, dependency failure, stale evidence, semantic contradiction, and unknown cause are distinct. The primary adverse case is `unknown or waiver is converted into permanent fact`. The module fails closed for the affected governed action and preserves restart-safe recovery.
## Quality attributes
Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where possible, and exact-hash verifiable.
## Visual semantics
`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative. The graph shows the authority gate, bounded operation, evidence decision, validated output, and finding loop; interface notes are registry-bound.
