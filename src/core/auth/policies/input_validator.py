"""Credential input validation helpers for RFU."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Tuple

from src.core.auth.security.credential_rules import (
    PasswordPolicy,
    PasswordValidationError,
)


class CredentialValidationError(ValueError):
    """Base class for credential validation errors."""


class UsernameValidationError(CredentialValidationError):
    """Raised when a username fails sanitization rules."""


@dataclass(slots=True)
class InputValidator:
    """Sanitize and validate username/password inputs per FR-011."""

    password_policy: PasswordPolicy | None = None

    # Contract accounts use underscores in addition to hyphen separators.
    _USERNAME_PATTERN = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$", re.ASCII)
    _SQL_INJECTION_PATTERN = re.compile(
        r"(--|/\*|\*/|;|\bor\b|\band\b|\bunion\b|\bselect\b|\bdrop\b)",
        re.IGNORECASE,
    )
    _MIN_USERNAME_LENGTH = 3

    def __post_init__(self) -> None:
        if self.password_policy is None:
            self.password_policy = PasswordPolicy()

    def validate_username(self, raw_username: str) -> str:
        """Return a sanitized username or raise UsernameValidationError."""

        if not isinstance(raw_username, str):
            raise UsernameValidationError("Username must be provided as text")
        candidate = raw_username.strip()
        if not candidate:
            raise UsernameValidationError(
                "Username is required and must meet the minimum length"
            )

        lowered = candidate.lower()
        if len(lowered) < self._MIN_USERNAME_LENGTH:
            raise UsernameValidationError(
                (
                    "Username must be at least "
                    f"{self._MIN_USERNAME_LENGTH} characters in length"
                )
            )

        if self._SQL_INJECTION_PATTERN.search(candidate):
            raise UsernameValidationError(
                (
                    "Username contains unsafe patterns that "
                    "resemble injection payloads"
                )
            )

        if not self._USERNAME_PATTERN.fullmatch(lowered):
            raise UsernameValidationError(
                (
                    "Username contains invalid characters; lowercase "
                    "letters, numbers, underscores, and single hyphen "
                    "separators are allowed"
                )
            )

        return lowered

    def validate_password(self, raw_password: str) -> str:
        """Validate *raw_password* using the configured password policy."""

        if raw_password is None:
            raise PasswordValidationError("Password is required")
        assert self.password_policy is not None
        return self.password_policy.validate(raw_password)

    def validate_credentials(self, username: str, password: str) -> Tuple[str, str]:
        """Validate username/password and return sanitized values."""

        return (
            self.validate_username(username),
            self.validate_password(password),
        )


__all__ = [
    "CredentialValidationError",
    "InputValidator",
    "PasswordValidationError",
    "UsernameValidationError",
]
