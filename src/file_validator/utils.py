"""Utility helpers for centralized file validation."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable, Optional, Set


def read_header(path: Path, size: int = 2048) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def normalise_extension(path: Path) -> str:
    return path.suffix.lower()


def guess_mime_type(path: Path) -> Optional[str]:
    mime, _ = mimetypes.guess_type(str(path))
    return mime


def canonicalise_allowed_types(allowed: Iterable[str] | None) -> Set[str]:
    if not allowed:
        return set()
    return {item.lower().lstrip(".") for item in allowed}
