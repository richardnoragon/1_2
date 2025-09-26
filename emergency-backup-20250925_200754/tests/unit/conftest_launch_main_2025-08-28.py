#!/usr/bin/env python3
"""
Pytest configuration and fixtures for launch_main.py tests

This module provides shared configuration, fixtures, and utilities
for testing launch_main.py functionality.

Created: 2025-08-28
Target: src/rfu/launch_main.py
Framework: pytest
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add necessary paths for imports
test_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_root))
sys.path.insert(0, str(test_root / "src"))


@pytest.fixture(scope="session")
def test_workspace_root():
    """Provide the test workspace root directory."""
    return test_root


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp(prefix="launch_main_test_")
    workspace = Path(temp_dir) / "test_workspace"
    src_dir = workspace / "src"
    rfu_dir = src_dir / "rfu"

    # Create directory structure
    rfu_dir.mkdir(parents=True)

    yield {
        "temp_dir": temp_dir,
        "workspace": workspace,
        "src_dir": src_dir,
        "rfu_dir": rfu_dir,
    }

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_launch_main_file():
    """Create a mock launch_main.py file content."""
    return '''#!/usr/bin/env python3
"""
Simple launcher for RFU from the rfu directory
"""
import sys
import os
from pathlib import Path

# Get the workspace root (two levels up from this script)
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Now we can import and run the main application
if __name__ == "__main__":
    try:
        # Import the main function from the workspace root main.py
        sys.path.insert(0, str(workspace_root))
        
        # Read and execute the main.py from workspace root
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            
            # Change working directory to workspace root
            original_cwd = os.getcwd()
            os.chdir(workspace_root)
            
            try:
                # Execute the main.py code
                exec(main_code)
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
        else:
            print("Error: main.py not found in workspace root")
            print(f"Looking for: {main_py_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error launching application: {e}")
        print("\\nAlternative: Run from workspace root:")
        print("cd c:\\\\Users\\\\HP1\\\\1_2\\\\1_2")
        print("python main.py")
        sys.exit(1)
'''


@pytest.fixture
def mock_main_file():
    """Create a mock main.py file content."""
    return '''#!/usr/bin/env python3
"""Test main.py file for launch_main testing."""
print("Test main.py executed successfully")
test_executed = True
'''


@pytest.fixture
def setup_test_files(temp_workspace, mock_launch_main_file, mock_main_file):
    """Set up test files in the temporary workspace."""
    workspace_data = temp_workspace

    # Create launch_main.py
    launch_main_path = workspace_data["rfu_dir"] / "launch_main.py"
    with open(launch_main_path, "w", encoding="utf-8") as f:
        f.write(mock_launch_main_file)

    # Create main.py
    main_py_path = workspace_data["workspace"] / "main.py"
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(mock_main_file)

    workspace_data["launch_main_path"] = launch_main_path
    workspace_data["main_py_path"] = main_py_path

    return workspace_data


@pytest.fixture
def original_state():
    """Preserve and restore original system state."""
    original_cwd = os.getcwd()
    original_path = sys.path.copy()

    yield {"cwd": original_cwd, "path": original_path}

    # Restore state
    os.chdir(original_cwd)
    sys.path[:] = original_path


@pytest.fixture
def capture_output():
    """Capture stdout and stderr for testing."""
    from io import StringIO

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    captured_stdout = StringIO()
    captured_stderr = StringIO()

    sys.stdout = captured_stdout
    sys.stderr = captured_stderr

    yield {"stdout": captured_stdout, "stderr": captured_stderr}

    # Restore original streams
    sys.stdout = original_stdout
    sys.stderr = original_stderr


@pytest.fixture
def mock_subprocess():
    """Mock subprocess operations for testing."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mock subprocess output"
        mock_run.return_value.stderr = ""
        yield mock_run


# Test markers
pytest_plugins = []


# Configure test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions and methods"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests with real file system"
    )
    config.addinivalue_line(
        "markers", "edge_case: Edge cases and boundary condition tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and resource usage tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to execute"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test class names
        if "Integration" in item.cls.__name__ if item.cls else "":
            item.add_marker(pytest.mark.integration)
        elif "EdgeCase" in item.cls.__name__ if item.cls else "":
            item.add_marker(pytest.mark.edge_case)
        elif "Performance" in item.cls.__name__ if item.cls else "":
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)


# Utility functions for tests
def create_test_file(path, content, encoding="utf-8"):
    """Utility function to create test files."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
    return path


def assert_file_exists(path):
    """Utility function to assert file existence."""
    path = Path(path)
    assert path.exists(), f"File does not exist: {path}"
    assert path.is_file(), f"Path is not a file: {path}"


def assert_directory_exists(path):
    """Utility function to assert directory existence."""
    path = Path(path)
    assert path.exists(), f"Directory does not exist: {path}"
    assert path.is_dir(), f"Path is not a directory: {path}"


# Test data constants
TEST_LAUNCH_MAIN_MINIMAL = """#!/usr/bin/env python3
import sys
from pathlib import Path
workspace_root = Path(__file__).parent.parent.parent
print(f"Workspace: {workspace_root}")
"""

TEST_MAIN_SIMPLE = """print("Hello from main.py")"""

TEST_MAIN_WITH_ERROR = """
print("Starting main.py")
raise ValueError("Test error in main.py")
print("This should not print")
"""

TEST_MAIN_EMPTY = ""

# Export utility functions and constants for use in tests
__all__ = [
    "create_test_file",
    "assert_file_exists",
    "assert_directory_exists",
    "TEST_LAUNCH_MAIN_MINIMAL",
    "TEST_MAIN_SIMPLE",
    "TEST_MAIN_WITH_ERROR",
    "TEST_MAIN_EMPTY",
]
