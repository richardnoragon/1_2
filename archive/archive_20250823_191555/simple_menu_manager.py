"""
Simplified menu system for RFU Hub

This provides a basic menu system that integrates directly with the Simple RFU Hub
without complex dependencies.
"""

from PyQt5.QtWidgets import (
    QMenuBar,
    QMenu,
    QAction,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QFont


class SimpleMenuManager:
    """Simplified menu manager for the RFU Hub."""

    def __init__(self, parent_window):
        """Initialize the menu manager."""
        self.parent_window = parent_window
        self.callbacks = {}

    def create_menubar(self):
        """Create a complete menu bar for the RFU Hub."""
        menubar = self.parent_window.menuBar()
        menubar.clear()

        # File Menu
        file_menu = menubar.addMenu("&File")

        # File menu actions
        self._add_action(file_menu, "&New Project...", "Ctrl+N", "new_project")
        self._add_action(file_menu, "&Open...", "Ctrl+O", "open_file")
        file_menu.addSeparator()
        self._add_action(file_menu, "&Save", "Ctrl+S", "save_file")
        self._add_action(file_menu, "Save &As...", "Ctrl+Shift+S", "save_as")
        file_menu.addSeparator()
        self._add_action(file_menu, "&Export...", "Ctrl+E", "export_data")
        self._add_action(file_menu, "&Import...", "Ctrl+I", "import_data")
        file_menu.addSeparator()
        self._add_action(file_menu, "Pr&eferences...", "Ctrl+,", "preferences")
        file_menu.addSeparator()

        exit_action = QAction("E&xit", self.parent_window)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.parent_window.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        self._add_action(edit_menu, "&Undo", "Ctrl+Z", "undo")
        self._add_action(edit_menu, "&Redo", "Ctrl+Y", "redo")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Cu&t", "Ctrl+X", "cut")
        self._add_action(edit_menu, "&Copy", "Ctrl+C", "copy")
        self._add_action(edit_menu, "&Paste", "Ctrl+V", "paste")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Select &All", "Ctrl+A", "select_all")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "&Find...", "Ctrl+F", "find_action")
        self._add_action(edit_menu, "&Replace...", "Ctrl+H", "replace_action")

        # View Menu
        view_menu = menubar.addMenu("&View")
        self._add_action(view_menu, "Zoom &In", "Ctrl++", "zoom_in")
        self._add_action(view_menu, "Zoom &Out", "Ctrl+-", "zoom_out")
        self._add_action(view_menu, "Reset &Zoom", "Ctrl+0", "zoom_reset")
        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")
        self._add_action(theme_menu, "&Light Theme", "", "light_theme")
        self._add_action(theme_menu, "&Dark Theme", "", "dark_theme")

        view_menu.addSeparator()
        self._add_action(view_menu, "&Refresh", "F5", "refresh")

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        self._add_action(tools_menu, "&Options...", "", "options")
        tools_menu.addSeparator()
        self._add_action(tools_menu, "&Log Viewer...", "", "log_viewer")
        self._add_action(
            tools_menu, "&Performance Monitor...", "", "performance"
        )
        tools_menu.addSeparator()
        self._add_action(
            tools_menu, "&Reset Settings...", "", "reset_settings"
        )

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        self._add_action(help_menu, "&User Guide", "F1", "user_guide")
        self._add_action(
            help_menu, "&Keyboard Shortcuts...", "Ctrl+?", "shortcuts"
        )
        help_menu.addSeparator()
        self._add_action(help_menu, "&About...", "", "about")

        return menubar

    def _add_action(self, menu, text, shortcut, callback_name):
        """Add an action to a menu."""
        action = QAction(text, self.parent_window)

        if shortcut:
            action.setShortcut(QKeySequence(shortcut))

        action.triggered.connect(lambda: self._handle_action(callback_name))
        menu.addAction(action)
        return action

    def _handle_action(self, callback_name):
        """Handle menu action."""
        if callback_name in self.callbacks:
            self.callbacks[callback_name]()
        else:
            # Default handler
            if hasattr(self.parent_window, "status_bar"):
                self.parent_window.status_bar.showMessage(
                    f"{callback_name.replace('_', ' ').title()} - Feature coming soon..."
                )

            if callback_name == "about":
                self._show_about()
            elif callback_name == "user_guide":
                self._show_help()
            elif callback_name == "shortcuts":
                self._show_shortcuts()
            elif callback_name == "log_viewer":
                self._show_log_viewer()

    def register_callback(self, action_name, callback):
        """Register a callback for a menu action."""
        self.callbacks[action_name] = callback

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self.parent_window,
            "About Richard's File Utilities",
            """<h2>Richard's File Utilities</h2>
            <p>Version 3.0.0</p>
            <p>A comprehensive suite of file management, analysis, and security tools.</p>
            <p>© 2025 Richard Noragon</p>
            <p>This software provides powerful utilities for file operations, 
            metadata management, security, and system analysis.</p>""",
        )

    def _show_help(self):
        """Show help dialog."""
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("User Guide")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml(
            """
        <h2>Richard's File Utilities - User Guide</h2>
        
        <h3>Overview</h3>
        <p>Welcome to Richard's File Utilities! This application provides comprehensive 
        tools for file management, analysis, and security operations.</p>
        
        <h3>Main Features</h3>
        <ul>
        <li><b>Analysis Tools:</b> Checksum verification, duplicate file finder, size analyzer</li>
        <li><b>File Operations:</b> File splitter, synchronization, backup tools</li>
        <li><b>Metadata Tools:</b> Image and office document metadata editing</li>
        <li><b>Network Tools:</b> Network scanner, connectivity tests, file transfer</li>
        <li><b>PDF Tools:</b> PDF merger, splitter, converter, security tools</li>
        <li><b>Privacy Tools:</b> Privacy cleaner, temporary file cleanup</li>
        <li><b>Security Tools:</b> File encryption, secure delete, password generator</li>
        <li><b>System Tools:</b> System information, disk analyzer, process monitor</li>
        </ul>
        
        <h3>Getting Started</h3>
        <ol>
        <li>Select a category tab that matches your needs</li>
        <li>Click on the specific tool you want to use</li>
        <li>Follow the on-screen instructions for each tool</li>
        </ol>
        
        <h3>Menu System</h3>
        <p>Use the menu bar to access file operations, preferences, and help resources.</p>
        """
        )
        layout.addWidget(help_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setModal(True)
        dialog.resize(400, 350)

        layout = QVBoxLayout(dialog)

        shortcuts_text = QTextEdit()
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setHtml(
            """
        <h2>Keyboard Shortcuts</h2>
        
        <h3>File Operations</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr><td><b>Ctrl+N</b></td><td>New project</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export</td></tr>
        <tr><td><b>Ctrl+I</b></td><td>Import</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
        </table>
        
        <h3>Edit Operations</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
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
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Reset Zoom</td></tr>
        <tr><td><b>F5</b></td><td>Refresh</td></tr>
        </table>
        
        <h3>Help</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr><td><b>F1</b></td><td>User Guide</td></tr>
        <tr><td><b>Ctrl+?</b></td><td>Keyboard Shortcuts</td></tr>
        </table>
        """
        )
        layout.addWidget(shortcuts_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_log_viewer(self):
        """Show log viewer dialog."""
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Log Viewer")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Consolas", 9))

        # Try to load logs
        try:
            import os

            log_file = os.path.join("src", "logs", "rfu.log")
            if not os.path.exists(log_file):
                log_file = os.path.join("logs", "rfu.log")

            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                log_text.setPlainText(content)
                # Scroll to bottom
                log_text.moveCursor(log_text.textCursor().End)
            else:
                log_text.setPlainText("No log file found.")
        except Exception as e:
            log_text.setPlainText(f"Error loading log file: {e}")

        layout.addWidget(log_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()
