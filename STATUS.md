# Status

**Current release: `ABS.RELEASE.1.3.1`** — internally verified; independent exact-hash certification
(gate `C20`) is external and pending. The framework never certifies itself.

## What 1.3.1 is

The public-distribution re-issue of `1.3.0`: framework content unchanged (no semantic removals),
relicensed Apache-2.0 under the FreeXStudio name, personal and host-specific data removed, the
documentation set restamped. `RELEASE_STAMP.json` carries the measured verification record and
`MANIFEST.sha256` the sha256 of every tracked file.

## Known limitations

These are stated, bounded and owned in the payload's `LIMITATIONS.md` and in GUIDE-170/REF-150:

- **Independent certification is pending.** Gate `C20` is an external handoff.
- **Predecessor archives are not distributed.** Their hashes are recorded in `BASELINE_CHAIN`, so a
  clone can *verify* the release; *regenerating* the release allowlist (a maintainer operation) needs
  the checksum-verified RC2 tree. Contributions to the payload reach maintainers with the allowlist
  stale by construction.
- **Visual derivatives are byte-compared under one recorded Graphviz build** (`LIMITATIONS.md`).
- **The vendored engine's own self-tests** are only meaningful from a standalone checkout of the
  engine (REF-150).

## Not planned / candidate

- A failover / degradation / assurance module is recorded as a 1.4 candidate in
  [docs/proposals/FAILOVER_AND_ASSURANCE.md](docs/proposals/FAILOVER_AND_ASSURANCE.md). Nothing is
  scheduled.
