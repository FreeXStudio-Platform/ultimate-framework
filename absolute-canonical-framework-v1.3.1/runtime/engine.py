"""Governed operations. Every mutation of a project passes through here.

The order inside each operation is fixed and load-bearing:

    1. authorize against the rail
    2. write the artifact
    3. append the ledger entry
    4. update project state

Steps 3 and 4 are in that order deliberately. If the process dies between them,
the truth ledger holds a record of an action whose state was not yet applied —
recoverable, and visible to ``absolute status``. The reverse order would produce
state with no record, which is indistinguishable from a forged state.
"""
from __future__ import annotations

import functools
import re
import shutil
from pathlib import Path
from typing import Any

from . import CONTROL_DIR, RUNTIME_VERSION
from .documents import (
    DOCUMENT_STEPS,
    GENERATORS,
    STEPS_BY_ID,
    TOTAL_STEPS,
    next_document_step,
    render_svg,
    scan_todos,
)
from .docvalidate import validate_document
from .errors import (
    AlreadyInstalledError,
    AuthorityError,
    DocumentStepError,
    EvidenceError,
    GoalLockError,
    SchemaError,
)
from .project import SUBDIRECTORIES, Project
from .rail import check_permitted, describe
from .util import (
    SLUG_PATTERN,
    actor_id,
    atomic_write,
    atomic_write_json,
    canonical_json,
    emit_interface_instance,
    exclusive_lock,
    normalize_actor,
    read_json,
    sha256_obj,
    sha256_path,
    sha256_tree,
    slug_to_namespace,
    utc_now,
    valid_id,
)

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
RESULT_STATES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN", "INCONCLUSIVE", "STALE")


def framework_identity() -> dict[str, Any]:
    """Identity of the framework installation performing the operation."""
    identity = read_json(FRAMEWORK_ROOT / ".absolute/release/release_identity.json")
    return {
        "framework_id": identity["framework_id"],
        "release_id": identity["release_id"],
        "version": identity["version"],
        "candidate_tree_sha256": identity["candidate_tree_sha256"],
        "runtime_version": RUNTIME_VERSION,
    }


def known_interfaces() -> set[str]:
    index = read_json(FRAMEWORK_ROOT / "docs/registries/INTERFACE_INDEX.json")
    return {item["interface_id"] for item in index["interfaces"]}


def available_profiles() -> dict[str, Path]:
    base = FRAMEWORK_ROOT / "06_project_profiles"
    return {path.parent.name: path for path in sorted(base.glob("*/profile.json"))}


def available_adapters() -> dict[str, Path]:
    base = FRAMEWORK_ROOT / "05_platform_adapters"
    return {path.parent.name: path for path in sorted(base.glob("*/adapter.json"))}


def governed(function: Any) -> Any:
    """Serialize one governed mutation against the project control namespace.

    Every mutation is a read-modify-write spanning the ledger head, the ordinal
    counters, and an artifact. Two concurrent processes each read the same head
    and the same ordinal, then each write — producing duplicate sequence
    numbers, a chain that can never verify again, and one artifact silently
    overwriting another. That was reproducible with eight parallel
    ``evidence add`` calls: four records survived of eight, and the chain broke
    permanently. The lock is held for the whole operation, not merely the
    authorization.
    """

    @functools.wraps(function)
    def wrapper(target: Any, *args: Any, **kwargs: Any) -> Any:
        control = target.control if isinstance(target, Project) else Path(target) / CONTROL_DIR
        with exclusive_lock(control):
            return function(target, *args, **kwargs)

    return wrapper


def authorize(project: Project, command: str, actor: str = "unknown_actor") -> Any:
    """Authorize a command against the rail and emit the governed decision.

    ``ABS.IFACE.RUNTIME.EXECUTE`` is declared *provided* by
    ``ABS.MODULE.RUNTIME.EXECUTOR``. Authorization is the operation that
    interface describes, so every decision — permitted or refused — is emitted
    here as a conforming instance. A refusal is emitted before the exception
    propagates, because a control that leaves no record of what it refused
    cannot be audited.
    """
    from .errors import RailViolationError

    context = project.rail_context()
    tree = context.get("tree_identity")
    namespace = (context.get("project_id") or "ABS.PROJECT.UNKNOWN").split(".")[-1]

    def _emit(step: Any, permitted: bool, reason: str) -> None:
        if not project.installed:
            return  # no control namespace yet to record into
        emit_interface_instance(
            project.path("interfaces"),
            "runtime_execute",
            {
                "schema_version": "1.0.0",
                "interface_id": "ABS.IFACE.RUNTIME.EXECUTE",
                "request_id": f"ABS.REQUEST.{command.upper().replace(' ', '_').replace('-', '_')}",
                "scope_id": f"ABS.SCOPE.{namespace}.RUNTIME",
                "actor_id": actor_id(actor),
                "authority_ref": context.get("project_id") or "ABS.AUTHORITY.PROJECT",
                "candidate_hash": f"sha256:{tree}" if tree else "sha256:" + "0" * 64,
                "payload": {"command": command, "reason": reason},
                "result_state": "PASS" if permitted else "BLOCKED",
                "evidence_ids": [],
                "limitations": [
                    "Records the rail decision only; it does not assert the action's outcome."
                ],
                "rail_step_id": getattr(step, "step_id", None) or "S0.READ_ONLY",
                "permitted": permitted,
            },
        )

    try:
        step = check_permitted(command, context)
    except RailViolationError as exc:
        _emit(None, False, exc.reason)
        raise
    _emit(step, True, "permitted by the rail")
    return step


