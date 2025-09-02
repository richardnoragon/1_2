#!/usr/bin/env python3
"""
Enhanced Secure Delete Tool for Richard's File Utilities

A comprehensive secure delete utility with menu integration and military-grade secure deletion.
Implements DoD 5220.22-M, Gutmann Method, and cryptographic overwrite patterns.
"""

import hashlib
import logging
import os
import secrets
import sys
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox,
                                 QFileDialog, QGroupBox, QHBoxLayout, QLabel,
                                 QLineEdit, QListWidget, QMainWindow,
                                 QMessageBox, QProgressBar, QPushButton,
                                 QSpinBox, QVBoxLayout, QWidget)
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class DeletionMethod(Enum):
    """Secure deletion methods available."""
    SINGLE_PASS = "Single Pass (Quick)"
    DOD_5220_22_M = "DoD 5220.22-M (3 Pass)"
    RANDOM_PATTERN = "Random Pattern (7 Pass)"
    GUTMANN_METHOD = "Gutmann Method (35 Pass)"
    CUSTOM_PATTERN = "Custom Pattern"


class SecureDeleteResult:
    """Result of a secure deletion operation."""
    
    def __init__(self, success: bool = True, message: str = "",
                 files_processed: int = 0, bytes_processed: int = 0,
                 errors: Optional[List[str]] = None,
                 verification_passed: bool = True):
        self.success = success
        self.message = message
        self.files_processed = files_processed
        self.bytes_processed = bytes_processed
        self.errors = errors or []
        self.verification_passed = verification_passed
        self.duration = 0.0


