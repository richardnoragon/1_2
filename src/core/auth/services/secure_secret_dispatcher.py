"""Deliver temporary reset secrets via approved channels."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet  # type: ignore[import]

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.models.reset_request import ResetChannel, ResetRequest
from src.core.auth.repositories.reset_request_repository import (
    ResetRequestRepository,
)
from src.core.auth.services.audit_logger import AuditLogger
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.SecureSecretDispatcher")


@dataclass(slots=True)
class SecretDispatchOutcome:
    """Description of how a temporary secret was delivered."""

    request_id: str
    username: str
    channel: str
    revealed: bool
    temporary_secret: str | None = None
    note_path: str | None = None
    note_key: str | None = None


class SecretDispatcherError(RuntimeError):
    """Base error for dispatcher failures."""


class SecretConfirmationRequiredError(SecretDispatcherError):
    """Raised when console delivery is attempted without confirmation."""


class SecretAlreadyDeliveredError(SecretDispatcherError):
    """Raised when a reset request has already been fulfilled."""


class SecretExpiredError(SecretDispatcherError):
    """Raised when a reset request is past its expiration timestamp."""


class SecretUnavailableError(SecretDispatcherError):
    """Raised when no temporary secret is available for delivery."""


class SecureSecretDispatcher:
    """Encapsulate approved secret delivery mechanisms."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        reset_repo: ResetRequestRepository | None = None,
        audit_logger: AuditLogger | None = None,
        output_dir: str | Path | None = None,
        origin_surface: str = "cli",
    ) -> None:
        db_path = Path(database_path) if database_path else None
        self._reset_repo = reset_repo or ResetRequestRepository(database_path=db_path)
        self._audit_logger = audit_logger or AuditLogger(
            database_path=db_path,
            default_surface=origin_surface,
        )
        directory = Path(output_dir) if output_dir else Path.cwd() / "secure_resets"
        directory.mkdir(parents=True, exist_ok=True)
        self._output_dir = directory
        self._origin_surface = origin_surface

    # ------------------------------------------------------------------
    def dispatch(
        self,
        *,
        request_id: str,
        confirm_display: bool = False,
        actor_username: str | None = None,
        note_directory: str | Path | None = None,
    ) -> SecretDispatchOutcome:
        request = self._require_request(request_id)
        self._ensure_request_open(request)
        plaintext = self._extract_secret(request)
        if request.dispatcher_channel == ResetChannel.SECURE_NOTE:
            return self._deliver_secure_note(
                request,
                plaintext,
                actor_username=actor_username,
                note_directory=note_directory,
            )
        return self._deliver_console(
            request,
            plaintext,
            confirm_display=confirm_display,
            actor_username=actor_username,
        )

    # ------------------------------------------------------------------
    def _require_request(self, request_id: str) -> ResetRequest:
        request = self._reset_repo.get(request_id)
        if request is None:
            raise SecretDispatcherError(f"Reset request {request_id!r} not found")
        return request

    def _ensure_request_open(self, request: ResetRequest) -> None:
        if request.has_expired():
            request.mark_expired()
            self._reset_repo.create(request)
            raise SecretExpiredError("Reset request has expired")
        if request.secret_displayed_at is not None:
            raise SecretAlreadyDeliveredError(
                "Temporary secret for this request has already been delivered"
            )
        if not request.secret_available():
            raise SecretUnavailableError(
                "Temporary secret is no longer available for delivery"
            )

    def _extract_secret(self, request: ResetRequest) -> str:
        blob = request.temporary_secret
        if blob is None:
            raise SecretUnavailableError(
                "Temporary secret is missing for this reset request"
            )
        if isinstance(blob, memoryview):
            blob = blob.tobytes()
        return blob.decode("utf-8")

    def _finalize_delivery(self, request: ResetRequest) -> datetime:
        timestamp = datetime.now(timezone.utc)
        request.mark_secret_delivered(timestamp=timestamp)
        request.clear_secret()
        self._reset_repo.create(request)
        return timestamp

    def _log_dispatch(
        self,
        request: ResetRequest,
        *,
        actor_username: str | None,
        note_path: Path | None = None,
    ) -> None:
        actor = actor_username or request.initiated_by
        details = {
            "dispatcher_event": True,
            "dispatcher_channel": request.dispatcher_channel.value,
            "request_id": request.request_id,
        }
        if note_path is not None:
            details["note_path"] = str(note_path)
        self._audit_logger.record_action(
            action_type=AdminActionType.RESET_PASSWORD,
            actor_username=actor,
            target_username=request.user_id,
            details=details,
            origin_surface=self._origin_surface,
            correlation_id=request.request_id,
        )

    def _deliver_console(
        self,
        request: ResetRequest,
        plaintext: str,
        *,
        confirm_display: bool,
        actor_username: str | None,
    ) -> SecretDispatchOutcome:
        if not confirm_display:
            raise SecretConfirmationRequiredError(
                ("Explicit confirmation is required to display the " "temporary secret")
            )
        self._finalize_delivery(request)
        self._log_dispatch(request, actor_username=actor_username)
        LOGGER.warning(
            "Temporary secret delivered via console for %s (request=%s)",
            request.user_id,
            request.request_id,
        )
        return SecretDispatchOutcome(
            request_id=request.request_id,
            username=request.user_id,
            channel=request.dispatcher_channel.value,
            revealed=True,
            temporary_secret=plaintext,
        )

    def _deliver_secure_note(
        self,
        request: ResetRequest,
        plaintext: str,
        *,
        actor_username: str | None,
        note_directory: str | Path | None,
    ) -> SecretDispatchOutcome:
        target_dir = Path(note_directory) if note_directory else self._output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc)
        file_name = (
            f"rfu_reset_secret_{request.user_id}_"
            f"{timestamp.strftime('%Y%m%d%H%M%S')}"
            ".secure-note"
        )
        note_path = target_dir / file_name
        key = Fernet.generate_key()
        cipher = Fernet(key)
        ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
        payload = {
            "rfu_secure_note": 1,
            "username": request.user_id,
            "generated_at": timestamp.isoformat().replace("+00:00", "Z"),
            "expires_at": request.expires_at.isoformat(),
            "ciphertext": ciphertext.decode("utf-8"),
        }
        note_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._finalize_delivery(request)
        self._log_dispatch(
            request,
            actor_username=actor_username,
            note_path=note_path,
        )
        LOGGER.info(
            "Temporary secret exported to secure note for %s at %s",
            request.user_id,
            note_path,
        )
        return SecretDispatchOutcome(
            request_id=request.request_id,
            username=request.user_id,
            channel=request.dispatcher_channel.value,
            revealed=True,
            note_path=str(note_path),
            note_key=key.decode("utf-8"),
        )


__all__ = [
    "SecretDispatchOutcome",
    "SecretDispatcherError",
    "SecretConfirmationRequiredError",
    "SecretAlreadyDeliveredError",
    "SecretExpiredError",
    "SecretUnavailableError",
    "SecureSecretDispatcher",
]
