#!/usr/bin/env python3
"""Network Connectivity Toolkit Deployment Validation Script.

This script performs comprehensive validation of the Network Connectivity Toolkit
deployment to ensure production readiness.
"""

import os
import sys
import subprocess
import platform
import importlib
import json
import yaml
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import argparse
import logging
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Represents the result of a validation test."""

    test_name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    duration: float = 0.0
    category: str = "general"


class NetworkConnectivityValidator:
    """Comprehensive validation for Network Connectivity Toolkit deployment."""

    def __init__(
        self, install_dir: Optional[str] = None, verbose: bool = False
    ):
        """Initialize validator.

        Args:
            install_dir: Installation directory to validate
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.setup_logging()

        # Determine installation directory
        if install_dir:
            self.install_dir = Path(install_dir).resolve()
        else:
            self.install_dir = self._detect_install_dir()

        # Validation results
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now()

        self.logger.info(f"Network Connectivity Validator initialized")
        self.logger.info(f"Installation directory: {self.install_dir}")
        self.logger.info(f"System: {platform.system()} {platform.version()}")

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("network_connectivity_validation.log"),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _detect_install_dir(self) -> Path:
        """Detect installation directory."""
        # Try common installation locations
        possible_dirs = [
            Path.cwd() / "network_connectivity",
            Path("/opt/network-connectivity"),
            Path.home() / ".local/share/network-connectivity",
            (
                Path("C:/Program Files/NetworkConnectivity")
                if platform.system() == "Windows"
                else None
            ),
            (
                Path.home() / "Applications/NetworkConnectivity"
                if platform.system() == "Darwin"
                else None
            ),
        ]

        for dir_path in possible_dirs:
            if (
                dir_path
                and dir_path.exists()
                and (dir_path / "__init__.py").exists()
            ):
                return dir_path

        # Default to current directory
        return Path.cwd() / "network_connectivity"

    def _run_test(
        self, test_name: str, test_func, category: str = "general"
    ) -> ValidationResult:
        """Run a validation test and record results.

        Args:
            test_name: Name of the test
            test_func: Function to execute for the test
            category: Test category

        Returns:
            ValidationResult object
        """
        self.logger.info(f"Running test: {test_name}")
        start_time = time.time()

        try:
            success, message, details = test_func()
            duration = time.time() - start_time

            result = ValidationResult(
                test_name=test_name,
                success=success,
                message=message,
                details=details,
                duration=duration,
                category=category,
            )

            if success:
                self.logger.info(f"✓ {test_name}: {message}")
            else:
                self.logger.error(f"✗ {test_name}: {message}")

        except Exception as e:
            duration = time.time() - start_time
            result = ValidationResult(
                test_name=test_name,
                success=False,
                message=f"Test failed with exception: {str(e)}",
                details={"exception": str(e), "type": type(e).__name__},
                duration=duration,
                category=category,
            )
            self.logger.error(f"✗ {test_name}: Exception - {str(e)}")

        self.results.append(result)
        return result

    def validate_file_structure(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate installation file structure."""
        required_dirs = ["core", "tools", "gui", "config", "docs"]

        required_files = [
            "__init__.py",
            "core/__init__.py",
            "tools/__init__.py",
            "gui/__init__.py",
        ]

        missing_dirs = []
        missing_files = []

        # Check directories
        for dir_name in required_dirs:
            dir_path = self.install_dir / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        # Check files
        for file_name in required_files:
            file_path = self.install_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        success = len(missing_dirs) == 0 and len(missing_files) == 0

        if success:
            message = "All required files and directories present"
        else:
            message = f"Missing {len(missing_dirs)} directories and {len(missing_files)} files"

        details = {
            "missing_directories": missing_dirs,
            "missing_files": missing_files,
            "install_directory": str(self.install_dir),
        }

        return success, message, details

    def validate_dependencies(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate Python dependencies."""
        required_packages = [
            "PyQt6",
            "psutil",
            "PyYAML",
            "cryptography",
            "requests",
        ]

        missing_packages = []
        package_versions = {}

        for package in required_packages:
            try:
                module = importlib.import_module(
                    package.lower().replace("-", "_")
                )
                version = getattr(module, "__version__", "unknown")
                package_versions[package] = version
            except ImportError:
                missing_packages.append(package)

        success = len(missing_packages) == 0

        if success:
            message = (
                f"All {len(required_packages)} required packages available"
            )
        else:
            message = f"Missing {len(missing_packages)} required packages"

        details = {
            "missing_packages": missing_packages,
            "package_versions": package_versions,
            "python_version": platform.python_version(),
        }

        return success, message, details

    def validate_imports(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate that all modules can be imported."""
        # Add installation directory to Python path
        if str(self.install_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.install_dir.parent))

        modules_to_test = [
            "network_connectivity",
            "network_connectivity.core.network_base",
            "network_connectivity.core.platform_network",
            "network_connectivity.tools.bandwidth_monitor",
            "network_connectivity.tools.port_scanner",
            "network_connectivity.tools.wifi_analyzer",
            "network_connectivity.tools.lan_file_transfer",
            "network_connectivity.gui.hub",
        ]

        import_results = {}
        failed_imports = []

        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                import_results[module_name] = {
                    "success": True,
                    "version": getattr(module, "__version__", "unknown"),
                }
            except Exception as e:
                import_results[module_name] = {
                    "success": False,
                    "error": str(e),
                }
                failed_imports.append(module_name)

        success = len(failed_imports) == 0

        if success:
            message = (
                f"All {len(modules_to_test)} modules imported successfully"
            )
        else:
            message = f"Failed to import {len(failed_imports)} modules"

        details = {
            "import_results": import_results,
            "failed_imports": failed_imports,
        }

        return success, message, details

    def validate_configuration(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate configuration files."""
        config_dir = self.install_dir / "config"

        if not config_dir.exists():
            return (
                False,
                "Configuration directory not found",
                {"config_dir": str(config_dir)},
            )

        config_files = ["default_settings.py", "tool_profiles.py"]

        yaml_files = list(config_dir.glob("*.yaml")) + list(
            config_dir.glob("*.yml")
        )

        config_status = {}
        errors = []

        # Check Python config files
        for config_file in config_files:
            file_path = config_dir / config_file
            if file_path.exists():
                try:
                    # Try to compile the Python file
                    with open(file_path, "r") as f:
                        compile(f.read(), str(file_path), "exec")
                    config_status[config_file] = "valid"
                except SyntaxError as e:
                    config_status[config_file] = f"syntax_error: {e}"
                    errors.append(f"{config_file}: {e}")
            else:
                config_status[config_file] = "missing"
                errors.append(f"{config_file}: file not found")

        # Check YAML config files
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    yaml.safe_load(f)
                config_status[yaml_file.name] = "valid"
            except yaml.YAMLError as e:
                config_status[yaml_file.name] = f"yaml_error: {e}"
                errors.append(f"{yaml_file.name}: {e}")

        success = len(errors) == 0

        if success:
            message = f"Configuration validation successful ({len(config_status)} files checked)"
        else:
            message = f"Configuration validation failed ({len(errors)} errors)"

        details = {
            "config_status": config_status,
            "errors": errors,
            "config_directory": str(config_dir),
        }

        return success, message, details

    def validate_tools_initialization(
        self,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate that network tools can be initialized."""
        # Add installation directory to Python path
        if str(self.install_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.install_dir.parent))

        tools_to_test = [
            (
                "BandwidthMonitor",
                "network_connectivity.tools.bandwidth_monitor",
            ),
            ("PortScanner", "network_connectivity.tools.port_scanner"),
            ("WiFiAnalyzer", "network_connectivity.tools.wifi_analyzer"),
            (
                "LANFileTransfer",
                "network_connectivity.tools.lan_file_transfer",
            ),
        ]

        tool_results = {}
        failed_tools = []

        for tool_name, module_name in tools_to_test:
            try:
                module = importlib.import_module(module_name)
                tool_class = getattr(module, tool_name)

                # Try to create instance (with mocked dependencies if needed)
                tool_instance = tool_class()

                tool_results[tool_name] = {
                    "success": True,
                    "class_name": tool_class.__name__,
                    "module": module_name,
                }

                # Clean up
                if hasattr(tool_instance, "cleanup"):
                    tool_instance.cleanup()

            except Exception as e:
                tool_results[tool_name] = {
                    "success": False,
                    "error": str(e),
                    "module": module_name,
                }
                failed_tools.append(tool_name)

        success = len(failed_tools) == 0

        if success:
            message = (
                f"All {len(tools_to_test)} tools initialized successfully"
            )
        else:
            message = f"Failed to initialize {len(failed_tools)} tools"

        details = {"tool_results": tool_results, "failed_tools": failed_tools}

        return success, message, details

    def validate_gui_components(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate GUI components (if display available)."""
        try:
            # Check if display is available
            if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
                return (
                    True,
                    "GUI validation skipped (no display available)",
                    {"skipped": True},
                )

            # Add installation directory to Python path
            if str(self.install_dir.parent) not in sys.path:
                sys.path.insert(0, str(self.install_dir.parent))

            # Try to import PyQt6
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer

            # Create QApplication instance
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            gui_components = [
                ("NetworkConnectivityHub", "network_connectivity.gui.hub"),
                (
                    "BandwidthMonitorWidget",
                    "network_connectivity.gui.widgets.bandwidth_monitor_widget",
                ),
            ]

            component_results = {}
            failed_components = []

            for component_name, module_name in gui_components:
                try:
                    module = importlib.import_module(module_name)
                    component_class = getattr(module, component_name)

                    component_results[component_name] = {
                        "success": True,
                        "class_name": component_class.__name__,
                        "module": module_name,
                    }

                except Exception as e:
                    component_results[component_name] = {
                        "success": False,
                        "error": str(e),
                        "module": module_name,
                    }
                    failed_components.append(component_name)

            success = len(failed_components) == 0

            if success:
                message = f"GUI components validation successful ({len(gui_components)} components)"
            else:
                message = f"GUI validation failed ({len(failed_components)} components)"

            details = {
                "component_results": component_results,
                "failed_components": failed_components,
                "qt_version": getattr(
                    __import__("PyQt6.QtCore"), "QT_VERSION_STR", "unknown"
                ),
            }

            return success, message, details

        except ImportError as e:
            return (
                False,
                f"GUI validation failed: PyQt6 not available - {e}",
                {"error": str(e)},
            )
        except Exception as e:
            return False, f"GUI validation failed: {e}", {"error": str(e)}

    def validate_network_operations(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate basic network operations."""
        # Add installation directory to Python path
        if str(self.install_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.install_dir.parent))

        network_tests = {}
        errors = []

        try:
            # Test platform network detection
            from network_connectivity.core.platform_network import (
                PlatformNetworkDetector,
            )

            detector = PlatformNetworkDetector()
            interfaces = detector.get_network_interfaces()

            network_tests["interface_detection"] = {
                "success": True,
                "interface_count": len(interfaces),
                "interfaces": [
                    iface.name for iface in interfaces[:5]
                ],  # First 5 only
            }

        except Exception as e:
            network_tests["interface_detection"] = {
                "success": False,
                "error": str(e),
            }
            errors.append(f"Interface detection: {e}")

        try:
            # Test basic connectivity
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=5)
            network_tests["internet_connectivity"] = {
                "success": True,
                "message": "Internet connectivity confirmed",
            }

        except Exception as e:
            network_tests["internet_connectivity"] = {
                "success": False,
                "error": str(e),
            }
            errors.append(f"Internet connectivity: {e}")

        success = len(errors) == 0

        if success:
            message = "Network operations validation successful"
        else:
            message = f"Network validation failed ({len(errors)} errors)"

        details = {"network_tests": network_tests, "errors": errors}

        return success, message, details

    def validate_security_features(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate security features."""
        security_tests = {}
        errors = []

        try:
            # Test cryptography
            from cryptography.fernet import Fernet

            key = Fernet.generate_key()
            cipher = Fernet(key)
            test_data = b"test encryption data"
            encrypted = cipher.encrypt(test_data)
            decrypted = cipher.decrypt(encrypted)

            security_tests["encryption"] = {
                "success": test_data == decrypted,
                "algorithm": "Fernet (AES 128)",
            }

        except Exception as e:
            security_tests["encryption"] = {"success": False, "error": str(e)}
            errors.append(f"Encryption test: {e}")

        try:
            # Test SSL/TLS
            import ssl

            context = ssl.create_default_context()
            security_tests["ssl_context"] = {
                "success": True,
                "protocol": context.protocol.name,
                "verify_mode": context.verify_mode.name,
            }

        except Exception as e:
            security_tests["ssl_context"] = {"success": False, "error": str(e)}
            errors.append(f"SSL context: {e}")

        success = len(errors) == 0

        if success:
            message = "Security features validation successful"
        else:
            message = f"Security validation failed ({len(errors)} errors)"

        details = {"security_tests": security_tests, "errors": errors}

        return success, message, details

    def validate_performance(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate performance characteristics."""
        performance_tests = {}

        # Test import time
        start_time = time.time()
        try:
            if str(self.install_dir.parent) not in sys.path:
                sys.path.insert(0, str(self.install_dir.parent))
            import network_connectivity

            import_time = time.time() - start_time

            performance_tests["import_time"] = {
                "success": import_time
                < 2.0,  # Should import in under 2 seconds
                "duration": import_time,
                "threshold": 2.0,
            }
        except Exception as e:
            performance_tests["import_time"] = {
                "success": False,
                "error": str(e),
            }

        # Test memory usage
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            performance_tests["memory_usage"] = {
                "success": memory_info.rss < 100 * 1024 * 1024,  # Under 100MB
                "rss_mb": memory_info.rss / (1024 * 1024),
                "vms_mb": memory_info.vms / (1024 * 1024),
                "threshold_mb": 100,
            }
        except Exception as e:
            performance_tests["memory_usage"] = {
                "success": False,
                "error": str(e),
            }

        # Calculate success
        successful_tests = sum(
            1
            for test in performance_tests.values()
            if test.get("success", False)
        )
        total_tests = len(performance_tests)
        success = successful_tests == total_tests

        if success:
            message = f"Performance validation successful ({successful_tests}/{total_tests} tests)"
        else:
            message = f"Performance validation failed ({successful_tests}/{total_tests} tests)"

        details = {
            "performance_tests": performance_tests,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
        }

        return success, message, details

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of the deployment."""
        self.logger.info("Starting comprehensive deployment validation...")

        # Define validation tests
        validation_tests = [
            ("File Structure", self.validate_file_structure, "installation"),
            ("Dependencies", self.validate_dependencies, "dependencies"),
            ("Module Imports", self.validate_imports, "imports"),
            ("Configuration", self.validate_configuration, "configuration"),
            (
                "Tool Initialization",
                self.validate_tools_initialization,
                "tools",
            ),
            ("GUI Components", self.validate_gui_components, "gui"),
            (
                "Network Operations",
                self.validate_network_operations,
                "network",
            ),
            ("Security Features", self.validate_security_features, "security"),
            ("Performance", self.validate_performance, "performance"),
        ]

        # Run all tests
        for test_name, test_func, category in validation_tests:
            self._run_test(test_name, test_func, category)

        # Generate summary
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - successful_tests

        # Calculate duration
        total_duration = time.time() - self.start_time.timestamp()

        # Group results by category
        results_by_category = {}
        for result in self.results:
            if result.category not in results_by_category:
                results_by_category[result.category] = []
            results_by_category[result.category].append(result)

        summary = {
            "overall_success": failed_tests == 0,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                (successful_tests / total_tests * 100)
                if total_tests > 0
                else 0
            ),
            "total_duration": total_duration,
            "validation_time": self.start_time.isoformat(),
            "results_by_category": results_by_category,
            "failed_test_names": [
                r.test_name for r in self.results if not r.success
            ],
        }

        if summary["overall_success"]:
            self.logger.info(
                f"✓ Validation completed successfully ({successful_tests}/{total_tests} tests passed)"
            )
        else:
            self.logger.error(
                f"✗ Validation failed ({failed_tests}/{total_tests} tests failed)"
            )

        return summary

    def generate_validation_report(self, summary: Dict[str, Any]) -> str:
        """Generate detailed validation report."""
        report_lines = [
            "=" * 80,
            "NETWORK CONNECTIVITY TOOLKIT - DEPLOYMENT VALIDATION REPORT",
            "=" * 80,
            "",
            f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Installation Directory: {self.install_dir}",
            f"System: {platform.system()} {platform.version()}",
            f"Python Version: {platform.python_version()}",
            "",
            "SUMMARY:",
            f"  Overall Success: {'✓ PASS' if summary['overall_success'] else '✗ FAIL'}",
            f"  Total Tests: {summary['total_tests']}",
            f"  Successful: {summary['successful_tests']}",
            f"  Failed: {summary['failed_tests']}",
            f"  Success Rate: {summary['success_rate']:.1f}%",
            f"  Duration: {summary['total_duration']:.2f} seconds",
            "",
        ]

        # Add category results
        for category, results in summary["results_by_category"].items():
            category_success = all(r.success for r in results)
            report_lines.extend(
                [
                    f"{category.upper()} TESTS:",
                    f"  Status: {'✓ PASS' if category_success else '✗ FAIL'}",
                    f"  Tests: {len(results)}",
                ]
            )

            for result in results:
                status = "✓" if result.success else "✗"
                report_lines.append(
                    f"    {status} {result.test_name}: {result.message}"
                )

                if not result.success and result.details:
                    if "error" in result.details:
                        report_lines.append(
                            f"      Error: {result.details['error']}"
                        )

            report_lines.append("")

        # Add failed tests details
        if summary["failed_tests"] > 0:
            report_lines.extend(["FAILED TESTS DETAILS:", ""])

            for result in self.results:
                if not result.success:
                    report_lines.extend(
                        [
                            f"Test: {result.test_name}",
                            f"  Message: {result.message}",
                            f"  Duration: {result.duration:.3f}s",
                            f"  Category: {result.category}",
                        ]
                    )

                    if result.details:
                        report_lines.append("  Details:")
                        for key, value in result.details.items():
                            if isinstance(value, (list, dict)):
                                report_lines.append(
                                    f"    {key}: {json.dumps(value, indent=6)}"
                                )
                            else:
                                report_lines.append(f"    {key}: {value}")

                    report_lines.append("")

        # Add recommendations
        report_lines.extend(["RECOMMENDATIONS:", ""])

        if summary["overall_success"]:
            report_lines.extend(
                [
                    "✓ Deployment validation successful!",
                    "✓ All components are functioning correctly",
                    "✓ System is ready for production use",
                    "",
                    "Next steps:",
                    "  1. Review configuration settings",
                    "  2. Perform user acceptance testing",
                    "  3. Set up monitoring and alerting",
                    "  4. Create backup procedures",
                ]
            )
        else:
            report_lines.extend(
                [
                    "✗ Deployment validation failed!",
                    "✗ Issues must be resolved before production use",
                    "",
                    "Required actions:",
                ]
            )

            for test_name in summary["failed_test_names"]:
                report_lines.append(f"  - Fix issues in: {test_name}")

            report_lines.extend(
                [
                    "",
                    "After fixing issues:",
                    "  1. Re-run validation: python deployment/validate_deployment.py",
                    "  2. Review logs for detailed error information",
                    "  3. Consult troubleshooting documentation",
                ]
            )

        report_lines.extend(["", "=" * 80])

        return "\n".join(report_lines)


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Network Connectivity Toolkit Deployment Validator"
    )

    parser.add_argument(
        "--install-dir", help="Installation directory to validate"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument("--report-file", help="Save validation report to file")

    parser.add_argument("--json-output", help="Save JSON results to file")

    args = parser.parse_args()

    # Create validator
    validator = NetworkConnectivityValidator(
        install_dir=args.install_dir, verbose=args.verbose
    )

    # Run validation
    summary = validator.run_comprehensive_validation()

    # Generate report
    report = validator.generate_validation_report(summary)

    # Output report
    print(report)

    # Save report to file if requested
    if args.report_file:
        with open(args.report_file, "w") as f:
            f.write(report)
        print(f"\nValidation report saved to: {args.report_file}")

    # Save JSON results if requested
    if args.json_output:
        json_data = {
            "summary": summary,
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "message": r.message,
                    "details": r.details,
                    "duration": r.duration,
                    "category": r.category,
                }
                for r in validator.results
            ],
        }

        with open(args.json_output, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"JSON results saved to: {args.json_output}")

    # Exit with appropriate code
    sys.exit(0 if summary["overall_success"] else 1)


if __name__ == "__main__":
    main()
