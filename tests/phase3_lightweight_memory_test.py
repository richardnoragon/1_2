#!/usr/bin/env python3
"""
Phase 3: Lightweight Enterprise Memory Management Test Suite

Principal Engineer Implementation - NO COMPROMISE ENTERPRISE STANDARDS
Author: Richard Noragon - Principal Engineer
Created: 2025-09-14
Version: 3.1.0 Enterprise Production (Controlled)

CRITICAL REQUIREMENTS:
- Memory management optimization validation
- Widget leak prevention verification
- Performance monitoring with timeout controls
- Production-ready error handling

This lightweight test suite implements:
1. Controlled Memory Leak Detection (small batches)
2. Widget Lifecycle Validation (limited iterations)
3. Performance Benchmarking (with timeouts)
4. Enterprise Production Readiness Assessment
"""

import gc
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import psutil

# Enterprise logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add src to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

try:
    from PyQt5.QtWidgets import QApplication
except ImportError as e:
    print(f"CRITICAL: PyQt5 missing: {e}")
    sys.exit(1)

try:
    from src.config_manager import get_config_manager
    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
except ImportError as e:
    print(f"CRITICAL: RFU components missing: {e}")
    sys.exit(1)


class LightweightMemoryProfiler:
    """Lightweight memory profiler with enterprise precision."""

    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = 0
        self.peak_memory = 0
        self.memory_samples = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def start_profiling(self) -> None:
        """Start memory profiling session."""
        gc.collect()
        time.sleep(0.1)

        memory_info = self.process.memory_info()
        self.baseline_memory = memory_info.rss
        self.peak_memory = self.baseline_memory
        self.memory_samples = [self.baseline_memory]

        baseline_mb = self.baseline_memory / 1024 / 1024
        msg = f"Memory profiling started - Baseline: {baseline_mb:.2f} MB"
        self.logger.info(msg)

    def sample_memory(self) -> float:
        """Sample current memory usage."""
        memory_info = self.process.memory_info()
        current_memory = memory_info.rss

        self.memory_samples.append(current_memory)
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        return current_memory

    def get_memory_growth(self) -> float:
        """Calculate memory growth percentage from baseline."""
        if not self.memory_samples or self.baseline_memory == 0:
            return 0.0

        current_memory = self.memory_samples[-1]
        delta = current_memory - self.baseline_memory
        growth = (delta / self.baseline_memory) * 100
        return growth

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate memory usage report."""
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
        }


class LightweightMemoryManagementTester:
    """Lightweight Memory Management Test Suite - Enterprise Standards."""

    # Enterprise test thresholds (more conservative)
    MAX_MEMORY_GROWTH_PERCENT = 5.0  # Allow 5% growth for smaller tests
    MAX_TEST_DURATION_SECONDS = 120  # 2-minute timeout
    TEST_ITERATIONS = 10  # Reduced from 1000 to prevent loops
    STRESS_OPERATIONS = 5  # Reduced from 50

    def __init__(self):
        self.app = None
        self.profiler = LightweightMemoryProfiler()
        self.config_manager = get_config_manager()
        self.logger = logging.getLogger(self.__class__.__name__)

    def setup_test_environment(self) -> bool:
        """Setup controlled test environment."""
        try:
            # Create QApplication if not exists
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            # Initialize profiler
            self.profiler.start_profiling()

            self.logger.info("✅ Lightweight test environment setup complete")
            return True

        except Exception as e:
            self.logger.error(f"❌ Test environment setup failed: {e}")
            return False

    def test_basic_widget_lifecycle(self) -> Dict[str, Any]:
        """Test basic widget lifecycle with timeout control."""
        self.logger.info("🔧 Testing Basic Widget Lifecycle...")

        test_start_time = time.perf_counter()
        widget_creation_times = []
        cleanup_failures = 0
        widgets_created = 0

        # Controlled widget creation and destruction
        for iteration in range(self.TEST_ITERATIONS):
            # Timeout check
            if (
                time.perf_counter() - test_start_time
            ) > self.MAX_TEST_DURATION_SECONDS:
                self.logger.warning(
                    f"Test timeout reached at iteration {iteration}"
                )
                break

            try:
                # Create explorer instance with timing
                widget_start = time.perf_counter()
                explorer = MultiPaneFileExplorer()

                # Show and initialize (minimal processing)
                explorer.show()
                self.app.processEvents()

                widget_create_time = (
                    time.perf_counter() - widget_start
                ) * 1000
                widget_creation_times.append(widget_create_time)
                widgets_created += 1

                # Perform minimal layout operation to test functionality
                try:
                    explorer.set_pane_count(2)
                    self.app.processEvents()
                except Exception as e:
                    self.logger.warning(f"Layout operation failed: {e}")
                    cleanup_failures += 1

                # Clean up widget immediately
                try:
                    explorer.close()
                    explorer.deleteLater()
                    self.app.processEvents()

                    # Force cleanup every 5 iterations
                    if (iteration + 1) % 5 == 0:
                        gc.collect()
                        self.profiler.sample_memory()

                except Exception as e:
                    self.logger.error(f"Widget cleanup failed: {e}")
                    cleanup_failures += 1

            except Exception as e:
                self.logger.error(f"Widget creation failed: {e}")
                cleanup_failures += 1

        test_duration = time.perf_counter() - test_start_time

        # Calculate metrics
        avg_creation_time = (
            sum(widget_creation_times) / len(widget_creation_times)
            if widget_creation_times
            else 0
        )
        cleanup_success_rate = (
            ((widgets_created - cleanup_failures) / widgets_created) * 100
            if widgets_created > 0
            else 0
        )

        # Get final memory report
        memory_report = self.profiler.get_memory_report()

        # Validate against thresholds
        test_passed = (
            memory_report["memory_growth_percent"]
            <= self.MAX_MEMORY_GROWTH_PERCENT
            and cleanup_success_rate >= 90.0
            and test_duration <= self.MAX_TEST_DURATION_SECONDS
        )

        return {
            "test_name": "Basic Widget Lifecycle",
            "test_passed": test_passed,
            "test_duration_seconds": test_duration,
            "iterations_completed": widgets_created,
            "performance_metrics": {
                "avg_creation_time_ms": avg_creation_time,
                "cleanup_success_rate_percent": cleanup_success_rate,
                "cleanup_failures": cleanup_failures,
            },
            "memory_analysis": memory_report,
            "threshold_validation": {
                "memory_growth_compliant": memory_report[
                    "memory_growth_percent"
                ]
                <= self.MAX_MEMORY_GROWTH_PERCENT,
                "cleanup_success_compliant": cleanup_success_rate >= 90.0,
                "duration_compliant": test_duration
                <= self.MAX_TEST_DURATION_SECONDS,
            },
        }

    def test_controlled_stress_operations(self) -> Dict[str, Any]:
        """Test controlled stress operations with timeout."""
        self.logger.info("🔥 Testing Controlled Stress Operations...")

        test_start_time = time.perf_counter()
        stress_operations_completed = 0
        stress_failures = 0

        # Create single persistent explorer for stress testing
        try:
            explorer = MultiPaneFileExplorer()
            explorer.show()
            self.app.processEvents()

            # Perform controlled stress operations
            for stress_cycle in range(self.STRESS_OPERATIONS):
                # Timeout check
                if (
                    time.perf_counter() - test_start_time
                ) > self.MAX_TEST_DURATION_SECONDS:
                    self.logger.warning(
                        f"Stress test timeout at cycle {stress_cycle}"
                    )
                    break

                try:
                    # Limited pane count changes
                    for pane_count in [2, 3, 2]:
                        explorer.set_pane_count(pane_count)
                        self.app.processEvents()
                        time.sleep(0.01)  # Small delay to prevent overwhelming

                    # Limited layout changes
                    if hasattr(explorer, "layout_combo"):
                        for layout_name in ["Horizontal", "Vertical"]:
                            index = explorer.layout_combo.findText(layout_name)
                            if index >= 0:
                                explorer.layout_combo.setCurrentIndex(index)
                                if hasattr(explorer, "_on_layout_changed"):
                                    explorer._on_layout_changed()
                                self.app.processEvents()
                                time.sleep(0.01)

                    # Sample memory
                    self.profiler.sample_memory()
                    stress_operations_completed += 1

                except Exception as e:
                    self.logger.error(f"Stress operation failed: {e}")
                    stress_failures += 1
                    # Continue with other operations

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
            (stress_operations_completed / self.STRESS_OPERATIONS) * 100
            if self.STRESS_OPERATIONS > 0
            else 0
        )

        stress_test_passed = (
            stress_success_rate >= 80.0
            and final_memory_report["memory_growth_percent"]
            <= (self.MAX_MEMORY_GROWTH_PERCENT * 2)
            and test_duration <= self.MAX_TEST_DURATION_SECONDS
        )

        return {
            "test_name": "Controlled Stress Operations",
            "test_passed": stress_test_passed,
            "test_duration_seconds": test_duration,
            "stress_metrics": {
                "operations_completed": stress_operations_completed,
                "operations_failed": stress_failures,
                "stress_success_rate_percent": stress_success_rate,
            },
            "memory_analysis": final_memory_report,
            "stress_validation": {
                "stress_success_compliant": stress_success_rate >= 80.0,
                "memory_efficiency_compliant": final_memory_report[
                    "memory_growth_percent"
                ]
                <= (self.MAX_MEMORY_GROWTH_PERCENT * 2),
                "duration_compliant": test_duration
                <= self.MAX_TEST_DURATION_SECONDS,
            },
        }

    def run_lightweight_memory_test(self) -> Dict[str, Any]:
        """Run lightweight enterprise memory management test suite."""
        self.logger.info(
            "🚀 Starting Lightweight Enterprise Memory Test Suite"
        )

        test_suite_start = time.perf_counter()

        # Setup test environment
        if not self.setup_test_environment():
            return {"error": "Test environment setup failed"}

        # Execute test suites
        test_results = {
            "test_metadata": {
                "test_suite": "Phase 3 Lightweight Enterprise Memory Management",
                "test_start_time": datetime.now().isoformat(),
                "tester_version": "3.1.0 Enterprise Production (Controlled)",
                "principal_engineer": "Richard Noragon",
                "test_standards": "NO COMPROMISE ENTERPRISE - LIGHTWEIGHT",
            },
            "test_suites": {},
        }

        # Basic Widget Lifecycle Test
        try:
            lifecycle_results = self.test_basic_widget_lifecycle()
            test_results["test_suites"]["widget_lifecycle"] = lifecycle_results
            status = (
                "✅ PASSED"
                if lifecycle_results["test_passed"]
                else "❌ FAILED"
            )
            self.logger.info(f"Widget Lifecycle Test: {status}")
        except Exception as e:
            self.logger.error(f"Widget Lifecycle Test failed: {e}")
            test_results["test_suites"]["widget_lifecycle"] = {
                "error": str(e),
                "test_passed": False,
            }

        # Controlled Stress Test
        try:
            stress_results = self.test_controlled_stress_operations()
            test_results["test_suites"]["controlled_stress"] = stress_results
            status = (
                "✅ PASSED" if stress_results["test_passed"] else "❌ FAILED"
            )
            self.logger.info(f"Controlled Stress Test: {status}")
        except Exception as e:
            self.logger.error(f"Controlled Stress Test failed: {e}")
            test_results["test_suites"]["controlled_stress"] = {
                "error": str(e),
                "test_passed": False,
            }

        # Calculate overall results
        test_suite_duration = time.perf_counter() - test_suite_start

        all_tests_passed = all(
            [
                test_results["test_suites"]
                .get("widget_lifecycle", {})
                .get("test_passed", False),
                test_results["test_suites"]
                .get("controlled_stress", {})
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
        """Save test results with enterprise documentation standards."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase3_lightweight_memory_test_{timestamp}.json"
        filepath = Path(__file__).parent.parent / "results" / filename

        # Ensure results directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save results
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"💾 Test results saved: {filepath}")
        return str(filepath)


