"""
Comprehensive Unit Tests for Enhanced Editor

Test file for enhanced_editor.py using pytest framework with standardized output
and detailed coverage analysis.

Created: 2025-08-31
Author: Test Framework Generator
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'file_operations', 'enhanced_editor'))

# Import PyQt5 modules first to avoid conflicts
import PyQt5.QtWidgets
# Import the modules to test
from enhanced_editor import (DocumentManager, DocumentType, EditorSettings,
                             EnhancedEditor, LineNumberArea, PreferencesDialog,
                             SearchDialog, SearchOptions, SyntaxHighlighter,
                             TextEditor)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtWidgets import QApplication, QWidget


class TestFixture:
    """Test fixture class for shared test resources."""
    
    app = None
    temp_dir = None
    test_files = {}
        
    @classmethod
    def setup_class(cls):
        """Set up test class resources."""
        pass
        
    @classmethod
    def teardown_class(cls):
        """Clean up test class resources."""
        if cls.temp_dir:
            import shutil
            shutil.rmtree(cls.temp_dir, ignore_errors=True)
        if cls.app:
            cls.app.quit()
    
    def setup_method(self):
        """Set up each test method."""
        # Create QApplication if not exists
        if not QApplication.instance():
            TestFixture.app = QApplication([])
        
        # Create temporary directory for test files
        if not TestFixture.temp_dir:
            TestFixture.temp_dir = tempfile.mkdtemp(prefix='enhanced_editor_test_')
        
        # Create test files
        self.create_test_files()
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Clear QSettings
        settings = QSettings("RFU", "EnhancedEditor")
        settings.clear()
    
    def create_test_files(self):
        """Create test files for testing."""
        # Ensure temp directory exists
        os.makedirs(TestFixture.temp_dir, exist_ok=True)
        
        test_files_data = {
            'test.txt': 'This is a test file.\nWith multiple lines.\nFor testing purposes.',
            'test.py': '''def hello_world():
    """Print hello world message."""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()''',
            'test.js': '''function greetUser(name) {
    // Function to greet user
    console.log("Hello, " + name + "!");
    return true;
}

greetUser("Test");''',
            'test.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Test Content</h1>
    <p>This is a test HTML file.</p>
</body>
</html>''',
            'test.json': '''{"name": "test", "version": "1.0", "data": [1, 2, 3]}''',
            'empty.txt': '',
            'unicode.txt': 'Test with unicode: ñáéíóú 中文 🚀'
        }
        
        for filename, content in test_files_data.items():
            filepath = os.path.join(TestFixture.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            TestFixture.test_files[filename] = filepath


class TestDocumentType(TestFixture):
    """Test DocumentType enumeration."""
    
    def test_document_type_values(self):
        """Test DocumentType enum values."""
        assert DocumentType.TEXT.value == "text"
        assert DocumentType.PYTHON.value == "python"
        assert DocumentType.JAVASCRIPT.value == "javascript"
        assert DocumentType.HTML.value == "html"
        assert DocumentType.CSS.value == "css"
        assert DocumentType.XML.value == "xml"
        assert DocumentType.JSON.value == "json"
        assert DocumentType.YAML.value == "yaml"
        assert DocumentType.SQL.value == "sql"
        assert DocumentType.BASH.value == "bash"
        assert DocumentType.POWERSHELL.value == "powershell"
        assert DocumentType.C.value == "c"
        assert DocumentType.CPP.value == "cpp"
        assert DocumentType.JAVA.value == "java"
        assert DocumentType.CSHARP.value == "csharp"
        assert DocumentType.MARKDOWN.value == "markdown"
    
    def test_document_type_count(self):
        """Test that all expected document types are present."""
        expected_count = 16
        actual_count = len([item for item in DocumentType])
        assert actual_count == expected_count


class TestSearchOptions(TestFixture):
    """Test SearchOptions dataclass."""
    
    def test_default_search_options(self):
        """Test default SearchOptions values."""
        options = SearchOptions()
        assert options.case_sensitive is False
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
        assert options.search_backwards is False
    
    def test_custom_search_options(self):
        """Test custom SearchOptions values."""
        options = SearchOptions(
            case_sensitive=True,
            whole_words=True,
            use_regex=True,
            wrap_around=False,
            search_backwards=True
        )
        assert options.case_sensitive is True
        assert options.whole_words is True
        assert options.use_regex is True
        assert options.wrap_around is False
        assert options.search_backwards is True


class TestEditorSettings(TestFixture):
    """Test EditorSettings dataclass."""
    
    def test_default_editor_settings(self):
        """Test default EditorSettings values."""
        settings = EditorSettings()
        assert settings.font_family == "Consolas"
        assert settings.font_size == 11
        assert settings.tab_width == 4
        assert settings.use_spaces is True
        assert settings.word_wrap is True
        assert settings.line_numbers is True
        assert settings.syntax_highlighting is True
        assert settings.auto_indent is True
        assert settings.show_whitespace is False
        assert settings.theme == "default"
    
    def test_custom_editor_settings(self):
        """Test custom EditorSettings values."""
        settings = EditorSettings(
            font_family="Arial",
            font_size=14,
            tab_width=2,
            use_spaces=False,
            word_wrap=False,
            line_numbers=False,
            syntax_highlighting=False,
            auto_indent=False,
            show_whitespace=True,
            theme="dark"
        )
        assert settings.font_family == "Arial"
        assert settings.font_size == 14
        assert settings.tab_width == 2
        assert settings.use_spaces is False
        assert settings.word_wrap is False
        assert settings.line_numbers is False
        assert settings.syntax_highlighting is False
        assert settings.auto_indent is False
        assert settings.show_whitespace is True
        assert settings.theme == "dark"


class TestSyntaxHighlighter(TestFixture):
    """Test SyntaxHighlighter class."""
    
    def test_syntax_highlighter_creation(self):
        """Test SyntaxHighlighter creation."""
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        assert highlighter.language == DocumentType.PYTHON
        assert isinstance(highlighter.highlighting_rules, list)
    
    def test_python_highlighting_rules(self):
        """Test Python syntax highlighting rules setup."""
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        
        # Should have rules for keywords, strings, and comments
        assert len(highlighter.highlighting_rules) > 0
        
        # Test that rules are properly formatted (pattern, format tuples)
        for rule in highlighter.highlighting_rules:
            assert len(rule) == 2
            assert hasattr(rule[0], 'finditer')  # Should be a compiled regex
    
    def test_javascript_highlighting_rules(self):
        """Test JavaScript syntax highlighting rules setup."""
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.JAVASCRIPT)
        
        # Should have rules for JavaScript keywords
        assert len(highlighter.highlighting_rules) > 0
    
    def test_text_highlighting_rules(self):
        """Test plain text highlighting (should have no rules)."""
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.TEXT)
        
        # Plain text should have no highlighting rules
        assert len(highlighter.highlighting_rules) == 0
    
    @patch('enhanced_editor.SyntaxHighlighter.setFormat')
    def test_highlight_block(self, mock_set_format):
        """Test highlightBlock method."""
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        
        # Test highlighting Python code
        test_text = "def hello_world():"
        highlighter.highlightBlock(test_text)
        
        # Should call setFormat for 'def' keyword
        mock_set_format.assert_called()


class TestDocumentManager(TestFixture):
    """Test DocumentManager class."""
    
    def test_document_manager_creation(self):
        """Test DocumentManager initialization."""
        manager = DocumentManager()
        assert isinstance(manager.documents, dict)
        assert manager.current_document is None
        assert isinstance(manager.recent_files, list)
        assert manager.max_recent_files == 10
    
    def test_create_document_basic(self):
        """Test basic document creation."""
        manager = DocumentManager()
        doc_id = manager.create_document("Hello World")
        
        assert doc_id.startswith("doc_")
        assert doc_id in manager.documents
        assert manager.current_document == doc_id
        
        document = manager.get_document(doc_id)
        assert document['content'] == "Hello World"
        assert document['file_path'] is None
        assert document['is_modified'] is False
        assert document['encoding'] == 'utf-8'
        assert document['document_type'] == DocumentType.TEXT
    
    def test_create_document_with_file_path(self):
        """Test document creation with file path."""
        manager = DocumentManager()
        test_file = TestFixture.test_files['test.py']
        doc_id = manager.create_document("print('hello')", test_file)
        
        document = manager.get_document(doc_id)
        assert document['file_path'] == test_file
        assert document['document_type'] == DocumentType.PYTHON
    
    def test_detect_document_type(self):
        """Test document type detection by file extension."""
        manager = DocumentManager()
        
        test_cases = [
            ('test.py', DocumentType.PYTHON),
            ('test.js', DocumentType.JAVASCRIPT),
            ('test.html', DocumentType.HTML),
            ('test.htm', DocumentType.HTML),
            ('test.css', DocumentType.CSS),
            ('test.xml', DocumentType.XML),
            ('test.json', DocumentType.JSON),
            ('test.yaml', DocumentType.YAML),
            ('test.yml', DocumentType.YAML),
            ('test.sql', DocumentType.SQL),
            ('test.sh', DocumentType.BASH),
            ('test.ps1', DocumentType.POWERSHELL),
            ('test.c', DocumentType.C),
            ('test.cpp', DocumentType.CPP),
            ('test.cc', DocumentType.CPP),
            ('test.cxx', DocumentType.CPP),
            ('test.java', DocumentType.JAVA),
            ('test.cs', DocumentType.CSHARP),
            ('test.md', DocumentType.MARKDOWN),
            ('test.markdown', DocumentType.MARKDOWN),
            ('test.txt', DocumentType.TEXT),
            ('unknown.xyz', DocumentType.TEXT),
            (None, DocumentType.TEXT)
        ]
        
        for file_path, expected_type in test_cases:
            detected_type = manager._detect_document_type(file_path)
            assert detected_type == expected_type, f"Failed for {file_path}"
    
    def test_update_document(self):
        """Test document update functionality."""
        manager = DocumentManager()
        doc_id = manager.create_document("Initial content")
        
        manager.update_document(doc_id, content="Updated content", is_modified=True)
        
        document = manager.get_document(doc_id)
        assert document['content'] == "Updated content"  # Content should be updated
        assert document['is_modified'] is True
    
    def test_remove_document(self):
        """Test document removal."""
        manager = DocumentManager()
        doc_id = manager.create_document("Test content")
        
        assert doc_id in manager.documents
        assert manager.current_document == doc_id
        
        manager.remove_document(doc_id)
        
        assert doc_id not in manager.documents
        assert manager.current_document is None
    
    def test_add_to_recent_files(self):
        """Test adding files to recent files list."""
        manager = DocumentManager()
        
        # Add files
        manager.add_to_recent_files("file1.txt")
        manager.add_to_recent_files("file2.txt")
        manager.add_to_recent_files("file3.txt")
        
        assert manager.recent_files == ["file3.txt", "file2.txt", "file1.txt"]
        
        # Add duplicate (should move to front)
        manager.add_to_recent_files("file1.txt")
        assert manager.recent_files == ["file1.txt", "file3.txt", "file2.txt"]
    
    def test_recent_files_limit(self):
        """Test recent files list respects maximum limit."""
        manager = DocumentManager()
        
        # Add more than max files
        for i in range(15):
            manager.add_to_recent_files(f"file{i}.txt")
        
        assert len(manager.recent_files) == manager.max_recent_files
        assert "file14.txt" in manager.recent_files
        assert "file0.txt" not in manager.recent_files


class TestSearchDialog(TestFixture):
    """Test SearchDialog class."""
    
    def test_search_dialog_creation(self):
        """Test SearchDialog initialization."""
        dialog = SearchDialog()
        assert dialog.windowTitle() == "Find and Replace"
        assert dialog.isModal() is False
        
        # Check UI elements exist
        assert hasattr(dialog, 'search_edit')
        assert hasattr(dialog, 'replace_edit')
        assert hasattr(dialog, 'case_sensitive_cb')
        assert hasattr(dialog, 'whole_words_cb')
        assert hasattr(dialog, 'use_regex_cb')
        assert hasattr(dialog, 'wrap_around_cb')
    
    def test_search_options_default(self):
        """Test default search options."""
        dialog = SearchDialog()
        options = dialog.get_search_options()
        
        assert options.case_sensitive is False
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
    
    def test_search_options_custom(self):
        """Test custom search options."""
        dialog = SearchDialog()
        
        # Set custom options
        dialog.case_sensitive_cb.setChecked(True)
        dialog.whole_words_cb.setChecked(True)
        dialog.use_regex_cb.setChecked(True)
        dialog.wrap_around_cb.setChecked(False)
        
        options = dialog.get_search_options()
        
        assert options.case_sensitive is True
        assert options.whole_words is True
        assert options.use_regex is True
        assert options.wrap_around is False


class TestTextEditor(TestFixture):
    """Test TextEditor class."""
    
    def test_text_editor_creation(self):
        """Test TextEditor initialization."""
        editor = TextEditor()
        assert editor.document_type == DocumentType.TEXT
        assert editor.highlighter is None
        assert isinstance(editor.settings, EditorSettings)
        assert hasattr(editor, 'line_number_area')
    
    def test_set_document_type(self):
        """Test setting document type."""
        editor = TextEditor()
        editor.set_document_type(DocumentType.PYTHON)
        
        assert editor.document_type == DocumentType.PYTHON
        assert editor.highlighter is not None
        assert isinstance(editor.highlighter, SyntaxHighlighter)
    
    def test_line_number_area_width(self):
        """Test line number area width calculation."""
        editor = TextEditor()
        width = editor.line_number_area_width()
        assert isinstance(width, int)
        assert width > 0
    
    def test_apply_settings(self):
        """Test applying editor settings."""
        editor = TextEditor()
        settings = EditorSettings(font_size=14, tab_width=8)
        editor.settings = settings
        
        editor.apply_settings()
        
        # Verify font settings applied
        font = editor.font()
        assert font.pointSize() == 14
    
    @patch('enhanced_editor.TextEditor.emit')
    def test_content_changed_signal(self, mock_emit):
        """Test content changed signal emission."""
        editor = TextEditor()
        editor.setPlainText("New content")
        
        # Signal should be emitted when content changes
        mock_emit.assert_called()
    
    def test_cursor_position_tracking(self):
        """Test cursor position change tracking."""
        editor = TextEditor()
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        
        # Move cursor to second line
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Down)
        editor.setTextCursor(cursor)
        
        # Position should be tracked
        assert cursor.blockNumber() == 1  # Second line (0-indexed)


class TestLineNumberArea(TestFixture):
    """Test LineNumberArea class."""
    
    def test_line_number_area_creation(self):
        """Test LineNumberArea initialization."""
        editor = TextEditor()
        line_area = LineNumberArea(editor)
        
        assert line_area.editor == editor
        assert isinstance(line_area, QWidget)
    
    def test_size_hint(self):
        """Test size hint calculation."""
        editor = TextEditor()
        line_area = LineNumberArea(editor)
        
        size_hint = line_area.sizeHint()
        assert size_hint.width() > 0
        assert size_hint.height() == 0  # Height is managed by parent


class TestEnhancedEditor(TestFixture):
    """Test EnhancedEditor main class."""
    
    def test_enhanced_editor_creation(self):
        """Test EnhancedEditor initialization."""
        # Patch all the UI setup methods to avoid Qt dependency issues
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Check basic initialization
            assert isinstance(editor.document_manager, DocumentManager)
            assert editor.search_dialog is None
            assert isinstance(editor.settings, EditorSettings)
            assert isinstance(editor.tab_to_doc_mapping, dict)
    
    @patch('enhanced_editor.EnhancedEditor.setup_ui')
    @patch('enhanced_editor.EnhancedEditor.setup_menu_callbacks')
    @patch('enhanced_editor.EnhancedEditor.load_settings')
    @patch('enhanced_editor.EnhancedEditor.new_document')
    def test_enhanced_editor_full_init(self, mock_new_doc, mock_load_settings, 
                                     mock_setup_menu, mock_setup_ui):
        """Test full EnhancedEditor initialization sequence."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Verify initialization methods were called
            mock_setup_ui.assert_called_once()
            mock_setup_menu.assert_called_once()
            mock_load_settings.assert_called_once()
            mock_new_doc.assert_called_once()
    
    def test_new_document(self):
        """Test new document creation."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Reset the new_document mock to test the actual method
            with patch.object(editor.document_manager, 'create_document') as mock_create:
                mock_create.return_value = "doc_1"
                
                # Call the actual new_document method
                doc_id = editor.new_document("Test content")
                
                assert doc_id == "doc_1"
                mock_create.assert_called_once_with("Test content")
    
    @patch('enhanced_editor.QFileDialog.getOpenFileName')
    @patch('builtins.open', new_callable=mock_open, read_data="Test file content")
    def test_open_document(self, mock_file, mock_dialog):
        """Test opening a document from file."""
        mock_dialog.return_value = (TestFixture.test_files['test.txt'], '')
        
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            with patch.object(editor, 'new_document') as mock_new_doc:
                mock_new_doc.return_value = "doc_0"
                with patch.object(editor, 'update_recent_files_list'):
                    doc_id = editor.open_document()
                    
                    assert doc_id == "doc_0"
                    mock_new_doc.assert_called_once()
    
    def test_detect_encoding_with_chardet(self):
        """Test encoding detection with chardet."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Test with mock chardet
            with patch('chardet.detect') as mock_detect:
                mock_detect.return_value = {'encoding': 'utf-8'}
                with patch('builtins.open', mock_open(read_data=b'test')):
                    encoding = editor.detect_encoding("test.txt")
                    assert encoding == 'utf-8'
    
    def test_detect_encoding_fallback(self):
        """Test encoding detection fallback when chardet not available."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Mock ImportError for chardet
            with patch('enhanced_editor.chardet', side_effect=ImportError):
                with patch('builtins.open', mock_open(read_data="test")):
                    encoding = editor.detect_encoding("test.txt")
                    assert encoding in ['utf-8', 'utf-16', 'ascii', 'latin-1']
    
    def test_save_document_new_file(self):
        """Test saving a document without file path (should call save_as)."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.document_manager = DocumentManager()
            doc_id = editor.document_manager.create_document("Test content")
            
            with patch.object(editor, 'save_document_as') as mock_save_as:
                mock_save_as.return_value = True
                result = editor.save_document(doc_id)
                
                mock_save_as.assert_called_once_with(doc_id)
                assert result is True
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_document_existing_file(self, mock_file):
        """Test saving a document with existing file path."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.document_manager = DocumentManager()
            
            # Create document with file path
            test_file = TestFixture.test_files['test.txt']
            doc_id = editor.document_manager.create_document("Test content", test_file)
            
            # Mock editor for document
            mock_editor = Mock()
            mock_editor.toPlainText.return_value = "Test content"
            
            with patch.object(editor, 'get_editor_for_document') as mock_get_editor:
                mock_get_editor.return_value = mock_editor
                with patch.object(editor, 'update_tab_title'):
                    result = editor.save_document(doc_id)
                    
                    assert result is True
                    mock_file.assert_called_once()
    
    def test_close_document_tab_unsaved_save(self):
        """Test closing tab with unsaved changes - save option."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create modified document
            doc_id = editor.document_manager.create_document("Test content")
            editor.document_manager.update_document(doc_id, is_modified=True)
            editor.tab_to_doc_mapping[0] = doc_id
            
            with patch('enhanced_editor.QMessageBox.question') as mock_question:
                mock_question.return_value = PyQt5.QtWidgets.QMessageBox.Save
                with patch.object(editor, 'save_document') as mock_save:
                    mock_save.return_value = True
                    
                    editor.close_document_tab(0)
                    
                    mock_save.assert_called_once_with(doc_id)
    
    def test_close_document_tab_unsaved_discard(self):
        """Test closing tab with unsaved changes - discard option."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create modified document
            doc_id = editor.document_manager.create_document("Test content")
            editor.document_manager.update_document(doc_id, is_modified=True)
            editor.tab_to_doc_mapping[0] = doc_id
            
            with patch('enhanced_editor.QMessageBox.question') as mock_question:
                mock_question.return_value = PyQt5.QtWidgets.QMessageBox.Discard
                with patch.object(editor, 'update_status_bar'):
                    
                    editor.close_document_tab(0)
                    
                    # Document should be removed
                    assert doc_id not in editor.document_manager.documents
    
    def test_close_document_tab_unsaved_cancel(self):
        """Test closing tab with unsaved changes - cancel option."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create modified document
            doc_id = editor.document_manager.create_document("Test content")
            editor.document_manager.update_document(doc_id, is_modified=True)
            editor.tab_to_doc_mapping[0] = doc_id
            
            with patch('enhanced_editor.QMessageBox.question') as mock_question:
                mock_question.return_value = PyQt5.QtWidgets.QMessageBox.Cancel
                
                editor.close_document_tab(0)
                
                # Document should not be removed
                assert doc_id in editor.document_manager.documents
                editor.tab_widget.removeTab.assert_not_called()
    
    def test_perform_search_simple(self):
        """Test simple text search."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Create mock text editor
            mock_editor = Mock(spec=TextEditor)
            mock_document = Mock()
            mock_cursor = Mock()
            
            mock_editor.textCursor.return_value = mock_cursor
            mock_editor.document.return_value = mock_document
            
            # Mock found cursor
            found_cursor = Mock()
            found_cursor.isNull.return_value = False
            mock_document.find.return_value = found_cursor
            
            options = SearchOptions(case_sensitive=True)
            result = editor.perform_search(mock_editor, "test", options, forward=True)
            
            assert result is True
            mock_editor.setTextCursor.assert_called_with(found_cursor)
    
    def test_perform_search_regex(self):
        """Test regex search."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Create mock text editor
            mock_editor = Mock(spec=TextEditor)
            mock_cursor = Mock()
            mock_cursor.position.return_value = 0
            
            mock_editor.textCursor.return_value = mock_cursor
            mock_editor.toPlainText.return_value = "test content for regex testing"
            
            options = SearchOptions(use_regex=True)
            result = editor.perform_search(mock_editor, r"test\w+", options, forward=True)
            
            assert result is True
    
    def test_replace_all_simple(self):
        """Test replace all functionality."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.search_dialog = Mock()
            editor.search_dialog.search_edit.text.return_value = "old"
            editor.search_dialog.replace_edit.text.return_value = "new"
            editor.search_dialog.get_search_options.return_value = SearchOptions()
            
            # Create mock text editor
            mock_editor = Mock(spec=TextEditor)
            mock_editor.toPlainText.return_value = "old text with old content"
            
            with patch.object(editor, 'get_current_editor') as mock_get_editor:
                mock_get_editor.return_value = mock_editor
                with patch('enhanced_editor.QMessageBox.information'):
                    
                    editor.replace_all()
                    
                    # Should set new text with replacements
                    mock_editor.setPlainText.assert_called_once()
                    call_args = mock_editor.setPlainText.call_args[0][0]
                    assert "new text with new content" == call_args
    
    def test_zoom_operations(self):
        """Test zoom in, zoom out, and zoom reset."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            initial_size = editor.settings.font_size
            
            with patch.object(editor, 'apply_settings_to_all_editors'):
                # Test zoom in
                editor.zoom_in()
                assert editor.settings.font_size == initial_size + 1
                
                # Test zoom out
                editor.zoom_out()
                assert editor.settings.font_size == initial_size
                
                # Test zoom reset
                editor.zoom_reset()
                assert editor.settings.font_size == 11
    
    def test_text_statistics(self):
        """Test text statistics calculation."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Mock text editor with content
            mock_editor = Mock()
            mock_editor.toPlainText.return_value = "Hello world!\n\nThis is a test.\nWith multiple lines."
            
            with patch.object(editor, 'get_current_editor') as mock_get_editor:
                mock_get_editor.return_value = mock_editor
                with patch('enhanced_editor.QMessageBox.information') as mock_msgbox:
                    
                    editor.show_text_statistics()
                    
                    # Should show message box with statistics
                    mock_msgbox.assert_called_once()
                    args = mock_msgbox.call_args[0]
                    assert "Text Statistics" in args[1]
    
    def test_settings_save_load(self):
        """Test settings save and load functionality."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Modify settings
            editor.settings.font_size = 14
            editor.settings.font_family = "Arial"
            editor.document_manager.recent_files = ["file1.txt", "file2.txt"]
            
            # Save settings
            editor.save_settings()
            
            # Create new editor and load settings
            editor2 = EnhancedEditor()
            editor2.load_settings()
            
            # Verify settings loaded
            assert editor2.settings.font_size == 14
            assert editor2.settings.font_family == "Arial"
            assert editor2.document_manager.recent_files == ["file1.txt", "file2.txt"]


