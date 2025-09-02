"""
Comprehensive unit tests for metrics_service.py
Generated on: 2025-08-28
Target: src/utilities/network/network_connectivity_complex/core/metrics_service.py
"""

import json
import os
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'network', 'network_connectivity_complex', 'core'))

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
        """Test all metric type values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"
        assert MetricType.RATE.value == "rate"
    
    def test_metric_type_membership(self):
        """Test metric type membership."""
        types = [e.value for e in MetricType]
        assert "counter" in types
        assert "gauge" in types
        assert "histogram" in types
        assert "timer" in types
        assert "rate" in types
        assert "invalid" not in types


class TestMetricUnit:
    """Test MetricUnit enum."""
    
    def test_metric_unit_values(self):
        """Test all metric unit values."""
        assert MetricUnit.NONE.value == ""
        assert MetricUnit.BYTES.value == "bytes"
        assert MetricUnit.SECONDS.value == "seconds"
        assert MetricUnit.MILLISECONDS.value == "ms"
        assert MetricUnit.PERCENT.value == "percent"
        assert MetricUnit.COUNT.value == "count"
        assert MetricUnit.RATE_PER_SECOND.value == "per_second"
        assert MetricUnit.MBPS.value == "mbps"
        assert MetricUnit.PACKETS.value == "packets"
    
    def test_metric_unit_membership(self):
        """Test metric unit membership."""
        units = [e.value for e in MetricUnit]
        assert "" in units
        assert "bytes" in units
        assert "ms" in units
        assert "invalid" not in units


class TestMetricValue:
    """Test MetricValue dataclass."""
    
    def test_metric_value_creation(self):
        """Test creating metric values."""
        timestamp = datetime.now()
        value = MetricValue(timestamp=timestamp, value=100)
        
        assert value.timestamp == timestamp
        assert value.value == 100
        assert value.tags == {}
    
    def test_metric_value_with_tags(self):
        """Test metric value with tags."""
        timestamp = datetime.now()
        tags = {"source": "test", "category": "performance"}
        value = MetricValue(timestamp=timestamp, value=50.5, tags=tags)
        
        assert value.timestamp == timestamp
        assert value.value == 50.5
        assert value.tags == tags
    
    def test_metric_value_tags_default(self):
        """Test default tags initialization."""
        value = MetricValue(timestamp=datetime.now(), value=10)
        assert isinstance(value.tags, dict)
        assert len(value.tags) == 0


class TestMetric:
    """Test Metric dataclass."""
    
    def test_metric_creation(self):
        """Test creating metrics."""
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
    
    def test_metric_with_tags(self):
        """Test metric with tags."""
        tags = {"component": "network", "severity": "high"}
        metric = Metric(
            name="error_count",
            type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Error counter",
            values=deque(),
            tags=tags
        )
        
        assert metric.tags == tags
    
    def test_metric_deque_initialization(self):
        """Test deque initialization in metric."""
        # Test with regular list
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=[1, 2, 3]
        )
        
        assert isinstance(metric.values, deque)
        assert metric.values.maxlen == 1000
    
    def test_metric_custom_max_values(self):
        """Test custom max values setting."""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque(),
            max_values=500
        )
        
        assert metric.max_values == 500
        assert metric.values.maxlen == 500


class TestMetricAlert:
    """Test MetricAlert dataclass."""
    
    def test_metric_alert_creation(self):
        """Test creating metric alerts."""
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
    
    def test_metric_alert_with_custom_values(self):
        """Test metric alert with custom values."""
        last_triggered = datetime.now()
        alert = MetricAlert(
            metric_name="memory_usage",
            condition="lt",
            threshold=10.0,
            duration_seconds=120,
            enabled=False,
            last_triggered=last_triggered,
            cooldown_seconds=600
        )
        
        assert alert.metric_name == "memory_usage"
        assert alert.condition == "lt"
        assert alert.threshold == 10.0
        assert alert.duration_seconds == 120
        assert alert.enabled is False
        assert alert.last_triggered == last_triggered
        assert alert.cooldown_seconds == 600


class TestMetricAggregator:
    """Test MetricAggregator class."""
    
    @pytest.fixture
    def aggregator(self):
        """Create aggregator instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return MetricAggregator(window_size_seconds=60)
    
    @pytest.fixture
    def sample_values(self):
        """Create sample metric values."""
        now = datetime.now()
        return [
            MetricValue(timestamp=now - timedelta(seconds=30), value=10),
            MetricValue(timestamp=now - timedelta(seconds=20), value=20),
            MetricValue(timestamp=now - timedelta(seconds=10), value=30),
            MetricValue(timestamp=now, value=40)
        ]
    
    def test_aggregator_initialization(self, aggregator):
        """Test aggregator initialization."""
        assert aggregator.window_size == 60
        assert hasattr(aggregator, 'logger')
    
    def test_aggregate_values_avg(self, aggregator, sample_values):
        """Test average aggregation."""
        result = aggregator.aggregate_values(sample_values, "avg")
        assert result == 25.0  # (10+20+30+40)/4
    
    def test_aggregate_values_sum(self, aggregator, sample_values):
        """Test sum aggregation."""
        result = aggregator.aggregate_values(sample_values, "sum")
        assert result == 100.0  # 10+20+30+40
    
    def test_aggregate_values_min(self, aggregator, sample_values):
        """Test min aggregation."""
        result = aggregator.aggregate_values(sample_values, "min")
        assert result == 10.0
    
    def test_aggregate_values_max(self, aggregator, sample_values):
        """Test max aggregation."""
        result = aggregator.aggregate_values(sample_values, "max")
        assert result == 40.0
    
    def test_aggregate_values_count(self, aggregator, sample_values):
        """Test count aggregation."""
        result = aggregator.aggregate_values(sample_values, "count")
        assert result == 4.0
    
    def test_aggregate_values_median(self, aggregator, sample_values):
        """Test median aggregation."""
        result = aggregator.aggregate_values(sample_values, "median")
        assert result == 25.0  # median of [10, 20, 30, 40]
    
    def test_aggregate_values_stdev(self, aggregator, sample_values):
        """Test standard deviation aggregation."""
        result = aggregator.aggregate_values(sample_values, "stdev")
        assert result > 0  # Should be positive
        # Exact value: sqrt(((10-25)^2 + (20-25)^2 + (30-25)^2 + (40-25)^2)/3)
        assert abs(result - 12.91) < 0.1
    
    def test_aggregate_values_empty(self, aggregator):
        """Test aggregation with empty values."""
        result = aggregator.aggregate_values([], "avg")
        assert result is None
    
    def test_aggregate_values_non_numeric(self, aggregator):
        """Test aggregation with non-numeric values."""
        values = [
            MetricValue(timestamp=datetime.now(), value="string"),
            MetricValue(timestamp=datetime.now(), value=None)
        ]
        result = aggregator.aggregate_values(values, "avg")
        assert result is None
    
    def test_aggregate_values_mixed_numeric(self, aggregator):
        """Test aggregation with mixed numeric values."""
        values = [
            MetricValue(timestamp=datetime.now(), value=10),
            MetricValue(timestamp=datetime.now(), value=20.5),
            MetricValue(timestamp=datetime.now(), value="invalid"),
            MetricValue(timestamp=datetime.now(), value=30)
        ]
        result = aggregator.aggregate_values(values, "avg")
        assert result == 20.166666666666668  # (10+20.5+30)/3
    
    def test_aggregate_values_unknown_type(self, aggregator, sample_values):
        """Test aggregation with unknown type."""
        with patch.object(aggregator.logger, 'warning') as mock_warning:
            result = aggregator.aggregate_values(sample_values, "unknown")
            assert result == 25.0  # Falls back to average
            mock_warning.assert_called_once()
    
    def test_aggregate_values_stdev_single_value(self, aggregator):
        """Test standard deviation with single value."""
        values = [MetricValue(timestamp=datetime.now(), value=10)]
        result = aggregator.aggregate_values(values, "stdev")
        assert result == 0
    
    def test_aggregate_values_exception(self, aggregator):
        """Test aggregation exception handling."""
        # Create invalid values that would cause an exception
        values = [MetricValue(timestamp=datetime.now(), value=float('inf'))]
        
        with patch.object(aggregator.logger, 'error') as mock_error:
            result = aggregator.aggregate_values(values, "stdev")
            assert result is None
            mock_error.assert_called_once()
    
    def test_get_time_window_values(self, aggregator):
        """Test getting values within time window."""
        now = datetime.now()
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque([
                MetricValue(timestamp=now - timedelta(seconds=120), value=1),  # Outside window
                MetricValue(timestamp=now - timedelta(seconds=30), value=2),   # Inside window
                MetricValue(timestamp=now - timedelta(seconds=10), value=3),   # Inside window
                MetricValue(timestamp=now, value=4)                            # Inside window
            ])
        )
        
        result = aggregator.get_time_window_values(metric, 60)
        assert len(result) == 3
        assert all(v.timestamp >= now - timedelta(seconds=60) for v in result)
    
    def test_get_time_window_values_default_window(self, aggregator):
        """Test getting values with default window size."""
        now = datetime.now()
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque([
                MetricValue(timestamp=now - timedelta(seconds=30), value=1),
                MetricValue(timestamp=now, value=2)
            ])
        )
        
        result = aggregator.get_time_window_values(metric)
        assert len(result) == 2  # Both within default 60-second window


