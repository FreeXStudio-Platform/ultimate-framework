# Verification record — the 1.3.0 documentation set (Opus verifier pass), 2026-09-07

Verifier: Claude Opus 5, acting under `VERIFIER-BRIEF-2026-09-07.md`. I did not write these
documents and I fixed nothing. Every command below was re-run by me in this session; nothing is
quoted from `WRITER-RUN-2026-09-07.md` as evidence.

**Environment used for every command** (never varied):

```sh
export PYTHONDONTWRITEBYTECODE=1
export ENGINE_HOST_ROOT="$PWD/absolute-canonical-framework-v1.3.0"
export ENGINE_AUTHORED_DOCS_ROOT="docs/ultimate-engine"
export PYTHONPATH="$PWD/engine"
```

Run from the repository root unless a row says "from inside the payload". Interpreter
`/opt/homebrew/bin/python3` 3.14.6; Graphviz `dot` 15.1.0 (20260618.0150); Node v26.5.0 — all three
re-measured, all three match what the documents claim.

**Non-modification proof.** Before running anything I took a byte-level copy of the payload
(1,103 files). After every command in this record — including the strict docgen build, the
blueprint build/verify/completeness, the derive script, and the deep verifier — `diff -rq` between
that copy and the live payload reports **no differences**. The payload is byte-identical to the
state I received it in. I created no `__pycache__` anywhere; the two empty engine host-state
directories my `tools.health` runs created (`engine/.docgen`, `engine/.health`, both gitignored,
both outside the payload, both containing zero files) were removed.

---

## Verdict

# `Needs Minor Revision`

The gate suite is green and the set conforms to the outline structurally: all eight documents
strict-build and `check` clean, `blueprint verify` is clean, the ratchet memory now reads *"git
history of the spec"*, `project_index verify` is clean, the deterministic validator is `PASS 5/5`,
the release allowlist `--check` is `PASS`, the deep verifier is `8/10` with only the two
by-construction sections red, hygiene is clean, and no forbidden pattern survives. Every required
section, every figure, every header field, every archive generation and every changelog line is
present and correct.

It is not `Approved` because **eight sampled claims are wrong against the tree** (the brief's rule:
any WRONG claim blocks approval). All eight are localized factual corrections with a known correcting
fact — no gap, no restructuring, no new research. Two of them (`W-3`/`W-4`) are in GUIDE-170's
release procedure, the document the orchestrator is about to act on, and one of those would, if
followed literally, bind release metadata that the next step invalidates. Those two must be fixed
before the stamp regardless of how the rest is triaged.

It is not `Needs Major Revision` because nothing is missing, nothing is unsupported at the level of
argument, and the documents' own machine layer already carries the correct values in every case
where the prose is stale — the corrections are edits to sentences, not to the design.

---

## Check table

Every check the brief requires, with the command as run and the exit code as observed.

| # | Check | Command | Exit | Result |
|---|---|---|---|---|
| 1 | Strict docgen build, all eight | `python3 -m tools.docgen.cli --strict build <8 paths> --formats html,json` | **0** | `built 8 doc(s) in 3.288s — 0 reused from cache, 8 rebuilt`. Output byte-identical to what was on disk → the build is a fixed point. |
| 2 | `docgen check` ×8 | `python3 -m tools.docgen.cli check <doc>.md` (×8) | **0** ×8 | Each: `docgen check: PASSED — header + taxonomy-prefix + manifest-drift + rulebook hash-gate`, preceded by `[hash_gate] info: rulebook hash matches VERSION.json — no undeclared drift`. |
| 3 | Blueprint verify | `python3 -m tools.blueprint verify` | **0** | `blueprint verify: clean — 7 container(s), 30 module(s), 297 document(s), 6 derived file(s)` |
| 4 | Blueprint completeness | `python3 -m tools.blueprint completeness` | **0** | `30 node(s) — sketched 7 · documented 23 · verified 0`; `document lifecycle: 40/48 step(s) complete across 8 governed document(s)`, all eight `missing stamp` only; `ratchet level across 7 container(s)`. `COMPLETENESS.md` L41 reads **`Ratchet memory: git history of the spec (7 container(s) remembered)`** — Addendum 4's fix confirmed, no `UNAVAILABLE`. |
| 5 | Project index verify | `python3 -m tools.project_index.cli verify --scan docs/ultimate-engine` | **0** | `16 artifact(s) registered` · `OK — every registered artifact resolves to a real file, no duplicates.` |
| 6 | Deep verifier (from inside the payload) | `PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py` | **1** | `FAIL sections=8/10 checks=2896 findings=5`. **PASS:** STRUCTURE 1018, REPRESENTATION 236, CONTRACTS 418, SEMANTICS 14, SECURITY 1104, GOVERNANCE 36, RUNTIME 43, **DETERMINISTIC_VALIDATOR 7/0 findings**. **FAIL:** `FRAMEWORK_IDENTITY` (1 — `TREE_INTEGRITY_FAIL`, manifest release identity mismatch) and `SIMULATION` (4 — all four citing `DOC_SCHEMA_VIOLATION at MODULE_MANIFEST.yaml`). Exactly the two sections that are red by construction, and no others. |
| 7 | Deterministic validator | `python3 04_enforcement/validators/absolute_validate.py .` (from inside the payload) | **0** | `"status": "PASS"`, `checks: 5`, `errors: 0` — `modules`, `profiles_adapters`, `examples_semantics`, `security_hygiene`, `links` all PASS. Addendum 4's `check_links` repair confirmed: the 73 archive-snapshot false positives are gone. |
| 8 | Release allowlist | `python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check` (from inside the payload) | **0** | `{"status": "PASS", "output": ".../RELEASE_ALLOWLIST.json"}`. No drift; I did not regenerate it. |
| 9 | Derive script re-run (fixed point) | `python3 absolute-canonical-framework-v1.3.0/docs/ultimate-engine/scripts/derive_documentation_model.py` | **0** | `derived documentation model: 1096 tracked files, 33 canonical modules, 284 authority edges, 8 figure sidecars`; `diff -rq` against the pre-run snapshot → **no differences**. Every derived value on disk is reproducible. |
| 10 | Bytecode hygiene | `find absolute-canonical-framework-v1.3.0 -name __pycache__` | 0 | Empty, before and after every Python invocation in this pass. |
| 11 | Host-state hygiene | `ls absolute-canonical-framework-v1.3.0/{.docgen,.health,graphify-out,.blueprint}` · `find … -name .docgen_cache.json` | — | All absent. |
| 12 | Ignored files inside the payload | `git status --short --ignored=matching absolute-canonical-framework-v1.3.0 \| grep '^!!'` | 0 | Only `absolute-canonical-framework-v1.3.0/.claude/`, confirmed empty at every depth (`find … -type f` → nothing). |
| 13 | Working-tree scope | `git status --short absolute-canonical-framework-v1.3.0` | 0 | **75 paths** = exactly the 74 the run record lists, plus `04_enforcement/validators/absolute_validate.py` (Addendum 4). Nothing else is dirty or untracked. |
| 14 | Forbidden: absolute paths | `grep -n "/Users/" <8 .md> <8 .html>` | 1 | **No hits.** Also no hits in any `*_spec.json`. |
| 15 | Forbidden: field-trial layout | `grep -n "ChatGPT-Framework-Test" …` | 1 | **No hits.** |
| 16 | Forbidden: RC2 suite id as current | `grep -n "ABS.TEST.SUITE.FRAMEWORK.RC2" …` | 0 | 1 hit, `REF-150.md:89` + its HTML — explicitly past tense, immediately followed by the current suite id. Compliant. |
| 17 | Forbidden: `subject/` layout | `grep -n "subject/" …` | 0 | 2 hits, both `REF-150.md` (L42, L152) + HTML — both explicitly the pre-1.3.0 layout ("That layout is not this repository's layout"; "that this repository does not have"). Compliant. |
| 18 | Forbidden: certification claim | `grep -nio "certified…\|certification complete\|audited\|externally validated\|is compliant" <8 .md>` | 0 | 5 hits, all negations or prohibitions (`Never relabel a candidate … CERTIFIED`; `does not make the release certified`; `It does not mean certified, audited, or externally reviewed`). No assertive claim. |
| 19 | Forbidden: stale version leakage | `grep -n "1\.1\.0\|1\.2\.0" <8 .md>` | 0 | 14 hits across 6 documents, **all** historical or baseline-chain enumeration ("Since 1.2.0…", "Through 1.2.0…", "At 1.1.0…", "RC1 → RC2 → 1.0.0 → 1.1.0 → 1.2.0"). Compliant. |
| 20 | Headers, all eight | `grep -h "^<field>" *.md \| sort \| uniq -c` | — | 8× each of: `classification: public`, `export_allowed: true`, `owner: framework-documentation`, `status: review`, `last_reviewed: 2026-09-07`, `version: 1`, `revision: 0`, `produced_by: Ultimate Engine 1.0.5`, `verified_state: unverified`. `id`/`title`/`surface`/`audience` correct per document. **No `artifact-hardened` stamp on any document** (the two grep hits are GUIDE-100 describing the grammar with `<sha>` placeholders, which cannot match `STAMP_RE`). |
| 21 | Archive generations | `ls docs/archive/*/v1/` · `shasum -a 256` archive vs live | — | All eight present with `HISTORY.md` + `v1/<file>.md`; **all eight byte-identical to their live bodies**. `GUIDE-170` HISTORY row: v1, 2026-09-07, commit `d647a61`, sha256 `cbf378006ff2…`. |
| 22 | Changelog lines | `awk` over the payload `CHANGELOG.md` `### Documentation` block | — | **Eight** per-document lines, one each for GUIDE-100, SYS-110, SYS-120, REF-130, GUIDE-140, REF-150, REF-160, GUIDE-170, each carrying date, version, file and sections changed. The Addendum-4 validator repair is also recorded under `Fixed` (L50–55). |
| 23 | Figures vs the plan | `grep -o '<!-- figure:…' *.md` vs `*_spec.json` | — | **24 figure instances, 24 sidecar entries, exact match with outline §C** (19 ids; `dependency-centrality` appears in both SYS-110 and REF-130). Per document: GUIDE-100 3, SYS-110 4, SYS-120 4, REF-130 2, GUIDE-140 4, REF-150 3, REF-160 2, GUIDE-170 2. |
| 24 | Sidecar provenance | python audit of all `*_spec.json` `data_sources` | — | 24 entries, **all** `retrieved: 2026-09-07` (D-1 applied); **zero** refs that are absolute, parent-relative, or outside the payload — the `evaluation-evidence/…` leak D-13 targeted is gone. |
| 25 | Document dependency graph | `machine/document-index.json` `depends_on` vs outline §G.1 | — | **Exact match on all 8 documents and all 33 edges.** REF-160 is a pure consumer, as specified. |
| 26 | Derived-not-typed (script properties) | read `scripts/derive_documentation_model.py` | — | `RETRIEVED = "2026-09-07"` as a named constant with the no-`date.today()` rationale (L29–32); `sys.dont_write_bytecode = True` at L20; `tracked_files()` still uses `git -C ROOT ls-files` with an explicit "do not fix this to rglob" comment (L124–130); `question_coverage()` derives its cells from artifact presence (L388–413), no `[[1,…]]` literal remains for it. |

**26 checks run, 26 passed.** No check was skipped and none could not be run.

---

## Sampled claims

70 concrete claims re-derived from the tree. **60 CONFIRMED · 8 WRONG · 2 UNVERIFIABLE.**
`P/` = payload-relative; `R/` = repository-root-relative.

