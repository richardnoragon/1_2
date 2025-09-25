"""
Enhanced Test Data Setup and Configuration for SecurityValidator Tests
======================================================================

Configuration File: conftest_security_validator_enhanced_2025-08-30.py
Target: test_security_validator_2025-08-30.py
Generated: 2025-08-30T09:40:00Z

This module provides enhanced pytest fixtures, test data, and configuration
for comprehensive SecurityValidator unit testing with performance monitoring
and memory profiling.

Features:
- All original fixtures from conftest_security_validator_2025-08-30.py
- Performance benchmarking utilities
- Memory profiling and monitoring
- Enhanced test data generation
- Comprehensive setup and teardown methods
- Test result analysis and reporting
"""

import json
import logging
import os
import random
import string
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

try:
    import memory_profiler

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    memory_profiler = None
    MEMORY_PROFILER_AVAILABLE = False

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Enhanced test configuration
ENHANCED_TEST_CONFIG = {
    "log_level": logging.DEBUG,
    "timeout": 60,
    "mock_data_size": 100,
    "performance_iterations": 1000,
    "memory_threshold_mb": 50,
    "performance_threshold_ms": 100,
    "benchmark_warmup_rounds": 3,
    "benchmark_min_rounds": 5,
}


class EnhancedTestDataGenerator:
    """Enhanced test data generator with performance considerations."""

    def __init__(self):
        """Initialize the enhanced test data generator."""
        self.cache = {}
        self.generation_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "generation_time": {},
        }

    def get_cached_or_generate(
        self, cache_key: str, generator_func, *args, **kwargs
    ):
        """Get data from cache or generate and cache it."""
        if cache_key in self.cache:
            self.generation_stats["cache_hits"] += 1
            return self.cache[cache_key]

        start_time = time.time()
        data = generator_func(*args, **kwargs)
        generation_time = time.time() - start_time

        self.cache[cache_key] = data
        self.generation_stats["cache_misses"] += 1
        self.generation_stats["generation_time"][cache_key] = generation_time

        return data

    def generate_stress_test_ips(self, count: int = 10000) -> List[str]:
        """Generate large number of IP addresses for stress testing."""
        cache_key = f"stress_ips_{count}"
        return self.get_cached_or_generate(
            cache_key, self._generate_stress_test_ips, count
        )

    def _generate_stress_test_ips(self, count: int) -> List[str]:
        """Internal method to generate stress test IPs."""
        ips = []
        for i in range(count):
            # Generate diverse IP patterns for comprehensive testing
            if i % 4 == 0:  # Public IPs
                ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            elif i % 4 == 1:  # Private 192.168.x.x
                ip = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
            elif i % 4 == 2:  # Private 10.x.x.x
                ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            else:  # Private 172.16-31.x.x
                ip = f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            ips.append(ip)
        return ips

    def generate_stress_test_domains(self, count: int = 10000) -> List[str]:
        """Generate large number of domains for stress testing."""
        cache_key = f"stress_domains_{count}"
        return self.get_cached_or_generate(
            cache_key, self._generate_stress_test_domains, count
        )

    def _generate_stress_test_domains(self, count: int) -> List[str]:
        """Internal method to generate stress test domains."""
        tlds = [
            ".com",
            ".org",
            ".net",
            ".edu",
            ".gov",
            ".mil",
            ".int",
            ".io",
            ".ai",
            ".co",
        ]
        domains = []

        for i in range(count):
            # Generate varied domain lengths and patterns
            if i % 3 == 0:  # Short domains
                length = random.randint(3, 8)
            elif i % 3 == 1:  # Medium domains
                length = random.randint(8, 20)
            else:  # Longer domains
                length = random.randint(20, 40)

            domain_name = "".join(
                random.choices(
                    string.ascii_lowercase + string.digits, k=length
                )
            )
            tld = random.choice(tlds)
            domains.append(f"{domain_name}{tld}")

        return domains

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about data generation performance."""
        return self.generation_stats.copy()


class MemoryProfiler:
    """Memory profiling utility for tests."""

    def __init__(self):
        """Initialize memory profiler."""
        self.snapshots = []
        self.peak_memory = 0
        self.enabled = psutil is not None

    def start_monitoring(self):
        """Start memory monitoring."""
        if not self.enabled:
            return

        self.snapshots = []
        self.peak_memory = 0
        self._take_snapshot("start")

    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot."""
        if self.enabled:
            self._take_snapshot(label)

    def _take_snapshot(self, label: str):
        """Internal method to take memory snapshot."""
        try:
            if psutil:
                process = psutil.Process()
                memory_info = process.memory_info()

                snapshot = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "label": label,
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": process.memory_percent(),
                    "available": psutil.virtual_memory().available,
                }

                self.snapshots.append(snapshot)
                self.peak_memory = max(self.peak_memory, memory_info.rss)
            else:
                self.snapshots.append(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "label": label,
                        "error": "psutil not available",
                    }
                )

        except Exception as e:
            self.snapshots.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "label": label,
                    "error": str(e),
                }
            )

    def stop_monitoring(self):
        """Stop monitoring and return results."""
        if self.enabled:
            self._take_snapshot("end")

        return {
            "snapshots": self.snapshots,
            "peak_memory_mb": (
                self.peak_memory / (1024 * 1024) if self.peak_memory else 0
            ),
            "enabled": self.enabled,
        }


