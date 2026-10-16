# Changelog

## 1.3.1 — 2026-10-16 — public distribution

Successor to `ABS.RELEASE.1.3.0`, which remains immutable. Nothing semantic was removed;
`governance/SUPERSESSION_LEDGER.json` is empty by design and `tools/check_no_loss.py` confirms it
against the extracted 1.3.0 tree.

- **Relicensed Apache-2.0.** `LICENSE.md` carries the full Apache License 2.0 text under the
  copyright of FreeXStudio (https://freexstudio.com). 1.3.0 and earlier were "all rights reserved".
- **Personal and host data removed from the payload.** The copyright holder's first name, the actor
  names used as examples in `runtime/engine.py`, `runtime/util.py` and `runtime/verify.py` (now
  `alice`/`Alice`; the control they illustrate — author/reviewer separation compared on a normalized
  identity — is unchanged), and a build-host absolute path embedded in `blueprint/SYSTEM.json` and
  `blueprint/SURFACES.md` by the blueprint builder's error message (the builder now reports the
  exception type only).
- **Documentation set restamped.** The eight governed documents describe the public layout (sealed
  artifacts are release assets; predecessor archives are held by maintainers, their hashes remain
  recorded in `BASELINE_CHAIN`) and were rebuilt, re-archived and re-stamped for this release.
- **Executable modes are tracked in git**, so a fresh clone satisfies `release_tree_integrity`
  without running `tools/restore_modes.py`.
- **Chain extended.** `BASELINE_CHAIN` and `docs/registries/FRAMEWORK.json` now end at 1.3.0.

## 1.3.0 — 2026-09-07 — first stable release

Successor to `ABS.RELEASE.1.2.0`, which remains immutable. Nothing semantic was removed;
`governance/SUPERSESSION_LEDGER.json` is empty by design and `tools/check_no_loss.py` confirms it
against the extracted 1.2.0 tree: every module, requirement, interface, concept, profile, adapter
and governance record carries forward.

1.2.0 joined two lines and verified clean in a sandbox. 1.3.0 is the release in which that tree was
placed under version control the way its own integrity model requires, the two representation
defects the 2026-09-01 field trial found and the verifier could not see were closed, and the
engine-built documentation and blueprint set was regenerated for the release it describes. It is
the first release published to a git remote.

### Changed

- **Repository layout.** The framework's `.git` no longer sits inside the release payload. The
  repository root is the parent directory (`Framework-Canonical/`), the payload is
  `absolute-canonical-framework-v1.3.0/` with no version-control metadata inside it, the sealed
  artifact and its predecessors live in `_release/`, and the documentation instrument is vendored
  at `engine/`. `release_tree_integrity` — which denylists `.git` by design — can now pass on a
  working tree, not only on a sealed zip, and a `git commit` no longer changes the work identity.
- **Every visual derivative re-rendered under one recorded renderer.** The 35 `.svg` files were
  produced by two different Graphviz builds (2.42.4 and 2.43.0); on any other host the byte-level
  parity check failed for all of them. They are now rendered by Graphviz 15.1.0 and the release
  records that version. The check is unchanged: a different renderer still fails it, and that
  dependence is stated in `LIMITATIONS.md` rather than hidden.
