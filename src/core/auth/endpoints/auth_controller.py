"""HTTP-style controller for authentication flows used by contract tests.

Task T065: Extended to support break-glass login with:
- Break-glass account detection
- Justification requirement
- RFU_ENABLE_BREAK_GLASS environment variable check
- session_type and usage_log_id in response
"""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.auth.policies import InputValidator
from src.core.auth.services import (
    build_auth_service,
    build_registration_service,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("AuthController")

# Environment variable to enable break-glass access
BREAK_GLASS_ENV_VAR = "RFU_ENABLE_BREAK_GLASS"
MIN_JUSTIFICATION_LENGTH = 10


class AuthController:
    """Provide POST/DELETE `/auth/login` semantics for contract tests.

    Extended (T065) to support break-glass login:
    - Detects break-glass accounts via is_break_glass flag
    - Requires justification for break-glass logins
    - Checks RFU_ENABLE_BREAK_GLASS environment variable
    - Returns session_type and usage_log_id for break-glass sessions
    """

    SESSION_DURATION_MINUTES = 60
    IDLE_TIMEOUT_MINUTES = 10
    BREAK_GLASS_SESSION_DURATION_MINUTES = 60

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
        """Handle login request.

        For break-glass accounts:
        - Requires 'justification' in payload
        - Requires RFU_ENABLE_BREAK_GLASS=true or enable_break_glass=True
        - Returns session_type='break_glass' and usage_log_id
        """
        username = payload.get("username")
        password = payload.get("password")
        surface = (payload.get("surface") or "gui").lower()
        origin_host = payload.get("origin_host") or "localhost"
        justification = payload.get("justification")
        enable_flag = payload.get("enable_break_glass", False)

        if surface not in {"gui", "cli"}:
            raise ValueError("surface must be either 'gui' or 'cli'")
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("username and password are required")

        # Check if account is break-glass before authentication
        is_break_glass = self._is_break_glass_account(username)

        if is_break_glass:
            return self._handle_break_glass_login(
                username=username,
                password=password,
                surface=surface,
                origin_host=origin_host,
                justification=justification,
                enable_flag=enable_flag,
            )

        # Standard login flow
        return self._handle_standard_login(
            username=username,
            password=password,
            surface=surface,
            origin_host=origin_host,
        )

    def post_break_glass_login(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dedicated break-glass login endpoint.

        Required payload:
        - username: break-glass account username
        - password: account password
        - justification: reason for break-glass access (min 10 chars)
        - enable_break_glass: True or RFU_ENABLE_BREAK_GLASS env var

        Returns session with session_type='break_glass' and usage_log_id.
        """
        username = payload.get("username")
        password = payload.get("password")
        justification = payload.get("justification")
        surface = (payload.get("surface") or "cli").lower()
        origin_host = payload.get("origin_host") or "localhost"
        enable_flag = payload.get("enable_break_glass", False)

        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("username and password are required")

        # Verify this is a break-glass account
        if not self._is_break_glass_account(username):
            raise PermissionError("not a break-glass account")

        return self._handle_break_glass_login(
            username=username,
            password=password,
            surface=surface,
            origin_host=origin_host,
            justification=justification,
            enable_flag=enable_flag,
        )

    def _handle_break_glass_login(
        self,
        *,
        username: str,
        password: str,
        surface: str,
        origin_host: str,
        justification: Optional[str],
        enable_flag: bool,
    ) -> Dict[str, Any]:
        """Handle break-glass login with validation."""
        # Check enablement
        if not self._is_break_glass_enabled(enable_flag):
            raise PermissionError("break-glass access not enabled")

        # Validate justification
        if not justification:
            raise ValueError("justification required")
        if len(justification.strip()) < MIN_JUSTIFICATION_LENGTH:
            raise ValueError(
                f"justification must be at least "
                f"{MIN_JUSTIFICATION_LENGTH} characters"
            )

        # Authenticate
        auth_service = build_auth_service(
            database_path=self.db_path,
            validator=self.validator,
        )
        session = auth_service.authenticate(
            username,
            password,
            surface=surface,
        )

        # Create session
        issued_at = self._utc_now()
        duration = self.BREAK_GLASS_SESSION_DURATION_MINUTES
        expires_at = issued_at + timedelta(minutes=duration)
        idle_deadline = issued_at + timedelta(minutes=self.IDLE_TIMEOUT_MINUTES)
        session_id = secrets.token_hex(24)

        # Create break-glass usage log
        usage_log_id = self._create_break_glass_usage_log(
            session_id=session_id,
            username=username,
            justification=justification.strip(),
            origin_host=origin_host,
        )

        # Persist session with break-glass type
        self._persist_session(
            session_id=session_id,
            username=session.username,
            surface=surface,
            origin_host=origin_host,
            preferences_id=session.preferences_user_id,
            issued_at=issued_at,
            expires_at=expires_at,
            idle_deadline=idle_deadline,
            session_type="break_glass",
            usage_log_id=usage_log_id,
        )

        LOGGER.warning(
            "Break-glass login: user=%s, justification=%s",
            session.username,
            justification[:50],
        )

        return {
            "username": session.username,
            "role": session.role,
            "preferences_id": session.preferences_user_id,
            "session_id": session_id,
            "expires_at": self._response_isoformat(expires_at),
            "session_type": "break_glass",
            "usage_log_id": usage_log_id,
        }

    def _handle_standard_login(
        self,
        *,
        username: str,
        password: str,
        surface: str,
        origin_host: str,
    ) -> Dict[str, Any]:
        """Handle standard (non-break-glass) login."""
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
        duration = self.SESSION_DURATION_MINUTES
        expires_at = issued_at + timedelta(minutes=duration)
        idle_mins = self.IDLE_TIMEOUT_MINUTES
        idle_deadline = issued_at + timedelta(minutes=idle_mins)
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
            session_type="normal",
            usage_log_id=None,
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
            "session_type": "normal",
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

    def delete_login(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Handle logout request.

        For break-glass sessions, returns rotation requirements.
        """
        if not session_id:
            raise ValueError("session_id is required for logout")

        with self._connect() as conn:
            row = conn.execute(
                "SELECT revoked, session_type, usage_log_id "
                "FROM session_tokens WHERE session_handle_hash=?",
                (session_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Session token not found")
            if row["revoked"]:
                raise PermissionError("Session already revoked")

            session_type = row["session_type"] or "normal"
            usage_log_id = row["usage_log_id"]

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

            # Update break-glass usage log if applicable
            result = None
            if session_type == "break_glass" and usage_log_id:
                conn.execute(
                    """
                    UPDATE break_glass_usage_log
                    SET logout_timestamp = ?,
                        post_usage_rotation_status = 'pending'
                    WHERE id = ?
                    """,
                    (now_iso, usage_log_id),
                )
                result = {
                    "session_type": "break_glass",
                    "usage_log_id": usage_log_id,
                    "rotation_required": True,
                }

            conn.commit()

        LOGGER.info("Session %s revoked", session_id)
        return result

    # ------------------------------------------------------------------
    def _is_break_glass_account(self, username: str) -> bool:
        """Check if an account is a break-glass account."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT is_break_glass FROM user_accounts " "WHERE username = ?",
                    (username,),
                ).fetchone()
                if row is None:
                    return False
                return bool(row["is_break_glass"])
        except Exception:
            return False

    def _is_break_glass_enabled(self, enable_flag: bool = False) -> bool:
        """Check if break-glass access is enabled."""
        if enable_flag:
            return True
        env_value = os.environ.get(BREAK_GLASS_ENV_VAR, "").lower()
        return env_value in ("true", "1", "yes")

    def _create_break_glass_usage_log(
        self,
        *,
        session_id: str,
        username: str,
        justification: str,
        origin_host: str,
    ) -> int:
        """Create a break-glass usage log entry."""
        now_iso = self._isoformat(self._utc_now())
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO break_glass_usage_log (
                    session_id,
                    account_username,
                    login_timestamp,
                    justification,
                    actions_performed,
                    post_usage_rotation_status,
                    client_ip,
                    client_hostname,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    username,
                    now_iso,
                    justification,
                    json.dumps([]),
                    "not_required",
                    "127.0.0.1",
                    origin_host,
                    now_iso,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            msg = f"Identity database not found at {self.db_path}"
            raise FileNotFoundError(msg)
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
        session_type: str = "normal",
        usage_log_id: Optional[int] = None,
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
                    idle_timeout_deadline,
                    session_type,
                    usage_log_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, ?, ?)
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
                    session_type,
                    usage_log_id,
                ),
            )
            conn.commit()


__all__ = ["AuthController"]
