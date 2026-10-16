"""Absolute Framework runtime.

The runtime is the executable enforcement of the framework operating loop. It is
the only supported way to install the framework into a project, author governed
documents, record evidence, evaluate gates, and stamp artifacts into the
project's append-only source of truth.

Design invariants:
  * No command may run out of rail order (see ``runtime.rail``).
  * Every state transition is written to the hash-chained ledger before the
    on-disk state is updated, so a crash can never produce an unrecorded change.
  * Nothing in the runtime may emit a certification claim; certification is an
    external act (see ``runtime.errors.SelfCertificationError``).
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

__all__ = ["RUNTIME_VERSION", "CONTROL_DIR"]

RUNTIME_VERSION = "1.0.0"
CONTROL_DIR = ".absolute"
