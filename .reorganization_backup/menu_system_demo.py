#!/usr/bin/env python3
"""
Menu System Demonstration

This script demonstrates the comprehensive menu system implementation
for Richard's File Utilities, showing how to integrate standardized
menus into tool interfaces.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QListWidget,
        QMessageBox, QTabWidget, QGroupBox
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from src.gui.standard_window import StandardWindow
    from gui.themes import ThemeManager, Colors, Fonts
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    print("Standard window system not available, using fallback")
    from PyQt5.QtWidgets import QMainWindow as StandardWindow
    STANDARD_WINDOW_AVAILABLE = False


class MenuDemoWindow(StandardWindow):
    """Demonstration window showing the comprehensive menu system."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Menu System Demo - Richard's File Utilities",
                enable_menu=True,
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Menu System Demo - Richard's File Utilities")
            self.resize(800, 600)
        
        self.demo_data = []
        self._setup_ui()
        
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
            ThemeManager.apply_utility_window_theme(self)
    
    def _setup_ui(self):
        """Setup the demonstration user interface."""
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        if STANDARD_WINDOW_AVAILABLE:
            header = self.create_header("Menu System Demonstration")
        else:
            header = QLabel("Menu System Demonstration")
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "This window demonstrates the comprehensive menu system for Richard's File Utilities. "
            "The menu bar above includes standardized File, Edit, View, Tools, and Help menus with "
            "proper keyboard shortcuts, platform-specific styling, and comprehensive functionality."
        )
        description.setWordWrap(True)
        description.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 4px;")
        layout.addWidget(description)
        
        # Tab widget for different demo sections
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Menu Features Tab
        menu_tab = self._create_menu_features_tab()
        tab_widget.addTab(menu_tab, "Menu Features")
        
        # Keyboard Shortcuts Tab
        shortcuts_tab = self._create_shortcuts_tab()
        tab_widget.addTab(shortcuts_tab, "Keyboard Shortcuts")
        
        # Menu Callbacks Tab
        callbacks_tab = self._create_callbacks_tab()
        tab_widget.addTab(callbacks_tab, "Menu Callbacks")
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        test_menu_btn = QPushButton("Test Menu Actions")
        test_menu_btn.clicked.connect(self.test_menu_actions)
        action_layout.addWidget(test_menu_btn)
        
        demo_callbacks_btn = QPushButton("Demo Callbacks")
        demo_callbacks_btn.clicked.connect(self.demo_callbacks)
        action_layout.addWidget(demo_callbacks_btn)
        
        action_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        action_layout.addWidget(close_btn)
        
        layout.addLayout(action_layout)
    
    def _create_menu_features_tab(self):
        """Create the menu features demonstration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Menu overview
        if STANDARD_WINDOW_AVAILABLE:
            features_group = self.create_group_box("Standard Menu Features")
        else:
            features_group = QGroupBox("Standard Menu Features")
        
        features_layout = QVBoxLayout(features_group)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(200)
        features_text.setPlainText("""
Standard Menu Structure:

• File Menu:
  - New Project (Ctrl+N)
  - Open (Ctrl+O)
  - Recent Files submenu
  - Save (Ctrl+S) / Save As (Ctrl+Shift+S)
  - Export/Import
  - Print (Ctrl+P)
  - Preferences (Ctrl+,)
  - Exit (Ctrl+Q)

• Edit Menu:
  - Undo/Redo (Ctrl+Z/Ctrl+Y)
  - Cut/Copy/Paste (Ctrl+X/C/V)
  - Select All (Ctrl+A)
  - Find/Replace (Ctrl+F/H)

• View Menu:
  - Zoom controls (Ctrl++/-/0)
  - Theme selection (Light/Dark)
  - Fullscreen toggle (F11)
  - Always on top
  - Refresh (F5)

• Tools Menu:
  - Tool-specific options
  - Log viewer
  - Performance monitor
  - Reset settings

• Help Menu:
  - User guide (F1)
  - Keyboard shortcuts (Ctrl+?)
  - Website/Bug report links
  - System information
  - Check for updates
  - About dialog
        """)
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_group)
        
        # Styling information
        if STANDARD_WINDOW_AVAILABLE:
            styling_group = self.create_group_box("Menu Styling Features")
        else:
            styling_group = QGroupBox("Menu Styling Features")
        
        styling_layout = QVBoxLayout(styling_group)
        
        styling_text = QTextEdit()
        styling_text.setReadOnly(True)
        styling_text.setMaximumHeight(150)
        styling_text.setPlainText("""
