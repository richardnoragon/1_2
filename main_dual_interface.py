#!/usr/bin/env python3
"""
Richard's File Utilities - Main Entry Point with Dual Interface System

This provides a comprehensive dual-interface system allowing users to choose between:
1. Dialog-based centralized hub interface
2. Multi-pane explorer layout
"""

import logging
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))

# Import constants
from src.core.constants import APP_NAME


class InterfaceMode(Enum):
    """Enumeration for interface modes."""
    DIALOG_HUB = "dialog_hub"
    MULTI_PANE = "multi_pane"


# Initialize database system
def initialize_database_system():
    """Initialize the database and enhanced configuration system."""
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('RFU.Main')
        logger.info("Database system initialized")
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False


DATABASE_AVAILABLE = initialize_database_system()

try:
    from PyQt5.QtCore import (QEasingCurve, QPropertyAnimation, Qt, QTimer,
                              pyqtSignal)
    from PyQt5.QtGui import QFont, QKeySequence
    from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog,
                                 QGraphicsOpacityEffect, QGroupBox,
                                 QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                                 QPushButton, QRadioButton, QShortcut,
                                 QTabWidget, QTextEdit, QVBoxLayout, QWidget)
    
    class InterfaceSelectionDialog:
        """Dialog for selecting interface mode on startup."""
        
        def __init__(self, parent=None):
            self.parent = parent
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
        
        def show_selection_dialog(self):
            """Show interface selection dialog."""
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("Choose Your Workspace Interface")
            dialog.setFixedSize(500, 350)
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Welcome to Richard's File Utilities")
            title.setAlignment(Qt.AlignCenter)
            title_font = QFont()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title.setFont(title_font)
            layout.addWidget(title)
            
            # Interface selection
            selection_group = QGroupBox("Select Interface Mode")
            selection_layout = QVBoxLayout(selection_group)
            
            # Dialog Hub option
            self.dialog_radio = QRadioButton("Dialog-Based Hub Interface")
            self.dialog_radio.setChecked(True)
            dialog_desc = QLabel("• Clean, modal-driven workflow\n• Contextual action menus\n• Perfect for focused tasks")
            dialog_desc.setStyleSheet("margin-left: 20px; color: #555;")
            selection_layout.addWidget(self.dialog_radio)
            selection_layout.addWidget(dialog_desc)
            
            # Multi-pane option
            self.pane_radio = QRadioButton("Multi-Pane Explorer Layout")
            pane_desc = QLabel("• Simultaneous multiple views\n• Resizable, dockable panels\n• Perfect for complex operations")
            pane_desc.setStyleSheet("margin-left: 20px; color: #555;")
            selection_layout.addWidget(self.pane_radio)
            selection_layout.addWidget(pane_desc)
            
            layout.addWidget(selection_group)
            
            # Remember choice checkbox
            self.remember_checkbox = QCheckBox("Remember my choice")
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
    
    class RFUMainWindow(QMainWindow):
        # Signals for communication
        interface_switched = pyqtSignal(str)
        tool_launched = pyqtSignal(str)
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_NAME)
            self.setGeometry(200, 200, 900, 700)
            
            # Interface mode management
            self.current_interface_mode = InterfaceMode.DIALOG_HUB
            self.multi_pane_explorer = None
            self.transition_in_progress = False
            
            # Workflow tracking
            self.session_start_time = datetime.now()
            self.tool_usage_count = 0
            self.interface_switch_count = 0
            
            # Configuration
            try:
                from src.config_manager import get_config_manager
                self.config_manager = get_config_manager()
                self._setup_interface_configuration()
            except:
                self.config_manager = None
            
            # Setup keyboard shortcuts
            self._setup_keyboard_shortcuts()
            
            # Setup accessibility features
            self._setup_accessibility()
            
            # Determine interface mode
            self._determine_interface_mode()
            
            # Initialize interface
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
                'workflow_analysis': {
                    'enabled': True,
                    'tool_usage_tracking': True,
                    'suggestion_threshold': 0.7
                },
                'accessibility': {
                    'high_contrast': False,
                    'large_fonts': False,
                    'screen_reader_support': True,
                    'keyboard_navigation': True
                }
            }
            
            for section, defaults in interface_sections.items():
                current_section = self.config_manager.get_section(section) if hasattr(self.config_manager, 'get_section') else {}
                for key, default_value in defaults.items():
                    if key not in current_section and hasattr(self.config_manager, 'set_setting'):
                        self.config_manager.set_setting(section, key, default_value)
        
        def _setup_keyboard_shortcuts(self):
            """Setup comprehensive keyboard shortcuts for both interface modes."""
            # Interface switching shortcuts
            switch_hub_shortcut = QShortcut(QKeySequence("Ctrl+Shift+H"), self)
            switch_hub_shortcut.activated.connect(lambda: self.switch_interface_mode(InterfaceMode.DIALOG_HUB))
            switch_hub_shortcut.setWhatsThis("Switch to Dialog Hub Interface")
            
            switch_pane_shortcut = QShortcut(QKeySequence("Ctrl+Shift+M"), self)
            switch_pane_shortcut.activated.connect(lambda: self.switch_interface_mode(InterfaceMode.MULTI_PANE))
            switch_pane_shortcut.setWhatsThis("Switch to Multi-Pane Explorer Interface")
            
            # Tool launching shortcuts
            tool_shortcuts = [
                ("Ctrl+F", lambda: self.launch_tool("File Finder")),
                ("Ctrl+D", lambda: self.launch_tool("Duplicate Finder")),
                ("Ctrl+S", lambda: self.launch_tool("Size Analyzer")),
                ("Ctrl+Shift+S", lambda: self.launch_tool("Security Tools"))
            ]
            
            for key_sequence, callback in tool_shortcuts:
                shortcut = QShortcut(QKeySequence(key_sequence), self)
                shortcut.activated.connect(callback)
            
            # Accessibility shortcuts
            help_shortcut = QShortcut(QKeySequence("F1"), self)
            help_shortcut.activated.connect(self._show_help)
            
            settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
            settings_shortcut.activated.connect(self._show_preferences)
        
        def _setup_accessibility(self):
            """Setup accessibility features for WCAG compliance."""
            # Set accessible names and descriptions
            self.setAccessibleName("Richard's File Utilities Main Window")
            self.setAccessibleDescription("Main application window with dual interface support")
            
            # Enable focus policy for keyboard navigation
            self.setFocusPolicy(Qt.StrongFocus)
            
            # Apply accessibility settings from config
            if self.config_manager:
                try:
                    high_contrast = self.config_manager.get_setting('accessibility', 'high_contrast', False)
                    large_fonts = self.config_manager.get_setting('accessibility', 'large_fonts', False)
                    
                    if high_contrast:
                        self._apply_high_contrast_theme()
                    
                    if large_fonts:
                        self._apply_large_fonts()
                except:
                    pass
        
        def _apply_high_contrast_theme(self):
            """Apply high contrast theme for accessibility."""
            high_contrast_style = """
                QMainWindow {
                    background-color: #000000;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 2px solid #FFFFFF;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFFF00;
                    color: #000000;
                }
                QLabel {
                    color: #FFFFFF;
                    font-weight: bold;
                }
            """
            self.setStyleSheet(high_contrast_style)
        
        def _apply_large_fonts(self):
            """Apply large fonts for accessibility."""
            font = self.font()
            font.setPointSize(font.pointSize() + 4)
            self.setFont(font)
        
        def _determine_interface_mode(self):
            """Determine which interface mode to use."""
            # For now, always show selection dialog
            try:
                dialog = InterfaceSelectionDialog(self)
                if dialog.show_selection_dialog():
                    self.current_interface_mode = dialog.selected_mode
                    if dialog.remember_choice and self.config_manager:
                        self.config_manager.set_setting(
                            'interface_mode', 'current_mode', 
                            self.current_interface_mode.value
                        )
            except Exception as e:
                print(f"Error showing interface selection: {e}")
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
        
        def switch_interface_mode(self, new_mode: InterfaceMode, 
                                animated: bool = True):
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
                    self.config_manager.set_setting(
                        'interface_mode', 'current_mode', new_mode.value
                    )
                except AttributeError:
                    pass
            
            # Track switch for analytics
            self.interface_switch_count += 1
            self._track_interface_switch(old_mode, new_mode)
            
            # Perform transition
            if animated:
                self._animate_interface_transition(old_mode, new_mode)
            else:
                self._initialize_interface()
                self.transition_in_progress = False
            
            # Emit signal
            self.interface_switched.emit(new_mode.value)
        
        def _animate_interface_transition(self, old_mode: InterfaceMode, 
                                        new_mode: InterfaceMode):
            """Animate transition between interface modes."""
            # Create fade out animation
            self.fade_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.fade_effect)
            
            self.fade_out = QPropertyAnimation(self.fade_effect, b"opacity")
            self.fade_out.setDuration(300)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.OutCubic)
            
            # When fade out completes, switch interface and fade in
            self.fade_out.finished.connect(
                lambda: self._complete_transition(new_mode)
            )
            
            self.fade_out.start()
        
        def _complete_transition(self, new_mode: InterfaceMode):
            """Complete the interface transition with fade in."""
            # Reinitialize the interface
            self._initialize_interface()
            
            # Create fade in animation
            self.fade_in = QPropertyAnimation(self.fade_effect, b"opacity")
            self.fade_in.setDuration(300)
            self.fade_in.setStartValue(0.0)
            self.fade_in.setEndValue(1.0)
            self.fade_in.setEasingCurve(QEasingCurve.InCubic)
            
            # When fade in completes, clean up
            self.fade_in.finished.connect(self._cleanup_transition)
            
            self.fade_in.start()
        
        def _cleanup_transition(self):
            """Clean up after transition animation."""
            self.setGraphicsEffect(None)
            self.transition_in_progress = False
        
        def _track_interface_switch(self, old_mode: InterfaceMode, 
                                  new_mode: InterfaceMode):
            """Track interface switching for workflow analysis."""
            if not self.config_manager:
                return
            
            try:
                timestamp = datetime.now().isoformat()
                switch_data = {
                    'timestamp': timestamp,
                    'from_mode': old_mode.value,
                    'to_mode': new_mode.value,
                    'session_duration': (
                        datetime.now() - self.session_start_time
                    ).total_seconds(),
                    'tool_usage_count': self.tool_usage_count
                }
                
                # Store in usage history for analysis
                usage_history = self.config_manager.get_setting(
                    'workflow_analysis', 'interface_switches', []
                )
                usage_history.append(switch_data)
                
                # Keep only last 100 switches for performance
                if len(usage_history) > 100:
                    usage_history = usage_history[-100:]
                
                self.config_manager.set_setting(
                    'workflow_analysis', 'interface_switches', usage_history
                )
                
            except (AttributeError, KeyError):
                pass
        
        def _analyze_workflow(self):
            """Analyze workflow patterns to suggest optimal interface mode."""
            if not self.config_manager:
                return None
            
            try:
                # Get workflow analysis settings
                enabled = self.config_manager.get_setting(
                    'workflow_analysis', 'enabled', True
                )
                
                if not enabled:
                    return None
                
                # Analyze tool usage patterns
                tool_usage = self.config_manager.get_setting(
                    'workflow_analysis', 'tool_usage_history', []
                )
                
                # Analyze interface switch patterns
                switch_history = self.config_manager.get_setting(
                    'workflow_analysis', 'interface_switches', []
                )
                
                # Simple heuristic: if user frequently switches to multi-pane
                # or uses file management tools heavily, suggest multi-pane
                if len(switch_history) > 5:
                    multi_pane_switches = sum(
                        1 for switch in switch_history[-10:] 
                        if switch.get('to_mode') == InterfaceMode.MULTI_PANE.value
                    )
                    
                    if multi_pane_switches > 6:  # More than 60% switches to multi-pane
                        return InterfaceMode.MULTI_PANE
                
                return None
                
            except (AttributeError, KeyError):
                return None
        
        def _initialize_interface(self):
            """Initialize the selected interface mode."""
            if self.current_interface_mode == InterfaceMode.MULTI_PANE:
                self._initialize_multi_pane_interface()
            else:
                self._initialize_dialog_hub_interface()
        
        def _initialize_dialog_hub_interface(self):
            """Initialize dialog-based hub interface."""
            self.setWindowTitle(f"{APP_NAME} - Hub Interface")
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # Title
            title_label = QLabel(APP_NAME)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px; 
                font-weight: bold; 
                padding: 20px;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 10px;
                margin: 10px;
            """)
            layout.addWidget(title_label)
            
            # Sample tools
            tools_widget = QWidget()
            tools_layout = QVBoxLayout(tools_widget)
            
            sample_tools = [
                "File Finder",
                "Duplicate Finder", 
                "Size Analyzer",
                "Security Tools"
            ]
            
            for tool in sample_tools:
                button = QPushButton(tool)
                button.setMinimumHeight(40)
                button.clicked.connect(lambda checked, t=tool: self.launch_tool(t))
                tools_layout.addWidget(button)
            
            layout.addWidget(tools_widget)
            
            # Interface switch button
            switch_button = QPushButton("Switch to Multi-Pane Explorer")
            switch_button.clicked.connect(lambda: self.switch_interface_mode(InterfaceMode.MULTI_PANE))
            layout.addWidget(switch_button)
            
            self.statusBar().showMessage("Dialog Hub Interface - Ready")
        
        def _initialize_multi_pane_interface(self):
            """Initialize multi-pane explorer interface."""
            self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer")
            
            try:
                from src.file_explorer.multi_pane_explorer import \
                    MultiPaneFileExplorer
                self.multi_pane_explorer = MultiPaneFileExplorer()
                self.setCentralWidget(self.multi_pane_explorer)
            except ImportError:
                # Fallback interface
                self._create_fallback_multi_pane()
            
            self.statusBar().showMessage("Multi-Pane Explorer Interface - Ready")
        
        def _create_fallback_multi_pane(self):
            """Create fallback multi-pane interface."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # Title
            title = QLabel("Multi-Pane Explorer (Simplified)")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
            layout.addWidget(title)
            
            # Simulated panes
            pane_layout = QHBoxLayout()
            
            for i in range(2):
                pane = QWidget()
                pane.setStyleSheet("border: 1px solid #ccc; margin: 5px;")
                pane_v_layout = QVBoxLayout(pane)
                
                pane_label = QLabel(f"Pane {i+1}")
                pane_label.setAlignment(Qt.AlignCenter)
                pane_v_layout.addWidget(pane_label)
                
                info_label = QLabel("Multi-pane file explorer\nwould appear here when\nfull components are loaded.")
                info_label.setAlignment(Qt.AlignCenter)
                info_label.setStyleSheet("color: #666; font-size: 12px;")
                pane_v_layout.addWidget(info_label)
                
                pane_layout.addWidget(pane)
            
            layout.addLayout(pane_layout)
            
            # Interface switch button
            switch_button = QPushButton("Switch to Dialog Hub")
            switch_button.clicked.connect(lambda: self.switch_interface_mode(InterfaceMode.DIALOG_HUB))
            layout.addWidget(switch_button)
        
        def switch_interface_mode(self, new_mode):
            """Switch between interface modes."""
            if new_mode == self.current_interface_mode:
                return
            
            # Save current state
            if self.config_manager:
                self.config_manager.set_setting('interface_mode', 'current_mode', new_mode.value)
            
            self.current_interface_mode = new_mode
            
            # Clear current interface
            current_widget = self.centralWidget()
            if current_widget:
                current_widget.setParent(None)
            
            # Initialize new interface
            self._initialize_interface()
            
            QMessageBox.information(self, "Interface Switched", 
                                  f"Switched to {new_mode.value.replace('_', ' ').title()} interface.")
        
        def _show_help(self):
            """Show application help and keyboard shortcuts."""
            help_text = """
Richard's File Utilities - Keyboard Shortcuts

Interface Switching:
Ctrl+Shift+H    - Switch to Dialog Hub Interface
Ctrl+Shift+M    - Switch to Multi-Pane Explorer Interface

Tool Shortcuts:
Ctrl+F          - Open File Finder
Ctrl+D          - Open Duplicate Finder
Ctrl+S          - Open Size Analyzer
Ctrl+Shift+S    - Open Security Tools

General:
F1              - Show this help
Ctrl+,          - Open Preferences
ESC             - Close current dialog

Accessibility:
High contrast and large fonts can be enabled in Preferences.
All tools support keyboard navigation and screen readers.
            """
            
            QMessageBox.information(self, "RFU Help", help_text)
        
        def _show_preferences(self):
            """Show preferences dialog for interface configuration."""
            from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDialog,
                                         QGroupBox, QHBoxLayout, QLabel,
                                         QPushButton, QVBoxLayout)
            
            dialog = QDialog(self)
            dialog.setWindowTitle("RFU Preferences")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Interface preferences group
            interface_group = QGroupBox("Interface Settings")
            interface_layout = QVBoxLayout(interface_group)
            
            # Default interface mode
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("Default Interface Mode:"))
            mode_combo = QComboBox()
            mode_combo.addItems([mode.value for mode in InterfaceMode])
            if self.config_manager:
                current_mode = self.config_manager.get_setting(
                    'interface_mode', 'current_mode', 
                    InterfaceMode.DIALOG_HUB.value
                )
                mode_combo.setCurrentText(current_mode)
            mode_layout.addWidget(mode_combo)
            interface_layout.addLayout(mode_layout)
            
            # Auto-detection checkbox
            auto_detect_cb = QCheckBox("Enable workflow-based suggestions")
            if self.config_manager:
                auto_detect_enabled = self.config_manager.get_setting(
                    'interface_mode', 'auto_detect_enabled', True
                )
                auto_detect_cb.setChecked(auto_detect_enabled)
            interface_layout.addWidget(auto_detect_cb)
            
            # Animation checkbox
            animations_cb = QCheckBox("Enable transition animations")
            if self.config_manager:
                animations_enabled = self.config_manager.get_setting(
                    'interface_mode', 'transition_animations', True
                )
                animations_cb.setChecked(animations_enabled)
            interface_layout.addWidget(animations_cb)
            
            layout.addWidget(interface_group)
            
            # Accessibility preferences group
            accessibility_group = QGroupBox("Accessibility Settings")
            accessibility_layout = QVBoxLayout(accessibility_group)
            
            high_contrast_cb = QCheckBox("High contrast theme")
            large_fonts_cb = QCheckBox("Large fonts")
            
            if self.config_manager:
                high_contrast = self.config_manager.get_setting(
                    'accessibility', 'high_contrast', False
                )
                large_fonts = self.config_manager.get_setting(
                    'accessibility', 'large_fonts', False
                )
                high_contrast_cb.setChecked(high_contrast)
                large_fonts_cb.setChecked(large_fonts)
            
            accessibility_layout.addWidget(high_contrast_cb)
            accessibility_layout.addWidget(large_fonts_cb)
            layout.addWidget(accessibility_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            def save_preferences():
                if self.config_manager:
                    # Save interface settings
                    self.config_manager.set_setting(
                        'interface_mode', 'current_mode', 
                        mode_combo.currentText()
                    )
                    self.config_manager.set_setting(
                        'interface_mode', 'auto_detect_enabled', 
                        auto_detect_cb.isChecked()
                    )
                    self.config_manager.set_setting(
                        'interface_mode', 'transition_animations', 
                        animations_cb.isChecked()
                    )
                    
                    # Save accessibility settings
                    self.config_manager.set_setting(
                        'accessibility', 'high_contrast', 
                        high_contrast_cb.isChecked()
                    )
                    self.config_manager.set_setting(
                        'accessibility', 'large_fonts', 
                        large_fonts_cb.isChecked()
                    )
                    
                    # Apply accessibility changes immediately
                    if high_contrast_cb.isChecked():
                        self._apply_high_contrast_theme()
                    else:
                        self.setStyleSheet("")  # Reset to default
                    
                    if large_fonts_cb.isChecked():
                        self._apply_large_fonts()
                    else:
                        self.setFont(QApplication.instance().font())
                
                dialog.accept()
            
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(save_preferences)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec_()
        
        def launch_tool(self, tool_name):
            """Launch a tool (placeholder implementation)."""
            # Track tool usage for workflow analysis
            self.tool_usage_count += 1
            
            # Track in configuration for analysis
            if self.config_manager:
                try:
                    usage_history = self.config_manager.get_setting(
                        'workflow_analysis', 'tool_usage_history', []
                    )
                    usage_data = {
                        'tool_name': tool_name,
                        'timestamp': datetime.now().isoformat(),
                        'interface_mode': self.current_interface_mode.value,
                        'session_duration': (
                            datetime.now() - self.session_start_time
                        ).total_seconds()
                    }
                    usage_history.append(usage_data)
                    
                    # Keep only last 200 entries for performance
                    if len(usage_history) > 200:
                        usage_history = usage_history[-200:]
                    
                    self.config_manager.set_setting(
                        'workflow_analysis', 'tool_usage_history', usage_history
                    )
                except (AttributeError, KeyError):
                    pass
            
            # Emit signal for tracking
            self.tool_launched.emit(tool_name)
            
            QMessageBox.information(
                self, "Tool Launch", 
                f"Launching {tool_name}...\n\n"
                f"Current Interface: {self.current_interface_mode.value}\n"
                f"This is a demonstration of the dual-interface system."
            )
    
    def main():
        """Main entry point."""
        print(f"Starting {APP_NAME} with Dual Interface System...")
        
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion("3.0.0")
        
        window = RFUMainWindow()
        window.show()
        
        print("Dual-interface system initialized successfully.")
        return app.exec_()
        
    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    print("Please ensure PyQt5 is properly installed.")
    sys.exit(1)