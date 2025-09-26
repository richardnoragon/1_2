#!/usr/bin/env python3
"""
Simple Permissions Editor GUI for Richard's File Utilities
"""

import sys
import os
import stat
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QListWidget, QCheckBox,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)


class PermissionsEditorGUI(QMainWindow):
    """Simple Permissions Editor GUI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Permissions Editor - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("File Permissions Editor")
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
        
        # File selection
        file_group = QGroupBox("File/Directory Selection")
        file_layout = QVBoxLayout(file_group)
        
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_button)
        
        select_dir_button = QPushButton("Select Directory")
        select_dir_button.clicked.connect(self.select_directory)
        file_layout.addWidget(select_dir_button)
        
        self.file_label = QLabel("No file/directory selected")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Permissions checkboxes
        perms_group = QGroupBox("Permissions")
        perms_layout = QVBoxLayout(perms_group)
        
        self.read_check = QCheckBox("Read")
        self.write_check = QCheckBox("Write")
        self.execute_check = QCheckBox("Execute")
        
        perms_layout.addWidget(self.read_check)
        perms_layout.addWidget(self.write_check)
        perms_layout.addWidget(self.execute_check)
        
        layout.addWidget(perms_group)
        
        # Buttons
        load_button = QPushButton("Load Current Permissions")
        load_button.clicked.connect(self.load_permissions)
        layout.addWidget(load_button)
        
        apply_button = QPushButton("Apply Permissions")
        apply_button.clicked.connect(self.apply_permissions)
        layout.addWidget(apply_button)
        
        # Status
        self.status_list = QListWidget()
        layout.addWidget(self.status_list)
        
        self.selected_path = None
    
    def select_file(self):
        """Select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
    
    def select_directory(self):
        """Select a directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory"
        )
        if dir_path:
            self.selected_path = dir_path
            self.file_label.setText(f"Selected: {dir_path}")
    
    def load_permissions(self):
        """Load current permissions."""
        if not self.selected_path:
            QMessageBox.warning(self, "Warning", "Please select a file/directory first.")
            return
        
        try:
            file_stat = os.stat(self.selected_path)
            mode = file_stat.st_mode
            
            self.read_check.setChecked(bool(mode & stat.S_IRUSR))
            self.write_check.setChecked(bool(mode & stat.S_IWUSR))
            self.execute_check.setChecked(bool(mode & stat.S_IXUSR))
            
            self.status_list.addItem(f"Loaded permissions for {os.path.basename(self.selected_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load permissions: {e}")
    
    def apply_permissions(self):
        """Apply selected permissions."""
        if not self.selected_path:
            QMessageBox.warning(self, "Warning", "Please select a file/directory first.")
            return
        
        try:
            mode = 0
            if self.read_check.isChecked():
                mode |= stat.S_IRUSR
            if self.write_check.isChecked():
                mode |= stat.S_IWUSR
            if self.execute_check.isChecked():
                mode |= stat.S_IXUSR
            
            os.chmod(self.selected_path, mode)
            self.status_list.addItem(f"Applied permissions to {os.path.basename(self.selected_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply permissions: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = PermissionsEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