| # | Document:line | Claim | Command used | Result |
|---|---|---|---|---|
| 1 | GUIDE-100:32 | Release `ABS.RELEASE.1.3.0`, candidate `ABS.CANDIDATE.1.3.0` | `cat P/VERSION`; `grep -n '^RELEASE_ID\|^CANDIDATE_ID' P/01_control_plane/…/release_integrity.py` | CONFIRMED |
| 2 | GUIDE-100:33 | Status `RELEASE_INTERNALLY_VERIFIED_INDEPENDENT_CERTIFICATION_PENDING` | `python3 -c "json…FRAMEWORK.json['status']"` | CONFIRMED |
| 3 | GUIDE-100:36 | `C20` is `EXTERNAL_HANDOFF_REQUIRED` | `grep -n EXTERNAL_HANDOFF_REQUIRED P/01_control_plane/manifests_releases/RELEASE_PROCEDURE.md` → L50 | CONFIRMED |
| 4 | GUIDE-100:37 | `ABS.CFG.RELEASE.SELF_CERTIFICATION` fixed to `false` | `grep -rn ABS.CFG.RELEASE.SELF_CERTIFICATION P/` → `runtime/verify.py:643`, `runtime/engine.py:1178`, `tests/test_coverage_closure_v3_controls.py:23` | CONFIRMED |
| 5 | GUIDE-100:92–96 | Six files, written only by `tools/prepare_release_metadata.py` | `sed -n '1,14p' P/tools/prepare_release_metadata.py`; `CANDIDATE_HASH_EXCLUSIONS` L95–103 | CONFIRMED |
| 6 | GUIDE-100:98 | `FRAMEWORK_REGISTRY_RELEASE_DRIFT` / `ALLOWLIST_RELEASE_DRIFT` check against `VERSION` | `sed -n '272,278p;684,692p' P/runtime/verify.py` | CONFIRMED |
| 7 | GUIDE-100:102 | Chain RC1→RC2→1.0.0→1.1.0→1.2.0, 1.2.0 immediate predecessor | `python3 -c "…FRAMEWORK.json['baseline_chain']"` | CONFIRMED |
| 8 | GUIDE-100:103 | `clean_zip_sha256` `cc2a4438…`, `candidate_tree_sha256` `add66854…` | `python3 -c "…FRAMEWORK.json['predecessor_release']"` | CONFIRMED |
| 9 | GUIDE-100:111 | `MODULE_INDEX_DRIFT` compares package set to indexed ids | `sed -n '259,264p' P/runtime/verify.py` | CONFIRMED |
| 10 | GUIDE-100:115 | 33 modules, 33 manifests, 33 narratives | `find P -name MODULE_MANIFEST.yaml \| wc -l` → 33; `find P -name MODULE.md \| wc -l` → 33; `MODULE_INDEX.json` → 33 | CONFIRMED |
| 11 | GUIDE-100:124 | `REQUIREMENT_REGISTRY_DRIFT` reconciles the registry against the union of packages | `sed -n '265,270p' P/runtime/verify.py` | CONFIRMED |
| 12 | GUIDE-100:127 | 99 core requirements, 105 total, 6 successor-governance | `FRAMEWORK.json['counts']` → `core_requirements 99, requirements 105, successor_governance_requirements 6`; `CANONICAL_REQUIREMENTS.json` → 99 rows | CONFIRMED |
| 13 | GUIDE-100:131 | 31 interfaces; `MODULE_UNKNOWN_INTERFACE` guards manifests | `INTERFACE_INDEX.json` → 31; `verification-model.json` `section_structure` | CONFIRMED |
| 14 | GUIDE-100:139 | `run_all.py` invokes five control families | `grep -n 'absolute_validate\|run_successor_controls\|deep_verify\|verifier_mutation_check\|validate_v2_contracts' P/09_tests_evals/run_all.py` → L25,26,30,33,37 | CONFIRMED |
| 15 | GUIDE-100:143–146 | `TEST_MANIFEST.json` is a description; nothing validates it | `grep -rn TEST_MANIFEST P/runtime/ P/tools/ P/09_tests_evals/` → **no hits** | CONFIRMED |
| 16 | GUIDE-100:174 | Stamp grammar: kind, uppercase status, 7–40 hex, ISO date, pass name | `sed -n '43,47p' R/engine/tools/docgen/identity.py` (`STAMP_RE`) | CONFIRMED |
| 17 | GUIDE-100:175 | `artifact-hardened` is the only drift-sensitive kind | `identity.py:56` — `DRIFT_SENSITIVE_KINDS = ("artifact-hardened",)` | CONFIRMED |
| 18 | GUIDE-100:188 | Every document `verified_state: unverified`, no stamp | `grep -h '^verified_state' *.md \| uniq -c` → 8; stamp grep → none | CONFIRMED |
| 19 | GUIDE-100:197 | Rendered under Graphviz 15.1.0 (20260618.0150) | `dot -V`; `grep -rhoE "Generated by graphviz version …" --include='*.svg' P` → **35/35 unanimous** | CONFIRMED |
| 20 | SYS-110:53–57 | `FORBIDDEN_PARTS` denylists `.git`; a working tree can now pass | `sed -n '109,113p' P/01_control_plane/…/release_integrity.py`; `.git` is at the repository root | CONFIRMED |
| 21 | SYS-110:43–51 | Four root-entry roles | `ls -1 R/` → `_release engine absolute-canonical-framework-v1.3.0 docs README.md RELEASE_STAMP.json MANIFEST.sha256 CHANGELOG.md CLAUDE.md` | CONFIRMED (see O-6) |
| 22 | SYS-110:118 | V2 contract layer since 1.2.0, validated by `tools/validate_v2_contracts.py`, wired into the aggregate suite | dir `P/governance/coverage_closure_v3/v2_contracts/` exists; `run_all.py:37` | CONFIRMED |
| 23 | SYS-110:182–186 | The nine `runtime/*.py` ownership statements | `git -C P ls-files 'runtime/*.py'` → all named files present | CONFIRMED |
| 24 | SYS-110:72–79 | Derived set (metadata, allowlist, svg, blueprint, machine, sidecars, builds, indexes, graphs) | cross-checked against `REGENERATE.md`/GUIDE-170 and the derive script's writes | CONFIRMED |
| 25 | SYS-120:103–107 | One version in four representations; all 33 narratives two releases behind their manifests | `grep -rh '^framework_release' predecessor/…-v1.2.0 --include=MODULE.md` → **33× `1.0.0`**; same over `MODULE_MANIFEST.yaml` → **33× `1.2.0`** | CONFIRMED |
| 26 | SYS-120:111–117 | The four new `FRAMEWORK_STRUCTURE` codes and what each compares | `grep -n` in `P/runtime/verify.py` → L209, L213, L217, L274 | CONFIRMED |
| 27 | SYS-120:119 | `_front_matter()` at `runtime/verify.py` line 77 | `grep -n 'def _front_matter' P/runtime/verify.py` → **77** | CONFIRMED |
| 28 | SYS-120:120–123 | `FRAMEWORK_COUNT_DRIFT` re-derives modules/interfaces/core_requirements/profiles/adapters | `sed -n '278,292p' P/runtime/verify.py` | CONFIRMED |
| 29 | SYS-120:129–131 | Policy `EXACT_RECORD_SET_FAIL_CLOSED`; 879 records against a 1,079-file tree through 1.2.0 | `python3 -c` over `predecessor/…-v1.2.0/RELEASE_ALLOWLIST.json` → `ABS.RELEASE.1.0.0-RC3 879 EXACT_RECORD_SET_FAIL_CLOSED`; `find predecessor/…-v1.2.0 -type f \| wc -l` → **1079** | CONFIRMED |
| 30 | SYS-120:134–139 | The governance allowlist codes, `__pycache__` the only exclusion | `grep -n ALLOWLIST P/runtime/verify.py` → L681–733; `verification-model.json` `section_governance` | CONFIRMED |
| 31 | SYS-120:154–159 | 11 mutations, 6 wired sections, three added in 1.3.0 (named) | `grep -c '^    (' P/tools/verifier_mutation_check.py` → **11**; `SECTIONS` keys → the six named; `verification-model.json` `mutation_controls.count` → 11 | CONFIRMED |
| 32 | SYS-120:161–164 | The harness imports the *mutated* copy | `sed -n '163,178p' P/tools/verifier_mutation_check.py` — comment and `sys.path.insert` confirm it | CONFIRMED |
| 33 | SYS-120:168–175 | Only `FRAMEWORK_IDENTITY` and `SIMULATION` are red, for the stated reasons | my `deep_verify.py` run: exactly those two, `SIMULATION` findings all cite `DOC_SCHEMA_VIOLATION at MODULE_MANIFEST.yaml` | CONFIRMED |
| 34 | **SYS-120:199** | "The **nine** named `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE` check codes above" | count of the codes the same document names (L111–117, L134–139) | **WRONG (W-5)** |
| 35 | REF-130:76 | Five adapters | `FRAMEWORK.json['counts']['adapters']` → 5 | CONFIRMED |
| 36 | REF-130:83 | Four profiles | `FRAMEWORK.json['counts']['profiles']` → 4 | CONFIRMED |
| 37 | REF-130:91–109 | The eight pin bucket classes beyond `VERSION` | `machine/extension-points.json` `release_version.also_update` → the same eight names | CONFIRMED |
| 38 | GUIDE-140:31–35 | Measured position: 8 sections + validator PASS, identity and simulation red | my `deep_verify.py` + `absolute_validate.py` runs | CONFIRMED |
| 39 | GUIDE-140:77–87 | Five aggregate control families, itemized | `run_all.py`; `verification-model.json` `aggregate_controls` (5 entries) | CONFIRMED |
| 40 | GUIDE-140:103 | 11 controls over 6 sections | as #31 | CONFIRMED |
| 41 | GUIDE-140:112–116 | V2 validator wired into `run_all.py` since 1.2.0; previously FAIL with nothing running it | `run_all.py:37`; payload `CHANGELOG.md` 1.2.0 `Fixed` | CONFIRMED |
| 42 | GUIDE-140:124,149 | The environment **is** pinned, at 15.1.0 (20260618.0150) | `P/LIMITATIONS.md` L100–107; 35/35 SVG comments unanimous | CONFIRMED |
| 43 | GUIDE-140:155 | `jsonschema` must be 4.x; 3.2.0 throws `Draft202012Validator` | `R/README.md` L70–73 | CONFIRMED |
| 44 | GUIDE-140:158 | Without `dot`, parity is `VISUAL_PARITY_NOT_RUN`, a finding not a skip | `P/runtime/verify.py:349`; `P/LIMITATIONS.md:73` | CONFIRMED |
| 45 | GUIDE-140:161 | Modes 644/755 checked but not part of candidate identity | `P/01_control_plane/…/RELEASE_PROCEDURE.md` L17–24 | CONFIRMED |
| 46 | GUIDE-140:138–141 | Output must be outside the project tree and must not already exist | `build_release.py:53–57` (`output must be outside the source tree`) and `:103–105` (`overwrite denied` unless `--replace` + authorized + rollback dir) | CONFIRMED |
| 47 | **GUIDE-140:133–136** | "**Eight steps**, in the canonical order, **derived from** the normative procedure document's own headings" | `grep -n '^## ' P/01_control_plane/…/RELEASE_PROCEDURE.md` → **nine** numbered headings; `machine/release-model.json` `procedure` → **nine** entries | **WRONG (W-6)** |
| 48 | REF-150:47 | Baseline 3 pass / 28 fail / 7 skip, exit 1 | `machine/evaluation-baseline.json` `engine_health` | CONFIRMED |
| 49 | REF-150:53 | Subject deep-verify: 2,688 checks, 35 findings, 8 of 10 sections | `evaluation-baseline.json` `subject_declared_environment.deep_verify` | CONFIRMED |
| 50 | REF-150:60–63 | Usability 4/5 then 5/5; failing question was enforcement; six sections lacked a protection claim | `machine/agent-usability-result.json` (`red_pass.answered 4`, `cause`, `green_pass.answered 5`) | CONFIRMED |
| 51 | REF-150:79–81 | F-05: 33 narratives at `1.0.0`; schema now pins the release | as #25; `04_enforcement/schemas/module_manifest.schema.json` `const` | CONFIRMED |
| 52 | REF-150:104–107 | 35 `.dot` sources; 32 rendered by 2.42.4 and 3 by 2.43.0, neither recorded | `grep -rhoE "Generated by graphviz version [0-9.]+" predecessor/…-v1.2.0 \| sort \| uniq -c` → **32× 2.42.4, 3× 2.43.0** | CONFIRMED |
| 53 | REF-150:115–119 | `.git` inside the payload through 1.2.0, recorded in `RELEASE_STAMP.json` as a working-tree note dated 2026-09-06 | `R/RELEASE_STAMP.json` → `working_tree_note`, `stamped_utc 2026-09-06T18:26:42Z`, `candidate_id ABS.CANDIDATE.1.2.0` | CONFIRMED |
| 54 | REF-150:124–127 | RC3 allowlist: 879 records / 1,079-file tree; generator looked the baseline up by chain position | as #29; `generate_release_allowlist.py` L10–15 docstring + L39–43 | CONFIRMED |
| 55 | **REF-150:129** | "It is fixed and now read on every run: `ABS.RELEASE.1.3.0`, **1,079 records**" | `python3 -c "…RELEASE_ALLOWLIST.json['record_count']"` → **1103** | **WRONG (W-1)** |
| 56 | REF-150:136–147 | `_release/predecessors/` holds the sealed RC2 zip and every other chain entry | `ls -1 R/_release/predecessors/` → RC1, RC2, 1.0.0, 1.1.0, 1.2.0 zips + `.sha256` each | CONFIRMED |
| 57 | **REF-150:225–227** | Engine self-health "**28 pass / 5 fail / 5 skip** (`CONS-11`, `BUILD-01`, `BUILD-03`, `SUITE-03`, `SUITE-05`)" | `cd engine && PYTHONDONTWRITEBYTECODE=1 python3 -m tools.health --json --no-run-log` → **24 pass / 10 fail / 4 skip**, exit 1 | **WRONG (W-2)** |
| 58 | REF-150:229–241 | OG-244…OG-248, each described | `grep -n 'OG-24[4-8]' R/engine/CHANGELOG.md` → L47–51, descriptions match one-for-one | CONFIRMED |
| 59 | **REF-150:97, :155** | Two resolved items "carried forward under 'What remains a limitation'" | `awk` the remains block → nine H3s, **neither item among them**; `machine/limitations-register.json` classifies both `REMAINS_A_LIMITATION` | **WRONG (W-7)** |
| 60 | REF-150:82 vs register | "**three** `FRAMEWORK_STRUCTURE` check codes" for F-05 | `limitations-register.json` F-05 `control` says "**four** FRAMEWORK_STRUCTURE check codes" and its `evidence` lists four | **UNVERIFIABLE (U-1)** — prose and register disagree; the tree cannot say which scoping was intended |
| 61 | REF-150 register | Disposition counts 5 / 10 / 9 back figure `field-trial-disposition` | `limitations-register.json` → 24 rows, `RESOLVED_IN_1_3_0` 5, `REMAINS_A_LIMITATION` 10, `INSTRUMENT_STATE` 9; sidecar items identical | CONFIRMED |
| 62 | REF-160:38–40 | Sixth routing row → `machine/release-model.json` | file exists, carries `repository`, `engine_pin`, `pins`, `procedure`, `baseline_chain`, `predecessor` | CONFIRMED |
| 63 | **REF-160:75–76** | "`verified` is 0 across all **28** nodes … **0 of 28** nodes are at rung 4 or deeper" | `python3 -m tools.blueprint completeness` → `30 node(s)`; `COMPLETENESS.md` L21 → "only **0 of 30**" | **WRONG (W-4)** |
| 64 | **REF-160:86** | "GUIDE-170 states this consequence in full for the containers this release touches" | `grep -in 'rung\|container\|completeness' P/docs/ultimate-engine/GUIDE-170-repository-release.md` → **no such statement** | **WRONG (W-8)** |
| 65 | REF-160:80–82 | The `gatekeepers` column is derived from the guard's own source | `blueprint/SYSTEM.md` §The risky core | CONFIRMED |
| 66 | GUIDE-170:74–93 | The gitignore classes, verbatim by class | `cat R/.gitignore` — every listed entry present, no class invented | CONFIRMED |
| 67 | GUIDE-170:99–113 | Pin table: 33 × manifest, 33 × narrative, nine classes | `machine/release-model.json` `pins` → `module_manifests 33`, `module_narratives 33`, nine keys + `total_pinned_files` | CONFIRMED |
| 68 | GUIDE-170:132 | "the release metadata must follow the allowlist, because the candidate hash … covers the allowlist file itself" | `CANDIDATE_HASH_EXCLUSIONS` (`release_integrity.py` L95–103) does **not** exclude `RELEASE_ALLOWLIST.json` | CONFIRMED — and this is what makes W-3 a contradiction |
| 69 | **GUIDE-170:143–144 + §3–8** | "**Nine steps, mirroring** `RELEASE_PROCEDURE.md`'s own numbered headings **so this summary cannot drift**" | `grep -n '^## ' RELEASE_PROCEDURE.md` vs the document's own `### N.` headings | **WRONG (W-3)** |
| 70 | GUIDE-170:171–176 | `--check` exits 0 on PASS, 2 on drift; output forced to the candidate-local file | `sed -n '203,225p' P/01_control_plane/…/generate_release_allowlist.py` (`return 2` on drift; `output must be the candidate-local …`) | CONFIRMED |
| 71 | GUIDE-170:165–170 | Generator refuses any baseline not named `absolute-canonical-framework-v1.0.0-rc.2`, verified against a detached checksum ledger | same file, L66–90 | CONFIRMED |
| 72 | GUIDE-170:226–243 | RC1 = input baseline, RC2 = allowlist baseline; looked up by release id | `generate_release_allowlist.py` L39–43 (`ALLOWLIST_BASELINE_RELEASE_ID = "ABS.RELEASE.1.0.0-RC2"`, `next(... if entry["release_id"] == ...)`) | CONFIRMED |
| 73 | GUIDE-170:249–252 | Engine is Ultimate Engine 1.0.5, subtree from `FreeXStudio-Platform/ultimate-engine@185725a`, outside release identity | `cat R/engine/PROJECT_VERSION` → 1.0.5; `git log -1 --format=%B 3ecedf3`; engine is outside the payload | CONFIRMED |
| 74 | GUIDE-170:313–316 | `ENGINE_AUTHORED_DOCS_ROOT` is config-declared (`docSystem.authoredDocsRoot`), read dynamically | `grep -n authoredDocsRoot R/engine/engine.config.json` → L91; `R/engine/tools/docgen/engine_config.py:410` | CONFIRMED |
| 75 | GUIDE-170:322–324 | `build.log` deliberately not copied; graph JSON carries a deterministic `content_version` | `find P -name build.log` → none; `graphs/structure/graph.json` `graph.content_version = 015db069` | CONFIRMED |
| 76 | **GUIDE-170:333** | "This repository **is published** as a private repository, default branch `main`, with one annotated tag per release" | `git remote -v` → **empty**; `git tag --list` → **empty** | **UNVERIFIABLE (U-2)** — planned, not yet true |
| 77 | GUIDE-170:348–353 | "first stable release" = internally verified, certification pending; never certified | `FRAMEWORK.json` `status`; `RELEASE_PROCEDURE.md` §8 | CONFIRMED |
| 78 | README/DOCS_INDEX/CONTENT_INDEX | Eight governed documents in the set | `DOCS_INDEX.html` lists 8 ids; `CONTENT_INDEX.json` `counts` → `{manifest_rows: 8, public: 8, non_public_excluded: 2}` | CONFIRMED |
| 79 | `system.spec.json` | Name 1.3.0; `documentation-derivation` owner → GUIDE-170; no `depthFloor` touched | `git diff d647a61 -- P/system.spec.json` → exactly three changed lines, zero `depthFloor` | CONFIRMED |
| 80 | `PROJECT_INDEX.json` | 16 artifacts incl. GUIDE-170 and `MERMAID-release-pipeline`; no 1.1.0 summaries left | `python3 -c` over the file; `grep -c '1\.1\.0'` → 0 | CONFIRMED |

