#!/usr/bin/env python3
"""Generate the exact release allowlist for the current candidate from the immutable RC2 tree.

The allowlist is path-authoritative.  It intentionally does not embed current
file hashes, which keeps the allowlist non-self-referential.  Exact current
hashes remain the responsibility of MANIFEST.json, CANDIDATE_SOURCE_MANIFEST.json,
and SHA256SUMS.txt.  Source identity is derived from the immutable RC2 member
hash when a predecessor path exists; RC2 is the allowlist's anchored baseline
because the mechanism was born on the RC3 line, which forked from RC2.

History: the RC3 version of this tool verified the RC2 baseline against
``BASELINE_CHAIN[0]``, which on the RC3 line *was* RC2.  After the 1.2.0 merge
that entry became RC1, so the tool refused every baseline it was handed and the
shipped allowlist was RC3's own record set carried forward unchanged.  The
anchored baseline is now looked up by release id, the derivative labels are
release-neutral, and ``runtime/verify.py`` asserts the record set against the
tree so a stale allowlist is a finding rather than a file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_integrity import (
    BASELINE_CHAIN,
    CANDIDATE_ID,
    FRAMEWORK_ID,
    RELEASE_ID,
    ROOT_NAME,
    canonical_json_bytes,
    iter_files,
    parse_checksum_ledger,
    sha256_file,
)

# The allowlist's anchored baseline is RC2, looked up by identity rather than by
# position in the chain (see the module docstring for why position was wrong).
ALLOWLIST_BASELINE_RELEASE_ID = "ABS.RELEASE.1.0.0-RC2"
ALLOWLIST_BASELINE = next(
    entry for entry in BASELINE_CHAIN if entry["release_id"] == ALLOWLIST_BASELINE_RELEASE_ID
)
BASELINE_RELEASE_ID = ALLOWLIST_BASELINE["release_id"]
BASELINE_CLEAN_SHA256 = ALLOWLIST_BASELINE["clean_zip_sha256"]
BASELINE_EVIDENCE_SHA256 = ALLOWLIST_BASELINE["build_evidence_zip_sha256"]
STATUS_PRESERVED = "PRESERVED_EXACT_FROM_BASELINE"
STATUS_MODIFIED = "MODIFIED_SINCE_BASELINE"
STATUS_NEW = "NEW_SINCE_BASELINE"
STATUS_GENERATED = "GENERATED_BUILD_CONTROL"

ALLOWLIST_NAME = "RELEASE_ALLOWLIST.json"
POLICY = "EXACT_RECORD_SET_FAIL_CLOSED"
GENERATOR_PATH = "01_control_plane/manifests_releases/tools/generate_release_allowlist.py"
GENERATED_BUILD_CONTROLS = {
    "MANIFEST.json",
    "CANDIDATE_SOURCE_MANIFEST.json",
    "SHA256SUMS.txt",
    ALLOWLIST_NAME,
    ".absolute/release/release_identity.json",
    ".absolute/release/authority_record.json",
    ".absolute/release/gate_binding.json",
}


def verify_immutable_baseline(baseline_root: Path) -> dict[str, object]:
    """Verify the extracted RC2 baseline against its detached checksum ledger and chain identity."""
    if baseline_root.name != "absolute-canonical-framework-v1.0.0-rc.2":
        raise ValueError("baseline root must be the immutable RC2 package root")
    identity_path = baseline_root / ".absolute/release/release_identity.json"
    ledger_path = baseline_root / "SHA256SUMS.txt"
    if not identity_path.is_file() or not ledger_path.is_file():
        raise ValueError("RC2 identity or checksum ledger is missing")
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    if identity.get("release_id") != BASELINE_RELEASE_ID:
        raise ValueError("baseline release identity mismatch")
    actual = {
        item.relative_to(baseline_root).as_posix(): item
        for item in iter_files(baseline_root)
    }
    sums = parse_checksum_ledger(ledger_path)
    expected_paths = set(actual) - {"SHA256SUMS.txt"}
    if set(sums) != expected_paths:
        raise ValueError("immutable RC2 checksum inventory mismatch")
    for relative_path, expected_hash in sums.items():
        if sha256_file(actual[relative_path]) != expected_hash:
            raise ValueError(f"immutable RC2 checksum mismatch: {relative_path}")
    return {
        "package_root": baseline_root.name,
        "release_id": BASELINE_RELEASE_ID,
        "checksum_ledger_verified": True,
        "verified_member_count": len(actual),
    }


def artifact_class(relative_path: str) -> str:
    path = Path(relative_path)
    name = path.name
    suffix = path.suffix.lower()
    parts = path.parts

    if relative_path in GENERATED_BUILD_CONTROLS:
        return "RELEASE_INTEGRITY_METADATA"
    if name == "LICENSE.md":
        return "LICENSE"
    if name.endswith(".schema.json"):
        return "MACHINE_SCHEMA"
    if "tests" in parts or (parts and parts[0] == "09_tests_evals"):
        return "TEST_ASSET"
    if name == "MODULE_MANIFEST.yaml":
        return "MODULE_MANIFEST"
    if "blueprint" in parts and suffix in {".dot", ".mmd"}:
        return "BLUEPRINT_SOURCE"
    if suffix == ".svg":
        return "VISUAL_DERIVATIVE"
    if suffix in {".py", ".sh"} and any(
        part in {"tools", "hooks", "validators"} for part in parts
    ):
        return "EXECUTABLE_TOOL"
    if parts and parts[0] == "governance":
        return "GOVERNANCE_RECORD"
    if "registries" in parts or "registry" in name.lower() or name.endswith("_INDEX.json"):
        return "REGISTRY"
    if "examples" in parts or (parts and parts[0] == "08_examples"):
        return "EXAMPLE"
    if suffix in {".yaml", ".yml", ".toml"}:
        return "CONFIGURATION"
    if suffix == ".md":
        return "NORMATIVE_DOCUMENTATION"
    return "OTHER_CANONICAL_PAYLOAD"


def build_record(relative_path: str, current: Path | None, baseline: Path | None) -> dict[str, str]:
    if relative_path in GENERATED_BUILD_CONTROLS:
        derivative_status = STATUS_GENERATED
        source_identity = f"{RELEASE_ID}:GENERATED_BUILD_CONTROL:{relative_path}"
    elif baseline is None:
        derivative_status = STATUS_NEW
        source_identity = f"{RELEASE_ID}:CANONICAL_NEW:{relative_path}"
    else:
        baseline_hash = sha256_file(baseline)
        source_identity = f"{BASELINE_RELEASE_ID}:{relative_path}@sha256:{baseline_hash}"
        derivative_status = (
            STATUS_PRESERVED
            if current is not None and sha256_file(current) == baseline_hash
            else STATUS_MODIFIED
        )
    return {
        "path": relative_path,
        "artifact_class": artifact_class(relative_path),
        "source_identity": source_identity,
        "derivative_status": derivative_status,
    }


def generate(candidate_root: Path, baseline_root: Path) -> dict:
    candidate_root = candidate_root.resolve()
    baseline_root = baseline_root.resolve()
    if candidate_root.name != ROOT_NAME:
        raise ValueError(f"candidate root must be named {ROOT_NAME}")
    if not baseline_root.is_dir():
        raise ValueError("immutable RC2 baseline root is missing")
    baseline_verification = verify_immutable_baseline(baseline_root)

    current_paths = {
        item.relative_to(candidate_root).as_posix(): item
        for item in iter_files(candidate_root)
        if item.relative_to(candidate_root).as_posix() != ALLOWLIST_NAME
    }
    baseline_paths = {
        item.relative_to(baseline_root).as_posix(): item
        for item in iter_files(baseline_root)
    }
    expected_paths = set(current_paths) | {ALLOWLIST_NAME}
    records = [
        build_record(relative, current_paths.get(relative), baseline_paths.get(relative))
        for relative in sorted(expected_paths, key=str.casefold)
    ]
    counts: dict[str, int] = {}
    for record in records:
        key = record["derivative_status"]
        counts[key] = counts.get(key, 0) + 1
    return {
        "schema_version": "1.0.0",
        "framework_id": FRAMEWORK_ID,
        "release_id": RELEASE_ID,
        "candidate_id": CANDIDATE_ID,
        "policy": POLICY,
        "generator": GENERATOR_PATH,
        "classification_policy_version": "1.0.0",
        "baseline_provenance": {
            "release_id": BASELINE_RELEASE_ID,
            "role": "IMMUTABLE_INPUT_BASELINE",
            "clean_zip_sha256": BASELINE_CLEAN_SHA256,
            "build_evidence_zip_sha256": BASELINE_EVIDENCE_SHA256,
        },
        "baseline_verification": baseline_verification,
        "record_count": len(records),
        "derivative_status_counts": dict(sorted(counts.items())),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_root", type=Path)
    parser.add_argument("baseline_root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    candidate_root = args.candidate_root.resolve()
    output = (args.output or candidate_root / ALLOWLIST_NAME).resolve()
    if output != candidate_root / ALLOWLIST_NAME:
        raise SystemExit(f"output must be the candidate-local {ALLOWLIST_NAME}")
    payload = canonical_json_bytes(generate(candidate_root, args.baseline_root))
    if args.check:
        if not output.is_file() or output.read_bytes() != payload:
            print(json.dumps({"status": "FAIL", "reason": "allowlist drift", "output": str(output)}))
            return 2
        print(json.dumps({"status": "PASS", "output": str(output)}))
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    print(json.dumps({"status": "PASS", "output": str(output), "sha256": sha256_file(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
