"""
Pane Management System for RFU Multi-Pane File Explorer
Advanced Layout Engine with Dynamic Creation and Persistence

This module provides comprehensive pane management with:

- Dynamic pane creation, destruction, and layout persistence
- Advanced layout algorithms (grid, tabbed, split, floating)
- Pane synchronization and state management
- Layout templates and presets
- Drag-and-drop pane operations
- Memory-efficient pane lifecycle management
- Cross-pane communication and coordination
- Accessibility support and keyboard navigation

Layout Features:
- Flexible grid-based layouts with resizable panes
- Tabbed pane groups with tab reordering
- Split layouts (horizontal, vertical, nested)
- Floating window support
- Picture-in-picture mode for file previews
- Custom layout templates and saved arrangements
- Dynamic layout adaptation for different screen sizes

Management Features:
- Pane state persistence across sessions
- Layout serialization and restoration
- Pane focus management and navigation
- Cross-pane drag-and-drop operations
- Global pane coordination and messaging
- Performance monitoring and optimization
- Memory usage tracking and cleanup

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import json
import logging
import threading
import time
import uuid
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (Any, Callable, ClassVar, Dict, Iterator, List, Optional,
                    Set, Tuple, Type, Union)

try:
    from PyQt5.QtCore import (QEasingCurve, QMimeData, QObject, QPoint,
                              QPropertyAnimation, QRect, QSize, Qt, QTimer,
                              pyqtSignal)
    from PyQt5.QtGui import QColor, QDrag, QFont, QPainter, QPixmap
    from PyQt5.QtWidgets import (QApplication, QDockWidget, QFrame,
                                 QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                                 QMainWindow, QScrollArea, QSizePolicy,
                                 QSplitter, QStackedWidget, QTabWidget,
                                 QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                                 QWidget)
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Fallback definitions
    class QObject:
        pass

    class QWidget:
        pass

    class QFrame:
        pass

    class QSplitter:
        pass

    class QTabWidget:
        pass

    class QTreeWidget:
        pass

    class QTreeWidgetItem:
        pass

    class QLineEdit:
        pass

    class QFont:
        pass

    class QColor:
        pass

    def pyqtSignal(*args):
        def dummy_signal(*signal_args):
            pass
        return dummy_signal


class PaneType(Enum):
    """Pane type enumeration."""
    FILE_EXPLORER = auto()
    PREVIEW = auto()
    TERMINAL = auto()
    PROPERTIES = auto()
    BOOKMARKS = auto()
    TOOLS = auto()
    SEARCH_RESULTS = auto()
    CUSTOM = auto()


class LayoutType(Enum):
    """Layout type enumeration."""
    GRID = auto()
    HORIZONTAL_SPLIT = auto()
    VERTICAL_SPLIT = auto()
    TABBED = auto()
    FLOATING = auto()
    PICTURE_IN_PICTURE = auto()


class PaneState(Enum):
    """Pane state enumeration."""
    ACTIVE = auto()
    INACTIVE = auto()
    MINIMIZED = auto()
    MAXIMIZED = auto()
    FLOATING = auto()
    HIDDEN = auto()


class DockPosition(Enum):
    """Dock position enumeration."""
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    CENTER = auto()


@dataclass
class PaneConfiguration:
    """Pane configuration and metadata."""
    
    # Basic pane information
    pane_id: str
    pane_type: PaneType
    title: str
    
    # Layout properties
    layout_type: LayoutType = LayoutType.GRID
    dock_position: DockPosition = DockPosition.CENTER
    size_hint: Tuple[int, int] = (300, 200)
    minimum_size: Tuple[int, int] = (100, 100)
    maximum_size: Tuple[int, int] = (9999, 9999)
    
    # State properties
    state: PaneState = PaneState.INACTIVE
    is_closable: bool = True
    is_resizable: bool = True
    is_movable: bool = True
    is_floating: bool = False
    
    # Visual properties
    background_color: str = "#FFFFFF"
    border_color: str = "#CCCCCC"
    border_width: int = 1
    opacity: float = 1.0
    
    # Behavior properties
    auto_hide: bool = False
    auto_focus: bool = True
    accepts_drops: bool = True
    provides_drag: bool = True
    
    # Custom properties
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    
    # Persistence properties
    persistent: bool = True
    save_state: bool = True
    restore_geometry: bool = True
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.pane_id:
            self.pane_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pane_id': self.pane_id,
            'pane_type': self.pane_type.name,
            'title': self.title,
            'layout_type': self.layout_type.name,
            'dock_position': self.dock_position.name,
            'size_hint': self.size_hint,
            'minimum_size': self.minimum_size,
            'maximum_size': self.maximum_size,
            'state': self.state.name,
            'is_closable': self.is_closable,
            'is_resizable': self.is_resizable,
            'is_movable': self.is_movable,
            'is_floating': self.is_floating,
            'background_color': self.background_color,
            'border_color': self.border_color,
            'border_width': self.border_width,
            'opacity': self.opacity,
            'auto_hide': self.auto_hide,
            'auto_focus': self.auto_focus,
            'accepts_drops': self.accepts_drops,
            'provides_drag': self.provides_drag,
            'custom_properties': self.custom_properties,
            'persistent': self.persistent,
            'save_state': self.save_state,
            'restore_geometry': self.restore_geometry
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaneConfiguration':
        """Create from dictionary."""
        # Convert enum strings back to enums
        pane_type = PaneType[data['pane_type']]
        layout_type = LayoutType[data.get('layout_type', 'GRID')]
        dock_position = DockPosition[data.get('dock_position', 'CENTER')]
        state = PaneState[data.get('state', 'INACTIVE')]
        
        return cls(
            pane_id=data['pane_id'],
            pane_type=pane_type,
            title=data['title'],
            layout_type=layout_type,
            dock_position=dock_position,
            size_hint=tuple(data.get('size_hint', (300, 200))),
            minimum_size=tuple(data.get('minimum_size', (100, 100))),
            maximum_size=tuple(data.get('maximum_size', (9999, 9999))),
            state=state,
            is_closable=data.get('is_closable', True),
            is_resizable=data.get('is_resizable', True),
            is_movable=data.get('is_movable', True),
            is_floating=data.get('is_floating', False),
            background_color=data.get('background_color', '#FFFFFF'),
            border_color=data.get('border_color', '#CCCCCC'),
            border_width=data.get('border_width', 1),
            opacity=data.get('opacity', 1.0),
            auto_hide=data.get('auto_hide', False),
            auto_focus=data.get('auto_focus', True),
            accepts_drops=data.get('accepts_drops', True),
            provides_drag=data.get('provides_drag', True),
            custom_properties=data.get('custom_properties', {}),
            persistent=data.get('persistent', True),
            save_state=data.get('save_state', True),
            restore_geometry=data.get('restore_geometry', True)
        )


@dataclass
class LayoutConfiguration:
    """Layout configuration and metadata."""
    
    # Basic layout information
    layout_id: str
    name: str
    description: str = ""
    
    # Layout structure
    layout_type: LayoutType = LayoutType.GRID
    rows: int = 1
    columns: int = 1
    splitter_sizes: List[int] = field(default_factory=list)
    
    # Pane arrangements
    pane_positions: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    pane_configurations: List[PaneConfiguration] = field(default_factory=list)
    
    # Layout properties
    allow_floating: bool = True
    allow_tabbed: bool = True
    auto_arrange: bool = False
    save_geometry: bool = True
    
    # Visual properties
    spacing: int = 5
    margins: Tuple[int, int, int, int] = (5, 5, 5, 5)  # left, top, right, bottom
    
    # Metadata
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.layout_id:
            self.layout_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'layout_id': self.layout_id,
            'name': self.name,
            'description': self.description,
            'layout_type': self.layout_type.name,
            'rows': self.rows,
            'columns': self.columns,
            'splitter_sizes': self.splitter_sizes,
            'pane_positions': self.pane_positions,
            'pane_configurations': [config.to_dict() for config in self.pane_configurations],
            'allow_floating': self.allow_floating,
            'allow_tabbed': self.allow_tabbed,
            'auto_arrange': self.auto_arrange,
            'save_geometry': self.save_geometry,
            'spacing': self.spacing,
            'margins': self.margins,
            'created_time': self.created_time.isoformat(),
            'modified_time': self.modified_time.isoformat(),
            'version': self.version,
            'author': self.author,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayoutConfiguration':
        """Create from dictionary."""
        layout_type = LayoutType[data.get('layout_type', 'GRID')]
        
        pane_configs = [
            PaneConfiguration.from_dict(config_data) 
            for config_data in data.get('pane_configurations', [])
        ]
        
        return cls(
            layout_id=data['layout_id'],
            name=data['name'],
            description=data.get('description', ''),
            layout_type=layout_type,
            rows=data.get('rows', 1),
            columns=data.get('columns', 1),
            splitter_sizes=data.get('splitter_sizes', []),
            pane_positions=data.get('pane_positions', {}),
            pane_configurations=pane_configs,
            allow_floating=data.get('allow_floating', True),
            allow_tabbed=data.get('allow_tabbed', True),
            auto_arrange=data.get('auto_arrange', False),
            save_geometry=data.get('save_geometry', True),
            spacing=data.get('spacing', 5),
            margins=tuple(data.get('margins', (5, 5, 5, 5))),
            created_time=datetime.fromisoformat(data.get('created_time', datetime.now().isoformat())),
            modified_time=datetime.fromisoformat(data.get('modified_time', datetime.now().isoformat())),
            version=data.get('version', '1.0'),
            author=data.get('author', ''),
            tags=data.get('tags', [])
        )


class BasePaneWidget(QFrame if QT_AVAILABLE else object):
    """
    Base pane widget with common functionality.
    
    Provides standard pane interface and behavior for all pane types.
    """
    
    # Signals for pane events
    paneActivated = pyqtSignal(str) if QT_AVAILABLE else None
    paneDeactivated = pyqtSignal(str) if QT_AVAILABLE else None
    paneClosed = pyqtSignal(str) if QT_AVAILABLE else None
    paneModified = pyqtSignal(str) if QT_AVAILABLE else None
    paneStateChanged = pyqtSignal(str, str) if QT_AVAILABLE else None
    
    def __init__(self, config: PaneConfiguration, parent=None):
        """
        Initialize base pane widget.
        
        Args:
            config: Pane configuration
            parent: Parent widget
        """
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.config = config
        self.logger = logging.getLogger('RFU.FileExplorer.BasePaneWidget')
        
        # Pane state
        self._is_active = False
        self._is_modified = False
        self._creation_time = datetime.now()
        self._last_access_time = datetime.now()
        
        # Widget references
        self._content_widget: Optional[QWidget] = None
        self._title_widget: Optional[QWidget] = None
        
        # Event tracking
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        if QT_AVAILABLE:
            self._setup_ui()
        
        self.logger.debug(f"Created pane widget: {self.config.pane_id}")
    
    def _setup_ui(self):
        """Setup the pane user interface."""
        if not QT_AVAILABLE:
            return
        
        # Set basic properties
        self.setObjectName(f"pane_{self.config.pane_id}")
        self.setWindowTitle(self.config.title)
        
        # Apply visual styling
        self._apply_styling()
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create title bar if needed
        if self._should_show_title():
            self._title_widget = self._create_title_widget()
            layout.addWidget(self._title_widget)
        
        # Create content area
        self._content_widget = self._create_content_widget()
        layout.addWidget(self._content_widget, 1)  # Give content area stretch factor
        
        # Set size policies
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(*self.config.minimum_size)
        self.setMaximumSize(*self.config.maximum_size)
    
    def _apply_styling(self):
        """Apply visual styling to the pane."""
        if not QT_AVAILABLE:
            return
        
        style = f"""
        QFrame#{self.objectName()} {{
            background-color: {self.config.background_color};
            border: {self.config.border_width}px solid {self.config.border_color};
            border-radius: 3px;
        }}
        """
        self.setStyleSheet(style)
    
    def _should_show_title(self) -> bool:
        """Check if title bar should be shown."""
        return True  # Can be overridden by subclasses
    
    def _create_title_widget(self) -> QWidget:
        """Create title bar widget."""
        if not QT_AVAILABLE:
            return None
        
        title_widget = QFrame()
        title_widget.setFixedHeight(30)
        title_widget.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
        """)
        
        layout = QHBoxLayout(title_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # Title label
        title_label = QLabel(self.config.title)
        title_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return title_widget
    
    def _create_content_widget(self) -> QWidget:
        """Create content widget. Override in subclasses."""
        if not QT_AVAILABLE:
            return None
        
        content = QLabel("Base Pane Content")
        content.setAlignment(Qt.AlignCenter)
        return content
    
    @property
    def pane_id(self) -> str:
        """Get pane ID."""
        return self.config.pane_id
    
    @property
    def pane_type(self) -> PaneType:
        """Get pane type."""
        return self.config.pane_type
    
    @property
    def is_active(self) -> bool:
        """Check if pane is active."""
        return self._is_active
    
    @property
    def is_modified(self) -> bool:
        """Check if pane has been modified."""
        return self._is_modified
    
    def activate(self):
        """Activate the pane."""
        if not self._is_active:
            self._is_active = True
            self._last_access_time = datetime.now()
            self.config.state = PaneState.ACTIVE
            
            if QT_AVAILABLE and self.paneActivated:
                self.paneActivated.emit(self.pane_id)
            
            self._on_activated()
    
    def deactivate(self):
        """Deactivate the pane."""
        if self._is_active:
            self._is_active = False
            self.config.state = PaneState.INACTIVE
            
            if QT_AVAILABLE and self.paneDeactivated:
                self.paneDeactivated.emit(self.pane_id)
            
            self._on_deactivated()
    
    def close_pane(self) -> bool:
        """
        Close the pane.
        
        Returns:
            bool: True if pane was closed successfully
        """
        if not self.config.is_closable:
            return False
        
        if self._can_close():
            if QT_AVAILABLE and self.paneClosed:
                self.paneClosed.emit(self.pane_id)
            
            self._on_closed()
            return True
        
        return False
    
    def set_modified(self, modified: bool = True):
        """
        Set pane modified state.
        
        Args:
            modified: Whether pane is modified
        """
        if self._is_modified != modified:
            self._is_modified = modified
            
            if QT_AVAILABLE and self.paneModified:
                self.paneModified.emit(self.pane_id)
            
            self._update_title_display()
    
    def set_state(self, state: PaneState):
        """
        Set pane state.
        
        Args:
            state: New pane state
        """
        old_state = self.config.state
        self.config.state = state
        
        if QT_AVAILABLE and self.paneStateChanged:
            self.paneStateChanged.emit(self.pane_id, state.name)
        
        self._on_state_changed(old_state, state)
    
    def _update_title_display(self):
        """Update title display to reflect modified state."""
        if not QT_AVAILABLE or not self._title_widget:
            return
        
        title = self.config.title
        if self._is_modified:
            title += "*"
        
        # Find title label and update text
        for child in self._title_widget.findChildren(QLabel):
            child.setText(title)
            break
    
    def _can_close(self) -> bool:
        """Check if pane can be closed. Override in subclasses."""
        return True
    
    def _on_activated(self):
        """Called when pane is activated. Override in subclasses."""
        pass
    
    def _on_deactivated(self):
        """Called when pane is deactivated. Override in subclasses."""
        pass
    
    def _on_closed(self):
        """Called when pane is closed. Override in subclasses."""
        pass
    
    def _on_state_changed(self, old_state: PaneState, new_state: PaneState):
        """Called when pane state changes. Override in subclasses."""
        pass
    
    def get_state_data(self) -> Dict[str, Any]:
        """Get pane state data for persistence. Override in subclasses."""
        return {
            'pane_id': self.pane_id,
            'is_modified': self.is_modified,
            'creation_time': self._creation_time.isoformat(),
            'last_access_time': self._last_access_time.isoformat()
        }
    
    def restore_state_data(self, data: Dict[str, Any]):
        """Restore pane state data from persistence. Override in subclasses."""
        self._is_modified = data.get('is_modified', False)
        
        try:
            self._creation_time = datetime.fromisoformat(data.get('creation_time', datetime.now().isoformat()))
            self._last_access_time = datetime.fromisoformat(data.get('last_access_time', datetime.now().isoformat()))
        except ValueError:
            pass


class ToolsPaneWidget(BasePaneWidget):
    """
    Tools pane widget displaying all RFU tool categories and utilities.
    
    Provides comprehensive access to all RFU tools organized by category
    with search functionality and keyboard navigation support.
    """
    
    # Signals for tool events
    toolLaunched = pyqtSignal(str, str) if QT_AVAILABLE else None
    categoryExpanded = pyqtSignal(str) if QT_AVAILABLE else None
    toolSelected = pyqtSignal(str) if QT_AVAILABLE else None
    
    def __init__(self, config: PaneConfiguration, parent=None):
        """Initialize tools pane widget."""
        # Initialize tool categories BEFORE calling super().__init__()
        # because super().__init__() will call _setup_ui() which needs tool_categories
        self.tool_categories = {
            "Analysis": [
                ("Checksum Calculator", "Calculate and verify file checksums", "src.tools.analysis.check_sum"),
                ("Duplicate Finder", "Find and remove duplicate files", "src.tools.analysis.find_duplicate_files"),
                ("Empty Folders", "Find and clean empty folders", "src.tools.analysis.empty_folders"),
                ("Size Analyzer", "Analyze disk space usage", "src.tools.analysis.size_analyzer"),
            ],
            "File Management": [
                ("File Finder", "Search and find files by criteria", "src.tools.file_management.file_finder"),
                ("Catalog Tool", "Create and manage file catalogs", "src.tools.file_management.catalog_tool"),
                ("File Renamer", "Batch rename files and folders", "src.tools.file_management.rename"),
                ("File Organizer", "Organize files by type/date", "src.tools.file_management.organize"),
                ("Advanced Folders", "Smart folder monitoring and search", "src.tools.file_management.advanced_folders"),
            ],
            "File Operations": [
                ("Copy/Move/Sync/Delete", "Advanced file operations", "src.tools.file_operations.cmsd.cmsd_logic"),
                ("File Splitter", "Split large files or join parts", "src.tools.file_operations.file_splitter_logic"),
                ("Enhanced Editor", "Text editor with syntax highlighting", "src.tools.file_operations.enhanced_editor"),
                ("File Touch", "Modify file timestamps", "src.tools.file_operations.file_touch"),
                ("Compression Tools", "Archive and extract files", "src.tools.file_operations.compression"),
                ("Secure Delete", "Securely delete sensitive files", "src.tools.file_operations.secure_delete"),
                ("Synchronizer", "Synchronize directories", "src.tools.file_operations.synchronizer"),
            ],
            "Metadata": [
                ("Image Metadata Editor", "View and edit image metadata", "src.tools.metadata.image_metadata_logic"),
                ("Office Metadata Editor", "Edit document metadata", "src.tools.metadata.office_meta_data_editor"),
            ],
            "Network": [
                ("Network Connectivity", "Check network connectivity and diagnostics", "src.tools.network.network_connectivity"),
                ("Network Scanner", "Scan network for devices and services", "src.tools.network.network_scanner"),
                ("Network Transfer", "Transfer files between RFU clients", "src.tools.network.network_transfer"),
                ("Bookmark Manager", "Cross-platform bookmark manager", "src.tools.network.bookmark_manager"),
            ],
            "PDF Tools": [
                ("PDF Basic Operations", "Basic PDF operations", "src.tools.pdf_tools.pdf_basic_operations"),
                ("PDF Content Extraction", "Extract content from PDFs", "src.tools.pdf_tools.pdf_content_extraction"),
                ("PDF Conversion", "Convert PDF files", "src.tools.pdf_tools.pdf_conversion"),
                ("PDF Enhancements", "Enhance PDF documents", "src.tools.pdf_tools.pdf_enhancements"),
                ("PDF Security", "PDF security operations", "src.tools.pdf_tools.pdf_security"),
                ("PDF View Analysis", "Analyze PDF structure", "src.tools.pdf_tools.pdf_view_analysis"),
                ("PDF Batch Processor", "Process PDFs in batch", "src.tools.pdf_tools.batch_processor"),
            ],
            "Privacy": [
                ("Privacy Cleaner", "Clean privacy-sensitive data", "src.tools.privacy.privacy_tools"),
                ("Data Anonymizer", "Anonymize sensitive file data", "src.tools.privacy.data_anonymizer"),
                ("Simple Privacy Hub", "Simple privacy tools interface", "src.tools.privacy.privacy_tools_simple"),
            ],
            "Security": [
                ("Encrypt/Decrypt", "File encryption and decryption", "src.tools.security.en_and_decrypt"),
                ("Secure Delete", "Permanently delete sensitive files", "src.tools.security.secure_delete"),
                ("Password Generator", "Generate secure passwords", "src.tools.security.simple_password_generator"),
                ("Security Scanner", "Basic security scanning", "src.tools.security.simple_security_scanner"),
            ],
            "System": [
                ("System Diagnostics", "Comprehensive system analysis", "src.tools.system.diagnostics_monitoring.system_diagnostics_gui"),
                ("System Cleanup", "Clean temporary and unnecessary files", "src.tools.system.system_cleanup"),
                ("Software Maintenance", "Update and maintain installed software", "src.tools.system.software_maintenance"),
                ("Permissions Editor", "Manage file and folder permissions", "src.tools.system.permissions_editor"),
                ("Process Monitor", "Monitor system processes", "src.tools.system.simple_process_monitor"),
                ("System Info", "Display system information", "src.tools.system.simple_system_info"),
            ]
        }
        
        # Widget references
        self.tools_tree = None
        self.search_widget = None
        self.status_label = None
        
        # Now call super().__init__() which will call _setup_ui()
        super().__init__(config, parent)
        
        self.logger.debug("ToolsPaneWidget initialized")
    
    def _should_show_title(self) -> bool:
        """Tools pane should show title."""
        return True
    
    def _create_content_widget(self) -> QWidget:
        """Create tools pane content widget."""
        if not QT_AVAILABLE:
            return None
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Search box for tool filtering
        self.search_widget = self._create_search_widget()
        layout.addWidget(self.search_widget)
        
        # Tools tree widget
        self.tools_tree = self._create_tools_tree()
        layout.addWidget(self.tools_tree, 1)
        
        # Status label
        self.status_label = QLabel("Tools Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666;
                padding: 3px;
                background-color: #e9ecef;
                border-radius: 2px;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.status_label)
        
        return content_widget
    
    def _create_search_widget(self) -> QWidget:
        """Create search widget for tool filtering."""
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit
        
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        
        layout = QHBoxLayout(search_frame)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(5)
        
        # Search label
        search_label = QLabel("🔍")
        search_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tools...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #495057;
                font-size: 11px;
            }
        """)
        self.search_input.textChanged.connect(self._filter_tools)
        layout.addWidget(self.search_input, 1)
        
        return search_frame
    
    def _create_tools_tree(self) -> QWidget:
        """Create tools tree widget with all RFU tool categories."""
        from PyQt5.QtWidgets import QTreeWidget
        
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["Tools"])
        tools_tree.setAlternatingRowColors(True)
        # We'll handle indicators manually
        tools_tree.setRootIsDecorated(False)
        tools_tree.setExpandsOnDoubleClick(False)  # Custom expand handling
        tools_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #ddd;
                font-size: 11px;
                selection-background-color: #007ACC;
                selection-color: white;
                outline: none;
            }
            QTreeWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 24px;
            }
            QTreeWidget::item:selected {
                background-color: #007ACC;
                color: white;
                border-radius: 3px;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
                border-radius: 3px;
            }
            QTreeWidget::item:has-children {
                font-weight: bold;
            }
            
            /* Disable default branch decorations */
            QTreeWidget::branch {
                background: transparent;
                border: none;
                width: 0px;
                margin: 0px;
            }
        """)
        
        # Populate tools tree with custom indicators
        self._populate_tools_tree_with_indicators(tools_tree)
        
        # Connect signals for enhanced click handling
        tools_tree.itemClicked.connect(self._on_tree_item_clicked)
        tools_tree.itemDoubleClicked.connect(self._on_tool_activated)
        tools_tree.itemExpanded.connect(self._on_category_state_changed)
        tools_tree.itemCollapsed.connect(self._on_category_state_changed)
        
        # Enable keyboard navigation
        tools_tree.setFocusPolicy(Qt.StrongFocus)
        
        return tools_tree
    
    def _populate_tools_tree_with_indicators(self, tree_widget):
        """Populate tools tree with custom expand/collapse indicators."""
        tree_widget.clear()
        
        total_tools = 0
        
        for category_name, tools in self.tool_categories.items():
            # Create category item with right arrow (collapsed state)
            category_display = f"▶ 📁 {category_name}"
            category_item = QTreeWidgetItem([category_display])
            category_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            category_item.setForeground(0, QColor("#2c3e50"))
            
            # Store original category name and indicator state
            category_data = {
                "type": "category",
                "name": category_name,
                "original_text": f"📁 {category_name}",
                "is_expanded": False
            }
            category_item.setData(0, Qt.UserRole, category_data)
            
            # Add tools to category
            for tool_name, tool_description, tool_module in tools:
                tool_item = QTreeWidgetItem([f"    🔧 {tool_name}"])
                tool_item.setFont(0, QFont("Arial", 9))
                tool_item.setForeground(0, QColor("#495057"))
                tool_item.setToolTip(0, tool_description)
                tool_item.setData(0, Qt.UserRole, {
                    "type": "tool",
                    "name": tool_name,
                    "category": category_name,
                    "description": tool_description,
                    "module": tool_module
                })
                
                category_item.addChild(tool_item)
                total_tools += 1
            
            tree_widget.addTopLevelItem(category_item)
            
            # Expand popular categories by default and update indicators
            popular_categories = ["File Management", "File Operations",
                                  "Analysis"]
            if category_name in popular_categories:
                self._expand_category_with_animation(
                    category_item, tree_widget)
        
        # Update status
        if hasattr(self, 'status_label') and self.status_label:
            categories_count = len(self.tool_categories)
            status_text = f"{categories_count} categories, {total_tools} tools"
            self.status_label.setText(status_text)
    
    def _on_tree_item_clicked(self, item, column):
        """Handle tree item clicks with smart expand/collapse logic."""
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        
        if item_type == "category":
            # Toggle category expansion on any click
            tree_widget = item.treeWidget()
            if item.isExpanded():
                self._collapse_category_with_animation(item, tree_widget)
            else:
                self._expand_category_with_animation(item, tree_widget)
        
        # Call the original selection handler
        self._on_tool_selected(item, column)
    
    def _expand_category_with_animation(self, category_item, tree_widget):
        """Expand category with visual indicator update and animation."""
        if not category_item or not tree_widget:
            return
        
        item_data = category_item.data(0, Qt.UserRole)
        if not item_data or item_data.get("type") != "category":
            return
        
        # Update indicator to down arrow
        original_text = item_data.get("original_text", "")
        expanded_display = f"▼ {original_text}"
        category_item.setText(0, expanded_display)
        
        # Update data
        item_data["is_expanded"] = True
        category_item.setData(0, Qt.UserRole, item_data)
        
        # Add visual feedback with color animation
        category_item.setForeground(0, QColor("#007ACC"))
        
        # Expand the item with animation-like effect
        if QT_AVAILABLE:
            # Create a smooth expansion effect
            category_item.setExpanded(True)
            
            # Animate child items appearing
            child_count = category_item.childCount()
            for i in range(child_count):
                child_item = category_item.child(i)
                if child_item:
                    # Add a subtle delay for each child
                    QTimer.singleShot(i * 50, lambda ci=child_item:
                                      self._animate_child_appearance(ci))
        else:
            category_item.setExpanded(True)
        
        # Emit category expanded signal
        if QT_AVAILABLE and self.categoryExpanded:
            category_name = item_data.get("name")
            self.categoryExpanded.emit(category_name)
    
    def _animate_child_appearance(self, child_item):
        """Animate child item appearance with subtle fade-in effect."""
        if not child_item or not QT_AVAILABLE:
            return
        
        # Create a temporary highlight effect
        original_color = child_item.foreground(0)
        highlight_color = QColor("#007ACC")
        
        # Brief highlight animation
        child_item.setForeground(0, highlight_color)
        QTimer.singleShot(200, lambda: child_item.setForeground(
            0, original_color))
    
    def _collapse_category_with_animation(self, category_item, tree_widget):
        """Collapse category with visual indicator update and animation."""
        if not category_item or not tree_widget:
            return
        
        item_data = category_item.data(0, Qt.UserRole)
        if not item_data or item_data.get("type") != "category":
            return
        
        # Animate child items disappearing before collapse
        if QT_AVAILABLE:
            child_count = category_item.childCount()
            for i in range(child_count):
                child_item = category_item.child(i)
                if child_item:
                    # Add fade-out effect for children
                    fade_color = QColor("#cccccc")
                    child_item.setForeground(0, fade_color)
        
        # Small delay for animation effect
        if QT_AVAILABLE:
            QTimer.singleShot(100, lambda:
                              self._complete_collapse(category_item,
                                                      item_data))
        else:
            self._complete_collapse(category_item, item_data)
    
    def _complete_collapse(self, category_item, item_data):
        """Complete the collapse animation."""
        # Update indicator to right arrow
        original_text = item_data.get("original_text", "")
        collapsed_display = f"▶ {original_text}"
        category_item.setText(0, collapsed_display)
        
        # Update data
        item_data["is_expanded"] = False
        category_item.setData(0, Qt.UserRole, item_data)
        
        # Collapse the item
        category_item.setExpanded(False)
        
        # Reset visual feedback
        category_item.setForeground(0, QColor("#2c3e50"))
        
        # Reset child item colors
        child_count = category_item.childCount()
        for i in range(child_count):
            child_item = category_item.child(i)
            if child_item:
                child_item.setForeground(0, QColor("#495057"))
    
    def _on_category_state_changed(self, item):
        """Handle category expansion/collapse state changes."""
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data or item_data.get("type") != "category":
            return
        
        # Sync indicator with actual state
        tree_widget = item.treeWidget()
        if item.isExpanded() and not item_data.get("is_expanded", False):
            self._expand_category_with_animation(item, tree_widget)
        elif not item.isExpanded() and item_data.get("is_expanded", False):
            self._collapse_category_with_animation(item, tree_widget)
    
    def _populate_tools_tree(self, tree_widget):
        """Populate tools tree with RFU tool categories (legacy method)."""
        # Delegate to the new indicator-based implementation
        self._populate_tools_tree_with_indicators(tree_widget)
    
    def _filter_tools(self, search_text: str):
        """Filter tools based on search text."""
        if not self.tools_tree:
            return
        
        search_text = search_text.lower().strip()
        
        if not search_text:
            # Show all items
            self._show_all_items()
            return
        
        # Hide/show items based on search
        visible_categories = 0
        visible_tools = 0
        
        for i in range(self.tools_tree.topLevelItemCount()):
            category_item = self.tools_tree.topLevelItem(i)
            category_data = category_item.data(0, Qt.UserRole)
            category_name = category_data.get("name", "").lower()
            
            category_visible = False
            
            # Check if category name matches
            if search_text in category_name:
                category_visible = True
            
            # Check tools in category
            for j in range(category_item.childCount()):
                tool_item = category_item.child(j)
                tool_data = tool_item.data(0, Qt.UserRole)
                tool_name = tool_data.get("name", "").lower()
                tool_description = tool_data.get("description", "").lower()
                
                tool_matches = (search_text in tool_name or
                                search_text in tool_description or
                                category_visible)
                
                tool_item.setHidden(not tool_matches)
                
                if tool_matches:
                    category_visible = True
                    visible_tools += 1
            
            category_item.setHidden(not category_visible)
            if category_visible:
                visible_categories += 1
                category_item.setExpanded(True)
        
        # Update status
        if hasattr(self, 'status_label') and self.status_label:
            if search_text:
                found_msg = f"Found: {visible_categories} categories, " \
                           f"{visible_tools} tools"
                self.status_label.setText(found_msg)
            else:
                total_tools = sum(len(tools)
                                  for tools in self.tool_categories.values())
                categories_count = len(self.tool_categories)
                status_text = f"{categories_count} categories, " \
                              f"{total_tools} tools"
                self.status_label.setText(status_text)
    
    def _show_all_items(self):
        """Show all tools and categories."""
        if not self.tools_tree:
            return
        
        for i in range(self.tools_tree.topLevelItemCount()):
            category_item = self.tools_tree.topLevelItem(i)
            category_item.setHidden(False)
            
            for j in range(category_item.childCount()):
                tool_item = category_item.child(j)
                tool_item.setHidden(False)
    
    def _on_tool_activated(self, item, column):
        """Handle tool double-click activation."""
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        
        if item_type == "tool":
            tool_name = item_data.get("name")
            category = item_data.get("category")
            description = item_data.get("description")  # noqa: F841
            module_path = item_data.get("module")
            
            if QT_AVAILABLE and self.toolLaunched:
                # Emit tool name and module path for proper tool launching
                self.toolLaunched.emit(tool_name, module_path or category)
            
            # Update status
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(f"Launching: {tool_name}")
            
            log_msg = f"Tool activated: {tool_name} ({category})"
            if module_path:
                log_msg += f" - Module: {module_path}"
            self.logger.info(log_msg)
            
        elif item_type == "category":
            # Toggle category expansion
            item.setExpanded(not item.isExpanded())
            
            if QT_AVAILABLE and self.categoryExpanded:
                self.categoryExpanded.emit(item_data.get("name"))
    
    def _on_tool_selected(self, item, column):
        """Handle tool selection."""
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        
        if item_type == "tool":
            tool_name = item_data.get("name")
            description = item_data.get("description")
            
            if QT_AVAILABLE and self.toolSelected:
                self.toolSelected.emit(tool_name)
            
            # Update status with tool description
            if hasattr(self, 'status_label') and self.status_label:
                if len(description) > 80:
                    truncated_desc = description[:80] + "..."
                else:
                    truncated_desc = description
                self.status_label.setText(truncated_desc)
            
        elif item_type == "category":
            category_name = item_data.get("name")
            tool_count = len(self.tool_categories.get(category_name, []))
            
            if hasattr(self, 'status_label') and self.status_label:
                status_text = f"{category_name}: {tool_count} tools"
                self.status_label.setText(status_text)
    
    def _on_category_expanded(self, item):
        """Handle category expansion."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get("type") == "category":
            category_name = item_data.get("name")
            
            if QT_AVAILABLE and self.categoryExpanded:
                self.categoryExpanded.emit(category_name)
            
            self.logger.debug(f"Category expanded: {category_name}")
    
    def get_tool_count(self) -> int:
        """Get total number of tools."""
        return sum(len(tools) for tools in self.tool_categories.values())
    
    def get_category_count(self) -> int:
        """Get total number of categories."""
        return len(self.tool_categories)
    
    def expand_all_categories(self):
        """Expand all tool categories with animation."""
        if not self.tools_tree:
            return
        
        for i in range(self.tools_tree.topLevelItemCount()):
            category_item = self.tools_tree.topLevelItem(i)
            if not category_item.isExpanded():
                self._expand_category_with_animation(
                    category_item, self.tools_tree)
    
    def collapse_all_categories(self):
        """Collapse all tool categories with animation."""
        if not self.tools_tree:
            return
        
        for i in range(self.tools_tree.topLevelItemCount()):
            category_item = self.tools_tree.topLevelItem(i)
            if category_item.isExpanded():
                self._collapse_category_with_animation(
                    category_item, self.tools_tree)
    
    def clear_search(self):
        """Clear search filter and show all tools."""
        if hasattr(self, 'search_input') and self.search_input:
            self.search_input.clear()
        self._show_all_items()
        
        total_tools = sum(len(tools) for tools in
                          self.tool_categories.values())
        if hasattr(self, 'status_label') and self.status_label:
            categories_count = len(self.tool_categories)
            status_text = f"{categories_count} categories, " \
                          f"{total_tools} tools"
            self.status_label.setText(status_text)
    
    def get_state_data(self) -> Dict[str, Any]:
        """Get tools pane state data for persistence."""
        base_data = super().get_state_data()
        
        # Add tools-specific state
        expanded_categories = []
        if self.tools_tree:
            for i in range(self.tools_tree.topLevelItemCount()):
                category_item = self.tools_tree.topLevelItem(i)
                if category_item.isExpanded():
                    item_data = category_item.data(0, Qt.UserRole)
                    if item_data:
                        category_name = item_data.get("name")
                        if category_name:
                            expanded_categories.append(category_name)
        
        base_data.update({
            'expanded_categories': expanded_categories,
            'search_text': getattr(self.search_input, 'text', lambda: '')(),
            'tool_count': self.get_tool_count(),
            'category_count': self.get_category_count()
        })
        
        return base_data
    
    def restore_state_data(self, data: Dict[str, Any]):
        """Restore tools pane state data from persistence."""
        super().restore_state_data(data)
        
        # Restore expanded categories
        expanded_categories = data.get('expanded_categories', [])
        if self.tools_tree and expanded_categories:
            for i in range(self.tools_tree.topLevelItemCount()):
                category_item = self.tools_tree.topLevelItem(i)
                item_data = category_item.data(0, Qt.UserRole)
                if item_data:
                    category_name = item_data.get("name")
                    if category_name in expanded_categories:
                        self._expand_category_with_animation(
                            category_item, self.tools_tree)
        
        # Restore search text
        search_text = data.get('search_text', '')
        if search_text and hasattr(self, 'search_input') and self.search_input:
            self.search_input.setText(search_text)


class PaneFactory:
    """Factory for creating pane widgets based on configuration."""
    
    _pane_classes: ClassVar[Dict[PaneType, Type[BasePaneWidget]]] = {}
    
    @classmethod
    def register_pane_class(cls, pane_type: PaneType,
                            pane_class: Type[BasePaneWidget]):
        """
        Register a pane class for a specific pane type.
        
        Args:
            pane_type: Pane type to register
            pane_class: Pane widget class
        """
        cls._pane_classes[pane_type] = pane_class
    
    @classmethod
    def create_pane(cls, config: PaneConfiguration,
                    parent=None) -> BasePaneWidget:
        """
        Create pane widget based on configuration.
        
        Args:
            config: Pane configuration
            parent: Parent widget
            
        Returns:
            BasePaneWidget: Created pane widget
        """
        pane_class = cls._pane_classes.get(config.pane_type, BasePaneWidget)
        return pane_class(config, parent)
    
    @classmethod
    def get_registered_types(cls) -> List[PaneType]:
        """Get list of registered pane types."""
        return list(cls._pane_classes.keys())


class LayoutEngine:
    """
    Advanced layout engine for pane management.
    
    Handles complex layout arrangements with support for multiple
    layout types and dynamic reconfiguration.
    """
    
    def __init__(self):
        """Initialize layout engine."""
        self.logger = logging.getLogger('RFU.FileExplorer.LayoutEngine')
        
        # Layout algorithms
        self._layout_algorithms: Dict[LayoutType, Callable] = {
            LayoutType.GRID: self._apply_grid_layout,
            LayoutType.HORIZONTAL_SPLIT: self._apply_horizontal_split_layout,
            LayoutType.VERTICAL_SPLIT: self._apply_vertical_split_layout,
            LayoutType.TABBED: self._apply_tabbed_layout,
            LayoutType.FLOATING: self._apply_floating_layout
        }
        
        # Layout state
        self._current_layout: Optional[LayoutConfiguration] = None
        self._layout_widgets: Dict[str, QWidget] = {}
    
    def apply_layout(self, layout_config: LayoutConfiguration,
                     container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """
        Apply layout configuration to container.
        
        Args:
            layout_config: Layout configuration to apply
            container: Container widget to arrange panes in
            panes: List of pane widgets to arrange
            
        Returns:
            bool: True if layout applied successfully
        """
        try:
            self._current_layout = layout_config
            
            # Get layout algorithm
            algorithm = self._layout_algorithms.get(layout_config.layout_type)
            if not algorithm:
                error_msg = f"Unknown layout type: {layout_config.layout_type}"
                self.logger.error(error_msg)
                return False
            
            # Apply layout
            success = algorithm(layout_config, container, panes)
            
            if success:
                self.logger.info(f"Applied layout: {layout_config.name}")
            else:
                error_msg = f"Failed to apply layout: {layout_config.name}"
                self.logger.error(error_msg)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying layout: {e}")
            return False
    
    def _apply_grid_layout(self, layout_config: LayoutConfiguration,
                          container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """Apply grid layout."""
        if not QT_AVAILABLE:
            return False
        
        # Create grid layout
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(layout_config.spacing)
        grid_layout.setContentsMargins(*layout_config.margins)
        
        # Arrange panes in grid
        pane_index = 0
        for row in range(layout_config.rows):
            for col in range(layout_config.columns):
                if pane_index < len(panes):
                    pane = panes[pane_index]
                    grid_layout.addWidget(pane, row, col)
                    pane_index += 1
        
        return True
    
    def _apply_horizontal_split_layout(self, layout_config: LayoutConfiguration,
                                     container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """Apply horizontal split layout."""
        if not QT_AVAILABLE:
            return False
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Horizontal, container)
        splitter.setChildrenCollapsible(False)
        
        # Add panes to splitter
        for pane in panes:
            splitter.addWidget(pane)
        
        # Apply splitter sizes if configured
        if layout_config.splitter_sizes:
            splitter.setSizes(layout_config.splitter_sizes)
        
        # Set splitter as container's layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        
        return True
    
    def _apply_vertical_split_layout(self, layout_config: LayoutConfiguration,
                                   container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """Apply vertical split layout."""
        if not QT_AVAILABLE:
            return False
        
        # Create vertical splitter
        splitter = QSplitter(Qt.Vertical, container)
        splitter.setChildrenCollapsible(False)
        
        # Add panes to splitter
        for pane in panes:
            splitter.addWidget(pane)
        
        # Apply splitter sizes if configured
        if layout_config.splitter_sizes:
            splitter.setSizes(layout_config.splitter_sizes)
        
        # Set splitter as container's layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        
        return True
    
    def _apply_tabbed_layout(self, layout_config: LayoutConfiguration,
                           container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """Apply tabbed layout."""
        if not QT_AVAILABLE:
            return False
        
        # Create tab widget
        tab_widget = QTabWidget(container)
        tab_widget.setTabsClosable(True)
        tab_widget.setMovable(True)
        
        # Add panes as tabs
        for pane in panes:
            tab_widget.addTab(pane, pane.config.title)
        
        # Set tab widget as container's layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tab_widget)
        
        return True
    
    def _apply_floating_layout(self, layout_config: LayoutConfiguration,
                             container: QWidget, panes: List[BasePaneWidget]) -> bool:
        """Apply floating layout."""
        if not QT_AVAILABLE:
            return False
        
        # Create stacked widget for base
        stacked_widget = QStackedWidget(container)
        
        # Add first pane to stack (if any)
        if panes:
            stacked_widget.addWidget(panes[0])
        
        # Set remaining panes as floating
        for pane in panes[1:]:
            pane.setParent(None)
            pane.setWindowFlags(Qt.Window)
            pane.show()
            pane.config.is_floating = True
        
        # Set stacked widget as container's layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(stacked_widget)
        
        return True


class PaneManager(QObject):
    """
    Comprehensive pane management system.
    
    Manages pane lifecycle, layout arrangements, and cross-pane coordination
    with persistence and state management capabilities.
    """
    
    # Signals for pane management events
    paneAdded = pyqtSignal(str) if QT_AVAILABLE else None
    paneRemoved = pyqtSignal(str) if QT_AVAILABLE else None
    layoutChanged = pyqtSignal(str) if QT_AVAILABLE else None
    paneActivated = pyqtSignal(str) if QT_AVAILABLE else None
    paneDeactivated = pyqtSignal(str) if QT_AVAILABLE else None
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize pane manager.
        
        Args:
            config_file: Optional configuration file path
        """
        if QT_AVAILABLE:
            super().__init__()
        
        self.logger = logging.getLogger('RFU.FileExplorer.PaneManager')
        
        # Configuration
        self.config_file = config_file or "pane_layouts.json"
        
        # Pane management
        self._panes: Dict[str, BasePaneWidget] = {}
        self._active_pane_id: Optional[str] = None
        self._pane_order: List[str] = []
        
        # Layout management
        self._layouts: Dict[str, LayoutConfiguration] = {}
        self._current_layout_id: Optional[str] = None
        self._layout_engine = LayoutEngine()
        
        # Container widgets
        self._main_container: Optional[QWidget] = None
        self._floating_containers: List[QWidget] = []
        
        # State management
        self._state_dirty = False
        self._auto_save_timer: Optional[QTimer] = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'panes_created': 0,
            'panes_destroyed': 0,
            'layouts_applied': 0,
            'state_saves': 0,
            'start_time': datetime.now()
        }
        
        self._setup_auto_save()
        self._load_configuration()
        
        self.logger.info("Pane manager initialized")
    
    def _setup_auto_save(self):
        """Setup automatic state saving."""
        if QT_AVAILABLE:
            self._auto_save_timer = QTimer()
            self._auto_save_timer.timeout.connect(self._auto_save_state)
            self._auto_save_timer.start(30000)  # Save every 30 seconds
    
    def _auto_save_state(self):
        """Automatically save state if dirty."""
        if self._state_dirty:
            self.save_state()
    
    def set_main_container(self, container: QWidget):
        """
        Set main container widget for pane layout.
        
        Args:
            container: Main container widget
        """
        self._main_container = container
        self.logger.debug("Main container set")
    
    def create_pane(self, config: PaneConfiguration) -> str:
        """
        Create new pane with specified configuration.
        
        Args:
            config: Pane configuration
            
        Returns:
            str: Pane ID of created pane
        """
        try:
            with self._lock:
                # Create pane widget
                pane = PaneFactory.create_pane(config, self._main_container)
                
                # Connect pane signals
                if QT_AVAILABLE:
                    pane.paneActivated.connect(self._on_pane_activated)
                    pane.paneDeactivated.connect(self._on_pane_deactivated)
                    pane.paneClosed.connect(self._on_pane_closed)
                
                # Add to management
                self._panes[pane.pane_id] = pane
                self._pane_order.append(pane.pane_id)
                
                # Update statistics
                self.stats['panes_created'] += 1
                self._state_dirty = True
                
                # Emit signal
                if QT_AVAILABLE and self.paneAdded:
                    self.paneAdded.emit(pane.pane_id)
                
                self.logger.info(f"Created pane: {pane.pane_id}")
                return pane.pane_id
                
        except Exception as e:
            self.logger.error(f"Failed to create pane: {e}")
            return ""
    
    def remove_pane(self, pane_id: str) -> bool:
        """
        Remove pane by ID.
        
        Args:
            pane_id: ID of pane to remove
            
        Returns:
            bool: True if pane was removed successfully
        """
        try:
            with self._lock:
                if pane_id not in self._panes:
                    return False
                
                pane = self._panes[pane_id]
                
                # Check if pane can be closed
                if not pane.close_pane():
                    return False
                
                # Remove from management
                del self._panes[pane_id]
                if pane_id in self._pane_order:
                    self._pane_order.remove(pane_id)
                
                # Update active pane if necessary
                if self._active_pane_id == pane_id:
                    self._active_pane_id = None
                    if self._pane_order:
                        self.activate_pane(self._pane_order[-1])
                
                # Update statistics
                self.stats['panes_destroyed'] += 1
                self._state_dirty = True
                
                # Emit signal
                if QT_AVAILABLE and self.paneRemoved:
                    self.paneRemoved.emit(pane_id)
                
                self.logger.info(f"Removed pane: {pane_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to remove pane {pane_id}: {e}")
            return False
    
    def get_pane(self, pane_id: str) -> Optional[BasePaneWidget]:
        """
        Get pane by ID.
        
        Args:
            pane_id: Pane ID
            
        Returns:
            Optional[BasePaneWidget]: Pane widget or None
        """
        return self._panes.get(pane_id)
    
    def get_active_pane(self) -> Optional[BasePaneWidget]:
        """Get currently active pane."""
        if self._active_pane_id:
            return self._panes.get(self._active_pane_id)
        return None
    
    def activate_pane(self, pane_id: str) -> bool:
        """
        Activate pane by ID.
        
        Args:
            pane_id: ID of pane to activate
            
        Returns:
            bool: True if pane was activated successfully
        """
        try:
            with self._lock:
                if pane_id not in self._panes:
                    return False
                
                # Deactivate current active pane
                if self._active_pane_id and self._active_pane_id != pane_id:
                    current_pane = self._panes.get(self._active_pane_id)
                    if current_pane:
                        current_pane.deactivate()
                
                # Activate new pane
                pane = self._panes[pane_id]
                pane.activate()
                self._active_pane_id = pane_id
                
                # Update pane order (move to end)
                if pane_id in self._pane_order:
                    self._pane_order.remove(pane_id)
                self._pane_order.append(pane_id)
                
                self._state_dirty = True
                
                self.logger.debug(f"Activated pane: {pane_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to activate pane {pane_id}: {e}")
            return False
    
    def apply_layout(self, layout_id: str) -> bool:
        """
        Apply layout configuration.
        
        Args:
            layout_id: Layout ID to apply
            
        Returns:
            bool: True if layout applied successfully
        """
        try:
            with self._lock:
                if layout_id not in self._layouts:
                    self.logger.error(f"Layout not found: {layout_id}")
                    return False
                
                if not self._main_container:
                    self.logger.error("No main container set")
                    return False
                
                layout_config = self._layouts[layout_id]
                panes = list(self._panes.values())
                
                # Apply layout using layout engine
                success = self._layout_engine.apply_layout(
                    layout_config, self._main_container, panes
                )
                
                if success:
                    self._current_layout_id = layout_id
                    self.stats['layouts_applied'] += 1
                    self._state_dirty = True
                    
                    # Emit signal
                    if QT_AVAILABLE and self.layoutChanged:
                        self.layoutChanged.emit(layout_id)
                    
                    self.logger.info(f"Applied layout: {layout_config.name}")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Failed to apply layout {layout_id}: {e}")
            return False
    
    def save_layout(self, layout_config: LayoutConfiguration) -> bool:
        """
        Save layout configuration.
        
        Args:
            layout_config: Layout configuration to save
            
        Returns:
            bool: True if layout saved successfully
        """
        try:
            with self._lock:
                layout_config.modified_time = datetime.now()
                self._layouts[layout_config.layout_id] = layout_config
                self._state_dirty = True
                
                self.logger.info(f"Saved layout: {layout_config.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save layout: {e}")
            return False
    
    def _on_pane_activated(self, pane_id: str):
        """Handle pane activation signal."""
        self._active_pane_id = pane_id
        if QT_AVAILABLE and self.paneActivated:
            self.paneActivated.emit(pane_id)
    
    def _on_pane_deactivated(self, pane_id: str):
        """Handle pane deactivation signal."""
        if QT_AVAILABLE and self.paneDeactivated:
            self.paneDeactivated.emit(pane_id)
    
    def _on_pane_closed(self, pane_id: str):
        """Handle pane closure signal."""
        self.remove_pane(pane_id)
    
    def save_state(self) -> bool:
        """
        Save current pane manager state.
        
        Returns:
            bool: True if state saved successfully
        """
        try:
            state_data = {
                'layouts': {
                    layout_id: layout.to_dict() 
                    for layout_id, layout in self._layouts.items()
                },
                'panes': {
                    pane_id: pane.get_state_data() 
                    for pane_id, pane in self._panes.items()
                },
                'active_pane_id': self._active_pane_id,
                'current_layout_id': self._current_layout_id,
                'pane_order': self._pane_order,
                'statistics': self.stats,
                'saved_time': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self._state_dirty = False
            self.stats['state_saves'] += 1
            
            self.logger.info(f"Saved state to: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
    
    def _load_configuration(self) -> bool:
        """
        Load pane manager configuration.
        
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            if not Path(self.config_file).exists():
                self.logger.info("No configuration file found, starting fresh")
                return True
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Load layouts
            for layout_id, layout_data in data.get('layouts', {}).items():
                layout = LayoutConfiguration.from_dict(layout_data)
                self._layouts[layout_id] = layout
            
            # Load other state
            self._active_pane_id = data.get('active_pane_id')
            self._current_layout_id = data.get('current_layout_id')
            self._pane_order = data.get('pane_order', [])
            
            # Load statistics
            saved_stats = data.get('statistics', {})
            self.stats.update(saved_stats)
            
            self.logger.info(f"Loaded configuration from: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pane manager statistics."""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_panes': len(self._panes),
            'active_pane_id': self._active_pane_id,
            'current_layout_id': self._current_layout_id,
            'total_layouts': len(self._layouts),
            'panes_created': self.stats['panes_created'],
            'panes_destroyed': self.stats['panes_destroyed'],
            'layouts_applied': self.stats['layouts_applied'],
            'state_saves': self.stats['state_saves'],
            'state_dirty': self._state_dirty
        }
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Save state if dirty
            if self._state_dirty:
                self.save_state()
            
            # Stop auto-save timer
            if self._auto_save_timer:
                self._auto_save_timer.stop()
            
            # Close all panes
            with self._lock:
                for pane_id in list(self._panes.keys()):
                    self.remove_pane(pane_id)
            
            self.logger.info("Pane manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Register standard pane types with the factory
if QT_AVAILABLE:
    PaneFactory.register_pane_class(PaneType.TOOLS, ToolsPaneWidget)


# For testing and development
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test pane manager
    pane_manager = PaneManager("test_pane_layouts.json")
    
    # Create test pane configurations
    config1 = PaneConfiguration(
        pane_id="test_pane_1",
        pane_type=PaneType.FILE_EXPLORER,
        title="File Explorer 1"
    )
    
    config2 = PaneConfiguration(
        pane_id="test_pane_2", 
        pane_type=PaneType.PREVIEW,
        title="Preview Pane"
    )
    
    # Create panes
    pane_id1 = pane_manager.create_pane(config1)
    pane_id2 = pane_manager.create_pane(config2)
    
    print(f"Created panes: {pane_id1}, {pane_id2}")
    
    # Test layout
    layout_config = LayoutConfiguration(
        layout_id="test_layout",
        name="Test Horizontal Split",
        layout_type=LayoutType.HORIZONTAL_SPLIT
    )
    
    pane_manager.save_layout(layout_config)
    
    # Test statistics
    stats = pane_manager.get_statistics()
    print(f"Statistics: {stats}")
    
    # Cleanup
    pane_manager.cleanup()
    print("Pane manager testing completed!")