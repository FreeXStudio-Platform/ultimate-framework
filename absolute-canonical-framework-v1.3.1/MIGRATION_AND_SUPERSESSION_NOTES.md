# Migration and Supersession Notes

## Identity relationship

- **Immutable input baseline:** `ABS.RELEASE.1.0.0-RC1`, clean ZIP SHA-256 `0cbe85257f2ad8f2496b4f25de1b1dfbe7576c5031d9be2ec3f9635752672827`.
- **Immutable predecessor releases:** `ABS.RELEASE.1.0.0-RC2`, `ABS.RELEASE.1.0.0` (clean ZIP SHA-256 `cb82186f404c7d088cc4c4b6d3db5cc578adab829ec5014a519965d9431ca55b`), `ABS.RELEASE.1.1.0` (clean ZIP SHA-256 `7568cf7db00f30bd23b35d2e82510f519e7908451764d07738f9b0438d595cdf`), then `ABS.RELEASE.1.2.0` (clean ZIP SHA-256 `cc2a4438fed352a911ee72842ca47e1cc44c054ee06536abb56a30f6ffe51338`, candidate tree `add66854e3b89daa077e6a5dabd9c913385fe39f7a8b0f888e87c0a5e04ca866`).
- **Immediate predecessor:** `ABS.RELEASE.1.3.0` (clean ZIP SHA-256 `37c71be4e6ab5b8c56c8e500894b24481f6289e4566a1b64bce4d125f7fc652f`).
- **Successor candidate:** `ABS.RELEASE.1.3.1` / `ABS.CANDIDATE.1.3.1`.
- Each release supersedes its predecessor only as the proposed active release. Every predecessor archive remains preserved provenance and a rollback baseline; none is rewritten.

## Migration rules

1. Install the successor in shadow mode beside its predecessor; do not rename or overwrite any predecessor archive.
2. Verify the detached RC2 ZIP checksum and run `tools/verify_successor_release.py` before extraction or use.
3. Treat prior paths rooted at `absolute-canonical-framework-v1.0.0-rc.1/`, `-rc.2/`, `-v1.0.0/`, `-v1.1.0/`, `-v1.2.0/` and `-v1.3.0/` as historical baseline locations. Current canonical paths are rooted at `absolute-canonical-framework-v1.3.0/`. The sealed predecessor archives live beside the current one under `_release/predecessors/` in the repository; the repository root, not the payload, carries version-control metadata.
4. Use the canonical C0–C20 gate IDs. Legacy IDs are interpretation-only aliases and must not create duplicate active gates.
5. Promote only after an independent exact-hash certifier returns an allowed certification outcome.

## Rollback

Rollback is exact restoration of a preserved predecessor clean ZIP and its indexes. No migration step is permitted to mutate any of those archives. Note that release rollback is exact archive restoration; the *project* runtime records a rollback statement per work packet but never performs or rehearses it — see `LIMITATIONS.md`.
