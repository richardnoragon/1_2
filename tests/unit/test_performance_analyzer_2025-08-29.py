"""
Comprehensive Unit Tests for performance_analyzer.py
Created: 2025-08-29
Target: src/utilities/network/network_connectivity_complex/core/performance_analyzer.py

This module provides complete test coverage for all components of the
performance_analyzer module including PerformanceMetric, PerformanceMeasurement,
PerformanceReport, and PerformanceAnalyzer classes.
"""

import os
import statistics
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Add source path for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Import the module under test
from src.tools.network.network_connectivity_complex.core.performance_analyzer import (
    PerformanceAnalyzer, PerformanceMeasurement, PerformanceMetric,
    PerformanceReport)


class TestPerformanceMetric:
    """Test cases for PerformanceMetric enum."""
    
    @pytest.mark.unit
    def test_performance_metric_values(self):
        """Test that all expected enum values exist."""
        expected_metrics = {
            'LATENCY': 'latency',
            'THROUGHPUT': 'throughput',
            'PACKET_LOSS': 'packet_loss',
            'JITTER': 'jitter',
            'BANDWIDTH_UTILIZATION': 'bandwidth_utilization'
        }
        
        for attr_name, expected_value in expected_metrics.items():
            assert hasattr(PerformanceMetric, attr_name)
            metric = getattr(PerformanceMetric, attr_name)
            assert metric.value == expected_value
    
    @pytest.mark.unit
    def test_performance_metric_string_values(self):
        """Test string representations of metrics."""
        assert PerformanceMetric.LATENCY.value == "latency"
        assert PerformanceMetric.THROUGHPUT.value == "throughput"
        assert PerformanceMetric.PACKET_LOSS.value == "packet_loss"
        assert PerformanceMetric.JITTER.value == "jitter"
        assert PerformanceMetric.BANDWIDTH_UTILIZATION.value == "bandwidth_utilization"
    
    @pytest.mark.unit
    def test_performance_metric_iteration(self):
        """Test that enum can be iterated."""
        metrics = list(PerformanceMetric)
        assert len(metrics) == 5
        assert PerformanceMetric.LATENCY in metrics
        assert PerformanceMetric.THROUGHPUT in metrics
    
    @pytest.mark.unit
    def test_performance_metric_membership(self):
        """Test membership operations."""
        assert PerformanceMetric.LATENCY in PerformanceMetric
        # String values are not members of the enum
        assert "latency" not in [m.value for m in PerformanceMetric]


class TestPerformanceMeasurement:
    """Test cases for PerformanceMeasurement dataclass."""
    
    @pytest.mark.unit
    def test_performance_measurement_creation_required_fields(self):
        """Test creation with only required fields."""
        timestamp = datetime.now()
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=50.0,
            unit="ms",
            timestamp=timestamp
        )
        
        assert measurement.metric == PerformanceMetric.LATENCY
        assert measurement.value == 50.0
        assert measurement.unit == "ms"
        assert measurement.timestamp == timestamp
        assert measurement.interface_name is None
        assert measurement.target is None
        assert measurement.additional_data is None
    
    @pytest.mark.unit
    def test_performance_measurement_creation_all_fields(self):
        """Test creation with all fields populated."""
        timestamp = datetime.now()
        additional_data = {"protocol": "icmp", "packet_size": 64}
        
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.THROUGHPUT,
            value=100.5,
            unit="Mbps",
            timestamp=timestamp,
            interface_name="eth0",
            target="8.8.8.8",
            additional_data=additional_data
        )
        
        assert measurement.metric == PerformanceMetric.THROUGHPUT
        assert measurement.value == 100.5
        assert measurement.unit == "Mbps"
        assert measurement.timestamp == timestamp
        assert measurement.interface_name == "eth0"
        assert measurement.target == "8.8.8.8"
        assert measurement.additional_data == additional_data
    
    @pytest.mark.unit
    def test_performance_measurement_field_types(self):
        """Test that fields have correct types."""
        timestamp = datetime.now()
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=50.0,
            unit="ms",
            timestamp=timestamp
        )
        
        assert isinstance(measurement.metric, PerformanceMetric)
        assert isinstance(measurement.value, float)
        assert isinstance(measurement.unit, str)
        assert isinstance(measurement.timestamp, datetime)
    
    @pytest.mark.unit
    def test_performance_measurement_equality(self):
        """Test dataclass equality comparison."""
        timestamp = datetime.now()
        
        measurement1 = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=50.0,
            unit="ms",
            timestamp=timestamp
        )
        
        measurement2 = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=50.0,
            unit="ms",
            timestamp=timestamp
        )
        
        measurement3 = PerformanceMeasurement(
            metric=PerformanceMetric.THROUGHPUT,
            value=50.0,
            unit="ms",
            timestamp=timestamp
        )
        
        assert measurement1 == measurement2
        assert measurement1 != measurement3


