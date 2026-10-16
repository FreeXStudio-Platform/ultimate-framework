"""The rail: a deterministic state machine that permits exactly one next action.

The framework's operating loop is an ordered sequence, and its central failure
mode is a step being skipped and later asserted as done. The rail removes the
possibility rather than warning about it: every mutating command declares which
rail step it satisfies, and the runtime refuses to run a command whose step is
not the current one.

The rail is derived from, and must stay loss-lessly mappable to, the kernel
lifecycle owned by ``ABS.MODULE.KERNEL.LIFECYCLE``:

    DISCOVERY -> ARCHITECTURE_FROZEN -> CANDIDATE -> SECOND_PASS
              -> INDEPENDENT_REVIEW -> RELEASED

Truthful off-ramps (``BLOCKED``, ``RECOVERING``, ``CANCELLED``, ``STALE``) are
states the rail can report, not steps it can skip to.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .errors import RailViolationError

LIFECYCLE_PHASES = (
    "DISCOVERY",
    "ARCHITECTURE_FROZEN",
    "CANDIDATE",
    "SECOND_PASS",
    "INDEPENDENT_REVIEW",
    "RELEASED",
)

OFF_RAMP_STATES = ("BLOCKED", "RECOVERING", "CANCELLED", "STALE")

# Commands that only read. They are always permitted, in any state, including
# before installation, because refusing to let an operator look at the project
# would make a blocked rail undiagnosable.
READ_ONLY_COMMANDS = {
    "status",
    "next",
    "explain",
    "doc list",
    "doc show",
    "wp list",
    "wp show",
    "evidence list",
    "gate list",
    "truth log",
    "truth verify",
    "verify",
    "help",
}

# Corrective commands repair a step rather than advancing one. They are
# permitted only while the rail is actually stopped on a step they can repair,
# and they satisfy nothing — the rail still has to be walked forward normally.
#
# This exists because a step that cannot be satisfied and cannot be repaired is
# a dead end, and the rail's whole promise is that `absolute next` always names
# an action that can succeed. A document package that cannot be sealed used to
# stop S5/S6 permanently with no command able to remove it.
CORRECTIVE_COMMANDS: dict[str, frozenset[str]] = {
    "doc abandon": frozenset({"S5.DOCUMENTS_AUTHORED", "S6.DOCUMENTS_SEALED"}),
}


@dataclass(frozen=True)
class RailStep:
    step_id: str
    ordinal: int
    phase_on_entry: str
    phase_on_exit: str
    command: str
    title: str
    why: str
    satisfied: Callable[[dict[str, Any]], bool]
    guidance: str
    repeatable: bool = False


def _has(ctx: dict[str, Any], key: str) -> bool:
    return bool(ctx.get(key))


def _identity_matches(ctx: dict[str, Any], key: str) -> bool:
    """True only when *both* identities exist and are equal.

    A naive ``ctx[key] == ctx["tree_identity"]`` reports satisfied on a fresh
    project, because ``None == None``. That would mark the terminal steps done
    before the project was even installed. Absence is never satisfaction.
    """
    recorded = ctx.get(key)
    current = ctx.get("tree_identity")
    return bool(recorded) and bool(current) and recorded == current


def _all_of(ctx: dict[str, Any], done_key: str) -> bool:
    """True when at least one live document exists and every one reached ``done_key``.

    ``document_count`` counts live packages only. An abandoned package is a
    recorded decision, not outstanding work, so it must not hold the rail — but
    abandoning every package leaves a count of zero, which is not satisfaction
    either.
    """
    total = ctx.get("document_count", 0)
    return bool(total) and ctx.get(done_key, 0) == total


def _work_closed(ctx: dict[str, Any]) -> bool:
    """True only once work has been opened and every packet is closed."""
    return bool(ctx.get("work_packets_created", 0)) and ctx.get("open_work_packets", 1) == 0


RAIL_STEPS: tuple[RailStep, ...] = (
    RailStep(
        step_id="S1.INSTALL",
        ordinal=1,
        phase_on_entry="DISCOVERY",
        phase_on_exit="DISCOVERY",
        command="init",
        title="Install the control namespace",
        why="Nothing can be governed until the project has a frozen identity and a source of truth.",
        satisfied=lambda ctx: _has(ctx, "installed"),
        guidance="absolute init --project <slug> --mission \"<mission>\" --profile <minimal|standard|enterprise|audithunt> --adapter <adapter>",
    ),
    RailStep(
        step_id="S2.GOAL_LOCK",
        ordinal=2,
        phase_on_entry="DISCOVERY",
        phase_on_exit="DISCOVERY",
        command="goal set",
        title="Lock the active goal",
        why="ABS.REQ.GOAL_LOCK.002 rejects material action that has no valid upward goal link.",
        satisfied=lambda ctx: _has(ctx, "active_goal_id"),
        guidance="absolute goal set --id <ABS.GOAL...> --statement \"<what done means>\"",
    ),
    RailStep(
        step_id="S3.WORK_OPENED",
        ordinal=3,
        phase_on_entry="DISCOVERY",
        phase_on_exit="DISCOVERY",
        command="wp new",
        title="Open one bounded work packet",
        why="Work is executed as one reversible, bounded unit with declared rollback.",
        # "Has work ever been opened", not "is a packet open right now". Closing
        # the last packet at S9 must not un-satisfy S3 and drag the rail
        # backwards; whether anything is still open is S9's question.
        satisfied=lambda ctx: bool(ctx.get("work_packets_created", 0)),
        guidance="absolute wp new --objective \"<objective>\" --rollback \"<how to undo>\"",
        repeatable=True,
    ),
    RailStep(
        step_id="S4.DOCUMENTS_CREATED",
        ordinal=4,
        phase_on_entry="DISCOVERY",
        phase_on_exit="DISCOVERY",
        command="doc new",
        title="Create the governed documents",
        why="The framework's unit of knowledge is the canonical module package, not a loose file.",
        satisfied=lambda ctx: ctx.get("document_count", 0) > 0,
        guidance=(
            "absolute doc new --id <slug> --title \"<title>\" --question \"<the question it answers>?\" "
            "--requirement \"<a normative rule this package owns>\" --requirement \"<a second one>\" "
            "--failure \"<the worst thing this package must prevent>\" "
            "--source-evidence \"<where its truth comes from>\" --excludes \"<what it deliberately does not own>\""
        ),
        repeatable=True,
    ),
    RailStep(
        step_id="S5.DOCUMENTS_AUTHORED",
        ordinal=5,
        phase_on_entry="DISCOVERY",
        phase_on_exit="DISCOVERY",
        command="doc step",
        title="Author every representation in lockstep",
        why="ABS.REQ.DOCUMENT_BLUEPRINT_PARITY.002 requires representations to be authored section-by-section, not back-filled.",
        satisfied=lambda ctx: _all_of(ctx, "documents_authored"),
        guidance=(
            "absolute doc step --id <slug> --all   (repeat per document; "
            "'absolute doc abandon --id <slug> --reason \"<why>\"' closes one that cannot be finished)"
        ),
        repeatable=True,
    ),
    RailStep(
        step_id="S6.DOCUMENTS_SEALED",
        ordinal=6,
        phase_on_entry="DISCOVERY",
        phase_on_exit="ARCHITECTURE_FROZEN",
        command="doc seal",
        title="Seal and stamp every document into the source of truth",
        why="An unstamped document has no identity, so no later claim can be bound to it.",
        satisfied=lambda ctx: _all_of(ctx, "documents_sealed"),
        guidance=(
            "absolute doc seal --id <slug>   ('absolute doc check --id <slug>' lists what blocks it; "
            "'absolute doc abandon --id <slug> --reason \"<why>\"' closes one that cannot be sealed)"
        ),
        repeatable=True,
    ),
    RailStep(
        step_id="S7.EVIDENCE",
        ordinal=7,
        phase_on_entry="CANDIDATE",
        phase_on_exit="CANDIDATE",
        command="evidence add",
        title="Record evidence for the active work packet",
        why="ABS.REQ.EVIDENCE_GATES: a completion claim without evidence bound to an exact hash is not a claim.",
        satisfied=lambda ctx: ctx.get("evidence_count", 0) > 0,
        guidance="absolute evidence add --method \"<what was run>\" --result PASS|FAIL|BLOCKED|NOT_RUN|INCONCLUSIVE",
        repeatable=True,
    ),
    RailStep(
        step_id="S8.GATE",
        ordinal=8,
        phase_on_entry="CANDIDATE",
        phase_on_exit="CANDIDATE",
        command="gate run",
        title="Evaluate the evidence gate",
        why="The gate is what converts recorded evidence into a permitted state change.",
        satisfied=lambda ctx: bool(ctx.get("gate_passed_current_identity")),
        guidance="absolute gate run --id <ABS.GATE...>",
        repeatable=True,
    ),
    RailStep(
        step_id="S9.WORK_COMPLETED",
        ordinal=9,
        phase_on_entry="CANDIDATE",
        phase_on_exit="CANDIDATE",
        command="wp complete",
        title="Complete the bounded work packet",
        why="A packet may only close once its own gate passed against the current identity.",
        satisfied=lambda ctx: _work_closed(ctx),
        guidance="absolute wp complete --id <ABS.WP...>",
        repeatable=True,
    ),
    RailStep(
        step_id="S10.CHECKPOINT",
        ordinal=10,
        phase_on_entry="CANDIDATE",
        phase_on_exit="CANDIDATE",
        command="checkpoint",
        title="Write a restart-safe session checkpoint",
        why="Recovery must not depend on a live context that can be lost.",
        satisfied=lambda ctx: bool(ctx.get("checkpoint_current_identity")),
        guidance="absolute checkpoint --next-action \"<exact first next action>\"",
        repeatable=True,
    ),
    RailStep(
        step_id="S11.SECOND_PASS",
        ordinal=11,
        phase_on_entry="SECOND_PASS",
        phase_on_exit="SECOND_PASS",
        command="pass2",
        title="Review the frozen whole (pass 2)",
        why="ABS.REQ.LIFECYCLE_TWO_PASS.002: pass 1 builds the candidate, pass 2 reviews it frozen.",
        satisfied=lambda ctx: _identity_matches(ctx, "second_pass_identity"),
        guidance="absolute pass2 --reviewer \"<role that did not author>\"",
    ),
    RailStep(
        step_id="S12.VERIFIED",
        ordinal=12,
        phase_on_entry="INDEPENDENT_REVIEW",
        phase_on_exit="INDEPENDENT_REVIEW",
        command="verify --record",
        title="Run deterministic deep verification and record it",
        why="Every claim in the project must be reproducible from raw bytes by a fresh process.",
        satisfied=lambda ctx: _identity_matches(ctx, "verified_identity"),
        guidance="absolute verify --record",
    ),
    RailStep(
        step_id="S13.RELEASED",
        ordinal=13,
        phase_on_entry="RELEASED",
        phase_on_exit="RELEASED",
        command="release",
        title="Assemble the release",
        why="Release is the only step that produces an externally shippable identity.",
        satisfied=lambda ctx: _identity_matches(ctx, "released_identity"),
        guidance="absolute release --out <path.zip>",
    ),
)

STEPS_BY_ID = {step.step_id: step for step in RAIL_STEPS}
STEPS_BY_COMMAND: dict[str, list[RailStep]] = {}
for _step in RAIL_STEPS:
    STEPS_BY_COMMAND.setdefault(_step.command, []).append(_step)


def completed_steps(ctx: dict[str, Any]) -> list[RailStep]:
    return [step for step in RAIL_STEPS if step.satisfied(ctx)]


def next_step(ctx: dict[str, Any]) -> RailStep | None:
    """The single next required step, or ``None`` when the rail is complete.

    The first unsatisfied step wins even if a later step happens to look
    satisfied, because out-of-order satisfaction is exactly the condition the
    rail exists to catch.
    """
    for step in RAIL_STEPS:
        if not step.satisfied(ctx):
            return step
    return None


def contiguous_completed(ctx: dict[str, Any]) -> list[RailStep]:
    """Steps completed in an unbroken run from the start.

    Phase is derived only from this prefix. A later step that happens to look
    satisfied while an earlier one is open must never advance the phase; that is
    precisely the skip the rail exists to prevent.
    """
    out: list[RailStep] = []
    for step in RAIL_STEPS:
        if not step.satisfied(ctx):
            break
        out.append(step)
    return out


def current_phase(ctx: dict[str, Any]) -> str:
    prefix = contiguous_completed(ctx)
    if not prefix:
        return RAIL_STEPS[0].phase_on_entry
    if len(prefix) == len(RAIL_STEPS):
        return "RELEASED"
    return RAIL_STEPS[len(prefix)].phase_on_entry


def check_permitted(command: str, ctx: dict[str, Any]) -> RailStep | None:
    """Authorize a command against the rail, or raise ``RailViolationError``.

    Returns the rail step the command satisfies (``None`` for read-only
    commands), so the caller can record which step a mutation advanced.
    """
    if command in READ_ONLY_COMMANDS:
        return None

    repairs = CORRECTIVE_COMMANDS.get(command)
    if repairs is not None:
        pending = next_step(ctx)
        if pending is not None and pending.step_id in repairs:
            return None  # repairs the current step; advances none
        raise RailViolationError(
            command,
            pending.guidance if pending is not None else "none",
            f"'{command}' repairs {sorted(repairs)}; the rail is at "
            f"{pending.step_id if pending is not None else 'complete'}",
        )

    candidates = STEPS_BY_COMMAND.get(command)
    if not candidates:
        raise RailViolationError(command, "unknown", f"'{command}' is not a rail command")

    pending = next_step(ctx)
    if pending is None:
        target = candidates[-1]
        if target.repeatable:
            return target
        raise RailViolationError(
            command,
            "none",
            "the rail is complete; reopen work with 'absolute wp new' before mutating again",
        )

    for step in candidates:
        if step.step_id == pending.step_id:
            return step

    # A repeatable step already passed may be re-run, but only while the rail has
    # not moved beyond the phase that owns it. This lets an operator add a second
    # work packet or a second document without letting them jump forward.
    for step in candidates:
        if step.repeatable and step.ordinal < pending.ordinal:
            return step

    earliest = min(candidates, key=lambda item: item.ordinal)
    if earliest.ordinal > pending.ordinal:
        reason = f"step {earliest.step_id} comes after the current step {pending.step_id}"
    else:
        reason = f"step {earliest.step_id} is already closed and is not repeatable"
    raise RailViolationError(command, pending.guidance, reason)


def describe(ctx: dict[str, Any]) -> dict[str, Any]:
    pending = next_step(ctx)
    done = contiguous_completed(ctx)
    out_of_order = [step.step_id for step in completed_steps(ctx) if step not in done]
    return {
        "phase": current_phase(ctx),
        "out_of_order_satisfied": out_of_order,
        "completed_step_count": len(done),
        "total_step_count": len(RAIL_STEPS),
        "completed_steps": [step.step_id for step in done],
        "next_step": None
        if pending is None
        else {
            "step_id": pending.step_id,
            "ordinal": pending.ordinal,
            "title": pending.title,
            "why": pending.why,
            "command": pending.guidance,
        },
        "rail_complete": pending is None,
    }
