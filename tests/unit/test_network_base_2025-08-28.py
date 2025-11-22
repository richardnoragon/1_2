"""
Comprehensive unit tests for network_base.py
Created: 2025-08-28
Target: src/utilities/network/network_connectivity_complex/core/network_base.py

This module provides comprehensive unit tests for the NetworkToolBase class
and related components including NetworkOperationStatus, NetworkAlertLevel,
and NetworkOperationResult. Tests cover all methods, error conditions,
and edge cases with proper mocking and assertions.
"""

import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

# Add source path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Import the modules under test
try:
    from src.tools.network.network_connectivity_complex.core.network_base import (
        NetworkAlertLevel,
        NetworkOperationResult,
        NetworkOperationStatus,
        NetworkToolBase,
    )
except ImportError as e:
    pytest.skip(f"Could not import network_base module: {e}", allow_module_level=True)


class TestNetworkOperationStatus:
    """Test cases for NetworkOperationStatus enum."""

    def test_enum_values(self):
        """Test that all enum values are correct."""
        assert NetworkOperationStatus.IDLE.value == "idle"
        assert NetworkOperationStatus.STARTING.value == "starting"
        assert NetworkOperationStatus.RUNNING.value == "running"
        assert NetworkOperationStatus.STOPPING.value == "stopping"
        assert NetworkOperationStatus.COMPLETED.value == "completed"
        assert NetworkOperationStatus.ERROR.value == "error"

    def test_enum_completeness(self):
        """Test that all expected enum values exist."""
        expected_values = [
            "idle",
            "starting",
            "running",
            "stopping",
            "completed",
            "error",
        ]
        actual_values = [status.value for status in NetworkOperationStatus]
        assert set(actual_values) == set(expected_values)


class TestNetworkAlertLevel:
    """Test cases for NetworkAlertLevel enum."""

    def test_enum_values(self):
        """Test that all enum values are correct."""
        assert NetworkAlertLevel.INFO.value == "info"
        assert NetworkAlertLevel.WARNING.value == "warning"
        assert NetworkAlertLevel.CRITICAL.value == "critical"

    def test_enum_completeness(self):
        """Test that all expected enum values exist."""
        expected_values = ["info", "warning", "critical"]
        actual_values = [level.value for level in NetworkAlertLevel]
        assert set(actual_values) == set(expected_values)


class TestNetworkOperationResult:
    """Test cases for NetworkOperationResult dataclass."""

    def test_basic_creation(self):
        """Test basic creation of NetworkOperationResult."""
        result = NetworkOperationResult(
            success=True, operation_type="test_operation", data={"test": "data"}
        )

        assert result.success is True
        assert result.operation_type == "test_operation"
        assert result.data == {"test": "data"}
        assert result.error_message is None
        assert result.duration_ms is None
        assert isinstance(result.timestamp, datetime)

    def test_creation_with_all_fields(self):
        """Test creation with all fields specified."""
        test_time = datetime(2025, 8, 28, 12, 0, 0)
        result = NetworkOperationResult(
            success=False,
            operation_type="failed_operation",
            data={"error": "details"},
            error_message="Operation failed",
            timestamp=test_time,
            duration_ms=1500.5,
        )

        assert result.success is False
        assert result.operation_type == "failed_operation"
        assert result.data == {"error": "details"}
        assert result.error_message == "Operation failed"
        assert result.timestamp == test_time
        assert result.duration_ms == 1500.5

    def test_timestamp_auto_creation(self):
        """Test that timestamp is automatically created when not provided."""
        before_creation = datetime.now()
        result = NetworkOperationResult(success=True, operation_type="test", data={})
        after_creation = datetime.now()

        assert before_creation <= result.timestamp <= after_creation

    def test_timestamp_preservation(self):
        """Test that provided timestamp is preserved."""
        test_time = datetime(2025, 1, 1, 0, 0, 0)
        result = NetworkOperationResult(
            success=True, operation_type="test", data={}, timestamp=test_time
        )

        assert result.timestamp == test_time


