"""
Base class for Software Maintenance Toolkit operations

This module provides the foundational MaintenanceToolBase class that serves as
the parent class for all software maintenance operations, providing common
functionality for progress tracking, error handling, logging, and safety protocols.
"""

import os
import sys
import time
import logging
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from PyQt5.QtCore import QObject, pyqtSignal, QThread
    from PyQt5.QtWidgets import QMessageBox
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Create dummy classes for when PyQt5 is not available
    class QObject:
        pass
    class pyqtSignal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass


class MaintenanceToolBase(QObject if PYQT_AVAILABLE else object):
    """
    Base class for all software maintenance tools providing common functionality
    including progress tracking, error handling, logging, and safety protocols.
    """
    
    # PyQt signals for GUI communication
    if PYQT_AVAILABLE:
        progress_updated = pyqtSignal(int)  # Progress percentage (0-100)
        status_updated = pyqtSignal(str)    # Status message
        error_occurred = pyqtSignal(str)    # Error message
        operation_completed = pyqtSignal(bool, str)  # Success, message
        log_message = pyqtSignal(str, str)  # Level, message
    
    def __init__(self, tool_name: str, log_level: int = logging.INFO):
        """
        Initialize the maintenance tool base.
        
        Args:
            tool_name: Name of the specific tool
            log_level: Logging level for this tool
        """
        if PYQT_AVAILABLE:
            super().__init__()
        
        self.tool_name = tool_name
        self.is_running = False
        self.is_cancelled = False
        self.progress = 0
        self.current_status = "Ready"
        self.start_time = None
        self.end_time = None
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
        # Create necessary directories
        self._create_directories()
        
        # Safety and backup settings
        self.backup_enabled = True
        self.create_restore_points = True
        self.require_admin = False
        
        # Progress tracking
        self.total_steps = 0
        self.current_step = 0
        self.step_weights = {}  # For weighted progress calculation
        
        self.log_info(f"{self.tool_name} initialized successfully")
    
    def _setup_logging(self, log_level: int) -> logging.Logger:
        """Setup logging for the maintenance tool."""
        logger = logging.getLogger(f"software_maintenance.{self.tool_name.lower().replace(' ', '_')}")
        logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("software_maintenance/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create file handler
        log_file = log_dir / f"{self.tool_name.lower().replace(' ', '_')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers if they don't exist
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _create_directories(self):
        """Create necessary directories for the maintenance tool."""
        directories = [
            "software_maintenance/logs",
            "software_maintenance/backups",
            "software_maintenance/temp",
            "software_maintenance/reports",
            "software_maintenance/config"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def set_progress_steps(self, steps: List[str], weights: Optional[Dict[str, float]] = None):
        """
        Set the progress steps for the operation.
        
        Args:
            steps: List of step names
            weights: Optional weights for each step (for weighted progress)
        """
        self.total_steps = len(steps)
        self.current_step = 0
        self.step_weights = weights or {}
        self.log_info(f"Progress tracking initialized with {self.total_steps} steps")
    
    def update_progress(self, step_name: str = None, percentage: int = None):
        """
        Update the progress of the current operation.
        
        Args:
            step_name: Name of the current step
            percentage: Direct percentage (0-100) or None to auto-calculate
        """
        if percentage is not None:
            self.progress = max(0, min(100, percentage))
        elif self.total_steps > 0:
            if step_name and step_name in self.step_weights:
                # Use weighted progress
                completed_weight = sum(
                    self.step_weights.get(step, 1.0) 
                    for step in list(self.step_weights.keys())[:self.current_step]
                )
                total_weight = sum(self.step_weights.values())
                self.progress = int((completed_weight / total_weight) * 100)
            else:
                # Use simple step-based progress
                self.progress = int((self.current_step / self.total_steps) * 100)
        
        if PYQT_AVAILABLE:
            self.progress_updated.emit(self.progress)
        
        if step_name:
            self.update_status(f"Step {self.current_step + 1}/{self.total_steps}: {step_name}")
    
    def update_status(self, status: str):
        """Update the current status message."""
        self.current_status = status
        self.log_info(f"Status: {status}")
        
        if PYQT_AVAILABLE:
            self.status_updated.emit(status)
    
    def next_step(self, step_name: str = None):
        """Move to the next step and update progress."""
        self.current_step += 1
        self.update_progress(step_name)
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
        if PYQT_AVAILABLE:
            self.log_message.emit("INFO", message)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
        if PYQT_AVAILABLE:
            self.log_message.emit("WARNING", message)
    
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
        if PYQT_AVAILABLE:
            self.log_message.emit("ERROR", message)
            self.error_occurred.emit(message)
    
    def cancel_operation(self):
        """Cancel the current operation."""
        self.is_cancelled = True
        self.log_info("Operation cancelled by user")
        self.update_status("Operation cancelled")
    
    def is_admin(self) -> bool:
        """Check if the current process has administrative privileges."""
        try:
            if sys.platform == "win32":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception as e:
            self.log_warning(f"Could not check admin privileges: {e}")
            return False
    
    def request_admin_privileges(self) -> bool:
        """Request administrative privileges if needed."""
        if self.is_admin():
            return True
        
        if not self.require_admin:
            return True
        
        self.log_warning("Administrative privileges required but not available")
        return False
    
    def create_backup(self, source_path: str, backup_name: str = None) -> Optional[str]:
        """
        Create a backup of a file or directory.
        
        Args:
            source_path: Path to backup
            backup_name: Optional custom backup name
            
        Returns:
            Path to backup or None if failed
        """
        if not self.backup_enabled:
            return None
        
        try:
            source = Path(source_path)
            if not source.exists():
                self.log_warning(f"Source path does not exist: {source_path}")
                return None
            
            # Create backup directory
            backup_dir = Path("software_maintenance/backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine backup name
            if backup_name is None:
                backup_name = source.name
            
            backup_path = backup_dir / backup_name
            
            # Copy file or directory
            import shutil
            if source.is_file():
                shutil.copy2(source, backup_path)
            else:
                shutil.copytree(source, backup_path)
            
            self.log_info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.log_error(f"Failed to create backup: {e}")
            return None
    
    def validate_operation(self) -> bool:
        """
        Validate that the operation can be performed safely.
        Override in subclasses for specific validation logic.
        """
        if self.require_admin and not self.is_admin():
            self.log_error("Administrative privileges required")
            return False
        
        return True
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during operation."""
        try:
            temp_dir = Path("software_maintenance/temp")
            if temp_dir.exists():
                import shutil
                for item in temp_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                self.log_info("Temporary files cleaned up")
        except Exception as e:
            self.log_warning(f"Failed to cleanup temp files: {e}")
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get a summary of the operation."""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "tool_name": self.tool_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "progress": self.progress,
            "status": self.current_status,
            "was_cancelled": self.is_cancelled,
            "total_steps": self.total_steps,
            "completed_steps": self.current_step
        }
    
    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """
        Execute the main operation of the tool.
        Must be implemented by subclasses.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def run(self, **kwargs) -> bool:
        """
        Main entry point to run the tool with full lifecycle management.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.is_running = True
            self.is_cancelled = False
            self.start_time = datetime.now()
            self.progress = 0
            
            self.log_info(f"Starting {self.tool_name} operation")
            self.update_status("Initializing...")
            
            # Validate operation
            if not self.validate_operation():
                self.log_error("Operation validation failed")
                return False
            
            # Execute the main operation
            result = self.execute(**kwargs)
            
            # Update completion status
            self.end_time = datetime.now()
            self.progress = 100 if result else self.progress
            
            if result:
                self.update_status("Operation completed successfully")
                self.log_info(f"{self.tool_name} completed successfully")
            else:
                self.update_status("Operation failed")
                self.log_error(f"{self.tool_name} operation failed")
            
            # Emit completion signal
            if PYQT_AVAILABLE:
                self.operation_completed.emit(result, self.current_status)
            
            return result
            
        except Exception as e:
            self.log_error(f"Unexpected error in {self.tool_name}: {e}")
            self.end_time = datetime.now()
            self.update_status(f"Error: {str(e)}")
            
            if PYQT_AVAILABLE:
                self.operation_completed.emit(False, f"Error: {str(e)}")
            
            return False
        
        finally:
            self.is_running = False
            self.cleanup_temp_files()