def _next_ordinal(project: Project, state: dict[str, Any], key: str, directory: str) -> int:
    """Allocate an id ordinal that cannot collide with a record already on disk.

    The state counter alone is not safe. Artifacts are written *before* the
    ledger entry and the state update, so a process that dies mid-operation
    leaves a durable record while the counter still points at it. The next run
    would then reuse the id, overwrite that record, and leave the ledger
    asserting a fact about a file that no longer says it — a false claim
    produced by the runtime itself. Taking the maximum of the counter and what
    is actually on disk makes reuse impossible.
    """
    counter = int(state.get(key, 1) or 1)
    highest = 0
    folder = project.path(directory)
    if folder.is_dir():
        for path in folder.glob("*.json"):
            match = re.search(r"(\d+)$", path.stem)
            if match:
                highest = max(highest, int(match.group(1)))
    return max(counter, highest + 1)


# --------------------------------------------------------------------- init


@governed
def init(
    root: Path,
    *,
    project_slug: str,
    mission: str,
    profile: str,
    adapter: str,
    actor: str,
) -> dict[str, Any]:
    """Install the control namespace. This is the only command that may run
    against an uninstalled directory."""
    project = Project(root)
    if project.installed:
        raise AlreadyInstalledError(f"a control namespace already exists at {project.control}")
    resolved = Path(root).resolve()
    if resolved == FRAMEWORK_ROOT or FRAMEWORK_ROOT in resolved.parents or resolved in FRAMEWORK_ROOT.parents:
        raise AuthorityError(
            f"refusing to install into {resolved}: it is the framework release tree at {FRAMEWORK_ROOT} "
            "(or contains it). ABS.CFG.RELEASE.SOURCE_TREE_MUTATION is false — the framework may not "
            "write project state into the payload whose exact identity it publishes. "
            "Run 'absolute init' from the project directory instead, with --root pointing at it."
        )
    if not SLUG_PATTERN.match(project_slug):
        raise SchemaError(
            f"project slug {project_slug!r} must be lowercase alphanumeric with - or _, 2-63 characters"
        )
    if not mission.strip():
        raise GoalLockError("a mission statement is required; the goal lock has nothing to bind to without one")

    profiles = available_profiles()
    if profile not in profiles:
        raise SchemaError(f"unknown profile {profile!r}; available: {sorted(profiles)}")
    adapters = available_adapters()
    if adapter not in adapters:
        raise SchemaError(f"unknown adapter {adapter!r}; available: {sorted(adapters)}")

    authorize(project, "init", actor)

    namespace = slug_to_namespace(project_slug)
    project_id = f"ABS.PROJECT.{namespace}"
    now = utc_now()

    for name in SUBDIRECTORIES:
        project.path(name).mkdir(parents=True, exist_ok=True)

    profile_record = read_json(profiles[profile])
    adapter_record = read_json(adapters[adapter])

    identity = {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "project_slug": project_slug,
        "namespace": namespace,
        "mission": mission.strip(),
        "created_at": now,
        "created_by": actor,
        "framework": framework_identity(),
        "profile": {"id": profile_record.get("profile_id"), "name": profile, "source": f"06_project_profiles/{profile}"},
        "adapter": {"id": adapter_record.get("adapter_id"), "name": adapter, "source": f"05_platform_adapters/{adapter}"},
        "identity_rule": (
            "Project identity is frozen at install. Changing it creates a new project, "
            "never a renamed one, because every stamped identity below binds to it."
        ),
    }
    atomic_write_json(project.control / "identity.json", identity)
    atomic_write_json(project.path("profile.json"), {"profile": profile_record, "adapter": adapter_record})

    state = {
        "schema_version": "1.0.0",
        "framework_id": identity["framework"]["framework_id"],
        "project_id": project_id,
        "active_goal_id": None,
        "phase": "DISCOVERY",
        "active_work_packet": None,
        "candidate_hash": None,
        "status": "ACTIVE",
        "rollback_ref": None,
        "second_pass_identity": None,
        "verified_identity": None,
        "released_identity": None,
        "next_work_packet_ordinal": 1,
        "next_evidence_ordinal": 1,
        "next_gate_ordinal": 1,
        "next_session_ordinal": 1,
        "updated_at": now,
    }
    project.save_state(state)

    atomic_write(
        project.control / "README.md",
        "# Absolute control namespace\n\n"
        "This directory is the governed state of this project. It is written by the `absolute`\n"
        "runtime and is not intended to be edited by hand.\n\n"
        "- `identity.json` — frozen project identity and the framework release that installed it.\n"
        "- `state.json` — current lifecycle state.\n"
        "- `truth/LEDGER.jsonl` — append-only, hash-chained source of truth.\n"
        "- `truth/anchors/` — detached receipts that detect a full-chain rewrite.\n"
        "- `documents/` — governed document packages.\n"
        "- `work/`, `evidence/`, `gates/`, `sessions/`, `decisions/` — durable registries.\n\n"
        "Run `absolute next` to see the single action the rail permits right now.\n",
    )

    tree = project.tree_identity()
    project.ledger.append(
        action="INSTALL",
        subject_type="project",
        subject_id=project_id,
        actor=actor,
        content_sha256=tree,
        state_after="DISCOVERY",
        authority_ref=identity["framework"]["release_id"],
        detail={
            "mission": identity["mission"],
            "profile": profile,
            "adapter": adapter,
            "framework_release": identity["framework"]["release_id"],
        },
    )
    state["candidate_hash"] = f"sha256:{tree}"
    state["updated_at"] = utc_now()
    project.save_state(state)
    project.ledger.anchor(actor, "install")
    return {"project_id": project_id, "control": str(project.control), "tree_identity": tree}


# --------------------------------------------------------------------- goal


