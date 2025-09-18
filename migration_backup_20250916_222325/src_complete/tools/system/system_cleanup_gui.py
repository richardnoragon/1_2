#!/usr/bin/env python3
"""
System Cleanup GUI for Richard's File Utilities

This module provides a comprehensive system cleanup interface that inherits
from SystemDiagnosticsGUI and integrates all available cleanup tools with
safety features and progress tracking.
"""

import sys
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QLabel, QPushButton, QStatusBar, QMessageBox, QSplitter,
        QGroupBox, QGridLayout, QProgressBar, QTextEdit, QFrame,
        QApplication, QMenuBar, QAction, QCheckBox, QSpinBox,
        QComboBox, QListWidget, QListWidgetItem, QScrollArea,
        QFileDialog
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
    from PyQt5.QtGui import QFont, QIcon, QPixmap
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Create dummy classes for when PyQt5 is not available
    QMainWindow = type('QMainWindow', (), {})
    QObject = type('QObject', (), {})
    pyqtSignal = type('pyqtSignal', (), {'__init__': lambda self, *args: None})
    QWidget = type('QWidget', (), {})
    QVBoxLayout = type('QVBoxLayout', (), {})
    QHBoxLayout = type('QHBoxLayout', (), {})
    QTabWidget = type('QTabWidget', (), {})
    QLabel = type('QLabel', (), {})
    QPushButton = type('QPushButton', (), {})
    QGroupBox = type('QGroupBox', (), {})
    QGridLayout = type('QGridLayout', (), {})
    QProgressBar = type('QProgressBar', (), {})
    QTextEdit = type('QTextEdit', (), {})
    QFrame = type('QFrame', (), {})
    QCheckBox = type('QCheckBox', (), {})
    QSpinBox = type('QSpinBox', (), {})
    QScrollArea = type('QScrollArea', (), {})
    QMessageBox = type('QMessageBox', (), {})
    QFileDialog = type('QFileDialog', (), {})

# Import the comprehensive SystemDiagnosticsGUI as base class
try:
    from .diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI
    DIAGNOSTICS_GUI_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_GUI_AVAILABLE = False
    SystemDiagnosticsGUI = QMainWindow

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


class CleanupWorker(QObject):
    """Worker thread for running cleanup operations."""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)       # CleanupOperationResult
    error_occurred = pyqtSignal(str)              # error message
    
    def __init__(self, cleanup_tool, operation_params):
        super().__init__()
        self.cleanup_tool = cleanup_tool
        self.operation_params = operation_params
        self._should_stop = False
    
    def run(self):
        """Run the cleanup operation."""
        try:
            # Connect tool signals to worker signals
            if hasattr(self.cleanup_tool, 'progress_updated'):
                self.cleanup_tool.progress_updated.connect(self.progress_updated)
            if hasattr(self.cleanup_tool, 'error_occurred'):
                self.cleanup_tool.error_occurred.connect(self.error_occurred)
            
            # Execute the operation
            result = self.cleanup_tool.execute_operation(**self.operation_params)
            self.operation_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"Cleanup operation failed: {str(e)}")
    
    def stop(self):
        """Request to stop the operation."""
        self._should_stop = True
        if hasattr(self.cleanup_tool, 'stop_operation'):
            self.cleanup_tool.stop_operation()


