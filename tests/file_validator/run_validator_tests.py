"""
HP-02: Direct File Validator Testing Execution
Enterprise Quality Engineering Gatekeeper - Zero Tolerance Validation

Executes comprehensive file validator tests without external dependencies.
Validates API consistency, performance, security, and integration.
"""

import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import file validator components
from file_validator import detect_file_type, validate_file_type
from file_validator.compat import is_allowed, legacy_validate
from file_validator.exceptions import InvalidModeError
from file_validator.models import DetectionResult, ValidationResult


class HP02TestExecutor:
    """Enterprise Quality Engineering Test Executor."""

    def __init__(self):
        """Initialize test executor."""
        self.test_results = []
        self.performance_results = []
        self.temp_dir = None
        self.test_files = {}

        # Performance targets
        self.PERFORMANCE_TARGET_MS = 2.0  # 2ms = 0.002s

    def setup_test_environment(self):
        """Create comprehensive test file environment."""
        print("📁 Setting up test environment...")

        self.temp_dir = Path(tempfile.mkdtemp(prefix="hp02_validator_"))

        # Test file specifications with magic numbers
        test_specs = {
            "pdf": (b"%PDF-1.4\ntest content", ".pdf"),
            "png": (bytes.fromhex("89504E470D0A1A0A"), ".png"),
            "gif": (b"GIF87a", ".gif"),
            "jpg": (bytes.fromhex("FFD8FF"), ".jpg"),
            "zip": (b"PK\x03\x04", ".zip"),
            "exe": (b"MZ\x90\x00", ".exe"),
            "elf": (b"\x7fELF", ""),
            "text": (b"Hello world text content", ".txt"),
            "docx": (b"PK\x03\x04word/document.xml", ".docx"),
            "unknown": (b"\x00\x01\x02\x03", ".unknown"),
        }

        for file_type, (content, extension) in test_specs.items():
            filename = f"test_{file_type}{extension}"
            file_path = self.temp_dir / filename
            file_path.write_bytes(content)
            self.test_files[file_type] = file_path

        print(f"✅ Created {len(self.test_files)} test files in {self.temp_dir}")

    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            print(f"✅ Cleaned up test environment")

    def run_test(self, test_name: str, test_func):
        """Execute test and record results."""
        print(f"\n🧪 Running test: {test_name}")

        try:
            start_time = time.perf_counter()
            result = test_func()
            end_time = time.perf_counter()

            test_result = {
                "test_name": test_name,
                "status": "PASS",
                "duration_ms": (end_time - start_time) * 1000,
                "result": result,
                "error": None,
            }

            print(f"   ✅ PASS - {test_result['duration_ms']:.2f}ms")

        except Exception as e:
            test_result = {
                "test_name": test_name,
                "status": "FAIL",
                "duration_ms": 0,
                "result": None,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

            print(f"   ❌ FAIL - {test_result['error']}")

        self.test_results.append(test_result)
        return test_result["status"] == "PASS"

    def test_file_type_detection_accuracy(self):
        """Test 1: File Type Detection Accuracy."""

        # Expected detections for magic number matching
        expected_detections = {
            "pdf": "pdf",
            "png": "png",
            "gif": "gif",
            "jpg": "jpg",
            "zip": "zip",
            "exe": "pe",  # PE format for Windows exe
            "elf": "elf",  # ELF format for Linux
            "text": "text",
            "docx": "docx",  # Should refine from zip to docx
        }

        results = {}
        for file_key, expected_type in expected_detections.items():
            file_path = self.test_files[file_key]
            detection = detect_file_type(file_path)

            # Validate detection result structure
            assert isinstance(detection, DetectionResult)
            assert detection.detected_type == expected_type
            assert detection.confidence in ["high", "medium", "low"]
            assert len(detection.evidence) > 0

            results[file_key] = {
                "detected": detection.detected_type,
                "expected": expected_type,
                "confidence": detection.confidence,
                "evidence_count": len(detection.evidence),
            }

        return results

    def test_security_policy_enforcement(self):
        """Test 2: Security Policy Enforcement."""

        test_file = self.test_files["pdf"]
        exe_file = self.test_files["exe"]

        results = {}

        # Test reject mode - strict blocking
        result = validate_file_type(test_file, allowed_types=["jpg"], mode="reject")
        assert isinstance(result, ValidationResult)
        assert not result.is_match
        assert result.action == "reject"
        results["reject_mode"] = "PASS"

        # Test warn mode - allow with warning
        result = validate_file_type(test_file, allowed_types=["jpg"], mode="warn")
        assert not result.is_match
        assert result.action == "warn"
        results["warn_mode"] = "PASS"

        # Test auto mode with executable - should auto-reject
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"  # High-risk executable
        results["auto_mode_executable"] = "PASS"

        # Test allowed file - should accept
        result = validate_file_type(test_file, allowed_types=["pdf"], mode="reject")
        assert result.is_match
        assert result.action == "accept"
        results["allow_matching_type"] = "PASS"

        return results

    def test_performance_benchmarks(self):
        """Test 3: Performance Benchmarks (<2ms target)."""

        test_file = self.test_files["pdf"]

        # Benchmark file detection
        detection_times = []
        for _ in range(100):
            start = time.perf_counter()
            detect_file_type(test_file)
            end = time.perf_counter()
            detection_times.append((end - start) * 1000)  # Convert to ms

        avg_detection_ms = sum(detection_times) / len(detection_times)
        max_detection_ms = max(detection_times)

        # Benchmark file validation
        validation_times = []
        for _ in range(100):
            start = time.perf_counter()
            validate_file_type(test_file, allowed_types=["pdf"])
            end = time.perf_counter()
            validation_times.append((end - start) * 1000)  # Convert to ms

        avg_validation_ms = sum(validation_times) / len(validation_times)
        max_validation_ms = max(validation_times)

        # ZERO TOLERANCE - Must meet performance targets
        assert (
            avg_detection_ms < self.PERFORMANCE_TARGET_MS
        ), f"Detection too slow: {avg_detection_ms:.3f}ms > {self.PERFORMANCE_TARGET_MS}ms"

        assert (
            avg_validation_ms < self.PERFORMANCE_TARGET_MS
        ), f"Validation too slow: {avg_validation_ms:.3f}ms > {self.PERFORMANCE_TARGET_MS}ms"

        performance_results = {
            "detection_avg_ms": avg_detection_ms,
            "detection_max_ms": max_detection_ms,
            "validation_avg_ms": avg_validation_ms,
            "validation_max_ms": max_validation_ms,
            "target_ms": self.PERFORMANCE_TARGET_MS,
            "detection_meets_target": avg_detection_ms < self.PERFORMANCE_TARGET_MS,
            "validation_meets_target": avg_validation_ms < self.PERFORMANCE_TARGET_MS,
        }

        self.performance_results.append(performance_results)
        return performance_results

    def test_legacy_compatibility(self):
        """Test 4: Legacy API Compatibility."""

        test_file = self.test_files["pdf"]

        # Test legacy_validate function
        success, reason, validation_result = legacy_validate(
            test_file, allowed_types=["pdf"]
        )

        assert success is True
        assert isinstance(reason, str)
        assert isinstance(validation_result, ValidationResult)

        # Test is_allowed shorthand function
        allowed = is_allowed(test_file, allowed_types=["pdf"])
        assert allowed is True

        disallowed = is_allowed(test_file, allowed_types=["jpg"])
        assert disallowed is False

        return {
            "legacy_validate": "PASS",
            "is_allowed_true": "PASS",
            "is_allowed_false": "PASS",
        }

    def test_exception_handling(self):
        """Test 5: Exception Handling."""

        results = {}

        # Test invalid mode
        try:
            validate_file_type(self.test_files["pdf"], mode="invalid_mode")
            assert False, "Should have raised InvalidModeError"
        except InvalidModeError:
            results["invalid_mode_error"] = "PASS"

        # Test non-existent file
        try:
            detect_file_type("/absolutely/non/existent/file.pdf")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            results["nonexistent_file_error"] = "PASS"

        return results

    def test_executable_threat_detection(self):
        """Test 6: Executable Threat Detection."""

        exe_file = self.test_files["exe"]
        elf_file = self.test_files["elf"]

        results = {}

        # Test PE executable detection and blocking
        result = validate_file_type(exe_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"
        results["pe_executable_blocked"] = "PASS"

        # Test ELF executable detection and blocking
        result = validate_file_type(elf_file, allowed_types=["pdf"], mode="auto")
        assert not result.is_match
        assert result.action == "reject"
        results["elf_executable_blocked"] = "PASS"

        return results

    def run_comprehensive_tests(self):
        """Execute complete HP-02 test suite."""

        print("=" * 80)
        print("🔒 HP-02: CRITICAL FILE VALIDATOR INTEGRATION TESTING")
        print("🏢 Enterprise Quality Engineering Gatekeeper")
        print("⚡ ZERO TOLERANCE QUALITY ENFORCEMENT")
        print("=" * 80)

        try:
            # Setup test environment
            self.setup_test_environment()

            # Execute test suite
            tests = [
                (
                    "File Type Detection Accuracy",
                    self.test_file_type_detection_accuracy,
                ),
                ("Security Policy Enforcement", self.test_security_policy_enforcement),
                ("Performance Benchmarks", self.test_performance_benchmarks),
                ("Legacy API Compatibility", self.test_legacy_compatibility),
                ("Exception Handling", self.test_exception_handling),
                ("Executable Threat Detection", self.test_executable_threat_detection),
            ]

            passed_tests = 0
            total_tests = len(tests)

            for test_name, test_func in tests:
                success = self.run_test(test_name, test_func)
                if success:
                    passed_tests += 1

            # Generate comprehensive results
            self.generate_test_report(passed_tests, total_tests)

            return passed_tests == total_tests

        finally:
            self.cleanup_test_environment()

    def generate_test_report(self, passed_tests: int, total_tests: int):
        """Generate comprehensive test execution report."""

        print(f"\n{'='*80}")
        print("📊 HP-02 TEST EXECUTION SUMMARY")
        print(f"{'='*80}")

        print(f"📈 Test Results: {passed_tests}/{total_tests} tests passed")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Performance summary
        if self.performance_results:
            perf = self.performance_results[0]
            print(f"\n⚡ Performance Results:")
            print(
                f"   Detection Average: {perf['detection_avg_ms']:.3f}ms (target: <{perf['target_ms']}ms)"
            )
            print(
                f"   Validation Average: {perf['validation_avg_ms']:.3f}ms (target: <{perf['target_ms']}ms)"
            )
            print(
                f"   Performance Targets Met: {perf['detection_meets_target'] and perf['validation_meets_target']}"
            )

        # Individual test results
        print(f"\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {status_icon} {result['test_name']}: {result['status']}")
            if result["error"]:
                print(f"      Error: {result['error']}")

        # Final verdict
        print(f"\n{'='*80}")
        if passed_tests == total_tests:
            print("🚀 HP-02 QUALITY GATES SATISFIED - PRODUCTION READY")
            print("✅ ALL FILE VALIDATOR TESTS PASSED")
        else:
            print("🛑 HP-02 QUALITY GATES FAILED - PRODUCTION BLOCKED")
            print("❌ CRITICAL ISSUES DETECTED - IMMEDIATE REMEDIATION REQUIRED")
        print(f"{'='*80}")


def main():
    """Execute HP-02 file validator testing."""

    executor = HP02TestExecutor()

    try:
        success = executor.run_comprehensive_tests()
        return 0 if success else 1

    except Exception as e:
        print(f"\n💥 CRITICAL TEST EXECUTION FAILURE: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
