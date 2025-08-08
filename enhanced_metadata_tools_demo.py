#!/usr/bin/env python3
"""
Enhanced Metadata Tools Comprehensive Demo

This demonstration script showcases all three enhanced metadata tools
with integrated File menu functionality following the File Finder template:

1. Enhanced Image Metadata Editor - EXIF data viewing and analysis
2. Enhanced Office Metadata Editor - Office document metadata extraction
3. Enhanced File Touch Tool - File timestamp modification

Each tool features:
- File menu with Exit and Help options
- Standardized menu integration using File Finder template
- Comprehensive help documentation
- Consistent UI/UX patterns
- Error handling and fallback modes
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGroupBox, QHBoxLayout
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QIcon
    
    # Import the enhanced tools
    from enhanced_image_metadata_editor_with_menu import EnhancedImageMetadataEditorGUI
    from enhanced_office_metadata_editor_with_menu import EnhancedOfficeMetadataEditorGUI  
    from enhanced_file_touch_with_menu import EnhancedFileTouchGUI
    
    class MetadataToolsLauncher(QMainWindow):
        """Main launcher for all enhanced metadata tools."""
        
        def __init__(self):
            super().__init__()
            self.init_ui()
            self.tool_windows = []
            
        def init_ui(self):
            """Initialize the launcher interface."""
            self.setWindowTitle("Enhanced Metadata Tools - Richard's File Utilities")
            self.setGeometry(200, 200, 600, 500)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Header
            header_label = QLabel("Enhanced Metadata Tools with File Menu Integration")
            header_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 20px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #ecf0f1, stop: 1 #d5dbdb);
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }
            """)
            header_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(header_label)
            
            # Description
            desc_label = QLabel("""
            These enhanced metadata tools feature comprehensive File menu integration 
            following the File Finder template pattern. Each tool includes Exit and Help 
            options, standardized callbacks, and consistent UI/UX design.
            """)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #666;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
            """)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc_label)
            
            # Tools grid
            tools_group = QGroupBox("Available Enhanced Tools")
            tools_group.setStyleSheet("""
                QGroupBox {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 20px;
                    padding: 0 5px 0 5px;
                }
            """)
            tools_layout = QVBoxLayout(tools_group)
            
            # Tool 1: Image Metadata Editor
            img_group = QGroupBox("📸 Enhanced Image Metadata Editor")
            img_layout = QVBoxLayout(img_group)
            
            img_desc = QLabel("View and analyze image EXIF data, file information, and metadata from JPEG, PNG, TIFF, and other image formats.")
            img_desc.setWordWrap(True)
            img_desc.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
            img_layout.addWidget(img_desc)
            
            img_button = QPushButton("Launch Image Metadata Editor")
            img_button.clicked.connect(self.launch_image_metadata_editor)
            img_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            img_layout.addWidget(img_button)
            tools_layout.addWidget(img_group)
            
            # Tool 2: Office Metadata Editor
            office_group = QGroupBox("📄 Enhanced Office Metadata Editor")
            office_layout = QVBoxLayout(office_group)
            
            office_desc = QLabel("Extract and view metadata from Microsoft Office documents (DOCX, XLSX, PPTX), PDFs, and other office formats.")
            office_desc.setWordWrap(True)
            office_desc.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
            office_layout.addWidget(office_desc)
            
            office_button = QPushButton("Launch Office Metadata Editor")
            office_button.clicked.connect(self.launch_office_metadata_editor)
            office_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            office_layout.addWidget(office_button)
            tools_layout.addWidget(office_group)
            
            # Tool 3: File Touch Tool
            touch_group = QGroupBox("🕒 Enhanced File Touch Tool")
            touch_layout = QVBoxLayout(touch_group)
            
            touch_desc = QLabel("Modify file timestamps including access time and modification time for individual files or batch operations.")
            touch_desc.setWordWrap(True)
            touch_desc.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
            touch_layout.addWidget(touch_desc)
            
            touch_button = QPushButton("Launch File Touch Tool")
            touch_button.clicked.connect(self.launch_file_touch_tool)
            touch_button.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
                QPushButton:pressed {
                    background-color: #ba4a00;
                }
            """)
            touch_layout.addWidget(touch_button)
            tools_layout.addWidget(touch_group)
            
            layout.addWidget(tools_group)
            
            # Launch all button
            launch_all_layout = QHBoxLayout()
            launch_all_layout.addStretch()
            
            launch_all_button = QPushButton("🚀 Launch All Tools")
            launch_all_button.clicked.connect(self.launch_all_tools)
            launch_all_button.setStyleSheet("""
                QPushButton {
                    background-color: #8e44ad;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #7d3c98;
                }
                QPushButton:pressed {
                    background-color: #6c3483;
                }
            """)
            launch_all_layout.addWidget(launch_all_button)
            launch_all_layout.addStretch()
            
            layout.addLayout(launch_all_layout)
            
            # Status and info
            status_group = QGroupBox("Implementation Details")
            status_layout = QVBoxLayout(status_group)
            
            features_text = """
            ✅ File Menu Integration - Exit and Help options in standardized menu bar
            ✅ Menu Callbacks - Registered callbacks using File Finder template pattern  
            ✅ Comprehensive Help - Detailed help dialogs with usage instructions
            ✅ Consistent UI/UX - Matching styling and behavior across all tools
            ✅ Error Handling - Graceful fallback modes and robust error handling
            ✅ StandardWindow Integration - Uses enhanced window base class when available
            """
            
            features_label = QLabel(features_text)
            features_label.setStyleSheet("""
                QLabel {
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                    color: #2c3e50;
                    background-color: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
            status_layout.addWidget(features_label)
            
            layout.addWidget(status_group)
            
        def launch_image_metadata_editor(self):
            """Launch the Enhanced Image Metadata Editor."""
            try:
                tool = EnhancedImageMetadataEditorGUI()
                tool.show()
                self.tool_windows.append(tool)
                print("✅ Launched Enhanced Image Metadata Editor")
            except Exception as e:
                print(f"❌ Error launching Image Metadata Editor: {e}")
                
        def launch_office_metadata_editor(self):
            """Launch the Enhanced Office Metadata Editor."""
            try:
                tool = EnhancedOfficeMetadataEditorGUI()
                tool.show()
                self.tool_windows.append(tool)
                print("✅ Launched Enhanced Office Metadata Editor")
            except Exception as e:
                print(f"❌ Error launching Office Metadata Editor: {e}")
                
        def launch_file_touch_tool(self):
            """Launch the Enhanced File Touch Tool."""
            try:
                tool = EnhancedFileTouchGUI()
                tool.show()
                self.tool_windows.append(tool)
                print("✅ Launched Enhanced File Touch Tool")
            except Exception as e:
                print(f"❌ Error launching File Touch Tool: {e}")
                
        def launch_all_tools(self):
            """Launch all enhanced metadata tools."""
            print("\n🚀 Launching all enhanced metadata tools...")
            self.launch_image_metadata_editor()
            self.launch_office_metadata_editor()
            self.launch_file_touch_tool()
            print("✨ All tools launched successfully!\n")
            
        def closeEvent(self, event):
            """Handle application close."""
            print("🔚 Closing Enhanced Metadata Tools Demo...")
            # Close all tool windows
            for tool in self.tool_windows:
                if tool:
                    tool.close()
            event.accept()

    def main():
        """Main demo function."""
        print("=" * 70)
        print("🎯 ENHANCED METADATA TOOLS COMPREHENSIVE DEMO")
        print("=" * 70)
        print("Starting demonstration of enhanced metadata tools with File menu integration...")
        print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Create and run the application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Modern look
        
        # Create launcher window
        launcher = MetadataToolsLauncher()
        launcher.show()
        
        print("📋 Available Enhanced Tools:")
        print("  1. Enhanced Image Metadata Editor - 📸 View image EXIF data and metadata")
        print("  2. Enhanced Office Metadata Editor - 📄 Extract office document metadata")  
        print("  3. Enhanced File Touch Tool - 🕒 Modify file timestamps")
        print()
        print("🎨 Key Features Demonstrated:")
        print("  • File menu integration with Exit and Help options")
        print("  • Standardized menu callbacks using File Finder template")
        print("  • Comprehensive help documentation")
        print("  • Consistent UI/UX design patterns")
        print("  • Error handling and fallback modes")
        print()
        print("💡 Instructions:")
        print("  • Click any tool button to launch that specific tool")
        print("  • Use 'Launch All Tools' to open all tools simultaneously")
        print("  • Each tool has a File menu with Exit and Help options")
        print("  • Access comprehensive help via File > Help in each tool")
        print()
        
        # Run the application
        sys.exit(app.exec_())

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure PyQt5 is installed and all enhanced tools are available.")
    print("Required files:")
    print("  - enhanced_image_metadata_editor_with_menu.py")
    print("  - enhanced_office_metadata_editor_with_menu.py") 
    print("  - enhanced_file_touch_with_menu.py")
    
    def main():
        print("Enhanced Metadata Tools Demo requires PyQt5 and the enhanced tool files.")
        
    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"💥 Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    
    def main():
        print("An unexpected error occurred while starting the demo.")
        
    if __name__ == "__main__":
        main()
