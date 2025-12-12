"""Internal endpoints for lockout prevention system.

Task T067: Provides internal endpoints for:
- GET /internal/health/lockout-prevention: Health check for lockout system
- GET /internal/recovery/cli-path: Get CLI recovery tool path
- POST /internal/bootstrap/protected-accounts: Bootstrap protected accounts
- POST /internal/accounts/{username}/auto-unblock: Trigger auto-unblock

These endpoints are for internal use only and should not be exposed
to external clients.
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.auth.repositories.user_account_repository import (
    UserAccountRepository,
)
from src.core.auth.services.account_bootstrap_service import (
    AccountBootstrapService,
)
from src.core.auth.services.lockout_prevention_service import (
    LockoutPreventionService,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("LockoutPreventionController")

# Constant for CLI filename
RECOVERY_CLI_FILENAME = "recovery_cli.py"


class LockoutPreventionController:
    """Internal controller for lockout prevention operations.

    Provides endpoints for:
    - Health monitoring of lockout prevention system
    - CLI recovery tool path discovery
    - Protected account bootstrapping
    - Auto-unblock trigger for always-available accounts
    """

    def __init__(self, *, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._lockout_service: Optional[LockoutPreventionService] = None
        self._bootstrap_service: Optional[AccountBootstrapService] = None
        self._user_repo: Optional[UserAccountRepository] = None

    def _connect(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @property
    def user_repo(self) -> UserAccountRepository:
        """Lazy-load user repository."""
        if self._user_repo is None:
            self._user_repo = UserAccountRepository(database_path=self.db_path)
        return self._user_repo

    @property
    def lockout_service(self) -> LockoutPreventionService:
        """Lazy-load lockout prevention service."""
        if self._lockout_service is None:
            self._lockout_service = LockoutPreventionService(
                user_repository=self.user_repo,
            )
        return self._lockout_service

    @property
    def bootstrap_service(self) -> AccountBootstrapService:
        """Lazy-load bootstrap service."""
        if self._bootstrap_service is None:
            self._bootstrap_service = AccountBootstrapService(
                user_repository=self.user_repo,
            )
        return self._bootstrap_service

    # ------------------------------------------------------------------
    # GET /internal/health/lockout-prevention
    # ------------------------------------------------------------------
    def get_health(self) -> Dict[str, Any]:
        """Check health of lockout prevention system.

        Returns:
            Health status including:
            - status: 'healthy' or 'unhealthy'
            - database_accessible: bool
            - protected_accounts_count: int
            - always_available_count: int
            - break_glass_count: int
            - checked_at: ISO timestamp
        """
        try:
            health = self.lockout_service.get_health_status()
            always_count = sum(
                1
                for p in health.accessible_paths
                if p.account_type == "always_available"
            )
            break_glass_count = sum(
                1 for p in health.accessible_paths if p.account_type == "break_glass"
            )

            return {
                "status": "healthy" if health.healthy else "unhealthy",
                "database_accessible": True,
                "protected_accounts_count": len(health.accessible_paths),
                "always_available_count": always_count,
                "break_glass_count": break_glass_count,
                "blocked_count": health.blocked_count,
                "reason": health.reason,
                "checked_at": self._utc_now_iso(),
            }
        except Exception as err:
            LOGGER.error("Health check failed: %s", err)
            return {
                "status": "unhealthy",
                "database_accessible": False,
                "error": str(err),
                "checked_at": self._utc_now_iso(),
            }

    # ------------------------------------------------------------------
    # GET /internal/recovery/cli-path
    # ------------------------------------------------------------------
    def get_cli_path(self) -> Dict[str, Any]:
        """Get path to CLI recovery tool.

        Returns:
            CLI tool information including:
            - cli_path: absolute path to recovery CLI
            - python_executable: path to Python interpreter
            - exists: whether the CLI file exists
        """
        # Locate the recovery CLI script
        src_root = Path(__file__).parent.parent.parent.parent
        cli_path = src_root / "rfu" / "cli" / RECOVERY_CLI_FILENAME

        # Alternative paths to check
        alt_paths = [
            src_root / "rfu" / RECOVERY_CLI_FILENAME,
            src_root / "cli" / RECOVERY_CLI_FILENAME,
            src_root.parent / "scripts" / RECOVERY_CLI_FILENAME,
        ]

        found_path = None
        if cli_path.exists():
            found_path = cli_path
        else:
            for alt in alt_paths:
                if alt.exists():
                    found_path = alt
                    break

        python_exe = Path(sys.executable)

        return {
            "cli_path": str(found_path) if found_path else None,
            "python_executable": str(python_exe),
            "exists": found_path is not None and found_path.exists(),
            "command": (
                f"{python_exe} {found_path}"
                if found_path
                else f"{RECOVERY_CLI_FILENAME} not found"
            ),
        }

    # ------------------------------------------------------------------
    # POST /internal/bootstrap/protected-accounts
    # ------------------------------------------------------------------
    def post_bootstrap(
        self, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Bootstrap protected accounts.

        Creates or updates the four protected accounts:
        - rfu_dev_always (dev, always-available)
        - rfu_admin_always (admin, always-available)
        - rfu_dev_breakglass (dev, break-glass)
        - rfu_admin_breakglass (admin, break-glass)

        Args:
            payload: Optional, may contain:
                - force: bool - Force re-bootstrap even if accounts exist
                - dry_run: bool - Only check what would be created

        Returns:
            Bootstrap result with created/existing account info.
        """
        payload = payload or {}
        force = payload.get("force", False)
        dry_run = payload.get("dry_run", False)

        LOGGER.info(
            "Bootstrap requested: force=%s, dry_run=%s",
            force,
            dry_run,
        )

        if dry_run:
            return self._dry_run_bootstrap()

        try:
            result = self.bootstrap_service.bootstrap_protected_accounts(
                show_console=False,
                export_credentials=True,
            )
            return {
                "success": result.success,
                "accounts_created": [a.username for a in result.accounts_created],
                "accounts_existing": result.accounts_existing,
                "credentials_file": result.credentials_file,
                "bootstrapped_at": self._utc_now_iso(),
            }
        except Exception as err:
            LOGGER.error("Bootstrap failed: %s", err)
            return {
                "success": False,
                "error": str(err),
                "bootstrapped_at": self._utc_now_iso(),
            }

    def _dry_run_bootstrap(self) -> Dict[str, Any]:
        """Check what would be created in bootstrap."""
        from src.core.auth.services.account_bootstrap_service import (
            PROTECTED_ACCOUNTS,
        )

        would_create: List[str] = []
        already_exists: List[str] = []

        try:
            health = self.lockout_service.get_health_status()
            existing_usernames = {p.account_username for p in health.accessible_paths}

            for account in PROTECTED_ACCOUNTS:
                username = account["username"]
                if username in existing_usernames:
                    already_exists.append(username)
                else:
                    would_create.append(username)

            return {
                "dry_run": True,
                "would_create": would_create,
                "already_exists": already_exists,
            }
        except Exception as err:
            return {
                "dry_run": True,
                "error": str(err),
            }

    # ------------------------------------------------------------------
    # POST /internal/accounts/{username}/auto-unblock
    # ------------------------------------------------------------------
    def post_auto_unblock(
        self, username: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trigger auto-unblock for an always-available account.

        Only works for accounts with is_always_available=True.
        Respects the 5-minute cooldown period.

        Args:
            username: The username to unblock
            payload: Optional, may contain:
                - force: bool - Skip cooldown check (admin override)

        Returns:
            Unblock result with status and timestamps.
        """
        payload = payload or {}
        force = payload.get("force", False)

        LOGGER.info(
            "Auto-unblock requested: username=%s, force=%s",
            username,
            force,
        )

        try:
            # Check if should auto-unblock
            result = self.lockout_service.check_auto_unblock(username)

            if result.should_unblock or force:
                # Perform the unblock
                success = self.lockout_service.perform_auto_unblock(username)
                return {
                    "success": success,
                    "username": username,
                    "was_blocked": True,
                    "unblocked": success,
                    "forced": force,
                    "processed_at": self._utc_now_iso(),
                }

            # Not ready to unblock
            remaining = 0
            if result.time_remaining:
                remaining = int(result.time_remaining.total_seconds())

            return {
                "success": False,
                "username": username,
                "reason": result.reason,
                "cooldown_remaining_seconds": remaining,
                "processed_at": self._utc_now_iso(),
            }
        except PermissionError as err:
            # Not an always-available account
            LOGGER.warning(
                "Auto-unblock denied for %s: %s",
                username,
                err,
            )
            return {
                "success": False,
                "username": username,
                "error": str(err),
                "error_type": "not_always_available",
                "processed_at": self._utc_now_iso(),
            }
        except Exception as err:
            LOGGER.error(
                "Auto-unblock failed for %s: %s",
                username,
                err,
            )
            return {
                "success": False,
                "username": username,
                "error": str(err),
                "error_type": "internal_error",
                "processed_at": self._utc_now_iso(),
            }

    # ------------------------------------------------------------------
    # GET /internal/accounts/protected
    # ------------------------------------------------------------------
    def get_protected_accounts(self) -> Dict[str, Any]:
        """List all protected accounts.

        Returns:
            List of protected accounts with their status.
        """
        try:
            health = self.lockout_service.get_health_status()
            accounts = [
                {
                    "username": p.account_username,
                    "role": p.role,
                    "account_type": p.account_type,
                    "is_accessible": p.is_accessible,
                    "will_auto_unblock_at": (
                        p.will_auto_unblock_at.isoformat()
                        if p.will_auto_unblock_at
                        else None
                    ),
                }
                for p in health.accessible_paths
            ]
            return {
                "success": True,
                "accounts": accounts,
                "count": len(accounts),
                "retrieved_at": self._utc_now_iso(),
            }
        except Exception as err:
            LOGGER.error("Failed to get protected accounts: %s", err)
            return {
                "success": False,
                "error": str(err),
                "retrieved_at": self._utc_now_iso(),
            }

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------
    @staticmethod
    def _utc_now_iso() -> str:
        """Get current UTC time as ISO string."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


__all__ = ["LockoutPreventionController"]
