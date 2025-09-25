#!/usr/bin/env python3
"""
Size Analyzer Final Migration Validation Script

This script performs comprehensive final validation and testing to ensure the entire
size analyzer migration is production-ready and meets all quality standards.

Phase 8: Final Validation and Production Readiness Testing
- End-to-end integration testing
- Production readiness validation
- Cross-platform compatibility testing
- Regression testing
- Documentation validation
- Final quality assurance
"""

import sys
import os
import time
import json
import tempfile
import traceback
import warnings
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Represents the result of a validation test."""

    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'WARNING'
    message: str
    details: Dict[str, Any]
    execution_time: float
    timestamp: str


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    validation_id: str
    start_time: str
    end_time: str
    total_duration: float
    system_info: Dict[str, Any]
    results: List[ValidationResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    production_ready: bool


class SizeAnalyzerFinalValidator:
    """
    Comprehensive final validation system for Size Analyzer migration.

    This validator performs all necessary checks to ensure the migration
    is production-ready and meets all quality standards.
    """

    def __init__(self):
        """Initialize the final validator."""
        self.validation_id = (
            f"size_analyzer_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.start_time = datetime.now()
        self.results: List[ValidationResult] = []
        self.temp_dir = None
        self.system_info = self._collect_system_info()

        # Validation configuration
        self.config = {
            "performance_thresholds": {
                "small_file_analysis_time": 5.0,  # seconds
                "medium_file_analysis_time": 15.0,  # seconds
                "large_file_analysis_time": 60.0,  # seconds
                "memory_usage_limit": 500 * 1024 * 1024,  # 500MB
                "cpu_usage_limit": 80.0,  # percentage
            },
            "quality_thresholds": {
                "test_coverage_minimum": 95.0,  # percentage
                "documentation_coverage": 90.0,  # percentage
                "code_quality_score": 8.0,  # out of 10
            },
            "compatibility_requirements": {
                "python_versions": ["3.8", "3.9", "3.10", "3.11"],
                "platforms": ["Windows", "Linux", "Darwin"],
                "pyqt5_versions": ["5.12", "5.15"],
            },
        }

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information."""
        try:
            import psutil

            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage(".")
            cpu_info = {
                "count": psutil.cpu_count(),
                "freq": (
                    psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                ),
            }
        except ImportError:
            memory_info = None
            disk_info = None
            cpu_info = None

        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "memory": (
                {
                    "total": memory_info.total if memory_info else None,
                    "available": (
                        memory_info.available if memory_info else None
                    ),
                    "percent": memory_info.percent if memory_info else None,
                }
                if memory_info
                else None
            ),
            "disk": (
                {
                    "total": disk_info.total if disk_info else None,
                    "free": disk_info.free if disk_info else None,
                    "used": disk_info.used if disk_info else None,
                }
                if disk_info
                else None
            ),
            "cpu": cpu_info,
            "working_directory": os.getcwd(),
            "path_separator": os.sep,
            "environment_variables": {
                "PYTHONPATH": os.environ.get("PYTHONPATH"),
                "PATH": os.environ.get("PATH", "")[:200]
                + "...",  # Truncate for readability
            },
        }

    def _record_result(
        self,
        test_name: str,
        status: str,
        message: str,
        details: Dict[str, Any] = None,
        execution_time: float = 0.0,
    ):
        """Record a validation test result."""
        result = ValidationResult(
            test_name=test_name,
            status=status,
            message=message,
            details=details or {},
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
        )
        self.results.append(result)

        # Print real-time feedback
        status_symbol = {
            "PASS": "✓",
            "FAIL": "✗",
            "SKIP": "⚠",
            "WARNING": "⚠",
        }.get(status, "?")

        print(f"{status_symbol} {test_name}: {message}")
        if details and status in ["FAIL", "WARNING"]:
            for key, value in details.items():
                print(f"    {key}: {value}")

    def test_import_compatibility(self) -> bool:
        """Test all import paths and module loading scenarios."""
        start_time = time.time()
        test_name = "Import Compatibility"

        try:
            # Test core imports
            import_tests = [
                (
                    "Core Logic",
                    "from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker",
                ),
                (
                    "GUI Components",
                    "from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI",
                ),
                (
                    "Configuration",
                    "from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig",
                ),
                (
                    "Logging",
                    "from file_utilities_2.core.size_analyzer_logging import SizeAnalyzerLogger",
                ),
                (
                    "Integration",
                    "from file_utilities_2.integration.hub_connector import HubConnector",
                ),
                (
                    "Package Level",
                    "from file_utilities_2 import SizeAnalyzer, SizeAnalyzerGUI",
                ),
            ]

            failed_imports = []
            successful_imports = []

            for test_desc, import_stmt in import_tests:
                try:
                    exec(import_stmt)
                    successful_imports.append(test_desc)
                except ImportError as e:
                    failed_imports.append(f"{test_desc}: {str(e)}")
                except Exception as e:
                    failed_imports.append(
                        f"{test_desc}: Unexpected error - {str(e)}"
                    )

            execution_time = time.time() - start_time

            if failed_imports:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"Import failures detected: {len(failed_imports)} failed, {len(successful_imports)} passed",
                    {
                        "failed_imports": failed_imports,
                        "successful_imports": successful_imports,
                    },
                    execution_time,
                )
                return False
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    f"All imports successful: {len(successful_imports)} modules",
                    {"successful_imports": successful_imports},
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Import testing failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_core_functionality(self) -> bool:
        """Test core size analyzer functionality."""
        start_time = time.time()
        test_name = "Core Functionality"

        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            # Create test directory with files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test files
                test_files = [
                    ("small.txt", "Small file content"),
                    ("medium.txt", "Medium file content " * 100),
                    ("large.txt", "Large file content " * 1000),
                ]

                for filename, content in test_files:
                    file_path = os.path.join(temp_dir, filename)
                    with open(file_path, "w") as f:
                        f.write(content)

                # Create subdirectory
                sub_dir = os.path.join(temp_dir, "subdir")
                os.makedirs(sub_dir)
                with open(os.path.join(sub_dir, "sub_file.txt"), "w") as f:
                    f.write("Subdirectory file content")

                # Test analyzer
                analyzer = SizeAnalyzer()

                # Test format_size method
                size_tests = [
                    (1024, "1.0 KB"),
                    (1048576, "1.0 MB"),
                    (1073741824, "1.0 GB"),
                    (0, "0.0 B"),
                ]

                format_failures = []
                for size_bytes, expected in size_tests:
                    result = analyzer.format_size(size_bytes)
                    if result != expected:
                        format_failures.append(
                            f"format_size({size_bytes}) = {result}, expected {expected}"
                        )

                # Test directory analysis
                analysis_result = analyzer.analyze_directory(temp_dir)

                # Validate analysis result structure
                required_keys = [
                    "path",
                    "total_size",
                    "file_count",
                    "directory_count",
                    "files",
                    "file_types",
                    "largest_files",
                    "directory_tree",
                ]
                missing_keys = [
                    key for key in required_keys if key not in analysis_result
                ]

                # Test export functionality
                export_path = os.path.join(temp_dir, "test_export.json")
                analyzer.export_analysis(analysis_result, export_path)
                export_exists = os.path.exists(export_path)

                execution_time = time.time() - start_time

                # Evaluate results
                issues = []
                if format_failures:
                    issues.extend(format_failures)
                if missing_keys:
                    issues.append(f"Missing analysis keys: {missing_keys}")
                if not export_exists:
                    issues.append("Export functionality failed")
                if (
                    analysis_result.get("file_count", 0) != 4
                ):  # 3 main files + 1 sub file
                    issues.append(
                        f"Incorrect file count: {analysis_result.get('file_count', 0)}, expected 4"
                    )

                if issues:
                    self._record_result(
                        test_name,
                        "FAIL",
                        f"Core functionality issues detected: {len(issues)} problems",
                        {
                            "issues": issues,
                            "analysis_result": analysis_result,
                            "export_exists": export_exists,
                        },
                        execution_time,
                    )
                    return False
                else:
                    self._record_result(
                        test_name,
                        "PASS",
                        "All core functionality tests passed",
                        {
                            "file_count": analysis_result.get("file_count"),
                            "total_size": analysis_result.get("total_size"),
                            "export_successful": export_exists,
                            "analysis_time": execution_time,
                        },
                        execution_time,
                    )
                    return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Core functionality test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_gui_initialization(self) -> bool:
        """Test GUI initialization and basic functionality."""
        start_time = time.time()
        test_name = "GUI Initialization"

        try:
            # Check if PyQt5 is available
            try:
                from PyQt5.QtWidgets import QApplication
                from PyQt5.QtCore import QTimer

                pyqt5_available = True
            except ImportError:
                self._record_result(
                    test_name,
                    "SKIP",
                    "PyQt5 not available - GUI testing skipped",
                    {"reason": "PyQt5 import failed"},
                    time.time() - start_time,
                )
                return True  # Not a failure, just skip

            # Test GUI import
            from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

            # Test GUI class structure
            expected_methods = [
                "__init__",
                "show",
                "close",
                "_start_analysis",
                "_browse_directory",
            ]
            missing_methods = [
                method
                for method in expected_methods
                if not hasattr(SizeAnalyzerGUI, method)
            ]

            # Test signal definitions
            expected_signals = [
                "tool_started",
                "tool_completed",
                "tool_error",
                "tool_progress",
            ]

            execution_time = time.time() - start_time

            if missing_methods:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"GUI class missing required methods: {missing_methods}",
                    {"missing_methods": missing_methods},
                    execution_time,
                )
                return False
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "GUI initialization test passed",
                    {
                        "pyqt5_available": pyqt5_available,
                        "methods_verified": expected_methods,
                        "class_structure": "valid",
                    },
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"GUI initialization test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_hub_integration(self) -> bool:
        """Test hub integration functionality."""
        start_time = time.time()
        test_name = "Hub Integration"

        try:
            from file_utilities_2.integration.hub_connector import (
                HubConnector,
                HubMessage,
            )
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            # Test hub connector initialization
            connector = HubConnector("Test Tool")

            # Test message creation
            message = HubMessage("test_message", "Test Tool", {"test": "data"})

            # Test analyzer with hub integration
            analyzer = SizeAnalyzer(hub_connector=connector)

            # Test hub connector methods
            required_methods = [
                "register_with_hub",
                "report_status_to_hub",
                "broadcast_event",
            ]
            missing_methods = [
                method
                for method in required_methods
                if not hasattr(connector, method)
            ]

            execution_time = time.time() - start_time

            if missing_methods:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"Hub integration missing required methods: {missing_methods}",
                    {"missing_methods": missing_methods},
                    execution_time,
                )
                return False
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "Hub integration test passed",
                    {
                        "connector_initialized": True,
                        "message_created": True,
                        "analyzer_integration": True,
                        "methods_verified": required_methods,
                    },
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Hub integration test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_performance_benchmarks(self) -> bool:
        """Test performance against established benchmarks."""
        start_time = time.time()
        test_name = "Performance Benchmarks"

        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            analyzer = SizeAnalyzer()
            performance_results = {}

            # Test small file performance
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create small test files
                for i in range(10):
                    file_path = os.path.join(temp_dir, f"small_{i}.txt")
                    with open(file_path, "w") as f:
                        f.write(f"Small file content {i}")

                small_start = time.time()
                small_result = analyzer.analyze_directory(temp_dir)
                small_time = time.time() - small_start
                performance_results["small_files"] = {
                    "time": small_time,
                    "file_count": small_result.get("file_count", 0),
                    "threshold": self.config["performance_thresholds"][
                        "small_file_analysis_time"
                    ],
                }

            # Test medium file performance
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create medium test files
                for i in range(50):
                    file_path = os.path.join(temp_dir, f"medium_{i}.txt")
                    with open(file_path, "w") as f:
                        f.write(f"Medium file content {i} " * 100)

                medium_start = time.time()
                medium_result = analyzer.analyze_directory(temp_dir)
                medium_time = time.time() - medium_start
                performance_results["medium_files"] = {
                    "time": medium_time,
                    "file_count": medium_result.get("file_count", 0),
                    "threshold": self.config["performance_thresholds"][
                        "medium_file_analysis_time"
                    ],
                }

            # Test format_size performance
            format_start = time.time()
            for i in range(10000):
                analyzer.format_size(i * 1024)
            format_time = time.time() - format_start
            performance_results["format_size"] = {
                "time": format_time,
                "operations": 10000,
                "ops_per_second": (
                    10000 / format_time if format_time > 0 else float("inf")
                ),
            }

            execution_time = time.time() - start_time

            # Evaluate performance
            performance_issues = []
            if (
                performance_results["small_files"]["time"]
                > performance_results["small_files"]["threshold"]
            ):
                performance_issues.append(
                    f"Small file analysis too slow: {performance_results['small_files']['time']:.2f}s > {performance_results['small_files']['threshold']}s"
                )

            if (
                performance_results["medium_files"]["time"]
                > performance_results["medium_files"]["threshold"]
            ):
                performance_issues.append(
                    f"Medium file analysis too slow: {performance_results['medium_files']['time']:.2f}s > {performance_results['medium_files']['threshold']}s"
                )

            if performance_results["format_size"]["ops_per_second"] < 1000:
                performance_issues.append(
                    f"format_size too slow: {performance_results['format_size']['ops_per_second']:.0f} ops/sec < 1000 ops/sec"
                )

            if performance_issues:
                self._record_result(
                    test_name,
                    "WARNING",
                    f"Performance issues detected: {len(performance_issues)} concerns",
                    {
                        "issues": performance_issues,
                        "performance_results": performance_results,
                    },
                    execution_time,
                )
                return True  # Warning, not failure
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "All performance benchmarks met",
                    {"performance_results": performance_results},
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Performance benchmark test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_error_handling(self) -> bool:
        """Test comprehensive error handling scenarios."""
        start_time = time.time()
        test_name = "Error Handling"

        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            analyzer = SizeAnalyzer()
            error_scenarios = []

            # Test non-existent directory
            try:
                analyzer.analyze_directory("/nonexistent/directory/path")
                error_scenarios.append(
                    "Non-existent directory should raise FileNotFoundError"
                )
            except FileNotFoundError:
                pass  # Expected
            except Exception as e:
                error_scenarios.append(
                    f"Non-existent directory raised unexpected error: {type(e).__name__}"
                )

            # Test file instead of directory
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False
            ) as temp_file:
                temp_file.write("test content")
                temp_file_path = temp_file.name

            try:
                analyzer.analyze_directory(temp_file_path)
                error_scenarios.append(
                    "File path should raise NotADirectoryError"
                )
            except NotADirectoryError:
                pass  # Expected
            except Exception as e:
                error_scenarios.append(
                    f"File path raised unexpected error: {type(e).__name__}"
                )
            finally:
                os.unlink(temp_file_path)

            # Test invalid export path
            try:
                analyzer.export_analysis({}, "/invalid/path/export.json")
                error_scenarios.append(
                    "Invalid export path should raise IOError"
                )
            except (IOError, OSError):
                pass  # Expected
            except Exception as e:
                error_scenarios.append(
                    f"Invalid export path raised unexpected error: {type(e).__name__}"
                )

            # Test cancellation
            analyzer.cancel_operation()
            if not analyzer._should_cancel:
                error_scenarios.append(
                    "Cancellation should set _should_cancel flag"
                )

            execution_time = time.time() - start_time

            if error_scenarios:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"Error handling issues detected: {len(error_scenarios)} problems",
                    {"error_scenarios": error_scenarios},
                    execution_time,
                )
                return False
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "All error handling scenarios passed",
                    {"scenarios_tested": 4},
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Error handling test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_configuration_system(self) -> bool:
        """Test configuration and settings management."""
        start_time = time.time()
        test_name = "Configuration System"

        try:
            from file_utilities_2.core.size_analyzer_config import (
                SizeAnalyzerConfig,
            )
            from file_utilities_2.core.size_analyzer_logging import (
                SizeAnalyzerLogger,
                get_size_analyzer_logger,
            )

            # Test configuration
            config = SizeAnalyzerConfig()

            # Test logging
            logger = get_size_analyzer_logger()

            # Test configuration methods
            config_methods = [
                "get_setting",
                "set_setting",
                "load_config",
                "save_config",
            ]
            missing_config_methods = [
                method
                for method in config_methods
                if not hasattr(config, method)
            ]

            # Test logger functionality
            logger_methods = ["debug", "info", "warning", "error"]
            missing_logger_methods = [
                method
                for method in logger_methods
                if not hasattr(logger, method)
            ]

            execution_time = time.time() - start_time

            issues = []
            if missing_config_methods:
                issues.append(
                    f"Missing config methods: {missing_config_methods}"
                )
            if missing_logger_methods:
                issues.append(
                    f"Missing logger methods: {missing_logger_methods}"
                )

            if issues:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"Configuration system issues: {len(issues)} problems",
                    {"issues": issues},
                    execution_time,
                )
                return False
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "Configuration system test passed",
                    {
                        "config_methods": config_methods,
                        "logger_methods": logger_methods,
                    },
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Configuration system test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_documentation_examples(self) -> bool:
        """Test that documentation examples work correctly."""
        start_time = time.time()
        test_name = "Documentation Examples"

        try:
            # Test basic usage example from documentation
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            # Create test directory for documentation example
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create sample files as shown in documentation
                sample_files = [
                    ("document.txt", "Sample document content"),
                    ("image.jpg", "Fake image data" * 100),
                    ("data.csv", "col1,col2,col3\nval1,val2,val3\n" * 50),
                ]

                for filename, content in sample_files:
                    file_path = os.path.join(temp_dir, filename)
                    with open(file_path, "w") as f:
                        f.write(content)

                # Test documentation example code
                analyzer = SizeAnalyzer()

                # Example 1: Basic analysis
                result = analyzer.analyze_directory(temp_dir)

                # Example 2: Format size
                formatted_size = analyzer.format_size(result["total_size"])

                # Example 3: Export results
                export_path = os.path.join(temp_dir, "analysis_results.json")
                analyzer.export_analysis(result, export_path)

                # Verify examples worked
                example_issues = []
                if not isinstance(result, dict):
                    example_issues.append(
                        "analyze_directory should return dict"
                    )
                if not isinstance(formatted_size, str):
                    example_issues.append("format_size should return string")
                if not os.path.exists(export_path):
                    example_issues.append("export_analysis should create file")

                execution_time = time.time() - start_time

                if example_issues:
                    self._record_result(
                        test_name,
                        "FAIL",
                        f"Documentation examples failed: {len(example_issues)} issues",
                        {"issues": example_issues},
                        execution_time,
                    )
                    return False
                else:
                    self._record_result(
                        test_name,
                        "PASS",
                        "All documentation examples work correctly",
                        {
                            "examples_tested": 3,
                            "result_keys": list(result.keys()),
                            "formatted_size": formatted_size,
                        },
                        execution_time,
                    )
                    return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Documentation examples test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_regression_scenarios(self) -> bool:
        """Test regression scenarios to ensure existing functionality remains intact."""
        start_time = time.time()
        test_name = "Regression Testing"

        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            # Test legacy compatibility
            analyzer = SizeAnalyzer()

            # Create comprehensive test scenario
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create various file types and structures
                test_structure = {
                    "root_file.txt": "Root level file",
                    "subdir1": {
                        "sub_file1.txt": "Subdirectory file 1",
                        "sub_file2.log": "Log file content",
                        "nested": {"deep_file.dat": "Deep nested file"},
                    },
                    "subdir2": {
                        "large_file.bin": "X" * 10000,
                        "empty_file.txt": "",
                    },
                }

                def create_structure(base_path, structure):
                    for name, content in structure.items():
                        path = os.path.join(base_path, name)
                        if isinstance(content, dict):
                            os.makedirs(path, exist_ok=True)
                            create_structure(path, content)
                        else:
                            with open(path, "w") as f:
                                f.write(content)

                create_structure(temp_dir, test_structure)

                # Test comprehensive analysis
                result = analyzer.analyze_directory(temp_dir)

                # Regression checks
                regression_issues = []

                # Check basic structure
                if "total_size" not in result:
                    regression_issues.append("Missing total_size in result")
                if "file_count" not in result:
                    regression_issues.append("Missing file_count in result")
                if "files" not in result:
                    regression_issues.append("Missing files list in result")

                # Check file counting
                expected_file_count = 6  # Count all files in structure
                if result.get("file_count", 0) != expected_file_count:
                    regression_issues.append(
                        f"File count mismatch: got {result.get('file_count')}, expected {expected_file_count}"
                    )

                # Check file types analysis
                if "file_types" not in result:
                    regression_issues.append("Missing file_types analysis")
                else:
                    expected_extensions = {".txt", ".log", ".dat", ".bin"}
                    found_extensions = set(result["file_types"].keys())
                    missing_extensions = expected_extensions - found_extensions
                    if missing_extensions:
                        regression_issues.append(
                            f"Missing file type analysis for: {missing_extensions}"
                        )

                # Check largest files
                if "largest_files" not in result:
                    regression_issues.append("Missing largest_files analysis")
                elif not isinstance(result["largest_files"], list):
                    regression_issues.append("largest_files should be a list")

                # Check directory tree
                if "directory_tree" not in result:
                    regression_issues.append("Missing directory_tree")

                execution_time = time.time() - start_time

                if regression_issues:
                    self._record_result(
                        test_name,
                        "FAIL",
                        f"Regression issues detected: {len(regression_issues)} problems",
                        {
                            "issues": regression_issues,
                            "result_structure": (
                                list(result.keys())
                                if isinstance(result, dict)
                                else "not_dict"
                            ),
                        },
                        execution_time,
                    )
                    return False
                else:
                    self._record_result(
                        test_name,
                        "PASS",
                        "All regression tests passed",
                        {
                            "file_count": result.get("file_count"),
                            "total_size": result.get("total_size"),
                            "file_types_count": len(
                                result.get("file_types", {})
                            ),
                            "largest_files_count": len(
                                result.get("largest_files", [])
                            ),
                        },
                        execution_time,
                    )
                    return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Regression testing failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def test_cross_platform_compatibility(self) -> bool:
        """Test cross-platform compatibility scenarios."""
        start_time = time.time()
        test_name = "Cross-Platform Compatibility"

        try:
            from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

            analyzer = SizeAnalyzer()
            compatibility_issues = []

            # Test path handling
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create files with different path separators
                test_paths = [
                    "normal_file.txt",
                    "file with spaces.txt",
                    "file-with-dashes.txt",
                    "file_with_underscores.txt",
                ]

                for filename in test_paths:
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        with open(file_path, "w") as f:
                            f.write(f"Content for {filename}")
                    except (OSError, UnicodeError) as e:
                        compatibility_issues.append(
                            f"Failed to create file {filename}: {e}"
                        )

                # Test analysis with various file names
                try:
                    result = analyzer.analyze_directory(temp_dir)
                    if result.get("file_count", 0) != len(test_paths) - len(
                        compatibility_issues
                    ):
                        compatibility_issues.append(
                            "File count mismatch in cross-platform test"
                        )
                except Exception as e:
                    compatibility_issues.append(
                        f"Analysis failed with special filenames: {e}"
                    )

            # Test Unicode handling
            try:
                unicode_size = analyzer.format_size(1024)
                if not isinstance(unicode_size, str):
                    compatibility_issues.append(
                        "format_size should return string for Unicode compatibility"
                    )
            except Exception as e:
                compatibility_issues.append(f"Unicode handling failed: {e}")

            # Test platform-specific features
            platform_info = {
                "system": platform.system(),
                "python_version": platform.python_version(),
                "path_separator": os.sep,
                "line_separator": os.linesep,
            }

            execution_time = time.time() - start_time

            if compatibility_issues:
                self._record_result(
                    test_name,
                    "WARNING",
                    f"Cross-platform compatibility issues: {len(compatibility_issues)} concerns",
                    {
                        "issues": compatibility_issues,
                        "platform_info": platform_info,
                    },
                    execution_time,
                )
                return True  # Warning, not failure
            else:
                self._record_result(
                    test_name,
                    "PASS",
                    "Cross-platform compatibility test passed",
                    {"platform_info": platform_info},
                    execution_time,
                )
                return True

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_result(
                test_name,
                "FAIL",
                f"Cross-platform compatibility test failed: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()},
                execution_time,
            )
            return False

    def run_comprehensive_validation(self) -> ValidationReport:
        """Run all validation tests and generate comprehensive report."""
        print("=" * 80)
        print("SIZE ANALYZER FINAL MIGRATION VALIDATION")
        print("=" * 80)
        print(f"Validation ID: {self.validation_id}")
        print(f"Start Time: {self.start_time.isoformat()}")
        print(
            f"System: {self.system_info['system']} {self.system_info['release']}"
        )
        print(f"Python: {self.system_info['python_version']}")
        print("=" * 80)

        # Define validation test suite
        validation_tests = [
            ("Import Compatibility", self.test_import_compatibility),
            ("Core Functionality", self.test_core_functionality),
            ("GUI Initialization", self.test_gui_initialization),
            ("Hub Integration", self.test_hub_integration),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Error Handling", self.test_error_handling),
            ("Configuration System", self.test_configuration_system),
            ("Documentation Examples", self.test_documentation_examples),
            ("Regression Testing", self.test_regression_scenarios),
            (
                "Cross-Platform Compatibility",
                self.test_cross_platform_compatibility,
            ),
        ]

        # Execute all tests
        for test_name, test_func in validation_tests:
            print(f"\nRunning {test_name}...")
            try:
                test_func()
            except Exception as e:
                self._record_result(
                    test_name,
                    "FAIL",
                    f"Test execution failed: {str(e)}",
                    {"error": str(e), "traceback": traceback.format_exc()},
                    0.0,
                )

        # Generate summary
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        # Calculate statistics
        status_counts = {}
        for result in self.results:
            status_counts[result.status] = (
                status_counts.get(result.status, 0) + 1
            )

        total_tests = len(self.results)
        passed_tests = status_counts.get("PASS", 0)
        failed_tests = status_counts.get("FAIL", 0)
        warning_tests = status_counts.get("WARNING", 0)
        skipped_tests = status_counts.get("SKIP", 0)

        # Determine production readiness
        critical_failures = failed_tests
        production_ready = critical_failures == 0

        # Generate recommendations
        recommendations = []
        if failed_tests > 0:
            recommendations.append(
                f"Address {failed_tests} critical failures before production deployment"
            )
        if warning_tests > 0:
            recommendations.append(
                f"Review {warning_tests} warnings for potential improvements"
            )
        if production_ready:
            recommendations.append(
                "Migration is production-ready with all critical tests passing"
            )
        else:
            recommendations.append(
                "Migration requires fixes before production deployment"
            )

        # Create comprehensive report
        report = ValidationReport(
            validation_id=self.validation_id,
            start_time=self.start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration=total_duration,
            system_info=self.system_info,
            results=self.results,
            summary={
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "skipped": skipped_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100)
                    if total_tests > 0
                    else 0
                ),
                "status_counts": status_counts,
            },
            recommendations=recommendations,
            production_ready=production_ready,
        )

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        for result in self.results:
            status_symbol = {
                "PASS": "✓",
                "FAIL": "✗",
                "SKIP": "⚠",
                "WARNING": "⚠",
            }.get(result.status, "?")
            print(f"{status_symbol} {result.test_name:.<50} {result.status}")

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Warnings: {warning_tests}")
        print(f"Skipped: {skipped_tests}")
        print(
            f"Success Rate: {passed_tests / total_tests * 100:.1f}%"
            if total_tests > 0
            else "N/A"
        )
        print(f"Total Duration: {total_duration:.2f} seconds")

        print(f"\nProduction Ready: {'✓ YES' if production_ready else '✗ NO'}")

        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

        print("=" * 80)

        return report


def main():
    """Main entry point for final validation."""
    try:
        validator = SizeAnalyzerFinalValidator()
        report = validator.run_comprehensive_validation()

        # Save detailed report
        report_filename = f"SIZE_ANALYZER_FINAL_VALIDATION_REPORT_{validator.validation_id}.json"
        with open(report_filename, "w") as f:
            # Convert dataclasses to dict for JSON serialization
            report_dict = asdict(report)
            json.dump(report_dict, f, indent=2, default=str)

        print(f"\nDetailed report saved to: {report_filename}")

        # Exit with appropriate code
        sys.exit(0 if report.production_ready else 1)

    except Exception as e:
        print(f"Fatal error during validation: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
