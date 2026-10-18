# Repository changelog

Changes to the **repository** — layout, the vendored instrument, sealed artifacts, pipeline records.
Changes to the framework itself are recorded in the payload's own
`absolute-canonical-framework-vX.Y.Z/CHANGELOG.md`, which is part of every sealed release.

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
