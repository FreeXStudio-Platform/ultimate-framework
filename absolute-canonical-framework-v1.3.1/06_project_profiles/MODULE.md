---
module_id: ABS.MODULE.PROFILES.PROJECT
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Minimal, standard, enterprise, and downstream profiles
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.PROJECT_PROFILES`. It answers: **What is the smallest profile satisfying project scale and risk?**
## Normative requirements
- **ABS.REQ.PROJECT_PROFILES.001 (MUST):** Minimal, standard, and enterprise profiles shall select bounded module, assurance, documentation, capability, and operational requirements without changing kernel invariants.
- **ABS.REQ.PROJECT_PROFILES.002 (MUST):** A project profile shall declare purpose, applicability, required/optional modules, capabilities, permissions, data classification, gates, installation, validation, migration, and uninstall/rollback.
- **ABS.REQ.PROJECT_PROFILES.003 (MUST):** Profiles shall be composable only through explicit precedence and compatibility checks and shall not import Builder Program history.
## Operating contract
1. Classify project scale, domain, risk, and assurance.
2. Select the smallest sufficient module composition.
3. Apply only stricter policy overlays.
4. Install in shadow mode with rollback.
5. Validate project and adapter conformance before activation.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`SELECTED` → `CONFIGURED` → `INSTALLED` → `VALIDATED` → `DEGRADED` → `MIGRATION_REQUIRED`
## Interfaces provided
- None; use package artifacts and shared registries.
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **profile silently weakens a mandatory invariant.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
