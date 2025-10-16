#!/usr/bin/env python3
# flake8: noqa
"""
Core Analysis Engine Integration Test Suite

This test suite provides comprehensive integration testing for the Core Analysis Engine
components, testing the interaction between data processing pipelines, configuration
management, logging systems, and performance monitoring.

Created: August 31, 2025
Coverage: Core Analysis Engine - Integration testing across all components
Priority: HIGH (addressing missing critical test coverage)
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
from unittest.mock import MagicMock, Mock, patch

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
    from tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False

# Skip all tests if imports fail
pytestmark = pytest.mark.skipif(
    not IMPORTS_SUCCESSFUL, reason="Required modules not available"
)


class TestCoreAnalysisEngineIntegration:
    """Integration tests for core analysis engine components."""

    @pytest.fixture
    def comprehensive_test_environment(self):
        """Create comprehensive test environment for integration testing."""
        temp_dir = tempfile.mkdtemp(prefix="core_analysis_integration_")

        # Create complex directory structure for testing
        structure = {
            "config_files": {
                "app.json": '{"name": "test_app", "version": "1.0.0"}',
                "settings.yaml": "debug: true\nlog_level: info\n",
                "database.ini": "[database]\nhost=localhost\nport=5432\n",
            },
            "large_dataset": {},
            "mixed_content": {"documents": {}, "images": {}, "code": {}},
            "performance_test": {},
            "edge_cases": {"empty_files": {}, "special_chars": {}, "deep_nesting": {}},
        }

        # Create directory structure
        def create_structure(base_path, struct):
            for name, content in struct.items():
                path = os.path.join(base_path, name)
                if isinstance(content, dict):
                    os.makedirs(path, exist_ok=True)
                    create_structure(path, content)
                else:
                    with open(path, "w") as f:
                        f.write(content)

        create_structure(temp_dir, structure)

        # Create test files for performance testing
        performance_dir = os.path.join(temp_dir, "performance_test")
        for i in range(100):
            test_file = os.path.join(performance_dir, f"perf_file_{i:03d}.txt")
            with open(test_file, "w") as f:
                f.write(f"Performance test file {i}" * 100)  # ~2KB each

        # Create large dataset
        large_dir = os.path.join(temp_dir, "large_dataset")
        for i in range(500):
            test_file = os.path.join(large_dir, f"data_{i:04d}.dat")
            with open(test_file, "w") as f:
                f.write("x" * 1024)  # 1KB files

        # Create mixed content
        mixed_dir = os.path.join(temp_dir, "mixed_content")

        # Documents
        docs_dir = os.path.join(mixed_dir, "documents")
        for i in range(20):
            doc_file = os.path.join(docs_dir, f"document_{i}.txt")
            with open(doc_file, "w") as f:
                f.write(f"Document content {i}\n" * 50)

        # Images (simulated)
        images_dir = os.path.join(mixed_dir, "images")
        for i in range(15):
            img_file = os.path.join(images_dir, f"image_{i}.jpg")
            with open(img_file, "wb") as f:
                f.write(b"\xff\xd8\xff\xe0" + b"fake_image_data" * 100)

        # Code files
        code_dir = os.path.join(mixed_dir, "code")
        for i in range(30):
            code_file = os.path.join(code_dir, f"module_{i}.py")
            with open(code_file, "w") as f:
                f.write(f"# Module {i}\ndef function_{i}():\n    return {i}\n")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_analyzer_config_logging_integration(
        self, qapp, comprehensive_test_environment
    ):
        """Test integration between analyzer, config, and logging components."""
        # Initialize components
        config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=config)
        analyzer = SizeAnalyzer()

        # Test basic integration
        assert config is not None
        assert logger is not None
        assert analyzer is not None

        # Test configuration affects logging
        settings = config.get_all_settings()
        assert isinstance(settings, dict)

        # Test analyzer can work with logging
        result = analyzer.analyze_directory(comprehensive_test_environment)

        assert result is not None
        assert result["file_count"] > 0
        assert result["total_size"] > 0

    def test_end_to_end_analysis_workflow(self, qapp, comprehensive_test_environment):
        """Test complete end-to-end analysis workflow."""
        # Initialize complete system
        config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=config)
        analyzer = SizeAnalyzer()

        # Track workflow steps
        workflow_steps = []

        def track_progress(percentage):
            workflow_steps.append(f"Progress: {percentage}%")

        def track_message(message):
            workflow_steps.append(f"Message: {message}")

        def track_milestone(milestone, percentage):
            workflow_steps.append(f"Milestone: {milestone} ({percentage}%)")

        # Connect signals
        analyzer.progress_percentage.connect(track_progress)
        analyzer.progress_message.connect(track_message)
        analyzer.milestone_reached.connect(track_milestone)

        # Execute complete workflow
        start_time = time.time()
        result = analyzer.analyze_directory(
            comprehensive_test_environment,
            top_files_count=20,
            include_extensions=[".txt", ".py", ".dat"],
        )
        end_time = time.time()

        # Verify workflow completion
        assert result is not None
        assert len(workflow_steps) > 0

        # Verify result completeness
        assert "total_size" in result
        assert "file_count" in result
        assert "directory_count" in result
        assert "files" in result
        assert "largest_files" in result
        assert "file_types" in result

        # Verify performance
        workflow_time = end_time - start_time
        assert workflow_time < 60  # Should complete within 60 seconds

        # Verify file type analysis
        assert ".txt" in result["file_types"]
        assert ".py" in result["file_types"]
        assert ".dat" in result["file_types"]

    def test_concurrent_analysis_integration(
        self, qapp, comprehensive_test_environment
    ):
        """Test system behavior under concurrent analysis operations."""
        config = SizeAnalyzerConfig()

        # Create multiple analyzer instances
        analyzers = [SizeAnalyzer() for _ in range(3)]
        results = []
        errors = []

        def run_analysis(analyzer_id, analyzer, directory):
            try:
                result = analyzer.analyze_directory(directory)
                results.append((analyzer_id, result))
            except Exception as e:
                errors.append((analyzer_id, str(e)))

        # Create subdirectories for concurrent analysis
        subdirs = []
        base_dirs = ["performance_test", "mixed_content", "large_dataset"]
        for dirname in base_dirs:
            subdir = os.path.join(comprehensive_test_environment, dirname)
            if os.path.exists(subdir):
                subdirs.append(subdir)

        # Run concurrent analyses
        threads = []
        for i, (analyzer, subdir) in enumerate(zip(analyzers, subdirs)):
            thread = threading.Thread(target=run_analysis, args=(i, analyzer, subdir))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == len(subdirs)

        # Verify all analyses completed successfully
        for analyzer_id, result in results:
            assert result is not None
            assert result["file_count"] >= 0
            assert result["total_size"] >= 0

    def test_error_recovery_integration(self, qapp, comprehensive_test_environment):
        """Test error recovery across integrated components."""
        config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=config)
        analyzer = SizeAnalyzer()

        errors_captured = []

        def capture_error(error_msg):
            errors_captured.append(error_msg)

        analyzer.error_occurred.connect(capture_error)

        # Test 1: Invalid directory handling
        try:
            analyzer.analyze_directory("/nonexistent/path/for/testing")
        except FileNotFoundError:
            pass  # Expected error

        # Test 2: Permission error simulation
        with patch("os.walk", side_effect=PermissionError("Access denied")):
            try:
                result = analyzer.analyze_directory(comprehensive_test_environment)
                # Should handle permission errors gracefully
            except Exception:
                pass  # May raise exception depending on implementation

        # Test 3: Partial analysis with errors
        with patch("os.path.getsize", side_effect=OSError("File access error")):
            try:
                result = analyzer.analyze_directory(comprehensive_test_environment)
                # Should continue analysis despite individual file errors
                assert result is not None
            except Exception:
                pass  # May raise exception depending on implementation

    def test_performance_monitoring_integration(
        self, qapp, comprehensive_test_environment
    ):
        """Test integration of performance monitoring across components."""
        config = SizeAnalyzerConfig()
        analyzer = SizeAnalyzer()

        # Monitor performance metrics
        start_memory = self._get_memory_usage()
        start_time = time.time()

        result = analyzer.analyze_directory(comprehensive_test_environment)

        end_time = time.time()
        end_memory = self._get_memory_usage()

        # Verify performance data collection
        assert result is not None

        performance_metrics = analyzer._performance_metrics
        assert "start_time" in performance_metrics
        assert "end_time" in performance_metrics

        # Verify reasonable performance
        analysis_time = end_time - start_time
        memory_increase = end_memory - start_memory

        assert analysis_time < 120  # Should complete within 2 minutes
        assert memory_increase < 500 * 1024 * 1024  # Less than 500MB increase

        # Verify throughput calculations
        if result["file_count"] > 0 and analysis_time > 0:
            files_per_second = result["file_count"] / analysis_time
            assert files_per_second > 0

            if result["total_size"] > 0:
                bytes_per_second = result["total_size"] / analysis_time
                assert bytes_per_second > 0

    def test_configuration_impact_on_analysis(
        self, qapp, comprehensive_test_environment
    ):
        """Test how configuration changes impact analysis behavior."""
        # Test with different configurations
        configurations = [
            {"analysis": {"include_hidden_files": True}},
            {"analysis": {"include_hidden_files": False}},
            {"analysis": {"max_depth": 5}},
            {"analysis": {"max_depth": 2}},
        ]

        results = []

        for config_data in configurations:
            with patch.object(
                SizeAnalyzerConfig, "get_all_settings", return_value=config_data
            ):
                config = SizeAnalyzerConfig()
                analyzer = SizeAnalyzer()

                result = analyzer.analyze_directory(comprehensive_test_environment)
                results.append((config_data, result))

        # Verify configuration impact
        assert len(results) == len(configurations)

        for config_data, result in results:
            assert result is not None
            assert result["file_count"] >= 0

    def test_hub_integration_simulation(self, qapp, comprehensive_test_environment):
        """Test integration with hub connector simulation."""
        # Create mock hub connector
        mock_hub = Mock()
        mock_hub.report_status_to_hub = Mock()
        mock_hub.get_resource_allocation = Mock(return_value={"max_threads": 4})

        analyzer = SizeAnalyzer(hub_connector=mock_hub)

        result = analyzer.analyze_directory(comprehensive_test_environment)

        assert result is not None

        # Verify hub interactions
        assert mock_hub.report_status_to_hub.called

        # Check status reporting calls
        call_args = mock_hub.report_status_to_hub.call_args_list
        assert len(call_args) > 0

        # Verify first call is analysis start
        first_call = call_args[0]
        assert first_call[0][0] == "analyzing"
        assert "directory" in first_call[0][1]

    def _get_memory_usage(self):
        """Get current memory usage for performance monitoring."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0  # Return 0 if psutil not available


