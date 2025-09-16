"""Comprehensive unit tests for metrics_service.py

Test file for the MetricsService module with comprehensive coverage
of all classes, methods, and edge cases.

Created: 2025-08-30
Framework: pytest
"""

import json
import os
# Import the modules under test
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, call, patch

import pytest

sys.path.insert(0, r'c:\Users\richardi\1_2\src\utilities\network\network_connectivity_complex\core')

from metrics_service import (Metric, MetricAggregator, MetricAlert,
                             MetricCollector, MetricsService, MetricType,
                             MetricUnit, MetricValue,
                             NetworkToolMetricsCollector,
                             SystemMetricsCollector, get_metrics_service,
                             record_counter, record_gauge, record_rate,
                             record_timer)


class TestMetricType:
    """Test cases for MetricType enum."""

    def test_metric_type_values(self):
        """Test all metric type values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"
        assert MetricType.RATE.value == "rate"

    def test_metric_type_enum_members(self):
        """Test metric type enum members."""
        assert len(MetricType) == 5
        assert MetricType.COUNTER in MetricType
        assert MetricType.GAUGE in MetricType


class TestMetricUnit:
    """Test cases for MetricUnit enum."""

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

    def test_metric_unit_enum_members(self):
        """Test metric unit enum members."""
        assert len(MetricUnit) == 9
        assert MetricUnit.NONE in MetricUnit
        assert MetricUnit.BYTES in MetricUnit


class TestMetricValue:
    """Test cases for MetricValue dataclass."""

    def test_metric_value_creation(self):
        """Test MetricValue creation."""
        timestamp = datetime.now()
        value = 42.0
        tags = {"source": "test"}
        
        metric_value = MetricValue(timestamp=timestamp, value=value, tags=tags)
        
        assert metric_value.timestamp == timestamp
        assert metric_value.value == value
        assert metric_value.tags == tags

    def test_metric_value_default_tags(self):
        """Test MetricValue with default tags."""
        timestamp = datetime.now()
        value = 42.0
        
        metric_value = MetricValue(timestamp=timestamp, value=value)
        
        assert metric_value.tags == {}

    def test_metric_value_none_tags(self):
        """Test MetricValue with None tags."""
        timestamp = datetime.now()
        value = 42.0
        
        metric_value = MetricValue(timestamp=timestamp, value=value, tags=None)
        
        assert metric_value.tags == {}

    def test_metric_value_different_types(self):
        """Test MetricValue with different value types."""
        timestamp = datetime.now()
        
        # Integer value
        mv_int = MetricValue(timestamp=timestamp, value=42)
        assert mv_int.value == 42
        assert isinstance(mv_int.value, int)
        
        # Float value
        mv_float = MetricValue(timestamp=timestamp, value=42.5)
        assert mv_float.value == 42.5
        assert isinstance(mv_float.value, float)


class TestMetric:
    """Test cases for Metric dataclass."""

    def test_metric_creation(self):
        """Test Metric creation."""
        name = "test_metric"
        metric_type = MetricType.GAUGE
        unit = MetricUnit.BYTES
        description = "Test metric"
        tags = {"environment": "test"}
        max_values = 500
        
        metric = Metric(
            name=name,
            type=metric_type,
            unit=unit,
            description=description,
            values=deque(),
            tags=tags,
            max_values=max_values
        )
        
        assert metric.name == name
        assert metric.type == metric_type
        assert metric.unit == unit
        assert metric.description == description
        assert metric.tags == tags
        assert metric.max_values == max_values
        assert isinstance(metric.values, deque)

    def test_metric_default_values(self):
        """Test Metric with default values."""
        metric = Metric(
            name="test",
            type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Test",
            values=deque()
        )
        
        assert metric.tags == {}
        assert metric.max_values == 1000

    def test_metric_values_deque_conversion(self):
        """Test Metric values conversion to deque."""
        values_list = [1, 2, 3]
        
        metric = Metric(
            name="test",
            type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            description="Test",
            values=values_list,
            max_values=100
        )
        
        assert isinstance(metric.values, deque)
        assert metric.values.maxlen == 100


class TestMetricAlert:
    """Test cases for MetricAlert dataclass."""

    def test_metric_alert_creation(self):
        """Test MetricAlert creation."""
        alert = MetricAlert(
            metric_name="test_metric",
            condition="gt",
            threshold=100.0,
            duration_seconds=30,
            enabled=True,
            cooldown_seconds=600
        )
        
        assert alert.metric_name == "test_metric"
        assert alert.condition == "gt"
        assert alert.threshold == 100.0
        assert alert.duration_seconds == 30
        assert alert.enabled is True
        assert alert.cooldown_seconds == 600
        assert alert.last_triggered is None

    def test_metric_alert_defaults(self):
        """Test MetricAlert with default values."""
        alert = MetricAlert(
            metric_name="test_metric",
            condition="lt",
            threshold=50
        )
        
        assert alert.duration_seconds == 60
        assert alert.enabled is True
        assert alert.cooldown_seconds == 300
        assert alert.last_triggered is None


class TestMetricAggregator:
    """Test cases for MetricAggregator class."""

    @pytest.fixture
    def aggregator(self):
        """Create MetricAggregator instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return MetricAggregator(window_size_seconds=60)

    @pytest.fixture
    def sample_values(self):
        """Create sample metric values."""
        base_time = datetime.now()
        return [
            MetricValue(timestamp=base_time - timedelta(seconds=30), value=10.0),
            MetricValue(timestamp=base_time - timedelta(seconds=20), value=20.0),
            MetricValue(timestamp=base_time - timedelta(seconds=10), value=30.0),
            MetricValue(timestamp=base_time, value=40.0),
        ]

    def test_aggregator_initialization(self, aggregator):
        """Test MetricAggregator initialization."""
        assert aggregator.window_size == 60

    def test_aggregate_values_avg(self, aggregator, sample_values):
        """Test average aggregation."""
        result = aggregator.aggregate_values(sample_values, "avg")
        assert result == 25.0  # (10+20+30+40)/4

    def test_aggregate_values_sum(self, aggregator, sample_values):
        """Test sum aggregation."""
        result = aggregator.aggregate_values(sample_values, "sum")
        assert result == 100.0

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
        assert result == 4

    def test_aggregate_values_median(self, aggregator, sample_values):
        """Test median aggregation."""
        result = aggregator.aggregate_values(sample_values, "median")
        assert result == 25.0

    def test_aggregate_values_stdev(self, aggregator, sample_values):
        """Test standard deviation aggregation."""
        result = aggregator.aggregate_values(sample_values, "stdev")
        assert result > 0

    def test_aggregate_values_empty_list(self, aggregator):
        """Test aggregation with empty values."""
        result = aggregator.aggregate_values([], "avg")
        assert result is None

    def test_aggregate_values_non_numeric(self, aggregator):
        """Test aggregation with non-numeric values."""
        values = [
            MetricValue(timestamp=datetime.now(), value="invalid"),
            MetricValue(timestamp=datetime.now(), value=None),
        ]
        result = aggregator.aggregate_values(values, "avg")
        assert result is None

    def test_aggregate_values_unknown_type(self, aggregator, sample_values):
        """Test aggregation with unknown type."""
        with patch.object(aggregator.logger, 'warning') as mock_warning:
            result = aggregator.aggregate_values(sample_values, "unknown")
            assert result == 25.0  # Should default to avg
            mock_warning.assert_called_once()

    def test_aggregate_values_exception(self, aggregator):
        """Test aggregation with exception."""
        with patch('statistics.mean', side_effect=Exception("Test error")):
            with patch.object(aggregator.logger, 'error') as mock_error:
                result = aggregator.aggregate_values([
                    MetricValue(timestamp=datetime.now(), value=10)
                ], "avg")
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
                MetricValue(timestamp=now - timedelta(seconds=120), value=1),  # Too old
                MetricValue(timestamp=now - timedelta(seconds=30), value=2),   # Within window
                MetricValue(timestamp=now - timedelta(seconds=10), value=3),   # Within window
                MetricValue(timestamp=now, value=4),                           # Within window
            ])
        )
        
        result = aggregator.get_time_window_values(metric, 60)
        assert len(result) == 3
        assert [v.value for v in result] == [2, 3, 4]

    def test_get_time_window_values_default_window(self, aggregator):
        """Test getting values with default window."""
        now = datetime.now()
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            unit=MetricUnit.NONE,
            description="Test",
            values=deque([
                MetricValue(timestamp=now - timedelta(seconds=30), value=1),
                MetricValue(timestamp=now, value=2),
            ])
        )
        
        result = aggregator.get_time_window_values(metric)
        assert len(result) == 2


