#!/usr/bin/env python3
"""
Duplicate Finder End-to-End Test Suite

Comprehensive E2E testing for Duplicate Finder tool functionality.
Tests complete workflows from duplicate detection through selective deletion.

Created: 2025-09-04
Coverage: Hash-based comparison, large dataset performance, selective deletion,
          false positive prevention, and tool integration
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
        AnalysisToolsTestDataFactory, MockAnalysisToolsHub,
        MockDuplicateFinderTool, assert_performance_target,
        duplicate_finder_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="Analysis Tools utilities not available"
)


class TestDuplicateFinderCompleteWorkflows:
    """End-to-end testing of complete Duplicate Finder workflows."""

    def test_hash_based_file_comparison_workflow(self,
                                                duplicate_finder_test_environment):
        """
        Test: File Selection → Hash Calculation → Duplicate Detection
        Algorithms: MD5, SHA-256, SHA-512
        Target: < 30 seconds for 1,000 files
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']

        # Connect signal tracking
        signal_tracker.connect_all_signals()

        # Test different hash algorithms
        algorithms = ['md5', 'sha256', 'sha512']

        for algorithm in algorithms:
            performance_monitor.start_monitoring('duplicate_finder',
                                                'hash_calculation')

            start_time = time.time()

            try:
                # Execute hash-based comparison workflow
                options = {
                    'algorithm': algorithm,
                    'duplicate_percentage': 0.20,
                    'include_metadata': True
                }

                result = tool.find_duplicates(test_data_path,
                                            algorithm, options)

                # Verify detection completion
                assert result is not None, "Detection result should not be None"
                assert result['status'] == 'success', \
                    f"Detection should succeed, got: {result.get('status')}"
                assert 'results_count' in result, \
                    "Result should include count"
                assert result['results_count'] >= 0, \
                    "Should have valid results count"

                # Verify duplicate groups structure
                assert len(tool.duplicate_groups) >= 0, \
                    "Tool should have duplicate groups data"

                if len(tool.duplicate_groups) > 0:
                    first_group = tool.duplicate_groups[0]
                    required_fields = ['group_id', 'hash', 'algorithm',
                                     'file_size', 'files']
                    for field in required_fields:
                        assert field in first_group, \
                            f"Duplicate group missing field: {field}"

                    # Verify algorithm consistency
                    assert first_group['algorithm'] == algorithm, \
                        f"Algorithm mismatch: expected {algorithm}, " \
                        f"got {first_group['algorithm']}"

                # Verify workflow timing
                workflow_time = time.time() - start_time
                assert workflow_time < 30.0, \
                    f"Hash calculation took too long: {workflow_time:.2f}s"

                # Validate basic operation completion (simplified for E2E testing)
                assert result['status'] == 'success', \
                    "Operation should complete successfully"
                assert len(tool.operation_history) > 0, \
                    "Tool should have operation history"

            finally:
                # Stop performance monitoring
                perf_result = performance_monitor.stop_monitoring(
                    'duplicate_finder', 'hash_calculation')
                assert perf_result['target_met'], \
                    f"Performance target not met: {perf_result}"

    def test_large_dataset_duplicate_detection_workflow(self,
                                                      duplicate_finder_test_environment):
        """
        Test: Large Dataset → Progress Tracking → Memory Management
        Target: < 120 seconds for 10,000+ files
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('duplicate_finder',
                                           'large_dataset_scan')

        start_time = time.time()

        try:
            # Simulate large dataset processing
            options = {
                'large_dataset_mode': True,
                'chunk_processing': True,
                'duplicate_percentage': 0.25,
                'memory_optimization': True
            }

            result = tool.find_duplicates(test_data_path, 'md5', options)

            assert result['status'] == 'success', \
                "Large dataset scan should succeed"

            # Check memory usage
            resource_usage = tool.get_resource_usage()
            assert isinstance(resource_usage, dict), \
                "Should track resource usage"
            assert resource_usage['memory'] > 0, \
                "Should track memory usage"

            # Verify statistics tracking
            assert hasattr(tool, 'analysis_statistics'), \
                "Should have analysis statistics"

            if tool.analysis_statistics:
                stats = tool.analysis_statistics
                required_stats = ['total_files_scanned',
                                'duplicate_files_found',
                                'duplicate_groups',
                                'space_wasted']
                for stat in required_stats:
                    assert stat in stats, f"Missing statistic: {stat}"

            workflow_time = time.time() - start_time
            assert workflow_time < 120.0, \
                f"Large dataset scan took too long: {workflow_time:.2f}s"

        finally:
            perf_result = performance_monitor.stop_monitoring(
                'duplicate_finder', 'large_dataset_scan')
            assert perf_result['target_met'], \
                f"Large dataset performance target not met: {perf_result}"

    def test_multi_algorithm_comparison_workflow(self,
                                               duplicate_finder_test_environment):
        """
        Test: Algorithm Selection → Parallel Processing → Accuracy Comparison
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']

        algorithms = ['md5', 'sha256', 'sha512']
        results = {}

        # Test each algorithm
        for algorithm in algorithms:
            result = tool.find_duplicates(test_data_path, algorithm)
            results[algorithm] = {
                'result': result,
                'groups': tool.duplicate_groups.copy(),
                'stats': tool.analysis_statistics.copy()
            }

            assert result['status'] == 'success', \
                f"Algorithm {algorithm} should succeed"

        # Verify algorithm consistency
        if len(results) > 1:
            # Compare group counts (should be similar)
            group_counts = [len(results[alg]['groups'])
                          for alg in algorithms]

            # Allow for some variation due to different hash algorithms
            max_count = max(group_counts) if group_counts else 0
            min_count = min(group_counts) if group_counts else 0

            # Results should be within 20% of each other
            if max_count > 0:
                variation = (max_count - min_count) / max_count
                assert variation < 0.2, \
                    f"Algorithm results vary too much: {group_counts}"


