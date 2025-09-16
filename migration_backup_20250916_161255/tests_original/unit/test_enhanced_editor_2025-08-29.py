"""
Comprehensive Unit Tests for Enhanced Editor

Test module for src.utilities.file_operations.enhanced_editor.enhanced_editor
Created: 2025-08-29
Framework: pytest

This module provides comprehensive testing coverage for the EnhancedEditor
application including all classes, methods, and edge cases.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QTextCursor, QTextDocument
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QWidget

    # Import the modules to test
    from src.utilities.file_operations.enhanced_editor.enhanced_editor import (
        DocumentManager, DocumentType, EditorSettings, EnhancedEditor,
        LineNumberArea, PreferencesDialog, SearchDialog, SearchOptions,
        SyntaxHighlighter, TextEditor)
    
    QT_AVAILABLE = True
except ImportError as e:
    QT_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)


class TestDocumentType:
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
        actual_count = len(list(DocumentType))
        assert actual_count == expected_count


class TestSearchOptions:
    """Test SearchOptions dataclass."""
    
    def test_default_values(self):
        """Test default values for SearchOptions."""
        options = SearchOptions()
        assert options.case_sensitive is False
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
        assert options.search_backwards is False
    
    def test_custom_values(self):
        """Test custom values for SearchOptions."""
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


class TestEditorSettings:
    """Test EditorSettings dataclass."""
    
    def test_default_values(self):
        """Test default values for EditorSettings."""
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
    
    def test_custom_values(self):
        """Test custom values for EditorSettings."""
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


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestSyntaxHighlighter:
    """Test SyntaxHighlighter class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def document(self, app):
        """Create QTextDocument instance."""
        return QTextDocument()
    
    def test_python_highlighter_creation(self, document):
        """Test creation of Python syntax highlighter."""
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        assert highlighter.language == DocumentType.PYTHON
        assert len(highlighter.highlighting_rules) > 0
    
    def test_javascript_highlighter_creation(self, document):
        """Test creation of JavaScript syntax highlighter."""
        highlighter = SyntaxHighlighter(document, DocumentType.JAVASCRIPT)
        assert highlighter.language == DocumentType.JAVASCRIPT
        assert len(highlighter.highlighting_rules) > 0
    
    def test_text_highlighter_creation(self, document):
        """Test creation of plain text highlighter."""
        highlighter = SyntaxHighlighter(document, DocumentType.TEXT)
        assert highlighter.language == DocumentType.TEXT
        # Text highlighter should have no rules by default
        assert len(highlighter.highlighting_rules) == 0
    
    def test_highlighting_rules_setup(self, document):
        """Test that highlighting rules are properly set up."""
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        # Should have rules for keywords, strings, and comments
        assert len(highlighter.highlighting_rules) >= 3


