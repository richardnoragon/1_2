"""Administrative CLI helpers for RFU identity workflows.

The integration tests exercise these callables directly instead of
shelling out so test environments can provision pending users,
approve them, and reset passwords without invoking subprocesses.
A thin argparse wrapper is provided for manual use but remains
secondary to the Python-level API.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from scripts.admin.cli_types import CommandResult
from src.core.auth.endpoints.mfa_placeholder_controller import (
    MFAFeatureUnavailableError,
    MFAPlaceholderController,
)
from src.core.auth.models import (
    AccountStatus,
    RegistrationChannel,
    UserAccount,
    UserRole,
)
from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.policies import InputValidator
from src.core.auth.repositories.user_account_repository import (
    UserAccountRepository,
)
from src.core.auth.security import PasswordHasher
from src.core.auth.services.admin_account_service import AdminAccountService
from src.core.auth.services.admin_approval_service import AdminApprovalService
from src.core.auth.services.audit_logger import AuditLogger
from src.core.auth.services.factory import build_auth_service
from src.core.auth.services.secure_secret_dispatcher import (
    SecretDispatcherError,
    SecureSecretDispatcher,
)
from src.core.auth.watchdogs.idle_timeout_watcher import enforce_idle_timeouts
from src.core.preferences.services.share_service import ShareService

ISO_UTC_SUFFIX = "+00:00"
ISO_Z_SUFFIX = "Z"
ACTOR_USERNAME = "rfu-admin"
ORIGIN_SURFACE = "cli"
ALLOWED_DELIVERIES = frozenset({"console", "cli", "secure_note"})
DELIVERY_CHOICES = tuple(sorted(ALLOWED_DELIVERIES))
AUDIT_EXPORT_DEFAULT_DAYS = 30
AUDIT_EXPORT_DEFAULT_LIMIT = 1000
MFA_EXIT_NOT_IMPLEMENTED = 3
SECURE_NOTE_DIRNAME = "secure_resets"
_CREDENTIAL_VALIDATOR = InputValidator()


def _ensure_actor_account(
    *,
    database_path: str | Path,
    username: str = ACTOR_USERNAME,
) -> UserAccount:
    repo = UserAccountRepository(database_path=Path(database_path))
    account = repo.get(username)
    if account:
        return account

    hasher = PasswordHasher()
    temp_password = PasswordHasher.generate_temporary_password(length=18)
    password_hash, password_salt = hasher.hash_with_salt(temp_password)
    now = datetime.now(timezone.utc)
    fallback_metadata = {
        "provisioned_by": "rfu-admin-cli",
        "generated_at": now.isoformat().replace(ISO_UTC_SUFFIX, ISO_Z_SUFFIX),
    }
    seeded_account = UserAccount(
        username=username,
        password_hash=password_hash,
        password_salt=password_salt,
        role=UserRole.ADMIN,
        account_status=AccountStatus.ACTIVE,
        registration_channel=RegistrationChannel.BOOTSTRAP,
        registration_metadata=fallback_metadata,
        created_at=now,
        activated_at=now,
        updated_at=now,
        reset_required=True,
    )
    repo.upsert(seeded_account)
    return seeded_account


def _build_approval_service(database_path: str | Path) -> AdminApprovalService:
    return AdminApprovalService(
        database_path=database_path,
        origin_surface=ORIGIN_SURFACE,
        default_actor=ACTOR_USERNAME,
    )


def _build_account_service(database_path: str | Path) -> AdminAccountService:
    return AdminAccountService(
        database_path=database_path,
        origin_surface=ORIGIN_SURFACE,
        default_actor=ACTOR_USERNAME,
    )


def _build_audit_logger(database_path: str | Path) -> AuditLogger:
    return AuditLogger(
        database_path=database_path,
        default_surface=ORIGIN_SURFACE,
    )


def _build_secret_dispatcher(
    database_path: str | Path,
) -> SecureSecretDispatcher:
    output_dir = Path(database_path).parent / SECURE_NOTE_DIRNAME
    return SecureSecretDispatcher(
        database_path=database_path,
        origin_surface=ORIGIN_SURFACE,
        output_dir=output_dir,
    )


def _actor_has_admin_role(
    database_path: str | Path,
    actor_username: str | None,
) -> bool:
    if not actor_username:
        return False
    repo = UserAccountRepository(database_path=Path(database_path))
    account = repo.get(actor_username)
    if account is None:
        return False
    role_value = getattr(account, "role", None)
    return str(role_value).lower() == "admin"


def _log_unauthorized_attempt(
    *,
    database_path: str | Path,
    actor_username: str | None,
    target_username: str | None,
    attempted_action: str,
    metadata: dict | None = None,
) -> None:
    if not _actor_has_admin_role(database_path, actor_username):
        # Even if the actor is not an admin we still log once the user exists.
        repo = UserAccountRepository(database_path=Path(database_path))
        if actor_username and repo.get(actor_username) is None:
            return
    if not actor_username:
        return
    logger = _build_audit_logger(database_path)
    details = {"attempted_action": attempted_action}
    if metadata:
        details.update(metadata)
    logger.record_action(
        action_type=AdminActionType.UNAUTHORIZED_ADMIN_ACTION,
        actor_username=actor_username,
        target_username=target_username,
        details=details,
    )


def _require_admin_actor(
    *,
    database_path: str | Path,
    actor_username: str | None,
    target_username: str | None,
    attempted_action: str,
    metadata: dict | None = None,
) -> str:
    candidate = actor_username or ACTOR_USERNAME
    if _actor_has_admin_role(database_path, candidate):
        return candidate
    _log_unauthorized_attempt(
        database_path=database_path,
        actor_username=actor_username,
        target_username=target_username,
        attempted_action=attempted_action,
        metadata=metadata,
    )
    raise PermissionError("Administrator role required")


def _fetch_audit_entries(
    *,
    database_path: str | Path,
    days: int,
    limit: int,
    actor_username: str | None,
    target_username: str | None,
) -> list[dict]:
    window_days = max(1, int(days))
    since_ts = datetime.now(timezone.utc) - timedelta(days=window_days)
    since_ts = since_ts.replace(microsecond=0)
    limit_value = max(1, min(int(limit), 5000))
    clauses = ["created_at >= :since"]
    params: dict[str, object] = {
        "since": since_ts.isoformat().replace(ISO_UTC_SUFFIX, ISO_Z_SUFFIX),
        "limit": limit_value,
    }
    if actor_username:
        clauses.append("actor_username = :actor")
        params["actor"] = actor_username
    if target_username:
        clauses.append("target_username = :target")
        params["target"] = target_username
    where_clause = " AND ".join(clauses)
    sql = textwrap.dedent(
        f"""
        SELECT audit_id,
               actor_username,
               target_username,
               action_type,
               origin_surface,
               details,
               created_at
        FROM admin_action_audit
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit
        """
    ).strip()
    db_path = Path(database_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Identity database not found at {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    entries: list[dict] = []
    for row in rows or []:
        details_text = row["details"] or "{}"
        try:
            details_payload = json.loads(details_text)
        except json.JSONDecodeError:
            details_payload = {"raw": details_text}
        entries.append(
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
    return entries


def login_cli(
    *,
    database_path: str | Path,
    username: str,
    password: str,
) -> CommandResult:
    """Authenticate a user via the CLI entrypoint with FR-011 validation."""

    sanitized_username, normalized_password = (
        _CREDENTIAL_VALIDATOR.validate_credentials(
            username,
            password,
        )
    )
    auth_service = build_auth_service(
        database_path=database_path,
        validator=_CREDENTIAL_VALIDATOR,
    )
    session = auth_service.authenticate(
        sanitized_username,
        normalized_password,
    )
    payload = {
        "username": session.username,
        "role": session.role,
        "preferences_user_id": session.preferences_user_id,
        "reset_required": session.reset_required,
    }
    return CommandResult(exit_code=0, payload=payload)


def approve_user_cli(
    *,
    database_path: str | Path,
    username: str,
    role: str,
    preferences_template: str = "default",
    actor_username: str | None = None,
) -> CommandResult:
    acting_username = actor_username
    if acting_username is None:
        acting_username = _ensure_actor_account(database_path=database_path).username
    service = _build_approval_service(database_path)
    try:
        payload = service.approve_user(
            username=username,
            role=role,
            preferences_template=preferences_template,
            actor_username=acting_username,
        )
        return CommandResult(exit_code=0, payload=payload)
    except PermissionError as exc:
        _log_unauthorized_attempt(
            database_path=database_path,
            actor_username=acting_username,
            target_username=username,
            attempted_action="approve_user",
            metadata={"role": role, "template": preferences_template},
        )
        return CommandResult(exit_code=1, error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))


def reset_password_cli(
    *,
    database_path: str | Path,
    username: str,
    delivery: str,
    justification: str,
    actor_username: str | None = None,
    confirm_display: bool = False,
) -> CommandResult:
    if delivery not in ALLOWED_DELIVERIES:
        return CommandResult(
            exit_code=1,
            error=f"delivery must be one of {sorted(ALLOWED_DELIVERIES)}",
        )
    if not justification or not justification.strip():
        return CommandResult(exit_code=1, error="justification is required")
    acting_username = actor_username
    actor_is_admin = False
    if acting_username is None:
        acting_username = _ensure_actor_account(database_path=database_path).username
        actor_is_admin = True
    else:
        actor_is_admin = _actor_has_admin_role(database_path, acting_username)

    requires_confirmation = delivery in {"console", "cli"} and not confirm_display
    if requires_confirmation and actor_is_admin:
        return CommandResult(
            exit_code=1,
            error="--confirm-display required for console delivery",
        )
    service = _build_account_service(database_path)
    try:
        result = service.reset_password(
            username=username,
            delivery=delivery,
            justification=justification.strip(),
            actor_username=acting_username,
        )
    except PermissionError as exc:
        _log_unauthorized_attempt(
            database_path=database_path,
            actor_username=acting_username,
            target_username=username,
            attempted_action="reset_password",
            metadata={"delivery": delivery},
        )
        return CommandResult(exit_code=1, error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))

    dispatcher = _build_secret_dispatcher(database_path)
    dispatch = None
    try:
        should_dispatch = delivery == "secure_note" or confirm_display
        if should_dispatch:
            request_id = result.get("reset_request_id")
            if not request_id:
                return CommandResult(
                    exit_code=1,
                    error="reset_request_id missing from admin service",
                )
            dispatch = dispatcher.dispatch(
                request_id=request_id,
                confirm_display=confirm_display or delivery == "secure_note",
                actor_username=acting_username,
                note_directory=Path(database_path).parent / SECURE_NOTE_DIRNAME,
            )
    except SecretDispatcherError as exc:
        return CommandResult(exit_code=1, error=str(exc))

    payload = {
        "username": result.get("username", username),
        "delivery": delivery,
        "enforced_password_change": result.get(
            "enforced_password_change",
            True,
        ),
        "reset_request_id": result.get("reset_request_id"),
        "secret_revealed": bool(dispatch and dispatch.revealed),
    }
    if dispatch and dispatch.temporary_secret:
        payload["temporary_password"] = dispatch.temporary_secret
    if dispatch and dispatch.note_path:
        payload["secret_note_path"] = dispatch.note_path
    if dispatch and dispatch.note_key:
        payload["secret_note_key"] = dispatch.note_key
    return CommandResult(exit_code=0, payload=payload)


def unblock_user_cli(
    *,
    database_path: str | Path,
    username: str,
    justification: str,
    actor_username: str | None = None,
) -> CommandResult:
    justification_value = (justification or "").strip()
    if not justification_value:
        return CommandResult(exit_code=1, error="justification is required")
    acting_username = actor_username
    if acting_username is None:
        acting_username = _ensure_actor_account(database_path=database_path).username
    service = _build_account_service(database_path)
    try:
        payload = service.unblock_user(
            username=username,
            justification=justification_value,
            actor_username=acting_username,
        )
        return CommandResult(exit_code=0, payload=payload)
    except PermissionError as exc:
        _log_unauthorized_attempt(
            database_path=database_path,
            actor_username=acting_username,
            target_username=username,
            attempted_action="unblock_user",
            metadata={"reason": justification_value},
        )
        return CommandResult(exit_code=1, error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))


def audit_export_cli(
    *,
    database_path: str | Path,
    days: int = AUDIT_EXPORT_DEFAULT_DAYS,
    limit: int = AUDIT_EXPORT_DEFAULT_LIMIT,
    target_username: str | None = None,
    actor_username: str | None = None,
    requesting_actor: str | None = None,
    output_path: str | None = None,
) -> CommandResult:
    operator_candidate = requesting_actor
    if operator_candidate is None:
        operator_candidate = _ensure_actor_account(database_path=database_path).username
    try:
        operator = _require_admin_actor(
            database_path=database_path,
            actor_username=operator_candidate,
            target_username=target_username,
            attempted_action="audit_export",
            metadata={"days": days, "limit": limit},
        )
    except PermissionError as exc:
        return CommandResult(exit_code=1, error=str(exc))

    try:
        entries = _fetch_audit_entries(
            database_path=database_path,
            days=days,
            limit=limit,
            actor_username=actor_username,
            target_username=target_username,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))

    payload = {
        "exported_by": operator,
        "count": len(entries),
        "entries": entries,
    }

    if output_path:
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:  # pylint: disable=broad-except
            return CommandResult(
                exit_code=1,
                error=str(exc),
            )  # pragma: no cover - file IO failures

    return CommandResult(exit_code=0, payload=payload)


def mfa_status_cli(
    *,
    database_path: str | Path,
    username: str | None = None,
) -> CommandResult:
    controller = MFAPlaceholderController(db_path=database_path)
    try:
        payload = controller.get_status(username=username)
    except MFAFeatureUnavailableError as exc:
        return CommandResult(
            exit_code=MFA_EXIT_NOT_IMPLEMENTED,
            error=str(exc),
        )
    return CommandResult(exit_code=MFA_EXIT_NOT_IMPLEMENTED, payload=payload)


def mfa_enroll_cli(
    *,
    database_path: str | Path,
    username: str,
    actor_username: str | None = None,
) -> CommandResult:
    operator_candidate = actor_username
    if operator_candidate is None:
        operator_candidate = _ensure_actor_account(database_path=database_path).username
    try:
        operator = _require_admin_actor(
            database_path=database_path,
            actor_username=operator_candidate,
            target_username=username,
            attempted_action="mfa_enroll",
        )
    except PermissionError as exc:
        return CommandResult(exit_code=1, error=str(exc))

    controller = MFAPlaceholderController(db_path=database_path)
    try:
        payload = controller.post_enroll(
            {
                "username": username,
                "token_username": operator,
                "token_role": "admin",
            }
        )
    except MFAFeatureUnavailableError as exc:
        return CommandResult(
            exit_code=MFA_EXIT_NOT_IMPLEMENTED,
            error=str(exc),
        )
    return CommandResult(exit_code=MFA_EXIT_NOT_IMPLEMENTED, payload=payload)


def export_preferences_cli(
    *,
    database_path: str | Path,
    username: str,
    purpose: str,
    actor_username: str | None = None,
) -> CommandResult:
    service = ShareService(
        database_path=Path(database_path),
        origin_surface=ORIGIN_SURFACE,
    )
    try:
        payload = service.export_preferences(
            username=username,
            purpose=purpose,
            actor_username=actor_username,
            additional_actor_candidates=[ACTOR_USERNAME],
        )
        return CommandResult(exit_code=0, payload=payload)
    except PermissionError as exc:
        return CommandResult(exit_code=1, error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))  # pragma: no cover


def run_idle_watchdog_cli(
    *,
    database_path: str | Path,
    idle_minutes: int = 10,
) -> CommandResult:
    db_path = Path(database_path)
    try:
        summary = enforce_idle_timeouts(
            database_path=db_path,
            idle_minutes=int(idle_minutes),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))

    revoked = int(summary.get("revoked_sessions", 0) or 0)
    exit_code = 2 if revoked > 0 else 0
    return CommandResult(exit_code=exit_code, payload=summary)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    approve = sub.add_parser("approve-user", help="Approve a pending user")
    approve.add_argument("--database-path", required=True)
    approve.add_argument("--username", required=True)
    approve.add_argument("--role", default="standard")
    approve.add_argument("--preferences-template", default="default")

    reset = sub.add_parser("reset-password", help="Reset a user's password")
    reset.add_argument("--database-path", required=True)
    reset.add_argument("--username", required=True)
    reset.add_argument("--delivery", choices=DELIVERY_CHOICES, required=True)
    reset.add_argument("--justification", required=True)
    reset.add_argument(
        "--confirm-display",
        action="store_true",
        help="Explicitly allow printing the temporary secret in the console",
    )

    unblock = sub.add_parser(
        "unblock-user",
        help="Clear login attempts and unblock an account",
    )
    unblock.add_argument("--database-path", required=True)
    unblock.add_argument("--username", required=True)
    unblock.add_argument("--justification", required=True)

    audit = sub.add_parser(
        "audit-export",
        help="Export recent admin action audit entries as JSON",
    )
    audit.add_argument("--database-path", required=True)
    audit.add_argument("--days", type=int, default=AUDIT_EXPORT_DEFAULT_DAYS)
    audit.add_argument("--limit", type=int, default=AUDIT_EXPORT_DEFAULT_LIMIT)
    audit.add_argument("--target-username")
    audit.add_argument(
        "--actor-username",
        help="Filter to entries performed by the specified actor",
    )
    audit.add_argument(
        "--requesting-actor",
        help="Operator requesting the export (for role enforcement)",
    )
    audit.add_argument("--output", help="Optional path to write JSON bundle")

    export_cmd = sub.add_parser(
        "export-preferences",
        help="Export sanitized preferences when sharing is enabled",
    )
    export_cmd.add_argument("--database-path", required=True)
    export_cmd.add_argument("--username", required=True)
    export_cmd.add_argument("--purpose", required=True)

    mfa_status = sub.add_parser(
        "mfa-status",
        help="Describe placeholder MFA capabilities",
    )
    mfa_status.add_argument("--database-path", required=True)
    mfa_status.add_argument(
        "--username",
        help="Optional username context for the status call",
    )

    mfa_enroll = sub.add_parser(
        "mfa-enroll",
        help="Placeholder MFA enrollment command (not yet available)",
    )
    mfa_enroll.add_argument("--database-path", required=True)
    mfa_enroll.add_argument("--username", required=True)
    mfa_enroll.add_argument(
        "--actor-username",
        help="Operator requesting enrollment (defaults to rfu-admin)",
    )

    idle = sub.add_parser(
        "idle-watchdog",
        help=(
            "Run idle-timeout enforcement and emit automation-friendly " "exit codes"
        ),
    )
    idle.add_argument("--database-path", required=True)
    idle.add_argument("--idle-minutes", type=int, default=10)

    return parser.parse_args(list(argv) if argv is not None else None)


def _handle_result(result: CommandResult) -> int:
    if result.payload is not None:
        print(json.dumps(result.payload, indent=2))
    if result.error:
        print(result.error, file=sys.stderr)
    return result.exit_code


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "approve-user":
        return _handle_result(
            approve_user_cli(
                database_path=args.database_path,
                username=args.username,
                role=args.role,
                preferences_template=args.preferences_template,
            )
        )
    if args.command == "reset-password":
        return _handle_result(
            reset_password_cli(
                database_path=args.database_path,
                username=args.username,
                delivery=args.delivery,
                justification=args.justification,
                confirm_display=args.confirm_display,
            )
        )
    if args.command == "unblock-user":
        return _handle_result(
            unblock_user_cli(
                database_path=args.database_path,
                username=args.username,
                justification=args.justification,
            )
        )
    if args.command == "audit-export":
        return _handle_result(
            audit_export_cli(
                database_path=args.database_path,
                days=args.days,
                limit=args.limit,
                target_username=args.target_username,
                actor_username=args.actor_username,
                requesting_actor=args.requesting_actor,
                output_path=args.output,
            )
        )
    if args.command == "export-preferences":
        return _handle_result(
            export_preferences_cli(
                database_path=args.database_path,
                username=args.username,
                purpose=args.purpose,
            )
        )
    if args.command == "mfa-status":
        return _handle_result(
            mfa_status_cli(
                database_path=args.database_path,
                username=getattr(args, "username", None),
            )
        )
    if args.command == "mfa-enroll":
        return _handle_result(
            mfa_enroll_cli(
                database_path=args.database_path,
                username=args.username,
                actor_username=getattr(args, "actor_username", None),
            )
        )
    if args.command == "idle-watchdog":
        return _handle_result(
            run_idle_watchdog_cli(
                database_path=args.database_path,
                idle_minutes=args.idle_minutes,
            )
        )
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
