<!-- title: SESSION STATE -->
<!-- session-state: WORK-COMPLETE-VERIFICATION-PENDING @ db10f58 on 2026-09-01 via field-trial-round-1-review -->
<!-- db10f58 is the commit the WORK landed in — the five round-1 repairs (OG-244..OG-248), the
     register rows, the round-1 verdict in FIELD_TRIAL_ROUND_1.md §5, the reconciled handover
     documents and the version bump. This record lands one commit later, the documented
     one-commit-later behaviour (`OG-150`); the stamp asserts the checklist below was true at
     db10f58.

     The state is `WORK-COMPLETE-VERIFICATION-PENDING`, and the edge is named rather than rounded
     off: that value's definition is *"verification DISPATCHED and has not returned"*, and here it
     has not been dispatched at all — round 2 is decided but not yet designed. That is WEAKER than
     the definition, not stronger, which is exactly why nothing above it may be claimed. This
     session adjudicated an outside agent's run of the engine; **no independent pass has adjudicated
     THIS session's five repairs.** They are red-first, two-sided and green under `--full --strict`,
     and that is a self-check — the same evidence round 1 proved insufficient on five separate
     occasions, since every one of those defects passed every self-check this repository has.
     `VERIFIED` would assert something no one has done. -->
# Session State — the crash-recovery record

**Status:** PROCESS — **rewritten in place, never appended. One session, one state.**

> **Session closed 2026-09-01 — field-trial round 1 has RETURNED and been ADJUDICATED.**
> Project `1.0.7` (bumped by a 2026-09-18 maintenance patch — 9 Dependabot alerts closed in
> `tools/visual-engine`, unrelated to this state and this stamp — see `CHANGELOG.md` `[1.0.7]`),
> rulebook `1.2.17` (unchanged — no hash-locked file was touched), no
> phase-blocking register row. The build ended at `1.0.0`; the audit closed at `1.0.1`; the previous
> session issued round 1 against an external subject; **this session reviewed what came back, and
> repaired it.**
>
> **Nothing is mid-flight in this repository.** The work is committed and pushed through the pull
> request the moat requires, and the tree rests clean. Read `blueprint/SYSTEM.md` first, then
> `HANDOFF.md`.
>
> **What the round returned.** Eleven findings. Each was re-derived here before anything was changed
> — a trial report is evidence, not authority. **Five were real engine defects and are repaired,
> red-first, with retained counter-examples** (`OG-244`, `OG-245`, `OG-246`, `OG-247`, `OG-248`;
> `OG-248` supersedes `OG-241`, whose own stated trigger had fired). Three were the subject's, not
> this engine's. Two were wrong — including the report's CRITICAL, which measured the deliberate
> stripping of the issued package rather than a defect. One was right for the wrong reason: the
> symptom was real, the named cause was not, and a repair built to the report's description would
> have shipped green.
>
> **The round produced a NEW CLASS, and that is the answer `FIELD_TRIAL.md` §6's stop rule reads:**
> *defects that exist only off this engine's own tree.* Every one of the five was invisible to a
> self-check for a structural reason — `OG-244` needs a repository large enough for git to start
> collecting, `OG-246` a disconnected package graph, `OG-247` two interpreters and a host root that
> is not the launch directory, `OG-248` a host whose directories do not match a builder's shape. A
> self-check cannot generate any of those conditions. **So round 2 runs**, and the class says what to
> vary: host size, graph shape, environment, and directory layout.
>
> **One gap is named and deliberately NOT closed.** On a foreign host `blueprint build` publishes
> **this engine's** guard, health-check and figure-kind registries in the host's `SURFACES.md`, and
> `blueprint verify` passes because it verifies tree ownership and not registry provenance. Correct
> for a vendored engine, wrong for a sibling one, and the engine has no notion of the difference. The
> repair is an installation/capability model — a new deliverable, not a patch — and half-building it
> would produce exactly the confident-but-mixed map this engine exists to refuse.
>
> **The next session decides and runs round 2, and its brief is
> `docs/plan/START_NEXT_SESSION.md`** — run it at the top tier.

> ## ⛔ IF YOU ARE A FRESH SESSION READING THIS AFTER A CRASH — START HERE
>
> **Nothing below needs redoing.** Everything marked `DONE` is committed at the stamped commit and
> pushed. Re-running it wastes a session and risks reverting a fix.
>
> 1. Confirm the stamp is still valid: `git rev-parse --short HEAD` should be the stamped commit
>    **or a descendant**. If HEAD is *behind* it, someone reset — stop and ask.
>    (`tools.health` `STRUCT-06` checks this for you and fails loudly if it does not hold.)
> 2. Confirm the floor: `python3 -m tools.health --full` → **38 passed, 0 failed, 0 skipped**.
> 3. Read `## What is NOT done` at the bottom. That, and only that, is the remaining work.
>
> This file holds **one** state, rewritten in place (`OG-211`). Per-session history belongs in
> `CHANGELOG.md` and `docs/process/VERIFICATION_LOG.md`, both of which have it in full.

