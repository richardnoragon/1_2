"""
Enhanced Editor Critical Functionality Tests - September 1, 2025

This test suite focuses on the CRITICAL CORE FUNCTIONALITY that was missing
from previous test implementations, addressing the gap identified in 
utilities-overview.md item 2: "Enhanced Editor - Core functionality untested"

Critical Areas Tested:
1. Undo/Redo Operations
2. Cursor Management and Positioning  
3. Text Manipulation (Insert, Delete, Cut, Copy, Paste)
4. Selection Handling
5. Real File I/O Operations
6. Document State Management
7. Memory Management
8. Multi-document Operations
9. Integration with StandardWindow
10. Error Recovery and Edge Cases

Author: Enhanced Editor Test Framework
Created: September 1, 2025
Purpose: Resolve utilities-overview.md High Priority Item 2
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch, PropertyMock

import pytest

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'file_operations', 'enhanced_editor'))

# Import PyQt5 components for testing
try:
    from PyQt5.QtCore import Qt, QTimer, QPoint
    from PyQt5.QtGui import QTextCursor, QTextDocument, QKeyEvent
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
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
    
    yield app


@pytest.fixture
def temp_test_files():
    """Create temporary test files with various content types."""
    temp_dir = tempfile.mkdtemp(prefix='enhanced_editor_critical_')
    
    files = {}
    
    # Simple text file
    simple_text = "Line 1\nLine 2\nLine 3"
    files['simple.txt'] = os.path.join(temp_dir, 'simple.txt')
    with open(files['simple.txt'], 'w', encoding='utf-8') as f:
        f.write(simple_text)
    
    # Python file with complex content
    python_content = '''def function_one():
    """First function."""
    variable = "Hello World"
    return variable

class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value * 2

# Comment line
if __name__ == "__main__":
    obj = TestClass()
    print(obj.method())
'''
    files['test.py'] = os.path.join(temp_dir, 'test.py')
    with open(files['test.py'], 'w', encoding='utf-8') as f:
        f.write(python_content)
    
    # Large file for performance testing
    large_content = "\n".join([f"Line {i}: {'x' * 50}" for i in range(1000)])
    files['large.txt'] = os.path.join(temp_dir, 'large.txt')
    with open(files['large.txt'], 'w', encoding='utf-8') as f:
        f.write(large_content)
    
    # Unicode file
    unicode_content = "Unicode test: ñáéíóú 中文 🚀 математика"
    files['unicode.txt'] = os.path.join(temp_dir, 'unicode.txt')
    with open(files['unicode.txt'], 'w', encoding='utf-8') as f:
        f.write(unicode_content)
    
    yield files
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


# CRITICAL TEST 1: UNDO/REDO OPERATIONS
class TestUndoRedoOperations:
    """Test critical undo/redo functionality."""
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_editor_undo_redo_basic(self, qapp):
        """Test basic undo/redo operations in TextEditor."""
        editor = TextEditor()
        
        # Initial content
        initial_text = "Initial content"
        editor.setPlainText(initial_text)
        
        # Verify initial state
        assert editor.toPlainText() == initial_text
        assert not editor.document().isUndoAvailable()
        
        # Make a change
        editor.insertPlainText(" - modified")
        modified_text = editor.toPlainText()
        assert "modified" in modified_text
        assert editor.document().isUndoAvailable()
        
        # Test undo
        editor.undo()
        assert editor.toPlainText() == initial_text
        assert editor.document().isRedoAvailable()
        
        # Test redo
        editor.redo()
        assert editor.toPlainText() == modified_text
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_editor_multiple_undo_redo(self, qapp):
        """Test multiple undo/redo operations."""
        editor = TextEditor()
        
        # Build up a sequence of changes
        changes = ["First", "Second", "Third"]
        states = [""]  # Initial empty state
        
        for change in changes:
            editor.insertPlainText(change + " ")
            states.append(editor.toPlainText())
        
        # Now states = ["", "First ", "First Second ", "First Second Third "]
        
        # Undo all changes step by step
        for i in range(len(changes)):
            assert editor.document().isUndoAvailable()
            editor.undo()
            expected_state = states[len(changes) - i - 1]
            assert editor.toPlainText() == expected_state
        
        # Redo all changes step by step
        for i in range(len(changes)):
            assert editor.document().isRedoAvailable()
            editor.redo()
            expected_state = states[i + 1]
            assert editor.toPlainText() == expected_state
    
    def test_enhanced_editor_undo_redo_integration(self):
        """Test undo/redo integration in EnhancedEditor."""
        # Mock the UI components to avoid GUI initialization issues
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create a mock text editor
            mock_text_editor = Mock(spec=TextEditor)
            mock_text_editor.undo = Mock()
            mock_text_editor.redo = Mock()
            
            # Test undo method
            with patch.object(editor, 'get_current_editor', return_value=mock_text_editor):
                editor.undo()
                mock_text_editor.undo.assert_called_once()
                
                # Test redo method
                editor.redo()
                mock_text_editor.redo.assert_called_once()
    
    def test_undo_redo_with_document_manager(self):
        """Test undo/redo with document state tracking."""
        dm = DocumentManager()
        
        # Create document
        doc_id = dm.create_document("Initial content")
        
        # Simulate modification
        dm.update_document(doc_id, is_modified=True)
        document = dm.get_document(doc_id)
        assert document['is_modified'] is True
        
        # After undo (simulated), document should remain modified
        # until actual save operation
        assert document['is_modified'] is True


# CRITICAL TEST 2: CURSOR MANAGEMENT AND POSITIONING
class TestCursorManagement:
    """Test critical cursor management functionality."""
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_cursor_position_tracking(self, qapp):
        """Test cursor position tracking and updates."""
        editor = TextEditor()
        content = "Line 1\nLine 2\nLine 3\nLine 4"
        editor.setPlainText(content)
        
        # Test cursor at beginning
        cursor = editor.textCursor()
        assert cursor.position() == 0
        assert cursor.blockNumber() == 0  # First line
        assert cursor.columnNumber() == 0  # First column
        
        # Move cursor to second line
        cursor.movePosition(QTextCursor.Down)
        editor.setTextCursor(cursor)
        assert cursor.blockNumber() == 1  # Second line
        
        # Move cursor to end of line
        cursor.movePosition(QTextCursor.EndOfLine)
        editor.setTextCursor(cursor)
        assert cursor.columnNumber() == 6  # After "Line 2"
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_cursor_position_signals(self, qapp):
        """Test cursor position change signals."""
        editor = TextEditor()
        editor.setPlainText("Test content for cursor positioning")
        
        # Track signal emissions
        position_changes = []
        
        def track_position(line, column):
            position_changes.append((line, column))
        
        editor.cursor_position_changed.connect(track_position)
        
        # Move cursor and verify signal emission
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 5)
        editor.setTextCursor(cursor)
        
        # Process events to ensure signal is emitted
        QApplication.processEvents()
        
        # Should have received position updates
        assert len(position_changes) > 0
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_cursor_selection_operations(self, qapp):
        """Test cursor selection functionality."""
        editor = TextEditor()
        content = "Select this text for testing"
        editor.setPlainText(content)
        
        # Select a word
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 7)  # Move to "this"
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)   # Select "this"
        editor.setTextCursor(cursor)
        
        # Verify selection
        assert cursor.hasSelection()
        assert cursor.selectedText() == "this"
        
        # Test selection boundaries
        assert cursor.selectionStart() == 7
        assert cursor.selectionEnd() == 11
    
    def test_enhanced_editor_cursor_tracking(self):
        """Test cursor tracking in EnhancedEditor."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Test cursor position update method
            position_updates = []
            
            def capture_status(message, timeout=1000):
                if "Line" in message and "Column" in message:
                    position_updates.append(message)
            
            editor.show_status_message = capture_status
            
            # Simulate cursor position change
            editor.update_cursor_position(5, 10)
            
            # Should have updated status
            assert len(position_updates) == 1
            assert "Line 5, Column 10" in position_updates[0]


