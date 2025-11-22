"""Password policy helpers for FR-011 credential validation."""

from __future__ import annotations

import string
from dataclasses import dataclass, field
from typing import Iterable, Set


class PasswordValidationError(ValueError):
    """Raised when a password violates the configured security policy."""


@dataclass(slots=True)
class PasswordPolicy:
    """Configurable password policy enforcing FR-011 requirements.

    Args:
        min_length: Minimum password length.
        required_classes: Number of distinct character classes that must be present
            (lowercase, uppercase, digit, symbol).
        breached_passwords: Optional iterable of known-compromised passwords.
    """

    min_length: int = 12
    required_classes: int = 3
    breached_passwords: Iterable[str] | None = None
    _denylist: Set[str] = field(init=False, repr=False, default_factory=set)

    def __post_init__(self) -> None:
        if self.min_length < 1:
            raise ValueError("Password min_length must be positive")
        if self.required_classes < 1:
            raise ValueError("required_classes must be positive")
        if self.breached_passwords is not None:
            self._denylist = {
                value.strip().lower() for value in self.breached_passwords if value
            }
        else:
            self._denylist = set()

    def validate(self, candidate: str) -> str:
        """Validate *candidate* against the configured policy."""

        if not isinstance(candidate, str):
            raise PasswordValidationError("Password must be supplied as text")

        password = candidate.strip()
        if len(password) < self.min_length:
            raise PasswordValidationError(
                f"Password must be at least {self.min_length} characters in length"
            )

        classes = self._count_character_classes(password)
        if classes < self.required_classes:
            raise PasswordValidationError(
                (
                    "Password must include at least "
                    f"{self.required_classes} character classes (upper, "
                    "lower, digit, symbol) while meeting the minimum length "
                    f"of {self.min_length} characters"
                )
            )

        if self._denylist and password.lower() in self._denylist:
            raise PasswordValidationError("Password appears in the breach denylist")

        return password

    def is_breached(self, candidate: str) -> bool:
        """Return True when *candidate* appears in the configured denylist."""

        if not self._denylist:
            return False
        return candidate.lower() in self._denylist

    @staticmethod
    def _count_character_classes(password: str) -> int:
        has_lower = any(char.islower() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_symbol = any(PasswordPolicy._is_symbol(char) for char in password)

        return sum([has_lower, has_upper, has_digit, has_symbol])

    @staticmethod
    def _is_symbol(char: str) -> bool:
        if char in string.punctuation:
            return True
        # Treat whitespace as a symbol to discourage space-only passwords.
        return char.isspace()


__all__ = ["PasswordPolicy", "PasswordValidationError"]
