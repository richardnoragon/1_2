"""
Simple menu bar implementation used by the RFU Hub launcher.

The original menu framework lived in legacy packages that are no longer
shipped with the application.  This lightweight drop-in replacement keeps
those entry points alive so the rest of the hub does not need to change.
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path
from typing import Callable, Dict, Iterable, cast

from PyQt5.QtGui import QFont, QKeySequence

try:
    from src.gui.themes import Typography as _Typography
except ImportError:
    try:
        from gui.themes import Typography as _Typography
    except ImportError:
        _Typography = None
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
)

HELP_DOC_CANDIDATES = [
    "docs/user-guides/rfu_user_guide_scroll_version.html",
    "docs/user-guides/rfu_user_guide_scroll_version.md",
    "docs/user_guides/rfu_user_guide_scroll_version.html",
    "docs/user_guides/rfu_user_guide_scroll_version.md",
    "docs/help_system/rfu_user_guide_scroll_version.html",
    "docs/help_system/rfu_user_guide_scroll_version.md",
    "docs/rfu_user_guide_scroll_version.html",
    "docs/rfu_user_guide_scroll_version.md",
]

SHORTCUT_DOC_CANDIDATES = [
    "docs/keybindings implementation chacklist.md",
    "docs/keybindings_implementation_checklist.md",
    "docs/user-guides/keybindings_reference.md",
    "docs/user_guides/keybindings_reference.md",
    "docs/help_system/keybindings_reference.md",
]

LOG_FILE_CANDIDATES = [
    "src/logs/rfu.log",
    "logs/rfu.log",
]


class SimpleMenuManager:
    """Builds the minimal menu structure required by the hub."""

    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.callbacks: Dict[str, Callable[[], None]] = {}

    def create_menubar(self) -> QMenuBar:
        menubar = self.parent_window.menuBar()
        if menubar is None:
            menubar = QMenuBar(self.parent_window)
            self.parent_window.setMenuBar(menubar)

        menubar_obj: QMenuBar = cast(QMenuBar, menubar)
        menubar_obj.clear()

        file_menu: QMenu = QMenu("&File", menubar_obj)
        menubar_obj.addMenu(file_menu)
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

        edit_menu: QMenu = QMenu("&Edit", menubar_obj)
        menubar_obj.addMenu(edit_menu)
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

        view_menu: QMenu = QMenu("&View", menubar_obj)
        menubar_obj.addMenu(view_menu)
        self._add_action(view_menu, "Zoom &In", "Ctrl++", "zoom_in")
        self._add_action(view_menu, "Zoom &Out", "Ctrl+-", "zoom_out")
        self._add_action(view_menu, "Reset &Zoom", "Ctrl+0", "zoom_reset")
        view_menu.addSeparator()
        theme_menu: QMenu = QMenu("&Theme", view_menu)
        view_menu.addMenu(theme_menu)
        self._add_action(theme_menu, "&Light Theme", "", "light_theme")
        self._add_action(theme_menu, "&Dark Theme", "", "dark_theme")
        view_menu.addSeparator()
        self._add_action(view_menu, "&Refresh", "F5", "refresh")

        tools_menu: QMenu = QMenu("&Tools", menubar_obj)
        menubar_obj.addMenu(tools_menu)
        self._add_action(tools_menu, "&Options...", "", "options")
        tools_menu.addSeparator()
        self._add_action(tools_menu, "&Log Viewer...", "", "log_viewer")
        self._add_action(
            tools_menu,
            "&Performance Monitor...",
            "",
            "performance",
        )
        tools_menu.addSeparator()
        self._add_action(
            tools_menu,
            "&Reset Settings...",
            "",
            "reset_settings",
        )

        help_menu: QMenu = QMenu("&Help", menubar_obj)
        menubar_obj.addMenu(help_menu)
        self._add_action(help_menu, "&User Guide", "F1", "user_guide")
        self._add_action(
            help_menu,
            "&Keyboard Shortcuts...",
            "Ctrl+?",
            "shortcuts",
        )
        help_menu.addSeparator()
        self._add_action(help_menu, "&About...", "", "about")

        return menubar

    def register_callback(self, action_name: str, callback: Callable[[], None]) -> None:
        self.callbacks[action_name] = callback

    def _add_action(
        self, menu: QMenu, text: str, shortcut: str, callback_name: str
    ) -> QAction:
        action = QAction(text, self.parent_window)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda: self._handle_action(callback_name))
        menu.addAction(action)
        return action

    def _handle_action(self, callback_name: str) -> None:
        callback = self.callbacks.get(callback_name)
        if callback:
            callback()
            return

        status_bar = getattr(self.parent_window, "status_bar", None)
        if status_bar is not None:
            status_bar.showMessage(
                f"{callback_name.replace('_', ' ').title()} - " "Feature coming soon..."
            )

        if callback_name == "about":
            self._show_about()
        elif callback_name == "user_guide":
            self._show_help()
        elif callback_name == "shortcuts":
            self._show_shortcuts()
        elif callback_name == "log_viewer":
            self._show_log_viewer()

    def _show_about(self) -> None:
        QMessageBox.about(
            self.parent_window,
            "About Richard's File Utilities",
            (
                "<h2>Richard's File Utilities</h2>"
                "<p>Version 3.0.0</p>"
                "<p>Modular file, analysis, and security tooling suite.</p>"
                "<p>© 2025 Richard Noragon</p>"
            ),
        )

    def _show_help(self) -> None:
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("User Guide")
        dialog.setModal(True)
        dialog.resize(520, 420)

        layout = QVBoxLayout(dialog)
        help_text = QTextEdit()
        help_text.setAccessibleName("User guide content")
        help_text.setReadOnly(True)
        help_text.setHtml(self._load_help_content())
        layout.addWidget(help_text)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close user guide")
        close_btn.setMinimumHeight(44)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_shortcuts(self) -> None:
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setModal(True)
        dialog.resize(420, 360)

        layout = QVBoxLayout(dialog)
        shortcuts_text = QTextEdit()
        shortcuts_text.setAccessibleName("Keyboard shortcuts list")
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setHtml(self._load_shortcuts_content())
        layout.addWidget(shortcuts_text)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close keyboard shortcuts")
        close_btn.setMinimumHeight(44)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_log_viewer(self) -> None:
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Log Viewer")
        dialog.setModal(True)
        dialog.resize(620, 420)

        layout = QVBoxLayout(dialog)
        log_text = QTextEdit()
        log_text.setAccessibleName("Application log viewer")
        log_text.setReadOnly(True)
        log_text.setFont(
            _Typography.monospace() if _Typography else QFont("Consolas", 9)
        )

        log_text.setPlainText(self._load_log_content())
        log_text.moveCursor(log_text.textCursor().End)
        layout.addWidget(log_text)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close log viewer")
        close_btn.setMinimumHeight(44)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    # ------------------------------------------------------------------
    # File helpers
    # ------------------------------------------------------------------
    def _project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _load_help_content(self) -> str:
        return self._read_first_available(
            HELP_DOC_CANDIDATES, self._default_help_content()
        )

    def _load_shortcuts_content(self) -> str:
        return self._read_first_available(
            SHORTCUT_DOC_CANDIDATES,
            self._default_shortcuts_content(),
        )

    def _load_log_content(self) -> str:
        root = self._project_root()
        for relative in LOG_FILE_CANDIDATES:
            log_path = root / relative
            if log_path.exists():
                return log_path.read_text(encoding="utf-8")
        return "No log file found."

    def _read_first_available(
        self, relative_candidates: Iterable[str], fallback: str
    ) -> str:
        root = self._project_root()
        for relative in relative_candidates:
            candidate = root / relative
            if candidate.exists():
                text = candidate.read_text(encoding="utf-8")
                if candidate.suffix.lower() == ".md":
                    return self._render_markdown(text)
                return text
        return fallback

    @staticmethod
    def _render_markdown(markdown_text: str) -> str:
        return (
            "<pre style='white-space: pre-wrap; "
            "font-family: Consolas, monospace;'>"
            f"{escape(markdown_text.strip())}"
            "</pre>"
        )

    @staticmethod
    def _default_help_content() -> str:
        return (
            "<h2>Richard's File Utilities - User Guide</h2>"
            "<p>Official documentation is stored under the docs directory.</p>"
            "<p>Open the on-disk guide for the most up-to-date "
            "instructions.</p>"
        )

    @staticmethod
    def _default_shortcuts_content() -> str:
        return (
            "<h2>Keyboard Shortcuts</h2>"
            "<table border='1' cellpadding='5' "
            "style='border-collapse: collapse;'>"
            "<tr><td><b>Ctrl+N</b></td><td>New project</td></tr>"
            "<tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>"
            "<tr><td><b>Ctrl+S</b></td><td>Save current view</td></tr>"
            "<tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>"
            "<tr><td><b>Ctrl+F</b></td><td>Find resources</td></tr>"
            "<tr><td><b>F1</b></td><td>Open user guide</td></tr>"
            "</table>"
        )


def _launch_demo() -> None:
    """Standalone preview for developers who run this file directly."""

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("RFU Menu Manager Demo")
    window.resize(960, 600)

    label = QLabel(
        "This demo window only exists to preview the SimpleMenuManager.\n"
        "Launch the full RFU Hub via src/main.py for the complete experience."
    )
    label.setWordWrap(True)
    label.setMargin(16)
    window.setCentralWidget(label)

    status = window.statusBar()
    if status is None:
        status = QStatusBar(window)
        window.setStatusBar(status)
    status.showMessage("Ready")
    window.status_bar = status  # type: ignore[attr-defined]

    manager = SimpleMenuManager(window)
    manager.create_menubar()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    _launch_demo()
