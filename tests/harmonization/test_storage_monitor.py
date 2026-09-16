from pathlib import Path
from types import SimpleNamespace
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog
from src.core.workflows import WorkflowCancelled
from src.tools.system.storage_monitor import model
from src.tools.system.storage_monitor.gui import StorageMonitorWindow


def test_rates_elapsed_time_reset_missing_and_peak():
    rates = model.Rates()
    assert rates.update(10, {'disk': {'read': 100, 'write': 200}})['disk'] is None
    assert rates.update(12, {'disk': {'read': 300, 'write': 600}})['disk'] == (100, 200)
    assert rates.update(13, {'disk': {'read': 350, 'write': 600}})['disk'] == (50, 0)
    assert rates.peaks['disk'] == (100, 200)
    assert rates.update(14, {'disk': {'read': 0, 'write': 0}})['disk'] is None
    rates.update(15, {})
    assert rates.update(16, {'disk': {'read': 900, 'write': 900}})['disk'] is None


def test_discovery_includes_network_and_unavailable_capacity(monkeypatch):
    partitions = [SimpleNamespace(device='/dev/sda1', mountpoint='/', fstype='ext4', opts='rw'),
                  SimpleNamespace(device='//server/share', mountpoint='/share', fstype='cifs', opts='rw'),
                  SimpleNamespace(device='proc', mountpoint='/proc', fstype='proc', opts='rw')]
    monkeypatch.setattr(model.psutil, 'disk_partitions', lambda all: partitions)
    monkeypatch.setattr(model.psutil, 'disk_io_counters', lambda **kwargs: {})
    def unavailable(path):
        raise PermissionError('offline')
    monkeypatch.setattr(model.psutil, 'disk_usage', unavailable)
    result = model.snapshot('/share')
    assert len(result['drives']) == 2
    assert result['drives'][1]['network']
    assert result['usage'] is None and result['error'] == 'PermissionError'


def test_benchmark_preserves_existing_files_and_cleans_up(tmp_path):
    original = tmp_path / 'important.txt'
    original.write_text('preserve')
    result = model.benchmark(tmp_path, size=1024 * 1024)
    assert result['bytes'] == 1024 * 1024
    assert result['read'] > 0 and result['write'] > 0
    assert list(tmp_path.iterdir()) == [original]
    with pytest.raises(WorkflowCancelled):
        model.benchmark(tmp_path, size=1024 * 1024, cancelled=lambda: True)
    assert original.read_text() == 'preserve'
    assert list(tmp_path.iterdir()) == [original]


def test_benchmark_failure_cleans_up(tmp_path, monkeypatch):
    def fail(fd):
        raise OSError('flush failed')
    monkeypatch.setattr(model.os, 'fsync', fail)
    with pytest.raises(OSError, match='flush'):
        model.benchmark(tmp_path, size=1024 * 1024)
    assert not list(tmp_path.iterdir())


def populate(window, path):
    window.drive.blockSignals(True)
    window.drive.addItem(str(path), str(path))
    window.drive.blockSignals(False)
    window._snapshot_path = str(path)
    window.latest = {'time': 1, 'usage': {'total': 1024**3, 'used': 256 * 1024**2,
                     'free': 768 * 1024**2, 'percent': 25, 'writable': True}, 'drives': []}
    window.render()


def test_window_capacity_top_resize_stale_selection_and_unavailability(qapp, tmp_path, monkeypatch):
    window = StorageMonitorWindow()
    monkeypatch.setattr(window, 'poll', lambda: None)
    populate(window, tmp_path)
    assert '1.0 GiB' in window.capacity.text()
    assert window.space.value() == 250
    assert not window.enable_bench.isChecked() and not window.bench_button.isEnabled()
    window.enable_bench.setChecked(True)
    assert window.bench_button.isEnabled()
    window.show()
    window.top.setChecked(True)
    assert window.windowFlags() & Qt.WindowStaysOnTopHint
    window.top.setChecked(False)
    assert not window.windowFlags() & Qt.WindowStaysOnTopHint
    window.resize(1100, 800)
    assert window.width() == 1100
    window.drive.addItem('Other', '/different-drive')
    window.drive.setCurrentIndex(1)
    window.render()
    assert '1.0 GiB' not in window.capacity.text()
    assert not window.bench_button.isEnabled()
    window.drive.setCurrentIndex(0)
    window.mark_unavailable()
    window.enable_bench.setChecked(False)
    window.enable_bench.setChecked(True)
    assert not window.bench_button.isEnabled()
    window.close()
    assert not window.timer.isActive()


def test_benchmark_requires_confirmation_and_worker_results(qapp, tmp_path, monkeypatch):
    import src.tools.system.storage_monitor.gui as gui
    window = StorageMonitorWindow()
    populate(window, tmp_path)
    calls = []
    monkeypatch.setattr(gui, 'benchmark', lambda path, **kwargs: calls.append(path) or {'read': 1234, 'write': 5678})
    window.run_benchmark()
    assert not calls
    window.enable_bench.setChecked(True)
    monkeypatch.setattr(gui.ConfirmationModal, 'exec_', lambda self: QDialog.Rejected)
    window.run_benchmark()
    assert not calls
    monkeypatch.setattr(gui.ConfirmationModal, 'exec_', lambda self: QDialog.Accepted)
    window.run_benchmark()
    for _ in range(200):
        QTest.qWait(10)
        if window.task.job is None:
            break
    assert window.task.job is None
    assert calls == [str(tmp_path)]
    assert 'Benchmark' in window.bench_info.text()
    assert 'not rated maximum' in window.bench_info.text()
    window.close()


def test_timeout_invalidates_stale_data_without_blocking(qapp, tmp_path, monkeypatch):
    window = StorageMonitorWindow()
    populate(window, tmp_path)
    window.enable_bench.setChecked(True)
    killed = []
    monkeypatch.setattr(window.process, 'kill', lambda: killed.append(True))
    window.probe_timeout()
    assert killed
    assert window.latest['usage'] is None
    assert not window.bench_button.isEnabled()
    assert 'Retrying' in window.capacity.text()
    window.close()


def test_real_probe_and_close_lifecycle(qapp):
    from PyQt5.QtCore import QProcess
    window = StorageMonitorWindow()
    window.show()
    for _ in range(300):
        QTest.qWait(10)
        if window.latest:
            break
    assert window.latest is not None
    assert window.drive.count() > 0
    window.close()
    for _ in range(100):
        QTest.qWait(10)
        if window.process.state() == QProcess.NotRunning and not window.isVisible():
            break
    assert window.process.state() == QProcess.NotRunning
    assert not window.timer.isActive() and not window.isVisible()
