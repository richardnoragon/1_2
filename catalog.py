import os
import sys
import webbrowser
from datetime import datetime
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic

class CatalogGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI from the .ui file
        uic.loadUi("catalog.ui", self)
        
        # Initialize variables
        self.directory = ""
        self.last_catalog = None
        self.listModel = QStandardItemModel()
        self.listListView.setModel(self.listModel)
        
        # Connect signals to slots
        self.setup_connections()
        
        # Load icons and set initial state
        self.setup_icons()
        self.set_initial_state()
        
        self.show()
    
    def setup_connections(self):
        """Connect UI signals to their respective slots"""
        self.selectFolderButton.clicked.connect(self.load_directory)
        self.actionselect.triggered.connect(self.load_directory)
        self.actionexit.triggered.connect(self.close)
        self.actionopen_catalog.triggered.connect(self.open_last_catalog)
        self.catalogPushButton.clicked.connect(self.catalog)
        
    def set_initial_state(self):
        """Set the initial state of UI elements"""
        self.catalogPushButton.setEnabled(False)
        self.actionopen_catalog.setEnabled(False)
        self.status_label.setText("Select a folder to begin")
    
    def setup_icons(self):
        """Load icons from the icons folder"""
        icon_path = os.path.join(os.path.dirname(__file__), "icons")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(os.path.join(icon_path, "catalog.png")))
    
    def format_size(self, size):
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def load_directory(self):
        """Load directory and display files in the list view"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory = directory
            self.directory_label.setText(directory)
            self.update_file_list()
            self.catalogPushButton.setEnabled(True)
            self.status_label.setText("Ready to generate catalog")
    
    def update_file_list(self):
        """Update the list view with files from the selected directory"""
        self.listModel.clear()
        try:
            if self.recursiveCheckBox.isChecked():
                for root, _, files in os.walk(self.directory):
                    for file in sorted(files):
                        rel_path = os.path.relpath(os.path.join(root, file), self.directory)
                        item = QStandardItem(rel_path)
                        self.listModel.appendRow(item)
            else:
                files = sorted(os.listdir(self.directory))
                for file in files:
                    if os.path.isfile(os.path.join(self.directory, file)):
                        item = QStandardItem(file)
                        self.listModel.appendRow(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read directory: {str(e)}")
    
    def is_duplicate(self, file_path):
        """Check if a file is a duplicate by comparing its content with other files"""
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            for root, _, files in os.walk(self.directory):
                for filename in files:
                    other_path = os.path.join(root, filename)
                    if other_path != file_path and os.path.isfile(other_path):
                        try:
                            with open(other_path, 'rb') as f:
                                if content == f.read():
                                    return True
                        except:
                            continue
            return False
        except:
            return False

    def catalog(self):
        """Generate HTML catalog of files"""
        if not self.directory:
            return
            
        try:
            catalog_path = os.path.join(self.directory, "catalog.html")
            with open(catalog_path, "w", encoding='utf-8') as html:
                # Write HTML header
                html.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Catalog of {self.directory}</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2196F3; }}
                        .file-list {{ list-style: none; padding: 0; }}
                        .file-item {{ 
                            padding: 10px;
                            margin: 5px 0;
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            background: #fff;
                        }}
                        .file-item:hover {{ background: #f5f5f5; }}
                        .duplicate {{ color: #f44336; }}
                        .file-info {{ color: #666; font-size: 0.9em; }}
                    </style>
                </head>
                <body>
                    <h1>File Catalog: {os.path.basename(self.directory)}</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <ul class="file-list">
                """)
                
                # Process files
                if self.recursiveCheckBox.isChecked():
                    files_to_process = []
                    for root, _, files in os.walk(self.directory):
                        for file in files:
                            files_to_process.append((root, file))
                else:
                    files_to_process = [(self.directory, f) for f in os.listdir(self.directory) 
                                      if os.path.isfile(os.path.join(self.directory, f))]
                
                # Write file entries
                for root, filename in sorted(files_to_process):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.directory)
                    
                    try:
                        is_dup = self.identdupCheckBox.isChecked() and self.is_duplicate(file_path)
                        stats = os.stat(file_path)
                        
                        # Build file info string
                        info_parts = []
                        if self.showSizesCheckBox.isChecked():
                            info_parts.append(f"Size: {self.format_size(stats.st_size)}")
                        if self.showDatesCheckBox.isChecked():
                            mtime = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            info_parts.append(f"Modified: {mtime}")
                        
                        info_str = " | ".join(info_parts)
                        dup_class = ' class="duplicate"' if is_dup else ""
                        dup_prefix = "DUPLICATE: " if is_dup else ""
                        
                        html.write(f"""
                            <li class="file-item">
                                <div{dup_class}><a href="file:///{file_path}">{dup_prefix}{rel_path}</a></div>
                                <div class="file-info">{info_str}</div>
                            </li>
                        """)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                
                # Close HTML
                html.write("</ul></body></html>")
            
            self.last_catalog = catalog_path
            self.actionopen_catalog.setEnabled(True)
            
            reply = QMessageBox.question(
                self,
                "Catalog Created",
                f"Catalog has been created at:\n{catalog_path}\n\nWould you like to open it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_last_catalog()
                
            self.status_label.setText("Catalog generated successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create catalog: {str(e)}")
            self.status_label.setText("Error generating catalog")
    
    def open_last_catalog(self):
        """Open the last generated catalog in the default web browser"""
        if self.last_catalog and os.path.exists(self.last_catalog):
            webbrowser.open(f"file:///{self.last_catalog}")
        else:
            QMessageBox.warning(self, "Error", "No catalog file available")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = CatalogGUI()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
