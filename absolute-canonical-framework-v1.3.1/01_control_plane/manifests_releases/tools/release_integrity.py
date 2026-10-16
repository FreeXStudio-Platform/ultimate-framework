#!/usr/bin/env python3
"""Shared deterministic integrity primitives for Absolute Framework RC2 releases."""
from __future__ import annotations

import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import argparse
import fnmatch
import hashlib
import json
import os
import re
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

RELEASE_VERSION = "1.3.1"
RELEASE_ID = "ABS.RELEASE.1.3.1"
CANDIDATE_ID = "ABS.CANDIDATE.1.3.1"
FRAMEWORK_ID = "ABS.FRAMEWORK.CANONICAL"

# The status a package may assert about itself. It stops short of "certified"
# on purpose: ABS.CFG.RELEASE.SELF_CERTIFICATION fixes self-certification to
# false, so the party that builds an artifact records internal verification and
# leaves certification to an external exact-hash review.
RELEASE_STATUS = "RELEASE_INTERNALLY_VERIFIED_INDEPENDENT_CERTIFICATION_PENDING"
ROOT_NAME = "absolute-canonical-framework-v1.3.1"

# Immutable predecessors, oldest first. Each entry is an input this release was
# derived from and must never be rewritten. Verification requires the recorded
# chain to match this constant exactly, so a tampered tree cannot quietly
# reattach itself to a different lineage.
BASELINE_CHAIN = (
    {
        "release_id": "ABS.RELEASE." + "1.0.0-RC1",
        "role": "IMMUTABLE_INPUT_BASELINE",
        "clean_zip_sha256": "0cbe85257f2ad8f2496b4f25de1b1dfbe7576c5031d9be2ec3f9635752672827",
        "build_evidence_zip_sha256": "bb563878423dedec4cae8580ff8f289a0fb35aa74936c35e77c019741af2ec11",
    },
    {
        "release_id": "ABS.RELEASE." + "1.0.0-RC2",
        "role": "IMMUTABLE_PREDECESSOR_RELEASE",
        "clean_zip_sha256": "3e403e5ea37c9f530cb69afbced5a841018a5e842d4610c3ab3dda21776fd7ba",
        "build_evidence_zip_sha256": "2c84aeeb3b7e29bdf39e0bee7924b033b395f8222e3cffd7623a425d400a4a1d",
        "candidate_tree_sha256": "2a766db38f08b68b9235ecbc1b76dc400363a6776b29995a4a82bff650226d50",
    },
    {
        "release_id": "ABS.RELEASE." + "1.0.0",
        "role": "IMMUTABLE_PREDECESSOR_RELEASE",
        "clean_zip_sha256": "cb82186f404c7d088cc4c4b6d3db5cc578adab829ec5014a519965d9431ca55b",
        "build_evidence_zip_sha256": "cb82186f404c7d088cc4c4b6d3db5cc578adab829ec5014a519965d9431ca55b",
        "candidate_tree_sha256": "d3f1f60622dca6014503debe0fd7cd8237bfe23ea14591c0eba12038c9666964",
    },
    {
        "release_id": "ABS.RELEASE." + "1.1.0",
        "role": "IMMUTABLE_PREDECESSOR_RELEASE",
        "clean_zip_sha256": "7568cf7db00f30bd23b35d2e82510f519e7908451764d07738f9b0438d595cdf",
        "build_evidence_zip_sha256": "7568cf7db00f30bd23b35d2e82510f519e7908451764d07738f9b0438d595cdf",
        "candidate_tree_sha256": "a1ff34736b3cac95fb5b35edb30ef482715e8ee2d376c8709e29387883759aba",
    },
    {
        "release_id": "ABS.RELEASE." + "1.2.0",
        "role": "IMMUTABLE_PREDECESSOR_RELEASE",
        "clean_zip_sha256": "cc2a4438fed352a911ee72842ca47e1cc44c054ee06536abb56a30f6ffe51338",
        "build_evidence_zip_sha256": "cc2a4438fed352a911ee72842ca47e1cc44c054ee06536abb56a30f6ffe51338",
        "candidate_tree_sha256": "add66854e3b89daa077e6a5dabd9c913385fe39f7a8b0f888e87c0a5e04ca866",
    },
    {
        "release_id": "ABS.RELEASE." + "1.3.0",
        "role": "IMMUTABLE_PREDECESSOR_RELEASE",
        "clean_zip_sha256": "37c71be4e6ab5b8c56c8e500894b24481f6289e4566a1b64bce4d125f7fc652f",
        "build_evidence_zip_sha256": "37c71be4e6ab5b8c56c8e500894b24481f6289e4566a1b64bce4d125f7fc652f",
        "candidate_tree_sha256": "1069d93309a3a2d8e15f4b001bb2f312d3b83098f5498b3519f3ab395468d998",
    },
)
BASELINE_RELEASE_ID = BASELINE_CHAIN[0]["release_id"]
BASELINE_CLEAN_SHA256 = BASELINE_CHAIN[0]["clean_zip_sha256"]
BASELINE_EVIDENCE_SHA256 = BASELINE_CHAIN[0]["build_evidence_zip_sha256"]
CANDIDATE_TREE_ALGORITHM = "sha256-canonical-path-size-content-v1"
INTEGRITY_MODEL = "non-circular-candidate-tree-plus-complete-detached-archive-binding-v1"
FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
MAX_MEMBER_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1000.0

