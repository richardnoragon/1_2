"""
Comprehensive unit tests for performance_analyzer.py

Test file: test_performance_analyzer_2025-08-28.py
Target: performance_analyzer.py
Created: 2025-08-28
Framework: pytest

This module contains comprehensive unit tests for the PerformanceAnalyzer class
and related components including PerformanceMeasurement, PerformanceReport,
and PerformanceMetric enums.
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

# Import the modules to test
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'network',
    'network_connectivity_complex', 'core'
))

from performance_analyzer import (PerformanceAnalyzer, PerformanceMeasurement,
                                  PerformanceMetric, PerformanceReport)


class TestPerformanceMetric:
    """Test cases for PerformanceMetric enum."""
    
    def test_performance_metric_values(self):
        """Test that all expected metric values are present."""
        expected_metrics = {
            "latency": PerformanceMetric.LATENCY,
            "throughput": PerformanceMetric.THROUGHPUT,
            "packet_loss": PerformanceMetric.PACKET_LOSS,
            "jitter": PerformanceMetric.JITTER,
            "bandwidth_utilization": PerformanceMetric.BANDWIDTH_UTILIZATION
        }
        
        for value, metric in expected_metrics.items():
            assert metric.value == value
    
    def test_performance_metric_enum_integrity(self):
        """Test that enum has expected number of values."""
        assert len(PerformanceMetric) == 5


class TestPerformanceMeasurement:
    """Test cases for PerformanceMeasurement dataclass."""
    
    def test_performance_measurement_creation(self):
        """Test creating a PerformanceMeasurement instance."""
        timestamp = datetime.now()
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=25.5,
            unit="ms",
            timestamp=timestamp,
            interface_name="eth0",
            target="google.com",
            additional_data={"source": "ping"}
        )
        
        assert measurement.metric == PerformanceMetric.LATENCY
        assert measurement.value == pytest.approx(25.5)
        assert measurement.unit == "ms"
        assert measurement.timestamp == timestamp
        assert measurement.interface_name == "eth0"
        assert measurement.target == "google.com"
        assert measurement.additional_data == {"source": "ping"}
    
    def test_performance_measurement_optional_fields(self):
        """Test PerformanceMeasurement with only required fields."""
        timestamp = datetime.now()
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.THROUGHPUT,
            value=100.0,
            unit="Mbps",
            timestamp=timestamp
        )
        
        assert measurement.metric == PerformanceMetric.THROUGHPUT
        assert measurement.value == pytest.approx(100.0)
        assert measurement.unit == "Mbps"
        assert measurement.timestamp == timestamp
        assert measurement.interface_name is None
        assert measurement.target is None
        assert measurement.additional_data is None


class TestPerformanceReport:
    """Test cases for PerformanceReport dataclass."""
    
    def test_performance_report_creation(self):
        """Test creating a PerformanceReport instance."""
        measurements = [
            PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=20.0,
                unit="ms",
                timestamp=datetime.now()
            )
        ]
        
        report = PerformanceReport(
            interface_name="eth0",
            analysis_period=timedelta(hours=1),
            measurements=measurements,
            statistics={"latency": {"mean": 20.0}},
            recommendations=["Network performance is good"],
            overall_score=0.85
        )
        
        assert report.interface_name == "eth0"
        assert report.analysis_period == timedelta(hours=1)
        assert len(report.measurements) == 1
        assert report.statistics == {"latency": {"mean": 20.0}}
        assert report.recommendations == ["Network performance is good"]
        assert report.overall_score == pytest.approx(0.85)


class TestPerformanceAnalyzer:
    """Comprehensive test cases for PerformanceAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a fresh PerformanceAnalyzer instance for each test."""
        return PerformanceAnalyzer()
    
    @pytest.fixture
    def sample_measurements(self):
        """Create sample measurements for testing."""
        now = datetime.now()
        return [
            PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=20.0,
                unit="ms",
                timestamp=now - timedelta(minutes=30),
                interface_name="eth0"
            ),
            PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=25.0,
                unit="ms",
                timestamp=now - timedelta(minutes=20),
                interface_name="eth0"
            ),
            PerformanceMeasurement(
                metric=PerformanceMetric.THROUGHPUT,
                value=100.0,
                unit="Mbps",
                timestamp=now - timedelta(minutes=15),
                interface_name="eth0"
            ),
            PerformanceMeasurement(
                metric=PerformanceMetric.PACKET_LOSS,
                value=0.5,
                unit="%",
                timestamp=now - timedelta(minutes=10),
                interface_name="eth0"
            )
        ]
    
    def test_analyzer_initialization(self, analyzer):
        """Test PerformanceAnalyzer initialization."""
        assert isinstance(analyzer.measurements, dict)
        assert len(analyzer.measurements) == 0
        assert analyzer.max_measurements_per_interface == 1000
        assert isinstance(analyzer.thresholds, dict)
        assert len(analyzer.thresholds) == 5  # One for each metric
        
        # Test threshold structure
        for metric in PerformanceMetric:
            assert metric in analyzer.thresholds
            assert 'excellent' in analyzer.thresholds[metric]
            assert 'good' in analyzer.thresholds[metric]
            assert 'fair' in analyzer.thresholds[metric]
            assert 'poor' in analyzer.thresholds[metric]
    
    def test_add_measurement_single(self, analyzer):
        """Test adding a single measurement."""
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=datetime.now(),
            interface_name="eth0"
        )
        
        analyzer.add_measurement(measurement)
        
        assert "eth0" in analyzer.measurements
        assert len(analyzer.measurements["eth0"]) == 1
        assert analyzer.measurements["eth0"][0] == measurement
    
    def test_add_measurement_default_interface(self, analyzer):
        """Test adding measurement without interface name."""
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=datetime.now()
        )
        
        analyzer.add_measurement(measurement)
        
        assert "default" in analyzer.measurements
        assert len(analyzer.measurements["default"]) == 1
    
    def test_add_measurement_limit_enforcement(self, analyzer):
        """Test that measurement limit is enforced per interface."""
        # Set a low limit for testing
        analyzer.max_measurements_per_interface = 3
        
        for i in range(5):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=float(i),
                unit="ms",
                timestamp=datetime.now(),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        # Should only keep the last 3 measurements
        assert len(analyzer.measurements["eth0"]) == 3
        assert analyzer.measurements["eth0"][0].value == pytest.approx(2.0)
        assert analyzer.measurements["eth0"][-1].value == pytest.approx(4.0)
    
    def test_add_multiple_measurements(self, analyzer, sample_measurements):
        """Test adding multiple measurements."""
        for measurement in sample_measurements:
            analyzer.add_measurement(measurement)
        
        assert "eth0" in analyzer.measurements
        assert len(analyzer.measurements["eth0"]) == 4
    
    def test_calculate_statistics_basic(self, analyzer, sample_measurements):
        """Test basic statistics calculation."""
        # Add latency measurements
        for measurement in sample_measurements[:2]:  # Only latency measurements
            analyzer.add_measurement(measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        
        assert stats['count'] == 2
        assert stats['mean'] == pytest.approx(22.5)  # (20 + 25) / 2
        assert stats['median'] == pytest.approx(22.5)
        assert stats['min'] == pytest.approx(20.0)
        assert stats['max'] == pytest.approx(25.0)
        assert stats['std_dev'] == pytest.approx(3.5355, rel=1e-3)
    
    def test_calculate_statistics_no_data(self, analyzer):
        """Test statistics calculation with no data."""
        stats = analyzer.calculate_statistics("nonexistent", PerformanceMetric.LATENCY, 1)
        assert stats == {}
    
    def test_calculate_statistics_no_matching_metric(self, analyzer):
        """Test statistics calculation with no matching metric."""
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.THROUGHPUT,
            value=100.0,
            unit="Mbps",
            timestamp=datetime.now(),
            interface_name="eth0"
        )
        analyzer.add_measurement(measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        assert stats == {}
    
    def test_calculate_statistics_time_filtering(self, analyzer):
        """Test that statistics calculation respects time filtering."""
        now = datetime.now()
        
        # Add old measurement (outside time window)
        old_measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=100.0,
            unit="ms",
            timestamp=now - timedelta(hours=2),
            interface_name="eth0"
        )
        analyzer.add_measurement(old_measurement)
        
        # Add recent measurement (inside time window)
        recent_measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=now - timedelta(minutes=30),
            interface_name="eth0"
        )
        analyzer.add_measurement(recent_measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        
        # Should only include the recent measurement
        assert stats['count'] == 1
        assert stats['mean'] == pytest.approx(20.0)
    
    def test_calculate_statistics_percentiles(self, analyzer):
        """Test percentile calculation in statistics."""
        # Add enough measurements to trigger percentile calculation
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        now = datetime.now()
        
        for i, value in enumerate(values):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=float(value),
                unit="ms",
                timestamp=now - timedelta(minutes=i),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        
        assert 'p25' in stats
        assert 'p75' in stats
        assert 'p95' in stats
        assert 'p99' in stats
        assert stats['p25'] == pytest.approx(32.5, rel=1e-2)
        assert stats['p75'] == pytest.approx(77.5, rel=1e-2)
    
    def test_percentile_calculation(self, analyzer):
        """Test the _percentile method directly."""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test basic percentiles
        assert analyzer._percentile(values, 50) == pytest.approx(5.5)  # Median
        assert analyzer._percentile(values, 25) == pytest.approx(3.25)  # 25th percentile
        assert analyzer._percentile(values, 75) == pytest.approx(7.75)  # 75th percentile
        
        # Test edge cases
        assert analyzer._percentile([], 50) == pytest.approx(0.0)  # Empty list
        assert analyzer._percentile([5], 50) == pytest.approx(5.0)  # Single value
        assert analyzer._percentile([1, 2], 50) == pytest.approx(1.5)  # Two values
    
    def test_score_metric_latency(self, analyzer):
        """Test metric scoring for latency (lower is better)."""
        # Test excellent score
        assert analyzer._score_metric(PerformanceMetric.LATENCY, 15.0) == pytest.approx(1.0)
        
        # Test good score
        assert analyzer._score_metric(PerformanceMetric.LATENCY, 35.0) == pytest.approx(0.8)
        
        # Test fair score
        assert analyzer._score_metric(PerformanceMetric.LATENCY, 75.0) == pytest.approx(0.6)
        
        # Test poor score
        assert analyzer._score_metric(PerformanceMetric.LATENCY, 150.0) == pytest.approx(0.4)
        
        # Test very poor score
        assert analyzer._score_metric(PerformanceMetric.LATENCY, 300.0) == pytest.approx(0.2)
    
    def test_score_metric_throughput(self, analyzer):
        """Test metric scoring for throughput (higher is better)."""
        # Test excellent score
        assert analyzer._score_metric(PerformanceMetric.THROUGHPUT, 150.0) == pytest.approx(1.0)
        
        # Test good score
        assert analyzer._score_metric(PerformanceMetric.THROUGHPUT, 75.0) == pytest.approx(0.8)
        
        # Test fair score
        assert analyzer._score_metric(PerformanceMetric.THROUGHPUT, 25.0) == pytest.approx(0.6)
        
        # Test poor score
        assert analyzer._score_metric(PerformanceMetric.THROUGHPUT, 5.0) == pytest.approx(0.4)
        
        # Test very poor score
        assert analyzer._score_metric(PerformanceMetric.THROUGHPUT, 0.5) == pytest.approx(0.2)
    
    def test_score_metric_bandwidth_utilization(self, analyzer):
        """Test metric scoring for bandwidth utilization (optimal range)."""
        # Test excellent score
        assert analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 65.0) == pytest.approx(1.0)
        
        # Test good score
        assert analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 75.0) == pytest.approx(0.8)
        
        # Test fair score
        assert analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 85.0) == pytest.approx(0.6)
        
        # Test poor score
        assert analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 92.0) == pytest.approx(0.4)
        
        # Test very poor score
        assert analyzer._score_metric(PerformanceMetric.BANDWIDTH_UTILIZATION, 98.0) == pytest.approx(0.2)
    
    def test_analyze_performance_no_data(self, analyzer):
        """Test performance analysis with no data."""
        report = analyzer.analyze_performance("nonexistent", 1)
        
        assert report.interface_name == "nonexistent"
        assert report.analysis_period == timedelta(hours=1)
        assert len(report.measurements) == 0
        assert len(report.statistics) == 0
        assert len(report.recommendations) == 0
        assert report.overall_score == pytest.approx(0.0)
    
    def test_analyze_performance_with_data(self, analyzer, sample_measurements):
        """Test performance analysis with actual data."""
        for measurement in sample_measurements:
            analyzer.add_measurement(measurement)
        
        report = analyzer.analyze_performance("eth0", 1)
        
        assert report.interface_name == "eth0"
        assert report.analysis_period == timedelta(hours=1)
        assert len(report.measurements) == 4
        assert len(report.statistics) > 0
        assert len(report.recommendations) > 0
        assert 0.0 <= report.overall_score <= 1.0
    
    def test_generate_recommendations_high_latency(self, analyzer):
        """Test recommendations for high latency."""
        # Add high latency measurements
        now = datetime.now()
        for i in range(3):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=150.0,  # High latency
                unit="ms",
                timestamp=now - timedelta(minutes=i),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        # Calculate metrics and scores
        stats = {"latency": {"mean": 150.0}}
        scores = {PerformanceMetric.LATENCY: 0.4}  # Poor score
        
        recommendations = analyzer._generate_recommendations("eth0", stats, scores)
        
        assert any("High latency detected" in rec for rec in recommendations)
    
    def test_generate_recommendations_packet_loss(self, analyzer):
        """Test recommendations for packet loss."""
        stats = {"packet_loss": {"mean": 5.0}}
        scores = {PerformanceMetric.PACKET_LOSS: 0.4}
        
        recommendations = analyzer._generate_recommendations("eth0", stats, scores)
        
        assert any("Packet loss detected" in rec for rec in recommendations)
    
    def test_generate_recommendations_good_performance(self, analyzer):
        """Test recommendations for good performance."""
        stats = {
            "latency": {"mean": 15.0},
            "throughput": {"mean": 100.0}
        }
        scores = {
            PerformanceMetric.LATENCY: 1.0,
            PerformanceMetric.THROUGHPUT: 1.0
        }
        
        recommendations = analyzer._generate_recommendations("eth0", stats, scores)
        
        assert any("acceptable ranges" in rec for rec in recommendations)
    
    def test_get_performance_trends_no_data(self, analyzer):
        """Test trend analysis with no data."""
        trends = analyzer.get_performance_trends("nonexistent", PerformanceMetric.LATENCY, 24)
        assert trends == {}
    
    def test_get_performance_trends_insufficient_data(self, analyzer):
        """Test trend analysis with insufficient data."""
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=datetime.now(),
            interface_name="eth0"
        )
        analyzer.add_measurement(measurement)
        
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        assert trends == {}
    
    def test_get_performance_trends_stable(self, analyzer):
        """Test trend analysis for stable metrics."""
        now = datetime.now()
        
        # Add measurements with stable values
        for i in range(5):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=20.0,  # Stable value
                unit="ms",
                timestamp=now - timedelta(minutes=i * 10),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        
        assert trends['trend'] == 'stable'
        assert trends['metric'] == 'latency'
        assert trends['data_points'] == 5
        assert abs(trends['slope']) < 0.001
    
    def test_get_performance_trends_increasing(self, analyzer):
        """Test trend analysis for increasing metrics."""
        now = datetime.now()
        
        # Add measurements with increasing values
        for i in range(5):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=float(10 + i * 10),  # Increasing values
                unit="ms",
                timestamp=now - timedelta(minutes=i * 10),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        
        assert trends['trend'] == 'increasing'
        assert trends['slope'] > 0.001
    
    def test_get_performance_trends_decreasing(self, analyzer):
        """Test trend analysis for decreasing metrics."""
        now = datetime.now()
        
        # Add measurements with decreasing values
        for i in range(5):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=float(50 - i * 5),  # Decreasing values
                unit="ms",
                timestamp=now - timedelta(minutes=i * 10),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        
        assert trends['trend'] == 'decreasing'
        assert trends['slope'] < -0.001
    
    def test_clear_measurements_specific_interface(self, analyzer, sample_measurements):
        """Test clearing measurements for a specific interface."""
        # Add measurements to multiple interfaces
        for measurement in sample_measurements:
            analyzer.add_measurement(measurement)
        
        # Add measurement to different interface
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=30.0,
            unit="ms",
            timestamp=datetime.now(),
            interface_name="wlan0"
        )
        analyzer.add_measurement(measurement)
        
        # Clear measurements for eth0 only
        analyzer.clear_measurements("eth0")
        
        assert "eth0" not in analyzer.measurements
        assert "wlan0" in analyzer.measurements
        assert len(analyzer.measurements["wlan0"]) == 1
    
    def test_clear_measurements_all(self, analyzer, sample_measurements):
        """Test clearing all measurements."""
        for measurement in sample_measurements:
            analyzer.add_measurement(measurement)
        
        analyzer.clear_measurements()
        
        assert len(analyzer.measurements) == 0
    
    def test_get_summary_empty(self, analyzer):
        """Test summary with no data."""
        summary = analyzer.get_summary()
        
        assert summary['total_interfaces'] == 0
        assert summary['total_measurements'] == 0
        assert summary['interfaces_with_data'] == []
        assert len(summary['supported_metrics']) == 5
        assert summary['max_measurements_per_interface'] == 1000
    
    def test_get_summary_with_data(self, analyzer, sample_measurements):
        """Test summary with data."""
        for measurement in sample_measurements:
            analyzer.add_measurement(measurement)
        
        # Add measurement to different interface
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=30.0,
            unit="ms",
            timestamp=datetime.now(),
            interface_name="wlan0"
        )
        analyzer.add_measurement(measurement)
        
        summary = analyzer.get_summary()
        
        assert summary['total_interfaces'] == 2
        assert summary['total_measurements'] == 5
        assert set(summary['interfaces_with_data']) == {"eth0", "wlan0"}
        assert len(summary['supported_metrics']) == 5
    
    def test_edge_case_empty_statistics_calculation(self, analyzer):
        """Test statistics calculation edge cases."""
        # Test with single measurement
        measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=datetime.now(),
            interface_name="eth0"
        )
        analyzer.add_measurement(measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        
        assert stats['count'] == 1
        assert stats['mean'] == pytest.approx(20.0)
        assert stats['std_dev'] == pytest.approx(0.0)  # Single value has no deviation
    
    @patch('performance_analyzer.datetime')
    def test_time_based_filtering_edge_cases(self, mock_datetime, analyzer):
        """Test edge cases in time-based filtering."""
        # Mock current time
        mock_now = datetime(2025, 8, 28, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Add measurement exactly at the cutoff time
        cutoff_measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=20.0,
            unit="ms",
            timestamp=mock_now - timedelta(hours=1),  # Exactly 1 hour ago
            interface_name="eth0"
        )
        analyzer.add_measurement(cutoff_measurement)
        
        # Add measurement just after cutoff (should be excluded)
        old_measurement = PerformanceMeasurement(
            metric=PerformanceMetric.LATENCY,
            value=30.0,
            unit="ms",
            timestamp=mock_now - timedelta(hours=1, seconds=1),
            interface_name="eth0"
        )
        analyzer.add_measurement(old_measurement)
        
        stats = analyzer.calculate_statistics("eth0", PerformanceMetric.LATENCY, 1)
        
        # Should only include the cutoff measurement
        assert stats['count'] == 1
        assert stats['mean'] == pytest.approx(20.0)
    
    def test_invalid_metric_scoring(self, analyzer):
        """Test scoring behavior with unknown metric."""
        # Create a mock metric that's not in thresholds
        class UnknownMetric:
            value = "unknown"
        
        score = analyzer._score_metric(UnknownMetric(), 50.0)
        assert score == pytest.approx(0.5)  # Should return neutral score
    
    def test_division_by_zero_in_trends(self, analyzer):
        """Test trend calculation with zero values."""
        now = datetime.now()
        
        # Add measurements with zero values
        for i in range(3):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=0.0,
                unit="ms",
                timestamp=now - timedelta(minutes=i * 10),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 24)
        
        # Should handle division by zero gracefully
        assert 'change_percent' in trends
        assert trends['change_percent'] == 0
    
    def test_memory_management_large_datasets(self, analyzer):
        """Test memory management with large number of measurements."""
        # Set a small limit for testing
        analyzer.max_measurements_per_interface = 10
        
        # Add more measurements than the limit
        now = datetime.now()
        for i in range(20):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=float(i),
                unit="ms",
                timestamp=now - timedelta(minutes=i),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        # Should only keep the most recent measurements
        assert len(analyzer.measurements["eth0"]) == 10
        # Should have values 10-19 (most recent)
        values = [m.value for m in analyzer.measurements["eth0"]]
        assert values == [pytest.approx(float(i)) for i in range(10, 20)]


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple components."""
    
    @pytest.fixture
    def analyzer_with_realistic_data(self):
        """Create analyzer with realistic network performance data."""
        analyzer = PerformanceAnalyzer()
        now = datetime.now()
        
        # Simulate 24 hours of measurements
        for hour in range(24):
            base_time = now - timedelta(hours=hour)
            
            # Add measurements every 15 minutes
            for minute in [0, 15, 30, 45]:
                timestamp = base_time - timedelta(minutes=minute)
                
                # Simulate varying network conditions
                latency_base = 30.0 + (hour % 6) * 5  # Varies with time of day
                throughput_base = 80.0 - (hour % 12) * 2  # Decreases during peak hours
                
                measurements = [
                    PerformanceMeasurement(
                        metric=PerformanceMetric.LATENCY,
                        value=latency_base + (minute / 10),
                        unit="ms",
                        timestamp=timestamp,
                        interface_name="eth0"
                    ),
                    PerformanceMeasurement(
                        metric=PerformanceMetric.THROUGHPUT,
                        value=throughput_base - (minute / 20),
                        unit="Mbps",
                        timestamp=timestamp,
                        interface_name="eth0"
                    ),
                    PerformanceMeasurement(
                        metric=PerformanceMetric.PACKET_LOSS,
                        value=0.1 + (hour % 3) * 0.2,
                        unit="%",
                        timestamp=timestamp,
                        interface_name="eth0"
                    )
                ]
                
                for measurement in measurements:
                    analyzer.add_measurement(measurement)
        
        return analyzer
    
    def test_full_analysis_workflow(self, analyzer_with_realistic_data):
        """Test complete analysis workflow with realistic data."""
        analyzer = analyzer_with_realistic_data
        
        # Generate performance report
        report = analyzer.analyze_performance("eth0", 24)
        
        # Verify report completeness
        assert report.interface_name == "eth0"
        assert len(report.measurements) > 0
        assert len(report.statistics) > 0
        assert len(report.recommendations) > 0
        assert 0.0 <= report.overall_score <= 1.0
        
        # Verify statistics for each metric
        expected_metrics = ["latency", "throughput", "packet_loss"]
        for metric in expected_metrics:
            assert metric in report.statistics
            stats = report.statistics[metric]
            assert 'mean' in stats
            assert 'count' in stats
            assert stats['count'] > 0
        
        # Get trend analysis
        latency_trends = analyzer.get_performance_trends(
            "eth0", PerformanceMetric.LATENCY, 24
        )
        assert latency_trends['metric'] == 'latency'
        assert latency_trends['data_points'] > 0
        
        # Get summary
        summary = analyzer.get_summary()
        assert summary['total_interfaces'] == 1
        assert summary['total_measurements'] > 0
    
    def test_multi_interface_analysis(self):
        """Test analysis across multiple network interfaces."""
        analyzer = PerformanceAnalyzer()
        now = datetime.now()
        
        interfaces = ["eth0", "wlan0", "eth1"]
        
        # Add measurements for each interface
        for interface in interfaces:
            for i in range(10):
                measurement = PerformanceMeasurement(
                    metric=PerformanceMetric.LATENCY,
                    value=20.0 + interfaces.index(interface) * 10 + i,
                    unit="ms",
                    timestamp=now - timedelta(minutes=i * 5),
                    interface_name=interface
                )
                analyzer.add_measurement(measurement)
        
        # Analyze each interface
        reports = {}
        for interface in interfaces:
            reports[interface] = analyzer.analyze_performance(interface, 1)
        
        # Verify all interfaces have reports
        assert len(reports) == 3
        for interface, report in reports.items():
            assert report.interface_name == interface
            assert len(report.measurements) == 10
        
        # Verify summary shows all interfaces
        summary = analyzer.get_summary()
        assert summary['total_interfaces'] == 3
        assert set(summary['interfaces_with_data']) == set(interfaces)
    
    def test_performance_degradation_detection(self):
        """Test detection of performance degradation over time."""
        analyzer = PerformanceAnalyzer()
        now = datetime.now()
        
        # Simulate degrading performance
        for i in range(20):
            # Latency increases over time
            latency_value = 20.0 + i * 2.0
            
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.LATENCY,
                value=latency_value,
                unit="ms",
                timestamp=now - timedelta(minutes=(20 - i) * 5),
                interface_name="eth0"
            )
            analyzer.add_measurement(measurement)
        
        # Analyze trends
        trends = analyzer.get_performance_trends("eth0", PerformanceMetric.LATENCY, 2)
        
        assert trends['trend'] == 'increasing'
        assert trends['slope'] > 0
        assert trends['change_percent'] > 0
        
        # Generate report
        report = analyzer.analyze_performance("eth0", 2)
        
        # Should generate recommendations about high latency
        assert any("latency" in rec.lower() for rec in report.recommendations)
        assert report.overall_score < 0.8  # Performance should be degraded


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def test_start_time():
    """Record test start time for reporting."""
    return datetime.now()


@pytest.fixture(scope="session", autouse=True)
def test_session_info(test_start_time):
    """Print test session information."""
    print(f"\n{'='*60}")
    print(f"Performance Analyzer Test Suite")
    print(f"Test execution started: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target file: performance_analyzer.py")
    print(f"Test framework: pytest")
    print(f"{'='*60}")


# Test markers for categorizing tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.performance_analyzer
]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])