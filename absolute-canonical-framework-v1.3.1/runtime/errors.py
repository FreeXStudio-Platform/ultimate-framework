"""Typed runtime failures.

Every failure mode the runtime can produce has a distinct class so that callers,
tests, and the deep verifier can assert on cause rather than on message text.
``ABS.REQ.RUNTIME_EXECUTION.002`` requires that a refusal always names the rule
that refused and the action that is actually permitted.
"""
from __future__ import annotations


class AbsoluteError(Exception):
    """Base class for every runtime failure."""

    exit_code = 1
    code = "ABS.ERR.GENERIC"


class NotInstalledError(AbsoluteError):
    code = "ABS.ERR.NOT_INSTALLED"


class AlreadyInstalledError(AbsoluteError):
    code = "ABS.ERR.ALREADY_INSTALLED"


class RailViolationError(AbsoluteError):
    """Raised when a command is attempted out of the enforced order."""

    code = "ABS.ERR.RAIL_VIOLATION"
    exit_code = 3

    def __init__(self, attempted: str, required: str, reason: str) -> None:
        super().__init__(
            f"rail violation: '{attempted}' is not permitted now. "
            f"Required next action: '{required}'. Reason: {reason}"
        )
        self.attempted = attempted
        self.required = required
        self.reason = reason


class LedgerIntegrityError(AbsoluteError):
    code = "ABS.ERR.LEDGER_INTEGRITY"
    exit_code = 4


class GoalLockError(AbsoluteError):
    """Work that does not link upward to the approved mission."""

    code = "ABS.ERR.GOAL_LOCK"
    exit_code = 5


class AuthorityError(AbsoluteError):
    code = "ABS.ERR.AUTHORITY"
    exit_code = 6


class SchemaError(AbsoluteError):
    code = "ABS.ERR.SCHEMA"
    exit_code = 7


class DocumentStepError(AbsoluteError):
    code = "ABS.ERR.DOCUMENT_STEP"
    exit_code = 8


class SelfCertificationError(AbsoluteError):
    """The runtime refuses to emit a certification claim about itself."""

    code = "ABS.ERR.SELF_CERTIFICATION"
    exit_code = 9


class EvidenceError(AbsoluteError):
    code = "ABS.ERR.EVIDENCE"
    exit_code = 10
