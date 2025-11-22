"""
RFU File Explorer Package

This package contains the multi-pane file explorer implementation that serves
as an enhanced Total Commander-style interface for Richard's File Utilities.

Components:
- MultiPaneExplorer: Simplified multi-pane interface for hub integration (NEW)
- MultiPaneFileExplorer: Full-featured standalone application window (legacy)
- FileExplorerPane: Individual file explorer pane
- PaneManager: Manages pane creation and layout
- FileOperationManager: Handles file operations with progress tracking
- DriveManager: Cross-platform drive detection
- ToolIntegration: Integration with existing RFU tools

Usage (recommended - simplified version):
    from src.file_explorer import MultiPaneExplorer

    app = QApplication(sys.argv)
    explorer = MultiPaneExplorer()
    explorer.show()
    app.exec_()

Usage (legacy - full version):
    from src.file_explorer import MultiPaneFileExplorer

    app = QApplication(sys.argv)
    explorer = MultiPaneFileExplorer()
    explorer.show()
    app.exec_()
"""

__version__ = "1.0.0"
__author__ = "Richard Noragon"

# Import exposure is intentionally lazy to avoid loading the heavy multi-pane
# explorer modules during package import (the hub only needs lightweight models
# such as ``HubInterfaceMode`` during startup).  Eagerly importing the explorer
# implementations caused the application to traverse the entire bookmark
# subsystem before the GUI even appeared, which now manifests as the
# KeyboardInterrupt stack trace reported in issue #RFU-189.

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["MultiPaneExplorer", "MultiPaneFileExplorer"]


if TYPE_CHECKING:  # pragma: no cover - type checkers resolve real classes
    from .multi_pane_explorer import MultiPaneFileExplorer as _MultiPaneFileExplorer
    from .multi_pane_explorer_simple import MultiPaneExplorer as _MultiPaneExplorer


def __getattr__(name: str) -> Any:
    """Lazily resolve explorer entry points on first access."""

    if name == "MultiPaneExplorer":
        module = import_module("src.file_explorer.multi_pane_explorer_simple")
        return getattr(module, name)
    if name == "MultiPaneFileExplorer":
        module = import_module("src.file_explorer.multi_pane_explorer")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
