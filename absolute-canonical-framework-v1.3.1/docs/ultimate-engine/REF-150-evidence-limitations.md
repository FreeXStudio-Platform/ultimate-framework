---
id: REF-150
classification: public
title: Absolute Evidence Limitations and Audit Notes
surface: web
audience: compliance
owner: framework-documentation
status: approved
export_allowed: true
last_reviewed: 2026-09-07
version: 1
revision: 0
produced_by: Ultimate Engine 1.0.5
verified_state: verified
---

# Absolute Evidence, Limitations, and Audit Notes

## How to read this document

`PASS`, `FAIL`, `SKIP`, and `CANNOT_VERIFY` are not interchangeable. A `PASS` is a derived,
reproducible result; a `SKIP` means a check declined to run for a stated reason; `CANNOT_VERIFY`
means this pass had no way to produce the evidence at all. None of the three may stand in for
another.

This document is organized as three blocks, in this order: a **dated history** of what one field
trial measured before this documentation set existed; **what 1.3.0 resolved**, each item with the
defect, the evidence it was real, the fix, and the control that now stops it returning; and **what
remains a limitation**, standing properties of the framework rather than a backlog. The history
block is preserved deliberately — it is dated evidence about an earlier release, not a claim about
this one, and rewriting it to look current would erase the record of what changed.

This document describes release `ABS.RELEASE.1.3.1`, status
`RELEASE_INTERNALLY_VERIFIED_INDEPENDENT_CERTIFICATION_PENDING`.

## The 2026-09-01 field trial — dated baseline

### What was measured, and against what

On 2026-09-01, before any document in this set existed, the Ultimate Engine was pointed at the
framework at release **1.1.0**, laid out as two sibling directories — an `engine/` checkout beside
a directory named `subject/`. That layout is not this repository's layout, and none of the numbers
below describe the framework at 1.3.0.

<!-- figure:baseline-engine-health -->

The engine-on-subject health run reported **3 pass / 28 fail / 7 skip** (exit 1), derived from the
retained baseline record rather than retyped here. Targeted commands discriminated better than the
aggregate figure: `docgen` and `blueprint` correctly refused absent host governance/spec artifacts;
`graphify` mapped the subject successfully; the corpus guards produced a mix of genuine
anti-vacuity failures and foreign-corpus false positives.

The subject's own deep verifier, run in its declared environment, reported 2,688 checks, 35
findings, and 8 of 10 sections passed.

### What the baseline does not measure

The health run measured the **instrument pointed at a foreign project**, so most of its failures
asked the subject to contain the engine repository's own process documents, Git hook source,
renderer packages, and test suite. That is a portability finding about the engine, not a defect in
the framework it was pointed at.

A separate, also-dated result from the same day: a blueprint-only usability test answered 4 of 5
questions correctly on its first pass (the failing question was the enforcement one, because six
verifier sections at the time carried no machine-readable protection claim) and 5 of 5 after each
section was given one. [REF-160](REF-160-agent-blueprint-guide.md) carries that result in full.

## What 1.3.0 resolved

Each item below states the defect, the evidence it was real, the fix, and the control that stops it
recurring. An item with no such control says so plainly rather than being counted as fully closed.

<!-- figure:field-trial-disposition -->

### F-05 — narrative release pins

All 33 `MODULE.md` front matters declared `framework_release: 1.0.0` while every sibling
`MODULE_MANIFEST.yaml` declared the release actually in force, and no check compared the two
representations of the same fact. Both now name `VERSION`, and
`04_enforcement/schemas/module_manifest.schema.json` pins the current release by schema `const`.

New controls, as recorded in [`machine/limitations-register.json`](machine/limitations-register.json)'s
`F-05-narrative-release-pins` row: four `FRAMEWORK_STRUCTURE` check codes
(`MODULE_RELEASE_PIN_DRIFT`, `MODULE_NARRATIVE_MISSING`, `MODULE_NARRATIVE_RELEASE_DRIFT`, and
`FRAMEWORK_REGISTRY_RELEASE_DRIFT` — the fourth pins the framework registry rather than the
narrative, but it closes the same class of drift) plus two mutation controls
(`narrative_release_pin_drifts_from_manifest_and_VERSION`,
`manifest_release_pin_drifts_from_VERSION`), both measured caught.

