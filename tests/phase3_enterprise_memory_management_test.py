#!/usr/bin/env python3
"""
Phase 3: Enterprise Memory Management Optimization and Widget Leak Prevention
Test Suite

Principal Engineer Implementation - NO COMPROMISE ENTERPRISE STANDARDS
Author: Richard Noragon - Principal Engineer
Created: 2025-09-14
Version: 3.0.0 Enterprise Production

CRITICAL REQUIREMENTS:
- Memory management optimization with <2% memory growth over 1000 operations
- Widget leak prevention with 100% cleanup validation
- Enterprise-grade performance monitoring with sub-millisecond precision
- Production-ready error handling with comprehensive recovery mechanisms

This test suite implements:
1. Comprehensive Memory Leak Detection
2. Widget Lifecycle Management Validation
3. Performance Benchmarking Under Load
4. Memory Optimization Verification
5. Enterprise Production Readiness Assessment
"""

import gc
import json
import logging
import sys
import time
import traceback
import weakref
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import psutil

# Enterprise logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/phase3_memory_test.log"),
        logging.StreamHandler(),
    ],
)

# Add src to path for imports
# Add src to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

try:
    from PyQt5.QtWidgets import QApplication, QWidget
except ImportError as e:
    print(f"CRITICAL: Required dependencies missing: {e}")
    sys.exit(1)

try:
    from src.config_manager import get_config_manager
    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
except ImportError as e:
    print(f"CRITICAL: RFU components missing: {e}")
    sys.exit(1)


