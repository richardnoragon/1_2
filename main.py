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

# PDF tool constants
PDF_UTILITIES = "PDF Utilities"
EXTRACT_LINKS = "Extract Links"
PAGE_ADMINISTRATION = "Page Administration"


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

# Import the full-featured multi-pane file explorer
try:
    MULTI_PANE_EXPLORER_AVAILABLE = True
except ImportError as e:
    print(f"Full multi-pane explorer not available: {e}")
    MULTI_PANE_EXPLORER_AVAILABLE = False

# Enhanced Interface selection dialog with comprehensive startup functionality
class InterfaceSelectionDialog:
    """Enhanced modal dialog for selecting interface mode on startup with comprehensive styling and error handling."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.selected_mode = InterfaceMode.DIALOG_HUB
        self.remember_choice = False
        self.workflow_detected = None
        self.dialog = None
        self.dialog_radio = None
        self.pane_radio = None
        self.remember_checkbox = None
        
        # Initialize logging for dialog operations
        self.logger = logging.getLogger('RFU.InterfaceDialog')
    
    def show_selection_dialog(self):
        """Show comprehensive modal interface selection dialog with enhanced styling and error handling."""
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
            from PyQt5.QtWidgets import (QButtonGroup, QCheckBox, QDialog,
                                         QFrame, QGroupBox, QHBoxLayout,
                                         QLabel, QPushButton, QRadioButton,
                                         QSizePolicy, QSpacerItem, QTextEdit,
                                         QVBoxLayout)

            # Create modal dialog with enhanced properties
            self.dialog = QDialog(self.parent)
            self.dialog.setWindowTitle("Choose Your Workspace Interface - Richard's File Utilities")
            self.dialog.setModal(True)
            self.dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
            
            # Prevent closing without selection
            self.dialog.closeEvent = self._handle_close_event
            
            # Apply comprehensive styling first
            self._apply_dialog_styling()
            
            layout = QVBoxLayout(self.dialog)
            layout.setSpacing(20)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Enhanced title section with branding
            title_frame = self._create_title_section()
            layout.addWidget(title_frame)
            
            # Workflow detection and recommendation section
            recommendation_frame = self._create_recommendation_section()
            layout.addWidget(recommendation_frame)
            
            # Interface selection section with enhanced styling
            selection_frame = self._create_selection_section()
            layout.addWidget(selection_frame)
            
            # Settings and preferences section
            preferences_frame = self._create_preferences_section()
            layout.addWidget(preferences_frame)
            
            # Enhanced button section
            button_frame = self._create_button_section()
            layout.addWidget(button_frame)
            
            # Get screen geometry for proper sizing
            from PyQt5.QtWidgets import QApplication, QDesktopWidget
            desktop = QApplication.desktop()
            screen_geometry = desktop.screenGeometry()
            
            # Calculate appropriate dialog size (40% of screen width, max 800px)
            dialog_width = min(800, int(screen_geometry.width() * 0.4))
            dialog_height = min(700, int(screen_geometry.height() * 0.6))
            
            # Ensure minimum readable size
            dialog_width = max(dialog_width, 750)
            dialog_height = max(dialog_height, 650)
            
            # Set dialog size with proper constraints
            self.dialog.setFixedSize(dialog_width, dialog_height)
            self.dialog.adjustSize()
            
            # Center dialog on screen
            if self.parent:
                parent_center_x = self.parent.x() + (self.parent.width() // 2)
                parent_center_y = self.parent.y() + (self.parent.height() // 2)
                self.dialog.move(
                    parent_center_x - (dialog_width // 2),
                    parent_center_y - (dialog_height // 2)
                )
            else:
                # Center on screen if no parent
                screen_center_x = screen_geometry.width() // 2
                screen_center_y = screen_geometry.height() // 2
                self.dialog.move(
                    screen_center_x - (dialog_width // 2),
                    screen_center_y - (dialog_height // 2)
                )
            
            # Show dialog and handle result with comprehensive error handling
            return self._execute_dialog()
            
        except Exception as e:
            self.logger.error(f"Error creating interface selection dialog: {e}")
            self._show_fallback_dialog()
            return True  # Default to continuing with fallback
    
    def _apply_dialog_styling(self):
        """Apply simplified styling to the dialog to ensure text visibility."""
        try:
            self.dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 12px;
                }
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    background-color: #ffffff;
                }
                QRadioButton {
                    font-weight: bold;
                    font-size: 14px;
                    color: #2c3e50;
                    spacing: 10px;
                    padding: 8px;
                    background-color: transparent;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    border: 2px solid #bdc3c7;
                    background-color: #ffffff;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #3498db;
                    background-color: #3498db;
                }
                QRadioButton::indicator:hover {
                    border: 2px solid #3498db;
                }
                QPushButton {
                    font-weight: bold;
                    font-size: 14px;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 6px;
                    border: none;
                    min-width: 120px;
                    min-height: 40px;
                }
                QPushButton#primary {
                    background-color: #3498db;
                }
                QPushButton#primary:hover {
                    background-color: #2980b9;
                }
                QPushButton#secondary {
                    background-color: #95a5a6;
                }
                QPushButton#secondary:hover {
                    background-color: #7f8c8d;
                }
                QCheckBox {
                    font-size: 12px;
                    color: #2c3e50;
                    background-color: transparent;
                }
                QTextEdit {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    padding: 8px;
                    font-size: 11px;
                    color: #495057;
                }
            """)
        except Exception as e:
            self.logger.warning(f"Failed to apply dialog styling: {e}")
    
    def _create_title_section(self):
        """Create enhanced title section with branding."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
        
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Main title
        title = QLabel("Welcome to Richard's File Utilities")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; margin: 10px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Choose your preferred interface mode to get started")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #ecf0f1; font-size: 13px; margin: 5px;")
        layout.addWidget(subtitle)
        
        return frame
    
    def _create_recommendation_section(self):
        """Create workflow detection and recommendation section."""
        from PyQt5.QtWidgets import QGroupBox, QLabel, QTextEdit, QVBoxLayout
        
        workflow_group = QGroupBox("📊 Intelligent Interface Recommendation")
        workflow_layout = QVBoxLayout(workflow_group)
        
        try:
            detected_workflow = self._detect_initial_workflow()
            recommendation = self._get_interface_recommendation(detected_workflow)
            
            recommendation_label = QLabel(f"🎯 Recommended: {recommendation['name']}")
            recommendation_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px; margin: 5px;")
            workflow_layout.addWidget(recommendation_label)
            
            reason_text = QTextEdit()
            reason_text.setPlainText(recommendation['reason'])
            reason_text.setMaximumHeight(90)
            reason_text.setReadOnly(True)
            workflow_layout.addWidget(reason_text)
            
        except Exception as e:
            self.logger.warning(f"Error creating recommendation section: {e}")
            fallback_label = QLabel("💡 Both interfaces are powerful - choose based on your workflow preference")
            fallback_label.setStyleSheet("color: #f39c12; font-weight: bold; margin: 5px;")
            workflow_layout.addWidget(fallback_label)
        
        return workflow_group
    
    def _create_selection_section(self):
        """Create enhanced interface selection section."""
        from PyQt5.QtWidgets import (QButtonGroup, QFrame, QGroupBox,
                                     QHBoxLayout, QLabel, QRadioButton,
                                     QVBoxLayout)
        
        selection_group = QGroupBox("🖥️ Select Your Interface Mode")
        selection_layout = QVBoxLayout(selection_group)
        
        # Create button group for mutual exclusion
        self.button_group = QButtonGroup()
        
        # Dialog Hub option with enhanced styling
        dialog_frame = self._create_interface_option(
            "dialog_hub",
            "📋 Dialog-Based Hub Interface",
            "• Comprehensive tabbed interface\n• All tools organized by category\n• Professional workflow design\n• Perfect for organized task management\n• Familiar traditional interface",
            "#3498db"
        )
        selection_layout.addWidget(dialog_frame)
        
        # Multi-pane option with enhanced styling
        pane_frame = self._create_interface_option(
            "multi_pane",
            "🔀 Multi-Pane Explorer Layout",
            "• Simultaneous multiple views\n• Resizable, dockable panels\n• File trees and property panels\n• Perfect for complex operations\n• Modern multi-window experience",
            "#e74c3c"
        )
        selection_layout.addWidget(pane_frame)
        
        return selection_group
    
    def _create_interface_option(self, option_id, title, description, color):
        """Create a styled interface option frame."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QFrame, QLabel, QRadioButton, QVBoxLayout
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                background-color: #ffffff;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Radio button with enhanced styling
        radio = QRadioButton(title)
        # Ensure text is visible with simplified styling
        radio.setStyleSheet(f"""
            QRadioButton {{
                color: {color}; 
                font-size: 14px;
                font-weight: bold;
                spacing: 10px;
                padding: 8px;
                margin: 3px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #bdc3c7;
                background-color: white;
                margin-right: 8px;
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {color};
                background-color: {color};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {color};
            }}
        """)
        
        # Ensure text is set and visible
        radio.setText(title)  # Explicitly set text again to ensure it's displayed
        
        if option_id == "dialog_hub":
            self.dialog_radio = radio
            radio.setChecked(True)  # Default selection
        else:
            self.pane_radio = radio
        
        self.button_group.addButton(radio)
        layout.addWidget(radio)
        
        # Description with better spacing
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            margin-left: 25px; 
            color: #555; 
            font-size: 11px; 
            line-height: 1.4;
            padding-top: 5px;
            padding-bottom: 10px;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return frame
    
    def _create_preferences_section(self):
        """Create preferences and settings section."""
        from PyQt5.QtWidgets import QCheckBox, QFrame, QLabel, QVBoxLayout
        
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        # Remember choice checkbox
        self.remember_checkbox = QCheckBox("🔒 Remember my choice for future sessions")
        self.remember_checkbox.setChecked(True)
        self.remember_checkbox.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.remember_checkbox)
        
        # Additional info
        info_label = QLabel("💡 You can always change your interface mode from the Interface menu")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px; margin-top: 5px;")
        layout.addWidget(info_label)
        
        return frame
    
    def _create_button_section(self):
        """Create enhanced button section with proper styling."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QPushButton,
                                     QSizePolicy, QSpacerItem)
        
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Add spacer
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("secondary")
        cancel_button.setText("Cancel")  # Ensure text is explicitly set
        cancel_button.setMinimumSize(100, 35)
        cancel_button.clicked.connect(self._handle_cancel)
        layout.addWidget(cancel_button)
        
        # Continue button
        continue_button = QPushButton("Continue")
        continue_button.setObjectName("primary")
        continue_button.setText("Continue")  # Ensure text is explicitly set
        continue_button.setMinimumSize(100, 35)
        continue_button.setDefault(True)
        continue_button.clicked.connect(self._handle_continue)
        layout.addWidget(continue_button)
        
        return frame
    
    def _execute_dialog(self):
        """Execute the dialog with comprehensive error handling."""
        try:
            # Ensure proper layout before showing
            self.dialog.updateGeometry()
            self.dialog.update()
            self.dialog.repaint()
            
            # Process events to ensure proper rendering
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            result = self.dialog.exec_()
            
            if result == self.dialog.Accepted:
                # Process user selection
                if self.dialog_radio and self.dialog_radio.isChecked():
                    self.selected_mode = InterfaceMode.DIALOG_HUB
                elif self.pane_radio and self.pane_radio.isChecked():
                    self.selected_mode = InterfaceMode.MULTI_PANE
                else:
                    # Fallback to default
                    self.selected_mode = InterfaceMode.DIALOG_HUB
                
                if self.remember_checkbox:
                    self.remember_choice = self.remember_checkbox.isChecked()
                else:
                    self.remember_choice = False
                
                self.logger.info(f"User selected interface mode: "
                                f"{self.selected_mode.value}")
                return True
            else:
                # User cancelled or closed dialog
                self.logger.info("User cancelled interface selection, "
                                "using default")
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                return False  # User cancelled
                
        except Exception as e:
            self.logger.error(f"Error executing interface selection "
                             f"dialog: {e}")
            self._show_fallback_dialog()
            return False  # Error occurred
    
    def _handle_continue(self):
        """Handle continue button click with validation."""
        try:
            # Validate selection
            if not (self.dialog_radio.isChecked() or self.pane_radio.isChecked()):
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self.dialog, "Selection Required", 
                                  "Please select an interface mode before continuing.")
                return
            
            self.dialog.accept()
            
        except Exception as e:
            self.logger.error(f"Error handling continue action: {e}")
            self.dialog.accept()  # Continue anyway
    
    def _handle_cancel(self):
        """Handle cancel button click with fallback to default interface."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            result = QMessageBox.question(
                self.dialog, 
                "Use Default Interface", 
                "Would you like to use the default Dialog Hub interface instead?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if result == QMessageBox.Yes:
                self.logger.info("User chose default interface mode")
                # Set default values and accept dialog
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                if self.dialog_radio:
                    self.dialog_radio.setChecked(True)
                if self.remember_checkbox:
                    self.remember_checkbox.setChecked(False)
                self.dialog.accept()
            else:
                # User chose not to use default, stay in dialog
                self.logger.info("User declined default interface, staying in dialog")
                
        except Exception as e:
            self.logger.error(f"Error handling cancel action: {e}")
            # Fallback to default interface and continue
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
            self.dialog.accept()
    
    def _handle_close_event(self, event):
        """Handle dialog close event to prevent accidental closure."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            result = QMessageBox.question(
                self.dialog,
                "Use Default Interface",
                "Would you like to use the default Dialog Hub interface?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if result == QMessageBox.Yes:
                self.logger.info("User chose default interface from close event")
                # Set default values and accept dialog
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                if self.dialog_radio:
                    self.dialog_radio.setChecked(True)
                if self.remember_checkbox:
                    self.remember_checkbox.setChecked(False)
                event.accept()
                self.dialog.accept()
            else:
                # User chose not to use default, prevent close
                self.logger.info("User declined default interface, "
                               "preventing dialog close")
                event.ignore()
                
        except Exception as e:
            self.logger.error(f"Error handling close event: {e}")
            # Fallback to default interface and continue
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
            event.accept()
            self.dialog.accept()
    
    def _show_fallback_dialog(self):
        """Show simple fallback dialog if main dialog fails."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            QMessageBox.information(
                self.parent,
                "Interface Selection",
                "Starting with Dialog-Based Hub Interface.\n\n"
                "You can switch to Multi-Pane Explorer from the Interface menu."
            )
            
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
            
        except Exception as e:
            self.logger.error(f"Error showing fallback dialog: {e}")
            # Ultimate fallback - just set defaults
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
    
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
            
            # Initialize logging system first
            self.logger = logging.getLogger('RFU.MainWindow')
            self.logger.info("Initializing RFU Main Window with dual interface system")
            
            # Set basic window properties with proper sizing
            self.setWindowTitle(APP_NAME)
            
            # Configure window size and positioning
            self._configure_window_geometry()
            
            # Initialize core systems
            self._initialize_core_systems()
            
            # Show startup dialog and determine interface mode BEFORE UI initialization
            self.logger.info("Determining interface mode through startup dialog")
            self._determine_interface_mode()
            
            # Initialize the selected interface
            self.logger.info(f"Initializing {self.current_interface_mode.value} interface")
            self._initialize_interface()
            
            # Log successful initialization
            self.logger.info(f"RFU Main Window initialized successfully with {self.current_interface_mode.value} interface")
        
        def _configure_window_geometry(self):
            """Configure window size and positioning based on screen geometry."""
            from PyQt5.QtWidgets import QApplication, QDesktopWidget
            
            desktop = QApplication.desktop()
            screen_geometry = desktop.screenGeometry()
            
            # Calculate window size (70% of screen width, 80% of screen height, with constraints)
            window_width = min(1200, int(screen_geometry.width() * 0.7))
            window_height = min(900, int(screen_geometry.height() * 0.8))
            
            # Ensure minimum usable size
            window_width = max(window_width, 1000)
            window_height = max(window_height, 750)
            
            # Set maximum size to prevent window from becoming too large
            self.setMaximumSize(
                min(1400, int(screen_geometry.width() * 0.9)),
                min(1000, int(screen_geometry.height() * 0.9))
            )
            
            # Set minimum size for usability
            self.setMinimumSize(900, 650)
            
            # Set initial geometry with calculated size
            start_x = max(50, (screen_geometry.width() - window_width) // 2)
            start_y = max(50, (screen_geometry.height() - window_height) // 2)
            self.setGeometry(start_x, start_y, window_width, window_height)
        
        def _initialize_core_systems(self):
            """Initialize core application systems and state management."""
            try:
                # Store references to opened windows
                self.opened_windows = {}
                
                # Interface mode management
                self.current_interface_mode = InterfaceMode.DIALOG_HUB  # Default fallback
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
                        self.logger.info("Database system initialized successfully")
                    except Exception as e:
                        self.logger.warning(f"Database initialization failed: {e}")
                        self.database_available = False
                        self.db_manager = None
                else:
                    self.db_manager = None
                    self.logger.info("Database system not available")
                
                # Initialize configuration manager
                try:
                    from src.config_manager import get_config_manager
                    self.config_manager = get_config_manager()
                    self._setup_interface_configuration()
                    self.logger.info("Configuration manager initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Configuration manager initialization failed: {e}")
                    self.config_manager = None
                
                self.logger.info("Core systems initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error initializing core systems: {e}")
                # Set minimal fallback state
                self.opened_windows = {}
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.database_available = False
                self.db_manager = None
                self.config_manager = None
        
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
            """Determine which interface mode to use with comprehensive startup dialog logic."""
            try:
                # Initialize default mode
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                
                if not self.config_manager:
                    self.logger.warning("Configuration manager not available, showing startup dialog")
                    self._show_interface_selection_dialog()
                    return
                
                # Check if user has saved preference and doesn't want to see dialog
                saved_mode = self.config_manager.get_setting('interface_mode', 'current_mode')
                show_startup = self.config_manager.get_setting('interface_mode', 'show_startup_dialog', True)
                remember_choice = self.config_manager.get_setting('interface_mode', 'remember_choice', False)
                
                self.logger.info(f"Startup configuration - saved_mode: {saved_mode}, show_startup: {show_startup}, remember_choice: {remember_choice}")
                
                # If user has saved preference and doesn't want to see dialog
                if saved_mode and remember_choice and not show_startup:
                    try:
                        self.current_interface_mode = InterfaceMode(saved_mode)
                        self.logger.info(f"Using saved interface mode: {self.current_interface_mode.value}")
                        return
                    except ValueError as e:
                        self.logger.warning(f"Invalid saved interface mode '{saved_mode}': {e}")
                        # Fall through to show dialog
                
                # Show interface selection dialog for first-time users or when requested
                self.logger.info("Showing interface selection dialog")
                self._show_interface_selection_dialog()
                
            except Exception as e:
                self.logger.error(f"Error determining interface mode: {e}")
                # Ultimate fallback
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.logger.info("Using fallback interface mode: DIALOG_HUB")
        
        def _show_interface_selection_dialog(self):
            """Show enhanced interface selection dialog on startup with comprehensive error handling."""
            try:
                self.logger.info("Initializing interface selection dialog")
                
                # Ensure QApplication is available for dialog creation
                from PyQt5.QtWidgets import QApplication
                if not QApplication.instance():
                    self.logger.error("QApplication not available for dialog creation")
                    self._handle_dialog_fallback()
                    return
                
                # Create and show the enhanced dialog
                dialog = InterfaceSelectionDialog(self)
                
                # Show dialog with proper error handling
                dialog_result = dialog.show_selection_dialog()
                
                if dialog_result:
                    # Process user selection
                    self.current_interface_mode = dialog.selected_mode
                    self.logger.info(f"User selected interface mode: {self.current_interface_mode.value}")
                    
                    # Save preferences if requested and config manager available
                    if dialog.remember_choice and self.config_manager:
                        try:
                            self.config_manager.set_setting('interface_mode', 'current_mode', 
                                                           self.current_interface_mode.value)
                            self.config_manager.set_setting('interface_mode', 'remember_choice', True)
                            self.config_manager.set_setting('interface_mode', 'show_startup_dialog', False)
                            self.logger.info("Saved user interface preferences")
                        except Exception as config_error:
                            self.logger.warning(f"Failed to save interface preferences: {config_error}")
                    
                    # Track dialog usage for analytics
                    if self.database_available and self.db_manager:
                        try:
                            self._track_interface_selection(self.current_interface_mode.value, dialog.remember_choice)
                        except Exception as db_error:
                            self.logger.warning(f"Failed to track interface selection: {db_error}")
                else:
                    # Dialog cancelled or failed
                    self.logger.warning("Interface selection dialog cancelled or failed")
                    self._handle_dialog_fallback()
                    
            except ImportError as ie:
                self.logger.error(f"PyQt5 import error during dialog creation: {ie}")
                self._handle_dialog_fallback()
            except Exception as e:
                self.logger.error(f"Unexpected error showing interface selection dialog: {e}")
                self._handle_dialog_fallback()
        
        def _handle_dialog_fallback(self):
            """Handle fallback when dialog creation or interaction fails."""
            try:
                self.logger.info("Using fallback interface selection logic")
                
                # Try to detect suitable interface based on system characteristics
                if self._detect_developer_environment():
                    self.current_interface_mode = InterfaceMode.MULTI_PANE
                    self.logger.info("Detected developer environment, defaulting to Multi-Pane Explorer")
                else:
                    self.current_interface_mode = InterfaceMode.DIALOG_HUB
                    self.logger.info("Detected general use environment, defaulting to Dialog Hub")
                
                # Show simple notification if possible
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "Interface Mode Selected",
                        f"Starting with {self.current_interface_mode.value.replace('_', ' ').title()} mode.\n\n"
                        "You can change interface modes from the Interface menu."
                    )
                except Exception:
                    # Ultimate fallback - just print message
                    print(f"Starting with {self.current_interface_mode.value.replace('_', ' ').title()} interface mode")
                    
            except Exception as e:
                self.logger.error(f"Error in dialog fallback handling: {e}")
                # Ultimate fallback
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
        
        def _detect_developer_environment(self):
            """Detect if the current environment suggests developer usage."""
            try:
                import os
                import subprocess
                from pathlib import Path
                
                developer_indicators = 0
                
                # Check for development directories
                home_dir = Path.home()
                dev_dirs = ['src', 'projects', 'code', 'development', 'workspace', 'git', 'repos']
                for dev_dir in dev_dirs:
                    if (home_dir / dev_dir).exists():
                        developer_indicators += 1
                
                # Check for development tools
                dev_tools = ['git', 'python', 'node', 'npm', 'code', 'vim', 'code.exe']
                for tool in dev_tools:
                    try:
                        subprocess.check_output(['where' if os.name == 'nt' else 'which', tool], 
                                               stderr=subprocess.STDOUT)
                        developer_indicators += 1
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        pass
                
                # Check current directory for project files
                current_dir = Path.cwd()
                project_files = ['.git', 'package.json', 'requirements.txt', 'Makefile', '.gitignore', 'src']
                for project_file in project_files:
                    if (current_dir / project_file).exists():
                        developer_indicators += 1
                
                # If we find 3 or more indicators, likely a developer environment
                return developer_indicators >= 3
                
            except Exception as e:
                self.logger.warning(f"Error detecting developer environment: {e}")
                return False
        
        def _track_interface_selection(self, mode, remember_choice):
            """Track interface selection for analytics and improvement."""
            try:
                if not self.database_available or not self.db_manager:
                    return
                
                # Record interface selection event
                query = """
                    INSERT OR REPLACE INTO interface_usage 
                    (selection_date, interface_mode, remember_choice, session_id)
                    VALUES (datetime('now'), ?, ?, ?)
                """
                
                session_id = f"{self.session_start_time.isoformat()}_{id(self)}"
                params = (mode, remember_choice, session_id)
                
                self.db_manager.execute_update(query, params)
                self.logger.debug(f"Tracked interface selection: {mode}")
                
            except Exception as e:
                self.logger.warning(f"Failed to track interface selection: {e}")
        
        def _initialize_interface(self):
            """Initialize the selected interface mode with comprehensive error handling."""
            try:
                self.logger.info(f"Initializing interface mode: {self.current_interface_mode.value}")
                
                if self.current_interface_mode == InterfaceMode.MULTI_PANE:
                    success = self._initialize_multi_pane_interface()
                    if not success:
                        self.logger.warning("Multi-pane interface initialization failed, falling back to dialog hub")
                        self.current_interface_mode = InterfaceMode.DIALOG_HUB
                        self._initialize_dialog_hub_interface()
                else:
                    self._initialize_dialog_hub_interface()
                
                # Setup interface switching menu
                self._setup_interface_switching_menu()
                
                self.logger.info(f"Interface initialization completed: {self.current_interface_mode.value}")
                
            except Exception as e:
                self.logger.error(f"Critical error during interface initialization: {e}")
                self._handle_interface_initialization_failure()
        
        def _handle_interface_initialization_failure(self):
            """Handle critical interface initialization failures with emergency fallback."""
            try:
                self.logger.warning("Attempting emergency interface fallback")
                
                # Create minimal emergency interface
                from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout,
                                             QWidget)
                
                emergency_widget = QWidget()
                layout = QVBoxLayout(emergency_widget)
                
                # Error message
                error_label = QLabel("Interface initialization failed. Using emergency mode.")
                error_label.setStyleSheet("color: red; font-weight: bold; padding: 20px;")
                layout.addWidget(error_label)
                
                # Retry button
                retry_button = QPushButton("Retry Interface Initialization")
                retry_button.clicked.connect(self._retry_interface_initialization)
                layout.addWidget(retry_button)
                
                # Exit button
                exit_button = QPushButton("Exit Application")
                exit_button.clicked.connect(self.close)
                layout.addWidget(exit_button)
                
                self.setCentralWidget(emergency_widget)
                self.setWindowTitle(f"{APP_NAME} - Emergency Mode")
                
                self.logger.info("Emergency interface fallback activated")
                
            except Exception as emergency_error:
                self.logger.critical(f"Emergency fallback failed: {emergency_error}")
                # Ultimate fallback - show message and exit
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        None, 
                        "Critical Error", 
                        f"Application failed to initialize properly.\n\nError: {emergency_error}\n\nThe application will now exit."
                    )
                except Exception:
                    print(f"CRITICAL ERROR: Application failed to initialize. Error: {emergency_error}")
                sys.exit(1)
        
        def _retry_interface_initialization(self):
            """Retry interface initialization after emergency fallback."""
            try:
                self.logger.info("Retrying interface initialization")
                
                # Reset interface state
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.multi_pane_explorer = None
                self.dialog_hub_widget = None
                
                # Try to initialize again
                self._initialize_interface()
                
            except Exception as e:
                self.logger.error(f"Interface retry failed: {e}")
                self._handle_interface_initialization_failure()
        
        def _initialize_dialog_hub_interface(self):
            """Initialize the dialog-based hub interface with full tabbed functionality."""
            # Ensure the main window is visible
            self.show()
            
            self.setWindowTitle(f"{APP_NAME} - Dialog Hub Interface")
            
            # Store reference to dialog hub widget for later restoration
            if hasattr(self, 'dialog_hub_widget') and self.dialog_hub_widget:
                self.setCentralWidget(self.dialog_hub_widget)
            else:
                self.init_ui()
                self.dialog_hub_widget = self.centralWidget()
        
        def _initialize_multi_pane_interface(self):
            """Initialize the multi-pane explorer interface embedded in the main window."""
            try:
                self.logger.info("Initializing multi-pane explorer interface")
                
                # Store current dialog hub widget if switching
                current_widget = self.centralWidget()
                if current_widget and not hasattr(self, 'dialog_hub_widget'):
                    self.dialog_hub_widget = current_widget
                    self.logger.debug("Stored current dialog hub widget for future restoration")
                
                # Create or reuse the multi-pane explorer widget
                if not self.multi_pane_explorer:
                    try:
                        # Try to import and create the multi-pane explorer widget
                        try:
                            from src.file_explorer.multi_pane_explorer import \
                                MultiPaneFileExplorer

                            # Create instance as widget, not window
                            self.multi_pane_explorer = MultiPaneFileExplorer()
                            
                            # Embed properly in main window
                            self.multi_pane_explorer.setWindowFlags(Qt.Widget)
                            
                            self.logger.info("Multi-pane explorer widget created successfully")
                        except ImportError:
                            # Fall back to simplified widget if import fails
                            self.multi_pane_explorer = self._create_simple_multi_pane_widget()
                            self.logger.warning("Import failed, using simplified widget")
                    except Exception as ce:
                        self.logger.error(f"Failed to create multi-pane explorer: {ce}")
                        self._create_fallback_multi_pane()
                        return True  # Fallback is still a success
                
                # Embed the multi-pane explorer in the main window
                self.setCentralWidget(self.multi_pane_explorer)
                self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer")
                
                # Ensure the main window stays visible
                self.show()
                
                self.logger.info("Multi-pane interface initialization completed successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error initializing multi-pane interface: {e}")
                self._create_fallback_multi_pane()
                return False  # Return False when falling back due to error

        
        def _create_simple_multi_pane_widget(self):
            """Create a proper multi-pane widget that can be embedded in the main window."""
            from PyQt5.QtCore import QDir
            from PyQt5.QtWidgets import (QFileSystemModel, QFrame, QHBoxLayout,
                                         QHeaderView, QSplitter, QTreeView,
                                         QVBoxLayout)

            # Create main container widget
            main_widget = QWidget()
            main_layout = QHBoxLayout(main_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            
            # Create horizontal splitter for multi-pane layout
            splitter = QSplitter(Qt.Horizontal)
            
            # Create two file browser panes
            for i in range(2):
                pane = self._create_file_browser_pane(f"Pane {i+1}")
                splitter.addWidget(pane)
            
            # Set equal sizes for both panes
            splitter.setSizes([400, 400])
            
            main_layout.addWidget(splitter)
            
            # Add some basic styling
            main_widget.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                }
                QFrame {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                QTreeView {
                    border: none;
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                }
                QTreeView::item:selected {
                    background-color: #0078d4;
                    color: white;
                }
            """)
            
            return main_widget
        
        def _create_file_browser_pane(self, title):
            """Create a single file browser pane."""
            from PyQt5.QtCore import QDir
            from PyQt5.QtWidgets import (QFileSystemModel, QFrame, QHBoxLayout,
                                         QLabel, QPushButton, QTreeView,
                                         QVBoxLayout)

            # Create frame for the pane
            pane_frame = QFrame()
            pane_layout = QVBoxLayout(pane_frame)
            pane_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add title and navigation
            header_layout = QHBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
            header_layout.addWidget(title_label)
            
            # Add home button
            home_button = QPushButton("🏠 Home")
            home_button.setMaximumWidth(80)
            home_button.clicked.connect(lambda: self._navigate_to_home(tree_view))
            header_layout.addWidget(home_button)
            
            pane_layout.addLayout(header_layout)
            
            # Create tree view with file system model
            tree_view = QTreeView()
            file_model = QFileSystemModel()
            file_model.setRootPath(QDir.rootPath())
            
            tree_view.setModel(file_model)
            tree_view.setRootIndex(file_model.index(str(Path.home())))
            
            # Configure tree view
            tree_view.setAlternatingRowColors(True)
            tree_view.setSortingEnabled(True)
            tree_view.sortByColumn(0, Qt.AscendingOrder)
            
            # Adjust column widths
            header = tree_view.header()
            header.resizeSection(0, 250)  # Name column
            header.resizeSection(1, 100)  # Size column
            header.resizeSection(2, 80)   # Type column
            header.resizeSection(3, 120)  # Date column
            
            pane_layout.addWidget(tree_view)
            
            return pane_frame
        
        def _navigate_to_home(self, tree_view):
            """Navigate tree view to home directory."""
            if hasattr(tree_view, 'model') and tree_view.model():
                home_index = tree_view.model().index(str(Path.home()))
                tree_view.setRootIndex(home_index)
        
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
            info_label = QLabel("Full multi-pane explorer not available.\nUsing simplified interface.")
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
            self.current_interface_mode = new_mode
            
            # Update configuration
            if self.config_manager:
                try:
                    self.config_manager.set_setting('interface_mode', 'current_mode', new_mode.value)
                except AttributeError:
                    pass
            
            # Track switch for analytics
            self.interface_switch_count += 1
            
            # Perform transition (no animation for window switching)
            self._immediate_interface_transition(new_mode)
            
            # Emit signal
            self.interface_switched.emit(new_mode.value)

        
        def _immediate_interface_transition(self, new_mode):
            """Perform immediate interface transition without animation."""
            if new_mode == InterfaceMode.MULTI_PANE:
                self._initialize_multi_pane_interface()
            else:
                self._initialize_dialog_hub_interface()
            
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
        
        def closeEvent(self, event):
            """Handle application close event - ensure all windows are properly closed."""
            try:
                # Save configuration if available
                if self.config_manager:
                    try:
                        # Save current interface mode
                        self.config_manager.set_setting('interface_mode', 'current_mode', 
                                                       self.current_interface_mode.value)
                    except Exception as e:
                        self.logger.warning(f"Error saving configuration: {e}")
                
                # Accept the close event
                event.accept()
                
            except Exception as e:
                self.logger.error(f"Error during application close: {e}")
                event.accept()  # Close anyway
        def launch_tool(self, tool_name, module_name=None, class_name=None):
            """Enhanced tool launch with tracking."""
            # Track tool usage
            self.tool_usage_count += 1
            
            # Emit signal for tracking
            self.tool_launched.emit(tool_name)
            
            # Show placeholder for demonstration
            QMessageBox.information(
                self, "Tool Launch", 
                f"Launching {tool_name}...\n\n"
                f"Current Interface: {self.current_interface_mode.value}\n"
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
                    (PDF_UTILITIES, "Comprehensive PDF tools", self.open_pdf_tools),
                    (EXTRACT_LINKS, "Extract links from PDF files", self.open_pdf_links),
                    (PAGE_ADMINISTRATION, "Manage PDF pages", self.open_pdf_pages),
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
                (PDF_UTILITIES, "Comprehensive PDF tools", self.open_pdf_tools),
                (EXTRACT_LINKS, "Extract links from PDF files", self.open_pdf_links),
                (PAGE_ADMINISTRATION, "Manage PDF pages", self.open_pdf_pages),
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
        def open_pdf_tools(self): self.launch_tool(PDF_UTILITIES)
        def open_pdf_links(self): self.launch_tool(EXTRACT_LINKS)
        def open_pdf_pages(self): self.launch_tool(PAGE_ADMINISTRATION)
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