class TestPreferencesDialog(TestFixture):
    """Test PreferencesDialog class."""
    
    def test_preferences_dialog_creation(self):
        """Test PreferencesDialog initialization."""
        settings = EditorSettings()
        dialog = PreferencesDialog(settings=settings)
        
        assert dialog.windowTitle() == "Enhanced Editor Preferences"
        assert dialog.isModal() is True
        assert dialog.settings == settings
    
    def test_load_settings_to_dialog(self):
        """Test loading settings into dialog controls."""
        settings = EditorSettings(
            font_family="Arial",
            font_size=14,
            tab_width=8,
            use_spaces=False,
            word_wrap=False,
            line_numbers=False,
            syntax_highlighting=False
        )
        
        dialog = PreferencesDialog(settings=settings)
        dialog.load_settings()
        
        # Verify settings loaded into controls
        assert dialog.font_size_spin.value() == 14
        assert dialog.tab_width_spin.value() == 8
        assert dialog.use_spaces_check.isChecked() is False
        assert dialog.word_wrap_check.isChecked() is False
        assert dialog.line_numbers_check.isChecked() is False
        assert dialog.syntax_highlighting_check.isChecked() is False
    
    def test_get_settings_from_dialog(self):
        """Test getting settings from dialog controls."""
        dialog = PreferencesDialog()
        
        # Set values in dialog
        dialog.font_family_combo.setCurrentText("Arial")
        dialog.font_size_spin.setValue(16)
        dialog.tab_width_spin.setValue(2)
        dialog.use_spaces_check.setChecked(False)
        dialog.word_wrap_check.setChecked(False)
        dialog.line_numbers_check.setChecked(False)
        dialog.syntax_highlighting_check.setChecked(False)
        
        settings = dialog.get_settings()
        
        # Verify settings retrieved correctly
        assert settings.font_family == "Arial"
        assert settings.font_size == 16
        assert settings.tab_width == 2
        assert settings.use_spaces is False
        assert settings.word_wrap is False
        assert settings.line_numbers is False
        assert settings.syntax_highlighting is False


