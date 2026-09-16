"""
Simple menu bar implementation used by the RFU Hub launcher.

The original menu framework lived in legacy packages that are no longer
shipped with the application.  This lightweight drop-in replacement keeps
those entry points alive so the rest of the hub does not need to change.
"""

from __future__ import annotations

from src.rfu.localization import tr, bind_text

import sys
import weakref
from html import escape
from pathlib import Path
from typing import Callable, Dict, Iterable, cast

from src.rfu import ui_strings

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
    QFileDialog,
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
        self._actions = {}
        self._tool_windows = weakref.WeakValueDictionary()

    def create_menubar(self) -> QMenuBar:
        menu_bar = getattr(self.parent_window, "menuBar", lambda: None)()

        # Some tests and lightweight host objects provide a mock menuBar()
        # instead of a real QMenuBar, so fall back to a real one when needed.
        if menu_bar is None or not hasattr(menu_bar, "clear") or not hasattr(menu_bar, "addMenu"):
            try:
                menu_bar = QMenuBar(self.parent_window)
                if hasattr(self.parent_window, "setMenuBar"):
                    self.parent_window.setMenuBar(menu_bar)
            except Exception:
                return cast(QMenuBar, menu_bar or QMenuBar())

        menubar_obj: QMenuBar = cast(QMenuBar, menu_bar)
        try:
            menubar_obj.clear()
        except Exception:
            pass

        file_menu: QMenu = QMenu(tr("Menu.FILE"), menubar_obj)
        menubar_obj.addMenu(file_menu)
        self._add_action(file_menu, tr("MenuLabels.NEW_PROJECT"), "Ctrl+N", "new_project")
        self._add_action(file_menu, tr("MenuLabels.OPEN"), "Ctrl+O", "open_file")
        file_menu.addSeparator()
        self._add_action(file_menu, tr("MenuLabels.SAVE"), "Ctrl+S", "save_file")
        self._add_action(file_menu, tr("MenuLabels.SAVE_AS"), "Ctrl+Shift+S", "save_as")
        file_menu.addSeparator()
        self._add_action(file_menu, tr("MenuLabels.EXPORT"), "Ctrl+E", "export_data")
        self._add_action(file_menu, tr("MenuLabels.IMPORT"), "Ctrl+I", "import_data")
        file_menu.addSeparator()
        self._add_action(file_menu, tr("MenuLabels.PREFERENCES"), "Ctrl+,", "preferences")
        file_menu.addSeparator()
        exit_action = QAction(tr("MenuLabels.EXIT"), self.parent_window)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.parent_window.close)
        file_menu.addAction(exit_action)

        edit_menu: QMenu = QMenu(tr("Menu.EDIT"), menubar_obj)
        menubar_obj.addMenu(edit_menu)
        self._add_action(edit_menu, tr("MenuLabels.UNDO"), "Ctrl+Z", "undo")
        self._add_action(edit_menu, tr("MenuLabels.REDO"), "Ctrl+Y", "redo")
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("MenuLabels.CUT"), "Ctrl+X", "cut")
        self._add_action(edit_menu, tr("MenuLabels.COPY"), "Ctrl+C", "copy")
        self._add_action(edit_menu, tr("MenuLabels.PASTE"), "Ctrl+V", "paste")
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("MenuLabels.SELECT_ALL"), "Ctrl+A", "select_all")
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("MenuLabels.FIND"), "Ctrl+F", "find_action")
        self._add_action(edit_menu, tr("MenuLabels.REPLACE"), "Ctrl+Shift+H", "replace_action")

        view_menu: QMenu = QMenu(tr("Menu.VIEW"), menubar_obj)
        menubar_obj.addMenu(view_menu)
        self._add_action(view_menu, tr("MenuLabels.ZOOM_IN"), "Ctrl++", "zoom_in")
        self._add_action(view_menu, tr("MenuLabels.ZOOM_OUT"), "Ctrl+-", "zoom_out")
        self._add_action(view_menu, tr("MenuLabels.RESET_ZOOM"), "Ctrl+0", "zoom_reset")
        view_menu.addSeparator()
        theme_menu: QMenu = QMenu(tr("MenuLabels.THEME"), view_menu)
        view_menu.addMenu(theme_menu)
        self._add_action(theme_menu, tr("MenuLabels.LIGHT_THEME"), "", "light_theme")
        self._add_action(theme_menu, tr("MenuLabels.DARK_THEME"), "", "dark_theme")
        view_menu.addSeparator()
        self._add_action(view_menu, tr("MenuLabels.REFRESH"), "F5", "refresh")

        tools_menu: QMenu = QMenu(tr("Menu.TOOLS"), menubar_obj)
        menubar_obj.addMenu(tools_menu)
        self._add_action(tools_menu, tr("MenuLabels.OPTIONS"), "", "options")
        tools_menu.addSeparator()
        self._add_action(tools_menu, tr("MenuLabels.LOG_VIEWER"), "", "log_viewer")
        self._add_action(
            tools_menu,
            tr("MenuLabels.PERFORMANCE_MONITOR"),
            "",
            "performance",
        )
        tools_menu.addSeparator()
        self._add_action(
            tools_menu,
            tr("MenuLabels.RESET_PREFERENCES"),
            "",
            "reset_settings",
        )

        help_menu: QMenu = QMenu(tr("Menu.HELP"), menubar_obj)
        menubar_obj.addMenu(help_menu)
        self._add_action(help_menu, tr("MenuLabels.USER_GUIDE"), "F1", "user_guide")
        self._add_action(
            help_menu,
            tr("MenuLabels.KEYBOARD_SHORTCUTS"),
            "Ctrl+?",
            "shortcuts",
        )
        help_menu.addSeparator()
        self._add_action(help_menu, tr("MenuLabels.ABOUT"), "", "about")

        from src.gui.menu_registry import MenuRegistry
        self.parent_window.menu_registry = MenuRegistry(self.parent_window)
        registry = self.parent_window.menu_registry
        registry.menus["Window"].aboutToShow.connect(self._refresh_windows)
        if not hasattr(self.parent_window, "parent_hub"):
            from src.rfu.localization import service
            if service._preferences is None:
                try:
                    from src.core.preferences.manager import PreferenceManager
                    service.configure_preferences(PreferenceManager())
                except Exception:
                    import logging
                    logging.getLogger(__name__).warning("Locale preferences unavailable; using the active session locale")
            registry.register(tool_id="hub", menu="Tools", label="Menu.LOAD_PLUGIN",
                              accelerator="Ctrl+Shift+P", callback=self._load_plugin)
            registry.register(tool_id="hub", menu="Tools", label="MenuLabels.FILE_WORKFLOW",
                              accelerator="Ctrl+Shift+K", callback=self._show_file_workflow)
            registry.register(tool_id="hub", menu="Tools", label="Menu.CAPABILITIES",
                              accelerator="Ctrl+Shift+D", callback=self._show_capabilities)
            registry.register(tool_id="hub", menu="View", label="MenuLabels.LOAD_LOCALE",
                              accelerator="Ctrl+Shift+L", callback=self._load_locale)
        else:
            action = QAction(ui_strings.Menu.RETURN_TO_HUB, self.parent_window)
            action.setShortcut(QKeySequence("Ctrl+H"))
            action.setStatusTip("Return to the hub")
            action.triggered.connect(self._return_to_hub)
            registry.menus["File"].insertAction(registry.menus["File"].actions()[0], action)
            hub_manager = getattr(self.parent_window.parent_hub, "menu_manager", None)
            if hasattr(hub_manager, "_tool_windows"):
                hub_manager._tool_windows[id(self.parent_window)] = self.parent_window
        return menubar_obj

    def _refresh_windows(self):
        menu = self.parent_window.menu_registry.menus["Window"]
        menu.clear()
        hub = getattr(self.parent_window, "parent_hub", self.parent_window)
        manager = getattr(hub, "menu_manager", self)
        for window in list(getattr(manager, "_tool_windows", {}).values()):
            try:
                title = window.windowTitle()
            except RuntimeError:
                continue
            action = menu.addAction(ui_strings.Menu.REOPEN.format(tool=title))
            action.setStatusTip(title)
            action.triggered.connect(lambda checked=False, ref=weakref.ref(window): self._show_window(ref))

    @staticmethod
    def _show_window(reference):
        window = reference()
        if window is not None:
            try:
                window.show()
                window.raise_()
                window.activateWindow()
            except RuntimeError:
                pass

    def _show_file_workflow(self):
        from src.gui.file_workflow_dialog import FileWorkflowDialog
        dialog = getattr(self, "_file_workflow", None)
        if dialog is None:
            dialog = self._file_workflow = FileWorkflowDialog(self.parent_window)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _show_capabilities(self):
        from src.gui.capability_dialog import CapabilityDialog
        dialog = CapabilityDialog(self.parent_window)
        dialog.exec_()

    def _load_locale(self):
        from src.rfu.localization import service
        path, _ = QFileDialog.getOpenFileName(self.parent_window, tr("MenuLabels.LOAD_LOCALE"), "", "Locale packs (*.json)")
        if not path:
            return
        try:
            locale, missing = service.load(path)
            service.switch(locale)
        except (ValueError, OSError):
            QMessageBox.warning(self.parent_window, "Language", "The language pack is invalid or unavailable.")
            return
        menu = getattr(self, "_language_menu", None)
        if menu is None:
            menu = self._language_menu = self.parent_window.menu_registry.menus["View"].addMenu(tr("MenuLabels.LANGUAGE"))
            service.bind(menu, "setTitle", "MenuLabels.LANGUAGE")
            english = menu.addAction("English")
            english.triggered.connect(lambda: service.switch("en"))
        if not any(action.data() == locale for action in menu.actions()):
            action = menu.addAction(locale)
            action.setData(locale)
            action.triggered.connect(lambda checked=False: service.switch(locale))

    def _return_to_hub(self):
        hub = self.parent_window.parent_hub
        hub.show()
        hub.raise_()
        hub.activateWindow()

    def _load_plugin(self):
        from src.core.tool_plugins import load_manifest
        path, _ = QFileDialog.getOpenFileName(
            self.parent_window, ui_strings.Menu.LOAD_PLUGIN.replace("&", ""),
            "", ui_strings.Menu.PLUGIN_FILTER)
        if not path:
            return
        try:
            entries = load_manifest(path)
        except (ValueError, OSError):
            QMessageBox.warning(self.parent_window, "Plugin", ui_strings.Menu.PLUGIN_ERROR)
            return
        self._plugin_windows = getattr(self, "_plugin_windows", {})
        for entry in entries:
            action = QAction(entry.display_name, self.parent_window)
            action.setObjectName(f"plugin:{entry.tool_id}")
            action.setStatusTip(entry.display_name)
            action.triggered.connect(lambda checked=False, entry=entry: self._launch_plugin(entry))
            self.parent_window.menu_registry.menus["Tools"].addAction(action)

    def _launch_plugin(self, entry):
        from src.core.tool_lifecycle import resolve_tool_class
        from PyQt5.QtWidgets import QWidget
        window = None
        try:
            existing = self._plugin_windows.get(entry.tool_id)
            if existing is not None:
                if entry.commands and entry.tool_id not in existing.menu_registry._items:
                    from src.core.plugin_contracts import install_contracts
                    install_contracts(existing, existing.centralWidget(), entry)
                existing.show()
                existing.raise_()
                existing.activateWindow()
                return
            cls = resolve_tool_class(entry.module_path, entry.class_name)
            if cls is None:
                raise ValueError("Plugin entry point is unavailable")
            widget = cls()
            if not isinstance(widget, QWidget):
                raise ValueError("Plugin entry point must construct a QWidget")
            window = QMainWindow(self.parent_window)
            window.parent_hub = self.parent_window
            window.tool_id = entry.tool_id
            window.setWindowTitle(entry.display_name)
            window.setMinimumSize(entry.min_window_width, entry.min_window_height)
            window.setCentralWidget(widget)
            window.menu_manager = SimpleMenuManager(window)
            window.menu_manager.create_menubar()
            if entry.undo_supported:
                from src.gui.undo_history import install_undo_history
                install_undo_history(window, getattr(widget, "undo_stack", None), tool_id=entry.tool_id)
            else:
                window.setProperty("undoSupported", entry.undo_supported)
            from src.core.plugin_contracts import install_contracts
            install_contracts(window, widget, entry)
            self._plugin_windows[entry.tool_id] = window
            window.show()
        except Exception:
            if window is not None:
                window.deleteLater()
            QMessageBox.warning(self.parent_window, "Plugin", ui_strings.Menu.PLUGIN_ERROR)

    def register_callback(self, action_name: str, callback: Callable[[], None]) -> None:
        aliases = {"save_as_file": "save_as", "show_preferences": "preferences",
                   "find": "find_action", "replace": "replace_action",
                   "show_options": "options", "show_performance": "performance"}
        action_name = aliases.get(action_name, action_name)
        self.callbacks[action_name] = callback
        if action_name in self._actions:
            self._actions[action_name].setEnabled(True)

    def _add_action(
        self, menu: QMenu, text: str, shortcut: str, callback_name: str
    ) -> QAction:
        action = QAction(text, self.parent_window)
        bind_text(action, "setText", text)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda: self._handle_action(callback_name))
        action.setProperty("toolCommand", callback_name)
        self._actions[callback_name] = action
        action.setEnabled(callback_name in self.callbacks or callback_name in {"about", "user_guide", "shortcuts", "log_viewer"})
        menu.addAction(action)
        return action

    def _handle_action(self, callback_name: str) -> None:
        dispatcher = getattr(self.parent_window, "command_dispatcher", None)
        if dispatcher is not None:
            dispatcher.invoke(callback_name)
            return
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