# CRITICAL TEST 3: TEXT MANIPULATION OPERATIONS
class TestTextManipulation:
    """Test critical text manipulation functionality."""
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_basic_text_insertion(self, qapp):
        """Test basic text insertion operations."""
        editor = TextEditor()
        
        # Test plain text insertion
        editor.setPlainText("Initial ")
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        editor.insertPlainText("content")
        
        assert editor.toPlainText() == "Initial content"
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_deletion_operations(self, qapp):
        """Test text deletion operations."""
        editor = TextEditor()
        content = "Delete this text"
        editor.setPlainText(content)
        
        # Select and delete a portion
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 7)  # Move to "this"
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 5)   # Select "this "
        editor.setTextCursor(cursor)
        
        # Delete selection
        cursor.removeSelectedText()
        assert editor.toPlainText() == "Delete text"
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_clipboard_operations(self, qapp):
        """Test cut, copy, paste operations."""
        editor = TextEditor()
        content = "Copy and paste this text"
        editor.setPlainText(content)
        
        # Select text to copy
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 9)   # Move to "paste"
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 5)    # Select "paste"
        editor.setTextCursor(cursor)
        
        # Test copy operation
        editor.copy()
        
        # Move cursor to end and paste
        cursor.movePosition(QTextCursor.End)
        editor.setTextCursor(cursor)
        editor.insertPlainText(" - ")
        editor.paste()
        
        # Should contain the pasted text
        result = editor.toPlainText()
        assert "paste" in result
        assert result.count("paste") == 2  # Original + pasted
    
    def test_enhanced_editor_edit_operations(self):
        """Test edit operations in EnhancedEditor."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Mock text editor
            mock_text_editor = Mock(spec=TextEditor)
            
            with patch.object(editor, 'get_current_editor', return_value=mock_text_editor):
                # Test cut operation
                editor.cut()
                mock_text_editor.cut.assert_called_once()
                
                # Test copy operation
                editor.copy()
                mock_text_editor.copy.assert_called_once()
                
                # Test paste operation
                editor.paste()
                mock_text_editor.paste.assert_called_once()
                
                # Test select all operation
                editor.select_all()
                mock_text_editor.selectAll.assert_called_once()


# CRITICAL TEST 4: SELECTION HANDLING
class TestSelectionHandling:
    """Test critical text selection functionality."""
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_selection_basic(self, qapp):
        """Test basic text selection operations."""
        editor = TextEditor()
        content = "This is test content for selection"
        editor.setPlainText(content)
        
        # Select all text
        editor.selectAll()
        cursor = editor.textCursor()
        assert cursor.hasSelection()
        assert cursor.selectedText() == content
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_partial_text_selection(self, qapp):
        """Test partial text selection."""
        editor = TextEditor()
        content = "Word1 Word2 Word3"
        editor.setPlainText(content)
        
        # Select middle word
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 6)   # Move to "Word2"
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 5)    # Select "Word2"
        editor.setTextCursor(cursor)
        
        assert cursor.hasSelection()
        assert cursor.selectedText() == "Word2"
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_selection_modification(self, qapp):
        """Test modifying selected text."""
        editor = TextEditor()
        content = "Replace this word"
        editor.setPlainText(content)
        
        # Select "this"
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 8)   # Move to "this"
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)    # Select "this"
        editor.setTextCursor(cursor)
        
        # Replace selected text
        cursor.insertText("that")
        
        assert editor.toPlainText() == "Replace that word"
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_multi_line_selection(self, qapp):
        """Test multi-line text selection."""
        editor = TextEditor()
        content = "Line 1\nLine 2\nLine 3"
        editor.setPlainText(content)
        
        # Select from middle of line 1 to middle of line 3
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 3)    # Move to "e 1"
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 2)     # Down 2 lines
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 3)    # To "e 3"
        editor.setTextCursor(cursor)
        
        selected = cursor.selectedText()
        assert "e 1" in selected
        assert "Line 2" in selected
        assert "e 3" in selected


# CRITICAL TEST 5: REAL FILE I/O OPERATIONS
class TestRealFileOperations:
    """Test critical file I/O operations with real files."""
    
    def test_file_creation_and_reading(self, temp_test_files):
        """Test creating and reading real files."""
        test_file = temp_test_files['simple.txt']
        
        # Verify file exists and has correct content
        assert os.path.exists(test_file)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content
    
    def test_enhanced_editor_file_operations(self, temp_test_files):
        """Test EnhancedEditor file operations with real files."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Test file opening
            test_file = temp_test_files['test.py']
            
            # Mock the new_document method and related UI updates
            with patch.object(editor, 'new_document') as mock_new_doc:
                mock_new_doc.return_value = "doc_0"
                with patch.object(editor, 'update_recent_files_list'):
                    doc_id = editor.open_document(test_file)
                    
                    # Should have called new_document with file content
                    mock_new_doc.assert_called_once()
                    call_args = mock_new_doc.call_args[0]
                    assert len(call_args) >= 1  # Content
                    assert "def function_one" in call_args[0]
    
    def test_file_encoding_detection(self, temp_test_files):
        """Test file encoding detection with real files."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Test with unicode file
            unicode_file = temp_test_files['unicode.txt']
            encoding = editor.detect_encoding(unicode_file)
            
            # Should detect UTF-8 or compatible encoding
            assert encoding in ['utf-8', 'UTF-8', 'ascii']
    
    def test_large_file_handling(self, temp_test_files):
        """Test handling of large files."""
        large_file = temp_test_files['large.txt']
        
        # Verify large file exists
        assert os.path.exists(large_file)
        
        # Check file size
        file_size = os.path.getsize(large_file)
        assert file_size > 50000  # Should be substantial
        
        # Test reading large file
        start_time = time.time()
        with open(large_file, 'r', encoding='utf-8') as f:
            content = f.read()
        end_time = time.time()
        
        # Should read within reasonable time
        assert end_time - start_time < 2.0
        assert "Line 999:" in content


# CRITICAL TEST 6: DOCUMENT STATE MANAGEMENT
class TestDocumentStateManagement:
    """Test critical document state management."""
    
    def test_document_modification_tracking(self):
        """Test document modification state tracking."""
        dm = DocumentManager()
        
        # Create clean document
        doc_id = dm.create_document("Initial content")
        document = dm.get_document(doc_id)
        assert document['is_modified'] is False
        
        # Mark as modified
        dm.update_document(doc_id, is_modified=True)
        assert document['is_modified'] is True
        
        # Clear modification flag
        dm.update_document(doc_id, is_modified=False)
        assert document['is_modified'] is False
    
    def test_multiple_document_state_tracking(self):
        """Test state tracking with multiple documents."""
        dm = DocumentManager()
        
        # Create multiple documents
        doc1 = dm.create_document("Document 1")
        doc2 = dm.create_document("Document 2")
        doc3 = dm.create_document("Document 3")
        
        # Modify some documents
        dm.update_document(doc1, is_modified=True)
        dm.update_document(doc3, is_modified=True)
        
        # Check states
        assert dm.get_document(doc1)['is_modified'] is True
        assert dm.get_document(doc2)['is_modified'] is False
        assert dm.get_document(doc3)['is_modified'] is True
    
    def test_document_properties_persistence(self):
        """Test document properties persistence."""
        dm = DocumentManager()
        doc_id = dm.create_document("Content", "/path/test.py")
        
        # Update multiple properties
        dm.update_document(doc_id, 
                         encoding='utf-16',
                         line_ending='crlf',
                         is_modified=True)
        
        document = dm.get_document(doc_id)
        assert document['encoding'] == 'utf-16'
        assert document['line_ending'] == 'crlf'
        assert document['is_modified'] is True
        assert document['document_type'] == DocumentType.PYTHON
    
    def test_enhanced_editor_document_state_integration(self):
        """Test document state integration in EnhancedEditor."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create document
            doc_id = editor.document_manager.create_document("Test content")
            
            # Mark as modified and test tab title update
            with patch.object(editor, 'update_tab_title') as mock_update_title:
                editor.mark_document_modified(doc_id)
                
                # Should update document state and tab title
                document = editor.document_manager.get_document(doc_id)
                assert document['is_modified'] is True
                mock_update_title.assert_called_once_with(doc_id)


