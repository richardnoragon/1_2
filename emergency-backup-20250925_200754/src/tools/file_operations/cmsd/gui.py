"""
CMSD GUI Wrapper

This module provides a GUI wrapper for the enhanced CMSD
(Copy/Move/Sync/Delete) logic, maintaining compatibility with the existing
tools interface while using the comprehensive utilities implementation.
"""

import os
import sys
from typing import Optional

try:
    from PyQt5.QtCore import QThread, pyqtSignal
    from PyQt5.QtWidgets import (
        QApplication,
        QButtonGroup,
        QCheckBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import enhanced CMSD logic
from ..cmsd_logic import CMSDLogic, DirectoryComparison, OperationResult

# Import GUI framework
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow

    StandardWindow = QMainWindow


# Constants
DIRECTORY_SELECTION = "Directory Selection"
OPERATION_BUTTONS_STYLE = """
    QPushButton {
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:disabled {
        background-color: #bdc3c7;
    }
"""


class CMSDWorkerThread(QThread):
    """Worker thread for CMSD operations."""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_processed = pyqtSignal(str)
    finished = pyqtSignal(bool, str, object)  # success, message, result

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.logic = CMSDLogic()

    def run(self):
        """Execute the file operation in background thread."""
        try:
            if self.operation == "copy":
                result = self._execute_copy()
            elif self.operation == "move":
                result = self._execute_move()
            elif self.operation == "sync":
                result = self._execute_sync()
            elif self.operation == "delete":
                result = self._execute_delete()
            elif self.operation == "compare":
                result = self._execute_compare()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

            operation_name = self.operation.title()
            message = f"{operation_name} operation completed"
            self.finished.emit(True, message, result)
        except Exception as e:
            self.finished.emit(False, f"Operation failed: {str(e)}", None)

    def _execute_copy(self):
        """Execute copy operation."""
        if "source" in self.kwargs and "destination" in self.kwargs:
            source_files = self._get_directory_files(self.kwargs["source"])
            destination = self.kwargs["destination"]
            return self.logic.copy_files(source_files, destination)
        return self.logic.copy_selected_to_right()

    def _execute_move(self):
        """Execute move operation."""
        if "source" in self.kwargs and "destination" in self.kwargs:
            source_files = self._get_directory_files(self.kwargs["source"])
            dest_dir = self.kwargs["destination"]

            # Copy first
            copy_result = self.logic.copy_files(source_files, dest_dir)
            if copy_result.success:
                # Then delete
                delete_result = self.logic.delete_files(source_files)
                return OperationResult(
                    delete_result.success,
                    copy_result.processed_files,
                    copy_result.failed_files + delete_result.failed_files,
                    copy_result.total_bytes,
                )
            return copy_result

        # Selected files move
        copy_result = self.logic.copy_selected_to_right()
        if copy_result.success:
            return self.logic.delete_selected_files()
        return copy_result

    def _execute_sync(self):
        """Execute sync operation."""
        source_dir = self.kwargs["source"]
        dest_dir = self.kwargs["destination"]

        self.logic.left_directory = source_dir
        self.logic.right_directory = dest_dir

        comparison = self.logic.compare_directories()

        # Sync files that are only in source to destination
        source_files = []
        for filename in comparison.only_left:
            source_path = os.path.join(source_dir, filename)
            if os.path.isfile(source_path):
                source_files.append(source_path)

        if source_files:
            return self.logic.copy_files(source_files, dest_dir)
        return OperationResult(True, [], [], 0)

    def _execute_delete(self):
        """Execute delete operation."""
        target_dir = self.kwargs["target"]
        recursive = self.kwargs.get("recursive", False)

        files_to_delete = self._get_files_to_delete(target_dir, recursive)
        return self.logic.delete_files(files_to_delete)

    def _execute_compare(self):
        """Execute compare operation."""
        dir1 = self.kwargs["dir1"]
        dir2 = self.kwargs["dir2"]

        self.logic.left_directory = dir1
        self.logic.right_directory = dir2

        return self.logic.compare_directories()

    def _get_directory_files(self, directory):
        """Get all files from a directory."""
        files = []
        if os.path.isdir(directory):
            for root, dirs, file_list in os.walk(directory):
                for file in file_list:
                    files.append(os.path.join(root, file))
        return files

    def _get_files_to_delete(self, target_dir, recursive):
        """Get files to delete from target directory."""
        files_to_delete = []
        if not os.path.isdir(target_dir):
            return files_to_delete

        if recursive:
            for root, dirs, file_list in os.walk(target_dir):
                for file in file_list:
                    files_to_delete.append(os.path.join(root, file))
        else:
            files_to_delete = [
                os.path.join(target_dir, f)
                for f in os.listdir(target_dir)
                if os.path.isfile(os.path.join(target_dir, f))
            ]

        return files_to_delete

    def _progress_callback(self, progress: int):
        """Emit progress signal."""
        self.progress_updated.emit(progress)

    def _status_callback(self, status: str):
        """Emit status signal."""
        self.status_updated.emit(status)

    def _file_callback(self, filename: str):
        """Emit file processed signal."""
        self.file_processed.emit(filename)


class CopyMoveSyncDeleteWindow(StandardWindow):
    """GUI wrapper for Copy/Move/Sync/Delete operations.

    Provides a unified interface for file operations using the enhanced
    utilities logic while maintaining compatibility with the existing
    tools interface.
    """

    def __init__(self):
        try:
            # Try to use StandardWindow with its parameters
            super().__init__(
                title="Copy/Move/Sync/Delete - Richard's File Utilities",
                window_type="file_operations",
            )
        except TypeError:
            # Fallback for QMainWindow (no parameters)
            super().__init__()
            title = "Copy/Move/Sync/Delete - Richard's File Utilities"
            self.setWindowTitle(title)

        self.worker_thread: Optional[CMSDWorkerThread] = None
        self.init_ui()
        self._setup_menu_callbacks()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback(
                "new_operation", self.reset_form
            )
            self.menu_manager.register_callback("show_help", self.show_help)

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create our own
        if hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for QMainWindow fallback
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Create header
        header_label = QLabel("Copy / Move / Sync / Delete")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Create tab widget for different operations
        self.tab_widget = QTabWidget()

        # Create tabs
        self._create_copy_move_tab()
        self._create_sync_tab()
        self._create_delete_tab()
        self._create_compare_tab()

        layout.addWidget(self.tab_widget)

        # Create progress section
        self._create_progress_section(layout)

    def _create_copy_move_tab(self):
        """Create the copy/move operations tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Operation selection
        operation_group = QGroupBox("Operation Type")
        operation_layout = QHBoxLayout(operation_group)

        self.operation_group = QButtonGroup()
        self.copy_radio = QRadioButton("Copy Files")
        self.move_radio = QRadioButton("Move Files")
        self.copy_radio.setChecked(True)

        self.operation_group.addButton(self.copy_radio, 0)
        self.operation_group.addButton(self.move_radio, 1)

        operation_layout.addWidget(self.copy_radio)
        operation_layout.addWidget(self.move_radio)
        layout.addWidget(operation_group)

        # Directory selection
        dir_group = QGroupBox(DIRECTORY_SELECTION)
        dir_layout = QGridLayout(dir_group)

        # Source directory
        dir_layout.addWidget(QLabel("Source Directory:"), 0, 0)
        self.source_edit = QLineEdit()
        dir_layout.addWidget(self.source_edit, 0, 1)
        self.browse_source_button = QPushButton("Browse")
        self.browse_source_button.clicked.connect(self.browse_source)
        dir_layout.addWidget(self.browse_source_button, 0, 2)

        # Destination directory
        dir_layout.addWidget(QLabel("Destination Directory:"), 1, 0)
        self.dest_edit = QLineEdit()
        dir_layout.addWidget(self.dest_edit, 1, 1)
        self.browse_dest_button = QPushButton("Browse")
        self.browse_dest_button.clicked.connect(self.browse_destination)
        dir_layout.addWidget(self.browse_dest_button, 1, 2)

        layout.addWidget(dir_group)

        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.setChecked(True)
        options_layout.addWidget(self.recursive_check)

        self.overwrite_check = QCheckBox("Overwrite existing files")
        options_layout.addWidget(self.overwrite_check)

        layout.addWidget(options_group)

        # Execute button
        self.copy_move_button = QPushButton("Execute Operation")
        self.copy_move_button.clicked.connect(self.execute_copy_move)
        self.copy_move_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #3498db;
                {OPERATION_BUTTONS_STYLE.strip()[13:-1]}
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """
        )
        layout.addWidget(self.copy_move_button)

        self.tab_widget.addTab(tab, "Copy/Move")

    def _create_sync_tab(self):
        """Create the synchronization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Directory selection
        dir_group = QGroupBox(DIRECTORY_SELECTION)
        dir_layout = QGridLayout(dir_group)

        # Source directory
        dir_layout.addWidget(QLabel("Source Directory:"), 0, 0)
        self.sync_source_edit = QLineEdit()
        dir_layout.addWidget(self.sync_source_edit, 0, 1)
        self.browse_sync_source_button = QPushButton("Browse")
        self.browse_sync_source_button.clicked.connect(self.browse_sync_source)
        dir_layout.addWidget(self.browse_sync_source_button, 0, 2)

        # Destination directory
        dir_layout.addWidget(QLabel("Destination Directory:"), 1, 0)
        self.sync_dest_edit = QLineEdit()
        dir_layout.addWidget(self.sync_dest_edit, 1, 1)
        self.browse_sync_dest_button = QPushButton("Browse")
        self.browse_sync_dest_button.clicked.connect(self.browse_sync_dest)
        dir_layout.addWidget(self.browse_sync_dest_button, 1, 2)

        layout.addWidget(dir_group)

        # Sync options
        options_group = QGroupBox("Synchronization Options")
        options_layout = QVBoxLayout(options_group)

        self.bidirectional_check = QCheckBox("Bidirectional sync")
        options_layout.addWidget(self.bidirectional_check)

        self.delete_extra_check = QCheckBox(
            "Delete extra files in destination"
        )
        options_layout.addWidget(self.delete_extra_check)

        self.backup_check = QCheckBox("Create backup before sync")
        options_layout.addWidget(self.backup_check)

        layout.addWidget(options_group)

        # Execute button
        self.sync_button = QPushButton("Start Synchronization")
        self.sync_button.clicked.connect(self.execute_sync)
        self.sync_button.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        layout.addWidget(self.sync_button)

        self.tab_widget.addTab(tab, "Sync")

    def _create_delete_tab(self):
        """Create the delete operations tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Warning label
        warning_label = QLabel("⚠️ WARNING: Delete operations are permanent!")
        warning_label.setStyleSheet(
            """
            QLabel {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(warning_label)

        # Target selection
        target_group = QGroupBox("Target Selection")
        target_layout = QGridLayout(target_group)

        target_layout.addWidget(QLabel("Target Directory:"), 0, 0)
        self.delete_target_edit = QLineEdit()
        target_layout.addWidget(self.delete_target_edit, 0, 1)
        self.browse_delete_target_button = QPushButton("Browse")
        self.browse_delete_target_button.clicked.connect(
            self.browse_delete_target
        )
        target_layout.addWidget(self.browse_delete_target_button, 0, 2)

        layout.addWidget(target_group)

        # Delete options
        options_group = QGroupBox("Delete Options")
        options_layout = QVBoxLayout(options_group)

        self.delete_recursive_check = QCheckBox("Delete subdirectories")
        options_layout.addWidget(self.delete_recursive_check)

        self.confirm_delete_check = QCheckBox("Confirm each deletion")
        self.confirm_delete_check.setChecked(True)
        options_layout.addWidget(self.confirm_delete_check)

        layout.addWidget(options_group)

        # Execute button
        self.delete_button = QPushButton("Delete Files")
        self.delete_button.clicked.connect(self.execute_delete)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        layout.addWidget(self.delete_button)

        self.tab_widget.addTab(tab, "Delete")

    def _create_compare_tab(self):
        """Create the directory comparison tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Directory selection
        dir_group = QGroupBox(DIRECTORY_SELECTION)
        dir_layout = QGridLayout(dir_group)

        # First directory
        dir_layout.addWidget(QLabel("First Directory:"), 0, 0)
        self.compare_dir1_edit = QLineEdit()
        dir_layout.addWidget(self.compare_dir1_edit, 0, 1)
        self.browse_dir1_button = QPushButton("Browse")
        self.browse_dir1_button.clicked.connect(self.browse_compare_dir1)
        dir_layout.addWidget(self.browse_dir1_button, 0, 2)

        # Second directory
        dir_layout.addWidget(QLabel("Second Directory:"), 1, 0)
        self.compare_dir2_edit = QLineEdit()
        dir_layout.addWidget(self.compare_dir2_edit, 1, 1)
        self.browse_dir2_button = QPushButton("Browse")
        self.browse_dir2_button.clicked.connect(self.browse_compare_dir2)
        dir_layout.addWidget(self.browse_dir2_button, 1, 2)

        layout.addWidget(dir_group)

        # Compare button
        self.compare_button = QPushButton("Compare Directories")
        self.compare_button.clicked.connect(self.execute_compare)
        self.compare_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        layout.addWidget(self.compare_button)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Item", "Status", "Location"])
        layout.addWidget(self.results_tree)

        self.tab_widget.addTab(tab, "Compare")

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
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        progress_layout.addWidget(self.status_text)

        parent_layout.addWidget(progress_group)

    # Directory browsing methods
    def browse_source(self):
        """Browse for source directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Source Directory"
        )
        if directory:
            self.source_edit.setText(directory)

    def browse_destination(self):
        """Browse for destination directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory"
        )
        if directory:
            self.dest_edit.setText(directory)

    def browse_sync_source(self):
        """Browse for sync source directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Source Directory"
        )
        if directory:
            self.sync_source_edit.setText(directory)

    def browse_sync_dest(self):
        """Browse for sync destination directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory"
        )
        if directory:
            self.sync_dest_edit.setText(directory)

    def browse_delete_target(self):
        """Browse for delete target directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Target Directory"
        )
        if directory:
            self.delete_target_edit.setText(directory)

    def browse_compare_dir1(self):
        """Browse for first comparison directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select First Directory"
        )
        if directory:
            self.compare_dir1_edit.setText(directory)

    def browse_compare_dir2(self):
        """Browse for second comparison directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Second Directory"
        )
        if directory:
            self.compare_dir2_edit.setText(directory)

    # Operation execution methods
    def execute_copy_move(self):
        """Execute copy or move operation."""
        source = self.source_edit.text().strip()
        dest = self.dest_edit.text().strip()

        if not source or not dest:
            QMessageBox.warning(
                self,
                "Error",
                "Please select both source and destination directories.",
            )
            return

        if not os.path.exists(source):
            QMessageBox.warning(
                self, "Error", "Source directory does not exist."
            )
            return

        operation = "copy" if self.copy_radio.isChecked() else "move"

        # Start operation
        self._start_operation(operation, source=source, destination=dest)

    def execute_sync(self):
        """Execute synchronization operation."""
        source = self.sync_source_edit.text().strip()
        dest = self.sync_dest_edit.text().strip()

        if not source or not dest:
            QMessageBox.warning(
                self,
                "Error",
                "Please select both source and destination directories.",
            )
            return

        if not os.path.exists(source) or not os.path.exists(dest):
            QMessageBox.warning(
                self,
                "Error",
                "Both directories must exist for synchronization.",
            )
            return

        delete_extra = self.delete_extra_check.isChecked()

        # Start operation
        self._start_operation(
            "sync", source=source, destination=dest, delete_extra=delete_extra
        )

    def execute_delete(self):
        """Execute delete operation."""
        target = self.delete_target_edit.text().strip()

        if not target:
            QMessageBox.warning(
                self, "Error", "Please select a target directory."
            )
            return

        if not os.path.exists(target):
            QMessageBox.warning(
                self, "Error", "Target directory does not exist."
            )
            return

        # Confirm deletion
        if self.confirm_delete_check.isChecked():
            message = (
                f"Are you sure you want to delete files in:\n{target}\n\n"
                "This operation cannot be undone!"
            )
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        recursive = self.delete_recursive_check.isChecked()

        # Start operation
        self._start_operation("delete", target=target, recursive=recursive)

    def execute_compare(self):
        """Execute directory comparison."""
        dir1 = self.compare_dir1_edit.text().strip()
        dir2 = self.compare_dir2_edit.text().strip()

        if not dir1 or not dir2:
            QMessageBox.warning(
                self, "Error", "Please select both directories to compare."
            )
            return

        if not os.path.exists(dir1) or not os.path.exists(dir2):
            QMessageBox.warning(
                self, "Error", "Both directories must exist for comparison."
            )
            return

        # Clear previous results
        self.results_tree.clear()

        # Start operation
        self._start_operation("compare", dir1=dir1, dir2=dir2)

    def _start_operation(self, operation, **kwargs):
        """Start a background operation."""
        # Disable UI and show progress
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append(f"Starting {operation} operation...")

        # Start worker thread
        self.worker_thread = CMSDWorkerThread(operation, **kwargs)
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_text.append)
        self.worker_thread.finished.connect(self._operation_finished)
        self.worker_thread.start()

    def _operation_finished(self, success: bool, message: str, result):
        """Handle operation completion."""
        self._set_ui_enabled(True)
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "Success", message)
            self.status_text.append(f"✓ {message}")

            # Handle specific result types
            if isinstance(result, DirectoryComparison):
                self._display_comparison_results(result)
            elif isinstance(result, OperationResult):
                self._display_operation_results(result)

        else:
            QMessageBox.warning(self, "Error", message)
            self.status_text.append(f"✗ {message}")

        self.worker_thread = None

    def _display_comparison_results(self, comparison: DirectoryComparison):
        """Display directory comparison results."""
        self.results_tree.clear()

        # Only in first directory
        if comparison.only_left:
            only_left_item = QTreeWidgetItem(
                ["Only in First Directory", "", ""]
            )
            for item in comparison.only_left:
                child = QTreeWidgetItem([item, "Missing in second", "First"])
                only_left_item.addChild(child)
            self.results_tree.addTopLevelItem(only_left_item)
            only_left_item.setExpanded(True)

        # Only in second directory
        if comparison.only_right:
            only_right_item = QTreeWidgetItem(
                ["Only in Second Directory", "", ""]
            )
            for item in comparison.only_right:
                child = QTreeWidgetItem([item, "Missing in first", "Second"])
                only_right_item.addChild(child)
            self.results_tree.addTopLevelItem(only_right_item)
            only_right_item.setExpanded(True)

        # Common files
        if comparison.common:
            common_item = QTreeWidgetItem(["Common Files", "", ""])
            for item in comparison.common:
                child = QTreeWidgetItem([item, "Exists in both", "Both"])
                common_item.addChild(child)
            self.results_tree.addTopLevelItem(common_item)

    def _display_operation_results(self, result: OperationResult):
        """Display operation results in status text."""
        self.status_text.append(
            f"Processed files: {len(result.processed_files)}"
        )
        self.status_text.append(f"Failed files: {len(result.failed_files)}")
        self.status_text.append(f"Total bytes: {result.total_bytes:,}")

        if result.failed_files:
            self.status_text.append("\nFailed files:")
            for file_path, error in result.failed_files:
                self.status_text.append(f"  {file_path}: {error}")

    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI controls during operations."""
        self.copy_move_button.setEnabled(enabled)
        self.sync_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.compare_button.setEnabled(enabled)

        # Disable browse buttons
        browse_buttons = [
            self.browse_source_button,
            self.browse_dest_button,
            self.browse_sync_source_button,
            self.browse_sync_dest_button,
            self.browse_delete_target_button,
            self.browse_dir1_button,
            self.browse_dir2_button,
        ]
        for button in browse_buttons:
            button.setEnabled(enabled)

    def reset_form(self):
        """Reset the form to initial state."""
        # Clear all input fields
        self.source_edit.clear()
        self.dest_edit.clear()
        self.sync_source_edit.clear()
        self.sync_dest_edit.clear()
        self.delete_target_edit.clear()
        self.compare_dir1_edit.clear()
        self.compare_dir2_edit.clear()

        # Reset checkboxes
        self.copy_radio.setChecked(True)
        self.recursive_check.setChecked(True)
        self.overwrite_check.setChecked(False)
        self.bidirectional_check.setChecked(False)
        self.delete_extra_check.setChecked(False)
        self.backup_check.setChecked(False)
        self.delete_recursive_check.setChecked(False)
        self.confirm_delete_check.setChecked(True)

        # Clear results
        self.status_text.clear()
        self.results_tree.clear()
        self.progress_bar.setVisible(False)

    def show_help(self):
        """Show help information."""
        help_text = """
Copy/Move/Sync/Delete Tool Help

COPY/MOVE:
1. Select source and destination directories
2. Choose operation type (Copy or Move)
3. Configure options as needed
4. Click 'Execute Operation'

SYNCHRONIZATION:
1. Select source and destination directories
2. Configure sync options
3. Click 'Start Synchronization'

DELETE:
⚠️ WARNING: Delete operations are permanent!
1. Select target directory
2. Configure delete options
3. Confirm operation when prompted
4. Click 'Delete Files'

COMPARE:
1. Select two directories to compare
2. Click 'Compare Directories'
3. Review differences in the results tree

FEATURES:
- Background processing with progress indication
- Detailed operation logging
- Error reporting and recovery
- Safe operation confirmation dialogs
        """
        QMessageBox.information(self, "Help", help_text.strip())


def main():
    """Main entry point for standalone execution."""
    app = QApplication(sys.argv)
    window = CopyMoveSyncDeleteWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
