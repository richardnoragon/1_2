# Advanced Folders - RFU Integration Guide

## Overview

This guide provides step-by-step instructions for integrating the Advanced Folders system into the main Richard's File Utilities (RFU) application, following established architectural patterns and conventions.

## Integration Architecture

### RFU Integration Points

```
RFU Main Application
├── main.py (Hub launcher)
├── hub.py (Main interface)
├── config_manager.py (Settings)
├── utilities/
│   └── advanced_folders/  ← New integration point
│       ├── advanced_folders_gui.py
│       ├── folder_manager_gui.py
│       ├── smart_search_gui.py
│       └── performance_dashboard_gui.py
└── src/rfu/advanced_folders/  ← Core engine (existing)
```

### Integration Strategy

1. **Tool Registration**: Add Advanced Folders tools to main tool hub
2. **GUI Implementation**: Create PyQt5 GUI classes following RFU patterns
3. **Configuration Integration**: Use existing ConfigManager
4. **Database Integration**: Leverage existing database infrastructure
5. **Error Handling**: Integrate with RFU error handling system
6. **Menu Integration**: Add to main application menus

## Step 1: Update main.py

### Add Tool Category Tab

```python
# In main.py - add to init_ui method
def init_ui(self):
    # ... existing code ...
    
    # Add Advanced Folders tab
    self.init_advanced_folders_tab()

def init_advanced_folders_tab(self):
    """Initialize Advanced Folders tools tab."""
    advanced_folders_tools = [
        ("Folder Manager", "Configure and manage advanced folder settings", 
         self.open_folder_manager),
        ("Smart Search", "Advanced file search with indexing and caching", 
         self.open_smart_search),
        ("Performance Dashboard", "Monitor file operations performance", 
         self.open_performance_dashboard),
        ("Metadata Explorer", "Browse and analyze file metadata", 
         self.open_metadata_explorer),
    ]
    
    for tool_name, description, handler in advanced_folders_tools:
        self.add_tool_to_tab("Advanced Folders", tool_name, description, handler)
```

### Add Tool Launchers

```python
# In main.py - add launcher methods
def open_folder_manager(self):
    """Launch Folder Manager tool."""
    self.launch_tool(
        "Folder Manager", 
        "src.utilities.advanced_folders.folder_manager_gui", 
        "FolderManagerGUI"
    )

def open_smart_search(self):
    """Launch Smart Search tool."""
    self.launch_tool(
        "Smart Search", 
        "src.utilities.advanced_folders.smart_search_gui", 
        "SmartSearchGUI"
    )

def open_performance_dashboard(self):
    """Launch Performance Dashboard tool."""
    self.launch_tool(
        "Performance Dashboard", 
        "src.utilities.advanced_folders.performance_dashboard_gui", 
        "PerformanceDashboardGUI"
    )

def open_metadata_explorer(self):
    """Launch Metadata Explorer tool."""
    self.launch_tool(
        "Metadata Explorer", 
        "src.utilities.advanced_folders.metadata_explorer_gui", 
        "MetadataExplorerGUI"
    )
```

## Step 2: Create GUI Components

### Base GUI Class

Create `src/utilities/advanced_folders/base_advanced_gui.py`:

