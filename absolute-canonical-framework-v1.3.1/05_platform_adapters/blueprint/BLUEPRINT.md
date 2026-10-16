# Blueprint — ChatGPT/Codex, Claude Code, Cursor, local, and generic adapters
**Module:** `ABS.MODULE.ADAPTERS.PLATFORMS`  
**Scope:** `ABS.SCOPE.ABS_MODULE_ADAPTERS_PLATFORMS.OPERATING_CONTRACT`  
**Truth context:** target framework architecture for `1.0.0`
## Reader question
How does this host translate the framework without changing authority?
## Components
Governed input boundary → identity/authority/permission gate → bounded module operation → evidence and policy evaluation → validated output or finding/repair loop.
## Sequence
1. Preflight the actual host.
2. Map canonical interfaces without changing semantics.
3. Declare unsupported behavior and fallback.
4. Configure least privilege and durable state.
5. Run conformance, denial, outage, checkpoint, and resume tests.
## Dependencies
- `ABS.MODULE.CAPABILITY.MANAGER`
- `ABS.MODULE.CONTROL.DECISIONS`
- `ABS.MODULE.CONTROL.RELEASE`
- `ABS.MODULE.CONTROL.STATE`
- `ABS.MODULE.CONTROL.WORK`
- `ABS.MODULE.ENFORCEMENT.CORE`
- `ABS.MODULE.ENFORCEMENT.SECURITY`
- `ABS.MODULE.KERNEL.AUTHORITY_TRUTH`
- `ABS.MODULE.KERNEL.CHANGE_RECOVERY`
- `ABS.MODULE.KERNEL.EVIDENCE_GATES`
- `ABS.MODULE.KERNEL.GOAL_LOCK`
- `ABS.MODULE.KERNEL.IDENTITY`
- `ABS.MODULE.KERNEL.LIFECYCLE`
- `ABS.MODULE.KNOWLEDGE.CANONICAL_MODULE`
- `ABS.MODULE.KNOWLEDGE.PARITY`
## Error design
Invalid input, missing authority, permission denial, dependency failure, stale evidence, semantic contradiction, and unknown cause are distinct. The primary adverse case is `adapter claims untested host capability`. The module fails closed for the affected governed action and preserves restart-safe recovery.
## Quality attributes
Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where possible, and exact-hash verifiable.
## Visual semantics
`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative. The graph shows the authority gate, bounded operation, evidence decision, validated output, and finding loop; interface notes are registry-bound.
