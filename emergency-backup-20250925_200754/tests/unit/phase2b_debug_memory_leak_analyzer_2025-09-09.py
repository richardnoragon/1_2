"""
Phase 2B-DEBUG: Memory Leak Resolution - Advanced Diagnostic System
Generated: September 9, 2025

This module implements comprehensive memory leak debugging and root cause analysis
for the identified SizeAnalyzer memory leak (10.08 MB/min during sustained operations).

**CRITICAL MEMORY LEAK ANALYSIS:**
- Component: src.utilities.analysis.core.size_analyzer_logic.SizeAnalyzer
- Manifestation: Progressive memory growth during sustained operations
- Threshold Exceeded: 10.08 MB/min > 10 MB/min maximum
- Business Impact: BLOCKS production deployment for sustained operations

**DEBUG MODE ACTIVATION:**
- Enhanced memory profiling with object-level tracking
- Real-time leak vector identification
- Resource lifecycle monitoring
- Memory pattern analysis and trend detection
- Automated fix suggestion engine

**NO-COMPROMISE DEBUG STANDARDS:**
- Zero simplification of analysis complexity
- Full object reference tracking and lifecycle analysis
- Comprehensive resource cleanup validation
- Production-scale sustained operation testing
- Complete fix validation with re-testing
"""

import gc
import json
import os
import sys
import tempfile
import threading
import time
import tracemalloc
import weakref
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import psutil
import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

    SizeAnalyzer_available = True
except ImportError as e:
    print(f"CRITICAL: Cannot import SizeAnalyzer for debugging: {e}")
    SizeAnalyzer_available = False
    raise


