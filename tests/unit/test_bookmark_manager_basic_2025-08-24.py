#!/usr/bin/env python3
"""
Comprehensive unit tests for bookmark_manager.py
Generated on: 2025-08-24
Test Framework: pytest

Basic test suite covering core functionality of bookmark_manager.py
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
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

# Import the modules to test
from tools.network.bookmark_manager import (BookmarkExporter,
                                                BookmarkImporter,
                                                BookmarkModel)

# Test constants
TEST_DB_NAME = "test_bookmarks.db"


class TestBookmarkModelBasic:
    """Basic test suite for BookmarkModel class"""
    
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
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
            return model
    
    def test_database_initialization(self, temp_db_path):
        """Test database initialization creates required tables"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            BookmarkModel(temp_db_path)
            
        # Verify database file exists
        assert os.path.exists(temp_db_path)
        
        # Verify tables exist
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check bookmarks table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND "
            "name='bookmarks'"
        )
        assert cursor.fetchone() is not None
        
        # Check tags table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND "
            "name='tags'"
        )
        assert cursor.fetchone() is not None
        
        # Check folders table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND "
            "name='folders'"
        )
        assert cursor.fetchone() is not None
        
        conn.close()
    
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
    
    def test_get_all_bookmarks_empty(self, bookmark_model):
        """Test getting bookmarks from empty database"""
        bookmarks = bookmark_model.get_all_bookmarks()
        assert bookmarks == []
    
    def test_get_all_bookmarks_populated(self, bookmark_model):
        """Test getting bookmarks from populated database"""
        # Add test bookmarks
        test_bookmarks = [
            ("Site 1", "https://example1.com", "Desc 1", "tag1", "Folder1"),
            ("Site 2", "https://example2.com", "Desc 2", "tag2", "Folder2"),
            ("Site 3", "https://example3.com", "Desc 3", "tag3", "Folder1")
        ]
        
        for title, url, desc, tags, folder in test_bookmarks:
            bookmark_model.add_bookmark(title, url, desc, tags, folder)
        
        bookmarks = bookmark_model.get_all_bookmarks()
        assert len(bookmarks) == 3
        
        # Verify bookmark structure
        for bookmark in bookmarks:
            required_fields = [
                'id', 'title', 'url', 'description', 'tags', 'folder',
                'created_date', 'modified_date', 'visit_count', 'favorite'
            ]
            for field in required_fields:
                assert field in bookmark
    
    def test_url_validation_valid_cases(self, bookmark_model):
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
            assert result.startswith(
                ('http://', 'https://', 'ftp://')
            ), f"URL should have protocol: {result}"
    
    def test_url_validation_invalid_cases(self, bookmark_model):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "",
            "   ",
            "not a url",
            "http://",
            "https://",
            "http:// invalid space.com",
            "https://example<>.com",
            'http://exam"ple.com'
        ]
        
        for url in invalid_urls:
            is_valid, error_msg = bookmark_model._validate_url(url)
            assert not is_valid, f"URL should be invalid: {url}"
            assert isinstance(error_msg, str), "Error message should be string"


class TestBookmarkImporterBasic:
    """Basic test suite for BookmarkImporter class"""
    
    def test_import_from_html_success(self):
        """Test successful HTML import"""
        html_content = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                         delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_html(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
            assert bookmarks[0]['folder'] == "Test Folder"
        finally:
            os.unlink(temp_file)
    
    def test_import_from_json_success(self):
        """Test successful JSON import"""
        json_content = [
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            json.dump(json_content, f)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
        finally:
            os.unlink(temp_file)
    
    def test_import_from_csv_success(self):
        """Test successful CSV import"""
        csv_content = """title,url,description,tags,folder
Example Site,https://example.com,Example description,example,Test
Test Site,https://test.com,Test description,test,Test"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', 
                                         delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_csv(temp_file)
            assert len(bookmarks) == 2
            assert bookmarks[0]['title'] == "Example Site"
            assert bookmarks[0]['url'] == "https://example.com"
        finally:
            os.unlink(temp_file)


class TestBookmarkExporterBasic:
    """Basic test suite for BookmarkExporter class"""
    
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_html(
                sample_bookmarks, temp_file
            )
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
    
    def test_export_to_json_success(self, sample_bookmarks):
        """Test successful JSON export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(
                sample_bookmarks, temp_file
            )
            assert success is True
            
            # Verify file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
                assert len(exported_data) == 2
                assert exported_data[0]['title'] == 'Example Site'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_csv_success(self, sample_bookmarks):
        """Test successful CSV export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_csv(
                sample_bookmarks, temp_file
            )
            assert success is True
            
            # Verify file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                header = "title,url,description,tags,folder,created_date"
                assert header in content
                assert "Example Site" in content
                assert "https://example.com" in content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBookmarkIntegration:
    """Integration tests for bookmark management workflow"""
    
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
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
        
        # Add bookmark
        success, _ = model.add_bookmark(
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


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])