# RC3 Remediation Design

RC3 is a new governed successor, not a rename of RC2. The immutable RC2 inputs remain the rollback baseline. A second-verifier audit found that RC2 preserved the V2 directive but did not bind the 13 preserved V2 machine contracts to actual candidate/evidence records. It also found incomplete conversation-decision, opportunity, configuration, surface, gate, and certification evidence, plus a release builder that claimed allowlist construction without consuming a per-file metadata allowlist.

## Clean-runtime changes

- Preserve all 13 V2 schemas under `04_enforcement/schemas/coverage_closure_v2`.
- Validate the six configuration, fourteen executable-surface, and fifty-two executed-decision compatibility views against actual candidate bytes. The fourteenth surface is the governed allowlist generator added by RC3.
- Compile every schema, run a positive instance for every contract, and prove every required-field deletion is rejected.
- Build from `RELEASE_ALLOWLIST.json` in a fresh staging directory and reject any added, missing, or metadata-incomplete file.
- Give every manifest entry path, bytes, SHA-256, artifact class, source identity, and derivative status.
- Preserve the existing 32 modules and 29 interfaces; no architecture identity is removed.

## Evidence-only changes

Source/archive inventories, knowledge units, frozen and resolved findings, scoreboards, opportunities, projection preflights, simulations, gate reports, and the certification handoff are build-specific evidence. They live outside the clean runtime and are bound by exact hashes in the handoff. Historical projection availability is never copied into current truth; unavailable optional connectors remain `INACTIVE` with `NONE` permission.

## Assurance boundary

Any mutation invalidates the candidate hash and every affected or downstream gate. Builder-scoped Pass A verifies structure, schemas, tests, manifests, and reproducibility. A distinct Pass B performs reverse-completeness and counterexample checks against the frozen bytes. These internal passes may establish a zero-findings release candidate, but only an external verifier can issue `FINAL` or `CERTIFIED` for the named artifact hash.
