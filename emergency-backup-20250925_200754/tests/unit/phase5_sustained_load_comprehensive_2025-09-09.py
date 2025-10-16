"""
Phase 5: Comprehensive Sustained Load Testing - Post Root Cause Analysis
Generated: September 9, 2025

This test validates the SizeAnalyzer memory performance profile against the established
threshold of <10 MB/min during sustained operations. Based on validation results showing
0.098 MB growth in first operation then stable performance, this test will determine
if the current implementation meets production requirements.

**VALIDATION CRITERIA:**
- Memory growth < 10 MB/min during sustained operations
- Successful completion of 50+ sustained operations
- Memory leak rate quantification with statistical analysis
- Performance degradation assessment under load
"""

import gc
import json
import os
import sys
import tempfile
import time
import tracemalloc
from datetime import datetime
from typing import Any, Dict, List

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import SizeAnalyzer
try:
    from tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import SizeAnalyzer: {e}")
    ANALYZER_AVAILABLE = False


class Phase5SustainedLoadTestingSuite:
    """Comprehensive sustained load testing suite for Phase 5."""

    def __init__(self):
        self.test_results = {}
        self.test_datasets = {}
        self.memory_samples = []

    def create_production_scale_dataset(self, size: str = "large") -> str:
        """Create production-scale test dataset."""
        test_dir = tempfile.mkdtemp(prefix="phase5_sustained_test_")

        if size == "small":
            file_count = 200
            subdir_count = 5
        elif size == "medium":
            file_count = 500
            subdir_count = 10
        else:  # large - production scale
            file_count = 1000
            subdir_count = 20

        print(
            f"Creating {size} dataset: {file_count} files in {subdir_count} subdirectories..."
        )

        # Create main directory files
        for i in range(file_count):
            file_path = os.path.join(test_dir, f"prod_file_{i:05d}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                # Realistic file content with varying sizes
                content_size = 1000 + (i % 5000)  # 1KB to 6KB files
                f.write(f"Production file {i} - timestamp: {datetime.now()}\n")
                f.write("x" * content_size)

        # Create subdirectories with files
        for i in range(subdir_count):
            subdir = os.path.join(test_dir, f"department_{i:03d}")
            os.makedirs(subdir, exist_ok=True)

            # Files per subdirectory
            for j in range(50):
                file_path = os.path.join(subdir, f"dept_file_{j:03d}.data")
                with open(file_path, "w", encoding="utf-8") as f:
                    content_size = 500 + (j % 2000)  # 0.5KB to 2.5KB files
                    f.write(f"Department {i} file {j}\n")
                    f.write("y" * content_size)

            # Create nested subdirectories
            nested_dir = os.path.join(subdir, "archived")
            os.makedirs(nested_dir, exist_ok=True)
            for k in range(10):
                file_path = os.path.join(nested_dir, f"archive_{k:02d}.old")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Archived file {k}\n" + "z" * 200)

        self.test_datasets[size] = test_dir
        total_files = file_count + (
            subdir_count * 60
        )  # Main + subdirs + nested
        print(f"Created dataset with {total_files} total files at: {test_dir}")

        return test_dir

    def run_sustained_load_test(
        self, operations_count: int = 50, dataset_size: str = "large"
    ) -> Dict[str, Any]:
        """Run sustained load testing with comprehensive monitoring."""
        print(f"=" * 80)
        print(f"PHASE 5: SUSTAINED LOAD TESTING")
        print(f"Operations: {operations_count}")
        print(f"Dataset Size: {dataset_size}")
        print(f"=" * 80)

        if not ANALYZER_AVAILABLE:
            return {"error": "SizeAnalyzer not available"}

        # Create test dataset
        test_dir = self.create_production_scale_dataset(dataset_size)

        try:
            analyzer = SizeAnalyzer()

            # Start memory tracking
            tracemalloc.start()
            baseline_memory = tracemalloc.get_traced_memory()[0]
            baseline_time = time.time()

            operation_results = []
            memory_samples = []
            performance_metrics = []

            print(f"\nStarting sustained operations...")

            for i in range(operations_count):
                operation_start = time.time()
                pre_memory = tracemalloc.get_traced_memory()[0]
                pre_objects = len(gc.get_objects())

                print(
                    f"Operation {i+1:2d}/{operations_count}: ",
                    end="",
                    flush=True,
                )

                try:
                    # Execute analysis
                    start_time = time.time()
                    result = analyzer.analyze_directory(test_dir)
                    end_time = time.time()

                    success = True
                    error = None
                    files_analyzed = (
                        result.get("file_count", 0) if result else 0
                    )
                    analysis_duration = end_time - start_time

                except Exception as e:
                    success = False
                    error = str(e)
                    files_analyzed = 0
                    analysis_duration = 0
                    print(f"ERROR - {error}")

                # Memory measurements
                post_memory = tracemalloc.get_traced_memory()[0]
                post_objects = len(gc.get_objects())

                # Force garbage collection
                gc.collect()
                post_gc_memory = tracemalloc.get_traced_memory()[0]
                post_gc_objects = len(gc.get_objects())

                operation_end = time.time()
                total_operation_time = operation_end - operation_start

                # Calculate metrics
                memory_change = (post_gc_memory - pre_memory) / 1024 / 1024
                object_change = post_gc_objects - pre_objects

                operation_result = {
                    "operation_id": i + 1,
                    "success": success,
                    "error": error,
                    "files_analyzed": files_analyzed,
                    "analysis_duration_sec": analysis_duration,
                    "total_operation_duration_sec": total_operation_time,
                    "memory_before_mb": pre_memory / 1024 / 1024,
                    "memory_after_gc_mb": post_gc_memory / 1024 / 1024,
                    "memory_change_mb": memory_change,
                    "objects_before": pre_objects,
                    "objects_after_gc": post_gc_objects,
                    "object_change": object_change,
                    "timestamp": datetime.now().isoformat(),
                }

                operation_results.append(operation_result)
                memory_samples.append(post_gc_memory)

                # Performance metrics
                if success:
                    files_per_sec = (
                        files_analyzed / analysis_duration
                        if analysis_duration > 0
                        else 0
                    )
                    performance_metrics.append(
                        {
                            "operation_id": i + 1,
                            "files_per_second": files_per_sec,
                            "mb_per_second": (
                                (result.get("total_size", 0) / 1024 / 1024)
                                / analysis_duration
                                if analysis_duration > 0
                                else 0
                            ),
                        }
                    )

                # Progress display
                if success:
                    print(
                        f"✓ {files_analyzed} files, {memory_change:+.3f} MB, {analysis_duration:.2f}s"
                    )
                else:
                    print(f"✗ Failed")

                # Brief pause between operations for realistic simulation
                time.sleep(0.1)

            # Final measurements
            final_memory = tracemalloc.get_traced_memory()[0]
            final_time = time.time()

            tracemalloc.stop()

            # Calculate comprehensive statistics
            successful_ops = [op for op in operation_results if op["success"]]
            total_duration_minutes = (final_time - baseline_time) / 60
            total_memory_change_mb = (
                (final_memory - baseline_memory) / 1024 / 1024
            )

            if successful_ops:
                avg_memory_change = sum(
                    op["memory_change_mb"] for op in successful_ops
                ) / len(successful_ops)
                max_memory_change = max(
                    op["memory_change_mb"] for op in successful_ops
                )
                min_memory_change = min(
                    op["memory_change_mb"] for op in successful_ops
                )
                avg_analysis_time = sum(
                    op["analysis_duration_sec"] for op in successful_ops
                ) / len(successful_ops)
            else:
                avg_memory_change = max_memory_change = min_memory_change = (
                    avg_analysis_time
                ) = 0

            # Memory leak rate calculation
            memory_leak_rate_mb_per_min = (
                total_memory_change_mb / total_duration_minutes
                if total_duration_minutes > 0
                else 0
            )

            return {
                "test_configuration": {
                    "operations_count": operations_count,
                    "dataset_size": dataset_size,
                    "test_dataset_path": test_dir,
                    "total_duration_minutes": total_duration_minutes,
                },
                "memory_analysis": {
                    "baseline_memory_mb": baseline_memory / 1024 / 1024,
                    "final_memory_mb": final_memory / 1024 / 1024,
                    "total_memory_change_mb": total_memory_change_mb,
                    "memory_leak_rate_mb_per_min": memory_leak_rate_mb_per_min,
                    "avg_memory_change_per_op_mb": avg_memory_change,
                    "max_memory_change_per_op_mb": max_memory_change,
                    "min_memory_change_per_op_mb": min_memory_change,
                },
                "performance_analysis": {
                    "total_operations": operations_count,
                    "successful_operations": len(successful_ops),
                    "success_rate_percent": (
                        len(successful_ops) / operations_count
                    )
                    * 100,
                    "avg_analysis_duration_sec": avg_analysis_time,
                    "performance_metrics": performance_metrics,
                },
                "threshold_compliance": {
                    "memory_leak_threshold_mb_per_min": 10.0,
                    "actual_leak_rate_mb_per_min": memory_leak_rate_mb_per_min,
                    "threshold_met": memory_leak_rate_mb_per_min < 10.0,
                    "safety_margin_percent": (
                        ((10.0 - memory_leak_rate_mb_per_min) / 10.0) * 100
                        if memory_leak_rate_mb_per_min < 10.0
                        else None
                    ),
                },
                "detailed_operations": operation_results,
            }

        finally:
            # Cleanup test dataset
            import shutil

            shutil.rmtree(test_dir, ignore_errors=True)

    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive Phase 5 test report."""
        if "error" in results:
            return f"PHASE 5 TEST FAILED: {results['error']}"

        lines = [
            "=" * 100,
            "PHASE 5: SUSTAINED LOAD TESTING - COMPREHENSIVE RESULTS",
            "=" * 100,
            "",
            "TEST CONFIGURATION:",
            f"- Operations Executed: {results['test_configuration']['operations_count']}",
            f"- Dataset Size: {results['test_configuration']['dataset_size']}",
            f"- Total Test Duration: {results['test_configuration']['total_duration_minutes']:.2f} minutes",
            "",
            "MEMORY ANALYSIS RESULTS:",
        ]

        memory = results["memory_analysis"]
        lines.extend(
            [
                f"- Baseline Memory: {memory['baseline_memory_mb']:.3f} MB",
                f"- Final Memory: {memory['final_memory_mb']:.3f} MB",
                f"- Total Memory Change: {memory['total_memory_change_mb']:.3f} MB",
                f"- Memory Leak Rate: {memory['memory_leak_rate_mb_per_min']:.6f} MB/min",
                f"- Average Memory Change per Operation: {memory['avg_memory_change_per_op_mb']:.6f} MB",
                f"- Maximum Memory Change per Operation: {memory['max_memory_change_per_op_mb']:.6f} MB",
                f"- Minimum Memory Change per Operation: {memory['min_memory_change_per_op_mb']:.6f} MB",
                "",
            ]
        )

        performance = results["performance_analysis"]
        lines.extend(
            [
                "PERFORMANCE ANALYSIS:",
                f"- Success Rate: {performance['success_rate_percent']:.1f}% ({performance['successful_operations']}/{performance['total_operations']})",
                f"- Average Analysis Duration: {performance['avg_analysis_duration_sec']:.3f} seconds",
                "",
            ]
        )

        threshold = results["threshold_compliance"]
        lines.extend(
            [
                "THRESHOLD COMPLIANCE ANALYSIS:",
                f"- Required Threshold: < {threshold['memory_leak_threshold_mb_per_min']:.1f} MB/min",
                f"- Actual Leak Rate: {threshold['actual_leak_rate_mb_per_min']:.6f} MB/min",
                f"- Threshold Compliance: {'✓ PASSED' if threshold['threshold_met'] else '✗ FAILED'}",
            ]
        )

        if (
            threshold["threshold_met"]
            and threshold["safety_margin_percent"] is not None
        ):
            lines.append(
                f"- Safety Margin: {threshold['safety_margin_percent']:.1f}%"
            )

        lines.extend(
            [
                "",
                "DETAILED ANALYSIS:",
            ]
        )

        # Operation breakdown
        ops = results["detailed_operations"]
        successful_ops = [op for op in ops if op["success"]]

        if successful_ops:
            # Memory growth pattern analysis
            first_5_ops = successful_ops[:5]
            last_5_ops = successful_ops[-5:]

            avg_first_5 = sum(
                op["memory_change_mb"] for op in first_5_ops
            ) / len(first_5_ops)
            avg_last_5 = sum(
                op["memory_change_mb"] for op in last_5_ops
            ) / len(last_5_ops)

            lines.extend(
                [
                    f"- First 5 Operations Average Memory Change: {avg_first_5:.6f} MB",
                    f"- Last 5 Operations Average Memory Change: {avg_last_5:.6f} MB",
                    f"- Memory Growth Trend: {'Increasing' if avg_last_5 > avg_first_5 else 'Stable/Decreasing'}",
                ]
            )

        lines.extend(
            [
                "",
                "PRODUCTION READINESS ASSESSMENT:",
            ]
        )

        # Overall assessment
        if threshold["threshold_met"]:
            if memory["memory_leak_rate_mb_per_min"] < 1.0:
                assessment = "EXCELLENT - Production Ready"
                recommendation = (
                    "Safe for production deployment with sustained operations"
                )
            elif memory["memory_leak_rate_mb_per_min"] < 5.0:
                assessment = "GOOD - Production Ready with Monitoring"
                recommendation = (
                    "Suitable for production with memory monitoring"
                )
            else:
                assessment = "ACCEPTABLE - Production Ready with Limits"
                recommendation = (
                    "Production ready but monitor for extended operations"
                )
        else:
            assessment = "REQUIRES OPTIMIZATION"
            recommendation = (
                "Additional memory optimization required before production"
            )

        lines.extend(
            [
                f"- Overall Assessment: {assessment}",
                f"- Recommendation: {recommendation}",
                "",
                "=" * 100,
                "END OF PHASE 5 SUSTAINED LOAD TESTING REPORT",
                "=" * 100,
            ]
        )

        return "\n".join(lines)


def main():
    """Execute Phase 5 sustained load testing."""
    print("Phase 5: Sustained Load Testing - Post Root Cause Analysis")
    print("=" * 70)

    if not ANALYZER_AVAILABLE:
        print("❌ CRITICAL ERROR: SizeAnalyzer not available for testing")
        return

    suite = Phase5SustainedLoadTestingSuite()

    # Execute comprehensive sustained load test
    results = suite.run_sustained_load_test(
        operations_count=50,  # Sustained operations
        dataset_size="large",  # Production-scale dataset
    )

    # Generate comprehensive report
    report = suite.generate_comprehensive_report(results)
    print("\n" + report)

    # Save detailed results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_file = f"phase5_sustained_load_results_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    # Quick summary for decision making
    if "threshold_compliance" in results:
        threshold_met = results["threshold_compliance"]["threshold_met"]
        leak_rate = results["threshold_compliance"][
            "actual_leak_rate_mb_per_min"
        ]

        print("\n" + "=" * 70)
        print("PHASE 5 EXECUTIVE SUMMARY:")
        print(
            f"Memory Leak Rate: {leak_rate:.6f} MB/min (Threshold: <10.0 MB/min)"
        )
        print(
            f"Threshold Compliance: {'✅ PASSED' if threshold_met else '❌ FAILED'}"
        )

        if threshold_met:
            print("🎉 PHASE 5 RESULT: PRODUCTION READY")
            print("   SizeAnalyzer meets sustained operation requirements!")
        else:
            print("⚠️  PHASE 5 RESULT: REQUIRES OPTIMIZATION")
            print(
                "   Additional memory optimization needed for production deployment."
            )

        print("=" * 70)

    return results


if __name__ == "__main__":
    main()
