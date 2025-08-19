"""
Richard's File Utilities Hub - Main application class.

This module provides the main hub interface that serves as the central
entry point for all file utility tools.
"""

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QObject
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QApplication = object
    QObject = object

from .log_manager import get_log_manager
from .config_manager import get_config_manager
from .core.error_handler import error_handler


class RFUHub(QObject if PYQT5_AVAILABLE else object):
    """
    Richard's File Utilities Hub - Main application class.
    
    This class serves as the central hub for all file utility tools,
    providing a unified interface and managing tool integration.
    """
    
    def __init__(self):
        """Initialize the RFU Hub."""
        if PYQT5_AVAILABLE:
            super().__init__()
        
        # Initialize core components
        self.logger = get_log_manager().get_logger('RFUHub')
        self.config = get_config_manager()
        
        # Hub state
        self.registered_tools = {}
        self.tool_status = {}
        self.message_queue = []
        
        self.logger.info("RFU Hub initialized")
        
        # Check for PyQt5 availability
        if not PYQT5_AVAILABLE:
            self.logger.warning(
                "PyQt5 not available - GUI functionality will be limited"
            )
    
    def show(self):
        """Show the hub interface."""
        if not PYQT5_AVAILABLE:
            self.logger.error(
                "Cannot show GUI - PyQt5 is not installed. "
                "Please install PyQt5 to use the graphical interface."
            )
            print("\n" + "="*60)
            print("RICHARD'S FILE UTILITIES - COMMAND LINE MODE")
            print("="*60)
            print("PyQt5 is not installed. GUI mode is not available.")
            print("\nTo install PyQt5, run:")
            print("  pip install PyQt5")
            print("\nAvailable tools (command line mode):")
            print("- Configuration management")
            print("- Logging system")
            print("- Error handling")
            print("\nFor full functionality, please install PyQt5.")
            print("="*60)
            return
        
        try:
            # Import and show the simple GUI hub (avoiding complex dependencies)
            from .simple_hub import SimpleRFUHub as GUIHub
            self.gui_hub = GUIHub()
            self.gui_hub.show()
            self.logger.info("GUI Hub displayed successfully")
        except Exception as e:
            self.logger.error(f"Failed to show GUI hub: {e}")
            print(f"Error displaying GUI: {e}")
            # Don't show error dialog that freezes the terminal
            return
    
    def register_tool(self, tool_name: str, tool_instance) -> bool:
        """
        Register a tool with the hub.
        
        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance
            
        Returns:
            bool: True if registration was successful
        """
        try:
            self.registered_tools[tool_name] = tool_instance
            self.tool_status[tool_name] = {
                'status': 'registered',
                'instance': tool_instance
            }
            self.logger.info(f"Tool registered: {tool_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the hub.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: True if unregistration was successful
        """
        try:
            if tool_name in self.registered_tools:
                del self.registered_tools[tool_name]
                del self.tool_status[tool_name]
                self.logger.info(f"Tool unregistered: {tool_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tool_status(self, tool_name: str = None):
        """
        Get status of tools.
        
        Args:
            tool_name: Specific tool name, or None for all tools
            
        Returns:
            Tool status information
        """
        if tool_name:
            return self.tool_status.get(tool_name, {})
        return self.tool_status.copy()
    
    def list_tools(self):
        """List all registered tools."""
        return list(self.registered_tools.keys())
    
    def close(self):
        """Close the hub and associated GUI."""
        try:
            if hasattr(self, 'gui_hub') and self.gui_hub:
                self.gui_hub.close()
                self.gui_hub = None
            self.logger.info("RFU Hub GUI closed")
        except Exception as e:
            self.logger.error(f"Error closing RFU Hub GUI: {e}")

    def shutdown(self):
        """Shutdown the hub and cleanup resources."""
        try:
            self.logger.info("Shutting down RFU Hub")
            
            # Unregister all tools
            for tool_name in list(self.registered_tools.keys()):
                self.unregister_tool(tool_name)
            
            # Clear message queue
            self.message_queue.clear()
            
            self.logger.info("RFU Hub shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during hub shutdown: {e}")


# Backward compatibility alias
class MyGUI(RFUHub):
    """Backward compatibility alias for RFUHub."""
    pass