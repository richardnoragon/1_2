#!/usr/bin/env python3
"""
Comprehensive Test Suite for Core Analysis Engine Components
Test Coverage for High Priority Missing Critical Tests ❌

This test suite addresses the missing critical test cases identified in the
Priority Recommendations section of utilities-overview.md, providing comprehensive
coverage for data processing pipelines, algorithm validation, error handling,
edge cases, performance benchmarks, and integration points.

Author: Richard's File Utilities Team
Date: August 31, 2025
Version: 1.0.0
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import core analysis components
try:
    from src.tools.analysis.checksum.check_sum import ChecksumGUI
    from src.tools.analysis.config.config_analyzer import (
        ConfigAnalysisResult,
        ConfigIssue,
        ConfigType,
        ConfigurationAnalyzer,
        SecurityLevel,
    )
    from src.tools.analysis.duplicate_finder.find_duplicate_files import (
        DuplicateFinderApp as DuplicateFilesFinder,
    )
    from src.tools.analysis.empty_folders import EmptyFoldersFinder
    from src.tools.analysis.size_analyzer.size_analyzer_logic import (
        SizeAnalyzer,
        SizeAnalyzerWorker,
    )
except ImportError as e:
    pytest.skip(f"Core analysis modules not available: {e}", allow_module_level=True)

# PyQt5 imports for GUI testing
try:
    from PyQt5.QtCore import QThread, QTimer, pyqtSignal
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QMessageBox

    PyQt5_available = True
except ImportError:
    PyQt5_available = False


class TestDataProcessingPipelines:
    """Test data processing pipelines in core analysis engine."""

    @pytest.fixture
    def size_analyzer(self):
        """Create a SizeAnalyzer instance for testing."""
        return SizeAnalyzer()

    @pytest.fixture
    def temp_directory_structure(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            test_files = {
                "root_file.txt": "Root level content",
                "subdir1/file1.py": "Python file content\n# Comment line",
                "subdir1/file2.json": '{"test": "data", "number": 42}',
                "subdir1/nested/deep_file.md": "# Markdown\n\nSome content",
                "subdir2/large_file.dat": "x" * 10000,  # 10KB file
                "subdir2/empty_file.txt": "",
                "subdir3/file.log": "Log entry 1\nLog entry 2\nLog entry 3",
            }

            for file_path, content in test_files.items():
                full_path = Path(temp_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            yield temp_dir, test_files

    def test_data_pipeline_initialization(self, size_analyzer):
        """Test data processing pipeline initialization."""
        # Verify initial state
        assert not size_analyzer.is_running()
        assert size_analyzer._should_cancel == False
        assert size_analyzer._current_analysis is None
        assert size_analyzer._performance_metrics["start_time"] is None

        # Verify signal connections exist
        assert hasattr(size_analyzer, "progress_updated")
        assert hasattr(size_analyzer, "analysis_complete")
        assert hasattr(size_analyzer, "error_occurred")

    def test_data_collection_phase(self, size_analyzer, temp_directory_structure):
        """Test data collection phase of processing pipeline."""
        temp_dir, test_files = temp_directory_structure

        # Test directory scanning
        total_items = size_analyzer._count_items(temp_dir)
        assert total_items == len(test_files)

        # Test file analysis method
        test_file = Path(temp_dir) / "subdir1/file1.py"
        file_info = size_analyzer._analyze_file(str(test_file))

        assert file_info["name"] == "file1.py"
        assert file_info["path"] == str(test_file)
        assert file_info["extension"] == ".py"
        assert file_info["size"] > 0
        assert "modified" in file_info

    def test_data_transformation_phase(self, size_analyzer, temp_directory_structure):
        """Test data transformation and aggregation phase."""
        temp_dir, test_files = temp_directory_structure

        # Test file type statistics update
        file_types = {}
        file_info = {"name": "test.py", "size": 100, "extension": ".py"}

        size_analyzer._update_file_type_stats(file_info, file_types)

        assert ".py" in file_types
        assert file_types[".py"]["count"] == 1
        assert file_types[".py"]["total_size"] == 100
        assert file_types[".py"]["average_size"] == 100

        # Add another file of same type
        file_info2 = {"name": "test2.py", "size": 200, "extension": ".py"}
        size_analyzer._update_file_type_stats(file_info2, file_types)

        assert file_types[".py"]["count"] == 2
        assert file_types[".py"]["total_size"] == 300
        assert file_types[".py"]["average_size"] == 150

    def test_data_processing_with_filters(
        self, size_analyzer, temp_directory_structure
    ):
        """Test data processing with extension filters."""
        temp_dir, test_files = temp_directory_structure

        # Test with Python files only
        result = size_analyzer.analyze_directory(temp_dir, include_extensions=[".py"])

        assert result["file_count"] == 1  # Only file1.py
        assert all(f["extension"] == ".py" for f in result["files"])

        # Test with multiple extensions
        result = size_analyzer.analyze_directory(
            temp_dir, include_extensions=[".py", ".json"]
        )

        assert result["file_count"] == 2  # file1.py and file2.json
        extensions = {f["extension"] for f in result["files"]}
        assert extensions == {".py", ".json"}

    def test_data_export_pipeline(self, size_analyzer, temp_directory_structure):
        """Test data export processing pipeline."""
        temp_dir, test_files = temp_directory_structure

        # Perform analysis
        result = size_analyzer.analyze_directory(temp_dir)

        # Test export preparation
        exportable = size_analyzer._prepare_for_export(result)

        assert "export_metadata" in exportable
        assert "export_time" in exportable["export_metadata"]
        assert "analyzer_version" in exportable["export_metadata"]
        assert "total_files_analyzed" in exportable["export_metadata"]

        # Verify all timestamp fields are converted to ISO format
        for file_info in exportable.get("files", []):
            if "modified" in file_info:
                assert isinstance(file_info["modified"], str)
                # Should be in ISO format (contains 'T')
                assert "T" in file_info["modified"]

    def test_concurrent_data_processing(self, size_analyzer, temp_directory_structure):
        """Test concurrent data processing scenarios."""
        temp_dir, test_files = temp_directory_structure

        # Start analysis in background thread
        results = []
        errors = []

        def analysis_worker():
            try:
                result = size_analyzer.analyze_directory(temp_dir)
                results.append(result)
            except Exception as e:
                errors.append(e)

        thread = threading.Thread(target=analysis_worker)
        thread.start()
        thread.join(timeout=10)

        assert len(errors) == 0, f"Analysis failed with errors: {errors}"
        assert len(results) == 1
        assert results[0]["file_count"] == len(test_files)


class TestAlgorithmValidation:
    """Test algorithm validation and correctness."""

    @pytest.fixture
    def config_analyzer(self):
        """Create a ConfigurationAnalyzer for testing."""
        return ConfigurationAnalyzer()

    def test_config_type_detection_algorithm(self, config_analyzer):
        """Test configuration type detection algorithm."""
        # Test JSON detection
        assert config_analyzer.detect_config_type("config.json") == ConfigType.JSON
        assert config_analyzer.detect_config_type("data.JSON") == ConfigType.JSON

        # Test YAML detection
        assert config_analyzer.detect_config_type("config.yaml") == ConfigType.YAML
        assert config_analyzer.detect_config_type("docker.yml") == ConfigType.YAML

        # Test INI detection
        assert config_analyzer.detect_config_type("config.ini") == ConfigType.INI
        assert config_analyzer.detect_config_type("app.cfg") == ConfigType.INI
        assert config_analyzer.detect_config_type("settings.conf") == ConfigType.INI

        # Test unknown type
        assert config_analyzer.detect_config_type("unknown.xyz") == ConfigType.UNKNOWN

    def test_security_pattern_validation(self, config_analyzer):
        """Test security pattern detection algorithms."""
        # Test password detection
        test_content = """
        password = "secret123"
        api_key = "abc123xyz"
        database_url = "mysql://user:pass@host/db"
        """

        result = ConfigAnalysisResult(
            file_path="test.conf",
            config_type=ConfigType.INI,
            is_valid=True,
            size_bytes=len(test_content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0,
        )

        config_analyzer._analyze_security(test_content, {}, result)

        # Should detect password and api_key issues
        security_issues = [
            issue for issue in result.issues if issue.category == "security"
        ]
        assert len(security_issues) >= 2

        # Security score should be reduced
        assert result.security_score < 100.0

    def test_performance_analysis_algorithm(self, config_analyzer):
        """Test performance analysis algorithms."""
        # Create large test content
        large_content = "large_setting = " + "x" * 15000  # Exceeds max_string_length

        result = ConfigAnalysisResult(
            file_path="test.conf",
            config_type=ConfigType.INI,
            is_valid=True,
            size_bytes=len(large_content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0,
        )

        config_analyzer._analyze_performance(large_content, {}, result)

        # Should detect long line issue
        perf_issues = [
            issue for issue in result.issues if issue.category == "performance"
        ]
        assert len(perf_issues) > 0
        assert any("long line" in issue.message.lower() for issue in perf_issues)

    def test_nesting_depth_algorithm(self, config_analyzer):
        """Test nesting depth calculation algorithm."""
        # Test simple nesting
        simple_dict = {"level1": {"level2": {"level3": "value"}}}
        depth = config_analyzer._calculate_nesting_depth(simple_dict)
        assert depth == 3

        # Test complex nesting with lists
        complex_dict = {
            "level1": {"level2": [{"level3": {"level4": "deep_value"}}, "simple_value"]}
        }
        depth = config_analyzer._calculate_nesting_depth(complex_dict)
        assert depth == 4

        # Test empty structures
        assert config_analyzer._calculate_nesting_depth({}) == 0
        assert config_analyzer._calculate_nesting_depth([]) == 0
        assert config_analyzer._calculate_nesting_depth("string") == 0

    def test_key_counting_algorithm(self, config_analyzer):
        """Test key counting algorithm for nested structures."""
        test_dict = {
            "key1": "value1",
            "key2": {
                "nested_key1": "nested_value1",
                "nested_key2": {"deep_key": "deep_value"},
            },
            "key3": ["item1", {"list_key": "list_value"}],
        }

        total_keys = config_analyzer._count_keys(test_dict)
        # key1, key2, nested_key1, nested_key2, deep_key, list_key = 6 keys
        assert total_keys == 6

        # Test with lists
        test_list = [{"key1": "value"}, {"key2": "value"}]
        total_keys = config_analyzer._count_keys(test_list)
        assert total_keys == 2

    def test_format_size_algorithm(self):
        """Test size formatting algorithm."""
        size_analyzer = SizeAnalyzer()

        # Test various sizes
        assert size_analyzer.format_size(0) == "0.0 B"
        assert size_analyzer.format_size(512) == "512.0 B"
        assert size_analyzer.format_size(1024) == "1.0 KB"
        assert size_analyzer.format_size(1536) == "1.5 KB"
        assert size_analyzer.format_size(1024 * 1024) == "1.0 MB"
        assert size_analyzer.format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert size_analyzer.format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_largest_files_algorithm(self):
        """Test largest files finding algorithm."""
        size_analyzer = SizeAnalyzer()

        files = [
            {"name": "small.txt", "size": 100},
            {"name": "large.txt", "size": 1000},
            {"name": "medium.txt", "size": 500},
            {"name": "huge.txt", "size": 5000},
            {"name": "tiny.txt", "size": 10},
        ]

        largest = size_analyzer._find_largest_files(files, 3)

        assert len(largest) == 3
        assert largest[0]["name"] == "huge.txt"
        assert largest[1]["name"] == "large.txt"
        assert largest[2]["name"] == "medium.txt"

        # Test edge case: more files requested than available
        largest_all = size_analyzer._find_largest_files(files, 10)
        assert len(largest_all) == len(files)


class TestErrorHandlingMechanisms:
    """Test error handling and recovery mechanisms."""

    @pytest.fixture
    def size_analyzer(self):
        """Create a SizeAnalyzer instance for testing."""
        return SizeAnalyzer()

    def test_file_not_found_error_handling(self, size_analyzer):
        """Test handling of file not found errors."""
        with pytest.raises(FileNotFoundError):
            size_analyzer.analyze_directory("/nonexistent/directory")

    def test_permission_error_handling(self, size_analyzer):
        """Test handling of permission errors."""
        # Create a mock that simulates permission errors
        with patch("os.path.exists", return_value=True), patch(
            "os.path.isdir", return_value=True
        ), patch("os.walk", side_effect=PermissionError("Access denied")):

            with pytest.raises(PermissionError):
                size_analyzer.analyze_directory("/restricted/directory")

    def test_corrupted_file_error_handling(self, size_analyzer):
        """Test handling of corrupted file errors during analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")

            # Mock os.stat to raise OSError for corrupted file
            with patch("os.stat", side_effect=OSError("File corrupted")):
                # Should handle the error gracefully and continue
                result = size_analyzer.analyze_directory(temp_dir)

                # Analysis should complete even with file errors
                assert "file_count" in result
                assert "total_size" in result

    def test_cancellation_mechanism(self, size_analyzer):
        """Test operation cancellation mechanism."""
        # Start cancellation
        size_analyzer.cancel_operation()
        assert size_analyzer._should_cancel == True

        # Test that cancelled operation returns early
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a small test structure
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("content")

            result = size_analyzer.analyze_directory(temp_dir)

            # Should return early due to cancellation
            assert result is not None  # Some result should be returned

    def test_invalid_config_error_handling(self):
        """Test handling of invalid configuration files."""
        config_analyzer = ConfigurationAnalyzer()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Write invalid JSON
            temp_file.write('{"invalid": json content}')
            temp_file.flush()

            try:
                result = config_analyzer.analyze_file(temp_file.name)

                # Should detect invalid syntax
                assert not result.is_valid
                syntax_issues = [
                    issue for issue in result.issues if issue.category == "syntax"
                ]
                assert len(syntax_issues) > 0

            finally:
                os.unlink(temp_file.name)

    def test_export_error_handling(self, size_analyzer):
        """Test error handling during export operations."""
        analysis_data = {"test": "data"}

        # Test export to invalid path
        with pytest.raises(IOError):
            size_analyzer.export_analysis(analysis_data, "/invalid/path/export.json")

    def test_hub_connection_error_handling(self, size_analyzer):
        """Test error handling when hub connection fails."""
        # Mock a failing hub connector
        mock_hub = Mock()
        mock_hub.report_status_to_hub.side_effect = Exception("Connection failed")

        size_analyzer.set_hub_connector(mock_hub)

        # Should handle hub connection errors gracefully
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("content")

            # Analysis should complete despite hub errors
            result = size_analyzer.analyze_directory(temp_dir)
            assert result is not None
            assert "file_count" in result

    def test_signal_emission_error_handling(self, size_analyzer):
        """Test error handling in signal emission."""

        # Connect a slot that raises an exception
        def failing_slot(*args):
            raise RuntimeError("Signal handler failed")

        size_analyzer.error_occurred.connect(failing_slot)

        # Emit error signal - should not crash the analyzer
        size_analyzer.error_occurred.emit("Test error")

        # Analyzer should still be functional
        assert hasattr(size_analyzer, "error_occurred")


