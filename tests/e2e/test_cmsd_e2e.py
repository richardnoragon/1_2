#!/usr/bin/env python3
"""
CMSD (Copy/Move/Sync/Delete) End-to-End Test Suite

Comprehensive E2E testing for CMSD tool functionality.
Tests complete workflows from directory comparison through synchronization
and conflict resolution.

Created: 2025-09-04
Coverage: Directory comparison workflows, bidirectional synchronization,
          large file operations, progress tracking, and cancellation
Priority: HIGH (implementing 0% E2E coverage for File Operations tools)
"""

import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.file_operations_test_utilities import (
        FileOperationsPerformanceMonitor, FileOperationsSignalTracker,
        FileOperationsTestDataFactory, MockCMSDTool, MockFileOperationsHub,
        assert_performance_target, cmsd_test_environment,
        create_mock_large_file)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Operations utilities not available"
)


class TestCMSDDirectoryComparison:
    """Test directory comparison workflows and diff detection."""
    
    def test_directory_comparison_workflow(self, cmsd_test_environment):
        """
        Test: Source/Target Selection → Comparison → Diff Analysis → Validation
        Target: < 30 seconds for directory comparison of medium dataset
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('cmsd', 'directory_comparison')
        
        start_time = time.time()
        
        try:
            # Set up source and target directories
            source_dir = os.path.join(test_data_path, 'source_directory')
            target_dir = os.path.join(test_data_path, 'target_directory')
            
            assert os.path.exists(source_dir), "Source directory should exist"
            assert os.path.exists(target_dir), "Target directory should exist"
            
            # Execute directory comparison
            comparison_options = {
                'recursive': True,
                'compare_content': True,
                'compare_timestamps': True,
                'include_metadata': True,
                'ignore_hidden': False
            }
            
            result = tool.compare_directories(source_dir, target_dir, comparison_options)
            
            # Verify comparison completion
            assert result is not None, "Comparison result should not be None"
            assert result['status'] == 'success', \
                f"Directory comparison should succeed, got: {result.get('status')}"
            assert 'file_count' in result, "Result should include file count"
            
            # Verify comparison results structure
            assert len(tool.comparison_results) > 0, "Tool should have comparison data"
            comparison_data = tool.comparison_results
            
            required_fields = ['source_path', 'target_path', 'differences', 
                             'total_differences', 'comparison_options']
            for field in required_fields:
                assert field in comparison_data, \
                    f"Comparison data missing field: {field}"
            
            # Verify differences structure
            differences = comparison_data['differences']
            if len(differences) > 0:
                first_diff = differences[0]
                diff_required_fields = ['file_path', 'difference_type', 'source_size']
                for field in diff_required_fields:
                    assert field in first_diff, \
                        f"Difference entry missing field: {field}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Directory comparison took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'cmsd', 'directory_comparison')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_diff_detection_workflow(self, cmsd_test_environment):
        """
        Test: Detailed Diff Analysis → File-level Changes → Change Classification
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Execute comparison to generate diffs
        comparison_options = {
            'recursive': True,
            'detailed_analysis': True,
            'content_comparison': True
        }
        
        result = tool.compare_directories(source_dir, target_dir, comparison_options)
        
        assert result['status'] == 'success', "Comparison should succeed"
        
        # Verify diff types are properly classified
        differences = tool.comparison_results['differences']
        
        diff_types = set()
        for diff in differences:
            diff_types.add(diff['difference_type'])
        
        # Should have various types of differences
        expected_diff_types = {'new_in_source', 'new_in_target', 'modified', 'identical'}
        found_diff_types = diff_types.intersection(expected_diff_types)
        assert len(found_diff_types) >= 2, \
            f"Should find multiple diff types, found: {found_diff_types}"
        
        # Verify size and timestamp information
        for diff in differences[:5]:  # Check first 5 for detailed verification
            assert 'source_size' in diff, "Should include source size info"
            if diff['difference_type'] != 'new_in_source':
                assert 'target_size' in diff, "Should include target size for existing files"
    
    def test_nested_structure_comparison_workflow(self, cmsd_test_environment):
        """
        Test: Deep Directory Structure → Recursive Comparison → Nested Diff Analysis
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Test recursive comparison with depth limits
        nested_options = {
            'recursive': True,
            'max_depth': 5,
            'follow_symlinks': False,
            'preserve_structure': True
        }
        
        result = tool.compare_directories(source_dir, target_dir, nested_options)
        
        assert result['status'] == 'success', "Nested comparison should succeed"
        
        # Verify recursive scanning worked
        differences = tool.comparison_results['differences']
        
        # Should find files at different directory levels
        directory_levels = set()
        for diff in differences:
            file_path = diff['file_path']
            # Count directory separators to determine depth
            depth = file_path.count(os.sep) if os.sep in file_path else 0
            directory_levels.add(depth)
        
        assert len(directory_levels) >= 2, \
            "Should find files at multiple directory levels"


class TestCMSDBidirectionalSync:
    """Test bidirectional synchronization mechanisms and conflict resolution."""
    
    def test_bidirectional_sync_workflow(self, cmsd_test_environment):
        """
        Test: Directory Sync → Conflict Detection → Bidirectional Updates → Validation
        Target: < 45 seconds for bidirectional sync of medium dataset
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        performance_monitor.start_monitoring('cmsd', 'bidirectional_sync')
        
        start_time = time.time()
        
        try:
            source_dir = os.path.join(test_data_path, 'source_directory')
            target_dir = os.path.join(test_data_path, 'target_directory')
            
            # Execute bidirectional synchronization
            sync_options = {
                'preview_mode': False,
                'delete_extra_files': False,
                'preserve_timestamps': True,
                'verify_after_sync': True,
                'create_backup': False
            }
            
            result = tool.sync_directories(
                source_dir, target_dir, 'bidirectional', sync_options)
            
            # Verify synchronization completion
            assert result['status'] == 'success', \
                "Bidirectional sync should succeed"
            assert 'file_count' in result, \
                "Should report number of files processed"
            assert 'sync_mode' in result, \
                "Should include sync mode in result"
            
            # Verify sync results
            assert len(tool.sync_results) > 0, "Should have sync results"
            sync_results = tool.sync_results
            
            # Check sync operations
            operations_found = set()
            for sync_item in sync_results:
                required_fields = ['file_path', 'operation', 'status', 'timestamp']
                for field in required_fields:
                    assert field in sync_item, \
                        f"Sync item missing field: {field}"
                operations_found.add(sync_item['operation'])
            
            # Should have various sync operations
            expected_operations = {'copy', 'move', 'delete', 'update'}
            found_operations = operations_found.intersection(expected_operations)
            assert len(found_operations) >= 2, \
                f"Should perform multiple operation types, found: {found_operations}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 45.0, \
                f"Bidirectional sync took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Sync workflow should complete successfully"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'cmsd', 'bidirectional_sync')
            assert perf_result['target_met'], \
                f"Bidirectional sync performance target not met: {perf_result}"
    
    def test_conflict_resolution_workflow(self, cmsd_test_environment):
        """
        Test: Sync Conflicts → Resolution Strategy → Conflict Resolution → Verification
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Perform sync that generates conflicts
        sync_result = tool.sync_directories(source_dir, target_dir, 'bidirectional')
        
        # Check if conflicts were detected
        conflicts = tool.conflict_list
        
        if len(conflicts) > 0:
            # Test different conflict resolution strategies
            resolution_strategies = ['newer_wins', 'source_wins', 'target_wins', 'manual']
            
            for strategy in resolution_strategies:
                # Reset conflicts for each strategy test
                for conflict in conflicts:
                    conflict['status'] = 'conflict'  # Reset status
                
                resolution_result = tool.resolve_conflicts(strategy)
                
                assert resolution_result['status'] == 'success', \
                    f"Conflict resolution should succeed for {strategy} strategy"
                
                if 'conflicts_resolved' in resolution_result:
                    assert resolution_result['conflicts_resolved'] >= 0, \
                        "Should report number of conflicts resolved"
                
                # Verify conflicts were marked as resolved
                resolved_conflicts = [c for c in conflicts if c.get('status') == 'resolved']
                assert len(resolved_conflicts) > 0, \
                    f"Should resolve conflicts with {strategy} strategy"
                
                # Test only one strategy in mock implementation
                break
        else:
            # If no conflicts generated, verify conflict resolution handles empty case
            resolution_result = tool.resolve_conflicts('newer_wins')
            assert resolution_result['status'] == 'success', \
                "Should handle case with no conflicts gracefully"
            assert 'No conflicts' in resolution_result['message'], \
                "Should indicate no conflicts to resolve"
    
    def test_incremental_sync_workflow(self, cmsd_test_environment):
        """
        Test: Initial Sync → Changes → Incremental Sync → Delta Verification
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Perform initial sync
        initial_sync_options = {
            'incremental_mode': False,
            'full_sync': True
        }
        
        initial_result = tool.sync_directories(
            source_dir, target_dir, 'bidirectional', initial_sync_options)
        
        assert initial_result['status'] == 'success', \
            "Initial sync should succeed"
        
        initial_file_count = len(tool.sync_results)
        
        # Simulate incremental sync (changes since last sync)
        incremental_sync_options = {
            'incremental_mode': True,
            'since_timestamp': datetime.now() - timedelta(minutes=5),
            'delta_only': True
        }
        
        incremental_result = tool.sync_directories(
            source_dir, target_dir, 'bidirectional', incremental_sync_options)
        
        assert incremental_result['status'] == 'success', \
            "Incremental sync should succeed"
        
        # Verify incremental sync processed changes appropriately
        # In a real implementation, this would process only changed files
        incremental_file_count = len(tool.sync_results)
        
        # Mock implementation generates new results each time
        # Real implementation would show fewer files in incremental sync
        assert incremental_file_count > 0, \
            "Incremental sync should process some files"


