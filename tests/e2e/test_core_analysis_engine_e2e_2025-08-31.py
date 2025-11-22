#!/usr/bin/env python3
# flake8: noqa
"""
Core Analysis Engine End-to-End Test Suite

This test suite provides comprehensive end-to-end testing for the Core Analysis Engine,
validating complete workflows from initialization through final results delivery.

Created: August 31, 2025
Coverage: Core Analysis Engine - End-to-end workflow validation
Priority: HIGH (addressing missing E2E test coverage)
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from src.tools.analysis.size_analyzer.size_analyzer_config import (
        SizeAnalyzerConfig,
    )
    from src.tools.analysis.size_analyzer.size_analyzer_logging import (
        SizeAnalyzerLogger,
    )
    from src.tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False

# Skip all tests if imports fail
pytestmark = pytest.mark.skipif(
    not IMPORTS_SUCCESSFUL, reason="Required modules not available"
)


class TestCompleteAnalysisWorkflows:
    """End-to-end testing of complete analysis workflows."""

    @pytest.fixture
    def real_world_dataset(self):
        """Create realistic dataset mimicking real-world directory structures."""
        temp_dir = tempfile.mkdtemp(prefix="e2e_real_world_")

        # Simulate a realistic project directory
        structure = {
            "src": {
                "main": {
                    "java": {
                        "com": {
                            "example": {
                                "Main.java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n    }\n}',
                                "util": {
                                    "Helper.java": "public class Helper {\n    // Helper methods\n}",
                                    "Logger.java": "public class Logger {\n    // Logging functionality\n}",
                                },
                            }
                        }
                    },
                    "resources": {
                        "config.properties": "app.name=TestApp\napp.version=1.0.0\n",
                        "application.yaml": "server:\n  port: 8080\nspring:\n  application:\n    name: test-app\n",
                    },
                },
                "test": {
                    "java": {
                        "com": {
                            "example": {
                                "MainTest.java": "public class MainTest {\n    // Test methods\n}",
                                "util": {
                                    "HelperTest.java": "public class HelperTest {\n    // Helper tests\n}"
                                },
                            }
                        }
                    }
                },
            },
            "docs": {
                "README.md": "# Test Project\n\nThis is a test project for analysis.",
                "api": {
                    "api-docs.html": "<html><body><h1>API Documentation</h1></body></html>"
                },
            },
            "target": {
                "classes": {
                    "com": {
                        "example": {
                            "Main.class": b"\xca\xfe\xba\xbe"
                            + b"fake class file" * 50  # Simulate compiled class
                        }
                    }
                }
            },
            "logs": {
                "application.log": "INFO: Application started\nINFO: Processing data\nERROR: Sample error\n"
                * 100,
                "debug.log": "DEBUG: Detailed logging\n" * 200,
            },
            ".git": {
                "config": "[core]\n    repositoryformatversion = 0\n",
                "HEAD": "ref: refs/heads/main\n",
            },
        }

        def create_structure(base_path, struct):
            for name, content in struct.items():
                path = os.path.join(base_path, name)
                if isinstance(content, dict):
                    os.makedirs(path, exist_ok=True)
                    create_structure(path, content)
                else:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    mode = "wb" if isinstance(content, bytes) else "w"
                    with open(path, mode) as f:
                        f.write(content)

        create_structure(temp_dir, structure)

        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_complete_project_analysis_workflow(self, qapp, real_world_dataset):
        """Test complete analysis workflow on realistic project structure."""
        # Initialize all components
        config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=config)
        analyzer = SizeAnalyzer()

        # Track workflow events
        workflow_events = []
        results_data = {}

        def track_progress(current, total):
            workflow_events.append(f"Progress: {current}/{total}")

        def track_percentage(percentage):
            workflow_events.append(f"Percentage: {percentage}%")

        def track_message(message):
            workflow_events.append(f"Message: {message}")

        def track_milestone(milestone, percentage):
            workflow_events.append(f"Milestone: {milestone} ({percentage}%)")

        def track_completion(result):
            results_data.update(result)

        def track_error(error):
            workflow_events.append(f"Error: {error}")

        # Connect all signals
        analyzer.progress_updated.connect(track_progress)
        analyzer.progress_percentage.connect(track_percentage)
        analyzer.progress_message.connect(track_message)
        analyzer.milestone_reached.connect(track_milestone)
        analyzer.analysis_complete.connect(track_completion)
        analyzer.error_occurred.connect(track_error)

        # Execute complete workflow
        start_time = time.time()
        result = analyzer.analyze_directory(real_world_dataset, top_files_count=15)
        end_time = time.time()

        # Verify workflow completion
        assert result is not None
        assert len(workflow_events) > 0

        # Verify comprehensive results
        assert "total_size" in result
        assert "file_count" in result
        assert "directory_count" in result
        assert "files" in result
        assert "file_types" in result
        assert "largest_files" in result
        assert "directory_tree" in result

        # Verify realistic expectations
        assert result["file_count"] >= 10  # Should find multiple files
        assert result["directory_count"] >= 5  # Should find multiple directories
        assert result["total_size"] > 0

        # Verify file type analysis
        expected_extensions = [".java", ".md", ".properties", ".yaml", ".log"]
        found_extensions = list(result["file_types"].keys())

        # Should find at least some expected file types
        common_extensions = set(expected_extensions) & set(found_extensions)
        assert len(common_extensions) >= 2

        # Verify largest files analysis
        assert len(result["largest_files"]) <= 15
        if len(result["largest_files"]) > 1:
            # Should be sorted by size (largest first)
            for i in range(len(result["largest_files"]) - 1):
                assert (
                    result["largest_files"][i]["size"]
                    >= result["largest_files"][i + 1]["size"]
                )

        # Verify workflow timing
        workflow_time = end_time - start_time
        assert workflow_time < 30  # Should complete within 30 seconds

        # Verify signal progression
        progress_events = [e for e in workflow_events if "Progress:" in e]
        percentage_events = [e for e in workflow_events if "Percentage:" in e]
        milestone_events = [e for e in workflow_events if "Milestone:" in e]

        assert len(progress_events) > 0
        assert len(percentage_events) > 0
        assert len(milestone_events) > 0

    def test_multi_filter_analysis_workflow(self, qapp, real_world_dataset):
        """Test workflow with multiple filtering criteria."""
        analyzer = SizeAnalyzer()

        # Test 1: Java files only
        java_result = analyzer.analyze_directory(
            real_world_dataset, include_extensions=[".java"]
        )

        assert java_result is not None
        assert all(f["name"].endswith(".java") for f in java_result["files"])
        assert ".java" in java_result["file_types"]

        # Test 2: Configuration files only
        config_result = analyzer.analyze_directory(
            real_world_dataset, include_extensions=[".properties", ".yaml", ".yml"]
        )

        assert config_result is not None
        config_extensions = {f["extension"] for f in config_result["files"]}
        assert config_extensions.issubset({".properties", ".yaml", ".yml"})

        # Test 3: Large files analysis
        all_result = analyzer.analyze_directory(real_world_dataset, top_files_count=5)

        assert all_result is not None
        assert len(all_result["largest_files"]) <= 5

    def test_error_recovery_workflow(self, qapp, real_world_dataset):
        """Test complete workflow with error conditions and recovery."""
        analyzer = SizeAnalyzer()

        errors_captured = []

        def capture_error(error):
            errors_captured.append(error)

        analyzer.error_occurred.connect(capture_error)

        # Test 1: Normal operation
        normal_result = analyzer.analyze_directory(real_world_dataset)
        assert normal_result is not None

        # Test 2: Simulate permission errors on some files
        with patch("os.path.getsize") as mock_getsize:
            # Make some files throw permission errors
            original_getsize = os.path.getsize

            def selective_error(path):
                if "debug.log" in path:
                    raise PermissionError("Access denied")
                return original_getsize(path)

            mock_getsize.side_effect = selective_error

            partial_result = analyzer.analyze_directory(real_world_dataset)

            # Should still complete analysis
            assert partial_result is not None
            assert partial_result["file_count"] >= 0

        # Test 3: Simulate file system errors
        with patch("os.walk") as mock_walk:
            # Make os.walk partially fail
            def partial_walk(path):
                for i, (root, dirs, files) in enumerate(os.walk(path)):
                    if i > 3:  # Fail after processing some directories
                        raise OSError("File system error")
                    yield root, dirs, files

            mock_walk.side_effect = partial_walk

            try:
                error_result = analyzer.analyze_directory(real_world_dataset)
                # May succeed with partial results
                if error_result:
                    assert error_result["file_count"] >= 0
            except OSError:
                # Or may propagate the error
                pass

    def test_cancellation_workflow(self, qapp, real_world_dataset):
        """Test complete workflow with user cancellation."""
        analyzer = SizeAnalyzer()

        cancellation_events = []

        def track_cancellation():
            cancellation_events.append("Cancelled")

        analyzer.operation_cancelled.connect(track_cancellation)

        # Test cancellation during analysis
        def cancel_after_delay():
            time.sleep(0.2)  # Let analysis start
            analyzer.cancel_analysis()

        cancel_thread = threading.Thread(target=cancel_after_delay)
        cancel_thread.start()

        start_time = time.time()
        result = analyzer.analyze_directory(real_world_dataset)
        cancellation_time = time.time() - start_time

        cancel_thread.join()

        # Should respond to cancellation quickly
        assert cancellation_time < 5  # Should cancel within 5 seconds
        assert analyzer._should_cancel

    def test_performance_monitoring_workflow(self, qapp, real_world_dataset):
        """Test workflow with comprehensive performance monitoring."""
        analyzer = SizeAnalyzer()

        # Monitor memory usage during analysis
        initial_memory = self._get_memory_usage()

        result = analyzer.analyze_directory(real_world_dataset)

        final_memory = self._get_memory_usage()

        # Verify analysis completed
        assert result is not None

        # Check performance metrics collection
        metrics = analyzer._performance_metrics
        assert "start_time" in metrics
        assert "end_time" in metrics

        # Verify reasonable resource usage
        memory_increase = final_memory - initial_memory
        assert memory_increase < 200 * 1024 * 1024  # Less than 200MB increase

        # Verify performance calculations
        if result["file_count"] > 0 and metrics["end_time"] and metrics["start_time"]:
            duration = (metrics["end_time"] - metrics["start_time"]).total_seconds()
            if duration > 0:
                expected_fps = result["file_count"] / duration
                expected_bps = result["total_size"] / duration

                assert expected_fps >= 0
                assert expected_bps >= 0

    def test_export_workflow_integration(self, qapp, real_world_dataset):
        """Test complete workflow including result export capabilities."""
        analyzer = SizeAnalyzer()

        # Perform analysis
        result = analyzer.analyze_directory(real_world_dataset)
        assert result is not None

        # Test JSON export capability
        temp_export_dir = tempfile.mkdtemp(prefix="export_test_")

        try:
            json_file = os.path.join(temp_export_dir, "analysis_results.json")

            # Export results to JSON
            with open(json_file, "w") as f:
                json.dump(result, f, indent=2, default=str)

            # Verify export
            assert os.path.exists(json_file)

            # Verify exported data integrity
            with open(json_file, "r") as f:
                exported_data = json.load(f)

            assert exported_data["file_count"] == result["file_count"]
            assert exported_data["total_size"] == result["total_size"]
            assert exported_data["directory_count"] == result["directory_count"]

        finally:
            shutil.rmtree(temp_export_dir, ignore_errors=True)

    def test_hub_integration_workflow(self, qapp, real_world_dataset):
        """Test complete workflow with hub integration."""
        # Create mock hub connector
        mock_hub = Mock()
        mock_hub.report_status_to_hub = Mock()
        mock_hub.get_resource_allocation = Mock(return_value={"max_threads": 4})

        analyzer = SizeAnalyzer(hub_connector=mock_hub)

        # Execute analysis with hub integration
        result = analyzer.analyze_directory(real_world_dataset)

        assert result is not None

        # Verify hub interactions
        assert mock_hub.report_status_to_hub.called

        # Verify status reporting sequence
        call_args = mock_hub.report_status_to_hub.call_args_list
        assert len(call_args) > 0

        # First call should be analysis start
        first_call = call_args[0]
        assert first_call[0][0] == "analyzing"
        assert "directory" in first_call[0][1]
        assert "start_time" in first_call[0][1]

    def _get_memory_usage(self):
        """Get current memory usage for monitoring."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0


