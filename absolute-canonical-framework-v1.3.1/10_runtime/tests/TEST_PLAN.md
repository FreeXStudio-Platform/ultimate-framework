# Test Plan — Runtime execution, rail enforcement, and source-of-truth stamping
## Requirement traceability
- `ABS.REQ.RUNTIME_EXECUTION.001` → narrative + policy + schema/semantic checks + fixtures + live simulation
- `ABS.REQ.RUNTIME_EXECUTION.002` → narrative + policy + schema/semantic checks + fixtures + live simulation
- `ABS.REQ.RUNTIME_EXECUTION.003` → narrative + policy + schema/semantic checks + fixtures + live simulation
## Required behavior
1. The positive fixture validates against `machine/contract.schema.json`.
2. The missing-evidence fixture fails for `minItems`.
3. The authority-override fixture fails because additional properties are forbidden.
4. Manifest canonical paths and provided/consumed interfaces resolve.
5. Every requirement ID appears in the narrative, requirements, policy, and this plan.
6. Visual source, output, semantic manifest, and text fallback resolve.
7. On an empty project every forward rail step is refused (`SIMULATION` section, live).
8. The end-to-end lifecycle completes and its ledger chain replays clean (`SIMULATION` section, live).
## Requirement coverage restated for traceability
- `ABS.REQ.RUNTIME_EXECUTION.001` is covered by behaviors 1-3, 5, 7 and 8 above.
- `ABS.REQ.RUNTIME_EXECUTION.002` is covered by behaviors 1-3, 5, 7 and 8 above.
- `ABS.REQ.RUNTIME_EXECUTION.003` is covered by behaviors 1-3, 5, 7 and 8 above.
