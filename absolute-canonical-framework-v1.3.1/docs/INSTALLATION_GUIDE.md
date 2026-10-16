# Installation Guide

## New project

```sh
cd /path/to/project
python3 /path/to/absolute-canonical-framework-v1.1.0/absolute \
    init --project <slug> \
         --mission "<what this project is for>" \
         --profile minimal|standard|enterprise|audithunt \
         --adapter chatgpt_codex|claude_code|cursor|generic_api|local_agent
python3 /path/to/absolute-canonical-framework-v1.1.0/absolute next
```

`init` freezes the project identity, resolves the chosen profile and adapter, creates the
`.absolute/` control namespace with its durable registries, writes the genesis ledger entry,
and takes the first anchor. It refuses to run twice, and it refuses an empty mission — the
goal lock would have nothing to bind to.

From there, follow `absolute next` until the rail is complete. Each step is explained in
`docs/RUNTIME_GUIDE.md`.

## Existing project

Do not overwrite current governance. `init` writes only inside `.absolute/` and touches
nothing else, so it is safe to install alongside an existing system, but the reconciliation
work is yours to do:

1. Install into the repository and record the pre-existing baseline as a document
   (`absolute doc new`) whose source evidence names the current governance artifacts.
2. Build an authority and concept crosswalk from the existing system to the framework's
   concepts, as a second document.
3. Record evidence for parity between the two, and run the gate.
4. Migrate stable IDs and links only after that gate passes.
5. Promote in a reversible step, with the rollback stated in the work packet.

`MIGRATION_GUIDE.md` covers moving a project from RC1 or RC2.

## Validation

```sh
python3 tools/restore_modes.py --check       # after any copy that may not preserve permissions
python3 tools/deep_verify.py --project /path/to/project
python3 09_tests_evals/run_all.py
```

Extract the release with a mode-preserving utility, or run `python3 tools/restore_modes.py`
afterwards. `zipfile.extractall()` alone does not restore the executable bit.

## Credentials

Use environment variables or a secret manager. Notion, Figma, repository hosts, MCP, RAG, and
graph systems remain disabled until actual availability, permission, health, data boundary,
need, and rollback are verified. Secret values never enter module state, and
`tools/deep_verify.py` fails the security section on any file matching a credential pattern.
