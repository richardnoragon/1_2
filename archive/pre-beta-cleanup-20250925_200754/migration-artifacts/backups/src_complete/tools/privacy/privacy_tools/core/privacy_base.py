"""
Base class for all privacy tools.

This module provides the foundation for all privacy cleaning tools,
including common functionality, error handling, and progress tracking.
"""

import os
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from .platform_utils import PlatformUtils
from .browser_detector import BrowserDetector


class PrivacyOperationResult:
    """Result of a privacy operation."""
    
    def __init__(self, success: bool, message: str, 
                 items_processed: int = 0, errors: List[str] = None):
        self.success = success
        self.message = message
        self.items_processed = items_processed
        self.errors = errors or []
    
    def __str__(self):
        return f"PrivacyOperationResult(success={self.success}, " \
               f"message='{self.message}', items={self.items_processed})"


class PrivacyToolBase(QObject):
    """Base class for all privacy tools."""
    
    # Signals for GUI communication
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)       # PrivacyOperationResult
    error_occurred = pyqtSignal(str)              # error message
    status_changed = pyqtSignal(str)              # status message
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.browser_detector = BrowserDetector()
        self._is_running = False
        self._should_stop = False
    
    def get_description(self) -> str:
        """Get a description of what this tool does."""
        return "Privacy tool"
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms."""
        return ["windows", "linux", "darwin"]
    
    def is_supported(self) -> bool:
        """Check if this tool is supported on the current platform."""
        return True
    
    def preview_operation(self, **kwargs) -> Dict[str, Any]:
        """Preview what the operation will do without executing it."""
        return {"preview": "No preview available"}
    
    def execute_operation(self, **kwargs) -> PrivacyOperationResult:
        """Execute the privacy operation."""
        return PrivacyOperationResult(True, "Operation completed", 0)
    
    def is_running(self) -> bool:
        """Check if the tool is currently running."""
        return self._is_running
    
    def stop_operation(self) -> None:
        """Request to stop the current operation."""
        self._should_stop = True
        self.status_changed.emit("Stopping operation...")
    
    def _check_should_stop(self) -> bool:
        """Check if operation should be stopped."""
        return self._should_stop
    
    def _emit_progress(self, current: int, total: int, message: str) -> None:
        """Emit progress update signal."""
        self.progress_updated.emit(current, total, message)
    
    def _emit_status(self, message: str) -> None:
        """Emit status change signal."""
        self.status_changed.emit(message)
    
    def _emit_error(self, message: str) -> None:
        """Emit error signal."""
        self.error_occurred.emit(message)
    
    def _emit_complete(self, result: PrivacyOperationResult) -> None:
        """Emit operation complete signal."""
        self.operation_complete.emit(result)
    
    def _safe_delete_file(self, file_path: Path, secure: bool = False) -> bool:
        """Safely delete a file with optional secure deletion."""
        try:
            if not file_path.exists():
                return True
            
            if secure:
                return PlatformUtils.secure_delete_file(file_path)
            else:
                file_path.unlink()
                return True
                
        except Exception as e:
            self._emit_error(f"Failed to delete {file_path}: {str(e)}")
            return False
    
    def _safe_delete_directory(self, dir_path: Path, 
                              secure: bool = False) -> bool:
        """Safely delete a directory and its contents."""
        try:
            if not dir_path.exists():
                return True
            
            # Delete all files in directory
            for item in dir_path.rglob('*'):
                if item.is_file():
                    if not self._safe_delete_file(item, secure):
                        return False
                if self._check_should_stop():
                    return False
            
            # Remove empty directories
            for item in sorted(dir_path.rglob('*'), reverse=True):
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()
            
            # Remove the main directory if empty
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
            
            return True
            
        except Exception as e:
            self._emit_error(f"Failed to delete directory {dir_path}: {str(e)}")
            return False
    
    def _backup_file(self, file_path: Path, 
                    backup_dir: Optional[Path] = None) -> Optional[Path]:
        """Create a backup of a file before deletion."""
        try:
            if not file_path.exists():
                return None
            
            if backup_dir is None:
                backup_dir = file_path.parent / "privacy_backup"
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{file_path.name}.backup"
            
            # Handle duplicate backup names
            counter = 1
            while backup_path.exists():
                backup_path = backup_dir / f"{file_path.name}.backup.{counter}"
                counter += 1
            
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except Exception as e:
            self._emit_error(f"Failed to backup {file_path}: {str(e)}")
            return None
    
    def _execute_sql_on_database(self, db_path: Path, 
                                sql_commands: List[str]) -> bool:
        """Execute SQL commands on a SQLite database."""
        try:
            if not db_path.exists():
                return True
            
            # Create a temporary copy to work with
            import tempfile
            import shutil
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                temp_db_path = Path(tmp.name)
            
            shutil.copy2(db_path, temp_db_path)
            
            try:
                with sqlite3.connect(str(temp_db_path)) as conn:
                    cursor = conn.cursor()
                    for command in sql_commands:
                        cursor.execute(command)
                    conn.commit()
                
                # Replace original with modified copy
                shutil.move(str(temp_db_path), str(db_path))
                return True
                
            except Exception as e:
                # Clean up temp file on error
                if temp_db_path.exists():
                    temp_db_path.unlink()
                raise e
                
        except Exception as e:
            self._emit_error(f"Database operation failed on {db_path}: {str(e)}")
            return False
    
    def _get_database_row_count(self, db_path: Path, table: str) -> int:
        """Get the number of rows in a database table."""
        try:
            if not db_path.exists():
                return 0
            
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                return cursor.fetchone()[0]
                
        except Exception:
            return 0
    
    def _validate_browser_not_running(self, browsers: List[str]) -> bool:
        """Validate that specified browsers are not running."""
        running_browsers = []
        
        for browser in browsers:
            if self.browser_detector.is_browser_running(browser):
                running_browsers.append(browser)
        
        if running_browsers:
            browser_list = ", ".join(running_browsers)
            self._emit_error(
                f"Please close the following browsers before proceeding: "
                f"{browser_list}"
            )
            return False
        
        return True
    
    def run_in_thread(self, operation_func: Callable, **kwargs) -> QThread:
        """Run an operation in a separate thread."""
        thread = QThread()
        
        def worker():
            self._is_running = True
            self._should_stop = False
            try:
                result = operation_func(**kwargs)
                self._emit_complete(result)
            except Exception as e:
                error_result = PrivacyOperationResult(
                    False, f"Operation failed: {str(e)}", 0, [str(e)]
                )
                self._emit_complete(error_result)
            finally:
                self._is_running = False
                thread.quit()
        
        thread.started.connect(worker)
        thread.start()
        return thread