```python
"""
Base GUI class for Advanced Folders tools.
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QTimer

from config_manager import get_config_manager
from log_manager import get_log_manager


class BaseAdvancedFoldersGUI(QMainWindow):
    """Base class for Advanced Folders GUI components."""
    
    def __init__(self, tool_name: str):
        super().__init__()
        self.tool_name = tool_name
        self.config_manager = get_config_manager()
        self.logger = get_log_manager().get_logger(f'AdvancedFolders.{tool_name}')
        
        # Initialize common resources
        self.init_common_resources()
        
        # Set up UI
        self.setWindowTitle(f"RFU - {tool_name}")
        self.setMinimumSize(800, 600)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def init_common_resources(self):
        """Initialize common Advanced Folders resources."""
        try:
            # Import core components
            from src.rfu.advanced_folders.core.file_system_scanner import FileSystemScanner
            from src.rfu.advanced_folders.core.search_engine import SearchEngine
            from src.rfu.advanced_folders.core.search_cache import SearchResultCache
            from src.rfu.advanced_folders.core.metadata_pipeline import MetadataExtractionPipeline
            from src.rfu.advanced_folders.core.performance_monitor import PerformanceMonitor
            
            # Get database paths from config
            db_base_path = self.config_manager.get_setting("database", "db_path", "data/")
            
            # Initialize core components
            self.scanner = FileSystemScanner()
            self.search_engine = SearchEngine(db_path=f"{db_base_path}/search_index.db")
            self.cache = SearchResultCache(db_path=f"{db_base_path}/search_cache.db")
            self.metadata_pipeline = MetadataExtractionPipeline()
            self.performance_monitor = PerformanceMonitor(
                db_path=f"{db_base_path}/performance.db"
            )
            
            self.logger.info(f"Initialized {self.tool_name} with Advanced Folders components")
            
        except Exception as e:
            self.logger.error(f"Error initializing Advanced Folders components: {str(e)}")
            self.show_error_message("Initialization Error", 
                                   f"Failed to initialize Advanced Folders: {str(e)}")
    
    def show_error_message(self, title: str, message: str):
        """Show error message dialog."""
        QMessageBox.critical(self, title, message)
    
    def show_info_message(self, title: str, message: str):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)
    
    def update_status(self):
        """Update status information - override in subclasses."""
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop performance monitoring
            if hasattr(self, 'performance_monitor'):
                self.performance_monitor.stop_monitoring()
            
            # Stop status timer
            self.status_timer.stop()
            
            self.logger.info(f"{self.tool_name} closed")
            
        except Exception as e:
            self.logger.error(f"Error during {self.tool_name} shutdown: {str(e)}")
        
        event.accept()
```

### Folder Manager GUI

Create `src/utilities/advanced_folders/folder_manager_gui.py`:

