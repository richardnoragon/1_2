"""Shared nonblocking task lifecycle for legacy windows."""
from threading import Event
from PyQt5.QtCore import QObject, QThreadPool, QEvent
from src.gui.document_tool import Job
from src.gui.components import LoadingIndicator
from src.core.error_codes import resolve_error


class BackgroundTask(QObject):
    def __init__(self, window, tool_id, layout, controls):
        super().__init__(window)
        self.window, self.tool_id, self.controls = window, tool_id, controls
        self.cancel = Event()
        self.cancel_callback = lambda: None
        self.job = None
        self.pending_close = False
        self.loading = LoadingIndicator(window, cancellable=True)
        self.loading.cancelled.connect(self.request_cancel)
        layout.addWidget(self.loading)
        window.installEventFilter(self)

    def request_cancel(self):
        self.cancel.set()
        self.cancel_callback()

    def start(self, name, work, completed):
        if self.job is not None:
            return False
        self.pending_close = False
        self.cancel.clear()
        self._enabled = [control.isEnabled() for control in self.controls]
        for control in self.controls:
            control.setEnabled(False)
        self.loading.start()
        self.job = self.window._job = Job(self.tool_id, name, work)
        self._completed = completed
        self._has_result = False
        self.job.signals.result.connect(self.result)
        self.job.signals.failed.connect(self.failed)
        self.job.signals.finished.connect(self.finished)
        QThreadPool.globalInstance().start(self.job)
        return True

    def result(self, value):
        self._result = value
        self._has_result = True

    def failed(self, code):
        from src.rfu.localization import tr
        message = tr('DocumentTool.CANCELLED') if code == 'DocumentTool.CANCELLED' else resolve_error(code).message
        self.window.statusBar().showMessage(message, 10000)

    def finished(self):
        self.loading.stop()
        self.job = self.window._job = None
        for control, enabled in zip(self.controls, self._enabled):
            control.setEnabled(enabled)
        dispatcher = getattr(self.window, 'command_dispatcher', None)
        if dispatcher:
            dispatcher.refresh()
        if self.pending_close:
            self.window.close()
        elif self._has_result:
            self._completed(self._result)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Close and self.job is not None:
            self.pending_close = True
            self.request_cancel()
            event.ignore()
            return True
        return False