class TestMetricCollector:
    """Test MetricCollector class."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return MetricCollector("test_collector", collection_interval=1)
    
    def test_collector_initialization(self, collector):
        """Test collector initialization."""
        assert collector.name == "test_collector"
        assert collector.collection_interval == 1
        assert collector._is_active is False
        assert collector._collection_thread is None
        assert collector._metrics_service is None
        assert len(collector._collection_functions) == 0
    
    def test_add_collection_function(self, collector):
        """Test adding collection functions."""
        def sample_func():
            return {"metric1": 10, "metric2": 20}
        
        collector.add_collection_function(sample_func)
        assert len(collector._collection_functions) == 1
        assert collector._collection_functions[0] == sample_func
    
    def test_start_collector(self, collector):
        """Test starting collector."""
        mock_service = Mock()
        
        collector.start(mock_service)
        
        assert collector._is_active is True
        assert collector._metrics_service == mock_service
        assert collector._collection_thread is not None
        assert collector._collection_thread.is_alive()
        
        # Clean up
        collector.stop()
    
    def test_stop_collector(self, collector):
        """Test stopping collector."""
        mock_service = Mock()
        collector.start(mock_service)
        
        collector.stop()
        
        assert collector._is_active is False
        assert collector._stop_event.is_set()
    
    def test_collection_loop(self, collector):
        """Test collection loop functionality."""
        collected_data = []
        
        def mock_collection_func():
            collected_data.append({"test_metric": len(collected_data) + 1})
            return {"test_metric": len(collected_data)}
        
        collector.add_collection_function(mock_collection_func)
        
        mock_service = Mock()
        collector.start(mock_service)
        
        # Wait for at least one collection cycle
        time.sleep(1.5)
        
        collector.stop()
        
        # Verify metrics were recorded
        assert mock_service.record_value.called
        assert len(collected_data) > 0
    
    def test_collection_function_exception(self, collector):
        """Test handling of collection function exceptions."""
        def failing_func():
            raise ValueError("Test error")
        
        def working_func():
            return {"working_metric": 1}
        
        collector.add_collection_function(failing_func)
        collector.add_collection_function(working_func)
        
        mock_service = Mock()
        
        with patch.object(collector.logger, 'error') as mock_error:
            collector.start(mock_service)
            time.sleep(1.5)
            collector.stop()
            
            # Should log error but continue with other functions
            assert mock_error.called
            mock_service.record_value.assert_called()


class TestSystemMetricsCollector:
    """Test SystemMetricsCollector class."""
    
    @pytest.fixture
    def system_collector(self):
        """Create system metrics collector."""
        with patch('metrics_service.get_network_logging_manager'):
            return SystemMetricsCollector()
    
    def test_system_collector_initialization(self, system_collector):
        """Test system collector initialization."""
        assert system_collector.name == "System"
        assert system_collector.collection_interval == 30
        assert len(system_collector._collection_functions) == 1
    
    @patch('metrics_service.psutil')
    def test_collect_system_metrics_success(self, mock_psutil, system_collector):
        """Test successful system metrics collection."""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 50.0
        
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = Mock()
        mock_disk.used = 500 * 1024 * 1024 * 1024  # 500GB
        mock_disk.total = 1000 * 1024 * 1024 * 1024  # 1TB
        mock_psutil.disk_usage.return_value = mock_disk
        
        mock_net_io = Mock()
        mock_net_io.bytes_sent = 1000000
        mock_net_io.bytes_recv = 2000000
        mock_net_io.packets_sent = 500
        mock_net_io.packets_recv = 800
        mock_psutil.net_io_counters.return_value = mock_net_io
        
        result = system_collector._collect_system_metrics()
        
        assert 'system.cpu.percent' in result
        assert result['system.cpu.percent'] == 50.0
        assert 'system.memory.percent' in result
        assert result['system.memory.percent'] == 60.0
        assert 'system.memory.used_mb' in result
        assert result['system.memory.used_mb'] == 8192.0
        assert 'system.disk.percent' in result
        assert result['system.disk.percent'] == 50.0
        assert 'system.network.bytes_sent' in result
        assert result['system.network.bytes_sent'] == 1000000
    
    def test_collect_system_metrics_no_psutil(self, system_collector):
        """Test system metrics collection without psutil."""
        with patch.object(system_collector.logger, 'warning') as mock_warning:
            result = system_collector._collect_system_metrics()
            
            assert result == {}
            mock_warning.assert_called_once()
    
    @patch('metrics_service.psutil')
    def test_collect_system_metrics_exception(self, mock_psutil, system_collector):
        """Test system metrics collection exception handling."""
        mock_psutil.cpu_percent.side_effect = Exception("Test error")
        
        with patch.object(system_collector.logger, 'error') as mock_error:
            result = system_collector._collect_system_metrics()
            
            assert result == {}
            mock_error.assert_called_once()


class TestNetworkToolMetricsCollector:
    """Test NetworkToolMetricsCollector class."""
    
    @pytest.fixture
    def tool_collector(self):
        """Create network tool metrics collector."""
        with patch('metrics_service.get_network_logging_manager'):
            return NetworkToolMetricsCollector("ping")
    
    def test_tool_collector_initialization(self, tool_collector):
        """Test tool collector initialization."""
        assert tool_collector.name == "NetworkTool.ping"
        assert tool_collector.collection_interval == 15
        assert tool_collector.tool_name == "ping"
        assert tool_collector._tool_instance is None
    
    def test_set_tool_instance(self, tool_collector):
        """Test setting tool instance."""
        mock_tool = Mock()
        tool_collector.set_tool_instance(mock_tool)
        
        assert tool_collector._tool_instance == mock_tool
        assert len(tool_collector._collection_functions) == 1
    
    def test_collect_tool_metrics_no_instance(self, tool_collector):
        """Test collecting metrics without tool instance."""
        result = tool_collector._collect_tool_metrics()
        assert result == {}
    
    def test_collect_tool_metrics_basic_attributes(self, tool_collector):
        """Test collecting basic tool metrics."""
        mock_tool = Mock()
        mock_tool.is_running = True
        mock_tool.is_healthy = False
        mock_tool._error_count = 5
        
        tool_collector.set_tool_instance(mock_tool)
        result = tool_collector._collect_tool_metrics()
        
        assert result['ping.is_running'] == 1
        assert result['ping.is_healthy'] == 0
        assert result['ping.error_count'] == 5
    
    def test_collect_tool_metrics_current_data(self, tool_collector):
        """Test collecting tool metrics with current data."""
        mock_tool = Mock()
        mock_tool.is_running = True
        mock_tool.get_current_data.return_value = {
            "latency": 25.5,
            "packets_sent": 100,
            "success_rate": 95.0,
            "status": "ok"  # Non-numeric, should be ignored
        }
        
        tool_collector.set_tool_instance(mock_tool)
        result = tool_collector._collect_tool_metrics()
        
        assert result['ping.is_running'] == 1
        assert result['ping.latency'] == 25.5
        assert result['ping.packets_sent'] == 100
        assert result['ping.success_rate'] == 95.0
        assert 'ping.status' not in result
    
    def test_collect_tool_metrics_exception(self, tool_collector):
        """Test tool metrics collection exception handling."""
        mock_tool = Mock()
        mock_tool.is_running.side_effect = Exception("Test error")
        
        tool_collector.set_tool_instance(mock_tool)
        
        with patch.object(tool_collector.logger, 'error') as mock_error:
            result = tool_collector._collect_tool_metrics()
            
            assert result == {}
            mock_error.assert_called_once()


class TestMetricsService:
    """Test MetricsService class."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create metrics service instance."""
        with patch('metrics_service.get_network_logging_manager'):
            service = MetricsService()
            # Stop background threads for testing
            service._stop_event.set()
            return service
    
    def test_metrics_service_initialization(self, metrics_service):
        """Test metrics service initialization."""
        assert isinstance(metrics_service._metrics, dict)
        assert isinstance(metrics_service._aggregator, MetricAggregator)
        assert isinstance(metrics_service._collectors, dict)
        assert isinstance(metrics_service._alerts, dict)
        assert 'default_max_values' in metrics_service._config
        assert 'total_metrics' in metrics_service._stats
    
    def test_create_metric_success(self, metrics_service):
        """Test successful metric creation."""
        result = metrics_service.create_metric(
            name="test_metric",
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Test counter metric"
        )
        
        assert result is True
        assert "test_metric" in metrics_service._metrics
        
        metric = metrics_service._metrics["test_metric"]
        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER
        assert metric.unit == MetricUnit.COUNT
        assert metric.description == "Test counter metric"
    
    def test_create_metric_duplicate(self, metrics_service):
        """Test creating duplicate metric."""
        metrics_service.create_metric("duplicate", MetricType.GAUGE)
        
        with patch.object(metrics_service.logger, 'warning') as mock_warning:
            result = metrics_service.create_metric("duplicate", MetricType.COUNTER)
            
            assert result is False
            mock_warning.assert_called_once()
    
    def test_create_metric_with_tags(self, metrics_service):
        """Test creating metric with tags."""
        tags = {"component": "network", "type": "latency"}
        result = metrics_service.create_metric(
            name="tagged_metric",
            metric_type=MetricType.TIMER,
            tags=tags
        )
        
        assert result is True
        metric = metrics_service._metrics["tagged_metric"]
        assert metric.tags == tags
    
    def test_create_metric_custom_max_values(self, metrics_service):
        """Test creating metric with custom max values."""
        result = metrics_service.create_metric(
            name="limited_metric",
            metric_type=MetricType.GAUGE,
            max_values=500
        )
        
        assert result is True
        metric = metrics_service._metrics["limited_metric"]
        assert metric.max_values == 500
        assert metric.values.maxlen == 500
    
    def test_create_metric_exception(self, metrics_service):
        """Test metric creation exception handling."""
        with patch.object(Metric, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.create_metric("error_metric", MetricType.GAUGE)
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_record_value_existing_metric(self, metrics_service):
        """Test recording value to existing metric."""
        metrics_service.create_metric("existing", MetricType.GAUGE)
        
        result = metrics_service.record_value("existing", 42.5)
        
        assert result is True
        metric = metrics_service._metrics["existing"]
        assert len(metric.values) == 1
        assert metric.values[0].value == 42.5
    
    def test_record_value_auto_create_int(self, metrics_service):
        """Test recording integer value with auto-creation."""
        result = metrics_service.record_value("auto_counter", 10)
        
        assert result is True
        assert "auto_counter" in metrics_service._metrics
        
        metric = metrics_service._metrics["auto_counter"]
        assert metric.type == MetricType.COUNTER
        assert metric.values[0].value == 10
    
    def test_record_value_auto_create_float(self, metrics_service):
        """Test recording float value with auto-creation."""
        result = metrics_service.record_value("auto_gauge", 10.5)
        
        assert result is True
        assert "auto_gauge" in metrics_service._metrics
        
        metric = metrics_service._metrics["auto_gauge"]
        assert metric.type == MetricType.GAUGE
        assert metric.values[0].value == 10.5
    
    def test_record_value_with_tags(self, metrics_service):
        """Test recording value with tags."""
        metrics_service.create_metric("tagged", MetricType.GAUGE)
        tags = {"source": "test", "level": "info"}
        
        result = metrics_service.record_value("tagged", 100, tags=tags)
        
        assert result is True
        metric = metrics_service._metrics["tagged"]
        assert metric.values[0].tags == tags
    
    def test_record_value_with_timestamp(self, metrics_service):
        """Test recording value with custom timestamp."""
        metrics_service.create_metric("timestamped", MetricType.GAUGE)
        custom_time = datetime(2025, 1, 1, 12, 0, 0)
        
        result = metrics_service.record_value("timestamped", 50, timestamp=custom_time)
        
        assert result is True
        metric = metrics_service._metrics["timestamped"]
        assert metric.values[0].timestamp == custom_time
    
    def test_record_value_exception(self, metrics_service):
        """Test record value exception handling."""
        with patch.object(MetricValue, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.record_value("error_metric", 10)
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_get_metric_existing(self, metrics_service):
        """Test getting existing metric."""
        metrics_service.create_metric("existing", MetricType.GAUGE)
        
        metric = metrics_service.get_metric("existing")
        
        assert metric is not None
        assert metric.name == "existing"
    
    def test_get_metric_non_existing(self, metrics_service):
        """Test getting non-existing metric."""
        metric = metrics_service.get_metric("non_existing")
        assert metric is None
    
    def test_get_metric_value_latest(self, metrics_service):
        """Test getting latest metric value."""
        metrics_service.create_metric("test", MetricType.GAUGE)
        metrics_service.record_value("test", 10)
        metrics_service.record_value("test", 20)
        metrics_service.record_value("test", 30)
        
        value = metrics_service.get_metric_value("test", "latest")
        assert value == 30
    
    def test_get_metric_value_aggregation(self, metrics_service):
        """Test getting aggregated metric value."""
        metrics_service.create_metric("test", MetricType.GAUGE)
        metrics_service.record_value("test", 10)
        metrics_service.record_value("test", 20)
        metrics_service.record_value("test", 30)
        
        avg_value = metrics_service.get_metric_value("test", "avg")
        assert avg_value == 20.0
        
        sum_value = metrics_service.get_metric_value("test", "sum")
        assert sum_value == 60.0
    
    def test_get_metric_value_non_existing(self, metrics_service):
        """Test getting value from non-existing metric."""
        value = metrics_service.get_metric_value("non_existing", "latest")
        assert value is None
    
    def test_get_metric_value_empty_metric(self, metrics_service):
        """Test getting value from empty metric."""
        metrics_service.create_metric("empty", MetricType.GAUGE)
        
        value = metrics_service.get_metric_value("empty", "latest")
        assert value is None
    
    def test_get_metric_values(self, metrics_service):
        """Test getting metric values within time window."""
        metrics_service.create_metric("test", MetricType.GAUGE)
        
        now = datetime.now()
        metrics_service.record_value("test", 10, timestamp=now - timedelta(seconds=120))
        metrics_service.record_value("test", 20, timestamp=now - timedelta(seconds=30))
        metrics_service.record_value("test", 30, timestamp=now)
        
        values = metrics_service.get_metric_values("test", window_seconds=60)
        
        assert len(values) == 2  # Only values within 60 seconds
        assert values[0].value == 20
        assert values[1].value == 30
    
    def test_get_metric_values_non_existing(self, metrics_service):
        """Test getting values from non-existing metric."""
        values = metrics_service.get_metric_values("non_existing")
        assert values == []
    
    def test_get_metrics_summary(self, metrics_service):
        """Test getting metrics summary."""
        # Create and populate metrics
        metrics_service.create_metric("metric1", MetricType.COUNTER, description="Counter")
        metrics_service.create_metric("metric2", MetricType.GAUGE, description="Gauge")
        
        now = datetime.now()
        metrics_service.record_value("metric1", 10, timestamp=now - timedelta(minutes=30))
        metrics_service.record_value("metric1", 20, timestamp=now)
        
        summary = metrics_service.get_metrics_summary()
        
        assert "metric1" in summary
        assert summary["metric1"]["type"] == "counter"
        assert summary["metric1"]["description"] == "Counter"
        assert summary["metric1"]["latest_value"] == 20
        assert summary["metric1"]["total_values"] == 2
        
        # metric2 should not be in summary (no values)
        assert "metric2" not in summary
    
    def test_add_tool_collector_success(self, metrics_service):
        """Test adding tool collector successfully."""
        mock_tool = Mock()
        
        result = metrics_service.add_tool_collector("ping", mock_tool)
        
        assert result is True
        assert "tool_ping" in metrics_service._collectors
        
        collector = metrics_service._collectors["tool_ping"]
        assert isinstance(collector, NetworkToolMetricsCollector)
    
    def test_add_tool_collector_exception(self, metrics_service):
        """Test tool collector addition exception handling."""
        with patch('metrics_service.NetworkToolMetricsCollector', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.add_tool_collector("error_tool", Mock())
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_add_alert_success(self, metrics_service):
        """Test adding alert successfully."""
        result = metrics_service.add_alert(
            metric_name="cpu_usage",
            condition="gt",
            threshold=80.0,
            duration_seconds=120
        )
        
        assert result is True
        alert_name = "cpu_usage_gt_80.0"
        assert alert_name in metrics_service._alerts
        
        alert = metrics_service._alerts[alert_name]
        assert alert.metric_name == "cpu_usage"
        assert alert.condition == "gt"
        assert alert.threshold == 80.0
        assert alert.duration_seconds == 120
    
    def test_add_alert_exception(self, metrics_service):
        """Test alert addition exception handling."""
        with patch.object(MetricAlert, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.add_alert("error_metric", "gt", 50)
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_evaluate_condition_gt(self, metrics_service):
        """Test greater than condition evaluation."""
        assert metrics_service._evaluate_condition(10, "gt", 5) is True
        assert metrics_service._evaluate_condition(5, "gt", 10) is False
        assert metrics_service._evaluate_condition(5, "gt", 5) is False
    
    def test_evaluate_condition_lt(self, metrics_service):
        """Test less than condition evaluation."""
        assert metrics_service._evaluate_condition(5, "lt", 10) is True
        assert metrics_service._evaluate_condition(10, "lt", 5) is False
        assert metrics_service._evaluate_condition(5, "lt", 5) is False
    
    def test_evaluate_condition_eq(self, metrics_service):
        """Test equal condition evaluation."""
        assert metrics_service._evaluate_condition(5, "eq", 5) is True
        assert metrics_service._evaluate_condition(5, "eq", 10) is False
    
    def test_evaluate_condition_gte(self, metrics_service):
        """Test greater than or equal condition evaluation."""
        assert metrics_service._evaluate_condition(10, "gte", 5) is True
        assert metrics_service._evaluate_condition(5, "gte", 5) is True
        assert metrics_service._evaluate_condition(5, "gte", 10) is False
    
    def test_evaluate_condition_lte(self, metrics_service):
        """Test less than or equal condition evaluation."""
        assert metrics_service._evaluate_condition(5, "lte", 10) is True
        assert metrics_service._evaluate_condition(5, "lte", 5) is True
        assert metrics_service._evaluate_condition(10, "lte", 5) is False
    
    def test_evaluate_condition_invalid(self, metrics_service):
        """Test invalid condition evaluation."""
        assert metrics_service._evaluate_condition(5, "invalid", 5) is False
    
    @patch('metrics_service.get_notification_service')
    def test_trigger_alert_with_notification(self, mock_get_notification, metrics_service):
        """Test alert triggering with notification service."""
        mock_notification_service = Mock()
        mock_get_notification.return_value = mock_notification_service
        
        alert = MetricAlert(
            metric_name="test_metric",
            condition="gt",
            threshold=80.0
        )
        
        with patch.object(metrics_service.logger, 'warning') as mock_warning:
            metrics_service._trigger_alert("test_alert", alert, 90.0)
            
            assert alert.last_triggered is not None
            assert metrics_service._stats['alerts_triggered'] == 1
            mock_notification_service.send_notification.assert_called_once()
            mock_warning.assert_called_once()
    
    def test_trigger_alert_no_notification(self, metrics_service):
        """Test alert triggering without notification service."""
        alert = MetricAlert(
            metric_name="test_metric",
            condition="gt",
            threshold=80.0
        )
        
        with patch.object(metrics_service.logger, 'warning') as mock_warning:
            metrics_service._trigger_alert("test_alert", alert, 90.0)
            
            assert alert.last_triggered is not None
            assert metrics_service._stats['alerts_triggered'] == 1
            mock_warning.assert_called_once()
    
    def test_cleanup_old_values(self, metrics_service):
        """Test cleanup of old metric values."""
        metrics_service.create_metric("test", MetricType.GAUGE)
        
        now = datetime.now()
        old_time = now - timedelta(hours=25)  # Older than 24 hours
        recent_time = now - timedelta(hours=1)
        
        metrics_service.record_value("test", 10, timestamp=old_time)
        metrics_service.record_value("test", 20, timestamp=recent_time)
        metrics_service.record_value("test", 30, timestamp=now)
        
        metrics_service._cleanup_old_values()
        
        metric = metrics_service._metrics["test"]
        assert len(metric.values) == 2  # Only recent values should remain
        assert metric.values[0].value == 20
        assert metric.values[1].value == 30
    
    def test_export_metrics_json(self, metrics_service):
        """Test exporting metrics to JSON."""
        metrics_service.create_metric("test", MetricType.GAUGE, MetricUnit.PERCENT, "Test metric")
        metrics_service.record_value("test", 50.5)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_path = f.name
        
        try:
            result = metrics_service.export_metrics(file_path, "json", window_seconds=3600)
            
            assert result is True
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "test" in data
            assert data["test"]["type"] == "gauge"
            assert data["test"]["unit"] == "percent"
            assert data["test"]["description"] == "Test metric"
            assert len(data["test"]["values"]) == 1
            assert data["test"]["values"][0]["value"] == 50.5
            
        finally:
            os.unlink(file_path)
    
    def test_export_metrics_csv(self, metrics_service):
        """Test exporting metrics to CSV."""
        metrics_service.create_metric("test", MetricType.COUNTER)
        metrics_service.record_value("test", 10)
        metrics_service.record_value("test", 20)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            file_path = f.name
        
        try:
            result = metrics_service.export_metrics(file_path, "csv", window_seconds=3600)
            
            assert result is True
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            assert len(lines) >= 3  # Header + 2 data rows
            assert "metric_name,timestamp,value,tags" in lines[0]
            assert "test," in lines[1]
            assert "test," in lines[2]
            
        finally:
            os.unlink(file_path)
    
    def test_export_metrics_exception(self, metrics_service):
        """Test export metrics exception handling."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.export_metrics("/invalid/path/file.json", "json")
                
                assert result is False
                mock_error.assert_called_once()
    
    def test_get_statistics(self, metrics_service):
        """Test getting service statistics."""
        metrics_service.create_metric("metric1", MetricType.GAUGE)
        metrics_service.create_metric("metric2", MetricType.COUNTER)
        metrics_service.record_value("metric1", 10)
        metrics_service.record_value("metric1", 20)
        
        stats = metrics_service.get_statistics()
        
        assert stats["total_metrics"] == 2
        assert stats["total_values_recorded"] >= 2
        assert stats["alerts_configured"] == 0
        assert stats["alerts_triggered"] == 0
        assert stats["active_collectors"] >= 0
        assert stats["memory_usage_values"] == 2
    
    def test_shutdown(self, metrics_service):
        """Test metrics service shutdown."""
        # Add a mock collector
        mock_collector = Mock()
        metrics_service._collectors["test"] = mock_collector
        
        with patch.object(metrics_service.logger, 'info') as mock_info:
            metrics_service.shutdown()
            
            assert metrics_service._stop_event.is_set()
            mock_collector.stop.assert_called_once()
            mock_info.assert_called_once()
    
    def test_shutdown_collector_exception(self, metrics_service):
        """Test shutdown with collector exception."""
        mock_collector = Mock()
        mock_collector.stop.side_effect = Exception("Stop error")
        metrics_service._collectors["error_collector"] = mock_collector
        
        with patch.object(metrics_service.logger, 'error') as mock_error:
            metrics_service.shutdown()
            
            mock_error.assert_called_once()


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_get_metrics_service_singleton(self):
        """Test metrics service singleton behavior."""
        with patch('metrics_service.MetricsService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            
            # Clear global instance
            import metrics_service
            metrics_service._metrics_service = None
            
            service1 = get_metrics_service()
            service2 = get_metrics_service()
            
            assert service1 == service2
            mock_service_class.assert_called_once()
    
    @patch('metrics_service.get_metrics_service')
    def test_record_counter(self, mock_get_service):
        """Test record_counter convenience function."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service._metrics = {}
        
        record_counter("test_counter", 5, tags={"source": "test"})
        
        mock_service.create_metric.assert_called_once_with(
            "test_counter", MetricType.COUNTER, MetricUnit.COUNT
        )
        mock_service.record_value.assert_called_once_with(
            "test_counter", 5, tags={"source": "test"}
        )
    
    @patch('metrics_service.get_metrics_service')
    def test_record_counter_existing_metric(self, mock_get_service):
        """Test record_counter with existing metric."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service._metrics = {"existing_counter": Mock()}
        
        record_counter("existing_counter", 3)
        
        mock_service.create_metric.assert_not_called()
        mock_service.record_value.assert_called_once_with("existing_counter", 3)
    
    @patch('metrics_service.get_metrics_service')
    def test_record_gauge(self, mock_get_service):
        """Test record_gauge convenience function."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service._metrics = {}
        
        record_gauge("test_gauge", 75.5)
        
        mock_service.create_metric.assert_called_once_with(
            "test_gauge", MetricType.GAUGE
        )
        mock_service.record_value.assert_called_once_with("test_gauge", 75.5)
    
    @patch('metrics_service.get_metrics_service')
    def test_record_timer(self, mock_get_service):
        """Test record_timer convenience function."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service._metrics = {}
        
        record_timer("test_timer", 125.7)
        
        mock_service.create_metric.assert_called_once_with(
            "test_timer", MetricType.TIMER, MetricUnit.MILLISECONDS
        )
        mock_service.record_value.assert_called_once_with("test_timer", 125.7)
    
    @patch('metrics_service.get_metrics_service')
    def test_record_rate(self, mock_get_service):
        """Test record_rate convenience function."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service._metrics = {}
        
        record_rate("test_rate", 10.5)
        
        mock_service.create_metric.assert_called_once_with(
            "test_rate", MetricType.RATE, MetricUnit.RATE_PER_SECOND
        )
        mock_service.record_value.assert_called_once_with("test_rate", 10.5)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create metrics service for edge case testing."""
        with patch('metrics_service.get_network_logging_manager'):
            service = MetricsService()
            service._stop_event.set()
            return service
    
    def test_metric_value_with_none_tags(self):
        """Test MetricValue creation with None tags."""
        value = MetricValue(timestamp=datetime.now(), value=10, tags=None)
        assert value.tags == {}
    
    def test_metric_with_none_tags(self):
        """Test Metric creation with None tags."""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque(),
            tags=None
        )
        assert metric.tags == {}
    
    def test_aggregator_with_infinite_values(self):
        """Test aggregator with infinite values."""
        with patch('metrics_service.get_network_logging_manager'):
            aggregator = MetricAggregator()
            
            values = [
                MetricValue(timestamp=datetime.now(), value=float('inf')),
                MetricValue(timestamp=datetime.now(), value=10),
                MetricValue(timestamp=datetime.now(), value=float('-inf'))
            ]
            
            # Most aggregations should handle infinite values
            result = aggregator.aggregate_values(values, "sum")
            assert result == float('inf')
            
            result = aggregator.aggregate_values(values, "count")
            assert result == 3
    
    def test_aggregator_with_nan_values(self):
        """Test aggregator with NaN values."""
        with patch('metrics_service.get_network_logging_manager'):
            aggregator = MetricAggregator()
            
            values = [
                MetricValue(timestamp=datetime.now(), value=float('nan')),
                MetricValue(timestamp=datetime.now(), value=10),
                MetricValue(timestamp=datetime.now(), value=20)
            ]
            
            # NaN should propagate in most operations
            result = aggregator.aggregate_values(values, "sum")
            assert str(result) == "nan"
    
    def test_metric_deque_overflow(self, metrics_service):
        """Test metric deque behavior when max values exceeded."""
        metrics_service.create_metric("overflow_test", MetricType.GAUGE, max_values=3)
        
        # Add more values than max_values
        for i in range(5):
            metrics_service.record_value("overflow_test", i)
        
        metric = metrics_service._metrics["overflow_test"]
        assert len(metric.values) == 3  # Should only keep last 3 values
        assert metric.values[0].value == 2  # First value should be index 2
        assert metric.values[-1].value == 4  # Last value should be index 4
    
    def test_concurrent_metric_access(self, metrics_service):
        """Test concurrent access to metrics."""
        metrics_service.create_metric("concurrent_test", MetricType.COUNTER)
        
        def record_values():
            for i in range(10):
                metrics_service.record_value("concurrent_test", i)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=record_values)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        metric = metrics_service._metrics["concurrent_test"]
        assert len(metric.values) == 30  # Should have all values
    
    def test_zero_window_size(self):
        """Test aggregator with zero window size."""
        with patch('metrics_service.get_network_logging_manager'):
            aggregator = MetricAggregator(window_size_seconds=0)
            
            metric = Metric(
                name="test",
                type=MetricType.GAUGE,
                unit=MetricUnit.NONE,
                description="Test",
                values=deque([
                    MetricValue(timestamp=datetime.now(), value=10)
                ])
            )
            
            values = aggregator.get_time_window_values(metric, 0)
            assert len(values) == 0  # No values should be within 0-second window
    
    def test_future_timestamp_values(self, metrics_service):
        """Test handling values with future timestamps."""
        metrics_service.create_metric("future_test", MetricType.GAUGE)
        
        future_time = datetime.now() + timedelta(hours=1)
        result = metrics_service.record_value("future_test", 100, timestamp=future_time)
        
        assert result is True
        values = metrics_service.get_metric_values("future_test", window_seconds=3600)
        assert len(values) == 1  # Future value should be included
    
    def test_empty_metric_name(self, metrics_service):
        """Test creating metric with empty name."""
        result = metrics_service.create_metric("", MetricType.GAUGE)
        assert result is True  # Should succeed with empty name
        assert "" in metrics_service._metrics


# Test configuration and fixtures for pytest
@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information."""
    return {
        "start_time": datetime.now(),
        "test_file": "test_metrics_service_2025-08-28.py",
        "target_module": "metrics_service.py"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["concurrent", "thread", "loop"]):
            item.add_marker(pytest.mark.slow)


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])