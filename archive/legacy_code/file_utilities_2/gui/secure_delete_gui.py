"""
Secure Delete GUI Module

Enhanced GUI implementation with StandardWindow base class, full hub integration,
and comprehensive PyQt5 signal-slot architecture.

Migrated from: secure_delete.py (SecureDeleteGUI class)
Target: file_utilities_2 package integration with hub support
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, 
                             QComboBox, QApplication)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# Import file_utilities_2 components
from .standard_window import StandardWindow
from .themes import ThemeManager, Colors
from ..core.secure_delete_logic import SecureDeleteLogic
from ..core.secure_delete_config import get_config
from ..core.secure_delete_logging import get_logger
from ..integration.hub_connector import HubConnector


class SecureDeleteGUI(StandardWindow):
    """
    Enhanced secure file deletion GUI with hub integration.
    
    Features:
    - StandardWindow base class for consistent theming
    - Full hub integration with progress reporting
    - Enhanced PyQt5 signal-slot connections
    - Comprehensive error handling and logging
    - Resource management coordination
    - Configuration management integration
    """
    
    # Enhanced signal definitions for hub integration
    deletion_started = pyqtSignal(str, int)        # filepath, passes
    deletion_progress = pyqtSignal(int, str)       # percentage, message
    deletion_completed = pyqtSignal(str, dict)     # filepath, stats
    deletion_error = pyqtSignal(str, str)          # filepath, error
    
    # Hub integration signals
    hub_status_update = pyqtSignal(str, dict)      # status, details
    hub_resource_request = pyqtSignal(str, dict)   # resource_type, requirements
    
    def __init__(self, hub_instance=None):
        """
        Initialize the secure delete GUI.
        
        Args:
            hub_instance: Reference to the hub for integration
        """
        super().__init__("Secure File Delete")
        
        # Core components
        self.hub_instance = hub_instance
        self.config = get_config()
        self.logger = get_logger()
        self.delete_thread: Optional[QThread] = None
        self.delete_logic: Optional[SecureDeleteLogic] = None
        self.file_path: Optional[str] = None
        
        # Hub integration
        self.hub_connector = HubConnector("SecureDeleteGUI", hub_instance)
        self._setup_hub_integration()
        
        # UI state tracking
        self.is_operation_running = False
        self.current_operation_id: Optional[str] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Initialize with configuration
        self._load_configuration()
        
        self.logger.logger.info("SecureDeleteGUI initialized")
    
    def _setup_hub_integration(self):
        """Setup hub integration and register with hub."""
        try:
            # Register with hub
            self.hub_connector.register_with_hub(self.hub_instance)
            
            # Connect hub signals
            self.hub_connector.hub_progress_update.connect(
                self._handle_hub_progress_update
            )
            self.hub_connector.hub_status_change.connect(
                self._handle_hub_status_change
            )
            self.hub_connector.hub_error_report.connect(
                self._handle_hub_error_report
            )
            
            self.logger.logger.info("Hub integration setup completed")
            
        except Exception as e:
            self.logger.logger.error(f"Failed to setup hub integration: {e}")
    
    def _setup_ui(self) -> None:
        """Setup the enhanced user interface."""
        # Create header
        header = self.create_header("Secure File Delete")
        self.main_layout.addWidget(header)
        
        # Create file selection group
        file_group = self.create_group_box("File Selection")
        file_layout = QVBoxLayout()
        
        # File path display with enhanced styling
        self.file_label = QLabel("No file selected")
        ThemeManager.style_label(self.file_label)
        self.file_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }}
        """)
        
        # Enhanced button layout
        button_layout = QHBoxLayout()
        self.select_btn = self.create_button("Select File", self.select_file)
        self.delete_btn = self.create_button("Secure Delete", self.start_deletion)
        self.delete_btn.setEnabled(False)  # Disabled until file selected
        
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.delete_btn)
        
        file_layout.addWidget(self.file_label)
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        self.main_layout.addWidget(file_group)
        
        # Create enhanced options group
        options_group = self.create_group_box("Deletion Options")
        options_layout = QVBoxLayout()
        
        # Passes selection with validation
        passes_layout = QHBoxLayout()
        passes_label = QLabel("Overwrite Passes:")
        ThemeManager.style_label(passes_label)
        
        self.passes_combo = self._create_enhanced_combo_box()
        self._populate_passes_combo()
        
        passes_layout.addWidget(passes_label)
        passes_layout.addWidget(self.passes_combo)
        passes_layout.addStretch()
        
        # Additional options
        options_layout.addLayout(passes_layout)
        
        # Hub integration status
        self.hub_status_label = QLabel("Hub: Connected" if self.hub_instance 
                                      else "Hub: Standalone")
        ThemeManager.style_label(self.hub_status_label)
        self.hub_status_label.setStyleSheet(f"color: {Colors.SUCCESS};")
        options_layout.addWidget(self.hub_status_label)
        
        options_group.setLayout(options_layout)
        self.main_layout.addWidget(options_group)
        
        # Create enhanced progress group
        progress_group = self.create_group_box("Progress")
        progress_layout = QVBoxLayout()
        
        # Progress bars with enhanced styling
        self.overall_progress = self.create_progress_bar()
        self.file_progress = self.create_progress_bar()
        
        # Progress labels
        self.overall_label = QLabel("Ready")
        self.file_label_progress = QLabel("")
        ThemeManager.style_label(self.overall_label)
        ThemeManager.style_label(self.file_label_progress)
        
        progress_layout.addWidget(self.overall_label)
        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.file_label_progress)
        progress_layout.addWidget(self.file_progress)
        
        # Operation controls
        controls_layout = QHBoxLayout()
        self.stop_btn = self.create_button("Stop", self.stop_deletion, 
                                          primary=False)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        progress_layout.addLayout(controls_layout)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)
        
        # Create enhanced info group
        info_group = self.create_group_box("Information")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "This tool securely deletes files by overwriting them multiple "
            "times with random data, making recovery impossible.\n\n"
            "⚠️ Warning: This operation is irreversible!\n\n"
            "Features:\n"
            "• Multiple overwrite passes (1-35)\n"
            "• Hub integration for progress tracking\n"
            "• Resource management coordination\n"
            "• Comprehensive audit logging"
        )
        info_text.setWordWrap(True)
        ThemeManager.style_label(info_text)
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        self.main_layout.addWidget(info_group)
        
        # Set up drag and drop
        self.setAcceptDrops(True)
    
    def _create_enhanced_combo_box(self) -> QComboBox:
        """Create an enhanced combo box with validation."""
        combo = QComboBox()
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                padding: 8px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
                min-height: 30px;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border: 2px solid {Colors.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 1px solid {Colors.TEXT_DISABLED};
                width: 8px;
                height: 8px;
            }}
        """)
        return combo
    
    def _populate_passes_combo(self):
        """Populate the passes combo box with valid options."""
        default_passes = self.config.get_setting('default_passes', 3)
        max_passes = self.config.get_setting('max_passes', 35)
        
        # Add common options
        common_passes = [1, 3, 7, 35]
        for passes in common_passes:
            if passes <= max_passes:
                self.passes_combo.addItem(str(passes))
        
        # Set default selection
        default_index = self.passes_combo.findText(str(default_passes))
        if default_index >= 0:
            self.passes_combo.setCurrentIndex(default_index)
    
    def _setup_connections(self):
        """Setup enhanced signal-slot connections."""
        # File selection connections
        self.select_btn.clicked.connect(self.select_file)
        self.delete_btn.clicked.connect(self.start_deletion)
        self.stop_btn.clicked.connect(self.stop_deletion)
        
        # Configuration connections
        self.passes_combo.currentTextChanged.connect(self._on_passes_changed)
        
        # Internal signal connections
        self.deletion_started.connect(self._on_deletion_started)
        self.deletion_progress.connect(self._on_deletion_progress)
        self.deletion_completed.connect(self._on_deletion_completed)
        self.deletion_error.connect(self._on_deletion_error)
    
    def _load_configuration(self):
        """Load configuration settings."""
        try:
            # Update UI based on configuration
            if self.config.get_setting('show_detailed_progress', True):
                self.file_progress.setVisible(True)
                self.file_label_progress.setVisible(True)
            else:
                self.file_progress.setVisible(False)
                self.file_label_progress.setVisible(False)
            
            self.logger.logger.info("Configuration loaded")
            
        except Exception as e:
            self.logger.logger.error(f"Failed to load configuration: {e}")
    
    def _on_passes_changed(self, text: str):
        """Handle passes selection change."""
        try:
            passes = int(text)
            max_passes = self.config.get_setting('max_passes', 35)
            
            if passes > max_passes:
                self.show_warning_dialog(
                    "Invalid Selection",
                    f"Maximum allowed passes: {max_passes}"
                )
                # Reset to default
                default_passes = self.config.get_setting('default_passes', 3)
                self.passes_combo.setCurrentText(str(default_passes))
            
        except ValueError:
            self.logger.logger.error(f"Invalid passes value: {text}")
    
    def select_file(self) -> None:
        """Select file to securely delete with enhanced validation."""
        file_path = self.get_file_path("Select File to Delete", 
                                      "All Files (*)")
        if file_path:
            # Validate file
            if not os.path.isfile(file_path):
                self.show_error_dialog("Error", "Selected path is not a file")
                return
            
            # Check file permissions
            if not os.access(file_path, os.W_OK):
                self.show_warning_dialog(
                    "Warning", 
                    "File may not be writable. Deletion might fail."
                )
            
            self.file_path = file_path
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Update UI
            self.file_label.setText(f"{filename} ({file_size:,} bytes)")
            self.delete_btn.setEnabled(True)
            
            # Log file selection
            self.logger.logger.info(f"File selected: {file_path}")
            self.show_status_message(f"Selected: {filename}")
            
            # Report to hub
            if self.hub_connector:
                self.hub_connector.report_status_to_hub("file_selected", {
                    'filepath': file_path,
                    'file_size': file_size
                })
    
    def start_deletion(self) -> None:
        """Start the secure deletion process with enhanced validation."""
        if not self.file_path or not os.path.isfile(self.file_path):
            self.show_error_dialog("Error", "Please select a valid file first")
            return
        
        if self.is_operation_running:
            self.show_warning_dialog("Warning", "Operation already in progress")
            return
        
        try:
            passes = int(self.passes_combo.currentText())
            filename = os.path.basename(self.file_path)
            file_size = os.path.getsize(self.file_path)
            
            # Enhanced confirmation dialog
            reply = QMessageBox.question(
                self, "Confirm Secure Deletion",
                f"Are you sure you want to securely delete:\n\n"
                f"File: {filename}\n"
                f"Size: {file_size:,} bytes\n"
                f"Passes: {passes}\n\n"
                f"⚠️ This operation cannot be undone!\n\n"
                f"The file will be overwritten {passes} times with random data "
                f"and then permanently deleted.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Request resources from hub
            if self.hub_connector:
                resource_granted = self.hub_connector.request_hub_resources(
                    "disk", {
                        "operation": "secure_delete",
                        "file_size": file_size,
                        "priority": "high"
                    }
                )
                
                if not resource_granted:
                    self.show_error_dialog(
                        "Resource Error",
                        "Unable to allocate required resources. "
                        "Please try again later."
                    )
                    return
            
            # Start deletion operation
            self._start_deletion_thread(passes)
            
        except ValueError:
            self.show_error_dialog("Error", "Invalid number of passes")
        except Exception as e:
            self.logger.logger.error(f"Failed to start deletion: {e}")
            self.show_error_dialog("Error", f"Failed to start deletion: {e}")
    
    def _start_deletion_thread(self, passes: int):
        """Start the deletion thread with enhanced monitoring."""
        try:
            # Update UI state
            self.is_operation_running = True
            self._update_ui_for_operation_start()
            
            # Create deletion logic with hub integration
            self.delete_logic = SecureDeleteLogic(self.hub_instance)
            self.delete_thread = QThread()
            self.delete_logic.moveToThread(self.delete_thread)
            
            # Connect enhanced signals
            self._connect_deletion_signals()
            
            # Start operation
            self.delete_thread.started.connect(
                lambda: self.delete_logic.shred_file(self.file_path, passes)
            )
            
            # Log operation start
            self.current_operation_id = self.logger.log_operation_start(
                self.file_path, passes, os.path.getsize(self.file_path)
            )
            
            # Emit signal and start thread
            self.deletion_started.emit(self.file_path, passes)
            self.delete_thread.start()
            
        except Exception as e:
            self.logger.logger.error(f"Failed to start deletion thread: {e}")
            self._reset_ui_state()
            self.show_error_dialog("Error", f"Failed to start deletion: {e}")
    
    def _connect_deletion_signals(self):
        """Connect deletion logic signals with enhanced handling."""
        if self.delete_logic:
            # Progress signals
            self.delete_logic.progress_updated.connect(
                self.update_overall_progress
            )
            self.delete_logic.file_progress.connect(
                self.update_file_progress
            )
            
            # Completion signals
            self.delete_logic.operation_complete.connect(
                self.deletion_complete
            )
            self.delete_logic.error_occurred.connect(
                self.handle_error
            )
            self.delete_logic.finished.connect(
                self.delete_thread.quit
            )
            
            # Hub integration signals
            self.delete_logic.hub_progress_update.connect(
                self._handle_hub_progress_update
            )
            self.delete_logic.hub_status_change.connect(
                self._handle_hub_status_change
            )
            self.delete_logic.hub_error_report.connect(
                self._handle_hub_error_report
            )
    
    def _update_ui_for_operation_start(self):
        """Update UI for operation start."""
        self.delete_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.passes_combo.setEnabled(False)
        
        self.overall_progress.setVisible(True)
        self.file_progress.setVisible(True)
        self.overall_progress.setValue(0)
        self.file_progress.setValue(0)
    
    def _reset_ui_state(self):
        """Reset UI to initial state."""
        self.is_operation_running = False
        self.current_operation_id = None
        
        self.delete_btn.setEnabled(bool(self.file_path))
        self.select_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.passes_combo.setEnabled(True)
        
        self.overall_progress.setVisible(False)
        self.file_progress.setVisible(False)
        self.overall_label.setText("Ready")
        self.file_label_progress.setText("")
    
    def stop_deletion(self) -> None:
        """Stop the deletion process gracefully."""
        if self.delete_logic and self.is_operation_running:
            self.delete_logic.stop()
            self.show_status_message("Stopping deletion...")
            self.logger.logger.info("User requested deletion stop")
    
    def update_overall_progress(self, value: int, total: int, message: str):
        """Update overall progress with enhanced display."""
        if total > 0:
            percentage = int((value / total) * 100)
            self.overall_progress.setMaximum(total)
            self.overall_progress.setValue(value)
            self.overall_label.setText(f"{message} ({percentage}%)")
            self.show_status_message(message)
            
            # Emit progress signal
            self.deletion_progress.emit(percentage, message)
    
    def update_file_progress(self, processed: int, total: int):
        """Update file progress with enhanced display."""
        if total > 0:
            percentage = int((processed / total) * 100)
            self.file_progress.setMaximum(total)
            self.file_progress.setValue(processed)
            self.file_label_progress.setText(
                f"Processing: {processed:,}/{total:,} bytes ({percentage}%)"
            )
    
    def deletion_complete(self, message: str):
        """Handle successful deletion completion."""
        try:
            # Log completion
            if self.current_operation_id:
                duration = 0.0  # Would be calculated from operation start time
                passes = int(self.passes_combo.currentText())
                self.logger.log_operation_complete(
                    self.current_operation_id, self.file_path, duration, passes
                )
            
            # Update UI
            self._reset_ui_state()
            self.file_label.setText("No file selected")
            self.file_path = None
            
            # Show success message
            self.show_info_dialog("Success", message)
            
            # Emit completion signal
            stats = self.delete_logic.get_statistics() if self.delete_logic else {}
            self.deletion_completed.emit(self.file_path or "", stats)
            
            self.logger.logger.info(f"Deletion completed: {message}")
            
        except Exception as e:
            self.logger.logger.error(f"Error handling deletion completion: {e}")
    
    def handle_error(self, error_message: str):
        """Handle deletion errors with enhanced reporting."""
        try:
            # Log error
            if self.current_operation_id:
                self.logger.log_operation_error(
                    self.current_operation_id, self.file_path or "", 
                    error_message, {}
                )
            
            # Update UI
            self._reset_ui_state()
            
            # Show error dialog
            self.show_error_dialog("Deletion Error", error_message)
            
            # Emit error signal
            self.deletion_error.emit(self.file_path or "", error_message)
            
            self.logger.logger.error(f"Deletion error: {error_message}")
            
        except Exception as e:
            self.logger.logger.error(f"Error handling deletion error: {e}")
    
    def _handle_hub_progress_update(self, percentage: int, message: str):
        """Handle hub progress updates."""
        self.hub_status_update.emit("progress", {
            'percentage': percentage,
            'message': message
        })
    
    def _handle_hub_status_change(self, status: str, details: Dict[str, Any]):
        """Handle hub status changes."""
        self.hub_status_update.emit(status, details)
    
    def _handle_hub_error_report(self, error_message: str, 
                                details: Dict[str, Any]):
        """Handle hub error reports."""
        self.hub_status_update.emit("error", {
            'error_message': error_message,
            'details': details
        })
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle enhanced drag enter events."""
        if event.mimeData().hasUrls() and not self.is_operation_running:
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle enhanced drop events."""
        if self.is_operation_running:
            return
        
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file_path in files:
            if os.path.isfile(file_path):
                self.file_path = file_path
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                self.file_label.setText(f"{filename} ({file_size:,} bytes)")
                self.delete_btn.setEnabled(True)
                self.show_status_message(f"Dropped: {filename}")
                self.logger.logger.info(f"File dropped: {file_path}")
                break
    
    def closeEvent(self, event) -> None:
        """Enhanced cleanup when closing."""
        try:
            # Stop any running operations
            if self.is_operation_running and self.delete_logic:
                self.delete_logic.stop()
                if self.delete_thread and self.delete_thread.isRunning():
                    self.delete_thread.quit()
                    self.delete_thread.wait(3000)  # Wait up to 3 seconds
            
            # Cleanup hub integration
            if self.hub_connector:
                self.hub_connector.cleanup()
            
            # Cleanup logging
            if self.delete_logic:
                self.delete_logic.cleanup()
            
            self.logger.logger.info("SecureDeleteGUI closed")
            event.accept()
            
        except Exception as e:
            self.logger.logger.error(f"Error during cleanup: {e}")
            event.accept()


def main() -> None:
    """Main function to run the secure delete GUI."""
    app = QApplication(sys.argv)
    window = SecureDeleteGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()