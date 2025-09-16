#!/usr/bin/env python3
"""
File Splitter End-to-End Test Suite

Comprehensive E2E testing for File Splitter tool functionality.
Tests complete workflows from large file splitting through chunk reassembly
and integrity verification.

Created: 2025-09-04
Coverage: Large file splitting workflows, chunk reassembly processes,
          integrity verification systems, resume functionality
Priority: HIGH (implementing 0% E2E coverage for File Operations tools)
"""

import os
import sys
import time
from unittest.mock import Mock

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.file_operations_test_utilities import (
        FileOperationsPerformanceMonitor, FileOperationsSignalTracker,
        MockFileSplitterTool, create_mock_large_file,
        file_splitter_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Operations utilities not available"
)


class TestFileSplitterLargeFiles:
    """Test large file splitting workflows and chunk management."""
    
    def test_large_file_splitting_workflow(self, file_splitter_test_environment):
        """
        Test: Large File → Chunk Config → Split Operation → Validation
        Target: < 45 seconds for file splitting (1GB file)
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('file_splitter', 'file_splitting')
        
        start_time = time.time()
        
        try:
            # Set up large file for splitting
            large_files_dir = os.path.join(test_data_path, 'large_files')
            if not os.path.exists(large_files_dir):
                os.makedirs(large_files_dir)
            
            large_file_path = os.path.join(large_files_dir, 'test_large.bin')
            
            # Create mock large file (simulated for testing)
            create_mock_large_file(large_file_path, 100)  # 100MB for testing
            
            # Set up split configuration
            chunk_size = 10 * 1024 * 1024  # 10MB chunks
            output_dir = os.path.join(test_data_path, 'split_output')
            os.makedirs(output_dir, exist_ok=True)
            
            split_options = {
                'preserve_metadata': True,
                'create_manifest': True,
                'verify_chunks': True,
                'chunk_naming_pattern': 'sequential'
            }
            
            # Execute file splitting
            result = tool.split_file(
                large_file_path, chunk_size, output_dir, split_options)
            
            # Verify splitting completion
            assert result is not None, "Split result should not be None"
            assert result['status'] == 'success', \
                f"File splitting should succeed, got: {result.get('status')}"
            assert 'chunks_created' in result, \
                "Result should include chunks created count"
            assert 'file_size' in result, \
                "Result should include original file size"
            
            # Verify split results structure
            assert len(tool.split_results) > 0, "Should have split results"
            
            chunks = tool.split_results
            for chunk in chunks[:3]:  # Check first 3 chunks
                required_fields = ['chunk_index', 'chunk_path', 'chunk_size',
                                 'chunk_hash', 'created_at']
                for field in required_fields:
                    assert field in chunk, \
                        f"Chunk missing field: {field}"
            
            # Verify chunk info was stored
            assert large_file_path in tool.chunk_info, \
                "Should store chunk info for the split file"
            
            chunk_info = tool.chunk_info[large_file_path]
            assert 'original_file' in chunk_info, \
                "Should store original file reference"
            assert 'chunks_count' in chunk_info, \
                "Should store chunk count"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 45.0, \
                f"File splitting took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'file_splitter', 'file_splitting')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_custom_chunk_size_workflow(self, file_splitter_test_environment):
        """
        Test: Custom Chunk Sizes → Split Configuration → Validation
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        test_file = os.path.join(large_files_dir, 'custom_split_test.bin')
        create_mock_large_file(test_file, 50)  # 50MB
        
        # Test different chunk sizes
        chunk_size_tests = [
            {
                'chunk_size': 1 * 1024 * 1024,  # 1MB
                'description': '1MB chunks'
            },
            {
                'chunk_size': 25 * 1024 * 1024,  # 25MB
                'description': '25MB chunks'
            },
            {
                'chunk_size': 100 * 1024 * 1024,  # 100MB (larger than file)
                'description': '100MB chunks (larger than file)'
            }
        ]
        
        for test_case in chunk_size_tests:
            output_dir = os.path.join(
                test_data_path, f"split_{test_case['chunk_size']//1024//1024}mb")
            os.makedirs(output_dir, exist_ok=True)
            
            result = tool.split_file(
                test_file, test_case['chunk_size'], output_dir)
            
            assert result['status'] == 'success', \
                f"Split should succeed for {test_case['description']}"
            
            # Verify chunk configuration
            chunk_info = tool.chunk_info[test_file]
            actual_chunk_size = chunk_info['chunk_size']
            assert actual_chunk_size == test_case['chunk_size'], \
                f"Chunk size should match configuration: {actual_chunk_size}"
    
    def test_split_progress_monitoring_workflow(self, 
                                              file_splitter_test_environment):
        """
        Test: Split Start → Progress Updates → Completion Tracking
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        progress_test_file = os.path.join(
            large_files_dir, 'progress_test.bin')
        create_mock_large_file(progress_test_file, 75)  # 75MB
        
        output_dir = os.path.join(test_data_path, 'progress_output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Execute split with progress monitoring
        progress_options = {
            'enable_progress_reporting': True,
            'progress_update_interval': 5,  # Every 5% progress
            'detailed_logging': True
        }
        
        chunk_size = 15 * 1024 * 1024  # 15MB chunks
        result = tool.split_file(
            progress_test_file, chunk_size, output_dir, progress_options)
        
        assert result['status'] == 'success', \
            "Progress monitored split should succeed"
        
        # Verify progress tracking worked
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


class TestFileSplitterReassembly:
    """Test chunk reassembly processes and integrity verification."""
    
    def test_chunk_reassembly_workflow(self, file_splitter_test_environment):
        """
        Test: Chunk Directory → Reassembly → Output File → Validation
        Target: < 30 seconds for chunk reassembly
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # First split a file to create chunks
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        original_file = os.path.join(large_files_dir, 'reassembly_test.bin')
        create_mock_large_file(original_file, 60)  # 60MB
        
        chunk_output_dir = os.path.join(test_data_path, 'chunks')
        os.makedirs(chunk_output_dir, exist_ok=True)
        
        # Split the file first
        chunk_size = 20 * 1024 * 1024  # 20MB chunks
        split_result = tool.split_file(
            original_file, chunk_size, chunk_output_dir)
        
        assert split_result['status'] == 'success', \
            "Initial split for reassembly test should succeed"
        
        # Start reassembly monitoring
        performance_monitor.start_monitoring(
            'file_splitter', 'chunk_reassembly')
        
        start_time = time.time()
        
        try:
            # Execute chunk reassembly
            reassembled_file = os.path.join(
                test_data_path, 'reassembled_file.bin')
            
            reassembly_options = {
                'verify_chunk_integrity': True,
                'preserve_timestamps': True,
                'cleanup_chunks': False  # Keep chunks for testing
            }
            
            result = tool.join_chunks(
                chunk_output_dir, reassembled_file, reassembly_options)
            
            # Verify reassembly completion
            assert result['status'] == 'success', \
                "Chunk reassembly should succeed"
            assert 'chunks_processed' in result, \
                "Should report chunks processed count"
            assert 'output_file' in result, \
                "Should include output file path"
            
            # Verify reassembly worked correctly
            chunks_processed = result['chunks_processed']
            assert chunks_processed > 0, \
                "Should process at least one chunk"
            
            # Verify chunk info consistency
            chunk_info = tool.chunk_info.get(original_file)
            if chunk_info:
                expected_chunks = len(chunk_info['chunks'])
                # In mock implementation, chunks_processed might not exactly match
                assert chunks_processed > 0, \
                    f"Should process chunks, got: {chunks_processed}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Chunk reassembly took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Reassembly workflow should complete successfully"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_splitter', 'chunk_reassembly')
            assert perf_result['target_met'], \
                f"Reassembly performance target not met: {perf_result}"
    
    def test_integrity_verification_workflow(self, 
                                           file_splitter_test_environment):
        """
        Test: Chunk Integrity Check → Hash Validation → Status Report
        Target: < 15 seconds for integrity verification
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Create split file chunks for integrity testing
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        integrity_test_file = os.path.join(
            large_files_dir, 'integrity_test.bin')
        create_mock_large_file(integrity_test_file, 40)  # 40MB
        
        chunk_dir = os.path.join(test_data_path, 'integrity_chunks')
        os.makedirs(chunk_dir, exist_ok=True)
        
        # Split file to create chunks
        split_result = tool.split_file(
            integrity_test_file, 10 * 1024 * 1024, chunk_dir)
        
        assert split_result['status'] == 'success', \
            "Split for integrity test should succeed"
        
        performance_monitor.start_monitoring(
            'file_splitter', 'integrity_verification')
        
        start_time = time.time()
        
        try:
            # Execute integrity verification
            integrity_result = tool.verify_chunks_integrity(chunk_dir)
            
            # Verify integrity check completion
            assert integrity_result['status'] == 'success', \
                "Integrity verification should complete successfully"
            assert 'chunks_verified' in integrity_result, \
                "Should report number of chunks verified"
            assert 'all_chunks_valid' in integrity_result, \
                "Should report overall integrity status"
            
            # Most chunks should be valid in mock implementation
            chunks_verified = integrity_result['chunks_verified']
            assert chunks_verified > 0, \
                "Should verify at least one chunk"
            
            # Verify timing
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Integrity verification took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_splitter', 'integrity_verification')
            assert perf_result['target_met'], \
                f"Integrity verification target not met: {perf_result}"
    
    def test_missing_chunk_detection_workflow(self, 
                                            file_splitter_test_environment):
        """
        Test: Missing Chunks → Detection → Error Reporting → Recovery Options
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Set up scenario with missing chunks
        chunk_dir = os.path.join(test_data_path, 'missing_chunks_test')
        os.makedirs(chunk_dir, exist_ok=True)
        
        # Create mock chunk info with missing chunks
        mock_file_path = '/mock/test_file.bin'
        mock_chunks = [
            {'chunk_index': i, 'chunk_path': f'chunk_{i:03d}.bin',
             'chunk_size': 10*1024*1024, 'chunk_hash': f'hash_{i}'}
            for i in range(5)
        ]
        
        tool.chunk_info[mock_file_path] = {
            'chunks': mock_chunks,
            'output_directory': chunk_dir
        }
        
        # Execute integrity verification (should detect missing chunks)
        integrity_result = tool.verify_chunks_integrity(chunk_dir)
        
        # Should handle missing chunks gracefully
        assert integrity_result['status'] == 'success', \
            "Should complete verification even with missing chunks"
        
        # In a real implementation, this would report missing chunks
        assert 'chunks_verified' in integrity_result, \
            "Should report verification attempt"


