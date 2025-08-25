#!/usr/bin/env python3
"""
Comprehensive unit tests for bookmark_manager.py
Generated on: 2025-08-24
Test Framework: pytest

This test suite covers all functions and methods in bookmark_manager.py:
- BookmarkModel class methods
- BookmarkImporter class methods
- BookmarkExporter class methods
- BookmarkDialog class methods
- BookmarkManagerGUI class methods
- URL validation and edge cases
- Database operations
- Import/Export functionality
- Error handling
"""

import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the modules to test
from utilities.network.bookmark_manager import (BookmarkDialog,
                                                BookmarkExporter,
                                                BookmarkImporter,
                                                BookmarkManagerGUI,
                                                BookmarkModel)

# Test constants
TEST_DB_NAME = "test_bookmarks.db"
SAMPLE_BOOKMARK_DATA = {
    'title': 'Test Bookmark',
    'url': 'https://example.com',
    'description': 'Test description',
    'tags': 'test,example',
    'folder': 'Test Folder'
}

SAMPLE_HTML_CONTENT = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1>
<DL><p>
    <DT><H3>Test Folder</H3>
    <DL><p>
        <DT><A HREF="https://example.com">Example Site</A>
        <DT><A HREF="https://test.com">Test Site</A>
    </DL><p>
