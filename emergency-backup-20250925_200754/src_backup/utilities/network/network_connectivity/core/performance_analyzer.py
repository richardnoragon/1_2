"""Network performance analysis utilities."""

import statistics
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class PerformanceMetric(Enum):
    """Network performance metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    PACKET_LOSS = "packet_loss"
    JITTER = "jitter"
    BANDWIDTH_UTILIZATION = "bandwidth_utilization"


@dataclass
class PerformanceMeasurement:
    """Single performance measurement."""
    metric: PerformanceMetric
    value: float
    unit: str
    timestamp: datetime
    interface_name: Optional[str] = None
    target: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceReport:
    """Performance analysis report."""
    interface_name: str
    analysis_period: timedelta
    measurements: List[PerformanceMeasurement]
    statistics: Dict[str, Dict[str, float]]
    recommendations: List[str]
    overall_score: float  # 0.0 to 1.0


class PerformanceAnalyzer:
    """Analyzes network performance metrics and provides insights."""
    
    def __init__(self):
        """Initialize performance analyzer."""
        self.logger = logging.getLogger(
            'RFU.NetworkConnectivity.PerformanceAnalyzer'
        )
        
        # Performance data storage
        self.measurements: Dict[str, List[PerformanceMeasurement]] = {}
        self.max_measurements_per_interface = 1000
        
        # Performance thresholds for scoring
        self.thresholds = {
            PerformanceMetric.LATENCY: {
                'excellent': 20.0,  # ms
                'good': 50.0,
                'fair': 100.0,
                'poor': 200.0
            },
            PerformanceMetric.THROUGHPUT: {
                'excellent': 100.0,  # Mbps
                'good': 50.0,
                'fair': 10.0,
                'poor': 1.0
            },
            PerformanceMetric.PACKET_LOSS: {
                'excellent': 0.1,  # %
                'good': 1.0,
                'fair': 3.0,
                'poor': 5.0
            },
            PerformanceMetric.JITTER: {
                'excellent': 5.0,  # ms
                'good': 15.0,
                'fair': 30.0,
                'poor': 50.0
            },
            PerformanceMetric.BANDWIDTH_UTILIZATION: {
                'excellent': 70.0,  # %
                'good': 80.0,
                'fair': 90.0,
                'poor': 95.0
            }
        }
    
    def add_measurement(self, measurement: PerformanceMeasurement):
        """Add a performance measurement.
        
        Args:
            measurement: Performance measurement to add
        """
        interface_name = measurement.interface_name or "default"
        
        if interface_name not in self.measurements:
            self.measurements[interface_name] = []
        
        self.measurements[interface_name].append(measurement)
        
        # Limit measurements per interface
        if (len(self.measurements[interface_name]) > 
                self.max_measurements_per_interface):
            self.measurements[interface_name] = (
                self.measurements[interface_name]
                [-self.max_measurements_per_interface:]
            )
        
        self.logger.debug(
            f"Added {measurement.metric.value} measurement: "
            f"{measurement.value} {measurement.unit}"
        )
    
    def calculate_statistics(
        self,
        interface_name: str,
        metric: PerformanceMetric,
        hours: int = 1
    ) -> Dict[str, float]:
        """Calculate statistics for a specific metric.
        
        Args:
            interface_name: Interface to analyze
            metric: Performance metric to analyze
            hours: Hours of data to analyze
            
        Returns:
            Dictionary with statistical data
        """
        if interface_name not in self.measurements:
            return {}
        
        # Filter measurements by time and metric
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_measurements = [
            m for m in self.measurements[interface_name]
            if m.metric == metric and m.timestamp > cutoff_time
        ]
        
        if not filtered_measurements:
            return {}
        
        values = [m.value for m in filtered_measurements]
        
        try:
            stats = {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
            
            # Add percentiles
            if len(values) >= 4:
                sorted_values = sorted(values)
                stats['p25'] = self._percentile(sorted_values, 25)
                stats['p75'] = self._percentile(sorted_values, 75)
                stats['p95'] = self._percentile(sorted_values, 95)
                stats['p99'] = self._percentile(sorted_values, 99)
            
            return stats
        
        except statistics.StatisticsError:
            return {'count': len(values)}
    
    def _percentile(
            self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile value.
        
        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        if lower_index == upper_index:
            return sorted_values[lower_index]
        
        # Linear interpolation
        weight = index - lower_index
        return (sorted_values[lower_index] * (1 - weight) + 
                sorted_values[upper_index] * weight)
    
    def analyze_performance(
        self,
        interface_name: str,
        hours: int = 1
    ) -> PerformanceReport:
        """Analyze performance for an interface.
        
        Args:
            interface_name: Interface to analyze
            hours: Hours of data to analyze
            
        Returns:
            Performance analysis report
        """
        if interface_name not in self.measurements:
            return PerformanceReport(
                interface_name=interface_name,
                analysis_period=timedelta(hours=hours),
                measurements=[],
                statistics={},
                recommendations=[],
                overall_score=0.0
            )
        
        # Get measurements for the time period
        cutoff_time = datetime.now() - timedelta(hours=hours)
        period_measurements = [
            m for m in self.measurements[interface_name]
            if m.timestamp > cutoff_time
        ]
        
        # Calculate statistics for each metric
        statistics_data = {}
        metric_scores = {}
        
        for metric in PerformanceMetric:
            stats = self.calculate_statistics(interface_name, metric, hours)
            if stats:
                statistics_data[metric.value] = stats
                metric_scores[metric] = self._score_metric(
                    metric, stats['mean'])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            interface_name, statistics_data, metric_scores
        )
        
        # Calculate overall score
        overall_score = (sum(metric_scores.values()) / len(metric_scores) 
                        if metric_scores else 0.0)
        
        return PerformanceReport(
            interface_name=interface_name,
            analysis_period=timedelta(hours=hours),
            measurements=period_measurements,
            statistics=statistics_data,
            recommendations=recommendations,
            overall_score=overall_score
        )
    
    def _score_metric(self, metric: PerformanceMetric, value: float) -> float:
        """Score a metric value from 0.0 to 1.0.
        
        Args:
            metric: Performance metric
            value: Metric value to score
            
        Returns:
            Score from 0.0 (poor) to 1.0 (excellent)
        """
        if metric not in self.thresholds:
            return 0.5  # Neutral score for unknown metrics
        
        thresholds = self.thresholds[metric]
        
        # For metrics where lower is better (latency, packet loss, jitter)
        if metric in [PerformanceMetric.LATENCY, PerformanceMetric.PACKET_LOSS, 
                     PerformanceMetric.JITTER]:
            if value <= thresholds['excellent']:
                return 1.0
            elif value <= thresholds['good']:
                return 0.8
            elif value <= thresholds['fair']:
                return 0.6
            elif value <= thresholds['poor']:
                return 0.4
            else:
                return 0.2
        
        # For metrics where higher is better (throughput)
        elif metric == PerformanceMetric.THROUGHPUT:
            if value >= thresholds['excellent']:
                return 1.0
            elif value >= thresholds['good']:
                return 0.8
            elif value >= thresholds['fair']:
                return 0.6
            elif value >= thresholds['poor']:
                return 0.4
            else:
                return 0.2
        
        # For bandwidth utilization (optimal range)
        elif metric == PerformanceMetric.BANDWIDTH_UTILIZATION:
            if value <= thresholds['excellent']:
                return 1.0
            elif value <= thresholds['good']:
                return 0.8
            elif value <= thresholds['fair']:
                return 0.6
            elif value <= thresholds['poor']:
                return 0.4
            else:
                return 0.2
        
        return 0.5
    
    def _generate_recommendations(
        self,
        interface_name: str,
        statistics_data: Dict[str, Dict[str, float]],
        metric_scores: Dict[PerformanceMetric, float]
    ) -> List[str]:
        """Generate performance recommendations.
        
        Args:
            interface_name: Interface name
            statistics_data: Statistical data for metrics
            metric_scores: Scores for each metric
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check latency
        if (PerformanceMetric.LATENCY in metric_scores and 
                metric_scores[PerformanceMetric.LATENCY] < 0.6):
            latency_stats = statistics_data.get('latency', {})
            if latency_stats.get('mean', 0) > 100:
                recommendations.append(
                    "High latency detected. Consider checking network "
                    "congestion or switching to a closer server."
                )
        
        # Check packet loss
        if (PerformanceMetric.PACKET_LOSS in metric_scores and 
                metric_scores[PerformanceMetric.PACKET_LOSS] < 0.6):
            recommendations.append(
                "Packet loss detected. Check network stability and "
                "consider investigating network hardware issues."
            )
        
        # Check throughput
        if (PerformanceMetric.THROUGHPUT in metric_scores and 
                metric_scores[PerformanceMetric.THROUGHPUT] < 0.6):
            recommendations.append(
                "Low throughput detected. Consider upgrading network "
                "connection or optimizing network configuration."
            )
        
        # Check jitter
        if (PerformanceMetric.JITTER in metric_scores and 
                metric_scores[PerformanceMetric.JITTER] < 0.6):
            recommendations.append(
                "High jitter detected. This may affect real-time "
                "applications. Consider QoS configuration."
            )
        
        # Check bandwidth utilization
        if (PerformanceMetric.BANDWIDTH_UTILIZATION in metric_scores and 
                metric_scores[PerformanceMetric.BANDWIDTH_UTILIZATION] < 0.6):
            util_stats = statistics_data.get('bandwidth_utilization', {})
            if util_stats.get('mean', 0) > 90:
                recommendations.append(
                    "High bandwidth utilization detected. Consider "
                    "upgrading connection or implementing traffic shaping."
                )
        
        # General recommendations based on overall performance
        overall_score = (sum(metric_scores.values()) / len(metric_scores) 
                        if metric_scores else 0.0)
        
        if overall_score < 0.5:
            recommendations.append(
                "Overall network performance is poor. Consider "
                "comprehensive network diagnostics and optimization."
            )
        elif overall_score < 0.7:
            recommendations.append(
                "Network performance has room for improvement. "
                "Monitor trends and consider targeted optimizations."
            )
        
        if not recommendations:
            recommendations.append(
                "Network performance appears to be within acceptable ranges."
            )
        
        return recommendations
    
    def get_performance_trends(
        self,
        interface_name: str,
        metric: PerformanceMetric,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance trends for a metric.
        
        Args:
            interface_name: Interface to analyze
            metric: Performance metric
            hours: Hours of data to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        if interface_name not in self.measurements:
            return {}
        
        # Get measurements for the time period
        cutoff_time = datetime.now() - timedelta(hours=hours)
        measurements = [
            m for m in self.measurements[interface_name]
            if m.metric == metric and m.timestamp > cutoff_time
        ]
        
        if len(measurements) < 2:
            return {}
        
        # Sort by timestamp
        measurements.sort(key=lambda x: x.timestamp)
        
        # Calculate trend
        values = [m.value for m in measurements]
        timestamps = [(m.timestamp - measurements[0].timestamp).total_seconds() 
                     for m in measurements]
        
        # Simple linear regression for trend
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Determine trend direction
            if abs(slope) < 0.001:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
        else:
            slope = 0
            intercept = sum_y / n if n > 0 else 0
            trend = "stable"
        
        return {
            'metric': metric.value,
            'trend': trend,
            'slope': slope,
            'intercept': intercept,
            'data_points': len(measurements),
            'time_span_hours': hours,
            'latest_value': values[-1],
            'earliest_value': values[0],
            'change_percent': ((values[-1] - values[0]) / values[0] * 100 
                              if values[0] != 0 else 0)
        }
    
    def clear_measurements(self, interface_name: Optional[str] = None):
        """Clear performance measurements.
        
        Args:
            interface_name: Interface to clear (None for all)
        """
        if interface_name:
            if interface_name in self.measurements:
                del self.measurements[interface_name]
                self.logger.info(f"Cleared measurements for {interface_name}")
        else:
            self.measurements.clear()
            self.logger.info("Cleared all performance measurements")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance analyzer summary.
        
        Returns:
            Dictionary with analyzer summary
        """
        total_measurements = sum(len(measurements) 
                               for measurements in self.measurements.values())
        
        interfaces_with_data = list(self.measurements.keys())
        
        return {
            'total_interfaces': len(interfaces_with_data),
            'total_measurements': total_measurements,
            'interfaces_with_data': interfaces_with_data,
            'supported_metrics': [metric.value for metric in PerformanceMetric],
            'max_measurements_per_interface': self.max_measurements_per_interface
        }