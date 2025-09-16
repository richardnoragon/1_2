#!/usr/bin/env python3
"""
Checksum End-to-End Test Suite

Comprehensive E2E testing for Checksum tool functionality.
Tests multi-algorithm verification, batch processing, and integrity validation.

Created: 2025-09-04
Coverage: Multi-algorithm support, batch processing, integrity validation,
          report generation, and automated workflows
Priority: HIGH (addressing 0% E2E coverage for Analysis Tools)
"""

import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.analysis_tools_test_utilities import (
        AnalysisToolsPerformanceMonitor, AnalysisToolsSignalTracker,
        AnalysisToolsTestDataFactory, MockAnalysisToolsHub, MockChecksumTool,
        assert_performance_target, checksum_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="Analysis Tools utilities not available"
)


class TestChecksumMultiAlgorithmVerification:
    """Test multi-algorithm checksum calculation and verification."""

    def test_multi_algorithm_calculation_workflow(self,
                                                checksum_test_environment):
        """
        Test: File Selection → Algorithm Selection → Calculation
        Algorithms: MD5, SHA-1, SHA-256, SHA-512, CRC32
        Target: < 25 seconds for multiple algorithms on 100 files
        """
        env = checksum_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']

        # Connect signal tracking
        signal_tracker.connect_all_signals()

        # Test all supported algorithms
        algorithms = ['md5', 'sha1', 'sha256', 'sha512', 'crc32']

        performance_monitor.start_monitoring('checksum', 'multi_algorithm')

        start_time = time.time()
        test_files = []

        try:
            # Create test files for checksum calculation
            for i in range(10):  # Create 10 test files
                file_path = os.path.join(test_data_path,
                                       f"checksum_test_{i:03d}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Test content for file {i}\n" * 100)
                test_files.append(file_path)

            # Execute multi-algorithm calculation
            result = tool.calculate_checksums(test_files, algorithms)

            # Verify calculation completion
            assert result is not None, "Checksum result should not be None"
            assert result['status'] == 'success', \
                f"Checksum calculation should succeed, got: {result.get('status')}"
            assert 'results_count' in result, \
                "Result should include count"

            # Verify checksum results structure
            assert len(tool.checksum_results) > 0, \
                "Tool should have checksum results"

            first_result = tool.checksum_results[0]
            required_fields = ['file_path', 'file_size', 'checksums',
                             'timestamp', 'status']
            for field in required_fields:
                assert field in first_result, \
                    f"Checksum result missing field: {field}"

            # Verify all algorithms are present
            checksums = first_result['checksums']
            for algorithm in algorithms:
                assert algorithm in checksums, \
                    f"Missing checksum for algorithm: {algorithm}"

            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 25.0, \
                f"Multi-algorithm calculation took too long: " \
                f"{workflow_time:.2f}s"

        finally:
            # Cleanup test files
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'checksum', 'multi_algorithm')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"


class TestChecksumBatchOperations:
    """Test batch processing capabilities for enterprise use."""

    def test_directory_tree_processing_workflow(self,
                                              checksum_test_environment):
        """
        Test: Root Directory → Recursive Scan → Batch Processing
        Target: < 60 seconds for 1,000 files in nested structure
        """
        env = checksum_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('checksum', 'batch_processing')

        start_time = time.time()
        nested_dirs = ['level1', 'level1/level2', 'level1/level2/level3']
        all_test_files = []

        try:
            # Create nested directory structure
            for dir_path in nested_dirs:
                full_dir_path = os.path.join(test_data_path, dir_path)
                os.makedirs(full_dir_path, exist_ok=True)

                # Create files in each directory
                for i in range(5):
                    file_path = os.path.join(full_dir_path,
                                           f"nested_file_{i:03d}.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Nested content {dir_path} file {i}")
                    all_test_files.append(file_path)

            # Execute batch processing
            algorithms = ['md5', 'sha256']
            options = {
                'recursive': True,
                'batch_size': 100,
                'parallel_threads': 4
            }

            result = tool.calculate_checksums(all_test_files, algorithms, options)

            assert result['status'] == 'success', \
                "Directory tree processing should succeed"

            # Verify comprehensive processing
            assert result['results_count'] >= len(all_test_files), \
                f"Should process all files: expected >= {len(all_test_files)}, " \
                f"got {result['results_count']}"

            workflow_time = time.time() - start_time
            assert workflow_time < 60.0, \
                f"Directory tree processing took too long: " \
                f"{workflow_time:.2f}s"

        finally:
            # Cleanup nested structure
            for dir_path in reversed(nested_dirs):
                full_dir_path = os.path.join(test_data_path, dir_path)
                if os.path.exists(full_dir_path):
                    shutil.rmtree(full_dir_path, ignore_errors=True)

            perf_result = performance_monitor.stop_monitoring(
                'checksum', 'batch_processing')
            assert perf_result['target_met'], \
                f"Batch processing performance target not met: {perf_result}"