# These files bind or enumerate the candidate hash and are excluded to avoid a
# circular digest. The clean ZIP SHA-256 and SHA256SUMS ledger bind them.
# Gate evidence records the result of verifying the payload. It cannot itself be
# payload: writing it would change the very hash it attests to, and no fixed
# point exists. It is release metadata, excluded from the candidate digest and
# covered instead by SHA256SUMS.txt, by gate_binding.json (which names each
# evidence file's SHA-256), and by the archive digest. This is what
# "non-circular candidate tree plus complete detached archive binding" means.
CANDIDATE_HASH_EXCLUSIONS = (
    "MANIFEST.json",
    "CANDIDATE_SOURCE_MANIFEST.json",
    "SHA256SUMS.txt",
    ".absolute/release/release_identity.json",
    ".absolute/release/authority_record.json",
    ".absolute/release/gate_binding.json",
    ".absolute/release/gate_evidence/*.json",
)
RELEASE_MANIFEST_EXCLUSIONS = (
    "MANIFEST.json",
    "SHA256SUMS.txt",
)

FORBIDDEN_PARTS = {
    ".git", ".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache",
    "node_modules", ".venv", "venv", "workbench", "session_state",
    "raw_chats", "raw_transcripts", "temporary_extraction", "cache",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".zip", ".tar", ".tgz", ".gz", ".7z"}
EXECUTABLE_PATHS = {
    "absolute",
    "tools/deep_verify.py",
    "tools/check_no_loss.py",
    "tools/prepare_release_metadata.py",
    "tools/restore_modes.py",
    "tools/verifier_mutation_check.py",
    "01_control_plane/manifests_releases/tools/build_release.py",
    "01_control_plane/manifests_releases/tools/release_integrity.py",
    "01_control_plane/manifests_releases/tools/verify_release.py",
    "04_enforcement/hooks/post_edit_validation.sh",
    "04_enforcement/hooks/pre_write_authority_check.py",
    "04_enforcement/validators/absolute_validate.py",
    "09_tests_evals/run_all.py",
    "tests/run_successor_controls.py",
    "tools/secure_release_builder.py",
    "tools/validate_ci_pins.py",
    "tools/verify_successor_release.py",
}


def expected_mode(relative_path: str) -> int:
    return 0o755 if relative_path in EXECUTABLE_PATHS else 0o644


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def is_excluded_from_candidate_hash(relative_path: str) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in CANDIDATE_HASH_EXCLUSIONS)


