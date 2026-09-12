"""Backward-compatibility alias for the legacy network_connectivity package name.

The current implementation lives under src/tools/network/network_connectivity_complex,
but older tests and tooling still import it as network_connectivity.
"""

from __future__ import annotations

from pathlib import Path

_TARGET = (Path(__file__).resolve().parent.parent / "src" / "tools" / "network" / "network_connectivity_complex").resolve()
__path__ = [str(_TARGET)]

__all__ = []
