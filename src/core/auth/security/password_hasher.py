"""Argon2id hashing helpers aligned with Phase 3.5 research settings."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass
from typing import Iterable, Tuple

from argon2 import PasswordHasher as _PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from argon2.low_level import Type as Argon2Type
from argon2.low_level import hash_secret


@dataclass(frozen=True, slots=True)
class Argon2Parameters:
    """Parameter bundle mirroring the research.md defaults."""

    time_cost: int = 3
    memory_cost: int = 64 * 1024
    parallelism: int = 4
    hash_len: int = 32
    salt_len: int = 16

    def as_kwargs(self) -> dict[str, int]:
        return {
            "time_cost": self.time_cost,
            "memory_cost": self.memory_cost,
            "parallelism": self.parallelism,
            "hash_len": self.hash_len,
            "salt_len": self.salt_len,
        }


class PasswordHasher:
    """Argon2id wrapper that centralizes normalize/hash/verify helpers."""

    def __init__(
        self,
        *,
        params: Argon2Parameters | None = None,
        encoding: str = "utf-8",
    ) -> None:
        self._params = params or Argon2Parameters()
        self._encoding = encoding
        self._hasher = _PasswordHasher(
            **self._params.as_kwargs(),
            type=Argon2Type.ID,
        )

    # ------------------------------------------------------------------
    def hash(self, password: str) -> str:
        normalized = self._normalize(password)
        return self._hasher.hash(normalized)

    def hash_with_salt(
        self,
        password: str,
        *,
        salt: bytes | None = None,
    ) -> Tuple[str, bytes]:
        normalized = self._normalize(password)
        salt_bytes = salt or secrets.token_bytes(self._params.salt_len)
        digest = hash_secret(
            normalized.encode(self._encoding),
            salt_bytes,
            time_cost=self._params.time_cost,
            memory_cost=self._params.memory_cost,
            parallelism=self._params.parallelism,
            hash_len=self._params.hash_len,
            type=Argon2Type.ID,
        )
        return digest.decode(self._encoding), salt_bytes

    def verify(
        self,
        hashed_password: str,
        candidate: str,
        *,
        raise_on_error: bool = False,
    ) -> bool:
        normalized = self._normalize(candidate)
        try:
            return self._hasher.verify(hashed_password, normalized)
        except (VerifyMismatchError, InvalidHash):
            if raise_on_error:
                raise
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        try:
            return self._hasher.check_needs_rehash(hashed_password)
        except InvalidHash:
            return True

    @staticmethod
    def generate_temporary_password(
        length: int = 16,
        *,
        alphabet: Iterable[str] | None = None,
    ) -> str:
        pool = (
            "".join(alphabet)
            if alphabet is not None
            else string.ascii_letters + string.digits + "!@#$%^*-_"
        )
        if length < 1:
            raise ValueError("length must be positive")
        return "".join(secrets.choice(pool) for _ in range(length))

    def _normalize(self, password: str) -> str:
        if not isinstance(password, str):
            raise TypeError("Password must be provided as text")
        candidate = password.strip()
        if not candidate:
            raise ValueError("Password cannot be empty")
        return candidate


__all__ = ["Argon2Parameters", "PasswordHasher"]
