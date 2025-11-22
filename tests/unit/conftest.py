"""
Pytest configuration and fixtures for comprehensive testing.
Created: 2025-08-28
Updated: 2025-09-02 (Added network GUI visualization mocks integration)
Target: system_cleanup.py, dev_hub.py, network GUI components

This module provides shared fixtures, test configuration, and utilities
for comprehensive testing including automatic visualization dependency mocking.
"""

import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add source path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Import network mocks for automatic setup
try:
    from tests.unit.network.mocks import (
        setup_all_dependency_mocks,
        setup_visualization_mocks,
    )

    NETWORK_MOCKS_AVAILABLE = True
except ImportError:
    NETWORK_MOCKS_AVAILABLE = False
    setup_visualization_mocks = None
    setup_all_dependency_mocks = None

# Add metrics service source path
metrics_src_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "src",
    "utilities",
    "network",
    "network_connectivity_complex",
    "core",
)
sys.path.insert(0, metrics_src_path)

# Import dev_hub for dev_hub specific fixtures
try:
    from rfu import dev_hub
except ImportError:
    dev_hub_path = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rfu")
    sys.path.insert(0, dev_hub_path)
    try:
        import dev_hub
    except ImportError:
        dev_hub = None


@pytest.fixture(scope="session")
def test_session_metadata():
    """Provide metadata about the test session."""
    return {
        "test_file": "test_system_cleanup_2025-08-28.py",
        "target_module": "system_cleanup.py",
        "execution_date": "2025-08-28",
        "timestamp": datetime.now().isoformat(),
        "framework": "pytest",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
    }


@pytest.fixture(scope="session", autouse=True)
def setup_network_visualization_mocks():
    """Automatically setup visualization mocks for all network GUI tests."""
    if NETWORK_MOCKS_AVAILABLE and setup_visualization_mocks:
        try:
            mocks = setup_visualization_mocks()
            print("[SUCCESS] Network visualization mocks automatically enabled")
            return mocks
        except Exception as e:
            print(f"[WARNING] Failed to setup visualization mocks: {e}")
            return None
    else:
        # Fallback: Create basic matplotlib/numpy mocks
        import sys

        matplotlib_mock = Mock()
        pyplot_mock = Mock()
        pyplot_mock.figure = Mock(return_value=Mock())
        pyplot_mock.plot = Mock()
        pyplot_mock.show = Mock()
        pyplot_mock.savefig = Mock()
        matplotlib_mock.pyplot = pyplot_mock

        numpy_mock = Mock()
        numpy_mock.array = Mock(return_value=[])
        numpy_mock.zeros = Mock(return_value=[])
        numpy_mock.ones = Mock(return_value=[])
        numpy_mock.mean = Mock(return_value=0.0)
        numpy_mock.std = Mock(return_value=0.0)

        sys.modules["matplotlib"] = matplotlib_mock
        sys.modules["matplotlib.pyplot"] = pyplot_mock
        sys.modules["numpy"] = numpy_mock

        print("[SUCCESS] Fallback visualization mocks enabled")
        return {
            "matplotlib": matplotlib_mock,
            "pyplot": pyplot_mock,
            "numpy": numpy_mock,
        }


@pytest.fixture(scope="function")
def temp_directory():
    """Create a temporary directory for test operations."""
    temp_dir = tempfile.mkdtemp(prefix="system_cleanup_test_")
    yield Path(temp_dir)
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_cleanup_result():
    """Create a mock CleanupOperationResult for testing."""
    try:
        from src.tools.system.system_cleanup.core.cleanup_base import (
            CleanupOperationResult,
        )

        def create_result(
            success=True,
            message="Test operation",
            items_processed=10,
            space_freed=1024 * 1024,
            errors=None,
        ):
            return CleanupOperationResult(
                success=success,
                message=message,
                items_processed=items_processed,
                space_freed=space_freed,
                errors=errors or [],
            )

        return create_result
    except ImportError:
        # Create a mock class if import fails
        class MockCleanupResult:
            def __init__(
                self,
                success=True,
                message="Test operation",
                items_processed=10,
                space_freed=1024 * 1024,
                errors=None,
            ):
                self.success = success
                self.message = message
                self.items_processed = items_processed
                self.space_freed = space_freed
                self.errors = errors or []

        return MockCleanupResult


