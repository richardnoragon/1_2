"""Advanced Folders Main Widget.

Enterprise-grade main widget implementing the comprehensive Advanced Folders interface.
Provides a unified interface for folder management, search, and file organization.

Architecture:
- Responsive layout with splitter-based design
- Component-based architecture with loose coupling
- Signal-based communication between components
- Enterprise-level error handling and logging
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import (QMutex, QSettings, Qt, QThread, QTimer,
                          QWaitCondition, pyqtSignal)
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QProgressBar,
                             QScrollArea, QSplitter, QStatusBar, QTabWidget,
                             QVBoxLayout, QWidget)

from ..core.folder_models import ValidationResult
from ..database import AdvancedFoldersDBManager
from ..models.folder_models import (ConfigurationManager, FileMetadata,
                                    FolderConfiguration, SearchParameter)
from ..repositories import RepositoryManager
from .menu_manager import AdvancedFoldersMenuManager
from .toolbar_manager import AdvancedFoldersToolbar


class AdvancedFoldersMainWidget(QMainWindow):
    """Enterprise-grade main widget for Advanced Folders functionality.
    
    Features:
    - Responsive layout with three-pane design
    - Real-time search and filtering
    - Advanced configuration management
    - Enterprise-level error handling
    - Performance monitoring and optimization
    - Accessibility compliance
    """
    
    # Signals for component communication
    folderSelected = pyqtSignal(str)  # folder_id
    searchRequested = pyqtSignal(str, dict)  # query, parameters
    configurationChanged = pyqtSignal(dict)  # configuration_data
    statusChanged = pyqtSignal(str, str)  # status_type, message
    errorOccurred = pyqtSignal(str, str, str)  # component, error_type, details
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the Advanced Folders main widget.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Initialize logging
        self.logger = logging.getLogger('AdvancedFolders.MainWidget')
        self.logger.info("Initializing Advanced Folders Main Widget")
        
        # Core components
        self.config_manager = ConfigurationManager()
        self.db_manager = AdvancedFoldersDBManager()
        self.repository_manager = RepositoryManager(self.db_manager)
        
        # UI Management components
        self.toolbar_manager = AdvancedFoldersToolbar(self)
        self.menu_manager = AdvancedFoldersMenuManager(self)
        
        # UI State Management
        self.ui_state = {
            'splitter_sizes': [],
            'selected_folder': None,
            'search_query': '',
            'view_mode': 'detailed',
            'sort_order': 'name_asc',
            'filter_settings': {}
        }
        
        # Performance monitoring
        self.performance_metrics = {
            'load_time': 0,
            'search_time': 0,
            'memory_usage': 0,
            'ui_responsiveness': 100
        }
        
        # Initialize UI components
        self._setup_ui()
        self._connect_signals()
        self._apply_styling()
        self._restore_settings()
        
        # Start performance monitoring
        self._setup_performance_monitoring()
        
        self.logger.info("Advanced Folders Main Widget initialized successfully")
    
    def _setup_ui(self):
        """Setup the main user interface with enterprise-grade layout."""
        self.logger.debug("Setting up main UI layout")
        
        # Configure main window
        self.setWindowTitle("Advanced Folders - Enterprise File Management")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main toolbar
        self._create_main_toolbar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create quick access bar
        self._create_quick_access_bar(main_layout)
        
        # Create main content area with splitter
        self._create_main_content_area(main_layout)
        
        # Create status bar
        self._create_status_bar()
        
        # Apply accessibility features
        self._setup_accessibility()
    
    def _create_menu_bar(self):
        """Create the main menu bar."""
        self.logger.debug("Creating menu bar")
        menu_bar = self.menu_manager.create_menu_bar(self)
        self.setMenuBar(menu_bar)
        
        # Connect menu signals
        self.menu_manager.menuItemTriggered.connect(self._handle_menu_action)
        self.menu_manager.contextMenuRequested.connect(self._handle_context_menu)
    
    def _create_main_toolbar(self):
        """Create the main toolbar."""
        self.logger.debug("Creating main toolbar")
        toolbar = self.toolbar_manager.create_main_toolbar(self)
        self.addToolBar(toolbar)
        
        # Connect toolbar signals
        self.toolbar_manager.actionTriggered.connect(self._handle_toolbar_action)
        self.toolbar_manager.contextChanged.connect(self._handle_context_change)
    
    def _create_quick_access_bar(self, parent_layout: QVBoxLayout):
        """Create the quick access bar.
        
        Args:
            parent_layout: Parent layout to add quick access bar to
        """
        self.logger.debug("Creating quick access bar")
        quick_access = self.toolbar_manager.create_quick_access_bar(self)
        parent_layout.addWidget(quick_access)
    
    def _create_toolbar_area(self, parent_layout: QVBoxLayout):
        """Create the comprehensive toolbar area.
        
        Args:
            parent_layout: Parent layout to add toolbar area to
        """
        # Toolbar container
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        toolbar_frame.setMaximumHeight(60)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        
        # Quick action buttons area
        self._create_quick_actions(toolbar_layout)
        
        # Search bar area
        self._create_search_bar(toolbar_layout)
        
        # View controls area
        self._create_view_controls(toolbar_layout)
        
        parent_layout.addWidget(toolbar_frame)
    
    def _create_quick_actions(self, parent_layout: QHBoxLayout):
        """Create quick action buttons.
        
        Args:
            parent_layout: Parent layout for quick actions
        """
        # Quick actions group
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_group)
        quick_layout.setSpacing(4)
        
        # Action buttons will be added by toolbar manager
        # Placeholder for now
        quick_label = QLabel("Quick Actions Area")
        quick_layout.addWidget(quick_label)
        
        parent_layout.addWidget(quick_group)
    
    def _create_search_bar(self, parent_layout: QHBoxLayout):
        """Create the advanced search bar.
        
        Args:
            parent_layout: Parent layout for search bar
        """
        # Search group
        search_group = QGroupBox("Search")
        search_layout = QHBoxLayout(search_group)
        search_layout.setSpacing(4)
        
        # Search components will be added by search manager
        # Placeholder for now
        search_label = QLabel("Advanced Search Area")
        search_layout.addWidget(search_label)
        
        parent_layout.addWidget(search_group)
    
    def _create_view_controls(self, parent_layout: QHBoxLayout):
        """Create view control buttons.
        
        Args:
            parent_layout: Parent layout for view controls
        """
        # View controls group
        view_group = QGroupBox("View")
        view_layout = QHBoxLayout(view_group)
        view_layout.setSpacing(4)
        
        # View controls will be added by view manager
        # Placeholder for now
        view_label = QLabel("View Controls Area")
        view_layout.addWidget(view_label)
        
        parent_layout.addWidget(view_group)
    
    def _create_main_content_area(self, parent_layout: QVBoxLayout):
        """Create the main content area with splitter layout.
        
        Args:
            parent_layout: Parent layout to add content area to
        """
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        
        # Left panel: Folder tree and filters
        self._create_left_panel()
        
        # Center panel: Search results
        self._create_center_panel()
        
        # Right panel: Preview and metadata
        self._create_right_panel()
        
        # Set initial splitter sizes (25%, 50%, 25%)
        self.main_splitter.setSizes([300, 600, 300])
        
        parent_layout.addWidget(self.main_splitter)
    
    def _create_left_panel(self):
        """Create the left panel with folder tree and filters."""
        # Left panel container
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(2, 2, 2, 2)
        left_layout.setSpacing(4)
        
        # Folder tree section
        self._create_folder_tree_section(left_layout)
        
        # Quick filters section
        self._create_quick_filters_section(left_layout)
        
        self.main_splitter.addWidget(left_widget)
    
    def _create_folder_tree_section(self, parent_layout: QVBoxLayout):
        """Create the folder tree section.
        
        Args:
            parent_layout: Parent layout for folder tree
        """
        # Folder tree group
        tree_group = QGroupBox("Configured Folders")
        tree_layout = QVBoxLayout(tree_group)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        
        # Folder tree will be added by folder tree view component
        # Placeholder for now
        tree_label = QLabel("Folder Tree View Area")
        tree_label.setAlignment(Qt.AlignCenter)
        tree_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 20px;
                border: 2px dashed #cccccc;
                background-color: #f8f8f8;
            }
        """)
        tree_layout.addWidget(tree_label)
        
        parent_layout.addWidget(tree_group)
    
    def _create_quick_filters_section(self, parent_layout: QVBoxLayout):
        """Create the quick filters section.
        
        Args:
            parent_layout: Parent layout for quick filters
        """
        # Quick filters group
        filters_group = QGroupBox("Quick Filters")
        filters_layout = QVBoxLayout(filters_group)
        filters_layout.setContentsMargins(4, 4, 4, 4)
        
        # Filters will be added by filter manager
        # Placeholder for now
        filters_label = QLabel("Quick Filters Area")
        filters_label.setAlignment(Qt.AlignCenter)
        filters_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 10px;
                border: 1px dashed #cccccc;
                background-color: #f8f8f8;
            }
        """)
        filters_layout.addWidget(filters_label)
        
        parent_layout.addWidget(filters_group)
    
    def _create_center_panel(self):
        """Create the center panel with search results."""
        # Center panel container
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(2, 2, 2, 2)
        center_layout.setSpacing(4)
        
        # Search results section
        self._create_search_results_section(center_layout)
        
        self.main_splitter.addWidget(center_widget)
    
    def _create_search_results_section(self, parent_layout: QVBoxLayout):
        """Create the search results section.
        
        Args:
            parent_layout: Parent layout for search results
        """
        # Search results group
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(4, 4, 4, 4)
        
        # Results header
        self._create_results_header(results_layout)
        
        # Results table will be added by search results table component
        # Placeholder for now
        results_label = QLabel("Search Results Table Area")
        results_label.setAlignment(Qt.AlignCenter)
        results_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 40px;
                border: 2px dashed #cccccc;
                background-color: #f8f8f8;
                font-size: 14px;
            }
        """)
        results_layout.addWidget(results_label)
        
        parent_layout.addWidget(results_group)
    
    def _create_results_header(self, parent_layout: QVBoxLayout):
        """Create the results header with stats and controls.
        
        Args:
            parent_layout: Parent layout for results header
        """
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        header_frame.setMaximumHeight(40)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # Results statistics
        self.results_stats_label = QLabel("Ready to search...")
        self.results_stats_label.setStyleSheet("font-weight: bold; color: #333333;")
        
        # Progress bar for search operations
        self.search_progress = QProgressBar()
        self.search_progress.setVisible(False)
        self.search_progress.setMaximumHeight(20)
        self.search_progress.setMaximumWidth(200)
        
        header_layout.addWidget(self.results_stats_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_progress)
        
        parent_layout.addWidget(header_frame)
    
    def _create_right_panel(self):
        """Create the right panel with preview and metadata."""
        # Right panel container
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(2, 2, 2, 2)
        right_layout.setSpacing(4)
        
        # Create tabbed interface for preview and metadata
        self._create_preview_tabs(right_layout)
        
        self.main_splitter.addWidget(right_widget)
    
    def _create_preview_tabs(self, parent_layout: QVBoxLayout):
        """Create the preview and metadata tabs.
        
        Args:
            parent_layout: Parent layout for preview tabs
        """
        # Tab widget
        self.preview_tabs = QTabWidget()
        self.preview_tabs.setTabPosition(QTabWidget.North)
        
        # Preview tab
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(4, 4, 4, 4)
        
        preview_label = QLabel("File Preview Area")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 20px;
                border: 1px dashed #cccccc;
                background-color: #f8f8f8;
            }
        """)
        preview_layout.addWidget(preview_label)
        
        self.preview_tabs.addTab(preview_widget, "Preview")
        
        # Metadata tab
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        metadata_layout.setContentsMargins(4, 4, 4, 4)
        
        metadata_label = QLabel("File Metadata Area")
        metadata_label.setAlignment(Qt.AlignCenter)
        metadata_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 20px;
                border: 1px dashed #cccccc;
                background-color: #f8f8f8;
            }
        """)
        metadata_layout.addWidget(metadata_label)
        
        self.preview_tabs.addTab(metadata_widget, "Metadata")
        
        # Statistics tab
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(4, 4, 4, 4)
        
        stats_label = QLabel("Statistics Area")
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 20px;
                border: 1px dashed #cccccc;
                background-color: #f8f8f8;
            }
        """)
        stats_layout.addWidget(stats_label)
        
        self.preview_tabs.addTab(stats_widget, "Statistics")
        
        parent_layout.addWidget(self.preview_tabs)
    
    def _create_status_bar(self):
        """Create the status bar with comprehensive information."""
        self.status_bar = self.statusBar()
        
        # Main status message
        self.status_bar.showMessage("Advanced Folders ready")
        
        # Performance indicator
        self.performance_label = QLabel("Performance: Excellent")
        self.performance_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.performance_label)
        
        # Memory usage indicator
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setStyleSheet("color: blue;")
        self.status_bar.addPermanentWidget(self.memory_label)
        
        # Connection status
        self.connection_label = QLabel("Database: Connected")
        self.connection_label.setStyleSheet("color: green;")
        self.status_bar.addPermanentWidget(self.connection_label)
    
    def _connect_signals(self):
        """Connect internal signals and slots."""
        self.logger.debug("Connecting internal signals")
        
        # Connect status change signal
        self.statusChanged.connect(self._handle_status_change)
        
        # Connect error signal
        self.errorOccurred.connect(self._handle_error)
        
        # Connect configuration change signal
        self.configurationChanged.connect(self._handle_configuration_change)
    
    def _handle_menu_action(self, item_id: str, data: Any):
        """Handle menu action triggered.
        
        Args:
            item_id: Menu item identifier
            data: Action data
        """
        self.logger.debug(f"Menu action triggered: {item_id}")
        
        # Map menu actions to methods
        action_map = {
            'new_folder': self._create_new_folder,
            'open_folder': self._open_folder_config,
            'save_config': self._save_configuration,
            'save_config_as': self._save_configuration_as,
            'import_config': self._import_configuration,
            'export_config': self._export_configuration,
            'exit': self.close,
            'quick_search': self._activate_quick_search,
            'advanced_search': self._open_advanced_search,
            'clear_search': self._clear_search_results,
            'refresh': self._refresh_current_view,
            'preferences': self._open_preferences,
            'help_contents': self._show_help,
            'about': self._show_about,
            'view_details': lambda: self._set_view_mode('details'),
            'view_list': lambda: self._set_view_mode('list'),
            'view_icons': lambda: self._set_view_mode('icons'),
        }
        
        if item_id in action_map:
            try:
                action_map[item_id]()
            except Exception as e:
                self.logger.error(f"Error executing menu action {item_id}: {e}")
                self.errorOccurred.emit("MenuAction", "ExecutionError", str(e))
        else:
            self.logger.warning(f"Unhandled menu action: {item_id}")
    
    def _handle_toolbar_action(self, action_id: str, data: Any):
        """Handle toolbar action triggered.
        
        Args:
            action_id: Action identifier
            data: Action data
        """
        self.logger.debug(f"Toolbar action triggered: {action_id}")
        
        # Toolbar actions can reuse menu action mapping
        self._handle_menu_action(action_id, data)
    
    def _handle_context_menu(self, context: str, position: Any):
        """Handle context menu request.
        
        Args:
            context: Context identifier
            position: Menu position
        """
        self.logger.debug(f"Context menu requested: {context}")
        # Context menu handling implementation would go here
    
    def _handle_context_change(self, context_name: str):
        """Handle toolbar context change.
        
        Args:
            context_name: New context name
        """
        self.logger.debug(f"Context changed to: {context_name}")
        self.statusChanged.emit("info", f"Context: {context_name}")
    
    # Placeholder methods for menu/toolbar actions
    def _create_new_folder(self):
        """Create new folder configuration."""
        self.logger.info("Creating new folder configuration")
        # Implementation placeholder
    
    def _open_folder_config(self):
        """Open folder configuration."""
        self.logger.info("Opening folder configuration")
        # Implementation placeholder
    
    def _save_configuration(self):
        """Save current configuration."""
        self.logger.info("Saving configuration")
        # Implementation placeholder
    
    def _save_configuration_as(self):
        """Save configuration as new file."""
        self.logger.info("Saving configuration as...")
        # Implementation placeholder
    
    def _import_configuration(self):
        """Import configuration from file."""
        self.logger.info("Importing configuration")
        # Implementation placeholder
    
    def _export_configuration(self):
        """Export configuration to file."""
        self.logger.info("Exporting configuration")
        # Implementation placeholder
    
    def _activate_quick_search(self):
        """Activate quick search."""
        self.logger.info("Activating quick search")
        # Implementation placeholder
    
    def _open_advanced_search(self):
        """Open advanced search dialog."""
        self.logger.info("Opening advanced search")
        # Implementation placeholder
    
    def _clear_search_results(self):
        """Clear search results."""
        self.logger.info("Clearing search results")
        # Implementation placeholder
    
    def _refresh_current_view(self):
        """Refresh current view."""
        self.logger.info("Refreshing current view")
        # Implementation placeholder
    
    def _open_preferences(self):
        """Open preferences dialog."""
        self.logger.info("Opening preferences")
        # Implementation placeholder
    
    def _show_help(self):
        """Show help documentation."""
        self.logger.info("Showing help")
        # Implementation placeholder
    
    def _show_about(self):
        """Show about dialog."""
        self.logger.info("Showing about dialog")
        # Implementation placeholder
    
    def _set_view_mode(self, mode: str):
        """Set view mode.
        
        Args:
            mode: View mode ('details', 'list', 'icons')
        """
        self.logger.info(f"Setting view mode to: {mode}")
        self.ui_state['view_mode'] = mode
        # Implementation placeholder
    
    def _apply_styling(self):
        """Apply enterprise-grade styling to the widget."""
        self.logger.debug("Applying enterprise styling")
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333333;
            }
            
            QSplitter::handle {
                background-color: #cccccc;
                width: 3px;
                height: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #999999;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #cccccc;
            }
        """)
    
    def _setup_accessibility(self):
        """Setup accessibility features for enterprise compliance."""
        self.logger.debug("Setting up accessibility features")
        
        # Set accessible names and descriptions
        self.setAccessibleName("Advanced Folders Main Interface")
        self.setAccessibleDescription("Enterprise file management and search interface")
        
        # Configure keyboard navigation
        self.setFocusPolicy(Qt.StrongFocus)
        
        # High contrast support
        if QApplication.instance().palette().color(QPalette.Window).lightness() < 128:
            # Dark theme detected, adjust styling
            self._apply_dark_theme_styling()
    
    def _apply_dark_theme_styling(self):
        """Apply dark theme styling for accessibility."""
        # Implementation would include dark theme CSS
        pass
    
    def _restore_settings(self):
        """Restore UI settings from previous session."""
        self.logger.debug("Restoring UI settings")
        
        settings = QSettings("RFU", "AdvancedFolders")
        
        # Restore window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore splitter sizes
        splitter_sizes = settings.value("splitter_sizes")
        if splitter_sizes:
            # Convert to integers (QSettings may store as strings)
            sizes = [int(size) for size in splitter_sizes if size]
            if len(sizes) == 3:
                self.main_splitter.setSizes(sizes)
        
        # Restore UI state
        ui_state = settings.value("ui_state")
        if ui_state:
            self.ui_state.update(ui_state)
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and optimization."""
        self.logger.debug("Setting up performance monitoring")
        
        # Performance monitoring timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._update_performance_metrics)
        self.performance_timer.start(5000)  # Update every 5 seconds
    
    def _update_performance_metrics(self):
        """Update performance metrics display."""
        try:
            import psutil

            # Get current process
            process = psutil.Process()
            
            # Update memory usage
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.setText(f"Memory: {memory_mb:.1f} MB")
            
            # Update performance status based on memory usage
            if memory_mb < 100:
                self.performance_label.setText("Performance: Excellent")
                self.performance_label.setStyleSheet("color: green; font-weight: bold;")
            elif memory_mb < 300:
                self.performance_label.setText("Performance: Good")
                self.performance_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.performance_label.setText("Performance: Monitor")
                self.performance_label.setStyleSheet("color: red; font-weight: bold;")
                
        except ImportError:
            # psutil not available
            self.memory_label.setText("Memory: N/A")
    
    def _handle_status_change(self, status_type: str, message: str):
        """Handle status change signals.
        
        Args:
            status_type: Type of status change
            message: Status message
        """
        self.logger.debug(f"Status change: {status_type} - {message}")
        self.status_bar.showMessage(message)
    
    def _handle_error(self, component: str, error_type: str, details: str):
        """Handle error signals.
        
        Args:
            component: Component that generated the error
            error_type: Type of error
            details: Error details
        """
        self.logger.error(f"Error in {component}: {error_type} - {details}")
        
        # Show error in status bar
        self.status_bar.showMessage(f"Error in {component}: {error_type}")
        
        # For critical errors, show message box
        if error_type.lower() in ['critical', 'fatal']:
            QMessageBox.critical(
                self, 
                f"Critical Error in {component}",
                f"Error Type: {error_type}\n\nDetails: {details}"
            )
    
    def _handle_configuration_change(self, configuration_data: dict):
        """Handle configuration change signals.
        
        Args:
            configuration_data: New configuration data
        """
        self.logger.info("Configuration changed")
        # Implementation would update UI based on new configuration
        pass
    
    def save_settings(self):
        """Save current UI settings."""
        self.logger.debug("Saving UI settings")
        
        settings = QSettings("RFU", "AdvancedFolders")
        
        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())
        
        # Save splitter sizes
        settings.setValue("splitter_sizes", self.main_splitter.sizes())
        
        # Save UI state
        settings.setValue("ui_state", self.ui_state)
    
    def closeEvent(self, event):
        """Handle widget close event."""
        self.logger.info("Advanced Folders Main Widget closing")
        
        # Save settings
        self.save_settings()
        
        # Cleanup toolbar and menu managers
        if hasattr(self, 'toolbar_manager'):
            self.toolbar_manager.cleanup()
        
        if hasattr(self, 'menu_manager'):
            self.menu_manager.cleanup()
        
        # Stop timers
        if hasattr(self, 'performance_timer'):
            self.performance_timer.stop()
        
        # Emit status change
        self.statusChanged.emit("shutdown", "Advanced Folders shutting down")
        
        event.accept()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        return self.performance_metrics.copy()
    
    def get_ui_state(self) -> Dict[str, Any]:
        """Get current UI state.
        
        Returns:
            Dictionary containing UI state
        """
        return self.ui_state.copy()
    
    def set_folder_selection(self, folder_id: str):
        """Set the selected folder.
        
        Args:
            folder_id: ID of folder to select
        """
        self.ui_state['selected_folder'] = folder_id
        self.folderSelected.emit(folder_id)
    
    def perform_search(self, query: str, parameters: dict):
        """Perform a search operation.
        
        Args:
            query: Search query string
            parameters: Search parameters
        """
        self.ui_state['search_query'] = query
        self.searchRequested.emit(query, parameters)
    
    def update_results_stats(self, count: int, search_time: float):
        """Update the results statistics display.
        
        Args:
            count: Number of results found
            search_time: Time taken for search
        """
        if count == 0:
            self.results_stats_label.setText("No results found")
        elif count == 1:
            self.results_stats_label.setText(f"1 result found in {search_time:.2f}s")
        else:
            self.results_stats_label.setText(
                f"{count:,} results found in {search_time:.2f}s"
            )