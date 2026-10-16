#!/usr/bin/env python3
"""Prove the deep verifier's checks actually fire.

``tools/deep_verify.py`` reporting ``PASS`` on a clean tree is consistent with
two very different situations: every check ran and found nothing, or a check
silently stopped running. Nothing in the package distinguished them, and the
deep verifier is the only test of the runtime — if it is wrong, nothing catches
it.

This harness closes that gap the way the framework closes every other one: by
execution rather than assertion. It copies the tree, injects one known defect at
a time, runs the section that is supposed to catch it, and requires the expected
finding code to appear. A mutation that survives is reported as a finding
against the *verifier*, not the tree.

It is deliberately not a substitute for the deep verifier. It answers one
question the deep verifier cannot answer about itself: are these checks alive?

    python3 tools/verifier_mutation_check.py [--report out.json]
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import verify as V  # noqa: E402


def _edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"mutation anchor not found in {path.name}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Each mutation: a name, the section that must catch it, the finding code that
# must appear, and the edit. Every entry is a defect this package has actually
# shipped or was one edit away from shipping.
MUTATIONS: list[tuple[str, str, str, Callable[[Path], None]]] = [
    (
        "extra_untracked_file_in_payload",
        "identity",
        "TREE_INTEGRITY_FAIL",
        lambda root: (root / "00_kernel/UNDECLARED.md").write_text("stray\n", encoding="utf-8"),
    ),
    (
        "indented_heading_hides_narrative_in_a_code_block",
        "representation",
        "DOC_MARKDOWN_INDENTED_HEADING",
        lambda root: _edit(next(root.glob("00_kernel/*/MODULE.md")), "\n## ", "\n    ## "),
    ),
    (
        "tool_entry_point_may_write_bytecode_into_the_tree",
        "runtime",
        "TOOL_MAY_MUTATE_SOURCE_TREE",
        lambda root: _edit(root / "runtime/cli.py", "sys.dont_write_bytecode = True", "pass  # removed"),
    ),
    (
        "mutation_no_longer_serialized_against_concurrent_runs",
        "runtime",
        "MUTATION_NOT_SERIALIZED",
        lambda root: _edit(root / "runtime/engine.py", "@governed\ndef add_evidence(", "def add_evidence("),
    ),
    (
        "actor_identity_compared_raw_so_a_self_review_passes",
        "runtime",
        "ACTOR_IDENTITY_NOT_NORMALIZED",
        lambda root: _edit(
            root / "runtime/util.py",
            'folded = re.sub(r"[\\s_.-]+", " ", str(value or "")).strip().casefold()',
            'folded = str(value or "")',
        ),
    ),
    (
        "rail_dead_end_left_unrepairable",
        "runtime",
        "RAIL_DEAD_END_UNREPAIRABLE",
        lambda root: _edit(
            root / "runtime/rail.py",
            'CORRECTIVE_COMMANDS: dict[str, frozenset[str]] = {\n    "doc abandon": frozenset({"S5.DOCUMENTS_AUTHORED", "S6.DOCUMENTS_SEALED"}),\n}',
            "CORRECTIVE_COMMANDS: dict[str, frozenset[str]] = {}",
        ),
    ),
    (
        "install_no_longer_refuses_the_framework_tree",
        "simulation",
        "SIMULATION_NOT_REFUSED",
        lambda root: _edit(
            root / "runtime/engine.py",
            "    if resolved == FRAMEWORK_ROOT or FRAMEWORK_ROOT in resolved.parents or resolved in FRAMEWORK_ROOT.parents:",
            "    if False:",
        ),
    ),
    (
        "narrative_release_pin_drifts_from_manifest_and_VERSION",
        "structure",
        "MODULE_NARRATIVE_RELEASE_DRIFT",
        lambda root: _edit(
            next(root.glob("00_kernel/*/MODULE.md")),
            "framework_release: " + (root / "VERSION").read_text(encoding="utf-8").strip(),
            "framework_release: 1.0.0",
        ),
    ),
    (
        "manifest_release_pin_drifts_from_VERSION",
        "structure",
        "MODULE_RELEASE_PIN_DRIFT",
        lambda root: _edit(
            next(root.glob("00_kernel/*/MODULE_MANIFEST.yaml")),
            "framework_release: " + (root / "VERSION").read_text(encoding="utf-8").strip(),
            "framework_release: 0.0.0",
        ),
    ),
    (
        "allowlist_record_removed_while_file_remains",
        "governance",
        "ALLOWLIST_RECORD_SET_DRIFT",
        lambda root: (root / "RELEASE_ALLOWLIST.json").write_text(
            json.dumps(
                {
                    **json.loads((root / "RELEASE_ALLOWLIST.json").read_text(encoding="utf-8")),
                    "records": json.loads((root / "RELEASE_ALLOWLIST.json").read_text(encoding="utf-8"))["records"][1:],
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        ),
    ),
    (
        "seal_accepts_a_package_still_full_of_template_text",
        "simulation",
        "SIMULATION_NOT_REFUSED",
        lambda root: _edit(
            root / "runtime/docvalidate.py",
            "    for todo in scan_todos(directory):",
            "    for todo in []:",
        ),
    ),
]

SECTIONS = {
    "identity": lambda root: V.section_identity(root),
    "structure": lambda root: V.section_structure(root),
    "governance": lambda root: V.section_governance(root),
    "representation": lambda root: V.section_representation(root),
    "runtime": lambda root: V.section_runtime(root),
    "simulation": lambda root: V.section_simulation(root),
}


def run() -> dict:
    results = []
    for name, section_name, expected, mutate in MUTATIONS:
        workspace = Path(tempfile.mkdtemp(prefix="abs-mutate-"))
        target = workspace / ROOT.name
        detected, detail = False, ""
        try:
            shutil.copytree(ROOT, target, symlinks=True)
            mutate(target)
            # Import the *mutated* copy so a mutation to runtime code is the
            # code under test, not the code doing the testing.
            sys.path.insert(0, str(target))
            for module in [key for key in sys.modules if key == "runtime" or key.startswith("runtime.")]:
                del sys.modules[module]
            import importlib

            mutated = importlib.import_module("runtime.verify")
            section = {
                "identity": mutated.section_identity,
                "structure": mutated.section_structure,
                "governance": mutated.section_governance,
                "representation": mutated.section_representation,
                "runtime": mutated.section_runtime,
                "simulation": mutated.section_simulation,
            }[section_name](target)
            codes = {finding["code"] for finding in section.result()["findings"]}
            detected = expected in codes
            detail = f"expected {expected}; section reported {sorted(codes) or 'nothing'}"
        except Exception as exc:  # a mutation that crashes the verifier is also undetected
            detail = f"{type(exc).__name__}: {exc}"
        finally:
            sys.path = [item for item in sys.path if item != str(target)]
            for module in [key for key in sys.modules if key == "runtime" or key.startswith("runtime.")]:
                del sys.modules[module]
            shutil.rmtree(workspace, ignore_errors=True)
        results.append(
            {"mutation": name, "section": section_name, "expected_code": expected,
             "detected": detected, "detail": detail}
        )

    undetected = [item for item in results if not item["detected"]]
    return {
        "schema_version": "1.0.0",
        "report": "ABSOLUTE_VERIFIER_MUTATION_CHECK",
        "intent": "Every injected defect must be reported by the check that claims to catch it.",
        "mutations_run": len(results),
        "undetected": len(undetected),
        "status": "PASS" if not undetected else "FAIL",
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", help="write the JSON result here")
    args = parser.parse_args()
    payload = run()
    if args.report:
        Path(args.report).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Verifier mutation check: {payload['status']}")
    for item in payload["results"]:
        print(f"  {'caught ' if item['detected'] else 'MISSED '} {item['expected_code']:<34} {item['mutation']}")
        if not item["detected"]:
            print(f"           {item['detail']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
