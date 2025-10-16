"""
Hub.py Basic Unit Tests
Created: 2025-08-28
Target: src/rfu/hub.py

Basic test suite to verify core functionality and identify any import issues.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src path to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


# Test basic imports
def test_hub_imports():
    """Test that hub module can be imported successfully."""
    try:
        from tabbed_hub import RFUHub, UtilityWindow

        assert RFUHub is not None
        assert UtilityWindow is not None
    except ImportError as e:
        pytest.fail(f"Failed to import hub module: {e}")


def test_hub_constants():
    """Test that color and style constants are defined."""
    from tabbed_hub import DARK_BLUE, PRIMARY_BLUE, WHITE

    assert PRIMARY_BLUE == "#3498db"
    assert DARK_BLUE == "#2980b9"
    assert WHITE == "#ffffff"


@patch("rfu.hub.get_log_manager")
@patch("rfu.hub.get_config_manager")
@patch("rfu.hub.PYQT5_AVAILABLE", False)
def test_hub_initialization_no_gui(mock_get_config, mock_get_log):
    """Test RFUHub initialization without GUI."""
    from tabbed_hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_log_manager.get_logger.return_value = Mock()
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()

    # Create hub instance
    hub = RFUHub()

    # Verify basic attributes
    assert hasattr(hub, "registered_tools")
    assert hasattr(hub, "tool_status")
    assert hasattr(hub, "resource_manager")
    assert isinstance(hub.registered_tools, dict)
    assert isinstance(hub.tool_status, dict)
    assert isinstance(hub.resource_manager, dict)


@patch("rfu.hub.get_log_manager")
@patch("rfu.hub.get_config_manager")
@patch("rfu.hub.PYQT5_AVAILABLE", False)
def test_register_tool_basic(mock_get_config, mock_get_log):
    """Test basic tool registration."""
    from tabbed_hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_log_manager.get_logger.return_value = Mock()
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()

    # Create hub and test tool registration
    hub = RFUHub()
    mock_tool = Mock()

    result = hub.register_tool("test_tool", mock_tool)

    assert result is True
    assert "test_tool" in hub.registered_tools
    assert hub.registered_tools["test_tool"] == mock_tool


@patch("rfu.hub.get_log_manager")
@patch("rfu.hub.get_config_manager")
@patch("rfu.hub.PYQT5_AVAILABLE", False)
def test_unregister_tool_basic(mock_get_config, mock_get_log):
    """Test basic tool unregistration."""
    from tabbed_hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_log_manager.get_logger.return_value = Mock()
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()

    # Create hub and register/unregister tool
    hub = RFUHub()
    mock_tool = Mock()

    # Register then unregister
    hub.register_tool("test_tool", mock_tool)
    result = hub.unregister_tool("test_tool")

    assert result is True
    assert "test_tool" not in hub.registered_tools


def test_fallback_functions():
    """Test that fallback functions work when imports fail."""
    from tabbed_hub import error_handler, get_config_manager, get_log_manager

    # These should be the fallback implementations that work
    logger = get_log_manager()
    config = get_config_manager()

    # Test fallback config
    assert hasattr(config, "get")
    assert config.get("test_key", "default") == "default"

    # Test fallback error handler
    test_func = error_handler(lambda: "test")
    assert callable(test_func)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
