"""
Comprehensive unit tests for metrics_service.py
Generated on: 2025-08-30
"""

import json
import os
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

"""
Comprehensive unit tests for metrics_service.py
Generated on: 2025-08-30
"""

import json
import os
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Import with proper mocking via conftest.py fixtures
with patch('logging_integration.get_network_logging_manager') as mock_logging:
    # Set up mock before import
    class MockLogger:
        def debug(self, msg, *args, **kwargs): pass
        def info(self, msg, *args, **kwargs): pass  
        def warning(self, msg, *args, **kwargs): pass
        def error(self, msg, *args, **kwargs): pass
        def critical(self, msg, *args, **kwargs): pass

    class MockLoggingManager:
        def get_tool_logger(self, name):
            return MockLogger()
    
    mock_logging.return_value = MockLoggingManager()
    
    # Now import metrics_service
    from metrics_service import (Metric, MetricAggregator, MetricAlert,
                                 MetricCollector, MetricsService, MetricType,
                                 MetricUnit, MetricValue,
                                 NetworkToolMetricsCollector,
                                 SystemMetricsCollector, get_metrics_service,
                                 record_counter, record_gauge, record_rate,
                                 record_timer)


class TestMetricType:
    """Test MetricType enum."""
    
    def test_metric_type_values(self):
        """Test MetricType enum values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"
        assert MetricType.RATE.value == "rate"


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


class TestMetricAlert:
    """Test MetricAlert dataclass."""
    
    def test_metric_alert_creation(self):
        """Test MetricAlert creation."""
        alert = MetricAlert(
            metric_name="cpu_usage",
            condition="gt",
            threshold=80.0
        )
        
        assert alert.metric_name == "cpu_usage"
        assert alert.condition == "gt"
        assert alert.threshold == 80.0
        assert alert.duration_seconds == 60
        assert alert.enabled is True
        assert alert.last_triggered is None
        assert alert.cooldown_seconds == 300
    
    def test_metric_alert_custom_values(self):
        """Test MetricAlert with custom values."""
        alert = MetricAlert(
            metric_name="memory_usage",
            condition="gte",
            threshold=90.0,
            duration_seconds=120,
            enabled=False,
            cooldown_seconds=600
        )
        
        assert alert.duration_seconds == 120
        assert alert.enabled is False
        assert alert.cooldown_seconds == 600


class TestMetricAggregator:
    """Test MetricAggregator class."""
    
    @pytest.fixture
    def aggregator(self):
        """Create MetricAggregator instance."""
        with patch('metrics_service.get_network_logging_manager'):
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
    
    def test_aggregate_values_stdev_single_value(self, aggregator):
        """Test aggregate_values stdev with single value."""
        values = [MetricValue(timestamp=datetime.now(), value=42)]
        result = aggregator.aggregate_values(values, "stdev")
        assert result == 0
    
    def test_get_time_window_values(self, aggregator):
        """Test get_time_window_values."""
        now = datetime.now()
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque([
                MetricValue(timestamp=now - timedelta(seconds=120), value=1),
                MetricValue(timestamp=now - timedelta(seconds=30), value=2),
                MetricValue(timestamp=now - timedelta(seconds=10), value=3),
            ])
        )
        
        # Get values from last 60 seconds
        values = aggregator.get_time_window_values(metric, 60)
        assert len(values) == 2
        assert values[0].value == 2
        assert values[1].value == 3
    
    def test_get_time_window_values_default_window(self, aggregator):
        """Test get_time_window_values with default window."""
        now = datetime.now()
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque([
                MetricValue(timestamp=now - timedelta(seconds=30), value=1),
                MetricValue(timestamp=now - timedelta(seconds=10), value=2),
            ])
        )
        
        values = aggregator.get_time_window_values(metric)
        assert len(values) == 2


class TestMetricCollector:
    """Test MetricCollector class."""
    
    @pytest.fixture
    def collector(self):
        """Create MetricCollector instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return MetricCollector("test_collector", collection_interval=1)
    
    @pytest.fixture
    def mock_metrics_service(self):
        """Create mock MetricsService."""
        return Mock()
    
    def test_collector_initialization(self, collector):
        """Test MetricCollector initialization."""
        assert collector.name == "test_collector"
        assert collector.collection_interval == 1
        assert collector._is_active is False
        assert collector._collection_thread is None
        assert len(collector._collection_functions) == 0
    
    def test_add_collection_function(self, collector):
        """Test adding collection function."""
        def test_func():
            return {"test_metric": 42}
        
        collector.add_collection_function(test_func)
        assert len(collector._collection_functions) == 1
        assert collector._collection_functions[0] == test_func
    
    def test_start_collector(self, collector, mock_metrics_service):
        """Test starting collector."""
        collector.start(mock_metrics_service)
        
        assert collector._is_active is True
        assert collector._metrics_service == mock_metrics_service
        assert collector._collection_thread is not None
        assert collector._collection_thread.is_alive()
        
        # Clean up
        collector.stop()
    
    def test_stop_collector(self, collector, mock_metrics_service):
        """Test stopping collector."""
        collector.start(mock_metrics_service)
        assert collector._is_active is True
        
        collector.stop()
        assert collector._is_active is False
    
    def test_collection_loop_with_function(self, collector, mock_metrics_service):
        """Test collection loop with function."""
        def test_func():
            return {"test_metric": 42}
        
        collector.add_collection_function(test_func)
        collector.start(mock_metrics_service)
        
        # Wait for at least one collection cycle
        time.sleep(2)
        
        collector.stop()
        
        # Verify metrics were recorded
        mock_metrics_service.record_value.assert_called()
    
    def test_collection_loop_with_exception(self, collector, mock_metrics_service):
        """Test collection loop with exception in function."""
        def failing_func():
            raise Exception("Test exception")
        
        collector.add_collection_function(failing_func)
        collector.start(mock_metrics_service)
        
        # Wait for collection cycle
        time.sleep(2)
        
        collector.stop()
        
        # Collector should continue running despite exception