- **The Ultimate Engine is pinned.** `engine/` is Ultimate Engine 1.0.5
  (upstream commit `185725a`, vendored by `git subtree`, so the documentation set
  regenerates from a clone without a sibling checkout. `docs/ultimate-engine/REGENERATE.md`
  describes this layout instead of the field-trial one.

### Fixed
- **The release-identity check now admits the engine-derived release model as labeled
  provenance.** `docs/ultimate-engine/machine/release-model.json` mirrors the baseline chain with
  each entry's role, so the stale-identity scan in `release_integrity.py` treats it as it treats
  `docs/registries/FRAMEWORK.json`; without that, the first metadata bind of this release refused
  the tree for naming RC1 in a file that exists to name it.

- **Thirty-three module narratives pinned themselves to a release two versions old, and nothing
  compared them to their manifests.** Every `MODULE.md` front matter said `framework_release:
  1.0.0` while every `MODULE_MANIFEST.yaml` said 1.2.0 (field-trial finding F-05). The deep
  verifier's `FRAMEWORK_STRUCTURE` section now compares the narrative, the manifest, `VERSION`
  and `docs/registries/FRAMEWORK.json` (`MODULE_NARRATIVE_RELEASE_DRIFT`,
  `MODULE_RELEASE_PIN_DRIFT`, `FRAMEWORK_REGISTRY_RELEASE_DRIFT`), and
  `tools/verifier_mutation_check.py` plants both drifts and requires them to be caught. A pin the
  verifier never reads is decoration.
- **The test manifest described a suite that no longer existed.** `09_tests_evals/TEST_MANIFEST.json`
  still named `ABS.TEST.SUITE.FRAMEWORK.RC2`, claimed 32 module schemas and fixtures against a
  33-module registry, and carried a candidate status the release had left behind (field-trial
  finding F-06). It now names the 1.3.0 suite, the measured 33/33/33/33 fixture surface, the V2
  contract validator, the cross-representation pin and the verifier liveness check.
- `RELEASE_NOTES.md` carried the heading `## Why 1.1.0` twice.
- **The deterministic validator broke on the first archived document generation.** The
  documentation engine's `archive cut` keeps a byte-identical snapshot of each governed document
  under `docs/archive/<id>/vN/`; `absolute_validate.py` resolved every relative link from the
  snapshot's own directory and reported 73 broken links the moment the first eight generations
  were cut. A snapshot cannot rewrite its links without ceasing to be a snapshot, so the validator
  now resolves an archived generation's links from the live document's directory and everything
  else exactly as before.
- **The release allowlist was RC3's, and its generator could not run.** `RELEASE_ALLOWLIST.json`
  in 1.2.0 still declared `ABS.RELEASE.1.0.0-RC3` and held 879 records against a 1,079-file
  tree, under a policy named `EXACT_RECORD_SET_FAIL_CLOSED` that nothing enforced. The generator
  had verified its RC2 baseline against `BASELINE_CHAIN[0]`, which on the RC3 line was RC2 and
  after the 1.2.0 merge became RC1, so every baseline it was handed was refused. It now looks the
  anchored RC2 baseline up by release id, its derivative labels are release-neutral
  (`PRESERVED_EXACT_FROM_BASELINE`, `MODIFIED_SINCE_BASELINE`, `NEW_SINCE_BASELINE`,
  `GENERATED_BUILD_CONTROL`), the schema pins the current release, the allowlist is regenerated
  against the hash-verified RC2 tree, and the deep verifier's `FRAMEWORK_GOVERNANCE` section
  asserts the record set against the tree on every run (`ALLOWLIST_RECORD_SET_DRIFT`,
  `ALLOWLIST_RELEASE_DRIFT`, `ALLOWLIST_POLICY_WEAKENED`, `ALLOWLIST_SCHEMA_VIOLATION`), with a
  mutation control that removes a record and requires the drift to be reported.

### Documentation

- The governed documentation set under `docs/ultimate-engine/` (GUIDE-100, SYS-110, SYS-120,
  REF-130, GUIDE-140, REF-150, REF-160) is rewritten for 1.3.0 and joined by **GUIDE-170 —
  repository, versioning and release operations**. Per-document lifecycle records follow below
  this line as the pipeline completes them.
- 2026-09-07, v1, `docs/ultimate-engine/SYS-110-architecture.md` — added "Repository layout" (root
  entries, source vs. derived, the `repository-layout` figure); renamed "Repository and runtime
  boundaries" to "Runtime module boundaries" and moved the repository content out of it; extended
  "Enforcement and tests" with the V2 machine-contract layer; re-scoped the `tools.blueprint`
  Python-only sentence from a one-off observation to a standing property; added GUIDE-170 to
  Dependencies.
- 2026-09-07, v1, `docs/ultimate-engine/SYS-120-runtime-enforcement.md` — added "Cross-representation
  release pins" (one fact/four representations with the `cross-representation-pin` figure, the
  release allowlist as a read section, the mutation controls that keep the checks alive, why two
  sections are red before the metadata step); extended "Tree identity and staleness" with the 1.3.0
  `.git` move; added a cross-representation-pins row to "Enforcement layers"; added GUIDE-170 to
  Dependencies.
