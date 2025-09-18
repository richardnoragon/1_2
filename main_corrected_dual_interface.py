#!/usr/bin/env python3
"""
Richard's File Utilities - Main Entry Point with Dual Interface System

This is the main entry point for the Richard's File Utilities application.
It provides a comprehensive GUI interface with dual interface modes:
- Dialog-Based Hub Interface (tabbed)
- Multi-Pane Explorer Layout

Enhanced with interface mode switching, workflow analysis, and accessibility features.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'development', 'demos'))

# Import constants for string literals
from src.core.constants import (APP_NAME, IMPORT_ERROR, JSON_FILES_FILTER,
                                    SECURITY_TEST, SUGGESTED_SOLUTIONS_HEADER)


# Interface mode definitions
class InterfaceMode(Enum):
    """Enumeration for interface modes."""
    DIALOG_HUB = "dialog_hub"
    MULTI_PANE = "multi_pane"
    AUTO_DETECT = "auto_detect"

class WorkflowPattern(Enum):
    """Enumeration for detected workflow patterns."""
    FILE_MANAGEMENT = "file_management"
    BATCH_OPERATIONS = "batch_operations"
    DEVELOPMENT = "development"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    SYSTEM_MAINTENANCE = "system_maintenance"

# Initialize database system
def initialize_database_system():
    """Initialize the database and enhanced configuration system with proper error handling."""
    db_manager = None
    logger = None
    
    try:
        # Setup basic logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('rfu_errors.log', encoding='utf-8')
            ]
        )
        logger = logging.getLogger('RFU.Main')
        
        # Import and initialize database manager with validation
        try:
            from scripts.maintenance.standalone_database_manager import \
                get_database_manager
            db_manager = get_database_manager()
            
            # Validate database connection
            if db_manager is None:
                logger.warning("Database manager initialization returned None")
                return False
                
            # Test database connectivity
            db_info = db_manager.get_database_info()
            if not db_info or 'database_file' not in db_info:
                logger.error("Database connectivity test failed")
                return False
                
        except ImportError as e:
            logger.error("Database module import failed: %s", e)
            return False
        except (RuntimeError, OSError, AttributeError) as e:
            logger.error("Database manager initialization failed: %s", e)
            return False
        
        logger.info("Database system initialized successfully")
        logger.info("Database: %s", db_info.get('database_file'))
        
        return True
        
    except (RuntimeError, OSError, ImportError, AttributeError) as e:
        # Ensure we always have logging even if database fails
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('RFU.Main')
        
        logger.error("Critical: Database system initialization failed: %s", e)
        logger.warning("Application will continue without database features")
        return False

# Initialize database system
DATABASE_AVAILABLE = initialize_database_system()

# Import the enhanced PDF tools widget
try:
    from scripts.development.demos.enhanced_pdf_tools_widget import \
        EnhancedPDFToolsWidget
    ENHANCED_PDF_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced PDF Tools not available: {e}")
    ENHANCED_PDF_TOOLS_AVAILABLE = False

# Interface selection dialog
class InterfaceSelectionDialog:
    """Dialog for selecting interface mode on startup."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.selected_mode = InterfaceMode.DIALOG_HUB
        self.remember_choice = False
        self.workflow_detected = None
    
    def show_selection_dialog(self):
        """Show interface selection dialog with recommendations."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import (QCheckBox, QDialog, QGroupBox,
                                     QHBoxLayout, QLabel, QPushButton,
                                     QRadioButton, QTextEdit, QVBoxLayout)
        
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Choose Your Workspace Interface")
        dialog.setFixedSize(600, 500)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("Welcome to Richard's File Utilities")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Workflow detection section
        workflow_group = QGroupBox("Recommended Interface")
        workflow_layout = QVBoxLayout(workflow_group)
        
        detected_workflow = self._detect_initial_workflow()
        recommendation = self._get_interface_recommendation(detected_workflow)
        
        recommendation_label = QLabel(f"Based on your system, we recommend: {recommendation['name']}")
        recommendation_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        workflow_layout.addWidget(recommendation_label)
        
        reason_text = QTextEdit()
        reason_text.setPlainText(recommendation['reason'])
        reason_text.setMaximumHeight(80)
        reason_text.setReadOnly(True)
        workflow_layout.addWidget(reason_text)
        
        layout.addWidget(workflow_group)
        
        # Interface selection
        selection_group = QGroupBox("Select Interface Mode")
        selection_layout = QVBoxLayout(selection_group)
        
        # Dialog Hub option
        self.dialog_radio = QRadioButton("Dialog-Based Hub Interface")
        self.dialog_radio.setChecked(recommendation['mode'] == InterfaceMode.DIALOG_HUB)
        dialog_desc = QLabel("• Comprehensive tabbed interface\\n• All tools organized by category\\n• Professional workflow design\\n• Perfect for organized task management")
        dialog_desc.setStyleSheet("margin-left: 20px; color: #555;")
        selection_layout.addWidget(self.dialog_radio)
        selection_layout.addWidget(dialog_desc)
        
        # Multi-pane option
        self.pane_radio = QRadioButton("Multi-Pane Explorer Layout")
        self.pane_radio.setChecked(recommendation['mode'] == InterfaceMode.MULTI_PANE)
        pane_desc = QLabel("• Simultaneous multiple views\\n• Resizable, dockable panels\\n• File trees and property panels\\n• Perfect for complex operations")
        pane_desc.setStyleSheet("margin-left: 20px; color: #555;")
        selection_layout.addWidget(self.pane_radio)
        selection_layout.addWidget(pane_desc)
        
        layout.addWidget(selection_group)
        
        # Remember choice checkbox
        self.remember_checkbox = QCheckBox("Remember my choice (can be changed in preferences)")
        self.remember_checkbox.setChecked(True)
        layout.addWidget(self.remember_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Continue")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        # Show dialog and get result
        if dialog.exec_() == QDialog.Accepted:
            self.selected_mode = InterfaceMode.DIALOG_HUB if self.dialog_radio.isChecked() else InterfaceMode.MULTI_PANE
            self.remember_choice = self.remember_checkbox.isChecked()
            return True
        return False
    
    def _detect_initial_workflow(self):
        """Detect initial workflow pattern based on system state."""
        development_indicators = 0
        
        # Check for development environment indicators
        home_dir = Path.home()
        dev_dirs = ['src', 'projects', 'code', 'development', 'workspace']
        for dev_dir in dev_dirs:
            if (home_dir / dev_dir).exists():
                development_indicators += 1
        
        # Check for common development tools
        common_tools = ['git', 'python', 'npm', 'code']
        for tool in common_tools:
            if self._command_exists(tool):
                development_indicators += 1
        
        # Default to file management for general users
        if development_indicators >= 3:
            return WorkflowPattern.DEVELOPMENT
        else:
            return WorkflowPattern.FILE_MANAGEMENT
    
    def _command_exists(self, command):
        """Check if a command exists in the system."""
        try:
            subprocess.check_output(['where' if os.name == 'nt' else 'which', command], 
                                   stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_interface_recommendation(self, workflow):
        """Get interface recommendation based on workflow pattern."""
        recommendations = {
            WorkflowPattern.FILE_MANAGEMENT: {
                'mode': InterfaceMode.DIALOG_HUB,
                'name': 'Dialog-Based Hub',
                'reason': 'Perfect for organized file operations with comprehensive tabbed interface. '
                         'All tools are categorized and easily accessible with professional workflow design.'
            },
            WorkflowPattern.DEVELOPMENT: {
                'mode': InterfaceMode.MULTI_PANE,
                'name': 'Multi-Pane Explorer',
                'reason': 'Ideal for development workflows requiring simultaneous access to multiple '
                         'directories, file comparison, and integrated tool access. Supports complex '
                         'project navigation and batch operations.'
            },
            WorkflowPattern.BATCH_OPERATIONS: {
                'mode': InterfaceMode.MULTI_PANE,
                'name': 'Multi-Pane Explorer',
                'reason': 'Optimized for batch operations with multiple file views, drag-and-drop '
                         'between panes, and efficient cross-directory operations.'
            }
        }
        
        return recommendations.get(workflow, recommendations[WorkflowPattern.FILE_MANAGEMENT])

try:
    from PyQt5.QtCore import (QEasingCurve, QPropertyAnimation, Qt, pyqtSignal,
                              pyqtSlot)
    from PyQt5.QtGui import QFont, QIcon
    from PyQt5.QtWidgets import (QApplication, QFileDialog, QFrame,
                                 QGraphicsOpacityEffect, QGridLayout,
                                 QGroupBox, QHBoxLayout, QLabel, QMainWindow,
                                 QMessageBox, QPushButton, QScrollArea,
                                 QTabWidget, QVBoxLayout, QWidget)
    
    class RFUMainWindow(QMainWindow):
        # Signals for communication
        interface_switched = pyqtSignal(str)
        tool_launched = pyqtSignal(str)
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_NAME)
            self.setGeometry(200, 200, 900, 700)
            
            # Store references to opened windows
            self.opened_windows = {}
            
            # Interface mode management
            self.current_interface_mode = InterfaceMode.DIALOG_HUB
            self.multi_pane_explorer = None
            self.dialog_hub_widget = None
            self.interface_switching_enabled = True
            self.transition_in_progress = False
            
            # Workflow analysis and session tracking
            self.session_start_time = datetime.now()
            self.tool_usage_count = 0
            self.interface_switch_count = 0
            
            # Data synchronization
            self.shared_state = {
                'recent_files': [],
                'recent_directories': [],
                'bookmarks': [],
                'tool_preferences': {},
                'window_states': {}
            }
            
            # Initialize database tracking
            self.database_available = DATABASE_AVAILABLE
            if self.database_available:
                try:
                    from scripts.maintenance.standalone_database_manager import \
                        get_database_manager
                    self.db_manager = get_database_manager()
                except Exception as e:
                    print(f"Database initialization failed: {e}")
                    self.database_available = False
                    self.db_manager = None
            
            # Initialize configuration manager
            try:
                from src.config_manager import get_config_manager
                self.config_manager = get_config_manager()
                self._setup_interface_configuration()
            except Exception as e:
                print(f"Configuration manager initialization failed: {e}")
                self.config_manager = None
            
            # Determine interface mode
            self._determine_interface_mode()
            
            # Initialize the appropriate interface
            self._initialize_interface()
        
        def _setup_interface_configuration(self):
            """Setup interface-specific configuration sections."""
            if not self.config_manager:
                return
            
            # Ensure interface configuration sections exist
            interface_sections = {
                'interface_mode': {
                    'current_mode': InterfaceMode.DIALOG_HUB.value,
                    'auto_detect_enabled': True,
                    'remember_choice': True,
                    'show_startup_dialog': True,
                    'transition_animations': True,
                    'switch_confirmation': False
                },
                'interface_usage': {
                    'mode_statistics': {},
                    'switch_count': 0,
                    'total_session_time': 0,
                    'preference_confidence': 0.5
                },
                'workflow_analysis': {
                    'enabled': True,
                    'suggestion_threshold': 0.7,
                    'recent_sessions': [],
                    'pattern_detection': True
                }
            }
            
            for section, defaults in interface_sections.items():
                for key, default_value in defaults.items():
                    try:
                        if hasattr(self.config_manager, 'get_setting'):
                            current_value = self.config_manager.get_setting(section, key)
                            if current_value is None and hasattr(self.config_manager, 'set_setting'):
                                self.config_manager.set_setting(section, key, default_value)
                    except (AttributeError, KeyError):
                        pass
        
        def _determine_interface_mode(self):
            """Determine which interface mode to use."""
            if not self.config_manager:
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                return
            
            try:
                # Check if user has saved preference
                saved_mode = self.config_manager.get_setting('interface_mode', 'current_mode')
                show_startup = self.config_manager.get_setting('interface_mode', 'show_startup_dialog', True)
                
                if saved_mode and not show_startup:
                    try:
                        self.current_interface_mode = InterfaceMode(saved_mode)
                        return
                    except ValueError:
                        pass
                
                # Show interface selection dialog
                self._show_interface_selection_dialog()
                
            except (AttributeError, KeyError):
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
        
        def _show_interface_selection_dialog(self):
            """Show interface selection dialog on startup."""
            try:
                dialog = InterfaceSelectionDialog(self)
                if dialog.show_selection_dialog():
                    self.current_interface_mode = dialog.selected_mode
                    if dialog.remember_choice and self.config_manager:
                        try:
                            self.config_manager.set_setting('interface_mode', 'current_mode', 
                                                           self.current_interface_mode.value)
                            self.config_manager.set_setting('interface_mode', 'show_startup_dialog', False)
                        except AttributeError:
                            pass
            except Exception as e:
                print(f"Error showing interface selection: {e}")
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
        
        def _initialize_interface(self):
            """Initialize the selected interface mode."""
            if self.current_interface_mode == InterfaceMode.MULTI_PANE:
                self._initialize_multi_pane_interface()
            else:
                self._initialize_dialog_hub_interface()
        
        def _initialize_dialog_hub_interface(self):
            """Initialize the dialog-based hub interface with full tabbed functionality."""
            self.setWindowTitle(f"{APP_NAME} - Dialog Hub Interface")
            
            # Store reference to dialog hub widget for later restoration
            if hasattr(self, 'dialog_hub_widget') and self.dialog_hub_widget:
                self.setCentralWidget(self.dialog_hub_widget)
            else:
                self.init_ui()
                self.dialog_hub_widget = self.centralWidget()
        
        def _initialize_multi_pane_interface(self):
            """Initialize the multi-pane explorer interface."""
            try:
                # Store current dialog hub widget if switching
                current_widget = self.centralWidget()
                if current_widget and not hasattr(self, 'dialog_hub_widget'):
                    self.dialog_hub_widget = current_widget
                
                # Clear current central widget
                if current_widget:
                    current_widget.setParent(None)
                
                # Try to import the multi-pane explorer
                if not self.multi_pane_explorer:
                    from src.file_explorer.multi_pane_explorer import \
                        MultiPaneExplorer
                    self.multi_pane_explorer = MultiPaneExplorer(self)
                
                self.setCentralWidget(self.multi_pane_explorer)
                self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer")
                
                # Setup interface switching menu for multi-pane mode
                self._setup_interface_switching_menu()
                
            except ImportError:
                # Fallback to simplified multi-pane interface
                self._create_fallback_multi_pane()
        
        def _create_fallback_multi_pane(self):
            """Create fallback multi-pane interface when full version not available."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # Title
            title_label = QLabel("Multi-Pane Explorer (Simplified)")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
            layout.addWidget(title_label)
            
            # Info message
            info_label = QLabel("Full multi-pane explorer not available.\\nUsing simplified interface.")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #666; margin: 10px;")
            layout.addWidget(info_label)
            
            # Switch back button
            switch_button = QPushButton("Switch to Dialog Hub")
            switch_button.clicked.connect(lambda: self.switch_interface_mode(InterfaceMode.DIALOG_HUB))
            layout.addWidget(switch_button)
            
            self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer (Simplified)")
        
        def switch_interface_mode(self, new_mode, animated=True):
            """Switch between interface modes with optional animation."""
            if (self.current_interface_mode == new_mode or 
                self.transition_in_progress):
                return
            
            self.transition_in_progress = True
            old_mode = self.current_interface_mode
            self.current_interface_mode = new_mode
            
            # Update configuration
            if self.config_manager:
                try:
                    self.config_manager.set_setting('interface_mode', 'current_mode', new_mode.value)
                except AttributeError:
                    pass
            
            # Track switch for analytics
            self.interface_switch_count += 1
            
            # Perform transition
            if animated:
                self._animate_interface_transition(old_mode, new_mode)
            else:
                self._immediate_interface_transition(new_mode)
            
            # Emit signal
            self.interface_switched.emit(new_mode.value)
        
        def _animate_interface_transition(self, old_mode, new_mode):
            """Animate transition between interface modes."""
            # Create fade out animation
            self.fade_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.fade_effect)
            
            self.fade_out = QPropertyAnimation(self.fade_effect, b"opacity")
            self.fade_out.setDuration(300)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.OutCubic)
            
            def complete_transition():
                self._immediate_interface_transition(new_mode)
                
                # Create fade in animation
                self.fade_in = QPropertyAnimation(self.fade_effect, b"opacity")
                self.fade_in.setDuration(300)
                self.fade_in.setStartValue(0.0)
                self.fade_in.setEndValue(1.0)
                self.fade_in.setEasingCurve(QEasingCurve.InCubic)
                
                def cleanup():
                    self.setGraphicsEffect(None)
                    self.transition_in_progress = False
                
                self.fade_in.finished.connect(cleanup)
                self.fade_in.start()
            
            self.fade_out.finished.connect(complete_transition)
            self.fade_out.start()
        
        def _immediate_interface_transition(self, new_mode):
            """Perform immediate interface transition without animation."""
            if new_mode == InterfaceMode.MULTI_PANE:
                self._initialize_multi_pane_interface()
            else:
                self._initialize_dialog_hub_interface()
            
            if not hasattr(self, 'fade_out'):  # Not in animated transition
                self.transition_in_progress = False
        
        def _setup_interface_switching_menu(self):
            """Setup menu for switching between interface modes."""
            menubar = self.menuBar()
            
            # Add interface menu
            interface_menu = menubar.addMenu('&Interface')
            
            # Switch to dialog hub action
            switch_hub_action = interface_menu.addAction('Switch to Dialog Hub')
            switch_hub_action.setShortcut('Ctrl+Shift+H')
            switch_hub_action.triggered.connect(lambda: self.switch_interface_mode(InterfaceMode.DIALOG_HUB))
            switch_hub_action.setEnabled(self.current_interface_mode != InterfaceMode.DIALOG_HUB)
            
            # Switch to multi-pane action
            switch_pane_action = interface_menu.addAction('Switch to Multi-Pane Explorer')
            switch_pane_action.setShortcut('Ctrl+Shift+M')
            switch_pane_action.triggered.connect(lambda: self.switch_interface_mode(InterfaceMode.MULTI_PANE))
            switch_pane_action.setEnabled(self.current_interface_mode != InterfaceMode.MULTI_PANE)
            
            interface_menu.addSeparator()
            
            # Interface preferences
            preferences_action = interface_menu.addAction('Interface Preferences...')
            preferences_action.triggered.connect(self._show_interface_preferences)
        
        def _show_interface_preferences(self):
            """Show interface preferences dialog."""
            QMessageBox.information(self, "Interface Preferences", 
                                  "Interface preferences dialog would be shown here.")
        
        def launch_tool(self, tool_name, module_name=None, class_name=None):
            """Enhanced tool launch with tracking."""
            # Track tool usage
            self.tool_usage_count += 1
            
            # Emit signal for tracking
            self.tool_launched.emit(tool_name)
            
            # Show placeholder for demonstration
            QMessageBox.information(
                self, "Tool Launch", 
                f"Launching {tool_name}...\\n\\n"
                f"Current Interface: {self.current_interface_mode.value}\\n"
                f"This demonstrates the integrated dual-interface system."
            )
        
        def init_ui(self):
            """Initialize the comprehensive tabbed user interface."""
            # Create menu bar
            self.create_menu_bar()
            
            # Setup interface switching menu
            self._setup_interface_switching_menu()
            
            # Create central widget and main layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            
            # Add title
            title_label = QLabel(APP_NAME)
            title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            title_label.setStyleSheet("""
                font-size: 28px; 
                font-weight: bold; 
                padding: 20px;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 10px;
                margin: 10px;
            """)
            main_layout.addWidget(title_label)
            
            # Create tab widget for different tool categories
            tab_widget = QTabWidget()
            main_layout.addWidget(tab_widget)
            
            # File Management Tools
            file_mgmt_tab = self.create_tool_category_tab([
                ("File Finder", "Search and find files based on various criteria", self.open_file_finder),
                ("Catalog Files", "Create and manage file catalogs", self.open_catalog),
                ("Rename Files", "Batch rename files and folders", self.open_rename),
                ("Organize Files", "Automatically organize files by type/date", self.open_organize),
                ("Advanced Folders", "Configure smart folder monitoring and search", self.open_advanced_folders),
            ])
            tab_widget.addTab(file_mgmt_tab, "File Management")
            
            # File Operations Tools
            file_ops_tab = self.create_tool_category_tab([
                ("Copy/Move/Sync/Delete", "Advanced file operations", self.open_cmsd),
                ("Compress/Decompress", "Archive and extract files", self.open_compress),
                ("Split/Join Files", "Split large files or join parts", self.open_file_splitter),
                ("Synchronize", "Synchronize directories", self.open_sync),
                ("Enhanced Editor", "Advanced text editor with syntax highlighting", self.open_enhanced_editor),
            ])
            tab_widget.addTab(file_ops_tab, "File Operations")
            
            # Analysis Tools
            analysis_tab = self.create_tool_category_tab([
                ("Size Analyzer", "Analyze disk space usage", self.open_size_analyzer),
                ("Duplicate Finder", "Find and remove duplicate files", self.open_duplicate_finder),
                ("File Checksum", "Calculate and verify checksums", self.open_checksum),
                ("Empty Folders", "Find and clean empty folders", self.open_empty_folders),
            ])
            tab_widget.addTab(analysis_tab, "Analysis")
            
            # Security Tools
            security_tab = self.create_tool_category_tab([
                ("Security Preferences", "Configure comprehensive security settings", self.open_security_preferences),
                ("Encrypt/Decrypt", "Secure file encryption and decryption", self.open_encrypt_decrypt),
                ("Secure Delete", "Permanently delete sensitive files", self.open_secure_delete),
                ("Permissions Editor", "Manage file and folder permissions", self.open_permissions),
            ])
            tab_widget.addTab(security_tab, "Security")
            
            # Metadata Tools
            metadata_tab = self.create_tool_category_tab([
                ("Edit Image Metadata", "View and edit image metadata", self.open_image_metadata),
                ("Office Metadata Editor", "Edit document metadata", self.open_office_metadata),
                ("File Touch", "Modify file timestamps", self.open_file_touch),
            ])
            tab_widget.addTab(metadata_tab, "Metadata")
            
            # PDF Tools
            if ENHANCED_PDF_TOOLS_AVAILABLE:
                pdf_tab = self.create_enhanced_pdf_tools_tab()
            else:
                pdf_tab = self.create_tool_category_tab([
                    ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                    ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                    ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
                ])
            tab_widget.addTab(pdf_tab, "PDF Tools")
            
            # Network Tools
            network_tab = self.create_tool_category_tab([
                ("Network Connectivity", "Check network connectivity and diagnostics", self.open_network_connectivity),
                ("Network Scanner", "Scan network for devices and services", self.open_network_scanner),
                ("Network Transfer", "Transfer files and configurations between RFU clients", self.open_network_transfer),
                ("Bookmark Manager", "Cross-platform bookmark keeper/editor/importer", self.open_bookmark_manager),
            ])
            tab_widget.addTab(network_tab, "Network Tools")
            
            # Privacy Tools
            privacy_tab = self.create_tool_category_tab([
                ("Privacy Cleaner", "Clean privacy-sensitive data", self.open_privacy_cleaner),
                ("Data Anonymizer", "Anonymize sensitive file data", self.open_data_anonymizer),
            ])
            tab_widget.addTab(privacy_tab, "Privacy Tools")
            
            # System Tools
            system_tab = self.create_tool_category_tab([
                ("Enhanced Clipboard", "Advanced clipboard management", self.open_enhanced_clipboard),
                ("System Diagnostics", "Comprehensive system analysis", self.open_system_diagnostics),
                ("System Cleanup", "Clean temporary and unnecessary files", self.open_system_cleanup),
                ("Software Maintenance", "Update and maintain installed software", self.open_software_maintenance),
            ])
            tab_widget.addTab(system_tab, "System Tools")
        
        def create_tool_category_tab(self, tools):
            """Create a tab widget for a category of tools."""
            tab_widget = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab_widget)
            
            # Create grid layout for tools
            grid_layout = QGridLayout(tab_widget)
            grid_layout.setSpacing(15)
            grid_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add tools to grid
            row, col = 0, 0
            max_cols = 2
            
            for name, description, callback in tools:
                tool_button = self.create_tool_button(name, description, callback)
                grid_layout.addWidget(tool_button, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Add stretch to push tools to top
            grid_layout.setRowStretch(row + 1, 1)
            
            return scroll_area
        
        def create_tool_button(self, name, description, callback):
            """Create a styled tool button."""
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
            """)
            
            layout = QVBoxLayout(frame)
            
            # Tool name
            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057;")
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)
            
            # Tool description
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 11px; color: #6c757d;")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
            
            # Launch button
            launch_button = QPushButton("Launch")
            launch_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """)
            launch_button.clicked.connect(lambda: self.launch_tool(name))
            layout.addWidget(launch_button)
            
            frame.setFixedHeight(120)
            return frame
        
        def create_enhanced_pdf_tools_tab(self):
            """Create enhanced PDF tools tab."""
            if ENHANCED_PDF_TOOLS_AVAILABLE:
                try:
                    pdf_widget = EnhancedPDFToolsWidget(self)
                    return pdf_widget
                except Exception as e:
                    print(f"Error creating enhanced PDF tools: {e}")
            
            # Fallback to simple PDF tools
            return self.create_tool_category_tab([
                ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
            ])
        
        def create_menu_bar(self):
            """Create the application menu bar."""
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu('&File')
            file_menu.addAction('&New Project', self.new_project)
            file_menu.addAction('&Open...', self.open_file)
            file_menu.addSeparator()
            file_menu.addAction('&Save Project', self.save_project)
            file_menu.addAction('Save Project &As...', self.save_project_as)
            file_menu.addSeparator()
            file_menu.addAction('E&xit', self.close)
            
            # Tools menu
            tools_menu = menubar.addMenu('&Tools')
            tools_menu.addAction('&Preferences...', self.show_main_preferences)
            tools_menu.addAction('&Refresh Tool List', self.refresh_tool_list)
            
            # Help menu
            help_menu = menubar.addMenu('&Help')
            help_menu.addAction('&About', self.show_about_dialog)
        
        # Placeholder tool launch methods (replace with actual implementations)
        def open_file_finder(self): self.launch_tool("File Finder")
        def open_catalog(self): self.launch_tool("Catalog Files")
        def open_rename(self): self.launch_tool("Rename Files")
        def open_organize(self): self.launch_tool("Organize Files")
        def open_advanced_folders(self): self.launch_tool("Advanced Folders")
        def open_cmsd(self): self.launch_tool("Copy/Move/Sync/Delete")
        def open_compress(self): self.launch_tool("Compress/Decompress")
        def open_file_splitter(self): self.launch_tool("Split/Join Files")
        def open_sync(self): self.launch_tool("Synchronize")
        def open_enhanced_editor(self): self.launch_tool("Enhanced Editor")
        def open_size_analyzer(self): self.launch_tool("Size Analyzer")
        def open_duplicate_finder(self): self.launch_tool("Duplicate Finder")
        def open_checksum(self): self.launch_tool("File Checksum")
        def open_empty_folders(self): self.launch_tool("Empty Folders")
        def open_security_preferences(self): self.launch_tool("Security Preferences")
        def open_encrypt_decrypt(self): self.launch_tool("Encrypt/Decrypt")
        def open_secure_delete(self): self.launch_tool("Secure Delete")
        def open_permissions(self): self.launch_tool("Permissions Editor")
        def open_image_metadata(self): self.launch_tool("Edit Image Metadata")
        def open_office_metadata(self): self.launch_tool("Office Metadata Editor")
        def open_file_touch(self): self.launch_tool("File Touch")
        def open_pdf_tools(self): self.launch_tool("PDF Utilities")
        def open_pdf_links(self): self.launch_tool("Extract Links")
        def open_pdf_pages(self): self.launch_tool("Page Administration")
        def open_network_connectivity(self): self.launch_tool("Network Connectivity")
        def open_network_scanner(self): self.launch_tool("Network Scanner")
        def open_network_transfer(self): self.launch_tool("Network Transfer")
        def open_bookmark_manager(self): self.launch_tool("Bookmark Manager")
        def open_privacy_cleaner(self): self.launch_tool("Privacy Cleaner")
        def open_data_anonymizer(self): self.launch_tool("Data Anonymizer")
        def open_enhanced_clipboard(self): self.launch_tool("Enhanced Clipboard")
        def open_system_diagnostics(self): self.launch_tool("System Diagnostics")
        def open_system_cleanup(self): self.launch_tool("System Cleanup")
        def open_software_maintenance(self): self.launch_tool("Software Maintenance")
        
        # Menu callback implementations
        def new_project(self): QMessageBox.information(self, "New Project", "New project functionality would be implemented here.")
        def open_file(self): QMessageBox.information(self, "Open File", "Open file functionality would be implemented here.")
        def save_project(self): QMessageBox.information(self, "Save Project", "Save project functionality would be implemented here.")
        def save_project_as(self): QMessageBox.information(self, "Save Project As", "Save project as functionality would be implemented here.")
        def show_main_preferences(self): QMessageBox.information(self, "Preferences", "Main preferences dialog would be shown here.")
        def refresh_tool_list(self): QMessageBox.information(self, "Refresh", "Tool list refresh functionality would be implemented here.")
        def show_about_dialog(self): QMessageBox.about(self, "About RFU", f"<h3>{APP_NAME}</h3><p>Version 3.0.0 with Dual Interface System</p><p>A comprehensive file utility suite with intelligent interface selection.</p>")
    
    def main():
        """Main entry point for the application."""
        print(f"Starting {APP_NAME} with Dual Interface System...")
        
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName(APP_NAME)
        
        window = RFUMainWindow()
        window.show()
        
        print("Dual-interface system initialized with tabbed hub interface.")
        return app.exec_()
    
    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    print("To install PyQt5, run: pip install PyQt5")
    sys.exit(1)
except (RuntimeError, OSError, AttributeError) as e:
    print(f"Error starting application: {e}")
    sys.exit(1)