class TestMetricCollector:
    """Test cases for MetricCollector class."""

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
        time.sleep(0.1)  # Let it start
        
        collector.stop()
        
        assert collector._is_active is False
        # Thread should stop within timeout

    def test_start_already_active(self, collector, mock_metrics_service):
        """Test starting already active collector."""
        collector._is_active = True
        collector.start(mock_metrics_service)
        
        assert collector._collection_thread is None

    def test_stop_inactive_collector(self, collector):
        """Test stopping inactive collector."""
        collector.stop()  # Should not raise exception
        assert collector._is_active is False

    def test_collection_loop_with_function(self, collector, mock_metrics_service):
        """Test collection loop with function."""
        def test_func():
            return {"test_metric": 42, "another_metric": 24}
        
        collector.add_collection_function(test_func)
        collector.start(mock_metrics_service)
        
        # Wait for at least one collection cycle
        time.sleep(1.5)
        collector.stop()
        
        # Verify metrics were recorded
        assert mock_metrics_service.record_value.called

    def test_collection_loop_with_exception(self, collector, mock_metrics_service):
        """Test collection loop with function exception."""
        def failing_func():
            raise Exception("Test error")
        
        collector.add_collection_function(failing_func)
        
        with patch.object(collector.logger, 'error') as mock_error:
            collector.start(mock_metrics_service)
            time.sleep(1.5)
            collector.stop()
            
            # Should log error but continue running
            mock_error.assert_called()


