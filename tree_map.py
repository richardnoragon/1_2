import os
import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from typing import Dict, Any, Optional, List

from gui.standard_window import StandardWindow
from gui.themes import ThemeManager, Colors


class TreeMapLogic(QObject):
    """Scans a directory to calculate item sizes for treemap visualization."""

    progress_updated = pyqtSignal(str, int, int)  # message, current, total
    scan_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self) -> None:
        """Initialize the tree map logic."""
        super().__init__()
        self._is_running: bool = False
        self._target_path: Optional[str] = None

    def stop(self) -> None:
        """Stop the scanning process."""
        self.progress_updated.emit("Stopping scan...", 0, 0)
        self._is_running = False

    def start_scan(self, target_path: str) -> None:
        """Initiate the directory scan process."""
        if not os.path.isdir(target_path):
            self.error_occurred.emit(
                f"Error: Not a valid directory: {target_path}")
            self.finished.emit()
            return

        self._is_running = True
        self._target_path = target_path
        scan_data: Dict[str, Any] = {'path': target_path, 'items': []}
        total_size: int = 0
        items_processed: int = 0

        try:
            # First Pass: Count items for progress
            total_items: int = sum(
                len(files) + len(dirs)
                for _, dirs, files in os.walk(target_path)
            )
            
            # Second Pass: Calculate sizes
            for root, dirs, files in os.walk(target_path):
                if not self._is_running:
                    break
                    
                for name in files + dirs:
                    if not self._is_running:
                        break
                        
                    full_path: str = os.path.join(root, name)
                    try:
                        if os.path.isfile(full_path):
                            size: int = os.path.getsize(full_path)
                        elif os.path.isdir(full_path):
                            size: int = self._get_dir_size(full_path)
                        else:
                            continue
                            
                        item_type: str = (
                            'file' if os.path.isfile(full_path)
                            else 'directory'
                        )
                        scan_data['items'].append({
                            'name': name,
                            'path': full_path,
                            'size': size,
                            'type': item_type
                        })
                        total_size += size
                        
                    except (OSError, PermissionError):
                        continue
                    
                    items_processed += 1
                    self.progress_updated.emit(
                        f"Scanning: {name}", items_processed, total_items)

            if self._is_running:
                scan_data['total_size'] = total_size
                self.scan_complete.emit(scan_data)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def _get_dir_size(self, path: str) -> int:
        """Calculate total size of a directory."""
        total: int = 0
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += self._get_dir_size(entry.path)
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError):
            pass
        return total


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
    app: QApplication = QApplication(sys.argv)
    window: TreeMapGUI = TreeMapGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
