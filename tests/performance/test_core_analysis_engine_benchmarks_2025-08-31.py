#!/usr/bin/env python3
"""
Core Analysis Engine Performance Benchmark Suite

This test suite provides comprehensive performance benchmarking for the Core Analysis Engine
components, measuring throughput, latency, memory usage, and scalability characteristics.

Created: August 31, 2025
Coverage: Core Analysis Engine - Performance benchmarks and scalability testing
Priority: HIGH (addressing missing performance benchmarks in core engine)
"""

import json
import os
import shutil
import statistics
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False

# Skip all tests if imports fail
pytestmark = pytest.mark.skipif(
    not IMPORTS_SUCCESSFUL, reason="Required modules not available"
)


@dataclass
class PerformanceMetrics:
    """Data class for storing performance metrics."""

    operation: str
    duration: float
    files_processed: int
    total_size: int
    files_per_second: float
    bytes_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "operation": self.operation,
            "duration": self.duration,
            "files_processed": self.files_processed,
            "total_size": self.total_size,
            "files_per_second": self.files_per_second,
            "bytes_per_second": self.bytes_per_second,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
        }


class PerformanceBenchmarkRunner:
    """Performance benchmark runner for analysis engine."""

    def __init__(self):
        """Initialize the benchmark runner."""
        self.results: List[PerformanceMetrics] = []
        self.baseline_metrics: Dict[str, float] = {
            "min_files_per_second": 50,  # Minimum expected files/sec
            "min_bytes_per_second": 1024 * 1024,  # Minimum 1MB/sec
            "max_memory_usage_mb": 500,  # Maximum 500MB
            "max_analysis_time_small": 5,  # Max 5 seconds for small datasets
            "max_analysis_time_medium": 30,  # Max 30 seconds for medium datasets
            "max_analysis_time_large": 120,  # Max 2 minutes for large datasets
        }

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil

            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def run_benchmark(
        self, test_name: str, analyzer: SizeAnalyzer, directory: str
    ) -> PerformanceMetrics:
        """Run a single benchmark test."""
        initial_memory = self.get_memory_usage()

        start_time = time.time()
        result = analyzer.analyze_directory(directory)
        end_time = time.time()

        final_memory = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()

        duration = end_time - start_time
        files_processed = result["file_count"]
        total_size = result["total_size"]

        files_per_second = files_processed / duration if duration > 0 else 0
        bytes_per_second = total_size / duration if duration > 0 else 0
        memory_usage = max(final_memory - initial_memory, 0)

        metrics = PerformanceMetrics(
            operation=test_name,
            duration=duration,
            files_processed=files_processed,
            total_size=total_size,
            files_per_second=files_per_second,
            bytes_per_second=bytes_per_second,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
        )

        self.results.append(metrics)
        return metrics

    def generate_report(self) -> str:
        """Generate performance benchmark report."""
        if not self.results:
            return "No benchmark results available."

        report = ["CORE ANALYSIS ENGINE PERFORMANCE BENCHMARK REPORT"]
        report.append("=" * 60)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.results)}")
        report.append("")

        # Summary statistics
        durations = [r.duration for r in self.results]
        files_per_sec = [
            r.files_per_second for r in self.results if r.files_per_second > 0
        ]
        memory_usage = [r.memory_usage_mb for r in self.results]

        report.append("SUMMARY STATISTICS")
        report.append("-" * 30)
        report.append(f"Average Duration: {statistics.mean(durations):.2f}s")
        report.append(f"Median Duration: {statistics.median(durations):.2f}s")
        if files_per_sec:
            report.append(
                f"Average Throughput: {statistics.mean(files_per_sec):.1f} files/sec"
            )
        report.append(f"Average Memory Usage: {statistics.mean(memory_usage):.1f} MB")
        report.append("")

        # Individual test results
        report.append("DETAILED RESULTS")
        report.append("-" * 30)
        for result in self.results:
            report.append(f"Test: {result.operation}")
            report.append(f"  Duration: {result.duration:.2f}s")
            report.append(f"  Files: {result.files_processed}")
            report.append(f"  Size: {result.total_size:,} bytes")
            report.append(f"  Throughput: {result.files_per_second:.1f} files/sec")
            report.append(
                f"  Bandwidth: {result.bytes_per_second/1024/1024:.1f} MB/sec"
            )
            report.append(f"  Memory: {result.memory_usage_mb:.1f} MB")
            report.append("")

        # Performance analysis
        report.append("PERFORMANCE ANALYSIS")
        report.append("-" * 30)

        # Check against baselines
        for result in self.results:
            if result.files_per_second < self.baseline_metrics["min_files_per_second"]:
                report.append(f"⚠️  {result.operation}: Low file processing rate")

            if result.bytes_per_second < self.baseline_metrics["min_bytes_per_second"]:
                report.append(f"⚠️  {result.operation}: Low byte processing rate")

            if result.memory_usage_mb > self.baseline_metrics["max_memory_usage_mb"]:
                report.append(f"⚠️  {result.operation}: High memory usage")

        if not any("⚠️" in line for line in report[-10:]):
            report.append("✅ All benchmarks passed baseline requirements")

        return "\n".join(report)