### F-06 — the test manifest

`09_tests_evals/TEST_MANIFEST.json` named `ABS.TEST.SUITE.FRAMEWORK.RC2` and claimed a 32-module
schema/fixture surface against a 33-module registry. It now names `ABS.TEST.SUITE.FRAMEWORK.1.3.1`,
the measured 33/33/33/33 fixture surface, the V2 contract validator, the cross-representation pin,
and the verifier liveness check.

**This is a repair, not a fully backed resolution, and the register says so plainly:** nothing
under `runtime/`, `tools/`, or `09_tests_evals/` reads this file to check it against the registry it
summarizes. Its content is correct today; nothing stops it drifting again the way F-06 happened the
first time. This limitation is carried forward under "What remains a limitation" rather than closed
here.

### Visual parity reproducibility

All 35 tracked `.dot` sources were rendered by two different Graphviz builds — 32 by 2.42.4 and 3
by 2.43.0 — and neither build was recorded anywhere, so the byte-level parity check passed only on
the original build host. Every derivative is now rendered by one recorded, unanimous build, Graphviz
**15.1.0 (20260618.0150)**, named in `LIMITATIONS.md`.

This resolves the specific defect — an unrecorded, disagreeing set of builds shipping silently — by
making the required build explicit and by re-rendering to make the tree agree with it. The
**dependence on the renderer build itself remains**, stated in full under "What remains a
limitation" below rather than confused with this fix.

### Release-root naming and `.git` inside the payload

`release_tree_integrity` requires the release root's basename to equal `ROOT_NAME` and denylists
`.git` among `FORBIDDEN_PARTS`. At 1.1.0 the release directory was named `subject`; through 1.2.0
the repository's `.git` lived inside the release payload (recorded in the repository's own
`RELEASE_STAMP.json` as a working-tree note dated 2026-09-06). Both conditions are now satisfied,
and a **working tree** can pass `release_tree_integrity` for the first time — previously only a
sealed zip, stripped of version-control metadata, ever could.

### The RC3 release allowlist

Not named in the original field-trial finding list, and worth stating on its own: `RELEASE_ALLOWLIST.json`
declared `ABS.RELEASE.1.0.0-RC3` and held 879 records against a 1,079-file tree, under a policy named
`EXACT_RECORD_SET_FAIL_CLOSED` that nothing enforced. Its generator looked up the baseline by
position in `BASELINE_CHAIN`, which the 1.2.0 merge shifted from RC2 to RC1, so every baseline it
was handed afterward was refused and the file was never regenerated.

It is fixed and now read on every run: `ABS.RELEASE.1.3.1`, its record count read from
`RELEASE_ALLOWLIST.json`'s own `record_count` field — mirrored in
[`machine/release-model.json`](machine/release-model.json)'s `allowlist` rather than typed here,
because the count moves every time a file is added to or removed from the payload — verified
against the baseline by release id rather than by chain position. Six `FRAMEWORK_GOVERNANCE` check codes plus
one mutation control (`allowlist_record_removed_while_file_remains`, measured caught) keep it read
going forward.

### The allowlist generator's RC2 baseline is held by maintainers, not distributed

`generate_release_allowlist.py` refuses any baseline directory not named
`absolute-canonical-framework-v1.0.0-rc.2`, verified against its own detached checksum ledger. That
immutable tree was not previously distributed with this repository, so a fresh clone could verify
the committed allowlist but not regenerate it — a genuine custody gap, not a bug in the generator.

**This remains a limitation of the public distribution (1.3.1).** The public repository does not
ship the predecessor archives, so a clone verifies the committed allowlist but cannot regenerate it;
regeneration is a maintainer operation that needs the checksum-verified RC2 tree. Every chain entry's
hashes are recorded in `BASELINE_CHAIN`, so nothing about verification depends on the archives.
[GUIDE-170](GUIDE-170-repository-release.md) states the exact command and the maintainer workflow.

### The stale regeneration procedure

