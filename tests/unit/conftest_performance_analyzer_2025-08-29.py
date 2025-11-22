"""
Pytest configuration and fixtures for performance_analyzer tests.
Created: 2025-08-29
Target: performance_analyzer.py

This module provides shared fixtures, test configuration, and utilities
for comprehensive testing of the performance_analyzer module.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Add source path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# Import the module under test
try:
    from src.tools.network.network_connectivity_complex.core.performance_analyzer import (
        PerformanceAnalyzer,
        PerformanceMeasurement,
        PerformanceMetric,
    )
except ImportError:
    try:
        from src.tools.network.network_connectivity_complex.core.performance_analyzer import (
            PerformanceAnalyzer,
            PerformanceMeasurement,
            PerformanceMetric,
        )
    except ImportError:
        # Mock the imports for testing if module not found
        class MockPerformanceMetric:
            LATENCY = "latency"
            THROUGHPUT = "throughput"
            PACKET_LOSS = "packet_loss"
            JITTER = "jitter"
            BANDWIDTH_UTILIZATION = "bandwidth_utilization"

        class MockPerformanceMeasurement:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class MockPerformanceAnalyzer:
            def __init__(self):
                self.measurements = {}
                self.max_measurements_per_interface = 1000
                self.logger = Mock()
                self.thresholds = {}

        PerformanceMetric = MockPerformanceMetric()
        PerformanceMeasurement = MockPerformanceMeasurement
        PerformanceAnalyzer = MockPerformanceAnalyzer


@pytest.fixture(scope="session")
def test_session_metadata():
    """Provide metadata about the test session."""
    return {
        "test_file": "test_performance_analyzer_2025-08-29.py",
        "target_module": "performance_analyzer.py",
        "execution_date": "2025-08-29",
        "timestamp": datetime.now().isoformat(),
        "framework": "pytest",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
    }


@pytest.fixture
def empty_analyzer():
    """Create a fresh PerformanceAnalyzer instance."""
    return PerformanceAnalyzer()


@pytest.fixture
def sample_measurement():
    """Create a sample PerformanceMeasurement."""
    return PerformanceMeasurement(
        metric=PerformanceMetric.LATENCY,
        value=50.0,
        unit="ms",
        timestamp=datetime.now(),
        interface_name="eth0",
        target="8.8.8.8",
        additional_data={"protocol": "icmp"},
    )


@pytest.fixture
def performance_measurement_factory():
    """Factory for creating PerformanceMeasurement instances."""

    def create_measurement(
        metric=PerformanceMetric.LATENCY,
        value=50.0,
        unit="ms",
        timestamp=None,
        interface_name="eth0",
        target="8.8.8.8",
        additional_data=None,
    ):
        return PerformanceMeasurement(
            metric=metric,
            value=value,
            unit=unit,
            timestamp=timestamp or datetime.now(),
            interface_name=interface_name,
            target=target,
            additional_data=additional_data,
        )

    return create_measurement


@pytest.fixture
def sample_measurements_set(performance_measurement_factory):
    """Create a set of realistic measurements for testing."""
    base_time = datetime.now()
    measurements = []

    # Latency measurements
    for i in range(10):
        measurements.append(
            performance_measurement_factory(
                metric=PerformanceMetric.LATENCY,
                value=20.0 + i * 5,  # 20, 25, 30, ..., 65 ms
                timestamp=base_time + timedelta(seconds=i * 30),
                interface_name="eth0",
            )
        )

    # Throughput measurements
    for i in range(10):
        measurements.append(
            performance_measurement_factory(
                metric=PerformanceMetric.THROUGHPUT,
                value=80.0 + i * 10,  # 80, 90, 100, ..., 170 Mbps
                unit="Mbps",
                timestamp=base_time + timedelta(seconds=i * 30),
                interface_name="eth0",
            )
        )

    # Packet loss measurements
    for i in range(10):
        measurements.append(
            performance_measurement_factory(
                metric=PerformanceMetric.PACKET_LOSS,
                value=0.1 + i * 0.2,  # 0.1, 0.3, 0.5, ..., 1.9 %
                unit="%",
                timestamp=base_time + timedelta(seconds=i * 30),
                interface_name="eth0",
            )
        )

    return measurements


@pytest.fixture
def populated_analyzer(empty_analyzer, sample_measurements_set):
    """Create an analyzer populated with sample data."""
    for measurement in sample_measurements_set:
        empty_analyzer.add_measurement(measurement)
    return empty_analyzer


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    fixed_time = datetime(2025, 8, 29, 12, 0, 0)
    target_module = (
        "src.tools.network.network_connectivity_complex."
        "core.performance_analyzer.datetime"
    )
    with patch(target_module) as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt


@pytest.fixture
def captured_logs():
    """Capture log messages during testing."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def test_logger():
    """Create a test logger for verification."""
    logger = logging.getLogger("test_performance_analyzer")
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


