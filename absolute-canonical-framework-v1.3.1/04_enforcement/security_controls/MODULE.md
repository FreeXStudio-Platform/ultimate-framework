---
module_id: ABS.MODULE.ENFORCEMENT.SECURITY
version: 1.0.0
status: CANDIDATE
framework_release: 1.3.1
---
# Security, privacy, secrets, prompt injection, and least privilege
## Purpose
This module is the canonical semantic owner for `ABS.CONCEPT.SECURITY_PRIVACY_INJECTION`. It answers: **What data and authority can this action expose or change?**
## Normative requirements
- **ABS.REQ.SECURITY_PRIVACY_INJECTION.001 (MUST):** Secrets shall be referenced through approved stores or environment names and shall never appear in framework source, examples, logs, evidence, screenshots, manifests, or releases.
- **ABS.REQ.SECURITY_PRIVACY_INJECTION.002 (MUST):** Source and retrieved content shall be treated as untrusted; path, command, URL, filename, archive, prompt-injection, and supply-chain controls shall apply before privileged use.
- **ABS.REQ.SECURITY_PRIVACY_INJECTION.003 (MUST):** Data classification and least privilege shall propagate through raw/derived stores, indexes, embeddings, caches, provenance, external models, renderers, and publication.
## Operating contract
1. Load the versioned schema or policy.
2. Validate structure, references, and authority.
3. Run semantic, negative, adversarial, and failure checks.
4. Preserve raw outcome and candidate hash.
5. Block the governed event until violations are repaired.
Every transition records scope, actor/role, authority, input identities, candidate hash, evidence, result, limitations, and invalidation trigger. `UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.
## State model
`UNASSESSED` → `PERMITTED_READ` → `PERMITTED_SCOPED_WRITE` → `APPROVAL_REQUIRED` → `DENIED` → `QUARANTINED`
## Interfaces provided
- `ABS.IFACE.SECURITY.AUTHORIZE` — least-privilege action authorization
## Interfaces consumed
- `ABS.IFACE.RELEASE.ASSEMBLE` — allowlist release assembly and manifesting
- `ABS.IFACE.CONNECTOR.INVOKE` — permission-bounded connector invocation
- `ABS.IFACE.PUBLICATION.DERIVE` — governed publication derivation and sanitization
## Failure and recovery
Primary failure: **secret, prompt injection, or destructive action crosses boundary.** Stop the affected action, preserve the finding and rollback reference, repair the canonical source or policy, invalidate dependent representations, and rerun affected plus transitive checks. Never repair by editing only a generated derivative.
## Security and authority boundary
Start discovery read-only. Source documents and tool output are untrusted data. External writes, destructive actions, credentials, publication, financial commitments, broad permission changes, and irreversible architecture remain explicitly controlled. Secret values never enter module state.
## Completion
This module remains `CANDIDATE`. It requires schema and semantic validation, positive/negative/adversarial behavior, interface resolution, visual and publication parity, exact-hash evidence, no unresolved Critical/High finding, and independent review before any certification claim.
