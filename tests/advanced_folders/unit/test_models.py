"""
Unit tests for Advanced Folders models.

Tests the FolderConfiguration and SearchParameters models with
validation, serialization, and enterprise patterns.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.rfu.advanced_folders.exceptions.advanced_folders_exceptions import \
    ValidationException
from src.rfu.advanced_folders.models.folder_configuration import (
    DirectoryTarget, FolderConfiguration, PerformanceSettings,
    SecuritySettings)
from src.rfu.advanced_folders.models.search_parameters import (
    ContentSearchOptions, DateFilter, FileTypeFilter, SearchParameters,
    SizeFilter)


class TestDirectoryTarget:
    """Test DirectoryTarget dataclass."""
    
    def test_basic_creation(self):
        """Test basic DirectoryTarget creation."""
        target = DirectoryTarget(
            path=Path("/test/path"),
            name="Test Directory",
            description="A test directory"
        )
        
        assert target.path == Path("/test/path")
        assert target.name == "Test Directory"
        assert target.description == "A test directory"
    
    def test_optional_fields(self):
        """Test DirectoryTarget with optional fields."""
        target = DirectoryTarget(
            path=Path("/test/path"),
            name="Test Directory"
        )
        
        assert target.description is None
        assert target.priority == 1  # Default value
        assert target.enabled is True  # Default value
    
    def test_path_conversion(self):
        """Test automatic path conversion."""
        # String path should be converted to Path
        target = DirectoryTarget(
            path="/string/path",
            name="String Path"
        )
        
        assert isinstance(target.path, Path)
        assert str(target.path) == "/string/path"


class TestPerformanceSettings:
    """Test PerformanceSettings dataclass."""
    
    def test_default_values(self):
        """Test default performance settings."""
        settings = PerformanceSettings()
        
        assert settings.max_search_depth == 10
        assert settings.timeout_seconds == 30
        assert settings.max_results == 1000
        assert settings.enable_caching is True
        assert settings.cache_duration_minutes == 60
    
    def test_custom_values(self):
        """Test custom performance settings."""
        settings = PerformanceSettings(
            max_search_depth=5,
            timeout_seconds=60,
            max_results=500,
            enable_caching=False,
            cache_duration_minutes=30
        )
        
        assert settings.max_search_depth == 5
        assert settings.timeout_seconds == 60
        assert settings.max_results == 500
        assert settings.enable_caching is False
        assert settings.cache_duration_minutes == 30


class TestSecuritySettings:
    """Test SecuritySettings dataclass."""
    
    def test_default_values(self):
        """Test default security settings."""
        settings = SecuritySettings()
        
        assert settings.restrict_access is False
        assert settings.allowed_extensions == set()
        assert settings.blocked_paths == set()
        assert settings.require_confirmation is False
    
    def test_custom_values(self):
        """Test custom security settings."""
        settings = SecuritySettings(
            restrict_access=True,
            allowed_extensions={".txt", ".pdf"},
            blocked_paths={"/system", "/windows"},
            require_confirmation=True
        )
        
        assert settings.restrict_access is True
        assert settings.allowed_extensions == {".txt", ".pdf"}
        assert settings.blocked_paths == {"/system", "/windows"}
        assert settings.require_confirmation is True


class TestFolderConfiguration:
    """Test FolderConfiguration class."""
    
    def test_basic_creation(self):
        """Test basic FolderConfiguration creation."""
        target = DirectoryTarget(
            path=Path("/test"),
            name="Test Target"
        )
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target],
            enabled=True,
            description="Test configuration"
        )
        
        assert config.name == "Test Config"
        assert len(config.directory_targets) == 1
        assert config.enabled is True
        assert config.description == "Test configuration"
        assert config.id is not None
        assert isinstance(config.created_at, datetime)
    
    def test_validation_framework_integration(self):
        """Test validation framework integration."""
        # This should pass validation
        target = DirectoryTarget(
            path=Path("/valid/path"),
            name="Valid Target"
        )
        
        config = FolderConfiguration(
            name="Valid Config",
            directory_targets=[target]
        )
        
        # Validate should not raise exception
        config.validate()
    
    def test_validation_failure(self):
        """Test validation failure scenarios."""
        # Empty name should fail
        with pytest.raises(ValidationException):
            config = FolderConfiguration(
                name="",
                directory_targets=[]
            )
            config.validate()
    
    def test_to_dict_serialization(self):
        """Test dictionary serialization."""
        target = DirectoryTarget(
            path=Path("/test"),
            name="Test Target",
            description="Test description"
        )
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target],
            description="Test configuration"
        )
        
        data = config.to_dict()
        
        assert data["name"] == "Test Config"
        assert data["description"] == "Test configuration"
        assert len(data["directory_targets"]) == 1
        assert data["directory_targets"][0]["name"] == "Test Target"
        assert "id" in data
        assert "created_at" in data
    
    def test_from_dict_deserialization(self):
        """Test dictionary deserialization."""
        data = {
            "name": "Test Config",
            "directory_targets": [
                {
                    "path": "/test/path",
                    "name": "Test Target",
                    "description": "Test description"
                }
            ],
            "enabled": True,
            "description": "Test configuration"
        }
        
        config = FolderConfiguration.from_dict(data)
        
        assert config.name == "Test Config"
        assert len(config.directory_targets) == 1
        assert config.directory_targets[0].name == "Test Target"
        assert config.enabled is True
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        target = DirectoryTarget(
            path=Path("/test"),
            name="Test Target"
        )
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target]
        )
        
        json_str = config.to_json()
        assert isinstance(json_str, str)
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["name"] == "Test Config"
    
    def test_json_deserialization(self):
        """Test JSON deserialization."""
        json_data = {
            "name": "Test Config",
            "directory_targets": [
                {
                    "path": "/test/path",
                    "name": "Test Target"
                }
            ],
            "enabled": True
        }
        
        json_str = json.dumps(json_data)
        config = FolderConfiguration.from_json(json_str)
        
        assert config.name == "Test Config"
        assert len(config.directory_targets) == 1
    
    def test_update_metadata(self):
        """Test metadata update."""
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[]
        )
        
        original_updated_at = config.updated_at
        
        # Update metadata
        config.update_metadata()
        
        assert config.updated_at > original_updated_at
    
    def test_add_directory_target(self):
        """Test adding directory target."""
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[]
        )
        
        target = DirectoryTarget(
            path=Path("/new/target"),
            name="New Target"
        )
        
        config.add_directory_target(target)
        
        assert len(config.directory_targets) == 1
        assert config.directory_targets[0].name == "New Target"
    
    def test_remove_directory_target(self):
        """Test removing directory target."""
        target1 = DirectoryTarget(path=Path("/target1"), name="Target 1")
        target2 = DirectoryTarget(path=Path("/target2"), name="Target 2")
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target1, target2]
        )
        
        config.remove_directory_target("Target 1")
        
        assert len(config.directory_targets) == 1
        assert config.directory_targets[0].name == "Target 2"
    
    def test_get_target_by_name(self):
        """Test getting target by name."""
        target = DirectoryTarget(path=Path("/test"), name="Test Target")
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target]
        )
        
        found_target = config.get_target_by_name("Test Target")
        assert found_target is not None
        assert found_target.name == "Test Target"
        
        # Non-existent target
        not_found = config.get_target_by_name("Non-existent")
        assert not_found is None


class TestFileTypeFilter:
    """Test FileTypeFilter dataclass."""
    
    def test_basic_creation(self):
        """Test basic FileTypeFilter creation."""
        filter_obj = FileTypeFilter(
            include_extensions={".txt", ".pdf"},
            exclude_extensions={".tmp"},
            include_mime_types={"text/plain"},
            exclude_mime_types={"application/octet-stream"}
        )
        
        assert filter_obj.include_extensions == {".txt", ".pdf"}
        assert filter_obj.exclude_extensions == {".tmp"}
        assert filter_obj.include_mime_types == {"text/plain"}
        assert filter_obj.exclude_mime_types == {"application/octet-stream"}
    
    def test_default_values(self):
        """Test default values."""
        filter_obj = FileTypeFilter()
        
        assert filter_obj.include_extensions == set()
        assert filter_obj.exclude_extensions == set()
        assert filter_obj.include_mime_types == set()
        assert filter_obj.exclude_mime_types == set()


class TestSizeFilter:
    """Test SizeFilter dataclass."""
    
    def test_basic_creation(self):
        """Test basic SizeFilter creation."""
        filter_obj = SizeFilter(
            min_size_bytes=1024,
            max_size_bytes=1048576
        )
        
        assert filter_obj.min_size_bytes == 1024
        assert filter_obj.max_size_bytes == 1048576
    
    def test_default_values(self):
        """Test default values."""
        filter_obj = SizeFilter()
        
        assert filter_obj.min_size_bytes is None
        assert filter_obj.max_size_bytes is None


class TestDateFilter:
    """Test DateFilter dataclass."""
    
    def test_basic_creation(self):
        """Test basic DateFilter creation."""
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
        
        filter_obj = DateFilter(
            created_after=start_date,
            created_before=end_date,
            modified_after=start_date,
            modified_before=end_date
        )
        
        assert filter_obj.created_after == start_date
        assert filter_obj.created_before == end_date
        assert filter_obj.modified_after == start_date
        assert filter_obj.modified_before == end_date
    
    def test_default_values(self):
        """Test default values."""
        filter_obj = DateFilter()
        
        assert filter_obj.created_after is None
        assert filter_obj.created_before is None
        assert filter_obj.modified_after is None
        assert filter_obj.modified_before is None


class TestContentSearchOptions:
    """Test ContentSearchOptions dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        options = ContentSearchOptions()
        
        assert options.search_text is True
        assert options.search_metadata is False
        assert options.case_sensitive is False
        assert options.use_regex is False
        assert options.encoding == "utf-8"
    
    def test_custom_values(self):
        """Test custom values."""
        options = ContentSearchOptions(
            search_text=False,
            search_metadata=True,
            case_sensitive=True,
            use_regex=True,
            encoding="latin-1"
        )
        
        assert options.search_text is False
        assert options.search_metadata is True
        assert options.case_sensitive is True
        assert options.use_regex is True
        assert options.encoding == "latin-1"


