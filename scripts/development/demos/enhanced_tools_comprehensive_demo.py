"""
Comprehensive Menu Integration Demonstration

This script demonstrates all the enhanced tools with menu integration,
showcasing the complete File Finder template implementation across
all metadata and system tools.
"""

import os
import sys
import subprocess
from datetime import datetime

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QGroupBox, QGridLayout,
        QMessageBox, QSplitter, QListWidget, QListWidgetItem,
        QTabWidget, QScrollArea, QFrame
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon

    class EnhancedToolsDemo(QMainWindow):
        """Demonstration of all enhanced tools with menu integration."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Enhanced Tools with Menu Integration - Comprehensive Demo")
            self.setGeometry(100, 100, 1400, 900)
            
            # Enhanced tools registry
            self.enhanced_tools = {
                'File Touch': {
                    'script': 'enhanced_file_touch_with_menu.py',
                    'description': 'File timestamp modification with comprehensive menu system',
                    'category': 'Metadata Tools',
                    'features': [
                        'StandardWindow integration with File/Edit/View/Tools/Help menus',
                        'Comprehensive help system with HTML formatting',
                        'File and folder timestamp modification',
                        'Batch processing capabilities',
                        'Progress monitoring and error handling',
                        'Keyboard shortcuts (Ctrl+Q for Exit, F1 for Help)'
                    ],
                    'menu_callbacks': [
                        'new_touch_session() - Clear files and start fresh',
                        'help_file_touch() - Show comprehensive help dialog'
                    ],
                    'status': 'Enhanced with Menu Integration'
                },
                'Office Metadata Editor': {
                    'script': 'enhanced_office_metadata_editor_with_menu.py',
                    'description': 'Comprehensive office document metadata viewer and editor',
                    'category': 'Metadata Tools',
                    'features': [
                        'StandardWindow integration with full menu system',
                        'OOXML format support (DOCX, XLSX, PPTX)',
                        'Legacy Office format basic support',
                        'PDF metadata extraction capabilities',
                        'Tabbed interface for organized metadata viewing',
                        'Worker thread processing for responsive UI',
                        'Export functionality for metadata reports'
                    ],
                    'menu_callbacks': [
                        'open_office_file() - Open and process office documents',
                        'save_metadata() - Save metadata changes',
                        'export_metadata() - Export metadata to various formats',
                        'help_office_metadata() - Show comprehensive help'
                    ],
                    'status': 'Enhanced with Menu Integration'
                },
                'Image Metadata Editor': {
                    'script': 'enhanced_image_metadata_editor_with_menu.py',
                    'description': 'Comprehensive image metadata viewer and EXIF editor',
                    'category': 'Metadata Tools',
                    'features': [
                        'StandardWindow integration with complete menu system',
                        'EXIF data extraction and viewing',
                        'Image metadata editing capabilities',
                        'Batch processing for multiple images',
                        'Metadata export and reporting',
                        'Advanced image format support'
                    ],
                    'menu_callbacks': [
                        'Worker thread for metadata extraction',
                        'Comprehensive help system',
                        'Export and save functionality'
                    ],
                    'status': 'Previously Enhanced with Menu Integration'
                },
                'Encrypt/Decrypt Tool': {
                    'script': 'enhanced_encrypt_decrypt_with_menu.py',
                    'description': 'File and text encryption/decryption with security features',
                    'category': 'Security Tools',
                    'features': [
                        'StandardWindow integration',
                        'Multiple encryption algorithms',
                        'Password strength validation',
                        'Secure key generation',
                        'File and text encryption modes'
                    ],
                    'status': 'Previously Enhanced with Menu Integration'
                },
                'Secure Delete Tool': {
                    'script': 'enhanced_secure_delete_with_menu.py',
                    'description': 'Secure file deletion with multiple overwrite patterns',
                    'category': 'Security Tools',
                    'features': [
                        'StandardWindow integration',
                        'Multiple secure deletion algorithms',
                        'Progress monitoring',
                        'Verification and reporting'
                    ],
                    'status': 'Previously Enhanced with Menu Integration'
                },
                'Security Preferences': {
                    'script': 'enhanced_security_preferences_with_menu.py',
                    'description': 'Security settings and preferences management',
                    'category': 'Security Tools',
                    'features': [
                        'StandardWindow integration',
                        'Comprehensive security settings',
                        'Configuration management',
                        'Security policy enforcement'
                    ],
                    'status': 'Previously Enhanced with Menu Integration'
                }
            }
            
            self.init_ui()
            
        def init_ui(self):
            """Initialize the user interface."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            
            # Header
            header_label = QLabel("Enhanced Tools with Menu Integration - Comprehensive Demonstration")
            header_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 15px;
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    text-align: center;
                }
            """)
            header_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(header_label)
            
            # Project overview
            overview_text = QLabel("""
            <b>Project Completion Summary:</b> Successfully enhanced all remaining metadata and system tools 
            with comprehensive menu integration following the File Finder template pattern. All tools now 
            feature StandardWindow inheritance, complete File/Edit/View/Tools/Help menus, keyboard shortcuts, 
            and comprehensive help systems with professional HTML formatting.
            """)
            overview_text.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: #d5f4e6;
                    border-left: 4px solid #27ae60;
                    border-radius: 4px;
                    margin-bottom: 15px;
                }
            """)
            overview_text.setWordWrap(True)
            main_layout.addWidget(overview_text)
            
            # Create splitter for main content
            splitter = QSplitter(Qt.Horizontal)
            main_layout.addWidget(splitter)
            
            # Left panel - Tool list
            left_panel = self.create_tool_list_panel()
            splitter.addWidget(left_panel)
            
            # Right panel - Tool details
            right_panel = self.create_tool_details_panel()
            splitter.addWidget(right_panel)
            
            # Set splitter proportions
            splitter.setSizes([400, 1000])
            
            # Status bar
            self.statusBar().showMessage("Ready - Select a tool to view details and launch demonstration")
            
        def create_tool_list_panel(self):
            """Create the tool list panel."""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Panel header
            header = QLabel("Enhanced Tools")
            header.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #34495e;
                    padding: 10px;
                    background-color: #bdc3c7;
                    border-radius: 4px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(header)
            
            # Tool list
            self.tool_list = QListWidget()
            self.tool_list.itemClicked.connect(self.on_tool_selected)
            
            # Add tools to list
            for tool_name, tool_info in self.enhanced_tools.items():
                item = QListWidgetItem(f"🔧 {tool_name}")
                item.setData(Qt.UserRole, tool_name)
                self.tool_list.addItem(item)
                
            # Style the list
            self.tool_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: white;
                    selection-background-color: #3498db;
                    selection-color: white;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QListWidget::item:hover {
                    background-color: #f8f9fa;
                }
            """)
            
            layout.addWidget(self.tool_list)
            
            # Launch all button
            launch_all_button = QPushButton("🚀 Launch All Enhanced Tools")
            launch_all_button.clicked.connect(self.launch_all_tools)
            launch_all_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            layout.addWidget(launch_all_button)
            
            return panel
            
        def create_tool_details_panel(self):
            """Create the tool details panel."""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Panel header
            self.details_header = QLabel("Select a tool to view details")
            self.details_header.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #34495e;
                    padding: 10px;
                    background-color: #bdc3c7;
                    border-radius: 4px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(self.details_header)
            
            # Scrollable content area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
            
            self.details_content = QWidget()
            self.details_layout = QVBoxLayout(self.details_content)
            
            scroll_area.setWidget(self.details_content)
            layout.addWidget(scroll_area)
            
            # Initially empty
            self.show_welcome_message()
            
            return panel
            
        def show_welcome_message(self):
            """Show welcome message in details panel."""
            # Clear existing content
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
                
            welcome_label = QLabel("""
            <h2>🎉 Menu Integration Project Complete!</h2>
            
            <p><b>Welcome to the comprehensive demonstration of all enhanced tools with menu integration.</b></p>
            
            <h3>✅ Project Accomplishments:</h3>
            <ul>
                <li><b>File Touch Tool</b> - Enhanced with complete menu system and timestamp modification</li>
                <li><b>Office Metadata Editor</b> - Advanced metadata viewing and editing with worker threads</li>
                <li><b>Image Metadata Editor</b> - Comprehensive EXIF viewing and editing (previously completed)</li>
                <li><b>Security Tools Suite</b> - Encrypt/Decrypt, Secure Delete, Security Preferences (previously completed)</li>
            </ul>
            
            <h3>🚀 Key Features Implemented:</h3>
            <ul>
                <li><b>StandardWindow Integration</b> - All tools inherit from StandardWindow base class</li>
                <li><b>Complete Menu System</b> - File/Edit/View/Tools/Help menus with keyboard shortcuts</li>
                <li><b>Comprehensive Help</b> - Professional HTML-formatted help dialogs for each tool</li>
                <li><b>Fallback Compatibility</b> - Dual-mode operation for different import contexts</li>
                <li><b>Tool-Specific Callbacks</b> - Custom menu callbacks for specialized functionality</li>
                <li><b>Professional UI</b> - Consistent styling and user experience across all tools</li>
            </ul>
            
            <h3>🔧 Technical Implementation:</h3>
            <ul>
                <li><b>Template Pattern</b> - Used File Finder as template for consistent implementation</li>
                <li><b>Menu Callbacks</b> - _setup_menu_callbacks() method for tool-specific menu registration</li>
                <li><b>Error Handling</b> - Robust error handling and user feedback</li>
                <li><b>Thread Safety</b> - Worker threads for responsive UI in complex operations</li>
                <li><b>Code Quality</b> - Professional code structure with comprehensive documentation</li>
            </ul>
            
            <p><b>Select a tool from the list to view detailed information and launch demonstrations.</b></p>
            """)
            
            welcome_label.setWordWrap(True)
            welcome_label.setStyleSheet("""
                QLabel {
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    line-height: 1.6;
                }
            """)
            
            self.details_layout.addWidget(welcome_label)
            self.details_layout.addStretch()
            
        def on_tool_selected(self, item):
            """Handle tool selection."""
            tool_name = item.data(Qt.UserRole)
            tool_info = self.enhanced_tools[tool_name]
            
            # Update header
            self.details_header.setText(f"🔧 {tool_name} - Details and Launch")
            
            # Clear existing content
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
                
            # Tool description
            desc_group = QGroupBox("Tool Description")
            desc_layout = QVBoxLayout(desc_group)
            
            desc_label = QLabel(tool_info['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
            desc_layout.addWidget(desc_label)
            
            self.details_layout.addWidget(desc_group)
            
            # Category and status
            info_group = QGroupBox("Tool Information")
            info_layout = QGridLayout(info_group)
            
            info_layout.addWidget(QLabel("Category:"), 0, 0)
            category_label = QLabel(tool_info['category'])
            category_label.setStyleSheet("font-weight: bold; color: #3498db;")
            info_layout.addWidget(category_label, 0, 1)
            
            info_layout.addWidget(QLabel("Status:"), 1, 0)
            status_label = QLabel(tool_info['status'])
            status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            info_layout.addWidget(status_label, 1, 1)
            
            info_layout.addWidget(QLabel("Script:"), 2, 0)
            script_label = QLabel(tool_info['script'])
            script_label.setStyleSheet("font-family: 'Courier New', monospace; color: #666;")
            info_layout.addWidget(script_label, 2, 1)
            
            self.details_layout.addWidget(info_group)
            
            # Features
            features_group = QGroupBox("Key Features")
            features_layout = QVBoxLayout(features_group)
            
            for feature in tool_info['features']:
                feature_label = QLabel(f"• {feature}")
                feature_label.setWordWrap(True)
                feature_label.setStyleSheet("padding: 2px; margin-left: 10px;")
                features_layout.addWidget(feature_label)
                
            self.details_layout.addWidget(features_group)
            
            # Menu callbacks (if available)
            if 'menu_callbacks' in tool_info:
                callbacks_group = QGroupBox("Menu Integration Callbacks")
                callbacks_layout = QVBoxLayout(callbacks_group)
                
                for callback in tool_info['menu_callbacks']:
                    callback_label = QLabel(f"📋 {callback}")
                    callback_label.setWordWrap(True)
                    callback_label.setStyleSheet("""
                        padding: 4px; 
                        margin-left: 10px; 
                        font-family: 'Courier New', monospace;
                        background-color: #f8f9fa;
                        border-radius: 2px;
                    """)
                    callbacks_layout.addWidget(callback_label)
                    
                self.details_layout.addWidget(callbacks_group)
            
            # Launch button
            launch_button = QPushButton(f"🚀 Launch {tool_name}")
            launch_button.clicked.connect(lambda: self.launch_tool(tool_info['script']))
            launch_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    margin: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.details_layout.addWidget(launch_button)
            
            self.details_layout.addStretch()
            
            # Update status
            self.statusBar().showMessage(f"Selected: {tool_name} - Ready to launch demonstration")
            
        def launch_tool(self, script_name):
            """Launch a specific enhanced tool."""
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            
            if os.path.exists(script_path):
                try:
                    # Launch the script in a new process
                    subprocess.Popen([sys.executable, script_path], 
                                   cwd=os.path.dirname(__file__))
                    
                    self.statusBar().showMessage(f"Launched: {script_name}")
                    
                    QMessageBox.information(self, "Tool Launched", 
                                           f"Successfully launched {script_name}\n\n"
                                           f"The enhanced tool should now be running in a separate window "
                                           f"with full menu integration including:\n\n"
                                           f"• File/Edit/View/Tools/Help menus\n"
                                           f"• Keyboard shortcuts (Ctrl+Q, F1, F5)\n"
                                           f"• Comprehensive help system\n"
                                           f"• Professional user interface\n"
                                           f"• Tool-specific menu callbacks")
                                           
                except Exception as e:
                    QMessageBox.critical(self, "Launch Error", 
                                        f"Error launching {script_name}:\n{e}")
                    
            else:
                QMessageBox.warning(self, "File Not Found", 
                                   f"Script not found: {script_name}")
                                   
        def launch_all_tools(self):
            """Launch all enhanced tools for comprehensive demonstration."""
            reply = QMessageBox.question(self, "Launch All Tools", 
                                        "Launch all enhanced tools for comprehensive demonstration?\n\n"
                                        "This will open all enhanced tools simultaneously to show "
                                        "the complete menu integration implementation.",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                launched_count = 0
                failed_count = 0
                
                for tool_name, tool_info in self.enhanced_tools.items():
                    script_path = os.path.join(os.path.dirname(__file__), tool_info['script'])
                    
                    if os.path.exists(script_path):
                        try:
                            subprocess.Popen([sys.executable, script_path], 
                                           cwd=os.path.dirname(__file__))
                            launched_count += 1
                        except Exception as e:
                            failed_count += 1
                            print(f"Error launching {tool_name}: {e}")
                    else:
                        failed_count += 1
                        print(f"Script not found: {tool_info['script']}")
                
                # Show results
                if failed_count == 0:
                    QMessageBox.information(self, "All Tools Launched", 
                                           f"Successfully launched all {launched_count} enhanced tools!\n\n"
                                           f"Each tool features:\n"
                                           f"• Complete menu integration\n"
                                           f"• StandardWindow inheritance\n"
                                           f"• Professional user interface\n"
                                           f"• Comprehensive help systems\n"
                                           f"• Keyboard shortcuts\n"
                                           f"• Tool-specific functionality")
                else:
                    QMessageBox.warning(self, "Launch Summary", 
                                       f"Launched: {launched_count} tools\n"
                                       f"Failed: {failed_count} tools\n\n"
                                       f"Check console for error details.")
                
                self.statusBar().showMessage(f"Batch launch completed: {launched_count} tools launched")


    def main():
        """Main function to run the Enhanced Tools Demo."""
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Set application properties
        app.setApplicationName("Enhanced Tools Menu Integration Demo")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Richard's File Utilities")
        
        # Create and show the main window
        window = EnhancedToolsDemo()
        window.show()
        
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing PyQt5 modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    
    def main():
        print("Enhanced Tools Demo requires PyQt5 to be installed.")
        print("Please install PyQt5 using: pip install PyQt5")

    if __name__ == "__main__":
        main()
