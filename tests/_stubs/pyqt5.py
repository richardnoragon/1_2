"""Lightweight PyQt5 stubs used when real bindings are unavailable."""
from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Callable, List, Optional


@dataclass
class _PseudoEventLoop:
    is_running: bool = False

    def process_events(self) -> None:  # pragma: no cover - noop placeholder
        return None


class QObject:  # pragma: no cover - stub
    def __init__(self, *args, **kwargs) -> None:
        pass


class _Signal:  # pragma: no cover - simple signal stub
    def __init__(self) -> None:
        self._subscribers: List[Callable[..., None]] = []

    def connect(self, callback: Callable[..., None]) -> None:
        self._subscribers.append(callback)

    def emit(self, *args, **kwargs) -> None:
        for subscriber in list(self._subscribers):
            subscriber(*args, **kwargs)


def pyqtSignal(*_args, **_kwargs) -> _Signal:  # pragma: no cover
    return _Signal()


class QApplication:  # pragma: no cover - behavior verified indirectly
    _instance: Optional["QApplication"] = None

    def __init__(self, args: Optional[List[str]] = None) -> None:
        QApplication._instance = self
        self._args = args or []
        self._loop = _PseudoEventLoop()

    @classmethod
    def instance(cls) -> Optional["QApplication"]:
        return cls._instance

    def exec_(self) -> int:
        self._loop.is_running = True
        return 0

    def quit(self) -> None:
        self._loop.is_running = False

    def processEvents(self) -> None:
        self._loop.process_events()


class QMessageBox:  # pragma: no cover - minimal dialog stub
    Critical = 3
    Warning = 2
    Information = 1

    def __init__(self) -> None:
        self.icon = None
        self.title = ""
        self.text = ""
        self.detailed_text = ""

    def setIcon(self, icon: int) -> None:
        self.icon = icon

    def setWindowTitle(self, title: str) -> None:
        self.title = title

    def setText(self, text: str) -> None:
        self.text = text

    def setDetailedText(self, text: str) -> None:
        self.detailed_text = text

    def exec_(self) -> int:
        return 0


def install_pyqt5_stubs() -> None:
    """Register stub modules under ``PyQt5`` in ``sys.modules``."""

    import sys

    if "PyQt5" in sys.modules:  # pragma: no cover - real bindings present
        return

    pyqt5_pkg = ModuleType("PyQt5")

    qtwidgets = ModuleType("PyQt5.QtWidgets")
    qtwidgets.QApplication = QApplication
    qtwidgets.QMessageBox = QMessageBox

    qtcore = ModuleType("PyQt5.QtCore")
    qtcore.QObject = QObject
    qtcore.pyqtSignal = pyqtSignal

    pyqt5_pkg.QtWidgets = qtwidgets
    pyqt5_pkg.QtCore = qtcore

    sys.modules["PyQt5"] = pyqt5_pkg
    sys.modules["PyQt5.QtWidgets"] = qtwidgets
    sys.modules["PyQt5.QtCore"] = qtcore
