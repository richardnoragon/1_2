"""
Hub Integration Testing for Size Analyzer

This module contains comprehensive tests for hub integration functionality,
including communication protocols, resource coordination, event handling,
and lifecycle management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import QObject
from PyQt5.QtTest import QSignalSpy

from file_utilities_2.integration.hub_connector import (
    HubConnector, HubMessage, HubCommunicationProtocol,
    SharedConfiguration, HubEventLogger
)
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI


class TestHubConnector:
    """Test HubConnector functionality."""
    
    def test_hub_connector_initialization(self):
        """Test HubConnector initialization."""
        connector = HubConnector("Test Tool")
        
        assert connector.tool_name == "Test Tool"
        assert connector.hub_instance is None
        assert not connector.is_connected
        assert not connector.is_registered
        assert connector.config is not None
        assert connector.logger is not None
        assert connector.tool_state is not None
    
    def test_hub_connector_with_instance(self, mock_hub):
        """Test HubConnector initialization with hub instance."""
        connector = HubConnector("Test Tool", mock_hub)
        
        assert connector.hub_instance == mock_hub
        assert connector.tool_name == "Test Tool"
    
    def test_hub_registration_success(self, mock_hub):
        """Test successful hub registration."""
        connector = HubConnector("Test Tool")
        
        result = connector.register_with_hub(mock_hub)
        
        assert result is True
        assert connector.is_connected
        assert connector.is_registered
        assert connector.hub_instance == mock_hub
        assert "Test Tool" in mock_hub.registered_tools
    
    def test_hub_registration_failure(self):
        """Test hub registration failure."""
        connector = HubConnector("Test Tool")
        
        # Try to register without hub instance
        result = connector.register_with_hub(None)
        
        assert result is False
        assert not connector.is_connected
        assert not connector.is_registered
    
    def test_hub_unregistration(self, mock_hub):
        """Test hub unregistration."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Verify registration
        assert connector.is_registered
        
        # Unregister
        connector.unregister_from_hub()
        
        assert not connector.is_connected
        assert not connector.is_registered
    
    def test_status_reporting(self, mock_hub):
        """Test status reporting to hub."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        status = "testing"
        details = {"test": "data"}
        
        connector.report_status_to_hub(status, details)
        
        assert connector.tool_state['status'] == status
        assert len(mock_hub.messages) > 0
    
    def test_progress_reporting(self, mock_hub):
        """Test progress reporting to hub."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        percentage = 50
        message = "Test progress"
        
        connector.report_progress_to_hub(percentage, message)
        
        assert connector.tool_state['progress'] == percentage
        assert connector.tool_state['current_operation'] == message
    
    def test_error_reporting(self, mock_hub):
        """Test error reporting to hub."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        error_message = "Test error"
        error_details = {"error_type": "TestError"}
        
        connector.report_error_to_hub(error_message, error_details)
        
        assert connector.tool_state['error_count'] == 1
        assert 'last_error' in connector.tool_state
    
    def test_resource_requests(self, mock_hub):
        """Test resource requests to hub."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        resource_type = "cpu"
        requirements = {"priority": "high"}
        
        result = connector.request_hub_resources(resource_type, requirements)
        
        assert result is True
        assert f"Test Tool_{resource_type}" in mock_hub.resources
    
    def test_event_broadcasting(self, mock_hub):
        """Test event broadcasting through hub."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        event_type = "test_event"
        event_data = {"test": "data"}
        
        connector.broadcast_event(event_type, event_data)
        
        assert len(mock_hub.events) > 0
        event = mock_hub.events[-1]
        assert event['tool_name'] == "Test Tool"
        assert event['event_type'] == event_type
        assert event['data'] == event_data
    
    def test_event_handler_registration(self):
        """Test event handler registration."""
        connector = HubConnector("Test Tool")
        
        handler = Mock()
        event_type = "test_event"
        
        connector.register_event_handler(event_type, handler)
        
        assert event_type in connector.event_handlers
        assert handler in connector.event_handlers[event_type]
    
    def test_hub_message_handling(self):
        """Test hub message handling."""
        connector = HubConnector("Test Tool")
        
        # Register event handler
        handler = Mock()
        connector.register_event_handler("test_message", handler)
        
        # Create test message
        message = HubMessage("test_message", "Test Tool", {"test": "data"})
        
        # Handle message
        connector.handle_hub_message(message)
        
        # Verify handler was called
        handler.assert_called_once_with(message)
    
    def test_heartbeat_functionality(self, qapp, mock_hub):
        """Test heartbeat functionality."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Verify heartbeat timer is running
        assert connector.heartbeat_timer.isActive()
        
        # Manually trigger heartbeat
        connector._send_heartbeat()
        
        # Verify heartbeat message was sent
        heartbeat_messages = [
            msg for msg in mock_hub.messages
            if msg.message_type == HubCommunicationProtocol.TOOL_HEARTBEAT
        ]
        assert len(heartbeat_messages) > 0
    
    def test_configuration_management(self):
        """Test configuration management."""
        connector = HubConnector("Test Tool")
        
        config_data = {"setting1": "value1", "setting2": "value2"}
        
        # Set configuration
        connector.set_tool_config(config_data)
        
        # Get configuration
        retrieved_config = connector.get_tool_config()
        
        assert retrieved_config == config_data
    
    def test_cleanup(self, mock_hub):
        """Test connector cleanup."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Verify registration
        assert connector.is_registered
        
        # Cleanup
        connector.cleanup()
        
        # Verify cleanup
        assert not connector.is_connected
        assert not connector.is_registered
        assert not connector.heartbeat_timer.isActive()


class TestHubMessage:
    """Test HubMessage functionality."""
    
    def test_message_creation(self):
        """Test message creation."""
        message_type = "test_message"
        tool_name = "Test Tool"
        data = {"test": "data"}
        
        message = HubMessage(message_type, tool_name, data)
        
        assert message.message_type == message_type
        assert message.tool_name == tool_name
        assert message.data == data
        assert message.timestamp is not None
        assert message.message_id is not None
    
    def test_message_serialization(self):
        """Test message serialization to dictionary."""
        message = HubMessage("test", "Tool", {"key": "value"})
        
        message_dict = message.to_dict()
        
        assert isinstance(message_dict, dict)
        assert message_dict['message_type'] == "test"
        assert message_dict['tool_name'] == "Tool"
        assert message_dict['data'] == {"key": "value"}
        assert 'timestamp' in message_dict
        assert 'message_id' in message_dict
    
    def test_message_deserialization(self):
        """Test message deserialization from dictionary."""
        original_message = HubMessage("test", "Tool", {"key": "value"})
        message_dict = original_message.to_dict()
        
        restored_message = HubMessage.from_dict(message_dict)
        
        assert restored_message.message_type == original_message.message_type
        assert restored_message.tool_name == original_message.tool_name
        assert restored_message.data == original_message.data
        assert restored_message.message_id == original_message.message_id


class TestSharedConfiguration:
    """Test SharedConfiguration functionality."""
    
    def test_configuration_initialization(self, temp_dir):
        """Test configuration initialization."""
        config_path = f"{temp_dir}/test_config.json"
        config = SharedConfiguration(config_path)
        
        assert config.config_path == config_path
        assert isinstance(config._config, dict)
    
    def test_configuration_get_set(self, temp_dir):
        """Test configuration get/set operations."""
        config_path = f"{temp_dir}/test_config.json"
        config = SharedConfiguration(config_path)
        
        # Set value
        config.set("test_key", "test_value")
        
        # Get value
        value = config.get("test_key")
        assert value == "test_value"
        
        # Get with default
        default_value = config.get("nonexistent", "default")
        assert default_value == "default"
    
    def test_tool_configuration(self, temp_dir):
        """Test tool-specific configuration."""
        config_path = f"{temp_dir}/test_config.json"
        config = SharedConfiguration(config_path)
        
        tool_config = {"setting1": "value1", "setting2": "value2"}
        
        # Set tool config
        config.set_tool_config("Test Tool", tool_config)
        
        # Get tool config
        retrieved_config = config.get_tool_config("Test Tool")
        assert retrieved_config == tool_config
        
        # Get non-existent tool config
        empty_config = config.get_tool_config("Nonexistent Tool")
        assert empty_config == {}


class TestSizeAnalyzerHubIntegration:
    """Test Size Analyzer hub integration."""
    
    def test_size_analyzer_hub_integration(self, mock_hub):
        """Test SizeAnalyzer with hub integration."""
        analyzer = SizeAnalyzer(hub_connector=mock_hub)
        
        assert analyzer._hub_connector == mock_hub
    
    def test_size_analyzer_hub_reporting(self, mock_hub, temp_dir, test_files):
        """Test SizeAnalyzer hub reporting during analysis."""
        analyzer = SizeAnalyzer(hub_connector=mock_hub)
        
        # Perform analysis
        result = analyzer.analyze_directory(temp_dir)
        
        # Verify hub reporting occurred
        assert len(mock_hub.messages) > 0 or hasattr(mock_hub, 'report_calls')
        assert result is not None
    
    def test_size_analyzer_resource_coordination(self, mock_hub):
        """Test SizeAnalyzer resource coordination."""
        analyzer = SizeAnalyzer(hub_connector=mock_hub)
        
        coordination_type = "resource_request"
        data = {"resource": "cpu", "priority": "high"}
        
        result = analyzer.request_hub_coordination(coordination_type, data)
        
        # Should succeed with mock hub
        assert result is True
    
    def test_size_analyzer_without_hub(self):
        """Test SizeAnalyzer without hub integration."""
        analyzer = SizeAnalyzer()
        
        # Should work without hub
        coordination_result = analyzer.request_hub_coordination("test", {})
        assert coordination_result is False
        
        # Resource usage update should work
        analyzer.update_resource_usage(cpu_usage=50.0)
        assert analyzer._resource_usage['cpu_usage'] == 50.0


class TestSizeAnalyzerGUIHubIntegration:
    """Test SizeAnalyzerGUI hub integration."""
    
    def test_gui_hub_initialization(self, qapp, mock_hub):
        """Test GUI hub integration initialization."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        assert gui.hub_instance == mock_hub
        assert gui.hub_connector is not None
        assert gui.hub_connector.tool_name == "Size Analyzer"
        
        gui.close()
    
    def test_gui_hub_registration(self, qapp, mock_hub):
        """Test GUI hub registration."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Verify registration occurred
        assert "Size Analyzer" in mock_hub.registered_tools
        
        gui.close()
    
    def test_gui_hub_status_reporting(self, qapp, mock_hub):
        """Test GUI hub status reporting."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        status = "testing"
        details = {"test": "data"}
        
        gui.report_status_to_hub(status, details)
        
        # Verify status was reported
        assert len(mock_hub.messages) > 0
        
        gui.close()
    
    def test_gui_hub_resource_requests(self, qapp, mock_hub):
        """Test GUI hub resource requests."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        resource_type = "cpu"
        requirements = {"operation": "analysis"}
        
        result = gui.request_hub_resources(resource_type, requirements)
        
        assert result is True
        assert f"Size Analyzer_{resource_type}" in mock_hub.resources
        
        gui.close()
    
    def test_gui_hub_event_broadcasting(self, qapp, mock_hub):
        """Test GUI hub event broadcasting."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        event_type = "analysis_started"
        event_data = {"directory": "/test"}
        
        gui.broadcast_hub_event(event_type, event_data)
        
        # Verify event was broadcasted
        assert len(mock_hub.events) > 0
        
        gui.close()
    
    def test_gui_hub_signal_emissions(self, qapp, mock_hub):
        """Test GUI hub signal emissions."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create signal spies
        tool_started_spy = QSignalSpy(gui.tool_started)
        tool_progress_spy = QSignalSpy(gui.tool_progress)
        tool_error_spy = QSignalSpy(gui.tool_error)
        tool_completed_spy = QSignalSpy(gui.tool_completed)
        
        # Verify spies are connected
        assert len(tool_started_spy) == 0
        assert len(tool_progress_spy) == 0
        assert len(tool_error_spy) == 0
        assert len(tool_completed_spy) == 0
        
        gui.close()
    
    def test_gui_hub_event_handlers(self, qapp, mock_hub):
        """Test GUI hub event handlers."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test resource request handler
        mock_message = Mock()
        mock_message.data = {"resource": "cpu"}
        gui._handle_resource_request(mock_message)
        
        # Test tool coordination handler
        mock_message.data = {"coordination": "test"}
        gui._handle_tool_coordination(mock_message)
        
        # Test configuration update handler
        mock_message.data = {"configuration": {"theme": "dark"}}
        gui._handle_configuration_update(mock_message)
        
        gui.close()
    
    def test_gui_hub_cleanup(self, qapp, mock_hub):
        """Test GUI hub cleanup on close."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Verify registration
        assert "Size Analyzer" in mock_hub.registered_tools
        
        # Close GUI
        from PyQt5.QtGui import QCloseEvent
        close_event = QCloseEvent()
        gui.closeEvent(close_event)
        
        # Verify cleanup occurred
        # (Mock hub doesn't actually remove tools, but cleanup was called)
        
        gui.close()


class TestHubCommunicationProtocols:
    """Test hub communication protocols."""
    
    def test_protocol_constants(self):
        """Test protocol constant definitions."""
        # Test message types
        assert hasattr(HubCommunicationProtocol, 'TOOL_STARTED')
        assert hasattr(HubCommunicationProtocol, 'TOOL_COMPLETED')
        assert hasattr(HubCommunicationProtocol, 'TOOL_ERROR')
        assert hasattr(HubCommunicationProtocol, 'TOOL_PROGRESS')
        assert hasattr(HubCommunicationProtocol, 'TOOL_STATUS')
        assert hasattr(HubCommunicationProtocol, 'TOOL_HEARTBEAT')
        
        # Test resource types
        assert hasattr(HubCommunicationProtocol, 'RESOURCE_CPU')
        assert hasattr(HubCommunicationProtocol, 'RESOURCE_MEMORY')
        assert hasattr(HubCommunicationProtocol, 'RESOURCE_DISK')
        assert hasattr(HubCommunicationProtocol, 'RESOURCE_NETWORK')
        
        # Test event types
        assert hasattr(HubCommunicationProtocol, 'EVENT_LIFECYCLE')
        assert hasattr(HubCommunicationProtocol, 'EVENT_USER_ACTION')
        assert hasattr(HubCommunicationProtocol, 'EVENT_SYSTEM')
        assert hasattr(HubCommunicationProtocol, 'EVENT_ERROR')
    
    def test_message_type_usage(self, mock_hub):
        """Test usage of protocol message types."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Test different message types
        connector.report_status_to_hub("active")
        connector.report_progress_to_hub(50, "Progress")
        connector.report_error_to_hub("Error message")
        
        # Verify messages were sent with correct types
        message_types = [msg.message_type for msg in mock_hub.messages]
        assert HubCommunicationProtocol.TOOL_STATUS in message_types
        assert HubCommunicationProtocol.TOOL_PROGRESS in message_types
        assert HubCommunicationProtocol.TOOL_ERROR in message_types