- 2026-09-07, v1, `docs/ultimate-engine/REF-130-extension-points.md` — added "Change the release
  version" (pin classes, routed to GUIDE-170); extended step 6 of "Add a new rule" with
  cross-representation revalidation; added derived adapter/profile counts; added GUIDE-170 to
  Dependencies.
- 2026-09-07, v1, `docs/ultimate-engine/GUIDE-140-operations-verification.md` — replaced the stale
  "current observed baseline is red" paragraph with the measured pass/red-until-metadata position;
  extended the verification-family list with the V2 contract validator; added "The
  cross-representation pin", "Mutation liveness" (`mutation-coverage` figure) and "The V2 contract
  validator"; added "The release procedure, in order" and "The environment a result is bound to";
  added GUIDE-170 to Dependencies.
- 2026-09-07, v1, `docs/ultimate-engine/REF-150-evidence-limitations.md` — full rewrite into dated
  2026-09-01 field-trial history, "What 1.3.0 resolved," and "What remains a limitation," each
  finding carrying its evidence and, where resolved, its control.
- 2026-09-07, v1, `docs/ultimate-engine/GUIDE-100-project-guide.md` — replaced "Sources of truth"
  with "Source of truth" (release identity, module semantics, requirements and interfaces,
  verification results, documentation, the two identity systems, with the `authority-of-facts`
  figure); added GUIDE-170 to "Documentation relationships"; re-scoped "What remains unverified" to
  point at REF-150 rather than restate 2026-09-01 findings.
- 2026-09-07, v1, `docs/ultimate-engine/REF-160-agent-blueprint-guide.md` — added a sixth
  routing-table row for the release-versioning question; dated the Stage-5 blueprint-only test
  section; added "What the blueprint pack cannot answer" (`verified: 0`, structurally unreachable);
  added GUIDE-170 to Dependencies.
- 2026-09-07, v1, `docs/ultimate-engine/GUIDE-170-repository-release.md` — new document: why it
  exists, repository layout, the version-bump checklist (`release-pin-surface` figure), the release
  procedure in ten steps mirroring `RELEASE_PROCEDURE.md`'s own numbered headings 0–9, allowlist
  regeneration ordered before the metadata bind (`release-pipeline` figure), the predecessor chain,
  the engine pin, regenerating the documentation set for this layout, GitHub conventions, and what
  "first stable release" means here.

### Verified

Recorded in `RELEASE_NOTES.md` and the repository-level `RELEASE_STAMP.json` from the final
clean-room run, not typed here in advance.

## 1.2.0 — 2026-09-06

Successor to `ABS.RELEASE.1.1.0`, which remains immutable. Nothing semantic was removed;
`governance/SUPERSESSION_LEDGER.json` is empty by design and `tools/check_no_loss.py` confirms it
against the 1.1.0 tree: every module, requirement, interface, concept, profile, adapter and
governance record carries forward.

1.1.0 and `ABS.RELEASE.1.0.0-RC3` were **siblings, not a sequence**. Both forked from RC2. RC3 was
handed to a second verifier and grew a V2 machine-contract layer, a release-allowlist mechanism and
their validator; 1.0.0 and 1.1.0 grew the executable rail. Neither line referenced the other, and
1.1.0 contained no mention of RC3 anywhere. 1.2.0 is the join: the 1.1.0 rail with RC3's contract
layer merged in and made coherent.

### Added

