"""Unit tests for Advanced Folders core models."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.advanced_folders.core.folder_models import (
    ConfigurationManager, DateTimeRange, FileMetadata, FolderConfiguration,
    FolderType, LogLevel, SearchParameter, SearchType, SizeRange, SortBy,
    ValidationResult)


class TestFolderConfiguration:
    """Test cases for FolderConfiguration dataclass."""
    
    @pytest.mark.unit
    def test_folder_configuration_creation(self):
        """Test basic folder configuration creation."""
        config = FolderConfiguration(
            name="Test Folder",
            path="/test/path",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        assert config.name == "Test Folder"
        assert config.path == "/test/path"
        assert config.folder_type == FolderType.SMART
        assert config.auto_organize is True
        assert config.priority == 1
        assert config.description == ""
        assert config.created_at is not None
        assert config.updated_at is not None
    
    @pytest.mark.unit
    def test_folder_configuration_validation_valid(self):
        """Test validation of valid folder configuration."""
        config = FolderConfiguration(
            name="Valid Folder",
            path="/valid/path",
            folder_type=FolderType.MONITORED,
            auto_organize=False,
            priority=5
        )
        
        result = config.validate()
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.unit
    def test_folder_configuration_validation_invalid_name(self):
        """Test validation with invalid name."""
        config = FolderConfiguration(
            name="",  # Empty name
            path="/valid/path",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        result = config.validate()
        assert result.is_valid is False
        assert "Name cannot be empty" in result.errors
    
    @pytest.mark.unit
    def test_folder_configuration_validation_invalid_path(self):
        """Test validation with invalid path."""
        config = FolderConfiguration(
            name="Valid Name",
            path="",  # Empty path
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        result = config.validate()
        assert result.is_valid is False
        assert "Path cannot be empty" in result.errors
    
    @pytest.mark.unit
    def test_folder_configuration_validation_invalid_priority(self):
        """Test validation with invalid priority."""
        config = FolderConfiguration(
            name="Valid Name",
            path="/valid/path",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=0  # Invalid priority
        )
        
        result = config.validate()
        assert result.is_valid is False
        assert "Priority must be between 1 and 10" in result.errors
    
    @pytest.mark.unit
    def test_folder_configuration_serialization(self):
        """Test JSON serialization and deserialization."""
        config = FolderConfiguration(
            name="Serialization Test",
            path="/test/serialization",
            folder_type=FolderType.ARCHIVE,
            auto_organize=True,
            priority=3,
            description="Test description"
        )
        
        # Test to_dict
        config_dict = config.to_dict()
        assert config_dict['name'] == "Serialization Test"
        assert config_dict['folder_type'] == "ARCHIVE"
        
        # Test from_dict
        restored_config = FolderConfiguration.from_dict(config_dict)
        assert restored_config.name == config.name
        assert restored_config.path == config.path
        assert restored_config.folder_type == config.folder_type
    
    @pytest.mark.unit
    def test_folder_configuration_update_timestamp(self):
        """Test that updated_at timestamp changes when configuration is modified."""
        config = FolderConfiguration(
            name="Timestamp Test",
            path="/test/timestamp",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        original_updated_at = config.updated_at
        
        # Simulate time passing
        import time
        time.sleep(0.001)
        
        config.update_timestamp()
        assert config.updated_at > original_updated_at


class TestSearchParameter:
    """Test cases for SearchParameter dataclass."""
    
    @pytest.mark.unit
    def test_search_parameter_creation(self):
        """Test basic search parameter creation."""
        search_param = SearchParameter(
            folder_config_id=1,
            name="Test Search",
            pattern="*.txt",
            case_sensitive=False,
            include_subdirs=True
        )
        
        assert search_param.folder_config_id == 1
        assert search_param.name == "Test Search"
        assert search_param.pattern == "*.txt"
        assert search_param.case_sensitive is False
        assert search_param.include_subdirs is True
        assert search_param.created_at is not None
    
    @pytest.mark.unit
    def test_search_parameter_validation_valid(self):
        """Test validation of valid search parameter."""
        search_param = SearchParameter(
            folder_config_id=1,
            name="Valid Search",
            pattern="*.pdf",
            case_sensitive=True,
            include_subdirs=False
        )
        
        result = search_param.validate()
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.unit
    def test_search_parameter_validation_invalid(self):
        """Test validation with invalid parameters."""
        search_param = SearchParameter(
            folder_config_id=0,  # Invalid ID
            name="",  # Empty name
            pattern="",  # Empty pattern
            case_sensitive=False,
            include_subdirs=True
        )
        
        result = search_param.validate()
        assert result.is_valid is False
        assert "Folder config ID must be positive" in result.errors
        assert "Name cannot be empty" in result.errors
        assert "Pattern cannot be empty" in result.errors
    
    @pytest.mark.unit
    def test_search_parameter_serialization(self):
        """Test JSON serialization and deserialization."""
        search_param = SearchParameter(
            folder_config_id=5,
            name="Serialization Test",
            pattern="*.json",
            case_sensitive=True,
            include_subdirs=False,
            min_size=1024,
            max_size=1024*1024
        )
        
        # Test to_dict
        param_dict = search_param.to_dict()
        assert param_dict['folder_config_id'] == 5
        assert param_dict['name'] == "Serialization Test"
        
        # Test from_dict
        restored_param = SearchParameter.from_dict(param_dict)
        assert restored_param.folder_config_id == search_param.folder_config_id
        assert restored_param.name == search_param.name
        assert restored_param.pattern == search_param.pattern


class TestFileMetadata:
    """Test cases for FileMetadata dataclass."""
    
    @pytest.mark.unit
    def test_file_metadata_creation(self):
        """Test basic file metadata creation."""
        metadata = FileMetadata(
            folder_config_id=1,
            file_path="/test/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_type="txt",
            checksum="abc123"
        )
        
        assert metadata.folder_config_id == 1
        assert metadata.file_path == "/test/file.txt"
        assert metadata.file_name == "file.txt"
        assert metadata.file_size == 1024
        assert metadata.file_type == "txt"
        assert metadata.checksum == "abc123"
        assert metadata.created_at is not None
    
    @pytest.mark.unit
    def test_file_metadata_validation_valid(self):
        """Test validation of valid file metadata."""
        metadata = FileMetadata(
            folder_config_id=1,
            file_path="/valid/path/file.pdf",
            file_name="file.pdf",
            file_size=2048,
            file_type="pdf",
            checksum="def456"
        )
        
        result = metadata.validate()
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.unit
    def test_file_metadata_validation_invalid(self):
        """Test validation with invalid metadata."""
        metadata = FileMetadata(
            folder_config_id=0,  # Invalid ID
            file_path="",  # Empty path
            file_name="",  # Empty name
            file_size=-1,  # Invalid size
            file_type="",  # Empty type
            checksum=""  # Empty checksum
        )
        
        result = metadata.validate()
        assert result.is_valid is False
        assert "Folder config ID must be positive" in result.errors
        assert "File path cannot be empty" in result.errors
        assert "File name cannot be empty" in result.errors
        assert "File size cannot be negative" in result.errors
        assert "File type cannot be empty" in result.errors
        assert "Checksum cannot be empty" in result.errors
    
    @pytest.mark.unit
    def test_file_metadata_human_readable_size(self):
        """Test human readable size formatting."""
        # Test bytes
        metadata = FileMetadata(
            folder_config_id=1,
            file_path="/test/small.txt",
            file_name="small.txt",
            file_size=512,
            file_type="txt",
            checksum="abc"
        )
        assert metadata.get_human_readable_size() == "512 B"
        
        # Test KB
        metadata.file_size = 1536  # 1.5 KB
        assert metadata.get_human_readable_size() == "1.5 KB"
        
        # Test MB
        metadata.file_size = 1572864  # 1.5 MB
        assert metadata.get_human_readable_size() == "1.5 MB"
        
        # Test GB
        metadata.file_size = 1610612736  # 1.5 GB
        assert metadata.get_human_readable_size() == "1.5 GB"


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    @pytest.mark.unit
    def test_configuration_manager_creation(self, configuration_manager):
        """Test configuration manager creation."""
        assert configuration_manager is not None
        assert configuration_manager.config_path.exists()
    
    @pytest.mark.unit
    def test_set_and_get_setting(self, configuration_manager):
        """Test setting and getting configuration values."""
        # Set a setting
        configuration_manager.set_setting("test_section", "test_key", "test_value")
        
        # Get the setting
        value = configuration_manager.get_setting("test_section", "test_key")
        assert value == "test_value"
    
    @pytest.mark.unit
    def test_get_setting_with_default(self, configuration_manager):
        """Test getting setting with default value."""
        # Get non-existent setting with default
        value = configuration_manager.get_setting(
            "non_existent_section", 
            "non_existent_key", 
            "default_value"
        )
        assert value == "default_value"
    
    @pytest.mark.unit
    def test_remove_setting(self, configuration_manager):
        """Test removing a setting."""
        # Set a setting first
        configuration_manager.set_setting("temp_section", "temp_key", "temp_value")
        
        # Verify it exists
        value = configuration_manager.get_setting("temp_section", "temp_key")
        assert value == "temp_value"
        
        # Remove the setting
        result = configuration_manager.remove_setting("temp_section", "temp_key")
        assert result is True
        
        # Verify it's gone
        value = configuration_manager.get_setting("temp_section", "temp_key", "not_found")
        assert value == "not_found"
    
    @pytest.mark.unit
    def test_backup_and_restore(self, configuration_manager):
        """Test configuration backup and restore."""
        # Set some settings
        configuration_manager.set_setting("backup_test", "key1", "value1")
        configuration_manager.set_setting("backup_test", "key2", "value2")
        
        # Create backup
        backup_path = configuration_manager.create_backup()
        assert backup_path.exists()
        
        # Modify configuration
        configuration_manager.set_setting("backup_test", "key1", "modified_value")
        
        # Restore from backup
        success = configuration_manager.restore_from_backup(backup_path)
        assert success is True
        
        # Verify restoration
        value = configuration_manager.get_setting("backup_test", "key1")
        assert value == "value1"
        
        # Clean up
        backup_path.unlink()
    
    @pytest.mark.unit
    def test_configuration_validation(self, configuration_manager):
        """Test configuration validation."""
        # Set valid configuration
        configuration_manager.set_setting("validation_test", "string_setting", "valid_string")
        configuration_manager.set_setting("validation_test", "number_setting", 42)
        configuration_manager.set_setting("validation_test", "bool_setting", True)
        
        # Validate configuration
        result = configuration_manager.validate_configuration()
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestEnums:
    """Test cases for enum classes."""
    
    @pytest.mark.unit
    def test_folder_type_enum(self):
        """Test FolderType enum values."""
        assert FolderType.SMART == "SMART"
        assert FolderType.MONITORED == "MONITORED"
        assert FolderType.ARCHIVE == "ARCHIVE"
        assert FolderType.TEMPLATE == "TEMPLATE"
        assert FolderType.VIRTUAL == "VIRTUAL"
    
    @pytest.mark.unit
    def test_log_level_enum(self):
        """Test LogLevel enum values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"
    
    @pytest.mark.unit
    def test_sort_by_enum(self):
        """Test SortBy enum values."""
        assert SortBy.NAME == "NAME"
        assert SortBy.SIZE == "SIZE"
        assert SortBy.DATE_MODIFIED == "DATE_MODIFIED"
        assert SortBy.DATE_CREATED == "DATE_CREATED"
        assert SortBy.TYPE == "TYPE"
    
    @pytest.mark.unit
    def test_search_type_enum(self):
        """Test SearchType enum values."""
        assert SearchType.PATTERN == "PATTERN"
        assert SearchType.CONTENT == "CONTENT"
        assert SearchType.METADATA == "METADATA"
        assert SearchType.ADVANCED == "ADVANCED"


