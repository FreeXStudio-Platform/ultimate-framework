#!/usr/bin/env python3
"""Standalone whole-system deep verifier.

Runs every section in one pass and exits non-zero on any finding. Intended for
CI and for the ``S12.VERIFIED`` rail step.

    python3 tools/deep_verify.py [--project <dir>] [--report <out.json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.project import Project  # noqa: E402
from runtime.verify import deep_verify  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, help="also verify the project installed at this path")
    parser.add_argument("--report", type=Path, help="write the JSON report here")
    parser.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = parser.parse_args()

    project = Project.discover(args.project) if args.project else None
    report = deep_verify(project)

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")

    if args.quiet:
        print(
            f"{report['status']}  sections={report['sections_passed']}/{report['section_count']}  "
            f"checks={report['checks_run']}  findings={report['finding_count']}"
        )
    else:
        print(f"Absolute deep verification — {report['scope']}")
        for section in report["sections"]:
            print(f"  {section['status']:<5} {section['section']:<26} checks={section['checks']:<5} findings={section['finding_count']}")
        print(
            f"\n{report['status']}  sections={report['sections_passed']}/{report['section_count']}  "
            f"checks={report['checks_run']}  findings={report['finding_count']}  "
            f"severity={report['severity_counts']}"
        )
        for finding in report["findings"][:60]:
            print(f"  {finding['severity']:<8} {finding['section']:<24} {finding['code']:<34} {finding.get('path','')}: {finding['message']}")
        if report["finding_count"] > 60:
            print(f"  … {report['finding_count'] - 60} more")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