class MockNetworkTool(NetworkToolBase):
    """Mock implementation of NetworkToolBase for testing."""

    def __init__(self, tool_name: str = "MockTool"):
        super().__init__(tool_name)
        self.execute_operation_called = False
        self.execute_operation_kwargs = {}
        self.mock_protocols = ["TCP", "UDP", "HTTP"]
        self.validation_result = True
        self.health_status = {"status": "healthy", "uptime": 100}

    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Mock implementation of execute_operation."""
        self.execute_operation_called = True
        self.execute_operation_kwargs = kwargs

        if kwargs.get("should_fail", False):
            raise Exception("Mock operation failure")

        return NetworkOperationResult(
            success=True,
            operation_type="mock_operation",
            data={"result": "success", "input": kwargs},
        )

    def get_supported_protocols(self) -> List[str]:
        """Mock implementation of get_supported_protocols."""
        return self.mock_protocols

    def validate_parameters(self, **kwargs) -> bool:
        """Mock implementation of validate_parameters."""
        return self.validation_result

    def get_health_status(self) -> Dict[str, Any]:
        """Mock implementation of get_health_status."""
        return self.health_status


class TestNetworkToolBase:
    """Test cases for NetworkToolBase abstract class."""

    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock ConfigManager."""
        mock_config = Mock()
        mock_config.config = {}
        mock_config.get_setting = Mock(return_value=None)
        mock_config.set_setting = Mock()
        return mock_config

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        logger = Mock()
        logger.info = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.debug = Mock()
        return logger

    @pytest.fixture
    def network_tool(self, mock_config_manager, mock_logger):
        """Create a MockNetworkTool instance with mocked dependencies."""
        with patch(
            "src.tools.network.network_connectivity_complex.core.network_base.ConfigManager"
        ) as mock_cm_class, patch(
            "src.tools.network.network_connectivity_complex.core.network_base.logging.getLogger"
        ) as mock_get_logger, patch(
            "src.tools.network.network_connectivity_complex.core.network_base.error_handler"
        ) as mock_error_handler:
            mock_cm_class.return_value = mock_config_manager
            mock_get_logger.return_value = mock_logger

            tool = MockNetworkTool("TestTool")
            tool.config_manager = mock_config_manager
            tool.logger = mock_logger
            return tool

    def test_initialization(self, network_tool):
        """Test proper initialization of NetworkToolBase."""
        assert network_tool.tool_name == "TestTool"
        assert network_tool.status == NetworkOperationStatus.IDLE
        assert network_tool._is_running is False
        assert network_tool._should_stop is False
        assert network_tool._current_operation is None
        assert network_tool._operation_start_time is None
        assert network_tool._current_data == {}
        assert network_tool._historical_data == []
        assert network_tool._max_history_size == 1000
        assert network_tool._error_count == 0
        assert network_tool._max_errors == 10
        assert network_tool._last_error_time is None

    def test_ensure_network_config(self, network_tool):
        """Test _ensure_network_config method."""
        # Mock that network_connectivity doesn't exist
        network_tool.config_manager.config = {}
        network_tool._ensure_network_config()

        # Verify set_setting was called with default config
        network_tool.config_manager.set_setting.assert_called_once()
        call_args = network_tool.config_manager.set_setting.call_args
        assert call_args[0][0] == "network_connectivity"
        assert call_args[0][1] == "general"
        assert "default_timeout" in call_args[0][2]

    def test_start_operation_success(self, network_tool):
        """Test successful operation start."""
        result = network_tool.start_operation("test_op", param1="value1")

        assert result is True
        assert network_tool._current_operation == "test_op"
        assert network_tool.status == NetworkOperationStatus.RUNNING
        assert network_tool._is_running is True

        # Wait for operation to complete
        time.sleep(0.1)

        # Verify operation was executed
        assert network_tool.execute_operation_called is True
        assert network_tool.execute_operation_kwargs == {"param1": "value1"}

    def test_start_operation_validation_failure(self, network_tool):
        """Test operation start with validation failure."""
        network_tool.validation_result = False

        result = network_tool.start_operation("test_op", param1="value1")

        assert result is False
        assert network_tool.status == NetworkOperationStatus.ERROR
        assert network_tool._is_running is False

    def test_start_operation_already_running(self, network_tool):
        """Test starting operation when already running."""
        network_tool._is_running = True

        result = network_tool.start_operation("test_op")

        assert result is False
        network_tool.logger.warning.assert_called_with("Operation is already running")

    def test_stop_operation_success(self, network_tool):
        """Test successful operation stop."""
        # Start an operation first
        network_tool.start_operation("test_op")
        time.sleep(0.05)  # Let it start

        result = network_tool.stop_operation()

        assert result is True
        assert network_tool._is_running is False
        assert network_tool.status == NetworkOperationStatus.IDLE
        assert network_tool._current_operation is None

    def test_stop_operation_not_running(self, network_tool):
        """Test stopping operation when not running."""
        result = network_tool.stop_operation()

        assert result is True
        network_tool.logger.warning.assert_called_with("No operation is running")

    def test_operation_wrapper_success(self, network_tool):
        """Test _operation_wrapper with successful execution."""
        kwargs = {"test_param": "value"}

        # Mock the operation start time
        network_tool._operation_start_time = datetime.now()

        network_tool._operation_wrapper("test_operation", kwargs)

        assert network_tool.status == NetworkOperationStatus.COMPLETED
        assert network_tool.execute_operation_called is True
        assert network_tool.execute_operation_kwargs == kwargs

    def test_operation_wrapper_failure(self, network_tool):
        """Test _operation_wrapper with execution failure."""
        kwargs = {"should_fail": True}

        network_tool._operation_start_time = datetime.now()

        network_tool._operation_wrapper("test_operation", kwargs)

        assert network_tool.status == NetworkOperationStatus.ERROR
        assert network_tool._error_count == 1
        assert network_tool._last_error_time is not None

    def test_handle_operation_error(self, network_tool):
        """Test _handle_operation_error method."""
        test_error = Exception("Test error")

        network_tool._handle_operation_error(test_error, "test_operation")

        assert network_tool._error_count == 1
        assert network_tool._last_error_time is not None
        assert network_tool.status == NetworkOperationStatus.ERROR
        network_tool.logger.error.assert_called()

    def test_get_tool_config(self, network_tool):
        """Test get_tool_config method."""
        network_tool.config_manager.get_setting.return_value = "test_value"

        result = network_tool.get_tool_config("test_key", "default_value")

        assert result == "test_value"
        network_tool.config_manager.get_setting.assert_called_with(
            "network_connectivity", "testtool.test_key", "default_value"
        )

    def test_set_tool_config(self, network_tool):
        """Test set_tool_config method."""
        network_tool.config_manager.get_setting.return_value = {}

        network_tool.set_tool_config("test_key", "test_value")

        network_tool.config_manager.set_setting.assert_called()
        call_args = network_tool.config_manager.set_setting.call_args
        assert call_args[0][0] == "network_connectivity"
        assert call_args[0][1] == "testtool"
        assert call_args[0][2]["test_key"] == "test_value"

    def test_add_data_callback(self, network_tool):
        """Test add_data_callback method."""
        callback = Mock()

        network_tool.add_data_callback(callback)

        assert callback in network_tool._data_callbacks

    def test_add_alert_callback(self, network_tool):
        """Test add_alert_callback method."""
        callback = Mock()

        network_tool.add_alert_callback(callback)

        assert callback in network_tool._alert_callbacks

    def test_notify_data_callbacks(self, network_tool):
        """Test _notify_data_callbacks method."""
        callback1 = Mock()
        callback2 = Mock()
        network_tool.add_data_callback(callback1)
        network_tool.add_data_callback(callback2)

        test_data = {"test": "data"}
        network_tool._notify_data_callbacks(test_data)

        callback1.assert_called_once_with(test_data)
        callback2.assert_called_once_with(test_data)

    def test_notify_data_callbacks_error_handling(self, network_tool):
        """Test _notify_data_callbacks with callback error."""
        failing_callback = Mock(side_effect=Exception("Callback error"))
        working_callback = Mock()

        network_tool.add_data_callback(failing_callback)
        network_tool.add_data_callback(working_callback)

        test_data = {"test": "data"}
        network_tool._notify_data_callbacks(test_data)

        # Should still call working callback despite error in first
        working_callback.assert_called_once_with(test_data)
        network_tool.logger.error.assert_called()

    def test_notify_alert_callbacks(self, network_tool):
        """Test _notify_alert_callbacks method."""
        callback = Mock()
        network_tool.add_alert_callback(callback)

        network_tool._notify_alert_callbacks(
            "test_alert", NetworkAlertLevel.WARNING, "Test message"
        )

        callback.assert_called_once_with(
            "test_alert", NetworkAlertLevel.WARNING, "Test message"
        )

    def test_get_current_data(self, network_tool):
        """Test get_current_data method."""
        test_data = {"current": "data", "value": 123}
        network_tool._current_data = test_data

        result = network_tool.get_current_data()

        assert result == test_data
        assert result is not network_tool._current_data  # Should be a copy

    def test_get_historical_data_all(self, network_tool):
        """Test get_historical_data method without filters."""
        test_data = [
            {"timestamp": "2025-08-28T10:00:00", "value": 1},
            {"timestamp": "2025-08-28T11:00:00", "value": 2},
            {"timestamp": "2025-08-28T12:00:00", "value": 3},
        ]
        network_tool._historical_data = test_data

        result = network_tool.get_historical_data()

        assert result == test_data
        assert result is not network_tool._historical_data  # Should be a copy

    def test_get_historical_data_filtered(self, network_tool):
        """Test get_historical_data method with time filters."""
        test_data = [
            {"timestamp": "2025-08-28T10:00:00", "value": 1},
            {"timestamp": "2025-08-28T11:00:00", "value": 2},
            {"timestamp": "2025-08-28T12:00:00", "value": 3},
        ]
        network_tool._historical_data = test_data

        start_time = datetime(2025, 8, 28, 10, 30, 0)
        end_time = datetime(2025, 8, 28, 11, 30, 0)

        result = network_tool.get_historical_data(start_time, end_time)

        assert len(result) == 1
        assert result[0]["value"] == 2

    def test_store_data(self, network_tool):
        """Test _store_data method."""
        test_data = {"measurement": "test", "value": 42}

        with patch.object(network_tool, "_notify_data_callbacks") as mock_notify:
            network_tool._store_data(test_data)

        # Check current data
        assert network_tool._current_data["measurement"] == "test"
        assert network_tool._current_data["value"] == 42
        assert network_tool._current_data["tool_name"] == "TestTool"
        assert "timestamp" in network_tool._current_data

        # Check historical data
        assert len(network_tool._historical_data) == 1
        assert network_tool._historical_data[0]["measurement"] == "test"

        # Check callback notification
        mock_notify.assert_called_once()

    def test_store_data_history_limit(self, network_tool):
        """Test _store_data method with history size limit."""
        network_tool._max_history_size = 3

        # Add more data than the limit
        for i in range(5):
            network_tool._store_data({"value": i})

        # Should only keep the last 3 entries
        assert len(network_tool._historical_data) == 3
        values = [data["value"] for data in network_tool._historical_data]
        assert values == [2, 3, 4]

    def test_is_running_property(self, network_tool):
        """Test is_running property."""
        assert network_tool.is_running is False

        network_tool._is_running = True
        assert network_tool.is_running is True

    def test_is_healthy_property_basic(self, network_tool):
        """Test is_healthy property with basic conditions."""
        assert network_tool.is_healthy is True

        network_tool.status = NetworkOperationStatus.ERROR
        assert network_tool.is_healthy is False

    def test_is_healthy_property_error_count(self, network_tool):
        """Test is_healthy property with error count threshold."""
        # Set recent error time and high error count
        network_tool._last_error_time = datetime.now()
        network_tool._error_count = 5

        assert network_tool.is_healthy is False

    def test_is_healthy_property_old_errors(self, network_tool):
        """Test is_healthy property with old errors."""
        # Set old error time
        old_time = datetime.now()
        old_time = old_time.replace(hour=old_time.hour - 1)  # 1 hour ago
        network_tool._last_error_time = old_time
        network_tool._error_count = 5

        assert network_tool.is_healthy is True

    def test_get_status_info(self, network_tool):
        """Test get_status_info method."""
        network_tool._current_operation = "test_op"
        network_tool._error_count = 2
        network_tool._last_error_time = datetime(2025, 8, 28, 12, 0, 0)
        network_tool._historical_data = [{"data": 1}, {"data": 2}]

        result = network_tool.get_status_info()

        expected_keys = [
            "tool_name",
            "status",
            "is_running",
            "is_healthy",
            "current_operation",
            "error_count",
            "last_error_time",
            "data_points",
            "supported_protocols",
        ]

        for key in expected_keys:
            assert key in result

        assert result["tool_name"] == "TestTool"
        assert result["status"] == NetworkOperationStatus.IDLE.value
        assert result["current_operation"] == "test_op"
        assert result["error_count"] == 2
        assert result["data_points"] == 2
        assert result["supported_protocols"] == ["TCP", "UDP", "HTTP"]

    def test_threading_safety(self, network_tool):
        """Test threading safety with concurrent operations."""
        results = []
        errors = []

        def worker():
            try:
                for i in range(10):
                    network_tool._store_data(
                        {"worker": threading.current_thread().name, "iteration": i}
                    )
                    time.sleep(0.001)
                results.append("success")
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, name=f"Worker-{i}")
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0
        assert len(results) == 3

        # Verify data was stored (should have 30 entries)
        assert len(network_tool._historical_data) == 30

    def test_signal_emission(self, network_tool):
        """Test PyQt signal emission."""
        # Mock the signals
        network_tool.progress_updated = Mock()
        network_tool.operation_complete = Mock()
        network_tool.error_occurred = Mock()
        network_tool.status_changed = Mock()
        network_tool.data_updated = Mock()
        network_tool.alert_triggered = Mock()

        # Test data update signal
        test_data = {"test": "data"}
        network_tool._store_data(test_data)
        network_tool.data_updated.emit.assert_called()

        # Test alert signal
        network_tool._notify_alert_callbacks(
            "test_alert", NetworkAlertLevel.INFO, "Test message"
        )
        network_tool.alert_triggered.emit.assert_called_with(
            "info", "test_alert", "Test message"
        )


