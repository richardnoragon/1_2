"""
Pytest Configuration and Fixtures for Privacy Hub Tests

This module provides comprehensive fixtures and configuration
for testing the privacy_hub.py module.

Generated: 2025-08-31
Target: test_privacy_hub_2025-08-31.py
"""

import json
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add source path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

# PyQt5 imports with error handling
try:
    from PyQt5.QtCore import Qt, QThread
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QWidget

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


class MockTool:
    """Mock tool class for testing."""

    def __init__(self, name="mock_tool"):
        self.name = name
        self.progress_updated = Mock()
        self.operation_complete = Mock()
        self.error_occurred = Mock()
        self.status_changed = Mock()
        self.run_in_thread = Mock()
        self.stop_operation = Mock()
        self.preview_operation = Mock()
        self.execute_operation = Mock()

        # Configure default return values
        self.preview_operation.return_value = {
            "platform": "windows",
            "items": [],
            "warnings": [],
        }

        self.execute_operation.return_value = {
            "success": True,
            "message": "Operation completed",
            "errors": [],
        }

        # Mock thread
        mock_thread = Mock()
        mock_thread.isRunning.return_value = False
        self.run_in_thread.return_value = mock_thread


class MockBrowserDetector:
    """Mock browser detector for testing."""

    def __init__(self):
        self.detected_browsers = ["chrome", "firefox", "edge"]
        self.running_browsers = ["chrome"]

    def detect_installed_browsers(self):
        return self.detected_browsers

    def get_running_browsers(self):
        return self.running_browsers


class MockPlatformUtils:
    """Mock platform utilities for testing."""

    @staticmethod
    def get_platform():
        return "windows"

    @staticmethod
    def is_admin():
        return True