class PerformanceBenchmark:
    """Performance benchmarking utility for tests."""

    def __init__(self):
        """Initialize performance benchmark."""
        self.measurements = []
        self.current_measurement = None

    def start_measurement(self, test_name: str, operation: str):
        """Start a performance measurement."""
        self.current_measurement = {
            "test_name": test_name,
            "operation": operation,
            "start_time": time.perf_counter(),
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def end_measurement(self) -> Dict[str, Any]:
        """End the current measurement and return results."""
        if not self.current_measurement:
            return {}

        end_time = time.perf_counter()
        duration = end_time - self.current_measurement["start_time"]

        measurement = {
            **self.current_measurement,
            "end_time": end_time,
            "end_timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "duration_milliseconds": duration * 1000,
        }

        self.measurements.append(measurement)
        self.current_measurement = None

        return measurement

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.measurements:
            return {}

        durations = [m["duration_milliseconds"] for m in self.measurements]

        return {
            "total_measurements": len(self.measurements),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "total_duration_ms": sum(durations),
            "measurements": self.measurements,
        }


# Enhanced Pytest fixtures
@pytest.fixture(scope="session")
def enhanced_test_config():
    """Fixture providing enhanced test configuration."""
    return ENHANCED_TEST_CONFIG.copy()


@pytest.fixture(scope="session")
def enhanced_data_generator():
    """Fixture providing enhanced test data generator."""
    return EnhancedTestDataGenerator()


@pytest.fixture
def memory_profiler():
    """Fixture providing memory profiler."""
    profiler = MemoryProfiler()
    profiler.start_monitoring()
    yield profiler
    return profiler.stop_monitoring()


@pytest.fixture
def performance_benchmark():
    """Fixture providing performance benchmark utility."""
    return PerformanceBenchmark()


@pytest.fixture
def stress_test_ips(enhanced_data_generator):
    """Fixture providing large dataset of IP addresses for stress testing."""
    return enhanced_data_generator.generate_stress_test_ips(1000)


@pytest.fixture
def stress_test_domains(enhanced_data_generator):
    """Fixture providing large dataset of domains for stress testing."""
    return enhanced_data_generator.generate_stress_test_domains(1000)


@pytest.fixture(autouse=True)
def test_execution_tracker(request):
    """Automatically track test execution metrics."""
    start_time = time.perf_counter()
    start_timestamp = datetime.now(timezone.utc)

    # Store test metadata
    test_metadata = {
        "test_name": request.node.name,
        "test_module": (
            request.module.__name__ if request.module else "unknown"
        ),
        "start_time": start_timestamp.isoformat(),
        "markers": [marker.name for marker in request.node.iter_markers()],
    }

    yield test_metadata

    # Calculate execution time
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    test_metadata.update(
        {
            "end_time": datetime.now(timezone.utc).isoformat(),
            "execution_time_seconds": execution_time,
            "execution_time_milliseconds": execution_time * 1000,
        }
    )

    # Store results for later analysis
    if not hasattr(request.config, "_test_execution_data"):
        request.config._test_execution_data = []
    request.config._test_execution_data.append(test_metadata)


# Include all original fixtures from the base conftest file
@pytest.fixture
def test_data_generator():
    """Fixture providing original test data generator for compatibility."""
    try:
        # Import from the existing conftest file
        sys.path.insert(0, str(Path(__file__).parent))
        from conftest_security_validator_2025_08_30 import TestDataGenerator

        return TestDataGenerator()
    except ImportError:
        # Fallback to enhanced generator if original not available
        return EnhancedTestDataGenerator()


@pytest.fixture
def valid_ipv4_addresses(test_data_generator):
    """Fixture providing valid IPv4 addresses."""
    return test_data_generator.generate_valid_ipv4_addresses()


@pytest.fixture
def private_ipv4_addresses(test_data_generator):
    """Fixture providing private IPv4 addresses."""
    return test_data_generator.generate_private_ipv4_addresses()


@pytest.fixture
def invalid_ip_addresses(test_data_generator):
    """Fixture providing invalid IP addresses."""
    return test_data_generator.generate_invalid_ip_addresses()


@pytest.fixture
def valid_domains(test_data_generator):
    """Fixture providing valid domain names."""
    return test_data_generator.generate_valid_domains()


@pytest.fixture
def invalid_domains(test_data_generator):
    """Fixture providing invalid domain names."""
    return test_data_generator.generate_invalid_domains()


@pytest.fixture
def port_numbers(test_data_generator):
    """Fixture providing categorized port numbers."""
    return test_data_generator.generate_port_numbers()


@pytest.fixture
def temp_directory():
    """Fixture providing temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def test_session_data():
    """Session-scoped fixture for test data that doesn't change."""
    return {
        "timestamp": datetime.now().isoformat(),
        "test_id": f"security_validator_enhanced_test_{random.randint(1000, 9999)}",
        "version": "2.0.0",
        "enhancement_features": [
            "performance_benchmarking",
            "memory_profiling",
            "stress_testing",
            "enhanced_reporting",
        ],
    }


# Enhanced test markers for better organization
# Note: These are registered in pytest_configure function below


# Test result collection hook
def pytest_configure(config):
    """Configure pytest for enhanced testing."""
    config.addinivalue_line(
        "markers", "enhanced: mark test as enhanced with additional monitoring"
    )
    config.addinivalue_line("markers", "stress: mark test as stress testing")
    config.addinivalue_line(
        "markers", "memory: mark test as memory profiling test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as performance benchmark"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add enhanced markers."""
    for item in items:
        # Add enhanced marker to all tests in this enhanced suite
        item.add_marker(pytest.mark.enhanced)

        # Add specific markers based on test names
        if "stress" in item.name.lower() or "bulk" in item.name.lower():
            item.add_marker(pytest.mark.stress)

        if "memory" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.memory)

        if "benchmark" in item.name.lower() or "timing" in item.name.lower():
            item.add_marker(pytest.mark.benchmark)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    if hasattr(session.config, "_test_execution_data"):
        # Save comprehensive test execution data
        execution_data = {
            "session_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "exit_status": exitstatus,
                "total_tests": len(session.config._test_execution_data),
            },
            "test_executions": session.config._test_execution_data,
        }

        # Calculate session statistics
        execution_times = [
            test["execution_time_milliseconds"]
            for test in session.config._test_execution_data
        ]

        if execution_times:
            execution_data["session_statistics"] = {
                "total_execution_time_ms": sum(execution_times),
                "average_execution_time_ms": sum(execution_times)
                / len(execution_times),
                "min_execution_time_ms": min(execution_times),
                "max_execution_time_ms": max(execution_times),
                "slow_tests": [
                    test
                    for test in session.config._test_execution_data
                    if test["execution_time_milliseconds"]
                    > ENHANCED_TEST_CONFIG["performance_threshold_ms"]
                ],
            }

        # Save to file
        output_file = (
            Path(__file__).parent
            / "result_security_validator_2025-08-30_session_data.json"
        )
        with open(output_file, "w") as f:
            json.dump(execution_data, f, indent=2, default=str)
