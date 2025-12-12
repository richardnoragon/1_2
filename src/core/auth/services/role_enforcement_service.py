"""Role enforcement service for permission checks and role changes.

Implements T049: Wraps role_policy.py with audit logging and provides
a service interface for role-based access control operations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

from src.core.auth.models.admin_action_audit import (
    AdminActionAudit,
    AdminActionSurface,
    AdminActionType,
)
from src.core.auth.models.user_account import UserRole
from src.core.auth.policies.role_policy import (
    Capability,
    PermissionResult,
    RoleChangeResult,
)
from src.core.auth.policies.role_policy import (
    check_permission as policy_check_permission,
)
from src.core.auth.policies.role_policy import (
    check_role_change as policy_check_role_change,
)
from src.core.auth.policies.role_policy import (
    get_privilege_level,
    has_capability,
)


class UserAccountRepository(Protocol):
    """Minimal interface for user account persistence."""

    def get(self, username: str) -> Any: ...

    def upsert(self, account: Any) -> None: ...


class AdminActionAuditRepository(Protocol):
    """Minimal interface for audit logging."""

    def append(self, audit: AdminActionAudit) -> AdminActionAudit: ...


@dataclass(frozen=True, slots=True)
class EnforcedPermissionResult:
    """Result of an enforced permission check."""

    allowed: bool
    role: str
    action: str
    reason: str | None = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_policy_result(
        cls,
        result: PermissionResult,
        role: str,
        action: str,
    ) -> "EnforcedPermissionResult":
        """Create from underlying policy result."""
        return cls(
            allowed=result.allowed,
            role=role,
            action=action,
            reason=result.reason,
        )


@dataclass(frozen=True, slots=True)
class EnforcedRoleChangeResult:
    """Result of an enforced role change operation."""

    success: bool
    actor_username: str
    target_username: str
    old_role: str | None = None
    new_role: str | None = None
    reason: str | None = None
    audit_id: str | None = None
    changed_at: datetime | None = None

    @classmethod
    def denied(
        cls,
        actor_username: str,
        target_username: str,
        reason: str,
    ) -> "EnforcedRoleChangeResult":
        """Create a denied result."""
        return cls(
            success=False,
            actor_username=actor_username,
            target_username=target_username,
            reason=reason,
        )

    @classmethod
    def completed(
        cls,
        actor_username: str,
        target_username: str,
        old_role: str,
        new_role: str,
        audit_id: str,
    ) -> "EnforcedRoleChangeResult":
        """Create a successful result."""
        return cls(
            success=True,
            actor_username=actor_username,
            target_username=target_username,
            old_role=old_role,
            new_role=new_role,
            audit_id=audit_id,
            changed_at=datetime.now(timezone.utc),
        )


class RoleEnforcementService:
    """Service for enforcing role-based access control with audit logging.

    Wraps role_policy.py to provide:
    - Permission checks with consistent interface
    - Role changes with audit trail
    - Integration with user repository for role updates
    """

    def __init__(
        self,
        user_repository: UserAccountRepository | None = None,
        audit_repository: AdminActionAuditRepository | None = None,
        origin_surface: AdminActionSurface = AdminActionSurface.SERVICE,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the role enforcement service.

        Args:
            user_repository: Repository for user account operations
            audit_repository: Repository for audit logging
            origin_surface: Surface identifier for audit records
            clock: Optional clock function for testing
        """
        self._user_repo = user_repository
        self._audit_repo = audit_repository
        self._origin_surface = origin_surface
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def check_permission(
        self,
        role: str,
        action: str,
    ) -> EnforcedPermissionResult:
        """Check if a role has permission to perform an action.

        Delegates to role_policy.check_permission with enhanced result.

        Args:
            role: The role to check (dev, admin, user, readonly)
            action: The action/capability name to check

        Returns:
            EnforcedPermissionResult with check details
        """
        policy_result = policy_check_permission(role, action)
        return EnforcedPermissionResult.from_policy_result(
            policy_result,
            role=role,
            action=action,
        )

    def check_capability(
        self,
        role: str,
        capability: Capability | str,
    ) -> bool:
        """Check if a role has a specific capability.

        Args:
            role: The role to check
            capability: The capability to check

        Returns:
            True if the role has the capability
        """
        return has_capability(role, capability)

    def get_role_level(self, role: str) -> int:
        """Get the privilege level for a role.

        Args:
            role: The role name

        Returns:
            Numeric privilege level (0 for unknown)
        """
        return get_privilege_level(role)

    def can_change_role(
        self,
        actor_role: str,
        target_current_role: str,
        target_new_role: str,
    ) -> RoleChangeResult:
        """Check if a role change is permitted (without performing it).

        Args:
            actor_role: Role of the user making the change
            target_current_role: Current role of the target
            target_new_role: Proposed new role

        Returns:
            RoleChangeResult indicating if change is allowed
        """
        return policy_check_role_change(
            actor_role=actor_role,
            target_username="(check only)",
            current_role=target_current_role,
            new_role=target_new_role,
        )

    def change_role(
        self,
        actor_username: str,
        actor_role: str,
        target_username: str,
        new_role: str,
        justification: str,
        *,
        correlation_id: str | None = None,
    ) -> EnforcedRoleChangeResult:
        """Change a user's role with full enforcement and audit logging.

        Args:
            actor_username: Username performing the change
            actor_role: Role of the actor
            target_username: Username whose role is being changed
            new_role: The new role to assign
            justification: Reason for the role change
            correlation_id: Optional correlation ID for tracing

        Returns:
            EnforcedRoleChangeResult with operation outcome
        """
        if self._user_repo is None:
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason="User repository not configured",
            )

        # Validate justification
        if not justification or len(justification.strip()) < 10:
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason="Justification must be at least 10 characters",
            )

        # Validate new role
        new_role_lower = new_role.lower()
        valid_roles = {"dev", "admin", "user", "readonly"}
        if new_role_lower not in valid_roles:
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason=f"Invalid role: {new_role}",
            )

        # Get target account
        target_account = self._user_repo.get(target_username)
        if target_account is None:
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason=f"User '{target_username}' not found",
            )

        # Get current role
        current_role = self._get_role_string(target_account)

        # Check if change is allowed
        change_check = policy_check_role_change(
            actor_role=actor_role,
            target_username=target_username,
            current_role=current_role,
            new_role=new_role,
        )

        if not change_check.success:
            self._log_failed_change(
                actor_username=actor_username,
                target_username=target_username,
                current_role=current_role,
                new_role=new_role,
                reason=change_check.reason or "Permission denied",
                correlation_id=correlation_id,
            )
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason=change_check.reason or "Permission denied",
            )

        # Perform the role change
        try:
            self._update_user_role(target_account, new_role_lower)
        except Exception as e:
            return EnforcedRoleChangeResult.denied(
                actor_username=actor_username,
                target_username=target_username,
                reason=f"Failed to update role: {e}",
            )

        # Log the successful change
        audit_id = self._log_role_change(
            actor_username=actor_username,
            target_username=target_username,
            old_role=current_role,
            new_role=new_role_lower,
            justification=justification,
            correlation_id=correlation_id,
        )

        return EnforcedRoleChangeResult.completed(
            actor_username=actor_username,
            target_username=target_username,
            old_role=current_role,
            new_role=new_role_lower,
            audit_id=audit_id,
        )

    def _get_role_string(self, account: Any) -> str:
        """Extract role string from account object."""
        role = getattr(account, "role", None)
        if role is None:
            return "readonly"
        if isinstance(role, UserRole):
            return role.value
        return str(role).lower()

    def _update_user_role(self, account: Any, new_role: str) -> None:
        """Update the user's role in the repository."""
        # Convert string to UserRole enum
        role_enum = UserRole(new_role.lower())

        # Update the account
        # Handle both mutable and immutable account objects
        if hasattr(account, "_replace"):
            # Named tuple style
            updated = account._replace(role=role_enum)
        elif hasattr(account, "__dataclass_fields__"):
            # Dataclass - create new instance with updated role
            from dataclasses import replace

            updated = replace(account, role=role_enum)
        else:
            # Mutable object
            account.role = role_enum
            updated = account

        self._user_repo.upsert(updated)

    def _log_role_change(
        self,
        actor_username: str,
        target_username: str,
        old_role: str,
        new_role: str,
        justification: str,
        correlation_id: str | None = None,
    ) -> str:
        """Log a successful role change to the audit trail.

        Returns:
            The audit ID of the created record
        """
        audit_id = str(uuid.uuid4())
        now = self._clock()

        # Determine if this is an escalation or demotion
        old_level = get_privilege_level(old_role)
        new_level = get_privilege_level(new_role)

        if new_level > old_level:
            action_type = AdminActionType.ROLE_ESCALATION
        elif new_level < old_level:
            action_type = AdminActionType.ROLE_DEMOTION
        else:
            action_type = AdminActionType.ROLE_CHANGE

        details = (
            f"Role changed from '{old_role}' to '{new_role}'. "
            f"Justification: {justification}"
        )

        audit = AdminActionAudit(
            audit_id=audit_id,
            actor_username=actor_username,
            action_type=action_type,
            target_username=target_username,
            origin_surface=self._origin_surface,
            details=details,
            created_at=now,
            correlation_id=correlation_id,
            metadata={
                "old_role": old_role,
                "new_role": new_role,
                "justification": justification,
            },
        )

        if self._audit_repo is not None:
            self._audit_repo.append(audit)

        return audit_id

    def _log_failed_change(
        self,
        actor_username: str,
        target_username: str,
        current_role: str,
        new_role: str,
        reason: str,
        correlation_id: str | None = None,
    ) -> None:
        """Log a failed role change attempt."""
        if self._audit_repo is None:
            return

        audit_id = str(uuid.uuid4())
        now = self._clock()

        details = (
            f"Failed role change from '{current_role}' to '{new_role}'. "
            f"Reason: {reason}"
        )

        audit = AdminActionAudit(
            audit_id=audit_id,
            actor_username=actor_username,
            action_type=AdminActionType.UNAUTHORIZED_ADMIN_ACTION,
            target_username=target_username,
            origin_surface=self._origin_surface,
            details=details,
            created_at=now,
            correlation_id=correlation_id,
            metadata={
                "attempted_role_change": True,
                "current_role": current_role,
                "requested_role": new_role,
                "failure_reason": reason,
            },
        )

        self._audit_repo.append(audit)


__all__ = [
    "EnforcedPermissionResult",
    "EnforcedRoleChangeResult",
    "RoleEnforcementService",
]