*(Rows 1–80 with eight consolidated pairs give the 70 distinct claims counted above.)*

---

## WRONG and UNVERIFIABLE claims, with the correcting fact

### W-1 · REF-150 states the wrong allowlist record count — **blocking**

**`absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.md:129`**
(propagated to `REF-150-evidence-limitations.html` and to
`docs/archive/REF-150/v1/REF-150-evidence-limitations.md:129`)

> It is fixed and now read on every run: `ABS.RELEASE.1.3.0`, **1,079 records**, verified against the
> baseline by release id rather than by chain position.

**Correcting fact:** `RELEASE_ALLOWLIST.json` `record_count` is **1103**, not 1,079.
`python3 -c "import json;print(json.load(open('RELEASE_ALLOWLIST.json'))['record_count'])"` → `1103`;
`find absolute-canonical-framework-v1.3.0 -type f -not -path "*/__pycache__/*" | wc -l` → `1103`.
1,079 was the count at the time of the architect pass (OUTLINES §0.3, which explicitly warned it
would change); the documentation pass added 24 files. This is the exact hand-typed-count failure
§H.4 forbids, in the document that owns the honesty boundary.

### W-2 · REF-150 states an engine self-health number that does not reproduce — **blocking**

**`…/REF-150-evidence-limitations.md:225–227`** (+ HTML + archive v1)

> The Ultimate Engine's own health check on itself, at version 1.0.5, reports **28 pass / 5 fail /
> 5 skip** (`CONS-11`, `BUILD-01`, `BUILD-03`, `SUITE-03`, `SUITE-05`).

**Correcting fact:** measured in this repository, from the vendored engine —
`cd engine && PYTHONDONTWRITEBYTECODE=1 python3 -m tools.health --json --no-run-log` (exit 1) —
the result is **24 pass / 10 fail / 4 skip** over 38 checks, failing `STRUCT-03`, `STRUCT-04`,
`STRUCT-06`, `RULE-01`, `CONS-11`, `BUILD-01`, `BUILD-02`, `BUILD-03`, `SUITE-03`, `SUITE-05`.
Run twice, identical both times. FACTS L80–82 records 28/5/5 and FACTS **Addendum 3** records a
third result (29 pass / 4 fail / 5 skip, a different fail set) for a differently-parameterised run —
so this number is invocation-dependent, and Addendum 3 states outright that *"the engine's
self-tests are not meaningful from the vendored copy."* REF-150 presents one of the three
unqualified, with no root, no invocation and no date, in a section whose first rule is that `PASS`,
`FAIL`, `SKIP` and `CANNOT_VERIFY` are not interchangeable. Either quote the measurement **with the
exact command and root it came from**, or state it as `CANNOT_VERIFY` for the vendored copy and cite
the standalone checkout Addendum 3 describes.

### W-3 · GUIDE-170's numbered procedure does not mirror the normative one it claims to mirror — **blocking, highest priority**

**`…/GUIDE-170-repository-release.md:143–144`** and its `### 0.`–`### 8.` headings (L146–222)

> **Nine steps, mirroring** `01_control_plane/manifests_releases/RELEASE_PROCEDURE.md`'s own numbered
> headings **so this summary cannot drift from the normative procedure it points at.**

**Correcting fact:** the ordinals do not correspond. `grep -n '^## ' RELEASE_PROCEDURE.md`:

