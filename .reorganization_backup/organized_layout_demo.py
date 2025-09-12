#!/usr/bin/env python3
"""
Organized Layout Demo - RFU Hub with Compact Grid Layouts
Demonstrates the improved button organization with grid layouts instead of spread-out buttons
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QTabWidget, QStatusBar,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class StyledToolButton(QPushButton):
    """Styled tool button for organized grid layout."""
    
    def __init__(self, text, tooltip, callback, primary=True):
        super().__init__(text)
        self.setToolTip(tooltip)
        self.clicked.connect(callback)
        self.setMinimumSize(180, 70)
        self.setMaximumSize(200, 80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5dade2, stop:1 #3498db);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #1f618d);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ecf0f1, stop:1 #bdc3c7);
                    color: #2c3e50;
                    border: 1px solid #95a5a6;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #ecf0f1);
                    border: 1px solid #7f8c8d;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #bdc3c7, stop:1 #95a5a6);
                }
            """)


class OrganizedRFUHub(QMainWindow):
    """RFU Hub with organized grid layouts for better button arrangement."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Richard's File Utilities - Organized Layout Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # Set up the main interface
        self.setup_ui()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("RFU Hub with Organized Grid Layout - Ready")
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = QLabel("Richard's File Utilities Hub")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin: 10px 0px 20px 0px; padding: 10px;")
        main_layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Organized Grid Layout - Professional Button Arrangement")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)
        
        # Tab widget for organized categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px 16px;
                margin-right: 1px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font: normal 9pt "Segoe UI";
                min-width: 80px;
                max-width: 140px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        main_layout.addWidget(self.tab_widget)
        
        # Create organized tabs
        self.create_analysis_tools_tab()
        self.create_file_operations_tab()
        self.create_metadata_tools_tab()
        self.create_privacy_tools_tab()
        self.create_network_tools_tab()
        self.create_security_tools_tab()
        self.create_pdf_tools_tab()
        self.create_system_tools_tab()
    
    def create_analysis_tools_tab(self):
        """Create Analysis Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("📊 Analysis Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Analyze file properties, find duplicates, and check data integrity")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("📏 Size Analyzer", "Analyze disk usage and file sizes", self.tool_clicked),
            ("🔍 Duplicate Finder", "Find and manage duplicate files", self.tool_clicked),
            ("📁 Empty Folders", "Find and clean empty directories", self.tool_clicked),
            ("✅ Checksum Tools", "Verify file integrity with checksums", self.tool_clicked),
            ("🗂️ File Catalog", "Generate comprehensive file catalogs", self.tool_clicked),
            ("📋 Tree Map", "Visual representation of disk usage", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Analysis")
    
    def create_file_operations_tab(self):
        """Create File Operations tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("📂 File Operations")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("File manipulation, splitting, copying, and synchronization tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("✂️ File Splitter", "Split large files into smaller chunks", self.tool_clicked),
            ("📋 Copy/Move/Sync", "Advanced file copy, move, and sync operations", self.tool_clicked),
            ("🔄 Backup Tools", "Synchronization and backup utilities", self.tool_clicked),
            ("⏰ File Touch", "Modify file timestamps and attributes", self.tool_clicked),
            ("📁 Organize Files", "Organize files automatically by rules", self.tool_clicked),
            ("🏷️ Batch Rename", "Rename multiple files with patterns", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "File Ops")
    
    def create_metadata_tools_tab(self):
        """Create Metadata Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("🏷️ Metadata Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("View and edit file metadata, EXIF data, and document properties")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("🖼️ Image Metadata", "Edit image metadata and properties", self.tool_clicked),
            ("📄 Office Documents", "Edit office document metadata", self.tool_clicked),
            ("📷 EXIF Data Viewer", "View and edit EXIF camera data", self.tool_clicked),
            ("🔍 Metadata Analyzer", "Analyze file metadata patterns", self.tool_clicked),
            ("🏷️ Tag Editor", "Edit file tags and labels", self.tool_clicked),
            ("📊 Property Inspector", "Inspect detailed file properties", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Metadata")
    
    def create_privacy_tools_tab(self):
        """Create Privacy Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("🛡️ Privacy Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Privacy protection, data cleanup, and secure browsing tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("🧹 Privacy Cleaner", "Clean privacy traces and personal data", self.tool_clicked),
            ("🗂️ Temp File Cleanup", "Remove temporary and cache files", self.tool_clicked),
            ("🌐 Browser Cleanup", "Clear browsing history and cookies", self.tool_clicked),
            ("⚙️ Privacy Settings", "Configure privacy and security settings", self.tool_clicked),
            ("🔍 Data Scanner", "Scan for sensitive data exposure", self.tool_clicked),
            ("🛡️ Privacy Shield", "Advanced privacy protection tools", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Privacy")

    def create_network_tools_tab(self):
        """Create Network Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("🌐 Network Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Network connectivity, scanning, file transfer, and remote access tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("🌐 Network Scanner", "Scan and discover network devices", self.tool_clicked),
            ("🔌 Connectivity Test", "Test network connectivity and speed", self.tool_clicked),
            ("📡 Network Transfer", "Transfer files over network", self.tool_clicked),
            ("🔗 Bookmark Manager", "Manage network bookmarks and links", self.tool_clicked),
            ("📊 Bandwidth Monitor", "Monitor network bandwidth usage", self.tool_clicked),
            ("🛡️ Network Security", "Network security analysis tools", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Network")
    
    def create_security_tools_tab(self):
        """Create Security Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("🔐 Security Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("File encryption, secure deletion, and security analysis tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("🔒 File Encryption", "Encrypt files and folders securely", self.tool_clicked),
            ("�️ Secure Delete", "Permanently delete sensitive files", self.tool_clicked),
            ("🔑 Password Generator", "Generate strong, secure passwords", self.tool_clicked),
            ("🔍 Security Scan", "Scan for security vulnerabilities", self.tool_clicked),
            ("�️ Security Monitor", "Monitor system security status", self.tool_clicked),
            ("⚙️ Security Settings", "Configure security preferences", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Security")
    
    def create_pdf_tools_tab(self):
        """Create PDF Tools tab with organized 2x3 grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("📄 PDF Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Comprehensive PDF operations, merging, splitting, and security")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("📄 PDF Merger", "Combine multiple PDFs into one", self.tool_clicked),
            ("✂️ PDF Splitter", "Split PDF into separate pages", self.tool_clicked),
            ("� PDF Converter", "Convert PDFs to other formats", self.tool_clicked),
            ("� PDF Security", "Add passwords and encryption", self.tool_clicked),
            ("� PDF Analysis", "Analyze PDF structure and content", self.tool_clicked),
            ("�️ PDF Optimizer", "Optimize and compress PDFs", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "PDF")
    
    def create_system_tools_tab(self):
        """Create System Tools tab with organized 3-column grid."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("⚙️ System Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("System monitoring, analysis, and maintenance tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 20px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools organized in 3 columns
        tools = [
            ("💻 System Information", "View detailed system specifications", self.tool_clicked),
            ("� Disk Usage Analyzer", "Analyze disk space usage and cleanup", self.tool_clicked),
            ("⚡ Process Monitor", "Monitor running processes and services", self.tool_clicked),
            ("🧹 System Cleanup", "Clean temporary files and system cache", self.tool_clicked),
            ("� Performance Monitor", "Monitor system performance metrics", self.tool_clicked),
            ("⚙️ System Settings", "Configure system preferences", self.tool_clicked),
        ]
        
        self.add_tools_to_grid(grid_layout, tools, max_cols=3)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "System")
    
    def add_tools_to_grid(self, grid_layout, tools, max_cols=3):
        """Add tools to grid layout in organized columns."""
        row, col = 0, 0
        
        for tool_name, tooltip, callback in tools:
            btn = StyledToolButton(tool_name, tooltip, callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def tool_clicked(self):
        """Handle tool button clicks."""
        sender = self.sender()
        tool_name = sender.text()
        self.status_bar.showMessage(f"{tool_name} - Feature demonstration (organized layout)")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("RFU Organized Layout Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = OrganizedRFUHub()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()