class TestSystemMetricsCollector:
    """Test SystemMetricsCollector class."""
    
    @pytest.fixture
    def system_collector(self):
        """Create SystemMetricsCollector instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return SystemMetricsCollector()
    
    def test_system_collector_initialization(self, system_collector):
        """Test SystemMetricsCollector initialization."""
        assert system_collector.name == "System"
        assert system_collector.collection_interval == 30
        assert len(system_collector._collection_functions) == 1
    
    @patch('metrics_service.psutil')
    def test_collect_system_metrics(self, mock_psutil, system_collector):
        """Test system metrics collection."""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0,
            used=1024 * 1024 * 1024  # 1GB
        )
        mock_psutil.disk_usage.return_value = Mock(
            total=100 * 1024 * 1024 * 1024,  # 100GB
            used=50 * 1024 * 1024 * 1024     # 50GB
        )
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1000,
            bytes_recv=2000,
            packets_sent=100,
            packets_recv=200
        )
        
        metrics = system_collector._collect_system_metrics()
        
        assert 'system.cpu.percent' in metrics
        assert 'system.memory.percent' in metrics
        assert 'system.memory.used_mb' in metrics
        assert 'system.disk.percent' in metrics
        assert 'system.network.bytes_sent' in metrics
        assert 'system.network.bytes_recv' in metrics
        assert 'system.network.packets_sent' in metrics
        assert 'system.network.packets_recv' in metrics
        
        assert metrics['system.cpu.percent'] == 50.0
        assert metrics['system.memory.percent'] == 60.0
        assert metrics['system.disk.percent'] == 50.0
    
    def test_collect_system_metrics_no_psutil(self, system_collector):
        """Test system metrics collection without psutil."""
        with patch('metrics_service.psutil', side_effect=ImportError):
            metrics = system_collector._collect_system_metrics()
            assert metrics == {}
    
    def test_collect_system_metrics_exception(self, system_collector):
        """Test system metrics collection with exception."""
        with patch('metrics_service.psutil') as mock_psutil:
            mock_psutil.cpu_percent.side_effect = Exception("Test error")
            
            metrics = system_collector._collect_system_metrics()
            assert metrics == {}


class TestNetworkToolMetricsCollector:
    """Test NetworkToolMetricsCollector class."""
    
    @pytest.fixture
    def tool_collector(self):
        """Create NetworkToolMetricsCollector instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return NetworkToolMetricsCollector("ping")
    
    @pytest.fixture
    def mock_tool(self):
        """Create mock tool instance."""
        tool = Mock()
        tool.is_running = True
        tool.is_healthy = True
        tool._error_count = 5
        tool.get_current_data.return_value = {
            "latency": 10.5,
            "packet_loss": 0.0,
            "jitter": 2.1
        }
        return tool
    
    def test_tool_collector_initialization(self, tool_collector):
        """Test NetworkToolMetricsCollector initialization."""
        assert tool_collector.name == "NetworkTool.ping"
        assert tool_collector.collection_interval == 15
        assert tool_collector.tool_name == "ping"
        assert tool_collector._tool_instance is None
    
    def test_set_tool_instance(self, tool_collector, mock_tool):
        """Test setting tool instance."""
        tool_collector.set_tool_instance(mock_tool)
        
        assert tool_collector._tool_instance == mock_tool
        assert len(tool_collector._collection_functions) == 1
    
    def test_collect_tool_metrics(self, tool_collector, mock_tool):
        """Test tool metrics collection."""
        tool_collector.set_tool_instance(mock_tool)
        
        metrics = tool_collector._collect_tool_metrics()
        
        assert 'ping.is_running' in metrics
        assert 'ping.is_healthy' in metrics
        assert 'ping.error_count' in metrics
        assert 'ping.latency' in metrics
        assert 'ping.packet_loss' in metrics
        assert 'ping.jitter' in metrics
        
        assert metrics['ping.is_running'] == 1
        assert metrics['ping.is_healthy'] == 1
        assert metrics['ping.error_count'] == 5
        assert metrics['ping.latency'] == 10.5
    
    def test_collect_tool_metrics_no_tool(self, tool_collector):
        """Test tool metrics collection without tool instance."""
        metrics = tool_collector._collect_tool_metrics()
        assert metrics == {}
    
    def test_collect_tool_metrics_partial_data(self, tool_collector):
        """Test tool metrics collection with partial tool data."""
        tool = Mock()
        tool.is_running = False
        # No other attributes
        
        tool_collector.set_tool_instance(tool)
        metrics = tool_collector._collect_tool_metrics()
        
        assert 'ping.is_running' in metrics
        assert metrics['ping.is_running'] == 0


