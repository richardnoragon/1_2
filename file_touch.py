# Filename: file_touch_logic.py

import sys
import os
import platform
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QLabel, QInputDialog, QMessageBox
)
from PyQt5 import uic
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog, show_info_dialog, get_open_file_name
)
from config_manager import ConfigManager


# Note: Reliably *setting* creation time is platform-specific and often
# requires extra privileges or libraries (like pywin32 on Windows).

SELECT_PROFILE_TEXT = "Select Profile..."


class FileTouchLogic(QObject):
    """Handles the logic for getting and setting file timestamps."""
    # Signals: access, modification, creation timestamps
    timestamps_fetched = pyqtSignal(dict)  # access, mod, create timestamps
    operation_result = pyqtSignal(bool, str)  # success (bool), message (str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self) -> None:
        """init."""
        super().__init__()
        self._is_running = False

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
            atime_dt = datetime.fromtimestamp(
                atime_ts, tz=timezone.utc
            ).astimezone()

            # Modification Time (mtime)
            mtime_ts = stat_result.st_mtime
            mtime_dt = datetime.fromtimestamp(
                mtime_ts, tz=timezone.utc
            ).astimezone()

            # Creation Time (birthtime or ctime)
            ctime_dt: Optional[datetime] = None
            if (hasattr(stat_result, 'st_birthtime') and
                    stat_result.st_birthtime):
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
                'access': atime_dt,
                'modification': mtime_dt,
                'creation': ctime_dt
            }
            self.timestamps_fetched.emit(result)
            msg = "Timestamps fetched successfully."
            self.operation_result.emit(True, msg)

        except FileNotFoundError as e:
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
        except ValueError as e:
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
        except PermissionError:
            err_msg = f"Permission denied: {filepath}"
            self.error_occurred.emit(err_msg)
            self.operation_result.emit(False, err_msg)
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.operation_result.emit(False, str(e))
        finally:
            self._is_running = False
            self.finished.emit()