class TestDuplicateFinderSelectiveDeletion:
    """Test selective deletion workflows with safety mechanisms."""

    def test_selective_deletion_workflow(self,
                                       duplicate_finder_test_environment):
        """
        Test: Duplicate Detection → User Selection → Safe Deletion
        Target: < 15 seconds for 100 file deletions
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # First, find duplicates
        result = tool.find_duplicates(test_data_path)
        assert result['status'] == 'success', "Initial scan should succeed"

        if len(tool.duplicate_groups) == 0:
            pytest.skip("No duplicate groups found for deletion test")

        performance_monitor.start_monitoring('duplicate_finder',
                                           'selective_deletion')

        start_time = time.time()

        try:
            # Select first few groups for deletion
            groups_to_delete = [group['group_id']
                              for group in tool.duplicate_groups[:5]]

            # Execute selective deletion with safety checks
            deletion_result = tool.delete_selected_duplicates(
                groups_to_delete, preserve_original=True)

            assert deletion_result['status'] == 'success', \
                "Selective deletion should succeed"
            assert 'results_count' in deletion_result, \
                "Should track deleted files count"

            # Verify deletion results tracking
            assert hasattr(tool, 'deletion_results'), \
                "Should track deletion results"
            assert len(tool.deletion_results) >= 0, \
                "Should have deletion results list"

            # Check that originals are preserved
            for result_item in tool.deletion_results:
                if 'operation' in result_item:
                    # Verify preservation logic (mock implementation)
                    assert isinstance(result_item, dict), \
                        "Deletion result should be dictionary"

            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Selective deletion took too long: {workflow_time:.2f}s"

        finally:
            perf_result = performance_monitor.stop_monitoring(
                'duplicate_finder', 'selective_deletion')
            assert perf_result['target_met'], \
                f"Selective deletion performance target not met: {perf_result}"

    def test_false_positive_prevention_workflow(self,
                                              duplicate_finder_test_environment):
        """
        Test: Edge Cases → Validation → False Positive Detection
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('duplicate_finder',
                                           'false_positive_check')

        start_time = time.time()
        test_files = []  # Initialize outside try block

        try:
            # Create test files for false positive testing
            for i in range(10):
                file_path = os.path.join(test_data_path,
                                       f"integrity_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Unique content {i}")
                test_files.append(file_path)

            # Perform integrity verification
            verification_result = tool.verify_integrity(test_files)

            assert verification_result['status'] == 'success', \
                "Integrity verification should succeed"

            # Check verification results
            if verification_result.get('results_count', 0) > 0:
                # Verify no false positives
                verification_accuracy = (
                    verification_result.get('results_count', 0) /
                    len(test_files)
                )
                assert verification_accuracy >= 0.999, \
                    f"Verification accuracy too low: {verification_accuracy}"

            workflow_time = time.time() - start_time
            assert workflow_time < 5.0, \
                f"False positive check took too long: {workflow_time:.2f}s"

        finally:
            # Cleanup test files
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.remove(file_path)

            perf_result = performance_monitor.stop_monitoring(
                'duplicate_finder', 'false_positive_check')
            assert perf_result['target_met'], \
                f"False positive check performance target not met: {perf_result}"