class EnterpriseMemoryProfiler:
    """Enterprise-grade memory profiling with sub-millisecond precision."""

    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = 0
        self.peak_memory = 0
        self.memory_samples = []
        self.widget_references = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    def start_profiling(self) -> None:
        """Start enterprise memory profiling session."""
        gc.collect()  # Force garbage collection for clean baseline
        time.sleep(0.1)  # Allow GC to complete

        memory_info = self.process.memory_info()
        self.baseline_memory = memory_info.rss
        self.peak_memory = self.baseline_memory
        self.memory_samples = [self.baseline_memory]

        baseline_mb = self.baseline_memory / 1024 / 1024
        msg = f"Memory profiling started - Baseline: {baseline_mb:.2f} MB"
        self.logger.info(msg)

    def sample_memory(self) -> float:
        """Sample current memory usage with high precision."""
        memory_info = self.process.memory_info()
        current_memory = memory_info.rss

        self.memory_samples.append(current_memory)
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        return current_memory

    def register_widget(self, widget: QWidget) -> str:
        """Register widget for leak detection."""
        widget_id = f"widget_{id(widget)}_{time.time_ns()}"
        weak_ref = weakref.ref(widget)
        self.widget_references.add((widget_id, weak_ref))
        return widget_id

    def check_widget_leaks(self) -> Tuple[int, int, List[str]]:
        """Check for widget memory leaks."""
        gc.collect()  # Force cleanup
        time.sleep(0.1)

        alive_widgets = []
        dead_widgets = []
        leaked_widgets = []

        for widget_id, weak_ref in self.widget_references:
            if weak_ref() is not None:
                alive_widgets.append(widget_id)
                leaked_widgets.append(widget_id)
            else:
                dead_widgets.append(widget_id)

        return len(alive_widgets), len(dead_widgets), leaked_widgets

    def get_memory_growth(self) -> float:
        """Calculate memory growth percentage from baseline."""
        if not self.memory_samples or self.baseline_memory == 0:
            return 0.0

        current_memory = self.memory_samples[-1]
        delta = current_memory - self.baseline_memory
        growth = (delta / self.baseline_memory) * 100
        return growth

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory usage report."""
        alive_count, dead_count, leaked_widgets = self.check_widget_leaks()

        return {
            "baseline_memory_mb": self.baseline_memory / 1024 / 1024,
            "peak_memory_mb": self.peak_memory / 1024 / 1024,
            "current_memory_mb": (
                self.memory_samples[-1] / 1024 / 1024
                if self.memory_samples
                else 0
            ),
            "memory_growth_percent": self.get_memory_growth(),
            "memory_samples_count": len(self.memory_samples),
            "widget_leak_detection": {
                "alive_widgets": alive_count,
                "dead_widgets": dead_count,
                "leaked_widgets": leaked_widgets,
                "leak_rate_percent": (
                    (alive_count / (alive_count + dead_count) * 100)
                    if (alive_count + dead_count) > 0
                    else 0
                ),
            },
        }


class EnterpriseMemoryManagementTester:
    """Enterprise Memory Management Test Suite with NO COMPROMISE standards."""

    # Enterprise test thresholds
    MAX_MEMORY_GROWTH_PERCENT = 2.0  # Maximum 2% memory growth
    MAX_WIDGET_LEAK_RATE = 0.0  # Zero tolerance for widget leaks
    MIN_CLEANUP_SUCCESS_RATE = 99.5  # 99.5% cleanup success rate
    MAX_OPERATION_TIME_MS = 100  # Sub-100ms operation time

    def __init__(self):
        self.app = None
        self.explorer = None
        self.profiler = EnterpriseMemoryProfiler()
        self.test_results = {}
        self.config_manager = get_config_manager()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Test configuration
        self.test_iterations = 1000  # Enterprise load testing
        self.stress_operations = 50  # High-stress operation count

    def setup_test_environment(self) -> bool:
        """Setup enterprise test environment with validation."""
        try:
            # Create QApplication if not exists
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            # Initialize profiler
            self.profiler.start_profiling()

            self.logger.info("✅ Enterprise test environment setup complete")
            return True

        except Exception as e:
            self.logger.error(f"❌ Test environment setup failed: {e}")
            traceback.print_exc()
            return False

    @contextmanager
    def memory_monitoring_context(self, operation_name: str):
        """Context manager for memory monitoring during operations."""
        start_time = time.perf_counter()
        start_memory = self.profiler.sample_memory()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = self.profiler.sample_memory()

            operation_time_ms = (end_time - start_time) * 1000
            memory_delta_mb = (end_memory - start_memory) / 1024 / 1024

            self.logger.info(
                f"{operation_name}: {operation_time_ms:.3f}ms, Memory Δ: {memory_delta_mb:.3f}MB"
            )

    def test_widget_lifecycle_management(self) -> Dict[str, Any]:
        """Test comprehensive widget lifecycle management."""
        self.logger.info("🔧 Testing Widget Lifecycle Management...")

        test_start_time = time.perf_counter()
        widget_creation_times = []
        widget_destruction_times = []
        cleanup_failures = 0

        # Test widget creation and destruction cycles
        for iteration in range(self.test_iterations):
            with self.memory_monitoring_context(
                f"Widget Lifecycle Iteration {iteration + 1}"
            ):

                # Create explorer instance
                widget_start = time.perf_counter()
                explorer = MultiPaneFileExplorer()
                self.profiler.register_widget(explorer)

                # Show and initialize
                explorer.show()
                self.app.processEvents()

                widget_create_time = (
                    time.perf_counter() - widget_start
                ) * 1000
                widget_creation_times.append(widget_create_time)

                # Perform layout operations
                try:
                    for pane_count in [1, 2, 3, 4]:
                        explorer.set_pane_count(pane_count)
                        self.app.processEvents()

                    for layout_mode in ["horizontal", "vertical", "grid"]:
                        if hasattr(explorer, "layout_combo"):
                            index = explorer.layout_combo.findText(
                                layout_mode.capitalize()
                            )
                            if index >= 0:
                                explorer.layout_combo.setCurrentIndex(index)
                                explorer._on_layout_changed()
                                self.app.processEvents()

                except Exception as e:
                    self.logger.warning(f"Layout operation failed: {e}")
                    cleanup_failures += 1

                # Clean up widget
                cleanup_start = time.perf_counter()
                try:
                    explorer.close()
                    explorer.deleteLater()
                    self.app.processEvents()
                    gc.collect()

                    cleanup_time = (time.perf_counter() - cleanup_start) * 1000
                    widget_destruction_times.append(cleanup_time)

                except Exception as e:
                    self.logger.error(f"Widget cleanup failed: {e}")
                    cleanup_failures += 1

                # Sample memory every 100 iterations
                if (iteration + 1) % 100 == 0:
                    self.profiler.sample_memory()
                    alive, _, leaked = self.profiler.check_widget_leaks()
                    msg = f"Progress: {iteration + 1}/{self.test_iterations}, "
                    msg += f"Alive widgets: {alive}, Leaked: {len(leaked)}"
                    self.logger.info(msg)

        test_duration = time.perf_counter() - test_start_time

        # Calculate performance metrics
        avg_creation_time = (
            sum(widget_creation_times) / len(widget_creation_times)
            if widget_creation_times
            else 0
        )
        avg_destruction_time = (
            sum(widget_destruction_times) / len(widget_destruction_times)
            if widget_destruction_times
            else 0
        )
        cleanup_success_rate = (
            (self.test_iterations - cleanup_failures) / self.test_iterations
        ) * 100

        # Get final memory report
        memory_report = self.profiler.get_memory_report()

        # Validate against enterprise thresholds
        test_passed = (
            memory_report["memory_growth_percent"]
            <= self.MAX_MEMORY_GROWTH_PERCENT
            and memory_report["widget_leak_detection"]["leak_rate_percent"]
            <= self.MAX_WIDGET_LEAK_RATE
            and cleanup_success_rate >= self.MIN_CLEANUP_SUCCESS_RATE
            and avg_creation_time <= self.MAX_OPERATION_TIME_MS
        )

        return {
            "test_name": "Widget Lifecycle Management",
            "test_passed": test_passed,
            "test_duration_seconds": test_duration,
            "iterations_completed": self.test_iterations,
            "performance_metrics": {
                "avg_creation_time_ms": avg_creation_time,
                "avg_destruction_time_ms": avg_destruction_time,
                "cleanup_success_rate_percent": cleanup_success_rate,
                "cleanup_failures": cleanup_failures,
            },
            "memory_analysis": memory_report,
            "enterprise_thresholds": {
                "max_memory_growth_percent": self.MAX_MEMORY_GROWTH_PERCENT,
                "max_widget_leak_rate": self.MAX_WIDGET_LEAK_RATE,
                "min_cleanup_success_rate": self.MIN_CLEANUP_SUCCESS_RATE,
                "max_operation_time_ms": self.MAX_OPERATION_TIME_MS,
            },
            "threshold_validation": {
                "memory_growth_compliant": memory_report[
                    "memory_growth_percent"
                ]
                <= self.MAX_MEMORY_GROWTH_PERCENT,
                "widget_leak_compliant": memory_report[
                    "widget_leak_detection"
                ]["leak_rate_percent"]
                <= self.MAX_WIDGET_LEAK_RATE,
                "cleanup_success_compliant": cleanup_success_rate
                >= self.MIN_CLEANUP_SUCCESS_RATE,
                "performance_compliant": avg_creation_time
                <= self.MAX_OPERATION_TIME_MS,
            },
        }

    def test_memory_stress_operations(self) -> Dict[str, Any]:
        """Test memory management under enterprise stress conditions."""
        self.logger.info(
            "🔥 Testing Memory Under Enterprise Stress Conditions..."
        )

        test_start_time = time.perf_counter()
        stress_operations_completed = 0
        stress_failures = 0
        memory_samples_under_stress = []

        # Create persistent explorer for stress testing
        try:
            explorer = MultiPaneFileExplorer()
            explorer.show()
            self.app.processEvents()

            self.profiler.sample_memory()

            # Perform high-stress operations
            for stress_cycle in range(self.stress_operations):
                with self.memory_monitoring_context(
                    f"Stress Cycle {stress_cycle + 1}"
                ):

                    try:
                        # Rapid pane count changes
                        for pane_count in [1, 4, 2, 3, 1, 4]:
                            explorer.set_pane_count(pane_count)
                            self.app.processEvents()

                        # Rapid layout changes
                        for layout_mode in [
                            "horizontal",
                            "vertical",
                            "grid",
                            "horizontal",
                        ]:
                            if hasattr(explorer, "layout_combo"):
                                index = explorer.layout_combo.findText(
                                    layout_mode.capitalize()
                                )
                                if index >= 0:
                                    explorer.layout_combo.setCurrentIndex(
                                        index
                                    )
                                    explorer._on_layout_changed()
                                    self.app.processEvents()

                        # Force memory sampling
                        current_memory = self.profiler.sample_memory()
                        memory_samples_under_stress.append(current_memory)

                        stress_operations_completed += 1

                    except Exception as e:
                        self.logger.error(f"Stress operation failed: {e}")
                        stress_failures += 1

                # Periodic cleanup and validation
                if (stress_cycle + 1) % 10 == 0:
                    gc.collect()
                    _, _, leaked = self.profiler.check_widget_leaks()
                    current_growth = self.profiler.get_memory_growth()

                    msg = f"Stress Progress: {stress_cycle + 1}/{self.stress_operations}, "
                    msg += f"Memory Growth: {current_growth:.2f}%, Leaked: {len(leaked)}"
                    self.logger.info(msg)

            # Final cleanup
            explorer.close()
            explorer.deleteLater()
            self.app.processEvents()
            gc.collect()

        except Exception as e:
            self.logger.error(f"Stress test setup failed: {e}")
            stress_failures += 1

        test_duration = time.perf_counter() - test_start_time
        final_memory_report = self.profiler.get_memory_report()

        # Calculate stress test metrics
        stress_success_rate = (
            (stress_operations_completed / self.stress_operations) * 100
            if self.stress_operations > 0
            else 0
        )
        memory_efficiency = final_memory_report["memory_growth_percent"] <= (
            self.MAX_MEMORY_GROWTH_PERCENT * 2
        )  # Allow 2x growth under stress

        stress_test_passed = (
            stress_success_rate >= 95.0  # 95% stress operation success
            and memory_efficiency
            and final_memory_report["widget_leak_detection"][
                "leak_rate_percent"
            ]
            <= self.MAX_WIDGET_LEAK_RATE
        )

        return {
            "test_name": "Memory Stress Operations",
            "test_passed": stress_test_passed,
            "test_duration_seconds": test_duration,
            "stress_metrics": {
                "operations_completed": stress_operations_completed,
                "operations_failed": stress_failures,
                "stress_success_rate_percent": stress_success_rate,
                "memory_samples_collected": len(memory_samples_under_stress),
            },
            "memory_analysis": final_memory_report,
            "stress_validation": {
                "stress_success_compliant": stress_success_rate >= 95.0,
                "memory_efficiency_compliant": memory_efficiency,
                "widget_leak_compliant": final_memory_report[
                    "widget_leak_detection"
                ]["leak_rate_percent"]
                <= self.MAX_WIDGET_LEAK_RATE,
            },
        }

    def run_comprehensive_memory_test(self) -> Dict[str, Any]:
        """Run comprehensive enterprise memory management test suite."""
        self.logger.info("🚀 Starting Enterprise Memory Management Test Suite")

        test_suite_start = time.perf_counter()

        # Setup test environment
        if not self.setup_test_environment():
            return {"error": "Test environment setup failed"}

        # Execute test suites
        test_results = {
            "test_metadata": {
                "test_suite": "Phase 3 Enterprise Memory Management",
                "test_start_time": datetime.now().isoformat(),
                "tester_version": "3.0.0 Enterprise Production",
                "principal_engineer": "Richard Noragon",
                "test_standards": "NO COMPROMISE ENTERPRISE",
            },
            "test_suites": {},
        }

        # Widget Lifecycle Management Test
        try:
            lifecycle_results = self.test_widget_lifecycle_management()
            test_results["test_suites"]["widget_lifecycle"] = lifecycle_results
            self.logger.info(
                f"Widget Lifecycle Test: {'✅ PASSED' if lifecycle_results['test_passed'] else '❌ FAILED'}"
            )
        except Exception as e:
            self.logger.error(f"Widget Lifecycle Test failed: {e}")
            test_results["test_suites"]["widget_lifecycle"] = {
                "error": str(e),
                "test_passed": False,
            }

        # Memory Stress Test
        try:
            stress_results = self.test_memory_stress_operations()
            test_results["test_suites"]["memory_stress"] = stress_results
            self.logger.info(
                f"Memory Stress Test: {'✅ PASSED' if stress_results['test_passed'] else '❌ FAILED'}"
            )
        except Exception as e:
            self.logger.error(f"Memory Stress Test failed: {e}")
            test_results["test_suites"]["memory_stress"] = {
                "error": str(e),
                "test_passed": False,
            }

        # Calculate overall test results
        test_suite_duration = time.perf_counter() - test_suite_start

        all_tests_passed = all(
            [
                test_results["test_suites"]
                .get("widget_lifecycle", {})
                .get("test_passed", False),
                test_results["test_suites"]
                .get("memory_stress", {})
                .get("test_passed", False),
            ]
        )

        test_results.update(
            {
                "test_completion": {
                    "test_end_time": datetime.now().isoformat(),
                    "total_duration_seconds": test_suite_duration,
                    "all_tests_passed": all_tests_passed,
                    "enterprise_compliance": all_tests_passed,
                },
                "final_memory_assessment": self.profiler.get_memory_report(),
                "production_readiness": {
                    "memory_management_ready": all_tests_passed,
                    "widget_leak_prevention_ready": all_tests_passed,
                    "enterprise_standards_met": all_tests_passed,
                    "deployment_recommendation": (
                        "APPROVED FOR ENTERPRISE DEPLOYMENT"
                        if all_tests_passed
                        else "REQUIRES REMEDIATION BEFORE DEPLOYMENT"
                    ),
                },
            }
        )

        return test_results

    def save_test_results(self, results: Dict[str, Any]) -> str:
        """Save comprehensive test results with enterprise documentation standards."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase3_enterprise_memory_management_test_{timestamp}.json"
        filepath = Path(__file__).parent.parent / "results" / filename

        # Ensure results directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save results with comprehensive formatting
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"💾 Enterprise test results saved: {filepath}")
        return str(filepath)