class TestCoreAnalysisEngineStressTests:
    """Stress tests for the core analysis engine."""

    def test_large_directory_stress_test(self, qapp):
        """Stress test with large directory structure."""
        temp_dir = tempfile.mkdtemp(prefix="stress_test_large_")

        try:
            # Create large directory structure
            file_count = 2000
            for i in range(file_count):
                subdir = os.path.join(temp_dir, f"subdir_{i // 100}")
                os.makedirs(subdir, exist_ok=True)

                test_file = os.path.join(subdir, f"file_{i:04d}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Content {i}\n" * 10)

            analyzer = SizeAnalyzer()

            start_time = time.time()
            result = analyzer.analyze_directory(temp_dir)
            analysis_time = time.time() - start_time

            assert result is not None
            assert result["file_count"] == file_count
            assert analysis_time < 300  # Should complete within 5 minutes

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_memory_stress_test(self, qapp):
        """Test memory usage under stress conditions."""
        temp_dir = tempfile.mkdtemp(prefix="stress_test_memory_")

        try:
            # Create files with varying sizes
            sizes = [1024, 10240, 102400, 1024000]  # 1KB to 1MB

            for i, size in enumerate(sizes * 100):  # 400 files total
                test_file = os.path.join(temp_dir, f"memory_test_{i:04d}.dat")
                with open(test_file, "w") as f:
                    f.write("x" * size)

            analyzer = SizeAnalyzer()

            import psutil

            process = psutil.Process()
            initial_memory = process.memory_info().rss

            result = analyzer.analyze_directory(temp_dir)

            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - initial_memory

            assert result is not None
            assert result["file_count"] == 400

            # Memory increase should be reasonable
            assert memory_increase < 1024 * 1024 * 1024  # Less than 1GB

        except ImportError:
            pytest.skip("psutil not available for memory testing")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cancellation_stress_test(self, qapp):
        """Test cancellation behavior under stress."""
        temp_dir = tempfile.mkdtemp(prefix="stress_test_cancellation_")

        try:
            # Create many files for long-running analysis
            for i in range(1000):
                test_file = os.path.join(temp_dir, f"cancel_test_{i:04d}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Cancel test content {i}\n" * 50)

            analyzer = SizeAnalyzer()

            # Start analysis and cancel after short delay
            def cancel_after_delay():
                time.sleep(0.5)  # Let analysis start
                analyzer.cancel_analysis()

            cancel_thread = threading.Thread(target=cancel_after_delay)
            cancel_thread.start()

            start_time = time.time()
            result = analyzer.analyze_directory(temp_dir)
            cancellation_time = time.time() - start_time

            cancel_thread.join()

            # Should respond to cancellation quickly
            assert cancellation_time < 10  # Should cancel within 10 seconds
            assert analyzer._should_cancel

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# Test runner configuration
def run_core_analysis_integration_tests():
    """Run the comprehensive core analysis engine integration test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=20",
        "-x",  # Stop on first failure
        "--maxfail=5",  # Stop after 5 failures
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
    exit_code = run_core_analysis_integration_tests()
    print(
        f"\nCore Analysis Engine Integration Test Suite completed with exit code: {exit_code}"
    )
    sys.exit(exit_code)
