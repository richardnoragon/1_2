"""File synchronization tool with multiple sync modes.

This module provides functionality to synchronize files between two directories
with support for mirror, update, and two-way synchronization modes.
"""

import logging
import os
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMessageBox

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow

    # For dialog functions, try both import paths
    try:
        from gui.common.dialogs import (
            get_existing_directory,
            show_error_dialog,
        )
    except ImportError:
        # Fallback functions if imports fail
        def show_error_dialog(parent, title, message):
            if Modal:
                Modal(title, message, ["OK"], parent).exec_()
            else:
                QMessageBox.critical(parent, title, message)

        def get_existing_directory(parent, caption):
            from PyQt5.QtWidgets import QFileDialog

            return QFileDialog.getExistingDirectory(parent, caption)

except ImportError:
    # Fallback to QMainWindow if StandardWindow not available
    from PyQt5.QtWidgets import QMainWindow

    StandardWindow = QMainWindow

    # Fallback functions for dialogs
    def show_error_dialog(parent, title, message):
        if Modal:
            Modal(title, message, ["OK"], parent).exec_()
        else:
            QMessageBox.critical(parent, title, message)

    def get_existing_directory(parent, caption):
        from PyQt5.QtWidgets import QFileDialog

        return QFileDialog.getExistingDirectory(parent, caption)


try:
    from src.gui.themes import ThemeManager, token
except ImportError:
    ThemeManager = None
    token = None

try:
    from PyQt5.QtWidgets import QDialog

    from src.gui.components.modal import ConfirmationModal, Modal
except ImportError:
    Modal = None
    ConfirmationModal = None
    QDialog = None

try:
    from src.gui.components.toast import ToastNotification
except ImportError:
    ToastNotification = None

try:
    from src.gui.components.loading_indicator import LoadingIndicator
except ImportError:
    LoadingIndicator = None

# GRD-1a: ComponentGuardian registration (graceful fallback)
try:
    from src.core.guardian import register_gui_component

    _COMPONENT_GUARDIAN_AVAILABLE = True
except ImportError:
    _COMPONENT_GUARDIAN_AVAILABLE = False

    def register_gui_component(widget, component_type=None, recovery_callback=None):
        """No-op stub used when ComponentGuardian is unavailable."""
        return ""


# TEL-1/2/3/4: UI telemetry (spec §9.3)
try:
    from src.gui.telemetry import emit_telemetry as _emit_telemetry

    _TELEMETRY_AVAILABLE = True
except ImportError:
    _TELEMETRY_AVAILABLE = False

    def _emit_telemetry(event_type: str, *, tool_id: str, **kwargs) -> None:
        """No-op stub used when ui_telemetry module is unavailable."""


try:
    from src.rfu.ui_strings import SynchronizationBackup as _SyncStrings
except ImportError:

    class _SyncStrings:
        TITLE = "Synchronization & Backup"
        LOADING = "Loading Synchronization & Backup\u2026"
        DRY_RUN_LABEL = "Dry Run (Preview Only)"
        WINDOW_TITLE = "Synchronize - Richard's File Utilities"
        LABEL_NO_DIR_SELECTED = "No directory selected"
        STATUS_COMPARISON_COMPLETE = "Comparison complete \u2014 ready to sync"
        STATUS_SYNC_COMPLETE = "Synchronization complete!"
        STATUS_DRY_RUN_COMPLETE = "Dry run complete \u2014 no files were modified"
        EMPTY_STATE_NO_FILES = "No files to display \u2014 select a directory first."
        ERR_CANNOT_READ_DIR = (
            "Could not read the selected directory. "
            "Check that the folder exists and you have permission to access it."
        )
        ERR_CANNOT_COMPARE = (
            "Could not compare the directories. "
            "Check that both folders are accessible and try again."
        )
        ERR_CANNOT_START_SYNC = (
            "Could not start the sync operation. "
            "Check that both directories are accessible and try again."
        )
        ERR_SYNC_FAILED = (
            "Synchronization encountered an error. "
            "Some files may not have been copied. Check the log for details."
        )


