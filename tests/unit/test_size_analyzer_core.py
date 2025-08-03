"""
Core Logic Testing for Size Analyzer

This module contains comprehensive tests for the SizeAnalyzer class functionality,
including directory analysis, progress tracking, signal emissions, and edge cases.
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtTest import QSignalSpy

from file_utilities_2.core.size_analyzer_logic import (
    SizeAnalyzer, SizeAnalyzerWorker
)


class TestSizeAnalyzerCore:
    """Test core SizeAnalyzer functionality."""
    
    def test_initialization(self, size_analyzer):
        """Test SizeAnalyzer initialization."""
        assert size_analyzer is not None
        assert not size_analyzer.is_running()
        assert size_analyzer._hub_connector is None
        assert size_analyzer._performance_metrics is not None
        assert size_analyzer._resource_usage is not None
    
    def test_initialization_with_hub(self, mock_hub):
        """Test SizeAnalyzer initialization with hub connector."""
        analyzer = SizeAnalyzer(hub_connector=mock_hub)
        assert analyzer._hub_connector == mock_hub
    
    def test_signal_definitions(self, size_analyzer):
        """Test that all required signals are defined."""
        required_signals = [
            'progress_updated',
            'progress_percentage', 
            'progress_message',
            'milestone_reached',
            'time_estimate',
            'analysis_complete',
            'error_occurred',
            'operation_cancelled'
        ]
        
        for signal_name in required_signals:
            assert hasattr(size_analyzer, signal_name)
            signal = getattr(size_analyzer, signal_name)
            assert isinstance(signal, pyqtSignal)
    
    def test_analyze_directory_basic(self, size_analyzer, test_files, temp_dir):
        """Test basic directory analysis functionality."""
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert isinstance(result, dict)
        assert result['path'] == temp_dir
        assert result['total_size'] > 0
        assert result['file_count'] > 0
        assert result['directory_count'] >= 0
        assert isinstance(result['files'], list)
        assert isinstance(result['file_types'], dict)
        assert isinstance(result['largest_files'], list)
        assert isinstance(result['directory_tree'], dict)
    
    def test_analyze_directory_with_progress_callback(self, size_analyzer, 
                                                     test_files, temp_dir):
        """Test directory analysis with progress callback."""
        progress_values = []
        
        def progress_callback(percentage):
            progress_values.append(percentage)
        
        result = size_analyzer.analyze_directory(
            temp_dir, 
            progress_callback=progress_callback
        )
        
        assert result is not None
        assert len(progress_values) > 0
        assert progress_values[-1] == 100
    
    def test_analyze_directory_with_extension_filter(self, size_analyzer, 
                                                    test_files, temp_dir):
        """Test directory analysis with file extension filtering."""
        result = size_analyzer.analyze_directory(
            temp_dir,
            include_extensions=['.txt']
        )
        
        # Should only include .txt files
        for file_info in result['files']:
            assert file_info['extension'] == '.txt'
    
    def test_analyze_directory_top_files_count(self, size_analyzer, 
                                              test_files, temp_dir):
        """Test directory analysis with custom top files count."""
        result = size_analyzer.analyze_directory(
            temp_dir,
            top_files_count=3
        )
        
        assert len(result['largest_files']) <= 3
    
    def test_analyze_nonexistent_directory(self, size_analyzer):
        """Test analysis of non-existent directory."""
        with pytest.raises(FileNotFoundError):
            size_analyzer.analyze_directory('/nonexistent/directory')
    
    def test_analyze_file_instead_of_directory(self, size_analyzer, test_files):
        """Test analysis when path is a file, not directory."""
        file_path = list(test_files.values())[0]['path']
        
        with pytest.raises(NotADirectoryError):
            size_analyzer.analyze_directory(file_path)
    
    def test_format_size(self, size_analyzer):
        """Test size formatting functionality."""
        test_cases = [
            (0, "0.0 B"),
            (512, "512.0 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (1099511627776, "1.0 TB")
        ]
        
        for size_bytes, expected in test_cases:
            result = size_analyzer.format_size(size_bytes)
            assert result == expected
    
    def test_export_analysis(self, size_analyzer, analysis_results_sample, 
                           temp_dir):
        """Test analysis export functionality."""
        export_path = os.path.join(temp_dir, 'export_test.json')
        
        size_analyzer.export_analysis(analysis_results_sample, export_path)
        
        assert os.path.exists(export_path)
        
        # Verify exported content
        import json
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        assert 'export_metadata' in exported_data
        assert 'export_time' in exported_data['export_metadata']
        assert 'analyzer_version' in exported_data['export_metadata']
    
    def test_export_analysis_invalid_path(self, size_analyzer, 
                                         analysis_results_sample):
        """Test export with invalid file path."""
        invalid_path = '/invalid/path/export.json'
        
        with pytest.raises(IOError):
            size_analyzer.export_analysis(analysis_results_sample, invalid_path)
    
    def test_cancellation_support(self, size_analyzer, performance_test_data):
        """Test operation cancellation."""
        # Start analysis and immediately cancel
        size_analyzer._should_cancel = False
        
        # Mock a long-running operation
        with patch.object(size_analyzer, '_count_items', return_value=1000000):
            size_analyzer.cancel_operation()
            assert size_analyzer._should_cancel is True
    
    def test_hub_integration_reporting(self, mock_hub):
        """Test hub integration and status reporting."""
        analyzer = SizeAnalyzer(hub_connector=mock_hub)
        
        # Test hub connector setting
        analyzer.set_hub_connector(mock_hub)
        assert analyzer._hub_connector == mock_hub
        
        # Test resource usage update
        analyzer.update_resource_usage(cpu_usage=50.0, memory_usage=100.0)
        assert analyzer._resource_usage['cpu_usage'] == 50.0
        assert analyzer._resource_usage['memory_usage'] == 100.0
    
    def test_performance_metrics_tracking(self, size_analyzer, test_files, 
                                         temp_dir):
        """Test performance metrics collection."""
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert 'performance_metrics' in result
        metrics = result['performance_metrics']
        
        assert 'start_time' in metrics
        assert 'end_time' in metrics
        assert 'files_per_second' in metrics
        assert 'bytes_per_second' in metrics
        
        assert metrics['files_per_second'] >= 0
        assert metrics['bytes_per_second'] >= 0
    
    def test_signal_emissions(self, qapp, size_analyzer, test_files, temp_dir):
        """Test that signals are properly emitted during analysis."""
        # Create signal spies
        progress_spy = QSignalSpy(size_analyzer.progress_percentage)
        message_spy = QSignalSpy(size_analyzer.progress_message)
        milestone_spy = QSignalSpy(size_analyzer.milestone_reached)
        complete_spy = QSignalSpy(size_analyzer.analysis_complete)
        
        # Perform analysis
        size_analyzer.analyze_directory(temp_dir)
        
        # Verify signals were emitted
        assert len(progress_spy) > 0
        assert len(message_spy) > 0
        assert len(milestone_spy) > 0
        assert len(complete_spy) == 1
    
    def test_file_type_analysis(self, size_analyzer, test_files, temp_dir):
        """Test file type analysis functionality."""
        result = size_analyzer.analyze_directory(temp_dir)
        
        file_types = result['file_types']
        assert isinstance(file_types, dict)
        
        # Check that file types are properly categorized
        for ext, stats in file_types.items():
            assert 'count' in stats
            assert 'total_size' in stats
            assert 'average_size' in stats
            assert stats['count'] > 0
            assert stats['total_size'] >= 0
            assert stats['average_size'] >= 0
    
    def test_largest_files_identification(self, size_analyzer, test_files, 
                                         temp_dir):
        """Test largest files identification."""
        result = size_analyzer.analyze_directory(temp_dir, top_files_count=5)
        
        largest_files = result['largest_files']
        assert isinstance(largest_files, list)
        assert len(largest_files) <= 5
        
        # Verify files are sorted by size (largest first)
        for i in range(1, len(largest_files)):
            assert largest_files[i-1]['size'] >= largest_files[i]['size']
    
    def test_directory_tree_generation(self, size_analyzer, test_files, 
                                      temp_dir):
        """Test directory tree generation."""
        result = size_analyzer.analyze_directory(temp_dir)
        
        tree = result['directory_tree']
        assert isinstance(tree, dict)
        assert 'name' in tree
        assert 'path' in tree
        assert 'size' in tree
        assert 'children' in tree
        
        assert tree['path'] == temp_dir
        assert tree['size'] >= 0
    
    def test_error_handling_permission_denied(self, size_analyzer):
        """Test error handling for permission denied scenarios."""
        with patch('os.walk') as mock_walk:
            mock_walk.side_effect = PermissionError("Permission denied")
            
            # Should not raise exception, but handle gracefully
            with patch('os.path.exists', return_value=True), \
                 patch('os.path.isdir', return_value=True):
                result = size_analyzer.analyze_directory('/restricted')
                assert result is not None
    
    def test_progress_tracking_accuracy(self, size_analyzer, test_files, 
                                       temp_dir):
        """Test progress tracking accuracy."""
        progress_values = []
        
        def track_progress(percentage):
            progress_values.append(percentage)
        
        size_analyzer.progress_percentage.connect(track_progress)
        size_analyzer.analyze_directory(temp_dir)
        
        # Verify progress values are reasonable
        assert len(progress_values) > 0
        assert all(0 <= p <= 100 for p in progress_values)
        assert progress_values[-1] == 100  # Should end at 100%
    
    def test_milestone_progression(self, size_analyzer, test_files, temp_dir):
        """Test milestone progression during analysis."""
        milestones = []
        
        def track_milestones(milestone, percentage):
            milestones.append((milestone, percentage))
        
        size_analyzer.milestone_reached.connect(track_milestones)
        size_analyzer.analyze_directory(temp_dir)
        
        # Verify milestone progression
        assert len(milestones) > 0
        
        milestone_names = [m[0] for m in milestones]
        assert "Analysis Started" in milestone_names
        assert "Analysis Complete" in milestone_names
        
        # Verify percentage progression
        percentages = [m[1] for m in milestones]
        assert percentages[0] == 0   # Should start at 0%
        assert percentages[-1] == 100  # Should end at 100%


class TestSizeAnalyzerWorker:
    """Test SizeAnalyzerWorker thread functionality."""
    
    def test_worker_initialization(self, size_analyzer, temp_dir):
        """Test worker thread initialization."""
        worker = SizeAnalyzerWorker(size_analyzer, temp_dir)
        
        assert worker.analyzer == size_analyzer
        assert worker.directory_path == temp_dir
        assert worker.hub_connector is None
    
    def test_worker_initialization_with_hub(self, size_analyzer, temp_dir, 
                                           mock_hub):
        """Test worker thread initialization with hub connector."""
        worker = SizeAnalyzerWorker(
            size_analyzer, temp_dir, hub_connector=mock_hub
        )
        
        assert worker.hub_connector == mock_hub
        assert worker.analyzer._hub_connector == mock_hub
    
    def test_worker_signal_connections(self, qapp, size_analyzer, temp_dir):
        """Test worker signal connections."""
        worker = SizeAnalyzerWorker(size_analyzer, temp_dir)
        
        # Test signal existence
        required_signals = [
            'analysis_finished',
            'analysis_error',
            'progress_update',
            'status_update'
        ]
        
        for signal_name in required_signals:
            assert hasattr(worker, signal_name)
            signal = getattr(worker, signal_name)
            assert isinstance(signal, pyqtSignal)
    
    def test_worker_cancellation(self, size_analyzer, temp_dir):
        """Test worker thread cancellation."""
        worker = SizeAnalyzerWorker(size_analyzer, temp_dir)
        
        # Test cancellation
        worker.cancel()
        
        # Verify analyzer was told to cancel
        assert size_analyzer._should_cancel is True
    
    def test_worker_run_success(self, qapp, size_analyzer, test_files, 
                               temp_dir):
        """Test successful worker execution."""
        worker = SizeAnalyzerWorker(size_analyzer, temp_dir)
        
        # Create signal spies
        finished_spy = QSignalSpy(worker.analysis_finished)
        error_spy = QSignalSpy(worker.analysis_error)
        
        # Run worker
        worker.run()
        
        # Verify successful completion
        assert len(finished_spy) == 1
        assert len(error_spy) == 0
    
    def test_worker_run_with_error(self, qapp, size_analyzer):
        """Test worker execution with error."""
        worker = SizeAnalyzerWorker(size_analyzer, '/nonexistent')
        
        # Create signal spies
        finished_spy = QSignalSpy(worker.analysis_finished)
        error_spy = QSignalSpy(worker.analysis_error)
        
        # Run worker (should fail)
        worker.run()
        
        # Verify error handling
        assert len(finished_spy) == 0
        assert len(error_spy) == 1


class TestSizeAnalyzerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_directory(self, size_analyzer, temp_dir):
        """Test analysis of empty directory."""
        empty_dir = os.path.join(temp_dir, 'empty')
        os.makedirs(empty_dir)
        
        result = size_analyzer.analyze_directory(empty_dir)
        
        assert result['file_count'] == 0
        assert result['total_size'] == 0
        assert len(result['files']) == 0
        assert len(result['file_types']) == 0
    
    def test_single_file_directory(self, size_analyzer, temp_dir):
        """Test analysis of directory with single file."""
        single_file = os.path.join(temp_dir, 'single.txt')
        with open(single_file, 'w') as f:
            f.write('Single file content')
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert result['file_count'] == 1
        assert len(result['files']) == 1
        assert result['files'][0]['name'] == 'single.txt'
    
    def test_deeply_nested_structure(self, size_analyzer, temp_dir):
        """Test analysis of deeply nested directory structure."""
        # Create deep nesting
        current_dir = temp_dir
        for i in range(10):  # 10 levels deep
            current_dir = os.path.join(current_dir, f'level_{i}')
            os.makedirs(current_dir)
            
            # Add a file at each level
            file_path = os.path.join(current_dir, f'file_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Content at level {i}')
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert result['file_count'] == 10
        assert result['directory_count'] >= 10
    
    def test_special_characters_in_filenames(self, size_analyzer, temp_dir):
        """Test analysis with special characters in filenames."""
        special_files = [
            'file with spaces.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
            'file.with.dots.txt',
            'file(with)parentheses.txt'
        ]
        
        for filename in special_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f'Content for {filename}')
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert result['file_count'] == len(special_files)
        
        # Verify all files were found
        found_names = [f['name'] for f in result['files']]
        for filename in special_files:
            assert filename in found_names
    
    def test_unicode_filenames(self, size_analyzer, temp_dir):
        """Test analysis with Unicode filenames."""
        unicode_files = [
            'файл.txt',  # Cyrillic
            '文件.txt',   # Chinese
            'ファイル.txt', # Japanese
            '파일.txt',   # Korean
            'αρχείο.txt'  # Greek
        ]
        
        for filename in unicode_files:
            try:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'Unicode content for {filename}')
            except (OSError, UnicodeError):
                # Skip if filesystem doesn't support Unicode
                continue
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        # Should handle Unicode filenames gracefully
        assert result is not None
        assert result['file_count'] >= 0
    
    def test_very_large_file_count(self, size_analyzer, temp_dir):
        """Test analysis with many files."""
        # Create many small files
        for i in range(1000):
            file_path = os.path.join(temp_dir, f'file_{i:04d}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Content {i}')
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        assert result['file_count'] == 1000
        assert len(result['files']) == 1000
    
    def test_mixed_file_extensions(self, size_analyzer, temp_dir):
        """Test analysis with various file extensions."""
        extensions = [
            '.txt', '.doc', '.pdf', '.jpg', '.png', '.mp3', '.mp4',
            '.zip', '.exe', '.dll', '.py', '.js', '.html', '.css'
        ]
        
        for i, ext in enumerate(extensions):
            file_path = os.path.join(temp_dir, f'file_{i}{ext}')
            with open(file_path, 'w') as f:
                f.write(f'Content for {ext} file')
        
        result = size_analyzer.analyze_directory(temp_dir)
        
        # Verify file types are properly categorized
        file_types = result['file_types']
        for ext in extensions:
            assert ext in file_types
            assert file_types[ext]['count'] == 1
    
    def test_symlink_handling(self, size_analyzer, temp_dir):
        """Test handling of symbolic links."""
        # Create a regular file
        regular_file = os.path.join(temp_dir, 'regular.txt')
        with open(regular_file, 'w') as f:
            f.write('Regular file content')
        
        # Try to create a symlink (may not work on all systems)
        try:
            symlink_path = os.path.join(temp_dir, 'symlink.txt')
            os.symlink(regular_file, symlink_path)
            
            result = size_analyzer.analyze_directory(temp_dir)
            
            # Should handle symlinks gracefully
            assert result is not None
            assert result['file_count'] >= 1
            
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            pytest.skip("Symbolic links not supported")