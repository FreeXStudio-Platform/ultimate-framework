---
id: GUIDE-100
classification: public
title: Absolute Canonical Framework Project Guide
surface: web
audience: technical
owner: framework-documentation
status: approved
export_allowed: true
last_reviewed: 2026-09-07
version: 1
revision: 0
produced_by: Ultimate Engine 1.0.5
verified_state: verified
---
<!-- artifact-hardened: Approved With Known Risks @ 2e0367a07de3 on 2026-10-16 via three-pass-v1 -->

# Absolute Canonical Framework Project Guide

## Purpose and boundary

Absolute is a reusable governance framework plus a Python runtime. It is meant to install into a
separate project, bind work to an approved mission, permit one next lifecycle action, record each
governed mutation in a hash-chained ledger, and refuse completion or release claims that lack
evidence tied to the current tree identity.

The release payload in this repository **is** the framework release, not an installed downstream
project. Its canonical module packages define semantic ownership; its registries connect modules,
requirements, interfaces, profiles, adapters, and concepts; its runtime enforces a project rail;
its verification tools inspect the release and, after installation, the project layered on top of
it.

This release's identity is `ABS.RELEASE.1.3.1`, candidate `ABS.CANDIDATE.1.3.1`, status
`RELEASE_INTERNALLY_VERIFIED_INDEPENDENT_CERTIFICATION_PENDING`.

The release explicitly does not certify itself. Internal verification and external independent
certification are different states. Gate `C20` is `EXTERNAL_HANDOFF_REQUIRED`,
`ABS.CFG.RELEASE.SELF_CERTIFICATION` is fixed to `false`, and no runtime code path turns its own
result into a certification claim.

<!-- figure:domain-operating-model -->

## The operating idea

Authority moves from a builder program into a versioned reusable framework, then from that
framework into a downstream project. Feedback can influence a future framework release; it cannot
silently rewrite the release already governing a project.

The kernel owns the invariants: goal linkage, identity isolation, scoped authority and truth,
lifecycle, evidence, recovery, modularity, and independent verification. The control plane owns
durable state and work records. Capability, knowledge, enforcement, adapter, profile, optional,
test, and runtime layers consume those invariants through stable interfaces and registries.

At runtime, the operator does not choose an arbitrary mutation. `absolute next` derives the single
permitted action from files. Read-only inspection remains available in every state so a blocked
project stays diagnosable.

## Numbered domains

| domain | responsibility | authoritative entry point |
|---|---|---|
| `00_kernel` | Mission, identity, truth, lifecycle, evidence, change, modularity, and fresh verification invariants. | Canonical module packages under the directory and `MODULE_INDEX.json`. |
| `01_control_plane` | Project state, work packets, sessions, decisions, release manifests, and migration. | Package manifests plus release tooling. |
| `02_capabilities` | Minimum-sufficient capability selection, delegation, connectors, and execution routing. | Capability module packages. |
| `03_knowledge_and_documentation` | Canonical packages, representation parity, publication, visuals, graph context, and reconciliation. | Knowledge module packages and graph registries. |
| `04_enforcement` | Schemas, deterministic validators, hooks, security controls, and observability. | Schema directory, validators, and enforcement module packages. |
| `05_platform_adapters` | Host-specific translation isolated from the kernel. | Adapter records and the profile/adapter registry. |
| `06_project_profiles` | Composition overlays for project scale and assurance. | Profile records and the profile/adapter registry. |
| `07_optional_addons` | Measured-need retrieval and operations extensions. | Optional module packages; disabled is a valid default. |
| `08_examples` | Example instances of shared records. | Example JSON; never authority for a real project. |
| `09_tests_evals` | Package, successor, adversarial, mutation, and aggregate test entry points. | `run_all.py` and its test manifest. |
| `10_runtime` | Executable rail, documents, truth ledger, identity binding, verification, and release. | Runtime module package and the `runtime/` Python package. |

The derived, count-bearing form of this table is
[`machine/domain-model.json`](machine/domain-model.json); its values come from Git and the
canonical module/dependency registries rather than prose.

<!-- figure:tracked-artifacts-by-domain -->

## Source of truth

This section states, for each kind of fact this release makes, which artifact is authoritative and
which are derived from it and checked against it. It replaces the earlier "sources of truth" table,
which predated the cross-representation checks and the release allowlist gate and could not
describe either.