class FileTouchGUI(BaseWindow):
    """A class that handles file touch g u i and inherits from BaseWindow."""
    def __init__(self) -> None:
        """init."""
        super().__init__()
        # Load the UI
        ui_file = os.path.join(os.path.dirname(__file__), "file_touch.ui")
        uic.loadUi(ui_file, self)
        
        # Initialize ConfigManager
        self.config_manager: ConfigManager = ConfigManager()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.filePathEdit.setAcceptDrops(True)
        
        # Add profile combo box to toolbar
        self.profileCombo: QComboBox = QComboBox(self)
        self.toolBar.addWidget(QLabel("Profile: "))
        self.toolBar.addWidget(self.profileCombo)
        
        # Add profile management buttons
        self.saveProfileButton = self.toolBar.addAction("Save Profile")
        self.deleteProfileButton = self.toolBar.addAction("Delete Profile")
        
        # Connect signals
        self.browseButton.clicked.connect(self.browse_file)
        self.refreshButton.clicked.connect(self.refresh_timestamps)
        self.applyButton.clicked.connect(self.apply_changes)
        self.actionExit.triggered.connect(self.close)
        self.filePathEdit.textChanged.connect(self.on_file_path_changed)
        self.saveProfileButton.triggered.connect(self.save_profile)
        self.deleteProfileButton.triggered.connect(self.delete_profile)
        self.profileCombo.currentTextChanged.connect(self.load_profile)
        
        # Initialize state
        self.filePathEdit.clear()
        self.applyButton.setEnabled(False)
        self.refreshButton.setEnabled(False)
        self.update_profile_list()
        self.show()
        
    def update_profile_list(self) -> None:
        """Update the profile combo box with available profiles."""
        current: str = self.profileCombo.currentText()
        self.profileCombo.clear()
        self.profileCombo.addItem(SELECT_PROFILE_TEXT)
        profiles: list[str] = self.config_manager.get_profiles("file_touch")
        self.profileCombo.addItems(profiles)
        if current in profiles:
            self.profileCombo.setCurrentText(current)
            
    def save_profile(self) -> None:
        """Save current timestamp settings as a profile."""
        name: str
        ok: bool
        name, ok = QInputDialog.getText(
            self,
            "Save Profile",
            "Enter profile name:"
        )
        if ok and name:
            settings: Dict[str, int] = {
                'access_time': (
                    self.accessTimeEdit.dateTime().toSecsSinceEpoch()
                ),
                'modification_time': (
                    self.modificationTimeEdit.dateTime().toSecsSinceEpoch()
                ),
                'creation_time': (
                    self.creationTimeEdit.dateTime().toSecsSinceEpoch()
                )
            }
            self.config_manager.save_profile(name, "file_touch", settings)
            self.update_profile_list()
            self.profileCombo.setCurrentText(name)
            show_info_dialog(
                self, "Success",
                f"Profile '{name}' saved successfully!"
            )
            
    def load_profile(self, profile_name: str) -> None:
        """Load timestamp settings from a profile."""
        if profile_name == SELECT_PROFILE_TEXT:
            return
            
        settings: Optional[Dict[str, Any]] = (
            self.config_manager.load_profile(profile_name, "file_touch")
        )
        if settings:
            self.accessTimeEdit.setDateTime(QDateTime.fromSecsSinceEpoch(
                int(settings['access_time'])
            ))
            self.modificationTimeEdit.setDateTime(QDateTime.fromSecsSinceEpoch(
                int(settings['modification_time'])
            ))
            self.creationTimeEdit.setDateTime(QDateTime.fromSecsSinceEpoch(
                int(settings['creation_time'])
            ))
            
    def delete_profile(self) -> None:
        """Delete the currently selected profile."""
        profile_name: str = self.profileCombo.currentText()
        if profile_name == SELECT_PROFILE_TEXT:
            return
        
        reply: int = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
            
        if reply == QMessageBox.Yes:
            if self.config_manager.delete_profile(profile_name, "file_touch"):
                show_info_dialog(
                    self, "Success",
                    f"Profile '{profile_name}' deleted successfully!"
                )
                self.update_profile_list()
            else:
                show_error_dialog(
                    self, "Error",
                    f"Failed to delete profile '{profile_name}'"
                )

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        """dragenterevent.
        Args:
            a0 (QDragEnterEvent): Description of event"""
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()
            
    def dropEvent(self, a0: QDropEvent) -> None:
        """dropevent.
        Args:
            a0 (QDropEvent): Description of event"""
        urls = a0.mimeData().urls()
        if urls:
            # Use the first dropped item's path
            path: str = urls[0].toLocalFile()
            if os.path.isfile(path):
                self.filePathEdit.setText(path)
                self.refresh_timestamps()
            else:
                show_error_dialog(
                    self, "Error",
                    "Please drop a file, not a folder"
                )

    def browse_file(self) -> None:
        """Open file dialog to select a file"""
        file_path = get_open_file_name(
            self,
            "Select File",
            "",
            "All Files (*.*)"
        )
        if file_path:
            self.filePathEdit.setText(file_path)

    def on_file_path_changed(self) -> None:
        """Handle file path text changes"""
        file_path: str = self.filePathEdit.text()
        has_file: bool = bool(file_path and os.path.isfile(file_path))
        self.refreshButton.setEnabled(has_file)
        if has_file:
            self.refresh_timestamps()
        else:
            self.applyButton.setEnabled(False)

    def refresh_timestamps(self) -> None:
        """Update the GUI with current file timestamps"""
        try:
            file_path: str = self.filePathEdit.text()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            stat = os.stat(file_path)

            # Access Time
            self.accessTimeEdit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(stat.st_atime))
            )

            # Modification Time
            mod_time = QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
            self.modificationTimeEdit.setDateTime(mod_time)

            # Creation Time (platform-specific)
            ctime: float
            if hasattr(stat, 'st_birthtime'):  # macOS, BSD
                ctime = stat.st_birthtime
            else:  # Windows: creation, Linux: metadata changes
                ctime = stat.st_ctime
            
            self.creationTimeEdit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(ctime))
            )

            self.applyButton.setEnabled(True)
            self.statusBar().showMessage("Timestamps loaded successfully")

        except Exception as e:
            show_error_dialog(self, "Error", str(e))
            self.statusBar().showMessage("Error loading timestamps")
            self.applyButton.setEnabled(False)

    def apply_changes(self) -> None:
        """Apply the timestamp changes to the file"""
        try:
            file_path: str = self.filePathEdit.text()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Get timestamps from GUI
            atime: int = self.accessTimeEdit.dateTime().toSecsSinceEpoch()
            mtime: int = self.modificationTimeEdit.dateTime().toSecsSinceEpoch()

            # Update access and modification times
            os.utime(file_path, (atime, mtime))

            # Note: Creation time modification requires platform-specific code
            # Windows: pywin32, Linux: unsupported, macOS: read-only

            self.statusBar().showMessage("Timestamps updated successfully")
            self.refresh_timestamps()  # Refresh to show actual changes

        except Exception as e:
            show_error_dialog(self, "Error", str(e))
            self.statusBar().showMessage("Error updating timestamps")


def main() -> None:
    """Main entry point for the application."""
    app: QApplication = QApplication(sys.argv)
    _ = FileTouchGUI()  # Store the window instance
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()