"""Factory helpers for constructing AuthService instances."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from src.core.auth.auth_service import AuthService
from src.core.auth.policies import InputValidator, LockoutPolicy
from src.core.auth.security import PasswordHasher
from src.core.auth.services.audit_logger import AuditLogger
from src.core.auth.services.pending_registration_dispatcher import (
    PendingRegistrationDispatcher,
)
from src.core.auth.services.registration_service import (
    NotificationHook,
    RegistrationService,
)
from src.core.auth.user_store import UserStore


def build_auth_service(
    *,
    database_path: str | Path,
    validator: Optional[InputValidator] = None,
) -> AuthService:
    """Return an AuthService wired to the provided SQLite database."""

    db_path = Path(database_path)
    store = UserStore(database_path=db_path)
    password_hasher = PasswordHasher()
    lockout_policy = LockoutPolicy(max_attempts=AuthService.MAX_LOGIN_ATTEMPTS)
    return AuthService(
        store=store,
        password_hasher=password_hasher,
        input_validator=validator or InputValidator(),
        lockout_policy=lockout_policy,
    )


def build_registration_service(
    *,
    database_path: str | Path,
    origin_surface: str = "service",
    validator: Optional[InputValidator] = None,
    notification_hooks: Iterable[NotificationHook] | None = None,
    include_pending_dispatcher: bool = True,
) -> RegistrationService:
    """Return a registration service wired to the provided SQLite database."""

    db_path = Path(database_path)
    audit_logger = AuditLogger(
        database_path=db_path,
        default_surface=origin_surface,
    )
    hooks: list[NotificationHook] = []
    if include_pending_dispatcher:
        dispatcher = PendingRegistrationDispatcher(
            database_path=db_path,
            audit_logger=audit_logger,
        )
        hooks.append(dispatcher)
    if notification_hooks:
        hooks.extend(notification_hooks)
    return RegistrationService(
        database_path=db_path,
        validator=validator or InputValidator(),
        origin_surface=origin_surface,
        notification_hooks=hooks,
        audit_logger=audit_logger,
    )


__all__ = ["build_auth_service", "build_registration_service"]