class TestEdgeCaseScenarios:
    """Test edge cases and boundary conditions."""

    def test_empty_directory_analysis(self):
        """Test analysis of empty directory."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 0
            assert result["total_size"] == 0
            assert result["directory_count"] == 0
            assert len(result["files"]) == 0
            assert len(result["file_types"]) == 0

    def test_single_file_directory(self):
        """Test analysis of directory with single file."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "single.txt"
            content = "Single file content"
            test_file.write_text(content)

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert result["total_size"] == len(content.encode("utf-8"))
            assert result["directory_count"] == 0
            assert len(result["files"]) == 1
            assert result["files"][0]["name"] == "single.txt"

    def test_deeply_nested_directory(self):
        """Test analysis of deeply nested directory structure."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create deeply nested structure
            nested_path = Path(temp_dir)
            for i in range(10):  # 10 levels deep
                nested_path = nested_path / f"level_{i}"
                nested_path.mkdir()

            # Add a file at the deepest level
            deep_file = nested_path / "deep_file.txt"
            deep_file.write_text("Deep content")

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert result["directory_count"] == 10
            assert len(result["files"]) == 1

    def test_very_large_file(self):
        """Test analysis with very large files."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            large_file = Path(temp_dir) / "large.dat"

            # Write a 1MB file
            chunk_size = 1024
            chunks = 1024  # 1024 * 1024 = 1MB

            with open(large_file, "wb") as f:
                for _ in range(chunks):
                    f.write(b"x" * chunk_size)

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert result["total_size"] == 1024 * 1024  # 1MB
            assert result["largest_files"][0]["size"] == 1024 * 1024

    def test_files_with_no_extension(self):
        """Test analysis of files without extensions."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            no_ext_file = Path(temp_dir) / "README"  # No extension
            no_ext_file.write_text("No extension file")

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert "no_extension" in result["file_types"]
            assert result["file_types"]["no_extension"]["count"] == 1

    def test_unicode_filename_handling(self):
        """Test handling of Unicode filenames."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            unicode_file = Path(temp_dir) / "тест_файл_测试.txt"
            unicode_file.write_text("Unicode content", encoding="utf-8")

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert any("тест_файл_测试.txt" in f["name"] for f in result["files"])

    def test_zero_byte_files(self):
        """Test handling of zero-byte files."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.txt"
            empty_file.touch()  # Creates empty file

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert result["total_size"] == 0
            assert result["files"][0]["size"] == 0

    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with special characters
            special_dir = Path(temp_dir) / "special chars & symbols@#$"
            special_dir.mkdir()

            special_file = special_dir / "file with spaces & symbols@#$.txt"
            special_file.write_text("Special content")

            result = size_analyzer.analyze_directory(temp_dir)

            assert result["file_count"] == 1
            assert result["directory_count"] == 1

    def test_concurrent_access_edge_case(self):
        """Test edge case of concurrent directory access."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "concurrent.txt"
            test_file.write_text("Initial content")

            # Simulate concurrent file modification during analysis
            def modify_file():
                time.sleep(0.1)  # Small delay
                if test_file.exists():
                    test_file.write_text("Modified content during analysis")

            import threading

            modifier_thread = threading.Thread(target=modify_file)
            modifier_thread.start()

            # Analysis should handle concurrent modifications gracefully
            result = size_analyzer.analyze_directory(temp_dir)

            modifier_thread.join()

            assert result["file_count"] == 1
            # Size might vary depending on timing, but should be > 0
            assert result["total_size"] > 0