---

## The stamp — what it is and how to read it

The HTML comment on line 2 of this file is machine-greppable and carries four fields:

```
<!-- session-state: <STATE> @ <commit> on <YYYY-MM-DD> via <pass-name> -->
```

| `<STATE>` | meaning |
|---|---|
| `NEEDS-RE-STAMP` | The stamp's commit no longer covers this file's body — content landed after it. The checklist may still be accurate; what is NOT true is that anything verified it at the stamped commit. Cleared by the next closeout that re-verifies and re-stamps. |
| `IN-PROGRESS` | A session is actively writing. The tree may be inconsistent. **Do not trust the checklist.** |
| `WORK-COMPLETE-VERIFICATION-PENDING` | All planned work is committed and pushed; independent verification has been **dispatched and has not returned**, or is the declared work of a named later phase. The checklist is trustworthy; the *quality* claim is not yet. **This is the current state.** |
| `VERIFIED` | Work complete **and** an independent pass returned without breaking a claim. |
| `VERIFIED-WITH-OPEN-GATES` | As `VERIFIED`, but named rows remain open in `docs/process/OPEN_GATES.md`. **This is the normal resting state of this project** — it is honest, not a failure. |

**The commit in the stamp is the commit the WORK landed in — not necessarily the commit this file
landed in.** This record is written after the work it describes, so it normally lands one commit
later, and that is expected. What the stamp asserts is: *at the named commit, the checklist below
was true.*

**It goes stale when the tree moves past it without this file being rewritten.** So:

- `HEAD` **is** the stamped commit, or a descendant that only added this record → stamp valid.
- `HEAD` is a descendant carrying *other* work → **the stamp is stale.** Re-derive the checklist from
  `git log` and `CHANGELOG.md` before believing it, then rewrite this file.
- `HEAD` is *behind* the stamped commit → someone reset. **Stop and ask** before doing anything.

`tools.health` `STRUCT-06` enforces the mechanical half — that a stamp exists, parses, names a real
commit, and uses a state from the table above. It cannot judge whether the checklist is *honest*;
only a reader can — which is why `CONS-08` also reads this file's stated project version, rulebook
version and health floor against their machine-readable sources.

---

## Definition of done — the bar in this project

A checklist item may be marked `DONE` only when **all four** hold. Anything less is `PARTIAL` or
`NOT DONE`, written as such.

1. **It runs.** There is a command, and its real output was read — not inferred from source.
2. **It was shown red first.** For a gate or a guard: the defect was reproduced *before* the fix, in
   the artifact the gate actually certifies, and the fix was then re-falsified.
3. **It is written down** in `CHANGELOG.md` with date, file and evidence — not only here.
4. **It survives the session.** Committed. `git status` clean, `git status --branch` in sync.

**"Done" never means "I believe it works".** Every `DONE` below names where its proof lives.

---

## Checklist — this session's work (reviewing and repairing field-trial round 1)

