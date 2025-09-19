"""
Custom UI Widgets for RFU Multi-Pane File Explorer
Specialized Widgets for Enhanced User Experience

This module provides custom UI widgets that enhance the file explorer
with specialized functionality and consistent styling.

Widget Categories:
- ToolbarWidgets: Enhanced toolbars with custom buttons and controls
- StatusWidgets: Advanced status bars with progress and information
- PropertyWidgets: File/folder property panels and inspectors
- PreviewWidgets: File content preview and thumbnail displays
- SearchWidgets: Advanced search interfaces and filters
- NavigationWidgets: Enhanced navigation components

Key Features:
- Consistent theming and styling across all widgets
- Accessibility support with keyboard navigation
- Responsive design for different screen sizes
- Integration with file explorer pane components
- Performance optimization for large datasets
- Extensible architecture for custom plugins

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from PyQt5.QtCore import (QEasingCurve, QEvent, QMimeData, QObject, QPoint,
                              QPropertyAnimation, QRect, QSize, Qt, QTimer,
                              QUrl, pyqtSignal)
    from PyQt5.QtGui import (QBrush, QColor, QDrag, QFont, QFontMetrics, QIcon,
                             QLinearGradient, QPainter, QPalette, QPen,
                             QPixmap, QPolygon)
    from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                                 QFrame, QGridLayout, QGroupBox, QHBoxLayout,
                                 QHeaderView, QLabel, QLineEdit, QListWidget,
                                 QListWidgetItem, QMenu, QProgressBar,
                                 QPushButton, QRadioButton, QScrollArea,
                                 QSizePolicy, QSlider, QSplitter, QStyle,
                                 QStyleOption, QTableWidget, QTableWidgetItem,
                                 QTabWidget, QTextEdit, QToolButton, QToolTip,
                                 QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                                 QWidget)
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Fallback definitions
    class QWidget:
        pass
    class QFrame:
        pass
    class QLabel:
        pass
    class QProgressBar:
        pass
    def pyqt_signal(*args):
        """
        Fallback signal implementation when PyQt5 is not available.
        This is a dummy implementation that returns a no-op function.
        """
        def dummy_signal(*signal_args):
            # Empty implementation for fallback compatibility
            # when PyQt5 is not installed on the system
            pass
        return dummy_signal
    
    # Maintain backward compatibility
    pyqtSignal = pyqt_signal


# Color scheme for consistent theming
class ThemeColors:
    """Centralized color scheme for consistent theming."""
    
    # Primary colors
    PRIMARY = QColor(70, 130, 180) if QT_AVAILABLE else None
    PRIMARY_LIGHT = QColor(100, 150, 200) if QT_AVAILABLE else None
    PRIMARY_DARK = QColor(40, 100, 150) if QT_AVAILABLE else None
    
    # Secondary colors
    SECONDARY = QColor(120, 120, 120) if QT_AVAILABLE else None
    SECONDARY_LIGHT = QColor(150, 150, 150) if QT_AVAILABLE else None
    SECONDARY_DARK = QColor(80, 80, 80) if QT_AVAILABLE else None
    
    # Background colors
    BACKGROUND = QColor(248, 249, 250) if QT_AVAILABLE else None
    BACKGROUND_DARK = QColor(240, 241, 242) if QT_AVAILABLE else None
    BACKGROUND_SELECTED = QColor(230, 240, 250) if QT_AVAILABLE else None
    
    # Text colors
    TEXT = QColor(33, 37, 41) if QT_AVAILABLE else None
    TEXT_SECONDARY = QColor(108, 117, 125) if QT_AVAILABLE else None
    TEXT_MUTED = QColor(173, 181, 189) if QT_AVAILABLE else None
    
    # Status colors
    SUCCESS = QColor(40, 167, 69) if QT_AVAILABLE else None
    WARNING = QColor(255, 193, 7) if QT_AVAILABLE else None
    ERROR = QColor(220, 53, 69) if QT_AVAILABLE else None
    INFO = QColor(23, 162, 184) if QT_AVAILABLE else None


class EnhancedToolbar(QFrame if QT_AVAILABLE else object):
    """Enhanced toolbar with custom styling and functionality."""
    
    # Signals
    actionTriggered = pyqtSignal(str) if QT_AVAILABLE else None
    
    def __init__(self, parent=None):
        """Initialize enhanced toolbar."""
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.EnhancedToolbar')
        
        # Toolbar state
        self.actions = {}
        self.button_groups = {}
        
        if QT_AVAILABLE:
            self._setup_ui()
    
    def _setup_ui(self):
        """Setup toolbar UI."""
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedHeight(40)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Apply styling
        self.setStyleSheet("""
            EnhancedToolbar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border-bottom: 1px solid #dee2e6;
            }
        """)
    
    def add_action_button(self, action_id: str, text: str, icon: QIcon = None,
                         tooltip: str = "", checkable: bool = False) -> QToolButton:
        """
        Add an action button to the toolbar.
        
        Args:
            action_id: Unique action identifier
            text: Button text
            icon: Button icon
            tooltip: Button tooltip
            checkable: Whether button is checkable
            
        Returns:
            Created QToolButton
        """
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip or text)
        button.setCheckable(checkable)
        
        if icon:
            button.setIcon(icon)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Style the button
        button.setStyleSheet("""
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
                background: transparent;
                font-weight: normal;
            }
            QToolButton:hover {
                background: rgba(0, 123, 255, 0.1);
                border-color: rgba(0, 123, 255, 0.25);
            }
            QToolButton:pressed {
                background: rgba(0, 123, 255, 0.2);
            }
            QToolButton:checked {
                background: rgba(0, 123, 255, 0.15);
                border-color: rgba(0, 123, 255, 0.5);
            }
        """)
        
        # Connect signal
        button.clicked.connect(lambda: self._emit_action(action_id))
        
        # Add to layout and store
        self.layout().addWidget(button)
        self.actions[action_id] = button
        
        return button
    
    def add_separator(self):
        """Add a separator to the toolbar."""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        self.layout().addWidget(separator)
    
    def add_spacer(self):
        """Add a spacer to the toolbar."""
        self.layout().addStretch()
    
    def add_widget(self, widget: QWidget):
        """Add a custom widget to the toolbar."""
        self.layout().addWidget(widget)
    
    def get_action_button(self, action_id: str) -> Optional[QToolButton]:
        """Get action button by ID."""
        return self.actions.get(action_id)
    
    def set_action_enabled(self, action_id: str, enabled: bool):
        """Enable/disable action button."""
        button = self.actions.get(action_id)
        if button:
            button.setEnabled(enabled)
    
    def set_action_checked(self, action_id: str, checked: bool):
        """Set action button checked state."""
        button = self.actions.get(action_id)
        if button and button.isCheckable():
            button.setChecked(checked)
    
    def _emit_action(self, action_id: str):
        """Emit action triggered signal."""
        if self.actionTriggered:
            self.actionTriggered.emit(action_id)


class EnhancedStatusBar(QFrame if QT_AVAILABLE else object):
    """Enhanced status bar with multiple information sections."""
    
    def __init__(self, parent=None):
        """Initialize enhanced status bar."""
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.EnhancedStatusBar')
        
        # Status components
        self.main_label = None
        self.file_count_label = None
        self.selection_label = None
        self.size_label = None
        self.progress_bar = None
        self.status_icon = None
        
        if QT_AVAILABLE:
            self._setup_ui()
    
    def _setup_ui(self):
        """Setup status bar UI."""
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedHeight(25)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        
        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        layout.addWidget(self.status_icon)
        
        # Main status label
        self.main_label = QLabel("Ready")
        layout.addWidget(self.main_label)
        
        # Spacer
        layout.addStretch()
        
        # File count label
        self.file_count_label = QLabel("")
        layout.addWidget(self.file_count_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)
        
        # Selection label
        self.selection_label = QLabel("")
        layout.addWidget(self.selection_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Size label
        self.size_label = QLabel("")
        layout.addWidget(self.size_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(150)
        layout.addWidget(self.progress_bar)
        
        # Apply styling
        self.setStyleSheet("""
            EnhancedStatusBar {
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
            QLabel {
                color: #495057;
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: #007bff;
                border-radius: 2px;
            }
        """)
    
    def set_main_message(self, message: str, status_type: str = "info"):
        """
        Set main status message.
        
        Args:
            message: Status message
            status_type: Message type (info, success, warning, error)
        """
        if self.main_label:
            self.main_label.setText(message)
        
        # Set status icon based on type
        if self.status_icon:
            icon_map = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            self.status_icon.setText(icon_map.get(status_type, "ℹ️"))
    
    def set_file_count(self, count: int, total_size: int = 0):
        """
        Set file count information.
        
        Args:
            count: Number of files
            total_size: Total size in bytes
        """
        if self.file_count_label:
            if count == 1:
                self.file_count_label.setText("1 item")
            else:
                self.file_count_label.setText(f"{count:,} items")
        
        if self.size_label and total_size > 0:
            size_text = self._format_file_size(total_size)
            self.size_label.setText(size_text)
    
    def set_selection_info(self, selected_count: int, selected_size: int = 0):
        """
        Set selection information.
        
        Args:
            selected_count: Number of selected items
            selected_size: Total size of selected items
        """
        if self.selection_label:
            if selected_count == 0:
                self.selection_label.setText("")
            elif selected_count == 1:
                self.selection_label.setText("1 selected")
            else:
                self.selection_label.setText(f"{selected_count:,} selected")
        
        if self.size_label and selected_count > 0 and selected_size > 0:
            size_text = self._format_file_size(selected_size)
            self.size_label.setText(f"Selected: {size_text}")
    
    def show_progress(self, minimum: int = 0, maximum: int = 100, value: int = 0):
        """
        Show progress bar.
        
        Args:
            minimum: Minimum value
            maximum: Maximum value
            value: Current value
        """
        if self.progress_bar:
            self.progress_bar.setRange(minimum, maximum)
            self.progress_bar.setValue(value)
            self.progress_bar.setVisible(True)
    
    def update_progress(self, value: int):
        """Update progress bar value."""
        if self.progress_bar:
            self.progress_bar.setValue(value)
    
    def hide_progress(self):
        """Hide progress bar."""
        if self.progress_bar:
            self.progress_bar.setVisible(False)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"


class FilePropertyPanel(QFrame if QT_AVAILABLE else object):
    """File/folder property panel for detailed information."""
    
    def __init__(self, parent=None):
        """Initialize file property panel."""
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.FilePropertyPanel')
        
        # Current file info
        self.current_file_path = ""
        
        # UI components
        self.file_icon = None
        self.file_name_label = None
        self.file_type_label = None
        self.file_size_label = None
        self.file_date_labels = {}
        self.file_permissions_label = None
        self.properties_table = None
        
        if QT_AVAILABLE:
            self._setup_ui()
    
    def _setup_ui(self):
        """Setup property panel UI."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumWidth(300)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header section
        self._create_header_section(layout)
        
        # Basic info section
        self._create_basic_info_section(layout)
        
        # Detailed properties section
        self._create_properties_section(layout)
        
        # Apply styling
        self.setStyleSheet("""
            FilePropertyPanel {
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QLabel {
                color: #495057;
            }
            .header-label {
                font-weight: bold;
                font-size: 12px;
                color: #212529;
            }
            .value-label {
                font-size: 11px;
                color: #6c757d;
            }
        """)
    
    def _create_header_section(self, layout):
        """Create header section with icon and name."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # File icon
        self.file_icon = QLabel()
        self.file_icon.setFixedSize(32, 32)
        self.file_icon.setAlignment(Qt.AlignCenter)
        self.file_icon.setStyleSheet("border: 1px solid #dee2e6; border-radius: 4px;")
        header_layout.addWidget(self.file_icon)
        
        # File name
        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setWordWrap(True)
        self.file_name_label.setProperty("class", "header-label")
        header_layout.addWidget(self.file_name_label, 1)
        
        layout.addWidget(header_frame)
    
    def _create_basic_info_section(self, layout):
        """Create basic information section."""
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        # File type
        type_frame = QFrame()
        type_layout = QHBoxLayout(type_frame)
        type_layout.setContentsMargins(0, 0, 0, 0)
        
        type_layout.addWidget(QLabel("Type:"))
        self.file_type_label = QLabel("-")
        self.file_type_label.setProperty("class", "value-label")
        type_layout.addWidget(self.file_type_label, 1)
        
        info_layout.addWidget(type_frame)
        
        # File size
        size_frame = QFrame()
        size_layout = QHBoxLayout(size_frame)
        size_layout.setContentsMargins(0, 0, 0, 0)
        
        size_layout.addWidget(QLabel("Size:"))
        self.file_size_label = QLabel("-")
        self.file_size_label.setProperty("class", "value-label")
        size_layout.addWidget(self.file_size_label, 1)
        
        info_layout.addWidget(size_frame)
        
        layout.addWidget(info_group)
    
    def _create_properties_section(self, layout):
        """Create detailed properties section."""
        props_group = QGroupBox("Properties")
        props_layout = QVBoxLayout(props_group)
        
        # Properties table
        self.properties_table = QTableWidget()
        self.properties_table.setColumnCount(2)
        self.properties_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.properties_table.horizontalHeader().setStretchLastSection(True)
        self.properties_table.verticalHeader().setVisible(False)
        self.properties_table.setAlternatingRowColors(True)
        self.properties_table.setMaximumHeight(200)
        
        props_layout.addWidget(self.properties_table)
        
        layout.addWidget(props_group)
        
        # Spacer
        layout.addStretch()
    
    def set_file_info(self, file_path: str):
        """
        Set file information to display.
        
        Args:
            file_path: Path to the file or directory
        """
        try:
            self.current_file_path = file_path
            
            if not file_path or not Path(file_path).exists():
                self._clear_info()
                return
            
            path_obj = Path(file_path)
            stat_info = path_obj.stat()
            
            # Update header
            self.file_name_label.setText(path_obj.name)
            
            # Update basic info
            if path_obj.is_dir():
                self.file_type_label.setText("Folder")
                
                # Calculate folder size (this could be expensive for large folders)
                try:
                    folder_size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
                    self.file_size_label.setText(self._format_file_size(folder_size))
                except Exception:
                    self.file_size_label.setText("Calculating...")
            else:
                # File type from suffix
                file_type = path_obj.suffix[1:].upper() if path_obj.suffix else "File"
                self.file_type_label.setText(f"{file_type} File")
                
                # File size
                self.file_size_label.setText(self._format_file_size(stat_info.st_size))
            
            # Update properties table
            self._update_properties_table(path_obj, stat_info)
            
        except Exception as e:
            self.logger.error(f"Error setting file info for {file_path}: {e}")
            self._clear_info()
    
    def _update_properties_table(self, path_obj: Path, stat_info):
        """Update properties table with file details."""
        properties = []
        
        # Basic properties
        properties.append(("Name", path_obj.name))
        properties.append(("Location", str(path_obj.parent)))
        
        if path_obj.is_file():
            properties.append(("Size", self._format_file_size(stat_info.st_size)))
        
        # Dates
        try:
            created_time = datetime.fromtimestamp(stat_info.st_ctime)
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            accessed_time = datetime.fromtimestamp(stat_info.st_atime)
            
            properties.append(("Created", created_time.strftime("%Y-%m-%d %H:%M:%S")))
            properties.append(("Modified", modified_time.strftime("%Y-%m-%d %H:%M:%S")))
            properties.append(("Accessed", accessed_time.strftime("%Y-%m-%d %H:%M:%S")))
        except Exception:
            pass
        
        # Permissions (on Unix-like systems)
        try:
            import stat
            mode = stat_info.st_mode
            
            permissions = []
            if mode & stat.S_IRUSR:
                permissions.append("Read")
            if mode & stat.S_IWUSR:
                permissions.append("Write")
            if mode & stat.S_IXUSR:
                permissions.append("Execute")
            
            if permissions:
                properties.append(("Permissions", ", ".join(permissions)))
        except Exception:
            pass
        
        # Update table
        self.properties_table.setRowCount(len(properties))
        
        for i, (prop, value) in enumerate(properties):
            prop_item = QTableWidgetItem(prop)
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemIsEditable)
            
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            
            self.properties_table.setItem(i, 0, prop_item)
            self.properties_table.setItem(i, 1, value_item)
        
        self.properties_table.resizeColumnsToContents()
    
    def _clear_info(self):
        """Clear displayed information."""
        self.file_name_label.setText("No file selected")
        self.file_type_label.setText("-")
        self.file_size_label.setText("-")
        self.properties_table.setRowCount(0)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"


class QuickPreviewWidget(QFrame if QT_AVAILABLE else object):
    """Quick preview widget for file content."""
    
    def __init__(self, parent=None):
        """Initialize quick preview widget."""
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.QuickPreviewWidget')
        
        # Current preview state
        self.current_file_path = ""
        self.preview_type = "none"
        
        # UI components
        self.preview_label = None
        self.preview_text = None
        self.preview_image = None
        self.no_preview_label = None
        
        if QT_AVAILABLE:
            self._setup_ui()
    
    def _setup_ui(self):
        """Setup preview widget UI."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumWidth(250)
        self.setMinimumHeight(200)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_label = QLabel("Quick Preview")
        header_label.setStyleSheet("font-weight: bold; color: #212529;")
        layout.addWidget(header_label)
        
        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(150)
        self.preview_label.setStyleSheet("""
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background: #f8f9fa;
        """)
        layout.addWidget(self.preview_label)
        
        # No preview message
        self.no_preview_label = QLabel("No preview available")
        self.no_preview_label.setAlignment(Qt.AlignCenter)
        self.no_preview_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.no_preview_label)
        
        # Initially show no preview
        self._show_no_preview()
        
        # Apply styling
        self.setStyleSheet("""
            QuickPreviewWidget {
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
    
    def set_file_preview(self, file_path: str):
        """
        Set file to preview.
        
        Args:
            file_path: Path to the file to preview
        """
        try:
            self.current_file_path = file_path
            
            if not file_path or not Path(file_path).exists():
                self._show_no_preview()
                return
            
            path_obj = Path(file_path)
            
            if path_obj.is_dir():
                self._show_folder_preview(path_obj)
            else:
                self._show_file_preview(path_obj)
                
        except Exception as e:
            self.logger.error(f"Error setting file preview for {file_path}: {e}")
            self._show_no_preview()
    
    def _show_file_preview(self, path_obj: Path):
        """Show file preview based on file type."""
        file_suffix = path_obj.suffix.lower()
        
        # Image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico'}
        if file_suffix in image_extensions:
            self._show_image_preview(path_obj)
            return
        
        # Text files
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.xml', '.json', '.md', '.log'}
        if file_suffix in text_extensions or self._is_text_file(path_obj):
            self._show_text_preview(path_obj)
            return
        
        # Default: show file info
        self._show_file_info_preview(path_obj)
    
    def _show_image_preview(self, path_obj: Path):
        """Show image preview."""
        try:
            pixmap = QPixmap(str(path_obj))
            if not pixmap.isNull():
                # Scale to fit preview area
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.show()
                self.no_preview_label.hide()
                self.preview_type = "image"
                return
        except Exception as e:
            self.logger.warning(f"Error loading image preview: {e}")
        
        self._show_no_preview()
    
    def _show_text_preview(self, path_obj: Path):
        """Show text file preview."""
        try:
            # Read first few lines of text file
            with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # First 1000 characters
            
            # Create preview text
            preview_text = content[:500] + "..." if len(content) > 500 else content
            
            self.preview_label.setText(preview_text)
            self.preview_label.setWordWrap(True)
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.show()
            self.no_preview_label.hide()
            self.preview_type = "text"
            
        except Exception as e:
            self.logger.warning(f"Error loading text preview: {e}")
            self._show_no_preview()
    
    def _show_file_info_preview(self, path_obj: Path):
        """Show basic file information."""
        try:
            stat_info = path_obj.stat()
            
            info_text = f"""
File: {path_obj.name}
Size: {self._format_file_size(stat_info.st_size)}
Type: {path_obj.suffix[1:].upper() if path_obj.suffix else 'File'}
Modified: {datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')}
            """.strip()
            
            self.preview_label.setText(info_text)
            self.preview_label.setWordWrap(True)
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.show()
            self.no_preview_label.hide()
            self.preview_type = "info"
            
        except Exception as e:
            self.logger.warning(f"Error showing file info: {e}")
            self._show_no_preview()
    
    def _show_folder_preview(self, path_obj: Path):
        """Show folder preview with item count."""
        try:
            # Count items in folder
            item_count = sum(1 for _ in path_obj.iterdir())
            
            folder_text = f"""
Folder: {path_obj.name}
Items: {item_count}
Location: {path_obj.parent}
            """.strip()
            
            self.preview_label.setText(folder_text)
            self.preview_label.setWordWrap(True)
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.show()
            self.no_preview_label.hide()
            self.preview_type = "folder"
            
        except Exception as e:
            self.logger.warning(f"Error showing folder preview: {e}")
            self._show_no_preview()
    
    def _show_no_preview(self):
        """Show no preview available message."""
        self.preview_label.clear()
        self.preview_label.hide()
        self.no_preview_label.show()
        self.preview_type = "none"
    
    def _is_text_file(self, path_obj: Path) -> bool:
        """Check if file is likely a text file."""
        try:
            with open(path_obj, 'rb') as f:
                chunk = f.read(1024)
                # Simple heuristic: check if most bytes are printable ASCII
                printable_ratio = sum(1 for b in chunk if 32 <= b <= 126 or b in [9, 10, 13]) / len(chunk)
                return printable_ratio > 0.7
        except Exception:
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"


class SearchWidget(QFrame if QT_AVAILABLE else object):
    """Advanced search widget with filters and options."""
    
    # Signals
    searchRequested = pyqtSignal(str, dict) if QT_AVAILABLE else None
    searchClosed = pyqtSignal() if QT_AVAILABLE else None
    
    def __init__(self, parent=None):
        """Initialize search widget."""
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.SearchWidget')
        
        # Search state
        self.is_search_active = False
        
        # UI components
        self.search_input = None
        self.search_button = None
        self.close_button = None
        self.options_frame = None
        
        if QT_AVAILABLE:
            self._setup_ui()
    
    def _setup_ui(self):
        """Setup search widget UI."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumHeight(100)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Search input row
        search_row = QFrame()
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files and folders...")
        self.search_input.returnPressed.connect(self._perform_search)
        search_layout.addWidget(self.search_input, 1)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)
        search_layout.addWidget(self.search_button)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self._close_search)
        search_layout.addWidget(self.close_button)
        
        layout.addWidget(search_row)
        
        # Options row
        options_row = QFrame()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        # Case sensitive checkbox
        self.case_sensitive_cb = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_cb)
        
        # Whole words checkbox
        self.whole_words_cb = QCheckBox("Whole words")
        options_layout.addWidget(self.whole_words_cb)
        
        # Include subfolders checkbox
        self.include_subfolders_cb = QCheckBox("Include subfolders")
        self.include_subfolders_cb.setChecked(True)
        options_layout.addWidget(self.include_subfolders_cb)
        
        options_layout.addStretch()
        
        layout.addWidget(options_row)
        
        # Apply styling
        self.setStyleSheet("""
            SearchWidget {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
            }
            QLineEdit {
                padding: 4px;
                border: 1px solid #ced4da;
                border-radius: 3px;
            }
            QPushButton {
                padding: 4px 12px;
                border: 1px solid #007bff;
                border-radius: 3px;
                background: #007bff;
                color: white;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        
        # Initially hidden
        self.hide()
    
    def show_search(self):
        """Show search widget and focus input."""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()
        self.is_search_active = True
    
    def hide_search(self):
        """Hide search widget."""
        self.hide()
        self.is_search_active = False
        if self.searchClosed:
            self.searchClosed.emit()
    
    def _perform_search(self):
        """Perform search with current criteria."""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        # Collect search options
        search_options = {
            'case_sensitive': self.case_sensitive_cb.isChecked(),
            'whole_words': self.whole_words_cb.isChecked(),
            'include_subfolders': self.include_subfolders_cb.isChecked()
        }
        
        # Emit search signal
        if self.searchRequested:
            self.searchRequested.emit(search_text, search_options)
        
        self.logger.debug(f"Search requested: '{search_text}' with options {search_options}")
    
    def _close_search(self):
        """Close search widget."""
        self.hide_search()


# For testing and development
if __name__ == '__main__':
    import sys
    
    if QT_AVAILABLE:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                                     QWidget)

        # Configure logging for testing
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        app = QApplication(sys.argv)
        
        # Test main window
        window = QMainWindow()
        window.setWindowTitle("Custom Widgets Test")
        window.resize(1000, 700)
        
        # Central widget
        central = QWidget()
        window.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Test toolbar
        toolbar = EnhancedToolbar()
        toolbar.add_action_button("new", "New", tooltip="Create new file")
        toolbar.add_action_button("open", "Open", tooltip="Open file")
        toolbar.add_separator()
        toolbar.add_action_button("list", "List", checkable=True)
        toolbar.add_action_button("grid", "Grid", checkable=True)
        toolbar.add_spacer()
        layout.addWidget(toolbar)
        
        # Test status bar
        status_bar = EnhancedStatusBar()
        status_bar.set_main_message("Ready to test custom widgets")
        status_bar.set_file_count(123, 1024*1024*15)
        status_bar.set_selection_info(5, 1024*512)
        layout.addWidget(status_bar)
        
        # Test property panel and preview (side by side)
        panels_frame = QFrame()
        panels_layout = QHBoxLayout(panels_frame)
        
        property_panel = FilePropertyPanel()
        property_panel.set_file_info(__file__)
        panels_layout.addWidget(property_panel)
        
        preview_widget = QuickPreviewWidget()
        preview_widget.set_file_preview(__file__)
        panels_layout.addWidget(preview_widget)
        
        panels_layout.addStretch()
        layout.addWidget(panels_frame, 1)
        
        # Test search widget
        search_widget = SearchWidget()
        search_widget.show_search()
        layout.addWidget(search_widget)
        
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available - cannot run GUI test")