def normalized_member_name(name: str) -> str:
    if not name or "\x00" in name:
        raise ValueError("empty or NUL archive path")
    if "\\" in name:
        raise ValueError(f"backslash archive path: {name!r}")
    if re.match(r"^[A-Za-z]:", name):
        raise ValueError(f"drive-qualified archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or name.startswith("/"):
        raise ValueError(f"absolute archive path: {name!r}")
    parts = [part for part in path.parts if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise ValueError(f"traversal archive path: {name!r}")
    return "/".join(parts)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    folded: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden: {path.relative_to(root).as_posix()}")
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        posix = PurePosixPath(rel)
        if posix.is_absolute() or ".." in posix.parts:
            raise ValueError(f"unsafe path: {rel}")
        if any(part in FORBIDDEN_PARTS for part in posix.parts):
            if "__pycache__" in posix.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                raise ValueError(
                    f"bytecode cache in the release tree: {rel}. Something imported a module from "
                    "this tree without setting sys.dont_write_bytecode. Delete the __pycache__ "
                    "directories and rerun; use the provided entry points, which set it."
                )
            raise ValueError(f"denylisted path: {rel}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise ValueError(f"forbidden nested/archive/cache file: {rel}")
        folded_key = rel.casefold()
        if folded_key in folded and folded[folded_key] != rel:
            raise ValueError(f"case-colliding paths: {folded[folded_key]} / {rel}")
        folded[folded_key] = rel
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().casefold())


def candidate_tree_records(root: Path) -> tuple[str, list[dict[str, Any]]]:
    digest = hashlib.sha256()
    records: list[dict[str, Any]] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if is_excluded_from_candidate_hash(rel):
            continue
        file_hash = sha256_file(path)
        size = path.stat().st_size
        records.append({"path": rel, "bytes": size, "sha256": file_hash})
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), records


def parse_checksum_ledger(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
        if not match:
            raise ValueError(f"invalid checksum line {line_no}")
        digest, rel = match.groups()
        normalized = normalized_member_name(rel)
        if normalized != rel:
            raise ValueError(f"non-canonical checksum path: {rel}")
        if rel in values:
            raise ValueError(f"duplicate checksum path: {rel}")
        values[rel] = digest
    return values


def verify_gate_binding(gate_path: Path, candidate_hash: str) -> dict[str, Any]:
    gate_binding = json.loads(gate_path.read_text(encoding="utf-8"))
    if gate_binding.get("release_id") != RELEASE_ID:
        raise ValueError("gate binding release identity mismatch")
    if gate_binding.get("candidate_tree_sha256") != candidate_hash:
        raise ValueError("gate binding candidate identity mismatch")
    gates = gate_binding.get("gates", [])
    ids = [gate.get("gate_id") for gate in gates]
    required_ids = [f"C{i}" for i in range(20)]
    if ids != required_ids:
        raise ValueError(f"candidate build gate binding must contain C0-C19 exactly once in order; observed={ids}")
    passed: set[str] = set()
    for index, gate in enumerate(gates):
        gate_id = gate.get("gate_id")
        expected_prerequisites = [] if index == 0 else [f"C{index - 1}"]
        if gate.get("prerequisites") != expected_prerequisites:
            raise ValueError(f"gate prerequisite mismatch: {gate_id}")
        if any(item not in passed for item in expected_prerequisites):
            raise ValueError(f"unmet prerequisite: {gate_id}")
        if gate.get("status") != "PASS":
            raise ValueError(f"non-PASS candidate gate: {gate_id}")
        if gate.get("candidate_tree_sha256") != candidate_hash:
            raise ValueError(f"gate candidate hash mismatch: {gate_id}")
        if gate.get("bypass") is not False or gate.get("stale") is not False:
            raise ValueError(f"bypassed or stale candidate gate: {gate_id}")
        if gate.get("required_check_state") not in {"PASS", "NOT_APPLICABLE_WITH_EVIDENCE"}:
            raise ValueError(f"unacceptable required check state: {gate_id}")
        evidence_hash = gate.get("evidence_sha256")
        if not isinstance(evidence_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", evidence_hash):
            raise ValueError(f"missing evidence hash: {gate_id}")
        # The binding is only meaningful if the file it names still hashes to the
        # recorded value; otherwise a gate could cite evidence that has since
        # been rewritten.
        evidence_ref = gate.get("evidence_ref")
        if not evidence_ref:
            raise ValueError(f"missing evidence reference: {gate_id}")
        evidence_path = gate_path.resolve().parents[2] / evidence_ref
        if not evidence_path.is_file():
            raise ValueError(f"gate evidence file missing: {evidence_ref}")
        if sha256_file(evidence_path) != evidence_hash:
            raise ValueError(f"gate evidence digest mismatch: {evidence_ref}")
        passed.add(gate_id)
    if gate_binding.get("delivery_gate") != {"gate_id": "C20", "status": "EXTERNAL_HANDOFF_REQUIRED"}:
        raise ValueError("C20 delivery boundary missing")
    return gate_binding


def verify_tree(root: Path, expected_candidate_hash: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("release root missing")
    if root.name != ROOT_NAME:
        raise ValueError(f"release root must be {ROOT_NAME}")
    files = iter_files(root)
    actual = {path.relative_to(root).as_posix(): path for path in files}
    mode_mismatches = []
    for rel, path in actual.items():
        observed_mode = stat.S_IMODE(path.stat().st_mode)
        required_mode = expected_mode(rel)
        if observed_mode != required_mode:
            mode_mismatches.append({"path": rel, "observed": oct(observed_mode), "expected": oct(required_mode)})
    if mode_mismatches:
        raise ValueError(f"release file-mode mismatch: {mode_mismatches[:10]}")
    required_metadata = {item for item in CANDIDATE_HASH_EXCLUSIONS if "*" not in item}
    missing_metadata = sorted(required_metadata - set(actual))
    if missing_metadata:
        raise ValueError(f"missing integrity metadata: {missing_metadata}")

    manifest = json.loads(actual["MANIFEST.json"].read_text(encoding="utf-8"))
    candidate_manifest = json.loads(actual["CANDIDATE_SOURCE_MANIFEST.json"].read_text(encoding="utf-8"))
    identity = json.loads(actual[".absolute/release/release_identity.json"].read_text(encoding="utf-8"))
    authority = json.loads(actual[".absolute/release/authority_record.json"].read_text(encoding="utf-8"))

    for record_name, record in (("manifest", manifest), ("candidate manifest", candidate_manifest), ("identity", identity)):
        if record.get("framework_id") != FRAMEWORK_ID:
            raise ValueError(f"{record_name} framework identity mismatch")
        if record.get("release_id") != RELEASE_ID or record.get("version") != RELEASE_VERSION:
            raise ValueError(f"{record_name} release identity mismatch")
        if record.get("candidate_id") != CANDIDATE_ID:
            raise ValueError(f"{record_name} candidate identity mismatch")
        if record.get("status") != RELEASE_STATUS:
            raise ValueError(f"{record_name} release status mismatch")
    if identity.get("candidate_id") != CANDIDATE_ID:
        raise ValueError("candidate ID mismatch")
    if identity.get("package_root") != ROOT_NAME:
        raise ValueError("identity package-root mismatch")
    if tuple(identity.get("candidate_tree_exclusions", [])) != CANDIDATE_HASH_EXCLUSIONS:
        raise ValueError("identity hash-exclusion model mismatch")
    expected_baseline = [dict(item) for item in BASELINE_CHAIN]
    for record_name, record in (("manifest", manifest), ("candidate manifest", candidate_manifest), ("identity", identity)):
        if record.get("baseline_provenance") != expected_baseline:
            raise ValueError(f"{record_name} baseline provenance chain mismatch")
    expected_integrity_files = list(CANDIDATE_HASH_EXCLUSIONS)
    for record_name, record in (("manifest", manifest), ("candidate manifest", candidate_manifest)):
        if record.get("schema_version") != "1.3.1":
            raise ValueError(f"{record_name} schema version mismatch")
        if record.get("candidate_tree_hash_algorithm") != CANDIDATE_TREE_ALGORITHM:
            raise ValueError(f"{record_name} candidate-tree algorithm mismatch")
        if record.get("built_from_allowlist") is not True or record.get("evidence_archive_included") is not False:
            raise ValueError(f"{record_name} clean-package policy mismatch")
        if record.get("integrity_model") != INTEGRITY_MODEL:
            raise ValueError(f"{record_name} integrity model mismatch")
        if record.get("integrity_metadata_files") != expected_integrity_files:
            raise ValueError(f"{record_name} integrity metadata inventory mismatch")
    if manifest.get("inventory_scope") != "RELEASE_TREE_NON_SELF_REFERENTIAL":
        raise ValueError("release manifest inventory scope mismatch")
    if manifest.get("inventory_exclusions") != list(RELEASE_MANIFEST_EXCLUSIONS):
        raise ValueError("release manifest inventory exclusions mismatch")
    if candidate_manifest.get("inventory_scope") != "CANDIDATE_PAYLOAD":
        raise ValueError("candidate manifest inventory scope mismatch")
    if candidate_manifest.get("inventory_exclusions") != list(CANDIDATE_HASH_EXCLUSIONS):
        raise ValueError("candidate manifest inventory exclusions mismatch")
    expected_authority = {
        "framework_id": FRAMEWORK_ID,
        "release_id": RELEASE_ID,
        "candidate_id": CANDIDATE_ID,
        "version": RELEASE_VERSION,
        "status": RELEASE_STATUS,
        "authorized_action": "BUILD_CLEAN_SUCCESSOR_RELEASE",
        "authority_scope": "SUCCESSOR_CANDIDATE_ONLY",
        "source_tree_mutation": False,
        "self_certification": False,
        "allow_replace": False,
    }
    for key, value in expected_authority.items():
        if authority.get(key) != value:
            raise ValueError(f"authority field mismatch: {key}")

    candidate_hash, payload_records = candidate_tree_records(root)
    if expected_candidate_hash and candidate_hash != expected_candidate_hash:
        raise ValueError("observed candidate hash differs from expected")
    expected_hash_field = f"sha256:{candidate_hash}"
    if manifest.get("candidate_hash") != expected_hash_field or candidate_manifest.get("candidate_hash") != expected_hash_field:
        raise ValueError("manifest candidate hash mismatch")
    if identity.get("candidate_tree_sha256") != candidate_hash or authority.get("candidate_tree_sha256") != candidate_hash:
        raise ValueError("identity/authority candidate hash mismatch")
    if authority.get("release_id") != RELEASE_ID or authority.get("source_tree_mutation") is not False:
        raise ValueError("authority policy mismatch")

    payload_map = {item["path"]: (item["bytes"], item["sha256"]) for item in payload_records}
    candidate_listed = {item["path"]: (item["bytes"], item["sha256"]) for item in candidate_manifest.get("files", [])}
    if candidate_listed != payload_map:
        extra = sorted(set(candidate_listed) - set(payload_map))[:10]
        missing = sorted(set(payload_map) - set(candidate_listed))[:10]
        mismatch = sorted(path for path in set(candidate_listed) & set(payload_map) if candidate_listed[path] != payload_map[path])[:10]
        raise ValueError(f"CANDIDATE_SOURCE_MANIFEST.json payload inventory mismatch extra={extra} missing={missing} mismatch={mismatch}")
    if candidate_manifest.get("file_count") != len(payload_records):
        raise ValueError("CANDIDATE_SOURCE_MANIFEST.json file_count mismatch")
    if candidate_manifest.get("total_bytes") != sum(item["bytes"] for item in payload_records):
        raise ValueError("CANDIDATE_SOURCE_MANIFEST.json total_bytes mismatch")

    release_inventory_paths = sorted(set(actual) - set(RELEASE_MANIFEST_EXCLUSIONS), key=str.casefold)
    release_map = {
        rel: (actual[rel].stat().st_size, sha256_file(actual[rel]))
        for rel in release_inventory_paths
    }
    manifest_listed = {item["path"]: (item["bytes"], item["sha256"]) for item in manifest.get("files", [])}
    if manifest_listed != release_map:
        extra = sorted(set(manifest_listed) - set(release_map))[:10]
        missing = sorted(set(release_map) - set(manifest_listed))[:10]
        mismatch = sorted(path for path in set(manifest_listed) & set(release_map) if manifest_listed[path] != release_map[path])[:10]
        raise ValueError(f"MANIFEST.json release inventory mismatch extra={extra} missing={missing} mismatch={mismatch}")
    if manifest.get("file_count") != len(release_map):
        raise ValueError("MANIFEST.json file_count mismatch")
    if manifest.get("total_bytes") != sum(size for size, _ in release_map.values()):
        raise ValueError("MANIFEST.json total_bytes mismatch")
    for label, record in (("MANIFEST.json", manifest), ("CANDIDATE_SOURCE_MANIFEST.json", candidate_manifest)):
        if tuple(record.get("candidate_tree_exclusions", [])) != CANDIDATE_HASH_EXCLUSIONS:
            raise ValueError(f"{label} exclusion model mismatch")

    sums = parse_checksum_ledger(actual["SHA256SUMS.txt"])
    expected_sum_paths = set(actual) - {"SHA256SUMS.txt"}
    if set(sums) != expected_sum_paths:
        raise ValueError(
            "checksum inventory mismatch "
            f"extra={sorted(set(sums)-expected_sum_paths)[:10]} "
            f"missing={sorted(expected_sum_paths-set(sums))[:10]}"
        )
    if "SHA256SUMS.txt" in sums:
        raise ValueError("checksum ledger must not self-reference")
    for rel, expected in sums.items():
        observed = sha256_file(actual[rel])
        if observed != expected:
            raise ValueError(f"checksum mismatch: {rel}")

    verify_gate_binding(actual[".absolute/release/gate_binding.json"], candidate_hash)

    # Stale successor identity is forbidden except in explicitly labeled baseline history.
    # Build historical tokens without embedding them contiguously in this scanner.
    # This keeps the scanner itself from becoming a false stale-identity hit.
    historical_release_id = "ABS.RELEASE." + "1.0.0-RC1"
    historical_version = "1.0.0-" + "rc.1"
    historical_candidate_hash = "sha256:" + (
        "a2b9256736f6ab46938fc1c8acc537a2" +
        "d77192788d03048ac45d4be6d5d57e9d"
    )
    pre_remediation_tree_hash = (
        "267f66f05fddfddc19750fd6734175d8" +
        "7c58376bc158b5efa85e3330df15dd31"
    )
    stale_successor_alias = "ABSOLUTE_CANONICAL_FRAMEWORK_" + "RC2_SUCCESSOR_CANDIDATE"
    exact_stale = {
        historical_release_id,
        historical_candidate_hash,
        pre_remediation_tree_hash,
        stale_successor_alias,
    }
    allowed_baseline_files = {
        "CHANGELOG.md",
        "MIGRATION_AND_SUPERSESSION_NOTES.md",
        "04_enforcement/schemas/release_manifest.schema.json",
        "docs/registries/FRAMEWORK.json",
        # The engine-derived release model mirrors FRAMEWORK.json's baseline chain, every entry
        # carrying its role label; it is provenance, not a successor claim.
        "docs/ultimate-engine/machine/release-model.json",
        "governance/coverage_closure_v3/normalized_concept_candidate_reconciliation.json",
        "governance/coverage_closure_v3/normalized_requirement_provenance.json",
        "governance/coverage_closure_v3/release_identity_migration.json",
        "governance/coverage_closure_v3/requirement_level_trace_repair_adr.json",
        "governance/coverage_closure_v3/successor_requirement_extensions.json",
        "MANIFEST.json",
        "CANDIDATE_SOURCE_MANIFEST.json",
        ".absolute/release/release_identity.json",
    }
    stale_hits: list[dict[str, str]] = []
    for rel, path in actual.items():
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".py", ".sh", ".dot", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in exact_stale:
            if token in text and rel not in allowed_baseline_files:
                stale_hits.append({"path": rel, "token": token})
        if historical_version in text and rel not in allowed_baseline_files:
            stale_hits.append({"path": rel, "token": historical_version})
    if stale_hits:
        raise ValueError(f"stale successor identity outside labeled baseline history: {stale_hits[:10]}")
    for rel in sorted(allowed_baseline_files & set(actual)):
        text = actual[rel].read_text(encoding="utf-8")
        lowered = text.lower()
        if "historical" not in lowered and "baseline" not in lowered and "immutable_input_baseline" not in lowered:
            raise ValueError(f"allowed RC1 reference lacks baseline/historical labeling: {rel}")

    return {
        "status": "PASS",
        "release_id": RELEASE_ID,
        "version": RELEASE_VERSION,
        "candidate_id": CANDIDATE_ID,
        "candidate_tree_sha256": candidate_hash,
        "payload_file_count": len(payload_records),
        "archive_member_file_count": len(actual),
        "checksum_member_count": len(sums),
        "checksum_self_reference": False,
        "single_root": True,
        "stale_successor_identity_hits": 0,
    }


def inspect_zip(path: Path) -> dict[str, Any]:
    seen: set[str] = set()
    folded: dict[str, str] = {}
    total = 0
    roots: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        bad_crc = archive.testzip()
        if bad_crc:
            raise ValueError(f"CRC failure: {bad_crc}")
        for info in archive.infolist():
            name = normalized_member_name(info.filename)
            if name in seen:
                raise ValueError(f"duplicate archive member: {name}")
            seen.add(name)
            folded_key = name.casefold()
            if folded_key in folded and folded[folded_key] != name:
                raise ValueError(f"case-colliding archive members: {folded[folded_key]} / {name}")
            folded[folded_key] = name
            roots.add(name.split("/", 1)[0])
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink archive member: {name}")
            if not info.is_dir() and not name.endswith("/"):
                relative = name.split("/", 1)[1] if "/" in name else ""
                observed_permissions = stat.S_IMODE(mode)
                required_permissions = expected_mode(relative)
                if observed_permissions != required_permissions:
                    raise ValueError(
                        f"archive file-mode mismatch: {name} observed={oct(observed_permissions)} expected={oct(required_permissions)}"
                    )
            total += info.file_size
            if info.file_size > MAX_MEMBER_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError("archive decompressed-size limit exceeded")
            ratio = info.file_size / max(info.compress_size, 1) if info.file_size else 0.0
            if ratio > MAX_COMPRESSION_RATIO:
                raise ValueError(f"compression-ratio limit exceeded: {name}")
        if roots != {ROOT_NAME}:
            raise ValueError(f"archive must contain exactly root {ROOT_NAME}; observed={sorted(roots)}")
    return {
        "member_count": len(seen),
        "total_uncompressed_bytes": total,
        "crc": "PASS",
        "path_safety": "PASS",
        "duplicate_and_case_collision_check": "PASS",
        "symlink_check": "PASS",
        "compression_ratio_check": "PASS",
        "single_root": ROOT_NAME,
    }


def safe_extract_zip(path: Path, destination: Path) -> Path:
    inspection = inspect_zip(path)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = normalized_member_name(info.filename)
            out = destination.joinpath(*PurePosixPath(name).parts)
            if info.is_dir() or name.endswith("/"):
                out.mkdir(parents=True, exist_ok=True)
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, out.open("wb") as target:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
            relative = name.split("/", 1)[1] if "/" in name else ""
            os.chmod(out, expected_mode(relative))
    return destination / inspection["single_root"]


def verify_zip(path: Path, expected_candidate_hash: str | None = None) -> dict[str, Any]:
    inspection = inspect_zip(path)
    with tempfile.TemporaryDirectory(prefix="absolute-rc2-verify-") as temp_dir:
        root = safe_extract_zip(path, Path(temp_dir))
        tree_result = verify_tree(root, expected_candidate_hash=expected_candidate_hash)
    return {
        **tree_result,
        "zip_sha256": sha256_file(path),
        "zip_bytes": path.stat().st_size,
        "archive": inspection,
        "post_extraction_hash_equality": "PASS",
    }



def main() -> int:
    parser = argparse.ArgumentParser(description="Absolute Framework RC2 integrity utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    candidate = subparsers.add_parser("candidate-hash", help="Compute the non-circular candidate source-tree hash")
    candidate.add_argument("root", type=Path)

    tree = subparsers.add_parser("verify-tree", help="Verify an extracted RC2 release tree")
    tree.add_argument("root", type=Path)
    tree.add_argument("--expected-candidate-sha256")

    archive = subparsers.add_parser("verify-zip", help="Verify a clean RC2 release ZIP")
    archive.add_argument("zip", type=Path)
    archive.add_argument("--expected-candidate-sha256")

    args = parser.parse_args()
    if args.command == "candidate-hash":
        digest, records = candidate_tree_records(args.root.resolve())
        result = {
            "status": "PASS",
            "candidate_tree_sha256": digest,
            "candidate_tree_hash_algorithm": CANDIDATE_TREE_ALGORITHM,
            "payload_file_count": len(records),
            "exclusions": list(CANDIDATE_HASH_EXCLUSIONS),
        }
    elif args.command == "verify-tree":
        result = verify_tree(args.root.resolve(), args.expected_candidate_sha256)
    else:
        result = verify_zip(args.zip.resolve(), args.expected_candidate_sha256)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
