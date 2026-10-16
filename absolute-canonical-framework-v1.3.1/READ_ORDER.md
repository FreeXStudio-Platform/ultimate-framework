# Read Order

1. `README.md` — product boundary and current status.
2. `LIMITATIONS.md` and `SECURITY.md` — the claims deliberately not made, and the permission
   and data boundary.
3. `docs/EXECUTIVE_OVERVIEW.md` — the operating model in one document.
4. `docs/ARCHITECTURE.md` — kernel, modules, interfaces, adapters, profiles, add-ons, runtime.
5. `docs/RUNTIME_GUIDE.md` — the enforced rail, the document authoring sequence, and the
   source-of-truth ledger. Read this before running anything.
6. Select `06_project_profiles/minimal`, `standard`, `enterprise`, or `audithunt`.
7. Select and preflight one directory under `05_platform_adapters`.
8. Read the required module packages in layer order: `00_kernel`, `01_control_plane`,
   `02_capabilities`, `03_knowledge_and_documentation`, `04_enforcement`, `10_runtime`.
9. Run `python3 tools/deep_verify.py` and `python3 09_tests_evals/run_all.py`.
10. Follow `docs/INSTALLATION_GUIDE.md`; use `MIGRATION_GUIDE.md` for an existing project.
11. Use `01_control_plane/manifests_releases/RELEASE_PROCEDURE.md` only after candidate freeze.
