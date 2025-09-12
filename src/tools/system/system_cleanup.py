#!/usr/bin/env python3
"""
System Cleanup GUI for Richard's File Utilities

This module provides a comprehensive system cleanup interface that integrates
with the existing diagnostics framework while providing cleanup-specific functionality.
"""

import sys
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QLabel, QPushButton, QMessageBox, QGroupBox, QGridLayout,
        QProgressBar, QTextEdit, QCheckBox, QSpinBox, QApplication
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("PyQt5 not available. System Cleanup GUI will not be functional.")

# Import the comprehensive SystemDiagnosticsGUI as base class
try:
    # Try absolute import first
    from src.utilities.system.diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI
    DIAGNOSTICS_GUI_AVAILABLE = True
except ImportError:
    try:
        # Try relative import
        from .diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI
        DIAGNOSTICS_GUI_AVAILABLE = True
    except ImportError:
        try:
            # Try alternative relative import
            from .diagnostics_monitoring import SystemDiagnosticsGUI
            DIAGNOSTICS_GUI_AVAILABLE = True
        except ImportError:
            DIAGNOSTICS_GUI_AVAILABLE = False
            if PYQT5_AVAILABLE:
                SystemDiagnosticsGUI = QMainWindow
            else:
                SystemDiagnosticsGUI = object

# Import cleanup tools
try:
    from .system_cleanup.tools.temp_cleaner import TempFilesCleaner
    from .system_cleanup.core.cleanup_base import CleanupOperationResult
    from .system_cleanup.core.safety_manager import SafetyManager
    from .system_cleanup.core.windows_utils import WindowsUtils
    CLEANUP_TOOLS_AVAILABLE = True
except ImportError:
    CLEANUP_TOOLS_AVAILABLE = False
    TempFilesCleaner = None
    CleanupOperationResult = None
    SafetyManager = None
    WindowsUtils = None


