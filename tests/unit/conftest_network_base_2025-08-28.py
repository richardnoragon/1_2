"""
Pytest configuration and fixtures for network_base.py testing.
Created: 2025-08-28
Target: src/utilities/network/network_connectivity_complex/core/network_base.py

This module provides specialized fixtures and configuration for testing
the NetworkToolBase class and related network components.
"""

import os
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add source paths for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import target modules with error handling
try:
    from src.tools.network.network_connectivity_complex.core.network_base import (
        NetworkAlertLevel,
        NetworkOperationResult,
        NetworkOperationStatus,
        NetworkToolBase,
    )

    NETWORK_BASE_AVAILABLE = True
except ImportError as e:
    NETWORK_BASE_AVAILABLE = False
    import warnings

    warnings.warn(f"Could not import network_base module: {e}")


# Test session configuration
@pytest.fixture(scope="session")
def test_session_info():
    """Provide information about the test session."""
    return {
        "test_target": "network_base.py",
        "test_date": "2025-08-28",
        "test_framework": "pytest",
        "python_version": sys.version,
        "test_directory": str(test_dir),
        "source_directory": str(src_dir),
        "module_available": NETWORK_BASE_AVAILABLE,
    }


# Mock fixtures for dependencies
@pytest.fixture(scope="function")
def mock_config_manager():
    """Create a mock ConfigManager instance."""
    config_manager = Mock()
    config_manager.config = {
        "network_connectivity": {
            "general": {
                "default_timeout": 5000,
                "max_concurrent_operations": 10,
                "enable_logging": True,
                "log_level": "INFO",
            }
        }
    }
    config_manager.get_setting = Mock(
        side_effect=lambda section, key, default=None: config_manager.config.get(
            section, {}
        ).get(key, default)
    )
    config_manager.set_setting = Mock()
    return config_manager


