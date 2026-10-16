"""Whole-system deep verification.

One pass covers every section. A section is a named group of checks that can be
reasoned about independently; the pass only reports ``PASS`` when *every*
section reports zero findings, so a green result cannot be produced by a partial
run.

Two design rules keep this honest:

* **Derive, never trust.** No section reads a stored PASS state and repeats it.
  Hashes are recomputed from bytes, fixtures are executed, the ledger chain is
  replayed, and adversarial cases are run live and required to fail.
* **Absence is a finding.** A check that cannot execute reports
  ``NOT_RUN`` as a finding rather than being silently skipped, because a
  verification that quietly shrinks its own denominator is the exact failure the
  framework was built to prevent.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


class Section:
    """Accumulates findings for one named area of the system."""

    def __init__(self, name: str, intent: str) -> None:
        self.name = name
        self.intent = intent
        self.findings: list[dict[str, Any]] = []
        self.checks = 0

    def check(self) -> None:
        self.checks += 1

    def fail(self, code: str, message: str, path: str = "", severity: str = "HIGH") -> None:
        self.findings.append(
            {"section": self.name, "code": code, "message": message, "path": path, "severity": severity}
        )

    def expect(self, condition: bool, code: str, message: str, path: str = "", severity: str = "HIGH") -> bool:
        self.check()
        if not condition:
            self.fail(code, message, path, severity)
        return bool(condition)

    def result(self) -> dict[str, Any]:
        return {
            "section": self.name,
            "intent": self.intent,
            "status": "PASS" if not self.findings else "FAIL",
            "checks": self.checks,
            "finding_count": len(self.findings),
            "findings": self.findings,
        }


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------- framework sections


def _front_matter(path: Path) -> dict[str, Any]:
    """Parse the YAML front matter of a narrative document; absent or malformed -> {}."""
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    head, sep, _ = text[4:].partition("\n---\n")
    if not sep:
        return {}
    try:
        data = yaml.safe_load(head)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def section_identity(root: Path, include_release_metadata: bool = True) -> Section:
    """Release identity checks.

    Two scopes exist on purpose.

    *Prebuild* (``include_release_metadata=False``) verifies only the payload:
    root name, version/registry agreement, and the payload digest. It must not
    inspect MANIFEST.json or the checksum ledger, because those files are
    written *from* this verification's result. Asserting them beforehand would
    be circular, and a gate that attests to its own output is worthless.

    *Full* (the default) additionally recomputes the manifests, the checksum
    ledger, and the gate binding. This is the acceptance scope, and it runs
    after metadata generation.
    """
    section = Section(
        "FRAMEWORK_IDENTITY",
        "Release identity and payload digest recomputed from bytes"
        + (", including manifests and checksum ledger." if include_release_metadata else " (prebuild payload scope)."),
    )
    sys.path.insert(0, str(root / "01_control_plane/manifests_releases/tools"))
    try:
        import release_integrity as integrity
    except Exception as exc:
        section.fail("IDENTITY_TOOLING_UNAVAILABLE", f"release_integrity is not importable: {exc}", severity="CRITICAL")
        return section

    if include_release_metadata:
        try:
            tree = integrity.verify_tree(root)
            section.check()
        except Exception as exc:
            section.fail("TREE_INTEGRITY_FAIL", str(exc), severity="CRITICAL")
            return section
        identity = _load(root / ".absolute/release/release_identity.json")
        section.expect(
            tree["candidate_tree_sha256"] == identity["candidate_tree_sha256"],
            "CANDIDATE_HASH_DRIFT",
            "recomputed candidate hash does not match the recorded release identity",
            ".absolute/release/release_identity.json",
            "CRITICAL",
        )
        section.expect(
            identity["self_certification"] is False,
            "SELF_CERTIFICATION_ENABLED",
            "release identity permits self certification",
            ".absolute/release/release_identity.json",
            "CRITICAL",
        )
    else:
        try:
            integrity.candidate_tree_records(root)
            section.check()
        except Exception as exc:
            section.fail("PAYLOAD_INTEGRITY_FAIL", str(exc), severity="CRITICAL")
            return section

    section.expect(
        root.name == integrity.ROOT_NAME,
        "ROOT_NAME_MISMATCH",
        f"tree root {root.name!r} != declared {integrity.ROOT_NAME!r}",
    )
    framework = _load(root / "docs/registries/FRAMEWORK.json")
    for field, expected in (
        ("release_id", integrity.RELEASE_ID),
        ("version", integrity.RELEASE_VERSION),
    ):
        section.expect(
            framework.get(field) == expected,
            "REGISTRY_IDENTITY_DRIFT",
            f"FRAMEWORK.json {field}={framework.get(field)!r} != tooling {expected!r}",
            "docs/registries/FRAMEWORK.json",
        )
    section.expect(
        (root / "VERSION").read_text(encoding="utf-8").strip() == integrity.RELEASE_VERSION,
        "VERSION_FILE_DRIFT",
        "VERSION does not match the tooling release version",
        "VERSION",
    )
    return section


def section_structure(root: Path) -> Section:
    section = Section("FRAMEWORK_STRUCTURE", "Modules, requirements, interfaces, profiles, and registries are mutually resolvable.")
    import yaml

    manifests = sorted(root.rglob("MODULE_MANIFEST.yaml"))
    module_index = _load(root / "docs/registries/MODULE_INDEX.json")
    interface_index = _load(root / "docs/registries/INTERFACE_INDEX.json")
    canonical = _load(root / "docs/registries/CANONICAL_REQUIREMENTS.json")
    framework = _load(root / "docs/registries/FRAMEWORK.json")

    known_interfaces = {item["interface_id"] for item in interface_index["interfaces"]}
    indexed_modules = {item["module_id"] for item in module_index["modules"]}
    registry_requirements = {item["requirement_id"] for item in canonical["requirements"]}

    package_modules: set[str] = set()
    package_requirements: set[str] = set()
    release_version = (root / "VERSION").read_text(encoding="utf-8").strip()

    for manifest_path in manifests:
        base = manifest_path.parent
        relative = base.relative_to(root).as_posix()
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        module_id = manifest.get("module_id")
        package_modules.add(module_id)

        # Cross-representation release pin. The narrative (MODULE.md front matter), the
        # manifest and the release's VERSION file must name the same framework release.
        # 1.2.0 shipped all 33 narratives pinned to 1.0.0 while every manifest said 1.2.0,
        # and no check compared the two representations of the same fact (field-trial
        # finding F-05). A pin the verifier never reads is decoration, not a pin.
        narrative_path = base / "MODULE.md"
        section.expect(
            manifest.get("framework_release") == release_version,
            "MODULE_RELEASE_PIN_DRIFT",
            f"manifest framework_release={manifest.get('framework_release')!r} but VERSION is {release_version!r}",
            relative,
        )
        if section.expect(narrative_path.is_file(), "MODULE_NARRATIVE_MISSING", "MODULE.md missing", relative):
            narrative_release = _front_matter(narrative_path).get("framework_release")
            section.expect(
                str(narrative_release) == release_version,
                "MODULE_NARRATIVE_RELEASE_DRIFT",
                f"MODULE.md framework_release={narrative_release!r} but VERSION is {release_version!r}",
                relative,
            )

        requirements_path = base / "requirements.json"
        if not section.expect(requirements_path.is_file(), "MODULE_NO_REQUIREMENTS", "requirements.json missing", relative):
            continue
        requirements = _load(requirements_path)
        ids = {item["requirement_id"] for item in requirements.get("requirements", [])}
        package_requirements |= ids

        section.expect(
            set(manifest.get("requirements", [])) == ids,
            "MODULE_REQUIREMENT_MISMATCH",
            "manifest requirement list differs from requirements.json",
            relative,
        )
        for key, target in (manifest.get("canonical_paths") or {}).items():
            section.expect((base / target).exists(), "MODULE_CANONICAL_PATH_MISSING", f"canonical_paths.{key} -> {target}", relative)
        declared = set(manifest.get("provided_interfaces", [])) | set(manifest.get("consumed_interfaces", []))
        unknown = declared - known_interfaces
        section.expect(not unknown, "MODULE_UNKNOWN_INTERFACE", f"unresolvable interfaces {sorted(unknown)}", relative)
        for dependency in manifest.get("dependencies", []):
            section.expect(
                dependency in indexed_modules,
                "MODULE_UNKNOWN_DEPENDENCY",
                f"dependency {dependency} is not an indexed module",
                relative,
            )
        if manifest.get("status") == "CERTIFIED":
            verification = manifest.get("verification") or {}
            section.expect(
                verification.get("independent_status") in {"CERTIFIED", "CERTIFIED_WITH_ACCEPTED_RISK"}
                and bool(verification.get("candidate_hash"))
                and bool(verification.get("evidence_ids")),
                "MODULE_FALSE_CERTIFIED",
                "status CERTIFIED without independent status, candidate hash, and evidence",
                relative,
                "CRITICAL",
            )

    section.expect(
        package_modules == indexed_modules,
        "MODULE_INDEX_DRIFT",
        f"packages-only={sorted(package_modules - indexed_modules)} index-only={sorted(indexed_modules - package_modules)}",
        "docs/registries/MODULE_INDEX.json",
    )
    section.expect(
        package_requirements == registry_requirements,
        "REQUIREMENT_REGISTRY_DRIFT",
        f"packages-only={sorted(package_requirements - registry_requirements)} "
        f"registry-only={sorted(registry_requirements - package_requirements)}",
        "docs/registries/CANONICAL_REQUIREMENTS.json",
    )
    section.expect(
        framework.get("version") == release_version and framework.get("release_id") == f"ABS.RELEASE.{release_version}",
        "FRAMEWORK_REGISTRY_RELEASE_DRIFT",
        f"FRAMEWORK.json version={framework.get('version')!r} release_id={framework.get('release_id')!r} but VERSION is {release_version!r}",
        "docs/registries/FRAMEWORK.json",
    )
    counts = framework.get("counts", {})
    for label, observed in (
        ("modules", len(indexed_modules)),
        ("interfaces", len(known_interfaces)),
        ("core_requirements", len(registry_requirements)),
        ("profiles", len(list((root / "06_project_profiles").glob("*/profile.json")))),
        ("adapters", len(list((root / "05_platform_adapters").glob("*/adapter.json")))),
    ):
        section.expect(
            counts.get(label) == observed,
            "FRAMEWORK_COUNT_DRIFT",
            f"FRAMEWORK.json counts.{label}={counts.get(label)} but observed {observed}",
            "docs/registries/FRAMEWORK.json",
        )

    for interface in interface_index["interfaces"]:
        schema_relative = "04_enforcement/" + interface["schema_ref"]
        section.expect(
            (root / schema_relative).is_file(),
            "INTERFACE_SCHEMA_MISSING",
            f"{interface['interface_id']} -> {schema_relative}",
            "docs/registries/INTERFACE_INDEX.json",
        )
        section.expect(
            interface["provider_module"] in indexed_modules,
            "INTERFACE_PROVIDER_UNKNOWN",
            f"{interface['interface_id']} provider {interface['provider_module']}",
            "docs/registries/INTERFACE_INDEX.json",
        )

    for profile_path in sorted((root / "06_project_profiles").glob("*/profile.json")):
        profile = _load(profile_path)
        relative = profile_path.relative_to(root).as_posix()
        unknown = (set(profile.get("required_modules", [])) | set(profile.get("optional_modules", []))) - indexed_modules
        section.expect(not unknown, "PROFILE_UNKNOWN_MODULE", f"unresolvable modules {sorted(unknown)}", relative)
    return section


def section_representation(root: Path) -> Section:
    section = Section(
        "FRAMEWORK_REPRESENTATION",
        "Narrative, blueprint, visual, and publication forms are well formed and in parity.",
    )
    from .docvalidate import markdown_structure_findings

    for finding in markdown_structure_findings(root):
        section.check()
        section.fail(finding["code"], finding["message"], finding["path"], finding["severity"])
    section.check()

    # Visual derivatives must be reproducible from their semantic source.
    if shutil.which("dot"):
        strip = re.compile(r"<!-- Generated by graphviz version[^>]*-->", re.S)
        for source in sorted(root.rglob("*.dot")):
            relative = source.relative_to(root).as_posix()
            target = source.with_suffix(".svg")
            if not section.expect(target.is_file(), "VISUAL_DERIVATIVE_MISSING", "no rendered .svg", relative):
                continue
            rendered = subprocess.run(["dot", "-Tsvg", str(source)], capture_output=True)
            if rendered.returncode != 0:
                section.fail("VISUAL_SOURCE_UNRENDERABLE", rendered.stderr.decode()[:200], relative)
                continue
            section.expect(
                strip.sub("", rendered.stdout.decode()).strip() == strip.sub("", target.read_text(encoding="utf-8")).strip(),
                "VISUAL_DERIVATIVE_STALE",
                "the .svg derivative does not match a fresh render of its .dot source",
                relative,
            )
    else:
        section.check()
        section.fail(
            "VISUAL_PARITY_NOT_RUN",
            "graphviz 'dot' is unavailable, so visual derivative parity could not be verified",
            severity="MEDIUM",
        )

    # Every module must carry its declared representations.
    import yaml

    for manifest_path in sorted(root.rglob("MODULE_MANIFEST.yaml")):
        base = manifest_path.parent
        relative = base.relative_to(root).as_posix()
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        for name, requirement in (manifest.get("representations") or {}).items():
            if requirement != "REQUIRED":
                continue
            mapping = {
                "narrative": "MODULE.md",
                "blueprint": "blueprint/BLUEPRINT.md",
                "plain_english": "publication/plain_english.md",
                "quick_reference": "publication/quick_reference.md",
                "tests": "tests/TEST_PLAN.md",
            }
            target = mapping.get(name)
            if target:
                section.expect(
                    (base / target).is_file(),
                    "REPRESENTATION_MISSING",
                    f"representations.{name}=REQUIRED but {target} is absent",
                    relative,
                )
    return section


def section_contracts(root: Path) -> Section:
    section = Section("FRAMEWORK_CONTRACTS", "Every schema is valid and every fixture behaves as its contract requires.")
    import jsonschema

    validator_class = jsonschema.Draft202012Validator

    schema_paths = sorted((root / "04_enforcement/schemas").glob("*.json"))
    section.expect(bool(schema_paths), "NO_SCHEMAS_FOUND", "04_enforcement/schemas is empty", severity="CRITICAL")
    for path in schema_paths:
        relative = path.relative_to(root).as_posix()
        try:
            validator_class.check_schema(_load(path))
            section.check()
        except Exception as exc:
            section.fail("SCHEMA_INVALID", str(exc)[:200], relative, "CRITICAL")

    # Interface schemas are only meaningful if something exercises them.
    interfaces = _load(root / "docs/registries/INTERFACE_INDEX.json")["interfaces"]
    fixtures = root / "09_tests_evals/interface_fixtures"
    for interface in interfaces:
        name = interface["schema_ref"].rsplit("/", 1)[-1].replace(".schema.json", "")
        schema_path = root / "04_enforcement" / interface["schema_ref"]
        positive = fixtures / f"{name}.valid.json"
        negative = fixtures / f"{name}.invalid.json"
        if not section.expect(
            positive.is_file() and negative.is_file(),
            "INTERFACE_FIXTURE_MISSING",
            f"{interface['interface_id']} has no positive/negative fixture pair; the schema is unexercised",
            f"09_tests_evals/interface_fixtures/{name}.*.json",
        ):
            continue
        validator = validator_class(_load(schema_path), format_checker=jsonschema.FormatChecker())
        errors = list(validator.iter_errors(_load(positive)))
        section.expect(
            not errors,
            "INTERFACE_FIXTURE_SHOULD_PASS",
            f"valid fixture rejected: {errors[0].message if errors else ''}",
            positive.relative_to(root).as_posix(),
        )
        section.expect(
            bool(list(validator.iter_errors(_load(negative)))),
            "INTERFACE_FIXTURE_SHOULD_FAIL",
            "invalid fixture was accepted; the schema does not constrain what it claims to",
            negative.relative_to(root).as_posix(),
        )

    # Module contracts: positive passes, negative and adversarial must fail.
    for contract in sorted(root.rglob("machine/contract.schema.json")):
        base = contract.parent.parent
        relative = base.relative_to(root).as_posix()
        try:
            validator = validator_class(_load(contract), format_checker=jsonschema.FormatChecker())
        except Exception as exc:
            section.fail("MODULE_CONTRACT_INVALID", str(exc)[:200], relative, "CRITICAL")
            continue
        for fixture, should_pass in (
            ("tests/positive/valid_instance.json", True),
            ("tests/negative/missing_evidence.json", False),
            ("tests/adversarial/authority_override.json", False),
            ("machine/examples/valid.json", True),
        ):
            path = base / fixture
            if not section.expect(path.is_file(), "MODULE_FIXTURE_MISSING", fixture, relative):
                continue
            errors = list(validator.iter_errors(_load(path)))
            if should_pass:
                section.expect(not errors, "MODULE_FIXTURE_SHOULD_PASS", f"{fixture}: {errors[0].message if errors else ''}", relative)
            else:
                section.expect(bool(errors), "MODULE_FIXTURE_SHOULD_FAIL", f"{fixture} was accepted but must be rejected", relative)

    # Root examples must validate against their declared schemas.
    mapping = {
        "project_state.json": "project_state.schema.json",
        "work_packet.json": "work_packet.schema.json",
        "evidence_record.json": "evidence_record.schema.json",
        "gate_report.json": "gate_report.schema.json",
        "capability_record.json": "capability_record.schema.json",
        "session_checkpoint.json": "session_checkpoint.schema.json",
        "publication_claim.json": "publication_claim.schema.json",
    }
    for example, schema_name in mapping.items():
        example_path = root / "08_examples" / example
        schema_path = root / "04_enforcement/schemas" / schema_name
        if not section.expect(example_path.is_file() and schema_path.is_file(), "EXAMPLE_OR_SCHEMA_MISSING", example):
            continue
        validator = validator_class(_load(schema_path), format_checker=jsonschema.FormatChecker())
        errors = list(validator.iter_errors(_load(example_path)))
        section.expect(not errors, "EXAMPLE_INVALID", errors[0].message if errors else "", f"08_examples/{example}")
    return section


def section_semantics(root: Path) -> Section:
    section = Section("FRAMEWORK_SEMANTICS", "States that would let the system assert a false completion are rejected.")
    gate = _load(root / "08_examples/gate_report.json")
    section.expect(
        not (gate.get("decision") == "PASS" and not gate.get("evidence_ids")),
        "GATE_PASS_WITHOUT_EVIDENCE",
        "an example gate passes with no evidence",
        "08_examples/gate_report.json",
        "CRITICAL",
    )
    blocking = ("fail", "blocked", "not_run", "inconclusive", "stale")
    section.expect(
        not (gate.get("decision") == "PASS" and any(gate.get("counts", {}).get(key, 0) for key in blocking)),
        "GATE_PASS_WITH_BLOCKING_COUNTS",
        "an example gate passes while carrying blocking counts",
        "08_examples/gate_report.json",
        "CRITICAL",
    )
    capability = _load(root / "08_examples/capability_record.json")
    section.expect(
        not (
            capability.get("activation_state") == "ENABLED"
            and (
                capability.get("health", {}).get("state") not in {"HEALTHY", "DEGRADED"}
                or not capability.get("health", {}).get("checked_at")
            )
        ),
        "CAPABILITY_ENABLED_WITHOUT_HEALTH",
        "an enabled capability has no current health record",
        "08_examples/capability_record.json",
    )
    claim = _load(root / "08_examples/publication_claim.json")
    section.expect(
        not ("PUBLIC" in claim.get("allowed_audiences", []) and claim.get("classification") in {"CONFIDENTIAL", "RESTRICTED"}),
        "RESTRICTED_PUBLIC_CLAIM",
        "a restricted classification is published to a PUBLIC audience",
        "08_examples/publication_claim.json",
        "CRITICAL",
    )

    # Negative fixtures must still describe the condition they exist to catch.
    fixtures = root / "09_tests_evals/fixtures"
    checks: list[tuple[str, Callable[[Any], bool], str]] = [
        (
            "false_pass_no_evidence.json",
            lambda data: data.get("decision") == "PASS" and not data.get("evidence_ids"),
            "must describe a PASS with no evidence",
        ),
        (
            "enabled_unknown_health.json",
            lambda data: data.get("activation_state") == "ENABLED" and data.get("health", {}).get("state") == "UNKNOWN",
            "must describe an enabled capability with unknown health",
        ),
        (
            "restricted_public_claim.json",
            lambda data: "PUBLIC" in data.get("allowed_audiences", []) and data.get("classification") == "RESTRICTED",
            "must describe a restricted claim published publicly",
        ),
        (
            "stale_hash_review.json",
            lambda data: data.get("reviewed_hash") != data.get("active_hash"),
            "must describe a review bound to a superseded hash",
        ),
        (
            "unsafe_archive_paths.json",
            lambda data: any(item.startswith("/") or ".." in item.split("/") for item in data.get("members", [])),
            "must contain at least one traversal or absolute member path",
        ),
    ]
    for name, predicate, why in checks:
        path = fixtures / name
        if not section.expect(path.is_file(), "NEGATIVE_FIXTURE_MISSING", name, f"09_tests_evals/fixtures/{name}"):
            continue
        section.expect(predicate(_load(path)), "NEGATIVE_FIXTURE_DEGRADED", why, f"09_tests_evals/fixtures/{name}")
    return section


def section_security(root: Path) -> Section:
    section = Section("FRAMEWORK_SECURITY", "Hygiene, secret exposure, unsafe paths, and supply-chain pinning.")
    deny_names = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
    secret_patterns = [
        ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("seed_phrase", re.compile(r"(?i)\b(?:seed phrase|mnemonic)\s*[:=]\s*\S+")),
        ("credential", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
    ]
    binary_suffixes = {".zip", ".tar", ".gz", ".7z", ".pyc", ".pyo"}
    skip_scan = {".svg", ".png", ".jpg", ".jpeg", ".pdf"}

    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            section.check()
            section.fail("SYMLINK_FORBIDDEN", "symlinks are not permitted in a release tree", relative, "CRITICAL")
            continue
        if any(part in deny_names for part in path.relative_to(root).parts):
            section.check()
            section.fail("DENYLISTED_PATH", "denylisted path component", relative)
            continue
        if not path.is_file():
            continue
        section.check()
        if ".." in relative.split("/") or relative.startswith("/"):
            section.fail("UNSAFE_PATH", "traversal or absolute path", relative, "CRITICAL")
        if path.suffix.lower() in binary_suffixes:
            section.fail("NESTED_ARCHIVE_OR_BYTECODE", "release trees carry no archives or bytecode", relative)
        if path.suffix.lower() in skip_scan or path.stat().st_size >= 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in secret_patterns:
            if pattern.search(text):
                section.fail("POSSIBLE_SECRET", f"matches the {name} pattern", relative, "CRITICAL")

    folded: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        key = relative.casefold()
        if key in folded and folded[key] != relative:
            section.check()
            section.fail("CASE_COLLISION", f"collides with {folded[key]} on case-insensitive filesystems", relative)
        folded[key] = relative

    pins = subprocess.run(
        [sys.executable, str(root / "tools/validate_ci_pins.py"), str(root)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    section.expect(
        pins.returncode == 0,
        "CI_ACTION_UNPINNED",
        f"unpinned CI actions: {pins.stdout.strip()[:300]}",
        "tools/validate_ci_pins.py",
    )
    return section


def section_governance(root: Path, include_release_metadata: bool = True) -> Section:
    """Governance checks.

    The gate-binding portion is scoped out of the prebuild pass for the same
    reason the manifests are: the binding is written *from* this pass's result.
    A prebuild gate that inspects its own recorded status can never leave a
    failing state — the first FAIL becomes permanent, because the evidence for
    the gate is a check that reads the gate. Prebuild therefore verifies the
    governance registries in the tree; the binding's internal consistency is a
    post-build property, asserted by the full pass and by the release builder.
    """
    section = Section(
        "FRAMEWORK_GOVERNANCE",
        "Governance registries assert only what the tree can substantiate"
        + (", and the gate binding is internally consistent." if include_release_metadata else " (prebuild registry scope)."),
    )
    governance = root / "governance/coverage_closure_v3"
    if not section.expect(governance.is_dir(), "GOVERNANCE_MISSING", "governance/coverage_closure_v3 is absent", severity="CRITICAL"):
        return section

    configuration = _load(governance / "configuration_registry.json")
    section.expect(
        configuration.get("mandatory_gate_disable_path_exists") is False,
        "GATE_DISABLE_PATH",
        "the configuration registry admits a path that disables a mandatory gate",
        "governance/coverage_closure_v3/configuration_registry.json",
        "CRITICAL",
    )
    by_id = {entry["config_id"]: entry for entry in configuration.get("entries", [])}
    for config_id in ("ABS.CFG.RELEASE.SOURCE_TREE_MUTATION", "ABS.CFG.RELEASE.SELF_CERTIFICATION"):
        section.expect(
            by_id.get(config_id, {}).get("allowed_values") == [False],
            "NONWAIVABLE_CONTROL_WEAKENED",
            f"{config_id} no longer fixes its only allowed value to false",
            "governance/coverage_closure_v3/configuration_registry.json",
            "CRITICAL",
        )

    surfaces = _load(governance / "release_surface_registry.json")
    for field in ("open_unsafe_release_surfaces", "unknown_privileged_surfaces"):
        section.expect(
            surfaces.get(field) == 0,
            "OPEN_RELEASE_SURFACE",
            f"{field}={surfaces.get(field)}",
            "governance/coverage_closure_v3/release_surface_registry.json",
            "CRITICAL",
        )

    gate_map = _load(governance / "legacy_gate_id_map.json")
    canonical = {item["canonical_id"] for item in gate_map.get("mapping", []) if item.get("canonical_id")}
    section.expect(
        canonical == {f"C{index}" for index in range(21)},
        "GATE_MAP_INCOMPLETE",
        f"legacy gate map does not cover C0-C20 exactly; observed {sorted(canonical)}",
        "governance/coverage_closure_v3/legacy_gate_id_map.json",
    )
    section.expect(
        gate_map.get("duplicate_active_gate_creation") is False,
        "DUPLICATE_ACTIVE_GATES",
        "the legacy gate map creates duplicate active gates",
        "governance/coverage_closure_v3/legacy_gate_id_map.json",
    )

    # The release allowlist claims an exact, fail-closed record set. 1.2.0 shipped the RC3
    # allowlist unchanged (879 records against a 1,079-file tree) because its generator could no
    # longer run and nothing read the file. A record set nobody compares to the tree is a claim.
    allowlist_path = root / "RELEASE_ALLOWLIST.json"
    if section.expect(allowlist_path.is_file(), "ALLOWLIST_MISSING", "RELEASE_ALLOWLIST.json is absent", "RELEASE_ALLOWLIST.json", "CRITICAL"):
        allowlist = _load(allowlist_path)
        release_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        section.expect(
            allowlist.get("release_id") == f"ABS.RELEASE.{release_version}"
            and allowlist.get("candidate_id") == f"ABS.CANDIDATE.{release_version}",
            "ALLOWLIST_RELEASE_DRIFT",
            f"allowlist names {allowlist.get('release_id')} / {allowlist.get('candidate_id')} but VERSION is {release_version}",
            "RELEASE_ALLOWLIST.json",
            "CRITICAL",
        )
        section.expect(
            allowlist.get("policy") == "EXACT_RECORD_SET_FAIL_CLOSED",
            "ALLOWLIST_POLICY_WEAKENED",
            f"policy={allowlist.get('policy')!r}",
            "RELEASE_ALLOWLIST.json",
            "CRITICAL",
        )
        recorded = {record.get("path") for record in allowlist.get("records", [])}
        present = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        missing_records = sorted(present - recorded)
        stale_records = sorted(recorded - present)
        section.expect(
            not missing_records and not stale_records,
            "ALLOWLIST_RECORD_SET_DRIFT",
            f"unrecorded files={missing_records[:5]}{'…' if len(missing_records) > 5 else ''} "
            f"({len(missing_records)}); records without files={stale_records[:5]}{'…' if len(stale_records) > 5 else ''} ({len(stale_records)})",
            "RELEASE_ALLOWLIST.json",
            "CRITICAL",
        )
        section.expect(
            allowlist.get("record_count") == len(allowlist.get("records", [])),
            "ALLOWLIST_COUNT_DRIFT",
            f"record_count={allowlist.get('record_count')} but {len(allowlist.get('records', []))} records",
            "RELEASE_ALLOWLIST.json",
        )
        try:
            import jsonschema

            schema = _load(root / "04_enforcement/schemas/release_allowlist.schema.json")
            errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(allowlist), key=lambda e: list(e.path))
            section.expect(
                not errors,
                "ALLOWLIST_SCHEMA_VIOLATION",
                "; ".join(error.message[:120] for error in errors[:3]),
                "RELEASE_ALLOWLIST.json",
            )
        except ImportError as exc:  # the pinned dependency is required, not optional
            section.fail("ALLOWLIST_SCHEMA_UNCHECKED", f"jsonschema unavailable: {exc}", "RELEASE_ALLOWLIST.json")

    if not include_release_metadata:
        return section

    binding = _load(root / ".absolute/release/gate_binding.json")
    gate_ids = [gate.get("gate_id") for gate in binding.get("gates", [])]
    section.expect(
        gate_ids == [f"C{index}" for index in range(20)],
        "GATE_BINDING_SEQUENCE",
        f"gate binding must list C0-C19 exactly once in order; observed {gate_ids}",
        ".absolute/release/gate_binding.json",
        "CRITICAL",
    )
    for gate in binding.get("gates", []):
        section.expect(
            gate.get("bypass") is False and gate.get("stale") is False and gate.get("status") == "PASS",
            "GATE_BYPASSED_OR_STALE",
            f"{gate.get('gate_id')} status={gate.get('status')} bypass={gate.get('bypass')} stale={gate.get('stale')}",
            ".absolute/release/gate_binding.json",
            "CRITICAL",
        )
    section.expect(
        binding.get("delivery_gate") == {"gate_id": "C20", "status": "EXTERNAL_HANDOFF_REQUIRED"},
        "DELIVERY_GATE_INTERNALIZED",
        "C20 must remain an external handoff; internalizing it would be self-certification",
        ".absolute/release/gate_binding.json",
        "CRITICAL",
    )
    return section


def section_runtime(root: Path) -> Section:
    section = Section("FRAMEWORK_RUNTIME", "Runtime invariants: rail ordering, refusal behavior, and no source mutation.")
    from . import rail
    from .documents import DOCUMENT_STEPS, GENERATORS
    from .errors import RailViolationError

    ordinals = [step.ordinal for step in rail.RAIL_STEPS]
    section.expect(ordinals == sorted(ordinals) and len(set(ordinals)) == len(ordinals), "RAIL_ORDINALS_INVALID", f"{ordinals}")
    section.expect(
        all(step.phase_on_entry in rail.LIFECYCLE_PHASES and step.phase_on_exit in rail.LIFECYCLE_PHASES for step in rail.RAIL_STEPS),
        "RAIL_PHASE_UNMAPPED",
        "a rail step names a phase outside the kernel lifecycle",
    )

    # An empty project must satisfy nothing and must refuse every mutation.
    empty: dict[str, Any] = {}
    section.expect(not rail.completed_steps(empty), "RAIL_FALSE_SATISFACTION", "steps report satisfied on an empty project", severity="CRITICAL")
    section.expect(rail.current_phase(empty) == "DISCOVERY", "RAIL_PHASE_FALSE_START", f"empty project reports {rail.current_phase(empty)}")
    refused = 0
    for step in rail.RAIL_STEPS[1:]:
        try:
            rail.check_permitted(step.command, empty)
        except RailViolationError:
            refused += 1
    section.expect(
        refused == len(rail.RAIL_STEPS) - 1,
        "RAIL_SKIP_PERMITTED",
        f"only {refused}/{len(rail.RAIL_STEPS) - 1} forward steps were refused on an empty project",
        severity="CRITICAL",
    )

    section.expect(
        set(GENERATORS) == {step.step_id for step in DOCUMENT_STEPS},
        "DOCUMENT_GENERATOR_GAP",
        "a document authoring step has no generator, or a generator has no step",
        severity="CRITICAL",
    )

    # Every mutating operation must hold the project lock for its whole
    # duration. Without it two concurrent processes read the same ledger head
    # and the same ordinal, then both write: duplicate sequence numbers, a
    # chain that can never verify again, and one artifact overwriting another.
    from . import engine

    for name in (
        "init", "set_goal", "new_work_packet", "complete_work_packet", "add_evidence",
        "run_gate", "new_document", "step_document", "seal_document", "abandon_document",
        "checkpoint", "second_pass", "record_verification", "assemble_release",
    ):
        operation = getattr(engine, name, None)
        section.expect(
            operation is not None and hasattr(operation, "__wrapped__"),
            "MUTATION_NOT_SERIALIZED",
            f"engine.{name} is not wrapped by @governed; concurrent runs can fork the ledger chain",
            "runtime/engine.py",
            "CRITICAL",
        )

    # Recording a verification is rail step S12, not a read. Left unauthorized
    # it satisfied a terminal step out of order.
    section.expect(
        "verify --record" in {step.command for step in rail.RAIL_STEPS},
        "RAIL_STEP_COMMAND_MISSING",
        "no rail step owns 'verify --record'",
        "runtime/rail.py",
    )
    # A step that can neither be satisfied nor repaired is a dead end, and the
    # rail's promise is that `absolute next` always names a usable action.
    section.expect(
        "doc abandon" in rail.CORRECTIVE_COMMANDS
        and rail.CORRECTIVE_COMMANDS["doc abandon"] >= {"S5.DOCUMENTS_AUTHORED", "S6.DOCUMENTS_SEALED"},
        "RAIL_DEAD_END_UNREPAIRABLE",
        "no corrective command can release a rail stopped by an unsealable document package",
        "runtime/rail.py",
        "CRITICAL",
    )

    # Authority comparison must not be defeatable by typing a name differently.
    from .util import normalize_actor

    section.expect(
        normalize_actor("alice") == normalize_actor("Alice") == normalize_actor("  ALICE ")
        and normalize_actor("a") != normalize_actor("b"),
        "ACTOR_IDENTITY_NOT_NORMALIZED",
        "actor names are compared raw; a self-review passes under a different capitalization",
        "runtime/util.py",
        "CRITICAL",
    )

    # Tool entry points must not write bytecode into the tree they govern.
    for relative in (
        "absolute",
        "runtime/cli.py",
        "runtime/verify.py",
        "01_control_plane/manifests_releases/tools/build_release.py",
        "01_control_plane/manifests_releases/tools/verify_release.py",
        "01_control_plane/manifests_releases/tools/release_integrity.py",
        "04_enforcement/validators/absolute_validate.py",
        "09_tests_evals/run_all.py",
        "tools/deep_verify.py",
        "tools/verifier_mutation_check.py",
    ):
        path = root / relative
        if not section.expect(path.is_file(), "TOOL_ENTRYPOINT_MISSING", relative, relative):
            continue
        section.expect(
            "sys.dont_write_bytecode = True" in path.read_text(encoding="utf-8"),
            "TOOL_MAY_MUTATE_SOURCE_TREE",
            "entry point does not disable bytecode writing; importing it would mutate the governed tree",
            relative,
        )
    return section


def section_deterministic_validator(root: Path) -> Section:
    """Run the shipped deterministic validator and adopt its errors as findings.

    The deep verifier and ``04_enforcement/validators/absolute_validate.py`` are
    two implementations of overlapping rules. Running the validator here rather
    than reimplementing it guarantees the deep pass is a strict superset: a rule
    the validator enforces can never be silently absent from the deep pass. That
    gap is not hypothetical — during 1.0.0 development the deep verifier reported
    clean while the validator was rejecting two non-conforming module artifacts.
    """
    section = Section(
        "FRAMEWORK_DETERMINISTIC_VALIDATOR",
        "The shipped deterministic validator run in a fresh process; its errors are adopted as findings.",
    )
    validator = root / "04_enforcement/validators/absolute_validate.py"
    if not section.expect(validator.is_file(), "VALIDATOR_MISSING", "the deterministic validator is absent", severity="CRITICAL"):
        return section
    result = subprocess.run(
        [sys.executable, str(validator), str(root)],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    try:
        payload = json.loads(result.stdout)
    except Exception:
        section.fail(
            "VALIDATOR_UNPARSEABLE",
            f"exit={result.returncode} stderr={result.stderr.strip()[:300]}",
            severity="CRITICAL",
        )
        return section
    for name, detail in payload.get("checks", {}).items():
        section.check()
        for error in detail.get("errors", []):
            section.fail("VALIDATOR_ERROR", f"{name}: {error}", "04_enforcement/validators/absolute_validate.py")
    section.expect(
        result.returncode == 0,
        "VALIDATOR_NONZERO_EXIT",
        f"validator exited {result.returncode} with {payload.get('counts', {}).get('errors')} error(s)",
        "04_enforcement/validators/absolute_validate.py",
    )
    return section


def section_simulation(root: Path) -> Section:
    """Run adversarial scenarios live and require each to be refused.

    A control that is only described is not a control. Each scenario below
    constructs the condition in a throwaway project and asserts the runtime
    refuses it. If a scenario silently succeeds, that is a finding.
    """
    section = Section("SIMULATION", "Adversarial scenarios executed live; each must be refused.")
    from .engine import (
        abandon_document,
        add_evidence,
        checkpoint,
        complete_work_packet,
        init,
        new_document,
        new_work_packet,
        record_verification,
        run_gate,
        seal_document,
        second_pass,
        set_goal,
        step_document,
    )
    from .errors import (
        AuthorityError,
        DocumentStepError,
        EvidenceError,
        GoalLockError,
        RailViolationError,
        SchemaError,
    )
    from .project import Project

    scenarios: list[tuple[str, Callable[[Path], None], tuple[type[Exception], ...]]] = []

    def scenario(name: str, *expected: type[Exception]):
        def register(function: Callable[[Path], None]):
            scenarios.append((name, function, expected))
            return function

        return register

    @scenario("SKIP_RAIL_TO_DOCUMENT", RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        new_document(Project(workspace), doc_id="demo", title="T", question="Q?", actor="a")

    @scenario("WORK_WITHOUT_GOAL", GoalLockError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        new_work_packet(Project(workspace), objective="o", rollback="r", actor="a")

    @scenario("WORK_WITHOUT_ROLLBACK", SchemaError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="a")
        new_work_packet(project, objective="o", rollback="   ", actor="a")

    @scenario("SEAL_WITH_UNRESOLVED_MARKERS", DocumentStepError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="a")
        new_work_packet(project, objective="o", rollback="r", actor="a")
        # Author content is supplied, but one statement is still template text.
        # The control under test is that `seal` refuses a marker wherever it
        # came from — not that `doc new` rejects a missing flag.
        new_document(
            project,
            doc_id="demo",
            title="T",
            question="Q?",
            actor="a",
            requirement_statements=["<<TODO: state the rule this package owns>>"],
            primary_failure="template text is stamped as if it were authored",
            source_evidence=["runtime/documents.py"],
            excludes=["host-specific behaviour"],
        )
        for _index in range(11):
            step_document(project, doc_id="demo", actor="a")
        seal_document(project, doc_id="demo", actor="a")

    @scenario("EVIDENCE_WITH_INVALID_RESULT", EvidenceError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        add_evidence(Project(workspace), method="m", result="DEFINITELY_FINE", actor="a")

    @scenario("COMPLETE_WORK_WITHOUT_GATE", EvidenceError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="a")
        new_work_packet(project, objective="o", rollback="r", actor="a")
        complete_work_packet(project, packet_id=None, actor="a")

    @scenario("SELF_REVIEW_AS_SECOND_PASS", AuthorityError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="author")
        second_pass(Project(workspace), reviewer="author")

    @scenario("DOCUMENT_QUESTION_NOT_A_QUESTION", SchemaError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="a")
        new_work_packet(project, objective="o", rollback="r", actor="a")
        new_document(project, doc_id="demo", title="T", question="not a question", actor="a")

    @scenario("UNKNOWN_INTERFACE_DECLARED", SchemaError, RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="a")
        new_work_packet(project, objective="o", rollback="r", actor="a")
        new_document(project, doc_id="demo", title="T", question="Q?", actor="a", provided=["ABS.IFACE.MADE.UP"])

    @scenario("INSTALL_TWICE", Exception)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")

    @scenario("UNKNOWN_PROFILE", SchemaError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="does_not_exist", adapter="claude_code", actor="a")

    @scenario("MISSION_EMPTY", GoalLockError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="   ", profile="minimal", adapter="claude_code", actor="a")

    def _to_documents(workspace: Path) -> Any:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="author")
        project = Project(workspace)
        set_goal(project, goal_id=None, statement="s", actor="author")
        new_work_packet(project, objective="o", rollback="r", actor="author")
        return project

    def _authored(project: Any, doc_id: str = "demo") -> None:
        new_document(
            project,
            doc_id=doc_id,
            title="T",
            question="Q?",
            actor="author",
            requirement_statements=["Every step shall complete before sealing.", "A seal shall carry an identity."],
            primary_failure="an unsealed package is treated as governed",
            source_evidence=["runtime/documents.py"],
            excludes=["host-specific behaviour"],
        )
        for _index in range(11):
            step_document(project, doc_id=doc_id, actor="author")

    @scenario("DOCUMENT_WITHOUT_AUTHOR_CONTENT", SchemaError)
    def _(workspace: Path) -> None:
        # A package created without the content the seal demands can never be
        # sealed, and the rail cannot pass a document it cannot seal.
        new_document(_to_documents(workspace), doc_id="demo", title="T", question="Q?", actor="author")

    @scenario("INSTALL_INTO_THE_FRAMEWORK_TREE", AuthorityError)
    def _(workspace: Path) -> None:
        # ABS.CFG.RELEASE.SOURCE_TREE_MUTATION is false; installing project
        # state into the published payload destroys its declared identity.
        init(FRAMEWORK_ROOT, project_slug="selfhost", mission="m", profile="minimal", adapter="claude_code", actor="a")

    @scenario("SELF_REVIEW_UNDER_A_DIFFERENT_SPELLING", AuthorityError)
    def _(workspace: Path) -> None:
        project = _to_documents(workspace)
        _authored(project)
        seal_document(project, doc_id="demo", actor="author")
        add_evidence(project, method="m", result="PASS", actor="author")
        run_gate(project, gate_id=None, actor="author")
        complete_work_packet(project, packet_id=None, actor="author")
        checkpoint(project, next_action="review", actor="author")
        second_pass(project, reviewer="Author")  # same person, capitalized

    @scenario("RECORD_VERIFICATION_OUT_OF_RAIL_ORDER", RailViolationError)
    def _(workspace: Path) -> None:
        init(workspace, project_slug="sim", mission="m", profile="minimal", adapter="claude_code", actor="a")
        project = Project(workspace)
        record_verification(
            project,
            report={"status": "PASS", "verified_identity": project.tree_identity()},
            actor="a",
        )

    @scenario("ABANDON_A_SEALED_DOCUMENT", AuthorityError)
    def _(workspace: Path) -> None:
        # A second, unfinished package holds the rail at S6 so the abandonment
        # is rail-permitted and the refusal must come from the seal guard: a
        # sealed identity is already bound into later claims.
        project = _to_documents(workspace)
        _authored(project, "sealed_one")
        seal_document(project, doc_id="sealed_one", actor="author")
        new_document(
            project, doc_id="unfinished", title="T", question="Q?", actor="author",
            requirement_statements=["<<TODO: unfinished>>"], primary_failure="f",
            source_evidence=["s"], excludes=["e"],
        )
        for _index in range(11):
            step_document(project, doc_id="unfinished", actor="author")
        abandon_document(project, doc_id="sealed_one", reason="changed my mind", actor="author")

    @scenario("ABANDON_WITHOUT_A_REASON", SchemaError, RailViolationError)
    def _(workspace: Path) -> None:
        project = _to_documents(workspace)
        _authored(project, "keep")
        new_document(
            project, doc_id="drop", title="T", question="Q?", actor="author",
            requirement_statements=["<<TODO: unfinished>>"], primary_failure="f",
            source_evidence=["s"], excludes=["e"],
        )
        for _index in range(11):
            step_document(project, doc_id="drop", actor="author")
        abandon_document(project, doc_id="drop", reason="   ", actor="author")

    for name, function, expected in scenarios:
        section.check()
        workspace = Path(tempfile.mkdtemp(prefix="abs-sim-"))
        try:
            function(workspace)
        except expected:
            continue
        except Exception as exc:  # wrong refusal is still a finding
            section.fail(
                "SIMULATION_WRONG_REFUSAL",
                f"{name} raised {type(exc).__name__} ({exc}); expected one of {[item.__name__ for item in expected]}",
                severity="HIGH",
            )
            continue
        else:
            section.fail(
                "SIMULATION_NOT_REFUSED",
                f"{name} completed without being refused; the control it tests is not enforced",
                severity="CRITICAL",
            )
        finally:
            shutil.rmtree(workspace, ignore_errors=True)

    # Positive control: a rail stopped by an unsealable package must be
    # repairable. A suite that only proves things are refused would be equally
    # satisfied by a runtime nobody can finish a project with.
    section.check()
    workspace = Path(tempfile.mkdtemp(prefix="abs-sim-repair-"))
    try:
        _run_stuck_rail_recovery(workspace)
    except Exception as exc:
        section.fail(
            "SIMULATION_STUCK_RAIL_UNRECOVERABLE",
            f"a rail stopped by an unsealable document could not be repaired: {type(exc).__name__}: {exc}",
            severity="CRITICAL",
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    # Positive control: the full happy path must complete end to end. A suite in
    # which everything is refused would pass the checks above while proving the
    # runtime unusable.
    section.check()
    workspace = Path(tempfile.mkdtemp(prefix="abs-sim-happy-"))
    try:
        _run_happy_path(workspace)
    except Exception as exc:
        section.fail(
            "SIMULATION_HAPPY_PATH_BROKEN",
            f"the end-to-end lifecycle failed: {type(exc).__name__}: {exc}",
            severity="CRITICAL",
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    return section


def _run_stuck_rail_recovery(workspace: Path) -> None:
    """Drive the rail into the dead end, then prove it can be walked out of.

    One good package and one that still contains template text. The rail stops
    at ``S6`` because `seal` refuses the second, correctly. Before `doc abandon`
    existed there was no command that could change that, in either direction:
    the project was unreleasable forever. This asserts the recorded-abandonment
    path reopens it and the rail reaches ``pass2``.
    """
    from .engine import (
        abandon_document,
        add_evidence,
        checkpoint,
        complete_work_packet,
        init,
        new_document,
        new_work_packet,
        run_gate,
        seal_document,
        second_pass,
        set_goal,
        step_document,
    )
    from .errors import DocumentStepError
    from .project import Project
    from .rail import next_step

    init(workspace, project_slug="stuck", mission="Prove the dead end is exitable.", profile="minimal", adapter="claude_code", actor="author")
    project = Project(workspace)
    set_goal(project, goal_id=None, statement="One sealed package exists.", actor="author")
    new_work_packet(project, objective="Author two packages.", rollback="Delete both packages.", actor="author")
    for doc_id, first in (("good", "Every step shall complete before sealing."), ("bad", "<<TODO: unfinished rule>>")):
        new_document(
            project, doc_id=doc_id, title="T", question="Q?", actor="author",
            requirement_statements=[first, "A seal shall carry an exact identity."],
            primary_failure="a package is stamped while still template text",
            source_evidence=["runtime/documents.py"], excludes=["host-specific behaviour"],
        )
        for _index in range(11):
            step_document(project, doc_id=doc_id, actor="author")
    seal_document(project, doc_id="good", actor="author")
    try:
        seal_document(project, doc_id="bad", actor="author")
    except DocumentStepError:
        pass
    else:
        raise RuntimeError("a package containing template text was sealed")

    pending = next_step(project.rail_context())
    if pending is None or pending.step_id != "S6.DOCUMENTS_SEALED":
        raise RuntimeError(f"expected the rail stopped at S6, got {pending and pending.step_id}")

    abandon_document(project, doc_id="bad", reason="superseded by 'good'; not worth completing", actor="author")

    pending = next_step(project.rail_context())
    if pending is None or pending.step_id != "S7.EVIDENCE":
        raise RuntimeError(f"abandonment did not release the rail; next is {pending and pending.step_id}")

    # Abandonment excuses a package from the authoring standard, so a status
    # field flipped by hand must not buy that excuse. Forge one and require the
    # project verification to report it.
    forged = project.path("documents", "good", "document.json")
    original = forged.read_text(encoding="utf-8")
    import json as _json

    record = _json.loads(original)
    record["status"] = "ABANDONED"
    forged.write_text(_json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    codes = {item["code"] for item in section_project_documents(project).result()["findings"]}
    forged.write_text(original, encoding="utf-8")
    if not {"ABANDONMENT_WITHOUT_REASON", "ABANDONMENT_UNSTAMPED"} & codes:
        raise RuntimeError(f"a hand-forged abandonment was accepted; findings were {sorted(codes)}")

    add_evidence(project, method="absolute doc check --id good", result="PASS", actor="author")
    if run_gate(project, gate_id=None, actor="author")["decision"] != "PASS":
        raise RuntimeError("gate did not pass after recovery")
    complete_work_packet(project, packet_id=None, actor="author")
    checkpoint(project, next_action="Run pass 2.", actor="author")
    second_pass(project, reviewer="independent_reviewer")
    if project.ledger.verify()["status"] != "PASS":
        raise RuntimeError("chain broken after recovery")


def _run_happy_path(workspace: Path) -> dict[str, Any]:
    """Drive one project from install to a recorded verification."""
    from .engine import (
        add_evidence,
        checkpoint,
        complete_work_packet,
        init,
        new_document,
        new_work_packet,
        run_gate,
        seal_document,
        second_pass,
        set_goal,
        step_document,
    )
    from .project import Project

    init(workspace, project_slug="happy", mission="Prove the lifecycle runs end to end.", profile="standard", adapter="claude_code", actor="builder")
    project = Project(workspace)
    set_goal(project, goal_id=None, statement="A sealed document and a passing gate exist.", actor="builder")
    new_work_packet(project, objective="Author one governed document.", rollback="Delete .absolute/documents/demo.", actor="builder")
    new_document(
        project,
        doc_id="demo",
        title="Demonstration package",
        question="Does the runtime author a complete package?",
        actor="builder",
        requirement_statements=[
            "Every authoring step shall complete before the package may be sealed.",
            "A sealed package shall carry an exact content identity in the source of truth.",
        ],
        primary_failure="a package is stamped while still containing template text",
        source_evidence=["runtime/documents.py DOCUMENT_STEPS", "runtime/docvalidate.py"],
        excludes=["host-specific behaviour", "any certification claim"],
    )
    for _index in range(11):
        step_document(project, doc_id="demo", actor="builder")
    seal_document(project, doc_id="demo", actor="builder")
    add_evidence(project, method="absolute doc check --id demo", result="PASS", actor="builder")
    report = run_gate(project, gate_id=None, actor="builder")
    if report["decision"] != "PASS":
        raise RuntimeError(f"gate did not pass: {report['rationale']}")
    complete_work_packet(project, packet_id=None, actor="builder")
    checkpoint(project, next_action="Run pass 2 with an independent reviewer.", actor="builder")
    second_pass(project, reviewer="independent_reviewer")
    chain = project.ledger.verify()
    if chain["status"] != "PASS":
        raise RuntimeError(f"ledger chain broken: {chain['problems']}")
    return chain


# ----------------------------------------------------------- project sections


def section_project_truth(project) -> Section:
    section = Section("PROJECT_TRUTH", "The project's source-of-truth chain and anchors replayed from raw bytes.")
    chain = project.ledger.verify()
    section.expect(chain["status"] == "PASS", "LEDGER_CHAIN_BROKEN", json.dumps(chain["problems"])[:400], ".absolute/truth/LEDGER.jsonl", "CRITICAL")
    anchors = project.ledger.verify_anchors()
    section.expect(anchors["status"] == "PASS", "LEDGER_ANCHOR_MISMATCH", json.dumps(anchors["problems"])[:400], ".absolute/truth/anchors", "CRITICAL")
    section.expect(chain["entry_count"] > 0, "LEDGER_EMPTY", "an installed project has no ledger entries", ".absolute/truth/LEDGER.jsonl")
    return section


def section_project_documents(project) -> Section:
    section = Section("PROJECT_DOCUMENTS", "Every governed document package validated, and every seal recomputed.")
    from .docvalidate import validate_document
    from .documents import TOTAL_STEPS
    from .engine import known_interfaces
    from .util import sha256_tree

    interfaces = known_interfaces()
    documents = project.documents()
    entries = project.ledger.entries()
    for record in documents:
        doc_id = record["doc_id"]
        directory = project.path("documents", doc_id)

        if record.get("status") == "ABANDONED":
            # An abandoned package is excused from the authoring standard —
            # the findings it carries are why it was abandoned, and holding it
            # to that standard forever would move the dead end from `doc seal`
            # to `verify --record` instead of removing it.
            #
            # The excuse is not free. It is granted only by a decision that is
            # actually on record, so what is verified here is the decision: a
            # stated reason, an attributed actor, a decision record on disk,
            # and a matching DECISION_RECORDED stamp in the chain. An
            # abandonment backed by none of those is a status field somebody
            # typed, and that is the hiding place this check exists to close.
            section.expect(
                bool((record.get("abandon_reason") or "").strip()),
                "ABANDONMENT_WITHOUT_REASON",
                "an abandoned package records no reason",
                doc_id,
            )
            section.expect(
                bool(record.get("abandoned_by")) and bool(record.get("abandoned_at")),
                "ABANDONMENT_UNATTRIBUTED",
                "an abandoned package records no actor or time",
                doc_id,
            )
            stamps = [
                item
                for item in entries
                if item["action"] == "DECISION_RECORDED"
                and (item.get("detail") or {}).get("module_id") == record["module_id"]
            ]
            section.expect(
                bool(stamps),
                "ABANDONMENT_UNSTAMPED",
                "an abandoned package has no DECISION_RECORDED entry in the source of truth",
                doc_id,
                "CRITICAL",
            )
            for stamp in stamps[:1]:
                decision_path = project.path("decisions", f"{stamp['subject_id']}.json")
                section.expect(
                    decision_path.is_file(),
                    "ABANDONMENT_DECISION_MISSING",
                    f"the ledger stamps {stamp['subject_id']} but no decision record exists on disk",
                    doc_id,
                    "CRITICAL",
                )
            section.expect(
                record.get("seal_sha256") is None,
                "ABANDONED_PACKAGE_WAS_SEALED",
                "a sealed package was abandoned; its identity is already bound into later claims",
                doc_id,
                "CRITICAL",
            )
            continue

        section.check()
        for finding in validate_document(directory, record, interfaces):
            section.fail(finding["code"], finding["message"], f"{doc_id}/{finding['path']}", finding["severity"])
        if record.get("status") == "SEALED":
            section.check()
            recomputed, _ = sha256_tree(directory, exclude={"document.json"})
            if recomputed != record.get("seal_sha256"):
                section.fail(
                    "DOCUMENT_SEAL_BROKEN",
                    f"content changed after sealing: recorded {record.get('seal_sha256')}, recomputed {recomputed}",
                    doc_id,
                    "CRITICAL",
                )
            stamped = [
                item
                for item in entries
                if item["action"] == "DOCUMENT_STAMPED" and item["subject_id"] == record["module_id"]
            ]
            section.expect(
                any(item["content_sha256"] == record.get("seal_sha256") for item in stamped),
                "DOCUMENT_SEAL_UNSTAMPED",
                "the recorded seal has no matching ledger stamp",
                doc_id,
                "CRITICAL",
            )
        else:
            section.expect(
                len(record.get("completed_steps", [])) <= TOTAL_STEPS,
                "DOCUMENT_STEP_OVERRUN",
                "more completed steps than the authoring sequence defines",
                doc_id,
            )
    return section


def section_project_claims(project) -> Section:
    section = Section("PROJECT_CLAIMS", "Every claim recorded in project state is backed by a ledger entry.")
    from .rail import describe

    state = project.state()
    entries = project.ledger.entries()

    # A crash between the ledger append and the state update leaves a durable
    # record whose state was never applied. The runtime's contract says that is
    # recoverable and visible; this is the check that makes it visible instead
    # of leaving the next run to reuse the id and overwrite the record.
    for drift in project.state_drift():
        section.check()
        section.fail(
            "STATE_UPDATE_NOT_APPLIED",
            f"{drift['registry']} holds {drift['highest_on_disk']} record(s) but {drift['counter']} "
            f"is {drift['recorded_next']}: {drift['meaning']}",
            ".absolute/state.json",
            "MEDIUM",
        )

    # ABS.IFACE.RUNTIME.EXECUTE and ABS.IFACE.TRUTH.STAMP are declared *provided*
    # by ABS.MODULE.RUNTIME.EXECUTOR. Declared-and-never-emitted is exactly the
    # unbacked claim this framework exists to refuse, so the emitted instances
    # are validated against the registry schemas here.
    if entries:
        import jsonschema

        for name, schema_name in (
            ("truth_stamp", "abs_iface_truth_stamp.schema.json"),
            ("runtime_execute", "abs_iface_runtime_execute.schema.json"),
        ):
            stream = project.path("interfaces", f"{name}.jsonl")
            if not section.expect(
                stream.is_file(),
                "INTERFACE_NEVER_PROVIDED",
                f"the runtime declares it provides this interface but emitted no instance ({name}.jsonl absent)",
                f".absolute/interfaces/{name}.jsonl",
            ):
                continue
            schema = _load(FRAMEWORK_ROOT / "04_enforcement/schemas" / schema_name)
            validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
            lines = [line for line in stream.read_text(encoding="utf-8").splitlines() if line.strip()]
            section.expect(
                bool(lines),
                "INTERFACE_STREAM_EMPTY",
                "the interface stream exists but holds no instance",
                f".absolute/interfaces/{name}.jsonl",
            )
            for number, line in enumerate(lines, 1):
                section.check()
                for error in list(validator.iter_errors(json.loads(line)))[:2]:
                    section.fail(
                        "INTERFACE_INSTANCE_NONCONFORMING",
                        f"line {number}: {error.message}",
                        f".absolute/interfaces/{name}.jsonl",
                    )
    context = project.rail_context()
    rail = describe(context)

    section.expect(
        not rail["out_of_order_satisfied"],
        "RAIL_OUT_OF_ORDER",
        (
            f"later step(s) {rail['out_of_order_satisfied']} are satisfied while an earlier step is open. "
            "Either a step was skipped, or the tree identity changed and invalidated an earlier step whose "
            "downstream results were never re-established. Both leave a claim standing on a foundation that "
            "no longer holds."
        ),
        ".absolute/state.json",
        "CRITICAL",
    )

    backing = {
        "active_goal_id": "GOAL_SET",
        "second_pass_identity": "PHASE_TRANSITION",
        "verified_identity": "VERIFICATION_RUN",
        "released_identity": "RELEASE_ASSEMBLED",
    }
    for field, action in backing.items():
        value = state.get(field)
        if not value:
            continue
        section.expect(
            any(item["action"] == action for item in entries),
            "STATE_CLAIM_UNBACKED",
            f"state.{field} is set but no {action} entry exists in the ledger",
            ".absolute/state.json",
            "CRITICAL",
        )

    for field in ("verified_identity", "released_identity", "second_pass_identity"):
        value = state.get(field)
        if value and value != context["tree_identity"]:
            section.check()
            section.fail(
                "STATE_CLAIM_STALE",
                f"state.{field} is bound to {value[:16]}… but the tree is now {context['tree_identity'][:16]}…",
                ".absolute/state.json",
                "MEDIUM",
            )

    for report in project.gate_reports():
        section.check()
        if report.get("decision") != "PASS":
            continue
        counts = report.get("counts", {})
        blocking = sum(counts.get(key, 0) for key in ("fail", "blocked", "not_run", "inconclusive", "stale"))
        if blocking or not report.get("evidence_ids"):
            section.fail(
                "GATE_FALSE_PASS",
                f"{report['gate_id']} claims PASS with blocking={blocking} evidence={len(report.get('evidence_ids', []))}",
                f".absolute/gates/{report['gate_id']}.json",
                "CRITICAL",
            )
        known = {item["evidence_id"] for item in project.evidence_records()}
        missing = set(report.get("evidence_ids", [])) - known
        if missing:
            section.fail(
                "GATE_EVIDENCE_MISSING",
                f"{report['gate_id']} cites evidence that does not exist: {sorted(missing)}",
                f".absolute/gates/{report['gate_id']}.json",
                "CRITICAL",
            )
    return section


# ------------------------------------------------------------------ entrypoint


def verify_framework(root: Path | None = None, include_release_metadata: bool = True) -> dict[str, Any]:
    """Deep-verify the framework installation itself."""
    root = Path(root or FRAMEWORK_ROOT).resolve()
    sections = [
        section_identity(root, include_release_metadata),
        section_structure(root),
        section_representation(root),
        section_contracts(root),
        section_semantics(root),
        section_security(root),
        section_governance(root, include_release_metadata),
        section_runtime(root),
        section_deterministic_validator(root),
        section_simulation(root),
    ]
    return _assemble(
        root,
        sections,
        scope="FRAMEWORK" if include_release_metadata else "FRAMEWORK_PREBUILD_PAYLOAD",
        verified_identity=None,
    )


def deep_verify(project=None, root: Path | None = None) -> dict[str, Any]:
    """One pass over the framework and, when present, the project on top of it."""
    root = Path(root or FRAMEWORK_ROOT).resolve()
    sections = [
        section_identity(root),
        section_structure(root),
        section_representation(root),
        section_contracts(root),
        section_semantics(root),
        section_security(root),
        section_governance(root),
        section_runtime(root),
        section_deterministic_validator(root),
        section_simulation(root),
    ]
    identity = None
    scope = "FRAMEWORK"
    if project is not None and project.installed:
        scope = "FRAMEWORK_AND_PROJECT"
        identity = project.tree_identity()
        sections += [
            section_project_truth(project),
            section_project_documents(project),
            section_project_claims(project),
        ]
    return _assemble(root, sections, scope=scope, verified_identity=identity)


def _assemble(root: Path, sections: list[Section], *, scope: str, verified_identity: str | None) -> dict[str, Any]:
    from .util import sha256_tree, utc_now

    results = [item.result() for item in sections]
    findings = [finding for item in results for finding in item["findings"]]
    findings.sort(key=lambda item: (SEVERITY_ORDER.get(item["severity"], 9), item["section"], item["code"]))
    # Reuse the release tooling's exclusion list rather than restating it. A
    # second copy would drift, and the two identities would silently disagree.
    sys.path.insert(0, str(root / "01_control_plane/manifests_releases/tools"))
    import fnmatch

    import release_integrity as integrity

    excluded = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and any(
            fnmatch.fnmatch(path.relative_to(root).as_posix(), pattern)
            for pattern in integrity.CANDIDATE_HASH_EXCLUSIONS
        )
    }
    framework_identity, _ = sha256_tree(root, exclude=excluded)
    return {
        "schema_version": "1.0.0",
        "report": "ABSOLUTE_DEEP_VERIFICATION",
        "scope": scope,
        "framework_root": str(root),
        "framework_candidate_sha256": framework_identity,
        "verified_identity": verified_identity,
        "generated_at": utc_now(),
        "status": "PASS" if not findings else "FAIL",
        "section_count": len(results),
        "sections_passed": sum(1 for item in results if item["status"] == "PASS"),
        "checks_run": sum(item["checks"] for item in results),
        "finding_count": len(findings),
        "severity_counts": {
            level: sum(1 for item in findings if item["severity"] == level)
            for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
        },
        "sections": results,
        "findings": findings,
        "certification_note": (
            "This is a deterministic verification result, not a certification. "
            "The party that builds an artifact may not certify it; independent exact-hash review remains external."
        ),
    }
