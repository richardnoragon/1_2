#!/usr/bin/env python3
"""
Enhanced Network Tools Demo
Demonstrates the File menu integration for network tools and bookmark manager.

This demo showcases:
- File menu with Exit and Help options
- Tool-specific preferences
- Consistent UI/UX patterns
- Menu-driven access to functionality
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt


def demo_network_connectivity():
    """Demo the enhanced Network Connectivity tool."""
    try:
        from src.utilities.network.network_connectivity import NetworkConnectivityGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show the tool
        tool = NetworkConnectivityGUI()
        tool.show()
        
        # Show demo message
        QMessageBox.information(
            tool, 
            "Network Connectivity Demo", 
            "Enhanced Network Connectivity Tool Features:\n\n"
            "✓ File menu with Exit and Help options\n"
            "✓ Preferences accessible via File → Preferences\n"
            "✓ Refresh functionality via File menu\n"
            "✓ Consistent styling with File Finder\n"
            "✓ Standard window integration\n\n"
            "Try using:\n"
            "• Ctrl+Q to exit\n"
            "• F5 to refresh\n"
            "• File → Preferences for settings"
        )
        
        return tool
        
    except Exception as e:
        print(f"Error launching Network Connectivity: {e}")
        return None


def demo_network_scanner():
    """Demo the enhanced Network Scanner tool."""
    try:
        from src.utilities.network.network_scanner import NetworkScannerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show the tool
        tool = NetworkScannerGUI()
        tool.show()
        
        # Show demo message
        QMessageBox.information(
            tool, 
            "Network Scanner Demo", 
            "Enhanced Network Scanner Tool Features:\n\n"
            "✓ File menu with Exit and Help options\n"
            "✓ Preferences accessible via File → Preferences\n"
            "✓ Refresh functionality via File menu\n"
            "✓ Consistent styling with File Finder\n"
            "✓ Standard window integration\n\n"
            "Try using:\n"
            "• Ctrl+Q to exit\n"
            "• F5 to refresh\n"
            "• File → Preferences for settings\n"
            "• Quick scan presets for common tasks"
        )
        
        return tool
        
    except Exception as e:
        print(f"Error launching Network Scanner: {e}")
        return None


def demo_network_transfer():
    """Demo the enhanced Network Transfer tool."""
    try:
        from src.utilities.network.network_transfer import NetworkTransferGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show the tool
        tool = NetworkTransferGUI()
        tool.show()
        
        # Show demo message
        QMessageBox.information(
            tool, 
            "Network Transfer Demo", 
            "Enhanced Network Transfer Tool Features:\n\n"
            "✓ File menu with Exit and Help options\n"
            "✓ Preferences accessible via File → Preferences\n"
            "✓ Import/Export functionality via File menu\n"
            "✓ Refresh functionality via File menu\n"
            "✓ Consistent styling with File Finder\n"
            "✓ Standard window integration\n\n"
            "Try using:\n"
            "• Ctrl+Q to exit\n"
            "• F5 to refresh\n"
            "• File → Preferences for settings\n"
            "• File → Export/Import for settings transfer"
        )
        
        return tool
        
    except Exception as e:
        print(f"Error launching Network Transfer: {e}")
        return None


def demo_bookmark_manager():
    """Demo the enhanced Bookmark Manager tool."""
    try:
        from src.utilities.network.bookmark_manager import BookmarkManagerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show the tool
        tool = BookmarkManagerGUI()
        tool.show()
        
        # Show demo message
        QMessageBox.information(
            tool, 
            "Bookmark Manager Demo", 
            "Enhanced Bookmark Manager Tool Features:\n\n"
            "✓ File menu with Exit and Help options\n"
            "✓ Preferences accessible via File → Preferences\n"
            "✓ Import/Export functionality via File menu\n"
            "✓ Refresh functionality via File menu\n"
            "✓ Consistent styling with File Finder\n"
            "✓ Standard window integration\n\n"
            "Try using:\n"
            "• Ctrl+Q to exit\n"
            "• F5 to refresh\n"
            "• File → Preferences for settings\n"
            "• File → Export/Import for bookmark transfer"
        )
        
        return tool
        
    except Exception as e:
        print(f"Error launching Bookmark Manager: {e}")
        return None


class EnhancedNetworkToolsDemo(QMainWindow):
    """Demo launcher for enhanced network tools."""
    
    def __init__(self):
        super().__init__()
        self.tools = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the demo interface."""
        self.setWindowTitle("Enhanced Network Tools Demo - File Menu Integration")
        self.setGeometry(200, 200, 500, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Enhanced Network Tools Demo")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "This demo showcases the enhanced network tools with File menu integration.\n"
            "Each tool now includes:\n\n"
            "• File menu with Exit and Help options\n"
            "• Tool-specific preferences\n"
            "• Consistent UI/UX patterns with File Finder\n"
            "• Menu-driven access to functionality\n"
            "• Standard keyboard shortcuts (Ctrl+Q, F5, etc.)"
        )
        description.setWordWrap(True)
        description.setStyleSheet("padding: 10px; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # Demo buttons
        self.create_demo_button(layout, "Network Connectivity", demo_network_connectivity)
        self.create_demo_button(layout, "Network Scanner", demo_network_scanner)
        self.create_demo_button(layout, "Network Transfer", demo_network_transfer)
        self.create_demo_button(layout, "Bookmark Manager", demo_bookmark_manager)
        
        layout.addStretch()
        
        # Exit button
        exit_btn = QPushButton("Exit Demo")
        exit_btn.clicked.connect(self.close_all_and_exit)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(exit_btn)
    
    def create_demo_button(self, layout, name, callback):
        """Create a demo button for a tool."""
        btn = QPushButton(f"Demo {name}")
        btn.clicked.connect(lambda: self.launch_demo(callback))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(btn)
    
    def launch_demo(self, demo_func):
        """Launch a demo tool."""
        tool = demo_func()
        if tool:
            self.tools.append(tool)
    
    def close_all_and_exit(self):
        """Close all demo tools and exit."""
        for tool in self.tools:
            try:
                tool.close()
            except:
                pass
        self.close()
    
    def closeEvent(self, event):
        """Handle close event."""
        self.close_all_and_exit()
        event.accept()


def main():
    """Main demo function."""
    print("Enhanced Network Tools Demo")
    print("=" * 40)
    print("Demonstrating File menu integration for:")
    print("• Network Connectivity")
    print("• Network Scanner") 
    print("• Network Transfer")
    print("• Bookmark Manager")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Network Tools Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Richard's File Utilities")
    
    # Show demo launcher
    demo = EnhancedNetworkToolsDemo()
    demo.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
