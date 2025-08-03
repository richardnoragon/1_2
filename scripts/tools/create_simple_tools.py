#!/usr/bin/env python3
"""
Quick Fix Script for Import Issues

This script creates simple, working versions of the tools that had import issues.
"""

import os

def create_simple_checksum_gui():
    """Create a simple checksum GUI that works."""
    content = '''#!/usr/bin/env python3
"""
Simple Checksum GUI for Richard's File Utilities
"""

import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QProgressBar,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)


class ChecksumGUI(QMainWindow):
    """Simple Checksum Calculator GUI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Checksum Calculator - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("File Checksum Calculator")
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
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        select_button = QPushButton("Select File")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_button)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Calculate button
        calc_button = QPushButton("Calculate MD5 Checksum")
        calc_button.clicked.connect(self.calculate_checksum)
        layout.addWidget(calc_button)
        
        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        self.selected_file = None
    
    def select_file(self):
        """Select a file for checksum calculation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
    
    def calculate_checksum(self):
        """Calculate MD5 checksum."""
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        
        try:
            md5_hash = hashlib.md5()
            with open(self.selected_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            
            checksum = md5_hash.hexdigest()
            result = f"MD5: {checksum}"
            self.results_list.addItem(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate checksum: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
'''
    
    with open('src/utilities/analysis/check_sum.py', 'w') as f:
        f.write(content)
    print("✅ Created simple checksum GUI")


def create_simple_duplicate_finder():
    """Create a simple duplicate finder GUI."""
    content = '''#!/usr/bin/env python3
"""
Simple Duplicate Finder GUI for Richard's File Utilities
"""

import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QListWidget,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)


class DuplicateFinderApp(QMainWindow):
    """Simple Duplicate Finder GUI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate Finder - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("Duplicate File Finder")
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
        
        # Directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)
        
        select_button = QPushButton("Select Directory")
        select_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_button)
        
        self.dir_label = QLabel("No directory selected")
        dir_layout.addWidget(self.dir_label)
        
        layout.addWidget(dir_group)
        
        # Find button
        find_button = QPushButton("Find Duplicates")
        find_button.clicked.connect(self.find_duplicates)
        layout.addWidget(find_button)
        
        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        self.selected_directory = None
    
    def select_directory(self):
        """Select a directory to scan."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan"
        )
        if dir_path:
            self.selected_directory = dir_path
            self.dir_label.setText(f"Selected: {dir_path}")
    
    def find_duplicates(self):
        """Find duplicate files in the selected directory."""
        if not self.selected_directory:
            QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return
        
        self.results_list.clear()
        self.results_list.addItem("Scanning for duplicates...")
        QApplication.processEvents()
        
        try:
            file_hashes = {}
            duplicates = []
            
            for root, dirs, files in os.walk(self.selected_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        if file_hash in file_hashes:
                            duplicates.append((file_hashes[file_hash], file_path))
                        else:
                            file_hashes[file_hash] = file_path
                    except Exception:
                        continue
            
            self.results_list.clear()
            if duplicates:
                self.results_list.addItem(f"Found {len(duplicates)} duplicate pairs:")
                for original, duplicate in duplicates:
                    self.results_list.addItem(f"Original: {original}")
                    self.results_list.addItem(f"Duplicate: {duplicate}")
                    self.results_list.addItem("---")
            else:
                self.results_list.addItem("No duplicates found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan directory: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
'''
    
    with open('src/utilities/analysis/find_duplicate_files.py', 'w') as f:
        f.write(content)
    print("✅ Created simple duplicate finder GUI")


def create_simple_permissions_editor():
    """Create a simple permissions editor GUI."""
    content = '''#!/usr/bin/env python3
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
'''
    
    with open('src/utilities/system/permissions_editor.py', 'w') as f:
        f.write(content)
    print("✅ Created simple permissions editor GUI")


def create_data_anonymizer():
    """Create a data anonymizer alias."""
    content = '''#!/usr/bin/env python3
"""
Data Anonymizer - Simple alias for privacy tools.
"""

from .privacy_tools import PrivacyCleanerGUI as DataAnonymizerGUI


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = DataAnonymizerGUI()
    window.setWindowTitle("Data Anonymizer - Richard's File Utilities")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
'''
    
    with open('src/utilities/privacy/data_anonymizer.py', 'w') as f:
        f.write(content)
    print("✅ Created data anonymizer alias")


def main():
    """Main function to create all simple versions."""
    print("Creating simple versions of problematic tools...")
    print("-" * 50)
    
    create_simple_checksum_gui()
    create_simple_duplicate_finder()
    create_simple_permissions_editor()
    create_data_anonymizer()
    
    print("-" * 50)
    print("✅ All simple tool versions created!")
    print("\nThese tools now have basic functionality and should work properly.")
    print("Run 'python verify_integration.py' to test the fixes.")


if __name__ == "__main__":
    main()