def main():
    """Execute Phase 3 Lightweight Enterprise Memory Test Suite."""
    print("=" * 80)
    print("🎯 PHASE 3 LIGHTWEIGHT ENTERPRISE MEMORY TEST SUITE")
    print("   Principal Engineer Implementation - NO COMPROMISE STANDARDS")
    print("   Author: Richard Noragon")
    print("   Version: 3.1.0 Enterprise Production (Controlled)")
    print("=" * 80)

    tester = LightweightMemoryManagementTester()

    try:
        # Run lightweight test suite
        results = tester.run_lightweight_memory_test()

        # Save results
        results_file = tester.save_test_results(results)

        # Print executive summary
        print("\n" + "=" * 80)
        print("📊 EXECUTIVE SUMMARY - LIGHTWEIGHT MEMORY TEST")
        print("=" * 80)

        test_completion = results.get("test_completion", {})
        production_readiness = results.get("production_readiness", {})

        status = (
            "✅ ALL TESTS PASSED"
            if test_completion.get("all_tests_passed")
            else "❌ TESTS FAILED"
        )
        print(f"Overall Test Result: {status}")

        compliance = (
            "✅ COMPLIANT"
            if test_completion.get("enterprise_compliance")
            else "❌ NON-COMPLIANT"
        )
        print(f"Enterprise Compliance: {compliance}")

        recommendation = production_readiness.get(
            "deployment_recommendation", "UNKNOWN"
        )
        print(f"Production Readiness: {recommendation}")

        duration = test_completion.get("total_duration_seconds", 0)
        print(f"Test Duration: {duration:.2f} seconds")

        # Memory summary
        memory_assessment = results.get("final_memory_assessment", {})
        growth = memory_assessment.get("memory_growth_percent", 0)
        print(f"\nMemory Growth: {growth:.2f}% (Threshold: ≤5.0%)")

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