@governed
def set_goal(project: Project, *, goal_id: str | None, statement: str, actor: str) -> dict[str, Any]:
    project.require_installed()
    authorize(project, "goal set", actor)
    identity = project.identity()
    goal_id = goal_id or f"ABS.GOAL.{identity['namespace']}.PRIMARY"
    if not valid_id(goal_id):
        raise SchemaError(f"goal id {goal_id!r} must match ABS.<UPPER.DOT.ID>")
    if not statement.strip():
        raise GoalLockError("a goal statement is required; 'done' must be stated before work is permitted")

    state = project.state()
    before = state.get("active_goal_id")
    goal = {
        "schema_version": "1.0.0",
        "goal_id": goal_id,
        "project_id": identity["project_id"],
        "statement": statement.strip(),
        "mission": identity["mission"],
        "declared_at": utc_now(),
        "declared_by": actor,
        "status": "LOCKED",
    }
    atomic_write_json(project.path("goal.json"), goal)
    project.ledger.append(
        action="GOAL_SET",
        subject_type="goal",
        subject_id=goal_id,
        actor=actor,
        content_sha256=sha256_obj(goal),
        state_before=before,
        state_after="LOCKED",
        authority_ref=identity["project_id"],
        detail={"statement": goal["statement"]},
    )
    state["active_goal_id"] = goal_id
    state["updated_at"] = utc_now()
    project.save_state(state)
    return goal


# ------------------------------------------------------------- work packets


@governed
def new_work_packet(
    project: Project,
    *,
    objective: str,
    rollback: str,
    actor: str,
    acceptance: list[str] | None = None,
) -> dict[str, Any]:
    project.require_installed()
    authorize(project, "wp new", actor)
    identity = project.identity()
    state = project.state()

    if not state.get("active_goal_id"):
        raise GoalLockError("no active goal; a work packet with no upward goal link is rejected")
    if not objective.strip():
        raise SchemaError("an objective is required")
    if not rollback.strip():
        raise SchemaError(
            "a rollback statement is required; work that cannot be undone is not a bounded reversible unit"
        )

    ordinal = _next_ordinal(project, state, "next_work_packet_ordinal", "work")
    packet_id = f"ABS.WP.{identity['namespace']}.{ordinal:04d}"
    packet = {
        "schema_version": "1.0.0",
        "work_packet_id": packet_id,
        "objective": objective.strip(),
        "parent_goal": state["active_goal_id"],
        "scope_ids": [f"ABS.SCOPE.{identity['namespace']}.{ordinal:04d}"],
        "inputs": [],
        "outputs": [],
        "requirements": [],
        "permissions": {"read": ["project repository"], "write": [CONTROL_DIR], "external": [], "destructive": False},
        "capabilities_required": ["filesystem"],
        "dependencies": [],
        "rollback": rollback.strip(),
        "acceptance_criteria": acceptance or ["deterministic validation passes", "limitations recorded"],
        "checks": ["schema validation", "rail order", "ledger chain"],
        "evidence_expected": [],
        "owner_role": actor,
        "independent_verifier_role": "fresh_semantic_verifier",
        "status": "READY",
        "opened_at": utc_now(),
        "closed_at": None,
        "exact_next_action": "Author or advance the governed documents this packet covers.",
    }
    atomic_write_json(project.path("work", f"{packet_id}.json"), packet)
    project.ledger.append(
        action="WORK_PACKET_CREATED",
        subject_type="work_packet",
        subject_id=packet_id,
        actor=actor,
        content_sha256=sha256_obj(packet),
        state_after="READY",
        authority_ref=state["active_goal_id"],
        detail={"objective": packet["objective"], "rollback": packet["rollback"]},
    )
    state["active_work_packet"] = packet_id
    state["next_work_packet_ordinal"] = ordinal + 1
    state["rollback_ref"] = packet["rollback"]
    state["updated_at"] = utc_now()
    project.save_state(state)
    return packet


@governed
def complete_work_packet(project: Project, *, packet_id: str | None, actor: str) -> dict[str, Any]:
    project.require_installed()
    authorize(project, "wp complete", actor)
    state = project.state()
    packet_id = packet_id or state.get("active_work_packet")
    path = project.path("work", f"{packet_id}.json")
    if not path.is_file():
        raise SchemaError(f"unknown work packet: {packet_id}")
    packet = read_json(path)
    if packet["status"] == "COMPLETED":
        raise SchemaError(f"{packet_id} is already completed")

    tree = project.tree_identity()
    gates = [
        item
        for item in project.gate_reports()
        if item.get("decision") == "PASS" and item.get("candidate_hash") == f"sha256:{tree}"
    ]
    if not gates:
        raise EvidenceError(
            f"cannot complete {packet_id}: no gate has passed against the current identity sha256:{tree[:16]}…. "
            "Record evidence and run the gate first."
        )

    before = packet["status"]
    packet["status"] = "COMPLETED"
    packet["closed_at"] = utc_now()
    packet["evidence_expected"] = sorted({eid for gate in gates for eid in gate.get("evidence_ids", [])})
    packet["exact_next_action"] = "Checkpoint the session."
    atomic_write_json(path, packet)
    project.ledger.append(
        action="WORK_PACKET_TRANSITION",
        subject_type="work_packet",
        subject_id=packet_id,
        actor=actor,
        content_sha256=sha256_obj(packet),
        state_before=before,
        state_after="COMPLETED",
        authority_ref=state.get("active_goal_id"),
        evidence_ids=packet["evidence_expected"],
        detail={"gate_ids": [gate["gate_id"] for gate in gates]},
    )
    remaining = [item for item in project.work_packets() if item.get("status") not in {"COMPLETED", "CANCELLED"}]
    state["active_work_packet"] = remaining[0]["work_packet_id"] if remaining else None
    state["updated_at"] = utc_now()
    project.save_state(state)
    return packet


# ----------------------------------------------------------------- evidence


