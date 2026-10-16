# Troubleshooting

## Runtime

- **`absolute next` names an action that keeps failing.** Run the action and read the refusal;
  it names the rule and the permitted action. If the blocked step is `S5`/`S6` and a document
  package cannot be finished or sealed, `absolute doc check --id <slug>` lists exactly what
  blocks it. If it genuinely cannot be fixed, close it on the record:
  `absolute doc abandon --id <slug> --reason "<why>"`. The package stays on disk, the decision
  is stamped into the ledger, and `status`, the pass-2 review, and the release manifest all
  report it. A sealed package cannot be abandoned — supersede it with a new one instead.
- **`doc new` refused for missing `--requirement` / `--failure` / `--source-evidence` /
  `--excludes`.** Each becomes template text that `doc seal` refuses. They are demanded at
  creation because a package that cannot be sealed stops the rail.
- **`doc seal` reports `DOC_UNRESOLVED_MARKER`.** Template text remains. Every `<<TODO: …>>`
  comes from something not supplied at `doc new`; author a replacement package with the
  content supplied, and abandon the incomplete one with a reason.
- **"another absolute process has held the project lock".** A second `absolute` process is
  mutating this project, or one died holding the lock. Mutations are serialized on purpose:
  concurrent writes fork the ledger chain and overwrite records. Wait, or confirm no other
  process is running.
- **`status` prints a `RECOVERY:` line.** A previous run recorded an action and died before its
  state update landed. Nothing is lost and nothing is overwritten — the next identifier is
  allocated past the records already on disk. The line clears after the next successful command.
- **`truth verify` reports `CHAIN_BREAK` or `SEQUENCE_GAP`.** The ledger was edited, or two
  processes wrote concurrently under an older runtime. The chain cannot be repaired without
  destroying the property that makes it worth having. Preserve it, treat every claim after the
  break as unbacked, and re-establish evidence against the current identity in a fresh project.
- **`truth verify` reports `HEAD_MISMATCH`.** The process died between the ledger append and the
  `HEAD` write. The chain itself is intact; `HEAD` is a cache of its last digest.
- **A gate that passed is suddenly `BLOCKED` with `stale`.** The tree identity changed. Evidence
  is bound to the identity it was computed against. Re-run the same method — same `--method`
  string — and the older record becomes *superseded* rather than *stale*. Note that the identity
  covers everything in the project directory, including `.git`, `node_modules`, and other
  derived directories; see `LIMITATIONS.md`.
- **`pass2` refused for authorship.** The reviewer authored material in this candidate. Names are
  compared on a normalized identity, so a different capitalization or spacing is the same person.

## Verification and release

- **`TREE_INTEGRITY_FAIL: release file-mode mismatch`.** The tree was copied by something that
  did not preserve UNIX permissions. Repair with `python3 tools/restore_modes.py`. File modes
  are not part of the candidate identity, so repairing them cannot change the release hash.
- **`TREE_INTEGRITY_FAIL: manifest candidate hash mismatch`.** The payload changed after the
  metadata was bound. Re-run `tools/prepare_release_metadata.py` twice.
- **`VISUAL_PARITY_NOT_RUN`.** Graphviz is absent. Install it. The check is recorded as a finding
  rather than skipped, because a verification that quietly shrinks its own denominator is the
  failure this framework exists to prevent.
- **A tool fails with a confusing denylist error.** A stray `__pycache__` was written into the
  governed tree. Remove it (`find . -name __pycache__ -type d -exec rm -rf {} +`) and ensure any
  ad-hoc script sets `sys.dont_write_bytecode = True` before importing from the tree.
- **`absolute init` refused inside the framework tree.** Correct.
  `ABS.CFG.RELEASE.SOURCE_TREE_MUTATION` is false; project state written into the published
  payload destroys the exact identity it publishes. Run `init` against the project directory.

## Governance

- **Validator fails:** use the first failing check, repair the canonical source rather than the
  generated output, and rerun affected plus transitive checks.
- **Tool unavailable:** mark it unavailable, select an approved fallback, or block only the
  dependent packet.
- **Permission denied:** do not expand permission silently; preserve the denial and request only
  the minimum required grant.
- **State conflict:** stop writes, compare candidate/source hashes and versions, restore the
  latest valid checkpoint, and reconcile explicitly.
- **Generated view drift:** invalidate the derivative, update the canonical scope, regenerate,
  and rerun parity.
- **Release inventory mismatch:** discard staging, rebuild from the allowlist, and reverify
  extraction.
- **Independent verifier unavailable:** keep the release candidate status; do not issue `FINAL`
  or `CERTIFIED`.
