#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Office Metadata Editor
File: office_meta_data_editor.py
Test Framework: pytest
Created: 2025-08-24
Coverage Target: 95%+

This test suite provides comprehensive coverage for all functions and methods
in the office_meta_data_editor.py module, including:
- OfficeMetadataWorker class testing
- OfficeMetaDataEditorGUI class testing  
- Metadata extraction and processing
- File operations and error handling
- GUI interactions and callbacks
- Edge cases and error scenarios
"""

import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pytest

# PyQt5 testing framework
try:
    from PyQt5.QtCore import QThread
    from PyQt5.QtWidgets import QApplication
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# Add source path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import modules under test
if PYQT5_AVAILABLE:
    from src.utilities.metadata.office_meta_data_editor import (
        OfficeMetaDataEditorGUI, OfficeMetadataWorker, main)


class TestOfficeMetadataWorker:
    """Test suite for OfficeMetadataWorker class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not PYQT5_AVAILABLE:
            pytest.skip("PyQt5 not available")
        
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def sample_files(self):
        """Create sample office files for testing."""
        temp_dir = tempfile.mkdtemp()
        files = []
        
        # Create sample DOCX file (empty ZIP)
        docx_path = os.path.join(temp_dir, "test.docx")
        with zipfile.ZipFile(docx_path, 'w') as zf:
            # Create minimal DOCX structure
            core_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dcmitype="http://purl.org/dc/dcmitype/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>Test Document</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:subject>Test Subject</dc:subject>
    <dc:description>Test Description</dc:description>
    <cp:keywords>test, keywords</cp:keywords>
    <cp:category>Test Category</cp:category>
    <dcterms:created xsi:type="dcterms:W3CDTF">2025-08-24T10:00:00Z</dcterms:created>
    <dcterms:modified xsi:type="dcterms:W3CDTF">2025-08-24T11:00:00Z</dcterms:modified>
    <cp:lastModifiedBy>Test Modifier</cp:lastModifiedBy>
    <cp:revision>1</cp:revision>
</cp:coreProperties>'''
            zf.writestr("docProps/core.xml", core_xml)
            
            app_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
    <Application>Microsoft Office Word</Application>
    <AppVersion>16.0000</AppVersion>
    <Company>Test Company</Company>
    <Manager>Test Manager</Manager>
    <TotalTime>120</TotalTime>
    <Pages>5</Pages>
    <Words>1000</Words>
    <Characters>5000</Characters>
    <Lines>100</Lines>
    <Paragraphs>25</Paragraphs>
</Properties>'''
            zf.writestr("docProps/app.xml", app_xml)
            
            custom_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties">
    <property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="Custom1">
        <lpwstr>Custom Value 1</lpwstr>
    </property>
    <property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="3" name="Custom2">
        <lpwstr>Custom Value 2</lpwstr>
    </property>