class TestSystemMetricsCollector:
    """Test cases for SystemMetricsCollector class."""

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
    def test_collect_system_metrics_success(self, mock_psutil, system_collector):
        """Test successful system metrics collection."""
        # Mock psutil components
        mock_psutil.cpu_percent.return_value = 50.0
        mock_memory = Mock()
        mock_memory.percent = 75.0
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB in bytes
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = Mock()
        mock_disk.used = 500 * 1024**3  # 500GB
        mock_disk.total = 1000 * 1024**3  # 1TB
        mock_psutil.disk_usage.return_value = mock_disk
        
        mock_net_io = Mock()
        mock_net_io.bytes_sent = 1000000
        mock_net_io.bytes_recv = 2000000
        mock_net_io.packets_sent = 1000
        mock_net_io.packets_recv = 2000
        mock_psutil.net_io_counters.return_value = mock_net_io
        
        # Call collection function
        result = system_collector._collect_system_metrics()
        
        # Verify results
        assert 'system.cpu.percent' in result
        assert result['system.cpu.percent'] == 50.0
        assert 'system.memory.percent' in result
        assert result['system.memory.percent'] == 75.0
        assert 'system.disk.percent' in result
        assert result['system.disk.percent'] == 50.0

    def test_collect_system_metrics_no_psutil(self, system_collector):
        """Test system metrics collection without psutil."""
        with patch('metrics_service.psutil', side_effect=ImportError):
            with patch.object(system_collector.logger, 'warning') as mock_warning:
                result = system_collector._collect_system_metrics()
                
                assert result == {}
                mock_warning.assert_called_with("psutil not available for system metrics")

    @patch('metrics_service.psutil')
    def test_collect_system_metrics_exception(self, mock_psutil, system_collector):
        """Test system metrics collection with exception."""
        mock_psutil.cpu_percent.side_effect = Exception("Test error")
        
        with patch.object(system_collector.logger, 'error') as mock_error:
            result = system_collector._collect_system_metrics()
            
            assert result == {}
            mock_error.assert_called()