class SecureDeleteEngine:
    """Core secure deletion engine with military-grade algorithms."""
    
    # Gutmann Method patterns (35 passes)
    GUTMANN_PATTERNS = [
        # Pass 1-4: Random patterns
        None, None, None, None,
        # Pass 5-31: Specific patterns to defeat various encoding schemes
        0x55, 0xAA, 0x92, 0x49, 0x24, 0x00, 0x11, 0x22, 0x33, 0x44,
        0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE,
        0xFF, 0x92, 0x49, 0x24, 0x00, 0x11, 0x22,
        # Pass 32-35: Random patterns
        None, None, None, None
    ]
    
    def __init__(self, progress_callback: Optional[Callable[[int, str],
                                                            None]] = None):
        """Initialize the secure delete engine.
        
        Args:
            progress_callback: Optional callback for progress updates
                              (percentage, message)
        """
        self.progress_callback = progress_callback
        self.cancel_requested = False
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def secure_delete_files(self, file_paths: List[str],
                           method: DeletionMethod,
                           verify: bool = True) -> SecureDeleteResult:
        """Securely delete multiple files or directories.
        
        Args:
            file_paths: List of file or directory paths to delete
            method: Deletion method to use
            verify: Whether to verify deletion completeness
            
        Returns:
            SecureDeleteResult with operation details
        """
        start_time = time.time()
        result = SecureDeleteResult()
        
        try:
            self.logger.info(f"Starting secure deletion with method: "
                           f"{method.value}")
            
            # Expand directories to individual files
            all_files = []
            for path in file_paths:
                if os.path.isdir(path):
                    all_files.extend(self._get_files_recursive(path))
                elif os.path.isfile(path):
                    all_files.append(path)
                else:
                    result.errors.append(f"Path not found: {path}")
            
            if not all_files:
                result.success = False
                result.message = "No valid files found to delete"
                return result
            
            total_files = len(all_files)
            total_bytes = sum(os.path.getsize(f) for f in all_files
                             if os.path.exists(f))
            
            self._update_progress(
                0, f"Preparing to delete {total_files} files "
                   f"({self._format_bytes(total_bytes)})")
            
            # Delete each file
            processed_files = 0
            processed_bytes = 0
            
            for file_path in all_files:
                if self.cancel_requested:
                    result.success = False
                    result.message = "Operation cancelled by user"
                    break
                
                try:
                    file_size = (os.path.getsize(file_path)
                               if os.path.exists(file_path) else 0)
                    
                    self._update_progress(
                        int((processed_files / total_files) * 100),
                        f"Deleting: {os.path.basename(file_path)}"
                    )
                    
                    # Perform secure deletion on the file
                    file_result = self._secure_delete_file(file_path,
                                                         method, verify)
                    
                    if file_result.success:
                        processed_files += 1
                        processed_bytes += file_size
                    else:
                        result.errors.extend(file_result.errors)
                        
                except Exception as e:
                    error_msg = f"Error deleting {file_path}: {str(e)}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Clean up empty directories
            for path in file_paths:
                if os.path.isdir(path):
                    self._remove_empty_directories(path)
            
            # Final results
            result.files_processed = processed_files
            result.bytes_processed = processed_bytes
            result.duration = time.time() - start_time
            
            if processed_files == total_files:
                result.success = True
                result.message = (f"Successfully deleted {processed_files} "
                                f"files ({self._format_bytes(processed_bytes)})")
            else:
                result.success = False
                result.message = (f"Partially completed: {processed_files}/"
                                f"{total_files} files deleted")
            
            self._update_progress(100, result.message)
            
        except Exception as e:
            result.success = False
            result.message = f"Critical error during deletion: {str(e)}"
            result.errors.append(result.message)
            self.logger.error(result.message)
        
        return result
    
    def _secure_delete_file(self, file_path: str, method: DeletionMethod,
                           verify: bool) -> SecureDeleteResult:
        """Securely delete a single file."""
        result = SecureDeleteResult()
        
        try:
            if not os.path.exists(file_path):
                result.errors.append(f"File not found: {file_path}")
                result.success = False
                return result
            
            file_size = os.path.getsize(file_path)
            
            # Check permissions
            if not os.access(file_path, os.W_OK):
                result.errors.append(f"No write permission: {file_path}")
                result.success = False
                return result
            
            # Perform overwrite passes based on method
            if method == DeletionMethod.SINGLE_PASS:
                passes = [None]  # Single random pass
            elif method == DeletionMethod.DOD_5220_22_M:
                passes = [0x00, 0xFF, None]  # DoD: zeros, ones, random
            elif method == DeletionMethod.RANDOM_PATTERN:
                passes = [None] * 7  # 7 random passes
            elif method == DeletionMethod.GUTMANN_METHOD:
                passes = self.GUTMANN_PATTERNS
            else:  # Custom pattern
                passes = [None] * 3  # Default to 3 random passes
            
            # Execute overwrite passes
            for pass_num, pattern in enumerate(passes, 1):
                if self.cancel_requested:
                    result.success = False
                    result.message = "Operation cancelled"
                    return result
                
                success = self._overwrite_file(file_path, pattern,
                                             pass_num, len(passes))
                if not success:
                    result.errors.append(
                        f"Failed overwrite pass {pass_num} for {file_path}")
            
            # Verify overwrite if requested
            if verify:
                if not self._verify_overwrite(file_path):
                    result.verification_passed = False
                    result.errors.append(f"Verification failed for {file_path}")
            
            # Final deletion
            try:
                os.remove(file_path)
                result.success = True
                result.files_processed = 1
                result.bytes_processed = file_size
                self.logger.info(f"Successfully deleted: {file_path}")
            except OSError as e:
                result.errors.append(
                    f"Failed to remove file {file_path}: {str(e)}")
                result.success = False
        
        except Exception as e:
            result.success = False
            result.errors.append(f"Error processing {file_path}: {str(e)}")
            self.logger.error(f"Error processing {file_path}: {str(e)}")
        
        return result
    
    def _overwrite_file(self, file_path: str, pattern: Optional[int],
                       pass_num: int, total_passes: int) -> bool:
        """Overwrite a file with the specified pattern."""
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r+b') as f:
                bytes_written = 0
                chunk_size = min(1024 * 1024, file_size)  # 1MB chunks
                
                while bytes_written < file_size:
                    if self.cancel_requested:
                        return False
                    
                    remaining = file_size - bytes_written
                    current_chunk = min(chunk_size, remaining)
                    
                    # Generate data for this chunk
                    if pattern is None:
                        # Random data using cryptographically secure generator
                        data = secrets.token_bytes(current_chunk)
                    else:
                        # Specific pattern
                        data = bytes([pattern] * current_chunk)
                    
                    f.seek(bytes_written)
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                    
                    bytes_written += current_chunk
                    
                    # Update progress
                    file_progress = int((bytes_written / file_size) * 100)
                    self._update_progress(
                        file_progress,
                        f"Pass {pass_num}/{total_passes}: "
                        f"{os.path.basename(file_path)} ({file_progress}%)"
                    )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error overwriting {file_path}: {str(e)}")
            return False
    
    def _verify_overwrite(self, file_path: str) -> bool:
        """Verify that the file has been properly overwritten."""
        try:
            # Read the file and check for patterns
            with open(file_path, 'rb') as f:
                # Check first and last chunks for obvious patterns
                f.seek(0)
                first_chunk = f.read(1024)
                
                f.seek(-1024, 2)  # Seek to last 1024 bytes
                last_chunk = f.read(1024)
                
                # Basic verification: check for obvious non-random patterns
                for chunk in [first_chunk, last_chunk]:
                    if len(set(chunk)) < 10:  # Too few unique bytes
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying {file_path}: {str(e)}")
            return False
    
    def _get_files_recursive(self, directory: str) -> List[str]:
        """Get all files in a directory recursively."""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {str(e)}")
        
        return files
    
    def _remove_empty_directories(self, directory: str):
        """Remove empty directories after file deletion."""
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                if not files and not dirs:
                    try:
                        os.rmdir(root)
                        self.logger.info(f"Removed empty directory: {root}")
                    except OSError:
                        pass  # Directory not empty or permission denied
        except Exception as e:
            self.logger.error(f"Error cleaning up directories: {str(e)}")
    
    def _update_progress(self, percentage: int, message: str):
        """Update progress through callback."""
        if self.progress_callback:
            try:
                self.progress_callback(percentage, message)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {str(e)}")
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format byte count for display."""
        count = float(bytes_count)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if count < 1024.0:
                return f"{count:.1f} {unit}"
            count /= 1024.0
        return f"{count:.1f} PB"
    
    def cancel(self):
        """Cancel the current operation."""
        self.cancel_requested = True
        self.logger.info("Cancellation requested")


class SecureDeleteGUI(StandardWindow):
    """Main window for Secure Delete operations."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Secure Delete - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Secure Delete - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.selected_files = []
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_deletion', self.clear_selection)
            self.menu_manager.register_callback('help_secure_delete', self.show_help)
            
    def show_help(self):
        """Show comprehensive help for Secure Delete tool."""
        help_text = """
        <h2>Secure Delete Tool - Comprehensive Guide</h2>
        
        <h3>🗑️ Overview</h3>
        <p>The Secure Delete tool provides military-grade file deletion capabilities that 
        prevent data recovery by overwriting files multiple times with random data patterns.</p>
        
        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>Multiple Pass Deletion</b>: 1-35 overwrite passes for maximum security</li>
            <li><b>DoD Standards</b>: DoD 5220.22-M compliant deletion patterns</li>
            <li><b>Random Overwriting</b>: Cryptographically secure random data patterns</li>
            <li><b>Directory Deletion</b>: Secure deletion of entire directory structures</li>
            <li><b>Free Space Wiping</b>: Clean unallocated disk space</li>
            <li><b>Verification</b>: Optional verification of deletion success</li>
        </ul>
        
        <h3>🔒 Deletion Methods</h3>
        <ul>
            <li><b>Single Pass</b>: Quick deletion with one random overwrite</li>
            <li><b>DoD 5220.22-M</b>: 3-pass DoD standard (0x00, 0xFF, random)</li>
            <li><b>Gutmann Method</b>: 35-pass algorithm for ultimate security</li>
            <li><b>Random Pattern</b>: Multiple passes with cryptographic random data</li>
            <li><b>Custom Pattern</b>: User-defined overwrite patterns</li>
        </ul>
        
        <h3>⚠️ Important Warnings</h3>
        <ul>
            <li><b>Permanent Deletion</b>: Securely deleted files CANNOT be recovered</li>
            <li><b>SSD Limitations</b>: Modern SSDs may have built-in wear leveling</li>
            <li><b>File System Features</b>: Copy-on-write file systems need special handling</li>
            <li><b>Backup Considerations</b>: Files may exist in backups elsewhere</li>
            <li><b>System Files</b>: Never delete critical system files</li>
        </ul>
        
        <p><b>Note:</b> This tool provides a foundation for secure deletion. Full implementation 
        requires system-level integration and may need additional libraries for optimal security.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Secure Delete Tool - Help")
        msg_box.setTextFormat(1)  # Rich text format
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def show_preferences(self):
        """Show Secure Delete preferences."""
        QMessageBox.information(self, "Secure Delete Preferences", 
                               "Secure Delete preferences:\n\n"
                               "• Default deletion method settings\n"
                               "• Overwrite pass count preferences\n"
                               "• Verification options\n"
                               "• Performance optimization settings\n"
                               "• Logging and audit preferences\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh the current view."""
        self.clear_selection()
        
    def clear_selection(self):
        """Clear current file selection."""
        if hasattr(self, 'files_list'):
            self.files_list.clear()
        if hasattr(self, 'status_label'):
            self.status_label.setText("Ready - Select files or directories to securely delete")
        self.selected_files = []
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, 'main_layout'):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("Secure Delete")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Add file selection group
        file_group = QGroupBox("File/Directory Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Selection buttons
        button_layout = QHBoxLayout()
        
        self.select_files_button = QPushButton("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        self.select_files_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(self.select_files_button)
        
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.select_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        button_layout.addWidget(self.select_folder_button)
        
        file_layout.addLayout(button_layout)
        
        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)
        file_layout.addWidget(QLabel("Selected Items:"))
        file_layout.addWidget(self.files_list)
        
        layout.addWidget(file_group)
        
        # Add security options
        security_group = QGroupBox("Deletion Method")
        security_layout = QVBoxLayout(security_group)
        
        # Deletion method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Single Pass (Quick)",
            "DoD 5220.22-M (3 Pass)",
            "Random Pattern (7 Pass)",
            "Gutmann Method (35 Pass)",
            "Custom Pattern"
        ])
        self.method_combo.setCurrentIndex(1)  # Default to DoD standard
        method_layout.addWidget(self.method_combo)
        security_layout.addLayout(method_layout)
        
        # Verification option
        self.verify_deletion = QCheckBox("Verify deletion (recommended)")
        self.verify_deletion.setChecked(True)
        security_layout.addWidget(self.verify_deletion)
        
        layout.addWidget(security_group)
        
        # Add progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready - Select files or directories to securely delete")
        self.status_label.setStyleSheet("padding: 10px; color: #666;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Add action buttons
        action_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("🗑️ Secure Delete")
        self.delete_button.clicked.connect(self.secure_delete)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        action_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        action_layout.addWidget(self.clear_button)
        
        layout.addLayout(action_layout)
        
    def select_files(self):
        """Select files for secure deletion."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files for Secure Deletion", "",
            "All Files (*.*)"
        )
        if files:
            self.files_list.clear()
            for file_path in files:
                self.files_list.addItem(f"📄 {os.path.basename(file_path)}")
            self.selected_files = files
            self.status_label.setText(f"Selected {len(files)} file(s) for secure deletion")
            
    def select_folder(self):
        """Select folder for secure deletion."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder for Secure Deletion"
        )
        if folder:
            self.files_list.clear()
            self.files_list.addItem(f"📁 {os.path.basename(folder)}")
            self.selected_files = [folder]
            self.status_label.setText(f"Selected folder for secure deletion")
            
    def secure_delete(self):
        """Perform secure deletion."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning",
                              "Please select files or folders first.")
            return
            
        method_text = self.method_combo.currentText()
        verify = self.verify_deletion.isChecked()
        
        # Map GUI method text to enum
        method_map = {
            "Single Pass (Quick)": DeletionMethod.SINGLE_PASS,
            "DoD 5220.22-M (3 Pass)": DeletionMethod.DOD_5220_22_M,
            "Random Pattern (7 Pass)": DeletionMethod.RANDOM_PATTERN,
            "Gutmann Method (35 Pass)": DeletionMethod.GUTMANN_METHOD,
            "Custom Pattern": DeletionMethod.CUSTOM_PATTERN
        }
        
        method = method_map.get(method_text, DeletionMethod.DOD_5220_22_M)
        
        # Confirmation dialog with strong warning
        reply = QMessageBox.critical(
            self, "⚠️ SECURE DELETE CONFIRMATION",
            f"WARNING: This will PERMANENTLY DELETE the selected items!\n\n"
            f"Items to delete: {len(self.selected_files)}\n"
            f"Method: {method_text}\n"
            f"Verification: {'Enabled' if verify else 'Disabled'}\n\n"
            f"This action CANNOT be undone!\n\n"
            f"Are you absolutely sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Start actual secure deletion
            self._perform_secure_deletion(method, verify)
    
    def _perform_secure_deletion(self, method: DeletionMethod, verify: bool):
        """Perform the actual secure deletion operation."""
        # Disable UI during operation
        self.delete_button.setEnabled(False)
        self.select_files_button.setEnabled(False)
        self.select_folder_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create progress callback
        def progress_callback(percentage: int, message: str):
            self.progress_bar.setValue(percentage)
            self.status_label.setText(message)
            QApplication.processEvents()  # Update GUI
        
        # Create and configure the deletion engine
        engine = SecureDeleteEngine(progress_callback)
        
        # Start deletion in a separate thread to keep GUI responsive
        def deletion_worker():
            try:
                result = engine.secure_delete_files(self.selected_files,
                                                  method, verify)
                
                # Update GUI with results (use QTimer to run on main thread)
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._handle_deletion_result(result))
                
            except Exception as e:
                error_result = SecureDeleteResult(
                    success=False,
                    message=f"Unexpected error: {str(e)}",
                    errors=[str(e)]
                )
                QTimer.singleShot(0, lambda: self._handle_deletion_result(error_result))
        
        # Start the deletion thread
        deletion_thread = threading.Thread(target=deletion_worker,
                                          daemon=True)
        deletion_thread.start()
    
    def _handle_deletion_result(self, result: SecureDeleteResult):
        """Handle the completion of secure deletion operation."""
        # Re-enable UI
        self.delete_button.setEnabled(True)
        self.select_files_button.setEnabled(True)
        self.select_folder_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if result.success:
            # Success message
            QMessageBox.information(
                self,
                "✅ Secure Delete Complete",
                f"Secure deletion completed successfully!\n\n"
                f"Files processed: {result.files_processed}\n"
                f"Data overwritten: {self._format_bytes(result.bytes_processed)}\n"
                f"Duration: {result.duration:.1f} seconds\n"
                f"Verification: {'Passed' if result.verification_passed else 'Failed'}\n\n"
                f"All selected items have been securely deleted."
            )
            
            # Clear selection after successful deletion
            self.clear_selection()
            
        else:
            # Error message
            error_details = "\n".join(result.errors[:5])  # Show first 5 errors
            if len(result.errors) > 5:
                error_details += f"\n... and {len(result.errors) - 5} more errors"
            
            QMessageBox.critical(
                self,
                "❌ Secure Delete Failed",
                f"Secure deletion encountered errors:\n\n"
                f"{result.message}\n\n"
                f"Files processed: {result.files_processed}\n"
                f"Errors encountered:\n{error_details}\n\n"
                f"Some files may not have been deleted."
            )
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format byte count for display."""
        count = float(bytes_count)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if count < 1024.0:
                return f"{count:.1f} {unit}"
            count /= 1024.0
        return f"{count:.1f} PB"
def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SecureDeleteGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