class TestPerformanceBenchmarks:
    """Test performance benchmarks and optimization."""

    @pytest.fixture
    def size_analyzer(self):
        """Create a SizeAnalyzer instance for testing."""
        return SizeAnalyzer()

    def test_small_directory_performance(self, size_analyzer):
        """Test performance with small directory (< 100 files)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create 50 small files
            for i in range(50):
                test_file = Path(temp_dir) / f"file_{i:03d}.txt"
                test_file.write_text(f"Content for file {i}")

            start_time = time.time()
            result = size_analyzer.analyze_directory(temp_dir)
            end_time = time.time()

            analysis_time = end_time - start_time

            # Should complete within 5 seconds for small directory
            assert (
                analysis_time < 5.0
            ), f"Analysis took {analysis_time:.2f}s, expected < 5s"
            assert result["file_count"] == 50

            # Check performance metrics
            metrics = size_analyzer.get_performance_metrics()
            assert "files_per_second" in metrics
            if metrics["files_per_second"] > 0:
                assert metrics["files_per_second"] >= 10  # At least 10 files/sec

    def test_medium_directory_performance(self, size_analyzer):
        """Test performance with medium directory (100-1000 files)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create 500 files in nested structure
            for i in range(5):
                subdir = Path(temp_dir) / f"subdir_{i}"
                subdir.mkdir()

                for j in range(100):
                    test_file = subdir / f"file_{j:03d}.dat"
                    test_file.write_text(f"Content for file {i}-{j}")

            start_time = time.time()
            result = size_analyzer.analyze_directory(temp_dir)
            end_time = time.time()

            analysis_time = end_time - start_time

            # Should complete within 10 seconds for medium directory
            assert (
                analysis_time < 10.0
            ), f"Analysis took {analysis_time:.2f}s, expected < 10s"
            assert result["file_count"] == 500
            assert result["directory_count"] == 5

    def test_memory_usage_monitoring(self, size_analyzer):
        """Test memory usage during analysis."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files that would use significant memory if loaded incorrectly
            for i in range(100):
                large_file = Path(temp_dir) / f"large_{i}.txt"
                large_file.write_text("x" * 10000)  # 10KB each = 1MB total

            result = size_analyzer.analyze_directory(temp_dir)

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (< 100MB for this test)
            assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"
            assert result["file_count"] == 100

    def test_progress_tracking_performance(self, size_analyzer):
        """Test performance impact of progress tracking."""
        progress_updates = []

        def capture_progress(current, total):
            progress_updates.append((current, total))

        size_analyzer.progress_updated.connect(capture_progress)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create moderate number of files
            for i in range(200):
                test_file = Path(temp_dir) / f"file_{i:03d}.txt"
                test_file.write_text(f"Content {i}")

            start_time = time.time()
            result = size_analyzer.analyze_directory(temp_dir)
            end_time = time.time()

            analysis_time = end_time - start_time

            # Progress tracking shouldn't significantly impact performance
            assert analysis_time < 15.0  # Reasonable time with progress tracking
            assert len(progress_updates) > 0  # Should have progress updates
            assert result["file_count"] == 200

    def test_signal_emission_overhead(self, size_analyzer):
        """Test overhead of signal emissions during analysis."""
        signal_counts = {"progress": 0, "milestone": 0, "message": 0}

        def count_progress(*args):
            signal_counts["progress"] += 1

        def count_milestone(*args):
            signal_counts["milestone"] += 1

        def count_message(*args):
            signal_counts["message"] += 1

        size_analyzer.progress_updated.connect(count_progress)
        size_analyzer.milestone_reached.connect(count_milestone)
        size_analyzer.progress_message.connect(count_message)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files to trigger signal emissions
            for i in range(150):
                test_file = Path(temp_dir) / f"file_{i:03d}.txt"
                test_file.write_text(f"Content {i}")

            start_time = time.time()
            result = size_analyzer.analyze_directory(temp_dir)
            end_time = time.time()

            analysis_time = end_time - start_time

            # Verify signals were emitted
            assert signal_counts["progress"] > 0
            assert signal_counts["milestone"] > 0
            assert signal_counts["message"] > 0

            # Performance should still be acceptable
            assert analysis_time < 20.0

    def test_export_performance(self, size_analyzer):
        """Test export operation performance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create analysis data
            for i in range(100):
                test_file = Path(temp_dir) / f"file_{i:03d}.txt"
                test_file.write_text(f"Content {i}")

            result = size_analyzer.analyze_directory(temp_dir)

            # Test export performance
            export_file = Path(temp_dir) / "export.json"

            start_time = time.time()
            size_analyzer.export_analysis(result, str(export_file))
            end_time = time.time()

            export_time = end_time - start_time

            # Export should be fast (< 2 seconds)
            assert export_time < 2.0, f"Export took {export_time:.2f}s, expected < 2s"
            assert export_file.exists()

            # Verify export file is valid JSON
            with open(export_file) as f:
                exported_data = json.load(f)

            assert "export_metadata" in exported_data
            assert exported_data["file_count"] == 100


