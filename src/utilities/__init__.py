"""Compatibility namespace for legacy src.utilities imports.

This exposes the current tool packages under the historical src.utilities.* path
without duplicating the implementation tree.
"""

from __future__ import annotations

from pathlib import Path

_TARGET = (Path(__file__).resolve().parent.parent / "tools").resolve()
__path__ = [str(_TARGET)]

__all__ = []
