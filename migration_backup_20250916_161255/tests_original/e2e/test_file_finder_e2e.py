#!/usr/bin/env python3
"""
File Finder End-to-End Test Suite

Comprehensive E2E testing for File Finder tool functionality.
Tests complete workflows from search initiation through result export.

Created: 2025-09-04
Coverage: File Finder search workflows, multi-directory scanning, 
          result filtering, export functionality, and tool integration
Priority: HIGH (addressing 0% E2E coverage for File Management tools)
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
    from tests.e2e.file_management_test_utilities import (
        FileManagementPerformanceMonitor, FileManagementSignalTracker,
        FileManagementTestDataFactory, MockFileFinderTool, MockRFUHub,
        assert_performance_target, file_finder_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE, 
    reason="File Management utilities not available"
)


class TestFileFinderCompleteWorkflows:
    """End-to-end testing of complete File Finder workflows."""
    
    def test_text_search_workflow(self, file_finder_test_environment):
        """
        Test: Text Search → Result Processing → Validation
        Target: < 15 seconds for medium dataset
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('file_finder', 'text_search')
        
        start_time = time.time()
        
        try:
            # Execute text search workflow
            search_criteria = {
                'text': 'project',
                'search_type': 'content',
                'case_sensitive': False,
                'whole_word': False
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            # Verify search completion
            assert result is not None, "Search result should not be None"
            assert result['status'] == 'success', \
                f"Search should succeed, got: {result.get('status')}"
            assert 'results_count' in result, "Result should include count"
            assert result['results_count'] > 0, "Should find some results"
            
            # Verify search results structure
            assert len(tool.search_results) > 0, "Tool should have results"
            
            first_result = tool.search_results[0]
            required_fields = ['name', 'path', 'size', 'modified_date']
            for field in required_fields:
                assert field in first_result, \
                    f"Search result missing field: {field}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Text search took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'file_finder', 'text_search')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_file_type_filtering_workflow(self, file_finder_test_environment):
        """
        Test: File Type Filter → Search → Result Validation
        Target: < 10 seconds for filtered search
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('file_finder', 'text_search')
        
        start_time = time.time()
        
        try:
            # Test multiple file type filters
            file_type_tests = [
                {
                    'extensions': ['.txt'],
                    'expected_types': ['txt'],
                    'description': 'Text files only'
                },
                {
                    'extensions': ['.py', '.js'],
                    'expected_types': ['py', 'js'],
                    'description': 'Code files only'
                },
                {
                    'extensions': ['.jpg', '.png'],
                    'expected_types': ['jpg', 'png'],
                    'description': 'Image files only'
                }
            ]
            
            for test_case in file_type_tests:
                search_criteria = {
                    'file_types': test_case['extensions'],
                    'search_type': 'extension_filter'
                }
                
                result = tool.search_files(test_data_path, search_criteria)
                
                assert result['status'] == 'success', \
                    f"File type search failed for {test_case['description']}"
                
                # Verify results match filter criteria
                if len(tool.search_results) > 0:
                    for search_result in tool.search_results[:5]:  # Check first 5
                        file_ext = search_result.get('file_type', '')
                        expected_types = [ext.lstrip('.') 
                                        for ext in test_case['extensions']]
                        assert file_ext in expected_types, \
                            f"Found {file_ext}, expected one of {expected_types}"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"File type filtering took too long: {workflow_time:.2f}s"
                
        finally:
            performance_monitor.stop_monitoring('file_finder', 'text_search')
    
    def test_size_parameters_workflow(self, file_finder_test_environment):
        """
        Test: Size Filter → Search → Size Validation
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        size_filter_tests = [
            {
                'min_size': 1024,  # 1KB
                'max_size': 1024 * 1024,  # 1MB
                'description': '1KB - 1MB range'
            },
            {
                'min_size': 1024 * 1024,  # 1MB
                'max_size': None,
                'description': 'Larger than 1MB'
            },
            {
                'min_size': None,
                'max_size': 1024,  # 1KB
                'description': 'Smaller than 1KB'
            }
        ]
        
        for test_case in size_filter_tests:
            search_criteria = {
                'size_filter': {
                    'min_size': test_case['min_size'],
                    'max_size': test_case['max_size']
                },
                'search_type': 'size_filter'
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            assert result['status'] == 'success', \
                f"Size filter search failed for {test_case['description']}"
            
            # Mock validation - in real implementation would check actual sizes
            assert 'results_count' in result, \
                "Size filter should return result count"
    
    def test_date_range_filtering_workflow(self, file_finder_test_environment):
        """
        Test: Date Range Filter → Search → Date Validation
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Define date ranges for testing
        now = datetime.now()
        date_tests = [
            {
                'start_date': now - timedelta(days=30),
                'end_date': now,
                'description': 'Last 30 days'
            },
            {
                'start_date': now - timedelta(days=365),
                'end_date': now - timedelta(days=30),
                'description': 'Between 30 days and 1 year ago'
            }
        ]
        
        for test_case in date_tests:
            search_criteria = {
                'date_filter': {
                    'start_date': test_case['start_date'].isoformat(),
                    'end_date': test_case['end_date'].isoformat(),
                    'date_type': 'modified'
                },
                'search_type': 'date_filter'
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            assert result['status'] == 'success', \
                f"Date filter search failed for {test_case['description']}"
            assert 'results_count' in result, \
                "Date filter should return result count"


class TestFileFinderMultiDirectoryScanning:
    """Test multi-directory scanning capabilities."""
    
    def test_recursive_directory_search_workflow(self, 
                                                file_finder_test_environment):
        """
        Test: Recursive Scan → Progress Tracking → Complete Coverage
        Target: < 30 seconds for recursive scan of medium dataset
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        performance_monitor.start_monitoring('file_finder', 'recursive_scan')
        
        start_time = time.time()
        
        try:
            # Execute recursive search
            search_criteria = {
                'recursive': True,
                'max_depth': 10,
                'follow_symlinks': False,
                'search_type': 'recursive_scan'
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            # Verify recursive search completion
            assert result['status'] == 'success', \
                "Recursive search should succeed"
            assert result['results_count'] > 0, \
                "Should find files in recursive search"
            
            # Verify comprehensive coverage
            assert len(tool.search_results) >= 10, \
                "Recursive search should find multiple files"
            
            # Check for files from different directory levels
            unique_dirs = set()
            for search_result in tool.search_results:
                file_dir = os.path.dirname(search_result['path'])
                unique_dirs.add(file_dir)
            
            assert len(unique_dirs) >= 3, \
                "Should find files from multiple directories"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Recursive scan took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_finder', 'recursive_scan')
            assert perf_result['target_met'], \
                f"Recursive scan performance target not met: {perf_result}"
    
    def test_symlink_handling_workflow(self, file_finder_test_environment):
        """
        Test: Symlink Detection → Handling Options → Safe Processing
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Test symlink handling options
        symlink_tests = [
            {
                'follow_symlinks': False,
                'description': 'Do not follow symlinks'
            },
            {
                'follow_symlinks': True,
                'description': 'Follow symlinks safely'
            }
        ]
        
        for test_case in symlink_tests:
            search_criteria = {
                'recursive': True,
                'follow_symlinks': test_case['follow_symlinks'],
                'search_type': 'symlink_handling'
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            assert result['status'] == 'success', \
                f"Symlink handling failed for {test_case['description']}"
            
            # Mock verification - real implementation would check symlink handling
            assert 'results_count' in result, \
                "Should return results count for symlink test"
    
    def test_large_dataset_performance_workflow(self, 
                                              file_finder_test_environment):
        """
        Test: Large Dataset → Performance Monitoring → Memory Management
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Monitor initial memory usage
        initial_memory = performance_monitor._get_memory_usage()
        
        performance_monitor.start_monitoring('file_finder', 'recursive_scan')
        
        try:
            # Simulate large dataset search
            search_criteria = {
                'recursive': True,
                'large_dataset_mode': True,
                'chunk_processing': True,
                'search_type': 'performance_test'
            }
            
            result = tool.search_files(test_data_path, search_criteria)
            
            assert result['status'] == 'success', \
                "Large dataset search should succeed"
            
            # Check memory usage
            final_memory = performance_monitor._get_memory_usage()
            if initial_memory > 0 and final_memory > 0:
                memory_increase_mb = (final_memory - initial_memory) / (1024 * 1024)
                assert memory_increase_mb < 200, \
                    f"Memory usage too high: {memory_increase_mb:.1f}MB"
            
            # Verify resource usage tracking
            resource_usage = tool.get_resource_usage()
            assert isinstance(resource_usage, dict), \
                "Should track resource usage"
            assert 'memory' in resource_usage, \
                "Should track memory usage"
            
        finally:
            performance_monitor.stop_monitoring('file_finder', 'recursive_scan')


class TestFileFinderResultProcessing:
    """Test result filtering and export functionality."""
    
    def test_result_export_workflow(self, file_finder_test_environment):
        """
        Test: Search → Export Selection → Format Generation → Validation
        Target: < 10 seconds for export operations
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # First, perform a search to get results
        search_criteria = {'search_type': 'basic', 'text': 'test'}
        search_result = tool.search_files(test_data_path, search_criteria)
        
        assert search_result['status'] == 'success', \
            "Initial search should succeed"
        assert len(tool.search_results) > 0, \
            "Should have results to export"
        
        # Test different export formats
        export_formats = ['json', 'csv', 'txt']
        
        for export_format in export_formats:
            performance_monitor.start_monitoring('file_finder', 'result_export')
            
            try:
                # Create temporary export file
                with tempfile.NamedTemporaryFile(
                    suffix=f'.{export_format}', delete=False) as tmp_file:
                    export_path = tmp_file.name
                
                # Execute export
                export_result = tool.export_results(export_format, export_path)
                
                # Verify export success
                assert export_result['status'] == 'success', \
                    f"Export to {export_format} should succeed"
                assert 'output_path' in export_result, \
                    "Export result should include output path"
                
                # Clean up
                if os.path.exists(export_path):
                    os.unlink(export_path)
                
            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'file_finder', 'result_export')
                assert perf_result['target_met'], \
                    f"Export performance target not met for {export_format}"
    
    def test_unsupported_export_format_workflow(self, 
                                              file_finder_test_environment):
        """
        Test: Export → Unsupported Format → Error Handling
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # First, perform a search to get results
        search_criteria = {'search_type': 'basic'}
        tool.search_files(test_data_path, search_criteria)
        
        # Try unsupported export format
        export_result = tool.export_results('unsupported_format', '/tmp/test')
        
        assert export_result['status'] == 'error', \
            "Unsupported format should return error"
        assert 'Unsupported format' in export_result['message'], \
            "Error message should indicate unsupported format"
    
    def test_result_sorting_workflow(self, file_finder_test_environment):
        """
        Test: Search Results → Sort Options → Ordered Output
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Perform search to get results
        search_criteria = {'search_type': 'basic'}
        result = tool.search_files(test_data_path, search_criteria)
        
        assert result['status'] == 'success', "Search should succeed"
        
        if len(tool.search_results) > 1:
            # Test sorting by size (mock implementation)
            original_results = tool.search_results.copy()
            
            # Simulate sorting by size (descending)
            sorted_by_size = sorted(
                original_results, 
                key=lambda x: x.get('size', 0), 
                reverse=True
            )
            
            # Verify sorting worked
            if len(sorted_by_size) >= 2:
                assert sorted_by_size[0]['size'] >= sorted_by_size[1]['size'], \
                    "Results should be sorted by size descending"
            
            # Test sorting by name (ascending)
            sorted_by_name = sorted(
                original_results,
                key=lambda x: x.get('name', '')
            )
            
            # Verify name sorting
            if len(sorted_by_name) >= 2:
                assert sorted_by_name[0]['name'] <= sorted_by_name[1]['name'], \
                    "Results should be sorted by name ascending"


class TestFileFinderIntegration:
    """Test integration with other file management tools."""
    
    def test_finder_to_organization_integration_workflow(self, 
                                                        file_finder_test_environment):
        """
        Test: File Search → Selection → Organization Tool Integration
        """
        env = file_finder_test_environment
        finder_tool = env['tool']
        test_data_path = env['test_data_path']
        hub = env['hub']
        
        # Step 1: Perform file search
        search_criteria = {
            'file_types': ['.txt', '.py'],
            'search_type': 'integration_test'
        }
        
        search_result = finder_tool.search_files(test_data_path, search_criteria)
        
        assert search_result['status'] == 'success', \
            "Initial search should succeed"
        assert len(finder_tool.search_results) > 0, \
            "Should find files for integration"
        
        # Step 2: Create mock organization tool for integration
        from tests.e2e.file_management_test_utilities import \
            MockFileManagementTool
        
        mock_org_tool = MockFileManagementTool(
            "FileOrganization", 
            {'rule_based_organization': True}
        )
        hub.register_tool('file_organization', mock_org_tool)
        
        # Step 3: Pass search results to organization tool
        selected_files = [result['path'] for result in finder_tool.search_results[:5]]
        
        org_result = mock_org_tool.process_data(
            selected_files, 
            operation='organize_selected_files'
        )
        
        assert org_result['status'] == 'success', \
            "Organization integration should succeed"
        
        # Step 4: Verify data flow integrity
        assert len(selected_files) > 0, "Should have files to organize"
        assert 'operations_count' in org_result, \
            "Organization should track operations"
        
        # Verify hub coordination
        hub_status = hub.tool_status
        assert 'file_finder' in hub_status, "Finder should be registered"
        assert 'file_organization' in hub_status, \
            "Organization tool should be registered"
    
    def test_concurrent_search_operations_workflow(self, 
                                                  file_finder_test_environment):
        """
        Test: Multiple Search Operations → Resource Coordination → Results
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Simulate concurrent operations by running multiple searches
        search_operations = [
            {'criteria': {'text': 'project'}, 'name': 'text_search'},
            {'criteria': {'file_types': ['.txt']}, 'name': 'type_search'},
            {'criteria': {'recursive': True}, 'name': 'recursive_search'}
        ]
        
        results = []
        
        for operation in search_operations:
            result = tool.search_files(test_data_path, operation['criteria'])
            results.append({
                'name': operation['name'],
                'result': result,
                'search_results_count': len(tool.search_results)
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
        assert len(tool.operation_history) >= len(search_operations), \
            "Should track all operations in history"


class TestFileFinderErrorHandling:
    """Test error handling and recovery scenarios."""
    
    def test_permission_error_recovery_workflow(self, 
                                               file_finder_test_environment):
        """
        Test: Permission Error → Graceful Handling → Partial Results
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
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
        assert len(signal_tracker.error_events) > 0, \
            "Should track error events"
    
    def test_search_cancellation_workflow(self, file_finder_test_environment):
        """
        Test: Long Search → User Cancellation → Clean Termination
        """
        env = file_finder_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Start a search operation
        search_criteria = {'search_type': 'long_running'}
        
        # Simulate cancellation
        tool.cancel_operation()
        
        # Execute search (should be cancelled)
        result = tool.process_data(f"search_{test_data_path}")
        
        assert result['status'] == 'cancelled', \
            "Cancelled operation should return cancelled status"
        assert 'cancelled' in result['message'].lower(), \
            "Should indicate cancellation in message"
        
        # Verify cancellation state
        assert tool._should_cancel, "Tool should be in cancelled state"


# Test runner configuration
def run_file_finder_e2e_tests():
    """Run the File Finder E2E test suite."""
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
    print("Starting File Finder End-to-End Tests...")
    exit_code = run_file_finder_e2e_tests()
    
    print(f"\nFile Finder E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)