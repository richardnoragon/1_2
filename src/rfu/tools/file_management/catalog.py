#!/usr/bin/env python3
"""
Simplified Catalog Files Tool for Richard's File Utilities

A streamlined file cataloging utility that creates HTML reports of directory contents.
"""

import os
import sys
import webbrowser
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel,
        QCheckBox, QGroupBox, QFileDialog, QMessageBox,
        QApplication, QTextEdit
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class CatalogWindow(QMainWindow):
    """Simplified Catalog Files GUI with essential functionality."""
    
    def __init__(self):
        super().__init__()
        self.current_directory = ""
        self.last_catalog_path = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Catalog Files - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("File Catalog Generator")
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
        
        dir_layout.addWidget(QLabel("Directory to Catalog:"), 0, 0)
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText(
            "Select a directory to catalog...")
        dir_layout.addWidget(self.directory_edit, 0, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button, 0, 2)
        
        layout.addWidget(dir_group)
        
        # Create catalog options
        options_group = QGroupBox("Catalog Options")
        options_layout = QGridLayout(options_group)
        
        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.setChecked(True)
        options_layout.addWidget(self.recursive_check, 0, 0)
        
        self.show_sizes_check = QCheckBox("Show file sizes")
        self.show_sizes_check.setChecked(True)
        options_layout.addWidget(self.show_sizes_check, 0, 1)
        
        self.show_dates_check = QCheckBox("Show modification dates")
        self.show_dates_check.setChecked(True)
        options_layout.addWidget(self.show_dates_check, 1, 0)
        
        self.show_hidden_check = QCheckBox("Include hidden files")
        self.show_hidden_check.setChecked(False)
        options_layout.addWidget(self.show_hidden_check, 1, 1)
        
        layout.addWidget(options_group)
        
        # Create action buttons
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Catalog")
        self.generate_button.clicked.connect(self.generate_catalog)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.generate_button)
        
        self.open_catalog_button = QPushButton("Open Last Catalog")
        self.open_catalog_button.clicked.connect(self.open_catalog)
        self.open_catalog_button.setEnabled(False)
        button_layout.addWidget(self.open_catalog_button)
        
        layout.addLayout(button_layout)
        
        # Create preview area
        preview_group = QGroupBox("File Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.status_label = QLabel("Select a directory to begin")
        preview_layout.addWidget(self.status_label)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_file_info)
        preview_layout.addWidget(self.file_list)
        
        self.file_info_text = QTextEdit()
        self.file_info_text.setMaximumHeight(80)
        self.file_info_text.setReadOnly(True)
        preview_layout.addWidget(self.file_info_text)
        
        layout.addWidget(preview_group)
        
    def browse_directory(self):
        """Open directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Catalog", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.directory_edit.setText(directory)
            self.load_directory_preview()
            
    def load_directory_preview(self):
        """Load a preview of files in the selected directory."""
        if not self.current_directory:
            return
            
        self.file_list.clear()
        self.status_label.setText(f"Loading: {self.current_directory}")
        
        try:
            file_count = 0
            if self.recursive_check.isChecked():
                for root, dirs, files in os.walk(self.current_directory):
                    for filename in files:
                        if not self.show_hidden_check.isChecked() and filename.startswith('.'):
                            continue
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, self.current_directory)
                        self.file_list.addItem(QListWidgetItem(rel_path))
                        file_count += 1
                        if file_count >= 100:  # Limit preview to 100 files
                            break
                    if file_count >= 100:
                        break
            else:
                for filename in os.listdir(self.current_directory):
                    if not self.show_hidden_check.isChecked() and filename.startswith('.'):
                        continue
                    file_path = os.path.join(self.current_directory, filename)
                    if os.path.isfile(file_path):
                        self.file_list.addItem(QListWidgetItem(filename))
                        file_count += 1
                        
            if file_count >= 100:
                self.status_label.setText(f"Preview: {file_count}+ files (showing first 100)")
            else:
                self.status_label.setText(f"Ready: {file_count} files found")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load directory: {e}")
            self.status_label.setText("Error loading directory")
            
    def show_file_info(self, item):
        """Show information about the selected file."""
        filename = item.text()
        file_path = os.path.join(self.current_directory, filename)
        
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                file_size = stat.st_size
                
                # Format file size
                if file_size < 1024:
                    size_str = f"{file_size} bytes"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                import time
                modified_time = time.ctime(stat.st_mtime)
                
                info_text = f"File: {filename} | Size: {size_str} | Modified: {modified_time}"
                self.file_info_text.setText(info_text)
            else:
                self.file_info_text.setText(f"File not found: {filename}")
                
        except Exception as e:
            self.file_info_text.setText(f"Error reading file info: {e}")
            
    def generate_catalog(self):
        """Generate HTML catalog of the directory."""
        if not self.current_directory:
            QMessageBox.warning(self, "Warning", 
                                "Please select a directory to catalog.")
            return
            
        if not os.path.exists(self.current_directory):
            QMessageBox.warning(self, "Warning", 
                                "Selected directory does not exist.")
            return
            
        try:
            # Generate catalog filename
            dir_name = os.path.basename(self.current_directory)
            catalog_filename = f"catalog_{dir_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            catalog_path = os.path.join(self.current_directory, catalog_filename)
            
            self.status_label.setText("Generating catalog...")
            
            # Create HTML content
            html_content = self.create_html_catalog()
            
            # Write to file
            with open(catalog_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.last_catalog_path = catalog_path
            self.open_catalog_button.setEnabled(True)
            
            self.status_label.setText(f"Catalog generated: {catalog_filename}")
            
            # Ask if user wants to open the catalog
            reply = QMessageBox.question(
                self, "Catalog Generated",
                f"Catalog has been created:\n{catalog_path}\n\nWould you like to open it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_catalog()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate catalog: {e}")
            self.status_label.setText("Catalog generation failed")
            
    def create_html_catalog(self):
        """Create HTML content for the catalog."""
        dir_name = os.path.basename(self.current_directory)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>File Catalog - {dir_name}</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .file-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .file-size {{
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>File Catalog: {dir_name}</h1>
    <div class="info">
        <strong>Directory:</strong> {self.current_directory}<br>
        <strong>Generated:</strong> {timestamp}<br>
        <strong>Options:</strong> 
        {'Recursive, ' if self.recursive_check.isChecked() else ''}
        {'Sizes, ' if self.show_sizes_check.isChecked() else ''}
        {'Dates, ' if self.show_dates_check.isChecked() else ''}
        {'Hidden files' if self.show_hidden_check.isChecked() else ''}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>File Name</th>"""
                
        if self.show_sizes_check.isChecked():
            html += "<th>Size</th>"
        if self.show_dates_check.isChecked():
            html += "<th>Modified</th>"
            
        html += """
            </tr>
        </thead>
        <tbody>"""
        
        # Add file entries
        file_count = 0
        try:
            if self.recursive_check.isChecked():
                for root, dirs, files in os.walk(self.current_directory):
                    for filename in sorted(files):
                        if not self.show_hidden_check.isChecked() and filename.startswith('.'):
                            continue
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, self.current_directory)
                        html += self.create_file_row(file_path, rel_path)
                        file_count += 1
            else:
                for filename in sorted(os.listdir(self.current_directory)):
                    if not self.show_hidden_check.isChecked() and filename.startswith('.'):
                        continue
                    file_path = os.path.join(self.current_directory, filename)
                    if os.path.isfile(file_path):
                        html += self.create_file_row(file_path, filename)
                        file_count += 1
        except Exception as e:
            html += f"<tr><td colspan='3'>Error reading directory: {e}</td></tr>"
            
        html += f"""
        </tbody>
    </table>
    
    <div class="info" style="margin-top: 20px;">
        <strong>Total Files:</strong> {file_count}
    </div>
</body>
</html>"""
        
        return html
        
    def create_file_row(self, file_path, display_name):
        """Create HTML table row for a file."""
        try:
            stat = os.stat(file_path)
            
            row = f'<tr><td class="file-name">{display_name}</td>'
            
            if self.show_sizes_check.isChecked():
                file_size = stat.st_size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                row += f'<td class="file-size">{size_str}</td>'
                
            if self.show_dates_check.isChecked():
                import time
                modified_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                           time.localtime(stat.st_mtime))
                row += f'<td>{modified_time}</td>'
                
            row += '</tr>'
            return row
            
        except Exception as e:
            return f'<tr><td class="file-name">{display_name}</td><td colspan="2">Error: {e}</td></tr>'
            
    def open_catalog(self):
        """Open the last generated catalog in the default web browser."""
        if self.last_catalog_path and os.path.exists(self.last_catalog_path):
            try:
                webbrowser.open(f"file:///{self.last_catalog_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open catalog: {e}")
        else:
            QMessageBox.warning(self, "Error", "No catalog file available to open.")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = CatalogWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