class SyncWorker(QThread):
    """A class that handles sync worker and inherits from QThread."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    preview = pyqtSignal(str, str, str)  # action, source, target

    def __init__(
        self,
        source_files: Dict[str, Any],
        target_files: Dict[str, Any],
        source_dir: str,
        target_dir: str,
        options: Dict[str, Any],
    ) -> None:
        """Initialize the SyncWorker.

        Args:
            source_files: Source files dictionary
            target_files: Target files dictionary
            source_dir: Source directory path
            target_dir: Target directory path
            options: Sync options
        """
        super().__init__()
        self.source_files: Dict[str, Any] = source_files
        self.target_files: Dict[str, Any] = target_files
        self.source_dir: str = source_dir
        self.target_dir: str = target_dir
        self.options: Dict[str, Any] = options
        self.running: bool = True

    def backup_file(self, file_path: str) -> None:
        """Create a backup of the specified file.

        Args:
            file_path: Path to the file to backup
        """
        if not self.options.get("backup", False):
            return
        backup_path: str = f"{file_path}.bak"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            base_name: str = os.path.basename(backup_path)
            self.status.emit(f"Backup created: {base_name}")

    def should_copy_file(self, src_path: str, tgt_path: str) -> Tuple[bool, str]:
        """Determine if a file should be copied based on sync rules.

        Args:
            src_path: Source file path
            tgt_path: Target file path

        Returns:
            Tuple of (should_copy, reason)
        """
        if not os.path.exists(tgt_path):
            return True, "new"

        src_time: float = os.path.getmtime(src_path)
        tgt_time: float = os.path.getmtime(tgt_path)

        if src_time == tgt_time:
            return False, "identical"

        conflict_resolution: str = self.options.get("conflict_resolution", "newest")

        if conflict_resolution == "newest":
            is_newer: bool = src_time > tgt_time
            return is_newer, "newer" if is_newer else "older"
        elif conflict_resolution == "source":
            return True, "source wins"
        elif conflict_resolution == "target":
            return False, "target wins"

        return False, "skipped"

    def run(self) -> None:
        """Execute the synchronization process."""
        try:
            sync_mode: str = self.options.get("sync_mode", "mirror")

            if sync_mode == "mirror":
                self.mirror_sync()
            elif sync_mode == "update":
                self.update_sync()
            else:  # two-way sync
                self.two_way_sync()

            if not self.options.get("dry_run", False):
                self.status.emit("Synchronization complete!")
            else:
                self.status.emit("Dry run complete - no files were modified")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def mirror_sync(self) -> None:
        """Perform mirror synchronization.

        Target becomes identical to source.
        """
        total_files: int = len(self.source_files)

        for idx, file in enumerate(self.source_files):
            if not self.running:
                return

            self._process_source_file_for_mirror(file)
            self.progress.emit(int((idx + 1) * 100 / total_files))

        self._remove_extra_target_files()

    def _process_source_file_for_mirror(self, file: str) -> None:
        """Process a single source file for mirror sync."""
        source_path: str = os.path.join(self.source_dir, file)
        target_path: str = os.path.join(self.target_dir, file)

        should_copy, _ = self.should_copy_file(source_path, target_path)

        if should_copy:
            self.preview.emit("COPY", source_path, target_path)
            if not self.options.get("dry_run", False):
                self.backup_file(target_path)
                shutil.copy2(source_path, target_path)
                self.status.emit(f"Copied: {file}")

    def _remove_extra_target_files(self) -> None:
        """Remove files in target that don't exist in source."""
        for file in self.target_files:
            if file not in self.source_files:
                target_path = os.path.join(self.target_dir, file)
                self.preview.emit("DELETE", "", target_path)
                if not self.options.get("dry_run", False):
                    os.remove(target_path)
                    self.status.emit(f"Deleted: {file}")

    def update_sync(self) -> None:
        """Perform update synchronization.

        Only copy newer files to target.
        """
        total_files: int = len(self.source_files)

        for idx, file in enumerate(self.source_files):
            if not self.running:
                return

            self._process_file_for_update(file)
            self.progress.emit(int((idx + 1) * 100 / total_files))

    def _process_file_for_update(self, file: str) -> None:
        """Process a single file for update sync."""
        source_path: str = os.path.join(self.source_dir, file)
        target_path: str = os.path.join(self.target_dir, file)

        should_copy, reason = self.should_copy_file(source_path, target_path)
        skip_newer: bool = self.options.get("skip_newer", False)

        if should_copy and (not skip_newer or reason == "new"):
            self.preview.emit("COPY", source_path, target_path)
            if not self.options.get("dry_run", False):
                self.backup_file(target_path)
                shutil.copy2(source_path, target_path)
                self.status.emit(f"Copied: {file}")

    def two_way_sync(self) -> None:
        """Perform two-way synchronization.

        Both directories synchronized.
        """
        all_files: set[str] = set(self.source_files) | set(self.target_files)
        total_files: int = len(all_files)

        for idx, file in enumerate(all_files):
            if not self.running:
                return

            self._process_file_for_two_way(file)
            self.progress.emit(int((idx + 1) * 100 / total_files))

    def _process_file_for_two_way(self, file: str) -> None:
        """Process a single file for two-way sync."""
        source_path: str = os.path.join(self.source_dir, file)
        target_path: str = os.path.join(self.target_dir, file)

        file_location = self._get_file_location(file)

        if file_location == "source_only":
            self._copy_to_target(file, source_path, target_path)
        elif file_location == "target_only":
            self._copy_to_source(file, target_path, source_path)
        elif file_location == "both":
            self._sync_existing_files(file, source_path, target_path)

    def _get_file_location(self, file: str) -> str:
        """Determine where the file exists."""
        if file in self.source_files and file not in self.target_files:
            return "source_only"
        elif file in self.target_files and file not in self.source_files:
            return "target_only"
        else:
            return "both"

    def _copy_to_target(self, file: str, source_path: str, target_path: str) -> None:
        """Copy file from source to target."""
        self.preview.emit("COPY", source_path, target_path)
        if not self.options.get("dry_run", False):
            shutil.copy2(source_path, target_path)
            self.status.emit(f"Copied to target: {file}")

    def _copy_to_source(self, file: str, target_path: str, source_path: str) -> None:
        """Copy file from target to source."""
        self.preview.emit("COPY", target_path, source_path)
        if not self.options.get("dry_run", False):
            shutil.copy2(target_path, source_path)
            self.status.emit(f"Copied to source: {file}")

    def _sync_existing_files(
        self, file: str, source_path: str, target_path: str
    ) -> None:
        """Sync files that exist in both locations."""
        source_time: float = os.path.getmtime(source_path)
        target_time: float = os.path.getmtime(target_path)

        if source_time > target_time:
            self._update_target_file(file, source_path, target_path)
        elif target_time > source_time:
            self._update_source_file(file, target_path, source_path)

    def _update_target_file(
        self, file: str, source_path: str, target_path: str
    ) -> None:
        """Update target file with newer source."""
        self.preview.emit("COPY", source_path, target_path)
        if not self.options.get("dry_run", False):
            self.backup_file(target_path)
            shutil.copy2(source_path, target_path)
            self.status.emit(f"Updated target: {file}")

    def _update_source_file(
        self, file: str, target_path: str, source_path: str
    ) -> None:
        """Update source file with newer target."""
        self.preview.emit("COPY", target_path, source_path)
        if not self.options.get("dry_run", False):
            self.backup_file(source_path)
            shutil.copy2(target_path, source_path)
            self.status.emit(f"Updated source: {file}")

    def stop(self) -> None:
        """Stop the synchronization process."""
        self.running = False


