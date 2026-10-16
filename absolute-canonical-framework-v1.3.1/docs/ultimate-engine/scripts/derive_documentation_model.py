#!/usr/bin/env python3
"""Derive the machine and figure inputs for the Ultimate Engine documentation set.

The script reads the subject's tracked tree, canonical registries, runtime constants, and verifier
AST. It writes deterministic JSON and Mermaid source; docgen and graphify perform the rendering.
It never edits the framework's existing source or canonical artifacts.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
DOC_ROOT = ROOT / "docs" / "ultimate-engine"
MACHINE = DOC_ROOT / "machine"
GRAPH_SOURCE = DOC_ROOT / "graphs" / "source"
REGISTRIES = ROOT / "docs" / "registries"

# Every sidecar's data_sources.retrieved carries this exact string. It is a single named
# constant, never date.today(): a script whose output depends on the calendar cannot satisfy the
# "a second run changes nothing" acceptance test, because the second run would happen on a
# different day than the first for anyone who does not run both in the same second.
RETRIEVED = "2026-09-07"

DOMAIN_PURPOSES = {
    "00_kernel": "Mission, identity, authority, lifecycle, evidence, recovery, modularity, and independent verification invariants.",
    "01_control_plane": "Durable project state, bounded work, sessions, decisions, and release assembly.",
    "02_capabilities": "Minimum-sufficient capability selection, delegation, connectors, and execution routing.",
    "03_knowledge_and_documentation": "Canonical packages, representation parity, publication, visuals, graph context, and source reconciliation.",
    "04_enforcement": "Schemas, validators, hooks, security controls, observability, and deterministic refusal.",
    "05_platform_adapters": "Host translations for Codex, Claude Code, Cursor, local agents, and generic APIs.",
    "06_project_profiles": "Minimal, standard, enterprise, and AuditHunt composition overlays.",
    "07_optional_addons": "Measured-need knowledge and operations extensions that must not outrank canonical truth.",
    "08_examples": "Non-authoritative example records for the framework's shared data contracts.",
    "09_tests_evals": "Positive, negative, adversarial, mutation, recovery, and release verification harnesses.",
    "10_runtime": "Executable rail, governed document lifecycle, ledger, identity binding, verification, and release commands.",
}

# Dependency edges match docs/doc-pipeline/OUTLINES-2026-09-07.md §G.1 exactly. An edge points
# from a document to a document it depends on.
DOCUMENTS = [
    {
        "id": "GUIDE-100",
        "path": "GUIDE-100-project-guide.md",
        "title": "Project Guide",
        "depends_on": ["SYS-110", "SYS-120", "GUIDE-140", "REF-150"],
        "figures": ["domain-operating-model", "tracked-artifacts-by-domain", "authority-of-facts"],
    },
    {
        "id": "SYS-110",
        "path": "SYS-110-architecture.md",
        "title": "Architecture and Domain Map",
        "depends_on": ["GUIDE-100", "REF-130", "GUIDE-170"],
        "figures": ["domain-dependencies", "dependency-centrality", "representation-mix", "repository-layout"],
    },
    {
        "id": "SYS-120",
        "path": "SYS-120-runtime-enforcement.md",
        "title": "Runtime and Enforcement",
        "depends_on": ["SYS-110", "GUIDE-140", "REF-130", "GUIDE-170"],
        "figures": ["project-rail", "document-rail", "governed-mutation", "cross-representation-pin"],
    },
    {
        "id": "REF-130",
        "path": "REF-130-extension-points.md",
        "title": "Extension Points and Change Risk",
        "depends_on": ["SYS-110", "SYS-120", "GUIDE-170"],
        "figures": ["extension-routing", "dependency-centrality"],
    },
    {
        "id": "GUIDE-140",
        "path": "GUIDE-140-operations-verification.md",
        "title": "Operations and Verification",
        "depends_on": ["GUIDE-100", "SYS-120", "REF-150", "GUIDE-170"],
        "figures": ["operator-path", "verification-stack", "profile-composition", "mutation-coverage"],
    },
    {
        "id": "REF-150",
        "path": "REF-150-evidence-limitations.md",
        "title": "Evidence, Limitations, and Audit Notes",
        "depends_on": ["GUIDE-100", "SYS-110", "SYS-120", "GUIDE-140", "GUIDE-170"],
        "figures": ["baseline-engine-health", "field-trial-disposition", "assurance-boundary"],
    },
    {
        "id": "REF-160",
        "path": "REF-160-agent-blueprint-guide.md",
        "title": "Agent Blueprint Guide",
        "depends_on": ["SYS-110", "SYS-120", "REF-130", "REF-150", "GUIDE-170"],
        "figures": ["agent-navigation", "question-coverage"],
    },
    {
        "id": "GUIDE-170",
        "path": "GUIDE-170-repository-release.md",
        "title": "Repository, Versioning and Release Operations",
        "depends_on": ["GUIDE-100", "SYS-110", "SYS-120", "GUIDE-140", "REF-150"],
        "figures": ["release-pipeline", "release-pin-surface"],
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def tracked_files() -> list[str]:
    # `git -C ROOT ls-files` still discovers the repository at ROOT.parent and lists
    # ROOT-relative paths even though `.git` moved outside the payload in 1.3.0 (verified
    # OUTLINES-2026-09-07.md §0.7). Do not "fix" this to `Path.rglob` — rglob would sweep
    # ignored files (caches, host-local run logs) into every derived count.
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True
    )
    return sorted(line for line in result.stdout.splitlines() if line)


def release_version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def graphviz_version(files: list[str]) -> tuple[str, bool]:
    """The Graphviz build that rendered every tracked module blueprint SVG.

    Regexes the version comment out of each tracked ``.svg`` under a module ``blueprint/``
    directory and raises if they are not unanimous — non-unanimity across renderer builds is
    exactly the defect 1.2.0 shipped (32 SVGs from 2.42.4, 3 from 2.43.0), and a figure that
    silently averaged over that disagreement would hide it instead of reporting it.
    """
    pattern = re.compile(r"<!--\s*Generated by graphviz version ([^\s]+(?:\s*\([^)]*\))?)\s*-->")
    versions: set[str] = set()
    candidates = [p for p in files if "/blueprint/" in p and p.endswith(".svg")]
    for relative in candidates:
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        match = pattern.search(text)
        if match:
            versions.add(match.group(1).strip())
    if not versions:
        raise RuntimeError("no Graphviz version comment found in any tracked module blueprint SVG")
    if len(versions) > 1:
        raise RuntimeError(f"tracked blueprint SVGs were rendered by disagreeing Graphviz builds: {sorted(versions)}")
    return next(iter(versions)), True


def transitive_dependents(nodes: list[str], edges: list[dict[str, str]]) -> dict[str, int]:
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        reverse[edge["target"]].add(edge["source"])
    counts: dict[str, int] = {}
    for start in nodes:
        seen: set[str] = set()
        queue = deque(reverse.get(start, ()))
        while queue:
            item = queue.popleft()
            if item in seen:
                continue
            seen.add(item)
            queue.extend(reverse.get(item, ()))
        counts[start] = len(seen)
    return counts


def verifier_sections() -> list[dict[str, str]]:
    path = ROOT / "runtime" / "verify.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    entry = functions["verify_framework"]
    called: list[str] = []
    for node in ast.walk(entry):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "sections" and isinstance(node.value, ast.List):
                    for item in node.value.elts:
                        if isinstance(item, ast.Call) and isinstance(item.func, ast.Name):
                            called.append(item.func.id)
    out = []
    for name in called:
        function = functions[name]
        declared_claim = ""
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "Section"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
            ):
                continue
            declared_claim = node.args[1].value
            break
        doc = ast.get_docstring(function) or ""
        protects = declared_claim or doc.splitlines()[0] if doc else declared_claim
        if not protects:
            protects = "No machine-readable protection claim is declared."
        out.append({"function": name, "protects": protects, "source": "runtime/verify.py"})
    return out


def verifier_check_codes() -> dict[str, list[str]]:
    """Every check code a ``section_*`` function in runtime/verify.py can report.

    Walks ``section.expect(condition, code, ...)`` and ``section.fail(code, ...)`` calls. The
    code argument sits at index 1 for ``expect`` (index 0 is the condition) and index 0 for
    ``fail``. A call that forwards a code computed elsewhere (for example ``finding["code"]``
    when a section replays another section's findings) is not a string literal and is skipped
    rather than guessed.
    """
    path = ROOT / "runtime" / "verify.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    out: dict[str, list[str]] = {}
    for name, function in functions.items():
        if not name.startswith("section_"):
            continue
        codes: set[str] = set()
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "section"
                and node.func.attr in {"expect", "fail"}
            ):
                continue
            index = 1 if node.func.attr == "expect" else 0
            if len(node.args) > index and isinstance(node.args[index], ast.Constant) and isinstance(node.args[index].value, str):
                codes.add(node.args[index].value)
        if codes:
            out[name] = sorted(codes)
    return out


def mutation_controls() -> dict[str, Any]:
    """Read `tools/verifier_mutation_check.py`'s own MUTATIONS list and SECTIONS map by AST.

    Returns the control name/section/expected-code triple for every planted mutation, the set
    of sections the harness wires at all, and the count — so "N mutations across M sections"
    is never typed by hand into a document again.
    """
    path = ROOT / "tools" / "verifier_mutation_check.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    controls: list[dict[str, str]] = []
    wired_sections: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "MUTATIONS":
            elements = node.value.elts if isinstance(node.value, (ast.List, ast.Tuple)) else []
            for element in elements:
                if not isinstance(element, ast.Tuple) or len(element.elts) < 3:
                    continue
                name_node, section_node, code_node = element.elts[0], element.elts[1], element.elts[2]
                if all(isinstance(item, ast.Constant) and isinstance(item.value, str) for item in (name_node, section_node, code_node)):
                    controls.append(
                        {
                            "name": name_node.value,
                            "section": section_node.value,
                            "expected_code": code_node.value,
                        }
                    )
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SECTIONS" and isinstance(node.value, ast.Dict):
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            wired_sections.append(key.value)
    return {
        "source": "tools/verifier_mutation_check.py",
        "controls": sorted(controls, key=lambda c: c["name"]),
        "wired_sections": sorted(wired_sections),
        "count": len(controls),
    }


def release_pins(files: list[str], version: str) -> dict[str, Any]:
    """Every tracked file whose bytes carry the release version, bucketed by pin class.

    Uses the already-collected `git ls-files` list plus a byte scan — never `Path.rglob`, which
    would sweep untracked/ignored files into a count that is supposed to describe the release.
    """
    tracked = set(files)
    buckets: dict[str, list[str]] = {
        "version_file": ["VERSION"],
        "release_tooling": ["01_control_plane/manifests_releases/tools/release_integrity.py"],
        "registries": ["docs/registries/FRAMEWORK.json"],
        "schemas": [
            "04_enforcement/schemas/module_manifest.schema.json",
            "04_enforcement/schemas/release_manifest.schema.json",
            "04_enforcement/schemas/release_allowlist.schema.json",
        ],
        "module_manifests": sorted(p for p in files if p.endswith("/MODULE_MANIFEST.yaml")),
        "module_narratives": sorted(p for p in files if p.endswith("/MODULE.md")),
        "test_manifest": ["09_tests_evals/TEST_MANIFEST.json"],
        "governance": [
            "governance/SUPERSESSION_LEDGER.json",
            "governance/coverage_closure_v3/release_surface_registry.json",
        ],
        "allowlist": ["RELEASE_ALLOWLIST.json"],
    }
    pins: dict[str, Any] = {}
    for bucket, candidates in buckets.items():
        matched = [
            relative
            for relative in candidates
            if relative in tracked and version in (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        ]
        pins[bucket] = {"paths": matched, "count": len(matched)}
    pins["total_pinned_files"] = sum(entry["count"] for entry in pins.values())
    return pins


def release_procedure_steps() -> list[dict[str, Any]]:
    """Ordinal + title for every `## N. Title` heading in the normative release procedure."""
    path = ROOT / "01_control_plane" / "manifests_releases" / "RELEASE_PROCEDURE.md"
    pattern = re.compile(r"^## (\d+)\. (.+)$")
    steps: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            steps.append({"ordinal": int(match.group(1)), "title": match.group(2).strip()})
    return steps


def repository_model() -> dict[str, Any]:
    """Describe the repository around the payload — degrading gracefully when it is not there.

    `ROOT.parent` is outside the payload and does not exist in a clean-room extract of the
    sealed zip. Probing for `.git` and returning an honest "not observed" object rather than
    raising means this script keeps working when it is run against an extracted release, not
    only against a git checkout.
    """
    repo_root = ROOT.parent
    if not (repo_root / ".git").exists():
        return {"observed": False, "reason": "payload extracted without its repository"}
    entries = sorted(p.name for p in repo_root.iterdir() if not p.name.startswith("."))
    return {
        "observed": True,
        "payload_directory": ROOT.name,
        "root_entries": entries,
    }


def engine_pin() -> dict[str, Any]:
    """The vendored documentation instrument's version and, when derivable, its upstream commit.

    Degrades the same way `repository_model()` does: a clean-room extract of the release does
    not carry `engine/` at all, and this must not raise merely because the instrument is absent.
    """
    repo_root = ROOT.parent
    if not (repo_root / ".git").exists():
        return {"observed": False, "reason": "payload extracted without its repository"}
    version_file = repo_root / "engine" / "PROJECT_VERSION"
    if not version_file.is_file():
        return {"observed": False, "reason": "engine checkout not present beside the payload"}
    upstream_commit = None
    log = subprocess.run(
        ["git", "-C", str(repo_root), "log", "--format=%B", "--", "engine"],
        capture_output=True,
        text=True,
    )
    if log.returncode == 0:
        match = re.search(r"ultimate-engine@([0-9a-f]{7,40})", log.stdout)
        if match:
            upstream_commit = match.group(1)
    return {
        "observed": True,
        "engine_version": version_file.read_text(encoding="utf-8").strip(),
        "upstream_commit": upstream_commit,
    }


def question_coverage() -> dict[str, Any]:
    """Derive the blueprint-only question-coverage matrix from REF-160's own routing table.

    A hand-typed coverage matrix in the document that tells other people not to ship hand-typed
    values is the defect this function exists to remove: each cell is 1 exactly when the named
    machine artifact is the one REF-160's routing table assigns to that question AND the file
    exists and is non-empty in this run.
    """
    routing: list[tuple[str, list[str]]] = [
        ("components", ["domain-model.json", "module-dependencies.json"]),
        ("change_location", ["extension-points.json"]),
        ("risk", ["module-dependencies.json"]),
        ("enforcement", ["verification-model.json"]),
        ("runtime_order", ["runtime-model.json"]),
        ("release", ["release-model.json"]),
    ]
    columns = [
        "domain-model.json",
        "module-dependencies.json",
        "extension-points.json",
        "verification-model.json",
        "runtime-model.json",
        "release-model.json",
    ]
    matrix: list[list[int]] = []
    for _, sources in routing:
        row = []
        for column in columns:
            present = column in sources and (MACHINE / column).is_file() and (MACHINE / column).stat().st_size > 0
            row.append(1 if present else 0)
        matrix.append(row)
    return {
        "row_labels": [question for question, _ in routing],
        "col_labels": [column.removesuffix(".json").replace("-", "_") for column in columns],
        "matrix": matrix,
    }


def mermaid_domain_graph(domain_edges: list[dict[str, Any]]) -> str:
    lines = ["flowchart LR"]
    for domain in DOMAIN_PURPOSES:
        lines.append(f'  {domain[:2]}["{domain}"]')
    for edge in domain_edges:
        lines.append(f'  {edge["source"][:2]} -->|"{edge["module_edges"]}"| {edge["target"][:2]}')
    return "\n".join(lines)


def mermaid_linear(nodes: list[tuple[str, str]], direction: str = "LR") -> str:
    lines = [f"flowchart {direction}"]
    for idx, (node_id, label) in enumerate(nodes):
        safe = node_id.replace(".", "_").replace("-", "_")
        lines.append(f'  {safe}["{label}"]')
        if idx:
            prev = nodes[idx - 1][0].replace(".", "_").replace("-", "_")
            lines.append(f"  {prev} --> {safe}")
    return "\n".join(lines)


def source(ref: str) -> list[dict[str, str]]:
    return [{"kind": "source", "ref": ref, "retrieved": RETRIEVED}]


def mermaid_figure(fid: str, title: str, caption: str, question: str, insight: str, code: str, ref: str) -> dict[str, Any]:
    return {
        "id": fid,
        "kind": "mermaid",
        "title": title,
        "caption": caption,
        "reader_question": question,
        "insight": insight,
        "code": code,
        "data_sources": source(ref),
    }


def bar_figure(fid: str, title: str, caption: str, question: str, insight: str, rows: list[tuple[str, int]], ref: str, unit: str = "") -> dict[str, Any]:
    return {
        "id": fid,
        "kind": "bar",
        "title": title,
        "caption": caption,
        "width": 1800,
        "height": max(440, 60 * len(rows)),
        "unit": unit,
        "reader_question": question,
        "insight": insight,
        "items": [{"label": label, "value": value} for label, value in rows],
        "data_sources": source(ref),
    }


def main() -> int:
    modules = read_json(REGISTRIES / "MODULE_INDEX.json")["modules"]
    interfaces = read_json(REGISTRIES / "INTERFACE_INDEX.json")["interfaces"]
    requirements = read_json(REGISTRIES / "CANONICAL_REQUIREMENTS.json")["requirements"]
    profiles_adapters = read_json(REGISTRIES / "PROFILE_ADAPTER_INDEX.json")
    dag = read_json(REGISTRIES / "AUTHORITY_DEPENDENCY_DAG.json")
    framework = read_json(REGISTRIES / "FRAMEWORK.json")
    allowlist = read_json(ROOT / "RELEASE_ALLOWLIST.json")
    files = tracked_files()
    version = release_version()

    by_domain = Counter(path.split("/", 1)[0] for path in files if path[:2].isdigit())
    by_ext = Counter(Path(path).suffix or "[none]" for path in files)
    modules_by_layer = Counter(item["layer"] for item in modules)

    module_by_id = {item["module_id"]: item for item in modules}
    direct_dependents = Counter(edge["target"] for edge in dag["edges"])
    direct_dependencies = Counter(edge["source"] for edge in dag["edges"])
    transitive = transitive_dependents(dag["nodes"], dag["edges"])
    risk_rows = sorted(
        [
            {
                "module_id": mid,
                "name": module_by_id[mid]["name"],
                "layer": module_by_id[mid]["layer"],
                "direct_dependents": direct_dependents[mid],
                "transitive_dependents": transitive[mid],
                "direct_dependencies": direct_dependencies[mid],
            }
            for mid in dag["nodes"]
        ],
        key=lambda row: (-row["transitive_dependents"], -row["direct_dependents"], row["module_id"]),
    )

    aggregate: Counter[tuple[str, str]] = Counter()
    for edge in dag["edges"]:
        source_layer = module_by_id[edge["source"]]["layer"]
        target_layer = module_by_id[edge["target"]]["layer"]
        if source_layer != target_layer:
            aggregate[(source_layer, target_layer)] += 1
    domain_edges = [
        {"source": src, "target": dst, "module_edges": count}
        for (src, dst), count in sorted(aggregate.items())
    ]

    sys.path.insert(0, str(ROOT))
    from runtime.documents import DOCUMENT_STEPS  # noqa: PLC0415
    from runtime.rail import RAIL_STEPS  # noqa: PLC0415

    runtime_model = {
        "sources": ["runtime/rail.py", "runtime/documents.py", "docs/RUNTIME_GUIDE.md"],
        "project_rail": [
            {
                "id": step.step_id,
                "ordinal": step.ordinal,
                "command": step.command,
                "title": step.title,
                "why": step.why,
                "repeatable": step.repeatable,
            }
            for step in RAIL_STEPS
        ],
        "document_rail": [
            {
                "id": step.step_id,
                "ordinal": step.ordinal,
                "title": step.title,
                "intent": step.intent,
                "artifacts": list(step.artifacts),
            }
            for step in DOCUMENT_STEPS
        ],
        "mutation_order": ["authorize against rail", "write artifact", "append ledger entry", "update project state"],
    }

    core_requirements = len(requirements)
    framework_counts = framework.get("counts", {})
    assert core_requirements == framework_counts.get("core_requirements"), (
        f"CANONICAL_REQUIREMENTS.json holds {core_requirements} requirements but "
        f"FRAMEWORK.json counts.core_requirements is {framework_counts.get('core_requirements')!r}"
    )
    requirements_total = framework_counts.get("requirements")
    successor_governance_requirements = framework_counts.get("successor_governance_requirements")

    graphviz_build, graphviz_unanimous = graphviz_version(files)

    inventory = {
        "source": "git ls-files and canonical registries",
        "release_version": version,
        "tracked_files": len(files),
        "tracked_by_numbered_domain": {k: by_domain[k] for k in DOMAIN_PURPOSES},
        "tracked_by_extension": dict(sorted(by_ext.items())),
        "canonical_modules": len(modules),
        "core_requirements": core_requirements,
        "requirements_total": requirements_total,
        "successor_governance_requirements": successor_governance_requirements,
        "interfaces": len(interfaces),
        "profiles": len(profiles_adapters["profiles"]),
        "adapters": len(profiles_adapters["adapters"]),
        "python_modules": sum(1 for path in files if path.endswith(".py")),
        "markdown_documents": sum(1 for path in files if path.endswith(".md")),
        "graphviz_version": graphviz_build,
        "graphviz_renderer_unanimous": graphviz_unanimous,
    }
    domain_model = {
        "source": ["docs/registries/MODULE_INDEX.json", "docs/registries/AUTHORITY_DEPENDENCY_DAG.json"],
        "domains": [
            {
                "id": domain,
                "purpose": purpose,
                "tracked_files": by_domain[domain],
                "canonical_modules": modules_by_layer[domain],
            }
            for domain, purpose in DOMAIN_PURPOSES.items()
        ],
        "cross_domain_dependencies": domain_edges,
    }
    dependency_model = {
        "source": "docs/registries/AUTHORITY_DEPENDENCY_DAG.json",
        "edge_direction": dag["authority_rule"],
        "acyclic": dag["acyclic"],
        "module_edges": dag["edges"],
        "centrality": risk_rows,
    }
    check_codes = verifier_check_codes()
    sections_in_order = verifier_sections()
    for row in sections_in_order:
        row["check_codes"] = check_codes.get(row["function"], [])
    verification_model = {
        "source": ["runtime/verify.py", "09_tests_evals/run_all.py", "tools/verifier_mutation_check.py"],
        "framework_sections_in_execution_order": sections_in_order,
        "aggregate_entry_point": "09_tests_evals/run_all.py",
        "aggregate_controls": [
            "04_enforcement/validators/absolute_validate.py",
            "tests/run_successor_controls.py",
            "tools/deep_verify.py",
            "tools/verifier_mutation_check.py",
            "tools/validate_v2_contracts.py",
        ],
        "mutation_controls": mutation_controls(),
    }
    pins = release_pins(files, version)
    extension_points = {
        "source": [
            "docs/ARCHITECTURE.md",
            "docs/CAPABILITY_AND_SECURITY_GUIDE.md",
            "05_platform_adapters/MODULE.md",
            "docs/registries/MODULE_INDEX.json",
        ],
        "changes": [
            {
                "kind": "new_rule",
                "primary_path": "the canonical owner package named by docs/registries/MODULE_INDEX.json",
                "also_update": [
                    "MODULE.md and requirements.json in that owner package",
                    "machine/policy.json and positive/negative/adversarial fixtures",
                    "docs/registries/CANONICAL_REQUIREMENTS.json and FRAMEWORK_GRAPH.jsonl",
                    "04_enforcement validators or runtime checks only when deterministic enforcement is required",
                ],
            },
            {
                "kind": "new_capability",
                "primary_path": "02_capabilities",
                "also_update": [
                    "02_capabilities/capability_manager",
                    "capability health, permission, fallback, provenance, and quarantine records",
                    "profiles that opt into the capability",
                ],
            },
            {
                "kind": "new_platform_adapter",
                "primary_path": "05_platform_adapters/<adapter>",
                "also_update": [
                    "docs/registries/PROFILE_ADAPTER_INDEX.json",
                    "05_platform_adapters tests and integration contracts",
                    "profiles that permit the adapter",
                ],
            },
            {
                "kind": "release_version",
                "primary_path": "VERSION",
                "also_update": sorted(bucket for bucket in pins if bucket not in ("version_file", "total_pinned_files")),
            },
        ],
    }
    procedure_steps = release_procedure_steps()
    release_model = {
        "source": [
            "01_control_plane/manifests_releases/RELEASE_PROCEDURE.md",
            "01_control_plane/manifests_releases/tools/release_integrity.py",
            "docs/registries/FRAMEWORK.json",
            "RELEASE_ALLOWLIST.json",
        ],
        "repository": repository_model(),
        "engine_pin": engine_pin(),
        "pins": pins,
        "procedure": procedure_steps,
        "baseline_chain": framework.get("baseline_chain", []),
        "predecessor": framework.get("predecessor_release", {}),
        "allowlist": {
            "release_id": allowlist.get("release_id"),
            "candidate_id": allowlist.get("candidate_id"),
            "policy": allowlist.get("policy"),
            "record_count": allowlist.get("record_count"),
        },
    }

    write_json(MACHINE / "inventory.json", inventory)
    write_json(MACHINE / "domain-model.json", domain_model)
    write_json(MACHINE / "module-dependencies.json", dependency_model)
    write_json(MACHINE / "runtime-model.json", runtime_model)
    write_json(MACHINE / "verification-model.json", verification_model)
    write_json(MACHINE / "extension-points.json", extension_points)
    write_json(MACHINE / "document-index.json", {"documents": DOCUMENTS})
    write_json(MACHINE / "release-model.json", release_model)

    # evaluation-baseline.json and limitations-register.json are READ inputs, never written by
    # this script (§E in OUTLINES-2026-09-07.md): the first is a frozen 2026-09-01 field-trial
    # record, the second is authored once per finding with its resolving control. Both back
    # REF-150's figures without this script re-measuring or re-typing either one.
    baseline = read_json(MACHINE / "evaluation-baseline.json")
    limitations_register = read_json(MACHINE / "limitations-register.json")

    domain_graph = mermaid_domain_graph(domain_edges)
    rail_graph = mermaid_linear([(s["id"], f'{s["id"]} · {s["command"]}') for s in runtime_model["project_rail"]], "TB")
    doc_graph = mermaid_linear([(s["id"], s["id"]) for s in runtime_model["document_rail"]], "TB")
    release_pipeline_graph = mermaid_linear(
        [(f"step{step['ordinal']}", f"{step['ordinal']}. {step['title']}") for step in procedure_steps], "TB"
    )
    write_text(GRAPH_SOURCE / "domain-dependencies.mmd", domain_graph)
    write_text(GRAPH_SOURCE / "project-rail.mmd", rail_graph)
    write_text(GRAPH_SOURCE / "document-rail.mmd", doc_graph)
    write_text(GRAPH_SOURCE / "release-pipeline.mmd", release_pipeline_graph)

    top_risk = [(row["module_id"].split(".")[-1], row["transitive_dependents"]) for row in risk_rows[:10]]
    representation_rows = sorted(by_ext.items(), key=lambda item: (-item[1], item[0]))[:8]

    operating_model = """flowchart TB
  Builder["Builder Program"] --> Framework["Absolute Framework"]
  Framework --> Project["Downstream Project"]
  Kernel["00 kernel invariants"] --> Control["01 control plane"]
  Control --> Runtime["10 runtime rail"]
  Runtime --> Evidence["evidence and gate"]
  Evidence --> Verify["fresh verification"]
  Verify --> Release["exact-identity release"]
  Framework --> Kernel
  Project -. feedback for future release .-> Builder"""
    authority_of_facts_graph = """flowchart TB
  Version["VERSION — release identity"] --> Manifests["MANIFEST.json, SHA256SUMS.txt,\n.absolute/release/* (derived, prepare_release_metadata.py only)"]
  Version --> RegistryCheck["FRAMEWORK.json, RELEASE_ALLOWLIST.json\n(derived, checked against VERSION)"]
  Modules["Canonical module packages — module semantics"] --> ModuleIndex["MODULE_INDEX.json, AUTHORITY_DEPENDENCY_DAG.json\n(derived index)"]
  Requirements["requirements.json per package — requirements and interfaces"] --> ReqRegistry["CANONICAL_REQUIREMENTS.json, INTERFACE_INDEX.json\n(derived, reconciled)"]
  VerifyRun["A run of tools/deep_verify.py, bound to a tree identity — verification results"] --> TestManifest["TEST_MANIFEST.json (a description, not the surface)"]
  RootDocs["README.md, CHANGELOG.md, LIMITATIONS.md, docs/*.md — the framework's own documentation"] --> DerivedDocs["docs/ultimate-engine/ (this set — derived documentation)"]"""
    mutation_graph = """sequenceDiagram
  participant CLI
  participant Rail
  participant Artifact
  participant Ledger
  participant State
  CLI->>Rail: authorize requested command
  Rail-->>CLI: permitted step or refusal
  CLI->>Artifact: write bounded artifact
  CLI->>Ledger: append hash-chained entry
  CLI->>State: update durable state
  State-->>CLI: exact next action"""
    repository_layout_graph = """flowchart TB
  Repo["Repository (git) — repository root"] --> Payload["absolute-canonical-framework-v1.3.1/\nthe release payload — no .git inside"]
  Repo --> EngineDir["engine/\nvendored instrument — outside release identity"]
  Repo --> ReleaseDir["_release/\nsealed zip + detached sha256; _release/predecessors/"]
  Repo --> RepoRecords["README.md, RELEASE_STAMP.json,\nMANIFEST.sha256, docs/doc-pipeline/"]
  Payload --> RootName["basename must equal ROOT_NAME —\nrelease_tree_integrity checks it"]
  Payload --> NoGit["FORBIDDEN_PARTS denylists .git —\na working tree can now pass release_tree_integrity"]"""
    extension_graph = """flowchart LR
  Rule["New rule"] --> Owner["canonical owner package"]
  Owner --> Registry["requirements and graph registries"]
  Owner --> Enforcement["validator/runtime check if executable"]
  Capability["New capability"] --> CapRoot["02_capabilities"]
  CapRoot --> CapMgr["capability_manager"]
  Adapter["New adapter"] --> AdapterRoot["05_platform_adapters/<adapter>"]
  AdapterRoot --> PAIndex["PROFILE_ADAPTER_INDEX"]
  CapMgr --> Profiles["opt-in profiles"]
  PAIndex --> Profiles
  Version["Change the release version"] --> VersionFile["VERSION"]
  VersionFile --> VersionPins["release_integrity constants, FRAMEWORK.json, schemas,\nmodule manifests, module narratives, TEST_MANIFEST, governance"]
  VersionPins --> Allowlist["RELEASE_ALLOWLIST.json regenerated last"]"""
    operator_graph = """flowchart TB
  VerifyPackage["verify framework package"] --> Select["select profile and adapter"]
  Select --> Init["absolute init"]
  Init --> Next["absolute next"]
  Next --> Bounded["perform only the named action"]
  Bounded --> Next
  Next --> Pass2["fresh pass 2"]
  Pass2 --> Verify["absolute verify --record"]
  Verify --> Release["absolute release outside project tree"]"""
    verification_graph = """flowchart TB
  RunAll["09_tests_evals/run_all.py"] --> Validator["deterministic validator"]
  RunAll --> Successor["successor controls"]
  RunAll --> Deep["deep verifier"]
  RunAll --> Mutation["verifier mutation check"]
  RunAll --> V2["V2 contract validator (tools/validate_v2_contracts.py)"]
  Deep --> Sections["identity → structure → representation → contracts → semantics → security → governance → runtime → validator → simulation"]
  Mutation --> Alive["requires planted defects to be caught"]"""
    release_pin_codes = {
        "structure": sorted(c for c in check_codes.get("section_structure", []) if "RELEASE" in c or "NARRATIVE" in c),
        "governance": sorted(c for c in check_codes.get("section_governance", []) if c.startswith("ALLOWLIST_RELEASE")),
    }
    cross_rep_graph = (
        "flowchart LR\n"
        '  Version["VERSION"] --> Manifest["MODULE_MANIFEST.yaml × 33"]\n'
        '  Version --> Narrative["MODULE.md front matter × 33"]\n'
        '  Version --> Framework["docs/registries/FRAMEWORK.json"]\n'
        '  Version --> Allowlist["RELEASE_ALLOWLIST.json"]\n'
        f'  Manifest -.->|"{", ".join(c for c in release_pin_codes["structure"] if "PIN" in c)}"| Version\n'
        f'  Narrative -.->|"{", ".join(c for c in release_pin_codes["structure"] if "NARRATIVE" in c)}"| Version\n'
        f'  Framework -.->|"{", ".join(c for c in release_pin_codes["structure"] if c.startswith("FRAMEWORK_REGISTRY"))}"| Version\n'
        f'  Allowlist -.->|"{", ".join(release_pin_codes["governance"])}"| Version'
    )
    assurance_graph = """flowchart LR
  Internal["Internal deterministic verification"] --> Hash["exact candidate identity"]
  Hash --> External["External independent certification pending"]
  Ledger["Local hash chain"] --> Tamper["detects local edit/remove/reorder"]
  Anchor["Detached external anchor"] --> Rewrite["detects full-chain rewrite"]
  Rollback["Recorded rollback statement"] -. not executed .-> Gap["rollback remains unproved"]
  Dot["Installed Graphviz"] --> Parity["visual parity check"]"""
    agent_graph = """flowchart TB
  Start["Start with machine/document-index.json"] --> Components["domain-model.json"]
  Components --> Dependencies["module-dependencies.json"]
  Dependencies --> Runtime["runtime-model.json"]
  Runtime --> Change["extension-points.json"]
  Change --> ReleaseModel["release-model.json"]
  ReleaseModel --> Evidence["evaluation-baseline.json"]
  Evidence --> Interactive["graphs/structure/graph.json"]"""

    mutation_by_section = Counter(control["section"] for control in mutation_controls()["controls"])
    mutation_rows = sorted(mutation_by_section.items())

    disposition_counts = Counter(row["disposition"] for row in limitations_register.get("findings", []))
    disposition_rows = sorted(disposition_counts.items())

    pin_rows = [
        (bucket, entry["count"])
        for bucket, entry in sorted(pins.items())
        if bucket != "total_pinned_files"
    ]

    specs: dict[str, list[dict[str, Any]]] = {
        "GUIDE-100-project-guide_spec.json": [
            mermaid_figure("domain-operating-model", "Authority and operating model", "The reusable framework governs a downstream project through kernel invariants, a durable control plane, the executable rail, evidence, verification, and release.", "How does authority flow from the builder to a governed downstream release?", "Authority flows one way into a downstream project; project feedback can inform a future framework version but cannot mutate the current release.", operating_model, "docs/EXECUTIVE_OVERVIEW.md; docs/ARCHITECTURE.md"),
            bar_figure("tracked-artifacts-by-domain", "Tracked artifacts by numbered domain", "Counts are derived from git ls-files; two-digit labels identify the framework's numbered domain boundaries and the machine domain model provides their full names.", "Where is the release's tracked material concentrated?", "The distribution is documentation/data heavy, which is why a Python-only blueprint cannot stand in for the whole framework.", [(k.split("_")[0], by_domain[k]) for k in DOMAIN_PURPOSES], "git ls-files", " files"),
            mermaid_figure("authority-of-facts", "Authority of facts", "For five kinds of fact this release makes, one artifact is authoritative and the rest are derived from it and checked against it.", "For each kind of fact, which artifact is authoritative and which are derived?", "Release identity, module semantics, requirements, verification results and documentation each have exactly one authority; every other artifact is derived from it and checked against it.", authority_of_facts_graph, "docs/registries/FRAMEWORK.json; runtime/verify.py"),
        ],
        "SYS-110-architecture_spec.json": [
            mermaid_figure("domain-dependencies", "Cross-domain authority dependencies", "An edge points from a consuming domain to an earlier-authority domain it depends on; labels are aggregated module-edge counts.", "Which numbered domains depend on which others?", "Kernel dependencies sit upstream of the control, capability, knowledge, enforcement, profile, test, and runtime layers; the runtime is an executor, not a new authority source.", domain_graph, "docs/registries/AUTHORITY_DEPENDENCY_DAG.json"),
            bar_figure("dependency-centrality", "Modules with the broadest transitive dependent set", "Risk proxy derived from the canonical authority DAG: more transitive dependents means a change can invalidate more downstream owners.", "Which canonical modules are riskiest to change?", "The highest-ranked modules should receive the broadest impact analysis because their authority is consumed transitively across the graph.", top_risk, "docs/registries/AUTHORITY_DEPENDENCY_DAG.json", " dependents"),
            bar_figure("representation-mix", "Tracked representation mix", "Largest extension groups derived from git ls-files.", "Is this framework mostly executable code or governed representations?", "Machine-readable JSON and Markdown dominate; executable Python is a small slice, so architecture cannot be inferred from imports alone.", representation_rows, "git ls-files", " files"),
            mermaid_figure("repository-layout", "Repository layout", "How the repository is arranged around the release payload, the vendored instrument, and the sealed artifacts.", "How is the repository arranged around the release payload?", "The payload is a subdirectory with no version-control metadata inside it, so the tree-integrity control can pass on a working tree; the instrument and the sealed artifacts sit beside it, outside release identity.", repository_layout_graph, "01_control_plane/manifests_releases/tools/release_integrity.py; CHANGELOG.md"),
        ],
        "SYS-120-runtime-enforcement_spec.json": [
            mermaid_figure("project-rail", "Project rail", "The single permitted project action advances through the runtime rail in source order.", "What is the project's enforced runtime sequence?", "The rail puts document creation and sealing before evidence and gates, then requires checkpoint, a non-author pass, recorded verification, and release.", rail_graph, "runtime/rail.py"),
            mermaid_figure("document-rail", "Governed document authoring rail", "A document package advances through each representation in source order.", "In what order does the runtime author a canonical document package?", "Narrative precedes machine and visual forms, and publication follows tests and integration; sealing is impossible while any step or template marker remains.", doc_graph, "runtime/documents.py"),
            mermaid_figure("governed-mutation", "Governed mutation write order", "Every mutating command follows the same write order.", "What is written first, and what may not happen until when?", "Authorization precedes every write; the ledger entry precedes the state update so a crash leaves evidence of an unapplied action rather than unrecorded state.", mutation_graph, "runtime/engine.py"),
            mermaid_figure("cross-representation-pin", "Cross-representation release pin", "One release version lives in four artifacts; the labeled edges name the check codes that compare each one back to VERSION.", "One release version lives in four artifacts — what compares them?", "Four structure codes and one governance code turn a decorative pin into a read one; before 1.3.0 nothing compared the narrative to its manifest.", cross_rep_graph, "runtime/verify.py"),
        ],
        "REF-130-extension-points_spec.json": [
            mermaid_figure("extension-routing", "Where changes belong", "Primary extension paths and their required registry/profile follow-through, including the release-version route.", "Which part changes for a new rule, capability, adapter, or release version?", "Rules begin at one canonical semantic owner, capabilities remain under the capability layer, host translation remains isolated under platform adapters, and a version bump routes through every pin before the allowlist.", extension_graph, "docs/ARCHITECTURE.md; docs/CAPABILITY_AND_SECURITY_GUIDE.md"),
            bar_figure("dependency-centrality", "Change-risk centrality", "Transitive dependent counts from the authority DAG.", "Which module changes demand the widest revalidation?", "Risk follows dependency reach, not file size; use the machine model for the complete ordered list.", top_risk, "docs/registries/AUTHORITY_DEPENDENCY_DAG.json", " dependents"),
        ],
        "GUIDE-140-operations-verification_spec.json": [
            mermaid_figure("operator-path", "Operator path", "The documented path from package verification through governed release.", "How does an operator adopt and run the framework?", "After profile and adapter selection, the operator follows absolute next rather than choosing arbitrary mutations; verification and release remain distinct terminal acts.", operator_graph, "docs/INSTALLATION_GUIDE.md; docs/RUNTIME_GUIDE.md"),
            mermaid_figure("verification-stack", "Verification stack", "The aggregate test entry point calls five independent control families.", "What does the subject verify, in what order, and what protects the verifier itself?", "The deep verifier checks the package while the mutation checker separately proves named defect classes still fire and the V2 contract validator checks the machine-contract layer; a clean deep pass alone is insufficient.", verification_graph, "09_tests_evals/run_all.py; runtime/verify.py"),
            {
                "id": "profile-composition",
                "kind": "heatmap",
                "title": "Profile layer composition",
                "caption": "Required-layer matrix derived from PROFILE_ADAPTER_INDEX.json.",
                "width": 1000,
                "height": 420,
                "min_value": 0,
                "max_value": 1,
                "reader_question": "Which numbered layers does each profile require?",
                "insight": "The minimal profile keeps kernel, control, and enforcement mandatory; broader profiles add capability, knowledge, adapters, tests, and runtime through the resolved module set.",
                "row_labels": [p["profile_id"].split(".")[-1] for p in profiles_adapters["profiles"]],
                "col_labels": [domain.split("_")[0] for domain in DOMAIN_PURPOSES],
                "matrix": [[1 if layer in p["required_layers"] else 0 for layer in DOMAIN_PURPOSES] for p in profiles_adapters["profiles"]],
                "data_sources": source("docs/registries/PROFILE_ADAPTER_INDEX.json"),
            },
            bar_figure("mutation-coverage", "Mutation controls by verifier section", "One bar per section the mutation harness wires; height is the number of planted defects that section must catch.", "Which verifier sections have a live mutation control, and how many?", "Liveness is proven per section, not per verifier; 1.3.0 newly wired structure and governance, which had none.", mutation_rows, "tools/verifier_mutation_check.py", " controls"),
        ],
        "REF-150-evidence-limitations_spec.json": [
            bar_figure("baseline-engine-health", "Engine-on-subject baseline", "Untouched foreign-project health result captured 2026-09-01 against the framework at release 1.1.0, before any governed documents in this set existed.", "What did the engine report before any governed subject documents existed?", "Most failures asked for the engine repository's own scaffolding inside the subject; the baseline therefore measures portability assumptions as much as missing documentation.", [("PASS", baseline["engine_health"]["pass"]), ("FAIL", baseline["engine_health"]["fail"]), ("SKIP", baseline["engine_health"]["skip"])], "docs/ultimate-engine/machine/evaluation-baseline.json", " checks"),
            bar_figure("field-trial-disposition", "2026-09-01 findings, by disposition", "Every finding this documentation set has ever recorded, sourced from the limitations register rather than counted by hand.", "Of the findings this set has recorded, how many did 1.3.0 close and how many stand?", "The majority of the 2026-09-01 findings are closed with a new control behind each; what remains is a small set of standing properties, not a backlog.", disposition_rows, "docs/ultimate-engine/machine/limitations-register.json", " findings"),
            mermaid_figure("assurance-boundary", "Assurance boundary", "Controls the subject explicitly claims, plus the limitations that keep them from becoming certification claims.", "What does internal verification prove, and what remains outside it?", "Internal verification binds claims to an identity, but independent certification, externally stored anchors, rollback rehearsal, content truth, and cross-host locking remain outside the guarantee.", assurance_graph, "LIMITATIONS.md; SECURITY.md"),
        ],
        "REF-160-agent-blueprint-guide_spec.json": [
            mermaid_figure("agent-navigation", "Blueprint-first navigation", "Read order for an agent restricted to blueprints, figures, and JSON.", "How should a fresh agent navigate the generated structural layer?", "The machine index routes from component identity to dependencies, runtime order, extension points, the release model, and the interactive file graph without requiring prose.", agent_graph, "docs/ultimate-engine/machine/document-index.json"),
            {
                "id": "question-coverage",
                "kind": "heatmap",
                "title": "Blueprint-only question coverage",
                "caption": "One means the named structural artifact is the one REF-160's routing table assigns to that question and the file is present and non-empty; zero means it is not.",
                "width": 1000,
                "height": 430,
                "min_value": 0,
                "max_value": 1,
                "reader_question": "Can the blueprint pack answer the six agent-usability questions without prose?",
                "insight": "The pack assigns at least one direct machine source to every required question, including the release-versioning question 1.3.0 added; the 2026-09-01 test independently checked whether the first five assignments were sufficient.",
                **question_coverage(),
                "data_sources": source("docs/ultimate-engine/machine/document-index.json"),
            },
        ],
        "GUIDE-170-repository-release_spec.json": [
            mermaid_figure("release-pipeline", "Release pipeline", "Nodes are the release procedure's own numbered steps, in order, so this figure cannot drift from the normative procedure it summarizes.", "How does a repository become a sealed, verifiable release?", "Metadata binds to the frozen payload, the artifact is verified rather than the tree it was built from, and reproduction is a separate step from building.", release_pipeline_graph, "01_control_plane/manifests_releases/RELEASE_PROCEDURE.md"),
            bar_figure("release-pin-surface", "Tracked files pinned to the release version, by class", "Counts of tracked files whose bytes carry the current release version, bucketed by what kind of artifact they are.", "How many artifacts must move when the release version moves?", "The version is one string in VERSION and a pin in dozens of files across eight other classes; three of those four representation classes were unchecked before 1.3.0.", pin_rows, "git ls-files; runtime/verify.py", " files"),
        ],
    }
    for name, spec in specs.items():
        write_json(DOC_ROOT / name, spec)

    print(
        "derived documentation model: "
        f"{len(files)} tracked files, {len(modules)} canonical modules, "
        f"{len(dag['edges'])} authority edges, {len(specs)} figure sidecars"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