@pytest.fixture(scope="function")
def mock_temp_cleaner():
    """Create a mock temporary files cleaner."""
    cleaner = Mock()
    cleaner.execute_operation = Mock()
    cleaner.preview_operation = Mock()
    cleaner.estimate_cleanup_size = Mock(return_value=1024 * 1024 * 50)  # 50MB
    return cleaner


@pytest.fixture(scope="function")
def mock_safety_manager():
    """Create a mock safety manager."""
    manager = Mock()
    manager.create_restore_point = Mock(return_value=True)
    manager.backup_file = Mock()
    manager.validate_operation = Mock(return_value=True)
    return manager


@pytest.fixture(scope="function")
def mock_qt_application():
    """Create a mock Qt application for GUI tests."""
    app = Mock()
    app.exec_ = Mock(return_value=0)
    return app


@pytest.fixture(scope="function")
def mock_qt_widgets():
    """Create mock Qt widgets for testing."""
    widgets = {
        "QMainWindow": Mock(),
        "QWidget": Mock(),
        "QVBoxLayout": Mock(),
        "QHBoxLayout": Mock(),
        "QTabWidget": Mock(),
        "QLabel": Mock(),
        "QPushButton": Mock(),
        "QMessageBox": Mock(),
        "QGroupBox": Mock(),
        "QGridLayout": Mock(),
        "QProgressBar": Mock(),
        "QTextEdit": Mock(),
        "QCheckBox": Mock(),
        "QSpinBox": Mock(),
    }

    # Configure QMessageBox
    widgets["QMessageBox"].Yes = 16384
    widgets["QMessageBox"].No = 65536
    widgets["QMessageBox"].question = Mock()
    widgets["QMessageBox"].information = Mock()
    widgets["QMessageBox"].warning = Mock()
    widgets["QMessageBox"].critical = Mock()

    return widgets


@pytest.fixture(scope="function")
def sample_test_files(temp_directory):
    """Create sample files for testing cleanup operations."""
    files_created = []

    # Create various test files
    test_files = [
        "temp_file_1.tmp",
        "temp_file_2.txt",
        "cache_file.cache",
        "log_file.log",
        "backup_file.bak",
    ]

    for filename in test_files:
        file_path = temp_directory / filename
        file_path.write_text(f"Test content for {filename}")
        files_created.append(file_path)

    # Create subdirectories with files
    subdir = temp_directory / "subdir"
    subdir.mkdir()
    sub_file = subdir / "nested_temp.tmp"
    sub_file.write_text("Nested temp file content")
    files_created.append(sub_file)

    return files_created


@pytest.fixture(scope="function")
def mock_system_diagnostics_gui():
    """Create a mock SystemDiagnosticsGUI base class."""
    mock_gui = Mock()
    mock_gui.tab_widget = Mock()
    mock_gui.setWindowTitle = Mock()
    return mock_gui


@pytest.fixture(scope="function")
def test_logger():
    """Create a test logger for verification."""
    import logging

    logger = logging.getLogger("test_system_cleanup")
    logger.setLevel(logging.DEBUG)

    # Add a handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Test data generators
@pytest.fixture(scope="function")
def cleanup_test_scenarios():
    """Generate various test scenarios for cleanup operations."""
    return [
        {
            "name": "successful_cleanup",
            "success": True,
            "items": 100,
            "space_freed": 1024 * 1024 * 50,  # 50MB
            "errors": [],
        },
        {
            "name": "partial_success_with_errors",
            "success": True,
            "items": 75,
            "space_freed": 1024 * 1024 * 30,  # 30MB
            "errors": ["Cannot delete file1.tmp", "Access denied file2.tmp"],
        },
        {
            "name": "complete_failure",
            "success": False,
            "items": 0,
            "space_freed": 0,
            "errors": ["Insufficient permissions", "Drive not accessible"],
        },
        {
            "name": "large_cleanup",
            "success": True,
            "items": 10000,
            "space_freed": 1024 * 1024 * 1024 * 2,  # 2GB
            "errors": [],
        },
    ]


# Pytest hooks for enhanced reporting
def pytest_runtest_setup(item):
    """Called before each test item is executed."""
    test_name = item.name
    try:
        print(f"\nStarting test: {test_name}")
    except UnicodeEncodeError:
        print(
            f"\nStarting test: {test_name.encode('ascii', 'replace').decode('ascii')}"
        )


def pytest_runtest_teardown(item):
    """Called after each test item is executed."""
    test_name = item.name
    try:
        print(f"Completed test: {test_name}")
    except UnicodeEncodeError:
        print(f"Completed test: {test_name.encode('ascii', 'replace').decode('ascii')}")


