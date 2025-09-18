"""
RFU File Explorer Package

This package contains the multi-pane file explorer implementation that serves
as an enhanced Total Commander-style interface for Richard's File Utilities.

Components:
- MultiPaneFileExplorer: Main application window
- FileExplorerPane: Individual file explorer pane
- PaneManager: Manages pane creation and layout
- FileOperationManager: Handles file operations with progress tracking
- DriveManager: Cross-platform drive detection
- ToolIntegration: Integration with existing RFU tools

Usage:
    from src.rfu.file_explorer import MultiPaneFileExplorer
    
    app = QApplication(sys.argv)
    explorer = MultiPaneFileExplorer()
    explorer.show()
    app.exec_()
"""

__version__ = "1.0.0"
__author__ = "Richard Noragon"

# Import main classes for easy access
try:
    from .multi_pane_explorer import MultiPaneFileExplorer
    
    __all__ = [
        'MultiPaneFileExplorer'
    ]
    
except ImportError:
    # Handle missing dependencies gracefully
    __all__ = []