#!/usr/bin/env python3
"""
Simplified Rename Files Tool for Richard's File Utilities

A streamlined file renaming utility with essential functionality.
"""

import os
import sys
from datetime import datetime

try:
    from PyQt5.QtWidgets import (QApplication, QButtonGroup, QCheckBox,
                                 QFileDialog, QGridLayout, QGroupBox,
                                 QHBoxLayout, QLabel, QLineEdit, QListWidget,
                                 QListWidgetItem, QMessageBox, QPushButton,
                                 QRadioButton, QTextEdit, QVBoxLayout, QWidget)
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
    
    class StandardWindow(QMainWindow):
        """Fallback StandardWindow when the main one isn't available."""
        def __init__(self, title="Rename Files", window_type="file_operations", **kwargs):
            super().__init__()
            self.setWindowTitle(title)
            self.window_type = window_type
            
            # Create central widget and main layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)


class RenameWindow(StandardWindow):
    """Simplified Rename Files GUI with essential functionality."""
    
    def __init__(self):
        super().__init__(
            title="Rename Files - Richard's File Utilities",
            window_type="file_operations"
        )
        self.current_directory = ""
        self.selected_files = []
        self.init_ui()
        self._setup_menu_callbacks()
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_rename', self.clear_selected_files)
            self.menu_manager.register_callback('save_operation', self.save_rename_settings)
            self.menu_manager.register_callback('load_operation', self.load_rename_settings)
            self.menu_manager.register_callback('export_results', self.export_rename_results)
            
    def save_rename_settings(self):
        """Save current rename settings to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Rename Settings", "rename_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                settings = {
                    'directory': self.current_directory,
                    'rename_mode': self._get_current_rename_mode(),
                    'prefix_text': self.prefix_edit.text(),
                    'suffix_text': self.suffix_edit.text(),
                    'find_text': self.find_edit.text(),
                    'replace_text': self.replace_edit.text(),
                    'start_number': self.start_number_edit.text(),
                    'number_format': self.number_format_edit.text()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
                    
                QMessageBox.information(self, "Success", f"Settings saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
                
    def load_rename_settings(self):
        """Load rename settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Rename Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Apply settings
                if 'directory' in settings and settings['directory']:
                    self.current_directory = settings['directory']
                    self.directory_edit.setText(settings['directory'])
                    self.load_available_files()
                    
                if 'prefix_text' in settings:
                    self.prefix_edit.setText(settings['prefix_text'])
                if 'suffix_text' in settings:
                    self.suffix_edit.setText(settings['suffix_text'])
                    
                QMessageBox.information(self, "Success", f"Settings loaded from {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")
                
    def export_rename_results(self):
        """Export rename preview results."""
        if not self.selected_files:
            QMessageBox.information(self, "No Files", "No files selected for renaming.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Rename Results", "rename_preview.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Rename Preview Results\n")
                    f.write(f"Directory: {self.current_directory}\n")
                    f.write(f"Rename Mode: {self._get_current_rename_mode()}\n")
                    f.write(f"Total Files: {len(self.selected_files)}\n\n")
                    
                    for i, filename in enumerate(self.selected_files):
                        new_filename = self.get_new_filename(filename, i)
                        f.write(f"{filename} → {new_filename}\n")
                        
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export results: {e}")
                
    def _get_current_rename_mode(self):
        """Get the currently selected rename mode."""
        if self.add_prefix_radio.isChecked():
            return "add_prefix"
        elif self.add_suffix_radio.isChecked():
            return "add_suffix"
        elif self.lowercase_radio.isChecked():
            return "lowercase"
        elif self.uppercase_radio.isChecked():
            return "uppercase"
        elif self.replace_radio.isChecked():
            return "replace_text"
        elif self.number_radio.isChecked():
            return "add_numbers"
        return "unknown"
        
    def show_preferences(self):
        """Show Rename tool preferences."""
        QMessageBox.information(self, "Rename Preferences", 
                               "Rename tool preferences:\n\n"
                               "• Default rename patterns\n"
                               "• Backup options\n"
                               "• Confirmation settings\n"
                               "• Undo functionality\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh the current file lists."""
        if self.current_directory:
            self.load_available_files()
        else:
            QMessageBox.information(self, "Refresh", "Select a directory first to refresh.")
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Create header
        header_label = QLabel("File Rename Utility")
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
        
        # Create directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QGridLayout(dir_group)
        
        dir_layout.addWidget(QLabel("Directory:"), 0, 0)
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText("Select a directory...")
        dir_layout.addWidget(self.directory_edit, 0, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button, 0, 2)
        
        layout.addWidget(dir_group)
        
        # Create file selection area
        files_group = QGroupBox("File Selection")
        files_layout = QVBoxLayout(files_group)
        
        # Available files list
        files_layout.addWidget(QLabel("Available Files:"))
        self.available_files_list = QListWidget()
        self.available_files_list.setMaximumHeight(150)
        files_layout.addWidget(self.available_files_list)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Selected →")
        self.add_button.clicked.connect(self.add_selected_files)
        selection_layout.addWidget(self.add_button)
        
        self.add_all_button = QPushButton("Add All →")
        self.add_all_button.clicked.connect(self.add_all_files)
        selection_layout.addWidget(self.add_all_button)
        
        self.remove_button = QPushButton("← Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_files)
        selection_layout.addWidget(self.remove_button)
        
        self.clear_button = QPushButton("← Clear All")
        self.clear_button.clicked.connect(self.clear_selected_files)
        selection_layout.addWidget(self.clear_button)
        
        files_layout.addLayout(selection_layout)
        
        # Selected files list
        files_layout.addWidget(QLabel("Files to Rename:"))
        self.selected_files_list = QListWidget()
        self.selected_files_list.setMaximumHeight(150)
        files_layout.addWidget(self.selected_files_list)
        
        layout.addWidget(files_group)
        
        # Create rename options
        options_group = QGroupBox("Rename Options")
        options_layout = QGridLayout(options_group)
        
        # Create button group for radio buttons
        self.rename_mode_group = QButtonGroup()
        
        # Prefix/Suffix options
        self.add_prefix_radio = QRadioButton("Add Prefix:")
        self.add_prefix_radio.setChecked(True)
        self.rename_mode_group.addButton(self.add_prefix_radio)
        options_layout.addWidget(self.add_prefix_radio, 0, 0)
        
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("Enter prefix text...")
        options_layout.addWidget(self.prefix_edit, 0, 1)
        
        self.add_suffix_radio = QRadioButton("Add Suffix:")
        self.rename_mode_group.addButton(self.add_suffix_radio)
        options_layout.addWidget(self.add_suffix_radio, 1, 0)
        
        self.suffix_edit = QLineEdit()
        self.suffix_edit.setPlaceholderText("Enter suffix text...")
        options_layout.addWidget(self.suffix_edit, 1, 1)
        
        # Case options
        self.lowercase_radio = QRadioButton("Convert to lowercase")
        self.rename_mode_group.addButton(self.lowercase_radio)
        options_layout.addWidget(self.lowercase_radio, 2, 0)
        
        self.uppercase_radio = QRadioButton("Convert to UPPERCASE")
        self.rename_mode_group.addButton(self.uppercase_radio)
        options_layout.addWidget(self.uppercase_radio, 2, 1)
        
        # Replace text
        self.replace_radio = QRadioButton("Replace text:")
        self.rename_mode_group.addButton(self.replace_radio)
        options_layout.addWidget(self.replace_radio, 3, 0)
        
        replace_layout = QHBoxLayout()
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Find...")
        replace_layout.addWidget(self.find_edit)
        
        replace_layout.addWidget(QLabel("→"))
        
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Replace with...")
        replace_layout.addWidget(self.replace_edit)
        
        options_layout.addLayout(replace_layout, 3, 1)
        
        # Number sequence
        self.number_radio = QRadioButton("Add number sequence")
        self.rename_mode_group.addButton(self.number_radio)
        options_layout.addWidget(self.number_radio, 4, 0)
        
        number_layout = QHBoxLayout()
        number_layout.addWidget(QLabel("Start:"))
        self.start_number_edit = QLineEdit("1")
        self.start_number_edit.setMaximumWidth(60)
        number_layout.addWidget(self.start_number_edit)
        
        number_layout.addWidget(QLabel("Format:"))
        self.number_format_edit = QLineEdit("_{:03d}")
        self.number_format_edit.setPlaceholderText("_{:03d}")
        number_layout.addWidget(self.number_format_edit)
        
        options_layout.addLayout(number_layout, 4, 1)
        
        layout.addWidget(options_group)
        
        # Create preview and action area
        action_group = QGroupBox("Preview and Actions")
        action_layout = QVBoxLayout(action_group)
        
        # Preview button
        self.preview_button = QPushButton("Preview Changes")
        self.preview_button.clicked.connect(self.preview_changes)
        action_layout.addWidget(self.preview_button)
        
        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        action_layout.addWidget(self.preview_text)
        
        # Rename button
        self.rename_button = QPushButton("Apply Rename")
        self.rename_button.clicked.connect(self.apply_rename)
        self.rename_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        action_layout.addWidget(self.rename_button)
        
        layout.addWidget(action_group)
        
    def browse_directory(self):
        """Open directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.directory_edit.setText(directory)
            self.load_available_files()
            
    def load_available_files(self):
        """Load files from the selected directory."""
        self.available_files_list.clear()
        self.selected_files_list.clear()
        self.selected_files = []
        
        if not self.current_directory:
            return
            
        try:
            for filename in sorted(os.listdir(self.current_directory)):
                file_path = os.path.join(self.current_directory, filename)
                if os.path.isfile(file_path):
                    self.available_files_list.addItem(QListWidgetItem(filename))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load directory: {e}")
            
    def add_selected_files(self):
        """Add selected files to rename list."""
        for item in self.available_files_list.selectedItems():
            filename = item.text()
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.selected_files_list.addItem(QListWidgetItem(filename))
                
    def add_all_files(self):
        """Add all files to rename list."""
        for i in range(self.available_files_list.count()):
            filename = self.available_files_list.item(i).text()
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.selected_files_list.addItem(QListWidgetItem(filename))
                
    def remove_selected_files(self):
        """Remove selected files from rename list."""
        for item in self.selected_files_list.selectedItems():
            filename = item.text()
            if filename in self.selected_files:
                self.selected_files.remove(filename)
                row = self.selected_files_list.row(item)
                self.selected_files_list.takeItem(row)
                
    def clear_selected_files(self):
        """Clear all selected files."""
        self.selected_files = []
        self.selected_files_list.clear()
        
    def get_new_filename(self, original_filename, index=0):
        """Generate new filename based on selected options."""
        name, ext = os.path.splitext(original_filename)
        
        if self.add_prefix_radio.isChecked():
            prefix = self.prefix_edit.text()
            return f"{prefix}{original_filename}"
            
        elif self.add_suffix_radio.isChecked():
            suffix = self.suffix_edit.text()
            return f"{name}{suffix}{ext}"
            
        elif self.lowercase_radio.isChecked():
            return original_filename.lower()
            
        elif self.uppercase_radio.isChecked():
            return original_filename.upper()
            
        elif self.replace_radio.isChecked():
            find_text = self.find_edit.text()
            replace_text = self.replace_edit.text()
            if find_text:
                return original_filename.replace(find_text, replace_text)
                
        elif self.number_radio.isChecked():
            try:
                start_num = int(self.start_number_edit.text())
                format_str = self.number_format_edit.text()
                number = start_num + index
                number_part = format_str.format(number)
                return f"{name}{number_part}{ext}"
            except (ValueError, KeyError):
                return original_filename
                
        return original_filename
        
    def preview_changes(self):
        """Preview the rename changes."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "No files selected for renaming.")
            return
            
        preview_text = "Rename Preview:\n" + "="*50 + "\n"
        
        for i, filename in enumerate(self.selected_files):
            new_filename = self.get_new_filename(filename, i)
            preview_text += f"{filename} → {new_filename}\n"
            
        self.preview_text.setText(preview_text)
        
    def apply_rename(self):
        """Apply the rename operation."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "No files selected for renaming.")
            return
            
        # Confirm the operation
        reply = QMessageBox.question(
            self, "Confirm Rename",
            f"Are you sure you want to rename {len(self.selected_files)} files?\n\n"
            "This operation cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Perform the rename operation
        success_count = 0
        error_count = 0
        errors = []
        
        for i, filename in enumerate(self.selected_files):
            try:
                old_path = os.path.join(self.current_directory, filename)
                new_filename = self.get_new_filename(filename, i)
                new_path = os.path.join(self.current_directory, new_filename)
                
                if old_path != new_path:
                    # Check if target file already exists
                    if os.path.exists(new_path):
                        errors.append(f"{filename}: Target file already exists")
                        error_count += 1
                        continue
                        
                    os.rename(old_path, new_path)
                    success_count += 1
                    
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
                error_count += 1
                
        # Show results
        if error_count == 0:
            QMessageBox.information(
                self, "Rename Complete",
                f"Successfully renamed {success_count} files."
            )
        else:
            error_text = "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                error_text += f"\n... and {len(errors) - 10} more errors"
                
            QMessageBox.warning(
                self, "Rename Results",
                f"Renamed {success_count} files successfully.\n"
                f"{error_count} files failed:\n\n{error_text}"
            )
            
        # Refresh the file list
        self.load_available_files()
        self.preview_text.clear()


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = RenameWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()