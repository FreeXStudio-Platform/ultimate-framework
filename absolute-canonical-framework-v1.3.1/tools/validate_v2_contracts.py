#!/usr/bin/env python3
"""Validate preserved V2 schemas and the RC3 clean compatibility projections.

This validator is intentionally release-local. Builder-only evidence records are
validated by the evidence replay, while this tool proves that the clean package
preserves every V2 schema and that its configuration, executable-surface, and
conversation-decision projections are both schema-valid and semantically bound
to current RC3 truth.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

try:
    import jsonschema
except Exception as exc:  # pragma: no cover - dependency failure is CLI-facing
    raise SystemExit("Install dependencies from requirements-validation.txt") from exc


SCHEMA_NAMES = (
    "certification-handoff.schema.json",
    "configuration-record.schema.json",
    "conversation-decision.schema.json",
    "coverage-scoreboard.schema.json",
    "executable-surface-record.schema.json",
    "finding.schema.json",
    "gate-control-record.schema.json",
    "gate-report.schema.json",
    "improvement-opportunity.schema.json",
    "knowledge-unit.schema.json",
    "projection-profile.schema.json",
    "simulation-scenario.schema.json",
    "source-record.schema.json",
)

SCHEMA_BY_RECORD_SET = {
    "configuration": "configuration-record.schema.json",
    "conversation_decision": "conversation-decision.schema.json",
    "executable_surface": "executable-surface-record.schema.json",
}

RECORD_SET_BY_SCHEMA = {value: key for key, value in SCHEMA_BY_RECORD_SET.items()}
EXTERNAL_RECORD_SET_BY_SCHEMA = {
    "certification-handoff.schema.json": "certification_handoff",
    "coverage-scoreboard.schema.json": "coverage_scoreboard",
    "finding.schema.json": "finding",
    "gate-control-record.schema.json": "gate_control",
    "gate-report.schema.json": "gate_report",
    "improvement-opportunity.schema.json": "improvement_opportunity",
    "knowledge-unit.schema.json": "knowledge_unit",
    "projection-profile.schema.json": "projection_profile",
    "simulation-scenario.schema.json": "simulation_scenario",
    "source-record.schema.json": "source_record",
}

EXPECTED_DECISION_IDS = [f"ABS.DEC.CONV.{number:03d}" for number in range(1, 53)]
PERMITTED_CERTIFICATION_OUTCOMES = {
    "CERTIFIED",
    "CERTIFIED_WITH_FORMALLY_ACCEPTED_NONBLOCKING_RISK",
    "REJECTED_REMEDIATION_REQUIRED",
    "UNVERIFIABLE_BLOCKED",
}
PASS_LIKE_SIMULATION_STATES = {
    "EXPECTED_SUCCESS_OBSERVED",
    "EXPECTED_REJECTION_OBSERVED",
    "EXPECTED_BLOCK_OBSERVED",
    "EXPECTED_DEGRADATION_WITH_FALLBACK_OBSERVED",
}
ACCESSIBLE_SOURCE_STATES = {"KNOWN_ACCESSIBLE", "DISCOVERED_ACCESSIBLE"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        records.append(value)
    return records


def schema_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    return [
        f"{('/'.join(str(part) for part in error.path) or '$')}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    ]


def metric_pairs(value: Any) -> Iterable[tuple[int | float, int | float]]:
    if isinstance(value, dict):
        if isinstance(value.get("numerator"), (int, float)) and isinstance(value.get("denominator"), (int, float)):
            yield value["numerator"], value["denominator"]
        for child in value.values():
            yield from metric_pairs(child)
    elif isinstance(value, list):
        for child in value:
            yield from metric_pairs(child)


def semantic_errors(schema_name: str, record: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if schema_name == "certification-handoff.schema.json":
        outcomes = record.get("permitted_outcomes", [])
        if set(outcomes) != PERMITTED_CERTIFICATION_OUTCOMES or len(outcomes) != len(PERMITTED_CERTIFICATION_OUTCOMES):
            errors.append("certification handoff must expose each permitted outcome exactly once")
    elif schema_name == "configuration-record.schema.json":
        if not record.get("precedence"):
            errors.append("configuration precedence must be nonempty")
        if record.get("secret_reference") and record.get("default") not in (None, ""):
            errors.append("secret-referenced configuration must not contain a plaintext default")
    elif schema_name == "conversation-decision.schema.json":
        if record.get("status") == "VERIFIED_IMPLEMENTED":
            if not record.get("implementation_refs") or not record.get("test_refs"):
                errors.append("verified decision requires implementation_refs and test_refs")
            for reference in [*record.get("implementation_refs", []), *record.get("test_refs", [])]:
                if "::" not in reference and not (root / reference).is_file():
                    errors.append(f"verified decision reference does not exist: {reference}")
    elif schema_name == "coverage-scoreboard.schema.json":
        if record.get("status") == "PASS" and record.get("hard_failures"):
            errors.append("PASS scoreboard cannot contain hard failures")
        for numerator, denominator in metric_pairs(record.get("metrics", {})):
            if denominator < 0 or numerator < 0 or numerator > denominator:
                errors.append(f"invalid scoreboard metric {numerator}/{denominator}")
    elif schema_name == "executable-surface-record.schema.json":
        location = record.get("location")
        if record.get("status") == "VERIFIED_ACTIVE" and (not location or not (root / location).is_file()):
            errors.append(f"verified active surface does not exist: {location}")
        authorization = str(record.get("authorization", "")).strip().lower()
        if record.get("state_changing") and authorization in {"read-only", "read-only verification"}:
            errors.append("state-changing surface cannot use read-only authorization")
    elif schema_name == "finding.schema.json":
        if record.get("state") == "RESOLVED" and not record.get("closure_evidence_ids"):
            errors.append("resolved finding requires closure evidence")
    elif schema_name == "gate-control-record.schema.json":
        if record.get("state") == "PASS" and not record.get("evidence_ids"):
            errors.append("PASS control requires evidence")
    elif schema_name == "gate-report.schema.json":
        if record.get("state") == "PASS":
            if record.get("decision") != "PASS":
                errors.append("PASS gate state requires PASS decision")
            if record.get("open_findings"):
                errors.append("PASS gate cannot have open findings")
            bad = {"fail", "blocked", "not_run", "inconclusive", "stale"}
            if any(record.get("counts", {}).get(key, 0) for key in bad):
                errors.append("PASS gate cannot contain non-pass counts")
    elif schema_name == "improvement-opportunity.schema.json":
        if record.get("priority") == "MUST" and not record.get("acceptance_criteria"):
            errors.append("MUST opportunity requires acceptance criteria")
    elif schema_name == "knowledge-unit.schema.json":
        mapped = record.get("rc_mapping_state") not in {"UNKNOWN_REQUIRES_REVIEW", "MISSING_FROM_RC1"}
        if mapped and not record.get("rc_target_refs"):
            errors.append("mapped knowledge unit requires rc_target_refs")
    elif schema_name == "projection-profile.schema.json":
        if record.get("status") == "INACTIVE" and (
            record.get("permission_mode") != "NONE" or record.get("sync_direction") != "NONE"
        ):
            errors.append("inactive projection must have NONE permission and sync direction")
    elif schema_name == "simulation-scenario.schema.json":
        if record.get("status") in PASS_LIKE_SIMULATION_STATES and not record.get("evidence_ids"):
            errors.append("observed simulation outcome requires evidence")
    elif schema_name == "source-record.schema.json":
        if record.get("access_state") in ACCESSIBLE_SOURCE_STATES and not record.get("sha256"):
            errors.append("accessible source requires sha256")
    return errors


def semantic_counterexample(schema_name: str, fixture: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(fixture)
    if schema_name == "certification-handoff.schema.json":
        value["permitted_outcomes"] = []
    elif schema_name == "configuration-record.schema.json":
        value["secret_reference"] = True
        value["default"] = "plaintext-secret"
    elif schema_name == "conversation-decision.schema.json":
        value["implementation_refs"] = []
    elif schema_name == "coverage-scoreboard.schema.json":
        value["hard_failures"] = ["fixture failure"]
    elif schema_name == "executable-surface-record.schema.json":
        value["state_changing"] = True
        value["authorization"] = "read-only verification"
    elif schema_name == "finding.schema.json":
        value["closure_evidence_ids"] = []
    elif schema_name == "gate-control-record.schema.json":
        value["evidence_ids"] = []
    elif schema_name == "gate-report.schema.json":
        value["counts"]["fail"] = 1
    elif schema_name == "improvement-opportunity.schema.json":
        value["priority"] = "MUST"
        value["acceptance_criteria"] = []
    elif schema_name == "knowledge-unit.schema.json":
        value["rc_target_refs"] = []
    elif schema_name == "projection-profile.schema.json":
        value["permission_mode"] = "SCOPED_WRITE"
    elif schema_name == "simulation-scenario.schema.json":
        value["evidence_ids"] = []
    elif schema_name == "source-record.schema.json":
        value["sha256"] = None
    return value


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    schema_root = root / "04_enforcement/schemas/coverage_closure_v2"
    fixture_path = root / "09_tests_evals/fixtures/v2_contracts/POSITIVE_FIXTURES.json"
    contracts_root = root / "governance/coverage_closure_v3/v2_contracts"
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        if not passed:
            errors.append(f"{name}: {detail}")

    discovered = sorted(path.name for path in schema_root.glob("*.schema.json"))
    record("schema_inventory", discovered == sorted(SCHEMA_NAMES), {"expected": list(SCHEMA_NAMES), "actual": discovered})

    schemas: dict[str, dict[str, Any]] = {}
    for name in SCHEMA_NAMES:
        path = schema_root / name
        try:
            schema = read_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            schemas[name] = schema
            record(f"schema_meta::{name}", True, schema.get("$id"))
        except Exception as exc:
            record(f"schema_meta::{name}", False, str(exc))

    index_path = root / "docs/registries/MACHINE_CONTRACT_INDEX.json"
    try:
        machine_index = read_json(index_path)
        indexed_contracts = machine_index.get("schemas", [])
    except Exception as exc:
        machine_index = {}
        indexed_contracts = []
        record("machine_contract_index", False, str(exc))
    else:
        indexed_names = [Path(str(item.get("path", ""))).name for item in indexed_contracts]
        record(
            "machine_contract_index_inventory",
            len(indexed_contracts) == 13 and sorted(indexed_names) == sorted(SCHEMA_NAMES),
            {"records": len(indexed_contracts), "schemas": indexed_names},
        )

    try:
        index_compatibility_manifest = read_json(contracts_root / "CONTRACT_COMPATIBILITY_MANIFEST.json")
    except Exception:
        index_compatibility_manifest = {}
    try:
        module_ids = {
            item["module_id"]
            for item in read_json(root / "docs/registries/MODULE_INDEX.json").get("modules", [])
        }
    except Exception:
        module_ids = set()

    allowed_scopes = {"CLEAN", "EVIDENCE", "HANDOFF"}
    for item in indexed_contracts:
        schema_path_text = str(item.get("path", ""))
        schema_name = Path(schema_path_text).name
        item_errors: list[str] = []
        try:
            resolved_schema_path = (root / schema_path_text).resolve()
            resolved_schema_path.relative_to(root)
        except Exception:
            item_errors.append(f"schema path escapes root: {schema_path_text}")
            resolved_schema_path = root / "__invalid_schema_path__"
        if not resolved_schema_path.is_file():
            item_errors.append(f"schema path does not resolve: {schema_path_text}")
        else:
            if item.get("sha256") != sha256_file(resolved_schema_path):
                item_errors.append("schema sha256 mismatch")
            loaded_schema = schemas.get(schema_name, {})
            if item.get("schema_id") != loaded_schema.get("$id"):
                item_errors.append("schema_id does not match schema $id")
        if item.get("owner_module") not in module_ids:
            item_errors.append(f"unknown owner_module: {item.get('owner_module')}")

        applicability = item.get("applicability")
        if not isinstance(applicability, dict):
            item_errors.append("missing applicability object")
            applicability = {}
        scopes = applicability.get("scopes")
        if not isinstance(scopes, list) or not scopes or len(scopes) != len(set(scopes)) or not set(scopes).issubset(allowed_scopes):
            item_errors.append(f"invalid applicability scopes: {scopes}")
            scopes = []
        actual = applicability.get("actual_instance")
        if not isinstance(actual, dict):
            item_errors.append("missing actual_instance contract")
            actual = {}
        actual_scope = actual.get("scope")
        actual_path = str(actual.get("path", ""))
        resolution_policy = actual.get("resolution_policy")
        if actual_scope not in scopes:
            item_errors.append("actual instance scope is outside applicability scopes")
        if actual_scope == "CLEAN":
            if resolution_policy != "LOCAL_FILE_REQUIRED":
                item_errors.append("CLEAN actual instance requires LOCAL_FILE_REQUIRED policy")
            try:
                resolved_actual_path = (root / actual_path).resolve()
                resolved_actual_path.relative_to(root)
            except Exception:
                item_errors.append(f"actual instance path escapes root: {actual_path}")
                resolved_actual_path = root / "__invalid_actual_path__"
            if not resolved_actual_path.is_file():
                item_errors.append(f"actual instance path does not resolve: {actual_path}")
            record_set = RECORD_SET_BY_SCHEMA.get(schema_name)
            expected_path = index_compatibility_manifest.get("clean_record_sets", {}).get(record_set, {}).get("path")
            if expected_path and actual_path != f"governance/coverage_closure_v3/v2_contracts/{expected_path}":
                item_errors.append("actual CLEAN path disagrees with compatibility manifest")
        elif actual_scope in {"EVIDENCE", "HANDOFF"}:
            expected_prefix = "RC3_BUILD_EVIDENCE::" if actual_scope == "EVIDENCE" else "RC3_HANDOFF::"
            if not resolution_policy or not str(resolution_policy).startswith("EXTERNAL_PACKAGE_REQUIRED"):
                item_errors.append("external actual instance requires EXTERNAL_PACKAGE_REQUIRED policy")
            if not actual_path.startswith(expected_prefix) or not actual_path.removeprefix(expected_prefix):
                item_errors.append(f"invalid external logical path: {actual_path}")
            record_set = EXTERNAL_RECORD_SET_BY_SCHEMA.get(schema_name)
            expected_path = index_compatibility_manifest.get("evidence_record_sets", {}).get(record_set)
            if expected_path and actual_path != expected_path:
                item_errors.append("external actual path disagrees with compatibility manifest")
        else:
            item_errors.append(f"unsupported actual instance scope: {actual_scope}")
        record(f"machine_contract_index::{schema_name}", not item_errors, item_errors or "hash/owner/applicability/path valid")

    try:
        fixtures = read_json(fixture_path)
    except Exception as exc:
        fixtures = {}
        record("positive_fixture_file", False, str(exc))
    else:
        record("positive_fixture_inventory", sorted(fixtures) == sorted(SCHEMA_NAMES), sorted(fixtures))

    required_negative_count = 0
    for name in SCHEMA_NAMES:
        if name not in schemas or name not in fixtures:
            continue
        fixture = fixtures[name]
        fixture_errors = schema_errors(schemas[name], fixture)
        record(f"positive_fixture::{name}", not fixture_errors, fixture_errors or "valid")
        semantics = semantic_errors(name, fixture, root)
        record(f"positive_fixture_semantics::{name}", not semantics, semantics or "valid")
        for required_field in schemas[name].get("required", []):
            required_negative_count += 1
            mutated = copy.deepcopy(fixture)
            mutated.pop(required_field, None)
            validation_errors = list(jsonschema.Draft202012Validator(schemas[name]).iter_errors(mutated))
            rejected = any(error.validator == "required" and required_field in error.message for error in validation_errors)
            record(f"required_negative::{name}::{required_field}", rejected, "rejected" if rejected else "unexpectedly accepted")
        counterexample = semantic_counterexample(name, fixture)
        counterexample_errors = semantic_errors(name, counterexample, root)
        record(f"semantic_negative::{name}", bool(counterexample_errors), counterexample_errors or "unexpectedly accepted")

    record("required_negative_denominator", required_negative_count == 86, required_negative_count)

    try:
        compatibility_manifest = read_json(contracts_root / "CONTRACT_COMPATIBILITY_MANIFEST.json")
    except Exception as exc:
        compatibility_manifest = {}
        record("compatibility_manifest", False, str(exc))
    else:
        record(
            "compatibility_manifest",
            compatibility_manifest.get("schema_contracts") == 13
            and compatibility_manifest.get("release_id") == "ABS.RELEASE.1.0.0-RC3",
            {"schema_contracts": compatibility_manifest.get("schema_contracts"), "release_id": compatibility_manifest.get("release_id")},
        )

    actual_records: dict[str, list[dict[str, Any]]] = {}
    for record_set, schema_name in SCHEMA_BY_RECORD_SET.items():
        descriptor = compatibility_manifest.get("clean_record_sets", {}).get(record_set, {})
        path = contracts_root / str(descriptor.get("path", ""))
        try:
            records = read_jsonl(path)
        except Exception as exc:
            record(f"actual_records::{record_set}", False, str(exc))
            continue
        actual_records[record_set] = records
        expected = descriptor.get("records")
        record(f"actual_count::{record_set}", len(records) == expected, {"expected": expected, "actual": len(records)})
        validation_failures = []
        semantic_failures = []
        for index, item in enumerate(records, 1):
            validation_failures.extend(f"record {index}: {message}" for message in schema_errors(schemas[schema_name], item))
            semantic_failures.extend(f"record {index}: {message}" for message in semantic_errors(schema_name, item, root))
        record(f"actual_schema::{record_set}", not validation_failures, validation_failures or f"{len(records)} records valid")
        record(f"actual_semantics::{record_set}", not semantic_failures, semantic_failures or f"{len(records)} records valid")

    configuration_records = actual_records.get("configuration", [])
    canonical_configuration = read_json(root / "governance/coverage_closure_v3/configuration_registry.json").get("entries", [])
    canonical_by_id = {item["config_id"]: item for item in canonical_configuration}
    configuration_errors = []
    if len({item.get("config_id") for item in configuration_records}) != len(configuration_records):
        configuration_errors.append("duplicate V2 configuration IDs")
    for item in configuration_records:
        canonical_id = item.get("canonical_config_id")
        canonical = canonical_by_id.get(canonical_id)
        if canonical is None:
            configuration_errors.append(f"unknown canonical configuration {canonical_id}")
            continue
        if item.get("config_id") != canonical_id.replace("ABS.CFG.", "ABS.CONFIG.", 1):
            configuration_errors.append(f"non-deterministic V2 configuration ID for {canonical_id}")
        for field in ("source", "required", "default", "precedence", "validation", "secret_reference"):
            expected_value = canonical.get("secret") if field == "secret_reference" else canonical.get(field)
            if item.get(field) != expected_value:
                configuration_errors.append(f"configuration parity mismatch {canonical_id}.{field}")
    nonwaivable = {"ABS.CONFIG.RELEASE.SOURCE_TREE_MUTATION", "ABS.CONFIG.RELEASE.SELF_CERTIFICATION"}
    for item in configuration_records:
        if item.get("config_id") in nonwaivable and (item.get("default") is not False or item.get("allowed_values") != [False]):
            configuration_errors.append(f"nonwaivable false-only configuration weakened: {item.get('config_id')}")
    record("configuration_canonical_parity", not configuration_errors, configuration_errors or "6/6 parity")

    surface_records = actual_records.get("executable_surface", [])
    canonical_surface_registry = read_json(root / "governance/coverage_closure_v3/release_surface_registry.json")
    canonical_surface_by_id = {item["surface_id"]: item for item in canonical_surface_registry.get("active_surfaces", [])}
    surface_errors = []
    if set(canonical_surface_by_id) != {item.get("surface_id") for item in surface_records}:
        surface_errors.append("canonical/V2 surface ID sets differ")
    for item in surface_records:
        canonical = canonical_surface_by_id.get(item.get("surface_id"), {})
        if item.get("location") != canonical.get("path") or item.get("path") != canonical.get("path"):
            surface_errors.append(f"surface path mismatch {item.get('surface_id')}")
        if item.get("status") != "VERIFIED_ACTIVE":
            surface_errors.append(f"active surface lacks VERIFIED_ACTIVE status {item.get('surface_id')}")
    if canonical_surface_registry.get("open_unsafe_release_surfaces") != 0 or canonical_surface_registry.get("unknown_privileged_surfaces") != 0:
        surface_errors.append("canonical surface registry contains open or unknown privileged surfaces")
    record("surface_canonical_parity", not surface_errors, surface_errors or f"{len(surface_records)}/{len(surface_records)} parity")

    decision_records = actual_records.get("conversation_decision", [])
    decision_errors = []
    ids = [item.get("decision_id") for item in decision_records]
    if ids != EXPECTED_DECISION_IDS:
        decision_errors.append("decision IDs are not the exact ordered ABS.DEC.CONV.001-.052 set")
    if any(item.get("status") != "VERIFIED_IMPLEMENTED" for item in decision_records):
        decision_errors.append("decision execution registry contains a non-verified status")
    record("decision_execution_closure", not decision_errors, decision_errors or "52/52 verified and ordered")

    report = {
        "schema_version": "1.0.0",
        "validator_id": "ABS.VALIDATOR.V2.CONTRACTS.RC3",
        "root": str(root),
        "status": "PASS" if not errors else "FAIL",
        "counts": {
            "schemas": len(schemas),
            "positive_fixtures": sum(1 for item in checks if item["check"].startswith("positive_fixture::") and item["pass"]),
            "required_field_negative_tests": required_negative_count,
            "semantic_negative_tests": sum(1 for item in checks if item["check"].startswith("semantic_negative::") and item["pass"]),
            "actual_configuration_records": len(configuration_records),
            "actual_executable_surface_records": len(surface_records),
            "actual_conversation_decision_records": len(decision_records),
            "checks": len(checks),
            "errors": len(errors),
        },
        "checks": checks,
        "errors": errors,
        "limitations": [
            "Builder-only evidence record sets are validated during RC3 evidence replay, not from the clean package.",
            "Schema conformance is necessary but supplemented here with explicit semantic invariants."
        ],
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--report")
    args = parser.parse_args()
    report = run(Path(args.root))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
