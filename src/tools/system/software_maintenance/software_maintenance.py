#!/usr/bin/env python3
"""Software Maintenance Toolkit launcher.

This module provides a standalone entry point for the Software Maintenance
Toolkit, ensuring the graphical interface can be started directly from the
package directory.
"""

from __future__ import annotations

try:
    from . import SoftwareMaintenanceGUI
except ImportError as import_error:  # pragma: no cover - defensive guard
    raise ImportError(
        "Software Maintenance Toolkit GUI is unavailable."
        " Ensure all dependencies are installed."
    ) from import_error


def main() -> None:
    """Launch the Software Maintenance Toolkit GUI."""
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = SoftwareMaintenanceGUI()
    window.setWindowTitle("Software Maintenance Toolkit - Richard's File Utilities")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
