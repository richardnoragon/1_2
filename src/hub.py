"""
Richard's File Utilities Hub - Unified Main Application Interface

This module provides the main hub interface that serves as the central
entry point for all file utility tools. This is a consolidated version
that combines the best features from the previous hub implementations.

Features:
- Professional tab-based interface with organized tool categories
- Comprehensive menu system with keyboard shortcuts
- Graceful fallback when dependencies are missing
- Tool registration and status management
- Professional styling and responsive layout
- Error handling and logging integration

Consolidated from:
- simple_hub.py (primary foundation - most functional)
- hub.py (hub integration features)
- rfuhub.py (core functionality and fallback mechanisms)
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core PyQt5 imports with graceful fallback
try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QIcon
    from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,
                                 QLabel, QMainWindow, QMessageBox, QPushButton,
                                 QSizePolicy, QStatusBar, QTabWidget,
                                 QTextEdit, QVBoxLayout, QWidget)
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QMainWindow = object
    QWidget = object
    QObject = object
    pyqtSignal = None

# Core application imports with fallback for direct execution
try:
    from .config_manager import get_config_manager
    from .core.error_handler import error_handler
    from .log_manager import get_log_manager
except ImportError:
    # Fallback for direct execution
    try:
        from config_manager import get_config_manager
        from core.error_handler import error_handler
        from log_manager import get_log_manager
    except ImportError:
        # Create minimal fallbacks
        def get_log_manager():
            import logging
            return logging.getLogger(__name__)
        
        def get_config_manager():
            class MockConfig:
                def get(self, key, default=None):
                    return default
            return MockConfig()
        
        def error_handler(func):
            return func

# Import constants for string literals with fallback
try:
    from core.constants import (ANALYSIS_TOOLS, PDF_TOOLS, PRIVACY_TOOLS,
                                SECTION_MARGIN_STYLE, SEGOE_UI_FONT,
                                SETTINGS_TOOLS, SUBTITLE_STYLE_COLOR,
                                TITLE_STYLE_COLOR, UTILITIES_TOOLS)
except ImportError:
    # Define fallback constants
    PDF_TOOLS = "PDF Tools"
    SEGOE_UI_FONT = "Segoe UI"
    TITLE_STYLE_COLOR = "#2c3e50"
    SUBTITLE_STYLE_COLOR = "#34495e"
    SECTION_MARGIN_STYLE = "margin: 10px;"
    PRIVACY_TOOLS = "Privacy Tools"
    ANALYSIS_TOOLS = "Analysis Tools"
    UTILITIES_TOOLS = "Utilities Tools"
    SETTINGS_TOOLS = "Settings Tools"

# CSS Color Constants for Professional Styling
PRIMARY_BLUE = "#3498db"
DARK_BLUE = "#2980b9"
DARKER_BLUE = "#1f618d"
LIGHT_BLUE = "#5dade2"
LIGHT_GRAY = "#ecf0f1"
MEDIUM_GRAY = "#bdc3c7"
DARK_GRAY = "#95a5a6"
DARKER_GRAY = "#7f8c8d"
TEXT_DARK = "#2c3e50"
WHITE = "#ffffff"
SUCCESS_GREEN = "#27ae60"
WARNING_ORANGE = "#f39c12"
ERROR_RED = "#e74c3c"

# CSS Style Constants
TITLE_HEADER_STYLE = f"color: {TEXT_DARK}; margin: 10px 0px;"


class UtilityWindow(QMainWindow if PYQT5_AVAILABLE else object):
    """Wrapper class to ensure utilities maintain the main window's menu bar."""
    
    def __init__(self, parent_hub, utility_widget, title="Utility"):
        if not PYQT5_AVAILABLE:
            return
            
        super().__init__(parent_hub)
        self.parent_hub = parent_hub
        self.setWindowTitle(f"Richard's File Utilities - {title}")
        self.resize(900, 700)
        self.move(150, 150)
        # Ensure maximize button is enabled
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Use the same menu bar as the parent hub
        if hasattr(parent_hub, 'menuBar') and parent_hub.menuBar():
            self._clone_menu_bar(parent_hub.menuBar())
        
        # Set the utility as central widget
        self.setCentralWidget(utility_widget)
        
        # Create status bar
        status_bar = self.statusBar()
        status_bar.showMessage(f"{title} ready")
        
        # Connect utility status signals if available
        if hasattr(utility_widget, 'status_changed'):
            utility_widget.status_changed.connect(status_bar.showMessage)
    
    def _clone_menu_bar(self, source_menu_bar):
        """Clone menu bar from source to maintain consistency."""
        try:
            # Use the same menu manager pattern
            if hasattr(self.parent_hub, 'menu_manager'):
                from .simple_menu_manager import SimpleMenuManager
                self.menu_manager = SimpleMenuManager(self)
                self.menu_manager.create_menubar()
                self._register_delegated_callbacks()
        except Exception as e:
            print(f"Warning: Could not clone menu bar: {e}")
    
    def _register_delegated_callbacks(self):
        """Register menu callbacks that delegate to parent hub."""
        if not hasattr(self, 'menu_manager') or not hasattr(self.parent_hub, 'menu_manager'):
            return
        
        # Get all callbacks from parent and delegate them
        parent_callbacks = getattr(self.parent_hub.menu_manager, 'callbacks', {})
        for callback_name, callback_func in parent_callbacks.items():
            self.menu_manager.register_callback(callback_name, callback_func)
    
    def closeEvent(self, event):
        """Handle close event to clean up properly."""
        # Hide instead of closing to preserve the utility
        self.hide()
        if PYQT5_AVAILABLE:
            event.ignore()