class TestDocumentManager:
    """Test DocumentManager class."""
    
    @pytest.fixture
    def doc_manager(self):
        """Create DocumentManager instance."""
        return DocumentManager()
    
    def test_initialization(self, doc_manager):
        """Test DocumentManager initialization."""
        assert doc_manager.documents == {}
        assert doc_manager.current_document is None
        assert doc_manager.recent_files == []
        assert doc_manager.max_recent_files == 10
    
    def test_create_document_default(self, doc_manager):
        """Test creating a document with default parameters."""
        doc_id = doc_manager.create_document()
        assert doc_id in doc_manager.documents
        assert doc_manager.current_document == doc_id
        
        document = doc_manager.documents[doc_id]
        assert document['content'] == ""
        assert document['file_path'] is None
        assert document['is_modified'] is False
        assert document['encoding'] == 'utf-8'
        assert document['line_ending'] == 'lf'
        assert document['document_type'] == DocumentType.TEXT
    
    def test_create_document_with_content(self, doc_manager):
        """Test creating a document with content."""
        content = "print('Hello, World!')"
        doc_id = doc_manager.create_document(content=content)
        
        document = doc_manager.documents[doc_id]
        assert document['content'] == content
    
    def test_create_document_with_file_path(self, doc_manager):
        """Test creating a document with file path."""
        file_path = "test.py"
        doc_id = doc_manager.create_document(file_path=file_path)
        
        document = doc_manager.documents[doc_id]
        assert document['file_path'] == file_path
        assert document['document_type'] == DocumentType.PYTHON
    
    def test_detect_document_type_python(self, doc_manager):
        """Test document type detection for Python files."""
        doc_type = doc_manager._detect_document_type("test.py")
        assert doc_type == DocumentType.PYTHON
    
    def test_detect_document_type_javascript(self, doc_manager):
        """Test document type detection for JavaScript files."""
        doc_type = doc_manager._detect_document_type("test.js")
        assert doc_type == DocumentType.JAVASCRIPT
    
    def test_detect_document_type_html(self, doc_manager):
        """Test document type detection for HTML files."""
        doc_type = doc_manager._detect_document_type("test.html")
        assert doc_type == DocumentType.HTML
        
        doc_type = doc_manager._detect_document_type("test.htm")
        assert doc_type == DocumentType.HTML
    
    def test_detect_document_type_unknown(self, doc_manager):
        """Test document type detection for unknown files."""
        doc_type = doc_manager._detect_document_type("test.unknown")
        assert doc_type == DocumentType.TEXT
        
        doc_type = doc_manager._detect_document_type(None)
        assert doc_type == DocumentType.TEXT
    
    def test_get_document(self, doc_manager):
        """Test getting a document by ID."""
        doc_id = doc_manager.create_document("test content")
        document = doc_manager.get_document(doc_id)
        assert document is not None
        assert document['content'] == "test content"
        
        # Test non-existent document
        assert doc_manager.get_document("non_existent") is None
    
    def test_update_document(self, doc_manager):
        """Test updating document properties."""
        doc_id = doc_manager.create_document()
        doc_manager.update_document(doc_id, is_modified=True, encoding='utf-16')
        
        document = doc_manager.get_document(doc_id)
        assert document['is_modified'] is True
        assert document['encoding'] == 'utf-16'
    
    def test_remove_document(self, doc_manager):
        """Test removing a document."""
        doc_id = doc_manager.create_document()
        assert doc_id in doc_manager.documents
        
        doc_manager.remove_document(doc_id)
        assert doc_id not in doc_manager.documents
        assert doc_manager.current_document is None
    
    def test_add_to_recent_files(self, doc_manager):
        """Test adding files to recent files list."""
        file1 = "file1.py"
        file2 = "file2.js"
        
        doc_manager.add_to_recent_files(file1)
        assert file1 in doc_manager.recent_files
        assert doc_manager.recent_files[0] == file1
        
        doc_manager.add_to_recent_files(file2)
        assert file2 == doc_manager.recent_files[0]
        assert file1 == doc_manager.recent_files[1]
        
        # Test adding duplicate - should move to front
        doc_manager.add_to_recent_files(file1)
        assert file1 == doc_manager.recent_files[0]
        assert file2 == doc_manager.recent_files[1]
    
    def test_recent_files_limit(self, doc_manager):
        """Test recent files list respects maximum limit."""
        # Add more files than the limit
        for i in range(15):
            doc_manager.add_to_recent_files(f"file{i}.txt")
        
        assert len(doc_manager.recent_files) == doc_manager.max_recent_files
        assert doc_manager.recent_files[0] == "file14.txt"
        assert "file0.txt" not in doc_manager.recent_files


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestSearchDialog:
    """Test SearchDialog class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def search_dialog(self, app):
        """Create SearchDialog instance."""
        return SearchDialog()
    
    def test_dialog_initialization(self, search_dialog):
        """Test SearchDialog initialization."""
        assert search_dialog.windowTitle() == "Find and Replace"
        assert not search_dialog.isModal()
        assert search_dialog.search_edit is not None
        assert search_dialog.replace_edit is not None
        assert search_dialog.case_sensitive_cb is not None
        assert search_dialog.whole_words_cb is not None
        assert search_dialog.use_regex_cb is not None
        assert search_dialog.wrap_around_cb is not None
    
    def test_default_options(self, search_dialog):
        """Test default search options."""
        options = search_dialog.get_search_options()
        assert options.case_sensitive is False
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
    
    def test_custom_options(self, search_dialog):
        """Test custom search options."""
        search_dialog.case_sensitive_cb.setChecked(True)
        search_dialog.whole_words_cb.setChecked(True)
        search_dialog.use_regex_cb.setChecked(True)
        search_dialog.wrap_around_cb.setChecked(False)
        
        options = search_dialog.get_search_options()
        assert options.case_sensitive is True
        assert options.whole_words is True
        assert options.use_regex is True
        assert options.wrap_around is False


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestTextEditor:
    """Test TextEditor class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def text_editor(self, app):
        """Create TextEditor instance."""
        return TextEditor()
    
    def test_editor_initialization(self, text_editor):
        """Test TextEditor initialization."""
        assert text_editor.document_type == DocumentType.TEXT
        assert text_editor.highlighter is None
        assert text_editor.line_number_area is not None
        assert isinstance(text_editor.settings, EditorSettings)
    
    def test_set_document_type(self, text_editor):
        """Test setting document type."""
        text_editor.set_document_type(DocumentType.PYTHON)
        assert text_editor.document_type == DocumentType.PYTHON
        assert text_editor.highlighter is not None
    
    def test_line_number_area_width(self, text_editor):
        """Test line number area width calculation."""
        width = text_editor.line_number_area_width()
        assert width > 0
        assert isinstance(width, int)
    
    def test_emit_cursor_position(self, text_editor):
        """Test cursor position emission."""
        # Mock the signal to capture emissions
        with patch.object(text_editor, 'cursor_position_changed') as mock_signal:
            text_editor.emit_cursor_position()
            mock_signal.emit.assert_called_once()


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestLineNumberArea:
    """Test LineNumberArea class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def text_editor(self, app):
        """Create TextEditor instance."""
        return TextEditor()
    
    @pytest.fixture
    def line_number_area(self, text_editor):
        """Create LineNumberArea instance."""
        return LineNumberArea(text_editor)
    
    def test_line_number_area_initialization(self, line_number_area, text_editor):
        """Test LineNumberArea initialization."""
        assert line_number_area.editor == text_editor
    
    def test_size_hint(self, line_number_area):
        """Test size hint calculation."""
        size_hint = line_number_area.sizeHint()
        assert size_hint.width() > 0
        assert size_hint.height() == 0


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestEnhancedEditor:
    """Test EnhancedEditor main class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def editor(self, app):
        """Create EnhancedEditor instance."""
        with patch('src.utilities.file_operations.enhanced_editor.enhanced_editor.StandardWindow'):
            return EnhancedEditor()
    
    def test_editor_initialization(self, editor):
        """Test EnhancedEditor initialization."""
        assert editor.document_manager is not None
        assert isinstance(editor.document_manager, DocumentManager)
        assert editor.search_dialog is None
        assert isinstance(editor.settings, EditorSettings)
        assert editor.tab_to_doc_mapping == {}
    
    def test_new_document(self, editor):
        """Test creating a new document."""
        doc_id = editor.new_document("print('test')", "test.py")
        assert doc_id is not None
        assert doc_id in editor.document_manager.documents
        assert editor.tab_widget.count() == 1
        
        # Check if tab is created correctly
        current_tab = editor.tab_widget.currentWidget()
        assert isinstance(current_tab, TextEditor)
    
    def test_get_current_editor(self, editor):
        """Test getting current editor."""
        # Initially no editor
        current_editor = editor.get_current_editor()
        assert current_editor is None
        
        # Create a document
        editor.new_document()
        current_editor = editor.get_current_editor()
        assert isinstance(current_editor, TextEditor)
    
    @patch('builtins.open', new_callable=mock_open, read_data="print('Hello')")
    @patch('os.path.exists', return_value=True)
    def test_open_document(self, mock_exists, mock_file, editor):
        """Test opening a document from file."""
        with patch.object(editor, 'detect_encoding', return_value='utf-8'):
            doc_id = editor.open_document("test.py")
            assert doc_id is not None
            assert doc_id in editor.document_manager.documents
            
            document = editor.document_manager.get_document(doc_id)
            assert document['file_path'] == "test.py"
    
    def test_detect_encoding_fallback(self, editor):
        """Test encoding detection fallback."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            encoding = editor.detect_encoding(temp_file)
            assert encoding in ['utf-8', 'ascii']  # Should detect one of these
        finally:
            os.unlink(temp_file)
    
    def test_save_document_new_file(self, editor):
        """Test saving a new document."""
        doc_id = editor.new_document("test content")
        
        # Mock save dialog to return a file path
        with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("test.txt", "")
            with patch('builtins.open', mock_open()) as mock_file:
                result = editor.save_document_as(doc_id)
                assert result is True
                mock_file.assert_called_once()
    
    def test_mark_document_modified(self, editor):
        """Test marking document as modified."""
        doc_id = editor.new_document()
        editor.mark_document_modified(doc_id)
        
        document = editor.document_manager.get_document(doc_id)
        assert document['is_modified'] is True
    
    def test_tab_to_doc_mapping(self, editor):
        """Test tab to document mapping."""
        doc_id1 = editor.new_document()
        doc_id2 = editor.new_document()
        
        assert len(editor.tab_to_doc_mapping) == 2
        assert 0 in editor.tab_to_doc_mapping
        assert 1 in editor.tab_to_doc_mapping
    
    def test_close_document_tab(self, editor):
        """Test closing a document tab."""
        doc_id = editor.new_document()
        initial_count = editor.tab_widget.count()
        
        # Close the tab
        editor.close_document_tab(0)
        
        assert editor.tab_widget.count() == initial_count - 1
        assert doc_id not in editor.document_manager.documents
    
    def test_search_operations(self, editor):
        """Test search operations."""
        # Create document with content
        editor.new_document("Hello World\nThis is a test\nHello again")
        
        # Create search dialog
        editor.show_search_dialog()
        assert editor.search_dialog is not None
        
        # Set search text
        editor.search_dialog.search_edit.setText("Hello")
        
        # Perform search
        current_editor = editor.get_current_editor()
        options = SearchOptions(case_sensitive=False)
        result = editor.perform_search(current_editor, "Hello", options)
        assert result is True
    
    def test_edit_operations(self, editor):
        """Test basic edit operations."""
        editor.new_document("test content")
        current_editor = editor.get_current_editor()
        
        # Test operations don't raise exceptions
        editor.undo()
        editor.redo()
        editor.cut()
        editor.copy()
        editor.paste()
        editor.select_all()
    
    def test_zoom_operations(self, editor):
        """Test zoom operations."""
        initial_size = editor.settings.font_size
        
        editor.zoom_in()
        assert editor.settings.font_size == initial_size + 1
        
        editor.zoom_out()
        assert editor.settings.font_size == initial_size
        
        editor.zoom_reset()
        assert editor.settings.font_size == 11
    
    def test_update_status_bar(self, editor):
        """Test status bar updates."""
        # Should not raise exceptions
        editor.update_status_bar()
        
        # Create a document and test again
        editor.new_document()
        editor.update_status_bar()
    
    @patch('PyQt5.QtCore.QSettings')
    def test_load_settings(self, mock_settings, editor):
        """Test loading settings."""
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_settings_instance.value.side_effect = lambda key, default=None, type=None: {
            'font_family': 'Arial',
            'font_size': 12,
            'recent_files': ['file1.py', 'file2.js']
        }.get(key, default)
        
        editor.load_settings()
        assert editor.settings.font_family == 'Arial'
        assert editor.settings.font_size == 12
    
    @patch('PyQt5.QtCore.QSettings')
    def test_save_settings(self, mock_settings, editor):
        """Test saving settings."""
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        
        editor.save_settings()
        mock_settings_instance.setValue.assert_called()


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestPreferencesDialog:
    """Test PreferencesDialog class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        if QApplication.instance() is None:
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def preferences_dialog(self, app):
        """Create PreferencesDialog instance."""
        settings = EditorSettings()
        return PreferencesDialog(settings=settings)
    
    def test_dialog_initialization(self, preferences_dialog):
        """Test PreferencesDialog initialization."""
        assert preferences_dialog.windowTitle() == "Enhanced Editor Preferences"
        assert preferences_dialog.isModal()
        assert preferences_dialog.settings is not None
    
    def test_load_settings(self, preferences_dialog):
        """Test loading settings into dialog."""
        # Settings should be loaded automatically on initialization
        assert preferences_dialog.font_family_combo.currentText() != ""
        assert preferences_dialog.font_size_spin.value() > 0
    
    def test_get_settings(self, preferences_dialog):
        """Test getting settings from dialog."""
        # Modify some settings
        preferences_dialog.font_size_spin.setValue(14)
        preferences_dialog.use_spaces_check.setChecked(False)
        
        settings = preferences_dialog.get_settings()
        assert settings.font_size == 14
        assert settings.use_spaces is False


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_document_manager_edge_cases(self):
        """Test DocumentManager edge cases."""
        doc_manager = DocumentManager()
        
        # Test updating non-existent document
        doc_manager.update_document("non_existent", is_modified=True)
        # Should not raise exception
        
        # Test removing non-existent document
        doc_manager.remove_document("non_existent")
        # Should not raise exception
        
        # Test empty file path detection
        doc_type = doc_manager._detect_document_type("")
        assert doc_type == DocumentType.TEXT
    
    def test_search_options_edge_cases(self):
        """Test SearchOptions edge cases."""
        # Test with all boolean combinations
        for case_sensitive in [True, False]:
            for whole_words in [True, False]:
                for use_regex in [True, False]:
                    for wrap_around in [True, False]:
                        for search_backwards in [True, False]:
                            options = SearchOptions(
                                case_sensitive=case_sensitive,
                                whole_words=whole_words,
                                use_regex=use_regex,
                                wrap_around=wrap_around,
                                search_backwards=search_backwards
                            )
                            assert isinstance(options.case_sensitive, bool)
                            assert isinstance(options.whole_words, bool)
                            assert isinstance(options.use_regex, bool)
                            assert isinstance(options.wrap_around, bool)
                            assert isinstance(options.search_backwards, bool)
    
    def test_editor_settings_edge_cases(self):
        """Test EditorSettings edge cases."""
        # Test with extreme values
        settings = EditorSettings(
            font_size=1,  # Very small
            tab_width=100,  # Very large
            font_family="",  # Empty string
        )
        assert settings.font_size == 1
        assert settings.tab_width == 100
        assert settings.font_family == ""


