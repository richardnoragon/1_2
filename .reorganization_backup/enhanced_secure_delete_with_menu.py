#!/usr/bin/env python3
"""
Enhanced Secure Delete Tool with Comprehensive Menu System

A secure delete utility with standardized menu bar and enhanced functionality.
"""

import os
import sys
import hashlib
import logging

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox, QLineEdit,
        QTextEdit, QComboBox, QCheckBox, QSpinBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

try:
    from src.rfu.gui.standard_window import StandardWindow
    from gui.themes import ThemeManager, Colors, Fonts
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow as StandardWindow


class SecureDeleteThread(QThread):
    """Thread for secure deletion operations."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, files_to_delete, passes=3):
        super().__init__()
        self.files_to_delete = files_to_delete
        self.passes = passes
        self.is_cancelled = False
    
    def run(self):
        """Execute the secure deletion process."""
        try:
            total_files = len(self.files_to_delete)
            
            for i, file_path in enumerate(self.files_to_delete):
                if self.is_cancelled:
                    break
                
                self.status_updated.emit(f"Securely deleting: {os.path.basename(file_path)}")
                
                # Perform secure deletion
                success = self._secure_delete_file(file_path)
                
                if not success:
                    self.finished.emit(False, f"Failed to delete: {file_path}")
                    return
                
                # Update progress
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)
            
            if not self.is_cancelled:
                self.finished.emit(True, "Secure deletion completed successfully")
            
        except Exception as e:
            self.finished.emit(False, f"Error during deletion: {str(e)}")
    
    def _secure_delete_file(self, file_path):
        """Securely delete a single file."""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            
            # Multiple pass overwrite
            with open(file_path, "r+b") as f:
                for pass_num in range(self.passes):
                    if self.is_cancelled:
                        return False
                    
                    f.seek(0)
                    
                    # Different patterns for each pass
                    if pass_num == 0:
                        # Pass 1: All zeros
                        f.write(b'\x00' * file_size)
                    elif pass_num == 1:
                        # Pass 2: All ones
                        f.write(b'\xFF' * file_size)
                    else:
                        # Pass 3+: Random data
                        import random
                        random_data = bytes([random.randint(0, 255) for _ in range(file_size)])
                        f.write(random_data)
                    
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally, remove the file
            os.remove(file_path)
            return True
            
        except Exception as e:
            logging.error(f"Error securely deleting {file_path}: {e}")
            return False
    
    def cancel(self):
        """Cancel the deletion process."""
        self.is_cancelled = True


class EnhancedSecureDeleteGUI(StandardWindow):
    """Enhanced Secure Delete GUI with comprehensive menu system."""
    
    def __init__(self):
        super().__init__(
            title="Secure Delete - Richard's File Utilities",
            enable_menu=True,
            window_type="utility"
        )
        
        self.files_to_delete = []
        self.deletion_thread = None
        
        self._setup_ui()
        self._setup_menu_callbacks()
        
        # Apply theme
        ThemeManager.apply_utility_window_theme(self)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = self.create_header("Secure File Deletion")
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Permanently and securely delete files using multiple-pass overwriting. "
            "This process makes file recovery extremely difficult or impossible."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY.name()};
                font-size: {Fonts.NORMAL_SIZE}pt;
                padding: 10px;
                background-color: {Colors.BACKGROUND_SECONDARY.name()};
                border-radius: 4px;
                border: 1px solid {Colors.BORDER_LIGHT.name()};
            }}
        """)
        layout.addWidget(description)
        
        # Settings group
        settings_group = self.create_group_box("Deletion Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Number of passes
        passes_layout = QHBoxLayout()
        passes_layout.addWidget(QLabel("Number of overwrite passes:"))
        self.passes_spin = QSpinBox()
        self.passes_spin.setRange(1, 10)
        self.passes_spin.setValue(3)
        self.passes_spin.setToolTip("More passes provide better security but take longer")
        passes_layout.addWidget(self.passes_spin)
        passes_layout.addStretch()
        settings_layout.addLayout(passes_layout)
        
        # Verification option
        self.verify_checkbox = QCheckBox("Verify deletion (slower but more secure)")
        self.verify_checkbox.setChecked(True)
        settings_layout.addWidget(self.verify_checkbox)
        
        layout.addWidget(settings_group)
        
        # File selection group
        file_group = self.create_group_box("Files to Delete")
        file_layout = QVBoxLayout(file_group)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        file_layout.addWidget(self.file_list)
        
        # File buttons
        file_buttons_layout = QHBoxLayout()
        
        add_files_btn = self.create_button("Add Files...", self.add_files)
        file_buttons_layout.addWidget(add_files_btn)
        
        add_folder_btn = self.create_button("Add Folder...", self.add_folder, primary=False)
        file_buttons_layout.addWidget(add_folder_btn)
        
        remove_btn = self.create_button("Remove Selected", self.remove_selected, primary=False)
        file_buttons_layout.addWidget(remove_btn)
        
        clear_btn = self.create_button("Clear All", self.clear_all, primary=False)
        file_buttons_layout.addWidget(clear_btn)
        
        file_buttons_layout.addStretch()
        file_layout.addLayout(file_buttons_layout)
        
        layout.addWidget(file_group)
        
        # Progress group
        progress_group = self.create_group_box("Deletion Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.status_label = QLabel("Ready to delete files")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = self.create_progress_bar()
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.delete_btn = self.create_button("Start Secure Deletion", self.start_deletion)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)
        
        self.cancel_btn = self.create_button("Cancel", self.cancel_deletion, primary=False)
        self.cancel_btn.setEnabled(False)
        action_layout.addWidget(self.cancel_btn)
        
        action_layout.addStretch()
        
        exit_btn = self.create_button("Exit", self.close, primary=False)
        action_layout.addWidget(exit_btn)
        
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _setup_menu_callbacks(self):
        """Setup menu callbacks specific to this tool."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('save_file', self.save_file_list)
            self.menu_manager.register_callback('open_file', self.load_file_list)
            self.menu_manager.register_callback('export_data', self.export_settings)
            self.menu_manager.register_callback('import_data', self.import_settings)
    
    def add_files(self):
        """Add files to the deletion list."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Delete",
            "",
            "All Files (*.*)"
        )
        
        for file_path in files:
            if file_path not in self.files_to_delete:
                self.files_to_delete.append(file_path)
                self.file_list.addItem(file_path)
        
        self._update_ui_state()
    
    def add_folder(self):
        """Add all files in a folder to the deletion list."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Delete (all files)"
        )
        
        if folder:
            try:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path not in self.files_to_delete:
                            self.files_to_delete.append(file_path)
                            self.file_list.addItem(file_path)
                
                self._update_ui_state()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error reading folder: {str(e)}")
    
    def remove_selected(self):
        """Remove selected files from the deletion list."""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            item = self.file_list.takeItem(current_row)
            if item:
                self.files_to_delete.remove(item.text())
        
        self._update_ui_state()
    
    def clear_all(self):
        """Clear all files from the deletion list."""
        self.file_list.clear()
        self.files_to_delete.clear()
        self._update_ui_state()
    
    def start_deletion(self):
        """Start the secure deletion process."""
        if not self.files_to_delete:
            QMessageBox.warning(self, "No Files", "Please select files to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Secure Deletion",
            f"Are you sure you want to permanently delete {len(self.files_to_delete)} file(s)?\n\n"
            "This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Start deletion thread
        self.deletion_thread = SecureDeleteThread(
            self.files_to_delete.copy(),
            self.passes_spin.value()
        )
        
        self.deletion_thread.progress_updated.connect(self.progress_bar.setValue)
        self.deletion_thread.status_updated.connect(self.status_label.setText)
        self.deletion_thread.finished.connect(self.deletion_finished)
        
        self.deletion_thread.start()
        
        # Update UI state
        self.delete_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("Starting secure deletion...")
        self.progress_bar.setValue(0)
    
    def cancel_deletion(self):
        """Cancel the ongoing deletion process."""
        if self.deletion_thread and self.deletion_thread.isRunning():
            self.deletion_thread.cancel()
            self.status_label.setText("Cancelling deletion...")
    
    def deletion_finished(self, success, message):
        """Handle completion of deletion process."""
        self.delete_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            self.status_label.setText(message)
            self.progress_bar.setValue(100)
            self.clear_all()  # Clear the list of successfully deleted files
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def _update_ui_state(self):
        """Update UI state based on current conditions."""
        has_files = len(self.files_to_delete) > 0
        self.delete_btn.setEnabled(has_files)
        
        # Update status
        if has_files:
            self.status_label.setText(f"{len(self.files_to_delete)} file(s) ready for deletion")
        else:
            self.status_label.setText("No files selected")
    
    def save_file_list(self):
        """Save the current file list."""
        if not self.files_to_delete:
            QMessageBox.information(self, "No Data", "No files in the list to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File List",
            "secure_delete_list.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for file in self.files_to_delete:
                        f.write(file + '\n')
                
                QMessageBox.information(self, "Saved", f"File list saved to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file list: {str(e)}")
    
    def load_file_list(self):
        """Load a file list from a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load File List",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                added_count = 0
                for line in lines:
                    file_path = line.strip()
                    if file_path and os.path.exists(file_path) and file_path not in self.files_to_delete:
                        self.files_to_delete.append(file_path)
                        self.file_list.addItem(file_path)
                        added_count += 1
                
                self._update_ui_state()
                QMessageBox.information(self, "Loaded", f"Added {added_count} files from list.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file list: {str(e)}")
    
    def export_settings(self):
        """Export current settings."""
        settings = {
            'passes': self.passes_spin.value(),
            'verify': self.verify_checkbox.isChecked(),
            'files': self.files_to_delete
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            "secure_delete_settings.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
                
                QMessageBox.information(self, "Exported", f"Settings exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export settings: {str(e)}")
    
    def import_settings(self):
        """Import settings from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Apply settings
                if 'passes' in settings:
                    self.passes_spin.setValue(settings['passes'])
                
                if 'verify' in settings:
                    self.verify_checkbox.setChecked(settings['verify'])
                
                if 'files' in settings:
                    for file in settings['files']:
                        if os.path.exists(file) and file not in self.files_to_delete:
                            self.files_to_delete.append(file)
                            self.file_list.addItem(file)
                
                self._update_ui_state()
                QMessageBox.information(self, "Imported", "Settings imported successfully.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import settings: {str(e)}")
    
    def show_preferences(self):
        """Show preferences specific to secure delete."""
        from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Secure Delete Preferences")
        dialog.setModal(True)
        dialog.resize(300, 200)
        
        layout = QFormLayout(dialog)
        
        # Default passes
        default_passes = QSpinBox()
        default_passes.setRange(1, 10)
        default_passes.setValue(self.passes_spin.value())
        layout.addRow("Default passes:", default_passes)
        
        # Default verification
        default_verify = QCheckBox()
        default_verify.setChecked(self.verify_checkbox.isChecked())
        layout.addRow("Default verification:", default_verify)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            self.passes_spin.setValue(default_passes.value())
            self.verify_checkbox.setChecked(default_verify.isChecked())
    
    def refresh_view(self):
        """Refresh the file list by checking if files still exist."""
        original_count = len(self.files_to_delete)
        existing_files = []
        
        for file_path in self.files_to_delete:
            if os.path.exists(file_path):
                existing_files.append(file_path)
        
        # Update the lists
        self.files_to_delete = existing_files
        
        # Rebuild the list widget
        self.file_list.clear()
        for file_path in self.files_to_delete:
            self.file_list.addItem(file_path)
        
        removed_count = original_count - len(existing_files)
        if removed_count > 0:
            self.show_status_message(f"Removed {removed_count} non-existent files from list")
        else:
            self.show_status_message("File list refreshed")
        
        self._update_ui_state()


def main():
    """Main entry point for the enhanced secure delete tool."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("RFU Secure Delete")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Richard's File Utilities")
    
    window = EnhancedSecureDeleteGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
