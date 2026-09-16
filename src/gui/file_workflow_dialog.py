"""Accessible, nonblocking file discovery → checksum → report workflow."""

from threading import Event
from contextvars import copy_context
from pathlib import Path

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout

from src.core.error_codes import resolve_error
from src.core.operations import operation
from src.core.workflows import inspect_files, export_report, WorkflowCancelled
from src.gui.components import LoadingIndicator, PrimaryButton, SecondaryButton
from src.rfu import font_tokens
from src.rfu.localization import service, tr


class _Signals(QObject):
    result = pyqtSignal(object)
    failure = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()


class _Job(QRunnable):
    def __init__(self, work):
        super().__init__()
        self.signals = _Signals()
        self.work = work
        self.context = copy_context()

    def run(self):
        self.context.run(self._run)

    def _run(self):
        try:
            self.signals.result.emit(self.work())
        except Exception as exc:
            self.signals.failure.emit(resolve_error(exc).code)
        finally:
            self.signals.finished.emit()


class FileWorkflowDialog(QDialog):
    undo_supported = False

    def __init__(self, parent=None):
        super().__init__(parent)
        service.bind(self, "setWindowTitle", "Workflow.TITLE")
        self.setAccessibleName(tr("Workflow.TITLE"))
        self.resize(650, 280)
        self.records = []
        self.root = None
        self._job = None
        self._pending_close = False
        self._cancel = Event()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.status = QLabel()
        self.status.setWordWrap(True)
        service.bind(self.status, "setText", "Workflow.INSTRUCTIONS")
        font_tokens.bind(self.status)
        layout.addWidget(self.status)
        self.loading = LoadingIndicator(self, cancellable=True)
        self.loading.cancelled.connect(self._cancel.set)
        layout.addWidget(self.loading)
        row = QHBoxLayout()
        row.addStretch()
        self.export = SecondaryButton(tr("Workflow.EXPORT"))
        self.export.setEnabled(False)
        self.export.clicked.connect(self.export_results)
        self.inspect = PrimaryButton(tr("Workflow.INSPECT"))
        self.inspect.clicked.connect(self.choose_folder)
        self.close_button = SecondaryButton(tr("Workflow.CLOSE"))
        self.close_button.clicked.connect(self.close)
        for button, key in ((self.close_button, "Workflow.CLOSE"), (self.export, "Workflow.EXPORT"), (self.inspect, "Workflow.INSPECT")):
            service.bind(button, "setText", key)
            service.bind(button, "setAccessibleName", key)
            row.addWidget(button)
        layout.addLayout(row)

    def choose_folder(self):
        root = QFileDialog.getExistingDirectory(self, tr("Workflow.CHOOSE"))
        if not root:
            return
        self.root = Path(root).resolve()
        self.records = []
        self._start(lambda: inspect_files(root, cancel=self._cancel,
                    progress=self._job.signals.progress.emit), self._inspected)

    def _start(self, work, completed):
        self._pending_close = False
        self._cancel.clear()
        self.inspect.setEnabled(False)
        self.export.setEnabled(False)
        self.status.setText(tr("Workflow.RUNNING"))
        self.loading.start()
        self._job = _Job(work)
        self._job.signals.result.connect(completed)
        self._job.signals.failure.connect(self._failed)
        self._job.signals.progress.connect(self._progress)
        self._job.signals.finished.connect(self._finished)
        QThreadPool.globalInstance().start(self._job)

    def _progress(self, count):
        self.loading.set_message(tr("Workflow.COUNT").format(count=count))

    def _inspected(self, records):
        self.records = records
        self.status.setText(tr("Workflow.COMPLETE").format(count=len(records)))

    def _failed(self, code):
        self.status.setText(resolve_error(code).message)

    def _finished(self):
        self.loading.stop()
        self._job = None
        self.inspect.setEnabled(True)
        self.export.setEnabled(bool(self.records))
        if self._pending_close:
            self.close()

    def export_results(self):
        destination, _ = QFileDialog.getSaveFileName(self, tr("Workflow.EXPORT"), "checksums.csv", "CSV (*.csv)")
        if not destination:
            return
        if self.root and any((self.root / record.path).resolve() == Path(destination).resolve() for record in self.records):
            self.status.setText(tr("Workflow.INPUT_OVERWRITE"))
            return

        def work():
            with operation("file-inspection", "export-report"):
                export_report(self.records, destination, cancel=self._cancel)
        self._start(work, self._exported)

    def _exported(self, _):
        self.status.setText(tr("Workflow.EXPORTED"))

    def closeEvent(self, event):
        if self._job is not None:
            self._pending_close = True
            self._cancel.set()
            event.ignore()
            return
        super().closeEvent(event)

    def reject(self):
        # Escape follows the same cancellation contract as the close button.
        if self._job is not None:
            self._pending_close = True
            self._cancel.set()
        else:
            super().reject()