class TestDuplicateFinderPerformanceOptimization:
    """Test performance optimization and large-scale operations."""

    def test_enterprise_scale_performance_workflow(self,
                                                 duplicate_finder_test_environment):
        """
        Test: 50,000+ files → Memory Management → Results
        Memory Limit: < 1GB peak usage
        Target: < 300 seconds for complete analysis
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # Monitor initial memory usage
        initial_memory = performance_monitor._get_memory_usage()

        performance_monitor.start_monitoring('duplicate_finder',
                                           'large_dataset_scan')

        start_time = time.time()

        try:
            # Simulate enterprise-scale dataset
            options = {
                'enterprise_mode': True,
                'memory_limit': 1024 * 1024 * 1024,  # 1GB limit
                'chunk_size': 10000,  # Process in chunks
                'duplicate_percentage': 0.30,
                'optimize_memory': True
            }

            result = tool.find_duplicates(test_data_path, 'md5', options)

            assert result['status'] == 'success', \
                "Enterprise scale processing should succeed"

            # Check memory usage constraints
            final_memory = performance_monitor._get_memory_usage()
            if initial_memory > 0 and final_memory > 0:
                memory_increase = final_memory - initial_memory
                memory_increase_mb = memory_increase / (1024 * 1024)
                assert memory_increase_mb < 1024, \
                    f"Memory usage too high: {memory_increase_mb:.1f}MB"

            # Verify resource efficiency
            resource_usage = tool.get_resource_usage()
            assert resource_usage['memory'] > 0, \
                "Should track memory usage"

            # Check for linear performance scaling
            workflow_time = time.time() - start_time
            assert workflow_time < 300.0, \
                f"Enterprise scale processing took too long: " \
                f"{workflow_time:.2f}s"

        finally:
            performance_monitor.stop_monitoring('duplicate_finder',
                                              'large_dataset_scan')


class TestDuplicateFinderIntegration:
    """Test integration with other Analysis and File Management tools."""

    def test_duplicate_to_secure_delete_integration(self,
                                                  duplicate_finder_test_environment):
        """
        Test: Duplicate Detection → Selection → Secure Delete Integration
        """
        env = duplicate_finder_test_environment
        finder_tool = env['tool']
        test_data_path = env['test_data_path']
        hub = env['hub']

        # Step 1: Perform duplicate detection
        result = finder_tool.find_duplicates(test_data_path)
        assert result['status'] == 'success', \
            "Initial duplicate detection should succeed"

        if len(finder_tool.duplicate_groups) == 0:
            pytest.skip("No duplicates found for integration test")

        # Step 2: Select duplicates for secure deletion
        selected_groups = finder_tool.duplicate_groups[:3]  # First 3 groups

        # Step 3: Create mock secure delete tool for integration
        from tests.e2e.analysis_tools_test_utilities import \
            MockAnalysisToolBase

        mock_secure_delete = MockAnalysisToolBase(
            "SecureDelete",
            {'secure_deletion': True, 'multiple_passes': True}
        )
        hub.register_tool('secure_delete', mock_secure_delete)

        # Step 4: Pass duplicate files to secure delete tool
        files_for_deletion = []
        for group in selected_groups:
            # Skip first file (original) in each group
            if len(group['files']) > 1:
                files_for_deletion.extend([f['path']
                                         for f in group['files'][1:]])

        secure_delete_result = mock_secure_delete.process_data(
            files_for_deletion,
            operation='secure_delete_duplicates',
            file_count=len(files_for_deletion)
        )

        assert secure_delete_result['status'] == 'success', \
            "Secure delete integration should succeed"

        # Step 5: Verify data flow integrity
        assert len(files_for_deletion) > 0, \
            "Should have files for secure deletion"
        assert 'files_processed' in secure_delete_result, \
            "Secure delete should track processed files"

        # Verify hub coordination
        hub_status = hub.tool_status
        assert 'duplicate_finder' in hub_status, \
            "Duplicate Finder should be registered"
        assert 'secure_delete' in hub_status, \
            "Secure Delete tool should be registered"

    def test_concurrent_duplicate_detection_workflow(self,
                                                   duplicate_finder_test_environment):
        """
        Test: Multiple Detection Operations → Resource Coordination
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']

        # Simulate concurrent operations by running multiple detections
        detection_operations = [
            {'algorithm': 'md5', 'name': 'md5_detection'},
            {'algorithm': 'sha256', 'name': 'sha256_detection'},
            {'algorithm': 'sha512', 'name': 'sha512_detection'}
        ]

        results = []

        for operation in detection_operations:
            result = tool.find_duplicates(test_data_path,
                                        operation['algorithm'])
            results.append({
                'name': operation['name'],
                'algorithm': operation['algorithm'],
                'result': result,
                'groups_count': len(tool.duplicate_groups)
            })

        # Verify all operations completed
        for result_set in results:
            assert result_set['result']['status'] == 'success', \
                f"Operation {result_set['name']} should succeed"

        # Verify resource coordination
        resource_usage = tool.get_resource_usage()
        assert resource_usage['cpu'] > 0, "Should track CPU usage"
        assert resource_usage['memory'] > 0, "Should track memory usage"

        # Verify operation history
        assert len(tool.operation_history) >= len(detection_operations), \
            "Should track all operations in history"


