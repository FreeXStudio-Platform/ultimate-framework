# Limitations

Stated plainly, because a limitation that is not written down becomes a claim.

## Certification

This package is internally verified and is **not** certified. `tools/deep_verify.py` reporting
`PASS` means every section derived zero findings from raw bytes in this environment. It does
not mean an independent party reviewed the artifact. `ABS.CFG.RELEASE.SELF_CERTIFICATION` is
fixed to `false`, gate `C20` remains `EXTERNAL_HANDOFF_REQUIRED`, and no runtime code path
emits a certification claim.

## Source-of-truth ledger

The hash chain detects editing, removing, or reordering any historical entry. It cannot by
itself detect an attacker with write access who rewrites the entire chain from genesis, since
they can recompute every digest. Anchors (`absolute truth anchor`) are the countermeasure and
only work if at least one anchor is stored where that attacker cannot reach it. An anchor kept
only inside the same working tree provides no additional protection.

The ledger is also not a substitute for filesystem permissions. It makes tampering *evident*,
not impossible.

## Concurrency

Mutating commands are serialized with an advisory `flock` on `.absolute/.lock`, held for the
whole operation. That makes two `absolute` processes on one host safe. It does **not**
coordinate across machines sharing one project over a network filesystem, where `flock`
semantics are unreliable or absent. Do not drive one project tree from two hosts at once.

## Rollback

Every work packet records a `rollback` statement and `state.rollback_ref` carries it into each
checkpoint. Nothing in the runtime **performs or rehearses** that rollback. It is a declared
intent captured at the moment the author still knew it, and it is checked for presence, not for
correctness — a packet with an unworkable rollback statement is accepted. Treat the recorded
value as documentation, not as a tested control. `ABS.MODULE.KERNEL.CHANGE_RECOVERY` specifies
reversible units and rollback rehearsal; the specification is ahead of the implementation here,
and this paragraph exists so that gap is a stated limitation rather than an implied claim.

## Abandoned document packages

`absolute doc abandon` closes a package that cannot be finished, so one bad package cannot make
an otherwise correct project permanently unreleasable. It is a recorded decision, not a
deletion: the package stays on disk, the act is stamped into the ledger with its stated reason,
a decision record is written, and `status`, the pass-2 review, and the release manifest all
report it. It is still a way to drop scope. The framework makes that evident rather than
impossible, which is the same guarantee it makes about tampering.

## Tree identity

The identity covers the work product and deliberately excludes the control plane's process
records, for the reason given in `docs/RUNTIME_GUIDE.md`. A change confined entirely to
`.absolute/evidence`, `.absolute/gates`, `.absolute/sessions`, or `.absolute/reports` does not
change the identity. Those records are covered individually by ledger stamps instead.

Everything *outside* `.absolute/` participates, with no exclusion list — including derived and
tool-managed directories such as `.git`, `__pycache__`, `node_modules`, and `.venv`. A `git
commit`, or anything that touches `.git/index`, therefore changes the work identity and makes
evidence bound to the previous identity stale. This is deliberate: an exclusion list is a place
to hide a file from the control that is supposed to cover everything. The cost is real and is
stated here rather than silently absorbed — re-run the evidence method and the gate after such
a change, or keep the governed tree separate from its version-control metadata.

A package's `framework_release` is pinned by schema to the release that authored it. Verifying
a project authored under an earlier release with a later framework will report
`DOC_SCHEMA_VIOLATION` on its manifests. That is a true statement about the binding, not a
defect, but it means an upgrade is a governed migration rather than a drop-in replacement.

## Visual derivatives

Visual parity is verified only when Graphviz `dot` is installed. Without it the deep verifier
records `VISUAL_PARITY_NOT_RUN` as a finding rather than skipping the check, and document
authoring writes a self-describing placeholder SVG carrying the declared alt text.

## Scope of the deep verifier

The deep verifier checks structure, contracts, semantics, hygiene, governance, runtime
invariants, and adversarial behaviour. It does not review whether the *content* of a document
is correct, useful, or true about the world. It can prove a package is complete, internally
consistent, and honestly stated. It cannot prove it is right.

## Simulations

The adversarial scenarios run live and each must be refused. They cover the controls the
runtime implements. They are not a proof that no other bypass exists.

`tools/verifier_mutation_check.py` injects known defects into a throwaway copy of the tree and
requires the check that claims to catch each one to report it. That answers the question the
deep verifier cannot answer about itself — whether its checks are still alive — for the defect
classes listed in that file. It is not a proof that every check is alive, and there are still
no unit tests for `runtime/` beyond what these two harnesses execute.

## Environment

Verification results are reproducible given the same Python version, the pinned dependencies
in `04_enforcement/requirements-validation.txt`, and the same Graphviz build. Results
from a different environment are comparable only where the report records the same inputs.

The visual-parity check compares bytes after stripping only Graphviz's version comment, so it is
sensitive to the renderer build, not merely to its presence. Every `.svg` in this release was
rendered by Graphviz 15.1.0 (20260618.0150), and that is the version a verifier must install to
reproduce a zero-finding `FRAMEWORK_REPRESENTATION` section. A different build that changes
layout or numeric formatting will report `VISUAL_DERIVATIVE_STALE` for every derivative; that is a
true statement about the environment, not about the sources, and re-rendering under the recorded
version restores parity. 1.2.0 shipped derivatives from two builds (2.42.4 and 2.43.0) and did not
record either, which is why it verified only where it was built.
