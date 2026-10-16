---
module_id: ABS.MODULE.CAPABILITY.ROUTING
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Provider-independent model and execution routing
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.MODEL_ROUTING`. It answers: **Which execution profile satisfies assurance and data boundaries?**
## Normative requirements
- **ABS.REQ.MODEL_ROUTING.001 (MUST):** Kernel routing shall be based on capability, assurance, data sensitivity, irreversibility, context shape, deterministic opportunity, cost, capacity, and health rather than volatile model aliases.
- **ABS.REQ.MODEL_ROUTING.002 (MUST):** Provider/model names, plans, prices, limits, and host behavior shall live in dated replaceable execution profiles and adapters.
- **ABS.REQ.MODEL_ROUTING.003 (MUST):** High-risk synthesis and final verification shall use separated roles/contexts, and routing decisions shall record model/tool/version and evidence boundaries.
## Operating contract
1. Derive the active packet's exact capability needs.
2. Filter by trust, permission, data boundary, health, cost, and fallback.
3. Activate the minimum sufficient set.
4. Execute only the bounded operation.
5. Record actual identity, revoke temporary grants, and review outcome.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`CLASSIFIED` → `ROUTED` → `EXECUTING` → `FALLBACK` → `CHECKPOINTED` → `VERIFIED`
## Interfaces provided
- `ABS.IFACE.MODEL.ROUTE` — provider-independent work routing
## Interfaces consumed
- `ABS.IFACE.CAPABILITY.SELECT` — smallest sufficient capability selection
## Failure and recovery
Primary failure: **routing lowers assurance or violates confidentiality.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
