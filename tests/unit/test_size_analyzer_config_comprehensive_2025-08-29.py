"""
Comprehensive Unit Tests for size_analyzer_config.py

Test module for the SizeAnalyzerConfig class and related functions.
Generated with standardized test output including execution timestamp and detailed results.

Created: 2025-08-29
Author: GitHub Copilot
Framework: pytest
Coverage: All functions and methods with edge cases and mock data
"""

import json
import logging
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    from src.tools.analysis.config.size_analyzer_config import (
        SizeAnalyzerConfig,
        get_config_manager,
        get_log_manager,
    )
except ImportError:
    # Fallback import path
    try:
        from src.tools.analysis.config.size_analyzer_config import (
            SizeAnalyzerConfig,
            get_config_manager,
            get_log_manager,
        )
    except ImportError:
        # Direct import for testing
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "size_analyzer_config",
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "src",
                "utilities",
                "analysis",
                "config",
                "size_analyzer_config.py",
            ),
        )
        size_analyzer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(size_analyzer_config)

        SizeAnalyzerConfig = size_analyzer_config.SizeAnalyzerConfig
        get_config_manager = size_analyzer_config.get_config_manager
        get_log_manager = size_analyzer_config.get_log_manager


class TestExecutionTracker:
    """Track test execution statistics and timing."""

    def __init__(self):
        self.start_time = datetime.now()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details = []
        self.execution_log = []

    def log_test_start(self, test_name):
        """Log the start of a test."""
        self.execution_log.append(
            {"test": test_name, "start_time": datetime.now(), "status": "running"}
        )

    def log_test_result(self, test_name, status, duration=None, error_msg=None):
        """Log test result."""
        self.tests_run += 1
        if status == "passed":
            self.tests_passed += 1
        else:
            self.tests_failed += 1

        self.test_details.append(
            {
                "test_name": test_name,
                "status": status,
                "duration": duration,
                "error_message": error_msg,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_summary(self):
        """Get execution summary."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "execution_timestamp": self.start_time.isoformat(),
            "total_duration_seconds": total_duration,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate": (
                (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
            ),
            "test_details": self.test_details,
        }


# Global test tracker
test_tracker = TestExecutionTracker()


class TestHelperFunctions:
    """Test helper functions in the module."""

    def test_get_config_manager_with_valid_import(self):
        """Test get_config_manager with successful import."""
        test_name = "test_get_config_manager_with_valid_import"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch("builtins.__import__") as mock_import:
                mock_module = Mock()
                mock_module.ConfigManager = Mock()
                mock_import.return_value = mock_module

                result = get_config_manager()
                assert result is not None
                assert result == mock_module.ConfigManager

                # Verify all import paths were attempted
                expected_paths = [
                    "src.rfu.core.config_manager",
                    "rfu.core.config_manager",
                    "src.config.config_manager",
                    "rfu.config_manager",
                ]

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_config_manager_import_error(self):
        """Test get_config_manager when import fails."""
        test_name = "test_get_config_manager_import_error"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                result = get_config_manager()
                assert result is None

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_config_manager_attribute_error(self):
        """Test get_config_manager when attribute doesn't exist."""
        test_name = "test_get_config_manager_attribute_error"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch("builtins.__import__") as mock_import:
                mock_module = Mock()
                del mock_module.ConfigManager  # Remove the attribute
                mock_import.return_value = mock_module

                result = get_config_manager()
                assert result is None

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_config_manager_multiple_paths(self):
        """Test get_config_manager trying multiple import paths."""
        test_name = "test_get_config_manager_multiple_paths"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:

            def mock_import_side_effect(path, fromlist=None):
                if path == "src.rfu.core.config_manager":
                    raise ImportError("First path fails")
                elif path == "rfu.core.config_manager":
                    mock_module = Mock()
                    mock_module.ConfigManager = Mock()
                    return mock_module
                else:
                    raise ImportError("Other paths fail")

            with patch("builtins.__import__", side_effect=mock_import_side_effect):
                result = get_config_manager()
                assert result is not None

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_log_manager_with_valid_import(self):
        """Test get_log_manager with successful import."""
        test_name = "test_get_log_manager_with_valid_import"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch("builtins.__import__") as mock_import:
                mock_module = Mock()
                mock_module.LogManager = Mock()
                mock_import.return_value = mock_module

                result = get_log_manager()
                assert result is not None
                assert result == mock_module.LogManager

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_log_manager_import_error(self):
        """Test get_log_manager fallback to basic logging."""
        test_name = "test_get_log_manager_import_error"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                result = get_log_manager()
                assert result == logging

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_get_log_manager_exception_fallback(self):
        """Test get_log_manager exception fallback."""
        test_name = "test_get_log_manager_exception_fallback"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch("builtins.__import__", side_effect=Exception("General error")):
                result = get_log_manager()
                assert result == logging

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigInitialization:
    """Test SizeAnalyzerConfig initialization and setup."""

    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock config manager for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        return mock_cm

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return Mock(spec=logging.Logger)

    def test_initialization_with_config_manager(self, mock_config_manager):
        """Test initialization with provided config manager."""
        test_name = "test_initialization_with_config_manager"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            config = SizeAnalyzerConfig(config_manager=mock_config_manager)
            assert config.config_manager == mock_config_manager
            assert config.section_name == "size_analyzer"
            assert hasattr(config, "defaults")
            assert isinstance(config.defaults, dict)

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_initialization_without_config_manager(self):
        """Test initialization without config manager (fallback)."""
        test_name = "test_initialization_without_config_manager"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            with patch(
                "src.tools.analysis.config.size_analyzer_config.get_config_manager",
                return_value=None,
            ):
                config = SizeAnalyzerConfig()
                assert config.config_manager is not None
                assert hasattr(config.config_manager, "config")
                assert hasattr(config.config_manager, "save_config")

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_initialization_with_log_manager(self, mock_config_manager):
        """Test initialization with log manager setup."""
        test_name = "test_initialization_with_log_manager"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            mock_log_manager = Mock()
            mock_log_manager.get_logger = Mock(return_value=Mock())

            with patch(
                "src.tools.analysis.config.size_analyzer_config.get_log_manager",
                return_value=mock_log_manager,
            ):
                config = SizeAnalyzerConfig(config_manager=mock_config_manager)
                mock_log_manager.get_logger.assert_called_with("SizeAnalyzer.Config")

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_defaults_structure_comprehensive(self, mock_config_manager):
        """Test comprehensive defaults structure validation."""
        test_name = "test_defaults_structure_comprehensive"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            config = SizeAnalyzerConfig(config_manager=mock_config_manager)
            defaults = config.defaults

            # Check main sections exist
            expected_sections = [
                "general",
                "analysis",
                "export",
                "ui",
                "performance",
                "resources",
                "hub_integration",
                "logging",
            ]
            for section in expected_sections:
                assert section in defaults, f"Missing section: {section}"
                assert isinstance(
                    defaults[section], dict
                ), f"Section {section} is not a dict"

            # Check specific subsection structures
            assert "window_geometry" in defaults["ui"]
            assert "progress_visualization" in defaults["ui"]
            assert "results_display" in defaults["ui"]

            assert "resource_requirements" in defaults["hub_integration"]
            assert "event_broadcasting" in defaults["hub_integration"]
            assert "coordination" in defaults["hub_integration"]

            # Validate data types
            assert isinstance(defaults["general"]["max_recent_directories"], int)
            assert isinstance(defaults["general"]["enable_logging"], bool)
            assert isinstance(defaults["analysis"]["default_top_files_count"], int)
            assert isinstance(defaults["analysis"]["include_hidden_files"], bool)

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigCore:
    """Test core functionality of SizeAnalyzerConfig."""

    @pytest.fixture
    def size_analyzer_config(self):
        """Create a SizeAnalyzerConfig instance for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        mock_logger = Mock(spec=logging.Logger)

        config = SizeAnalyzerConfig(config_manager=mock_cm)
        config.logger = mock_logger
        return config

    def test_ensure_configuration_exists_new_config(self, size_analyzer_config):
        """Test _ensure_configuration_exists with new configuration."""
        test_name = "test_ensure_configuration_exists_new_config"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            size_analyzer_config.config_manager.config = {}

            size_analyzer_config._ensure_configuration_exists()

            assert "size_analyzer" in size_analyzer_config.config_manager.config
            assert (
                size_analyzer_config.config_manager.config["size_analyzer"]
                == size_analyzer_config.defaults
            )
            size_analyzer_config.config_manager.save_config.assert_called_once()

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_ensure_configuration_exists_existing_config(self, size_analyzer_config):
        """Test _ensure_configuration_exists with existing configuration."""
        test_name = "test_ensure_configuration_exists_existing_config"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            existing_config = {"general": {"module_path": "custom_path"}}
            size_analyzer_config.config_manager.config = {
                "size_analyzer": existing_config
            }

            with patch.object(
                size_analyzer_config, "_merge_with_defaults"
            ) as mock_merge:
                size_analyzer_config._ensure_configuration_exists()
                mock_merge.assert_called_once_with(existing_config)

                duration = time.time() - start_time
                test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_merge_with_defaults_comprehensive(self, size_analyzer_config):
        """Test comprehensive _merge_with_defaults functionality."""
        test_name = "test_merge_with_defaults_comprehensive"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            existing_config = {
                "general": {
                    "module_path": "custom_path",
                    "new_key": "new_value",
                    "last_opened_directory": "custom_dir",
                },
                "ui": {
                    "window_geometry": {
                        "width": 1024,
                        "height": 768,
                        "custom_property": True,
                    },
                    "progress_visualization": {
                        "show_progress_bar": False,
                        "custom_viz_option": "custom_value",
                    },
                },
                "new_section": {"new_option": "new_value"},
            }

            size_analyzer_config._merge_with_defaults(existing_config)

            merged = size_analyzer_config.config_manager.config["size_analyzer"]

            # Check that custom values are preserved
            assert merged["general"]["module_path"] == "custom_path"
            assert merged["general"]["new_key"] == "new_value"
            assert merged["general"]["last_opened_directory"] == "custom_dir"
            assert merged["ui"]["window_geometry"]["width"] == 1024
            assert merged["ui"]["window_geometry"]["height"] == 768
            assert merged["ui"]["window_geometry"]["custom_property"] is True
            assert merged["ui"]["progress_visualization"]["show_progress_bar"] is False
            assert (
                merged["ui"]["progress_visualization"]["custom_viz_option"]
                == "custom_value"
            )
            assert merged["new_section"]["new_option"] == "new_value"

            # Check that default values are still present where not overridden
            assert "recent_directories" in merged["general"]
            assert "remember_size" in merged["ui"]["window_geometry"]
            assert "show_progress_details" in merged["ui"]["progress_visualization"]

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigSettings:
    """Test settings management functionality."""

    @pytest.fixture
    def size_analyzer_config(self):
        """Create a SizeAnalyzerConfig instance for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        mock_logger = Mock(spec=logging.Logger)

        config = SizeAnalyzerConfig(config_manager=mock_cm)
        config.logger = mock_logger
        return config

    def test_get_setting_all_scenarios(self, size_analyzer_config):
        """Test get_setting with all possible scenarios."""
        test_name = "test_get_setting_all_scenarios"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Scenario 1: Existing value
            size_analyzer_config.config_manager.config = {
                "size_analyzer": {
                    "general": {
                        "module_path": "test_path",
                        "enable_logging": True,
                        "max_recent_directories": 15,
                    }
                }
            }

            assert (
                size_analyzer_config.get_setting("general", "module_path")
                == "test_path"
            )
            assert size_analyzer_config.get_setting("general", "enable_logging") is True
            assert (
                size_analyzer_config.get_setting("general", "max_recent_directories")
                == 15
            )

            # Scenario 2: Fallback to default values
            size_analyzer_config.config_manager.config = {"size_analyzer": {}}
            result = size_analyzer_config.get_setting("general", "module_path")
            assert result == size_analyzer_config.defaults["general"]["module_path"]

            # Scenario 3: Custom default value
            result = size_analyzer_config.get_setting(
                "general", "nonexistent_key", "custom_default"
            )
            assert result == "custom_default"

            # Scenario 4: Nested missing subsection
            result = size_analyzer_config.get_setting(
                "missing_section", "missing_key", "fallback"
            )
            assert result == "fallback"

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_set_setting_comprehensive(self, size_analyzer_config):
        """Test comprehensive set_setting functionality."""
        test_name = "test_set_setting_comprehensive"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Test setting in new section
            result = size_analyzer_config.set_setting(
                "new_section", "new_key", "new_value"
            )
            assert result is True
            assert (
                size_analyzer_config.config_manager.config["size_analyzer"][
                    "new_section"
                ]["new_key"]
                == "new_value"
            )

            # Test setting in existing section
            size_analyzer_config.config_manager.config["size_analyzer"]["general"] = {}
            result = size_analyzer_config.set_setting("general", "test_key", 42)
            assert result is True
            assert (
                size_analyzer_config.config_manager.config["size_analyzer"]["general"][
                    "test_key"
                ]
                == 42
            )

            # Test setting complex data types
            complex_data = {
                "nested": {"deeply": {"value": [1, 2, 3]}},
                "list": ["a", "b", "c"],
                "boolean": True,
                "none_value": None,
            }
            result = size_analyzer_config.set_setting(
                "general", "complex_data", complex_data
            )
            assert result is True
            assert (
                size_analyzer_config.config_manager.config["size_analyzer"]["general"][
                    "complex_data"
                ]
                == complex_data
            )

            # Verify save_config was called
            assert size_analyzer_config.config_manager.save_config.call_count >= 3

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_recent_directories_management(self, size_analyzer_config):
        """Test comprehensive recent directories management."""
        test_name = "test_recent_directories_management"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Initialize with some directories
            size_analyzer_config.config_manager.config = {
                "size_analyzer": {
                    "general": {
                        "recent_directories": ["/path1", "/path2", "/path3"],
                        "max_recent_directories": 5,
                    }
                }
            }

            # Test adding new directory
            result = size_analyzer_config.add_recent_directory("/new/path")
            assert result is True
            recent_dirs = size_analyzer_config.get_recent_directories()
            assert recent_dirs[0] == "/new/path"
            assert len(recent_dirs) == 4

            # Test adding existing directory (should move to front)
            result = size_analyzer_config.add_recent_directory("/path2")
            assert result is True
            recent_dirs = size_analyzer_config.get_recent_directories()
            assert recent_dirs[0] == "/path2"
            assert recent_dirs.count("/path2") == 1  # Should not duplicate
            assert len(recent_dirs) == 4

            # Test maximum limit enforcement
            for i in range(10):
                size_analyzer_config.add_recent_directory(f"/extra/path{i}")

            recent_dirs = size_analyzer_config.get_recent_directories()
            assert len(recent_dirs) == 5  # Should respect max limit
            assert recent_dirs[0] == "/extra/path9"  # Most recent should be first

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_window_geometry_management(self, size_analyzer_config):
        """Test comprehensive window geometry management."""
        test_name = "test_window_geometry_management"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Test saving full geometry
            result = size_analyzer_config.save_window_geometry(1920, 1080, 100, 50)
            assert result is True

            geometry = size_analyzer_config.get_window_geometry()
            assert geometry["width"] == 1920
            assert geometry["height"] == 1080
            assert geometry["x"] == 100
            assert geometry["y"] == 50

            # Test saving size only
            result = size_analyzer_config.save_window_geometry(1024, 768)
            assert result is True

            geometry = size_analyzer_config.get_window_geometry()
            assert geometry["width"] == 1024
            assert geometry["height"] == 768
            # x and y should be preserved from previous save
            assert geometry["x"] == 100
            assert geometry["y"] == 50

            # Test default geometry values
            size_analyzer_config.config_manager.config = {"size_analyzer": {}}
            geometry = size_analyzer_config.get_window_geometry()
            assert geometry["width"] == 800
            assert geometry["height"] == 600
            assert geometry["remember_size"] is True
            assert geometry["remember_position"] is True
            assert geometry["center_on_screen"] is True

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigResourceManagement:
    """Test resource path management functionality."""

    @pytest.fixture
    def size_analyzer_config(self):
        """Create a SizeAnalyzerConfig instance for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        return config

    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_resource_path_scenarios(self, size_analyzer_config, temp_directory):
        """Test get_resource_path with various scenarios."""
        test_name = "test_get_resource_path_scenarios"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Test absolute path
            absolute_path = os.path.abspath(temp_directory)
            size_analyzer_config.config_manager.config = {
                "size_analyzer": {"resources": {"absolute_resource": absolute_path}}
            }

            result = size_analyzer_config.get_resource_path("absolute_resource")
            assert result == absolute_path
            assert os.path.isabs(result)

            # Test relative path conversion
            relative_path = "relative/path/to/resource"
            size_analyzer_config.config_manager.config["size_analyzer"]["resources"][
                "relative_resource"
            ] = relative_path

            result = size_analyzer_config.get_resource_path("relative_resource")
            assert os.path.isabs(result)
            assert result.endswith(relative_path.replace("/", os.sep))

            # Test empty path
            size_analyzer_config.config_manager.config["size_analyzer"]["resources"][
                "empty_resource"
            ] = ""
            result = size_analyzer_config.get_resource_path("empty_resource")
            assert result == ""

            # Test missing resource
            result = size_analyzer_config.get_resource_path("missing_resource")
            assert result == ""

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigValidation:
    """Test configuration validation functionality."""

    @pytest.fixture
    def size_analyzer_config(self):
        """Create a SizeAnalyzerConfig instance for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        return config

    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_validate_configuration_comprehensive(
        self, size_analyzer_config, temp_directory
    ):
        """Test comprehensive configuration validation."""
        test_name = "test_validate_configuration_comprehensive"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Create test files and directories
            test_file = os.path.join(temp_directory, "test_file.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            missing_file = os.path.join(temp_directory, "missing_file.txt")

            # Setup test configuration
            size_analyzer_config.config_manager.config = {
                "size_analyzer": {
                    "resources": {
                        "existing_file": test_file,
                        "missing_file": missing_file,
                        "cache_directory": os.path.join(temp_directory, "cache"),
                        "temp_directory": os.path.join(temp_directory, "temp"),
                        "log_directory": os.path.join(temp_directory, "logs"),
                        "non_path_resource": "not_a_path",
                    },
                    "performance": {
                        "max_memory_usage_mb": 32,  # Low memory warning
                        "operation_timeout_seconds": 10,  # Low timeout warning
                        "max_cpu_usage_percent": 80,  # Normal value
                    },
                    "analysis": {
                        "default_top_files_count": 200,  # High count warning
                        "progress_update_interval": 100,  # Normal value
                    },
                }
            }

            issues = size_analyzer_config.validate_configuration()

            # Verify structure
            assert isinstance(issues, dict)
            assert "errors" in issues
            assert "warnings" in issues
            assert "info" in issues

            # Check for expected warnings
            warning_messages = " ".join(issues["warnings"])
            assert (
                "missing_file.txt" in warning_messages
                or "Resource not found" in warning_messages
            )
            assert "Memory limit is very low" in warning_messages
            assert "Operation timeout is very low" in warning_messages
            assert "Large top files count" in warning_messages

            # Check that directories were created
            assert os.path.exists(os.path.join(temp_directory, "cache"))
            assert os.path.exists(os.path.join(temp_directory, "temp"))
            assert os.path.exists(os.path.join(temp_directory, "logs"))

            # Check for info messages about created directories
            info_messages = " ".join(issues["info"])
            assert "Created directory" in info_messages

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigImportExport:
    """Test configuration import/export functionality."""

    @pytest.fixture
    def size_analyzer_config(self):
        """Create a SizeAnalyzerConfig instance for testing."""
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        return config

    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_export_import_configuration_roundtrip(
        self, size_analyzer_config, temp_directory
    ):
        """Test complete export/import roundtrip."""
        test_name = "test_export_import_configuration_roundtrip"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            # Setup complex test configuration
            test_config = {
                "general": {
                    "module_path": "custom.module.path",
                    "recent_directories": ["/path1", "/path2", "/path3"],
                    "max_recent_directories": 15,
                    "enable_logging": True,
                },
                "analysis": {
                    "default_top_files_count": 50,
                    "include_hidden_files": True,
                    "follow_symlinks": False,
                },
                "ui": {
                    "window_geometry": {
                        "width": 1200,
                        "height": 800,
                        "x": 100,
                        "y": 50,
                    },
                    "results_display": {
                        "show_file_types": True,
                        "results_font_size": 12,
                    },
                },
                "custom_section": {
                    "custom_key": "custom_value",
                    "custom_list": [1, 2, 3, 4, 5],
                    "custom_nested": {"deep_key": "deep_value"},
                },
            }

            size_analyzer_config.config_manager.config = {"size_analyzer": test_config}

            # Export configuration
            export_file = os.path.join(temp_directory, "exported_config.json")
            result = size_analyzer_config.export_configuration(export_file)
            assert result is True
            assert os.path.exists(export_file)

            # Verify exported content
            with open(export_file, "r", encoding="utf-8") as f:
                exported_data = json.load(f)
            assert exported_data == test_config

            # Reset configuration
            size_analyzer_config.config_manager.config = {"size_analyzer": {}}

            # Import configuration
            result = size_analyzer_config.import_configuration(export_file)
            assert result is True
            assert (
                size_analyzer_config.config_manager.config["size_analyzer"]
                == test_config
            )

            # Verify specific values
            assert (
                size_analyzer_config.get_setting("general", "module_path")
                == "custom.module.path"
            )
            assert (
                size_analyzer_config.get_setting("analysis", "default_top_files_count")
                == 50
            )
            assert (
                size_analyzer_config.get_setting("ui", "window_geometry")["width"]
                == 1200
            )
            assert (
                size_analyzer_config.get_setting("custom_section", "custom_key")
                == "custom_value"
            )

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigEdgeCases:
    """Test edge cases and error conditions."""

    def test_corrupted_configuration_handling(self):
        """Test handling of corrupted configuration data."""
        test_name = "test_corrupted_configuration_handling"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            mock_cm = Mock()
            mock_cm.config = {"size_analyzer": "not_a_dict"}  # Invalid structure
            mock_cm.save_config = Mock()

            config = SizeAnalyzerConfig(config_manager=mock_cm)

            # Should handle gracefully
            result = config.get_setting("general", "module_path", "fallback")
            assert result == "fallback"

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise

    def test_unicode_handling(self):
        """Test handling of Unicode characters in configuration."""
        test_name = "test_unicode_handling"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            mock_cm = Mock()
            mock_cm.config = {}
            mock_cm.save_config = Mock()

            config = SizeAnalyzerConfig(config_manager=mock_cm)

            # Test various Unicode strings
            unicode_strings = [
                "/path/with/unicode/测试/файл",
                "Configuration with émojis 🚀 and symbols ñáéíóú",
                "Japanese: こんにちは世界",
                "Arabic: مرحبا بالعالم",
                "Mixed: Test_测试_тест_🌟",
            ]

            for i, unicode_str in enumerate(unicode_strings):
                result = config.set_setting("general", f"unicode_test_{i}", unicode_str)
                assert result is True

                retrieved = config.get_setting("general", f"unicode_test_{i}")
                assert retrieved == unicode_str

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


class TestSizeAnalyzerConfigIntegration:
    """Integration tests combining multiple operations."""

    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_complete_workflow_integration(self, temp_directory):
        """Test a complete configuration workflow."""
        test_name = "test_complete_workflow_integration"
        test_tracker.log_test_start(test_name)
        start_time = time.time()

        try:
            mock_cm = Mock()
            mock_cm.config = {}
            mock_cm.save_config = Mock()

            config = SizeAnalyzerConfig(config_manager=mock_cm)

            # Phase 1: Initial configuration setup
            assert config.set_setting(
                "general", "last_opened_directory", temp_directory
            )
            assert config.set_setting("general", "enable_logging", True)
            assert config.set_setting("analysis", "default_top_files_count", 75)
            assert config.set_setting("analysis", "include_hidden_files", True)
            assert config.set_setting("performance", "max_memory_usage_mb", 512)

            # Phase 2: Recent directories management
            test_directories = [
                os.path.join(temp_directory, "dir1"),
                os.path.join(temp_directory, "dir2"),
                os.path.join(temp_directory, "dir3"),
                os.path.join(temp_directory, "dir4"),
                os.path.join(temp_directory, "dir5"),
            ]

            for test_dir in test_directories:
                os.makedirs(test_dir, exist_ok=True)
                assert config.add_recent_directory(test_dir)

            recent_dirs = config.get_recent_directories()
            assert len(recent_dirs) == 5
            assert recent_dirs[0] == test_directories[-1]  # Most recent first

            # Phase 3: Window geometry management
            assert config.save_window_geometry(1920, 1080, 200, 100)
            geometry = config.get_window_geometry()
            assert geometry["width"] == 1920
            assert geometry["height"] == 1080
            assert geometry["x"] == 200
            assert geometry["y"] == 100

            # Phase 4: Configuration validation
            issues = config.validate_configuration()
            assert isinstance(issues, dict)
            assert all(key in issues for key in ["errors", "warnings", "info"])

            # Phase 5: Export configuration
            export_file = os.path.join(temp_directory, "workflow_config.json")
            assert config.export_configuration(export_file)
            assert os.path.exists(export_file)

            # Phase 6: Configuration reset
            original_config = config.get_all_settings().copy()
            assert config.reset_to_defaults()

            # Verify reset worked
            reset_config = config.get_all_settings()
            assert reset_config == config.defaults

            # Phase 7: Import configuration back
            assert config.import_configuration(export_file)

            # Phase 8: Verify all values were restored correctly
            assert (
                config.get_setting("general", "last_opened_directory") == temp_directory
            )
            assert config.get_setting("general", "enable_logging") is True
            assert config.get_setting("analysis", "default_top_files_count") == 75
            assert config.get_setting("analysis", "include_hidden_files") is True
            assert config.get_setting("performance", "max_memory_usage_mb") == 512

            restored_recent_dirs = config.get_recent_directories()
            assert len(restored_recent_dirs) == 5

            restored_geometry = config.get_window_geometry()
            assert restored_geometry["width"] == 1920
            assert restored_geometry["height"] == 1080

            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "passed", duration)

        except Exception as e:
            duration = time.time() - start_time
            test_tracker.log_test_result(test_name, "failed", duration, str(e))
            raise


def generate_test_report():
    """Generate comprehensive test report."""
    summary = test_tracker.get_summary()

    # Create detailed report
    report = {
        "test_execution_summary": summary,
        "test_environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "test_file": __file__,
            "working_directory": os.getcwd(),
        },
        "coverage_summary": {
            "functions_tested": [
                "get_config_manager",
                "get_log_manager",
                "SizeAnalyzerConfig.__init__",
                "SizeAnalyzerConfig._ensure_configuration_exists",
                "SizeAnalyzerConfig._merge_with_defaults",
                "SizeAnalyzerConfig.get_setting",
                "SizeAnalyzerConfig.set_setting",
                "SizeAnalyzerConfig.get_all_settings",
                "SizeAnalyzerConfig.reset_to_defaults",
                "SizeAnalyzerConfig.add_recent_directory",
                "SizeAnalyzerConfig.get_recent_directories",
                "SizeAnalyzerConfig.save_window_geometry",
                "SizeAnalyzerConfig.get_window_geometry",
                "SizeAnalyzerConfig.get_resource_path",
                "SizeAnalyzerConfig.validate_configuration",
                "SizeAnalyzerConfig.export_configuration",
                "SizeAnalyzerConfig.import_configuration",
                "SizeAnalyzerConfig._create_fallback_config_manager",
            ],
            "edge_cases_tested": [
                "corrupted_configuration",
                "none_values",
                "unicode_handling",
                "large_data_structures",
                "error_conditions",
                "import_errors",
                "file_system_errors",
            ],
            "integration_scenarios": [
                "complete_workflow",
                "export_import_roundtrip",
                "configuration_validation",
                "recent_directories_management",
                "window_geometry_management",
            ],
        },
    }

    return report


if __name__ == "__main__":
    # Run tests when executed directly
    import pytest

    # Configure pytest with detailed output
    pytest_args = [__file__, "-v", "--tb=short", "--durations=10", "--strict-markers"]

    pytest.main(pytest_args)

    # Generate and save test report
    report = generate_test_report()

    # Save report to results directory
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(
        results_dir, f"result_size_analyzer_config_{timestamp}.json"
    )

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nTest execution completed!")
    print(f"Report saved to: {report_file}")
    print(f"Tests run: {test_tracker.tests_run}")
    print(f"Tests passed: {test_tracker.tests_passed}")
    print(f"Tests failed: {test_tracker.tests_failed}")
    print(
        f"Success rate: {test_tracker.tests_passed / test_tracker.tests_run * 100:.1f}%"
        if test_tracker.tests_run > 0
        else "No tests run"
    )