class MockQWidget:
    """Mock QWidget for testing."""

    def __init__(self):
        self.setChecked = Mock()
        self.isChecked = Mock(return_value=False)
        self.text = Mock(return_value="")
        self.value = Mock(return_value=0)
        self.setPlainText = Mock()
        self.setVisible = Mock()
        self.setRange = Mock()
        self.setValue = Mock()
        self.clear = Mock()
        self.addItem = Mock()
        self.currentIndex = Mock(return_value=0)


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup for entire test session."""
    print(f"\n{'='*60}")
    print("PRIVACY HUB TEST SESSION STARTING")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"PyQt5 Available: {PYQT5_AVAILABLE}")
    print(f"{'='*60}")

    yield

    print(f"\n{'='*60}")
    print("PRIVACY HUB TEST SESSION COMPLETED")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")


@pytest.fixture(scope="function")
def temp_directory():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="privacy_hub_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_qt_application():
    """Create mock Qt application for testing."""
    if PYQT5_AVAILABLE:
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        yield app
    else:
        yield None


@pytest.fixture(scope="function")
def mock_tools():
    """Create mock tools for testing."""
    return {"trash": MockTool("trash"), "cookies": MockTool("cookies")}


@pytest.fixture(scope="function")
def mock_browser_detector():
    """Create mock browser detector."""
    return MockBrowserDetector()


@pytest.fixture(scope="function")
def mock_platform_utils():
    """Create mock platform utilities."""
    return MockPlatformUtils()


@pytest.fixture(scope="function")
def mock_ui_components():
    """Create mock UI components."""
    return {
        "tab_widget": MockQWidget(),
        "browser_list": MockQWidget(),
        "browser_checkboxes": {
            "chrome": MockQWidget(),
            "firefox": MockQWidget(),
            "edge": MockQWidget(),
            "safari": MockQWidget(),
        },
        "trash_secure_check": MockQWidget(),
        "trash_backup_check": MockQWidget(),
        "trash_preview_text": MockQWidget(),
        "trash_progress": MockQWidget(),
        "cookies_backup_check": MockQWidget(),
        "domain_filter_edit": MockQWidget(),
        "age_spinbox": MockQWidget(),
        "cookies_preview_text": MockQWidget(),
        "cookies_progress": MockQWidget(),
        "main_layout": MockQWidget(),
    }


@pytest.fixture(scope="function")
def mock_inherited_methods():
    """Create mock inherited methods."""
    return {
        "create_header": Mock(),
        "create_group_box": Mock(),
        "create_button": Mock(),
        "create_progress_bar": Mock(),
        "show_error_dialog": Mock(),
        "show_info_dialog": Mock(),
        "show_status_message": Mock(),
        "setMinimumSize": Mock(),
        "resize": Mock(),
    }


@pytest.fixture(scope="function")
def test_data():
    """Provide test data for various scenarios."""
    return {
        "browsers": {
            "detected": ["chrome", "firefox", "edge", "safari"],
            "running": ["chrome"],
            "supported": ["chrome", "firefox", "edge", "safari"],
        },
        "trash_preview": {
            "platform": "windows",
            "trash_items": ["file1.txt", "file2.txt", "folder1"],
            "warnings": ["Large files detected", "System files present"],
        },
        "cookies_preview": {
            "estimated_cookies": {"chrome": 150, "firefox": 75, "edge": 25},
            "warnings": ["Some browsers are running"],
        },
        "operation_results": {
            "success": {
                "success": True,
                "message": "Operation completed successfully",
                "errors": [],
            },
            "failure": {
                "success": False,
                "message": "Operation failed",
                "errors": ["Error 1", "Error 2"],
            },
        },
    }


@pytest.fixture(autouse=True)
def test_method_timer():
    """Time each test method execution."""
    start_time = time.time()
    yield
    end_time = time.time()
    execution_time = end_time - start_time
    print(f" [{execution_time:.3f}s]", end="")


@pytest.fixture(scope="function")
def mock_all_imports():
    """Mock all external imports comprehensively."""
    with patch.multiple(
        "sys.modules",
        **{
            "PyQt5.QtWidgets": Mock(),
            "PyQt5.QtCore": Mock(),
            "PyQt5.QtGui": Mock(),
            "gui.standard_window": Mock(),
            "gui.themes": Mock(),
            "src.tools.privacy.privacy_tools.tools.secure_empty_trash": Mock(),
            "src.tools.privacy.privacy_tools.tools.delete_cookies": Mock(),
            "src.tools.privacy.privacy_tools.core.browser_detector": Mock(),
            "src.tools.privacy.privacy_tools.core.platform_utils": Mock(),
        },
    ):
        yield


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "gui: GUI tests requiring display")
    config.addinivalue_line("markers", "mock: Tests using mocks")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Add markers to tests based on name patterns
    for item in items:
        if "gui" in item.name.lower():
            item.add_marker(pytest.mark.gui)
        if "mock" in item.name.lower():
            item.add_marker(pytest.mark.mock)
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


def pytest_runtest_setup(item):
    """Setup before each test."""
    if item.get_closest_marker("gui") and not PYQT5_AVAILABLE:
        pytest.skip("PyQt5 not available for GUI tests")


def pytest_runtest_teardown(item):
    """Cleanup after each test."""
    # Force garbage collection
    import gc

    gc.collect()


def pytest_report_header(config):
    """Add custom information to pytest header."""
    return [
        f"Privacy Hub Test Suite - Generated: 2025-08-31",
        f"Target: src/utilities/privacy/privacy_tools/gui/privacy_hub.py",
        f"PyQt5 Available: {PYQT5_AVAILABLE}",
        f"Python: {sys.version}",
        f"Platform: {sys.platform}",
    ]


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_browser_list(count=3, running_count=1):
        """Generate browser list data."""
        browsers = ["chrome", "firefox", "edge", "safari", "opera"][:count]
        running = browsers[:running_count]
        return browsers, running

    @staticmethod
    def generate_trash_items(count=5):
        """Generate trash items list."""
        return [f"test_file_{i}.txt" for i in range(count)]

    @staticmethod
    def generate_cookie_data(browsers=None):
        """Generate cookie data for browsers."""
        if browsers is None:
            browsers = ["chrome", "firefox"]

        return {browser: (i + 1) * 50 for i, browser in enumerate(browsers)}


# Global test state tracking
test_state = {
    "start_time": None,
    "test_count": 0,
    "passed_count": 0,
    "failed_count": 0,
}


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    test_state["start_time"] = time.time()


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    end_time = time.time()
    total_time = end_time - test_state["start_time"]

    print(f"\n{'='*60}")
    print("PRIVACY HUB TEST SESSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Exit status: {exitstatus}")
    print(f"{'='*60}")


# Export commonly used fixtures and utilities
__all__ = [
    "MockTool",
    "MockBrowserDetector",
    "MockPlatformUtils",
    "MockQWidget",
    "TestDataGenerator",
    "PYQT5_AVAILABLE",
]
