---
id: SYS-110
classification: public
title: Absolute Architecture and Domain Map
surface: repo
audience: agents
owner: framework-documentation
status: approved
export_allowed: true
last_reviewed: 2026-09-07
version: 1
revision: 0
produced_by: Ultimate Engine 1.0.5
verified_state: verified
---

# Absolute Architecture and Domain Map

## Architectural thesis

Absolute separates semantic authority from representations and host execution. Each canonical
module owns one bounded concept and its normative requirements. Narrative, manifest, machine
policy, visual, test, integration, and publication artifacts express that scope; none may silently
become an independent authority.

The canonical dependency graph points from a lower-authority consumer to an earlier-authority
dependency. This direction matters: a control-plane module may consume a kernel invariant, but the
kernel does not become dependent on how the control plane happens to implement it.

<!-- figure:domain-dependencies -->

The complete module-level edge set and both direct and transitive dependency measures are in
[`machine/module-dependencies.json`](machine/module-dependencies.json). The domain aggregation is
in [`machine/domain-model.json`](machine/domain-model.json).

## Repository layout

### What each root entry is

The repository holds four kinds of thing at its root, described here by role rather than by name,
because the name of the release payload changes with every version:

- the **release payload**, `absolute-canonical-framework-v1.3.1/` — the subject of every integrity
  control this document and [SYS-120](SYS-120-runtime-enforcement.md) describe; its basename must
  equal the tooling's `ROOT_NAME`;
- the **vendored instrument**, `engine/` — the documentation and blueprint engine that produced
  this document, not part of this release's identity;
- the **sealed artifacts** — the current release's zip and detached SHA-256, written under
  `_release/` by the procedure and published as GitHub Release assets rather than committed;
- the **repository's own records** — `README.md`, `RELEASE_STAMP.json`, `MANIFEST.sha256`,
  `.gitignore`, and `docs/doc-pipeline/`.

**`.git` is outside the payload, and that is the structural change 1.3.0 makes.**
`release_tree_integrity`'s `FORBIDDEN_PARTS` denylists `.git` by design, so before 1.3.0 no working
tree could pass that control — only a sealed zip, with no version-control metadata inside it,
ever could. Moving `.git` to the repository root, one level above the payload, is what lets a
working tree pass `release_tree_integrity` for the first time.

A second consequence follows from the same move, and it is worth stating plainly: because tree
identity covers everything outside `.absolute/`, a `git commit` inside the payload used to change
the work identity every time it ran. With `.git` outside the payload, an ordinary commit no longer
touches the tree the identity model measures.

<!-- figure:repository-layout -->

### What is source and what is derived

**Source:** module packages, registries, schemas, fixtures, `runtime/`, `tools/`, the root
documents, `system.spec.json`, `PROJECT_INDEX.json`, the `.dot` graph sources, and the authored
bodies of the eight governed documents under `docs/ultimate-engine/`.

**Derived, regenerated, never hand-edited:** the six hash-binding metadata files (`MANIFEST.json`,
`CANDIDATE_SOURCE_MANIFEST.json`, `SHA256SUMS.txt`, and the `.absolute/release/` identity records);
`RELEASE_ALLOWLIST.json`; every `.svg` (rendered from its `.dot`); `blueprint/*`;
`docs/ultimate-engine/machine/*.json` produced by
[`scripts/derive_documentation_model.py`](scripts/derive_documentation_model.py); the
`docs/ultimate-engine/*_spec.json` figure sidecars; the `.html`/`.json` document builds;
`DOCS_INDEX.html`; `docs/design/doc-system/CONTENT_INDEX.json`; and
`graphs/source/*.mmd`, `graphs/rendered/*.svg`, `graphs/structure/*`.

**The rule that follows is not new here.** Editing a generated SVG, global graph, or publication
without changing its canonical source is never a fix — [REF-130](REF-130-extension-points.md)
states this once and this document cross-references it rather than restating it.

`PROJECT_INDEX.json` is the one exception worth naming on its own: it is an **intentionally
maintained registry**, not a filesystem scan, and it is updated with `tools.project_index.cli
register` rather than regenerated wholesale.

## Semantic containers

### Kernel

The kernel provides the framework's non-negotiable invariants. Goal lock connects work to mission.
Identity prevents builder, framework, release, adapter, profile, and project namespaces from
colliding. Authority/truth scopes claims and conflicts. Lifecycle defines promotion and truthful
off-ramps. Evidence gates bind status to a candidate identity. Change/recovery determines what
becomes stale. Modularity governs ownership and interfaces. Independent verification separates a
fresh adversarial review from the builder's own assurance.

