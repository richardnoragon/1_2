#!/usr/bin/env python3
"""
Advanced Folders Settings Persistence Validation (Corrected)

Tests the settings persistence functionality with correct constructor parameters.
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


def test_basic_configuration_persistence():
    """Test basic configuration creation and persistence."""
    print("Testing basic configuration persistence...")
    
    # Create test configuration
    config = FolderConfiguration(
        name="Test Persistence",
        directory_paths=["C:\\Test\\Path"],
        description="Testing settings persistence"
    )
    
    print(f"  ✓ Created configuration: {config.name}")
    
    # Test serialization
    config_dict = config.to_dict()
    json_data = json.dumps(config_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized to JSON ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_config = FolderConfiguration.from_dict(parsed_dict)
    
    # Validate basic fields
    assert restored_config.name == config.name
    assert restored_config.directory_paths == config.directory_paths
    assert restored_config.description == config.description
    
    print("  ✓ Successfully restored configuration from JSON")
    return True


def test_file_based_persistence():
    """Test file-based persistence operations."""
    print("Testing file-based persistence...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        
        # Create configuration manager
        manager = FolderConfigurationManager()
        manager.config_file = config_file
        
        # Create test configuration
        config = FolderConfiguration(
            name="File Test",
            directory_paths=["C:\\File\\Test"],
            description="Testing file persistence"
        )
        
        # Test saving
        manager.save_configuration(config)
        print("  ✓ Saved configuration to file")
        
        # Verify file exists
        assert config_file.exists()
        
        # Test loading
        loaded_configs = manager.load_configurations()
        assert len(loaded_configs) == 1
        assert loaded_configs[0].name == config.name
        
        print("  ✓ Loaded configuration from file")
        
    return True


def test_search_parameters():
    """Test search parameters functionality."""
    print("Testing search parameters...")
    
    # Create search parameters
    search_params = SearchParameters(
        filename_pattern="*.txt",
        content_search="test query",
        case_sensitive=True,
        size_min=1024,
        size_max=1048576
    )
    
    # Test serialization
    params_dict = search_params.to_dict()
    json_data = json.dumps(params_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized search parameters ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_params = SearchParameters.from_dict(parsed_dict)
    
    # Validate fields
    assert restored_params.filename_pattern == search_params.filename_pattern
    assert restored_params.content_search == search_params.content_search
    assert restored_params.case_sensitive == search_params.case_sensitive
    assert restored_params.size_min == search_params.size_min
    assert restored_params.size_max == search_params.size_max
    
    print("  ✓ Successfully restored search parameters")
    return True


def test_folder_statistics():
    """Test folder statistics functionality."""
    print("Testing folder statistics...")
    
    # Create statistics
    stats = FolderStatistics(
        total_files=1000,
        total_size=50000000,
        last_scan_time=datetime.now(),
        scan_duration=12.5,
        file_type_breakdown={".txt": 500, ".pdf": 300, ".jpg": 200}
    )
    
    # Test serialization
    stats_dict = stats.to_dict()
    json_data = json.dumps(stats_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized statistics ({len(json_data)} bytes)")
    
    # Test deserialization
    parsed_dict = json.loads(json_data)
    restored_stats = FolderStatistics.from_dict(parsed_dict)
    
    # Validate fields
    assert restored_stats.total_files == stats.total_files
    assert restored_stats.total_size == stats.total_size
    assert restored_stats.file_type_breakdown == stats.file_type_breakdown
    assert abs(restored_stats.scan_duration - stats.scan_duration) < 0.01
    
    print("  ✓ Successfully restored statistics")
    return True


def test_configuration_with_all_components():
    """Test complete configuration with all components."""
    print("Testing complete configuration...")
    
    # Create configuration with all components
    config = FolderConfiguration(
        name="Complete Test",
        directory_paths=["C:\\Complete\\Test\\1", "C:\\Complete\\Test\\2"],
        description="Complete configuration test"
    )
    
    # Add search parameters
    config.search_parameters = SearchParameters(
        filename_pattern="*.py",
        content_search="import",
        include_extensions={".py", ".txt"},
        size_min=100
    )
    
    # Add statistics  
    config.statistics = FolderStatistics(
        total_files=250,
        total_size=5000000,
        file_type_breakdown={".py": 150, ".txt": 100}
    )
    
    # Test full serialization/deserialization cycle
    config_dict = config.to_dict()
    json_data = json.dumps(config_dict, indent=2, default=str)
    
    print(f"  ✓ Serialized complete configuration ({len(json_data)} bytes)")
    
    parsed_dict = json.loads(json_data)
    restored_config = FolderConfiguration.from_dict(parsed_dict)
    
    # Validate all components
    assert restored_config.name == config.name
    assert restored_config.directory_paths == config.directory_paths
    assert restored_config.search_parameters.filename_pattern == config.search_parameters.filename_pattern
    assert restored_config.statistics.total_files == config.statistics.total_files
    
    print("  ✓ Successfully restored complete configuration")
    return True


def main():
    """Run all settings persistence validation tests."""
    print("="*60)
    print("Advanced Folders - Settings Persistence Validation")
    print("="*60)
    
    tests = [
        test_basic_configuration_persistence,
        test_file_based_persistence,
        test_search_parameters,
        test_folder_statistics,
        test_configuration_with_all_components
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
        print("✓ All data models properly implemented")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)