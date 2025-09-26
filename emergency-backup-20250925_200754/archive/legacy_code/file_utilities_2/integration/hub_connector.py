"""
Hub Connector Integration Module

This module provides comprehensive integration between file_utilities_2 tools
and the central RFU Hub application, enabling bidirectional communication,
progress reporting, and shared resource management.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QApplication
from datetime import datetime
import threading


class HubCommunicationProtocol:
    """Protocol definitions for hub communication."""
    
    # Message types
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_ERROR = "tool_error"
    TOOL_PROGRESS = "tool_progress"
    TOOL_STATUS = "tool_status"
    TOOL_HEARTBEAT = "tool_heartbeat"
    
    # Resource types
    RESOURCE_CPU = "cpu"
    RESOURCE_MEMORY = "memory"
    RESOURCE_DISK = "disk"
    RESOURCE_NETWORK = "network"
    
    # Event types
    EVENT_LIFECYCLE = "lifecycle"
    EVENT_USER_ACTION = "user_action"
    EVENT_SYSTEM = "system"
    EVENT_ERROR = "error"


class HubMessage:
    """Standardized message format for hub communication."""
    
    def __init__(self, message_type: str, tool_name: str, 
                 data: Dict[str, Any] = None, timestamp: datetime = None):
        self.message_type = message_type
        self.tool_name = tool_name
        self.data = data or {}
        self.timestamp = timestamp or datetime.now()
        self.message_id = self._generate_message_id()
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type,
            'tool_name': self.tool_name,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HubMessage':
        """Create message from dictionary."""
        timestamp = datetime.fromisoformat(data['timestamp'])
        msg = cls(
            data['message_type'],
            data['tool_name'],
            data.get('data', {}),
            timestamp
        )
        msg.message_id = data['message_id']
        return msg


class SharedConfiguration:
    """Shared configuration management for hub integration."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        app_data = os.path.expanduser("~/.rfu_hub")
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, "hub_config.json")
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load hub config: {e}")
            self._config = {}
    
    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save hub config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
        self.save_config()
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get tool-specific configuration."""
        return self._config.get('tools', {}).get(tool_name, {})
    
    def set_tool_config(self, tool_name: str, config: Dict[str, Any]):
        """Set tool-specific configuration."""
        if 'tools' not in self._config:
            self._config['tools'] = {}
        self._config['tools'][tool_name] = config
        self.save_config()


class HubEventLogger:
    """Event logging system for hub integration."""
    
    def __init__(self, log_path: str = None):
        self.log_path = log_path or self._get_default_log_path()
        self._setup_logging()
    
    def _get_default_log_path(self) -> str:
        """Get default log file path."""
        app_data = os.path.expanduser("~/.rfu_hub")
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, "hub_events.log")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HubConnector')
    
    def log_event(self, event_type: str, tool_name: str, 
                  message: str, data: Dict[str, Any] = None):
        """Log hub event."""
        event_data = {
            'event_type': event_type,
            'tool_name': tool_name,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"[{event_type}] {tool_name}: {message}")
        
        # Also log to structured event file
        self._log_structured_event(event_data)
    
    def _log_structured_event(self, event_data: Dict[str, Any]):
        """Log structured event data."""
        try:
            events_file = self.log_path.replace('.log', '_events.jsonl')
            with open(events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to log structured event: {e}")


class HubConnector(QObject):
    """
    Main hub connector class providing comprehensive integration
    between tools and the central hub.
    """
    
    # Hub communication signals
    hub_message_received = pyqtSignal(object)  # HubMessage
    hub_connection_status = pyqtSignal(bool)   # connected/disconnected
    hub_resource_available = pyqtSignal(str, dict)  # resource_type, details
    hub_broadcast_received = pyqtSignal(str, dict)  # event_type, data
    
    # Tool registration signals
    tool_registered = pyqtSignal(str)          # tool_name
    tool_unregistered = pyqtSignal(str)        # tool_name
    tool_status_changed = pyqtSignal(str, str) # tool_name, status
    
    def __init__(self, tool_name: str, hub_instance=None):
        """
        Initialize hub connector.
        
        Args:
            tool_name: Name of the tool using this connector
            hub_instance: Reference to the hub instance (optional)
        """
        super().__init__()
        self.tool_name = tool_name
        self.hub_instance = hub_instance
        self.is_connected = False
        self.is_registered = False
        
        # Initialize components
        self.config = SharedConfiguration()
        self.logger = HubEventLogger()
        self.message_queue = []
        self._lock = threading.Lock()
        
        # Setup heartbeat timer
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.setInterval(30000)  # 30 seconds
        
        # Tool state tracking
        self.tool_state = {
            'status': 'idle',
            'progress': 0,
            'current_operation': None,
            'last_activity': datetime.now(),
            'resource_usage': {},
            'error_count': 0
        }
        
        # Event handlers
        self.event_handlers = {}
        
        self.logger.log_event(
            HubCommunicationProtocol.EVENT_LIFECYCLE,
            self.tool_name,
            "Hub connector initialized"
        )
    
    def register_with_hub(self, hub_instance=None) -> bool:
        """
        Register tool with central hub for communication.
        
        Args:
            hub_instance: Hub instance to register with
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if hub_instance:
                self.hub_instance = hub_instance
            
            if not self.hub_instance:
                # Try to find hub instance in QApplication
                app = QApplication.instance()
                if app:
                    for widget in app.allWidgets():
                        if hasattr(widget, '__class__') and 'Hub' in widget.__class__.__name__:
                            self.hub_instance = widget
                            break
            
            if self.hub_instance:
                # Register with hub
                if hasattr(self.hub_instance, 'register_tool'):
                    self.hub_instance.register_tool(self.tool_name, self)
                
                self.is_connected = True
                self.is_registered = True
                
                # Start heartbeat
                self.heartbeat_timer.start()
                
                # Send registration message
                self._send_message(
                    HubCommunicationProtocol.TOOL_STARTED,
                    {'registration_time': datetime.now().isoformat()}
                )
                
                self.tool_registered.emit(self.tool_name)
                self.hub_connection_status.emit(True)
                
                self.logger.log_event(
                    HubCommunicationProtocol.EVENT_LIFECYCLE,
                    self.tool_name,
                    "Successfully registered with hub"
                )
                
                return True
            else:
                self.logger.log_event(
                    HubCommunicationProtocol.EVENT_ERROR,
                    self.tool_name,
                    "Hub instance not found for registration"
                )
                return False
                
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to register with hub: {e}"
            )
            return False
    
    def unregister_from_hub(self):
        """Unregister tool from hub."""
        try:
            if self.is_registered and self.hub_instance:
                # Send completion message
                self._send_message(
                    HubCommunicationProtocol.TOOL_COMPLETED,
                    {
                        'unregistration_time': datetime.now().isoformat(),
                        'final_state': self.tool_state.copy()
                    }
                )
                
                # Unregister from hub
                if hasattr(self.hub_instance, 'unregister_tool'):
                    self.hub_instance.unregister_tool(self.tool_name)
                
                # Stop heartbeat
                self.heartbeat_timer.stop()
                
                self.is_connected = False
                self.is_registered = False
                
                self.tool_unregistered.emit(self.tool_name)
                self.hub_connection_status.emit(False)
                
                self.logger.log_event(
                    HubCommunicationProtocol.EVENT_LIFECYCLE,
                    self.tool_name,
                    "Successfully unregistered from hub"
                )
                
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to unregister from hub: {e}"
            )
    
    def report_status_to_hub(self, status: str, details: Dict[str, Any] = None):
        """
        Report current status to hub.
        
        Args:
            status: Current tool status
            details: Additional status details
        """
        try:
            self.tool_state['status'] = status
            self.tool_state['last_activity'] = datetime.now()
            
            if details:
                self.tool_state.update(details)
            
            self._send_message(
                HubCommunicationProtocol.TOOL_STATUS,
                {
                    'status': status,
                    'details': details or {},
                    'tool_state': self.tool_state.copy()
                }
            )
            
            self.tool_status_changed.emit(self.tool_name, status)
            
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to report status: {e}"
            )
    
    def report_progress_to_hub(self, percentage: int, message: str = ""):
        """
        Report progress to hub's central progress tracking system.
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        try:
            self.tool_state['progress'] = percentage
            self.tool_state['current_operation'] = message
            self.tool_state['last_activity'] = datetime.now()
            
            self._send_message(
                HubCommunicationProtocol.TOOL_PROGRESS,
                {
                    'percentage': percentage,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Update hub status if available
            if self.hub_instance and hasattr(self.hub_instance, 'update_tool_progress'):
                self.hub_instance.update_tool_progress(
                    self.tool_name, percentage, message
                )
                
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to report progress: {e}"
            )
    
    def report_error_to_hub(self, error_message: str, error_details: Dict[str, Any] = None):
        """
        Report error to hub's error tracking system.
        
        Args:
            error_message: Error message
            error_details: Additional error details
        """
        try:
            self.tool_state['error_count'] += 1
            self.tool_state['last_error'] = {
                'message': error_message,
                'details': error_details or {},
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_message(
                HubCommunicationProtocol.TOOL_ERROR,
                {
                    'error_message': error_message,
                    'error_details': error_details or {},
                    'error_count': self.tool_state['error_count']
                }
            )
            
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                error_message,
                error_details
            )
            
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to report error: {e}"
            )
    
    def request_hub_resources(self, resource_type: str, requirements: Dict[str, Any] = None) -> bool:
        """
        Request shared resources from hub.
        
        Args:
            resource_type: Type of resource requested
            requirements: Resource requirements
            
        Returns:
            True if resource granted, False otherwise
        """
        try:
            if not self.is_connected:
                return False
            
            # Check with hub for resource availability
            if self.hub_instance and hasattr(self.hub_instance, 'request_resource'):
                granted = self.hub_instance.request_resource(
                    self.tool_name, resource_type, requirements or {}
                )
                
                if granted:
                    self.hub_resource_available.emit(resource_type, requirements or {})
                    
                    self.logger.log_event(
                        HubCommunicationProtocol.EVENT_SYSTEM,
                        self.tool_name,
                        f"Resource granted: {resource_type}",
                        requirements
                    )
                
                return granted
            
            return True  # Default to granted if hub doesn't support resource management
            
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to request resources: {e}"
            )
            return False
    
    def broadcast_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Broadcast event to other tools through hub.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        try:
            if self.hub_instance and hasattr(self.hub_instance, 'broadcast_event'):
                self.hub_instance.broadcast_event(
                    self.tool_name, event_type, event_data
                )
                
                self.logger.log_event(
                    HubCommunicationProtocol.EVENT_SYSTEM,
                    self.tool_name,
                    f"Event broadcasted: {event_type}",
                    event_data
                )
                
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to broadcast event: {e}"
            )
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register handler for specific event types.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def handle_hub_message(self, message: HubMessage):
        """
        Handle incoming message from hub.
        
        Args:
            message: Hub message to handle
        """
        try:
            self.hub_message_received.emit(message)
            
            # Call registered event handlers
            if message.message_type in self.event_handlers:
                for handler in self.event_handlers[message.message_type]:
                    try:
                        handler(message)
                    except Exception as e:
                        self.logger.log_event(
                            HubCommunicationProtocol.EVENT_ERROR,
                            self.tool_name,
                            f"Event handler error: {e}"
                        )
                        
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to handle hub message: {e}"
            )
    
    def get_tool_config(self) -> Dict[str, Any]:
        """Get tool-specific configuration."""
        return self.config.get_tool_config(self.tool_name)
    
    def set_tool_config(self, config: Dict[str, Any]):
        """Set tool-specific configuration."""
        self.config.set_tool_config(self.tool_name, config)
    
    def _send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message to hub."""
        try:
            with self._lock:
                message = HubMessage(message_type, self.tool_name, data)
                
                if self.is_connected and self.hub_instance:
                    if hasattr(self.hub_instance, 'receive_message'):
                        self.hub_instance.receive_message(message)
                    else:
                        # Queue message for later delivery
                        self.message_queue.append(message)
                else:
                    # Queue message for later delivery
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to send message: {e}"
            )
    
    def _send_heartbeat(self):
        """Send heartbeat to hub."""
        try:
            self._send_message(
                HubCommunicationProtocol.TOOL_HEARTBEAT,
                {
                    'timestamp': datetime.now().isoformat(),
                    'tool_state': self.tool_state.copy()
                }
            )
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to send heartbeat: {e}"
            )
    
    def _flush_message_queue(self):
        """Flush queued messages to hub."""
        try:
            with self._lock:
                if self.is_connected and self.hub_instance and self.message_queue:
                    for message in self.message_queue:
                        if hasattr(self.hub_instance, 'receive_message'):
                            self.hub_instance.receive_message(message)
                    self.message_queue.clear()
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to flush message queue: {e}"
            )
    
    def cleanup(self):
        """Cleanup hub connector resources."""
        try:
            self.unregister_from_hub()
            self.heartbeat_timer.stop()
            
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_LIFECYCLE,
                self.tool_name,
                "Hub connector cleaned up"
            )
            
        except Exception as e:
            self.logger.log_event(
                HubCommunicationProtocol.EVENT_ERROR,
                self.tool_name,
                f"Failed to cleanup hub connector: {e}"
            )


