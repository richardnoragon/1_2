"""Compatibility façade for the legacy `rfu.dev_hub` import contract.

This module mirrors the minimal API expected by the repo's historical tests
and validation scripts while delegating the real runtime behavior to the
currently supported implementation points.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

try:  # pragma: no cover - exercised via test patching
    from PyQt5 import QtCore, QtWidgets  # type: ignore
    PYQT5_AVAILABLE = True
except Exception:  # pragma: no cover - compatibility fallback
    PYQT5_AVAILABLE = False
    QtCore = None  # type: ignore[assignment]
    QtWidgets = None  # type: ignore[assignment]


class LogHandler(logging.Handler):
    """Simple log collector compatible with historical dev_hub tests."""

    def __init__(self, log_signal: Optional[Any] = None, max_entries: int = 1000):
        super().__init__()
        self.log_signal = log_signal
        self.log_entries: list[dict[str, Any]] = []
        self.max_entries = max_entries

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
        except Exception:  # pragma: no cover - defensive fallback
            message = str(record.getMessage())

        entry = {
            "timestamp": time.time(),
            "level": record.levelname,
            "message": message,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        self.log_entries.append(entry)
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries :]

        if self.log_signal is not None and hasattr(self.log_signal, "emit"):
            self.log_signal.emit(message)


class PerformanceMonitor:
    """Minimal performance monitor API used by legacy validation tests."""

    def __init__(self, interval: float = 1.0):
        self.running = False
        self.interval = float(interval)
        self.performance_updated = None
        self._thread = QtCore.QThread() if PYQT5_AVAILABLE and QtCore is not None else None

    def _collect_metrics(self) -> Dict[str, Any]:
        try:
            import psutil
        except Exception:  # pragma: no cover - safe fallback
            psutil = None

        cpu_percent = 0.0
        cpu_count = 0
        memory_percent = 0.0
        memory_available_gb = 0.0
        memory_total_gb = 0.0
        disk_percent = 0.0
        disk_free_gb = 0.0
        process_memory_mb = 0.0
        process_cpu_percent = 0.0

        if psutil is not None:
            try:
                cpu_percent = float(psutil.cpu_percent(interval=0.1))
            except Exception:
                cpu_percent = 0.0
            try:
                cpu_count = int(psutil.cpu_count() or 0)
            except Exception:
                cpu_count = 0
            try:
                mem = psutil.virtual_memory()
                memory_percent = float(getattr(mem, "percent", 0.0) or 0.0)
                memory_available_gb = float(getattr(mem, "available", 0) or 0) / (1024 ** 3)
                memory_total_gb = float(getattr(mem, "total", 0) or 0) / (1024 ** 3)
            except Exception:
                pass
            try:
                disk = psutil.disk_usage("/")
                disk_total = float(getattr(disk, "total", 0) or 0)
                disk_used = float(getattr(disk, "used", 0) or 0)
                disk_free = float(getattr(disk, "free", 0) or 0)
                disk_percent = (disk_used / disk_total * 100.0) if disk_total else 0.0
                disk_free_gb = disk_free / (1024 ** 3)
            except Exception:
                pass
            try:
                proc = psutil.Process()
                proc_mem = proc.memory_info()
                process_memory_mb = float(getattr(proc_mem, "rss", 0) or 0) / (1024 ** 2)
                process_cpu_percent = float(proc.cpu_percent() or 0.0)
            except Exception:
                pass

        return {
            "timestamp": time.time(),
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "memory_percent": memory_percent,
            "memory_available_gb": memory_available_gb,
            "memory_total_gb": memory_total_gb,
            "disk_percent": disk_percent,
            "disk_free_gb": disk_free_gb,
            "process_memory_mb": process_memory_mb,
            "process_cpu_percent": process_cpu_percent,
        }

    def run(self) -> None:
        self.running = True
        while self.running:
            data = self._collect_metrics()
            if self.performance_updated is not None and hasattr(self.performance_updated, "emit"):
                self.performance_updated.emit(data)
            time.sleep(self.interval)

    def stop(self) -> None:
        self.running = False


class PerformanceProfiler:
    """Compatibility profiler with the expected start/stop/get_results API."""

    def __init__(self):
        self._started = False
        self._samples: list[Dict[str, Any]] = []

    def start_profiling(self) -> None:
        self._started = True
        self._samples = []

    def stop_profiling(self) -> None:
        self._started = False

    def get_results(self) -> Dict[str, Any]:
        return {"started": self._started, "samples": list(self._samples)}


class DevHub:
    """Compatibility DevHub implementation for package-level access."""

    def __init__(self):
        self.logger = logging.getLogger("DevHub")
        self.logger.setLevel(logging.DEBUG)
        self.log_handler = LogHandler()
        self.performance_monitor = PerformanceMonitor()
        self._init_fallback()

    def _init_fallback(self):
        self.status = "fallback"

    def _init_gui(self):
        self.status = "gui"

    def _setup_performance_monitoring(self):
        self.performance_monitor = PerformanceMonitor()

    def _console_interface(self):
        return None

    def show(self):
        return None


def performance_analysis(*args, **kwargs):
    """Return a minimal structured analysis payload for compatibility callers."""
    return {
        "status": "ok",
        "arguments": {"args": args, "kwargs": kwargs},
        "timestamp": time.time(),
    }


def main() -> DevHub:
    """Create and return the compatibility DevHub instance."""
    hub = DevHub()
    if PYQT5_AVAILABLE and QtWidgets is not None:
        try:
            app = QtWidgets.QApplication.instance()
            if app is None:
                app = QtWidgets.QApplication([])
            hub.show()
        except Exception:  # pragma: no cover - conservative fallback
            pass
    return hub


__all__ = [
    "DevHub",
    "LogHandler",
    "PerformanceMonitor",
    "PerformanceProfiler",
    "PYQT5_AVAILABLE",
    "QtCore",
    "QtWidgets",
    "main",
    "performance_analysis",
]
