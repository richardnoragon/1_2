"""
HP-02 File Validator Critical Testing Suite
Enterprise Quality Engineering Gatekeeper

ZERO TOLERANCE VALIDATION:
- API consistency across tool categories
- Security policy validation
- Performance benchmarking (<0.002s target)
- Integration validation

AUTHORITY: Quality Engineering Gatekeeper
"""

import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import MagicMock

# Mock log_manager before importing file_validator
mock_log_manager = MagicMock()
mock_logger = MagicMock()
mock_log_manager.get_logger.return_value = mock_logger

# Set up path and mocks
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.modules["src.log_manager"] = mock_log_manager

# Import file validator after mocking
from file_validator import detect_file_type, validate_file_type
from file_validator.compat import is_allowed, legacy_validate
from file_validator.exceptions import InvalidModeError
from file_validator.models import DetectionResult, ValidationResult


class HP02TestRunner:
    """HP-02 File Validator Test Execution Engine."""

    def __init__(self):
        """Initialize test runner."""
        self.test_results = []
        self.temp_dir = None
        self.test_files = {}

        # CRITICAL PERFORMANCE TARGET
        self.PERFORMANCE_TARGET_MS = 2.0  # Must be <2ms (0.002s)

    def setup_test_environment(self):
        """Create test files with magic signatures."""
        print("Setting up test environment...")

        self.temp_dir = Path(tempfile.mkdtemp(prefix="hp02_"))

        # Test files with proper magic numbers
        test_data = {
            "pdf": (b"%PDF-1.4\ntest content", ".pdf"),
            "png": (bytes.fromhex("89504E470D0A1A0A"), ".png"),
            "gif": (b"GIF87a", ".gif"),
            "jpg": (bytes.fromhex("FFD8FF"), ".jpg"),
            "zip": (b"PK\x03\x04", ".zip"),
            "exe": (b"MZ\x90\x00", ".exe"),
            "elf": (b"\x7fELF", ""),
            "text": (b"Hello world text file content", ".txt"),
            "docx": (b"PK\x03\x04word/document.xml", ".docx"),
        }

        for file_type, (content, extension) in test_data.items():
            file_path = self.temp_dir / f"test_{file_type}{extension}"
            file_path.write_bytes(content)
            self.test_files[file_type] = file_path

        print(f"Created {len(self.test_files)} test files")

    def cleanup_environment(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            print("Test environment cleaned up")

    def execute_test(self, test_name, test_function):
        """Execute individual test and track results."""
        print(f"\nExecuting: {test_name}")

        try:
            start_time = time.perf_counter()
            result = test_function()
            duration = (time.perf_counter() - start_time) * 1000

            self.test_results.append(
                {
                    "name": test_name,
                    "status": "PASS",
                    "duration_ms": duration,
                    "result": result,
                }
            )

            print(f"   PASS ({duration:.2f}ms)")
            return True

        except Exception as e:
            self.test_results.append(
                {
                    "name": test_name,
                    "status": "FAIL",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )

            print(f"   FAIL: {e}")
            return False

    def test_file_detection(self):
        """Test 1: File type detection accuracy."""
        expected_detections = {
            "pdf": "pdf",
            "png": "png",
            "gif": "gif",
            "jpg": "jpg",
            "zip": "zip",
            "exe": "pe",
            "elf": "elf",
            "text": "text",
            "docx": "docx",
        }

        results = {}
        for file_type, expected in expected_detections.items():
            detection = detect_file_type(self.test_files[file_type])

            # Validate detection result
            assert isinstance(detection, DetectionResult)
            assert detection.detected_type == expected
            assert detection.confidence in ["high", "medium", "low"]
            assert len(detection.evidence) > 0

            results[file_type] = detection.detected_type

        return f"Detected {len(results)} file types correctly"

    def test_security_enforcement(self):
        """Test 2: Security policy enforcement."""
        pdf_file = self.test_files["pdf"]
        exe_file = self.test_files["exe"]

        # Test reject mode
        result = validate_file_type(pdf_file, allowed_types=["jpg"], mode="reject")
        assert not result.is_match
        assert result.action == "reject"

        # Test warn mode
        result = validate_file_type(pdf_file, allowed_types=["jpg"], mode="warn")
        assert not result.is_match
        assert result.action == "warn"

        # Test auto mode with executable - CRITICAL SECURITY CHECK
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"

        # Test allowed file
        result = validate_file_type(pdf_file, allowed_types=["pdf"], mode="reject")
        assert result.is_match
        assert result.action == "accept"

        return "Security policies enforced correctly"

    def test_performance_critical(self):
        """Test 3: CRITICAL performance benchmarks."""
        pdf_file = self.test_files["pdf"]

        # Test detection performance
        detect_times = []
        for _ in range(100):
            start = time.perf_counter()
            detect_file_type(pdf_file)
            detect_times.append((time.perf_counter() - start) * 1000)

        avg_detect = sum(detect_times) / len(detect_times)

        # Test validation performance
        validate_times = []
        for _ in range(100):
            start = time.perf_counter()
            validate_file_type(pdf_file, allowed_types=["pdf"])
            validate_times.append((time.perf_counter() - start) * 1000)

        avg_validate = sum(validate_times) / len(validate_times)

        # ZERO TOLERANCE PERFORMANCE CHECK
        if avg_detect >= self.PERFORMANCE_TARGET_MS:
            raise AssertionError(
                f"Detection too slow: {avg_detect:.3f}ms >= {self.PERFORMANCE_TARGET_MS}ms"
            )
        if avg_validate >= self.PERFORMANCE_TARGET_MS:
            raise AssertionError(
                f"Validation too slow: {avg_validate:.3f}ms >= {self.PERFORMANCE_TARGET_MS}ms"
            )

        return {
            "detection_avg": avg_detect,
            "validation_avg": avg_validate,
            "target": self.PERFORMANCE_TARGET_MS,
            "status": "MEETS_TARGET",
        }

    def test_legacy_api(self):
        """Test 4: Legacy API compatibility."""
        pdf_file = self.test_files["pdf"]

        # Test legacy_validate
        success, reason, validation = legacy_validate(pdf_file, allowed_types=["pdf"])
        assert success is True
        assert isinstance(validation, ValidationResult)

        # Test is_allowed
        assert is_allowed(pdf_file, allowed_types=["pdf"]) is True
        assert is_allowed(pdf_file, allowed_types=["jpg"]) is False

        return "Legacy API compatibility verified"

    def test_exception_handling(self):
        """Test 5: Exception handling."""
        # Test invalid mode
        try:
            validate_file_type(self.test_files["pdf"], mode="invalid")
            raise AssertionError("Should have raised InvalidModeError")
        except InvalidModeError:
            pass

        # Test non-existent file
        try:
            detect_file_type("/nonexistent/file.pdf")
            raise AssertionError("Should have raised FileNotFoundError")
        except FileNotFoundError:
            pass

        return "Exception handling working correctly"

    def test_executable_blocking(self):
        """Test 6: Executable threat blocking."""
        exe_file = self.test_files["exe"]
        elf_file = self.test_files["elf"]

        # Test PE executable blocking
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"

        # Test ELF executable blocking
        result = validate_file_type(elf_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"

        return "Executable threats properly blocked"

    def run_comprehensive_suite(self):
        """Execute complete HP-02 test suite."""

        print("=" * 70)
        print("HP-02: CRITICAL FILE VALIDATOR INTEGRATION TESTING")
        print("Enterprise Quality Engineering Gatekeeper")
        print("ZERO TOLERANCE QUALITY ENFORCEMENT")
        print("=" * 70)

        try:
            self.setup_test_environment()

            # Define test suite
            tests = [
                ("File Type Detection Accuracy", self.test_file_detection),
                ("Security Policy Enforcement", self.test_security_enforcement),
                ("Performance Benchmarks", self.test_performance_critical),
                ("Legacy API Compatibility", self.test_legacy_api),
                ("Exception Handling", self.test_exception_handling),
                ("Executable Threat Blocking", self.test_executable_blocking),
            ]

            # Execute tests
            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                if self.execute_test(test_name, test_func):
                    passed += 1

            self.generate_report(passed, total)
            return passed == total

        finally:
            self.cleanup_environment()

    def generate_report(self, passed, total):
        """Generate final test report."""

        print(f"\n{'=' * 70}")
        print("HP-02 TEST EXECUTION REPORT")
        print(f"{'=' * 70}")

        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")

        # Find performance results
        perf_result = None
        for result in self.test_results:
            if (
                result["name"] == "Performance Benchmarks"
                and result["status"] == "PASS"
            ):
                perf_result = result["result"]
                break

        if perf_result:
            print("\nPerformance Results:")
            print(f"   Detection: {perf_result['detection_avg']:.3f}ms")
            print(f"   Validation: {perf_result['validation_avg']:.3f}ms")
            print(f"   Target: <{perf_result['target']}ms")
            print(f"   Status: {perf_result['status']}")

        # Test details
        print("\nTest Details:")
        for result in self.test_results:
            status_icon = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
            print(f"   {status_icon} {result['name']}")
            if result["status"] == "FAIL" and "error" in result:
                print(f"         Error: {result['error']}")

        # Final assessment
        print(f"\n{'=' * 70}")
        if passed == total:
            print("STATUS: FILE VALIDATOR READY FOR PRODUCTION")
            print("VERDICT: ALL QUALITY GATES SATISFIED")
        else:
            print("STATUS: PRODUCTION BLOCKED")
            print("VERDICT: CRITICAL ISSUES REQUIRE REMEDIATION")
        print(f"{'=' * 70}")


def main():
    """Execute HP-02 file validator testing."""
    runner = HP02TestRunner()

    try:
        success = runner.run_comprehensive_suite()
        return 0 if success else 1

    except Exception as e:
        print(f"\nCRITICAL TEST EXECUTION FAILURE: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