class TestUtilityClasses:
    """Test cases for utility classes."""
    
    @pytest.mark.unit
    def test_datetime_range_creation(self):
        """Test DateTimeRange creation and validation."""
        start_time = datetime(2023, 1, 1)
        end_time = datetime(2023, 12, 31)
        
        dt_range = DateTimeRange(start_time, end_time)
        assert dt_range.start == start_time
        assert dt_range.end == end_time
        
        # Test validation
        result = dt_range.validate()
        assert result.is_valid is True
    
    @pytest.mark.unit
    def test_datetime_range_invalid(self):
        """Test DateTimeRange with invalid range."""
        start_time = datetime(2023, 12, 31)
        end_time = datetime(2023, 1, 1)  # End before start
        
        dt_range = DateTimeRange(start_time, end_time)
        result = dt_range.validate()
        assert result.is_valid is False
        assert "Start time must be before end time" in result.errors
    
    @pytest.mark.unit
    def test_size_range_creation(self):
        """Test SizeRange creation and validation."""
        size_range = SizeRange(min_size=1024, max_size=1024*1024)
        assert size_range.min_size == 1024
        assert size_range.max_size == 1024*1024
        
        # Test validation
        result = size_range.validate()
        assert result.is_valid is True
    
    @pytest.mark.unit
    def test_size_range_invalid(self):
        """Test SizeRange with invalid range."""
        size_range = SizeRange(min_size=1024*1024, max_size=1024)  # Min > Max
        result = size_range.validate()
        assert result.is_valid is False
        assert "Minimum size must be less than maximum size" in result.errors
    
    @pytest.mark.unit
    def test_validation_result(self):
        """Test ValidationResult class."""
        # Valid result
        valid_result = ValidationResult(is_valid=True, errors=[])
        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0
        
        # Invalid result
        invalid_result = ValidationResult(
            is_valid=False, 
            errors=["Error 1", "Error 2"]
        )
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) == 2
        assert "Error 1" in invalid_result.errors
        assert "Error 2" in invalid_result.errors