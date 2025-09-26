"""
Pytest configuration and fixtures for extract_tables_camelot tests
Created: 2025-08-24
Provides test fixtures, setup, and teardown methods
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before all tests."""
    print(f"\n{'='*60}")
    print(
        f"EXTRACT TABLES CAMELOT TEST SUITE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"{'='*60}")

    # Ensure test data directory exists
    os.makedirs(TEST_DATA_DIR, exist_ok=True)

    # Add the source directory to Python path for imports
    src_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "utilities",
        "pdf_tools",
        "pdf_content_extraction",
    )
    if src_path not in sys.path:
        sys.path.insert(0, os.path.abspath(src_path))

    yield

    print(f"\n{'='*60}")
    print(
        f"TEST SUITE COMPLETED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"{'='*60}")


@pytest.fixture(scope="session")
def test_data_directory():
    """Provide the test data directory path."""
    return TEST_DATA_DIR


@pytest.fixture
def temp_directory():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="test_extract_tables_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_directory):
    """Create a temporary config file for testing."""
    config_path = os.path.join(temp_directory, "config.json")
    test_config = {
        "extract_tables": {
            "flavor": "lattice",
            "line_scale": 15,
            "process_background": False,
            "table_borders": "normal",
            "edge_tol": 50,
            "row_tol": 2,
            "column_tol": 2,
            "pages": "",
        }
    }
    with open(config_path, "w") as f:
        json.dump(test_config, f, indent=4)

    yield config_path


@pytest.fixture
def temp_pdf_file(temp_directory):
    """Create a temporary PDF file for testing."""
    pdf_path = os.path.join(temp_directory, "test_document.pdf")
    # Create a dummy PDF file (just for path testing)
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4 dummy content for testing")

    yield pdf_path


@pytest.fixture
def temp_output_dir(temp_directory):
    """Create a temporary output directory for testing."""
    output_dir = os.path.join(temp_directory, "extracted_tables")
    os.makedirs(output_dir, exist_ok=True)
    yield output_dir


@pytest.fixture
def sample_config_data():
    """Provide sample configuration data for testing."""
    return {
        "extract_tables": {
            "flavor": "lattice",
            "line_scale": 15,
            "process_background": False,
            "table_borders": "normal",
            "edge_tol": 50,
            "row_tol": 2,
            "column_tol": 2,
            "pages": "1-3",
        },
        "other_settings": {"debug": True, "log_level": "INFO"},
    }


@pytest.fixture
def mock_camelot_table():
    """Create a mock camelot table object."""
    mock_table = Mock()
    mock_table.to_csv = Mock()
    mock_table.df = Mock()  # DataFrame property
    mock_table.shape = (10, 5)  # Table dimensions
    mock_table.accuracy = 95.5  # Accuracy score
    mock_table.whitespace = 12.3  # Whitespace percentage
    return mock_table


@pytest.fixture
def mock_camelot_tables(mock_camelot_table):
    """Create a list of mock camelot table objects."""
    table1 = mock_camelot_table
    table2 = Mock()
    table2.to_csv = Mock()
    table2.df = Mock()
    table2.shape = (8, 4)
    table2.accuracy = 88.7
    table2.whitespace = 15.2

    return [table1, table2]


@pytest.fixture
def mock_qt_application():
    """Mock QApplication for GUI testing."""
    with patch("PyQt5.QtWidgets.QApplication") as mock_app:
        mock_instance = Mock()
        mock_app.return_value = mock_instance
        mock_app.instance.return_value = mock_instance
        yield mock_app


@pytest.fixture
def mock_ui_file():
    """Mock UI file loading."""
    with patch("PyQt5.uic.loadUi") as mock_load_ui:
        yield mock_load_ui


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("extract_tables_camelot.logger") as logger_mock:
        logger_mock.info = Mock()
        logger_mock.debug = Mock()
        logger_mock.warning = Mock()
        logger_mock.error = Mock()
        logger_mock.critical = Mock()
        yield logger_mock


@pytest.fixture
def mock_file_operations():
    """Mock file system operations."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("os.makedirs") as mock_makedirs,
        patch("os.path.dirname") as mock_dirname,
        patch("os.path.basename") as mock_basename,
        patch("os.path.splitext") as mock_splitext,
        patch("os.path.join") as mock_join,
    ):

        # Set up default behaviors
        mock_exists.return_value = True
        mock_dirname.return_value = "/test/dir"
        mock_basename.return_value = "test_file.pdf"
        mock_splitext.return_value = ("test_file", ".pdf")
        mock_join.side_effect = lambda *args: "/".join(args)

        yield {
            "exists": mock_exists,
            "makedirs": mock_makedirs,
            "dirname": mock_dirname,
            "basename": mock_basename,
            "splitext": mock_splitext,
            "join": mock_join,
        }


@pytest.fixture
def mock_messagebox():
    """Mock QMessageBox for GUI testing."""
    with patch("PyQt5.QtWidgets.QMessageBox") as mock_box:
        mock_box.information = Mock()
        mock_box.warning = Mock()
        mock_box.critical = Mock()
        mock_box.question = Mock()
        yield mock_box


@pytest.fixture
def extraction_parameters():
    """Provide various parameter sets for extraction testing."""
    return {
        "basic": {"flavor": "lattice"},
        "advanced": {
            "flavor": "stream",
            "line_scale": 20,
            "process_background": True,
            "table_borders": "vertical",
            "edge_tol": 75,
            "row_tol": 3,
            "column_tol": 3,
            "pages": "1-5",
        },
        "minimal": {"flavor": "lattice", "pages": "1"},
        "invalid": {
            "flavor": "invalid_flavor",
            "line_scale": -1,
            "edge_tol": "invalid",
        },
    }


@pytest.fixture
def error_scenarios():
    """Provide different error scenarios for testing."""
    return {
        "file_not_found": FileNotFoundError("PDF file not found"),
        "permission_error": PermissionError("Permission denied"),
        "camelot_error": Exception("Camelot processing error"),
        "json_error": json.JSONDecodeError("Invalid JSON", "", 0),
        "os_error": OSError("Operating system error"),
        "value_error": ValueError("Invalid parameter value"),
        "runtime_error": RuntimeError("Runtime processing error"),
    }


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up test files after each test."""
    yield
    # Cleanup any remaining test files
    for root, dirs, files in os.walk(TEST_DATA_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".tmp"):
                try:
                    os.remove(os.path.join(root, file))
                except OSError:
                    pass


@pytest.fixture
def performance_monitor():
    """Monitor test performance and execution time."""
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    print(f"\nTest execution time: {execution_time:.3f} seconds")


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line("markers", "gui: mark test as a GUI test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_runtest_setup(item):
    """Set up before each test item."""
    # Print test name for detailed output
    if hasattr(item, "function"):
        print(f"\n🔍 Running: {item.function.__name__}")


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test item."""
    # Additional cleanup if needed
    pass


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(f"\n📊 Starting test session for extract_tables_camelot")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗂️  Test directory: {session.config.option.file_or_dir}")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    print(f"\n✅ Test session completed with exit status: {exitstatus}")
    if exitstatus == 0:
        print("🎉 All tests passed successfully!")
    else:
        print(f"❌ Some tests failed (exit code: {exitstatus})")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add additional terminal summary."""
    if hasattr(terminalreporter, "stats"):
        passed = len(terminalreporter.stats.get("passed", []))
        failed = len(terminalreporter.stats.get("failed", []))
        skipped = len(terminalreporter.stats.get("skipped", []))
        errors = len(terminalreporter.stats.get("error", []))

        print(f"\n📈 Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   🚫 Errors: {errors}")
        print(f"   📊 Total: {passed + failed + skipped + errors}")


# Test data creation helpers
def create_test_pdf_content():
    """Create realistic PDF content for testing."""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 100 Td
(Test PDF with table) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000174 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
268
%%EOF"""


def create_test_config(flavor="lattice", **kwargs):
    """Create test configuration data."""
    config = {
        "extract_tables": {
            "flavor": flavor,
            "line_scale": kwargs.get("line_scale", 15),
            "process_background": kwargs.get("process_background", False),
            "table_borders": kwargs.get("table_borders", "normal"),
            "edge_tol": kwargs.get("edge_tol", 50),
            "row_tol": kwargs.get("row_tol", 2),
            "column_tol": kwargs.get("column_tol", 2),
            "pages": kwargs.get("pages", ""),
        }
    }
    return config