class HubIntegratedTool(QObject):
    """
    Base class for tools that integrate with the hub.
    Provides common hub integration functionality.
    """
    
    # Hub integration signals
    tool_started = pyqtSignal(str)              # tool name
    tool_completed = pyqtSignal(str, dict)      # tool name, results
    tool_error = pyqtSignal(str, str)           # tool name, error message
    tool_progress = pyqtSignal(str, int, str)   # tool name, percentage, message
    tool_status_changed = pyqtSignal(str, str)  # tool name, status
    
    def __init__(self, tool_name: str):
        """
        Initialize hub-integrated tool.
        
        Args:
            tool_name: Name of the tool
        """
        super().__init__()
        self.tool_name = tool_name
        self.hub_connector = HubConnector(tool_name)
        
        # Connect hub connector signals to tool signals
        self.hub_connector.tool_status_changed.connect(
            lambda name, status: self.tool_status_changed.emit(name, status)
        )
        
        # Auto-register with hub on initialization
        self.hub_connector.register_with_hub()
    
    def report_tool_started(self, details: Dict[str, Any] = None):
        """Report that tool has started."""
        self.hub_connector.report_status_to_hub("started", details)
        self.tool_started.emit(self.tool_name)
    
    def report_tool_completed(self, results: Dict[str, Any] = None):
        """Report that tool has completed."""
        self.hub_connector.report_status_to_hub("completed", {"results": results})
        self.tool_completed.emit(self.tool_name, results or {})
    
    def report_tool_error(self, error_message: str, error_details: Dict[str, Any] = None):
        """Report tool error."""
        self.hub_connector.report_error_to_hub(error_message, error_details)
        self.tool_error.emit(self.tool_name, error_message)
    
    def report_tool_progress(self, percentage: int, message: str = ""):
        """Report tool progress."""
        self.hub_connector.report_progress_to_hub(percentage, message)
        self.tool_progress.emit(self.tool_name, percentage, message)
    
    def cleanup_hub_integration(self):
        """Cleanup hub integration."""
        self.hub_connector.cleanup()