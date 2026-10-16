---
id: REF-130
classification: public
title: Absolute Extension Points and Change Risk
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

# Absolute Extension Points and Change Risk

## Rule for every change

Start from semantic ownership, not the nearest convenient file. A change belongs to the one module
that owns the affected concept. Update its canonical representations, then update every registry,
consumer, profile, adapter, test, and derivative reached by the dependency graph. Editing a
generated SVG, global graph, or publication without changing its canonical source is never a fix.

The structured change routes are in
[`machine/extension-points.json`](machine/extension-points.json).

<!-- figure:extension-routing -->

## Add a new rule

1. Identify the canonical concept and owner in `MODULE_INDEX.json`. If the concept genuinely has no
   owner, create one bounded module package rather than attaching the rule to a consumer.
2. Update the owner's narrative and machine-readable requirements. The requirement must have a
   falsifiable failure condition and a stable identifier.
3. Update policy, schema when the shape changes, and positive, negative, and adversarial fixtures.
   A rule with no counter-example is still a claim.
4. Update the canonical requirements registry and framework graph. Update the authority DAG only
   when the rule changes ownership dependencies.
5. Add deterministic enforcement under `04_enforcement` or the runtime only when code can actually
   decide the condition. Semantic judgement remains a review/evidence obligation and must not be
   disguised as a mechanical pass.
6. Run affected validation, deep verification, mutation checking, and transitive revalidation. Since
   1.3.0, "transitive" also covers the cross-representation release pins: a rule change that touches
   a module's narrative must keep that narrative, its manifest, `VERSION`, and
   `docs/registries/FRAMEWORK.json` in agreement, or `FRAMEWORK_STRUCTURE` reports the drift.

## Add a new capability

Capabilities live under `02_capabilities` and are governed by the capability manager. A capability
record must distinguish identity/version, purpose/non-purpose, input/output, permissions,
authentication reference, data and network boundary, trust, approval mode, health/freshness,
fallback, license/security, pinning, update, rollback, quarantine, and host compatibility.

Activate the smallest sufficient set. Unknown or stale health is not healthy. Retrieved content
cannot grant authority. A new connector or provider route may implement a capability contract; it
does not become an authority source for the project.

Profiles opt into capabilities. The minimal profile must remain operable without optional layers,
and a new capability cannot silently expand every profile.

## Add a platform adapter

Create an isolated directory under `05_platform_adapters` with an adapter record, policy,
integration contracts, publication guidance, machine-readable configuration, and tests matching
the sibling adapters. Register it in `PROFILE_ADAPTER_INDEX.json` and name which profiles may select
it.

The adapter translates host operations—tool discovery, file/repository work, permission prompts,
message/tool schemas, or checkpoint handoff. It may not redefine kernel truth, import host history
as canonical framework state, or claim provider-specific certification.

Preflight real availability, permissions, health, data boundary, need, and rollback before
activation. Repository files are declarations; they do not prove an external service is reachable.
Five adapters exist today, derived from `PROFILE_ADAPTER_INDEX.json` rather than named here.

## Add a profile or optional add-on

A profile composes existing modules and may overlay stricter policy. It must preserve a lossless
mapping to the kernel lifecycle. An add-on requires a measured activation threshold, owner, cost,
data boundary, success measure, fallback, and removal path. Derived retrieval indexes never
outrank canonical source or survive incompatible source/model changes. Four profiles exist today,
derived from `PROFILE_ADAPTER_INDEX.json` rather than named here.

## Change the release version

This is a real extension point with a real blast radius, and it was undocumented until the 1.3.0
version bump exercised it.

The primary path is a single file: `VERSION`. Every other file that must move with it is a pin, and
the set is derived rather than enumerated by hand — `machine/extension-points.json`'s
`release_version` change kind names the bucket classes, each backed by
`machine/release-model.json`'s `pins`:

- `release_tooling` — the `RELEASE_VERSION`/`RELEASE_ID`/`CANDIDATE_ID`/`ROOT_NAME` constants in
  `01_control_plane/manifests_releases/tools/release_integrity.py`;
- `registries` — `docs/registries/FRAMEWORK.json`'s `version`, `release_id`, `baseline_chain`, and
  `predecessor_release`;
- `schemas` — `04_enforcement/schemas/module_manifest.schema.json`'s `framework_release` `const`,
  and the `$id`/`schema_version` fields of `release_manifest.schema.json` and
  `release_allowlist.schema.json`;
- `module_manifests` — every `MODULE_MANIFEST.yaml`;
- `module_narratives` — every `MODULE.md` front matter;
- `test_manifest` — `09_tests_evals/TEST_MANIFEST.json`'s `suite_id`;
- `governance` — `governance/SUPERSESSION_LEDGER.json` and
  `governance/coverage_closure_v3/release_surface_registry.json`;
- `allowlist` — `RELEASE_ALLOWLIST.json`'s `release_id` and `candidate_id`, which must be
  regenerated rather than hand-edited once every other pin has moved.

The order that avoids a red working tree while these move — and the reason each ordering constraint
exists — belongs to [GUIDE-170](GUIDE-170-repository-release.md). It is not duplicated here.

## Risk-based validation

<!-- figure:dependency-centrality -->

The chart ranks transitive dependents from the canonical authority DAG. Use the complete rows in
[`machine/module-dependencies.json`](machine/module-dependencies.json) to build the impact set.
High reach means broader revalidation; it does not authorize skipping security or runtime checks
for lower-reach modules.

For any change, record:

- canonical owner and affected requirements;
- direct and transitive consumers;
- representations and derivatives invalidated;
- schemas, fixtures, and runtime branches exercised;
- profile and adapter compatibility;
- migration and rollback route;
- exact evidence and identity after the change;
- unresolved `UNKNOWN`, `BLOCKED`, `INCONCLUSIVE`, or `STALE` states.

## What not to change here

This documentation set is not a second requirements registry. If it disagrees with a package
manifest or canonical registry, the disagreement is a finding. Correct the canonical artifact in a
separately authorized change; regenerate this layer afterward.

## Dependencies

This reference depends on [SYS-110](SYS-110-architecture.md) for ownership and dependency direction
and [SYS-120](SYS-120-runtime-enforcement.md) for enforcement order. The release-version route above
is ordered by [GUIDE-170](GUIDE-170-repository-release.md).
