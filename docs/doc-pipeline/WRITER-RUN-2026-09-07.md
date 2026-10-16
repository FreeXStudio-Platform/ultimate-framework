# Writer run record — 1.3.0 documentation pass 1 (Sonnet), 2026-09-07

Scope actually executed: outline §I steps **1 through 11**. Steps 12–21 (blueprint/graphs rebuild,
project-index registration, lifecycle archive cuts + changelog lines, second regeneration pass,
hygiene sweep, deep-verify, allowlist regeneration, this pass's own acceptance-criteria closure)
are explicitly **not** done here — see "Handoff to pass 2" at the end.

Environment used for every command below (never varied):

```sh
export PYTHONDONTWRITEBYTECODE=1
export ENGINE_HOST_ROOT="$PWD/absolute-canonical-framework-v1.3.0"
export ENGINE_AUTHORED_DOCS_ROOT="docs/ultimate-engine"
export PYTHONPATH="$PWD/engine"
```
Run from the repository root `<repo>`
(never written into any document — payloads and sidecars only ever carry the repository-relative
form).

---

## Step 1 — starting state

- `git status --short absolute-canonical-framework-v1.3.0` → empty (clean payload, as FACTS §0.12
  records: the orchestrator's commit `d647a61` left it clean).
- `git -C absolute-canonical-framework-v1.3.0 ls-files | wc -l` → **1079** (matches outline §0.4).
- `find absolute-canonical-framework-v1.3.0 -name __pycache__` → empty.

## Step 2 — Addendum 1 / Addendum 2 resolution

`docs/doc-pipeline/FACTS-2026-09-07.md` was read in full: it contains **both** Addendum 1 (release
allowlist repaired) and Addendum 2 (post-architect-pass corrections, including the predecessor-chain
correction that supersedes outline §B.6's "allowlist generator needs a tree this repository does not
contain" H3). Both addenda were treated as ground truth throughout, and Addendum 2's correction is
applied to REF-150 as directed (see the REF-150 section below and "Deviations").

## Step 3 — derive script extended (§D-1…D-14, one edit)

File: `absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py`.
All fourteen items implemented in a single rewrite:

| # | what was added |
|---|---|
| D-1 | `TODAY` renamed to `RETRIEVED`, set to `"2026-09-07"`, with a module comment on why it stays a literal constant. |
| D-2 | `release_version()` reads `VERSION`; feeds `inventory.release_version` (`"1.3.0"`). |
| D-3 | `inventory.canonical_requirements` renamed to `core_requirements`; added `requirements_total`, `successor_governance_requirements` from `FRAMEWORK.json.counts`; added an `assert` that `core_requirements` equals `FRAMEWORK.json`'s own count. |
| D-4 | `graphviz_version()` regexes the version comment from every tracked `*/blueprint/*.svg`, raises on non-unanimity; feeds `inventory.graphviz_version` / `graphviz_renderer_unanimous`. |
| D-5 | `verifier_check_codes()` walks each `section_*` function's `section.expect`/`section.fail` calls by AST and returns `{function: [codes]}`; merged onto each row of `verification_model.framework_sections_in_execution_order` as `check_codes`. |
| D-6 | `mutation_controls()` reads `MUTATIONS` (AnnAssign) and `SECTIONS` (Assign/Dict) from `tools/verifier_mutation_check.py` by AST; writes `verification_model.mutation_controls` (`controls`, `wired_sections`, `count`). |
| D-7 | `release_pins()` buckets tracked files carrying the release version into 9 classes (`version_file`, `release_tooling`, `registries`, `schemas`, `module_manifests`, `module_narratives`, `test_manifest`, `governance`, `allowlist`); writes `machine/release-model.json.pins`. |
| D-8 | `release_procedure_steps()` parses `^## (\d+)\. (.+)$` from `RELEASE_PROCEDURE.md`; writes `machine/release-model.json.procedure` and backs the `release-pipeline` Mermaid figure. |
| D-9 | Fourth `extension_points.changes` entry, `kind: "release_version"`, `also_update` generated from `release_pins()`'s bucket names. |
| D-10 | `question_coverage()` derives the heatmap matrix from REF-160's own routing-table assignments (6 questions × 6 machine artifacts) instead of a hand-typed literal. |
| D-11 | `DOCUMENTS` gained the GUIDE-170 entry; `depends_on` on all eight recomputed to match outline §G.1's graph exactly. |
| D-12 | `repository_model()` and `engine_pin()` both probe `ROOT.parent/".git"` and degrade to `{"observed": false, "reason": ...}` rather than raising when the payload is extracted without its repository. `engine_pin()` additionally regexes the vendoring commit's message for the upstream `ultimate-engine@<sha>` reference. |
| D-13 | `baseline-engine-health`'s `data_sources.ref` changed from the out-of-payload `evaluation-evidence/baseline-engine-health.txt` to `docs/ultimate-engine/machine/evaluation-baseline.json`. Audited every other `source(...)` call — no second instance of the leak class existed. |
| D-14 | New spec file `GUIDE-170-repository-release_spec.json` (figures `release-pipeline`, `release-pin-surface`); `limitations-register.json` registered as a **read** input in `main()`, exactly like `evaluation-baseline.json`. |

Both preservation rules were kept: `sys.dont_write_bytecode = True` still sits at module load, and
`tracked_files()` is untouched (`git -C ROOT ls-files`, no `rglob`).

## Step 4 — `machine/limitations-register.json` authored

New file, 24 findings, each with `id`, `first_recorded`, `statement`, `disposition` (one of
`RESOLVED_IN_1_3_0` / `REMAINS_A_LIMITATION` / `INSTRUMENT_STATE`), `evidence`, and — for every
`RESOLVED_IN_1_3_0` row — a `control` naming the check code or tool that prevents recurrence. The
file states its own rule in a header `note` field: a resolved row with no control is
`REMAINS_A_LIMITATION` instead, even when the surrounding document narrates the repair under a
"what 1.3.0 resolved" heading.

Disposition counts feeding the `field-trial-disposition` figure: `RESOLVED_IN_1_3_0` 5,
`REMAINS_A_LIMITATION` 10, `INSTRUMENT_STATE` 9.

## Step 5 — derive script run, diff inspected

```
$ python3 absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py
derived documentation model: 1079 tracked files, 33 canonical modules, 284 authority edges, 8 figure sidecars
EXIT: 0
```

`git diff --stat -- absolute-canonical-framework-v1.3.0/docs/ultimate-engine` (before any document
was hand-edited):

```
 GUIDE-100-project-guide_spec.json           |  28 +-
 GUIDE-140-operations-verification_spec.json |  56 ++-
 REF-130-extension-points_spec.json          |  12 +-
 REF-150-evidence-limitations_spec.json      |  40 +-
 REF-160-agent-blueprint-guide_spec.json     |  45 ++-
 SYS-110-architecture_spec.json              |  34 +-
 SYS-120-runtime-enforcement_spec.json       |  22 +-
 machine/document-index.json                 |  48 ++-
 machine/domain-model.json                   |   6 +-
 machine/extension-points.json               |  14 +
 machine/inventory.json                      |  31 +-
 machine/verification-model.json             | 181 ++++++++-
 scripts/derive_documentation_model.py       | 421 +++++++++++++++++++--
 13 files changed, 833 insertions(+), 105 deletions(-)
```
Plus 4 new untracked files: `GUIDE-170-repository-release_spec.json`,
`graphs/source/release-pipeline.mmd`, `machine/limitations-register.json`,
`machine/release-model.json`.

Spot-checked before writing any prose: `inventory.json` matches outline §0.4 exactly (1079 tracked
files; `.py` 30, `.md` 280, `.json` 596, `.svg` 39, `.dot` 35, `.jsonl` 4; domains `01` 113, `04`
133, `09` 94); `representation-mix`'s top-8 list has `.jsonl` (4) ahead of nothing named `.mmd` (also
4, correctly excluded by the alphabetical tiebreak, matching §0.4's called-out effect);
`verification-model.json` shows 4 new `section_structure` codes, 7 `section_governance` codes
(5 core + 2 schema-fail-path), 11 mutation controls over 6 wired sections; `release-model.json`'s
`engine_pin` correctly resolved `upstream_commit: "185725a"` from the vendoring commit message;
`release-model.json.pins` shows 33/33 module manifests/narratives and a `total_pinned_files` of 76.

## Step 6 — seven documents rewritten, in dependency order

Order used: **SYS-110 → SYS-120 → REF-130 → GUIDE-140 → REF-150 → GUIDE-100 → REF-160**, exactly as
directed.

- **SYS-110-architecture.md** — added H2 "Repository layout" (H3s "What each root entry is" / "What
  is source and what is derived") with the new `repository-layout` figure; renamed "Repository and
  runtime boundaries" to "Runtime module boundaries" and moved the repository half out of it; added
  the V2 machine-contract-layer sentence to "Enforcement and tests"; re-scoped the
  `tools.blueprint`-Python-only sentence from "during this exercise" to a standing property with a
  REF-160 cross-reference; added GUIDE-170 to Dependencies. Architectural thesis, semantic
  containers (other than the one sentence), interface topology, and change risk kept verbatim.
- **SYS-120-runtime-enforcement.md** — added H2 "Cross-representation release pins" with four H3s
  ("One fact, four representations" + `cross-representation-pin` figure; "The release allowlist,
  and why it is now read"; "The mutation controls that keep these checks alive"; "Why two sections
  are red before the metadata step"); added one sentence to "Tree identity and staleness" about the
  1.3.0 `.git` move; added a cross-representation-pins row to "Enforcement layers" and rephrased the
  mutation-checker row to cite the derived count; added GUIDE-170 to Dependencies. Runtime contract,
  governed document packages, mutation order, truth ledger, commands, unchanged.
- **REF-130-extension-points.md** — added H2 "Change the release version" (pin classes named from
  the derived model, routes ordering to GUIDE-170); extended step 6 of "Add a new rule" to mention
  cross-representation revalidation; added derived adapter/profile counts (5, 4) as sentences rather
  than a table change; added GUIDE-170 to Dependencies. Everything else unchanged in substance.
- **GUIDE-140-operations-verification.md** — replaced the stale "current observed baseline is red"
  paragraph with the measured PASS/red-until-metadata position; extended the verification-family
  list to five (added the V2 validator) and added two new H3s ("The cross-representation pin",
  "Mutation liveness" with the new `mutation-coverage` figure, "The V2 contract validator"); added
  two new H2s, "The release procedure, in order" (8-step one-line summary, explicitly routing
  everything else to GUIDE-170) and "The environment a result is bound to" (Graphviz build,
  jsonschema pin, `VISUAL_PARITY_NOT_RUN`, file-mode/candidate-identity note); corrected the
  representation-family table row to state the environment **is** pinned; added GUIDE-170 to
  Dependencies.
- **REF-150-evidence-limitations.md** — full rewrite per the outline's explicit instruction, into
  three ordered blocks: dated 2026-09-01 field-trial history; "What 1.3.0 resolved" (7 H3s — the
  outline's 6 plus one, see "Deviations"); "What remains a limitation" (8 H3s — the outline's 8 minus
  the RC2-custody one, which Addendum 2 moved into "resolved"; see "Deviations"). Every dated claim
  cites its date; every "resolved" item either names its control or explicitly says it is a repair,
  not a control-backed resolution (F-06 test-manifest and the stale-regeneration-procedure items).
  Engine-limitation bullets were checked against `engine/CHANGELOG.md`'s `[1.0.5]` entry
  (`OG-244`…`OG-248`) before being carried forward — none of the five repaired engine defects closes
  any of the eight limitation bullets, so all eight are retained, restated with the reason each is
  instrument state rather than a subject claim.
- **GUIDE-100-project-guide.md** — replaced "Sources of truth" with the new "Source of truth" H2
  (six H3s — Release identity / Module semantics / Requirements and interfaces / Verification
  results / Documentation / The two identity systems — plus the new `authority-of-facts` figure);
  named the release identity/status once in "Purpose and boundary"; named the pinned Graphviz build
  in step 1 of "How someone uses it"; added GUIDE-170 to "Documentation relationships"; re-scoped
  "What remains unverified" to point at REF-150's "What 1.3.0 resolved" for the dated record rather
  than re-quoting stale 2026-09-01 findings. Written last of the seven so it could cite all of them.
- **REF-160-agent-blueprint-guide.md** — added the sixth routing-table row (release-versioning
  question → `release-model.json` → GUIDE-170's figures); retitled and dated the Stage-5 section
  ("What the 2026-09-01 blueprint-only test showed"), stating plainly it has not been re-run against
  1.3.0; added the new H2 "What the blueprint pack cannot answer" (the `verified: 0`, structurally
  unreachable arithmetic; the `gatekeepers` derivation rule; the GUIDE-170 cross-reference on what a
  new governed owner can and cannot change about that arithmetic); added GUIDE-170 to Dependencies.

## Step 7 — GUIDE-170 written and staged

New file `absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md`,
following §B.8 section-by-section: Why this document exists; Repository layout (linking, not
duplicating, SYS-110's figure); The version-bump checklist (pins table + `release-pin-surface`
figure, mass-rewrite surface, the ordering rationale); The release procedure, in order (9 H3s, `0.`
through `8.`, mirroring `RELEASE_PROCEDURE.md`'s own headings, `release-pipeline` figure at the
end); The predecessor chain (RC1/RC2 role distinction, where sealed predecessors live, the
Addendum-2 custody correction); The engine pin; Regenerating the documentation set for this layout
(single fenced block); GitHub conventions (written as conventions, never past tense — no push or tag
has happened); What "first stable release" means here; Dependencies.

```sh
$ git add absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md
$ git status --short absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md
A  absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md
```
(The sandboxed shell refused to write `.git/index.lock` on the first attempt — `Operation not
permitted` — so this one `git add` ran with the sandbox override. No other git-state-changing
command in this pass used the override; no commit was made.)

## Step 8 — README.md and REGENERATE.md rewritten

- **README.md** — dropped all field-trial framing; names all eight documents by id and title; points
  the regeneration line at GUIDE-170's own section instead of the retired `REGENERATE.md` procedure.
- **REGENERATE.md** — rewritten as a short pointer, not a second copy of the command sequence: it
  states that the regeneration sequence now lives in GUIDE-170 (a governed document, so it carries
  this set's own lifecycle), explains why `system.spec.json`'s `documentation-derivation` container
  reassigned its owning document to GUIDE-170, and says GUIDE-170 is authoritative if the two ever
  disagree. See "Deviations" for why this became a pointer rather than a rewritten full procedure.

## Step 9 — `system.spec.json` edited (edits 1–3 only)

- Edit 1: `system.name` → `"Absolute Canonical Framework 1.3.0"`.
- Edit 2: `_readme` reworded to describe the vendored-engine reality (`"...derived from the tracked
  tree by the vendored Ultimate Engine instrument..."`) instead of "the sibling Ultimate Engine";
  the substantive sentence about Python-derived vs. registry-derived topology is unchanged.
- Edit 3: `documentation-derivation`'s `document` field reassigned from
  `"docs/ultimate-engine/REGENERATE.md"` to `"docs/ultimate-engine/GUIDE-170-repository-release.md"`.
- No `depthFloor` value touched (verified by diff: only `system.name`, `_readme`, and one
  container's `document` field changed).

## Step 10 — strict build + check, all eight

First strict-build attempt caught two real defects before they could reach pass 2:

1. `REF-150-evidence-limitations.md` referenced figure id `ID` — an artifact of literally writing
   `` `<!-- figure:ID -->` `` inside a prose bullet (describing the engine's figure-directive
   syntax) with no escaping; the parser reads any `<!-- figure:` sequence anywhere in the raw
   Markdown, including inside a backtick span. Fixed by rephrasing the bullet without the literal
   comment syntax.
2. `GUIDE-170`'s header `surface: repo` (as literally specified in outline §B.8's one-line
   audience/surface note) disagreed with `DOC_MANIFEST.md`'s registered `surface: web` for the
   `GUIDE` type prefix — a `manifest_drift` finding, blocking under `--strict`. Fixed by setting
   `surface: web`, matching GUIDE-100 and GUIDE-140's own headers. See "Deviations."

After both fixes:

```sh
$ python3 -m tools.docgen.cli --strict build <all eight paths> --formats html,json
built 8 doc(s) in 3.394s — 0 reused from cache, 8 rebuilt
EXIT: 0
```

`python3 -m tools.docgen.cli check <doc>.md` for each of the eight — every one:
```
docgen check: PASSED — header + taxonomy-prefix + manifest-drift + rulebook hash-gate (<doc>.md)
EXIT: 0
```

## Step 11 — indexes rebuilt

```sh
$ ( cd absolute-canonical-framework-v1.3.0 \
    && python3 -m tools.docgen.cli index docs/ultimate-engine -o docs/ultimate-engine/DOCS_INDEX.html \
    && python3 -m tools.docgen.cli content-index --docs-root docs/ultimate-engine -o docs/design/doc-system/CONTENT_INDEX.json )
wrote index: docs/ultimate-engine/DOCS_INDEX.html (8 public document(s) indexed)
wrote content-index: docs/design/doc-system/CONTENT_INDEX.json (8 public doc(s) listed, 2 non-public excluded)
EXIT: 0
```
Confirmed all eight ids appear in `DOCS_INDEX.html` and `CONTENT_INDEX.json` lists exactly 8
entries.

## Hygiene, checked at the end of this pass

```sh
$ find absolute-canonical-framework-v1.3.0 -name __pycache__      # empty
$ ls absolute-canonical-framework-v1.3.0/.docgen                  # No such file or directory
$ ls absolute-canonical-framework-v1.3.0/.health                  # No such file or directory
$ ls absolute-canonical-framework-v1.3.0/graphify-out             # No such file or directory
$ find absolute-canonical-framework-v1.3.0 -name .docgen_cache.json  # empty
$ git status --short --ignored=matching absolute-canonical-framework-v1.3.0 | grep '^!!'
!! absolute-canonical-framework-v1.3.0/.claude/
```
`.claude/` is confirmed empty (`find ... -type f` returns nothing) — the harness-created, harmless,
gitignored artifact FACTS §0.8 describes. Nothing else ignored sits inside the payload.

## Self-check against §H forbidden claims (informal — the verifier's own grep is authoritative)

Grepped all eight new/rewritten `.md` bodies for: `certifi` (every hit is either the sanctioned
status string, a negation, or discussion of the stamp/certification *rule* — none asserts the
framework or a document IS certified); `/Users/` (zero hits); `subject/` (two hits, both in
REF-150, both explicitly framed as the pre-1.3.0 layout, not the current one);
`ChatGPT-Framework-Test` (zero hits); `ABS.TEST.SUITE.FRAMEWORK.RC2` (one hit, in REF-150's F-06
history, explicitly past tense before the sentence that gives the current suite id); every `1.1.0`/
`1.2.0` mention (all are either baseline-chain enumeration, explicitly dated field-trial context,
or "since 1.2.0"/"through 1.2.0" historical framing — none claims the current release is 1.1.0 or
1.2.0).

## Files added or changed (final state after step 11)

**Modified (37):**
```
absolute-canonical-framework-v1.3.0/docs/design/doc-system/CONTENT_INDEX.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/DOCS_INDEX.html
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.{html,json,md,_spec.json→GUIDE-100-project-guide_spec.json}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/README.md
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REGENERATE.md
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.{html,json,md}
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/document-index.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/domain-model.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/extension-points.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/inventory.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/verification-model.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py
absolute-canonical-framework-v1.3.0/system.spec.json
```

**Added (6, one already `git add`-ed per step 7):**
```
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md   (staged)
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.html
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release_spec.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/source/release-pipeline.mmd
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/limitations-register.json
absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/release-model.json
```

**Also written by this pass, tracked under `docs/doc-pipeline/` (outside the payload):**
```
docs/doc-pipeline/WRITER-RUN-2026-09-07.md   (this file)
```

## Deviations from the outline, and why

1. **REF-150's H3 count changed from the outline's 6-resolved/8-remains split to 7-resolved/7-remains**,
   because FACTS Addendum 2 explicitly instructs exactly this: "the predecessor archives now live in
   `_release/predecessors/`, so a clone CAN regenerate the allowlist after extracting RC2 … Addendum
   2 wins and you must write it that way." The outline's §B.6 draft text for the "remains" H3 "The
   allowlist generator needs a tree this repository does not contain" describes the pre-Addendum-2
   state. I wrote a new "resolved" H3, "The allowlist generator's RC2 baseline is now in the
   repository," and did not write the corresponding "remains" H3, per the task instruction that
   "nothing in the 'remains' block may be phrased in a way that would survive being fixed" — keeping
   that H3 in "remains" would have been exactly such a violation.
2. **GUIDE-170's header `surface` is `web`, not the `repo` the outline's one-line audience/surface
   note specifies**, because `DOC_MANIFEST.md` (out of scope to edit — explicitly listed under §H.10
   / the non-negotiables) fixes `surface: web` for every `GUIDE`-prefixed document, and building
   with `surface: repo` is a blocking `manifest_drift` finding under `--strict`. Matches GUIDE-100
   and GUIDE-140's own existing headers.
3. **A REF-150 bullet was rephrased to avoid a literal `<!-- figure:ID -->` HTML comment inside a
   backtick span**, because `tools.docgen`'s figure-reference scan is not backtick-aware — it reads
   any `<!-- figure:` sequence in the raw source. The sentence's meaning is unchanged; only the
   literal comment syntax was removed.
4. **REGENERATE.md became a short pointer to GUIDE-170 rather than a full rewritten command block**,
   reasoned from `system.spec.json` edit 3 itself: `documentation-derivation`'s owning document
   moved to GUIDE-170 specifically because `REGENERATE.md` carries no doc-system header and cannot
   appear in the completeness lifecycle table. Keeping a second full copy of the command sequence in
   an ungoverned file the completeness report cannot see would recreate exactly the "two normative
   copies of one procedure" pattern §H.7 forbids for `RELEASE_PROCEDURE.md`/GUIDE-170 and
   `LIMITATIONS.md`/REF-150. The single authoritative sequence now lives only in GUIDE-170.
5. **`question_coverage()`'s derived mapping does not reproduce the old hand-typed matrix's exact
   cell pattern** (the old "enforcement" row lit both the verification and runtime columns; the
   derived version lights only the column REF-160's own routing table assigns to that question). The
   outline's instruction (D-10) is to derive strictly from "the machine artifact(s) named in
   REF-160's routing table," which is what the new function does; the old matrix's extra cell looks
   like exactly the kind of hand-typed drift D-10 exists to remove, not a pattern worth preserving.
6. **`verifier_check_codes()` reads the code argument at index 1 for `section.expect(...)` calls and
   index 0 for `section.fail(...)` calls**, not "index 1" uniformly for both as one literal reading
   of D-5's wording could suggest. Applying index 1 uniformly would collect several `fail()` calls'
   *message* strings (e.g. `"symlinks are not permitted in a release tree"`) as if they were check
   codes, which is verifiably wrong against the source (`fail(code, message, ...)` — code is
   `fail`'s first positional argument). The per-call-kind indexing is the reading that produces
   correct data and was used throughout.

## What I could not do / did not attempt

Nothing in my assigned scope (steps 1–11) was left undone. The following are explicitly out of
scope for this pass and are not attempted, per the task's own instruction not to do steps 12–21:
the blueprint/graphs rebuild, `PROJECT_INDEX.json` registration, per-document `archive cut` +
`CHANGELOG.md` lines, the required second full regeneration pass, the final hygiene/deep-verify/
allowlist-regeneration sequence, and any stamping. `verified_state: unverified` and `status: review`
are unchanged on all eight documents, as directed.

---

## Handoff to pass 2

**State pass 2 inherits:**
- All eight governed documents exist, strict-build clean, `check` clean, with `last_reviewed:
  2026-09-07`, `produced_by: Ultimate Engine 1.0.5`, `version: 0`, `revision: 0`,
  `verified_state: unverified`, `status: review`. **No document has been archived (`archive cut`)
  and no document has a stamp.** `version`/`revision` will change the moment pass 2 (or the
  orchestrator) runs `archive cut` — do that only after a document's body is truly final.
- `machine/release-model.json` and `machine/limitations-register.json` are new; both are read by
  the derive script, not written by it — `limitations-register.json` is hand-authored and should
  only be **appended to**, never rewritten wholesale, if pass 2 finds another finding worth adding.
- `system.spec.json` has its 3 authored edits applied and zero `depthFloor` changes; pass 2's
  blueprint build/layout/verify/completeness run (step 12) is the first time this pass's container
  reassignment (`documentation-derivation` → GUIDE-170) is actually exercised end to end.
- `git status --short absolute-canonical-framework-v1.3.0` currently shows exactly the 43 paths
  listed above (37 modified + 6 added, one of the six already `git add`-ed). Nothing else is dirty
  or untracked inside the payload.

**What pass 2 must do (outline §I steps 12–21):**

12. `python3 -m tools.blueprint build && layout && verify && completeness` — read the ratchet
    verdict. Expect: containers 7 (unchanged), Python modules 30 tracked / 28 mapped (the two new
    `.py` files fall under existing container package prefixes per §F), `verified` stays 0 and
    structurally unreachable (0 of 28 nodes at rung 4+) — say so, don't apologize for it.
    `documentation-derivation`'s lifecycle row should move from 3/6 (this pass didn't touch archive
    cut) toward higher once pass 2 does its own lifecycle steps, and it gains a *governed* owner for
    the first time.
13. Render the four standalone Mermaid sources — `domain-dependencies`, `project-rail`,
    `document-rail`, and the **new** `release-pipeline` — with `engine/tools/mermaid-engine/render.mjs`,
    and rebuild the structure graph with `engine/tools/graphify/build.mjs`. Copy exactly what
    GUIDE-170's own "Regenerating the documentation set for this layout" section names — never
    `build.log`.
14. Register GUIDE-170 and `MERMAID-release-pipeline` in `PROJECT_INDEX.json` (currently 14
    artifacts, will become 16), refresh every `summary` field off `release_version` (this pass's
    `inventory.json` already has it derived — read it rather than re-deriving), then `dashboard` and
    `verify --scan docs/ultimate-engine`.
15. Lifecycle steps pass 2 owns: `archive cut` for all eight documents **after** confirming no
    further body edits are needed (this pass explicitly left `version: 0`/`revision: 0` for exactly
    this reason); one `CHANGELOG.md` line per document under the existing 1.3.0 `### Documentation`
    heading (the heading and its placeholder sentence already exist in the payload's
    `CHANGELOG.md` — do not create a second one). **Do not stamp** — the orchestrator stamps after
    the Opus verification pass, per WRITER-BRIEF §7.
16. Re-run steps 5 and 10–14. **This is not optional**: derived counts include the documents
    themselves (word counts land nowhere derived, but the archive/version bump from step 15 changes
    file counts and `PROJECT_INDEX.json`'s own summaries), so the first pass through 10–14 is never
    a fixed point. `git diff --stat` after the second pass must be empty.
17. Hygiene sweep — repeat exactly what this pass already checked clean once (see "Hygiene, checked
    at the end of this pass" above); it can be reintroduced by anything pass 2 runs.
18. `PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py` from inside the payload — quote every
    section verdict including the two expected-red ones (`FRAMEWORK_IDENTITY`, `SIMULATION`; both
    documents explain why this is ordering, not a defect — verify the explanation still matches
    reality once the orchestrator's metadata step has or has not run yet).
19. **Last payload step:** regenerate the release allowlist from inside the payload —
    `python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2`
    then the same with `--check`. The extracted RC2 tree already exists at
    `predecessor/absolute-canonical-framework-v1.0.0-rc.2` (confirmed present, alongside
    `predecessor/absolute-canonical-framework-v1.2.0`, both gitignored) — no extraction step is
    needed before this command, only after a clean clone.
20. Re-run `deep_verify.py` after step 19 — `FRAMEWORK_GOVERNANCE` is stale the instant the
    allowlist regenerates.
21. This file (`WRITER-RUN-2026-09-07.md`) is the record pass 1 promised; pass 2 should extend it or
    write its own dated continuation rather than overwrite it — the orchestrator needs both this
    pass's file list and pass 2's for the metadata and release steps.

**One fact pass 2 should not have to re-derive:** the RC2 predecessor tree needed for both step 3
of the release procedure (allowlist regeneration) and `check_no_loss.py` is **already extracted**
locally at `predecessor/absolute-canonical-framework-v1.0.0-rc.2` (sibling to
`predecessor/absolute-canonical-framework-v1.2.0`), confirmed present during this pass. This is
local working-tree convenience, gitignored, and not itself evidence of anything — but it means pass
2 does not need to re-run the extraction before exercising step 19.

---

# Pass 2 (Sonnet), 2026-09-07 — blueprint, graphs, lifecycle, allowlist, deep-verify, corpus-check

Scope executed: outline §I steps **12 through 21**, exactly as assigned. Starting state matched
pass 1's handoff precisely: `git status --short absolute-canonical-framework-v1.3.0` showed the 43
paths pass 1 listed (37 modified + 6 added, `GUIDE-170-repository-release.md` already `git add`-ed),
`git -C absolute-canonical-framework-v1.3.0 ls-files | wc -l` → **1080** (1079 + the staged
`GUIDE-170.md`), `find absolute-canonical-framework-v1.3.0 -name __pycache__` → empty.

Environment for every command (identical to pass 1's, never varied):

```sh
export PYTHONDONTWRITEBYTECODE=1
export ENGINE_HOST_ROOT="$PWD/absolute-canonical-framework-v1.3.0"
export ENGINE_AUTHORED_DOCS_ROOT="docs/ultimate-engine"
export PYTHONPATH="$PWD/engine"
```

Run from the repository root `<repo>` unless
a step is marked "from inside the payload."

---

## Step 12 — blueprint build / layout / verify / completeness

```
$ python3 -m tools.blueprint build
blueprint: wrote COMPLETENESS.md, SURFACES.md, SYSTEM.json, SYSTEM.md, system.d2, system.mmd
EXIT: 0

$ python3 -m tools.blueprint layout
blueprint layout: wrote system.layout.json, system.layout.svg (8 node(s), 609×704, 0 placement finding(s))
EXIT: 0

$ python3 -m tools.blueprint verify
blueprint verify: clean — 7 container(s), 30 module(s), 297 document(s), 6 derived file(s)
EXIT: 0

$ python3 -m tools.blueprint completeness
completeness: ratchet memory UNAVAILABLE — historical spec blob 3ecedf3077e8:system.spec.json is
  unreadable — the object store is incomplete (partial clone or missing objects), so the
  highest-ever floor cannot be known — loosening cannot be detected this run
completeness: 30 node(s) — sketched 7 · documented 23 · verified 0
EXIT: 0
```

**Ratchet verdict, quoted honestly and diagnosed, not apologised for:** `ratchet memory:
UNAVAILABLE`. Root cause, reproduced directly: this repository's payload has no `.git` of its own
(1.3.0's repository-layout change — the payload sits inside a parent repo). `_historical_floors()`
computes `rel` as the spec path **relative to the payload root** (`system.spec.json`) and then calls
`git -C <payload> show <commit>:<rel>`. `git -C <payload> ls-tree`/`log -- <rel>` resolve `<rel>`
relative to the invocation **directory** and succeed (confirmed:
`git -C absolute-canonical-framework-v1.3.0 ls-tree 3ecedf3077e8 -- system.spec.json` finds the
blob), but `git show <rev>:<path>` resolves a **blob-syntax path** relative to the repository
**top-level** unless prefixed `./`, so the identical `<rel>` fails there
(`fatal: path 'absolute-canonical-framework-v1.3.0/system.spec.json' exists, but not
'system.spec.json'`) — confirmed by direct reproduction of both commands. The function's own
`ls-tree`/`show` split (added specifically to distinguish "absent at this commit" from "object store
truncated") is defeated by this specific git path-resolution asymmetry, which did not exist under
the pre-1.3.0 layout where the scanned root **was** the git top-level. This is the same class of
finding as Addendum 3 (engine self-tests assume "repository root" is the enclosing git top-level) —
an **engine-portability finding**, not a subject defect, not fixed here (`engine/tools/blueprint/`
is instrument code, out of writer scope). Consequence: `verify` still enforces spec-vs-tree
agreement and exits 0; only the ratchet's cross-run **loosening** detection is unavailable this run.
No `depthFloor` was touched by this pass (confirmed by diff — `system.spec.json`'s only changes are
pass 1's three edits), so there is nothing to loosen in the first place.

**Node states:** `sketched` 7 (23%) · `documented` 23 (77%) · `verified` 0 (0%) — exactly as §F
predicted (documented moved 21→23 for the two newly-mapped `.py` modules,
`01_control_plane.manifests_releases.tools.generate_release_allowlist` and
`tools.validate_v2_contracts`, both rung 2; node total 28→30). `verified` stays **0** and is
structurally unreachable this release: 0 of 30 nodes are at rung 4+, and all seven containers have
no rung-4 module at all — arithmetic, not an effort gap. `documentation-derivation` gained a
*governed* owner (GUIDE-170) for the first time, which is what moves the charter's purpose-2
governed-document count from 7 to 8; it does not and cannot move `verified`.

**Containers: 7, unchanged. Python modules: 30 tracked / 28 mapped**, exactly as §F predicted — the
two new `.py` files fall under existing container package prefixes and no container gained or lost
a package.

---

## Step 13 — Mermaid renders + structure graph

```
$ node engine/tools/mermaid-engine/render.mjs .../document-rail.mmd -o .../document-rail.svg
wrote svg: .../document-rail.svg
EXIT: 0
$ node engine/tools/mermaid-engine/render.mjs .../domain-dependencies.mmd -o .../domain-dependencies.svg
wrote svg: .../domain-dependencies.svg
EXIT: 0
$ node engine/tools/mermaid-engine/render.mjs .../project-rail.mmd -o .../project-rail.svg
wrote svg: .../project-rail.svg
EXIT: 0
$ node engine/tools/mermaid-engine/render.mjs .../release-pipeline.mmd -o .../release-pipeline.svg
wrote svg: .../release-pipeline.svg
EXIT: 0

$ ENGINE_HOST_ROOT="$ENGINE_HOST_ROOT" node engine/tools/graphify/build.mjs
[/graphify] mapped .../absolute-canonical-framework-v1.3.0
[/graphify] 705 nodes · 705 links → engine/graphify-out/{graph.json,graph-data.js,build.log}
EXIT: 0
```

Copied exactly the artifacts GUIDE-170's own "Regenerating the documentation set for this layout"
section names, **never `build.log`**: `graph.json`, `graph-data.js` (from `engine/graphify-out/`,
gitignored inside `engine/`, outside the payload) and `graph-view.html` + `vendor/force-graph.min.js`
+ `vendor/3d-force-graph.min.js` (static, copied verbatim from `engine/tools/graphify/`, matching the
pattern the committed copies already followed) into
`absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/structure/`.

---

## Step 14 — PROJECT_INDEX registration

Registered 16 artifacts total (was 14): re-registered all seven governed documents' `summary` field
(1.1.0 → 1.3.0), `DOCS-INDEX`'s summary ("seven" → "eight governed documents"), bumped `updated` to
2026-09-07 on the three existing Mermaid entries / `GRAPH-STRUCTURE` / `BLUEPRINT-SYSTEM` /
`BLUEPRINT-LAYOUT`, and added two new entries: `GUIDE-170` (document,
`docs/ultimate-engine/GUIDE-170-repository-release.html`) and `MERMAID-release-pipeline` (mermaid,
`docs/ultimate-engine/graphs/rendered/release-pipeline.svg`). `register` replaces the whole record
(verified from `tools/project_index/index.py`'s `register_artifact`), so every call passed every
field, including the original `created` date, to avoid silently blanking it.

```
$ python3 -m tools.project_index.cli register ... (×16)
registered: <id> (<type>) -> <path>            [×16, all EXIT 0]

$ python3 -m tools.project_index.cli dashboard
wrote dashboard: .../PROJECT_INDEX.html
EXIT: 0

$ python3 -m tools.project_index.cli verify --scan docs/ultimate-engine
16 artifact(s) registered
OK — every registered artifact resolves to a real file, no duplicates.
EXIT: 0
```

---

## Step 15 — lifecycle: date confirmed, archive cut ×8, changelog

`last_reviewed: 2026-09-07` confirmed already present on all eight headers (pass 1's work).

```
$ python3 -m tools.docgen.cli archive cut <path> --date 2026-09-07     (×8)
cut GUIDE-100 v1 from docs/ultimate-engine/GUIDE-100-project-guide.md (sha256 ee4a4edf1361…, commit d647a61)
cut SYS-110   v1 from docs/ultimate-engine/SYS-110-architecture.md (sha256 69350594cfef…, commit d647a61)
cut SYS-120   v1 from docs/ultimate-engine/SYS-120-runtime-enforcement.md (sha256 4760f39c1517…, commit d647a61)
cut REF-130   v1 from docs/ultimate-engine/REF-130-extension-points.md (sha256 6cb5217c7c16…, commit d647a61)
cut GUIDE-140 v1 from docs/ultimate-engine/GUIDE-140-operations-verification.md (sha256 cedf2d2d1eb4…, commit d647a61)
cut REF-150   v1 from docs/ultimate-engine/REF-150-evidence-limitations.md (sha256 ac0f4896b16e…, commit d647a61)
cut REF-160   v1 from docs/ultimate-engine/REF-160-agent-blueprint-guide.md (sha256 4b30fdcbbaef…, commit d647a61)
cut GUIDE-170 v1 from docs/ultimate-engine/GUIDE-170-repository-release.md (sha256 cbf378006ff2…, commit d647a61)
EXIT: 0 (all eight)
```

Every cut names commit `d647a61` — the last commit that touched each file — because nothing in
either pass has committed since; this is the tool reading real git history honestly, not a defect.
`version`/`revision` bumped `0`→`1` on all eight headers; `docs/archive/<ID>/v1/<file>.md` +
`docs/archive/<ID>/HISTORY.md` created for all eight (16 new files).

Re-ran the strict build + check for all eight (required after `archive cut` bumps the header) —
covered under step 16 below, since it is the same command the outline's step-16 re-run repeats.

**CHANGELOG.md** — appended nine lines under the existing 1.3.0 `### Documentation` heading (one
per document, in dependency order matching pass 1's own write order), each naming the date, version,
file and the sections it changed, ending with GUIDE-170's line. This is the **only** edit made to
`CHANGELOG.md`, and it was made **after** the existing placeholder paragraph, before `### Verified` —
no other line in the file was touched.

`verified_state: unverified` and `status: review` left untouched on all eight, as directed. No
document was stamped.

---

## Step 16 — second regeneration pass (steps 5, 10–14 again)

Ran the full sequence (derive → strict build ×8 + check ×8 → index + content-index → blueprint
build/layout/verify/completeness → Mermaid renders + graphify → project-index register/dashboard/
verify) **three times** total in immediate succession, not two, because the first run surfaced a
real (if small) non-determinism worth recording rather than silently absorbing:

1. **Run 1** (first execution of the complete, correctly-ordered sequence after archive cut):
   `derived documentation model: 1080 tracked files, 33 canonical modules, 284 authority edges, 8
   figure sidecars`; `blueprint verify: clean`; all builds/checks/verifies exit 0.
2. **Run 2:** identical inputs, run immediately after. `git diff`-equivalent hash comparison
   (`shasum -a 256` over every file under `docs/ultimate-engine/`, `blueprint/`, `PROJECT_INDEX.*`,
   comparing Run 1 vs Run 2) found **two files differing**:
   `docs/ultimate-engine/graphs/structure/graph.json` and `graph-data.js` — different
   `content_version` each run, same node/link counts (705/705 confirmed both runs). Root cause: my
   own out-of-order manual work immediately before writing the reusable regeneration script (I had
   re-run the strict build manually right after `archive cut`, but had not yet re-run the derive
   script first) left the structure-graph output one step behind the canonical `5 → 10 → 11 → 12 →
   13 → 14` order; Run 1 was the first execution in the *correct* order and its own graphify output
   had not yet settled relative to that reordering.
3. **Run 3:** identical inputs, run immediately after Run 2. Hash comparison Run 2 vs Run 3: **zero
   files differ**, across every file under `docs/ultimate-engine/`, `blueprint/`, and
   `PROJECT_INDEX.{json,html}` — genuine fixed point.

**Reading, honestly:** the non-determinism was in *my own execution order*, not in the tooling —
once the canonical order ran twice back-to-back (Run 2, Run 3) with no other change in between, the
output was byte-identical, including `graph.json`'s `content_version`. `tracked_files` legitimately
moved 1079→1080 between pass 1's step-5 run and this pass's (because `GUIDE-170.md` is now staged) —
that is not non-determinism, it is the documented "derived counts include the documents themselves"
effect (WRITER-BRIEF §8), confirmed stable at 1080 across Runs 1–3.

After archive-cut lifecycle work (step 15 above, `git add docs/archive/` — see "Deviations" below),
the full sequence was run **twice more** (Run 4, Run 5) to re-establish the fixed point against the
new tracked-file count: `derived documentation model: 1096 tracked files` both runs; full hash
comparison Run 4 vs Run 5 → **zero files differ**. Fixed point confirmed a second time, this time
inclusive of the archive directory's effect on every derived count.

`git status --short` after the final run lists only the 74 paths in "Files added or changed" below —
identical in shape (adds/mods, not a new file) to what step 15 produced, confirming the second full
pass changed no additional file identities, only content that was expected to re-derive.

---

## Step 17 — hygiene sweep

```
$ find absolute-canonical-framework-v1.3.0 -name __pycache__          # empty
$ ls absolute-canonical-framework-v1.3.0/.docgen                       # No such file or directory
$ ls absolute-canonical-framework-v1.3.0/.health                       # No such file or directory
$ ls absolute-canonical-framework-v1.3.0/graphify-out                  # No such file or directory
$ ls absolute-canonical-framework-v1.3.0/.blueprint                    # No such file or directory
$ find absolute-canonical-framework-v1.3.0 -name .docgen_cache.json    # empty
$ git status --short --ignored=matching absolute-canonical-framework-v1.3.0 | grep '^!!'
!! absolute-canonical-framework-v1.3.0/.claude/
```

One deviation from pass 1's clean state, found and fixed: the harness had also created a **second**,
nested, empty `.claude/.cc-writes` under `docs/ultimate-engine/.claude/` (from `cd`-ing into that
directory for `tools.project_index.cli` calls). Confirmed empty at every depth
(`find ... -mindepth 0` listed only the two directory entries, no files), then removed — not because
it was harmful (`ALLOWLIST_RECORD_SET_DRIFT` enumerates files, and it held none), but so
`git status --short --ignored=matching` shows **at most** the one documented empty `.claude/`
FACTS §0.8 describes, matching the outline's literal wording. `engine/graphify-out/` (outside the
payload, gitignored by `engine/.gitignore`) was left as-is — it is instrument output, not payload
content, and is explicitly the documented landing spot for graphify's regeneration (graph-engine
SKILL.md: "Output always lands in this engine's own `graphify-out/`... safe to point at a read-only
or sensitive directory").

---

## Step 18 — deep_verify (before allowlist regeneration)

From inside the payload:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py
  FAIL  FRAMEWORK_IDENTITY                 checks=0     findings=1
  PASS  FRAMEWORK_STRUCTURE                checks=1018  findings=0
  PASS  FRAMEWORK_REPRESENTATION           checks=236   findings=0
  PASS  FRAMEWORK_CONTRACTS                checks=418   findings=0
  PASS  FRAMEWORK_SEMANTICS                checks=14    findings=0
  PASS  FRAMEWORK_SECURITY                 checks=1104  findings=0
  FAIL  FRAMEWORK_GOVERNANCE               checks=36    findings=1
  PASS  FRAMEWORK_RUNTIME                  checks=43    findings=0
  FAIL  FRAMEWORK_DETERMINISTIC_VALIDATOR  checks=7     findings=74
  FAIL  SIMULATION                         checks=20    findings=4
FAIL  sections=6/10  checks=2896  findings=80
EXIT: 1
```

Four sections red at this point, three of them expected/explained and one genuinely new:

- **`FRAMEWORK_IDENTITY`** (`TREE_INTEGRITY_FAIL`, "manifest release identity mismatch") — expected,
  per FACTS: `MANIFEST.json`/`SHA256SUMS.txt` still describe 1.2.0 until
  `tools/prepare_release_metadata.py` runs (orchestrator's step). Ordering, not a defect.
- **`SIMULATION`** (4 findings: `SIMULATION_HAPPY_PATH_BROKEN`, `SIMULATION_STUCK_RAIL_UNRECOVERABLE`,
  two `SIMULATION_WRONG_REFUSAL`) — all four cite the identical underlying cause,
  `DocumentStepError: ... DOC_SCHEMA_VIOLATION at MODULE_MANIFEST.yaml`, which is exactly FACTS'
  documented explanation (`.absolute/release/release_identity.json` still names 1.2.0). Ordering,
  not a defect.
- **`FRAMEWORK_GOVERNANCE`** (`ALLOWLIST_RECORD_SET_DRIFT`, listing the newly-created
  `docs/archive/**` files as unrecorded) — expected per the outline's own step 20 text ("step 18's
  governance result is stale the moment step 19 runs"): the allowlist was not yet regenerated to
  reflect the archive cuts. Resolved by step 19/20 below.
- **`FRAMEWORK_DETERMINISTIC_VALIDATOR`** (`checks=7 findings=74`) — **genuinely new, not previously
  documented anywhere in this repository.** See the dedicated finding below.

### New finding: archive-cut snapshots break `04_enforcement/validators/absolute_validate.py`'s link check

73 of the 74 findings (the 74th is the summary wrapper `VALIDATOR_NONZERO_EXIT`) are individual
`broken link` errors, **100% of them under `docs/archive/**`, 0% elsewhere**. Root cause, confirmed
by reading the validator source: `check_links()` does `for p in root.rglob("*.md")` and resolves
every `[text](target)` relative to `p.parent`. This is correct for live documents but breaks for
archive snapshots: `archive cut` copies a document's body verbatim into
`docs/archive/<ID>/v1/<file>.md`, preserving its original relative links (`SYS-120-runtime-
enforcement.md`, `machine/module-dependencies.json`, …) unchanged — links that resolved from
`docs/ultimate-engine/` do not resolve from `docs/archive/<ID>/v1/`.

**This was never seen before because it could not have been**: `docs/archive/` does not exist in
either predecessor release (confirmed: `find predecessor/absolute-canonical-framework-v1.2.0/docs/
archive` and the RC2 equivalent both report "No such file or directory"). The eight `archive cut`
invocations in step 15 above are **the first time this lifecycle step has ever been exercised** on
this framework's governed documents — the bug exists in the interaction between two features that
had never previously run against each other.

**This is real, reproducible, and out of my write scope to fix.** `04_enforcement/validators/
absolute_validate.py` is subject code (inside the payload, not vendored `engine/`), but it is not
among the paths this pass is permitted to write (`docs/ultimate-engine/**`, `docs/archive/**`,
`docs/design/doc-system/CONTENT_INDEX.json`, `blueprint/**`, `PROJECT_INDEX.*`, one `CHANGELOG.md`
heading, `RELEASE_ALLOWLIST.json` via its generator only). I did **not** attempt a workaround (e.g.
hand-editing the archived snapshot bodies) — that would invalidate the sha256 each `HISTORY.md`
already recorded for the original body, which is a worse defect than the one it would "fix." I
flagged this via `spawn_task` (task `task_c1df0020`, title "Fix archive-snapshot false positives in
absolute_validate.py links check") with the root cause, evidence, and three candidate fixes
(recommending: exclude `docs/archive/**` from `check_links`'s scan, matching how this codebase
already treats historical/append-only text specially elsewhere). **Acceptance criterion 6
("deterministic validator PASS") is not met, and cannot be met from within this pass's write scope**
— see "What I could not do" below.

---

## Step 19 — release allowlist regeneration (LAST payload step, run twice: before and after `git add docs/archive/`)

First invocation hit a real sandbox/hygiene issue, fixed before proceeding:

```
$ python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2
Traceback ...
ValueError: bytecode cache in the release tree: 01_control_plane/manifests_releases/tools/__pycache__/release_integrity.cpython-314.pyc
EXIT: 1
```
Caused by omitting `PYTHONDONTWRITEBYTECODE=1` on this one invocation (an earlier `deep_verify.py`
call in the same shell had imported the module without it). Fixed: `find . -name __pycache__ -exec
rm -rf {} +`, then re-ran with the env var set:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2
{"status": "PASS", "output": ".../RELEASE_ALLOWLIST.json", "sha256": "0d64ac49d071cb613a8ccbf75bd8774670c9ea892f2406323e1fb34bea95b847"}
EXIT: 0
$ PYTHONDONTWRITEBYTECODE=1 python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check
{"status": "PASS", "output": ".../RELEASE_ALLOWLIST.json"}
EXIT: 0
```
`record_count`: **1103**. Reconciliation at that point: `git -C absolute-canonical-framework-v1.3.0
ls-files | wc -l` = **1080** + 23 untracked-but-present files (16 under `docs/archive/**` + 7
individually-listed new sidecars/machine files) = **1103**. Matches exactly.

**After `git add docs/archive/`** (see Deviations), re-ran both commands again — **identical sha256**
(`0d64ac49…`), confirming the generator scans the raw filesystem regardless of git-tracked status:
```
$ PYTHONDONTWRITEBYTECODE=1 python3 .../generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2
{"status": "PASS", ..., "sha256": "0d64ac49d071cb613a8ccbf75bd8774670c9ea892f2406323e1fb34bea95b847"}
EXIT: 0
$ PYTHONDONTWRITEBYTECODE=1 python3 .../generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check
{"status": "PASS", ...}
EXIT: 0
```
Final `record_count`: **1103** (unchanged). Final reconciliation: `git ls-files` = **1096** + 7
untracked-but-present files (`GUIDE-170-repository-release.{html,json,_spec.json}`,
`graphs/rendered/release-pipeline.svg`, `graphs/source/release-pipeline.mmd`,
`machine/limitations-register.json`, `machine/release-model.json`) = **1103**. Matches exactly, and
the raw-filesystem file count (`find absolute-canonical-framework-v1.3.0 -type f -not -path
"*/__pycache__/*" | wc -l` → 1103) confirms the generator's own enumeration independently.

---

## Step 20 — deep_verify (after allowlist regeneration)

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py
  FAIL  FRAMEWORK_IDENTITY                 checks=0     findings=1
  PASS  FRAMEWORK_STRUCTURE                checks=1018  findings=0
  PASS  FRAMEWORK_REPRESENTATION           checks=236   findings=0
  PASS  FRAMEWORK_CONTRACTS                checks=418   findings=0
  PASS  FRAMEWORK_SEMANTICS                checks=14    findings=0
  PASS  FRAMEWORK_SECURITY                 checks=1104  findings=0
  PASS  FRAMEWORK_GOVERNANCE               checks=36    findings=0
  PASS  FRAMEWORK_RUNTIME                  checks=43    findings=0
  FAIL  FRAMEWORK_DETERMINISTIC_VALIDATOR  checks=7     findings=74
  FAIL  SIMULATION                         checks=20    findings=4
FAIL  sections=7/10  checks=2896  findings=79
EXIT: 1
```

`FRAMEWORK_GOVERNANCE` moved FAIL→PASS exactly as predicted (the allowlist now reflects every file
on disk, including the archive). Re-ran again after `git add docs/archive/` and the second allowlist
regeneration — identical section pattern, `FRAMEWORK_GOVERNANCE` stays PASS (confirmed: staging
files does not change what the allowlist generator counts, since it scans the filesystem, not git
index state). `FRAMEWORK_IDENTITY` and `SIMULATION` remain red, exactly as expected until the
orchestrator's metadata step. `FRAMEWORK_DETERMINISTIC_VALIDATOR` remains red — the archive-link
finding above, unaffected by tracked-vs-untracked status (confirmed: identical finding set and count
before and after `git add`, since `check_links` scans content/location, not git state).

---

## Step 21 — corpus_check

```
$ ENGINE_HOST_ROOT=<payload> python3 -m tools.corpus_check --root <payload> --json
EXIT: 1
```
`{"guards": 11, "passed": 2, "failed": 8, "skipped": 1, "findings": 94}`,
`{"CRITICAL": 0, "HIGH": 90, "MEDIUM": 4, "LOW": 0}`.

**Reported honestly, not fixed** (per WRITER-BRIEF's explicit instruction: "some guards are
engine-portability failures ... do not 'fix' the subject to satisfy an engine-shaped guard"). Every
one of the 94 findings, plus the 3 zero-finding `FAIL`s, was traced to a root cause and none is a
defect in the eight governed documents or in this pass's work:

| guard | status | root cause |
|---|---|---|
| `register` | PASS | — |
| `identity` | PASS | — |
| `crossrefs` | FAIL (1 finding) | `GUIDE-170.md` links to `machine/release-model.json`, which exists on disk but was untracked at first-check time (deliberate staged-commit discipline, matching pass 1's own minimal-staging precedent — same ordering-effect class as `FRAMEWORK_IDENTITY`/`SIMULATION`). |
| `symbols` | FAIL (43 findings) | 23 of 43 are inside engine-generated `blueprint/{COMPLETENESS,SURFACES,SYSTEM}.md`/`.json` boilerplate that names the *engine's own* generic examples (`docs/CHARTER.md`, `tools.blueprint`, `engine.config.json`) regardless of subject — engine self-referential template text, not subject content. Of the 20 non-blueprint hits: several are in pre-existing subject documents this pass never touched (`docs/design/doc-system/{CLASSIFICATION,DOC_MANIFEST,TAXONOMY}.md`, `09_tests_evals/interface_fixtures/README.md`, `governance/coverage_closure_v3/.../EXECUTABLE_SURFACE_TRACEABILITY_MATRIX.md` — confirmed via `git log -1` on each: last touched at `80562b1`, the repo re-root commit, before this documentation pipeline began); the rest are legitimate cross-boundary citations in GUIDE-170/REF-150/SYS-110 to files this guard cannot see because they live outside the scanned payload root by design — `RELEASE_STAMP.json` (repository root, exactly the class GUIDE-170 exists to document), `.docgen_cache.json`/`engine.config.json` (engine-side, cited in the "what never enters git" table), `tools.health`/`tools.corpus_check`/`tools.blueprint`/`INTERPRETATION.md` (vendored `engine/` modules and docs, confirmed to exist at `engine/INTERPRETATION.md` etc. — the guard is scoped to the payload only). |
| `test-refs` | FAIL (2 findings) | Guard heuristic collision: `` `test_manifest` `` is one of nine **pin-class identifiers** `release_pins()` derives (matching the real artifact `09_tests_evals/TEST_MANIFEST.json`), cited in backticks in GUIDE-170 and REF-130's pin tables. The guard's regex (`` `(test_[a-z0-9_]+)(\.py)?` ``) treats any backticked `test_`-prefixed token as a Python test-function citation. Not a defect — the pin-class name is correct and matches the derived model; renaming it to dodge the regex would break consistency with `release_pins()`'s own output. |
| `counts` | FAIL (0 findings, `checked=2 floor=4`) | Docstring-confirmed: calibrated against this engine's *own* corpus (`BUILD_PLAN.md`'s hand-maintained line counts). The subject payload does not carry that document shape. |
| `cross-doc` | FAIL (0 findings, `checked=4 floor=40`) | Same class: checks register-key citations (`OG-47`, `L-15`, `R2`) and `SCHEDULED (Phase N)` rows specific to the engine's own `OPEN_GATES.md`/doctrine files, absent from the subject by design. |
| `present-tense` | FAIL (19 findings) | 6 of 19 are blueprint boilerplate (engine self-reference, as above); 13 are pre-existing findings in `docs/RUNTIME_GUIDE.md`, `docs/design/doc-system/{CLASSIFICATION,DOC_MANIFEST,RULEBOOK}.md` — all confirmed untouched by this pass (last commit `80562b1`), predate the documentation pipeline entirely. |
| `stamps` | FAIL (0 findings, `checked=0 floor=1`) | Floor requires at least one stamped document to exist anywhere in the corpus. **None of the eight governed documents is stamped** — by design: WRITER-BRIEF §7 explicitly reserves stamping for the orchestrator, after Opus verification. Same ordering-effect class as `FRAMEWORK_IDENTITY`/`SIMULATION`/`stamps`-lifecycle-column, not a defect. |
| `built-claims` | FAIL (29 findings) | 11 of 29 are blueprint boilerplate; the rest are GUIDE-170 (and `system.spec.json`, `machine/evaluation-baseline.json`, pre-existing `RULEBOOK.md`) documenting real, verified-this-session ENGINE commands (`python3 -m tools.docgen.cli`, `python3 -m tools.blueprint`, `python3 -m tools.project_index.cli`, `node engine/tools/graphify/build.mjs`, `node engine/tools/mermaid-engine/render.mjs`) that resolve only when `PYTHONPATH` includes `engine/` — this guard resolves module names against the scanned payload root alone, with no knowledge of the `PYTHONPATH`-based instrument/subject boundary this whole doc set is built around. The `node` commands are additionally flagged for a guard limitation the guard's own evidence text names outright: `"this guard read python3 -m, python3 <script>.py and npm run and was blind to node ... (OG-143)"`. Every one of GUIDE-170's flagged commands was executed this session with `EXIT: 0` (see steps 12–19 above). |
| `rendered-output` | SKIP | render engines absent in this environment (documented, non-blocking per the guard's own evidence text). |

`.docgen/corpus_check/runs.jsonl` deleted from inside the payload after each run (twice — once before,
once after `git add docs/archive/`), per the WRITER-BRIEF run-log-hygiene addendum.

---

## Deviations from the outline, and why

1. **`git add absolute-canonical-framework-v1.3.0/docs/archive/` (all 16 files)** — not literally
   named as a required action in outline step 15, but required to reach §F's own explicit prediction
   ("the lifecycle table moves from seven rows at 3/6 to eight rows at 5/6 — tag, wire, date,
   version, changelog complete; stamp outstanding"). Root cause traced in
   `engine/tools/blueprint/completeness.py`'s `document_lifecycle()`: the `version` step counts a
   generation only when its snapshot file is **tracked** (`if tracked_paths(root, snap_rel)`), with
   the function's own comment stating the rationale explicitly — "an untracked file is present for
   its author and absent for everybody else," matching how `tracked_files()` treats the rest of this
   pipeline. Measured before staging: `version` reported `—` for all eight documents (4/6, missing
   both `version` and `stamp`) despite `archive.versions_on_disk()` correctly finding the `v1/`
   directory on disk (confirmed by calling it directly in Python) — the archive cut itself was
   correct; only its *visibility to a second reader* was incomplete. After `git add`, `version`
   reports ✅ for all eight (5/6, missing only `stamp`), matching §F exactly.
   `.git/index.lock` was refused by the sandbox on the first attempt (`Operation not permitted`);
   retried with the sandbox override per the hard rules — the only git operation in this pass to use
   it, no other git-state-changing command was affected. The full regeneration sequence (steps
   5/10–14) was then re-run twice more (Runs 4–5) to reach a fresh, confirmed fixed point against the
   new 1096-tracked-file count, and the allowlist (step 19) and both deep_verify passes (steps 18/20)
   were re-run against the final staged state — every number quoted above in steps 12–20 is from
   **after** this staging, i.e. the true final state.
2. **`FRAMEWORK_DETERMINISTIC_VALIDATOR` does not reach PASS** — Acceptance criterion 6 names it as a
   required-PASS section. It cannot be brought to PASS from within this pass's write scope: the root
   cause is `04_enforcement/validators/absolute_validate.py`'s `check_links()`, which is subject code
   but not among the paths this pass may write. See the dedicated finding under Step 18 and
   `spawn_task` `task_c1df0020`. This is reported, not hidden, per §H.8's own rule that a finding is
   never quietly repaired-by-redescription.
3. **The second regeneration pass needed three runs, not two, the first time through** — see Step 16.
   The extra run was needed because of my own execution-order artifact (manual out-of-order rebuild
   immediately after archive cut, before the reusable regeneration script existed), not because the
   tooling is non-deterministic. Recorded rather than silently smoothed over, per WRITER-BRIEF §8's
   instruction to find and fix non-determinism at the source and repeat until stable — the "source"
   here was my own command sequencing, and the fix was running the canonical order.
4. One CHANGELOG.md deviation carried over from pass 1 remains true of this pass too: no edit was
   made to `CHANGELOG.md` outside the nine lines appended under the existing 1.3.0
   `### Documentation` heading.

## What I could not do

- **Could not bring `FRAMEWORK_DETERMINISTIC_VALIDATOR` to PASS** (Acceptance criterion 6). Root
  cause identified, reproduced, and fully explained (Step 18); fix is a small, well-scoped change to
  `04_enforcement/validators/absolute_validate.py`, outside this pass's permitted write paths.
  Flagged via `spawn_task` (`task_c1df0020`) with root cause, evidence, and three candidate fixes.
- **Could not make `python3 -m tools.blueprint completeness`'s ratchet memory available.** Root cause
  identified and reproduced directly (Step 12) — a git blob-path-resolution asymmetry
  (`git show <rev>:<path>` resolves top-level-relative; `ls-tree`/`log -- <path>` resolve
  cwd-relative) triggered by the 1.3.0 repository-layout change (payload has no `.git` of its own).
  This is `engine/tools/blueprint/completeness.py` — instrument code, out of scope to edit. `verify`
  still enforces spec-vs-tree agreement and passes; only cross-run loosening detection is affected,
  and no `depthFloor` was touched this pass regardless.
- Everything else assigned to this pass (steps 12–21, all of §I) was completed.

## Files added, changed, or removed in this pass

**Added, git-added (17):** `docs/archive/GUIDE-100/{HISTORY.md,v1/GUIDE-100-project-guide.md}`,
`docs/archive/GUIDE-140/{HISTORY.md,v1/GUIDE-140-operations-verification.md}`,
`docs/archive/GUIDE-170/{HISTORY.md,v1/GUIDE-170-repository-release.md}`,
`docs/archive/REF-130/{HISTORY.md,v1/REF-130-extension-points.md}`,
`docs/archive/REF-150/{HISTORY.md,v1/REF-150-evidence-limitations.md}`,
`docs/archive/REF-160/{HISTORY.md,v1/REF-160-agent-blueprint-guide.md}`,
`docs/archive/SYS-110/{HISTORY.md,v1/SYS-110-architecture.md}`,
`docs/archive/SYS-120/{HISTORY.md,v1/SYS-120-runtime-enforcement.md}` (16 files, `git add`-ed this
pass) plus `docs/ultimate-engine/GUIDE-170-repository-release.md` (already staged by pass 1).

**Added, untracked on disk (7, present for `RELEASE_ALLOWLIST.json`'s enumeration, deliberately not
staged — matching pass 1's precedent of staging only what a mechanical gate requires):**
`docs/ultimate-engine/GUIDE-170-repository-release.html`,
`docs/ultimate-engine/GUIDE-170-repository-release.json`,
`docs/ultimate-engine/GUIDE-170-repository-release_spec.json`,
`docs/ultimate-engine/graphs/rendered/release-pipeline.svg`,
`docs/ultimate-engine/graphs/source/release-pipeline.mmd`,
`docs/ultimate-engine/machine/limitations-register.json`,
`docs/ultimate-engine/machine/release-model.json` — all six of these already existed from pass 1
except `release-pipeline.svg` (rendered this pass, step 13).

**Changed (this pass, on top of pass 1's 37):** `CHANGELOG.md` (nine lines under `### Documentation`),
`PROJECT_INDEX.json`/`.html` (16 artifacts registered/re-registered), `RELEASE_ALLOWLIST.json`
(regenerated twice), `blueprint/{COMPLETENESS,SURFACES,SYSTEM}.md`, `blueprint/SYSTEM.json`,
`blueprint/system.d2` (blueprint build outputs — `system.layout.{json,svg}` and `system.mmd` also
regenerated but byte-identical to pass 1's, per the fixed-point checks), all eight documents'
`.html`/`.json` builds and `_spec.json` sidecars (re-built after `archive cut` bumped their headers
to `version: 1`), `docs/ultimate-engine/graphs/structure/{graph.json,graph-data.js}` (graphify
rebuild), `docs/ultimate-engine/DOCS_INDEX.html`, `docs/design/doc-system/CONTENT_INDEX.json`.

**Removed:** nothing tracked. `absolute-canonical-framework-v1.3.0/.docgen/` (corpus_check's own
run-log directory) was created and deleted twice, per the WRITER-BRIEF hygiene addendum. A stray,
harness-created empty `docs/ultimate-engine/.claude/.cc-writes/` was found and removed (Step 17).

## Final `git status --short absolute-canonical-framework-v1.3.0`

```
 M absolute-canonical-framework-v1.3.0/CHANGELOG.md
 M absolute-canonical-framework-v1.3.0/PROJECT_INDEX.html
 M absolute-canonical-framework-v1.3.0/PROJECT_INDEX.json
 M absolute-canonical-framework-v1.3.0/RELEASE_ALLOWLIST.json
 M absolute-canonical-framework-v1.3.0/blueprint/COMPLETENESS.md
 M absolute-canonical-framework-v1.3.0/blueprint/SURFACES.md
 M absolute-canonical-framework-v1.3.0/blueprint/SYSTEM.json
 M absolute-canonical-framework-v1.3.0/blueprint/SYSTEM.md
 M absolute-canonical-framework-v1.3.0/blueprint/system.d2
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-100/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-100/v1/GUIDE-100-project-guide.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-140/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-140/v1/GUIDE-140-operations-verification.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-170/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-170/v1/GUIDE-170-repository-release.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-130/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-130/v1/REF-130-extension-points.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-150/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-150/v1/REF-150-evidence-limitations.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-160/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-160/v1/REF-160-agent-blueprint-guide.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-110/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-110/v1/SYS-110-architecture.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-120/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-120/v1/SYS-120-runtime-enforcement.md
 M absolute-canonical-framework-v1.3.0/docs/design/doc-system/CONTENT_INDEX.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/DOCS_INDEX.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification_spec.json
AM absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/README.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REGENERATE.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/structure/graph-data.js
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/structure/graph.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/document-index.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/domain-model.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/extension-points.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/inventory.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/verification-model.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py
 M absolute-canonical-framework-v1.3.0/system.spec.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.html
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release_spec.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/rendered/release-pipeline.svg
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/source/release-pipeline.mmd
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/limitations-register.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/release-model.json
```

`find absolute-canonical-framework-v1.3.0 -name __pycache__` → empty. `git status --short
--ignored=matching absolute-canonical-framework-v1.3.0` → only `absolute-canonical-framework-v1.3.0/.claude/`
(confirmed empty at every depth).

## Handoff to the orchestrator

- Remaining before sealing: metadata regeneration (`prepare_release_metadata.py` ×2), the
  orchestrator's stamp pass (all eight documents currently `verified_state: unverified`,
  `status: review`, lifecycle 5/6 — only `stamp` outstanding), sealed zip build, clean-room
  verification, reproduction, `RELEASE_STAMP.json`, git tag, GitHub release — none of this is in
  writer scope (WRITER-BRIEF §1).
- **One real, unresolved defect for the orchestrator or a follow-up session to pick up before
  sealing:** `FRAMEWORK_DETERMINISTIC_VALIDATOR` fails deep_verify (73 broken-link findings, all
  under `docs/archive/**`) because `04_enforcement/validators/absolute_validate.py`'s `check_links()`
  does not account for archived-snapshot documents living in a different directory than their links
  assume. Flagged as `spawn_task` `task_c1df0020`. This is a **pre-existing subject defect that this
  pass's lifecycle work (archive cut) was the first to expose**, not something introduced by writing
  wrong content.
- `python3 -m tools.blueprint completeness`'s ratchet memory is `UNAVAILABLE` in this environment
  (git blob-path-resolution asymmetry under the 1.3.0 repository layout, `engine/tools/blueprint/`
  instrument code, not fixed here). `verify` itself is unaffected and passes.
- Nothing else the outline assigned to this pass was left undone.

---

# Pass 3 (revision), 2026-09-07 — the nine required fixes from `VERIFICATION-2026-09-07.md`

Scope: apply exactly the nine fixes the Opus verifier's `Needs Minor Revision` verdict required
(§"Required fixes, in priority order"), run the full rework loop those fixes require (§"The rework
loop these fixes require"), and hand back a tree ready for a focused re-verification. No stamping —
`verified_state: unverified` and `status: review` are unchanged on all eight documents.

Environment for every command (never varied):

```sh
export PYTHONDONTWRITEBYTECODE=1
export ENGINE_HOST_ROOT="$PWD/absolute-canonical-framework-v1.3.0"
export ENGINE_AUTHORED_DOCS_ROOT="docs/ultimate-engine"
export PYTHONPATH="$PWD/engine"
```

Run from the repository root unless a step says "from inside the payload."

## The nine fixes, file:line before → after

### 1. (W-3, W-4) GUIDE-170 §"The release procedure, in order"

`docs/ultimate-engine/GUIDE-170-repository-release.md:143-222`. Before: nine `### 0.`–`### 8.`
headings with `### 2. Bind the release metadata (twice)` preceding
`### 3. Regenerate the release allowlist` — the opposite order from §"The order that avoids a red
tree" and from the (already-edited) normative `RELEASE_PROCEDURE.md`, and the intro sentence
claimed "Nine steps, mirroring … so this summary cannot drift" while it did not mirror. After: ten
`### 0.`–`### 9.` headings, titles matching `RELEASE_PROCEDURE.md`'s `## 0.`–`## 9.` headings
exactly — `### 2. Regenerate the release allowlist` now precedes `### 3. Bind the release
metadata`; `### 9. Do not rename it` is a new heading carrying the certification-naming prose that
used to sit inside `### 8. Record`'s paragraph; the intro now reads "Ten steps, mirroring …
headings (`0`–`9`) so this summary cannot drift…". Also fixed a downstream reference at
`GUIDE-170:246` ("which is what step 3 above consumes" → "step 2", since the allowlist step's
ordinal moved) — found only after re-grepping `step [0-9]` across all eight documents post-edit.
`machine/release-model.json`'s `procedure` array (derived by `release_procedure_steps()`, already
generic — no script change needed) now carries the ten entries after re-running the derive script.

### 2. (W-1) REF-150:129

Before: "It is fixed and now read on every run: `ABS.RELEASE.1.3.0`, **1,079 records**, verified
against the baseline by release id rather than by chain position." After: "…its record count read
from `RELEASE_ALLOWLIST.json`'s own `record_count` field — mirrored in
[`machine/release-model.json`](machine/release-model.json)'s `allowlist` rather than typed here,
because the count moves every time a file is added to or removed from the payload — verified
against the baseline…". Extended `scripts/derive_documentation_model.py`: read
`RELEASE_ALLOWLIST.json` in `main()`, added it to `release_model["source"]`, and added a
`release_model["allowlist"]` object (`release_id`, `candidate_id`, `policy`, `record_count`) so the
figure is derived, not typed. Current value: `1103` (verified live: `RELEASE_ALLOWLIST.json`'s
`record_count` after the final regeneration in this pass is `1103`, unchanged from the start of the
pass — no files were added or removed by the content edits).

### 3. (W-4′) REF-160:75-76

Before: "`verified` is **0** across all 28 nodes… `verified` requires rung 4 or deeper, and 0 of 28
nodes are at rung 4 or deeper…". After: "…as recorded in
[`blueprint/COMPLETENESS.md`](../../blueprint/COMPLETENESS.md), `verified` is **0** across every
tracked node… and that same report states none of the tracked nodes are at rung 4 or deeper…" — no
typed number; `blueprint verify`/`completeness` (re-run in this pass) confirm `30 module(s)` / `30
node(s)`, `0 of 30` at rung 4+.

### 4. (W-2) REF-150:225-227 ("The instrument's own state")

Before: "The Ultimate Engine's own health check on itself, at version 1.0.5, reports **28 pass / 5
fail / 5 skip** (`CONS-11`, `BUILD-01`, `BUILD-03`, `SUITE-03`, `SUITE-05`)." — unqualified, no
command, no root. After: states the exact command and root — `cd engine && PYTHONDONTWRITEBYTECODE=1
ENGINE_HOST_ROOT="$PWD" python3 -m tools.health --json --no-run-log` → **29 pass / 4 fail / 5 skip**
(`STRUCT-03`, `STRUCT-04`, `STRUCT-06`, `SUITE-05`); names the standalone-checkout result
(`FreeXStudio-Platform/ultimate-engine@185725a`, its own git root — `python3 -m unittest discover -s
tools/tests -t .` → OK, 587 tests); and states that a run without `ENGINE_HOST_ROOT` pinned to
`engine/`, or one that treats the payload as the engine's host root, produces yet another set of
numbers for the identical root-resolution reason. I independently re-ran the pinned-root command
live in this session (`$TMPDIR/health_vendored.json`) and measured **30 pass / 4 fail / 4 skip**
(same 38 total checks, same failing codes `STRUCT-03`/`STRUCT-04`/`STRUCT-06`/`SUITE-05`) — a ±1
pass/skip split against FACTS Addendum 3's figure with an identical fail set and identical total,
which is exactly the invocation-dependence the fix documents. Per the task's explicit instruction
("state the measurement … exactly as FACTS Addendum 3 records it"), the document quotes Addendum
3's `29/4/5`, not my own re-run's `30/4/4`; both are recorded here for the audit trail. The
standalone-checkout figure (587 tests, OK) was not independently re-run — no standalone checkout of
`FreeXStudio-Platform/ultimate-engine@185725a` exists in this sandbox — and is quoted from FACTS Addendum 3
as instructed.

### 5. (W-7) REF-150:97 and :155 ("carried forward under 'What remains a limitation'")

Before: the "What remains a limitation" section (`REF-150:158-227` before this pass) held nine H3s,
none of them the test-manifest or regeneration-procedure residuals the two forward references
pointed at. After: two new H3s added immediately before "### The instrument's own state" —
"### The test manifest is a description, not a control" and "### The regeneration procedure is not
self-verifying" — each citing the matching `machine/limitations-register.json` row
(`F-06-test-manifest-description-only`, `stale-regeneration-procedure`) and its
`REMAINS_A_LIMITATION` disposition. The section now holds eleven H3s (confirmed by
`awk '/^## What remains a limitation/,/^## Dependencies/'` + `grep -c '^### '` → `11`). This also
repairs `GUIDE-170:107`'s route to REF-150 (the `test_manifest` pin row's "not mechanically
checked — see REF-150" link), which now lands on a section that actually carries the residual.

### 6. (W-5) SYS-120:199

Before: "…| The **nine** named `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE` check codes above. |" —
the document's own enumeration (four structure codes at L111-117, six governance checks / seven
governance codes at L134-139) sums to ten checks or eleven codes, matching neither "nine" nor the
derived model. After: "…| The `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE` check codes named
above. |" — no count asserted; the codes are the ones already named in the same document, so
nothing is typed that could drift from them. (`verification-model.json`'s full
`section_structure`/`section_governance` `check_codes` lists — 16 each — cover every code either
function can emit, not only the cross-representation-pin subset this row describes, so citing that
list's length would have overcounted; dropping the bare number was the correct fix rather than
substituting a different wrong one.)

### 7. (W-8) REF-160:86

Before: "…whatever its owning document claims. [GUIDE-170](GUIDE-170-repository-release.md) states
this consequence in full for the containers this release touches." — `grep -in
'rung|container|completeness' GUIDE-170-repository-release.md` finds no such statement. After:
"…whatever its owning document claims. [`blueprint/COMPLETENESS.md`](../../blueprint/COMPLETENESS.md)
states this consequence in full, per container, for every container this release touches." —
verified `COMPLETENESS.md:24` does list `documentation-derivation` among the seven containers with
no rung-4 module, so they "can never report themselves verified whatever their documents say."

### 8. (W-6) GUIDE-140:133-136

Before: "**Eight steps**, in the canonical order, derived from the normative procedure document's
own headings so this summary cannot drift from it: **Environment · Freeze the payload · Bind the
release metadata (twice) · Verify — all of it, in a fresh process · Build · Verify the artifact,
not the working tree · Reproduce · Record.**" — nine headings exist and the list silently dropped
the ninth. After: "The canonical order — recorded in
[`machine/release-model.json`](machine/release-model.json)'s `procedure` array, which is derived
from `RELEASE_PROCEDURE.md`'s own numbered headings rather than typed here — is: **Environment ·
Freeze the payload · Regenerate the release allowlist · Bind the release metadata (twice) · Verify
— all of it, in a fresh process · Build · Verify the artifact, not the working tree · Reproduce ·
Record · Do not rename it.**" — all ten current steps named, no bare count asserted, and the
citation makes the claim genuinely re-derivable rather than typed.

### 9. (U-1) REF-150:82 vs `machine/limitations-register.json`

Before: "New controls: three `FRAMEWORK_STRUCTURE` check codes (`MODULE_RELEASE_PIN_DRIFT`,
`MODULE_NARRATIVE_MISSING`, `MODULE_NARRATIVE_RELEASE_DRIFT`) plus two mutation controls…" — the
register's `F-05-narrative-release-pins` row names **four** codes, the fourth being
`FRAMEWORK_REGISTRY_RELEASE_DRIFT`. Per the fix's instruction, the register is the sourced side;
`runtime/verify.py` `section_structure` does define all four codes (`MODULE_RELEASE_PIN_DRIFT`,
`MODULE_NARRATIVE_MISSING`, `MODULE_NARRATIVE_RELEASE_DRIFT`, `FRAMEWORK_REGISTRY_RELEASE_DRIFT`),
so the register was right and the prose undercounted. After: "New controls, as recorded in
[`machine/limitations-register.json`](machine/limitations-register.json)'s
`F-05-narrative-release-pins` row: four `FRAMEWORK_STRUCTURE` check codes
(`MODULE_RELEASE_PIN_DRIFT`, `MODULE_NARRATIVE_MISSING`, `MODULE_NARRATIVE_RELEASE_DRIFT`, and
`FRAMEWORK_REGISTRY_RELEASE_DRIFT` — the fourth pins the framework registry rather than the
narrative, but it closes the same class of drift) plus two mutation controls…".

## The rework loop, every command and its exit code

Applied twice in full (a genuine mid-loop correction — see "One in-loop correction" below — made a
first "second run" comparison invalid, so the loop was executed a third time to get a clean
before/after pair; all exit codes below are from the final, clean execution).

| step | command | exit |
|---|---|---|
| derive | `python3 absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py` | 0 — `derived documentation model: 1096 tracked files, 33 canonical modules, 284 authority edges, 8 figure sidecars` |
| strict build ×8 | `python3 -m tools.docgen.cli --strict build <8 paths> --formats html,json` | 0 — `built 8 doc(s) in 3.454s — 0 reused from cache, 8 rebuilt` |
| check ×8 | `python3 -m tools.docgen.cli check <doc>.md` (×8) | 0 ×8, each `docgen check: PASSED — header + taxonomy-prefix + manifest-drift + rulebook hash-gate` |
| DOCS_INDEX | `python3 -m tools.docgen.cli index docs/ultimate-engine -o docs/ultimate-engine/DOCS_INDEX.html` (from inside the payload) | 0 — `8 public document(s) indexed` |
| CONTENT_INDEX | `python3 -m tools.docgen.cli content-index --docs-root docs/ultimate-engine -o docs/design/doc-system/CONTENT_INDEX.json` (from inside the payload) | 0 — `8 public doc(s) listed, 2 non-public excluded` |
| archive re-cut ×5 | `rm -rf docs/archive/<id>/` then `archive cut <doc> --date 2026-09-07` for GUIDE-140, GUIDE-170, REF-150, REF-160, SYS-120 | 0 ×5, each reports `v1` with a fresh sha256, `commit d647a61` (HEAD unchanged — nothing was committed) |
| `git add docs/archive` | (sandbox override required — `.git/index.lock` denied under the default sandbox, retried with the override per the task's own instruction) | 0 |
| blueprint build | `python3 -m tools.blueprint build` | 0 |
| blueprint layout | `python3 -m tools.blueprint layout` | 0 — `8 node(s), 609×704, 0 placement finding(s)` |
| blueprint verify | `python3 -m tools.blueprint verify` | 0 — `clean — 7 container(s), 30 module(s), 297 document(s), 6 derived file(s)` |
| blueprint completeness | `python3 -m tools.blueprint completeness` | 0 — `30 node(s) — sketched 7 · documented 23 · verified 0`; lifecycle `40/48`, `missing stamp` the only gap on all eight, matching the verifier's own baseline |
| graphify build | `ENGINE_HOST_ROOT=<payload> node engine/tools/graphify/build.mjs` | 0 — `705 nodes · 704 links` |
| copy graph artifacts | `cp` `graph.json`/`graph-data.js` from `engine/graphify-out/`, `graph-view.html` + `vendor/{force-graph.min.js,3d-force-graph.min.js}` from `engine/tools/graphify/` into `docs/ultimate-engine/graphs/structure/` | — (see "One in-loop correction": the first attempt over-copied `vendor/PROVENANCE.md`, which is not a `.js` file and not part of what GUIDE-170's own regeneration section names to copy; removed, and `content-index` re-run confirmed 2, not 3, non-public-excluded) |
| mermaid renders ×4 | `node engine/tools/mermaid-engine/render.mjs <source>.mmd -o <rendered>.svg` for `document-rail`, `domain-dependencies`, `project-rail`, `release-pipeline` | 0 ×4 |
| project_index dashboard | `python3 -m tools.project_index.cli dashboard` | 0 |
| project_index verify | `python3 -m tools.project_index.cli verify --scan docs/ultimate-engine` | 0 — `16 artifact(s) registered`, `OK — every registered artifact resolves to a real file, no duplicates.` |
| allowlist regen | `python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2` (from inside the payload) | 0 — `{"status": "PASS", "sha256": "0d64ac49d071cb613a8ccbf75bd8774670c9ea892f2406323e1fb34bea95b847"}`, `record_count: 1103` — identical sha256 across both clean runs, i.e. the regeneration is itself a fixed point given no file-count change |
| allowlist `--check` | same command + `--check` | 0 — `{"status": "PASS"}` |
| deep_verify | `PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py` (from inside the payload) | 1 (expected) — `FAIL sections=8/10 checks=2896 findings=5 severity={'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 0, 'LOW': 0}`; only `FRAMEWORK_IDENTITY` (1 finding, `TREE_INTEGRITY_FAIL`) and `SIMULATION` (4 findings, all `DOC_SCHEMA_VIOLATION`-rooted) are red, matching the verifier's own re-run exactly; `FRAMEWORK_DETERMINISTIC_VALIDATOR checks=7 findings=0` |
| absolute_validate | `python3 04_enforcement/validators/absolute_validate.py .` (from inside the payload) | 0 — `{"status": "PASS", "counts": {"checks": 5, "errors": 0}}` — `modules`, `profiles_adapters`, `examples_semantics`, `security_hygiene`, `links` all PASS |

### One in-loop correction (found and fixed before the idempotence check was trusted)

Copying `vendor/*.js` from `engine/tools/graphify/vendor/` on the first pass through step (d) was
done as a wholesale directory copy, which also copied `vendor/PROVENANCE.md` — a file GUIDE-170's
own regeneration section does **not** name (`vendor/*.js` only) and which was never part of the
payload's tracked `graphs/structure/vendor/` (confirmed via `git ls-tree -r HEAD -- …vendor/`: only
the two `.min.js` files). Its presence flipped `content-index`'s `non_public_excluded` count from 2
to 3 (the new `.md` has no `classification: public` header) — caught by comparing `content-index`
output across two supposedly-identical runs rather than by inspection. Removed the stray file,
re-ran `content-index` (back to `2 non-public excluded`), and re-ran the entire loop a further time
to get a clean idempotence pair. The two vendor `.js` files themselves were verified byte-identical
to the committed copies (`cmp` against `git show HEAD:…`) before and after.

A second issue surfaced the same way: after the GUIDE-170 renumbering (fix 1), a residual
cross-reference at `GUIDE-170:246` ("which is what step 3 above consumes") still pointed at the old
ordinal for the allowlist-regeneration step, which is now step 2. Found by re-grepping
`step [0-9]|Step [0-9]|§[0-9]` across all eight documents after the renumbering edit, before trusting
the loop closed; fixed to "step 2", which required one more full pass through derive → build ×8 →
check ×8 → indexes → archive re-cut (GUIDE-170 only, since it was the only body that changed again)
→ blueprint → graphify → mermaid → project_index → allowlist regen → deep_verify → absolute_validate,
all exit codes as tabulated above (the table reflects this final pass).

## Idempotence — sha256 over four trees, before and after a second clean run of steps (b) and (d)

```
find <tree> -type f | sort | xargs shasum -a 256 | shasum -a 256
```

| tree | before | after | match |
|---|---|---|---|
| `docs/ultimate-engine` | `e1577ab5b4b79130031eeb131ffd424ad0c1f4318b692de99bb32e742ee99ce4` | `e1577ab5b4b79130031eeb131ffd424ad0c1f4318b692de99bb32e742ee99ce4` | **IDENTICAL** |
| `docs/archive` | `601bfc5a4bef50c91ac41aedd8a7bbed23e25840431d1fc5cfade8be2821ba71` | `601bfc5a4bef50c91ac41aedd8a7bbed23e25840431d1fc5cfade8be2821ba71` | **IDENTICAL** |
| `blueprint` | `13199bf1fa07fb6ede66fe95d212e004a18add090762ca08b8d7b87160a9d34c` | `13199bf1fa07fb6ede66fe95d212e004a18add090762ca08b8d7b87160a9d34c` | **IDENTICAL** |
| `PROJECT_INDEX.{json,html}` (sha256 of the two files' sha256 lines) | `00092b87a68352db4040e209415d8f02671c089f5aafe7c0365776adf3007a90` | `00092b87a68352db4040e209415d8f02671c089f5aafe7c0365776adf3007a90` | **IDENTICAL** |

The allowlist regeneration's own sha256 (`0d64ac49d071cb613a8ccbf75bd8774670c9ea892f2406323e1fb34bea95b847`)
was also identical across its two runs in this pass (before and after the final full loop), and
`deep_verify`/`absolute_validate` produced byte-identical section/check counts on both runs quoted
in the table above.

## Hygiene, checked clean after the final loop

- `find absolute-canonical-framework-v1.3.0 -name __pycache__` → empty.
- `.docgen/`, `.health/`, `graphify-out/`, `.docgen_cache.json`, `.blueprint/` at the payload root →
  all absent.
- `git status --short --ignored=matching absolute-canonical-framework-v1.3.0 | grep '^!!'` → empty
  (no ignored files inside the payload).
- `absolute-canonical-framework-v1.3.0/.claude/` (harness-created, contained only an empty
  `.cc-writes` subdirectory) → removed.
- `engine/.health`, `engine/.docgen`, `engine/graphify-out` (created by this pass's own
  `tools.health`/`tools.blueprint`/`graphify` invocations, all gitignored, all outside the payload)
  → removed for tidiness; their absence is not itself evidence of anything since they are outside
  the payload's identity boundary.

## Header fields — unchanged, no stamping

`version: 1` / `revision: 0` on all eight (unchanged by these edits — the archive re-cut writes the
same values back since the five re-cut documents were already at v1/revision 0 from pass 2);
`verified_state: unverified`, `status: review` on all eight; no `artifact-hardened` stamp anywhere
(confirmed by grep — the only `artifact-hardened` string in the tree is GUIDE-100's own description
of the stamp grammar, using placeholder syntax that cannot match `STAMP_RE`).

## `CHANGELOG.md` — one line updated

Only `docs/ultimate-engine/GUIDE-170-repository-release.md`'s changelog entry named a specific,
now-wrong count ("the release procedure in nine steps"); updated to "the release procedure in ten
steps mirroring `RELEASE_PROCEDURE.md`'s own numbered headings 0–9, allowlist regeneration ordered
before the metadata bind". The other four changed documents' changelog entries either describe
their sections generically (REF-150) or name a set of section titles that did not change (GUIDE-140,
REF-160, SYS-120 — only the *content* inside an already-listed section changed, which the fix
criterion ("only if a document's changed-sections list changed") does not require updating for) —
left as-is.

## Final `git status --short absolute-canonical-framework-v1.3.0` (verbatim)

```
 M absolute-canonical-framework-v1.3.0/01_control_plane/manifests_releases/RELEASE_PROCEDURE.md
 M absolute-canonical-framework-v1.3.0/04_enforcement/validators/absolute_validate.py
 M absolute-canonical-framework-v1.3.0/CHANGELOG.md
 M absolute-canonical-framework-v1.3.0/PROJECT_INDEX.html
 M absolute-canonical-framework-v1.3.0/PROJECT_INDEX.json
 M absolute-canonical-framework-v1.3.0/RELEASE_ALLOWLIST.json
 M absolute-canonical-framework-v1.3.0/blueprint/COMPLETENESS.md
 M absolute-canonical-framework-v1.3.0/blueprint/SURFACES.md
 M absolute-canonical-framework-v1.3.0/blueprint/SYSTEM.json
 M absolute-canonical-framework-v1.3.0/blueprint/SYSTEM.md
 M absolute-canonical-framework-v1.3.0/blueprint/system.d2
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-100/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-100/v1/GUIDE-100-project-guide.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-140/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-140/v1/GUIDE-140-operations-verification.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-170/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/GUIDE-170/v1/GUIDE-170-repository-release.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-130/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-130/v1/REF-130-extension-points.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-150/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-150/v1/REF-150-evidence-limitations.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-160/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/REF-160/v1/REF-160-agent-blueprint-guide.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-110/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-110/v1/SYS-110-architecture.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-120/HISTORY.md
A  absolute-canonical-framework-v1.3.0/docs/archive/SYS-120/v1/SYS-120-runtime-enforcement.md
 M absolute-canonical-framework-v1.3.0/docs/design/doc-system/CONTENT_INDEX.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/DOCS_INDEX.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-100-project-guide_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-140-operations-verification_spec.json
AM absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/README.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-130-extension-points_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-160-agent-blueprint-guide_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REGENERATE.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-110-architecture_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.html
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement.md
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/SYS-120-runtime-enforcement_spec.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/structure/graph-data.js
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/structure/graph.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/document-index.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/domain-model.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/extension-points.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/inventory.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/verification-model.json
 M absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py
 M absolute-canonical-framework-v1.3.0/system.spec.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.html
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/GUIDE-170-repository-release_spec.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/rendered/release-pipeline.svg
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/graphs/source/release-pipeline.mmd
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/limitations-register.json
?? absolute-canonical-framework-v1.3.0/docs/ultimate-engine/machine/release-model.json
```

The seven `??` entries (`GUIDE-170`'s built html/json/spec, the `release-pipeline` mermaid
source/render, and the two new `machine/*.json` files) are unchanged from the state pass 2 left
them in — they are new files pass 2 introduced, not files this pass re-cut or created, so per this
pass's hard rule ("`git add` new/re-cut files only") they were left for the orchestrator to stage
alongside the rest of pass 2's own new files, exactly as pass 2 left them.

## What I could not do / did not do

- Did not independently reproduce the standalone-checkout engine-health figure (587 tests, OK) —
  no standalone checkout of `FreeXStudio-Platform/ultimate-engine@185725a` exists in this sandbox; quoted
  from FACTS Addendum 3 per the task's explicit instruction.
- Did not stamp any document, did not touch `RELEASE_PROCEDURE.md` (already edited by the
  orchestrator before this pass), `README.md`, `RELEASE_NOTES.md`, `LIMITATIONS.md`, `engine/`
  source, `MANIFEST*`/`SHA256SUMS`/`.absolute`, or any `system.spec.json` `depthFloor` value.
- Did not commit, reset, or stash anything; the only `git` write actions were `git add
  absolute-canonical-framework-v1.3.0/docs/archive` (twice, both under the sandbox override the
  task pre-authorized for the `.git/index.lock` denial).
- Everything else the task assigned was completed: all nine fixes, the full rework loop (including
  a second clean run proving idempotence), hygiene, the one warranted `CHANGELOG.md` line, and this
  record.
