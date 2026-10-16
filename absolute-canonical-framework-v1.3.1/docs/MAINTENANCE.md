# Maintenance
Review dependencies, capability health, permissions, data policies, schemas, adapters, profiles, evidence freshness, open risks, publication claims, and release reproducibility on a defined cadence. Every material change identifies descendants in the dependency graph, invalidates affected verification, updates coordinated representations, reruns negative controls, and produces a new semantic version or documented compatibility record. Deprecated modules remain traceable until migration and retention obligations close.

## Runtime maintenance

Re-run `python3 09_tests_evals/run_all.py` on the cadence above: it runs the deterministic
validator, the successor controls, `tools/deep_verify.py`, and
`tools/verifier_mutation_check.py`. The mutation check is the one that answers whether the
verifier's own checks are still alive — a section that silently stopped running reports `PASS`
exactly like a clean tree, so a green deep verification alone does not establish coverage.

Adding a check to `runtime/verify.py` that guards a defect class worth guarding means adding a
mutation for it to `tools/verifier_mutation_check.py`. A check with no mutation behind it is
unproven.

For governed projects, re-run `absolute verify --record` after any change to the project tree;
evidence and gates are bound to the tree identity and go stale when it moves. `absolute status`
reports chain health, anchor health, abandoned packages, and any unapplied state update.
