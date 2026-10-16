# Absolute Canonical Framework 1.3.1

**Release:** `ABS.RELEASE.1.3.1`
**Candidate:** `ABS.CANDIDATE.1.3.1`
**Status:** internally verified; independent exact-hash certification remains external and pending.

Absolute keeps project work tied to an approved mission, and refuses to let a completion
claim exist without evidence bound to an exact identity. 1.0.0 was the first release in which
that was *executed* rather than only specified: the `absolute` runtime installs the framework
into a project, drives the authoring sequence, and stamps every governed fact into an
append-only, hash-chained source of truth. 1.1.0 attacked that runtime rather than only
exercising it. 1.2.0 joined it with the `ABS.RELEASE.1.0.0-RC3` machine-contract layer. 1.3.0 is
the first stable release: the tree is placed under version control the way its own integrity
model requires (no `.git` inside the payload, so a working tree verifies), the representation
defects the 2026-09-01 field trial found are closed and guarded by the verifier, every visual
derivative is rendered under one recorded renderer, the release allowlist is a running control
again, and the engine-built documentation set under `docs/ultimate-engine/` is regenerated for
this release and stamped as the source of truth for how the framework is described — see
`CHANGELOG.md` and `docs/ultimate-engine/GUIDE-170-repository-release.md`.
## Start here

1.3.1 is the public-distribution re-issue of 1.3.0: the framework content is unchanged, the
repository is relicensed Apache-2.0 under the FreeXStudio name, and personal and host-specific data
(a copyright holder's first name, example actor names, one build-host path) is removed. See
`CHANGELOG.md`.

```sh
python3 absolute explain                      # the enforced order, end to end
python3 absolute init --project <slug> \
        --mission "<what this project is for>" \
        --profile standard --adapter claude_code
python3 absolute next                         # the single action permitted right now
```

`absolute next` is the whole interaction model. At any moment the rail permits exactly one
next action; anything else is refused with the rule that refused it and the action that is
actually permitted. There is no flag to skip a step.

## Verify this package before you trust it

```sh
python3 09_tests_evals/run_all.py             # the one entry point: runs everything below
python3 tools/deep_verify.py                  # every section, one pass, zero findings required
python3 tools/verifier_mutation_check.py      # proves those checks still fire
python3 tools/verify_successor_release.py .   # exact-hash release integrity
```

Graphviz is required for a zero-finding result: without `dot`, visual parity is recorded as a
finding rather than skipped.

If verification reports a **file-mode mismatch**, the tree was copied by something that did
not preserve UNIX permissions — a network share, a container mount, a restrictive umask. The
declared modes are part of the release, so this is a real failure, not noise. Repair it with
`python3 tools/restore_modes.py` (or inspect first with `--check`) and re-verify. File modes
are not part of the candidate identity, so repairing them cannot change the release hash.

`tools/deep_verify.py` derives every result from raw bytes: it recomputes hashes, executes
fixtures, replays the ledger chain, and runs adversarial scenarios live, requiring each to be
refused. It reports `PASS` only when all sections report zero findings.

A clean report is consistent with two different situations: every check ran and found nothing,
or a check silently stopped running. `tools/verifier_mutation_check.py` distinguishes them by
injecting known defects into a throwaway copy and requiring the check that claims to catch each
one to report it.

## What is here

| Path | Contents |
|---|---|
| `00_kernel` … `04_enforcement` | The 33 canonical module packages: scope, truth, lifecycle, evidence, change, recovery, modularity, verification, control plane, capabilities, knowledge, enforcement. |
| `05_platform_adapters` | Five host adapters. Host-specific behaviour is isolated here and nowhere else. |
| `06_project_profiles` | `minimal`, `standard`, `enterprise`, `audithunt`. |
| `10_runtime` | The runtime's own canonical module package. |
| `runtime/`, `absolute` | The executable runtime and its entry point. |
| `tools/` | Deep verifier, no-loss check, release metadata, release builder, CI pin check. |
| `docs/registries` | Machine-readable topology: modules, interfaces, requirements, concepts, graph. |

## What this package does not claim

It does not certify itself. `ABS.CFG.RELEASE.SELF_CERTIFICATION` is fixed to `false`, and the
runtime has no code path that emits a certification claim about an artifact it produced.
Internal verification is deterministic and reproducible; certification is an external act.

## Baseline provenance

RC1 is the immutable input baseline; RC2 and 1.0.0 are the immutable predecessor releases.
References containing `RC1`, `RC2`, or `1.0.0` are historical provenance and do not identify
this release.
`tools/check_no_loss.py` proves nothing semantic was dropped in the transition.