### Release identity

**Authoritative:** the single string in `VERSION`, and the constants it must agree with —
`RELEASE_VERSION`, `RELEASE_ID`, `CANDIDATE_ID`, and `ROOT_NAME` in
`01_control_plane/manifests_releases/tools/release_integrity.py`.

**Derived from it:** `MANIFEST.json`, `CANDIDATE_SOURCE_MANIFEST.json`, `SHA256SUMS.txt`,
`.absolute/release/release_identity.json`, `.absolute/release/authority_record.json`, and
`.absolute/release/gate_binding.json` with its `gate_evidence/` records. All six are written
**only** by `tools/prepare_release_metadata.py`; hand-editing any one of them is exactly how a
manifest stops describing its subject.

**Also derived, and checked against `VERSION` on every run:** `docs/registries/FRAMEWORK.json`
(`FRAMEWORK_REGISTRY_RELEASE_DRIFT`) and `RELEASE_ALLOWLIST.json` (`ALLOWLIST_RELEASE_DRIFT`).

The baseline chain is authoritative in `release_integrity.BASELINE_CHAIN` and mirrored in
`FRAMEWORK.json`'s `baseline_chain`: RC1 → RC2 → 1.0.0 → 1.1.0 → 1.2.0, with 1.2.0 the immediate
predecessor (`clean_zip_sha256` `cc2a4438…`, `candidate_tree_sha256` `add66854…`; first eight hex
characters quoted deliberately, not the full digest).

### Module semantics

**Authoritative:** each canonical module package — its `MODULE.md` narrative,
`MODULE_MANIFEST.yaml`, `requirements.json`, `machine/policy.json`, and fixtures.

**Derived / index:** `docs/registries/MODULE_INDEX.json` and `AUTHORITY_DEPENDENCY_DAG.json`. The
index is checked *against the packages*, not the reverse — `MODULE_INDEX_DRIFT` compares the set of
packages to the set of indexed ids.

33 modules, 33 manifests, 33 narratives — derived from the tree, not typed.

**New in 1.3.0:** the narrative and the manifest must both name `VERSION`
(`MODULE_NARRATIVE_RELEASE_DRIFT`, `MODULE_RELEASE_PIN_DRIFT`, `MODULE_NARRATIVE_MISSING`) —
before 1.3.0 nothing compared the two representations of the same fact, and all 33 narratives sat
two releases behind their manifests.

### Requirements and interfaces

**Authoritative:** each package's `requirements.json`. **Derived:** `CANONICAL_REQUIREMENTS.json`,
which `REQUIREMENT_REGISTRY_DRIFT` reconciles against the union of the packages.

Two counts, and they answer different questions: **99** core requirements in the registry; **105**
total once the 6 successor-governance requirements are added. Name both, and name the difference —
a single number here would answer the wrong question for whichever reader needed the other one.

Interfaces: **31**, authoritative in `INTERFACE_INDEX.json`; a manifest may not declare an
interface the index does not know (`MODULE_UNKNOWN_INTERFACE`).

### Verification results

**Authoritative:** the *output* of a run, in a named environment, bound to a tree identity — never
a document's summary of it. `tools/deep_verify.py` derives every result from raw bytes.

The aggregate entry point is `09_tests_evals/run_all.py`; it invokes the deterministic validator,
the successor controls, the deep verifier, the mutation check, and the V2 contract validator. Any
non-zero exit fails the run.

`TEST_MANIFEST.json` is a **description** of that surface, not the surface itself. It was wrong for
two releases precisely because nothing validated it against the registry it summarized — see
[REF-150](REF-150-evidence-limitations.md)'s F-06 record, and note that the description being
correct today does not mean it is checked.

### Documentation

**Authoritative for the framework's own claims:** the payload's root documents and `docs/*.md` —
`README.md`, `CHANGELOG.md`, `RELEASE_NOTES.md`, `LIMITATIONS.md`, `SECURITY.md`,
`docs/ARCHITECTURE.md`, `docs/RUNTIME_GUIDE.md`.