class TestErrorHandling(TestFixture):
    """Test error handling scenarios."""
    
    def test_open_nonexistent_file(self):
        """Test opening a non-existent file."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            with patch('enhanced_editor.QMessageBox.critical') as mock_error:
                result = editor.open_document("/nonexistent/file.txt")
                
                assert result is None
                mock_error.assert_called_once()
    
    def test_save_file_permission_error(self):
        """Test saving file with permission error."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.document_manager = DocumentManager()
            
            # Create document with file path
            doc_id = editor.document_manager.create_document("Test", "/readonly/file.txt")
            
            # Mock editor
            mock_editor = Mock()
            mock_editor.toPlainText.return_value = "Test content"
            
            with patch.object(editor, 'get_editor_for_document') as mock_get_editor:
                mock_get_editor.return_value = mock_editor
                with patch('builtins.open', side_effect=PermissionError("Access denied")):
                    with patch('enhanced_editor.QMessageBox.critical') as mock_error:
                        
                        result = editor.save_document(doc_id)
                        
                        assert result is False
                        mock_error.assert_called_once()
    
    def test_invalid_regex_search(self):
        """Test search with invalid regex pattern."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            mock_editor = Mock(spec=TextEditor)
            mock_cursor = Mock()
            mock_cursor.position.return_value = 0
            mock_editor.textCursor.return_value = mock_cursor
            mock_editor.toPlainText.return_value = "test content"
            
            # Use invalid regex pattern
            options = SearchOptions(use_regex=True)
            
            with patch('re.compile', side_effect=Exception("Invalid regex")):
                with patch('enhanced_editor.QMessageBox.information') as mock_info:
                    result = editor.perform_search(mock_editor, "[invalid", options)
                    
                    # Should handle error gracefully
                    assert result is False


class TestIntegration(TestFixture):
    """Integration tests for multiple components working together."""
    
    @pytest.mark.integration
    def test_complete_document_workflow(self):
        """Test complete document creation, editing, and saving workflow."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create document
            with patch.object(editor, 'update_status_bar'):
                doc_id = editor.new_document("Initial content")
                
                # Verify document created
                assert doc_id in editor.document_manager.documents
                document = editor.document_manager.get_document(doc_id)
                assert document['content'] == "Initial content"
                assert document['is_modified'] is False
                
                # Mark as modified
                editor.mark_document_modified(doc_id)
                assert document['is_modified'] is True
                
                # Save document
                document['file_path'] = TestFixture.test_files['test.txt']
                mock_editor = Mock()
                mock_editor.toPlainText.return_value = "Modified content"
                
                with patch.object(editor, 'get_editor_for_document') as mock_get:
                    mock_get.return_value = mock_editor
                    with patch('builtins.open', mock_open()) as mock_file:
                        with patch.object(editor, 'update_tab_title'):
                            result = editor.save_document(doc_id)
                            
                            assert result is True
                            assert document['is_modified'] is False
    
    @pytest.mark.integration
    def test_search_and_replace_workflow(self):
        """Test complete search and replace workflow."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Create search dialog
            editor.show_search_dialog()
            assert editor.search_dialog is not None
            
            # Set search parameters
            editor.search_dialog.search_edit.setText("test")
            editor.search_dialog.replace_edit.setText("demo")
            
            # Mock text editor
            mock_editor = Mock(spec=TextEditor)
            mock_editor.toPlainText.return_value = "This is a test file with test content."
            
            with patch.object(editor, 'get_current_editor') as mock_get_editor:
                mock_get_editor.return_value = mock_editor
                with patch('enhanced_editor.QMessageBox.information'):
                    
                    # Perform replace all
                    editor.replace_all()
                    
                    # Verify replacement occurred
                    mock_editor.setPlainText.assert_called_once()
                    replaced_text = mock_editor.setPlainText.call_args[0][0]
                    assert "demo" in replaced_text
                    assert "test" not in replaced_text
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_documents_workflow(self):
        """Test working with multiple documents simultaneously."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create multiple documents
            with patch.object(editor, 'update_status_bar'):
                doc1_id = editor.new_document("Document 1 content")
                doc2_id = editor.new_document("Document 2 content") 
                doc3_id = editor.new_document("Document 3 content")
                
                # Verify all documents created
                assert len(editor.document_manager.documents) == 3
                assert doc1_id in editor.document_manager.documents
                assert doc2_id in editor.document_manager.documents
                assert doc3_id in editor.document_manager.documents
                
                # Test document switching
                editor.document_manager.current_document = doc1_id
                assert editor.document_manager.current_document == doc1_id
                
                editor.document_manager.current_document = doc2_id
                assert editor.document_manager.current_document == doc2_id
                
                # Test closing documents
                editor.document_manager.remove_document(doc1_id)
                assert doc1_id not in editor.document_manager.documents
                assert len(editor.document_manager.documents) == 2
    
    @pytest.mark.integration
    def test_syntax_highlighting_integration(self):
        """Test syntax highlighting with different document types."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            # Test Python file highlighting
            editor = TextEditor()
            editor.set_document_type(DocumentType.PYTHON)
            assert editor.document_type == DocumentType.PYTHON
            assert editor.highlighter is not None
            
            # Test JavaScript file highlighting  
            editor2 = TextEditor()
            editor2.set_document_type(DocumentType.JAVASCRIPT)
            assert editor2.document_type == DocumentType.JAVASCRIPT
            assert editor2.highlighter is not None
            
            # Test that different highlighters are created
            assert editor.highlighter != editor2.highlighter
    
    @pytest.mark.integration
    def test_preferences_integration(self):
        """Test preferences dialog integration with main editor."""
        settings = EditorSettings(font_size=12, word_wrap=False)
        dialog = PreferencesDialog(settings=settings)
        
        # Load settings into dialog
        dialog.load_settings()
        assert dialog.font_size_spin.value() == 12
        assert dialog.word_wrap_check.isChecked() is False
        
        # Modify settings in dialog
        dialog.font_size_spin.setValue(16)
        dialog.word_wrap_check.setChecked(True)
        
        # Get modified settings
        new_settings = dialog.get_settings()
        assert new_settings.font_size == 16
        assert new_settings.word_wrap is True
        
        # Original settings should be unchanged
        assert settings.font_size == 12
        assert settings.word_wrap is False


class TestPerformance(TestFixture):
    """Performance tests for Enhanced Editor components."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_document_handling(self):
        """Test handling of large documents."""
        # Create large content
        large_content = "Line of text\n" * 10000  # 10k lines
        
        manager = DocumentManager()
        doc_id = manager.create_document(large_content)
        
        # Should handle large content without issues
        document = manager.get_document(doc_id)
        assert document is not None
        assert len(document['content']) == len(large_content)
    
    @pytest.mark.performance
    def test_syntax_highlighting_performance(self):
        """Test syntax highlighting performance on medium-sized code."""
        # Create moderately large Python code
        python_code = '''
def function_{}():
    """Test function {}."""
    for i in range(100):
        if i % 2 == 0:
            print(f"Even number: {{i}}")
        else:
            print(f"Odd number: {{i}}")
    return True
'''.format * 50  # Repeat pattern 50 times
        
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        
        # Test highlighting - should complete without timeout
        start_time = time.time()
        document.setPlainText(python_code)
        end_time = time.time()
        
        # Should complete within reasonable time (2 seconds)
        assert end_time - start_time < 2.0
    
    @pytest.mark.performance  
    def test_document_manager_performance(self):
        """Test document manager performance with many documents."""
        manager = DocumentManager()
        
        # Create many documents
        doc_ids = []
        start_time = time.time()
        
        for i in range(100):
            doc_id = manager.create_document(f"Content {i}")
            doc_ids.append(doc_id)
        
        end_time = time.time()
        
        # Should create 100 documents quickly (under 1 second)
        assert end_time - start_time < 1.0
        assert len(manager.documents) == 100
        
        # Test retrieval performance
        start_time = time.time()
        for doc_id in doc_ids:
            document = manager.get_document(doc_id)
            assert document is not None
        end_time = time.time()
        
        # Should retrieve all documents quickly
        assert end_time - start_time < 0.5


