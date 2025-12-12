"""Role policy enforcement for the four-role system.

This module implements the role hierarchy and capability matrix defined in
specs/007-upgrade-to-login/spec.md, providing consistent permission checks
across CLI, GUI, and API surfaces.

Role hierarchy (highest to lowest): dev > admin > user > readonly
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, FrozenSet, Mapping


class Capability(StrEnum):
    """Capabilities that can be granted to roles."""

    VIEW_DATA = "view_data"
    MODIFY_DATA = "modify_data"
    MANAGE_USERS = "manage_users"
    MANAGE_CONFIG = "manage_config"
    ACCESS_DEBUGGING = "access_debugging"
    ACCESS_LOGS = "access_logs"
    MANAGE_BREAK_GLASS = "manage_break_glass"
    MANAGE_ALWAYS_AVAILABLE = "manage_always_available"


# Privilege levels for role hierarchy
ROLE_HIERARCHY: Dict[str, int] = {
    "dev": 4,
    "admin": 3,
    "user": 2,
    "readonly": 1,
}

# Capability matrix matching spec.md
CAPABILITY_MATRIX: Dict[str, FrozenSet[Capability]] = {
    "dev": frozenset(Capability),  # All capabilities
    "admin": frozenset(
        [
            Capability.VIEW_DATA,
            Capability.MODIFY_DATA,
            Capability.MANAGE_USERS,
            Capability.MANAGE_CONFIG,
            Capability.ACCESS_LOGS,
        ]
    ),
    "user": frozenset(
        [
            Capability.VIEW_DATA,
            Capability.MODIFY_DATA,
        ]
    ),
    "readonly": frozenset(
        [
            Capability.VIEW_DATA,
        ]
    ),
}


@dataclass(frozen=True, slots=True)
class PermissionResult:
    """Result of a permission check."""

    allowed: bool
    reason: str | None = None

    @classmethod
    def allow(cls) -> "PermissionResult":
        return cls(allowed=True)

    @classmethod
    def deny(cls, reason: str) -> "PermissionResult":
        return cls(allowed=False, reason=reason)


@dataclass(frozen=True, slots=True)
class RoleChangeResult:
    """Result of a role change operation."""

    success: bool
    old_role: str | None = None
    new_role: str | None = None
    reason: str | None = None


def get_privilege_level(role: str) -> int:
    """Return numeric privilege level for a role. Unknown roles get 0."""
    return ROLE_HIERARCHY.get(role.lower(), 0)


def has_capability(role: str, capability: Capability | str) -> bool:
    """Check if a role has a specific capability."""
    role_lower = role.lower()
    if role_lower not in CAPABILITY_MATRIX:
        return False

    cap = Capability(capability) if isinstance(capability, str) else capability
    return cap in CAPABILITY_MATRIX[role_lower]


def check_permission(role: str, action: str) -> PermissionResult:
    """Check if a role has permission to perform an action.

    Args:
        role: The role to check (dev, admin, user, readonly)
        action: The action/capability name to check

    Returns:
        PermissionResult indicating whether the action is allowed
    """
    role_lower = role.lower()

    # Normalize action to capability
    action_to_capability: Mapping[str, Capability] = {
        "view": Capability.VIEW_DATA,
        "view_data": Capability.VIEW_DATA,
        "read": Capability.VIEW_DATA,
        "modify": Capability.MODIFY_DATA,
        "modify_data": Capability.MODIFY_DATA,
        "write": Capability.MODIFY_DATA,
        "delete": Capability.MODIFY_DATA,
        "manage_users": Capability.MANAGE_USERS,
        "user_management": Capability.MANAGE_USERS,
        "approve_user": Capability.MANAGE_USERS,
        "reset_password": Capability.MANAGE_USERS,
        "unblock_user": Capability.MANAGE_USERS,
        "manage_config": Capability.MANAGE_CONFIG,
        "configuration": Capability.MANAGE_CONFIG,
        "debug": Capability.ACCESS_DEBUGGING,
        "access_debugging": Capability.ACCESS_DEBUGGING,
        "diagnostics": Capability.ACCESS_DEBUGGING,
        "logs": Capability.ACCESS_LOGS,
        "access_logs": Capability.ACCESS_LOGS,
        "break_glass": Capability.MANAGE_BREAK_GLASS,
        "manage_break_glass": Capability.MANAGE_BREAK_GLASS,
        "always_available": Capability.MANAGE_ALWAYS_AVAILABLE,
        "manage_always_available": Capability.MANAGE_ALWAYS_AVAILABLE,
    }

    action_lower = action.lower()
    capability = action_to_capability.get(action_lower)

    if capability is None:
        return PermissionResult.deny(f"unknown action: {action}")

    if has_capability(role_lower, capability):
        return PermissionResult.allow()

    # Provide specific denial reasons
    required_role = _get_required_role_for_capability(capability)
    return PermissionResult.deny(f"{required_role} role required")


def _get_required_role_for_capability(capability: Capability) -> str:
    """Return the minimum role required for a capability."""
    if capability in (
        Capability.MANAGE_BREAK_GLASS,
        Capability.MANAGE_ALWAYS_AVAILABLE,
        Capability.ACCESS_DEBUGGING,
    ):
        return "dev"
    if capability in (
        Capability.MANAGE_USERS,
        Capability.MANAGE_CONFIG,
        Capability.ACCESS_LOGS,
    ):
        return "admin"
    if capability == Capability.MODIFY_DATA:
        return "user"
    return "readonly"


def can_escalate(actor_role: str, target_role: str) -> bool:
    """Check if actor can escalate someone to target role.

    Rules:
    - Escalation to dev requires dev role
    - Escalation to admin requires admin or dev role
    - Demotion is always allowed (checked separately)
    """
    actor_level = get_privilege_level(actor_role)
    target_level = get_privilege_level(target_role)

    # Cannot escalate above own level
    if target_level > actor_level:
        return False

    # Escalation to dev requires dev
    if target_role.lower() == "dev" and actor_role.lower() != "dev":
        return False

    return True


def can_demote(actor_role: str, current_role: str, new_role: str) -> bool:
    """Check if actor can demote someone from current to new role.

    Demotion (lowering privilege level) is generally allowed if:
    - Actor has sufficient privilege to manage the current role
    - Actor is at least as privileged as the current role holder
    """
    actor_level = get_privilege_level(actor_role)
    current_level = get_privilege_level(current_role)
    new_level = get_privilege_level(new_role)

    # Must be a demotion
    if new_level >= current_level:
        return False

    # Actor must be at least as privileged as current role
    return actor_level >= current_level


def check_role_change(
    actor_role: str,
    target_username: str,
    current_role: str,
    new_role: str,
) -> RoleChangeResult:
    """Check if a role change is permitted.

    Args:
        actor_role: Role of the user making the change
        target_username: Username being modified
        current_role: Current role of the target
        new_role: Proposed new role

    Returns:
        RoleChangeResult with success status and details
    """
    current_level = get_privilege_level(current_role)
    new_level = get_privilege_level(new_role)

    # No change needed
    if current_role.lower() == new_role.lower():
        return RoleChangeResult(
            success=True,
            old_role=current_role,
            new_role=new_role,
            reason="no change required",
        )

    # Check if escalation or demotion
    if new_level > current_level:
        # Escalation
        if can_escalate(actor_role, new_role):
            return RoleChangeResult(
                success=True,
                old_role=current_role,
                new_role=new_role,
            )
        if new_role.lower() == "dev":
            return RoleChangeResult(
                success=False,
                reason="dev role required for escalation to dev",
            )
        return RoleChangeResult(
            success=False,
            reason=f"insufficient privilege to escalate to {new_role}",
        )
    else:
        # Demotion
        if can_demote(actor_role, current_role, new_role):
            return RoleChangeResult(
                success=True,
                old_role=current_role,
                new_role=new_role,
            )
        return RoleChangeResult(
            success=False,
            reason="insufficient privilege to demote this user",
        )


__all__ = [
    "Capability",
    "CAPABILITY_MATRIX",
    "PermissionResult",
    "ROLE_HIERARCHY",
    "RoleChangeResult",
    "can_demote",
    "can_escalate",
    "check_permission",
    "check_role_change",
    "get_privilege_level",
    "has_capability",
]