@governed
def add_evidence(
    project: Project,
    *,
    method: str,
    result: str,
    actor: str,
    supports: list[str] | None = None,
    raw_output: str | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    project.require_installed()
    authorize(project, "evidence add", actor)
    if result not in RESULT_STATES:
        raise EvidenceError(f"result must be one of {list(RESULT_STATES)}; got {result!r}")
    if not method.strip():
        raise EvidenceError("a method is required; evidence with no stated method is not reproducible")

    identity = project.identity()
    state = project.state()
    ordinal = _next_ordinal(project, state, "next_evidence_ordinal", "evidence")
    evidence_id = f"ABS.EVIDENCE.{identity['namespace']}.{ordinal:04d}"
    tree = project.tree_identity()
    supports = supports or ([state["active_work_packet"]] if state.get("active_work_packet") else [])

    record = {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "supports": supports,
        "producer": actor,
        "independent_verifier": None,
        "method": method.strip(),
        "environment": {"runtime": RUNTIME_VERSION, "framework": identity["framework"]["release_id"]},
        "candidate_hash": f"sha256:{tree}",
        "inputs": {"project_id": identity["project_id"]},
        "raw_output_location": raw_output,
        "timestamp": utc_now(),
        "result": result,
        "expected_result": "The stated method reproduces this result against the same candidate hash.",
        "limitations": limitations or ["Recorded by the producing actor; not independently reproduced."],
        "reproduction": [method.strip()],
        "invalidation_trigger": "Any change to the project tree identity invalidates this record.",
        "classification": "INTERNAL",
    }
    atomic_write_json(project.path("evidence", f"{evidence_id}.json"), record)
    project.ledger.append(
        action="EVIDENCE_RECORDED",
        subject_type="evidence",
        subject_id=evidence_id,
        actor=actor,
        content_sha256=sha256_obj(record),
        state_after=result,
        authority_ref=state.get("active_work_packet"),
        evidence_ids=[evidence_id],
        detail={"method": record["method"], "result": result},
    )
    state["next_evidence_ordinal"] = ordinal + 1
    state["updated_at"] = utc_now()
    project.save_state(state)
    return record


# --------------------------------------------------------------------- gate


@governed
def run_gate(project: Project, *, gate_id: str | None, actor: str, required_checks: list[str] | None = None) -> dict[str, Any]:
    """Evaluate the evidence gate against the *current* identity.

    A gate decision is only ever computed from evidence whose ``candidate_hash``
    equals the identity being decided. Evidence recorded against an older tree is
    counted as ``stale`` and forces a non-PASS decision — this is the control
    that stops a passing result from surviving a change it never saw.
    """
    project.require_installed()
    authorize(project, "gate run", actor)
    identity = project.identity()
    state = project.state()
    tree = project.tree_identity()
    bound = f"sha256:{tree}"

    ordinal = _next_ordinal(project, state, "next_gate_ordinal", "gates")
    gate_id = gate_id or f"ABS.GATE.{identity['namespace']}.{ordinal:02d}"
    if not valid_id(gate_id):
        raise SchemaError(f"gate id {gate_id!r} must match ABS.<UPPER.DOT.ID>")

    records = project.evidence_records()
    if not records:
        raise EvidenceError("no evidence exists; a gate with no evidence cannot produce PASS")

    current = [item for item in records if item.get("candidate_hash") == bound]
    older = [item for item in records if item.get("candidate_hash") != bound]

    # An older record is *superseded* when the same method has been re-run
    # against the current identity, and *stale* when it has not. The
    # distinction matters: treating every historical record as blocking would
    # make a gate unpassable forever after the first tree change, while
    # ignoring them all would let coverage silently disappear — a check that
    # once ran, then stopped running, would look identical to one that never
    # existed. Only genuinely unrepeated coverage blocks.
    current_methods = {item.get("method") for item in current}
    superseded = [item for item in older if item.get("method") in current_methods]
    stale = [item for item in older if item.get("method") not in current_methods]

    counts = {
        "pass": sum(1 for item in current if item["result"] == "PASS"),
        "fail": sum(1 for item in current if item["result"] == "FAIL"),
        "blocked": sum(1 for item in current if item["result"] == "BLOCKED"),
        "not_run": sum(1 for item in current if item["result"] == "NOT_RUN"),
        "inconclusive": sum(1 for item in current if item["result"] == "INCONCLUSIVE"),
        "stale": len(stale),
        "superseded": len(superseded),
    }
    findings: list[dict[str, Any]] = []
    if not current:
        findings.append({"code": "GATE_NO_CURRENT_EVIDENCE", "message": "all evidence predates the current identity"})
    for item in stale:
        findings.append(
            {
                "code": "GATE_STALE_EVIDENCE",
                "evidence_id": item["evidence_id"],
                "message": (
                    f"method {item.get('method')!r} was last run against {item.get('candidate_hash')} "
                    f"and has not been repeated against {bound}"
                ),
            }
        )
    for item in superseded:
        findings.append(
            {
                "code": "GATE_EVIDENCE_SUPERSEDED",
                "evidence_id": item["evidence_id"],
                "message": f"superseded by a current run of the same method; not blocking",
                "informational": True,
            }
        )

    blocking = (
        counts["fail"] + counts["blocked"] + counts["not_run"] + counts["inconclusive"] + counts["stale"]
    )
    decision = "PASS" if counts["pass"] > 0 and blocking == 0 else ("FAIL" if counts["fail"] else "BLOCKED")

    report = {
        "schema_version": "1.0.0",
        "gate_id": gate_id,
        "scope": [f"ABS.SCOPE.{identity['namespace']}.RELEASE"],
        "candidate_hash": bound,
        "required_checks": required_checks or ["evidence bound to current identity", "no blocking result"],
        "checks_run": required_checks or ["evidence bound to current identity", "no blocking result"],
        "counts": counts,
        "evidence_ids": sorted(item["evidence_id"] for item in current),
        "findings": findings,
        "waivers": [],
        "verifier": actor,
        "decision": decision,
        "evaluated_at": utc_now(),
        "rationale": (
            f"{counts['pass']} passing evidence record(s) bound to {bound} and no blocking result."
            if decision == "PASS"
            else f"Blocking results present: {counts}."
        ),
    }
    atomic_write_json(project.path("gates", f"{gate_id}.json"), report)
    project.ledger.append(
        action="GATE_EVALUATED",
        subject_type="gate",
        subject_id=gate_id,
        actor=actor,
        content_sha256=sha256_obj(report),
        state_after=decision,
        authority_ref=state.get("active_work_packet"),
        evidence_ids=report["evidence_ids"],
        detail={"counts": counts, "decision": decision},
    )
    state["next_gate_ordinal"] = ordinal + 1
    state["candidate_hash"] = bound
    state["updated_at"] = utc_now()
    project.save_state(state)
    return report


# ---------------------------------------------------------------- documents


@governed
def new_document(
    project: Project,
    *,
    doc_id: str,
    title: str,
    question: str,
    actor: str,
    requirement_statements: list[str] | None = None,
    states: list[str] | None = None,
    primary_failure: str | None = None,
    provided: list[str] | None = None,
    consumed: list[str] | None = None,
    source_evidence: list[str] | None = None,
    excludes: list[str] | None = None,
) -> dict[str, Any]:
    project.require_installed()
    authorize(project, "doc new", actor)
    if not SLUG_PATTERN.match(doc_id):
        raise SchemaError(f"document id {doc_id!r} must be lowercase alphanumeric with - or _, 2-63 characters")
    directory = project.path("documents", doc_id)
    if directory.exists():
        raise SchemaError(f"document {doc_id!r} already exists at {directory}")
    if not question.strip().endswith("?"):
        raise SchemaError(
            "a document must answer exactly one question; the --question value must end with '?'"
        )

    # Every authoring step generates its artifacts from what was declared here,
    # and `seal` refuses while a single template marker remains. Accepting a
    # `doc new` that omits the author-specific content therefore creates a
    # package that can never be sealed, and the rail cannot advance past a
    # document it cannot seal. That combination bricked the project: the one
    # action `absolute next` permitted was the one action that could not
    # succeed. The inputs the seal will demand are demanded here instead, where
    # refusing is free.
    missing = [
        name
        for name, value in (
            ("--requirement", requirement_statements),
            ("--failure", (primary_failure or "").strip() or None),
            ("--source-evidence", source_evidence),
            ("--excludes", excludes),
        )
        if not value
    ]
    if missing:
        raise SchemaError(
            f"document {doc_id!r} is missing author-specific content: {', '.join(missing)}. "
            "Each one becomes template text that 'absolute doc seal' refuses, and a document "
            "that cannot be sealed stops the rail permanently. Supply them now, for example:\n"
            f"  absolute doc new --id {doc_id} --title {title.strip()!r} --question {question.strip()!r} \\\n"
            '    --requirement "<the first normative rule this package owns>" \\\n'
            '    --requirement "<the second normative rule this package owns>" \\\n'
            '    --failure "<the single worst thing this package must prevent>" \\\n'
            '    --source-evidence "<the raw source this package\'s truth derives from>" \\\n'
            '    --excludes "<something this package deliberately does not own>"'
        )

    identity = project.identity()
    namespace = identity["namespace"]
    concept = doc_id.upper().replace("-", "_")
    statements = requirement_statements or [
        f"<<TODO: state the first normative rule this package owns>>",
        f"<<TODO: state the second normative rule this package owns>>",
    ]
    requirements = [
        {"requirement_id": f"ABS.REQ.{namespace}.{concept}.{index:03d}", "level": "MUST", "statement": statement}
        for index, statement in enumerate(statements, 1)
    ]
    unknown = (set(provided or []) | set(consumed or [])) - known_interfaces()
    if unknown:
        raise SchemaError(f"unresolvable interfaces {sorted(unknown)}; declare only registry-known interface IDs")

    record = {
        "schema_version": "1.0.0",
        "doc_id": doc_id,
        "module_id": f"ABS.MODULE.{namespace}.{concept}",
        "concept_id": f"ABS.CONCEPT.{namespace}.{concept}",
        "scope_id": f"ABS.SCOPE.{namespace}.{concept}",
        "namespace": namespace,
        "project_id": identity["project_id"],
        "title": title.strip(),
        "question": question.strip(),
        "version": "1.0.0",
        "status": "DRAFT",
        # The schema-governed manifest field is the version string, not the
        # release id; both are kept so a package traces to its exact release.
        "framework_release": identity["framework"]["version"],
        "framework_release_id": identity["framework"]["release_id"],
        "requirements": requirements,
        "states": states or ["DRAFT", "CANDIDATE", "VERIFIED", "CERTIFIED", "SUPERSEDED"],
        "primary_failure": (primary_failure or "<<TODO: name the single worst thing this package must prevent>>").rstrip() + ("" if (primary_failure or "").endswith(".") else "."),
        "provided_interfaces": provided or [],
        "consumed_interfaces": consumed or [],
        "dependencies": [],
        "classification": "INTERNAL",
        "allowed_audiences": ["INTERNAL"],
        "gate_ids": [],
        "source_evidence": source_evidence or [],
        "excludes": excludes or [],
        "owner": actor,
        "created_at": utc_now(),
        "created_by": actor,
        "completed_steps": [],
        "sealed_at": None,
        "seal_sha256": None,
    }
    directory.mkdir(parents=True, exist_ok=True)
    atomic_write_json(directory / "document.json", record)
    project.ledger.append(
        action="DOCUMENT_CREATED",
        subject_type="document",
        subject_id=record["module_id"],
        actor=actor,
        content_sha256=sha256_obj(record),
        state_after="DRAFT",
        authority_ref=project.state().get("active_work_packet"),
        detail={"doc_id": doc_id, "title": record["title"], "question": record["question"]},
    )
    return record


@governed
def step_document(project: Project, *, doc_id: str, actor: str) -> dict[str, Any]:
    """Advance one authoring step, generating that step's artifacts."""
    project.require_installed()
    authorize(project, "doc step", actor)
    directory = project.path("documents", doc_id)
    record_path = directory / "document.json"
    if not record_path.is_file():
        raise SchemaError(f"unknown document: {doc_id}")
    record = read_json(record_path)

    step = next_document_step(record)
    if step is None:
        raise DocumentStepError(
            f"{doc_id} has completed all {TOTAL_STEPS} authoring steps; the next action is 'absolute doc seal'"
        )

    written = GENERATORS[step.step_id](record)
    for relative, text in written.items():
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, text)
    if step.step_id == "D6.VISUAL":
        render_svg(directory)

    missing = [item for item in step.artifacts if not (directory / item).is_file()]
    if missing:
        raise DocumentStepError(f"{step.step_id} did not produce {missing}")

    record["completed_steps"] = list(record.get("completed_steps", [])) + [step.step_id]
    record["status"] = "CANDIDATE" if len(record["completed_steps"]) == TOTAL_STEPS else "DRAFT"
    atomic_write_json(record_path, record)

    project.ledger.append(
        action="DOCUMENT_STEP_COMPLETED",
        subject_type="document",
        subject_id=record["module_id"],
        actor=actor,
        content_sha256=sha256_obj(record),
        state_before=f"{len(record['completed_steps']) - 1}/{TOTAL_STEPS}",
        state_after=f"{len(record['completed_steps'])}/{TOTAL_STEPS}",
        authority_ref=project.state().get("active_work_packet"),
        detail={"step_id": step.step_id, "artifacts": list(step.artifacts)},
    )
    following = next_document_step(record)
    return {
        "doc_id": doc_id,
        "completed_step": step.step_id,
        "artifacts": sorted(written) + (["blueprint/architecture.svg"] if step.step_id == "D6.VISUAL" else []),
        "remaining": TOTAL_STEPS - len(record["completed_steps"]),
        "next_step": None
        if following is None
        else {"step_id": following.step_id, "title": following.title, "intent": following.intent},
        "unresolved_markers": len(scan_todos(directory)),
    }


