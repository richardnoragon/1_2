from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
import logging
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5 import uic
from PyQt5.QtCore import QDateTime, QObject, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QInputDialog,
    QLabel,
    QMessageBox,
)

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
)
sys.path.append(project_root)

from src.config.config_manager import ConfigManager
from src.gui.common.base_window import BaseWindow
from src.gui.common.dialogs import (
    get_open_file_name,
    show_error_dialog,
    show_info_dialog,
)

# Import shared components
from src.log_manager import LogManager

# Note: Reliably *setting* creation time is platform-specific and often
# requires extra privileges or libraries (like pywin32 on Windows).

SELECT_PROFILE_TEXT = "Select Profile..."

try:
    from src.log_manager import get_log_manager as _get_log_manager
except ImportError:
    _get_log_manager = None

try:
    from src.rfu.ui_strings import FileTouch as _FTStrings
except ImportError:

    class _FTStrings:
        """Fallback string constants — mirrors src/rfu/ui_strings.FileTouch."""

        TITLE = "File Touch"
        WINDOW_TITLE = "File Touch — RFU"
        LOADING = "Loading File Touch…"
        MODAL_ERROR_TITLE = "File Touch"
        ERR_INIT_FAILED = (
            "Could not start File Touch. "
            "Please try again or restart the application."
        )
        ERR_FETCH_FAILED = (
            "Failed to fetch file timestamps. "
            "Check that the file exists and is accessible."
        )
        ERR_APPLY_FAILED = (
            "Failed to apply timestamp changes. "
            "Check that you have write permission to the file."
        )


try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None  # type: ignore[assignment,misc]

try:
    from src.gui.themes import ThemeManager as _ThemeManager

    _THEME_AVAILABLE = True
except ImportError:
    _ThemeManager = None  # type: ignore[assignment,misc]
    _THEME_AVAILABLE = False


class FileTouchLogic(QObject):
    """Handles the logic for getting and setting file timestamps."""

    # Signals: access, modification, creation timestamps
    timestamps_fetched = pyqtSignal(dict)  # access, mod, create timestamps
    operation_result = pyqtSignal(bool, str)  # success (bool), message (str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self) -> None:
        """Initialize file touch logic with logging integration."""
        super().__init__()
        self.logger = LogManager().get_logger("FileTouch")
        self._is_running = False
        self.logger.info("File Touch Logic initialized")

    def stop(self) -> None:
        """Stop the current operation (if possible)."""
        self._is_running = False

    def get_file_timestamps(self, filepath: str) -> None:
        """Fetches access, modification, and creation timestamps for a file."""
        self._is_running = True
        if not self._is_running:
            return

        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            if not os.path.isfile(filepath):
                raise ValueError(f"Path is not a file: {filepath}")

            stat_result = os.stat(filepath)

            # Access Time (atime)
            atime_ts = stat_result.st_atime
            atime_dt = datetime.fromtimestamp(atime_ts, tz=timezone.utc).astimezone()

            # Modification Time (mtime)
            mtime_ts = stat_result.st_mtime
            mtime_dt = datetime.fromtimestamp(mtime_ts, tz=timezone.utc).astimezone()

            # Creation Time (birthtime or ctime)
            ctime_dt: Optional[datetime] = None
            if hasattr(stat_result, "st_birthtime") and stat_result.st_birthtime:
                ctime_ts = stat_result.st_birthtime
                ctime_dt = datetime.fromtimestamp(
                    ctime_ts, tz=timezone.utc
                ).astimezone()
            elif platform.system() == "Windows":
                # On Windows, ctime is creation time
                ctime_ts = stat_result.st_ctime
                ctime_dt = datetime.fromtimestamp(
                    ctime_ts, tz=timezone.utc
                ).astimezone()

            result: Dict[str, Optional[datetime]] = {
                "access": atime_dt,
                "modification": mtime_dt,
                "creation": ctime_dt,
            }
            self.timestamps_fetched.emit(result)
            msg = "Timestamps fetched successfully."
            self.operation_result.emit(True, msg)
            self.logger.info(f"Timestamps fetched for: {filepath}")

        except (
            FileNotFoundError
        ) as e:  # ERR: non-fatal — surfaced via error_occurred signal
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
            self.logger.error(f"File not found: {e}")
        except ValueError as e:  # ERR: non-fatal — surfaced via error_occurred signal
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
            self.logger.error(f"Invalid file path: {e}")
        except PermissionError:  # ERR: non-fatal — surfaced via error_occurred signal
            err_msg = f"Permission denied: {filepath}"
            self.error_occurred.emit(err_msg)
            self.operation_result.emit(False, err_msg)
            self.logger.error(err_msg)
        except Exception as e:  # ERR: non-fatal — surfaced via error_occurred signal
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._is_running = False
            self.finished.emit()


