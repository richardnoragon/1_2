"""Unit tests for NetworkToolBase class."""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ...core.network_base import NetworkToolBase, ToolStatus


class TestNetworkTool(NetworkToolBase):
    """Test implementation of NetworkToolBase for testing."""
    
    def __init__(self, tool_name="TestTool"):
        super().__init__(tool_name)
        self.test_operation_called = False
        self.test_operation_result = None
    
    def _perform_operation(self, operation_data):
        """Test operation implementation."""
        self.test_operation_called = True
        self.test_operation_result = operation_data
        time.sleep(0.1)  # Simulate work
        return {"result": "success", "data": operation_data}


class TestNetworkToolBase:
    """Test NetworkToolBase functionality."""
    
    @pytest.fixture
    def network_tool(self):
        """Create a test network tool instance."""
        return TestNetworkTool()
    
    def test_initialization(self, network_tool):
        """Test tool initialization."""
        assert network_tool.tool_name == "TestTool"
        assert network_tool.status == ToolStatus.IDLE
        assert network_tool.progress == 0
        assert network_tool.error_message == ""
        assert not network_tool.is_running
        assert network_tool.logger is not None
    
    def test_status_property(self, network_tool):
        """Test status property getter and setter."""
        # Test initial status
        assert network_tool.status == ToolStatus.IDLE
        
        # Test status change
        network_tool.status = ToolStatus.RUNNING
        assert network_tool.status == ToolStatus.RUNNING
        
        # Test invalid status (should raise ValueError)
        with pytest.raises(ValueError):
            network_tool.status = "INVALID_STATUS"
    
    def test_progress_property(self, network_tool):
        """Test progress property getter and setter."""
        # Test initial progress
        assert network_tool.progress == 0
        
        # Test valid progress values
        network_tool.progress = 50
        assert network_tool.progress == 50
        
        network_tool.progress = 100
        assert network_tool.progress == 100
        
        # Test invalid progress values
        with pytest.raises(ValueError):
            network_tool.progress = -1
        
        with pytest.raises(ValueError):
            network_tool.progress = 101
    
    def test_is_running_property(self, network_tool):
        """Test is_running property."""
        # Initially not running
        assert not network_tool.is_running
        
        # Set to running status
        network_tool.status = ToolStatus.RUNNING
        assert network_tool.is_running
        
        # Set to other statuses
        network_tool.status = ToolStatus.COMPLETED
        assert not network_tool.is_running
        
        network_tool.status = ToolStatus.ERROR
        assert not network_tool.is_running
    
    def test_start_operation_sync(self, network_tool):
        """Test synchronous operation start."""
        operation_data = {"test": "data"}
        
        # Start operation synchronously
        result = network_tool.start_operation(operation_data, async_mode=False)
        
        # Verify operation was called
        assert network_tool.test_operation_called
        assert network_tool.test_operation_result == operation_data
        assert result["result"] == "success"
        assert result["data"] == operation_data
        
        # Verify status
        assert network_tool.status == ToolStatus.COMPLETED
        assert network_tool.progress == 100
    
    def test_start_operation_async(self, network_tool):
        """Test asynchronous operation start."""
        operation_data = {"test": "async_data"}
        
        # Start operation asynchronously
        result = network_tool.start_operation(operation_data, async_mode=True)
        
        # Should return immediately
        assert result is None
        assert network_tool.status == ToolStatus.RUNNING
        
        # Wait for completion
        timeout = 5.0
        start_time = time.time()
        while network_tool.is_running and time.time() - start_time < timeout:
            time.sleep(0.01)
        
        # Verify operation completed
        assert not network_tool.is_running
        assert network_tool.status == ToolStatus.COMPLETED
        assert network_tool.test_operation_called
        assert network_tool.test_operation_result == operation_data
    
    def test_stop_operation(self, network_tool):
        """Test operation stopping."""
        # Start async operation
        network_tool.start_operation({"test": "stop_data"}, async_mode=True)
        
        # Verify it's running
        assert network_tool.is_running
        
        # Stop operation
        network_tool.stop_operation()
        
        # Wait a bit for stop to take effect
        time.sleep(0.2)
        
        # Verify it stopped
        assert not network_tool.is_running
        assert network_tool.status == ToolStatus.STOPPED
    
    def test_reset_operation(self, network_tool):
        """Test operation reset."""
        # Set some state
        network_tool.status = ToolStatus.ERROR
        network_tool.progress = 75
        network_tool.error_message = "Test error"
        
        # Reset
        network_tool.reset()
        
        # Verify reset state
        assert network_tool.status == ToolStatus.IDLE
        assert network_tool.progress == 0
        assert network_tool.error_message == ""
        assert not network_tool.is_running
    
    def test_signal_emission(self, network_tool):
        """Test signal emission."""
        # Track signal emissions
        status_signals = []
        progress_signals = []
        error_signals = []
        
        def on_status_changed(status):
            status_signals.append(status)
        
        def on_progress_updated(progress):
            progress_signals.append(progress)
        
        def on_error_occurred(error):
            error_signals.append(error)
        
        # Connect signals
        network_tool.status_changed.connect(on_status_changed)
        network_tool.progress_updated.connect(on_progress_updated)
        network_tool.error_occurred.connect(on_error_occurred)
        
        # Change status
        network_tool.status = ToolStatus.RUNNING
        assert ToolStatus.RUNNING in status_signals
        
        # Update progress
        network_tool.progress = 50
        assert 50 in progress_signals
        
        # Set error
        network_tool._set_error("Test error")
        assert "Test error" in error_signals
        assert network_tool.status == ToolStatus.ERROR
    
    def test_concurrent_operations(self, network_tool):
        """Test that concurrent operations are handled properly."""
        # Start first operation
        network_tool.start_operation({"test": "first"}, async_mode=True)
        
        # Try to start second operation while first is running
        with pytest.raises(RuntimeError, match="already running"):
            network_tool.start_operation({"test": "second"}, async_mode=False)
        
        # Stop first operation
        network_tool.stop_operation()
        time.sleep(0.1)
        
        # Now second operation should work
        result = network_tool.start_operation({"test": "second"}, async_mode=False)
        assert result["data"]["test"] == "second"
    
    def test_error_handling(self, network_tool):
        """Test error handling in operations."""
        # Create a tool that raises an exception
        class ErrorTool(NetworkToolBase):
            def _perform_operation(self, operation_data):
                raise ValueError("Test error")
        
        error_tool = ErrorTool("ErrorTool")
        
        # Test synchronous error handling
        result = error_tool.start_operation({"test": "error"}, async_mode=False)
        
        assert result is None
        assert error_tool.status == ToolStatus.ERROR
        assert "Test error" in error_tool.error_message
    
    def test_thread_safety(self, network_tool):
        """Test thread safety of the tool."""
        results = []
        errors = []
        
        def worker(data):
            try:
                # Each thread gets its own tool instance
                tool = TestNetworkTool(f"TestTool_{data}")
                result = tool.start_operation({"worker": data}, async_mode=False)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0
        assert len(results) == 5
        
        # Verify each result is correct
        for i, result in enumerate(results):
            assert result["data"]["worker"] == i
    
    def test_logging_integration(self, network_tool):
        """Test logging integration."""
        with patch.object(network_tool.logger, 'info') as mock_info, \
             patch.object(network_tool.logger, 'error') as mock_error:
            
            # Start operation (should log)
            network_tool.start_operation({"test": "logging"}, async_mode=False)
            
            # Verify logging calls
            mock_info.assert_called()
            
            # Test error logging
            network_tool._set_error("Test error")
            mock_error.assert_called()
    
    def test_performance_tracking(self, network_tool):
        """Test performance tracking."""
        # Start operation
        start_time = time.time()
        network_tool.start_operation({"test": "performance"}, async_mode=False)
        end_time = time.time()
        
        # Verify timing is reasonable
        duration = end_time - start_time
        assert duration >= 0.1  # Should take at least 0.1s due to sleep
        assert duration < 1.0   # Should not take too long
    
    def test_cleanup_on_destruction(self, network_tool):
        """Test cleanup when tool is destroyed."""
        # Start async operation
        network_tool.start_operation({"test": "cleanup"}, async_mode=True)
        
        # Verify it's running
        assert network_tool.is_running
        
        # Delete the tool (should trigger cleanup)
        tool_id = id(network_tool)
        del network_tool
        
        # Give some time for cleanup
        time.sleep(0.2)
        
        # Note: We can't directly verify cleanup since the object is deleted,
        # but this test ensures no exceptions are raised during cleanup


