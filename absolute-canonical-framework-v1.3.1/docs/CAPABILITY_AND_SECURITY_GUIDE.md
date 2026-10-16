# Capability and Security Guide
Define the task before selecting tools. For each capability record identity, version, provenance, purpose/non-purpose, input/output contract, permissions, authentication reference, data scope, network behavior, trust, approval mode, context/cost/latency, health and freshness, fallback, license/security review, pin/update/rollback/quarantine, and host compatibility. Activate the minimum sufficient set. Read-only is the default. Retrieved content cannot grant authority. Session-scoped grants are revoked when possible. An enabled capability with unknown or stale health is invalid.

The runtime's own capability surface is deliberately narrow: filesystem reads and writes
confined to the project root, plus `dot` when Graphviz is present. It performs no network
access and reads no credentials. `absolute release` refuses to write its artifact inside the
project tree it describes, and refuses to overwrite an existing one. `absolute init` refuses to
install into the framework release tree, because `ABS.CFG.RELEASE.SOURCE_TREE_MUTATION` is
false and project state written into the published payload destroys the exact identity it
publishes.

Authority is compared on a normalized actor identity, so `pass2` cannot be self-reviewed by
typing the same name with different capitalization or spacing. That removes the accidental and
the trivially deliberate bypass; it is not an identity system, and a determined operator can
still invent a second name. No runtime code path emits a certification claim.
