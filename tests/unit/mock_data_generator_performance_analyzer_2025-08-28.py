"""
Mock Data Generator for Performance Analyzer Tests
Generated: 2025-08-28

This module provides utilities for generating realistic test data for performance analyzer tests.
"""

import os
import random

# Import the performance analyzer components
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "utilities",
        "network",
        "network_connectivity_complex",
        "core",
    ),
)

from performance_analyzer import PerformanceMeasurement, PerformanceMetric


@dataclass
class NetworkScenario:
    """Represents a network performance scenario for testing."""

    name: str
    description: str
    latency_range: tuple
    throughput_range: tuple
    packet_loss_range: tuple
    jitter_range: tuple
    bandwidth_util_range: tuple
    duration_hours: int = 24


class MockDataGenerator:
    """Generates realistic mock data for performance analyzer testing."""

    # Predefined network scenarios
    SCENARIOS = {
        "excellent": NetworkScenario(
            name="Excellent Network",
            description="High-quality enterprise network with optimal performance",
            latency_range=(5, 25),
            throughput_range=(90, 120),
            packet_loss_range=(0.0, 0.5),
            jitter_range=(1, 8),
            bandwidth_util_range=(40, 70),
            duration_hours=24,
        ),
        "good": NetworkScenario(
            name="Good Network",
            description="Typical business network with good performance",
            latency_range=(20, 60),
            throughput_range=(50, 90),
            packet_loss_range=(0.2, 1.5),
            jitter_range=(5, 20),
            bandwidth_util_range=(50, 80),
            duration_hours=24,
        ),
        "degraded": NetworkScenario(
            name="Degraded Network",
            description="Network with performance issues",
            latency_range=(80, 150),
            throughput_range=(10, 40),
            packet_loss_range=(2.0, 8.0),
            jitter_range=(20, 50),
            bandwidth_util_range=(70, 95),
            duration_hours=24,
        ),
        "poor": NetworkScenario(
            name="Poor Network",
            description="Severely impacted network performance",
            latency_range=(150, 300),
            throughput_range=(1, 15),
            packet_loss_range=(5.0, 20.0),
            jitter_range=(40, 100),
            bandwidth_util_range=(85, 99),
            duration_hours=24,
        ),
        "variable": NetworkScenario(
            name="Variable Network",
            description="Network with highly variable performance",
            latency_range=(10, 200),
            throughput_range=(5, 100),
            packet_loss_range=(0.1, 15.0),
            jitter_range=(2, 80),
            bandwidth_util_range=(30, 95),
            duration_hours=24,
        ),
    }

    def __init__(self, seed: int = None):
        """Initialize the mock data generator."""
        if seed:
            random.seed(seed)

    def generate_measurements(
        self,
        scenario: str = "good",
        interface_name: str = "eth0",
        measurements_per_hour: int = 4,
        add_noise: bool = True,
    ) -> List[PerformanceMeasurement]:
        """Generate a list of performance measurements based on a scenario.

        Args:
            scenario: Scenario name from SCENARIOS
            interface_name: Network interface name
            measurements_per_hour: Number of measurements per hour
            add_noise: Whether to add random noise to values

        Returns:
            List of PerformanceMeasurement objects
        """
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")

        scenario_config = self.SCENARIOS[scenario]
        measurements = []

        # Calculate time intervals
        total_measurements = (
            scenario_config.duration_hours * measurements_per_hour
        )
        interval_minutes = 60 / measurements_per_hour

        base_time = datetime.now()

        for i in range(total_measurements):
            # Calculate timestamp (going backwards in time)
            timestamp = base_time - timedelta(minutes=i * interval_minutes)

            # Generate measurements for each metric
            for metric in PerformanceMetric:
                value = self._generate_metric_value(
                    metric, scenario_config, add_noise
                )
                unit = self._get_metric_unit(metric)

                measurement = PerformanceMeasurement(
                    metric=metric,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    interface_name=interface_name,
                    target=f"target_{i % 5 + 1}.example.com",  # Rotate targets
                    additional_data={
                        "scenario": scenario,
                        "measurement_index": i,
                        "generator": "MockDataGenerator",
                    },
                )
                measurements.append(measurement)

        return measurements

    def _generate_metric_value(
        self,
        metric: PerformanceMetric,
        scenario: NetworkScenario,
        add_noise: bool,
    ) -> float:
        """Generate a realistic value for a specific metric."""

        # Map metrics to scenario ranges
        range_map = {
            PerformanceMetric.LATENCY: scenario.latency_range,
            PerformanceMetric.THROUGHPUT: scenario.throughput_range,
            PerformanceMetric.PACKET_LOSS: scenario.packet_loss_range,
            PerformanceMetric.JITTER: scenario.jitter_range,
            PerformanceMetric.BANDWIDTH_UTILIZATION: scenario.bandwidth_util_range,
        }

        min_val, max_val = range_map[metric]

        # Generate base value
        base_value = random.uniform(min_val, max_val)

        if add_noise:
            # Add some random noise (±10% of range)
            noise_range = (max_val - min_val) * 0.1
            noise = random.uniform(-noise_range, noise_range)
            base_value += noise

            # Ensure value stays within reasonable bounds
            base_value = max(0, base_value)
            if metric == PerformanceMetric.PACKET_LOSS:
                base_value = min(100, base_value)
            elif metric == PerformanceMetric.BANDWIDTH_UTILIZATION:
                base_value = min(100, base_value)

        return round(base_value, 2)

    def _get_metric_unit(self, metric: PerformanceMetric) -> str:
        """Get the unit for a specific metric."""
        unit_map = {
            PerformanceMetric.LATENCY: "ms",
            PerformanceMetric.THROUGHPUT: "Mbps",
            PerformanceMetric.PACKET_LOSS: "%",
            PerformanceMetric.JITTER: "ms",
            PerformanceMetric.BANDWIDTH_UTILIZATION: "%",
        }
        return unit_map[metric]

    def generate_trend_data(
        self,
        metric: PerformanceMetric,
        trend_type: str = "stable",
        base_value: float = None,
        num_points: int = 20,
        interface_name: str = "eth0",
    ) -> List[PerformanceMeasurement]:
        """Generate measurement data with a specific trend.

        Args:
            metric: Performance metric to generate
            trend_type: "increasing", "decreasing", or "stable"
            base_value: Starting value (auto-generated if None)
            num_points: Number of data points
            interface_name: Interface name

        Returns:
            List of measurements with the specified trend
        """
        measurements = []

        # Set base value if not provided
        if base_value is None:
            good_scenario = self.SCENARIOS["good"]
            range_map = {
                PerformanceMetric.LATENCY: good_scenario.latency_range,
                PerformanceMetric.THROUGHPUT: good_scenario.throughput_range,
                PerformanceMetric.PACKET_LOSS: good_scenario.packet_loss_range,
                PerformanceMetric.JITTER: good_scenario.jitter_range,
                PerformanceMetric.BANDWIDTH_UTILIZATION: good_scenario.bandwidth_util_range,
            }
            min_val, max_val = range_map[metric]
            base_value = (min_val + max_val) / 2

        # Calculate trend parameters
        if trend_type == "increasing":
            trend_factor = 0.1  # 10% increase per step
        elif trend_type == "decreasing":
            trend_factor = -0.1  # 10% decrease per step
        else:  # stable
            trend_factor = 0.0

        base_time = datetime.now()
        unit = self._get_metric_unit(metric)

        for i in range(num_points):
            # Calculate value with trend
            trend_adjustment = base_value * trend_factor * i
            value = base_value + trend_adjustment

            # Add small random variation
            variation = value * random.uniform(-0.05, 0.05)
            value += variation

            # Ensure reasonable bounds
            value = max(0, value)
            if metric in [
                PerformanceMetric.PACKET_LOSS,
                PerformanceMetric.BANDWIDTH_UTILIZATION,
            ]:
                value = min(100, value)

            timestamp = base_time - timedelta(minutes=i * 10)

            measurement = PerformanceMeasurement(
                metric=metric,
                value=round(value, 2),
                unit=unit,
                timestamp=timestamp,
                interface_name=interface_name,
                additional_data={
                    "trend_type": trend_type,
                    "base_value": base_value,
                    "trend_index": i,
                },
            )
            measurements.append(measurement)

        return measurements

    def generate_multi_interface_data(
        self,
        interfaces: List[str] = None,
        scenario_per_interface: Dict[str, str] = None,
    ) -> Dict[str, List[PerformanceMeasurement]]:
        """Generate data for multiple network interfaces.

        Args:
            interfaces: List of interface names
            scenario_per_interface: Scenario for each interface

        Returns:
            Dictionary mapping interface names to measurement lists
        """
        if interfaces is None:
            interfaces = ["eth0", "wlan0", "eth1"]

        if scenario_per_interface is None:
            scenarios = ["excellent", "good", "degraded"]
            scenario_per_interface = {
                interface: scenarios[i % len(scenarios)]
                for i, interface in enumerate(interfaces)
            }

        results = {}
        for interface in interfaces:
            scenario = scenario_per_interface.get(interface, "good")
            results[interface] = self.generate_measurements(
                scenario=scenario,
                interface_name=interface,
                measurements_per_hour=2,  # Fewer measurements for multi-interface
            )

        return results

    def generate_performance_degradation_sequence(
        self, interface_name: str = "eth0", duration_hours: int = 6
    ) -> List[PerformanceMeasurement]:
        """Generate a sequence showing network performance degradation.

        Args:
            interface_name: Interface name
            duration_hours: Duration of the sequence

        Returns:
            List of measurements showing degradation
        """
        measurements = []
        base_time = datetime.now()

        # Define phases of degradation
        phases = [
            ("excellent", 0.3),  # 30% of time - excellent
            ("good", 0.3),  # 30% of time - good
            ("degraded", 0.3),  # 30% of time - degraded
            ("poor", 0.1),  # 10% of time - poor
        ]

        current_time = 0
        for scenario_name, time_fraction in phases:
            phase_duration = duration_hours * time_fraction
            phase_measurements = int(phase_duration * 4)  # 4 per hour

            scenario = self.SCENARIOS[scenario_name]

            for i in range(phase_measurements):
                timestamp = base_time - timedelta(
                    hours=current_time
                    + (i * phase_duration / phase_measurements)
                )

                # Generate measurements for all metrics
                for metric in PerformanceMetric:
                    value = self._generate_metric_value(metric, scenario, True)
                    unit = self._get_metric_unit(metric)

                    measurement = PerformanceMeasurement(
                        metric=metric,
                        value=value,
                        unit=unit,
                        timestamp=timestamp,
                        interface_name=interface_name,
                        additional_data={
                            "degradation_phase": scenario_name,
                            "phase_index": i,
                            "total_phases": len(phases),
                        },
                    )
                    measurements.append(measurement)

            current_time += phase_duration

        return measurements