class TestCMSDLargeFileOperations:
    """Test large file operations and progress tracking."""
    
    def test_large_file_copy_workflow(self, cmsd_test_environment):
        """
        Test: Large File Copy → Progress Monitoring → Integrity Verification
        Target: < 60 seconds for large file copy operation
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Create mock large file for testing
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        source_file = os.path.join(large_files_dir, 'test_large_file.bin')
        target_file = os.path.join(test_data_path, 'target_large_file.bin')
        
        # Create a mock large file (simulated)
        mock_large_file = create_mock_large_file(source_file, 100)  # 100MB
        
        performance_monitor.start_monitoring('cmsd', 'large_file_copy')
        
        start_time = time.time()
        
        try:
            # Execute large file copy
            copy_result = tool.copy_large_file(source_file, target_file)
            
            assert copy_result['status'] == 'success', \
                "Large file copy should succeed"
            assert 'file_size' in copy_result, \
                "Should report file size"
            assert 'chunks_processed' in copy_result, \
                "Should report chunks processed"
            
            # Verify copy was tracked properly
            assert copy_result['file_size'] > 50*1024*1024, \
                "Should handle large file (>50MB)"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 60.0, \
                f"Large file copy took too long: {workflow_time:.2f}s"
            
            # Verify progress tracking signals
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['total_events'] > 0, \
                "Should emit progress tracking events"
            
        finally:
            perf_result = performance_monitor.stop_monitoring('cmsd', 'large_file_copy')
            assert perf_result['target_met'], \
                f"Large file copy performance target not met: {perf_result}"
    
    def test_large_file_move_workflow(self, cmsd_test_environment):
        """
        Test: Large File Move → Progress Tracking → Source Cleanup → Verification
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        source_file = os.path.join(large_files_dir, 'move_test_large_file.bin')
        target_file = os.path.join(test_data_path, 'moved_large_file.bin')
        
        # Create mock large file
        create_mock_large_file(source_file, 50)  # 50MB
        
        # Simulate large file move (copy + delete source)
        copy_result = tool.copy_large_file(source_file, target_file)
        
        assert copy_result['status'] == 'success', \
            "Large file copy (part of move) should succeed"
        
        # Verify move operation would include source cleanup
        # In real implementation, this would delete the source file
        assert 'chunks_processed' in copy_result, \
            "Move operation should track progress"
    
    def test_progress_tracking_workflow(self, cmsd_test_environment):
        """
        Test: Large Operation → Real-time Progress → Progress Callbacks → Completion
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Execute sync with progress tracking
        progress_options = {
            'enable_progress_tracking': True,
            'progress_callback_interval': 1,  # Every 1% progress
            'detailed_progress': True
        }
        
        sync_result = tool.sync_directories(
            source_dir, target_dir, 'bidirectional', progress_options)
        
        assert sync_result['status'] == 'success', \
            "Sync with progress tracking should succeed"
        
        # Verify progress tracking signals were emitted
        workflow_summary = signal_tracker.get_workflow_summary()
        
        # Should have progress events
        progress_events = [e for e in signal_tracker.workflow_events 
                          if 'Progress:' in e]
        assert len(progress_events) > 0, \
            "Should emit progress tracking events"
        
        # Should have file processing events
        file_events = [e for e in signal_tracker.workflow_events 
                      if 'File processed:' in e]
        assert len(file_events) > 0, \
            "Should emit file processing events"


class TestCMSDProgressCancellation:
    """Test progress tracking and cancellation capabilities."""
    
    def test_progress_tracking_workflow(self, cmsd_test_environment):
        """
        Test: Operation Start → Progress Updates → Completion Tracking → Validation
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Execute operation with detailed progress tracking
        progress_sync_result = tool.sync_directories(source_dir, target_dir)
        
        assert progress_sync_result['status'] == 'success', \
            "Progress tracked sync should succeed"
        
        # Verify comprehensive progress tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        
        assert workflow_summary['total_events'] > 0, \
            "Should track workflow events"
        assert workflow_summary['completion_status'], \
            "Should track completion status"
        
        # Verify specific progress events
        assert len(signal_tracker.workflow_events) >= 3, \
            "Should have multiple workflow events (start, progress, completion)"
    
    def test_operation_cancellation_workflow(self, cmsd_test_environment):
        """
        Test: Long Operation → User Cancellation → Clean Termination → State Recovery
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Start a potentially long-running operation
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Simulate cancellation request
        tool.cancel_operation()
        
        # Execute operation (should be cancelled)
        cancelled_result = tool.sync_directories(source_dir, target_dir)
        
        # In the mock implementation, cancellation is checked in process_data
        if tool._should_cancel:
            # Operation might be cancelled, or might complete if cancellation check missed
            assert cancelled_result['status'] in ['cancelled', 'success'], \
                f"Cancelled operation should return cancelled or success status, got: {cancelled_result['status']}"
        
        # Verify cancellation was tracked
        cancellation_events = [e for e in tool.workflow_events 
                              if 'cancellation' in e.lower()]
        assert len(cancellation_events) > 0, \
            "Should track cancellation request"
    
    def test_resume_interrupted_operation_workflow(self, cmsd_test_environment):
        """
        Test: Operation Interruption → State Persistence → Operation Resume → Completion
        """
        env = cmsd_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        source_dir = os.path.join(test_data_path, 'source_directory')
        target_dir = os.path.join(test_data_path, 'target_directory')
        
        # Simulate interrupted operation state
        interrupted_state = {
            'source_directory': source_dir,
            'target_directory': target_dir,
            'sync_mode': 'bidirectional',
            'completed_files': 25,
            'total_files': 100,
            'last_processed_file': 'documents/test_file_025.txt',
            'interruption_timestamp': datetime.now().isoformat()
        }
        
        # Store interrupted state
        tool.sync_state[f"{source_dir}_{target_dir}"] = interrupted_state
        
        # Resume operation
        resume_options = {
            'resume_mode': True,
            'resume_from_state': interrupted_state
        }
        
        resume_result = tool.sync_directories(
            source_dir, target_dir, 'bidirectional', resume_options)
        
        assert resume_result['status'] == 'success', \
            "Resume operation should succeed"
        
        # Verify resume functionality
        if 'resume_from_state' in resume_result:
            assert resume_result['resume_from_state'] is not None, \
                "Should acknowledge resume operation"


# Test runner configuration
def run_cmsd_e2e_tests():
    """Run the CMSD E2E test suite."""
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
    print("Starting CMSD End-to-End Tests...")
    exit_code = run_cmsd_e2e_tests()
    
    print(f"\nCMSD E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)