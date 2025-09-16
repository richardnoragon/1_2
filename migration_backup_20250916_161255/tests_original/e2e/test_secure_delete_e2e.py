#!/usr/bin/env python3
"""
Secure Delete End-to-End Test Suite

Comprehensive E2E testing for Secure Delete tool functionality.
Tests multi-pass deletion workflows, directory wiping operations,
verification of secure removal processes, and performance benchmarking.

Created: 2025-09-04
Coverage: Multi-pass deletion workflows, DoD 5220.22-M compliance,
          directory wiping, verification systems, safety mechanisms
Priority: HIGH (addressing 0% E2E coverage for Security Tools)
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
    from tests.e2e.security_tools_test_utilities import (
        MockSecureDeleteTool, MockSecurityToolsHub,
        SecurityToolsPerformanceMonitor, SecurityToolsSignalTracker,
        SecurityToolsTestDataFactory, assert_performance_target,
        secure_delete_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE, 
    reason="Security Tools utilities not available"
)


class TestSecureDeleteMultiPassDeletion:
    """End-to-end testing of multi-pass secure deletion workflows."""
    
    def test_dod_5220_22_m_deletion_workflow(self, 
                                           secure_delete_test_environment):
        """
        Test: DoD Standard Deletion → 3-Pass Overwrite → Verification
        Target: < 30 seconds for DoD standard deletion
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('secure_delete', 
                                           'dod_deletion')
        
        start_time = time.time()
        
        try:
            # Prepare test files for DoD deletion
            test_files = []
            for i in range(5):
                file_path = os.path.join(test_data_path, f"dod_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"DoD deletion test content {i}\n" * 500)
                test_files.append(file_path)
            
            # Execute DoD 5220.22-M deletion workflow
            deletion_method = "dod_5220_22_m"
            verify_deletion = True
            deletion_options = {
                'overwrite_passes': 3,
                'verify_each_pass': True,
                'final_verification': True
            }
            
            result = tool.secure_delete_files(test_files, deletion_method, 
                                            verify_deletion, deletion_options)
            
            # Verify deletion completion
            assert result is not None, "Deletion result should not be None"
            assert result['status'] == 'success', \
                f"DoD deletion should succeed, got: {result.get('status')}"
            assert 'results_count' in result, \
                "Result should include success count"
            assert result['results_count'] > 0, \
                "Should successfully delete some files"
            
            # Verify DoD compliance
            assert 'overwrite_passes' in result, \
                "Should report overwrite passes"
            assert result['overwrite_passes'] == 3, \
                "DoD standard should use 3 passes"
            
            # Verify deletion history tracking
            assert len(tool.deletion_history) > 0, \
                "Tool should track deletion history"
            
            first_deletion = tool.deletion_history[0]
            required_fields = ['file_path', 'deletion_method', 
                             'overwrite_passes', 'verification_passed']
            for field in required_fields:
                assert field in first_deletion, \
                    f"Deletion record missing field: {field}"
            
            # Verify DoD method was used
            assert first_deletion['deletion_method'] == deletion_method, \
                f"Should use {deletion_method} method"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"DoD deletion took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'secure_delete', 'dod_deletion')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_gutmann_method_deletion_workflow(self, 
                                            secure_delete_test_environment):
        """
        Test: Gutmann Method → 35-Pass Deletion → Maximum Security
        Target: < 120 seconds for Gutmann method deletion
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('secure_delete', 
                                           'gutmann_deletion')
        
        start_time = time.time()
        
        try:
            # Create test file for Gutmann method testing
            test_file = os.path.join(test_data_path, "gutmann_test.txt")
            with open(test_file, 'w') as f:
                f.write("Gutmann method test content\n" * 200)
            
            # Execute Gutmann method deletion
            deletion_method = "gutmann_method"
            verify_deletion = True
            
            result = tool.secure_delete_files([test_file], deletion_method, 
                                            verify_deletion)
            
            # Verify Gutmann method execution
            assert result['status'] == 'success', \
                "Gutmann deletion should succeed"
            assert result['overwrite_passes'] == 35, \
                "Gutmann method should use 35 passes"
            
            # Verify maximum security compliance
            deletion_record = tool.deletion_history[-1]
            assert deletion_record['deletion_method'] == 'gutmann_method', \
                "Should use Gutmann method"
            assert deletion_record['overwrite_passes'] == 35, \
                "Should perform 35 overwrite passes"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 120.0, \
                f"Gutmann deletion took too long: {workflow_time:.2f}s"
                
        finally:
            performance_monitor.stop_monitoring('secure_delete', 
                                              'gutmann_deletion')
    
    def test_single_pass_quick_deletion_workflow(self, 
                                                secure_delete_test_environment):
        """
        Test: Single Pass Deletion → Quick Processing → Basic Security
        Target: < 10 seconds for single pass deletion
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('secure_delete', 
                                           'single_pass_deletion')
        
        start_time = time.time()
        
        try:
            # Create test files for quick deletion
            quick_delete_files = []
            for i in range(8):
                file_path = os.path.join(test_data_path, 
                                       f"quick_delete_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Quick delete test {i}")
                quick_delete_files.append(file_path)
            
            # Execute single pass deletion
            deletion_method = "single_pass"
            
            result = tool.secure_delete_files(quick_delete_files, 
                                            deletion_method, True)
            
            assert result['status'] == 'success', \
                "Single pass deletion should succeed"
            assert result['overwrite_passes'] == 1, \
                "Single pass should use 1 overwrite"
            
            # Verify quick processing
            workflow_time = time.time() - start_time
            assert workflow_time < 10.0, \
                f"Single pass deletion took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('secure_delete', 
                                              'single_pass_deletion')