class TestMetricsService:
    """Test MetricsService class."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create MetricsService instance."""
        with patch('metrics_service.get_network_logging_manager'):
            service = MetricsService()
            # Stop background threads for testing
            service._stop_event.set()
            if service._cleanup_thread:
                service._cleanup_thread.join(timeout=1)
            if service._alert_thread:
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
    
    def test_record_value_auto_create_float(self, metrics_service):
        """Test recording float value with auto-create metric."""
        result = metrics_service.record_value("auto_gauge", 42.5)
        
        assert result is True
        metric = metrics_service._metrics["auto_gauge"]
        assert metric.type == MetricType.GAUGE  # float value -> gauge
    
    def test_record_value_with_tags(self, metrics_service):
        """Test recording value with tags."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        tags = {"host": "server1", "env": "prod"}
        
        result = metrics_service.record_value("test_metric", 42.5, tags=tags)
        
        assert result is True
        metric = metrics_service._metrics["test_metric"]
        assert metric.values[0].tags == tags
    
    def test_record_value_with_timestamp(self, metrics_service):
        """Test recording value with custom timestamp."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        result = metrics_service.record_value("test_metric", 42.5, timestamp=timestamp)
        
        assert result is True
        metric = metrics_service._metrics["test_metric"]
        assert metric.values[0].timestamp == timestamp
    
    def test_get_metric(self, metrics_service):
        """Test getting metric."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        metric = metrics_service.get_metric("test_metric")
        assert metric is not None
        assert metric.name == "test_metric"
        
        # Non-existent metric
        metric = metrics_service.get_metric("nonexistent")
        assert metric is None
    
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
    
    def test_get_metric_value_nonexistent(self, metrics_service):
        """Test getting value for nonexistent metric."""
        value = metrics_service.get_metric_value("nonexistent", "latest")
        assert value is None
    
    def test_get_metric_value_empty(self, metrics_service):
        """Test getting value for empty metric."""
        metrics_service.create_metric("empty_metric", MetricType.GAUGE)
        
        value = metrics_service.get_metric_value("empty_metric", "latest")
        assert value is None
    
    def test_get_metric_values(self, metrics_service):
        """Test getting metric values in time window."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        now = datetime.now()
        # Add values at different times
        metrics_service.record_value("test_metric", 10, timestamp=now - timedelta(seconds=120))
        metrics_service.record_value("test_metric", 20, timestamp=now - timedelta(seconds=30))
        metrics_service.record_value("test_metric", 30, timestamp=now - timedelta(seconds=10))
        
        # Get values from last 60 seconds
        values = metrics_service.get_metric_values("test_metric", 60)
        assert len(values) == 2
        assert values[0].value == 20
        assert values[1].value == 30
    
    def test_get_metric_values_nonexistent(self, metrics_service):
        """Test getting values for nonexistent metric."""
        values = metrics_service.get_metric_values("nonexistent", 60)
        assert values == []
    
    def test_get_metrics_summary(self, metrics_service):
        """Test getting metrics summary."""
        # Create and populate metrics
        metrics_service.create_metric("metric1", MetricType.GAUGE, description="Test metric 1")
        metrics_service.create_metric("metric2", MetricType.COUNTER, description="Test metric 2")
        
        for i in range(5):
            metrics_service.record_value("metric1", i * 10)
            metrics_service.record_value("metric2", i)
        
        summary = metrics_service.get_metrics_summary()
        
        assert "metric1" in summary
        assert "metric2" in summary
        
        assert summary["metric1"]["latest_value"] == 40
        assert summary["metric1"]["total_values"] == 5
        assert summary["metric1"]["type"] == "gauge"
        
        assert summary["metric2"]["latest_value"] == 4
        assert summary["metric2"]["type"] == "counter"
    
    def test_add_tool_collector(self, metrics_service):
        """Test adding tool collector."""
        mock_tool = Mock()
        mock_tool.is_running = True
        
        result = metrics_service.add_tool_collector("ping", mock_tool)
        
        assert result is True
        assert "tool_ping" in metrics_service._collectors
        
        collector = metrics_service._collectors["tool_ping"]
        assert isinstance(collector, NetworkToolMetricsCollector)
        assert collector.tool_name == "ping"
    
    def test_add_alert(self, metrics_service):
        """Test adding metric alert."""
        result = metrics_service.add_alert(
            metric_name="cpu_usage",
            condition="gt",
            threshold=80.0,
            duration_seconds=60,
            cooldown_seconds=300
        )
        
        assert result is True
        alert_name = "cpu_usage_gt_80.0"
        assert alert_name in metrics_service._alerts
        
        alert = metrics_service._alerts[alert_name]
        assert alert.metric_name == "cpu_usage"
        assert alert.condition == "gt"
        assert alert.threshold == 80.0
        assert alert.duration_seconds == 60
        assert alert.cooldown_seconds == 300
    
    def test_evaluate_condition(self, metrics_service):
        """Test alert condition evaluation."""
        assert metrics_service._evaluate_condition(85, "gt", 80) is True
        assert metrics_service._evaluate_condition(75, "gt", 80) is False
        
        assert metrics_service._evaluate_condition(75, "lt", 80) is True
        assert metrics_service._evaluate_condition(85, "lt", 80) is False
        
        assert metrics_service._evaluate_condition(80, "eq", 80) is True
        assert metrics_service._evaluate_condition(75, "eq", 80) is False
        
        assert metrics_service._evaluate_condition(80, "gte", 80) is True
        assert metrics_service._evaluate_condition(85, "gte", 80) is True
        assert metrics_service._evaluate_condition(75, "gte", 80) is False
        
        assert metrics_service._evaluate_condition(80, "lte", 80) is True
        assert metrics_service._evaluate_condition(75, "lte", 80) is True
        assert metrics_service._evaluate_condition(85, "lte", 80) is False
        
        assert metrics_service._evaluate_condition(80, "unknown", 80) is False
    
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
    
    def test_export_metrics_csv(self, metrics_service):
        """Test exporting metrics to CSV."""
        # Create and populate metric
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        metrics_service.record_value("test_metric", 42.5, tags={"env": "test"})
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            file_path = f.name
        
        try:
            result = metrics_service.export_metrics(file_path, "csv", 3600)
            assert result is True
            
            # Verify exported data
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) >= 2  # Header + at least one data line
            assert "metric_name,timestamp,value,tags" in lines[0]
            assert "test_metric" in lines[1]
            assert "42.5" in lines[1]
            
        finally:
            os.unlink(file_path)
    
    def test_get_statistics(self, metrics_service):
        """Test getting service statistics."""
        # Add some data
        metrics_service.create_metric("metric1", MetricType.GAUGE)
        metrics_service.create_metric("metric2", MetricType.COUNTER)
        metrics_service.record_value("metric1", 10)
        metrics_service.record_value("metric1", 20)
        metrics_service.record_value("metric2", 5)
        
        stats = metrics_service.get_statistics()
        
        assert stats["total_metrics"] == 2
        assert stats["total_values_recorded"] == 3
        assert stats["alerts_configured"] == 0
        assert stats["memory_usage_values"] == 3
    
    def test_shutdown(self, metrics_service):
        """Test service shutdown."""
        # Add a collector
        mock_collector = Mock()
        metrics_service._collectors["test"] = mock_collector
        
        metrics_service.shutdown()
        
        assert metrics_service._stop_event.is_set()
        mock_collector.stop.assert_called_once()


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    @pytest.fixture(autouse=True)
    def reset_global_service(self):
        """Reset global service before each test."""
        # Reset the global service variable
        import metrics_service
        metrics_service._metrics_service = None
    
    @patch('metrics_service.get_network_logging_manager')
    def test_get_metrics_service(self, mock_logging):
        """Test get_metrics_service function."""
        service1 = get_metrics_service()
        service2 = get_metrics_service()
        
        assert service1 is service2  # Should return same instance
        assert isinstance(service1, MetricsService)
    
    @patch('metrics_service.get_network_logging_manager')
    def test_record_counter(self, mock_logging):
        """Test record_counter function."""
        record_counter("test_counter", 5)
        
        service = get_metrics_service()
        assert "test_counter" in service._metrics
        
        metric = service._metrics["test_counter"]
        assert metric.type == MetricType.COUNTER
        assert metric.unit == MetricUnit.COUNT
        assert len(metric.values) == 1
        assert metric.values[0].value == 5
    
    @patch('metrics_service.get_network_logging_manager')
    def test_record_counter_default_value(self, mock_logging):
        """Test record_counter with default value."""
        record_counter("test_counter")
        
        service = get_metrics_service()
        metric = service._metrics["test_counter"]
        assert metric.values[0].value == 1
    
    @patch('metrics_service.get_network_logging_manager')
    def test_record_gauge(self, mock_logging):
        """Test record_gauge function."""
        record_gauge("test_gauge", 42.5)
        
        service = get_metrics_service()
        assert "test_gauge" in service._metrics
        
        metric = service._metrics["test_gauge"]
        assert metric.type == MetricType.GAUGE
        assert len(metric.values) == 1
        assert metric.values[0].value == 42.5
    
    @patch('metrics_service.get_network_logging_manager')
    def test_record_timer(self, mock_logging):
        """Test record_timer function."""
        record_timer("test_timer", 123.45)
        
        service = get_metrics_service()
        assert "test_timer" in service._metrics
        
        metric = service._metrics["test_timer"]
        assert metric.type == MetricType.TIMER
        assert metric.unit == MetricUnit.MILLISECONDS
        assert len(metric.values) == 1
        assert metric.values[0].value == 123.45
    
    @patch('metrics_service.get_network_logging_manager')
    def test_record_rate(self, mock_logging):
        """Test record_rate function."""
        record_rate("test_rate", 15.5)
        
        service = get_metrics_service()
        assert "test_rate" in service._metrics
        
        metric = service._metrics["test_rate"]
        assert metric.type == MetricType.RATE
        assert metric.unit == MetricUnit.RATE_PER_SECOND
        assert len(metric.values) == 1
        assert metric.values[0].value == 15.5


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create MetricsService instance."""
        with patch('metrics_service.get_network_logging_manager'):
            service = MetricsService()
            service._stop_event.set()
            return service
    
    def test_metric_with_max_values_overflow(self, metrics_service):
        """Test metric value storage with overflow."""
        metrics_service.create_metric(
            "overflow_metric", MetricType.GAUGE, max_values=3
        )
        
        # Add more values than max_values
        for i in range(5):
            metrics_service.record_value("overflow_metric", i)
        
        metric = metrics_service._metrics["overflow_metric"]
        assert len(metric.values) == 3  # Only keeps last 3
        assert metric.values[0].value == 2
        assert metric.values[1].value == 3
        assert metric.values[2].value == 4
    
    def test_aggregation_with_mixed_numeric_types(self, metrics_service):
        """Test aggregation with mixed int and float values."""
        metrics_service.create_metric("mixed_metric", MetricType.GAUGE)
        
        # Mix int and float values
        metrics_service.record_value("mixed_metric", 10)      # int
        metrics_service.record_value("mixed_metric", 20.5)    # float
        metrics_service.record_value("mixed_metric", 30)      # int
        
        avg = metrics_service.get_metric_value("mixed_metric", "avg")
        assert abs(avg - 20.166666666666668) < 0.0001
    
    def test_concurrent_metric_operations(self, metrics_service):
        """Test concurrent metric operations."""
        metrics_service.create_metric("concurrent_metric", MetricType.COUNTER)
        
        def record_values():
            for i in range(10):
                metrics_service.record_value("concurrent_metric", 1)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=record_values)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        metric = metrics_service._metrics["concurrent_metric"]
        assert len(metric.values) == 50  # 5 threads * 10 values each
    
    def test_large_metric_names_and_values(self, metrics_service):
        """Test handling of large metric names and values."""
        large_name = "x" * 1000  # Very long metric name
        large_value = 1e10  # Very large value
        
        result = metrics_service.create_metric(large_name, MetricType.GAUGE)
        assert result is True
        
        result = metrics_service.record_value(large_name, large_value)
        assert result is True
        
        value = metrics_service.get_metric_value(large_name, "latest")
        assert value == large_value
    
    def test_unicode_metric_names_and_tags(self, metrics_service):
        """Test handling of unicode in metric names and tags."""
        unicode_name = "测试指标"  # Chinese characters
        unicode_tags = {"환경": "테스트", "주机": "서버1"}  # Korean characters
        
        result = metrics_service.create_metric(unicode_name, MetricType.GAUGE)
        assert result is True
        
        result = metrics_service.record_value(unicode_name, 42, tags=unicode_tags)
        assert result is True
        
        metric = metrics_service._metrics[unicode_name]
        assert metric.values[0].tags == unicode_tags
    
    def test_negative_and_zero_values(self, metrics_service):
        """Test handling of negative and zero values."""
        metrics_service.create_metric("signed_metric", MetricType.GAUGE)
        
        # Test various values
        test_values = [-100, -0.1, 0, 0.0, 100.5]
        for value in test_values:
            metrics_service.record_value("signed_metric", value)
        
        metric = metrics_service._metrics["signed_metric"]
        assert len(metric.values) == 5
        
        # Test aggregations work with negative values
        assert metrics_service.get_metric_value("signed_metric", "min") == -100
        assert metrics_service.get_metric_value("signed_metric", "max") == 100.5
    
    def test_extreme_timestamps(self, metrics_service):
        """Test handling of extreme timestamps."""
        metrics_service.create_metric("time_metric", MetricType.GAUGE)
        
        # Very old timestamp
        old_time = datetime(1970, 1, 1)
        result = metrics_service.record_value("time_metric", 10, timestamp=old_time)
        assert result is True
        
        # Far future timestamp
        future_time = datetime(2100, 12, 31)
        result = metrics_service.record_value("time_metric", 20, timestamp=future_time)
        assert result is True
        
        metric = metrics_service._metrics["time_metric"]
        assert len(metric.values) == 2


if __name__ == "__main__":
    pytest.main([__file__])