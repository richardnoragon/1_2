"""File organization tool with rule-based file sorting.

This module provides functionality to organize files based on
customizable rules such as file type, size, date, and naming patterns.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

import logging
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt5 import uic
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.gui.themes import ThemeManager, token

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow

    class StandardWindow(QMainWindow):
        """Fallback StandardWindow when the main one isn't available."""

        def __init__(
            self,
            title="Organize Files",
            window_type="file_operations",
            **kwargs,
        ):
            super().__init__()
            self.setWindowTitle(title)
            self.window_type = window_type


# ---------------------------------------------------------------------------
# GRD-1a: Guardian registration (graceful no-op when guardian absent)
# ---------------------------------------------------------------------------
try:
    from src.core.guardian import register_gui_component
except ImportError:

    def register_gui_component(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# TEL: Telemetry helpers (graceful no-op when telemetry absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.telemetry import emit_telemetry

    def _emit_telemetry(event_type, **kw):
        emit_telemetry(event_type, **kw)  # noqa: E731

except ImportError:

    def _emit_telemetry(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# STR: Centralised string constants with fallback (P1-C15 / STR-1)
# ---------------------------------------------------------------------------
try:
    from src.rfu.ui_strings import Organizer as _OrganizerStrings
except ImportError:

    class _OrganizerStrings:  # type: ignore[no-redef]
        TITLE = "File Organizer"
        WINDOW_TITLE = "File Organizer — RFU"
        LOADING = "Loading File Organizer…"
        MODAL_ERROR_TITLE = "Error"
        ERR_INIT_FAILED = (
            "Could not start File Organizer. "
            "Please try again or restart the application."
        )
        ERR_ORGANIZE_FAILED = (
            "File organization could not be completed. "
            "Check that the source folder is accessible and try again."
        )
        ERR_SAVE_SETTINGS_FAILED = (
            "Could not save organizer settings. "
            "Check that the destination folder is writable and try again."
        )
        ERR_LOAD_SETTINGS_FAILED = (
            "Could not load organizer settings. "
            "Check that the file is a valid settings file and try again."
        )
        ERR_EXPORT_RESULTS_FAILED = (
            "Could not export results. "
            "Check that you have write permission to the chosen location."
        )
        ERR_PREVIEW_FAILED = (
            "Could not generate a preview. "
            "Make sure the source folder is accessible and try again."
        )
        ERR_READ_DIR_FAILED = (
            "Could not read the source directory. "
            "Check that the folder exists and you have the required permissions."
        )
        ERR_UNDO_FAILED = (
            "Could not undo the last organization. "
            "The files may have already been moved or deleted."
        )


# ---------------------------------------------------------------------------
# ERR: Modal helper (graceful no-op when modal absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    Modal = None  # type: ignore[assignment,misc]
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


def get_existing_directory(parent, title):
    """Directory selection dialog."""
    from PyQt5.QtWidgets import QFileDialog

    return QFileDialog.getExistingDirectory(parent, title)


@dataclass
class OrganizeRule:
    """Represents a file organization rule.

    Attributes:
        name: Name of the rule
        pattern: File pattern to match (e.g., "*.txt", "*.jpg")
        destination: Destination folder path
        enabled: Whether the rule is active
    """

    name: str
    pattern: str
    destination: str
    enabled: bool = True


# ---------------------------------------------------------------------------
# LI: LoadingIndicator import (PERF-3a/3b)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.loading_indicator import LoadingIndicator
except ImportError:  # pragma: no cover
    LoadingIndicator = None  # type: ignore[misc,assignment]


# ---------------------------------------------------------------------------
# PERF-1d: Background workers for file-system operations
# ---------------------------------------------------------------------------
class _FileListWorker(QObject):
    """Reads directory file list off the UI thread."""

    finished = pyqtSignal(list)  # list[str]
    error = pyqtSignal(str)

    def __init__(self, current_dir: str, recursive: bool):
        super().__init__()
        self._dir = current_dir
        self._recursive = recursive

    def run(self):
        from pathlib import Path

        try:
            base_path = Path(self._dir)
            files = []
            if self._recursive:
                for path in base_path.rglob("*"):
                    if path.is_file():
                        files.append(str(path))
            else:
                for path in base_path.iterdir():
                    if path.is_file():
                        files.append(str(path))
            self.finished.emit(sorted(files))
        except Exception as exc:  # ERR: non-fatal
            self.error.emit(str(exc))


class _OrganizeWorker(QObject):
    """Moves files according to rules off the UI thread."""

    finished = pyqtSignal(int, list)  # (count_moved, organized_files_list)
    error = pyqtSignal(str)

    def __init__(self, current_dir: str, rules, get_file_list_fn, move_fn):
        super().__init__()
        self._dir = current_dir
        self._rules = rules
        self._get_file_list_fn = get_file_list_fn
        self._move_fn = move_fn

    def run(self):
        try:
            organized_files: list = []
            count = 0
            files = self._get_file_list_fn()
            from pathlib import Path

            for file_path in files:
                fp = Path(file_path)
                if not fp.exists():
                    continue
                for rule in self._rules:
                    if not rule.enabled:
                        continue
                    for pattern in [p.strip() for p in rule.pattern.split(";")]:
                        if fp.match(pattern):
                            result = self._move_fn(
                                file_path, rule.destination, organized_files
                            )
                            if result:
                                count += 1
                            break
                    else:
                        continue
                    break
            self.finished.emit(count, organized_files)
        except Exception as exc:  # ERR: non-fatal
            self.error.emit(str(exc))


class _UndoWorker(QObject):
    """Reverses the last file organization off the UI thread."""

    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, organized_files: list):
        super().__init__()
        self._organized_files = list(organized_files)

    def run(self):
        import shutil
        from pathlib import Path

        try:
            count = 0
            for original_path, new_path in reversed(self._organized_files):
                if Path(new_path).exists():
                    shutil.move(new_path, original_path)
                    count += 1
            self.finished.emit(count)
        except Exception as exc:  # ERR: non-fatal
            self.error.emit(str(exc))


class OrganizeWindow(StandardWindow):
    """Main window for file organization operations.

    This window provides a graphical interface for organizing files
    based on customizable rules and patterns.

    Features:
    - Directory selection and recursive scanning
    - Rule-based file organization
    - Customizable file patterns
    - Preview before organization
    - Undo functionality

    Attributes:
        _current_dir: Path to currently selected directory
        _rules: List of organization rules
        _list_model: Model for file list view
        _organized_files: List of files that were moved
    """

    # Default paths
    _ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
    _ICON_NAME = "organize.png"
    _UI_FILE = "organize.ui"

    def __init__(self, hub_instance=None) -> None:
        """Initialize the OrganizeWindow.

        Sets up:
        - UI components and layout
        - Data models and internal state
        - Signal connections
        - Default organization rules
        """
        try:
            super().__init__(
                title=_OrganizerStrings.WINDOW_TITLE,
                window_type="file_operations",
            )
        except TypeError:
            # Fallback for QMainWindow
            super().__init__()
            self.setWindowTitle(_OrganizerStrings.WINDOW_TITLE)
        self._hub = hub_instance
        # PERF: thread tracking for background workers
        self._op_thread: QThread | None = None
        self._op_worker = None
        self._loading_indicator = None  # instantiated in _setup_ui if available
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("OrganizeWindow")
        except Exception:
            self._logger = logging.getLogger("OrganizeWindow")
        self._init_models()
        self._setup_ui()
        self._setup_icons()
        self._connect_signals()
        self._set_initial_state()
        self._load_default_rules()
        self._setup_menu_callbacks()
        register_gui_component(
            self, tool_id="organizer", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="organizer")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.centralWidget() is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("OrganizeWindow entering degraded mode")
        except Exception:
            pass
        _emit_telemetry("ui_error_event", tool_id="organizer", error_type="degraded")

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_organize", self.clear_organization)
            self.menu_manager.register_callback(
                "save_operation", self.save_organize_settings
            )
            self.menu_manager.register_callback(
                "load_operation", self.load_organize_settings
            )
            self.menu_manager.register_callback(
                "export_results", self.export_organize_results
            )

    def clear_organization(self):
        """Clear current organization state."""
        self._current_dir = ""
        self._organized_files.clear()
        self._list_model.clear()
        if hasattr(self, "directory_label"):
            self.directory_label.setText("No folder selected")
        if hasattr(self, "status_label"):
            self.status_label.setText("Select a folder to begin")
        if hasattr(self, "organizePushButton"):
            self.organizePushButton.setEnabled(False)

    def save_organize_settings(self):
        """Save current organize settings to file."""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Organize Settings",
            "organize_settings.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                import json

                settings = {
                    "directory": self._current_dir,
                    "rules": [
                        {
                            "name": rule.name,
                            "pattern": rule.pattern,
                            "destination": rule.destination,
                            "enabled": rule.enabled,
                        }
                        for rule in self._rules
                    ],
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)

                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Settings saved to {file_path}", "success"
                    )
                else:
                    QMessageBox.information(
                        self, "Success", f"Settings saved to {file_path}"
                    )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal
                self._logger.error(
                    f"Error saving organizer settings: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _OrganizerStrings.MODAL_ERROR_TITLE,
                        _OrganizerStrings.ERR_SAVE_SETTINGS_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

    def load_organize_settings(self):
        """Load organize settings from file."""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Organize Settings",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                import json

                with open(file_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                # Apply settings
                if "directory" in settings and settings["directory"]:
                    self._current_dir = settings["directory"]
                    if hasattr(self, "directory_label"):
                        self.directory_label.setText(settings["directory"])
                    self._update_file_list()

                if "rules" in settings:
                    self._rules = [
                        OrganizeRule(
                            name=rule["name"],
                            pattern=rule["pattern"],
                            destination=rule["destination"],
                            enabled=rule.get("enabled", True),
                        )
                        for rule in settings["rules"]
                    ]

                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Settings loaded from {file_path}", "success"
                    )
                else:
                    QMessageBox.information(
                        self, "Success", f"Settings loaded from {file_path}"
                    )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal
                self._logger.error(
                    f"Error loading organizer settings: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _OrganizerStrings.MODAL_ERROR_TITLE,
                        _OrganizerStrings.ERR_LOAD_SETTINGS_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

    def export_organize_results(self):
        """Export organize preview results."""
        if not self._current_dir:
            if Modal:
                Modal(
                    "No Directory",
                    "No directory selected for organizing.",
                    ["OK"],
                    parent=self,
                ).exec_()
            else:
                QMessageBox.information(
                    self, "No Directory", "No directory selected for organizing."
                )
            return

        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Organize Results",
            "organize_preview.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Organize Preview Results\n")
                    f.write(f"Directory: {self._current_dir}\n")
                    f.write(f"Total Rules: {len(self._rules)}\n\n")

                    f.write("Organization Rules:\n")
                    for rule in self._rules:
                        status = "✓" if rule.enabled else "✗"
                        rule_desc = (
                            f"{status} {rule.name}: {rule.pattern}"
                            f" → {rule.destination}"
                        )
                        f.write(f"{rule_desc}\n")

                    f.write(f"\nFiles organized: {len(self._organized_files)}\n")
                    for original, new in self._organized_files:
                        f.write(f"{original} → {new}\n")

                if ToastNotification:
                    ToastNotification(parent=self).show_message(
                        f"Results exported to {file_path}", "success"
                    )
                else:
                    QMessageBox.information(
                        self, "Success", f"Results exported to {file_path}"
                    )
            except Exception as e:  # ERR: non-fatal — surfaced via Modal
                self._logger.error(
                    f"Error exporting organizer results: {e}", exc_info=True
                )
                if Modal:
                    Modal(
                        _OrganizerStrings.MODAL_ERROR_TITLE,
                        _OrganizerStrings.ERR_EXPORT_RESULTS_FAILED,
                        ["OK"],
                        self,
                    ).exec_()

    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        self._current_dir = ""
        self._rules: List[OrganizeRule] = []
        self._list_model = QStandardItemModel()
        self._organized_files: List[Tuple[str, str]] = []

        if hasattr(self, "listListView"):
            self.listListView.setModel(self._list_model)

    def _setup_ui(self) -> None:
        """Initialize and load the UI file."""
        try:
            ui_file = Path(__file__).parent / self._UI_FILE
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")

            uic.loadUi(str(ui_file), self)

        except (
            FileNotFoundError,
            ValueError,
        ) as e:  # ERR: fatal — UI setup failed; tool cannot render
            self._logger.error(
                f"UI setup failed for OrganizeWindow: {e}", exc_info=True
            )
            raise
            sys.exit(1)

        # PERF-3a/3b: add LoadingIndicator to the central widget layout
        if LoadingIndicator:
            cw = self.centralWidget()
            if cw and cw.layout():
                self._loading_indicator = LoadingIndicator(
                    parent=self, message="Working…"
                )
                cw.layout().addWidget(self._loading_indicator)

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        if hasattr(self, "selectFolderButton"):
            self.selectFolderButton.clicked.connect(self._load_directory)
        if hasattr(self, "previewPushButton"):
            self.previewPushButton.clicked.connect(self._preview_organization)
        if hasattr(self, "organizePushButton"):
            self.organizePushButton.clicked.connect(self._organize_files)
        if hasattr(self, "rulesButton"):
            self.rulesButton.clicked.connect(self._show_rules_dialog)

        # Connect menu actions
        if hasattr(self, "actionexit"):
            self.actionexit.triggered.connect(self.close)
        if hasattr(self, "actionselect"):
            self.actionselect.triggered.connect(self._load_directory)

    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        if hasattr(self, "previewPushButton"):
            self.previewPushButton.setEnabled(False)
        if hasattr(self, "organizePushButton"):
            self.organizePushButton.setEnabled(False)
        if hasattr(self, "status_label"):
            self.status_label.setText("Select a folder to begin")

    def _setup_icons(self) -> None:
        """Load application icons."""
        icon_file = Path(self._ICON_PATH) / self._ICON_NAME
        if icon_file.exists():
            self.setWindowIcon(QIcon(str(icon_file)))

    def _load_default_rules(self) -> None:
        """Load default organization rules."""
        self._rules = [
            OrganizeRule("Documents", "*.pdf;*.doc;*.docx;*.txt", "Documents"),
            OrganizeRule("Images", "*.jpg;*.jpeg;*.png;*.gif;*.bmp", "Images"),
            OrganizeRule("Videos", "*.mp4;*.avi;*.mkv;*.mov;*.wmv", "Videos"),
            OrganizeRule("Audio", "*.mp3;*.wav;*.flac;*.aac", "Audio"),
            OrganizeRule("Archives", "*.zip;*.rar;*.7z;*.tar;*.gz", "Archives"),
        ]

    def _load_directory(self) -> None:
        """Load directory and display files in the list view."""
        directory = get_existing_directory(self, "Select Directory to Organize")
        if directory:
            self._current_dir = directory
            if hasattr(self, "directory_label"):
                self.directory_label.setText(directory)
            self._update_file_list()
            if hasattr(self, "previewPushButton"):
                self.previewPushButton.setEnabled(True)
            if hasattr(self, "organizePushButton"):
                self.organizePushButton.setEnabled(True)
            if hasattr(self, "status_label"):
                self.status_label.setText("Ready to organize files")

    def _update_file_list(self) -> None:
        """Update the list view with files (off UI thread, PERF-1d)."""
        self._list_model.clear()

        if not self._current_dir:
            return

        if self._op_thread and self._op_thread.isRunning():
            return  # previous op still running

        recursive = bool(
            hasattr(self, "recursiveCheckBox") and self.recursiveCheckBox.isChecked()
        )

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        self._op_worker = _FileListWorker(self._current_dir, recursive)
        self._op_thread = QThread()
        self._op_worker.moveToThread(self._op_thread)
        self._op_thread.started.connect(self._op_worker.run)
        self._op_worker.finished.connect(self._on_file_list_done)
        self._op_worker.error.connect(self._on_file_list_error)
        self._op_worker.finished.connect(self._stop_op_indicator)  # PERF-4a
        self._op_worker.error.connect(self._stop_op_indicator)  # PERF-4b
        self._op_thread.start()

    def _on_file_list_done(self, files: list) -> None:
        for file_path in files:
            self._add_file_to_list(file_path)

    def _on_file_list_error(self, message: str) -> None:  # ERR: non-fatal
        self._logger.error(
            f"Error reading directory '{self._current_dir}': {message}", exc_info=True
        )
        if Modal:
            Modal(
                _OrganizerStrings.MODAL_ERROR_TITLE,
                _OrganizerStrings.ERR_READ_DIR_FAILED,
                ["OK"],
                self,
            ).exec_()

    def _stop_op_indicator(self) -> None:
        """Stop the loading indicator and clean up the operation thread."""
        if self._loading_indicator:
            self._loading_indicator.stop()
        if self._op_thread:
            self._op_thread.quit()
            self._op_thread = None
        self._op_worker = None

    def _get_file_list(self) -> List[str]:
        """Get list of files from the current directory.

        Returns:
            List[str]: List of full file paths
        """
        files = []
        base_path = Path(self._current_dir)

        recursive = False
        if hasattr(self, "recursiveCheckBox"):
            recursive = self.recursiveCheckBox.isChecked()

        if recursive:
            for path in base_path.rglob("*"):
                if path.is_file():
                    files.append(str(path))
        else:
            for path in base_path.iterdir():
                if path.is_file():
                    files.append(str(path))

        return files

    def _add_file_to_list(self, file_path: str) -> None:
        """Add a file entry to the list model.

        Args:
            file_path: Full path to the file
        """
        item = QStandardItem(os.path.basename(file_path))
        item.setData(file_path)  # Store full path in item data
        self._list_model.appendRow(item)

    def _preview_organization(self) -> None:
        """Preview file organization without moving any files (dry run)."""
        if not self._current_dir:
            return

        try:
            files = self._get_file_list()
            preview_lines = []
            unmatched = []

            for file_path in sorted(files):
                file_path_obj = Path(file_path)
                matched = False
                for rule in self._rules:
                    if not rule.enabled:
                        continue
                    for pattern in [p.strip() for p in rule.pattern.split(";")]:
                        if file_path_obj.match(pattern):
                            preview_lines.append(
                                f"  {file_path_obj.name}  \u2192  {rule.destination}/"
                            )
                            matched = True
                            break
                    if matched:
                        break
                if not matched:
                    unmatched.append(file_path_obj.name)

            msg_parts = [
                f"DRY RUN \u2014 no files will be moved.\n",
                f"{len(preview_lines)} file(s) would be organized:\n",
            ]
            if preview_lines:
                display = preview_lines[:50]
                msg_parts.append("\n".join(display))
                if len(preview_lines) > 50:
                    msg_parts.append(f"\n\u2026 and {len(preview_lines) - 50} more")
            else:
                msg_parts.append("  (none)")

            if unmatched:
                msg_parts.append(
                    f"\n\n{len(unmatched)} file(s) would not be moved (no matching rule)."
                )

            QMessageBox.information(
                self,
                "Organization Preview (Dry Run)",
                "\n".join(msg_parts),
            )

            if hasattr(self, "status_label"):
                self.status_label.setText(
                    f"Preview: {len(preview_lines)} file(s) would be moved"
                )

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self._logger.error(
                f"Error generating organization preview: {e}", exc_info=True
            )
            if Modal:
                Modal(
                    _OrganizerStrings.MODAL_ERROR_TITLE,
                    _OrganizerStrings.ERR_PREVIEW_FAILED,
                    ["OK"],
                    self,
                ).exec_()

    def _organize_files(self) -> None:
        """Organize files based on the current rules (off UI thread, PERF-1d)."""
        if not self._current_dir:
            return

        if self._op_thread and self._op_thread.isRunning():
            return  # already running

        self._organized_files.clear()

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        self._op_worker = _OrganizeWorker(
            self._current_dir,
            list(self._rules),
            self._get_file_list,
            self._move_file_to_destination_threadsafe,
        )
        self._op_thread = QThread()
        self._op_worker.moveToThread(self._op_thread)
        self._op_thread.started.connect(self._op_worker.run)
        self._op_worker.finished.connect(self._on_organize_done)
        self._op_worker.error.connect(self._on_organize_error)
        self._op_worker.finished.connect(self._stop_op_indicator)  # PERF-4a
        self._op_worker.error.connect(self._stop_op_indicator)  # PERF-4b
        self._op_thread.start()

    def _move_file_to_destination_threadsafe(
        self, file_path: str, destination: str, organized_files: list
    ) -> bool:
        """Move a file to destination (called from worker thread)."""
        import shutil

        try:
            source_path = Path(file_path)
            dest_dir = Path(self._current_dir) / destination
            dest_dir.mkdir(exist_ok=True)
            dest_path = dest_dir / source_path.name
            counter = 1
            while dest_path.exists():
                dest_path = (
                    dest_dir / f"{source_path.stem}_{counter}{source_path.suffix}"
                )
                counter += 1
            shutil.move(str(source_path), str(dest_path))
            organized_files.append((str(source_path), str(dest_path)))
            return True
        except Exception as e:  # ERR: non-fatal — per-file error logged only
            self._logger.error(f"Error moving file '{file_path}': {e}", exc_info=True)
            return False

    def _on_organize_done(self, count: int, organized_files: list) -> None:
        self._organized_files.extend(organized_files)
        self._update_file_list()
        QMessageBox.information(
            self, "Organization Complete", f"Organized {count} files based on rules."
        )
        if hasattr(self, "status_label"):
            self.status_label.setText(f"Organized {count} files")

    def _on_organize_error(self, message: str) -> None:  # ERR: non-fatal
        self._logger.error(
            f"Error organizing files in '{self._current_dir}': {message}", exc_info=True
        )
        if Modal:
            Modal(
                _OrganizerStrings.MODAL_ERROR_TITLE,
                _OrganizerStrings.ERR_ORGANIZE_FAILED,
                ["OK"],
                self,
            ).exec_()

    def _organize_single_file(self, file_path: str) -> bool:
        """Organize a single file based on rules.

        Args:
            file_path: Path to the file to organize

        Returns:
            bool: True if file was moved, False otherwise
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return False

        for rule in self._rules:
            if not rule.enabled:
                continue

            patterns = [p.strip() for p in rule.pattern.split(";")]
            for pattern in patterns:
                if file_path_obj.match(pattern):
                    return self._move_file_to_destination(file_path, rule.destination)

        return False

    def _move_file_to_destination(self, file_path: str, destination: str) -> bool:
        """Move a file to its destination folder.

        Args:
            file_path: Source file path
            destination: Destination folder name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source_path = Path(file_path)
            dest_dir = Path(self._current_dir) / destination

            # Create destination directory if it doesn't exist
            dest_dir.mkdir(exist_ok=True)

            # Build destination path
            dest_path = dest_dir / source_path.name

            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            # Move the file
            shutil.move(str(source_path), str(dest_path))

            # Store for potential undo
            self._organized_files.append((str(source_path), str(dest_path)))

            return True

        except (
            Exception
        ) as e:  # ERR: non-fatal — logged only; per-file error during batch
            self._logger.error(f"Error moving file '{file_path}': {e}", exc_info=True)
            return False

    def _show_rules_dialog(self) -> None:
        """Show the rules management dialog."""
        dialog = RulesDialog(self._rules, self)
        if dialog.exec_():
            self._rules = dialog.get_rules()

    def _undo_last_organization(self) -> None:
        """Undo the last organization operation (off UI thread, PERF-1d)."""
        if self._op_thread and self._op_thread.isRunning():
            return  # operation in progress

        if not self._organized_files:
            return

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        self._op_worker = _UndoWorker(self._organized_files)
        self._op_thread = QThread()
        self._op_worker.moveToThread(self._op_thread)
        self._op_thread.started.connect(self._op_worker.run)
        self._op_worker.finished.connect(self._on_undo_done)
        self._op_worker.error.connect(self._on_undo_error)
        self._op_worker.finished.connect(self._stop_op_indicator)  # PERF-4a
        self._op_worker.error.connect(self._stop_op_indicator)  # PERF-4b
        self._op_thread.start()

    def _on_undo_done(self, count: int) -> None:
        self._organized_files.clear()
        self._update_file_list()
        QMessageBox.information(
            self, "Undo Complete", f"Restored {count} files to original locations."
        )

    def _on_undo_error(self, message: str) -> None:  # ERR: non-fatal
        self._logger.error(f"Error undoing file organization: {message}", exc_info=True)
        if Modal:
            Modal(
                _OrganizerStrings.MODAL_ERROR_TITLE,
                _OrganizerStrings.ERR_UNDO_FAILED,
                ["OK"],
                self,
            ).exec_()


class RulesDialog(QDialog):
    """Dialog for managing organization rules."""

    def __init__(self, rules: List[OrganizeRule], parent=None) -> None:
        """Initialize the rules dialog.

        Args:
            rules: Current list of organization rules
            parent: Parent widget
        """
        super().__init__(parent)
        self._rules = rules.copy()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the dialog UI."""
        _ui_bind(self, 'setWindowTitle', 'Legacy.sab7b0315f9de7bfc')
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        # Rules list
        self.rules_list = QListWidget()
        _ui_bind(self.rules_list, 'setAccessibleName', 'Legacy.s1a3b4e0512f971c2')
        self._populate_rules_list()
        layout.addWidget(_ui_widget(QLabel, 'Legacy.s1b732e8bdc4ef0f3', 'setText'))
        layout.addWidget(self.rules_list)

        # Buttons
        button_layout = QHBoxLayout()

        _SB = SecondaryButton if SecondaryButton else QPushButton

        add_button = _SB("Add Rule")
        add_button.clicked.connect(self._add_rule)
        button_layout.addWidget(add_button)

        edit_button = _SB("Edit Rule")
        edit_button.clicked.connect(self._edit_rule)
        button_layout.addWidget(edit_button)

        remove_button = _SB("Remove Rule")
        remove_button.clicked.connect(self._remove_rule)
        button_layout.addWidget(remove_button)

        layout.addLayout(button_layout)

        # OK/Cancel buttons
        _PB = PrimaryButton if PrimaryButton else QPushButton
        ok_button = _PB("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def _populate_rules_list(self) -> None:
        """Populate the rules list widget."""
        self.rules_list.clear()
        for rule in self._rules:
            status = "✓" if rule.enabled else "✗"
            item_text = f"{status} {rule.name}: {rule.pattern}" f" → {rule.destination}"
            self.rules_list.addItem(QListWidgetItem(item_text))

    def _add_rule(self) -> None:
        """Add a new organization rule."""
        dialog = RuleEditDialog(self)
        if dialog.exec_():
            new_rule = dialog.get_rule()
            self._rules.append(new_rule)
            self._populate_rules_list()

    def _edit_rule(self) -> None:
        """Edit the selected rule."""
        current_row = self.rules_list.currentRow()
        if 0 <= current_row < len(self._rules):
            dialog = RuleEditDialog(self, self._rules[current_row])
            if dialog.exec_():
                self._rules[current_row] = dialog.get_rule()
                self._populate_rules_list()

    def _remove_rule(self) -> None:
        """Remove the selected rule."""
        current_row = self.rules_list.currentRow()
        if 0 <= current_row < len(self._rules):
            del self._rules[current_row]
            self._populate_rules_list()

    def get_rules(self) -> List[OrganizeRule]:
        """Get the current list of rules.

        Returns:
            List[OrganizeRule]: Current organization rules
        """
        return self._rules


class RuleEditDialog(QDialog):
    """Dialog for editing individual organization rules."""

    def __init__(self, parent=None, rule: Optional[OrganizeRule] = None) -> None:
        """Initialize the rule edit dialog.

        Args:
            parent: Parent widget
            rule: Rule to edit (None for new rule)
        """
        super().__init__(parent)
        self._rule = rule
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the dialog UI."""
        _ui_bind(self, 'setWindowTitle', 'Legacy.s257ceefcf23f0dc0')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Rule name
        name_layout = QHBoxLayout()
        name_layout.addWidget(_ui_widget(QLabel, 'Legacy.s8fdad3bc4fb3cb50', 'setText'))
        self.name_edit = QLineEdit()
        _ui_bind(self.name_edit, 'setAccessibleName', 'Legacy.s7c9de4e8e989511f')
        if self._rule:
            self.name_edit.setText(self._rule.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # File pattern
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(_ui_widget(QLabel, 'Legacy.sea823d52add28a6e', 'setText'))
        self.pattern_edit = QLineEdit()
        _ui_bind(self.pattern_edit, 'setAccessibleName', 'Legacy.sd7e7b6eb5ff6f813')
        if self._rule:
            self.pattern_edit.setText(self._rule.pattern)
        pattern_layout.addWidget(self.pattern_edit)
        layout.addLayout(pattern_layout)

        # Destination folder
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(_ui_widget(QLabel, 'Legacy.s0c109e62332e2b1b', 'setText'))
        self.dest_edit = QLineEdit()
        _ui_bind(self.dest_edit, 'setAccessibleName', 'Legacy.se5cc0d5cbec38423')
        if self._rule:
            self.dest_edit.setText(self._rule.destination)
        dest_layout.addWidget(self.dest_edit)
        layout.addLayout(dest_layout)

        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        _PB = PrimaryButton if PrimaryButton else QPushButton
        _SB = SecondaryButton if SecondaryButton else QPushButton
        ok_button = _PB("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = _SB("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_rule(self) -> OrganizeRule:
        """Get the edited rule.

        Returns:
            OrganizeRule: The edited rule
        """
        return OrganizeRule(
            name=self.name_edit.text(),
            pattern=self.pattern_edit.text(),
            destination=self.dest_edit.text(),
        )


def main() -> None:
    """Main entry point for the organize application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    _ = OrganizeWindow()  # Keep reference to prevent garbage collection
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# Compatibility alias for legacy entry points
OrganizeGUI = OrganizeWindow
