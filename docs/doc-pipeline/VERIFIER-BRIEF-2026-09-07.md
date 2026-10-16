# Verifier brief — confirming the 1.3.0 documentation set (Opus pass)

You did not write these documents. Your job is to falsify them. Inputs: `FACTS-2026-09-07.md`
(+ addenda), `OUTLINES-2026-09-07.md`, `WRITER-BRIEF-2026-09-07.md`, `WRITER-RUN-2026-09-07.md`,
and the tree itself. The writer's run record is a claim, not evidence — re-run what it quotes.

## What to check, in order

1. **Outline conformance.** Every section the outline requires exists in final wording; every
   bullet's required fact is present; every EVIDENCE-PENDING item now has evidence or is stated as
   pending in REF-150. List deviations with file:line.
2. **Truth against the tree.** Sample at least 40 concrete claims across the eight documents
   (counts, file paths, check codes, command names, version strings, hashes) and re-derive each
   from the payload with a command. Report each as CONFIRMED / WRONG / UNVERIFIABLE with the
   command used. Any WRONG claim blocks approval.
3. **Derived, not typed.** Every number that the outline said must be derived is produced by
   `scripts/derive_documentation_model.py` (read the script; grep the sidecars for hand-typed
   values that should be derived).
4. **Gates.** Re-run yourself (PYTHONDONTWRITEBYTECODE=1, engine on PYTHONPATH, ENGINE_HOST_ROOT =
   payload): strict docgen build for all eight; `cli check` for all eight; `tools.blueprint
   verify`; `tools.project_index.cli verify --scan docs/ultimate-engine`; the payload's
   `tools/deep_verify.py` (sections other than identity/simulation must PASS — those two stay red
   until the orchestrator's metadata step, and the documents must say so accurately);
   `generate_release_allowlist.py ... --check`. Quote every exit code.
5. **Hygiene.** `find <payload> -name __pycache__` empty; no `.docgen/`, `.health/`,
   `graphify-out/`, run logs inside the payload; `git status --short <payload>` contains only
   the files the writer's run record lists as added/changed.
6. **Forbidden claims.** grep the eight documents and their built HTML for: "certified",
   "certification complete", absolute `/Users/` paths, "will " + present-tense planned work,
   any 1.1.0/1.2.0 reference that is not explicitly historical.
7. **Lifecycle.** For each document: header complete (`version`, `revision`, `produced_by`,
   `verified_state: unverified` at this point); an archive generation exists under
   `docs/archive/<id>/`; a changelog line exists in the payload `CHANGELOG.md`. Run
   `python3 -m tools.blueprint completeness` and quote the lifecycle table.

## Verdict format (write `docs/doc-pipeline/VERIFICATION-2026-09-07.md`)

- One of: `Approved` / `Approved With Known Risks` / `Needs Minor Revision` /
  `Needs Major Revision` / `Rejected / Not Ready`, per the portfolio three-pass contract. Known
  risks need description, bound, owner, and resolution path each, or the verdict is Major.
- A table of every check above with the command, exit code, and result.
- The list of WRONG/UNVERIFIABLE claims with file:line and the correcting fact.
- Exactly what the orchestrator must do next: fixes required (if any), then the stamp step.
You may fix nothing. You report; the writer or the orchestrator fixes.