# Factory function for easy access
def create_mock_generator(seed: int = None) -> MockDataGenerator:
    """Create a mock data generator instance."""
    return MockDataGenerator(seed=seed)


# Predefined data sets for common test scenarios
def get_test_dataset(dataset_name: str) -> List[PerformanceMeasurement]:
    """Get a predefined test dataset.

    Args:
        dataset_name: Name of the dataset

    Returns:
        List of performance measurements
    """
    generator = MockDataGenerator(seed=42)  # Fixed seed for reproducibility

    datasets = {
        "small_good": lambda: generator.generate_measurements(
            scenario="good", measurements_per_hour=1
        )[:20],
        "large_excellent": lambda: generator.generate_measurements(
            scenario="excellent", measurements_per_hour=6
        ),
        "degradation": lambda: generator.generate_performance_degradation_sequence(),
        "multi_interface": lambda: [
            m
            for measurements in generator.generate_multi_interface_data().values()
            for m in measurements
        ],
        "high_latency": lambda: generator.generate_trend_data(
            PerformanceMetric.LATENCY, "increasing", 50.0, 15
        ),
        "low_throughput": lambda: generator.generate_trend_data(
            PerformanceMetric.THROUGHPUT, "decreasing", 100.0, 15
        ),
    }

    if dataset_name not in datasets:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    return datasets[dataset_name]()


if __name__ == "__main__":
    # Example usage
    generator = MockDataGenerator(seed=42)

    print("Generating sample data...")
    measurements = generator.generate_measurements(
        "good", measurements_per_hour=2
    )
    print(f"Generated {len(measurements)} measurements")

    # Show sample
    for i, m in enumerate(measurements[:5]):
        print(f"{i+1}. {m.metric.value}: {m.value} {m.unit} at {m.timestamp}")
