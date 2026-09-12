"""
Privacy Tools Hub GUI

Main interface for accessing all privacy cleaning tools.
Provides a unified interface with tabs for each tool category.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import the main project's GUI components
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.inputs import TextInput
    from src.gui.standard_window import StandardWindow

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    class TextInput(QWidget):
        def __init__(self, label: str = "", placeholder: str = ""):
            super().__init__()
            layout = QVBoxLayout(self)
            self._label = QLabel(label)
            self._edit = QLineEdit()
            self._edit.setPlaceholderText(placeholder or label)
            layout.addWidget(self._label)
            layout.addWidget(self._edit)

        def text(self):
            return self._edit.text()

        def setText(self, value):
            self._edit.setText(value)

        def setEchoMode(self, mode):
            self._edit.setEchoMode(mode)

        def setReadOnly(self, value):
            self._edit.setReadOnly(value)

        def setAccessibleName(self, value):
            super().setAccessibleName(value)
            self._edit.setAccessibleName(value)

        def setAccessibleDescription(self, value):
            super().setAccessibleDescription(value)
            self._edit.setAccessibleDescription(value)

    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False

try:
    from src.gui.themes import Colors, Fonts, ThemeManager
except ImportError:
    ThemeManager = None
    Colors = None
    Fonts = None


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
    from src.rfu.ui_strings import Privacy as _PrivStrings
except ImportError:

    class _PrivStrings:  # type: ignore[no-redef]
        TITLE = "Privacy Tools"
        WINDOW_TITLE = "Privacy Tools — RFU"
        LOADING = "Loading Privacy Tools…"
        MODAL_ERROR_TITLE = "Privacy Tools"
        ERR_INIT_FAILED = (
            "Could not start Privacy Tools. "
            "Please try again or restart the application."
        )
        ERR_CLEAN_FAILED = (
            "Privacy clean operation failed. "
            "Check that you have the required permissions."
        )
        ERR_PREVIEW_FAILED = (
            "Could not preview the operation. "
            "Check that you have the required permissions."
        )


# ---------------------------------------------------------------------------
# CP: Component Placement — PrimaryButton / SecondaryButton
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = QPushButton  # type: ignore[misc,assignment]
    SecondaryButton = QPushButton  # type: ignore[misc,assignment]
    _CP_AVAILABLE = False

try:
    from src.gui.components.modal import ConfirmationModal, Modal
except ImportError:
    Modal = None  # type: ignore[assignment,misc]
    ConfirmationModal = None  # type: ignore[assignment,misc]


from ..core.browser_detector import BrowserDetector
from ..core.platform_utils import PlatformUtils
from ..tools.delete_cookies import DeleteCookiesTool

# Import privacy tools
from ..tools.secure_empty_trash import SecureEmptyTrashTool


class PrivacyToolsHub(StandardWindow):
    """Main hub for privacy cleaning tools."""

    def __init__(self, hub_instance=None):
        self._hub = hub_instance
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__("Privacy Tools - Richard's File Utilities")
        else:
            super().__init__()
            self.setWindowTitle(_PrivStrings.WINDOW_TITLE)
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        try:
            from src.rfu.log_manager import get_log_manager

            self._logger = get_log_manager().get_logger("PrivacyToolsHub")
        except Exception:  # ERR: non-fatal — logger fallback to module logger
            self._logger = logging.getLogger("PrivacyToolsHub")

        # Initialize tools
        self.tools = {
            "trash": SecureEmptyTrashTool(),
            "cookies": DeleteCookiesTool(),
        }

        # Initialize browser detector
        self.browser_detector = BrowserDetector()

        # Current operation thread
        self.current_thread = None

        self._setup_ui()
        self._connect_signals()
        self._refresh_browser_info()
        register_gui_component(
            self, tool_id="privacy_tools", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="privacy_tools")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def create_button(self, text, callback=None, primary=True):
        """Override to use CP components when available (CP-1)."""
        if _CP_AVAILABLE:
            btn = PrimaryButton(text) if primary else SecondaryButton(text)
            if callback:
                btn.clicked.connect(callback)
            return btn
        return super().create_button(text, callback, primary)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return hasattr(self, "tab_widget") and self.tab_widget is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("PrivacyToolsHub entering degraded mode")
        except Exception:
            pass
        _emit_telemetry(
            "ui_error_event", tool_id="privacy_tools", error_type="degraded"
        )

    def _setup_ui(self):
        """Setup the user interface."""
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Privacy tools tabs")
        self.main_layout.addWidget(self.tab_widget)

        # Create tabs for each tool category
        self._create_trash_tab()
        self._create_cookies_tab()
        self._create_history_tab()
        self._create_file_history_tab()
        self._create_downloads_tab()
        self._create_overview_tab()

    def _create_overview_tab(self):
        """Create overview tab showing system status."""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)

        # Header
        header = self.create_header("Privacy Tools Overview")
        layout.addWidget(header)

        # System info group
        system_group = self.create_group_box("System Information")
        system_layout = QVBoxLayout()

        platform_label = QLabel(f"Platform: {PlatformUtils.get_platform().title()}")
        ThemeManager.style_label(platform_label)
        system_layout.addWidget(platform_label)

        admin_status = "Administrator" if PlatformUtils.is_admin() else "Standard User"
        admin_label = QLabel(f"Privileges: {admin_status}")
        ThemeManager.style_label(admin_label)
        system_layout.addWidget(admin_label)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Browser info group
        browser_group = self.create_group_box("Detected Browsers")
        browser_layout = QVBoxLayout()

        self.browser_list = QListWidget()
        self.browser_list.setAccessibleName("Detected browsers list")
        browser_layout.addWidget(self.browser_list)

        refresh_btn = self.create_button(
            "Refresh Browser Info", self._refresh_browser_info, primary=False
        )
        browser_layout.addWidget(refresh_btn)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        # Quick actions group
        actions_group = self.create_group_box("Quick Actions")
        actions_layout = QVBoxLayout()

        quick_clean_btn = self.create_button(
            "Quick Clean All", self._quick_clean_all, primary=True
        )
        actions_layout.addWidget(quick_clean_btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        self.tab_widget.addTab(overview_widget, "Overview")

    def _create_trash_tab(self):
        """Create secure empty trash tab."""
        trash_widget = QWidget()
        layout = QVBoxLayout(trash_widget)

        # Header
        header = self.create_header("Secure Empty Trash")
        layout.addWidget(header)

        # Options group
        options_group = self.create_group_box("Options")
        options_layout = QVBoxLayout()

        self.trash_secure_check = QCheckBox("Secure deletion (overwrite files)")
        self.trash_secure_check.setAccessibleName("Secure deletion")
        self.trash_secure_check.setAccessibleDescription(
            "Overwrites file content before deletion to prevent data recovery"
        )
        self.trash_secure_check.setMinimumHeight(44)
        self.trash_backup_check = QCheckBox("Create backup before deletion")
        self.trash_backup_check.setAccessibleName("Create backup before deletion")
        self.trash_backup_check.setAccessibleDescription(
            "Creates a copy of files before they are permanently deleted"
        )
        self.trash_backup_check.setMinimumHeight(44)

        options_layout.addWidget(self.trash_secure_check)
        options_layout.addWidget(self.trash_backup_check)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Preview group
        preview_group = self.create_group_box("Preview")
        preview_layout = QVBoxLayout()

        self.trash_preview_text = QTextEdit()
        self.trash_preview_text.setAccessibleName("Trash operation preview")
        self.trash_preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.trash_preview_text)

        preview_btn = self.create_button(
            "Preview Operation", self._preview_trash_operation, primary=False
        )
        preview_layout.addWidget(preview_btn)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Action buttons
        button_layout = QHBoxLayout()
        empty_trash_btn = self.create_button(
            "Empty Trash", self._execute_trash_operation, primary=True
        )
        button_layout.addWidget(empty_trash_btn)
        layout.addLayout(button_layout)

        # Progress
        self.trash_progress = self.create_progress_bar()
        self.trash_progress.setVisible(False)
        layout.addWidget(self.trash_progress)

        self.tab_widget.addTab(trash_widget, "Empty Trash")

    def _create_cookies_tab(self):
        """Create delete cookies tab."""
        cookies_widget = QWidget()
        layout = QVBoxLayout(cookies_widget)

        # Header
        header = self.create_header("Delete Browser Cookies")
        layout.addWidget(header)

        # Browser selection group
        browser_group = self.create_group_box("Browser Selection")
        browser_layout = QVBoxLayout()

        self.browser_checkboxes = {}
        for browser in ["chrome", "firefox", "edge", "safari"]:
            checkbox = QCheckBox(browser.title())
            checkbox.setChecked(True)
            checkbox.setAccessibleName(f"{browser.title()} browser")
            checkbox.setMinimumHeight(44)
            self.browser_checkboxes[browser] = checkbox
            browser_layout.addWidget(checkbox)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        # Filter options group
        filter_group = self.create_group_box("Filter Options")
        filter_layout = QVBoxLayout()

        # Domain filter
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("Domain filter:"))
        self.domain_filter_edit = TextInput("Domain filter", "e.g., google.com (optional)")
        self.domain_filter_edit.setAccessibleName("Domain filter")
        self.domain_filter_edit.setAccessibleDescription(
            "Enter a domain to delete only cookies from that site; leave blank for all"
        )
        domain_layout.addWidget(self.domain_filter_edit)
        filter_layout.addLayout(domain_layout)

        # Age filter
        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Delete cookies older than:"))
        self.age_spinbox = QSpinBox()
        self.age_spinbox.setAccessibleName("Delete cookies older than (days)")
        self.age_spinbox.setAccessibleDescription(
            "Only cookies older than this many days are deleted; 0 deletes all"
        )
        self.age_spinbox.setMinimumHeight(44)
        self.age_spinbox.setRange(0, 365)
        self.age_spinbox.setValue(0)
        self.age_spinbox.setSuffix(" days (0 = all)")
        age_layout.addWidget(self.age_spinbox)
        filter_layout.addLayout(age_layout)

        # Backup option
        self.cookies_backup_check = QCheckBox("Create backup before deletion")
        self.cookies_backup_check.setAccessibleName("Create cookies backup")
        self.cookies_backup_check.setAccessibleDescription(
            "Saves a backup of all cookies before any deletion takes place"
        )
        self.cookies_backup_check.setMinimumHeight(44)
        filter_layout.addWidget(self.cookies_backup_check)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Preview group
        preview_group = self.create_group_box("Preview")
        preview_layout = QVBoxLayout()

        self.cookies_preview_text = QTextEdit()
        self.cookies_preview_text.setAccessibleName("Cookies operation preview")
        self.cookies_preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.cookies_preview_text)

        preview_btn = self.create_button(
            "Preview Operation", self._preview_cookies_operation, primary=False
        )
        preview_layout.addWidget(preview_btn)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Action buttons
        button_layout = QHBoxLayout()
        delete_cookies_btn = self.create_button(
            "Delete Cookies", self._execute_cookies_operation, primary=True
        )
        button_layout.addWidget(delete_cookies_btn)
        layout.addLayout(button_layout)

        # Progress
        self.cookies_progress = self.create_progress_bar()
        self.cookies_progress.setVisible(False)
        layout.addWidget(self.cookies_progress)

        self.tab_widget.addTab(cookies_widget, "Delete Cookies")

    def _create_history_tab(self):
        """Create delete history tab (placeholder)."""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)

        header = self.create_header("Delete Browser History")
        layout.addWidget(header)

        info_label = QLabel("Browser history deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)

        self.tab_widget.addTab(history_widget, "Delete History")

    def _create_file_history_tab(self):
        """Create delete file history tab (placeholder)."""
        file_history_widget = QWidget()
        layout = QVBoxLayout(file_history_widget)

        header = self.create_header("Delete File History")
        layout.addWidget(header)

        info_label = QLabel("File history deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)

        self.tab_widget.addTab(file_history_widget, "Delete File History")

    def _create_downloads_tab(self):
        """Create delete downloads tab (placeholder)."""
        downloads_widget = QWidget()
        layout = QVBoxLayout(downloads_widget)

        header = self.create_header("Delete Browser Downloads")
        layout.addWidget(header)

        info_label = QLabel("Browser downloads deletion tool will be implemented here.")
        ThemeManager.style_label(info_label)
        layout.addWidget(info_label)

        self.tab_widget.addTab(downloads_widget, "Delete Downloads")

    def _connect_signals(self):
        """Connect tool signals to GUI updates."""
        for tool in self.tools.values():
            tool.progress_updated.connect(self._update_progress)
            tool.operation_complete.connect(self._operation_complete)
            tool.error_occurred.connect(self._show_error)
            tool.status_changed.connect(self._update_status)

    def _refresh_browser_info(self):
        """Refresh browser detection information."""
        self.browser_list.clear()

        detected_browsers = self.browser_detector.detect_installed_browsers()
        running_browsers = self.browser_detector.get_running_browsers()

        for browser in detected_browsers:
            status = "Running" if browser in running_browsers else "Closed"
            item_text = f"{browser.title()} - {status}"

            item = QListWidgetItem(item_text)
            if browser in running_browsers:
                item.setForeground(Colors.WARNING)
            else:
                item.setForeground(Colors.SUCCESS)

            self.browser_list.addItem(item)

        if not detected_browsers:
            item = QListWidgetItem("No supported browsers detected")
            item.setForeground(Colors.TEXT_DISABLED)
            self.browser_list.addItem(item)

    def _preview_trash_operation(self):
        """Preview trash emptying operation."""
        secure_delete = self.trash_secure_check.isChecked()

        try:
            preview = self.tools["trash"].preview_operation(secure_delete=secure_delete)

            preview_text = f"Platform: {preview['platform'].title()}\n"
            preview_text += f"Secure deletion: {'Yes' if secure_delete else 'No'}\n"
            preview_text += f"Items to delete: {len(preview['trash_items'])}\n"

            if preview["trash_items"]:
                preview_text += "\nItems:\n"
                for item in preview["trash_items"][:10]:  # Show first 10 items
                    preview_text += f"  - {item}\n"
                if len(preview["trash_items"]) > 10:
                    preview_text += (
                        f"  ... and {len(preview['trash_items']) - 10} more\n"
                    )

            if preview["warnings"]:
                preview_text += "\nWarnings:\n"
                for warning in preview["warnings"]:
                    preview_text += f"  ! {warning}\n"

            self.trash_preview_text.setPlainText(preview_text)

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self._logger.error("Trash preview failed", exc_info=True)
            if Modal:
                Modal(
                    _PrivStrings.MODAL_ERROR_TITLE,
                    _PrivStrings.ERR_PREVIEW_FAILED,
                    ["OK"],
                    self,
                ).exec_()

    def _preview_cookies_operation(self):
        """Preview cookies deletion operation."""
        selected_browsers = [
            browser
            for browser, checkbox in self.browser_checkboxes.items()
            if checkbox.isChecked()
        ]

        domain_filter = self.domain_filter_edit.text().strip() or None
        days_old = self.age_spinbox.value() if self.age_spinbox.value() > 0 else None

        try:
            preview = self.tools["cookies"].preview_operation(
                browsers=selected_browsers,
                domain_filter=domain_filter,
                days_old=days_old,
            )

            preview_text = f"Selected browsers: {', '.join(b.title() for b in selected_browsers)}\n"
            if domain_filter:
                preview_text += f"Domain filter: {domain_filter}\n"
            if days_old:
                preview_text += f"Age filter: older than {days_old} days\n"

            preview_text += "\nEstimated cookies to delete:\n"
            total_cookies = 0
            for browser, count in preview["estimated_cookies"].items():
                preview_text += f"  {browser.title()}: {count} cookies\n"
                total_cookies += count

            preview_text += f"\nTotal: {total_cookies} cookies\n"

            if preview["warnings"]:
                preview_text += "\nWarnings:\n"
                for warning in preview["warnings"]:
                    preview_text += f"  ! {warning}\n"

            self.cookies_preview_text.setPlainText(preview_text)

        except Exception as e:  # ERR: non-fatal — surfaced via Modal
            self._logger.error("Cookies preview failed", exc_info=True)
            if Modal:
                Modal(
                    _PrivStrings.MODAL_ERROR_TITLE,
                    _PrivStrings.ERR_PREVIEW_FAILED,
                    ["OK"],
                    self,
                ).exec_()

    def _execute_trash_operation(self):
        """Execute trash emptying operation."""
        secure_delete = self.trash_secure_check.isChecked()
        create_backup = self.trash_backup_check.isChecked()

        self.trash_progress.setVisible(True)
        self.trash_progress.setRange(0, 0)  # Indeterminate progress

        def execute():
            return self.tools["trash"].execute_operation(
                secure_delete=secure_delete, create_backup=create_backup
            )

        self.current_thread = self.tools["trash"].run_in_thread(execute)

    def _execute_cookies_operation(self):
        """Execute cookies deletion operation."""
        selected_browsers = [
            browser
            for browser, checkbox in self.browser_checkboxes.items()
            if checkbox.isChecked()
        ]

        if not selected_browsers:
            self.show_error_dialog(
                "No Browsers Selected", "Please select at least one browser."
            )
            return

        domain_filter = self.domain_filter_edit.text().strip() or None
        days_old = self.age_spinbox.value() if self.age_spinbox.value() > 0 else None
        create_backup = self.cookies_backup_check.isChecked()

        self.cookies_progress.setVisible(True)
        self.cookies_progress.setRange(0, len(selected_browsers))

        def execute():
            return self.tools["cookies"].execute_operation(
                browsers=selected_browsers,
                domain_filter=domain_filter,
                days_old=days_old,
                create_backup=create_backup,
            )

        self.current_thread = self.tools["cookies"].run_in_thread(execute)

    def _quick_clean_all(self):
        """Execute quick clean of all privacy data."""
        if ConfirmationModal:
            dlg = ConfirmationModal(
                "Quick Clean All",
                "This will delete cookies from all browsers and empty the trash.\n"
                "Are you sure you want to continue?",
                confirm_text="Continue",
                cancel_text="Cancel",
                parent=self,
            )
            confirmed = dlg.exec_() == QDialog.Accepted
        else:
            reply = QMessageBox.question(
                self,
                "Quick Clean All",
                "This will delete cookies from all browsers and empty the trash.\n"
                "Are you sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            confirmed = reply == QMessageBox.Yes

        if confirmed:
            # Set all browser checkboxes
            for checkbox in self.browser_checkboxes.values():
                checkbox.setChecked(True)

            # Execute cookies operation first, then trash
            self._execute_cookies_operation()

    def _update_progress(self, current, total, message):
        """Update progress bars."""
        # Determine which progress bar to update based on current tab
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 1:  # Trash tab
            if total > 0:
                self.trash_progress.setRange(0, total)
                self.trash_progress.setValue(current)
            self.show_status_message(message)
        elif current_tab == 2:  # Cookies tab
            if total > 0:
                self.cookies_progress.setRange(0, total)
                self.cookies_progress.setValue(current)
            self.show_status_message(message)

    def _operation_complete(self, result):
        """Handle operation completion."""
        # Hide progress bars
        self.trash_progress.setVisible(False)
        self.cookies_progress.setVisible(False)

        if result.success:
            self.show_info_dialog("Operation Complete", result.message)
        else:
            error_details = (
                "\n".join(result.errors) if result.errors else "Unknown error"
            )
            self.show_error_dialog(
                "Operation Failed",
                f"{result.message}\n\nDetails:\n{error_details}",
            )

        # Refresh browser info
        self._refresh_browser_info()

    def _show_error(self, message):
        """Show error message."""
        self.show_error_dialog("Error", message)

    def _update_status(self, message):
        """Update status message."""
        self.show_status_message(message)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_thread and self.current_thread.isRunning():
            if Modal:
                dlg = Modal(
                    "Operation in Progress",
                    "An operation is currently running. Do you want to stop it and exit?",
                    ["Yes", "No"],
                    parent=self,
                )
                confirmed = dlg.exec_() == QDialog.Accepted
            else:
                reply = QMessageBox.question(
                    self,
                    "Operation in Progress",
                    "An operation is currently running. Do you want to stop it and exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                confirmed = reply == QMessageBox.Yes

            if confirmed:
                # Stop all tools
                for tool in self.tools.values():
                    tool.stop_operation()

                # Wait for threads to finish
                if self.current_thread:
                    self.current_thread.quit()
                    self.current_thread.wait(3000)  # Wait up to 3 seconds

                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main function for standalone execution."""
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = PrivacyToolsHub()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
