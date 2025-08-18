"""
Simple RFU Hub - A working GUI interface without complex dependencies.

This is a simplified version of the RFU Hub that focuses on basic functionality
while avoiding import issues.
"""

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTabWidget, QTextEdit,
    QStatusBar, QApplication, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from .log_manager import get_log_manager
from .config_manager import get_config_manager

# Import the simplified menu system
from .simple_menu_manager import SimpleMenuManager


class SimpleRFUHub(QMainWindow):
    """A simple RFU Hub interface that actually works."""
    
    def __init__(self):
        """Initialize the simple hub."""
        super().__init__()
        
        # Initialize core components
        self.logger = get_log_manager().get_logger('SimpleRFUHub')
        self.config = get_config_manager()
        
        self.logger.info("Simple RFU Hub initializing...")
        
        # Initialize menu system
        self.menu_manager = SimpleMenuManager(self)
        self.menu_manager.create_menubar()
        self._setup_menu_callbacks()
        self.logger.info("Menu system initialized")
        
        # Set up the window
        self.setWindowTitle("Richard's File Utilities - Main Hub")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Richard's File Utilities")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs based on utilities folder structure
        self.create_analysis_tab()
        self.create_file_operations_tab()
        self.create_metadata_tab()
        self.create_network_tab()
        self.create_pdf_tools_tab()
        self.create_privacy_tab()
        self.create_security_tab()
        self.create_system_tab()
        self.create_logs_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("RFU Hub initialized successfully")
        
        self.logger.info("Simple RFU Hub initialized successfully")
    
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
        """Create a styled tool button with organized layout."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setMinimumSize(180, 70)
        button.setMaximumSize(200, 80)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if primary:
            button.setStyleSheet("""
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
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #1f618d);
                }
            """)
        else:
            button.setStyleSheet("""
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
        
        return button
    
    # Menu callback implementations
    def new_project(self):
        """Create a new project."""
        self.status_bar.showMessage("New Project - Feature coming soon...")
        self.logger.info("New Project requested")
    
    def open_file(self):
        """Open a file."""
        self.status_bar.showMessage("Open File - Feature coming soon...")
        self.logger.info("Open File requested")
    
    def save_file(self):
        """Save current work."""
        self.status_bar.showMessage("Save File - Feature coming soon...")
        self.logger.info("Save File requested")
    
    def save_as_file(self):
        """Save with new name."""
        self.status_bar.showMessage("Save As - Feature coming soon...")
        self.logger.info("Save As requested")
    
    def export_data(self):
        """Export data."""
        self.status_bar.showMessage("Export Data - Feature coming soon...")
        self.logger.info("Export Data requested")
    
    def import_data(self):
        """Import data."""
        self.status_bar.showMessage("Import Data - Feature coming soon...")
        self.logger.info("Import Data requested")
    
    def print_document(self):
        """Print current document."""
        self.status_bar.showMessage("Print Document - Feature coming soon...")
        self.logger.info("Print Document requested")
    
    def show_preferences(self):
        """Show preferences dialog."""
        self.status_bar.showMessage("Preferences - Feature coming soon...")
        self.logger.info("Preferences requested")
    
    def undo(self):
        """Undo last action."""
        self.status_bar.showMessage("Undo - Feature coming soon...")
        self.logger.info("Undo requested")
    
    def redo(self):
        """Redo last action."""
        self.status_bar.showMessage("Redo - Feature coming soon...")
        self.logger.info("Redo requested")
    
    def cut(self):
        """Cut to clipboard."""
        self.status_bar.showMessage("Cut - Feature coming soon...")
        self.logger.info("Cut requested")
    
    def copy(self):
        """Copy to clipboard."""
        self.status_bar.showMessage("Copy - Feature coming soon...")
        self.logger.info("Copy requested")
    
    def paste(self):
        """Paste from clipboard."""
        self.status_bar.showMessage("Paste - Feature coming soon...")
        self.logger.info("Paste requested")
    
    def select_all(self):
        """Select all items."""
        self.status_bar.showMessage("Select All - Feature coming soon...")
        self.logger.info("Select All requested")
    
    def find(self):
        """Find text or items."""
        self.status_bar.showMessage("Find - Feature coming soon...")
        self.logger.info("Find requested")
    
    def replace(self):
        """Find and replace."""
        self.status_bar.showMessage("Replace - Feature coming soon...")
        self.logger.info("Replace requested")
    
    def zoom_in(self):
        """Increase zoom level."""
        self.status_bar.showMessage("Zoom In - Feature coming soon...")
        self.logger.info("Zoom In requested")
    
    def zoom_out(self):
        """Decrease zoom level."""
        self.status_bar.showMessage("Zoom Out - Feature coming soon...")
        self.logger.info("Zoom Out requested")
    
    def zoom_reset(self):
        """Reset zoom to default."""
        self.status_bar.showMessage("Zoom Reset - Feature coming soon...")
        self.logger.info("Zoom Reset requested")
    
    def refresh(self):
        """Refresh current view."""
        self.load_recent_logs()
        self.status_bar.showMessage("View refreshed")
        self.logger.info("Refresh requested")
    
    def show_options(self):
        """Show tool options."""
        self.status_bar.showMessage("Options - Feature coming soon...")
        self.logger.info("Options requested")
    
    def show_performance(self):
        """Show performance monitor."""
        self.status_bar.showMessage("Performance Monitor - Feature coming soon...")
        self.logger.info("Performance Monitor requested")
    
    def create_analysis_tab(self):
        """Create the Analysis tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Analysis Tools")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #2c3e50; margin: 10px 0px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for analyzing file properties, finding duplicates, and checking data integrity")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Create organized grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        # Analysis tools in organized grid (3 columns)
        tools = [
            ("📊 Size Analyzer", "Analyze disk usage and file sizes", self.open_size_analyzer),
            ("🔍 Duplicate Finder", "Find and manage duplicate files", self.open_duplicate_finder),
            ("📁 Empty Folders", "Find and clean empty directories", self.open_empty_folders),
            ("✅ Checksum Verification", "Verify file integrity with checksums", self.open_checksum),
            ("📋 Import Validator", "Validate imported data", self.open_import_validator),
            ("🗂️ File Catalog", "Generate comprehensive file catalogs", self.open_file_catalog),
        ]
        
        row, col = 0, 0
        max_cols = 3  # 3 columns for organized layout
        
        for title_text, tooltip, callback in tools:
            btn = self._create_styled_tool_button(title_text, tooltip, callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Analysis")
    
    def create_file_operations_tab(self):
        """Create the File Operations tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("File Operations")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #2c3e50; margin: 10px 0px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for file manipulation, splitting, copying, and synchronization")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Create organized grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        # File operations tools in organized grid
        tools = [
            ("📂 File Splitter", "Split large files into smaller chunks", self.open_file_splitter),
            ("📋 Copy/Move/Sync", "Advanced file operations", self.open_cmsd_logic),
            ("🔄 Sync & Backup", "Synchronization and backup tools", self.open_sync_backup),
            ("⏰ File Touch", "Modify file timestamps", self.open_file_touch),
            ("📁 Organize Files", "Organize files by rules", self.open_organize_files),
            ("🗂️ Batch Rename", "Rename multiple files", self.open_batch_rename),
        ]
        
        row, col = 0, 0
        max_cols = 3  # 3 columns for organized layout
        
        for title_text, tooltip, callback in tools:
            btn = self._create_styled_tool_button(title_text, tooltip, callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "File Operations")
    
    def create_metadata_tab(self):
        """Create the Metadata tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Metadata Tools")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #2c3e50; margin: 10px 0px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for viewing and editing file metadata, EXIF data, and document properties")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Create organized grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        # Metadata tools in organized grid (3 columns)
        tools = [
            ("🖼️ Image Metadata", "Edit image metadata and properties", self.open_image_metadata),
            ("📄 Office Documents", "Edit office document metadata", self.open_office_metadata),
            ("📷 EXIF Data Viewer", "View and edit EXIF camera data", self.open_exif_viewer),
            ("🔍 Metadata Analyzer", "Analyze file metadata patterns", self.open_metadata_analyzer),
            ("🏷️ Tag Editor", "Edit file tags and labels", self.open_tag_editor),
            ("📊 Property Inspector", "Inspect detailed file properties", self.open_property_inspector),
        ]
        
        row, col = 0, 0
        max_cols = 3  # 3 columns for organized layout
        
        for title_text, tooltip, callback in tools:
            btn = self._create_styled_tool_button(title_text, tooltip, callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Metadata")
    
    def create_network_tab(self):
        """Create the Network tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Network Tools")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #2c3e50; margin: 10px 0px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Network connectivity, scanning, file transfer, and remote access tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px; font-size: 10px;")
        layout.addWidget(desc)
        
        # Create organized grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        # Network tools in organized grid (3 columns)
        tools = [
            ("🌐 Network Scanner", "Scan and discover network devices", self.open_network_scanner),
            ("🔌 Connectivity Test", "Test network connectivity and speed", self.open_connectivity_test),
            ("📡 Network Transfer", "Transfer files over network", self.open_network_transfer),
            ("🔗 Bookmark Manager", "Manage network bookmarks and links", self.open_bookmark_manager),
            ("📊 Bandwidth Monitor", "Monitor network bandwidth usage", self.open_bandwidth_monitor),
            ("🛡️ Network Security", "Network security analysis tools", self.open_network_security),
        ]
        
        row, col = 0, 0
        max_cols = 3  # 3 columns for organized layout
        
        for title_text, tooltip, callback in tools:
            btn = self._create_styled_tool_button(title_text, tooltip, callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Network")
    
    def create_pdf_tools_tab(self):
        """Create the PDF Tools tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel("PDF Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("PDF processing, conversion, security, and analysis tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced PDF tools with icons and descriptions (3×2 grid)
        tools = [
            ("📄 PDF Merger", "Combine multiple PDFs into one", self.open_pdf_merger),
            ("✂️ PDF Splitter", "Split PDF into separate pages", self.open_pdf_splitter),
            ("🔄 PDF Converter", "Convert PDFs to other formats", self.open_pdf_converter),
            ("🔒 PDF Security", "Add passwords and encryption", self.open_pdf_security),
            ("🔍 PDF Analysis", "Analyze PDF structure and content", self.open_pdf_analysis),
            ("🖼️ PDF Optimizer", "Optimize and compress PDFs", self.open_pdf_optimizer)
        ]
        
        # Add tools to grid (3 columns, 2 rows)
        for i, (title_text, desc_text, callback) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_btn = self._create_styled_tool_button(title_text, desc_text, callback)
            grid_layout.addWidget(tool_btn, row, col)
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "PDF Tools")
    
    def create_privacy_tab(self):
        """Create the Privacy tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel("Privacy Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Privacy protection, data cleanup, and secure browsing tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced privacy tools with icons and descriptions (3×2 grid)
        tools = [
            ("🧹 Privacy Cleaner", "Clean privacy traces and personal data", self.open_privacy_cleaner),
            ("🗂️ Temp File Cleanup", "Remove temporary and cache files", self.open_temp_cleanup),
            ("🌐 Browser Cleanup", "Clear browsing history and cookies", self.open_browser_cleanup),
            ("⚙️ Privacy Settings", "Configure privacy and security settings", self.open_privacy_settings),
            ("🔍 Data Scanner", "Scan for sensitive data exposure", self.open_data_scanner),
            ("🛡️ Privacy Shield", "Advanced privacy protection tools", self.open_privacy_shield)
        ]
        
        # Add tools to grid (3 columns, 2 rows)
        for i, (title_text, desc_text, callback) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_btn = self._create_styled_tool_button(title_text, desc_text, callback)
            grid_layout.addWidget(tool_btn, row, col)
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Privacy")
    
    def create_security_tab(self):
        """Create the Security tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel("Security Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("File encryption, secure deletion, and security analysis tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced security tools with icons and descriptions (3×2 grid)
        tools = [
            ("🔒 File Encryption", "Encrypt files and folders securely", self.open_file_encryption),
            ("🗑️ Secure Delete", "Permanently delete sensitive files", self.open_secure_delete),
            ("🔑 Password Generator", "Generate strong, secure passwords", self.open_password_generator),
            ("🔍 Security Scan", "Scan for security vulnerabilities", self.open_security_scan),
            ("🛡️ Security Monitor", "Monitor system security status", self.open_security_monitor),
            ("⚙️ Security Settings", "Configure security preferences", self.open_security_settings)
        ]
        
        # Add tools to grid (3 columns, 2 rows)
        for i, (title_text, desc_text, callback) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_btn = self._create_styled_tool_button(title_text, desc_text, callback)
            grid_layout.addWidget(tool_btn, row, col)
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "Security")
    
    def create_system_tab(self):
        """Create the System tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel("System Tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("System monitoring, analysis, and maintenance tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced system tools with icons and descriptions (3×2 grid)
        tools = [
            ("💻 System Information", "View detailed system specifications", self.open_system_info),
            ("💿 Disk Usage Analyzer", "Analyze disk space usage and cleanup", self.open_disk_analyzer),
            ("⚡ Process Monitor", "Monitor running processes and services", self.open_process_monitor),
            ("🧹 System Cleanup", "Clean temporary files and system cache", self.open_system_cleanup),
            ("📊 Performance Monitor", "Monitor system performance metrics", self.open_performance_monitor),
            ("⚙️ System Settings", "Configure system preferences", self.open_system_settings)
        ]
        
        # Add tools to grid (3 columns, 2 rows)
        for i, (title_text, desc_text, callback) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_btn = self._create_styled_tool_button(title_text, desc_text, callback)
            grid_layout.addWidget(tool_btn, row, col)
        
        layout.addWidget(grid_widget)
        layout.addStretch()
        self.tab_widget.addTab(tab, "System")
    
    def create_logs_tab(self):
        """Create the logs tab with enhanced display and professional styling."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel("Application Logs")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Real-time application logs and system monitoring")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Enhanced log viewer with professional styling
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #2c3e50;
                selection-background-color: #3498db;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.log_viewer.setMinimumHeight(350)
        layout.addWidget(self.log_viewer)
        
        # Load recent logs
        self.load_recent_logs()
        
        # Professional control buttons in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Refresh button with icon and styling
        refresh_btn = QPushButton("🔄 Refresh Logs")
        refresh_btn.clicked.connect(self.load_recent_logs)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #4CAF50, stop: 1 #45a049);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #5CBF60, stop: 1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #45a049, stop: 1 #3d8b40);
            }
        """)
        controls_layout.addWidget(refresh_btn)
        
        # Clear logs button
        clear_btn = QPushButton("🗑️ Clear Display")
        clear_btn.clicked.connect(self.clear_log_display)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #f39c12, stop: 1 #e67e22);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #f7a41e, stop: 1 #f39c12);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #e67e22, stop: 1 #d35400);
            }
        """)
        controls_layout.addWidget(clear_btn)
        
        # Export logs button
        export_btn = QPushButton("💾 Export Logs")
        export_btn.clicked.connect(self.export_logs)
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #4DA6E5, stop: 1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                           stop: 0 #2980b9, stop: 1 #1f5582);
            }
        """)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()  # Push buttons to the left
        layout.addLayout(controls_layout)
        
        self.tab_widget.addTab(tab, "Logs")
    
    def load_recent_logs(self):
        """Load and display recent log entries."""
        try:
            import os
            log_file = os.path.join("logs", "rfu.log")
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Show last 50 lines
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    self.log_viewer.setPlainText(''.join(recent_lines))
            else:
                self.log_viewer.setPlainText("No log file found yet.")
        except Exception as e:
            self.log_viewer.setPlainText(f"Error loading logs: {e}")
    
    def clear_log_display(self):
        """Clear the log display (not the log file)."""
        self.log_viewer.clear()
        self.log_viewer.setPlainText(
            "Log display cleared. Click 'Refresh Logs' to reload.")
        self.status_bar.showMessage("Log display cleared")
        self.logger.info("Log display cleared by user")
    
    def export_logs(self):
        """Export current logs to file."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"exported_logs_{timestamp}.txt"
            
            log_content = self.log_viewer.toPlainText()
            if log_content:
                with open(export_filename, 'w', encoding='utf-8') as f:
                    f.write("# RFU Application Logs Export\n")
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                    f.write(f"# Exported on: {timestamp_str}\n")
                    f.write("# " + "=" * 38 + "\n\n")
                    f.write(log_content)
                
                self.status_bar.showMessage(
                    f"Logs exported to {export_filename}")
                self.logger.info(f"Logs exported to {export_filename}")
            else:
                self.status_bar.showMessage("No logs to export")
                self.logger.info(
                    "Export logs requested but no content available")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting logs: {e}")
            self.logger.error(f"Error exporting logs: {e}")
    
    # Analysis Tools Methods
    def open_checksum(self):
        """Open checksum verification tool."""
        try:
            # Import and launch the checksum tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from utilities.analysis.check_sum import ChecksumGUI
            
            # Create and show the checksum window
            if not hasattr(self, 'checksum_window') or \
               self.checksum_window is None:
                self.checksum_window = ChecksumGUI()
            
            self.checksum_window.show()
            self.checksum_window.raise_()
            self.checksum_window.activateWindow()
            
            self.status_bar.showMessage("Checksum Verification opened successfully")
            self.logger.info("Checksum Verification tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Checksum tool not available")
            self.logger.error(f"ImportError opening Checksum tool: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Checksum tool: {e}")
            self.logger.error(f"Error opening Checksum tool: {e}")
    
    def open_duplicate_finder(self):
        """Open duplicate file finder."""
        try:
            # Import and launch the duplicate finder tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from utilities.analysis.find_duplicate_files import (
                DuplicateFinderApp)
            
            # Create and show the duplicate finder window
            if not hasattr(self, 'duplicate_finder_window') or \
               self.duplicate_finder_window is None:
                self.duplicate_finder_window = DuplicateFinderApp()
            
            self.duplicate_finder_window.show()
            self.duplicate_finder_window.raise_()
            self.duplicate_finder_window.activateWindow()
            
            self.status_bar.showMessage("Duplicate Finder opened successfully")
            self.logger.info("Duplicate File Finder tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Duplicate Finder tool not available")
            self.logger.error(f"ImportError opening Duplicate Finder: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Duplicate Finder: {e}")
            self.logger.error(f"Error opening Duplicate Finder: {e}")
    
    def open_size_analyzer(self):
        """Open size analyzer."""
        try:
            # Import and launch the size analyzer tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            root_dir = os.path.join(src_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from utilities.analysis.size_analyzer import SizeAnalyzerGUI
            
            # Create and show the size analyzer window
            if not hasattr(self, 'size_analyzer_window') or \
               self.size_analyzer_window is None:
                self.size_analyzer_window = SizeAnalyzerGUI()
            
            self.size_analyzer_window.show()
            self.size_analyzer_window.raise_()
            self.size_analyzer_window.activateWindow()
            
            self.status_bar.showMessage("Size Analyzer opened successfully")
            self.logger.info("Size Analyzer tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Size Analyzer tool not available")
            self.logger.error(f"ImportError opening Size Analyzer: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Size Analyzer: {e}")
            self.logger.error(f"Error opening Size Analyzer: {e}")
    
    def open_import_validator(self):
        """Open import validator."""
        try:
            # Try to import and launch the enhanced import validator tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Import Validator - Feature coming soon...")
            self.logger.info("Import Validator requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Import Validator: {e}")
            self.logger.error(f"Error opening Import Validator: {e}")
    
    def open_empty_folders(self):
        """Open empty folders finder."""
        try:
            # Try to import and launch the enhanced empty folders tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Empty Folders Finder - Feature coming soon...")
            self.logger.info("Empty Folders Finder requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Empty Folders tool: {e}")
            self.logger.error(f"Error opening Empty Folders tool: {e}")
    
    def open_file_catalog(self):
        """Open file catalog generator."""
        try:
            # Try to import and launch the enhanced file catalog tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("File Catalog Generator - Feature coming soon...")
            self.logger.info("File Catalog Generator requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Catalog tool: {e}")
            self.logger.error(f"Error opening File Catalog tool: {e}")
    
    # File Operations Methods
    def open_file_splitter(self):
        """Open file splitter."""
        try:
            # Try to import and launch the enhanced file splitter tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("File Splitter - Feature coming soon...")
            self.logger.info("File Splitter requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Splitter: {e}")
            self.logger.error(f"Error opening File Splitter: {e}")
    
    def open_cmsd_logic(self):
        """Open CMSD logic tool."""
        try:
            # Try to import and launch the enhanced CMSD logic tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("CMSD Logic - Feature coming soon...")
            self.logger.info("CMSD Logic requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening CMSD Logic: {e}")
            self.logger.error(f"Error opening CMSD Logic: {e}")
    
    def open_sync_backup(self):
        """Open synchronization and backup."""
        try:
            # Try to import and launch the enhanced sync/backup tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Synchronization & Backup - Feature coming soon...")
            self.logger.info("Synchronization & Backup requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Sync/Backup: {e}")
            self.logger.error(f"Error opening Sync/Backup: {e}")
    
    def open_file_touch(self):
        """Open file touch operations."""
        try:
            # Import and launch the enhanced file touch tool
            import sys
            import os
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_file_touch_with_menu import EnhancedFileTouchGUI
            
            # Create and show the file touch window
            if not hasattr(self, 'file_touch_window') or self.file_touch_window is None:
                self.file_touch_window = EnhancedFileTouchGUI()
            
            self.file_touch_window.show()
            self.file_touch_window.raise_()
            self.file_touch_window.activateWindow()
            
            self.status_bar.showMessage("File Touch tool opened successfully")
            self.logger.info("File Touch tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("File Touch tool not available")
            self.logger.error(f"ImportError opening File Touch: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Touch tool: {e}")
            self.logger.error(f"Error opening File Touch tool: {e}")
    
    def open_organize_files(self):
        """Open file organization tool."""
        try:
            # Try to import and launch the enhanced file organization tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("File Organization - Feature coming soon...")
            self.logger.info("File Organization requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Organization: {e}")
            self.logger.error(f"Error opening File Organization: {e}")
    
    def open_batch_rename(self):
        """Open batch rename tool."""
        try:
            # Try to import and launch the enhanced batch rename tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Batch Rename - Feature coming soon...")
            self.logger.info("Batch Rename requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Batch Rename: {e}")
            self.logger.error(f"Error opening Batch Rename: {e}")
        self.status_bar.showMessage("File Touch Operations - Feature coming soon...")
        self.logger.info("File Touch Operations requested")
    
    def open_organize_files(self):
        """Open organize files tool."""
        self.status_bar.showMessage("Organize Files - Feature coming soon...")
        self.logger.info("Organize Files requested")
    
    def open_batch_rename(self):
        """Open batch rename tool."""
        self.status_bar.showMessage("Batch Rename - Feature coming soon...")
        self.logger.info("Batch Rename requested")
    
    # Metadata Tools Methods
    def open_image_metadata(self):
        """Open image metadata editor."""
        try:
            # Import and launch the enhanced image metadata editor
            import sys
            import os
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_image_metadata_editor_with_menu import EnhancedImageMetadataEditorGUI
            
            # Create and show the image metadata editor
            if not hasattr(self, 'image_metadata_window') or self.image_metadata_window is None:
                self.image_metadata_window = EnhancedImageMetadataEditorGUI()
            
            self.image_metadata_window.show()
            self.image_metadata_window.raise_()
            self.image_metadata_window.activateWindow()
            
            self.status_bar.showMessage("Image Metadata Editor opened successfully")
            self.logger.info("Image Metadata Editor opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Image Metadata Editor not available")
            self.logger.error(f"ImportError opening Image Metadata Editor: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Image Metadata Editor: {e}")
            self.logger.error(f"Error opening Image Metadata Editor: {e}")
    
    def open_office_metadata(self):
        """Open office document metadata."""
        try:
            # Import and launch the enhanced office metadata editor
            import sys
            import os
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_office_metadata_editor_with_menu import EnhancedOfficeMetadataEditorGUI
            
            # Create and show the office metadata editor
            if not hasattr(self, 'office_metadata_window') or self.office_metadata_window is None:
                self.office_metadata_window = EnhancedOfficeMetadataEditorGUI()
            
            self.office_metadata_window.show()
            self.office_metadata_window.raise_()
            self.office_metadata_window.activateWindow()
            
            self.status_bar.showMessage("Office Metadata Editor opened successfully")
            self.logger.info("Office Metadata Editor opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Office Metadata Editor not available")
            self.logger.error(f"ImportError opening Office Metadata Editor: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Office Metadata Editor: {e}")
            self.logger.error(f"Error opening Office Metadata Editor: {e}")
    
    def open_exif_viewer(self):
        """Open EXIF data viewer."""
        try:
            # Try to import and launch the enhanced EXIF viewer tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("EXIF Data Viewer - Feature coming soon...")
            self.logger.info("EXIF Data Viewer requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening EXIF Viewer: {e}")
            self.logger.error(f"Error opening EXIF Viewer: {e}")
    
    def open_metadata_analyzer(self):
        """Open metadata analyzer."""
        try:
            # Try to import and launch the enhanced metadata analyzer tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Metadata Analyzer - Feature coming soon...")
            self.logger.info("Metadata Analyzer requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Metadata Analyzer: {e}")
            self.logger.error(f"Error opening Metadata Analyzer: {e}")
    
    def open_tag_editor(self):
        """Open tag editor."""
        try:
            # Try to import and launch the enhanced tag editor tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Tag Editor - Feature coming soon...")
            self.logger.info("Tag Editor requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Tag Editor: {e}")
            self.logger.error(f"Error opening Tag Editor: {e}")
    
    def open_property_inspector(self):
        """Open property inspector."""
        try:
            # Try to import and launch the enhanced property inspector tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Property Inspector - Feature coming soon...")
            self.logger.info("Property Inspector requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Property Inspector: {e}")
            self.logger.error(f"Error opening Property Inspector: {e}")
        """Open property inspector."""
        self.status_bar.showMessage("Property Inspector - Feature coming soon...")
        self.logger.info("Property Inspector requested")
    
    # Network Tools Methods
    def open_network_scanner(self):
        """Open network scanner."""
        self.status_bar.showMessage("Network Scanner - Feature coming soon...")
        self.logger.info("Network Scanner requested")
    
    def open_connectivity_test(self):
        """Open connectivity test."""
        self.status_bar.showMessage("Connectivity Test - Feature coming soon...")
        self.logger.info("Connectivity Test requested")
    
    def open_network_transfer(self):
        """Open network transfer."""
        self.status_bar.showMessage("Network Transfer - Feature coming soon...")
        self.logger.info("Network Transfer requested")
    
    def open_bookmark_manager(self):
        """Open bookmark manager."""
        self.status_bar.showMessage("Bookmark Manager - Feature coming soon...")
        self.logger.info("Bookmark Manager requested")
    
    def open_bandwidth_monitor(self):
        """Open bandwidth monitor."""
        self.status_bar.showMessage("Bandwidth Monitor - Feature coming soon...")
        self.logger.info("Bandwidth Monitor requested")
    
    def open_network_security(self):
        """Open network security tools."""
        self.status_bar.showMessage("Network Security - Feature coming soon...")
        self.logger.info("Network Security requested")
    
    # PDF Tools Methods
    def open_pdf_merger(self):
        """Open PDF merger."""
        self.status_bar.showMessage("PDF Merger - Feature coming soon...")
        self.logger.info("PDF Merger requested")
    
    def open_pdf_splitter(self):
        """Open PDF splitter."""
        self.status_bar.showMessage("PDF Splitter - Feature coming soon...")
        self.logger.info("PDF Splitter requested")
    
    def open_pdf_converter(self):
        """Open PDF converter."""
        self.status_bar.showMessage("PDF Converter - Feature coming soon...")
        self.logger.info("PDF Converter requested")
    
    def open_pdf_security(self):
        """Open PDF security."""
        self.status_bar.showMessage("PDF Security - Feature coming soon...")
        self.logger.info("PDF Security requested")
    
    def open_pdf_analysis(self):
        """Open PDF analysis."""
        self.status_bar.showMessage("PDF Analysis - Feature coming soon...")
        self.logger.info("PDF Analysis requested")
    
    def open_pdf_optimizer(self):
        """Open PDF optimizer."""
        self.status_bar.showMessage("PDF Optimizer - Feature coming soon...")
        self.logger.info("PDF Optimizer requested")
    
    # Privacy Tools Methods
    def open_privacy_cleaner(self):
        """Open privacy cleaner."""
        self.status_bar.showMessage("Privacy Cleaner - Feature coming soon...")
        self.logger.info("Privacy Cleaner requested")
    
    def open_temp_cleanup(self):
        """Open temporary file cleanup."""
        self.status_bar.showMessage("Temporary File Cleanup - Feature coming soon...")
        self.logger.info("Temporary File Cleanup requested")
    
    def open_browser_cleanup(self):
        """Open browser history cleaner."""
        self.status_bar.showMessage("Browser History Cleaner - Feature coming soon...")
        self.logger.info("Browser History Cleaner requested")
    
    def open_privacy_settings(self):
        """Open privacy settings."""
        self.status_bar.showMessage("Privacy Settings - Feature coming soon...")
        self.logger.info("Privacy Settings requested")
    
    def open_data_scanner(self):
        """Open data scanner."""
        self.status_bar.showMessage("Data Scanner - Feature coming soon...")
        self.logger.info("Data Scanner requested")
    
    def open_privacy_shield(self):
        """Open privacy shield."""
        self.status_bar.showMessage("Privacy Shield - Feature coming soon...")
        self.logger.info("Privacy Shield requested")
    
    # Security Tools Methods
    def open_file_encryption(self):
        """Open file encryption."""
        try:
            # Import and launch the enhanced encryption/decryption tool
            import sys
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_encrypt_decrypt_with_menu import EnAndDecryptGUI
            
            # Create and show the encryption window
            if not hasattr(self, 'encryption_window') or self.encryption_window is None:
                self.encryption_window = EnAndDecryptGUI()
            
            self.encryption_window.show()
            self.encryption_window.raise_()
            self.encryption_window.activateWindow()
            
            self.status_bar.showMessage("File Encryption tool opened successfully")
            self.logger.info("File Encryption tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("File Encryption tool not available")
            self.logger.error(f"ImportError opening File Encryption: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Encryption: {e}")
            self.logger.error(f"Error opening File Encryption: {e}")
    
    def open_secure_delete(self):
        """Open secure delete."""
        try:
            # Import and launch the enhanced secure delete tool
            import sys
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_secure_delete_with_menu import EnhancedSecureDeleteGUI
            
            # Create and show the secure delete window
            if not hasattr(self, 'secure_delete_window') or self.secure_delete_window is None:
                self.secure_delete_window = EnhancedSecureDeleteGUI()
            
            self.secure_delete_window.show()
            self.secure_delete_window.raise_()
            self.secure_delete_window.activateWindow()
            
            self.status_bar.showMessage("Secure Delete tool opened successfully")
            self.logger.info("Secure Delete tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Secure Delete tool not available")
            self.logger.error(f"ImportError opening Secure Delete: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Secure Delete: {e}")
            self.logger.error(f"Error opening Secure Delete: {e}")
    
    def open_password_generator(self):
        """Open password generator."""
        try:
            # Try to import and launch the enhanced password generator tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Password Generator - Feature coming soon...")
            self.logger.info("Password Generator requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Password Generator: {e}")
            self.logger.error(f"Error opening Password Generator: {e}")
    
    def open_security_scan(self):
        """Open security scan."""
        try:
            # Try to import and launch the enhanced security scan tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Security Scan - Feature coming soon...")
            self.logger.info("Security Scan requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Security Scan: {e}")
            self.logger.error(f"Error opening Security Scan: {e}")
    
    def open_security_monitor(self):
        """Open security monitor."""
        try:
            # Try to import and launch the enhanced security monitor tool
            # For now, show status message until tool is available
            self.status_bar.showMessage("Security Monitor - Feature coming soon...")
            self.logger.info("Security Monitor requested")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Security Monitor: {e}")
            self.logger.error(f"Error opening Security Monitor: {e}")
    
    def open_security_settings(self):
        """Open security settings."""
        try:
            # Import and launch the enhanced security preferences tool
            import sys
            
            # Add root directory to path for imports
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            from enhanced_security_preferences_with_menu import EnhancedSecurityPreferencesGUI
            
            # Create and show the security settings window
            if not hasattr(self, 'security_settings_window') or self.security_settings_window is None:
                self.security_settings_window = EnhancedSecurityPreferencesGUI()
            
            self.security_settings_window.show()
            self.security_settings_window.raise_()
            self.security_settings_window.activateWindow()
            
            self.status_bar.showMessage("Security Settings opened successfully")
            self.logger.info("Security Settings opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Security Settings not available")
            self.logger.error(f"ImportError opening Security Settings: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Security Settings: {e}")
            self.logger.error(f"Error opening Security Settings: {e}")
        """Open security settings."""
        self.status_bar.showMessage("Security Settings - Feature coming soon...")
        self.logger.info("Security Settings requested")
    
    # System Tools Methods
    def open_system_info(self):
        """Open system information."""
        self.status_bar.showMessage("System Information - Feature coming soon...")
        self.logger.info("System Information requested")
    
    def open_disk_analyzer(self):
        """Open disk usage analyzer."""
        self.status_bar.showMessage("Disk Usage Analyzer - Feature coming soon...")
        self.logger.info("Disk Usage Analyzer requested")
    
    def open_process_monitor(self):
        """Open process monitor."""
        self.status_bar.showMessage("Process Monitor - Feature coming soon...")
        self.logger.info("Process Monitor requested")
    
    def open_system_cleanup(self):
        """Open system cleanup."""
        self.status_bar.showMessage("System Cleanup - Feature coming soon...")
        self.logger.info("System Cleanup requested")
    
    def open_performance_monitor(self):
        """Open performance monitor."""
        self.status_bar.showMessage("Performance Monitor - Feature coming soon...")
        self.logger.info("Performance Monitor requested")
    
    def open_system_settings(self):
        """Open system settings."""
        self.status_bar.showMessage("System Settings - Feature coming soon...")
        self.logger.info("System Settings requested")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hub = SimpleRFUHub()
    hub.show()
    sys.exit(app.exec_())