class SystemCleanupGUI(SystemDiagnosticsGUI):
    """System Cleanup GUI that extends SystemDiagnosticsGUI with cleanup functionality.
    
    This class provides a specialized interface for system cleanup operations,
    including temporary file removal, cache clearing, and other system optimization tasks.
    """
    
    # Cleanup-specific signals
    cleanup_started = pyqtSignal(str) if PYQT5_AVAILABLE else None
    cleanup_completed = pyqtSignal(str, object) if PYQT5_AVAILABLE else None
    
    def __init__(self, hub_instance=None, parent=None):
        """Initialize the System Cleanup GUI.
        
        Args:
            hub_instance: Optional hub instance for integration
            parent: Parent widget
        """
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 is required for the System Cleanup GUI")
        
        # Initialize the base class - SystemDiagnosticsGUI handles QMainWindow properly
        super().__init__(hub_instance, parent)
        
        # Setup logging
        self.logger = logging.getLogger('RFU.SystemCleanup')
        
        # Cleanup-specific components
        self.cleanup_tools = {}
        self.safety_manager = None
        
        # Initialize cleanup tools
        self.init_cleanup_tools()
        
        # Customize the interface for cleanup
        self.customize_for_cleanup()
    
    def init_cleanup_tools(self):
        """Initialize available cleanup tools."""
        try:
            if CLEANUP_TOOLS_AVAILABLE:
                # Initialize safety manager
                if SafetyManager:
                    self.safety_manager = SafetyManager()
                
                # Initialize cleanup tools
                if TempFilesCleaner:
                    self.cleanup_tools['temp_files'] = TempFilesCleaner()
                
                self.logger.info(f"Initialized {len(self.cleanup_tools)} cleanup tools")
            else:
                self.logger.warning("Cleanup tools not available")
                
        except Exception as e:
            self.logger.error(f"Error initializing cleanup tools: {e}")
    
    def customize_for_cleanup(self):
        """Customize the interface for cleanup operations."""
        try:
            # Update window title
            self.setWindowTitle("System Cleanup - Richard's File Utilities")
            
            # If we have the comprehensive GUI, customize it
            if hasattr(self, 'tab_widget') and self.tab_widget:
                self.add_cleanup_tab()
            
        except Exception as e:
            self.logger.error(f"Error customizing cleanup interface: {e}")
    
    def add_cleanup_tab(self):
        """Add a cleanup tab to the existing interface."""
        try:
            cleanup_widget = QWidget()
            layout = QVBoxLayout(cleanup_widget)
            
            # Header
            header_label = QLabel("System Cleanup Tools")
            header_font = QFont()
            header_font.setPointSize(14)
            header_font.setBold(True)
            header_label.setFont(header_font)
            layout.addWidget(header_label)
            
            # Quick cleanup section
            quick_group = QGroupBox("Quick Cleanup")
            quick_layout = QVBoxLayout(quick_group)
            
            # Temporary files cleanup
            if 'temp_files' in self.cleanup_tools:
                temp_button = QPushButton("Clean Temporary Files")
                temp_button.clicked.connect(self.run_temp_cleanup)
                temp_button.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        font-weight: bold;
                        padding: 10px 20px;
                        border-radius: 5px;
                        margin: 5px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                quick_layout.addWidget(temp_button)
            
            # Placeholder for other tools
            placeholder_label = QLabel("Additional cleanup tools will be available in future updates")
            placeholder_label.setStyleSheet("color: #666666; font-style: italic; margin: 10px;")
            quick_layout.addWidget(placeholder_label)
            
            layout.addWidget(quick_group)
            
            # Results area
            results_group = QGroupBox("Cleanup Results")
            results_layout = QVBoxLayout(results_group)
            
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setMaximumHeight(200)
            self.results_text.setPlainText("No cleanup operations performed yet.")
            results_layout.addWidget(self.results_text)
            
            layout.addWidget(results_group)
            layout.addStretch()
            
            # Add the cleanup tab
            self.tab_widget.addTab(cleanup_widget, "System Cleanup")
            
        except Exception as e:
            self.logger.error(f"Error adding cleanup tab: {e}")
    
    def run_temp_cleanup(self):
        """Run temporary files cleanup."""
        try:
            if 'temp_files' not in self.cleanup_tools:
                QMessageBox.warning(
                    self, "Tool Not Available",
                    "Temporary files cleanup tool is not available."
                )
                return
            
            # Confirm operation
            reply = QMessageBox.question(
                self, "Confirm Cleanup",
                "Are you sure you want to clean temporary files?\n\n"
                "This operation will delete temporary files from system directories.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Update results
            self.results_text.setPlainText("Starting temporary files cleanup...")
            
            # Get the temp cleaner tool
            temp_tool = self.cleanup_tools['temp_files']
            
            # Run cleanup with default parameters
            params = {
                'max_age_days': 0,  # Delete all temp files
                'min_size_bytes': 0,  # All sizes
                'include_system_temp': True,
                'create_backup': False,  # No backup for temp files
                'secure_delete': False  # Fast deletion
            }
            
            # Execute the cleanup
            result = temp_tool.execute_operation(**params)
            
            # Display results
            if result.success:
                results_text = f"Temporary files cleanup completed successfully!\n\n"
                results_text += f"Files deleted: {result.items_processed}\n"
                results_text += f"Space freed: {self._format_size(result.space_freed)}\n"
                results_text += f"Message: {result.message}"
                
                if result.errors:
                    results_text += f"\n\nWarnings/Errors:\n"
                    for error in result.errors:
                        results_text += f"• {error}\n"
            else:
                results_text = f"Temporary files cleanup failed:\n{result.message}\n\n"
                if result.errors:
                    results_text += "Errors:\n"
                    for error in result.errors:
                        results_text += f"• {error}\n"
            
            self.results_text.setPlainText(results_text)
            
            # Show completion message
            QMessageBox.information(
                self, "Cleanup Complete",
                f"Temporary files cleanup completed.\n\n"
                f"Files deleted: {result.items_processed}\n"
                f"Space freed: {self._format_size(result.space_freed)}"
            )
            
        except Exception as e:
            self.logger.error(f"Error running temp cleanup: {e}")
            error_text = f"Error during temporary files cleanup:\n{str(e)}"
            self.results_text.setPlainText(error_text)
            QMessageBox.critical(
                self, "Cleanup Error",
                f"An error occurred during cleanup:\n{str(e)}"
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


def main():
    """Main function for standalone execution."""
    try:
        if not PYQT5_AVAILABLE:
            print("PyQt5 is required to run the System Cleanup GUI.")
            print("Please install PyQt5: pip install PyQt5")
            return
        
        app = QApplication(sys.argv)
        
        # Create and show the GUI
        window = SystemCleanupGUI()
        window.show()
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error running System Cleanup GUI: {e}")


if __name__ == "__main__":
    main()