class TestSearchParameters:
    """Test SearchParameters class."""
    
    def test_basic_creation(self):
        """Test basic SearchParameters creation."""
        params = SearchParameters(
            query="test query",
            max_results=100,
            timeout_seconds=30
        )
        
        assert params.query == "test query"
        assert params.max_results == 100
        assert params.timeout_seconds == 30
        assert params.id is not None
        assert isinstance(params.created_at, datetime)
    
    def test_with_filters(self):
        """Test SearchParameters with filters."""
        file_filter = FileTypeFilter(include_extensions={".txt"})
        size_filter = SizeFilter(min_size_bytes=1024)
        date_filter = DateFilter(
            created_after=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        content_options = ContentSearchOptions(case_sensitive=True)
        
        params = SearchParameters(
            query="test",
            file_type_filter=file_filter,
            size_filter=size_filter,
            date_filter=date_filter,
            content_search_options=content_options
        )
        
        assert params.file_type_filter == file_filter
        assert params.size_filter == size_filter
        assert params.date_filter == date_filter
        assert params.content_search_options == content_options
    
    def test_validation(self):
        """Test SearchParameters validation."""
        # Valid parameters
        params = SearchParameters(query="valid query")
        params.validate()  # Should not raise
        
        # Invalid parameters
        with pytest.raises(ValidationException):
            invalid_params = SearchParameters(query="")
            invalid_params.validate()
    
    def test_to_dict_serialization(self):
        """Test dictionary serialization."""
        params = SearchParameters(
            query="test query",
            max_results=50
        )
        
        data = params.to_dict()
        
        assert data["query"] == "test query"
        assert data["max_results"] == 50
        assert "id" in data
        assert "created_at" in data
    
    def test_from_dict_deserialization(self):
        """Test dictionary deserialization."""
        data = {
            "query": "test query",
            "max_results": 75,
            "timeout_seconds": 45
        }
        
        params = SearchParameters.from_dict(data)
        
        assert params.query == "test query"
        assert params.max_results == 75
        assert params.timeout_seconds == 45
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        params = SearchParameters(query="json test")
        
        json_str = params.to_json()
        assert isinstance(json_str, str)
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["query"] == "json test"
    
    def test_json_deserialization(self):
        """Test JSON deserialization."""
        json_data = {
            "query": "json test",
            "max_results": 200
        }
        
        json_str = json.dumps(json_data)
        params = SearchParameters.from_json(json_str)
        
        assert params.query == "json test"
        assert params.max_results == 200
    
    def test_build_query_dict(self):
        """Test query dictionary building."""
        file_filter = FileTypeFilter(include_extensions={".txt", ".pdf"})
        size_filter = SizeFilter(min_size_bytes=1024, max_size_bytes=1048576)
        
        params = SearchParameters(
            query="test",
            file_type_filter=file_filter,
            size_filter=size_filter
        )
        
        query_dict = params.build_query_dict()
        
        assert query_dict["query"] == "test"
        assert "file_type_filter" in query_dict
        assert "size_filter" in query_dict
    
    def test_update_metadata(self):
        """Test metadata update."""
        params = SearchParameters(query="test")
        original_updated_at = params.updated_at
        
        params.update_metadata()
        
        assert params.updated_at > original_updated_at


class TestModelEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_json_deserialization(self):
        """Test invalid JSON deserialization."""
        with pytest.raises(json.JSONDecodeError):
            FolderConfiguration.from_json("invalid json")
    
    def test_missing_required_fields_in_dict(self):
        """Test missing required fields in dictionary."""
        # Missing name field
        with pytest.raises((KeyError, TypeError)):
            FolderConfiguration.from_dict({
                "directory_targets": []
            })
    
    def test_large_configuration(self):
        """Test handling of large configurations."""
        # Create many directory targets
        targets = [
            DirectoryTarget(
                path=Path(f"/test/path_{i}"),
                name=f"Target {i}"
            )
            for i in range(1000)
        ]
        
        config = FolderConfiguration(
            name="Large Config",
            directory_targets=targets
        )
        
        assert len(config.directory_targets) == 1000
        
        # Serialization should work
        data = config.to_dict()
        assert len(data["directory_targets"]) == 1000
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        config = FolderConfiguration(
            name="測試配置",  # Chinese characters
            directory_targets=[
                DirectoryTarget(
                    path=Path("/test/测试路径"),
                    name="测试目标",
                    description="這是一個測試配置"
                )
            ],
            description="配置説明"
        )
        
        # Should handle Unicode in serialization
        json_str = config.to_json()
        restored_config = FolderConfiguration.from_json(json_str)
        
        assert restored_config.name == "測試配置"
        assert restored_config.directory_targets[0].name == "测试目标"
    
    def test_datetime_serialization(self):
        """Test datetime serialization/deserialization."""
        config = FolderConfiguration(
            name="DateTime Test",
            directory_targets=[]
        )
        
        # Serialize and deserialize
        json_str = config.to_json()
        restored_config = FolderConfiguration.from_json(json_str)
        
        # Datetime should be preserved (within reasonable precision)
        time_diff = abs(
            (config.created_at - restored_config.created_at).total_seconds()
        )
        assert time_diff < 1.0  # Less than 1 second difference


if __name__ == "__main__":
    pytest.main([__file__])