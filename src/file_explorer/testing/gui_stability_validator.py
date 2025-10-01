#!/usr/bin/env python3
"""
GUI Stability Validation Framework

Comprehensive testing and validation framework for GUI component stability,
preventing degradation during development iterations and ensuring reliable
operation under all conditions.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class StabilityTestResult:
    """Result of a stability test."""

    def __init__(
        self,
        test_name: str,
        success: bool,
        duration: float,
        error: Optional[str] = None,
    ):
        """Initialize test result."""
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.error = error
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration": self.duration,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


class GUIStabilityValidator:
    """
    Comprehensive GUI stability validation framework.

    Features:
    - Widget lifecycle testing
    - Memory leak detection
    - Component degradation prevention
    - Stress testing capabilities
    - Automated regression detection
    """

    def __init__(self):
        """Initialize stability validator."""
        self.logger = logging.getLogger("RFU.StabilityValidator")
        self.test_results: List[StabilityTestResult] = []

        # Test configuration
        self.stress_test_duration = 30  # seconds
        self.memory_check_interval = 1  # seconds
        self.max_memory_growth = 50  # MB

        # Component tracking
        self.tracked_components: Dict[str, Any] = {}
        self.baseline_memory = 0

    def validate_widget_lifecycle(
        self, widget: QWidget, test_duration: int = 10
    ) -> StabilityTestResult:
        """
        Validate widget lifecycle stability.

        Args:
            widget: Widget to test
            test_duration: Test duration in seconds

        Returns:
            StabilityTestResult: Test result
        """
        test_name = f"Widget Lifecycle - {widget.__class__.__name__}"
        start_time = time.time()

        try:
            self.logger.info(
                f"Starting widget lifecycle test for {widget.__class__.__name__}"
            )

            # Register with component guardian
            from ...gui.component_guardian import register_gui_component

            comp_id = register_gui_component(widget, widget.__class__.__name__)

            if not comp_id:
                error = "Failed to register with component guardian"
                duration = time.time() - start_time
                return StabilityTestResult(test_name, False, duration, error)

            # Perform lifecycle operations
            operations = [
                ("show", lambda w: w.show()),
                ("hide", lambda w: w.hide()),
                ("resize", lambda w: w.resize(800, 600)),
                ("move", lambda w: w.move(100, 100)),
                ("visibility_check", lambda w: w.isVisible()),
                ("geometry_check", lambda w: w.geometry()),
                ("parent_check", lambda w: w.parent()),
            ]

            for op_name, operation in operations:
                try:
                    operation(widget)
                    self.logger.debug(f"Operation {op_name} successful")
                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        error = f"Widget destroyed during {op_name}"
                        duration = time.time() - start_time
                        return StabilityTestResult(test_name, False, duration, error)
                    raise

                # Brief pause between operations
                time.sleep(0.1)

            # Stress test - rapid operations
            for i in range(100):
                try:
                    widget.isVisible()
                    if i % 10 == 0:
                        widget.update()
                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        error = f"Widget destroyed during stress test iteration {i}"
                        duration = time.time() - start_time
                        return StabilityTestResult(test_name, False, duration, error)
                    raise

            duration = time.time() - start_time
            self.logger.info(
                f"Widget lifecycle test completed successfully in {duration:.2f}s"
            )

            result = StabilityTestResult(test_name, True, duration)
            self.test_results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start_time
            error = f"Unexpected error: {str(e)}"
            self.logger.error(f"Widget lifecycle test failed: {e}")

            result = StabilityTestResult(test_name, False, duration, error)
            self.test_results.append(result)
            return result

    def validate_memory_stability(
        self, widget: QWidget, duration: int = 60
    ) -> StabilityTestResult:
        """
        Validate memory stability over time.

        Args:
            widget: Widget to monitor
            duration: Monitoring duration in seconds

        Returns:
            StabilityTestResult: Test result
        """
        test_name = f"Memory Stability - {widget.__class__.__name__}"
        start_time = time.time()

        try:
            import gc

            import psutil

            self.logger.info(f"Starting memory stability test for {duration}s")

            # Record baseline memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            memory_samples = []
            end_time = start_time + duration

            while time.time() < end_time:
                try:
                    # Perform operations that might leak memory
                    widget.isVisible()
                    widget.geometry()
                    widget.update()

                    # Force garbage collection
                    gc.collect()

                    # Sample memory usage
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)

                    time.sleep(1)

                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        error = "Widget destroyed during memory test"
                        duration_actual = time.time() - start_time
                        return StabilityTestResult(
                            test_name, False, duration_actual, error
                        )
                    raise

            # Analyze memory usage
            final_memory = memory_samples[-1] if memory_samples else initial_memory
            memory_growth = final_memory - initial_memory
            max_memory = max(memory_samples) if memory_samples else initial_memory

            duration_actual = time.time() - start_time

            if memory_growth > self.max_memory_growth:
                error = f"Memory growth {memory_growth:.1f}MB exceeds limit"
                result = StabilityTestResult(test_name, False, duration_actual, error)
            else:
                self.logger.info(f"Memory test passed: growth {memory_growth:.1f}MB")
                result = StabilityTestResult(test_name, True, duration_actual)

            self.test_results.append(result)
            return result

        except Exception as e:
            duration_actual = time.time() - start_time
            error = f"Memory test error: {str(e)}"

            result = StabilityTestResult(test_name, False, duration_actual, error)
            self.test_results.append(result)
            return result

    def validate_component_interactions(
        self, components: List[QWidget]
    ) -> StabilityTestResult:
        """
        Validate interactions between multiple components.

        Args:
            components: List of components to test

        Returns:
            StabilityTestResult: Test result
        """
        test_name = "Component Interactions"
        start_time = time.time()

        try:
            self.logger.info(
                f"Testing interactions between {len(components)} components"
            )

            # Test parent-child relationships
            for i, parent in enumerate(components):
                for j, child in enumerate(components[i + 1 :], i + 1):
                    try:
                        # Test setting parent-child relationship
                        original_parent = child.parent()
                        child.setParent(parent)

                        # Verify relationship
                        if child.parent() != parent:
                            error = f"Parent-child relationship failed: {i}->{j}"
                            duration = time.time() - start_time
                            return StabilityTestResult(
                                test_name, False, duration, error
                            )

                        # Restore original parent
                        child.setParent(original_parent)

                    except RuntimeError as e:
                        if "wrapped C/C++ object" in str(e):
                            error = f"Component destroyed during interaction test"
                            duration = time.time() - start_time
                            return StabilityTestResult(
                                test_name, False, duration, error
                            )
                        raise

            # Test rapid property access
            for component in components:
                for _ in range(50):
                    try:
                        _ = component.isVisible()
                        _ = component.geometry()
                        _ = component.parent()
                    except RuntimeError as e:
                        if "wrapped C/C++ object" in str(e):
                            error = "Component destroyed during property access"
                            duration = time.time() - start_time
                            return StabilityTestResult(
                                test_name, False, duration, error
                            )
                        raise

            duration = time.time() - start_time
            self.logger.info(f"Component interaction test passed in {duration:.2f}s")

            result = StabilityTestResult(test_name, True, duration)
            self.test_results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start_time
            error = f"Interaction test error: {str(e)}"

            result = StabilityTestResult(test_name, False, duration, error)
            self.test_results.append(result)
            return result

    def run_comprehensive_stability_test(self, main_widget: QWidget) -> Dict[str, Any]:
        """
        Run comprehensive stability test suite.

        Args:
            main_widget: Main widget to test

        Returns:
            Dict: Comprehensive test results
        """
        try:
            self.logger.info("Starting comprehensive stability test suite")
            start_time = datetime.now()

            # Clear previous results
            self.test_results.clear()

            # Test 1: Widget lifecycle
            lifecycle_result = self.validate_widget_lifecycle(main_widget)

            # Test 2: Memory stability
            memory_result = self.validate_memory_stability(main_widget, 30)

            # Test 3: Find child components and test interactions
            child_components = self._find_child_components(main_widget)
            if child_components:
                interaction_result = self.validate_component_interactions(
                    child_components[:5]
                )
            else:
                interaction_result = StabilityTestResult(
                    "Component Interactions", True, 0.0, "No child components found"
                )

            # Test 4: Stress test with rapid operations
            stress_result = self._perform_stress_test(main_widget)

            # Compile results
            all_results = [
                lifecycle_result,
                memory_result,
                interaction_result,
                stress_result,
            ]

            total_duration = (datetime.now() - start_time).total_seconds()
            success_count = sum(1 for r in all_results if r.success)
            overall_success = success_count == len(all_results)

            results = {
                "overall_success": overall_success,
                "success_rate": success_count / len(all_results),
                "total_duration": total_duration,
                "individual_results": [r.to_dict() for r in all_results],
                "summary": {
                    "total_tests": len(all_results),
                    "passed": success_count,
                    "failed": len(all_results) - success_count,
                },
            }

            status = "PASSED" if overall_success else "FAILED"
            self.logger.info(
                f"Comprehensive stability test {status} ({success_count}/{len(all_results)})"
            )

            return results

        except Exception as e:
            self.logger.error(f"Error during comprehensive test: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _find_child_components(self, widget: QWidget) -> List[QWidget]:
        """Find child components for interaction testing."""
        try:
            if not QT_AVAILABLE:
                return []

            children = widget.findChildren(QWidget)
            # Filter to meaningful components (not tiny utility widgets)
            meaningful_children = [
                child
                for child in children
                if (
                    hasattr(child, "width")
                    and child.width() > 50
                    and hasattr(child, "height")
                    and child.height() > 50
                )
            ]

            return meaningful_children[:10]  # Limit to first 10 for performance

        except Exception as e:
            self.logger.error(f"Error finding child components: {e}")
            return []

    def _perform_stress_test(self, widget: QWidget) -> StabilityTestResult:
        """Perform stress test with rapid operations."""
        test_name = "Stress Test"
        start_time = time.time()

        try:
            self.logger.info("Starting stress test")

            # Rapid operations for 10 seconds
            end_time = start_time + 10
            operation_count = 0

            while time.time() < end_time:
                try:
                    # Rapid property access
                    _ = widget.isVisible()
                    _ = widget.geometry()
                    _ = widget.size()
                    _ = widget.pos()

                    # Occasional updates
                    if operation_count % 100 == 0:
                        widget.update()

                    operation_count += 1

                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        error = f"Widget destroyed after {operation_count} operations"
                        duration = time.time() - start_time
                        return StabilityTestResult(test_name, False, duration, error)
                    raise

            duration = time.time() - start_time
            msg = f"Stress test passed: {operation_count} operations in {duration:.2f}s"
            self.logger.info(msg)

            return StabilityTestResult(test_name, True, duration)

        except Exception as e:
            duration = time.time() - start_time
            error = f"Stress test error: {str(e)}"
            return StabilityTestResult(test_name, False, duration, error)

    def validate_explorer_stability(self, explorer_widget) -> Dict[str, Any]:
        """
        Specialized validation for multi-pane explorer.

        Args:
            explorer_widget: Explorer widget to validate

        Returns:
            Dict: Validation results
        """
        try:
            self.logger.info("Starting explorer-specific stability validation")

            results = []

            # Test 1: Controller availability
            controller_result = self._test_controller_stability(explorer_widget)
            results.append(controller_result)

            # Test 2: Pane operations
            pane_result = self._test_pane_operations(explorer_widget)
            results.append(pane_result)

            # Test 3: Layout stability
            layout_result = self._test_layout_stability(explorer_widget)
            results.append(layout_result)

            # Test 4: Tool integration
            tool_result = self._test_tool_integration(explorer_widget)
            results.append(tool_result)

            # Compile results
            success_count = sum(1 for r in results if r.success)
            overall_success = success_count == len(results)

            return {
                "overall_success": overall_success,
                "success_rate": success_count / len(results),
                "individual_results": [r.to_dict() for r in results],
                "explorer_specific": True,
            }

        except Exception as e:
            self.logger.error(f"Error in explorer stability validation: {e}")
            return {"overall_success": False, "error": str(e)}

    def _test_controller_stability(self, explorer) -> StabilityTestResult:
        """Test explorer controller stability."""
        test_name = "Controller Stability"
        start_time = time.time()

        try:
            if not hasattr(explorer, "controller"):
                error = "No controller found"
                return StabilityTestResult(test_name, False, 0.0, error)

            controller = explorer.controller

            # Test controller methods
            try:
                status = controller.get_status()
                if not isinstance(status, dict):
                    error = "Controller status invalid"
                    duration = time.time() - start_time
                    return StabilityTestResult(test_name, False, duration, error)
            except Exception as e:
                error = f"Controller method failed: {e}"
                duration = time.time() - start_time
                return StabilityTestResult(test_name, False, duration, error)

            duration = time.time() - start_time
            return StabilityTestResult(test_name, True, duration)

        except Exception as e:
            duration = time.time() - start_time
            error = f"Controller test error: {e}"
            return StabilityTestResult(test_name, False, duration, error)

    def _test_pane_operations(self, explorer) -> StabilityTestResult:
        """Test pane operation stability."""
        test_name = "Pane Operations"
        start_time = time.time()

        try:
            if not hasattr(explorer, "controller"):
                error = "No controller for pane testing"
                return StabilityTestResult(test_name, False, 0.0, error)

            controller = explorer.controller

            # Test pane count changes
            original_count = getattr(controller, "pane_count", 2)

            for count in [1, 2, 3, 4, 2]:  # Test sequence
                try:
                    success = controller.set_pane_count(count)
                    if not success:
                        error = f"Failed to set pane count to {count}"
                        duration = time.time() - start_time
                        return StabilityTestResult(test_name, False, duration, error)

                    time.sleep(0.2)  # Allow UI to settle

                except Exception as e:
                    error = f"Pane count operation failed: {e}"
                    duration = time.time() - start_time
                    return StabilityTestResult(test_name, False, duration, error)

            # Restore original count
            controller.set_pane_count(original_count)

            duration = time.time() - start_time
            return StabilityTestResult(test_name, True, duration)

        except Exception as e:
            duration = time.time() - start_time
            error = f"Pane operations test error: {e}"
            return StabilityTestResult(test_name, False, duration, error)

    def _test_layout_stability(self, explorer) -> StabilityTestResult:
        """Test layout operation stability."""
        test_name = "Layout Stability"
        start_time = time.time()

        try:
            if not hasattr(explorer, "controller"):
                error = "No controller for layout testing"
                return StabilityTestResult(test_name, False, 0.0, error)

            controller = explorer.controller

            # Test layout mode changes
            layout_modes = ["horizontal", "vertical", "horizontal"]

            for mode in layout_modes:
                try:
                    success = controller.set_layout_mode(mode)
                    if not success:
                        error = f"Failed to set layout mode to {mode}"
                        duration = time.time() - start_time
                        return StabilityTestResult(test_name, False, duration, error)

                    time.sleep(0.2)  # Allow layout to settle

                except Exception as e:
                    error = f"Layout mode operation failed: {e}"
                    duration = time.time() - start_time
                    return StabilityTestResult(test_name, False, duration, error)

            duration = time.time() - start_time
            return StabilityTestResult(test_name, True, duration)

        except Exception as e:
            duration = time.time() - start_time
            error = f"Layout stability test error: {e}"
            return StabilityTestResult(test_name, False, duration, error)

    def _test_tool_integration(self, explorer) -> StabilityTestResult:
        """Test tool integration stability."""
        test_name = "Tool Integration"
        start_time = time.time()

        try:
            if not hasattr(explorer, "controller"):
                error = "No controller for tool testing"
                return StabilityTestResult(test_name, False, 0.0, error)

            controller = explorer.controller

            # Test tool availability
            if hasattr(controller, "_tool_integration"):
                tool_integration = controller._tool_integration

                if hasattr(tool_integration, "get_available_tools"):
                    available_tools = tool_integration.get_available_tools()
                    self.logger.info(f"Found {len(available_tools)} available tools")

                    # Test tool info retrieval
                    for tool_name in available_tools[:3]:  # Test first 3 tools
                        try:
                            info = tool_integration.get_tool_info(tool_name)
                            if not info:
                                error = f"Failed to get info for tool {tool_name}"
                                duration = time.time() - start_time
                                return StabilityTestResult(
                                    test_name, False, duration, error
                                )
                        except Exception as e:
                            error = f"Tool info retrieval failed: {e}"
                            duration = time.time() - start_time
                            return StabilityTestResult(
                                test_name, False, duration, error
                            )

            duration = time.time() - start_time
            return StabilityTestResult(test_name, True, duration)

        except Exception as e:
            duration = time.time() - start_time
            error = f"Tool integration test error: {e}"
            return StabilityTestResult(test_name, False, duration, error)

    def generate_stability_report(self) -> str:
        """Generate comprehensive stability report."""
        try:
            if not self.test_results:
                return "No test results available"

            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r.success)
            failed_tests = total_tests - passed_tests

            report = []
            report.append("=" * 60)
            report.append("GUI STABILITY VALIDATION REPORT")
            report.append("=" * 60)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Total Tests: {total_tests}")
            report.append(f"Passed: {passed_tests}")
            report.append(f"Failed: {failed_tests}")
            report.append(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            report.append("")

            # Individual test results
            report.append("INDIVIDUAL TEST RESULTS:")
            report.append("-" * 40)

            for result in self.test_results:
                status = "PASS" if result.success else "FAIL"
                report.append(f"{result.test_name}: {status} ({result.duration:.2f}s)")
                if result.error:
                    report.append(f"  Error: {result.error}")
                report.append("")

            # Recommendations
            report.append("RECOMMENDATIONS:")
            report.append("-" * 40)

            if failed_tests == 0:
                report.append("✅ All tests passed - GUI is stable")
            else:
                report.append("⚠️  Some tests failed - review errors above")
                report.append("• Consider implementing component guardian protection")
                report.append("• Review widget lifecycle management")
                report.append("• Check for memory leaks and resource cleanup")

            return "\n".join(report)

        except Exception as e:
            self.logger.error(f"Error generating stability report: {e}")
            return f"Error generating report: {e}"


def validate_gui_stability(widget: QWidget) -> Dict[str, Any]:
    """
    Convenience function for GUI stability validation.

    Args:
        widget: Widget to validate

    Returns:
        Dict: Validation results
    """
    validator = GUIStabilityValidator()
    return validator.run_comprehensive_stability_test(widget)


def quick_stability_check(widget: QWidget) -> bool:
    """
    Quick stability check for development use.

    Args:
        widget: Widget to check

    Returns:
        bool: True if stable
    """
    try:
        validator = GUIStabilityValidator()
        result = validator.validate_widget_lifecycle(widget, 5)
        return result.success
    except Exception:
        return False