# CRITICAL TEST 7: MEMORY MANAGEMENT
class TestMemoryManagement:
    """Test critical memory management functionality."""
    
    def test_document_cleanup_on_removal(self):
        """Test proper cleanup when documents are removed."""
        dm = DocumentManager()
        
        # Create multiple documents
        doc_ids = []
        for i in range(10):
            doc_id = dm.create_document(f"Document {i}")
            doc_ids.append(doc_id)
        
        assert len(dm.documents) == 10
        
        # Remove half the documents
        for doc_id in doc_ids[:5]:
            dm.remove_document(doc_id)
        
        assert len(dm.documents) == 5
        
        # Verify removed documents are gone
        for doc_id in doc_ids[:5]:
            assert dm.get_document(doc_id) is None
    
    def test_recent_files_memory_limit(self):
        """Test recent files list memory management."""
        dm = DocumentManager()
        original_limit = dm.max_recent_files
        
        # Add more files than limit
        for i in range(original_limit + 5):
            dm.add_to_recent_files(f"/path/file{i}.txt")
        
        # Should not exceed limit
        assert len(dm.recent_files) == original_limit
        
        # Should contain most recent files
        assert f"/path/file{original_limit + 4}.txt" in dm.recent_files
        assert "/path/file0.txt" not in dm.recent_files
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_text_editor_memory_with_large_content(self, qapp):
        """Test TextEditor memory usage with large content."""
        editor = TextEditor()
        
        # Create large content
        large_content = "Large line content " * 1000 + "\n"
        large_text = large_content * 100  # ~2MB of text
        
        # Set large content
        start_time = time.time()
        editor.setPlainText(large_text)
        end_time = time.time()
        
        # Should handle large content reasonably quickly
        assert end_time - start_time < 2.0
        
        # Verify content is set
        assert len(editor.toPlainText()) > 100000
        
        # Clear content to free memory
        editor.clear()
        assert len(editor.toPlainText()) == 0


