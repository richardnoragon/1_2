#!/usr/bin/env python3
"""
Enhanced Richard's File Utilities Main Application
Comprehensive menu integration across all tools and components
"""

import sys
import os
import traceback
import importlib
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QPushButton, QLabel, QGroupBox, QMessageBox,
        QSplashScreen, QStatusBar, QFrame, QScrollArea
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QIcon, QPixmap, QFont
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import menu system components
try:
    from gui.menu_manager import MenuManager
    from gui.themes import ThemeManager
    from src.rfu.gui.standard_window import StandardWindow
except ImportError as e:
    print(f"Warning: Could not import menu system: {e}")
    MenuManager = None
    ThemeManager = None
    StandardWindow = QMainWindow


class EnhancedRFUMainWindow(QMainWindow):
    """Enhanced main window with comprehensive menu integration."""
    
    tool_launched = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.active_tools = {}
        self.menu_manager = None
        
        # Initialize the application
        self._setup_window()
        self._create_menu_system()
        self._create_central_widget()
        self._create_status_bar()
        self._apply_theme()
        
        # Show welcome message
        self.statusBar().showMessage("Richard's File Utilities - Enhanced Menu System Ready", 3000)
        
    def _setup_window(self):
        """Setup basic window properties."""
        self.setWindowTitle("Richard's File Utilities - Enhanced Edition")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Set application icon
        icon_path = self._get_app_icon()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
    def _get_app_icon(self):
        """Get application icon path."""
        possible_paths = [
            "assets/icons/app_icon.png",
            "gui/icons/app_icon.png",
            "icons/app_icon.png"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
        
    def _create_menu_system(self):
        """Create comprehensive menu system."""
        if MenuManager:
            self.menu_manager = MenuManager(self)
            self.menu_manager.create_standard_menubar("main_hub")
            
            # Register main application callbacks
            self._register_menu_callbacks()
            
            # Add RFU-specific menus
            self._add_file_tools_menu()
            self._add_security_tools_menu()
            self._add_analysis_tools_menu()
            self._add_utilities_menu()
        else:
            # Fallback: create basic menu bar
            self._create_fallback_menu()
            
    def _register_menu_callbacks(self):
        """Register callbacks for menu actions."""
        if not self.menu_manager:
            return
            
        # File operations
        self.menu_manager.register_callback('new_project', self.new_project)
        self.menu_manager.register_callback('open_project', self.open_project)
        self.menu_manager.register_callback('save_project', self.save_project)
        self.menu_manager.register_callback('export_data', self.export_project_data)
        self.menu_manager.register_callback('import_data', self.import_project_data)
        
        # View operations
        self.menu_manager.register_callback('refresh', self.refresh_tool_grid)
        self.menu_manager.register_callback('show_preferences', self.show_main_preferences)
        self.menu_manager.register_callback('show_options', self.show_main_options)
        
    def _add_file_tools_menu(self):
        """Add file management tools menu."""
        if not self.menu_manager:
            return
            
        # Ensure tools menu exists
        if not hasattr(self.menu_manager, 'tools_menu') or self.menu_manager.tools_menu is None:
            # Create tools menu if it doesn't exist
            self.menu_manager.tools_menu = self.menuBar().addMenu('🛠️ &Tools')
            
        file_tools_menu = self.menu_manager.tools_menu.addMenu('📁 &File Management')
        
        # File search and organization
        file_tools_menu.addAction('🔍 File Finder').triggered.connect(self.open_file_finder)
        file_tools_menu.addAction('📋 Catalog Files').triggered.connect(self.open_catalog)
        file_tools_menu.addAction('✏️ Rename Files').triggered.connect(self.open_rename)
        file_tools_menu.addAction('📂 Organize Files').triggered.connect(self.open_organize)
        
        file_tools_menu.addSeparator()
        
        # File operations
        file_tools_menu.addAction('📦 Compress/Decompress').triggered.connect(self.open_compress)
        file_tools_menu.addAction('✂️ Split/Join Files').triggered.connect(self.open_file_splitter)
        file_tools_menu.addAction('🔄 Copy/Move/Sync').triggered.connect(self.open_cmsd)
        file_tools_menu.addAction('🗑️ Secure Delete').triggered.connect(self.open_secure_delete)
        
    def _add_security_tools_menu(self):
        """Add security tools menu."""
        if not self.menu_manager:
            return
            
        security_menu = self.menuBar().addMenu('🔒 &Security')
        
        # Encryption/Decryption
        encryption_menu = security_menu.addMenu('🔐 &Encryption')
        encryption_menu.addAction('🔒 Encrypt Files').triggered.connect(self.open_encryption)
        encryption_menu.addAction('🔓 Decrypt Files').triggered.connect(self.open_decryption)
        encryption_menu.addAction('🔑 Manage Keys').triggered.connect(self.open_key_manager)
        
        # Security analysis
        analysis_menu = security_menu.addMenu('🛡️ Security &Analysis')
        analysis_menu.addAction('🔍 Security Scan').triggered.connect(self.open_security_scan)
        analysis_menu.addAction('📊 Audit Report').triggered.connect(self.open_audit_report)
        analysis_menu.addAction('⚠️ Vulnerability Check').triggered.connect(self.open_vuln_check)
        
    def _add_analysis_tools_menu(self):
        """Add analysis tools menu."""
        if not self.menu_manager:
            return
            
        # Ensure tools menu exists
        if not hasattr(self.menu_manager, 'tools_menu') or self.menu_manager.tools_menu is None:
            self.menu_manager.tools_menu = self.menuBar().addMenu('🛠️ &Tools')
            
        analysis_menu = self.menu_manager.tools_menu.addMenu('📊 &Analysis')
        
        # File analysis
        analysis_menu.addAction('📏 Size Analyzer').triggered.connect(self.open_size_analyzer)
        analysis_menu.addAction('🔍 Duplicate Finder').triggered.connect(self.open_duplicate_finder)
        analysis_menu.addAction('📁 Empty Folders').triggered.connect(self.open_empty_folders)
        analysis_menu.addAction('✅ Checksum Validator').triggered.connect(self.open_checksum)
        
        analysis_menu.addSeparator()
        
        # Advanced analysis
        analysis_menu.addAction('📈 Disk Usage').triggered.connect(self.open_disk_usage)
        analysis_menu.addAction('🕒 File Timeline').triggered.connect(self.open_file_timeline)
        analysis_menu.addAction('🏷️ Metadata Viewer').triggered.connect(self.open_metadata_viewer)
        
    def _add_utilities_menu(self):
        """Add utilities menu."""
        if not self.menu_manager:
            return
            
        utilities_menu = self.menuBar().addMenu('🛠️ &Utilities')
        
        # System utilities
        system_menu = utilities_menu.addMenu('💻 &System')
        system_menu.addAction('🔧 System Info').triggered.connect(self.show_system_info)
        system_menu.addAction('🧹 Temp Cleaner').triggered.connect(self.open_temp_cleaner)
        system_menu.addAction('📊 Performance Monitor').triggered.connect(self.open_perf_monitor)
        
        # PDF utilities
        pdf_menu = utilities_menu.addMenu('📄 &PDF Tools')
        pdf_menu.addAction('📄 PDF Manager').triggered.connect(self.open_pdf_manager)
        pdf_menu.addAction('✂️ PDF Splitter').triggered.connect(self.open_pdf_manager)
        pdf_menu.addAction('🔗 PDF Merger').triggered.connect(self.open_pdf_manager)
        pdf_menu.addAction('🔒 PDF Security').triggered.connect(self.open_pdf_security)
        
    def _create_fallback_menu(self):
        """Create fallback menu system when MenuManager is not available."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        file_menu.addAction('&New Project').triggered.connect(self.new_project)
        file_menu.addAction('&Open Project').triggered.connect(self.open_project)
        file_menu.addAction('&Save Project').triggered.connect(self.save_project)
        file_menu.addSeparator()
        file_menu.addAction('E&xit').triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        tools_menu.addAction('File Finder').triggered.connect(self.open_file_finder)
        tools_menu.addAction('Catalog Files').triggered.connect(self.open_catalog)
        tools_menu.addAction('Rename Files').triggered.connect(self.open_rename)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction('&About').triggered.connect(self.show_about)
        
    def _create_central_widget(self):
        """Create the main application interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("Richard's File Utilities - Enhanced Edition")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 10px;
                margin: 10px;
            }
        """)
        main_layout.addWidget(header_label)
        
        # Tool grid in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Tool grid widget
        self.tool_grid_widget = QWidget()
        self.tool_grid_layout = QGridLayout(self.tool_grid_widget)
        self.tool_grid_layout.setSpacing(15)
        
        # Create tool buttons
        self._create_tool_buttons()
        
        scroll_area.setWidget(self.tool_grid_widget)
        main_layout.addWidget(scroll_area)
        
        # Footer
        footer_label = QLabel("Use the comprehensive menu system above for advanced features and operations")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                padding: 10px;
            }
        """)
        main_layout.addWidget(footer_label)
        
    def _create_tool_buttons(self):
        """Create buttons for all available tools."""
        tools = [
            # File Management Tools
            ("🔍 File Finder", "Search for files by name, type, or content", self.open_file_finder),
            ("📋 Catalog Files", "Create detailed file catalogs and reports", self.open_catalog),
            ("✏️ Rename Files", "Batch rename files with advanced patterns", self.open_rename),
            ("📂 Organize Files", "Automatically organize files by type/date", self.open_organize),
            
            # File Operations
            ("📦 Compress Files", "Compress and decompress archives", self.open_compress),
            ("✂️ Split/Join Files", "Split large files or join file parts", self.open_file_splitter),
            ("🔄 Copy/Move/Sync", "Advanced file copy, move, and sync operations", self.open_cmsd),
            ("🗑️ Secure Delete", "Securely delete files beyond recovery", self.open_secure_delete),
            
            # Analysis Tools
            ("📏 Size Analyzer", "Analyze disk usage and file sizes", self.open_size_analyzer),
            ("🔍 Duplicate Finder", "Find and manage duplicate files", self.open_duplicate_finder),
            ("📁 Empty Folders", "Find and clean empty directories", self.open_empty_folders),
            ("✅ Checksum Tools", "Verify file integrity with checksums", self.open_checksum),
            
            # PDF Tools
            ("📄 PDF Manager", "Comprehensive PDF operations", self.open_pdf_manager),
            ("🔒 PDF Security", "Encrypt and secure PDF documents", self.open_pdf_security),
            
            # Security Tools
            ("🔐 File Encryption", "Encrypt files and folders", self.open_encryption),
            ("🛡️ Security Scan", "Scan for security vulnerabilities", self.open_security_scan),
        ]
        
        row, col = 0, 0
        max_cols = 4
        
        for icon_name, description, callback in tools:
            button = self._create_tool_button(icon_name, description, callback)
            self.tool_grid_layout.addWidget(button, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def _create_tool_button(self, text, tooltip, callback):
        """Create a styled tool button."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setMinimumSize(200, 80)
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
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
        return button
        
    def _create_status_bar(self):
        """Create status bar with tool information."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready - Select a tool or use the menu system")
        
    def _apply_theme(self):
        """Apply theme to the main window."""
        if ThemeManager:
            try:
                # Apply theme if available
                self.setStyleSheet(ThemeManager.get_main_window_style())
            except:
                pass
                
    # Tool launcher methods with menu integration
    def launch_tool(self, tool_name, module_path, class_name):
        """Enhanced tool launcher with menu integration tracking."""
        try:
            # Check if tool is already open
            if tool_name in self.active_tools:
                self.active_tools[tool_name].raise_()
                self.active_tools[tool_name].activateWindow()
                return
                
            # Import and launch tool
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            
            # Create tool instance
            tool_instance = tool_class()
            
            # Store reference
            self.active_tools[tool_name] = tool_instance
            
            # Connect close event to cleanup
            def cleanup_tool():
                if tool_name in self.active_tools:
                    del self.active_tools[tool_name]
                    
            tool_instance.destroyed.connect(cleanup_tool)
            
            # Show tool
            tool_instance.show()
            
            # Update status
            self.statusBar().showMessage(f"Opened: {tool_name}", 3000)
            self.tool_launched.emit(tool_name)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to launch {tool_name}:\n{str(e)}\n\n"
                f"Module: {module_path}\nClass: {class_name}"
            )
            print(f"Tool launch error: {e}")
            traceback.print_exc()
            
    # File Management Tools
    def open_file_finder(self):
        """Open File Finder with enhanced menu integration."""
        self.launch_tool("File Finder", "src.rfu.tools.file_management.file_finder", "FileFinderGUI")
        
    def open_catalog(self):
        """Open Catalog tool with enhanced menu integration."""
        self.launch_tool("Catalog", "src.rfu.tools.file_management.catalog", "CatalogWindow")
        
    def open_rename(self):
        """Open Rename tool with enhanced menu integration."""
        self.launch_tool("Rename", "src.rfu.tools.file_management.rename", "RenameWindow")
        
    def open_organize(self):
        """Open Organize tool with enhanced menu integration."""
        self.launch_tool("Organize", "src.rfu.tools.file_management.organize", "OrganizeWindow")
        
    # File Operations
    def open_compress(self):
        """Open Compress/Decompress tool."""
        self.launch_tool("Compress", "src.rfu.tools.file_operations.compress_decompress", "CompressDecompressApp")
        
    def open_file_splitter(self):
        """Open File Splitter tool."""
        self.launch_tool("File Splitter", "src.rfu.tools.file_operations.file_splitter_joiner", "FileSplitJoinGUI")
        
    def open_cmsd(self):
        """Open Copy/Move/Sync/Delete tool."""
        self.launch_tool("CMSD", "src.rfu.tools.file_operations.cmsd", "CopyMoveSyncDeleteWindow")
        
    def open_secure_delete(self):
        """Open Enhanced Secure Delete tool."""
        try:
            from enhanced_secure_delete_with_menu import EnhancedSecureDeleteGUI
            if "Secure Delete" not in self.active_tools:
                tool = EnhancedSecureDeleteGUI()
                self.active_tools["Secure Delete"] = tool
                tool.show()
                self.statusBar().showMessage("Opened: Enhanced Secure Delete", 3000)
            else:
                self.active_tools["Secure Delete"].raise_()
        except ImportError:
            QMessageBox.warning(self, "Tool Not Available", 
                               "Enhanced Secure Delete tool is not available.")
        
    # Analysis Tools
    def open_size_analyzer(self):
        """Open Size Analyzer tool."""
        self.launch_tool("Size Analyzer", "src.utilities.analysis.size_analyzer", "SizeAnalyzerGUI")
        
    def open_duplicate_finder(self):
        """Open Duplicate Finder tool."""
        self.launch_tool("Duplicate Finder", "src.utilities.analysis.find_duplicate_files", "DuplicateFinderApp")
        
    def open_empty_folders(self):
        """Open Empty Folders tool."""
        self.launch_tool("Empty Folders", "src.rfu.tools.analysis.empty_folders", "EmptyFoldersGUI")
        
    def open_checksum(self):
        """Open Checksum tool."""
        self.launch_tool("Checksum", "src.utilities.analysis.check_sum", "ChecksumGUI")
        
    # PDF Tools
    def open_pdf_manager(self):
        """Open PDF Manager."""
        QMessageBox.information(self, "PDF Manager", 
                               "PDF Manager with comprehensive menu integration coming soon!")
        
    def open_pdf_security(self):
        """Open PDF Security tool."""
        QMessageBox.information(self, "PDF Security", 
                               "PDF Security tool with menu integration coming soon!")
        
    # Security Tools
    def open_encryption(self):
        """Open File Encryption tool."""
        QMessageBox.information(self, "File Encryption", 
                               "File Encryption tool with menu integration coming soon!")
        
    def open_decryption(self):
        """Open File Decryption tool."""
        QMessageBox.information(self, "File Decryption", 
                               "File Decryption tool with menu integration coming soon!")
        
    def open_key_manager(self):
        """Open Key Manager."""
        QMessageBox.information(self, "Key Manager", 
                               "Encryption Key Manager coming soon!")
        
    def open_security_scan(self):
        """Open Security Scanner."""
        QMessageBox.information(self, "Security Scanner", 
                               "Security Scanner with menu integration coming soon!")
        
    def open_audit_report(self):
        """Open Audit Report generator."""
        QMessageBox.information(self, "Audit Report", 
                               "Security Audit Report generator coming soon!")
        
    def open_vuln_check(self):
        """Open Vulnerability Checker."""
        QMessageBox.information(self, "Vulnerability Check", 
                               "Vulnerability Checker coming soon!")
        
    # Utility Tools
    def show_system_info(self):
        """Show system information."""
        if self.menu_manager:
            self.menu_manager.show_system_info()
        else:
            QMessageBox.information(self, "System Info", "System information display coming soon!")
        
    def open_temp_cleaner(self):
        """Open Temp File Cleaner."""
        QMessageBox.information(self, "Temp Cleaner", 
                               "Temporary File Cleaner coming soon!")
        
    def open_perf_monitor(self):
        """Open Performance Monitor."""
        QMessageBox.information(self, "Performance Monitor", 
                               "Performance Monitor coming soon!")
        
    def open_disk_usage(self):
        """Open Disk Usage Analyzer."""
        QMessageBox.information(self, "Disk Usage", 
                               "Disk Usage Analyzer coming soon!")
        
    def open_file_timeline(self):
        """Open File Timeline Analyzer."""
        QMessageBox.information(self, "File Timeline", 
                               "File Timeline Analyzer coming soon!")
        
    def open_metadata_viewer(self):
        """Open Metadata Viewer."""
        QMessageBox.information(self, "Metadata Viewer", 
                               "File Metadata Viewer coming soon!")
        
    # Menu callback implementations
    def new_project(self):
        """Create a new project."""
        QMessageBox.information(self, "New Project", 
                               "New project functionality with menu integration coming soon!")
        
    def open_project(self):
        """Open an existing project."""
        QMessageBox.information(self, "Open Project", 
                               "Open project functionality with menu integration coming soon!")
        
    def save_project(self):
        """Save current project."""
        QMessageBox.information(self, "Save Project", 
                               "Save project functionality with menu integration coming soon!")
        
    def export_project_data(self):
        """Export project data."""
        QMessageBox.information(self, "Export Data", 
                               "Export project data functionality coming soon!")
        
    def import_project_data(self):
        """Import project data."""
        QMessageBox.information(self, "Import Data", 
                               "Import project data functionality coming soon!")
        
    def refresh_tool_grid(self):
        """Refresh the tool grid display."""
        self.statusBar().showMessage("Tool grid refreshed", 2000)
        
    def show_main_preferences(self):
        """Show main application preferences."""
        if self.menu_manager:
            # Use menu manager's preferences dialog
            try:
                self.menu_manager.show_preferences()
            except:
                QMessageBox.information(self, "Preferences", 
                                       "Main application preferences coming soon!")
        else:
            QMessageBox.information(self, "Preferences", 
                                   "Main application preferences coming soon!")
        
    def show_main_options(self):
        """Show main application options."""
        QMessageBox.information(self, "Options", 
                               "Main application options coming soon!")
        
    def show_about(self):
        """Show about dialog."""
        if self.menu_manager:
            self.menu_manager.show_about()
        else:
            QMessageBox.about(self, "About", 
                             "Richard's File Utilities - Enhanced Edition\n"
                             "Comprehensive file management and analysis tools\n"
                             "with integrated menu system")
        
    def closeEvent(self, event):
        """Handle application close event."""
        # Close all active tools
        for tool_name, tool_instance in list(self.active_tools.items()):
            try:
                tool_instance.close()
            except:
                pass
                
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Richard's File Utilities - Enhanced")
    app.setApplicationVersion("2.0.0")
    
    # Create and show splash screen if available
    splash = None
    splash_path = "assets/splash.png"
    if os.path.exists(splash_path):
        try:
            splash_pixmap = QPixmap(splash_path)
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            app.processEvents()
        except:
            pass
    
    try:
        # Create main window
        main_window = EnhancedRFUMainWindow()
        
        # Close splash and show main window
        if splash:
            splash.finish(main_window)
            
        main_window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Application startup error: {e}")
        traceback.print_exc()
        if splash:
            splash.close()
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start application:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
