#!/usr/bin/env python3
"""
Advanced unit tests for bookmark_manager.py
Generated on: 2025-08-24
Test Framework: pytest

Extended test suite covering advanced scenarios and edge cases
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
from src.tools.network.bookmark_manager import (BookmarkExporter,
                                                BookmarkImporter,
                                                BookmarkModel)


class TestBookmarkModelAdvanced:
    """Advanced test suite for BookmarkModel class"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "advanced_test.db")
        yield db_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def bookmark_model(self, temp_db_path):
        """Create BookmarkModel instance with temporary database"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
            return model
    
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
    
    def test_search_bookmarks_by_title(self, bookmark_model):
        """Test searching bookmarks by title"""
        # Add test bookmarks
        bookmark_model.add_bookmark("Python Tutorial", "https://python.org")
        bookmark_model.add_bookmark("Java Guide", "https://java.com")
        bookmark_model.add_bookmark("Python Advanced", "https://advanced.com")
        
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
        bookmark_model.add_bookmark("Site 1", "https://site1.com", 
                                    tags="python,tutorial")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", 
                                    tags="java,guide")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", 
                                    tags="python,advanced")
        
        results = bookmark_model.search_bookmarks("python", "tags")
        assert len(results) == 2
    
    def test_search_bookmarks_no_results(self, bookmark_model):
        """Test search with no matching results"""
        bookmark_model.add_bookmark("Test Site", "https://example.com")
        
        results = bookmark_model.search_bookmarks("nonexistent", "all")
        assert len(results) == 0
    
    def test_get_all_tags(self, bookmark_model):
        """Test getting all unique tags"""
        # Add bookmarks with various tags
        bookmark_model.add_bookmark("Site 1", "https://site1.com", 
                                    tags="python,web,tutorial")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", 
                                    tags="java,programming")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", 
                                    tags="python,advanced")
        
        tags = bookmark_model.get_all_tags()
        expected_tags = ["advanced", "java", "programming", "python", 
                        "tutorial", "web"]
        assert sorted(tags) == expected_tags
    
    def test_get_all_folders(self, bookmark_model):
        """Test getting all unique folders"""
        bookmark_model.add_bookmark("Site 1", "https://site1.com", 
                                    folder="Development")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", 
                                    folder="Reference")
        bookmark_model.add_bookmark("Site 3", "https://site3.com", 
                                    folder="Development")
        
        folders = bookmark_model.get_all_folders()
        expected_folders = ["Development", "Reference"]
        assert sorted(folders) == expected_folders
    
    def test_get_tags_and_folders(self, bookmark_model):
        """Test getting tags and folders in single call"""
        bookmark_model.add_bookmark("Site 1", "https://site1.com", 
                                    tags="python,web", folder="Dev")
        bookmark_model.add_bookmark("Site 2", "https://site2.com", 
                                    tags="java", folder="Reference")
        
        tags, folders = bookmark_model.get_tags_and_folders()
        assert sorted(tags) == ["java", "python", "web"]
        assert sorted(folders) == ["Dev", "Reference"]
    
    def test_url_validation_protocol_addition(self, bookmark_model):
        """Test URL validation adds protocol when missing"""
        test_cases = [
            ("example.com", "https://example.com"),
            ("www.test.com", "https://www.test.com"),
            ("http://already.com", "http://already.com"),
            ("https://secure.com", "https://secure.com"),
            ("ftp://files.com", "ftp://files.com")
        ]
        
        for input_url, expected_url in test_cases:
            is_valid, result = bookmark_model._validate_url(input_url)
            assert is_valid
            assert result == expected_url
    
    def test_database_error_handling(self, temp_db_path):
        """Test database error handling scenarios"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
        
        # Simulate database corruption by deleting the file
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        
        # Attempt operations on corrupted database
        success, message = model.add_bookmark("Test", "https://test.com")
        assert success is False
        assert "Database error" in message


