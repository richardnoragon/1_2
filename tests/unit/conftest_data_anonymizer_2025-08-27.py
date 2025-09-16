"""
Pytest Configuration for Data Anonymizer Unit Tests

File: conftest.py
Created: 2025-08-27
Purpose: Setup and configuration for pytest test execution

This file provides shared fixtures, setup, and teardown functionality
for the data_anonymizer unit test suite.
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root():
    """Fixture providing the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_timestamp():
    """Fixture providing the test execution timestamp."""
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


@pytest.fixture(scope="function")
def clean_sys_modules():
    """Fixture to clean sys.modules before and after each test."""
    original_modules = sys.modules.copy()
    yield
    
    # Reset sys.modules to original state
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name not in original_modules:
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]


@pytest.fixture(scope="function")
def mock_pyqt5():
    """Fixture providing mocked PyQt5 components."""
    with patch('PyQt5.QtWidgets.QApplication') as mock_qapp:
        with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
            mock_app = Mock()
            mock_qapp.return_value = mock_app
            mock_app.exec_.return_value = 0
            
            yield {
                'QApplication': mock_qapp,
                'QMessageBox': mock_msgbox,
                'app_instance': mock_app
            }


@pytest.fixture(scope="function")
def mock_data_anonymizer_imports():
    """Fixture for mocking data_anonymizer imports."""
    with patch('src.tools.privacy.data_anonymizer.PrivacyCleanerGUI') as mock_privacy:
        with patch('src.tools.privacy.data_anonymizer.SimplePrivacyHub') as mock_simple:
            yield {
                'PrivacyCleanerGUI': mock_privacy,
                'SimplePrivacyHub': mock_simple
            }


@pytest.fixture(scope="function")
def test_environment():
    """Fixture providing a clean test environment."""
    # Store original environment
    original_environ = os.environ.copy()
    original_argv = sys.argv.copy()
    
    # Setup test environment
    os.environ['PYTEST_RUNNING'] = 'true'
    os.environ['PYTHONPATH'] = str(PROJECT_ROOT)
    
    yield {
        'project_root': PROJECT_ROOT,
        'original_environ': original_environ,
        'original_argv': original_argv
    }
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_environ)
    sys.argv = original_argv


@pytest.fixture(scope="function", autouse=True)
def setup_logging():
    """Auto-fixture to setup logging for each test."""
    import logging

    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Create test logger
    logger = logging.getLogger('test_data_anonymizer')
    logger.info("Starting test execution")
    
    yield logger
    
    logger.info("Test execution completed")


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest behavior."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as a GUI test"
    )
    config.addinivalue_line(
        "markers", "import_test: mark test as an import mechanism test"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as error handling test"
    )


def pytest_runtest_setup(item):
    """Setup for each test item."""
    # Ensure clean environment for each test
    if 'PYTEST_RUNNING' not in os.environ:
        os.environ['PYTEST_RUNNING'] = 'true'


def pytest_runtest_teardown(item, nextitem):
    """Teardown for each test item."""
    # Clean up any test artifacts
    pass


def pytest_collection_modifyitems(config, items):
    """Modify collected test items."""
    # Auto-mark tests based on their names
    for item in items:
        if "import" in item.name.lower():
            item.add_marker(pytest.mark.import_test)
        if "gui" in item.name.lower():
            item.add_marker(pytest.mark.gui)
        if "error" in item.name.lower():
            item.add_marker(pytest.mark.error_handling)
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# Test data and utilities
TEST_DATA = {
    'window_title': "Data Anonymizer - Richard's File Utilities",
    'error_dialog_title': "Data Anonymizer Error",
    'pyqt5_error_msg': "Error: PyQt5 is required to run the Data Anonymizer.",
    'install_msg': "Please install PyQt5: pip install PyQt5"
}


class TestHelpers:
    """Helper utilities for testing."""
    
    @staticmethod
    def get_test_data(key):
        """Get test data by key."""
        return TEST_DATA.get(key)
    
    @staticmethod
    def create_mock_exception(message="Test exception"):
        """Create a mock exception for testing."""
        return Exception(message)
    
    @staticmethod
    def assert_function_called_with_args(mock_func, expected_args):
        """Assert that a mock function was called with expected arguments."""
        mock_func.assert_called_once()
        call_args = mock_func.call_args[0]
        for i, expected_arg in enumerate(expected_args):
            if i < len(call_args):
                assert expected_arg in str(call_args[i])


@pytest.fixture
def test_helpers():
    """Fixture providing test helper utilities."""
    return TestHelpers