- **The V2 machine-contract layer**, recovered from RC3: 13 machine contracts, their traceability
  matrices, blueprint and visual manifest under `governance/coverage_closure_v3/v2_contracts/`, the
  `coverage_closure_v2` schema set, and positive fixtures in `09_tests_evals/fixtures/v2_contracts/`.
- **`tools/validate_v2_contracts.py`** — 168 checks over the contract layer, including canonical
  parity of every configuration and executable-surface record.
- **The release-allowlist mechanism** — `RELEASE_ALLOWLIST.json`, its schema, and
  `01_control_plane/manifests_releases/tools/generate_release_allowlist.py`.
- **`docs/registries/MACHINE_CONTRACT_INDEX.json`** and `docs/RC3_REMEDIATION_DESIGN.md`.

### Fixed

- **A validator that reported FAIL was never run.** `validate_v2_contracts.py` was not wired into
  `09_tests_evals/run_all.py`, so the whole contract layer could fail silently while the harness
  reported PASS. It is now invoked by the harness and a non-zero exit fails the run. An unwired
  validator is a false-green path, not a spare part.
- **The no-loss check pinned itself to a version it would outlive.** `prepare_release_metadata.py`
  hardcoded its predecessor as `absolute-canonical-framework-v1.0.0-rc.2`, so after any version bump
  the comparison silently degraded to `NOT_RUN` — and `NOT_RUN` still satisfied gates C5, C7 and C17.
  The predecessor is now derived from `BASELINE_CHAIN[-1]`, so it follows every future bump.
- **The canonical configuration registry was missing the fields its own contracts assert.** All six
  `ABS.CFG.RELEASE.*` entries lacked `precedence` and `validation`, so canonical/V2 parity could not
  hold. Both fields are now present and match.
- **Two live executable surfaces were unregistered.** `ABS.SURFACE.CONTRACT.V2.VALIDATE` and
  `ABS.SURFACE.RELEASE.ALLOWLIST.GENERATE` existed as files but were absent from
  `release_surface_registry.json`, leaving 12 registered against 14 declared.
- **`module_manifest.schema.json` pinned `framework_release` to a `const` of the previous version.**
  Bumping the release therefore broke document sealing for every module, which broke the lifecycle
  simulation and the stuck-rail recovery scenario. The pin and all 33 module manifests now agree.
- **A visual derivative did not match its source.** The merged
  `v2_contracts/blueprint/architecture.svg` was hand-authored and its labels had drifted from
  `architecture.dot`; it is now a real graphviz render of that source.

### Verified

`deep_verify` 10/10 sections, 2,773 checks, 0 findings · all 20 gates C0–C19 PASS · 15/15 support
checks PASS · `SHA256SUMS.txt` 1,078/1,078 · mutation check catches every planted defect ·
`check_no_loss` against 1.1.0 reports zero removals · greenfield install, rail refusal
(`ABS.ERR.RAIL_VIOLATION`) and tamper detection (`manifest candidate hash mismatch`) all exercised
live.

## 1.1.0 — 2026-08-17

Successor to `ABS.RELEASE.1.0.0`, which remains immutable. Nothing semantic was removed;
`governance/SUPERSESSION_LEDGER.json` is empty by design.

1.0.0 shipped a runtime that had been exercised but never attacked. This release is the result
of attacking it. Every defect below was reproduced before it was fixed, and every fix has a
live scenario in `tools/deep_verify.py` that fails if it regresses.

### Fixed

- **The rail could be driven into an unrecoverable dead end from its own documented happy
  path.** `absolute doc new` has three required arguments and four optional ones, and every
  optional one it omits becomes template text that `doc seal` correctly refuses. `S5`/`S6`
  require *every* document to be authored and sealed, and no command could edit, replace, or
  remove one — so `absolute next` named `doc seal` as the single permitted action while
  `doc seal` could never succeed. The rail's own guidance string omitted all four flags. The
  project was bricked, with the whole interaction model pointing at a wall. `doc new` now
  demands the content the seal will demand, where refusing is free; `absolute doc abandon
  --id <slug> --reason "<why>"` closes a package that still cannot be finished, as a recorded
  decision rather than a deletion; and the guidance strings name the flags. A live positive
  control drives the rail into the dead end and requires it to be walked out of.