| normative `RELEASE_PROCEDURE.md` | GUIDE-170 |
|---|---|
| `## 0. Environment` | `### 0. Environment` ✓ |
| `## 1. Freeze the payload` | `### 1. Freeze the payload` ✓ |
| `## 2. Bind the release metadata` | `### 2. Bind the release metadata (twice)` ✓ |
| — *(no such heading)* | `### 3. Regenerate the release allowlist` ← **inserted** |
| `## 3. Verify — all of it, in a fresh process` | `### 4. …` ← shifted |
| `## 4. Build` | `### 5. Build` ← shifted |
| `## 5. Verify the artifact, not the working tree` | `### 6. …` ← shifted |
| `## 6. Reproduce` | `### 7. Reproduce` ← shifted |
| `## 7. Record` | `### 8. Record` ← shifted |
| `## 8. Do not rename it` | *(absorbed into step 8's prose, no heading)* | 

A reader who follows GUIDE-170's "step 5. Build" and opens `## 5` in the normative document lands on
"Verify the artifact, not the working tree". `machine/release-model.json`'s **derived** `procedure`
array carries the normative nine with the correct ordinals — the document does not use it, so the
sentence claiming the summary "cannot drift" is exactly the drift it disclaims. Either renumber to
the normative ordinals and present the allowlist regeneration as an unnumbered step *before* step 2,
or drop the "mirroring … cannot drift" sentence and say plainly that this is a re-ordered operational
summary.

### W-4 · GUIDE-170 contradicts itself on metadata-vs-allowlist ordering — **blocking, highest priority**

**`…/GUIDE-170-repository-release.md:126–133`** vs **`:159–177`**

L126–133 (§"The order that avoids a red tree"):
> `VERSION` moves first; then the pins; then the derivatives; then the documentation; then the
> allowlist; **then** the release metadata; then the build. … the release metadata must follow the
> allowlist, because the candidate hash the metadata binds covers the allowlist file itself.

L159–177 (§"The release procedure, in order"): `### 2. Bind the release metadata (twice)` comes
**before** `### 3. Regenerate the release allowlist`.

**Correcting fact:** the rationale in L132 is *correct* and I verified it —
`CANDIDATE_HASH_EXCLUSIONS` in `01_control_plane/manifests_releases/tools/release_integrity.py`
(L95–103) lists `MANIFEST.json`, `CANDIDATE_SOURCE_MANIFEST.json`, `SHA256SUMS.txt` and the four
`.absolute/release/*` records, and **does not exclude `RELEASE_ALLOWLIST.json`**, so the allowlist
is inside the candidate digest. Following the numbered procedure literally binds metadata to a
candidate hash that step 3 then invalidates; the next `deep_verify` would report
`TREE_INTEGRITY_FAIL` and the whole metadata bind would have to be redone. WRITER-BRIEF §9,
OUTLINES §I step 19 and FACTS Addendum 1 all state the allowlist is the **last** payload step, i.e.
before the metadata. The numbered section is the half that is wrong.

### W-5 · SYS-120's enforcement table under-counts the codes the same document names

**`…/SYS-120-runtime-enforcement.md:199`**

> | Cross-representation pins | … | The **nine** named `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE`
> check codes above. |

**Correcting fact:** the document names **four** structure codes (L111–117) and **six** governance
checks / **seven** governance codes (L134–139): 4 + 6 = 10, or 4 + 7 = 11. `verification-model.json`
`section_governance` lists all seven `ALLOWLIST_*` codes. "Nine" matches neither the document's own
enumeration nor the derived model. (OUTLINES §0.2 reached nine by counting the two schema paths as
one *extra* rather than as governance codes; the document then counted them as a sixth governance
check and kept the nine.) State the count the way the body enumerates it, or cite
`verification_model…check_codes` and stop typing a total.

### W-6 · GUIDE-140 calls a typed, incomplete list "derived"

**`…/GUIDE-140-operations-verification.md:133–136`**

> **Eight steps**, in the canonical order, **derived from the normative procedure document's own
> headings so this summary cannot drift from it**: Environment · Freeze the payload · … · Record.

**Correcting fact:** `RELEASE_PROCEDURE.md` has **nine** numbered headings and
`machine/release-model.json`'s derived `procedure` array has **nine** entries; the list here is the
first eight and silently drops `## 8. Do not rename it`. The titles it does give are correct and in
order, so the harm is bounded — but the sentence asserts derivation for a value that was typed.
Either take nine from the derived model, or say "the first eight of the procedure's nine headings;
the ninth is a naming prohibition, quoted in GUIDE-170 §8".

### W-7 · REF-150 forwards the reader to items that are not in the section named

**`…/REF-150-evidence-limitations.md:97`** and **`:155`**

> This limitation is **carried forward under "What remains a limitation"** rather than closed here.
> … so this item is **also carried forward under "What remains a limitation."**

**Correcting fact:** the "What remains a limitation" section contains exactly nine H3s —
Independent certification · The ledger detects edits, not a full rewrite · Rollback is declared, not
rehearsed · Concurrency is single-host · Visual parity depends on the renderer build · Tree identity
covers everything, and that costs something · Content truth and external surfaces · Mutation coverage
is a list, not a proof · The instrument's own state. **Neither the test-manifest residual nor the
regeneration-procedure residual has an H3 there.** `machine/limitations-register.json` classifies
both (`F-06-test-manifest-description-only`, `stale-regeneration-procedure`) as
`REMAINS_A_LIMITATION`, so the prose and the machine layer that feeds figure
`field-trial-disposition` disagree — and `GUIDE-170:107` routes a reader to REF-150 for exactly the
test-manifest residual (*"not mechanically checked — see REF-150"*), where the section it points to
does not carry it. Add the two H3s, or change both forward references to say the residual is stated
in place.

### W-8 · REF-160 attributes to GUIDE-170 a statement GUIDE-170 does not make

**`…/REF-160-agent-blueprint-guide.md:86`**

> [GUIDE-170] **states this consequence in full** for the containers this release touches.

**Correcting fact:** `grep -in 'rung\|container\|completeness' GUIDE-170-repository-release.md`
returns nothing about rungs, containers, node states or the `verified` predicate. GUIDE-170 never
discusses blueprint completeness. Either add the statement to GUIDE-170 (it belongs there under the
`documentation-derivation` reassignment) or point the sentence at `blueprint/COMPLETENESS.md`, which
does state it in full.

### W-4′ (numbered W-4 in the claim table) · REF-160's node count is stale

**`…/REF-160-agent-blueprint-guide.md:75–76`** (+ HTML + archive v1)

> `verified` is **0** across all **28** nodes … `verified` requires rung 4 or deeper, and **0 of 28**
> nodes are at rung 4 or deeper.

**Correcting fact:** the blueprint now has **30** nodes.
`python3 -m tools.blueprint completeness` → `30 node(s) — sketched 7 · documented 23 · verified 0`;
`blueprint/COMPLETENESS.md:21` → *"only **0 of 30** nodes are at rung 4 or deeper"*, and L23 →
*"7 container(s) have no rung-4 module at all"*. The writer's own run record states 30, and
OUTLINES §F predicted the 28→30 move; the prose carried the pre-pass 28 through. The **claim**
(`verified` is 0, structurally unreachable) is true; only the denominator is wrong, twice.

### U-1 · REF-150 prose and the limitations register disagree on F-05's control count

`REF-150:82` says "**three** `FRAMEWORK_STRUCTURE` check codes (`MODULE_RELEASE_PIN_DRIFT`,
`MODULE_NARRATIVE_MISSING`, `MODULE_NARRATIVE_RELEASE_DRIFT`)"; `machine/limitations-register.json`
row `F-05-narrative-release-pins` says "**four** FRAMEWORK_STRUCTURE check codes" and lists
`FRAMEWORK_REGISTRY_RELEASE_DRIFT` as the fourth. Both readings are defensible — the fourth code
pins the *registry* rather than the *narrative* — and the tree cannot say which scoping was intended.
Reconcile the two; whichever is chosen, the register is the sourced artifact and the prose should
follow it.

### U-2 · GUIDE-170's GitHub conventions are written in the present tense for a publication that has not happened

`GUIDE-170:333`: *"This repository **is published** as a private repository, default branch `main`,
with one annotated tag per release in the form `vX.Y.Z`."* Measured: `git remote -v` is **empty** and
`git tag --list` is **empty**. OUTLINES §B.8 explicitly sanctioned the "conventions form" for this
section, while §H.2 forbids "the repository is published at …" while no remote or tag exists. I am
recording it rather than calling it WRONG because the orchestrator's own closing steps (push + tag)
make it true, and the outline authorized the phrasing. **Re-check after the push**: if the repository
is published and tagged as `v1.3.0` before the stamp, the sentence becomes accurate and needs no
edit; if publication slips, it must be reworded to the conditional.

---

## Non-blocking observations (no action required before the stamp)

- **O-1** `machine/evaluation-baseline.json` was **not** extended with `subject_release`,
  `subject_layout` and `scope` as OUTLINES §E prescribes ("KEEP AS HISTORY + minimal EXTEND"), and
  the omission is not recorded in `WRITER-RUN-2026-09-07.md`'s deviations. The risk it was meant to
  close — a reader mistaking the 2026-09-01 numbers for current — is closed anyway by REF-150's prose
  and by the figure caption (*"captured 2026-09-01 against the framework at release 1.1.0"*), so this
  is an unrecorded deviation rather than a live hazard.
- **O-2** `SYS-110:48` describes `_release/` as "the current release's zip and detached SHA-256, plus
  `_release/predecessors/`". `_release/` currently contains only `predecessors/` — the 1.3.0 zip is
  produced at the end. It reads as a role description, but a literal reader checking the directory
  finds the first half absent.
- **O-3** `machine/release-model.json` `repository.root_entries` enumerates the live working-tree
  contents, including the gitignored `predecessor/` and the repository's `CLAUDE.md`. That derived
  value is host-dependent: a fresh clone would produce a different array, so this one field breaks
  the "a second run changes nothing" property across environments (it holds within this one).
- **O-4** `system.spec.json`'s `$schema` string still reads *"enforced by the sibling Ultimate
  Engine"* — the field-trial phrasing the `_readme` edit corrected. §F only named `_readme`, so this
  is in-spec, but it is the last surviving "sibling engine" phrase in the payload.
- **O-5** `docs/ultimate-engine/REGENERATE.md` closes with *"If this file's regeneration commands and
  GUIDE-170's ever disagree"* — this file no longer carries regeneration commands.
- **O-6** `GUIDE-100:115` writes "33 modules, 33 manifests, 33 narratives — derived from the tree, not
  typed". The values are correct and are derived elsewhere, but the sentence names no file or command,
  which is what §H.4 asks of a number in prose.
- **O-7** The Addendum-4 repair to `04_enforcement/validators/absolute_validate.py` is correctly
  scoped and I verified it works (validator PASS 5/5, 0 errors). One property worth knowing: its
  `_link_base()` resolves an archived generation's links by globbing `docs/**/<basename>` and only
  applies the redirect when **exactly one** live match exists. If two governed documents ever share a
  basename, it silently falls back to the old behaviour. Correct today; worth a comment upstream.

---

## What the orchestrator must do next

### Required fixes, in priority order

1. **W-3 + W-4 — GUIDE-170's release procedure.** Fix the ordering contradiction and the numbering
   claim together, because they are the same defect seen twice. Recommended: keep §"The order that
   avoids a red tree" as written (it is correct and its reason is verified), move the allowlist
   regeneration ahead of the metadata bind in §"The release procedure, in order", and renumber the
   H3s to the normative `RELEASE_PROCEDURE.md` ordinals — presenting the allowlist step as an
   explicitly unnumbered "before step 2" so the "mirroring … cannot drift" sentence becomes true.
   **This one is not optional and not cosmetic:** the orchestrator's own next action is the metadata
   bind, and the document as written prescribes doing it too early.
2. **W-1 — REF-150:129.** `1,079 records` → `1,103 records`. Better: cite
   `RELEASE_ALLOWLIST.json`'s `record_count` rather than typing a number that changes every time a
   file is added.
3. **W-4′ — REF-160:75–76.** `28` → `30`, both occurrences. Better: cite
   `blueprint/COMPLETENESS.md`, which derives it.
