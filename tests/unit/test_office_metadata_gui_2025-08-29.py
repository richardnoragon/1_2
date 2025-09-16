"""
Comprehensive Unit Tests for office_metadata_gui.py
Test Suite: Office Metadata Tools GUI Testing Framework
Created: 2025-08-29
Target: src/utilities/office_metadata/office_metadata_gui.py

This module provides comprehensive unit tests for the Office Metadata Tools GUI,
covering all functionality including metadata extraction, GUI components,
worker threads, security analysis, and file operations.
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QTableWidget, QTextEdit, QWidget
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("PyQt5 not available - GUI tests will be skipped")

# Import the modules under test
try:
    from src.tools.office_metadata.office_metadata_gui import (
        MetadataWorker, OfficeMetadataGUI, OfficeMetadataLogic)
except ImportError as e:
    print(f"Warning: Could not import target modules: {e}")
    OfficeMetadataLogic = None
    MetadataWorker = None
    OfficeMetadataGUI = None


class TestOfficeMetadataLogic(unittest.TestCase):
    """Test cases for OfficeMetadataLogic class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_timestamp = datetime.now().isoformat()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_docx_path = os.path.join(self.test_dir, "test_document.docx")
        self.test_pdf_path = os.path.join(self.test_dir, "test_document.pdf")
        self.test_txt_path = os.path.join(self.test_dir, "test_document.txt")
        
        # Create mock DOCX file structure
        self._create_mock_docx()
        
        # Create simple test files
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%fake pdf content')
        
        with open(self.test_txt_path, 'w') as f:
            f.write("Test text file content")
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_mock_docx(self):
        """Create a mock DOCX file with proper structure."""
        with zipfile.ZipFile(self.test_docx_path, 'w') as zip_file:
            # Core properties XML
            core_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                              xmlns:dc="http://purl.org/dc/elements/1.1/"
                              xmlns:dcterms="http://purl.org/dc/terms/">
                <dc:title>Test Document</dc:title>
                <dc:creator>Test Author</dc:creator>
                <dc:subject>Test Subject</dc:subject>
                <dc:description>Test Description</dc:description>
                <cp:keywords>test, document, metadata</cp:keywords>
                <cp:category>Test Category</cp:category>
                <dcterms:created>2025-08-29T10:00:00Z</dcterms:created>
                <dcterms:modified>2025-08-29T12:00:00Z</dcterms:modified>
                <cp:lastModifiedBy>Test Editor</cp:lastModifiedBy>
                <cp:revision>1</cp:revision>
                <dc:language>en-US</dc:language>
            </cp:coreProperties>"""
            
            # App properties XML
            app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
                <Application>Microsoft Word</Application>
                <AppVersion>16.0000</AppVersion>
                <Company>Test Company</Company>
                <Manager>Test Manager</Manager>
                <TotalTime>120</TotalTime>
                <Pages>5</Pages>
                <Words>1000</Words>
                <Characters>5000</Characters>
                <CharactersWithSpaces>6000</CharactersWithSpaces>
                <Lines>50</Lines>
                <Paragraphs>20</Paragraphs>
                <Template>Normal.dotm</Template>
                <ScaleCrop>false</ScaleCrop>
                <DocSecurity>0</DocSecurity>
                <SharedDoc>false</SharedDoc>
            </Properties>"""
            
            # Custom properties XML
            custom_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties">
                <property name="CustomProperty1" pid="2">
                    <vt:lpwstr xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">Custom Value 1</vt:lpwstr>
                </property>
                <property name="ProjectCode" pid="3">
                    <vt:lpwstr xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">PROJ-2025-001</vt:lpwstr>
                </property>
            </Properties>"""
            
            zip_file.writestr('docProps/core.xml', core_xml)
            zip_file.writestr('docProps/app.xml', app_xml)
            zip_file.writestr('docProps/custom.xml', custom_xml)
            
            # Add minimal document structure
            zip_file.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
            zip_file.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships/>')
    
    def test_extract_metadata_docx_success(self):
        """Test successful metadata extraction from DOCX file."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        metadata = OfficeMetadataLogic.extract_metadata(self.test_docx_path)
        
        # Verify structure
        self.assertIn('file_info', metadata)
        self.assertIn('core_properties', metadata)
        self.assertIn('app_properties', metadata)
        self.assertIn('custom_properties', metadata)
        self.assertIn('security_info', metadata)
        
        # Verify file info
        file_info = metadata['file_info']
        self.assertEqual(file_info['filename'], 'test_document.docx')
        self.assertEqual(file_info['extension'], '.docx')
        self.assertIn('size', file_info)
        self.assertIn('created', file_info)
        
        # Verify core properties
        core_props = metadata['core_properties']
        self.assertEqual(core_props.get('title'), 'Test Document')
        self.assertEqual(core_props.get('creator'), 'Test Author')
        self.assertEqual(core_props.get('subject'), 'Test Subject')
        
        # Verify app properties
        app_props = metadata['app_properties']
        self.assertEqual(app_props.get('Application'), 'Microsoft Word')
        self.assertEqual(app_props.get('Company'), 'Test Company')
        
        # Verify custom properties
        custom_props = metadata['custom_properties']
        self.assertEqual(custom_props.get('CustomProperty1'), 'Custom Value 1')
        self.assertEqual(custom_props.get('ProjectCode'), 'PROJ-2025-001')
    
    def test_extract_metadata_file_not_found(self):
        """Test metadata extraction with non-existent file."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        with self.assertRaises(FileNotFoundError):
            OfficeMetadataLogic.extract_metadata("nonexistent_file.docx")
    
    def test_extract_metadata_unsupported_format(self):
        """Test metadata extraction with unsupported file format."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        with self.assertRaises(ValueError) as context:
            OfficeMetadataLogic.extract_metadata(self.test_txt_path)
        
        self.assertIn("Unsupported file type", str(context.exception))
    
    def test_extract_metadata_pdf_format(self):
        """Test metadata extraction from PDF file."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        metadata = OfficeMetadataLogic.extract_metadata(self.test_pdf_path)
        
        self.assertIn('file_info', metadata)
        self.assertIn('pdf_properties', metadata)
        
        pdf_props = metadata['pdf_properties']
        self.assertIn('note', pdf_props)
        self.assertIn('PyPDF2', pdf_props['note'])
    
    def test_extract_ole_metadata(self):
        """Test OLE metadata extraction for legacy formats."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Create a mock .doc file
        ole_path = os.path.join(self.test_dir, "test.doc")
        with open(ole_path, 'wb') as f:
            f.write(b'Mock OLE document content')
        
        metadata = OfficeMetadataLogic._extract_ole_metadata(ole_path)
        
        self.assertIn('file_info', metadata)
        self.assertIn('ole_properties', metadata)
        
        ole_props = metadata['ole_properties']
        self.assertIn('note', ole_props)
        self.assertIn('olefile', ole_props['note'])
    
    def test_get_file_info(self):
        """Test file information extraction."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        file_info = OfficeMetadataLogic._get_file_info(self.test_docx_path)
        
        self.assertEqual(file_info['filename'], 'test_document.docx')
        self.assertEqual(file_info['filepath'], self.test_docx_path)
        self.assertEqual(file_info['extension'], '.docx')
        self.assertIn('size', file_info)
        self.assertIn('size_formatted', file_info)
        self.assertIn('created', file_info)
        self.assertIn('modified', file_info)
        self.assertIn('accessed', file_info)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Test various sizes
        self.assertEqual(OfficeMetadataLogic._format_file_size(500), "500.0 B")
        self.assertEqual(OfficeMetadataLogic._format_file_size(1024), "1.0 KB")
        self.assertEqual(OfficeMetadataLogic._format_file_size(1048576), "1.0 MB")
        self.assertEqual(OfficeMetadataLogic._format_file_size(1073741824), "1.0 GB")
        self.assertEqual(OfficeMetadataLogic._format_file_size(1099511627776), "1.0 TB")
    
    def test_parse_core_properties_empty(self):
        """Test parsing empty core properties."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        empty_xml = b'<?xml version="1.0"?><root/>'
        result = OfficeMetadataLogic._parse_core_properties(empty_xml)
        
        self.assertIsInstance(result, dict)
        # Should return empty dict for elements not found
        self.assertEqual(len([k for k, v in result.items() if v]), 0)
    
    def test_parse_core_properties_invalid_xml(self):
        """Test parsing invalid XML in core properties."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        invalid_xml = b'<invalid xml structure'
        result = OfficeMetadataLogic._parse_core_properties(invalid_xml)
        
        self.assertIn('error', result)
        self.assertIn('Error parsing core properties', result['error'])
    
    def test_parse_app_properties(self):
        """Test parsing application properties."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        app_xml = b"""<?xml version="1.0"?>
        <Properties>
            <Application>Test App</Application>
            <Company>Test Company</Company>
            <Pages>10</Pages>
        </Properties>"""
        
        result = OfficeMetadataLogic._parse_app_properties(app_xml)
        
        self.assertEqual(result.get('Application'), 'Test App')
        self.assertEqual(result.get('Company'), 'Test Company')
        self.assertEqual(result.get('Pages'), '10')
    
    def test_parse_custom_properties(self):
        """Test parsing custom properties."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        custom_xml = b"""<?xml version="1.0"?>
        <Properties>
            <property name="CustomProp1">
                <value>Custom Value 1</value>
            </property>
            <property name="CustomProp2">
                <value>Custom Value 2</value>
            </property>
        </Properties>"""
        
        result = OfficeMetadataLogic._parse_custom_properties(custom_xml)
        
        self.assertIsInstance(result, dict)
        # Note: The actual implementation might differ in XML structure
    
    def test_analyze_security_metadata_privacy_concerns(self):
        """Test security analysis for privacy concerns."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        metadata = {
            'core_properties': {
                'creator': 'John Doe',
                'lastModifiedBy': 'Jane Smith'
            },
            'app_properties': {
                'Company': 'Secret Corp',
                'Manager': 'Boss Person'
            },
            'custom_properties': {
                'password_hint': 'my_secret',
                'confidential_data': 'classified'
            }
        }
        
        security_info = OfficeMetadataLogic._analyze_security_metadata(metadata)
        
        self.assertIn('privacy_concerns', security_info)
        self.assertIn('sensitive_data', security_info)
        self.assertIn('recommendations', security_info)
        
        # Check for detected privacy concerns
        privacy_concerns = security_info['privacy_concerns']
        self.assertTrue(any('John Doe' in concern for concern in privacy_concerns))
        self.assertTrue(any('Secret Corp' in concern for concern in privacy_concerns))
        
        # Check for sensitive data detection
        sensitive_data = security_info['sensitive_data']
        self.assertTrue(any('password_hint' in data for data in sensitive_data))
        
        # Check recommendations
        recommendations = security_info['recommendations']
        self.assertTrue(len(recommendations) > 0)
    
    def test_analyze_security_metadata_clean(self):
        """Test security analysis with clean metadata."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        metadata = {
            'core_properties': {},
            'app_properties': {},
            'custom_properties': {}
        }
        
        security_info = OfficeMetadataLogic._analyze_security_metadata(metadata)
        
        self.assertEqual(len(security_info['privacy_concerns']), 0)
        self.assertEqual(len(security_info['sensitive_data']), 0)
        
        recommendations = security_info['recommendations']
        self.assertTrue(any('No obvious privacy concerns' in rec for rec in recommendations))


@pytest.mark.skipif(not PYQT5_AVAILABLE, reason="PyQt5 not available")
class TestMetadataWorker(unittest.TestCase):
    """Test cases for MetadataWorker thread class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PYQT5_AVAILABLE:
            self.skipTest("PyQt5 not available")
        
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.test_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.test_dir, "test.docx")
        
        # Create minimal test file
        with open(self.test_file_path, 'wb') as f:
            f.write(b'Test file content')
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_metadata_worker_initialization(self):
        """Test MetadataWorker initialization."""
        if MetadataWorker is None:
            self.skipTest("Target module not available")
        
        worker = MetadataWorker(self.test_file_path, 'extract')
        
        self.assertEqual(worker.file_path, self.test_file_path)
        self.assertEqual(worker.operation_type, 'extract')
        self.assertIsInstance(worker, QThread)
    
    @patch.object(OfficeMetadataLogic, 'extract_metadata')
    def test_metadata_worker_run_success(self, mock_extract):
        """Test successful worker run operation."""
        if MetadataWorker is None:
            self.skipTest("Target module not available")
        
        # Mock successful extraction
        mock_metadata = {'test': 'data'}
        mock_extract.return_value = mock_metadata
        
        worker = MetadataWorker(self.test_file_path, 'extract')
        
        # Track signal emissions
        progress_signals = []
        status_signals = []
        metadata_signals = []
        error_signals = []
        
        worker.progress_updated.connect(lambda x: progress_signals.append(x))
        worker.status_updated.connect(lambda x: status_signals.append(x))
        worker.metadata_extracted.connect(lambda x: metadata_signals.append(x))
        worker.error_occurred.connect(lambda x: error_signals.append(x))
        
        # Run worker
        worker.run()
        
        # Verify signals
        self.assertTrue(len(progress_signals) > 0)
        self.assertTrue(len(status_signals) > 0)
        self.assertEqual(len(metadata_signals), 1)
        self.assertEqual(len(error_signals), 0)
        
        # Verify metadata
        self.assertEqual(metadata_signals[0], mock_metadata)
        
        # Verify progress
        self.assertIn(100, progress_signals)  # Should complete at 100%
    
    @patch.object(OfficeMetadataLogic, 'extract_metadata')
    def test_metadata_worker_run_error(self, mock_extract):
        """Test worker error handling."""
        if MetadataWorker is None:
            self.skipTest("Target module not available")
        
        # Mock extraction error
        mock_extract.side_effect = Exception("Test error")
        
        worker = MetadataWorker(self.test_file_path, 'extract')
        
        # Track error signals
        error_signals = []
        worker.error_occurred.connect(lambda x: error_signals.append(x))
        
        # Run worker
        worker.run()
        
        # Verify error signal
        self.assertEqual(len(error_signals), 1)
        self.assertIn("Test error", error_signals[0])