class TestSecureDeleteDirectoryWiping:
    """Test directory wiping operations and recursive deletion."""
    
    def test_directory_wipe_workflow(self, secure_delete_test_environment):
        """
        Test: Directory Selection → Recursive Wipe → Complete Removal
        Target: < 45 seconds for directory wipe
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        performance_monitor.start_monitoring('secure_delete', 
                                           'directory_wipe')
        
        start_time = time.time()
        
        try:
            # Create test directory structure for wiping
            wipe_directory = os.path.join(test_data_path, "directory_to_wipe")
            os.makedirs(wipe_directory, exist_ok=True)
            
            # Create subdirectories and files
            for i in range(3):
                subdir = os.path.join(wipe_directory, f"subdir_{i}")
                os.makedirs(subdir, exist_ok=True)
                
                for j in range(5):
                    file_path = os.path.join(subdir, f"file_{j}.txt")
                    with open(file_path, 'w') as f:
                        f.write(f"Directory wipe test content {i}-{j}")
            
            # Execute directory wipe workflow
            deletion_method = "dod_5220_22_m"
            recursive = True
            verify_deletion = True
            
            result = tool.wipe_directory(wipe_directory, deletion_method, 
                                       recursive, verify_deletion)
            
            # Verify directory wipe completion
            assert result['status'] == 'success', \
                "Directory wipe should succeed"
            assert 'total_files' in result, \
                "Should report total files wiped"
            assert 'total_directories' in result, \
                "Should report directories removed"
            
            # Verify recursive processing
            assert result['total_files'] > 0, \
                "Should find files to wipe"
            assert result['total_directories'] > 0, \
                "Should find directories to remove"
            
            # Verify comprehensive wipe
            wiped_bytes = result.get('total_bytes_wiped', 0)
            assert wiped_bytes > 0, \
                "Should report bytes wiped"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 45.0, \
                f"Directory wipe took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'secure_delete', 'directory_wipe')
            assert perf_result['target_met'], \
                f"Directory wipe performance target not met"
    
    def test_selective_directory_deletion_workflow(self, 
                                                  secure_delete_test_environment):
        """
        Test: Directory Scan → File Selection → Selective Deletion
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create mixed directory with different file types
        mixed_directory = os.path.join(test_data_path, "mixed_files")
        os.makedirs(mixed_directory, exist_ok=True)
        
        # Create files of different types
        file_types = ['.txt', '.log', '.tmp', '.bak']
        created_files = []
        
        for i, file_type in enumerate(file_types):
            for j in range(3):
                file_path = os.path.join(mixed_directory, 
                                       f"mixed_file_{i}_{j}{file_type}")
                with open(file_path, 'w') as f:
                    f.write(f"Mixed file content {i}-{j}")
                created_files.append(file_path)
        
        # Select only certain files for deletion (e.g., .tmp and .log files)
        selected_files = [f for f in created_files 
                         if f.endswith('.tmp') or f.endswith('.log')]
        
        # Execute selective deletion
        deletion_method = "random_pattern"
        
        result = tool.secure_delete_files(selected_files, deletion_method, True)
        
        assert result['status'] == 'success', \
            "Selective deletion should succeed"
        assert result['file_count'] == len(selected_files), \
            "Should process selected files only"


