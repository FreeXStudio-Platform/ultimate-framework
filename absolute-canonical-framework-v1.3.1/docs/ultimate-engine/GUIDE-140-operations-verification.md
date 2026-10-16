---
id: GUIDE-140
classification: public
title: Absolute Operations and Verification Guide
surface: web
audience: operations
owner: framework-documentation
status: approved
export_allowed: true
last_reviewed: 2026-09-07
version: 1
revision: 0
produced_by: Ultimate Engine 1.0.5
verified_state: verified
---
<!-- artifact-hardened: Approved With Known Risks @ 2e0367a07de3 on 2026-10-16 via three-pass-v1 -->

# Absolute Operations and Verification Guide

## Before installation

Use a mode-preserving copy of the framework release. Verify filesystem modes after any transport
that may drop executable bits. Install the pinned validation dependencies in an environment you can
name and reproduce. Verify Graphviz availability; without `dot`, visual parity is a finding rather
than a passing skip.

Run the package's documented validation entry points and retain stdout, stderr, interpreter path,
Graphviz version, exit code, and the exact tree identity. A command reaching the shell is not proof
that all downstream controls ran. The Graphviz item is now a **pinned** value, not merely a recorded
one — see "The environment a result is bound to" below.

The measured position on this release's working tree is: structure, representation, contracts,
semantics, security, governance, runtime, and the deterministic validator report `PASS`. Identity
and simulation remain red until the orchestrator's release-metadata step runs, and that redness is
ordering, not a defect — [SYS-120](SYS-120-runtime-enforcement.md) explains exactly why. Do not
convert either result into a release claim on its own.

## Select a profile and adapter

The minimal profile preserves the mandatory kernel, control, and enforcement core. Standard and
enterprise compose broader capability, knowledge, adapter, and test layers; enterprise adds
stronger assurance overlays rather than a different kernel. The AuditHunt profile is an
installation mapping only and contains no AuditHunt implementation or certification.

Adapters isolate host translation. Select exactly one host adapter after preflighting the actual
host. A directory in the release does not prove the provider, credential, permission, or external
service exists.

<!-- figure:profile-composition -->

The figure is derived from `PROFILE_ADAPTER_INDEX.json`. The runtime module is resolved through the
selected module set even where a profile record expresses its requirements as domain layers; use
the live profile resolution rather than this matrix alone when installing.

## Install and operate

<!-- figure:operator-path -->

Installation freezes project identity, writes the `.absolute/` namespace, creates the ledger
genesis and first anchor, and refuses a second installation. It does not overwrite existing project
governance outside that namespace.

For an existing project, install in shadow mode, document the incumbent baseline and authority
crosswalk, prove parity, then migrate stable identifiers in a bounded reversible work packet. There
is no automated in-place replacement of an already governed tree.

After installation, use `absolute next` as the interaction contract. Read-only status, explanation,
listing, truth inspection, and non-recording verification remain available for diagnosis. Mutating
commands that do not match the current rail step are refused.

## Verification stack

<!-- figure:verification-stack -->

The derived execution order and function-level sources are in
[`machine/verification-model.json`](machine/verification-model.json).

The aggregate entry point runs five independent control families:

- the deterministic validator over modules, profiles/adapters, example semantics, security hygiene,
  and links;
- successor controls over release identity, CI action pinning, and release-builder protections;
- the deep verifier over identity, structure, representation, contracts, semantics, security,
  governance, runtime, deterministic validation, and live simulations;
- the mutation checker, which plants named defects in throwaway copies and requires the matching
  checker to catch them;
- the V2 contract validator, over the machine-contract layer under
  `governance/coverage_closure_v3/v2_contracts/`.

The order is not a substitute for the output. Each subprocess exit code participates in the
aggregate verdict.

### The cross-representation pin

The release version is expressed in `VERSION`, every module's manifest and narrative, and the
framework registry. Two deep-verifier sections — `structure` and `governance` — read all four
representations and the release allowlist on every run, so a drift in any one of them is a finding
rather than a silent disagreement. One command exercises the whole family:
`PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py`. The exact check codes and what each one
compares are in [SYS-120](SYS-120-runtime-enforcement.md).

### Mutation liveness

`python3 tools/verifier_mutation_check.py` — 11 controls over 6 sections, derived from the tool's
own source rather than typed here. State the honest bound in the same breath: it proves liveness
only for the defect classes listed in that file, and it is not a proof that every check in the
deep verifier is alive.

