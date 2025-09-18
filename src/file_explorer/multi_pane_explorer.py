"""
Multi-Pane File Explorer - Main Window

This is the main window class that implements the enhanced Total Commander-style
interface with 1-4 configurable panes and full RFU tool integration.
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
except ImportError:
    # Fallback imports for development
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
    
    # Fallback classes for file explorer pane
    class FileExplorerPane(QWidget):
        def __init__(self, config, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel(f"File Explorer Pane {getattr(config, 'pane_id', 'Unknown')}")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
    
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
        
        # Update layout combo options after loading configuration
        if hasattr(self, 'layout_combo') and self.layout_combo:
            self._update_layout_combo_options(self.layout_combo)
        
        # Setup default layout
        self.setup_default_panes()
        
        self.logger.info("MultiPaneFileExplorer initialized successfully")
    
    def resizeEvent(self, event):
        """Handle window resize for responsive behavior."""
        super().resizeEvent(event)
        
        # Re-detect viewport on resize
        old_mobile = self.is_mobile_viewport
        self._detect_viewport()
        
        # If viewport type changed, update layout
        if old_mobile != self.is_mobile_viewport:
            self.logger.info(
                f"Viewport changed: mobile={self.is_mobile_viewport}"
            )
            # Update layout combo options if needed
            if hasattr(self, 'layout_combo') and self.layout_combo:
                self._update_layout_combo_options(self.layout_combo)
            
            # Re-apply layout with new viewport constraints
            self._update_pane_layout()
    
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
    
    def _detect_viewport(self):
        """Detect viewport size and type for responsive behavior."""
        try:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    geometry = screen.geometry()
                    self.screen_size = (geometry.width(), geometry.height())
                    
                    # Consider mobile viewport if width < 1024px or height < 768px
                    self.is_mobile_viewport = (
                        geometry.width() < 1024 or 
                        geometry.height() < 768
                    )
                    
                    # Adjust grid columns based on screen width
                    if geometry.width() < 800:
                        self.grid_columns = {2: 1, 3: 1, 4: 2}
                    elif geometry.width() < 1200:
                        self.grid_columns = {2: 1, 3: 2, 4: 2}
                    else:
                        self.grid_columns = {2: 2, 3: 3, 4: 2}
                        
                    self.logger.info(
                        f"Viewport detected: {self.screen_size}, "
                        f"mobile: {self.is_mobile_viewport}"
                    )
                else:
                    # Fallback values
                    self.screen_size = (1920, 1080)
                    self.is_mobile_viewport = False
        except Exception as e:
            self.logger.warning(f"Could not detect viewport: {e}")
            self.screen_size = (1920, 1080)
            self.is_mobile_viewport = False
    
    def _update_layout_combo_options(self, layout_combo):
        """Update layout combo options based on current pane count."""
        current_text = layout_combo.currentText()
        layout_combo.clear()
        
        available = self.available_layouts.get(self.pane_count, [])
        
        if not available:
            # Single pane - no layout options
            layout_combo.addItem("Single View")
            layout_combo.setEnabled(False)
            layout_combo.setToolTip("Layout options disabled for single pane")
        else:
            layout_combo.setEnabled(True)
            layout_combo.setToolTip("Select layout arrangement")
            
            for layout in available:
                display_name = layout.title()
                layout_combo.addItem(display_name)
            
            # Restore previous selection if valid, otherwise use first option
            if current_text in [item.title() for item in available]:
                index = layout_combo.findText(current_text)
                if index >= 0:
                    layout_combo.setCurrentIndex(index)
            elif available:
                # Fallback to first available option
                self.layout_mode = available[0]
                layout_combo.setCurrentText(self.layout_mode.title())
    
    def _validate_and_update_layout(self):
        """Validate current layout mode and update if necessary."""
        available = self.available_layouts.get(self.pane_count, [])
        
        if self.layout_mode not in available:
            if available:
                old_mode = self.layout_mode
                self.layout_mode = available[0]
                self.logger.info(
                    f"Layout changed from {old_mode} to {self.layout_mode} "
                    f"due to pane count constraint"
                )
            else:
                self.layout_mode = 'single'
        
        # Update layout combo if it exists
        if hasattr(self, 'layout_combo') and self.layout_combo:
            self._update_layout_combo_options(self.layout_combo)
    
    def setup_window(self):
        """Setup main window properties with responsive behavior."""
        self.setWindowTitle("RFU Multi-Pane File Explorer")
        
        # Detect screen size and viewport type
        self._detect_viewport()
        
        # Set responsive window size
        if self.is_mobile_viewport:
            self.setMinimumSize(400, 300)
            self.resize(800, 600)
        else:
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
        
        # Search widget (initially hidden)
        self.setup_search_widget(main_layout)
        
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
        
        self.enhanced_toolbar = EnhancedToolbar()
        
        # Navigation actions
        self.enhanced_toolbar.add_action_button(
            "back", "Back", tooltip="Go Back (Alt+Left)"
        )
        self.enhanced_toolbar.add_action_button(
            "forward", "Forward", tooltip="Go Forward (Alt+Right)"
        )
        self.enhanced_toolbar.add_action_button(
            "up", "Up", tooltip="Go Up (Alt+Up)"
        )
        self.enhanced_toolbar.add_action_button(
            "refresh", "Refresh", tooltip="Refresh (F5)"
        )
        
        self.enhanced_toolbar.add_separator()
        
        # Pane configuration
        pane_combo = QComboBox()
        pane_combo.addItems(['1 Pane', '2 Panes', '3 Panes', '4 Panes'])
        pane_combo.setCurrentIndex(self.pane_count - 1)
        pane_combo.currentIndexChanged.connect(
            lambda idx: self.set_pane_count(idx + 1)
        )
        self.enhanced_toolbar.add_widget(pane_combo)
        
        # Layout mode with conditional options
        layout_combo = QComboBox()
        self._update_layout_combo_options(layout_combo)
        layout_combo.currentTextChanged.connect(self.on_layout_mode_changed)
        self.enhanced_toolbar.add_widget(layout_combo)
        
        self.enhanced_toolbar.add_separator()
        
        # View mode actions
        self.enhanced_toolbar.add_action_button(
            "view_list", "List", checkable=True, tooltip="List View"
        )
        self.enhanced_toolbar.add_action_button(
            "view_details", "Details", checkable=True, tooltip="Details View"
        )
        self.enhanced_toolbar.add_action_button(
            "view_grid", "Grid", checkable=True, tooltip="Grid View"
        )
        self.enhanced_toolbar.add_action_button(
            "view_tree", "Tree", checkable=True, tooltip="Tree View"
        )
        
        self.enhanced_toolbar.add_separator()
        
        # Search and tools
        self.enhanced_toolbar.add_action_button(
            "search", "Search", tooltip="Search Files (Ctrl+F)"
        )
        self.enhanced_toolbar.add_action_button(
            "bookmark", "Bookmark", tooltip="Bookmark Current Location"
        )
        
        self.enhanced_toolbar.add_spacer()
        
        # Quick tools
        self.enhanced_toolbar.add_action_button(
            "file_finder", "Find Files", tooltip="Launch File Finder"
        )
        self.enhanced_toolbar.add_action_button(
            "size_analyzer", "Analyze Size", tooltip="Launch Size Analyzer"
        )
        self.enhanced_toolbar.add_action_button(
            "duplicate_finder", "Find Duplicates", tooltip="Launch Duplicate Finder"
        )
        
        # Connect toolbar signals
        self.enhanced_toolbar.actionTriggered.connect(self.on_toolbar_action)
        
        parent_layout.addWidget(self.enhanced_toolbar)
        
        # Store references for combo boxes
        self.pane_count_combo = pane_combo
        self.layout_combo = layout_combo
    
    def setup_search_widget(self, parent_layout):
        """Setup search widget (initially hidden)."""
        if SearchWidget:
            self.search_widget = SearchWidget()
            self.search_widget.searchRequested.connect(self.perform_search)
            self.search_widget.searchClosed.connect(self.close_search)
            parent_layout.addWidget(self.search_widget)
        else:
            self.search_widget = None
    
    def setup_main_content_area(self, parent_layout):
        """Setup main content area with panes and side panels."""
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (bookmarks, properties)
        left_panel = self.create_left_panel()
        if left_panel:
            main_splitter.addWidget(left_panel)
        
        # Center area (file panes) - Create QSplitter for panes
        self.pane_splitter = QSplitter(Qt.Horizontal)
        self.is_fallback_splitter = False
        
        # Verify splitter was created properly
        if self.pane_splitter:
            self.logger.info(f"Created pane_splitter: {type(self.pane_splitter).__name__}")
            main_splitter.addWidget(self.pane_splitter)
        else:
            self.logger.error("CRITICAL: pane_splitter creation failed!")
        
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
        
        # Final verification before leaving setup
        if self.pane_splitter:
            splitter_type = type(self.pane_splitter).__name__
            self.logger.info(f"Main content area setup completed - pane_splitter: {splitter_type}")
        else:
            self.logger.error("CRITICAL: pane_splitter is None at end of setup!")
    
    def create_left_panel(self):
        """Create left side panel with bookmarks and navigation."""
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(250)
        
        # Bookmarks tab
        self.bookmark_widget = self.create_enhanced_bookmark_widget()
        left_panel.addTab(self.bookmark_widget, "Bookmarks")
        
        # Recent locations tab
        self.recent_widget = self.create_recent_locations_widget()
        left_panel.addTab(self.recent_widget, "Recent")
        
        # Tools tab
        self.tools_widget = self.create_enhanced_tools_widget()
        left_panel.addTab(self.tools_widget, "Tools")
        
        return left_panel
    
    def create_right_panel(self):
        """Create right side panel with preview and properties."""
        right_panel = QTabWidget()
        right_panel.setMaximumWidth(300)
        
        # File preview tab
        if QuickPreviewWidget:
            self.preview_widget = QuickPreviewWidget()
            right_panel.addTab(self.preview_widget, "Preview")
        
        # File properties tab
        if FilePropertyPanel:
            self.property_panel = FilePropertyPanel()
            right_panel.addTab(self.property_panel, "Properties")
        
        # Return None if no widgets were created
        if right_panel.count() == 0:
            return None
        
        return right_panel
    
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
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Pane configuration submenu
        pane_menu = view_menu.addMenu("&Panes")
        
        pane_group = QActionGroup(self)
        for i in range(1, 5):
            action = QAction(f"{i} Pane{'s' if i > 1 else ''}", self)
            action.setCheckable(True)
            action.setData(i)
            action.triggered.connect(lambda checked, count=i: self.set_pane_count(count))
            if i == self.pane_count:
                action.setChecked(True)
            pane_group.addAction(action)
            pane_menu.addAction(action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        self.populate_tools_menu(tools_menu)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def populate_tools_menu(self, menu):
        """Populate the tools menu with RFU tools."""
        tool_categories = {
            "File Management": [
                ("File Finder", self.launch_file_finder),
                ("Catalog Files", self.launch_catalog),
                ("Organize Files", self.launch_organize)
            ],
            "Analysis": [
                ("Size Analyzer", self.launch_size_analyzer),
                ("Duplicate Finder", self.launch_duplicate_finder),
                ("File Checksum", self.launch_checksum)
            ],
            "Security": [
                ("Encrypt/Decrypt", self.launch_encrypt_decrypt),
                ("Secure Delete", self.launch_secure_delete),
                ("Permissions Editor", self.launch_permissions)
            ]
        }
        
        for category, tools in tool_categories.items():
            submenu = menu.addMenu(category)
            for tool_name, callback in tools:
                action = QAction(tool_name, self)
                action.triggered.connect(callback)
                submenu.addAction(action)
    
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
        try:
            # Tool dock only - bookmarks are already in left panel
            self.tool_dock = QDockWidget("Tools", self)
            self.tool_dock.setFeatures(QDockWidget.DockWidgetMovable |
                                     QDockWidget.DockWidgetClosable)
            tool_widget = self._create_tool_widget()
            self.tool_dock.setWidget(tool_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.tool_dock)
            
            # Keep tool dock visible by default
            self.tool_dock.show()
            
        except Exception as e:
            self.logger.error(f"Error setting up docks: {e}")
    
    def create_recent_locations_widget(self):
        """Create recent locations widget."""
        recent_tree = QTreeWidget()
        recent_tree.setHeaderLabels(["Recent Locations"])
        
        # Populate with recent locations
        for location in self.recent_locations[-10:]:  # Show last 10
            item = QTreeWidgetItem([Path(location).name])
            item.setData(0, Qt.UserRole, location)
            item.setToolTip(0, location)
            recent_tree.addTopLevelItem(item)
        
        recent_tree.itemDoubleClicked.connect(self._on_recent_location_activated)
        return recent_tree
    
    def create_enhanced_tools_widget(self):
        """Create enhanced tools widget with categorized tool access."""
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["RFU Tools"])
        
        # Categorized tools
        tool_categories = {
            "File Management": [
                ("File Finder", "🔍", self.launch_file_finder),
                ("Catalog Files", "📁", self.launch_catalog),
                ("Organize Files", "📂", self.launch_organize),
                ("Copy/Move/Sync", "📋", self.launch_copy_move_sync)
            ],
            "Analysis": [
                ("Size Analyzer", "📊", self.launch_size_analyzer),
                ("Duplicate Finder", "🔍", self.launch_duplicate_finder),
                ("File Checksum", "🛡️", self.launch_checksum),
                ("Disk Usage", "💾", self.launch_disk_usage)
            ],
            "Security": [
                ("Encrypt/Decrypt", "🔒", self.launch_encrypt_decrypt),
                ("Secure Delete", "🗑️", self.launch_secure_delete),
                ("Permissions Editor", "🔐", self.launch_permissions),
                ("File Integrity", "✅", self.launch_file_integrity)
            ],
            "PDF Tools": [
                ("PDF Utilities", "📄", self.launch_pdf_utilities),
                ("Extract Links", "🔗", self.launch_extract_links),
                ("Page Administration", "📋", self.launch_page_admin),
                ("PDF Conversion", "🔄", self.launch_pdf_conversion)
            ],
            "Network": [
                ("Network Connectivity", "🌐", self.launch_network_test),
                ("File Transfer", "📡", self.launch_file_transfer),
                ("Remote Access", "🖥️", self.launch_remote_access)
            ]
        }
        
        for category, tools in tool_categories.items():
            category_item = QTreeWidgetItem([category])
            category_item.setExpanded(True)
            
            for tool_name, icon, callback in tools:
                tool_item = QTreeWidgetItem([f"{icon} {tool_name}"])
                tool_item.setData(0, Qt.UserRole, callback)
                category_item.addChild(tool_item)
            
            tools_tree.addTopLevelItem(category_item)
        
        tools_tree.itemDoubleClicked.connect(self._on_tool_activated)
        return tools_tree
    
    def create_enhanced_bookmark_widget(self):
        """Create enhanced bookmark widget with advanced features."""
        if BookmarkManager:
            try:
                # Initialize bookmark manager
                self.bookmark_manager = BookmarkManager()
                
                # Create bookmark tree widget
                bookmark_tree = QTreeWidget()
                bookmark_tree.setHeaderLabels(["Bookmarks"])
                bookmark_tree.setContextMenuPolicy(Qt.CustomContextMenu)
                
                # Load bookmarks into tree
                self._populate_bookmark_tree(bookmark_tree)
                
                # Connect signals
                bookmark_tree.itemDoubleClicked.connect(self._on_bookmark_activated)
                bookmark_tree.customContextMenuRequested.connect(self._show_bookmark_context_menu)
                
                return bookmark_tree
                
            except Exception as e:
                self.logger.error(f"Error creating enhanced bookmark widget: {e}")
        
        # Fallback to simple bookmark widget
        return self.create_simple_bookmark_widget()
    
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
        self._update_layout_combo_options(self.layout_combo)
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
    
    def on_toolbar_action(self, action_id: str):
        """Handle enhanced toolbar actions."""
        try:
            if action_id == "back":
                self.go_back()
            elif action_id == "forward":
                self.go_forward()
            elif action_id == "up":
                self.go_up()
            elif action_id == "refresh":
                self.refresh_current_pane()
            elif action_id == "search":
                self.show_search()
            elif action_id == "bookmark":
                self.bookmark_current_location()
            elif action_id.startswith("view_"):
                view_mode = action_id.replace("view_", "")
                self.set_view_mode_all_panes(view_mode)
            elif action_id == "file_finder":
                self.launch_file_finder()
            elif action_id == "size_analyzer":
                self.launch_size_analyzer()
            elif action_id == "duplicate_finder":
                self.launch_duplicate_finder()
            
            self.logger.debug(f"Toolbar action executed: {action_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing toolbar action {action_id}: {e}")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcuts = {
            QKeySequence("Ctrl+1"): lambda: self.set_pane_count(1),
            QKeySequence("Ctrl+2"): lambda: self.set_pane_count(2),
            QKeySequence("Ctrl+3"): lambda: self.set_pane_count(3),
            QKeySequence("Ctrl+4"): lambda: self.set_pane_count(4),
            QKeySequence("F5"): self.refresh_current_pane,
            QKeySequence("Ctrl+F"): self.launch_file_finder,
            QKeySequence("Ctrl+D"): self.launch_duplicate_finder,
            QKeySequence("F1"): self.show_help
        }
        
        for shortcut, callback in shortcuts.items():
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            self.addAction(action)
    
    def _create_tool_widget(self):
        """Create tool widget for tool dock."""
        try:
            # Simple tool widget with common tools
            from PyQt5.QtWidgets import QListWidget, QListWidgetItem
            
            tool_widget = QListWidget()
            
            # Add common tools
            tools = [
                "Find Files",
                "Disk Usage",
                "File Copy/Move",
                "Duplicate Finder",
                "Permission Editor",
                "File Integrity Check"
            ]
            
            for tool in tools:
                item = QListWidgetItem(tool)
                tool_widget.addItem(item)
            
            # Connect tool activation
            tool_widget.itemDoubleClicked.connect(self._launch_selected_tool)
            
            return tool_widget
            
        except Exception as e:
            self.logger.error(f"Error creating tool widget: {e}")
            # Fallback to simple label
            return QLabel("Tools")
    
    def _launch_selected_tool(self, item):
        """Launch the selected tool."""
        try:
            tool_name = item.text()
            
            # Map tool names to launcher methods
            tool_map = {
                "Find Files": self.launch_file_finder,
                "Disk Usage": self.launch_disk_usage,
                "File Copy/Move": self.launch_copy_move_sync,
                "Duplicate Finder": self.launch_duplicate_finder,
                "Permission Editor": self.launch_permissions_editor,
                "File Integrity Check": self.launch_file_integrity,
            }
            
            if tool_name in tool_map:
                tool_map[tool_name]()
            else:
                self.statusBar().showMessage(f"Tool not implemented: {tool_name}", 3000)
                
        except Exception as e:
            self.logger.error(f"Error launching tool: {e}")
    
    def load_configuration(self):
        """Load user configuration and preferences with responsive support."""
        if self.config_manager:
            try:
                # Load basic configuration - use get_section for dict access
                try:
                    config = self.config_manager.get_section('file_explorer') or {}
                except:
                    config = {}
                
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
                    self.logger.info(
                        f"Layout {saved_layout} not available for "
                        f"{self.pane_count} panes, using {self.layout_mode}"
                    )
                
                # Load responsive settings
                responsive_config = config.get('responsive', {})
                if 'grid_columns' in responsive_config:
                    self.grid_columns.update(responsive_config['grid_columns'])
                
                self.logger.info(
                    f"Configuration loaded: {self.pane_count} panes, "
                    f"{self.layout_mode} layout"
                )
                
            except Exception as e:
                self.logger.warning(f"Error loading configuration: {e}")
    
    def setup_default_panes(self):
        """Setup the default pane configuration."""
        self.set_pane_count(self.pane_count)

    def set_pane_count(self, count: int):
        """Set the number of active panes with responsive layout validation."""
        if not 1 <= count <= 4:
            return
        
        old_count = len(self.panes)
        self.pane_count = count
        
        # Update combo box
        if hasattr(self, 'pane_count_combo') and self.pane_count_combo:
            self.pane_count_combo.setCurrentText(str(count))
        
        # Validate and update layout constraints
        self._validate_and_update_layout()
        
        # Update layout combo options
        if hasattr(self, 'layout_combo') and self.layout_combo:
            self._update_layout_combo_options(self.layout_combo)
        
        # Adjust panes
        if count > old_count:
            self._add_panes(count - old_count)
        elif count < old_count:
            self._remove_panes(old_count - count)
        
        # Update layout
        self._update_pane_layout()
        
        # Emit signal
        self.pane_count_changed.emit(count)
        
        # Save configuration
        self.save_configuration()
        
        self.logger.info(f"Pane count changed to {count}")
    
    def _add_panes(self, count: int):
        """Add new file explorer panes."""
        self.logger.info(f"Adding {count} panes. Current pane count: {len(self.panes)}")
        
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
        
        self.logger.info(f"Created enhanced fallback pane {pane_number} with visible styling")
        
        return pane_widget
    
    def _create_navigation_bar(self, parent_pane) -> QWidget:
        """Create navigation bar with drive selection dropdown and path display."""
        nav_widget = QFrame()
        nav_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 3px;")
        
        layout = QHBoxLayout(nav_widget)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Drive selection dropdown
        drive_label = QLabel("Drive:")
        drive_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(drive_label)
        
        drive_combo = QComboBox()
        drive_combo.setMinimumWidth(80)
        drive_combo.setToolTip("Select drive to browse")
        
        # Populate available drives
        drives = self._get_available_drives()
        for drive in drives:
            drive_combo.addItem(drive['label'], drive['path'])
        
        # Set current drive based on home directory
        current_drive = self._get_drive_from_path(Path.home())
        index = drive_combo.findData(current_drive)
        if index >= 0:
            drive_combo.setCurrentIndex(index)
        
        drive_combo.currentTextChanged.connect(
            lambda: self._on_drive_changed(parent_pane, drive_combo)
        )
        layout.addWidget(drive_combo)
        
        # Path display
        path_label = QLabel("Path:")
        path_label.setStyleSheet("font-weight: bold; margin-left: 10px;")
        layout.addWidget(path_label)
        
        path_display = QLabel(str(Path.home()))
        path_display.setStyleSheet("font-family: monospace; background-color: white; padding: 3px; border: 1px solid #999;")
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
        nav_widget._drive_combo = drive_combo
        nav_widget._path_display = path_display
        parent_pane._nav_widget = nav_widget
        
        return nav_widget
    
    def _create_enhanced_file_list(self, parent_pane) -> QTreeWidget:
        """Create enhanced file list with navigation support."""
        file_list = QTreeWidget()
        file_list.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        file_list.setAlternatingRowColors(True)
        file_list.setSortingEnabled(True)
        
        # Configure column widths
        file_list.setColumnWidth(0, 200)  # Name
        file_list.setColumnWidth(1, 80)   # Size
        file_list.setColumnWidth(2, 80)   # Type
        file_list.setColumnWidth(3, 120)  # Modified
        
        # Connect double-click for navigation
        file_list.itemDoubleClicked.connect(
            lambda item: self._on_file_item_activated(parent_pane, item)
        )
        
        # Populate with initial directory
        self._populate_file_list(file_list, Path.home())
        
        return file_list
    
    def _get_available_drives(self) -> List[Dict[str, str]]:
        """Get list of available drives on the system."""
        drives = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows drive detection
                import string
                for letter in string.ascii_uppercase:
                    drive_path = f"{letter}:\\"
                    if os.path.exists(drive_path):
                        try:
                            # Get drive type and label
                            free_space = ""
                            try:
                                stat = os.statvfs(drive_path) if hasattr(os, 'statvfs') else None
                                if stat:
                                    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                                    free_space = f" ({free_gb:.1f} GB free)"
                            except:
                                pass
                            
                            drives.append({
                                'label': f"{letter}: Drive{free_space}",
                                'path': drive_path
                            })
                        except:
                            continue
            else:
                # Unix-like systems (Linux, macOS)
                # Add root filesystem
                drives.append({'label': "/ (Root)", 'path': "/"})
                
                # Add common mount points
                mount_points = ["/home", "/media", "/mnt", "/Volumes"]
                for mount_point in mount_points:
                    if os.path.exists(mount_point) and os.path.ismount(mount_point):
                        drives.append({
                            'label': f"{mount_point}",
                            'path': mount_point
                        })
                
                # Parse /proc/mounts for additional mount points
                try:
                    with open('/proc/mounts', 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                mount_point = parts[1]
                                if (mount_point.startswith('/media/') or 
                                    mount_point.startswith('/mnt/') or
                                    mount_point.startswith('/Volumes/')):
                                    if mount_point not in [d['path'] for d in drives]:
                                        drives.append({
                                            'label': os.path.basename(mount_point) or mount_point,
                                            'path': mount_point
                                        })
                except (OSError, IOError):
                    pass
        
        except Exception as e:
            self.logger.warning(f"Error detecting drives: {e}")
            # Fallback to home directory
            drives = [{'label': "Home", 'path': str(Path.home())}]
        
        # Always ensure home directory is available
        home_path = str(Path.home())
        if not any(d['path'] == home_path for d in drives):
            drives.insert(0, {'label': "Home", 'path': home_path})
        
        return drives
    
    def _get_drive_from_path(self, path: Path) -> str:
        """Extract drive/mount point from a given path."""
        try:
            if platform.system() == "Windows":
                return str(path.anchor)  # Returns "C:\\" etc.
            else:
                # For Unix-like systems, find the mount point
                path_str = str(path.resolve())
                drives = self._get_available_drives()
                
                # Find the longest matching mount point
                best_match = "/"
                for drive in drives:
                    if path_str.startswith(drive['path']) and len(drive['path']) > len(best_match):
                        best_match = drive['path']
                return best_match
        except Exception as e:
            self.logger.warning(f"Error getting drive from path: {e}")
            return str(Path.home())
    
    def _on_drive_changed(self, pane_widget, drive_combo):
        """Handle drive selection change."""
        try:
            selected_path = drive_combo.currentData()
            if selected_path:
                new_path = Path(selected_path)
                self._navigate_to_path(pane_widget, new_path)
        except Exception as e:
            self.logger.error(f"Error changing drive: {e}")
    
    def _navigate_to_path(self, pane_widget, path: Path):
        """Navigate pane to specified path."""
        try:
            if path.exists():
                pane_widget._current_path = path
                
                # Update path display
                if hasattr(pane_widget, '_nav_widget'):
                    pane_widget._nav_widget._path_display.setText(str(path))
                
                # Update file list
                if hasattr(pane_widget, '_file_list'):
                    self._populate_file_list(pane_widget._file_list, path)
                
                self.statusBar().showMessage(f"Navigated to: {path}", 2000)
            else:
                QMessageBox.warning(self, "Navigation Error", f"Path does not exist: {path}")
        except Exception as e:
            self.logger.error(f"Error navigating to path: {e}")
            QMessageBox.warning(self, "Navigation Error", f"Error navigating to {path}: {e}")
    
    def _navigate_up(self, pane_widget):
        """Navigate up one directory level."""
        try:
            current_path = getattr(pane_widget, '_current_path', Path.home())
            parent_path = current_path.parent
            
            if parent_path != current_path:  # Not at root
                self._navigate_to_path(pane_widget, parent_path)
            else:
                self.statusBar().showMessage("Already at root directory", 2000)
        except Exception as e:
            self.logger.error(f"Error navigating up: {e}")
    
    def _refresh_pane(self, pane_widget):
        """Refresh the current pane."""
        try:
            current_path = getattr(pane_widget, '_current_path', Path.home())
            self._navigate_to_path(pane_widget, current_path)
        except Exception as e:
            self.logger.error(f"Error refreshing pane: {e}")
    
    def _on_file_item_activated(self, pane_widget, item):
        """Handle file/directory activation in file list."""
        try:
            if item and item.parent() is None:  # Top-level item
                file_name = item.text(0)
                current_path = getattr(pane_widget, '_current_path', Path.home())
                file_path = current_path / file_name
                
                if file_path.is_dir():
                    # Navigate into directory
                    self._navigate_to_path(pane_widget, file_path)
                elif file_path.is_file():
                    # Open file with default application
                    self._handle_file_activation(str(file_path))
        except Exception as e:
            self.logger.error(f"Error activating file item: {e}")
    
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
                            elif size > 1024**2:  # MB
                                size_str = f"{size / (1024**2):.1f} MB"
                            elif size > 1024:  # KB
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
                        
                        # Set icon or styling for directories
                        if item.is_dir():
                            tree_item.setBackground(0, Qt.GlobalColor.lightGray)
                        
                        items.append((item.is_dir(), item.name.lower(), tree_item))
                        
                    except (OSError, PermissionError) as e:
                        # Handle files we can't access
                        error_item = QTreeWidgetItem([
                            item.name,
                            "",
                            "Access Denied",
                            f"Error: {e}"
                        ])
                        items.append((False, item.name.lower(), error_item))
                
                # Sort items: directories first, then by name
                items.sort(key=lambda x: (not x[0], x[1]))
                
                # Add to tree widget
                for _, _, tree_item in items:
                    file_list.addTopLevelItem(tree_item)
                    
            except PermissionError:
                error_item = QTreeWidgetItem(["Permission denied", "", "", ""])
                file_list.addTopLevelItem(error_item)
            except Exception as e:
                error_item = QTreeWidgetItem([f"Error: {e}", "", "", ""])
                file_list.addTopLevelItem(error_item)
                
        except Exception as e:
            self.logger.error(f"Error populating file list: {e}")
            error_item = QTreeWidgetItem([f"Failed to load: {e}", "", "", ""])
            file_list.clear()
            file_list.addTopLevelItem(error_item)
    
    def _connect_pane_signals(self, pane):
        """Connect signals from a pane to the main window."""
        try:
            # Connect path change signals
            if hasattr(pane, 'currentPathChanged'):
                pane.currentPathChanged.connect(
                    lambda path: self.statusBar().showMessage(f"Path: {path}", 2000)
                )
            
            # Connect file selection signals
            if hasattr(pane, 'fileSelected'):
                pane.fileSelected.connect(
                    lambda path: self.statusBar().showMessage(f"Selected: {Path(path).name}", 3000)
                )
            
            # Connect file activation signals
            if hasattr(pane, 'fileActivated'):
                pane.fileActivated.connect(self._handle_file_activation)
                
        except Exception as e:
            self.logger.warning(f"Error connecting pane signals: {e}")
    
    def _handle_file_activation(self, file_path: str):
        """Handle file activation from panes."""
        try:
            path_obj = Path(file_path)
            
            if path_obj.is_file():
                # Try to open file with default application
                import platform
                import subprocess
                
                system = platform.system()
                if system == "Windows":
                    os.startfile(file_path)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
                
                self.statusBar().showMessage(f"Opened: {path_obj.name}", 3000)
                
        except Exception as e:
            self.logger.warning(f"Could not open file {file_path}: {e}")
            QMessageBox.warning(
                self,
                "File Open Error",
                f"Could not open file:\n{file_path}\n\nError: {e}"
            )
    
    def _remove_panes(self, count: int):
        """Remove excess panes with enhanced widget lifecycle management."""
        WIDGET_DELETED_ERROR = "wrapped C/C++ object"
        
        for _ in range(count):
            if self.panes:
                pane = self.panes.pop()
                
                # Check if pane widget is still valid before operations
                pane_id = getattr(pane, '_lifecycle_id', None)
                
                if pane_id and is_widget_valid(pane_id):
                    # Use safe widget operation to set parent
                    def safe_set_parent(widget):
                        try:
                            widget.setParent(None)
                            return True
                        except RuntimeError as e:
                            if WIDGET_DELETED_ERROR in str(e):
                                return False
                            raise
                    
                    success = safe_widget_operation(pane_id, safe_set_parent)
                    if not success:
                        self.logger.warning("Failed to safely remove pane")
                    
                    # Destroy the widget through lifecycle manager
                    safe_destroy_widget(pane_id)
                else:
                    # Fallback for widgets not managed by lifecycle manager
                    try:
                        pane.setParent(None)
                        pane.deleteLater()
                    except RuntimeError as e:
                        if WIDGET_DELETED_ERROR in str(e):
                            self.logger.warning(f"Widget already deleted: {e}")
                        else:
                            raise
    
    def _create_single_layout(self):
        """Create single pane layout."""
        if not self.pane_splitter:
            self.logger.error("Cannot create layout: pane_splitter is None")
            return
            
        # Handle QSplitter
        if hasattr(self.pane_splitter, 'setOrientation'):
            self.pane_splitter.setOrientation(Qt.Horizontal)
            
            # Clear existing widgets from splitter
            if hasattr(self.pane_splitter, 'count'):
                for i in reversed(range(self.pane_splitter.count())):
                    widget = self.pane_splitter.widget(i)
                    if widget:
                        widget.setParent(None)
        
        # Handle QWidget with layout
        elif hasattr(self.pane_splitter, 'layout'):
            layout = self.pane_splitter.layout()
            if layout:
                # Clear existing widgets from layout
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
        
        # Add single pane if available
        if self.panes:
            self._safe_add_widget_to_splitter_with_target(
                self.pane_splitter, self.panes[0]
            )
    
    def _apply_mobile_layout_adjustments(self):
        """Apply mobile-specific layout adjustments."""
        if not self.is_mobile_viewport:
            return
        
        try:
            # Force vertical layout for mobile with > 2 panes
            if self.pane_count > 2 and self.layout_mode == 'horizontal':
                self.layout_mode = 'vertical'
                self._create_vertical_layout()
            
            # Adjust splitter sizes for mobile viewing
            if self.pane_splitter.count() > 1:
                total = self.pane_splitter.count()
                # Make first pane larger on mobile
                sizes = [60] + [40 // (total - 1)] * (total - 1)
                self.pane_splitter.setSizes(sizes)
        
        except Exception as e:
            self.logger.warning(f"Mobile layout adjustment failed: {e}")
    
    def _update_pane_layout(self):
        """Update the layout of panes based on current responsive configuration."""
        WIDGET_DELETED_ERROR = "wrapped C/C++ object"
        
        self.logger.info(f"_update_pane_layout called with {len(self.panes)} panes, "
                        f"layout_mode: {self.layout_mode}")
        
        try:
            if not self.pane_splitter:
                self.logger.error("Cannot update layout: pane_splitter is None")
                return
                
            if len(self.panes) == 0:
                self.logger.warning("Cannot update layout: no panes available")
                return
            
            # Validate panes before applying layout
            valid_panes = []
            for pane in self.panes:
                try:
                    _ = pane.isVisible()  # Test if widget is valid
                    valid_panes.append(pane)
                except RuntimeError as e:
                    if WIDGET_DELETED_ERROR in str(e):
                        self.logger.warning(f"Skipping deleted pane: {e}")
                        continue
                    raise
            
            self.panes = valid_panes
            
            # Apply responsive layout based on mode and constraints
            self.logger.info(f"Applying layout: {self.layout_mode} for {self.pane_count} panes")
            
            if self.pane_count == 1 or self.layout_mode == 'single':
                self.logger.info("Creating single pane layout")
                self._create_single_layout()
            elif self.layout_mode == 'horizontal':
                self.logger.info("Creating horizontal layout")
                self._create_horizontal_layout()
            elif self.layout_mode == 'vertical':
                self.logger.info("Creating vertical layout")
                self._create_vertical_layout()
            elif self.layout_mode == 'grid' and self.pane_count >= 3:
                self.logger.info("Creating grid layout")
                self._create_grid_layout()
            else:
                # Fallback to horizontal for invalid combinations
                self.logger.info("Using fallback horizontal layout")
                self.layout_mode = 'horizontal'
                self._create_horizontal_layout()
            
            # Apply mobile-specific adjustments
            if self.is_mobile_viewport:
                self._apply_mobile_layout_adjustments()
                
        except Exception as e:
            self.logger.error(f"Error updating pane layout: {e}")
            # Fallback to simple horizontal layout
            try:
                self._create_horizontal_layout()
            except Exception as fallback_error:
                self.logger.error(f"Fallback layout failed: {fallback_error}")
            
            # Set equal sizes if we have valid panes
            if self.panes:
                sizes = [100] * len(self.panes)
                self.pane_splitter.setSizes(sizes)
                
        except Exception as e:
            self.logger.error(f"Error during pane layout update: {e}")
    
    def _safe_add_widget_to_splitter(self, widget):
        """Safely add widget to splitter with validation."""
        WIDGET_DELETED_ERROR = "wrapped C/C++ object"
        
        try:
            if not self.pane_splitter:
                self.logger.error("Cannot add widget: pane_splitter is None")
                return
                
            # Test widget validity before adding
            _ = widget.isVisible()
            
            if hasattr(self.pane_splitter, 'addWidget'):
                self.pane_splitter.addWidget(widget)
                count = getattr(self.pane_splitter, 'count', lambda: 0)()
                self.logger.debug(f"Successfully added widget to splitter. "
                                f"Splitter now has {count} widgets")
            elif hasattr(self.pane_splitter, 'layout'):
                # Fallback for QWidget with layout
                layout = self.pane_splitter.layout()
                if layout:
                    layout.addWidget(widget)
                    self.logger.debug("Added widget to fallback layout")
            else:
                self.logger.warning("pane_splitter does not support widget addition")
                
        except RuntimeError as e:
            if WIDGET_DELETED_ERROR in str(e):
                self.logger.warning(f"Cannot add deleted widget: {e}")
            else:
                raise
    
    def _create_grid_layout(self):
        """Create a responsive grid layout for panes."""
        if len(self.panes) < 3:
            # Fallback to horizontal for insufficient panes
            self._create_horizontal_layout()
            return
        
        # Determine optimal grid configuration
        pane_count = len(self.panes)
        cols = self.grid_columns.get(pane_count, 2)
        rows = (pane_count + cols - 1) // cols  # Ceiling division
        
        self.pane_splitter.setOrientation(Qt.Vertical)
        
        # Clear existing widgets
        for i in reversed(range(self.pane_splitter.count())):
            widget = self.pane_splitter.widget(i)
            if widget:
                widget.setParent(None)
        
        # Create row splitters
        row_splitters = []
        for row in range(rows):
            row_splitter = QSplitter(Qt.Horizontal)
            row_splitters.append(row_splitter)
            
            # Add panes to this row
            start_idx = row * cols
            end_idx = min(start_idx + cols, pane_count)
            
            for pane_idx in range(start_idx, end_idx):
                if pane_idx < len(self.panes):
                    self._safe_add_widget_to_splitter_with_target(
                        row_splitter, self.panes[pane_idx]
                    )
            
            self.pane_splitter.addWidget(row_splitter)
        
        # Set equal sizes for responsive behavior
        if row_splitters:
            sizes = [100] * len(row_splitters)
            self.pane_splitter.setSizes(sizes)
            
            # Set equal column sizes within each row
            for splitter in row_splitters:
                if splitter.count() > 0:
                    col_sizes = [100] * splitter.count()
                    splitter.setSizes(col_sizes)
    
    def _create_horizontal_layout(self):
        """Create horizontal layout for panes."""
        if not self.pane_splitter:
            self.logger.error("Cannot create layout: pane_splitter is None")
            return
            
        self.logger.info(f"Creating horizontal layout for {len(self.panes)} panes")
        
        # Handle QSplitter
        if hasattr(self.pane_splitter, 'setOrientation'):
            self.pane_splitter.setOrientation(Qt.Horizontal)
            
            # Clear existing widgets from splitter
            if hasattr(self.pane_splitter, 'count'):
                for i in reversed(range(self.pane_splitter.count())):
                    widget = self.pane_splitter.widget(i)
                    if widget:
                        widget.setParent(None)
        
        # Handle QWidget with layout
        elif hasattr(self.pane_splitter, 'layout'):
            layout = self.pane_splitter.layout()
            if layout:
                # Clear existing widgets from layout
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
        
        self.logger.info("Cleared existing widgets from container")
        
        # Add all panes horizontally
        for idx, pane in enumerate(self.panes):
            self.logger.info(f"Adding pane {idx + 1} to horizontal layout")
            
            # Ensure pane is visible before adding
            if hasattr(pane, 'show'):
                pane.show()
                pane.setVisible(True)
            
            self._safe_add_widget_to_splitter_with_target(
                self.pane_splitter, pane
            )
        
        # Verify panes were added
        if hasattr(self.pane_splitter, 'count'):
            final_count = self.pane_splitter.count()
            self.logger.info(f"Final splitter count: {final_count}")
            if final_count != len(self.panes):
                self.logger.warning(f"Expected {len(self.panes)} panes in splitter, "
                                  f"but found {final_count}")
        
        # Set equal sizes
        if self.panes and hasattr(self.pane_splitter, 'setSizes'):
            sizes = [100] * len(self.panes)
            self.pane_splitter.setSizes(sizes)
            self.logger.info(f"Set equal sizes for {len(self.panes)} panes")
        
        self.logger.info("Horizontal layout creation completed")
    
    def _create_vertical_layout(self):
        """Create vertical layout for panes."""
        if not self.pane_splitter:
            self.logger.error("Cannot create layout: pane_splitter is None")
            return
            
        # Handle QSplitter
        if hasattr(self.pane_splitter, 'setOrientation'):
            self.pane_splitter.setOrientation(Qt.Vertical)
            
            # Clear existing widgets from splitter
            if hasattr(self.pane_splitter, 'count'):
                for i in reversed(range(self.pane_splitter.count())):
                    widget = self.pane_splitter.widget(i)
                    if widget:
                        widget.setParent(None)
        
        # Handle QWidget with layout (convert to vertical layout)
        elif hasattr(self.pane_splitter, 'layout'):
            # Remove existing layout and create new vertical layout
            old_layout = self.pane_splitter.layout()
            if old_layout:
                while old_layout.count():
                    child = old_layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                old_layout.deleteLater()
            
            # Create new vertical layout
            new_layout = QVBoxLayout(self.pane_splitter)
            new_layout.setContentsMargins(0, 0, 0, 0)
            new_layout.setSpacing(2)
        
        # Add all panes vertically
        for pane in self.panes:
            self._safe_add_widget_to_splitter_with_target(
                self.pane_splitter, pane
            )
        
        # Set equal sizes for QSplitter
        if self.panes and hasattr(self.pane_splitter, 'setSizes'):
            sizes = [100] * len(self.panes)
            self.pane_splitter.setSizes(sizes)
    
    def _safe_add_widget_to_splitter_with_target(
            self, target_splitter, widget):
        """Safely add widget to specific splitter with validation."""
        WIDGET_DELETED_ERROR = "wrapped C/C++ object"
        
        try:
            if not target_splitter or not widget:
                self.logger.warning("Cannot add widget: target_splitter or widget is None")
                return
                
            # Test widget validity before adding
            try:
                _ = widget.isVisible()
            except RuntimeError as e:
                if WIDGET_DELETED_ERROR in str(e):
                    self.logger.warning(f"Widget already deleted: {e}")
                    return
                raise
            
            # Add widget to target splitter
            if hasattr(target_splitter, 'addWidget'):
                target_splitter.addWidget(widget)
                # Get count for verification
                count = getattr(target_splitter, 'count', lambda: 0)()
                self.logger.debug(f"Successfully added widget to "
                                f"{type(target_splitter).__name__}, count now: {count}")
            elif hasattr(target_splitter, 'layout'):
                # Fallback for QWidget with layout
                layout = target_splitter.layout()
                if layout:
                    layout.addWidget(widget)
                    self.logger.debug("Added widget to fallback layout")
            else:
                self.logger.error(f"Target splitter {type(target_splitter).__name__} "
                                f"does not support widget addition")
                
        except RuntimeError as e:
            if WIDGET_DELETED_ERROR in str(e):
                self.logger.warning(f"Widget already deleted: {e}")
            else:
                raise
        except Exception as e:
            self.logger.error(f"Error adding widget to splitter: {e}")
    
    def on_pane_count_changed(self, text):
        """Handle pane count change from combo box."""
        try:
            count = int(text)
            self.set_pane_count(count)
        except ValueError:
            pass
    
    def on_layout_mode_changed(self, text):
        """Handle layout mode change with responsive validation."""
        if not text or not text.strip():
            # Ignore empty or whitespace-only changes
            return
            
        new_mode = text.lower()
        
        # Validate layout mode against current pane count constraints
        available = self.available_layouts.get(self.pane_count, [])
        
        if new_mode in available or new_mode == 'single view':
            if new_mode == 'single view':
                self.layout_mode = 'single'
            else:
                self.layout_mode = new_mode
            
            self._update_pane_layout()
            self.save_configuration()
            
            self.logger.info(
                f"Layout mode changed to {self.layout_mode} "
                f"for {self.pane_count} panes"
            )
        else:
            self.logger.warning(
                f"Layout mode {new_mode} not available for "
                f"{self.pane_count} panes"
            )
            # Revert combo to valid selection
            if hasattr(self, 'layout_combo') and self.layout_combo:
                self._update_layout_combo_options(self.layout_combo)
    
    def save_configuration(self):
        """Save current configuration with enhanced Qt object support."""
        try:
            # Use enhanced config manager if available
            if get_enhanced_config_manager:
                enhanced_config = get_enhanced_config_manager()
                if enhanced_config:
                    # Save configuration with proper Qt object handling
                    enhanced_config.set_setting('file_explorer', 'geometry',
                                               self.saveGeometry())
                    enhanced_config.set_setting('file_explorer', 'pane_count',
                                               self.pane_count)
                    enhanced_config.set_setting('file_explorer', 'layout_mode',
                                               self.layout_mode)
                    enhanced_config.save_config()
                    self.logger.debug("Configuration saved with enhanced manager")
                    return
            
            # Fallback to basic config manager
            if self.config_manager:
                try:
                    self.config_manager.set_setting('file_explorer.pane_count',
                                                   self.pane_count)
                    self.config_manager.set_setting('file_explorer.layout_mode',
                                                   self.layout_mode)
                    self.logger.debug("Configuration saved with basic manager")
                except Exception as e:
                    self.logger.warning(f"Basic config save failed: {e}")
                
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    # Tool launcher methods
    def launch_file_finder(self):
        """Launch File Finder tool."""
        self._launch_tool("File Finder", "src.tools.file_management.file_finder", "FileFinderGUI")
    
    def launch_size_analyzer(self):
        """Launch Size Analyzer tool."""
        self._launch_tool("Size Analyzer", "src.tools.analysis.size_analyzer", "SizeAnalyzerGUI")
    
    def launch_duplicate_finder(self):
        """Launch Duplicate Finder tool."""
        self._launch_tool("Duplicate Finder", "src.tools.analysis.find_duplicate_files", "DuplicateFinderApp")
    
    def launch_encrypt_decrypt(self):
        """Launch Encrypt/Decrypt tool."""
        self._launch_tool("Encrypt/Decrypt", "src.tools.security.en_and_decrypt", "EnAndDecryptGUI")
    
    def launch_catalog(self):
        """Launch Catalog tool."""
        self._launch_tool("Catalog", "src.tools.file_management.catalog", "CatalogWindow")
    
    def launch_organize(self):
        """Launch Organize tool."""
        self._launch_tool("Organize", "src.tools.file_management.organize", "OrganizeWindow")
    
    def launch_checksum(self):
        """Launch Checksum tool."""
        self._launch_tool("Checksum", "src.tools.analysis.check_sum", "ChecksumGUI")
    
    def launch_secure_delete(self):
        """Launch Secure Delete tool."""
        self._launch_tool("Secure Delete", "src.tools.security.secure_delete", "SecureDeleteGUI")
    
    def launch_permissions(self):
        """Launch Permissions Editor tool."""
        self._launch_tool("Permissions", "src.tools.system.permissions_editor", "PermissionsEditorGUI")
    
    def _launch_tool(self, tool_name: str, module_name: str, class_name: str):
        """Generic tool launcher with error handling."""
        try:
            # Import and launch tool
            module = __import__(module_name, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            tool_instance = tool_class()
            tool_instance.show()
            
            self.statusBar().showMessage(f"{tool_name} launched successfully", 3000)
            self.logger.info(f"Launched tool: {tool_name}")
            
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to launch {tool_name}: {e}")
            QMessageBox.warning(
                self,
                "Tool Launch Error",
                f"Could not launch {tool_name}:\n\n{e}\n\n"
                f"Please ensure the tool is properly installed."
            )
    
    def go_back(self):
        """Navigate back in active pane."""
        try:
            if self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                
                # Try enhanced navigation first
                if hasattr(active_pane, 'navigation_bar') and hasattr(active_pane.navigation_bar, '_go_back'):
                    active_pane.navigation_bar._go_back()
                else:
                    # Fallback navigation
                    self._fallback_navigation_back(active_pane)
                
                if self.enhanced_status_bar:
                    self.enhanced_status_bar.set_main_message("Navigated back")
            
        except Exception as e:
            self.logger.error(f"Error navigating back: {e}")
    
    def go_forward(self):
        """Navigate forward in active pane."""
        try:
            if self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                
                # Try enhanced navigation first
                if hasattr(active_pane, 'navigation_bar') and hasattr(active_pane.navigation_bar, '_go_forward'):
                    active_pane.navigation_bar._go_forward()
                else:
                    # Fallback navigation
                    self._fallback_navigation_forward(active_pane)
                
                if self.enhanced_status_bar:
                    self.enhanced_status_bar.set_main_message("Navigated forward")
            
        except Exception as e:
            self.logger.error(f"Error navigating forward: {e}")
    
    def go_up(self):
        """Navigate up one directory level in active pane."""
        try:
            if self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                
                # Try enhanced navigation first
                if hasattr(active_pane, 'navigation_bar') and hasattr(active_pane.navigation_bar, '_go_up'):
                    active_pane.navigation_bar._go_up()
                elif hasattr(active_pane, 'navigate_up'):
                    active_pane.navigate_up()
                else:
                    # Fallback navigation
                    self._fallback_navigation_up(active_pane)
                
                if self.enhanced_status_bar:
                    self.enhanced_status_bar.set_main_message("Navigated up")
            
        except Exception as e:
            self.logger.error(f"Error navigating up: {e}")
    
    def refresh_current_pane(self):
        """Refresh the current active pane."""
        try:
            if self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                
                # Try enhanced refresh first
                if hasattr(active_pane, 'navigation_bar') and hasattr(active_pane.navigation_bar, '_refresh'):
                    active_pane.navigation_bar._refresh()
                elif hasattr(active_pane, 'refresh_current_directory'):
                    active_pane.refresh_current_directory()
                elif hasattr(active_pane, '_refresh_pane'):
                    active_pane._refresh_pane(active_pane)
                else:
                    # Fallback refresh
                    self._fallback_refresh_pane(active_pane)
                
                if self.enhanced_status_bar:
                    self.enhanced_status_bar.set_main_message("Refreshed pane")
            
        except Exception as e:
            self.logger.error(f"Error refreshing pane: {e}")
    
    # Event handlers
    def new_tab(self):
        """Create a new tab."""
        self.statusBar().showMessage("New tab functionality will be implemented", 2000)
    
    def on_tool_selected(self, item, column):
        """Handle tool selection from tool dock."""
        if item.parent():  # Only handle leaf items (actual tools)
            tool_name = item.text(0)
            self.statusBar().showMessage(f"Selected tool: {tool_name}", 2000)
    
    def on_bookmark_selected(self, item, column):
        """Handle bookmark selection."""
        path = item.data(0, Qt.UserRole)
        if path:
            self.statusBar().showMessage(f"Navigate to: {path}", 2000)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About RFU Multi-Pane Explorer",
            "RFU Multi-Pane File Explorer v1.0\n\n"
            "A sophisticated file management interface inspired by Total Commander\n"
            "with full integration to Richard's File Utilities.\n\n"
            "Features:\n"
            "• 1-4 configurable file explorer panes\n"
            "• Cross-platform compatibility\n"
            "• Integrated access to all RFU tools\n"
            "• Advanced file operations\n"
            "• Customizable layouts and themes\n\n"
            "© 2025 Richard Noragon"
        )
    
    def show_help(self):
        """Show help dialog."""
        QMessageBox.information(
            self,
            "RFU Explorer Help",
            "RFU Multi-Pane File Explorer Help\n\n"
            "Keyboard Shortcuts:\n"
            "• Ctrl+1/2/3/4 - Switch pane count\n"
            "• F5 - Refresh current pane\n"
            "• Ctrl+F - Launch File Finder\n"
            "• Ctrl+D - Launch Duplicate Finder\n"
            "• F1 - Show this help\n\n"
            "Mouse Operations:\n"
            "• Double-click bookmark to navigate\n"
            "• Double-click tool to launch\n"
            "• Drag splitters to resize panes\n\n"
            "For complete documentation, see the RFU manual."
        )
    
    # Advanced feature support methods
    def _sync_navigation_to_other_panes(self, path: str):
        """Synchronize navigation to other panes if enabled."""
        if not self.synchronized_navigation:
            return
        
        try:
            for i, pane in enumerate(self.panes):
                if i != self.active_pane_index:
                    if hasattr(pane, 'set_path'):
                        pane.set_path(path)
                    elif hasattr(pane, 'navigate_to_path'):
                        pane.navigate_to_path(Path(path))
        except Exception as e:
            self.logger.error(f"Error syncing navigation: {e}")
    
    def _update_side_panels_for_path(self, path: str):
        """Update side panels when path changes."""
        try:
            # Update property panel if it's a directory
            if self.property_panel and Path(path).is_dir():
                self.property_panel.set_file_info(path)
            
            # Update preview widget
            if self.preview_widget:
                self.preview_widget.set_file_preview(path)
                
        except Exception as e:
            self.logger.error(f"Error updating side panels: {e}")
    
    def _get_pane_current_path(self, pane) -> Optional[str]:
        """Get current path from a pane."""
        try:
            if hasattr(pane, 'current_path'):
                return pane.current_path
            elif hasattr(pane, 'get_current_path'):
                return pane.get_current_path()
            elif hasattr(pane, '_current_path'):
                return getattr(pane, '_current_path', None)
            return None
        except Exception:
            return None
    
    def _open_file_with_default_app(self, file_path: str):
        """Open file with default application."""
        try:
            path_obj = Path(file_path)
            
            if path_obj.is_file():
                import platform
                import subprocess
                
                system = platform.system()
                if system == "Windows":
                    os.startfile(str(path_obj))
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", str(path_obj)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(path_obj)])
                
                if self.enhanced_status_bar:
                    self.enhanced_status_bar.set_main_message(f"Opened: {path_obj.name}", "success")
                
        except Exception as e:
            self.logger.warning(f"Could not open file {file_path}: {e}")
            QMessageBox.warning(
                self,
                "File Open Error",
                f"Could not open file:\n{file_path}\n\nError: {e}"
            )
    
    def _refresh_bookmark_widget(self):
        """Refresh bookmark widget display."""
        try:
            if hasattr(self, 'bookmark_widget'):
                self._populate_bookmark_tree(self.bookmark_widget)
        except Exception as e:
            self.logger.error(f"Error refreshing bookmark widget: {e}")
    
    def _refresh_recent_locations_widget(self):
        """Refresh recent locations widget."""
        try:
            if hasattr(self, 'recent_widget'):
                self.recent_widget.clear()
                for location in self.recent_locations[-10:]:
                    item = QTreeWidgetItem([Path(location).name])
                    item.setData(0, Qt.UserRole, location)
                    item.setToolTip(0, location)
                    self.recent_widget.addTopLevelItem(item)
        except Exception as e:
            self.logger.error(f"Error refreshing recent locations: {e}")
    
    def _populate_bookmark_tree(self, bookmark_tree):
        """Populate bookmark tree with bookmarks."""
        try:
            bookmark_tree.clear()
            
            if self.bookmark_manager:
                # Use advanced bookmark manager
                bookmarks = self.bookmark_manager.get_all_bookmarks()
                for bookmark in bookmarks:
                    item = QTreeWidgetItem([bookmark.name])
                    item.setData(0, Qt.UserRole, bookmark.path)
                    item.setToolTip(0, bookmark.path)
                    bookmark_tree.addTopLevelItem(item)
            else:
                # Fallback to simple bookmarks
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
                    
        except Exception as e:
            self.logger.error(f"Error populating bookmark tree: {e}")
    
    # Event handlers for enhanced widgets
    def _on_bookmark_activated(self, item, column):
        """Handle bookmark activation."""
        try:
            path = item.data(0, Qt.UserRole)
            if path and self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                if hasattr(active_pane, 'set_path'):
                    active_pane.set_path(path)
                elif hasattr(active_pane, 'navigate_to_path'):
                    active_pane.navigate_to_path(Path(path))
        except Exception as e:
            self.logger.error(f"Error activating bookmark: {e}")
    
    def _on_simple_bookmark_activated(self, item, column):
        """Handle simple bookmark activation."""
        self._on_bookmark_activated(item, column)
    
    def _on_recent_location_activated(self, item, column):
        """Handle recent location activation."""
        try:
            path = item.data(0, Qt.UserRole)
            if path and self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                if hasattr(active_pane, 'set_path'):
                    active_pane.set_path(path)
                elif hasattr(active_pane, 'navigate_to_path'):
                    active_pane.navigate_to_path(Path(path))
        except Exception as e:
            self.logger.error(f"Error activating recent location: {e}")
    
    def _on_tool_activated(self, item, column):
        """Handle tool activation from enhanced tools widget."""
        try:
            if item.parent():  # Only handle leaf items
                callback = item.data(0, Qt.UserRole)
                if callable(callback):
                    callback()
        except Exception as e:
            self.logger.error(f"Error activating tool: {e}")
    
    def _show_bookmark_context_menu(self, position):
        """Show context menu for bookmarks."""
        try:
            item = self.bookmark_widget.itemAt(position)
            if not item:
                return
            
            menu = QMenu(self)
            
            # Open action
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self._on_bookmark_activated(item, 0))
            menu.addAction(open_action)
            
            # Open in new pane action
            if len(self.panes) > 1:
                new_pane_action = QAction("Open in Other Pane", self)
                new_pane_action.triggered.connect(lambda: self._open_bookmark_in_other_pane(item))
                menu.addAction(new_pane_action)
            
            menu.addSeparator()
            
            # Delete action
            delete_action = QAction("Delete Bookmark", self)
            delete_action.triggered.connect(lambda: self._delete_bookmark(item))
            menu.addAction(delete_action)
            
            menu.exec_(self.bookmark_widget.mapToGlobal(position))
            
        except Exception as e:
            self.logger.error(f"Error showing bookmark context menu: {e}")
    
    def _open_bookmark_in_other_pane(self, item):
        """Open bookmark in other pane."""
        try:
            path = item.data(0, Qt.UserRole)
            if path and len(self.panes) > 1:
                # Find another pane
                other_pane_index = (self.active_pane_index + 1) % len(self.panes)
                other_pane = self.panes[other_pane_index]
                
                if hasattr(other_pane, 'set_path'):
                    other_pane.set_path(path)
                elif hasattr(other_pane, 'navigate_to_path'):
                    other_pane.navigate_to_path(Path(path))
        except Exception as e:
            self.logger.error(f"Error opening bookmark in other pane: {e}")
    
    def _delete_bookmark(self, item):
        """Delete bookmark."""
        try:
            if self.bookmark_manager:
                # Use advanced bookmark manager
                bookmark_path = item.data(0, Qt.UserRole)
                # TODO: Implement bookmark deletion by path
                pass
        except Exception as e:
            self.logger.error(f"Error deleting bookmark: {e}")
    
    def _handle_file_activation(self, file_path: str):
        """Handle file activation (opening with default application)."""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            self.logger.error(f"Error opening file {file_path}: {e}")
            QMessageBox.warning(self, "File Open Error", f"Could not open file: {e}")
    
    def _copy_to_other_pane(self):
        """Copy selected files to other pane."""
        try:
            source_pane = self._get_active_pane()
            target_pane = self._get_other_pane()
            
            if not source_pane or not target_pane:
                QMessageBox.warning(self, "Copy Error", "Need at least two panes for copy operation")
                return
            
            # Get selected files from source pane
            selected_files = self._get_selected_files(source_pane)
            if not selected_files:
                QMessageBox.warning(self, "Copy Error", "No files selected")
                return
            
            # Get target directory
            target_path = getattr(target_pane, '_current_path', Path.home())
            
            # Perform copy operation
            for file_path in selected_files:
                try:
                    src = Path(file_path)
                    dst = target_path / src.name
                    
                    if src.is_file():
                        dst.write_bytes(src.read_bytes())
                    elif src.is_dir():
                        # For directories, use shutil.copytree
                        import shutil
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        
                    self.statusBar().showMessage(f"Copied {src.name} to {target_path}", 3000)
                    
                except Exception as e:
                    self.logger.error(f"Error copying {file_path}: {e}")
                    QMessageBox.warning(self, "Copy Error", f"Error copying {file_path}: {e}")
            
            # Refresh target pane
            self._refresh_pane(target_pane)
            
        except Exception as e:
            self.logger.error(f"Error in copy to other pane: {e}")
    
    def _move_to_other_pane(self):
        """Move selected files to other pane."""
        try:
            source_pane = self._get_active_pane()
            target_pane = self._get_other_pane()
            
            if not source_pane or not target_pane:
                QMessageBox.warning(self, "Move Error", "Need at least two panes for move operation")
                return
            
            # Get selected files from source pane
            selected_files = self._get_selected_files(source_pane)
            if not selected_files:
                QMessageBox.warning(self, "Move Error", "No files selected")
                return
            
            # Get target directory
            target_path = getattr(target_pane, '_current_path', Path.home())
            
            # Perform move operation
            for file_path in selected_files:
                try:
                    src = Path(file_path)
                    dst = target_path / src.name
                    
                    src.rename(dst)
                    self.statusBar().showMessage(f"Moved {src.name} to {target_path}", 3000)
                    
                except Exception as e:
                    self.logger.error(f"Error moving {file_path}: {e}")
                    QMessageBox.warning(self, "Move Error", f"Error moving {file_path}: {e}")
            
            # Refresh both panes
            self._refresh_pane(source_pane)
            self._refresh_pane(target_pane)
            
        except Exception as e:
            self.logger.error(f"Error in move to other pane: {e}")
    
    def _get_active_pane(self):
        """Get the currently active pane."""
        try:
            if 0 <= self.active_pane_index < len(self.panes):
                return self.panes[self.active_pane_index]
            return None
        except Exception:
            return None
    
    def _get_other_pane(self):
        """Get a different pane (not the active one)."""
        try:
            if len(self.panes) < 2:
                return None
            
            for i, pane in enumerate(self.panes):
                if i != self.active_pane_index:
                    return pane
            return None
        except Exception:
            return None
    
    def _get_selected_files(self, pane):
        """Get list of selected files from a pane."""
        try:
            selected_files = []
            
            if hasattr(pane, '_file_list'):
                file_list = pane._file_list
                selected_items = file_list.selectedItems()
                current_path = getattr(pane, '_current_path', Path.home())
                
                for item in selected_items:
                    if item.parent() is None:  # Top-level item
                        file_name = item.text(0)
                        file_path = current_path / file_name
                        selected_files.append(str(file_path))
            
            return selected_files
        except Exception as e:
            self.logger.error(f"Error getting selected files: {e}")
            return []
    
    def _sync_panes(self):
        """Synchronize navigation between panes."""
        try:
            active_pane = self._get_active_pane()
            if not active_pane:
                return
            
            active_path = getattr(active_pane, '_current_path', None)
            if not active_path:
                return
            
            # Navigate all other panes to the same path
            for i, pane in enumerate(self.panes):
                if i != self.active_pane_index:
                    self._navigate_to_path(pane, active_path)
            
            self.statusBar().showMessage(f"Synchronized panes to: {active_path}", 3000)
            
        except Exception as e:
            self.logger.error(f"Error synchronizing panes: {e}")
    
    def _compare_panes(self):
        """Compare files between two panes."""
        try:
            if len(self.panes) < 2:
                QMessageBox.warning(self, "Compare Error", "Need at least two panes for comparison")
                return
            
            pane1 = self.panes[0]
            pane2 = self.panes[1]
            
            path1 = getattr(pane1, '_current_path', None)
            path2 = getattr(pane2, '_current_path', None)
            
            if not path1 or not path2:
                QMessageBox.warning(self, "Compare Error", "Both panes must have valid paths")
                return
            
            # Simple comparison - list different files
            try:
                files1 = set(item.name for item in path1.iterdir() if item.is_file())
                files2 = set(item.name for item in path2.iterdir() if item.is_file())
                
                only_in_pane1 = files1 - files2
                only_in_pane2 = files2 - files1
                
                message = f"Comparison Results:\n\n"
                message += f"Only in {path1.name}: {len(only_in_pane1)} files\n"
                message += f"Only in {path2.name}: {len(only_in_pane2)} files\n"
                message += f"Common files: {len(files1 & files2)} files"
                
                if only_in_pane1:
                    message += f"\n\nUnique to {path1.name}:\n" + "\n".join(list(only_in_pane1)[:10])
                    if len(only_in_pane1) > 10:
                        message += f"\n... and {len(only_in_pane1) - 10} more"
                
                if only_in_pane2:
                    message += f"\n\nUnique to {path2.name}:\n" + "\n".join(list(only_in_pane2)[:10])
                    if len(only_in_pane2) > 10:
                        message += f"\n... and {len(only_in_pane2) - 10} more"
                
                QMessageBox.information(self, "Pane Comparison", message)
                
            except Exception as e:
                QMessageBox.warning(self, "Compare Error", f"Error comparing directories: {e}")
            
        except Exception as e:
            self.logger.error(f"Error comparing panes: {e}")
    
    # Fallback navigation methods
    def _fallback_navigation_back(self, pane):
        """Fallback navigation back implementation."""
        # Basic implementation - go to parent directory
        current_path = self._get_pane_current_path(pane)
        if current_path:
            parent_path = str(Path(current_path).parent)
            if parent_path != current_path:
                if hasattr(pane, 'navigate_to_path'):
                    pane.navigate_to_path(Path(parent_path))
    
    def _fallback_navigation_forward(self, pane):
        """Fallback navigation forward implementation."""
        # No simple implementation for forward navigation
        pass
    
    def _fallback_navigation_up(self, pane):
        """Fallback navigation up implementation."""
        current_path = self._get_pane_current_path(pane)
        if current_path:
            parent_path = str(Path(current_path).parent)
            if parent_path != current_path:
                if hasattr(pane, 'navigate_to_path'):
                    pane.navigate_to_path(Path(parent_path))
    
    def _fallback_refresh_pane(self, pane):
        """Fallback pane refresh implementation."""
        current_path = self._get_pane_current_path(pane)
        if current_path and hasattr(pane, 'navigate_to_path'):
            pane.navigate_to_path(Path(current_path))
    
    # Enhanced setup and initialization methods
    def setup_advanced_features(self):
        """Setup advanced features and managers."""
        try:
            # Initialize bookmark manager
            if BookmarkManager:
                self.bookmark_manager = BookmarkManager()
            
            # Initialize advanced tool launcher
            if AdvancedToolLauncher:
                self.tool_launcher = AdvancedToolLauncher(registry=None)  # TODO: Provide proper registry
            
            # Initialize keyboard shortcut manager
            if KeyboardShortcutManager:
                self.shortcut_manager = KeyboardShortcutManager()
                self._setup_enhanced_shortcuts()
            
            # Setup advanced search functionality
            self._setup_search_functionality()
            
            # Setup context menus
            self._setup_context_menus()
            
            # Setup drag and drop
            self._setup_drag_drop()
            
            # Setup file preview
            self._setup_file_preview()
            
            self.logger.info("Advanced features setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up advanced features: {e}")
    
    def _setup_search_functionality(self):
        """Setup enhanced search and filtering."""
        try:
            # Global search shortcut
            search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
            search_shortcut.activated.connect(self._show_search_dialog)
            
            # Quick filter shortcut
            filter_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
            filter_shortcut.activated.connect(self._show_quick_filter)
            
            self.logger.debug("Search functionality setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up search functionality: {e}")
    
    def _setup_context_menus(self):
        """Setup enhanced context menus for panes."""
        try:
            # Enable context menus for all panes
            for pane in self.panes:
                if hasattr(pane, '_file_list'):
                    file_list = pane._file_list
                    file_list.setContextMenuPolicy(Qt.CustomContextMenu)
                    file_list.customContextMenuRequested.connect(
                        lambda pos, p=pane: self._show_file_context_menu(pos, p)
                    )
            
            self.logger.debug("Context menus setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up context menus: {e}")
    
    def _setup_drag_drop(self):
        """Setup drag and drop functionality between panes."""
        try:
            # Enable drag and drop for all panes
            for pane in self.panes:
                if hasattr(pane, '_file_list'):
                    file_list = pane._file_list
                    file_list.setDragDropMode(file_list.DragDropMode.DragDrop)
                    file_list.setDefaultDropAction(Qt.CopyAction)
            
            self.logger.debug("Drag and drop setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up drag and drop: {e}")
    
    def _setup_file_preview(self):
        """Setup file preview functionality."""
        try:
            # File preview shortcut
            preview_shortcut = QShortcut(QKeySequence("Space"), self)
            preview_shortcut.activated.connect(self._show_file_preview)
            
            self.logger.debug("File preview setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up file preview: {e}")
    
    def _show_search_dialog(self):
        """Show advanced search dialog."""
        try:
            from PyQt5.QtWidgets import (QCheckBox, QDialog, QLineEdit,
                                         QPushButton, QVBoxLayout)
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Advanced Search")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QVBoxLayout()
            
            # Search query
            query_input = QLineEdit()
            query_input.setPlaceholderText("Enter search query...")
            layout.addWidget(QLabel("Search Query:"))
            layout.addWidget(query_input)
            
            # Search options
            case_sensitive = QCheckBox("Case sensitive")
            regex_search = QCheckBox("Use regular expressions")
            search_subdirs = QCheckBox("Search in subdirectories")
            search_subdirs.setChecked(True)
            
            layout.addWidget(case_sensitive)
            layout.addWidget(regex_search)
            layout.addWidget(search_subdirs)
            
            # Buttons
            button_layout = QHBoxLayout()
            search_btn = QPushButton("Search")
            cancel_btn = QPushButton("Cancel")
            
            search_btn.clicked.connect(lambda: self._perform_search(
                query_input.text(),
                case_sensitive.isChecked(),
                regex_search.isChecked(),
                search_subdirs.isChecked()
            ))
            search_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(search_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            self.logger.error(f"Error showing search dialog: {e}")
    
    def _show_quick_filter(self):
        """Show quick filter input."""
        try:
            from PyQt5.QtWidgets import QInputDialog
            
            text, ok = QInputDialog.getText(self, "Quick Filter", "Filter files by name:")
            if ok and text:
                self._apply_filter_to_active_pane(text)
                
        except Exception as e:
            self.logger.error(f"Error showing quick filter: {e}")
    
    def _perform_search(self, query, case_sensitive, use_regex, search_subdirs):
        """Perform search operation."""
        try:
            if not query:
                return
            
            active_pane = self._get_active_pane()
            if not active_pane:
                return
            
            current_path = getattr(active_pane, '_current_path', Path.home())
            results = []
            
            import re
            pattern = query
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    regex = re.compile(pattern, flags)
                except re.error:
                    QMessageBox.warning(self, "Search Error", "Invalid regular expression")
                    return
            else:
                if not case_sensitive:
                    query = query.lower()
            
            # Search files
            def search_directory(directory):
                try:
                    for item in directory.iterdir():
                        if item.is_file():
                            name = item.name
                            if not case_sensitive and not use_regex:
                                name = name.lower()
                            
                            if use_regex:
                                if regex.search(item.name):
                                    results.append(str(item))
                            else:
                                if query in name:
                                    results.append(str(item))
                        
                        elif item.is_dir() and search_subdirs:
                            search_directory(item)
                except (PermissionError, OSError):
                    pass
            
            search_directory(current_path)
            
            # Show results
            if results:
                message = f"Found {len(results)} files:\n\n"
                message += "\n".join(results[:20])
                if len(results) > 20:
                    message += f"\n\n... and {len(results) - 20} more files"
                
                QMessageBox.information(self, "Search Results", message)
            else:
                QMessageBox.information(self, "Search Results", "No files found matching the search criteria")
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            QMessageBox.warning(self, "Search Error", f"Error during search: {e}")
    
    def _apply_filter_to_active_pane(self, filter_text):
        """Apply filter to active pane."""
        try:
            active_pane = self._get_active_pane()
            if not active_pane or not hasattr(active_pane, '_file_list'):
                return
            
            file_list = active_pane._file_list
            filter_text = filter_text.lower()
            
            # Hide items that don't match filter
            for i in range(file_list.topLevelItemCount()):
                item = file_list.topLevelItem(i)
                if item:
                    item_name = item.text(0).lower()
                    item.setHidden(filter_text not in item_name)
            
            self.statusBar().showMessage(f"Filter applied: {filter_text}", 3000)
            
        except Exception as e:
            self.logger.error(f"Error applying filter: {e}")
    
    def _show_file_context_menu(self, position, pane):
        """Show context menu for file operations."""
        try:
            if not hasattr(pane, '_file_list'):
                return
            
            file_list = pane._file_list
            item = file_list.itemAt(position)
            
            menu = QMenu(self)
            
            if item:
                # File-specific actions
                open_action = QAction("Open", self)
                open_action.triggered.connect(lambda: self._open_selected_file(pane))
                menu.addAction(open_action)
                
                menu.addSeparator()
                
                copy_action = QAction("Copy to Other Pane", self)
                copy_action.triggered.connect(self._copy_to_other_pane)
                menu.addAction(copy_action)
                
                move_action = QAction("Move to Other Pane", self)
                move_action.triggered.connect(self._move_to_other_pane)
                menu.addAction(move_action)
                
                menu.addSeparator()
                
                delete_action = QAction("Delete", self)
                delete_action.triggered.connect(lambda: self._delete_selected_files(pane))
                menu.addAction(delete_action)
                
                properties_action = QAction("Properties", self)
                properties_action.triggered.connect(lambda: self._show_file_properties(pane))
                menu.addAction(properties_action)
            
            # Pane-level actions
            menu.addSeparator()
            
            refresh_action = QAction("Refresh", self)
            refresh_action.triggered.connect(lambda: self._refresh_pane(pane))
            menu.addAction(refresh_action)
            
            new_folder_action = QAction("New Folder", self)
            new_folder_action.triggered.connect(lambda: self._create_new_folder(pane))
            menu.addAction(new_folder_action)
            
            menu.exec_(file_list.mapToGlobal(position))
            
        except Exception as e:
            self.logger.error(f"Error showing file context menu: {e}")
    
    def _open_selected_file(self, pane):
        """Open the selected file in the pane."""
        try:
            selected_files = self._get_selected_files(pane)
            for file_path in selected_files:
                if Path(file_path).is_file():
                    self._handle_file_activation(file_path)
                    break
        except Exception as e:
            self.logger.error(f"Error opening selected file: {e}")
    
    def _delete_selected_files(self, pane):
        """Delete selected files after confirmation."""
        try:
            selected_files = self._get_selected_files(pane)
            if not selected_files:
                return
            
            file_names = [Path(f).name for f in selected_files]
            message = f"Are you sure you want to delete {len(selected_files)} item(s)?\n\n"
            message += "\n".join(file_names[:5])
            if len(file_names) > 5:
                message += f"\n... and {len(file_names) - 5} more"
            
            reply = QMessageBox.question(
                self, "Confirm Delete", message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                for file_path in selected_files:
                    try:
                        path = Path(file_path)
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            import shutil
                            shutil.rmtree(path)
                    except Exception as e:
                        self.logger.error(f"Error deleting {file_path}: {e}")
                        QMessageBox.warning(self, "Delete Error", f"Could not delete {path.name}: {e}")
                
                # Refresh pane
                self._refresh_pane(pane)
                self.statusBar().showMessage(f"Deleted {len(selected_files)} items", 3000)
            
        except Exception as e:
            self.logger.error(f"Error deleting selected files: {e}")
    
    def _create_new_folder(self, pane):
        """Create a new folder in the pane."""
        try:
            from PyQt5.QtWidgets import QInputDialog
            
            current_path = getattr(pane, '_current_path', Path.home())
            
            name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
            if ok and name:
                new_folder = current_path / name
                try:
                    new_folder.mkdir(exist_ok=False)
                    self._refresh_pane(pane)
                    self.statusBar().showMessage(f"Created folder: {name}", 3000)
                except FileExistsError:
                    QMessageBox.warning(self, "Create Folder", f"Folder '{name}' already exists")
                except Exception as e:
                    QMessageBox.warning(self, "Create Folder", f"Error creating folder: {e}")
            
        except Exception as e:
            self.logger.error(f"Error creating new folder: {e}")
    
    def _show_file_properties(self, pane):
        """Show properties of selected file."""
        try:
            selected_files = self._get_selected_files(pane)
            if not selected_files:
                return
            
            file_path = Path(selected_files[0])
            if not file_path.exists():
                return
            
            # Create properties dialog
            from PyQt5.QtWidgets import QDialog, QFormLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Properties: {file_path.name}")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QFormLayout()
            
            # Basic properties
            layout.addRow("Name:", QLabel(file_path.name))
            layout.addRow("Path:", QLabel(str(file_path.parent)))
            layout.addRow("Type:", QLabel("Directory" if file_path.is_dir() else "File"))
            
            try:
                stat = file_path.stat()
                size = stat.st_size
                if file_path.is_file():
                    if size > 1024**3:
                        size_str = f"{size / (1024**3):.2f} GB"
                    elif size > 1024**2:
                        size_str = f"{size / (1024**2):.2f} MB"
                    elif size > 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    else:
                        size_str = f"{size} bytes"
                    layout.addRow("Size:", QLabel(size_str))
                
                modified = datetime.fromtimestamp(stat.st_mtime)
                layout.addRow("Modified:", QLabel(modified.strftime("%Y-%m-%d %H:%M:%S")))
                
                created = datetime.fromtimestamp(stat.st_ctime)
                layout.addRow("Created:", QLabel(created.strftime("%Y-%m-%d %H:%M:%S")))
                
            except Exception as e:
                layout.addRow("Error:", QLabel(f"Could not read file stats: {e}"))
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            self.logger.error(f"Error showing file properties: {e}")
    
    def _show_file_preview(self):
        """Show preview of selected file."""
        try:
            active_pane = self._get_active_pane()
            if not active_pane:
                return
            
            selected_files = self._get_selected_files(active_pane)
            if not selected_files:
                return
            
            file_path = Path(selected_files[0])
            if not file_path.is_file():
                return
            
            # Simple preview for text files
            if file_path.suffix.lower() in ['.txt', '.py', '.md', '.json', '.xml', '.css', '.js', '.html']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='replace')
                    if len(content) > 10000:
                        content = content[:10000] + "\n\n... (truncated)"
                    
                    from PyQt5.QtWidgets import QDialog, QTextEdit
                    
                    dialog = QDialog(self)
                    dialog.setWindowTitle(f"Preview: {file_path.name}")
                    dialog.setModal(True)
                    dialog.resize(600, 400)
                    
                    layout = QVBoxLayout()
                    text_edit = QTextEdit()
                    text_edit.setPlainText(content)
                    text_edit.setReadOnly(True)
                    layout.addWidget(text_edit)
                    
                    dialog.setLayout(layout)
                    dialog.exec_()
                    
                except Exception as e:
                    QMessageBox.warning(self, "Preview Error", f"Could not preview file: {e}")
            else:
                QMessageBox.information(self, "Preview", f"Preview not available for {file_path.suffix} files")
            
        except Exception as e:
            self.logger.error(f"Error showing file preview: {e}")
            
            self.logger.info("Advanced features initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up advanced features: {e}")
    
    def _setup_enhanced_shortcuts(self):
        """Setup enhanced keyboard shortcuts."""
        try:
            if not self.shortcut_manager:
                return
            
            # Navigation shortcuts
            self.shortcut_manager.register_shortcut("Alt+Left", self.go_back, "Go Back")
            self.shortcut_manager.register_shortcut("Alt+Right", self.go_forward, "Go Forward")
            self.shortcut_manager.register_shortcut("Alt+Up", self.go_up, "Go Up")
            self.shortcut_manager.register_shortcut("F5", self.refresh_current_pane, "Refresh")
            
            # Search and tools
            self.shortcut_manager.register_shortcut("Ctrl+F", self.show_search, "Search")
            self.shortcut_manager.register_shortcut("Ctrl+B", self.bookmark_current_location, "Bookmark")
            
            # Pane management
            self.shortcut_manager.register_shortcut("Ctrl+1", lambda: self.set_pane_count(1), "1 Pane")
            self.shortcut_manager.register_shortcut("Ctrl+2", lambda: self.set_pane_count(2), "2 Panes")
            self.shortcut_manager.register_shortcut("Ctrl+3", lambda: self.set_pane_count(3), "3 Panes")
            self.shortcut_manager.register_shortcut("Ctrl+4", lambda: self.set_pane_count(4), "4 Panes")
            
            # Tools
            self.shortcut_manager.register_shortcut("Ctrl+Shift+F", self.launch_file_finder, "File Finder")
            self.shortcut_manager.register_shortcut("Ctrl+Shift+D", self.launch_duplicate_finder, "Duplicate Finder")
            self.shortcut_manager.register_shortcut("Ctrl+Shift+S", self.launch_size_analyzer, "Size Analyzer")
            
        except Exception as e:
            self.logger.error(f"Error setting up enhanced shortcuts: {e}")
    
    # Additional tool launcher methods
    def launch_copy_move_sync(self):
        """Launch Copy/Move/Sync tool."""
        self._launch_tool("Copy/Move/Sync", "src.tools.file_operations.copy_move_sync_delete", "CopyMoveSyncDeleteWindow")
    
    def launch_disk_usage(self):
        """Launch Disk Usage analyzer."""
        self._launch_tool("Disk Usage", "src.tools.analysis.disk_usage", "DiskUsageGUI")
    
    def launch_file_integrity(self):
        """Launch File Integrity checker."""
        self._launch_tool("File Integrity", "src.tools.security.file_integrity", "FileIntegrityGUI")
    
    def launch_pdf_utilities(self):
        """Launch PDF Utilities."""
        self._launch_tool("PDF Utilities", "src.tools.pdf_tools.pdf_utilities", "PDFUtilitiesGUI")
    
    def launch_extract_links(self):
        """Launch Extract Links tool."""
        self._launch_tool("Extract Links", "src.tools.pdf_tools.extract_links", "ExtractLinksGUI")
    
    def launch_page_admin(self):
        """Launch Page Administration tool."""
        self._launch_tool("Page Administration", "src.tools.pdf_tools.page_admin", "PageAdminGUI")
    
    def launch_pdf_conversion(self):
        """Launch PDF Conversion tool."""
        self._launch_tool("PDF Conversion", "src.tools.pdf_tools.conversion", "PDFConversionGUI")
    
    def launch_network_test(self):
        """Launch Network Connectivity test."""
        self._launch_tool("Network Test", "src.tools.network.connectivity", "NetworkConnectivityGUI")
    
    def launch_file_transfer(self):
        """Launch File Transfer tool."""
        self._launch_tool("File Transfer", "src.tools.network.file_transfer", "FileTransferGUI")
    



    def launch_remote_access(self):
        """Launch Remote Access tool."""
        self._launch_tool("Remote Access", "src.tools.network.remote_access", "RemoteAccessGUI")


# For development and testing
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MultiPaneFileExplorer()
    window.show()
    
    sys.exit(app.exec_())