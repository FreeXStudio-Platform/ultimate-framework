#!/usr/bin/env python3
"""Verify an Absolute Framework RC2 clean ZIP or extracted release tree."""
from __future__ import annotations
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from release_integrity import verify_tree, verify_zip

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--expected-candidate-sha256")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    target = args.target.resolve()
    result = verify_zip(target, args.expected_candidate_sha256) if target.is_file() else verify_tree(target, args.expected_candidate_sha256)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
