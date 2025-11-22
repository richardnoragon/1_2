"""Shared CLI response helpers for admin scripts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CommandResult:
    """Simple container mirroring CLI exit semantics.

    Integration tests only depend on ``exit_code`` and ``payload`` so keeping
    this lightweight avoids coupling to argparse or click.
    """

    exit_code: int
    payload: Any | None = None
    error: str | None = None


__all__ = ["CommandResult"]
