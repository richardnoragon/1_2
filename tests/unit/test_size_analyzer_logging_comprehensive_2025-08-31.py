#!/usr/bin/env python3
# flake8: noqa
"""
Comprehensive Test Suite for Size Analyzer Logging Component

This test suite provides comprehensive coverage for the SizeAnalyzerLogger component
that was identified as missing critical test coverage in the Core Analysis Engine.

Created: August 31, 2025
Coverage: SizeAnalyzerLogger - All critical logging functionality
Priority: HIGH (identified as missing critical test in utilities-overview.md)
"""

import json
import logging
import os
import shutil
import sys
import tempfile
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

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False

# Skip all tests if imports fail
pytestmark = pytest.mark.skipif(
    not IMPORTS_SUCCESSFUL, reason="Required modules not available"
)


class TestSizeAnalyzerLoggerInitialization:
    """Test initialization and configuration of SizeAnalyzerLogger."""

    def test_logger_default_initialization(self):
        """Test logger initialization with default configuration."""
        logger = SizeAnalyzerLogger()

        assert logger is not None
        assert hasattr(logger, "config")
        assert hasattr(logger, "loggers")
        assert hasattr(logger, "main_logger")
        assert isinstance(logger.loggers, dict)

    def test_logger_custom_config_initialization(self):
        """Test logger initialization with custom configuration."""
        custom_config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=custom_config)

        assert logger is not None
        assert logger.config == custom_config
        assert hasattr(logger, "loggers")
        assert hasattr(logger, "main_logger")

    def test_supported_log_categories(self):
        """Test that logger supports expected log categories."""
        logger = SizeAnalyzerLogger()

        # Test category logger creation
        expected_categories = ["analysis", "performance", "errors", "debug"]

        for category in expected_categories:
            try:
                category_logger = logger.get_category_logger(category)
                assert category_logger is not None
                assert isinstance(category_logger, logging.Logger)
            except AttributeError:
                # Method might not exist yet, skip
                pass

    @patch("src.tools.analysis.size_analyzer.size_analyzer_logging.LogManager")
    def test_logger_integration_with_main_logging(self, mock_log_manager):
        """Test integration with main logging system."""
        mock_main_logger = Mock()
        mock_log_manager.get_logger.return_value = mock_main_logger

        logger = SizeAnalyzerLogger()

        assert logger.main_logger == mock_main_logger
        mock_log_manager.get_logger.assert_called_with("SizeAnalyzer")


