# Release scripts

Executable forms of procedures whose **normative description lives in the payload** — this directory
never defines a rule, it runs one:

| script | runs | normative source |
|---|---|---|
| `seal.sh` | allowlist regeneration → metadata bind (×3, hash must be stable) → verification in fresh processes → build → artifact verification → clean-room extraction with POSIX modes → reproduction → record | payload `01_control_plane/manifests_releases/RELEASE_PROCEDURE.md`, summarised in `docs/ultimate-engine/GUIDE-170-repository-release.md` |
| `stamp-docs.sh` | the two-commit stamp of the governed documentation set (phase A: the verified claim; commit; phase B: the stamp naming that commit, rebuild, re-cut archive generations, allowlist, guard proof) | `docs/ultimate-engine/GUIDE-100-project-guide.md` §Source of truth; `engine/docs/process/AUTHORING_CONTRACT.md` |

Both scripts locate the repository root with `git rev-parse --show-toplevel` and the payload by its
`absolute-canonical-framework-v*` name, and run every Python step with `PYTHONDONTWRITEBYTECODE=1`.
Environment for the engine steps: `PYTHONPATH=<repo>/engine`, `ENGINE_HOST_ROOT=<payload>`,
`ENGINE_AUTHORED_DOCS_ROOT=docs/ultimate-engine`.

They were used, in this form, to seal and stamp 1.3.0 (`docs/doc-pipeline/`, `RELEASE_STAMP.json`).
The GitHub publication step (repository, tag, release assets) is described in GUIDE-170 and was done
with the GitHub CLI; it is deliberately not scripted here because it needs an operator credential.
