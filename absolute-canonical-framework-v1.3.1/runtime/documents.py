"""Governed document authoring.

A "document" in this framework is not a file; it is a canonical module package —
one bounded semantic scope expressed in every representation that applies to it.
This module drives the authoring of that package in the exact order the
framework's operating contract declares, and refuses to let a later
representation be written before an earlier one exists.

Two guarantees make the output trustworthy rather than merely tidy:

1. **Order.** ``DOCUMENT_STEPS`` is the framework's authoring sequence. A step
   cannot be completed while any earlier step is open, so a machine contract can
   never predate the narrative meaning it is supposed to encode.
2. **No unfilled scaffolding.** Every generated artifact marks author-specific
   content with :data:`TODO_MARKER`. ``seal`` refuses while a single marker
   remains, so a package can never be stamped into the source of truth while it
   still contains template text.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .errors import DocumentStepError
from .util import atomic_write, atomic_write_json, canonical_json, read_json, sha256_path, sha256_tree, utc_now

TODO_MARKER = "<<TODO"
TODO_PATTERN = re.compile(r"<<TODO:[^>]*>>")

RESULT_STATES = ["PASS", "FAIL", "BLOCKED", "NOT_RUN", "INCONCLUSIVE", "STALE"]


@dataclass(frozen=True)
class DocumentStep:
    step_id: str
    ordinal: int
    title: str
    intent: str
    artifacts: tuple[str, ...]


DOCUMENT_STEPS: tuple[DocumentStep, ...] = (
    DocumentStep(
        "D1.SCOPE",
        1,
        "Declare the canonical scope and source evidence",
        "Name exactly one question this package owns, and where its truth comes from.",
        ("scope.json",),
    ),
    DocumentStep(
        "D2.NARRATIVE",
        2,
        "Write the narrative meaning",
        "Human-authoritative meaning. Every other representation derives its intent from here.",
        ("MODULE.md",),
    ),
    DocumentStep(
        "D3.MANIFEST",
        3,
        "Declare the manifest",
        "Machine-readable identity, scope boundary, interfaces, and canonical paths.",
        ("MODULE_MANIFEST.yaml",),
    ),
    DocumentStep(
        "D4.REQUIREMENTS",
        4,
        "Enumerate normative requirements",
        "Each requirement is testable and owned here and nowhere else.",
        ("requirements.json",),
    ),
    DocumentStep(
        "D5.BLUEPRINT",
        5,
        "Write the blueprint",
        "Components, sequence, dependencies, error design, and quality attributes.",
        ("blueprint/BLUEPRINT.md",),
    ),
    DocumentStep(
        "D6.VISUAL",
        6,
        "Author the visual contract",
        "A semantic source graph plus its rendered derivative and a manifest binding them.",
        ("blueprint/architecture.dot", "blueprint/architecture.svg", "blueprint/visual_manifest.json"),
    ),
    DocumentStep(
        "D7.MACHINE",
        7,
        "Author the machine contract",
        "The schema and policy that make the narrative deterministically checkable.",
        ("machine/contract.schema.json", "machine/policy.json", "machine/examples/valid.json"),
    ),
    DocumentStep(
        "D8.TESTS",
        8,
        "Author positive, negative, and adversarial tests",
        "A contract nothing can fail is not a contract.",
        (
            "tests/TEST_PLAN.md",
            "tests/positive/valid_instance.json",
            "tests/negative/missing_evidence.json",
            "tests/adversarial/authority_override.json",
        ),
    ),
    DocumentStep(
        "D9.INTEGRATION",
        9,
        "Declare integration surfaces",
        "Provided and consumed interfaces and dependencies, resolvable against the registry.",
        (
            "integration/provided_interfaces.json",
            "integration/consumed_interfaces.json",
            "integration/dependencies.json",
        ),
    ),
    DocumentStep(
        "D10.PUBLICATION",
        10,
        "Derive the governed publications",
        "Plain-English and quick-reference derivatives, classified and audience-bound.",
        (
            "publication/plain_english.md",
            "publication/quick_reference.md",
            "publication/publication_manifest.yaml",
        ),
    ),
    DocumentStep(
        "D11.CHANGELOG",
        11,
        "Open the changelog",
        "Every later substantive change to this package must land here.",
        ("CHANGELOG.md",),
    ),
)

STEPS_BY_ID = {step.step_id: step for step in DOCUMENT_STEPS}
TOTAL_STEPS = len(DOCUMENT_STEPS)


def next_document_step(record: dict[str, Any]) -> DocumentStep | None:
    done = set(record.get("completed_steps", []))
    for step in DOCUMENT_STEPS:
        if step.step_id not in done:
            return step
    return None


def scan_todos(directory: Path) -> list[dict[str, Any]]:
    """Every unresolved authoring marker under ``directory``."""
    findings: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for match in TODO_PATTERN.finditer(line):
                findings.append(
                    {
                        "path": path.relative_to(directory).as_posix(),
                        "line": number,
                        "marker": match.group(0),
                    }
                )
    return findings


# ---------------------------------------------------------------- generators
#
# Each generator returns ``{relative_path: text}``. Generators receive the
# document record so that identity, requirement IDs, and declared states flow
# into every representation from one place — this is what keeps the
# representations in parity instead of merely adjacent.


def _req_ids(record: dict[str, Any]) -> list[str]:
    return [item["requirement_id"] for item in record.get("requirements", [])]


def _gen_scope(record: dict[str, Any]) -> dict[str, str]:
    return {
        "scope.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "scope_id": record["scope_id"],
                "module_id": record["module_id"],
                "question": record["question"],
                "source_evidence": record.get("source_evidence")
                or [f"{TODO_MARKER}: name the raw source this package's truth derives from>>"],
                "excludes": record.get("excludes")
                or [f"{TODO_MARKER}: name at least one thing this package deliberately does not own>>"],
                "question_owner": record["module_id"],
                "declared_at": record["created_at"],
            }
        )
    }


def _gen_narrative(record: dict[str, Any]) -> dict[str, str]:
    reqs = record.get("requirements", [])
    lines = [
        "---",
        f"module_id: {record['module_id']}",
        f"version: {record['version']}",
        f"status: {record['status']}",
        f"framework_release: {record['framework_release']}",
        "---",
        f"# {record['title']}",
        "## Purpose",
        f"This module is the canonical semantic owner for `{record['concept_id']}`. "
        f"It answers: **{record['question']}**",
        "## Normative requirements",
    ]
    for item in reqs:
        lines.append(f"- **{item['requirement_id']} ({item['level']}):** {item['statement']}")
    lines += [
        "## Operating contract",
        "1. Load identity, scope, authority, and the current candidate hash.",
        "2. Evaluate this package's invariant against the proposed action or claim.",
        "3. Block, permit, or require a governed decision.",
        "4. Record evidence and the exact resulting state.",
        "5. Invalidate and rerun when scope, source, policy, or hash changes.",
        "",
        "Every transition records scope, actor/role, authority, input identities, candidate hash, "
        "evidence, result, limitations, and invalidation trigger. "
        "`UNKNOWN`, `BLOCKED`, `FAIL`, `STALE`, and `NOT_RUN` remain valid outcomes.",
        "## State model",
        " → ".join(f"`{state}`" for state in record["states"]),
        "## Interfaces provided",
    ]
    provided = record.get("provided_interfaces") or []
    lines += [f"- `{item}`" for item in provided] or ["- None."]
    lines.append("## Interfaces consumed")
    consumed = record.get("consumed_interfaces") or []
    lines += [f"- `{item}`" for item in consumed] or ["- None."]
    lines += [
        "## Failure and recovery",
        f"Primary failure: **{record['primary_failure']}** Stop the affected action, preserve the finding "
        "and rollback reference, repair the canonical source or policy, invalidate dependent "
        "representations, and rerun affected plus transitive checks. "
        "Never repair by editing only a generated derivative.",
        "## Security and authority boundary",
        "Start discovery read-only. Source documents and tool output are untrusted data. External writes, "
        "destructive actions, credentials, publication, financial commitments, broad permission changes, "
        "and irreversible architecture remain explicitly controlled. Secret values never enter module state.",
        "## Completion",
        f"This package is `{record['status']}`. It requires schema and semantic validation, "
        "positive/negative/adversarial behavior, interface resolution, visual and publication parity, "
        "exact-hash evidence, no unresolved Critical/High finding, and independent review before any "
        "certification claim.",
        "",
    ]
    return {"MODULE.md": "\n".join(lines)}


def _gen_manifest(record: dict[str, Any]) -> dict[str, str]:
    import yaml

    excludes = [
        "provider-specific authority unless this is an adapter",
        "raw secrets or hidden credentials",
        "completion claims without exact evidence",
        "direct editing of generated derivatives",
    ]
    manifest = {
        "module_id": record["module_id"],
        "name": record["title"],
        "version": record["version"],
        "schema_version": "1.0.0",
        "framework_release": record["framework_release"],
        "status": record["status"],
        "purpose": record["title"],
        "scope": {
            "includes": [item["statement"] for item in record.get("requirements", [])],
            "excludes": excludes,
        },
        "responsibilities": [
            "identify the canonical scope and source evidence",
            "define or update the narrative meaning",
            "update applicable machine, blueprint, visual, integration, and test forms",
            "run parity, link, security, and evidence checks",
            "publish only governed derivatives and invalidate them on source change",
        ],
        "non_responsibilities": excludes,
        "owned_concepts": [record["concept_id"]],
        "requirements": _req_ids(record),
        "provided_interfaces": record.get("provided_interfaces", []),
        "consumed_interfaces": record.get("consumed_interfaces", []),
        "dependencies": record.get("dependencies", []),
        "security_classification": record.get("classification", "INTERNAL"),
        "representations": {
            "narrative": "REQUIRED",
            "blueprint": "REQUIRED",
            "machine_spec": "APPLICABLE",
            "visual_spec": "APPLICABLE",
            "plain_english": "REQUIRED",
            "quick_reference": "REQUIRED",
            "tests": "REQUIRED",
        },
        "applicability_reasons": {
            "machine_spec": "States, requirements, evidence, and transitions require deterministic validation.",
            "visual_spec": record["question"],
        },
        "canonical_paths": {
            "narrative": "MODULE.md",
            "manifest": "MODULE_MANIFEST.yaml",
            "requirements": "requirements.json",
            "blueprint": "blueprint/BLUEPRINT.md",
            "visual_source": "blueprint/architecture.dot",
            "visual_output": "blueprint/architecture.svg",
            "visual_manifest": "blueprint/visual_manifest.json",
            "machine_schema": "machine/contract.schema.json",
            "machine_policy": "machine/policy.json",
            "positive_fixture": "tests/positive/valid_instance.json",
            "negative_fixture": "tests/negative/missing_evidence.json",
            "adversarial_fixture": "tests/adversarial/authority_override.json",
            "plain_english": "publication/plain_english.md",
            "quick_reference": "publication/quick_reference.md",
        },
        "verification": {
            "candidate_hash": None,
            "gate_ids": record.get("gate_ids", []),
            "evidence_ids": [],
            "independent_status": "PENDING",
            "invalidation_triggers": ["requirement", "schema", "policy", "interface", "security", "candidate_hash"],
        },
        "owner": record.get("owner", "project_module_owner"),
        "reviewers": ["fresh_semantic_verifier", "independent_adversarial_verifier"],
    }
    return {"MODULE_MANIFEST.yaml": yaml.safe_dump(manifest, sort_keys=False, width=110)}


def _gen_requirements(record: dict[str, Any]) -> dict[str, str]:
    return {
        "requirements.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "module_id": record["module_id"],
                "requirements": [
                    {
                        "requirement_id": item["requirement_id"],
                        "level": item["level"],
                        "statement": item["statement"],
                        "owner_module": record["module_id"],
                        "verification": "schema + semantic validation + positive/negative/adversarial fixtures",
                    }
                    for item in record.get("requirements", [])
                ],
            }
        )
    }


def _gen_blueprint(record: dict[str, Any]) -> dict[str, str]:
    reqs = _req_ids(record)
    lines = [
        f"# Blueprint — {record['title']}",
        f"**Module:** `{record['module_id']}`  ",
        f"**Scope:** `{record['scope_id']}`  ",
        f"**Truth context:** {record['framework_release']}",
        "## Reader question",
        record["question"],
        "## Components",
        "Governed input boundary → identity/authority/permission gate → bounded operation → "
        "evidence and policy evaluation → validated output or finding/repair loop.",
        "## Sequence",
        "1. Load identity, scope, and current authority.",
        "2. Evaluate the invariant against the proposed action or claim.",
        "3. Block, permit, or require a governed decision.",
        "4. Record evidence and exact state.",
        "5. Invalidate and rerun when scope, source, policy, or hash changes.",
        "## Requirement coverage",
    ]
    lines += [f"- `{rid}` is realized by the gate and evidence steps above." for rid in reqs]
    lines += [
        "## Dependencies",
    ]
    deps = record.get("dependencies") or []
    lines += [f"- `{item}`" for item in deps] or ["- No direct provider-module dependency beyond kernel contracts."]
    lines += [
        "## Error design",
        "Invalid input, missing authority, permission denial, dependency failure, stale evidence, "
        "semantic contradiction, and unknown cause are distinct. The primary adverse case is "
        f"`{record['primary_failure'].rstrip('.')}`. The package fails closed for the affected governed "
        "action and preserves restart-safe recovery.",
        "## Quality attributes",
        "Traceable, provider-independent, reversible, restart-safe, least-privilege, deterministic where "
        "possible, and exact-hash verifiable.",
        "## Visual semantics",
        "`architecture.dot` is the editable semantic source. `architecture.svg` is a derivative and is "
        "regenerated, never hand-edited. The graph shows the authority gate, bounded operation, evidence "
        "decision, validated output, and finding loop.",
        "",
    ]
    return {"blueprint/BLUEPRINT.md": "\n".join(lines)}


def _escape_dot(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _gen_visual(record: dict[str, Any]) -> dict[str, str]:
    label = _escape_dot(record["title"])
    caption = _escape_dot(record["module_id"])
    dot = (
        "digraph module {\n"
        'graph [rankdir=LR,bgcolor="transparent",pad="0.2"];\n'
        'node [shape=box,style="rounded",fontname="Arial",fontsize=10];\n'
        'edge [fontname="Arial",fontsize=9];\n'
        'input [label="Governed inputs"]; '
        'gate [label="Authority + policy",shape=diamond]; '
        f'op [label="{label}"]; '
        'evidence [label="Evidence + checks",shape=diamond]; '
        'output [label="Validated output"];\n'
        'input -> gate [label="scope + identity"]; '
        'gate -> op [label="authorized"]; '
        'op -> evidence [label="claims"]; '
        'evidence -> output [label="pass / truthful state"]; '
        'evidence -> op [label="finding",style=dashed];\n'
        f'label="{caption}"; labelloc=b; fontname="Arial"; fontsize=11;\n'
        "}\n"
    )
    return {
        "blueprint/architecture.dot": dot,
        "blueprint/visual_manifest.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "visual_id": f"ABS.VIS.{record['namespace']}.{record['doc_id'].upper().replace('-', '_')}.ARCHITECTURE",
                "module_id": record["module_id"],
                "scope_id": record["scope_id"],
                "reader_question": record["question"],
                "communication_intent": (
                    "show governed input, authority gate, bounded operation, evidence decision, "
                    "validated output, and repair loop"
                ),
                "audience": ["INTERNAL_EXHAUSTIVE", "RESTRICTED_ENGINEERING", "PLAIN_ENGLISH"],
                "truth_context": "TARGET_PROJECT_ARCHITECTURE",
                "data_source": [
                    "MODULE_MANIFEST.yaml",
                    "requirements.json",
                    "integration/provided_interfaces.json",
                    "integration/consumed_interfaces.json",
                ],
                "visual_grammar": "directed process and interface graph",
                "semantic_encodings": {
                    "diamond": "decision",
                    "solid_arrow": "governed flow",
                    "dashed_arrow": "finding/repair",
                    "note": "registered interface",
                },
                "renderer": {
                    "route": "GRAPHVIZ_DOT",
                    "source": "architecture.dot",
                    "output": "architecture.svg",
                    "runtime_version": "VERIFY_AT_BUILD",
                },
                "accessibility": {
                    "alt_text": (
                        f"{record['title']} accepts governed inputs through an authority gate, evaluates "
                        "evidence, then emits validated output or a finding loop."
                    ),
                    "static_fallback": "BLUEPRINT.md",
                },
                "validation": [
                    "source_parses",
                    "output_exists",
                    "ids_present",
                    "interfaces_resolve",
                    "alt_text_present",
                ],
            }
        ),
    }


def render_svg(directory: Path) -> None:
    """Render the visual derivative from its semantic source.

    Graphviz is optional at author time. When it is absent a deterministic,
    self-describing placeholder is written so the package is still complete and
    the derivative still declares how it was produced — silently emitting no
    file would leave the visual representation missing without saying so.
    """
    source = directory / "blueprint/architecture.dot"
    target = directory / "blueprint/architecture.svg"
    if shutil.which("dot"):
        result = subprocess.run(["dot", "-Tsvg", str(source)], capture_output=True)
        if result.returncode == 0 and result.stdout:
            target.write_bytes(result.stdout)
            return
    manifest = read_json(directory / "blueprint/visual_manifest.json")
    fallback = manifest["accessibility"]["alt_text"]
    target.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="120" '
        'viewBox="0 0 720 120" role="img">\n'
        f"  <title>{manifest['module_id']}</title>\n"
        f"  <desc>{fallback}</desc>\n"
        '  <text x="12" y="40" font-family="Arial" font-size="13">'
        "Graphviz was unavailable; this derivative carries the declared text fallback."
        "</text>\n"
        '  <text x="12" y="70" font-family="Arial" font-size="11">'
        f"{fallback[:96]}</text>\n"
        "</svg>\n",
        encoding="utf-8",
    )


def _gen_machine(record: dict[str, Any]) -> dict[str, str]:
    module_id = record["module_id"]
    contract = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:absolute:{module_id.lower().replace('.', '_')}:contract:1.0.0",
        "title": f"{record['title']} Contract Instance",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "module_id",
            "scope_id",
            "state",
            "requirement_evidence",
            "candidate_hash",
            "limitations",
        ],
        "properties": {
            "schema_version": {"const": "1.0.0"},
            "module_id": {"const": module_id},
            "scope_id": {"type": "string", "pattern": "^ABS\\.SCOPE\\."},
            "state": {"enum": list(record["states"])},
            "requirement_evidence": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["requirement_id", "evidence_ids", "result"],
                    "properties": {
                        "requirement_id": {"enum": _req_ids(record)},
                        "evidence_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "pattern": "^ABS\\.EVIDENCE\\."},
                        },
                        "result": {"enum": RESULT_STATES},
                    },
                },
            },
            "candidate_hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
            "limitations": {"type": "array", "items": {"type": "string"}},
            "updated_at": {"type": "string", "format": "date-time"},
        },
    }
    # Shape is fixed by 04_enforcement/schemas/module_policy.schema.json, which
    # forbids additional properties. Generating a "reasonable looking" policy
    # that the framework's own validator rejects would produce documents that
    # can never be sealed.
    states = list(record["states"])
    policy = {
        "schema_version": "1.0.0",
        "module_id": module_id,
        "policy_version": "1.0.0",
        "scope_id": record["scope_id"],
        "truth_scope": [record["concept_id"]],
        "default_action": "DENY_UNLESS_SCOPE_AUTHORITY_PERMISSION_AND_EVIDENCE_ARE_VALID",
        "rules": [
            {
                "rule_id": f"{module_id}.RULE.{index:03d}",
                "requirement_id": item["requirement_id"],
                "condition": "governed action or claim is in module scope",
                "effect": "REQUIRE_CONFORMANCE_AND_EVIDENCE",
                "on_failure": "BLOCK_AND_RECORD_FINDING",
            }
            for index, item in enumerate(record.get("requirements", []), 1)
        ],
        "states": states,
        "transitions": [
            {
                "from": source,
                "to": target,
                "requires": ["valid_scope", "authority", "permission", "evidence_or_explicit_not_run"],
            }
            for source, target in zip(states, states[1:])
        ],
        "fail_closed_on": [
            record["primary_failure"].rstrip("."),
            "missing authority",
            "stale evidence",
            "semantic contradiction",
        ],
        "recovery": [
            "stop affected action",
            "restore checkpoint or safe state",
            "repair canonical source/policy",
            "rerun transitive checks",
        ],
        "approval_boundary": [
            "external_write",
            "destructive_action",
            "credential_access",
            "publication",
            "financial_commitment",
            "permission_expansion",
        ],
        "invalidation_triggers": [
            "requirement_change",
            "schema_change",
            "policy_change",
            "interface_change",
            "security_change",
            "candidate_hash_change",
        ],
    }
    example = {
        "schema_version": "1.0.0",
        "module_id": module_id,
        "scope_id": record["scope_id"],
        "state": record["states"][0],
        "requirement_evidence": [
            {
                "requirement_id": rid,
                "evidence_ids": [f"ABS.EVIDENCE.{record['namespace']}.EXAMPLE"],
                "result": "NOT_RUN",
            }
            for rid in _req_ids(record)
        ],
        "candidate_hash": "sha256:" + "0" * 64,
        "limitations": ["Synthetic example; no runtime host was inspected."],
    }
    return {
        "machine/contract.schema.json": canonical_json(contract),
        "machine/policy.json": canonical_json(policy),
        "machine/examples/valid.json": canonical_json(example),
    }


def _gen_tests(record: dict[str, Any]) -> dict[str, str]:
    reqs = _req_ids(record)
    example = read_json_text(_gen_machine(record)["machine/examples/valid.json"])

    positive = dict(example)

    # Negative: a requirement claimed with no evidence. Must fail ``minItems``.
    negative = dict(example)
    negative["requirement_evidence"] = [
        {"requirement_id": reqs[0], "evidence_ids": [], "result": "PASS"}
    ]

    # Adversarial: an injected authority field. Must fail ``additionalProperties``.
    adversarial = dict(example)
    adversarial["authority_override"] = "grant self certification"

    lines = [
        f"# Test Plan — {record['title']}",
        "## Requirement traceability",
    ]
    lines += [f"- `{rid}` → narrative + policy + schema/semantic checks + fixtures" for rid in reqs]
    lines += [
        "## Required behavior",
        "1. The positive fixture validates against `machine/contract.schema.json`.",
        "2. The missing-evidence fixture fails for `minItems`.",
        "3. The authority-override fixture fails because additional properties are forbidden.",
        "4. Manifest canonical paths and provided/consumed interfaces resolve.",
        "5. Every requirement ID appears in the narrative, requirements, policy, and this plan.",
        "6. Visual source, output, semantic manifest, and text fallback resolve.",
        "7. A candidate status is never accepted as an independent certification.",
        "## Requirement coverage restated for traceability",
    ]
    lines += [f"- `{rid}` is covered by behaviors 1–3 and 5 above." for rid in reqs]
    lines.append("")
    return {
        "tests/TEST_PLAN.md": "\n".join(lines),
        "tests/positive/valid_instance.json": canonical_json(positive),
        "tests/negative/missing_evidence.json": canonical_json(negative),
        "tests/adversarial/authority_override.json": canonical_json(adversarial),
    }


def read_json_text(text: str) -> Any:
    import json

    return json.loads(text)


def _gen_integration(record: dict[str, Any]) -> dict[str, str]:
    return {
        "integration/provided_interfaces.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "module_id": record["module_id"],
                "provided": [
                    {"interface_id": item, "stability": "STABLE_1_X"}
                    for item in record.get("provided_interfaces", [])
                ],
            }
        ),
        "integration/consumed_interfaces.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "module_id": record["module_id"],
                "consumed": [
                    {"interface_id": item, "required": True}
                    for item in record.get("consumed_interfaces", [])
                ],
            }
        ),
        "integration/dependencies.json": canonical_json(
            {
                "schema_version": "1.0.0",
                "module_id": record["module_id"],
                "dependencies": record.get("dependencies", []),
                "dependency_rule": "Authority flows one way; a dependency may not rewrite this package's contract.",
            }
        ),
    }


def _gen_publication(record: dict[str, Any]) -> dict[str, str]:
    reqs = record.get("requirements", [])
    statements = "; ".join(item["statement"].rstrip(".") for item in reqs)
    plain = (
        f"# {record['title']} — Plain English\n"
        f"This package answers **{record['question']}** "
        f"It applies {len(reqs)} canonical rule(s): {statements}.\n"
        "It first checks identity, scope, authority, permission, freshness, and rollback; performs one "
        "bounded operation; records evidence and limitations; and reports a truthful state. "
        f"The key failure is `{record['primary_failure'].rstrip('.')}`. The response is to stop the affected "
        "action, preserve the finding, restore a safe checkpoint where needed, fix the canonical source, "
        "and rerun affected checks.\n"
    )
    provided = ", ".join(f"`{item}`" for item in record.get("provided_interfaces", [])) or "none"
    consumed = ", ".join(f"`{item}`" for item in record.get("consumed_interfaces", [])) or "none"
    quick = (
        f"# Quick Reference — {record['title']}\n"
        "| Field | Value |\n|---|---|\n"
        f"| Module | `{record['module_id']}` |\n"
        f"| Concept | `{record['concept_id']}` |\n"
        f"| Requirements | {', '.join('`' + rid + '`' for rid in _req_ids(record))} |\n"
        f"| States | {', '.join('`' + state + '`' for state in record['states'])} |\n"
        f"| Primary failure | `{record['primary_failure'].rstrip('.')}` |\n"
        f"\nProvided: {provided}. Consumed: {consumed}.\n"
        "Mandatory: validate manifest, requirements, policy, schema, fixtures, links, interfaces, "
        "visual source/output, and exact-hash evidence. Invalidate all dependent views after change.\n"
    )
    import yaml

    manifest = yaml.safe_dump(
        {
            "schema_version": "1.0.0",
            "module_id": record["module_id"],
            "classification": record.get("classification", "INTERNAL"),
            "allowed_audiences": record.get("allowed_audiences", ["INTERNAL"]),
            "derivatives": [
                {"path": "publication/plain_english.md", "derived_from": "MODULE.md"},
                {"path": "publication/quick_reference.md", "derived_from": "MODULE_MANIFEST.yaml"},
            ],
            "invalidation_rule": "Any change to the canonical source invalidates every derivative listed here.",
        },
        sort_keys=False,
    )
    return {
        "publication/plain_english.md": plain,
        "publication/quick_reference.md": quick,
        "publication/publication_manifest.yaml": manifest,
    }


def _gen_changelog(record: dict[str, Any]) -> dict[str, str]:
    return {
        "CHANGELOG.md": (
            f"# Changelog — {record['title']}\n"
            f"## {record['version']} — {record['created_at'][:10]}\n"
            f"- Opened the canonical package for `{record['concept_id']}`.\n"
            f"- Declared {len(record.get('requirements', []))} normative requirement(s).\n"
            "- Authored narrative, manifest, requirements, blueprint, visual, machine, test, "
            "integration, and publication representations in lockstep.\n"
        )
    }


GENERATORS: dict[str, Callable[[dict[str, Any]], dict[str, str]]] = {
    "D1.SCOPE": _gen_scope,
    "D2.NARRATIVE": _gen_narrative,
    "D3.MANIFEST": _gen_manifest,
    "D4.REQUIREMENTS": _gen_requirements,
    "D5.BLUEPRINT": _gen_blueprint,
    "D6.VISUAL": _gen_visual,
    "D7.MACHINE": _gen_machine,
    "D8.TESTS": _gen_tests,
    "D9.INTEGRATION": _gen_integration,
    "D10.PUBLICATION": _gen_publication,
    "D11.CHANGELOG": _gen_changelog,
}