`docs/ultimate-engine/REGENERATE.md` documented a two-directory layout — a sibling `engine/` beside
a directory named `subject/` — that this repository does not have, so none of its commands could
run as written. It is rewritten for this layout. **This is a repair, not a control-backed
resolution**: nothing mechanically checks that `REGENERATE.md`'s fenced commands still match the
tree the next time the layout changes, so this item is also carried forward under "What remains a
limitation."

## What remains a limitation

Each item below is a **standing property**, not a scheduled fix. None of them is phrased in a way
that would survive being resolved.

### Independent certification

Internal verification demonstrates deterministic consistency in a named environment. It cannot make
the runtime an independent certifier of its own artifact. `ABS.CFG.RELEASE.SELF_CERTIFICATION` is
fixed to `false`, gate `C20` is `EXTERNAL_HANDOFF_REQUIRED`, no runtime code path emits a
certification claim, and the strongest internal state a release reaches is
`READY_FOR_INDEPENDENT_CERTIFICATION_HANDOFF`.

### The ledger detects edits, not a full rewrite

The local hash chain detects an edited, removed, or reordered entry, a sequence gap, a broken
previous-link, or a mismatched head. A writer who can replace the entire chain can recompute every
digest in it. The countermeasure is a detached anchor stored where the chain writer cannot reach it;
an anchor kept only inside the same working tree adds nothing.

### Rollback is declared, not rehearsed

Every work packet carries a `rollback` statement. Its presence is enforced; its feasibility is not,
and the runtime neither executes nor rehearses it. `ABS.MODULE.KERNEL.CHANGE_RECOVERY` specifies
reversible units and rollback rehearsal ahead of what the implementation currently does; this is a
stated gap, not an implied guarantee.

### Concurrency is single-host

Mutating commands are serialized with an advisory `flock` on `.absolute/.lock`, held for the whole
read-modify-write operation. That makes two `absolute` processes on one host safe. It does not
coordinate two hosts sharing a project over a network filesystem, where `flock` semantics are
unreliable or absent.

### Visual parity depends on the renderer build

The byte-level check strips only Graphviz's own version comment from a derivative, so it is
sensitive to the renderer *build*, not merely to its presence. Every derivative in this release is
now recorded as rendered by Graphviz 15.1.0 (20260618.0150) — this corrects the earlier claim that
no version was recorded at all — but a different build that changes layout or numeric formatting
still reports `VISUAL_DERIVATIVE_STALE` for every derivative, which is a true statement about the
verifying environment, not about the sources.

### Tree identity covers everything, and that costs something

No exclusion list exists outside the control-plane process records, deliberately, because an
exclusion list is a place to hide a file from the control meant to cover everything. 1.3.0 removed
the largest instance of this cost by moving `.git` outside the payload; the property itself —
ordinary tooling can still invalidate evidence inside the payload — is unchanged.

### Content truth and external surfaces

The deep verifier proves internal completeness and consistency from raw bytes. It does not prove
that a document is correct about the world. No provider host, remote repository, credential,
production project, publication service, or external certifier is exercised by the package-local
suite.

### Mutation coverage is a list, not a proof

`tools/verifier_mutation_check.py` proves liveness for exactly the defect classes named in its own
`MUTATIONS` list. It is not a proof that every check in the deep verifier is alive, and there are no
unit tests for `runtime/` beyond what these two harnesses — the deep verifier and the mutation
checker — execute.

### The test manifest is a description, not a control

`09_tests_evals/TEST_MANIFEST.json`'s content is correct for this release — suite
`ABS.TEST.SUITE.FRAMEWORK.1.3.1`, the measured 33/33/33/33 fixture surface, the V2 contract
validator, the cross-representation pin, and the verifier liveness check are all named — but nothing
under `runtime/`, `tools/`, or `09_tests_evals/` reads this file to check it against the registry it
summarizes. Its content can drift out from under the registry again, silently, the same way F-06
happened the first time; only the content is fixed, not the property that let it go stale.
`machine/limitations-register.json`'s `F-06-test-manifest-description-only` row classifies this
`REMAINS_A_LIMITATION`, with no control named, because none exists.

### The regeneration procedure is not self-verifying

`docs/ultimate-engine/REGENERATE.md` is rewritten for this repository's current layout and its
fenced commands run as written today. Nothing mechanically checks that they still match the tree
the next time the layout changes — the previous version of this file went stale exactly that way,
undetected, until this pass read it by hand. `machine/limitations-register.json`'s
`stale-regeneration-procedure` row classifies this `REMAINS_A_LIMITATION` for the same reason: a
repair to the content is not a control against recurrence.