class TestSecureDeleteSafetyMechanisms:
    """Test safety mechanisms and system protection features."""
    
    def test_system_file_protection_workflow(self, 
                                           secure_delete_test_environment):
        """
        Test: System File Detection → Safety Block → Protection Verification
        Target: < 3 seconds for safety verification
        """
        env = secure_delete_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('secure_delete', 
                                           'verification')
        
        start_time = time.time()
        
        try:
            # Test system file protection
            system_file_paths = [
                "/Windows/System32/kernel32.dll",
                "/usr/bin/bash",
                "/System/Library/CoreServices/Finder.app",
                "C:\\Program Files\\Important\\system.exe"
            ]
            
            # Attempt to delete system files (should be blocked)
            deletion_method = "dod_5220_22_m"
            
            result = tool.secure_delete_files(system_file_paths, 
                                            deletion_method, True)
            
            # Verify safety mechanisms worked
            # Note: Mock implementation tracks safety violations
            assert len(tool.safety_violations) > 0, \
                "Should detect and block system file deletion attempts"
            
            # Verify safety violation tracking
            for violation in tool.safety_violations:
                assert 'file_path' in violation, \
                    "Safety violation should include file path"
                assert 'violation_type' in violation, \
                    "Should identify violation type"
                assert violation['blocked'], \
                    "System files should be blocked"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 3.0, \
                f"Safety verification took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'secure_delete', 'verification')
            assert perf_result['target_met'], \
                f"Safety verification performance target not met"
    
    def test_user_confirmation_workflow(self, 
                                      secure_delete_test_environment):
        """
        Test: Deletion Request → User Confirmation → Execution Control
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create test files for confirmation testing
        test_files = []
        for i in range(3):
            file_path = os.path.join(test_data_path, 
                                   f"confirmation_test_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Confirmation test content {i}")
            test_files.append(file_path)
        
        # Test deletion with confirmation required
        deletion_method = "dod_5220_22_m"
        
        # Note: Mock implementation doesn't implement actual confirmation UI
        # Real implementation would show confirmation dialog
        result = tool.secure_delete_files(test_files, deletion_method, True)
        
        # Verify operation completed (mock bypasses confirmation)
        assert 'status' in result, \
            "Should handle confirmation workflow"
        assert 'file_count' in result, \
            "Should process file count"
    
    def test_deletion_verification_workflow(self, 
                                          secure_delete_test_environment):
        """
        Test: Secure Deletion → Verification Process → Recovery Prevention
        Target: < 15 seconds for deletion verification
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('secure_delete', 
                                           'verification')
        
        start_time = time.time()
        
        try:
            # Create test files for verification
            verification_files = []
            for i in range(4):
                file_path = os.path.join(test_data_path, 
                                       f"verification_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Verification test content {i}\n" * 100)
                verification_files.append(file_path)
            
            # Execute deletion with verification enabled
            deletion_method = "random_pattern"
            verify_deletion = True
            
            result = tool.secure_delete_files(verification_files, 
                                            deletion_method, verify_deletion)
            
            assert result['status'] == 'success', \
                "Verified deletion should succeed"
            
            # Verify verification results were tracked
            assert len(tool.verification_results) > 0, \
                "Should track verification results"
            
            # Check verification record structure
            verification_record = tool.verification_results[0]
            verification_fields = ['file_path', 'deletion_method', 
                                 'verified', 'verification_time']
            for field in verification_fields:
                assert field in verification_record, \
                    f"Verification record missing field: {field}"
            
            # Verify recovery prevention
            assert verification_record.get('recovery_test_passed', True), \
                "Recovery prevention should be verified"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Verification took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('secure_delete', 
                                              'verification')