4. **W-2 — REF-150:225–227.** Give the engine-health figure its command and root, or downgrade it to
   `CANNOT_VERIFY` for the vendored copy with a pointer to Addendum 3. Do not leave an unqualified
   number in the document whose subject is the difference between a measurement and a claim.
5. **W-7 — REF-150:97 and :155.** Either add the two missing "remains" H3s (matching
   `limitations-register.json`, which already classifies both as `REMAINS_A_LIMITATION`) or rewrite
   both forward references. Fixing this also repairs `GUIDE-170:107`'s dangling route.
6. **W-5 — SYS-120:199.** Correct "nine" to match the body's own enumeration, or replace the count
   with a reference to `verification_model…check_codes`.
7. **W-8 — REF-160:86.** Add the statement to GUIDE-170 or repoint the sentence at
   `blueprint/COMPLETENESS.md`.
8. **W-6 — GUIDE-140:133–136.** Take the nine steps from `machine/release-model.json`'s `procedure`,
   or state explicitly that this is the first eight of nine and why.
9. **U-1 — REF-150:82 vs the register.** Reconcile three-vs-four; the register is the sourced side.

### The rework loop these fixes require — plan for it

Editing any of the eight bodies is not a one-line change in isolation. In order:

1. Edit the `.md` bodies (all fixes above touch `REF-150`, `REF-160`, `SYS-120`, `GUIDE-140`,
   `GUIDE-170`; `machine/limitations-register.json` if W-7/U-1 are fixed there).
2. Re-run the derive script (step 5), then the strict build ×8 and `check` ×8, then the two indexes.
3. **Re-cut the archives.** `docs/archive/<id>/v1/` currently holds byte-identical snapshots of the
   *old* bodies; the deterministic validator's new `check_links` depends on that byte-identity, and
   `HISTORY.md` records a sha256 that will no longer match. Re-cut every document whose body changes.
4. Rebuild the blueprint, re-render the Mermaid sources, rebuild the structure graph,
   re-register/rebuild `PROJECT_INDEX`.
5. Run the sequence a second time and confirm an empty diff.
6. **Regenerate `RELEASE_ALLOWLIST.json` last** (the archive re-cut may change the record set), then
   `--check`.
7. Re-run `deep_verify.py` and `absolute_validate.py`.

### Then, and only then, the stamp step

Once the fixes above are in and the loop above is clean, the set is ready for the orchestrator's
lifecycle closure. In order:

1. **Commit the frozen bodies.** The stamp's `<sha>` must be a commit in this repository that
   contains the body it certifies; `artifact-hardened` is drift-sensitive, so any edit after the
   stamp invalidates it.
2. **Apply the stamp** to each of the eight, using the grammar
   `<!-- artifact-hardened: <STATUS> @ <sha> on 2026-09-07 via <pass> -->`, and set
   `verified_state: verified` — the header field is the claim, the stamp is the evidence, and the
   engine treats `verified` without a covering stamp as a blocking finding. This moves the lifecycle
   from **40/48** to 48/48 (`missing stamp` is currently the only gap on all eight).
3. **Rebuild and re-verify after stamping** — the stamp changes each body, so the builds, the
   archives, the allowlist and `deep_verify` all need one more clean pass.
4. **Then** the release steps FACTS assigns to you and no one else:
   `prepare_release_metadata.py` ×2 → allowlist re-check → `run_all.py` → build → verify the
   artifact → reproduce → `RELEASE_STAMP.json` → tag → GitHub release. Expect `FRAMEWORK_IDENTITY`
   and `SIMULATION` to go green at the metadata step, and re-measure
   `seal_accepts_a_package_still_full_of_template_text` (currently MISSED in the same window) then.
5. **Re-read U-2 after the push.** If the repository is published private on `main` and tagged
   `v1.3.0`, `GUIDE-170:333` becomes accurate as written and needs no edit.

### What I did not do

I fixed nothing, modified nothing in the payload, the engine or the pipeline records other than
writing this file. I did not run `prepare_release_metadata.py`, `build_release.py`, or any
state-changing git command. I did not regenerate `RELEASE_ALLOWLIST.json` (only `--check`). The
payload is byte-identical to the state I received; no `__pycache__` exists anywhere in the payload or
the engine; the only host state my runs created (`engine/.docgen`, `engine/.health` — empty,
gitignored, outside the payload) has been removed.

---

# Re-verification (pass 3 result) — 2026-09-07 15:10

Second verifier pass, same verifier, same discipline: I fixed nothing and changed nothing except
appending this section. Focus: are the nine required fixes closed, do the gates still pass, and does
anything new break under a fresh sample.

**Environment (identical to the first pass, never varied):**

```sh
export PYTHONDONTWRITEBYTECODE=1
export ENGINE_HOST_ROOT="$PWD/absolute-canonical-framework-v1.3.0"
export ENGINE_AUTHORED_DOCS_ROOT="docs/ultimate-engine"
export PYTHONPATH="$PWD/engine"
```

Engine commands from the repository root; payload tools from inside the payload.

**Non-modification proof.** Before any command I copied the payload byte-for-byte (**1,103 files**).
After every command in this section — the strict build ×2, `check` ×8, blueprint verify/completeness,
project_index verify, the derive script, `deep_verify.py`, `absolute_validate.py` and the allowlist
`--check` — `diff -rq` between that copy and the live payload reports **no differences**. Zero
`__pycache__` anywhere in the repository. The two gitignored engine host-state directories my
`tools.health` runs created (`engine/.docgen`, `engine/.health`, both outside the payload) were
removed after use.

---

## Per-finding closure

Each finding re-opened at its cited location and read as it now stands. **9 of 9 required fixes
CLOSED**; one of them (W-2) leaves a residual defect, recorded below as `W-2R`.

| # | Finding | Verdict | The line now present (and the check that settles it) |
|---|---|---|---|
| W-1 | REF-150 wrong allowlist record count (`1,079`) | **CLOSED** | `REF-150:132-134` — *"its record count read from `RELEASE_ALLOWLIST.json`'s own `record_count` field — mirrored in `machine/release-model.json`'s `allowlist` rather than typed here, because the count moves every time a file is added"*. No number is typed. `release-model.json` `allowlist.record_count` = **1103**, `RELEASE_ALLOWLIST.json` `record_count` = **1103**, `find … -type f` = **1103**. The derive script reads it (`derive_documentation_model.py:486`, `:682`), so it is genuinely derived. |
| W-2 | REF-150 engine self-health figure unqualified | **CLOSED** (residual `W-2R`) | `REF-150:253-259` now prints the exact command and root before the figure and states the invocation-dependence explicitly. The *qualification* the finding demanded is present. The figure itself still does not reproduce — see `W-2R` below. |
| W-3 | GUIDE-170's procedure did not mirror the normative ordinals | **CLOSED** | `GUIDE-170:143` — *"Ten steps, mirroring `01_control_plane/manifests_releases/RELEASE_PROCEDURE.md`'s own numbered headings (`0`–`9`)…"*, and the claim is now true — see the three-way ordinal table below. |
| W-4 | GUIDE-170 contradicted itself on metadata-vs-allowlist order | **CLOSED** | `GUIDE-170:159` `### 2. Regenerate the release allowlist` precedes `:174` `### 3. Bind the release metadata`, matching §"The order that avoids a red tree" (`:129-133`). `:172-173` states the reason in place: *"This step runs **before** the metadata bind, because the candidate hash the metadata binds covers the allowlist file itself."* |
| W-4′ | REF-160's stale node count (`28`) | **CLOSED** | `REF-160:74-78` — *"as recorded in `blueprint/COMPLETENESS.md`, `verified` is **0** across every tracked node … that same report states none of the tracked nodes are at rung 4 or deeper"*. No denominator typed. `blueprint completeness` → `30 node(s)`; `COMPLETENESS.md:21` → `0 of 30`. |
| W-5 | SYS-120's enforcement table under-counted ("nine") | **CLOSED** | `SYS-120:199` — *"\| Cross-representation pins \| … \| The `FRAMEWORK_STRUCTURE`/`FRAMEWORK_GOVERNANCE` check codes named above. \|"*. The count is gone; the row points at the document's own enumeration. |
| W-6 | GUIDE-140 called a typed, incomplete list "derived" | **CLOSED** | `GUIDE-140:133-137` — *"The canonical order — recorded in `machine/release-model.json`'s `procedure` array, which is derived from `RELEASE_PROCEDURE.md`'s own numbered headings rather than typed here — is: Environment · Freeze the payload · Regenerate the release allowlist · Bind the release metadata (twice) · … · Record · Do not rename it."* All ten steps named, in the derived order, no count asserted. |
| W-7 | REF-150 forwarded readers to items not in the section named | **CLOSED** | The "What remains a limitation" section now holds **11** H3s (`awk` the block + `grep -c '^### '` → 11), including `### The test manifest is a description, not a control` and `### The regeneration procedure is not self-verifying`. Both cite their `limitations-register.json` rows; both rows read `REMAINS_A_LIMITATION` with `control: null`. `GUIDE-170:107`'s route now lands on a section that carries the residual. |
| W-8 | REF-160 attributed a statement to GUIDE-170 | **CLOSED** | `REF-160:86-88` — *"…`blueprint/COMPLETENESS.md` states this consequence in full, per container, for every container this release touches."* Verified at `COMPLETENESS.md:24`, which names all seven rung-4-less containers **including `documentation-derivation`**, the container this pass reassigns. |
| U-1 | REF-150 prose vs register on F-05's control count | **CLOSED** | `REF-150:82-86` now reads *"as recorded in `machine/limitations-register.json`'s `F-05-narrative-release-pins` row: four `FRAMEWORK_STRUCTURE` check codes (… and `FRAMEWORK_REGISTRY_RELEASE_DRIFT` — the fourth pins the framework registry rather than the narrative…)"*. The register says four; `runtime/verify.py` defines all four (L209, L213, L217, L274). Prose now follows the sourced side, as required. |
| U-2 | GUIDE-170:333 present-tense publication | **CARRIED FORWARD, unchanged** | `git remote -v` and `git tag --list` are both still empty. Not a pass-3 failure — the first pass recorded this as conditional on the orchestrator's own push+tag. Re-check after publication. |

### W-3 / W-4 — the three-way ordinal check the task asked for, in full

`grep -n '^## ' RELEASE_PROCEDURE.md` vs `grep -n '^### [0-9]\.' GUIDE-170-…md` vs
`release-model.json` `procedure`:

| normative `RELEASE_PROCEDURE.md` | GUIDE-170 | `machine/release-model.json` `procedure` |
|---|---|---|
| `## 0. Environment` | `### 0. Environment` | `{ordinal: 0, title: "Environment"}` |
| `## 1. Freeze the payload` | `### 1. Freeze the payload` | `{1, "Freeze the payload"}` |
| `## 2. Regenerate the release allowlist` | `### 2. Regenerate the release allowlist` | `{2, "Regenerate the release allowlist"}` |
| `## 3. Bind the release metadata` | `### 3. Bind the release metadata` | `{3, "Bind the release metadata"}` |
| `## 4. Verify — all of it, in a fresh process` | `### 4. Verify — all of it, in a fresh process` | `{4, "Verify — all of it, in a fresh process"}` |
| `## 5. Build` | `### 5. Build` | `{5, "Build"}` |
| `## 6. Verify the artifact, not the working tree` | `### 6. Verify the artifact, not the working tree` | `{6, "Verify the artifact, not the working tree"}` |
| `## 7. Reproduce` | `### 7. Reproduce` | `{7, "Reproduce"}` |
| `## 8. Record` | `### 8. Record` | `{8, "Record"}` |
| `## 9. Do not rename it` | `### 9. Do not rename it` | `{9, "Do not rename it"}` |

**Ten ordinals, ten titles, exact string match on all three sides.** The allowlist step is `2` and
the metadata bind is `3` in every representation. Four further consistency checks, all clean:

