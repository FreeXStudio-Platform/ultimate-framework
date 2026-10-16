"""The project source of truth: an append-only, hash-chained ledger.

Every governed fact about a project — its installation, each document stamp,
each lifecycle transition, each piece of evidence, each gate decision, each
checkpoint — is one line in ``.absolute/truth/LEDGER.jsonl``.

Why a chain and not a log: the framework's central claim is that a completion
state cannot be asserted without evidence bound to an exact identity. A plain
log can be edited after the fact to manufacture that evidence. Each entry here
commits to the digest of the entry before it, so removing, reordering, or
editing any historical entry invalidates every entry after it, and
``verify()`` reports the exact sequence number where the chain broke.

The genesis entry commits to ``GENESIS_PREV``, a fixed constant, so an attacker
cannot truncate the chain to a shorter valid prefix and pass verification.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from .errors import LedgerIntegrityError
from .util import (
    actor_id,
    append_line,
    atomic_write,
    canonical_json,
    emit_interface_instance,
    sha256_obj,
    utc_now,
)

GENESIS_PREV = "0" * 64

ACTIONS = {
    "INSTALL",
    "GOAL_SET",
    "WORK_PACKET_CREATED",
    "WORK_PACKET_TRANSITION",
    "DOCUMENT_CREATED",
    "DOCUMENT_STEP_COMPLETED",
    "DOCUMENT_STAMPED",
    "EVIDENCE_RECORDED",
    "GATE_EVALUATED",
    "CHECKPOINT",
    "DECISION_RECORDED",
    "PHASE_TRANSITION",
    "VERIFICATION_RUN",
    "RELEASE_ASSEMBLED",
}

# Fields that participate in the entry digest, in the order they are declared.
# ``entry_sha256`` is excluded because it is the digest itself.
DIGEST_EXCLUDED = {"entry_sha256"}


def _digest_payload(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key not in DIGEST_EXCLUDED}


def compute_entry_hash(entry: dict[str, Any]) -> str:
    return sha256_obj(_digest_payload(entry))


class Ledger:
    """Append-only hash-chained record bound to one project."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.path = self.root / "LEDGER.jsonl"
        self.head_path = self.root / "HEAD"

    # ------------------------------------------------------------------ read

    def exists(self) -> bool:
        return self.path.exists()

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        import json

        out: list[dict[str, Any]] = []
        for number, raw in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                out.append(json.loads(raw))
            except Exception as exc:  # pragma: no cover - defensive
                raise LedgerIntegrityError(f"ledger line {number} is not valid JSON: {exc}") from exc
        return out

    def head(self) -> str:
        records = self.entries()
        return records[-1]["entry_sha256"] if records else GENESIS_PREV

    def next_seq(self) -> int:
        return len(self.entries()) + 1

    def find(self, subject_id: str) -> list[dict[str, Any]]:
        return [item for item in self.entries() if item.get("subject_id") == subject_id]

    def last_for(self, subject_id: str) -> dict[str, Any] | None:
        found = self.find(subject_id)
        return found[-1] if found else None

    # ----------------------------------------------------------------- write

    def append(
        self,
        *,
        action: str,
        subject_type: str,
        subject_id: str,
        actor: str,
        content_sha256: str | None = None,
        state_before: str | None = None,
        state_after: str | None = None,
        authority_ref: str | None = None,
        evidence_ids: list[str] | None = None,
        detail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if action not in ACTIONS:
            raise LedgerIntegrityError(f"unknown ledger action: {action}")
        previous = self.head()
        seq = self.next_seq()
        entry: dict[str, Any] = {
            "schema_version": "1.0.0",
            "seq": seq,
            "entry_id": f"ABS.LEDGER.{seq:06d}",
            "timestamp": utc_now(),
            "actor": actor,
            "action": action,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "content_sha256": content_sha256,
            "state_before": state_before,
            "state_after": state_after,
            "authority_ref": authority_ref,
            "evidence_ids": sorted(evidence_ids or []),
            "detail": detail or {},
            "prev_entry_sha256": previous,
        }
        entry["entry_sha256"] = compute_entry_hash(entry)
        import json

        append_line(self.path, json.dumps(entry, sort_keys=True, ensure_ascii=False))
        atomic_write(self.head_path, entry["entry_sha256"] + "\n")

        # ABS.IFACE.TRUTH.STAMP is declared *provided* by
        # ABS.MODULE.RUNTIME.EXECUTOR. A provided interface that no code path
        # ever emits an instance of is precisely the unbacked claim this
        # framework exists to prevent, so the stamp is emitted here, at the one
        # place stamping happens, and the deep verifier validates every emitted
        # instance against the registry schema.
        emit_interface_instance(
            self.root.parent / "interfaces",
            "truth_stamp",
            {
                "schema_version": "1.0.0",
                "interface_id": "ABS.IFACE.TRUTH.STAMP",
                "request_id": entry["entry_id"],
                "scope_id": f"ABS.SCOPE.TRUTH.{subject_type.upper()}",
                "actor_id": actor_id(actor),
                "authority_ref": authority_ref if authority_ref and authority_ref.startswith("ABS.") else "ABS.AUTHORITY.PROJECT_LEDGER",
                "candidate_hash": f"sha256:{content_sha256}"
                if isinstance(content_sha256, str) and len(content_sha256) == 64
                else "sha256:" + "0" * 64,
                "payload": {"action": action, "subject_id": subject_id, "seq": seq},
                "result_state": "PASS",
                "evidence_ids": sorted(evidence_ids or []),
                "limitations": [
                    "Stamped by the producing runtime; independent reproduction is a separate act."
                ],
                "entry_sha256": entry["entry_sha256"],
                "prev_entry_sha256": previous,
            },
        )
        return entry

    # ---------------------------------------------------------------- verify

    def verify(self) -> dict[str, Any]:
        """Recompute the whole chain from raw bytes.

        Returns a structured result rather than raising, because the deep
        verifier needs to report *where* a chain broke, not merely that it did.
        """
        records = self.entries()
        problems: list[dict[str, Any]] = []
        previous = GENESIS_PREV
        for index, entry in enumerate(records):
            seq = entry.get("seq")
            if seq != index + 1:
                problems.append({"seq": seq, "problem": "SEQUENCE_GAP", "expected": index + 1})
            if entry.get("prev_entry_sha256") != previous:
                problems.append(
                    {
                        "seq": seq,
                        "problem": "CHAIN_BREAK",
                        "expected_prev": previous,
                        "observed_prev": entry.get("prev_entry_sha256"),
                    }
                )
            recomputed = compute_entry_hash(entry)
            if recomputed != entry.get("entry_sha256"):
                problems.append(
                    {
                        "seq": seq,
                        "problem": "ENTRY_TAMPERED",
                        "expected_hash": recomputed,
                        "observed_hash": entry.get("entry_sha256"),
                    }
                )
            if entry.get("action") not in ACTIONS:
                problems.append({"seq": seq, "problem": "UNKNOWN_ACTION", "action": entry.get("action")})
            previous = entry.get("entry_sha256")

        head_file = None
        if self.head_path.exists():
            head_file = self.head_path.read_text(encoding="utf-8").strip()
            if head_file != previous:
                problems.append({"problem": "HEAD_MISMATCH", "head_file": head_file, "chain_head": previous})
        elif records:
            problems.append({"problem": "HEAD_MISSING"})

        return {
            "status": "PASS" if not problems else "FAIL",
            "entry_count": len(records),
            "chain_head": previous,
            "head_file": head_file,
            "problems": problems,
        }

    def subjects_for(self, action: str) -> list[str]:
        """Every subject id the chain records for one action, oldest first."""
        return [item.get("subject_id") for item in self.entries() if item.get("action") == action]

    # --------------------------------------------------------------- anchors

    def anchor(self, actor: str, note: str = "") -> dict[str, Any]:
        """Write a detached receipt committing to the current chain state.

        A local hash chain proves that no *individual* historical entry was
        edited, because editing one breaks every digest after it. It cannot by
        itself detect an attacker who rewrites the entire chain from genesis.
        An anchor is the countermeasure: a small receipt naming the head digest
        and entry count at a point in time, intended to be stored somewhere the
        chain's holder does not solely control (a commit, a signed tag, a second
        machine). ``verify_anchors`` then requires the chain to still contain
        every anchored prefix, so a full rewrite is detected as soon as one
        anchor survives.
        """
        records = self.entries()
        receipt = {
            "schema_version": "1.0.0",
            "anchor_id": f"ABS.ANCHOR.{len(records):06d}",
            "timestamp": utc_now(),
            "actor": actor,
            "entry_count": len(records),
            "chain_head": self.head(),
            "note": note,
        }
        receipt["anchor_sha256"] = sha256_obj(receipt)
        target = self.root / "anchors" / f"{receipt['anchor_id']}.json"
        atomic_write(target, canonical_json(receipt))
        return receipt

    def anchors(self) -> list[dict[str, Any]]:
        directory = self.root / "anchors"
        if not directory.is_dir():
            return []
        import json

        out = []
        for path in sorted(directory.glob("*.json")):
            out.append(json.loads(path.read_text(encoding="utf-8")))
        return sorted(out, key=lambda item: item.get("entry_count", 0))

    def verify_anchors(self) -> dict[str, Any]:
        """Check every stored anchor against the live chain."""
        records = self.entries()
        problems: list[dict[str, Any]] = []
        checked = 0
        for receipt in self.anchors():
            expected = {key: value for key, value in receipt.items() if key != "anchor_sha256"}
            if sha256_obj(expected) != receipt.get("anchor_sha256"):
                problems.append({"anchor_id": receipt.get("anchor_id"), "problem": "ANCHOR_TAMPERED"})
                continue
            count = receipt.get("entry_count", 0)
            if count > len(records):
                problems.append(
                    {
                        "anchor_id": receipt.get("anchor_id"),
                        "problem": "CHAIN_TRUNCATED",
                        "anchored_entry_count": count,
                        "observed_entry_count": len(records),
                    }
                )
                continue
            observed_head = records[count - 1]["entry_sha256"] if count else GENESIS_PREV
            if observed_head != receipt.get("chain_head"):
                problems.append(
                    {
                        "anchor_id": receipt.get("anchor_id"),
                        "problem": "CHAIN_REWRITTEN",
                        "anchored_head": receipt.get("chain_head"),
                        "observed_head": observed_head,
                    }
                )
                continue
            checked += 1
        return {
            "status": "PASS" if not problems else "FAIL",
            "anchors_checked": checked,
            "problems": problems,
        }
