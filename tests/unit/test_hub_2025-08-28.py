"""
Comprehensive Unit Tests for hub.py
Test file created on: 2025-08-28
Target: src/rfu/hub.py

This module provides comprehensive unit tests for the RFU Hub application,
covering all functions, methods, and edge cases with appropriate mocking
and error handling scenarios.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add src path to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the module under test
try:
    from src.hub import (DARK_BLUE, DARK_GRAY, DARKER_BLUE, DARKER_GRAY,
                         ERROR_RED, LIGHT_BLUE, LIGHT_GRAY, MEDIUM_GRAY,
                         PRIMARY_BLUE, PYQT5_AVAILABLE, SUCCESS_GREEN,
                         TEXT_DARK, TITLE_HEADER_STYLE, WARNING_ORANGE, WHITE,
                         RFUHub, UtilityWindow)
except ImportError as e:
    pytest.skip(f"Cannot import hub module: {e}", allow_module_level=True)

class TestRFUHubConstants:
    """Test class for RFU Hub constants and configuration."""
    
    def test_color_constants_defined(self):
        """Test that all color constants are properly defined."""
        assert PRIMARY_BLUE == "#3498db"
        assert DARK_BLUE == "#2980b9"
        assert DARKER_BLUE == "#1f618d"
        assert LIGHT_BLUE == "#5dade2"
        assert LIGHT_GRAY == "#ecf0f1"
        assert MEDIUM_GRAY == "#bdc3c7"
        assert DARK_GRAY == "#95a5a6"
        assert DARKER_GRAY == "#7f8c8d"
        assert TEXT_DARK == "#2c3e50"
        assert WHITE == "#ffffff"
        assert SUCCESS_GREEN == "#27ae60"
        assert WARNING_ORANGE == "#f39c12"
        assert ERROR_RED == "#e74c3c"
    
    def test_style_constants_defined(self):
        """Test that style constants are properly defined."""
        assert TITLE_HEADER_STYLE == f"color: {TEXT_DARK}; margin: 10px 0px;"


class TestUtilityWindow:
    """Test class for UtilityWindow functionality."""
    
    @pytest.fixture
    def mock_parent_hub(self):
        """Create a mock parent hub for testing."""
        parent = Mock()
        parent.menuBar.return_value = Mock()
        parent.menu_manager = Mock()
        return parent
    
    @pytest.fixture
    def mock_utility_widget(self):
        """Create a mock utility widget for testing."""
        widget = Mock()
        widget.status_changed = Mock()
        return widget
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_utility_window_init_with_pyqt5(self, mock_qmainwindow, mock_parent_hub, mock_utility_widget):
        """Test UtilityWindow initialization when PyQt5 is available."""
        window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
        
        # Verify the window was initialized with correct properties
        assert window.parent_hub == mock_parent_hub
        assert window.title == "Test Tool"  # This would be set by the mocked QMainWindow
    
    @patch('rfu.hub.PYQT5_AVAILABLE', False)
    def test_utility_window_init_without_pyqt5(self, mock_parent_hub, mock_utility_widget):
        """Test UtilityWindow initialization when PyQt5 is not available."""
        window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
        # When PyQt5 is not available, the constructor should return early
        assert window is not None
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_clone_menu_bar_success(self, mock_qmainwindow, mock_parent_hub, mock_utility_widget):
        """Test successful menu bar cloning."""
        mock_parent_hub.menu_manager = Mock()
        
        with patch('rfu.hub.SimpleMenuManager') as mock_menu_manager:
            window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
            window._clone_menu_bar(mock_parent_hub.menuBar())
            
            # Verify menu manager was created and configured
            mock_menu_manager.assert_called_once()
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_clone_menu_bar_exception(self, mock_qmainwindow, mock_parent_hub, mock_utility_widget):
        """Test menu bar cloning with exception handling."""
        mock_parent_hub.menu_manager = Mock()
        
        with patch('rfu.hub.SimpleMenuManager', side_effect=Exception("Test error")):
            window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
            # Should not raise exception, just print warning
            window._clone_menu_bar(mock_parent_hub.menuBar())
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_register_delegated_callbacks(self, mock_qmainwindow, mock_parent_hub, mock_utility_widget):
        """Test registration of delegated callbacks."""
        mock_parent_hub.menu_manager = Mock()
        mock_parent_hub.menu_manager.callbacks = {'test_callback': Mock()}
        
        window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
        window.menu_manager = Mock()
        window._register_delegated_callbacks()
        
        # Verify callbacks were registered
        window.menu_manager.register_callback.assert_called()
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_close_event(self, mock_qmainwindow, mock_parent_hub, mock_utility_widget):
        """Test close event handling."""
        window = UtilityWindow(mock_parent_hub, mock_utility_widget, "Test Tool")
        mock_event = Mock()
        
        window.closeEvent(mock_event)
        
        # Verify event was ignored (window hidden instead of closed)
        mock_event.ignore.assert_called_once()


class TestRFUHub:
    """Test class for RFUHub main functionality."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = Mock()
        return logger
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config manager for testing."""
        config = Mock()
        config.get.return_value = "default_value"
        return config
    
    @patch('rfu.hub.get_log_manager')
    @patch('rfu.hub.get_config_manager')
    @patch('rfu.hub.PYQT5_AVAILABLE', False)
    def test_hub_init_without_pyqt5(self, mock_get_config, mock_get_log):
        """Test RFUHub initialization without PyQt5."""
        mock_log_manager = Mock()
        mock_log_manager.get_logger.return_value = Mock()
        mock_get_log.return_value = mock_log_manager
        mock_get_config.return_value = Mock()
        
        hub = RFUHub()
        
        assert hub.registered_tools == {}
        assert hub.tool_status == {}
        assert hub.message_queue == []
        assert 'cpu' in hub.resource_manager
        assert 'memory' in hub.resource_manager
        assert 'disk' in hub.resource_manager
    
    @patch('rfu.hub.get_log_manager')
    @patch('rfu.hub.get_config_manager')
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_hub_init_with_pyqt5(self, mock_qmainwindow, mock_get_config, mock_get_log):
        """Test RFUHub initialization with PyQt5."""
        mock_log_manager = Mock()
        mock_log_manager.get_logger.return_value = Mock()
        mock_get_log.return_value = mock_log_manager
        mock_get_config.return_value = Mock()
        
        with patch.object(RFUHub, '_setup_gui'), \
             patch.object(RFUHub, '_setup_hub_integration'):
            hub = RFUHub()
            
            assert hub.registered_tools == {}
            assert hub.tool_status == {}
            assert hub.message_queue == []
    
    @patch('rfu.hub.get_log_manager')
    @patch('rfu.hub.get_config_manager')
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QMainWindow')
    def test_setup_gui(self, mock_qmainwindow, mock_get_config, mock_get_log):
        """Test GUI setup functionality."""
        mock_log_manager = Mock()
        mock_log_manager.get_logger.return_value = Mock()
        mock_get_log.return_value = mock_log_manager
        mock_get_config.return_value = Mock()
        
        with patch('rfu.hub.SimpleMenuManager') as mock_menu_manager, \
             patch.object(RFUHub, '_setup_menu_callbacks'), \
             patch.object(RFUHub, '_get_application_icon'), \
             patch.object(RFUHub, 'create_analysis_tab'), \
             patch.object(RFUHub, 'create_file_operations_tab'), \
             patch.object(RFUHub, 'create_metadata_tab'), \
             patch.object(RFUHub, 'create_network_tab'), \
             patch.object(RFUHub, 'create_pdf_tools_tab'), \
             patch.object(RFUHub, 'create_privacy_tab'), \
             patch.object(RFUHub, 'create_security_tab'), \
             patch.object(RFUHub, 'create_system_tab'), \
             patch.object(RFUHub, 'create_logs_tab'):
            
            hub = RFUHub()
            
            # Verify menu manager was created
            mock_menu_manager.assert_called_once()
    
    def test_register_tool_success(self):
        """Test successful tool registration."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            result = hub.register_tool("test_tool", tool_instance)
            
            assert result is True
            assert "test_tool" in hub.registered_tools
            assert hub.registered_tools["test_tool"] == tool_instance
            assert "test_tool" in hub.tool_status
            assert hub.tool_status["test_tool"]["status"] == "registered"
    
    def test_register_tool_existing(self):
        """Test registering an existing tool (should update)."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance1 = Mock()
            tool_instance2 = Mock()
            
            # Register first tool
            hub.register_tool("test_tool", tool_instance1)
            # Register same tool name with different instance
            result = hub.register_tool("test_tool", tool_instance2)
            
            assert result is True
            assert hub.registered_tools["test_tool"] == tool_instance2
    
    def test_register_tool_exception(self):
        """Test tool registration with exception."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            
            # Mock tool_status to raise exception
            with patch.object(hub, 'tool_status', side_effect=Exception("Test error")):
                result = hub.register_tool("test_tool", Mock())
                
                assert result is False
    
    def test_unregister_tool_success(self):
        """Test successful tool unregistration."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            # First register a tool
            hub.register_tool("test_tool", tool_instance)
            
            # Then unregister it
            result = hub.unregister_tool("test_tool")
            
            assert result is True
            assert "test_tool" not in hub.registered_tools
            assert "test_tool" not in hub.tool_status
    
    def test_unregister_tool_not_found(self):
        """Test unregistering a non-existent tool."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            
            result = hub.unregister_tool("non_existent_tool")
            
            assert result is False
    
    def test_unregister_tool_exception(self):
        """Test tool unregistration with exception."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            # Register a tool first
            hub.register_tool("test_tool", tool_instance)
            
            # Mock registered_tools to raise exception during deletion
            with patch.object(hub, 'registered_tools', side_effect=Exception("Test error")):
                result = hub.unregister_tool("test_tool")
                
                assert result is False
    
    def test_update_tool_progress(self):
        """Test tool progress update functionality."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            # Register a tool first
            hub.register_tool("test_tool", tool_instance)
            
            # Update progress
            hub.update_tool_progress("test_tool", 50, "Processing files")
            
            assert hub.tool_status["test_tool"]["progress"] == 50
            assert hub.tool_status["test_tool"]["current_operation"] == "Processing files"
            assert isinstance(hub.tool_status["test_tool"]["last_activity"], datetime)
    
    def test_update_tool_progress_completion(self):
        """Test tool progress update at 100% completion."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            hub.register_tool("test_tool", tool_instance)
            hub.update_tool_progress("test_tool", 100, "Completed")
            
            assert hub.tool_status["test_tool"]["progress"] == 100
            assert hub.tool_status["test_tool"]["current_operation"] == "Completed"
    
    def test_release_tool_resources(self):
        """Test resource release functionality."""
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
    
    def test_update_status_bar_with_status_bar(self):
        """Test status bar update when status bar exists."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            hub.status_bar = Mock()
            
            hub._update_status_bar("Test message")
            
            hub.status_bar.showMessage.assert_called_once_with("Test message", 5000)
    
    def test_update_status_bar_without_status_bar(self):
        """Test status bar update when status bar doesn't exist."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            
            # Should not raise exception when status_bar doesn't exist
            hub._update_status_bar("Test message")
    
    def test_show_with_pyqt5(self):
        """Test show method when PyQt5 is available."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', True), \
             patch('rfu.hub.QMainWindow'):
            
            hub = RFUHub()
            
            with patch.object(hub, '_setup_gui'), \
                 patch.object(hub, '_setup_hub_integration'), \
                 patch('rfu.hub.QMainWindow.show') as mock_show:
                
                hub.show()
                
                # Verify that the parent show method was called
                mock_show.assert_called_once()
    
    def test_show_without_pyqt5(self):
        """Test show method when PyQt5 is not available."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            
            with patch.object(hub, '_show_command_line_interface') as mock_cli:
                hub.show()
                
                mock_cli.assert_called_once()
    
    def test_show_command_line_interface(self):
        """Test command line interface display."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False), \
             patch('builtins.print') as mock_print:
            
            hub = RFUHub()
            hub._show_command_line_interface()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that some expected messages were printed
            printed_messages = [call[0][0] for call in mock_print.call_args_list]
            assert any("RICHARD'S FILE UTILITIES - COMMAND LINE MODE" in msg for msg in printed_messages)
    
    def test_get_application_icon_exists(self):
        """Test getting application icon when file exists."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', True), \
             patch('rfu.hub.QMainWindow'), \
             patch('os.path.exists', return_value=True), \
             patch('rfu.hub.QIcon') as mock_qicon:
            
            hub = RFUHub()
            
            with patch.object(hub, '_setup_gui'), \
                 patch.object(hub, '_setup_hub_integration'):
                
                icon = hub._get_application_icon()
                
                mock_qicon.assert_called()
    
    def test_get_application_icon_not_exists(self):
        """Test getting application icon when file doesn't exist."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', True), \
             patch('rfu.hub.QMainWindow'), \
             patch('os.path.exists', return_value=False), \
             patch('rfu.hub.QIcon') as mock_qicon:
            
            hub = RFUHub()
            
            with patch.object(hub, '_setup_gui'), \
                 patch.object(hub, '_setup_hub_integration'):
                
                icon = hub._get_application_icon()
                
                # Should return empty icon when file doesn't exist
                mock_qicon.assert_called_with()


