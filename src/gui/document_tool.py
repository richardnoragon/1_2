"""Shared worker lifecycle and controls for source-preserving document tools."""
from threading import Event
from contextvars import copy_context
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QSizePolicy
from src.core.operations import operation
from src.core.error_codes import resolve_error
from src.core.workflows import WorkflowCancelled
from src.gui.components import LoadingIndicator, PrimaryButton, SecondaryButton
from src.rfu import font_tokens
from src.rfu.localization import service, tr


class Signals(QObject):
    result = pyqtSignal(object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()


class Job(QRunnable):
    def __init__(self, tool_id, name, work):
        super().__init__()
        self.signals = Signals()
        self.tool_id, self.name, self.work = tool_id, name, work
        self.context = copy_context()

    def run(self):
        self.context.run(self._run)

    def _run(self):
        try:
            with operation(self.tool_id, self.name):
                result = self.work()
            self.signals.result.emit(result)
        except WorkflowCancelled:
            self.signals.failed.emit('DocumentTool.CANCELLED')
        except Exception as exc:
            self.signals.failed.emit(resolve_error(exc).code)
        finally:
            self.signals.finished.emit()


class DocumentToolWindow(QMainWindow):
    def __init__(self, tool_id, title, instructions, parent=None):
        super().__init__(parent)
        font_tokens.bind(self)
        self.tool_id = tool_id
        self._job = None
        self._closing = False
        self.cancel = Event()
        self.controls = []
        service.bind(self, 'setWindowTitle', title)
        service.bind(self, 'setAccessibleName', title)
        self.resize(1100, 800)
        self.body = QWidget(self)
        self.setCentralWidget(self.body)
        self.layout = QVBoxLayout(self.body)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(12)
        label = QLabel()
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        service.bind(label, 'setText', instructions)
        font_tokens.bind(label)
        self.layout.addWidget(label)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        font_tokens.bind(self.status)
        self.loading = LoadingIndicator(self, cancellable=True)
        self.loading.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.loading.cancelled.connect(self.cancel.set)
        self.layout.addWidget(self.loading)
        self.layout.addWidget(self.status)

    def button(self, key, callback, primary=False):
        button = (PrimaryButton if primary else SecondaryButton)(tr(key))
        service.bind(button, 'setText', key)
        service.bind(button, 'setAccessibleName', key)
        button.clicked.connect(callback)
        self.controls.append(button)
        return button

    def run_job(self, name, work, completed):
        if self._job is not None:
            return False
        self._closing = False
        self.cancel.clear()
        for control in self.controls:
            control.setEnabled(False)
        self.status.setText(tr('DocumentTool.BUSY'))
        self.loading.start()
        self._job = Job(self.tool_id, name, work)
        self._job.signals.result.connect(completed)
        self._job.signals.failed.connect(self.failed)
        self._job.signals.finished.connect(self._finished)
        QThreadPool.globalInstance().start(self._job)
        return True

    def failed(self, code):
        self.status.setProperty("errorCode", code)
        self.status.setText(resolve_error(code).message if code.startswith("RFU-") else tr(code))

    def _finished(self):
        self.loading.stop()
        self._job = None
        for control in self.controls:
            control.setEnabled(True)
        self.update_controls()
        if self._closing:
            self.close()

    def update_controls(self):
        pass

    def exported(self, _):
        self.status.setText(tr('DocumentTool.SAVED'))

    def closeEvent(self, event):
        if self._job is not None:
            self._closing = True
            self.cancel.set()
            event.ignore()
        else:
            super().closeEvent(event)
