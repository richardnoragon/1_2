import os
import sys

import pytest

try:  # pragma: no cover - compatibility shim for pytest-lazy-fixture
    from _pytest.python import CallSpec2
except Exception:  # pragma: no cover - best effort import guard
    CallSpec2 = None
else:
    if not hasattr(CallSpec2, "funcargs"):

        def _get_funcargs(self):
            return getattr(self, "_lazy_fixture_funcargs", {})

        def _set_funcargs(self, value):
            setattr(self, "_lazy_fixture_funcargs", value or {})

        CallSpec2.funcargs = property(_get_funcargs, _set_funcargs)

try:
    from PyQt5.QtWidgets import QApplication  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for headless envs
    from tests._stubs.pyqt5 import install_pyqt5_stubs

    install_pyqt5_stubs()
    from PyQt5.QtWidgets import QApplication  # type: ignore

# Add the project root to Python path
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def qapp():
    """
    Fixture for PyQt5 QApplication instance.

    Provides a single QApplication instance for the entire test session.
    Required for any PyQt5 GUI testing.

    Yields:
        QApplication: The application instance
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Note: QApplication cleanup is handled automatically


@pytest.fixture
def qtbot(qapp, qtbot):
    """
    Enhanced qtbot fixture that ensures QApplication is available.

    Args:
        qapp: The QApplication fixture
        qtbot: The pytest-qt qtbot fixture

    Returns:
        QtBot: The qtbot instance for GUI testing
    """
    return qtbot


@pytest.fixture
def test_config_dir(tmp_path):
    """
    Fixture providing a temporary configuration directory for tests.

    Args:
        tmp_path: pytest's temporary path fixture

    Returns:
        Path: Path to temporary config directory
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_rfu_config(test_config_dir, monkeypatch):
    """
    Fixture that mocks the RFU configuration directory.

    This ensures tests don't modify the actual user configuration.

    Args:
        test_config_dir: Temporary config directory fixture
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        Path: Path to the mocked config directory
    """
    # Mock config directory path in config_manager
    monkeypatch.setenv("RFU_CONFIG_DIR", str(test_config_dir))
    return test_config_dir


def pytest_configure(config):
    """Register custom markers for strict-marker runs."""

    for name, description in (
        ("unit", "Unit tests"),
        ("integration", "Integration tests"),
        ("identity", "Identity workflow integration tests"),
        ("performance", "Performance envelope validation tests"),
        ("cli", "CLI workflow coverage"),
        ("smoke", "Smoke tests"),
        ("slow", "Tests that take a long time to run"),
        ("gui", "Tests that require GUI components"),
        ("pdf", "Tests that work with PDF files"),
    ):
        config.addinivalue_line("markers", f"{name}: {description}")
