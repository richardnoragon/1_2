import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication

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
