#!/usr/bin/env python3
"""Compatibility bridge for the Software Maintenance Toolkit launcher.

This module keeps the historical import path
``src.tools.system.software_maintenance`` working after promoting the real
implementation into the ``src.tools.system.software_maintenance`` package
directory.  We turn this module into a package shim so both legacy imports and
the new package layout stay in sync without breaking tool discovery.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import List

# Expose the package directory so Python treats this module as a package.  This
# allows ``import src.tools.system.software_maintenance.software_maintenance``
# to resolve even though this file remains for backward compatibility.
_package_dir = Path(__file__).with_suffix("")
__path__: List[str] = [str(_package_dir)] if _package_dir.is_dir() else []

# Import the actual GUI class and launcher from the package implementation.
_package = import_module(".software_maintenance", __name__)
SoftwareMaintenanceGUI = _package.SoftwareMaintenanceGUI

_launcher = import_module(
    ".software_maintenance.software_maintenance",
    __name__,
)
main = _launcher.main

__all__ = ["SoftwareMaintenanceGUI", "main"]


if __name__ == "__main__":  # pragma: no cover - manual execution path
    main()
