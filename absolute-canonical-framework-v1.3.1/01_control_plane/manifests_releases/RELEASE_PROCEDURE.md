# Deterministic, Gate-Bound Release Procedure

Every step names the command that performs it. A procedure that describes an outcome without
naming the tool that produces it is a trap: the previous revision of this file required six
hash-binding files to exist and never said what writes them.

## 0. Environment

```sh
pip install -r 04_enforcement/requirements-validation.txt   # jsonschema, PyYAML, pinned
apt-get install -y graphviz                                 # or the host equivalent
```

Graphviz is not optional. Without `dot` the deep verifier records `VISUAL_PARITY_NOT_RUN` as a
finding rather than skipping it, so the release can never reach zero findings.

If the tree was copied by anything that does not preserve UNIX permissions — a network share,
a container mount, a restrictive umask — repair the executable surface first. File modes are
not part of the candidate identity, so this cannot change the release hash:

```sh
python3 tools/restore_modes.py --check      # inspect
python3 tools/restore_modes.py              # apply
```

## 1. Freeze the payload

Do not edit the tree after the candidate identity is computed without invalidating all
affected and transitive evidence. The package root directory must be named exactly
`ROOT_NAME` from `01_control_plane/manifests_releases/tools/release_integrity.py`; the tooling
refuses any other name.

## 2. Regenerate the release allowlist

```sh
python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . <extracted RC2 tree>
python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . <extracted RC2 tree> --check
```

`RELEASE_ALLOWLIST.json` declares the **exact** record set of the payload under
`EXACT_RECORD_SET_FAIL_CLOSED`, and the deep verifier's `FRAMEWORK_GOVERNANCE` section compares
that set to the tree on every run. It must therefore be regenerated after the last file is added
to or removed from the payload and **before** the release metadata is bound, because the
allowlist is inside the candidate identity: regenerating it afterwards invalidates the metadata
just written. The anchored baseline is the immutable RC2 clean tree
(`absolute-canonical-framework-v1.0.0-rc.2`, verified against its own checksum ledger and the
chain's `clean_zip_sha256` by the generator); its sealed archive ships beside every other
predecessor. `--check` must print `{"status": "PASS"}` before step 3.

Until 1.3.0 this step did not exist and could not have run: the generator verified the RC2
baseline against `BASELINE_CHAIN[0]`, which is RC1, and the shipped allowlist was the RC3 record
set carried forward unchanged. A control nobody can run is a file, not a control.

## 3. Bind the release metadata

```sh
python3 tools/prepare_release_metadata.py
python3 tools/prepare_release_metadata.py   # run twice — see below
```

This is the only supported way to write the six hash-binding files: `MANIFEST.json`,
`CANDIDATE_SOURCE_MANIFEST.json`, `SHA256SUMS.txt`, `.absolute/release/release_identity.json`,
`.absolute/release/authority_record.json`, and `.absolute/release/gate_binding.json` with its
`gate_evidence/` records.

**Two runs are required from a dirty state.** The gate evidence is derived from a verification
that runs *before* the metadata is rewritten, so the first run after any payload change records
the pre-change state. Confirm the candidate hash is identical across two further runs before
trusting it.

The C0–C20 gate binding is written here. C20 is `EXTERNAL_HANDOFF_REQUIRED` and stays that way:
`ABS.CFG.RELEASE.SELF_CERTIFICATION` is fixed to `false`.

## 4. Verify — all of it, in a fresh process

```sh
python3 tools/deep_verify.py                       # every section, zero findings required
python3 tools/verifier_mutation_check.py           # proves those checks still fire
python3 09_tests_evals/run_all.py                  # runs all of the above plus the validator
python3 tools/check_no_loss.py --predecessor <extracted predecessor tree>
```

`run_all.py` is the single documented entry point and invokes the deterministic validator, the
successor controls, the deep verifier, and the mutation check. Any one of them failing fails
the run.

`check_no_loss.py` proves no module, requirement, interface, concept, profile, adapter, or
governance record was dropped relative to the predecessor. Anything genuinely removed must be
declared in `governance/SUPERSESSION_LEDGER.json` with a reason, or the check fails.

## 5. Build

Every argument is mandatory. Dry-run first:

```sh
python3 01_control_plane/manifests_releases/tools/build_release.py . OUTPUT.zip \
  --expected-candidate-sha256 <64-hex> \
  --authority-record .absolute/release/authority_record.json \
  --gate-binding .absolute/release/gate_binding.json
```

Commit only after the dry run passes, by adding `--commit`.

Recover the expected candidate hash with:

```sh
python3 01_control_plane/manifests_releases/tools/release_integrity.py candidate-hash .
```

## 6. Verify the artifact, not the working tree

```sh
python3 01_control_plane/manifests_releases/tools/verify_release.py OUTPUT.zip --expected-candidate-sha256 <64-hex>
python3 tools/verify_successor_release.py OUTPUT.zip --expected-candidate-sha256 <64-hex>
```

Then extract to a clean directory **preserving file modes** and run `tools/deep_verify.py`
there. `unzip` and `zipfile.extractall()` both drop the executable bit, which fails release
verification; extract applying `(info.external_attr >> 16) & 0xFFFF`, or run
`tools/restore_modes.py` afterwards. The shipped artifact must verify, not merely the tree it
was built from.

## 7. Reproduce

Rebuild from a fresh staging copy and require an identical ZIP SHA-256. Build evidence is a
separate archive; never nest it inside the clean package.

## 8. Record

Record detached hashes, sizes, tool versions, raw reports, limitations, the rollback
reference, and the exact independent-certification status.

## 9. Do not rename it

Never relabel a candidate `FINAL` or `CERTIFIED`. The strongest internal state is
`READY_FOR_INDEPENDENT_CERTIFICATION_HANDOFF` after C20 delivery succeeds. The party that
builds an artifact may not declare it certified.

## Notes

Overwrite is denied by default. An authorized replacement requires `--replace`, a matching
authority record with `allow_replace: true`, and `--rollback-dir`; the builder verifies the
rollback copy before replacement.

Archive file modes are deterministic: the executable-path allowlist is emitted as `0755`,
every other file as `0644`. The verifier rejects mode drift. A new executable entry point must
be added to `EXECUTABLE_PATHS` in `release_integrity.py` or verification will reject it.
