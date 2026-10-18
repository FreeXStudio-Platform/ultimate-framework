<p align="center"><img src="assets/icon.svg" alt="Ultimate Framework" width="112" height="112"></p>

<h1 align="center">Ultimate Framework</h1>

<p align="center"><b>Completion claims that need evidence. Releases you can verify yourself.</b><br>
The Absolute Canonical Framework — governance and a Python runtime that bind project work, evidence,
verification and release to scoped authority and exact identity.</p>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"></a>
  <a href="https://github.com/FreeXStudio-Platform/ultimate-framework/releases/latest"><img alt="Release" src="https://img.shields.io/badge/release-1.3.1-0e8a16.svg"></a>
  <a href="https://github.com/FreeXStudio-Platform/ultimate-framework/actions/workflows/verify.yml"><img alt="verify" src="https://github.com/FreeXStudio-Platform/ultimate-framework/actions/workflows/verify.yml/badge.svg"></a>
  <a href="https://freexstudio.com"><img alt="A FreeXStudio product" src="https://img.shields.io/badge/a%20product%20of-FreeXStudio-black.svg"></a>
</p>

---

## The problem

Any project — and any AI agent working on one — can *say* it is done. Nothing stops a status file,
a changelog or a pull request from claiming "complete", "verified" or "released" with no evidence behind
it, or with evidence for a *different* version of the code. Documents drift from the code they describe,
checks get skipped and reported as passes, and "approved" quietly outlives the thing it approved.

## The solution

Ultimate Framework makes an unsupported claim **impossible to record**:

- **One next action at a time.** The runtime walks a project through a fixed rail (goal → bounded work
  packet → governed documents → evidence → gate → pass-2 review → verification → release) and permits
  only the next legal step.
- **An append-only, hash-chained ledger** records every governed mutation; tampering is evident.
- **Evidence is bound to an exact tree identity.** A completion or release claim is refused unless its
  evidence matches the current tree, byte for byte.
- **Two-pass completion.** Whoever authors a change cannot be its independent reviewer, even by typing
  their name differently.
- **It never certifies itself.** The strongest state it can reach is *internally verified*; independent
  certification (gate `C20`) stays an external handoff by design.

## What you get — and which repository you need

| You want to… | Use | Notes |
|---|---|---|
| Govern a project's work, evidence and releases | **this repository** | Includes everything below. |
| Generate numbered, linked, machine-readable documents, figures and a project **graph** | **this repository** *or* [`ultimate-engine`](https://github.com/FreeXStudio-Platform/ultimate-engine) | The engine is a standalone product. |
| *Only* the engine / graph tooling, nothing else | [`ultimate-engine`](https://github.com/FreeXStudio-Platform/ultimate-engine) | Smaller, and it carries the newest engine release. |

**You do not need to download both.** This repository already contains the Ultimate Engine, vendored in
[`engine/`](engine/) (a pinned snapshot, currently 1.0.7), because the framework uses it to generate and
verify its own documentation. If you only want documents, figures or the graph, skip this repository and
clone `ultimate-engine` on its own.

## Walkthrough: govern your first project

Requirements: Python 3, plus the pinned `jsonschema` and `PyYAML`.

```sh
# 1. Get it
git clone https://github.com/FreeXStudio-Platform/ultimate-framework.git
python3 -m pip install -r ultimate-framework/absolute-canonical-framework-v1.3.1/04_enforcement/requirements-validation.txt
export ABSOLUTE=$PWD/ultimate-framework/absolute-canonical-framework-v1.3.1/absolute

# 2. See the rule of the game (the enforced order, end to end)
python3 $ABSOLUTE explain

# 3. Install it into YOUR project (run this inside your project folder)
cd /path/to/your-project
python3 $ABSOLUTE init --project my-project --mission "Ship a verified v1" --profile standard --adapter claude_code
python3 $ABSOLUTE status            # phase, identity, ledger state, rail progress

# 4. Do exactly what it says is next
python3 $ABSOLUTE next              # -> absolute goal set --id <ABS.GOAL...> --statement "<what done means>"
python3 $ABSOLUTE goal set --id ABS.GOAL.SHIP --statement "v1 ships with evidence"
python3 $ABSOLUTE next              # -> absolute wp new --objective "..." --rollback "how to undo"
```

Keep following `next` — it walks the 13-step rail: bounded work packet → governed documents → evidence →
gate → pass-2 review → deep verification → release. `absolute --help` lists every command. The runtime
installs only a `.absolute/` control folder into your project, makes no network calls, reads no
credentials and refuses to write anywhere outside your project's own tree.

The payload's own guide is the next read: `absolute-canonical-framework-v1.3.1/README.md` →
`LIMITATIONS.md` → `docs/ultimate-engine/GUIDE-100-project-guide.md`.

## Verify before you trust

```sh
cd ultimate-framework/absolute-canonical-framework-v1.3.1
PYTHONDONTWRITEBYTECODE=1 python3 09_tests_evals/run_all.py          # the one entry point
PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py               # every section, zero findings required
PYTHONDONTWRITEBYTECODE=1 python3 tools/verifier_mutation_check.py   # proves the checks still fire
```

At the 1.3.1 seal: 10 sections, 2,903 checks, 0 findings, and the sealed archive rebuilt byte-identically
(see [`RELEASE_STAMP.json`](RELEASE_STAMP.json)). Archives and their SHA-256 are on the
[Releases](https://github.com/FreeXStudio-Platform/ultimate-framework/releases) page. If your copy lost
file modes (some archive tools do), run `python3 tools/restore_modes.py`; a git clone keeps them.

## Repository layout

```
absolute-canonical-framework-v1.3.1/   the release payload — 33 canonical modules, the runtime, the
                                       verifiers and the governed documentation (no .git inside)
engine/                                Ultimate Engine (vendored) — documents, figures, blueprint, graph
docs/doc-pipeline/                     how the documentation set was outlined, written and verified
scripts/release/                       the seal and stamp procedures, as scripts
assets/                                icon and social-preview artwork
RELEASE_STAMP.json · MANIFEST.sha256   what was verified, and how; sha256 of every tracked file
```

The payload sits one level down on purpose: the framework's own integrity model forbids a `.git`
inside the release tree.

## Documentation

Eight governed documents under `absolute-canonical-framework-v1.3.1/docs/ultimate-engine/`, each stamped
with the commit whose body it certifies: **GUIDE-100** project guide (start here) · **SYS-110**
architecture · **SYS-120** runtime enforcement · **REF-130** extension points · **GUIDE-140** operations
and verification · **REF-150** evidence and limitations · **REF-160** agent blueprint guide ·
**GUIDE-170** repository, versioning and release operations.

## Contributing & security

Issues, questions and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). The payload is
hash-bound, so a change to it is cut into a new release by a maintainer (GUIDE-170 explains why). Ask
questions in [Discussions](https://github.com/FreeXStudio-Platform/ultimate-framework/discussions).
Report vulnerabilities privately by email: [SECURITY.md](SECURITY.md). Status and known limits:
[STATUS.md](STATUS.md).

## License

[Apache License 2.0](LICENSE) · Copyright 2026 FreeXStudio — [freexstudio.com](https://freexstudio.com)
