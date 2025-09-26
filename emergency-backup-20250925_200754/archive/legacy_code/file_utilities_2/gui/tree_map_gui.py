"""
Tree map GUI components for directory visualization.

This module contains the GUI classes for displaying treemap visualizations
of directory structures and file sizes.
"""

import os
import math
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QVBoxLayout, 
    QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from typing import Dict, Any, Optional, List

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager, Colors
from file_utilities_2.core.tree_map_logic import TreeMapLogic


class TreeMapView(QGraphicsView):
    """Custom graphics view for displaying treemap visualization."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumSize(400, 300)


class TreeMapGUI(StandardWindow):
    """Tree map visualization utility with standardized styling."""
    
    def __init__(self) -> None:
        super().__init__("Tree Map Visualization")
        self.scan_thread: Optional[QThread] = None
        self.tree_map_logic: Optional[TreeMapLogic] = None
        self.scan_data: Optional[Dict[str, Any]] = None
        self.directory_path: str = ""
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup the user interface with standardized styling."""
        # Create header
        header = self.create_header("Tree Map Visualization")
        self.main_layout.addWidget(header)
        
        # Create control group
        control_group = self.create_group_box("Controls")
        control_layout = QVBoxLayout()
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        ThemeManager.style_label(self.dir_label)
        
        select_btn = self.create_button(
            "Select Directory", self.select_directory
        )
        scan_btn = self.create_button(
            "Scan Directory", self.start_scan, primary=False
        )
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(select_btn)
        dir_layout.addWidget(scan_btn)
        
        control_layout.addLayout(dir_layout)
        control_group.setLayout(control_layout)
        self.main_layout.addWidget(control_group)
        
        # Create visualization group
        viz_group = self.create_group_box("Visualization")
        viz_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = self.create_progress_bar()
        self.progress_bar.setVisible(False)
        
        # Graphics view for treemap
        self.scene = QGraphicsScene()
        self.view = TreeMapView()
        self.view.setScene(self.scene)
        
        viz_layout.addWidget(self.progress_bar)
        viz_layout.addWidget(self.view)
        viz_group.setLayout(viz_layout)
        self.main_layout.addWidget(viz_group)
        
        # Create info group
        info_group = self.create_group_box("Information")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Select a directory to visualize")
        ThemeManager.style_label(self.info_label)
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        self.main_layout.addWidget(info_group)
        
    def select_directory(self) -> None:
        """Select directory to visualize."""
        directory: str = self.get_directory_path(
            "Select Directory to Visualize"
        )
        if directory:
            self.dir_label.setText(os.path.basename(directory))
            self.directory_path = directory
            self.show_status_message(f"Selected: {directory}")
            
    def start_scan(self) -> None:
        """Start scanning the selected directory."""
        if not self.directory_path:
            self.show_error_dialog("Error", "Please select a directory first")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_status_message("Scanning directory...")
        
        # Clear previous visualization
        self.scene.clear()
        
        # Create and start scan thread
        self.tree_map_logic = TreeMapLogic()
        self.scan_thread = QThread()
        self.tree_map_logic.moveToThread(self.scan_thread)
        
        # Connect signals
        self.tree_map_logic.progress_updated.connect(self.update_progress)
        self.tree_map_logic.scan_complete.connect(self.display_treemap)
        self.tree_map_logic.error_occurred.connect(self.handle_error)
        self.tree_map_logic.finished.connect(self.scan_thread.quit)
        
        # Use a local variable to avoid type issues
        logic = self.tree_map_logic
        self.scan_thread.started.connect(
            lambda: logic.start_scan(self.directory_path)
        )
        
        self.scan_thread.start()
        
    def update_progress(self, message: str, current: int, total: int) -> None:
        """Update progress bar during scanning."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.show_status_message(message)
        
    def display_treemap(self, scan_data: Dict[str, Any]) -> None:
        """Display the treemap visualization."""
        self.scan_data = scan_data
        self.progress_bar.setVisible(False)
        
        if not scan_data['items']:
            self.show_info_dialog("Info", "No items found in directory")
            return
            
        # Calculate layout
        total_size: int = scan_data['total_size']
        items: List[Dict[str, Any]] = sorted(
            scan_data['items'], key=lambda x: x['size'], reverse=True
        )[:50]
        
        # Create treemap rectangles
        self._create_treemap_rectangles(items, total_size)
        
        # Update info
        self.info_label.setText(
            f"Directory: {os.path.basename(scan_data['path'])}\n"
            f"Total Size: {self._format_size(total_size)}\n"
            f"Items: {len(scan_data['items'])}"
        )
        
        self.show_status_message("Visualization complete")
        
    def _create_treemap_rectangles(
        self, items: List[Dict[str, Any]], total_size: int
    ) -> None:
        """Create rectangles for treemap visualization."""
        if not items:
            return
            
        # Simple treemap layout (squarified)
        view_width: int = 400
        view_height: int = 300
        
        x: int = 0
        y: int = 0
        
        for item in items:
            if total_size == 0:
                continue
                
            proportion: float = item['size'] / total_size
            rect_width: int = max(20, int(view_width * proportion))
            rect_height: int = max(20, int(view_height * proportion**0.5))
            
            # Color based on file type and size
            color: QColor = self._get_item_color(item)
            
            rect = QGraphicsRectItem(x, y, rect_width, rect_height)
            rect.setBrush(QBrush(color))
            rect.setPen(QPen(Qt.black, 1))
            
            self.scene.addItem(rect)
            
            x += rect_width
            if x >= view_width:
                x = 0
                y += rect_height
                
    def _get_item_color(self, item: Dict[str, Any]) -> QColor:
        """Get color for treemap item based on type and size."""
        if item['type'] == 'directory':
            return QColor(Colors.ACCENT)
        else:
            # Color intensity based on file size
            size_ratio: float = min(
                item['size'] / (1024 * 1024), 1.0
            )  # Normalize to 1MB
            return QColor(
                int(255 * size_ratio),
                int(100 * (1 - size_ratio)),
                50
            )
            
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        size: float = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def handle_error(self, error_message: str) -> None:
        """Handle errors during scanning."""
        self.progress_bar.setVisible(False)
        self.show_error_dialog("Error", error_message)
        
    def closeEvent(self, event) -> None:
        """Clean up when closing."""
        if self.scan_thread and self.scan_thread.isRunning():
            if self.tree_map_logic:
                self.tree_map_logic.stop()
            self.scan_thread.quit()
            self.scan_thread.wait()
        event.accept()


def main() -> None:
    """Main function to run the tree map utility."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app: QApplication = QApplication(sys.argv)
    window: TreeMapGUI = TreeMapGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()