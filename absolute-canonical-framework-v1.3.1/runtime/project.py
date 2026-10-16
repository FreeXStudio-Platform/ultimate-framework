"""Project control namespace: layout, load/save, and rail context derivation.

Everything the runtime knows about a project is reconstructed from files under
``.absolute/``. Nothing is cached across commands, so a stale in-memory belief
can never outlive the bytes on disk — the framework's ``STALE`` failure mode.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import CONTROL_DIR, RUNTIME_VERSION
from .errors import NotInstalledError
from .ledger import Ledger
from .util import atomic_write_json, read_json, sha256_tree

# Directories created at install time. Each one is a durable registry the
# framework requires; creating them eagerly means a later write can never fail
# because a registry was missing.
SUBDIRECTORIES = (
    "truth",
    "truth/anchors",
    "work",
    "evidence",
    "gates",
    "sessions",
    "decisions",
    "documents",
    "reports",
)

IDENTITY_FILE = "identity.json"
STATE_FILE = "state.json"


class Project:
    """A framework-governed project rooted at ``root``."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.control = self.root / CONTROL_DIR

    # ------------------------------------------------------------- discovery

    @classmethod
    def discover(cls, start: Path) -> "Project":
        """Walk upward for a control namespace, like a version-control root."""
        current = Path(start).resolve()
        for candidate in [current, *current.parents]:
            if (candidate / CONTROL_DIR / IDENTITY_FILE).is_file():
                return cls(candidate)
        return cls(current)

    @property
    def installed(self) -> bool:
        return (self.control / IDENTITY_FILE).is_file()

    def require_installed(self) -> None:
        if not self.installed:
            raise NotInstalledError(
                f"no Absolute control namespace at {self.root}. Run 'absolute init' first."
            )

    # ----------------------------------------------------------------- paths

    @property
    def ledger(self) -> Ledger:
        return Ledger(self.control / "truth")

    def path(self, *parts: str) -> Path:
        return self.control.joinpath(*parts)

    # ------------------------------------------------------------- documents

    def identity(self) -> dict[str, Any]:
        self.require_installed()
        return read_json(self.control / IDENTITY_FILE)

    def state(self) -> dict[str, Any]:
        self.require_installed()
        return read_json(self.control / STATE_FILE)

    def save_state(self, state: dict[str, Any]) -> None:
        atomic_write_json(self.control / STATE_FILE, state)

    def _load_dir(self, name: str) -> list[dict[str, Any]]:
        directory = self.path(name)
        if not directory.is_dir():
            return []
        return [read_json(path) for path in sorted(directory.glob("*.json"))]

    def work_packets(self) -> list[dict[str, Any]]:
        return self._load_dir("work")

    def evidence_records(self) -> list[dict[str, Any]]:
        return self._load_dir("evidence")

    def gate_reports(self) -> list[dict[str, Any]]:
        return self._load_dir("gates")

    def checkpoints(self) -> list[dict[str, Any]]:
        return self._load_dir("sessions")

    def decisions(self) -> list[dict[str, Any]]:
        return self._load_dir("decisions")

    def documents(self) -> list[dict[str, Any]]:
        directory = self.path("documents")
        if not directory.is_dir():
            return []
        out = []
        for record in sorted(directory.glob("*/document.json")):
            out.append(read_json(record))
        return out

    def document(self, doc_id: str) -> dict[str, Any] | None:
        record = self.path("documents", doc_id, "document.json")
        return read_json(record) if record.is_file() else None

    # ---------------------------------------------------------- tree identity

    # The identity covers the *work product*, not the control plane's records
    # about it. Evidence, gates, checkpoints, reports, work-packet status, and
    # the ledger are observations; if they were included, recording an
    # observation would change the identity that observation was bound to, and
    # every gate would immediately go stale against its own evidence.
    #
    # This is the same separation the release model already makes when it
    # excludes MANIFEST.json and the release metadata from the candidate-tree
    # digest. Integrity of the excluded records is not lost: each one is
    # hash-stamped individually into the ledger at the moment it is written.
    IDENTITY_INCLUDED_CONTROL_PATHS = (
        f"{CONTROL_DIR}/identity.json",
        f"{CONTROL_DIR}/documents/",
    )

    def _identity_excluded(self, relative: str) -> bool:
        if not relative.startswith(f"{CONTROL_DIR}/"):
            return False  # all project source participates in the identity
        return not any(
            relative == item or relative.startswith(item)
            for item in self.IDENTITY_INCLUDED_CONTROL_PATHS
        )

    def tree_identity(self) -> str:
        """Content identity of the governed work product.

        Includes every project source file plus the frozen project identity and
        every governed document package. Excludes the control plane's process
        records, for the reason given above.
        """
        exclusions = {
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file() and self._identity_excluded(path.relative_to(self.root).as_posix())
        }
        digest, _ = sha256_tree(self.root, exclude=exclusions)
        return digest

    # ---------------------------------------------------------- rail context

    def rail_context(self) -> dict[str, Any]:
        """Derive the rail's view of this project from files only."""
        if not self.installed:
            return {"installed": False}

        state = self.state()
        identity = self.identity()
        tree = self.tree_identity()

        packets = self.work_packets()
        open_packets = [item for item in packets if item.get("status") not in {"COMPLETED", "CANCELLED"}]
        all_docs = self.documents()
        # An abandoned package is a closed decision on record, not outstanding
        # work. Counting it would keep the rail stopped on a document nobody is
        # going to finish, which is the dead end `doc abandon` exists to end.
        abandoned = [item for item in all_docs if item.get("status") == "ABANDONED"]
        docs = [item for item in all_docs if item.get("status") != "ABANDONED"]

        from .documents import DOCUMENT_STEPS  # local import avoids a cycle

        authored = sum(1 for item in docs if len(item.get("completed_steps", [])) == len(DOCUMENT_STEPS))
        sealed = sum(1 for item in docs if item.get("status") == "SEALED")

        gates = self.gate_reports()
        gate_pass = any(
            item.get("decision") == "PASS" and item.get("candidate_hash") == f"sha256:{tree}" for item in gates
        )
        checkpoint_current = any(
            item.get("candidate_hash_after") == f"sha256:{tree}" for item in self.checkpoints()
        )

        return {
            "installed": True,
            "project_id": identity.get("project_id"),
            "active_goal_id": state.get("active_goal_id"),
            "active_work_packet": state.get("active_work_packet"),
            "work_packets_created": len(packets),
            "open_work_packets": len(open_packets),
            "document_count": len(docs),
            "documents_abandoned": len(abandoned),
            "documents_authored": authored,
            "documents_sealed": sealed,
            "evidence_count": len(self.evidence_records()),
            "gate_passed_current_identity": gate_pass,
            "checkpoint_current_identity": checkpoint_current,
            "tree_identity": tree,
            "second_pass_identity": state.get("second_pass_identity"),
            "verified_identity": state.get("verified_identity"),
            "released_identity": state.get("released_identity"),
            "runtime_version": RUNTIME_VERSION,
            "state_drift": self.state_drift(),
        }

    # ---------------------------------------------------------- state drift

    # Artifacts are written before the ledger entry and the ledger entry before
    # the state update, so a process killed mid-operation leaves a durable
    # record while the ordinal counters still point at it. The runtime docstring
    # promises that situation is "visible to absolute status"; this is what
    # makes that true instead of merely stated.
    ORDINAL_REGISTRIES = (
        ("next_work_packet_ordinal", "work"),
        ("next_evidence_ordinal", "evidence"),
        ("next_gate_ordinal", "gates"),
        ("next_session_ordinal", "sessions"),
    )

    def state_drift(self) -> list[dict[str, Any]]:
        """Ordinal counters that lag the records already durable on disk."""
        import re

        drift: list[dict[str, Any]] = []
        try:
            state = self.state()
        except Exception:
            return drift
        for key, directory in self.ORDINAL_REGISTRIES:
            folder = self.path(directory)
            if not folder.is_dir():
                continue
            highest = 0
            for path in folder.glob("*.json"):
                match = re.search(r"(\d+)$", path.stem)
                if match:
                    highest = max(highest, int(match.group(1)))
            counter = int(state.get(key, 1) or 1)
            if highest and counter <= highest:
                drift.append(
                    {
                        "counter": key,
                        "registry": directory,
                        "recorded_next": counter,
                        "highest_on_disk": highest,
                        "meaning": "an operation was recorded but its state update did not land",
                    }
                )
        return drift