- `release_procedure_steps()` (`derive_documentation_model.py:328-337`) parses `^## (\d+)\. (.+)$`
  out of `RELEASE_PROCEDURE.md` — the array is genuinely derived, not typed, so the "cannot drift"
  sentence is now backed by a mechanism.
- `GUIDE-140:133-137`'s prose list is the same ten titles in the same order.
- The derived figure `graphs/source/release-pipeline.mmd` renders `step0 → … → step9` with
  `2. Regenerate the release allowlist` feeding `3. Bind the release metadata`; the rendered
  `graphs/rendered/release-pipeline.svg` carries the same node labels in that order.
- `GUIDE-170:244`'s downstream cross-reference was updated with the renumbering — *"which is what
  **step 2** above consumes"* — and `grep -n 'step [0-9]'` across all eight documents returns that
  one hit and nothing stale.

---

## Gate table

Every gate the task requires, re-run by me, with the exit code as observed.

| # | Gate | Command | Exit | Result |
|---|---|---|---|---|
| 1 | Strict docgen build ×8 | `python3 -m tools.docgen.cli --strict build <8 paths> --formats html,json` | **0** | `built 8 doc(s) in 4.555s — 0 reused from cache, 8 rebuilt`. Run twice; the second run's output is byte-identical to what was on disk (`diff -rq` against the pre-run snapshot → no differences), so the build is a **fixed point**. |
| 2 | `docgen check` ×8 | `python3 -m tools.docgen.cli check <doc>.md` (×8) | **0 ×8** | Each: `docgen check: PASSED — header + taxonomy-prefix + manifest-drift + rulebook hash-gate`. |
| 3 | Blueprint verify | `python3 -m tools.blueprint verify` | **0** | `blueprint verify: clean — 7 container(s), 30 module(s), 297 document(s), 6 derived file(s)` |
| 4 | Blueprint completeness | `python3 -m tools.blueprint completeness` | **0** | `30 node(s) — sketched 7 · documented 23 · verified 0`; `document lifecycle: 40/48 step(s) complete across 8 governed document(s)`, all eight `missing stamp` and nothing else. **Ratchet memory reads `git history of the spec (7 container(s) remembered)`** (`COMPLETENESS.md:41`) — Addendum 4's calibration holds, no `UNAVAILABLE`. |
| 5 | Project index verify | `python3 -m tools.project_index.cli verify --scan docs/ultimate-engine` | **0** | `16 artifact(s) registered` · `OK — every registered artifact resolves to a real file, no duplicates.` |
| 6 | Deep verifier (inside payload) | `PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py` | **1** (expected) | `FAIL sections=8/10 checks=2896 findings=5 severity={'CRITICAL': 3, 'HIGH': 2}`. **PASS:** STRUCTURE 1018, REPRESENTATION 236, CONTRACTS 418, SEMANTICS 14, SECURITY 1104, GOVERNANCE 36, RUNTIME 43, DETERMINISTIC_VALIDATOR 7/0. **FAIL:** `FRAMEWORK_IDENTITY` (1, `TREE_INTEGRITY_FAIL`) and `SIMULATION` (4, all `DOC_SCHEMA_VIOLATION at MODULE_MANIFEST.yaml`) — exactly the two red-by-construction sections, and no others. Identical counts to the pre-pass-3 run. |
| 7 | Deterministic validator (inside payload) | `python3 04_enforcement/validators/absolute_validate.py .` | **0** | `{"status": "PASS", "counts": {"checks": 5, "errors": 0}}` — `modules`, `profiles_adapters`, `examples_semantics`, `security_hygiene`, `links` all PASS. **5/5.** |
| 8 | Release allowlist (inside payload) | `generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check` | **0** | `{"status": "PASS", "output": "…/RELEASE_ALLOWLIST.json"}`. **I did not regenerate it.** |
| 9 | Derive script (fixed point) | `python3 …/scripts/derive_documentation_model.py` | **0** | `derived documentation model: 1096 tracked files, 33 canonical modules, 284 authority edges, 8 figure sidecars`; `diff -rq` against the snapshot → **no differences**. |
| 10 | Bytecode hygiene | `find absolute-canonical-framework-v1.3.0 -name __pycache__` | — | **0 results**, before and after every Python invocation. |
| 11 | Host-state hygiene | `ls` for `.docgen` `.health` `graphify-out` `.blueprint` `.claude` at the payload root; `find … -name .docgen_cache.json` | — | **All absent** (`.claude/` is gone too — pass 3 removed it). |
| 12 | Ignored files inside the payload | `git status --short --ignored=matching … \| grep '^!!'` | — | **Empty.** |
| 13 | Working-tree scope | `git status --short absolute-canonical-framework-v1.3.0` | 0 | **76 paths, byte-identical to the pass 3 record's verbatim block** — `diff` on the sorted full lines (status codes included) and on the sorted paths alone both return empty. Nothing added, nothing dropped, no status code changed. |
| 14 | Headers ×8 | `grep -h '^<field>' *.md \| sort \| uniq -c` | — | 8× each of `last_reviewed: 2026-09-07`, `version: 1`, `revision: 0`, `verified_state: unverified`, `status: review`, `produced_by: Ultimate Engine 1.0.5`; per-document `id` correct on all eight. **No `artifact-hardened` stamp** — the only two hits are `GUIDE-100:174-175` describing the grammar with `<STATUS>`/`<sha>` placeholders, which cannot match `STAMP_RE`. |
| 15 | Archive generations ×8 | `shasum -a 256` live vs `docs/archive/<id>/v1/<file>.md` vs the `HISTORY.md` row | — | All eight present; **all eight byte-identical to their live bodies**; **all eight `HISTORY.md` sha256 values match their snapshot**. The five re-cut in pass 3 carry new hashes (e.g. GUIDE-170 `b891f1d64711…`, was `cbf378006ff2…`); all rows record `2026-09-07`, commit `d647a61`, `docgen 1.0.5`. |
| 16 | Changelog | `awk` over the payload `CHANGELOG.md` `### Documentation` block | — | The block holds the set-level preamble plus **eight** per-document lines, one for each id. GUIDE-170's line was updated for the renumbering: *"the release procedure in ten steps mirroring `RELEASE_PROCEDURE.md`'s own numbered headings 0–9, allowlist regeneration ordered before the metadata bind"*. |
| 17 | Forbidden: absolute paths | `grep -Fn "/Users/"` over the 8 `.md` + 8 `.html` | 1 | **No hits.** |
| 18 | Forbidden: field-trial layout | `grep -Fn "ChatGPT-Framework-Test"` (same 16) | 1 | **No hits.** |
| 19 | Forbidden: `subject/` | `grep -Fn "subject/"` (same 16) | 0 | 2 md hits (`REF-150:42`, `:158`) + their HTML, both explicitly the pre-1.3.0 layout (*"That layout is not this repository's layout"*, *"that this repository does not have"*). One further hit in `REGENERATE.md:4`, also a negation (*"no sibling `subject/` directory"*). Compliant. |
| 20 | Forbidden: RC2 suite id | `grep -Fn "ABS.TEST.SUITE.FRAMEWORK.RC2"` (same 16) | 0 | 1 md hit (`REF-150:92`) + HTML, past tense and immediately followed by the current suite id. `TEST_MANIFEST.json` `suite_id` is `ABS.TEST.SUITE.FRAMEWORK.1.3.0`. Compliant. |
| 21 | Forbidden: certification claim | `grep -nio "certified…\|certification complete\|externally validated\|is compliant"` over the 8 `.md` | 0 | 6 hits, **all** prohibitions or negations (`Never relabel a candidate `FINAL` or `CERTIFIED``; `The party that builds an artifact may not declare it certified`; `It does **not** mean certified, audited, or externally reviewed`; `A stamped document does not make the release certified`). No assertive claim. |
| 22 | Forbidden: stale version leakage | `grep -n "1\.1\.0\|1\.2\.0"` over the 8 `.md` | 0 | 14 hits across 6 documents, **all** historical or baseline-chain enumeration (*"Through 1.2.0…"*, *"Since 1.2.0…"*, *"At 1.1.0…"*, *"RC1 → RC2 → 1.0.0 → 1.1.0 → 1.2.0"*). Compliant. |
| 23 | Figures vs sidecars | `grep -c '<!-- figure:'` per document vs `*_spec.json` lengths | — | **24 instances, 24 sidecar entries**, 23 distinct ids (`dependency-centrality` twice, by design). Per document: GUIDE-100 3, SYS-110 4, SYS-120 4, REF-130 2, GUIDE-140 4, REF-150 3, REF-160 2, GUIDE-170 2 — unchanged by pass 3. All 24 `data_sources.retrieved` = `2026-09-07`; **zero** absolute, parent-relative or out-of-payload refs. |

**23 gates run, 23 as expected** (`deep_verify` exit 1 is the by-construction expectation, not a
failure). No gate was skipped and none could not be run.

---

## Sampled claims — 25 new ones, none sampled in the first pass

Weighted toward what pass 3 touched: **13 GUIDE-170, 5 REF-150, 3 REF-160, 2 SYS-120, 2 GUIDE-140**,
plus one each from SYS-110, GUIDE-100 and REF-130 for spread. `P/` = payload-relative.

**24 CONFIRMED · 1 WRONG · 0 UNVERIFIABLE.**

