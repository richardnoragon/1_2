#!/usr/bin/env python3
"""Compatibility wrapper for advanced System Cleanup GUI."""

from src.tools.system.system_cleanup import system_cleanup_gui as _system_cleanup_gui

CleanupWorker = _system_cleanup_gui.CleanupWorker
SystemCleanupGUI = _system_cleanup_gui.SystemCleanupGUI

__all__ = ["CleanupWorker", "SystemCleanupGUI"]


def __getattr__(name):
    """Proxy attribute access to the relocated implementation."""
    return getattr(_system_cleanup_gui, name)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = SystemCleanupGUI()
    window.show()
    sys.exit(app.exec_())