```python
"""
Folder Manager GUI for Advanced Folders system.
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QComboBox, QCheckBox, QSpinBox, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QSplitter, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from .base_advanced_gui import BaseAdvancedFoldersGUI
from src.rfu.advanced_folders.models.folder_configuration import (
    FolderConfiguration, SortOption, ViewMode, FilterOption
)


class FolderScanWorker(QThread):
    """Worker thread for folder scanning."""
    
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scanner, folder_path, config):
        super().__init__()
        self.scanner = scanner
        self.folder_path = folder_path
        self.config = config
    
    def run(self):
        try:
            self.progress_updated.emit(0, "Starting scan...")
            
            files = self.scanner.scan_directory(
                self.folder_path,
                recursive=self.config.is_recursive,
                exclusion_patterns=self.config.exclusion_patterns
            )
            
            self.progress_updated.emit(100, f"Completed - found {len(files)} files")
            self.scan_completed.emit(files)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class FolderManagerGUI(BaseAdvancedFoldersGUI):
    """GUI for managing Advanced Folders configurations."""
    
    def __init__(self):
        super().__init__("Folder Manager")
        self.setup_ui()
        self.load_configurations()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(splitter)
        
        # Left panel - Configuration list
        self.setup_config_list_panel(splitter)
        
        # Right panel - Configuration details
        self.setup_config_details_panel(splitter)
        
        # Bottom panel - Actions
        self.setup_actions_panel()
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
    
    def setup_config_list_panel(self, parent):
        """Set up the configuration list panel."""
        list_widget = QGroupBox("Folder Configurations")
        list_layout = QVBoxLayout(list_widget)
        
        # Configuration list
        self.config_list = QListWidget()
        self.config_list.itemSelectionChanged.connect(self.on_config_selected)
        list_layout.addWidget(self.config_list)
        
        # List actions
        list_actions = QHBoxLayout()
        
        self.add_button = QPushButton("Add Folder")
        self.add_button.clicked.connect(self.add_folder_configuration)
        list_actions.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_folder_configuration)
        self.remove_button.setEnabled(False)
        list_actions.addWidget(self.remove_button)
        
        list_layout.addLayout(list_actions)
        parent.addWidget(list_widget)
    
    def setup_config_details_panel(self, parent):
        """Set up the configuration details panel."""
        details_widget = QGroupBox("Configuration Details")
        details_layout = QVBoxLayout(details_widget)
        
        # Configuration form
        form_layout = QGridLayout()
        
        # Folder path
        form_layout.addWidget(QLabel("Folder Path:"), 0, 0)
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.textChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.folder_path_edit, 0, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        form_layout.addWidget(self.browse_button, 0, 2)
        
        # Display name
        form_layout.addWidget(QLabel("Display Name:"), 1, 0)
        self.display_name_edit = QLineEdit()
        self.display_name_edit.textChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.display_name_edit, 1, 1, 1, 2)
        
        # Sort option
        form_layout.addWidget(QLabel("Sort By:"), 2, 0)
        self.sort_combo = QComboBox()
        for option in SortOption:
            self.sort_combo.addItem(option.value.title(), option)
        self.sort_combo.currentTextChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.sort_combo, 2, 1, 1, 2)
        
        # View mode
        form_layout.addWidget(QLabel("View Mode:"), 3, 0)
        self.view_combo = QComboBox()
        for mode in ViewMode:
            self.view_combo.addItem(mode.value.title(), mode)
        self.view_combo.currentTextChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.view_combo, 3, 1, 1, 2)
        
        # Options
        form_layout.addWidget(QLabel("Options:"), 4, 0)
        options_layout = QVBoxLayout()
        
        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.stateChanged.connect(self.on_config_changed)
        options_layout.addWidget(self.recursive_check)
        
        self.auto_scan_check = QCheckBox("Auto-scan folder")
        self.auto_scan_check.stateChanged.connect(self.on_config_changed)
        options_layout.addWidget(self.auto_scan_check)
        
        form_layout.addLayout(options_layout, 4, 1, 1, 2)
        
        # Scan interval
        form_layout.addWidget(QLabel("Scan Interval (minutes):"), 5, 0)
        self.scan_interval_spin = QSpinBox()
        self.scan_interval_spin.setRange(1, 1440)  # 1 minute to 24 hours
        self.scan_interval_spin.setValue(60)
        self.scan_interval_spin.valueChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.scan_interval_spin, 5, 1, 1, 2)
        
        # Exclusion patterns
        form_layout.addWidget(QLabel("Exclusion Patterns:"), 6, 0)
        self.exclusion_patterns_edit = QTextEdit()
        self.exclusion_patterns_edit.setMaximumHeight(100)
        self.exclusion_patterns_edit.setPlaceholderText("Enter patterns (one per line)\nExample: *.tmp\n.*\n__pycache__")
        self.exclusion_patterns_edit.textChanged.connect(self.on_config_changed)
        form_layout.addWidget(self.exclusion_patterns_edit, 6, 1, 1, 2)
        
        details_layout.addLayout(form_layout)
        
        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.save_current_configuration)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        self.scan_button = QPushButton("Scan Now")
        self.scan_button.clicked.connect(self.scan_current_folder)
        self.scan_button.setEnabled(False)
        button_layout.addWidget(self.scan_button)
        
        button_layout.addStretch()
        details_layout.addLayout(button_layout)
        
        parent.addWidget(details_widget)
    
    def setup_actions_panel(self):
        """Set up the actions panel."""
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        actions_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        actions_layout.addWidget(self.status_label)
        
        actions_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_configurations)
        actions_layout.addWidget(refresh_button)
        
        self.layout.addWidget(actions_group)
    
    def load_configurations(self):
        """Load folder configurations from database."""
        try:
            # Get database path
            db_base_path = self.config_manager.get_setting("database", "db_path", "data/")
            db_path = f"{db_base_path}/advanced_folders.db"
            
            # Load configurations
            configs = FolderConfiguration.load_all(db_path)
            
            # Update list
            self.config_list.clear()
            for config in configs:
                item = QListWidgetItem(f"{config.display_name} ({config.folder_path})")
                item.setData(Qt.UserRole, config)
                self.config_list.addItem(item)
            
            self.status_label.setText(f"Loaded {len(configs)} configurations")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {str(e)}")
            self.show_error_message("Load Error", f"Failed to load configurations: {str(e)}")
    
    def on_config_selected(self):
        """Handle configuration selection."""
        current_item = self.config_list.currentItem()
        if current_item:
            config = current_item.data(Qt.UserRole)
            self.load_configuration_to_form(config)
            self.remove_button.setEnabled(True)
            self.scan_button.setEnabled(True)
        else:
            self.clear_form()
            self.remove_button.setEnabled(False)
            self.scan_button.setEnabled(False)
    
    def load_configuration_to_form(self, config: FolderConfiguration):
        """Load configuration data into form."""
        self.folder_path_edit.setText(config.folder_path)
        self.display_name_edit.setText(config.display_name)
        
        # Set combo box values
        for i in range(self.sort_combo.count()):
            if self.sort_combo.itemData(i) == config.sort_option:
                self.sort_combo.setCurrentIndex(i)
                break
        
        for i in range(self.view_combo.count()):
            if self.view_combo.itemData(i) == config.view_mode:
                self.view_combo.setCurrentIndex(i)
                break
        
        self.recursive_check.setChecked(config.is_recursive)
        self.auto_scan_check.setChecked(config.auto_scan)
        self.scan_interval_spin.setValue(config.scan_interval_minutes)
        
        # Load exclusion patterns
        self.exclusion_patterns_edit.setPlainText('\n'.join(config.exclusion_patterns))
        
        self.save_button.setEnabled(False)  # No changes yet
    
    def clear_form(self):
        """Clear the configuration form."""
        self.folder_path_edit.clear()
        self.display_name_edit.clear()
        self.sort_combo.setCurrentIndex(0)
        self.view_combo.setCurrentIndex(0)
        self.recursive_check.setChecked(True)
        self.auto_scan_check.setChecked(False)
        self.scan_interval_spin.setValue(60)
        self.exclusion_patterns_edit.clear()
        self.save_button.setEnabled(False)
    
    def on_config_changed(self):
        """Handle configuration changes."""
        self.save_button.setEnabled(True)
    
    def browse_folder(self):
        """Browse for folder path."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path_edit.setText(folder)
            
            # Auto-generate display name if empty
            if not self.display_name_edit.text():
                self.display_name_edit.setText(os.path.basename(folder))
    
    def add_folder_configuration(self):
        """Add new folder configuration."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Add")
        if folder:
            # Create new configuration
            config = FolderConfiguration(
                folder_path=folder,
                display_name=os.path.basename(folder),
                sort_option=SortOption.NAME,
                view_mode=ViewMode.LIST
            )
            
            # Save to database
            try:
                db_base_path = self.config_manager.get_setting("database", "db_path", "data/")
                db_path = f"{db_base_path}/advanced_folders.db"
                config.save(db_path)
                
                # Reload configurations
                self.load_configurations()
                
                # Select the new configuration
                for i in range(self.config_list.count()):
                    item = self.config_list.item(i)
                    item_config = item.data(Qt.UserRole)
                    if item_config.folder_path == folder:
                        self.config_list.setCurrentItem(item)
                        break
                
                self.status_label.setText(f"Added configuration for {folder}")
                
            except Exception as e:
                self.logger.error(f"Error adding configuration: {str(e)}")
                self.show_error_message("Add Error", f"Failed to add configuration: {str(e)}")
    
    def remove_folder_configuration(self):
        """Remove selected folder configuration."""
        current_item = self.config_list.currentItem()
        if current_item:
            config = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Remove configuration for '{config.display_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    db_base_path = self.config_manager.get_setting("database", "db_path", "data/")
                    db_path = f"{db_base_path}/advanced_folders.db"
                    config.delete(db_path)
                    
                    self.load_configurations()
                    self.status_label.setText(f"Removed configuration for {config.folder_path}")
                    
                except Exception as e:
                    self.logger.error(f"Error removing configuration: {str(e)}")
                    self.show_error_message("Remove Error", f"Failed to remove configuration: {str(e)}")
    
    def save_current_configuration(self):
        """Save current configuration."""
        current_item = self.config_list.currentItem()
        if current_item:
            config = current_item.data(Qt.UserRole)
            
            # Update configuration from form
            config.folder_path = self.folder_path_edit.text()
            config.display_name = self.display_name_edit.text()
            config.sort_option = self.sort_combo.currentData()
            config.view_mode = self.view_combo.currentData()
            config.is_recursive = self.recursive_check.isChecked()
            config.auto_scan = self.auto_scan_check.isChecked()
            config.scan_interval_minutes = self.scan_interval_spin.value()
            
            # Parse exclusion patterns
            patterns_text = self.exclusion_patterns_edit.toPlainText()
            config.exclusion_patterns = [
                line.strip() for line in patterns_text.split('\n')
                if line.strip()
            ]
            
            try:
                db_base_path = self.config_manager.get_setting("database", "db_path", "data/")
                db_path = f"{db_base_path}/advanced_folders.db"
                config.save(db_path)
                
                self.save_button.setEnabled(False)
                self.load_configurations()
                self.status_label.setText(f"Saved configuration for {config.folder_path}")
                
            except Exception as e:
                self.logger.error(f"Error saving configuration: {str(e)}")
                self.show_error_message("Save Error", f"Failed to save configuration: {str(e)}")
    
    def scan_current_folder(self):
        """Scan the currently selected folder."""
        current_item = self.config_list.currentItem()
        if current_item:
            config = current_item.data(Qt.UserRole)
            
            if not os.path.exists(config.folder_path):
                self.show_error_message("Scan Error", f"Folder does not exist: {config.folder_path}")
                return
            
            # Start scan in worker thread
            self.scan_worker = FolderScanWorker(self.scanner, config.folder_path, config)
            self.scan_worker.progress_updated.connect(self.on_scan_progress)
            self.scan_worker.scan_completed.connect(self.on_scan_completed)
            self.scan_worker.error_occurred.connect(self.on_scan_error)
            
            self.progress_bar.setVisible(True)
            self.scan_button.setEnabled(False)
            self.scan_worker.start()
    
    def on_scan_progress(self, progress: int, message: str):
        """Handle scan progress updates."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def on_scan_completed(self, files: list):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        
        # Index files in search engine
        try:
            for file_info in files:
                self.search_engine.add_file(file_info)
            
            self.status_label.setText(f"Scan completed - indexed {len(files)} files")
            
        except Exception as e:
            self.logger.error(f"Error indexing files: {str(e)}")
            self.status_label.setText(f"Scan completed but indexing failed: {str(e)}")
    
    def on_scan_error(self, error_message: str):
        """Handle scan errors."""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        self.status_label.setText("Scan failed")
        self.show_error_message("Scan Error", error_message)
```

