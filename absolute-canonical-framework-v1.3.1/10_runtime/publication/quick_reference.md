# Quick Reference — Runtime execution, rail enforcement, and source-of-truth stamping
| Field | Value |
|---|---|
| Module | `ABS.MODULE.RUNTIME.EXECUTOR` |
| Path | `10_runtime` |
| Concept | `ABS.CONCEPT.RUNTIME_EXECUTION` |
| Requirements | `ABS.REQ.RUNTIME_EXECUTION.001`, `ABS.REQ.RUNTIME_EXECUTION.002`, `ABS.REQ.RUNTIME_EXECUTION.003` |
| States | `UNINSTALLED`, `DISCOVERY`, `ARCHITECTURE_FROZEN`, `CANDIDATE`, `SECOND_PASS`, `INDEPENDENT_REVIEW`, `RELEASED`, `BLOCKED` |
| Primary failure | `a step is skipped and later asserted as done` |
| Entry point | `absolute` (see `runtime/cli.py`) |

Provided: `ABS.IFACE.RUNTIME.EXECUTE`, `ABS.IFACE.TRUTH.STAMP`. Consumed: `ABS.IFACE.LIFECYCLE.TRANSITION`, `ABS.IFACE.EVIDENCE.RECORD`, `ABS.IFACE.GATE.EVALUATE`, `ABS.IFACE.STATE.ATOMIC_UPDATE`, `ABS.IFACE.MODULE.PACKAGE`, `ABS.IFACE.WORK.PACKET`, `ABS.IFACE.RECOVERY.CHECKPOINT`, `ABS.IFACE.IDENTITY.ALLOCATE`.
Mandatory: rail authorization before every mutation, ledger append before state write, identity binding on every observation. Invalidate all dependent claims after an identity change.