@pytest.fixture(scope="function")
def mock_logger():
    """Create a mock logger instance."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    logger.setLevel = Mock()
    logger.addHandler = Mock()
    return logger


@pytest.fixture(scope="function")
def mock_error_handler():
    """Create a mock error handler."""
    error_handler = Mock()
    error_handler.handle_error = Mock()
    return error_handler


@pytest.fixture(scope="function")
def mock_pyqt5():
    """Mock PyQt5 components for testing."""
    # Mock QObject and pyqtSignal
    mock_qobject = Mock()
    mock_pyqt_signal = Mock()

    # Configure signal behavior
    mock_signal_instance = Mock()
    mock_signal_instance.emit = Mock()
    mock_signal_instance.connect = Mock()
    mock_signal_instance.disconnect = Mock()
    mock_pyqt_signal.return_value = mock_signal_instance

    return {
        "QObject": mock_qobject,
        "pyqtSignal": mock_pyqt_signal,
        "signal_instance": mock_signal_instance,
    }


# Network-specific fixtures
@pytest.fixture(scope="function")
def sample_network_operation_result():
    """Create a sample NetworkOperationResult for testing."""
    if not NETWORK_BASE_AVAILABLE:
        pytest.skip("network_base module not available")

    return NetworkOperationResult(
        success=True,
        operation_type="test_operation",
        data={
            "test_key": "test_value",
            "timestamp": datetime.now().isoformat(),
        },
        error_message=None,
        timestamp=datetime.now(),
        duration_ms=150.5,
    )


@pytest.fixture(scope="function")
def failed_network_operation_result():
    """Create a failed NetworkOperationResult for testing."""
    if not NETWORK_BASE_AVAILABLE:
        pytest.skip("network_base module not available")

    return NetworkOperationResult(
        success=False,
        operation_type="failed_operation",
        data={"error_details": "Something went wrong"},
        error_message="Operation failed due to network timeout",
        timestamp=datetime.now(),
        duration_ms=5000.0,
    )


@pytest.fixture(scope="function")
def mock_network_tool_implementation():
    """Create a concrete implementation of NetworkToolBase for testing."""
    if not NETWORK_BASE_AVAILABLE:
        pytest.skip("network_base module not available")

    class TestNetworkTool(NetworkToolBase):
        def __init__(self, tool_name="TestTool"):
            with (
                patch(
                    "src.tools.network.network_connectivity_complex.core.network_base.ConfigManager"
                ),
                patch(
                    "src.tools.network.network_connectivity_complex.core.network_base.logging.getLogger"
                ),
                patch(
                    "src.tools.network.network_connectivity_complex.core.network_base.error_handler"
                ),
            ):
                super().__init__(tool_name)

            # Test-specific attributes
            self.test_data = {}
            self.test_protocols = ["TCP", "UDP", "HTTP", "HTTPS"]
            self.test_health = {
                "status": "healthy",
                "last_check": datetime.now(),
            }
            self.test_validation_result = True
            self.test_operation_results = []

        def execute_operation(self, **kwargs):
            """Test implementation of execute_operation."""
            self.test_data.update(kwargs)

            if kwargs.get("force_failure", False):
                raise Exception("Forced test failure")

            result = NetworkOperationResult(
                success=True,
                operation_type=kwargs.get("operation_type", "test"),
                data=kwargs,
            )
            self.test_operation_results.append(result)
            return result

        def get_supported_protocols(self):
            """Test implementation of get_supported_protocols."""
            return self.test_protocols

        def validate_parameters(self, **kwargs):
            """Test implementation of validate_parameters."""
            if kwargs.get("invalid", False):
                return False
            return self.test_validation_result

        def get_health_status(self):
            """Test implementation of get_health_status."""
            return self.test_health

    return TestNetworkTool


@pytest.fixture(scope="function")
def network_tool_instance(mock_network_tool_implementation):
    """Create an instance of the test network tool."""
    if not NETWORK_BASE_AVAILABLE:
        pytest.skip("network_base module not available")

    return mock_network_tool_implementation()


# Test data fixtures
@pytest.fixture(scope="function")
def sample_test_data():
    """Provide sample test data for network operations."""
    return {
        "basic_operation": {
            "host": "192.168.1.1",
            "port": 80,
            "timeout": 5000,
            "protocol": "TCP",
        },
        "complex_operation": {
            "targets": ["google.com", "github.com", "stackoverflow.com"],
            "methods": ["ping", "traceroute", "port_scan"],
            "options": {
                "max_concurrent": 5,
                "timeout_per_host": 3000,
                "retry_count": 3,
            },
        },
        "invalid_operation": {
            "host": "",  # Invalid empty host
            "port": -1,  # Invalid port
            "timeout": 0,  # Invalid timeout
        },
    }


@pytest.fixture(scope="function")
def historical_test_data():
    """Provide historical data for testing data storage and retrieval."""
    base_time = datetime(2025, 8, 28, 10, 0, 0)
    data_points = []

    for i in range(10):
        timestamp = base_time.replace(minute=i * 5)  # Every 5 minutes
        data_points.append(
            {
                "timestamp": timestamp.isoformat(),
                "measurement": f"test_metric_{i}",
                "value": i * 10 + 5,
                "status": "active" if i % 2 == 0 else "inactive",
                "metadata": {"source": "test_generator", "iteration": i},
            }
        )

    return data_points


@pytest.fixture(scope="function")
def threading_test_environment():
    """Set up environment for threading tests."""
    test_env = {
        "threads": [],
        "results": [],
        "errors": [],
        "completion_events": [],
    }

    def create_test_thread(target, *args, **kwargs):
        """Helper to create and track test threads."""
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        test_env["threads"].append(thread)
        return thread

    def wait_for_threads(timeout=10.0):
        """Helper to wait for all threads to complete."""
        for thread in test_env["threads"]:
            thread.join(timeout=timeout)

        # Check if any threads are still alive
        alive_threads = [t for t in test_env["threads"] if t.is_alive()]
        if alive_threads:
            raise TimeoutError(
                f"{len(alive_threads)} threads did not complete within timeout"
            )

    test_env["create_thread"] = create_test_thread
    test_env["wait_for_completion"] = wait_for_threads

    yield test_env

    # Cleanup: ensure all threads are stopped
    for thread in test_env["threads"]:
        if thread.is_alive():
            thread.join(timeout=1.0)


# Performance testing fixtures
@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor performance metrics during tests."""
    import time

    import psutil

    monitor_data = {
        "start_time": time.time(),
        "start_memory": psutil.Process().memory_info().rss,
        "start_cpu": psutil.cpu_percent(),
        "measurements": [],
    }

    def record_measurement(label=""):
        """Record a performance measurement."""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        current_cpu = psutil.cpu_percent()

        measurement = {
            "label": label,
            "timestamp": current_time,
            "elapsed": current_time - monitor_data["start_time"],
            "memory_rss": current_memory,
            "memory_delta": current_memory - monitor_data["start_memory"],
            "cpu_percent": current_cpu,
        }

        monitor_data["measurements"].append(measurement)
        return measurement

    monitor_data["record"] = record_measurement

    yield monitor_data

    # Final measurement
    final_measurement = record_measurement("test_completion")

    # Log performance summary if test was slow or used excessive memory
    if final_measurement["elapsed"] > 1.0:  # More than 1 second
        print(f"Slow test detected: {final_measurement['elapsed']:.2f}s")

    if final_measurement["memory_delta"] > 50 * 1024 * 1024:  # More than 50MB
        print(
            f"High memory usage: {final_measurement['memory_delta'] / 1024 / 1024:.2f}MB"
        )