- **Concurrent runs forked the source of truth and destroyed records.** `Ledger.append`
  computed `prev_entry_sha256` from a prior read and identifiers came from a state counter, with
  no lock anywhere. Eight parallel `evidence add` calls produced four surviving records of
  eight, duplicate sequence numbers, and a chain that could never verify again. Every mutating
  operation now holds an exclusive `flock` on `.absolute/.lock` for its whole duration.
- **A crash between the ledger write and the state write made the runtime assert something
  false.** Artifacts are written before the ledger entry and the ledger entry before the state
  update — deliberately, so a death mid-operation leaves a record rather than unrecorded state.
  But the identifier counter did not advance, so the next run reused the id, overwrote the
  record, and left the ledger stamping two different methods under one evidence id while
  `truth verify` reported `PASS`. Identifiers are now allocated past whatever is already on
  disk, and `absolute status` reports the unapplied update on a `RECOVERY:` line — the module
  docstring already promised that visibility.
- **The pass-2 authority check was defeated by capitalization.** `alice` authored the material
  and `Alice` was accepted as its independent reviewer. Actor names are now compared on a
  normalized identity, folding case, surrounding and internal whitespace, and `-`/`_`/`.`.
- **`absolute init` installed project state into the framework's own release tree.** There was
  no guard: it wrote thirteen entries into `.absolute/`, violating
  `ABS.CFG.RELEASE.SOURCE_TREE_MUTATION` and destroying the exact candidate identity the
  package publishes. `init` now refuses at or inside the framework root and says why.
- **`verify --record` bypassed the rail.** `record_verification` never authorized, so running
  it immediately after `init` satisfied `S12` — a terminal, non-repeatable step — while the
  rail sat at `S2`. It is now authorized as the rail command it declares.
- **Two declared interfaces were provided by nothing.** `ABS.IFACE.RUNTIME.EXECUTE` and
  `ABS.IFACE.TRUTH.STAMP` were declared *provided* by `ABS.MODULE.RUNTIME.EXECUTOR`, indexed,
  and given fixtures, but no code path ever emitted a conforming instance — the unbacked claim
  this framework exists to refuse. Every rail decision and every ledger append now emits one to
  `.absolute/interfaces/`, and deep verification validates each instance against the registry
  schema.
- **`DECISION_RECORDED` and `.absolute/decisions/` were dead surface.** Both are now written by
  `doc abandon`, which is a decision with a rationale and needed a durable record.
- **The documented test path was weaker than the real one.** `READ_ORDER.md` names
  `09_tests_evals/run_all.py`, which did not run `tools/deep_verify.py`; the CI example did not
  either, and did not install Graphviz, so it could never reach zero findings. `run_all.py` now
  runs the deterministic validator, the successor controls, the deep verifier, and the mutation
  check, and fails if any of them fails.
- **`RELEASE_PROCEDURE.md` named none of the release tools.** It required six hash-binding
  files to exist without saying that `tools/prepare_release_metadata.py` writes them, and never
  mentioned `deep_verify.py`, `check_no_loss.py`, `restore_modes.py`, or the two-run rule. It is
  rewritten so every step names its command.
- **Eight documents had no mention of the runtime.** `TROUBLESHOOTING.md`, `MAINTENANCE.md`,
  `GLOSSARY.md`, `CAPABILITY_AND_SECURITY_GUIDE.md`, `DOCUMENTATION_BLUEPRINT_VISUAL_GUIDE.md`,
  `SECURITY.md`, and `MIGRATION_AND_SUPERSESSION_NOTES.md` predated the execution layer.

### Added