class TestChecksumReportGeneration:
    """Test automated report generation in multiple formats."""

    def test_multi_format_report_generation_workflow(self,
                                                   checksum_test_environment):
        """
        Test: Checksum Calculation → Format Selection → Report Generation
        Formats: JSON, CSV, XML, HTML
        Target: < 5 seconds for report generation
        """
        env = checksum_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # First, calculate some checksums
        test_files = []
        for i in range(5):
            file_path = os.path.join(test_data_path, f"report_test_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Content for report test {i}")
            test_files.append(file_path)

        try:
            # Calculate checksums
            calculation_result = tool.calculate_checksums(test_files, ['md5', 'sha256'])
            assert calculation_result['status'] == 'success', \
                "Initial checksum calculation should succeed"

            # Test different report formats
            report_formats = ['json', 'csv', 'xml', 'html']

            for report_format in report_formats:
                performance_monitor.start_monitoring('checksum', 'report_generation')

                try:
                    # Create temporary output file
                    with tempfile.NamedTemporaryFile(
                        suffix=f'.{report_format}', delete=False) as tmp_file:
                        output_path = tmp_file.name

                    # Generate report
                    report_result = tool.generate_report(report_format, output_path)

                    # Verify report generation
                    assert report_result['status'] == 'success', \
                        f"Report generation should succeed for {report_format}"

                    # Clean up
                    if os.path.exists(output_path):
                        os.unlink(output_path)

                finally:
                    perf_result = performance_monitor.stop_monitoring(
                        'checksum', 'report_generation')
                    assert perf_result['target_met'], \
                        f"Report generation performance target not met for {report_format}"

        finally:
            # Cleanup test files
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.remove(file_path)


class TestChecksumErrorHandling:
    """Test error handling and recovery scenarios."""

    def test_file_access_error_handling(self, checksum_test_environment):
        """
        Test: File Access Error → Graceful Handling → Partial Results
        """
        env = checksum_test_environment
        tool = env['tool']
        signal_tracker = env['signal_tracker']

        signal_tracker.connect_all_signals()

        # Simulate file access error
        error_result = tool.simulate_error(
            'file_access_denied',
            'Permission denied for some files'
        )

        assert error_result['status'] == 'error', \
            "Should return error status"
        assert error_result['error_type'] == 'file_access_denied', \
            "Should identify error type"

        # Verify error tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['error_events'] > 0, \
            "Should track error events"

    def test_checksum_calculation_cancellation(self, checksum_test_environment):
        """
        Test: Long Operation → User Cancellation → Clean Termination
        """
        env = checksum_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']

        # Simulate cancellation
        tool.cancel_operation()

        # Execute operation (should be cancelled)
        result = tool.process_data(f"checksum_{test_data_path}")

        assert result['status'] == 'cancelled', \
            "Cancelled operation should return cancelled status"
        assert 'cancelled' in result['message'].lower(), \
            "Should indicate cancellation in message"

        # Verify cancellation state
        assert tool._should_cancel, "Tool should be in cancelled state"


# Test runner configuration
def run_checksum_e2e_tests():
    """Run the Checksum E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3"  # Stop after 3 failures
    ]

    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing if available
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass

    # Run the tests
    print("Starting Checksum End-to-End Tests...")
    exit_code = run_checksum_e2e_tests()

    print(f"\nChecksum E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)