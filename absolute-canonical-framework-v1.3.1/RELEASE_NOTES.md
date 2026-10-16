# Release Notes — ABS.RELEASE.1.3.1

## What changed in one sentence

1.3.0 is re-issued for public distribution: Apache-2.0 under the FreeXStudio name, personal and
host-specific data removed, the documentation set restamped — with no change to the framework's
modules, requirements, interfaces or runtime behaviour.

## What you need to know

- **Identity moved**, as every release does: `ABS.RELEASE.1.3.1`, candidate `ABS.CANDIDATE.1.3.1`,
  package root `absolute-canonical-framework-v1.3.1`. Module manifests and narratives pin
  `framework_release: 1.3.1`.
- **No semantic removals.** `python3 tools/check_no_loss.py --predecessor <1.3.0 tree>` passes.
- **License changed** from all-rights-reserved to Apache-2.0.
- **Verify it yourself**:

```sh
python3 tools/restore_modes.py --check        # only needed if your copy lost file modes
python3 09_tests_evals/run_all.py
python3 tools/deep_verify.py
python3 tools/verify_successor_release.py .
```

Independent certification (gate `C20`) remains external and pending.

---

## Previous release notes — ABS.RELEASE.1.3.0

## What changed in one sentence

The 1.2.0 tree is placed under version control the way its own integrity model requires, the two
representation defects the field trial found and the verifier could not see are closed, every
visual derivative is rendered under one recorded renderer, and the engine-built documentation is
regenerated for the release it describes — the first release published to a git remote.

## Why 1.3.0

1.2.0 was verified clean, but only in one sandbox. Its `.git` lived inside the release payload the
integrity model denylists, so no working tree could ever pass `release_tree_integrity`; its 35
visual derivatives came from two different Graphviz builds, so the parity check failed on every
other host; thirty-three module narratives still pinned `framework_release: 1.0.0` while their
manifests said 1.2.0 and nothing compared the two; and the test manifest still described the RC2
suite. None of those is a semantic change to the framework. All of them are the difference between
a tree that verifies where it was built and a tree that verifies where it is cloned. 1.3.0 closes
them, adds the verifier check and mutation controls that keep the narrative/manifest pin honest,
pins the documentation instrument, and regenerates the governed documentation for this release.
See `CHANGELOG.md`.

## Why 1.2.0

1.1.0 and RC3 were siblings. RC3 went to a second verifier and came back with a contract layer,
a release-allowlist mechanism and a 168-check validator; 1.1.0 went the other way and came back
with an attacked, hardened runtime. Merging them surfaced six real defects — the sharpest being a
validator that reported FAIL while nothing ran it, and a no-loss check that silently degraded to
NOT_RUN after any version bump while still satisfying three gates. Both are false-green paths,
and both are closed. See `CHANGELOG.md`.

## Why 1.1.0

RC2 was a complete and internally consistent specification with a genuinely excellent release
integrity engine — its build is bit-for-bit reproducible, and that engine is carried forward
unchanged in behaviour. What it did not have was a way to *use* it. `docs/INSTALLATION_GUIDE.md`
described copying templates into a control namespace; no tool did that. The framework governed
only itself. 1.0.0 closed that gap, which is the difference between a specification and a system.
1.1.0 is what a deliberate adversarial pass over that system found: a rail that could be driven
into an unrecoverable dead end from its own documented happy path, concurrent runs that forked
the source of truth and destroyed records, an authority check defeated by capitalization, and an
`init` that would install project state into the release payload it publishes. Each is fixed at
source, each has a live scenario that fails if it regresses, and the verifier's own checks are
now proven to fire. See `CHANGELOG.md`.

## The three defects that mattered

**Every module narrative was rendering as a code block.** All 96 narrative, blueprint, and test
plan documents had their body indented four spaces, and all 32 frontmatter blocks were
unparseable. A framework whose core control is representation parity had a broken narrative
representation in every single module, and nothing checked for it.

**The release builder mutated the tree it declared immutable.** Running it wrote `__pycache__`
into the source tree and then aborted on its own artifact, violating a control the package
explicitly fixes to `false`.

**Twenty-nine interface schemas were never executed.** Declared, indexed, cross-referenced —
and unexercised, so a wrong contract could sit there indefinitely.

None were found by the package's own tests. All three are now hard findings in
`tools/deep_verify.py`.

## Upgrading

Nothing semantic was removed. `tools/check_no_loss.py --predecessor <rc2-tree>` proves it, and
`governance/SUPERSESSION_LEDGER.json` is empty by design. Existing RC1 or RC2 content maps
one-to-one; see `MIGRATION_GUIDE.md`.

The additions are one module (`10_runtime`), three requirements, and two interfaces. Counts
move from 32/96/29 to 33/99/31. That single module was not a discretionary addition: leaving
the execution layer ungoverned would have contradicted
`ABS.REQ.CANONICAL_MODULE_PACKAGE.001`.

## Verify before you trust

```sh
python3 tools/deep_verify.py            # ten sections, one pass, zero findings required
python3 09_tests_evals/run_all.py
python3 tools/verify_successor_release.py .
```

## What is still pending

Independent exact-hash certification. It is external by construction: gate `C20` remains
`EXTERNAL_HANDOFF_REQUIRED`, `ABS.CFG.RELEASE.SELF_CERTIFICATION` is fixed to `false`, and the
runtime has no code path that can emit a certification claim about an artifact it produced.
`LIMITATIONS.md` states the rest of the boundary.