</Properties>'''
            zf.writestr("docProps/custom.xml", custom_xml)
        
        files.append(docx_path)
        
        # Create sample PDF file
        pdf_path = os.path.join(temp_dir, "test.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%Test PDF content')
        files.append(pdf_path)
        
        # Create sample DOC file (will trigger OLE handling)
        doc_path = os.path.join(temp_dir, "test.doc")
        with open(doc_path, 'wb') as f:
            f.write(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')  # OLE signature
        files.append(doc_path)
        
        # Create unsupported file
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("Test text file")
        files.append(txt_path)
        
        yield files, temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_worker_initialization(self, app):
        """Test OfficeMetadataWorker initialization."""
        files = ["test1.docx", "test2.xlsx"]
        operation = "read"
        updates = {"title": "New Title"}
        
        worker = OfficeMetadataWorker(files, operation, updates)
        
        assert worker.files == files
        assert worker.operation == operation
        assert worker.metadata_updates == updates
        assert worker.is_cancelled == False
        assert isinstance(worker, QThread)
    
    def test_worker_initialization_without_updates(self, app):
        """Test worker initialization without metadata updates."""
        files = ["test.docx"]
        operation = "read"
        
        worker = OfficeMetadataWorker(files, operation)
        
        assert worker.metadata_updates == {}
    
    def test_worker_cancel(self, app):
        """Test worker cancellation."""
        worker = OfficeMetadataWorker(["test.docx"], "read")
        worker.cancel()
        
        assert worker.is_cancelled == True
    
    def test_read_metadata_file_info(self, app, sample_files):
        """Test reading basic file information."""
        files, temp_dir = sample_files
        docx_file = files[0]
        
        worker = OfficeMetadataWorker([docx_file], "read")
        metadata = worker.read_metadata(docx_file)
        
        assert "file_info" in metadata
        assert metadata["file_info"]["filename"] == "test.docx"
        assert metadata["file_info"]["filepath"] == docx_file
        assert metadata["file_info"]["extension"] == ".docx"
        assert "size" in metadata["file_info"]
        assert "modified" in metadata["file_info"]
        assert "created" in metadata["file_info"]
    
    def test_read_ooxml_metadata_docx(self, app, sample_files):
        """Test reading OOXML metadata from DOCX file."""
        files, temp_dir = sample_files
        docx_file = files[0]
        
        worker = OfficeMetadataWorker([docx_file], "read")
        metadata = worker.read_ooxml_metadata(docx_file)
        
        # Check built-in properties
        assert "built_in_properties" in metadata
        built_in = metadata["built_in_properties"]
        assert built_in.get("title") == "Test Document"
        assert built_in.get("creator") == "Test Author"
        assert built_in.get("subject") == "Test Subject"
        assert built_in.get("description") == "Test Description"
        assert built_in.get("keywords") == "test, keywords"
        assert built_in.get("category") == "Test Category"
        
        # Check document properties
        assert "document_properties" in metadata
        doc_props = metadata["document_properties"]
        assert doc_props.get("application") == "Microsoft Office Word"
        assert doc_props.get("company") == "Test Company"
        assert doc_props.get("pages") == "5"
        assert doc_props.get("words") == "1000"
        
        # Check custom properties
        assert "custom_properties" in metadata
        custom_props = metadata["custom_properties"]
        assert custom_props.get("Custom1") == "Custom Value 1"
        assert custom_props.get("Custom2") == "Custom Value 2"
    
    def test_read_ooxml_metadata_invalid_zip(self, app):
        """Test reading OOXML metadata from invalid ZIP file."""
        temp_dir = tempfile.mkdtemp()
        try:
            invalid_file = os.path.join(temp_dir, "invalid.docx")
            with open(invalid_file, 'w') as f:
                f.write("Not a valid ZIP file")
            
            worker = OfficeMetadataWorker([invalid_file], "read")
            metadata = worker.read_ooxml_metadata(invalid_file)
            
            assert "error" in metadata
            assert "OOXML parsing error" in metadata["error"]
        finally:
            shutil.rmtree(temp_dir)
    
    def test_read_ooxml_metadata_missing_props(self, app):
        """Test reading OOXML metadata from file without properties."""
        temp_dir = tempfile.mkdtemp()
        try:
            docx_path = os.path.join(temp_dir, "minimal.docx")
            with zipfile.ZipFile(docx_path, 'w') as zf:
                # Create minimal DOCX without properties
                zf.writestr("word/document.xml", "<?xml version='1.0'?><document/>")
            
            worker = OfficeMetadataWorker([docx_path], "read")
            metadata = worker.read_ooxml_metadata(docx_path)
            
            assert "built_in_properties" in metadata
            assert "document_properties" in metadata
            assert "custom_properties" in metadata
        finally:
            shutil.rmtree(temp_dir)
    
    def test_read_ole_metadata(self, app, sample_files):
        """Test reading OLE metadata."""
        files, temp_dir = sample_files
        doc_file = files[2]  # DOC file
        
        worker = OfficeMetadataWorker([doc_file], "read")
        metadata = worker.read_ole_metadata(doc_file)
        
        assert "document_properties" in metadata
        assert metadata["document_properties"]["note"] == "OLE format detected"
        assert "error" in metadata
        assert "OLE metadata extraction requires additional libraries" in metadata["error"]
    
    def test_read_pdf_metadata_valid(self, app, sample_files):
        """Test reading PDF metadata from valid file."""
        files, temp_dir = sample_files
        pdf_file = files[1]  # PDF file
        
        worker = OfficeMetadataWorker([pdf_file], "read")
        metadata = worker.read_pdf_metadata(pdf_file)
        
        assert "document_properties" in metadata
        assert metadata["document_properties"]["format"] == "PDF"
        assert "note" in metadata["document_properties"]
    
    def test_read_pdf_metadata_invalid(self, app):
        """Test reading PDF metadata from invalid file."""
        temp_dir = tempfile.mkdtemp()
        try:
            invalid_pdf = os.path.join(temp_dir, "invalid.pdf")
            with open(invalid_pdf, 'w') as f:
                f.write("Not a PDF file")
            
            worker = OfficeMetadataWorker([invalid_pdf], "read")
            metadata = worker.read_pdf_metadata(invalid_pdf)
            
            assert "error" in metadata
            assert "Not a valid PDF file" in metadata["error"]
        finally:
            shutil.rmtree(temp_dir)
    
    def test_read_metadata_unsupported_format(self, app, sample_files):
        """Test reading metadata from unsupported file format."""
        files, temp_dir = sample_files
        txt_file = files[3]  # TXT file
        
        worker = OfficeMetadataWorker([txt_file], "read")
        metadata = worker.read_metadata(txt_file)
        
        assert "error" in metadata
        assert "Unsupported file format: .txt" in metadata["error"]
    
    def test_read_metadata_file_access_error(self, app):
        """Test reading metadata with file access error."""
        nonexistent_file = "/nonexistent/path/file.docx"
        
        worker = OfficeMetadataWorker([nonexistent_file], "read")
        metadata = worker.read_metadata(nonexistent_file)
        
        assert "error" in metadata
        assert "File access error" in metadata["error"]
    
    @patch('docx.Document')
    def test_write_metadata_docx_success(self, mock_document, app):
        """Test writing metadata to DOCX file successfully."""
        mock_doc = Mock()
        mock_props = Mock()
        mock_doc.core_properties = mock_props
        mock_document.return_value = mock_doc
        
        updates = {
            'title': 'New Title',
            'author': 'New Author',
            'subject': 'New Subject',
            'comments': 'New Comments',
            'keywords': 'new, keywords',
            'category': 'New Category'
        }
        
        worker = OfficeMetadataWorker([], "write")
        result = worker.write_metadata("test.docx", updates)
        
        assert result == True
        assert mock_props.title == 'New Title'
        assert mock_props.author == 'New Author'
        assert mock_props.subject == 'New Subject'
        assert mock_props.comments == 'New Comments'
        assert mock_props.keywords == 'new, keywords'
        assert mock_props.category == 'New Category'
        mock_doc.save.assert_called_once_with("test.docx")
    
    @patch('openpyxl.load_workbook')
    def test_write_metadata_xlsx_success(self, mock_load_workbook, app):
        """Test writing metadata to XLSX file successfully."""
        mock_wb = Mock()
        mock_props = Mock()
        mock_wb.properties = mock_props
        mock_load_workbook.return_value = mock_wb
        
        updates = {
            'title': 'New Title',
            'creator': 'New Creator',
            'subject': 'New Subject',
            'description': 'New Description',
            'keywords': 'new, keywords',
            'category': 'New Category'
        }
        
        worker = OfficeMetadataWorker([], "write")
        result = worker.write_metadata("test.xlsx", updates)
        
        assert result == True
        assert mock_props.title == 'New Title'
        assert mock_props.creator == 'New Creator'
        assert mock_props.subject == 'New Subject'
        assert mock_props.description == 'New Description'
        assert mock_props.keywords == 'new, keywords'
        assert mock_props.category == 'New Category'
        mock_wb.save.assert_called_once_with("test.xlsx")
    
    def test_write_metadata_docx_import_error(self, app):
        """Test writing metadata to DOCX with import error."""
        with patch('docx.Document', side_effect=ImportError):
            worker = OfficeMetadataWorker([], "write")
            result = worker.write_metadata("test.docx", {'title': 'New Title'})
            
            assert result == False
    
    def test_write_metadata_xlsx_import_error(self, app):
        """Test writing metadata to XLSX with import error."""
        with patch('openpyxl.load_workbook', side_effect=ImportError):
            worker = OfficeMetadataWorker([], "write")
            result = worker.write_metadata("test.xlsx", {'title': 'New Title'})
            
            assert result == False
    
    def test_write_metadata_unsupported_format(self, app):
        """Test writing metadata to unsupported format."""
        worker = OfficeMetadataWorker([], "write")
        result = worker.write_metadata("test.pdf", {'title': 'New Title'})
        
        assert result == False
    
    def test_write_metadata_exception(self, app):
        """Test writing metadata with exception."""
        with patch('docx.Document', side_effect=Exception("Test error")):
            worker = OfficeMetadataWorker([], "write")
            result = worker.write_metadata("test.docx", {'title': 'New Title'})
            
            assert result == False
    
    def test_worker_run_read_operation(self, app, sample_files):
        """Test worker run method with read operation."""
        files, temp_dir = sample_files
        worker = OfficeMetadataWorker([files[0]], "read")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        worker.run()
        
        worker.progress_updated.emit.assert_called_with(100)
        worker.file_processed.emit.assert_called_once()
        worker.finished.emit.assert_called_once()
    
    def test_worker_run_write_operation(self, app, sample_files):
        """Test worker run method with write operation."""
        files, temp_dir = sample_files
        updates = {'title': 'New Title'}
        worker = OfficeMetadataWorker([files[0]], "write", updates)
        
        # Mock signals and methods
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        worker.write_metadata = Mock(return_value=True)
        
        worker.run()
        
        worker.progress_updated.emit.assert_called_with(100)
        worker.file_processed.emit.assert_called_once()
        worker.finished.emit.assert_called_once()
        worker.write_metadata.assert_called_once_with(files[0], updates)
    
    def test_worker_run_with_cancellation(self, app):
        """Test worker run method with cancellation."""
        worker = OfficeMetadataWorker(["test1.docx", "test2.docx"], "read")
        worker.cancel()
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        worker.run()
        
        worker.finished.emit.assert_called_once()
        worker.file_processed.emit.assert_not_called()
    
    def test_worker_run_with_file_error(self, app):
        """Test worker run method with file processing error."""
        worker = OfficeMetadataWorker(["/nonexistent/file.docx"], "read")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        worker.run()
        
        worker.error_occurred.emit.assert_called()
        worker.finished.emit.assert_called_once()
    
    def test_worker_run_with_general_error(self, app):
        """Test worker run method with general error."""
        worker = OfficeMetadataWorker(["test.docx"], "read")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        # Mock read_metadata to raise exception
        worker.read_metadata = Mock(side_effect=Exception("General error"))
        
        worker.run()
        
        worker.error_occurred.emit.assert_called_with("Worker error: General error")


class TestOfficeMetaDataEditorGUI:
    """Test suite for OfficeMetaDataEditorGUI class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not PYQT5_AVAILABLE:
            pytest.skip("PyQt5 not available")
        
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def window(self, app):
        """Create GUI window for testing."""
        with patch('src.utilities.metadata.office_meta_data_editor.StandardWindow'):
            window = OfficeMetaDataEditorGUI()
            return window
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files."""
        temp_dir = tempfile.mkdtemp()
        files = []
        
        for i, ext in enumerate(['.docx', '.xlsx', '.pdf']):
            file_path = os.path.join(temp_dir, f"test{i}{ext}")
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            files.append(file_path)
        
        yield files, temp_dir
        shutil.rmtree(temp_dir)
    
    def test_gui_initialization(self, window):
        """Test GUI initialization."""
        assert window is not None
        assert hasattr(window, 'worker')
        assert hasattr(window, 'selected_files')
        assert hasattr(window, 'current_metadata')
        assert window.selected_files == []
        assert window.current_metadata == {}
    
    def test_setup_menu_callbacks(self, window):
        """Test menu callback setup."""
        # Mock menu manager
        window.menu_manager = Mock()
        window._setup_menu_callbacks()
        
        # Verify callback registrations
        assert window.menu_manager.register_callback.call_count > 0
        
        # Check specific callbacks
        calls = [call[0][0] for call in window.menu_manager.register_callback.call_args_list]
        expected_callbacks = [
            'new_metadata_session', 'save_file', 'open_file', 'export_data',
            'import_data', 'print_document', 'cut', 'copy', 'paste',
            'select_all', 'find', 'zoom_in', 'zoom_out', 'zoom_reset',
            'show_options', 'batch_processing', 'document_analysis', 'help_metadata'
        ]
        
        for callback in expected_callbacks:
            assert callback in calls
    
    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames')
    def test_browse_files_success(self, mock_dialog, window):
        """Test successful file browsing."""
        mock_files = ['/path/to/test1.docx', '/path/to/test2.xlsx']
        mock_dialog.return_value = (mock_files, '')
        
        window.browse_files()
        
        assert window.selected_files == mock_files
        assert window.files_edit.text() == "2 document(s) selected"
        assert window.edit_button.isEnabled() == True
    
    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames')
    def test_browse_files_cancelled(self, mock_dialog, window):
        """Test cancelled file browsing."""
        mock_dialog.return_value = ([], '')
        
        original_files = window.selected_files[:]
        window.browse_files()
        
        assert window.selected_files == original_files
    
    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_browse_folder_non_recursive(self, mock_isfile, mock_listdir, mock_dialog, window):
        """Test folder browsing without recursion."""
        mock_dialog.return_value = '/test/folder'
        mock_listdir.return_value = ['file1.docx', 'file2.txt', 'file3.xlsx']
        mock_isfile.return_value = True
        
        window.recursive_check.setChecked(False)
        window.browse_folder()
        
        expected_files = [
            '/test/folder/file1.docx',
            '/test/folder/file3.xlsx'
        ]
        assert window.selected_files == expected_files
        assert "Folder: /test/folder (2 documents)" in window.files_edit.text()
    
    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    @patch('os.walk')
    def test_browse_folder_recursive(self, mock_walk, mock_dialog, window):
        """Test folder browsing with recursion."""
        mock_dialog.return_value = '/test/folder'
        mock_walk.return_value = [
            ('/test/folder', ['subfolder'], ['file1.docx', 'file2.txt']),
            ('/test/folder/subfolder', [], ['file3.xlsx', 'file4.pdf'])
        ]
        
        window.recursive_check.setChecked(True)
        window.browse_folder()
        
        expected_files = [
            '/test/folder/file1.docx',
            '/test/folder/subfolder/file3.xlsx',
            '/test/folder/subfolder/file4.pdf'
        ]
        assert window.selected_files == expected_files
    
    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_browse_folder_cancelled(self, mock_dialog, window):
        """Test cancelled folder browsing."""
        mock_dialog.return_value = ''
        
        original_files = window.selected_files[:]
        window.browse_folder()
        
        assert window.selected_files == original_files
    
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_read_metadata_no_files(self, mock_warning, window):
        """Test reading metadata with no files selected."""
        window.selected_files = []
        window.read_metadata()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "Please select office documents first" in args[1]
    
    def test_read_metadata_with_files(self, window):
        """Test reading metadata with files selected."""
        window.selected_files = ['test.docx']
        window.start_operation = Mock()
        
        window.read_metadata()
        
        window.start_operation.assert_called_once_with("read")
    
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_edit_metadata(self, mock_info, window):
        """Test edit metadata functionality."""
        window.edit_metadata()
        
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Edit Metadata" in args[1]
        assert "additional libraries" in args[2]
    
    def test_start_operation_read(self, window):
        """Test starting read operation."""
        window.selected_files = ['test.docx']
        window.clear_results = Mock()
        
        with patch.object(window, 'worker', None):
            with patch('src.utilities.metadata.office_meta_data_editor.OfficeMetadataWorker') as mock_worker_class:
                mock_worker = Mock()
                mock_worker_class.return_value = mock_worker
                
                window.start_operation("read")
                
                window.clear_results.assert_called_once()
                assert window.read_button.isEnabled() == False
                assert window.edit_button.isEnabled() == False
                assert window.progress_bar.isVisible() == True
                assert "Reading document metadata" in window.status_label.text()
                
                mock_worker.start.assert_called_once()
    
    def test_start_operation_write(self, window):
        """Test starting write operation."""
        window.selected_files = ['test.docx']
        window.clear_results = Mock()
        updates = {'title': 'New Title'}
        
        with patch.object(window, 'worker', None):
            with patch('src.utilities.metadata.office_meta_data_editor.OfficeMetadataWorker') as mock_worker_class:
                mock_worker = Mock()
                mock_worker_class.return_value = mock_worker
                
                window.start_operation("write", updates)
                
                assert "Updating document metadata" in window.status_label.text()
                mock_worker_class.assert_called_with(window.selected_files, "write", updates)
    
    def test_update_progress(self, window):
        """Test progress bar update."""
        window.update_progress(50)
        assert window.progress_bar.value() == 50
    
    def test_add_result_docx(self, window):
        """Test adding DOCX file result."""
        file_path = "/test/document.docx"
        metadata = {
            "file_info": {
                "size": 1024,
                "modified": "2025-08-24T10:00:00"
            }
        }
        
        window.add_result(file_path, metadata)
        
        # Check file tree
        assert window.file_tree.topLevelItemCount() == 1
        item = window.file_tree.topLevelItem(0)
        assert item.text(0) == "document.docx"
        assert item.text(1) == "Word Document"
        assert item.text(2) == "1.0 KB"
        
        # Check metadata storage
        assert file_path in window.current_metadata
        assert window.current_metadata[file_path] == metadata
    
    def test_add_result_pdf(self, window):
        """Test adding PDF file result."""
        file_path = "/test/document.pdf"
        metadata = {
            "file_info": {
                "size": 2048000,  # 2MB
                "modified": "2025-08-24T10:00:00"
            }
        }
        
        window.add_result(file_path, metadata)
        
        item = window.file_tree.topLevelItem(0)
        assert item.text(1) == "PDF Document"
        assert item.text(2) == "2.0 MB"
    
    def test_add_result_unknown_type(self, window):
        """Test adding unknown file type result."""
        file_path = "/test/document.unknown"
        metadata = {
            "file_info": {
                "size": 512,
                "modified": "invalid-date"
            }
        }
        
        window.add_result(file_path, metadata)
        
        item = window.file_tree.topLevelItem(0)
        assert item.text(1) == "Unknown"
        assert item.text(2) == "512 B"
        assert item.text(3) == "Unknown"
    
    def test_operation_finished(self, window):
        """Test operation completion."""
        # Add some items to file tree
        window.file_tree.addTopLevelItem(window.file_tree.createItem())
        window.file_tree.addTopLevelItem(window.file_tree.createItem())
        
        mock_worker = Mock()
        window.worker = mock_worker
        
        window.operation_finished()
        
        assert window.read_button.isEnabled() == True
        assert window.edit_button.isEnabled() == True
        assert window.progress_bar.isVisible() == False
        assert window.export_button.isEnabled() == True
        assert "Completed - 2 documents processed" in window.status_label.text()
        
        mock_worker.deleteLater.assert_called_once()
        assert window.worker is None
    
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_show_error(self, mock_warning, window):
        """Test error message display."""
        error_message = "Test error message"
        window.show_error(error_message)
        
        mock_warning.assert_called_once_with(window, "Error", error_message)
    
    def test_show_file_metadata(self, window):
        """Test showing detailed file metadata."""
        # Create mock item with metadata
        item = Mock()
        metadata = {
            "built_in_properties": {"title": "Test Title", "author": "Test Author"},
            "document_properties": {"pages": "5", "words": "1000"},
            "custom_properties": {"custom1": "value1", "custom2": "value2"}
        }
        item.data.return_value = {"metadata": metadata}
        
        window.show_file_metadata(item)
        
        # Verify tables are populated
        assert window.builtin_table.rowCount() == 2
        assert window.document_table.rowCount() == 2
        assert window.custom_table.rowCount() == 2
    
    def test_show_file_metadata_no_data(self, window):
        """Test showing file metadata with no data."""
        item = Mock()
        item.data.return_value = None
        
        window.show_file_metadata(item)
        
        # Tables should remain empty
        assert window.builtin_table.rowCount() == 0
    
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_metadata_json(self, mock_file, mock_dialog, window):
        """Test exporting metadata to JSON file."""
        mock_dialog.return_value = ('/test/export.json', '')
        window.current_metadata = {
            '/test/file1.docx': {'title': 'Test Document 1'},
            '/test/file2.xlsx': {'title': 'Test Document 2'}
        }
        
        with patch('json.dump') as mock_json_dump:
            with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
                window.export_metadata()
                
                mock_file.assert_called_once_with('/test/export.json', 'w')
                mock_json_dump.assert_called_once()
                mock_info.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_metadata_text(self, mock_file, mock_dialog, window):
        """Test exporting metadata to text file."""
        mock_dialog.return_value = ('/test/export.txt', '')
        window.current_metadata = {
            '/test/file1.docx': {'title': 'Test Document 1'}
        }
        
        with patch('json.dumps') as mock_json_dumps:
            with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
                mock_json_dumps.return_value = '{"title": "Test Document 1"}'
                
                window.export_metadata()
                
                mock_file.assert_called_once_with('/test/export.txt', 'w')
                mock_info.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_export_metadata_no_data(self, mock_warning, window):
        """Test exporting metadata with no data."""
        window.current_metadata = {}
        window.export_metadata()
        
        mock_warning.assert_called_once()
        assert "No metadata to export" in mock_warning.call_args[0][1]
    
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_export_metadata_cancelled(self, mock_dialog, window):
        """Test cancelled metadata export."""
        mock_dialog.return_value = ('', '')
        window.current_metadata = {'test': 'data'}
        
        window.export_metadata()
        
        # No file operations should occur
        mock_dialog.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_export_metadata_error(self, mock_warning, mock_file, mock_dialog, window):
        """Test export metadata with file error."""
        mock_dialog.return_value = ('/test/export.json', '')
        window.current_metadata = {'test': 'data'}
        
        window.export_metadata()
        
        mock_warning.assert_called_once()
        assert "Failed to export metadata" in mock_warning.call_args[0][1]
    
    def test_clear_results(self, window):
        """Test clearing all results."""
        # Add some test data
        window.current_metadata = {'test': 'data'}
        window.file_tree.addTopLevelItem(window.file_tree.createItem())
        window.builtin_table.insertRow(0)
        window.document_table.insertRow(0)
        window.custom_table.insertRow(0)
        window.export_button.setEnabled(True)
        
        window.clear_results()
        
        assert window.file_tree.topLevelItemCount() == 0
        assert window.builtin_table.rowCount() == 0
        assert window.document_table.rowCount() == 0
        assert window.custom_table.rowCount() == 0
        assert window.current_metadata == {}
        assert window.export_button.isEnabled() == False
        assert "Ready to process office documents" in window.status_label.text()
    
    def test_new_metadata_session(self, window):
        """Test starting new metadata session."""
        # Set up some existing data
        window.selected_files = ['test.docx']
        window.files_edit.setText("Test text")
        window.current_metadata = {'test': 'data'}
        window.clear_results = Mock()
        window.show_status_message = Mock()
        
        window.new_metadata_session()
        
        assert window.selected_files == []
        assert window.files_edit.text() == ""
        window.clear_results.assert_called_once()
        window.show_status_message.assert_called_once_with("New metadata session started")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_metadata_settings_success(self, mock_json_dump, mock_file, window):
        """Test saving metadata settings successfully."""
        window.selected_files = ['test1.docx', 'test2.xlsx']
        window.recursive_check.setChecked(True)
        window.get_save_file_path = Mock(return_value='/test/settings.json')
        window.show_info_dialog = Mock()
        
        window.save_metadata_settings()
        
        mock_file.assert_called_once_with('/test/settings.json', 'w')
        mock_json_dump.assert_called_once()
        
        # Check settings content
        settings = mock_json_dump.call_args[0][0]
        assert settings['selected_files'] == ['test1.docx', 'test2.xlsx']
        assert settings['recursive_search'] == True
        assert 'timestamp' in settings
        
        window.show_info_dialog.assert_called_once()
    
    def test_save_metadata_settings_cancelled(self, window):
        """Test cancelled metadata settings save."""
        window.get_save_file_path = Mock(return_value='')
        window.show_info_dialog = Mock()
        
        window.save_metadata_settings()
        
        window.show_info_dialog.assert_not_called()
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_metadata_settings_error(self, mock_file, window):
        """Test save metadata settings with error."""
        window.get_save_file_path = Mock(return_value='/test/settings.json')
        window.show_error_dialog = Mock()
        
        window.save_metadata_settings()
        
        window.show_error_dialog.assert_called_once()
        assert "Failed to save settings" in window.show_error_dialog.call_args[0][1]
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"selected_files": ["test.docx"], "recursive_search": true}')
    @patch('json.load')
    def test_load_metadata_settings_success(self, mock_json_load, mock_file, window):
        """Test loading metadata settings successfully."""
        settings = {
            'selected_files': ['test1.docx', 'test2.xlsx'],
            'recursive_search': True
        }
        mock_json_load.return_value = settings
        
        window.get_file_path = Mock(return_value='/test/settings.json')
        window.show_info_dialog = Mock()
        
        window.load_metadata_settings()
        
        mock_file.assert_called_once_with('/test/settings.json', 'r')
        assert window.selected_files == ['test1.docx', 'test2.xlsx']
        assert window.recursive_check.isChecked() == True
        assert window.files_edit.text() == "2 document(s) loaded"
        assert window.edit_button.isEnabled() == True
        
        window.show_info_dialog.assert_called_once()
    
    def test_load_metadata_settings_cancelled(self, window):
        """Test cancelled metadata settings load."""
        window.get_file_path = Mock(return_value='')
        window.show_info_dialog = Mock()
        
        window.load_metadata_settings()
        
        window.show_info_dialog.assert_not_called()
    
    @patch('builtins.open', side_effect=IOError("File not found"))
    def test_load_metadata_settings_error(self, mock_file, window):
        """Test load metadata settings with error."""
        window.get_file_path = Mock(return_value='/test/settings.json')
        window.show_error_dialog = Mock()
        
        window.load_metadata_settings()
        
        window.show_error_dialog.assert_called_once()
        assert "Failed to load settings" in window.show_error_dialog.call_args[0][1]
    
    def test_import_metadata_settings(self, window):
        """Test import metadata settings placeholder."""
        window.show_info_dialog = Mock()
        
        window.import_metadata_settings()
        
        window.show_info_dialog.assert_called_once()
        assert "Import Metadata" in window.show_info_dialog.call_args[0][0]
    
    def test_print_metadata_report(self, window):
        """Test print metadata report placeholder."""
        window.show_info_dialog = Mock()
        
        window.print_metadata_report()
        
        window.show_info_dialog.assert_called_once()
        assert "Print Report" in window.show_info_dialog.call_args[0][0]
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_cut_text(self, mock_focus_widget, window):
        """Test cut text functionality."""
        mock_widget = Mock()
        mock_focus_widget.return_value = mock_widget
        
        window.cut_text()
        
        mock_widget.cut.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_copy_text(self, mock_focus_widget, window):
        """Test copy text functionality."""
        mock_widget = Mock()
        mock_focus_widget.return_value = mock_widget
        
        window.copy_text()
        
        mock_widget.copy.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_paste_text(self, mock_focus_widget, window):
        """Test paste text functionality."""
        mock_widget = Mock()
        mock_focus_widget.return_value = mock_widget
        
        window.paste_text()
        
        mock_widget.paste.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_select_all_text(self, mock_focus_widget, window):
        """Test select all text functionality."""
        mock_widget = Mock()
        mock_focus_widget.return_value = mock_widget
        
        window.select_all_text()
        
        mock_widget.selectAll.assert_called_once()
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_text_operations_no_widget(self, mock_focus_widget, window):
        """Test text operations with no focused widget."""
        mock_focus_widget.return_value = None
        
        # These should not raise exceptions
        window.cut_text()
        window.copy_text()
        window.paste_text()
        window.select_all_text()
    
    @patch('PyQt5.QtWidgets.QApplication.focusWidget')
    def test_text_operations_no_method(self, mock_focus_widget, window):
        """Test text operations with widget that doesn't support the operation."""
        mock_widget = Mock()
        del mock_widget.cut  # Remove the method
        mock_focus_widget.return_value = mock_widget
        
        # Should not raise exception
        window.cut_text()
    
    def test_find_metadata(self, window):
        """Test find metadata placeholder."""
        window.show_info_dialog = Mock()
        
        window.find_metadata()
        
        window.show_info_dialog.assert_called_once()
        assert "Find in Metadata" in window.show_info_dialog.call_args[0][0]
    
    def test_zoom_operations(self, window):
        """Test zoom operations."""
        window.show_status_message = Mock()
        
        window.zoom_in()
        window.zoom_out()
        window.zoom_reset()
        
        assert window.show_status_message.call_count == 3
    
    def test_show_metadata_options(self, window):
        """Test show metadata options dialog."""
        window.show_info_dialog = Mock()
        
        window.show_metadata_options()
        
        window.show_info_dialog.assert_called_once()
        args = window.show_info_dialog.call_args[0]
        assert "Metadata Options" in args[0]
        assert "Supported file formats" in args[1]
    
    def test_show_batch_processing(self, window):
        """Test show batch processing dialog."""
        window.show_info_dialog = Mock()
        
        window.show_batch_processing()
        
        window.show_info_dialog.assert_called_once()
        assert "Batch Processing" in window.show_info_dialog.call_args[0][0]
    
    def test_analyze_documents_no_files(self, window):
        """Test analyze documents with no files selected."""
        window.selected_files = []
        window.show_warning_dialog = Mock()
        
        window.analyze_documents()
        
        window.show_warning_dialog.assert_called_once()
        assert "No Documents Selected" in window.show_warning_dialog.call_args[0][0]
    
    def test_analyze_documents_with_files(self, window):
        """Test analyze documents with files selected."""
        window.selected_files = ['test1.docx', 'test2.xlsx']
        window.show_info_dialog = Mock()
        
        window.analyze_documents()
        
        window.show_info_dialog.assert_called_once()
        args = window.show_info_dialog.call_args[0]
        assert "Document Analysis" in args[0]
        assert "Analyzing 2 document(s)" in args[1]
    
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_show_help(self, mock_info, window):
        """Test show help dialog."""
        window.show_help()
        
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Office Metadata Editor Help" in args[1]
        assert "Overview:" in args[2]
        assert "Supported Formats:" in args[2]
        assert "Features:" in args[2]
        assert "Usage:" in args[2]
        assert "Keyboard Shortcuts:" in args[2]
    
    def test_close_event_with_worker(self, window):
        """Test close event with running worker."""
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        window.worker = mock_worker
        
        mock_event = Mock()
        mock_event.accept = Mock()
        
        # Mock the super() call properly
        with patch.object(window.__class__.__bases__[0], 'closeEvent') as mock_super_close:
            window.closeEvent(mock_event)
            
            mock_worker.cancel.assert_called_once()
            mock_worker.wait.assert_called_once()
            mock_super_close.assert_called_once_with(mock_event)
    
    def test_close_event_without_worker(self, window):
        """Test close event without worker."""
        window.worker = None
        mock_event = Mock()
        mock_event.accept = Mock()
        
        # Mock the super() call properly
        with patch.object(window.__class__.__bases__[0], 'closeEvent') as mock_super_close:
            window.closeEvent(mock_event)
            
            mock_super_close.assert_called_once_with(mock_event)


class TestMainFunction:
    """Test suite for main function."""
    
    @patch('src.utilities.metadata.office_meta_data_editor.sys.exit')
    @patch('src.utilities.metadata.office_meta_data_editor.QApplication')
    def test_main_function_execution(self, mock_app_class, mock_exit):
        """Test main function execution."""
        if not PYQT5_AVAILABLE:
            pytest.skip("PyQt5 not available")
        
        mock_app = Mock()
        mock_app.exec_.return_value = 0
        mock_app_class.return_value = mock_app
        
        with patch('src.utilities.metadata.office_meta_data_editor.OfficeMetaDataEditorGUI') as mock_gui:
            mock_window = Mock()
            mock_gui.return_value = mock_window
            
            # Import and call main function
            from src.utilities.metadata.office_meta_data_editor import main
            main()
            
            mock_app_class.assert_called_once()
            mock_gui.assert_called_once()
            mock_window.show.assert_called_once()
            mock_app.exec_.assert_called_once()
            mock_exit.assert_called_once_with(0)


class TestEdgeCases:
    """Test suite for edge cases and error scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not PYQT5_AVAILABLE:
            pytest.skip("PyQt5 not available")
        
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    def test_worker_with_empty_file_list(self, app):
        """Test worker with empty file list."""
        worker = OfficeMetadataWorker([], "read")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        worker.run()
        
        worker.finished.emit.assert_called_once()
        worker.file_processed.emit.assert_not_called()
    
    def test_worker_with_invalid_operation(self, app):
        """Test worker with invalid operation."""
        worker = OfficeMetadataWorker(["test.docx"], "invalid_operation")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.file_processed = Mock()
        worker.finished = Mock()
        worker.error_occurred = Mock()
        
        worker.run()
        
        worker.finished.emit.assert_called_once()
    
    def test_ooxml_metadata_malformed_xml(self, app):
        """Test OOXML metadata extraction with malformed XML."""
        temp_dir = tempfile.mkdtemp()
        try:
            docx_path = os.path.join(temp_dir, "malformed.docx")
            with zipfile.ZipFile(docx_path, 'w') as zf:
                # Write malformed XML
                zf.writestr("docProps/core.xml", "<?xml version='1.0'?><invalid>malformed")
            
            worker = OfficeMetadataWorker([docx_path], "read")
            metadata = worker.read_ooxml_metadata(docx_path)
            
            assert "error" in metadata
            assert "Core properties error" in metadata["error"]
        finally:
            shutil.rmtree(temp_dir)
    
    def test_metadata_extraction_unicode_filename(self, app):
        """Test metadata extraction with unicode filename."""
        temp_dir = tempfile.mkdtemp()
        try:
            unicode_filename = os.path.join(temp_dir, "tëst_文档.docx")
            with zipfile.ZipFile(unicode_filename, 'w') as zf:
                zf.writestr("word/document.xml", "<?xml version='1.0'?><document/>")
            
            worker = OfficeMetadataWorker([unicode_filename], "read")
            metadata = worker.read_metadata(unicode_filename)
            
            assert "file_info" in metadata
            assert metadata["file_info"]["filename"] == "tëst_文档.docx"
        finally:
            shutil.rmtree(temp_dir)
    
    def test_metadata_extraction_large_file(self, app):
        """Test metadata extraction from large file."""
        temp_dir = tempfile.mkdtemp()
        try:
            large_file = os.path.join(temp_dir, "large.pdf")
            with open(large_file, 'wb') as f:
                # Create a large file (10MB)
                f.write(b'%PDF-1.4\n')
                f.write(b'0' * (10 * 1024 * 1024))
            
            worker = OfficeMetadataWorker([large_file], "read")
            metadata = worker.read_metadata(large_file)
            
            assert "file_info" in metadata
            assert metadata["file_info"]["size"] > 10 * 1024 * 1024
        finally:
            shutil.rmtree(temp_dir)
    
    def test_permission_denied_file_access(self, app):
        """Test handling of permission denied errors."""
        # This test simulates permission denied by mocking os.stat
        with patch('os.stat', side_effect=PermissionError("Permission denied")):
            worker = OfficeMetadataWorker(["restricted.docx"], "read")
            metadata = worker.read_metadata("restricted.docx")
            
            assert "error" in metadata
            assert "File access error" in metadata["error"]
    
    def test_gui_with_corrupted_metadata(self, app):
        """Test GUI handling of corrupted metadata."""
        with patch('src.utilities.metadata.office_meta_data_editor.StandardWindow'):
            window = OfficeMetaDataEditorGUI()
            
            # Test with metadata containing various data types
            corrupted_metadata = {
                "built_in_properties": {"title": None, "author": 123, "invalid": object()},
                "document_properties": {"pages": []},
                "custom_properties": {"test": {"nested": "value"}}
            }
            
            # This should not raise an exception
            item = Mock()
            item.data.return_value = {"metadata": corrupted_metadata}
            
            window.show_file_metadata(item)
            
            # Tables should be populated with string representations
            assert window.builtin_table.rowCount() > 0
            assert window.document_table.rowCount() > 0
            assert window.custom_table.rowCount() > 0
    
    def test_export_metadata_with_non_serializable_data(self, app):
        """Test exporting metadata with non-serializable data."""
        with patch('src.utilities.metadata.office_meta_data_editor.StandardWindow'):
            window = OfficeMetaDataEditorGUI()
            
            # Add non-serializable data
            window.current_metadata = {
                'test.docx': {
                    'datetime_obj': datetime.now(),
                    'complex_obj': object(),
                    'normal_data': 'test'
                }
            }
            
            with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
                with patch('builtins.open', mock_open()) as mock_file:
                    with patch('json.dump') as mock_json_dump:
                        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
                            mock_dialog.return_value = ('/test/export.json', '')
                            
                            window.export_metadata()
                            
                            # Should use default=str to handle non-serializable objects
                            mock_json_dump.assert_called_once()
                            call_args = mock_json_dump.call_args
                            assert call_args[1]['default'] == str
    
    def test_worker_thread_cleanup(self, app):
        """Test proper worker thread cleanup."""
        with patch('src.utilities.metadata.office_meta_data_editor.StandardWindow'):
            window = OfficeMetaDataEditorGUI()
            
            # Create mock worker
            mock_worker = Mock()
            mock_worker.isRunning.return_value = False
            window.worker = mock_worker
            
            # Test operation finished cleanup
            window.operation_finished()
            
            mock_worker.deleteLater.assert_called_once()
            assert window.worker is None
    
    def test_empty_metadata_properties_handling(self, app):
        """Test handling of empty metadata properties."""
        temp_dir = tempfile.mkdtemp()
        try:
            docx_path = os.path.join(temp_dir, "empty_props.docx")
            with zipfile.ZipFile(docx_path, 'w') as zf:
                # Create core.xml with empty elements
                core_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title></dc:title>
    <dc:creator/>
    <dc:subject></dc:subject>
</cp:coreProperties>'''
                zf.writestr("docProps/core.xml", core_xml)
            
            worker = OfficeMetadataWorker([docx_path], "read")
            metadata = worker.read_ooxml_metadata(docx_path)
            
            # Should handle empty elements gracefully
            assert "built_in_properties" in metadata
            # Empty elements should not be included
            assert len(metadata["built_in_properties"]) == 0
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=src.utilities.metadata.office_meta_data_editor",
        "--cov-report=term-missing",
        "--cov-report=html:tests/unit/result_office_meta_data_editor_coverage_2025-08-24",
        "--cov-report=json:tests/unit/result_office_meta_data_editor_coverage_2025-08-24.json"
    ])