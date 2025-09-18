"""
Multi-Pane File Explorer - Main Window (FIXED VERSION)

This is the main window class that implements the enhanced Total Commander-style
interface with 1-4 configurable panes and full RFU tool integration.

FIXES APPLIED:
- Proper FileExplorerPane instantiation with PaneConfiguration
- Robust widget lifecycle management with null checks
- Fallback handling for missing import dependencies
- Memory management improvements
- Enhanced error handling for widget operations
"""

import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QSettings, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QComboBox,
                             QDialog, QDockWidget, QFrame, QHBoxLayout, QLabel,
                             QMainWindow, QMenu, QMenuBar, QMessageBox,
                             QPushButton, QShortcut, QSplitter, QStatusBar,
                             QTabWidget, QToolBar, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)

# Import RFU components with comprehensive feature set
try:
    from scripts.maintenance.standalone_database_manager import \
        get_database_manager
    from src.config_manager import get_config_manager
    from src.file_explorer.core.enhanced_config_manager import \
        get_enhanced_config_manager
    from src.file_explorer.enhanced_file_browser import EnhancedFileBrowser
    from src.file_explorer.features.bookmark_manager import (
        BookmarkManager, BookmarkType)
    from src.file_explorer.integration.advanced_tool_launcher import (
        AdvancedToolLauncher, LaunchConfiguration)
    from src.file_explorer.integration.keyboard_shortcuts_system import \
        KeyboardShortcutManager
    from src.file_explorer.ui.custom_widgets import (EnhancedStatusBar,
                                                         EnhancedToolbar,
                                                         FilePropertyPanel,
                                                         QuickPreviewWidget,
                                                         SearchWidget,
                                                         ThemeColors)
    from src.file_explorer.ui.file_explorer_pane import (FileExplorerPane,
                                                             FileListWidget,
                                                             NavigationBar,
                                                             SortCriteria,
                                                             ViewMode)
    from src.file_explorer.ui.pane_manager import (PaneConfiguration,
                                                       PaneType)
    from src.file_explorer.ui.widget_lifecycle_manager import (
        get_widget_lifecycle_manager, is_widget_valid, register_widget,
        safe_destroy_widget, safe_widget_operation)
    from src.log_manager import get_log_manager
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    # Fallback imports for development
    print(f"Import warning: {e}")
    IMPORTS_SUCCESSFUL = False
    get_database_manager = None
    get_config_manager = None
    get_log_manager = None
    get_widget_lifecycle_manager = None
    register_widget = lambda *args: ""
    safe_destroy_widget = lambda *args: True
    is_widget_valid = lambda *args: True
    safe_widget_operation = lambda *args: True
    get_enhanced_config_manager = None
    EnhancedFileBrowser = None
    EnhancedToolbar = None
    EnhancedStatusBar = None
    FilePropertyPanel = None
    QuickPreviewWidget = None
    SearchWidget = None
    BookmarkManager = None
    AdvancedToolLauncher = None
    KeyboardShortcutManager = None
    
    # Enhanced fallback classes for file explorer pane
    class FileExplorerPane(QWidget):
        def __init__(self, config, parent=None):
            super().__init__(parent)
            self.config = config
            self.current_path = str(Path.home())
            
            # Create a complete file explorer interface
            layout = QVBoxLayout(self)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(5)
            
            # Title bar
            title_label = QLabel(f"File Explorer - {getattr(config, 'title', 'Unknown')}")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-weight: bold; 
                    font-size: 14px; 
                    padding: 8px;
                    background-color: #007ACC;
                    color: white;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(title_label)
            
            # Navigation bar
            nav_frame = QFrame()
            nav_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 3px;")
            nav_layout = QHBoxLayout(nav_frame)
            nav_layout.addWidget(QLabel(f"Path: {self.current_path}"))
            layout.addWidget(nav_frame)
            
            # File list
            self.file_list = QTreeWidget()
            self.file_list.setHeaderLabels(["Name", "Size", "Type", "Modified"])
            self.file_list.setAlternatingRowColors(True)
            layout.addWidget(self.file_list, 1)
            
            # Status bar
            status_label = QLabel("Ready")
            status_label.setStyleSheet("font-size: 10px; color: #666; padding: 3px;")
            layout.addWidget(status_label)
            
            # Populate with initial content
            self._populate_file_list()
            
            # Store references
            self._current_path = Path.home()
            self._nav_widget = nav_frame
            self._file_list = self.file_list
        
        def _populate_file_list(self):
            """Populate file list with home directory contents."""
            try:
                self.file_list.clear()
                path = Path(self.current_path)
                
                for item in path.iterdir():
                    try:
                        stat = item.stat()
                        size_str = ""
                        if item.is_file():
                            size = stat.st_size
                            if size > 1024**3:
                                size_str = f"{size / (1024**3):.1f} GB"
                            elif size > 1024**2:
                                size_str = f"{size / (1024**2):.1f} MB"
                            elif size > 1024:
                                size_str = f"{size / 1024:.1f} KB"
                            else:
                                size_str = f"{size} B"
                        
                        type_str = "Directory" if item.is_dir() else "File"
                        modified_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        
                        tree_item = QTreeWidgetItem([
                            item.name,
                            size_str,
                            type_str,
                            modified_str
                        ])
                        
                        self.file_list.addTopLevelItem(tree_item)
                        
                    except (OSError, PermissionError):
                        continue
                        
            except Exception as e:
                error_item = QTreeWidgetItem([f"Error loading directory: {e}", "", "", ""])
                self.file_list.addTopLevelItem(error_item)
        
        def set_path(self, path: str):
            """Set current path and update display."""
            self.current_path = path
            self._current_path = Path(path)
            self._populate_file_list()
    
    class PaneConfiguration:
        def __init__(self, pane_id, pane_type="file_explorer", title="File Explorer"):
            self.pane_id = pane_id
            self.pane_type = pane_type
            self.title = title
    
    class PaneType:
        FILE_EXPLORER = "file_explorer"
    
    class ViewMode:
        DETAILS = "details"