def check_document(project: Project, *, doc_id: str) -> dict[str, Any]:
    project.require_installed()
    directory = project.path("documents", doc_id)
    record_path = directory / "document.json"
    if not record_path.is_file():
        raise SchemaError(f"unknown document: {doc_id}")
    record = read_json(record_path)
    findings = validate_document(directory, record, known_interfaces())
    return {
        "doc_id": doc_id,
        "module_id": record["module_id"],
        "status": record["status"],
        "steps_completed": len(record.get("completed_steps", [])),
        "steps_total": TOTAL_STEPS,
        "finding_count": len(findings),
        "findings": findings,
        "result": "PASS" if not findings else "FAIL",
    }


@governed
def seal_document(project: Project, *, doc_id: str, actor: str) -> dict[str, Any]:
    """Validate, freeze, and stamp a document into the source of truth.

    Sealing is the moment a document acquires an identity that later claims can
    bind to, so it is the strictest checkpoint in the runtime: all steps done,
    zero findings, zero unresolved markers.
    """
    project.require_installed()
    authorize(project, "doc seal", actor)
    directory = project.path("documents", doc_id)
    record_path = directory / "document.json"
    if not record_path.is_file():
        raise SchemaError(f"unknown document: {doc_id}")
    record = read_json(record_path)

    done = len(record.get("completed_steps", []))
    if done != TOTAL_STEPS:
        pending = next_document_step(record)
        raise DocumentStepError(
            f"{doc_id} has completed {done}/{TOTAL_STEPS} authoring steps. "
            f"Next required step: {pending.step_id} — {pending.title}."
        )

    findings = validate_document(directory, record, known_interfaces())
    if findings:
        summary = "; ".join(f"{item['code']} at {item['path']}" for item in findings[:5])
        raise DocumentStepError(
            f"{doc_id} cannot be sealed: {len(findings)} finding(s). {summary}"
            + ("" if len(findings) <= 5 else f" (+{len(findings) - 5} more)")
        )

    seal, records = sha256_tree(directory, exclude={"document.json"})
    record["status"] = "SEALED"
    record["sealed_at"] = utc_now()
    record["seal_sha256"] = seal
    record["sealed_artifacts"] = records
    atomic_write_json(record_path, record)

    project.ledger.append(
        action="DOCUMENT_STAMPED",
        subject_type="document",
        subject_id=record["module_id"],
        actor=actor,
        content_sha256=seal,
        state_before="CANDIDATE",
        state_after="SEALED",
        authority_ref=project.state().get("active_work_packet"),
        detail={"doc_id": doc_id, "artifact_count": len(records), "seal_sha256": seal},
    )
    return {"doc_id": doc_id, "module_id": record["module_id"], "seal_sha256": seal, "artifact_count": len(records)}


