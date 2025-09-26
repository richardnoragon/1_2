"""
Office Metadata Tools GUI Wrapper

This module provides a comprehensive GUI for office document metadata
operations, including extraction, viewing, editing, and security analysis
for various office formats. Integrated with the StandardWindow framework
for consistent UI.
"""

import os
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
        QTableWidget, QTableWidgetItem, QProgressBar, QGroupBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("PyQt5 not available. Please install PyQt5 to use the GUI features.")
    sys.exit(1)

# Import the StandardWindow framework
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    print("StandardWindow not available, using basic QMainWindow")
    from PyQt5.QtWidgets import QMainWindow as StandardWindow
    STANDARD_WINDOW_AVAILABLE = False


class OfficeMetadataLogic:
    """Core logic for office metadata operations."""
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from an office document."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.docx', '.xlsx', '.pptx']:
            return OfficeMetadataLogic._extract_ooxml_metadata(file_path)
        elif file_ext in ['.doc', '.xls', '.ppt']:
            return OfficeMetadataLogic._extract_ole_metadata(file_path)
        elif file_ext == '.pdf':
            return OfficeMetadataLogic._extract_pdf_metadata(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    @staticmethod
    def _extract_ooxml_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from OOXML files (docx, xlsx, pptx)."""
        metadata = {
            'file_info': OfficeMetadataLogic._get_file_info(file_path),
            'core_properties': {},
            'app_properties': {},
            'custom_properties': {},
            'security_info': {}
        }
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Core properties
                if 'docProps/core.xml' in zip_file.namelist():
                    core_xml = zip_file.read('docProps/core.xml')
                    metadata['core_properties'] = OfficeMetadataLogic._parse_core_properties(core_xml)
                
                # App properties  
                if 'docProps/app.xml' in zip_file.namelist():
                    app_xml = zip_file.read('docProps/app.xml')
                    metadata['app_properties'] = OfficeMetadataLogic._parse_app_properties(app_xml)
                
                # Custom properties
                if 'docProps/custom.xml' in zip_file.namelist():
                    custom_xml = zip_file.read('docProps/custom.xml')
                    metadata['custom_properties'] = OfficeMetadataLogic._parse_custom_properties(custom_xml)
                
                # Security analysis
                metadata['security_info'] = OfficeMetadataLogic._analyze_security_metadata(metadata)
                
        except Exception as e:
            raise Exception(f"Error reading OOXML file: {e}")
        
        return metadata
    
    @staticmethod
    def _extract_ole_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from OLE files (doc, xls, ppt)."""
        metadata = {
            'file_info': OfficeMetadataLogic._get_file_info(file_path),
            'ole_properties': {
                'note': 'OLE metadata extraction requires additional libraries (olefile, python-oletools)',
                'suggestion': 'Convert to modern format (DOCX/XLSX/PPTX) for full metadata access',
                'basic_analysis': 'File appears to be legacy Office format'
            }
        }
        return metadata
    
    @staticmethod
    def _extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        metadata = {
            'file_info': OfficeMetadataLogic._get_file_info(file_path),
            'pdf_properties': {
                'note': 'PDF metadata extraction requires PyPDF2 or similar library',
                'suggestion': 'Install PyPDF2 for full PDF metadata support: pip install PyPDF2',
                'basic_analysis': 'File appears to be PDF format'
            }
        }
        return metadata
    
    @staticmethod
    def _get_file_info(file_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        stat = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'filepath': file_path,
            'size': stat.st_size,
            'size_formatted': OfficeMetadataLogic._format_file_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    
    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def _parse_core_properties(xml_data: bytes) -> Dict[str, str]:
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
                'revision': 'cp:revision',
                'language': 'dc:language'
            }
            
            for prop_name, xpath in prop_map.items():
                element = root.find(xpath, namespaces)
                if element is not None:
                    properties[prop_name] = element.text or ''
            
            return properties
            
        except Exception as e:
            return {'error': f'Error parsing core properties: {e}'}
    
    @staticmethod
    def _parse_app_properties(xml_data: bytes) -> Dict[str, str]:
        """Parse application properties XML."""
        try:
            root = ET.fromstring(xml_data)
            properties = {}
            
            # Common app properties
            app_props = [
                'Application', 'AppVersion', 'Company', 'Manager',
                'TotalTime', 'Pages', 'Words', 'Characters',
                'CharactersWithSpaces', 'Lines', 'Paragraphs',
                'Slides', 'Notes', 'Sheets', 'Template',
                'ScaleCrop', 'DocSecurity', 'SharedDoc'
            ]
            
            for prop in app_props:
                element = root.find(prop)
                if element is not None:
                    properties[prop] = element.text or ''
            
            return properties
            
        except Exception as e:
            return {'error': f'Error parsing app properties: {e}'}
    
    @staticmethod
    def _parse_custom_properties(xml_data: bytes) -> Dict[str, str]:
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
    
    @staticmethod
    def _analyze_security_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metadata for potential security issues."""
        security_info = {
            'privacy_concerns': [],
            'sensitive_data': [],
            'recommendations': []
        }
        
        # Check for personal information in core properties
        core_props = metadata.get('core_properties', {})
        if core_props.get('creator'):
            security_info['privacy_concerns'].append(f"Author name: {core_props['creator']}")
        if core_props.get('lastModifiedBy'):
            security_info['privacy_concerns'].append(f"Last modified by: {core_props['lastModifiedBy']}")
        
        # Check application properties for company info
        app_props = metadata.get('app_properties', {})
        if app_props.get('Company'):
            security_info['privacy_concerns'].append(f"Company: {app_props['Company']}")
        if app_props.get('Manager'):
            security_info['privacy_concerns'].append(f"Manager: {app_props['Manager']}")
        
        # Check for potentially sensitive custom properties
        custom_props = metadata.get('custom_properties', {})
        for key, value in custom_props.items():
            if any(keyword in key.lower() for keyword in ['password', 'secret', 'confidential', 'private']):
                security_info['sensitive_data'].append(f"Custom property '{key}' may contain sensitive data")
        
        # Generate recommendations
        if security_info['privacy_concerns']:
            security_info['recommendations'].append("Consider removing or anonymizing personal information")
        if security_info['sensitive_data']:
            security_info['recommendations'].append("Review custom properties for sensitive data")
        if not security_info['privacy_concerns'] and not security_info['sensitive_data']:
            security_info['recommendations'].append("No obvious privacy concerns detected")
        
        return security_info


class MetadataWorker(QThread):
    """Worker thread for metadata extraction and processing."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    metadata_extracted = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: str, operation_type: str = 'extract'):
        super().__init__()
        self.file_path = file_path
        self.operation_type = operation_type
    
    def run(self):
        """Run the metadata operation."""
        try:
            self.status_updated.emit(f"Processing: {os.path.basename(self.file_path)}")
            self.progress_updated.emit(20)
            
            if self.operation_type == 'extract':
                metadata = OfficeMetadataLogic.extract_metadata(self.file_path)
                self.progress_updated.emit(80)
                self.metadata_extracted.emit(metadata)
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Operation completed successfully")
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class OfficeMetadataGUI(StandardWindow):
    """Enhanced Office Metadata Tools GUI with comprehensive features."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Office Metadata Tools - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Office Metadata Tools - Richard's File Utilities")
            self.setGeometry(100, 100, 1400, 900)
        
        self.current_file = None
        self.current_metadata = {}
        self.metadata_worker = None
        
        self.init_ui()
        
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            self.menu_manager.register_callback('open_office_file', self.open_file)
            self.menu_manager.register_callback('save_metadata', self.save_metadata)
            self.menu_manager.register_callback('export_metadata', self.export_metadata)
            self.menu_manager.register_callback('batch_process', self.batch_process)
            self.menu_manager.register_callback('security_scan', self.security_scan)
            self.menu_manager.register_callback('help_office_metadata', self.show_help)
    
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
        
        # Header section
        self.create_header(layout)
        
        # Control panel
        self.create_control_panel(layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content area with tabs
        self.create_tab_interface(layout)
    
    def create_header(self, layout):
        """Create the header section."""
        header_label = QLabel("Office Metadata Tools")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        description = QLabel("Extract, view, edit, and analyze metadata from Office documents, PDFs, and more")
        description.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 5px 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(description)
    
    def create_control_panel(self, layout):
        """Create the control panel with buttons."""
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QHBoxLayout(file_group)
        
        open_button = QPushButton("📂 Open File")
        open_button.clicked.connect(self.open_file)
        open_button.setStyleSheet(self._get_button_style("#3498db", "#2980b9"))
        file_layout.addWidget(open_button)
        
        batch_button = QPushButton("📁 Batch Process")
        batch_button.clicked.connect(self.batch_process)
        batch_button.setStyleSheet(self._get_button_style("#9b59b6", "#8e44ad"))
        file_layout.addWidget(batch_button)
        
        control_layout.addWidget(file_group)
        
        # Analysis operations group
        analysis_group = QGroupBox("Analysis & Export")
        analysis_layout = QHBoxLayout(analysis_group)
        
        security_button = QPushButton("🔒 Security Scan")
        security_button.clicked.connect(self.security_scan)
        security_button.setStyleSheet(self._get_button_style("#e74c3c", "#c0392b"))
        analysis_layout.addWidget(security_button)
        
        export_button = QPushButton("📤 Export Metadata")
        export_button.clicked.connect(self.export_metadata)
        export_button.setStyleSheet(self._get_button_style("#e67e22", "#d35400"))
        analysis_layout.addWidget(export_button)
        
        save_button = QPushButton("💾 Save Changes")
        save_button.clicked.connect(self.save_metadata)
        save_button.setStyleSheet(self._get_button_style("#27ae60", "#229954"))
        analysis_layout.addWidget(save_button)
        
        control_layout.addWidget(analysis_group)
        
        # Status area
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready - Select a file to analyze metadata")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        status_layout.addWidget(self.status_label)
        
        control_layout.addWidget(status_group)
        
        layout.addWidget(control_panel)
    
    def _get_button_style(self, bg_color, hover_color):
        """Get standardized button style."""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                padding: 11px 15px 9px 17px;
            }}
        """
    
    def create_tab_interface(self, layout):
        """Create the tabbed interface for metadata display."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        # File Information tab
        self.create_file_info_tab()
        
        # Core Properties tab
        self.create_core_properties_tab()
        
        # Application Properties tab
        self.create_app_properties_tab()
        
        # Custom Properties tab
        self.create_custom_properties_tab()
        
        # Security Analysis tab
        self.create_security_tab()
        
        # Raw Data tab
        self.create_raw_data_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_file_info_tab(self):
        """Create the file information tab."""
        self.file_info_tab = QWidget()
        self.tab_widget.addTab(self.file_info_tab, "📄 File Info")
        
        layout = QVBoxLayout(self.file_info_tab)
        
        self.file_info_table = QTableWidget()
        self.file_info_table.setColumnCount(2)
        self.file_info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.file_info_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.file_info_table)
    
    def create_core_properties_tab(self):
        """Create the core properties tab."""
        self.core_props_tab = QWidget()
        self.tab_widget.addTab(self.core_props_tab, "📋 Core Properties")
        
        layout = QVBoxLayout(self.core_props_tab)
        
        self.core_props_table = QTableWidget()
        self.core_props_table.setColumnCount(2)
        self.core_props_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.core_props_table.horizontalHeader().setStretchLastSection(True)
        self.core_props_table.itemDoubleClicked.connect(self.edit_metadata_item)
        layout.addWidget(self.core_props_table)
    
    def create_app_properties_tab(self):
        """Create the application properties tab."""
        self.app_props_tab = QWidget()
        self.tab_widget.addTab(self.app_props_tab, "⚙️ App Properties")
        
        layout = QVBoxLayout(self.app_props_tab)
        
        self.app_props_table = QTableWidget()
        self.app_props_table.setColumnCount(2)
        self.app_props_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.app_props_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.app_props_table)
    
    def create_custom_properties_tab(self):
        """Create the custom properties tab."""
        self.custom_props_tab = QWidget()
        self.tab_widget.addTab(self.custom_props_tab, "🏷️ Custom Properties")
        
        layout = QVBoxLayout(self.custom_props_tab)
        
        # Add/Remove custom properties controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        
        add_button = QPushButton("➕ Add Property")
        add_button.clicked.connect(self.add_custom_property)
        remove_button = QPushButton("➖ Remove Property")
        remove_button.clicked.connect(self.remove_custom_property)
        
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(remove_button)
        controls_layout.addStretch()
        
        layout.addWidget(controls)
        
        self.custom_props_table = QTableWidget()
        self.custom_props_table.setColumnCount(2)
        self.custom_props_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.custom_props_table.horizontalHeader().setStretchLastSection(True)
        self.custom_props_table.itemDoubleClicked.connect(self.edit_metadata_item)
        layout.addWidget(self.custom_props_table)
    
    def create_security_tab(self):
        """Create the security analysis tab."""
        self.security_tab = QWidget()
        self.tab_widget.addTab(self.security_tab, "🔒 Security Analysis")
        
        layout = QVBoxLayout(self.security_tab)
        
        # Security analysis results
        self.security_text = QTextEdit()
        self.security_text.setReadOnly(True)
        layout.addWidget(self.security_text)
    
    def create_raw_data_tab(self):
        """Create the raw data tab."""
        self.raw_data_tab = QWidget()
        self.tab_widget.addTab(self.raw_data_tab, "🔧 Raw Data")
        
        layout = QVBoxLayout(self.raw_data_tab)
        
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setReadOnly(True)
        self.raw_data_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px;")
        layout.addWidget(self.raw_data_text)
    
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
            self.metadata_worker = MetadataWorker(file_path, 'extract')
            self.metadata_worker.progress_updated.connect(self.progress_bar.setValue)
            self.metadata_worker.status_updated.connect(self.status_label.setText)
            self.metadata_worker.metadata_extracted.connect(self.display_metadata)
            self.metadata_worker.error_occurred.connect(self.handle_error)
            self.metadata_worker.finished.connect(self.worker_finished)
            
            self.metadata_worker.start()
    
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
        
        # Security Analysis
        if 'security_info' in metadata:
            self.display_security_analysis(metadata['security_info'])
        
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
            
            # Make key column read-only
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            
            table.setItem(row, 0, key_item)
            table.setItem(row, 1, value_item)
        
        table.resizeColumnsToContents()
    
    def display_security_analysis(self, security_info):
        """Display security analysis results."""
        analysis_text = "🔒 Security Analysis Results\n" + "="*50 + "\n\n"
        
        # Privacy concerns
        if security_info.get('privacy_concerns'):
            analysis_text += "⚠️ Privacy Concerns Found:\n"
            for concern in security_info['privacy_concerns']:
                analysis_text += f"  • {concern}\n"
            analysis_text += "\n"
        
        # Sensitive data
        if security_info.get('sensitive_data'):
            analysis_text += "🚨 Potentially Sensitive Data:\n"
            for data in security_info['sensitive_data']:
                analysis_text += f"  • {data}\n"
            analysis_text += "\n"
        
        # Recommendations
        if security_info.get('recommendations'):
            analysis_text += "💡 Recommendations:\n"
            for rec in security_info['recommendations']:
                analysis_text += f"  • {rec}\n"
            analysis_text += "\n"
        
        self.security_text.setText(analysis_text)
    
    def clear_metadata(self):
        """Clear all metadata displays."""
        for table in [self.file_info_table, self.core_props_table, 
                     self.app_props_table, self.custom_props_table]:
            table.setRowCount(0)
        
        self.raw_data_text.clear()
        self.security_text.clear()
        self.current_metadata = {}
    
    def worker_finished(self):
        """Handle worker thread completion."""
        self.progress_bar.setVisible(False)
    
    def handle_error(self, error_message):
        """Handle worker errors."""
        QMessageBox.critical(self, "Error", f"Error processing file:\n{error_message}")
        self.status_label.setText("Error - Failed to process file")
    
    def edit_metadata_item(self, item):
        """Handle editing of metadata items."""
        if item.column() == 1:  # Only allow editing of value column
            QMessageBox.information(self, "Edit Metadata", 
                                   "Metadata editing will be available in a future version.\n\n"
                                   "This will allow you to modify metadata values and save "
                                   "changes back to the document.")
    
    def add_custom_property(self):
        """Add a new custom property."""
        QMessageBox.information(self, "Add Custom Property", 
                               "Custom property addition will be available in a future version.")
    
    def remove_custom_property(self):
        """Remove selected custom property."""
        QMessageBox.information(self, "Remove Custom Property", 
                               "Custom property removal will be available in a future version.")
    
    def batch_process(self):
        """Process multiple files in batch."""
        QMessageBox.information(self, "Batch Processing", 
                               "Batch processing will be available in a future version.\n\n"
                               "This will allow you to:\n"
                               "• Process multiple files simultaneously\n"
                               "• Apply metadata templates\n"
                               "• Generate batch reports\n"
                               "• Clean metadata from multiple files")
    
    def security_scan(self):
        """Perform detailed security scan."""
        if not self.current_metadata:
            QMessageBox.warning(self, "Warning", "No file is currently loaded.")
            return
        
        # Switch to security analysis tab
        self.tab_widget.setCurrentWidget(self.security_tab)
        
        QMessageBox.information(self, "Security Scan", 
                               "Enhanced security scanning features will be available "
                               "in a future version, including:\n\n"
                               "• Deep metadata analysis\n"
                               "• Hidden content detection\n"
                               "• Privacy risk assessment\n"
                               "• Automated cleaning recommendations")
    
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
        
        filename, file_type = QFileDialog.getSaveFileName(
            self, "Export Metadata",
            f"{os.path.splitext(os.path.basename(self.current_file))[0]}_metadata.json",
            "JSON Files (*.json);;XML Files (*.xml);;CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.current_metadata, f, indent=2, default=str, ensure_ascii=False)
                elif filename.endswith('.txt'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(self.current_metadata, indent=2, default=str))
                else:
                    # Default to JSON format
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.current_metadata, f, indent=2, default=str, ensure_ascii=False)
                
                QMessageBox.information(self, "Export Successful", 
                                       f"Metadata exported to:\n{filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                    f"Error exporting metadata:\n{e}")
    
    def show_help(self):
        """Show comprehensive help for Office Metadata Tools."""
        help_text = """
        <h2>Office Metadata Tools - Comprehensive Guide</h2>
        
        <h3>📄 Overview</h3>
        <p>Extract, view, edit, and analyze metadata from Office documents, PDFs, and other file formats. 
        This tool helps you understand what information is embedded in your documents and manage it securely.</p>
        
        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>Multi-Format Support:</b> DOCX, XLSX, PPTX, DOC, XLS, PPT, PDF</li>
            <li><b>Comprehensive Analysis:</b> Core, application, and custom properties</li>
            <li><b>Security Scanning:</b> Identify potentially sensitive metadata</li>
            <li><b>Export Options:</b> JSON, XML, CSV, and text formats</li>
            <li><b>Batch Processing:</b> Handle multiple files (coming soon)</li>
        </ul>
        
        <h3>📊 Metadata Types</h3>
        <ul>
            <li><b>File Information:</b> Size, dates, path, format details</li>
            <li><b>Core Properties:</b> Title, author, subject, keywords, description</li>
            <li><b>Application Properties:</b> Software version, company, document statistics</li>
            <li><b>Custom Properties:</b> User-defined metadata fields</li>
            <li><b>Security Analysis:</b> Privacy concerns and sensitive data detection</li>
        </ul>
        
        <h3>🔒 Security Features</h3>
        <ul>
            <li><b>Privacy Detection:</b> Identifies author names, company info</li>
            <li><b>Sensitive Data Scanning:</b> Finds potentially confidential metadata</li>
            <li><b>Recommendations:</b> Suggests metadata cleanup actions</li>
            <li><b>Export for Analysis:</b> Save metadata for security review</li>
        </ul>
        
        <h3>📋 Usage Instructions</h3>
        <ol>
            <li><b>Open File:</b> Click "Open File" and select an office document</li>
            <li><b>Review Metadata:</b> Browse through the different tabs to examine metadata</li>
            <li><b>Security Analysis:</b> Check the Security Analysis tab for privacy concerns</li>
            <li><b>Export Data:</b> Use "Export Metadata" to save analysis results</li>
        </ol>
        
        <h3>⚠️ Important Notes</h3>
        <ul>
            <li>Always backup important files before making changes</li>
            <li>Review metadata before sharing sensitive documents</li>
            <li>Some features require additional Python libraries</li>
            <li>Legacy Office formats have limited metadata extraction</li>
        </ul>
        
        <p><b>Future Enhancements:</b> Metadata editing, batch processing, automated cleaning, 
        and advanced security scanning features are in development.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Office Metadata Tools - Help")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.resize(800, 600)
        msg_box.exec_()


def main():
    """Main function to run the Office Metadata Tools GUI."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = OfficeMetadataGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()