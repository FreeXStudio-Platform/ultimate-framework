# Session-Close Reconciliation Hook
Before closing an execution context: finish or safely pause the atomic unit; run affected checks; update durable state, requirements, graph, decisions, findings, hashes, and capability health; preserve failed/not-run results; write the rollback point, exact next packet, and exact first action. The transcript is never the handoff authority.
