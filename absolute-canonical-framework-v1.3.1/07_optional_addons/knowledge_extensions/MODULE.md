---
module_id: ABS.MODULE.ADDON.KNOWLEDGE
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Optional RAG, vector search, and graph database
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.OPTIONAL_RAG_GRAPH`. It answers: **Has measured retrieval need justified RAG, vectors, or graph infrastructure?**
## Normative requirements
- **ABS.REQ.OPTIONAL_RAG_GRAPH.001 (MUST):** RAG, embeddings, vector indexes, and graph databases shall be optional and adopted only when measured scale, retrieval quality, latency, collaboration, or query complexity justifies them.
- **ABS.REQ.OPTIONAL_RAG_GRAPH.002 (MUST):** Retrieval infrastructure shall record source/version, chunking, embedding/model identity, access classification, tests, rebuild triggers, and provenance.
- **ABS.REQ.OPTIONAL_RAG_GRAPH.003 (MUST):** No derived index or embedding may outrank canonical source, bypass confidentiality, or survive invalidation after incompatible source/model changes.
## Operating contract
1. Measure the problem with the add-on disabled.
2. Define threshold, owner, cost, data, success, and exit.
3. Pilot one bounded add-on.
4. Compare measured benefit and risk.
5. Retain, revise, or remove without losing canonical truth.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`DISABLED` → `PILOT` → `APPROVED` → `ACTIVE` → `STALE` → `DEGRADED` → `REMOVED`
## Interfaces provided
- None; use package artifacts and shared registries.
## Interfaces consumed
- None beyond kernel/package contracts.
## Failure and recovery
Primary failure: **projection outranks canonical source or leaks restricted content.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