class TestPerformance:
    """Test performance-related scenarios."""
    
    def test_large_document_handling(self):
        """Test handling of large documents."""
        doc_manager = DocumentManager()
        
        # Create a large document
        large_content = ("Line {}\n".format(i) for i in range(10000))
        large_content = "".join(large_content)
        
        doc_id = doc_manager.create_document(content=large_content)
        document = doc_manager.get_document(doc_id)
        
        assert document['content'] == large_content
        assert len(document['content']) > 50000  # Should be substantial
    
    def test_many_documents(self):
        """Test handling many documents."""
        doc_manager = DocumentManager()
        
        # Create many documents
        doc_ids = []
        for i in range(100):
            doc_id = doc_manager.create_document(f"Document {i}")
            doc_ids.append(doc_id)
        
        assert len(doc_manager.documents) == 100
        
        # Test accessing each document
        for doc_id in doc_ids:
            document = doc_manager.get_document(doc_id)
            assert document is not None
    
    def test_recent_files_performance(self):
        """Test recent files list performance."""
        doc_manager = DocumentManager()
        
        # Add many files to recent list
        for i in range(1000):
            doc_manager.add_to_recent_files(f"file{i}.txt")
        
        # Should still respect the limit
        assert len(doc_manager.recent_files) == doc_manager.max_recent_files


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])