"""Service for bootstrapping protected (always-available + break-glass) accounts."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.auth.models.user_account import (
    AccountStatus,
    RegistrationChannel,
    UserAccount,
    UserRole,
)
from src.core.auth.security.password_hasher import PasswordHasher

# ---------------------------------------------------------------------------
# Protected account definitions
# ---------------------------------------------------------------------------
PROTECTED_ACCOUNTS: List[Dict[str, Any]] = [
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


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------
@dataclass
class CreatedAccount:
    """Holds information about a freshly-created protected account."""

    username: str
    role: UserRole
    account_type: str
    temporary_password: Optional[str] = None
    password_displayed: bool = False


@dataclass
class BootstrapResult:
    """Result from a bootstrap operation."""

    success: bool
    accounts_created: List[CreatedAccount] = field(default_factory=list)
    accounts_existing: List[str] = field(default_factory=list)
    credentials_file: Optional[str] = None
    console_output_shown: bool = False
    error: Optional[str] = None

    @classmethod
    def completed(
        cls,
        *,
        accounts_created: List[CreatedAccount],
        accounts_existing: List[str],
        credentials_file: Optional[str] = None,
        console_output_shown: bool = False,
    ) -> "BootstrapResult":
        return cls(
            success=True,
            accounts_created=accounts_created,
            accounts_existing=accounts_existing,
            credentials_file=credentials_file,
            console_output_shown=console_output_shown,
        )

    @classmethod
    def failed(cls, error: str) -> "BootstrapResult":
        return cls(
            success=False,
            error=error,
        )


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class AccountBootstrapService:
    """Create and verify the four protected accounts on a fresh system."""

    DEFAULT_PASSWORD_LENGTH = 24
    _CREDENTIAL_FILE_NAME = "protected_credentials.txt"

    def __init__(
        self,
        *,
        user_repository: Any = None,
        credentials_dir: Optional[Path] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._repo = user_repository
        self._credentials_dir = credentials_dir
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._hasher = PasswordHasher()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def bootstrap_protected_accounts(
        self,
        *,
        show_console: bool = True,
        export_credentials: bool = True,
    ) -> BootstrapResult:
        """Create the four protected accounts if they do not yet exist.

        This method is idempotent — calling it multiple times is safe.
        """
        if self._repo is None:
            return BootstrapResult.failed(
                "Repository not configured; cannot bootstrap accounts."
            )

        now = self._clock()
        accounts_created: List[CreatedAccount] = []
        accounts_existing: List[str] = []

        for defn in PROTECTED_ACCOUNTS:
            username: str = defn["username"]
            existing = self._repo.get(username)
            if existing is not None:
                accounts_existing.append(username)
                continue

            password = self._generate_password()
            password_hash, password_salt = self._hasher.hash_with_salt(password)

            account = UserAccount(
                username=username,
                password_hash=password_hash,
                password_salt=password_salt,
                role=defn["role"],
                account_status=AccountStatus.ACTIVE,
                registration_channel=RegistrationChannel.BOOTSTRAP,
                is_always_available=defn["is_always_available"],
                is_break_glass=defn["is_break_glass"],
                created_at=now,
                activated_at=now,
                updated_at=now,
                reset_required=True,
            )
            self._repo.upsert(account)

            accounts_created.append(
                CreatedAccount(
                    username=username,
                    role=defn["role"],
                    account_type=defn["account_type"],
                    temporary_password=password,
                    password_displayed=show_console,
                )
            )

        credentials_file: Optional[str] = None
        if export_credentials and accounts_created and self._credentials_dir:
            credentials_file = self._export_credentials(accounts_created)

        return BootstrapResult.completed(
            accounts_created=accounts_created,
            accounts_existing=accounts_existing,
            credentials_file=credentials_file,
            console_output_shown=show_console,
        )

    def get_protected_account_list(self) -> List[Dict[str, Any]]:
        """Return metadata about all four protected account definitions."""
        return [
            {
                "username": d["username"],
                "role": d["role"],
                "account_type": d["account_type"],
            }
            for d in PROTECTED_ACCOUNTS
        ]

    def verify_protected_accounts_exist(self) -> Dict[str, Any]:
        """Check which protected accounts exist in the repository."""
        if self._repo is None:
            return {
                "complete": False,
                "existing": [],
                "missing": [d["username"] for d in PROTECTED_ACCOUNTS],
                "error": "Repository not configured",
            }

        existing = []
        missing = []
        for defn in PROTECTED_ACCOUNTS:
            username = defn["username"]
            account = self._repo.get(username)
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
        *,
        username: str,
        show_console: bool = True,
        export_credential: bool = True,
    ) -> Dict[str, Any]:
        """Rotate credentials for a break-glass account."""
        if self._repo is None:
            return {"success": False, "error": "Repository not configured"}

        account = self._repo.get(username)
        if account is None:
            return {"success": False, "error": f"Account '{username}' not found"}

        if not account.is_break_glass:
            return {
                "success": False,
                "error": f"Account '{username}' is not a break-glass account",
            }

        new_password = self._generate_password()
        password_hash, password_salt = self._hasher.hash_with_salt(new_password)
        account.password_hash = password_hash
        account.password_salt = password_salt
        account.updated_at = self._clock()
        account.reset_required = True
        self._repo.upsert(account)

        credentials_file: Optional[str] = None
        if export_credential and self._credentials_dir:
            rotated = CreatedAccount(
                username=username,
                role=account.role,
                account_type="break_glass",
                temporary_password=new_password,
                password_displayed=show_console,
            )
            credentials_file = self._export_credentials([rotated])

        return {
            "success": True,
            "username": username,
            "role": account.role.value,
            "new_password": new_password if show_console else None,
            "credentials_file": credentials_file,
            "rotated_at": self._clock().isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _generate_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^*-_"
        return "".join(
            secrets.choice(alphabet) for _ in range(self.DEFAULT_PASSWORD_LENGTH)
        )

    def _export_credentials(
        self,
        accounts: List[CreatedAccount],
    ) -> Optional[str]:
        if self._credentials_dir is None:
            return None
        cred_dir = Path(self._credentials_dir)
        cred_dir.mkdir(parents=True, exist_ok=True)
        cred_file = cred_dir / self._CREDENTIAL_FILE_NAME

        lines = [
            "=" * 60,
            "PROTECTED ACCOUNT CREDENTIALS",
            "SECURE THIS FILE IMMEDIATELY — DO NOT COMMIT TO VCS",
            "=" * 60,
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "-" * 60,
        ]
        for acc in accounts:
            lines += [
                f"Username: {acc.username}",
                f"Role:     {acc.role.value}",
                f"Type:     {acc.account_type}",
                f"Password: {acc.temporary_password}",
                "-" * 60,
            ]
        lines += [
            "Change these passwords after first login.",
            "=" * 60,
        ]

        cred_file.write_text("\n".join(lines), encoding="utf-8")
        return str(cred_file)


__all__ = [
    "PROTECTED_ACCOUNTS",
    "AccountBootstrapService",
    "BootstrapResult",
    "CreatedAccount",
]
