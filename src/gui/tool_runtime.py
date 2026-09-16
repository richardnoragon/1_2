"""Tool health, fallbacks, command routing and event-loop budget monitoring."""
from time import monotonic
from weakref import ref
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QAction
from src.core.guardian.component_guardian import get_component_guardian
from src.gui.command_dispatch import CommandDispatcher
from src.gui.components.hub_error_screen import HubErrorScreen
from src.gui.telemetry import emit_telemetry
from src.rfu.localization import service


class UIThreadBudget(QObject):
    exceeded = pyqtSignal(float)

    def __init__(self, window, tool_id, budget_ms=100):
        super().__init__(window)
        self.window, self.tool_id, self.budget_ms = window, tool_id, budget_ms
        self.previous = monotonic()
        self.max_gap_ms = 0.0
        self.was_visible = False
        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.sample)
        self.timer.start()

    def sample(self):
        now = monotonic()
        gap = (now - self.previous) * 1000
        self.previous = now
        visible = self.window.isVisible()
        previous_visible = self.was_visible
        self.was_visible = visible
        if not visible or not previous_visible:
            return
        self.max_gap_ms = max(self.max_gap_ms, gap)
        if gap > self.budget_ms:
            emit_telemetry('ui_performance_metric', tool_id=self.tool_id,
                           metric='ui_thread_gap_ms', value=gap, budget_ms=self.budget_ms)
            self.exceeded.emit(gap)


class ToolRuntime(QObject):
    def __init__(self, window, owner, entry, hub):
        super().__init__(window)
        self.window, self.owner, self.entry, self.hub = window, owner, entry, hub
        self.guardian = get_component_guardian()
        self.guardian_id = self.guardian.register_component(owner, component_type='tool:' + entry.tool_id)
        window.tool_guardian_id = self.guardian_id
        window.command_dispatcher = CommandDispatcher(window, owner, entry.tool_id)
        self.budget = UIThreadBudget(window, entry.tool_id)
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.check_health)
        self.timer.start()
        self.fallback = None
        self.stack = None
        self.return_action = QAction(window)
        service.bind(self.return_action, 'setText', 'Menu.RETURN_TO_HUB')
        # Reuse existing Return to Hub shortcut when the simple manager owns it.
        if not any(a.shortcut().toString() == 'Ctrl+H' for a in window.findChildren(QAction)):
            self.return_action.setShortcut('Ctrl+H')
            self.return_action.triggered.connect(self.return_to_hub)
            window.menu_registry.menus['File'].addAction(self.return_action)
        manager = getattr(hub, 'menu_manager', None)
        if manager is not None and hasattr(manager, '_tool_windows'):
            manager._tool_windows[id(window)] = window
        self.check_health()

    def return_to_hub(self):
        self.hub.show()
        self.hub.raise_()
        self.hub.activateWindow()

    def check_health(self):
        check = getattr(self.owner, 'health_check', None)
        try:
            healthy = bool(check()) if callable(check) else (self.owner.centralWidget() is not None
                if isinstance(self.owner, QMainWindow) else self.owner.layout() is not None)
        except Exception:
            healthy = False
        if not healthy and not self.window.property('toolDegraded'):
            self.degrade()
        return healthy

    def degrade(self):
        self.guardian.report_degradation(self.guardian_id, 'tool_health_check')
        fallback = getattr(self.owner, 'degraded_fallback', None)
        if callable(fallback):
            try:
                fallback()
            except Exception:
                pass
        if self.stack is not None:
            self.stack.widget(0).setEnabled(False)
            self.stack.setCurrentWidget(self.fallback)
            self.window.setProperty('toolDegraded', True)
            self.window.command_dispatcher.refresh()
            return
        self.stack = QStackedWidget(self.window)
        body = self.window.takeCentralWidget()
        if body is not None:
            self.stack.addWidget(body)
            body.setEnabled(False)
        self.fallback = HubErrorScreen(self.entry.display_name, 'RFU-UNAVAILABLE', self.stack)
        self.fallback.retry_requested.connect(self.retry)
        self.fallback.go_home_requested.connect(self.return_to_hub)
        self.stack.addWidget(self.fallback)
        self.window.setCentralWidget(self.stack)
        self.stack.setCurrentWidget(self.fallback)
        self.window.setProperty('toolDegraded', True)
        self.window.command_dispatcher.refresh()

    def retry(self):
        check = getattr(self.owner, 'health_check', None)
        if not callable(check):
            return
        try:
            healthy = bool(check())
        except Exception:
            healthy = False
        if healthy and self.stack.count() > 1:
            body = self.stack.widget(0)
            body.setEnabled(True)
            self.stack.setCurrentWidget(body)
            self.window.setProperty('toolDegraded', False)
            # Recovery is based on the tool's check, never merely a live QWidget.
            self.guardian.confirm_recovery(self.guardian_id)
            self.window.command_dispatcher.refresh()