class RFUHub(QMainWindow if PYQT5_AVAILABLE else QObject):
    """
    Richard's File Utilities Hub - Unified Main Application Interface
    
    This class combines the best features from all previous hub implementations:
    - Professional GUI from simple_hub.py
    - Hub integration features from hub.py  
    - Core functionality and fallbacks from rfuhub.py
    """
    
    # Hub integration signals (from hub.py)
    if PYQT5_AVAILABLE:
        tool_registered = pyqtSignal(str, object)
        tool_unregistered = pyqtSignal(str)
        tool_progress_updated = pyqtSignal(str, int, str)
        tool_status_changed = pyqtSignal(str, str)
        hub_event_broadcast = pyqtSignal(str, str, dict)
    
    def __init__(self):
        """Initialize the unified RFU Hub."""
        if PYQT5_AVAILABLE:
            super().__init__()
        
        # Initialize core components
        self.logger = get_log_manager().get_logger('RFUHub')
        self.config = get_config_manager()
        
        self.logger.info("RFU Hub initializing...")
        
        # Hub state management (from hub.py and rfuhub.py)
        self.registered_tools = {}
        self.tool_status = {}
        self.message_queue = []
        self.resource_manager = {
            'cpu': {'available': True, 'allocated_to': None},
            'memory': {'available': True, 'allocated_to': None},
            'disk': {'available': True, 'allocated_to': None}
        }
        
        # Check for PyQt5 availability (from rfuhub.py)
        if not PYQT5_AVAILABLE:
            self.logger.warning("PyQt5 not available - GUI functionality will be limited")
            return
        
        # Initialize GUI components (from simple_hub.py)
        self._setup_gui()
        self._setup_hub_integration()
        
        self.logger.info("RFU Hub initialized successfully")
    
    def _setup_gui(self):
        """Setup the GUI interface (adapted from simple_hub.py)."""
        if not PYQT5_AVAILABLE:
            return
        
        # Initialize menu system
        from .simple_menu_manager import SimpleMenuManager
        self.menu_manager = SimpleMenuManager(self)
        self.menu_manager.create_menubar()
        self._setup_menu_callbacks()
        self.logger.info("Menu system initialized")
        
        # Set up the window with proper maximize support
        self.setWindowTitle("Richard's File Utilities - Main Hub")
        self.resize(800, 600)
        self.move(100, 100)
        self.setWindowIcon(self._get_application_icon())
        # Ensure window can be maximized properly
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title with professional styling
        title_label = QLabel("Richard's File Utilities")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                margin: 15px 0px;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                border-radius: 8px;
                border: 1px solid {MEDIUM_GRAY};
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Create tab widget with professional styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {MEDIUM_GRAY};
                background-color: {WHITE};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {LIGHT_GRAY}, stop:1 {MEDIUM_GRAY});
                border: 1px solid {DARK_GRAY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                border-bottom-color: {WHITE};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {LIGHT_BLUE}, stop:1 {PRIMARY_BLUE});
                color: white;
            }}
        """)
        main_layout.addWidget(self.tab_widget)
        
        # Create all tabs (from simple_hub.py)
        self.create_analysis_tab()
        self.create_file_operations_tab()
        self.create_metadata_tab()
        self.create_network_tab()
        self.create_pdf_tools_tab()
        self.create_privacy_tab()
        self.create_security_tab()
        self.create_system_tab()
        self.create_logs_tab()
        
        # Status bar with professional styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {LIGHT_GRAY};
                border-top: 1px solid {MEDIUM_GRAY};
                padding: 5px;
            }}
        """)
        self.status_bar.showMessage("RFU Hub initialized successfully")
    
    def _setup_hub_integration(self):
        """Setup hub integration components (from hub.py)."""
        if not PYQT5_AVAILABLE:
            return
        
        # Connect internal signals
        if hasattr(self, 'tool_registered'):
            self.tool_registered.connect(self._on_tool_registered)
            self.tool_unregistered.connect(self._on_tool_unregistered)
            self.tool_progress_updated.connect(self._on_tool_progress_updated)
            self.tool_status_changed.connect(self._on_tool_status_changed)
            self.hub_event_broadcast.connect(self._on_hub_event_broadcast)
    
    def _get_application_icon(self):
        """Get application icon with fallback."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        except Exception:
            pass
        return QIcon()  # Return empty icon as fallback
    
    def show(self):
        """Show the hub interface with graceful fallback."""
        if not PYQT5_AVAILABLE:
            self.logger.error(
                "Cannot show GUI - PyQt5 is not installed. "
                "Please install PyQt5 to use the graphical interface."
            )
            self._show_command_line_interface()
            return
        
        try:
            super().show()
            self.logger.info("GUI Hub displayed successfully")
        except Exception as e:
            self.logger.error(f"Failed to show GUI hub: {e}")
            self._show_command_line_interface()
    
    def _show_command_line_interface(self):
        """Show command line interface when GUI is not available (from rfuhub.py)."""
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
    
    # Menu callback implementations (from simple_hub.py)
    def _setup_menu_callbacks(self):
        """Setup menu callbacks for the RFU Hub."""
        if not self.menu_manager:
            return
        
        # File menu callbacks
        self.menu_manager.register_callback('new_project', self.new_project)
        self.menu_manager.register_callback('open_file', self.open_file)
        self.menu_manager.register_callback('save_file', self.save_file)
        self.menu_manager.register_callback('save_as_file', self.save_as_file)
        self.menu_manager.register_callback('export_data', self.export_data)
        self.menu_manager.register_callback('import_data', self.import_data)
        self.menu_manager.register_callback('print_document', self.print_document)
        self.menu_manager.register_callback('show_preferences', self.show_preferences)
        
        # Edit menu callbacks
        self.menu_manager.register_callback('undo', self.undo)
        self.menu_manager.register_callback('redo', self.redo)
        self.menu_manager.register_callback('cut', self.cut)
        self.menu_manager.register_callback('copy', self.copy)
        self.menu_manager.register_callback('paste', self.paste)
        self.menu_manager.register_callback('select_all', self.select_all)
        self.menu_manager.register_callback('find', self.find)
        self.menu_manager.register_callback('replace', self.replace)
        
        # View menu callbacks
        self.menu_manager.register_callback('zoom_in', self.zoom_in)
        self.menu_manager.register_callback('zoom_out', self.zoom_out)
        self.menu_manager.register_callback('zoom_reset', self.zoom_reset)
        self.menu_manager.register_callback('refresh', self.refresh)
        
        # Tools menu callbacks
        self.menu_manager.register_callback('show_options', self.show_options)
        self.menu_manager.register_callback('show_performance', self.show_performance)
        
        self.logger.info("Menu callbacks registered")
    
    def _create_styled_tool_button(self, text, tooltip, callback, primary=True):
        """Create a styled tool button with organized layout (from simple_hub.py)."""
        if not PYQT5_AVAILABLE:
            return None
            
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setMinimumSize(180, 70)
        button.setMaximumSize(200, 80)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if primary:
            button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {PRIMARY_BLUE}, stop:1 {DARK_BLUE});
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {LIGHT_BLUE}, stop:1 {PRIMARY_BLUE});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {DARK_BLUE}, stop:1 {DARKER_BLUE});
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {LIGHT_GRAY}, stop:1 {MEDIUM_GRAY});
                    color: {TEXT_DARK};
                    border: 1px solid {DARK_GRAY};
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                    border: 1px solid {DARKER_GRAY};
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {MEDIUM_GRAY}, stop:1 {DARK_GRAY});
                }}
            """)
        
        return button
    
    # Hub Integration Methods (from hub.py)
    def register_tool(self, tool_name: str, tool_instance) -> bool:
        """Register a tool with the hub."""
        try:
            if tool_name in self.registered_tools:
                self.registered_tools[tool_name] = tool_instance
            else:
                self.registered_tools[tool_name] = tool_instance
                self.tool_status[tool_name] = {
                    'status': 'registered',
                    'last_activity': datetime.now(),
                    'progress': 0,
                    'current_operation': None
                }
            
            if PYQT5_AVAILABLE and hasattr(self, 'tool_registered'):
                self.tool_registered.emit(tool_name, tool_instance)
            
            self._update_status_bar(f"Tool registered: {tool_name}")
            self.logger.info(f"Tool registered: {tool_name}")
            return True
            
        except Exception as e:
            self._update_status_bar(f"Failed to register tool {tool_name}: {e}")
            self.logger.error(f"Failed to register tool {tool_name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the hub."""
        try:
            if tool_name in self.registered_tools:
                del self.registered_tools[tool_name]
                if tool_name in self.tool_status:
                    del self.tool_status[tool_name]
                
                self._release_tool_resources(tool_name)
                
                if PYQT5_AVAILABLE and hasattr(self, 'tool_unregistered'):
                    self.tool_unregistered.emit(tool_name)
                
                self._update_status_bar(f"Tool unregistered: {tool_name}")
                self.logger.info(f"Tool unregistered: {tool_name}")
                return True
            return False
            
        except Exception as e:
            self._update_status_bar(f"Failed to unregister tool {tool_name}: {e}")
            self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def update_tool_progress(self, tool_name: str, percentage: int, message: str = ""):
        """Update tool progress in hub."""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update({
                'progress': percentage,
                'current_operation': message,
                'last_activity': datetime.now()
            })
            
            if PYQT5_AVAILABLE and hasattr(self, 'tool_progress_updated'):
                self.tool_progress_updated.emit(tool_name, percentage, message)
            
            if percentage < 100:
                self._update_status_bar(f"{tool_name}: {message} ({percentage}%)")
            else:
                self._update_status_bar(f"{tool_name}: Completed")
    
    def _release_tool_resources(self, tool_name: str):
        """Release all resources allocated to a tool."""
        for resource_type, resource_info in self.resource_manager.items():
            if resource_info.get('allocated_to') == tool_name:
                resource_info['available'] = True
                resource_info['allocated_to'] = None
                resource_info.pop('allocated_at', None)
    
    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        if PYQT5_AVAILABLE and hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 5000)
    
    # Signal Handlers (from hub.py)
    def _on_tool_registered(self, tool_name: str, tool_instance):
        """Handle tool registration event."""
        pass  # Additional processing if needed
    
    def _on_tool_unregistered(self, tool_name: str):
        """Handle tool unregistration event."""
        pass  # Additional processing if needed
    
    def _on_tool_progress_updated(self, tool_name: str, percentage: int, message: str):
        """Handle tool progress update event."""
        pass  # Additional processing if needed
    
    def _on_tool_status_changed(self, tool_name: str, status: str):
        """Handle tool status change event."""
        pass  # Additional processing if needed
    
    def _on_hub_event_broadcast(self, sender: str, event_type: str, data: Dict):
        """Handle hub event broadcast."""
        pass  # Additional processing if needed
    
    # Menu Callback Implementations
    def new_project(self):
        """Create a new project."""
        self._update_status_bar("New Project - Feature coming soon...")
        self.logger.info("New Project requested")
    
    def open_file(self):
        """Open a file."""
        self._update_status_bar("Open File - Feature coming soon...")
        self.logger.info("Open File requested")
    
    def save_file(self):
        """Save current work."""
        self._update_status_bar("Save File - Feature coming soon...")
        self.logger.info("Save File requested")
    
    def save_as_file(self):
        """Save with new name."""
        self._update_status_bar("Save As - Feature coming soon...")
        self.logger.info("Save As requested")
    
    def export_data(self):
        """Export data."""
        self._update_status_bar("Export Data - Feature coming soon...")
        self.logger.info("Export Data requested")
    
    def import_data(self):
        """Import data."""
        self._update_status_bar("Import Data - Feature coming soon...")
        self.logger.info("Import Data requested")
    
    def launch_tool(self, tool_name: str, *args, **kwargs):
        """
        Generic tool launcher interface for enterprise integration testing.
        
        This method provides a unified interface for launching any tool in the RFU suite.
        It maps tool names to their corresponding open_ methods.
        
        Args:
            tool_name (str): Name of the tool to launch
            *args: Additional arguments to pass to the tool
            **kwargs: Additional keyword arguments to pass to the tool
            
        Returns:
            bool: True if tool launched successfully, False otherwise
        """
        try:
            # Normalize tool name to method name
            method_name = f"open_{tool_name.lower().replace(' ', '_').replace('-', '_')}"
            
            # Check if method exists
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    method(*args, **kwargs)
                    self.logger.info(f"Successfully launched tool: {tool_name}")
                    return True
                else:
                    self.logger.error(f"Tool method {method_name} is not callable")
                    return False
            else:
                # Try alternative naming patterns
                alternative_names = [
                    f"open_{tool_name.lower()}",
                    f"start_{tool_name.lower()}",
                    f"show_{tool_name.lower()}",
                    tool_name.lower().replace(' ', '_')
                ]
                
                for alt_name in alternative_names:
                    if hasattr(self, alt_name):
                        method = getattr(self, alt_name)
                        if callable(method):
                            method(*args, **kwargs)
                            self.logger.info(f"Successfully launched tool: {tool_name} via {alt_name}")
                            return True
                
                self.logger.error(f"Tool method not found for: {tool_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching tool {tool_name}: {str(e)}")
            return False
    
    def get_available_tools(self):
        """
        Get list of available tools for enterprise testing.
        
        Returns:
            list: List of available tool names
        """
        import inspect
        tools = []
        
        # Find all open_ methods
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('open_') and name != 'open_file':
                tool_name = name[5:].replace('_', ' ').title()
                tools.append(tool_name)
        
        return sorted(tools)
    
    def print_document(self):
        """Print current document."""
        self._update_status_bar("Print Document - Feature coming soon...")
        self.logger.info("Print Document requested")
    
    def show_preferences(self):
        """Show preferences dialog."""
        self._update_status_bar("Preferences - Feature coming soon...")
        self.logger.info("Preferences requested")
    
    def undo(self):
        """Undo last action."""
        self._update_status_bar("Undo - Feature coming soon...")
        self.logger.info("Undo requested")
    
    def redo(self):
        """Redo last action."""
        self._update_status_bar("Redo - Feature coming soon...")
        self.logger.info("Redo requested")
    
    def cut(self):
        """Cut to clipboard."""
        self._update_status_bar("Cut - Feature coming soon...")
        self.logger.info("Cut requested")
    
    def copy(self):
        """Copy to clipboard."""
        self._update_status_bar("Copy - Feature coming soon...")
        self.logger.info("Copy requested")
    
    def paste(self):
        """Paste from clipboard."""
        self._update_status_bar("Paste - Feature coming soon...")
        self.logger.info("Paste requested")
    
    def select_all(self):
        """Select all items."""
        self._update_status_bar("Select All - Feature coming soon...")
        self.logger.info("Select All requested")
    
    def find(self):
        """Find text or items."""
        self._update_status_bar("Find - Feature coming soon...")
        self.logger.info("Find requested")
    
    def replace(self):
        """Find and replace."""
        self._update_status_bar("Replace - Feature coming soon...")
        self.logger.info("Replace requested")
    
    def zoom_in(self):
        """Increase zoom level."""
        self._update_status_bar("Zoom In - Feature coming soon...")
        self.logger.info("Zoom In requested")
    
    def zoom_out(self):
        """Decrease zoom level."""
        self._update_status_bar("Zoom Out - Feature coming soon...")
        self.logger.info("Zoom Out requested")
    
    def zoom_reset(self):
        """Reset zoom to default."""
        self._update_status_bar("Zoom Reset - Feature coming soon...")
        self.logger.info("Zoom Reset requested")
    
    def refresh(self):
        """Refresh current view."""
        if hasattr(self, 'load_recent_logs'):
            self.load_recent_logs()
        self._update_status_bar("View refreshed")
        self.logger.info("Refresh requested")
    
    def show_options(self):
        """Show tool options."""
        self._update_status_bar("Options - Feature coming soon...")
        self.logger.info("Options requested")
    
    def show_documentation(self):
        """Show documentation."""
        self._update_status_bar("Documentation - Feature coming soon...")
        self.logger.info("Documentation requested")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        self._update_status_bar("Shortcuts - Feature coming soon...")
        self.logger.info("Shortcuts requested")
    
    def show_about(self):
        """Show about dialog."""
        self._update_status_bar("RFU Hub - File Processing and Utility Tools")
        self.logger.info("About dialog requested")
    
    # Tab Creation Methods
    def _create_main_tab(self, tab_widget):
        """Create the main control tab."""
        main_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(main_tab)
        
        # Welcome section
        welcome_label = QtWidgets.QLabel("<h2>Welcome to RFU Hub</h2>")
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Description
        desc_label = QtWidgets.QLabel(
            "<p>RFU Hub is your comprehensive file processing and utility toolkit. "
            "Use the tabs above to access various tools and utilities.</p>"
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Quick action buttons
        quick_actions_group = QtWidgets.QGroupBox("Quick Actions")
        quick_layout = QtWidgets.QGridLayout(quick_actions_group)
        
        # File operations
        file_catalog_btn = QtWidgets.QPushButton("📁 File Catalog")
        file_catalog_btn.setMinimumHeight(40)
        file_catalog_btn.clicked.connect(self.open_file_catalog)
        quick_layout.addWidget(file_catalog_btn, 0, 0)
        
        # Network tools
        network_btn = QtWidgets.QPushButton("🌐 Network Tools")
        network_btn.setMinimumHeight(40)
        network_btn.clicked.connect(self.open_network_tools)
        quick_layout.addWidget(network_btn, 0, 1)
        
        # Security tools
        security_btn = QtWidgets.QPushButton("🔒 Security Tools")
        security_btn.setMinimumHeight(40)
        security_btn.clicked.connect(self.open_security_tools)
        quick_layout.addWidget(security_btn, 1, 0)
        
        # System tools
        system_btn = QtWidgets.QPushButton("⚙️ System Tools")
        system_btn.setMinimumHeight(40)
        system_btn.clicked.connect(self.open_system_tools)
        quick_layout.addWidget(system_btn, 1, 1)
        
        layout.addWidget(quick_actions_group)
        layout.addStretch()
        
        return main_tab
    
    def _create_file_operations_tab(self, tab_widget):
        """Create the file operations tab."""
        file_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(file_tab)
        
        # File operations group
        file_ops_group = QtWidgets.QGroupBox("File Operations")
        file_ops_layout = QtWidgets.QGridLayout(file_ops_group)
        
        # File touch tool
        touch_btn = QtWidgets.QPushButton("📝 File Touch")
        touch_btn.setToolTip("Create or update file timestamps")
        touch_btn.clicked.connect(self.open_file_touch)
        file_ops_layout.addWidget(touch_btn, 0, 0)
        
        # File splitter
        splitter_btn = QtWidgets.QPushButton("✂️ File Splitter")
        splitter_btn.setToolTip("Split large files into smaller chunks")
        splitter_btn.clicked.connect(self.open_file_splitter)
        file_ops_layout.addWidget(splitter_btn, 0, 1)
        
        # Secure delete
        secure_delete_btn = QtWidgets.QPushButton("🗑️ Secure Delete")
        secure_delete_btn.setToolTip("Securely delete files")
        secure_delete_btn.clicked.connect(self.open_secure_delete)
        file_ops_layout.addWidget(secure_delete_btn, 0, 2)
        
        # Compression tools
        compress_btn = QtWidgets.QPushButton("📦 Compression")
        compress_btn.setToolTip("Compress and decompress files")
        compress_btn.clicked.connect(self.open_compression_tools)
        file_ops_layout.addWidget(compress_btn, 1, 0)
        
        # File catalog
        catalog_btn = QtWidgets.QPushButton("📋 File Catalog")
        catalog_btn.setToolTip("Generate detailed file catalogs")
        catalog_btn.clicked.connect(self.open_file_catalog)
        file_ops_layout.addWidget(catalog_btn, 1, 1)
        
        # Duplicate finder
        duplicate_btn = QtWidgets.QPushButton("🔍 Duplicate Finder")
        duplicate_btn.setToolTip("Find and manage duplicate files")
        duplicate_btn.clicked.connect(self.open_duplicate_finder)
        file_ops_layout.addWidget(duplicate_btn, 1, 2)
        
        layout.addWidget(file_ops_group)
        
        # Metadata tools group
        metadata_group = QtWidgets.QGroupBox("Metadata Tools")
        metadata_layout = QtWidgets.QGridLayout(metadata_group)
        
        # Image metadata
        image_meta_btn = QtWidgets.QPushButton("🖼️ Image Metadata")
        image_meta_btn.setToolTip("Edit image metadata and EXIF data")
        image_meta_btn.clicked.connect(self.open_image_metadata)
        metadata_layout.addWidget(image_meta_btn, 0, 0)
        
        # Office metadata
        office_meta_btn = QtWidgets.QPushButton("📄 Office Metadata")
        office_meta_btn.setToolTip("Edit office document metadata")
        office_meta_btn.clicked.connect(self.open_office_metadata)
        metadata_layout.addWidget(office_meta_btn, 0, 1)
        
        # PDF tools
        pdf_btn = QtWidgets.QPushButton("📑 PDF Tools")
        pdf_btn.setToolTip("PDF processing and metadata tools")
        pdf_btn.clicked.connect(self.open_pdf_tools)
        metadata_layout.addWidget(pdf_btn, 0, 2)
        
        layout.addWidget(metadata_group)
        layout.addStretch()
        
    def _create_network_tools_tab(self, tab_widget):
        """Create the network tools tab."""
        network_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(network_tab)
        
        # Network operations group
        network_group = QtWidgets.QGroupBox("Network Operations")
        network_layout = QtWidgets.QGridLayout(network_group)
        
        # Network transfer
        transfer_btn = QtWidgets.QPushButton("🚀 Network Transfer")
        transfer_btn.setToolTip("Transfer files over network")
        transfer_btn.clicked.connect(self.open_network_transfer)
        network_layout.addWidget(transfer_btn, 0, 0)
        
        # Network scan
        scan_btn = QtWidgets.QPushButton("🔍 Network Scan")
        scan_btn.setToolTip("Scan network for devices and services")
        scan_btn.clicked.connect(self.open_network_scan)
        network_layout.addWidget(scan_btn, 0, 1)
        
        # Port scanner
        port_btn = QtWidgets.QPushButton("🔌 Port Scanner")
        port_btn.setToolTip("Scan for open ports on network hosts")
        port_btn.clicked.connect(self.open_port_scanner)
        network_layout.addWidget(port_btn, 0, 2)
        
        # Network monitor
        monitor_btn = QtWidgets.QPushButton("📊 Network Monitor")
        monitor_btn.setToolTip("Monitor network traffic and connections")
        monitor_btn.clicked.connect(self.open_network_monitor)
        network_layout.addWidget(monitor_btn, 1, 0)
        
        # Bandwidth test
        bandwidth_btn = QtWidgets.QPushButton("📈 Bandwidth Test")
        bandwidth_btn.setToolTip("Test network bandwidth and latency")
        bandwidth_btn.clicked.connect(self.open_bandwidth_test)
        network_layout.addWidget(bandwidth_btn, 1, 1)
        
        # Wake on LAN
        wol_btn = QtWidgets.QPushButton("⚡ Wake on LAN")
        wol_btn.setToolTip("Wake up network devices remotely")
        wol_btn.clicked.connect(self.open_wake_on_lan)
        network_layout.addWidget(wol_btn, 1, 2)
        
        layout.addWidget(network_group)
        layout.addStretch()
        
        return network_tab
    
    def _create_security_tools_tab(self, tab_widget):
        """Create the security tools tab."""
        security_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(security_tab)
        
        # Encryption group
        encryption_group = QtWidgets.QGroupBox("Encryption & Security")
        encryption_layout = QtWidgets.QGridLayout(encryption_group)
        
        # Encrypt/Decrypt
        encrypt_btn = QtWidgets.QPushButton("🔐 Encrypt/Decrypt")
        encrypt_btn.setToolTip("Encrypt and decrypt files")
        encrypt_btn.clicked.connect(self.open_encrypt_decrypt)
        encryption_layout.addWidget(encrypt_btn, 0, 0)
        
        # Hash calculator
        hash_btn = QtWidgets.QPushButton("🔢 Hash Calculator")
        hash_btn.setToolTip("Calculate file hashes and checksums")
        hash_btn.clicked.connect(self.open_hash_calculator)
        encryption_layout.addWidget(hash_btn, 0, 1)
        
        # Password generator
        password_btn = QtWidgets.QPushButton("🎲 Password Generator")
        password_btn.setToolTip("Generate secure passwords")
        password_btn.clicked.connect(self.open_password_generator)
        encryption_layout.addWidget(password_btn, 0, 2)
        
        # Security preferences
        security_prefs_btn = QtWidgets.QPushButton("⚙️ Security Preferences")
        security_prefs_btn.setToolTip("Configure security settings")
        security_prefs_btn.clicked.connect(self.open_security_preferences)
        encryption_layout.addWidget(security_prefs_btn, 1, 0)
        
        # Key manager
        key_mgr_btn = QtWidgets.QPushButton("🔑 Key Manager")
        key_mgr_btn.setToolTip("Manage encryption keys")
        key_mgr_btn.clicked.connect(self.open_key_manager)
        encryption_layout.addWidget(key_mgr_btn, 1, 1)
        
        # Secure notes
        notes_btn = QtWidgets.QPushButton("📝 Secure Notes")
        notes_btn.setToolTip("Create and manage encrypted notes")
        notes_btn.clicked.connect(self.open_secure_notes)
        encryption_layout.addWidget(notes_btn, 1, 2)
        
        layout.addWidget(encryption_group)
        layout.addStretch()
        
        return security_tab
    
    def _create_system_tools_tab(self, tab_widget):
        """Create the system tools tab."""
        system_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(system_tab)
        
        # System utilities group
        system_group = QtWidgets.QGroupBox("System Utilities")
        system_layout = QtWidgets.QGridLayout(system_group)
        
        # Clipboard manager
        clipboard_btn = QtWidgets.QPushButton("📋 Clipboard Manager")
        clipboard_btn.setToolTip("Enhanced clipboard management")
        clipboard_btn.clicked.connect(self.open_clipboard_manager)
        system_layout.addWidget(clipboard_btn, 0, 0)
        
        # System monitor
        monitor_btn = QtWidgets.QPushButton("📊 System Monitor")
        monitor_btn.setToolTip("Monitor system performance")
        monitor_btn.clicked.connect(self.open_system_monitor)
        system_layout.addWidget(monitor_btn, 0, 1)
        
        # Registry tools
        registry_btn = QtWidgets.QPushButton("🗂️ Registry Tools")
        registry_btn.setToolTip("Windows registry utilities")
        registry_btn.clicked.connect(self.open_registry_tools)
        system_layout.addWidget(registry_btn, 0, 2)
        
        # Disk tools
        disk_btn = QtWidgets.QPushButton("💾 Disk Tools")
        disk_btn.setToolTip("Disk analysis and cleanup tools")
        disk_btn.clicked.connect(self.open_disk_tools)
        system_layout.addWidget(disk_btn, 1, 0)
        
        # Process manager
        process_btn = QtWidgets.QPushButton("⚙️ Process Manager")
        process_btn.setToolTip("Advanced process management")
        process_btn.clicked.connect(self.open_process_manager)
        system_layout.addWidget(process_btn, 1, 1)
        
        # Service manager
        service_btn = QtWidgets.QPushButton("🔧 Service Manager")
        service_btn.setToolTip("Manage Windows services")
        service_btn.clicked.connect(self.open_service_manager)
        system_layout.addWidget(service_btn, 1, 2)
        
        layout.addWidget(system_group)
        layout.addStretch()
        
    def _create_logs_tab(self, tab_widget):
        """Create the logs and status tab."""
        logs_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(logs_tab)
        
        # Controls
        controls_group = QtWidgets.QGroupBox("Log Controls")
        controls_layout = QtWidgets.QHBoxLayout(controls_group)
        
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh Logs")
        refresh_btn.clicked.connect(self.load_recent_logs)
        controls_layout.addWidget(refresh_btn)
        
        clear_btn = QtWidgets.QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)
        
        save_btn = QtWidgets.QPushButton("💾 Save Logs")
        save_btn.clicked.connect(self.save_logs)
        controls_layout.addWidget(save_btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Log display
        self.log_display = QtWidgets.QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QtGui.QFont("Consolas", 9))
        layout.addWidget(self.log_display)
        
        return logs_tab
    
    # Tool Opening Methods
    def open_file_catalog(self):
        """Open file catalog tool."""
        try:
            from ..utilities.file_operations.file_catalog import FileCatalogGUI
            tool = FileCatalogGUI()
            tool.show()
            self._update_status_bar("File Catalog opened")
            self.logger.info("File Catalog tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Catalog: {str(e)}")
            self.logger.error(f"Error opening File Catalog: {str(e)}")
    
    def open_file_touch(self):
        """Open file touch tool."""
        try:
            from ..utilities.file_operations.file_touch import FileTouchGUI
            tool = FileTouchGUI()
            tool.show()
            self._update_status_bar("File Touch opened")
            self.logger.info("File Touch tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Touch: {str(e)}")
            self.logger.error(f"Error opening File Touch: {str(e)}")
    
    def open_file_splitter(self):
        """Open file splitter tool."""
        try:
            from ..utilities.file_operations.file_splitter import \
                FileSplitterGUI
            tool = FileSplitterGUI()
            tool.show()
            self._update_status_bar("File Splitter opened")
            self.logger.info("File Splitter tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Splitter: {str(e)}")
            self.logger.error(f"Error opening File Splitter: {str(e)}")
    
    def open_secure_delete(self):
        """Open secure delete tool."""
        try:
            from ..utilities.file_operations.secure_delete import \
                SecureDeleteGUI
            tool = SecureDeleteGUI()
            tool.show()
            self._update_status_bar("Secure Delete opened")
            self.logger.info("Secure Delete tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Secure Delete: {str(e)}")
            self.logger.error(f"Error opening Secure Delete: {str(e)}")
    
    def open_compression_tools(self):
        """Open compression tools."""
        try:
            from ..utilities.file_operations.compression import CompressionGUI
            tool = CompressionGUI()
            tool.show()
            self._update_status_bar("Compression Tools opened")
            self.logger.info("Compression Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Compression Tools: {str(e)}")
            self.logger.error(f"Error opening Compression Tools: {str(e)}")
    
    def open_duplicate_finder(self):
        """Open duplicate finder tool."""
        try:
            from ..utilities.file_operations.duplicate_finder import \
                DuplicateFinderGUI
            tool = DuplicateFinderGUI()
            tool.show()
            self._update_status_bar("Duplicate Finder opened")
            self.logger.info("Duplicate Finder tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Duplicate Finder: {str(e)}")
            self.logger.error(f"Error opening Duplicate Finder: {str(e)}")
    
    def open_image_metadata(self):
        """Open image metadata editor."""
        try:
            from ..utilities.metadata.image_metadata import ImageMetadataGUI
            tool = ImageMetadataGUI()
            tool.show()
            self._update_status_bar("Image Metadata Editor opened")
            self.logger.info("Image Metadata Editor opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Image Metadata Editor: {str(e)}")
            self.logger.error(f"Error opening Image Metadata Editor: {str(e)}")
    
    def open_office_metadata(self):
        """Open office metadata editor."""
        try:
            from ..tools.metadata.office_metadata import OfficeMetadataGUI
            tool = OfficeMetadataGUI()
            tool.show()
            self._update_status_bar("Office Metadata Editor opened")
            self.logger.info("Office Metadata Editor opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Office Metadata Editor: {str(e)}")
            self.logger.error(f"Error opening Office Metadata Editor: {str(e)}")
    
    def open_pdf_tools(self):
        """Open PDF tools."""
        try:
            from ..tools.pdf_tools.widgets.enhanced_pdf_tools_widget import \
                EnhancedPDFToolsWidget
            tool = EnhancedPDFToolsWidget()
            tool.show()
            self._update_status_bar("PDF Tools opened")
            self.logger.info("PDF Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening PDF Tools: {str(e)}")
            self.logger.error(f"Error opening PDF Tools: {str(e)}")
    
    def open_network_transfer(self):
        """Open network transfer tool."""
        try:
            from ..utilities.network.network_transfer import NetworkTransferGUI
            tool = NetworkTransferGUI()
            tool.show()
            self._update_status_bar("Network Transfer opened")
            self.logger.info("Network Transfer tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Transfer: {str(e)}")
            self.logger.error(f"Error opening Network Transfer: {str(e)}")
    
    def open_network_scan(self):
        """Open network scan tool."""
        try:
            from ..utilities.network.network_scanner import NetworkScannerGUI
            tool = NetworkScannerGUI()
            tool.show()
            self._update_status_bar("Network Scanner opened")
            self.logger.info("Network Scanner tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Scanner: {str(e)}")
            self.logger.error(f"Error opening Network Scanner: {str(e)}")
    
    def open_network_tools(self):
        """Open general network tools."""
        self.tab_widget.setCurrentIndex(2)  # Switch to network tools tab
        self._update_status_bar("Switched to Network Tools tab")
        self.logger.info("Switched to Network Tools tab")
    
    def open_security_tools(self):
        """Open general security tools."""
        self.tab_widget.setCurrentIndex(3)  # Switch to security tools tab
        self._update_status_bar("Switched to Security Tools tab")
        self.logger.info("Switched to Security Tools tab")
    
    def open_system_tools(self):
        """Open general system tools."""
        self.tab_widget.setCurrentIndex(4)  # Switch to system tools tab
        self._update_status_bar("Switched to System Tools tab")
    # Additional tool opening methods for completeness
    def open_port_scanner(self):
        """Open port scanner tool."""
        try:
            from ..utilities.network.port_scanner import PortScannerGUI
            tool = PortScannerGUI()
            tool.show()
            self._update_status_bar("Port Scanner opened")
            self.logger.info("Port Scanner tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Port Scanner: {str(e)}")
            self.logger.error(f"Error opening Port Scanner: {str(e)}")
    
    def open_network_monitor(self):
        """Open network monitor tool."""
        try:
            from ..utilities.network.network_monitor import NetworkMonitorGUI
            tool = NetworkMonitorGUI()
            tool.show()
            self._update_status_bar("Network Monitor opened")
            self.logger.info("Network Monitor tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Monitor: {str(e)}")
            self.logger.error(f"Error opening Network Monitor: {str(e)}")
    
    def open_bandwidth_test(self):
        """Open bandwidth test tool."""
        try:
            from ..utilities.network.bandwidth_test import BandwidthTestGUI
            tool = BandwidthTestGUI()
            tool.show()
            self._update_status_bar("Bandwidth Test opened")
            self.logger.info("Bandwidth Test tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Bandwidth Test: {str(e)}")
            self.logger.error(f"Error opening Bandwidth Test: {str(e)}")
    
    def open_wake_on_lan(self):
        """Open Wake on LAN tool."""
        try:
            from ..utilities.network.wake_on_lan import WakeOnLANGUI
            tool = WakeOnLANGUI()
            tool.show()
            self._update_status_bar("Wake on LAN opened")
            self.logger.info("Wake on LAN tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Wake on LAN: {str(e)}")
            self.logger.error(f"Error opening Wake on LAN: {str(e)}")
    
    def open_encrypt_decrypt(self):
        """Open encrypt/decrypt tool."""
        try:
            from ..utilities.security.encrypt_decrypt import EncryptDecryptGUI
            tool = EncryptDecryptGUI()
            tool.show()
            self._update_status_bar("Encrypt/Decrypt opened")
            self.logger.info("Encrypt/Decrypt tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Encrypt/Decrypt: {str(e)}")
            self.logger.error(f"Error opening Encrypt/Decrypt: {str(e)}")
    
    def open_hash_calculator(self):
        """Open hash calculator tool."""
        try:
            from ..utilities.security.hash_calculator import HashCalculatorGUI
            tool = HashCalculatorGUI()
            tool.show()
            self._update_status_bar("Hash Calculator opened")
            self.logger.info("Hash Calculator tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Hash Calculator: {str(e)}")
            self.logger.error(f"Error opening Hash Calculator: {str(e)}")
    
    def open_password_generator(self):
        """Open password generator tool."""
        try:
            from ..utilities.security.password_generator import \
                PasswordGeneratorGUI
            tool = PasswordGeneratorGUI()
            tool.show()
            self._update_status_bar("Password Generator opened")
            self.logger.info("Password Generator tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Password Generator: {str(e)}")
            self.logger.error(f"Error opening Password Generator: {str(e)}")
    
    def open_security_preferences(self):
        """Open security preferences tool."""
        try:
            from ..utilities.security.security_preferences import \
                SecurityPreferencesGUI
            tool = SecurityPreferencesGUI()
            tool.show()
            self._update_status_bar("Security Preferences opened")
            self.logger.info("Security Preferences tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Security Preferences: {str(e)}")
            self.logger.error(f"Error opening Security Preferences: {str(e)}")
    
    def open_key_manager(self):
        """Open key manager tool."""
        try:
            from ..utilities.security.key_manager import KeyManagerGUI
            tool = KeyManagerGUI()
            tool.show()
            self._update_status_bar("Key Manager opened")
            self.logger.info("Key Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Key Manager: {str(e)}")
            self.logger.error(f"Error opening Key Manager: {str(e)}")
    
    def open_secure_notes(self):
        """Open secure notes tool."""
        try:
            from ..utilities.security.secure_notes import SecureNotesGUI
            tool = SecureNotesGUI()
            tool.show()
            self._update_status_bar("Secure Notes opened")
            self.logger.info("Secure Notes tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Secure Notes: {str(e)}")
            self.logger.error(f"Error opening Secure Notes: {str(e)}")
    
    def open_clipboard_manager(self):
        """Open clipboard manager tool."""
        try:
            from ..utilities.system.clipboard_manager import \
                ClipboardManagerGUI
            tool = ClipboardManagerGUI()
            tool.show()
            self._update_status_bar("Clipboard Manager opened")
            self.logger.info("Clipboard Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Clipboard Manager: {str(e)}")
            self.logger.error(f"Error opening Clipboard Manager: {str(e)}")
    
    def open_system_monitor(self):
        """Open system monitor tool."""
        try:
            from ..utilities.system.system_monitor import SystemMonitorGUI
            tool = SystemMonitorGUI()
            tool.show()
            self._update_status_bar("System Monitor opened")
            self.logger.info("System Monitor tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening System Monitor: {str(e)}")
            self.logger.error(f"Error opening System Monitor: {str(e)}")
    
    def open_registry_tools(self):
        """Open registry tools."""
        try:
            from ..utilities.system.registry_tools import RegistryToolsGUI
            tool = RegistryToolsGUI()
            tool.show()
            self._update_status_bar("Registry Tools opened")
            self.logger.info("Registry Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Registry Tools: {str(e)}")
            self.logger.error(f"Error opening Registry Tools: {str(e)}")
    
    def open_disk_tools(self):
        """Open disk tools."""
        try:
            from ..utilities.system.disk_tools import DiskToolsGUI
            tool = DiskToolsGUI()
            tool.show()
            self._update_status_bar("Disk Tools opened")
            self.logger.info("Disk Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Disk Tools: {str(e)}")
            self.logger.error(f"Error opening Disk Tools: {str(e)}")
    
    def open_process_manager(self):
        """Open process manager tool."""
        try:
            from ..utilities.system.process_manager import ProcessManagerGUI
            tool = ProcessManagerGUI()
            tool.show()
            self._update_status_bar("Process Manager opened")
            self.logger.info("Process Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Process Manager: {str(e)}")
            self.logger.error(f"Error opening Process Manager: {str(e)}")
    
    def open_service_manager(self):
        """Open service manager tool."""
        try:
            from ..utilities.system.service_manager import ServiceManagerGUI
            tool = ServiceManagerGUI()
            tool.show()
            self._update_status_bar("Service Manager opened")
            self.logger.info("Service Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Service Manager: {str(e)}")
            self.logger.error(f"Error opening Service Manager: {str(e)}")
    
    # Log management methods
    def load_recent_logs(self):
        """Load and display recent log entries."""
        if hasattr(self, 'log_display'):
            try:
                # Get recent log entries from the logger
                log_entries = []
                if hasattr(self.logger, 'handlers'):
                    for handler in self.logger.handlers:
                        if hasattr(handler, 'get_recent_logs'):
                            log_entries.extend(handler.get_recent_logs())
                
                if log_entries:
                    self.log_display.clear()
                    for entry in log_entries[-100:]:  # Show last 100 entries
                        self.log_display.append(entry)
                else:
                    self.log_display.setText("No recent log entries found.")
                    
                self._update_status_bar("Logs refreshed")
            except Exception as e:
                self.log_display.setText(f"Error loading logs: {str(e)}")
                self.logger.error(f"Error loading logs: {str(e)}")
    
    def clear_logs(self):
        """Clear the log display."""
        if hasattr(self, 'log_display'):
            self.log_display.clear()
            self._update_status_bar("Logs cleared")
            self.logger.info("Log display cleared")
    
    def save_logs(self):
        """Save current logs to file."""
        if hasattr(self, 'log_display'):
            try:
                from PyQt5.QtWidgets import QFileDialog
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Logs",
                    f"rfu_hub_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "Text Files (*.txt);;All Files (*)"
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.log_display.toPlainText())
                    self._update_status_bar(f"Logs saved to {filename}")
                    self.logger.info(f"Logs saved to {filename}")
            except Exception as e:
                self._update_status_bar(f"Error saving logs: {str(e)}")
                self.logger.error(f"Error saving logs: {str(e)}")
    
    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 5000)  # Show for 5 seconds


def main():
    """Main function to run the RFU Hub."""
    import sys

    # Create QApplication if it doesn't exist
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create and show the hub
    hub = RFUHub()
    hub.show()
    
    # Start the event loop if this is the main application
    if __name__ == "__main__":
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()