## Step 3: Update Configuration

### Add Advanced Folders Settings

Update `config_manager.py` or add to initialization:

```python
def init_advanced_folders_config():
    """Initialize Advanced Folders configuration settings."""
    config = get_config_manager()
    
    # Database settings
    config.set_setting("advanced_folders", "search_db_path", "data/search_index.db")
    config.set_setting("advanced_folders", "cache_db_path", "data/search_cache.db")
    config.set_setting("advanced_folders", "performance_db_path", "data/performance.db")
    config.set_setting("advanced_folders", "config_db_path", "data/advanced_folders.db")
    
    # Performance settings
    config.set_setting("advanced_folders", "max_scan_workers", 4)
    config.set_setting("advanced_folders", "max_search_results", 1000)
    config.set_setting("advanced_folders", "cache_size_entries", 1000)
    config.set_setting("advanced_folders", "cache_ttl_hours", 24)
    
    # UI settings
    config.set_setting("advanced_folders", "auto_refresh_interval", 5)
    config.set_setting("advanced_folders", "show_hidden_files", False)
    config.set_setting("advanced_folders", "default_view_mode", "list")
    
    # Monitoring settings
    config.set_setting("advanced_folders", "enable_performance_monitoring", True)
    config.set_setting("advanced_folders", "monitoring_interval", 5)
    config.set_setting("advanced_folders", "alert_thresholds", {
        "search_duration_ms": 5000,
        "scan_duration_ms": 10000,
        "memory_usage_percent": 80
    })
```

