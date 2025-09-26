"""
Test Configuration for Advanced Folders GUI

Pytest configuration file specifically for GUI component testing.
Configures test environment, fixtures, and testing parameters for
PyQt5 GUI components with enterprise testing standards.

Author: RFU Development Team
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test configuration
pytest_plugins = ["pytestqt"]

# Test markers


def pytest_configure(config):
    """Configure pytest markers and settings."""
    config.addinivalue_line(
        "markers", "gui: GUI tests requiring PyQt5 and display"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and stress tests"
    )
    config.addinivalue_line(
        "markers", "accessibility: Accessibility compliance tests"
    )
    config.addinivalue_line("markers", "slow: Slow running tests (>1 second)")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add appropriate markers."""
    for item in items:
        # Add gui marker to all tests
        if not any(marker.name == "gui" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.gui)

        # Add unit marker to most tests by default
        if not any(
            marker.name in ["integration", "performance", "accessibility"]
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)


# Skip all tests if PyQt5 is not available
def pytest_runtest_setup(item):
    """Skip tests if PyQt5 is not available."""
    try:
        import PyQt5  # noqa: F401
    except ImportError:
        pytest.skip("PyQt5 not available")


# Test directory configuration
def pytest_sessionstart(session):
    """Set up test session."""
    # Ensure we're in the correct directory context
    test_dir = Path(__file__).parent
    os.chdir(test_dir.parent.parent.parent.parent.parent)  # Go to project root
