"""Identity facade module for RFU authentication flows.

This module provides a simplified interface for identity-related operations,
re-exporting key components from the core auth subsystem and providing
convenience functions for GUI login flows.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from src.core.auth.auth_service import AuthService, BreakGlassJustificationRequired
from src.core.auth.exceptions import AccountBlockedError, AuthenticationError
from src.core.auth.models import AuthSession, UserAccount
from src.core.auth.services.registration_service import RegistrationService
from src.core.auth.user_store import UserStore
from src.log_manager import get_log_manager

_LOGGER = get_log_manager().get_logger("RFU.Identity")


def login_with_preferences(
    *,
    database_path: str | Path,
    username: str,
    password: str,
    justification: Optional[str] = None,
    surface: str = "gui",
) -> Dict[str, Any]:
    """Authenticate a user and return session with preferences.

    This is the primary entry point for GUI login flows. It handles
    authentication and loads any user preferences associated with the account.

    Args:
        database_path: Path to the identity database.
        username: The username to authenticate.
        password: The user's password.
        justification: Required justification for break-glass accounts.
        surface: The login surface identifier (default: 'gui').

    Returns:
        A dictionary containing:
            - status: 'authenticated' on success
            - session: The AuthSession object
            - workspace_ready: Boolean indicating workspace is ready
            - preference_snapshot: User preferences if available
            - preference_badge: Badge metadata for UI display

    Raises:
        AuthenticationError: If credentials are invalid.
        AccountBlockedError: If the account is blocked.
        BreakGlassJustificationRequired: If break-glass login needs justification.
    """
    db_path = Path(database_path)

    # Initialize the user store and auth service
    store = UserStore(database_path=db_path)
    auth_service = AuthService(store=store)

    # Attempt authentication
    session = auth_service.authenticate(
        username=username,
        password=password,
        surface=surface,
        justification=justification,
    )

    # Build the result with preferences
    result: Dict[str, Any] = {
        "status": "authenticated",
        "session": session,
        "workspace_ready": True,
        "username": session.username,
        "role": session.role,
    }

    # Load user preferences if available
    preference_snapshot = _load_user_preferences(db_path, session.username)
    if preference_snapshot:
        result["preference_snapshot"] = preference_snapshot
        result["preference_badge"] = {
            "text": f"Preferences loaded for {session.username}",
            "label": preference_snapshot.get("layout_label", "Default"),
            "user": session.username,
            "preferences_id": preference_snapshot.get("preferences_id"),
        }
    else:
        result["preference_snapshot"] = None
        result["preference_badge"] = None

    _LOGGER.info("User '%s' authenticated successfully via %s", username, surface)
    return result


def submit_registration_request(
    *,
    database_path: str | Path,
    username: str,
    password: str,
    metadata: Optional[Mapping[str, Any]] = None,
    channel: str = "gui",
) -> Dict[str, Any]:
    """Submit a self-registration request for a new user account.

    Args:
        database_path: Path to the identity database.
        username: Desired username for the new account.
        password: Password for the new account.
        metadata: Optional metadata (workspace preferences, notes, etc.).
        channel: Registration channel identifier (default: 'gui').

    Returns:
        A dictionary containing:
            - username: The sanitized username
            - status: 'pending' for accounts awaiting approval
            - requires_approval: Boolean indicating admin approval needed
            - message: User-friendly status message

    Raises:
        ValueError: If username/password validation fails or user exists.
        FileNotFoundError: If the identity database doesn't exist.
    """
    db_path = Path(database_path)

    registration_service = RegistrationService(
        database_path=db_path,
        origin_surface="gui",
    )

    result = registration_service.register_user(
        username=username,
        password=password,
        channel=channel,
        metadata=metadata,
    )

    _LOGGER.info(
        "Registration request submitted for '%s' via %s",
        result.get("username", username),
        channel,
    )
    return result


def _load_user_preferences(
    database_path: Path,
    username: str,
) -> Optional[Dict[str, Any]]:
    """Load user preferences from the database.

    Args:
        database_path: Path to the identity database.
        username: The username to load preferences for.

    Returns:
        Dictionary with preferences or None if not found.
    """
    try:
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            # Try to find user's preferences_id
            row = conn.execute(
                """
                SELECT preferences_id FROM user_accounts
                WHERE username = ? AND preferences_id IS NOT NULL
                """,
                (username,),
            ).fetchone()

            if not row or not row["preferences_id"]:
                return None

            preferences_id = row["preferences_id"]

            # Try to load preferences data
            pref_row = conn.execute(
                """
                SELECT * FROM user_preferences
                WHERE id = ? OR preferences_id = ?
                """,
                (preferences_id, preferences_id),
            ).fetchone()

            if pref_row:
                return {
                    "preferences_id": preferences_id,
                    "layout_label": pref_row.get("layout_label", "Default")
                    if hasattr(pref_row, "get")
                    else "Default",
                    "data": dict(pref_row) if pref_row else {},
                }

    except sqlite3.Error as exc:
        _LOGGER.debug("Could not load preferences for %s: %s", username, exc)
    except Exception as exc:
        _LOGGER.debug("Preferences lookup failed for %s: %s", username, exc)

    return None


__all__ = [
    # Re-exported from core auth
    "AuthenticationError",
    "AccountBlockedError",
    "BreakGlassJustificationRequired",
    "AuthSession",
    "UserAccount",
    # Convenience functions
    "login_with_preferences",
    "submit_registration_request",
]