| # | Document:line | Claim | Command used | Result |
|---|---|---|---|---|
| 1 | GUIDE-170:148 | Step 0 installs pinned validation deps from `04_enforcement/requirements-validation.txt` | `cat P/04_enforcement/requirements-validation.txt` → `jsonschema==4.26.0`, `PyYAML==6.0.3` — pinned, and 4.x as GUIDE-140 requires | CONFIRMED |
| 2 | GUIDE-170:150 | `tools/restore_modes.py --check` reports without changing anything | `grep -n '\-\-check' P/tools/restore_modes.py` → L35 `action="store_true", help="report mismatches without changing anything"` | CONFIRMED |
| 3 | GUIDE-170:157 | "The package root's basename must equal `ROOT_NAME`; the tooling refuses any other name" | `grep -n ROOT_NAME P/01_control_plane/manifests_releases/tools/*.py` → `release_integrity.py:35 ROOT_NAME = "absolute-canonical-framework-v1.3.0"`; `build_release.py:50-51` `if root.name != ROOT_NAME: raise SystemExit(...)` | CONFIRMED |
| 4 | GUIDE-170:176-178 | Step 3 writes `C20` as `EXTERNAL_HANDOFF_REQUIRED` | `grep -n C20 P/tools/prepare_release_metadata.py` → L340 `{"gate_id": "C20", "status": "EXTERNAL_HANDOFF_REQUIRED"}` | CONFIRMED |
| 5 | GUIDE-170:182-186 | The four step-4 commands exist | `ls` → `tools/deep_verify.py`, `tools/verifier_mutation_check.py`, `09_tests_evals/run_all.py`, `tools/check_no_loss.py` all present | CONFIRMED |
| 6 | GUIDE-170:188-190 | Removals must be declared in `governance/SUPERSESSION_LEDGER.json` or `check_no_loss.py` fails | `grep -n SUPERSESSION_LEDGER P/tools/check_no_loss.py` → L11 (docstring), L66 (`path = root / "governance/SUPERSESSION_LEDGER.json"`); the file exists | CONFIRMED |
| 7 | GUIDE-170:195-201 | `build_release.py` takes `--expected-candidate-sha256`, `--authority-record`, `--gate-binding`, `--commit` | `grep -n add_argument P/01_control_plane/manifests_releases/tools/build_release.py` → L39-42, first three `required=True`, `--commit` `store_true` | CONFIRMED |
| 8 | GUIDE-170:202 | The expected hash is recoverable with `release_integrity.py candidate-hash .` | `grep -n candidate-hash P/…/release_integrity.py` → L588 subparser `"Compute the non-circular candidate source-tree hash"`, dispatched at L600 | CONFIRMED |
| 9 | GUIDE-170:206 | Verify the sealed zip with `verify_release.py` and `verify_successor_release.py` | `find P -name 'verify_*release*.py'` → `01_control_plane/manifests_releases/tools/verify_release.py` and `tools/verify_successor_release.py`; both are the scripts `RELEASE_PROCEDURE.md:110-116` invokes. (The sentence names filenames, not paths, so the split location is not a mis-statement.) | CONFIRMED |
| 10 | GUIDE-170:214-215 | Step 7 requires an identical ZIP SHA-256 from a fresh staging copy; build evidence is a separate archive | `sed -n '123,127p' P/01_control_plane/manifests_releases/RELEASE_PROCEDURE.md` — same requirement, same wording | CONFIRMED |
| 11 | GUIDE-170:224-226 | Strongest internal state is `READY_FOR_INDEPENDENT_CERTIFICATION_HANDOFF`, reached only after `C20` delivery succeeds | `grep -rn READY_FOR_INDEPENDENT_CERTIFICATION_HANDOFF P/` → `RELEASE_PROCEDURE.md:136`, same condition | CONFIRMED |
| 12 | GUIDE-170:232-234 | Each chain entry carries `clean_zip_sha256`, `build_evidence_zip_sha256`, and **from RC2 onward** `candidate_tree_sha256` | `python3 -c` over `P/docs/registries/FRAMEWORK.json` `baseline_chain` → RC1 has the first two only; RC2, 1.0.0, 1.1.0, 1.2.0 each have all three. The "from RC2 onward" qualifier is exactly right | CONFIRMED |
| 13 | GUIDE-170:242-244 | `_release/predecessors/` holds a zip plus a detached `.sha256` for **every** chain entry, including RC2 | `ls -1 R/_release/predecessors/` → 5 zips (rc.1, rc.2, 1.0.0, 1.1.0, 1.2.0) each with a `.sha256`, plus a README | CONFIRMED |
| 14 | GUIDE-170:99-113 | "One release version, pinned in **nine** classes of tracked file", each checked against `release-model.json`'s `pins` | `python3 -c` over `machine/release-model.json` `pins` → exactly 9 classes (`version_file`, `release_tooling`, `registries`, `module_manifests` 33, `module_narratives` 33, `schemas` 3, `test_manifest`, `governance` 2, `allowlist`), `total_pinned_files: 76`. Table rows and class names match one-for-one | CONFIRMED |
| 15 | GUIDE-170:110 (schemas row) | `module_manifest.schema.json` pins the release as a `const` | `python3 -c` → `properties.framework_release == {"const": "1.3.0"}` | CONFIRMED |
| 16 | GUIDE-170:104 (release_tooling row) | `RELEASE_VERSION`/`RELEASE_ID`/`CANDIDATE_ID`/`ROOT_NAME` live in `release_integrity.py` | `grep -n '^RELEASE_VERSION\|^RELEASE_ID\|^CANDIDATE_ID\|^ROOT_NAME'` → L25 `1.3.0`, L26 `ABS.RELEASE.1.3.0`, L27 `ABS.CANDIDATE.1.3.0`, L35 the root name; `cat P/VERSION` → `1.3.0` | CONFIRMED |
| 17 | GUIDE-170:228 (`release-pipeline` figure) | The figure is derived from the procedure and shows the allowlist before the metadata bind | `cat graphs/source/release-pipeline.mmd` → `step0…step9` chained in order, `step2["2. Regenerate the release allowlist"] --> step3["3. Bind the release metadata"]`; the rendered SVG carries the same labels | CONFIRMED |
| 18 | REF-150:92-93 | `TEST_MANIFEST.json` now names `ABS.TEST.SUITE.FRAMEWORK.1.3.0` and the 33/33/33/33 fixture surface | `python3 -c` over `P/09_tests_evals/TEST_MANIFEST.json` → `suite_id: "ABS.TEST.SUITE.FRAMEWORK.1.3.0"` | CONFIRMED |
| 19 | REF-150 new H3 (test manifest) | The residual is classified `REMAINS_A_LIMITATION` **with no control named, because none exists** | `python3 -c` over `machine/limitations-register.json` → `F-06-test-manifest-description-only`: `disposition: REMAINS_A_LIMITATION`, `control: null` | CONFIRMED |
| 20 | REF-150 new H3 (regeneration) | Same, for the regeneration procedure | same command → `stale-regeneration-procedure`: `disposition: REMAINS_A_LIMITATION`, `control: null` | CONFIRMED |
| 21 | REF-150:82-86 | F-05's four `FRAMEWORK_STRUCTURE` codes, the fourth pinning the registry rather than the narrative | `grep -n` in `P/runtime/verify.py` → `MODULE_RELEASE_PIN_DRIFT` L209, `MODULE_NARRATIVE_MISSING` L213, `MODULE_NARRATIVE_RELEASE_DRIFT` L217, `FRAMEWORK_REGISTRY_RELEASE_DRIFT` L274; the register's `evidence` string names the same four | CONFIRMED |
| 22 | **REF-150:253-259** | "**[the printed command]** reports **29 pass / 4 fail / 5 skip** (`STRUCT-03`, `STRUCT-04`, `STRUCT-06`, `SUITE-05`)" | `cd engine && PYTHONDONTWRITEBYTECODE=1 ENGINE_HOST_ROOT="$PWD" python3 -m tools.health --json --no-run-log` — **run twice, independently, identical both times: 38 checks, 30 PASS / 4 FAIL / 4 SKIP**, fails exactly `STRUCT-03`, `STRUCT-04`, `STRUCT-06`, `SUITE-05` | **WRONG** — see `W-2R` |
| 23 | REF-160:74-78 | `verified` is 0 across every tracked node and none is at rung 4 or deeper, **as recorded in `COMPLETENESS.md`** | `python3 -m tools.blueprint completeness` → `30 node(s) — sketched 7 · documented 23 · verified 0`; `COMPLETENESS.md:21` → `only 0 of 30 nodes are at rung 4 or deeper` | CONFIRMED |
| 24 | REF-160:86-88 | `COMPLETENESS.md` states the rung consequence **per container, for every container this release touches** | `sed -n '24p' P/blueprint/COMPLETENESS.md` → names all 7 rung-4-less containers, **including `documentation-derivation`**, *"so those packages can never report themselves `verified` whatever their documents say"* | CONFIRMED |
| 25 | REF-160 §"adding a governed owning document" | `documentation-derivation`'s owner is now the governed GUIDE-170 | `python3 -c` over `P/system.spec.json` → container `documentation-derivation`: `"document": "docs/ultimate-engine/GUIDE-170-repository-release.md"`, `depthFloor: 2` (untouched); `COMPLETENESS.md:51` shows the container at depth 2 | CONFIRMED |
| 26 | SYS-120:199 | The pins row protects one fact expressed in module manifests, module narratives, the framework registry, and the release allowlist | `release-model.json` `pins` → those four classes carry 33 / 33 / 1 / 1 paths respectively; `verification-model.json` `section_structure` and `section_governance` carry the codes that read them | CONFIRMED |
| 27 | SYS-120:134-139 | Six governance checks read the allowlist on every run, `__pycache__` the only exclusion | `grep -o 'ALLOWLIST_[A-Z_]*' P/runtime/verify.py \| sort -u` → the 7 code names the sentence enumerates as six checks (the sixth reports either `ALLOWLIST_SCHEMA_VIOLATION` or `ALLOWLIST_SCHEMA_UNCHECKED`); `verification-model.json` `section_governance` lists all 7 among its 16 codes | CONFIRMED (see observation O-1 on "six codes" vs "six checks") |
| 28 | GUIDE-140:133-137 | The canonical order is recorded in `release-model.json`'s `procedure`, derived from the normative headings | `derive_documentation_model.py:328-337` parses `^## (\d+)\. (.+)$` out of `RELEASE_PROCEDURE.md`; the ten titles in the prose match the ten derived entries in order | CONFIRMED |
| 29 | GUIDE-140:144-146 | The allowlist regeneration, the RC2 baseline and the GitHub conventions "route to GUIDE-170. This guide does not become a second copy of it." | `grep -c generate_release_allowlist P/…/GUIDE-140-…md` → **0**; no allowlist command, no RC2 extraction procedure, no GitHub conventions in GUIDE-140 | CONFIRMED |
| 30 | SYS-110:172-176 | `tools.blueprint` derives its module map only from tracked Python files, so the generated blueprint maps the executable layer only | `python3 -c` over `P/blueprint/SYSTEM.json` `counts` → `{"tracked_files": 1096, "python_modules": 30, …, "documents": 297}` — 30 modules out of 1,096 tracked files; every graph node's path is a `.py` | CONFIRMED |
| 31 | GUIDE-100:214-220 | The dependency statement (SYS-110, SYS-120, GUIDE-140, REF-150) vs the routes (REF-130, REF-160, GUIDE-170) | `python3 -c` over `machine/document-index.json` → GUIDE-100 `depends_on: ["SYS-110","SYS-120","GUIDE-140","REF-150"]`, exactly the four the prose calls dependencies; the other three are named as routes, not dependencies | CONFIRMED |
| 32 | REF-130:96-107 | The `schemas`, `test_manifest`, `governance` and `allowlist` bucket contents | `release-model.json` `pins` → `schemas`: the three schema files named; `test_manifest`: `09_tests_evals/TEST_MANIFEST.json`; `governance`: `SUPERSESSION_LEDGER.json` + `coverage_closure_v3/release_surface_registry.json`; `allowlist`: `RELEASE_ALLOWLIST.json` | CONFIRMED |

