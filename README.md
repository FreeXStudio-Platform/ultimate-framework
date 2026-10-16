# Ultimate Framework

**The Absolute Canonical Framework** — a governance framework and Python runtime that bind project
work, evidence, verification and release to scoped authority and exact identity.

A [FreeXStudio](https://freexstudio.com) product · Apache-2.0 · current release `ABS.RELEASE.1.3.1`

---

## What it is

Most projects can *claim* they are done. This framework makes a claim impossible to record unless the
evidence for it is bound to the exact tree it describes:

- **One next action at a time.** The runtime installs the framework into a project and permits
  exactly one next lifecycle step.
- **An append-only, hash-chained ledger** records every governed mutation.
- **Completion and release claims are refused** when they lack evidence bound to the current tree
  identity.
- **It does not certify itself.** The strongest state it can reach is *internally verified*; gate
  `C20` (independent exact-hash certification) stays an external handoff by design.

## Repository layout

```
absolute-canonical-framework-v1.3.1/   the release payload — 33 canonical module packages, the runtime,
                                       the verifiers and the governed documentation set (no .git inside)
engine/                                Ultimate Engine 1.0.7 (vendored) — the documentation and blueprint
                                       instrument that regenerates the payload's docs
docs/doc-pipeline/                     how the documentation set was outlined, written and verified
scripts/release/                       executable forms of the seal and stamp procedures
RELEASE_STAMP.json · MANIFEST.sha256   what was verified, how; sha256 of every tracked file
```

The payload sits in a subdirectory on purpose: the framework's own integrity model forbids a `.git`
inside the release tree, so the repository root is one level up.

## Quick start

Requirements: Python 3, `jsonschema` 4.x and `PyYAML` (pinned in
`absolute-canonical-framework-v1.3.1/04_enforcement/requirements-validation.txt`).

```sh
git clone https://github.com/FreeXStudio-Platform/ultimate-framework.git
cd ultimate-framework/absolute-canonical-framework-v1.3.1
python3 -m pip install -r 04_enforcement/requirements-validation.txt

python3 absolute explain        # the enforced order, end to end
python3 absolute init --project <slug> --mission "<what done means>" --profile standard --adapter claude_code
```

Read order inside the payload: `README.md` → `LIMITATIONS.md` → `READ_ORDER.md` →
`docs/ultimate-engine/GUIDE-100-project-guide.md`.

## Verify before you trust

```sh
cd absolute-canonical-framework-v1.3.1
PYTHONDONTWRITEBYTECODE=1 python3 09_tests_evals/run_all.py          # the one entry point
PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py               # every section, zero findings required
PYTHONDONTWRITEBYTECODE=1 python3 tools/verifier_mutation_check.py   # proves the checks still fire
```

If your copy lost file modes (some archive tools and network mounts do), run
`python3 tools/restore_modes.py` first; a git clone keeps them.

## Documentation

Eight governed documents live under
`absolute-canonical-framework-v1.3.1/docs/ultimate-engine/`, each stamped with the commit whose body
it certifies:

| Document | Subject |
|---|---|
| GUIDE-100 | Project guide — start here |
| SYS-110 | Architecture |
| SYS-120 | Runtime enforcement |
| REF-130 | Extension points |
| GUIDE-140 | Operations and verification |
| REF-150 | Evidence and limitations |
| REF-160 | Agent blueprint guide |
| GUIDE-170 | Repository, versioning and release operations |

## Releases

Sealed release archives and their detached SHA-256 are published as
[GitHub Release](../../releases) assets — never committed. What each release changed is in
`absolute-canonical-framework-v1.3.1/CHANGELOG.md`; the repository's own changes are in
[CHANGELOG.md](CHANGELOG.md); current state is in [STATUS.md](STATUS.md).

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Because the payload is
hash-bound, a change to it is cut into a new release by a maintainer; GUIDE-170 explains why and how.
Report vulnerabilities privately: [SECURITY.md](SECURITY.md).

## License

Licensed under the [Apache License, Version 2.0](LICENSE). Copyright 2026 FreeXStudio.