class SyncWindow(StandardWindow):
    """Main window for file synchronization operations."""

    def __init__(self, hub_instance=None) -> None:
        """Initialize the sync window.

        Args:
            hub_instance: Optional reference to the parent hub window.
        """
        self._hub_instance = hub_instance
        _title = _SyncStrings.WINDOW_TITLE
        try:
            super().__init__(
                title=_title,
                window_type="utility",
            )
        except TypeError:
            super().__init__()
            self.setWindowTitle(_title)

        # ERR-5a: centralised logger for technical detail
        try:
            from src.core.log_manager import get_log_manager as _get_lm

            self._logger = _get_lm().get_logger("SynchronizationBackup")
        except Exception:
            self._logger = logging.getLogger("SynchronizationBackup")

        ui_file: str = os.path.join(os.path.dirname(__file__), "sync.ui")
        uic.loadUi(ui_file, self)
        if hasattr(self, "dry_run_checkbox"):
            self.dry_run_checkbox.setText(_SyncStrings.DRY_RUN_LABEL)

        self._setup_menu_callbacks()

        # Initialize models
        self.left_model: QStandardItemModel = QStandardItemModel()
        self.right_model: QStandardItemModel = QStandardItemModel()
        self.left_listView.setModel(self.left_model)
        self.right_listView.setModel(self.right_model)

        # Setup menu actions
        self.actionExit = self.menuExit.addAction("Exit")
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(self.close)
        if hasattr(self, "ensure_exit_action_reference"):
            self.ensure_exit_action_reference()

        # Connect buttons
        self.select_left_pushButton.clicked.connect(
            lambda: self.select_directory("left")
        )
        self.select_right_pushButton.clicked.connect(
            lambda: self.select_directory("right")
        )
        self.compare_pushButton.clicked.connect(self.compare_directories)
        self.sync_pushButton.clicked.connect(self.sync_directories)

        # Initialize variables
        self.left_dir: str = ""
        self.right_dir: str = ""
        self.sync_worker: Optional[SyncWorker] = None

        # Initial state
        self.sync_pushButton.setEnabled(False)
        self.compare_pushButton.setEnabled(False)
        self.progress_bar.setValue(0)

        # Register theme-change callback
        if ThemeManager:
            ThemeManager.add_theme_changed_callback(self._on_theme_changed)

        # Apply initial token-based stylesheet
        self._on_theme_changed("light")
        self._toast = (
            ToastNotification(self, role="info") if ToastNotification else None
        )
        # Loading indicator (spec §8.1, CP-6b / CP-7b/c)
        self._loading_indicator = None
        if LoadingIndicator and self.centralWidget():
            self._loading_indicator = LoadingIndicator(
                self.centralWidget(),
                cancellable=True,
                message="Syncing files...",
            )
            _central_layout = self.centralWidget().layout()
            if _central_layout:
                _central_layout.insertWidget(0, self._loading_indicator)

        # GRD-1b/c: register with ComponentGuardian
        self._guardian_id = register_gui_component(
            self,
            component_type="tool_window",
            recovery_callback=self.degraded_fallback,
        )

        # TEL-1b: view_load telemetry
        _emit_telemetry(
            "ui_view_load",
            tool_id="synchronization_backup",
        )

        # Only auto-show when running standalone (not embedded in hub)
        if hub_instance is None:
            self.show()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_sync", self.clear_sync)
            self.menu_manager.register_callback("help_sync", self.show_help)

    def _on_theme_changed(self, variant: str) -> None:
        """Handle theme change — re-apply token-based stylesheet."""
        if not token:
            return
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {token('surface')};
            }}
            QPushButton {{
                background-color: {token('button_primary')};
                color: {token('text_on_primary')};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {token('button_primary_hover')};
            }}
            QPushButton:pressed {{
                background-color: {token('button_primary_pressed')};
            }}
            QLabel {{
                color: {token('text_primary')};
                font-size: 12px;
            }}
            QListView {{
                background-color: {token('window_background')};
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 4px;
            }}
            QProgressBar {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                text-align: center;
            }}
        """
        )
        if hasattr(self, "sync_pushButton"):
            self.sync_pushButton._apply_style()
        if hasattr(self, "select_left_pushButton"):
            self.select_left_pushButton._apply_style()
        if hasattr(self, "compare_pushButton"):
            self.compare_pushButton._apply_style()
        if hasattr(self, "select_right_pushButton"):
            self.select_right_pushButton._apply_style()

    def clear_sync(self):
        """Clear all sync operations for a new task."""
        # Clear the directory selections and file lists
        self.left_dir = ""
        self.right_dir = ""
        self.left_directory_label.setText(_SyncStrings.LABEL_NO_DIR_SELECTED)
        self.right_directory_label.setText(_SyncStrings.LABEL_NO_DIR_SELECTED)
        self.left_model.clear()
        self.right_model.clear()
        self.sync_pushButton.setEnabled(False)
        self.compare_pushButton.setEnabled(False)
        self.progress_bar.setValue(0)

    def show_help(self):
        """Show help dialog for Synchronize tool."""
        help_text = """
        <h2>Synchronize Tool - Help</h2>
        
        <h3>Directory Synchronization:</h3>
        <ul>
        <li><b>Left Directory:</b> The source directory to sync from</li>
        <li><b>Right Directory:</b> The target directory to sync to</li>
        <li><b>Compare:</b> Analyze differences between directories</li>
        <li><b>Sync:</b> Execute the synchronization operation</li>
        </ul>
        
        <h3>Sync Modes:</h3>
        <ul>
        <li><b>Mirror Sync:</b> Make target identical to source</li>
        <li><b>Update Sync:</b> Copy newer files only</li>
        <li><b>Two-way Sync:</b> Synchronize both directions</li>
        </ul>
        
        <h3>Features:</h3>
        <ul>
        <li>Visual directory comparison</li>
        <li>Real-time progress tracking</li>
        <li>Detailed sync reports</li>
        <li>Safe file operations with verification</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear sync operations</li>
        </ul>
        """

        Modal("Synchronize Help", help_text, ["OK"], self).exec_()

    def select_directory(self, side: str) -> None:
        """Select a directory for synchronization.

        Args:
            side: Either 'left' or 'right' to indicate which directory
        """
        # TEL-2b: KEY_ACTION — Select Directory
        _emit_telemetry(
            "ui_user_action",
            tool_id="synchronization_backup",
            action=f"select_{side}_directory",
        )
        directory: str = get_existing_directory(self, "Select Directory")
        if directory:
            if side == "left":
                self.left_dir = directory
                self.left_directory_label.setText(directory)
                self.update_file_list(self.left_model, directory)
            else:
                self.right_dir = directory
                self.right_directory_label.setText(directory)
                self.update_file_list(self.right_model, directory)

            # Enable compare if both directories are selected
            both_dirs: bool = bool(self.left_dir and self.right_dir)
            self.compare_pushButton.setEnabled(both_dirs)

    def update_file_list(self, model: QStandardItemModel, directory: str) -> None:
        """Update the file list for the specified model and directory.

        Args:
            model: The QStandardItemModel to update
            directory: The directory path to list files from
        """
        model.clear()
        try:
            files: List[str] = sorted(os.listdir(directory))
            for file in files:
                file_path: str = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    item: QStandardItem = QStandardItem(file)
                    item.setToolTip(self.get_file_info(file_path))
                    model.appendRow(item)
        except OSError as e:
            # ERR-5a: log technical detail; ERR-4b: show user-friendly message
            self._logger.error(
                "Could not read directory %s: %s", directory, e, exc_info=True
            )
            _emit_telemetry(
                "ui_error_event",
                tool_id="synchronization_backup",
                error_code="cannot_read_directory",
            )
            show_error_dialog(
                message=_SyncStrings.ERR_CANNOT_READ_DIR,
                title=_SyncStrings.TITLE,
                parent=self,
            )

    def get_file_info(self, file_path: str) -> str:
        """Get formatted file information for display.

        Args:
            file_path: Path to the file

        Returns:
            Formatted string with file size and modification time
        """
        try:
            stats: os.stat_result = os.stat(file_path)
            modified: str = datetime.fromtimestamp(stats.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            size: str = self.format_size(stats.st_size)
            return f"Size: {size}\nModified: {modified}"
        except OSError:
            return "Could not read file info"

    def format_size(self, size: int) -> str:
        """Format file size in human-readable format.

        Args:
            size: File size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def compare_directories(self) -> None:
        """Compare the contents of both selected directories."""
        if not (self.left_dir and self.right_dir):
            return

        # TEL-2b: KEY_ACTION — Compare
        _emit_telemetry(
            "ui_user_action",
            tool_id="synchronization_backup",
            action="compare_directories",
        )
        try:
            left_files: set[str] = set(os.listdir(self.left_dir))
            right_files: set[str] = set(os.listdir(self.right_dir))

            # Reset models
            self.left_model.clear()
            self.right_model.clear()

            # Process all files
            all_files: List[str] = sorted(left_files.union(right_files))
            for file in all_files:
                left_path: str = os.path.join(self.left_dir, file)
                right_path: str = os.path.join(self.right_dir, file)

                # Add to left list
                self._add_list_item(
                    file,
                    left_path,
                    right_path,
                    file in left_files,
                    file in right_files,
                    self.left_model,
                    is_left=True,
                )

                # Add to right list
                self._add_list_item(
                    file,
                    right_path,
                    left_path,
                    file in right_files,
                    file in left_files,
                    self.right_model,
                    is_left=False,
                )

            self.sync_pushButton.setEnabled(True)
            if self._toast:
                self._toast.show_message(
                    _SyncStrings.STATUS_COMPARISON_COMPLETE, "info"
                )
            else:
                self.status_label.setText(_SyncStrings.STATUS_COMPARISON_COMPLETE)
        except OSError as e:
            # ERR-5a: log technical detail; ERR-4b: show user-friendly message
            self._logger.error("Could not compare directories: %s", e, exc_info=True)
            _emit_telemetry(
                "ui_error_event",
                tool_id="synchronization_backup",
                error_code="cannot_compare_directories",
            )
            show_error_dialog(
                message=_SyncStrings.ERR_CANNOT_COMPARE,
                title=_SyncStrings.TITLE,
                parent=self,
            )

    def _add_list_item(
        self,
        file: str,
        path1: str,
        path2: str,
        in_first: bool,
        in_second: bool,
        model: QStandardItemModel,
        is_left: bool,
    ) -> None:
        """Add a file item to the specified model with appropriate styling.

        Args:
            file: The filename
            path1: First file path for comparison
            path2: Second file path for comparison
            in_first: Whether file exists in first directory
            in_second: Whether file exists in second directory
            model: The QStandardItemModel to add to
            is_left: Whether this is for the left panel
        """
        if not in_first:
            return

        item: QStandardItem = QStandardItem(file)
        if not in_second:
            # Blue for new files
            item.setForeground(QColor("#2196F3"))
            item.setToolTip("New file")
        elif os.path.exists(path1) and os.path.exists(path2):
            time1: float = os.path.getmtime(path1)
            time2: float = os.path.getmtime(path2)
            if time1 > time2:
                # Green for newer files
                item.setForeground(QColor("#4CAF50"))
                item.setToolTip("Newer version")
            elif time1 < time2:
                # Orange for older files
                item.setForeground(QColor("#FF5722"))
                item.setToolTip("Older version")
        model.appendRow(item)

    def get_sync_options(self) -> Dict[str, Any]:
        """Get the current sync options from the UI.

        Returns:
            Dictionary containing sync configuration options
        """
        # Get sync mode
        if hasattr(self, "mirror_radio") and self.mirror_radio.isChecked():
            sync_mode: str = "mirror"
        elif hasattr(self, "update_radio") and self.update_radio.isChecked():
            sync_mode = "update"
        else:
            sync_mode = "two-way"

        # Get conflict resolution
        if hasattr(self, "source_radio") and self.source_radio.isChecked():
            conflict_resolution: str = "source"
        elif hasattr(self, "target_radio") and self.target_radio.isChecked():
            conflict_resolution = "target"
        else:
            conflict_resolution = "newest"

        return {
            "sync_mode": sync_mode,
            "conflict_resolution": conflict_resolution,
            "backup": (
                hasattr(self, "backup_checkbox") and self.backup_checkbox.isChecked()
            ),
            "dry_run": (
                hasattr(self, "dry_run_checkbox") and self.dry_run_checkbox.isChecked()
            ),
            "skip_newer": (
                hasattr(self, "skip_newer_checkbox")
                and self.skip_newer_checkbox.isChecked()
            ),
        }

    def sync_directories(self) -> None:
        """Start the directory synchronization process."""
        if not (self.left_dir and self.right_dir):
            return

        # TEL-2b: KEY_ACTION — Sync
        _emit_telemetry(
            "ui_user_action",
            tool_id="synchronization_backup",
            action="sync_directories",
        )

        options: Dict[str, Any] = self.get_sync_options()

        if not self._confirm_sync_operation(options):
            return

        try:
            self._prepare_and_start_sync(options)
        except OSError as e:
            self._handle_sync_start_error(e)

    def _confirm_sync_operation(self, options: Dict[str, Any]) -> bool:
        """Show confirmation dialog for sync operation."""
        message = self._build_confirmation_message(options)

        return (
            ConfirmationModal(
                "Confirm Sync",
                "\n".join(message),
                confirm_text="Yes",
                cancel_text="Cancel",
                parent=self,
            ).exec_()
            == QDialog.Accepted
        )

    def _build_confirmation_message(self, options: Dict[str, Any]) -> List[str]:
        """Build confirmation message based on sync options."""
        message: List[str] = ["Please confirm the following sync operation:\n"]

        # Add sync mode description
        if options["sync_mode"] == "mirror":
            message.append("- Mirror Mode: Target will be made identical to source")
        elif options["sync_mode"] == "update":
            message.append("- Update Mode: Only copy newer files to target")
        else:
            message.append("- Two-Way Sync: Both directories will be synchronized")

        message.append(
            f"- Conflict Resolution: {options['conflict_resolution'].title()}"
        )

        # Add optional features
        if options["backup"]:
            message.append("- Backup files will be created before overwriting")
        if options["dry_run"]:
            message.append("- DRY RUN: No files will be modified")
        if options["skip_newer"]:
            message.append("- Existing newer files will be skipped")

        message.append("\nContinue with these settings?")
        return message

    def _prepare_and_start_sync(self, options: Dict[str, Any]) -> None:
        """Prepare file lists and start sync worker."""
        # TEL-4a: performance metric — sync start
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="synchronization_backup",
            operation="sync",
            phase="start",
        )
        left_files, right_files = self._get_file_lists()

        self.sync_worker = SyncWorker(
            left_files, right_files, self.left_dir, self.right_dir, options
        )

        self._connect_worker_signals()
        self._disable_ui_during_sync()
        self.sync_worker.start()

    def _get_file_lists(self) -> Tuple[List[str], List[str]]:
        """Get file lists from both directories."""
        left_files: List[str] = [
            f
            for f in os.listdir(self.left_dir)
            if os.path.isfile(os.path.join(self.left_dir, f))
        ]
        right_files: List[str] = [
            f
            for f in os.listdir(self.right_dir)
            if os.path.isfile(os.path.join(self.right_dir, f))
        ]
        return left_files, right_files

    def _connect_worker_signals(self) -> None:
        """Connect sync worker signals to UI handlers."""
        self.sync_worker.progress.connect(self.progress_bar.setValue)
        self.sync_worker.status.connect(self.status_label.setText)
        self.sync_worker.error.connect(self.handle_error)
        self.sync_worker.finished.connect(self.sync_finished)
        self.sync_worker.preview.connect(self.show_preview)

        # Loading indicator wiring (spec §8.1, CP-6c/d / CP-7c)
        if self._loading_indicator:
            self.sync_worker.started.connect(self._loading_indicator.start)
            self.sync_worker.finished.connect(self._loading_indicator.stop)
            self._loading_indicator.cancelled.connect(self.sync_worker.stop)

    def _disable_ui_during_sync(self) -> None:
        """Disable UI elements during synchronization."""
        self.sync_pushButton.setEnabled(False)
        self.compare_pushButton.setEnabled(False)
        self.select_left_pushButton.setEnabled(False)
        self.select_right_pushButton.setEnabled(False)

        # Disable option groups if they exist
        for group_name in [
            "sync_mode_group",
            "conflict_group",
            "additional_options_group",
        ]:
            if hasattr(self, group_name):
                getattr(self, group_name).setEnabled(False)

    def _handle_sync_start_error(self, error: OSError) -> None:
        """Handle errors when starting sync operation."""
        # ERR-5a: log technical detail; ERR-4b: show user-friendly message
        self._logger.error("Could not start sync operation: %s", error, exc_info=True)
        _emit_telemetry(
            "ui_error_event",
            tool_id="synchronization_backup",
            error_code="cannot_start_sync",
        )
        show_error_dialog(
            message=_SyncStrings.ERR_CANNOT_START_SYNC,
            title=_SyncStrings.TITLE,
            parent=self,
        )

    def show_preview(self, action: str, source: str, target: str) -> None:
        """Show a preview of the sync operation.

        Args:
            action: The sync action (COPY or DELETE)
            source: Source file path
            target: Target file path
        """
        if action == "COPY":
            msg: str = (
                f"Would copy: {os.path.basename(source)} -> "
                f"{os.path.basename(target)}"
            )
            self.status_label.setText(msg)
        elif action == "DELETE":
            msg = f"Would delete: {os.path.basename(target)}"
            self.status_label.setText(msg)

    def sync_finished(self) -> None:
        """Handle completion of the synchronization process."""
        # TEL-4b: performance metric — sync stop
        _emit_telemetry(
            "ui_performance_metric",
            tool_id="synchronization_backup",
            operation="sync",
            phase="stop",
        )
        # TEL-2b: KEY_ACTION — Sync Complete
        _emit_telemetry(
            "ui_user_action",
            tool_id="synchronization_backup",
            action="sync_complete",
        )
        # Re-enable all UI elements
        self.sync_pushButton.setEnabled(True)
        self.compare_pushButton.setEnabled(True)
        self.select_left_pushButton.setEnabled(True)
        self.select_right_pushButton.setEnabled(True)

        # Re-enable options
        if hasattr(self, "sync_mode_group"):
            self.sync_mode_group.setEnabled(True)
        if hasattr(self, "conflict_group"):
            self.conflict_group.setEnabled(True)
        if hasattr(self, "additional_options_group"):
            self.additional_options_group.setEnabled(True)

        self.compare_directories()  # Refresh the comparison

    def handle_error(self, error_msg: str) -> None:
        """Handle synchronization errors.

        Args:
            error_msg: The technical error message from the sync worker.
        """
        # ERR-5a: log technical detail
        self._logger.error("Sync worker error: %s", error_msg)
        # TEL-3a: error telemetry
        _emit_telemetry(
            "ui_error_event",
            tool_id="synchronization_backup",
            error_code="sync_worker_error",
        )
        # ERR-4b: show user-friendly message
        show_error_dialog(
            message=_SyncStrings.ERR_SYNC_FAILED,
            title=_SyncStrings.TITLE,
            parent=self,
        )
        self.sync_finished()

    def health_check(self) -> bool:
        """GRD-2: Return True when the widget can serve requests normally."""
        try:
            ok = (
                self.left_model is not None
                and self.right_model is not None
                and self.sync_pushButton is not None
            )
            return ok
        except Exception as e:
            self._logger.warning("health_check failed: %s", e)
            return False

    def degraded_fallback(self) -> None:
        """GRD-3: Enter degraded mode — disable operations, show status."""
        try:
            for btn_name in (
                "sync_pushButton",
                "compare_pushButton",
                "select_left_pushButton",
                "select_right_pushButton",
            ):
                btn = getattr(self, btn_name, None)
                if btn is not None:
                    btn.setEnabled(False)
            if hasattr(self, "status_label"):
                self.status_label.setText(
                    "Sync & Backup is running in limited mode. Some features are unavailable."
                )
            self._logger.warning(
                "Synchronization & Backup entered degraded fallback mode."
            )
        except Exception as e:
            self._logger.error("degraded_fallback error: %s", e)


def main() -> None:
    """Main function to run the sync application."""
    app: QApplication = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style
    window: SyncWindow = SyncWindow()
    window.show()  # Make sure window stays alive
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
