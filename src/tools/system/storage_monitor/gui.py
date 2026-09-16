"""Independent, resizable storage capacity and activity window."""
from collections import deque
import json
import os
from pathlib import Path
import sys

from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QCheckBox, QProgressBar, QInputDialog, QDialog, QScrollArea, QLayout, QSizePolicy, QApplication)
from src.gui.components import SecondaryButton, ConfirmationModal
from src.gui.background_task import BackgroundTask
from src.rfu import font_tokens
from src.rfu.localization import service, tr
from .model import Rates, benchmark


def size_text(value, rate=False):
    suffix = '/s' if rate else ''
    if value is None:
        return tr('StorageMonitor.UNKNOWN')
    value = float(value)
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'):
        if abs(value) < 1024 or unit == 'PiB':
            return f'{value:,.1f} {unit}{suffix}'
        value /= 1024


class ActivityGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.samples = deque(maxlen=60)
        self.setFixedHeight(110)
        service.bind(self, 'setAccessibleName', 'StorageMonitor.GRAPH')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.palette().base())
        ceiling = max((max(pair) for pair in self.samples), default=1) or 1
        for component, color in ((0, '#2563eb'), (1, '#c75b00')):
            painter.setPen(QColor(color))
            path = QPainterPath()
            for index, pair in enumerate(self.samples):
                x = 5 + index * max(1, self.width() - 10) / 59
                y = self.height() - 5 - pair[component] / ceiling * (self.height() - 10)
                if index:
                    path.lineTo(x, y)
                else:
                    path.moveTo(x, y)
            painter.drawPath(path)