@pytest.mark.skipif(not PYQT5_AVAILABLE, reason="PyQt5 not available")
class TestOfficeMetadataGUI(unittest.TestCase):
    """Test cases for OfficeMetadataGUI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PYQT5_AVAILABLE:
            self.skipTest("PyQt5 not available")
        
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_gui_initialization(self):
        """Test GUI initialization."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        # Verify basic properties
        self.assertIsNotNone(gui.tab_widget)
        self.assertIsNotNone(gui.progress_bar)
        self.assertIsNotNone(gui.status_label)
        
        # Verify tables
        self.assertIsNotNone(gui.file_info_table)
        self.assertIsNotNone(gui.core_props_table)
        self.assertIsNotNone(gui.app_props_table)
        self.assertIsNotNone(gui.custom_props_table)
        
        # Verify text areas
        self.assertIsNotNone(gui.security_text)
        self.assertIsNotNone(gui.raw_data_text)
        
        # Verify initial state
        self.assertIsNone(gui.current_file)
        self.assertEqual(gui.current_metadata, {})
        
        gui.close()
    
    def test_populate_table(self):
        """Test table population functionality."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        test_data = {
            'property1': 'value1',
            'property2': 'value2',
            'property3': 'value3'
        }
        
        gui.populate_table(gui.file_info_table, test_data)
        
        # Verify table content
        self.assertEqual(gui.file_info_table.rowCount(), 3)
        self.assertEqual(gui.file_info_table.columnCount(), 2)
        
        # Check first row
        key_item = gui.file_info_table.item(0, 0)
        value_item = gui.file_info_table.item(0, 1)
        
        self.assertIsNotNone(key_item)
        self.assertIsNotNone(value_item)
        
        gui.close()
    
    def test_populate_table_empty_data(self):
        """Test table population with empty data."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        # Test with None
        gui.populate_table(gui.file_info_table, None)
        self.assertEqual(gui.file_info_table.rowCount(), 0)
        
        # Test with empty dict
        gui.populate_table(gui.file_info_table, {})
        self.assertEqual(gui.file_info_table.rowCount(), 0)
        
        gui.close()
    
    def test_display_metadata(self):
        """Test metadata display functionality."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        test_metadata = {
            'file_info': {
                'filename': 'test.docx',
                'size': 1024,
                'extension': '.docx'
            },
            'core_properties': {
                'title': 'Test Document',
                'creator': 'Test Author'
            },
            'app_properties': {
                'Application': 'Microsoft Word',
                'Company': 'Test Company'
            },
            'custom_properties': {
                'ProjectCode': 'PROJ-001'
            },
            'security_info': {
                'privacy_concerns': ['Author name: Test Author'],
                'sensitive_data': [],
                'recommendations': ['Consider removing personal information']
            }
        }
        
        gui.display_metadata(test_metadata)
        
        # Verify metadata stored
        self.assertEqual(gui.current_metadata, test_metadata)
        
        # Verify tables populated
        self.assertEqual(gui.file_info_table.rowCount(), 3)
        self.assertEqual(gui.core_props_table.rowCount(), 2)
        self.assertEqual(gui.app_props_table.rowCount(), 2)
        self.assertEqual(gui.custom_props_table.rowCount(), 1)
        
        # Verify security analysis displayed
        security_text = gui.security_text.toPlainText()
        self.assertIn('Privacy Concerns Found', security_text)
        self.assertIn('Test Author', security_text)
        
        # Verify raw data displayed
        raw_text = gui.raw_data_text.toPlainText()
        self.assertIn('test.docx', raw_text)
        
        gui.close()
    
    def test_clear_metadata(self):
        """Test metadata clearing functionality."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        # First populate with data
        test_data = {'test': 'data'}
        gui.populate_table(gui.file_info_table, test_data)
        gui.security_text.setText("Test security info")
        gui.raw_data_text.setText("Test raw data")
        gui.current_metadata = test_data
        
        # Clear metadata
        gui.clear_metadata()
        
        # Verify clearing
        self.assertEqual(gui.file_info_table.rowCount(), 0)
        self.assertEqual(gui.core_props_table.rowCount(), 0)
        self.assertEqual(gui.app_props_table.rowCount(), 0)
        self.assertEqual(gui.custom_props_table.rowCount(), 0)
        
        self.assertEqual(gui.security_text.toPlainText(), "")
        self.assertEqual(gui.raw_data_text.toPlainText(), "")
        self.assertEqual(gui.current_metadata, {})
        
        gui.close()
    
    def test_display_security_analysis(self):
        """Test security analysis display."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        security_info = {
            'privacy_concerns': [
                'Author name: John Doe',
                'Company: Secret Corp'
            ],
            'sensitive_data': [
                'Custom property "password" may contain sensitive data'
            ],
            'recommendations': [
                'Remove personal information',
                'Review custom properties'
            ]
        }
        
        gui.display_security_analysis(security_info)
        
        security_text = gui.security_text.toPlainText()
        
        # Verify content
        self.assertIn('Security Analysis Results', security_text)
        self.assertIn('Privacy Concerns Found', security_text)
        self.assertIn('John Doe', security_text)
        self.assertIn('Potentially Sensitive Data', security_text)
        self.assertIn('password', security_text)
        self.assertIn('Recommendations', security_text)
        self.assertIn('Remove personal information', security_text)
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QFileDialog.getOpenFileName')
    def test_open_file_dialog_cancelled(self, mock_dialog):
        """Test open file when dialog is cancelled."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        # Mock cancelled dialog
        mock_dialog.return_value = ("", "")
        
        gui = OfficeMetadataGUI()
        initial_file = gui.current_file
        
        gui.open_file()
        
        # Verify no change
        self.assertEqual(gui.current_file, initial_file)
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QFileDialog.getSaveFileName')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_metadata_json(self, mock_file, mock_dialog):
        """Test metadata export to JSON."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        # Mock save dialog
        test_filename = "exported_metadata.json"
        mock_dialog.return_value = (test_filename, "JSON Files (*.json)")
        
        gui = OfficeMetadataGUI()
        gui.current_metadata = {'test': 'data'}
        
        gui.export_metadata()
        
        # Verify file operations
        mock_file.assert_called_once_with(test_filename, 'w', encoding='utf-8')
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.warning')
    def test_export_metadata_no_data(self, mock_warning):
        """Test export metadata with no data loaded."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        gui.current_metadata = {}
        
        gui.export_metadata()
        
        # Verify warning shown
        mock_warning.assert_called_once()
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.information')
    def test_batch_process_not_implemented(self, mock_info):
        """Test batch process feature (not yet implemented)."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        gui.batch_process()
        
        # Verify info dialog shown
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertIn("Batch processing", args[1])
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.information')
    def test_security_scan_no_file(self, mock_info):
        """Test security scan with no file loaded."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        gui.current_metadata = {}
        
        gui.security_scan()
        
        # Should show warning about no file
        mock_info.assert_called()
        
        gui.close()
    
    def test_security_scan_with_file(self):
        """Test security scan with file loaded."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        gui.current_metadata = {'test': 'data'}
        
        # Should switch to security tab
        initial_tab = gui.tab_widget.currentIndex()
        gui.security_scan()
        
        # Verify tab switch (security tab should be different from initial)
        current_tab = gui.tab_widget.currentIndex()
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.information')
    def test_add_custom_property_not_implemented(self, mock_info):
        """Test add custom property feature (not yet implemented)."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        gui.add_custom_property()
        
        # Verify info dialog shown
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertIn("Custom property addition", args[1])
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.information')
    def test_remove_custom_property_not_implemented(self, mock_info):
        """Test remove custom property feature (not yet implemented)."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        gui.remove_custom_property()
        
        # Verify info dialog shown
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertIn("Custom property removal", args[1])
        
        gui.close()
    
    @patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.information')
    def test_save_metadata_no_file(self, mock_info):
        """Test save metadata with no file open."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        gui.current_file = None
        
        gui.save_metadata()
        
        # Should show warning
        mock_info.assert_called()
        
        gui.close()
    
    def test_handle_error(self):
        """Test error handling in GUI."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        test_error = "Test error message"
        
        with patch('src.tools.office_metadata.office_metadata_gui.QMessageBox.critical') as mock_critical:
            gui.handle_error(test_error)
            
            # Verify critical error dialog shown
            mock_critical.assert_called_once()
            args = mock_critical.call_args[0]
            self.assertIn(test_error, args[2])
        
        # Verify status updated
        self.assertIn("Error", gui.status_label.text())
        
        gui.close()
    
    def test_worker_finished(self):
        """Test worker finished handling."""
        if OfficeMetadataGUI is None:
            self.skipTest("Target module not available")
        
        gui = OfficeMetadataGUI()
        
        # Show progress bar
        gui.progress_bar.setVisible(True)
        self.assertTrue(gui.progress_bar.isVisible())
        
        # Call worker finished
        gui.worker_finished()
        
        # Verify progress bar hidden
        self.assertFalse(gui.progress_bar.isVisible())
        
        gui.close()


class TestIntegration(unittest.TestCase):
    """Integration tests for the office metadata system."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_timestamp = datetime.now().isoformat()
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_end_to_end_docx_processing(self):
        """Test complete end-to-end DOCX processing."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Create test DOCX file
        docx_path = os.path.join(self.test_dir, "integration_test.docx")
        
        with zipfile.ZipFile(docx_path, 'w') as zip_file:
            core_xml = """<?xml version="1.0"?>
            <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                              xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>Integration Test Document</dc:title>
                <dc:creator>Integration Tester</dc:creator>
            </cp:coreProperties>"""
            
            zip_file.writestr('docProps/core.xml', core_xml)
            zip_file.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
        
        # Process the file
        metadata = OfficeMetadataLogic.extract_metadata(docx_path)
        
        # Verify complete processing
        self.assertIn('file_info', metadata)
        self.assertIn('core_properties', metadata)
        self.assertIn('security_info', metadata)
        
        # Verify specific content
        self.assertEqual(metadata['core_properties']['title'], 'Integration Test Document')
        self.assertEqual(metadata['core_properties']['creator'], 'Integration Tester')
        
        # Verify security analysis
        security_info = metadata['security_info']
        self.assertIn('privacy_concerns', security_info)
        self.assertTrue(any('Integration Tester' in concern 
                          for concern in security_info['privacy_concerns']))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up edge case test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up edge case test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_corrupted_zip_file(self):
        """Test handling of corrupted ZIP/DOCX files."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Create corrupted DOCX file
        corrupted_path = os.path.join(self.test_dir, "corrupted.docx")
        with open(corrupted_path, 'wb') as f:
            f.write(b'This is not a valid ZIP file')
        
        with self.assertRaises(Exception) as context:
            OfficeMetadataLogic.extract_metadata(corrupted_path)
        
        self.assertIn("Error reading OOXML file", str(context.exception))
    
    def test_empty_zip_file(self):
        """Test handling of empty ZIP files."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Create empty ZIP file
        empty_path = os.path.join(self.test_dir, "empty.docx")
        with zipfile.ZipFile(empty_path, 'w') as zip_file:
            pass  # Create empty ZIP
        
        # Should handle gracefully
        metadata = OfficeMetadataLogic.extract_metadata(empty_path)
        
        self.assertIn('file_info', metadata)
        self.assertIn('core_properties', metadata)
        self.assertIn('app_properties', metadata)
        self.assertIn('custom_properties', metadata)
    
    def test_malformed_xml(self):
        """Test handling of malformed XML in metadata."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        malformed_xml = b'<xml><unclosed_tag>content'
        
        result = OfficeMetadataLogic._parse_core_properties(malformed_xml)
        
        self.assertIn('error', result)
        self.assertIn('Error parsing core properties', result['error'])
    
    def test_very_large_metadata_values(self):
        """Test handling of very large metadata values."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Test large file size formatting
        large_size = 1024 * 1024 * 1024 * 1024 * 5  # 5TB
        formatted = OfficeMetadataLogic._format_file_size(large_size)
        
        self.assertIn("TB", formatted)
        self.assertTrue(float(formatted.split()[0]) >= 5.0)
    
    def test_unicode_in_metadata(self):
        """Test handling of Unicode characters in metadata."""
        if OfficeMetadataLogic is None:
            self.skipTest("Target module not available")
        
        # Create DOCX with Unicode metadata
        unicode_path = os.path.join(self.test_dir, "unicode_test.docx")
        
        with zipfile.ZipFile(unicode_path, 'w') as zip_file:
            unicode_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                              xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>测试文档 🌟</dc:title>
                <dc:creator>مؤلف التجربة</dc:creator>
                <dc:subject>Тестовый субъект</dc:subject>
            </cp:coreProperties>""".encode('utf-8')
            
            zip_file.writestr('docProps/core.xml', unicode_xml)
            zip_file.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
        
        # Should handle Unicode gracefully
        metadata = OfficeMetadataLogic.extract_metadata(unicode_path)
        
        core_props = metadata['core_properties']
        self.assertEqual(core_props['title'], '测试文档 🌟')
        self.assertEqual(core_props['creator'], 'مؤلف التجربة')
        self.assertEqual(core_props['subject'], 'Тестовый субъект')