class SystemCleanupGUI(SystemDiagnosticsGUI):
    """Comprehensive System Cleanup GUI with integrated cleanup tools.
    
    This class inherits from SystemDiagnosticsGUI and provides a specialized
    interface for system cleanup operations, including temporary file removal,
    cache clearing, registry cleaning, and other system optimization tasks.
    """
    
    # Additional signals for cleanup operations
    cleanup_started = pyqtSignal(str)  # tool_name
    cleanup_completed = pyqtSignal(str, object)  # tool_name, result
    cleanup_progress = pyqtSignal(str, int, str)  # tool_name, percentage, message
    
    def __init__(self, hub_instance=None, parent=None):
        """Initialize the System Cleanup GUI.
        
        Args:
            hub_instance: Optional hub instance for integration
            parent: Parent widget
        """
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 is required for the System Cleanup GUI")
        
        if not DIAGNOSTICS_GUI_AVAILABLE:
            raise ImportError("SystemDiagnosticsGUI is required as base class")
        
        # Initialize the base class
        super().__init__(hub_instance, parent)
        
        # Setup logging
        self.logger = logging.getLogger('RFU.SystemCleanup')
        
        # Cleanup-specific components
        self.cleanup_tools = {}
        self.safety_manager = None
        self.current_worker = None
        self.current_thread = None
        
        # Initialize cleanup tools
        self.init_cleanup_tools()
        
        # Override window title and customize UI
        self.setWindowTitle("System Cleanup - Richard's File Utilities")
        self.customize_cleanup_interface()
        
        # Connect cleanup-specific signals
        self.setup_cleanup_signals()
    
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
                
                # TODO: Add other cleanup tools as they become available
                # self.cleanup_tools['registry'] = RegistryCleaner()
                # self.cleanup_tools['cache'] = CacheCleaner()
                # self.cleanup_tools['logs'] = LogCleaner()
                
                self.logger.info(f"Initialized {len(self.cleanup_tools)} cleanup tools")
            else:
                self.logger.warning("Cleanup tools not available")
                
        except Exception as e:
            self.logger.error(f"Error initializing cleanup tools: {e}")
    
    def customize_cleanup_interface(self):
        """Customize the interface for cleanup operations."""
        try:
            # Clear existing tabs and create cleanup-specific tabs
            self.tab_widget.clear()
            
            # Create cleanup-specific tabs
            self.create_quick_cleanup_tab()
            self.create_advanced_cleanup_tab()
            self.create_safety_backup_tab()
            self.create_cleanup_results_tab()
            
            # Update header section
            self.update_header_for_cleanup()
            
        except Exception as e:
            self.logger.error(f"Error customizing cleanup interface: {e}")
    
    def update_header_for_cleanup(self):
        """Update the header section for cleanup operations."""
        try:
            # Find and update the header widget
            central_widget = self.centralWidget()
            if central_widget:
                layout = central_widget.layout()
                if layout and layout.count() > 0:
                    # Get the header widget (first item)
                    header_item = layout.itemAt(0)
                    if header_item:
                        header_widget = header_item.widget()
                        if isinstance(header_widget, QFrame):
                            # Update title and description
                            header_layout = header_widget.layout()
                            if header_layout:
                                title_layout = header_layout.itemAt(0)
                                if title_layout:
                                    title_widget = title_layout.itemAt(0)
                                    if title_widget:
                                        title_label = title_widget.widget()
                                        if isinstance(title_label, QLabel):
                                            title_label.setText("System Cleanup & Optimization")
                                    
                                    desc_widget = title_layout.itemAt(1)
                                    if desc_widget:
                                        desc_label = desc_widget.widget()
                                        if isinstance(desc_label, QLabel):
                                            desc_label.setText("Comprehensive system cleanup and optimization tools")
        except Exception as e:
            self.logger.error(f"Error updating header: {e}")
    
    def create_quick_cleanup_tab(self):
        """Create the quick cleanup tab with common operations."""
        try:
            quick_widget = QWidget()
            layout = QVBoxLayout(quick_widget)
            
            # Quick cleanup section
            quick_group = QGroupBox("Quick Cleanup")
            quick_layout = QVBoxLayout(quick_group)
            
            # Quick cleanup options
            self.quick_cleanup_options = {}
            
            # Temporary files cleanup
            temp_checkbox = QCheckBox("Clean Temporary Files")
            temp_checkbox.setChecked(True)
            temp_checkbox.setToolTip("Remove temporary files from system and user temp directories")
            self.quick_cleanup_options['temp_files'] = temp_checkbox
            quick_layout.addWidget(temp_checkbox)
            
            # Cache cleanup (placeholder for future implementation)
            cache_checkbox = QCheckBox("Clear Application Caches")
            cache_checkbox.setToolTip("Clear application and system caches (Coming Soon)")
            cache_checkbox.setEnabled(False)  # Disabled until implemented
            self.quick_cleanup_options['cache'] = cache_checkbox
            quick_layout.addWidget(cache_checkbox)
            
            # Windows logs cleanup (placeholder)
            logs_checkbox = QCheckBox("Clean Windows Logs")
            logs_checkbox.setToolTip("Remove old Windows system and application logs (Coming Soon)")
            logs_checkbox.setEnabled(False)  # Disabled until implemented
            self.quick_cleanup_options['logs'] = logs_checkbox
            quick_layout.addWidget(logs_checkbox)
            
            layout.addWidget(quick_group)
            
            # Quick cleanup controls
            controls_group = QGroupBox("Quick Cleanup Controls")
            controls_layout = QHBoxLayout(controls_group)
            
            # Estimate button
            self.estimate_button = QPushButton("Estimate Space to Free")
            self.estimate_button.clicked.connect(self.estimate_quick_cleanup)
            controls_layout.addWidget(self.estimate_button)
            
            # Run quick cleanup button
            self.quick_cleanup_button = QPushButton("Run Quick Cleanup")
            self.quick_cleanup_button.clicked.connect(self.run_quick_cleanup)
            self.quick_cleanup_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            controls_layout.addWidget(self.quick_cleanup_button)
            
            layout.addWidget(controls_group)
            
            # Quick cleanup results
            results_group = QGroupBox("Cleanup Estimate")
            results_layout = QVBoxLayout(results_group)
            
            self.quick_results_text = QTextEdit()
            self.quick_results_text.setMaximumHeight(150)
            self.quick_results_text.setReadOnly(True)
            self.quick_results_text.setPlainText("Click 'Estimate Space to Free' to see potential cleanup results.")
            results_layout.addWidget(self.quick_results_text)
            
            layout.addWidget(results_group)
            layout.addStretch()
            
            self.tab_widget.addTab(quick_widget, "Quick Cleanup")
            
        except Exception as e:
            self.logger.error(f"Error creating quick cleanup tab: {e}")
    
    def create_advanced_cleanup_tab(self):
        """Create the advanced cleanup tab with detailed options."""
        try:
            advanced_widget = QWidget()
            layout = QVBoxLayout(advanced_widget)
            
            # Create scroll area for advanced options
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            # Temporary Files Advanced Options
            if 'temp_files' in self.cleanup_tools:
                temp_group = self.create_temp_files_advanced_group()
                scroll_layout.addWidget(temp_group)
            
            # Placeholder for other advanced tools
            placeholder_group = QGroupBox("Additional Cleanup Tools")
            placeholder_layout = QVBoxLayout(placeholder_group)
            placeholder_label = QLabel("Additional cleanup tools will be available in future updates:")
            placeholder_label.setStyleSheet("color: #666666; font-style: italic;")
            placeholder_layout.addWidget(placeholder_label)
            
            tools_list = QLabel("• Registry Cleaner\n• Cache Cleaner\n• Log Files Cleaner\n• Restore Points Manager\n• Memory Dumps Cleaner")
            tools_list.setStyleSheet("color: #666666; margin-left: 20px;")
            placeholder_layout.addWidget(tools_list)
            
            scroll_layout.addWidget(placeholder_group)
            scroll_layout.addStretch()
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            
            self.tab_widget.addTab(advanced_widget, "Advanced Tools")
            
        except Exception as e:
            self.logger.error(f"Error creating advanced cleanup tab: {e}")
    
    def create_temp_files_advanced_group(self) -> QGroupBox:
        """Create advanced options group for temporary files cleanup."""
        temp_group = QGroupBox("Temporary Files - Advanced Options")
        temp_layout = QGridLayout(temp_group)
        
        # Age filter
        temp_layout.addWidget(QLabel("Delete files older than (days):"), 0, 0)
        self.temp_age_spinbox = QSpinBox()
        self.temp_age_spinbox.setRange(0, 365)
        self.temp_age_spinbox.setValue(0)
        self.temp_age_spinbox.setToolTip("0 = delete all temp files, >0 = only delete files older than specified days")
        temp_layout.addWidget(self.temp_age_spinbox, 0, 1)
        
        # Size filter
        temp_layout.addWidget(QLabel("Minimum file size (MB):"), 1, 0)
        self.temp_size_spinbox = QSpinBox()
        self.temp_size_spinbox.setRange(0, 1000)
        self.temp_size_spinbox.setValue(0)
        self.temp_size_spinbox.setToolTip("0 = delete all sizes, >0 = only delete files larger than specified MB")
        temp_layout.addWidget(self.temp_size_spinbox, 1, 1)
        
        # Include system temp
        self.temp_system_checkbox = QCheckBox("Include system temp directories")
        self.temp_system_checkbox.setChecked(True)
        self.temp_system_checkbox.setToolTip("Include Windows system temp directories (may require admin privileges)")
        temp_layout.addWidget(self.temp_system_checkbox, 2, 0, 1, 2)
        
        # Create backup
        self.temp_backup_checkbox = QCheckBox("Create backup before deletion")
        self.temp_backup_checkbox.setChecked(False)
        self.temp_backup_checkbox.setToolTip("Create backup of files before deletion (uses additional disk space)")
        temp_layout.addWidget(self.temp_backup_checkbox, 3, 0, 1, 2)
        
        # Secure delete
        self.temp_secure_checkbox = QCheckBox("Secure deletion (overwrite data)")
        self.temp_secure_checkbox.setChecked(False)
        self.temp_secure_checkbox.setToolTip("Securely overwrite file data before deletion (slower but more secure)")
        temp_layout.addWidget(self.temp_secure_checkbox, 4, 0, 1, 2)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        preview_button = QPushButton("Preview Temp Files Cleanup")
        preview_button.clicked.connect(self.preview_temp_cleanup)
        button_layout.addWidget(preview_button)
        
        execute_button = QPushButton("Execute Temp Files Cleanup")
        execute_button.clicked.connect(self.execute_temp_cleanup)
        execute_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(execute_button)
        
        temp_layout.addLayout(button_layout, 5, 0, 1, 2)
        
        return temp_group
    
    def create_safety_backup_tab(self):
        """Create the safety and backup management tab."""
        try:
            safety_widget = QWidget()
            layout = QVBoxLayout(safety_widget)
            
            # Safety settings
            safety_group = QGroupBox("Safety Settings")
            safety_layout = QVBoxLayout(safety_group)
            
            # Create restore point
            self.restore_point_checkbox = QCheckBox("Create system restore point before cleanup")
            self.restore_point_checkbox.setChecked(True)
            self.restore_point_checkbox.setToolTip("Create a system restore point before performing cleanup operations")
            safety_layout.addWidget(self.restore_point_checkbox)
            
            # Backup important files
            self.backup_files_checkbox = QCheckBox("Backup important files before deletion")
            self.backup_files_checkbox.setChecked(True)
            self.backup_files_checkbox.setToolTip("Create backups of important files before deletion")
            safety_layout.addWidget(self.backup_files_checkbox)
            
            # Confirmation dialogs
            self.confirm_operations_checkbox = QCheckBox("Show confirmation dialogs for destructive operations")
            self.confirm_operations_checkbox.setChecked(True)
            self.confirm_operations_checkbox.setToolTip("Show confirmation dialogs before performing potentially destructive operations")
            safety_layout.addWidget(self.confirm_operations_checkbox)
            
            layout.addWidget(safety_group)
            
            # Backup management
            backup_group = QGroupBox("Backup Management")
            backup_layout = QVBoxLayout(backup_group)
            
            # Backup location
            backup_info_layout = QHBoxLayout()
            backup_info_layout.addWidget(QLabel("Backup Location:"))
            self.backup_location_label = QLabel("Not initialized")
            if self.safety_manager:
                self.backup_location_label.setText(str(self.safety_manager.session_backup_dir))
            backup_info_layout.addWidget(self.backup_location_label)
            backup_layout.addLayout(backup_info_layout)
            
            # Backup actions
            backup_actions_layout = QHBoxLayout()
            
            view_backups_button = QPushButton("View Backups")
            view_backups_button.clicked.connect(self.view_backups)
            backup_actions_layout.addWidget(view_backups_button)
            
            cleanup_backups_button = QPushButton("Cleanup Old Backups")
            cleanup_backups_button.clicked.connect(self.cleanup_old_backups)
            backup_actions_layout.addWidget(cleanup_backups_button)
            
            restore_backups_button = QPushButton("Restore All Backups")
            restore_backups_button.clicked.connect(self.restore_all_backups)
            restore_backups_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            backup_actions_layout.addWidget(restore_backups_button)
            
            backup_layout.addLayout(backup_actions_layout)
            
            layout.addWidget(backup_group)
            
            # System information
            system_group = QGroupBox("System Information")
            system_layout = QVBoxLayout(system_group)
            
            self.system_info_text = QTextEdit()
            self.system_info_text.setReadOnly(True)
            self.system_info_text.setMaximumHeight(200)
            self.update_system_info_display()
            system_layout.addWidget(self.system_info_text)
            
            layout.addWidget(system_group)
            layout.addStretch()
            
            self.tab_widget.addTab(safety_widget, "Safety & Backups")
            
        except Exception as e:
            self.logger.error(f"Error creating safety backup tab: {e}")
    
    def create_cleanup_results_tab(self):
        """Create the cleanup results and reports tab."""
        try:
            results_widget = QWidget()
            layout = QVBoxLayout(results_widget)
            
            # Current operation status
            status_group = QGroupBox("Current Operation Status")
            status_layout = QVBoxLayout(status_group)
            
            # Progress bar
            self.cleanup_progress_bar = QProgressBar()
            self.cleanup_progress_bar.setVisible(False)
            status_layout.addWidget(self.cleanup_progress_bar)
            
            # Status label
            self.cleanup_status_label = QLabel("No cleanup operation in progress")
            status_layout.addWidget(self.cleanup_status_label)
            
            # Stop button
            self.stop_cleanup_button = QPushButton("Stop Current Operation")
            self.stop_cleanup_button.clicked.connect(self.stop_current_cleanup)
            self.stop_cleanup_button.setVisible(False)
            self.stop_cleanup_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            status_layout.addWidget(self.stop_cleanup_button)
            
            layout.addWidget(status_group)
            
            # Results display
            results_group = QGroupBox("Cleanup Results")
            results_layout = QVBoxLayout(results_group)
            
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setPlainText("No cleanup operations performed yet.")
            results_layout.addWidget(self.results_text)
            
            # Export results button
            export_button = QPushButton("Export Results Report")
            export_button.clicked.connect(self.export_results_report)
            results_layout.addWidget(export_button)
            
            layout.addWidget(results_group)
            
            self.tab_widget.addTab(results_widget, "Results & Reports")
            
        except Exception as e:
            self.logger.error(f"Error creating cleanup results tab: {e}")
    
    def setup_cleanup_signals(self):
        """Setup cleanup-specific signal connections."""
        try:
            # Connect cleanup signals to update UI
            self.cleanup_started.connect(self.on_cleanup_started)
            self.cleanup_completed.connect(self.on_cleanup_completed)
            self.cleanup_progress.connect(self.on_cleanup_progress)
            
        except Exception as e:
            self.logger.error(f"Error setting up cleanup signals: {e}")
    
    def estimate_quick_cleanup(self):
        """Estimate space that can be freed by quick cleanup."""
        try:
            self.quick_results_text.setPlainText("Estimating cleanup size...")
            
            total_size = 0
            results = []
            
            # Estimate temp files if selected
            if (self.quick_cleanup_options['temp_files'].isChecked() and 
                'temp_files' in self.cleanup_tools):
                
                temp_tool = self.cleanup_tools['temp_files']
                temp_size = temp_tool.estimate_cleanup_size(
                    max_age_days=0,
                    min_size_bytes=0,
                    include_system_temp=True
                )
                
                total_size += temp_size
                results.append(f"Temporary Files: {self._format_size(temp_size)}")
            
            # Add other estimations as tools become available
            if self.quick_cleanup_options['cache'].isChecked():
                results.append("Application Caches: Coming Soon")
            
            if self.quick_cleanup_options['logs'].isChecked():
                results.append("Windows Logs: Coming Soon")
            
            # Display results
            results_text = f"Estimated space to be freed: {self._format_size(total_size)}\n\n"
            results_text += "Breakdown:\n" + "\n".join(f"• {result}" for result in results)
            
            if total_size == 0:
                results_text += "\n\nNo cleanup tools are currently selected or available."
            
            self.quick_results_text.setPlainText(results_text)
            
        except Exception as e:
            self.logger.error(f"Error estimating quick cleanup: {e}")
            self.quick_results_text.setPlainText(f"Error estimating cleanup size: {str(e)}")
    
    def run_quick_cleanup(self):
        """Run the quick cleanup operation."""
        try:
            # Check if any options are selected
            selected_tools = [name for name, checkbox in self.quick_cleanup_options.items() 
                            if checkbox.isChecked() and checkbox.isEnabled()]
            
            if not selected_tools:
                QMessageBox.warning(
                    self, "No Tools Selected",
                    "Please select at least one cleanup option to proceed."
                )
                return
            
            # Confirm operation
            if self.confirm_operations_checkbox.isChecked():
                reply = QMessageBox.question(
                    self, "Confirm Quick Cleanup",
                    f"Are you sure you want to run quick cleanup?\n\n"
                    f"Selected tools: {', '.join(selected_tools)}\n\n"
                    f"This operation may delete files permanently.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            # Create restore point if requested
            if self.restore_point_checkbox.isChecked():
                self.create_restore_point("RFU System Cleanup - Quick Cleanup")
            
            # Run temp files cleanup if selected
            if ('temp_files' in selected_tools and 
                'temp_files' in self.cleanup_tools):
                
                self.execute_temp_cleanup_with_defaults()
            
            # TODO: Add other quick cleanup operations as tools become available
            
        except Exception as e:
            self.logger.error(f"Error running quick cleanup: {e}")
            QMessageBox.critical(
                self, "Quick Cleanup Error",
                f"An error occurred during quick cleanup:\n{str(e)}"
            )
    
    def execute_temp_cleanup_with_defaults(self):
        """Execute temp files cleanup with default quick cleanup settings."""
        try:
            if 'temp_files' not in self.cleanup_tools:
                return
            
            temp_tool = self.cleanup_tools['temp_files']
            
            # Use default settings for quick cleanup
            params = {
                'max_age_days': 0,  # Delete all temp files
                'min_size_bytes': 0,  # All sizes
                'file_extensions': [],  # All extensions
                'include_system_temp': True,
                'create_backup': self.backup_files_checkbox.isChecked(),
                'secure_delete': False  # Fast deletion for quick cleanup
            }
            
            self.execute_cleanup_operation(temp_tool, params, "Temporary Files")
            
        except Exception as e:
            self.logger.error(f"Error executing temp cleanup with defaults: {e}")
    
    def preview_temp_cleanup(self):
        """Preview temporary files cleanup operation."""
        try:
            if 'temp_files' not in self.cleanup_tools:
                QMessageBox.warning(
                    self, "Tool Not Available",
                    "Temporary files cleanup tool is not available."
                )
                return
            
            temp_tool = self.cleanup_tools['temp_files']
            
            # Get parameters from UI
            params = self.get_temp_cleanup_params()
            
            # Get preview
            preview = temp_tool.preview_operation(**params)
            
            # Display preview
            self.show_cleanup_preview("Temporary Files Cleanup", preview)
            
        except Exception as e:
            self.logger.error(f"Error previewing temp cleanup: {e}")
            QMessageBox.critical(
                self, "Preview Error",
                f"Error generating preview:\n{str(e)}"
            )
    
    def execute_temp_cleanup(self):
        """Execute temporary files cleanup operation."""
        try:
            if 'temp_files' not in self.cleanup_tools:
                QMessageBox.warning(
                    self, "Tool Not Available",
                    "Temporary files cleanup tool is not available."
                )
                return
            
            # Confirm operation
            if self.confirm_operations_checkbox.isChecked():
                reply = QMessageBox.question(
                    self, "Confirm Temp Files Cleanup",
                    "Are you sure you want to clean temporary files?\n\n"
                    "This operation may delete files permanently.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            # Create restore point if requested
            if self.restore_point_checkbox.isChecked():
                self.create_restore_point("RFU System Cleanup - Temp Files")
            
            temp_tool = self.cleanup_tools['temp_files']
            params = self.get_temp_cleanup_params()
            
            self.execute_cleanup_operation(temp_tool, params, "Temporary Files")
            
        except Exception as e:
            self.logger.error(f"Error executing temp cleanup: {e}")
            QMessageBox.critical(
                self, "Cleanup Error",
                f"Error executing temp files cleanup:\n{str(e)}"
            )
    
    def get_temp_cleanup_params(self) -> Dict[str, Any]:
        """Get temporary files cleanup parameters from UI."""
        return {
            'max_age_days': self.temp_age_spinbox.value(),
            'min_size_bytes': self.temp_size_spinbox.value() * 1024 * 1024,  # Convert MB to bytes
            'file_extensions': [],  # TODO: Add extension filter UI
            'include_system_temp': self.temp_system_checkbox.isChecked(),
            'create_backup': self.temp_backup_checkbox.isChecked(),
            'secure_delete': self.temp_secure_checkbox.isChecked()
        }
    
    def execute_cleanup_operation(self, cleanup_tool, params, tool_name):
        """Execute a cleanup operation in a worker thread."""
        try:
            # Check if another operation is running
            if self.current_worker is not None:
                QMessageBox