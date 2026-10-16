from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def test_rc2_identity_and_release_surface_replacement():
    framework = load("docs/registries/FRAMEWORK.json")
    surfaces = load("governance/coverage_closure_v3/release_surface_registry.json")
    assert framework["release_id"] == "ABS.RELEASE.1.0.0-RC2"
    assert framework["version"] == "1.0.0-rc.2"
    assert surfaces["open_unsafe_release_surfaces"] == 0
    assert surfaces["unknown_privileged_surfaces"] == 0
    assert surfaces["legacy_surface_disposition"]["active_unsafe_legacy_copy_remaining"] is False

def test_nonwaivable_configuration_controls():
    config = load("governance/coverage_closure_v3/configuration_registry.json")
    assert config["mandatory_gate_disable_path_exists"] is False
    by_id = {entry["config_id"]: entry for entry in config["entries"]}
    assert by_id["ABS.CFG.RELEASE.SOURCE_TREE_MUTATION"]["allowed_values"] == [False]
    assert by_id["ABS.CFG.RELEASE.SELF_CERTIFICATION"]["allowed_values"] == [False]

def test_legacy_gate_mapping_is_interpretation_only():
    gate_map = load("governance/coverage_closure_v3/legacy_gate_id_map.json")
    canonical = [item["canonical_id"] for item in gate_map["mapping"] if item["canonical_id"]]
    assert set(canonical) == {f"C{i}" for i in range(21)}
    assert gate_map["duplicate_active_gate_creation"] is False
