#!/usr/bin/env python3
"""
RFU Multi-Pane File Explorer - Main Entry Point

This replaces the dialog-based hub with a sophisticated file explorer interface
similar to Total Commander but cross-platform and fully integrated with RFU tools.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from PyQt5.QtCore import QSettings, Qt
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QMessageBox

    # Import the multi-pane explorer
    from src.rfu.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure PyQt5 is properly installed:")
    print("  pip install PyQt5")
    sys.exit(1)


def setup_application() -> QApplication:
    """Setup and configure the QApplication."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("RFU Multi-Pane Explorer")
    app.setApplicationDisplayName("Richard's File Utilities - File Explorer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RFU")
    app.setOrganizationDomain("rfu.local")
    
    # Set application icon if available
    icon_path = project_root / "assets" / "images" / "rfu_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    return app


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    try:
        # Check if database is accessible
        from scripts.maintenance.standalone_database_manager import \
            get_database_manager
        db_manager = get_database_manager()
        if db_manager is None:
            print("Warning: Database manager not available. Some features may be limited.")
            return True  # Continue without database
            
        # Check if configuration system is available
        from src.rfu.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        return True
        
    except ImportError as e:
        print(f"Missing required components: {e}")
        return False


def main():
    """Main entry point for the RFU Multi-Pane File Explorer."""
    print("Starting RFU Multi-Pane File Explorer...")
    
    # Check prerequisites
    if not check_prerequisites():
        print("Prerequisites check failed. Please ensure all components are properly installed.")
        return 1
    
    # Setup application
    app = setup_application()
    
    try:
        # Create and show the main explorer window
        explorer = MultiPaneFileExplorer()
        explorer.show()
        
        # Center window on screen
        screen_geometry = app.desktop().availableGeometry()
        window_geometry = explorer.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        explorer.move(window_geometry.topLeft())
        
        print("RFU Multi-Pane File Explorer started successfully.")
        print("Features:")
        print("  • 1-4 configurable file explorer panes")
        print("  • Cross-platform compatibility")
        print("  • Integrated access to all RFU tools")
        print("  • Advanced file operations with progress tracking")
        print("  • Customizable color schemes and layouts")
        print("  • Bookmark and favorites management")
        print()
        print("Use Ctrl+1/2/3/4 to switch between pane configurations")
        print("Use F1 for help and documentation")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"Error starting RFU Multi-Pane File Explorer: {e}")
        
        # Show error dialog if GUI is available
        try:
            QMessageBox.critical(
                None,
                "RFU Explorer Error",
                f"Failed to start RFU Multi-Pane File Explorer:\n\n{e}\n\n"
                f"Please check the installation and try again."
            )
        except:
            pass
            
        return 1


if __name__ == '__main__':
    sys.exit(main())