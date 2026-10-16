# Architecture
The release contains 33 semantic-owner packages across a compact kernel, durable control plane, capability system, knowledge/documentation system, deterministic enforcement, platform adapters, project profiles, optional add-ons, examples, tests, and the runtime. All 99 canonical requirements belong to exactly one owner. The 31 interfaces are provider-independent contracts; host-specific behavior is isolated in five adapters.

`10_runtime` owns `ABS.CONCEPT.RUNTIME_EXECUTION`: the executable enforcement of the operating loop. It exists as a canonical package rather than as loose tooling because a framework whose thesis is that nothing material is ungoverned cannot ship its own execution layer ungoverned. The runtime consumes the kernel and control-plane interfaces and provides two: `ABS.IFACE.RUNTIME.EXECUTE` and `ABS.IFACE.TRUTH.STAMP`.

Authority flows one way: Builder Program creates Framework; Framework governs a downstream Project; project feedback may inform a future framework release but cannot silently rewrite the current kernel. Raw sources are evidence, candidate files are not released, generated views are derivatives, and a package is not certified until the exact artifact hash receives independent approval.

The rail that the runtime enforces maps losslessly onto the kernel lifecycle owned by `ABS.MODULE.KERNEL.LIFECYCLE`; `docs/RUNTIME_GUIDE.md` gives the step-by-step mapping.

See `docs/registries/MODULE_INDEX.json`, `INTERFACE_INDEX.json`, and `FRAMEWORK_GRAPH.jsonl` for machine-readable topology.
