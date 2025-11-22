"""HTTP-style controller for authentication flows used by contract tests."""

from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from src.core.auth.policies import InputValidator
from src.core.auth.services import (
    build_auth_service,
    build_registration_service,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("AuthController")


class AuthController:
    """Provide POST/DELETE `/auth/login` semantics for contract tests."""

    SESSION_DURATION_MINUTES = 60
    IDLE_TIMEOUT_MINUTES = 10

    def __init__(
        self,
        *,
        db_path: str | Path,
        validator: InputValidator | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.validator = validator or InputValidator()

    # ------------------------------------------------------------------
    def post_login(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        username = payload.get("username")
        password = payload.get("password")
        surface = (payload.get("surface") or "gui").lower()
        origin_host = payload.get("origin_host") or "localhost"
        if surface not in {"gui", "cli"}:
            raise ValueError("surface must be either 'gui' or 'cli'")
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("username and password are required")

        auth_service = build_auth_service(
            database_path=self.db_path,
            validator=self.validator,
        )
        session = auth_service.authenticate(
            username,
            password,
            surface=surface,
        )

        issued_at = self._utc_now()
        expires_at = issued_at + timedelta(minutes=self.SESSION_DURATION_MINUTES)
        idle_deadline = issued_at + timedelta(minutes=self.IDLE_TIMEOUT_MINUTES)
        session_id = secrets.token_hex(24)

        self._persist_session(
            session_id=session_id,
            username=session.username,
            surface=surface,
            origin_host=origin_host,
            preferences_id=session.preferences_user_id,
            issued_at=issued_at,
            expires_at=expires_at,
            idle_deadline=idle_deadline,
        )

        LOGGER.info(
            "User %s authenticated via %s surface",
            session.username,
            surface,
        )
        return {
            "username": session.username,
            "role": session.role,
            "preferences_id": session.preferences_user_id,
            "session_id": session_id,
            "expires_at": self._response_isoformat(expires_at),
        }

    def post_register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        username = payload.get("username")
        password = payload.get("password")
        surface = (payload.get("surface") or "gui").lower()
        metadata = payload.get("metadata")
        if surface not in {"gui", "cli", "hub"}:
            raise ValueError("surface must be one of gui, cli, or hub")
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("username and password are required")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be an object when provided")

        registration_service = build_registration_service(
            database_path=self.db_path,
            validator=self.validator,
            origin_surface="service",
        )
        result = registration_service.register_user(
            username=username,
            password=password,
            channel=surface,
            metadata=metadata,
        )
        LOGGER.info(
            "Queued self-registration for %s via %s surface",
            result["username"],
            surface,
        )
        return result

    def delete_login(self, session_id: str) -> None:
        if not session_id:
            raise ValueError("session_id is required for logout")

        with self._connect() as conn:
            row = conn.execute(
                ("SELECT revoked FROM session_tokens " "WHERE session_handle_hash=?"),
                (session_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Session token not found")
            if row["revoked"]:
                raise PermissionError("Session already revoked")

            now_iso = self._isoformat(self._utc_now())
            conn.execute(
                """
                UPDATE session_tokens
                SET revoked = 1,
                    revoked_at = ?
                WHERE session_handle_hash = ?
                """,
                (now_iso, session_id),
            )
            conn.commit()
        LOGGER.info("Session %s revoked", session_id)
        return None

    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise FileNotFoundError(f"Identity database not found at {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(microsecond=0)

    @staticmethod
    def _isoformat(value: datetime) -> str:
        utc_value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return utc_value.isoformat(timespec="seconds")

    @staticmethod
    def _response_isoformat(value: datetime) -> str:
        return value.astimezone(timezone.utc).replace(tzinfo=None).isoformat()

    def _persist_session(
        self,
        *,
        session_id: str,
        username: str,
        surface: str,
        origin_host: str,
        preferences_id: str | None,
        issued_at: datetime,
        expires_at: datetime,
        idle_deadline: datetime,
    ) -> None:
        issued_iso = self._isoformat(issued_at)
        expires_iso = self._isoformat(expires_at)
        idle_iso = self._isoformat(idle_deadline)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_tokens (
                    session_handle_hash,
                    user_id,
                    issued_at,
                    last_activity_at,
                    expires_at,
                    surface,
                    origin_host,
                    revoked,
                    revoked_at,
                    preferences_id,
                    idle_timeout_deadline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?)
                """,
                (
                    session_id,
                    username,
                    issued_iso,
                    issued_iso,
                    expires_iso,
                    surface,
                    origin_host,
                    preferences_id,
                    idle_iso,
                ),
            )
            conn.commit()


__all__ = ["AuthController"]
