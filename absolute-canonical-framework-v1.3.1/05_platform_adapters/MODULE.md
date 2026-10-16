---
module_id: ABS.MODULE.ADAPTERS.PLATFORMS
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# ChatGPT/Codex, Claude Code, Cursor, local, and generic adapters
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.PLATFORM_ADAPTERS`. It answers: **How does this host translate the framework without changing authority?**
## Normative requirements
- **ABS.REQ.PLATFORM_ADAPTERS.001 (MUST):** ChatGPT/Codex, Claude Code, Cursor, local-agent, and generic-host adapters shall translate kernel contracts into host-specific files, hooks, permissions, context loading, and commands.
- **ABS.REQ.PLATFORM_ADAPTERS.002 (MUST):** Adapters shall declare required capabilities, limitations, fallbacks, generated artifacts, approval boundaries, and non-authoritative surfaces.
- **ABS.REQ.PLATFORM_ADAPTERS.003 (MUST):** Host-specific behavior shall not contaminate kernel invariants, and adapter compatibility shall be versioned and tested.
## Operating contract
1. Preflight the actual host.
2. Map canonical interfaces without changing semantics.
3. Declare unsupported behavior and fallback.
4. Configure least privilege and durable state.
5. Run conformance, denial, outage, checkpoint, and resume tests.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`UNTESTED` → `PREFLIGHTED` → `CONFIGURED` → `CONFORMANT` → `DEGRADED` → `INCOMPATIBLE`
## Interfaces provided
- None; use package artifacts and shared registries.
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **adapter claims untested host capability.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
