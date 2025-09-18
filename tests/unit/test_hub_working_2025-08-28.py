"""
Hub.py Working Unit Tests
Created: 2025-08-28
Target: src/rfu/hub.py

Working test suite that properly handles the hub initialization issues.
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add src path to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def test_hub_imports():
    """Test that hub module can be imported successfully."""
    try:
        from src.hub import RFUHub, UtilityWindow
        assert RFUHub is not None
        assert UtilityWindow is not None
    except ImportError as e:
        pytest.fail(f"Failed to import hub module: {e}")


def test_hub_constants():
    """Test that color and style constants are defined."""
    from src.hub import (DARK_BLUE, ERROR_RED, PRIMARY_BLUE, SUCCESS_GREEN,
                         TITLE_HEADER_STYLE, WARNING_ORANGE, WHITE)
    assert PRIMARY_BLUE == "#3498db"
    assert DARK_BLUE == "#2980b9"
    assert WHITE == "#ffffff"
    assert SUCCESS_GREEN == "#27ae60"
    assert WARNING_ORANGE == "#f39c12"
    assert ERROR_RED == "#e74c3c"
    assert "color: #2c3e50" in TITLE_HEADER_STYLE


@patch('rfu.hub.get_log_manager')
@patch('rfu.hub.get_config_manager')
@patch('rfu.hub.PYQT5_AVAILABLE', False)
def test_hub_basic_attributes(mock_get_config, mock_get_log):
    """Test RFUHub basic attributes without GUI."""
    from src.hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_log_manager.get_logger.return_value = Mock()
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()
    
    # Create hub instance
    hub = RFUHub()
    
    # Verify basic attributes exist
    assert hasattr(hub, 'registered_tools')
    assert hasattr(hub, 'tool_status')
    assert hasattr(hub, 'resource_manager')
    assert hasattr(hub, 'message_queue')
    
    # Verify correct types
    assert isinstance(hub.registered_tools, dict)
    assert isinstance(hub.tool_status, dict)
    assert isinstance(hub.resource_manager, dict)
    assert isinstance(hub.message_queue, list)
    
    # Verify resource manager structure
    assert 'cpu' in hub.resource_manager
    assert 'memory' in hub.resource_manager
    assert 'disk' in hub.resource_manager
    
    for resource in ['cpu', 'memory', 'disk']:
        assert 'available' in hub.resource_manager[resource]
        assert 'allocated_to' in hub.resource_manager[resource]


@patch('rfu.hub.get_log_manager')
@patch('rfu.hub.get_config_manager')
@patch('rfu.hub.PYQT5_AVAILABLE', False)
def test_tool_registration_structure(mock_get_config, mock_get_log):
    """Test tool registration data structures."""
    from src.hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_logger = Mock()
    mock_log_manager.get_logger.return_value = mock_logger
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()
    
    # Create hub instance
    hub = RFUHub()
    
    # Mock the status bar update method to avoid initialization issues
    hub._update_status_bar = Mock()
    
    # Test tool registration
    mock_tool = Mock()
    result = hub.register_tool("test_tool", mock_tool)
    
    assert result is True
    assert "test_tool" in hub.registered_tools
    assert hub.registered_tools["test_tool"] == mock_tool
    assert "test_tool" in hub.tool_status
    
    # Verify tool status structure
    status = hub.tool_status["test_tool"]
    assert 'status' in status
    assert 'last_activity' in status
    assert 'progress' in status
    assert 'current_operation' in status
    assert status['status'] == 'registered'
    assert isinstance(status['last_activity'], datetime)
    assert status['progress'] == 0
    assert status['current_operation'] is None


@patch('rfu.hub.get_log_manager')
@patch('rfu.hub.get_config_manager')
@patch('rfu.hub.PYQT5_AVAILABLE', False)
def test_tool_unregistration(mock_get_config, mock_get_log):
    """Test tool unregistration functionality."""
    from src.hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_logger = Mock()
    mock_log_manager.get_logger.return_value = mock_logger
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()
    
    # Create hub instance
    hub = RFUHub()
    hub._update_status_bar = Mock()
    
    # Register then unregister tool
    mock_tool = Mock()
    hub.register_tool("test_tool", mock_tool)
    
    # Test unregistration
    result = hub.unregister_tool("test_tool")
    
    assert result is True
    assert "test_tool" not in hub.registered_tools
    assert "test_tool" not in hub.tool_status


@patch('rfu.hub.get_log_manager')
@patch('rfu.hub.get_config_manager')
@patch('rfu.hub.PYQT5_AVAILABLE', False)
def test_progress_update(mock_get_config, mock_get_log):
    """Test tool progress update functionality."""
    from src.hub import RFUHub

    # Setup mocks
    mock_log_manager = Mock()
    mock_logger = Mock()
    mock_log_manager.get_logger.return_value = mock_logger
    mock_get_log.return_value = mock_log_manager
    mock_get_config.return_value = Mock()
    
    # Create hub instance
    hub = RFUHub()
    hub._update_status_bar = Mock()
    
    # Register a tool first
    mock_tool = Mock()
    hub.register_tool("test_tool", mock_tool)
    
    # Test progress update
    hub.update_tool_progress("test_tool", 50, "Processing files")
    
    status = hub.tool_status["test_tool"]
    assert status['progress'] == 50
    assert status['current_operation'] == "Processing files"
    assert isinstance(status['last_activity'], datetime)


def test_resource_manager_structure():
    """Test resource manager initialization."""
    from src.hub import RFUHub
    
    with patch('rfu.hub.get_log_manager'), \
         patch('rfu.hub.get_config_manager'), \
         patch('rfu.hub.PYQT5_AVAILABLE', False):
        
        hub = RFUHub()
        
        expected_resources = ['cpu', 'memory', 'disk']
        for resource in expected_resources:
            assert resource in hub.resource_manager
            assert hub.resource_manager[resource]['available'] is True
            assert hub.resource_manager[resource]['allocated_to'] is None


def test_resource_release():
    """Test resource release functionality."""
    from src.hub import RFUHub
    
    with patch('rfu.hub.get_log_manager'), \
         patch('rfu.hub.get_config_manager'), \
         patch('rfu.hub.PYQT5_AVAILABLE', False):
        
        hub = RFUHub()
        
        # Allocate resources to a tool
        hub.resource_manager['cpu']['available'] = False
        hub.resource_manager['cpu']['allocated_to'] = 'test_tool'
        hub.resource_manager['memory']['available'] = False
        hub.resource_manager['memory']['allocated_to'] = 'test_tool'
        
        # Release resources
        hub._release_tool_resources('test_tool')
        
        assert hub.resource_manager['cpu']['available'] is True
        assert hub.resource_manager['cpu']['allocated_to'] is None
        assert hub.resource_manager['memory']['available'] is True
        assert hub.resource_manager['memory']['allocated_to'] is None


def test_signal_handlers():
    """Test signal handler methods (should not raise exceptions)."""
    from src.hub import RFUHub
    
    with patch('rfu.hub.get_log_manager'), \
         patch('rfu.hub.get_config_manager'), \
         patch('rfu.hub.PYQT5_AVAILABLE', False):
        
        hub = RFUHub()
        
        # Test all signal handlers (they should not raise exceptions)
        hub._on_tool_registered("test_tool", Mock())
        hub._on_tool_unregistered("test_tool")
        hub._on_tool_progress_updated("test_tool", 50, "Processing")
        hub._on_tool_status_changed("test_tool", "active")
        hub._on_hub_event_broadcast("sender", "event_type", {})


def test_menu_callbacks_exist():
    """Test that menu callback methods exist."""
    from src.hub import RFUHub
    
    with patch('rfu.hub.get_log_manager'), \
         patch('rfu.hub.get_config_manager'), \
         patch('rfu.hub.PYQT5_AVAILABLE', False):
        
        hub = RFUHub()
        hub._update_status_bar = Mock()
        hub.logger = Mock()
        
        # Test that callback methods exist and can be called
        callback_methods = [
            'new_project', 'open_file', 'save_file', 'refresh',
            'show_about', 'undo', 'redo', 'copy', 'paste'
        ]
        
        for method_name in callback_methods:
            assert hasattr(hub, method_name)
            method = getattr(hub, method_name)
            assert callable(method)
            
            # Call the method to ensure it doesn't raise exceptions
            method()


def test_tool_opening_methods_exist():
    """Test that tool opening methods exist."""
    from src.hub import RFUHub
    
    with patch('rfu.hub.get_log_manager'), \
         patch('rfu.hub.get_config_manager'), \
         patch('rfu.hub.PYQT5_AVAILABLE', False):
        
        hub = RFUHub()
        
        # Test that tool opening methods exist
        tool_methods = [
            'open_network_tools', 'open_security_tools', 'open_system_tools'
        ]
        
        for method_name in tool_methods:
            assert hasattr(hub, method_name)
            method = getattr(hub, method_name)
            assert callable(method)


def test_utility_window_basic():
    """Test UtilityWindow basic functionality."""
    from src.hub import UtilityWindow
    
    with patch('rfu.hub.PYQT5_AVAILABLE', False):
        parent_hub = Mock()
        utility_widget = Mock()
        
        # Should not raise exception even when PyQt5 is not available
        window = UtilityWindow(parent_hub, utility_widget, "Test Tool")
        assert window is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])