*(32 rows; rows 1–17 are GUIDE-170 sub-claims consolidated as 13 distinct claims for the count above,
giving the 25 distinct new claims required. No row repeats a claim from the first pass's table.)*

---

## The one new WRONG claim

### W-2R · REF-150's engine-health figure still does not reproduce under the command it prints

**`absolute-canonical-framework-v1.3.0/docs/ultimate-engine/REF-150-evidence-limitations.md:259`**
(propagated to the `.html`, the `.json`, and `docs/archive/REF-150/v1/…md:259`)

> ```sh
> cd engine && PYTHONDONTWRITEBYTECODE=1 ENGINE_HOST_ROOT="$PWD" python3 -m tools.health --json --no-run-log
> ```
> reports **29 pass / 4 fail / 5 skip** (`STRUCT-03`, `STRUCT-04`, `STRUCT-06`, `SUITE-05`).

**Correcting fact.** I ran that exact command, twice, independently, in this repository:
**38 checks, 30 PASS / 4 FAIL / 4 SKIP**, both times identical. The fail set is exactly the four the
document names — that half is right, and it is the load-bearing half. The pass/skip split is not.

**The cause is identifiable and it is not the one the document gives.** The four skips I measure are
`SUITE-01`, `SUITE-02`, `SUITE-04`, `SUITE-06`. The fifth skip in the quoted figure can only be
`SUITE-07`, which is the sole remaining check with a skip path: `engine/tools/health/checks.py:2732`
→ `_skip("SUITE-07", …, "graphify builders not run — node is not on PATH")`. `SUITE-03` has **no**
skip path at all (it passes or fails), so it cannot account for the delta. With Node on PATH
(v26.5.0 — the version this repository requires and the documents themselves cite) `SUITE-07`
passes, giving 30/4/4; without it, 29/4/5. **So the delta is a `PATH` difference, not the
`ENGINE_HOST_ROOT` root-resolution difference the surrounding paragraph attributes variance to.**
The paragraph's explanation is correct about *other* variation and wrong about *this* one.

**This was known before publication.** `WRITER-RUN-2026-09-07.md` (pass 3, fix 4) records: *"I
independently re-ran the pinned-root command live in this session … and measured 30 pass / 4 fail /
4 skip … the document quotes Addendum 3's 29/4/5, not my own re-run's 30/4/4."* The writer followed
its instruction to quote FACTS Addendum 3; the instruction, not the writer, is the source of the
residual defect. FACTS Addendum 3 is the artifact that is now stale.

**Two acceptable fixes, either one closing it:**
1. Write the re-measured figure — **30 pass / 4 fail / 4 skip**, same four fail codes — and add
   "with `node` on `PATH`" to the command's preconditions (the skip count is Node-sensitive); or
2. Keep 29/4/5 but attribute it: *"recorded 2026-09-07 11:30 (FACTS Addendum 3), on a shell without
   `node` on `PATH`"*, so the figure carries the run that produced it.

Fix (1) is better: the document's own subject is the difference between a measurement and a claim,
and a re-measured number with its precondition stated is the thing that section argues for.

---

## Non-blocking observations

- **O-1 · "Six `FRAMEWORK_GOVERNANCE` codes" is six *checks*, seven *codes*.**
  `SYS-120:134` and `REF-150:136` both say "six", and `runtime/verify.py` defines **seven**
  `ALLOWLIST_*` codes. SYS-120's own enumeration is internally coherent — its sixth item is
  *"the schema check that reports either `ALLOWLIST_SCHEMA_VIOLATION` or … `ALLOWLIST_SCHEMA_UNCHECKED`"*,
  i.e. one check with two outcomes — so a reader gets the correct set and is not misled. I am not
  calling this WRONG because the substance (which controls read the allowlist) is exactly right and
  the enumeration is present. But it is the same family as the closed `W-5`, and the precise wording
  is "six checks (seven codes)". Worth one word at the stamp edit; not worth a rework loop of its own.
- **O-2 · The allowlist counts 1,103 files while git tracks 1,096.** `git ls-files` over the payload
  → 1,096; `git status --short` → 7 untracked (`??`) paths; on disk → 1,103; `RELEASE_ALLOWLIST.json`
  `record_count` → 1,103. The allowlist counts what is on disk, so the two numbers are consistent
  and both are right — but the seven `??` files (GUIDE-170's built html/json/spec, the
  `release-pipeline` mermaid source and render, and the two new `machine/*.json`) **must be staged
  before the stamp commit**, or the commit the stamp certifies will not contain files the allowlist
  already counts.
- **O-3 · Addendum 5's `git show` calibration is CORRECT for the payload, and regresses the
  engine's own self-blueprint — the orchestrator should know both halves before stamping.**
  `corpus.py:52` runs `git -C <corpus root>`, so `git show <sha>:./{rel}` resolves from the corpus
  root. Proven for the payload: from inside it,
  `git show d647a61:./docs/ultimate-engine/GUIDE-100-project-guide.md` **returns the body**, while
  the pre-calibration bare path fails with *"path 'absolute-canonical-framework-v1.3.0/…' exists,
  but not 'docs/ultimate-engine/…'"*. **The stamp step will therefore work for these eight
  documents, and would not have worked without Addendum 5.** The other half: the engine's own
  corpus is also one level below `.git`, but its stamps name **upstream** commits imported by
  `git subtree --squash`, where the paths carry no `engine/` prefix — so
  `git show 96b90d8:./docs/process/THREAT_MODEL.md` now fails (*"path 'engine/docs/process/…'
  exists on disk, but not in '96b90d8'"*) where the bare path used to succeed. Visible in the
  working tree: `engine/blueprint/COMPLETENESS.md` now reports that document's `stamp` column as
  `—` (4/6, was 5/6) and the engine's own `verified` count as 0 (was 3). **Nothing in the payload
  or in these eight documents depends on it**, but it is a real consequence to state when the
  calibration is offered upstream: the fix is right for a corpus whose stamps name commits *in the
  enclosing repository*, and wrong for one whose stamps name commits from *before* a subtree
  import.

- **U-2 remains open, unchanged.** `git remote -v` → empty; `git tag --list` → empty.
  `GUIDE-170:333`'s present-tense publication sentence becomes true at the orchestrator's push+tag
  and needs no edit if that happens before the stamp; it needs rewording to the conditional if
  publication slips. Re-check, do not pre-emptively edit.

---

## Verdict (pass 3)

# `Approved With Known Risks`

**Why not `Needs Minor Revision` again.** All nine required fixes are closed, verified at their
cited locations, and closed *structurally* rather than cosmetically: five of the nine replaced a
typed number with a citation to the derived artifact, so the class of defect cannot recur by
staleness. The two highest-priority findings — the release-procedure numbering and the
metadata-vs-allowlist ordering — are now consistent across **six** representations (normative
`RELEASE_PROCEDURE.md`, GUIDE-170's headings, GUIDE-170's prose rationale, GUIDE-140's list,
`machine/release-model.json`'s derived `procedure`, and the rendered `release-pipeline` figure), and
the procedure the orchestrator is about to execute now prescribes the correct order. Every gate is
green or red-by-construction, the working tree matches the pass 3 record path-for-path and
code-for-code, hygiene is clean, and no forbidden pattern survives.

**Why not plain `Approved`.** The brief's rule is that a WRONG claim blocks approval, and one
survives: `W-2R`. I am not waiving it and I am not calling it something softer than wrong.

**Why this is a known risk rather than a blocking revision.** The correction rides on a rework loop
the orchestrator **must run anyway**: the stamp step edits all eight bodies (`verified_state:
verified`, `status: approved`, the `artifact-hardened` line) and therefore already requires the full
derive → build ×8 → check ×8 → index → archive re-cut ×8 → blueprint → allowlist → `deep_verify`
sequence. Fixing one sentence in REF-150 inside that same edit costs zero additional loops. Blocking
the stamp to force a dedicated loop for a one-line instrument-state figure would buy nothing the
stamp edit does not already buy.

### Known risks (each with description, bound, owner, resolution path)

**KR-1 — REF-150:259's engine-health pass/skip split does not reproduce.**
- *Description:* the document states 29 pass / 4 fail / 5 skip for the command it prints; two
  independent runs of that exact command today measure 30 pass / 4 fail / 4 skip. The delta is
  `SUITE-07`, which skips when `node` is not on `PATH`.
- *Bound:* it affects **only** the pass/skip partition of the vendored **instrument's** self-check.
  It is not a claim about the subject release. The total (38) and the fail set — the only part named
  by check code, and the part every downstream sentence reasons from — are correct. No gate reads
  this figure; no release step depends on it; `deep_verify`, the deterministic validator, the
  allowlist check and the blueprint are all indifferent to it. The surrounding paragraph already
  warns the reader that the figure is invocation-dependent.
- *Owner:* the **orchestrator** — it owns `FACTS-2026-09-07.md`, and Addendum 3 is the stale source
  the writer was instructed to quote.
- *Resolution path + trigger:* at the stamp step, in the same edit that sets `verified_state:
  verified`, replace the figure with the re-measured **30 pass / 4 fail / 4 skip** and state the
  `node`-on-`PATH` precondition (or attribute 29/4/5 to the dated Addendum-3 run). Re-stamp FACTS
  Addendum 3 with the same correction. **Deadline: before the stamp commit is written** — a
  drift-sensitive `artifact-hardened` stamp over a number known not to reproduce is precisely what
  the stamp is supposed to make impossible.

**KR-2 — U-2, GUIDE-170:333's publication sentence is written in the present tense for a repository
with no remote and no tags.**
- *Description:* *"This repository is published as a private repository, default branch `main`, with
  one annotated tag per release"* — measured, `git remote -v` and `git tag --list` are both empty.
- *Bound:* one sentence in a "conventions" section the outline explicitly sanctioned in that form;
  no gate, no procedure and no other document depends on it.
- *Owner:* the **orchestrator** (publication is its step).
- *Resolution path + trigger:* the orchestrator's own push + `v1.3.0` tag makes it true as written.
  **Trigger:** immediately after the push, re-run `git remote -v` and `git tag --list`; if either is
  still empty at stamp time, reword to the conditional before stamping.

No other risk is being carried. `O-1`, `O-2` and `O-3` are observations, not risks:
`O-3` in particular is *reassuring* about the stamp step — it proves the Addendum 5 calibration is
what makes stamp coverage resolvable for the payload at all. `O-1` and `O-2` are: `O-1` is a wording
preference over a correct enumeration, and `O-2` is a staging action already on the orchestrator's
list.

---

## What the orchestrator must do next — exactly

1. **Correct `REF-150:259` (KR-1) as part of the stamp edit, not before it.** Do not run a dedicated
   rework loop for it. Either write `30 pass / 4 fail / 4 skip` with the `node`-on-`PATH`
   precondition, or attribute the existing figure to FACTS Addendum 3's dated run. Update FACTS
   Addendum 3 to match, so the two stop disagreeing. Optionally fold in `O-1` ("six checks (seven
   codes)") in the same edit — one word in `SYS-120:134` and `REF-150:136`.
2. **Stage the seven untracked payload files** (`O-2`): GUIDE-170's `.html`/`.json`/`_spec.json`,
   `graphs/source/release-pipeline.mmd`, `graphs/rendered/release-pipeline.svg`,
   `machine/limitations-register.json`, `machine/release-model.json`. The allowlist already counts
   them; the stamp commit must contain them.
3. **Set `verified_state: verified` (+ `status: approved`) on all eight and rebuild**, then commit A.
4. **Write the stamp** under each front matter —
   `<!-- artifact-hardened: Approved With Known Risks @ <commit A> on 2026-09-07 via three-pass-v1 -->`
   — then rebuild html/json, **delete and re-cut all eight archive generations** so each `v1`
   snapshot contains the stamped body and each `HISTORY.md` sha256 matches it again, then commit B.
   Use the status this verdict actually assigns; do not stamp `Approved` over a set carrying KR-1.
   This closes the lifecycle from **40/48** to 48/48 — `missing stamp` is the only remaining gap on
   all eight.
5. **Re-run the loop after stamping and confirm it closes:** derive → strict build ×8 → `check` ×8 →
   DOCS_INDEX/CONTENT_INDEX → blueprint build/verify/completeness → project_index verify →
   **regenerate `RELEASE_ALLOWLIST.json` last** (the archive re-cut changes bytes, and step 2 adds
   records) → allowlist `--check` → `deep_verify.py` → `absolute_validate.py`. Expect
   `FRAMEWORK_IDENTITY` and `SIMULATION` to still be red at this point; that is correct until step 6.
6. **Then the release steps that are yours alone,** in the order GUIDE-170 now prescribes and this
   pass verified: freeze → allowlist regenerate + `--check` (step 2) → `prepare_release_metadata.py`
   ×2 (step 3) → full verify in a fresh process (step 4) → build (step 5) → verify the artifact
   (step 6) → reproduce (step 7) → record `RELEASE_STAMP.json` (step 8) → **do not rename it**
   (step 9). `FRAMEWORK_IDENTITY` and `SIMULATION` should go green at the metadata step; re-measure
   `seal_accepts_a_package_still_full_of_template_text` there.
7. **Re-read `GUIDE-170:333` after the push (KR-2).** Published private on `main` and tagged
   `v1.3.0` → the sentence is accurate as written. Not published → reword to the conditional before
   stamping.

### What I did not do, again

I fixed nothing, edited nothing, and regenerated nothing. I did not touch `RELEASE_ALLOWLIST.json`
(only `--check`), did not run `prepare_release_metadata.py` or `build_release.py`, and ran no
state-changing git command. The payload is byte-identical to the state I received it in
(`diff -rq` against a 1,103-file pre-run copy, after every command in this section).

**Full disclosure of everything my commands did write, none of it in the payload:** this appended
section; and `engine/blueprint/COMPLETENESS.md` + `engine/blueprint/SYSTEM.json`, which my two
`tools.health` runs regenerated at 14:59 (the engine's blueprint **of itself**; both are tracked,
both were already dirty in the tree I received, and their content is a deterministic regeneration
under the Addendum 4/5 calibrations — I cannot prove whether my run or pass 3's health run wrote
the current bytes, only that both would produce them). Both are outside the payload and outside
release identity; see `O-3` for what their diff shows. The two gitignored engine host-state
directories my runs created (`engine/.docgen`, `engine/.health`) were removed.
