"""
Tree map logic for directory scanning and size calculation.

This module contains the core logic for scanning directories and calculating
file/folder sizes for treemap visualization.
"""

import os
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Optional


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