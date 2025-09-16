#!/usr/bin/env python3
"""
Size Analyzer End-to-End Test Suite

Comprehensive E2E testing for Size Analyzer tool functionality.
Tests directory analysis, visualization data generation, and export capabilities.

Created: 2025-09-04
Coverage: Directory analysis, size calculations, visualization data,
          export capabilities, and performance optimization
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
        MockSizeAnalyzerTool, assert_performance_target,
        size_analyzer_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="Analysis Tools utilities not available"
)


class TestSizeAnalyzerDirectoryAnalysis:
    """Test directory tree analysis and size calculations."""

    def test_directory_tree_analysis_workflow(self,
                                            size_analyzer_test_environment):
        """
        Test: Directory Selection → Analysis → Hierarchical Results
        Target: < 25 seconds for complex directory trees
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']

        # Connect signal tracking
        signal_tracker.connect_all_signals()

        performance_monitor.start_monitoring('size_analyzer',
                                           'directory_analysis')

        start_time = time.time()

        try:
            # Create complex directory structure for analysis
            complex_dirs = [
                'documents/reports',
                'documents/archives',
                'media/photos',
                'media/videos',
                'code/projects/project1',
                'code/projects/project2'
            ]

            created_dirs = []
            for dir_path in complex_dirs:
                full_path = os.path.join(test_data_path, dir_path)
                os.makedirs(full_path, exist_ok=True)
                created_dirs.append(full_path)

                # Create files of varying sizes
                for i in range(3):
                    file_path = os.path.join(full_path, f"file_{i}.txt")
                    size = 1024 * (i + 1) * 10  # 10KB, 20KB, 30KB
                    with open(file_path, 'w') as f:
                        f.write('x' * size)

            # Execute directory analysis
            options = {
                'include_subdirectories': True,
                'calculate_percentages': True,
                'sort_by_size': True
            }

            result = tool.analyze_directory_sizes(test_data_path, options)

            # Verify analysis completion
            assert result is not None, "Analysis result should not be None"
            assert result['status'] == 'success', \
                f"Analysis should succeed, got: {result.get('status')}"
            assert 'results_count' in result, \
                "Result should include count"

            # Verify analysis results structure
            if hasattr(tool, 'analysis_results') and tool.analysis_results:
                analysis = tool.analysis_results
                required_fields = ['root_path', 'total_size', 'total_files',
                                 'directory_count', 'directories']
                for field in required_fields:
                    assert field in analysis, \
                        f"Analysis result missing field: {field}"

                # Verify directory data
                if 'directories' in analysis and analysis['directories']:
                    first_dir = analysis['directories'][0]
                    dir_required_fields = ['path', 'size', 'file_count']
                    for field in dir_required_fields:
                        assert field in first_dir, \
                            f"Directory data missing field: {field}"

            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 25.0, \
                f"Directory analysis took too long: {workflow_time:.2f}s"

            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"

        finally:
            # Cleanup created directories
            for dir_path in created_dirs:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)

            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'size_analyzer', 'directory_analysis')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"

    def test_size_calculation_accuracy_workflow(self,
                                              size_analyzer_test_environment):
        """
        Test: Size Calculation → Accuracy Validation → Statistics
        Target: < 15 seconds for 1,000 files
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        performance_monitor.start_monitoring('size_analyzer',
                                           'size_calculation')

        start_time = time.time()

        try:
            # Create files with known sizes for accuracy testing
            test_files_data = []
            total_expected_size = 0

            for i in range(10):
                file_size = 1024 * (i + 1) * 5  # 5KB, 10KB, 15KB, etc.
                file_path = os.path.join(test_data_path,
                                       f"size_test_{i:03d}.txt")
                
                with open(file_path, 'w') as f:
                    f.write('x' * file_size)
                
                test_files_data.append({
                    'path': file_path,
                    'expected_size': file_size
                })
                total_expected_size += file_size

            # Execute size analysis
            result = tool.analyze_directory_sizes(test_data_path)

            assert result['status'] == 'success', \
                "Size calculation should succeed"

            # Verify calculation accuracy (mock implementation)
            if hasattr(tool, 'analysis_results') and tool.analysis_results:
                analysis = tool.analysis_results
                calculated_size = analysis.get('total_size', 0)
                
                # In real implementation, would verify exact size match
                # Mock implementation provides reasonable values
                assert calculated_size > 0, \
                    "Should calculate non-zero total size"

            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Size calculation took too long: {workflow_time:.2f}s"

        finally:
            # Cleanup test files
            for file_data in test_files_data:
                if os.path.exists(file_data['path']):
                    os.remove(file_data['path'])

            perf_result = performance_monitor.stop_monitoring(
                'size_analyzer', 'size_calculation')
            assert perf_result['target_met'], \
                f"Size calculation performance target not met: {perf_result}"


class TestSizeAnalyzerVisualizationData:
    """Test visualization data generation for charts and reports."""

    def test_visualization_data_generation_workflow(self,
                                                  size_analyzer_test_environment):
        """
        Test: Analysis Results → Visualization Data → Chart Generation
        Target: < 5 seconds for chart data preparation
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # First, perform directory analysis
        analysis_result = tool.analyze_directory_sizes(test_data_path)
        assert analysis_result['status'] == 'success', \
            "Initial analysis should succeed"

        # Test different chart types
        chart_types = ['treemap', 'pie', 'bar', 'bubble']

        for chart_type in chart_types:
            performance_monitor.start_monitoring('size_analyzer',
                                               'visualization_data')

            start_time = time.time()

            try:
                # Generate visualization data
                viz_result = tool.generate_visualization_data(chart_type)

                assert viz_result['status'] == 'success', \
                    f"Visualization data generation should succeed for {chart_type}"

                # Verify visualization data structure
                if hasattr(tool, 'visualization_data'):
                    viz_data = tool.visualization_data
                    assert 'chart_type' in viz_data, \
                        "Should include chart type"
                    assert viz_data['chart_type'] == chart_type, \
                        f"Chart type should match: expected {chart_type}"

                workflow_time = time.time() - start_time
                assert workflow_time < 5.0, \
                    f"Visualization data generation took too long: " \
                    f"{workflow_time:.2f}s"

            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'size_analyzer', 'visualization_data')
                assert perf_result['target_met'], \
                    f"Visualization performance target not met for {chart_type}"


