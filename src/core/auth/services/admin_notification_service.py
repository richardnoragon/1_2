"""Admin notification service for security alerts and break-glass events.

This service handles the creation and delivery of notifications to
administrators for security-sensitive events such as:
- Break-glass login usage
- Lockout alerts
- Credential rotation requirements
- Security incidents
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from src.core.auth.models.admin_notification import (
    AdminNotification,
    NotificationType,
)
from src.core.auth.repositories.admin_notification_repository import (
    AdminNotificationRepository,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("Auth.AdminNotification")

# Default notification expiry in days
DEFAULT_EXPIRY_DAYS = 30
# Break-glass notifications have longer retention
BREAK_GLASS_EXPIRY_DAYS = 90


@dataclass(slots=True)
class NotificationResult:
    """Result of a notification operation."""

    success: bool
    notification_id: int | None = None
    message: str = ""

    @classmethod
    def sent(cls, notification_id: int) -> "NotificationResult":
        """Create a successful result."""
        return cls(
            success=True,
            notification_id=notification_id,
            message="Notification sent",
        )

    @classmethod
    def failed(cls, message: str) -> "NotificationResult":
        """Create a failure result."""
        return cls(success=False, message=message)


class AdminNotificationService:
    """Service for sending and managing administrator notifications.

    This service provides high-level operations for creating and
    managing notifications to administrators about security events.
    """

    def __init__(
        self,
        *,
        database_path: str | Path | None = None,
        repository: AdminNotificationRepository | None = None,
        default_expiry_days: int = DEFAULT_EXPIRY_DAYS,
    ) -> None:
        self._repository = repository or AdminNotificationRepository(
            database_path=database_path
        )
        self._default_expiry_days = default_expiry_days

    # ------------------------------------------------------------------
    # Break-glass notifications
    # ------------------------------------------------------------------
    def notify_break_glass_usage(
        self,
        *,
        username: str,
        justification: str,
        session_id: str,
        source_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> NotificationResult:
        """Send notification about break-glass account usage.

        This should be called immediately when a break-glass login
        is initiated to alert all administrators.
        """
        subject = f"ALERT: Break-glass login by {username}"
        body = (
            f"Break-glass account '{username}' was accessed.\n\n"
            f"Justification: {justification}\n"
            f"Session ID: {session_id}\n"
        )
        if source_ip:
            body += f"Source IP: {source_ip}\n"

        metadata = {
            "username": username,
            "justification": justification,
            "session_id": session_id,
            "source_ip": source_ip,
        }
        if correlation_id:
            metadata["correlation_id"] = correlation_id

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=BREAK_GLASS_EXPIRY_DAYS
        )

        notification = AdminNotification(
            notification_type=NotificationType.BREAK_GLASS_USAGE,
            subject=subject,
            body=body,
            metadata=metadata,
            expires_at=expires_at,
        )

        try:
            saved = self._repository.create(notification)
            LOGGER.warning(
                "Break-glass usage notification sent: %s (id=%s)",
                username,
                saved.notification_id,
            )
            return NotificationResult.sent(saved.notification_id or 0)
        except Exception as e:
            LOGGER.error("Failed to send break-glass notification: %s", e)
            return NotificationResult.failed(str(e))

    def notify_break_glass_session_ended(
        self,
        *,
        username: str,
        session_id: str,
        duration_minutes: int,
        rotation_required: bool,
        correlation_id: str | None = None,
    ) -> NotificationResult:
        """Send notification when break-glass session ends.

        Notifies administrators that the session is complete and
        whether credential rotation is required.
        """
        subject = f"Break-glass session ended: {username}"
        body = (
            f"Break-glass session for '{username}' has ended.\n\n"
            f"Session ID: {session_id}\n"
            f"Duration: {duration_minutes} minutes\n"
            f"Credential rotation: "
            f"{'Required' if rotation_required else 'Not required'}\n"
        )

        metadata = {
            "username": username,
            "session_id": session_id,
            "duration_minutes": duration_minutes,
            "rotation_required": rotation_required,
        }
        if correlation_id:
            metadata["correlation_id"] = correlation_id

        notification = AdminNotification(
            notification_type=NotificationType.BREAK_GLASS_USAGE,
            subject=subject,
            body=body,
            metadata=metadata,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=BREAK_GLASS_EXPIRY_DAYS),
        )

        try:
            saved = self._repository.create(notification)
            LOGGER.info(
                "Break-glass session end notification: %s (id=%s)",
                username,
                saved.notification_id,
            )
            return NotificationResult.sent(saved.notification_id or 0)
        except Exception as e:
            LOGGER.error("Failed to send session end notification: %s", e)
            return NotificationResult.failed(str(e))

    # ------------------------------------------------------------------
    # Rotation notifications
    # ------------------------------------------------------------------
    def notify_rotation_required(
        self,
        *,
        username: str,
        reason: str,
        urgency: str = "normal",
    ) -> NotificationResult:
        """Send notification that credential rotation is required.

        Args:
            username: Account requiring rotation.
            reason: Why rotation is needed.
            urgency: 'normal' or 'urgent'.
        """
        prefix = "[URGENT] " if urgency == "urgent" else ""
        subject = f"{prefix}Credential rotation required: {username}"
        body = (
            f"Account '{username}' requires credential rotation.\n\n"
            f"Reason: {reason}\n"
            f"Urgency: {urgency}\n"
        )

        notification = AdminNotification(
            notification_type=NotificationType.ROTATION_REQUIRED,
            subject=subject,
            body=body,
            metadata={
                "username": username,
                "reason": reason,
                "urgency": urgency,
            },
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self._default_expiry_days),
        )

        try:
            saved = self._repository.create(notification)
            LOGGER.warning(
                "Rotation required notification: %s (id=%s)",
                username,
                saved.notification_id,
            )
            return NotificationResult.sent(saved.notification_id or 0)
        except Exception as e:
            LOGGER.error("Failed to send rotation notification: %s", e)
            return NotificationResult.failed(str(e))

    # ------------------------------------------------------------------
    # Lockout notifications
    # ------------------------------------------------------------------
    def notify_lockout_alert(
        self,
        *,
        username: str,
        attempts: int,
        is_cooldown: bool,
        cooldown_minutes: int | None = None,
        source_ip: str | None = None,
    ) -> NotificationResult:
        """Send notification about account lockout.

        Args:
            username: Account that was locked.
            attempts: Number of failed attempts.
            is_cooldown: Whether this is a cooldown (True) or permanent
                lockout (False).
            cooldown_minutes: If cooldown, how long until auto-unblock.
            source_ip: Source IP of the failed attempts.
        """
        if is_cooldown:
            subject = f"Account cooldown: {username}"
            body = (
                f"Account '{username}' entered cooldown after "
                f"{attempts} failed attempts.\n\n"
                f"Auto-unblock in: {cooldown_minutes} minutes\n"
            )
        else:
            subject = f"Account locked: {username}"
            body = (
                f"Account '{username}' has been locked after "
                f"{attempts} failed attempts.\n\n"
                "Manual admin intervention required to unblock.\n"
            )

        if source_ip:
            body += f"Source IP: {source_ip}\n"

        notification = AdminNotification(
            notification_type=NotificationType.LOCKOUT_ALERT,
            subject=subject,
            body=body,
            metadata={
                "username": username,
                "attempts": attempts,
                "is_cooldown": is_cooldown,
                "cooldown_minutes": cooldown_minutes,
                "source_ip": source_ip,
            },
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self._default_expiry_days),
        )

        try:
            saved = self._repository.create(notification)
            log_level = LOGGER.info if is_cooldown else LOGGER.warning
            log_level(
                "Lockout notification: %s (id=%s, cooldown=%s)",
                username,
                saved.notification_id,
                is_cooldown,
            )
            return NotificationResult.sent(saved.notification_id or 0)
        except Exception as e:
            LOGGER.error("Failed to send lockout notification: %s", e)
            return NotificationResult.failed(str(e))

    # ------------------------------------------------------------------
    # Security incident notifications
    # ------------------------------------------------------------------
    def notify_security_incident(
        self,
        *,
        incident_type: str,
        description: str,
        affected_accounts: Sequence[str] | None = None,
        severity: str = "medium",
        correlation_id: str | None = None,
    ) -> NotificationResult:
        """Send notification about a security incident.

        Args:
            incident_type: Type of incident (e.g., 'brute_force',
                'privilege_escalation', 'unauthorized_access').
            description: Detailed description of the incident.
            affected_accounts: List of affected usernames.
            severity: 'low', 'medium', 'high', or 'critical'.
            correlation_id: Optional correlation ID for tracking.
        """
        severity_prefix = {
            "critical": "[CRITICAL] ",
            "high": "[HIGH] ",
            "medium": "",
            "low": "",
        }.get(severity, "")

        subject = f"{severity_prefix}Security Incident: {incident_type}"
        body = f"Security incident detected.\n\n{description}\n"

        if affected_accounts:
            body += f"\nAffected accounts: {', '.join(affected_accounts)}\n"

        metadata: dict = {
            "incident_type": incident_type,
            "severity": severity,
        }
        if affected_accounts:
            metadata["affected_accounts"] = list(affected_accounts)
        if correlation_id:
            metadata["correlation_id"] = correlation_id

        notification = AdminNotification(
            notification_type=NotificationType.SECURITY_INCIDENT,
            subject=subject,
            body=body,
            metadata=metadata,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=BREAK_GLASS_EXPIRY_DAYS),
        )

        try:
            saved = self._repository.create(notification)
            LOGGER.error(
                "Security incident notification: %s (id=%s, severity=%s)",
                incident_type,
                saved.notification_id,
                severity,
            )
            return NotificationResult.sent(saved.notification_id or 0)
        except Exception as e:
            LOGGER.error("Failed to send security notification: %s", e)
            return NotificationResult.failed(str(e))

    # ------------------------------------------------------------------
    # Notification management
    # ------------------------------------------------------------------
    def get_unacknowledged(
        self,
        *,
        notification_type: NotificationType | None = None,
        limit: int = 50,
    ) -> Sequence[AdminNotification]:
        """Get all unacknowledged notifications."""
        return self._repository.list_unacknowledged(
            notification_type=notification_type,
            limit=limit,
        )

    def get_break_glass_alerts(
        self,
        *,
        limit: int = 50,
    ) -> Sequence[AdminNotification]:
        """Get all unacknowledged break-glass alerts."""
        return self._repository.list_unacknowledged(
            notification_type=NotificationType.BREAK_GLASS_USAGE,
            limit=limit,
        )

    def acknowledge(
        self,
        notification_id: int,
        admin_username: str,
    ) -> bool:
        """Acknowledge a notification. Returns True if acknowledged."""
        success = self._repository.acknowledge(notification_id, admin_username)
        if success:
            LOGGER.info(
                "Notification %s acknowledged by %s",
                notification_id,
                admin_username,
            )
        return success

    def get_unacknowledged_count(
        self,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Count unacknowledged notifications."""
        return self._repository.count_unacknowledged(notification_type)

    def cleanup_expired(self) -> int:
        """Remove expired notifications. Returns count removed."""
        count = self._repository.delete_expired()
        if count > 0:
            LOGGER.info("Cleaned up %d expired notifications", count)
        return count


__all__ = ["AdminNotificationService", "NotificationResult"]
