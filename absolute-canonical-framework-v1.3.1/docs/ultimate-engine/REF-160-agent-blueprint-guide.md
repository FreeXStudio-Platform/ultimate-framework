---
id: REF-160
classification: public
title: Absolute Agent Blueprint Guide
surface: web
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

# Absolute Agent Blueprint Guide

## Purpose

This is the entry point for a fresh agent that must understand the project from blueprints,
figures, tables, graphs, and JSON rather than reading the prose corpus.

<!-- figure:agent-navigation -->

## Structural artifact routing

| question | primary machine artifact | primary visual |
|---|---|---|
| What are the major components and dependencies? | `machine/domain-model.json` and `machine/module-dependencies.json` | `domain-dependencies` in SYS-110; standalone domain graph. |
| Where does a new rule, capability, or adapter go? | `machine/extension-points.json` | `extension-routing` in REF-130. |
| What is risky to change? | `machine/module-dependencies.json` centrality rows | `dependency-centrality` in SYS-110/REF-130. |
| What is enforced and what protects each check? | `machine/verification-model.json` | `verification-stack` and `assurance-boundary`. |
| What happens first and what must wait? | `machine/runtime-model.json` | project rail, document rail, and governed-mutation sequence. |
| How is this repository versioned and released? | `machine/release-model.json` | `release-pipeline` and `release-pin-surface` in GUIDE-170. |

The interactive directory graph is under `graphs/structure/`. It compresses deep files into
directory nodes at a fixed depth; use it for navigation, not as the canonical module dependency
graph.

<!-- figure:question-coverage -->

## What the 2026-09-01 blueprint-only test showed

On 2026-09-01, a test restricted to blueprints, figures, and JSON — no narrative documentation, no
implementation source — answered 4 of 5 required questions on its first pass. The unanswered
question was the enforcement one, because six verifier sections at the time redirected the reader
to implementation source instead of carrying a machine-readable protection claim. After each
section was given one, a second pass answered 5 of 5.

Its dated verdict: blueprint-first navigation was faster and complete for those five questions;
narrative documentation remained necessary for semantic nuance. This test has **not** been re-run
against the framework at 1.3.0; re-running it against the sixth, release-versioning question this
release adds is a new evaluation and a new dated artifact, out of scope for this pass.

## Blueprint completeness rules

A structural answer is acceptable only when the artifact identifies the source it derives from,
the edge direction, and any known missing domain. A pretty rendering with no machine-readable
source does not qualify. A machine model that cannot be regenerated from the subject is a copied
claim, not a blueprint.

The engine's built-in `blueprint/` is part of the pack but has a narrower scope: it derives the
tracked Python module import graph and maps those modules into authored executable containers. It
does not replace `domain-model.json` or the canonical authority DAG.

## What the blueprint pack cannot answer

`blueprint/` derives the **tracked Python import graph** only. Most canonical modules in this
framework are representation-owned — their authority lives in Markdown, YAML, JSON, schemas, or
fixtures — and are invisible to it. The full topology is `machine/domain-model.json` and the
canonical authority DAG, not the built-in blueprint.

The completeness report's headline number is a measurement, not an oversight: as recorded in
[`blueprint/COMPLETENESS.md`](../../blueprint/COMPLETENESS.md), `verified` is **0** across every
tracked node, and it is **structurally unreachable** for the current map. `verified` requires rung 4
or deeper, and that same report states none of the tracked nodes are at rung 4 or deeper — no amount
of documentation work alone changes that arithmetic.

The `gatekeepers` column answers "what will refuse me?" and is itself derived — a registered guard
is listed only when its own source actually reads the module in question.

Adding a governed owning document for a container — as this pass does for
`documentation-derivation`, whose owner reassigns from an ungoverned `REGENERATE.md` to the
governed `GUIDE-170` — changes the *document* half of the `verified` predicate. It cannot change
the *rung* half: a container with no rung-4 module still cannot report `verified`, whatever its
owning document claims. [`blueprint/COMPLETENESS.md`](../../blueprint/COMPLETENESS.md) states this
consequence in full, per container, for every container this release touches.

## Dependencies

This guide routes to [SYS-110](SYS-110-architecture.md),
[SYS-120](SYS-120-runtime-enforcement.md), [REF-130](REF-130-extension-points.md),
[REF-150](REF-150-evidence-limitations.md), and [GUIDE-170](GUIDE-170-repository-release.md). The
machine-readable document/dependency index is
[`machine/document-index.json`](machine/document-index.json).