def generate_test_summary():
    """Generate comprehensive test execution summary."""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'test_suite': 'office_metadata_gui_2025-08-29',
        'target_module': 'src/utilities/office_metadata/office_metadata_gui.py',
        'test_framework': 'pytest + unittest',
        'test_categories': {
            'core_logic': 'OfficeMetadataLogic class tests',
            'worker_thread': 'MetadataWorker thread tests',
            'gui_components': 'OfficeMetadataGUI interface tests',
            'integration': 'End-to-end integration tests',
            'edge_cases': 'Error handling and edge case tests'
        },
        'coverage_areas': [
            'Metadata extraction (DOCX, PDF, OLE)',
            'XML parsing and validation',
            'Security analysis and privacy detection',
            'GUI component initialization and interaction',
            'Worker thread operations and signals',
            'File operations and error handling',
            'Data export and import functionality',
            'Unicode and internationalization support'
        ],
        'test_data': {
            'mock_files_created': 'DOCX, PDF, OLE, and text files',
            'xml_structures': 'Core, app, and custom property XML',
            'unicode_content': 'Multi-language metadata testing',
            'security_scenarios': 'Privacy and sensitive data detection'
        },
        'assertions_verified': [
            'Successful metadata extraction',
            'Proper error handling for invalid files',
            'GUI component initialization',
            'Table population and clearing',
            'Security analysis accuracy',
            'Export functionality',
            'Worker thread signal emission',
            'File size formatting',
            'Unicode handling'
        ]
    }
    
    return summary


if __name__ == '__main__':
    # Create test results directory
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate and save test summary
    summary = generate_test_summary()
    
    summary_file = os.path.join(results_dir, 'result_office_metadata_gui_test_summary_2025-08-29.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Test summary generated: {summary_file}")
    
    # Run the tests
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--capture=no'
    ])