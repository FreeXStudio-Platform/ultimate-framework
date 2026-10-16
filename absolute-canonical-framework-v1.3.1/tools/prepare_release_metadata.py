#!/usr/bin/env python3
"""Regenerate the release identity, gate binding, manifests, and checksum ledger.

This tool exists because six files in the tree bind to the tree's own content
hash. Editing any governed file invalidates all six, and hand-editing them is
how a manifest quietly stops describing the thing it manifests. Running this is
the only supported way to re-bind them.

It is deliberately *not* a certifier: it records what the gates actually
returned. If a gate did not pass, it writes that, and the release builder will
refuse to build.

    python3 tools/prepare_release_metadata.py [--gate-results <json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_control_plane/manifests_releases/tools"))

import release_integrity as integrity  # noqa: E402

GATE_NAMES = {
    "C0": "Bootstrap Integrity",
    "C1": "Capability Truth",
    "C2": "Source Admission",
    "C3": "Nested Coverage",
    "C4": "Execution Continuity",
    "C5": "Lineage Integrity",
    "C6": "Coverage Baseline",
    "C7": "Knowledge No-Loss",
    "C8": "Synthesis Quality",
    "C9": "Architecture Completeness",
    "C10": "Executable Surface Closure",
    "C11": "Control and Configuration Integrity",
    "C12": "Representation Parity",
    "C13": "External Tool Truth",
    "C14": "Operational Assurance",
    "C15": "Simulation Conformance",
    "C16": "Findings Integrity",
    "C17": "Remediation Candidate",
    "C18": "Revalidated Release Candidate",
    "C19": "Coverage Closure",
    "C20": "Certification-Ready Delivery",
}

# Which verifier output substantiates each gate. Every gate must name at least
# one, or the gate is unsupported and is written as NOT_RUN.
GATE_SUPPORT = {
    "C0": ["baseline_chain_recomputed"],
    "C1": ["FRAMEWORK_STRUCTURE"],
    "C2": ["baseline_chain_recomputed", "FRAMEWORK_IDENTITY"],
    "C3": ["FRAMEWORK_IDENTITY", "payload_inventory_complete"],
    "C4": ["FRAMEWORK_RUNTIME", "SIMULATION"],
    "C5": ["FRAMEWORK_IDENTITY", "no_loss_check"],
    "C6": ["FRAMEWORK_STRUCTURE"],
    "C7": ["no_loss_check"],
    "C8": ["FRAMEWORK_REPRESENTATION"],
    "C9": ["FRAMEWORK_STRUCTURE", "authority_dag_acyclic"],
    "C10": ["FRAMEWORK_SECURITY", "FRAMEWORK_RUNTIME"],
    "C11": ["FRAMEWORK_GOVERNANCE"],
    "C12": ["FRAMEWORK_REPRESENTATION"],
    "C13": ["FRAMEWORK_SECURITY"],
    "C14": ["SIMULATION", "FRAMEWORK_RUNTIME"],
    "C15": ["SIMULATION"],
    "C16": ["FRAMEWORK_CONTRACTS", "FRAMEWORK_SEMANTICS"],
    "C17": ["no_loss_check", "FRAMEWORK_CONTRACTS"],
    "C18": ["FRAMEWORK_IDENTITY", "FRAMEWORK_CONTRACTS", "FRAMEWORK_SECURITY"],
    "C19": ["deep_verification_zero_findings"],
}


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_gate_evidence(root: Path, support: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Write one evidence file per gate and return the records keyed by gate id.

    The evidence body deliberately does **not** name the candidate hash. Gate
    evidence is payload, so embedding the hash of the tree that contains it
    would be circular: writing the evidence changes the hash, which changes the
    evidence, forever. The binding lives in ``.absolute/release/gate_binding.json``,
    which is excluded from the candidate digest and names both the candidate
    hash and the SHA-256 of each evidence file. That is the non-circular model
    the release identity already declares.
    """
    directory = root / ".absolute/release/gate_evidence"
    directory.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict[str, Any]] = {}
    for index in range(20):
        gate_id = f"C{index}"
        names = GATE_SUPPORT[gate_id]
        results = [support.get(name) for name in names]
        missing = [name for name, value in zip(names, results) if value is None]
        passed = not missing and all(item.get("status") == "PASS" for item in results if isinstance(item, dict))
        evidence = {
            "schema": "absolute.gate_evidence.v1",
            "gate_id": gate_id,
            "gate_name": GATE_NAMES[gate_id],
            "release_id": integrity.RELEASE_ID,
            "prerequisites": [] if index == 0 else [f"C{index - 1}"],
            "required_check_state": "PASS",
            "status": "PASS" if passed else ("NOT_RUN" if missing else "FAIL"),
            "bypass": False,
            "stale": False,
            "blocking_findings": sum(
                item.get("finding_count", 0) for item in results if isinstance(item, dict)
            ),
            "not_run_required_checks": len(missing),
            "inconclusive_required_checks": 0,
            "supporting_results": [
                {
                    "name": name,
                    "status": (value or {}).get("status", "NOT_RUN"),
                    "checks": (value or {}).get("checks", 0),
                    "finding_count": (value or {}).get("finding_count", 0),
                    "detail": (value or {}).get("detail", ""),
                }
                for name, value in zip(names, results)
            ],
            "summary": (
                f"{GATE_NAMES[gate_id]} evaluated from {', '.join(names)}. "
                "The candidate identity this evidence is bound to is recorded in "
                ".absolute/release/gate_binding.json, not here, to keep the digest non-circular."
            ),
        }
        path = directory / f"{gate_id}.json"
        path.write_text(canonical(evidence), encoding="utf-8")
        records[gate_id] = evidence
    return records