class MultiPaneFileExplorer(QMainWindow):
    """
    Main file explorer window with configurable multi-pane interface.
    
    Features:
    - 1-4 configurable file explorer panes
    - Cross-platform file operations
    - Integrated access to all RFU tools
    - Customizable layouts and color schemes
    - Bookmark and favorites management
    """
    
    # Signals
    pane_count_changed = pyqtSignal(int)
    active_pane_changed = pyqtSignal(int)
    file_operation_started = pyqtSignal(str, list)
    file_operation_completed = pyqtSignal(str, bool, str)
    
    def __init__(self):
        super().__init__()        
        
        # Initialize core systems
        self.config_manager = None
        self.db_manager = None
        self.setup_core_systems()
        
        # Explorer state
        self.panes: List['FileExplorerPane'] = []
        self.active_pane_index = 0
        self.pane_count = 2  # Default to dual-pane
        self.layout_mode = 'horizontal'
        
        # Responsive layout configuration
        self.available_layouts = {
            1: [],  # Single pane: no layout options
            2: ['horizontal', 'vertical'],  # Two panes: h/v only
            3: ['horizontal', 'vertical', 'grid'],  # Three+ panes: all
            4: ['horizontal', 'vertical', 'grid']
        }
        self.is_mobile_viewport = False
        self.screen_size = None
        # Default grid columns by pane count
        self.grid_columns = {2: 1, 3: 2, 4: 2}
        
        # UI components
        self.central_widget = None
        self.pane_splitter = None
        self.enhanced_toolbar = None
        self.enhanced_status_bar = None
        self.property_panel = None
        self.preview_widget = None
        self.search_widget = None
        self.tool_dock = None
        self.bookmark_dock = None
        
        # Advanced feature managers
        self.bookmark_manager = None
        self.tool_launcher = None
        self.shortcut_manager = None
        self.drag_drop_manager = None
        
        # Cross-pane coordination
        self.synchronized_navigation = False
        self.synchronized_selection = False
        self.cross_pane_operations = True
        
        # Recent files and paths
        self.recent_locations = []
        self.recent_files = []
        self.max_recent_items = 20
        
        # Setup UI
        self.setup_window()
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_docks()
        self.setup_simple_status_bar()
        self.setup_shortcuts()
        
        # Load configuration
        self.load_configuration()
        
        # Setup default layout
        self.setup_default_panes()
        
        self.logger.info("MultiPaneFileExplorer initialized successfully")
    
    def setup_core_systems(self):
        """Initialize core system components."""
        # Setup logging
        self.logger = logging.getLogger('RFU.FileExplorer')
        
        # Initialize configuration manager
        if get_config_manager:
            try:
                self.config_manager = get_config_manager()
            except Exception as e:
                self.logger.warning(f"ConfigManager not available: {e}")
        
        # Initialize database manager
        if get_database_manager:
            try:
                self.db_manager = get_database_manager()
            except Exception as e:
                self.logger.warning(f"Database manager not available: {e}")
    
    def setup_window(self):
        """Setup main window properties with responsive behavior."""
        self.setWindowTitle("RFU Multi-Pane File Explorer")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Set window icon if available
        icon_path = Path("assets/images/rfu_explorer.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def setup_ui(self):
        """Setup the enhanced user interface with all advanced features."""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Enhanced toolbar
        self.setup_enhanced_toolbar(main_layout)
        
        # Main content area with splitters
        self.setup_main_content_area(main_layout)
        
        # Enhanced status bar
        self.setup_enhanced_status_bar(main_layout)
    
    def setup_enhanced_toolbar(self, parent_layout):
        """Setup enhanced toolbar with comprehensive controls."""
        if not EnhancedToolbar:
            # Fallback to simple toolbar
            self.logger.info("EnhancedToolbar not available, using simple toolbar")
            self.create_simple_toolbar(parent_layout)
            return
        
        # Enhanced toolbar implementation would go here
        self.create_simple_toolbar(parent_layout)
    
    def setup_main_content_area(self, parent_layout):
        """Setup main content area with panes and side panels."""
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (bookmarks, properties)
        left_panel = self.create_left_panel()
        if left_panel:
            main_splitter.addWidget(left_panel)
        
        # Center area (file panes) - CRITICAL: Initialize properly with error handling
        try:
            self.pane_splitter = QSplitter(Qt.Horizontal)
            self.logger.info("Successfully created QSplitter for panes")
        except Exception as e:
            self.logger.warning(f"Failed to create QSplitter, using QWidget fallback: {e}")
            # Create fallback container with layout
            self.pane_splitter = QWidget()
            self.pane_splitter_layout = QHBoxLayout(self.pane_splitter)
            self.pane_splitter_layout.setContentsMargins(0, 0, 0, 0)
            self.pane_splitter_layout.setSpacing(2)
        
        main_splitter.addWidget(self.pane_splitter)
        
        # Right panel (preview, tools)
        right_panel = self.create_right_panel()
        if right_panel:
            main_splitter.addWidget(right_panel)
        
        # Set splitter sizes (left: 200px, center: expand, right: 250px)
        if left_panel and right_panel:
            main_splitter.setSizes([200, 600, 250])
        elif left_panel:
            main_splitter.setSizes([200, 800])
        elif right_panel:
            main_splitter.setSizes([750, 250])
        
        parent_layout.addWidget(main_splitter, 1)  # Give it stretch factor
        
        self.logger.info("Main content area setup completed with robust pane_splitter")
    
    def create_left_panel(self):
        """Create left side panel with bookmarks and navigation."""
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(250)
        
        # Bookmarks tab
        self.bookmark_widget = self.create_simple_bookmark_widget()
        left_panel.addTab(self.bookmark_widget, "Bookmarks")
        
        # Recent locations tab
        self.recent_widget = self.create_recent_locations_widget()
        left_panel.addTab(self.recent_widget, "Recent")
        
        return left_panel
    
    def create_right_panel(self):
        """Create right side panel with preview and properties."""
        # Return None for now since enhanced widgets aren't available
        return None
    
    def create_simple_bookmark_widget(self):
        """Create simple bookmark widget fallback."""
        bookmark_tree = QTreeWidget()
        bookmark_tree.setHeaderLabels(["Bookmarks"])
        
        # Add default bookmarks
        default_bookmarks = [
            ("Home", str(Path.home())),
            ("Documents", str(Path.home() / "Documents")),
            ("Downloads", str(Path.home() / "Downloads")),
            ("Desktop", str(Path.home() / "Desktop"))
        ]
        
        for name, path in default_bookmarks:
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, path)
            bookmark_tree.addTopLevelItem(item)
        
        bookmark_tree.itemDoubleClicked.connect(self._on_simple_bookmark_activated)
        return bookmark_tree
    
    def create_recent_locations_widget(self):
        """Create recent locations widget."""
        recent_tree = QTreeWidget()
        recent_tree.setHeaderLabels(["Recent Locations"])
        
        # Add some default recent locations
        recent_locations = [str(Path.home()), str(Path.home() / "Documents")]
        for location in recent_locations:
            item = QTreeWidgetItem([Path(location).name])
            item.setData(0, Qt.UserRole, location)
            item.setToolTip(0, location)
            recent_tree.addTopLevelItem(item)
        
        recent_tree.itemDoubleClicked.connect(self._on_recent_location_activated)
        return recent_tree
    
    def setup_enhanced_status_bar(self, parent_layout):
        """Setup enhanced status bar with comprehensive information."""
        if EnhancedStatusBar:
            self.enhanced_status_bar = EnhancedStatusBar()
            self.enhanced_status_bar.set_main_message("Ready")
            parent_layout.addWidget(self.enhanced_status_bar)
        else:
            # Fallback to simple status bar
            self.setup_simple_status_bar()
    
    def create_simple_toolbar(self, parent_layout):
        """Create simple toolbar fallback."""
        toolbar_frame = QFrame()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Basic controls
        toolbar_layout.addWidget(QLabel("Panes:"))
        self.pane_count_combo = QComboBox()
        self.pane_count_combo.addItems(['1', '2', '3', '4'])
        self.pane_count_combo.setCurrentText(str(self.pane_count))
        self.pane_count_combo.currentTextChanged.connect(self.on_pane_count_changed)
        toolbar_layout.addWidget(self.pane_count_combo)
        
        toolbar_layout.addWidget(QLabel("Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(['Horizontal', 'Vertical', 'Grid'])
        self.layout_combo.setCurrentText(self.layout_mode.title())
        self.layout_combo.currentTextChanged.connect(self.on_layout_mode_changed)
        toolbar_layout.addWidget(self.layout_combo)
        
        toolbar_layout.addStretch()
        
        parent_layout.addWidget(toolbar_frame)
    
    def setup_simple_status_bar(self):
        """Setup simple status bar fallback."""
        status_bar = self.statusBar()
        self.file_count_label = QLabel("Ready")
        status_bar.addWidget(self.file_count_label)
        self.operation_label = QLabel("")
        status_bar.addPermanentWidget(self.operation_label)
    
    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_tab_action = QAction("&New Tab", self)
        new_tab_action.setShortcut(QKeySequence.New)
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_toolbars(self):
        """Setup application toolbars."""
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        
        # Navigation actions
        back_action = QAction("⬅", self)
        back_action.setToolTip("Go Back")
        back_action.triggered.connect(self.go_back)
        main_toolbar.addAction(back_action)
        
        forward_action = QAction("➡", self)
        forward_action.setToolTip("Go Forward")
        forward_action.triggered.connect(self.go_forward)
        main_toolbar.addAction(forward_action)
        
        up_action = QAction("⬆", self)
        up_action.setToolTip("Go Up")
        up_action.triggered.connect(self.go_up)
        main_toolbar.addAction(up_action)
        
        main_toolbar.addSeparator()
        
        # View actions
        refresh_action = QAction("🔄", self)
        refresh_action.setToolTip("Refresh")
        refresh_action.triggered.connect(self.refresh_current_pane)
        main_toolbar.addAction(refresh_action)
    
    def setup_docks(self):
        """Setup dock widgets for additional functionality."""
        # Skip dock setup for now to focus on core pane functionality
        pass
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcuts = {
            QKeySequence("Ctrl+1"): lambda: self.set_pane_count(1),
            QKeySequence("Ctrl+2"): lambda: self.set_pane_count(2),
            QKeySequence("Ctrl+3"): lambda: self.set_pane_count(3),
            QKeySequence("Ctrl+4"): lambda: self.set_pane_count(4),
            QKeySequence("F5"): self.refresh_current_pane,
            QKeySequence("F1"): self.show_help
        }
        
        for shortcut, callback in shortcuts.items():
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            self.addAction(action)
    
    def load_configuration(self):
        """Load user configuration and preferences with responsive support."""
        if self.config_manager:
            try:
                # Use get_section instead of get_setting with dict default
                config = self.config_manager.get_section('file_explorer') or {}
                
                # Load pane count and validate
                saved_pane_count = config.get('pane_count', 2)
                if 1 <= saved_pane_count <= 4:
                    self.pane_count = saved_pane_count
                
                # Load layout mode and validate against pane count
                saved_layout = config.get('layout_mode', 'horizontal')
                available = self.available_layouts.get(self.pane_count, [])
                
                if saved_layout in available:
                    self.layout_mode = saved_layout
                elif available:
                    self.layout_mode = available[0]
                
                self.logger.info(f"Configuration loaded: {self.pane_count} panes, {self.layout_mode} layout")
                
            except Exception as e:
                self.logger.warning(f"Error loading configuration: {e}")
    
    def setup_default_panes(self):
        """Setup the default pane configuration."""
        self.set_pane_count(self.pane_count)

    def set_pane_count(self, count: int):
        """Set the number of active panes with responsive layout validation."""
        if not 1 <= count <= 4:
            self.logger.warning(f"Invalid pane count: {count}")
            return
        
        old_count = len(self.panes)
        self.pane_count = count
        
        # Update combo box
        if hasattr(self, 'pane_count_combo') and self.pane_count_combo:
            self.pane_count_combo.setCurrentText(str(count))
        
        # Adjust panes
        if count > old_count:
            self._add_panes(count - old_count)
        elif count < old_count:
            self._remove_panes(old_count - count)
        
        # Update layout
        self._update_pane_layout()
        
        # Emit signal
        self.pane_count_changed.emit(count)
        
        self.logger.info(f"Pane count changed to {count}")
    
    def _add_panes(self, count: int):
        """Add new file explorer panes."""
        self.logger.info(f"Adding {count} panes. Current count: {len(self.panes)}")
        
        for i in range(count):
            try:
                # Try to create a proper FileExplorerPane first
                pane = self._create_file_explorer_pane(len(self.panes) + 1)
                self.logger.info(f"Created FileExplorerPane {len(self.panes) + 1}")
            except Exception as e:
                self.logger.warning(f"Failed to create FileExplorerPane: {e}")
                # Fall back to simple pane
                pane = self._create_simple_fallback_pane(len(self.panes) + 1)
                self.logger.info(f"Created fallback pane {len(self.panes) + 1}")
            
            self.panes.append(pane)
            
            # Connect pane signals
            try:
                self._connect_pane_signals(pane)
            except Exception as e:
                self.logger.warning(f"Failed to connect pane signals: {e}")
                
        # Update layout
        self._update_pane_layout()
    
    def _create_file_explorer_pane(self, pane_number: int) -> 'FileExplorerPane':
        """Create a proper FileExplorerPane instance."""
        try:
            # Create proper PaneConfiguration for FileExplorerPane
            config = PaneConfiguration(
                pane_id=f"pane_{pane_number}",
                pane_type=PaneType.FILE_EXPLORER,
                title=f"File Explorer {pane_number}"
            )
            
            # Create enhanced file explorer pane with proper configuration
            pane = FileExplorerPane(config, self)
            
            # Set initial directory to home
            home_path = str(Path.home())
            if hasattr(pane, 'navigate_to'):
                pane.navigate_to(home_path)
            elif hasattr(pane, 'set_path'):
                pane.set_path(home_path)
            
            # Register widget for lifecycle management
            if register_widget:
                register_widget(pane, f"file_explorer_pane_{pane_number}")
            
            return pane
        except Exception as e:
            self.logger.error(f"Failed to create FileExplorerPane: {e}")
            raise
    
    def _create_simple_fallback_pane(self, pane_number: int) -> QWidget:
        """Create a simple fallback pane when enhanced browser fails."""
        pane_widget = QFrame()
        pane_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #007ACC;
                background-color: #f8f9fa;
                margin: 2px;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout(pane_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title label with enhanced styling
        title_label = QLabel(f"File Explorer Pane {pane_number}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 14px; 
                padding: 8px;
                background-color: #007ACC;
                color: white;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title_label)
        
        # Add navigation bar
        nav_widget = self._create_navigation_bar(pane_widget)
        layout.addWidget(nav_widget)
        
        # Simple file list with enhanced styling
        file_list = QTreeWidget()
        file_list.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        file_list.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #ddd;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #007ACC;
                color: white;
            }
        """)
        
        # Store references for navigation
        pane_widget._current_path = Path.home()
        pane_widget._nav_widget = nav_widget
        pane_widget._file_list = file_list
        
        # Populate with home directory contents
        self._populate_file_list(file_list, Path.home())
        
        # Connect file list signals
        file_list.itemDoubleClicked.connect(
            lambda item: self._on_file_item_activated(pane_widget, item)
        )
        
        layout.addWidget(file_list, 1)
        
        # Status label with enhanced styling
        status_label = QLabel(f"Pane {pane_number} - Ready")
        status_label.setStyleSheet("""
            QLabel {
                font-size: 10px; 
                color: #666; 
                padding: 3px;
                background-color: #e9ecef;
                border-radius: 2px;
            }
        """)
        layout.addWidget(status_label)
        
        # Ensure the pane is visible
        pane_widget.show()
        
        self.logger.info(f"Created enhanced fallback pane {pane_number}")
        
        return pane_widget
    
    def _create_navigation_bar(self, parent_pane) -> QWidget:
        """Create navigation bar with path display."""
        nav_widget = QFrame()
        nav_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 3px;")
        
        layout = QHBoxLayout(nav_widget)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Path display
        path_label = QLabel("Path:")
        path_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(path_label)
        
        path_display = QLabel(str(Path.home()))
        path_display.setStyleSheet("""
            font-family: monospace; 
            background-color: white; 
            padding: 3px; 
            border: 1px solid #999;
        """)
        path_display.setMinimumWidth(200)
        layout.addWidget(path_display, 1)
        
        # Navigation buttons
        up_btn = QPushButton("↑")
        up_btn.setMaximumWidth(25)
        up_btn.setToolTip("Go up one directory")
        up_btn.clicked.connect(lambda: self._navigate_up(parent_pane))
        layout.addWidget(up_btn)
        
        refresh_btn = QPushButton("⟲")
        refresh_btn.setMaximumWidth(25)
        refresh_btn.setToolTip("Refresh current directory")
        refresh_btn.clicked.connect(lambda: self._refresh_pane(parent_pane))
        layout.addWidget(refresh_btn)
        
        # Store references for updating
        nav_widget._path_display = path_display
        parent_pane._nav_widget = nav_widget
        
        return nav_widget
    
    def _populate_file_list(self, file_list: QTreeWidget, path: Path):
        """Populate file list with directory contents."""
        try:
            file_list.clear()
            
            if not path.exists():
                error_item = QTreeWidgetItem(["Path does not exist", "", "", ""])
                file_list.addTopLevelItem(error_item)
                return
            
            if not path.is_dir():
                error_item = QTreeWidgetItem(["Not a directory", "", "", ""])
                file_list.addTopLevelItem(error_item)
                return
            
            # Add items
            items = []
            try:
                for item in path.iterdir():
                    try:
                        # Get item statistics
                        stat = item.stat()
                        size_str = ""
                        if item.is_file():
                            size = stat.st_size
                            if size > 1024**3:  # GB
                                size_str = f"{size / (1024**3):.1f} GB"
                            elif size > 1024**2:  #