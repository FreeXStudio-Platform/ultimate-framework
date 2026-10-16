#!/usr/bin/env python3
"""Prove that nothing semantic was dropped between a predecessor release and this one.

A remediation pass can always make a verifier green by deleting whatever it was
complaining about. This check makes that route visible: it compares the semantic
inventory of a predecessor tree against this one and reports every module,
requirement, interface, concept, profile, adapter, governance record, and
document that exists there and not here.

Removals are not forbidden — a genuinely redundant artifact may go — but every
one must be listed in ``governance/SUPERSESSION_LEDGER.json`` with a reason, and
an unlisted removal is a hard failure.

    python3 tools/check_no_loss.py --predecessor <path-to-extracted-predecessor>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path) -> dict[str, set[str]]:
    """The semantic denominator of a framework tree."""
    import yaml

    registries = root / "docs/registries"
    modules: set[str] = set()
    requirements: set[str] = set()
    for manifest_path in root.rglob("MODULE_MANIFEST.yaml"):
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        modules.add(manifest["module_id"])
        requirements |= set(manifest.get("requirements", []))
    interfaces = {item["interface_id"] for item in _load(registries / "INTERFACE_INDEX.json")["interfaces"]}
    concepts = {item["concept_id"] for item in _load(registries / "CONCEPT_REGISTRY.json")["concepts"]}
    profiles = {path.parent.name for path in (root / "06_project_profiles").glob("*/profile.json")}
    adapters = {path.parent.name for path in (root / "05_platform_adapters").glob("*/adapter.json")}
    governance = {path.name for path in (root / "governance").rglob("*") if path.is_file()}
    documents = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".dot", ".svg", ".py", ".sh", ".txt"}
    }
    return {
        "modules": modules,
        "requirements": requirements,
        "interfaces": interfaces,
        "concepts": concepts,
        "profiles": profiles,
        "adapters": adapters,
        "governance_files": governance,
        "files": documents,
    }


def supersessions(root: Path) -> dict[str, dict[str, str]]:
    path = root / "governance/SUPERSESSION_LEDGER.json"
    if not path.is_file():
        return {}
    ledger = _load(path)
    out: dict[str, dict[str, str]] = {}
    for entry in ledger.get("entries", []):
        out[f"{entry['category']}::{entry['identifier']}"] = entry
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predecessor", type=Path, required=True, help="extracted predecessor release root")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    before = inventory(args.predecessor.resolve())
    after = inventory(ROOT)
    declared = supersessions(ROOT)

    categories: list[dict[str, Any]] = []
    undeclared: list[dict[str, str]] = []
    for category in before:
        lost = sorted(before[category] - after[category])
        gained = sorted(after[category] - before[category])
        unexplained = []
        for identifier in lost:
            key = f"{category}::{identifier}"
            if key not in declared:
                unexplained.append(identifier)
                undeclared.append({"category": category, "identifier": identifier})
        categories.append(
            {
                "category": category,
                "before": len(before[category]),
                "after": len(after[category]),
                "removed": lost,
                "added": gained,
                "removed_declared": [item for item in lost if f"{category}::{item}" in declared],
                "removed_undeclared": unexplained,
            }
        )

    report = {
        "schema_version": "1.0.0",
        "report": "ABSOLUTE_NO_LOSS_CHECK",
        "predecessor_root": str(args.predecessor.resolve()),
        "successor_root": str(ROOT),
        "status": "PASS" if not undeclared else "FAIL",
        "undeclared_removal_count": len(undeclared),
        "undeclared_removals": undeclared,
        "categories": categories,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    for item in categories:
        print(
            f"  {item['category']:<18} before={item['before']:<5} after={item['after']:<5} "
            f"removed={len(item['removed']):<4} undeclared={len(item['removed_undeclared'])}"
        )
    print(f"\n{report['status']}  undeclared removals: {len(undeclared)}")
    for item in undeclared[:40]:
        print(f"  {item['category']}: {item['identifier']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
