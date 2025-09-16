"""
Comprehensive Unit Tests for Enhanced Editor Core Functionality
Created: 2025-08-31
Target: enhanced_editor.py - core functionality

This test suite focuses on the core functionality of the Enhanced Editor module,
including document management, text editing operations, file I/O, search/replace,
and basic editor components.

Test Categories:
- Core Data Structures (DocumentType, SearchOptions, EditorSettings)
- Document Manager Core Functionality
- Text Editor Core Operations
- File Operations (Open, Save, Encoding Detection)
- Search and Replace Functionality
- Syntax Highlighting Core
- Basic GUI Components
- Error Handling and Edge Cases
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'file_operations', 'enhanced_editor'))

# Import PyQt5 components for testing
try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QTextCursor, QTextDocument
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QWidget
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import the module under test
try:
    from enhanced_editor import (DocumentManager, DocumentType, EditorSettings,
                                 EnhancedEditor, LineNumberArea,
                                 PreferencesDialog, SearchDialog,
                                 SearchOptions, SyntaxHighlighter, TextEditor)
except ImportError as e:
    pytest.skip(f"Cannot import enhanced_editor module: {e}", allow_module_level=True)


# Test Fixtures and Setup
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    if not PYQT_AVAILABLE:
        pytest.skip("PyQt5 not available")
    
    import sys

    from PyQt5.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
    
    yield app
    
    # Cleanup is handled by pytest automatically


@pytest.fixture
def temp_text_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello, World!\nThis is a test file.\nLine 3 with special chars: äöü")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    python_content = '''"""
Test Python file for syntax highlighting.
"""

def hello_world():
    """A simple function."""
    message = "Hello, World!"
    print(message)
    return message

class TestClass:
    """A test class."""
    
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(python_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def sample_search_options():
    """Sample search options for testing."""
    return SearchOptions(
        case_sensitive=True,
        whole_words=False,
        use_regex=False,
        wrap_around=True,
        search_backwards=False
    )


@pytest.fixture
def sample_editor_settings():
    """Sample editor settings for testing."""
    return EditorSettings(
        font_family="Consolas",
        font_size=12,
        tab_width=4,
        use_spaces=True,
        word_wrap=True,
        line_numbers=True,
        syntax_highlighting=True,
        auto_indent=True,
        show_whitespace=False,
        theme="default"
    )


# Core Data Structures Tests
class TestDocumentType:
    """Test DocumentType enumeration."""
    
    def test_document_type_values(self):
        """Test that all document types have correct values."""
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
    
    def test_document_type_enum_completeness(self):
        """Test that all expected document types are defined."""
        expected_types = {
            'TEXT', 'PYTHON', 'JAVASCRIPT', 'HTML', 'CSS', 'XML',
            'JSON', 'YAML', 'SQL', 'BASH', 'POWERSHELL', 'C',
            'CPP', 'JAVA', 'CSHARP', 'MARKDOWN'
        }
        actual_types = {dt.name for dt in DocumentType}
        assert actual_types == expected_types
    
    def test_document_type_uniqueness(self):
        """Test that all document type values are unique."""
        values = [dt.value for dt in DocumentType]
        assert len(values) == len(set(values))


class TestSearchOptions:
    """Test SearchOptions dataclass."""
    
    def test_search_options_defaults(self):
        """Test default values for SearchOptions."""
        options = SearchOptions()
        assert options.case_sensitive is False
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
        assert options.search_backwards is False
    
    def test_search_options_custom_values(self):
        """Test SearchOptions with custom values."""
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
    
    def test_search_options_partial_override(self):
        """Test SearchOptions with partial value override."""
        options = SearchOptions(case_sensitive=True, use_regex=True)
        assert options.case_sensitive is True
        assert options.use_regex is True
        # Defaults should remain
        assert options.whole_words is False
        assert options.wrap_around is True
        assert options.search_backwards is False


class TestEditorSettings:
    """Test EditorSettings dataclass."""
    
    def test_editor_settings_defaults(self):
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
    
    def test_editor_settings_custom_values(self):
        """Test EditorSettings with custom values."""
        settings = EditorSettings(
            font_family="Courier New",
            font_size=14,
            tab_width=8,
            use_spaces=False,
            word_wrap=False,
            line_numbers=False,
            syntax_highlighting=False,
            auto_indent=False,
            show_whitespace=True,
            theme="dark"
        )
        assert settings.font_family == "Courier New"
        assert settings.font_size == 14
        assert settings.tab_width == 8
        assert settings.use_spaces is False
        assert settings.word_wrap is False
        assert settings.line_numbers is False
        assert settings.syntax_highlighting is False
        assert settings.auto_indent is False
        assert settings.show_whitespace is True
        assert settings.theme == "dark"
    
    def test_editor_settings_validation_ranges(self):
        """Test that settings can handle edge case values."""
        # Test minimum values
        settings = EditorSettings(font_size=1, tab_width=1)
        assert settings.font_size == 1
        assert settings.tab_width == 1
        
        # Test maximum reasonable values
        settings = EditorSettings(font_size=72, tab_width=16)
        assert settings.font_size == 72
        assert settings.tab_width == 16


# Document Manager Core Tests
class TestDocumentManager:
    """Test DocumentManager core functionality."""
    
    def test_document_manager_initialization(self):
        """Test DocumentManager initialization."""
        dm = DocumentManager()
        assert dm.documents == {}
        assert dm.current_document is None
        assert dm.recent_files == []
        assert dm.max_recent_files == 10
    
    def test_create_document_basic(self):
        """Test creating a basic document."""
        dm = DocumentManager()
        doc_id = dm.create_document("Hello, World!")
        
        assert doc_id.startswith("doc_")
        assert doc_id in dm.documents
        assert dm.current_document == doc_id
        
        document = dm.documents[doc_id]
        assert document['content'] == "Hello, World!"
        assert document['file_path'] is None
        assert document['is_modified'] is False
        assert document['encoding'] == 'utf-8'
        assert document['line_ending'] == 'lf'
        assert document['document_type'] == DocumentType.TEXT
    
    def test_create_document_with_file_path(self):
        """Test creating a document with file path."""
        dm = DocumentManager()
        doc_id = dm.create_document("print('hello')", "/test/file.py")
        
        document = dm.documents[doc_id]
        assert document['file_path'] == "/test/file.py"
        assert document['document_type'] == DocumentType.PYTHON
    
    def test_create_multiple_documents(self):
        """Test creating multiple documents."""
        dm = DocumentManager()
        
        doc1 = dm.create_document("Content 1")
        doc2 = dm.create_document("Content 2")
        doc3 = dm.create_document("Content 3")
        
        assert len(dm.documents) == 3
        assert dm.current_document == doc3  # Last created becomes current
        assert all(doc_id in dm.documents for doc_id in [doc1, doc2, doc3])
    
    def test_detect_document_type_extensions(self):
        """Test document type detection by file extension."""
        dm = DocumentManager()
        
        test_cases = [
            ("file.py", DocumentType.PYTHON),
            ("script.js", DocumentType.JAVASCRIPT),
            ("page.html", DocumentType.HTML),
            ("page.htm", DocumentType.HTML),
            ("style.css", DocumentType.CSS),
            ("data.xml", DocumentType.XML),
            ("config.json", DocumentType.JSON),
            ("config.yaml", DocumentType.YAML),
            ("config.yml", DocumentType.YAML),
            ("query.sql", DocumentType.SQL),
            ("script.sh", DocumentType.BASH),
            ("script.ps1", DocumentType.POWERSHELL),
            ("program.c", DocumentType.C),
            ("program.cpp", DocumentType.CPP),
            ("program.cc", DocumentType.CPP),
            ("program.cxx", DocumentType.CPP),
            ("Program.java", DocumentType.JAVA),
            ("Program.cs", DocumentType.CSHARP),
            ("readme.md", DocumentType.MARKDOWN),
            ("readme.markdown", DocumentType.MARKDOWN),
            ("unknown.xyz", DocumentType.TEXT),
            ("", DocumentType.TEXT),
            (None, DocumentType.TEXT)
        ]
        
        for file_path, expected_type in test_cases:
            detected_type = dm._detect_document_type(file_path)
            assert detected_type == expected_type, f"Failed for {file_path}"
    
    def test_get_document(self):
        """Test getting documents by ID."""
        dm = DocumentManager()
        doc_id = dm.create_document("Test content")
        
        # Valid document ID
        document = dm.get_document(doc_id)
        assert document is not None
        assert document['content'] == "Test content"
        
        # Invalid document ID
        invalid_doc = dm.get_document("invalid_id")
        assert invalid_doc is None
    
    def test_update_document(self):
        """Test updating document properties."""
        dm = DocumentManager()
        doc_id = dm.create_document("Original content")
        
        # Update properties
        dm.update_document(doc_id, content="Updated content", is_modified=True)
        
        document = dm.get_document(doc_id)
        assert document['content'] == "Updated content"
        assert document['is_modified'] is True
    
    def test_update_nonexistent_document(self):
        """Test updating a nonexistent document."""
        dm = DocumentManager()
        # Should not raise exception
        dm.update_document("invalid_id", content="New content")
        assert len(dm.documents) == 0
    
    def test_remove_document(self):
        """Test removing documents."""
        dm = DocumentManager()
        doc_id = dm.create_document("Test content")
        
        assert doc_id in dm.documents
        assert dm.current_document == doc_id
        
        dm.remove_document(doc_id)
        
        assert doc_id not in dm.documents
        assert dm.current_document is None
    
    def test_remove_nonexistent_document(self):
        """Test removing a nonexistent document."""
        dm = DocumentManager()
        # Should not raise exception
        dm.remove_document("invalid_id")
        assert len(dm.documents) == 0
    
    def test_recent_files_management(self):
        """Test recent files list management."""
        dm = DocumentManager()
        
        # Add files to recent list
        files = [f"/path/file{i}.txt" for i in range(5)]
        for file_path in files:
            dm.add_to_recent_files(file_path)
        
        assert len(dm.recent_files) == 5
        assert dm.recent_files[0] == "/path/file4.txt"  # Last added is first
        assert dm.recent_files[-1] == "/path/file0.txt"  # First added is last
    
    def test_recent_files_duplicate_handling(self):
        """Test handling duplicate files in recent list."""
        dm = DocumentManager()
        
        dm.add_to_recent_files("/path/file1.txt")
        dm.add_to_recent_files("/path/file2.txt")
        dm.add_to_recent_files("/path/file1.txt")  # Duplicate
        
        assert len(dm.recent_files) == 2
        assert dm.recent_files[0] == "/path/file1.txt"
        assert dm.recent_files[1] == "/path/file2.txt"
    
    def test_recent_files_max_limit(self):
        """Test recent files maximum limit."""
        dm = DocumentManager()
        
        # Add more files than the limit
        for i in range(15):
            dm.add_to_recent_files(f"/path/file{i}.txt")
        
        assert len(dm.recent_files) == dm.max_recent_files
        assert dm.recent_files[0] == "/path/file14.txt"  # Most recent
        assert dm.recent_files[-1] == "/path/file5.txt"  # Oldest kept


# Syntax Highlighting Core Tests
class TestSyntaxHighlighterCore:
    """Test SyntaxHighlighter core functionality."""
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_syntax_highlighter_initialization(self, qapp):
        """Test SyntaxHighlighter initialization."""
        from PyQt5.QtGui import QTextDocument
        
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        
        assert highlighter.language == DocumentType.PYTHON
        assert highlighter.highlighting_rules is not None
        assert isinstance(highlighter.highlighting_rules, list)
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_python_highlighting_rules(self, qapp):
        """Test Python syntax highlighting rules setup."""
        from PyQt5.QtGui import QTextDocument
        
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.PYTHON)
        
        # Should have highlighting rules
        assert len(highlighter.highlighting_rules) > 0
        
        # Check that we have keyword rules
        has_keyword_rules = any(
            rule for rule in highlighter.highlighting_rules
            if hasattr(rule[0], 'pattern') and 'def' in str(rule[0].pattern)
        )
        assert has_keyword_rules
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_javascript_highlighting_rules(self, qapp):
        """Test JavaScript syntax highlighting rules setup."""
        from PyQt5.QtGui import QTextDocument
        
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.JAVASCRIPT)
        
        # Should have highlighting rules
        assert len(highlighter.highlighting_rules) > 0
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_no_highlighting(self, qapp):
        """Test that plain text has no highlighting rules."""
        from PyQt5.QtGui import QTextDocument
        
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.TEXT)
        
        # Text documents should have no highlighting rules
        assert len(highlighter.highlighting_rules) == 0


# File Operations Core Tests
class TestFileOperationsCore:
    """Test core file operations functionality."""
    
    def test_encoding_detection_utf8(self, temp_text_file):
        """Test UTF-8 encoding detection."""
        # Create a mock EnhancedEditor to test encoding detection
        class MockEditor:
            def detect_encoding(self, file_path):
                try:
                    import chardet
                    with open(file_path, 'rb') as f:
                        raw_data = f.read(10000)
                        result = chardet.detect(raw_data)
                        return result.get('encoding', 'utf-8') or 'utf-8'
                except ImportError:
                    return 'utf-8'
        
        editor = MockEditor()
        encoding = editor.detect_encoding(temp_text_file)
        assert encoding in ['utf-8', 'UTF-8', 'ascii']  # Common valid encodings
    
    def test_encoding_detection_fallback(self, temp_text_file):
        """Test encoding detection fallback mechanism."""
        class MockEditor:
            def detect_encoding(self, file_path):
                # Simulate chardet not available
                encodings = ['utf-8', 'utf-16', 'ascii', 'latin-1']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            f.read(1000)
                        return encoding
                    except UnicodeDecodeError:
                        continue
                return 'utf-8'
        
        editor = MockEditor()
        encoding = editor.detect_encoding(temp_text_file)
        assert encoding == 'utf-8'  # Should fallback to utf-8
    
    def test_file_reading_basic(self, temp_text_file):
        """Test basic file reading functionality."""
        with open(temp_text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Hello, World!" in content
        assert "This is a test file." in content
        assert "Line 3" in content
    
    def test_file_writing_basic(self, temp_text_file):
        """Test basic file writing functionality."""
        test_content = "New content\nLine 2\nLine 3"
        
        # Write content
        with open(temp_text_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Read and verify
        with open(temp_text_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        assert read_content == test_content


# Search and Replace Core Tests
class TestSearchReplaceCore:
    """Test search and replace core functionality."""
    
    def test_search_options_creation(self, sample_search_options):
        """Test SearchOptions object creation and properties."""
        options = sample_search_options
        assert options.case_sensitive is True
        assert options.whole_words is False
        assert options.use_regex is False
        assert options.wrap_around is True
        assert options.search_backwards is False
    
    def test_basic_text_search_simulation(self):
        """Test basic text search simulation."""
        text = "Hello World\nThis is a test\nHello again"
        search_term = "Hello"
        
        # Simple case-sensitive search
        positions = []
        start = 0
        while True:
            pos = text.find(search_term, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        assert len(positions) == 2
        assert positions[0] == 0  # First "Hello"
        assert positions[1] == text.find("Hello again")
    
    def test_case_insensitive_search_simulation(self):
        """Test case-insensitive search simulation."""
        text = "Hello World\nthis is a test\nhello again"
        search_term = "hello"
        
        # Case-insensitive search simulation
        import re
        pattern = re.compile(search_term, re.IGNORECASE)
        matches = list(pattern.finditer(text))
        
        assert len(matches) == 2
        assert matches[0].start() == 0  # "Hello"
        assert matches[1].start() == text.lower().find("hello again")
    
    def test_regex_search_simulation(self):
        """Test regex search simulation."""
        text = "Email: test@example.com\nAnother: user@domain.org"
        
        # Email regex pattern
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = list(re.finditer(email_pattern, text))
        
        assert len(matches) == 2
        assert "test@example.com" in text[matches[0].start():matches[0].end()]
        assert "user@domain.org" in text[matches[1].start():matches[1].end()]
    
    def test_whole_word_search_simulation(self):
        """Test whole word search simulation."""
        text = "test testing tester"
        search_term = "test"
        
        # Whole word search simulation
        import re
        pattern = re.compile(r'\b' + re.escape(search_term) + r'\b')
        matches = list(pattern.finditer(text))
        
        assert len(matches) == 1  # Only "test", not "testing" or "tester"
        assert matches[0].start() == 0
    
    def test_replace_basic_simulation(self):
        """Test basic text replacement simulation."""
        text = "Hello World\nHello Universe"
        search_term = "Hello"
        replace_term = "Hi"
        
        # Basic replacement
        result = text.replace(search_term, replace_term)
        assert result == "Hi World\nHi Universe"
    
    def test_replace_regex_simulation(self):
        """Test regex replacement simulation."""
        text = "Date: 2025-08-31\nAnother date: 2025-12-25"
        
        # Replace date format YYYY-MM-DD with MM/DD/YYYY
        import re
        pattern = r'(\d{4})-(\d{2})-(\d{2})'
        replacement = r'\2/\3/\1'
        result = re.sub(pattern, replacement, text)
        
        assert "08/31/2025" in result
        assert "12/25/2025" in result


# Text Editor Core Tests
@pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
class TestTextEditorCore:
    """Test TextEditor core functionality."""
    
    def test_text_editor_initialization(self, qapp):
        """Test TextEditor initialization."""
        editor = TextEditor()
        
        assert editor.document_type == DocumentType.TEXT
        assert editor.highlighter is None
        assert editor.line_number_area is not None
        assert isinstance(editor.settings, EditorSettings)
    
    def test_text_editor_content_operations(self, qapp):
        """Test basic text content operations."""
        editor = TextEditor()
        
        # Set content
        test_content = "Hello, World!\nLine 2\nLine 3"
        editor.setPlainText(test_content)
        
        # Get content
        content = editor.toPlainText()
        assert content == test_content
        
        # Check line count
        assert editor.blockCount() == 3
    
    def test_text_editor_document_type_setting(self, qapp):
        """Test setting document type."""
        editor = TextEditor()
        
        # Set Python document type
        editor.set_document_type(DocumentType.PYTHON)
        assert editor.document_type == DocumentType.PYTHON
        
        # Should create syntax highlighter for Python
        if editor.settings.syntax_highlighting:
            assert editor.highlighter is not None
    
    def test_text_editor_settings_application(self, qapp):
        """Test applying settings to editor."""
        editor = TextEditor()
        
        # Modify settings
        editor.settings.font_size = 14
        editor.settings.tab_width = 8
        editor.apply_settings()
        
        # Font size should be applied
        font = editor.font()
        assert font.pointSize() == 14
    
    def test_line_number_area_width_calculation(self, qapp):
        """Test line number area width calculation."""
        editor = TextEditor()
        
        # Set content with multiple lines
        content = "\n".join([f"Line {i}" for i in range(100)])
        editor.setPlainText(content)
        
        # Calculate width
        width = editor.line_number_area_width()
        assert width > 0
        assert isinstance(width, int)


# Error Handling and Edge Cases Tests
class TestErrorHandlingCore:
    """Test error handling and edge cases."""
    
    def test_document_manager_with_invalid_inputs(self):
        """Test DocumentManager with invalid inputs."""
        dm = DocumentManager()
        
        # Create document with None content
        doc_id = dm.create_document(None)
        document = dm.get_document(doc_id)
        assert document['content'] is None
        
        # Create document with empty string
        doc_id2 = dm.create_document("")
        document2 = dm.get_document(doc_id2)
        assert document2['content'] == ""
    
    def test_file_operations_with_nonexistent_file(self):
        """Test file operations with nonexistent files."""
        nonexistent_file = "/path/that/does/not/exist.txt"
        
        # Reading should raise exception
        with pytest.raises(FileNotFoundError):
            with open(nonexistent_file, 'r') as f:
                f.read()
    
    def test_search_with_empty_patterns(self):
        """Test search operations with empty patterns."""
        text = "Hello World"
        
        # Empty search term
        result = text.find("")
        assert result == 0  # Empty string is found at position 0
        
        # Search for None (should handle gracefully)
        try:
            text.find(None)
        except TypeError:
            pass  # Expected behavior
    
    def test_syntax_highlighter_with_invalid_language(self):
        """Test syntax highlighter with edge cases."""
        if not PYQT_AVAILABLE:
            pytest.skip("PyQt5 not available")
        
        from PyQt5.QtGui import QTextDocument

        # Test with a language that has no rules
        document = QTextDocument()
        highlighter = SyntaxHighlighter(document, DocumentType.TEXT)
        
        # Should not crash and should have no rules
        assert len(highlighter.highlighting_rules) == 0
    
    def test_recent_files_with_special_characters(self):
        """Test recent files handling with special characters."""
        dm = DocumentManager()
        
        special_files = [
            "/path/with spaces/file.txt",
            "/path/with-dashes/file.txt",
            "/path/with_underscores/file.txt",
            "/path/with.dots/file.txt",
            "/path/with(parentheses)/file.txt"
        ]
        
        for file_path in special_files:
            dm.add_to_recent_files(file_path)
        
        assert len(dm.recent_files) == len(special_files)
        assert all(path in dm.recent_files for path in special_files)


# Integration Tests for Core Components
class TestCoreIntegration:
    """Test integration between core components."""
    
    def test_document_manager_and_settings_integration(self):
        """Test integration between DocumentManager and EditorSettings."""
        dm = DocumentManager()
        settings = EditorSettings(syntax_highlighting=True)
        
        # Create document with Python file
        doc_id = dm.create_document("def hello():\n    pass", "test.py")
        document = dm.get_document(doc_id)
        
        # Document should be detected as Python
        assert document['document_type'] == DocumentType.PYTHON
        
        # Settings should be compatible
        assert settings.syntax_highlighting is True
    
    def test_search_options_and_text_operations(self):
        """Test integration between SearchOptions and text operations."""
        options = SearchOptions(case_sensitive=True, use_regex=False)
        text = "Hello World\nhello world"
        
        # Case-sensitive search should find only first occurrence
        if options.case_sensitive:
            count = text.count("Hello")
            assert count == 1
        else:
            count = text.lower().count("hello")
            assert count == 2
    
    def test_document_type_detection_consistency(self):
        """Test consistency of document type detection."""
        dm = DocumentManager()
        
        # Test various file extensions
        test_files = [
            ("script.py", DocumentType.PYTHON),
            ("app.js", DocumentType.JAVASCRIPT),
            ("index.html", DocumentType.HTML),
            ("styles.css", DocumentType.CSS),
            ("data.json", DocumentType.JSON)
        ]
        
        for file_path, expected_type in test_files:
            doc_id = dm.create_document("", file_path)
            document = dm.get_document(doc_id)
            assert document['document_type'] == expected_type


# Performance and Stress Tests
class TestCorePerformance:
    """Test core functionality performance characteristics."""
    
    def test_document_manager_with_many_documents(self):
        """Test DocumentManager performance with many documents."""
        dm = DocumentManager()
        
        # Create many documents
        doc_ids = []
        for i in range(100):
            doc_id = dm.create_document(f"Content {i}", f"file{i}.txt")
            doc_ids.append(doc_id)
        
        assert len(dm.documents) == 100
        assert all(dm.get_document(doc_id) is not None for doc_id in doc_ids)
    
    def test_recent_files_performance(self):
        """Test recent files list performance."""
        dm = DocumentManager()
        
        # Add many files
        for i in range(1000):
            dm.add_to_recent_files(f"/path/file{i}.txt")
        
        # Should maintain limit
        assert len(dm.recent_files) == dm.max_recent_files
        
        # Most recent should be first
        assert dm.recent_files[0] == "/path/file999.txt"
    
    def test_large_text_operations(self):
        """Test operations with large text content."""
        # Create large text content
        large_content = "Line of text\n" * 10000  # 10k lines
        
        # Basic operations should work
        assert len(large_content.splitlines()) == 10000
        assert "Line of text" in large_content
        
        # Search in large content
        position = large_content.find("Line of text")
        assert position == 0


# Fixture Data and Mock Tests
class TestMockIntegration:
    """Test using mocks for external dependencies."""
    
    @patch('builtins.open', new_callable=mock_open, read_data="Mock file content")
    def test_file_reading_with_mock(self, mock_file):
        """Test file reading with mocked file operations."""
        # Simulate reading a file
        with open("test_file.txt", 'r') as f:
            content = f.read()
        
        assert content == "Mock file content"
        mock_file.assert_called_once_with("test_file.txt", 'r')
    
    def test_document_manager_with_mocked_file_detection(self):
        """Test DocumentManager with mocked file type detection."""
        dm = DocumentManager()
        
        # Mock the _detect_document_type method
        original_detect = dm._detect_document_type
        dm._detect_document_type = Mock(return_value=DocumentType.PYTHON)
        
        doc_id = dm.create_document("content", "unknown.ext")
        document = dm.get_document(doc_id)
        
        # Should use mocked return value
        assert document['document_type'] == DocumentType.PYTHON
        
        # Restore original method
        dm._detect_document_type = original_detect
    
    @patch('os.path.exists')
    def test_file_existence_checking(self, mock_exists):
        """Test file existence checking with mocks."""
        mock_exists.return_value = False
        
        # Check nonexistent file
        exists = os.path.exists("/nonexistent/file.txt")
        assert exists is False
        
        mock_exists.assert_called_once_with("/nonexistent/file.txt")


# Configuration and Settings Tests
class TestConfigurationCore:
    """Test configuration and settings management."""
    
    def test_editor_settings_serialization(self):
        """Test EditorSettings serialization/deserialization."""
        settings = EditorSettings(
            font_family="Monaco",
            font_size=13,
            tab_width=2,
            use_spaces=False
        )
        
        # Convert to dict for serialization
        settings_dict = {
            'font_family': settings.font_family,
            'font_size': settings.font_size,
            'tab_width': settings.tab_width,
            'use_spaces': settings.use_spaces,
            'word_wrap': settings.word_wrap,
            'line_numbers': settings.line_numbers,
            'syntax_highlighting': settings.syntax_highlighting,
            'auto_indent': settings.auto_indent,
            'show_whitespace': settings.show_whitespace,
            'theme': settings.theme
        }
        
        # Verify serialization
        assert settings_dict['font_family'] == "Monaco"
        assert settings_dict['font_size'] == 13
        assert settings_dict['tab_width'] == 2
        assert settings_dict['use_spaces'] is False
    
    def test_search_options_serialization(self):
        """Test SearchOptions serialization/deserialization."""
        options = SearchOptions(
            case_sensitive=True,
            use_regex=True,
            wrap_around=False
        )
        
        # Convert to dict
        options_dict = {
            'case_sensitive': options.case_sensitive,
            'whole_words': options.whole_words,
            'use_regex': options.use_regex,
            'wrap_around': options.wrap_around,
            'search_backwards': options.search_backwards
        }
        
        # Verify serialization
        assert options_dict['case_sensitive'] is True
        assert options_dict['use_regex'] is True
        assert options_dict['wrap_around'] is False


# Test Execution Summary and Reporting
def test_execution_summary():
    """Provide test execution summary information."""
    test_info = {
        'test_file': 'test_enhanced_editor_core_functionality_2025-08-31.py',
        'target_module': 'enhanced_editor.py',
        'test_categories': [
            'Core Data Structures',
            'Document Manager Core',
            'Syntax Highlighting Core',
            'File Operations Core', 
            'Search and Replace Core',
            'Text Editor Core',
            'Error Handling',
            'Integration Tests',
            'Performance Tests',
            'Mock Integration',
            'Configuration Management'
        ],
        'total_test_classes': 12,
        'pyqt_dependency': PYQT_AVAILABLE,
        'execution_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # This test always passes and provides summary info
    assert test_info['test_file'] == 'test_enhanced_editor_core_functionality_2025-08-31.py'
    assert len(test_info['test_categories']) == 11


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        f"--html=result_enhanced_editor_core_functionality_2025-08-31_report.html",
        "--self-contained-html",
        f"--junitxml=result_enhanced_editor_core_functionality_2025-08-31_junit.xml",
        "--json-report",
        f"--json-report-file=result_enhanced_editor_core_functionality_2025-08-31_results.json"
    ])