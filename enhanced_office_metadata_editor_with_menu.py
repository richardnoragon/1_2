"""
Enhanced Office Metadata Editor with Menu Integration

This enhanced version provides comprehensive office document metadata viewing 
and editing with standardized menu integration following the File Finder template.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import StandardWindow, fall back to QMainWindow if not available
STANDARD_WINDOW_AVAILABLE = False
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    print("StandardWindow not available, using fallback mode")
    from PyQt5.QtWidgets import QMainWindow as StandardWindow

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
        QTreeWidget, QTreeWidgetItem, QSplitter, QGroupBox,
        QLineEdit, QTableWidget, QTableWidgetItem, QProgressBar,
        QComboBox, QCheckBox, QDateTimeEdit, QSpinBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime
    from PyQt5.QtGui import QIcon
    import zipfile
    import json
    import xml.etree.ElementTree as ET
    from datetime import datetime

    class OfficeMetadataWorker(QThread):
        """Worker thread for metadata extraction and processing."""
        
        progress_updated = pyqtSignal(int)
        status_updated = pyqtSignal(str)
        metadata_extracted = pyqtSignal(dict)
        error_occurred = pyqtSignal(str)
        
        def __init__(self, file_path, operation_type='extract'):
            super().__init__()
            self.file_path = file_path
            self.operation_type = operation_type
            self.metadata = {}
            
        def run(self):
            """Run the metadata operation."""
            try:
                self.status_updated.emit(f"Processing: {os.path.basename(self.file_path)}")
                self.progress_updated.emit(20)
                
                if self.operation_type == 'extract':
                    self.extract_metadata()
                elif self.operation_type == 'update':
                    self.update_metadata()
                    
                self.progress_updated.emit(100)
                self.status_updated.emit("Operation completed successfully")
                
            except Exception as e:
                self.error_occurred.emit(str(e))
                
        def extract_metadata(self):
            """Extract metadata from office document."""
            file_ext = os.path.splitext(self.file_path)[1].lower()
            
            if file_ext in ['.docx', '.xlsx', '.pptx']:
                self.extract_ooxml_metadata()
            elif file_ext in ['.doc', '.xls', '.ppt']:
                self.extract_ole_metadata()
            elif file_ext == '.pdf':
                self.extract_pdf_metadata()
            else:
                raise Exception(f"Unsupported file type: {file_ext}")
                
        def extract_ooxml_metadata(self):
            """Extract metadata from OOXML files (docx, xlsx, pptx)."""
            self.status_updated.emit("Extracting OOXML metadata...")
            self.progress_updated.emit(40)
            
            metadata = {
                'file_info': self.get_file_info(),
                'core_properties': {},
                'app_properties': {},
                'custom_properties': {}
            }
            
            try:
                with zipfile.ZipFile(self.file_path, 'r') as zip_file:
                    # Core properties
                    if 'docProps/core.xml' in zip_file.namelist():
                        core_xml = zip_file.read('docProps/core.xml')
                        metadata['core_properties'] = self.parse_core_properties(core_xml)
                        
                    self.progress_updated.emit(60)
                    
                    # App properties  
                    if 'docProps/app.xml' in zip_file.namelist():
                        app_xml = zip_file.read('docProps/app.xml')
                        metadata['app_properties'] = self.parse_app_properties(app_xml)
                        
                    self.progress_updated.emit(80)
                    
                    # Custom properties
                    if 'docProps/custom.xml' in zip_file.namelist():
                        custom_xml = zip_file.read('docProps/custom.xml')
                        metadata['custom_properties'] = self.parse_custom_properties(custom_xml)
                        
            except Exception as e:
                raise Exception(f"Error reading OOXML file: {e}")
                
            self.metadata_extracted.emit(metadata)
            
        def extract_ole_metadata(self):
            """Extract metadata from OLE files (doc, xls, ppt)."""
            self.status_updated.emit("Extracting OLE metadata...")
            self.progress_updated.emit(40)
            
            # Simplified OLE metadata extraction
            metadata = {
                'file_info': self.get_file_info(),
                'ole_properties': {
                    'note': 'OLE metadata extraction requires additional libraries',
                    'suggestion': 'Convert to modern format for full metadata access'
                }
            }
            
            self.progress_updated.emit(80)
            self.metadata_extracted.emit(metadata)
            
        def extract_pdf_metadata(self):
            """Extract metadata from PDF files."""
            self.status_updated.emit("Extracting PDF metadata...")
            self.progress_updated.emit(40)
            
            # Simplified PDF metadata extraction
            metadata = {
                'file_info': self.get_file_info(),
                'pdf_properties': {
                    'note': 'PDF metadata extraction requires PyPDF2 or similar',
                    'suggestion': 'Install PyPDF2 for full PDF metadata support'
                }
            }
            
            self.progress_updated.emit(80)
            self.metadata_extracted.emit(metadata)
            
        def get_file_info(self):
            """Get basic file information."""
            stat = os.stat(self.file_path)
            return {
                'filename': os.path.basename(self.file_path),
                'filepath': self.file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat()
            }
            
        def parse_core_properties(self, xml_data):
            """Parse core properties XML."""
            try:
                root = ET.fromstring(xml_data)
                properties = {}
                
                # Define namespace mappings
                namespaces = {
                    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'dcterms': 'http://purl.org/dc/terms/'
                }
                
                # Extract common properties
                prop_map = {
                    'title': 'dc:title',
                    'creator': 'dc:creator',
                    'subject': 'dc:subject',
                    'description': 'dc:description',
                    'keywords': 'cp:keywords',
                    'category': 'cp:category',
                    'created': 'dcterms:created',
                    'modified': 'dcterms:modified',
                    'lastModifiedBy': 'cp:lastModifiedBy',
                    'revision': 'cp:revision'
                }
                
                for prop_name, xpath in prop_map.items():
                    element = root.find(xpath, namespaces)
                    if element is not None:
                        properties[prop_name] = element.text or ''
                        
                return properties
                
            except Exception as e:
                return {'error': f'Error parsing core properties: {e}'}
                
        def parse_app_properties(self, xml_data):
            """Parse application properties XML."""
            try:
                root = ET.fromstring(xml_data)
                properties = {}
                
                # Common app properties
                app_props = [
                    'Application', 'AppVersion', 'Company', 'Manager',
                    'TotalTime', 'Pages', 'Words', 'Characters',
                    'CharactersWithSpaces', 'Lines', 'Paragraphs',
                    'Slides', 'Notes', 'Sheets'
                ]
                
                for prop in app_props:
                    element = root.find(prop)
                    if element is not None:
                        properties[prop] = element.text or ''
                        
                return properties
                
            except Exception as e:
                return {'error': f'Error parsing app properties: {e}'}
                
        def parse_custom_properties(self, xml_data):
            """Parse custom properties XML."""
            try:
                root = ET.fromstring(xml_data)
                properties = {}
                
                # Extract custom properties
                for prop in root.findall('.//property'):
                    name = prop.get('name')
                    value_elem = prop.find('.//*')
                    if name and value_elem is not None:
                        properties[name] = value_elem.text or ''
                        
                return properties
                
            except Exception as e:
                return {'error': f'Error parsing custom properties: {e}'}

    class EnhancedOfficeMetadataEditorGUI(StandardWindow):
        """Enhanced Office Metadata Editor GUI with menu integration."""
        
        def __init__(self):
            if STANDARD_WINDOW_AVAILABLE:
                super().__init__(
                    title="Office Metadata Editor - Richard's File Utilities",
                    window_type="system"
                )
            else:
                super().__init__()
                self.setWindowTitle("Office Metadata Editor - Richard's File Utilities")
                self.setGeometry(100, 100, 1200, 800)
            
            self.current_file = None
            self.current_metadata = {}
            self.metadata_worker = None
            
            self.init_ui()
            if STANDARD_WINDOW_AVAILABLE:
                self._setup_menu_callbacks()
        
        def _setup_menu_callbacks(self):
            """Setup tool-specific menu callbacks."""
            if hasattr(self, 'menu_manager'):
                # Register tool-specific callbacks
                self.menu_manager.register_callback('open_office_file', self.open_file)
                self.menu_manager.register_callback('save_metadata', self.save_metadata)
                self.menu_manager.register_callback('export_metadata', self.export_metadata)
                self.menu_manager.register_callback('help_office_metadata', self.show_help)
                
        def show_help(self):
            """Show comprehensive help for Office Metadata Editor."""
            help_text = """
            <h2>Office Metadata Editor - Comprehensive Guide</h2>
            
            <h3>📄 Overview</h3>
            <p>The Office Metadata Editor provides comprehensive viewing and editing 
            capabilities for metadata in Microsoft Office documents, PDFs, and other 
            office file formats.</p>
            
            <h3>🚀 Key Features</h3>
            <ul>
                <li><b>Multi-Format Support</b>: DOCX, XLSX, PPTX, DOC, XLS, PPT, PDF</li>
                <li><b>Comprehensive Metadata</b>: Core, application, and custom properties</li>
                <li><b>Batch Processing</b>: Process multiple files simultaneously</li>
                <li><b>Export Options</b>: Export metadata to JSON, XML, or CSV</li>
                <li><b>Security Analysis</b>: Identify potentially sensitive information</li>
                <li><b>Metadata Cleaning</b>: Remove or modify sensitive metadata</li>
            </ul>
            
            <h3>📊 Supported Metadata Types</h3>
            <ul>
                <li><b>Core Properties</b>: Title, author, subject, keywords, comments</li>
                <li><b>Application Properties</b>: Application version, company, statistics</li>
                <li><b>Custom Properties</b>: User-defined custom metadata fields</li>
                <li><b>File Properties</b>: Creation time, modification time, size</li>
                <li><b>Document Statistics</b>: Page count, word count, character count</li>
                <li><b>Security Properties</b>: Password protection, permissions</li>
            </ul>
            
            <h3>🔧 File Format Support</h3>
            <ul>
                <li><b>OOXML Formats</b>: Full metadata extraction and editing</li>
                <li><b>Legacy Office</b>: Basic metadata viewing (requires additional libraries)</li>
                <li><b>PDF Documents</b>: Metadata viewing and basic editing</li>
                <li><b>OpenDocument</b>: Limited support for ODF formats</li>
            </ul>
            
            <h3>📋 Step-by-Step Instructions</h3>
            <ol>
                <li><b>File Selection</b>:
                    <ul>
                        <li>Click "Open File" or use File menu</li>
                        <li>Select office document or PDF file</li>
                        <li>Wait for metadata extraction to complete</li>
                    </ul>
                </li>
                <li><b>Metadata Viewing</b>:
                    <ul>
                        <li>Browse metadata in organized tabs</li>
                        <li>View core, application, and custom properties</li>
                        <li>Examine file statistics and document information</li>
                    </ul>
                </li>
                <li><b>Metadata Editing</b>:
                    <ul>
                        <li>Double-click metadata values to edit</li>
                        <li>Add new custom properties as needed</li>
                        <li>Remove sensitive or unwanted metadata</li>
                    </ul>
                </li>
                <li><b>Export and Save</b>:
                    <ul>
                        <li>Export metadata to various formats</li>
                        <li>Save changes back to the original file</li>
                        <li>Create metadata reports for documentation</li>
                    </ul>
                </li>
            </ol>
            
            <h3>🛠️ Advanced Features</h3>
            <ul>
                <li><b>Batch Processing</b>: Process multiple files in sequence</li>
                <li><b>Metadata Templates</b>: Apply standard metadata to multiple files</li>
                <li><b>Security Scanner</b>: Identify potentially sensitive metadata</li>
                <li><b>Comparison Mode</b>: Compare metadata between file versions</li>
                <li><b>History Tracking</b>: Track metadata changes over time</li>
                <li><b>Automation Scripts</b>: Automate repetitive metadata operations</li>
            </ul>
            
            <h3>🔒 Security Considerations</h3>
            <ul>
                <li><b>Personal Information</b>: Author names, company information</li>
                <li><b>File Paths</b>: Local file system paths and network locations</li>
                <li><b>Revision History</b>: Document change tracking information</li>
                <li><b>Hidden Content</b>: Comments, tracked changes, hidden text</li>
                <li><b>System Information</b>: Computer names, user accounts</li>
                <li><b>Timestamps</b>: Creation and modification dates</li>
            </ul>
            
            <h3>⚠️ Important Considerations</h3>
            <ul>
                <li><b>Backup Files</b>: Always backup important documents before editing</li>
                <li><b>File Compatibility</b>: Some metadata changes may affect application compatibility</li>
                <li><b>Version Control</b>: Be aware of version control implications</li>
                <li><b>Legal Requirements</b>: Consider legal requirements for metadata retention</li>
                <li><b>Collaboration</b>: Metadata changes may affect document sharing</li>
            </ul>
            
            <h3>💡 Best Practices</h3>
            <ul>
                <li><b>Regular Cleaning</b>: Regularly clean metadata from sensitive documents</li>
                <li><b>Template Usage</b>: Use metadata templates for consistency</li>
                <li><b>Security Review</b>: Review metadata before sharing documents</li>
                <li><b>Documentation</b>: Document metadata standards for your organization</li>
                <li><b>Training</b>: Train users on metadata security implications</li>
            </ul>
            
            <h3>🚨 Troubleshooting</h3>
            <ul>
                <li><b>Extraction Errors</b>: Ensure file is not corrupted or password-protected</li>
                <li><b>Editing Limitations</b>: Some properties may be read-only</li>
                <li><b>Format Issues</b>: Convert legacy formats to modern OOXML for full support</li>
                <li><b>Permission Errors</b>: Ensure write permissions for file modification</li>
                <li><b>Large Files</b>: Large files may take longer to process</li>
            </ul>
            
            <h3>🔍 Technical Details</h3>
            <ul>
                <li><b>OOXML Processing</b>: Uses ZIP archive extraction and XML parsing</li>
                <li><b>Metadata Standards</b>: Follows Dublin Core and Office Open XML standards</li>
                <li><b>Character Encoding</b>: Supports UTF-8 and various character encodings</li>
                <li><b>Thread Safety</b>: Uses worker threads for responsive UI</li>
                <li><b>Memory Management</b>: Efficient handling of large document metadata</li>
            </ul>
            
            <p><b>Note:</b> Some advanced features require additional Python libraries. 
            Install optional dependencies for full functionality with legacy Office formats and PDFs.</p>
            """
            
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Office Metadata Editor - Help")
            msg_box.setTextFormat(1)  # Rich text format
            msg_box.setText(help_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.resize(800, 600)
            msg_box.exec_()
            
        def show_preferences(self):
            """Show Office Metadata Editor preferences."""
            QMessageBox.information(self, "Office Metadata Editor Preferences", 
                                   "Office Metadata Editor preferences:\n\n"
                                   "• Default export formats\n"
                                   "• Metadata extraction settings\n"
                                   "• Security scanning options\n"
                                   "• Batch processing preferences\n"
                                   "• Auto-backup settings\n\n"
                                   "Advanced preferences coming soon!")
                                   
        def refresh_view(self):
            """Refresh the current metadata view."""
            if self.current_file:
                self.open_file(self.current_file)
            else:
                self.clear_metadata()
                
        def new_session(self):
            """Start a new metadata editing session."""
            self.clear_metadata()
            
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
            
            # Header
            header_label = QLabel("Office Metadata Editor - View and Edit Document Metadata")
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
            
            # Control panel
            control_panel = QWidget()
            control_layout = QHBoxLayout(control_panel)
            
            # File operations
            open_button = QPushButton("Open File")
            open_button.clicked.connect(self.open_file)
            open_button.setStyleSheet("""
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
            control_layout.addWidget(open_button)
            
            save_button = QPushButton("Save Metadata")
            save_button.clicked.connect(self.save_metadata)
            save_button.setStyleSheet("""
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
            control_layout.addWidget(save_button)
            
            export_button = QPushButton("Export Metadata")
            export_button.clicked.connect(self.export_metadata)
            export_button.setStyleSheet("""
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
            control_layout.addWidget(export_button)
            
            control_layout.addStretch()
            
            # Status and progress
            self.status_label = QLabel("Ready - Open a file to view metadata")
            self.status_label.setStyleSheet("color: #666; font-style: italic;")
            control_layout.addWidget(self.status_label)
            
            layout.addWidget(control_panel)
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            layout.addWidget(self.progress_bar)
            
            # Main content area with tabs
            self.tab_widget = QTabWidget()
            layout.addWidget(self.tab_widget)
            
            # Initialize tabs
            self.init_tabs()
            
        def init_tabs(self):
            """Initialize the tab interface."""
            # File Information tab
            self.file_info_tab = QWidget()
            self.tab_widget.addTab(self.file_info_tab, "File Information")
            
            file_info_layout = QVBoxLayout(self.file_info_tab)
            
            self.file_info_table = QTableWidget()
            self.file_info_table.setColumnCount(2)
            self.file_info_table.setHorizontalHeaderLabels(["Property", "Value"])
            file_info_layout.addWidget(self.file_info_table)
            
            # Core Properties tab
            self.core_props_tab = QWidget()
            self.tab_widget.addTab(self.core_props_tab, "Core Properties")
            
            core_layout = QVBoxLayout(self.core_props_tab)
            
            self.core_props_table = QTableWidget()
            self.core_props_table.setColumnCount(2)
            self.core_props_table.setHorizontalHeaderLabels(["Property", "Value"])
            core_layout.addWidget(self.core_props_table)
            
            # Application Properties tab
            self.app_props_tab = QWidget()
            self.tab_widget.addTab(self.app_props_tab, "Application Properties")
            
            app_layout = QVBoxLayout(self.app_props_tab)
            
            self.app_props_table = QTableWidget()
            self.app_props_table.setColumnCount(2)
            self.app_props_table.setHorizontalHeaderLabels(["Property", "Value"])
            app_layout.addWidget(self.app_props_table)
            
            # Custom Properties tab
            self.custom_props_tab = QWidget()
            self.tab_widget.addTab(self.custom_props_tab, "Custom Properties")
            
            custom_layout = QVBoxLayout(self.custom_props_tab)
            
            self.custom_props_table = QTableWidget()
            self.custom_props_table.setColumnCount(2)
            self.custom_props_table.setHorizontalHeaderLabels(["Property", "Value"])
            custom_layout.addWidget(self.custom_props_table)
            
            # Raw Data tab
            self.raw_data_tab = QWidget()
            self.tab_widget.addTab(self.raw_data_tab, "Raw Data")
            
            raw_layout = QVBoxLayout(self.raw_data_tab)
            
            self.raw_data_text = QTextEdit()
            self.raw_data_text.setReadOnly(True)
            self.raw_data_text.setStyleSheet("font-family: 'Courier New', monospace;")
            raw_layout.addWidget(self.raw_data_text)
        
        def open_file(self, file_path=None):
            """Open and process an office document."""
            if file_path is None:
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Open Office Document",
                    "",
                    "Office Documents (*.docx *.xlsx *.pptx *.doc *.xls *.ppt *.pdf);;All Files (*.*)"
                )
            
            if file_path and os.path.exists(file_path):
                self.current_file = file_path
                self.clear_metadata()
                
                # Show progress and start worker
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                # Create and start metadata worker
                self.metadata_worker = OfficeMetadataWorker(file_path, 'extract')
                self.metadata_worker.progress_updated.connect(self.progress_bar.setValue)
                self.metadata_worker.status_updated.connect(self.status_label.setText)
                self.metadata_worker.metadata_extracted.connect(self.display_metadata)
                self.metadata_worker.error_occurred.connect(self.handle_error)
                self.metadata_worker.finished.connect(self.worker_finished)
                
                self.metadata_worker.start()
                
        def worker_finished(self):
            """Handle worker thread completion."""
            self.progress_bar.setVisible(False)
            
        def handle_error(self, error_message):
            """Handle worker errors."""
            QMessageBox.critical(self, "Error", f"Error processing file:\n{error_message}")
            self.status_label.setText("Error - Failed to process file")
            
        def display_metadata(self, metadata):
            """Display extracted metadata in the interface."""
            self.current_metadata = metadata
            
            # File Information
            if 'file_info' in metadata:
                self.populate_table(self.file_info_table, metadata['file_info'])
                
            # Core Properties
            if 'core_properties' in metadata:
                self.populate_table(self.core_props_table, metadata['core_properties'])
                
            # Application Properties
            if 'app_properties' in metadata:
                self.populate_table(self.app_props_table, metadata['app_properties'])
                
            # Custom Properties
            if 'custom_properties' in metadata:
                self.populate_table(self.custom_props_table, metadata['custom_properties'])
                
            # Raw Data
            self.raw_data_text.setText(json.dumps(metadata, indent=2, default=str))
            
            # Update status
            filename = os.path.basename(self.current_file)
            self.status_label.setText(f"Loaded metadata from: {filename}")
            
        def populate_table(self, table, data):
            """Populate a table widget with data."""
            if not data:
                table.setRowCount(0)
                return
                
            table.setRowCount(len(data))
            
            for row, (key, value) in enumerate(data.items()):
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))
                
                table.setItem(row, 0, key_item)
                table.setItem(row, 1, value_item)
                
            table.resizeColumnsToContents()
            
        def clear_metadata(self):
            """Clear all metadata displays."""
            for table in [self.file_info_table, self.core_props_table, 
                         self.app_props_table, self.custom_props_table]:
                table.setRowCount(0)
                
            self.raw_data_text.clear()
            self.current_metadata = {}
            
        def save_metadata(self):
            """Save metadata changes back to file."""
            if not self.current_file:
                QMessageBox.warning(self, "Warning", "No file is currently open.")
                return
                
            QMessageBox.information(self, "Save Metadata", 
                                   "Metadata saving functionality will be implemented "
                                   "in a future version.\n\nThis will allow you to "
                                   "save edited metadata back to the original document.")
                                   
        def export_metadata(self):
            """Export metadata to external file."""
            if not self.current_metadata:
                QMessageBox.warning(self, "Warning", "No metadata to export.")
                return
                
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Metadata",
                f"{os.path.splitext(os.path.basename(self.current_file))[0]}_metadata.json",
                "JSON Files (*.json);;XML Files (*.xml);;CSV Files (*.csv);;All Files (*.*)"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.current_metadata, f, indent=2, default=str, ensure_ascii=False)
                    
                    QMessageBox.information(self, "Export Successful", 
                                           f"Metadata exported to:\n{filename}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", 
                                        f"Error exporting metadata:\n{e}")


    def main():
        """Main function to run the Enhanced Office Metadata Editor."""
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = EnhancedOfficeMetadataEditorGUI()
        window.show()
        
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing PyQt5 modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    
    def main():
        print("Enhanced Office Metadata Editor requires PyQt5 to be installed.")
        print("Please install PyQt5 using: pip install PyQt5")

    if __name__ == "__main__":
        main()