@governed
def abandon_document(project: Project, *, doc_id: str, reason: str, actor: str) -> dict[str, Any]:
    """Close an unfinishable document package truthfully, and record why.

    Without this, any document that cannot be sealed — template text left in
    it, an artifact deleted by hand, a contract that will not validate — halts
    the rail forever, because ``S5``/``S6`` require *every* document to be
    authored and sealed and nothing could remove one. That is work loss: the
    rest of a correct project becomes unreleasable because of one bad package.

    Abandonment is deliberately not deletion. The package stays on disk, the
    act is stamped into the source of truth with its stated reason, a decision
    record is written, and ``status``, the pass-2 review, and the release
    manifest all report it. The framework's rule is that tampering must be
    evident, not impossible; the same applies to giving up on a package.

    A sealed document may not be abandoned. Its identity is already bound into
    later claims, so retracting it would falsify them.
    """
    project.require_installed()
    authorize(project, "doc abandon", actor)
    if not reason.strip():
        raise SchemaError(
            "a reason is required; an abandonment with no stated reason is indistinguishable "
            "from work quietly disappearing"
        )
    directory = project.path("documents", doc_id)
    record_path = directory / "document.json"
    if not record_path.is_file():
        raise SchemaError(f"unknown document: {doc_id}")
    record = read_json(record_path)
    if record.get("status") == "SEALED":
        raise AuthorityError(
            f"{doc_id} is SEALED; its identity is already bound into later claims and cannot be "
            "retracted. Supersede it with a new package instead."
        )
    if record.get("status") == "ABANDONED":
        raise SchemaError(f"{doc_id} is already abandoned")

    before = record.get("status")
    record["status"] = "ABANDONED"
    record["abandoned_at"] = utc_now()
    record["abandoned_by"] = actor
    record["abandon_reason"] = reason.strip()
    atomic_write_json(record_path, record)

    identity = project.identity()
    state = project.state()
    decision_id = f"ABS.DECISION.{identity['namespace']}.{doc_id.upper().replace('-', '_')}.ABANDON"
    decision = {
        "schema_version": "1.0.0",
        "decision_id": decision_id,
        "project_id": identity["project_id"],
        "subject_id": record["module_id"],
        "decision": "ABANDON_DOCUMENT_PACKAGE",
        "rationale": reason.strip(),
        "state_before": before,
        "state_after": "ABANDONED",
        "steps_completed": len(record.get("completed_steps", [])),
        "steps_total": TOTAL_STEPS,
        "decided_by": actor,
        "decided_at": utc_now(),
        "reversible": "Author a replacement package under a new document id.",
    }
    atomic_write_json(project.path("decisions", f"{decision_id}.json"), decision)
    project.ledger.append(
        action="DECISION_RECORDED",
        subject_type="decision",
        subject_id=decision_id,
        actor=actor,
        content_sha256=sha256_obj(decision),
        state_before=before,
        state_after="ABANDONED",
        authority_ref=state.get("active_goal_id"),
        detail={"doc_id": doc_id, "module_id": record["module_id"], "reason": reason.strip()},
    )
    return decision


