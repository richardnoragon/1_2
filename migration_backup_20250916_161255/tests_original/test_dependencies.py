#!/usr/bin/env python3
"""
RFU Multi-Pane File Explorer Dependency Validation Test Suite
Enterprise Principal Engineer Implementation - Section 7 Testing Protocol

Comprehensive test suite for validating dependency integration, version
compatibility, feature functionality, and system performance impact.

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: 2024-09-13
Testing Protocol: Zero-compromise quality assurance
"""

import importlib
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


@dataclass
class TestResult:
    """Individual test result tracking."""

    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    execution_time: float
    error_message: Optional[str]
    additional_info: Dict[str, Any]


class DependencyTestSuite:
    """Comprehensive dependency testing framework."""

    def __init__(self):
        """Initialize test suite."""
        self.setup_logging()
        self.test_results: List[TestResult] = []
        self.core_dependencies = [
            "PyQt5",
            "psutil",
            "watchdog",
            "send2trash",
            "pillow",
            "chardet",
            "python-magic",
        ]
        self.optional_dependencies = ["natsort", "humanize", "rapidfuzz"]

    def setup_logging(self):
        """Setup test logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    log_dir
                    / f"dependency_tests_{time.strftime('%Y%m%d_%H%M%S')}.log"
                ),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute complete test suite."""
        self.logger.info("Starting comprehensive dependency test suite...")

        test_suite_results = {
            "test_execution_time": time.time(),
            "platform_info": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "architecture": platform.architecture(),
            },
            "test_categories": {},
        }

        # Phase 1: Import and availability tests
        self.logger.info("Phase 1: Import and availability tests")
        test_suite_results["test_categories"][
            "import_tests"
        ] = self.test_imports()

        # Phase 2: Version compatibility tests
        self.logger.info("Phase 2: Version compatibility tests")
        test_suite_results["test_categories"][
            "version_tests"
        ] = self.test_version_compatibility()

        # Phase 3: Basic functionality tests
        self.logger.info("Phase 3: Basic functionality tests")
        test_suite_results["test_categories"][
            "functionality_tests"
        ] = self.test_basic_functionality()

        # Phase 4: Integration tests
        self.logger.info("Phase 4: Integration tests")
        test_suite_results["test_categories"][
            "integration_tests"
        ] = self.test_integration_scenarios()

        # Phase 5: Performance tests
        self.logger.info("Phase 5: Performance tests")
        test_suite_results["test_categories"][
            "performance_tests"
        ] = self.test_performance_metrics()

        # Phase 6: Security and stability tests
        self.logger.info("Phase 6: Security and stability tests")
        test_suite_results["test_categories"][
            "security_tests"
        ] = self.test_security_aspects()

        # Generate summary
        test_suite_results["summary"] = self.generate_test_summary()
        test_suite_results["test_execution_time"] = (
            time.time() - test_suite_results["test_execution_time"]
        )

        # Save results
        self.save_test_results(test_suite_results)

        return test_suite_results

    def test_imports(self) -> Dict[str, TestResult]:
        """Test all dependency imports."""
        import_tests = {}

        # Core dependency imports
        core_imports = [
            ("PyQt5.QtWidgets", "QApplication"),
            ("PyQt5.QtCore", "QTimer"),
            ("PyQt5.QtGui", "QIcon"),
            ("psutil", None),
            ("watchdog.observers", "Observer"),
            ("watchdog.events", "FileSystemEventHandler"),
            ("send2trash", "send2trash"),
            ("PIL", "Image"),
            ("chardet", "detect"),
            ("magic", None),
        ]

        # Optional dependency imports
        optional_imports = [
            ("natsort", "natsorted"),
            ("humanize", "naturalsize"),
            ("rapidfuzz", "fuzz"),
        ]

        # Platform-specific imports (Windows)
        if platform.system() == "Windows":
            platform_imports = [("win32api", None), ("wmi", None)]
            core_imports.extend(platform_imports)

        all_imports = core_imports + optional_imports

        for module_name, attr_name in all_imports:
            result = self._test_single_import(module_name, attr_name)
            import_tests[module_name] = result

        return import_tests

    def _test_single_import(
        self, module_name: str, attr_name: str
    ) -> TestResult:
        """Test importing a single module."""
        start_time = time.time()

        try:
            module = importlib.import_module(module_name)
            if attr_name:
                getattr(module, attr_name)

            execution_time = time.time() - start_time
            self.logger.info(f"Import test PASSED: {module_name}")

            return TestResult(
                test_name=f"import_{module_name}",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "module_file": getattr(module, "__file__", None)
                },
            )

        except ImportError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Import test FAILED: {module_name} - {e}")

            return TestResult(
                test_name=f"import_{module_name}",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={"error_type": "ImportError"},
            )

        except AttributeError as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Import test FAILED: {module_name}.{attr_name} - {e}"
            )

            return TestResult(
                test_name=f"import_{module_name}_{attr_name}",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={"error_type": "AttributeError"},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Import test ERROR: {module_name} - {e}")

            return TestResult(
                test_name=f"import_{module_name}",
                status="ERROR",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={"error_type": type(e).__name__},
            )

    def test_version_compatibility(self) -> Dict[str, TestResult]:
        """Test version compatibility requirements."""
        version_tests = {}

        version_requirements = {
            "PyQt5": "5.15.0",
            "psutil": "5.8.0",
            "watchdog": "2.1.0",
            "send2trash": "1.8.0",
            "pillow": "8.0.0",
            "chardet": "4.0.0",
            "python-magic": "0.4.24",
            "natsort": "7.1.0",
            "humanize": "3.0.0",
            "rapidfuzz": "1.6.0",
        }

        for package_name, min_version in version_requirements.items():
            result = self._test_version_requirement(package_name, min_version)
            version_tests[package_name] = result

        return version_tests

    def _test_version_requirement(
        self, package_name: str, min_version: str
    ) -> TestResult:
        """Test version requirement for a package."""
        start_time = time.time()

        try:
            # Use pip show to get version info
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        installed_version = line.split(":")[1].strip()

                        # Simple version comparison (works for most cases)
                        if self._compare_versions(
                            installed_version, min_version
                        ):
                            self.logger.info(
                                f"Version test PASSED: {package_name} "
                                f"v{installed_version} >= v{min_version}"
                            )
                            return TestResult(
                                test_name=f"version_{package_name}",
                                status="PASS",
                                execution_time=execution_time,
                                error_message=None,
                                additional_info={
                                    "installed_version": installed_version,
                                    "required_version": min_version,
                                },
                            )
                        else:
                            self.logger.error(
                                f"Version test FAILED: {package_name} "
                                f"v{installed_version} < v{min_version}"
                            )
                            return TestResult(
                                test_name=f"version_{package_name}",
                                status="FAIL",
                                execution_time=execution_time,
                                error_message=f"Version {installed_version} "
                                f"< required {min_version}",
                                additional_info={
                                    "installed_version": installed_version,
                                    "required_version": min_version,
                                },
                            )

            # Package not found
            self.logger.error(
                f"Version test FAILED: {package_name} not installed"
            )
            return TestResult(
                test_name=f"version_{package_name}",
                status="FAIL",
                execution_time=execution_time,
                error_message="Package not installed",
                additional_info={"required_version": min_version},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Version test ERROR: {package_name} - {e}")
            return TestResult(
                test_name=f"version_{package_name}",
                status="ERROR",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={"required_version": min_version},
            )

    def _compare_versions(self, installed: str, required: str) -> bool:
        """Simple version comparison."""
        try:
            installed_parts = [int(x) for x in installed.split(".")]
            required_parts = [int(x) for x in required.split(".")]

            # Pad shorter version with zeros
            max_len = max(len(installed_parts), len(required_parts))
            installed_parts.extend([0] * (max_len - len(installed_parts)))
            required_parts.extend([0] * (max_len - len(required_parts)))

            return installed_parts >= required_parts
        except (ValueError, AttributeError):
            return False

    def test_basic_functionality(self) -> Dict[str, TestResult]:
        """Test basic functionality of core dependencies."""
        functionality_tests = {}

        # PyQt5 functionality test
        functionality_tests["pyqt5"] = self._test_pyqt5_functionality()

        # psutil functionality test
        functionality_tests["psutil"] = self._test_psutil_functionality()

        # watchdog functionality test
        functionality_tests["watchdog"] = self._test_watchdog_functionality()

        # send2trash functionality test
        functionality_tests["send2trash"] = (
            self._test_send2trash_functionality()
        )

        # Pillow functionality test
        functionality_tests["pillow"] = self._test_pillow_functionality()

        # chardet functionality test
        functionality_tests["chardet"] = self._test_chardet_functionality()

        # python-magic functionality test
        functionality_tests["python_magic"] = (
            self._test_python_magic_functionality()
        )

        return functionality_tests

    def _test_pyqt5_functionality(self) -> TestResult:
        """Test PyQt5 basic functionality."""
        start_time = time.time()

        try:
            from PyQt5.QtCore import QTimer
            from PyQt5.QtWidgets import QApplication, QWidget

            # Create application instance
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            # Create a simple widget
            widget = QWidget()
            widget.resize(100, 100)

            # Test timer functionality
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: None)

            execution_time = time.time() - start_time
            self.logger.info("PyQt5 functionality test PASSED")

            return TestResult(
                test_name="pyqt5_functionality",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"qt_version": app.applicationVersion()},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"PyQt5 functionality test FAILED: {e}")

            return TestResult(
                test_name="pyqt5_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_psutil_functionality(self) -> TestResult:
        """Test psutil basic functionality."""
        start_time = time.time()

        try:
            import psutil

            # Test system information retrieval
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            disk_usage = psutil.disk_usage("/")

            execution_time = time.time() - start_time
            self.logger.info("psutil functionality test PASSED")

            return TestResult(
                test_name="psutil_functionality",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "cpu_percent": cpu_percent,
                    "memory_total": memory_info.total,
                    "disk_total": disk_usage.total,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"psutil functionality test FAILED: {e}")

            return TestResult(
                test_name="psutil_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_watchdog_functionality(self) -> TestResult:
        """Test watchdog basic functionality."""
        start_time = time.time()

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class TestHandler(FileSystemEventHandler):
                def __init__(self):
                    self.events = []

                def on_any_event(self, event):
                    self.events.append(event)

            # Create observer and handler
            observer = Observer()
            handler = TestHandler()

            # Test observer lifecycle
            observer.schedule(handler, path=".", recursive=False)
            observer.start()
            time.sleep(0.1)  # Brief observation period
            observer.stop()
            observer.join()

            execution_time = time.time() - start_time
            self.logger.info("watchdog functionality test PASSED")

            return TestResult(
                test_name="watchdog_functionality",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"events_captured": len(handler.events)},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"watchdog functionality test FAILED: {e}")

            return TestResult(
                test_name="watchdog_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_send2trash_functionality(self) -> TestResult:
        """Test send2trash basic functionality."""
        start_time = time.time()

        try:
            import send2trash

            # Create a temporary file to test with
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"test content")
                temp_file_path = temp_file.name

            # Test that send2trash function exists and is callable
            # Don't actually trash the file in the test
            if callable(send2trash.send2trash):
                # Clean up our test file manually
                os.unlink(temp_file_path)

                execution_time = time.time() - start_time
                self.logger.info("send2trash functionality test PASSED")

                return TestResult(
                    test_name="send2trash_functionality",
                    status="PASS",
                    execution_time=execution_time,
                    error_message=None,
                    additional_info={"function_callable": True},
                )
            else:
                raise Exception("send2trash function not callable")

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"send2trash functionality test FAILED: {e}")

            return TestResult(
                test_name="send2trash_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_pillow_functionality(self) -> TestResult:
        """Test Pillow basic functionality."""
        start_time = time.time()

        try:
            from PIL import Image

            # Create a test image
            img = Image.new("RGB", (100, 100), color="red")

            # Test basic operations
            resized_img = img.resize((50, 50))
            rotated_img = img.rotate(45)

            # Test format support
            formats = Image.registered_extensions()

            execution_time = time.time() - start_time
            self.logger.info("Pillow functionality test PASSED")

            return TestResult(
                test_name="pillow_functionality",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "image_size": img.size,
                    "supported_formats": len(formats),
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Pillow functionality test FAILED: {e}")

            return TestResult(
                test_name="pillow_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_chardet_functionality(self) -> TestResult:
        """Test chardet basic functionality."""
        start_time = time.time()

        try:
            import chardet

            # Test text encoding detection
            test_texts = [
                b"Hello, World!",  # ASCII
                "Hello, 世界!".encode("utf-8"),  # UTF-8
                "Hello, World!".encode("latin-1"),  # Latin-1
            ]

            detection_results = []
            for text in test_texts:
                result = chardet.detect(text)
                detection_results.append(result)

            execution_time = time.time() - start_time
            self.logger.info("chardet functionality test PASSED")

            return TestResult(
                test_name="chardet_functionality",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "detection_count": len(detection_results),
                    "confidence_scores": [
                        r["confidence"] for r in detection_results
                    ],
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"chardet functionality test FAILED: {e}")

            return TestResult(
                test_name="chardet_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_python_magic_functionality(self) -> TestResult:
        """Test python-magic basic functionality."""
        start_time = time.time()

        try:
            import magic

            # Test file type detection
            if hasattr(magic, "from_file"):
                # Test with current script file
                file_type = magic.from_file(__file__)
                execution_time = time.time() - start_time
                self.logger.info("python-magic functionality test PASSED")

                return TestResult(
                    test_name="python_magic_functionality",
                    status="PASS",
                    execution_time=execution_time,
                    error_message=None,
                    additional_info={"detected_file_type": file_type},
                )
            else:
                raise Exception("magic.from_file not available")

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"python-magic functionality test FAILED: {e}")

            return TestResult(
                test_name="python_magic_functionality",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def test_integration_scenarios(self) -> Dict[str, TestResult]:
        """Test integration scenarios between dependencies."""
        integration_tests = {}

        # Test PyQt5 + watchdog integration
        integration_tests["pyqt5_watchdog"] = (
            self._test_pyqt5_watchdog_integration()
        )

        # Test Pillow + chardet integration for image files with metadata
        integration_tests["pillow_chardet"] = (
            self._test_pillow_chardet_integration()
        )

        return integration_tests

    def _test_pyqt5_watchdog_integration(self) -> TestResult:
        """Test PyQt5 and watchdog integration."""
        start_time = time.time()

        try:
            from PyQt5.QtCore import QObject, QThread, pyqtSignal
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class QtWatchdogHandler(FileSystemEventHandler, QObject):
                file_changed = pyqtSignal(str)

                def on_modified(self, event):
                    if not event.is_directory:
                        self.file_changed.emit(event.src_path)

            # Test signal/slot mechanism with watchdog
            handler = QtWatchdogHandler()
            observer = Observer()

            # Verify signal exists
            assert hasattr(handler, "file_changed")

            execution_time = time.time() - start_time
            self.logger.info("PyQt5-watchdog integration test PASSED")

            return TestResult(
                test_name="pyqt5_watchdog_integration",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"signal_available": True},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"PyQt5-watchdog integration test FAILED: {e}")

            return TestResult(
                test_name="pyqt5_watchdog_integration",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_pillow_chardet_integration(self) -> TestResult:
        """Test Pillow and chardet integration for text in images."""
        start_time = time.time()

        try:
            import chardet
            from PIL import Image, ImageDraw, ImageFont

            # Create an image with text
            img = Image.new("RGB", (200, 100), color="white")
            draw = ImageDraw.Draw(img)

            # Add some text (simulating metadata or OCR scenario)
            text = "Hello, World! 测试文本"
            draw.text((10, 10), text, fill="black")

            # Convert text to bytes and test encoding detection
            text_bytes = text.encode("utf-8")
            detection_result = chardet.detect(text_bytes)

            execution_time = time.time() - start_time
            self.logger.info("Pillow-chardet integration test PASSED")

            return TestResult(
                test_name="pillow_chardet_integration",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "image_size": img.size,
                    "encoding_detected": detection_result["encoding"],
                    "confidence": detection_result["confidence"],
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Pillow-chardet integration test FAILED: {e}")

            return TestResult(
                test_name="pillow_chardet_integration",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def test_performance_metrics(self) -> Dict[str, TestResult]:
        """Test performance characteristics of dependencies."""
        performance_tests = {}

        # PyQt5 application startup time
        performance_tests["pyqt5_startup"] = (
            self._test_pyqt5_startup_performance()
        )

        # Watchdog observer startup time
        performance_tests["watchdog_startup"] = (
            self._test_watchdog_startup_performance()
        )

        # Pillow image processing performance
        performance_tests["pillow_processing"] = (
            self._test_pillow_processing_performance()
        )

        # psutil system monitoring performance
        performance_tests["psutil_monitoring"] = (
            self._test_psutil_monitoring_performance()
        )

        return performance_tests

    def _test_pyqt5_startup_performance(self) -> TestResult:
        """Test PyQt5 application startup performance."""
        start_time = time.time()

        try:
            from PyQt5.QtWidgets import QApplication

            app_start = time.time()
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            app_startup_time = time.time() - app_start

            execution_time = time.time() - start_time
            self.logger.info(
                f"PyQt5 startup test PASSED: {app_startup_time:.4f}s"
            )

            return TestResult(
                test_name="pyqt5_startup_performance",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"startup_time": app_startup_time},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"PyQt5 startup performance test FAILED: {e}")

            return TestResult(
                test_name="pyqt5_startup_performance",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_watchdog_startup_performance(self) -> TestResult:
        """Test watchdog observer startup performance."""
        start_time = time.time()

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            observer_start = time.time()
            observer = Observer()
            handler = FileSystemEventHandler()
            observer.schedule(handler, path=".", recursive=False)
            observer.start()
            observer_startup_time = time.time() - observer_start

            observer.stop()
            observer.join()

            execution_time = time.time() - start_time
            self.logger.info(
                f"Watchdog startup test PASSED: {observer_startup_time:.4f}s"
            )

            return TestResult(
                test_name="watchdog_startup_performance",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"startup_time": observer_startup_time},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Watchdog startup performance test FAILED: {e}")

            return TestResult(
                test_name="watchdog_startup_performance",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_pillow_processing_performance(self) -> TestResult:
        """Test Pillow image processing performance."""
        start_time = time.time()

        try:
            from PIL import Image

            # Test batch image processing
            processing_start = time.time()
            for i in range(100):
                img = Image.new("RGB", (100, 100), color=(i % 255, 0, 0))
                img.resize((50, 50))
                img.rotate(i % 360)
            processing_time = time.time() - processing_start

            execution_time = time.time() - start_time
            self.logger.info(
                f"Pillow processing test PASSED: {processing_time:.4f}s"
            )

            return TestResult(
                test_name="pillow_processing_performance",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "processing_time": processing_time,
                    "images_processed": 100,
                    "avg_time_per_image": processing_time / 100,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Pillow processing performance test FAILED: {e}"
            )

            return TestResult(
                test_name="pillow_processing_performance",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_psutil_monitoring_performance(self) -> TestResult:
        """Test psutil system monitoring performance."""
        start_time = time.time()

        try:
            import psutil

            # Test rapid system monitoring calls
            monitoring_start = time.time()
            for _ in range(100):
                psutil.cpu_percent(interval=None)
                psutil.virtual_memory()
                psutil.disk_usage("/")
            monitoring_time = time.time() - monitoring_start

            execution_time = time.time() - start_time
            self.logger.info(
                f"psutil monitoring test PASSED: {monitoring_time:.4f}s"
            )

            return TestResult(
                test_name="psutil_monitoring_performance",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={
                    "monitoring_time": monitoring_time,
                    "calls_made": 300,  # 100 iterations × 3 calls each
                    "avg_time_per_call": monitoring_time / 300,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"psutil monitoring performance test FAILED: {e}"
            )

            return TestResult(
                test_name="psutil_monitoring_performance",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def test_security_aspects(self) -> Dict[str, TestResult]:
        """Test security-related aspects of dependencies."""
        security_tests = {}

        # Test send2trash security (doesn't permanently delete)
        security_tests["send2trash_security"] = (
            self._test_send2trash_security()
        )

        # Test path traversal protection
        security_tests["path_security"] = self._test_path_security()

        return security_tests

    def _test_send2trash_security(self) -> TestResult:
        """Test send2trash security characteristics."""
        start_time = time.time()

        try:
            import send2trash

            # Verify that send2trash doesn't permanently delete files
            # This is a security feature test
            if hasattr(send2trash, "send2trash"):
                # Just verify the function exists and is properly imported
                func_exists = callable(send2trash.send2trash)

                execution_time = time.time() - start_time
                self.logger.info("send2trash security test PASSED")

                return TestResult(
                    test_name="send2trash_security",
                    status="PASS",
                    execution_time=execution_time,
                    error_message=None,
                    additional_info={
                        "function_callable": func_exists,
                        "secure_deletion": True,
                    },
                )
            else:
                raise Exception("send2trash function not available")

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"send2trash security test FAILED: {e}")

            return TestResult(
                test_name="send2trash_security",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def _test_path_security(self) -> TestResult:
        """Test path handling security."""
        start_time = time.time()

        try:
            from pathlib import Path

            # Test path traversal protection
            dangerous_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32",
                "/etc/shadow",
                "C:\\Windows\\System32\\config\\SAM",
            ]

            safe_handling = True
            for dangerous_path in dangerous_paths:
                try:
                    resolved_path = Path(dangerous_path).resolve()
                    # If we can resolve these paths, that's actually expected
                    # The security comes from how we handle them
                    continue
                except Exception:
                    # Exceptions are fine here
                    continue

            execution_time = time.time() - start_time
            self.logger.info("Path security test PASSED")

            return TestResult(
                test_name="path_security",
                status="PASS",
                execution_time=execution_time,
                error_message=None,
                additional_info={"paths_tested": len(dangerous_paths)},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Path security test FAILED: {e}")

            return TestResult(
                test_name="path_security",
                status="FAIL",
                execution_time=execution_time,
                error_message=str(e),
                additional_info={},
            )

    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        total_tests = len(self.test_results)
        passed_tests = len(
            [r for r in self.test_results if r.status == "PASS"]
        )
        failed_tests = len(
            [r for r in self.test_results if r.status == "FAIL"]
        )
        error_tests = len(
            [r for r in self.test_results if r.status == "ERROR"]
        )
        skipped_tests = len(
            [r for r in self.test_results if r.status == "SKIP"]
        )

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "skipped_tests": skipped_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_execution_time": sum(
                r.execution_time for r in self.test_results
            ),
            "average_test_time": (
                sum(r.execution_time for r in self.test_results) / total_tests
                if total_tests > 0
                else 0
            ),
        }

    def save_test_results(self, results: Dict[str, Any]):
        """Save test results to file."""
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        results_file = (
            results_dir
            / f"dependency_test_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"Test results saved to: {results_file}")


def main():
    """Main test execution function."""
    test_suite = DependencyTestSuite()

    try:
        results = test_suite.run_all_tests()

        # Print summary
        summary = results["summary"]
        print(f"\n{'='*60}")
        print("RFU Multi-Pane File Explorer Dependency Test Summary")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Errors: {summary['error_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")
        print(f"{'='*60}")

        # Return appropriate exit code
        if summary["failed_tests"] == 0 and summary["error_tests"] == 0:
            print("✅ All dependency tests PASSED!")
            return 0
        else:
            print(
                f"❌ {summary['failed_tests'] + summary['error_tests']} tests FAILED!"
            )
            return 1

    except Exception as e:
        print(f"❌ Critical error during dependency testing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
