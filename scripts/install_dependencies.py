#!/usr/bin/env python3
"""
RFU Multi-Pane File Explorer Dependency Installation Framework
Enterprise Principal Engineer Implementation - Section 7

This script handles the installation, validation, and testing of all
dependencies specified in Section 7 of the RFU Multi-Pane File Explorer
Development Plan.

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: 2024-09-13
Compliance: Zero-compromise quality assurance protocols
"""

import importlib.util
import json
import logging
import platform
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pkg_resources


@dataclass
class DependencyStatus:
    """Tracks the status of a dependency installation."""

    name: str
    required_version: str
    installed_version: Optional[str]
    # Status: 'not_installed', 'installed', 'upgrade_needed', 'incompatible'
    status: str
    installation_success: bool
    test_results: Dict[str, Any]
    error_message: Optional[str]
    timestamp: str


@dataclass
class InstallationReport:
    """Comprehensive installation report."""

    timestamp: str
    python_version: str
    platform_info: str
    total_dependencies: int
    successful_installations: int
    failed_installations: int
    skipped_dependencies: int
    dependency_statuses: List[DependencyStatus]
    performance_metrics: Dict[str, float]
    test_summary: Dict[str, Any]


class DependencyInstaller:
    """Enterprise-grade dependency installation and validation framework."""

    def __init__(
        self, requirements_file: str = "requirements_multi_pane_explorer.txt"
    ):
        """Initialize the dependency installer."""
        self.requirements_file = Path(requirements_file)
        self.setup_logging()
        self.core_dependencies = [
            "PyQt5>=5.15.0",
            "psutil>=5.8.0",
            "watchdog>=2.1.0",
            "send2trash>=1.8.0",
            "pillow>=8.0.0",
            "chardet>=4.0.0",
            "python-magic>=0.4.24",
        ]
        self.optional_dependencies = [
            "natsort>=7.1.0",
            "humanize>=3.0.0",
            "rapidfuzz>=1.6.0",
            "thumbnail>=0.1.0",
        ]
        self.dependency_statuses: List[DependencyStatus] = []

    def setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    log_dir
                    / f"dependency_installation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                ),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def validate_environment(self) -> Dict[str, Any]:
        """Validate the Python environment before installation."""
        self.logger.info("Validating Python environment...")

        environment_info = {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "pip_version": self._get_pip_version(),
            "virtual_env": self._detect_virtual_environment(),
            "available_memory": self._get_available_memory(),
            "disk_space": self._get_available_disk_space(),
        }

        # Validation checks
        checks = {
            "python_version_check": self._validate_python_version(),
            "pip_available": self._validate_pip(),
            "internet_connectivity": self._test_internet_connectivity(),
            "write_permissions": self._test_write_permissions(),
            "memory_sufficient": environment_info["available_memory"]
            > 1024 * 1024 * 1024,  # 1GB
            "disk_space_sufficient": environment_info["disk_space"]
            > 5 * 1024 * 1024 * 1024,  # 5GB
        }

        environment_info["validation_checks"] = checks

        # Log validation results
        for check, result in checks.items():
            self.logger.info(
                f"Environment check {check}: {'PASS' if result else 'FAIL'}"
            )

        return environment_info

    def _get_pip_version(self) -> str:
        """Get pip version."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return (
                result.stdout.strip() if result.returncode == 0 else "Unknown"
            )
        except Exception:
            return "Unknown"

    def _detect_virtual_environment(self) -> bool:
        """Detect if running in a virtual environment."""
        return hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

    def _get_available_memory(self) -> int:
        """Get available system memory in bytes."""
        try:
            import psutil

            return psutil.virtual_memory().available
        except ImportError:
            return 0

    def _get_available_disk_space(self) -> int:
        """Get available disk space in bytes."""
        try:
            import shutil

            return shutil.disk_usage(".").free
        except Exception:
            return 0

    def _validate_python_version(self) -> bool:
        """Validate Python version compatibility."""
        return sys.version_info >= (3, 8)

    def _validate_pip(self) -> bool:
        """Validate pip availability."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                timeout=30,
                check=True,
            )
            return True
        except Exception:
            return False

    def _test_internet_connectivity(self) -> bool:
        """Test internet connectivity for package downloads."""
        try:
            import urllib.request

            urllib.request.urlopen("https://pypi.org", timeout=10)
            return True
        except Exception:
            return False

    def _test_write_permissions(self) -> bool:
        """Test write permissions in current directory."""
        try:
            test_file = Path("._permission_test")
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False

    def check_current_dependencies(self) -> Dict[str, DependencyStatus]:
        """Check the current status of all dependencies."""
        self.logger.info("Checking current dependency status...")

        all_deps = self.core_dependencies + self.optional_dependencies
        status_map = {}

        for dep_spec in all_deps:
            dep_name = dep_spec.split(">=")[0].split("==")[0].split("[")[0]
            required_version = (
                dep_spec.split(">=")[1] if ">=" in dep_spec else "latest"
            )

            status = DependencyStatus(
                name=dep_name,
                required_version=required_version,
                installed_version=None,
                status="not_installed",
                installation_success=False,
                test_results={},
                error_message=None,
                timestamp=datetime.now().isoformat(),
            )

            try:
                # Check if package is installed
                installed_version = pkg_resources.get_distribution(
                    dep_name
                ).version
                status.installed_version = installed_version
                status.status = "installed"

                # Check version compatibility
                if ">=" in dep_spec:
                    min_version = dep_spec.split(">=")[1].split(",")[0]
                    if pkg_resources.parse_version(
                        installed_version
                    ) < pkg_resources.parse_version(min_version):
                        status.status = "upgrade_needed"

            except pkg_resources.DistributionNotFound:
                status.status = "not_installed"
            except Exception as e:
                status.status = "error"
                status.error_message = str(e)

            status_map[dep_name] = status
            self.dependency_statuses.append(status)

        return status_map

    def install_dependencies(
        self, force_reinstall: bool = False
    ) -> InstallationReport:
        """Install all dependencies with comprehensive error handling."""
        self.logger.info("Starting dependency installation process...")

        start_time = datetime.now()
        environment_info = self.validate_environment()

        # Check current status
        current_status = self.check_current_dependencies()

        # Install core dependencies first
        self.logger.info("Installing core dependencies...")
        core_results = self._install_dependency_group(
            self.core_dependencies, "core", force_reinstall
        )

        # Install optional dependencies
        self.logger.info("Installing optional dependencies...")
        optional_results = self._install_dependency_group(
            self.optional_dependencies, "optional", force_reinstall
        )

        # Platform-specific dependencies
        platform_deps = self._get_platform_specific_dependencies()
        if platform_deps:
            self.logger.info("Installing platform-specific dependencies...")
            platform_results = self._install_dependency_group(
                platform_deps, "platform", force_reinstall
            )
        else:
            platform_results = {}

        # Compile results
        all_results = {**core_results, **optional_results, **platform_results}

        # Run post-installation tests
        test_results = self._run_post_installation_tests()

        # Generate comprehensive report
        end_time = datetime.now()
        installation_time = (end_time - start_time).total_seconds()

        report = InstallationReport(
            timestamp=end_time.isoformat(),
            python_version=sys.version,
            platform_info=platform.platform(),
            total_dependencies=len(all_results),
            successful_installations=len(
                [r for r in all_results.values() if r.installation_success]
            ),
            failed_installations=len(
                [r for r in all_results.values() if not r.installation_success]
            ),
            skipped_dependencies=0,
            dependency_statuses=list(all_results.values()),
            performance_metrics={
                "total_installation_time": installation_time,
                "average_time_per_dependency": (
                    installation_time / len(all_results) if all_results else 0
                ),
            },
            test_summary=test_results,
        )

        # Save report
        self._save_installation_report(report)

        return report

    def _install_dependency_group(
        self,
        dependencies: List[str],
        group_name: str,
        force_reinstall: bool = False,
    ) -> Dict[str, DependencyStatus]:
        """Install a group of dependencies."""
        results = {}

        for dep_spec in dependencies:
            dep_name = dep_spec.split(">=")[0].split("==")[0].split("[")[0]
            self.logger.info(f"Installing {group_name} dependency: {dep_name}")

            status = self._install_single_dependency(dep_spec, force_reinstall)
            results[dep_name] = status

            # Update global status list
            for i, existing_status in enumerate(self.dependency_statuses):
                if existing_status.name == dep_name:
                    self.dependency_statuses[i] = status
                    break

        return results

    def _install_single_dependency(
        self, dep_spec: str, force_reinstall: bool = False
    ) -> DependencyStatus:
        """Install a single dependency with comprehensive error handling."""
        dep_name = dep_spec.split(">=")[0].split("==")[0].split("[")[0]

        status = DependencyStatus(
            name=dep_name,
            required_version=dep_spec,
            installed_version=None,
            status="installing",
            installation_success=False,
            test_results={},
            error_message=None,
            timestamp=datetime.now().isoformat(),
        )

        try:
            # Prepare installation command
            cmd = [sys.executable, "-m", "pip", "install"]

            if force_reinstall:
                cmd.append("--force-reinstall")

            cmd.extend(["--upgrade", dep_spec])

            # Execute installation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )

            if result.returncode == 0:
                status.installation_success = True
                status.status = "installed"

                # Get installed version
                try:
                    installed_version = pkg_resources.get_distribution(
                        dep_name
                    ).version
                    status.installed_version = installed_version
                except Exception:
                    status.installed_version = "unknown"

                self.logger.info(
                    f"Successfully installed {dep_name} version {status.installed_version}"
                )

            else:
                status.installation_success = False
                status.status = "failed"
                status.error_message = result.stderr
                self.logger.error(
                    f"Failed to install {dep_name}: {result.stderr}"
                )

        except subprocess.TimeoutExpired:
            status.installation_success = False
            status.status = "timeout"
            status.error_message = "Installation timeout"
            self.logger.error(f"Installation timeout for {dep_name}")

        except Exception as e:
            status.installation_success = False
            status.status = "error"
            status.error_message = str(e)
            self.logger.error(f"Installation error for {dep_name}: {e}")

        return status

    def _get_platform_specific_dependencies(self) -> List[str]:
        """Get platform-specific dependencies."""
        deps = []

        if platform.system() == "Windows":
            deps.extend(["pywin32>=306", "wmi>=1.5.1"])
        elif platform.system() == "Linux":
            deps.extend(["python-magic-bin>=0.4.14"])

        return deps

    def _run_post_installation_tests(self) -> Dict[str, Any]:
        """Run comprehensive post-installation tests."""
        self.logger.info("Running post-installation tests...")

        test_results = {
            "import_tests": {},
            "functionality_tests": {},
            "version_compatibility_tests": {},
            "performance_tests": {},
        }

        # Import tests
        core_imports = [
            ("PyQt5.QtWidgets", "QApplication"),
            ("psutil", None),
            ("watchdog.observers", "Observer"),
            ("send2trash", "send2trash"),
            ("PIL", "Image"),
            ("chardet", "detect"),
        ]

        optional_imports = [
            ("natsort", "natsorted"),
            ("humanize", "naturalsize"),
            ("rapidfuzz", "fuzz"),
        ]

        test_results["import_tests"]["core"] = self._test_imports(core_imports)
        test_results["import_tests"]["optional"] = self._test_imports(
            optional_imports
        )

        # Functionality tests
        test_results["functionality_tests"] = self._test_basic_functionality()

        # Performance tests
        test_results["performance_tests"] = self._test_performance()

        return test_results

    def _test_imports(
        self, import_list: List[Tuple[str, Optional[str]]]
    ) -> Dict[str, bool]:
        """Test imports for a list of modules."""
        results = {}

        for module_name, attr_name in import_list:
            try:
                module = importlib.import_module(module_name)
                if attr_name:
                    getattr(module, attr_name)
                results[module_name] = True
                self.logger.info(f"Import test PASSED: {module_name}")
            except Exception as e:
                results[module_name] = False
                self.logger.error(f"Import test FAILED: {module_name} - {e}")

        return results

    def _test_basic_functionality(self) -> Dict[str, bool]:
        """Test basic functionality of core dependencies."""
        results = {}

        # Test PyQt5
        try:
            import sys

            from PyQt5.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            results["pyqt5_functionality"] = True
        except Exception as e:
            results["pyqt5_functionality"] = False
            self.logger.error(f"PyQt5 functionality test failed: {e}")

        # Test psutil
        try:
            import psutil

            _ = psutil.cpu_percent()
            _ = psutil.virtual_memory()
            results["psutil_functionality"] = True
        except Exception as e:
            results["psutil_functionality"] = False
            self.logger.error(f"psutil functionality test failed: {e}")

        # Test watchdog
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            observer = Observer()
            results["watchdog_functionality"] = True
        except Exception as e:
            results["watchdog_functionality"] = False
            self.logger.error(f"watchdog functionality test failed: {e}")

        # Test send2trash
        try:
            import send2trash

            # Don't actually trash anything in test
            results["send2trash_functionality"] = True
        except Exception as e:
            results["send2trash_functionality"] = False
            self.logger.error(f"send2trash functionality test failed: {e}")

        # Test Pillow
        try:
            from PIL import Image

            # Create a small test image
            img = Image.new("RGB", (10, 10), color="red")
            results["pillow_functionality"] = True
        except Exception as e:
            results["pillow_functionality"] = False
            self.logger.error(f"Pillow functionality test failed: {e}")

        return results

    def _test_performance(self) -> Dict[str, float]:
        """Test performance of critical dependencies."""
        import time

        results = {}

        # Test rapid file system operations with watchdog
        try:
            from watchdog.observers import Observer

            start_time = time.time()
            observer = Observer()
            observer.start()
            observer.stop()
            observer.join()
            results["watchdog_startup_time"] = time.time() - start_time
        except Exception:
            results["watchdog_startup_time"] = -1

        # Test image processing with Pillow
        try:
            from PIL import Image

            start_time = time.time()
            for _ in range(100):
                img = Image.new("RGB", (100, 100), color="red")
                img.resize((50, 50))
            results["pillow_processing_time"] = time.time() - start_time
        except Exception:
            results["pillow_processing_time"] = -1

        return results

    def _save_installation_report(self, report: InstallationReport):
        """Save installation report to file."""
        reports_dir = Path("results")
        reports_dir.mkdir(exist_ok=True)

        report_file = (
            reports_dir
            / f"dependency_installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Convert dataclass to dict for JSON serialization
        report_dict = asdict(report)

        with open(report_file, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        self.logger.info(f"Installation report saved to: {report_file}")

    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        if not self.dependency_statuses:
            return "No dependency status information available."

        successful = len(
            [s for s in self.dependency_statuses if s.installation_success]
        )
        failed = len(
            [s for s in self.dependency_statuses if not s.installation_success]
        )
        total = len(self.dependency_statuses)

        report = f"""
RFU Multi-Pane File Explorer Dependency Installation Summary
=========================================================
Total Dependencies: {total}
Successful Installations: {successful}
Failed Installations: {failed}
Success Rate: {(successful/total)*100:.1f}%

Core Dependencies Status:
"""

        for status in self.dependency_statuses:
            if status.name in [
                dep.split(">=")[0] for dep in self.core_dependencies
            ]:
                report += f"  {status.name}: {status.status} (v{status.installed_version or 'N/A'})\n"

        report += "\nOptional Dependencies Status:\n"
        for status in self.dependency_statuses:
            if status.name in [
                dep.split(">=")[0] for dep in self.optional_dependencies
            ]:
                report += f"  {status.name}: {status.status} (v{status.installed_version or 'N/A'})\n"

        if failed > 0:
            report += "\nFailed Installations:\n"
            for status in self.dependency_statuses:
                if not status.installation_success:
                    report += f"  {status.name}: {status.error_message or 'Unknown error'}\n"

        return report


def main():
    """Main execution function."""
    installer = DependencyInstaller()

    try:
        # Check environment
        env_info = installer.validate_environment()

        # Check current dependencies
        current_status = installer.check_current_dependencies()

        # Install dependencies
        report = installer.install_dependencies()

        # Generate summary
        summary = installer.generate_summary_report()
        print(summary)

        # Return appropriate exit code
        if report.failed_installations == 0:
            print("\n✅ All dependencies installed successfully!")
            return 0
        else:
            print(
                f"\n❌ {report.failed_installations} dependencies failed to install."
            )
            return 1

    except Exception as e:
        print(f"❌ Critical error during dependency installation: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