Menu Styling Features:

• Platform-specific design guidelines
• Consistent color scheme with theme support
• Hover effects and visual feedback
• Proper keyboard shortcut display
• Icon support for menu items
• Separator lines for logical grouping
• Disabled state styling
• Accessibility support
        """)
        styling_layout.addWidget(styling_text)
        
        layout.addWidget(styling_group)
        
        return tab
    
    def _create_shortcuts_tab(self):
        """Create the keyboard shortcuts demonstration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        shortcuts_text = QTextEdit()
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setHtml("""
        <h3>Keyboard Shortcuts Reference</h3>
        
        <h4>File Operations</h4>
        <table border="1" cellpadding="3" style="border-collapse: collapse;">
        <tr><td><b>Ctrl+N</b></td><td>New project or document</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open file or project</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save current work</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save with new name</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Print current document</td></tr>
        <tr><td><b>Ctrl+,</b></td><td>Open preferences</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit application</td></tr>
        </table>
        
        <h4>Edit Operations</h4>
        <table border="1" cellpadding="3" style="border-collapse: collapse;">
        <tr><td><b>Ctrl+Z</b></td><td>Undo last action</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Redo last undone action</td></tr>
        <tr><td><b>Ctrl+X</b></td><td>Cut selection</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Copy selection</td></tr>
        <tr><td><b>Ctrl+V</b></td><td>Paste from clipboard</td></tr>
        <tr><td><b>Ctrl+A</b></td><td>Select all items</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Find text or items</td></tr>
        <tr><td><b>Ctrl+H</b></td><td>Find and replace</td></tr>
        </table>
        
        <h4>View Operations</h4>
        <table border="1" cellpadding="3" style="border-collapse: collapse;">
        <tr><td><b>Ctrl++</b></td><td>Zoom in</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Reset zoom level</td></tr>
        <tr><td><b>F11</b></td><td>Toggle fullscreen mode</td></tr>
        <tr><td><b>F5</b></td><td>Refresh current view</td></tr>
        </table>
        
        <h4>Help and Navigation</h4>
        <table border="1" cellpadding="3" style="border-collapse: collapse;">
        <tr><td><b>F1</b></td><td>Open user guide</td></tr>
        <tr><td><b>Ctrl+?</b></td><td>Show keyboard shortcuts</td></tr>
        </table>
        """)
        
        layout.addWidget(shortcuts_text)
        
        return tab
    
    def _create_callbacks_tab(self):
        """Create the menu callbacks demonstration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Callback list
        if STANDARD_WINDOW_AVAILABLE:
            callbacks_group = self.create_group_box("Registered Menu Callbacks")
        else:
            callbacks_group = QGroupBox("Registered Menu Callbacks")
        
        callbacks_layout = QVBoxLayout(callbacks_group)
        
        self.callbacks_list = QListWidget()
        callbacks_layout.addWidget(self.callbacks_list)
        
        layout.addWidget(callbacks_group)
        
        # Callback demo buttons
        if STANDARD_WINDOW_AVAILABLE:
            demo_group = self.create_group_box("Callback Demonstrations")
        else:
            demo_group = QGroupBox("Callback Demonstrations")
        
        demo_layout = QVBoxLayout(demo_group)
        
        button_layout = QHBoxLayout()
        
        save_demo_btn = QPushButton("Demo Save")
        save_demo_btn.clicked.connect(lambda: self.demo_save_callback())
        button_layout.addWidget(save_demo_btn)
        
        export_demo_btn = QPushButton("Demo Export")
        export_demo_btn.clicked.connect(lambda: self.demo_export_callback())
        button_layout.addWidget(export_demo_btn)
        
        refresh_demo_btn = QPushButton("Demo Refresh")
        refresh_demo_btn.clicked.connect(lambda: self.demo_refresh_callback())
        button_layout.addWidget(refresh_demo_btn)
        
        demo_layout.addLayout(button_layout)
        layout.addWidget(demo_group)
        
        return tab
    
    def _setup_menu_callbacks(self):
        """Setup menu callbacks specific to this demo."""
        if hasattr(self, 'menu_manager'):
            # Register demo-specific callbacks
            self.menu_manager.register_callback('save_file', self.demo_save_callback)
            self.menu_manager.register_callback('export_data', self.demo_export_callback)
            self.menu_manager.register_callback('import_data', self.demo_import_callback)
            self.menu_manager.register_callback('show_options', self.demo_show_options)
            
            # Update the callbacks list
            self._update_callbacks_list()
    
    def _update_callbacks_list(self):
        """Update the callbacks list display."""
        if hasattr(self, 'callbacks_list') and hasattr(self, 'menu_manager'):
            self.callbacks_list.clear()
            if hasattr(self.menu_manager, 'callbacks'):
                for action_name, callback in self.menu_manager.callbacks.items():
                    self.callbacks_list.addItem(f"{action_name}: {callback.__name__}")
    
    def test_menu_actions(self):
        """Test various menu actions."""
        QMessageBox.information(
            self,
            "Menu Test",
            "Try using the keyboard shortcuts:\n\n"
            "• Ctrl+S - Save (demo)\n"
            "• Ctrl+E - Export (demo)\n"
            "• F5 - Refresh\n"
            "• F1 - Help\n"
            "• Ctrl+Q - Exit\n\n"
            "Or use the menus directly!"
        )
    
    def demo_callbacks(self):
        """Demonstrate the callback system."""
        if hasattr(self, 'menu_manager'):
            QMessageBox.information(
                self,
                "Callback Demo",
                f"Menu manager has {len(self.menu_manager.callbacks)} registered callbacks.\n\n"
                "These callbacks handle menu actions and can be customized for each tool."
            )
        else:
            QMessageBox.information(
                self,
                "Callback Demo",
                "Menu manager not available in fallback mode."
            )
    
    def demo_save_callback(self):
        """Demonstrate save callback."""
        self.demo_data.append(f"Save action at {self._get_timestamp()}")
        QMessageBox.information(self, "Save Demo", "Save callback executed successfully!")
    
    def demo_export_callback(self):
        """Demonstrate export callback."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Demo Export", "demo_data.txt", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Menu System Demo Export\n")
                    f.write("======================\n\n")
                    for item in self.demo_data:
                        f.write(f"{item}\n")
                
                QMessageBox.information(self, "Export Demo", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def demo_import_callback(self):
        """Demonstrate import callback."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Demo Import", "", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                QMessageBox.information(self, "Import Demo", f"Imported file content:\n\n{content[:200]}...")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")
    
    def demo_refresh_callback(self):
        """Demonstrate refresh callback."""
        self._update_callbacks_list()
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage("Demo refreshed!", 2000)
        QMessageBox.information(self, "Refresh Demo", "Refresh callback executed!")
    
    def demo_show_options(self):
        """Demonstrate options dialog."""
        QMessageBox.information(
            self,
            "Options Demo",
            "This would show tool-specific options.\n\n"
            "Each tool can customize its options dialog."
        )
    
    def show_preferences(self):
        """Override preferences to show demo-specific preferences."""
        QMessageBox.information(
            self,
            "Demo Preferences",
            "Menu System Demo Preferences:\n\n"
            "• Theme selection\n"
            "• Keyboard shortcuts\n"
            "• Menu behavior\n"
            "• Window settings"
        )
    
    def refresh_view(self):
        """Override refresh to update demo data."""
        self.demo_refresh_callback()
    
    def _get_timestamp(self):
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point for the menu system demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("RFU Menu Demo")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Richard's File Utilities")
    
    # Create and show the demo window
    demo_window = MenuDemoWindow()
    demo_window.show()
    
    # Show initial information
    QMessageBox.information(
        demo_window,
        "Menu System Demo",
        "Welcome to the Menu System Demonstration!\n\n"
        "This window showcases the comprehensive menu system for RFU tools.\n\n"
        "Features:\n"
        "• Standardized menu structure\n"
        "• Platform-specific styling\n"
        "• Keyboard shortcuts\n"
        "• Theme support\n"
        "• Customizable callbacks\n\n"
        "Try the menus and keyboard shortcuts!"
    )
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
