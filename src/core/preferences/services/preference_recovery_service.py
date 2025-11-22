"""Preference recovery helpers for missing or corrupt payloads."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, Mapping

try:  # pragma: no cover - fallback when executed outside package context
    from src.log_manager import get_log_manager
except ImportError:  # pragma: no cover
    from log_manager import get_log_manager  # type: ignore

from src.core.auth.models import UserAccount
from src.core.auth.models.admin_action_audit import AdminActionType
from src.core.auth.policies import InputValidator
from src.core.auth.repositories.user_account_repository import (
    UserAccountRepository,
)
from src.core.auth.services.audit_logger import AuditLogger
from src.core.preferences.models import (
    PreferenceProfile,
    PreferenceSchemaVersion,
)
from src.core.preferences.models.pending_preference_alert import (
    AlertResolutionState,
    AlertSeverity,
    PendingPreferenceAlert,
)
from src.core.preferences.repositories import (
    pending_preference_alert_repository as pending_alert_repo,
)
from src.core.preferences.repositories import (
    preference_profile_repository as profile_repo,
)

LOGGER = get_log_manager().get_logger("Preferences.RecoveryService")

PendingPreferenceAlertRepository = pending_alert_repo.PendingPreferenceAlertRepository
PreferenceProfileRepository = profile_repo.PreferenceProfileRepository

NotificationHook = Callable[
    [PendingPreferenceAlert, Mapping[str, object]],
    None,
]

_DEFAULT_TEMPLATE_PAYLOAD: Dict[str, object] = {
    "layout": "default",
    "favorite_tools": ["file_finder", "size_analyzer"],
    "shortcuts": ["Ctrl+Shift+F"],
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RecoveryResult:
    username: str
    preferences_id: str
    alert_id: str
    created_profile: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "username": self.username,
            "preferences_id": self.preferences_id,
            "alert_id": self.alert_id,
            "created_profile": self.created_profile,
            "reason": self.reason,
        }


class PreferenceRecoveryService:
    """Bootstrap defaults and raise alerts when corruption occurs."""

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        user_repo: UserAccountRepository | None = None,
        preference_repo: PreferenceProfileRepository | None = None,
        alert_repo: PendingPreferenceAlertRepository | None = None,
        audit_logger: AuditLogger | None = None,
        validator: InputValidator | None = None,
        origin_surface: str = "service",
        default_actor: str = "system",
        default_template: Mapping[str, object] | None = None,
        notification_hooks: Iterable[NotificationHook] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        db_path = Path(database_path) if database_path else None
        self._user_repo = user_repo or UserAccountRepository(database_path=db_path)
        self._pref_repo = preference_repo or PreferenceProfileRepository(
            database_path=db_path
        )
        self._alert_repo = alert_repo or PendingPreferenceAlertRepository(
            database_path=db_path
        )
        self._audit_logger = audit_logger or AuditLogger(
            database_path=db_path,
            default_surface=origin_surface,
        )
        self._validator = validator or InputValidator()
        self._origin_surface = origin_surface
        self._default_actor = default_actor
        self._default_template = dict(default_template or _DEFAULT_TEMPLATE_PAYLOAD)
        self._notification_hooks: tuple[NotificationHook, ...] = tuple(
            notification_hooks or ()
        )
        self._clock = clock or _utcnow

    # ------------------------------------------------------------------
    def recover_preferences(
        self,
        username: str,
        *,
        reason: str = "missing_preferences",
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        actor_username: str | None = None,
        notes: str | None = None,
        metadata: Mapping[str, object] | None = None,
        template_payload: Mapping[str, object] | None = None,
    ) -> Dict[str, object]:
        sanitized_username = self._validator.validate_username(username)
        actor = actor_username or self._default_actor
        account = self._require_account(sanitized_username)
        preferences_id = account.preferences_id or self._generate_preferences_id(
            sanitized_username
        )
        template = dict(template_payload or self._default_template)
        created_profile = False
        timestamp = self._clock()

        profile = self._pref_repo.get(preferences_id)
        if profile is None:
            profile = PreferenceProfile(
                preferences_id=preferences_id,
                user_id=sanitized_username,
                schema_version=PreferenceSchemaVersion.V1,
                payload=template,
                created_at=timestamp,
            )
            created_profile = True
        else:
            profile.update_payload(updates=template, replace=True)
        profile = self._pref_repo.save(profile)

        if account.preferences_id != preferences_id:
            account.preferences_id = preferences_id
            account.updated_at = timestamp
            self._user_repo.upsert(account)

        alert_metadata = self._build_alert_metadata(
            reason=reason,
            preferences_id=preferences_id,
            created_profile=created_profile,
            extra=metadata,
        )
        alert = PendingPreferenceAlert(
            alert_id=self._generate_alert_id(),
            user_id=sanitized_username,
            detected_at=timestamp,
            severity=severity,
            resolution_state=AlertResolutionState.OPEN,
            notes=notes or reason,
            preference_snapshot_version=int(profile.schema_version),
            metadata=alert_metadata,
        )
        self._alert_repo.create(alert)
        self._notify(alert, actor=actor)

        self._audit_logger.record_action(
            action_type=AdminActionType.PREFERENCE_RECOVERY,
            actor_username=actor,
            target_username=sanitized_username,
            details={
                "reason": reason,
                "preferences_id": preferences_id,
                "alert_id": alert.alert_id,
                "created_profile": created_profile,
            },
            origin_surface=self._origin_surface,
            metadata={"severity": severity.value},
            correlation_id=alert.alert_id,
        )
        LOGGER.warning(
            "Preference recovery executed for %s (reason=%s, alert=%s)",
            sanitized_username,
            reason,
            alert.alert_id,
        )
        return RecoveryResult(
            username=sanitized_username,
            preferences_id=preferences_id,
            alert_id=alert.alert_id,
            created_profile=created_profile,
            reason=reason,
        ).to_dict()

    # ------------------------------------------------------------------
    def _require_account(self, username: str) -> UserAccount:
        account = self._user_repo.get(username)
        if account is None:
            raise ValueError(f"User '{username}' not found")
        return account

    @staticmethod
    def _generate_preferences_id(username: str) -> str:
        return f"pref_{username}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _generate_alert_id() -> str:
        return f"pref_alert_{uuid.uuid4().hex}"

    def _build_alert_metadata(
        self,
        *,
        reason: str,
        preferences_id: str,
        created_profile: bool,
        extra: Mapping[str, object] | None = None,
    ) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "reason": reason,
            "preferences_id": preferences_id,
            "created_profile": created_profile,
        }
        if extra:
            payload.update(dict(extra))
        return payload

    def _notify(self, alert: PendingPreferenceAlert, *, actor: str) -> None:
        if not self._notification_hooks:
            return
        context: Mapping[str, object] = {
            "actor": actor,
            "origin_surface": self._origin_surface,
        }
        for hook in self._notification_hooks:
            try:
                hook(alert, context)
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Preference recovery hook failed: %s", exc)


__all__ = ["PreferenceRecoveryService", "RecoveryResult", "NotificationHook"]