class TestNetworkToolBaseEdgeCases:
    """Test edge cases and error conditions for NetworkToolBase."""

    @pytest.fixture
    def network_tool(self):
        """Create a MockNetworkTool with minimal mocking."""
        with patch(
            "src.tools.network.network_connectivity_complex.core.network_base.ConfigManager"
        ), patch(
            "src.tools.network.network_connectivity_complex.core.network_base.logging.getLogger"
        ), patch(
            "src.tools.network.network_connectivity_complex.core.network_base.error_handler"
        ):
            return MockNetworkTool("EdgeCaseTool")

    def test_empty_data_storage(self, network_tool):
        """Test storing empty data."""
        network_tool._store_data({})

        assert len(network_tool._historical_data) == 1
        assert "timestamp" in network_tool._historical_data[0]
        assert "tool_name" in network_tool._historical_data[0]

    def test_none_data_handling(self, network_tool):
        """Test handling of None values in data."""
        test_data = {"value": None, "status": "unknown"}
        network_tool._store_data(test_data)

        assert network_tool._current_data["value"] is None
        assert network_tool._current_data["status"] == "unknown"

    def test_large_data_handling(self, network_tool):
        """Test handling of large data sets."""
        large_data = {"large_list": list(range(10000))}
        network_tool._store_data(large_data)

        assert len(network_tool._current_data["large_list"]) == 10000

    def test_unicode_data_handling(self, network_tool):
        """Test handling of unicode data."""
        unicode_data = {
            "message": "测试数据 🚀",
            "emoji": "🌟⭐✨",
            "special_chars": "αβγδε",
        }
        network_tool._store_data(unicode_data)

        assert network_tool._current_data["message"] == "测试数据 🚀"
        assert network_tool._current_data["emoji"] == "🌟⭐✨"

    def test_rapid_operation_starts(self, network_tool):
        """Test rapid successive operation starts."""
        # First operation should succeed
        result1 = network_tool.start_operation("op1")
        assert result1 is True

        # Immediate second operation should fail
        result2 = network_tool.start_operation("op2")
        assert result2 is False

        # Stop and start again should work
        network_tool.stop_operation()
        time.sleep(0.1)
        result3 = network_tool.start_operation("op3")
        assert result3 is True

    def test_stop_before_start(self, network_tool):
        """Test stopping operation before starting any."""
        result = network_tool.stop_operation()
        assert result is True  # Should succeed gracefully

    def test_multiple_stops(self, network_tool):
        """Test multiple stop calls."""
        network_tool.start_operation("test_op")
        time.sleep(0.05)

        result1 = network_tool.stop_operation()
        result2 = network_tool.stop_operation()  # Second stop

        assert result1 is True
        assert result2 is True

    def test_callback_exception_isolation(self, network_tool):
        """Test that callback exceptions don't affect other callbacks."""
        good_callback = Mock()
        bad_callback = Mock(side_effect=Exception("Callback failed"))
        another_good_callback = Mock()

        network_tool.add_data_callback(good_callback)
        network_tool.add_data_callback(bad_callback)
        network_tool.add_data_callback(another_good_callback)

        test_data = {"test": "data"}
        network_tool._store_data(test_data)

        # All callbacks should be called despite the exception
        good_callback.assert_called_once_with(test_data)
        bad_callback.assert_called_once_with(test_data)
        another_good_callback.assert_called_once_with(test_data)


