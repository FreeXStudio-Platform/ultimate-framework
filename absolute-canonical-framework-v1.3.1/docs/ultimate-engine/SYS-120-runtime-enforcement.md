---
id: SYS-120
classification: public
title: Absolute Runtime and Enforcement
surface: repo
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

# Absolute Runtime and Enforcement

## Runtime contract

The runtime reconstructs project state from files on each command, derives the first unsatisfied
rail step, and permits only the command associated with that step. A refusal changes no project
state and names both the refusing rule and the action that is actually allowed. Read-only commands
remain available before installation and while blocked.

<!-- figure:project-rail -->

The exact source-derived rows, titles, commands, repeatability flags, and reasons are in
[`machine/runtime-model.json`](machine/runtime-model.json). The visual is the required runtime
sequence; it does not imply every step is a one-shot operation. Work, documents, evidence, gates,
and checkpoints can repeat within their governed bounds without permitting forward skips.

## Governed document packages

The subject's own document runtime defines a document as a canonical package rather than a loose
file. The package proceeds from declared scope to narrative, manifest, requirements, blueprint,
visual, machine contract, tests, integration, publication, and changelog. Later representations may
not precede the meaning they express.

<!-- figure:document-rail -->

Creation requires author-specific material that the generators cannot safely invent: owned
requirements, primary failure, source evidence, and exclusions. The generated package uses
explicit template markers for anything that remains author-owned. `doc seal` refuses until every
step is complete, every required artifact exists, the package validates against framework schemas,
positive fixtures pass, negative and adversarial fixtures fail, links resolve, and no template
marker remains.

An unfinishable package can be abandoned only while the document rail is actually stopped at the
authoring or sealing stage. Abandonment records a decision and preserves the package; it is not a
deletion. Abandoning every package does not satisfy the rail because there would be nothing to
review.

## Mutation order and crash recovery

Every governed mutation follows one ordering, and the order is the recovery design.

<!-- figure:governed-mutation -->

Writing the artifact before the ledger means an interrupted operation can leave an artifact the
next command must reconcile. Writing the ledger before state means a later interruption leaves a
durable action whose state update did not land. The reverse ordering would permit state with no
record, which the framework treats as indistinguishable from forged state.

Mutating commands hold an advisory lock on `.absolute/.lock` for the whole read-modify-write
operation. This serializes processes on one host. It does not provide reliable distributed locking
for two hosts sharing a network filesystem.

## Truth ledger and anchors

Each ledger entry contains its sequence, subject, action, actor, state transition, authority and
evidence references, payload identity when applicable, the previous entry digest, and its own
digest. Verification recomputes the chain and reports sequence gaps, changed entries, broken
previous links, unknown actions, and a mismatched or missing head.

A valid local chain cannot prove that a writer did not replace the entire chain and recompute it
from genesis. Detached anchors bind an observed head and entry count. At least one anchor must
survive outside the sole control of the chain writer for full-rewrite detection to add assurance.

## Tree identity and staleness

The project identity covers the work product, frozen project identity, and governed document
packages. Process records such as evidence, gates, checkpoints, reports, work status, and the ledger
are excluded so recording an observation does not invalidate itself. Those excluded records are
individually stamped into the ledger.

The framework deliberately avoids a broad source exclusion list. Version-control metadata,
environments, caches, and derived directories outside the excluded control-plane records
participate in identity. Consequently a Git operation or generated cache can make earlier evidence
stale. This is documented cost, not an accidental side effect. What 1.3.0 changes in practice: with
`.git` moved outside the release payload, an ordinary `git commit` no longer touches the tree this
identity model measures, so routine version-control activity on the payload's own history no longer
invalidates evidence. The deliberate no-exclusion-list design inside the payload is unchanged — a
generated cache or an added file still participates in identity exactly as before.

Evidence history is classified rather than discarded. A method rerun against the new identity
supersedes its older record; a method not rerun leaves its older evidence stale and blocking.

## Cross-representation release pins

### One fact, four representations

The release version exists in four places: the single `VERSION` file, each canonical module's
`MODULE.md` front matter (`framework_release`), each module's `MODULE_MANIFEST.yaml`
(`framework_release`), and `docs/registries/FRAMEWORK.json` (`version` and `release_id`). Before
1.3.0 nothing compared these four representations of the same fact, and all 33 narratives sat two
releases behind their manifests without a single red finding (field-trial finding F-05).

Four `FRAMEWORK_STRUCTURE` codes now compare them, each against a different pair:

- `MODULE_RELEASE_PIN_DRIFT` — a manifest's `framework_release` against `VERSION`;
- `MODULE_NARRATIVE_MISSING` — whether the narrative file exists at all, a precondition for the
  next check;
- `MODULE_NARRATIVE_RELEASE_DRIFT` — the narrative's front-matter `framework_release` against
  `VERSION`;
- `FRAMEWORK_REGISTRY_RELEASE_DRIFT` — `FRAMEWORK.json`'s `version` **and** `release_id` against
  `VERSION`.

The helper that parses a narrative's front matter is `_front_matter()` at `runtime/verify.py` line
77; an audit of the check starts there. Adjacent in the same section, `FRAMEWORK_COUNT_DRIFT`
re-derives `FRAMEWORK.json`'s `counts.modules`, `counts.interfaces`, `counts.core_requirements`,
`counts.profiles`, and `counts.adapters` from the tree, so a registry count cannot drift from what
the tree actually contains either.

<!-- figure:cross-representation-pin -->

### The release allowlist, and why it is now read