class TestEdgeCases(TestFixture):
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.edge_case
    def test_empty_document_operations(self):
        """Test operations on empty documents."""
        manager = DocumentManager()
        doc_id = manager.create_document("")  # Empty content
        
        document = manager.get_document(doc_id)
        assert document['content'] == ""
        assert document['is_modified'] is False
        
        # Test updating empty document
        manager.update_document(doc_id, is_modified=True)
        assert document['is_modified'] is True
    
    @pytest.mark.edge_case
    def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        unicode_content = "Test with unicode: ñáéíóú 中文 🚀 математика"
        
        manager = DocumentManager()
        doc_id = manager.create_document(unicode_content)
        
        document = manager.get_document(doc_id)
        assert document['content'] == unicode_content
    
    @pytest.mark.edge_case
    def test_very_long_file_paths(self):
        """Test handling of very long file paths."""
        long_path = "/very/long/path/" + "a" * 200 + "/test.py"
        
        manager = DocumentManager()
        doc_id = manager.create_document("content", long_path)
        
        document = manager.get_document(doc_id)
        assert document['file_path'] == long_path
        # Should still detect Python type despite long path
        assert document['document_type'] == DocumentType.PYTHON
    
    @pytest.mark.edge_case
    def test_special_characters_in_search(self):
        """Test search with special regex characters."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            mock_editor = Mock(spec=TextEditor)
            mock_cursor = Mock()
            mock_cursor.position.return_value = 0
            mock_editor.textCursor.return_value = mock_cursor
            mock_editor.toPlainText.return_value = "Test [special] characters (parens) and $symbols$"
            
            # Test search with special characters
            options = SearchOptions(use_regex=False)
            result = editor.perform_search(mock_editor, "[special]", options)
            
            # Should handle special characters in non-regex mode
            # Result depends on document.find implementation
    
    @pytest.mark.edge_case
    def test_maximum_recent_files(self):
        """Test recent files list maximum limit."""
        manager = DocumentManager()
        
        # Add more than max recent files
        max_files = manager.max_recent_files
        for i in range(max_files + 5):  # Add 5 more than max
            manager.add_to_recent_files(f"file_{i}.txt")
        
        # Should respect maximum
        assert len(manager.recent_files) == max_files
        
        # Most recent files should be at the beginning
        assert manager.recent_files[0] == f"file_{max_files + 4}.txt"
        assert manager.recent_files[-1] == f"file_5.txt"
    
    @pytest.mark.edge_case
    def test_invalid_document_operations(self):
        """Test operations on invalid/non-existent documents."""
        manager = DocumentManager()
        
        # Test getting non-existent document
        result = manager.get_document("non_existent_id")
        assert result is None
        
        # Test updating non-existent document (should not crash)
        manager.update_document("non_existent_id", content="new content")
        # Should not add new document
        assert "non_existent_id" not in manager.documents
        
        # Test removing non-existent document (should not crash)
        manager.remove_document("non_existent_id")
    
    @pytest.mark.edge_case
    def test_file_extension_edge_cases(self):
        """Test document type detection with edge case file extensions."""
        manager = DocumentManager()
        
        test_cases = [
            ("file.PY", DocumentType.PYTHON),  # Uppercase
            ("file.JS", DocumentType.JAVASCRIPT),  # Uppercase
            ("file.html.bak", DocumentType.TEXT),  # Multiple extensions
            ("file", DocumentType.TEXT),  # No extension
            (".hidden", DocumentType.TEXT),  # Hidden file
            ("file.", DocumentType.TEXT),  # Trailing dot
            ("", DocumentType.TEXT),  # Empty string
            (None, DocumentType.TEXT)  # None value
        ]
        
        for file_path, expected_type in test_cases:
            detected_type = manager._detect_document_type(file_path)
            assert detected_type == expected_type, f"Failed for {file_path}"


class TestCompatibility(TestFixture):
    """Test compatibility with different environments and configurations."""
    
    @pytest.mark.compatibility
    def test_settings_persistence(self):
        """Test settings save/load compatibility."""
        # Test with various settings combinations
        test_settings = [
            EditorSettings(),  # Default settings
            EditorSettings(font_size=8, tab_width=2),  # Minimal values
            EditorSettings(font_size=72, tab_width=16),  # Maximum values
            EditorSettings(font_family="Comic Sans MS", theme="dark"),  # Unusual values
        ]
        
        for settings in test_settings:
            # Settings should be serializable
            assert isinstance(settings.font_family, str)
            assert isinstance(settings.font_size, int)
            assert isinstance(settings.tab_width, int)
            assert isinstance(settings.use_spaces, bool)
    
    @pytest.mark.compatibility
    def test_qt_widget_compatibility(self):
        """Test Qt widget creation and basic functionality."""
        # Test basic widget creation
        editor = TextEditor()
        assert editor is not None
        assert hasattr(editor, 'setPlainText')
        assert hasattr(editor, 'toPlainText')
        
        # Test search dialog creation
        dialog = SearchDialog()
        assert dialog is not None
        assert hasattr(dialog, 'search_edit')
        assert hasattr(dialog, 'replace_edit')
    
    @pytest.mark.compatibility
    def test_encoding_detection_fallback(self):
        """Test encoding detection with various scenarios."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch.object(EnhancedEditor, 'new_document'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            editor = EnhancedEditor()
            
            # Test with chardet available
            with patch('chardet.detect') as mock_detect:
                mock_detect.return_value = {'encoding': 'utf-8'}
                with patch('builtins.open', mock_open(read_data=b'test')):
                    encoding = editor.detect_encoding("test.txt")
                    assert encoding == 'utf-8'
            
            # Test with chardet unavailable
            with patch('enhanced_editor.chardet', side_effect=ImportError):
                with patch('builtins.open', mock_open(read_data="test")):
                    encoding = editor.detect_encoding("test.txt")
                    assert encoding in ['utf-8', 'utf-16', 'ascii', 'latin-1']


