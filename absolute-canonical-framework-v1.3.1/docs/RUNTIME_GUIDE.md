# Runtime Guide

The runtime is the executable form of the operating loop. Everything below is enforced, not
advised: a command that is not the current step is refused, and the refusal names both the
rule and the action that is permitted instead.

## The rail

Thirteen steps, in order. `absolute next` always reports exactly one.

| # | Step | Command | Why it cannot be skipped |
|---|---|---|---|
| 1 | `S1.INSTALL` | `absolute init` | Nothing can be governed before the project has a frozen identity and a source of truth. |
| 2 | `S2.GOAL_LOCK` | `absolute goal set` | `ABS.REQ.GOAL_LOCK.002` rejects material action with no upward goal link. |
| 3 | `S3.WORK_OPENED` | `absolute wp new` | Work executes as one reversible bounded unit with a declared rollback. |
| 4 | `S4.DOCUMENTS_CREATED` | `absolute doc new` | The unit of knowledge is a canonical package, not a loose file. |
| 5 | `S5.DOCUMENTS_AUTHORED` | `absolute doc step` | `ABS.REQ.DOCUMENT_BLUEPRINT_PARITY.002` requires lockstep authoring, not back-filling. |
| 6 | `S6.DOCUMENTS_SEALED` | `absolute doc seal` | An unstamped document has no identity, so nothing later can bind to it. |
| 7 | `S7.EVIDENCE` | `absolute evidence add` | A completion claim without evidence is not a claim. |
| 8 | `S8.GATE` | `absolute gate run` | The gate is what converts evidence into a permitted state change. |
| 9 | `S9.WORK_COMPLETED` | `absolute wp complete` | A packet closes only once its gate passed against the current identity. |
| 10 | `S10.CHECKPOINT` | `absolute checkpoint` | Recovery must not depend on a live context that can be lost. |
| 11 | `S11.SECOND_PASS` | `absolute pass2` | Pass 1 builds the candidate; pass 2 reviews it frozen, and not by its author. |
| 12 | `S12.VERIFIED` | `absolute verify --record` | Every claim must be reproducible from raw bytes by a fresh process. |
| 13 | `S13.RELEASED` | `absolute release` | Release is the only step producing an externally shippable identity. |

Read-only commands (`status`, `next`, `explain`, `*/list`, `truth log`, `truth verify`,
`verify`) are permitted in any state, including before installation. Refusing to let an
operator look at a blocked project would make the block undiagnosable.

Steps 3–9 are repeatable: a second work packet or a second document may be opened while the
rail sits at or before the step that owns it. Repeatability never permits moving forward.

## Authoring a document

A document is a canonical module package — one bounded semantic scope in every representation
that applies to it. Eleven steps, in order:

`D1.SCOPE` → `D2.NARRATIVE` → `D3.MANIFEST` → `D4.REQUIREMENTS` → `D5.BLUEPRINT` →
`D6.VISUAL` → `D7.MACHINE` → `D8.TESTS` → `D9.INTEGRATION` → `D10.PUBLICATION` →
`D11.CHANGELOG`

Each step generates its artifacts from what was declared at `doc new`, so identity,
requirement IDs, states, and the primary failure flow into every representation from one
place. That is what keeps them in parity rather than merely adjacent.

Because every representation is generated from what was declared at `doc new`, the
author-specific content is required there: `--requirement` (at least one), `--failure`,
`--source-evidence`, and `--excludes`. Omitting any of them produces a package whose template
text `doc seal` will refuse, and the rail cannot advance past a document it cannot seal — so
the refusal happens at creation, where it costs nothing.

Anything the runtime cannot derive is written as a `<<TODO: …>>` marker. `doc seal` refuses
while a single marker remains, so a package can never be stamped while it still contains
template text. `doc seal` additionally requires all eleven steps complete and zero validation
findings — including conformance to the framework's own manifest, policy, and visual schemas.
A project document is held to exactly the standard a framework module is held to.

## When a package cannot be finished

A package that cannot be sealed would otherwise stop `S5`/`S6` permanently: the rail requires
every document to be authored and sealed, and nothing could remove one. `absolute doc abandon
--id <slug> --reason "<why>"` closes it.

Abandonment is a corrective command, not a rail step: it is permitted only while the rail is
actually stopped at `S5` or `S6`, it advances nothing, and the rail still has to be walked
forward normally. It is refused for a `SEALED` package, whose identity is already bound into
later claims, and refused without a stated reason. The package is not deleted — it stays on
disk, a `DECISION_RECORDED` entry is stamped into the ledger, a decision record is written to
`.absolute/decisions/`, and `absolute status`, the pass-2 review, and the release manifest each
report it. Abandoning every package leaves nothing to review, and `pass2` refuses.

## The source of truth

`.absolute/truth/LEDGER.jsonl` is append-only and hash-chained: each entry commits to the
digest of the entry before it. Editing, removing, or reordering any historical entry
invalidates every entry after it, and `absolute truth verify` reports the sequence number
where the chain broke.

A local chain cannot by itself detect an attacker who rewrites the entire chain from genesis.
`absolute truth anchor` writes a detached receipt naming the head digest and entry count.
Store an anchor somewhere the chain's holder does not solely control — a commit, a signed
tag, a second machine — and `truth verify` will then detect a full rewrite as soon as one
anchor survives. Anchors are written automatically at install, at each checkpoint, and at
release.

Every mutating command is serialized on `.absolute/.lock` for its whole duration. Two
concurrent processes would otherwise read the same chain head and the same identifier counter
and both write, forking the chain at one sequence number and overwriting one record with the
other. `absolute` will wait for a competing process and then refuse rather than race it.

Identifiers are allocated past whatever is already on disk, not from the state counter alone.
Artifacts are written before the ledger entry and the ledger entry before the state update, so
a process killed mid-operation leaves a durable record the counter still points at; reusing
that identifier would overwrite the record and leave the ledger asserting something no longer
true. `absolute status` reports the situation on a `RECOVERY:` line until the next command
clears it.

The runtime emits an instance of each interface it declares it provides —
`ABS.IFACE.RUNTIME.EXECUTE` for every rail decision, permitted or refused, and
`ABS.IFACE.TRUTH.STAMP` for every ledger append — to `.absolute/interfaces/`. Deep verification
validates every emitted instance against the registry schema. A provided interface that nothing
ever provides is the unbacked claim this framework exists to refuse.

## Identity and staleness

The tree identity covers the work product: every project source file, the frozen project
identity, and every governed document package. It excludes the control plane's own process
records — evidence, gates, checkpoints, reports, work-packet status, the ledger — because
otherwise recording an observation would change the identity that observation was bound to,
and every gate would go stale against its own evidence. Those records are not unprotected:
each is hash-stamped individually into the ledger when written.

Evidence is bound to the identity it was computed against. When the tree changes:

* evidence whose **method has been re-run** against the new identity is *superseded* —
  informational, never blocking;
* evidence whose method has **not** been re-run is *stale* — blocking.

That distinction is deliberate. Treating all history as blocking would make a gate unpassable
forever after the first change; ignoring all history would let coverage disappear silently,
because a check that once ran and then stopped would look identical to one that never
existed. Renaming a check does not count as re-running it.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | generic failure, or verification findings |
| 2 | gate did not pass |
| 3 | rail violation |
| 4 | ledger integrity failure |
| 5 | goal lock violation |
| 6 | authority violation, including self-review as pass 2 |
| 7 | schema violation |
| 8 | document step violation |
| 9 | self-certification refused |
| 10 | evidence violation |