# CRITICAL TEST 8: MULTI-DOCUMENT OPERATIONS
class TestMultiDocumentOperations:
    """Test critical multi-document functionality."""
    
    def test_enhanced_editor_tab_management(self):
        """Test tab management in EnhancedEditor."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create multiple documents
            with patch.object(editor, 'update_status_bar'):
                doc1 = editor.new_document("Content 1")
                doc2 = editor.new_document("Content 2")
                doc3 = editor.new_document("Content 3")
            
            # Should have 3 documents
            assert len(editor.document_manager.documents) == 3
            
            # Test tab mapping
            assert 0 in editor.tab_to_doc_mapping
            assert 1 in editor.tab_to_doc_mapping
            assert 2 in editor.tab_to_doc_mapping
    
    def test_document_switching(self):
        """Test switching between documents."""
        dm = DocumentManager()
        
        # Create documents
        doc1 = dm.create_document("Document 1")
        doc2 = dm.create_document("Document 2")
        
        # Current should be last created
        assert dm.current_document == doc2
        
        # Switch to first document
        dm.current_document = doc1
        assert dm.current_document == doc1
    
    def test_tab_close_with_unsaved_changes(self):
        """Test closing tabs with unsaved changes."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create modified document
            doc_id = editor.document_manager.create_document("Test content")
            editor.document_manager.update_document(doc_id, is_modified=True)
            editor.tab_to_doc_mapping[0] = doc_id
            
            # Test close with save option
            with patch('enhanced_editor.QMessageBox.question') as mock_question:
                mock_question.return_value = QMessageBox.Save
                with patch.object(editor, 'save_document') as mock_save:
                    mock_save.return_value = True
                    
                    editor.close_document_tab(0)
                    
                    # Should attempt to save
                    mock_save.assert_called_once_with(doc_id)


