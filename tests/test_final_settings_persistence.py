#!/usr/bin/env python3
"""
Advanced Folders Settings Persistence Final Validation

Tests the settings persistence functionality using the correct API methods.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utilities.file_management.advanced_folders.core.folder_configuration import (
    FolderConfiguration, FolderConfigurationManager, FolderStatistics,
    SearchParameters)


def test_configuration_manager_api():
    """Test FolderConfigurationManager API functionality."""
    print("Testing FolderConfigurationManager API...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create manager
        manager = FolderConfigurationManager()
        manager._config_file = Path(temp_dir) / "test_config.json"
        
        # Test creating folder
        config = manager.create_folder(
            name="API Test Folder",
            description="Testing the manager API",
            directory_paths=["C:\\API\\Test"]
        )
        
        print(f"  ✓ Created folder configuration: {config.name}")
        print(f"  ✓ Folder ID: {config.folder_id}")
        
        # Test retrieving folder
        retrieved_config = manager.get_folder(config.folder_id)
        assert retrieved_config is not None
        assert retrieved_config.name == config.name
        
        print("  ✓ Successfully retrieved folder configuration")
        
        # Test updating folder
        success = manager.update_folder(
            config.folder_id,
            name="Updated API Test Folder",
            description="Updated description"
        )
        assert success
        
        updated_config = manager.get_folder(config.folder_id)
        assert updated_config.name == "Updated API Test Folder"
        
        print("  ✓ Successfully updated folder configuration")
        
        # Test listing folders
        all_folders = manager.list_folders()
        assert len(all_folders) == 1
        assert all_folders[0].folder_id == config.folder_id
        
        print("  ✓ Successfully listed folder configurations")
        
        # Test deleting folder
        success = manager.delete_folder(config.folder_id)
        assert success
        
        remaining_folders = manager.list_folders()
        assert len(remaining_folders) == 0
        
        print("  ✓ Successfully deleted folder configuration")
        
    return True


def test_persistence_workflow():
    """Test complete persistence workflow."""
    print("Testing complete persistence workflow...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "workflow_test.json"
        
        # Create first manager and add configurations
        manager1 = FolderConfigurationManager()
        manager1._config_file = config_file
        
        # Create multiple configurations
        config1 = manager1.create_folder(
            name="Workflow Test 1",
            description="First test configuration",
            directory_paths=["C:\\Test\\1"]
        )
        
        config2 = manager1.create_folder(
            name="Workflow Test 2", 
            description="Second test configuration",
            directory_paths=["C:\\Test\\2", "C:\\Test\\3"]
        )
        
        print(f"  ✓ Created {len(manager1.list_folders())} configurations")
        
        # Save configurations
        success = manager1.save_configurations()
        assert success
        assert config_file.exists()
        
        print("  ✓ Saved configurations to file")
        
        # Create second manager and load configurations
        manager2 = FolderConfigurationManager()
        manager2._config_file = config_file
        
        loaded_folders = manager2.list_folders()
        assert len(loaded_folders) == 2
        
        # Verify loaded data
        folder_names = [f.name for f in loaded_folders]
        assert "Workflow Test 1" in folder_names
        assert "Workflow Test 2" in folder_names
        
        print("  ✓ Loaded configurations from file")
        
        # Test finding specific configuration
        found_config = None
        for folder in loaded_folders:
            if folder.name == "Workflow Test 2":
                found_config = folder
                break
        
        assert found_config is not None
        assert len(found_config.directory_paths) == 2
        
        print("  ✓ Verified loaded configuration data")
        
    return True


def test_search_parameters_integration():
    """Test search parameters with configuration manager."""
    print("Testing search parameters integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = FolderConfigurationManager()
        manager._config_file = Path(temp_dir) / "search_test.json"
        
        # Create configuration
        config = manager.create_folder(
            name="Search Test",
            description="Testing search parameters",
            directory_paths=["C:\\Search\\Test"]
        )
        
        # Configure search parameters
        config.search_parameters.filename_pattern = "*.py"
        config.search_parameters.content_search = "def test_"
        config.search_parameters.case_sensitive = True
        config.search_parameters.include_extensions = {".py", ".txt"}
        config.search_parameters.size_min = 100
        config.search_parameters.size_max = 100000
        
        # Update configuration with new search parameters
        manager.update_folder(
            config.folder_id,
            search_parameters=config.search_parameters
        )
        
        print("  ✓ Updated configuration with search parameters")
        
        # Save and reload
        manager.save_configurations()
        
        # Create new manager to test persistence
        manager2 = FolderConfigurationManager()
        manager2._config_file = manager._config_file
        
        loaded_config = manager2.get_folder(config.folder_id)
        assert loaded_config is not None
        
        # Verify search parameters persisted
        search_params = loaded_config.search_parameters
        assert search_params.filename_pattern == "*.py"
        assert search_params.content_search == "def test_"
        assert search_params.case_sensitive is True
        assert ".py" in search_params.include_extensions
        assert search_params.size_min == 100
        assert search_params.size_max == 100000
        
        print("  ✓ Search parameters properly persisted and restored")
        
    return True


def test_statistics_integration():
    """Test statistics with configuration manager."""
    print("Testing statistics integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = FolderConfigurationManager()
        manager._config_file = Path(temp_dir) / "stats_test.json"
        
        # Create configuration
        config = manager.create_folder(
            name="Statistics Test",
            description="Testing statistics",
            directory_paths=["C:\\Stats\\Test"]
        )
        
        # Update statistics
        config.statistics.total_files = 500
        config.statistics.total_size = 25000000
        config.statistics.last_scan_time = datetime.now()
        config.statistics.scan_duration = 15.5
        config.statistics.file_type_breakdown = {
            ".py": 200,
            ".txt": 150,
            ".json": 100,
            ".md": 50
        }
        
        # Save configuration
        manager.save_configurations()
        
        print("  ✓ Saved configuration with statistics")
        
        # Load with new manager
        manager2 = FolderConfigurationManager()
        manager2._config_file = manager._config_file
        
        loaded_config = manager2.get_folder(config.folder_id)
        assert loaded_config is not None
        
        # Verify statistics
        stats = loaded_config.statistics
        assert stats.total_files == 500
        assert stats.total_size == 25000000
        assert stats.file_type_breakdown[".py"] == 200
        assert abs(stats.scan_duration - 15.5) < 0.01
        
        print("  ✓ Statistics properly persisted and restored")
        
    return True


def main():
    """Run all persistence validation tests."""
    print("="*60)
    print("Advanced Folders - Final Settings Persistence Validation")
    print("="*60)
    
    tests = [
        test_configuration_manager_api,
        test_persistence_workflow,
        test_search_parameters_integration,
        test_statistics_integration
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("Final Settings Persistence Validation Summary")
    print("="*60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL SETTINGS PERSISTENCE TESTS COMPLETED SUCCESSFULLY!")
        print("✓ FolderConfigurationManager API fully functional")
        print("✓ JSON serialization/deserialization working correctly")
        print("✓ File-based persistence operations validated")
        print("✓ Search parameters persistence confirmed")
        print("✓ Statistics persistence confirmed")
        print("✓ Ready for production use!")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)