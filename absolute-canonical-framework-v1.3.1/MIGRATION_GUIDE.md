# Migration Guide

1. Preserve the incumbent project, the exact RC1 clean ZIP, and every active identifier.
2. Verify the RC2 detached checksum and the release manifest before use.
3. Classify existing artifacts as knowledge source, canonical definition, representation, runtime evidence, or historical record.
4. Build concept, requirement, interface, state, permission, publication, and legacy-gate crosswalks.
5. Resolve contradictory authority explicitly; never average incompatible rules.
6. Create one-to-one, split, merge, historical, tombstone, and blocker redirects for moved IDs.
7. Install RC2 in shadow mode and regenerate derivatives from canonical sources.
8. Prove coverage is not reduced, active references are mapped, required tests and recovery pass, and rollback is rehearsed.
9. Promote only after independent exact-hash certification; preserve RC1 and the complete migration evidence.

## From RC2 to 1.0.0

RC2 remains immutable; 1.0.0 is a successor tree, not an in-place edit.

1. Keep the RC2 tree. It is the predecessor of record and the input to the no-loss check.
2. Extract 1.1.0 alongside it and run
   `python3 tools/check_no_loss.py --predecessor <path-to-rc2-tree>`. It must report `PASS`
   with zero undeclared removals.
3. Run `python3 tools/deep_verify.py`. It must report `PASS` with zero findings.
4. Identifier mapping: module, requirement, interface, and concept IDs are unchanged. The
   package root and release identity change from `absolute-canonical-framework-v1.0.0-rc.2`
   and `ABS.RELEASE.1.0.0-RC2` to `absolute-canonical-framework-v1.0.0` and
   `ABS.RELEASE.1.1.0`. Module manifests pin `framework_release: 1.1.0`; a package authored
   under an earlier release reports `DOC_SCHEMA_VIOLATION` until it is migrated, because the
   binding to an exact release is the point of the field.
5. New surface to adopt: `10_runtime`, the `absolute` entry point, and the two new interfaces
   `ABS.IFACE.RUNTIME.EXECUTE` and `ABS.IFACE.TRUTH.STAMP`. All four profiles now list
   `ABS.MODULE.RUNTIME.EXECUTOR` as required.
6. Existing RC2-era references containing `RC1` or `RC2` in governance provenance records are
   historical and are deliberately left unchanged; they name where a finding was observed, not
   what this release is.

There is no automated in-place upgrade, and there should not be: replacing a governed tree
under a running project without a work packet and a rollback would be exactly the unbounded
change the framework exists to prevent. Install 1.1.0 alongside, reconcile as a governed
document, and promote in a reversible step.

## From 1.3.0 to 1.3.1

1.3.0 remains immutable; its sealed archive's hashes are recorded in `BASELINE_CHAIN`. 1.3.1 is a
successor tree with the same framework content.

1. `python3 tools/check_no_loss.py --predecessor <path-to-1.3.0-tree>` must report `PASS` with zero
   undeclared removals.
2. The package root and release identity move from `absolute-canonical-framework-v1.3.0` /
   `ABS.RELEASE.1.3.0` to `absolute-canonical-framework-v1.3.1` / `ABS.RELEASE.1.3.1`.
3. A project authored under 1.3.0 reports `DOC_SCHEMA_VIOLATION` on its manifests under 1.3.1 until
   its `framework_release` pin is migrated, by design (`LIMITATIONS.md`, *Tree identity*).
4. Licensing changed to Apache-2.0; review your redistribution terms if you relied on the old notice.

## From 1.2.0 to 1.3.0

1.2.0 remains immutable (its sealed archive's hashes are recorded in `BASELINE_CHAIN`); 1.3.0 is a
successor tree.

1. Keep the extracted 1.2.0 tree; `python3 tools/check_no_loss.py --predecessor <path-to-1.2.0-tree>`
   must report `PASS` with zero undeclared removals (it does: nothing semantic changed).
2. Identifier mapping: every module, requirement, interface, concept, profile and adapter id is
   unchanged. The package root and release identity move from
   `absolute-canonical-framework-v1.2.0` / `ABS.RELEASE.1.2.0` to
   `absolute-canonical-framework-v1.3.0` / `ABS.RELEASE.1.3.0`; module manifests **and** module
   narratives pin `framework_release: 1.3.0`, and the verifier now refuses a tree in which the two
   disagree (`MODULE_NARRATIVE_RELEASE_DRIFT`, `MODULE_RELEASE_PIN_DRIFT`).
3. A project authored under 1.2.0 reports `DOC_SCHEMA_VIOLATION` on its manifests under 1.3.0
   until migrated, by design (`LIMITATIONS.md`, *Tree identity*).
4. New controls to expect in a verification run: the release-allowlist record-set check in
   `FRAMEWORK_GOVERNANCE`, and three additional planted defects in
   `tools/verifier_mutation_check.py`. New in the tree: `docs/archive/` (governed document
   generations) and `docs/ultimate-engine/GUIDE-170-repository-release.md`, which is the
   procedure for the next bump.
5. Visual derivatives are rendered by Graphviz 15.1.0; re-render under that build before
   comparing (`LIMITATIONS.md`, *Environment*).
