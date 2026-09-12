"""Backward-compatibility alias for the legacy utilities package name.

The project moved tool implementations under src/tools/<category>, but older
integration tests expect imports via the top-level utilities package.
"""

from __future__ import annotations

from pathlib import Path

_TARGET = (Path(__file__).resolve().parent.parent / "src" / "tools").resolve()
__path__ = [str(_TARGET)]

__all__ = []
