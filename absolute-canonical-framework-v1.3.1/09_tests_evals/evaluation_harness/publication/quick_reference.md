# Quick Reference — Positive, negative, adversarial, recovery, and clean-state tests
| Field | Value |
|---|---|
| Module | `ABS.MODULE.ENFORCEMENT.TESTING` |
| Path | `09_tests_evals/evaluation_harness` |
| Concept | `ABS.CONCEPT.TEST_EVALUATION` |
| Requirements | `ABS.REQ.TEST_EVALUATION.001`, `ABS.REQ.TEST_EVALUATION.002`, `ABS.REQ.TEST_EVALUATION.003` |
| States | `PLANNED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `FLAKY_QUARANTINED` |
| Primary failure | `negative fixture unexpectedly passes` |
Provided: `ABS.IFACE.TEST.EVALUATE`. Consumed: `ABS.IFACE.EVIDENCE.RECORD`.
Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, visual source/output, and exact-hash evidence. Invalidate all dependent views after change.