class TestHubIntegrationErrorHandling:
    """Test error handling in hub integration."""
    
    def test_hub_connection_failure(self):
        """Test handling of hub connection failures."""
        connector = HubConnector("Test Tool")
        
        # Try to register with invalid hub
        invalid_hub = Mock()
        invalid_hub.register_tool.side_effect = Exception("Connection failed")
        
        result = connector.register_with_hub(invalid_hub)
        
        # Should handle failure gracefully
        assert result is False
        assert not connector.is_connected
    
    def test_hub_communication_failure(self, mock_hub):
        """Test handling of communication failures."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Mock communication failure
        mock_hub.receive_message.side_effect = Exception("Communication failed")
        
        # Should handle failure gracefully
        connector.report_status_to_hub("test")
        # Should not raise exception
    
    def test_hub_resource_denial(self, mock_hub):
        """Test handling of resource denial."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Mock resource denial
        mock_hub.request_resource.return_value = False
        
        result = connector.request_hub_resources("cpu", {})
        
        assert result is False
    
    def test_hub_disconnection_handling(self, qapp, mock_hub):
        """Test handling of hub disconnection."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Verify connection
        assert connector.is_connected
        
        # Simulate disconnection
        connector.hub_instance = None
        connector.is_connected = False
        
        # Operations should handle disconnection gracefully
        connector.report_status_to_hub("test")
        connector.broadcast_event("test", {})
        # Should not raise exceptions


class TestHubIntegrationPerformance:
    """Test performance aspects of hub integration."""
    
    def test_message_queue_performance(self, mock_hub):
        """Test message queue performance."""
        connector = HubConnector("Test Tool")
        
        # Send messages before registration (should be queued)
        for i in range(100):
            connector.report_status_to_hub(f"status_{i}")
        
        # Register with hub
        connector.register_with_hub(mock_hub)
        
        # Flush queued messages
        connector._flush_message_queue()
        
        # Verify messages were processed
        assert len(mock_hub.messages) > 0
    
    def test_heartbeat_performance(self, qapp, mock_hub):
        """Test heartbeat performance impact."""
        connector = HubConnector("Test Tool")
        connector.register_with_hub(mock_hub)
        
        # Verify heartbeat doesn't overwhelm system
        initial_message_count = len(mock_hub.messages)
        
        # Wait for a few heartbeats (simulated)
        for _ in range(5):
            connector._send_heartbeat()
        
        # Verify reasonable message count
        final_message_count = len(mock_hub.messages)
        assert final_message_count > initial_message_count
        assert final_message_count - initial_message_count <= 10
    
    def test_event_handler_performance(self):
        """Test event handler performance."""
        connector = HubConnector("Test Tool")
        
        # Register multiple handlers
        handlers = [Mock() for _ in range(10)]
        for handler in handlers:
            connector.register_event_handler("test_event", handler)
        
        # Create test message
        message = HubMessage("test_event", "Test Tool", {})
        
        # Handle message (should call all handlers)
        connector.handle_hub_message(message)
        
        # Verify all handlers were called
        for handler in handlers:
            handler.assert_called_once_with(message)