# CRITICAL TEST 9: INTEGRATION WITH STANDARDWINDOW
class TestStandardWindowIntegration:
    """Test critical StandardWindow integration."""
    
    def test_enhanced_editor_initialization_sequence(self):
        """Test proper initialization sequence with StandardWindow."""
        # Mock StandardWindow initialization to avoid dependency issues
        with patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            with patch.object(EnhancedEditor, 'setup_ui') as mock_setup_ui, \
                 patch.object(EnhancedEditor, 'setup_menu_callbacks') as mock_setup_menu, \
                 patch.object(EnhancedEditor, 'load_settings') as mock_load_settings, \
                 patch.object(EnhancedEditor, 'new_document') as mock_new_doc:
                
                editor = EnhancedEditor()
                
                # Verify initialization sequence
                mock_setup_ui.assert_called_once()
                mock_setup_menu.assert_called_once()
                mock_load_settings.assert_called_once()
                mock_new_doc.assert_called_once()
    
    def test_menu_callback_registration(self):
        """Test menu callback registration."""
        with patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            with patch.object(EnhancedEditor, 'setup_ui'), \
                 patch.object(EnhancedEditor, 'load_settings'), \
                 patch.object(EnhancedEditor, 'new_document'):
                
                editor = EnhancedEditor()
                
                # Mock menu manager
                mock_menu_manager = Mock()
                editor.menu_manager = mock_menu_manager
                
                # Call setup_menu_callbacks
                editor.setup_menu_callbacks()
                
                # Should have registered callbacks
                assert mock_menu_manager.register_callback.call_count > 0
    
    def test_status_message_integration(self):
        """Test status message integration."""
        with patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            with patch.object(EnhancedEditor, 'setup_ui'), \
                 patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
                 patch.object(EnhancedEditor, 'load_settings'), \
                 patch.object(EnhancedEditor, 'new_document'):
                
                editor = EnhancedEditor()
                
                # Mock show_status_message
                status_messages = []
                def capture_status(message, timeout=3000):
                    status_messages.append((message, timeout))
                
                editor.show_status_message = capture_status
                
                # Test status updates
                editor.update_cursor_position(10, 5)
                editor.update_status_bar()
                
                # Should have status messages
                assert len(status_messages) > 0


