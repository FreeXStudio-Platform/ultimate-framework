# Executable Surface Traceability Matrix

| Surface | Type | Location | Authorization | Test |
|---|---|---|---|---|
| `ABS.SURFACE.RELEASE.INTEGRITY` | `CLI` | `01_control_plane/manifests_releases/tools/release_integrity.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.RELEASE.BUILD` | `CLI` | `01_control_plane/manifests_releases/tools/build_release.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.RELEASE.BUILD.ALIAS` | `CLI` | `tools/secure_release_builder.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.RELEASE.VERIFY` | `CLI` | `01_control_plane/manifests_releases/tools/verify_release.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.RELEASE.VERIFY.ALIAS` | `CLI` | `tools/verify_successor_release.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.CI.PIN_VALIDATE` | `CLI` | `tools/validate_ci_pins.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.FRAMEWORK.VALIDATE` | `CLI` | `04_enforcement/validators/absolute_validate.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.TEST.RUN_ALL` | `CLI` | `09_tests_evals/run_all.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.TEST.SUCCESSOR_CONTROLS` | `CLI` | `tests/run_successor_controls.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.HOOK.PRE_WRITE` | `HOOK` | `04_enforcement/hooks/pre_write_authority_check.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.HOOK.POST_EDIT` | `HOOK` | `04_enforcement/hooks/post_edit_validation.sh` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.CI.EXAMPLE` | `CI_ACTION` | `04_enforcement/ci_policy_examples/generic_ci.yaml` | explicit release authority and gate binding | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.CONTRACT.V2.VALIDATE` | `CLI` | `tools/validate_v2_contracts.py` | read-only verification | `09_tests_evals/run_all.py` |
| `ABS.SURFACE.RELEASE.ALLOWLIST.GENERATE` | `CLI` | `01_control_plane/manifests_releases/tools/generate_release_allowlist.py` | deterministic candidate-local allowlist generation from immutable RC2 | `09_tests_evals/run_all.py` |
