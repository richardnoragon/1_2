"""Placeholder MFA hook service for FR-013 scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence

try:  # pragma: no cover - imported lazily for direct execution scenarios
    from src.log_manager import get_log_manager
except ImportError:  # pragma: no cover - fallback for script execution
    from log_manager import get_log_manager  # type: ignore


@dataclass(frozen=True)
class MFAFeatureUnavailableError(RuntimeError):
    """Exception raised while MFA remains disabled."""

    operation: str | None = None
    status_code: int = 501

    def __str__(self) -> str:  # pragma: no cover - trivial
        message = (
            "Multi-factor authentication is not yet available. "
            "See specs/006-baseline-login-password/mfa-readiness.md for the rollout plan."
        )
        if self.operation:
            return f"{message} (operation={self.operation})"
        return message


class MFAHookService:
    """No-op MFA hook that documents future integration points."""

    def __init__(self, *, db_path: str | None = None) -> None:
        self.db_path = db_path
        self._logger = get_log_manager().get_logger("Auth.MFAHookService")

    # ------------------------------------------------------------------
    def describe_capabilities(self) -> Dict[str, Any]:
        self._raise_unavailable("describe_capabilities")

    def enroll_user(
        self, username: str, metadata: Mapping[str, Any] | None = None
    ) -> Dict[str, Any]:
        metadata_keys = sorted(metadata.keys()) if metadata else []
        self._raise_unavailable(
            "enroll_user",
            username=username,
            metadata_keys=metadata_keys,
        )

    def verify_challenge(self, username: str, token: str) -> bool:
        self._raise_unavailable(
            "verify_challenge",
            username=username,
            token_provided=bool(token),
        )

    def disable_mfa(
        self, username: str, justification: str | None = None
    ) -> Dict[str, Any]:
        self._raise_unavailable(
            "disable_mfa",
            username=username,
            justification_provided=bool(justification),
        )

    def issue_recovery_codes(self, username: str, *, count: int = 10) -> Sequence[str]:
        self._raise_unavailable(
            "issue_recovery_codes",
            username=username,
            count=count,
        )

    def import_secrets(self, username: str, payload: Mapping[str, Any]) -> None:
        self._raise_unavailable(
            "import_secrets",
            username=username,
            payload_keys=sorted(payload.keys()),
        )

    def export_audit_snapshot(self, usernames: Iterable[str]) -> Dict[str, Any]:
        total = len(list(usernames))
        self._raise_unavailable("export_audit_snapshot", user_count=total)

    # ------------------------------------------------------------------
    def _raise_unavailable(self, operation: str, **context: Any) -> None:
        if context:
            self._logger.warning(
                "MFA placeholder invoked: %s context=%s",
                operation,
                context,
            )
        else:
            self._logger.warning("MFA placeholder invoked: %s", operation)
        raise MFAFeatureUnavailableError(operation=operation)


__all__ = ["MFAHookService", "MFAFeatureUnavailableError"]