class StorageMonitorWindow(QMainWindow):
    def __init__(self, hub_instance=None):
        super().__init__()
        self.parent_hub = hub_instance
        service.bind(self, 'setWindowTitle', 'StorageMonitor.TITLE')
        font_tokens.bind(self)
        self.resize(960, 800)
        self.setMinimumSize(600, 480)
        self.rates = Rates()
        self.latest = None
        self.current_rates = {}
        self.custom_paths = []
        self._last_graph_time = None
        self._probe_path = None
        self._snapshot_path = None
        self._closing = False
        self._benchmark_result = None
        body = QWidget(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        self.setCentralWidget(scroll)
        layout = QVBoxLayout(body)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        self.drive = QComboBox()
        service.bind(self.drive, 'setAccessibleName', 'StorageMonitor.DRIVE')
        self.drive.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        layout.addWidget(self.label('StorageMonitor.DRIVE'))
        row = QHBoxLayout()
        row.addWidget(self.drive, 1)
        add = self.button('StorageMonitor.ADD', self.add_path)
        refresh = self.button('StorageMonitor.REFRESH', self.poll)
        row.addWidget(add)
        row.addWidget(refresh)
        layout.addLayout(row)
        self.top = QCheckBox()
        service.bind(self.top, 'setText', 'StorageMonitor.TOP')
        self.top.toggled.connect(self.set_on_top)
        layout.addWidget(self.top)
        self.capacity = QLabel()
        self.capacity.setWordWrap(True)
        layout.addWidget(self.capacity)
        self.space = QProgressBar()
        service.bind(self.space, 'setAccessibleName', 'StorageMonitor.SPACE')
        service.bind(self.space, 'setToolTip', 'StorageMonitor.RESERVED')
        self.space.setRange(0, 1000)
        layout.addWidget(self.space)
        layout.addWidget(self.label('StorageMonitor.SOURCE'))
        self.source = QComboBox()
        service.bind(self.source, 'setAccessibleName', 'StorageMonitor.SOURCE')
        self.source.addItem(tr('StorageMonitor.UNAVAILABLE'), None)
        layout.addWidget(self.source)
        self.read = QLabel()
        self.write = QLabel()
        self.info = QLabel()
        for label in (self.read, self.write, self.info):
            label.setWordWrap(True)
            layout.addWidget(label)
        self.graph = ActivityGraph()
        layout.addWidget(self.graph, 1)
        layout.addWidget(self.label('StorageMonitor.GRAPH'))
        self.enable_bench = QCheckBox()
        service.bind(self.enable_bench, 'setText', 'StorageMonitor.ENABLE_BENCH')
        layout.addWidget(self.enable_bench)
        self.bench_button = self.button('StorageMonitor.BENCH', self.run_benchmark)
        self.bench_button.setEnabled(False)
        layout.addWidget(self.bench_button)
        self.bench_info = self.label('StorageMonitor.BENCH_HELP')
        layout.addWidget(self.bench_info)
        self.task = BackgroundTask(self, 'storage-monitor', layout,
                                   [self.drive, add, refresh, self.enable_bench, self.bench_button])
        self.enable_bench.toggled.connect(self.update_benchmark)
        self.drive.currentIndexChanged.connect(self.drive_changed)
        self.source.currentIndexChanged.connect(self.source_changed)
        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(Path(__file__).resolve().parents[4]))
        self.process.finished.connect(self.probe_finished)
        self.process.errorOccurred.connect(self.probe_error)
        QApplication.instance().aboutToQuit.connect(self.stop_probe)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.probe_timeout)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.poll)
        service.subscribe(self, 'render')
        self.render()
        for label in body.findChildren(QLabel):
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        # Polling starts only when visible, including when a closed window reopens.

    def label(self, key):
        label = QLabel()
        label.setWordWrap(True)
        service.bind(label, 'setText', key)
        font_tokens.bind(label)
        return label

    def button(self, key, callback):
        button = SecondaryButton(tr(key))
        service.bind(button, 'setText', key)
        service.bind(button, 'setAccessibleName', key)
        button.clicked.connect(callback)
        return button

    def set_on_top(self, enabled):
        geometry = self.geometry()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()
        self.setGeometry(geometry)

    def add_path(self):
        path, accepted = QInputDialog.getText(self, tr('StorageMonitor.ADD'), tr('StorageMonitor.PATH'))
        if accepted and path.strip():
            path = os.path.abspath(os.path.expanduser(path.strip()))
            if path not in self.custom_paths:
                self.custom_paths.append(path)
                self.drive.addItem(path, path)
            self.drive.setCurrentIndex(self.drive.findData(path))

    def drive_changed(self):
        self._benchmark_result = None
        self.bench_info.setText(tr('StorageMonitor.BENCH_HELP'))
        self.capacity.setText(tr('StorageMonitor.WAITING'))
        self.space.setValue(0)
        self.update_benchmark()
        self.select_matching_source()
        self.poll()

    def select_matching_source(self):
        path = self.drive.currentData()
        entry = next((d for d in (self.latest or {}).get('drives', []) if d['path'] == path), None)
        # Match exact OS identifiers only. Never guess that a network share is a local disk.
        device = os.path.basename(os.path.realpath(entry['device'])) if entry and not entry['network'] and sys.platform.startswith('linux') else None
        index = self.source.findData(device) if device else 0
        self.source.setCurrentIndex(max(0, index))
        self.source_changed()

    def source_changed(self):
        self.graph.samples.clear()
        self.graph.update()
        self._last_graph_time = None
        self.render()

    def poll(self):
        if self._closing or not self.isVisible() or self.task.job is not None or self.process.state() != QProcess.NotRunning:
            return
        self._probe_path = self.drive.currentData()
        self.process.start(sys.executable, ['-m', 'src.tools.system.storage_monitor.probe', self._probe_path or ''])
        self.deadline.start(5000)

    def probe_timeout(self):
        self.process.kill()
        self.mark_unavailable()

    def probe_error(self, error):
        if error == QProcess.FailedToStart:
            self.deadline.stop()
            self.mark_unavailable()

    def mark_unavailable(self):
        self.capacity.setText(tr('StorageMonitor.FAILED'))
        self.statusBar().showMessage(tr('StorageMonitor.FAILED'))
        self.space.setValue(0)
        self.current_rates = {}
        if self.latest:
            self.latest['usage'] = None
        self.rates.previous.clear()
        self.read.setText(tr('StorageMonitor.UNKNOWN'))
        self.write.setText(tr('StorageMonitor.UNKNOWN'))
        self.bench_button.setEnabled(False)

    def probe_finished(self, code, status):
        self.deadline.stop()
        if self._closing:
            QTimer.singleShot(0, self.close)
            return
        try:
            if code != 0 or status != QProcess.NormalExit:
                raise ValueError('Probe failed')
            data = json.loads(bytes(self.process.readAllStandardOutput()))
            if 'drives' not in data:
                raise ValueError('No snapshot')
        except (ValueError, TypeError):
            self.mark_unavailable()
            return
        self.latest = data
        self._snapshot_path = self._probe_path
        self.current_rates = self.rates.update(data['time'], data['counters'])
        selected = self.drive.currentData()
        paths = [(d['path'] + ' — ' + d['device'], d['path']) for d in data['drives']]
        paths += [(p, p) for p in self.custom_paths if p not in {d['path'] for d in data['drives']}]
        if selected and selected not in {p for _, p in paths}:
            paths.append((selected, selected))  # Retain disconnected selection and report unavailable.
        self.drive.blockSignals(True)
        self.drive.clear()
        for label, path in paths:
            self.drive.addItem(label, path)
        self.drive.setCurrentIndex(max(0, self.drive.findData(selected)))
        self.drive.blockSignals(False)
        old_source = self.source.currentData()
        self.source.blockSignals(True)
        self.source.clear()
        self.source.addItem(tr('StorageMonitor.UNAVAILABLE'), None)
        for device in sorted(data['counters']):
            self.source.addItem(device, device)
        self.source.setCurrentIndex(max(0, self.source.findData(old_source)))
        self.source.blockSignals(False)
        if selected is None:
            self.select_matching_source()
            QTimer.singleShot(0, self.poll)
        self.render()

    def render(self):
        data = self.latest or {}
        usage = data.get('usage') if self.drive.currentData() == self._snapshot_path else None
        if usage:
            self.capacity.setText(tr('StorageMonitor.CAPACITY').format(**{k: size_text(usage[k]) for k in ('total', 'used', 'free')}))
            percent = 100 * usage['used'] / usage['total'] if usage['total'] else 0
            self.space.setValue(round(percent * 10))
            self.space.setFormat(f'{percent:.1f}%')
        elif self.latest:
            self.capacity.setText(tr('StorageMonitor.FAILED'))
            self.space.setValue(0)
        else:
            self.capacity.setText(tr('StorageMonitor.WAITING'))
        device = self.source.currentData()
        rate = self.current_rates.get(device)
        peaks = self.rates.peaks.get(device, (None, None))
        for index, label, key in ((0, self.read, 'StorageMonitor.READING'), (1, self.write, 'StorageMonitor.WRITING')):
            label.setText(tr(key).format(rate=size_text(rate[index] if rate else None, True), peak=size_text(peaks[index], True)))
        self.info.setText(tr('StorageMonitor.READY').format(device=device) if device else tr('StorageMonitor.NETWORK'))
        if rate is not None:
            self.statusBar().showMessage(tr('StorageMonitor.STATE').format(state=tr('StorageMonitor.ACTIVE' if any(rate) else 'StorageMonitor.IDLE')))
            if data.get('time') != self._last_graph_time:
                self.graph.samples.append(rate)
                self.graph.update()
                self._last_graph_time = data.get('time')
        else:
            self.statusBar().showMessage(tr('StorageMonitor.WAITING') if device else tr('StorageMonitor.UNAVAILABLE'))
        if self._benchmark_result:
            self.bench_info.setText(tr('StorageMonitor.BENCH_RESULT').format(**{k: size_text(self._benchmark_result[k], True) for k in ('read', 'write')}))
        self.update_benchmark()

    def update_benchmark(self):
        usage = (self.latest or {}).get('usage') if self.drive.currentData() == self._snapshot_path else None
        self.bench_button.setEnabled(self.enable_bench.isChecked() and self.task.job is None and bool(usage) and usage.get('writable', False) and usage['free'] >= 192 * 1024 * 1024)

    def run_benchmark(self):
        if not self.bench_button.isEnabled():
            return
        path = self.drive.currentData()
        if ConfirmationModal(tr('StorageMonitor.BENCH_TITLE'), tr('StorageMonitor.BENCH_CONFIRM').format(path=path), parent=self).exec_() != QDialog.Accepted:
            return
        self._benchmark_result = None
        self.bench_info.setText(tr('StorageMonitor.BENCH_HELP'))
        self.rates.previous.clear()
        self.task.start('benchmark', lambda: benchmark(path, cancelled=self.task.cancel.is_set), self.benchmark_finished)

    def benchmark_finished(self, result):
        self._benchmark_result = result
        self.render()

    def showEvent(self, event):
        super().showEvent(event)
        self._closing = False
        self.timer.start()
        QTimer.singleShot(0, self.poll)

    def closeEvent(self, event):
        if self.task.job is not None:
            self.task.pending_close = True
            self.task.request_cancel()
            event.ignore()
            return
        self._closing = True
        self.timer.stop()
        self.deadline.stop()
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            event.ignore()
            return
        super().closeEvent(event)

    def stop_probe(self):
        """Reap the read-only child on application shutdown with a bounded wait."""
        self.timer.stop()
        self.deadline.stop()
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.process.waitForFinished(100)

    def health_check(self):
        return self.centralWidget() is not None
