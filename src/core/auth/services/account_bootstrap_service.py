"""Account bootstrap service for initializing protected accounts.

Creates always-available and break-glass accounts during database
initialization. Idempotent - safe to call multiple times.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Protocol

from src.core.auth.models.user_account import (
    AccountStatus,
    RegistrationChannel,
    UserAccount,
    UserRole,
)
from src.core.auth.security.password_hasher import PasswordHasher


class UserAccountRepository(Protocol):
    """Minimal interface for user account persistence."""

    def get(self, username: str) -> Optional[UserAccount]: ...

    def upsert(self, account: UserAccount) -> None: ...


@dataclass(frozen=True, slots=True)
class CreatedAccount:
    """Details of a created protected account."""

    username: str
    role: UserRole
    account_type: str  # 'always_available' or 'break_glass'
    temporary_password: str | None = None
    password_displayed: bool = False


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    """Result of bootstrap operation."""

    success: bool
    accounts_created: List[CreatedAccount] = field(default_factory=list)
    accounts_existing: List[str] = field(default_factory=list)
    credentials_file: str | None = None
    console_output_shown: bool = False
    error: str | None = None

    @classmethod
    def completed(
        cls,
        accounts_created: List[CreatedAccount],
        accounts_existing: List[str],
        credentials_file: str | None = None,
        console_output_shown: bool = False,
    ) -> "BootstrapResult":
        """Successful bootstrap."""
        return cls(
            success=True,
            accounts_created=accounts_created,
            accounts_existing=accounts_existing,
            credentials_file=credentials_file,
            console_output_shown=console_output_shown,
        )

    @classmethod
    def failed(cls, error: str) -> "BootstrapResult":
        """Failed bootstrap."""
        return cls(success=False, error=error)


# Protected account definitions
PROTECTED_ACCOUNTS = [
    {
        "username": "rfu_dev_always",
        "role": UserRole.DEV,
        "account_type": "always_available",
        "is_always_available": True,
        "is_break_glass": False,
    },
    {
        "username": "rfu_admin_always",
        "role": UserRole.ADMIN,
        "account_type": "always_available",
        "is_always_available": True,
        "is_break_glass": False,
    },
    {
        "username": "rfu_dev_breakglass",
        "role": UserRole.DEV,
        "account_type": "break_glass",
        "is_always_available": False,
        "is_break_glass": True,
    },
    {
        "username": "rfu_admin_breakglass",
        "role": UserRole.ADMIN,
        "account_type": "break_glass",
        "is_always_available": False,
        "is_break_glass": True,
    },
]


class AccountBootstrapService:
    """Service for bootstrapping protected administrative accounts.

    Creates always-available and break-glass accounts with secure
    random credentials. Idempotent - existing accounts are skipped.
    """

    DEFAULT_PASSWORD_LENGTH = 24
    DEFAULT_CREDENTIALS_DIR = Path("config")

    def __init__(
        self,
        user_repository: UserAccountRepository | None = None,
        password_hasher: PasswordHasher | None = None,
        credentials_dir: Path | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._user_repo = user_repository
        self._hasher = password_hasher or PasswordHasher()
        self._credentials_dir = credentials_dir or self.DEFAULT_CREDENTIALS_DIR
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def bootstrap_protected_accounts(
        self,
        *,
        show_console: bool = True,
        export_credentials: bool = True,
    ) -> BootstrapResult:
        """Initialize all protected accounts.

        Args:
            show_console: Whether to display credentials on console
            export_credentials: Whether to export to secure file

        Returns:
            BootstrapResult with created accounts and credential paths
        """
        if self._user_repo is None:
            return BootstrapResult.failed("User repository not configured")

        created_accounts: List[CreatedAccount] = []
        existing_accounts: List[str] = []
        credentials_for_export: List[dict] = []

        for account_def in PROTECTED_ACCOUNTS:
            username = account_def["username"]
            existing = self._user_repo.get(username)

            if existing is not None:
                existing_accounts.append(username)
                continue

            # Generate secure random password
            password = self._hasher.generate_temporary_password(
                length=self.DEFAULT_PASSWORD_LENGTH
            )
            password_hash, password_salt = self._hasher.hash_with_salt(password)

            # Create account
            now = self._clock()
            account = UserAccount(
                username=username,
                password_hash=password_hash,
                password_salt=password_salt,
                role=account_def["role"],
                account_status=AccountStatus.ACTIVE,
                is_always_available=account_def["is_always_available"],
                is_break_glass=account_def["is_break_glass"],
                registration_channel=RegistrationChannel.BOOTSTRAP,
                created_at=now,
                activated_at=now,
            )

            self._user_repo.upsert(account)

            created_accounts.append(
                CreatedAccount(
                    username=username,
                    role=account_def["role"],
                    account_type=account_def["account_type"],
                    temporary_password=password,
                    password_displayed=show_console,
                )
            )

            credentials_for_export.append(
                {
                    "username": username,
                    "role": account_def["role"].value,
                    "account_type": account_def["account_type"],
                    "password": password,
                }
            )

        # Export credentials to file
        credentials_file = None
        if export_credentials and credentials_for_export:
            credentials_file = self._export_credentials(credentials_for_export)

        # Show on console
        if show_console and created_accounts:
            self._display_credentials(created_accounts)

        return BootstrapResult.completed(
            accounts_created=created_accounts,
            accounts_existing=existing_accounts,
            credentials_file=credentials_file,
            console_output_shown=show_console and bool(created_accounts),
        )

    def _export_credentials(
        self,
        credentials: List[dict],
    ) -> str | None:
        """Export credentials to secure file.

        Returns:
            Path to created file, or None on failure
        """
        try:
            self._credentials_dir.mkdir(parents=True, exist_ok=True)
            timestamp = self._clock().strftime("%Y%m%d_%H%M%S")
            filename = f"protected_credentials_{timestamp}.secure"
            filepath = self._credentials_dir / filename

            # Write credentials in a parseable format
            lines = [
                "# RFU Protected Account Credentials",
                f"# Generated: {timestamp}",
                "# SECURE THIS FILE IMMEDIATELY",
                "#",
                "# Format: username | role | type | password",
                "",
            ]

            for cred in credentials:
                lines.append(
                    f"{cred['username']} | {cred['role']} | "
                    f"{cred['account_type']} | {cred['password']}"
                )

            lines.append("")
            lines.append("# After securing, delete this file")

            filepath.write_text("\n".join(lines), encoding="utf-8")

            # Set restrictive permissions on Unix
            try:
                os.chmod(filepath, 0o600)
            except (OSError, AttributeError):
                pass  # Windows or permission error

            return str(filepath)

        except OSError:
            return None

    def _display_credentials(
        self,
        accounts: List[CreatedAccount],
    ) -> None:
        """Display credentials on console.

        This is intentionally a no-op in the service layer.
        The CLI command will handle the actual display.
        """
        # In the service layer, we just prepare the data
        # The CLI command handles actual console output
        _ = accounts  # Mark as intentionally unused

    def get_protected_account_list(
        self,
    ) -> List[dict]:
        """Get list of protected account definitions.

        Returns:
            List of account definition dictionaries
        """
        return [
            {
                "username": acc["username"],
                "role": acc["role"].value,
                "account_type": acc["account_type"],
            }
            for acc in PROTECTED_ACCOUNTS
        ]

    def verify_protected_accounts_exist(
        self,
    ) -> dict:
        """Verify all protected accounts exist in database.

        Returns:
            Dict with 'complete', 'missing', 'existing' keys
        """
        if self._user_repo is None:
            return {
                "complete": False,
                "error": "User repository not configured",
            }

        existing = []
        missing = []

        for account_def in PROTECTED_ACCOUNTS:
            username = account_def["username"]
            account = self._user_repo.get(username)
            if account is not None:
                existing.append(username)
            else:
                missing.append(username)

        return {
            "complete": len(missing) == 0,
            "existing": existing,
            "missing": missing,
        }

    def rotate_break_glass_credentials(
        self,
        username: str,
        *,
        show_console: bool = True,
        export_credential: bool = True,
    ) -> dict:
        """Rotate credentials for a break-glass account.

        Args:
            username: The break-glass account to rotate
            show_console: Whether to display new credential on console
            export_credential: Whether to export to secure file

        Returns:
            Dict with success status, new credential info, and paths
        """
        if self._user_repo is None:
            return {
                "success": False,
                "error": "User repository not configured",
            }

        # Verify account exists and is break-glass
        account = self._user_repo.get(username)
        if account is None:
            return {
                "success": False,
                "error": f"Account '{username}' not found",
            }

        if not account.is_break_glass:
            return {
                "success": False,
                "error": f"Account '{username}' is not a break-glass account",
            }

        # Generate new secure password
        new_password = self._hasher.generate_temporary_password(
            length=self.DEFAULT_PASSWORD_LENGTH
        )
        new_hash, new_salt = self._hasher.hash_with_salt(new_password)

        # Update account with new password
        now = self._clock()
        updated_account = UserAccount(
            username=account.username,
            password_hash=new_hash,
            password_salt=new_salt,
            role=account.role,
            account_status=account.account_status,
            is_blocked=False,  # Reset blocked state on rotation
            login_attempts=0,  # Reset login attempts
            is_always_available=account.is_always_available,
            is_break_glass=account.is_break_glass,
            registration_channel=account.registration_channel,
            created_at=account.created_at,
            activated_at=account.activated_at,
            updated_at=now,
        )
        self._user_repo.upsert(updated_account)

        # Export credential to file
        credentials_file = None
        if export_credential:
            credentials_file = self._export_credentials(
                [
                    {
                        "username": username,
                        "role": account.role.value,
                        "account_type": "break_glass",
                        "password": new_password,
                    }
                ]
            )

        return {
            "success": True,
            "username": username,
            "role": account.role.value,
            "new_password": new_password if show_console else None,
            "password_rotated": True,
            "credentials_file": credentials_file,
            "rotated_at": now.isoformat(),
        }


__all__ = [
    "AccountBootstrapService",
    "BootstrapResult",
    "CreatedAccount",
    "PROTECTED_ACCOUNTS",
]