class FileTouchWindow(BaseWindow):
    """File Touch utility window following file_utilities_1 patterns.

    This class provides a graphical interface for:
    - Viewing file timestamps (access, modification, creation)
    - Modifying file timestamps
    - Managing timestamp profiles
    - Drag-and-drop file support
    - Profile-based timestamp management

    Inherits from BaseWindow to maintain consistent GUI behavior.
    """

    def __init__(self, hub_instance=None, config_manager=None) -> None:
        """Initialize the file touch window."""
        super().__init__()
        self._hub = hub_instance
        self.config_manager = config_manager or ConfigManager()
        self.logger = LogManager().get_logger("FileTouch")
        if _get_log_manager is not None:
            try:
                self._logger = _get_log_manager().get_logger("FileTouchWindow")
            except Exception:
                self._logger = self.logger
        else:
            self._logger = self.logger
        self.logger.info("Initializing File Touch Window")
        self.setWindowTitle(_FTStrings.WINDOW_TITLE)

        self._init_models()
        self._setup_ui()
        self._setup_icons()
        self._connect_signals()
        self._set_initial_state()

        self.register_gui_component(
            tool_id="file_touch",
            recovery_callback=self.degraded_fallback,
        )
        self._emit_telemetry("ui_view_load", tool_id="file_touch")
        if _THEME_AVAILABLE and _ThemeManager is not None:
            _ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply deferred (TH-4c/4d)

    # ── GRD : ComponentGuardian integration ──────────────────────────
    def register_gui_component(self, tool_id: str, recovery_callback=None) -> None:
        """Register this widget with ComponentGuardian (no-op if unavailable)."""
        try:
            from src.core.guardian.component_guardian import ComponentGuardian

            ComponentGuardian.instance().register(
                tool_id, self, recovery_callback=recovery_callback
            )
        except Exception:
            pass

    # ── TEL : telemetry stub ──────────────────────────────────────────
    def _emit_telemetry(self, event_type: str, **kwargs) -> None:
        """Emit a telemetry event (no-op stub until TEL infrastructure lands)."""
        try:
            from src.core.telemetry import emit_telemetry

            emit_telemetry(event_type, **kwargs)
        except Exception:
            pass

    def health_check(self) -> bool:
        """Return True if the central widget is present and functional."""
        return self.centralWidget() is not None

    def degraded_fallback(self) -> None:
        """Show a minimal error state when the component fails to load."""
        try:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                _FTStrings.TITLE,
                _FTStrings.ERR_INIT_FAILED,
            )
        except Exception:
            pass

    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        # Initialize the logic component
        self.logic = FileTouchLogic()

    def _setup_ui(self) -> None:
        """Initialize and load the UI file."""
        try:
            ui_file = Path(__file__).parent / "file_touch.ui"
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            uic.loadUi(str(ui_file), self)
            self.logger.info(f"UI loaded from {ui_file}")
        except Exception as e:  # ERR: fatal — UI setup failed; tool cannot render
            self.logger.error(f"Failed to load UI file: {ui_file}", exc_info=True)
            raise

    def _setup_icons(self) -> None:
        """Setup icons and UI styling."""
        # Icons are handled by the UI file
        pass

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        # Connect menu actions
        if hasattr(self, "actionExit"):
            self.actionExit.triggered.connect(self.close)

        # Connect main buttons
        if hasattr(self, "browseButton"):
            self.browseButton.clicked.connect(self.browse_file)
        if hasattr(self, "refreshButton"):
            self.refreshButton.clicked.connect(self.refresh_timestamps)
        if hasattr(self, "applyButton"):
            self.applyButton.clicked.connect(self.apply_changes)

        # Connect file path changes
        if hasattr(self, "filePathEdit"):
            self.filePathEdit.textChanged.connect(self.on_file_path_changed)

        # Connect profile management signals (will be added in _set_initial_state)

    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        # Enable drag and drop
        self.setAcceptDrops(True)
        if hasattr(self, "filePathEdit"):
            self.filePathEdit.setAcceptDrops(True)

        # Add profile combo box to toolbar if toolbar exists
        if hasattr(self, "toolBar"):
            self.profileCombo = QComboBox(self)
            _ui_bind(self.profileCombo, 'setAccessibleName', 'Legacy.s55c708af8fd15614')
            self.profileCombo.setMinimumHeight(44)
            self.toolBar.addWidget(_ui_widget(QLabel, 'Legacy.s51aa1b8bfaff8c46', 'setText'))
            self.toolBar.addWidget(self.profileCombo)

            # Add profile management buttons
            self.saveProfileButton = self.toolBar.addAction("Save Profile")
            self.deleteProfileButton = self.toolBar.addAction("Delete Profile")

            # Connect profile signals
            self.saveProfileButton.triggered.connect(self.save_profile)
            self.deleteProfileButton.triggered.connect(self.delete_profile)
            self.profileCombo.currentTextChanged.connect(self.load_profile)

        # Initialize state
        if hasattr(self, "filePathEdit"):
            self.filePathEdit.clear()
        if hasattr(self, "applyButton"):
            self.applyButton.setEnabled(False)
        if hasattr(self, "refreshButton"):
            self.refreshButton.setEnabled(False)

        # Update profile list
        if hasattr(self, "profileCombo"):
            self.update_profile_list()

        # Show the window
        self.show()

    def update_profile_list(self) -> None:
        """Update the profile combo box with available profiles."""
        if not hasattr(self, "profileCombo"):
            return

        current: str = self.profileCombo.currentText()
        self.profileCombo.clear()
        self.profileCombo.addItem(SELECT_PROFILE_TEXT)
        profiles: list[str] = self.config_manager.get_profiles("file_touch")
        self.profileCombo.addItems(profiles)
        if current in profiles:
            self.profileCombo.setCurrentText(current)

    def save_profile(self) -> None:
        """Save current timestamp settings as a profile."""
        if not all(
            hasattr(self, attr)
            for attr in [
                "accessTimeEdit",
                "modificationTimeEdit",
                "creationTimeEdit",
            ]
        ):
            show_error_dialog(self, "Error", "Timestamp editors not available")
            return

        name: str
        ok: bool
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and name:
            settings: Dict[str, int] = {
                "access_time": (self.accessTimeEdit.dateTime().toSecsSinceEpoch()),
                "modification_time": (
                    self.modificationTimeEdit.dateTime().toSecsSinceEpoch()
                ),
                "creation_time": (self.creationTimeEdit.dateTime().toSecsSinceEpoch()),
            }
            self.config_manager.save_profile(name, "file_touch", settings)
            self.update_profile_list()
            if hasattr(self, "profileCombo"):
                self.profileCombo.setCurrentText(name)
            show_info_dialog(self, "Success", f"Profile '{name}' saved successfully!")
            self.logger.info(f"Profile '{name}' saved")

    def load_profile(self, profile_name: str) -> None:
        """Load timestamp settings from a profile."""
        if profile_name == SELECT_PROFILE_TEXT:
            return

        if not all(
            hasattr(self, attr)
            for attr in [
                "accessTimeEdit",
                "modificationTimeEdit",
                "creationTimeEdit",
            ]
        ):
            return

        settings: Optional[Dict[str, Any]] = self.config_manager.load_profile(
            profile_name, "file_touch"
        )
        if settings:
            self.accessTimeEdit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(settings["access_time"]))
            )
            self.modificationTimeEdit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(settings["modification_time"]))
            )
            self.creationTimeEdit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(settings["creation_time"]))
            )
            self.logger.info(f"Profile '{profile_name}' loaded")

    def delete_profile(self) -> None:
        """Delete the currently selected profile."""
        if not hasattr(self, "profileCombo"):
            return

        profile_name: str = self.profileCombo.currentText()
        if profile_name == SELECT_PROFILE_TEXT:
            return

        reply: int = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.config_manager.delete_profile(profile_name, "file_touch"):
                show_info_dialog(
                    self,
                    "Success",
                    f"Profile '{profile_name}' deleted successfully!",
                )
                self.update_profile_list()
                self.logger.info(f"Profile '{profile_name}' deleted")
            else:
                show_error_dialog(
                    self, "Error", f"Failed to delete profile '{profile_name}'"
                )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events for file dropping.

        Args:
            event: The drag enter event to handle
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle file drop events.

        Args:
            event: The drop event to handle
        """
        urls = event.mimeData().urls()
        if urls:
            # Use the first dropped item's path
            path: str = urls[0].toLocalFile()
            if os.path.isfile(path):
                if hasattr(self, "filePathEdit"):
                    self.filePathEdit.setText(path)
                    self.refresh_timestamps()
                self.logger.info(f"File dropped: {path}")
            else:
                show_error_dialog(self, "Error", "Please drop a file, not a folder")

    def browse_file(self) -> None:
        """Open file dialog to select a file"""
        file_path = get_open_file_name(self, "Select File", "", "All Files (*.*)")
        if file_path and hasattr(self, "filePathEdit"):
            self.filePathEdit.setText(file_path)
            self.logger.info(f"File selected: {file_path}")

    def on_file_path_changed(self) -> None:
        """Handle file path text changes"""
        if not hasattr(self, "filePathEdit"):
            return

        file_path: str = self.filePathEdit.text()
        has_file: bool = bool(file_path and os.path.isfile(file_path))

        if hasattr(self, "refreshButton"):
            self.refreshButton.setEnabled(has_file)
        if has_file:
            self.refresh_timestamps()
        else:
            if hasattr(self, "applyButton"):
                self.applyButton.setEnabled(False)

    def refresh_timestamps(self) -> None:
        """Update the GUI with current file timestamps"""
        if not hasattr(self, "filePathEdit"):
            return

        try:
            file_path: str = self.filePathEdit.text()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            stat = os.stat(file_path)

            # Access Time
            if hasattr(self, "accessTimeEdit"):
                self.accessTimeEdit.setDateTime(
                    QDateTime.fromSecsSinceEpoch(int(stat.st_atime))
                )

            # Modification Time
            if hasattr(self, "modificationTimeEdit"):
                mod_time = QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
                self.modificationTimeEdit.setDateTime(mod_time)

            # Creation Time (platform-specific)
            if hasattr(self, "creationTimeEdit"):
                ctime: float
                if hasattr(stat, "st_birthtime"):  # macOS, BSD
                    ctime = stat.st_birthtime
                else:  # Windows: creation, Linux: metadata changes
                    ctime = stat.st_ctime

                self.creationTimeEdit.setDateTime(
                    QDateTime.fromSecsSinceEpoch(int(ctime))
                )

            if hasattr(self, "applyButton"):
                self.applyButton.setEnabled(True)

            if hasattr(self, "statusBar"):
                self.statusBar().showMessage("Timestamps loaded successfully")

            self.logger.info(f"Timestamps refreshed for: {file_path}")

        except Exception as e:  # ERR: non-fatal — surfaced via Modal and status bar
            self.logger.error(f"Error refreshing timestamps: {e}", exc_info=True)
            if Modal:
                Modal(
                    _FTStrings.MODAL_ERROR_TITLE,
                    _FTStrings.ERR_FETCH_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            if hasattr(self, "statusBar"):
                self.statusBar().showMessage(_FTStrings.ERR_FETCH_FAILED)
            if hasattr(self, "applyButton"):
                self.applyButton.setEnabled(False)

    def apply_changes(self) -> None:
        """Apply the timestamp changes to the file"""
        if not hasattr(self, "filePathEdit"):
            return

        try:
            file_path: str = self.filePathEdit.text()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Get timestamps from GUI
            if not all(
                hasattr(self, attr)
                for attr in ["accessTimeEdit", "modificationTimeEdit"]
            ):
                raise ValueError("Timestamp editors not available")

            atime: int = self.accessTimeEdit.dateTime().toSecsSinceEpoch()
            mtime: int = self.modificationTimeEdit.dateTime().toSecsSinceEpoch()

            # Update access and modification times
            os.utime(file_path, (atime, mtime))

            # Note: Creation time modification requires platform-specific code
            # Windows: pywin32, Linux: unsupported, macOS: read-only

            if hasattr(self, "statusBar"):
                self.statusBar().showMessage("Timestamps updated successfully")
            self.refresh_timestamps()  # Refresh to show actual changes
            self.logger.info(f"Timestamps updated for: {file_path}")

        except Exception as e:  # ERR: non-fatal — surfaced via Modal and status bar
            self.logger.error(f"Error applying changes: {e}", exc_info=True)
            if Modal:
                Modal(
                    _FTStrings.MODAL_ERROR_TITLE,
                    _FTStrings.ERR_APPLY_FAILED,
                    ["OK"],
                    self,
                ).exec_()
            if hasattr(self, "statusBar"):
                self.statusBar().showMessage(_FTStrings.ERR_APPLY_FAILED)

    def save_settings(self) -> None:
        """Save current settings for future sessions."""
        # Implementation for saving settings
        pass

    def show(self) -> None:
        """Show the file touch window."""
        super().show()

    def close(self) -> None:
        """Close the file touch window."""
        super().close()


# Compatibility class for testing
class FileTouchGUI(FileTouchWindow):
    """Compatibility class that maintains the original class name for backward compatibility."""

    def __init__(self, hub_instance=None) -> None:
        """Initialize with default config manager."""
        super().__init__(hub_instance=hub_instance)


def main() -> None:
    """Main entry point for the application."""
    try:
        print("Starting File Touch...")
        app: QApplication = QApplication(sys.argv)
        print("QApplication created...")
        window = FileTouchWindow()
        print("GUI instance created...")
        window.show()
        print("GUI shown...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