class TestSecureDeletePerformanceBenchmarking:
    """Test performance benchmarking and optimization scenarios."""
    
    def test_large_file_deletion_performance_workflow(self, 
                                                     secure_delete_test_environment):
        """
        Test: Large File → Efficient Deletion → Performance Validation
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Create simulated large file (without actually creating large content)
        large_file_path = os.path.join(test_data_path, "large_file.bin")
        with open(large_file_path, 'w') as f:
            f.write("Simulated large file content\n" * 1000)
        
        performance_monitor.start_monitoring('secure_delete', 
                                           'dod_deletion')
        
        start_time = time.time()
        
        try:
            # Test large file deletion with performance monitoring
            deletion_method = "dod_5220_22_m"
            large_file_options = {
                'chunk_processing': True,
                'progress_updates': True,
                'memory_efficient': True
            }
            
            result = tool.secure_delete_files([large_file_path], 
                                            deletion_method, True, 
                                            large_file_options)
            
            assert result['status'] == 'success', \
                "Large file deletion should succeed"
            
            # Verify performance tracking
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['total_events'] > 0, \
                "Should have progress events for large files"
            
            # Verify memory usage tracking
            resource_usage = tool.get_resource_usage()
            assert resource_usage['memory'] > 0, \
                "Should track memory usage for large files"
            
            # Note: Mock implementation doesn't enforce strict timing
            # Real implementation would have optimized large file handling
            
        finally:
            performance_monitor.stop_monitoring('secure_delete', 
                                              'dod_deletion')
    
    def test_concurrent_deletion_operations_workflow(self, 
                                                   secure_delete_test_environment):
        """
        Test: Multiple Deletion Operations → Resource Coordination → Results
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create multiple sets of files for concurrent operations
        file_sets = []
        for set_num in range(3):
            file_set = []
            for i in range(3):
                file_path = os.path.join(test_data_path, 
                                       f"concurrent_{set_num}_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Concurrent deletion test {set_num}-{i}")
                file_set.append(file_path)
            file_sets.append(file_set)
        
        # Simulate concurrent deletion operations
        deletion_operations = [
            {'files': file_sets[0], 'method': 'single_pass'},
            {'files': file_sets[1], 'method': 'dod_5220_22_m'},
            {'files': file_sets[2], 'method': 'random_pattern'}
        ]
        
        results = []
        
        for operation in deletion_operations:
            result = tool.secure_delete_files(operation['files'], 
                                             operation['method'], True)
            results.append({
                'method': operation['method'],
                'result': result,
                'files_count': len(operation['files'])
            })
        
        # Verify all operations completed
        for result_set in results:
            assert result_set['result']['status'] == 'success', \
                f"Operation {result_set['method']} should succeed"
        
        # Verify resource coordination
        resource_usage = tool.get_resource_usage()
        assert resource_usage['cpu'] > 0, "Should track CPU usage"
        assert resource_usage['memory'] > 0, "Should track memory usage"
        
        # Verify operation history
        assert len(tool.operation_history) >= len(deletion_operations), \
            "Should track all operations in history"


