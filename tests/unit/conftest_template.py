"""
Standardized Test Configuration Template
Purpose: Provide consistent pytest configuration addressing import system issues

This template resolves the critical issues identified in unit test review:
- Standardized Python path configuration
- Proper module installation for test dependencies
- Consistent test environment setup scripts
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import standardized environment configuration
from test_env_config import setup_test_environment, get_module_import_path

# Setup test environment
TEST_CONFIG = setup_test_environment()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment_fixture():
    """Automatically setup standardized test environment for all tests."""
    config = setup_test_environment()
    print(f"✅ Test environment initialized")
    print(f"   Workspace: {config['workspace_root']}")
    print(f"   Python paths: {len(config['python_paths'])}")
    print(f"   Available modules: {len(config['available_modules'])}")
    if config["missing_modules"]:
        print(f"   ⚠️ Missing modules: {len(config['missing_modules'])}")
    return config


@pytest.fixture(scope="function")
def temp_directory():
    """Create a temporary directory for test operations."""
    temp_dir = tempfile.mkdtemp(prefix="test_")
    yield Path(temp_dir)
    # Cleanup
    import shutil

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_missing_dependencies():
    """Mock missing dependencies to prevent import errors."""
    config = TEST_CONFIG
    mocks = {}

    for module in config["missing_modules"]:
        if module not in ["unittest.mock", "pathlib", "tempfile", "logging"]:
            mock_module = MagicMock()
            sys.modules[module] = mock_module
            mocks[module] = mock_module

    yield mocks

    # Cleanup mocks
    for module in mocks:
        if module in sys.modules:
            del sys.modules[module]


@pytest.fixture(scope="function")
def safe_import():
    """Provide safe import functionality that handles missing modules."""

    def _safe_import(module_name: str, fallback=None):
        corrected_name = get_module_import_path(module_name)
        try:
            return __import__(corrected_name)
        except ImportError:
            if fallback is not None:
                return fallback
            return MagicMock()

    return _safe_import


@pytest.fixture(scope="function")
def debug_logger():
    """Provide debug logger for test debugging."""
    logger = logging.getLogger("test_debug")
    logger.setLevel(logging.DEBUG)
    return logger


# Custom markers for categorizing tests
def pytest_configure(config):
    """Configure custom markers for the test suite."""
    markers = [
        "unit: Unit tests for individual components",
        "integration: Integration tests across components",
        "gui: GUI-related tests requiring mocking",
        "network: Network-related tests",
        "file_operations: File system operation tests",
        "security: Security-related tests",
        "performance: Performance and benchmarking tests",
        "edge_case: Edge case and boundary condition tests",
        "mock_heavy: Tests requiring extensive mocking",
        "import_issues: Tests that address import system issues",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_runtest_setup(item):
    """Setup for each test item."""
    # Ensure environment is properly configured
    setup_test_environment()


def pytest_runtest_makereport(item, call):
    """Create test reports with enhanced debugging."""
    if call.when == "call" and call.excinfo is not None:
        # Log import-related failures for debugging
        if "ImportError" in str(
            call.excinfo.value
        ) or "ModuleNotFoundError" in str(call.excinfo.value):
            logger = logging.getLogger("import_debug")
            logger.error(f"Import error in {item.name}: {call.excinfo.value}")
            logger.error(
                f"Current sys.path: {sys.path[:5]}..."
            )  # First 5 paths