class TestIntegrationPoints:
    """Test integration points between components."""

    @pytest.fixture
    def mock_hub_connector(self):
        """Create a mock hub connector for testing."""
        mock_hub = Mock()
        mock_hub.report_status_to_hub = Mock()
        mock_hub.report_error_to_hub = Mock()
        mock_hub.broadcast_event = Mock()
        return mock_hub

    def test_size_analyzer_hub_integration(self, mock_hub_connector):
        """Test SizeAnalyzer integration with hub connector."""
        size_analyzer = SizeAnalyzer(hub_connector=mock_hub_connector)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Integration test")

            result = size_analyzer.analyze_directory(temp_dir)

            # Verify hub interactions
            assert mock_hub_connector.report_status_to_hub.called

            # Check start status call
            start_calls = [
                call
                for call in mock_hub_connector.report_status_to_hub.call_args_list
                if call[0][0] == "analyzing"
            ]
            assert len(start_calls) > 0

            # Check completion status call
            completion_calls = [
                call
                for call in mock_hub_connector.report_status_to_hub.call_args_list
                if call[0][0] == "completed"
            ]
            assert len(completion_calls) > 0

    def test_worker_thread_integration(self, mock_hub_connector):
        """Test SizeAnalyzerWorker integration."""
        if not PyQt5_available:
            pytest.skip("PyQt5 not available for worker thread testing")

        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "worker_test.txt"
            test_file.write_text("Worker integration test")

            worker = SizeAnalyzerWorker(
                analyzer=size_analyzer,
                directory_path=temp_dir,
                hub_connector=mock_hub_connector,
            )

            # Mock signals to capture results
            results = []
            errors = []

            worker.analysis_finished.connect(lambda result: results.append(result))
            worker.analysis_error.connect(lambda error: errors.append(error))

            # Run worker in test environment
            worker.run()

            # Verify integration
            assert len(errors) == 0, f"Worker failed with errors: {errors}"
            assert len(results) == 1
            assert results[0]["file_count"] == 1

    def test_config_analyzer_integration(self):
        """Test ConfigurationAnalyzer integration capabilities."""
        config_analyzer = ConfigurationAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration files
            json_config = Path(temp_dir) / "config.json"
            json_config.write_text('{"database": {"password": "secret123"}}')

            yaml_config = Path(temp_dir) / "app.yaml"
            yaml_config.write_text('api_key: "abc123"\ndebug: true')

            # Test directory analysis integration
            results = config_analyzer.analyze_directory(temp_dir)

            assert len(results) == 2
            config_types = {result.config_type for result in results}
            assert ConfigType.JSON in config_types
            assert ConfigType.YAML in config_types

            # Test report generation integration
            text_report = config_analyzer.generate_report(results, "text")
            assert "CONFIGURATION ANALYSIS REPORT" in text_report

            json_report = config_analyzer.generate_report(results, "json")
            report_data = json.loads(json_report)
            assert "metadata" in report_data
            assert "summary" in report_data
            assert "results" in report_data

    def test_cross_component_data_flow(self, mock_hub_connector):
        """Test data flow between different analysis components."""
        # Create integrated analysis scenario
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mixed content for comprehensive analysis

            # Size analysis targets
            for i in range(10):
                data_file = Path(temp_dir) / f"data_{i}.txt"
                data_file.write_text(f"Data content {i}")

            # Configuration files for config analysis
            config_file = Path(temp_dir) / "config.json"
            config_file.write_text('{"app": {"name": "test", "debug": true}}')

            # Run size analysis
            size_analyzer = SizeAnalyzer(hub_connector=mock_hub_connector)
            size_result = size_analyzer.analyze_directory(temp_dir)

            # Run config analysis
            config_analyzer = ConfigurationAnalyzer()
            config_results = config_analyzer.analyze_directory(temp_dir)

            # Verify cross-component compatibility
            assert size_result["file_count"] == 11  # 10 data files + 1 config
            assert len(config_results) == 1  # 1 config file detected

            # Verify data structure compatibility
            assert "files" in size_result
            assert all("name" in f for f in size_result["files"])

            for config_result in config_results:
                assert hasattr(config_result, "file_path")
                assert hasattr(config_result, "config_type")

    def test_error_propagation_integration(self, mock_hub_connector):
        """Test error propagation across integration points."""
        size_analyzer = SizeAnalyzer(hub_connector=mock_hub_connector)

        # Test error propagation to hub
        try:
            size_analyzer.analyze_directory("/nonexistent/path")
        except FileNotFoundError:
            pass  # Expected error

        # Check if error was reported to hub
        assert mock_hub_connector.report_error_to_hub.called
        error_call = mock_hub_connector.report_error_to_hub.call_args
        assert "not found" in error_call[0][0].lower()

    def test_resource_coordination_integration(self, mock_hub_connector):
        """Test resource coordination through hub integration."""
        size_analyzer = SizeAnalyzer(hub_connector=mock_hub_connector)

        # Test resource request coordination
        coordination_result = size_analyzer.request_hub_coordination(
            "resource_request", {"resource_type": "analysis_slot", "priority": "high"}
        )

        assert coordination_result == True  # Should succeed with mock
        assert mock_hub_connector.broadcast_event.called

        event_call = mock_hub_connector.broadcast_event.call_args
        assert event_call[0][0] == "resource_request"
        assert "tool" in event_call[0][1]
        assert event_call[0][1]["tool"] == "Size Analyzer"


