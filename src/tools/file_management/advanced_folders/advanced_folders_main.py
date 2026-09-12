"""
Advanced Folders integration with RFU Hub.

This module provides the main integration point for Advanced Folders
feature within the Richard's File Utilities hub system.
"""

import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from PyQt5.QtWidgets import QApplication

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from .ui.advanced_folders_widget import AdvancedFoldersGUI


def main():
    """Main function for standalone testing."""
    if not PYQT5_AVAILABLE:
        print("PyQt5 is required for the GUI. Please install it with:")
        print("pip install PyQt5")
        return 1

    app = QApplication.instance()
    app_module = getattr(type(app), "__module__", "") if app is not None else ""
    if app is None or app_module.startswith("unittest.mock"):
        app = QApplication(sys.argv)

    # Create and show the Advanced Folders GUI
    try:
        window = AdvancedFoldersGUI()
        window.show()

        if hasattr(app, "exec_"):
            result = app.exec_()
        else:
            result = app.exec()

        if result is None:
            return 0
        if hasattr(result, "__int__") and not isinstance(result, (str, bytes)):
            try:
                return int(result)
            except (TypeError, ValueError):
                return 0
        return int(result)

    except Exception as e:
        print(f"Failed to launch Advanced Folders: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
