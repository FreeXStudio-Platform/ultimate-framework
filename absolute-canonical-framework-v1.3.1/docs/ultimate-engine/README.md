# Ultimate Engine documentation set

This directory is the governed, engine-built documentation layer for the Absolute Canonical
Framework release supplied in this repository. The framework's existing Markdown, canonical module
packages, registries, runtime, and tests are source material; they are not duplicated here.

Eight governed documents make up this set: [GUIDE-100](GUIDE-100-project-guide.md) (project guide),
[SYS-110](SYS-110-architecture.md) (architecture and domain map),
[SYS-120](SYS-120-runtime-enforcement.md) (runtime and enforcement),
[REF-130](REF-130-extension-points.md) (extension points and change risk),
[GUIDE-140](GUIDE-140-operations-verification.md) (operations and verification),
[REF-150](REF-150-evidence-limitations.md) (evidence, limitations, and audit notes),
[REF-160](REF-160-agent-blueprint-guide.md) (agent blueprint guide), and
[GUIDE-170](GUIDE-170-repository-release.md) (repository, versioning, and release operations).

Start with [GUIDE-100](GUIDE-100-project-guide.md). An agent that must avoid prose starts with
[`machine/document-index.json`](machine/document-index.json), then follows the machine and graph
artifacts named by [REF-160](REF-160-agent-blueprint-guide.md).

Regenerate the derived JSON, figures, documents, blueprint, structure graph, artifact index, and
dashboards with the commands in [GUIDE-170](GUIDE-170-repository-release.md#regenerating-the-documentation-set-for-this-layout).
Generated HTML/JSON is committed so a reader does not need a renderer merely to inspect the result.

This set does not alter the framework's runtime or canonical source. Known disagreements and
standing limitations are recorded in [REF-150](REF-150-evidence-limitations.md), not repaired here.