class TestNetworkToolMetricsCollector:
    """Test cases for NetworkToolMetricsCollector class."""

    @pytest.fixture
    def tool_collector(self):
        """Create NetworkToolMetricsCollector instance."""
        with patch('metrics_service.get_network_logging_manager'):
            return NetworkToolMetricsCollector("test_tool")

    @pytest.fixture
    def mock_tool(self):
        """Create mock tool instance."""
        tool = Mock()
        tool.is_running = True
        tool.is_healthy = True
        tool._error_count = 5
        tool.get_current_data.return_value = {
            "connections": 10,
            "latency": 50.5,
            "bandwidth": 1000
        }
        return tool

    def test_tool_collector_initialization(self, tool_collector):
        """Test NetworkToolMetricsCollector initialization."""
        assert tool_collector.name == "NetworkTool.test_tool"
        assert tool_collector.tool_name == "test_tool"
        assert tool_collector._tool_instance is None

    def test_set_tool_instance(self, tool_collector, mock_tool):
        """Test setting tool instance."""
        tool_collector.set_tool_instance(mock_tool)
        
        assert tool_collector._tool_instance == mock_tool
        assert len(tool_collector._collection_functions) == 1

    def test_collect_tool_metrics_success(self, tool_collector, mock_tool):
        """Test successful tool metrics collection."""
        tool_collector.set_tool_instance(mock_tool)
        
        result = tool_collector._collect_tool_metrics()
        
        assert 'test_tool.is_running' in result
        assert result['test_tool.is_running'] == 1
        assert 'test_tool.is_healthy' in result
        assert result['test_tool.is_healthy'] == 1
        assert 'test_tool.error_count' in result
        assert result['test_tool.error_count'] == 5
        assert 'test_tool.connections' in result
        assert result['test_tool.connections'] == 10

    def test_collect_tool_metrics_no_instance(self, tool_collector):
        """Test tool metrics collection without instance."""
        result = tool_collector._collect_tool_metrics()
        assert result == {}

    def test_collect_tool_metrics_partial_attributes(self, tool_collector):
        """Test tool metrics collection with partial attributes."""
        tool = Mock()
        tool.is_running = False
        # Missing other attributes
        del tool.is_healthy
        del tool._error_count
        del tool.get_current_data
        
        tool_collector.set_tool_instance(tool)
        result = tool_collector._collect_tool_metrics()
        
        assert 'test_tool.is_running' in result
        assert result['test_tool.is_running'] == 0
        assert 'test_tool.is_healthy' not in result

    def test_collect_tool_metrics_exception(self, tool_collector, mock_tool):
        """Test tool metrics collection with exception."""
        mock_tool.get_current_data.side_effect = Exception("Test error")
        tool_collector.set_tool_instance(mock_tool)
        
        with patch.object(tool_collector.logger, 'error') as mock_error:
            result = tool_collector._collect_tool_metrics()
            
            # Should still get basic metrics
            assert 'test_tool.is_running' in result
            mock_error.assert_called()


