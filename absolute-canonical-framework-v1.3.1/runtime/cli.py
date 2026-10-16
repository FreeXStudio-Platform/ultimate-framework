"""``absolute`` command line interface.

Output contract: every command prints either a human summary (default) or a
single JSON object (``--json``). Exit codes are typed — see ``runtime.errors`` —
so a wrapper script or CI job can branch on the *reason* a command refused,
not on parsed text.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from . import RUNTIME_VERSION
from .documents import DOCUMENT_STEPS, TOTAL_STEPS, next_document_step
from .errors import AbsoluteError
from .project import Project
from .rail import RAIL_STEPS, describe
from . import engine


def _actor(args: argparse.Namespace) -> str:
    return args.actor or os.environ.get("ABSOLUTE_ACTOR") or os.environ.get("USER") or "unknown_actor"


def _emit(args: argparse.Namespace, payload: dict[str, Any], human: str) -> int:
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(human)
    return 0


def _project(args: argparse.Namespace) -> Project:
    return Project.discover(Path(args.root or "."))


# --------------------------------------------------------------- commands


def cmd_init(args: argparse.Namespace) -> int:
    result = engine.init(
        Path(args.root or "."),
        project_slug=args.project,
        mission=args.mission,
        profile=args.profile,
        adapter=args.adapter,
        actor=_actor(args),
    )
    project = Project(Path(args.root or "."))
    rail = describe(project.rail_context())
    result["next"] = rail["next_step"]
    return _emit(
        args,
        result,
        f"Installed {result['project_id']}\n"
        f"  control namespace : {result['control']}\n"
        f"  tree identity     : sha256:{result['tree_identity']}\n"
        f"  next              : {rail['next_step']['command']}",
    )


def cmd_status(args: argparse.Namespace) -> int:
    project = _project(args)
    if not project.installed:
        return _emit(
            args,
            {"installed": False, "root": str(project.root), "next": "absolute init"},
            f"No Absolute control namespace under {project.root}.\n  next : absolute init --project <slug> "
            '--mission "<mission>" --profile standard --adapter claude_code',
        )
    context = project.rail_context()
    rail = describe(context)
    identity = project.identity()
    chain = project.ledger.verify()
    anchors = project.ledger.verify_anchors()
    payload = {
        "installed": True,
        "project_id": identity["project_id"],
        "mission": identity["mission"],
        "framework": identity["framework"],
        "phase": rail["phase"],
        "tree_identity": f"sha256:{context['tree_identity']}",
        "rail": rail,
        "state_drift": context["state_drift"],
        "counts": {
            "documents": context["document_count"],
            "documents_abandoned": context["documents_abandoned"],
            "documents_sealed": context["documents_sealed"],
            "work_packets": context["work_packets_created"],
            "open_work_packets": context["open_work_packets"],
            "evidence": context["evidence_count"],
            "ledger_entries": chain["entry_count"],
        },
        "truth": {"chain": chain["status"], "anchors": anchors["status"]},
    }
    following = rail["next_step"]
    lines = [
        f"{identity['project_id']}  [{rail['phase']}]",
        f"  mission        : {identity['mission']}",
        f"  framework      : {identity['framework']['release_id']} (runtime {RUNTIME_VERSION})",
        f"  identity       : sha256:{context['tree_identity']}",
        f"  rail           : {rail['completed_step_count']}/{rail['total_step_count']} steps",
        f"  documents      : {context['documents_sealed']} sealed / {context['document_count']} live"
        + (f" ({context['documents_abandoned']} abandoned)" if context["documents_abandoned"] else ""),
        f"  work packets   : {context['open_work_packets']} open / {context['work_packets_created']} total",
        f"  evidence       : {context['evidence_count']}",
        f"  truth ledger   : {chain['status']} ({chain['entry_count']} entries), anchors {anchors['status']}",
    ]
    for drift in context["state_drift"]:
        lines.append(
            f"  RECOVERY       : {drift['registry']} holds {drift['highest_on_disk']} record(s) but "
            f"{drift['counter']} is {drift['recorded_next']} — {drift['meaning']}. "
            "The next id is allocated past it; no record is overwritten."
        )
    if rail["out_of_order_satisfied"]:
        lines.append(f"  WARNING        : out-of-order state detected: {rail['out_of_order_satisfied']}")
    lines.append(
        f"  next           : {following['command']}" if following else "  next           : rail complete"
    )
    return _emit(args, payload, "\n".join(lines))


def cmd_next(args: argparse.Namespace) -> int:
    project = _project(args)
    rail = describe(project.rail_context())
    following = rail["next_step"]
    if following is None:
        return _emit(args, rail, "Rail complete. Open new work with 'absolute wp new' to continue.")
    return _emit(
        args,
        rail,
        f"[{rail['phase']}] step {following['ordinal']}/{rail['total_step_count']} — {following['step_id']}\n"
        f"  {following['title']}\n"
        f"  why : {following['why']}\n"
        f"  run : {following['command']}",
    )


def cmd_explain(args: argparse.Namespace) -> int:
    payload = {
        "rail": [
            {
                "step_id": step.step_id,
                "ordinal": step.ordinal,
                "phase_on_entry": step.phase_on_entry,
                "phase_on_exit": step.phase_on_exit,
                "title": step.title,
                "why": step.why,
                "command": step.guidance,
                "repeatable": step.repeatable,
            }
            for step in RAIL_STEPS
        ],
        "document_steps": [
            {"step_id": step.step_id, "ordinal": step.ordinal, "title": step.title, "intent": step.intent, "artifacts": list(step.artifacts)}
            for step in DOCUMENT_STEPS
        ],
    }
    lines = ["Project rail (enforced order):"]
    for step in RAIL_STEPS:
        lines.append(f"  {step.ordinal:2d}. {step.step_id:<22} {step.title}")
    lines.append("")
    lines.append(f"Document authoring steps (enforced order, {TOTAL_STEPS} per document):")
    for step in DOCUMENT_STEPS:
        lines.append(f"  {step.ordinal:2d}. {step.step_id:<16} {step.title}")
    return _emit(args, payload, "\n".join(lines))


def cmd_goal_set(args: argparse.Namespace) -> int:
    goal = engine.set_goal(_project(args), goal_id=args.id, statement=args.statement, actor=_actor(args))
    return _emit(args, goal, f"Goal locked: {goal['goal_id']}\n  {goal['statement']}")


def cmd_wp_new(args: argparse.Namespace) -> int:
    packet = engine.new_work_packet(
        _project(args), objective=args.objective, rollback=args.rollback, actor=_actor(args)
    )
    return _emit(
        args,
        packet,
        f"Work packet {packet['work_packet_id']} [{packet['status']}]\n"
        f"  objective : {packet['objective']}\n"
        f"  rollback  : {packet['rollback']}",
    )


def cmd_wp_complete(args: argparse.Namespace) -> int:
    packet = engine.complete_work_packet(_project(args), packet_id=args.id, actor=_actor(args))
    return _emit(args, packet, f"Work packet {packet['work_packet_id']} completed.")


def cmd_wp_list(args: argparse.Namespace) -> int:
    packets = _project(args).work_packets()
    lines = [f"  {item['work_packet_id']}  {item['status']:<10} {item['objective']}" for item in packets]
    return _emit(args, {"work_packets": packets}, "\n".join(lines) or "  (none)")


def cmd_doc_new(args: argparse.Namespace) -> int:
    record = engine.new_document(
        _project(args),
        doc_id=args.id,
        title=args.title,
        question=args.question,
        actor=_actor(args),
        requirement_statements=args.requirement or None,
        primary_failure=args.failure,
        provided=args.provides or None,
        consumed=args.consumes or None,
        source_evidence=args.source_evidence or None,
        excludes=args.excludes or None,
    )
    return _emit(
        args,
        record,
        f"Document {record['doc_id']} created as {record['module_id']}\n"
        f"  question : {record['question']}\n"
        f"  next     : absolute doc step --id {record['doc_id']}   (step 1/{TOTAL_STEPS})",
    )


def cmd_doc_step(args: argparse.Namespace) -> int:
    project = _project(args)
    if args.all:
        results = []
        while True:
            record = project.document(args.id)
            if record is None:
                raise engine.SchemaError(f"unknown document: {args.id}")
            if next_document_step(record) is None:
                break
            results.append(engine.step_document(project, doc_id=args.id, actor=_actor(args)))
        payload = {"doc_id": args.id, "steps_run": len(results), "results": results}
        human = "\n".join(f"  {item['completed_step']:<16} {', '.join(item['artifacts'])}" for item in results)
        markers = results[-1]["unresolved_markers"] if results else 0
        human += f"\n  {TOTAL_STEPS}/{TOTAL_STEPS} steps complete; {markers} unresolved marker(s)."
        return _emit(args, payload, human)
    result = engine.step_document(project, doc_id=args.id, actor=_actor(args))
    following = result["next_step"]
    human = (
        f"{result['completed_step']} complete — wrote {', '.join(result['artifacts'])}\n"
        f"  remaining : {result['remaining']} step(s)"
    )
    if following:
        human += f"\n  next      : {following['step_id']} — {following['title']}"
    return _emit(args, result, human)


def cmd_doc_check(args: argparse.Namespace) -> int:
    result = engine.check_document(_project(args), doc_id=args.id)
    lines = [f"{result['doc_id']}  {result['result']}  ({result['steps_completed']}/{result['steps_total']} steps)"]
    for finding in result["findings"]:
        lines.append(f"  {finding['severity']:<6} {finding['code']:<32} {finding['path']}: {finding['message']}")
    return 0 if _emit(args, result, "\n".join(lines)) == 0 and result["result"] == "PASS" else 1


def cmd_doc_seal(args: argparse.Namespace) -> int:
    result = engine.seal_document(_project(args), doc_id=args.id, actor=_actor(args))
    return _emit(
        args,
        result,
        f"Sealed {result['doc_id']} ({result['module_id']})\n"
        f"  seal      : sha256:{result['seal_sha256']}\n"
        f"  artifacts : {result['artifact_count']}\n"
        f"  stamped into the source of truth.",
    )


def cmd_doc_abandon(args: argparse.Namespace) -> int:
    decision = engine.abandon_document(
        _project(args), doc_id=args.id, reason=args.reason, actor=_actor(args)
    )
    return _emit(
        args,
        decision,
        f"Abandoned {decision['subject_id']} at {decision['steps_completed']}/{decision['steps_total']} steps\n"
        f"  reason   : {decision['rationale']}\n"
        f"  recorded : {decision['decision_id']} (stamped into the source of truth)",
    )


def cmd_doc_list(args: argparse.Namespace) -> int:
    docs = _project(args).documents()
    lines = [
        f"  {item['doc_id']:<24} {item['status']:<10} {len(item.get('completed_steps', []))}/{TOTAL_STEPS}  "
        f"{(item.get('seal_sha256') or item.get('abandon_reason') or '-')[:40]}"
        for item in docs
    ]
    return _emit(args, {"documents": docs}, "\n".join(lines) or "  (none)")


def cmd_evidence_add(args: argparse.Namespace) -> int:
    record = engine.add_evidence(
        _project(args), method=args.method, result=args.result, actor=_actor(args), raw_output=args.raw_output
    )
    return _emit(
        args,
        record,
        f"Evidence {record['evidence_id']} [{record['result']}] bound to {record['candidate_hash']}",
    )


def cmd_evidence_list(args: argparse.Namespace) -> int:
    records = _project(args).evidence_records()
    lines = [f"  {item['evidence_id']}  {item['result']:<13} {item['method']}" for item in records]
    return _emit(args, {"evidence": records}, "\n".join(lines) or "  (none)")


def cmd_gate_run(args: argparse.Namespace) -> int:
    report = engine.run_gate(_project(args), gate_id=args.id, actor=_actor(args))
    lines = [f"Gate {report['gate_id']}: {report['decision']}", f"  {report['rationale']}"]
    for finding in report["findings"]:
        lines.append(f"  {finding['code']}: {finding['message']}")
    print("\n".join(lines)) if not args.json else print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"] == "PASS" else 2


def cmd_gate_list(args: argparse.Namespace) -> int:
    reports = _project(args).gate_reports()
    lines = [f"  {item['gate_id']}  {item['decision']:<8} {item['candidate_hash'][:23]}…" for item in reports]
    return _emit(args, {"gates": reports}, "\n".join(lines) or "  (none)")


def cmd_checkpoint(args: argparse.Namespace) -> int:
    record = engine.checkpoint(_project(args), next_action=args.next_action, actor=_actor(args))
    return _emit(
        args,
        record,
        f"Checkpoint {record['session_id']} written.\n  next action : {record['exact_first_next_action']}",
    )


def cmd_pass2(args: argparse.Namespace) -> int:
    review = engine.second_pass(_project(args), reviewer=args.reviewer, notes=args.note or None)
    return _emit(
        args,
        review,
        f"Pass 2 recorded by {review['reviewer']} over {review['document_count']} sealed document(s)\n"
        f"  reviewed identity : {review['reviewed_identity']}",
    )


def cmd_truth_log(args: argparse.Namespace) -> int:
    entries = _project(args).ledger.entries()
    if args.limit:
        entries = entries[-args.limit :]
    lines = [
        f"  {item['seq']:>4}  {item['timestamp']}  {item['action']:<24} {item['subject_id']}"
        for item in entries
    ]
    return _emit(args, {"entries": entries}, "\n".join(lines) or "  (empty)")


def cmd_truth_verify(args: argparse.Namespace) -> int:
    ledger = _project(args).ledger
    chain = ledger.verify()
    anchors = ledger.verify_anchors()
    payload = {"chain": chain, "anchors": anchors, "status": "PASS" if chain["status"] == "PASS" and anchors["status"] == "PASS" else "FAIL"}
    lines = [
        f"Chain   : {chain['status']}  ({chain['entry_count']} entries, head {chain['chain_head'][:16]}…)",
        f"Anchors : {anchors['status']}  ({anchors['anchors_checked']} verified)",
    ]
    for problem in chain["problems"] + anchors["problems"]:
        lines.append(f"  {problem}")
    print("\n".join(lines)) if not args.json else print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 4


def cmd_truth_anchor(args: argparse.Namespace) -> int:
    project = _project(args)
    project.require_installed()
    receipt = project.ledger.anchor(_actor(args), args.note or "")
    return _emit(
        args,
        receipt,
        f"Anchor {receipt['anchor_id']} written at entry {receipt['entry_count']} "
        f"(head {receipt['chain_head'][:16]}…)",
    )


def cmd_verify(args: argparse.Namespace) -> int:
    from .verify import deep_verify

    project = _project(args)
    report = deep_verify(project)
    if args.record and project.installed:
        engine.record_verification(project, report=report, actor=_actor(args))
    lines = [
        f"Deep verification: {report['status']}",
        f"  sections  : {report['sections_passed']}/{report['section_count']}",
        f"  checks    : {report['checks_run']}",
        f"  findings  : {report['finding_count']}",
    ]
    for finding in report["findings"][:40]:
        lines.append(f"  {finding['severity']:<8} {finding['code']:<34} {finding.get('path', '')}: {finding['message']}")
    if report["finding_count"] > 40:
        lines.append(f"  … {report['finding_count'] - 40} more")
    print("\n".join(lines)) if not args.json else print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


def cmd_release(args: argparse.Namespace) -> int:
    manifest = engine.assemble_release(_project(args), output=Path(args.out), actor=_actor(args))
    return _emit(
        args,
        manifest,
        f"Release assembled: {manifest['artifact']}\n"
        f"  sha256   : {manifest['artifact_sha256']}\n"
        f"  bytes    : {manifest['artifact_bytes']}\n"
        f"  members  : {manifest['member_count']}\n"
        f"  identity : {manifest['release_identity']}\n"
        f"  NOTE     : {manifest['certification']['rule']}",
    )


# ----------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="absolute",
        description="Absolute Canonical Framework runtime — install, author, stamp, verify, release.",
    )
    parser.add_argument("--root", help="project root (default: discover upward from the working directory)")
    parser.add_argument("--json", action="store_true", help="emit a single JSON object")
    parser.add_argument("--actor", help="acting role (default: $ABSOLUTE_ACTOR, then $USER)")
    parser.add_argument("--version", action="version", version=f"absolute runtime {RUNTIME_VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="install the control namespace into a project")
    init.add_argument("--project", required=True, help="lowercase project slug")
    init.add_argument("--mission", required=True, help="the mission every action must link upward to")
    init.add_argument("--profile", default="standard", help="minimal | standard | enterprise | audithunt")
    init.add_argument("--adapter", default="claude_code", help="platform adapter directory name")
    init.set_defaults(func=cmd_init)

    sub.add_parser("status", help="current phase, identity, counts, and truth state").set_defaults(func=cmd_status)
    sub.add_parser("next", help="the single next permitted action").set_defaults(func=cmd_next)
    sub.add_parser("explain", help="print the enforced rail and document authoring order").set_defaults(func=cmd_explain)

    goal = sub.add_parser("goal", help="goal lock").add_subparsers(dest="goal_command", required=True)
    goal_set = goal.add_parser("set", help="lock the active goal")
    goal_set.add_argument("--id", help="goal id (default: ABS.GOAL.<NAMESPACE>.PRIMARY)")
    goal_set.add_argument("--statement", required=True, help="what 'done' means")
    goal_set.set_defaults(func=cmd_goal_set)

    work = sub.add_parser("wp", help="work packets").add_subparsers(dest="wp_command", required=True)
    wp_new = work.add_parser("new", help="open one bounded reversible work packet")
    wp_new.add_argument("--objective", required=True)
    wp_new.add_argument("--rollback", required=True, help="exactly how to undo this packet")
    wp_new.set_defaults(func=cmd_wp_new)
    wp_done = work.add_parser("complete", help="close a work packet (requires a passing gate)")
    wp_done.add_argument("--id")
    wp_done.set_defaults(func=cmd_wp_complete)
    work.add_parser("list").set_defaults(func=cmd_wp_list)

    doc = sub.add_parser("doc", help="governed documents").add_subparsers(dest="doc_command", required=True)
    doc_new = doc.add_parser("new", help="open a canonical document package")
    doc_new.add_argument("--id", required=True, help="lowercase document slug")
    doc_new.add_argument("--title", required=True)
    doc_new.add_argument("--question", required=True, help="the single question this package answers (must end in '?')")
    doc_new.add_argument("--requirement", action="append", help="a normative requirement statement (repeatable)")
    doc_new.add_argument("--failure", help="the primary failure this package prevents")
    doc_new.add_argument("--provides", action="append", help="provided interface id (repeatable)")
    doc_new.add_argument("--consumes", action="append", help="consumed interface id (repeatable)")
    doc_new.add_argument("--source-evidence", dest="source_evidence", action="append",
                         help="raw source this package's truth derives from (repeatable)")
    doc_new.add_argument("--excludes", action="append",
                         help="something this package deliberately does not own (repeatable)")
    doc_new.set_defaults(func=cmd_doc_new)
    doc_step = doc.add_parser("step", help="advance one authoring step")
    doc_step.add_argument("--id", required=True)
    doc_step.add_argument("--all", action="store_true", help="run every remaining step")
    doc_step.set_defaults(func=cmd_doc_step)
    doc_check = doc.add_parser("check", help="validate a document package without sealing it")
    doc_check.add_argument("--id", required=True)
    doc_check.set_defaults(func=cmd_doc_check)
    doc_seal = doc.add_parser("seal", help="validate, freeze, and stamp into the source of truth")
    doc_seal.add_argument("--id", required=True)
    doc_seal.set_defaults(func=cmd_doc_seal)
    doc_abandon = doc.add_parser(
        "abandon", help="close a package that cannot be finished, with a recorded reason"
    )
    doc_abandon.add_argument("--id", required=True)
    doc_abandon.add_argument("--reason", required=True, help="why this package will not be finished")
    doc_abandon.set_defaults(func=cmd_doc_abandon)
    doc.add_parser("list").set_defaults(func=cmd_doc_list)

    evidence = sub.add_parser("evidence", help="evidence records").add_subparsers(dest="evidence_command", required=True)
    ev_add = evidence.add_parser("add", help="record evidence bound to the current identity")
    ev_add.add_argument("--method", required=True, help="exactly what was run")
    ev_add.add_argument("--result", required=True, choices=list(engine.RESULT_STATES))
    ev_add.add_argument("--raw-output", dest="raw_output", help="where the raw output is stored")
    ev_add.set_defaults(func=cmd_evidence_add)
    evidence.add_parser("list").set_defaults(func=cmd_evidence_list)

    gate = sub.add_parser("gate", help="evidence gates").add_subparsers(dest="gate_command", required=True)
    gate_run = gate.add_parser("run", help="evaluate the gate against the current identity")
    gate_run.add_argument("--id")
    gate_run.set_defaults(func=cmd_gate_run)
    gate.add_parser("list").set_defaults(func=cmd_gate_list)

    checkpoint = sub.add_parser("checkpoint", help="write a restart-safe session checkpoint")
    checkpoint.add_argument("--next-action", dest="next_action", required=True, help="the exact first next action")
    checkpoint.set_defaults(func=cmd_checkpoint)

    pass2 = sub.add_parser("pass2", help="record the pass-2 review of the frozen whole")
    pass2.add_argument("--reviewer", required=True, help="a role that did not author the material")
    pass2.add_argument("--note", action="append")
    pass2.set_defaults(func=cmd_pass2)

    truth = sub.add_parser("truth", help="source of truth").add_subparsers(dest="truth_command", required=True)
    truth_log = truth.add_parser("log", help="print ledger entries")
    truth_log.add_argument("--limit", type=int, default=0)
    truth_log.set_defaults(func=cmd_truth_log)
    truth.add_parser("verify", help="recompute the hash chain and check anchors").set_defaults(func=cmd_truth_verify)
    truth_anchor = truth.add_parser("anchor", help="write a detached anchor receipt")
    truth_anchor.add_argument("--note")
    truth_anchor.set_defaults(func=cmd_truth_anchor)

    verify = sub.add_parser("verify", help="run the whole-system deep verification")
    verify.add_argument("--record", action="store_true", help="bind the result to the project identity")
    verify.set_defaults(func=cmd_verify)

    release = sub.add_parser("release", help="assemble the shippable artifact")
    release.add_argument("--out", required=True, help="output ZIP path, outside the project tree")
    release.set_defaults(func=cmd_release)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except AbsoluteError as exc:
        payload = {"error": type(exc).__name__, "code": exc.code, "message": str(exc)}
        if hasattr(exc, "required"):
            payload["required_next_action"] = exc.required
            payload["reason"] = exc.reason
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        else:
            print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except BrokenPipeError:  # pragma: no cover
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
