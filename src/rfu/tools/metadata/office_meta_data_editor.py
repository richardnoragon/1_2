#!/usr/bin/env python3
"""
Office Metadata Editor Tool for Richard's File Utilities

A comprehensive office document metadata viewing and editing utility.
"""

import os
import sys
import json
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QGridLayout,
        QPushButton, QLineEdit, QLabel, QCheckBox, QGroupBox, 
        QFileDialog, QMessageBox, QProgressBar, QApplication, 
        QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
        QTableWidget, QTableWidgetItem, QTabWidget
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class OfficeMetadataWorker(QThread):
    """Worker thread for office metadata operations."""
    
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str, dict)  # file_path, metadata
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, files, operation, metadata_updates=None):
        super().__init__()
        self.files = files
        self.operation = operation
        self.metadata_updates = metadata_updates or {}
        self.is_cancelled = False
        
    def run(self):
        """Execute metadata operation."""
        try:
            total_files = len(self.files)
            
            for i, file_path in enumerate(self.files):
                if self.is_cancelled:
                    break
                    
                try:
                    if self.operation == "read":
                        metadata = self.read_metadata(file_path)
                        self.file_processed.emit(file_path, metadata)
                    elif self.operation == "write":
                        self.write_metadata(file_path, self.metadata_updates)
                        metadata = self.read_metadata(file_path)
                        self.file_processed.emit(file_path, metadata)
                        
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    self.error_occurred.emit(error_msg)
                
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                
            self.finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Worker error: {str(e)}")
    
    def read_metadata(self, file_path):
        """Read metadata from office document."""
        metadata = {
            "file_info": {},
            "document_properties": {},
            "custom_properties": {},
            "built_in_properties": {},
            "error": None
        }
        
        try:
            # Basic file information
            stat_info = os.stat(file_path)
            metadata["file_info"] = {
                "filename": os.path.basename(file_path),
                "filepath": file_path,
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(
                    stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(
                    stat_info.st_ctime).isoformat(),
                "extension": os.path.splitext(file_path)[1].lower()
            }
            
            # Try to extract office document metadata
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.docx', '.xlsx', '.pptx']:
                metadata.update(self.read_ooxml_metadata(file_path))
            elif file_ext in ['.doc', '.xls', '.ppt']:
                metadata.update(self.read_ole_metadata(file_path))
            elif file_ext == '.pdf':
                metadata.update(self.read_pdf_metadata(file_path))
            else:
                metadata["error"] = f"Unsupported file format: {file_ext}"
                
        except Exception as e:
            metadata["error"] = f"File access error: {str(e)}"
            
        return metadata
    
    def read_ooxml_metadata(self, file_path):
        """Read metadata from OOXML documents (docx, xlsx, pptx)."""
        metadata = {
            "document_properties": {},
            "custom_properties": {},
            "built_in_properties": {}
        }
        
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Read core properties
                try:
                    core_xml = zip_file.read('docProps/core.xml')
                    root = ET.fromstring(core_xml)
                    
                    # Define namespaces
                    namespaces = {
                        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                        'dc': 'http://purl.org/dc/elements/1.1/',
                        'dcterms': 'http://purl.org/dc/terms/',
                        'dcmitype': 'http://purl.org/dc/dcmitype/',
                        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                    }
                    
                    # Extract core properties
                    properties = {
                        'title': root.find('.//dc:title', namespaces),
                        'creator': root.find('.//dc:creator', namespaces),
                        'subject': root.find('.//dc:subject', namespaces),
                        'description': root.find('.//dc:description', namespaces),
                        'keywords': root.find('.//cp:keywords', namespaces),
                        'category': root.find('.//cp:category', namespaces),
                        'created': root.find('.//dcterms:created', namespaces),
                        'modified': root.find('.//dcterms:modified', namespaces),
                        'lastModifiedBy': root.find('.//cp:lastModifiedBy', namespaces),
                        'revision': root.find('.//cp:revision', namespaces)
                    }
                    
                    for key, element in properties.items():
                        if element is not None and element.text:
                            metadata["built_in_properties"][key] = element.text
                            
                except Exception as e:
                    metadata["error"] = f"Core properties error: {str(e)}"
                
                # Read app properties
                try:
                    app_xml = zip_file.read('docProps/app.xml')
                    root = ET.fromstring(app_xml)
                    
                    app_ns = {'app': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'}
                    
                    app_properties = {
                        'application': root.find('.//app:Application', app_ns),
                        'appVersion': root.find('.//app:AppVersion', app_ns),
                        'company': root.find('.//app:Company', app_ns),
                        'manager': root.find('.//app:Manager', app_ns),
                        'totalTime': root.find('.//app:TotalTime', app_ns),
                        'pages': root.find('.//app:Pages', app_ns),
                        'words': root.find('.//app:Words', app_ns),
                        'characters': root.find('.//app:Characters', app_ns),
                        'lines': root.find('.//app:Lines', app_ns),
                        'paragraphs': root.find('.//app:Paragraphs', app_ns)
                    }
                    
                    for key, element in app_properties.items():
                        if element is not None and element.text:
                            metadata["document_properties"][key] = element.text
                            
                except Exception:
                    # App properties file might not exist
                    pass
                
                # Read custom properties
                try:
                    custom_xml = zip_file.read('docProps/custom.xml')
                    root = ET.fromstring(custom_xml)
                    
                    custom_ns = {'custom': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'}
                    
                    for prop in root.findall('.//custom:property', custom_ns):
                        name = prop.get('name')
                        value_elem = prop.find('.//*')
                        if name and value_elem is not None:
                            metadata["custom_properties"][name] = value_elem.text or ""
                            
                except Exception:
                    # Custom properties file might not exist
                    pass
                    
        except Exception as e:
            metadata["error"] = f"OOXML parsing error: {str(e)}"
            
        return metadata
    
    def read_ole_metadata(self, file_path):
        """Read metadata from OLE documents (doc, xls, ppt)."""
        metadata = {
            "document_properties": {"note": "OLE format detected"},
            "custom_properties": {},
            "built_in_properties": {}
        }
        
        # OLE metadata extraction would require specialized libraries like olefile
        metadata["error"] = "OLE metadata extraction requires additional libraries (olefile, python-docx)"
        
        return metadata
    
    def read_pdf_metadata(self, file_path):
        """Read metadata from PDF documents."""
        metadata = {
            "document_properties": {},
            "custom_properties": {},
            "built_in_properties": {}
        }
        
        try:
            # Basic PDF metadata extraction without external libraries
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB
                if b'%PDF' in content:
                    metadata["document_properties"]["format"] = "PDF"
                    metadata["document_properties"]["note"] = "PDF metadata extraction requires PyPDF2 or similar library"
                else:
                    metadata["error"] = "Not a valid PDF file"
                    
        except Exception as e:
            metadata["error"] = f"PDF reading error: {str(e)}"
            
        return metadata
    
    def write_metadata(self, file_path, updates):
        """Write metadata to office document."""
        # This is a placeholder for metadata writing functionality
        # Full implementation would require specialized libraries
        raise NotImplementedError(
            "Metadata writing requires additional libraries")
    
    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True


class OfficeMetaDataEditorGUI(QMainWindow):
    """Office Metadata Editor GUI."""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.selected_files = []
        self.current_metadata = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Office Metadata Editor - Richard's File Utilities")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("Office Document Metadata Editor")
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
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel - File selection and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File selection group
        selection_group = QGroupBox("Document Selection")
        selection_layout = QGridLayout(selection_group)
        
        # File input
        selection_layout.addWidget(QLabel("Files:"), 0, 0)
        self.files_edit = QLineEdit()
        self.files_edit.setPlaceholderText("Select office documents...")
        self.files_edit.setReadOnly(True)
        selection_layout.addWidget(self.files_edit, 0, 1)
        
        # Browse buttons
        self.browse_files_button = QPushButton("Browse Documents")
        self.browse_files_button.clicked.connect(self.browse_files)
        selection_layout.addWidget(self.browse_files_button, 0, 2)
        
        self.browse_folder_button = QPushButton("Browse Folder")
        self.browse_folder_button.clicked.connect(self.browse_folder)
        selection_layout.addWidget(self.browse_folder_button, 0, 3)
        
        # Options
        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.setChecked(False)
        selection_layout.addWidget(self.recursive_check, 1, 0, 1, 2)
        
        # Supported formats info
        formats_label = QLabel("Supported: DOCX, XLSX, PPTX, DOC, XLS, PPT, PDF")
        formats_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        selection_layout.addWidget(formats_label, 1, 2, 1, 2)
        
        # Action buttons
        self.read_button = QPushButton("Read Metadata")
        self.read_button.clicked.connect(self.read_metadata)
        self.read_button.setStyleSheet("""
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
        selection_layout.addWidget(self.read_button, 2, 0, 1, 2)
        
        self.edit_button = QPushButton("Edit Metadata")
        self.edit_button.clicked.connect(self.edit_metadata)
        self.edit_button.setStyleSheet("""
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
        self.edit_button.setEnabled(False)
        selection_layout.addWidget(self.edit_button, 2, 2, 1, 2)
        
        left_layout.addWidget(selection_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to process office documents")
        progress_layout.addWidget(self.status_label)
        
        left_layout.addWidget(progress_group)
        
        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.export_button = QPushButton("Export Metadata")
        self.export_button.clicked.connect(self.export_metadata)
        self.export_button.setEnabled(False)
        actions_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        actions_layout.addWidget(self.clear_button)
        
        left_layout.addWidget(actions_group)
        
        main_splitter.addWidget(left_panel)
        
        # Right panel - Metadata display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Metadata tabs
        self.metadata_tabs = QTabWidget()
        
        # File list tab
        self.file_list_tab = QWidget()
        file_list_layout = QVBoxLayout(self.file_list_tab)
        
        file_list_layout.addWidget(QLabel("Processed Documents:"))
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(
            ["Filename", "Type", "Size", "Modified"])
        self.file_tree.itemClicked.connect(self.show_file_metadata)
        file_list_layout.addWidget(self.file_tree)
        
        self.metadata_tabs.addTab(self.file_list_tab, "Documents")
        
        # Built-in properties tab
        self.builtin_tab = QWidget()
        builtin_layout = QVBoxLayout(self.builtin_tab)
        
        builtin_layout.addWidget(QLabel("Built-in Properties:"))
        self.builtin_table = QTableWidget()
        self.builtin_table.setColumnCount(2)
        self.builtin_table.setHorizontalHeaderLabels(["Property", "Value"])
        builtin_layout.addWidget(self.builtin_table)
        
        self.metadata_tabs.addTab(self.builtin_tab, "Built-in")
        
        # Document properties tab
        self.document_tab = QWidget()
        document_layout = QVBoxLayout(self.document_tab)
        
        document_layout.addWidget(QLabel("Document Properties:"))
        self.document_table = QTableWidget()
        self.document_table.setColumnCount(2)
        self.document_table.setHorizontalHeaderLabels(["Property", "Value"])
        document_layout.addWidget(self.document_table)
        
        self.metadata_tabs.addTab(self.document_tab, "Document")
        
        # Custom properties tab
        self.custom_tab = QWidget()
        custom_layout = QVBoxLayout(self.custom_tab)
        
        custom_layout.addWidget(QLabel("Custom Properties:"))
        self.custom_table = QTableWidget()
        self.custom_table.setColumnCount(2)
        self.custom_table.setHorizontalHeaderLabels(["Property", "Value"])
        custom_layout.addWidget(self.custom_table)
        
        self.metadata_tabs.addTab(self.custom_tab, "Custom")
        
        right_layout.addWidget(self.metadata_tabs)
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 800])
        
    def browse_files(self):
        """Browse for office document files."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Office Documents", "",
            "Office Files (*.docx *.xlsx *.pptx *.doc *.xls *.ppt *.pdf);;"
            "All Files (*.*)"
        )
        if files:
            self.selected_files = files
            self.files_edit.setText(f"{len(files)} document(s) selected")
            self.edit_button.setEnabled(True)
            
    def browse_folder(self):
        """Browse for folder containing office documents."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder with Office Documents"
        )
        if folder:
            office_extensions = {'.docx', '.xlsx', '.pptx', '.doc', 
                               '.xls', '.ppt', '.pdf'}
            files = []
            
            if self.recursive_check.isChecked():
                for root, dirs, filenames in os.walk(folder):
                    for filename in filenames:
                        if any(filename.lower().endswith(ext) 
                               for ext in office_extensions):
                            files.append(os.path.join(root, filename))
            else:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if (os.path.isfile(file_path) and 
                            any(filename.lower().endswith(ext) 
                                for ext in office_extensions)):
                        files.append(file_path)
            
            self.selected_files = files
            self.files_edit.setText(f"Folder: {folder} ({len(files)} documents)")
            self.edit_button.setEnabled(True)
            
    def read_metadata(self):
        """Read metadata from selected documents."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning",
                                "Please select office documents first.")
            return
            
        self.start_operation("read")
        
    def edit_metadata(self):
        """Edit metadata for selected documents."""
        QMessageBox.information(
            self, "Edit Metadata",
            "Office metadata editing functionality requires additional "
            "libraries (python-docx, openpyxl, PyPDF2) for full document "
            "manipulation. This feature provides a foundation for metadata "
            "editing implementation."
        )
        
    def start_operation(self, operation, updates=None):
        """Start metadata operation."""
        # Clear previous results
        self.clear_results()
        
        # Setup UI for operation
        self.read_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if operation == "read":
            self.status_label.setText("Reading document metadata...")
        else:
            self.status_label.setText("Updating document metadata...")
        
        # Start worker thread
        self.worker = OfficeMetadataWorker(self.selected_files, operation, updates)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.file_processed.connect(self.add_result)
        self.worker.finished.connect(self.operation_finished)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()
        
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
        
    def add_result(self, file_path, metadata):
        """Add metadata result to the display."""
        filename = os.path.basename(file_path)
        
        # Add to file tree
        item = QTreeWidgetItem()
        item.setText(0, filename)
        
        # Determine file type
        ext = os.path.splitext(file_path)[1].lower()
        type_map = {
            '.docx': 'Word Document', '.doc': 'Word Document (Legacy)',
            '.xlsx': 'Excel Spreadsheet', '.xls': 'Excel Spreadsheet (Legacy)',
            '.pptx': 'PowerPoint Presentation', '.ppt': 'PowerPoint (Legacy)',
            '.pdf': 'PDF Document'
        }
        item.setText(1, type_map.get(ext, 'Unknown'))
        
        # File size
        if "file_info" in metadata and metadata["file_info"]:
            size = metadata["file_info"].get("size", 0)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            item.setText(2, size_str)
            
            # Modified date
            modified = metadata["file_info"].get("modified", "")
            if modified:
                try:
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    item.setText(3, dt.strftime("%Y-%m-%d %H:%M"))
                except:
                    item.setText(3, "Unknown")
        
        item.setData(0, Qt.ItemDataRole.UserRole, 
                     {"path": file_path, "metadata": metadata})
        self.file_tree.addTopLevelItem(item)
        
        # Store metadata
        self.current_metadata[file_path] = metadata
        
    def operation_finished(self):
        """Handle operation completion."""
        self.read_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        count = self.file_tree.topLevelItemCount()
        self.status_label.setText(f"Completed - {count} documents processed")
        
        # Enable action buttons
        self.export_button.setEnabled(True)
        
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
            
    def show_error(self, error_message):
        """Show error message."""
        QMessageBox.warning(self, "Error", error_message)
        
    def show_file_metadata(self, item):
        """Show detailed metadata for selected file."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and "metadata" in data:
            metadata = data["metadata"]
            
            # Update built-in properties table
            self.builtin_table.setRowCount(0)
            if "built_in_properties" in metadata:
                for key, value in metadata["built_in_properties"].items():
                    row = self.builtin_table.rowCount()
                    self.builtin_table.insertRow(row)
                    self.builtin_table.setItem(row, 0, 
                                             QTableWidgetItem(key))
                    self.builtin_table.setItem(row, 1, 
                                             QTableWidgetItem(str(value)))
            
            # Update document properties table
            self.document_table.setRowCount(0)
            if "document_properties" in metadata:
                for key, value in metadata["document_properties"].items():
                    row = self.document_table.rowCount()
                    self.document_table.insertRow(row)
                    self.document_table.setItem(row, 0, 
                                               QTableWidgetItem(key))
                    self.document_table.setItem(row, 1, 
                                               QTableWidgetItem(str(value)))
            
            # Update custom properties table
            self.custom_table.setRowCount(0)
            if "custom_properties" in metadata:
                for key, value in metadata["custom_properties"].items():
                    row = self.custom_table.rowCount()
                    self.custom_table.insertRow(row)
                    self.custom_table.setItem(row, 0, 
                                            QTableWidgetItem(key))
                    self.custom_table.setItem(row, 1, 
                                            QTableWidgetItem(str(value)))
            
            # Resize table columns
            for table in [self.builtin_table, self.document_table, self.custom_table]:
                table.resizeColumnsToContents()
            
    def export_metadata(self):
        """Export metadata to file."""
        if not self.current_metadata:
            QMessageBox.warning(self, "Warning", "No metadata to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Office Metadata", "office_metadata.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    if file_path.endswith('.json'):
                        json.dump(self.current_metadata, f, indent=2,
                                 default=str)
                    else:
                        f.write("Office Document Metadata Export\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for file_path, metadata in \
                                self.current_metadata.items():
                            f.write(f"Document: {file_path}\n")
                            f.write("-" * 30 + "\n")
                            f.write(json.dumps(metadata, indent=2,
                                             default=str))
                            f.write("\n\n")
                        
                QMessageBox.information(self, "Success",
                                        "Metadata exported successfully.")
                
            except Exception as e:
                QMessageBox.warning(self, "Error",
                                    f"Failed to export metadata: {e}")
                
    def clear_results(self):
        """Clear all results."""
        self.file_tree.clear()
        self.builtin_table.setRowCount(0)
        self.document_table.setRowCount(0)
        self.custom_table.setRowCount(0)
        self.current_metadata.clear()
        self.status_label.setText("Ready to process office documents")
        
        # Disable action buttons
        self.export_button.setEnabled(False)
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        super().closeEvent(event)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = OfficeMetaDataEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()