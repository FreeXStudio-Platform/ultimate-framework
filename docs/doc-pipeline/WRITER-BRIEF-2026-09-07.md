# Writer brief — completing the 1.3.0 documentation set (Sonnet pass)

Inputs, in order: `FACTS-2026-09-07.md` (ground truth, incl. Addendum 1) → `OUTLINES-2026-09-07.md`
(the architect's outline; follow it literally, section by section) → the current documents under
`absolute-canonical-framework-v1.3.0/docs/ultimate-engine/`.

## Non-negotiables

1. Work only inside `absolute-canonical-framework-v1.3.0/` (payload) and `docs/doc-pipeline/`
   (your run record). Do not touch `engine/` source. Do not run `tools/prepare_release_metadata.py`,
   `build_release.py`, or anything under `01_control_plane/manifests_releases/tools/` except the
   allowlist generator at the very end.
2. Every python invocation touching the payload runs with `PYTHONDONTWRITEBYTECODE=1`. Before
   finishing: `find absolute-canonical-framework-v1.3.0 -name __pycache__` must print nothing and
   `git status --short absolute-canonical-framework-v1.3.0` must list only intended files.
3. No absolute local paths, no secrets, no invented numbers in any governed document or sidecar.
   A number in a figure carries a `data_sources` ref; a number in prose names the file or command
   it came from. Present tense only for what exists.
4. No certification language. The framework is internally verified, independent certification
   pending, C20 external.
5. Do not add or remove documents beyond the eight the outline names. Do not rename ids.
6. Regenerate, do not hand-edit, every derived artifact (`machine/*.json` derived fields,
   `*_spec.json` derived figures, HTML/JSON builds, `DOCS_INDEX.html`, `CONTENT_INDEX.json`,
   `blueprint/*`, structure graph, rendered Mermaid, project-index dashboard). Extend
   `scripts/derive_documentation_model.py` when the outline says a value must be derived.
7. Lifecycle steps you own: tag (header), wire (prefix rows exist), date (`last_reviewed:
   2026-09-07`), **version** (`archive cut` for each document, after the body is final),
   **changelog** (append one line per document under the 1.3.0 `### Documentation` heading in the
   payload `CHANGELOG.md`: date, version, file, sections changed). You do NOT stamp; leave
   `verified_state: unverified` and `status: review` — the orchestrator stamps after the Opus
   verification pass. Headers must still carry `version`, `revision`, `produced_by`.
8. Run the regeneration sequence at least twice; the second run must change nothing
   (`git status --short` identical, `git diff --stat` empty after the second run). Derived counts
   include the documents themselves, so one pass is never a fixed point.
9. The allowlist is the LAST payload step: from inside the payload,
   `python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2`
   then the same command with `--check` → `PASS`.

## Acceptance (all must hold; quote the command output in your run record)

- `python3 -m tools.docgen.cli --strict build <doc>.md --formats html,json` → exit 0 for all eight.
- `python3 -m tools.docgen.cli check <doc>.md` → clean for all eight.
- `python3 -m tools.blueprint verify` → clean; `python3 -m tools.blueprint completeness` written.
- `python3 -m tools.project_index.cli verify --scan docs/ultimate-engine` → clean, every
  artifact registered (GUIDE-170 and its figures/graphs included).
- `ENGINE_HOST_ROOT=<payload> python3 -m tools.corpus_check --root <payload> --json` → report the
  result honestly (some guards are engine-portability failures; list which and why, do not
  "fix" the subject to satisfy an engine-shaped guard).
- Deep verifier sections structure, representation, contracts, semantics, security, governance,
  runtime, deterministic validator → PASS via
  `PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py` (identity and simulation remain red
  until the orchestrator's metadata step — quote them, do not hide them).
- `git status --short absolute-canonical-framework-v1.3.0` shows no untracked files except the
  ones the outline introduces (new doc, its sidecar/build outputs, archive cuts, graphs).
- Write `docs/doc-pipeline/WRITER-RUN-2026-09-07.md`: what changed per document, every command
  run with its exit code, every deviation from the outline with the reason, and the exact list
  of files added/removed (the orchestrator needs it for the allowlist and the release step).

## Addendum — run-log hygiene

`tools.corpus_check` writes `<root>/.docgen/corpus_check/runs.jsonl` under the host root. When the
host root is the payload, delete `absolute-canonical-framework-v1.3.0/.docgen/` afterwards (and any
`.health/`, `.docgen_cache.json`, `graphify-out/` the engine leaves there). The tree identity
covers ignored files too; an ignored file is still a file.
