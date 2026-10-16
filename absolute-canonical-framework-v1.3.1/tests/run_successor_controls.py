#!/usr/bin/env python3
from __future__ import annotations
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_TOOLS = ROOT / "01_control_plane/manifests_releases/tools"
sys.path.insert(0, str(CANONICAL_TOOLS))
from release_integrity import verify_tree


def main() -> int:
    checks = []
    def record(name: str, passed: bool, detail):
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    try:
        tree = verify_tree(ROOT)
        record("release_tree_integrity", True, tree)
    except Exception as exc:
        record("release_tree_integrity", False, str(exc))

    pin = subprocess.run([sys.executable, str(ROOT / "tools/validate_ci_pins.py"), str(ROOT)], text=True, capture_output=True)
    record("ci_action_pins", pin.returncode == 0, {"stdout": pin.stdout, "stderr": pin.stderr, "returncode": pin.returncode})

    builder_text = (CANONICAL_TOOLS / "build_release.py").read_text(encoding="utf-8")
    required_tokens = ["--expected-candidate-sha256", "--authority-record", "--gate-binding", "overwrite denied", "source tree changed during build"]
    record("release_builder_controls", all(token in builder_text for token in required_tokens), required_tokens)

    result = {"status": "PASS" if all(item["pass"] for item in checks) else "FAIL", "checks": checks}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
