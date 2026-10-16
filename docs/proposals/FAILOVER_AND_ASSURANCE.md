---
type: proposal
id: ABS.PROPOSAL.FAILOVER_AND_ASSURANCE
target_release: 1.4 (candidate — not scheduled)
status: PROPOSED — first pass, NOT hardened, NOT source-of-truth
raised: 2026-09-16
raised_by: FreeXStudio (field use in a downstream product), recorded and independently re-measured by this project
---

# Proposal — a failover / degradation / assurance module for a 1.4 candidate

**This is a pass-1 artifact.** It records a gap and a proposed scope. It has not been through deep
refinement or hardening, carries no `artifact-hardened` stamp, and is not source-of-truth. Nothing
here is scheduled.

## The gap

The Absolute Canonical Framework payload has no failover, degradation, or assurance workflow.
It names the right vocabulary and states the right requirements; the **contract beneath them is
absent**.

## Measured evidence (re-measured in this repository, 2026-09-16)

Run against `absolute-canonical-framework-v1.3.1/`:

| Probe | Result |
|---|---|
| `grep -ril -E 'failover\|standby'` | **0 files** |
| `grep -ril 'gatekeeper'` | **8 files** — `blueprint/SYSTEM.{md,json}` plus GUIDE-170 and REF-160 (and their archived/HTML twins). Every hit is the derived *"which gate guards a module"* relation, never a runtime gatekeeper. |
| `grep -ril 'health check'` | **3 files** |
| `04_enforcement/observability/HEALTH_MODEL.md` | **2 lines** — the eight verdict states and one sentence on probes |
| `00_kernel/evidence_gate_health/MODULE.md` | 34 lines |
| `04_enforcement/observability/MODULE.md` | 32 lines |

> **Correction to the originating note.** It reported `health check` as 5 files; this repository
> measures **3**. The discrepancy does not change the finding — most likely a different file-type
> filter — but the number recorded here is the one measured locally.

## What actually exists today (stated fairly)

The two modules are **not** empty, and the gap is not that they point the wrong way:

- `ABS.REQ.EVIDENCE_GATES_HEALTH.003 (MUST)` already requires health to distinguish healthy,
  degraded, partial, dependency-failed, unknown, untested, stale, misconfigured and
  root-cause-unknown — **and to test the reporter itself**.
- `ABS.REQ.OBSERVABILITY_INCIDENT.001/003 (MUST)` already forbid treating absence of alerts as
  health, and already require watchdogs and health reporters to be fault-injected and to fail
  truthfully when their own reporting path is down.
- Both modules carry a state model, a failure-and-recovery clause naming the right primary failure
  (`PASS is issued without evidence`; `silence or stale probe is labeled healthy`), and both are
  `status: CANDIDATE`.

So the direction is already correct and normative. What is missing is the **operational contract** a
builder could conform to and a verifier could check.

## What is missing

No module in the payload defines:

1. The eight-state verdict contract expanded into rules — freshness windows, `UNKNOWN` on timeout,
   no default-OK, critical-only green.
2. Degrade modes and hot flags, with **money invariants** that hold across every mode.
3. Breaker consultation on hot paths.
4. Outbox + dead-letter for derived stores.
5. One escalation bus, with explicit adjudication and aging.
6. A gate ladder with stable ids derived from the gates (the engine's `gatekeepers.py` relation).
7. A separate fault-seeking assurance plane — synthetic canary, negative probes, census,
   health-vs-behaviour cross-check.
8. Drills as tests, producing artifacts.
9. Hash-chained transition receipts.
10. An `ENV.DOMAIN.MODULE.GATE.CHECK.ERROR` error-identity registry.

## Why it is worth doing

The incident class this closes — *every failure returned success* — is precisely what a
framework-level health and assurance contract exists to prevent, and it is the same defect class the
framework's own `HEALTH_MODEL.md` vocabulary was written for. A downstream FreeXStudio product hit it in July 2026 and is
now building the concrete system. The generic half belongs in the framework so the next project does
not re-derive it from scratch.

## Constraints on any implementation

- **The payload is not edited in place.** `absolute-canonical-framework-v1.3.1/` is the sealed,
  hash-attested record of release `ABS.RELEASE.1.3.1`. Adding a module means a **new release by
  GUIDE-170** (`docs/ultimate-engine/GUIDE-170-repository-release.md`): rename the payload, update
  every pin it lists, regenerate the documentation set with the vendored engine, regenerate the
  allowlist, run the release procedure, seal, verify clean-room, reproduce, tag.
- Likely home: a `FAILOVER_AND_ASSURANCE` module under `00_kernel/` or `04_enforcement/`, owning a
  new `ABS.CONCEPT.*` and extending — not duplicating — the two modules above. Two copies of one
  requirement is the drift defect this framework exists to prevent.
- Three-pass applies: this is an architecture-class artifact, so creation → deep refinement →
  hardening before it earns source-of-truth status.

## Source to lift from, once accepted

The downstream product's own failover and assurance design is a **candidate input, not an
authority**: the framework absorbs only the project-independent part, and re-derives it against the
payload's own identity and gate model.

## Next step

Maintainers decide whether a 1.4 exists. Until then this file is the record and nothing is scheduled.
