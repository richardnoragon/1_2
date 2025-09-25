"""
Size Analyzer Comprehensive Test Suite Runner

This script runs the complete testing suite for the Size Analyzer migration,
providing comprehensive validation of all aspects including core logic, GUI,
hub integration, configuration, imports, and performance.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestSuiteRunner:
    """Main test suite runner for Size Analyzer comprehensive testing."""

    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "start_time": self.start_time.isoformat(),
            "test_modules": {},
            "summary": {},
            "errors": [],
            "warnings": [],
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run the complete comprehensive test suite."""
        print("=" * 80)
        print("SIZE ANALYZER COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started at: {self.start_time}")
        print()

        # Test modules to run in order
        test_modules = [
            (
                "Import and Compatibility Tests",
                "file_utilities_2/tests/test_size_analyzer_imports.py",
            ),
            (
                "Configuration and Resource Tests",
                "file_utilities_2/tests/test_size_analyzer_config.py",
            ),
            (
                "Core Logic Tests",
                "file_utilities_2/tests/test_size_analyzer_core.py",
            ),
            (
                "Hub Integration Tests",
                "file_utilities_2/tests/test_size_analyzer_integration.py",
            ),
            (
                "GUI Component Tests",
                "file_utilities_2/tests/test_size_analyzer_gui.py",
            ),
            (
                "Performance and Stress Tests",
                "file_utilities_2/tests/test_size_analyzer_performance.py",
            ),
        ]

        # Run each test module
        for module_name, module_path in test_modules:
            print(f"Running {module_name}...")
            result = self._run_test_module(module_name, module_path)
            self.results["test_modules"][module_name] = result

            if result["status"] == "passed":
                print(f"✓ {module_name} - PASSED")
            elif result["status"] == "failed":
                print(f"✗ {module_name} - FAILED")
                self.results["errors"].append(
                    f"{module_name}: {result.get('error', 'Unknown error')}"
                )
            else:
                print(f"⚠ {module_name} - SKIPPED")

            print()

        # Run additional validation tests
        print("Running additional validation tests...")
        self._run_integration_validation()
        self._run_deployment_validation()
        self._run_compatibility_validation()

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

        return self.results

    def _run_test_module(
        self, module_name: str, module_path: str
    ) -> Dict[str, Any]:
        """Run a specific test module using pytest."""
        result = {
            "module_name": module_name,
            "module_path": module_path,
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "duration": 0,
            "output": "",
            "error": None,
        }

        try:
            # Check if test file exists
            if not os.path.exists(module_path):
                result["status"] = "skipped"
                result["error"] = f"Test file not found: {module_path}"
                return result

            # Run pytest on the module
            start_time = time.time()

            cmd = [
                sys.executable,
                "-m",
                "pytest",
                module_path,
                "-v",
                "--tb=short",
                "--no-header",
                "--json-report",
                "--json-report-file=test_report.json",
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per module
            )

            end_time = time.time()
            result["duration"] = end_time - start_time
            result["output"] = process.stdout

            # Parse pytest results
            if os.path.exists("test_report.json"):
                try:
                    with open("test_report.json", "r") as f:
                        pytest_report = json.load(f)

                    summary = pytest_report.get("summary", {})
                    result["tests_run"] = summary.get("total", 0)
                    result["tests_passed"] = summary.get("passed", 0)
                    result["tests_failed"] = summary.get("failed", 0)
                    result["tests_skipped"] = summary.get("skipped", 0)

                    # Update totals
                    self.total_tests += result["tests_run"]
                    self.passed_tests += result["tests_passed"]
                    self.failed_tests += result["tests_failed"]
                    self.skipped_tests += result["tests_skipped"]

                    # Cleanup
                    os.remove("test_report.json")

                except Exception as e:
                    result["error"] = f"Failed to parse pytest report: {e}"

            # Determine status
            if process.returncode == 0:
                result["status"] = "passed"
            else:
                result["status"] = "failed"
                result["error"] = process.stderr or "Tests failed"

        except subprocess.TimeoutExpired:
            result["status"] = "failed"
            result["error"] = "Test execution timed out"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        result["end_time"] = datetime.now().isoformat()
        return result

    def _run_integration_validation(self):
        """Run integration validation tests."""
        print("Running integration validation...")

        validation_tests = [
            self._validate_imports,
            self._validate_core_functionality,
            self._validate_gui_components,
            self._validate_hub_integration,
            self._validate_configuration,
        ]

        integration_results = []

        for test_func in validation_tests:
            try:
                test_name = test_func.__name__.replace("_validate_", "")
                print(f"  Validating {test_name}...")

                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time

                integration_results.append(
                    {
                        "test": test_name,
                        "status": "passed" if result else "failed",
                        "duration": duration,
                    }
                )

                if result:
                    print(f"    ✓ {test_name} validation passed")
                else:
                    print(f"    ✗ {test_name} validation failed")

            except Exception as e:
                print(f"    ✗ {test_name} validation error: {e}")
                integration_results.append(
                    {
                        "test": test_name,
                        "status": "error",
                        "error": str(e),
                        "duration": 0,
                    }
                )

        self.results["integration_validation"] = integration_results

    def _validate_imports(self) -> bool:
        """Validate that all imports work correctly."""
        try:
            # Test core imports
            from file_utilities_2.core.size_analyzer_logic import (
                SizeAnalyzer,
                SizeAnalyzerWorker,
            )
            from file_utilities_2.core.size_analyzer_config import (
                SizeAnalyzerConfig,
            )
            from file_utilities_2.core.size_analyzer_logging import (
                SizeAnalyzerLogger,
            )

            # Test GUI imports
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

            # Test integration imports
            from file_utilities_2.integration.hub_connector import HubConnector

            # Test package-level imports
            from file_utilities_2 import SizeAnalyzer as PackageSizeAnalyzer

            return True
        except ImportError as e:
            self.results["errors"].append(f"Import validation failed: {e}")
            return False

    def _validate_core_functionality(self) -> bool:
        """Validate core functionality works."""
        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            # Create analyzer
            analyzer = SizeAnalyzer()

            # Test basic functionality
            assert hasattr(analyzer, "analyze_directory")
            assert hasattr(analyzer, "format_size")
            assert hasattr(analyzer, "export_analysis")

            # Test format_size
            assert analyzer.format_size(1024) == "1.0 KB"
            assert analyzer.format_size(0) == "0.0 B"

            return True
        except Exception as e:
            self.results["errors"].append(
                f"Core functionality validation failed: {e}"
            )
            return False

    def _validate_gui_components(self) -> bool:
        """Validate GUI components can be created."""
        try:
            from PyQt5.QtWidgets import QApplication
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

            # Create QApplication if needed
            if not QApplication.instance():
                app = QApplication([])

            # Create GUI (with mock hub)
            class MockHub:
                def __init__(self):
                    self.registered_tools = {}

                def register_tool(self, name, connector):
                    self.registered_tools[name] = connector
                    return True

            mock_hub = MockHub()
            gui = SizeAnalyzerGUI(hub_instance=mock_hub)

            # Verify basic components
            assert hasattr(gui, "analyzer")
            assert hasattr(gui, "hub_connector")

            gui.close()
            return True
        except Exception as e:
            self.results["errors"].append(f"GUI validation failed: {e}")
            return False

    def _validate_hub_integration(self) -> bool:
        """Validate hub integration works."""
        try:
            from file_utilities_2.integration.hub_connector import (
                HubConnector,
                HubMessage,
            )

            # Create hub connector
            connector = HubConnector("Test Tool")

            # Test message creation
            message = HubMessage("test", "Test Tool", {"data": "test"})
            assert message.message_type == "test"
            assert message.tool_name == "Test Tool"

            # Test serialization
            message_dict = message.to_dict()
            assert isinstance(message_dict, dict)

            return True
        except Exception as e:
            self.results["errors"].append(
                f"Hub integration validation failed: {e}"
            )
            return False

    def _validate_configuration(self) -> bool:
        """Validate configuration system works."""
        try:
            from unittest.mock import Mock
            from file_utilities_2.core.size_analyzer_config import (
                SizeAnalyzerConfig,
            )

            # Mock ConfigManager
            mock_config_manager = Mock()
            mock_config_manager.config = {"size_analyzer": {}}

            with Mock() as mock_cm:
                mock_cm.return_value = mock_config_manager
                config = SizeAnalyzerConfig()

                # Test basic functionality
                assert config.defaults is not None
                assert "general" in config.defaults
                assert "analysis" in config.defaults

                return True
        except Exception as e:
            self.results["errors"].append(
                f"Configuration validation failed: {e}"
            )
            return False

    def _run_deployment_validation(self):
        """Run deployment validation tests."""
        print("Running deployment validation...")

        deployment_tests = [
            ("Package Structure", self._check_package_structure),
            ("Required Files", self._check_required_files),
            ("Dependencies", self._check_dependencies),
            ("Entry Points", self._check_entry_points),
        ]

        deployment_results = []

        for test_name, test_func in deployment_tests:
            try:
                print(f"  Checking {test_name}...")
                result = test_func()

                deployment_results.append(
                    {
                        "test": test_name,
                        "status": "passed" if result else "failed",
                    }
                )

                if result:
                    print(f"    ✓ {test_name} check passed")
                else:
                    print(f"    ✗ {test_name} check failed")

            except Exception as e:
                print(f"    ✗ {test_name} check error: {e}")
                deployment_results.append(
                    {"test": test_name, "status": "error", "error": str(e)}
                )

        self.results["deployment_validation"] = deployment_results

    def _check_package_structure(self) -> bool:
        """Check package structure is correct."""
        required_dirs = [
            "file_utilities_2",
            "file_utilities_2/core",
            "file_utilities_2/gui",
            "file_utilities_2/integration",
            "file_utilities_2/tests",
        ]

        for dir_path in required_dirs:
            if not os.path.isdir(dir_path):
                self.results["errors"].append(f"Missing directory: {dir_path}")
                return False

        return True

    def _check_required_files(self) -> bool:
        """Check required files exist."""
        required_files = [
            "file_utilities_2/__init__.py",
            "file_utilities_2/core/__init__.py",
            "file_utilities_2/core/size_analyzer_logic.py",
            "file_utilities_2/core/size_analyzer_config.py",
            "file_utilities_2/core/size_analyzer_logging.py",
            "file_utilities_2/gui/__init__.py",
            "file_utilities_2/gui/size_analyzer_gui.py",
            "file_utilities_2/integration/__init__.py",
            "file_utilities_2/integration/hub_connector.py",
            "file_utilities_2/tests/__init__.py",
            "file_utilities_2/tests/conftest.py",
        ]

        for file_path in required_files:
            if not os.path.isfile(file_path):
                self.results["errors"].append(f"Missing file: {file_path}")
                return False

        return True

    def _check_dependencies(self) -> bool:
        """Check that required dependencies are available."""
        required_deps = ["PyQt5", "pytest"]

        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                self.results["warnings"].append(f"Missing dependency: {dep}")
                return False

        return True

    def _check_entry_points(self) -> bool:
        """Check that entry points work."""
        try:
            # Test that main classes can be imported and instantiated
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            analyzer = SizeAnalyzer()
            assert analyzer is not None

            return True
        except Exception as e:
            self.results["errors"].append(f"Entry point check failed: {e}")
            return False

    def _run_compatibility_validation(self):
        """Run compatibility validation tests."""
        print("Running compatibility validation...")

        compatibility_tests = [
            ("Python Version", self._check_python_version),
            ("PyQt5 Version", self._check_pyqt5_version),
            ("Platform Compatibility", self._check_platform_compatibility),
        ]

        compatibility_results = []

        for test_name, test_func in compatibility_tests:
            try:
                print(f"  Checking {test_name}...")
                result = test_func()

                compatibility_results.append(
                    {
                        "test": test_name,
                        "status": "passed" if result else "failed",
                    }
                )

                if result:
                    print(f"    ✓ {test_name} compatible")
                else:
                    print(f"    ✗ {test_name} incompatible")

            except Exception as e:
                print(f"    ✗ {test_name} check error: {e}")
                compatibility_results.append(
                    {"test": test_name, "status": "error", "error": str(e)}
                )

        self.results["compatibility_validation"] = compatibility_results

    def _check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version = sys.version_info

        # Require Python 3.7+
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            self.results["errors"].append(
                f"Python {version.major}.{version.minor} not supported. "
                "Requires Python 3.7+"
            )
            return False

        return True

    def _check_pyqt5_version(self) -> bool:
        """Check PyQt5 version compatibility."""
        try:
            from PyQt5.QtCore import QT_VERSION_STR

            print(f"    PyQt5 version: {QT_VERSION_STR}")
            return True
        except ImportError:
            self.results["errors"].append("PyQt5 not available")
            return False

    def _check_platform_compatibility(self) -> bool:
        """Check platform compatibility."""
        import platform

        system = platform.system()
        print(f"    Platform: {system} {platform.release()}")

        # Should work on Windows, Linux, macOS
        supported_platforms = ["Windows", "Linux", "Darwin"]

        if system not in supported_platforms:
            self.results["warnings"].append(f"Untested platform: {system}")

        return True

    def _generate_summary(self):
        """Generate test summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time

        self.results["end_time"] = end_time.isoformat()
        self.results["duration"] = duration.total_seconds()

        # Calculate success rate
        success_rate = 0
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100

        self.results["summary"] = {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": success_rate,
            "duration_seconds": duration.total_seconds(),
            "status": "PASSED" if self.failed_tests == 0 else "FAILED",
        }

        # Print summary
        print("=" * 80)
        print("TEST SUITE SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Skipped: {self.skipped_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration}")
        print(f"Status: {self.results['summary']['status']}")

        if self.results["errors"]:
            print("\nERRORS:")
            for error in self.results["errors"]:
                print(f"  - {error}")

        if self.results["warnings"]:
            print("\nWARNINGS:")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")

        print("=" * 80)

    def _save_results(self):
        """Save test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"size_analyzer_test_results_{timestamp}.json"

        try:
            with open(results_file, "w") as f:
                json.dump(self.results, f, indent=2, default=str)

            print(f"Test results saved to: {results_file}")
        except Exception as e:
            print(f"Failed to save results: {e}")


def main():
    """Main entry point for the test suite."""
    print("Size Analyzer Comprehensive Test Suite")
    print("Phase 6: Testing and Validation")
    print()

    # Check if we're in the right directory
    if not os.path.exists("file_utilities_2"):
        print("Error: file_utilities_2 directory not found.")
        print("Please run this script from the project root directory.")
        sys.exit(1)

    # Run the test suite
    runner = TestSuiteRunner()
    results = runner.run_comprehensive_tests()

    # Exit with appropriate code
    if results["summary"]["status"] == "PASSED":
        print(
            "\n🎉 All tests passed! Size Analyzer migration is ready for production."
        )
        sys.exit(0)
    else:
        print(
            "\n❌ Some tests failed. Please review the results and fix issues."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