class TestToolStatus:
    """Test ToolStatus enum."""
    
    def test_status_values(self):
        """Test status enum values."""
        assert ToolStatus.IDLE.value == "idle"
        assert ToolStatus.RUNNING.value == "running"
        assert ToolStatus.COMPLETED.value == "completed"
        assert ToolStatus.ERROR.value == "error"
        assert ToolStatus.STOPPED.value == "stopped"
    
    def test_status_comparison(self):
        """Test status comparison."""
        assert ToolStatus.IDLE == ToolStatus.IDLE
        assert ToolStatus.IDLE != ToolStatus.RUNNING
        
        # Test string comparison
        assert ToolStatus.IDLE.value == "idle"
        assert ToolStatus.RUNNING.value == "running"


class TestNetworkToolBaseIntegration:
    """Integration tests for NetworkToolBase with other components."""
    
    def test_config_integration(self):
        """Test integration with configuration service."""
        with patch('network_connectivity.core.network_base.get_config_service') as mock_get_config:
            mock_config_service = Mock()
            mock_config_service.get_setting.return_value = 10000
            mock_get_config.return_value = mock_config_service
            
            tool = TestNetworkTool()
            
            # Verify config service was called during initialization
            mock_get_config.assert_called_once()
    
    def test_logging_integration(self):
        """Test integration with logging service."""
        with patch('network_connectivity.core.network_base.get_logging_service') as mock_get_logging:
            mock_logging_service = Mock()
            mock_logger = Mock()
            mock_logging_service.get_logger.return_value = mock_logger
            mock_get_logging.return_value = mock_logging_service
            
            tool = TestNetworkTool()
            
            # Verify logging service was called during initialization
            mock_get_logging.assert_called_once()
            mock_logging_service.get_logger.assert_called_once()
    
    def test_metrics_integration(self):
        """Test integration with metrics service."""
        with patch('network_connectivity.core.network_base.get_metrics_service') as mock_get_metrics:
            mock_metrics_service = Mock()
            mock_get_metrics.return_value = mock_metrics_service
            
            tool = TestNetworkTool()
            tool.start_operation({"test": "metrics"}, async_mode=False)
            
            # Verify metrics service was used
            mock_get_metrics.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])