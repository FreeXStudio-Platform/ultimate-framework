# Truthful Health Model
Valid states are `HEALTHY`, `DEGRADED`, `PARTIAL`, `DEPENDENCY_FAILED`, `UNKNOWN`, `UNTESTED`, `STALE`, and `MISCONFIGURED`. Every probe records target, method, expected result, observed result, tool/environment identity, freshness, limitations, and evidence. The watcher and reporter are tested independently. Absence of an alert is never sufficient evidence of health.