- `absolute doc abandon` — the only corrective command. It repairs the step the rail is stopped
  on without advancing it, is refused for a sealed package and without a stated reason, and is
  reported by `status`, the pass-2 review, and the release manifest.
- `tools/verifier_mutation_check.py` — the deep verifier is the only test of the runtime, so
  nothing caught the deep verifier being wrong. A `PASS` on a clean tree is consistent with a
  check having silently stopped running. This injects eight known defects into a throwaway copy
  one at a time and requires the check that claims to catch each one to report it.
- Regression guards in `FRAMEWORK_RUNTIME` for every fix above: unserialized mutations, an
  unrepairable rail dead end, and raw actor comparison are each a `CRITICAL` finding.
- Eight new adversarial scenarios and a second positive control in `SIMULATION`, which now runs
  twenty.

### Changed

- Release identity `ABS.RELEASE.1.1.0`, package root `absolute-canonical-framework-v1.1.0`,
  module manifests pin `framework_release: 1.1.0`. Behaviour changed and surface was added, so
  shipping under the 1.0.0 identity would itself have been the kind of claim this framework
  refuses. `BASELINE_CHAIN` gains 1.0.0 as an immutable predecessor release.
- `LIMITATIONS.md` states three gaps that were previously implied rather than written down: the
  project lock is per-host and does not coordinate over a network filesystem; the tree identity
  includes derived directories such as `.git`, so a commit makes evidence stale; and the
  `rollback` string recorded on every work packet is never performed or rehearsed by anything —
  it is documentation, not a tested control.

## 1.0.0 — 2026-08-17

Successor to `ABS.RELEASE.1.0.0-RC2`, which remains immutable. Nothing semantic was removed;
`tools/check_no_loss.py` verifies this against the predecessor tree and
`governance/SUPERSESSION_LEDGER.json` is empty by design.

### Added — the execution layer

- `runtime/` and the `absolute` entry point: install a project, lock a goal, open work packets,
  author governed documents, record evidence, evaluate gates, checkpoint, review, verify, release.
- An append-only hash-chained source of truth at `.absolute/truth/LEDGER.jsonl`, with detached
  anchor receipts that detect a full-chain rewrite.
- A thirteen-step rail that permits exactly one next action and refuses anything else, naming both
  the refusing rule and the permitted action.
- An eleven-step document authoring sequence producing a complete canonical module package, with
  unresolved-marker and schema conformance both blocking `doc seal`.
- `10_runtime`: the runtime's own canonical module package. Adding it was not optional —
  `ABS.REQ.CANONICAL_MODULE_PACKAGE.001` requires every material module to be governed, and an
  ungoverned execution layer would have contradicted the framework's central claim.
  Adds `ABS.CONCEPT.RUNTIME_EXECUTION`, three requirements, and two interfaces
  (`ABS.IFACE.RUNTIME.EXECUTE`, `ABS.IFACE.TRUTH.STAMP`). Counts move to 33 modules,
  99 core requirements, 31 interfaces.
- `tools/deep_verify.py`: whole-system verification in one pass across ten sections, deriving every
  result from raw bytes and running twelve adversarial scenarios live, each required to be refused,
  plus a positive control that the full lifecycle completes.
- `tools/check_no_loss.py`: proves no module, requirement, interface, concept, profile, adapter, or
  governance record was dropped relative to a predecessor.
- `tools/prepare_release_metadata.py`: the only supported way to re-bind the six hash-binding files.
- `09_tests_evals/interface_fixtures/`: a positive and negative instance for all 31 interface schemas.
- `tools/restore_modes.py`: re-applies the declared executable surface after a copy that did not
  preserve UNIX permissions, which otherwise fails release verification with no stated remedy.
- `docs/RUNTIME_GUIDE.md`.

### Fixed

- **Narrative rendering.** All 96 `MODULE.md`, `BLUEPRINT.md`, and `TEST_PLAN.md` files had their
  body indented four spaces, which renders as a code block, and all 32 `MODULE.md` frontmatter
  blocks were unparseable because their keys and closing delimiter were indented. Every heading in
  every module narrative was invisible to a conformant renderer. Representation parity is a core
  control, and its own narrative representation was broken. A `markdown_structure` check now makes
  this class of defect a hard finding.