class TestNetworkToolBasePerformance:
    """Performance tests for NetworkToolBase."""

    @pytest.fixture
    def network_tool(self):
        """Create a MockNetworkTool for performance testing."""
        with patch(
            "src.tools.network.network_connectivity_complex.core.network_base.ConfigManager"
        ), patch(
            "src.tools.network.network_connectivity_complex.core.network_base.logging.getLogger"
        ), patch(
            "src.tools.network.network_connectivity_complex.core.network_base.error_handler"
        ):
            return MockNetworkTool("PerformanceTool")

    def test_large_history_performance(self, network_tool):
        """Test performance with large historical data."""
        start_time = time.time()

        # Store 1000 data points
        for i in range(1000):
            network_tool._store_data({"index": i, "value": i * 2})

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0  # 5 seconds
        assert len(network_tool._historical_data) == 1000

    def test_concurrent_data_storage(self, network_tool):
        """Test concurrent data storage performance."""
        import concurrent.futures

        def store_data_batch(start_index):
            for i in range(start_index, start_index + 100):
                network_tool._store_data({"batch": start_index, "index": i})

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(0, 500, 100):
                future = executor.submit(store_data_batch, i)
                futures.append(future)

            # Wait for all to complete
            for future in concurrent.futures.as_completed(futures):
                future.result()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 10.0  # 10 seconds
        assert len(network_tool._historical_data) == 500

    def test_memory_usage_large_dataset(self, network_tool):
        """Test memory usage with large dataset."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Store large amount of data
        for i in range(5000):
            large_data = {
                "index": i,
                "data": [j for j in range(100)],  # 100 integers per entry
                "metadata": f"entry_{i}_with_long_description",
            }
            network_tool._store_data(large_data)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100 * 1024 * 1024


# Test fixtures and utilities
@pytest.fixture(scope="session")
def test_execution_metadata():
    """Provide metadata about the test execution."""
    return {
        "test_file": "test_network_base_2025-08-28.py",
        "target_module": "network_base.py",
        "execution_date": "2025-08-28",
        "timestamp": datetime.now().isoformat(),
        "framework": "pytest",
        "test_categories": [
            "unit_tests",
            "edge_cases",
            "performance_tests",
            "threading_tests",
            "signal_tests",
        ],
    }


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
