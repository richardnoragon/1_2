"""
Embeddable File Splitter Widget

This module provides a compact, embeddable widget version of the file splitter
for integration into other applications or the main hub interface.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QRadioButton, QSpinBox, QComboBox, QLineEdit, QPushButton,
    QProgressBar, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal

from file_utilities_2.gui.standard_window import StandardUtilityWidget
from file_utilities_2.gui.themes import ThemeManager
from file_utilities_2.core.file_splitter_logic import (
    FileSplitterLogic, FileSplitterWorkerThread
)
from file_utilities_2.core.file_splitter_config import FileSplitterConfig
from file_utilities_2.core.file_splitter_logging import get_file_splitter_logger


class FileSplitterWidget(StandardUtilityWidget):
    """
    Embeddable file splitter widget for integration.
    
    Provides a compact interface for file splitting and joining operations
    that can be embedded in other applications or the main hub interface.
    """
    
    # Signals for parent communication
    operation_started = pyqtSignal(str)  # operation type
    operation_completed = pyqtSignal(str, dict)  # operation type, results
    operation_failed = pyqtSignal(str, str)  # operation type, error message
    
    def __init__(self, parent=None):
        """Initialize the embeddable file splitter widget."""
        super().__init__(title="File Splitter/Joiner", parent=parent)
        
        # Initialize components
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.logic = FileSplitterLogic(self.config, self.logger)
        self.worker_thread = None
        
        # Setup UI and connections
        self._setup_widget_ui()
        self._connect_signals()
        
        self.logger.info("FileSplitterWidget initialized successfully")
    
    def _setup_widget_ui(self):
        """Setup compact widget UI optimized for embedding."""
        # Create compact tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create compact split tab
        self.split_tab = self._create_compact_split_tab()
        self.tab_widget.addTab(self.split_tab, "Split")
        
        # Create compact join tab
        self.join_tab = self._create_compact_join_tab()
        self.tab_widget.addTab(self.join_tab, "Join")
        
        # Create compact progress section
        self.progress_section = self._create_compact_progress_section()
        self.main_layout.addWidget(self.progress_section)
    
    def _create_compact_split_tab(self) -> QWidget:
        """Create compact file splitting tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)  # Compact spacing
        
        # Input file selection (compact)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input:"))
        
        self.split_input_path = QLineEdit()
        self.split_input_path.setPlaceholderText("File to split...")
        ThemeManager.style_input_field(self.split_input_path)
        
        self.split_browse_input = QPushButton("...")
        self.split_browse_input.setMaximumWidth(30)
        self.split_browse_input.clicked.connect(self.browse_split_input)
        
        input_layout.addWidget(self.split_input_path)
        input_layout.addWidget(self.split_browse_input)
        layout.addLayout(input_layout)
        
        # Output directory selection (compact)
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        
        self.split_output_path = QLineEdit()
        self.split_output_path.setPlaceholderText("Output directory...")
        ThemeManager.style_input_field(self.split_output_path)
        
        self.split_browse_output = QPushButton("...")
        self.split_browse_output.setMaximumWidth(30)
        self.split_browse_output.clicked.connect(self.browse_split_output)
        
        output_layout.addWidget(self.split_output_path)
        output_layout.addWidget(self.split_browse_output)
        layout.addLayout(output_layout)
        
        # Split options (compact)
        options_layout = QHBoxLayout()
        
        self.split_by_size = QRadioButton("Size:")
        self.split_by_size.setChecked(True)
        options_layout.addWidget(self.split_by_size)
        
        self.size_value = QSpinBox()
        self.size_value.setMinimum(1)
        self.size_value.setMaximum(9999)
        self.size_value.setValue(1)
        self.size_value.setMaximumWidth(80)
        
        self.size_unit = QComboBox()
        self.size_unit.addItems(["MB", "KB", "GB"])
        self.size_unit.setMaximumWidth(60)
        
        options_layout.addWidget(self.size_value)
        options_layout.addWidget(self.size_unit)
        
        self.split_by_parts = QRadioButton("Parts:")
        options_layout.addWidget(self.split_by_parts)
        
        self.parts_value = QSpinBox()
        self.parts_value.setMinimum(2)
        self.parts_value.setMaximum(9999)
        self.parts_value.setValue(2)
        self.parts_value.setEnabled(False)
        self.parts_value.setMaximumWidth(80)
        options_layout.addWidget(self.parts_value)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Split button
        self.split_button = QPushButton("Split File")
        ThemeManager.style_primary_button(self.split_button)
        self.split_button.clicked.connect(self.start_split_operation)
        layout.addWidget(self.split_button)
        
        return tab
    
    def _create_compact_join_tab(self) -> QWidget:
        """Create compact file joining tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)  # Compact spacing
        
        # Input chunk file selection (compact)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Chunk:"))
        
        self.join_input_path = QLineEdit()
        self.join_input_path.setPlaceholderText("First chunk (.part001)...")
        ThemeManager.style_input_field(self.join_input_path)
        
        self.join_browse_input = QPushButton("...")
        self.join_browse_input.setMaximumWidth(30)
        self.join_browse_input.clicked.connect(self.browse_join_input)
        
        input_layout.addWidget(self.join_input_path)
        input_layout.addWidget(self.join_browse_input)
        layout.addLayout(input_layout)
        
        # Output file selection (compact)
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        
        self.join_output_path = QLineEdit()
        self.join_output_path.setPlaceholderText("Output file...")
        ThemeManager.style_input_field(self.join_output_path)
        
        self.join_browse_output = QPushButton("...")
        self.join_browse_output.setMaximumWidth(30)
        self.join_browse_output.clicked.connect(self.browse_join_output)
        
        output_layout.addWidget(self.join_output_path)
        output_layout.addWidget(self.join_browse_output)
        layout.addLayout(output_layout)
        
        # Join button
        self.join_button = QPushButton("Join Files")
        ThemeManager.style_primary_button(self.join_button)
        self.join_button.clicked.connect(self.start_join_operation)
        layout.addWidget(self.join_button)
        
        return tab
    
    def _create_compact_progress_section(self) -> QWidget:
        """Create compact progress monitoring section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(4)  # Very compact spacing
        
        # Progress bar (compact)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)
        ThemeManager.style_progress_bar(self.progress_bar)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label (compact)
        self.status_label = QLabel("Ready")
        self.status_label.setMaximumHeight(20)
        ThemeManager.style_label(self.status_label)
        layout.addWidget(self.status_label)
        
        return section
    
    def _connect_signals(self):
        """Connect UI signals to their respective slots."""
        # Radio button signals
        self.split_by_size.toggled.connect(self.on_split_mode_changed)
        self.split_by_parts.toggled.connect(self.on_split_mode_changed)
        
        # Operation logic signals
        self.logic.progress_updated.connect(self.update_progress)
        self.logic.operation_complete.connect(self.operation_completed_handler)
        self.logic.error_occurred.connect(self.operation_error_handler)
        self.logic.finished.connect(self.operation_finished_handler)
    
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Split", "", "All Files (*)"
        )
        if file_path:
            self.split_input_path.setText(file_path)
    
    def browse_split_output(self):
        """Browse for output directory for split files."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if dir_path:
            self.split_output_path.setText(dir_path)
    
    def browse_join_input(self):
        """Browse for first chunk file to join."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select First Chunk File", "", "Part Files (*.part*)"
        )
        if file_path:
            self.join_input_path.setText(file_path)
    
    def browse_join_output(self):
        """Browse for output file for joined result."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "All Files (*)"
        )
        if file_path:
            self.join_output_path.setText(file_path)
    
    def start_split_operation(self):
        """Start the file splitting operation."""
        # Validate inputs
        input_path = self.split_input_path.text().strip()
        output_path = self.split_output_path.text().strip()
        
        if not input_path or not output_path:
            QMessageBox.warning(
                self, "Input Error",
                "Please select both input file and output directory."
            )
            return
        
        if not os.path.exists(input_path):
            QMessageBox.warning(
                self, "File Error",
                "Input file does not exist."
            )
            return
        
        # Get split parameters
        if self.split_by_size.isChecked():
            split_mode = 'size'
            value = self.size_value.value()
            unit_text = self.size_unit.currentText()
            unit_multiplier = {
                'KB': 1024,
                'MB': 1024 * 1024,
                'GB': 1024 * 1024 * 1024
            }.get(unit_text, 1024 * 1024)
        else:
            split_mode = 'parts'
            value = self.parts_value.value()
            unit_multiplier = 1
        
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
    
    def start_join_operation(self):
        """Start the file joining operation."""
        # Validate inputs
        input_path = self.join_input_path.text().strip()
        output_path = self.join_output_path.text().strip()
        
        if not input_path or not output_path:
            QMessageBox.warning(
                self, "Input Error",
                "Please select both input chunk file and output file."
            )
            return
        
        if not os.path.exists(input_path):
            QMessageBox.warning(
                self, "File Error",
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
    
    def operation_completed_handler(self, message: str):
        """Handle successful operation completion."""
        QMessageBox.information(self, "Operation Complete", message)
        self.status_label.setText("Operation completed successfully")
        
        # Emit completion signal
        operation_type = "split" if (self.worker_thread and 
                                   self.worker_thread.operation_type == "split") else "join"
        self.operation_completed.emit(operation_type, {"message": message})
    
    def operation_error_handler(self, error_message: str):
        """Handle operation errors."""
        QMessageBox.critical(self, "Operation Error", error_message)
        self.status_label.setText("Operation failed")
        
        # Emit error signal
        operation_type = "split" if (self.worker_thread and 
                                   self.worker_thread.operation_type == "split") else "join"
        self.operation_failed.emit(operation_type, error_message)
    
    def operation_finished_handler(self):
        """Handle operation thread completion."""
        # Reset UI state
        self._set_operation_state(False)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
    
    def stop_operation(self):
        """Stop any running operation (for external control)."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.logic.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
            self._set_operation_state(False)
            self.status_label.setText("Operation stopped")


# Test widget standalone
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = FileSplitterWidget()
    widget.show()
    sys.exit(app.exec_())