def pytest_runtest_makereport(item, call):
    """Called to create test reports."""
    if call.when == "call":
        test_name = item.name
        try:
            if call.excinfo is None:
                print(f"PASSED: {test_name}")
            else:
                print(f"FAILED: {test_name}")
        except UnicodeEncodeError:
            # Handle Unicode encoding issues in Windows terminal
            safe_name = test_name.encode("ascii", "replace").decode("ascii")
            if call.excinfo is None:
                print(f"PASSED: {safe_name}")
            else:
                print(f"FAILED: {safe_name}")


# Custom markers configuration
def pytest_configure(config):
    """Configure custom markers for the test suite."""
    markers = [
        "unit: marks tests as unit tests for individual components",
        "integration: marks tests as integration tests",
        "gui: marks tests that involve GUI components",
        "cleanup: marks tests for cleanup functionality",
        "safety: marks tests for safety features",
        "temp_files: marks tests for temporary file operations",
        "error_handling: marks tests for error handling scenarios",
        "mock: marks tests that use extensive mocking",
        "slow: marks tests that are slow to execute",
        "edge_case: marks tests for edge cases",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


# Performance monitoring
@pytest.fixture(scope="function", autouse=True)
def performance_monitor():
    """Monitor test performance and resource usage."""
    import time

    try:
        import psutil

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        # Ensure we got actual numeric values, not mocks
        if hasattr(start_memory, "_mock_name"):
            start_memory = None
    except (ImportError, AttributeError, TypeError):
        start_time = time.time()
        start_memory = None

    yield

    try:
        end_time = time.time()
        execution_time = end_time - start_time

        if start_memory is not None:
            end_memory = psutil.Process().memory_info().rss

            # Ensure we got actual numeric values, not mocks
            if hasattr(end_memory, "_mock_name"):
                end_memory = None
                memory_delta = None
            else:
                memory_delta = end_memory - start_memory
        else:
            memory_delta = None

        # Log performance data if test is slow
        if execution_time > 1.0:  # More than 1 second
            if memory_delta is not None:
                print(
                    f"Slow test detected: {execution_time:.2f}s, "
                    f"memory delta: {memory_delta/1024/1024:.2f}MB"
                )
            else:
                print(f"Slow test detected: {execution_time:.2f}s")
    except (ImportError, AttributeError, TypeError):
        # If we can't measure memory, just measure time
        end_time = time.time()
        execution_time = end_time - start_time
        if execution_time > 1.0:
            print(f"Slow test detected: {execution_time:.2f}s")


# Test result collection
test_results = []


@pytest.fixture(scope="function", autouse=True)
def collect_test_results(request):
    """Collect test results for final reporting."""
    yield

    # Collect test information
    test_info = {
        "name": request.node.name,
        "file": request.node.fspath.basename,
        "timestamp": datetime.now().isoformat(),
    }

    test_results.append(test_info)


def pytest_sessionfinish(session, exitstatus):
    """Generate final test summary."""
    summary_file = "result_system_cleanup_test_summary_2025-08-28.json"

    summary = {
        "session_info": {
            "exit_status": exitstatus,
            "completion_time": datetime.now().isoformat(),
            "total_tests": len(test_results),
        },
        "test_details": test_results,
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        import json

        json.dump(summary, f, indent=2, ensure_ascii=False)

    try:
        print(f"\nTest summary saved to: {summary_file}")
        print(f"Total tests executed: {len(test_results)}")
        print(f"Session exit status: {exitstatus}")
    except UnicodeEncodeError:
        # Handle Unicode encoding issues in Windows terminal
        print(f"\nTest summary saved to: {summary_file}")
        print(f"Total tests executed: {len(test_results)}")
        print(f"Session exit status: {exitstatus}")


# ===== DEV_HUB SPECIFIC FIXTURES =====


@pytest.fixture
def mock_pyqt5_dev_hub():
    """Fixture to mock PyQt5 components for dev_hub tests."""
    if dev_hub is None:
        pytest.skip("dev_hub module not available")

    with (
        patch("rfu.dev_hub.PYQT5_AVAILABLE", True)
        if dev_hub
        else patch("dev_hub.PYQT5_AVAILABLE", True)
    ):
        # Mock QtCore
        mock_qtcore = Mock()
        mock_qtcore.QThread = Mock()
        mock_qtcore.pyqtSignal = Mock()
        mock_qtcore.Qt = Mock()
        mock_qtcore.Qt.Horizontal = Mock()

        # Mock QtWidgets
        mock_qtwidgets = Mock()
        mock_qtwidgets.QMainWindow = Mock()
        mock_qtwidgets.QWidget = Mock()
        mock_qtwidgets.QVBoxLayout = Mock()
        mock_qtwidgets.QHBoxLayout = Mock()
        mock_qtwidgets.QTabWidget = Mock()
        mock_qtwidgets.QApplication = Mock()
        mock_qtwidgets.QSplitter = Mock()

        with (
            patch.object(dev_hub, "QtCore", mock_qtcore) if dev_hub else Mock(),
            patch.object(dev_hub, "QtWidgets", mock_qtwidgets) if dev_hub else Mock(),
        ):
            yield {"QtCore": mock_qtcore, "QtWidgets": mock_qtwidgets}


@pytest.fixture
def mock_psutil_dev_hub():
    """Fixture to mock psutil components for dev_hub tests."""
    with (
        patch("psutil.cpu_percent", return_value=50.0),
        patch("psutil.cpu_count", return_value=4),
        patch("psutil.virtual_memory") as mock_mem,
        patch("psutil.disk_usage") as mock_disk,
        patch("psutil.Process") as mock_process,
    ):

        # Configure memory mock
        mock_mem_obj = Mock()
        mock_mem_obj.percent = 60.0
        mock_mem_obj.available = 4 * (1024**3)  # 4GB
        mock_mem_obj.total = 8 * (1024**3)  # 8GB
        mock_mem.return_value = mock_mem_obj

        # Configure disk mock
        mock_disk_obj = Mock()
        mock_disk_obj.used = 200 * (1024**3)  # 200GB
        mock_disk_obj.total = 500 * (1024**3)  # 500GB
        mock_disk_obj.free = 300 * (1024**3)  # 300GB
        mock_disk.return_value = mock_disk_obj

        # Configure process mock
        mock_proc = Mock()
        mock_mem_info = Mock()
        mock_mem_info.rss = 50 * (1024**2)  # 50MB
        mock_proc.memory_info.return_value = mock_mem_info
        mock_proc.cpu_percent.return_value = 10.0
        mock_process.return_value = mock_proc

        yield {"memory": mock_mem, "disk": mock_disk, "process": mock_process}


@pytest.fixture
def dev_hub_instance_fixture(mock_pyqt5_dev_hub):
    """Fixture providing a DevHub instance with mocked dependencies."""
    if dev_hub is None:
        pytest.skip("dev_hub module not available")

    with (
        patch.object(dev_hub.DevHub, "_init_gui"),
        patch.object(dev_hub.DevHub, "_setup_performance_monitoring"),
    ):
        instance = dev_hub.DevHub()
        yield instance


@pytest.fixture
def performance_monitor_fixture(mock_pyqt5_dev_hub, mock_psutil_dev_hub):
    """Fixture providing a PerformanceMonitor instance."""
    if dev_hub is None:
        pytest.skip("dev_hub module not available")

    monitor = dev_hub.PerformanceMonitor()
    yield monitor
    # Cleanup
    if hasattr(monitor, "running") and monitor.running:
        monitor.stop()


@pytest.fixture
def log_handler_fixture():
    """Fixture providing a LogHandler instance for dev_hub tests."""
    if dev_hub is None:
        pytest.skip("dev_hub module not available")

    mock_signal = Mock()
    handler = dev_hub.LogHandler(mock_signal)
    yield handler


@pytest.fixture
def sample_log_records_dev_hub():
    """Fixture providing sample log records for dev_hub testing."""
    records = []

    for i in range(5):
        record = Mock()
        record.created = datetime.now().timestamp()
        record.levelname = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"][i]
        record.module = f"test_module_{i}"
        record.funcName = f"test_function_{i}"
        record.lineno = i * 10 + 1
        record.getMessage = Mock(return_value=f"Test message {i}")
        records.append(record)

    return records


# ===== LOG_MANAGER SPECIFIC FIXTURES =====


@pytest.fixture
def clean_log_manager():
    """Ensure LogManager singleton is reset for each test."""
    try:
        from src.log_manager import LogManager

        # Reset singleton before test
        LogManager._instance = None

        yield

        # Clean up after test
        if LogManager._instance:
            try:
                LogManager._instance.cleanup()
            except Exception:
                pass
        LogManager._instance = None
    except ImportError:
        pytest.skip("log_manager module not available")


@pytest.fixture
def temp_test_dir_log_manager():
    """Create a temporary directory for log_manager testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="log_manager_test_"))
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    yield temp_dir

    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_file_system_log_manager():
    """Mock file system operations for log_manager testing."""
    from unittest.mock import patch

    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.write_text") as mock_write,
    ):

        mock_exists.return_value = True
        mock_mkdir.return_value = None
        mock_write.return_value = None

        yield {
            "mkdir": mock_mkdir,
            "exists": mock_exists,
            "write_text": mock_write,
        }


@pytest.fixture
def captured_logs_log_manager():
    """Capture log messages during log_manager testing."""
    import logging

    # Create a test handler to capture logs
    test_handler = logging.Handler()
    test_handler.setLevel(logging.DEBUG)

    captured_messages = []

    def capture_log(record):
        captured_messages.append(record)

    test_handler.emit = capture_log

    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(test_handler)

    yield captured_messages

    # Remove handler
    root_logger.removeHandler(test_handler)


# ===== METRICS_SERVICE SPECIFIC FIXTURES =====


@pytest.fixture
def mock_metrics_logging():
    """Mock logging for metrics_service tests."""

    class MockLogger:
        def debug(self, msg, *args, **kwargs):
            pass

        def info(self, msg, *args, **kwargs):
            pass

        def warning(self, msg, *args, **kwargs):
            pass

        def error(self, msg, *args, **kwargs):
            pass

        def critical(self, msg, *args, **kwargs):
            pass

    class MockLoggingManager:
        def get_tool_logger(self, name):
            return MockLogger()

    def mock_get_network_logging_manager():
        return MockLoggingManager()

    with patch(
        "logging_integration.get_network_logging_manager",
        mock_get_network_logging_manager,
    ):
        yield mock_get_network_logging_manager


@pytest.fixture(autouse=True)
def reset_metrics_global_service():
    """Reset global metrics service before each test."""
    try:
        # Import and reset if available
        import metrics_service

        metrics_service._metrics_service = None
    except ImportError:
        pass


# ===== ERROR_RECOVERY SPECIFIC FIXTURES =====


@pytest.fixture
def error_recovery_instance():
    """Create a fresh instance of PrivacyToolsErrorRecovery for each test."""
    try:
        from src.tools.privacy.error_recovery import PrivacyToolsErrorRecovery

        return PrivacyToolsErrorRecovery()
    except ImportError:
        pytest.skip("error_recovery module not available")


@pytest.fixture
def temp_log_file_error_recovery():
    """Create a temporary log file for error recovery testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def mock_qapplication_error_recovery():
    """Mock QApplication for error recovery GUI-related tests."""
    with patch("utilities.privacy.error_recovery.QApplication") as mock_app:
        mock_instance = Mock()
        mock_app.instance.return_value = mock_instance
        mock_app.return_value = mock_instance
        yield mock_app


@pytest.fixture
def mock_qmessagebox_error_recovery():
    """Mock QMessageBox for error recovery dialog testing."""
    with patch("utilities.privacy.error_recovery.QMessageBox") as mock_box:
        yield mock_box


@pytest.fixture
def sample_errors_error_recovery():
    """Provide sample errors for error recovery testing."""
    return {
        "import_error": ImportError("No module named 'test_module'"),
        "module_not_found": ModuleNotFoundError("No module named 'PyQt5'"),
        "attribute_error": AttributeError("'NoneType' object has no attribute 'test'"),
        "type_error": TypeError("unsupported operand type(s) for +: 'int' and 'str'"),
        "runtime_error": RuntimeError("Something went wrong at runtime"),
        "value_error": ValueError("invalid literal for int() with base 10"),
        "metaclass_attribute_error": AttributeError("metaclass conflict detected"),
        "metaclass_type_error": TypeError(
            "metaclass conflict: the metaclass of a derived class"
        ),
        "privacy_tools_import_error": ImportError("No module named 'privacy_tools'"),
        "gui_themes_import_error": ImportError("No module named 'gui.themes'"),
        "standard_window_import_error": ImportError("No module named 'StandardWindow'"),
    }


@pytest.fixture
def error_recovery_strategies_mapping():
    """Provide the expected error recovery strategies mapping."""
    return {
        "ImportError": "_handle_import_error",
        "ModuleNotFoundError": "_handle_module_not_found",
        "AttributeError": "_handle_attribute_error",
        "TypeError": "_handle_type_error",
        "RuntimeError": "_handle_runtime_error",
    }


@pytest.fixture
def minimal_theme_data_error_recovery():
    """Provide expected minimal theme data for error recovery."""
    return {
        "primary_color": "#3498db",
        "background_color": "#f5f5f5",
        "text_color": "#2c3e50",
        "font_family": "Arial",
        "font_size": 10,
    }


@pytest.fixture
def module_installation_suggestions_error_recovery():
    """Provide module installation suggestions mapping for error recovery."""
    return {
        "PyQt5": "pip install PyQt5",
        "pathlib": "Built-in module - check Python version",
        "typing": "Built-in module - check Python version",
    }

    # Removed problematic auto-fixture that was causing import errors
    # @pytest.fixture(autouse=True)
    # def reset_logging_error_recovery():
    #     """Reset logging configuration before each error recovery test."""
    #     import logging
    #     # Remove any existing handlers
    #     root_logger = logging.getLogger()
    #     for handler in root_logger.handlers[:]:
    #         root_logger.removeHandler(handler)
    #
    #     # Reset the specific logger used by error recovery
    #     privacy_logger = logging.getLogger('privacy_tools_recovery')
    #     for handler in privacy_logger.handlers[:]:
    #         privacy_logger.removeHandler(handler)
    #
    #     yield

    # Cleanup after test
    for handler in privacy_logger.handlers[:]:
        privacy_logger.removeHandler(handler)


@pytest.fixture
def test_functions_error_recovery():
    """Provide test functions for safe_execute testing in error recovery."""

    def success_func(x, y=10):
        return x + y

    def failure_func():
        raise ValueError("Test function failure")

    def complex_func(*args, **kwargs):
        result = sum(args)
        for key, value in kwargs.items():
            result += value
        return result

    return {
        "success": success_func,
        "failure": failure_func,
        "complex": complex_func,
    }


class ErrorRecoveryTestDataProvider:
    """Utility class to provide complex test data for error recovery."""

    @staticmethod
    def get_error_scenarios():
        """Get comprehensive error scenarios for testing."""
        return [
            {
                "error": ImportError("No module named 'privacy_tools'"),
                "context": "privacy_tools_import",
                "expected_handler": "_handle_import_error",
                "expected_fallback": True,
            },
            {
                "error": ModuleNotFoundError("No module named 'PyQt5'"),
                "context": "gui_setup",
                "expected_handler": "_handle_module_not_found",
                "expected_fallback": False,
            },
            {
                "error": AttributeError("metaclass conflict"),
                "context": "class_creation",
                "expected_handler": "_handle_attribute_error",
                "expected_fallback": True,
            },
            {
                "error": TypeError("metaclass conflict: derived class"),
                "context": "inheritance",
                "expected_handler": "_handle_type_error",
                "expected_fallback": True,
            },
            {
                "error": RuntimeError("Application state error"),
                "context": "runtime_operation",
                "expected_handler": "_handle_runtime_error",
                "expected_fallback": False,
            },
        ]

    @staticmethod
    def get_dialog_test_scenarios():
        """Get dialog testing scenarios for error recovery."""
        return [
            {
                "dialog_type": "import_error",
                "error": ImportError("Test import error"),
                "message_type": "critical",
                "title": "Import Error",
            },
            {
                "dialog_type": "module_error",
                "module": "test_module",
                "suggestion": "pip install test_module",
                "message_type": "critical",
                "title": "Module Not Found",
            },
            {
                "dialog_type": "attribute_error",
                "error": AttributeError("Test attribute error"),
                "message_type": "warning",
                "title": "Attribute Error",
            },
            {
                "dialog_type": "type_error",
                "error": TypeError("Test type error"),
                "message_type": "critical",
                "title": "Type Error",
            },
            {
                "dialog_type": "runtime_error",
                "error": RuntimeError("Test runtime error"),
                "message_type": "warning",
                "title": "Runtime Error",
            },
            {
                "dialog_type": "generic_error",
                "error": ValueError("Test value error"),
                "message_type": "critical",
                "title": "Unexpected Error",
            },
        ]


@pytest.fixture
def error_recovery_test_data_provider():
    """Provide the ErrorRecoveryTestDataProvider class."""
    return ErrorRecoveryTestDataProvider