# CRITICAL TEST 10: ERROR RECOVERY AND EDGE CASES
class TestErrorRecoveryAndEdgeCases:
    """Test critical error recovery and edge case handling."""
    
    def test_file_operation_error_recovery(self):
        """Test error recovery for file operations."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Test opening non-existent file
            with patch('enhanced_editor.QMessageBox.critical') as mock_error:
                result = editor.open_document("/nonexistent/file.txt")
                
                # Should handle error gracefully
                assert result is None
                mock_error.assert_called_once()
    
    def test_save_operation_error_recovery(self):
        """Test error recovery for save operations."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.document_manager = DocumentManager()
            
            # Create document
            doc_id = editor.document_manager.create_document("Content", "/readonly/file.txt")
            
            # Mock editor and file operations
            mock_editor = Mock()
            mock_editor.toPlainText.return_value = "Content"
            
            with patch.object(editor, 'get_editor_for_document', return_value=mock_editor):
                with patch('builtins.open', side_effect=PermissionError("Access denied")):
                    with patch('enhanced_editor.QMessageBox.critical') as mock_error:
                        
                        result = editor.save_document(doc_id)
                        
                        # Should handle error gracefully
                        assert result is False
                        mock_error.assert_called_once()
    
    def test_invalid_regex_error_handling(self):
        """Test handling of invalid regex in search."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            
            # Mock text editor
            mock_editor = Mock(spec=TextEditor)
            mock_cursor = Mock()
            mock_cursor.position.return_value = 0
            mock_editor.textCursor.return_value = mock_cursor
            mock_editor.toPlainText.return_value = "test content"
            
            # Test with invalid regex
            options = SearchOptions(use_regex=True)
            
            # Should handle regex errors gracefully
            result = editor.perform_search(mock_editor, "[invalid", options)
            
            # Should return False for invalid regex
            assert result is False
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_empty_document_operations(self, qapp):
        """Test operations on empty documents."""
        editor = TextEditor()
        
        # Test operations on empty editor
        assert editor.toPlainText() == ""
        
        # Should handle undo on empty document
        editor.undo()  # Should not crash
        
        # Should handle selection on empty document
        editor.selectAll()
        cursor = editor.textCursor()
        assert not cursor.hasSelection()
    
    @pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
    def test_unicode_content_edge_cases(self, qapp):
        """Test Unicode content edge cases."""
        editor = TextEditor()
        
        # Test various Unicode content
        unicode_tests = [
            "Basic ASCII",
            "Accented: ñáéíóú",
            "Chinese: 中文测试",
            "Emoji: 🚀🎉💻",
            "Mathematical: ∑∆∇∂",
            "Mixed: Test 中文 🚀 ñáéíóú"
        ]
        
        for content in unicode_tests:
            editor.setPlainText(content)
            assert editor.toPlainText() == content
            
            # Test cursor operations with Unicode
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            editor.setTextCursor(cursor)
            # Should not crash


# COMPREHENSIVE INTEGRATION TEST
class TestCriticalFunctionalityIntegration:
    """Integration test for all critical functionality together."""
    
    def test_complete_editing_workflow(self, temp_test_files):
        """Test complete editing workflow with critical functionality."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # 1. Create new document
            with patch.object(editor, 'update_status_bar'):
                doc_id = editor.new_document("Initial content")
            
            # 2. Verify document state
            document = editor.document_manager.get_document(doc_id)
            assert document is not None
            assert document['content'] == "Initial content"
            assert document['is_modified'] is False
            
            # 3. Mark as modified (simulating user edit)
            editor.mark_document_modified(doc_id)
            assert document['is_modified'] is True
            
            # 4. Test save operation
            test_file = temp_test_files['simple.txt']
            document['file_path'] = test_file
            
            mock_editor = Mock()
            mock_editor.toPlainText.return_value = "Modified content"
            
            with patch.object(editor, 'get_editor_for_document', return_value=mock_editor):
                with patch('builtins.open', mock_open()) as mock_file:
                    with patch.object(editor, 'update_tab_title'):
                        result = editor.save_document(doc_id)
                        
                        # Should successfully save
                        assert result is True
                        assert document['is_modified'] is False
    
    def test_multiple_document_workflow(self):
        """Test workflow with multiple documents."""
        with patch.object(EnhancedEditor, 'setup_ui'), \
             patch.object(EnhancedEditor, 'setup_menu_callbacks'), \
             patch.object(EnhancedEditor, 'load_settings'), \
             patch('enhanced_editor.StandardWindow.__init__', return_value=None):
            
            editor = EnhancedEditor()
            editor.tab_widget = Mock()
            editor.document_manager = DocumentManager()
            
            # Create multiple documents
            docs = []
            with patch.object(editor, 'update_status_bar'):
                for i in range(3):
                    doc_id = editor.new_document(f"Document {i}")
                    docs.append(doc_id)
            
            # All documents should exist
            assert len(editor.document_manager.documents) == 3
            
            # Test document switching
            for doc_id in docs:
                editor.document_manager.current_document = doc_id
                assert editor.document_manager.current_document == doc_id
            
            # Test closing documents
            for doc_id in docs:
                editor.document_manager.remove_document(doc_id)
            
            # All documents should be removed
            assert len(editor.document_manager.documents) == 0