class TestRealWorldScenarios:
    """Test scenarios based on real-world usage patterns."""

    def test_large_codebase_analysis(self, qapp):
        """Test analysis of large codebase structure."""
        temp_dir = tempfile.mkdtemp(prefix="large_codebase_")

        try:
            # Simulate large codebase
            languages = ["java", "py", "js", "cpp", "h"]

            for lang in languages:
                lang_dir = os.path.join(temp_dir, f"{lang}_src")
                os.makedirs(lang_dir, exist_ok=True)

                for i in range(100):  # 100 files per language
                    filename = f"module_{i:03d}.{lang}"
                    filepath = os.path.join(lang_dir, filename)

                    with open(filepath, "w") as f:
                        f.write(f"// {lang.upper()} source file {i}\n")
                        f.write("// Sample code content\n" * 50)

            analyzer = SizeAnalyzer()
            result = analyzer.analyze_directory(temp_dir)

            assert result is not None
            assert result["file_count"] == 500  # 100 files * 5 languages

            # Verify all languages detected
            found_extensions = set(result["file_types"].keys())
            expected_extensions = {f".{lang}" for lang in languages}
            assert expected_extensions.issubset(found_extensions)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_mixed_media_directory_analysis(self, qapp):
        """Test analysis of directory with mixed media files."""
        temp_dir = tempfile.mkdtemp(prefix="mixed_media_")

        try:
            # Create mixed media files
            media_types = [
                ("images", ["jpg", "png", "gif"], 1024 * 10),  # 10KB images
                ("videos", ["mp4", "avi", "mov"], 1024 * 1024),  # 1MB videos
                ("audio", ["mp3", "wav", "flac"], 1024 * 100),  # 100KB audio
                ("documents", ["pdf", "doc", "txt"], 1024 * 5),  # 5KB docs
            ]

            total_files = 0

            for category, extensions, size in media_types:
                cat_dir = os.path.join(temp_dir, category)
                os.makedirs(cat_dir, exist_ok=True)

                for ext in extensions:
                    for i in range(10):  # 10 files per extension
                        filename = f"{category}_{i:02d}.{ext}"
                        filepath = os.path.join(cat_dir, filename)

                        with open(filepath, "wb") as f:
                            f.write(b"x" * size)

                        total_files += 1

            analyzer = SizeAnalyzer()
            result = analyzer.analyze_directory(temp_dir)

            assert result is not None
            assert result["file_count"] == total_files

            # Verify size categories
            large_files = [f for f in result["files"] if f["size"] > 100 * 1024]
            assert len(large_files) > 0  # Should find some large files

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_deep_nested_structure_analysis(self, qapp):
        """Test analysis of deeply nested directory structure."""
        temp_dir = tempfile.mkdtemp(prefix="deep_nested_")

        try:
            # Create deep nesting (20 levels)
            current_path = temp_dir

            for level in range(20):
                current_path = os.path.join(current_path, f"level_{level:02d}")
                os.makedirs(current_path, exist_ok=True)

                # Add a file at each level
                filepath = os.path.join(current_path, f"file_at_level_{level}.txt")
                with open(filepath, "w") as f:
                    f.write(f"Content at nesting level {level}\n" * 10)

            analyzer = SizeAnalyzer()
            result = analyzer.analyze_directory(temp_dir)

            assert result is not None
            assert result["file_count"] == 20  # One file per level
            assert result["directory_count"] >= 20  # At least 20 directories

            # Verify deep nesting handled correctly
            assert result["total_size"] > 0

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# Test runner configuration
def run_end_to_end_tests():
    """Run the comprehensive end-to-end test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=15",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3",  # Stop after 3 failures
    ]

    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing
    try:
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass

    # Run the tests
    print("Starting Core Analysis Engine End-to-End Tests...")
    exit_code = run_end_to_end_tests()

    print(f"\nEnd-to-End Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)