</DL><p>
'''

SAMPLE_JSON_CONTENT = [
    {
        "title": "Example Site",
        "url": "https://example.com",
        "description": "Example description",
        "tags": "example",
        "folder": "Test"
    },
    {
        "title": "Test Site", 
        "url": "https://test.com",
        "description": "Test description",
        "tags": "test",
        "folder": "Test"
    }
]


class TestBookmarkModel:
    """Test suite for BookmarkModel class"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, TEST_DB_NAME)
        yield db_path
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture  
    def bookmark_model(self, temp_db_path):
        """Create BookmarkModel instance with temporary database"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
            return model
    
    def test_init_database_creation(self, temp_db_path):
        """Test database initialization creates required tables"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
            
        # Verify database file exists
        assert os.path.exists(temp_db_path)
        
        # Verify tables exist
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check bookmarks table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookmarks'")
        assert cursor.fetchone() is not None
        
        # Check tags table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tags'")
        assert cursor.fetchone() is not None
        
        # Check folders table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='folders'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_init_database_error_handling(self):
        """Test database initialization error handling"""
        # Test with invalid path
        invalid_path = "/invalid/path/test.db"
        
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            with pytest.raises(sqlite3.Error):
                model = BookmarkModel(invalid_path)
    
    def test_validate_url_valid_cases(self, bookmark_model):
        """Test URL validation with valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://test.com",
            "ftp://files.example.com",
            "example.com",  # Should add https://
            "www.example.com",
            "https://example.com/path?param=value"
        ]
        
        for url in valid_urls:
            is_valid, result = bookmark_model._validate_url(url)
            assert is_valid, f"URL should be valid: {url}"
            assert result.startswith(('http://', 'https://', 'ftp://')), f"URL should have protocol: {result}"
    
    def test_validate_url_invalid_cases(self, bookmark_model):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "",
            "   ",
            "not a url",
            "http://",
            "https://",
            "http:// invalid space.com",
            "https://example<>.com",
            "http://exam\"ple.com"
        ]
        
        for url in invalid_urls:
            is_valid, error_msg = bookmark_model._validate_url(url)
            assert not is_valid, f"URL should be invalid: {url}"
            assert isinstance(error_msg, str), "Error message should be string"
    
    def test_add_bookmark_success(self, bookmark_model):
        """Test successful bookmark addition"""
        success, message = bookmark_model.add_bookmark(
            title="Test Site",
            url="https://example.com",
            description="Test description",
            tags="test,example",
            folder="Test"
        )
        
        assert success is True
        assert "Successfully added bookmark" in message
        
        # Verify bookmark was added
        bookmarks = bookmark_model.get_all_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0]['title'] == "Test Site"
        assert bookmarks[0]['url'] == "https://example.com"
    
    def test_add_bookmark_invalid_url(self, bookmark_model):
        """Test bookmark addition with invalid URL"""
        success, message = bookmark_model.add_bookmark(
            title="Test Site",
            url="",  # Invalid empty URL
            description="Test description"
        )
        
        assert success is False
        assert "URL validation failed" in message
    
    def test_add_bookmark_empty_title(self, bookmark_model):
        """Test bookmark addition with empty title"""
        success, message = bookmark_model.add_bookmark(
            title="",  # Invalid empty title
            url="https://example.com",
            description="Test description"
        )
        
        assert success is False
        assert "Title cannot be empty" in message
    
    def test_add_bookmark_database_error(self, temp_db_path):
        """Test bookmark addition with database error"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        # Close and delete database to simulate error
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        
        success, message = model.add_bookmark(
            title="Test Site",
            url="https://example.com"
        )
        
        assert success is False
        assert "Database error" in message
    
    def test_update_bookmark_success(self, bookmark_model):
        """Test successful bookmark update"""
        # First add a bookmark
        bookmark_model.add_bookmark("Original Title", "https://example.com")
        bookmarks = bookmark_model.get_all_bookmarks()
        bookmark_id = bookmarks[0]['id']
        
        # Update the bookmark
        success = bookmark_model.update_bookmark(
            bookmark_id=bookmark_id,
            title="Updated Title",
            url="https://updated.com",
            description="Updated description",
            tags="updated",
            folder="Updated Folder"
        )
        
        assert success is True
        
        # Verify update
        updated_bookmarks = bookmark_model.get_all_bookmarks()
        assert len(updated_bookmarks) == 1
        assert updated_bookmarks[0]['title'] == "Updated Title"
        assert updated_bookmarks[0]['url'] == "https://updated.com"
    
    def test_update_bookmark_nonexistent(self, bookmark_model):
        """Test updating non-existent bookmark"""
        success = bookmark_model.update_bookmark(
            bookmark_id=999,  # Non-existent ID
            title="Test",
            url="https://example.com"
        )
        
        assert success is True  # SQLite doesn't error for non-existent updates
    
    def test_delete_bookmark_success(self, bookmark_model):
        """Test successful bookmark deletion"""
        # Add a bookmark
        bookmark_model.add_bookmark("Test Site", "https://example.com")
        bookmarks = bookmark_model.get_all_bookmarks()
        assert len(bookmarks) == 1
        bookmark_id = bookmarks[0]['id']
        
        # Delete the bookmark
        success = bookmark_model.delete_bookmark(bookmark_id)
        assert success is True
        
        # Verify deletion
        bookmarks = bookmark_model.get_all_bookmarks()
        assert len(bookmarks) == 0
    
    def test_delete_bookmark_nonexistent(self, bookmark_model):
        """Test deleting non-existent bookmark"""
        success = bookmark_model.delete_bookmark(999)  # Non-existent ID
        assert success is True  # SQLite doesn't error for non-existent deletes
    
    def test_get_all_bookmarks_empty(self, bookmark_model):
        """Test getting bookmarks from empty database"""
        bookmarks = bookmark_model.get_all_bookmarks()
        assert bookmarks == []
    
    def test_get_all_bookmarks_populated(self, bookmark_model):
        """Test getting bookmarks from populated database"""
        # Add multiple bookmarks
        test_bookmarks = [
            ("Site 1", "https://example1.com", "Description 1", "tag1", "Folder1"),
            ("Site 2", "https://example2.com", "Description 2", "tag2", "Folder2"),
            ("Site 3", "https://example3.com", "Description 3", "tag3", "Folder1")
        ]
        
        for title, url, desc, tags, folder in test_bookmarks:
            bookmark_model.add_bookmark(title, url, desc, tags, folder)
        
        bookmarks = bookmark_model.get_all_bookmarks()
        assert len(bookmarks) == 3
        
        # Verify bookmark structure
        for bookmark in bookmarks:
            required_fields = ['id', 'title', 'url', 'description', 'tags', 'folder', 
                             'created_date', 'modified_date', 'visit_count', 'favorite']
            for field in required_fields:
                assert field in bookmark
    
    def test_search_bookmarks_by_title(self, bookmark_model):
        """Test searching bookmarks by title"""
        # Add test bookmarks
        bookmark_model.add_bookmark("Python Tutorial", "https://python.org")
        bookmark_model.add_bookmark("Java Guide", "https://java.com")
        bookmark_model.add_bookmark("Python Advanced", "https://advanced-python.com")
        
        # Search by title
        results = bookmark_model.search_bookmarks("Python", "title")
        assert len(results) == 2
        assert all("Python" in bookmark['title'] for bookmark in results)
    
    def test_search_bookmarks_by_url(self, bookmark_model):
        """Test searching bookmarks by URL"""
        bookmark_model.add_bookmark("Example", "https://example.com/test")
        bookmark_model.add_bookmark("Test", "https://test.com/demo")
        bookmark_model.add_bookmark("Demo", "https://example.org/demo")
        
        results = bookmark_model.search_bookmarks("example", "url")
        assert len(results) == 2
    
    def test_search_bookmarks_by_tags(self, bookmark_model):
        """Test searching bookmarks by tags"""
        bookmark_model.add_bookmark("Site 1", "https://site1.com", tags="python,tutorial")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", tags="java,guide")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", tags="python,advanced")
        
        results = bookmark_model.search_bookmarks("python", "tags")
        assert len(results) == 2
    
    def test_search_bookmarks_all_fields(self, bookmark_model):
        """Test searching across all fields"""
        bookmark_model.add_bookmark("Python Site", "https://python.com", "Learn Python", "programming")
        bookmark_model.add_bookmark("Java Tutorial", "https://java.com", "Java guide", "programming")
        
        # Search term appears in different fields
        results = bookmark_model.search_bookmarks("Python", "all")
        assert len(results) >= 1
    
    def test_search_bookmarks_no_results(self, bookmark_model):
        """Test search with no matching results"""
        bookmark_model.add_bookmark("Test Site", "https://example.com")
        
        results = bookmark_model.search_bookmarks("nonexistent", "all")
        assert len(results) == 0
    
    def test_get_all_tags(self, bookmark_model):
        """Test getting all unique tags"""
        # Add bookmarks with various tags
        bookmark_model.add_bookmark("Site 1", "https://site1.com", tags="python,web,tutorial")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", tags="java,programming")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", tags="python,advanced")
        
        tags = bookmark_model.get_all_tags()
        expected_tags = ["advanced", "java", "programming", "python", "tutorial", "web"]
        assert sorted(tags) == expected_tags
    
    def test_get_all_tags_empty(self, bookmark_model):
        """Test getting tags from database with no bookmarks"""
        tags = bookmark_model.get_all_tags()
        assert tags == []
    
    def test_get_all_folders(self, bookmark_model):
        """Test getting all unique folders"""
        bookmark_model.add_bookmark("Site 1", "https://site1.com", folder="Development")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", folder="Reference")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", folder="Development")
        
        folders = bookmark_model.get_all_folders()
        expected_folders = ["Development", "Reference"]
        assert sorted(folders) == expected_folders
    
    def test_get_tags_and_folders(self, bookmark_model):
        """Test getting tags and folders in single call"""
        bookmark_model.add_bookmark("Site 1", "https://site1.com", tags="python,web", folder="Dev")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", tags="java", folder="Reference")
        
        tags, folders = bookmark_model.get_tags_and_folders()
        assert sorted(tags) == ["java", "python", "web"]
        assert sorted(folders) == ["Dev", "Reference"]


class TestBookmarkImporter:
    """Test suite for BookmarkImporter class"""
    
    def test_import_from_html_success(self):
        """Test successful HTML import"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(SAMPLE_HTML_CONTENT)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_html(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
            assert bookmarks[0]['folder'] == "Test Folder"
        finally:
            os.unlink(temp_file)
    
    def test_import_from_html_file_not_found(self):
        """Test HTML import with non-existent file"""
        bookmarks = BookmarkImporter.import_from_html("nonexistent.html")
        assert bookmarks == []
    
    def test_import_from_html_malformed(self):
        """Test HTML import with malformed content"""
        malformed_html = "<html><body>Not valid bookmark format</body></html>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(malformed_html)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_html(temp_file)
            assert bookmarks == []  # Should handle gracefully
        finally:
            os.unlink(temp_file)
    
    def test_import_from_json_success(self):
        """Test successful JSON import"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(SAMPLE_JSON_CONTENT, f)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
        finally:
            os.unlink(temp_file)
    
    def test_import_from_json_nested_structure(self):
        """Test JSON import with nested structure"""
        nested_json = {
            "bookmarks": {
                "folder1": [
                    {"title": "Site 1", "url": "https://site1.com"},
                    {"title": "Site 2", "url": "https://site2.com"}
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(nested_json, f)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert len(bookmarks) == 2
        finally:
            os.unlink(temp_file)
    
    def test_import_from_json_invalid_file(self):
        """Test JSON import with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert bookmarks == []
        finally:
            os.unlink(temp_file)
    
    def test_import_from_csv_success(self):
        """Test successful CSV import"""
        csv_content = """title,url,description,tags,folder
Example Site,https://example.com,Example description,example,Test
Test Site,https://test.com,Test description,test,Test"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_csv(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
        finally:
            os.unlink(temp_file)
    
    def test_import_from_csv_alternative_headers(self):
        """Test CSV import with alternative header names"""
        csv_content = """Title,URL,Description,Tags,Folder
Example Site,https://example.com,Example description,example,Test"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_csv(temp_file)
            assert len(bookmarks) == 1
            assert bookmarks[0]['title'] == "Example Site"
        finally:
            os.unlink(temp_file)
    
    def test_process_json_data_list(self):
        """Test processing JSON data as list"""
        bookmarks = []
        BookmarkImporter._process_json_data(SAMPLE_JSON_CONTENT, bookmarks)
        assert len(bookmarks) == 2
    
    def test_process_json_data_dict(self):
        """Test processing JSON data as dictionary"""
        bookmarks = []
        json_dict = {"bookmarks": SAMPLE_JSON_CONTENT}
        BookmarkImporter._process_json_data(json_dict, bookmarks)
        assert len(bookmarks) == 2
    
    def test_is_valid_bookmark_item(self):
        """Test bookmark item validation"""
        valid_item = {"title": "Test", "url": "https://test.com"}
        invalid_item1 = {"title": "Test"}  # Missing URL
        invalid_item2 = {"url": "https://test.com"}  # Missing title
        invalid_item3 = {}  # Missing both
        
        assert BookmarkImporter._is_valid_bookmark_item(valid_item) is True
        assert BookmarkImporter._is_valid_bookmark_item(invalid_item1) is False
        assert BookmarkImporter._is_valid_bookmark_item(invalid_item2) is False
        assert BookmarkImporter._is_valid_bookmark_item(invalid_item3) is False
    
    def test_create_bookmark_from_item(self):
        """Test creating bookmark from item data"""
        item = {
            "title": "Test Site",
            "url": "https://test.com",
            "description": "Test description",
            "tags": "test,example"
        }
        
        bookmark = BookmarkImporter._create_bookmark_from_item(item, "Default")
        
        assert bookmark['title'] == "Test Site"
        assert bookmark['url'] == "https://test.com"
        assert bookmark['description'] == "Test description"
        assert bookmark['tags'] == "test,example"
        assert bookmark['folder'] == "Default"
    
    def test_create_bookmark_from_item_minimal(self):
        """Test creating bookmark with minimal data"""
        item = {"title": "Test", "url": "https://test.com"}
        
        bookmark = BookmarkImporter._create_bookmark_from_item(item, "Default")
        
        assert bookmark['title'] == "Test"
        assert bookmark['url'] == "https://test.com"
        assert bookmark['description'] == ""
        assert bookmark['tags'] == ""
        assert bookmark['folder'] == "Default"


class TestBookmarkExporter:
    """Test suite for BookmarkExporter class"""
    
    @pytest.fixture
    def sample_bookmarks(self):
        """Sample bookmark data for testing"""
        return [
            {
                'title': 'Example Site',
                'url': 'https://example.com',
                'description': 'Example description',
                'tags': 'example,test',
                'folder': 'Test Folder',
                'created_date': '2025-08-24T10:00:00'
            },
            {
                'title': 'Test Site',
                'url': 'https://test.com',
                'description': 'Test description',
                'tags': 'test',
                'folder': 'Test Folder',
                'created_date': '2025-08-24T10:05:00'
            }
        ]
    
    def test_export_to_html_success(self, sample_bookmarks):
        """Test successful HTML export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_html(sample_bookmarks, temp_file)
            assert success is True
            
            # Verify file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Example Site" in content
                assert "https://example.com" in content
                assert "Test Folder" in content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_html_permission_error(self, sample_bookmarks):
        """Test HTML export with permission error"""
        # Try to write to a protected location
        protected_path = "/root/test.html" if os.name != 'nt' else "C:\\Windows\\System32\\test.html"
        
        success = BookmarkExporter.export_to_html(sample_bookmarks, protected_path)
        assert success is False
    
    def test_export_to_json_success(self, sample_bookmarks):
        """Test successful JSON export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(sample_bookmarks, temp_file)
            assert success is True
            
            # Verify file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
                assert len(exported_data) == 2
                assert exported_data[0]['title'] == 'Example Site'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_json_serialization_error(self):
        """Test JSON export with non-serializable data"""
        # Create bookmarks with non-serializable data
        bad_bookmarks = [{'title': 'Test', 'date': datetime.now()}]  # datetime not serializable
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(bad_bookmarks, temp_file)
            assert success is False
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_csv_success(self, sample_bookmarks):
        """Test successful CSV export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_csv(sample_bookmarks, temp_file)
            assert success is True
            
            # Verify file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "title,url,description,tags,folder,created_date" in content
                assert "Example Site" in content
                assert "https://example.com" in content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_csv_write_error(self, sample_bookmarks):
        """Test CSV export with write error"""
        # Use invalid path
        invalid_path = "/invalid/path/test.csv"
        
        success = BookmarkExporter.export_to_csv(sample_bookmarks, invalid_path)
        assert success is False


class TestBookmarkDialog:
    """Test suite for BookmarkDialog class"""
    
    @pytest.fixture
    def qt_app(self):
        """Create QApplication for testing Qt widgets"""
        import sys

        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    
    def test_dialog_initialization_new_bookmark(self, qt_app):
        """Test dialog initialization for new bookmark"""
        dialog = BookmarkDialog()
        
        assert dialog.windowTitle() == "Add Bookmark"
        assert dialog.bookmark is None
        assert dialog.title_edit.text() == ""
        assert dialog.url_edit.text() == ""
        assert dialog.folder_edit.text() == "Default"
    
    def test_dialog_initialization_edit_bookmark(self, qt_app):
        """Test dialog initialization for editing bookmark"""
        bookmark_data = {
            'title': 'Test Site',
            'url': 'https://test.com',
            'description': 'Test description',
            'tags': 'test,example',
            'folder': 'Test Folder'
        }
        
        dialog = BookmarkDialog(bookmark=bookmark_data)
        
        assert dialog.windowTitle() == "Edit Bookmark"
        assert dialog.title_edit.text() == "Test Site"
        assert dialog.url_edit.text() == "https://test.com"
        assert dialog.description_edit.toPlainText() == "Test description"
        assert dialog.tags_edit.text() == "test,example"
        assert dialog.folder_edit.text() == "Test Folder"
    
    def test_get_bookmark_data(self, qt_app):
        """Test getting bookmark data from dialog"""
        dialog = BookmarkDialog()
        
        # Set form values
        dialog.title_edit.setText("Test Bookmark")
        dialog.url_edit.setText("https://example.com")
        dialog.description_edit.setPlainText("Test description")
        dialog.tags_edit.setText("test,bookmark")
        dialog.folder_edit.setText("Test Folder")
        
        data = dialog.get_bookmark_data()
        
        assert data['title'] == "Test Bookmark"
        assert data['url'] == "https://example.com"
        assert data['description'] == "Test description"
        assert data['tags'] == "test,bookmark"
        assert data['folder'] == "Test Folder"
    
    def test_get_bookmark_data_empty_folder(self, qt_app):
        """Test getting bookmark data with empty folder defaults to Default"""
        dialog = BookmarkDialog()
        
        dialog.title_edit.setText("Test")
        dialog.url_edit.setText("https://test.com")
        dialog.folder_edit.setText("")  # Empty folder
        
        data = dialog.get_bookmark_data()
        assert data['folder'] == "Default"
    
    def test_get_bookmark_data_whitespace_handling(self, qt_app):
        """Test bookmark data whitespace trimming"""
        dialog = BookmarkDialog()
        
        dialog.title_edit.setText("  Test Bookmark  ")
        dialog.url_edit.setText("  https://example.com  ")
        dialog.description_edit.setPlainText("  Test description  ")
        dialog.tags_edit.setText("  test, bookmark  ")
        
        data = dialog.get_bookmark_data()
        
        assert data['title'] == "Test Bookmark"
        assert data['url'] == "https://example.com"
        assert data['description'] == "Test description"
        assert data['tags'] == "test, bookmark"


class TestBookmarkManagerGUI:
    """Test suite for BookmarkManagerGUI class"""
    
    @pytest.fixture
    def qt_app(self):
        """Create QApplication for testing Qt widgets"""
        import sys

        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, TEST_DB_NAME)
        yield db_path
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def bookmark_gui(self, qt_app, temp_db_path):
        """Create BookmarkManagerGUI instance for testing"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            with patch('utilities.network.bookmark_manager.BookmarkModel') as mock_model:
                mock_instance = Mock()
                mock_model.return_value = mock_instance
                mock_instance.get_all_bookmarks.return_value = []
                mock_instance.get_all_folders.return_value = []
                mock_instance.get_all_tags.return_value = []
                
                gui = BookmarkManagerGUI()
                gui.model = mock_instance
                return gui
    
    def test_gui_initialization(self, bookmark_gui):
        """Test GUI initialization"""
        assert bookmark_gui.windowTitle() == "Bookmark Manager - Richard's File Utilities"
        assert hasattr(bookmark_gui, 'model')
        assert hasattr(bookmark_gui, 'bookmark_table')
        assert hasattr(bookmark_gui, 'search_box')
    
    def test_load_bookmarks(self, bookmark_gui):
        """Test loading bookmarks into table"""
        sample_bookmarks = [
            {
                'id': 1,
                'title': 'Test Site',
                'url': 'https://test.com',
                'description': 'Test description',
                'tags': 'test',
                'folder': 'Test',
                'created_date': '2025-08-24T10:00:00',
                'modified_date': '2025-08-24T10:00:00',
                'visit_count': 0,
                'favorite': 0
            }
        ]
        
        bookmark_gui.model.get_all_bookmarks.return_value = sample_bookmarks
        bookmark_gui.load_bookmarks()
        
        assert bookmark_gui.bookmark_table.rowCount() == 1
        assert bookmark_gui.bookmark_table.item(0, 0).text() == "Test Site"
        assert bookmark_gui.bookmark_table.item(0, 1).text() == "https://test.com"
    
    def test_populate_table(self, bookmark_gui):
        """Test populating table with bookmark data"""
        bookmarks = [
            {
                'id': 1,
                'title': 'Site 1',
                'url': 'https://site1.com',
                'tags': 'tag1',
                'folder': 'Folder1',
                'created_date': '2025-08-24T10:00:00',
                'modified_date': '2025-08-24T10:00:00',
                'visit_count': 5,
                'favorite': 1
            },
            {
                'id': 2,
                'title': 'Site 2',
                'url': 'https://site2.com',
                'tags': 'tag2',
                'folder': 'Folder2',
                'created_date': '2025-08-24T11:00:00',
                'modified_date': '2025-08-24T11:00:00',
                'visit_count': 0,
                'favorite': 0
            }
        ]
        
        bookmark_gui.populate_table(bookmarks)
        
        assert bookmark_gui.bookmark_table.rowCount() == 2
        
        # Check first row
        assert bookmark_gui.bookmark_table.item(0, 0).text() == "Site 1"
        assert bookmark_gui.bookmark_table.item(0, 0).data(bookmark_gui.qt_app.instance().UserRole) == 1
        assert bookmark_gui.bookmark_table.item(0, 1).text() == "https://site1.com"
        
        # Check second row
        assert bookmark_gui.bookmark_table.item(1, 0).text() == "Site 2"
        assert bookmark_gui.bookmark_table.item(1, 1).text() == "https://site2.com"
    
    def test_find_bookmark_by_id(self, bookmark_gui):
        """Test finding bookmark by ID"""
        bookmark_gui.current_bookmarks = [
            {'id': 1, 'title': 'Site 1'},
            {'id': 2, 'title': 'Site 2'},
            {'id': 3, 'title': 'Site 3'}
        ]
        
        bookmark = bookmark_gui._find_bookmark_by_id(2)
        assert bookmark is not None
        assert bookmark['title'] == 'Site 2'
        
        bookmark = bookmark_gui._find_bookmark_by_id(999)
        assert bookmark is None
    
    def test_validate_bookmark_data(self, bookmark_gui):
        """Test bookmark data validation"""
        valid_data = {'title': 'Test', 'url': 'https://test.com'}
        invalid_data1 = {'title': '', 'url': 'https://test.com'}
        invalid_data2 = {'title': 'Test', 'url': ''}
        invalid_data3 = {'title': '', 'url': ''}
        
        assert bookmark_gui._validate_bookmark_data(valid_data) is True
        assert bookmark_gui._validate_bookmark_data(invalid_data1) is False
        assert bookmark_gui._validate_bookmark_data(invalid_data2) is False
        assert bookmark_gui._validate_bookmark_data(invalid_data3) is False
    
    def test_get_import_file_path(self, bookmark_gui):
        """Test getting import file path"""
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ('/path/to/file.html', 'HTML Files (*.html)')
            
            result = bookmark_gui._get_import_file_path()
            assert result == '/path/to/file.html'
            
            # Test cancel
            mock_dialog.return_value = ('', '')
            result = bookmark_gui._get_import_file_path()
            assert result is None
    
    def test_load_bookmarks_from_file(self, bookmark_gui):
        """Test loading bookmarks from different file types"""
        # Test HTML file
        with patch('utilities.network.bookmark_manager.BookmarkImporter.import_from_html') as mock_import:
            mock_import.return_value = [{'title': 'Test', 'url': 'https://test.com'}]
            
            result = bookmark_gui._load_bookmarks_from_file('test.html')
            assert len(result) == 1
            mock_import.assert_called_once_with('test.html')
        
        # Test JSON file
        with patch('utilities.network.bookmark_manager.BookmarkImporter.import_from_json') as mock_import:
            mock_import.return_value = [{'title': 'Test', 'url': 'https://test.com'}]
            
            result = bookmark_gui._load_bookmarks_from_file('test.json')
            assert len(result) == 1
            mock_import.assert_called_once_with('test.json')
        
        # Test CSV file
        with patch('utilities.network.bookmark_manager.BookmarkImporter.import_from_csv') as mock_import:
            mock_import.return_value = [{'title': 'Test', 'url': 'https://test.com'}]
            
            result = bookmark_gui._load_bookmarks_from_file('test.csv')
            assert len(result) == 1
            mock_import.assert_called_once_with('test.csv')
        
        # Test unsupported file
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            result = bookmark_gui._load_bookmarks_from_file('test.txt')
            assert result is None
            mock_warning.assert_called_once()
    
    def test_add_imported_bookmarks(self, bookmark_gui):
        """Test adding imported bookmarks to database"""
        bookmarks = [
            {'title': 'Site 1', 'url': 'https://site1.com', 'description': '', 'tags': '', 'folder': 'Test'},
            {'title': '', 'url': 'https://site2.com', 'description': '', 'tags': '', 'folder': 'Test'},  # Invalid
            {'title': 'Site 3', 'url': 'https://site3.com', 'description': '', 'tags': '', 'folder': 'Test'}
        ]
        
        bookmark_gui.model.add_bookmark.side_effect = [True, False, True]
        
        imported_count = bookmark_gui._add_imported_bookmarks(bookmarks)
        assert imported_count == 2  # Only valid bookmarks with successful adds
    
    def test_search_bookmarks(self, bookmark_gui):
        """Test bookmark search functionality"""
        # Setup search box and combo
        bookmark_gui.search_box.setText("python")
        bookmark_gui.search_field_combo.setCurrentText("Title")
        
        search_results = [{'id': 1, 'title': 'Python Tutorial', 'url': 'https://python.org'}]
        bookmark_gui.model.search_bookmarks.return_value = search_results
        
        bookmark_gui.search_bookmarks()
        
        bookmark_gui.model.search_bookmarks.assert_called_once_with("python", "title")
    
    def test_filter_by_folder(self, bookmark_gui):
        """Test filtering bookmarks by folder"""
        bookmark_gui.current_bookmarks = [
            {'id': 1, 'folder': 'Work'},
            {'id': 2, 'folder': 'Personal'},
            {'id': 3, 'folder': 'Work'}
        ]
        
        # Mock QListWidgetItem
        mock_item = Mock()
        mock_item.text.return_value = "Work"
        
        bookmark_gui.filter_by_folder(mock_item)
        
        # Should call populate_table with filtered bookmarks
        assert bookmark_gui.bookmark_table.rowCount() == 2
    
    def test_filter_by_tag(self, bookmark_gui):
        """Test filtering bookmarks by tag"""
        bookmark_gui.current_bookmarks = [
            {'id': 1, 'tags': 'python,tutorial'},
            {'id': 2, 'tags': 'java,guide'},
            {'id': 3, 'tags': 'python,advanced'}
        ]
        
        # Mock QListWidgetItem
        mock_item = Mock()
        mock_item.text.return_value = "python"
        
        bookmark_gui.filter_by_tag(mock_item)
        
        # Should call populate_table with filtered bookmarks
        assert bookmark_gui.bookmark_table.rowCount() == 2


class TestBookmarkManagerIntegration:
    """Integration tests for complete bookmark management workflow"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "integration_test.db")
        yield db_path
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_complete_bookmark_lifecycle(self, temp_db_path):
        """Test complete bookmark CRUD operations"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        # Add bookmark
        success, message = model.add_bookmark(
            title="Integration Test Site",
            url="https://integration-test.com",
            description="Integration test description",
            tags="integration,test",
            folder="Test Folder"
        )
        assert success is True
        
        # Get all bookmarks
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 1
        bookmark_id = bookmarks[0]['id']
        
        # Update bookmark
        success = model.update_bookmark(
            bookmark_id=bookmark_id,
            title="Updated Integration Test",
            url="https://updated-integration-test.com",
            description="Updated description",
            tags="integration,test,updated",
            folder="Updated Folder"
        )
        assert success is True
        
        # Verify update
        bookmarks = model.get_all_bookmarks()
        assert bookmarks[0]['title'] == "Updated Integration Test"
        assert bookmarks[0]['url'] == "https://updated-integration-test.com"
        
        # Search bookmark
        search_results = model.search_bookmarks("integration", "all")
        assert len(search_results) == 1
        
        # Delete bookmark
        success = model.delete_bookmark(bookmark_id)
        assert success is True
        
        # Verify deletion
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 0
    
    def test_import_export_integration(self, temp_db_path):
        """Test import and export integration"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        # Add test bookmarks
        test_bookmarks = [
            ("Site 1", "https://site1.com", "Description 1", "tag1", "Folder1"),
            ("Site 2", "https://site2.com", "Description 2", "tag2", "Folder2")
        ]
        
        for title, url, desc, tags, folder in test_bookmarks:
            model.add_bookmark(title, url, desc, tags, folder)
        
        # Export to JSON
        bookmarks = model.get_all_bookmarks()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(bookmarks, export_file)
            assert success is True
            
            # Import from JSON to new database
            with tempfile.mkdtemp() as temp_dir:
                import_db_path = os.path.join(temp_dir, "import_test.db")
                import_model = BookmarkModel(import_db_path)
                
                imported_bookmarks = BookmarkImporter.import_from_json(export_file)
                assert len(imported_bookmarks) == 2
                
                # Add imported bookmarks
                for bookmark in imported_bookmarks:
                    import_model.add_bookmark(**bookmark)
                
                # Verify import
                final_bookmarks = import_model.get_all_bookmarks()
                assert len(final_bookmarks) == 2
                
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)


# Performance and edge case tests
class TestBookmarkManagerPerformance:
    """Performance and stress tests"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "performance_test.db")
        yield db_path
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_large_bookmark_set_performance(self, temp_db_path):
        """Test performance with large number of bookmarks"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        # Add many bookmarks
        num_bookmarks = 1000
        for i in range(num_bookmarks):
            success, _ = model.add_bookmark(
                title=f"Test Site {i}",
                url=f"https://test{i}.com",
                description=f"Description {i}",
                tags=f"tag{i % 10}",
                folder=f"Folder{i % 5}"
            )
            assert success is True
        
        # Test retrieval performance
        import time
        start_time = time.time()
        bookmarks = model.get_all_bookmarks()
        end_time = time.time()
        
        assert len(bookmarks) == num_bookmarks
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
        
        # Test search performance
        start_time = time.time()
        search_results = model.search_bookmarks("tag5", "tags")
        end_time = time.time()
        
        assert len(search_results) == 100  # Should find 100 bookmarks with tag5
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds


class TestBookmarkManagerEdgeCases:
    """Edge case and error condition tests"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "edge_case_test.db")
        yield db_path
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_unicode_bookmark_handling(self, temp_db_path):
        """Test handling of Unicode characters in bookmarks"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        unicode_bookmark = {
            'title': '测试网站 🌟',
            'url': 'https://测试.com',
            'description': 'Unicode description with émojis 🚀',
            'tags': 'unicode,测试,emoji',
            'folder': 'Special Characters'
        }
        
        success, _ = model.add_bookmark(**unicode_bookmark)
        assert success is True
        
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0]['title'] == '测试网站 🌟'
    
    def test_very_long_strings(self, temp_db_path):
        """Test handling of very long strings"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        long_string = "A" * 10000  # 10KB string
        
        success, _ = model.add_bookmark(
            title=long_string,
            url="https://example.com",
            description=long_string,
            tags=long_string
        )
        assert success is True
        
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 1
        assert len(bookmarks[0]['title']) == 10000
    
    def test_sql_injection_protection(self, temp_db_path):
        """Test protection against SQL injection"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', False):
            model = BookmarkModel(temp_db_path)
        
        # Attempt SQL injection in various fields
        malicious_inputs = [
            "'; DROP TABLE bookmarks; --",
            "' OR '1'='1",
            "'; INSERT INTO bookmarks VALUES (999, 'hacked', 'http://hacker.com'); --"
        ]
        
        for malicious_input in malicious_inputs:
            success, _ = model.add_bookmark(
                title=malicious_input,
                url="https://example.com",
                description=malicious_input,
                tags=malicious_input
            )
            # Should succeed but not execute malicious SQL
            assert success is True
        
        # Verify table still exists and contains expected data
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 3  # Only our legitimate test bookmarks
        
        # Verify table structure is intact
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'bookmarks' in tables
        conn.close()


# Test configuration and setup
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])