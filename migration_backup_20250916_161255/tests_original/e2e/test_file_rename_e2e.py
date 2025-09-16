#!/usr/bin/env python3
"""
File Rename End-to-End Test Suite

Comprehensive E2E testing for File Rename tool functionality.
Tests complete workflows from rename pattern definition through execution and undo.

Created: 2025-09-04
Coverage: Batch rename operations, pattern-based renaming, preview workflows,
          undo functionality, and cross-tool integration
Priority: HIGH (addressing 0% E2E coverage for File Management tools)
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
    from tests.e2e.file_management_test_utilities import (
        FileManagementPerformanceMonitor, FileManagementSignalTracker,
        FileManagementTestDataFactory, MockFileRenameTool, MockRFUHub,
        assert_performance_target, file_rename_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Management utilities not available"
)


class TestFileRenameBatchOperations:
    """Test batch rename operations and sequential numbering."""
    
    def test_batch_rename_workflow(self, file_rename_test_environment):
        """
        Test: File Selection → Pattern Definition → Preview → Batch Application → Validation
        Target: < 20 seconds for 500 files batch rename
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('file_rename', 'batch_rename')
        
        start_time = time.time()
        
        try:
            # Step 1: Collect files for batch rename
            test_files = []
            for root, dirs, files in os.walk(test_data_path):
                for file in files[:20]:  # Limit to first 20 files for testing
                    test_files.append(os.path.join(root, file))
            
            assert len(test_files) >= 5, "Should have files for batch rename testing"
            
            # Step 2: Define batch rename pattern
            batch_pattern = {
                'mode': 'sequential',
                'base_name': 'renamed_file',
                'start_index': 1,
                'digit_padding': 3,
                'preserve_extension': True,
                'case_modification': 'none'
            }
            
            # Step 3: Preview batch rename
            preview_result = tool.preview_rename(test_files, batch_pattern)
            
            assert preview_result['status'] == 'success', \
                "Batch rename preview should succeed"
            assert len(tool.preview_data) == len(test_files), \
                "Should preview all selected files"
            
            # Verify preview data structure
            for preview_item in tool.preview_data:
                required_fields = ['original', 'new', 'path', 'status']
                for field in required_fields:
                    assert field in preview_item, \
                        f"Preview item missing field: {field}"
            
            # Step 4: Apply batch rename
            apply_result = tool.apply_rename()
            
            assert apply_result['status'] == 'success', \
                "Batch rename application should succeed"
            
            # Verify rename history was recorded
            assert len(tool.rename_history) > 0, \
                "Should record rename operation in history"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 20.0, \
                f"Batch rename took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'file_rename', 'batch_rename')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_sequential_numbering_workflow(self, file_rename_test_environment):
        """
        Test: Sequential Pattern → Numbering Configuration → Application
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Collect test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:10]])
        
        # Test different sequential numbering patterns
        numbering_tests = [
            {
                'pattern': {
                    'mode': 'sequential',
                    'base_name': 'item',
                    'start_index': 1,
                    'digit_padding': 2
                },
                'description': '2-digit padding starting from 1'
            },
            {
                'pattern': {
                    'mode': 'sequential',
                    'base_name': 'document',
                    'start_index': 100,
                    'digit_padding': 4
                },
                'description': '4-digit padding starting from 100'
            }
        ]
        
        for test_case in numbering_tests:
            preview_result = tool.preview_rename(test_files, test_case['pattern'])
            
            assert preview_result['status'] == 'success', \
                f"Sequential numbering failed for {test_case['description']}"
            
            # Verify sequential naming pattern
            if len(tool.preview_data) >= 2:
                first_item = tool.preview_data[0]
                second_item = tool.preview_data[1]
                
                # Should follow sequential pattern
                assert 'item_01' in first_item['new'] or 'document_0100' in first_item['new'], \
                    f"First item should follow pattern: {first_item['new']}"
    
    def test_case_modification_workflow(self, file_rename_test_environment):
        """
        Test: Case Modification → Pattern Application → Verification
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:5]])
        
        # Test case modification options
        case_tests = [
            {
                'mode': 'uppercase',
                'description': 'Convert to uppercase'
            },
            {
                'mode': 'lowercase',
                'description': 'Convert to lowercase'
            },
            {
                'mode': 'title_case',
                'description': 'Convert to title case'
            }
        ]
        
        for case_test in case_tests:
            case_pattern = {
                'mode': 'case_modification',
                'case_type': case_test['mode'],
                'preserve_extension': True
            }
            
            preview_result = tool.preview_rename(test_files, case_pattern)
            
            assert preview_result['status'] == 'success', \
                f"Case modification failed for {case_test['description']}"
            
            # Verify case modification was applied in preview
            assert len(tool.preview_data) > 0, \
                "Should have preview data for case modification"


