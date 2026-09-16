#!/usr/bin/env python3
"""
Empty Folders Finder for Richard's File Utilities

A streamlined empty folders finder utility with essential functionality.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from src.gui.themes import ThemeManager, token

try:
    from src.gui.components.buttons import (
        DestructiveButton,
        PrimaryButton,
        SecondaryButton,
    )
    from src.gui.components.loading_indicator import LoadingIndicator
    from src.gui.components.modal import ConfirmationModal, Modal

    _COMPONENTS_AVAILABLE = True
except ImportError:
    PrimaryButton = SecondaryButton = DestructiveButton = None
    Modal = ConfirmationModal = LoadingIndicator = None
    _COMPONENTS_AVAILABLE = False

from PyQt5.QtWidgets import QPushButton as _QPushButton

try:
    from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import SafeStandardWindow for reliable menu integration
try:
    # Add the correct path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from src.gui.safe_standard_window import (
        SafeStandardWindow as StandardWindow,
    )

    STANDARD_WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"SafeStandardWindow not available: {e}")
    # Try original StandardWindow as fallback
    try:
        from src.gui.standard_window import StandardWindow

        STANDARD_WINDOW_AVAILABLE = True
    except ImportError:
        # Final fallback - minimal implementation
        class StandardWindow(QMainWindow):
            def __init__(self, title="Window", window_type="utility", parent=None):
                super().__init__(parent)
                self.setWindowTitle(title)

            def ensure_menu_bar(self):
                pass  # No-op for fallback

        STANDARD_WINDOW_AVAILABLE = False


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
    from src.rfu.ui_strings import EmptyFolders as _EmptyFoldersStrings
except ImportError:

    class _EmptyFoldersStrings:  # type: ignore[no-redef]
        TITLE = "Empty Folders Finder"
        WINDOW_TITLE = "Empty Folders Finder — RFU"
        LOADING = "Loading Empty Folders Finder…"
        ERR_INIT_FAILED = (
            "Could not start Empty Folders Finder. "
            "Please try again or restart the application."
        )
        ERR_SCAN_FAILED = "Could not scan the selected directory. Please try again."
        ERR_DELETE_FAILED = (
            "Could not delete the selected folder. Please check permissions."
        )


class EmptyFolderLogic(QObject):
    """Handles the logic for finding and deleting empty folders."""

    progress_updated = pyqtSignal(str)
    folders_found = pyqtSignal(list)
    deletion_update = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._is_running = False
        self._base_path = None

    def stop(self) -> None:
        """Stop the operation."""
        self._is_running = False
        self.progress_updated.emit("Stopping operation...")

    @pyqtSlot()
    def run_scan(self):
        self.find_empty_folders(self.pending_path)

    @pyqtSlot()
    def run_delete(self):
        self.delete_folders(self.pending_folders)

    def find_empty_folders(self, start_path: str) -> None:
        """Find empty folders recursively."""
        self._is_running = True
        self._base_path = start_path
        empty_folders = []

        try:
            self.progress_updated.emit(f"Scanning directory: {start_path}...")

            # Walk through all directories
            for root, dirs, files in os.walk(start_path):
                if not self._is_running:
                    break

                # Check if directory is empty
                try:
                    dir_contents = os.listdir(root)
                    if not dir_contents:  # Empty directory
                        empty_folders.append(root)
                        folder_name = os.path.basename(root)
                        self.progress_updated.emit(f"Found: {folder_name}")
                except (
                    OSError
                ):  # ERR: non-fatal — inaccessible directory skipped during scan
                    continue

            if self._is_running:
                self.folders_found.emit(empty_folders)
                self.progress_updated.emit(
                    f"Scan complete. Found {len(empty_folders)} empty folders."
                )

        except (
            Exception
        ) as e:  # ERR: non-fatal — surfaced via error_occurred signal to GUI
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit(True)

    def delete_folders(self, folders: List[str]) -> None:
        """Delete the specified empty folders."""
        self._is_running = True
        deleted_count = 0
        failed_count = 0

        # Sort by path length in reverse order to delete nested folders first
        folders_to_delete = sorted(folders, key=len, reverse=True)

        self.progress_updated.emit(
            f"Starting deletion of {len(folders_to_delete)} folders..."
        )

        for folder in folders_to_delete:
            if not self._is_running:
                break

            try:
                if os.path.exists(folder) and os.path.isdir(folder):
                    os.rmdir(folder)
                    self.deletion_update.emit(folder, True)
                    deleted_count += 1
                    folder_name = os.path.basename(folder)
                    self.progress_updated.emit(f"Deleted: {folder_name}")
                else:
                    self.deletion_update.emit(folder, False)
                    failed_count += 1
            except (
                Exception
            ) as e:  # ERR: non-fatal — surfaced via deletion_update signal; per-folder error
                self.deletion_update.emit(folder, False)
                failed_count += 1
                msg = f"Failed to delete {folder}: {str(e)}"
                self.error_occurred.emit(msg)

        if self._is_running:
            self.progress_updated.emit(
                f"Deletion complete. Deleted: {deleted_count}, Failed: {failed_count}"
            )

        self.finished.emit(False)


class EmptyFoldersGUI(StandardWindow):
    """Main window for Empty Folders operations."""

    def __init__(self, hub_instance=None, parent=None):
        # Always use the safe constructor parameters
        super().__init__(
            title=_EmptyFoldersStrings.WINDOW_TITLE,
            window_type="utility",
            parent=parent,
        )
        self._hub = hub_instance
        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("EmptyFoldersGUI")
        except Exception:
            self._logger = logging.getLogger("EmptyFoldersGUI")
        self.setGeometry(100, 100, 800, 600)

        self.current_path: Optional[str] = None
        self.empty_folders: List[str] = []
        self.logic: Optional[EmptyFolderLogic] = None
        self.thread: Optional[QThread] = None

        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        # Ensure menu bar exists (safe to call in both modes)
        self.ensure_menu_bar()
        register_gui_component(
            self, tool_id="empty_folders", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="empty_folders")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "results_list") and self.results_list is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("EmptyFoldersGUI entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="empty_folders", error_type="degraded"
        )

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_scan", self.clear_results)
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback("show_user_guide", self.show_help)
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_results(self):
        """Clear all scan results."""
        self.empty_folders = []
        if hasattr(self, "results_list"):
            self.results_list.clear()

    def show_help(self):
        """Show help dialog for Empty Folders tool."""
        help_text = """
        <h2>Empty Folders Finder - Help</h2>

        <h3>How to Find Empty Folders:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to scan</li>
        <li><b>Start Scan:</b> Begin searching for empty directories</li>
        <li><b>Review Results:</b> Browse the list of found empty folders</li>
        <li><b>Delete Selected:</b> Remove unwanted empty directories</li>
        </ul>

        <h3>Scan Features:</h3>
        <ul>
        <li><b>Recursive Search:</b> Scans all subdirectories thoroughly</li>
        <li><b>Safe Detection:</b> Only identifies truly empty folders</li>
        <li><b>Progress Tracking:</b> Real-time scan progress updates</li>
        <li><b>Error Handling:</b> Handles permission and access issues</li>
        </ul>

        <h3>Deletion Safety:</h3>
        <ul>
        <li><b>Selective Deletion:</b> Choose which folders to remove</li>
        <li><b>Nested Order:</b> Deletes nested folders before parents</li>
        <li><b>Confirmation:</b> Asks before permanent deletion</li>
        <li><b>Status Updates:</b> Shows success/failure for each folder</li>
        </ul>

        <h3>Use Cases:</h3>
        <ul>
        <li><b>Cleanup:</b> Remove leftover empty directories</li>
        <li><b>Organization:</b> Clean up project folder structures</li>
        <li><b>Maintenance:</b> Regular system housekeeping</li>
        <li><b>Archive Prep:</b> Clean folders before archiving</li>
        </ul>

        <h3>Best Practices:</h3>
        <ul>
        <li><b>Test First:</b> Scan before deleting to review results</li>
        <li><b>Backup Important:</b> Backup critical directory structures</li>
        <li><b>Avoid System:</b> Don't scan critical system directories</li>
        <li><b>Regular Use:</b> Run periodically for maintenance</li>
        </ul>

        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new scan</li>
        </ul>
        """

        if Modal:
            Modal("Empty Folders Finder Help", help_text, ["OK"], parent=self).exec_()
        else:
            QMessageBox.information(self, "Empty Folders Finder Help", help_text)

    def show_preferences(self):
        """Show Empty Folders preferences."""
        _msg = (
            "Empty Folders Finder preferences:\n\n"
            "• Scan depth limits\n"
            "• Directory exclusion filters\n"
            "• Deletion confirmation options\n"
            "• Progress display settings\n\n"
            "Advanced preferences coming soon!"
        )
        if Modal:
            Modal("Empty Folders Finder Preferences", _msg, ["OK"], parent=self).exec_()
        else:
            QMessageBox.information(self, "Empty Folders Finder Preferences", _msg)

    def refresh_view(self):
        """Refresh/clear the current scan results."""
        self.clear_results()

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Add header
        header_label = _ui_widget(QLabel, 'Legacy.s27be31b1452098f2', 'setText')
        header_label.setStyleSheet(
            f"""
            QLabel {{

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # Directory selection area
        selection_group = _ui_widget(QGroupBox, 'Legacy.s30d2d5574cce5ea3', 'setTitle')
        selection_layout = QVBoxLayout(selection_group)

        # Path selection
        path_layout = QHBoxLayout()
        self.path_input = _ui_widget(QLabel, 'Legacy.sbf355de778591b63', 'setText')
        self.path_input.setStyleSheet(
            f"""
            QLabel {{
                padding: 8px;
                border: 2px solid {token('text_disabled')};
                border-radius: 4px;
                background-color: {token('dialog_background')};
                color: {token('text_primary')};
            }}
        """
        )
        _Btn = SecondaryButton if _COMPONENTS_AVAILABLE else _QPushButton
        self.browse_button = _Btn("Browse...")
        self.browse_button.clicked.connect(self.select_directory)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        selection_layout.addLayout(path_layout)

        # Control buttons
        control_layout = QHBoxLayout()
        self.scan_button = (PrimaryButton if _COMPONENTS_AVAILABLE else _QPushButton)(
            "Scan for Empty Folders"
        )
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setEnabled(False)
        self.stop_button = (SecondaryButton if _COMPONENTS_AVAILABLE else _QPushButton)(
            "Stop"
        )
        self.stop_button.clicked.connect(self.stop_operation)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.scan_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        selection_layout.addLayout(control_layout)

        layout.addWidget(selection_group)

        # Results area
        results_group = _ui_widget(QGroupBox, 'Legacy.sd7053555fe638c79', 'setTitle')
        results_layout = QVBoxLayout(results_group)

        self.results_list = QListWidget()
        _ui_bind(self.results_list, 'setAccessibleName', 'Legacy.sc9fdae2b72d21e5a')
        self.results_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        results_layout.addWidget(self.results_list)

        # List control buttons
        list_control_layout = QHBoxLayout()
        self.select_all_button = (
            SecondaryButton if _COMPONENTS_AVAILABLE else _QPushButton
        )("Select All")
        self.select_all_button.clicked.connect(self.select_all_folders)
        self.select_all_button.setEnabled(False)
        self.unselect_all_button = (
            SecondaryButton if _COMPONENTS_AVAILABLE else _QPushButton
        )("Unselect All")
        self.unselect_all_button.clicked.connect(self.unselect_all_folders)
        self.unselect_all_button.setEnabled(False)
        if _COMPONENTS_AVAILABLE:
            self.delete_button = _ui_widget(SecondaryButton, 'Legacy.s6662750e03313bdd', 'setText')
            self.delete_button.setStyleSheet(f"color: {token('semantic_error')};")
            self.delete_button.clicked.connect(self.delete_selected)
        else:
            self.delete_button = _QPushButton("Delete Selected")
            self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)

        list_control_layout.addWidget(self.select_all_button)
        list_control_layout.addWidget(self.unselect_all_button)
        list_control_layout.addStretch()
        list_control_layout.addWidget(self.delete_button)
        results_layout.addLayout(list_control_layout)

        layout.addWidget(results_group)

        # Status area
        self.status_label = _ui_widget(QLabel, 'Legacy.s0506135a8bea582e', 'setText')
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                padding: 8px;
                background-color: {token('color_bg_subtle')};
                border: 1px solid {token('border')};
                border-radius: 4px;
                color: {token('text_primary')};
            }}
        """
        )
        layout.addWidget(self.status_label)

        # Loading indicator (PERF-3a/3b)
        if LoadingIndicator:
            self._loading_indicator = LoadingIndicator(parent=self, message="Working…")
            layout.addWidget(self._loading_indicator)
        else:
            self._loading_indicator = None

    def select_directory(self):
        """Select directory to scan."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            self.current_path = directory
            self.path_input.setText(directory)
            self.status_label.setText(f"Selected: {os.path.basename(directory)}")

            # Clear previous results
            self.results_list.clear()
            self.empty_folders = []
            self.scan_button.setEnabled(True)
            self.update_button_states()

    def start_scan(self):
        """Start scanning for empty folders."""
        if not self.current_path:
            if Modal:
                Modal(
                    "Error", "Please select a directory first", ["OK"], parent=self
                ).exec_()
            else:
                QMessageBox.warning(self, "Error", "Please select a directory first")
            return

        # Clear previous results
        self.results_list.clear()
        self.empty_folders = []

        self.status_label.setText("Scanning for empty folders...")

        # Update button states
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.delete_button.setEnabled(False)

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        # Create and start scan thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)

        # Connect signals
        self.logic.progress_updated.connect(self.update_status)
        self.logic.folders_found.connect(self.display_folders)
        self.logic.error_occurred.connect(self.handle_error)
        self.logic.finished.connect(self.scan_complete)
        self.logic.pending_path = self.current_path
        self.thread.started.connect(self.logic.run_scan)

        self.thread.start()

    def stop_operation(self):
        """Stop the current operation."""
        if self.logic:
            self.logic.stop()
        self.stop_button.setEnabled(False)
        self.status_label.setText("Stopping operation...")

    def update_status(self, message: str):
        """Update status message."""
        self.status_label.setText(message)

    def display_folders(self, folders: List[str]):
        """Display found empty folders."""
        self.empty_folders = folders

        self.results_list.clear()

        for folder in folders:
            # Show relative path if possible
            if self.current_path:
                try:
                    display_path = os.path.relpath(folder, self.current_path)
                    if display_path == ".":
                        display_path = os.path.basename(folder)
                except (
                    ValueError
                ):  # ERR: non-fatal — path display fallback; full path used instead
                    display_path = folder
            else:
                display_path = folder

            item = QListWidgetItem(display_path)
            item.setData(Qt.UserRole, folder)  # Store full path
            self.results_list.addItem(item)

        self.status_label.setText(f"Found {len(folders)} empty folders")
        self.update_button_states()

    def select_all_folders(self):
        """Select all folders in the list."""
        self.results_list.selectAll()

    def unselect_all_folders(self):
        """Unselect all folders in the list."""
        self.results_list.clearSelection()

    def delete_selected(self):
        """Delete selected empty folders."""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            if Modal:
                Modal(
                    "Error", "Please select folders to delete", ["OK"], parent=self
                ).exec_()
            else:
                QMessageBox.warning(self, "Error", "Please select folders to delete")
            return

        folders_to_delete: List[str] = [
            item.data(Qt.UserRole) for item in selected_items
        ]

        # Confirm deletion
        if ConfirmationModal:
            dlg = ConfirmationModal(
                "Confirm Deletion",
                f"Delete {len(folders_to_delete)} empty folder"
                f"{'s' if len(folders_to_delete) != 1 else ''}?\n\n"
                "This action cannot be undone.",
                confirm_text="Delete",
                cancel_text="Cancel",
                parent=self,
            )
            if not dlg.exec_():  # 0 = cancelled
                return
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Delete {len(folders_to_delete)} empty folders?\n\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self.status_label.setText("Deleting folders...")

        # Update button states
        self.delete_button.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # PERF-3a: start indicator before worker
        if self._loading_indicator:
            self._loading_indicator.start()

        # Create and start delete thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)

        # Connect signals
        self.logic.progress_updated.connect(self.update_status)
        self.logic.deletion_update.connect(self.handle_deletion)
        self.logic.error_occurred.connect(self.handle_error)
        self.logic.finished.connect(self.delete_complete)
        self.logic.pending_folders = list(folders_to_delete)
        self.thread.started.connect(self.logic.run_delete)

        self.thread.start()

    def handle_deletion(self, folder_path: str, success: bool):
        """Handle deletion results."""
        # Find and update the item in the list
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item and item.data(Qt.UserRole) == folder_path:
                if success:
                    item.setForeground(QColor("gray"))
                    item.setText(f"[DELETED] {item.text()}")
                    item.setSelected(False)
                else:
                    item.setForeground(QColor("red"))
                    item.setText(f"[FAILED] {item.text()}")
                break

    def scan_complete(self):
        """Handle scan completion."""
        self.operation_complete()

    def delete_complete(self):
        """Handle delete completion."""
        self.operation_complete()

    def operation_complete(self):
        """Handle operation completion - common cleanup."""
        # PERF-4a: stop indicator on normal completion
        if self._loading_indicator:
            self._loading_indicator.stop()

        # Re-enable buttons
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.update_button_states()

        # Clean up thread
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
        self.logic = None

    def update_button_states(self):
        """Update button enabled states based on current state."""
        has_folders = self.results_list.count() > 0

        self.delete_button.setEnabled(has_folders)
        self.select_all_button.setEnabled(has_folders)
        self.unselect_all_button.setEnabled(has_folders)

    def handle_error(self, error_message: str):
        """Handle errors."""
        # PERF-4b: stop indicator on error path
        if self._loading_indicator:
            self._loading_indicator.stop()
        if Modal:
            Modal("Error", error_message, ["OK"], parent=self).exec_()
        else:
            QMessageBox.critical(self, "Error", error_message)
        self.operation_complete()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = EmptyFoldersGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
