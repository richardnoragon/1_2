import os
import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QVBoxLayout
)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QColor
from gui.common import BaseWindow, get_existing_directory


class DiskScanLogic(QObject):
    """Scans a directory to calculate item sizes for treemap visualization."""

    # Data format: {'path': path, 'items': [{'name': name, 'size': size, ...}]}
    progress_updated = pyqtSignal(str, int, int)  # message, current, total
    scan_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._target_path = None

    def stop(self):
        self.progress_updated.emit("Stopping scan...", 0, 0)
        self._is_running = False

    def start_scan(self, target_path):
        """Initiates the directory scan process."""
        if not os.path.isdir(target_path):
            self.error_occurred.emit(
                f"Error: Not a valid directory: {target_path}")
            self.finished.emit()
            return

        self._is_running = True
        self._target_path = target_path
        scan_data = {'path': target_path, 'items': []}
        total_size = 0
        items_processed = 0

        try:
            # First Pass: Count items for progress
            all_entries = []
            try:
                with os.scandir(target_path) as entries:
                    for entry in entries:
                        if not self._is_running:
                            break
                        all_entries.append(entry)
            except PermissionError:
                self.error_occurred.emit(
                    f"Permission denied accessing: {target_path}")
                self._is_running = False
            except Exception as e:
                self.error_occurred.emit(
                    f"Error listing directory {target_path}: {e}")
                self._is_running = False

            if not self._is_running:
                self.progress_updated.emit("Scan cancelled.", 0, 0)
                self.finished.emit()
                return

            total_items = len(all_entries)
            self.progress_updated.emit(
                f"Scanning {total_items} items in "
                f"{os.path.basename(target_path)}...",
                0, total_items
            )

            # Second Pass: Get sizes
            for entry in all_entries:
                if not self._is_running:
                    break
                items_processed += 1
                self.progress_updated.emit(
                    f"Processing: {entry.name}",
                    items_processed,
                    total_items
                )
                item_path = entry.path
                item_size = 0
                try:
                    if entry.is_dir(follow_symlinks=False):
                        item_size = self._get_dir_size(item_path)
                    elif entry.is_file(follow_symlinks=False):
                        item_size = entry.stat(follow_symlinks=False).st_size
                    else:
                        continue

                    if item_size > 0:
                        scan_data['items'].append({
                            'name': entry.name,
                            'size': item_size,
                            'path': item_path
                        })
                        total_size += item_size
                except PermissionError:
                    self.progress_updated.emit(
                        f"Skipping (permission denied): {entry.name}",
                        items_processed,
                        total_items
                    )
                except FileNotFoundError:
                    self.progress_updated.emit(
                        f"Skipping (not found/broken link?): {entry.name}",
                        items_processed,
                        total_items
                    )
                except Exception as e:
                    self.progress_updated.emit(
                        f"Skipping (error): {entry.name} - {e}",
                        items_processed,
                        total_items
                    )

            if self._is_running:
                self.progress_updated.emit(
                    f"Scan finished for {os.path.basename(target_path)}. "
                    "Preparing results...",
                    total_items,
                    total_items
                )
                self.scan_complete.emit(scan_data)

        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(
                    f"An unexpected error occurred during scan: {e}")
        finally:
            if self._is_running:
                self._is_running = False
            self.finished.emit()

    def _get_dir_size(self, dir_path):
        """Recursively calculates the total size of a directory."""
        total_size = 0
        if not self._is_running:
            return 0
        try:
            for dirpath, dirnames, filenames in os.walk(
                dir_path,
                topdown=True,
                onerror=self._handle_walk_error
            ):
                if not self._is_running:
                    break
                for f in filenames:
                    if not self._is_running:
                        break
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp) and os.path.isfile(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except FileNotFoundError:
                            self.progress_updated.emit(
                                f"Skipping (link/not found): {fp}", -1, -1)
                        except PermissionError:
                            self.progress_updated.emit(
                                f"Skipping (permission): {fp}", -1, -1)
                        except Exception as e:
                            self.progress_updated.emit(
                                f"Skipping (error getting size): {fp} - {e}",
                                -1, -1
                            )
        except PermissionError:
            self.progress_updated.emit(
                f"Skipping directory (permission): {dir_path}", -1, -1)
        except Exception as e:
            self.progress_updated.emit(
                f"Error walking directory {dir_path}: {e}", -1, -1)
        return total_size

    def _handle_walk_error(self, os_error):
        """Handles errors during os.walk, typically permission errors."""
        if self._is_running:
            self.progress_updated.emit(
                f"Cannot access: {os_error.filename} ({os_error.strerror})",
                -1,
                -1
            )


class TreeMapWindow(BaseWindow):
    def __init__(self):
        super().__init__("tree_map.ui")
        
        # Initialize scene and view for treemap
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.treeMapContainer.layout() or self.treeMapContainer.setLayout(
            QVBoxLayout()
        )
        self.treeMapContainer.layout().addWidget(self.view)
        
        # Initialize disk scanner
        self.scanner = DiskScanLogic()
        self.scanner_thread = QThread()
        self.scanner.moveToThread(self.scanner_thread)
        
        # Connect signals
        self.btnSelectDirectory.clicked.connect(self.select_directory)
        self.btnStop.clicked.connect(self.stop_scan)
        self.scanner.progress_updated.connect(self.update_progress)
        self.scanner.scan_complete.connect(self.draw_treemap)
        self.scanner.error_occurred.connect(self.show_error)
        self.scanner.finished.connect(self.scan_finished)
        
        # Connect menu actions
        self.actionExit.triggered.connect(self.close)
        
        self.scanner_thread.start()
        
    def select_directory(self):
        dir_path = get_existing_directory(self, "Select Directory")
        if dir_path:
            self.lblPath.setText(dir_path)
            self.btnStop.setEnabled(True)
            self.progressBar.setValue(0)
            self.scene.clear()
            self.scanner.start_scan(dir_path)
    
    def stop_scan(self):
        self.scanner.stop()
        self.btnStop.setEnabled(False)
    
    def update_progress(self, message, current, total):
        self.lblStatus.setText(message)
        if total > 0:
            self.progressBar.setValue(int((current / total) * 100))
    
    def show_error(self, message):
        self.lblStatus.setText(f"Error: {message}")
    
    def scan_finished(self):
        self.btnStop.setEnabled(False)
        
    def draw_treemap(self, data):
        """Draw the treemap visualization using the scanned data."""
        self.scene.clear()
        
        # Get total size and sort items by size
        items = sorted(data['items'], key=lambda x: x['size'], reverse=True)
        total_size = sum(item['size'] for item in items)
        
        if total_size == 0:
            self.lblStatus.setText("No items to display")
            return
            
        # Calculate available space
        view_width = self.view.width() - 20
        view_height = self.view.height() - 20
        
        # Draw rectangles
        self.draw_rectangles(items, total_size, 0, 0, view_width, view_height)
        
        # Fit scene in view
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
        self.lblStatus.setText(f"Scan complete: {len(items)} items found")
    
    def draw_rectangles(self, items, total_size, x, y, width, height):
        """Recursively draw rectangles for the treemap."""
        if not items:
            return
            
        # Calculate area for first item
        item = items[0]
        item_ratio = item['size'] / total_size
        
        # Decide orientation (horizontal or vertical split)
        if width > height:
            # Horizontal split
            item_width = width * item_ratio
            self.create_rectangle(x, y, item_width, height, item)
            
            # Recursively draw remaining items
            remaining_width = width - item_width
            if remaining_width > 0 and len(items) > 1:
                remaining_size = sum(i['size'] for i in items[1:])
                self.draw_rectangles(
                    items[1:],
                    remaining_size,
                    x + item_width,
                    y,
                    remaining_width,
                    height
                )
        else:
            # Vertical split
            item_height = height * item_ratio
            self.create_rectangle(x, y, width, item_height, item)
            
            # Recursively draw remaining items
            remaining_height = height - item_height
            if remaining_height > 0 and len(items) > 1:
                remaining_size = sum(i['size'] for i in items[1:])
                self.draw_rectangles(
                    items[1:],
                    remaining_size,
                    x,
                    y + item_height,
                    width,
                    remaining_height
                )
    
    def create_rectangle(self, x, y, width, height, item):
        """Create a rectangle item for the treemap with appropriate styling."""
        rect = QGraphicsRectItem(x, y, width, height)
        
        # Calculate color based on size (larger items are darker)
        color_value = max(100, 255 - int(math.log2(item['size']) * 10))
        color = QColor(color_value, color_value, 255)
        
        rect.setBrush(QBrush(color))
        rect.setPen(QPen(Qt.black, 1))
        
        # Add tooltip with item info
        size_str = self.format_size(item['size'])
        rect.setToolTip(f"{item['name']}\n{size_str}")
        
        self.scene.addItem(rect)
        return rect
    
    def format_size(self, size):
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def resizeEvent(self, event):
        """Handle window resize event to update treemap."""
        super().resizeEvent(event)
        if self.scene.items():
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeMapWindow()
    window.show()
    sys.exit(app.exec_())
