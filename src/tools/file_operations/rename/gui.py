"""
Enhanced File Rename GUI Wrapper

This module provides a PyQt5 GUI wrapper for the file renaming functionality
using the utilities logic framework.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.gui import menu_surfaces

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from PyQt5.QtCore import QMutex, QMutexLocker, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.gui.themes import token

# Import the standard window framework
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    try:
        from ....gui.standard_window import StandardWindow
    except ImportError:
        StandardWindow = QMainWindow

# Import rename logic
from .rename_logic import FileRenamer


@dataclass
class RenamePreview:
    """Preview of rename operation."""

    original_name: str
    new_name: str
    file_path: str
    is_valid: bool
    error_message: str = ""


class RenameWorkerThread(QThread):
    """Worker thread for rename operations."""

    # Signals
    progress_updated = pyqtSignal(int, str)  # progress, status
    operation_completed = pyqtSignal(str, bool, str)  # filename, success, msg
    batch_completed = pyqtSignal(int, int)  # successful, total
    error_occurred = pyqtSignal(str)

    def __init__(self, file_paths: List[str], rename_settings: Dict[str, Any]):
        super().__init__()
        self.file_paths = file_paths
        self.rename_settings = rename_settings
        self.renamer = FileRenamer()
        self.is_cancelled = False
        self._mutex = QMutex()

        # Connect renamer signals
        self.renamer.progress_updated.connect(self.progress_updated.emit)
        self.renamer.operation_completed.connect(self.operation_completed.emit)
        self.renamer.error_occurred.connect(self.error_occurred.emit)

    def run(self):
        """Execute rename operations."""
        try:
            successful_count = 0
            total_count = len(self.file_paths)

            for i, file_path in enumerate(self.file_paths):
                with QMutexLocker(self._mutex):
                    if self.is_cancelled:
                        break

                # Generate new name
                filename = Path(file_path).name
                new_name = self.renamer.generate_new_name(
                    filename,
                    self.rename_settings.get("mode", "prefix"),
                    self.rename_settings.get("text", ""),
                    self.rename_settings.get("date_format"),
                    file_path,
                    self.rename_settings.get("counter", i + 1),
                )

                # Perform rename
                result = self.renamer.rename_file(file_path, new_name)

                if result.success:
                    successful_count += 1
                    self.operation_completed.emit(
                        filename, True, "Renamed successfully"
                    )
                else:
                    self.operation_completed.emit(filename, False, result.error_message)

                # Update progress
                progress = int((i + 1) / total_count * 100)
                self.progress_updated.emit(progress, f"Processing {filename}")

            self.batch_completed.emit(successful_count, total_count)

        except Exception as e:
            self.error_occurred.emit(f"Batch rename error: {str(e)}")

    def cancel(self):
        """Cancel the operation."""
        with QMutexLocker(self._mutex):
            self.is_cancelled = True


class FileRenameWindow(StandardWindow):
    """Enhanced File Rename GUI with comprehensive functionality."""

    def __init__(self):
        super().__init__()
        _ui_bind(self, 'setWindowTitle', 'Legacy.se632e3a0880fb972')
        self.setGeometry(100, 100, 1200, 800)

        # Initialize components
        self.renamer = FileRenamer()
        self.worker_thread = None
        self.file_paths = []
        self.preview_data = []

        self.init_ui()
        self.connect_signals()
        self._ensure_exit_action_reference()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Configuration
        left_panel = self.create_config_panel()
        splitter.addWidget(left_panel)

        # Right panel - Files and Preview
        right_panel = self.create_preview_panel()
        splitter.addWidget(right_panel)

        # Bottom panel - Progress and controls
        bottom_panel = self.create_control_panel()
        main_layout.addWidget(bottom_panel)

        # Set splitter proportions
        splitter.setSizes([400, 800])

    def create_config_panel(self) -> QWidget:
        """Create the configuration panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File selection group
        file_group = _ui_widget(QGroupBox, 'Legacy.s1eef7fd26962e3d2', 'setTitle')
        file_layout = QVBoxLayout(file_group)

        # File selection buttons
        btn_layout = QHBoxLayout()
        self.btn_select_files = _ui_widget(QPushButton, 'Legacy.sff52da8b75c1415a', 'setText')
        _ui_bind(self.btn_select_files, 'setAccessibleName', 'Legacy.s582306e7fa513e63')
        self.btn_select_files.setMinimumHeight(44)
        self.btn_select_folder = _ui_widget(QPushButton, 'Legacy.se597da9c984517f8', 'setText')
        _ui_bind(self.btn_select_folder, 'setAccessibleName', 'Legacy.s36c788320a6a7305')
        self.btn_select_folder.setMinimumHeight(44)
        self.btn_clear_files = _ui_widget(QPushButton, 'Legacy.s83b12c2216efb4fd', 'setText')
        _ui_bind(self.btn_clear_files, 'setAccessibleName', 'Legacy.s91792e6c58ae0c94')
        self.btn_clear_files.setMinimumHeight(44)

        btn_layout.addWidget(self.btn_select_files)
        btn_layout.addWidget(self.btn_select_folder)
        btn_layout.addWidget(self.btn_clear_files)
        file_layout.addLayout(btn_layout)

        # File count label
        self.lbl_file_count = _ui_widget(QLabel, 'Legacy.s0c4ba345e8af497a', 'setText')
        file_layout.addWidget(self.lbl_file_count)

        layout.addWidget(file_group)

        # Rename mode group
        mode_group = _ui_widget(QGroupBox, 'Legacy.sca6d1819fb4b2a07', 'setTitle')
        mode_layout = QGridLayout(mode_group)

        # Mode selection
        mode_layout.addWidget(_ui_widget(QLabel, 'Legacy.s7ce1afa3f281b07b', 'setText'), 0, 0)
        self.combo_mode = QComboBox()
        _ui_bind(self.combo_mode, 'setAccessibleName', 'Legacy.s02e33d9e4d4013be')
        self.combo_mode.addItems(
            [
                "prefix",
                "suffix",
                "remove_prefix",
                "remove_suffix",
                "new_name",
                "lower",
                "upper",
                "title",
                "replace",
                "sequential",
                "date_prefix",
                "date_suffix",
                "metadata",
                "remove_extension",
                "change_extension",
            ]
        )
        mode_layout.addWidget(self.combo_mode, 0, 1)

        # Text input
        mode_layout.addWidget(_ui_widget(QLabel, 'Legacy.s796961b8f89ef6cd', 'setText'), 1, 0)
        self.edit_text = QLineEdit()
        _ui_bind(self.edit_text, 'setAccessibleName', 'Legacy.sc57b4ea341114a4e')
        _ui_bind(self.edit_text, 'setPlaceholderText', 'Legacy.s70492bd41d6b1eef')
        mode_layout.addWidget(self.edit_text, 1, 1)

        # Date format
        mode_layout.addWidget(_ui_widget(QLabel, 'Legacy.sa2c3d2e05607b0e6', 'setText'), 2, 0)
        self.edit_date_format = QLineEdit()
        _ui_bind(self.edit_date_format, 'setAccessibleName', 'Legacy.saf189a1d3172f8e4')
        _ui_bind(self.edit_date_format, 'setPlaceholderText', 'Legacy.sc2e065a67bc0ecbf')
        mode_layout.addWidget(self.edit_date_format, 2, 1)

        # Counter start
        mode_layout.addWidget(_ui_widget(QLabel, 'Legacy.s7143d1d7a7336ae7', 'setText'), 3, 0)
        self.spin_counter = QSpinBox()
        _ui_bind(self.spin_counter, 'setAccessibleName', 'Legacy.sbebb40c1f493084f')
        self.spin_counter.setMinimumHeight(44)
        self.spin_counter.setMinimum(1)
        self.spin_counter.setMaximum(9999)
        self.spin_counter.setValue(1)
        mode_layout.addWidget(self.spin_counter, 3, 1)

        layout.addWidget(mode_group)

        # Options group
        options_group = _ui_widget(QGroupBox, 'Legacy.sd0db8b5e364b6989', 'setTitle')
        options_layout = QVBoxLayout(options_group)

        self.chk_preview = _ui_widget(QCheckBox, 'Legacy.s7eee09f9a25b2b5c', 'setText')
        _ui_bind(self.chk_preview, 'setAccessibleName', 'Legacy.sae64023788829dc3')
        self.chk_preview.setMinimumHeight(44)
        self.chk_preview.setChecked(True)
        options_layout.addWidget(self.chk_preview)

        self.chk_backup = _ui_widget(QCheckBox, 'Legacy.s8cc8d8f9fadf60e7', 'setText')
        _ui_bind(self.chk_backup, 'setAccessibleName', 'Legacy.s8cc8d8f9fadf60e7')
        self.chk_backup.setMinimumHeight(44)
        options_layout.addWidget(self.chk_backup)

        self.chk_recursive = _ui_widget(QCheckBox, 'Legacy.s7fe3b250ab4b4940', 'setText')
        _ui_bind(self.chk_recursive, 'setAccessibleName', 'Legacy.sbab1e6b508c03514')
        self.chk_recursive.setMinimumHeight(44)
        options_layout.addWidget(self.chk_recursive)

        layout.addWidget(options_group)

        # Preview button
        self.btn_preview = _ui_widget(QPushButton, 'Legacy.s8da3a067a8cc5d09', 'setText')
        _ui_bind(self.btn_preview, 'setAccessibleName', 'Legacy.s1673bc0277de1db9')
        self.btn_preview.setMinimumHeight(44)
        self.btn_preview.setStyleSheet("QPushButton { font-weight: bold; }")
        layout.addWidget(self.btn_preview)

        layout.addStretch()
        return panel

    def create_preview_panel(self) -> QWidget:
        """Create the preview panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        _ui_bind(self.tab_widget, 'setAccessibleName', 'Legacy.s13c05d8f6d18fc3c')
        layout.addWidget(self.tab_widget)

        # Files tab
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)

        # File list
        files_layout.addWidget(_ui_widget(QLabel, 'Legacy.sa5b10b7bd507a96e', 'setText'))
        self.list_files = QListWidget()
        _ui_bind(self.list_files, 'setAccessibleName', 'Legacy.s67ebdcdd5dc43309')
        files_layout.addWidget(self.list_files)

        self.tab_widget.addTab(files_tab, "Files")

        # Preview tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        # Preview table
        preview_layout.addWidget(_ui_widget(QLabel, 'Legacy.s1d505c621288091e', 'setText'))
        self.table_preview = QTableWidget()
        _ui_bind(self.table_preview, 'setAccessibleName', 'Legacy.sb139eb9a8a1541ab')
        self.table_preview.setColumnCount(4)
        self.table_preview.setHorizontalHeaderLabels(
            ["Original Name", "New Name", "Status", "Path"]
        )

        # Configure table
        header = self.table_preview.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        preview_layout.addWidget(self.table_preview)

        self.tab_widget.addTab(preview_tab, "Preview")

        # Results tab
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)

        # Results text
        results_layout.addWidget(_ui_widget(QLabel, 'Legacy.s0f8e2efaa6600366', 'setText'))
        self.text_results = QTextEdit()
        _ui_bind(self.text_results, 'setAccessibleName', 'Legacy.s632f0d85bbf1b706')
        self.text_results.setReadOnly(True)
        self.text_results.setMaximumHeight(200)
        results_layout.addWidget(self.text_results)

        self.tab_widget.addTab(results_tab, "Results")

        return panel

    def create_control_panel(self) -> QWidget:
        """Create the control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.lbl_status = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        layout.addWidget(self.lbl_status)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.btn_rename = _ui_widget(QPushButton, 'Legacy.sb097eebdde7bd240', 'setText')
        _ui_bind(self.btn_rename, 'setAccessibleName', 'Legacy.sf563aa222ba05741')
        self.btn_rename.setMinimumHeight(44)
        self.btn_rename.setStyleSheet(
            """
            QPushButton {
                background-color: {token('semantic_success')};
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: {token('semantic_success')};
            }
        """
        )

        self.btn_cancel = _ui_widget(QPushButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.btn_cancel, 'setAccessibleName', 'Legacy.s587e9d4a8377a77b')
        self.btn_cancel.setMinimumHeight(44)
        self.btn_cancel.setEnabled(False)

        self.btn_reset = _ui_widget(QPushButton, 'Legacy.sdaee7606b339f3c3', 'setText')
        _ui_bind(self.btn_reset, 'setAccessibleName', 'Legacy.s5754456351064909')
        self.btn_reset.setMinimumHeight(44)

        btn_layout.addWidget(self.btn_rename)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        return panel

    def connect_signals(self):
        """Connect signals and slots."""
        # File selection
        self.btn_select_files.clicked.connect(self.select_files)
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_clear_files.clicked.connect(self.clear_files)

        # Configuration
        self.combo_mode.currentTextChanged.connect(self.on_mode_changed)
        self.edit_text.textChanged.connect(self.update_preview_availability)

        # Actions
        self.btn_preview.clicked.connect(self.generate_preview)
        self.btn_rename.clicked.connect(self.start_rename)
        self.btn_cancel.clicked.connect(self.cancel_rename)
        self.btn_reset.clicked.connect(self.reset_form)

    def select_files(self):
        """Select individual files."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Rename", "", "All Files (*)"
        )

        if files:
            self.file_paths.extend(files)
            self.update_file_list()

    def select_folder(self):
        """Select folder and get all files."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "")

        if folder:
            folder_path = Path(folder)
            files = []

            if self.chk_recursive.isChecked():
                files = list(folder_path.rglob("*"))
            else:
                files = list(folder_path.iterdir())

            # Filter to files only
            file_paths = [str(f) for f in files if f.is_file()]
            self.file_paths.extend(file_paths)
            self.update_file_list()

    def clear_files(self):
        """Clear selected files."""
        self.file_paths.clear()
        self.update_file_list()
        self.clear_preview()

    def update_file_list(self):
        """Update the file list display."""
        self.list_files.clear()

        for file_path in self.file_paths:
            self.list_files.addItem(Path(file_path).name)

        count = len(self.file_paths)
        self.lbl_file_count.setText(f"{count} file(s) selected")

        self.update_preview_availability()

    def on_mode_changed(self, mode: str):
        """Handle mode change."""
        # Enable/disable controls based on mode
        text_required = mode in [
            "prefix",
            "suffix",
            "remove_prefix",
            "remove_suffix",
            "new_name",
            "replace",
            "sequential",
            "change_extension",
        ]

        self.edit_text.setEnabled(text_required)

        date_required = mode in ["date_prefix", "date_suffix", "metadata"]
        self.edit_date_format.setEnabled(date_required)

        counter_required = mode == "sequential"
        self.spin_counter.setEnabled(counter_required)

        self.update_preview_availability()

    def update_preview_availability(self):
        """Update preview button availability."""
        has_files = len(self.file_paths) > 0
        mode = self.combo_mode.currentText()

        # Check if text is required but empty
        text_required = mode in [
            "prefix",
            "suffix",
            "remove_prefix",
            "remove_suffix",
            "new_name",
            "replace",
            "sequential",
            "change_extension",
        ]

        text_provided = bool(self.edit_text.text().strip()) or not text_required

        self.btn_preview.setEnabled(has_files and text_provided)
        self.btn_rename.setEnabled(has_files and text_provided)

    def generate_preview(self):
        """Generate rename preview."""
        if not self.file_paths:
            return

        self.preview_data.clear()
        settings = self.get_rename_settings()

        for i, file_path in enumerate(self.file_paths):
            try:
                filename = Path(file_path).name
                new_name = self.renamer.generate_new_name(
                    filename,
                    settings["mode"],
                    settings["text"],
                    settings.get("date_format"),
                    file_path,
                    settings.get("counter", i + 1),
                )

                # Validate rename
                is_valid, error_msg = self.renamer.validate_rename(file_path, new_name)

                preview = RenamePreview(
                    original_name=filename,
                    new_name=new_name,
                    file_path=file_path,
                    is_valid=is_valid,
                    error_message=error_msg,
                )

                self.preview_data.append(preview)

            except Exception as e:
                preview = RenamePreview(
                    original_name=Path(file_path).name,
                    new_name="ERROR",
                    file_path=file_path,
                    is_valid=False,
                    error_message=str(e),
                )
                self.preview_data.append(preview)

        self.update_preview_table()
        self.tab_widget.setCurrentIndex(1)  # Switch to preview tab

    def update_preview_table(self):
        """Update the preview table."""
        self.table_preview.setRowCount(len(self.preview_data))

        for row, preview in enumerate(self.preview_data):
            # Original name
            self.table_preview.setItem(row, 0, QTableWidgetItem(preview.original_name))

            # New name
            new_name_item = QTableWidgetItem(preview.new_name)
            if not preview.is_valid:
                new_name_item.setBackground(Qt.red)
            self.table_preview.setItem(row, 1, new_name_item)

            # Status
            status = "Valid" if preview.is_valid else preview.error_message
            status_item = QTableWidgetItem(status)
            if not preview.is_valid:
                status_item.setBackground(Qt.red)
            self.table_preview.setItem(row, 2, status_item)

            # Path
            self.table_preview.setItem(row, 3, QTableWidgetItem(preview.file_path))

    def clear_preview(self):
        """Clear preview data."""
        self.preview_data.clear()
        self.table_preview.setRowCount(0)
        self.text_results.clear()

    def get_rename_settings(self) -> Dict[str, Any]:
        """Get current rename settings."""
        return {
            "mode": self.combo_mode.currentText(),
            "text": self.edit_text.text(),
            "date_format": self.edit_date_format.text() or None,
            "counter": self.spin_counter.value(),
            "create_backup": self.chk_backup.isChecked(),
        }

    def start_rename(self):
        """Start the rename operation."""
        if not self.file_paths:
            QMessageBox.warning(self, "Warning", "No files selected")
            return

        # Show preview if enabled
        if self.chk_preview.isChecked() and not self.preview_data:
            self.generate_preview()
            reply = QMessageBox.question(
                self,
                "Confirm Rename",
                f"Rename {len(self.file_paths)} files?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

        # Disable controls
        self.btn_rename.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear results
        self.text_results.clear()

        # Start worker thread
        settings = self.get_rename_settings()
        self.worker_thread = RenameWorkerThread(self.file_paths, settings)

        # Connect signals
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.operation_completed.connect(self.on_operation_completed)
        self.worker_thread.batch_completed.connect(self.on_batch_completed)
        self.worker_thread.error_occurred.connect(self.on_error_occurred)

        self.worker_thread.start()

    def cancel_rename(self):
        """Cancel the rename operation."""
        if self.worker_thread:
            self.worker_thread.cancel()
            self.worker_thread.wait()

        self.on_operation_finished()

    def on_progress_updated(self, progress: int, status: str):
        """Handle progress update."""
        self.progress_bar.setValue(progress)
        self.lbl_status.setText(status)

    def on_operation_completed(self, filename: str, success: bool, message: str):
        """Handle individual operation completion."""
        status = "SUCCESS" if success else "FAILED"
        result_text = f"[{status}] {filename}: {message}\n"

        self.text_results.append(result_text)
        self.text_results.ensureCursorVisible()

    def on_batch_completed(self, successful: int, total: int):
        """Handle batch completion."""
        self.on_operation_finished()

        # Show summary
        failed = total - successful
        summary = f"\nRename completed: {successful} successful, {failed} failed out of {total} total"
        self.text_results.append(summary)

        # Switch to results tab
        self.tab_widget.setCurrentIndex(2)

        QMessageBox.information(
            self,
            "Rename Completed",
            f"Rename operation completed.\n{successful} files renamed successfully.\n{failed} files failed.",
        )

    def on_error_occurred(self, error_message: str):
        """Handle error."""
        self.text_results.append(f"[ERROR] {error_message}\n")
        QMessageBox.critical(self, "Error", error_message)

    def on_operation_finished(self):
        """Handle operation finishing."""
        self.btn_rename.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("Ready")

        if self.worker_thread:
            self.worker_thread = None

    def reset_form(self):
        """Reset the form to default state."""
        # Cancel any running operation
        if self.worker_thread:
            self.cancel_rename()

        # Clear data
        self.clear_files()
        self.clear_preview()

        # Reset controls
        self.combo_mode.setCurrentIndex(0)
        self.edit_text.clear()
        self.edit_date_format.clear()
        self.spin_counter.setValue(1)

        # Reset checkboxes
        self.chk_preview.setChecked(True)
        self.chk_backup.setChecked(False)
        self.chk_recursive.setChecked(False)

        # Reset status
        self.lbl_status.setText("Ready")
        self.text_results.clear()

    def ensure_exit_action_reference(self):
        """Expose exit action reference for compatibility checks."""
        return self._ensure_exit_action_reference()

    def _ensure_exit_action_reference(self):
        """Ensure the window exposes standard exit actions."""
        if hasattr(self, "actionexit"):
            return getattr(self, "actionExit", None)

        menubar = self.menuBar() if hasattr(self, "menuBar") else None
        if menubar is None:
            return None

        exit_action = self._find_exit_action(menubar)
        if exit_action is None:
            exit_action = self._create_exit_action(menubar)

        if exit_action is not None:
            setattr(self, "actionexit", exit_action)
            if not hasattr(self, "actionExit"):
                setattr(self, "actionExit", exit_action)
            return exit_action

        return getattr(self, "actionExit", None)

    def _find_exit_action(self, menubar):
        """Search for an existing exit action in the menu bar."""
        for top_action in menubar.actions():
            menu = top_action.menu()
            if menu is None:
                continue

            for action in menu.actions():
                label = self._normalize_action_text(action.text())
                if label in {"exit", "quit"}:
                    return action

        return None

    def _create_exit_action(self, menubar):
        """Create a fallback exit action when none exists."""
        file_menu = self._resolve_file_menu(menubar)
        if file_menu is None:
            return None

        exit_action = _ui_widget(QAction, 'Legacy.s2eb7984c42b97146', 'setText', self)
        exit_action.setShortcut("Ctrl+Q")
        _ui_bind(exit_action, 'setStatusTip', 'Legacy.s909d2d80aa165d77')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        return exit_action

    def _resolve_file_menu(self, menubar):
        """Return the File menu, creating it when required."""
        for action in menubar.actions():
            label = self._normalize_action_text(action.text())
            if label == "file":
                return action.menu()

        return menu_surfaces.add_menu(menubar, '&File')

    @staticmethod
    def _normalize_action_text(label: str) -> str:
        """Normalize menu text for comparisons."""
        return label.replace("&", "").strip().lower()

    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Close",
                "Rename operation is in progress. Cancel and close?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.cancel_rename()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    app.setApplicationName("File Rename Tool")

    # Set application style
    app.setStyle("Fusion")

    window = FileRenameWindow()
    window.show()

    sys.exit(app.exec_())


# Alias for backward compatibility and import resolution
EnhancedRenameWindow = FileRenameWindow


if __name__ == "__main__":
    main()