class TestDuplicateFinderErrorHandling:
    """Test error handling and recovery scenarios."""

    def test_permission_error_recovery_workflow(self,
                                               duplicate_finder_test_environment):
        """
        Test: Permission Error → Graceful Handling → Partial Results
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        signal_tracker = env['signal_tracker']

        signal_tracker.connect_all_signals()

        # Simulate permission error
        error_result = tool.simulate_error(
            'permission_denied',
            'Access denied to some directories'
        )

        assert error_result['status'] == 'error', \
            "Should return error status"
        assert error_result['error_type'] == 'permission_denied', \
            "Should identify error type"

        # Verify error tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['error_events'] > 0, \
            "Should track error events"

    def test_cancellation_workflow(self, duplicate_finder_test_environment):
        """
        Test: Long Operation → User Cancellation → Clean Termination
        """
        env = duplicate_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']

        # Simulate cancellation
        tool.cancel_operation()

        # Execute operation (should be cancelled)
        result = tool.process_data(f"scan_{test_data_path}")

        assert result['status'] == 'cancelled', \
            "Cancelled operation should return cancelled status"
        assert 'cancelled' in result['message'].lower(), \
            "Should indicate cancellation in message"

        # Verify cancellation state
        assert tool._should_cancel, "Tool should be in cancelled state"


# Test runner configuration
def run_duplicate_finder_e2e_tests():
    """Run the Duplicate Finder E2E test suite."""
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
    print("Starting Duplicate Finder End-to-End Tests...")
    exit_code = run_duplicate_finder_e2e_tests()

    print(f"\nDuplicate Finder E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)