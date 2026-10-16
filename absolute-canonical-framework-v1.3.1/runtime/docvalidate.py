"""Structural and semantic validation of one governed document package.

These are the same rules the framework applies to its own module packages,
applied to project-authored packages. Keeping one rule set means a project
cannot be held to a weaker standard than the framework holds itself to.

Every check returns a finding list rather than raising, so a single run reports
everything wrong with a package instead of only the first problem.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .documents import DOCUMENT_STEPS, TODO_PATTERN, scan_todos
from .util import read_json

REQUIRED_NARRATIVE_SECTIONS = (
    "## Purpose",
    "## Normative requirements",
    "## Operating contract",
    "## State model",
    "## Interfaces provided",
    "## Interfaces consumed",
    "## Failure and recovery",
    "## Security and authority boundary",
    "## Completion",
)

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _finding(code: str, path: str, message: str, severity: str = "HIGH") -> dict[str, Any]:
    return {"code": code, "path": path, "message": message, "severity": severity}


def validate_document(directory: Path, record: dict[str, Any], known_interfaces: set[str]) -> list[dict[str, Any]]:
    """Validate a complete document package. Returns findings; empty means clean."""
    import jsonschema
    import yaml

    findings: list[dict[str, Any]] = []
    done = set(record.get("completed_steps", []))

    # 1. Every artifact for every completed step must exist and be non-empty.
    for step in DOCUMENT_STEPS:
        if step.step_id not in done:
            continue
        for artifact in step.artifacts:
            path = directory / artifact
            if not path.is_file():
                findings.append(_finding("DOC_ARTIFACT_MISSING", artifact, f"{step.step_id} declares it"))
            elif path.stat().st_size == 0:
                findings.append(_finding("DOC_ARTIFACT_EMPTY", artifact, "artifact is zero bytes"))

    if not (directory / "MODULE.md").is_file():
        return findings  # nothing further is checkable

    # 2. Narrative structure: parseable frontmatter, no indented markdown.
    text = (directory / "MODULE.md").read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        findings.append(_finding("DOC_FRONTMATTER_INVALID", "MODULE.md", "no parseable YAML frontmatter block"))
    else:
        try:
            front = yaml.safe_load(match.group(1))
            if not isinstance(front, dict) or "module_id" not in front:
                findings.append(_finding("DOC_FRONTMATTER_INVALID", "MODULE.md", "frontmatter lacks module_id"))
            elif front["module_id"] != record["module_id"]:
                findings.append(
                    _finding(
                        "DOC_IDENTITY_DRIFT",
                        "MODULE.md",
                        f"frontmatter module_id {front['module_id']} != record {record['module_id']}",
                    )
                )
        except Exception as exc:
            findings.append(_finding("DOC_FRONTMATTER_INVALID", "MODULE.md", f"unparseable: {exc}"))

    findings += markdown_structure_findings(directory)

    for section in REQUIRED_NARRATIVE_SECTIONS:
        if section not in text:
            findings.append(_finding("DOC_SECTION_MISSING", "MODULE.md", f"missing section {section}"))

    # 3. Manifest / requirements / policy must agree on the requirement set.
    if (directory / "MODULE_MANIFEST.yaml").is_file() and (directory / "requirements.json").is_file():
        manifest = yaml.safe_load((directory / "MODULE_MANIFEST.yaml").read_text(encoding="utf-8"))
        requirements = read_json(directory / "requirements.json")
        manifest_ids = set(manifest.get("requirements", []))
        requirement_ids = {item["requirement_id"] for item in requirements.get("requirements", [])}
        if manifest_ids != requirement_ids:
            findings.append(
                _finding(
                    "DOC_REQUIREMENT_MISMATCH",
                    "MODULE_MANIFEST.yaml",
                    f"manifest {sorted(manifest_ids)} != requirements.json {sorted(requirement_ids)}",
                )
            )
        for key, relative in (manifest.get("canonical_paths") or {}).items():
            if not (directory / relative).exists():
                findings.append(
                    _finding("DOC_CANONICAL_PATH_MISSING", relative, f"canonical_paths.{key} does not resolve")
                )
        declared = set(manifest.get("provided_interfaces", [])) | set(manifest.get("consumed_interfaces", []))
        unknown = declared - known_interfaces
        if unknown:
            findings.append(
                _finding("DOC_UNKNOWN_INTERFACE", "MODULE_MANIFEST.yaml", f"unresolvable interfaces {sorted(unknown)}")
            )
        # A package may not declare itself certified.
        if manifest.get("status") == "CERTIFIED":
            verification = manifest.get("verification") or {}
            if verification.get("independent_status") not in {"CERTIFIED", "CERTIFIED_WITH_ACCEPTED_RISK"}:
                findings.append(
                    _finding("DOC_FALSE_CERTIFIED", "MODULE_MANIFEST.yaml", "CERTIFIED without independent status")
                )

        if (directory / "machine/policy.json").is_file():
            policy = read_json(directory / "machine/policy.json")
            policy_ids = {item.get("requirement_id") for item in policy.get("rules", [])}
            if policy_ids != requirement_ids:
                findings.append(
                    _finding(
                        "DOC_POLICY_TRACE_MISMATCH",
                        "machine/policy.json",
                        f"policy {sorted(policy_ids)} != requirements {sorted(requirement_ids)}",
                    )
                )

        # 4. Traceability: each requirement must appear in narrative *and* plan.
        plan = directory / "tests/TEST_PLAN.md"
        combined = text + (plan.read_text(encoding="utf-8") if plan.is_file() else "")
        for rid in sorted(requirement_ids):
            if combined.count(rid) < 2:
                findings.append(
                    _finding("DOC_WEAK_TRACEABILITY", "MODULE.md", f"{rid} appears fewer than twice across narrative and test plan")
                )

    # 5. Fixture behavior: positive passes, negative and adversarial must fail.
    contract = directory / "machine/contract.schema.json"
    if contract.is_file():
        try:
            schema = read_json(contract)
            jsonschema.Draft202012Validator.check_schema(schema)
            validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
            expectations = (
                ("tests/positive/valid_instance.json", True),
                ("tests/negative/missing_evidence.json", False),
                ("tests/adversarial/authority_override.json", False),
                ("machine/examples/valid.json", True),
            )
            for relative, should_pass in expectations:
                path = directory / relative
                if not path.is_file():
                    continue
                errors = list(validator.iter_errors(read_json(path)))
                if should_pass and errors:
                    findings.append(
                        _finding("DOC_FIXTURE_SHOULD_PASS", relative, f"fixture rejected: {errors[0].message}")
                    )
                if not should_pass and not errors:
                    findings.append(
                        _finding("DOC_FIXTURE_SHOULD_FAIL", relative, "fixture was accepted but must be rejected")
                    )
        except Exception as exc:
            findings.append(_finding("DOC_CONTRACT_INVALID", "machine/contract.schema.json", str(exc)))

    # 6. Visual parity: source, derivative, and manifest must all resolve.
    manifest_path = directory / "blueprint/visual_manifest.json"
    if manifest_path.is_file():
        visual = read_json(manifest_path)
        renderer = visual.get("renderer") or {}
        for key in ("source", "output"):
            relative = renderer.get(key)
            if not relative or not (directory / "blueprint" / relative).is_file():
                findings.append(
                    _finding("DOC_VISUAL_UNRESOLVED", str(relative), f"visual_manifest.renderer.{key} does not resolve")
                )
        if not ((visual.get("accessibility") or {}).get("alt_text") or "").strip():
            findings.append(
                _finding("DOC_VISUAL_NO_FALLBACK", "blueprint/visual_manifest.json", "no accessible alt text", "MEDIUM")
            )

    # 6b. The three schema-governed artifacts must satisfy the framework's own
    # schemas, not merely look plausible. A project document held to a weaker
    # standard than a framework module would be a two-tier system.
    framework_root = Path(__file__).resolve().parents[1]
    for relative, schema_name, loader in (
        ("MODULE_MANIFEST.yaml", "module_manifest.schema.json", "yaml"),
        ("machine/policy.json", "module_policy.schema.json", "json"),
        ("blueprint/visual_manifest.json", "visual_spec.schema.json", "json"),
    ):
        path = directory / relative
        schema_path = framework_root / "04_enforcement/schemas" / schema_name
        if not path.is_file() or not schema_path.is_file():
            continue
        try:
            instance = (
                yaml.safe_load(path.read_text(encoding="utf-8")) if loader == "yaml" else read_json(path)
            )
            validator = jsonschema.Draft202012Validator(
                read_json(schema_path), format_checker=jsonschema.FormatChecker()
            )
            for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path))[:6]:
                findings.append(_finding("DOC_SCHEMA_VIOLATION", relative, f"{schema_name}: {error.message}"))
        except Exception as exc:
            findings.append(_finding("DOC_SCHEMA_UNCHECKABLE", relative, f"{schema_name}: {exc}"))

    # 7. No unresolved authoring markers.
    for todo in scan_todos(directory):
        findings.append(
            _finding("DOC_UNRESOLVED_MARKER", todo["path"], f"line {todo['line']}: {todo['marker']}")
        )

    # 8. Relative markdown links must resolve.
    link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in sorted(directory.rglob("*.md")):
        for target in link.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                findings.append(
                    _finding(
                        "DOC_BROKEN_LINK",
                        path.relative_to(directory).as_posix(),
                        f"link target does not resolve: {target}",
                    )
                )
    return findings


def markdown_structure_findings(directory: Path) -> list[dict[str, Any]]:
    """Catch the rendering defect class: structural markdown hidden in code blocks.

    A heading or list indented four spaces is a code block to every conformant
    markdown renderer. The document then *looks* authored while publishing as an
    undifferentiated blob, which silently breaks representation parity. This
    check exists because that defect shipped undetected in a prior release.
    """
    findings: list[dict[str, Any]] = []
    heading = re.compile(r"^\s{4,}#{1,6}\s")
    for path in sorted(directory.rglob("*.md")):
        relative = path.relative_to(directory).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        fenced = False
        offenders: list[int] = []
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            if heading.match(line):
                offenders.append(number)
        if offenders:
            findings.append(
                _finding(
                    "DOC_MARKDOWN_INDENTED_HEADING",
                    relative,
                    f"headings indented four or more spaces render as code: lines {offenders[:8]}",
                )
            )
        if lines and lines[0].strip() == "---":
            closing = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
            if closing is None:
                findings.append(_finding("DOC_FRONTMATTER_UNCLOSED", relative, "frontmatter never closed"))
            else:
                if any(line.startswith("    ") and line.strip() for line in lines[1:closing]):
                    findings.append(
                        _finding("DOC_FRONTMATTER_INDENTED", relative, "frontmatter keys indented; block is not parseable")
                    )
                if lines[closing].startswith(" "):
                    findings.append(
                        _finding("DOC_FRONTMATTER_INDENTED", relative, "closing frontmatter delimiter is indented")
                    )
    return findings