- **Release builder mutated the tree it declared immutable.** `build_release.py` wrote
  `__pycache__` into the source tree on import and then aborted on its own artifact via the
  denylist, violating `ABS.CFG.RELEASE.SOURCE_TREE_MUTATION`. Every tool entry point now sets
  `sys.dont_write_bytecode` before importing a sibling, the deep verifier asserts it, and the
  denylist message now says what to do.
- **Twenty-nine unexercised interface schemas.** They were declared, indexed, and referenced by
  module integration files, but no fixture ever validated against them, so a wrong contract could
  not be detected. Each now has a fixture pair and the deep verifier fails on a missing one.
- **Circular gate evidence.** Gate evidence that names the hash of the tree containing it has no
  fixed point. Evidence moved to `.absolute/release/gate_evidence/` as release metadata, excluded
  from the candidate digest and bound instead by `gate_binding.json`, which records each file's
  digest and is itself verified.
- **Self-referential prebuild gates.** `C11` and `C16`–`C19` were supported by checks that read
  their own recorded status, so a single `FAIL` became permanent. Prebuild verification is now
  scoped to the payload; manifests, the checksum ledger, and the gate binding are asserted by the
  full post-build pass.
- **Module denominator.** The validator's hard-coded `32` is now a named constant asserted against
  the tree, so a package disappearing is a failure rather than a smaller number nobody notices.
- Schema `const` values for `framework_release` updated from `1.0.0-rc.2` to `1.0.0`.

### Changed

- Release identity `ABS.RELEASE.1.0.0`, package root `absolute-canonical-framework-v1.0.0`,
  manifest schema `1.3.0`. Baseline provenance is now an ordered chain: RC1 as immutable input
  baseline, RC2 as immutable predecessor release.
- Status is `RELEASE_INTERNALLY_VERIFIED_INDEPENDENT_CERTIFICATION_PENDING`. It stops short of
  certified on purpose; see `LIMITATIONS.md`.
- Gate evaluation distinguishes *superseded* evidence (method re-run against the current identity,
  informational) from *stale* evidence (method not repeated, blocking). Treating all history as
  blocking made a gate unpassable forever after the first tree change; ignoring all history would
  have let coverage disappear silently.
- The deep verifier runs the shipped deterministic validator and adopts its errors, guaranteeing it
  is a strict superset rather than a parallel implementation that can drift.

## 1.0.0-rc.2 — 2026-08-15

- Established the explicit successor identity `ABS.RELEASE.1.0.0` and package root `absolute-canonical-framework-v1.0.0-rc.2`.
- Preserved the immutable RC1 baseline and labeled all remaining RC1 references as input provenance or historical lineage.
- Replaced the legacy authority-bypassing release builder with a gate-bound, non-mutating, deterministic builder and a hardened verifier.
- Regenerated release identity metadata, the payload manifest, and the per-file checksum ledger from actual successor bytes.
- Added canonical C0–C20 gate bindings, legacy-gate mapping, dependency/bypass validation, transitive invalidation records, and deterministic release tests.
- Kept independent exact-hash certification external; this release candidate does not claim `FINAL` or `CERTIFIED`.

## 1.0.0-rc.1 — 2026-08-13 — historical immutable baseline

- Constructed the first clean canonical release candidate from concept-level source reconciliation.
- Added 32 synchronized module packages and 96 canonical requirements.
- Added deterministic schemas, validators, negative/adversarial fixtures, graph registries, profiles, adapters, examples, and release tooling.
- Added minimal, standard, enterprise, and AuditHunt installation profiles.
- Preserved provider specifics in replaceable adapters and optional systems in add-ons.
- Retained non-final status because external independent exact-hash verification was unavailable in the execution environment.
