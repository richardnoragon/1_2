"""
Menu Manager for Richard's File Utilities

This module provides comprehensive menu bar functionality for all GUI windows,
including standardized File, Edit, View, Tools, and Help menus with proper
keyboard shortcuts and platform-specific design guidelines.
"""

import os
import sys
import webbrowser
from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from gui.themes import Colors, Fonts, ThemeManager, Typography


class MenuManager:
    """Centralized menu management for all application windows."""

    def __init__(self, parent_window: QMainWindow):
        """Initialize the menu manager for a specific window."""
        self.parent_window = parent_window
        self.menubar = None
        self.settings = QSettings("RFU", "Menu_Preferences")

        # Menu references for easy access
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.tools_menu = None
        self.help_menu = None

        # Window-specific callbacks
        self.callbacks = {}

    def create_standard_menubar(self, window_type: str = "utility") -> QMenuBar:
        """
        Create a standard menu bar for the application.

        Args:
            window_type: Type of window ("main", "utility", "dialog")

        Returns:
            Configured QMenuBar instance
        """
        self.menubar = self.parent_window.menuBar()
        self.menubar.clear()

        # Apply menu bar styling
        self._apply_menubar_styling()

        # Create standard menus
        self._create_file_menu(window_type)

        if window_type in ["main", "utility"]:
            self._create_edit_menu()
            self._create_view_menu()
            self._create_tools_menu()

        self._create_help_menu()

        return self.menubar

    def _apply_menubar_styling(self):
        """Apply consistent styling to the menu bar."""
        self.menubar.setStyleSheet(
            f"""
            QMenuBar {{
                background-color: {Colors.BACKGROUND_LIGHT.name()};
                color: {Colors.TEXT_PRIMARY.name()};
                border-bottom: 1px solid {Colors.BORDER_LIGHT.name()};
                padding: 2px;
                font-family: {Fonts.PRIMARY_FAMILY};
                font-size: {Fonts.NORMAL_SIZE}pt;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                margin: 0px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {Colors.PRIMARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
            }}
            
            QMenuBar::item:pressed {{
                background-color: {Colors.PRIMARY_PRESSED.name()};
            }}
            
            QMenu {{
                background-color: {Colors.BACKGROUND_LIGHT.name()};
                color: {Colors.TEXT_PRIMARY.name()};
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 4px;
                padding: 2px;
                margin: 0px;
            }}
            
            QMenu::item {{
                background-color: transparent;
                padding: 8px 24px 8px 32px;
                margin: 1px;
                border-radius: 3px;
            }}
            
            QMenu::item:selected {{
                background-color: {Colors.PRIMARY.name()};
                color: {Colors.TEXT_LIGHT.name()};
            }}
            
            QMenu::item:disabled {{
                color: {Colors.TEXT_DISABLED.name()};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {Colors.BORDER_LIGHT.name()};
                margin: 4px 8px;
            }}
            
            QMenu::indicator {{
                width: 16px;
                height: 16px;
                left: 8px;
            }}
            
            QMenu::indicator:checked {{
                image: url(:/icons/check.png);
            }}
        """
        )

    def _create_file_menu(self, window_type: str):
        """Create the File menu with standard actions."""
        self.file_menu = self.menubar.addMenu("&File")

        if window_type == "main":
            # New actions for main window
            new_action = self._create_action(
                "&New Project...",
                "Ctrl+N",
                "Create a new project",
                callback=self._get_callback("new_project"),
            )
            self.file_menu.addAction(new_action)

            # Open actions
            open_action = self._create_action(
                "&Open...",
                "Ctrl+O",
                "Open a file or project",
                callback=self._get_callback("open_file"),
            )
            self.file_menu.addAction(open_action)

            # Recent files submenu
            recent_menu = self.file_menu.addMenu("Recent &Files")
            self._populate_recent_files_menu(recent_menu)

            self.file_menu.addSeparator()

        # Save actions (for applicable windows)
        if window_type in ["main", "utility"]:
            save_action = self._create_action(
                "&Save",
                "Ctrl+S",
                "Save current work",
                callback=self._get_callback("save_file"),
            )
            self.file_menu.addAction(save_action)

            save_as_action = self._create_action(
                "Save &As...",
                "Ctrl+Shift+S",
                "Save with a new name",
                callback=self._get_callback("save_as_file"),
            )
            self.file_menu.addAction(save_as_action)

            self.file_menu.addSeparator()

            # Export/Import
            export_action = self._create_action(
                "&Export...",
                "Ctrl+E",
                "Export data",
                callback=self._get_callback("export_data"),
            )
            self.file_menu.addAction(export_action)

            import_action = self._create_action(
                "&Import...",
                "Ctrl+I",
                "Import data",
                callback=self._get_callback("import_data"),
            )
            self.file_menu.addAction(import_action)

            self.file_menu.addSeparator()

        # Print actions (for applicable windows)
        if window_type in ["main", "utility"]:
            print_action = self._create_action(
                "&Print...",
                "Ctrl+P",
                "Print current document",
                callback=self._get_callback("print_document"),
            )
            self.file_menu.addAction(print_action)

            self.file_menu.addSeparator()

        # Preferences/Settings
        preferences_action = self._create_action(
            "Pr&eferences...",
            "Ctrl+,",
            "Open application preferences",
            callback=self._get_callback("show_preferences"),
        )
        self.file_menu.addAction(preferences_action)

        self.file_menu.addSeparator()

        # Exit action (standard Ctrl+Q)
        exit_action = self._create_action(
            "E&xit",
            "Ctrl+Q",
            "Exit the application",
            callback=self._exit_application,
        )
        self.file_menu.addAction(exit_action)

    def _create_edit_menu(self):
        """Create the Edit menu with standard actions."""
        self.edit_menu = self.menubar.addMenu("&Edit")

        # Standard edit actions
        undo_action = self._create_action(
            "&Undo",
            "Ctrl+Z",
            "Undo last action",
            callback=self._get_callback("undo"),
        )
        self.edit_menu.addAction(undo_action)

        redo_action = self._create_action(
            "&Redo",
            "Ctrl+Y",
            "Redo last undone action",
            callback=self._get_callback("redo"),
        )
        self.edit_menu.addAction(redo_action)

        self.edit_menu.addSeparator()

        # Clipboard actions
        cut_action = self._create_action(
            "Cu&t",
            "Ctrl+X",
            "Cut selection to clipboard",
            callback=self._get_callback("cut"),
        )
        self.edit_menu.addAction(cut_action)

        copy_action = self._create_action(
            "&Copy",
            "Ctrl+C",
            "Copy selection to clipboard",
            callback=self._get_callback("copy"),
        )
        self.edit_menu.addAction(copy_action)

        paste_action = self._create_action(
            "&Paste",
            "Ctrl+V",
            "Paste from clipboard",
            callback=self._get_callback("paste"),
        )
        self.edit_menu.addAction(paste_action)

        self.edit_menu.addSeparator()

        # Selection actions
        select_all_action = self._create_action(
            "Select &All",
            "Ctrl+A",
            "Select all items",
            callback=self._get_callback("select_all"),
        )
        self.edit_menu.addAction(select_all_action)

        # Find actions
        self.edit_menu.addSeparator()

        find_action = self._create_action(
            "&Find...",
            "Ctrl+F",
            "Find text or items",
            callback=self._get_callback("find"),
        )
        self.edit_menu.addAction(find_action)

        replace_action = self._create_action(
            "&Replace...",
            "Ctrl+H",
            "Find and replace text",
            callback=self._get_callback("replace"),
        )
        self.edit_menu.addAction(replace_action)

    def _create_view_menu(self):
        """Create the View menu with standard actions."""
        self.view_menu = self.menubar.addMenu("&View")

        # Zoom actions
        zoom_in_action = self._create_action(
            "Zoom &In",
            "Ctrl++",
            "Increase zoom level",
            callback=self._get_callback("zoom_in"),
        )
        self.view_menu.addAction(zoom_in_action)

        zoom_out_action = self._create_action(
            "Zoom &Out",
            "Ctrl+-",
            "Decrease zoom level",
            callback=self._get_callback("zoom_out"),
        )
        self.view_menu.addAction(zoom_out_action)

        zoom_reset_action = self._create_action(
            "Reset &Zoom",
            "Ctrl+0",
            "Reset zoom to default",
            callback=self._get_callback("zoom_reset"),
        )
        self.view_menu.addAction(zoom_reset_action)

        self.view_menu.addSeparator()

        # Theme submenu
        theme_menu = self.view_menu.addMenu("&Theme")

        # Theme actions with radio button behavior
        theme_group = QActionGroup(self.parent_window)

        light_theme_action = self._create_action(
            "&Light Theme",
            "",
            "Switch to light theme",
            callback=lambda: self._set_theme("light"),
            checkable=True,
        )
        theme_group.addAction(light_theme_action)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = self._create_action(
            "&Dark Theme",
            "",
            "Switch to dark theme",
            callback=lambda: self._set_theme("dark"),
            checkable=True,
        )
        theme_group.addAction(dark_theme_action)
        theme_menu.addAction(dark_theme_action)

        # Set current theme as checked
        current_theme = self.settings.value("theme", "light")
        if current_theme == "light":
            light_theme_action.setChecked(True)
        else:
            dark_theme_action.setChecked(True)

        self.view_menu.addSeparator()

        # Fullscreen toggle
        fullscreen_action = self._create_action(
            "&Fullscreen",
            "F11",
            "Toggle fullscreen mode",
            callback=self._toggle_fullscreen,
            checkable=True,
        )
        self.view_menu.addAction(fullscreen_action)

        # Always on top toggle
        always_on_top_action = self._create_action(
            "Always on &Top",
            "",
            "Keep window always on top",
            callback=self._toggle_always_on_top,
            checkable=True,
        )
        self.view_menu.addAction(always_on_top_action)

        self.view_menu.addSeparator()

        # Refresh action
        refresh_action = self._create_action(
            "&Refresh",
            "F5",
            "Refresh current view",
            callback=self._get_callback("refresh"),
        )
        self.view_menu.addAction(refresh_action)

    def _create_tools_menu(self):
        """Create the Tools menu with standard actions."""
        self.tools_menu = self.menubar.addMenu("&Tools")

        # Tool-specific actions (to be customized by individual tools)
        options_action = self._create_action(
            "&Options...",
            "",
            "Configure tool options",
            callback=self._get_callback("show_options"),
        )
        self.tools_menu.addAction(options_action)

        self.tools_menu.addSeparator()

        # Common utility actions
        log_viewer_action = self._create_action(
            "&Log Viewer...",
            "",
            "View application logs",
            callback=self._show_log_viewer,
        )
        self.tools_menu.addAction(log_viewer_action)

        performance_action = self._create_action(
            "&Performance Monitor...",
            "",
            "Monitor application performance",
            callback=self._get_callback("show_performance"),
        )
        self.tools_menu.addAction(performance_action)

        self.tools_menu.addSeparator()

        # Reset/Clear actions
        reset_settings_action = self._create_action(
            "&Reset Settings...",
            "",
            "Reset application settings to defaults",
            callback=self._reset_settings,
        )
        self.tools_menu.addAction(reset_settings_action)

    def _create_help_menu(self):
        """Create the Help menu with standard actions."""
        self.help_menu = self.menubar.addMenu("&Help")

        # Documentation actions
        user_guide_action = self._create_action(
            "&User Guide",
            "F1",
            "Open user documentation",
            callback=self._show_user_guide,
        )
        self.help_menu.addAction(user_guide_action)

        keyboard_shortcuts_action = self._create_action(
            "&Keyboard Shortcuts...",
            "Ctrl+?",
            "View keyboard shortcuts",
            callback=self._show_keyboard_shortcuts,
        )
        self.help_menu.addAction(keyboard_shortcuts_action)

        self.help_menu.addSeparator()

        # Online resources
        website_action = self._create_action(
            "Visit &Website",
            "",
            "Open official website",
            callback=lambda: webbrowser.open("https://github.com/richardnoragon"),
        )
        self.help_menu.addAction(website_action)

        report_bug_action = self._create_action(
            "&Report Bug...",
            "",
            "Report a bug or issue",
            callback=lambda: webbrowser.open(
                "https://github.com/richardnoragon/issues"
            ),
        )
        self.help_menu.addAction(report_bug_action)

        self.help_menu.addSeparator()

        # System info and about
        system_info_action = self._create_action(
            "System &Information...",
            "",
            "View system information",
            callback=self._show_system_info,
        )
        self.help_menu.addAction(system_info_action)

        check_updates_action = self._create_action(
            "Check for &Updates...",
            "",
            "Check for application updates",
            callback=self._check_for_updates,
        )
        self.help_menu.addAction(check_updates_action)

        self.help_menu.addSeparator()

        # About dialog
        about_action = self._create_action(
            "&About...",
            "",
            "About this application",
            callback=self._show_about_dialog,
        )
        self.help_menu.addAction(about_action)

    def _create_action(
        self,
        text: str,
        shortcut: str,
        tooltip: str,
        callback: Optional[Callable] = None,
        checkable: bool = False,
    ) -> QAction:
        """Create a standardized menu action."""
        action = QAction(text, self.parent_window)

        if shortcut:
            action.setShortcut(QKeySequence(shortcut))

        if tooltip:
            action.setStatusTip(tooltip)
            action.setToolTip(tooltip)

        if callback:
            action.triggered.connect(callback)

        if checkable:
            action.setCheckable(True)

        return action

    def _get_callback(self, action_name: str) -> Callable:
        """Get callback function for an action, with fallback."""
        return self.callbacks.get(
            action_name, lambda: self._default_action(action_name)
        )

    def _default_action(self, action_name: str):
        """Default action handler for unimplemented features."""
        QMessageBox.information(
            self.parent_window,
            "Feature Not Implemented",
            f"The '{action_name}' feature is not yet implemented in this tool.",
        )

    def register_callback(self, action_name: str, callback: Callable):
        """Register a callback for a specific menu action."""
        self.callbacks[action_name] = callback

    def _exit_application(self):
        """Handle application exit with proper cleanup."""
        reply = QMessageBox.question(
            self.parent_window,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Save window state
            self._save_window_state()

            # Close the application
            if hasattr(self.parent_window, "close_application"):
                self.parent_window.close_application()
            else:
                self.parent_window.close()

    def _populate_recent_files_menu(self, menu: QMenu):
        """Populate the recent files menu."""
        recent_files = self.settings.value("recent_files", [])

        if isinstance(recent_files, str):
            recent_files = [recent_files]
        elif not isinstance(recent_files, list):
            recent_files = []

        if recent_files:
            for i, file_path in enumerate(
                recent_files[:10]
            ):  # Limit to 10 recent files
                if os.path.exists(file_path):
                    action = QAction(
                        f"&{i+1} {os.path.basename(file_path)}",
                        self.parent_window,
                    )
                    action.setStatusTip(file_path)
                    action.triggered.connect(
                        lambda checked, path=file_path: self._open_recent_file(path)
                    )
                    menu.addAction(action)

            menu.addSeparator()

            clear_action = QAction("&Clear Recent Files", self.parent_window)
            clear_action.triggered.connect(self._clear_recent_files)
            menu.addAction(clear_action)
        else:
            no_recent_action = QAction("No recent files", self.parent_window)
            no_recent_action.setEnabled(False)
            menu.addAction(no_recent_action)

    def _open_recent_file(self, file_path: str):
        """Open a recent file."""
        if hasattr(self.parent_window, "open_file"):
            self.parent_window.open_file(file_path)
        else:
            self._default_action(f"open recent file: {file_path}")

    def _clear_recent_files(self):
        """Clear the recent files list."""
        self.settings.setValue("recent_files", [])

    def _set_theme(self, theme_name: str):
        """Change the application theme."""
        self.settings.setValue("theme", theme_name)

        if theme_name == "dark":
            from gui.themes import ThemeType

            ThemeManager.set_theme(ThemeType.DARK)
        else:
            from gui.themes import ThemeType

            ThemeManager.set_theme(ThemeType.LIGHT)

        # Reapply menu styling
        self._apply_menubar_styling()

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.parent_window.isFullScreen():
            self.parent_window.showNormal()
        else:
            self.parent_window.showFullScreen()

    def _toggle_always_on_top(self):
        """Toggle always on top mode."""
        flags = self.parent_window.windowFlags()
        if flags & Qt.WindowStaysOnTopHint:
            self.parent_window.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        else:
            self.parent_window.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        self.parent_window.show()

    def _show_log_viewer(self):
        """Show the log viewer dialog."""
        dialog = LogViewerDialog(self.parent_window)
        dialog.exec_()

    def _reset_settings(self):
        """Reset application settings to defaults."""
        reply = QMessageBox.question(
            self.parent_window,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.settings.clear()
            QMessageBox.information(
                self.parent_window,
                "Settings Reset",
                "Settings have been reset to defaults.\nPlease restart the application for changes to take effect.",
            )

    def _show_user_guide(self):
        """Show the user guide."""
        help_dialog = HelpDialog(self.parent_window)
        help_dialog.exec_()

    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_dialog = KeyboardShortcutsDialog(self.parent_window)
        shortcuts_dialog.exec_()

    def _show_system_info(self):
        """Show system information dialog."""
        info_dialog = SystemInfoDialog(self.parent_window)
        info_dialog.exec_()

    def _check_for_updates(self):
        """Check for application updates."""
        QMessageBox.information(
            self.parent_window,
            "Check for Updates",
            "Update checking functionality will be implemented in a future version.",
        )

    def _show_about_dialog(self):
        """Show the about dialog."""
        about_dialog = AboutDialog(self.parent_window)
        about_dialog.exec_()

    def _save_window_state(self):
        """Save the current window state."""
        self.settings.setValue("window_geometry", self.parent_window.saveGeometry())
        self.settings.setValue("window_state", self.parent_window.saveState())

    def restore_window_state(self):
        """Restore the saved window state."""
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.parent_window.restoreGeometry(geometry)

        state = self.settings.value("window_state")
        if state:
            self.parent_window.restoreState(state)


class LogViewerDialog(QDialog):
    """Dialog for viewing application logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(Typography.monospace())
        layout.addWidget(self.log_text)

        # Load logs
        self._load_logs()

        # Buttons
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_logs)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Apply theme
        ThemeManager.apply_dialog_theme(self)

    def _load_logs(self):
        """Load and display logs."""
        log_file = "rfu_errors.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_text.setPlainText(content)
                # Scroll to bottom
                self.log_text.moveCursor(self.log_text.textCursor().End)
            except Exception as e:
                self.log_text.setPlainText(f"Error loading log file: {e}")
        else:
            self.log_text.setPlainText("No log file found.")


class HelpDialog(QDialog):
    """Dialog for displaying help information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml(
            """
        <h2>Richard's File Utilities - User Guide</h2>
        
        <h3>Getting Started</h3>
        <p>Welcome to Richard's File Utilities! This comprehensive toolkit provides
        various file management, analysis, and security tools.</p>
        
        <h3>Menu Overview</h3>
        <ul>
        <li><b>File Menu:</b> File operations, preferences, and exit</li>
        <li><b>Edit Menu:</b> Standard editing operations</li>
        <li><b>View Menu:</b> Display options and themes</li>
        <li><b>Tools Menu:</b> Tool-specific options and utilities</li>
        <li><b>Help Menu:</b> Documentation and support</li>
        </ul>
        
        <h3>Keyboard Shortcuts</h3>
        <ul>
        <li><b>Ctrl+N:</b> New project</li>
        <li><b>Ctrl+O:</b> Open file</li>
        <li><b>Ctrl+S:</b> Save</li>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Refresh</li>
        <li><b>F11:</b> Toggle fullscreen</li>
        </ul>
        
        <h3>Support</h3>
        <p>For additional help, visit our website or report issues through the Help menu.</p>
        """
        )
        layout.addWidget(help_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Apply theme
        ThemeManager.apply_dialog_theme(self)


class KeyboardShortcutsDialog(QDialog):
    """Dialog for displaying keyboard shortcuts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)
        self.resize(400, 350)

        layout = QVBoxLayout(self)

        shortcuts_text = QTextEdit()
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setHtml(
            """
        <h2>Keyboard Shortcuts</h2>
        
        <h3>File Operations</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>Ctrl+N</b></td><td>New project</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Print</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
        </table>
        
        <h3>Edit Operations</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
        <tr><td><b>Ctrl+X</b></td><td>Cut</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Copy</td></tr>
        <tr><td><b>Ctrl+V</b></td><td>Paste</td></tr>
        <tr><td><b>Ctrl+A</b></td><td>Select All</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Find</td></tr>
        <tr><td><b>Ctrl+H</b></td><td>Replace</td></tr>
        </table>
        
        <h3>View Operations</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Reset Zoom</td></tr>
        <tr><td><b>F11</b></td><td>Fullscreen</td></tr>
        <tr><td><b>F5</b></td><td>Refresh</td></tr>
        </table>
        
        <h3>Help</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>F1</b></td><td>User Guide</td></tr>
        <tr><td><b>Ctrl+?</b></td><td>Keyboard Shortcuts</td></tr>
        </table>
        """
        )
        layout.addWidget(shortcuts_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Apply theme
        ThemeManager.apply_dialog_theme(self)


class SystemInfoDialog(QDialog):
    """Dialog for displaying system information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Information")
        self.setModal(True)
        self.resize(450, 300)

        layout = QVBoxLayout(self)

        info_text = QTextEdit()
        info_text.setReadOnly(True)

        # Gather system information
        import platform

        import PyQt5.QtCore

        info_html = f"""
        <h2>System Information</h2>
        
        <h3>Application</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>Name:</b></td><td>Richard's File Utilities</td></tr>
        <tr><td><b>Version:</b></td><td>2.0.0</td></tr>
        <tr><td><b>Qt Version:</b></td><td>{PyQt5.QtCore.QT_VERSION_STR}</td></tr>
        <tr><td><b>PyQt Version:</b></td><td>{PyQt5.QtCore.PYQT_VERSION_STR}</td></tr>
        </table>
        
        <h3>System</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>OS:</b></td><td>{platform.system()} {platform.release()}</td></tr>
        <tr><td><b>Architecture:</b></td><td>{platform.architecture()[0]}</td></tr>
        <tr><td><b>Machine:</b></td><td>{platform.machine()}</td></tr>
        <tr><td><b>Python:</b></td><td>{platform.python_version()}</td></tr>
        <tr><td><b>Node:</b></td><td>{platform.node()}</td></tr>
        </table>
        """

        info_text.setHtml(info_html)
        layout.addWidget(info_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Apply theme
        ThemeManager.apply_dialog_theme(self)


class AboutDialog(QDialog):
    """Dialog for displaying about information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        about_text = QLabel()
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setText(
            """
        Richard's File Utilities
        Version 2.0.0
        
        A comprehensive suite of file management,
        analysis, and security tools.
        
        © 2025 Richard Noragon
        
        This software is provided as-is under the
        terms of the included license agreement.
        
        Visit our website for updates and support.
        """
        )

        # Style the about text
        about_text.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Fonts.MEDIUM_SIZE}pt;
                color: {Colors.TEXT_PRIMARY.name()};
                padding: 20px;
                line-height: 1.5;
            }}
        """
        )

        layout.addWidget(about_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Apply theme
        ThemeManager.apply_dialog_theme(self)
