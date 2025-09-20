"""
File Splitter GUI Wrapper

This module provides a GUI wrapper for the enhanced file splitter l    def __init__(self):
        try:
            super().__init__(
                title="File Split & Join - Richard's File Utilities",
                window_type="file_operations"
            )
        except TypeError:
            super().__init__()
            self.setWindowTitle("File Split & Join - Richard's File Utilities")
maintaining compatibility with the existing tools interface while using
the comprehensive utilities implementation.
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtWidgets import (QApplication, QFileDialog, QGridLayout,
                                 QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                                 QMessageBox, QProgressBar, QPushButton,
                                 QSpinBox, QTextEdit, QVBoxLayout, QWidget)
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(current_dir))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import enhanced file splitter logic
from ..file_splitter_logic import FileSplitterError, FileSplitterLogic

# Import GUI framework
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    StandardWindow = QMainWindow


class SplitterWorkerThread(QThread):
    """Worker thread for file splitting operations."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.logic = FileSplitterLogic()
    
    def run(self):
        """Execute the file operation in background thread."""
        try:
            if self.operation == 'split':
                self.logic.split_file(
                    input_file=self.kwargs['input_file'],
                    chunk_size_mb=self.kwargs['chunk_size'],
                    output_dir=self.kwargs.get('output_dir'),
                    progress_callback=self._progress_callback,
                    status_callback=self._status_callback
                )
                self.finished.emit(True, "File split successfully")
                
            elif self.operation == 'join':
                self.logic.join_files(
                    first_part_file=self.kwargs['first_part'],
                    output_file=self.kwargs.get('output_file'),
                    progress_callback=self._progress_callback,
                    status_callback=self._status_callback
                )
                self.finished.emit(True, "Files joined successfully")
                
        except FileSplitterError as e:
            self.finished.emit(False, f"Operation failed: {str(e)}")
        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}")
    
    def _progress_callback(self, progress: int):
        """Emit progress signal."""
        self.progress_updated.emit(progress)
    
    def _status_callback(self, status: str):
        """Emit status signal."""
        self.status_updated.emit(status)


