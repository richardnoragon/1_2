"""Backward-compatibility shim for the legacy password hasher."""

from __future__ import annotations

import warnings
from typing import Final

from src.core.auth.security import Argon2Parameters, PasswordHasher

_DEFAULT_TIME_COST: Final[int] = 3
_DEFAULT_MEMORY_COST_KIB: Final[int] = 64 * 1024
_DEFAULT_PARALLELISM: Final[int] = 4


class PasswordHashingService(PasswordHasher):
    """Deprecated alias that forwards to :class:`PasswordHasher`."""

    def __init__(
        self,
        *,
        time_cost: int = _DEFAULT_TIME_COST,
        memory_cost: int = _DEFAULT_MEMORY_COST_KIB,
        parallelism: int = _DEFAULT_PARALLELISM,
    ) -> None:
        warnings.warn(
            "PasswordHashingService is deprecated; use"
            " src.core.auth.security.PasswordHasher instead",
            DeprecationWarning,
            stacklevel=2,
        )
        params = Argon2Parameters(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )
        super().__init__(params=params)

    def hash_password(self, password: str) -> str:  # pragma: no cover - shim
        return self.hash(password)


__all__ = ["PasswordHashingService"]