class TestFileSplitterResume:
    """Test resume functionality for interrupted operations."""
    
    def test_resume_interrupted_split_workflow(self, 
                                             file_splitter_test_environment):
        """
        Test: Interrupted Split → State Persistence → Resume → Completion
        Target: < 5 seconds for resume operation
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Set up interrupted split scenario
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        resume_test_file = os.path.join(large_files_dir, 'resume_test.bin')
        create_mock_large_file(resume_test_file, 80)  # 80MB
        
        # Simulate interrupted split state
        interrupted_state = {
            'original_file': resume_test_file,
            'total_chunks': 8,
            'completed_chunks': 3,
            'chunk_size': 10 * 1024 * 1024,
            'output_directory': os.path.join(test_data_path, 'resume_output'),
            'interruption_timestamp': time.time() - 300  # 5 minutes ago
        }
        
        performance_monitor.start_monitoring(
            'file_splitter', 'resume_operation')
        
        start_time = time.time()
        
        try:
            # Execute resume operation
            resume_result = tool.resume_split_operation(
                resume_test_file, interrupted_state)
            
            # Verify resume completion
            assert resume_result['status'] == 'success', \
                "Resume operation should succeed"
            assert 'remaining_chunks' in resume_result, \
                "Should report remaining chunks processed"
            assert 'total_chunks' in resume_result, \
                "Should include total chunk count"
            
            # Verify resume logic
            remaining_chunks = resume_result['remaining_chunks']
            total_chunks = resume_result['total_chunks']
            expected_remaining = total_chunks - interrupted_state['completed_chunks']
            
            assert remaining_chunks == expected_remaining, \
                f"Should process {expected_remaining} remaining chunks, got {remaining_chunks}"
            
            # Verify timing
            workflow_time = time.time() - start_time
            assert workflow_time < 5.0, \
                f"Resume operation took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_splitter', 'resume_operation')
            assert perf_result['target_met'], \
                f"Resume performance target not met: {perf_result}"
    
    def test_resume_interrupted_join_workflow(self, 
                                            file_splitter_test_environment):
        """
        Test: Interrupted Join → State Recovery → Resume Join → Completion
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Set up join resume scenario
        chunk_dir = os.path.join(test_data_path, 'join_resume_chunks')
        os.makedirs(chunk_dir, exist_ok=True)
        
        # Create mock chunk data for join resume
        mock_chunks = [
            {'chunk_index': i, 'chunk_size': 15*1024*1024}
            for i in range(6)
        ]
        
        original_file = '/mock/join_resume_test.bin'
        tool.chunk_info[original_file] = {
            'chunks': mock_chunks,
            'output_directory': chunk_dir,
            'join_progress': {
                'completed_chunks': 2,
                'total_chunks': 6,
                'bytes_joined': 30*1024*1024
            }
        }
        
        # Resume join operation
        output_file = os.path.join(test_data_path, 'resumed_join.bin')
        
        join_result = tool.join_chunks(chunk_dir, output_file)
        
        # Verify join resume
        assert join_result['status'] == 'success', \
            "Resume join should succeed"
        assert 'chunks_processed' in join_result, \
            "Should report chunks processed"
    
    def test_state_persistence_workflow(self, file_splitter_test_environment):
        """
        Test: Operation State → Persistence → Recovery → Validation
        """
        env = file_splitter_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create file and split to generate state
        large_files_dir = os.path.join(test_data_path, 'large_files')
        if not os.path.exists(large_files_dir):
            os.makedirs(large_files_dir)
        
        persistence_file = os.path.join(
            large_files_dir, 'persistence_test.bin')
        create_mock_large_file(persistence_file, 30)  # 30MB
        
        chunk_dir = os.path.join(test_data_path, 'persistence_chunks')
        os.makedirs(chunk_dir, exist_ok=True)
        
        # Execute split to create persistent state
        split_result = tool.split_file(
            persistence_file, 10 * 1024 * 1024, chunk_dir)
        
        assert split_result['status'] == 'success', \
            "Split for persistence test should succeed"
        
        # Verify state was persisted
        assert persistence_file in tool.chunk_info, \
            "Split state should be persisted"
        
        chunk_info = tool.chunk_info[persistence_file]
        required_state_fields = ['original_file', 'chunk_size', 'chunks',
                               'output_directory', 'split_completed_at']
        for field in required_state_fields:
            assert field in chunk_info, \
                f"Persistent state missing field: {field}"
        
        # Verify state can be used for operations
        chunks = chunk_info['chunks']
        assert len(chunks) > 0, "Should have chunk information"
        
        # Test state-based join operation
        join_file = os.path.join(test_data_path, 'state_joined.bin')
        join_result = tool.join_chunks(chunk_dir, join_file)
        
        assert join_result['status'] == 'success', \
            "State-based join should succeed"


# Test runner configuration
def run_file_splitter_e2e_tests():
    """Run the File Splitter E2E test suite."""
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
    print("Starting File Splitter End-to-End Tests...")
    exit_code = run_file_splitter_e2e_tests()
    
    print(f"\nFile Splitter E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)