class TestRFUHubMenuCallbacks:
    """Test class for RFU Hub menu callback methods."""
    
    @pytest.fixture
    def hub_instance(self):
        """Create a hub instance for testing menu callbacks."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            hub = RFUHub()
            hub.logger = Mock()
            hub._update_status_bar = Mock()
            return hub
    
    def test_menu_callback_methods(self, hub_instance):
        """Test all menu callback methods."""
        callbacks = [
            'new_project', 'open_file', 'save_file', 'save_as_file',
            'export_data', 'import_data', 'print_document', 'show_preferences',
            'undo', 'redo', 'cut', 'copy', 'paste', 'select_all',
            'find', 'replace', 'zoom_in', 'zoom_out', 'zoom_reset',
            'refresh', 'show_options', 'show_documentation', 'show_shortcuts',
            'show_about'
        ]
        
        for callback_name in callbacks:
            if hasattr(hub_instance, callback_name):
                callback_method = getattr(hub_instance, callback_name)
                
                # Call the method and verify it doesn't raise exceptions
                callback_method()
                
                # Verify status bar was updated
                hub_instance._update_status_bar.assert_called()
                
                # Verify logger was called
                hub_instance.logger.info.assert_called()
                
                # Reset mocks for next test
                hub_instance._update_status_bar.reset_mock()
                hub_instance.logger.reset_mock()
    
    def test_refresh_with_load_recent_logs(self, hub_instance):
        """Test refresh method when load_recent_logs is available."""
        hub_instance.load_recent_logs = Mock()
        
        hub_instance.refresh()
        
        hub_instance.load_recent_logs.assert_called_once()


class TestRFUHubToolOpening:
    """Test class for RFU Hub tool opening methods."""
    
    @pytest.fixture
    def hub_instance(self):
        """Create a hub instance for testing tool opening methods."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            hub = RFUHub()
            hub.logger = Mock()
            hub._update_status_bar = Mock()
            hub.tab_widget = Mock()
            return hub
    
    def test_open_tool_methods_success(self, hub_instance):
        """Test tool opening methods with successful imports."""
        tool_methods = [
            ('open_file_catalog', '..utilities.file_operations.file_catalog', 'FileCatalogGUI'),
            ('open_file_touch', '..utilities.file_operations.file_touch', 'FileTouchGUI'),
            ('open_file_splitter', '..utilities.file_operations.file_splitter', 'FileSplitterGUI'),
            ('open_secure_delete', '..utilities.file_operations.secure_delete', 'SecureDeleteGUI'),
            ('open_compression_tools', '..utilities.file_operations.compression', 'CompressionGUI'),
            ('open_duplicate_finder', '..utilities.file_operations.duplicate_finder', 'DuplicateFinderGUI'),
        ]
        
        for method_name, module_path, class_name in tool_methods:
            if hasattr(hub_instance, method_name):
                with patch(f'rfu.hub.{module_path}') as mock_module:
                    mock_tool_class = Mock()
                    mock_tool_instance = Mock()
                    mock_tool_class.return_value = mock_tool_instance
                    setattr(mock_module, class_name, mock_tool_class)
                    
                    method = getattr(hub_instance, method_name)
                    method()
                    
                    # Verify tool was created and shown
                    mock_tool_class.assert_called_once()
                    mock_tool_instance.show.assert_called_once()
                    
                    # Verify status was updated
                    hub_instance._update_status_bar.assert_called()
                    hub_instance.logger.info.assert_called()
    
    def test_open_tool_methods_import_error(self, hub_instance):
        """Test tool opening methods with import errors."""
        method_name = 'open_file_catalog'
        
        if hasattr(hub_instance, method_name):
            with patch('rfu.hub.FileCatalogGUI', side_effect=ImportError("Module not found")):
                method = getattr(hub_instance, method_name)
                method()
                
                # Verify error was handled gracefully
                hub_instance._update_status_bar.assert_called()
                hub_instance.logger.error.assert_called()
    
    def test_open_network_tools(self, hub_instance):
        """Test opening network tools tab."""
        hub_instance.open_network_tools()
        
        hub_instance.tab_widget.setCurrentIndex.assert_called_with(2)
        hub_instance._update_status_bar.assert_called()
        hub_instance.logger.info.assert_called()
    
    def test_open_security_tools(self, hub_instance):
        """Test opening security tools tab."""
        hub_instance.open_security_tools()
        
        hub_instance.tab_widget.setCurrentIndex.assert_called_with(3)
        hub_instance._update_status_bar.assert_called()
        hub_instance.logger.info.assert_called()
    
    def test_open_system_tools(self, hub_instance):
        """Test opening system tools tab."""
        hub_instance.open_system_tools()
        
        hub_instance.tab_widget.setCurrentIndex.assert_called_with(4)


