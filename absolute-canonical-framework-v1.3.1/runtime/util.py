"""Deterministic primitives shared by every runtime component.

Canonical JSON is the single serialization used for hashing anywhere in the
runtime. Two artifacts with the same meaning must produce the same bytes, or the
ledger chain and the stamp identities would not be reproducible.
"""
from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ID_PATTERN = re.compile(r"^ABS\.[A-Z0-9_.-]+$")
SHA256_FIELD = re.compile(r"^sha256:[0-9a-f]{64}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")


def utc_now() -> str:
    """RFC3339 UTC timestamp with second precision.

    Second precision is deliberate: it keeps ledger entries stable when the same
    logical action is replayed inside one second during tests, and it is the
    precision the framework schemas declare.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_obj(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path, exclude: set[str] | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Hash a directory with the framework's canonical path-size-content algorithm.

    Identical to ``release_integrity.candidate_tree_records`` so that a stamped
    project tree and a stamped release tree are comparable identities.
    """
    exclude = exclude or set()
    digest = hashlib.sha256()
    records: list[dict[str, Any]] = []
    paths = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(root).as_posix().casefold(),
    )
    for path in paths:
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        file_hash = sha256_path(path)
        size = path.stat().st_size
        records.append({"path": rel, "bytes": size, "sha256": file_hash})
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), records


def atomic_write(path: Path, text: str) -> None:
    """Write via a same-directory temp file and ``os.replace``.

    A half-written control file would leave the project in a state the rail
    cannot classify, so no control-plane write is ever done in place.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp", delete=False
    )
    try:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    os.replace(handle.name, path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(path, canonical_json(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_line(path: Path, line: str) -> None:
    """Append one durable line. Used only by the ledger.

    Callers must already hold the project lock (:func:`exclusive_lock`). Append
    mode alone is not sufficient: the ledger's ``prev_entry_sha256`` is computed
    from a prior read, so two processes can each read the same head and each
    append a valid-looking line, forking the chain at one sequence number.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip("\n") + "\n")
        handle.flush()
        os.fsync(handle.fileno())


LOCK_FILE = ".lock"

# flock is granted per open file description, so a second acquire from the same
# process on a fresh descriptor would wait on a lock this process already holds
# and never return. Governed operations are not nested today; this makes that
# assumption safe to break later rather than a latent deadlock.
_HELD: set[str] = set()


@contextmanager
def exclusive_lock(directory: Path, timeout: float = 30.0) -> Iterator[Path]:
    """Serialize every mutating operation on one project control namespace.

    Every governed mutation is a read-modify-write across several files: the
    ledger head, the sequence number, the ordinal counters in ``state.json``,
    and the artifact itself. Without a lock two concurrent ``absolute``
    processes each read the same head and the same ordinal, then each write —
    producing duplicate sequence numbers, a permanently broken chain, and one
    artifact silently overwriting the other. Detecting that afterwards is not
    enough, because the overwritten record is gone.

    ``flock`` is advisory and per-open-file-description, so it serializes
    processes on one host and is released automatically if a process dies. It
    does not coordinate across machines sharing a network filesystem; that
    limitation is stated in ``LIMITATIONS.md``.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / LOCK_FILE
    key = str(target.resolve())
    if key in _HELD:
        yield target
        return
    handle = os.open(str(target), os.O_RDWR | os.O_CREAT, 0o644)
    waited = 0.0
    try:
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                if waited >= timeout:
                    raise TimeoutError(
                        f"another absolute process has held the project lock at {target} for "
                        f"{timeout:.0f}s; refusing rather than racing it"
                    ) from exc
                import time

                time.sleep(0.05)
                waited += 0.05
        _HELD.add(key)
        yield target
    finally:
        _HELD.discard(key)
        try:
            fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)


def normalize_actor(value: str) -> str:
    """Fold an actor name to the identity used for authority comparisons.

    Author/reviewer separation is the point of the two-pass control. Comparing
    raw strings makes it defeatable by typing the same name differently —
    ``alice`` authoring and ``Alice`` reviewing passed a check whose entire
    purpose is to stop exactly that. Case, surrounding whitespace, internal
    whitespace runs, and ``-``/``_``/``.`` separators are all folded.

    This does not solve identity; a determined operator can still invent a
    second name. It removes the accidental and the trivially deliberate bypass,
    which is what a name-based control can honestly promise.
    """
    folded = re.sub(r"[\s_.-]+", " ", str(value or "")).strip().casefold()
    return folded


def actor_id(actor: str) -> str:
    """The registry-shaped identifier for an actor name."""
    safe = re.sub(r"[^A-Z0-9_]+", "_", normalize_actor(actor).upper()).strip("_")
    return f"ABS.ACTOR.{safe or 'UNKNOWN'}"


def emit_interface_instance(directory: Path, name: str, instance: Any) -> None:
    """Append one instance of a declared interface to its evidence stream.

    Written under the control plane, which is excluded from the project's work
    identity, so recording that an interface was honoured cannot change the
    identity the record is about.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    append_line(
        directory / f"{name}.jsonl",
        json.dumps(instance, sort_keys=True, ensure_ascii=False),
    )


def valid_id(value: str) -> bool:
    return bool(isinstance(value, str) and ID_PATTERN.match(value))


def slug_to_namespace(slug: str) -> str:
    return slug.upper().replace("-", "_")