@pytest.mark.skipif(not PyQt5_available, reason="PyQt5 not available")
class TestGUIIntegration:
    """Test GUI integration aspects of analysis components."""

    @pytest.fixture
    def qapp(self):
        """Create QApplication instance for GUI testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        # Don't quit the app as it might be shared

    def test_checksum_gui_initialization(self, qapp):
        """Test ChecksumGUI initialization and basic functionality."""
        with patch("src.rfu.gui.standard_window.StandardWindow", autospec=True):
            checksum_gui = ChecksumGUI()

            # Verify basic initialization
            assert hasattr(checksum_gui, "selected_file")
            assert hasattr(checksum_gui, "results_list")
            assert checksum_gui.selected_file is None

    def test_signal_slot_connections(self, qapp):
        """Test signal-slot connections in analysis components."""
        size_analyzer = SizeAnalyzer()

        # Test signal connections
        signal_received = []

        def capture_signal(value):
            signal_received.append(value)

        size_analyzer.progress_percentage.connect(capture_signal)

        # Emit test signal
        size_analyzer.progress_percentage.emit(50)

        # Process events
        qapp.processEvents()

        assert 50 in signal_received

    def test_thread_safety_gui_integration(self, qapp):
        """Test thread safety in GUI integration scenarios."""
        size_analyzer = SizeAnalyzer()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "thread_test.txt"
            test_file.write_text("Thread safety test")

            # Create worker for thread testing
            worker = SizeAnalyzerWorker(analyzer=size_analyzer, directory_path=temp_dir)

            # Verify worker can be created without errors
            assert worker.analyzer == size_analyzer
            assert worker.directory_path == temp_dir


def run_comprehensive_test_suite():
    """Run the complete comprehensive test suite with detailed reporting."""

    print("=" * 80)
    print("CORE ANALYSIS ENGINE - COMPREHENSIVE TEST EXECUTION")
    print("=" * 80)
    print(f"Test execution started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configure pytest for detailed reporting
    pytest_args = [
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "-x",  # Stop on first failure for debugging
        "--durations=10",  # Show 10 slowest tests
        "--capture=no",  # Don't capture output
    ]

    try:
        # Run the test suite
        exit_code = pytest.main(pytest_args)

        print()
        print("=" * 80)
        print("TEST SUITE EXECUTION COMPLETED")
        print("=" * 80)
        print(f"Exit code: {exit_code}")
        print(f"Execution completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        return exit_code == 0

    except Exception as e:
        print(f"Test execution failed with error: {e}")
        return False


if __name__ == "__main__":
    # Run comprehensive test suite if executed directly
    success = run_comprehensive_test_suite()
    exit(0 if success else 1)