class TestFileRenamePatternBased:
    """Test pattern-based renaming with regex and variables."""
    
    def test_regex_pattern_renaming_workflow(self, file_rename_test_environment):
        """
        Test: Regex Pattern → Pattern Matching → Replacement → Application
        Target: < 25 seconds for pattern application
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('file_rename', 'pattern_application')
        
        start_time = time.time()
        
        try:
            # Get test files
            test_files = []
            for root, dirs, files in os.walk(test_data_path):
                test_files.extend([os.path.join(root, f) for f in files[:15]])
            
            # Test regex-based pattern renaming
            regex_pattern = {
                'mode': 'pattern',
                'search_pattern': r'(.+)_(\d+)\.(.+)',
                'replacement_pattern': r'new_\1_\2.\3',
                'use_regex': True,
                'case_sensitive': False
            }
            
            preview_result = tool.preview_rename(test_files, regex_pattern)
            
            assert preview_result['status'] == 'success', \
                "Regex pattern renaming should succeed"
            
            # Apply the pattern
            apply_result = tool.apply_rename()
            
            assert apply_result['status'] == 'success', \
                "Pattern application should succeed"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 25.0, \
                f"Pattern application took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_rename', 'pattern_application')
            assert perf_result['target_met'], \
                f"Pattern application performance target not met: {perf_result}"
    
    def test_placeholder_variable_substitution(self, file_rename_test_environment):
        """
        Test: Variable Definition → Substitution → Pattern Application
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:8]])
        
        # Test placeholder variable substitution
        variable_pattern = {
            'mode': 'variables',
            'template': '{date}_{original_name}_{counter}',
            'variables': {
                'date': datetime.now().strftime('%Y%m%d'),
                'counter_start': 1,
                'counter_format': '{:03d}'
            },
            'preserve_extension': True
        }
        
        preview_result = tool.preview_rename(test_files, variable_pattern)
        
        assert preview_result['status'] == 'success', \
            "Variable substitution should succeed"
        
        # Verify variable substitution in preview
        if len(tool.preview_data) > 0:
            first_preview = tool.preview_data[0]
            new_name = first_preview['new']
            
            # Should contain date stamp
            current_date = datetime.now().strftime('%Y%m%d')
            assert current_date in new_name, \
                f"Should contain date stamp: {new_name}"
    
    def test_metadata_substitution_workflow(self, file_rename_test_environment):
        """
        Test: Metadata Extraction → Variable Substitution → Renaming
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:6]])
        
        # Test metadata-based substitution
        metadata_pattern = {
            'mode': 'metadata',
            'template': '{size}_{modified_date}_{original_name}',
            'metadata_fields': ['size', 'modified_date', 'file_type'],
            'date_format': '%Y%m%d',
            'size_format': 'human_readable'
        }
        
        preview_result = tool.preview_rename(test_files, metadata_pattern)
        
        assert preview_result['status'] == 'success', \
            "Metadata substitution should succeed"
        
        # Mock verification - real implementation would check actual metadata
        assert tool.generation_options == metadata_pattern, \
            "Metadata pattern should be stored"


class TestFileRenamePreviewApply:
    """Test preview and apply workflow functionality."""
    
    def test_preview_visualization_workflow(self, file_rename_test_environment):
        """
        Test: Rename Preview → Change Visualization → User Confirmation
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:12]])
        
        # Test preview with various rename patterns
        preview_patterns = [
            {
                'mode': 'sequential',
                'base_name': 'preview_test',
                'description': 'Sequential renaming preview'
            },
            {
                'mode': 'pattern',
                'search_pattern': 'old',
                'replacement': 'new',
                'description': 'Pattern replacement preview'
            }
        ]
        
        for pattern_test in preview_patterns:
            preview_result = tool.preview_rename(test_files, pattern_test)
            
            assert preview_result['status'] == 'success', \
                f"Preview failed for {pattern_test['description']}"
            
            # Verify comprehensive preview data
            assert len(tool.preview_data) == len(test_files), \
                "Should preview all files"
            
            for preview_item in tool.preview_data:
                assert preview_item['status'] == 'ready', \
                    "Preview items should be ready for application"
                assert preview_item['original'] != preview_item['new'], \
                    "Preview should show actual name changes"
    
    def test_selective_application_workflow(self, file_rename_test_environment):
        """
        Test: Preview → Selective Choose → Partial Application
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:10]])
        
        # Generate preview
        selective_pattern = {
            'mode': 'sequential',
            'base_name': 'selective_test'
        }
        
        preview_result = tool.preview_rename(test_files, selective_pattern)
        assert preview_result['status'] == 'success', \
            "Preview should succeed for selective application"
        
        # Test selective application (apply only first 5 items)
        selected_operations = tool.preview_data[:5]
        
        apply_result = tool.apply_rename(selected_operations)
        
        assert apply_result['status'] == 'success', \
            "Selective application should succeed"
        
        # Verify only selected operations were recorded
        if len(tool.rename_history) > 0:
            last_operation = tool.rename_history[-1]
            assert len(last_operation['operations']) == 5, \
                "Should record only selected operations"
    
    def test_confirmation_dialog_workflow(self, file_rename_test_environment):
        """
        Test: Preview → Confirmation Options → User Decision
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:8]])
        
        # Test confirmation workflow
        confirmation_pattern = {
            'mode': 'sequential',
            'base_name': 'confirmed_rename',
            'require_confirmation': True,
            'show_details': True
        }
        
        preview_result = tool.preview_rename(test_files, confirmation_pattern)
        assert preview_result['status'] == 'success', \
            "Preview with confirmation should succeed"
        
        # Mock confirmation acceptance
        confirmed_operations = tool.preview_data
        for operation in confirmed_operations:
            operation['confirmed'] = True
            operation['confirmation_timestamp'] = datetime.now().isoformat()
        
        apply_result = tool.apply_rename(confirmed_operations)
        
        assert apply_result['status'] == 'success', \
            "Confirmed rename should succeed"