## Step 4: Update Database Schema

### Create Migration Script

Create `scripts/migrations/add_advanced_folders_tables.py`:

```python
"""
Migration script to add Advanced Folders tables to existing RFU database.
"""

import sqlite3
import os
from config_manager import get_config_manager

def migrate_database():
    """Add Advanced Folders tables to database."""
    config = get_config_manager()
    db_path = config.get_setting("database", "db_path", "data/rfu_database.db")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        # Add Advanced Folders tables
        conn.executescript("""
            -- Folder configurations
            CREATE TABLE IF NOT EXISTS advanced_folder_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT UNIQUE NOT NULL,
                display_name TEXT,
                sort_option TEXT,
                view_mode TEXT,
                filter_options_json TEXT,
                is_recursive BOOLEAN DEFAULT TRUE,
                auto_scan BOOLEAN DEFAULT FALSE,
                scan_interval_minutes INTEGER DEFAULT 60,
                exclusion_patterns_json TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                last_scan_time TEXT,
                is_active BOOLEAN DEFAULT TRUE
            );
            
            -- Search index
            CREATE TABLE IF NOT EXISTS advanced_search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                modified_time TEXT,
                is_directory BOOLEAN,
                file_extension TEXT,
                metadata_json TEXT,
                indexed_time TEXT DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT
            );
            
            -- Search cache
            CREATE TABLE IF NOT EXISTS advanced_search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                parameters_json TEXT NOT NULL,
                results_json TEXT NOT NULL,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_time TEXT NOT NULL,
                access_count INTEGER DEFAULT 1,
                last_access_time TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Performance metrics
            CREATE TABLE IF NOT EXISTS advanced_performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                operation_name TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                resource_usage_json TEXT,
                metadata_json TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_af_config_path 
                ON advanced_folder_configurations(folder_path);
            CREATE INDEX IF NOT EXISTS idx_af_search_path 
                ON advanced_search_index(file_path);
            CREATE INDEX IF NOT EXISTS idx_af_search_name 
                ON advanced_search_index(file_name);
            CREATE INDEX IF NOT EXISTS idx_af_cache_key 
                ON advanced_search_cache(cache_key);
            CREATE INDEX IF NOT EXISTS idx_af_performance_timestamp 
                ON advanced_performance_metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_af_performance_type 
                ON advanced_performance_metrics(metric_type);
        """)
        
        print("Advanced Folders database tables created successfully")

if __name__ == "__main__":
    migrate_database()
```