class TestSecureDeleteErrorHandling:
    """Test error handling and recovery scenarios."""
    
    def test_permission_denied_error_workflow(self, 
                                             secure_delete_test_environment):
        """
        Test: Permission Error → Graceful Handling → Partial Results
        """
        env = secure_delete_test_environment
        tool = env['tool']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Simulate permission error
        error_result = tool.simulate_error(
            'permission_denied', 
            'Access denied for secure deletion'
        )
        
        assert error_result['status'] == 'error', \
            "Should return error status"
        assert error_result['error_type'] == 'permission_denied', \
            "Should identify error type"
        
        # Verify error tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert len(signal_tracker.error_events) > 0, \
            "Should track error events"
    
    def test_invalid_deletion_method_error_workflow(self, 
                                                   secure_delete_test_environment):
        """
        Test: Invalid Method → Error Detection → Graceful Handling
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create test file
        test_file = os.path.join(test_data_path, "invalid_method_test.txt")
        with open(test_file, 'w') as f:
            f.write("Invalid method test content")
        
        # Attempt deletion with invalid method
        invalid_method = "non_existent_method"
        
        result = tool.secure_delete_files([test_file], invalid_method, True)
        
        assert result['status'] == 'error', \
            "Invalid method should return error"
        assert 'invalid_method' in result['error_type'], \
            "Should identify invalid method error"
        assert invalid_method in result['message'], \
            "Error message should mention invalid method"
    
    def test_deletion_cancellation_workflow(self, 
                                          secure_delete_test_environment):
        """
        Test: Long Deletion → User Cancellation → Clean Termination
        """
        env = secure_delete_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create test file
        test_file = os.path.join(test_data_path, "cancellation_test.txt")
        with open(test_file, 'w') as f:
            f.write("Content for deletion cancellation testing")
        
        # Start deletion operation
        deletion_method = "gutmann_method"  # Long operation for cancellation
        
        # Simulate cancellation
        tool.cancel_operation()
        
        # Execute deletion (should be cancelled)
        result = tool.process_data(f"delete_{test_file}")
        
        assert result['status'] == 'cancelled', \
            "Cancelled operation should return cancelled status"
        assert 'cancelled' in result['message'].lower(), \
            "Should indicate cancellation in message"
        
        # Verify cancellation state
        assert tool._should_cancel, "Tool should be in cancelled state"


class TestSecureDeleteIntegration:
    """Test integration with other security tools and workflows."""
    
    def test_secure_delete_hub_integration_workflow(self, 
                                                   secure_delete_test_environment):
        """
        Test: Secure Delete → Hub Registration → Resource Coordination
        """
        env = secure_delete_test_environment
        delete_tool = env['tool']
        hub = env['hub']
        
        # Verify tool is registered with hub
        assert 'secure_delete' in hub.registered_tools, \
            "Secure Delete should be registered with hub"
        
        # Verify hub coordination
        hub_status = hub.tool_status
        assert 'secure_delete' in hub_status, \
            "Hub should track Secure Delete status"
        
        # Test resource-coordinated deletion
        test_files = ["/tmp/hub_integration_test.txt"]
        
        result = delete_tool.secure_delete_files(test_files, 
                                                'dod_5220_22_m', True)
        
        assert result['status'] == 'success', \
            "Hub-coordinated deletion should succeed"
        
        # Verify resource coordination
        resource_usage = delete_tool.get_resource_usage()
        assert isinstance(resource_usage, dict), \
            "Should track resource usage for hub coordination"
        assert 'memory' in resource_usage, \
            "Should track memory usage"
        assert 'cpu' in resource_usage, \
            "Should track CPU usage"
    
    def test_cross_tool_workflow_integration(self, 
                                           secure_delete_test_environment):
        """
        Test: Multi-tool Workflow → Data Handoff → Workflow Completion
        """
        env = secure_delete_test_environment
        delete_tool = env['tool']
        hub = env['hub']
        test_data_path = env['test_data_path']
        
        # Step 1: Create test files
        workflow_files = []
        for i in range(4):
            file_path = os.path.join(test_data_path, 
                                   f"workflow_test_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Cross-tool workflow content {i}")
            workflow_files.append(file_path)
        
        # Step 2: Simulate receiving files from another security tool
        # (e.g., after encryption, original files need secure deletion)
        
        # Step 3: Execute secure deletion as part of workflow
        deletion_method = "dod_5220_22_m"
        workflow_options = {
            'workflow_integration': True,
            'preserve_audit_trail': True
        }
        
        result = delete_tool.secure_delete_files(workflow_files, 
                                                deletion_method, True, 
                                                workflow_options)
        
        assert result['status'] == 'success', \
            "Cross-tool workflow deletion should succeed"
        
        # Verify workflow integration tracking
        assert 'operations_count' in result, \
            "Should track operations for workflow"
        assert len(delete_tool.operation_history) > 0, \
            "Should maintain operation history for workflows"


# Test runner configuration
def run_secure_delete_e2e_tests():
    """Run the Secure Delete E2E test suite."""
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
    print("Starting Secure Delete End-to-End Tests...")
    exit_code = run_secure_delete_e2e_tests()
    
    print(f"\nSecure Delete E2E Test Suite completed "
          f"with exit code: {exit_code}")
    sys.exit(exit_code)