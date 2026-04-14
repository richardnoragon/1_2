"""HTTP-style controller for lockout-prevention endpoints.

Exposes always-available account health checks and auto-unblock
status via a simple request/response interface (no framework required).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.core.auth.repositories.user_account_repository import (
    UserAccountRepository,
)
from src.core.auth.services.lockout_prevention_service import (
    LockoutPreventionService,
)


class LockoutPreventionController:
    """Provide lockout-prevention query endpoints for the RFU identity system."""

    def __init__(self, *, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_service(self) -> Optional[LockoutPreventionService]:
        if self.db_path is None:
            return None
        repo = UserAccountRepository(database_path=self.db_path)
        return LockoutPreventionService(user_repository=repo)

    # ------------------------------------------------------------------
    # GET /lockout-prevention/health
    # ------------------------------------------------------------------

    def get_health(self) -> Dict[str, Any]:
        """Return lockout-prevention health status."""
        service = self._build_service()
        if service is None:
            return {
                "status": "error",
                "message": "Database path not configured.",
            }
        health = service.get_health_status()
        paths = [
            {
                "username": p.account_username,
                "role": p.role,
                "account_type": p.account_type,
                "accessible": p.is_accessible,
                "will_auto_unblock_at": p.will_auto_unblock_at,
            }
            for p in health.accessible_paths
        ]
        return {
            "status": "ok",
            "healthy": health.healthy,
            "reason": health.reason,
            "has_dev_access": health.has_dev_access,
            "has_admin_access": health.has_admin_access,
            "blocked_count": health.blocked_count,
            "accessible_paths": paths,
        }

    # ------------------------------------------------------------------
    # GET /lockout-prevention/check-unblock?username=...
    # ------------------------------------------------------------------

    def get_check_unblock(self, username: str) -> Dict[str, Any]:
        """Return auto-unblock status for *username*."""
        service = self._build_service()
        if service is None:
            return {
                "status": "error",
                "message": "Database path not configured.",
            }
        result = service.check_auto_unblock(username=username)
        payload: Dict[str, Any] = {
            "status": "ok",
            "username": result.account_username,
            "should_unblock": result.should_unblock,
            "reason": result.reason,
        }
        if result.time_remaining is not None:
            payload["time_remaining_seconds"] = int(
                result.time_remaining.total_seconds()
            )
        return payload

    # ------------------------------------------------------------------
    # POST /lockout-prevention/auto-unblock
    # ------------------------------------------------------------------

    def post_auto_unblock(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform auto-unblock for the requested account."""
        username = payload.get("username") if isinstance(payload, dict) else None
        if not username:
            return {"status": "error", "message": "username is required."}

        service = self._build_service()
        if service is None:
            return {"status": "error", "message": "Database path not configured."}

        service.perform_auto_unblock(username=str(username))
        return {
            "status": "ok",
            "username": username,
            "message": f"Account '{username}' has been unblocked.",
        }


__all__ = ["LockoutPreventionController"]
