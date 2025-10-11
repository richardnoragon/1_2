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

# Import main classes for easy access
try:
    # New simplified version for hub integration (preferred)
    # Legacy full-featured version (standalone)
    from .multi_pane_explorer import MultiPaneFileExplorer
    from .multi_pane_explorer_simple import MultiPaneExplorer

    __all__ = ["MultiPaneExplorer", "MultiPaneFileExplorer"]

except ImportError as e:
    # Handle missing dependencies gracefully
    print(f"Warning: Could not import file explorer components: {e}")
    __all__ = []
