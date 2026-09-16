"""Graphical interface for RFU file splitter and joiner.

Provides the enhanced Qt-based interface for splitting large files into
manageable chunks and joining them back together while integrating with the
shared StandardWindow framework, logging, and configuration helpers.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import math
import os
import sys
from typing import Optional

try:
    from PyQt5.QtCore import QThread, pyqtSignal
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QLabel,
        QLineEdit,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from src.gui.themes import token
except ImportError:

    def token(key: str) -> str:
        return ""


# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import enhanced file splitter logic
from .file_splitter_logic import (  # noqa: E402
    FileSplitterError,
    FileSplitterLogic,
)

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
            if self.operation == "split":
                self.logic.split_file(
                    input_file=self.kwargs["input_file"],
                    chunk_size_mb=self.kwargs["chunk_size"],
                    output_dir=self.kwargs.get("output_dir"),
                    progress_callback=self._progress_callback,
                    status_callback=self._status_callback,
                )
                self.finished.emit(True, "File split successfully")

            elif self.operation == "join":
                self.logic.join_files(
                    first_part_file=self.kwargs["first_part"],
                    output_file=self.kwargs.get("output_file"),
                    progress_callback=self._progress_callback,
                    status_callback=self._status_callback,
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
                window_type="file_operations",
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
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_operation", self.reset_form)
            self.menu_manager.register_callback("show_help", self.show_help)

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        # Use the existing main layout from StandardWindow or create our own
        if hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for QMainWindow fallback
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Create header
        header_label = _ui_widget(QLabel, 'Legacy.s437ccb48e73d7cdc', 'setText')
        header_label.setStyleSheet(
            """
            QLabel {

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # Create split section
        self._create_split_section(layout)

        # Create join section
        self._create_join_section(layout)

        # Create progress section
        self._create_progress_section(layout)

    def _create_split_section(self, parent_layout):
        """Create the file splitting section."""
        split_group = _ui_widget(QGroupBox, 'Legacy.s620ce9fb1020a2da', 'setTitle')
        split_layout = QGridLayout(split_group)

        # Input file selection
        split_layout.addWidget(_ui_widget(QLabel, 'Legacy.scc14a62bfd5df0c5', 'setText'), 0, 0)
        self.split_file_edit = QLineEdit()
        _ui_bind(self.split_file_edit, 'setAccessibleName', 'Legacy.sbeeffea7ce781e78')
        _ui_bind(self.split_file_edit, 'setPlaceholderText', 'Legacy.s73635a38c219cd02')
        split_layout.addWidget(self.split_file_edit, 0, 1)

        self.browse_split_button = _ui_widget(QPushButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_split_button, 'setAccessibleName', 'Legacy.s8b25f6b043bdba27')
        self.browse_split_button.setMinimumHeight(44)
        self.browse_split_button.clicked.connect(self.browse_split_file)
        split_layout.addWidget(self.browse_split_button, 0, 2)

        # Chunk size
        split_layout.addWidget(_ui_widget(QLabel, 'Legacy.s40ca0b7ac864a185', 'setText'), 1, 0)
        self.chunk_size_spin = QSpinBox()
        _ui_bind(self.chunk_size_spin, 'setAccessibleName', 'Legacy.s2184df6d8f299715')
        self.chunk_size_spin.setMinimumHeight(44)
        self.chunk_size_spin.setRange(1, 2048)
        self.chunk_size_spin.setValue(100)
        split_layout.addWidget(self.chunk_size_spin, 1, 1)

        # Output directory
        split_layout.addWidget(_ui_widget(QLabel, 'Legacy.sf14245e1dd8c28ac', 'setText'), 2, 0)
        self.split_output_edit = QLineEdit()
        _ui_bind(self.split_output_edit, 'setAccessibleName', 'Legacy.s6f9bb2768cf6e9d2')
        _ui_bind(self.split_output_edit, 'setPlaceholderText', 'Legacy.s756dd9d7975c1979')
        split_layout.addWidget(self.split_output_edit, 2, 1)

        self.browse_split_output_button = _ui_widget(QPushButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_split_output_button, 'setAccessibleName', 'Legacy.sc615df9b2f4f7a36')
        self.browse_split_output_button.setMinimumHeight(44)
        self.browse_split_output_button.clicked.connect(self.browse_split_output)
        split_layout.addWidget(self.browse_split_output_button, 2, 2)

        # Preview button (dry run — must precede split button per spec §5.2)
        self.preview_split_button = _ui_widget(QPushButton, 'Legacy.s151024547572d853', 'setText')
        _ui_bind(self.preview_split_button, 'setAccessibleName', 'Legacy.sa54835fceef0f56a')
        self.preview_split_button.setMinimumHeight(44)
        self.preview_split_button.clicked.connect(self.preview_split)
        _ui_bind(self.preview_split_button, 'setToolTip', 'Legacy.s70d8b635813eb754')
        split_layout.addWidget(self.preview_split_button, 3, 0, 1, 3)

        # Split button
        self.split_button = _ui_widget(QPushButton, 'Legacy.s620ce9fb1020a2da', 'setText')
        _ui_bind(self.split_button, 'setAccessibleName', 'Legacy.s389ce2c62976a80d')
        self.split_button.setMinimumHeight(44)
        self.split_button.clicked.connect(self.split_file)
        self.split_button.setStyleSheet(
            """
            QPushButton {
                background-color: {token('accent')};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: {token('button_primary_hover')};
            }
            QPushButton:disabled {
                background-color: {token('text_disabled')};
            }
        """
        )
        split_layout.addWidget(self.split_button, 3, 0, 1, 3)

        parent_layout.addWidget(split_group)

    def _create_join_section(self, parent_layout):
        """Create the file joining section."""
        join_group = _ui_widget(QGroupBox, 'Legacy.sa95f7c3af18995bc', 'setTitle')
        join_layout = QGridLayout(join_group)

        # First part file selection
        join_layout.addWidget(_ui_widget(QLabel, 'Legacy.s69e911b276462de8', 'setText'), 0, 0)
        self.join_file_edit = QLineEdit()
        _ui_bind(self.join_file_edit, 'setAccessibleName', 'Legacy.s918450e51a439b1c')
        _ui_bind(self.join_file_edit, 'setPlaceholderText', 'Legacy.s6db43a2714da8087')
        join_layout.addWidget(self.join_file_edit, 0, 1)

        self.browse_join_button = _ui_widget(QPushButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_join_button, 'setAccessibleName', 'Legacy.sfdccae902d0310d1')
        self.browse_join_button.setMinimumHeight(44)
        self.browse_join_button.clicked.connect(self.browse_join_file)
        join_layout.addWidget(self.browse_join_button, 0, 2)

        # Output file
        join_layout.addWidget(_ui_widget(QLabel, 'Legacy.sb20feaf128a2aa6d', 'setText'), 1, 0)
        self.join_output_edit = QLineEdit()
        _ui_bind(self.join_output_edit, 'setAccessibleName', 'Legacy.s0cffccc211f47c8a')
        _ui_bind(self.join_output_edit, 'setPlaceholderText', 'Legacy.sb875b52d8d42589b')
        join_layout.addWidget(self.join_output_edit, 1, 1)

        self.browse_join_output_button = _ui_widget(QPushButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_join_output_button, 'setAccessibleName', 'Legacy.sf5311a974fa2195a')
        self.browse_join_output_button.setMinimumHeight(44)
        self.browse_join_output_button.clicked.connect(self.browse_join_output)
        join_layout.addWidget(self.browse_join_output_button, 1, 2)

        # Join button
        self.join_button = _ui_widget(QPushButton, 'Legacy.sa95f7c3af18995bc', 'setText')
        _ui_bind(self.join_button, 'setAccessibleName', 'Legacy.s3e05fb8334d496a6')
        self.join_button.setMinimumHeight(44)
        self.join_button.clicked.connect(self.join_files)
        self.join_button.setStyleSheet(
            """
            QPushButton {
                background-color: {token('semantic_success')};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: {token('semantic_success')};
            }
            QPushButton:disabled {
                background-color: {token('text_disabled')};
            }
        """
        )
        join_layout.addWidget(self.join_button, 2, 0, 1, 3)

        parent_layout.addWidget(join_group)

    def _create_progress_section(self, parent_layout):
        """Create the progress monitoring section."""
        progress_group = _ui_widget(QGroupBox, 'Legacy.s9ece66e0d30cdbcc', 'setTitle')
        progress_layout = QVBoxLayout(progress_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        _ui_bind(self.status_text, 'setAccessibleName', 'Legacy.s749dd48425dda10a')
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
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.split_output_edit.setText(directory)

    def browse_join_file(self):
        """Browse for first part file to join."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select First Part File",
            "",
            "Part Files (*.part001);;All Files (*)",
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

    def preview_split(self):
        """Preview split operation without creating files."""
        input_file = self.split_file_edit.text().strip()
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "Error", "Please select a valid input file.")
            return

        chunk_size = self.chunk_size_spin.value()
        file_size = os.path.getsize(input_file)
        chunk_bytes = chunk_size * 1024 * 1024
        num_parts = math.ceil(file_size / chunk_bytes) if chunk_bytes > 0 else 0
        base_name = os.path.basename(input_file)

        last_part_size = file_size % chunk_bytes if chunk_bytes > 0 else 0
        if last_part_size == 0 and num_parts > 0:
            last_part_size = chunk_bytes

        msg = (
            f"DRY RUN — No files will be created.\n\n"
            f"File: {base_name}\n"
            f"Size: {file_size / (1024 ** 2):.2f} MB\n"
            f"Chunk size: {chunk_size} MB\n"
            f"Parts: {num_parts}\n"
        )
        if num_parts > 1:
            msg += (
                f"Parts 1–{num_parts - 1}: {chunk_size} MB each\n"
                f"Part {num_parts}: {last_part_size / (1024 ** 2):.2f} MB"
            )

        QMessageBox.information(self, "Preview Split (Dry Run)", msg)
        self.status_text.append(
            f"Preview: '{base_name}' ({file_size / (1024 ** 2):.1f} MB) "
            f"would be split into {num_parts} part(s) of up to {chunk_size} MB each."
        )

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
            "split",
            input_file=input_file,
            chunk_size=chunk_size,
            output_dir=output_dir,
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
            "join", first_part=first_part, output_file=output_file
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
