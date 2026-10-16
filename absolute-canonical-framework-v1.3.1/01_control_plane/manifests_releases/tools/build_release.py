#!/usr/bin/env python3
"""Gate-bound, deterministic, non-mutating Absolute Framework RC2 release builder."""
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
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from release_integrity import (
    FIXED_ZIP_DT,
    ROOT_NAME,
    candidate_tree_records,
    expected_mode,
    iter_files,
    sha256_file,
    verify_gate_binding,
    verify_tree,
    verify_zip,
)

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact RC2 successor clean ZIP")
    parser.add_argument("source", type=Path)
    parser.add_argument("output_zip", type=Path)
    parser.add_argument("--expected-candidate-sha256", required=True)
    parser.add_argument("--authority-record", type=Path, required=True)
    parser.add_argument("--gate-binding", type=Path, required=True)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--rollback-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    root = args.source.resolve()
    output = args.output_zip.resolve()
    if root.name != ROOT_NAME:
        raise SystemExit(f"source root must be named {ROOT_NAME}")
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise SystemExit("output must be outside the source tree")

    before = {p.relative_to(root).as_posix(): (p.stat().st_size, sha256_file(p)) for p in iter_files(root)}
    tree_result = verify_tree(root, expected_candidate_hash=args.expected_candidate_sha256)
    authority = load_json(args.authority_record.resolve())
    gate_binding = verify_gate_binding(args.gate_binding.resolve(), args.expected_candidate_sha256)
    required_authority = {
        "release_id": tree_result["release_id"],
        "candidate_tree_sha256": args.expected_candidate_sha256,
        "authorized_action": "BUILD_CLEAN_SUCCESSOR_RELEASE",
        "authority_scope": "SUCCESSOR_CANDIDATE_ONLY",
        "source_tree_mutation": False,
        "self_certification": False,
    }
    for key, expected in required_authority.items():
        if authority.get(key) != expected:
            raise SystemExit(f"authority mismatch: {key}")

    validator = root / "04_enforcement/validators/absolute_validate.py"
    validation = subprocess.run(
        [sys.executable, str(validator), str(root)],
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if validation.returncode:
        sys.stderr.write(validation.stdout + validation.stderr)
        raise SystemExit("framework validator failed")

    result = {
        "mode": "DRY_RUN",
        "release_id": tree_result["release_id"],
        "candidate_tree_sha256": args.expected_candidate_sha256,
        "payload_file_count": tree_result["payload_file_count"],
        "gate_count": len(gate_binding["gates"]),
        "source_tree_mutation": False,
    }
    if not args.commit:
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        if not args.replace:
            raise SystemExit("overwrite denied")
        if authority.get("allow_replace") is not True:
            raise SystemExit("replacement not authorized")
        if not args.rollback_dir:
            raise SystemExit("rollback directory required for replacement")
        rollback_dir = args.rollback_dir.resolve()
        rollback_dir.mkdir(parents=True, exist_ok=True)
        rollback = rollback_dir / f"{output.name}.{sha256_file(output)}.rollback"
        shutil.copy2(output, rollback)
        if sha256_file(rollback) != sha256_file(output):
            raise SystemExit("rollback snapshot verification failed")

    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    files = iter_files(root)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{ROOT_NAME}/{rel}", FIXED_ZIP_DT)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            permissions = expected_mode(rel)
            info.external_attr = (permissions & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    verify_zip(temporary, expected_candidate_hash=args.expected_candidate_sha256)
    temporary.replace(output)

    after = {p.relative_to(root).as_posix(): (p.stat().st_size, sha256_file(p)) for p in iter_files(root)}
    if after != before:
        raise SystemExit("source tree changed during build")

    result.update({
        "mode": "COMMIT",
        "output": str(output),
        "output_sha256": sha256_file(output),
        "output_bytes": output.stat().st_size,
        "archive_member_file_count": len(files),
        "verification": verify_zip(output, expected_candidate_hash=args.expected_candidate_sha256),
    })
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{result['output_sha256']}  {output.name}\n", encoding="utf-8"
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