class FileSplitJoinGUI(StandardWindow):
    """GUI wrapper for file splitting and joining operations.
    
    Provides a unified interface for file splitting and joining
    using the enhanced utilities logic while maintaining compatibility
    with the existing tools interface.
    """
    
    def __init__(self):
        try:
            super().__init__(
                title="File Splitter/Joiner - Richard's File Utilities",
                window_type="file_operations"
            )
        except TypeError:
            super().__init__()
            title = "File Splitter/Joiner - Richard's File Utilities"
            self.setWindowTitle(title)
        
        self.worker_thread: Optional[SplitterWorkerThread] = None
        self.init_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_operation', self.reset_form)
            self.menu_manager.register_callback('show_help', self.show_help)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        # Use the existing main layout from StandardWindow or create our own
        if hasattr(self, 'main_layout'):
            layout = self.main_layout
        else:
            # Create central widget and layout for QMainWindow fallback
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("File Splitter & Joiner")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Create split section
        self._create_split_section(layout)
        
        # Create join section
        self._create_join_section(layout)
        
        # Create progress section
        self._create_progress_section(layout)
    
    def _create_split_section(self, parent_layout):
        """Create the file splitting section."""
        split_group = QGroupBox("Split File")
        split_layout = QGridLayout(split_group)
        
        # Input file selection
        split_layout.addWidget(QLabel("File to Split:"), 0, 0)
        self.split_file_edit = QLineEdit()
        self.split_file_edit.setPlaceholderText("Select file to split...")
        split_layout.addWidget(self.split_file_edit, 0, 1)
        
        self.browse_split_button = QPushButton("Browse")
        self.browse_split_button.clicked.connect(self.browse_split_file)
        split_layout.addWidget(self.browse_split_button, 0, 2)
        
        # Chunk size
        split_layout.addWidget(QLabel("Chunk Size (MB):"), 1, 0)
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1, 2048)
        self.chunk_size_spin.setValue(100)
        split_layout.addWidget(self.chunk_size_spin, 1, 1)
        
        # Output directory
        split_layout.addWidget(QLabel("Output Directory:"), 2, 0)
        self.split_output_edit = QLineEdit()
        self.split_output_edit.setPlaceholderText("Same as input file")
        split_layout.addWidget(self.split_output_edit, 2, 1)
        
        self.browse_split_output_button = QPushButton("Browse")
        self.browse_split_output_button.clicked.connect(self.browse_split_output)
        split_layout.addWidget(self.browse_split_output_button, 2, 2)
        
        # Split button
        self.split_button = QPushButton("Split File")
        self.split_button.clicked.connect(self.split_file)
        self.split_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        split_layout.addWidget(self.split_button, 3, 0, 1, 3)
        
        parent_layout.addWidget(split_group)
    
    def _create_join_section(self, parent_layout):
        """Create the file joining section."""
        join_group = QGroupBox("Join Files")
        join_layout = QGridLayout(join_group)
        
        # First part file selection
        join_layout.addWidget(QLabel("First Part File:"), 0, 0)
        self.join_file_edit = QLineEdit()
        self.join_file_edit.setPlaceholderText("Select first part file (.part001)...")
        join_layout.addWidget(self.join_file_edit, 0, 1)
        
        self.browse_join_button = QPushButton("Browse")
        self.browse_join_button.clicked.connect(self.browse_join_file)
        join_layout.addWidget(self.browse_join_button, 0, 2)
        
        # Output file
        join_layout.addWidget(QLabel("Output File:"), 1, 0)
        self.join_output_edit = QLineEdit()
        self.join_output_edit.setPlaceholderText("Auto-detected from metadata")
        join_layout.addWidget(self.join_output_edit, 1, 1)
        
        self.browse_join_output_button = QPushButton("Browse")
        self.browse_join_output_button.clicked.connect(self.browse_join_output)
        join_layout.addWidget(self.browse_join_output_button, 1, 2)
        
        # Join button
        self.join_button = QPushButton("Join Files")
        self.join_button.clicked.connect(self.join_files)
        self.join_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        join_layout.addWidget(self.join_button, 2, 0, 1, 3)
        
        parent_layout.addWidget(join_group)
    
    def _create_progress_section(self, parent_layout):
        """Create the progress monitoring section."""
        progress_group = QGroupBox("Operation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        progress_layout.addWidget(self.status_text)
        
        parent_layout.addWidget(progress_group)
    
    def browse_split_file(self):
        """Browse for file to split."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Split", "", "All Files (*)"
        )
        if file_path:
            self.split_file_edit.setText(file_path)
    
    def browse_split_output(self):
        """Browse for split output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory:
            self.split_output_edit.setText(directory)
    
    def browse_join_file(self):
        """Browse for first part file to join."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select First Part File", "", 
            "Part Files (*.part001);;All Files (*)"
        )
        if file_path:
            self.join_file_edit.setText(file_path)
    
    def browse_join_output(self):
        """Browse for join output file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "All Files (*)"
        )
        if file_path:
            self.join_output_edit.setText(file_path)
    
    def split_file(self):
        """Start file splitting operation."""
        input_file = self.split_file_edit.text().strip()
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "Error", "Please select a valid input file.")
            return
        
        chunk_size = self.chunk_size_spin.value()
        output_dir = self.split_output_edit.text().strip() or None
        
        # Disable UI and show progress
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append("Starting file split operation...")
        
        # Start worker thread
        self.worker_thread = SplitterWorkerThread(
            'split',
            input_file=input_file,
            chunk_size=chunk_size,
            output_dir=output_dir
        )
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_text.append)
        self.worker_thread.finished.connect(self._operation_finished)
        self.worker_thread.start()
    
    def join_files(self):
        """Start file joining operation."""
        first_part = self.join_file_edit.text().strip()
        if not first_part or not os.path.exists(first_part):
            QMessageBox.warning(self, "Error", "Please select a valid first part file.")
            return
        
        output_file = self.join_output_edit.text().strip() or None
        
        # Disable UI and show progress
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append("Starting file join operation...")
        
        # Start worker thread
        self.worker_thread = SplitterWorkerThread(
            'join',
            first_part=first_part,
            output_file=output_file
        )
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_text.append)
        self.worker_thread.finished.connect(self._operation_finished)
        self.worker_thread.start()
    
    def _operation_finished(self, success: bool, message: str):
        """Handle operation completion."""
        self._set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.status_text.append(f"✓ {message}")
        else:
            QMessageBox.warning(self, "Error", message)
            self.status_text.append(f"✗ {message}")
        
        self.worker_thread = None
    
    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI controls during operations."""
        self.split_button.setEnabled(enabled)
        self.join_button.setEnabled(enabled)
        self.browse_split_button.setEnabled(enabled)
        self.browse_split_output_button.setEnabled(enabled)
        self.browse_join_button.setEnabled(enabled)
        self.browse_join_output_button.setEnabled(enabled)
    
    def reset_form(self):
        """Reset the form to initial state."""
        self.split_file_edit.clear()
        self.split_output_edit.clear()
        self.join_file_edit.clear()
        self.join_output_edit.clear()
        self.chunk_size_spin.setValue(100)
        self.status_text.clear()
        self.progress_bar.setVisible(False)
    
    def show_help(self):
        """Show help information."""
        help_text = """
File Splitter & Joiner Help

SPLITTING FILES:
1. Select the file you want to split
2. Choose chunk size in MB (default: 100MB)
3. Optionally select output directory
4. Click 'Split File'

JOINING FILES:
1. Select the first part file (.part001)
2. Optionally specify output filename
3. Click 'Join Files'

NOTES:
- Split files are numbered .part001, .part002, etc.
- Metadata is automatically saved and used for joining
- All part files must be in the same directory for joining
- Original file integrity is verified after joining
        """
        QMessageBox.information(self, "Help", help_text.strip())


def main():
    """Main entry point for standalone execution."""
    app = QApplication(sys.argv)
    window = FileSplitJoinGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()