class TestRFUHubLogManagement:
    """Test class for RFU Hub log management functionality."""
    
    @pytest.fixture
    def hub_instance(self):
        """Create a hub instance for testing log management."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            hub = RFUHub()
            hub.logger = Mock()
            hub._update_status_bar = Mock()
            hub.log_display = Mock()
            return hub
    
    def test_load_recent_logs_with_entries(self, hub_instance):
        """Test loading recent logs when entries exist."""
        # Mock logger with handlers that have get_recent_logs method
        mock_handler = Mock()
        mock_handler.get_recent_logs.return_value = [
            "2025-08-28 10:00:00 - INFO - Test log entry 1",
            "2025-08-28 10:01:00 - INFO - Test log entry 2",
        ]
        hub_instance.logger.handlers = [mock_handler]
        
        hub_instance.load_recent_logs()
        
        hub_instance.log_display.clear.assert_called_once()
        hub_instance.log_display.append.assert_called()
        hub_instance._update_status_bar.assert_called_with("Logs refreshed")
    
    def test_load_recent_logs_no_entries(self, hub_instance):
        """Test loading recent logs when no entries exist."""
        hub_instance.logger.handlers = []
        
        hub_instance.load_recent_logs()
        
        hub_instance.log_display.setText.assert_called_with("No recent log entries found.")
        hub_instance._update_status_bar.assert_called_with("Logs refreshed")
    
    def test_load_recent_logs_exception(self, hub_instance):
        """Test loading recent logs with exception."""
        hub_instance.logger.handlers = [Mock()]
        hub_instance.logger.handlers[0].get_recent_logs.side_effect = Exception("Test error")
        
        hub_instance.load_recent_logs()
        
        hub_instance.log_display.setText.assert_called()
        hub_instance.logger.error.assert_called()
    
    def test_clear_logs(self, hub_instance):
        """Test clearing log display."""
        hub_instance.clear_logs()
        
        hub_instance.log_display.clear.assert_called_once()
        hub_instance._update_status_bar.assert_called_with("Logs cleared")
        hub_instance.logger.info.assert_called_with("Log display cleared")
    
    def test_save_logs_success(self, hub_instance):
        """Test saving logs successfully."""
        hub_instance.log_display.toPlainText.return_value = "Test log content"
        
        with patch('rfu.hub.QFileDialog') as mock_dialog, \
             patch('builtins.open', create=True) as mock_file:
            
            mock_dialog.getSaveFileName.return_value = ("test_logs.txt", "")
            mock_file.return_value.__enter__.return_value = Mock()
            
            hub_instance.save_logs()
            
            mock_dialog.getSaveFileName.assert_called_once()
            mock_file.assert_called_once()
            hub_instance._update_status_bar.assert_called()
            hub_instance.logger.info.assert_called()
    
    def test_save_logs_cancelled(self, hub_instance):
        """Test saving logs when user cancels."""
        with patch('rfu.hub.QFileDialog') as mock_dialog:
            mock_dialog.getSaveFileName.return_value = ("", "")
            
            hub_instance.save_logs()
            
            # Verify no file operations occurred
            mock_dialog.getSaveFileName.assert_called_once()
    
    def test_save_logs_exception(self, hub_instance):
        """Test saving logs with exception."""
        with patch('rfu.hub.QFileDialog') as mock_dialog, \
             patch('builtins.open', create=True, side_effect=Exception("Test error")):
            
            mock_dialog.getSaveFileName.return_value = ("test_logs.txt", "")
            
            hub_instance.save_logs()
            
            hub_instance._update_status_bar.assert_called()
            hub_instance.logger.error.assert_called()


class TestRFUHubSignalHandlers:
    """Test class for RFU Hub signal handlers."""
    
    @pytest.fixture
    def hub_instance(self):
        """Create a hub instance for testing signal handlers."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            hub = RFUHub()
            return hub
    
    def test_signal_handlers(self, hub_instance):
        """Test all signal handler methods."""
        # Test _on_tool_registered
        hub_instance._on_tool_registered("test_tool", Mock())
        
        # Test _on_tool_unregistered
        hub_instance._on_tool_unregistered("test_tool")
        
        # Test _on_tool_progress_updated
        hub_instance._on_tool_progress_updated("test_tool", 50, "Processing")
        
        # Test _on_tool_status_changed
        hub_instance._on_tool_status_changed("test_tool", "active")
        
        # Test _on_hub_event_broadcast
        hub_instance._on_hub_event_broadcast("sender", "event_type", {})
        
        # All methods should execute without errors (they are currently pass statements)