# --------------------------------------------------------- checkpoint / pass


@governed
def checkpoint(project: Project, *, next_action: str, actor: str, context_status: str = "HEALTHY") -> dict[str, Any]:
    project.require_installed()
    authorize(project, "checkpoint", actor)
    if not next_action.strip():
        raise SchemaError(
            "an exact next action is required; a checkpoint that does not say what to do next is not restart-safe"
        )
    identity = project.identity()
    state = project.state()
    tree = project.tree_identity()
    ordinal = _next_ordinal(project, state, "next_session_ordinal", "sessions")
    session_id = f"ABS.SESSION.{identity['namespace']}.{ordinal:04d}"
    packets = project.work_packets()

    record = {
        "schema_version": "1.0.0",
        "session_id": session_id,
        "program_state_version": "1.0.0",
        "active_work_packet": state.get("active_work_packet"),
        "candidate_hash_before": state.get("candidate_hash"),
        "candidate_hash_after": f"sha256:{tree}",
        "completed_atomic_units": [item["work_packet_id"] for item in packets if item["status"] == "COMPLETED"],
        "partial_units": [item["work_packet_id"] for item in packets if item["status"] not in {"COMPLETED", "CANCELLED"}],
        "files_changed": [],
        "checks_run": [item["gate_id"] for item in project.gate_reports()],
        "failed_or_not_run": [
            item["evidence_id"] for item in project.evidence_records() if item["result"] != "PASS"
        ],
        "findings_opened": [],
        "findings_closed": [],
        "capability_state_changes": [],
        "rollback_point": state.get("rollback_ref"),
        "context_status": context_status,
        "exact_next_packet": state.get("active_work_packet"),
        "exact_first_next_action": next_action.strip(),
        "written_at": utc_now(),
    }
    atomic_write_json(project.path("sessions", f"{session_id}.json"), record)
    project.ledger.append(
        action="CHECKPOINT",
        subject_type="session",
        subject_id=session_id,
        actor=actor,
        content_sha256=sha256_obj(record),
        state_after=context_status,
        authority_ref=state.get("active_work_packet"),
        detail={"exact_first_next_action": record["exact_first_next_action"]},
    )
    state["next_session_ordinal"] = ordinal + 1
    state["candidate_hash"] = f"sha256:{tree}"
    state["updated_at"] = utc_now()
    project.save_state(state)
    project.ledger.anchor(actor, f"checkpoint {session_id}")
    return record