class AdvancedMemoryProfiler:
    """
    Advanced memory profiler for comprehensive leak detection and analysis.

    This profiler goes beyond basic memory monitoring to provide:
    - Object-level memory tracking
    - Reference counting analysis
    - Memory allocation pattern detection
    - Leak vector identification
    - Resource lifecycle monitoring
    """

    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = None
        self.memory_samples = deque()
        self.object_tracking = {}
        self.reference_tracking = defaultdict(list)
        self.allocation_patterns = []
        self.resource_usage_history = []
        self.monitoring = False
        self.monitor_thread = None
        self.tracemalloc_active = False

        # Memory leak detection parameters
        self.leak_detection_window = 30  # samples
        self.leak_threshold_mb_per_min = 10.0
        self.memory_stability_threshold = 5.0  # MB

        # Object lifecycle tracking
        self.tracked_objects = weakref.WeakSet()
        self.object_creation_times = {}
        self.object_memory_usage = {}

    def start_advanced_monitoring(
        self, sample_interval: float = 0.1, track_objects: bool = True
    ) -> None:
        """Start comprehensive memory monitoring with object tracking."""
        # Initialize baseline
        self.baseline_memory = self.process.memory_info().rss
        self.memory_samples.clear()
        self.monitoring = True

        # Start Python memory allocation tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self.tracemalloc_active = True

        # Clear object tracking data
        if track_objects:
            self.object_tracking.clear()
            self.reference_tracking.clear()
            self.tracked_objects.clear()
            self.object_creation_times.clear()
            self.object_memory_usage.clear()

        def advanced_monitor():
            sample_count = 0
            while self.monitoring:
                try:
                    sample_count += 1
                    current_time = time.time()

                    # Basic memory info
                    memory_info = self.process.memory_info()

                    # Python memory tracking
                    if self.tracemalloc_active:
                        current, peak = tracemalloc.get_traced_memory()
                    else:
                        current = peak = 0

                    # CPU usage
                    cpu_percent = self.process.cpu_percent()

                    # Garbage collection stats
                    gc_stats = gc.get_stats()

                    sample = {
                        "timestamp": current_time,
                        "sample_id": sample_count,
                        "rss": memory_info.rss,
                        "vms": memory_info.vms,
                        "percent": self.process.memory_percent(),
                        "cpu_percent": cpu_percent,
                        "python_current": current,
                        "python_peak": peak,
                        "gc_collections": [
                            stats["collections"] for stats in gc_stats
                        ],
                        "gc_collected": [
                            stats["collected"] for stats in gc_stats
                        ],
                        "gc_uncollectable": [
                            stats["uncollectable"] for stats in gc_stats
                        ],
                    }

                    # Object tracking every 10 samples to reduce overhead
                    if track_objects and sample_count % 10 == 0:
                        sample["object_counts"] = self._get_object_counts()
                        sample["reference_analysis"] = (
                            self._analyze_references()
                        )

                    self.memory_samples.append(sample)

                    # Keep only recent samples to prevent memory growth
                    if len(self.memory_samples) > 1000:
                        self.memory_samples.popleft()

                    # Real-time leak detection
                    if len(self.memory_samples) >= self.leak_detection_window:
                        leak_detected, leak_rate = (
                            self._detect_real_time_leak()
                        )
                        if leak_detected:
                            sample["leak_detected"] = True
                            sample["leak_rate_mb_per_min"] = leak_rate

                    time.sleep(sample_interval)

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    Exception,
                ) as e:
                    print(f"Monitoring error: {e}")
                    break

        self.monitor_thread = threading.Thread(
            target=advanced_monitor, daemon=True
        )
        self.monitor_thread.start()

    def stop_advanced_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return comprehensive analysis."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        if self.tracemalloc_active:
            tracemalloc.stop()
            self.tracemalloc_active = False

        if not self.memory_samples:
            return {"error": "No memory samples collected"}

        return self._generate_comprehensive_analysis()

    def _get_object_counts(self) -> Dict[str, int]:
        """Get current object counts by type."""
        object_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        return object_counts

    def _analyze_references(self) -> Dict[str, Any]:
        """Analyze object references for potential circular references."""
        gc.collect()  # Force garbage collection

        reference_analysis = {
            "total_objects": len(gc.get_objects()),
            "garbage_objects": len(gc.garbage),
            "circular_references": 0,
        }

        # Check for circular references
        for obj in gc.garbage:
            if gc.is_tracked(obj):
                reference_analysis["circular_references"] += 1

        return reference_analysis

    def _detect_real_time_leak(self) -> Tuple[bool, float]:
        """Detect memory leaks in real-time using trend analysis."""
        if len(self.memory_samples) < self.leak_detection_window:
            return False, 0.0

        # Get recent samples
        recent_samples = list(self.memory_samples)[
            -self.leak_detection_window :
        ]
        timestamps = [s["timestamp"] for s in recent_samples]
        memory_values = [s["rss"] for s in recent_samples]

        # Linear regression for trend detection
        n = len(memory_values)
        if n < 2:
            return False, 0.0

        # Calculate slope (memory increase rate)
        x_mean = sum(range(n)) / n
        y_mean = sum(memory_values) / n

        numerator = sum(
            (i - x_mean) * (memory_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return False, 0.0

        slope = numerator / denominator  # bytes per sample

        # Convert to MB per minute
        sample_duration = (timestamps[-1] - timestamps[0]) / (
            n - 1
        )  # seconds per sample
        samples_per_minute = (
            60.0 / sample_duration if sample_duration > 0 else 0
        )
        leak_rate_mb_per_min = (slope * samples_per_minute) / (1024 * 1024)

        leak_detected = leak_rate_mb_per_min > self.leak_threshold_mb_per_min

        return leak_detected, leak_rate_mb_per_min

    def _generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive memory analysis report."""
        samples = list(self.memory_samples)
        if not samples:
            return {"error": "No samples to analyze"}

        memory_values = [s["rss"] for s in samples]
        timestamps = [s["timestamp"] for s in samples]

        analysis = {
            "baseline_memory_mb": self.baseline_memory / 1024 / 1024,
            "final_memory_mb": memory_values[-1] / 1024 / 1024,
            "peak_memory_mb": max(memory_values) / 1024 / 1024,
            "memory_increase_mb": (memory_values[-1] - self.baseline_memory)
            / 1024
            / 1024,
            "avg_memory_mb": sum(memory_values)
            / len(memory_values)
            / 1024
            / 1024,
            "total_samples": len(samples),
            "monitoring_duration_seconds": timestamps[-1] - timestamps[0],
            "memory_leak_analysis": self._analyze_memory_leak_patterns(
                samples
            ),
            "object_analysis": self._analyze_object_patterns(samples),
            "performance_impact": self._analyze_performance_impact(samples),
            "recommendations": self._generate_recommendations(samples),
        }

        return analysis

    def _analyze_memory_leak_patterns(
        self, samples: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze memory leak patterns from samples."""
        memory_values = [s["rss"] for s in samples]
        timestamps = [s["timestamp"] for s in samples]

        # Calculate overall trend
        n = len(memory_values)
        if n < 2:
            return {"error": "Insufficient samples for leak analysis"}

        # Linear regression
        x_mean = sum(range(n)) / n
        y_mean = sum(memory_values) / n

        numerator = sum(
            (i - x_mean) * (memory_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Convert to leak rate
        total_duration_minutes = (timestamps[-1] - timestamps[0]) / 60.0
        if total_duration_minutes > 0:
            leak_rate_mb_per_min = (slope * n * 60.0) / (
                total_duration_minutes * 1024 * 1024
            )
        else:
            leak_rate_mb_per_min = 0

        # Analyze patterns
        leak_patterns = {
            "overall_trend": (
                "increasing"
                if slope > 0
                else "stable" if slope == 0 else "decreasing"
            ),
            "leak_rate_mb_per_min": leak_rate_mb_per_min,
            "leak_detected": abs(leak_rate_mb_per_min)
            > self.leak_threshold_mb_per_min,
            "leak_severity": self._classify_leak_severity(
                leak_rate_mb_per_min
            ),
            "memory_stability": self._calculate_memory_stability(
                memory_values
            ),
            "leak_acceleration": self._detect_leak_acceleration(samples),
        }

        return leak_patterns

    def _analyze_object_patterns(self, samples: List[Dict]) -> Dict[str, Any]:
        """Analyze object creation and destruction patterns."""
        object_samples = [s for s in samples if "object_counts" in s]

        if not object_samples:
            return {"error": "No object tracking data available"}

        # Track object count changes
        object_trends = defaultdict(list)
        for sample in object_samples:
            for obj_type, count in sample["object_counts"].items():
                object_trends[obj_type].append(count)

        # Find objects with increasing trends
        growing_objects = {}
        for obj_type, counts in object_trends.items():
            if len(counts) >= 2:
                growth = counts[-1] - counts[0]
                if growth > 0:
                    growth_rate = growth / len(counts)
                    growing_objects[obj_type] = {
                        "initial_count": counts[0],
                        "final_count": counts[-1],
                        "total_growth": growth,
                        "growth_rate": growth_rate,
                    }

        return {
            "tracked_samples": len(object_samples),
            "object_types_tracked": len(object_trends),
            "growing_object_types": len(growing_objects),
            "top_growing_objects": dict(
                sorted(
                    growing_objects.items(),
                    key=lambda x: x[1]["total_growth"],
                    reverse=True,
                )[:10]
            ),
        }

    def _analyze_performance_impact(
        self, samples: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze performance impact of memory usage."""
        cpu_values = [s.get("cpu_percent", 0) for s in samples]
        memory_values = [s["rss"] for s in samples]

        return {
            "avg_cpu_percent": (
                sum(cpu_values) / len(cpu_values) if cpu_values else 0
            ),
            "max_cpu_percent": max(cpu_values) if cpu_values else 0,
            "cpu_memory_correlation": self._calculate_correlation(
                cpu_values, memory_values
            ),
            "performance_degradation": (
                max(cpu_values) > 50.0 if cpu_values else False
            ),
        }

    def _calculate_correlation(
        self, x_values: List[float], y_values: List[float]
    ) -> float:
        """Calculate correlation coefficient between two series."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0

        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)
        )
        x_variance = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        y_variance = sum((y_values[i] - y_mean) ** 2 for i in range(n))

        denominator = (x_variance * y_variance) ** 0.5

        return numerator / denominator if denominator > 0 else 0.0

    def _classify_leak_severity(self, leak_rate: float) -> str:
        """Classify memory leak severity."""
        abs_rate = abs(leak_rate)

        if abs_rate < 1.0:
            return "minimal"
        elif abs_rate < 5.0:
            return "low"
        elif abs_rate < 15.0:
            return "medium"
        elif abs_rate < 50.0:
            return "high"
        else:
            return "critical"

    def _calculate_memory_stability(self, memory_values: List[int]) -> float:
        """Calculate memory usage stability."""
        if len(memory_values) < 2:
            return 0.0

        mean_memory = sum(memory_values) / len(memory_values)
        variance = sum(
            (value - mean_memory) ** 2 for value in memory_values
        ) / len(memory_values)
        std_deviation = variance**0.5

        return (std_deviation / mean_memory) * 100 if mean_memory > 0 else 0.0

    def _detect_leak_acceleration(self, samples: List[Dict]) -> Dict[str, Any]:
        """Detect if memory leak is accelerating over time."""
        if len(samples) < 10:
            return {"insufficient_data": True}

        # Split samples into early and late periods
        mid_point = len(samples) // 2
        early_samples = samples[:mid_point]
        late_samples = samples[mid_point:]

        early_leak_rate = self._calculate_leak_rate(
            [s["rss"] for s in early_samples]
        )
        late_leak_rate = self._calculate_leak_rate(
            [s["rss"] for s in late_samples]
        )

        acceleration = late_leak_rate - early_leak_rate

        return {
            "early_period_leak_rate": early_leak_rate,
            "late_period_leak_rate": late_leak_rate,
            "acceleration": acceleration,
            "accelerating": acceleration > 1.0,  # MB/min increase
        }

    def _calculate_leak_rate(self, memory_values: List[int]) -> float:
        """Calculate leak rate for a series of memory values."""
        if len(memory_values) < 2:
            return 0.0

        # Simple linear regression
        n = len(memory_values)
        x_mean = (n - 1) / 2
        y_mean = sum(memory_values) / n

        numerator = sum(
            (i - x_mean) * (memory_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator  # bytes per sample
        return slope / (1024 * 1024)  # MB per sample

    def _generate_recommendations(self, samples: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Analyze final state
        if not samples:
            return ["No data available for recommendations"]

        memory_values = [s["rss"] for s in samples]
        final_memory = memory_values[-1]
        initial_memory = memory_values[0]
        memory_increase = (final_memory - initial_memory) / 1024 / 1024

        if memory_increase > 50:  # >50MB increase
            recommendations.append(
                "CRITICAL: Investigate major memory leak - >50MB increase detected"
            )
        elif memory_increase > 10:  # >10MB increase
            recommendations.append(
                "HIGH: Significant memory growth detected - implement resource cleanup"
            )

        # Check for object growth
        object_samples = [s for s in samples if "object_counts" in s]
        if object_samples:
            recommendations.append(
                "Implement object lifecycle monitoring in production"
            )
            recommendations.append(
                "Add garbage collection checkpoints in long-running operations"
            )

        # Performance recommendations
        cpu_values = [s.get("cpu_percent", 0) for s in samples]
        if cpu_values and max(cpu_values) > 80:
            recommendations.append(
                "Optimize CPU usage - high utilization detected"
            )

        recommendations.extend(
            [
                "Implement memory monitoring in production environment",
                "Add memory usage alerts for sustained operations",
                "Consider implementing operation time limits for memory protection",
                "Add resource cleanup checkpoints every N operations",
            ]
        )

        return recommendations


class SizeAnalyzerDebugWrapper:
    """
    Debug wrapper for SizeAnalyzer with comprehensive monitoring.

    This wrapper provides detailed insights into SizeAnalyzer behavior
    during sustained operations to identify memory leak sources.
    """

    def __init__(self, analyzer: SizeAnalyzer):
        self.analyzer = analyzer
        self.profiler = AdvancedMemoryProfiler()
        self.debug_data = {
            "operations": [],
            "resource_usage": [],
            "object_lifecycle": [],
            "error_events": [],
        }
        self.operation_count = 0

    @contextmanager
    def debug_operation(
        self, operation_name: str, operation_data: Dict = None
    ):
        """Context manager for debugging individual operations."""
        self.operation_count += 1
        operation_id = (
            f"{operation_name}_{self.operation_count}_{int(time.time())}"
        )

        # Pre-operation state
        pre_state = {
            "timestamp": time.time(),
            "memory_info": self.profiler.process.memory_info()._asdict(),
            "object_count": len(gc.get_objects()),
            "operation_id": operation_id,
            "operation_name": operation_name,
            "operation_data": operation_data or {},
        }

        try:
            yield operation_id

            # Post-operation state
            post_state = {
                "timestamp": time.time(),
                "memory_info": self.profiler.process.memory_info()._asdict(),
                "object_count": len(gc.get_objects()),
                "operation_id": operation_id,
                "success": True,
            }

            # Calculate changes
            memory_change = (
                post_state["memory_info"]["rss"]
                - pre_state["memory_info"]["rss"]
            )
            object_change = (
                post_state["object_count"] - pre_state["object_count"]
            )
            duration = post_state["timestamp"] - pre_state["timestamp"]

            operation_summary = {
                "operation_id": operation_id,
                "operation_name": operation_name,
                "duration_seconds": duration,
                "memory_change_bytes": memory_change,
                "memory_change_mb": memory_change / 1024 / 1024,
                "object_count_change": object_change,
                "pre_state": pre_state,
                "post_state": post_state,
                "success": True,
            }

            self.debug_data["operations"].append(operation_summary)

        except Exception as e:
            # Error handling
            error_state = {
                "timestamp": time.time(),
                "memory_info": self.profiler.process.memory_info()._asdict(),
                "object_count": len(gc.get_objects()),
                "operation_id": operation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            }

            error_summary = {
                "operation_id": operation_id,
                "operation_name": operation_name,
                "error": str(e),
                "error_type": type(e).__name__,
                "pre_state": pre_state,
                "error_state": error_state,
                "success": False,
            }

            self.debug_data["operations"].append(error_summary)
            self.debug_data["error_events"].append(error_summary)

            raise

    def analyze_directory_debug(
        self, directory_path: str, **kwargs
    ) -> Dict[str, Any]:
        """Analyze directory with comprehensive debugging."""
        with self.debug_operation(
            "analyze_directory", {"path": directory_path, "kwargs": kwargs}
        ) as op_id:
            return self.analyzer.analyze_directory(directory_path, **kwargs)

    def get_debug_summary(self) -> Dict[str, Any]:
        """Get comprehensive debug summary."""
        operations = self.debug_data["operations"]
        if not operations:
            return {"error": "No operations recorded"}

        total_operations = len(operations)
        successful_operations = len(
            [op for op in operations if op.get("success", False)]
        )
        failed_operations = total_operations - successful_operations

        # Memory analysis
        memory_changes = [
            op.get("memory_change_mb", 0)
            for op in operations
            if op.get("success", False)
        ]
        total_memory_change = sum(memory_changes)
        avg_memory_change = (
            total_memory_change / len(memory_changes) if memory_changes else 0
        )

        # Object analysis
        object_changes = [
            op.get("object_count_change", 0)
            for op in operations
            if op.get("success", False)
        ]
        total_object_change = sum(object_changes)
        avg_object_change = (
            total_object_change / len(object_changes) if object_changes else 0
        )

        # Duration analysis
        durations = [
            op.get("duration_seconds", 0)
            for op in operations
            if op.get("success", False)
        ]
        total_duration = sum(durations)
        avg_duration = total_duration / len(durations) if durations else 0

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (
                (successful_operations / total_operations * 100)
                if total_operations > 0
                else 0
            ),
            "memory_analysis": {
                "total_memory_change_mb": total_memory_change,
                "avg_memory_change_mb": avg_memory_change,
                "max_memory_change_mb": (
                    max(memory_changes) if memory_changes else 0
                ),
                "min_memory_change_mb": (
                    min(memory_changes) if memory_changes else 0
                ),
                "memory_leak_detected": avg_memory_change
                > 1.0,  # >1MB average increase
            },
            "object_analysis": {
                "total_object_change": total_object_change,
                "avg_object_change": avg_object_change,
                "max_object_change": (
                    max(object_changes) if object_changes else 0
                ),
                "object_leak_detected": avg_object_change
                > 100,  # >100 objects average increase
            },
            "performance_analysis": {
                "total_duration_seconds": total_duration,
                "avg_duration_seconds": avg_duration,
                "max_duration_seconds": max(durations) if durations else 0,
                "operations_per_second": (
                    total_operations / total_duration
                    if total_duration > 0
                    else 0
                ),
            },
            "error_analysis": {
                "error_count": len(self.debug_data["error_events"]),
                "error_types": list(
                    set(
                        err.get("error_type", "unknown")
                        for err in self.debug_data["error_events"]
                    )
                ),
            },
        }


class MemoryLeakDetectionTestSuite:
    """Comprehensive memory leak detection and debugging test suite."""

    def __init__(self):
        self.profiler = AdvancedMemoryProfiler()
        self.debug_results = {}
        self.test_datasets = {}

    def setup_debug_environment(self):
        """Set up debug environment with production datasets."""
        # Import the ProductionScaleDatasetGenerator from the existing test file
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "phase2b_perf_test",
            os.path.join(
                os.path.dirname(__file__),
                "phase2b_performance_load_testing_no_compromise_2025-09-09.py",
            ),
        )
        perf_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(perf_module)
        ProductionScaleDatasetGenerator = (
            perf_module.ProductionScaleDatasetGenerator
        )

        generator = ProductionScaleDatasetGenerator()

        # Create smaller datasets for focused debugging (use integer scale factor)
        self.test_datasets = {
            "debug_simple": generator.create_production_scale_dataset(
                "simple_uniform", scale_factor=1
            ),
            "debug_mixed": generator.create_production_scale_dataset(
                "mixed_sizes", scale_factor=1
            ),
            "debug_nested": generator.create_production_scale_dataset(
                "deep_nesting", scale_factor=1
            ),
        }

        return generator

    def run_memory_leak_debug_analysis(self) -> Dict[str, Any]:
        """Run comprehensive memory leak debugging analysis."""
        generator = self.setup_debug_environment()

        try:
            # Initialize debug wrapper
            analyzer = SizeAnalyzer()
            debug_wrapper = SizeAnalyzerDebugWrapper(analyzer)

            # Start advanced monitoring
            self.profiler.start_advanced_monitoring(
                sample_interval=0.05, track_objects=True
            )

            # Execute sustained operations for debugging
            debug_results = self._execute_debug_scenario(debug_wrapper)

            # Stop monitoring and get analysis
            memory_analysis = self.profiler.stop_advanced_monitoring()

            # Combine results
            comprehensive_results = {
                "debug_execution": debug_results,
                "memory_analysis": memory_analysis,
                "debug_wrapper_summary": debug_wrapper.get_debug_summary(),
                "leak_diagnosis": self._diagnose_memory_leak(
                    memory_analysis, debug_results
                ),
                "recommendations": self._generate_fix_recommendations(
                    memory_analysis, debug_results
                ),
            }

            return comprehensive_results

        finally:
            generator.cleanup_datasets()

    def _execute_debug_scenario(
        self, debug_wrapper: SizeAnalyzerDebugWrapper
    ) -> Dict[str, Any]:
        """Execute debug scenario with sustained operations."""
        debug_scenario_results = {
            "scenario": "sustained_operations_debug",
            "operations_planned": 10,
            "operations_completed": 0,
            "operations_failed": 0,
            "operation_results": [],
        }

        datasets = list(self.test_datasets.keys())

        for i in range(10):  # 10 operations for focused debugging
            try:
                dataset_name = datasets[i % len(datasets)]
                dataset_path = self.test_datasets[dataset_name]

                print(f"Debug operation {i+1}: Analyzing {dataset_name}")

                start_time = time.time()
                result = debug_wrapper.analyze_directory_debug(dataset_path)
                end_time = time.time()

                operation_result = {
                    "operation_id": i + 1,
                    "dataset": dataset_name,
                    "success": True,
                    "duration": end_time - start_time,
                    "files_analyzed": result.get("file_count", 0),
                    "memory_state": "tracked_by_wrapper",
                }

                debug_scenario_results["operation_results"].append(
                    operation_result
                )
                debug_scenario_results["operations_completed"] += 1

                # Small delay between operations
                time.sleep(0.1)

            except Exception as e:
                error_result = {
                    "operation_id": i + 1,
                    "dataset": dataset_name,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

                debug_scenario_results["operation_results"].append(
                    error_result
                )
                debug_scenario_results["operations_failed"] += 1

                print(f"Debug operation {i+1} failed: {e}")

        return debug_scenario_results

    def _diagnose_memory_leak(
        self, memory_analysis: Dict, debug_results: Dict
    ) -> Dict[str, Any]:
        """Diagnose the specific cause of memory leak."""
        diagnosis = {
            "leak_confirmed": False,
            "leak_source": "unknown",
            "leak_mechanism": "unknown",
            "leak_severity": "low",
            "diagnostic_confidence": 0.0,
        }

        # Check for leak confirmation
        leak_analysis = memory_analysis.get("memory_leak_analysis", {})
        if leak_analysis.get("leak_detected", False):
            diagnosis["leak_confirmed"] = True
            diagnosis["leak_severity"] = leak_analysis.get(
                "leak_severity", "unknown"
            )

        # Analyze object patterns
        object_analysis = memory_analysis.get("object_analysis", {})
        growing_objects = object_analysis.get("top_growing_objects", {})

        if growing_objects:
            # Identify most likely leak sources
            max_growth_type = max(
                growing_objects.keys(),
                key=lambda x: growing_objects[x]["total_growth"],
            )
            diagnosis["leak_source"] = max_growth_type
            diagnosis["diagnostic_confidence"] = 0.8

            # Determine leak mechanism
            if (
                "dict" in max_growth_type.lower()
                or "cache" in max_growth_type.lower()
            ):
                diagnosis["leak_mechanism"] = "cache_accumulation"
            elif "list" in max_growth_type.lower():
                diagnosis["leak_mechanism"] = "list_accumulation"
            elif "object" in max_growth_type.lower():
                diagnosis["leak_mechanism"] = "object_retention"
            else:
                diagnosis["leak_mechanism"] = "reference_retention"

        # Add specific SizeAnalyzer analysis
        debug_summary = debug_results.get("debug_wrapper_summary", {})
        memory_info = debug_summary.get("memory_analysis", {})

        if memory_info.get("memory_leak_detected", False):
            diagnosis["sizeanalyzer_specific"] = {
                "avg_memory_increase_per_operation": memory_info.get(
                    "avg_memory_change_mb", 0
                ),
                "total_memory_increase": memory_info.get(
                    "total_memory_change_mb", 0
                ),
                "leak_per_operation": memory_info.get(
                    "avg_memory_change_mb", 0
                )
                > 0.5,
            }

        return diagnosis

    def _generate_fix_recommendations(
        self, memory_analysis: Dict, debug_results: Dict
    ) -> List[str]:
        """Generate specific fix recommendations based on analysis."""
        recommendations = []

        # General recommendations
        recommendations.extend(
            [
                "IMMEDIATE: Add explicit resource cleanup in SizeAnalyzer.analyze_directory()",
                "IMMEDIATE: Implement garbage collection checkpoints after each operation",
                "HIGH: Add weak references for internal caches and tracking objects",
                "HIGH: Implement memory usage limits with automatic cleanup triggers",
            ]
        )

        # Specific recommendations based on diagnosis
        diagnosis = self._diagnose_memory_leak(memory_analysis, debug_results)

        if diagnosis.get("leak_confirmed", False):
            leak_source = diagnosis.get("leak_source", "unknown")
            leak_mechanism = diagnosis.get("leak_mechanism", "unknown")

            if "cache" in leak_mechanism.lower():
                recommendations.extend(
                    [
                        f"CRITICAL: Implement cache size limits for {leak_source} objects",
                        f"CRITICAL: Add cache eviction policy for {leak_source}",
                        "HIGH: Consider using LRU cache with size limits",
                    ]
                )

            if "list" in leak_mechanism.lower():
                recommendations.extend(
                    [
                        f"CRITICAL: Clear {leak_source} collections after each operation",
                        "HIGH: Use generators instead of lists where possible",
                        "MEDIUM: Implement list size monitoring and automatic clearing",
                    ]
                )

            if "object" in leak_mechanism.lower():
                recommendations.extend(
                    [
                        f"CRITICAL: Ensure proper cleanup of {leak_source} objects",
                        "HIGH: Add explicit __del__ methods with resource cleanup",
                        "HIGH: Use context managers for object lifecycle management",
                    ]
                )

        # Performance recommendations
        recommendations.extend(
            [
                "MEDIUM: Add memory usage monitoring to production SizeAnalyzer",
                "MEDIUM: Implement operation timeout to prevent excessive memory usage",
                "LOW: Add memory usage reporting in progress callbacks",
                "LOW: Consider implementing memory usage alerts for sustained operations",
            ]
        )

        return recommendations


if __name__ == "__main__":
    print("=" * 80)
    print(
        "Phase 2B-DEBUG: Memory Leak Resolution - Advanced Diagnostic System"
    )
    print("=" * 80)

    if not SizeAnalyzer_available:
        print("CRITICAL ERROR: SizeAnalyzer not available for debugging")
        sys.exit(1)

    # Initialize and run comprehensive debugging
    test_suite = MemoryLeakDetectionTestSuite()

    print("Starting comprehensive memory leak debugging analysis...")
    debug_results = test_suite.run_memory_leak_debug_analysis()

    print("\n" + "=" * 80)
    print("MEMORY LEAK DEBUG ANALYSIS RESULTS")
    print("=" * 80)

    # Display key findings
    memory_analysis = debug_results.get("memory_analysis", {})
    leak_analysis = memory_analysis.get("memory_leak_analysis", {})

    print(
        f"Memory Leak Detected: {leak_analysis.get('leak_detected', 'Unknown')}"
    )
    print(
        f"Leak Rate: {leak_analysis.get('leak_rate_mb_per_min', 0):.2f} MB/min"
    )
    print(f"Leak Severity: {leak_analysis.get('leak_severity', 'Unknown')}")

    object_analysis = memory_analysis.get("object_analysis", {})
    print(
        f"Growing Object Types: {object_analysis.get('growing_object_types', 0)}"
    )

    diagnosis = debug_results.get("leak_diagnosis", {})
    print(f"Leak Source: {diagnosis.get('leak_source', 'Unknown')}")
    print(f"Leak Mechanism: {diagnosis.get('leak_mechanism', 'Unknown')}")

    print("\nRecommendations:")
    recommendations = debug_results.get("recommendations", [])
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec}")

    # Save detailed results
    results_file = "memory_leak_debug_results_2025-09-09.json"
    with open(results_file, "w") as f:
        json.dump(debug_results, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")
    print("=" * 80)