`RELEASE_ALLOWLIST.json` declares an exact, fail-closed record set
(`policy: EXACT_RECORD_SET_FAIL_CLOSED`). Through 1.2.0 it still declared `ABS.RELEASE.1.0.0-RC3`
and held 879 records against a 1,079-file tree, because its generator could no longer run and
nothing in the runtime read the file to notice.

Six `FRAMEWORK_GOVERNANCE` codes now read it on every run: `ALLOWLIST_MISSING` (CRITICAL),
`ALLOWLIST_RELEASE_DRIFT` (`release_id`/`candidate_id` against `VERSION`, CRITICAL),
`ALLOWLIST_POLICY_WEAKENED` (CRITICAL), `ALLOWLIST_RECORD_SET_DRIFT` (the recorded set against
every file `root.rglob("*")` finds, `__pycache__` excluded, CRITICAL), `ALLOWLIST_COUNT_DRIFT`, and
the schema check that reports either `ALLOWLIST_SCHEMA_VIOLATION` or, when `jsonschema` itself is
unavailable, `ALLOWLIST_SCHEMA_UNCHECKED`.

The operational consequence is worth stating for the reader rather than leaving implicit: any file
added anywhere in the payload — a build output, an archive cut, a stray run log — is an unrecorded
file and a CRITICAL finding the moment it exists, until the allowlist is regenerated.
[GUIDE-170](GUIDE-170-repository-release.md) states the exact ordering that keeps this from firing
during a version bump.

### The mutation controls that keep these checks alive

A clean deep-verify pass is consistent with two very different situations: every check ran and
found nothing, or a check silently stopped running. `tools/verifier_mutation_check.py` tells the
two apart by planting one known defect at a time in a throwaway copy of the tree and requiring the
named finding code to appear.

The harness now carries **11 mutations across 6 wired sections** (`identity`, `structure`,
`governance`, `representation`, `runtime`, `simulation`), derived from the tool's own `MUTATIONS`
list and `SECTIONS` map rather than typed here. 1.3.0 added three of the eleven —
`narrative_release_pin_drifts_from_manifest_and_VERSION`, `manifest_release_pin_drifts_from_VERSION`,
and `allowlist_record_removed_while_file_remains` — and, with them, newly wired the `structure` and
`governance` sections, which previously had no mutation control at all.

The design detail that makes the harness honest: it imports the **mutated** copy of `runtime.verify`
rather than the harness's own, so a mutation to runtime code is the code under test, not the code
doing the testing. A mutation that crashes the verifier outright counts as undetected, not as a
pass by omission.

### Why two sections are red before the metadata step

On a working tree that has been edited since the last metadata bind, `FRAMEWORK_IDENTITY` and
`SIMULATION` both report findings. **This is ordering, not a defect.**

`FRAMEWORK_IDENTITY` is red because `MANIFEST.json` and `SHA256SUMS.txt` still describe the
predecessor tree until `tools/prepare_release_metadata.py` rewrites them. `SIMULATION` is red for a
related reason: its live scenarios read `.absolute/release/release_identity.json`, which still names
the predecessor release, so `doc seal` reports `DOC_SCHEMA_VIOLATION` against the current release's
schema `const`. The same effect existed at every prior version bump, including 1.1.0 → 1.2.0.

`prepare_release_metadata.py` is run **twice** for the same underlying reason: the gate evidence it
writes is derived from a verification that runs *before* the metadata is rewritten, so the first run
after any payload change necessarily records the pre-change state. Only the second run's evidence
describes the tree the metadata itself now claims.

One mutation control lives in this same window: `seal_accepts_a_package_still_full_of_template_text`
reports MISSED for the identical reason `SIMULATION` is red, and is re-measured once the
orchestrator's metadata step has run. This is a known, bounded window, not a dead control.

The full ordered release procedure — including where the allowlist regeneration and the two
metadata runs sit relative to each other — is [GUIDE-170](GUIDE-170-repository-release.md)'s; it is
not duplicated here.

## Enforcement layers

| layer | what it protects | evidence of operation |
|---|---|---|
| Rail authorization | Prevents skipped lifecycle steps and writes in the wrong state. | A permitted or refused runtime interface instance. |
| Document validation | Prevents incomplete or internally inconsistent canonical packages. | `doc check`, seal result, package findings, and truth stamp. |
| Schema and semantic validators | Prevent malformed registries, manifests, policies, examples, and links. | Deterministic validation report. |
| Evidence gate | Prevents work completion without current evidence. | Gate record bound to the tree identity. |
| Deep verification | Re-derives framework and installed-project claims from raw bytes. | Ordered section report with findings and exit code. |
| Cross-representation pins | Protect one fact — the release version — expressed in module manifests, module narratives, the framework registry, and the release allowlist. | The `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE` check codes named above. |
| Mutation checker | Prevents a silent dead verifier for named defect classes. | 11 planted mutations across 6 sections, each required to be caught. |
| Independent review | Prevents the builder from being the final authority on the exact candidate. | External/fresh evidence; absent here. |

## Commands and error semantics

The CLI exposes installation, status/next/explain, goal lock, work packets, governed documents,
evidence, gates, checkpoint, pass 2, truth inspection/verification/anchors, verification, and
release. It assigns distinct exit codes to rail, ledger, goal, authority, schema, document,
self-certification, and evidence failures so automation can distinguish refusal classes.

The command surface is described by `absolute --help`; the permitted command at a given moment is
described by `absolute next`. Scripts should not infer a write from the help text.

## Dependencies

This document depends on [SYS-110](SYS-110-architecture.md) for semantic ownership and
[GUIDE-140](GUIDE-140-operations-verification.md) for the operator workflow. Change locations are
kept in [REF-130](REF-130-extension-points.md). Repository and release ordering that this document
only assumes are in [GUIDE-170](GUIDE-170-repository-release.md).