class TestPerformanceReport:
    """Test cases for PerformanceReport dataclass."""
    
    @pytest.mark.unit
    def test_performance_report_creation(self):
        """Test PerformanceReport creation."""
        measurements = []
        statistics_data = {"latency": {"mean": 50.0, "std_dev": 10.0}}
        recommendations = ["Check network stability"]
        
        report = PerformanceReport(
            interface_name="eth0",
            analysis_period=timedelta(hours=1),
            measurements=measurements,
            statistics=statistics_data,
            recommendations=recommendations,
            overall_score=0.8
        )
        
        assert report.interface_name == "eth0"
        assert report.analysis_period == timedelta(hours=1)
        assert report.measurements == measurements
        assert report.statistics == statistics_data
        assert report.recommendations == recommendations
        assert report.overall_score == 0.8
    
    @pytest.mark.unit
    def test_performance_report_field_types(self):
        """Test PerformanceReport field types."""
        report = PerformanceReport(
            interface_name="eth0",
            analysis_period=timedelta(hours=1),
            measurements=[],
            statistics={},
            recommendations=[],
            overall_score=0.5
        )
        
        assert isinstance(report.interface_name, str)
        assert isinstance(report.analysis_period, timedelta)
        assert isinstance(report.measurements, list)
        assert isinstance(report.statistics, dict)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.overall_score, float)


