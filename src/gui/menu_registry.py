"""Shared menu ownership, validation, lifetime and telemetry for tool windows."""

from __future__ import annotations

import re

from PyQt5.QtCore import QObject, QEvent, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction

from src.gui.telemetry import emit_telemetry
from src.rfu import ui_strings
from src.rfu.localization import service, tr
from src.rfu import font_tokens


class MenuRegistry(QObject):
    """Own tool contributions without replacing existing global actions.

    One registry belongs to one window; tool actions disappear on accepted close.
    Shortcuts are unique within that window, including existing global actions.
    """

    ORDER = ("File", "Edit", "View", "Tools", "Reports", "Window", "Help")
    ALLOWED = frozenset({"View", "Tools", "Reports"})

    def __init__(self, window, *, warning_handler=None):
        super().__init__(window)
        self.window = window
        self.warning_handler = warning_handler
        self.menus = {}
        self._items = {}
        self._conditions = {}
        self._fallbacks = {}
        bar = window.menuBar()
        font_tokens.bind(bar)
        for action in list(bar.actions()):
            name = next((key for key in self.ORDER if action.text() == tr(f"Menu.{key.upper()}")), action.text().replace("&", ""))
            if name in self.ORDER and action.menu() is not None:
                self.menus[name] = action.menu()
                bar.removeAction(action)
        for name in self.ORDER:
            menu = self.menus.get(name)
            if menu is None:
                menu = bar.addMenu(getattr(ui_strings.Menu, name.upper()))
                self.menus[name] = menu
            else:
                bar.addAction(menu.menuAction())
            service.bind(menu, "setTitle", f"Menu.{name.upper()}")
            font_tokens.bind(menu)
            menu.aboutToShow.connect(self.refresh)
        self.refresh()
        window.installEventFilter(self)
        from src.core.guardian.component_guardian import get_component_guardian
        self.guardian = get_component_guardian()
        self.guardian_id = self.guardian.register_component(window, component_type="menu-window")

    def register(self, *, tool_id, menu, label, accelerator, callback,
                 enabled_condition=lambda: True, visible_condition=lambda: True):
        """Register a tool action, rejecting conflicts before mutating menus.

        ``label`` is a dotted ui_strings token, e.g. ``Menu.LOAD_PLUGIN``.
        ``accelerator`` is a QKeySequence string; mnemonics are in the label.
        """
        try:
            if not isinstance(tool_id, str) or not tool_id.strip():
                raise ValueError("A tool ID is required")
            if menu not in self.ALLOWED:
                raise ValueError("Tools may contribute only to View, Tools or Reports")
            owner, attribute = label.split(".")
            text = tr(label)
            if not isinstance(text, str) or "&" not in text.replace("&&", ""):
                raise ValueError("Menu label must provide a mnemonic")
            sequence = QKeySequence(accelerator)
            if sequence.isEmpty():
                raise ValueError("A valid accelerator is required")
            for action in self.window.findChildren(QAction):
                if not action.shortcut().isEmpty() and action.shortcut() == sequence:
                    raise ValueError(f"Accelerator is already assigned: {accelerator}")
            mnemonic = re.search(r"&(.)", text.replace("&&", "")).group(1).casefold()
            for action in self.menus[menu].actions():
                existing = re.search(r"&(.)", action.text().replace("&&", ""))
                if existing and existing.group(1).casefold() == mnemonic:
                    raise ValueError(f"Menu mnemonic is already assigned: {mnemonic}")
            if not all(callable(value) for value in (callback, enabled_condition, visible_condition)):
                raise ValueError("Action and conditions must be callable")
        except (ValueError, AttributeError, TypeError, KeyError) as exc:
            self._warn(tool_id, str(exc))
            raise ValueError(str(exc)) from exc

        action = QAction(text, self.window)
        service.bind(action, "setText", label)
        action.setObjectName(f"{tool_id}:{label}")
        action.setShortcut(sequence)
        action.setToolTip(text.replace("&", ""))
        action.setStatusTip(action.toolTip())
        action.setProperty("accessibleName", action.toolTip())
        action.setProperty("accessibleDescription", action.toolTip())

        def activate():
            self.refresh()
            if action.isEnabled() and action.isVisible():
                self._emit(tool_id, "menu_activate", label=label)
                try:
                    callback()
                except Exception as exc:
                    from src.core.error_codes import resolve_error
                    self._warn(tool_id, resolve_error(exc).message)

        action.triggered.connect(activate)
        target = self.menus[menu]
        existing = target.actions()
        target.insertAction(existing[0] if existing else None, action)
        self._items.setdefault(tool_id, []).append((target, action))
        self._conditions[action] = (enabled_condition, visible_condition, tool_id)
        self.refresh()
        self._emit(tool_id, "menu_register", label=label)
        return action

    def deregister(self, *, tool_id):
        for menu, action in self._items.pop(tool_id, []):
            menu.removeAction(action)
            action.setShortcut("")
            self._conditions.pop(action, None)
            action.deleteLater()
        self.refresh()
        self._emit(tool_id, "menu_deregister")

    def refresh(self):
        for action, (enabled, visible, tool_id) in list(self._conditions.items()):
            try:
                is_visible = bool(visible())
                action.setEnabled(bool(enabled()))
            except Exception:
                is_visible = False
                action.setEnabled(False)
                self._warn(tool_id, "Menu availability could not be evaluated")
            if action.isVisible() != is_visible:
                self._emit(tool_id, "menu_visibility", visible=is_visible)
            action.setVisible(is_visible)
        reports = self.menus["Reports"]
        reports.menuAction().setVisible(any(a.isVisible() and not a.isSeparator() for a in reports.actions()))

    def eventFilter(self, watched, event):
        # Qt can deliver destruction events after Python clears a cyclic wrapper.
        if watched is getattr(self, "window", None) and event.type() == QEvent.Close:
            # A tool may reject close (unsaved data); inspect acceptance afterward.
            QTimer.singleShot(0, self._cleanup_closed)
        return False

    def _cleanup_closed(self):
        try:
            if self.window.isVisible():
                return
        except RuntimeError:
            return
        for tool_id in list(self._items):
            self.deregister(tool_id=tool_id)

    def _warn(self, tool_id, message):
        self.window.setProperty("menuDegraded", True)
        if tool_id not in self._fallbacks:
            action = QAction(tr("Menu.UNAVAILABLE"), self.window)
            action.setEnabled(False)
            self.menus["Tools"].addAction(action)
            self._fallbacks[tool_id] = action
        self._fallbacks[tool_id].setStatusTip(message)
        self._fallbacks[tool_id].setToolTip(message)
        self.window.statusBar().showMessage(message, 8000)
        self.guardian.report_degradation(self.guardian_id, "menu_registration")
        self._emit(tool_id or "unknown", "menu_registration_failed", message=message)
        if self.warning_handler:
            self.warning_handler(tool_id, message)

    @staticmethod
    def _emit(tool_id, action, **metadata):
        emit_telemetry("ui_user_action", tool_id=tool_id, action=action, **metadata)
