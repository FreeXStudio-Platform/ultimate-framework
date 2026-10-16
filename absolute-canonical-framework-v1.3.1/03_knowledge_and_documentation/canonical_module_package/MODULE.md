---
module_id: ABS.MODULE.KNOWLEDGE.CANONICAL_MODULE
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Canonical module package and scoped representations
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.CANONICAL_MODULE_PACKAGE`. It answers: **Does this package represent one coherent, testable semantic scope?**
## Normative requirements
- **ABS.REQ.CANONICAL_MODULE_PACKAGE.001 (MUST):** Every material module shall have one bounded semantic scope and coordinated narrative, manifest, requirements, blueprint/visual, machine contracts, tests/evidence, integration, publication, and changelog artifacts where applicable.
- **ABS.REQ.CANONICAL_MODULE_PACKAGE.002 (MUST):** Non-applicable representations shall be recorded as N/A with a reason; empty symmetry artifacts are prohibited.
- **ABS.REQ.CANONICAL_MODULE_PACKAGE.003 (MUST):** A module may be certified only when scope, responsibilities, interfaces, failure/recovery, security, dependencies, parity, tests, links, and independent review meet its contract.
## Operating contract
1. Identify the canonical scope and source evidence.
2. Define or update the narrative meaning.
3. Update applicable machine, blueprint, visual, integration, and test forms.
4. Run parity, link, security, and evidence checks.
5. Publish only governed derivatives and invalidate them on source change.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`DRAFT` → `CANDIDATE` → `VERIFIED` → `CERTIFIED` → `SUPERSEDED`
## Interfaces provided
- `ABS.IFACE.MODULE.PACKAGE` — canonical module package contract
## Interfaces consumed
- `ABS.IFACE.IDENTITY.ALLOCATE` — stable identity and namespace allocation
- `ABS.IFACE.GRAPH.QUERY` — typed graph and context-pack query
## Failure and recovery
Primary failure: **representations become independent truth islands.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
