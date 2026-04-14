#!/usr/bin/env python3
"""
RFU Multi-Pane File Explorer - Entry Point

This is the standalone entry point for the RFU Multi-Pane File Explorer interface.
It provides a comprehensive Total Commander-style file management interface
with full integration to Richard's File Utilities tool ecosystem.

Features:
- 1-4 configurable file explorer panes
- Tool Bookmark navigation pane (left sidebar)
- Preview/properties information pane (right sidebar)
- Complete application menu bar with RFU tool integration
- Cross-platform file operations with drag-and-drop
- Customizable layouts and responsive design
- Advanced file operations and tool launching
"""

import logging
import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, "src"))


def setup_logging():
    """Setup logging for the multi-pane explorer."""
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("rfu_explorer.log", encoding="utf-8"),
            ],
        )
        logger = logging.getLogger("RFU.Explorer")
        logger.info("RFU Multi-Pane File Explorer logging initialized")
        return logger
    except Exception as e:
        print(f"Warning: Could not setup logging: {e}")
        return logging.getLogger("RFU.Explorer")


def main():
    """Main entry point for RFU Multi-Pane File Explorer."""
    logger = setup_logging()

    try:
        # Import PyQt5 components
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication, QMessageBox

        logger.info("Starting RFU Multi-Pane File Explorer...")

        # Enable HiDPI scaling (A11Y-5) — must be set before QApplication.
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("RFU Multi-Pane File Explorer")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Richard's File Utilities")

        # Import and create the multi-pane explorer with new architecture
        try:
            from src.file_explorer.explorer_controller import (
                ExplorerMainWindow,
            )

            # Create main window with enterprise-grade architecture
            explorer = ExplorerMainWindow()

            # Set window properties
            explorer.setWindowTitle("RFU Multi-Pane File Explorer - Enterprise Edition")

            # Show the window
            explorer.show()

            logger.info("Enterprise multi-pane explorer launched successfully")
            logger.info("New architecture features:")
            logger.info("  • Component Guardian protection against GUI degradation")
            logger.info("  • Separated concerns with specialized managers")
            logger.info("  • Robust error handling and automatic recovery")
            logger.info("  • Clean import strategies with fallback mechanisms")
            logger.info("  • Enterprise-grade widget lifecycle management")
            logger.info("  • Comprehensive monitoring and health checks")

            # Start the application event loop
            return app.exec_()

        except ImportError as ie:
            logger.error(f"Failed to import ExplorerMainWindow: {ie}")
            logger.info("Falling back to legacy multi-pane explorer")

            try:
                from src.file_explorer.multi_pane_explorer import (
                    MultiPaneFileExplorer,
                )

                explorer = MultiPaneFileExplorer()
                explorer.setWindowTitle("RFU Multi-Pane File Explorer - Legacy Mode")
                explorer.show()

                logger.warning("Using legacy explorer due to import failure")
                return app.exec_()

            except ImportError as legacy_ie:
                QMessageBox.critical(
                    None,
                    "Import Error",
                    f"Could not import explorer components:\n\n{legacy_ie}\n\n"
                    "Please ensure all required dependencies are installed.",
                )
                return 1

        except Exception as e:
            logger.error(f"Error creating multi-pane explorer: {e}")
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to create the multi-pane explorer:\n\n{e}\n\n"
                "Please check the logs for more details.",
            )
            return 1

    except ImportError as ie:
        logger.error(f"PyQt5 import error: {ie}")
        print("ERROR: PyQt5 is not available.")
        print("Please install PyQt5 with: pip install PyQt5")
        return 1

    except Exception as e:
        logger.error(f"Critical error starting application: {e}")
        print(f"CRITICAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    """Direct execution entry point."""
    print("=" * 60)
    print("RFU Multi-Pane File Explorer")
    print("Complete interface with all components")
    print("=" * 60)

    exit_code = main()

    if exit_code == 0:
        print("RFU Multi-Pane File Explorer closed successfully.")
    else:
        print(f"RFU Multi-Pane File Explorer exited with code: {exit_code}")

    sys.exit(exit_code)