class TestMetricsService:
    """Test cases for MetricsService class."""

    @pytest.fixture
    def metrics_service(self):
        """Create MetricsService instance."""
        with patch('metrics_service.get_network_logging_manager'):
            with patch.object(MetricsService, '_start_background_threads'):
                service = MetricsService()
                return service

    @pytest.fixture
    def sample_metric(self):
        """Create sample metric."""
        return Metric(
            name="test_metric",
            type=MetricType.GAUGE,
            unit=MetricUnit.BYTES,
            description="Test metric",
            values=deque()
        )

    def test_metrics_service_initialization(self, metrics_service):
        """Test MetricsService initialization."""
        assert isinstance(metrics_service._metrics, dict)
        assert isinstance(metrics_service._aggregator, MetricAggregator)
        assert isinstance(metrics_service._collectors, dict)
        assert isinstance(metrics_service._alerts, dict)
        assert 'default_max_values' in metrics_service._config

    def test_create_metric_success(self, metrics_service):
        """Test successful metric creation."""
        result = metrics_service.create_metric(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.BYTES,
            description="Test metric",
            tags={"env": "test"},
            max_values=500
        )
        
        assert result is True
        assert "test_metric" in metrics_service._metrics
        metric = metrics_service._metrics["test_metric"]
        assert metric.name == "test_metric"
        assert metric.type == MetricType.GAUGE
        assert metric.unit == MetricUnit.BYTES

    def test_create_metric_duplicate(self, metrics_service):
        """Test creating duplicate metric."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        with patch.object(metrics_service.logger, 'warning') as mock_warning:
            result = metrics_service.create_metric("test_metric", MetricType.COUNTER)
            
            assert result is False
            mock_warning.assert_called()

    def test_create_metric_exception(self, metrics_service):
        """Test metric creation with exception."""
        with patch.object(Metric, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.create_metric("test_metric", MetricType.GAUGE)
                
                assert result is False
                mock_error.assert_called()

    def test_record_value_existing_metric(self, metrics_service):
        """Test recording value for existing metric."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        timestamp = datetime.now()
        
        result = metrics_service.record_value(
            "test_metric", 42.0, 
            tags={"source": "test"}, 
            timestamp=timestamp
        )
        
        assert result is True
        metric = metrics_service._metrics["test_metric"]
        assert len(metric.values) == 1
        assert metric.values[0].value == 42.0
        assert metric.values[0].timestamp == timestamp

    def test_record_value_auto_create_int(self, metrics_service):
        """Test recording value with auto-creation (int)."""
        result = metrics_service.record_value("new_metric", 42)
        
        assert result is True
        assert "new_metric" in metrics_service._metrics
        metric = metrics_service._metrics["new_metric"]
        assert metric.type == MetricType.COUNTER

    def test_record_value_auto_create_float(self, metrics_service):
        """Test recording value with auto-creation (float)."""
        result = metrics_service.record_value("new_metric", 42.5)
        
        assert result is True
        assert "new_metric" in metrics_service._metrics
        metric = metrics_service._metrics["new_metric"]
        assert metric.type == MetricType.GAUGE

    def test_record_value_default_timestamp(self, metrics_service):
        """Test recording value with default timestamp."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        result = metrics_service.record_value("test_metric", 42.0)
        
        assert result is True
        metric = metrics_service._metrics["test_metric"]
        assert len(metric.values) == 1
        # Timestamp should be recent
        assert (datetime.now() - metric.values[0].timestamp).total_seconds() < 1

    def test_record_value_exception(self, metrics_service):
        """Test recording value with exception."""
        with patch.object(MetricValue, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.record_value("test_metric", 42.0)
                
                assert result is False
                mock_error.assert_called()

    def test_get_metric_existing(self, metrics_service, sample_metric):
        """Test getting existing metric."""
        metrics_service._metrics["test_metric"] = sample_metric
        
        result = metrics_service.get_metric("test_metric")
        
        assert result == sample_metric

    def test_get_metric_non_existing(self, metrics_service):
        """Test getting non-existing metric."""
        result = metrics_service.get_metric("non_existing")
        
        assert result is None

    def test_get_metric_value_latest(self, metrics_service):
        """Test getting latest metric value."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        metrics_service.record_value("test_metric", 42.0)
        metrics_service.record_value("test_metric", 84.0)
        
        result = metrics_service.get_metric_value("test_metric", "latest")
        
        assert result == 84.0

    def test_get_metric_value_aggregated(self, metrics_service):
        """Test getting aggregated metric value."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        metrics_service.record_value("test_metric", 10.0)
        metrics_service.record_value("test_metric", 20.0)
        
        with patch.object(metrics_service._aggregator, 'aggregate_values', return_value=15.0) as mock_agg:
            result = metrics_service.get_metric_value("test_metric", "avg")
            
            assert result == 15.0
            mock_agg.assert_called_once()

    def test_get_metric_value_no_metric(self, metrics_service):
        """Test getting value for non-existing metric."""
        result = metrics_service.get_metric_value("non_existing", "latest")
        
        assert result is None

    def test_get_metric_value_no_values(self, metrics_service):
        """Test getting value for metric with no values."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        result = metrics_service.get_metric_value("test_metric", "latest")
        
        assert result is None

    def test_get_metric_values(self, metrics_service):
        """Test getting metric values within time window."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        
        with patch.object(metrics_service._aggregator, 'get_time_window_values') as mock_get:
            mock_get.return_value = [Mock()]
            
            result = metrics_service.get_metric_values("test_metric", 3600)
            
            assert len(result) == 1
            mock_get.assert_called_once()

    def test_get_metric_values_no_metric(self, metrics_service):
        """Test getting values for non-existing metric."""
        result = metrics_service.get_metric_values("non_existing", 3600)
        
        assert result == []

    def test_get_metrics_summary(self, metrics_service):
        """Test getting metrics summary."""
        # Create metric with values
        metrics_service.create_metric("test_metric", MetricType.GAUGE, description="Test")
        metrics_service.record_value("test_metric", 42.0)
        
        with patch.object(metrics_service._aggregator, 'get_time_window_values') as mock_get:
            with patch.object(metrics_service._aggregator, 'aggregate_values') as mock_agg:
                mock_get.return_value = [Mock()]
                mock_agg.return_value = 42.0
                
                result = metrics_service.get_metrics_summary()
                
                assert "test_metric" in result
                assert result["test_metric"]["latest_value"] == 42.0
                assert result["test_metric"]["description"] == "Test"

    def test_add_tool_collector_success(self, metrics_service):
        """Test adding tool collector successfully."""
        mock_tool = Mock()
        
        with patch('metrics_service.NetworkToolMetricsCollector') as mock_collector_class:
            mock_collector = Mock()
            mock_collector_class.return_value = mock_collector
            
            result = metrics_service.add_tool_collector("test_tool", mock_tool)
            
            assert result is True
            assert "tool_test_tool" in metrics_service._collectors
            mock_collector.set_tool_instance.assert_called_with(mock_tool)
            mock_collector.start.assert_called_with(metrics_service)

    def test_add_tool_collector_exception(self, metrics_service):
        """Test adding tool collector with exception."""
        mock_tool = Mock()
        
        with patch('metrics_service.NetworkToolMetricsCollector', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.add_tool_collector("test_tool", mock_tool)
                
                assert result is False
                mock_error.assert_called()

    def test_add_alert_success(self, metrics_service):
        """Test adding alert successfully."""
        result = metrics_service.add_alert(
            "test_metric", "gt", 100.0, 
            duration_seconds=30, cooldown_seconds=600
        )
        
        assert result is True
        alert_name = "test_metric_gt_100.0"
        assert alert_name in metrics_service._alerts
        alert = metrics_service._alerts[alert_name]
        assert alert.metric_name == "test_metric"
        assert alert.condition == "gt"
        assert alert.threshold == 100.0

    def test_add_alert_exception(self, metrics_service):
        """Test adding alert with exception."""
        with patch.object(MetricAlert, '__init__', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.add_alert("test_metric", "gt", 100.0)
                
                assert result is False
                mock_error.assert_called()

    def test_evaluate_condition(self, metrics_service):
        """Test condition evaluation."""
        assert metrics_service._evaluate_condition(10, "gt", 5) is True
        assert metrics_service._evaluate_condition(10, "gt", 15) is False
        assert metrics_service._evaluate_condition(10, "lt", 15) is True
        assert metrics_service._evaluate_condition(10, "lt", 5) is False
        assert metrics_service._evaluate_condition(10, "eq", 10) is True
        assert metrics_service._evaluate_condition(10, "eq", 5) is False
        assert metrics_service._evaluate_condition(10, "gte", 10) is True
        assert metrics_service._evaluate_condition(10, "gte", 15) is False
        assert metrics_service._evaluate_condition(10, "lte", 10) is True
        assert metrics_service._evaluate_condition(10, "lte", 5) is False
        assert metrics_service._evaluate_condition(10, "unknown", 5) is False

    def test_export_metrics_json(self, metrics_service):
        """Test exporting metrics to JSON."""
        # Create test metric with values
        metrics_service.create_metric("test_metric", MetricType.GAUGE, description="Test")
        timestamp = datetime.now()
        metrics_service.record_value("test_metric", 42.0, timestamp=timestamp)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_path = f.name
        
        try:
            with patch.object(metrics_service._aggregator, 'get_time_window_values') as mock_get:
                mock_value = MetricValue(timestamp=timestamp, value=42.0, tags={})
                mock_get.return_value = [mock_value]
                
                result = metrics_service.export_metrics(file_path, "json", 3600)
                
                assert result is True
                
                # Verify file contents
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                assert "test_metric" in data
                assert data["test_metric"]["description"] == "Test"
                assert len(data["test_metric"]["values"]) == 1
        
        finally:
            os.unlink(file_path)

    def test_export_metrics_csv(self, metrics_service):
        """Test exporting metrics to CSV."""
        # Create test metric with values
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        timestamp = datetime.now()
        metrics_service.record_value("test_metric", 42.0, timestamp=timestamp)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            file_path = f.name
        
        try:
            with patch.object(metrics_service._aggregator, 'get_time_window_values') as mock_get:
                mock_value = MetricValue(timestamp=timestamp, value=42.0, tags={})
                mock_get.return_value = [mock_value]
                
                result = metrics_service.export_metrics(file_path, "csv", 3600)
                
                assert result is True
                
                # Verify file exists and has content
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert "metric_name" in content
                    assert "test_metric" in content
        
        finally:
            os.unlink(file_path)

    def test_export_metrics_exception(self, metrics_service):
        """Test exporting metrics with exception."""
        with patch('builtins.open', side_effect=Exception("Test error")):
            with patch.object(metrics_service.logger, 'error') as mock_error:
                result = metrics_service.export_metrics("/invalid/path", "json")
                
                assert result is False
                mock_error.assert_called()

    def test_get_statistics(self, metrics_service):
        """Test getting service statistics."""
        metrics_service.create_metric("test_metric", MetricType.GAUGE)
        metrics_service.record_value("test_metric", 42.0)
        
        result = metrics_service.get_statistics()
        
        assert "total_metrics" in result
        assert "total_values_recorded" in result
        assert "alerts_configured" in result
        assert "memory_usage_values" in result
        assert result["total_metrics"] == 1

    def test_shutdown(self, metrics_service):
        """Test service shutdown."""
        # Add mock collectors
        mock_collector = Mock()
        metrics_service._collectors["test"] = mock_collector
        
        # Mock threads
        metrics_service._cleanup_thread = Mock()
        metrics_service._cleanup_thread.is_alive.return_value = True
        metrics_service._alert_thread = Mock()
        metrics_service._alert_thread.is_alive.return_value = True
        
        metrics_service.shutdown()
        
        # Verify shutdown actions
        assert metrics_service._stop_event.is_set()
        mock_collector.stop.assert_called_once()
        metrics_service._cleanup_thread.join.assert_called_once()
        metrics_service._alert_thread.join.assert_called_once()


class TestGlobalFunctions:
    """Test cases for global functions."""

    def test_get_metrics_service_singleton(self):
        """Test that get_metrics_service returns singleton."""
        with patch('metrics_service.MetricsService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            
            # Clear global instance
            import metrics_service
            metrics_service._metrics_service = None
            
            # First call should create instance
            result1 = get_metrics_service()
            assert result1 == mock_instance
            mock_service_class.assert_called_once()
            
            # Second call should return same instance
            result2 = get_metrics_service()
            assert result2 == mock_instance
            # Should not create new instance
            mock_service_class.assert_called_once()

    def test_record_counter(self):
        """Test record_counter convenience function."""
        with patch('metrics_service.get_metrics_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service._metrics = {}
            
            record_counter("test_counter", 5, tags={"env": "test"})
            
            mock_service.create_metric.assert_called_with(
                "test_counter", MetricType.COUNTER, MetricUnit.COUNT
            )
            mock_service.record_value.assert_called_with(
                "test_counter", 5, tags={"env": "test"}
            )

    def test_record_counter_existing_metric(self):
        """Test record_counter with existing metric."""
        with patch('metrics_service.get_metrics_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service._metrics = {"test_counter": Mock()}
            
            record_counter("test_counter", 5)
            
            mock_service.create_metric.assert_not_called()
            mock_service.record_value.assert_called_with("test_counter", 5)

    def test_record_gauge(self):
        """Test record_gauge convenience function."""
        with patch('metrics_service.get_metrics_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service._metrics = {}
            
            record_gauge("test_gauge", 42.5)
            
            mock_service.create_metric.assert_called_with(
                "test_gauge", MetricType.GAUGE
            )
            mock_service.record_value.assert_called_with("test_gauge", 42.5)

    def test_record_timer(self):
        """Test record_timer convenience function."""
        with patch('metrics_service.get_metrics_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service._metrics = {}
            
            record_timer("test_timer", 150.5)
            
            mock_service.create_metric.assert_called_with(
                "test_timer", MetricType.TIMER, MetricUnit.MILLISECONDS
            )
            mock_service.record_value.assert_called_with("test_timer", 150.5)

    def test_record_rate(self):
        """Test record_rate convenience function."""
        with patch('metrics_service.get_metrics_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            mock_service._metrics = {}
            
            record_rate("test_rate", 25.0)
            
            mock_service.create_metric.assert_called_with(
                "test_rate", MetricType.RATE, MetricUnit.RATE_PER_SECOND
            )
            mock_service.record_value.assert_called_with("test_rate", 25.0)


class TestComplexScenarios:
    """Test cases for complex scenarios and edge cases."""

    @pytest.fixture
    def full_metrics_service(self):
        """Create a fully configured MetricsService."""
        with patch('metrics_service.get_network_logging_manager'):
            with patch.object(MetricsService, '_start_background_threads'):
                service = MetricsService()
                return service

    def test_concurrent_metric_operations(self, full_metrics_service):
        """Test concurrent metric operations."""
        import threading
        import time
        
        results = []
        
        def record_metrics(thread_id):
            for i in range(10):
                result = full_metrics_service.record_value(f"thread_{thread_id}_metric", i)
                results.append(result)
                time.sleep(0.01)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=record_metrics, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert all(results)
        # Should have 3 metrics (one per thread)
        assert len(full_metrics_service._metrics) == 3

    def test_metric_lifecycle(self, full_metrics_service):
        """Test complete metric lifecycle."""
        # Create metric
        assert full_metrics_service.create_metric(
            "lifecycle_metric", MetricType.GAUGE, MetricUnit.BYTES, "Test metric"
        )
        
        # Record multiple values
        timestamps = []
        for i in range(5):
            timestamp = datetime.now() + timedelta(seconds=i)
            timestamps.append(timestamp)
            assert full_metrics_service.record_value(
                "lifecycle_metric", float(i * 10), timestamp=timestamp
            )
        
        # Get values
        values = full_metrics_service.get_metric_values("lifecycle_metric", 3600)
        assert len(values) == 5
        
        # Get aggregated values
        latest = full_metrics_service.get_metric_value("lifecycle_metric", "latest")
        assert latest == 40.0
        
        avg = full_metrics_service.get_metric_value("lifecycle_metric", "avg")
        assert avg == 20.0  # (0+10+20+30+40)/5
        
        # Get summary
        summary = full_metrics_service.get_metrics_summary()
        assert "lifecycle_metric" in summary

    def test_alert_system_integration(self, full_metrics_service):
        """Test alert system integration."""
        # Create metric and alert
        full_metrics_service.create_metric("alert_metric", MetricType.GAUGE)
        full_metrics_service.add_alert("alert_metric", "gt", 50.0, duration_seconds=1)
        
        # Record values that should trigger alert
        for _ in range(3):
            full_metrics_service.record_value("alert_metric", 60.0)
        
        # Mock alert checking
        with patch.object(full_metrics_service, '_trigger_alert') as mock_trigger:
            full_metrics_service._check_alerts()
            # Should trigger alert since all values > 50
            mock_trigger.assert_called()

    def test_memory_management(self, full_metrics_service):
        """Test memory management with max values."""
        # Create metric with small max values
        full_metrics_service.create_metric(
            "memory_test", MetricType.GAUGE, max_values=3
        )
        
        # Record more values than max
        for i in range(10):
            full_metrics_service.record_value("memory_test", float(i))
        
        # Should only keep last 3 values
        metric = full_metrics_service.get_metric("memory_test")
        assert len(metric.values) == 3
        assert [v.value for v in metric.values] == [7.0, 8.0, 9.0]


# Test configuration and fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Ensure clean state for global metrics service
    import metrics_service
    metrics_service._metrics_service = None
    
    yield
    
    # Clean up after tests
    metrics_service._metrics_service = None


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    import metrics_service
    metrics_service._metrics_service = None
    yield
    metrics_service._metrics_service = None


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("metric_type,unit", [
    (MetricType.COUNTER, MetricUnit.COUNT),
    (MetricType.GAUGE, MetricUnit.BYTES),
    (MetricType.HISTOGRAM, MetricUnit.SECONDS),
    (MetricType.TIMER, MetricUnit.MILLISECONDS),
    (MetricType.RATE, MetricUnit.RATE_PER_SECOND),
])
def test_metric_types_and_units(metric_type, unit):
    """Test different metric types and units."""
    with patch('metrics_service.get_network_logging_manager'):
        with patch.object(MetricsService, '_start_background_threads'):
            service = MetricsService()
            
            result = service.create_metric(
                f"test_{metric_type.value}", metric_type, unit
            )
            
            assert result is True
            metric = service.get_metric(f"test_{metric_type.value}")
            assert metric.type == metric_type
            assert metric.unit == unit


@pytest.mark.parametrize("aggregation_type,values,expected", [
    ("avg", [10, 20, 30], 20.0),
    ("sum", [10, 20, 30], 60.0),
    ("min", [10, 20, 30], 10.0),
    ("max", [10, 20, 30], 30.0),
    ("count", [10, 20, 30], 3),
    ("median", [10, 20, 30, 40], 25.0),
])
def test_aggregation_functions(aggregation_type, values, expected):
    """Test different aggregation functions."""
    with patch('metrics_service.get_network_logging_manager'):
        aggregator = MetricAggregator()
        
        metric_values = [
            MetricValue(timestamp=datetime.now(), value=float(v))
            for v in values
        ]
        
        result = aggregator.aggregate_values(metric_values, aggregation_type)
        assert result == expected


@pytest.mark.parametrize("condition,value,threshold,expected", [
    ("gt", 10, 5, True),
    ("gt", 5, 10, False),
    ("lt", 5, 10, True),
    ("lt", 10, 5, False),
    ("eq", 10, 10, True),
    ("eq", 10, 5, False),
    ("gte", 10, 10, True),
    ("gte", 10, 15, False),
    ("lte", 10, 10, True),
    ("lte", 15, 10, False),
])
def test_alert_conditions(condition, value, threshold, expected):
    """Test different alert conditions."""
    with patch('metrics_service.get_network_logging_manager'):
        with patch.object(MetricsService, '_start_background_threads'):
            service = MetricsService()
            
            result = service._evaluate_condition(value, condition, threshold)
            assert result == expected


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=metrics_service",
        "--cov-report=html",
        "--cov-report=json",
        "--cov-report=term-missing"
    ])