## Step 5: Update Menu System

### Add to Main Menu

Update `menu_manager.py` or equivalent:

```python
def setup_advanced_folders_menu(self):
    """Set up Advanced Folders menu items."""
    # Add to main menu bar
    advanced_menu = self.menubar.addMenu("Advanced Folders")
    
    # Folder management
    folder_manager_action = advanced_menu.addAction("Folder Manager")
    folder_manager_action.triggered.connect(self.open_folder_manager)
    
    # Search
    smart_search_action = advanced_menu.addAction("Smart Search")
    smart_search_action.triggered.connect(self.open_smart_search)
    
    advanced_menu.addSeparator()
    
    # Performance
    performance_action = advanced_menu.addAction("Performance Dashboard")
    performance_action.triggered.connect(self.open_performance_dashboard)
    
    # Settings
    settings_action = advanced_menu.addAction("Advanced Folders Settings")
    settings_action.triggered.connect(self.open_advanced_folders_settings)
```

## Step 6: Testing Integration

### Integration Test Script

Create `tests/test_advanced_folders_integration.py`:

```python
"""
Integration tests for Advanced Folders with RFU.
"""

import unittest
import tempfile
import os
from pathlib import Path

# Test imports
def test_imports():
    """Test that all Advanced Folders components can be imported."""
    try:
        # Core components
        from src.rfu.advanced_folders.core.file_system_scanner import FileSystemScanner
        from src.rfu.advanced_folders.core.search_engine import SearchEngine
        from src.rfu.advanced_folders.models.folder_configuration import FolderConfiguration
        
        # GUI components
        from src.utilities.advanced_folders.folder_manager_gui import FolderManagerGUI
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_database_integration():
    """Test database integration."""
    try:
        from config_manager import get_config_manager
        
        config = get_config_manager()
        db_path = config.get_setting("database", "db_path", "data/test.db")
        
        # Test folder configuration
        from src.rfu.advanced_folders.models.folder_configuration import FolderConfiguration, SortOption, ViewMode
        
        test_config = FolderConfiguration(
            folder_path="/test/path",
            display_name="Test Folder",
            sort_option=SortOption.NAME,
            view_mode=ViewMode.LIST
        )
        
        test_config.save(db_path)
        loaded_config = FolderConfiguration.load(db_path, "/test/path")
        
        assert loaded_config is not None
        assert loaded_config.display_name == "Test Folder"
        
        print("✓ Database integration successful")
        return True
    except Exception as e:
        print(f"❌ Database integration failed: {str(e)}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("Running Advanced Folders Integration Tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_integration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
```