<!-- figure:mutation-coverage -->

### The V2 contract validator

`python3 tools/validate_v2_contracts.py` has been wired into `09_tests_evals/run_all.py` since
1.2.0. It is worth naming on its own because of the finding that made it necessary: before it was
wired in, it reported `FAIL` while nothing in the aggregate suite ever ran it — an unwired
validator is a false-green path in the suite that is supposed to be the release's single source of
verification truth, not a spare part waiting to be connected.

## What each verification family protects

| family | protects against | does not prove |
|---|---|---|
| Identity/integrity | Wrong release root or bytes, undeclared payload changes, checksum drift. | That the documented behavior is useful or correct in the world. |
| Structure/contracts | Missing packages, malformed schemas/manifests, unresolved interfaces. | Reachability of every external integration. |
| Representation | Narrative/blueprint/machine/visual/test drift and stale generated SVG. | Pixel identity across an unpinned Graphviz version — this release's environment **is** pinned, to 15.1.0 (20260618.0150). |
| Semantics/governance | Contradictory ownership, invalid states, release and supersession rules. | Independent certification. |
| Security | Secret patterns, unsafe paths, prohibited network/credential behavior. | Absence of every unknown vulnerability. |
| Runtime/simulation | Rail refusal, evidence binding, concurrency and self-review controls. | Distributed locking across hosts or correctness of a rollback statement. |
| Cross-representation pins | One fact (the release version) expressed identically across module manifests, module narratives, the framework registry, and the release allowlist. | That the pinned value is the *correct* version — only that it agrees everywhere it is written. |
| Mutation checker | Liveness of the named defect detectors it mutates. | Liveness of every possible check or completeness of mutation coverage. |

## The release procedure, in order

The canonical order — recorded in [`machine/release-model.json`](machine/release-model.json)'s
`procedure` array, which is derived from `RELEASE_PROCEDURE.md`'s own numbered headings rather than
typed here — is: **Environment · Freeze the payload · Regenerate the release allowlist · Bind the
release metadata (twice) · Verify — all of it, in a fresh process · Build · Verify the artifact, not
the working tree · Reproduce · Record · Do not rename it.**

Two rules an operator will hit and should know before starting: the build output path must be
outside the project tree and must not already exist; and both `unzip` and `zipfile.extractall()`
drop the executable bit, which fails release verification unless the extraction applies the
archive's own recorded mode or `tools/restore_modes.py` runs afterward.

Everything else about this procedure — the release allowlist regeneration, the RC2 baseline
dependency, and the GitHub conventions around the sealed artifact — routes to
[GUIDE-170](GUIDE-170-repository-release.md). This guide does not become a second copy of it.

## The environment a result is bound to

Every `.svg` in this release was rendered by Graphviz **15.1.0 (20260618.0150)**, and that is the
version a verifier must install to reproduce a zero-finding representation section. The parity
check strips only Graphviz's own version comment, so it is sensitive to the *build*, not merely to
the renderer's presence — a different build reports `VISUAL_DERIVATIVE_STALE` for every derivative,
and that is a true statement about the environment, not about the sources.

`jsonschema` must be the pinned 4.x line: on 3.2.0 the validator throws
`module 'jsonschema' has no attribute 'Draft202012Validator'` and the whole harness reports `FAIL`.

Without `dot` installed, visual parity is a **finding** (`VISUAL_PARITY_NOT_RUN`), never a silent
skip.

File modes (644/755) are checked and are **not** part of the candidate identity, so
`tools/restore_modes.py` can repair mode drift without changing the release hash. Some network and
virtual filesystems report every file as `600` and ignore `chmod`; that is a known environment
limitation, not a release defect, and is reproducible on a real POSIX filesystem.

## Recovery and maintenance

Use checkpoints for restart-safe recovery and the ledger/state drift report to diagnose interrupted
operations. Re-run evidence methods after anything that changes tree identity. Store an anchor
outside the sole control of the project-tree writer. Treat the recorded rollback statement as
documentation until it has been rehearsed by a separate authorized process.

## Dependencies

This guide depends on [GUIDE-100](GUIDE-100-project-guide.md), the executable sequence in
[SYS-120](SYS-120-runtime-enforcement.md), the current evidence boundary in
[REF-150](REF-150-evidence-limitations.md), and the full release procedure in
[GUIDE-170](GUIDE-170-repository-release.md).