### The instrument's own state

**This is the vendored engine's own state, not a claim about the subject release**, and this
document keeps the two separate rather than let a reader conflate them. This number is also
invocation-dependent, so it is stated here with its exact command and root rather than as a bare
figure: from the vendored copy at `engine/`, with `ENGINE_HOST_ROOT` pinned to `engine/` —

```sh
cd engine && PYTHONDONTWRITEBYTECODE=1 ENGINE_HOST_ROOT="$PWD" python3 -m tools.health --json --no-run-log
```

reports **30 pass / 4 fail / 4 skip** (`STRUCT-03`, `STRUCT-04`, `STRUCT-06`, `SUITE-05`), measured
twice with identical results; with `node` absent from `PATH` the `SUITE-07` check skips instead of
passing and the same command reads 29 / 4 / 5, so the pass and skip counts depend on the shell
and the four failing ids are the stable fact. A
standalone checkout of the upstream engine at the pinned commit (its own git root)
instead reports its own unit suite clean — `python3 -m unittest discover -s tools/tests -t .` → **OK,
587 tests**. The two do not disagree about the engine's health; they disagree about where "the
repository root" is. The vendored copy's tests and hook/session checks resolve that root as the
enclosing git top-level, which for a `git subtree --squash` install is this repository, not
`engine/` — a run without `ENGINE_HOST_ROOT` pinned to `engine/`, or a run that treats the payload
as the engine's host root, produces yet another set of numbers for the identical reason, not a
third health state. This is a different measurement again from the 2026-09-01
**engine-on-subject** baseline of 3 pass / 28 fail / 7 skip recorded above — the numbers are close
enough in shape to be transposed by a careless reader, and they answer three different questions:
the engine checking itself from its own root, the engine checking itself from the wrong root, and
the engine checking a foreign project it was never configured for.

The engine limitations the 2026-09-01 field trial surfaced were re-checked against `engine/CHANGELOG.md`'s
`[1.0.5]` entry for this pass. None of that entry's five repaired defects (`OG-244` through `OG-248`
— a `tools.draft check` crash, an ELK layout/placement disagreement, a child process losing its
parent's import path, three graphify builders writing an empty graph and exiting 0, and a
legend-less figure leaving whitespace errors in generated HTML) closes any of the following, so all
are carried forward, each still true as read against the current engine source:

- no documented engine command initializes a new host project's rule layer, system spec, or
  project index from nothing;
- `tools.health`'s engine-on-subject run assumes its `--root` is also the engine repository, and
  cannot evaluate a separate engine installation cleanly;
- the built-in blueprint discovers only tracked Python modules, so most canonical modules in a
  representation-heavy framework like this one are invisible to it;
- `tools.corpus_check` writes a host-local run log under `<root>/.docgen/corpus_check/` by default,
  which changes a subject whose own identity model covers every file under its root;
- present-tense and cross-reference guards can treat a runtime-created `.absolute/` path as an
  absent product claim in a pristine, not-yet-installed release;
- engine guidance disagrees with itself about numeric figure provenance: the document-engine skill
  states an unsourced value fails closed, while `INTERPRETATION.md` and the sidecar-loading code
  treat the convention as advisory;
- a figure directive with no matching sidecar entry is documented as silently omitted rather than
  refused at build time, a false-green shape with no red-first test for it in the engine's own
  audit.

One further limitation is durable enough to restate on its own: the lifecycle describes a final
content-certifying stamp but documents no single command that creates one. Applying one requires
the comment grammar in `tools/docgen/identity.py` and a two-commit procedure.

<!-- figure:assurance-boundary -->

## Dependencies

This evidence record depends on the product boundary in [GUIDE-100](GUIDE-100-project-guide.md),
architecture in [SYS-110](SYS-110-architecture.md), runtime in
[SYS-120](SYS-120-runtime-enforcement.md), verification procedure in
[GUIDE-140](GUIDE-140-operations-verification.md), and repository/release operations in
[GUIDE-170](GUIDE-170-repository-release.md).