## Step 7: Documentation Updates

### Update Main README

Add to main `README.md`:

```markdown
## Advanced Folders Feature

RFU now includes an Advanced Folders system that provides:

- **Smart Folder Management**: Configure folder settings with auto-scanning
- **Enterprise Search**: Fast file search with indexing and caching  
- **Performance Monitoring**: Track and optimize file operations
- **Metadata Extraction**: Analyze file properties and content

### Getting Started

1. Launch RFU
2. Go to the "Advanced Folders" tab
3. Click "Folder Manager" to configure your first managed folder
4. Use "Smart Search" for fast file searching

### Configuration

Advanced Folders settings are stored in the RFU database and can be configured through the GUI or by modifying configuration files.
```

## Step 8: Deployment Checklist

### Pre-Deployment Verification

- [ ] All GUI components launch without errors
- [ ] Database migrations run successfully  
- [ ] Configuration settings are properly integrated
- [ ] Menu items are functional
- [ ] Error handling works correctly
- [ ] Performance monitoring is operational
- [ ] File scanning and indexing work
- [ ] Search functionality is responsive
- [ ] Cache system is functioning

### Deployment Steps

1. **Backup existing RFU data**
2. **Run database migration script**
3. **Update configuration files**
4. **Install Advanced Folders GUI components**
5. **Update main.py with new tool registrations**
6. **Test all functionality**
7. **Update user documentation**

### Post-Deployment Verification

- [ ] All existing RFU functionality still works
- [ ] Advanced Folders tools are accessible
- [ ] Performance is acceptable
- [ ] Error logging is working
- [ ] Database integrity is maintained

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Python path includes Advanced Folders modules
2. **Database Errors**: Check database permissions and run migrations
3. **GUI Not Opening**: Verify PyQt5 dependencies and error logs
4. **Performance Issues**: Review resource usage and adjust settings
5. **Search Not Working**: Check index status and rebuild if necessary

### Support

For issues with the Advanced Folders integration:

1. Check the RFU logs for error messages
2. Verify database schema is up to date
3. Review configuration settings
4. Contact the development team with specific error details

---

*This integration guide ensures the Advanced Folders system is properly incorporated into RFU following established patterns and maintaining system stability.*