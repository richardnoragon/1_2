"""
PyQt5 Mock Components for Network Module Testing

This module provides mock implementations for PyQt5 components
to enable testing of network modules without full GUI dependencies.
"""

import sys
from abc import ABC, ABCMeta
from typing import Any
from unittest.mock import MagicMock, Mock


class MockQObjectMeta(ABCMeta):
    """Compatible metaclass that works with both QObject and ABC."""

    pass


class MockQObject(metaclass=MockQObjectMeta):
    """Mock QObject that's compatible with ABC inheritance."""

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self._signals = {}

    def connect(self, signal, slot):
        """Mock signal connection."""
        pass

    def disconnect(self, signal=None, slot=None):
        """Mock signal disconnection."""
        pass

    def emit(self, *args, **kwargs):
        """Mock signal emission."""
        pass


class MockQThread(MockQObject):
    """Mock QThread for threading operations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

    def start(self):
        """Mock thread start."""
        self._running = True

    def terminate(self):
        """Mock thread termination."""
        self._running = False

    def wait(self, timeout=None):
        """Mock thread wait."""
        self._running = False
        return True

    def isRunning(self):
        """Mock running status."""
        return self._running


class MockQMutex:
    """Mock QMutex for thread synchronization."""

    def __init__(self):
        self._locked = False

    def lock(self):
        """Mock mutex lock."""
        self._locked = True

    def unlock(self):
        """Mock mutex unlock."""
        self._locked = False

    def tryLock(self, timeout=None):
        """Mock mutex try lock."""
        return True


class MockQMutexLocker:
    """Mock QMutexLocker for RAII-style mutex locking."""

    def __init__(self, mutex):
        self.mutex = mutex
        if mutex:
            mutex.lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mutex:
            self.mutex.unlock()


def mock_pyqt_signal(*args, **kwargs):
    """Mock pyqtSignal decorator/function."""

    def signal_decorator(func=None):
        if func is None:
            # Return a mock signal object
            signal = Mock()
            signal.emit = Mock()
            signal.connect = Mock()
            signal.disconnect = Mock()
            return signal
        else:
            # Return the original function with signal attributes
            func.emit = Mock()
            func.connect = Mock()
            func.disconnect = Mock()
            return func

    return signal_decorator


def setup_pyqt5_mocks():
    """Setup PyQt5 mocks in sys.modules."""

    # Create mock PyQt5 modules
    mock_qtcore = Mock()
    mock_qtcore.QObject = MockQObject
    mock_qtcore.QThread = MockQThread
    mock_qtcore.QMutex = MockQMutex
    mock_qtcore.QMutexLocker = MockQMutexLocker
    mock_qtcore.pyqtSignal = mock_pyqt_signal

    mock_qtwidgets = Mock()
    mock_qtwidgets.QApplication = Mock()
    mock_qtwidgets.QWidget = Mock()

    mock_pyqt5 = Mock()
    mock_pyqt5.QtCore = mock_qtcore
    mock_pyqt5.QtWidgets = mock_qtwidgets

    # Install mocks in sys.modules
    sys.modules["PyQt5"] = mock_pyqt5
    sys.modules["PyQt5.QtCore"] = mock_qtcore
    sys.modules["PyQt5.QtWidgets"] = mock_qtwidgets

    return {
        "PyQt5": mock_pyqt5,
        "QtCore": mock_qtcore,
        "QtWidgets": mock_qtwidgets,
    }


if __name__ == "__main__":
    # Test the PyQt5 mocks
    setup_pyqt5_mocks()

    # Test that we can now create compatible classes
    from abc import ABC

    from PyQt5.QtCore import QObject

    class TestClass(QObject, ABC):
        """Test class that inherits from both QObject and ABC."""

        pass

    # Create instance to verify compatibility
    test_instance = TestClass()
    print("✅ PyQt5 mocks working - compatible metaclass created")
