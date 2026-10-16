#!/usr/bin/env python3
from __future__ import annotations
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--report")
args = parser.parse_args()
report = Path(args.report).resolve() if args.report else Path(tempfile.gettempdir()) / "absolute-framework-test-run-report.json"
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
validator = subprocess.run([sys.executable, str(root / "04_enforcement/validators/absolute_validate.py"), str(root), "--report", str(report)], text=True, capture_output=True, env=env)
controls = subprocess.run([sys.executable, str(root / "tests/run_successor_controls.py")], text=True, capture_output=True, env=env)
# READ_ORDER names this file as the test entry point. It must not be weaker
# than the verification the README tells a reader to trust, or following the
# documented path yields a green result the real pass would have refused.
deep = subprocess.run([sys.executable, str(root / "tools/deep_verify.py")], text=True, capture_output=True, env=env)
# And the verifier itself must be shown to still be checking: a section that
# silently stopped running reports PASS exactly like a clean tree.
mutation = subprocess.run([sys.executable, str(root / "tools/verifier_mutation_check.py")], text=True, capture_output=True, env=env)
# V2 machine-contract records (configuration/executable-surface/conversation-decision
# projections) must be checked on every run, or a merged validator nobody invokes is a
# false-green path exactly like the mutation-check gap above.
v2_contracts = subprocess.run([sys.executable, str(root / "tools/validate_v2_contracts.py")], text=True, capture_output=True, env=env)
stale = json.loads((root / "09_tests_evals/fixtures/stale_hash_review.json").read_text())
unsafe = json.loads((root / "09_tests_evals/fixtures/unsafe_archive_paths.json").read_text())
extra = {
  "stale_hash_rejected": stale["reviewed_hash"] != stale["active_hash"],
  "unsafe_path_fixture_detected": any(item.startswith("/") or ".." in item.split("/") for item in unsafe["members"]),
  "validator_exit_code": validator.returncode,
  "successor_controls_exit_code": controls.returncode,
  "deep_verify_exit_code": deep.returncode,
  "verifier_mutation_check_exit_code": mutation.returncode,
  "v2_contracts_exit_code": v2_contracts.returncode,
}
passed = (
  validator.returncode == 0
  and controls.returncode == 0
  and deep.returncode == 0
  and mutation.returncode == 0
  and v2_contracts.returncode == 0
  and extra["stale_hash_rejected"]
  and extra["unsafe_path_fixture_detected"]
)
result = {
  "status": "PASS" if passed else "FAIL",
  "deterministic_validator": str(report),
  "additional_controls": extra,
  "validator_stdout": validator.stdout,
  "validator_stderr": validator.stderr,
  "successor_controls_stdout": controls.stdout,
  "successor_controls_stderr": controls.stderr,
  "deep_verify_stdout": deep.stdout,
  "deep_verify_stderr": deep.stderr,
  "verifier_mutation_check_stdout": mutation.stdout,
  "verifier_mutation_check_stderr": mutation.stderr,
  "v2_contracts_stdout": v2_contracts.stdout,
  "v2_contracts_stderr": v2_contracts.stderr,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if passed else 1)