# Callback testing fixtures
@pytest.fixture(scope="function")
def callback_tracker():
    """Track callback invocations for testing."""
    tracker = {"data_callbacks": [], "alert_callbacks": [], "call_history": []}

    def create_data_callback(callback_id):
        """Create a trackable data callback."""

        def callback(data):
            call_info = {
                "type": "data",
                "callback_id": callback_id,
                "timestamp": datetime.now(),
                "data": data,
            }
            tracker["data_callbacks"].append(call_info)
            tracker["call_history"].append(call_info)

        return callback

    def create_alert_callback(callback_id):
        """Create a trackable alert callback."""

        def callback(alert_type, level, message):
            call_info = {
                "type": "alert",
                "callback_id": callback_id,
                "timestamp": datetime.now(),
                "alert_type": alert_type,
                "level": level,
                "message": message,
            }
            tracker["alert_callbacks"].append(call_info)
            tracker["call_history"].append(call_info)

        return callback

    def create_failing_callback(callback_id, exception_message="Test callback failure"):
        """Create a callback that always fails."""

        def callback(*args, **kwargs):
            call_info = {
                "type": "failing",
                "callback_id": callback_id,
                "timestamp": datetime.now(),
                "args": args,
                "kwargs": kwargs,
            }
            tracker["call_history"].append(call_info)
            raise Exception(exception_message)

        return callback

    tracker["create_data_callback"] = create_data_callback
    tracker["create_alert_callback"] = create_alert_callback
    tracker["create_failing_callback"] = create_failing_callback

    return tracker


# Temporary directory fixture
@pytest.fixture(scope="function")
def temp_test_directory():
    """Create a temporary directory for test operations."""
    temp_dir = Path(tempfile.mkdtemp(prefix="network_base_test_"))

    yield temp_dir

    # Cleanup
    import shutil

    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Could not clean up temp directory {temp_dir}: {e}")


# Test result collection
test_results_collection = []


@pytest.fixture(scope="function", autouse=True)
def collect_test_metadata(request):
    """Automatically collect test metadata."""
    test_info = {
        "name": request.node.name,
        "file": request.node.fspath.basename,
        "start_time": datetime.now().isoformat(),
        "markers": [mark.name for mark in request.node.iter_markers()],
    }

    yield

    test_info["end_time"] = datetime.now().isoformat()
    test_results_collection.append(test_info)


# Pytest hooks for enhanced reporting
def pytest_runtest_setup(item):
    """Called before each test item is executed."""
    if not NETWORK_BASE_AVAILABLE:
        pytest.skip("network_base module not available", allow_module_level=True)


def pytest_runtest_makereport(item, call):
    """Called to create test reports."""
    if call.when == "call":
        outcome = "PASSED" if call.excinfo is None else "FAILED"
        print(f"{outcome}: {item.name}")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    markers = [
        "unit: Unit tests for individual components",
        "integration: Integration tests across components",
        "performance: Performance and load tests",
        "threading: Multi-threading safety tests",
        "edge_case: Edge case and boundary condition tests",
        "mock: Tests using extensive mocking",
        "slow: Tests that take longer to execute",
        "signal: Tests for PyQt signal functionality",
        "callback: Tests for callback mechanisms",
        "error_handling: Tests for error handling scenarios",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_sessionfinish(session, exitstatus):
    """Generate session summary."""
    summary_file = test_dir / "result_network_base_test_metadata_2025-08-28.json"

    summary = {
        "session_info": {
            "exit_status": exitstatus,
            "completion_time": datetime.now().isoformat(),
            "total_tests": len(test_results_collection),
            "module_available": NETWORK_BASE_AVAILABLE,
        },
        "test_details": test_results_collection,
    }

    try:
        import json

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nTest metadata saved to: {summary_file}")
    except Exception as e:
        print(f"Could not save test metadata: {e}")

    print(f"Session completed with exit status: {exitstatus}")
    print(f"Total tests collected: {len(test_results_collection)}")