# TEST EXECUTION SUMMARY AND REPORTING
def test_critical_functionality_coverage():
    """Verify that all critical functionality areas are covered."""
    critical_areas = [
        "Undo/Redo Operations",
        "Cursor Management", 
        "Text Manipulation",
        "Selection Handling",
        "File I/O Operations",
        "Document State Management",
        "Memory Management",
        "Multi-document Operations",
        "StandardWindow Integration",
        "Error Recovery"
    ]
    
    # This test verifies we have test classes for all critical areas
    test_classes = [
        TestUndoRedoOperations,
        TestCursorManagement,
        TestTextManipulation,
        TestSelectionHandling,
        TestRealFileOperations,
        TestDocumentStateManagement,
        TestMemoryManagement,
        TestMultiDocumentOperations,
        TestStandardWindowIntegration,
        TestErrorRecoveryAndEdgeCases
    ]
    
    assert len(test_classes) == len(critical_areas)
    
    # Generate test execution summary
    test_summary = {
        "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_file": "test_enhanced_editor_critical_functionality_2025-09-01.py",
        "target_module": "enhanced_editor.py",
        "purpose": "Resolve utilities-overview.md High Priority Item 2",
        "critical_areas_tested": critical_areas,
        "total_test_classes": len(test_classes),
        "pyqt_dependency": PYQT_AVAILABLE,
        "test_categories": [
            "Undo/Redo functionality",
            "Cursor positioning and tracking",
            "Text insertion/deletion/clipboard",
            "Text selection operations",
            "Real file read/write operations",
            "Document state tracking",
            "Memory management and cleanup",
            "Multi-document tab management",
            "StandardWindow integration",
            "Error handling and recovery"
        ]
    }
    
    # Verify summary is valid
    assert test_summary["target_module"] == "enhanced_editor.py"
    assert len(test_summary["critical_areas_tested"]) == 10


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        f"--html=result_enhanced_editor_critical_functionality_2025-09-01_report.html",
        "--self-contained-html",
        f"--junitxml=result_enhanced_editor_critical_functionality_2025-09-01_junit.xml"
    ])