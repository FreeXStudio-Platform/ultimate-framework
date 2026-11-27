# Repository changelog

Changes to the **repository** — layout, the vendored instrument, sealed artifacts, pipeline records.
Changes to the framework itself are recorded in the payload's own
`absolute-canonical-framework-vX.Y.Z/CHANGELOG.md`, which is part of every sealed release.

## 2026-11-27 — beta channel; documents move to Ultimate Engine

- The framework is marked **beta** (README, `STATUS.md`, the GitHub release). 1.3.1 is unchanged; the payload is not
  touched.
- Documents now belong to Ultimate Engine, a stable release from 2.1.0: document types and their writing order, the
  document rules, links between documents and blueprints, and the machine-readable document map. The framework keeps the
  process guardrails. The README no longer tells readers to clone the engine, whose source is private from 2.0.0.
- **Process rules** (`docs/PROCESS_RULES.md`): thirteen guardrails consolidated from the projects that worked by
  the framework — authority and scope, starting from the recorded state, goal lock, bounded packets, gates on evidence,
  independence, converging review, blockers with a way out, bounded runs, close-out, safety, effort and decisions —
  with their rank and the scenarios they were checked against. The payload takes them in the next version.
- `MANIFEST.sha256` regenerated.

## 2026-10-18 — README and artwork

- README rewritten: the problem, the solution, which repository to use (this one already includes the
  Ultimate Engine; engine-only users should clone `ultimate-engine`), a verified step-by-step
  walkthrough, and the verification record.
- Added `assets/` — icon (SVG + 512 px PNG) and a 1280×640 social-preview image.

## 2026-10-17 — maintenance after publication

- All open Dependabot alerts cleared (engine dev tooling: `@modelcontextprotocol/sdk` 1.32.1, `proxy-addr`,
  `ip-address`, `brace-expansion`); `eslint` 10.12.0; `actions/checkout` 7.0.1 and `actions/setup-python`
  7.0.0 (SHA-pinned). `VERSION_LOCK.json` lockfile hashes re-derived. The release payload is unchanged
  (candidate tree `3715764100a5…`).
- `SECURITY.md`: report by email (private vulnerability reporting is not enabled by org policy).
- Dependabot now groups updates and ignores the `zod` major (exact-pinned, needs a compatibility pass).
- `MANIFEST.sha256` regenerated.

## 2026-10-16 — public release 1.3.1

- Repository published as `FreeXStudio-Platform/ultimate-framework` under Apache-2.0, as a fresh
  history rooted at the 1.3.1 tree.
- Payload `absolute-canonical-framework-v1.3.1/` (see its `CHANGELOG.md`): relicense, personal-data
  removal, documentation set restamped, executable modes tracked in git, chain extended to 1.3.0.
- Added community files (`LICENSE`, `NOTICE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`), issue/PR templates, `CODEOWNERS`, Dependabot config and a pull-request
  verification workflow.
- `engine/` is Ultimate Engine 1.0.7, vendored with `git subtree --squash`. One local calibration:
  the blueprint builder's "engine.config.json unreadable" message no longer includes the absolute
  host path of the builder (`engine/tools/blueprint/surfaces.py`).
- Sealed archives are published as release assets and no longer committed (`_release/` is ignored);
  predecessor archives are not distributed — their hashes remain recorded in `BASELINE_CHAIN`.
- Internal operator/agent instruction files and the private knowledge-graph pointer were removed.

## Earlier history

Releases `1.0.0-RC1` through `1.3.0` were developed in a private repository. Their record is the
payload's `CHANGELOG.md`; the release lineage is the `BASELINE_CHAIN` in
`01_control_plane/manifests_releases/tools/release_integrity.py`.
