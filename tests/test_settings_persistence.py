#!/usr/bin/env python3
"""
Advanced Folders Settings Persistence Validation

Tests the settings persistence functionality with real JSON operations
and ConfigManager integration patterns.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tools.file_management.advanced_folders.core.folder_configuration import (
    FolderConfiguration, FolderConfigurationManager, FolderStatistics,
    SearchParameters)


def test_json_persistence():
    """Test JSON serialization and deserialization."""
    print("Testing JSON persistence...")
    
    # Create test configuration
    config = FolderConfiguration(
        name="Test Persistence",
        directory_paths=["C:\\Test\\Path"],
        description="Testing settings persistence"
    )
    
    # Add search parameters
    config.search_parameters = SearchParameters(
        include_extensions={".txt", ".md"},
        size_min=1024,
        size_max=1048576,
        content_search="test query"
    )
    
    # Add statistics
    config.statistics = FolderStatistics(
        total_files=150,
        total_size=2048000,
        last_scan=datetime.now()
    )
    
    # Test serialization
    config_dict = config.to_dict()
    json_data = json.dumps(config_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized config to JSON ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_config = FolderConfiguration.from_dict(parsed_dict)
    
    # Validate restored data
    assert restored_config.name == config.name
    assert restored_config.path == config.path
    assert restored_config.description == config.description
    assert restored_config.enabled == config.enabled
    assert restored_config.search_parameters.file_extensions == config.search_parameters.file_extensions
    assert restored_config.search_parameters.size_min == config.search_parameters.size_min
    assert restored_config.statistics.total_files == config.statistics.total_files
    
    print("  ✓ Successfully restored config from JSON")
    return True


def test_file_persistence():
    """Test file-based persistence operations."""
    print("Testing file-based persistence...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        
        # Create configuration manager
        manager = FolderConfigurationManager()
        manager.config_file = config_file
        
        # Create multiple test configurations
        configs = []
        for i in range(3):
            config = FolderConfiguration(
                name=f"Test Config {i+1}",
                path=f"C:\\Test\\Path{i+1}",
                description=f"Test configuration {i+1}",
                enabled=i % 2 == 0  # Alternate enabled/disabled
            )
            configs.append(config)
        
        # Test saving configurations
        for config in configs:
            manager.save_configuration(config)
        
        print(f"  ✓ Saved {len(configs)} configurations to file")
        
        # Verify file was created
        assert config_file.exists()
        
        # Test loading configurations
        loaded_configs = manager.load_configurations()
        assert len(loaded_configs) == len(configs)
        
        print(f"  ✓ Loaded {len(loaded_configs)} configurations from file")
        
        # Test updating configuration
        original_config = loaded_configs[0]
        original_config.description = "Updated description"
        manager.update_configuration(original_config)
        
        # Verify update
        updated_configs = manager.load_configurations()
        updated_config = next(c for c in updated_configs if c.id == original_config.id)
        assert updated_config.description == "Updated description"
        
        print("  ✓ Successfully updated configuration")
        
        # Test deleting configuration
        config_to_delete = loaded_configs[1]
        manager.delete_configuration(config_to_delete.id)
        
        # Verify deletion
        remaining_configs = manager.load_configurations()
        assert len(remaining_configs) == len(configs) - 1
        assert not any(c.id == config_to_delete.id for c in remaining_configs)
        
        print("  ✓ Successfully deleted configuration")
        
    return True


def test_search_parameters_persistence():
    """Test persistence of complex search parameters."""
    print("Testing search parameters persistence...")
    
    # Create complex search parameters
    search_params = SearchParameters(
        path="C:\\Complex\\Search\\Path",
        file_extensions=[".pdf", ".docx", ".txt", ".md", ".py"],
        size_min=2048,
        size_max=10485760,
        modified_after=datetime(2023, 1, 1),
        modified_before=datetime(2024, 12, 31),
        content_search="complex search query with spaces",
        case_sensitive=True,
        include_hidden=False,
        recursive=True,
        max_depth=5
    )
    
    # Test serialization
    params_dict = search_params.to_dict()
    json_data = json.dumps(params_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized search parameters ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_params = SearchParameters.from_dict(parsed_dict)
    
    # Validate all fields
    assert restored_params.path == search_params.path
    assert restored_params.file_extensions == search_params.file_extensions
    assert restored_params.size_min == search_params.size_min
    assert restored_params.size_max == search_params.size_max
    assert restored_params.content_search == search_params.content_search
    assert restored_params.case_sensitive == search_params.case_sensitive
    assert restored_params.include_hidden == search_params.include_hidden
    assert restored_params.recursive == search_params.recursive
    assert restored_params.max_depth == search_params.max_depth
    
    print("  ✓ Successfully restored search parameters")
    return True


def test_statistics_persistence():
    """Test persistence of folder statistics."""
    print("Testing statistics persistence...")
    
    # Create detailed statistics
    stats = FolderStatistics(
        total_files=12345,
        total_size=987654321,
        average_file_size=80000,
        largest_file_size=15728640,
        smallest_file_size=512,
        file_types={
            ".txt": 5000,
            ".pdf": 2000,
            ".docx": 1500,
            ".jpg": 3845
        },
        last_scan=datetime.now(),
        scan_duration=45.67
    )
    
    # Test serialization
    stats_dict = stats.to_dict()
    json_data = json.dumps(stats_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized statistics ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_stats = FolderStatistics.from_dict(parsed_dict)
    
    # Validate statistics
    assert restored_stats.total_files == stats.total_files
    assert restored_stats.total_size == stats.total_size
    assert restored_stats.average_file_size == stats.average_file_size
    assert restored_stats.largest_file_size == stats.largest_file_size
    assert restored_stats.smallest_file_size == stats.smallest_file_size
    assert restored_stats.file_types == stats.file_types
    assert abs(restored_stats.scan_duration - stats.scan_duration) < 0.01
    
    print("  ✓ Successfully restored statistics")
    return True


def test_config_manager_integration_pattern():
    """Test the ConfigManager integration pattern (mock simulation)."""
    print("Testing ConfigManager integration pattern...")
    
    # Simulate ConfigManager structure
    mock_config_data = {
        'advanced_folders': {
            'configurations': []
        }
    }
    
    # Create test configuration
    config = FolderConfiguration(
        name="ConfigManager Test",
        path="C:\\ConfigManager\\Test",
        description="Testing ConfigManager integration"
    )
    
    # Simulate saving to ConfigManager
    config_list = [config.to_dict()]
    mock_config_data['advanced_folders']['configurations'] = config_list
    
    print("  ✓ Simulated save to ConfigManager")
    
    # Simulate loading from ConfigManager
    loaded_config_dicts = mock_config_data['advanced_folders']['configurations']
    loaded_configs = [FolderConfiguration.from_dict(d) for d in loaded_config_dicts]
    
    # Validate loaded configuration
    assert len(loaded_configs) == 1
    assert loaded_configs[0].name == config.name
    assert loaded_configs[0].path == config.path
    
    print("  ✓ Simulated load from ConfigManager")
    return True


def validate_json_format():
    """Validate that generated JSON follows expected format."""
    print("Validating JSON format compliance...")
    
    config = FolderConfiguration(
        name="Format Validation",
        path="C:\\Format\\Test",
        description="Validating JSON format"
    )
    
    # Generate JSON
    config_dict = config.to_dict()
    json_str = json.dumps(config_dict, indent=2)
    
    # Parse and validate structure
    parsed = json.loads(json_str)
    
    # Required fields
    required_fields = ['id', 'name', 'path', 'description', 'enabled', 'created_date']
    for field in required_fields:
        assert field in parsed, f"Missing required field: {field}"
    
    # Data types
    assert isinstance(parsed['name'], str)
    assert isinstance(parsed['path'], str)
    assert isinstance(parsed['enabled'], bool)
    
    print("  ✓ JSON format validation passed")
    return True


def main():
    """Run all settings persistence validation tests."""
    print("="*60)
    print("Advanced Folders - Settings Persistence Validation")
    print("="*60)
    
    tests = [
        test_json_persistence,
        test_file_persistence,
        test_search_parameters_persistence,
        test_statistics_persistence,
        test_config_manager_integration_pattern,
        validate_json_format
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("Settings Persistence Validation Summary")
    print("="*60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    
    if failed == 0:
        print("\n✓ All settings persistence tests completed successfully!")
        print("✓ JSON serialization/deserialization working correctly")
        print("✓ File-based persistence operations functional")
        print("✓ ConfigManager integration pattern validated")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)