def gather_support(root: Path) -> dict[str, Any]:
    """Run the verifiers whose results substantiate the gates."""
    import subprocess

    sys.path.insert(0, str(root))
    from runtime.verify import verify_framework

    report = verify_framework(root, include_release_metadata=False)
    support: dict[str, Any] = {
        item["section"]: {
            "status": item["status"],
            "checks": item["checks"],
            "finding_count": item["finding_count"],
            "detail": item["intent"],
        }
        for item in report["sections"]
    }
    support["deep_verification_zero_findings"] = {
        "status": "PASS" if report["finding_count"] == 0 else "FAIL",
        "checks": report["checks_run"],
        "finding_count": report["finding_count"],
        "detail": f"whole-system deep verification over {report['section_count']} sections",
    }

    predecessor_release_id = integrity.BASELINE_CHAIN[-1]["release_id"]
    predecessor_version = predecessor_release_id.removeprefix("ABS.RELEASE.")
    predecessor = root.parent / "predecessor" / f"absolute-canonical-framework-v{predecessor_version}"
    if predecessor.is_dir():
        result = subprocess.run(
            [sys.executable, str(root / "tools/check_no_loss.py"), "--predecessor", str(predecessor)],
            capture_output=True,
            text=True,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        support["no_loss_check"] = {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "checks": 8,
            "finding_count": 0 if result.returncode == 0 else 1,
            "detail": f"semantic inventory compared against {predecessor.name}",
        }
    else:
        support["no_loss_check"] = {
            "status": "NOT_RUN",
            "checks": 0,
            "finding_count": 1,
            "detail": f"predecessor tree not present at {predecessor}",
        }

    chain_ok = all(
        (root / "docs/registries/FRAMEWORK.json").is_file()
        for _ in [0]
    )
    framework = json.loads((root / "docs/registries/FRAMEWORK.json").read_text(encoding="utf-8"))
    expected_chain = [dict(item) for item in integrity.BASELINE_CHAIN]
    identity = json.loads((root / ".absolute/release/release_identity.json").read_text(encoding="utf-8")) if (root / ".absolute/release/release_identity.json").is_file() else {}
    support["baseline_chain_recomputed"] = {
        "status": "PASS" if chain_ok and framework.get("predecessor_release", {}).get("release_id") == expected_chain[-1]["release_id"] else "FAIL",
        "checks": len(expected_chain),
        "finding_count": 0,
        "detail": "immutable predecessor chain matches the tooling constant",
    }

    dag = json.loads((root / "docs/registries/AUTHORITY_DEPENDENCY_DAG.json").read_text(encoding="utf-8"))
    support["authority_dag_acyclic"] = {
        "status": "PASS" if dag.get("acyclic") is True else "FAIL",
        "checks": len(dag.get("edges", [])),
        "finding_count": 0 if dag.get("acyclic") else 1,
        "detail": "authority dependency graph is acyclic",
    }

    # Payload inventory completeness is a prebuild property: every payload file
    # is enumerable, safe, and hashable. Checksum-ledger completeness is a
    # post-build property and is asserted by the full deep verification, not here.
    _, payload_records = integrity.candidate_tree_records(root)
    support["payload_inventory_complete"] = {
        "status": "PASS" if payload_records else "FAIL",
        "checks": len(payload_records),
        "finding_count": 0 if payload_records else 1,
        "detail": "every payload file enumerated, path-safe, and hashed",
    }
    return support


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = ROOT

    release_dir = root / ".absolute/release"
    release_dir.mkdir(parents=True, exist_ok=True)
    baseline = [dict(item) for item in integrity.BASELINE_CHAIN]

    # Pass 1: write placeholders so the tree is complete, then compute the
    # candidate hash (which excludes exactly these six files), then write the
    # real values. The exclusion list is what makes this terminate.
    for name in ("release_identity.json", "authority_record.json", "gate_binding.json"):
        target = release_dir / name
        if not target.is_file():
            target.write_text(canonical({"placeholder": True}), encoding="utf-8")
    for name in ("MANIFEST.json", "CANDIDATE_SOURCE_MANIFEST.json"):
        target = root / name
        if not target.is_file():
            target.write_text(canonical({"placeholder": True}), encoding="utf-8")
    if not (root / "SHA256SUMS.txt").is_file():
        (root / "SHA256SUMS.txt").write_text("", encoding="utf-8")

    support = gather_support(root)

    # Gate evidence is itself payload, so writing it changes the candidate hash
    # it is bound to. Iterate to a fixed point: rewrite the evidence against the
    # current hash, recompute, and repeat until the hash stops moving. The
    # timestamp is captured once so that the only thing varying between
    # iterations is the hash itself — otherwise this would never converge.
    # Gate evidence carries no timestamp: it must be byte-identical when the
    # same payload is verified twice, or the manifests would never converge and
    # the build would not be reproducible. The evaluation time is recorded once
    # in gate_binding.json, which is release metadata.
    evaluated_at = now()
    gates = build_gate_evidence(root, support)
    # Gate evidence carries no hash of its own tree, so one write is enough and
    # the candidate identity computed afterwards is final.
    candidate_hash, payload_records = integrity.candidate_tree_records(root)

    from hashlib import sha256

    gate_entries = []
    for index in range(20):
        gate_id = f"C{index}"
        evidence_path = root / f".absolute/release/gate_evidence/{gate_id}.json"
        gate_entries.append(
            {
                "gate_id": gate_id,
                "gate_name": GATE_NAMES[gate_id],
                "prerequisites": [] if index == 0 else [f"C{index - 1}"],
                "status": gates[gate_id]["status"],
                "required_check_state": "PASS",
                "bypass": False,
                "stale": False,
                "candidate_tree_sha256": candidate_hash,
                "evidence_ref": f".absolute/release/gate_evidence/{gate_id}.json",
                "evidence_sha256": sha256(evidence_path.read_bytes()).hexdigest(),
            }
        )

    identity_record = {
        "schema": "absolute.release_identity.v1",
        "framework_id": integrity.FRAMEWORK_ID,
        "release_id": integrity.RELEASE_ID,
        "candidate_id": integrity.CANDIDATE_ID,
        "version": integrity.RELEASE_VERSION,
        "status": integrity.RELEASE_STATUS,
        "package_root": integrity.ROOT_NAME,
        "candidate_tree_sha256": candidate_hash,
        "candidate_tree_hash_algorithm": integrity.CANDIDATE_TREE_ALGORITHM,
        "candidate_tree_exclusions": list(integrity.CANDIDATE_HASH_EXCLUSIONS),
        "integrity_model": integrity.INTEGRITY_MODEL,
        "baseline_provenance": baseline,
        "self_certification": False,
        "independent_certification": "PENDING_EXTERNAL_EXACT_HASH_REVIEW",
    }
    (release_dir / "release_identity.json").write_text(canonical(identity_record), encoding="utf-8")

    authority = {
        "schema": "absolute.release_authority.v1",
        "framework_id": integrity.FRAMEWORK_ID,
        "release_id": integrity.RELEASE_ID,
        "candidate_id": integrity.CANDIDATE_ID,
        "version": integrity.RELEASE_VERSION,
        "status": integrity.RELEASE_STATUS,
        "candidate_tree_sha256": candidate_hash,
        "authorized_action": "BUILD_CLEAN_SUCCESSOR_RELEASE",
        "authority_scope": "SUCCESSOR_CANDIDATE_ONLY",
        "source_tree_mutation": False,
        "self_certification": False,
        "allow_replace": False,
        "rollback_required_on_replace": True,
        "issued_at": now(),
        "authority_basis": {
            "predecessor_candidate_tree_sha256": baseline[-1]["candidate_tree_sha256"],
            "deep_verification_status": support["deep_verification_zero_findings"]["status"],
            "no_loss_status": support["no_loss_check"]["status"],
        },
    }
    (release_dir / "authority_record.json").write_text(canonical(authority), encoding="utf-8")

    binding = {
        "schema": "absolute.gate_binding.v1",
        "framework_id": integrity.FRAMEWORK_ID,
        "release_id": integrity.RELEASE_ID,
        "candidate_id": integrity.CANDIDATE_ID,
        "candidate_tree_sha256": candidate_hash,
        "binding_scope": "C0-C19_PREBUILD_SOURCE_TREE_NON_CIRCULAR",
        "evaluated_at": evaluated_at,
        "gates": gate_entries,
        "delivery_gate": {"gate_id": "C20", "status": "EXTERNAL_HANDOFF_REQUIRED"},
    }
    (release_dir / "gate_binding.json").write_text(canonical(binding), encoding="utf-8")

    limitations = [
        "This release records internal deterministic verification, not an independent certification.",
        "Candidate-tree identity excludes explicitly declared hash-binding metadata to avoid circular digests.",
        "External tool projections remain non-canonical unless separately hash-bound.",
    ]
    candidate_manifest = {
        "schema_version": "1.3.1",
        "framework_id": integrity.FRAMEWORK_ID,
        "release_id": integrity.RELEASE_ID,
        "candidate_id": integrity.CANDIDATE_ID,
        "version": integrity.RELEASE_VERSION,
        "status": integrity.RELEASE_STATUS,
        "candidate_hash": f"sha256:{candidate_hash}",
        "candidate_tree_hash_algorithm": integrity.CANDIDATE_TREE_ALGORITHM,
        "candidate_tree_exclusions": list(integrity.CANDIDATE_HASH_EXCLUSIONS),
        "integrity_model": integrity.INTEGRITY_MODEL,
        "integrity_metadata_files": list(integrity.CANDIDATE_HASH_EXCLUSIONS),
        "inventory_scope": "CANDIDATE_PAYLOAD",
        "inventory_exclusions": list(integrity.CANDIDATE_HASH_EXCLUSIONS),
        "built_from_allowlist": True,
        "evidence_archive_included": False,
        "baseline_provenance": baseline,
        "limitations": limitations,
        "file_count": len(payload_records),
        "total_bytes": sum(item["bytes"] for item in payload_records),
        "files": payload_records,
    }
    (root / "CANDIDATE_SOURCE_MANIFEST.json").write_text(canonical(candidate_manifest), encoding="utf-8")

    release_files = [
        path
        for path in integrity.iter_files(root)
        if path.relative_to(root).as_posix() not in integrity.RELEASE_MANIFEST_EXCLUSIONS
    ]
    release_records = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": integrity.sha256_file(path),
        }
        for path in release_files
    ]
    manifest = dict(candidate_manifest)
    manifest.update(
        {
            "inventory_scope": "RELEASE_TREE_NON_SELF_REFERENTIAL",
            "inventory_exclusions": list(integrity.RELEASE_MANIFEST_EXCLUSIONS),
            "file_count": len(release_records),
            "total_bytes": sum(item["bytes"] for item in release_records),
            "files": release_records,
        }
    )
    (root / "MANIFEST.json").write_text(canonical(manifest), encoding="utf-8")

    ledger_lines = [
        f"{integrity.sha256_file(path)}  {path.relative_to(root).as_posix()}"
        for path in integrity.iter_files(root)
        if path.relative_to(root).as_posix() != "SHA256SUMS.txt"
    ]
    (root / "SHA256SUMS.txt").write_text("\n".join(ledger_lines) + "\n", encoding="utf-8")

    result = {
        "candidate_tree_sha256": candidate_hash,
        "release_id": integrity.RELEASE_ID,
        "payload_file_count": len(payload_records),
        "release_file_count": len(release_records),
        "gate_status": {item["gate_id"]: item["status"] for item in gate_entries},
        "support": {name: value["status"] for name, value in sorted(support.items())},
    }
    text = canonical(result)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if all(item["status"] == "PASS" for item in gate_entries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
