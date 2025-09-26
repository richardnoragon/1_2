"""
Breadcrumb Widget for RFU Multi-Pane File Explorer

This module provides an interactive breadcrumb navigation component
with clickable path segments and dropdown menus.

Author: Richard Noragon
Version: 2.0.0
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt5.QtWidgets import (QAction, QFrame, QHBoxLayout, QLabel, QMenu,
                             QPushButton, QSizePolicy, QStyle, QToolButton,
                             QWidget)


@dataclass
class BreadcrumbSegment:
    """Represents a single breadcrumb segment."""
    path: str
    display_text: str
    is_clickable: bool = True
    is_current: bool = False
    has_children: bool = False
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.display_text:
            self.display_text = Path(self.path).name or self.path


class ClickableLabel(QLabel):
    """Clickable label for breadcrumb segments."""
    
    clicked = pyqtSignal()
    right_clicked = pyqtSignal()
    
    def __init__(self, text: str = "", parent=None):
        """Initialize clickable label."""
        super().__init__(text, parent)
        
        self.setStyleSheet("""
            QLabel {
                padding: 4px 8px;
                border-radius: 3px;
                background-color: transparent;
            }
            QLabel:hover {
                background-color: #e6f3ff;
                text-decoration: underline;
            }
        """)
        
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit()
        super().mousePressEvent(event)


class BreadcrumbDropdown(QToolButton):
    """Dropdown button for breadcrumb segments with children."""
    
    segment_selected = pyqtSignal(str)  # path
    
    def __init__(self, segment: BreadcrumbSegment, parent=None):
        """Initialize dropdown button."""
        super().__init__(parent)
        
        self.segment = segment
        self.setText("▼")
        self.setToolTip(f"Show subdirectories of {segment.display_text}")
        
        self.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 2px;
                margin: 0px 2px;
            }
            QToolButton:hover {
                background-color: #e6f3ff;
                border-radius: 2px;
            }
        """)
        
        # Setup menu
        self.setPopupMode(QToolButton.InstantPopup)
        self.setup_menu()
    
    def setup_menu(self) -> None:
        """Setup dropdown menu with subdirectories."""
        menu = QMenu(self)
        
        try:
            path_obj = Path(self.segment.path)
            if path_obj.exists() and path_obj.is_dir():
                # Get subdirectories
                subdirs = []
                for item in path_obj.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        subdirs.append(item)
                
                # Sort subdirectories
                subdirs.sort(key=lambda x: x.name.lower())
                
                # Add menu actions
                for subdir in subdirs[:20]:  # Limit to prevent huge menus
                    action = QAction(subdir.name, menu)
                    action.triggered.connect(
                        lambda checked, p=str(subdir): self.segment_selected.emit(p)
                    )
                    menu.addAction(action)
                
                if len(subdirs) > 20:
                    menu.addSeparator()
                    more_action = QAction(f"... and {len(subdirs) - 20} more", menu)
                    more_action.setEnabled(False)
                    menu.addAction(more_action)
                
                if not subdirs:
                    empty_action = QAction("No subdirectories", menu)
                    empty_action.setEnabled(False)
                    menu.addAction(empty_action)
            
            else:
                # Directory not accessible
                error_action = QAction("Directory not accessible", menu)
                error_action.setEnabled(False)
                menu.addAction(error_action)
        
        except (PermissionError, OSError):
            # Handle permission errors
            error_action = QAction("Access denied", menu)
            error_action.setEnabled(False)
            menu.addAction(error_action)
        
        self.setMenu(menu)


class BreadcrumbSeparator(QLabel):
    """Visual separator between breadcrumb segments."""
    
    def __init__(self, parent=None):
        """Initialize separator."""
        super().__init__("›", parent)
        
        self.setStyleSheet("""
            QLabel {
                color: #666666;
                font-weight: bold;
                padding: 0px 4px;
            }
        """)
        
        self.setAlignment(Qt.AlignCenter)


