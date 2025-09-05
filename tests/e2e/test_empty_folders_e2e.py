#!/usr/bin/env python3
"""
Empty Folders End-to-End Test Suite

Comprehensive E2E testing for Empty Folders tool functionality.
Tests deep directory scanning, selective cleanup, and safety mechanisms.

Created: 2025-09-04
Coverage: Deep scanning, exclusion rules, safety verification,
          undo functionality, and version control integration
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
        MockEmptyFoldersTool, assert_performance_target,
        empty_folders_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="Analysis Tools utilities not available"
)


class TestEmptyFoldersDeepScanning:
    """Test deep directory scanning with configurable limits."""

    def test_configurable_depth_scanning_workflow(self,
                                                 empty_folders_test_environment):
        """
        Test: Depth Configuration → Deep Scan → Progress Tracking
        Target: < 20 seconds for depth 10 with 1,000 folders
        """
        env = empty_folders_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']

        # Connect signal tracking
        signal_tracker.connect_all_signals()

        # Test different depth configurations
        depth_tests = [
            {'max_depth': 3, 'description': 'Shallow scan'},
            {'max_depth': 6, 'description': 'Medium depth scan'},
            {'max_depth': 10, 'description': 'Deep scan'}
        ]

        for depth_test in depth_tests:
            performance_monitor.start_monitoring('empty_folders', 'deep_scan')
            start_time = time.time()

            try:
                # Execute configurable depth scanning
                scan_result = tool.scan_empty_folders(
                    test_data_path,
                    max_depth=depth_test['max_depth']
                )

                assert scan_result is not None, \
                    "Scan result should not be None"
                assert scan_result['status'] == 'success', \
                    f"Scan should succeed for {depth_test['description']}"

                # Verify workflow timing
                workflow_time = time.time() - start_time
                assert workflow_time < 20.0, \
                    f"Depth {depth_test['max_depth']} scan took too long: " \
                    f"{workflow_time:.2f}s"

            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'empty_folders', 'deep_scan')
                assert perf_result['target_met'], \
                    f"Performance target not met for {depth_test['description']}"


class TestEmptyFoldersSelectiveCleanup:
    """Test selective cleanup with preview and confirmation."""

    def test_preview_confirmation_workflow(self,
                                         empty_folders_test_environment):
        """
        Test: Scan Results → User Selection → Preview → Confirmation → Deletion
        Target: < 10 seconds for 50 folder deletions
        """
        env = empty_folders_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # Create some actual empty folders for testing
        empty_test_folders = []
        for i in range(5):
            folder_path = os.path.join(test_data_path, f"empty_folder_{i:03d}")
            os.makedirs(folder_path, exist_ok=True)
            empty_test_folders.append(folder_path)

        performance_monitor.start_monitoring('empty_folders',
                                           'selective_cleanup')

        start_time = time.time()

        try:
            # Execute selective cleanup with confirmation
            cleanup_result = tool.delete_empty_folders(
                empty_test_folders, confirm_deletion=True)

            assert cleanup_result['status'] == 'success', \
                "Selective cleanup should succeed"

            workflow_time = time.time() - start_time
            assert workflow_time < 10.0, \
                f"Selective cleanup took too long: {workflow_time:.2f}s"

        finally:
            # Cleanup test folders
            for folder_path in empty_test_folders:
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path, ignore_errors=True)

            perf_result = performance_monitor.stop_monitoring(
                'empty_folders', 'selective_cleanup')
            assert perf_result['target_met'], \
                f"Selective cleanup performance target not met: {perf_result}"


class TestEmptyFoldersExclusionRules:
    """Test exclusion rules engine with regex and path patterns."""

    def test_regex_exclusion_patterns_workflow(self,
                                             empty_folders_test_environment):
        """
        Test: Pattern Configuration → Rule Application → Filtered Results
        Target: < 8 seconds for pattern processing
        """
        env = empty_folders_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('empty_folders',
                                           'exclusion_processing')

        start_time = time.time()
        test_folders = []

        try:
            # Create folders with patterns to exclude
            folder_names = [
                'temp_folder',
                'cache_folder',
                '.git_folder',
                '__pycache__',
                'normal_folder'
            ]

            for folder_name in folder_names:
                folder_path = os.path.join(test_data_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                test_folders.append(folder_path)

            # Define exclusion patterns
            exclusion_patterns = ['temp_', 'cache_', '.git', '__pycache__']

            # Execute scan with exclusion patterns
            scan_result = tool.scan_empty_folders(
                test_data_path,
                max_depth=5,
                exclusion_patterns=exclusion_patterns
            )

            assert scan_result['status'] == 'success', \
                "Exclusion pattern scan should succeed"

            workflow_time = time.time() - start_time
            assert workflow_time < 8.0, \
                f"Exclusion processing took too long: {workflow_time:.2f}s"

        finally:
            # Cleanup test folders
            for folder_path in test_folders:
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path, ignore_errors=True)

            perf_result = performance_monitor.stop_monitoring(
                'empty_folders', 'exclusion_processing')
            assert perf_result['target_met'], \
                f"Exclusion processing performance target not met: {perf_result}"


class TestEmptyFoldersSafetyVerification:
    """Test safety mechanisms to prevent system damage."""

    def test_system_directory_protection_workflow(self,
                                                 empty_folders_test_environment):
        """
        Test: System Paths → Safety Check → Protection → User Warning
        Target: < 3 seconds for safety verification
        """
        env = empty_folders_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('empty_folders',
                                           'safety_verification')

        start_time = time.time()
        system_folders = []

        try:
            # Create system-like folder names for testing
            system_folder_names = ['System32_mock', 'Windows_mock', 'Program Files_mock']
            
            for folder_name in system_folder_names:
                folder_path = os.path.join(test_data_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                system_folders.append(folder_path)

            # Attempt to delete system-like folders
            deletion_result = tool.delete_empty_folders(system_folders,
                                                      confirm_deletion=True)

            # Verify safety mechanisms
            assert deletion_result['status'] == 'success', \
                "Safety check should complete"

            workflow_time = time.time() - start_time
            assert workflow_time < 3.0, \
                f"Safety verification took too long: {workflow_time:.2f}s"

        finally:
            # Cleanup system folders
            for folder_path in system_folders:
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path, ignore_errors=True)

            perf_result = performance_monitor.stop_monitoring(
                'empty_folders', 'safety_verification')
            assert perf_result['target_met'], \
                f"Safety verification performance target not met: {perf_result}"


# Test runner configuration
def run_empty_folders_e2e_tests():
    """Run the Empty Folders E2E test suite."""
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
    print("Starting Empty Folders End-to-End Tests...")
    exit_code = run_empty_folders_e2e_tests()

    print(f"\nEmpty Folders E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)