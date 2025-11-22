"""Shared admin workflows for identity approvals, resets, and auditing.

These helpers centralize the SQLite logic that both the CLI and GUI/HTTP
layers rely on to enforce FR-010 role requirements while keeping database
writes consistent.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
import string
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from argon2.low_level import Type, hash_secret

from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.services.audit_logger import AuditLogger
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.AdminActions")

DEFAULT_RESET_DELIVERY_CHANNELS = frozenset({"console", "secure_note", "cli"})
_ARGON2_SETTINGS = {
    "time_cost": 3,
    "memory_cost": 64 * 1024,
    "parallelism": 4,
    "hash_len": 32,
    "salt_len": 16,
}


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _utc_from_now(minutes: int) -> str:
    future = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return future.replace(microsecond=0).isoformat().replace("+00:00", "Z")


class AdminIdentityActions:
    """Encapsulate identity admin workflows backed by SQLite."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        origin_surface: str = "cli",
        default_actor: str = "rfu-admin",
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self.origin_surface = origin_surface
        self.default_actor = default_actor
        self._audit_logger = audit_logger or AuditLogger(
            database_path=self.database_path,
            default_surface=self.origin_surface,
        )

    # ------------------------------------------------------------------
    # Connection + lookup helpers
    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Identity database not found at {self.database_path}"
            )
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _fetch_user(
        self,
        conn: sqlite3.Connection,
        username: str,
    ) -> sqlite3.Row:
        row = conn.execute(
            """
            SELECT username,
                   role,
                   account_status,
                   preferences_id,
                   share_preferences,
                   is_blocked,
                   login_attempts,
                   blocked_at,
                   updated_at
            FROM user_accounts
            WHERE username = ?
            LIMIT 1
            """,
            (username,),
        ).fetchone()
        if row is None:
            raise ValueError(f"User {username!r} does not exist in user_accounts")
        return row

    def _store_preferences(
        self,
        conn: sqlite3.Connection,
        *,
        username: str,
        template_name: str,
        preferences_id: str | None = None,
    ) -> str:
        pref_id = preferences_id or f"pref_{uuid.uuid4().hex[:8]}"
        now = _utc_now_iso()
        payload = {
            "template": template_name,
            "layout": "default",
            "favorite_tools": ["file_finder", "size_analyzer"],
        }
        conn.execute(
            """
            INSERT OR REPLACE INTO user_preferences (
                preferences_id,
                user_id,
                schema_version,
                payload,
                is_encrypted,
                metadata,
                shared_metadata,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pref_id,
                username,
                1,
                json.dumps(payload, sort_keys=True),
                0,
                json.dumps({"generated_at": now}, sort_keys=True),
                None,
                now,
                now,
            ),
        )
        return pref_id

    def _resolve_actor(
        self,
        conn: sqlite3.Connection,
        *,
        target_username: str,
        override: str | None,
    ) -> str:
        candidates: Iterable[str | None] = (
            override,
            self.default_actor,
            target_username,
        )
        for candidate in candidates:
            if not candidate:
                continue
            row = conn.execute(
                "SELECT 1 FROM user_accounts WHERE username = ? LIMIT 1",
                (candidate,),
            ).fetchone()
            if row:
                return candidate
        return target_username

    def _generate_temp_password(self, length: int = 14) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^*-_"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _hash_password(self, plaintext: str) -> tuple[str, bytes]:
        if not plaintext:
            raise ValueError("Temporary password must be non-empty")
        salt_bytes = secrets.token_bytes(_ARGON2_SETTINGS["salt_len"])
        hashed = hash_secret(
            plaintext.encode("utf-8"),
            salt_bytes,
            time_cost=_ARGON2_SETTINGS["time_cost"],
            memory_cost=_ARGON2_SETTINGS["memory_cost"],
            parallelism=_ARGON2_SETTINGS["parallelism"],
            hash_len=_ARGON2_SETTINGS["hash_len"],
            type=Type.ID,
        )
        return hashed.decode("utf-8"), salt_bytes

    def _insert_reset_request(
        self,
        conn: sqlite3.Connection,
        *,
        username: str,
        actor_username: str,
        delivery: str,
        justification: str,
        temporary_secret: bytes,
        secret_nonce: bytes,
    ) -> str:
        created_at = _utc_now_iso()
        expires_at = _utc_from_now(30)
        request_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO reset_requests (
                request_id,
                user_id,
                initiated_by,
                reason,
                origin_surface,
                dispatcher_channel,
                status,
                temporary_secret,
                secret_nonce,
                secret_displayed_at,
                expires_at,
                created_at,
                justification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                username,
                actor_username,
                justification,
                self.origin_surface,
                delivery,
                "pending",
                temporary_secret,
                secret_nonce,
                None,
                expires_at,
                created_at,
                justification,
            ),
        )
        return request_id

    def _revoke_sessions(
        self,
        conn: sqlite3.Connection,
        *,
        username: str,
        revoked_at: str,
    ) -> None:
        conn.execute(
            """
            UPDATE session_tokens
            SET revoked = 1,
                revoked_at = ?
            WHERE user_id = ? AND revoked = 0
            """,
            (revoked_at, username),
        )

    def _normalize_justification(self, justification: str | None) -> str:
        value = (justification or "").strip()
        if not value:
            raise ValueError("justification is required")
        return value

    # ------------------------------------------------------------------
    # Role helpers
    # ------------------------------------------------------------------
    def actor_has_admin_role(self, actor_username: str | None) -> bool:
        if not actor_username:
            return False
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role FROM user_accounts WHERE username = ? LIMIT 1",
                (actor_username,),
            ).fetchone()
            return bool(row and str(row["role"]).lower() == "admin")

    def log_unauthorized_attempt(
        self,
        *,
        actor_username: str | None,
        target_username: str | None,
        attempted_action: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if not actor_username:
            return
        with self._connect() as conn:
            actor_row = conn.execute(
                """
                SELECT username
                FROM user_accounts
                WHERE username = ?
                LIMIT 1
                """,
                (actor_username,),
            ).fetchone()
            if not actor_row:
                return
        details = {
            "attempted_action": attempted_action,
        }
        if metadata:
            details.update(metadata)
        self._record_audit_action(
            actor_username=actor_username,
            target_username=target_username,
            action_type=AdminActionType.UNAUTHORIZED_ADMIN_ACTION,
            details=details,
        )
        LOGGER.warning(
            ("Unauthorized admin action blocked " "(actor=%s, target=%s, action=%s)"),
            actor_username,
            target_username,
            attempted_action,
        )

    # ------------------------------------------------------------------
    # Public workflows
    # ------------------------------------------------------------------
    def approve_user(
        self,
        *,
        username: str,
        role: str = "standard",
        preferences_template: str = "default",
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        actor: str
        with self._connect() as conn:
            user_row = self._fetch_user(conn, username)
            pref_id = self._store_preferences(
                conn,
                username=username,
                template_name=preferences_template,
                preferences_id=user_row["preferences_id"],
            )
            now = _utc_now_iso()
            conn.execute(
                """
                UPDATE user_accounts
                SET account_status = 'active',
                    role = ?,
                    preferences_id = ?,
                    activated_at = COALESCE(activated_at, ?),
                    updated_at = ?,
                    is_blocked = 0,
                    login_attempts = 0
                WHERE username = ?
                """,
                (
                    role,
                    pref_id,
                    now,
                    now,
                    username,
                ),
            )
            actor = self._resolve_actor(
                conn,
                target_username=username,
                override=actor_username,
            )
            conn.commit()
        self._record_audit_action(
            actor_username=actor,
            target_username=username,
            action_type=AdminActionType.APPROVE_USER,
            details={
                "role": role,
                "preferences_template": preferences_template,
            },
        )
        LOGGER.info(
            "User %s activated via admin workflow (role=%s, actor=%s)",
            username,
            role,
            actor,
        )
        return {
            "username": username,
            "role": role,
            "preferences_id": pref_id,
            "account_status": "active",
            "preferences_template": preferences_template,
        }

    def reset_password(
        self,
        *,
        username: str,
        delivery: str,
        justification: str,
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        if delivery not in DEFAULT_RESET_DELIVERY_CHANNELS:
            raise ValueError(
                (
                    "delivery must be one of "
                    f"{sorted(DEFAULT_RESET_DELIVERY_CHANNELS)}"
                )
            )
        justification_value = (justification or "").strip()
        if not justification_value:
            raise ValueError("justification is required")
        actor: str
        with self._connect() as conn:
            self._fetch_user(conn, username)
            temp_password = self._generate_temp_password()
            password_hash, password_salt = self._hash_password(temp_password)
            now = _utc_now_iso()
            conn.execute(
                """
                UPDATE user_accounts
                SET password_hash = ?,
                    password_salt = ?,
                    enforced_password_change = 1,
                    account_status = CASE
                        WHEN account_status = 'pending' THEN 'active'
                        ELSE account_status
                    END,
                    is_blocked = 0,
                    login_attempts = 0,
                    updated_at = ?
                WHERE username = ?
                """,
                (
                    password_hash,
                    sqlite3.Binary(password_salt),
                    now,
                    username,
                ),
            )
            self._revoke_sessions(conn, username=username, revoked_at=now)
            actor = self._resolve_actor(
                conn,
                target_username=username,
                override=actor_username,
            )
            request_id = self._insert_reset_request(
                conn,
                username=username,
                actor_username=actor,
                delivery=delivery,
                justification=justification_value,
                temporary_secret=temp_password.encode("utf-8"),
                secret_nonce=secrets.token_bytes(16),
            )
            conn.execute(
                """
                UPDATE reset_requests
                SET status = 'delivered',
                    secret_displayed_at = ?
                WHERE request_id = ?
                """,
                (now, request_id),
            )
            conn.commit()
        self._record_audit_action(
            actor_username=actor,
            target_username=username,
            action_type=AdminActionType.RESET_PASSWORD,
            details={
                "delivery": delivery,
                "justification": justification_value,
            },
        )
        LOGGER.warning(
            "Password for %s reset via %s (actor=%s)",
            username,
            delivery,
            actor,
        )
        return {
            "username": username,
            "delivery": delivery,
            "enforced_password_change": True,
            "reset_request_id": request_id,
            "temporary_password": temp_password,
        }

    def unblock_user(
        self,
        *,
        username: str,
        justification: str,
        actor_username: str | None = None,
    ) -> Dict[str, Any]:
        justification_value = self._normalize_justification(justification)
        actor: str
        with self._connect() as conn:
            user_row = self._fetch_user(conn, username)
            previous_status = user_row["account_status"]
            previous_attempts = user_row["login_attempts"]
            was_blocked = bool(user_row["is_blocked"])
            now = _utc_now_iso()
            conn.execute(
                """
                UPDATE user_accounts
                SET is_blocked = 0,
                    login_attempts = 0,
                    account_status = CASE
                        WHEN account_status = 'disabled' THEN account_status
                        ELSE 'active'
                    END,
                    blocked_at = NULL,
                    updated_at = ?
                WHERE username = ?
                """,
                (now, username),
            )
            self._revoke_sessions(conn, username=username, revoked_at=now)
            actor = self._resolve_actor(
                conn,
                target_username=username,
                override=actor_username,
            )
            conn.commit()
        self._record_audit_action(
            actor_username=actor,
            target_username=username,
            action_type=AdminActionType.UNBLOCK_USER,
            details={
                "justification": justification_value,
                "previous_status": previous_status,
                "previous_attempts": previous_attempts,
                "was_blocked": was_blocked,
            },
        )
        LOGGER.info(
            "User %s unblocked via admin workflow (actor=%s)",
            username,
            actor,
        )
        return {
            "username": username,
            "account_status": "active",
            "justification": justification_value,
            "login_attempts": 0,
        }

    def list_pending_users(self, *, limit: int = 25) -> List[Dict[str, Any]]:
        pending_limit = max(1, int(limit))
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT username,
                       role,
                       created_at,
                       registration_channel
                FROM user_accounts
                WHERE account_status = 'pending'
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (pending_limit,),
            ).fetchall()
        return [
            {
                "username": row["username"],
                "role": row["role"],
                "created_at": row["created_at"],
                "registration_channel": row["registration_channel"],
            }
            for row in rows
        ]

    def export_audit_entries(
        self,
        *,
        days: int = 30,
        limit: int = 500,
        actor_username: str | None = None,
        target_username: str | None = None,
    ) -> List[Dict[str, Any]]:
        window_days = max(1, int(days))
        since_timestamp = (
            datetime.now(timezone.utc) - timedelta(days=window_days)
        ).replace(microsecond=0)
        limit_value = max(1, min(int(limit), 5000))
        query = [
            """
            SELECT audit_id,
                   actor_username,
                   target_username,
                   action_type,
                   origin_surface,
                   details,
                   created_at
            FROM admin_action_audit
            WHERE created_at >= ?
            """
        ]
        params: List[Any] = [since_timestamp.isoformat()]
        if actor_username:
            query.append("AND actor_username = ?")
            params.append(actor_username)
        if target_username:
            query.append("AND target_username = ?")
            params.append(target_username)
        query.append("ORDER BY created_at DESC LIMIT ?")
        params.append(limit_value)

        with self._connect() as conn:
            rows = conn.execute("\n".join(query), params).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            details_text = row["details"] or "{}"
            try:
                details_payload = json.loads(details_text)
            except json.JSONDecodeError:
                details_payload = {"raw": details_text}
            results.append(
                {
                    "audit_id": row["audit_id"],
                    "actor_username": row["actor_username"],
                    "target_username": row["target_username"],
                    "action_type": row["action_type"],
                    "origin_surface": row["origin_surface"],
                    "details": details_payload,
                    "created_at": row["created_at"],
                }
            )
        return results

    def _record_audit_action(
        self,
        *,
        actor_username: str,
        target_username: str | None,
        action_type: AdminActionType,
        details: Dict[str, Any],
    ) -> None:
        correlation_id = self._build_correlation_id(
            action_type=action_type,
            target_username=target_username,
        )
        self._audit_logger.record_action(
            action_type=action_type,
            actor_username=actor_username,
            target_username=target_username,
            details=details,
            origin_surface=self.origin_surface,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _build_correlation_id(
        *,
        action_type: AdminActionType,
        target_username: str | None,
    ) -> str:
        token = uuid.uuid4().hex[:10]
        if target_username:
            safe_target = target_username.replace(" ", "-")
            return f"admin-action-{action_type.value}-{safe_target}-{token}"
        return f"admin-action-{action_type.value}-{token}"


__all__ = ["AdminIdentityActions", "DEFAULT_RESET_DELIVERY_CHANNELS"]