class BreadcrumbWidget(QWidget):
    """
    Interactive breadcrumb navigation widget.
    
    Features:
    - Clickable path segments
    - Dropdown menus for subdirectories
    - Automatic path truncation
    - Drag and drop support
    - Keyboard navigation
    - Custom styling
    """
    
    # Signals
    path_clicked = pyqtSignal(str)  # path
    navigation_requested = pyqtSignal(str)  # path
    segment_right_clicked = pyqtSignal(str)  # path
    breadcrumb_changed = pyqtSignal(str)  # current_path
    
    def __init__(self, parent=None):
        """Initialize breadcrumb widget."""
        super().__init__(parent)
        
        # Current state
        self.current_path = ""
        self.segments: List[BreadcrumbSegment] = []
        self.segment_widgets: List[QWidget] = []
        
        # Configuration
        self.max_segments = 8
        self.min_segment_width = 50
        self.show_dropdowns = True
        self.show_icons = True
        
        # Setup UI
        self.setup_ui()
        
        # Setup logging
        self.logger = logging.getLogger('RFU.BreadcrumbWidget')
        
        self.logger.debug("BreadcrumbWidget initialized")
    
    def setup_ui(self) -> None:
        """Setup the breadcrumb widget UI."""
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(0)
        
        # Root button (always visible)
        self.root_button = QPushButton()
        self.root_button.setText("💾")
        self.root_button.setToolTip("Go to drives/root")
        self.root_button.setFixedSize(28, 24)
        self.root_button.clicked.connect(self.show_root_menu)
        
        self.root_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #d1e7ff;
            }
        """)
        
        self.layout.addWidget(self.root_button)
        
        # Spacer for dynamic content
        self.layout.addStretch()
        
        # Setup context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def set_path(self, path: str) -> None:
        """
        Set the current path and update breadcrumbs.
        
        Args:
            path: Path to display as breadcrumbs
        """
        try:
            # Normalize path
            normalized_path = str(Path(path).resolve())
            
            if normalized_path == self.current_path:
                return
            
            self.current_path = normalized_path
            
            # Generate segments
            self.segments = self._generate_segments(normalized_path)
            
            # Update UI
            self._update_breadcrumb_display()
            
            # Emit signal
            self.breadcrumb_changed.emit(self.current_path)
            
            self.logger.debug(f"Breadcrumb path set to: {self.current_path}")
            
        except (OSError, ValueError) as e:
            self.logger.warning(f"Invalid path for breadcrumbs: {path} - {e}")
    
    def get_path(self) -> str:
        """Get current path."""
        return self.current_path
    
    def _generate_segments(self, path: str) -> List[BreadcrumbSegment]:
        """
        Generate breadcrumb segments from path.
        
        Args:
            path: Full path to segment
            
        Returns:
            List of breadcrumb segments
        """
        segments = []
        
        try:
            path_obj = Path(path)
            parts = path_obj.parts
            
            # Build segments from path parts
            current_path = ""
            for i, part in enumerate(parts):
                if i == 0:
                    # Handle root/drive
                    current_path = part
                    if part.endswith(':\\'):
                        display_text = part  # Show "C:\" etc.
                    else:
                        display_text = part  # Unix root "/"
                else:
                    current_path = str(Path(current_path) / part)
                    display_text = part
                
                # Check if segment has children
                has_children = self._path_has_subdirectories(current_path)
                
                # Create segment
                segment = BreadcrumbSegment(
                    path=current_path,
                    display_text=display_text,
                    is_clickable=True,
                    is_current=(i == len(parts) - 1),
                    has_children=has_children
                )
                
                segments.append(segment)
            
            # Apply truncation if needed
            if len(segments) > self.max_segments:
                segments = self._truncate_segments(segments)
            
        except Exception as e:
            self.logger.error(f"Failed to generate segments: {e}")
        
        return segments
    
    def _path_has_subdirectories(self, path: str) -> bool:
        """
        Check if path has subdirectories.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path has subdirectories
        """
        try:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir():
                for item in path_obj.iterdir():
                    if item.is_dir():
                        return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _truncate_segments(self, segments: List[BreadcrumbSegment]) -> List[BreadcrumbSegment]:
        """
        Truncate segments if too many.
        
        Args:
            segments: Original segments list
            
        Returns:
            Truncated segments list
        """
        if len(segments) <= self.max_segments:
            return segments
        
        # Keep first segment (root), last few segments, and add ellipsis
        truncated = []
        
        # Root segment
        truncated.append(segments[0])
        
        # Ellipsis segment
        ellipsis_segment = BreadcrumbSegment(
            path="...",
            display_text="...",
            is_clickable=True,
            has_children=False
        )
        truncated.append(ellipsis_segment)
        
        # Last segments
        keep_count = self.max_segments - 2
        truncated.extend(segments[-keep_count:])
        
        return truncated
    
    def _update_breadcrumb_display(self) -> None:
        """Update the breadcrumb display with current segments."""
        # Clear existing widgets (except root button)
        self._clear_segment_widgets()
        
        # Add segments
        for i, segment in enumerate(self.segments):
            # Add separator (except before first segment)
            if i > 0:
                separator = BreadcrumbSeparator(self)
                self.layout.insertWidget(-1, separator)
                self.segment_widgets.append(separator)
            
            # Add segment widget
            segment_widget = self._create_segment_widget(segment)
            self.layout.insertWidget(-1, segment_widget)
            self.segment_widgets.append(segment_widget)
            
            # Add dropdown if segment has children
            if segment.has_children and self.show_dropdowns and not segment.is_current:
                dropdown = BreadcrumbDropdown(segment, self)
                dropdown.segment_selected.connect(self.navigation_requested.emit)
                self.layout.insertWidget(-1, dropdown)
                self.segment_widgets.append(dropdown)
    
    def _create_segment_widget(self, segment: BreadcrumbSegment) -> QWidget:
        """
        Create widget for a breadcrumb segment.
        
        Args:
            segment: Segment to create widget for
            
        Returns:
            QWidget for the segment
        """
        if segment.path == "...":
            # Ellipsis segment - shows truncated path menu
            button = QPushButton("...")
            button.setToolTip("Show full path")
            button.clicked.connect(self.show_full_path_menu)
            
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #e6f3ff;
                }
            """)
            
            return button
        
        else:
            # Regular segment
            label = ClickableLabel(segment.display_text, self)
            label.setToolTip(f"Navigate to: {segment.path}")
            
            # Connect signals
            label.clicked.connect(lambda: self._on_segment_clicked(segment.path))
            label.right_clicked.connect(lambda: self._on_segment_right_clicked(segment.path))
            
            # Style current segment differently
            if segment.is_current:
                label.setStyleSheet("""
                    QLabel {
                        padding: 4px 8px;
                        border-radius: 3px;
                        background-color: #0078d4;
                        color: white;
                        font-weight: bold;
                    }
                """)
                label.setCursor(Qt.ArrowCursor)
            
            return label
    
    def _clear_segment_widgets(self) -> None:
        """Clear all segment widgets from layout."""
        for widget in self.segment_widgets:
            widget.setParent(None)
            widget.deleteLater()
        
        self.segment_widgets.clear()
    
    def _on_segment_clicked(self, path: str) -> None:
        """Handle segment click."""
        self.path_clicked.emit(path)
        self.navigation_requested.emit(path)
        self.logger.debug(f"Segment clicked: {path}")
    
    def _on_segment_right_clicked(self, path: str) -> None:
        """Handle segment right-click."""
        self.segment_right_clicked.emit(path)
        self.logger.debug(f"Segment right-clicked: {path}")
    
    def show_root_menu(self) -> None:
        """Show root/drives menu."""
        menu = QMenu(self)
        
        # Get available drives/mount points
        drives = self._get_available_drives()
        
        for drive in drives:
            action = QAction(drive, menu)
            action.triggered.connect(lambda checked, d=drive: self.navigation_requested.emit(d))
            menu.addAction(action)
        
        if not drives:
            no_drives_action = QAction("No drives available", menu)
            no_drives_action.setEnabled(False)
            menu.addAction(no_drives_action)
        
        # Show menu
        menu.exec_(self.root_button.mapToGlobal(QPoint(0, self.root_button.height())))
    
    def show_full_path_menu(self) -> None:
        """Show full path menu when ellipsis is clicked."""
        if not self.current_path:
            return
        
        menu = QMenu(self)
        
        # Show all path segments
        path_obj = Path(self.current_path)
        parts = path_obj.parts
        
        current_path = ""
        for i, part in enumerate(parts):
            if i == 0:
                current_path = part
                display_text = part
            else:
                current_path = str(Path(current_path) / part)
                display_text = f"{'  ' * i}{part}"
            
            action = QAction(display_text, menu)
            action.triggered.connect(lambda checked, p=current_path: self.navigation_requested.emit(p))
            menu.addAction(action)
        
        # Show menu
        menu.exec_(self.mapToGlobal(QPoint(100, self.height())))
    
    def show_context_menu(self, position: QPoint) -> None:
        """Show context menu for breadcrumb widget."""
        menu = QMenu(self)
        
        # Copy path action
        copy_action = QAction("Copy Path", menu)
        copy_action.triggered.connect(self.copy_path_to_clipboard)
        menu.addAction(copy_action)
        
        # Copy segment path action
        segment_path = self._get_segment_at_position(position)
        if segment_path:
            copy_segment_action = QAction(f"Copy '{Path(segment_path).name}' Path", menu)
            copy_segment_action.triggered.connect(lambda: self.copy_path_to_clipboard(segment_path))
            menu.addAction(copy_segment_action)
        
        menu.addSeparator()
        
        # Open in file manager
        open_action = QAction("Open in File Manager", menu)
        open_action.triggered.connect(self.open_in_file_manager)
        menu.addAction(open_action)
        
        # Properties
        props_action = QAction("Properties", menu)
        props_action.triggered.connect(self.show_path_properties)
        menu.addAction(props_action)
        
        # Show menu
        menu.exec_(self.mapToGlobal(position))
    
    def _get_segment_at_position(self, position: QPoint) -> Optional[str]:
        """Get segment path at given position."""
        # Find which segment widget is at the position
        for widget in self.segment_widgets:
            if isinstance(widget, ClickableLabel) and widget.geometry().contains(position):
                # Find corresponding segment
                for segment in self.segments:
                    if segment.display_text == widget.text():
                        return segment.path
        return None
    
    def _get_available_drives(self) -> List[str]:
        """Get list of available drives/mount points."""
        import sys
        drives = []
        
        if sys.platform == 'win32':
            # Windows drives
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # Unix-like systems
            drives.append('/')
        
        return drives
    
    def copy_path_to_clipboard(self, path: Optional[str] = None) -> None:
        """Copy path to clipboard."""
        from PyQt5.QtWidgets import QApplication
        
        target_path = path or self.current_path
        if target_path:
            clipboard = QApplication.clipboard()
            clipboard.setText(target_path)
            self.logger.debug(f"Path copied to clipboard: {target_path}")
    
    def open_in_file_manager(self) -> None:
        """Open current path in system file manager."""
        if self.current_path:
            import subprocess
            import sys
            
            try:
                if sys.platform == 'win32':
                    subprocess.run(['explorer', self.current_path], check=True)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', self.current_path], check=True)
                else:
                    subprocess.run(['xdg-open', self.current_path], check=True)
                
                self.logger.info(f"Opened in file manager: {self.current_path}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to open in file manager: {e}")
    
    def show_path_properties(self) -> None:
        """Show path properties dialog."""
        # This would show a properties dialog
        self.logger.info(f"Properties requested for: {self.current_path}")
    
    def set_max_segments(self, count: int) -> None:
        """
        Set maximum number of segments to display.
        
        Args:
            count: Maximum segment count
        """
        self.max_segments = max(3, count)  # Minimum 3 segments
        
        # Regenerate display if path is set
        if self.current_path:
            self.set_path(self.current_path)
    
    def set_show_dropdowns(self, show: bool) -> None:
        """
        Set whether to show dropdown menus.
        
        Args:
            show: Whether to show dropdowns
        """
        self.show_dropdowns = show
        
        # Regenerate display if path is set
        if self.current_path:
            self.set_path(self.current_path)
    
    def get_segments(self) -> List[BreadcrumbSegment]:
        """Get current breadcrumb segments."""
        return self.segments.copy()
    
    def clear(self) -> None:
        """Clear the breadcrumb display."""
        self.current_path = ""
        self.segments.clear()
        self._clear_segment_widgets()
        self.logger.debug("Breadcrumb cleared")