@governed
def second_pass(project: Project, *, reviewer: str, notes: list[str] | None = None) -> dict[str, Any]:
    """Record the pass-2 review of the frozen whole.

    Pass 2 is refused when the reviewer is the same actor that authored the
    material under review. ``ABS.REQ.LIFECYCLE_TWO_PASS.002`` exists to get a
    second set of eyes on a frozen candidate; a self-review satisfies the
    bookkeeping while defeating the control.
    """
    project.require_installed()
    authorize(project, "pass2", reviewer)
    state = project.state()
    tree = project.tree_identity()
    entries = project.ledger.entries()
    authors = {
        item["actor"]
        for item in entries
        if item["action"] in {"DOCUMENT_STEP_COMPLETED", "DOCUMENT_STAMPED", "DOCUMENT_CREATED"}
    }
    # Compared on the normalized identity, not the raw string. 'alice' authoring
    # and 'Alice' reviewing is the same person defeating the control by typing.
    if normalize_actor(reviewer) in {normalize_actor(item) for item in authors}:
        raise AuthorityError(
            f"'{reviewer}' authored material in this candidate and cannot also be its pass-2 reviewer. "
            f"Authors on record: {sorted(authors)}."
        )

    every = project.documents()
    abandoned = [item for item in every if item.get("status") == "ABANDONED"]
    docs = [item for item in every if item.get("status") != "ABANDONED"]
    unsealed = [item["doc_id"] for item in docs if item.get("status") != "SEALED"]
    if unsealed:
        raise DocumentStepError(f"the whole is not frozen; unsealed documents: {unsealed}")
    if not docs:
        raise DocumentStepError(
            "every document package in this candidate was abandoned; there is no frozen whole to review"
        )

    review = {
        "schema_version": "1.0.0",
        "pass": 2,
        "reviewer": reviewer,
        "reviewed_identity": f"sha256:{tree}",
        "document_count": len(docs),
        "document_seals": {item["doc_id"]: item.get("seal_sha256") for item in docs},
        # Abandonment is part of what pass 2 reviews. A package dropped from the
        # candidate is a decision the reviewer must see, not a gap to hide.
        "abandoned_documents": [
            {"doc_id": item["doc_id"], "reason": item.get("abandon_reason"), "by": item.get("abandoned_by")}
            for item in abandoned
        ],
        "notes": notes or [],
        "reviewed_at": utc_now(),
        "scope": "frozen whole: every sealed document, the ledger chain, and the recorded gate decisions",
    }
    atomic_write_json(project.path("reports", "SECOND_PASS_REVIEW.json"), review)
    project.ledger.append(
        action="PHASE_TRANSITION",
        subject_type="phase",
        subject_id="SECOND_PASS",
        actor=reviewer,
        content_sha256=sha256_obj(review),
        state_before="CANDIDATE",
        state_after="SECOND_PASS",
        authority_ref=state.get("active_goal_id"),
        detail={
            "reviewed_identity": review["reviewed_identity"],
            "document_count": len(docs),
            "abandoned_document_count": len(abandoned),
        },
    )
    state["second_pass_identity"] = tree
    state["updated_at"] = utc_now()
    project.save_state(state)
    return review


@governed
def record_verification(project: Project, *, report: dict[str, Any], actor: str) -> dict[str, Any]:
    """Bind a deep-verification result to the identity it was computed against.

    A verification that did not pass is still recorded — suppressing it would
    make the absence of a record indistinguishable from a clean run — but it
    does not advance the rail.
    """
    project.require_installed()
    # S12 is a rail step like any other. Recording a verification without
    # authorizing it let the terminal steps be satisfied out of order, which is
    # the one thing the rail exists to make impossible.
    authorize(project, "verify --record", actor)
    state = project.state()
    tree = project.tree_identity()
    if report.get("verified_identity") != tree:
        raise EvidenceError(
            "the verification report was computed against a different identity than the current tree; rerun it"
        )
    atomic_write_json(project.path("reports", "DEEP_VERIFICATION.json"), report)
    project.ledger.append(
        action="VERIFICATION_RUN",
        subject_type="verification",
        subject_id=f"ABS.VERIFY.{tree[:16]}",
        actor=actor,
        content_sha256=sha256_obj(report),
        state_after=report.get("status"),
        authority_ref=state.get("active_goal_id"),
        detail={"status": report.get("status"), "finding_count": report.get("finding_count")},
    )
    if report.get("status") == "PASS":
        state["verified_identity"] = tree
        state["updated_at"] = utc_now()
        project.save_state(state)
    return report


@governed
def assemble_release(project: Project, *, output: Path, actor: str) -> dict[str, Any]:
    """Produce the shippable artifact and stamp its exact identity.

    This never emits a certification claim. The framework's own configuration
    registry fixes ``ABS.CFG.RELEASE.SELF_CERTIFICATION`` to ``false``: the party
    that builds an artifact may not also declare it certified.
    """
    import zipfile

    project.require_installed()
    authorize(project, "release", actor)
    identity = project.identity()
    state = project.state()
    tree = project.tree_identity()

    if state.get("verified_identity") != tree:
        raise EvidenceError("release requires a recorded deep verification bound to the current identity")

    output = Path(output).resolve()
    try:
        output.relative_to(project.root)
    except ValueError:
        pass
    else:
        raise AuthorityError("the release artifact must be written outside the project tree it describes")
    if output.exists():
        raise AuthorityError(f"overwrite denied: {output} already exists")

    files = sorted(
        (path for path in project.root.rglob("*") if path.is_file()),
        key=lambda item: item.relative_to(project.root).as_posix().casefold(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    root_name = identity["project_slug"]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(project.root).as_posix()
            info = zipfile.ZipInfo(f"{root_name}/{relative}", (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o644 & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    digest = sha256_path(output)
    output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")

    manifest = {
        "schema_version": "1.0.0",
        "project_id": identity["project_id"],
        "release_identity": f"sha256:{tree}",
        "artifact": output.name,
        "artifact_sha256": digest,
        "artifact_bytes": output.stat().st_size,
        "member_count": len(files),
        "framework": identity["framework"],
        "assembled_at": utc_now(),
        "assembled_by": actor,
        "abandoned_documents": [
            {"doc_id": item["doc_id"], "reason": item.get("abandon_reason")}
            for item in project.documents()
            if item.get("status") == "ABANDONED"
        ],
        "certification": {
            "self_certification": False,
            "independent_status": "PENDING_EXTERNAL_EXACT_HASH_REVIEW",
            "rule": "The party that assembles an artifact may not declare it certified.",
        },
    }
    atomic_write_json(project.path("reports", "RELEASE_MANIFEST.json"), manifest)
    project.ledger.append(
        action="RELEASE_ASSEMBLED",
        subject_type="release",
        subject_id=f"ABS.RELEASE.{identity['namespace']}",
        actor=actor,
        content_sha256=digest,
        state_before="INDEPENDENT_REVIEW",
        state_after="RELEASED",
        authority_ref=state.get("active_goal_id"),
        detail={"artifact": output.name, "artifact_sha256": digest, "release_identity": tree},
    )
    state["released_identity"] = tree
    state["phase"] = "RELEASED"
    state["updated_at"] = utc_now()
    project.save_state(state)
    project.ledger.anchor(actor, "release")
    return manifest