def main():
    """Execute Phase 3 Enterprise Memory Management Test Suite."""
    print("=" * 80)
    print("🎯 PHASE 3 ENTERPRISE MEMORY MANAGEMENT TEST SUITE")
    print("   Principal Engineer Implementation - NO COMPROMISE STANDARDS")
    print("   Author: Richard Noragon")
    print("   Version: 3.0.0 Enterprise Production")
    print("=" * 80)

    tester = EnterpriseMemoryManagementTester()

    try:
        # Run comprehensive test suite
        results = tester.run_comprehensive_memory_test()

        # Save results
        results_file = tester.save_test_results(results)

        # Print executive summary
        print("\n" + "=" * 80)
        print("📊 EXECUTIVE SUMMARY - ENTERPRISE MEMORY MANAGEMENT TEST")
        print("=" * 80)

        test_completion = results.get("test_completion", {})
        production_readiness = results.get("production_readiness", {})

        print(
            f"Overall Test Result: {'✅ ALL TESTS PASSED' if test_completion.get('all_tests_passed') else '❌ TESTS FAILED'}"
        )
        print(
            f"Enterprise Compliance: {'✅ COMPLIANT' if test_completion.get('enterprise_compliance') else '❌ NON-COMPLIANT'}"
        )
        print(
            f"Production Readiness: {production_readiness.get('deployment_recommendation', 'UNKNOWN')}"
        )
        print(
            f"Test Duration: {test_completion.get('total_duration_seconds', 0):.2f} seconds"
        )

        # Memory management summary
        memory_assessment = results.get("final_memory_assessment", {})
        print(
            f"\nMemory Growth: {memory_assessment.get('memory_growth_percent', 0):.2f}% (Threshold: ≤2.0%)"
        )
        print(
            f"Widget Leak Rate: {memory_assessment.get('widget_leak_detection', {}).get('leak_rate_percent', 0):.2f}% (Threshold: 0.0%)"
        )

        print(f"\nDetailed Results: {results_file}")
        print("=" * 80)

        # Return appropriate exit code
        return 0 if test_completion.get("all_tests_passed") else 1

    except Exception as e:
        print(f"\n❌ CRITICAL TEST FAILURE: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
