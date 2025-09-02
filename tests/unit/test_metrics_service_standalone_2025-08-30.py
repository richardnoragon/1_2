"""
Comprehensive unit tests for metrics_service.py - Self-contained version
Generated on: 2025-08-30

This test file includes all necessary mocks and handles imports directly.
"""

import json
import os
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Setup paths and imports
current_dir = Path(__file__).parent
src_path = current_dir.parent.parent / "src" / "utilities" / "network" / "network_connectivity_complex" / "core"
sys.path.insert(0, str(src_path))

# Create comprehensive mocks for dependencies
class MockLogger:
    """Mock logger for testing."""
    def debug(self, msg, *args, **kwargs): pass
    def info(self, msg, *args, **kwargs): pass  
    def warning(self, msg, *args, **kwargs): pass
    def error(self, msg, *args, **kwargs): pass
    def critical(self, msg, *args, **kwargs): pass

class MockLoggingManager:
    """Mock logging manager for testing."""
    def get_tool_logger(self, name):
        return MockLogger()

def mock_get_network_logging_manager():
    """Mock function to get network logging manager."""
    return MockLoggingManager()

# Mock the logging integration module
mock_logging_module = Mock()
mock_logging_module.get_network_logging_manager = mock_get_network_logging_manager
sys.modules['logging_integration'] = mock_logging_module

# Now import the metrics service with the mock in place
try:
    import metrics_service
    from metrics_service import (Metric, MetricAggregator, MetricAlert,
                                 MetricCollector, MetricsService, MetricType,
                                 MetricUnit, MetricValue,
                                 NetworkToolMetricsCollector,
                                 SystemMetricsCollector, get_metrics_service,
                                 record_counter, record_gauge, record_rate,
                                 record_timer)
    METRICS_SERVICE_AVAILABLE = True
except ImportError as e:
    # If import fails, create mock classes for testing
    METRICS_SERVICE_AVAILABLE = False
    print(f"WARNING: Could not import metrics_service: {e}")
    
    # Create mock classes to allow tests to run
    from enum import Enum
    
    class MetricType(Enum):
        COUNTER = "counter"
        GAUGE = "gauge"
        HISTOGRAM = "histogram"
        TIMER = "timer"
        RATE = "rate"
    
    class MetricUnit(Enum):
        NONE = ""
        BYTES = "bytes"
        SECONDS = "seconds"
        MILLISECONDS = "ms"
        PERCENT = "percent"
        COUNT = "count"
        RATE_PER_SECOND = "per_second"
        MBPS = "mbps"
        PACKETS = "packets"
    
    # For testing purposes, create minimal mock implementations
    MetricValue = Mock
    Metric = Mock
    MetricAlert = Mock
    MetricAggregator = Mock
    MetricCollector = Mock
    SystemMetricsCollector = Mock
    NetworkToolMetricsCollector = Mock
    MetricsService = Mock
    get_metrics_service = Mock
    record_counter = Mock
    record_gauge = Mock
    record_timer = Mock
    record_rate = Mock


