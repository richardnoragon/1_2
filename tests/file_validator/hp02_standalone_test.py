"""
HP-02 Standalone File Validator Test Suite
Enterprise Quality Engineering Gatekeeper - ZERO TOLERANCE

Critical validation of centralized file validator system:
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
sys.modules["src.log_manager"] = MagicMock()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def create_mock_log_manager():
    """Create mock log manager for testing."""
    mock_manager = MagicMock()
    mock_logger = MagicMock()
    mock_manager.get_logger.return_value = mock_logger
    return mock_manager


# Mock the get_log_manager function
def get_log_manager():
    return create_mock_log_manager()


# Set up the mock
sys.modules["src.log_manager"].get_log_manager = get_log_manager

# Now import file validator components
from file_validator import detect_file_type, validate_file_type
from file_validator.compat import is_allowed, legacy_validate
from file_validator.exceptions import InvalidModeError
from file_validator.models import DetectionResult, ValidationResult


class HP02FileValidatorTestExecutor:
    """ZERO TOLERANCE file validator test execution."""

    def __init__(self):
        """Initialize test executor."""
        self.test_results = []
        self.temp_dir = None
        self.test_files = {}

        # CRITICAL PERFORMANCE TARGET
        self.PERFORMANCE_TARGET_MS = 2.0  # <0.002s = 2ms

    def setup_test_files(self):
        """Create test files with proper magic numbers."""
        print("🔧 Setting up test environment...")

        self.temp_dir = Path(tempfile.mkdtemp(prefix="hp02_"))

        # Test files with correct magic signatures
        files = {
            "pdf": (b"%PDF-1.4\ntest", ".pdf"),
            "png": (bytes.fromhex("89504E470D0A1A0A"), ".png"),
            "gif": (b"GIF87a", ".gif"),
            "jpg": (bytes.fromhex("FFD8FF"), ".jpg"),
            "zip": (b"PK\x03\x04", ".zip"),
            "exe": (b"MZ\x90\x00", ".exe"),  # PE header
            "elf": (b"\x7fELF", ""),  # ELF header
            "text": (b"Hello world test file", ".txt"),
            "docx": (b"PK\x03\x04word/", ".docx"),  # ZIP with word/
        }

        for ftype, (content, ext) in files.items():
            path = self.temp_dir / f"test_{ftype}{ext}"
            path.write_bytes(content)
            self.test_files[ftype] = path

        print(f"✅ Created {len(self.test_files)} test files")

    def cleanup(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            print("✅ Test cleanup complete")

    def run_test(self, name, func):
        """Execute test with result tracking."""
        print(f"\n🧪 {name}")

        try:
            start = time.perf_counter()
            result = func()
            duration = (time.perf_counter() - start) * 1000

            self.test_results.append(
                {
                    "name": name,
                    "status": "PASS",
                    "duration_ms": duration,
                    "result": result,
                }
            )

            print(f"   ✅ PASS ({duration:.2f}ms)")
            return True

        except Exception as e:
            self.test_results.append(
                {
                    "name": name,
                    "status": "FAIL",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )

            print(f"   ❌ FAIL: {e}")
            return False

    def test_file_detection_accuracy(self):
        """Test 1: File type detection accuracy."""
        expected = {
            "pdf": "pdf",
            "png": "png",
            "gif": "gif",
            "jpg": "jpg",
            "zip": "zip",
            "exe": "pe",  # Windows PE
            "elf": "elf",  # Linux ELF
            "text": "text",
            "docx": "docx",  # Office doc
        }

        results = {}
        for ftype, expected_type in expected.items():
            detection = detect_file_type(self.test_files[ftype])

            assert isinstance(detection, DetectionResult)
            assert detection.detected_type == expected_type
            assert detection.confidence in ["high", "medium", "low"]
            assert len(detection.evidence) > 0

            results[ftype] = detection.detected_type

        return results

    def test_security_policies(self):
        """Test 2: Security policy enforcement."""
        pdf_file = self.test_files["pdf"]
        exe_file = self.test_files["exe"]

        # Test reject mode
        result = validate_file_type(pdf_file, allowed_types=["jpg"], mode="reject")
        assert not result.is_match and result.action == "reject"

        # Test warn mode
        result = validate_file_type(pdf_file, allowed_types=["jpg"], mode="warn")
        assert not result.is_match and result.action == "warn"

        # Test auto mode with executable (CRITICAL)
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match and result.action == "reject"

        # Test allowed file
        result = validate_file_type(pdf_file, allowed_types=["pdf"], mode="reject")
        assert result.is_match and result.action == "accept"

        return "All security policies enforced"

    def test_performance_benchmarks(self):
        """Test 3: Performance benchmarks - CRITICAL."""
        pdf_file = self.test_files["pdf"]

        # Detection performance
        times = []
        for _ in range(100):
            start = time.perf_counter()
            detect_file_type(pdf_file)
            times.append((time.perf_counter() - start) * 1000)

        avg_detect_ms = sum(times) / len(times)

        # Validation performance
        times = []
        for _ in range(100):
            start = time.perf_counter()
            validate_file_type(pdf_file, allowed_types=["pdf"])
            times.append((time.perf_counter() - start) * 1000)

        avg_validate_ms = sum(times) / len(times)

        # ZERO TOLERANCE CHECK
        assert (
            avg_detect_ms < self.PERFORMANCE_TARGET_MS
        ), f"Detection too slow: {avg_detect_ms:.3f}ms"
        assert (
            avg_validate_ms < self.PERFORMANCE_TARGET_MS
        ), f"Validation too slow: {avg_validate_ms:.3f}ms"

        return {
            "detection_avg_ms": avg_detect_ms,
            "validation_avg_ms": avg_validate_ms,
            "target_ms": self.PERFORMANCE_TARGET_MS,
            "meets_target": True,
        }

    def test_legacy_compatibility(self):
        """Test 4: Legacy API compatibility."""
        pdf_file = self.test_files["pdf"]

        # Test legacy_validate
        success, reason, validation = legacy_validate(pdf_file, allowed_types=["pdf"])
        assert success is True
        assert isinstance(validation, ValidationResult)

        # Test is_allowed
        assert is_allowed(pdf_file, allowed_types=["pdf"]) is True
        assert is_allowed(pdf_file, allowed_types=["jpg"]) is False

        return "Legacy compatibility verified"

    def test_exception_handling(self):
        """Test 5: Exception handling."""
        # Invalid mode
        try:
            validate_file_type(self.test_files["pdf"], mode="invalid")
            assert False
        except InvalidModeError:
            pass

        # Non-existent file
        try:
            detect_file_type("/nonexistent/file.pdf")
            assert False
        except FileNotFoundError:
            pass

        return "Exception handling verified"

    def test_executable_blocking(self):
        """Test 6: Executable threat blocking."""
        exe_file = self.test_files["exe"]
        elf_file = self.test_files["elf"]

        # PE executable blocking
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match and result.action == "reject"

        # ELF executable blocking
        result = validate_file_type(elf_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match and result.action == "reject"

        return "Executable threats blocked"

    def run_complete_test_suite(self):
        """Execute HP-02 comprehensive test suite."""

        print("=" * 70)
        print("🔒 HP-02: CRITICAL FILE VALIDATOR INTEGRATION TESTING")
        print("🏢 Enterprise Quality Engineering Gatekeeper")
        print("⚡ ZERO TOLERANCE QUALITY ENFORCEMENT")
        print("=" * 70)

        try:
            self.setup_test_files()

            tests = [
                ("File Detection Accuracy", self.test_file_detection_accuracy),
                ("Security Policy Enforcement", self.test_security_policies),
                ("Performance Benchmarks", self.test_performance_benchmarks),
                ("Legacy API Compatibility", self.test_legacy_compatibility),
                ("Exception Handling", self.test_exception_handling),
                ("Executable Threat Blocking", self.test_executable_blocking),
            ]

            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                if self.run_test(test_name, test_func):
                    passed += 1

            self.generate_final_report(passed, total)
            return passed == total

        finally:
            self.cleanup()

    def generate_final_report(self, passed, total):
        """Generate comprehensive test report."""

        print(f"\n{'='*70}")
        print("📊 HP-02 TEST EXECUTION REPORT")
        print(f"{'='*70}")

        print(f"📈 Tests Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")

        # Performance summary
        perf_result = None
        for result in self.test_results:
            if (
                result["name"] == "Performance Benchmarks"
                and result["status"] == "PASS"
            ):
                perf_result = result["result"]
                break

        if perf_result:
            print(f"\n⚡ Performance Summary:")
            print(f"   Detection: {perf_result['detection_avg_ms']:.3f}ms")
            print(f"   Validation: {perf_result['validation_avg_ms']:.3f}ms")
            print(f"   Target: <{perf_result['target_ms']}ms")
            print(
                f"   Status: {'✅ MET' if perf_result['meets_target'] else '❌ FAILED'}"
            )

        # Test details
        print(f"\n📋 Test Results:")
        for result in self.test_results:
            icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {icon} {result['name']}: {result['status']}")
            if result["status"] == "FAIL":
                print(f"      {result['error']}")

        # Final verdict
        print(f"\n{'='*70}")
        if passed == total:
            print("🚀 HP-02 QUALITY GATES SATISFIED")
            print("✅ FILE VALIDATOR PRODUCTION READY")
        else:
            print("🛑 HP-02 QUALITY GATES FAILED")
            print("❌ PRODUCTION BLOCKED - REMEDIATION REQUIRED")
        print(f"{'='*70}")


def main():
    """Execute HP-02 file validator testing."""
    executor = HP02FileValidatorTestExecutor()

    try:
        success = executor.run_complete_test_suite()
        return 0 if success else 1

    except Exception as e:
        print(f"\n💥 CRITICAL TEST FAILURE: {e}")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
