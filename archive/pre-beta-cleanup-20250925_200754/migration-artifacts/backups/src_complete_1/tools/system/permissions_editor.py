#!/usr/bin/env python3
"""
Enhanced Permissions Editor GUI for Richard's File Utilities
"""

import sys
import os
import stat
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QCheckBox,
    QApplication, QMessageBox, QGroupBox, QFileDialog, QMainWindow
)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class PermissionsEditorGUI(StandardWindow):
    """Enhanced Permissions Editor GUI."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Permissions Editor - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Permissions Editor - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.selected_path = None
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_permissions', self.clear_selection)
            self.menu_manager.register_callback('help_permissions', self.show_help)
            
    def show_help(self):
        """Show comprehensive help for Permissions Editor."""
        help_text = """
        <h2>Permissions Editor - Comprehensive Guide</h2>
        
        <h3>🔐 Overview</h3>
        <p>The Permissions Editor allows you to view and modify file and directory 
        permissions, controlling who can read, write, or execute files on your system.</p>
        
        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>File Permissions</b>: View and modify individual file permissions</li>
            <li><b>Directory Permissions</b>: Manage folder access controls</li>
            <li><b>Batch Operations</b>: Apply permissions to multiple files</li>
            <li><b>Security Analysis</b>: Identify potential security issues</li>
            <li><b>Permission Templates</b>: Apply common permission patterns</li>
            <li><b>Inheritance Control</b>: Manage permission inheritance</li>
        </ul>
        
        <h3>📊 Permission Types</h3>
        <ul>
            <li><b>Read (r)</b>: Allows viewing file contents or listing directory</li>
            <li><b>Write (w)</b>: Allows modifying file contents or directory structure</li>
            <li><b>Execute (x)</b>: Allows running files or accessing directories</li>
        </ul>
        
        <h3>👥 Permission Categories</h3>
        <ul>
            <li><b>Owner</b>: The user who owns the file or directory</li>
            <li><b>Group</b>: Members of the file's assigned group</li>
            <li><b>Others</b>: All other users on the system</li>
        </ul>
        
        <h3>🔧 Common Permission Patterns</h3>
        <ul>
            <li><b>644 (rw-r--r--)</b>: Standard file permissions</li>
            <li><b>755 (rwxr-xr-x)</b>: Executable files and directories</li>
            <li><b>600 (rw-------)</b>: Private files (owner only)</li>
            <li><b>700 (rwx------)</b>: Private directories (owner only)</li>
            <li><b>666 (rw-rw-rw-)</b>: Shared files (read/write for all)</li>
        </ul>
        
        <h3>⚠️ Security Considerations</h3>
        <ul>
            <li><b>Least Privilege</b>: Grant only necessary permissions</li>
            <li><b>Sensitive Files</b>: Restrict access to confidential data</li>
            <li><b>System Files</b>: Never modify critical system file permissions</li>
            <li><b>Backup First</b>: Create backups before changing permissions</li>
        </ul>
        
        <h3>🛠️ Best Practices</h3>
        <ul>
            <li><b>Regular Audits</b>: Periodically review file permissions</li>
            <li><b>Group Management</b>: Use groups for easier permission management</li>
            <li><b>Documentation</b>: Document permission changes and reasons</li>
            <li><b>Testing</b>: Test permission changes in safe environments</li>
        </ul>
        
        <p><b>Note:</b> Modifying permissions requires appropriate system privileges. 
        Some operations may require administrator rights.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Permissions Editor - Help")
        msg_box.setTextFormat(1)  # Rich text format
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def show_preferences(self):
        """Show Permissions Editor preferences."""
        QMessageBox.information(self, "Permissions Editor Preferences", 
                               "Permissions Editor preferences:\n\n"
                               "• Default permission templates\n"
                               "• Security audit settings\n"
                               "• Backup options before changes\n"
                               "• Display format preferences\n"
                               "• Warning and confirmation settings\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh the current view."""
        if self.selected_path:
            self.load_permissions()
        else:
            self.clear_selection()
        
    def clear_selection(self):
        """Clear current selection and reset interface."""
        self.selected_path = None
        if hasattr(self, 'file_label'):
            self.file_label.setText("No file/directory selected")
        if hasattr(self, 'read_check'):
            self.read_check.setChecked(False)
            self.write_check.setChecked(False)
            self.execute_check.setChecked(False)
        if hasattr(self, 'status_list'):
            self.status_list.clear()
        
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
        
        # Selection buttons
        button_layout = QHBoxLayout()
        
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self.select_file)
        select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(select_file_button)
        
        select_dir_button = QPushButton("Select Directory")
        select_dir_button.clicked.connect(self.select_directory)
        select_dir_button.setStyleSheet("""
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
        button_layout.addWidget(select_dir_button)
        
        file_layout.addLayout(button_layout)
        
        self.file_label = QLabel("No file/directory selected")
        self.file_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Permissions checkboxes
        perms_group = QGroupBox("Permissions")
        perms_layout = QVBoxLayout(perms_group)
        
        self.read_check = QCheckBox("Read (r) - View file contents or list directory")
        self.write_check = QCheckBox("Write (w) - Modify file contents or directory structure")
        self.execute_check = QCheckBox("Execute (x) - Run file or access directory")
        
        for checkbox in [self.read_check, self.write_check, self.execute_check]:
            checkbox.setStyleSheet("padding: 5px;")
        
        perms_layout.addWidget(self.read_check)
        perms_layout.addWidget(self.write_check)
        perms_layout.addWidget(self.execute_check)
        
        layout.addWidget(perms_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        load_button = QPushButton("Load Current Permissions")
        load_button.clicked.connect(self.load_permissions)
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        control_layout.addWidget(load_button)
        
        apply_button = QPushButton("Apply Permissions")
        apply_button.clicked.connect(self.apply_permissions)
        apply_button.setStyleSheet("""
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
        control_layout.addWidget(apply_button)
        
        clear_button = QPushButton("Clear Selection")
        clear_button.clicked.connect(self.clear_selection)
        control_layout.addWidget(clear_button)
        
        layout.addLayout(control_layout)
        
        # Status
        status_group = QGroupBox("Status and Log")
        status_layout = QVBoxLayout(status_group)
        
        self.status_list = QListWidget()
        self.status_list.setMaximumHeight(150)
        status_layout.addWidget(self.status_list)
        
        layout.addWidget(status_group)
    
    def select_file(self):
        """Select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.status_list.addItem(f"File selected: {os.path.basename(file_path)}")
    
    def select_directory(self):
        """Select a directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory"
        )
        if dir_path:
            self.selected_path = dir_path
            self.file_label.setText(f"Selected: {dir_path}")
            self.status_list.addItem(f"Directory selected: {os.path.basename(dir_path)}")
    
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
            
            # Format permission string
            perm_str = stat.filemode(mode)
            self.status_list.addItem(f"Loaded permissions: {perm_str} for {os.path.basename(self.selected_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load permissions: {e}")
            self.status_list.addItem(f"Error loading permissions: {e}")
    
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
            
            # Confirmation dialog
            perm_str = ""
            perm_str += "r" if self.read_check.isChecked() else "-"
            perm_str += "w" if self.write_check.isChecked() else "-"
            perm_str += "x" if self.execute_check.isChecked() else "-"
            
            reply = QMessageBox.question(
                self, "Confirm Permission Change",
                f"Apply permissions '{perm_str}' to:\n{self.selected_path}\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.chmod(self.selected_path, mode)
                self.status_list.addItem(f"Applied permissions: {perm_str} to {os.path.basename(self.selected_path)}")
                QMessageBox.information(self, "Success", "Permissions applied successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply permissions: {e}")
            self.status_list.addItem(f"Error applying permissions: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = PermissionsEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