class TestRFUHubButtonCreation:
    """Test class for RFU Hub button creation functionality."""
    
    @pytest.fixture
    def hub_instance(self):
        """Create a hub instance for testing button creation."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', True), \
             patch('rfu.hub.QMainWindow'):
            hub = RFUHub()
            return hub
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QPushButton')
    def test_create_styled_tool_button_primary(self, mock_button, hub_instance):
        """Test creating primary styled tool button."""
        mock_callback = Mock()
        mock_button_instance = Mock()
        mock_button.return_value = mock_button_instance
        
        with patch.object(hub_instance, '_setup_gui'), \
             patch.object(hub_instance, '_setup_hub_integration'):
            
            button = hub_instance._create_styled_tool_button(
                "Test Button", 
                "Test tooltip", 
                mock_callback, 
                primary=True
            )
            
            mock_button.assert_called_once_with("Test Button")
            mock_button_instance.setToolTip.assert_called_with("Test tooltip")
            mock_button_instance.clicked.connect.assert_called_with(mock_callback)
            mock_button_instance.setStyleSheet.assert_called()
    
    @patch('rfu.hub.PYQT5_AVAILABLE', True)
    @patch('rfu.hub.QPushButton')
    def test_create_styled_tool_button_secondary(self, mock_button, hub_instance):
        """Test creating secondary styled tool button."""
        mock_callback = Mock()
        mock_button_instance = Mock()
        mock_button.return_value = mock_button_instance
        
        with patch.object(hub_instance, '_setup_gui'), \
             patch.object(hub_instance, '_setup_hub_integration'):
            
            button = hub_instance._create_styled_tool_button(
                "Test Button", 
                "Test tooltip", 
                mock_callback, 
                primary=False
            )
            
            mock_button.assert_called_once_with("Test Button")
            mock_button_instance.setStyleSheet.assert_called()
    
    @patch('rfu.hub.PYQT5_AVAILABLE', False)
    def test_create_styled_tool_button_no_pyqt5(self, hub_instance):
        """Test creating button when PyQt5 is not available."""
        button = hub_instance._create_styled_tool_button(
            "Test Button", 
            "Test tooltip", 
            Mock(), 
            primary=True
        )
        
        assert button is None


class TestRFUHubEdgeCases:
    """Test class for RFU Hub edge cases and error scenarios."""
    
    def test_import_fallbacks(self):
        """Test import fallback mechanisms."""
        # Test that fallback functions work when imports fail
        from src.hub import error_handler, get_config_manager, get_log_manager

        # These should be the fallback implementations
        logger = get_log_manager()
        config = get_config_manager()
        
        # Test fallback logger
        assert hasattr(logger, 'info') or hasattr(logger, 'getLogger')
        
        # Test fallback config
        assert hasattr(config, 'get')
        assert config.get('test_key', 'default') == 'default'
        
        # Test fallback error handler
        test_func = error_handler(lambda: "test")
        assert callable(test_func)
    
    def test_resource_manager_structure(self):
        """Test resource manager initialization and structure."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            
            # Verify resource manager structure
            expected_resources = ['cpu', 'memory', 'disk']
            for resource in expected_resources:
                assert resource in hub.resource_manager
                assert 'available' in hub.resource_manager[resource]
                assert 'allocated_to' in hub.resource_manager[resource]
                assert hub.resource_manager[resource]['available'] is True
                assert hub.resource_manager[resource]['allocated_to'] is None
    
    def test_tool_status_structure(self):
        """Test tool status structure after registration."""
        with patch('rfu.hub.get_log_manager'), \
             patch('rfu.hub.get_config_manager'), \
             patch('rfu.hub.PYQT5_AVAILABLE', False):
            
            hub = RFUHub()
            tool_instance = Mock()
            
            hub.register_tool("test_tool", tool_instance)
            
            status = hub.tool_status["test_tool"]
            assert 'status' in status
            assert 'last_activity' in status
            assert 'progress' in status
            assert 'current_operation' in status
            
            assert status['status'] == 'registered'
            assert isinstance(status['last_activity'], datetime)
            assert status['progress'] == 0
            assert status['current_operation'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])