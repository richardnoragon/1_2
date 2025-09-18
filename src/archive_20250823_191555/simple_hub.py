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
    QStatusBar, QApplication, QGridLayout, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from .log_manager import get_log_manager
from .config_manager import get_config_manager

# CSS Color Constants
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

# CSS Style Constants
TITLE_HEADER_STYLE = f"color: {TEXT_DARK}; margin: 10px 0px;"

# Import constants for string literals
from core.constants import (
    PDF_TOOLS, SEGOE_UI_FONT, TITLE_STYLE_COLOR, 
    SUBTITLE_STYLE_COLOR, SECTION_MARGIN_STYLE,
    PRIVACY_TOOLS, ANALYSIS_TOOLS, UTILITIES_TOOLS, SETTINGS_TOOLS
)

# Import the simplified menu system
from .simple_menu_manager import SimpleMenuManager


class UtilityWindow(QMainWindow):
    """Wrapper class to ensure utilities maintain the main window's menu bar."""
    
    def __init__(self, parent_hub, utility_widget, title="Utility"):
        super().__init__(parent_hub)
        self.parent_hub = parent_hub
        self.setWindowTitle(f"Richard's File Utilities - {title}")
        self.setGeometry(150, 150, 900, 700)
        
        # Use the same menu bar as the parent hub
        if hasattr(parent_hub, 'menuBar') and parent_hub.menuBar():
            # Clone the menu bar from parent
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
                # Create new menu manager for this window
                from .simple_menu_manager import SimpleMenuManager
                self.menu_manager = SimpleMenuManager(self)
                self.menu_manager.create_menubar()
                
                # Register callbacks to delegate to parent hub
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
        event.ignore()


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
        title = QLabel(ANALYSIS_TOOLS)
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet(SECTION_MARGIN_STYLE)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for analyzing file properties, finding duplicates, and checking data integrity")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {DARKER_GRAY}; margin-bottom: 15px; "
                           f"font-size: 10px;")
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
            ("️ File Catalog", "Generate comprehensive file catalogs", self.open_file_catalog),
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
        title.setStyleSheet(TITLE_HEADER_STYLE)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for file manipulation, splitting, copying, and synchronization")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {DARKER_GRAY}; margin-bottom: 15px; "
                           f"font-size: 10px;")
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
        title.setStyleSheet(TITLE_HEADER_STYLE)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Tools for viewing and editing file metadata, "
                      "EXIF data, and document properties")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {DARKER_GRAY}; margin-bottom: 15px; "
                           f"font-size: 10px;")
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
        title.setStyleSheet(TITLE_HEADER_STYLE)
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
            ("🌐 Network Scanner", "Scan and discover network devices", 
             self.open_network_scanner),
            ("🔌 Connectivity Test\nComing Soon", 
             "Test network connectivity and speed", 
             self.open_connectivity_test),
            ("📡 Network Transfer", "Transfer files over network", 
             self.open_network_transfer),
            ("🔗 Bookmark Manager\nComing Soon", 
             "Manage network bookmarks and links", 
             self.open_bookmark_manager),
            ("📊 Bandwidth Monitor", "Monitor network bandwidth usage", 
             self.open_bandwidth_monitor),
            ("🛡️ Network Security\nComing Soon", 
             "Network security analysis tools", 
             self.open_network_security),
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
        """Create the PDF Tools tab with folder-based dynamic structure."""
        try:
            # Import our enhanced PDF tools widget
            from src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget import (
                EnhancedPDFToolsWidget
            )
            
            # Create the enhanced PDF tools widget
            pdf_tools_widget = EnhancedPDFToolsWidget(self)
            
            # Add it as a tab
            self.tab_widget.addTab(pdf_tools_widget, PDF_TOOLS)
            
            self.logger.info(f"{PDF_TOOLS} tab created with enhanced widget")
            
        except Exception as e:
            self.logger.error(f"Failed to create enhanced PDF Tools tab: {e}")
            # Fallback to simple tab
            self._create_simple_pdf_tools_tab()
    
    def _create_simple_pdf_tools_tab(self):
        """Create a simple PDF Tools tab as fallback."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel(PDF_TOOLS)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(SEGOE_UI_FONT, 16, QFont.Bold))
        title.setStyleSheet(TITLE_STYLE_COLOR)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("PDF processing, conversion, security, and analysis tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont(SEGOE_UI_FONT, 10))
        desc.setStyleSheet(SUBTITLE_STYLE_COLOR)
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
        self.tab_widget.addTab(tab, PDF_TOOLS)
        
        self.logger.info(f"Simple {PDF_TOOLS} tab created as fallback")
    
    def create_privacy_tab(self):
        """Create the Privacy tab with organized grid layout."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Professional header
        title = QLabel(PRIVACY_TOOLS)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(SEGOE_UI_FONT, 16, QFont.Bold))
        title.setStyleSheet(TITLE_STYLE_COLOR)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Privacy protection, data cleanup, and secure browsing tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont(SEGOE_UI_FONT, 10))
        desc.setStyleSheet(SUBTITLE_STYLE_COLOR)
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced privacy tools with icons and descriptions (3×2 grid)
        tools = [
            ("🧹 Privacy Cleaner", "Clean privacy traces and personal data", 
             self.open_privacy_cleaner),
            ("🗂️ Temp File Cleanup", "Remove temporary and cache files", 
             self.open_temp_cleanup),
            ("🌐 Browser Cleanup", "Clear browsing history and cookies", 
             self.open_browser_cleanup),
            ("⚙️ Privacy Settings\nComing Soon", 
             "Configure privacy and security settings", 
             self.open_privacy_settings),
            ("🔍 Data Scanner", "Scan for sensitive data exposure", 
             self.open_data_scanner),
            ("🛡️ Privacy Shield\nComing Soon", 
             "Advanced privacy protection tools", 
             self.open_privacy_shield)
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
        title.setFont(QFont(SEGOE_UI_FONT, 16, QFont.Bold))
        title.setStyleSheet(TITLE_STYLE_COLOR)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("File encryption, secure deletion, and security analysis tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont(SEGOE_UI_FONT, 10))
        desc.setStyleSheet(SUBTITLE_STYLE_COLOR)
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced security tools with icons and descriptions (3×2 grid)
        tools = [
            ("🔒 File Encryption", "Encrypt files and folders securely", 
             self.open_file_encryption),
            ("🗑️ Secure Delete", "Permanently delete sensitive files", 
             self.open_secure_delete),
            ("🔑 Password Generator", "Generate strong, secure passwords", 
             self.open_password_generator),
            ("🔍 Security Scan", "Scan for security vulnerabilities", 
             self.open_security_scan),
            ("🛡️ Security Monitor\nComing Soon", 
             "Monitor system security status", 
             self.open_security_monitor),
            ("⚙️ Security Settings", "Configure security preferences", 
             self.open_security_settings)
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
        title.setFont(QFont(SEGOE_UI_FONT, 16, QFont.Bold))
        title.setStyleSheet(TITLE_STYLE_COLOR)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("System monitoring, analysis, and maintenance tools")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont(SEGOE_UI_FONT, 10))
        desc.setStyleSheet(SUBTITLE_STYLE_COLOR)
        layout.addWidget(desc)
        
        # Create grid widget for tools
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced system tools with icons and descriptions (3×2 grid)
        tools = [
            ("💻 System Information", "View detailed system specifications", self.open_system_info),
            ("💿 Disk Usage Analyzer\nComing Soon", "Analyze disk space usage and cleanup", self.open_disk_analyzer),
            ("⚡ Process Monitor", "Monitor running processes and services", self.open_process_monitor),
            ("🧹 System Cleanup\nComing Soon", "Clean temporary files and system cache", self.open_system_cleanup),
            ("📊 Performance Monitor\nComing Soon", "Monitor system performance metrics", self.open_performance_monitor),
            ("⚙️ System Settings\nComing Soon", "Configure system preferences", self.open_system_settings)
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
        title.setFont(QFont(SEGOE_UI_FONT, 16, QFont.Bold))
        title.setStyleSheet(TITLE_STYLE_COLOR)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Real-time application logs and system monitoring")
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont(SEGOE_UI_FONT, 10))
        desc.setStyleSheet(SUBTITLE_STYLE_COLOR)
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
            
            from tools.analysis.check_sum import ChecksumGUI
            
            # Use the new window manager
            utility_window = self._create_utility_window(
                ChecksumGUI, 
                "Checksum Verification"
            )
            
            if utility_window:
                self.status_bar.showMessage("Checksum Verification opened successfully")
                self.logger.info("Checksum Verification tool opened")
                
                # Store reference to prevent garbage collection
                if not hasattr(self, '_utility_windows'):
                    self._utility_windows = {}
                self._utility_windows['checksum'] = utility_window
            
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
            
            from tools.analysis.find_duplicate_files import (
                DuplicateFinderApp)
            
            # Use the new window manager
            utility_window = self._create_utility_window(
                DuplicateFinderApp,
                "Duplicate Finder"
            )
            
            if utility_window:
                self.status_bar.showMessage("Duplicate Finder opened successfully")
                self.logger.info("Duplicate File Finder tool opened")
                
                # Store reference to prevent garbage collection
                if not hasattr(self, '_utility_windows'):
                    self._utility_windows = {}
                self._utility_windows['duplicate_finder'] = utility_window
                
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
            
            from tools.analysis.size_analyzer import SizeAnalyzerGUI
            
            # Use the new window manager
            utility_window = self._create_utility_window(
                SizeAnalyzerGUI,
                "Size Analyzer"
            )
            
            if utility_window:
                self.status_bar.showMessage("Size Analyzer opened successfully")
                self.logger.info("Size Analyzer tool opened")
                
                # Store reference to prevent garbage collection
                if not hasattr(self, '_utility_windows'):
                    self._utility_windows = {}
                self._utility_windows['size_analyzer'] = utility_window
            
        except ImportError as e:
            self.status_bar.showMessage("Size Analyzer tool not available")
            self.logger.error(f"ImportError opening Size Analyzer: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Size Analyzer: {e}")
            self.logger.error(f"Error opening Size Analyzer: {e}")
    
    def open_empty_folders(self):
        """Open empty folders finder."""
        try:
            # Import and launch the empty folders tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from tools.analysis.empty_folders import EmptyFoldersGUI
            
            # Use the new window manager
            utility_window = self._create_utility_window(
                EmptyFoldersGUI,
                "Empty Folders Finder"
            )
            
            if utility_window:
                self.status_bar.showMessage("Empty Folders Finder opened successfully")
                self.logger.info("Empty Folders Finder tool opened")
                
                # Store reference to prevent garbage collection
                if not hasattr(self, '_utility_windows'):
                    self._utility_windows = {}
                self._utility_windows['empty_folders'] = utility_window
            
        except ImportError as e:
            self.status_bar.showMessage("Empty Folders tool not available")
            self.logger.error(f"ImportError opening Empty Folders: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Empty Folders: {e}")
            self.logger.error(f"Error opening Empty Folders: {e}")
    
    def open_file_catalog(self):
        """Open file catalog generator."""
        try:
            # Import and launch the catalog tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            # Use the utilities catalog implementation
            from src.tools.file_operations.catalog.catalog import CatalogWindow
            
            # Create fresh catalog window
            self._ensure_fresh_window('file_catalog_window')
            self.file_catalog_window = CatalogWindow()
            
            self.file_catalog_window.show()
            self.file_catalog_window.raise_()
            self.file_catalog_window.activateWindow()
            
            self.status_bar.showMessage(
                "File Catalog Generator opened successfully"
            )
            self.logger.info("File Catalog Generator tool opened")
                
        except ImportError as e:
            self.status_bar.showMessage("File Catalog tool not available")
            self.logger.error(f"ImportError opening File Catalog: {e}")
        except Exception as e:
            self.status_bar.showMessage(
                f"Error opening File Catalog tool: {e}"
            )
            self.logger.error(f"Error opening File Catalog tool: {e}")
    
    # File Operations Methods
    def open_file_splitter(self):
        """Open file splitter."""
        try:
            # Import and launch the file splitter tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from src.tools.file_operations.file_splitter.gui import (
                FileSplitJoinGUI
            )
            
            # Create and show the file splitter window
            if not hasattr(self, 'file_splitter_window') or \
               self.file_splitter_window is None:
                self.file_splitter_window = FileSplitJoinGUI()
            
            self.file_splitter_window.show()
            self.file_splitter_window.raise_()
            self.file_splitter_window.activateWindow()
            
            self.status_bar.showMessage(
                "File Splitter/Joiner opened successfully"
            )
            self.logger.info("File Splitter/Joiner tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("File Splitter tool not available")
            self.logger.error(f"ImportError opening File Splitter: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening File Splitter: {e}")
            self.logger.error(f"Error opening File Splitter: {e}")
    
    def open_cmsd_logic(self):
        """Open CMSD logic tool."""
        try:
            # Import and launch the CMSD (Copy/Move/Sync/Delete) tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from src.tools.file_operations.cmsd import CopyMoveSyncDeleteWindow
            
            # Create and show the CMSD window
            if not hasattr(self, 'cmsd_window') or \
               self.cmsd_window is None:
                self.cmsd_window = CopyMoveSyncDeleteWindow()
            
            self.cmsd_window.show()
            self.cmsd_window.raise_()
            self.cmsd_window.activateWindow()
            
            self.status_bar.showMessage(
                "Copy/Move/Sync/Delete tool opened successfully"
            )
            self.logger.info("Copy/Move/Sync/Delete tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("CMSD tool not available")
            self.logger.error(f"ImportError opening CMSD Logic: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening CMSD Logic: {e}")
            self.logger.error(f"Error opening CMSD Logic: {e}")
    
    def open_sync_backup(self):
        """Open synchronization and backup."""
        try:
            # Import and launch the sync/backup tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            # Try to import the sync tool, fall back to placeholder
            try:
                from tools.file_operations.synchronization_backup.sync import (
                    SyncWindow
                )
                
                # Create and show the sync/backup window
                if not hasattr(self, 'sync_backup_window') or \
                   self.sync_backup_window is None:
                    self.sync_backup_window = SyncWindow()
                
                self.sync_backup_window.show()
                self.sync_backup_window.raise_()
                self.sync_backup_window.activateWindow()
                
                self.status_bar.showMessage(
                    "Synchronization & Backup tool opened successfully"
                )
                self.logger.info("Synchronization & Backup tool opened")
                
            except ImportError:
                # Fallback message when sync tool has dependency issues
                self.status_bar.showMessage(
                    "Sync & Backup tool temporarily unavailable"
                )
                self.logger.info(
                    "Sync & Backup tool unavailable - dependency issues"
                )
            
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
            # Import and launch the file organization tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from src.tools.file_operations.organize.organize import OrganizeWindow
            
            # Create and show the organize files window
            if not hasattr(self, 'organize_files_window') or \
               self.organize_files_window is None:
                self.organize_files_window = OrganizeWindow()
            
            self.organize_files_window.show()
            self.organize_files_window.raise_()
            self.organize_files_window.activateWindow()
            
            self.status_bar.showMessage(
                "File Organization tool opened successfully"
            )
            self.logger.info("File Organization tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("File Organization tool not available")
            self.logger.error(f"ImportError opening File Organization: {e}")
        except Exception as e:
            self.status_bar.showMessage(
                f"Error opening File Organization: {e}"
            )
            self.logger.error(f"Error opening File Organization: {e}")
    
    def open_batch_rename(self):
        """Open batch rename tool."""
        try:
            # Import and launch the batch rename tool
            import sys
            import os
            
            # Add src directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, '..')
            
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from src.tools.file_management.rename import RenameWindow
            
            # Create and show the batch rename window
            if not hasattr(self, 'batch_rename_window') or \
               self.batch_rename_window is None:
                self.batch_rename_window = RenameWindow()
            
            self.batch_rename_window.show()
            self.batch_rename_window.raise_()
            self.batch_rename_window.activateWindow()
            
            self.status_bar.showMessage(
                "Batch Rename tool opened successfully"
            )
            self.logger.info("Batch Rename tool opened")
            
        except ImportError as e:
            self.status_bar.showMessage("Batch Rename tool not available")
            self.logger.error(f"ImportError opening Batch Rename: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Batch Rename: {e}")
            self.logger.error(f"Error opening Batch Rename: {e}")
    
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
            from src.tools.metadata.image_metadata import ImageMetadataEditorGUI
            exif_window = ImageMetadataEditorGUI()
            exif_window.show()
            self.status_bar.showMessage("EXIF Data Viewer opened")
            self.logger.info("EXIF Data Viewer (Image Metadata Editor) opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("EXIF Data Viewer not available")
            self.logger.error(f"ImportError opening EXIF Data Viewer: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening EXIF Viewer: {e}")
            self.logger.error(f"Error opening EXIF Viewer: {e}")
    
    def open_metadata_analyzer(self):
        """Open metadata analyzer."""
        try:
            from src.tools.metadata.image_metadata import \
                ImageMetadataEditorGUI
            analyzer_window = ImageMetadataEditorGUI()
            analyzer_window.show()
            self.status_bar.showMessage("Metadata Analyzer opened")
            self.logger.info("Metadata Analyzer (Image Metadata) opened")
        except ImportError as e:
            self.status_bar.showMessage("Metadata Analyzer not available")
            self.logger.error(f"ImportError opening Metadata Analyzer: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Analyzer: {e}")
            self.logger.error(f"Error opening Metadata Analyzer: {e}")
    
    def open_tag_editor(self):
        """Open tag editor."""
        try:
            # Try enhanced image metadata editor for tag editing first
            from src.tools.metadata.image_metadata import \
                ImageMetadataEditorGUI
            tag_window = ImageMetadataEditorGUI()
            tag_window.show()
            self.status_bar.showMessage("Tag Editor opened")
            self.logger.info("Tag Editor (Image Metadata Tags) opened")
        except ImportError as e:
            self.status_bar.showMessage("Tag Editor not available")
            self.logger.error(f"ImportError opening Tag Editor: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Tag Editor: {e}")
            self.logger.error(f"Error opening Tag Editor: {e}")
    
    def open_property_inspector(self):
        """Open property inspector."""
        try:
            from src.tools.metadata.office_meta_data_editor import \
                OfficeMetaDataEditorGUI
            property_window = OfficeMetaDataEditorGUI()
            property_window.show()
            self.status_bar.showMessage("Property Inspector opened")
            self.logger.info("Property Inspector (Office Metadata) opened")
        except ImportError as e:
            self.status_bar.showMessage("Property Inspector not available")
            self.logger.error(f"ImportError opening Property Inspector: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Inspector: {e}")
            self.logger.error(f"Error opening Property Inspector: {e}")
    
    # Network Tools Methods
    def open_network_scanner(self):
        """Open network scanner."""
        try:
            from src.tools.network.network_scanner import NetworkScannerGUI
            scanner_window = NetworkScannerGUI()
            scanner_window.show()
            self.status_bar.showMessage("Network Scanner opened")
            self.logger.info("Network Scanner opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Network Scanner not available")
            self.logger.error(f"ImportError opening Network Scanner: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Network Scanner: {e}")
            self.logger.error(f"Error opening Network Scanner: {e}")

    def open_connectivity_test(self):
        """Open connectivity test."""
        self.status_bar.showMessage("Connectivity Test - Feature coming soon...")
        self.logger.info("Connectivity Test requested")

    def open_network_transfer(self):
        """Open network transfer."""
        try:
            from src.tools.network.network_transfer import \
                NetworkTransferGUI
            transfer_window = NetworkTransferGUI()
            transfer_window.show()
            self.status_bar.showMessage("Network Transfer opened")
            self.logger.info("Network Transfer opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Network Transfer not available")
            self.logger.error(f"ImportError opening Network Transfer: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Transfer: {e}")
            self.logger.error(f"Error opening Network Transfer: {e}")

    def open_bookmark_manager(self):
        """Open bookmark manager."""
        self.status_bar.showMessage("Bookmark Manager - Feature coming soon...")
        self.logger.info("Bookmark Manager requested")

    def open_bandwidth_monitor(self):
        """Open bandwidth monitor."""
        try:
            from src.tools.network.network_connectivity_complex.gui.\
                widgets.bandwidth_monitor_widget import BandwidthMonitorWidget
            from src.gui.standard_window import StandardWindow
            
            # Create a standalone window for the bandwidth monitor
            class BandwidthMonitorWindow(StandardWindow):
                def __init__(self):
                    super().__init__(
                        title="Bandwidth Monitor - Richard's File Utilities",
                        window_type="utility"
                    )
                    widget = BandwidthMonitorWidget()
                    self.setCentralWidget(widget)
                    
            monitor_window = BandwidthMonitorWindow()
            monitor_window.show()
            self.status_bar.showMessage("Bandwidth Monitor opened")
            self.logger.info("Bandwidth Monitor opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Bandwidth Monitor not available")
            self.logger.error(f"ImportError opening Bandwidth Monitor: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Monitor: {e}")
            self.logger.error(f"Error opening Bandwidth Monitor: {e}")

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
        try:
            from src.tools.privacy.privacy_tools_simple import SimplePrivacyHub
            privacy_window = SimplePrivacyHub()
            privacy_window.show()
            self.status_bar.showMessage("Privacy Cleaner opened")
            self.logger.info("Privacy Cleaner opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Privacy Cleaner not available")
            self.logger.error(f"ImportError opening Privacy Cleaner: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Privacy Cleaner: {e}")
            self.logger.error(f"Error opening Privacy Cleaner: {e}")

    def open_temp_cleanup(self):
        """Open temporary file cleanup."""
        try:
            from src.tools.privacy.privacy_tools_simple import SimplePrivacyHub
            # Use privacy cleaner for temp cleanup functionality
            temp_window = SimplePrivacyHub()
            temp_window.show()
            self.status_bar.showMessage("Temp File Cleanup opened")
            self.logger.info("Temp File Cleanup opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Temp File Cleanup not available")
            self.logger.error(f"ImportError opening Temp Cleanup: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Temp Cleanup: {e}")
            self.logger.error(f"Error opening Temp File Cleanup: {e}")

    def open_browser_cleanup(self):
        """Open browser history cleaner."""
        try:
            from src.tools.privacy.privacy_tools_simple import SimplePrivacyHub
            # Use privacy cleaner for browser cleanup functionality
            browser_window = SimplePrivacyHub()
            browser_window.show()
            self.status_bar.showMessage("Browser Cleanup opened")
            self.logger.info("Browser Cleanup opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Browser Cleanup not available")
            self.logger.error(f"ImportError opening Browser Cleanup: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Browser Cleanup: {e}")
            self.logger.error(f"Error opening Browser Cleanup: {e}")

    def open_privacy_settings(self):
        """Open privacy settings configuration (Coming Soon)"""
        QMessageBox.information(
            self, 
            "Privacy Settings", 
            "Privacy Settings feature is being developed\n\n"
            "This feature will allow you to configure comprehensive "
            "privacy and security settings."
        )
        self.status_bar.showMessage("Privacy Settings - Feature coming soon...")
        self.logger.info("Privacy Settings requested")

    def open_data_scanner(self):
        """Open data scanner."""
        try:
            from src.tools.privacy.data_anonymizer import DataAnonymizerGUI
            scanner_window = DataAnonymizerGUI()
            scanner_window.show()
            self.status_bar.showMessage("Data Scanner opened")
            self.logger.info("Data Scanner opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Data Scanner not available")
            self.logger.error(f"ImportError opening Data Scanner: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Data Scanner: {e}")
            self.logger.error(f"Error opening Data Scanner: {e}")

    def open_privacy_shield(self):
        """Open privacy shield (Coming Soon)"""
        QMessageBox.information(
            self,
            "Privacy Shield", 
            "Privacy Shield feature is being developed\n\n"
            "This feature will provide advanced privacy protection "
            "tools and monitoring."
        )
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
            
            # Use the new window manager
            utility_window = self._create_utility_window(
                EnAndDecryptGUI,
                "File Encryption"
            )
            
            if utility_window:
                self.status_bar.showMessage("File Encryption tool opened successfully")
                self.logger.info("File Encryption tool opened")
                
                # Store reference to prevent garbage collection
                if not hasattr(self, '_utility_windows'):
                    self._utility_windows = {}
                self._utility_windows['encryption'] = utility_window
            
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
            from src.tools.security.simple_password_generator import SimplePasswordGeneratorGUI
            password_window = SimplePasswordGeneratorGUI()
            password_window.show()
            self.status_bar.showMessage("Password Generator opened")
            self.logger.info("Password Generator opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Password Generator not available")
            self.logger.error(f"ImportError opening Password Generator: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Password Generator: {e}")
            self.logger.error(f"Error opening Password Generator: {e}")
    
    def open_security_scan(self):
        """Open security scan."""
        try:
            from src.tools.security.simple_security_scanner import SimpleSecurityScannerGUI
            scan_window = SimpleSecurityScannerGUI()
            scan_window.show()
            self.status_bar.showMessage("Security Scan opened")
            self.logger.info("Security Scan opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Security Scan not available")
            self.logger.error(f"ImportError opening Security Scan: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Security Scan: {e}")
            self.logger.error(f"Error opening Security Scan: {e}")
    
    def open_security_monitor(self):
        """Open security monitor (Coming Soon)."""
        QMessageBox.information(
            self,
            "Security Monitor",
            "Security Monitor feature is being developed\n\n"
            "This feature will provide real-time security monitoring "
            "and threat detection capabilities."
        )
        self.status_bar.showMessage("Security Monitor - Feature coming soon...")
        self.logger.info("Security Monitor requested")
    
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
        try:
            from src.tools.system.simple_system_info import \
                SimpleSystemInfoGUI
            system_window = SimpleSystemInfoGUI()
            system_window.show()
            self.status_bar.showMessage("System Information opened")
            self.logger.info("System Information opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("System Information not available")
            self.logger.error(f"ImportError opening System Information: {e}")
        except Exception as e:
            self.status_bar.showMessage(
                f"Error opening System Information: {e}")
            self.logger.error(f"Error opening System Information: {e}")
    
    def open_disk_analyzer(self):
        """Open disk usage analyzer."""
        self.status_bar.showMessage(
            "Disk Usage Analyzer - Feature coming soon...")
        self.logger.info("Disk Usage Analyzer requested")
    
    def open_process_monitor(self):
        """Open process monitor."""
        try:
            from src.tools.system.simple_process_monitor import \
                SimpleProcessMonitorGUI
            process_window = SimpleProcessMonitorGUI()
            process_window.show()
            self.status_bar.showMessage("Process Monitor opened")
            self.logger.info("Process Monitor opened successfully")
        except ImportError as e:
            self.status_bar.showMessage("Process Monitor not available")
            self.logger.error(f"ImportError opening Process Monitor: {e}")
        except Exception as e:
            self.status_bar.showMessage(f"Error opening Process Monitor: {e}")
            self.logger.error(f"Error opening Process Monitor: {e}")
    
    def open_system_cleanup(self):
        """Open system cleanup."""
        self.status_bar.showMessage("System Cleanup - Feature coming soon...")
        self.logger.info("System Cleanup requested")
    
    def open_performance_monitor(self):
        """Open performance monitor."""
        self.status_bar.showMessage(
            "Performance Monitor - Feature coming soon...")
        self.logger.info("Performance Monitor requested")
    
    def open_system_settings(self):
        """Open system settings."""
        self.status_bar.showMessage("System Settings - Feature coming soon...")
        self.logger.info("System Settings requested")

    def register_tool(self, tool_name: str, tool_instance):
        """Register a tool instance with the hub for tracking purposes."""
        if not hasattr(self, '_registered_tools'):
            self._registered_tools = {}
        self._registered_tools[tool_name] = tool_instance
        self.logger.info(f"Tool registered: {tool_name}")

    def _create_utility_window(self, utility_class, title, *args, **kwargs):
        """Create a utility window with proper menu bar inheritance."""
        try:
            # Create the utility instance
            if issubclass(utility_class, QMainWindow):
                # If it's a QMainWindow, convert to widget
                utility_instance = utility_class(*args, **kwargs)
                utility_widget = utility_instance.centralWidget()
                if utility_widget:
                    utility_widget.setParent(None)
                else:
                    # Create a simple wrapper widget
                    utility_widget = QWidget()
                    layout = QVBoxLayout(utility_widget)
                    layout.addWidget(QLabel(f"{title} - Not properly configured"))
                
                # Clean up the temporary QMainWindow
                utility_instance.hide()
                utility_instance.deleteLater()
            else:
                # If it's already a widget, use directly
                utility_widget = utility_class(parent=self, *args, **kwargs)
            
            # Create wrapper window with menu bar
            utility_window = UtilityWindow(self, utility_widget, title)
            utility_window.show()
            utility_window.raise_()
            utility_window.activateWindow()
            
            return utility_window
            
        except Exception as e:
            self.logger.error(f"Error creating utility window for {title}: {e}")
            self.status_bar.showMessage(f"Error opening {title}: {e}")
            return None

    def _ensure_fresh_window(self, window_attr_name):
        """Ensure a window attribute is properly reset for fresh initialization."""
        if hasattr(self, window_attr_name):
            old_window = getattr(self, window_attr_name)
            if old_window:
                try:
                    if hasattr(old_window, 'close'):
                        old_window.close()
                except Exception as e:
                    self.logger.error(f"Error closing old {window_attr_name}: {e}")
            setattr(self, window_attr_name, None)
        return True

    def closeEvent(self, event):
        """Handle application close event with proper cleanup."""
        self.logger.info("Simple RFU Hub closing - starting cleanup...")
        
        try:
            # Close all utility windows
            if hasattr(self, '_utility_windows'):
                for window_name, window in self._utility_windows.items():
                    try:
                        if window and not window.isHidden():
                            window.hide()
                            window.deleteLater()
                            self.logger.info(f"Closed utility window: {window_name}")
                    except Exception as e:
                        self.logger.error(f"Error closing {window_name}: {e}")
                self._utility_windows.clear()
            
            # Close registered tools
            self._close_registered_tools()
            self._close_window_attributes()
            self._cleanup_menu_system()
            self.logger.info("Simple RFU Hub cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        
        # Accept the close event
        event.accept()
    
    def _close_registered_tools(self):
        """Close all registered tools."""
        if hasattr(self, '_registered_tools'):
            for tool_name, tool_instance in self._registered_tools.items():
                try:
                    if tool_instance and hasattr(tool_instance, 'close'):
                        tool_instance.close()
                        self.logger.info(f"Closed tool: {tool_name}")
                except Exception as e:
                    self.logger.error(f"Error closing {tool_name}: {e}")
            self._registered_tools.clear()
    
    def _close_window_attributes(self):
        """Close all window instances stored as attributes."""
        window_attributes = [
            'checksum_window', 'duplicate_finder_window',
            'size_analyzer_window', 'empty_folders_window',
            'file_catalog_window', 'file_splitter_window',
            'cmsd_window', 'sync_backup_window', 'file_touch_window',
            'organize_files_window', 'batch_rename_window',
            'image_metadata_window', 'office_metadata_window',
            'encryption_window', 'secure_delete_window',
            'security_settings_window'
        ]
        
        for attr_name in window_attributes:
            if hasattr(self, attr_name):
                window = getattr(self, attr_name)
                if window and hasattr(window, 'close'):
                    try:
                        window.close()
                        self.logger.info(f"Closed: {attr_name}")
                    except Exception as e:
                        self.logger.error(f"Error closing {attr_name}: {e}")
                setattr(self, attr_name, None)
    
    def _cleanup_menu_system(self):
        """Clean up menu system."""
        if hasattr(self, 'menu_manager'):
            try:
                # Just set to None since SimpleMenuManager may not have cleanup
                self.menu_manager = None
            except Exception as e:
                self.logger.error(f"Error cleaning up menu: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hub = SimpleRFUHub()
    hub.show()
    sys.exit(app.exec_())