class TestCoreAnalysisEnginePerformance:
    """Performance benchmark tests for core analysis engine."""

    @pytest.fixture
    def benchmark_runner(self):
        """Create benchmark runner instance."""
        return PerformanceBenchmarkRunner()

    @pytest.fixture
    def small_dataset(self):
        """Create small dataset for performance testing."""
        temp_dir = tempfile.mkdtemp(prefix="perf_small_")

        # Create 50 small files
        for i in range(50):
            test_file = os.path.join(temp_dir, f"small_file_{i:03d}.txt")
            with open(test_file, "w") as f:
                f.write(f"Small file content {i}\n" * 10)  # ~200 bytes each

        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def medium_dataset(self):
        """Create medium dataset for performance testing."""
        temp_dir = tempfile.mkdtemp(prefix="perf_medium_")

        # Create 500 medium files in subdirectories
        for i in range(500):
            subdir = os.path.join(temp_dir, f"subdir_{i // 50}")
            os.makedirs(subdir, exist_ok=True)

            test_file = os.path.join(subdir, f"medium_file_{i:04d}.txt")
            with open(test_file, "w") as f:
                f.write(f"Medium file content {i}\n" * 100)  # ~2KB each

        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def large_dataset(self):
        """Create large dataset for performance testing."""
        temp_dir = tempfile.mkdtemp(prefix="perf_large_")

        # Create 2000 files with varying sizes
        for i in range(2000):
            subdir = os.path.join(temp_dir, f"dir_{i // 200}")
            os.makedirs(subdir, exist_ok=True)

            test_file = os.path.join(subdir, f"large_file_{i:05d}.dat")
            file_size = 1024 + (i % 10) * 512  # 1KB to 6KB files
            with open(test_file, "w") as f:
                f.write("x" * file_size)

        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_small_dataset_performance(self, qapp, benchmark_runner, small_dataset):
        """Test performance with small dataset."""
        analyzer = SizeAnalyzer()

        metrics = benchmark_runner.run_benchmark(
            "Small Dataset Analysis", analyzer, small_dataset
        )

        # Verify performance requirements
        assert (
            metrics.duration
            < benchmark_runner.baseline_metrics["max_analysis_time_small"]
        )
        assert (
            metrics.files_per_second
            >= benchmark_runner.baseline_metrics["min_files_per_second"]
        )
        assert (
            metrics.memory_usage_mb
            <= benchmark_runner.baseline_metrics["max_memory_usage_mb"]
        )
        assert metrics.files_processed == 50

    def test_medium_dataset_performance(self, qapp, benchmark_runner, medium_dataset):
        """Test performance with medium dataset."""
        analyzer = SizeAnalyzer()

        metrics = benchmark_runner.run_benchmark(
            "Medium Dataset Analysis", analyzer, medium_dataset
        )

        # Verify performance requirements
        assert (
            metrics.duration
            < benchmark_runner.baseline_metrics["max_analysis_time_medium"]
        )
        assert metrics.files_per_second >= 20  # Lower threshold for larger datasets
        assert (
            metrics.memory_usage_mb
            <= benchmark_runner.baseline_metrics["max_memory_usage_mb"]
        )
        assert metrics.files_processed == 500

    def test_large_dataset_performance(self, qapp, benchmark_runner, large_dataset):
        """Test performance with large dataset."""
        analyzer = SizeAnalyzer()

        metrics = benchmark_runner.run_benchmark(
            "Large Dataset Analysis", analyzer, large_dataset
        )

        # Verify performance requirements
        assert (
            metrics.duration
            < benchmark_runner.baseline_metrics["max_analysis_time_large"]
        )
        assert metrics.files_per_second >= 10  # Lower threshold for very large datasets
        assert (
            metrics.memory_usage_mb
            <= benchmark_runner.baseline_metrics["max_memory_usage_mb"]
        )
        assert metrics.files_processed == 2000

    def test_memory_efficiency_benchmark(self, qapp, benchmark_runner):
        """Test memory efficiency across different dataset sizes."""
        datasets = []

        # Create multiple datasets of different sizes
        for size, count in [(100, "tiny"), (500, "small"), (1000, "medium")]:
            temp_dir = tempfile.mkdtemp(prefix=f"mem_test_{count}_")

            for i in range(size):
                test_file = os.path.join(temp_dir, f"mem_file_{i:04d}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Memory test content {i}\n" * 20)

            datasets.append((temp_dir, count, size))

        try:
            analyzer = SizeAnalyzer()
            memory_metrics = []

            for temp_dir, label, expected_count in datasets:
                metrics = benchmark_runner.run_benchmark(
                    f"Memory Test - {label.title()}", analyzer, temp_dir
                )
                memory_metrics.append(metrics)

                # Memory usage should scale reasonably
                memory_per_file = (
                    metrics.memory_usage_mb / expected_count
                    if expected_count > 0
                    else 0
                )
                assert memory_per_file < 1.0  # Less than 1MB per file

            # Memory usage should be somewhat proportional to dataset size
            if len(memory_metrics) >= 2:
                small_memory = memory_metrics[0].memory_usage_mb
                large_memory = memory_metrics[-1].memory_usage_mb

                # Larger dataset shouldn't use exponentially more memory
                memory_ratio = large_memory / small_memory if small_memory > 0 else 1
                assert memory_ratio < 20  # Should not be more than 20x increase

        finally:
            for temp_dir, _, _ in datasets:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_scalability_benchmark(self, qapp, benchmark_runner):
        """Test scalability characteristics of the analysis engine."""
        test_sizes = [50, 100, 200, 400]
        scalability_results = []

        for size in test_sizes:
            temp_dir = tempfile.mkdtemp(prefix=f"scale_test_{size}_")

            try:
                # Create dataset of specified size
                for i in range(size):
                    test_file = os.path.join(temp_dir, f"scale_file_{i:04d}.txt")
                    with open(test_file, "w") as f:
                        f.write(f"Scalability test content {i}\n" * 10)

                analyzer = SizeAnalyzer()
                metrics = benchmark_runner.run_benchmark(
                    f"Scalability Test - {size} files", analyzer, temp_dir
                )

                scalability_results.append((size, metrics))

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        # Analyze scalability
        assert len(scalability_results) >= 2

        # Check that performance scales reasonably
        for i in range(1, len(scalability_results)):
            prev_size, prev_metrics = scalability_results[i - 1]
            curr_size, curr_metrics = scalability_results[i]

            size_ratio = curr_size / prev_size
            time_ratio = curr_metrics.duration / prev_metrics.duration

            # Time should scale sub-quadratically (ideally linearly)
            assert time_ratio <= size_ratio * 2  # Allow 2x overhead for scaling

    def test_concurrent_performance_benchmark(self, qapp, benchmark_runner):
        """Test performance under concurrent load."""
        # Create test datasets
        datasets = []
        for i in range(4):
            temp_dir = tempfile.mkdtemp(prefix=f"concurrent_test_{i}_")

            for j in range(100):
                test_file = os.path.join(temp_dir, f"concurrent_file_{j:03d}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Concurrent test content {i}-{j}\n" * 15)

            datasets.append(temp_dir)

        try:
            # Test sequential performance
            sequential_start = time.time()
            sequential_results = []

            for i, temp_dir in enumerate(datasets):
                analyzer = SizeAnalyzer()
                metrics = benchmark_runner.run_benchmark(
                    f"Sequential Test {i}", analyzer, temp_dir
                )
                sequential_results.append(metrics)

            sequential_time = time.time() - sequential_start

            # Test concurrent performance
            concurrent_start = time.time()
            concurrent_results = []

            def run_concurrent_analysis(dataset_id, temp_dir):
                analyzer = SizeAnalyzer()
                return benchmark_runner.run_benchmark(
                    f"Concurrent Test {dataset_id}", analyzer, temp_dir
                )

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(run_concurrent_analysis, i, temp_dir)
                    for i, temp_dir in enumerate(datasets)
                ]

                for future in as_completed(futures):
                    concurrent_results.append(future.result())

            concurrent_time = time.time() - concurrent_start

            # Verify concurrent performance
            assert len(concurrent_results) == len(datasets)

            # Concurrent execution should not be significantly slower
            # (allowing for overhead)
            max_sequential_time = max(r.duration for r in sequential_results)
            assert concurrent_time <= max_sequential_time * 2

        finally:
            for temp_dir in datasets:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_throughput_benchmark_analysis(self, qapp, benchmark_runner):
        """Test detailed throughput analysis across different file types."""
        temp_dir = tempfile.mkdtemp(prefix="throughput_test_")

        try:
            # Create files of different types and sizes
            file_types = [
                (".txt", 1024, 100),  # 100 x 1KB text files
                (".dat", 10240, 50),  # 50 x 10KB data files
                (".log", 512, 200),  # 200 x 512B log files
                (".json", 2048, 75),  # 75 x 2KB JSON files
            ]

            total_files = 0
            total_size = 0

            for ext, size, count in file_types:
                for i in range(count):
                    filename = f"throughput_test_{total_files:04d}{ext}"
                    test_file = os.path.join(temp_dir, filename)

                    with open(test_file, "w") as f:
                        f.write("x" * size)

                    total_files += 1
                    total_size += size

            analyzer = SizeAnalyzer()
            metrics = benchmark_runner.run_benchmark(
                "Throughput Analysis", analyzer, temp_dir
            )

            # Verify throughput metrics
            assert metrics.files_processed == total_files
            assert metrics.total_size >= total_size * 0.9  # Allow for slight variations

            # Calculate expected minimums
            min_expected_throughput = 30  # files per second
            min_expected_bandwidth = 1024 * 1024  # 1 MB/s

            assert metrics.files_per_second >= min_expected_throughput
            assert metrics.bytes_per_second >= min_expected_bandwidth

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestCoreAnalysisEngineRegressionBenchmarks:
    """Regression benchmark tests to detect performance degradation."""

    def test_performance_regression_detection(self, qapp):
        """Test for performance regressions compared to baseline."""
        temp_dir = tempfile.mkdtemp(prefix="regression_test_")

        try:
            # Create standardized test dataset
            standard_file_count = 300
            for i in range(standard_file_count):
                test_file = os.path.join(temp_dir, f"regression_file_{i:04d}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Regression test content {i}\n" * 25)  # ~500B each

            analyzer = SizeAnalyzer()

            # Run multiple iterations to get stable measurements
            durations = []
            throughputs = []

            for iteration in range(3):
                start_time = time.time()
                result = analyzer.analyze_directory(temp_dir)
                duration = time.time() - start_time

                durations.append(duration)
                if duration > 0:
                    throughputs.append(result["file_count"] / duration)

            # Calculate statistics
            avg_duration = statistics.mean(durations)
            avg_throughput = statistics.mean(throughputs) if throughputs else 0

            # Performance regression thresholds
            max_acceptable_duration = 15.0  # seconds
            min_acceptable_throughput = 20.0  # files per second

            # Check for regressions
            assert (
                avg_duration <= max_acceptable_duration
            ), f"Performance regression: {avg_duration:.2f}s > {max_acceptable_duration}s"

            assert (
                avg_throughput >= min_acceptable_throughput
            ), f"Throughput regression: {avg_throughput:.1f} < {min_acceptable_throughput} files/sec"

            # Log performance data for tracking
            performance_data = {
                "timestamp": time.time(),
                "avg_duration": avg_duration,
                "avg_throughput": avg_throughput,
                "file_count": standard_file_count,
                "test_type": "regression_baseline",
            }

            # Save performance data for regression tracking
            perf_log_file = os.path.join(temp_dir, "performance_log.json")
            with open(perf_log_file, "w") as f:
                json.dump(performance_data, f, indent=2)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# Test runner configuration
def run_performance_benchmarks():
    """Run the comprehensive performance benchmark suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=20",
        "-s",  # Don't capture output for performance monitoring
        "--benchmark-sort=name",  # Sort by test name
    ]

    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing
    try:
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass

    # Run the benchmarks
    print("Starting Core Analysis Engine Performance Benchmarks...")
    exit_code = run_performance_benchmarks()

    print(f"\nPerformance Benchmark Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)