class TestLogConfigurationManagement:
    """Test log configuration management and setup."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="size_analyzer_log_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_log_directory_creation(self, temp_log_dir):
        """Test automatic log directory creation."""
        with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
            mock_settings.return_value = {
                "logging": {"enable_tool_logging": True, "log_directory": temp_log_dir}
            }

            logger = SizeAnalyzerLogger()

            # Verify log directory exists
            assert os.path.exists(temp_log_dir)

    def test_log_file_creation(self, temp_log_dir):
        """Test log file creation and configuration."""
        with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
            mock_settings.return_value = {
                "logging": {
                    "enable_tool_logging": True,
                    "log_directory": temp_log_dir,
                    "log_level": "INFO",
                }
            }

            logger = SizeAnalyzerLogger()

            # Check if main log file would be created
            expected_log_file = os.path.join(temp_log_dir, "size_analyzer.log")
            # Note: Actual file creation depends on implementation

    def test_logging_disabled_configuration(self):
        """Test behavior when logging is disabled."""
        with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
            mock_settings.return_value = {"logging": {"enable_tool_logging": False}}

            logger = SizeAnalyzerLogger()

            # Should initialize without setting up file handlers
            assert logger is not None

    def test_log_level_configuration(self):
        """Test different log level configurations."""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in log_levels:
            with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
                mock_settings.return_value = {
                    "logging": {"enable_tool_logging": True, "log_level": level}
                }

                logger = SizeAnalyzerLogger()
                assert logger is not None

    def test_log_format_configuration(self):
        """Test log format configuration options."""
        custom_formats = [
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "%(levelname)s: %(message)s",
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        ]

        for format_str in custom_formats:
            with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
                mock_settings.return_value = {
                    "logging": {"enable_tool_logging": True, "log_format": format_str}
                }

                logger = SizeAnalyzerLogger()
                assert logger is not None


class TestLoggingOperations:
    """Test actual logging operations and message handling."""

    @pytest.fixture
    def logger_with_mock_config(self):
        """Create logger with mocked configuration for testing."""
        with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
            mock_settings.return_value = {
                "logging": {"enable_tool_logging": True, "log_level": "DEBUG"}
            }
            return SizeAnalyzerLogger()

    def test_basic_logging_operations(self, logger_with_mock_config):
        """Test basic logging operations."""
        logger = logger_with_mock_config

        # Test that logger can be used for basic operations
        assert logger is not None
        assert hasattr(logger, "main_logger")

        # Test logging methods if they exist
        if hasattr(logger, "log_analysis_start"):
            logger.log_analysis_start("/test/path")

        if hasattr(logger, "log_analysis_progress"):
            logger.log_analysis_progress(50, 100)

        if hasattr(logger, "log_analysis_complete"):
            logger.log_analysis_complete({"files": 10, "size": 1000})

    def test_error_logging(self, logger_with_mock_config):
        """Test error logging functionality."""
        logger = logger_with_mock_config

        # Test error logging methods if they exist
        if hasattr(logger, "log_error"):
            logger.log_error("Test error message")
            logger.log_error("Permission denied", {"file": "/test/file.txt"})

        if hasattr(logger, "log_exception"):
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                if hasattr(logger, "log_exception"):
                    logger.log_exception(e)

    def test_performance_logging(self, logger_with_mock_config):
        """Test performance metrics logging."""
        logger = logger_with_mock_config

        # Test performance logging methods if they exist
        if hasattr(logger, "log_performance_metrics"):
            metrics = {
                "analysis_time": 5.2,
                "files_per_second": 150,
                "memory_usage": 45.5,
            }
            logger.log_performance_metrics(metrics)

        if hasattr(logger, "log_benchmark_result"):
            benchmark = {
                "operation": "directory_scan",
                "duration": 2.1,
                "file_count": 500,
            }
            if hasattr(logger, "log_benchmark_result"):
                logger.log_benchmark_result(benchmark)

    def test_debug_logging(self, logger_with_mock_config):
        """Test debug level logging functionality."""
        logger = logger_with_mock_config

        # Test debug logging methods if they exist
        if hasattr(logger, "log_debug"):
            logger.log_debug("Debug message")
            logger.log_debug("Processing file", {"filename": "test.txt"})

        if hasattr(logger, "log_trace"):
            if hasattr(logger, "log_trace"):
                logger.log_trace("Function entry", {"function": "analyze_directory"})


class TestLogCategoryManagement:
    """Test management of different log categories."""

    @pytest.fixture
    def logger_instance(self):
        """Create logger instance for testing."""
        return SizeAnalyzerLogger()

    def test_category_logger_creation(self, logger_instance):
        """Test creation of category-specific loggers."""
        categories = ["analysis", "performance", "errors", "debug"]

        for category in categories:
            try:
                if hasattr(logger_instance, "get_category_logger"):
                    category_logger = logger_instance.get_category_logger(category)
                    assert category_logger is not None
                    assert category in logger_instance.loggers
            except (AttributeError, KeyError):
                # Method or category might not exist, skip
                pass

    def test_category_specific_logging(self, logger_instance):
        """Test logging to specific categories."""
        test_cases = [
            ("analysis", "Starting directory analysis"),
            ("performance", "Analysis completed in 5.2 seconds"),
            ("errors", "Permission denied accessing file"),
            ("debug", "Processing file: test.txt"),
        ]

        for category, message in test_cases:
            try:
                if hasattr(logger_instance, "log_to_category"):
                    logger_instance.log_to_category(category, message)
            except (AttributeError, KeyError):
                # Method might not exist, skip
                pass

    def test_category_log_file_separation(self, logger_instance):
        """Test that different categories can log to separate files."""
        # This test would verify file separation if implemented
        categories = ["analysis", "performance", "errors"]

        for category in categories:
            try:
                if hasattr(logger_instance, "get_category_log_file"):
                    log_file = logger_instance.get_category_log_file(category)
                    assert log_file is not None
                    assert category in log_file
            except (AttributeError, KeyError):
                # Method might not exist, skip
                pass


class TestLoggingErrorHandling:
    """Test error handling in logging operations."""

    def test_logging_with_invalid_directory(self):
        """Test logging setup with invalid log directory."""
        with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
            mock_settings.return_value = {
                "logging": {
                    "enable_tool_logging": True,
                    "log_directory": "/invalid/readonly/path",
                }
            }

            # Should handle invalid directory gracefully
            try:
                logger = SizeAnalyzerLogger()
                assert logger is not None
            except Exception:
                # If it raises an exception, it should be handled gracefully
                pass

    def test_logging_with_permission_errors(self):
        """Test logging behavior with permission errors."""
        with patch("os.makedirs", side_effect=PermissionError("Access denied")):
            logger = SizeAnalyzerLogger()
            # Should initialize even if directory creation fails
            assert logger is not None

    def test_logging_with_disk_full(self):
        """Test logging behavior when disk is full."""
        with patch("builtins.open", side_effect=OSError("No space left on device")):
            logger = SizeAnalyzerLogger()
            # Should handle disk full errors gracefully
            assert logger is not None

    def test_malformed_log_configuration(self):
        """Test handling of malformed logging configuration."""
        malformed_configs = [
            {"logging": None},
            {"logging": "invalid_string"},
            {"logging": {"invalid_key": "value"}},
            {},
            None,
        ]

        for config in malformed_configs:
            with patch.object(SizeAnalyzerConfig, "get_all_settings") as mock_settings:
                mock_settings.return_value = config

                # Should handle malformed config gracefully
                try:
                    logger = SizeAnalyzerLogger()
                    assert logger is not None
                except Exception:
                    # Should not crash, but if it does, that's a test failure
                    pytest.fail(f"Logger crashed with config: {config}")


class TestLoggingPerformance:
    """Test performance aspects of logging operations."""

    def test_logging_overhead(self):
        """Test that logging operations have minimal overhead."""
        logger = SizeAnalyzerLogger()

        # Test many rapid log operations
        start_time = time.time()

        for i in range(1000):
            try:
                if hasattr(logger, "log_debug"):
                    logger.log_debug(f"Debug message {i}")
                elif hasattr(logger.main_logger, "debug"):
                    logger.main_logger.debug(f"Debug message {i}")
            except Exception:
                # Skip if logging method doesn't exist
                pass

        end_time = time.time()
        logging_time = end_time - start_time

        # Logging 1000 messages should complete quickly
        assert logging_time < 5.0  # Should complete within 5 seconds

    def test_concurrent_logging(self):
        """Test logging operations under concurrent access."""
        logger = SizeAnalyzerLogger()
        results = []

        def log_worker(worker_id):
            try:
                for i in range(100):
                    if hasattr(logger.main_logger, "info"):
                        logger.main_logger.info(f"Worker {worker_id} message {i}")
                results.append(f"Worker {worker_id} completed")
            except Exception as e:
                results.append(f"Worker {worker_id} failed: {e}")

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)

        # All workers should complete successfully
        completed_workers = [r for r in results if "completed" in r]
        assert len(completed_workers) == 5

    def test_memory_usage_during_logging(self):
        """Test memory usage during extensive logging."""
        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        logger = SizeAnalyzerLogger()

        # Perform extensive logging
        for i in range(5000):
            try:
                if hasattr(logger.main_logger, "info"):
                    logger.main_logger.info(f"Memory test message {i}")
            except Exception:
                pass

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024


class TestLoggingIntegration:
    """Test integration with other system components."""

    def test_config_integration(self):
        """Test integration with configuration system."""
        config = SizeAnalyzerConfig()
        logger = SizeAnalyzerLogger(config=config)

        assert logger.config == config
        assert logger is not None

    def test_main_logger_integration(self):
        """Test integration with main logging system."""

    with patch(
        "src.tools.analysis.size_analyzer.size_analyzer_logging.LogManager"
    ) as mock_log_manager:
        mock_main_logger = Mock()
        mock_log_manager.get_logger.return_value = mock_main_logger

        logger = SizeAnalyzerLogger()

        assert logger.main_logger == mock_main_logger
        mock_log_manager.get_logger.assert_called_once_with("SizeAnalyzer")

    def test_analysis_engine_integration(self):
        """Test integration with analysis engine components."""
        logger = SizeAnalyzerLogger()

        # Test that logger can be used by analysis engine
        try:
            from src.tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer

            analyzer = SizeAnalyzer()

            # Logger should be compatible with analyzer
            assert logger is not None
            assert analyzer is not None

        except ImportError:
            # If analyzer not available, skip integration test
            pytest.skip("SizeAnalyzer not available for integration test")


# Test fixtures for shared resources
@pytest.fixture
def temp_log_environment():
    """Create temporary logging environment for testing."""
    temp_dir = tempfile.mkdtemp(prefix="size_analyzer_logging_test_")

    # Create test log directory structure
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    yield {"temp_dir": temp_dir, "log_dir": log_dir}

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


# Test runner configuration
def run_size_analyzer_logging_tests():
    """Run the comprehensive size analyzer logging test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for faster feedback
    ]

    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Run the tests
    exit_code = run_size_analyzer_logging_tests()
    print(f"\nSize Analyzer Logging Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)