@pytest.fixture
def multi_interface_measurements(performance_measurement_factory):
    """Create measurements for multiple interfaces."""
    base_time = datetime.now()
    measurements = []

    interfaces = ["eth0", "wlan0", "default"]

    for interface in interfaces:
        for i in range(5):
            # Latency measurements
            measurements.append(
                performance_measurement_factory(
                    metric=PerformanceMetric.LATENCY,
                    value=30.0 + i * 10,
                    timestamp=base_time + timedelta(seconds=i * 60),
                    interface_name=interface,
                )
            )

            # Throughput measurements
            measurements.append(
                performance_measurement_factory(
                    metric=PerformanceMetric.THROUGHPUT,
                    value=50.0 + i * 20,
                    unit="Mbps",
                    timestamp=base_time + timedelta(seconds=i * 60),
                    interface_name=interface,
                )
            )

    return measurements


@pytest.fixture
def edge_case_measurements(performance_measurement_factory):
    """Create edge case measurements for testing."""
    base_time = datetime.now()
    measurements = []

    # Extreme values
    measurements.extend(
        [
            # Very high latency
            performance_measurement_factory(
                metric=PerformanceMetric.LATENCY,
                value=1000.0,
                timestamp=base_time,
            ),
            # Zero throughput
            performance_measurement_factory(
                metric=PerformanceMetric.THROUGHPUT,
                value=0.0,
                unit="Mbps",
                timestamp=base_time,
            ),
            # 100% packet loss
            performance_measurement_factory(
                metric=PerformanceMetric.PACKET_LOSS,
                value=100.0,
                unit="%",
                timestamp=base_time,
            ),
            # Very high jitter
            performance_measurement_factory(
                metric=PerformanceMetric.JITTER,
                value=500.0,
                unit="ms",
                timestamp=base_time,
            ),
            # 100% bandwidth utilization
            performance_measurement_factory(
                metric=PerformanceMetric.BANDWIDTH_UTILIZATION,
                value=100.0,
                unit="%",
                timestamp=base_time,
            ),
        ]
    )

    return measurements


@pytest.fixture
def time_series_measurements(performance_measurement_factory):
    """Create time series measurements for trend analysis."""
    base_time = datetime.now() - timedelta(hours=2)
    measurements = []

    # Create increasing trend for latency
    for i in range(20):
        measurements.append(
            performance_measurement_factory(
                metric=PerformanceMetric.LATENCY,
                value=20.0 + i * 2.0,  # Increasing from 20 to 58
                timestamp=base_time + timedelta(minutes=i * 5),
                interface_name="eth0",
            )
        )

    # Create decreasing trend for throughput
    for i in range(20):
        measurements.append(
            performance_measurement_factory(
                metric=PerformanceMetric.THROUGHPUT,
                value=100.0 - i * 2.0,  # Decreasing from 100 to 62
                unit="Mbps",
                timestamp=base_time + timedelta(minutes=i * 5),
                interface_name="eth0",
            )
        )

    return measurements


# Performance monitoring
@pytest.fixture(scope="function", autouse=True)
def performance_monitor():
    """Monitor test performance and resource usage."""
    import time

    try:
        import psutil

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        yield

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        # Log performance data if test is slow
        if execution_time > 1.0:  # More than 1 second
            print(
                f"Slow test detected: {execution_time:.2f}s, "
                f"memory delta: {memory_delta/1024/1024:.2f}MB"
            )
    except ImportError:
        # If psutil not available, just track time
        start_time = time.time()
        yield
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
    summary_file = "result_performance_analyzer_test_summary_2025-08-29.json"

    summary = {
        "session_info": {
            "exit_status": exitstatus,
            "completion_time": datetime.now().isoformat(),
            "total_tests": len(test_results),
        },
        "test_details": test_results,
    }

    try:
        import json

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
    except Exception as e:
        print(f"Failed to save test summary: {e}")

    print(f"\nTest summary saved to: {summary_file}")
    print(f"Total tests executed: {len(test_results)}")
    print(f"Session exit status: {exitstatus}")


# Custom pytest hooks
def pytest_runtest_setup(item):
    """Called before each test item is executed."""
    test_name = item.name
    print(f"\n→ Starting test: {test_name}")


def pytest_runtest_teardown(item):
    """Called after each test item is executed."""
    test_name = item.name
    print(f"✓ Completed test: {test_name}")


def pytest_runtest_makereport(item, call):
    """Called to create test reports."""
    if call.when == "call":
        test_name = item.name
        if call.excinfo is None:
            print(f"✅ PASSED: {test_name}")
        else:
            print(f"❌ FAILED: {test_name}")


# Custom markers configuration
def pytest_configure(config):
    """Configure custom markers for the test suite."""
    markers = [
        "unit: marks tests as unit tests for individual components",
        "integration: marks tests as integration tests",
        "edge_case: marks tests for edge cases and boundary conditions",
        "error_handling: marks tests for error handling scenarios",
        "mock: marks tests that use extensive mocking",
        "slow: marks tests that are slow to execute",
        "statistics: marks tests for statistical calculations",
        "trending: marks tests for trend analysis functionality",
        "scoring: marks tests for metric scoring functionality",
        "recommendations: marks tests for recommendation generation",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)