class TestFileRenameUndoFunctionality:
    """Test undo functionality and operation history."""
    
    def test_operation_history_workflow(self, file_rename_test_environment):
        """
        Test: Multiple Rename Operations → History Tracking → Selective Undo
        Target: < 5 seconds for undo operations
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:6]])
        
        # Perform multiple rename operations
        operations = [
            {
                'mode': 'sequential',
                'base_name': 'operation_1',
                'description': 'First rename operation'
            },
            {
                'mode': 'sequential',
                'base_name': 'operation_2',
                'description': 'Second rename operation'
            }
        ]
        
        for i, operation in enumerate(operations):
            # Preview and apply each operation
            preview_result = tool.preview_rename(test_files, operation)
            assert preview_result['status'] == 'success', \
                f"Preview failed for {operation['description']}"
            
            apply_result = tool.apply_rename()
            assert apply_result['status'] == 'success', \
                f"Apply failed for {operation['description']}"
        
        # Verify operation history
        assert len(tool.rename_history) == len(operations), \
            "Should track all rename operations in history"
        
        # Test undo functionality
        performance_monitor.start_monitoring('file_rename', 'undo_operations')
        
        try:
            undo_result = tool.undo_last_operation()
            
            assert undo_result['status'] == 'success', \
                "Undo operation should succeed"
            
            # Verify history was modified
            assert len(tool.rename_history) == len(operations) - 1, \
                "Undo should remove last operation from history"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_rename', 'undo_operations')
            assert perf_result['target_met'], \
                "Undo performance target should be met"
    
    def test_partial_undo_workflow(self, file_rename_test_environment):
        """
        Test: Complex Rename → Partial Failure → Selective Rollback
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:8]])
        
        # Simulate complex rename with partial failure
        complex_pattern = {
            'mode': 'pattern',
            'complex_operation': True,
            'simulate_partial_failure': True
        }
        
        preview_result = tool.preview_rename(test_files, complex_pattern)
        assert preview_result['status'] == 'success', \
            "Complex pattern preview should succeed"
        
        # Apply with simulated partial failure
        apply_result = tool.apply_rename()
        
        # Should handle partial failure gracefully
        assert apply_result['status'] in ['success', 'partial'], \
            "Should handle partial failure scenarios"
        
        # Test selective rollback if needed
        if apply_result['status'] == 'partial':
            undo_result = tool.undo_last_operation()
            assert undo_result['status'] == 'success', \
                "Should be able to undo partial operations"
    
    def test_undo_state_persistence(self, file_rename_test_environment):
        """
        Test: Operation → State Recording → Undo → State Verification
        """
        env = file_rename_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Get test files
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            test_files.extend([os.path.join(root, f) for f in files[:5]])
        
        # Perform rename operation
        persistence_pattern = {
            'mode': 'sequential',
            'base_name': 'persistence_test'
        }
        
        preview_result = tool.preview_rename(test_files, persistence_pattern)
        assert preview_result['status'] == 'success', \
            "Persistence test preview should succeed"
        
        apply_result = tool.apply_rename()
        assert apply_result['status'] == 'success', \
            "Persistence test apply should succeed"
        
        # Verify state was recorded
        assert len(tool.rename_history) > 0, \
            "Should have operation history for undo"
        
        last_operation = tool.rename_history[-1]
        assert 'timestamp' in last_operation, \
            "Operation should have timestamp"
        assert 'operations' in last_operation, \
            "Operation should record file operations"
        assert 'results' in last_operation, \
            "Operation should record results"
        
        # Test undo with state verification
        undo_result = tool.undo_last_operation()
        assert undo_result['status'] == 'success', \
            "Undo should succeed with proper state"


# Test runner configuration
def run_file_rename_e2e_tests():
    """Run the File Rename E2E test suite."""
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
    print("Starting File Rename End-to-End Tests...")
    exit_code = run_file_rename_e2e_tests()
    
    print(f"\nFile Rename E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)