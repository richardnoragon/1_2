#!/usr/bin/env python3
"""
Catalog Files End-to-End Test Suite

Comprehensive E2E testing for Catalog Files tool functionality.
Tests complete workflows from catalog generation through export and sharing.

Created: 2025-09-04
Coverage: HTML catalog generation, recursive cataloging, export workflows,
          large directory handling, and template customization
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
        FileManagementTestDataFactory, MockCatalogFilesTool, MockRFUHub,
        assert_performance_target, catalog_files_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Management utilities not available"
)


class TestCatalogFilesHTMLGeneration:
    """Test HTML catalog generation workflows and template processing."""
    
    def test_html_catalog_generation_workflow(self, catalog_files_test_environment):
        """
        Test: Directory Selection → Template Configuration → HTML Generation → Validation
        Target: < 30 seconds for medium dataset catalog generation
        """
        env = catalog_files_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('catalog_files', 'html_generation')
        
        start_time = time.time()
        
        try:
            # Execute HTML catalog generation
            catalog_options = {
                'template': 'standard',
                'include_metadata': True,
                'include_thumbnails': True,
                'responsive_layout': True,
                'custom_css': True,
                'include_file_counts': True,
                'sort_order': 'name'
            }
            
            result = tool.generate_catalog(test_data_path, catalog_options)
            
            # Verify catalog generation completion
            assert result is not None, "Catalog result should not be None"
            assert result['status'] == 'success', \
                f"Catalog generation should succeed, got: {result.get('status')}"
            assert 'file_count' in result, "Result should include file count"
            assert result['file_count'] > 0, "Should catalog some files"
            
            # Verify catalog data structure
            assert len(tool.catalog_data) > 0, "Tool should have catalog data"
            catalog_data = tool.catalog_data
            
            required_fields = ['directory', 'file_count', 'total_size', 
                             'generation_date', 'files']
            for field in required_fields:
                assert field in catalog_data, \
                    f"Catalog data missing field: {field}"
            
            # Verify file entries structure
            if len(catalog_data['files']) > 0:
                first_file = catalog_data['files'][0]
                file_required_fields = ['name', 'size', 'type', 'modified']
                for field in file_required_fields:
                    assert field in first_file, \
                        f"File entry missing field: {field}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"HTML generation took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'catalog_files', 'html_generation')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_template_customization_workflow(self, catalog_files_test_environment):
        """
        Test: Template Selection → Customization → HTML Generation → Template Validation
        """
        env = catalog_files_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Test different template configurations
        template_tests = [
            {
                'template': 'minimal',
                'include_metadata': False,
                'include_thumbnails': False,
                'description': 'Minimal template'
            },
            {
                'template': 'detailed',
                'include_metadata': True,
                'include_thumbnails': True,
                'custom_css': True,
                'description': 'Detailed template with metadata'
            },
            {
                'template': 'gallery',
                'include_thumbnails': True,
                'gallery_mode': True,
                'thumbnail_size': 'medium',
                'description': 'Gallery-style template'
            }
        ]
        
        for test_case in template_tests:
            result = tool.generate_catalog(test_data_path, test_case)
            
            assert result['status'] == 'success', \
                f"Template generation failed for {test_case['description']}"
            
            # Verify template options were applied
            assert tool.generation_options == test_case, \
                f"Template options not stored correctly for {test_case['description']}"
            
            # Verify catalog data reflects template settings
            catalog_data = tool.catalog_data
            assert catalog_data['options'] == test_case, \
                "Catalog data should include generation options"


class TestCatalogFilesRecursiveProcessing:
    """Test recursive vs single directory cataloging workflows."""
    
    def test_recursive_cataloging_workflow(self, catalog_files_test_environment):
        """
        Test: Recursive Option → Deep Directory Scanning → Complete Catalog
        Target: < 60 seconds for recursive catalog of medium dataset
        """
        env = catalog_files_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('catalog_files', 'recursive_catalog')
        
        start_time = time.time()
        
        try:
            # Execute recursive cataloging
            recursive_options = {
                'recursive': True,
                'max_depth': 10,
                'follow_symlinks': False,
                'include_hidden': False,
                'directory_tree_view': True
            }
            
            result = tool.generate_catalog(test_data_path, recursive_options)
            
            # Verify recursive cataloging completion
            assert result['status'] == 'success', \
                "Recursive cataloging should succeed"
            assert result['file_count'] > 0, \
                "Should find files in recursive scan"
            
            # Verify comprehensive coverage
            catalog_data = tool.catalog_data
            assert catalog_data['file_count'] >= 10, \
                "Recursive scan should find multiple files"
            
            # Verify recursive option was applied
            assert tool.generation_options['recursive'], \
                "Recursive option should be stored"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 60.0, \
                f"Recursive cataloging took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'catalog_files', 'recursive_catalog')
            assert perf_result['target_met'], \
                f"Recursive catalog performance target not met: {perf_result}"


class TestCatalogFilesExportSharing:
    """Test catalog export and sharing functionality."""
    
    def test_multiple_format_export_workflow(self, 
                                           catalog_files_test_environment):
        """
        Test: Catalog Generation → Format Selection → Export → Validation
        Target: < 20 seconds for export operations
        """
        env = catalog_files_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # First generate a catalog
        catalog_options = {'template': 'standard', 'include_metadata': True}
        catalog_result = tool.generate_catalog(test_data_path, catalog_options)
        
        assert catalog_result['status'] == 'success', \
            "Initial catalog generation should succeed"
        assert len(tool.catalog_data) > 0, "Should have catalog data to export"
        
        # Test different export formats
        export_formats = ['html', 'pdf', 'json']
        
        for export_format in export_formats:
            performance_monitor.start_monitoring(
                'catalog_files', 'export_operations')
            
            try:
                # Create temporary export file
                with tempfile.NamedTemporaryFile(
                    suffix=f'.{export_format}', delete=False) as tmp_file:
                    export_path = tmp_file.name
                
                # Execute export
                export_result = tool.export_catalog(export_format, export_path)
                
                # Verify export success
                assert export_result['status'] == 'success', \
                    f"Export to {export_format} should succeed"
                assert 'output_path' in export_result or 'format' in export_result, \
                    "Export result should include format info"
                
                # Clean up
                if os.path.exists(export_path):
                    os.unlink(export_path)
                
            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'catalog_files', 'export_operations')
                assert perf_result['target_met'], \
                    f"Export performance target not met for {export_format}"


class TestCatalogFilesLargeDirectory:
    """Test large directory handling and performance scenarios."""
    
    def test_large_directory_performance_workflow(self, 
                                                 catalog_files_test_environment):
        """
        Test: Large Directory → Memory Management → Progress Reporting → Completion
        Target: < 120 seconds for enterprise-scale cataloging (10,000+ files)
        """
        env = catalog_files_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Monitor initial memory usage
        initial_memory = performance_monitor._get_memory_usage()
        
        performance_monitor.start_monitoring('catalog_files', 'recursive_catalog')
        
        try:
            # Simulate large dataset cataloging
            large_dataset_options = {
                'recursive': True,
                'max_depth': 15,
                'chunk_processing': True,
                'memory_limit_mb': 500,
                'progress_reporting': True,
                'optimize_for_size': True
            }
            
            result = tool.generate_catalog(test_data_path, large_dataset_options)
            
            assert result['status'] == 'success', \
                "Large directory cataloging should succeed"
            
            # Check memory usage
            final_memory = performance_monitor._get_memory_usage()
            if initial_memory > 0 and final_memory > 0:
                memory_increase_mb = (final_memory - initial_memory) / (1024 * 1024)
                assert memory_increase_mb < 300, \
                    f"Memory usage too high: {memory_increase_mb:.1f}MB"
            
            # Verify resource usage tracking
            resource_usage = tool.get_resource_usage()
            assert isinstance(resource_usage, dict), \
                "Should track resource usage"
            assert 'memory' in resource_usage, \
                "Should track memory usage"
            
        finally:
            performance_monitor.stop_monitoring('catalog_files', 'recursive_catalog')


# Test runner configuration
def run_catalog_files_e2e_tests():
    """Run the Catalog Files E2E test suite."""
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
    print("Starting Catalog Files End-to-End Tests...")
    exit_code = run_catalog_files_e2e_tests()
    
    print(f"\nCatalog Files E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)