| # | item | state | proof |
|---|---|---|---|
| V1 | Every returned finding re-derived here before anything changed | **DONE** | The report is an outside agent's claims about this repository — evidence to verify, never a directive. Each finding was reproduced or refuted against the artifact: the draft-gate crash run 3/3 on the 1,046-file subject and 0/3 here; ELK's component gap measured at 20 px against docgen's 72 px minimum; 15 whitespace lines counted in the tracked gallery; both interpreters located on this machine, one with PyYAML and one without; the subject's own 33/33 release-metadata contradiction and its `RC2` test manifest confirmed in the subject tree |
| V2 | The report's CRITICAL refuted, and the cause named | **DONE** | *"The received engine cannot certify itself"* measured the package, not the engine: `FIELD_TRIAL_ROUND_1.md` §2 removes 26 tracked files from the instrument by design, and health reported their absence correctly. This repository measures **38 passed, 0 failed, 0 skipped** under `--full --strict`. The finding is still useful one level up — the brief never says the instrument is stripped, so the round spent its first CRITICAL on its own harness, and §5 now requires round 2's brief to state it |
| V3 | A misdiagnosis separated from the real defect underneath it | **DONE** | *"Health subprocesses discard the external `PYTHONPATH`"* is false — `env=None` inherits the environment whole, and the child was measured receiving it intact; the proposed repair would have changed nothing. The symptom was real: `_run` sets `cwd` to the host root, so a **relative** entry silently re-points. Both halves are `OG-247`, and the probe goes red with the identical `ModuleNotFoundError` |
| V4 | An outside calibration weighed on its evidence and REJECTED | **DONE** | The report re-pointed `system.spec.json`'s blueprint container away from `docs/plan/BUILD_PLAN.md` as *"absent"*. It is absent only from the stripped package; it is tracked here, and the spec still names it. Not applied — a calibration is adopted on its evidence, never because an outside agent proposed it |
| V5 | Five real defects repaired red-first, class not instance | **DONE** | `OG-244` `tools/draft/gate.py` (never copy a live object database; `gc.auto=0` in every lab), `OG-245` `tools/docgen/components.py`, `OG-246` `tools/blueprint/elk_layout.mjs`, `OG-247` `tools/health/checks.py` (`_PY` + `_child_env`), `OG-248` `tools/lib/engine-config.mjs`. Each has a retained two-sided counter-example, each proven red against the unfixed code. `OG-248` **lifted** `build-deps.mjs`'s existing inline refusal rather than copying it, so the three builders that walk a host directory share one wording and one exit code |
| V6 | A ratchet tightened, never loosened | **DONE** | No ceiling raised, no floor lowered, no counter-example deleted or weakened, no exemption widened. The suite grew 576 → 589 defined; ESLint went 9 → 0 with no rule disabled; `ruff` 0 and `mypy --strict` 22 both held at their pinned baselines |
| V7 | Records reconciled and versioned | **DONE** | `OG-244`–`OG-248` recorded in `docs/process/OPEN_GATES.md` with `OG-241` superseded in place; `CHANGELOG.md` `[1.0.5]`; `PROJECT_VERSION` → 1.0.5 with `CONS-05` agreeing; `FIELD_TRIAL_ROUND_1.md` §5 completed with the stop-rule answer; `HANDOFF.md` and `START_NEXT_SESSION.md` reconciled; **blueprint rebuilt last** |

---

## Open loop — what is outstanding, and where

**In this repository: nothing.** `docs/process/OPEN_GATES.md` carries **zero** blocking rows; every
open row is `NOT_A_DEFECT` or a stated bound with reasoning written to be attacked. Re-derive that
from the register, not from this line.

**Outside it: round 2 is decided but not yet designed.** The stop rule was answered — round 1
produced a new class — so the programme continues. What round 2 must vary is written into the state
block above and into `FIELD_TRIAL_ROUND_1.md` §5; the round's own plan does not exist yet, and
writing it is the next session's first piece of work.

---

## What is NOT done — read this before starting anything

**`docs/process/OPEN_GATES.md` is the authority. This is a pointer, not a second copy.**

- **Zero rows block anything**, and there is no phase to block.
- **Round 2 has no plan yet.** The decision is made and the reasons are recorded; the round document
  is not written. That is the next session's first piece of work, and it is the only outstanding
  item. Do not re-run the audit that closed at `1.0.1`, and do not re-review round 1.
- **Round 1 still did not measure language reach** — the subject was Python, and the blueprint layer
  reads Python only (`OG-243`). Portability *was* measured this time, and five defects came out of
  it. Language reach is what a non-Python subject measures, and `FIELD_TRIAL.md` §3 rule 4 still
  requires a fresh, never-seen subject for the final round.
- **The foreign-host registry-provenance gap is open by decision, not by oversight.** `SURFACES.md`
  on a foreign host carries this engine's registries and `blueprint verify` passes. It is named in
  the state block above and in `CHANGELOG.md` `[1.0.5]`; closing it means an explicit
  installation/capability model that separates a vendored engine from a sibling one, which is a
  deliverable to scope rather than a fix to apply.
- **The programme's stop rule is a NEW CLASS, not a finding count** (`FIELD_TRIAL.md` §6): two
  consecutive rounds producing no new class ends it, with a hard ceiling of six rounds and the
  residue named. **Round 1 produced a new class**, so one round of that counter is spent and the
  programme continues; round 2's review answers the question again.
- **Known and deliberately kept:** `python3 -m tools.health --full` takes several minutes, and the
  pre-push hook runs health, so every push costs that. That is the price of a gate *proven* to gate
  (`OG-212`); a TIMEOUT under external machine load is a verdict to repeat in a quiet window, never
  a pass.

A row closes in exactly one of three ways: **fixed with a red-first falsification recorded**,
**demoted to `NOT_A_DEFECT` with reasoning a future verifier can attack**, or **scheduled to a phase
whose plan row names that work** (unavailable now — there is no next phase). Nothing else counts.