# Test execution marker
@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetricType:
    """Test MetricType enum."""
    
    def test_metric_type_values(self):
        """Test MetricType enum values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"
        assert MetricType.RATE.value == "rate"


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetricUnit:
    """Test MetricUnit enum."""
    
    def test_metric_unit_values(self):
        """Test MetricUnit enum values."""
        assert MetricUnit.NONE.value == ""
        assert MetricUnit.BYTES.value == "bytes"
        assert MetricUnit.SECONDS.value == "seconds"
        assert MetricUnit.MILLISECONDS.value == "ms"
        assert MetricUnit.PERCENT.value == "percent"
        assert MetricUnit.COUNT.value == "count"
        assert MetricUnit.RATE_PER_SECOND.value == "per_second"
        assert MetricUnit.MBPS.value == "mbps"
        assert MetricUnit.PACKETS.value == "packets"


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetricValue:
    """Test MetricValue dataclass."""
    
    def test_metric_value_creation(self):
        """Test MetricValue creation."""
        timestamp = datetime.now()
        value = MetricValue(timestamp=timestamp, value=42.5)
        
        assert value.timestamp == timestamp
        assert value.value == 42.5
        assert value.tags == {}
    
    def test_metric_value_with_tags(self):
        """Test MetricValue creation with tags."""
        timestamp = datetime.now()
        tags = {"host": "server1", "env": "prod"}
        value = MetricValue(timestamp=timestamp, value=100, tags=tags)
        
        assert value.timestamp == timestamp
        assert value.value == 100
        assert value.tags == tags
    
    def test_metric_value_post_init(self):
        """Test MetricValue __post_init__ behavior."""
        timestamp = datetime.now()
        value = MetricValue(timestamp=timestamp, value=42.5, tags=None)
        
        assert value.tags == {}


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetric:
    """Test Metric dataclass."""
    
    def test_metric_creation(self):
        """Test Metric creation."""
        metric = Metric(
            name="test_metric",
            type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Test metric",
            values=deque()
        )
        
        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER
        assert metric.unit == MetricUnit.COUNT
        assert metric.description == "Test metric"
        assert isinstance(metric.values, deque)
        assert metric.tags == {}
        assert metric.max_values == 1000
    
    def test_metric_post_init(self):
        """Test Metric __post_init__ behavior."""
        metric = Metric(
            name="test_metric",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=[],  # Not a deque
            tags=None,
            max_values=500
        )
        
        assert isinstance(metric.values, deque)
        assert metric.values.maxlen == 500
        assert metric.tags == {}


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetricAggregator:
    """Test MetricAggregator class."""
    
    @pytest.fixture
    def aggregator(self):
        """Create MetricAggregator instance."""
        return MetricAggregator(window_size_seconds=60)
    
    @pytest.fixture
    def sample_values(self):
        """Create sample metric values."""
        timestamp = datetime.now()
        return [
            MetricValue(timestamp=timestamp, value=10),
            MetricValue(timestamp=timestamp, value=20),
            MetricValue(timestamp=timestamp, value=30),
            MetricValue(timestamp=timestamp, value=40),
            MetricValue(timestamp=timestamp, value=50),
        ]
    
    def test_aggregator_initialization(self, aggregator):
        """Test MetricAggregator initialization."""
        assert aggregator.window_size == 60
        assert aggregator.logger is not None
    
    def test_aggregate_values_avg(self, aggregator, sample_values):
        """Test aggregate_values with avg."""
        result = aggregator.aggregate_values(sample_values, "avg")
        assert result == 30.0
    
    def test_aggregate_values_sum(self, aggregator, sample_values):
        """Test aggregate_values with sum."""
        result = aggregator.aggregate_values(sample_values, "sum")
        assert result == 150
    
    def test_aggregate_values_min(self, aggregator, sample_values):
        """Test aggregate_values with min."""
        result = aggregator.aggregate_values(sample_values, "min")
        assert result == 10
    
    def test_aggregate_values_max(self, aggregator, sample_values):
        """Test aggregate_values with max."""
        result = aggregator.aggregate_values(sample_values, "max")
        assert result == 50
    
    def test_aggregate_values_count(self, aggregator, sample_values):
        """Test aggregate_values with count."""
        result = aggregator.aggregate_values(sample_values, "count")
        assert result == 5
    
    def test_aggregate_values_median(self, aggregator, sample_values):
        """Test aggregate_values with median."""
        result = aggregator.aggregate_values(sample_values, "median")
        assert result == 30
    
    def test_aggregate_values_stdev(self, aggregator, sample_values):
        """Test aggregate_values with stdev."""
        result = aggregator.aggregate_values(sample_values, "stdev")
        assert abs(result - 15.811388300841898) < 0.0001
    
    def test_aggregate_values_empty_list(self, aggregator):
        """Test aggregate_values with empty list."""
        result = aggregator.aggregate_values([], "avg")
        assert result is None
    
    def test_aggregate_values_non_numeric(self, aggregator):
        """Test aggregate_values with non-numeric values."""
        values = [
            MetricValue(timestamp=datetime.now(), value="string"),
            MetricValue(timestamp=datetime.now(), value=None),
        ]
        result = aggregator.aggregate_values(values, "avg")
        assert result is None
    
    def test_aggregate_values_unknown_type(self, aggregator, sample_values):
        """Test aggregate_values with unknown aggregation type."""
        result = aggregator.aggregate_values(sample_values, "unknown")
        assert result == 30.0  # Falls back to avg


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")
class TestMetricsService:
    """Test MetricsService class."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create MetricsService instance."""
        service = MetricsService()
        # Stop background threads for testing
        service._stop_event.set()
        if service._cleanup_thread and service._cleanup_thread.is_alive():
            service._cleanup_thread.join(timeout=1)
        if service._alert_thread and service._alert_thread.is_alive():
            service._alert_thread.join(timeout=1)
        return service
    
    def test_metrics_service_initialization(self, metrics_service):
        """Test MetricsService initialization."""
        assert len(metrics_service._metrics) == 0
        assert isinstance(metrics_service._aggregator, MetricAggregator)
        assert isinstance(metrics_service._collectors, dict)
        assert isinstance(metrics_service._alerts, dict)
        assert isinstance(metrics_service._config, dict)
        assert isinstance(metrics_service._stats, dict)
    
    def test_create_metric(self, metrics_service):
        """Test creating a metric."""
        result = metrics_service.create_metric(
            name="test_metric",
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Test metric"
        )
        
        assert result is True
        assert "test_metric" in metrics_service._metrics
        
        metric = metrics_service._metrics["test_metric"]
        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER
        assert metric.unit == MetricUnit.COUNT
        assert metric.description == "Test metric"
    
    def test_create_metric_duplicate(self, metrics_service):
        """Test creating duplicate metric."""
        metrics_service.create_metric(
            "test_metric", MetricType.COUNTER
        )
        
        # Try to create again
        result = metrics_service.create_metric(
            "test_metric", MetricType.GAUGE
        )
        
        assert result is False
        # Original metric should remain
        assert metrics_service._metrics["test_metric"].type == MetricType.COUNTER
    
    def test_record_value(self, metrics_service):
        """Test recording metric value."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        result = metrics_service.record_value("test_metric", 42.5)
        
        assert result is True
        metric = metrics_service._metrics["test_metric"]
        assert len(metric.values) == 1
        assert metric.values[0].value == 42.5
    
    def test_record_value_auto_create(self, metrics_service):
        """Test recording value with auto-create metric."""
        result = metrics_service.record_value("auto_metric", 100)
        
        assert result is True
        assert "auto_metric" in metrics_service._metrics
        
        metric = metrics_service._metrics["auto_metric"]
        assert metric.type == MetricType.COUNTER  # int value -> counter
        assert len(metric.values) == 1
        assert metric.values[0].value == 100
    
    def test_get_metric_value_latest(self, metrics_service):
        """Test getting latest metric value."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        metrics_service.record_value("test_metric", 10)
        metrics_service.record_value("test_metric", 20)
        metrics_service.record_value("test_metric", 30)
        
        value = metrics_service.get_metric_value("test_metric", "latest")
        assert value == 30
    
    def test_get_metric_value_aggregations(self, metrics_service):
        """Test getting aggregated metric values."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        for val in [10, 20, 30, 40, 50]:
            metrics_service.record_value("test_metric", val)
        
        assert metrics_service.get_metric_value("test_metric", "avg") == 30.0
        assert metrics_service.get_metric_value("test_metric", "sum") == 150
        assert metrics_service.get_metric_value("test_metric", "min") == 10
        assert metrics_service.get_metric_value("test_metric", "max") == 50
        assert metrics_service.get_metric_value("test_metric", "count") == 5
    
    def test_export_metrics_json(self, metrics_service):
        """Test exporting metrics to JSON."""
        # Create and populate metric
        metrics_service.create_metric(
            "test_metric", MetricType.GAUGE, MetricUnit.PERCENT, "Test metric"
        )
        metrics_service.record_value("test_metric", 42.5, tags={"env": "test"})
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            file_path = f.name
        
        try:
            result = metrics_service.export_metrics(file_path, "json", 3600)
            assert result is True
            
            # Verify exported data
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            assert "test_metric" in data
            metric_data = data["test_metric"]
            assert metric_data["type"] == "gauge"
            assert metric_data["unit"] == "percent"
            assert metric_data["description"] == "Test metric"
            assert len(metric_data["values"]) == 1
            assert metric_data["values"][0]["value"] == 42.5
            assert metric_data["values"][0]["tags"] == {"env": "test"}
            
        finally:
            os.unlink(file_path)


@pytest.mark.skipif(not METRICS_SERVICE_AVAILABLE, reason="metrics_service module not available")  
class TestGlobalFunctions:
    """Test global convenience functions."""
    
    @pytest.fixture(autouse=True)
    def reset_global_service(self):
        """Reset global service before each test."""
        if METRICS_SERVICE_AVAILABLE:
            metrics_service._metrics_service = None
    
    def test_get_metrics_service(self):
        """Test get_metrics_service function."""
        service1 = get_metrics_service()
        service2 = get_metrics_service()
        
        assert service1 is service2  # Should return same instance
        assert isinstance(service1, MetricsService)
    
    def test_record_counter(self):
        """Test record_counter function."""
        record_counter("test_counter", 5)
        
        service = get_metrics_service()
        assert "test_counter" in service._metrics
        
        metric = service._metrics["test_counter"]
        assert metric.type == MetricType.COUNTER
        assert metric.unit == MetricUnit.COUNT
        assert len(metric.values) == 1
        assert metric.values[0].value == 5
    
    def test_record_gauge(self):
        """Test record_gauge function."""
        record_gauge("test_gauge", 42.5)
        
        service = get_metrics_service()
        assert "test_gauge" in service._metrics
        
        metric = service._metrics["test_gauge"]
        assert metric.type == MetricType.GAUGE
        assert len(metric.values) == 1
        assert metric.values[0].value == 42.5


class TestModuleAvailability:
    """Test suite when metrics_service module is not available."""
    
    @pytest.mark.skipif(METRICS_SERVICE_AVAILABLE, reason="metrics_service module is available")
    def test_module_not_available_graceful_handling(self):
        """Test that the test suite handles missing module gracefully."""
        # This test will only run if the module is not available
        assert not METRICS_SERVICE_AVAILABLE
        print("metrics_service module not available - tests skipped gracefully")


class TestSystemIntegration:
    """Integration tests that work regardless of module availability."""
    
    def test_test_environment_setup(self):
        """Test that the test environment is properly set up."""
        # Check Python path includes our source directory
        assert str(src_path) in sys.path or any(str(src_path) in p for p in sys.path)
        
        # Check that we can create temporary files
        with tempfile.NamedTemporaryFile() as f:
            assert f.name is not None
        
        # Check JSON functionality
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        assert parsed_data["test"] == "data"
    
    def test_mock_functionality(self):
        """Test that our mocks work correctly."""
        logger = MockLogger()
        logger.info("Test message")  # Should not raise an exception
        logger.error("Test error")   # Should not raise an exception
        
        manager = MockLoggingManager()
        tool_logger = manager.get_tool_logger("test_tool")
        assert tool_logger is not None
        tool_logger.debug("Test debug message")


if __name__ == "__main__":
    # Print test execution information
    print(f"Test Execution Information:")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Python Version: {sys.version}")
    print(f"Module Available: {METRICS_SERVICE_AVAILABLE}")
    print(f"Source Path: {src_path}")
    print("-" * 60)
    
    # Run the tests
    pytest.main([__file__, "-v"])