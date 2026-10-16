# Blueprint — Runtime execution, rail enforcement, and source-of-truth stamping
**Module:** `ABS.MODULE.RUNTIME.EXECUTOR`  
**Scope:** `ABS.SCOPE.ABS_MODULE_RUNTIME_EXECUTOR.OPERATING_CONTRACT`  
**Truth context:** target framework architecture for `1.0.0`
## Reader question
Which single action is permitted right now, and what record proves the last one happened?
## Components
CLI surface → rail authorizer → operation → artifact writer → ledger appender → state writer. The rail authorizer is the only entry to the mutating path; there is no second door.
## Sequence
1. Reconstruct project context from files (`runtime.project.Project.rail_context`).
2. Authorize the command against the rail (`runtime.rail.check_permitted`).
3. Perform the bounded operation and write its artifact atomically.
4. Append the hash-chained ledger entry.
5. Update project state.
## Requirement coverage
- `ABS.REQ.RUNTIME_EXECUTION.001` is realized by step 2 of the sequence above.
- `ABS.REQ.RUNTIME_EXECUTION.002` is realized by step 4 of the sequence above.
- `ABS.REQ.RUNTIME_EXECUTION.003` is realized by step 3 of the sequence above.
## Dependencies
- `ABS.MODULE.KERNEL.LIFECYCLE`
- `ABS.MODULE.KERNEL.EVIDENCE_GATES`
- `ABS.MODULE.KERNEL.IDENTITY`
- `ABS.MODULE.KERNEL.GOAL_LOCK`
- `ABS.MODULE.KERNEL.CHANGE_RECOVERY`
- `ABS.MODULE.CONTROL.STATE`
- `ABS.MODULE.CONTROL.WORK`
- `ABS.MODULE.CONTROL.SESSIONS`
- `ABS.MODULE.CONTROL.RELEASE`
- `ABS.MODULE.KNOWLEDGE.CANONICAL_MODULE`
## Error design
Each refusal has its own type in `runtime.errors` with a distinct exit code, so a caller can branch on cause rather than on message text. The primary adverse case is `a step is skipped and later asserted as done`. The runtime fails closed for the affected action and preserves restart-safe recovery.
## Quality attributes
Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where possible, and exact-hash verifiable.
## Visual semantics
`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative and is regenerated, never hand-edited.
