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
        QApplication,
        QCheckBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
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

        def __init__(
            self, title="Catalog Files", window_type="utility", **kwargs
        ):
            super().__init__()
            self.setWindowTitle(title)
            self.window_type = window_type

            # Create central widget and main layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)


class CatalogWindow(StandardWindow):
    """Simplified Catalog Files GUI with essential functionality."""

    def __init__(self):
        super().__init__(
            title="Catalog Files - Richard's File Utilities",
            window_type="analysis",
        )
        self.current_directory = ""
        self.last_catalog_path = ""
        self.init_ui()
        self._setup_menu_callbacks()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback(
                "new_catalog", self.clear_directory
            )
            self.menu_manager.register_callback(
                "save_catalog", self.generate_catalog
            )
            self.menu_manager.register_callback(
                "open_catalog", self.open_catalog
            )
            self.menu_manager.register_callback(
                "export_catalog", self.export_catalog_settings
            )
            # Override the standard help with our tool-specific help
            self.menu_manager.register_callback(
                "show_user_guide", self.show_help
            )
            self.menu_manager.register_callback(
                "show_preferences", self.show_preferences
            )
            self.menu_manager.register_callback("refresh", self.refresh_view)

    def clear_directory(self):
        """Clear the current directory selection."""
        self.current_directory = ""
        self.directory_edit.clear()
        self.file_list.clear()
        self.file_info_text.clear()
        self.status_label.setText("Select a directory to begin")
        self.open_catalog_button.setEnabled(False)

    def export_catalog_settings(self):
        """Export current catalog settings to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Catalog Settings",
            "catalog_settings.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                import json

                settings = {
                    "directory": self.current_directory,
                    "recursive": self.recursive_check.isChecked(),
                    "show_sizes": self.show_sizes_check.isChecked(),
                    "show_dates": self.show_dates_check.isChecked(),
                    "show_hidden": self.show_hidden_check.isChecked(),
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)

                QMessageBox.information(
                    self, "Success", f"Settings exported to {file_path}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to export settings: {e}"
                )

    def show_help(self):
        """Show help dialog for File Catalog tool."""
        help_text = """
        <h2>File Catalog Generator - Help</h2>
        
        <h3>How to Create File Catalogs:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the folder to catalog</li>
        <li><b>Configure Options:</b> Set recursive, sizes, dates, hidden files</li>
        <li><b>Generate Catalog:</b> Create HTML report of directory contents</li>
        <li><b>View Results:</b> Open generated catalog in browser</li>
        </ul>
        
        <h3>Catalog Features:</h3>
        <ul>
        <li><b>HTML Output:</b> Professional web-based catalog reports</li>
        <li><b>Recursive Scanning:</b> Include subdirectories and files</li>
        <li><b>File Metadata:</b> Show sizes, dates, and properties</li>
        <li><b>Hidden Files:</b> Option to include hidden system files</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>Documentation:</b> Document project structures</li>
        <li><b>Inventory:</b> Create file inventories for archives</li>
        <li><b>Backup Records:</b> Maintain backup content records</li>
        <li><b>Project Reports:</b> Generate project file listings</li>
        </ul>
        
        <h3>Output Options:</h3>
        <ul>
        <li><b>HTML Format:</b> Web-friendly browsable catalogs</li>
        <li><b>File Information:</b> Names, sizes, dates, paths</li>
        <li><b>Folder Structure:</b> Hierarchical directory layout</li>
        <li><b>Timestamps:</b> Creation and modification dates</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Regular Catalogs:</b> Create periodic directory snapshots</li>
        <li><b>Filter Hidden:</b> Exclude system files unless needed</li>
        <li><b>Save Settings:</b> Export/import catalog configurations</li>
        <li><b>Archive Catalogs:</b> Keep catalog records with backups</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Refresh current directory preview</li>
        </ul>
        """

        QMessageBox.information(self, "File Catalog Help", help_text)

    def show_preferences(self):
        """Show Catalog tool preferences."""
        QMessageBox.information(
            self,
            "Catalog Preferences",
            "Catalog tool preferences:\n\n"
            "• Default output formats\n"
            "• Custom HTML templates\n"
            "• File type filters\n"
            "• Catalog metadata options\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh the current directory preview."""
        if self.current_directory:
            self.load_directory_preview()
        else:
            QMessageBox.information(
                self, "Refresh", "Select a directory first to refresh."
            )

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout

        # Create header
        header_label = QLabel("File Catalog Generator")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Create directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QGridLayout(dir_group)

        dir_layout.addWidget(QLabel("Directory to Catalog:"), 0, 0)
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText(
            "Select a directory to catalog..."
        )
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
        self.generate_button.setStyleSheet(
            """
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
        """
        )
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
            file_count = self._load_files_preview()
            self._update_status_after_load(file_count)

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not load directory: {e}"
            )
            self.status_label.setText("Error loading directory")

    def _load_files_preview(self):
        """Load files for preview, handling recursive/non-recursive modes."""
        file_count = 0

        if self.recursive_check.isChecked():
            file_count = self._load_recursive_files()
        else:
            file_count = self._load_single_directory_files()

        return file_count

    def _load_recursive_files(self):
        """Load files recursively from current directory."""
        file_count = 0
        for root, dirs, files in os.walk(self.current_directory):
            for filename in files:
                if self._should_skip_hidden_file(filename):
                    continue

                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.current_directory)
                self.file_list.addItem(QListWidgetItem(rel_path))
                file_count += 1

                if file_count >= 100:  # Limit preview to 100 files
                    return file_count

        return file_count

    def _load_single_directory_files(self):
        """Load files from current directory only (non-recursive)."""
        file_count = 0
        for filename in os.listdir(self.current_directory):
            if self._should_skip_hidden_file(filename):
                continue

            file_path = os.path.join(self.current_directory, filename)
            if os.path.isfile(file_path):
                self.file_list.addItem(QListWidgetItem(filename))
                file_count += 1

        return file_count

    def _should_skip_hidden_file(self, filename):
        """Check if hidden file should be skipped based on user preference."""
        return not self.show_hidden_check.isChecked() and filename.startswith(
            "."
        )

    def _update_status_after_load(self, file_count):
        """Update status label after loading files."""
        if file_count >= 100:
            status_text = f"Preview: {file_count}+ files (showing first 100)"
            self.status_label.setText(status_text)
        else:
            self.status_label.setText(f"Ready: {file_count} files found")

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
            QMessageBox.warning(
                self, "Warning", "Please select a directory to catalog."
            )
            return

        if not os.path.exists(self.current_directory):
            QMessageBox.warning(
                self, "Warning", "Selected directory does not exist."
            )
            return

        try:
            # Generate catalog filename
            dir_name = os.path.basename(self.current_directory)
            catalog_filename = f"catalog_{dir_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            catalog_path = os.path.join(
                self.current_directory, catalog_filename
            )

            self.status_label.setText("Generating catalog...")

            # Create HTML content
            html_content = self.create_html_catalog()

            # Write to file
            with open(catalog_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.last_catalog_path = catalog_path
            self.open_catalog_button.setEnabled(True)

            self.status_label.setText(f"Catalog generated: {catalog_filename}")

            # Ask if user wants to open the catalog
            reply = QMessageBox.question(
                self,
                "Catalog Generated",
                f"Catalog has been created:\n{catalog_path}\n\nWould you like to open it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if reply == QMessageBox.Yes:
                self.open_catalog()

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to generate catalog: {e}"
            )
            self.status_label.setText("Catalog generation failed")

    def create_html_catalog(self):
        """Create HTML content for the catalog."""
        dir_name = os.path.basename(self.current_directory)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = self._create_html_header(dir_name, timestamp)
        html += self._create_html_table_header()
        html += self._create_html_file_entries()
        html += self._create_html_footer()

        return html

    def _create_html_header(self, dir_name, timestamp):
        """Create HTML header with title and info section."""
        return f"""<!DOCTYPE html>
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
        <strong>Options:</strong> {self._get_options_text()}
    </div>
    
    <table>
        <thead>"""

    def _get_options_text(self):
        """Get formatted options text based on current settings."""
        options = []
        if self.recursive_check.isChecked():
            options.append("Recursive")
        if self.show_sizes_check.isChecked():
            options.append("Sizes")
        if self.show_dates_check.isChecked():
            options.append("Dates")
        if self.show_hidden_check.isChecked():
            options.append("Hidden files")
        return ", ".join(options) if options else "None"

    def _create_html_table_header(self):
        """Create HTML table header with appropriate columns."""
        header = """
            <tr>
                <th>File Name</th>"""

        if self.show_sizes_check.isChecked():
            header += "<th>Size</th>"
        if self.show_dates_check.isChecked():
            header += "<th>Modified</th>"

        header += """
            </tr>
        </thead>
        <tbody>"""

        return header

    def _create_html_file_entries(self):
        """Create HTML entries for all files in the directory."""
        file_entries = ""

        try:
            if self.recursive_check.isChecked():
                file_entries, _ = self._process_recursive_files()
            else:
                file_entries, _ = self._process_single_directory_files()
        except Exception as e:
            file_entries = (
                f"<tr><td colspan='3'>"
                f"Error reading directory: {e}</td></tr>"
            )

        return file_entries

    def _process_recursive_files(self):
        """Process files recursively and return HTML entries with count."""
        file_entries = ""
        file_count = 0

        for root, dirs, files in os.walk(self.current_directory):
            for filename in sorted(files):
                if self._should_skip_hidden_file(filename):
                    continue

                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.current_directory)
                file_entries += self.create_file_row(file_path, rel_path)
                file_count += 1

        return file_entries, file_count

    def _process_single_directory_files(self):
        """Process files in single directory and return HTML entries/count."""
        file_entries = ""
        file_count = 0

        for filename in sorted(os.listdir(self.current_directory)):
            if self._should_skip_hidden_file(filename):
                continue

            file_path = os.path.join(self.current_directory, filename)
            if os.path.isfile(file_path):
                file_entries += self.create_file_row(file_path, filename)
                file_count += 1

        return file_entries, file_count

    def _create_html_footer(self):
        """Create HTML footer with file count and closing tags."""
        # Count files for footer
        file_count = 0
        try:
            if self.recursive_check.isChecked():
                for root, dirs, files in os.walk(self.current_directory):
                    valid_files = [
                        f
                        for f in files
                        if not self._should_skip_hidden_file(f)
                    ]
                    file_count += len(valid_files)
            else:
                file_count = len(
                    [
                        f
                        for f in os.listdir(self.current_directory)
                        if (
                            not self._should_skip_hidden_file(f)
                            and os.path.isfile(
                                os.path.join(self.current_directory, f)
                            )
                        )
                    ]
                )
        except Exception:
            file_count = 0

        return f"""
        </tbody>
    </table>
    
    <div class="info" style="margin-top: 20px;">
        <strong>Total Files:</strong> {file_count}
    </div>
</body>
</html>"""

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

                modified_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)
                )
                row += f"<td>{modified_time}</td>"

            row += "</tr>"
            return row

        except Exception as e:
            return f'<tr><td class="file-name">{display_name}</td><td colspan="2">Error: {e}</td></tr>'

    def open_catalog(self):
        """Open the last generated catalog in the default web browser."""
        if self.last_catalog_path and os.path.exists(self.last_catalog_path):
            try:
                webbrowser.open(f"file:///{self.last_catalog_path}")
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Could not open catalog: {e}"
                )
        else:
            QMessageBox.warning(
                self, "Error", "No catalog file available to open."
            )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = CatalogWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
