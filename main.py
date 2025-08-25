#!/usr/bin/env python3
"""
Richard's File Utilities - Main Entry Point

This is the main entry point for the Richard's File Utilities application.
It provides a comprehensive GUI interface for accessing all file utility tools.
Enhanced with SQLite database integration for settings and logging.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import constants for string literals
from src.core.constants import (
    APP_NAME, JSON_FILES_FILTER, IMPORT_ERROR, SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER
)

# Initialize database and logging systems
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
            from standalone_database_manager import get_database_manager
            db_manager = get_database_manager()
            
            # Validate database connection
            if db_manager is None:
                raise RuntimeError("Database manager returned None")
                
            # Test database connectivity
            db_info = db_manager.get_database_info()
            if not db_info or 'database_file' not in db_info:
                raise RuntimeError("Database info validation failed")
                
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
    from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
    ENHANCED_PDF_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced PDF Tools not available: {e}")
    ENHANCED_PDF_TOOLS_AVAILABLE = False

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
        QWidget, QHBoxLayout, QGridLayout, QScrollArea, QFrame,
        QTabWidget, QGroupBox, QMessageBox, QFileDialog
    )
    from PyQt5.QtCore import Qt, pyqtSlot
    from PyQt5.QtGui import QFont, QIcon
    
    class RFUMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_NAME)
            self.setGeometry(200, 200, 900, 700)
            
            # Store references to opened windows
            self.opened_windows = {}
            
            # Initialize database tracking
            self.database_available = DATABASE_AVAILABLE
            if self.database_available:
                try:
                    from standalone_database_manager import get_database_manager
                    self.db_manager = get_database_manager()
                    self.logger = logging.getLogger('RFU.MainWindow')
                    self.logger.info("Main window database tracking enabled")
                except Exception as e:
                    self.database_available = False
                    print(f"Database integration failed: {e}")
            
            self.init_ui()
        
        def track_tool_usage(self, tool_name: str, operation_type: str = 'launch'):
            """Track tool usage in database with race condition protection."""
            if not self.database_available:
                return
            
            try:
                # Use a single UPSERT query to avoid race conditions
                upsert_query = """
                    INSERT INTO tool_usage
                    (tool_name, operation_type, usage_count, first_used, 
                     last_used, success_count)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                    ON CONFLICT(tool_name, operation_type) DO UPDATE SET
                        usage_count = usage_count + 1,
                        last_used = CURRENT_TIMESTAMP,
                        success_count = success_count + 1
                """
                
                # Execute as a single atomic operation
                self.db_manager.execute_update(upsert_query, 
                                               (tool_name, operation_type))
                self.logger.info("Tracked tool usage: %s - %s",
                                 tool_name, operation_type)
                
            except (OSError, AttributeError, RuntimeError) as e:
                self.logger.error("Failed to track tool usage: %s", e)
                # Fallback: try simpler insert without conflict resolution
                try:
                    simple_query = """
                        INSERT OR IGNORE INTO tool_usage
                        (tool_name, operation_type, usage_count, first_used, 
                         last_used, success_count)
                        VALUES (?, ?, 1, CURRENT_TIMESTAMP, 
                                CURRENT_TIMESTAMP, 1)
                    """
                    self.db_manager.execute_update(simple_query, 
                                                   (tool_name, operation_type))
                except (OSError, AttributeError,
                        RuntimeError) as fallback_error:
                    error_msg = "Fallback tool usage tracking failed: %s"
                    self.logger.error(error_msg, fallback_error)
        
        def track_file_access(self, file_path: str, tool_name: str = None,
                              operation_type: str = 'access'):
            """Track file access in database."""
            if not self.database_available:
                return
            
            try:
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    return
                
                # Insert or update file history
                query = """
                    INSERT OR IGNORE INTO file_history
                    (file_path, file_name, file_size, file_type,
                     directory_path, tool_name, operation_type, access_count,
                     first_accessed, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP)
                """
                
                update_query = """
                    UPDATE file_history
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP,
                        tool_name = COALESCE(?, tool_name),
                        operation_type = COALESCE(?, operation_type)
                    WHERE file_path = ?
                """
                
                file_info = file_path_obj.stat()
                params = (
                    str(file_path_obj.absolute()),
                    file_path_obj.name,
                    file_info.st_size,
                    file_path_obj.suffix,
                    str(file_path_obj.parent.absolute()),
                    tool_name,
                    operation_type
                )
                
                # Try insert first, then update if it already exists
                affected = self.db_manager.execute_update(query, params)
                if affected == 0:
                    update_params = (tool_name, operation_type,
                                     str(file_path_obj.absolute()))
                    self.db_manager.execute_update(update_query, update_params)
                
                self.logger.debug("Tracked file access: %s",
                                 file_path_obj.name)
                
            except (OSError, AttributeError) as e:
                self.logger.error("Failed to track file access: %s", e)
        
        def track_directory_access(self, directory_path: str,
                                   tool_name: Optional[str] = None):
            """Track directory access in database."""
            if not self.database_available:
                return
            
            try:
                dir_path_obj = Path(directory_path)
                if not dir_path_obj.exists() or not dir_path_obj.is_dir():
                    return
                
                # Insert or update directory history
                query = """
                    INSERT OR IGNORE INTO directory_history
                    (directory_path, tool_name, access_count, first_accessed,
                     last_accessed)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                
                update_query = """
                    UPDATE directory_history
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP,
                        tool_name = COALESCE(?, tool_name)
                    WHERE directory_path = ?
                """
                
                dir_path_str = str(dir_path_obj.absolute())
                
                # Try insert first, then update if it already exists
                affected = self.db_manager.execute_update(
                    query, (dir_path_str, tool_name))
                if affected == 0:
                    self.db_manager.execute_update(
                        update_query, (tool_name, dir_path_str))
                
                self.logger.debug("Tracked directory access: %s",
                                  dir_path_obj.name)
                
            except (OSError, AttributeError) as e:
                self.logger.error("Failed to track directory access: %s", e)
        
        def create_menu_bar(self):
            """Create the comprehensive application menu bar."""
            try:
                # Import the menu manager
                from gui.menu_manager import MenuManager
                
                # Initialize menu manager for main window
                self.menu_manager = MenuManager(self)
                menubar = self.menu_manager.create_standard_menubar("main")
                
                # Register main window specific callbacks
                self.menu_manager.register_callback('new_project', self.new_project)
                self.menu_manager.register_callback('open_file', self.open_file)
                self.menu_manager.register_callback('save_file', self.save_project)
                self.menu_manager.register_callback('save_as_file', self.save_project_as)
                self.menu_manager.register_callback('export_data', self.export_settings)
                self.menu_manager.register_callback('import_data', self.import_settings)
                self.menu_manager.register_callback('print_document', self.print_info)
                self.menu_manager.register_callback('show_preferences', self.show_main_preferences)
                self.menu_manager.register_callback('show_options', self.show_tool_options)
                self.menu_manager.register_callback('refresh', self.refresh_tool_list)
                
                # Add custom security menu after standard menus
                self._add_security_menu(menubar)
                
                # Add tools menu with specific RFU tools
                self._add_tools_menu(menubar)
                
            except ImportError:
                # Fallback to original menu if menu manager not available
                self._create_fallback_menu_bar()
            except (AttributeError, RuntimeError, KeyError) as e:
                if hasattr(self, 'logger'):
                    self.logger.error("Failed to create menu bar: %s", e)
                else:
                    print(f"Failed to create menu bar: {e}")
                # Try fallback
                self._create_fallback_menu_bar()
        
        def _add_security_menu(self, menubar):
            """Add security-specific menu items."""
            # Security Menu - prominently placed
            security_menu = menubar.addMenu('&Security')
            
            # Security Preferences action
            security_prefs_action = security_menu.addAction('🔒 Security &Preferences...')
            security_prefs_action.setShortcut('Ctrl+Shift+S')
            security_prefs_action.setStatusTip('Configure comprehensive security settings')
            security_prefs_action.triggered.connect(self.open_security_preferences)
            
            security_menu.addSeparator()
            
            # Security Features submenu
            security_features_menu = security_menu.addMenu('🛡️ Security &Features')
            
            # Migration submenu
            migration_menu = security_features_menu.addMenu('🔄 Database &Migration')
            migration_menu.addAction('Execute Migration...').triggered.connect(self.open_migration_dialog)
            migration_menu.addAction('Rollback Migration...').triggered.connect(self.open_rollback_dialog)
            migration_menu.addAction('Validate Schema...').triggered.connect(self.open_schema_validation)
            
            # Theme Security submenu
            theme_security_menu = security_features_menu.addMenu('🎨 &Theme Security')
            theme_security_menu.addAction('Encrypt Themes...').triggered.connect(self.encrypt_themes_action)
            theme_security_menu.addAction('Decrypt Themes...').triggered.connect(self.decrypt_themes_action)
            theme_security_menu.addAction('Scan for Corruption...').triggered.connect(self.scan_theme_corruption_action)
            
            # Directory Security submenu
            directory_security_menu = security_features_menu.addMenu('📁 &Directory Security')
            directory_security_menu.addAction('Manage Protected Directories...').triggered.connect(self.manage_protected_directories)
            directory_security_menu.addAction('Security Monitor...').triggered.connect(self.open_security_monitor)
            
            security_menu.addSeparator()
            
            # Security Tools submenu
            security_tools_menu = security_menu.addMenu('🔧 Security &Tools')
            security_tools_menu.addAction('Test Security Features...').triggered.connect(self.test_security_features_action)
            security_tools_menu.addAction('Security Audit...').triggered.connect(self.run_security_audit_action)
            security_tools_menu.addAction('Export Security Config...').triggered.connect(self.export_security_config_action)
            security_tools_menu.addAction('Import Security Config...').triggered.connect(self.import_security_config_action)
            
            security_menu.addSeparator()
            
            # Emergency Actions
            emergency_menu = security_menu.addMenu('🚨 &Emergency')
            emergency_menu.addAction('Security Lockdown...').triggered.connect(self.emergency_lockdown_action)
            emergency_menu.addAction('Disable All Security...').triggered.connect(self.emergency_disable_action)
            emergency_menu.addAction('Force Security Backup...').triggered.connect(self.force_backup_action)
        
        def _add_tools_menu(self, _menubar):
            """Add tools-specific menu items."""
            # Get existing tools menu from menu manager
            if hasattr(self.menu_manager, 'tools_menu'):
                tools_menu = self.menu_manager.tools_menu
                
                # Add RFU specific tool categories
                tools_menu.addSeparator()
                
                # File Tools submenu
                file_tools_menu = tools_menu.addMenu('📁 &File Tools')
                file_tools_menu.addAction('File Finder').triggered.connect(self.open_file_finder)
                file_tools_menu.addAction('Duplicate Finder').triggered.connect(self.open_duplicate_finder)
                file_tools_menu.addAction('Size Analyzer').triggered.connect(self.open_size_analyzer)
                file_tools_menu.addAction('Organize Files').triggered.connect(self.open_organize)
                
                # Security Tools submenu
                security_tools_menu = tools_menu.addMenu('🔐 &Security Tools')
                security_tools_menu.addAction('Encrypt/Decrypt').triggered.connect(self.open_encrypt_decrypt)
                security_tools_menu.addAction('Secure Delete').triggered.connect(self.open_secure_delete)
                security_tools_menu.addAction('Permissions Editor').triggered.connect(self.open_permissions)
                
                # System Tools submenu
                system_tools_menu = tools_menu.addMenu('⚙️ &System Tools')
                system_tools_menu.addAction('Enhanced Clipboard Manager').triggered.connect(self.open_enhanced_clipboard)
                system_tools_menu.addAction('System Diagnostics').triggered.connect(self.open_system_diagnostics)
                system_tools_menu.addAction('System Cleanup').triggered.connect(self.open_system_cleanup)
                system_tools_menu.addAction('Software Maintenance').triggered.connect(self.open_software_maintenance)
        
        def _create_fallback_menu_bar(self):
            """Create a basic fallback menu bar if the comprehensive system fails."""
            try:
                menubar = self.menuBar()
                
                # File Menu
                file_menu = menubar.addMenu('&File')
                file_menu.addAction('&Exit', self.close, 'Ctrl+Q')
                
                # Help Menu
                help_menu = menubar.addMenu('&Help')
                help_menu.addAction('&About', self.show_about_dialog)
                
            except (AttributeError, RuntimeError, KeyError) as e:
                if hasattr(self, 'logger'):
                    self.logger.error("Failed to create fallback menu bar: %s",
                                     e)
                else:
                    print(f"Failed to create fallback menu bar: {e}")
        
        # Menu callback implementations
        def new_project(self):
            """Create a new project."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "New Project", "New project functionality will be implemented in a future version.")
        
        def open_file(self, file_path=None):
            """Open a file or project."""
            if not file_path:
                from PyQt5.QtWidgets import QFileDialog
                file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
            
            if file_path:
                # Track file access
                self.track_file_access(file_path, "Main Window", "open")
                # Add to recent files
                self._add_to_recent_files(file_path)
        
        def save_project(self):
            """Save current project."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Save", "Project save functionality will be implemented in a future version.")
        
        def save_project_as(self):
            """Save project with new name."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Save As", "Save As functionality will be implemented in a future version.")
        
        def export_settings(self):
            """Export application settings."""
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Settings", "rfu_settings.json", JSON_FILES_FILTER
            )
            
            if file_path:
                try:
                    import json
                    from PyQt5.QtCore import QSettings
                    
                    settings = QSettings("RFU", "MainApplication")
                    settings_dict = {}
                    
                    # Export basic settings
                    for key in settings.allKeys():
                        settings_dict[key] = settings.value(key)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(settings_dict, f, indent=2)
                    
                    QMessageBox.information(self, "Export Complete", f"Settings exported to {file_path}")
                    
                except (OSError, IOError, ValueError, KeyError) as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export settings: {str(e)}")
        
        def import_settings(self):
            """Import application settings."""
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Settings", "", JSON_FILES_FILTER
            )
            
            if file_path:
                try:
                    import json
                    from PyQt5.QtCore import QSettings
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        settings_dict = json.load(f)
                    
                    settings = QSettings("RFU", "MainApplication")
                    
                    for key, value in settings_dict.items():
                        settings.setValue(key, value)
                    
                    QMessageBox.information(self, "Import Complete", "Settings imported successfully. Please restart the application.")
                    
                except (OSError, IOError, ValueError, KeyError) as e:
                    QMessageBox.critical(self, IMPORT_ERROR, f"Failed to import settings: {str(e)}")
        
        def print_info(self):
            """Print application information."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Print", "Print functionality will be implemented in a future version.")
        
        def show_main_preferences(self):
            """Show main application preferences."""
            try:
                self.open_security_preferences()  # Reuse existing preferences dialog
            except Exception:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Preferences", "Preferences dialog will be implemented in a future version.")
        
        def show_tool_options(self):
            """Show tool-specific options."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Tool Options", "Tool options dialog will be implemented in a future version.")
        
        def refresh_tool_list(self):
            """Refresh the tool list and interface."""
            try:
                # Clear any caches
                self.opened_windows.clear()
                
                # Update status
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Tool list refreshed", 2000)
                
            except (AttributeError, RuntimeError, OSError) as e:
                if hasattr(self, 'logger'):
                    self.logger.error("Error refreshing tool list: %s", e)
        
        def show_about_dialog(self):
            """Show about dialog."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.about(self, "About RFU", 
                             f"{APP_NAME} v2.0.0\n\n"
                             "A comprehensive suite of file management tools.\n\n"
                             "© 2025 Richard Noragon")
        
        def _add_to_recent_files(self, file_path):
            """Add file to recent files list."""
            try:
                from PyQt5.QtCore import QSettings
                settings = QSettings("RFU", "Menu_Preferences")
                recent_files = settings.value('recent_files', [])
                
                if isinstance(recent_files, str):
                    recent_files = [recent_files]
                elif not isinstance(recent_files, list):
                    recent_files = []
                
                # Remove if already in list
                if file_path in recent_files:
                    recent_files.remove(file_path)
                
                # Add to beginning
                recent_files.insert(0, file_path)
                
                # Limit to 10 files
                recent_files = recent_files[:10]
                
                settings.setValue('recent_files', recent_files)
                
            except (AttributeError, RuntimeError, OSError) as e:
                if hasattr(self, 'logger'):
                    self.logger.error("Error adding to recent files: %s", e)
        
        def init_ui(self):
            """Initialize the user interface."""
            # Create menu bar
            self.create_menu_bar()
            
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
            
            # Enhanced PDF Tools with Comprehensive Tabbed Interface
            if ENHANCED_PDF_TOOLS_AVAILABLE:
                pdf_tab = self.create_enhanced_pdf_tools_tab()
            else:
                # Fallback to simple PDF tools if enhanced version not available
                pdf_tab = self.create_tool_category_tab([
                    ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                    ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                    ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
                ])
            
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
                ("Enhanced Clipboard Manager", "Comprehensive clipboard management with advanced features", self.open_enhanced_clipboard),
                ("System Diagnostics", "Run system diagnostics and monitoring", self.open_system_diagnostics),
                ("System Cleanup", "Clean system temporary files", self.open_system_cleanup),
                ("Software Maintenance", "Maintain and update software", self.open_software_maintenance),
            ])
            tab_widget.addTab(system_tab, "System Tools")
            
            tab_widget.addTab(pdf_tab, "PDF Tools")
            
            # Add status bar
            self.statusBar().showMessage("Ready - Select a tool to begin")
        
        def create_tool_category_tab(self, tools):
            """Create a tab with tools for a specific category."""
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(5)
            
            # Create scroll area for tools
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameStyle(QFrame.NoFrame)
            scroll_widget = QWidget()
            scroll_layout = QGridLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            scroll_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add tools in a grid layout
            row, col = 0, 0
            for tool_name, description, callback in tools:
                tool_frame = self.create_tool_button(tool_name, description, callback)
                scroll_layout.addWidget(tool_frame, row, col)
                
                col += 1
                if col >= 2:  # 2 columns
                    col = 0
                    row += 1
            
            # Add stretch to push tools to the top
            scroll_layout.setRowStretch(row + 1, 1)
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            
            return tab_widget
        
        def create_tool_button(self, name, description, callback):
            """Create a styled button for a tool."""
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    margin: 5px;
                }
                QFrame:hover {
                    background-color: #e9ecef;
                    border-color: #3498db;
                }
            """)
            
            layout = QVBoxLayout(frame)
            
            # Tool name button
            button = QPushButton(name)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    color: #2c3e50;
                    border: none;
                    padding: 10px;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #3498db;
                }
                QPushButton:pressed {
                    color: #2980b9;
                }
            """)
            button.clicked.connect(callback)
            layout.addWidget(button)
            
            # Description
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #6c757d;
                padding: 0 10px 10px 10px;
            """)
            layout.addWidget(desc_label)
            
            frame.setMaximumHeight(120)
            frame.setMinimumHeight(100)
            
            return frame
        
        def create_enhanced_pdf_tools_tab(self):
            """Create enhanced PDF tools tab with comprehensive tabbed sub-interface"""
            try:
                # Create the enhanced PDF tools widget
                enhanced_pdf_widget = EnhancedPDFToolsWidget(self)
                
                # Connect signals for integration with main hub
                enhanced_pdf_widget.tool_operation_started.connect(self.on_pdf_operation_started)
                enhanced_pdf_widget.tool_operation_completed.connect(self.on_pdf_operation_completed)
                enhanced_pdf_widget.file_selected.connect(self.on_pdf_file_selected)
                
                # Store reference for later use
                self.enhanced_pdf_widget = enhanced_pdf_widget
                
                return enhanced_pdf_widget
                
            except Exception as e:
                print(f"Error creating enhanced PDF tools tab: {e}")
                # Fallback to simple tab
                return self.create_tool_category_tab([
                    ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                    ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                    ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
                ])
        
        def on_pdf_operation_started(self, tool_name: str, operation: str):
            """Handle PDF operation started signal"""
            self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} started...")
            
        def on_pdf_operation_completed(self, tool_name: str, operation: str, success: bool):
            """Handle PDF operation completed signal"""
            if success:
                self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} completed successfully")
            else:
                self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} failed")
                
        def on_pdf_file_selected(self, file_path: str):
            """Handle PDF file selected signal"""
            self.statusBar().showMessage(f"PDF File selected: {os.path.basename(file_path)}")
            
        
        # Tool launcher methods
        def open_file_finder(self):
            """Open File Finder tool."""
            self.launch_tool("File Finder", "src.utilities.file_management.file_finder", "FileFinderGUI")
        
        def open_catalog(self):
            """Open Catalog tool."""
            self.launch_tool("Catalog", "src.utilities.file_management.catalog", "CatalogWindow")
        
        def open_rename(self):
            """Open Rename tool."""
            self.launch_tool("Rename", "src.utilities.file_management.rename", "RenameWindow")
            
        def open_organize(self):
            """Open Organize tool."""
            self.launch_tool("Organize", "src.utilities.file_management.organize", "OrganizeWindow")
            
        def open_cmsd(self):
            """Open Copy/Move/Sync/Delete tool."""
            self.launch_tool("CMSD", "src.utilities.file_operations.cmsd", "CopyMoveSyncDeleteWindow")
            
        def open_compress(self):
            """Open Compress/Decompress tool."""
            self.launch_tool("Compress", "src.utilities.file_operations.compression", "CompressDecompressApp")
            
        def open_file_splitter(self):
            """Open File Splitter tool."""
            self.launch_tool("File Splitter", "src.utilities.file_operations.file_splitter", "FileSplitJoinGUI")
            
        def open_sync(self):
            """Open Sync tool."""
            self.launch_tool("Sync", "src.utilities.file_operations.synchronization_backup.sync", "SyncWindow")
            
        def open_enhanced_editor(self):
            """Open Enhanced Editor tool."""
            self.launch_tool("Enhanced Editor", "src.utilities.file_operations.enhanced_editor.enhanced_editor", "EnhancedEditor")
            
        def open_size_analyzer(self):
            """Open Size Analyzer tool."""
            self.launch_tool("Size Analyzer", "src.utilities.analysis.size_analyzer", "SizeAnalyzerGUI")
            
        def open_duplicate_finder(self):
            """Open Duplicate Finder tool."""
            self.launch_tool("Duplicate Finder", "src.utilities.analysis.find_duplicate_files", "DuplicateFinderApp")
            
        def open_checksum(self):
            """Open Checksum tool."""
            self.launch_tool("Checksum", "src.utilities.analysis.check_sum", "ChecksumGUI")
            
        def open_empty_folders(self):
            """Open Empty Folders tool."""
            self.launch_tool("Empty Folders", "src.utilities.analysis.empty_folders", "EmptyFoldersGUI")
            
        def open_security_preferences(self):
            """Open Security Preferences dialog."""
            try:
                from src.rfu.gui.security_preferences_dialog import SecurityPreferencesDialog
                
                # Check if dialog is already open
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.show()
                    self.security_preferences_dialog.raise_()
                    self.security_preferences_dialog.activateWindow()
                    return
                
                # Create and show new dialog
                self.security_preferences_dialog = SecurityPreferencesDialog(self)
                self.security_preferences_dialog.show()
                self.track_tool_usage("Security Preferences", "open")
                self.statusBar().showMessage("Security Preferences dialog opened")
                
            except ImportError as e:
                self.logger.error(
                    "Failed to import SecurityPreferencesDialog: %s", e)
                QMessageBox.warning(
                    self, 
                    IMPORT_ERROR,
                    f"Security Preferences dialog is not available.\n\n"
                    f"Error: {e}\n\n"
                    f"Please ensure all security components are properly installed."
                )
            except (AttributeError, RuntimeError, OSError) as e:
                self.logger.error("Failed to open Security Preferences: %s", e)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to open Security Preferences dialog:\n\n{e}"
                )
        
        def open_encrypt_decrypt(self):
            """Open Encrypt/Decrypt tool."""
            self.launch_tool("Encrypt/Decrypt", "src.utilities.security.en_and_decrypt", "EnAndDecryptGUI")
            
        def open_secure_delete(self):
            """Open Secure Delete tool."""
            self.launch_tool("Secure Delete", "src.utilities.security.secure_delete", "SecureDeleteGUI")
            
        def open_permissions(self):
            """Open Permissions Editor tool."""
            self.launch_tool("Permissions", "src.utilities.system.permissions_editor", "PermissionsEditorGUI")
            
        def open_image_metadata(self):
            """Open Image Metadata Editor tool."""
            self.launch_tool("Image Metadata", "src.utilities.metadata.image_metadata", "ImageMetadataEditorGUI")
            
        def open_office_metadata(self):
            """Open Office Metadata Editor tool."""
            self.launch_tool("Office Metadata", 
                           "src.utilities.metadata.office_meta_data_editor", 
                           "OfficeMetaDataEditorGUI")
            
        def open_file_touch(self):
            """Open File Touch tool."""
            self.launch_tool("File Touch", 
                           "src.utilities.file_operations.file_touch", 
                           "FileTouchWindow")
            
        def open_pdf_tools(self):
            """Open PDF Tools."""
            self.launch_tool("PDF Tools", "enhanced_pdf_tools_widget", "EnhancedPDFToolsWidget")
            
        def open_pdf_links(self):
            """Open PDF Links Extractor."""
            self.launch_tool("PDF Links", "pdf_utilities.extract_links", "ExtractLinksGUI")
            
        def open_pdf_pages(self):
            """Open PDF Page Administration."""
            self.launch_tool("PDF Pages", "pdf_utilities.page_administration", "PageAdminGUI")
        
        # Network Tools
        def open_network_connectivity(self):
            """Open Network Connectivity tool."""
            self.launch_tool("Network Connectivity", "src.utilities.network.network_connectivity", "NetworkConnectivityGUI")
        
        def open_network_scanner(self):
            """Open Network Scanner tool."""
            self.launch_tool("Network Scanner", "src.utilities.network.network_scanner", "NetworkScannerGUI")
        
        def open_network_transfer(self):
            """Open Network Transfer tool."""
            self.launch_tool("Network Transfer", "src.utilities.network.network_transfer", "NetworkTransferGUI")
        
        def open_bookmark_manager(self):
            """Open Bookmark Manager tool."""
            self.launch_tool("Bookmark Manager", "src.utilities.network.bookmark_manager", "BookmarkManagerGUI")
        
        # Privacy Tools
        def open_privacy_cleaner(self):
            """Open Privacy Cleaner tool."""
            self.launch_tool("Privacy Cleaner", "src.utilities.privacy.privacy_tools_simple", "PrivacyCleanerGUI")
        
        def open_data_anonymizer(self):
            """Open Data Anonymizer tool."""
            self.launch_tool("Data Anonymizer", "src.utilities.privacy.data_anonymizer", "DataAnonymizerGUI")
        
        # System Tools
        def open_enhanced_clipboard(self):
            """Open Enhanced Clipboard Manager tool."""
            self.launch_tool("Enhanced Clipboard Manager", "enhanced_clipboard_system_integration", "EnhancedClipboardGUI")
        
        def open_system_diagnostics(self):
            """Open System Diagnostics tool."""
            self.launch_tool("System Diagnostics", "src.utilities.system.diagnostics_monitoring", "SystemDiagnosticsGUI")
        
        def open_system_cleanup(self):
            """Open System Cleanup tool."""
            self.launch_tool("System Cleanup", "src.utilities.system.system_cleanup", "SystemCleanupGUI")
        
        def open_software_maintenance(self):
            """Open Software Maintenance tool."""
            self.launch_tool("Software Maintenance", "src.utilities.system.software_maintenance", "SoftwareMaintenanceGUI")
        
        # Security Menu Action Methods
        def open_migration_dialog(self):
            """Open migration dialog directly."""
            try:
                self.open_security_preferences()
                # Switch to migration tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(0)  # Migration tab
            except Exception as e:
                self.logger.error(f"Failed to open migration dialog: {e}")
                
        def open_rollback_dialog(self):
            """Open rollback dialog directly."""
            try:
                self.open_security_preferences()
                # Switch to migration tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(0)  # Migration tab
            except Exception as e:
                self.logger.error(f"Failed to open rollback dialog: {e}")
                
        def open_schema_validation(self):
            """Open schema validation directly."""
            try:
                self.open_security_preferences()
                # Switch to migration tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(0)  # Migration tab
            except Exception as e:
                self.logger.error(f"Failed to open schema validation: {e}")
                
        def encrypt_themes_action(self):
            """Quick action to encrypt themes."""
            try:
                self.open_security_preferences()
                # Switch to theme security tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(1)  # Theme security tab
            except Exception as e:
                self.logger.error(f"Failed to open theme encryption: {e}")
                
        def decrypt_themes_action(self):
            """Quick action to decrypt themes."""
            try:
                self.open_security_preferences()
                # Switch to theme security tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(1)  # Theme security tab
            except Exception as e:
                self.logger.error(f"Failed to open theme decryption: {e}")
                
        def scan_theme_corruption_action(self):
            """Quick action to scan for theme corruption."""
            try:
                self.open_security_preferences()
                # Switch to theme security tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(1)  # Theme security tab
            except Exception as e:
                self.logger.error(f"Failed to open theme corruption scan: {e}")
                
        def manage_protected_directories(self):
            """Open directory security management."""
            try:
                self.open_security_preferences()
                # Switch to directory security tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(2)  # Directory security tab
            except Exception as e:
                self.logger.error(f"Failed to open directory security: {e}")
                
        def open_security_monitor(self):
            """Open security status monitor."""
            try:
                self.open_security_preferences()
                # Switch to status monitoring tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(4)  # Status monitoring tab
            except Exception as e:
                self.logger.error(f"Failed to open security monitor: {e}")
                
        def test_security_features_action(self):
            """Test all security features."""
            try:
                # Run the demo security implementation script
                import subprocess
                import sys
                
                result = subprocess.run([
                    sys.executable, 
                    "demo_security_implementation.py"
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode == 0:
                    QMessageBox.information(
                        self,
                        SECURITY_TEST,
                        f"Security feature test completed successfully!\n\n"
                        f"Output:\n{result.stdout}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        SECURITY_TEST,
                        f"Security test completed with warnings:\n\n"
                        f"Error: {result.stderr}\n"
                        f"Output: {result.stdout}"
                    )
                    
                self.track_tool_usage(SECURITY_TEST, "execute")
                
            except Exception as e:
                self.logger.error(f"Failed to run security test: {e}")
                QMessageBox.critical(
                    self,
                    "Security Test Error",
                    f"Failed to execute security feature test:\n\n{e}"
                )
                
        def run_security_audit_action(self):
            """Run comprehensive security audit."""
            try:
                self.open_security_preferences()
                # Switch to audit tab if dialog opens successfully
                if hasattr(self, 'security_preferences_dialog') and self.security_preferences_dialog:
                    self.security_preferences_dialog.tab_widget.setCurrentIndex(3)  # Audit tab
            except Exception as e:
                self.logger.error(f"Failed to open security audit: {e}")
                
        def export_security_config_action(self):
            """Export security configuration."""
            try:
                from datetime import datetime
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Export Security Configuration",
                    f"rfu_security_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    JSON_FILES_FILTER
                )
                
                if file_path:
                    # Export security-related configuration sections
                    security_config = {}
                    security_sections = [
                        'security_migration', 'security_theme', 
                        'security_directory', 'security_audit', 'security_advanced'
                    ]
                    
                    for section in security_sections:
                        security_config[section] = self.config_manager.get_section(section)
                    
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(security_config, f, indent=2, ensure_ascii=False)
                    
                    QMessageBox.information(
                        self,
                        "Export Complete",
                        f"Security configuration exported to:\n{file_path}"
                    )
                    
                    self.track_tool_usage("Security Config Export", "export")
                    
            except Exception as e:
                self.logger.error(f"Failed to export security config: {e}")
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export security configuration:\n\n{e}"
                )
                
        def import_security_config_action(self):
            """Import security configuration."""
            try:
                
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Import Security Configuration",
                    "",
                    JSON_FILES_FILTER
                )
                
                if file_path:
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        security_config = json.load(f)
                    
                    # Import security sections
                    for section, settings in security_config.items():
                        if section.startswith('security_'):
                            self.config_manager.set_section(section, settings)
                    
                    self.config_manager.save_config()
                    
                    QMessageBox.information(
                        self,
                        "Import Complete",
                        f"Security configuration imported from:\n{file_path}\n\n"
                        f"Please restart the application for all changes to take effect."
                    )
                    
                    self.track_tool_usage("Security Config Import", "import")
                    
            except Exception as e:
                self.logger.error(f"Failed to import security config: {e}")
                QMessageBox.critical(
                    self,
                    IMPORT_ERROR, 
                    f"Failed to import security configuration:\n\n{e}"
                )
                
        def emergency_lockdown_action(self):
            """Emergency security lockdown."""
            try:
                from datetime import datetime
                
                reply = QMessageBox.critical(
                    self,
                    "🚨 Emergency Lockdown",
                    "⚠️ WARNING: Emergency Security Lockdown\n\n"
                    "This will:\n"
                    "• Lock all security features\n"
                    "• Force immediate backup\n"
                    "• Log security event\n"
                    "• Restrict access to sensitive operations\n\n"
                    "This action should only be used in emergency situations.\n\n"
                    "Continue with lockdown?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Log emergency action
                    self.logger.critical("Emergency security lockdown initiated by user")
                    
                    # Set emergency lockdown flags in config
                    self.config_manager.set_setting('security_emergency', 'lockdown_active', True)
                    self.config_manager.set_setting('security_emergency', 'lockdown_timestamp', 
                                                   datetime.now().isoformat())
                    self.config_manager.save_config()
                    
                    QMessageBox.information(
                        self,
                        "Lockdown Active",
                        "🔒 Emergency security lockdown is now active.\n\n"
                        "Contact your system administrator to restore normal operation."
                    )
                    
                    self.track_tool_usage("Emergency Lockdown", "activate")
                    
            except Exception as e:
                self.logger.error(f"Failed to execute emergency lockdown: {e}")
                
        def emergency_disable_action(self):
            """Emergency disable all security features."""
            try:
                from datetime import datetime
                
                reply = QMessageBox.critical(
                    self,
                    "🚨 Emergency Disable",
                    "⚠️ CRITICAL WARNING: Disable All Security\n\n"
                    "This will DISABLE ALL security features including:\n"
                    "• Database migration protection\n"
                    "• Theme encryption\n"
                    "• Directory access controls\n"
                    "• Security audit logging\n\n"
                    "⚠️ This leaves your system VULNERABLE!\n\n"
                    "Only use this in critical emergencies!\n\n"
                    "Continue with disabling all security?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Log critical emergency action
                    self.logger.critical("EMERGENCY: All security features disabled by user")
                    
                    # Disable all security features
                    security_sections = [
                        'security_migration', 'security_theme', 
                        'security_directory', 'security_audit'
                    ]
                    
                    for section in security_sections:
                        section_settings = self.config_manager.get_section(section)
                        for key in section_settings:
                            if key.startswith('enable_') or key.endswith('_enabled'):
                                self.config_manager.set_setting(section, key, False)
                    
                    # Set emergency disable flag
                    self.config_manager.set_setting('security_emergency', 'all_disabled', True)
                    self.config_manager.set_setting('security_emergency', 'disable_timestamp', 
                                                   datetime.now().isoformat())
                    self.config_manager.save_config()
                    
                    QMessageBox.warning(
                        self,
                        "Security Disabled",
                        "⚠️ ALL SECURITY FEATURES HAVE BEEN DISABLED!\n\n"
                        "Your system is now vulnerable.\n"
                        "Re-enable security features as soon as possible."
                    )
                    
                    self.track_tool_usage("Emergency Disable All", "disable")
                    
            except Exception as e:
                self.logger.error(f"Failed to execute emergency disable: {e}")
                
        def force_backup_action(self):
            """Force immediate security backup."""
            try:
                QMessageBox.information(
                    self,
                    "Force Backup",
                    "Security backup functionality will be implemented.\n\n"
                    "This will create immediate backups of:\n"
                    "• Database state\n"
                    "• Security configurations\n"
                    "• Theme data\n"
                    "• Directory security settings"
                )
                
                self.track_tool_usage("Force Security Backup", "execute")
                
            except Exception as e:
                self.logger.error(f"Failed to execute force backup: {e}")
                
        def show_security_help(self):
            """Show security help documentation."""
            try:
                QMessageBox.information(
                    self,
                    "Security Help",
                    "RFU Hub Security Features Help\n\n"
                    "📖 Available Documentation:\n"
                    "• Security Implementation Guide\n"
                    "• Migration System Documentation\n" 
                    "• Theme Security Manual\n"
                    "• Directory Protection Guide\n"
                    "• Audit Logging Reference\n\n"
                    "📁 Documentation files:\n"
                    "• RFU_Hub_Security_Implementation_COMPLETE.md\n"
                    "• Implementation Plan Preferences Menu for RFU Hub.md\n\n"
                    "For detailed information, please refer to the documentation files."
                )
            except Exception as e:
                self.logger.error(f"Failed to show security help: {e}")
                
        def show_security_about(self):
            """Show about security features."""
            try:
                QMessageBox.about(
                    self,
                    "About Security Features",
                    "RFU Hub Security Implementation\n\n"
                    "🔒 Comprehensive Security System\n"
                    "Version: 1.0.0\n\n"
                    "Features:\n"
                    "• Database Migration with Rollback\n"
                    "• AES-256-GCM Theme Encryption\n"
                    "• Directory Access Controls\n"
                    "• Comprehensive Audit Logging\n"
                    "• Real-time Security Monitoring\n\n"
                    "Implementation Date: August 2025\n"
                    "Security Standards: Enterprise-grade\n\n"
                    "All security features are designed to protect\n"
                    "your data while maintaining system performance."
                )
            except Exception as e:
                self.logger.error(f"Failed to show security about: {e}")

        def _import_direct(self, module_name, class_name):
            """Strategy 1: Direct module import."""
            try:
                module = __import__(module_name, fromlist=[class_name])
                return getattr(module, class_name)
            except (ImportError, AttributeError):
                return None

        def _import_absolute(self, module_name, class_name):
            """Strategy 2: Absolute path import with explicit path resolution."""
            try:
                # Convert module path to absolute import
                if module_name.startswith('src.'):
                    # Remove 'src.' prefix since we already added src to path
                    clean_module = module_name[4:]
                else:
                    clean_module = module_name
                    
                module = __import__(clean_module, fromlist=[class_name])
                return getattr(module, class_name)
            except (ImportError, AttributeError):
                return None

        def _import_dynamic(self, module_name, class_name):
            """Strategy 3: Dynamic import using importlib."""
            try:
                import importlib
                
                # Try different module path variations
                module_variations = [
                    module_name,
                    module_name.replace('src.', ''),
                    f"src.{module_name}" if not module_name.startswith('src.') else module_name
                ]
                
                for module_path in module_variations:
                    try:
                        module = importlib.import_module(module_path)
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except ImportError:
                        continue
                return None
            except Exception:
                return None

        def _import_legacy(self, module_name, class_name):
            """Strategy 4: Legacy compatibility import."""
            try:
                # Try utilities paths first (new location)
                utilities_paths = [
                    f"src.utilities.file_operations.catalog.{module_name}",
                    f"src.utilities.file_operations.file_touch.{module_name}",
                    f"src.utilities.file_operations.organize.{module_name}",
                    f"src.utilities.file_operations.file_finder.{module_name}",
                    f"src.utilities.file_operations.compression.{module_name}",
                ]
                
                for utilities_path in utilities_paths:
                    try:
                        module = __import__(utilities_path, fromlist=[class_name])
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except (ImportError, AttributeError):
                        continue
                
                # Try legacy paths for backward compatibility
                legacy_paths = [
                    f"src.legacy.file_utilities_1.{module_name}",
                    f"legacy.file_utilities_1.{module_name}",
                    module_name.split('.')[-1]  # Just the final module name
                ]
                
                for legacy_path in legacy_paths:
                    try:
                        module = __import__(legacy_path, fromlist=[class_name])
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except (ImportError, AttributeError):
                        continue
                return None
            except Exception:
                return None

        def _validate_tool_class(self, tool_class, tool_name):
            """Validate that a tool class can be instantiated."""
            try:
                # Quick instantiation test without showing
                test_instance = tool_class()
                if hasattr(test_instance, 'hide'):
                    test_instance.hide()
                if hasattr(test_instance, 'close'):
                    test_instance.close()
                return True
            except Exception as e:
                print(f"Tool validation failed for {tool_name}: {e}")
                return False

        def _launch_validated_tool(self, tool_name, tool_class):
            """Launch a validated tool class."""
            try:
                # Validate before launching
                if not self._validate_tool_class(tool_class, tool_name):
                    self._handle_validation_failure(tool_name)
                    return
                    
                # Create and show the tool
                window = tool_class()
                self.opened_windows[tool_name] = window
                window.show()
                self.statusBar().showMessage(f"{tool_name} opened successfully")
                
            except Exception as e:
                self._handle_instantiation_error(tool_name, e)

        def _handle_import_failure(self, tool_name, module_name, class_name, last_error):
            """Handle import failure with detailed diagnostics."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"{IMPORT_ERROR} - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to import {tool_name}:\n\n"
            error_text += f"Module: {module_name}\n"
            error_text += f"Class: {class_name}\n"
            error_text += f"Last Error: {str(last_error)}\n\n"
            
            # Add diagnostic information
            error_text += "🔍 Diagnostic Information:\n"
            
            # Check if module file exists
            module_path = module_name.replace('.', os.sep) + '.py'
            if os.path.exists(module_path):
                error_text += f"✓ Module file exists: {module_path}\n"
            else:
                error_text += f"✗ Module file not found: {module_path}\n"
            
            # Check Python path
            error_text += f"✓ Python path includes: {sys.path[:3]}...\n"
            
            # Add solution suggestions
            error_text += SUGGESTED_SOLUTIONS_HEADER
            error_text += "• Check if all required dependencies are installed\n"
            error_text += "• Verify the module file exists and is accessible\n"
            error_text += "• Run the automated tool corrector\n"
            error_text += "• Check the import validation utility\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"Import failed for {tool_name}")

        def _handle_validation_failure(self, tool_name):
            """Handle tool validation failure."""
            from PyQt5.QtWidgets import QMessageBox
            
            QMessageBox.warning(
                self,
                f"Validation Error - {tool_name}",
                f"The {tool_name} tool failed validation checks.\n\n"
                f"This usually indicates missing dependencies or "
                f"configuration issues.\n\n"
                f"Please run the diagnostic tools to identify the problem."
            )

        def _handle_instantiation_error(self, tool_name, error):
            """Handle tool instantiation error."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Instantiation Error - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to create {tool_name} window:\n\n{str(error)}\n\n"
            
            # Provide specific guidance based on error type
            if "not defined" in str(error) or "NameError" in str(error):
                error_text += "🔧 This appears to be a missing import issue.\n"
                error_text += "The tool is missing required widget imports.\n\n"
                error_text += "Solutions:\n"
                error_text += "• Check PyQt5 installation\n"
                error_text += "• Verify all imports in the tool file\n"
                error_text += "• Run the automated tool corrector\n"
            elif "QApplication" in str(error):
                error_text += "🔧 QApplication initialization issue.\n"
                error_text += "The tool may have application lifecycle problems.\n"
            else:
                error_text += "🔧 General instantiation error.\n"
                error_text += "Check the tool's __init__ method for issues.\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} instantiation failed")

        def _handle_unexpected_error(self, tool_name, error):
            """Handle unexpected errors during tool launch."""
            from PyQt5.QtWidgets import QMessageBox
            
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred while launching {tool_name}:\n\n"
                f"{str(error)}\n\n"
                f"Please report this issue with the error details."
            )
            self.statusBar().showMessage(f"Unexpected error opening {tool_name}")

        def launch_tool(self, tool_name, module_name, class_name):
            """Enhanced tool launcher with comprehensive error handling and multiple import strategies."""
            try:
                # Check if tool is already open
                if tool_name in self.opened_windows:
                    window = self.opened_windows[tool_name]
                    if window and hasattr(window, 'show'):
                        window.show()
                        window.raise_()
                        window.activateWindow()
                        self.statusBar().showMessage(f"{tool_name} window activated")
                        return
                
                # Multiple import strategies with fallbacks
                import_strategies = [
                    # Strategy 1: Direct module import
                    lambda: self._import_direct(module_name, class_name),
                    # Strategy 2: Absolute path import
                    lambda: self._import_absolute(module_name, class_name),
                    # Strategy 3: Dynamic import with importlib
                    lambda: self._import_dynamic(module_name, class_name),
                    # Strategy 4: Legacy compatibility import
                    lambda: self._import_legacy(module_name, class_name)
                ]
                
                tool_class = None
                last_error = None
                
                self.statusBar().showMessage(f"Loading {tool_name}...")
                
                for i, strategy in enumerate(import_strategies, 1):
                    try:
                        tool_class = strategy()
                        if tool_class:
                            self.statusBar().showMessage(f"Loaded {tool_name} using strategy {i}")
                            break
                    except Exception as e:
                        last_error = e
                        continue
                
                if tool_class is None:
                    self._handle_import_failure(tool_name, module_name, class_name, last_error)
                    return
                    
                # Launch the validated tool
                self._launch_validated_tool(tool_name, tool_class)
                
            except Exception as e:
                self._handle_unexpected_error(tool_name, e)
                
        def validate_tool_before_launch(self, module_name, class_name):
            """Validate tool dependencies before launch."""
            validation_result = {
                "success": True,
                "errors": [],
                "warnings": []
            }
            
            try:
                # Test import
                try:
                    module = __import__(module_name)
                except ImportError as e:
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Import failed: {str(e)}")
                    return validation_result
                
                # Test class existence
                if not hasattr(module, class_name):
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Class '{class_name}' not found in module")
                    return validation_result
                
                # Test basic instantiation (without showing)
                try:
                    tool_class = getattr(module, class_name)
                    # Quick instantiation test
                    test_instance = tool_class()
                    if hasattr(test_instance, 'hide'):
                        test_instance.hide()
                    if hasattr(test_instance, 'close'):
                        test_instance.close()
                except Exception as e:
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Instantiation failed: {str(e)}")
                    return validation_result
                    
            except Exception as e:
                validation_result["success"] = False
                validation_result["errors"].append(f"Validation error: {str(e)}")
            
            return validation_result
            
        def show_enhanced_error_dialog(self, tool_name, module_name, validation_result):
            """Show enhanced error dialog with specific guidance."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Tool Launch Error - {tool_name}")
            msg.setIcon(QMessageBox.Warning)
            
            error_text = f"Could not launch {tool_name}:\n\n"
            for error in validation_result["errors"]:
                error_text += f"• {error}\n"
            
            # Add specific guidance based on error type
            if "Import failed" in str(validation_result["errors"]):
                error_text += SUGGESTED_SOLUTIONS_HEADER
                error_text += f"• Check if {module_name}.py exists in the current directory\n"
                error_text += "• Verify all required dependencies are installed\n"
                error_text += "• Run the automated tool corrector to fix missing tools\n"
            elif "not found" in str(validation_result["errors"]):
                error_text += SUGGESTED_SOLUTIONS_HEADER
                error_text += f"• Check class name in {module_name}.py\n"
                error_text += "• Run the comprehensive test suite for validation\n"
            elif "Instantiation failed" in str(validation_result["errors"]):
                error_text += SUGGESTED_SOLUTIONS_HEADER
                error_text += "• Check for missing PyQt5 widget imports\n"
                error_text += "• Verify all dependencies are properly imported\n"
                error_text += "• Check the tool's __init__ method for errors\n"
            
            msg.setText(error_text)
            msg.setInformativeText(f"Module: {module_name}\nTool Status: Needs attention")
            msg.exec_()
            self.statusBar().showMessage(f"Failed to open {tool_name} - See error details")
            
        def show_enhanced_placeholder_window(self, tool_name, module_name, import_error):
            """Show enhanced placeholder with specific error information."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"{tool_name} - Tool Not Available")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"The {tool_name} tool is currently not available.")
            
            info_text = f"Module: {module_name}\n"
            if import_error:
                info_text += f"Error: {str(import_error)}\n"
            info_text += "\n🔧 Quick Fix Options:\n"
            info_text += "• Run: python automated_tool_corrector.py --mode=single --tool=" + module_name + "\n"
            info_text += "• Run: python comprehensive_test_suite.py\n"
            info_text += "• Check the tool integration documentation\n"
            
            msg.setInformativeText(info_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} not available - Use automated corrector")
            
        def show_instantiation_error_dialog(self, tool_name, error):
            """Show specific error dialog for instantiation failures."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Tool Instantiation Error - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to create {tool_name} window:\n\n{str(error)}\n\n"
            
            # Provide specific guidance based on error type
            if "not defined" in str(error):
                error_text += "🔧 This appears to be a missing import issue.\n"
                error_text += "The tool is missing required PyQt5 widget imports.\n\n"
                error_text += "Quick Fix:\n"
                error_text += "• Run the automated tool corrector to fix imports\n"
                error_text += "• Check the tool's import statements\n"
            elif "QApplication" in str(error):
                error_text += "🔧 This is a QApplication initialization issue.\n"
                error_text += "The tool may be trying to create widgets before QApplication is ready.\n"
            else:
                error_text += "🔧 General instantiation error.\n"
                error_text += "Check the tool's __init__ method for issues.\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} instantiation failed")
            
        def show_generic_error_dialog(self, tool_name, error):
            """Show generic error dialog for unexpected errors."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred while launching {tool_name}:\n\n{str(error)}\n\n"
                f"Please report this issue with the error details."
            )
            self.statusBar().showMessage(f"Unexpected error opening {tool_name}")
        
        def show_placeholder_window(self, tool_name, module_name):
            """Show a placeholder window for tools that aren't implemented yet."""
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(f"{tool_name} - Not Available")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"The {tool_name} tool is currently being integrated.")
            msg.setInformativeText(
                f"Module: {module_name}\n\n"
                f"This tool will be available in a future update. "
                f"The integration is in progress."
            )
            msg.exec_()
    
    def main():
        """Main entry point for the application."""
        print(f"Starting {APP_NAME}...")
        
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName(APP_NAME)
        
        # Create and show main window
        window = RFUMainWindow()
        window.show()
        
        print("Application window displayed. Use the tabs to access different tools.")
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