def generate_test_execution_timestamp():
    """Generate standardized test execution timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_test_summary_report(test_results):
    """Create standardized test summary report."""
    timestamp = generate_test_execution_timestamp()
    
    summary = {
        "execution_timestamp": timestamp,
        "test_file": "test_enhanced_editor_2025-08-31.py",
        "target_module": "enhanced_editor.py",
        "total_tests": test_results.get('total', 0),
        "passed": test_results.get('passed', 0),
        "failed": test_results.get('failed', 0),
        "skipped": test_results.get('skipped', 0),
        "errors": test_results.get('errors', 0),
        "success_rate": f"{(test_results.get('passed', 0) / max(test_results.get('total', 1), 1)) * 100:.2f}%",
        "execution_time": test_results.get('duration', 0),
        "coverage_info": "See HTML report for detailed coverage",
        "test_categories": [
            "DocumentType enumeration tests",
            "SearchOptions dataclass tests", 
            "EditorSettings dataclass tests",
            "SyntaxHighlighter functionality tests",
            "DocumentManager core operations tests",
            "SearchDialog UI component tests",
            "TextEditor widget tests",
            "LineNumberArea widget tests", 
            "EnhancedEditor main class tests",
            "PreferencesDialog tests",
            "Error handling scenarios tests",
            "Integration workflow tests"
        ]
    }
    
    return summary


if __name__ == "__main__":
    # This allows the test file to be run directly
    pytest.main([__file__, "-v", "--tb=short"])