"""
File Splitter GUI using file_utilities_2 StandardWindow

This module provides the main GUI for file splitting and joining operations,
using the standardized file_utilities_2 components for consistent UI/UX.
"""

import os
from PyQt5.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QSpinBox, QComboBox, QLineEdit, QPushButton,
    QProgressBar, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager
from file_utilities_2.integration.hub_connector import HubConnector
from file_utilities_2.core.file_splitter_logic import (
    FileSplitterLogic, FileSplitterWorkerThread
)
from file_utilities_2.core.file_splitter_config import FileSplitterConfig
from file_utilities_2.core.file_splitter_logging import get_file_splitter_logger


class FileSplitterGUI(StandardWindow):
    """
    File splitter GUI using standardized components.
    
    Provides a consistent interface for file splitting and joining operations
    with full file_utilities_2 integration including hub connectivity,
    shared theming, and standardized dialogs.
    """
    
    # Signals for external communication
    operation_started = pyqtSignal(str)  # operation type
    operation_completed = pyqtSignal(str, dict)  # operation type, results
    operation_failed = pyqtSignal(str, str)  # operation type, error message
    
    def __init__(self):
        """Initialize the file splitter GUI."""
        super().__init__(
            title="File Splitter & Joiner",
            icon_path=self._get_splitter_icon()
        )
        
        # Initialize components
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.logic = FileSplitterLogic(self.config, self.logger)
        self.hub_connector = HubConnector("file_splitter")
        self.worker_thread = None
        
        # Setup UI and connections
        self._setup_splitter_ui()
        self._connect_signals()
        self._connect_hub_integration()
        
        # Apply saved settings
        self._apply_saved_settings()
        
        self.logger.info("FileSplitterGUI initialized successfully")
    
    def _get_splitter_icon(self) -> str:
        """Get file splitter icon path."""
        icon_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'gui', 'icons', 'file_splitter.png'
        )
        # Fallback to default if specific icon doesn't exist
        if not os.path.exists(icon_path):
            return os.path.join(
                os.path.dirname(__file__), 
                '..', 'gui', 'icons', 'app_icon.png'
            )
        return icon_path
    
    def _setup_splitter_ui(self):
        """Setup file splitter specific UI using standardized components."""
        # Create main tab widget
        self.tab_widget = QTabWidget()
        ThemeManager.style_tab_widget(self.tab_widget)
        self.main_layout.addWidget(self.tab_widget)
        
        # Create split tab
        self.split_tab = self._create_split_tab()
        self.tab_widget.addTab(self.split_tab, "Split File")
        
        # Create join tab
        self.join_tab = self._create_join_tab()
        self.tab_widget.addTab(self.join_tab, "Join Files")
        
        # Create progress section
        self.progress_section = self._create_progress_section()
        self.main_layout.addWidget(self.progress_section)
    
    def _create_split_tab(self) -> QWidget:
        """Create the file splitting tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input file selection
        input_group = self.create_group_box("Input File")
        input_layout = QHBoxLayout(input_group)
        
        self.split_input_path = QLineEdit()
        self.split_input_path.setPlaceholderText("Select file to split...")
        ThemeManager.style_input_field(self.split_input_path)
        
        self.split_browse_input = self.create_button(
            "Browse", self.browse_split_input, primary=False
        )
        
        input_layout.addWidget(self.split_input_path)
        input_layout.addWidget(self.split_browse_input)
        layout.addWidget(input_group)
        
        # Output directory selection
        output_group = self.create_group_box("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.split_output_path = QLineEdit()
        self.split_output_path.setPlaceholderText("Select output directory...")
        ThemeManager.style_input_field(self.split_output_path)
        
        self.split_browse_output = self.create_button(
            "Browse", self.browse_split_output, primary=False
        )
        
        output_layout.addWidget(self.split_output_path)
        output_layout.addWidget(self.split_browse_output)
        layout.addWidget(output_group)
        
        # Split options
        options_group = self.create_group_box("Split Options")
        options_layout = QVBoxLayout(options_group)
        
        # Split by size option
        self.split_by_size = QRadioButton("Split by size")
        self.split_by_size.setChecked(True)
        options_layout.addWidget(self.split_by_size)
        
        size_layout = QHBoxLayout()
        self.size_value = QSpinBox()
        self.size_value.setMinimum(1)
        self.size_value.setMaximum(9999)
        self.size_value.setValue(1)
        
        self.size_unit = QComboBox()
        self.size_unit.addItems(["Bytes", "KB", "MB", "GB"])
        self.size_unit.setCurrentText("MB")
        
        size_layout.addWidget(self.size_value)
        size_layout.addWidget(self.size_unit)
        size_layout.addStretch()
        options_layout.addLayout(size_layout)
        
        # Split by parts option
        self.split_by_parts = QRadioButton("Split into parts")
        options_layout.addWidget(self.split_by_parts)
        
        self.parts_value = QSpinBox()
        self.parts_value.setMinimum(2)
        self.parts_value.setMaximum(9999)
        self.parts_value.setValue(2)
        self.parts_value.setEnabled(False)
        options_layout.addWidget(self.parts_value)
        
        layout.addWidget(options_group)
        
        # Split button
        self.split_button = self.create_button(
            "Split File", self.start_split_operation
        )
        layout.addWidget(self.split_button)
        
        layout.addStretch()
        return tab
    
    def _create_join_tab(self) -> QWidget:
        """Create the file joining tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input chunk file selection
        input_group = self.create_group_box("Input Chunk File")
        input_layout = QHBoxLayout(input_group)
        
        self.join_input_path = QLineEdit()
        self.join_input_path.setPlaceholderText(
            "Select first chunk (.part001 file)..."
        )
        ThemeManager.style_input_field(self.join_input_path)
        
        self.join_browse_input = self.create_button(
            "Browse", self.browse_join_input, primary=False
        )
        
        input_layout.addWidget(self.join_input_path)
        input_layout.addWidget(self.join_browse_input)
        layout.addWidget(input_group)
        
        # Output file selection
        output_group = self.create_group_box("Output File")
        output_layout = QHBoxLayout(output_group)
        
        self.join_output_path = QLineEdit()
        self.join_output_path.setPlaceholderText("Select output file...")
        ThemeManager.style_input_field(self.join_output_path)
        
        self.join_browse_output = self.create_button(
            "Browse", self.browse_join_output, primary=False
        )
        
        output_layout.addWidget(self.join_output_path)
        output_layout.addWidget(self.join_browse_output)
        layout.addWidget(output_group)
        
        # Join button
        self.join_button = self.create_button(
            "Join Files", self.start_join_operation
        )
        layout.addWidget(self.join_button)
        
        layout.addStretch()
        return tab
    
    def _create_progress_section(self) -> QWidget:
        """Create the progress monitoring section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        # Progress bar
        self.progress_bar = self.create_progress_bar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        ThemeManager.style_label(self.status_label)
        layout.addWidget(self.status_label)
        
        return section
    
    def _connect_signals(self):
        """Connect UI signals to their respective slots."""
        # Radio button signals for enabling/disabling controls
        self.split_by_size.toggled.connect(self.on_split_mode_changed)
        self.split_by_parts.toggled.connect(self.on_split_mode_changed)
        
        # Operation logic signals
        self.logic.progress_updated.connect(self.update_progress)
        self.logic.operation_complete.connect(self.operation_completed_handler)
        self.logic.error_occurred.connect(self.operation_error_handler)
        self.logic.finished.connect(self.operation_finished_handler)
    
    def _connect_hub_integration(self):
        """Connect hub integration."""
        # Set hub connector in logic
        self.logic.set_hub_connector(self.hub_connector)
        
        # Register with hub
        self.hub_connector.register_with_hub()
        
        # Connect hub signals
        self.hub_connector.tool_status_changed.connect(
            self._on_hub_status_changed
        )
    
    def _apply_saved_settings(self):
        """Apply saved configuration settings."""
        # Set default output directory if configured
        default_output = self.config.get_default_output_directory()
        if default_output:
            self.split_output_path.setText(default_output)
        
        # Set default chunk size
        chunk_size_mb = self.config.get_chunk_size_bytes() / (1024 * 1024)
        if chunk_size_mb >= 1:
            self.size_value.setValue(int(chunk_size_mb))
            self.size_unit.setCurrentText("MB")
    
    def on_split_mode_changed(self):
        """Handle split mode radio button changes."""
        if self.split_by_size.isChecked():
            self.size_value.setEnabled(True)
            self.size_unit.setEnabled(True)
            self.parts_value.setEnabled(False)
        else:
            self.size_value.setEnabled(False)
            self.size_unit.setEnabled(False)
            self.parts_value.setEnabled(True)
    
    def browse_split_input(self):
        """Browse for input file to split."""
        file_path = self.get_file_path(
            "Select File to Split", 
            "All Files (*)"
        )
        if file_path:
            self.split_input_path.setText(file_path)
    
    def browse_split_output(self):
        """Browse for output directory for split files."""
        dir_path = self.get_directory_path("Select Output Directory")
        if dir_path:
            self.split_output_path.setText(dir_path)
            
            # Save as default if configured
            if self.config.should_remember_directories():
                self.config.set_default_output_directory(dir_path)
    
    def browse_join_input(self):
        """Browse for first chunk file to join."""
        file_path = self.get_file_path(
            "Select First Chunk File", 
            "Part Files (*.part*);; All Files (*)"
        )
        if file_path:
            self.join_input_path.setText(file_path)
    
    def browse_join_output(self):
        """Browse for output file for joined result."""
        file_path = self.get_save_file_path(
            "Select Output File", 
            "All Files (*)"
        )
        if file_path:
            self.join_output_path.setText(file_path)
    
    def start_split_operation(self):
        """Start the file splitting operation."""
        # Validate inputs
        input_path = self.split_input_path.text().strip()
        output_path = self.split_output_path.text().strip()
        
        if not input_path or not output_path:
            self.show_warning_dialog(
                "Input Error",
                "Please select both input file and output directory."
            )
            return
        
        if not os.path.exists(input_path):
            self.show_error_dialog(
                "File Error",
                "Input file does not exist."
            )
            return
        
        # Get split parameters
        if self.split_by_size.isChecked():
            split_mode = 'size'
            value = self.size_value.value()
            unit_text = self.size_unit.currentText()
            unit_multiplier = {
                'Bytes': 1,
                'KB': 1024,
                'MB': 1024 * 1024,
                'GB': 1024 * 1024 * 1024
            }.get(unit_text, 1)
        else:
            split_mode = 'parts'
            value = self.parts_value.value()
            unit_multiplier = 1
        
        # Confirm large operations if configured
        if self.config.should_confirm_large_operations():
            file_size = os.path.getsize(input_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                reply = QMessageBox.question(
                    self, "Confirm Operation",
                    f"Split large file ({file_size / (1024*1024):.1f} MB)?\n"
                    f"This may take some time.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
        
        # Start operation in worker thread
        self.worker_thread = FileSplitterWorkerThread(
            self.logic, 'split',
            input_path, output_path, split_mode, value, unit_multiplier
        )
        
        # Update UI state
        self._set_operation_state(True)
        self.status_label.setText("Starting split operation...")
        
        # Emit operation started signal
        self.operation_started.emit("split")
        
        # Start the worker thread
        self.worker_thread.start()
        
        self.logger.info(f"Split operation started: {input_path}")
    
    def start_join_operation(self):
        """Start the file joining operation."""
        # Validate inputs
        input_path = self.join_input_path.text().strip()
        output_path = self.join_output_path.text().strip()
        
        if not input_path or not output_path:
            self.show_warning_dialog(
                "Input Error",
                "Please select both input chunk file and output file."
            )
            return
        
        if not os.path.exists(input_path):
            self.show_error_dialog(
                "File Error",
                "Input chunk file does not exist."
            )
            return
        
        # Start operation in worker thread
        self.worker_thread = FileSplitterWorkerThread(
            self.logic, 'join',
            input_path, output_path
        )
        
        # Update UI state
        self._set_operation_state(True)
        self.status_label.setText("Starting join operation...")
        
        # Emit operation started signal
        self.operation_started.emit("join")
        
        # Start the worker thread
        self.worker_thread.start()
        
        self.logger.info(f"Join operation started: {input_path}")
    
    def _set_operation_state(self, running: bool):
        """Set UI state for running/idle operation."""
        # Disable/enable buttons
        self.split_button.setEnabled(not running)
        self.join_button.setEnabled(not running)
        
        # Show/hide progress bar
        self.progress_bar.setVisible(running)
        if not running:
            self.progress_bar.setValue(0)
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status message."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        
        self.status_label.setText(message)
        
        # Update status bar
        if total > 0:
            self.show_status_message(
                f"{message} ({current}/{total})", 
                timeout=0  # No timeout during operation
            )
    
    def operation_completed_handler(self, message: str):
        """Handle successful operation completion."""
        self.show_info_dialog("Operation Complete", message)
        self.status_label.setText("Operation completed successfully")
        
        # Emit completion signal
        operation_type = "split" if self.worker_thread and self.worker_thread.operation_type == "split" else "join"
        self.operation_completed.emit(operation_type, {"message": message})
        
        self.logger.info(f"Operation completed: {message}")
    
    def operation_error_handler(self, error_message: str):
        """Handle operation errors."""
        self.show_error_dialog("Operation Error", error_message)
        self.status_label.setText("Operation failed")
        
        # Emit error signal
        operation_type = "split" if self.worker_thread and self.worker_thread.operation_type == "split" else "join"
        self.operation_failed.emit(operation_type, error_message)
        
        self.logger.error(f"Operation failed: {error_message}")
    
    def operation_finished_handler(self):
        """Handle operation thread completion."""
        # Reset UI state
        self._set_operation_state(False)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        
        # Update status bar
        self.show_status_message("Ready")
    
    def _on_hub_status_changed(self, tool_name: str, status: str):
        """Handle hub status changes."""
        if tool_name == "file_splitter":
            self.logger.debug(f"Hub status changed: {status}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop any running operations
        if self.worker_thread and self.worker_thread.isRunning():
            self.logic.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        # Cleanup hub integration
        if self.hub_connector:
            self.hub_connector.cleanup()
        
        self.logger.info("FileSplitterGUI closed")
        event.accept()


# Standalone application entry point
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = FileSplitterGUI()
    window.show()
    sys.exit(app.exec_())