### Control plane

The control plane persists the framework's operational memory: project state, bounded work,
session checkpoints, decisions and unknowns, and release/migration artifacts. Its records are not a
second kernel; they are durable instances governed by kernel interfaces.

### Capability and knowledge layers

The capability layer selects the smallest healthy permission-bounded capability set and keeps
provider routing or connectors from expanding authority. The knowledge layer defines one canonical
module package, keeps representations in parity, controls publication, expresses visual contracts,
maintains registries/graphs, and reconciles sources without silent loss.

### Enforcement and tests

The enforcement layer gives requirements executable boundaries: schemas, validators, hooks,
security rules, and fault-seeking health. The tests/evaluations layer supplies positive, negative,
adversarial, recovery, successor, and mutation checks. A test name is not proof; its observed red
and green behavior is. Since 1.2.0 this layer also carries a V2 machine-contract layer under
`governance/coverage_closure_v3/v2_contracts/`, validated by `tools/validate_v2_contracts.py` and
wired into the aggregate suite alongside the deterministic validator, successor controls, the deep
verifier, and the mutation checker.

### Adapters, profiles, optional add-ons, and runtime

Adapters translate host mechanics and remain outside the kernel. Profiles compose required layers
for a project without loosening invariants. Optional add-ons remain disabled until measured need
justifies their cost and data boundary. The runtime executes the lifecycle and emits the two
runtime-owned interfaces for rail decisions and truth stamps.

## Interface topology

The interface registry is provider-independent. A row names one provider module, its consumers,
schema reference, failure rule, and stability. Runtime code reads this registry when validating
governed document packages and emits instances for the interfaces it claims to provide.

The most important interface families are:

- goal, identity, truth, lifecycle, evidence, gate, change, and recovery interfaces from the
  kernel;
- atomic state, work packet, session handoff, decisions, and release assembly from the control
  plane;
- capability selection, delegation, connector invocation, and routing from capabilities;
- canonical package, parity, publication, visual, graph, context, and source admission from
  knowledge;
- schema validation, authorization, test evaluation, health, and dependency registration from
  enforcement and modularity;
- governed execution and truth stamping from the runtime.

Consumers should resolve exact rows from `INTERFACE_INDEX.json`; this document does not duplicate
the registry's version or consumer lists.

## Change risk

Dependency reach is the appropriate first risk proxy for canonical modules: a widely consumed
truth owner can invalidate more downstream artifacts than a large but isolated file. It is not the
whole risk model—security boundary, migration surface, and runtime reachability still matter—but it
answers where impact analysis must start.

<!-- figure:dependency-centrality -->

The chart is derived from graph reachability, not hand-ranked. [REF-130](REF-130-extension-points.md)
turns that reach into concrete change packets.

## Representations are the architecture

This project is primarily a governed representation system, not merely a Python library. Canonical
module packages and registries carry most of the semantic topology. The Python import graph covers
the executable runtime and tools, but it cannot discover modules whose authority lives entirely in
Markdown, YAML, JSON, schemas, fixtures, or visual contracts.

<!-- figure:representation-mix -->

That distinction exposes a standing engine limitation, not a one-time observation: `tools.blueprint`
derives its module map only from tracked Python files, so its generated subject blueprint is an
honest map of the executable layer, never a complete map of the framework. The full domain and
canonical module topology lives in this document's figures and machine JSON, which derive from the
subject's own registries. [REF-160](REF-160-agent-blueprint-guide.md) states what an agent restricted
to the blueprint pack alone cannot answer as a result.

## Runtime module boundaries

The root `absolute` script is the command entry point. `runtime/cli.py` owns command parsing and
presentation; `runtime/rail.py` owns permitted order; `runtime/engine.py` owns governed mutations;
`runtime/project.py` derives installed state and tree identity; `runtime/ledger.py` owns the truth
chain; `runtime/documents.py` and `docvalidate.py` own governed packages; `runtime/verify.py` owns
deep verification; `runtime/util.py` owns shared I/O, hashes, locking, and identifiers.

Release-specific tooling remains under the control plane and `tools/`. The framework refuses to
install project state into its own release tree and refuses to write a release artifact inside the
tree it describes.

## Dependencies

This document depends on [GUIDE-100](GUIDE-100-project-guide.md) for the product boundary and
[REF-130](REF-130-extension-points.md) for change procedure. Runtime order is deliberately kept in
[SYS-120](SYS-120-runtime-enforcement.md) so architecture and operation do not become competing
copies of the same sequence. Repository and release operations that this document only maps are in
[GUIDE-170](GUIDE-170-repository-release.md).