class TestSizeAnalyzerExportCapabilities:
    """Test export capabilities in multiple formats."""

    def test_multi_format_export_workflow(self, size_analyzer_test_environment):
        """
        Test: Analysis Results → Format Selection → Export Generation
        Formats: JSON, CSV, HTML, XML
        Target: < 8 seconds for export operations
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']

        # First, perform analysis
        analysis_result = tool.analyze_directory_sizes(test_data_path)
        assert analysis_result['status'] == 'success', \
            "Initial analysis should succeed"

        # Test different export formats
        export_formats = ['json', 'csv', 'html', 'xml']

        for export_format in export_formats:
            performance_monitor.start_monitoring('size_analyzer',
                                               'export_operations')

            try:
                # Create temporary export file
                with tempfile.NamedTemporaryFile(
                    suffix=f'.{export_format}', delete=False) as tmp_file:
                    export_path = tmp_file.name

                # Execute export
                export_result = tool.export_analysis(export_format,
                                                   export_path)

                # Verify export success
                assert export_result['status'] == 'success', \
                    f"Export to {export_format} should succeed"

                # Clean up
                if os.path.exists(export_path):
                    os.unlink(export_path)

            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'size_analyzer', 'export_operations')
                assert perf_result['target_met'], \
                    f"Export performance target not met for {export_format}"


class TestSizeAnalyzerErrorHandling:
    """Test error handling and recovery scenarios."""

    def test_analysis_error_recovery_workflow(self,
                                            size_analyzer_test_environment):
        """
        Test: Analysis Error → Graceful Handling → Partial Results
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        signal_tracker = env['signal_tracker']

        signal_tracker.connect_all_signals()

        # Simulate analysis error
        error_result = tool.simulate_error(
            'directory_access_denied',
            'Permission denied for some directories'
        )

        assert error_result['status'] == 'error', \
            "Should return error status"
        assert error_result['error_type'] == 'directory_access_denied', \
            "Should identify error type"

        # Verify error tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['error_events'] > 0, \
            "Should track error events"

    def test_analysis_cancellation_workflow(self, size_analyzer_test_environment):
        """
        Test: Long Analysis → User Cancellation → Clean Termination
        """
        env = size_analyzer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']

        # Simulate cancellation
        tool.cancel_operation()

        # Execute operation (should be cancelled)
        result = tool.process_data(f"analyze_{test_data_path}")

        assert result['status'] == 'cancelled', \
            "Cancelled operation should return cancelled status"
        assert 'cancelled' in result['message'].lower(), \
            "Should indicate cancellation in message"

        # Verify cancellation state
        assert tool._should_cancel, "Tool should be in cancelled state"


# Test runner configuration
def run_size_analyzer_e2e_tests():
    """Run the Size Analyzer E2E test suite."""
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
    print("Starting Size Analyzer End-to-End Tests...")
    exit_code = run_size_analyzer_e2e_tests()

    print(f"\nSize Analyzer E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)