class TestBookmarkImporterAdvanced:
    """Advanced test suite for BookmarkImporter class"""
    
    def test_import_from_html_file_not_found(self):
        """Test HTML import with non-existent file"""
        bookmarks = BookmarkImporter.import_from_html("nonexistent.html")
        assert bookmarks == []
    
    def test_import_from_html_malformed(self):
        """Test HTML import with malformed content"""
        malformed_html = "<html><body>Not valid bookmark format</body></html>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                         delete=False) as f:
            f.write(malformed_html)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_html(temp_file)
            assert bookmarks == []  # Should handle gracefully
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            json.dump(nested_json, f)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert len(bookmarks) == 2
        finally:
            os.unlink(temp_file)
    
    def test_import_from_json_invalid_file(self):
        """Test JSON import with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_json(temp_file)
            assert bookmarks == []
        finally:
            os.unlink(temp_file)
    
    def test_import_from_csv_alternative_headers(self):
        """Test CSV import with alternative header names"""
        csv_content = """Title,URL,Description,Tags,Folder
Example Site,https://example.com,Example description,example,Test"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', 
                                         delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            bookmarks = BookmarkImporter.import_from_csv(temp_file)
            assert len(bookmarks) == 1
            assert bookmarks[0]['title'] == "Example Site"
        finally:
            os.unlink(temp_file)
    
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
    
    def test_create_bookmark_from_item_minimal(self):
        """Test creating bookmark with minimal data"""
        item = {"title": "Test", "url": "https://test.com"}
        
        bookmark = BookmarkImporter._create_bookmark_from_item(item, "Default")
        
        assert bookmark['title'] == "Test"
        assert bookmark['url'] == "https://test.com"
        assert bookmark['description'] == ""
        assert bookmark['tags'] == ""
        assert bookmark['folder'] == "Default"


class TestBookmarkExporterAdvanced:
    """Advanced test suite for BookmarkExporter class"""
    
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
                'folder': 'Different Folder',
                'created_date': '2025-08-24T10:05:00'
            }
        ]
    
    def test_export_to_html_folder_grouping(self, sample_bookmarks):
        """Test HTML export groups bookmarks by folder"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_html(
                sample_bookmarks, temp_file
            )
            assert success is True
            
            # Verify folder grouping in content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Test Folder" in content
                assert "Different Folder" in content
                assert "<H3>" in content  # Folder headers
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_json_serialization_error(self):
        """Test JSON export with non-serializable data"""
        # Create bookmarks with non-serializable data
        bad_bookmarks = [{'title': 'Test', 'date': datetime.now()}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(bad_bookmarks, temp_file)
            assert success is False
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_to_csv_write_error(self, sample_bookmarks):
        """Test CSV export with write error"""
        # Use invalid path that should cause write error
        invalid_path = "/invalid/path/test.csv"
        
        success = BookmarkExporter.export_to_csv(sample_bookmarks, invalid_path)
        assert success is False
    
    def test_export_empty_bookmark_list(self):
        """Test exporting empty bookmark list"""
        empty_bookmarks = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            temp_file = f.name
        
        try:
            success = BookmarkExporter.export_to_json(empty_bookmarks, temp_file)
            assert success is True
            
            # Verify empty array was written
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                assert content == []
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestBookmarkManagerEdgeCases:
    """Edge case tests for bookmark manager"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "edge_case_test.db")
        yield db_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_unicode_bookmark_handling(self, temp_db_path):
        """Test handling of Unicode characters in bookmarks"""
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
        
        unicode_bookmark = {
            'title': '测试网站 🌟',
            'url': 'https://example.com',  # Keep URL simple for validation
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
        with patch('utilities.network.bookmark_manager.LOGGING_AVAILABLE', 
                   False):
            model = BookmarkModel(temp_db_path)
        
        long_string = "A" * 1000  # 1KB string
        
        success, _ = model.add_bookmark(
            title=long_string,
            url="https://example.com",
            description=long_string,
            tags=long_string
        )
        assert success is True
        
        bookmarks = model.get_all_bookmarks()
        assert len(bookmarks) == 1
        assert len(bookmarks[0]['title']) == 1000


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])