**This set (`docs/ultimate-engine/`) is derived documentation.** It re-expresses the registries, the
runtime constants, and the verifier's own AST. Where it disagrees with a package manifest or a
canonical registry, **the disagreement is a finding against this set**, not against the tree —
[REF-130](REF-130-extension-points.md) states this rule once and it is cited here rather than
restated.

The `machine/*.json` files are this set's machine-readable form and are regenerated, never
hand-edited.

### The two identity systems, and why a hardened stamp is not a release claim

Two identity models exist in this repository and neither substitutes for the other.

**The framework's own identity model** binds *release payload bytes* to a candidate tree SHA-256.
Its subject is the whole tree; its evidence is `MANIFEST.json`, `SHA256SUMS.txt`, and
`.absolute/release/release_identity.json`; its verdict is a gate binding across `C0`–`C20`; its
strongest honest state is `READY_FOR_INDEPENDENT_CERTIFICATION_HANDOFF`, never `CERTIFIED`.

**The documentation engine's identity model** binds *one document body* to *one git commit in this
repository*. Its grammar is
`<!-- artifact-hardened: <STATUS> @ <sha> on <YYYY-MM-DD> via <pass> -->` — a kind, a status
starting uppercase, 7–40 hex characters, an ISO date, and a pass name. `artifact-hardened` is the
only **drift-sensitive** stamp kind: it certifies *this body, at this commit*, so editing the body
after the stamp invalidates it.

A document's header field `verified_state: verified` is the **claim**; the stamp is the
**evidence**. A document claiming `verified` with no content-certifying stamp behind it is a
blocking finding — it would read as verified forever and for free, which is exactly the false-green
shape both identity models exist to refuse.

**Neither system substitutes for the other, in either direction.** A stamped document does not make
the release certified; a verified, sealed release does not make any document `verified`. The
framework's own `C20` stays external regardless of how many documents in this set carry stamps.

The current, honest position: every document in this set carries `verified_state: unverified` and
no stamp, as of this writing.

<!-- figure:authority-of-facts -->

## How someone uses it

1. Verify the framework tree in the intended environment. Graphviz availability is part of that
   environment because visual parity is a real check, not an optional decoration — this release was
   rendered under, and must be verified against, Graphviz **15.1.0 (20260618.0150)**.
2. Choose one profile and one adapter. A profile may make policy stricter; it may not weaken kernel
   invariants. An adapter translates host behavior; it is not a second semantic authority.
3. From the downstream project, run `absolute init` with a non-empty mission. Installation writes
   only the project's `.absolute/` namespace and refuses the framework release tree.
4. Follow `absolute next`. Open bounded work, create and seal governed document packages, record
   evidence, run the gate, close work, checkpoint, perform a non-author second pass, verify, and
   release.
5. Store at least one detached truth anchor somewhere the project-tree writer does not solely
   control. A local hash chain detects local history edits; an external surviving anchor is needed
   to detect a full rewrite from genesis.

Detailed command order is in [SYS-120](SYS-120-runtime-enforcement.md). Installation, profile,
adapter, and verification practice is in [GUIDE-140](GUIDE-140-operations-verification.md).

## Documentation relationships

This guide depends on the architecture map [SYS-110](SYS-110-architecture.md), runtime and
enforcement detail [SYS-120](SYS-120-runtime-enforcement.md), operational guide
[GUIDE-140](GUIDE-140-operations-verification.md), and evidence boundary
[REF-150](REF-150-evidence-limitations.md). Change locations and risk are in
[REF-130](REF-130-extension-points.md). Blueprint-only navigation is in
[REF-160](REF-160-agent-blueprint-guide.md). Repository, versioning, and release operations are in
[GUIDE-170](GUIDE-170-repository-release.md).

## What remains unverified

`CANNOT_VERIFY`: no provider host, remote repository, production project, Notion/Figma surface,
external certifier, or AuditHunt runtime is exercised by this release's package-local suite.

The 2026-09-01 red findings quoted in earlier versions of this document set were measured against
the framework at release 1.1.0, in a layout this repository no longer has. They were resolved in
1.3.0; [REF-150](REF-150-evidence-limitations.md)'s "What 1.3.0 resolved" section is the dated
record of exactly what changed and what control now stops each one recurring.
[REF-150](REF-150-evidence-limitations.md) also carries this release's full standing boundary,
including which limitations are the framework's own and which describe the documentation
instrument's state rather than the subject.