class TestPerformanceAnalyzerInit:
    """Test cases for PerformanceAnalyzer initialization."""
    
    @pytest.mark.unit
    def test_init_logger_setup(self):
        """Test logger initialization."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            analyzer = PerformanceAnalyzer()
            
            mock_get_logger.assert_called_with('RFU.NetworkConnectivity.PerformanceAnalyzer')
            assert analyzer.logger == mock_logger
    
    @pytest.mark.unit
    def test_init_measurements_dict_empty(self):
        """Test measurements dictionary is initialized empty."""
        analyzer = PerformanceAnalyzer()
        assert analyzer.measurements == {}
        assert isinstance(analyzer.measurements, dict)
    
    @pytest.mark.unit
    def test_init_max_measurements_default(self):
        """Test max measurements per interface default value."""
        analyzer = PerformanceAnalyzer()
        assert analyzer.max_measurements_per_interface == 1000
    
    @pytest.mark.unit
    def test_init_thresholds_structure(self):
        """Test thresholds dictionary structure."""
        analyzer = PerformanceAnalyzer()
        
        # Verify all metrics have thresholds
        for metric in PerformanceMetric:
            assert metric in analyzer.thresholds
            
            # Verify threshold categories
            threshold_categories = ['excellent', 'good', 'fair', 'poor']
            for category in threshold_categories:
                assert category in analyzer.thresholds[metric]
    
    @pytest.mark.unit
    def test_init_thresholds_values(self):
        """Test specific threshold values."""
        analyzer = PerformanceAnalyzer()
        
        # Test latency thresholds
        latency_thresholds = analyzer.thresholds[PerformanceMetric.LATENCY]
        assert latency_thresholds['excellent'] == 20.0
        assert latency_thresholds['good'] == 50.0
        assert latency_thresholds['fair'] == 100.0
        assert latency_thresholds['poor'] == 200.0
        
        # Test throughput thresholds
        throughput_thresholds = analyzer.thresholds[PerformanceMetric.THROUGHPUT]
        assert throughput_thresholds['excellent'] == 100.0
        assert throughput_thresholds['good'] == 50.0


class TestPerformanceAnalyzerAddMeasurement:
    """Test cases for add_measurement method."""
    
    @pytest.mark.unit
    def test_add_measurement_new_interface(self, empty_analyzer, sample_measurement):
        """Test adding measurement to new interface."""
        empty_analyzer.add_measurement(sample_measurement)
        
        interface_name = sample_measurement.interface_name
        assert interface_name in empty_analyzer.measurements
        assert len(empty_analyzer.measurements[interface_name]) == 1
        assert empty_analyzer.measurements[interface_name][0] == sample_measurement
    
    @pytest.mark.unit
    def test_add_measurement_existing_interface(self, empty_analyzer, performance_measurement_factory):
        """Test adding measurement to existing interface."""
        measurement1 = performance_measurement_factory(value=50.0)
        measurement2 = performance_measurement_factory(value=60.0)
        
        empty_analyzer.add_measurement(measurement1)
        empty_analyzer.add_measurement(measurement2)
        
        interface_name = measurement1.interface_name
        assert len(empty_analyzer.measurements[interface_name]) == 2
        assert measurement1 in empty_analyzer.measurements[interface_name]
        assert measurement2 in empty_analyzer.measurements[interface_name]
    
    @pytest.mark.unit
    def test_add_measurement_limit_enforcement(self, empty_analyzer, performance_measurement_factory):
        """Test measurement limit enforcement."""
        # Add more than the limit
        for i in range(1005):
            measurement = performance_measurement_factory(value=float(i))
            empty_analyzer.add_measurement(measurement)
        
        interface_name = "eth0"
        # Should only keep the last 1000 measurements
        assert len(empty_analyzer.measurements[interface_name]) == 1000
        # The first measurement should be the one with value 5.0 (1005 - 1000)
        assert empty_analyzer.measurements[interface_name][0].value == 5.0
        # The last measurement should be the one with value 1004.0
        assert empty_analyzer.measurements[interface_name][-1].value == 1004.0
    
    @pytest.mark.unit
    def test_add_measurement_default_interface_name(self, empty_analyzer, performance_measurement_factory):
        """Test default interface name when None provided."""
        measurement = performance_measurement_factory(interface_name=None)
        empty_analyzer.add_measurement(measurement)
        
        assert "default" in empty_analyzer.measurements
        assert len(empty_analyzer.measurements["default"]) == 1
    
    @pytest.mark.unit
    def test_add_measurement_logging(self, empty_analyzer, sample_measurement):
        """Test logging output during add_measurement."""
        with patch.object(empty_analyzer.logger, 'debug') as mock_debug:
            empty_analyzer.add_measurement(sample_measurement)
            
            # Verify debug log was called
            mock_debug.assert_called_once()
            log_message = mock_debug.call_args[0][0]
            assert "Added latency measurement" in log_message
            assert "50.0 ms" in log_message


class TestPerformanceAnalyzerCalculateStatistics:
    """Test cases for calculate_statistics method."""
    
    @pytest.mark.unit
    @pytest.mark.statistics
    def test_calculate_statistics_valid_data(self, populated_analyzer):
        """Test statistics calculation with valid data."""
        stats = populated_analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 24)
        
        assert 'count' in stats
        assert 'mean' in stats
        assert 'median' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'std_dev' in stats
        assert stats['count'] > 0
        assert stats['mean'] > 0
    
    @pytest.mark.unit
    def test_calculate_statistics_empty_interface(self, empty_analyzer):
        """Test statistics calculation with empty interface."""
        stats = empty_analyzer.calculate_statistics("nonexistent", PerformanceMetric.LATENCY, 1)
        assert stats == {}
    
    @pytest.mark.unit
    def test_calculate_statistics_no_matching_measurements(self, populated_analyzer):
        """Test statistics calculation with no matching measurements."""
        # Use a very short time window to ensure no matches
        with patch('src.tools.network.network_connectivity_complex.core.performance_analyzer.datetime') as mock_dt:
            # Set current time to very early so no measurements match
            mock_dt.now.return_value = datetime(2020, 1, 1)
            stats = populated_analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
            assert stats == {}
    
    @pytest.mark.unit
    def test_calculate_statistics_single_value(self, empty_analyzer, performance_measurement_factory):
        """Test statistics calculation with single value."""
        measurement = performance_measurement_factory(value=50.0)
        empty_analyzer.add_measurement(measurement)
        
        stats = empty_analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 24)
        
        assert stats['count'] == 1
        assert stats['mean'] == 50.0
        assert stats['median'] == 50.0
        assert stats['std_dev'] == 0.0
    
    @pytest.mark.unit
    def test_calculate_statistics_percentiles(self, empty_analyzer, performance_measurement_factory):
        """Test percentile calculations."""
        # Add enough measurements for percentiles
        values = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        for value in values:
            measurement = performance_measurement_factory(value=value)
            empty_analyzer.add_measurement(measurement)
        
        stats = empty_analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 24)
        
        assert 'p25' in stats
        assert 'p75' in stats
        assert 'p95' in stats
        assert 'p99' in stats
        assert stats['p25'] <= stats['p75']
        assert stats['p75'] <= stats['p95']


class TestPerformanceAnalyzerPercentile:
    """Test cases for _percentile helper method."""
    
    @pytest.mark.unit
    def test_percentile_empty_list(self, empty_analyzer):
        """Test percentile calculation with empty list."""
        result = empty_analyzer._percentile([], 50)
        assert result == 0.0
    
    @pytest.mark.unit
    def test_percentile_single_value(self, empty_analyzer):
        """Test percentile calculation with single value."""
        result = empty_analyzer._percentile([42.0], 50)
        assert result == 42.0
    
    @pytest.mark.unit
    def test_percentile_two_values(self, empty_analyzer):
        """Test percentile calculation with two values."""
        result = empty_analyzer._percentile([10.0, 20.0], 50)
        assert result == 15.0  # Median of 10 and 20
    
    @pytest.mark.unit
    def test_percentile_multiple_values(self, empty_analyzer):
        """Test percentile calculation with multiple values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        
        # Test various percentiles
        p25 = empty_analyzer._percentile(values, 25)
        p50 = empty_analyzer._percentile(values, 50)
        p75 = empty_analyzer._percentile(values, 75)
        
        assert p25 < p50 < p75
        assert 2.0 <= p25 <= 3.5
        assert 5.0 <= p50 <= 6.0
        assert 7.5 <= p75 <= 9.0
    
    @pytest.mark.unit
    def test_percentile_boundary_values(self, empty_analyzer):
        """Test percentile calculation with boundary values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        # 0th percentile should be minimum
        p0 = empty_analyzer._percentile(values, 0)
        assert p0 == 1.0
        
        # 100th percentile should be maximum
        p100 = empty_analyzer._percentile(values, 100)
        assert p100 == 5.0


class TestPerformanceAnalyzerScoreMetric:
    """Test cases for _score_metric method."""
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_latency_excellent(self, empty_analyzer):
        """Test scoring for excellent latency."""
        score = empty_analyzer._score_metric(PerformanceMetric.LATENCY, 15.0)
        assert score == 1.0  # Excellent threshold is 20.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_latency_poor(self, empty_analyzer):
        """Test scoring for poor latency."""
        score = empty_analyzer._score_metric(PerformanceMetric.LATENCY, 300.0)
        assert score == 0.2  # Above poor threshold of 200.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_throughput_excellent(self, empty_analyzer):
        """Test scoring for excellent throughput."""
        score = empty_analyzer._score_metric(PerformanceMetric.THROUGHPUT, 150.0)
        assert score == 1.0  # Above excellent threshold of 100.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_throughput_poor(self, empty_analyzer):
        """Test scoring for poor throughput."""
        score = empty_analyzer._score_metric(PerformanceMetric.THROUGHPUT, 0.5)
        assert score == 0.2  # Below poor threshold of 1.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_bandwidth_utilization_optimal(self, empty_analyzer):
        """Test scoring for optimal bandwidth utilization."""
        score = empty_analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 65.0)
        assert score == 1.0  # Below excellent threshold of 70.0
    
    @pytest.mark.unit
    @pytest.mark.scoring
    def test_score_metric_unknown_metric(self, empty_analyzer):
        """Test scoring for unknown metric returns neutral score."""
        # Create a mock metric not in thresholds
        empty_analyzer.thresholds = {}  # Clear thresholds
        score = empty_analyzer._score_metric(PerformanceMetric.LATENCY, 50.0)
        assert score == 0.5  # Neutral score


class TestPerformanceAnalyzerGenerateRecommendations:
    """Test cases for _generate_recommendations method."""
    
    @pytest.mark.unit
    @pytest.mark.recommendations
    def test_generate_recommendations_high_latency(self, empty_analyzer):
        """Test recommendations for high latency."""
        statistics_data = {'latency': {'mean': 150.0}}
        metric_scores = {PerformanceMetric.LATENCY: 0.4}
        
        recommendations = empty_analyzer._generate_recommendations(
            "eth0", statistics_data, metric_scores
        )
        
        assert any("High latency detected" in rec for rec in recommendations)
    
    @pytest.mark.unit
    @pytest.mark.recommendations
    def test_generate_recommendations_packet_loss(self, empty_analyzer):
        """Test recommendations for packet loss."""
        statistics_data = {}
        metric_scores = {PerformanceMetric.PACKET_LOSS: 0.4}
        
        recommendations = empty_analyzer._generate_recommendations(
            "eth0", statistics_data, metric_scores
        )
        
        assert any("Packet loss detected" in rec for rec in recommendations)
    
    @pytest.mark.unit
    @pytest.mark.recommendations
    def test_generate_recommendations_good_performance(self, empty_analyzer):
        """Test recommendations for good performance."""
        statistics_data = {}
        metric_scores = {
            PerformanceMetric.LATENCY: 0.9,
            PerformanceMetric.THROUGHPUT: 0.9,
            PerformanceMetric.PACKET_LOSS: 0.9
        }
        
        recommendations = empty_analyzer._generate_recommendations(
            "eth0", statistics_data, metric_scores
        )
        
        assert any("within acceptable ranges" in rec for rec in recommendations)


class TestPerformanceAnalyzerClearMeasurements:
    """Test cases for clear_measurements method."""
    
    @pytest.mark.unit
    def test_clear_measurements_specific_interface(self, populated_analyzer):
        """Test clearing specific interface."""
        # Verify data exists
        assert "eth0" in populated_analyzer.measurements
        initial_count = len(populated_analyzer.measurements)
        
        with patch.object(populated_analyzer.logger, 'info') as mock_info:
            populated_analyzer.clear_measurements("eth0")
            
            assert "eth0" not in populated_analyzer.measurements
            mock_info.assert_called_once_with("Cleared measurements for eth0")
    
    @pytest.mark.unit
    def test_clear_measurements_all_interfaces(self, populated_analyzer):
        """Test clearing all interfaces."""
        # Verify data exists
        assert len(populated_analyzer.measurements) > 0
        
        with patch.object(populated_analyzer.logger, 'info') as mock_info:
            populated_analyzer.clear_measurements(None)
            
            assert len(populated_analyzer.measurements) == 0
            mock_info.assert_called_once_with("Cleared all performance measurements")
    
    @pytest.mark.unit
    def test_clear_measurements_nonexistent_interface(self, populated_analyzer):
        """Test clearing non-existent interface."""
        initial_count = len(populated_analyzer.measurements)
        
        populated_analyzer.clear_measurements("nonexistent")
        
        # Should not affect existing measurements
        assert len(populated_analyzer.measurements) == initial_count


class TestPerformanceAnalyzerGetSummary:
    """Test cases for get_summary method."""
    
    @pytest.mark.unit
    def test_get_summary_no_data(self, empty_analyzer):
        """Test summary with no data."""
        summary = empty_analyzer.get_summary()
        
        assert summary['total_interfaces'] == 0
        assert summary['total_measurements'] == 0
        assert summary['interfaces_with_data'] == []
        assert 'supported_metrics' in summary
        assert 'max_measurements_per_interface' in summary
    
    @pytest.mark.unit
    def test_get_summary_with_data(self, populated_analyzer):
        """Test summary with data."""
        summary = populated_analyzer.get_summary()
        
        assert summary['total_interfaces'] > 0
        assert summary['total_measurements'] > 0
        assert len(summary['interfaces_with_data']) > 0
        assert summary['max_measurements_per_interface'] == 1000
        
        # Check supported metrics
        expected_metrics = ['latency', 'throughput', 'packet_loss', 'jitter', 'bandwidth_utilization']
        assert all(metric in summary['supported_metrics'] for metric in expected_metrics)


class TestPerformanceAnalyzerEdgeCases:
    """Test cases for edge cases and error handling."""
    
    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_analyze_performance_no_interface_data(self, empty_analyzer):
        """Test analyze_performance with no interface data."""
        report = empty_analyzer.analyze_performance("nonexistent", 1)
        
        assert report.interface_name == "nonexistent"
        assert report.analysis_period == timedelta(hours=1)
        assert report.measurements == []
        assert report.statistics == {}
        assert report.recommendations == []
        assert report.overall_score == 0.0
    
    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_get_performance_trends_insufficient_data(self, empty_analyzer, performance_measurement_factory):
        """Test trend analysis with insufficient data."""
        # Add only one measurement
        measurement = performance_measurement_factory()
        empty_analyzer.add_measurement(measurement)
        
        trends = empty_analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        assert trends == {}
    
    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_statistics_error_handling(self, empty_analyzer, performance_measurement_factory):
        """Test statistics calculation error handling."""
        # This should test the StatisticsError exception path
        with patch('statistics.mean', side_effect=statistics.StatisticsError("Mock error")):
            measurement = performance_measurement_factory()
            empty_analyzer.add_measurement(measurement)
            
            stats = empty_analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 24)
            # Should return count only when statistics fail
            assert 'count' in stats
            assert len(stats) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])