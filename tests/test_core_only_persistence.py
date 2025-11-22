#!/usr/bin/env python3
"""
Advanced Folders Core-Only Settings Persistence Test

Tests only the core functionality without GUI imports.
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


def test_core_persistence():
    """Test core persistence functionality."""
    print("Testing core persistence functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        
        # Create manager
        manager = FolderConfigurationManager()
        manager._config_file = config_file
        
        # Create folder configuration
        config = manager.create_folder(
            name="Core Test Folder",
            description="Testing core functionality",
            directory_paths=["C:\\Core\\Test"]
        )
        
        print(f"  ✓ Created folder: {config.name}")
        print(f"  ✓ Folder ID: {config.folder_id}")
        print(f"  ✓ Config file: {config_file}")
        
        # Test persistence
        success = manager.save_configurations()
        assert success
        
        print("  ✓ Saved configurations")
        print(f"  ✓ Config file exists: {config_file.exists()}")
        
        # Create new manager and load
        manager2 = FolderConfigurationManager()
        manager2._config_file = config_file
        manager2.load_configurations()  # Explicitly load
        
        print(f"  ✓ Loaded {len(manager2.list_folders())} configurations")
        
        loaded_config = manager2.get_folder(config.folder_id)
        if loaded_config is None:
            print(f"  ✗ Failed to load config with ID: {config.folder_id}")
            print(f"  ✗ Available IDs: {list(manager2._configurations.keys())}")
            return False
        
        assert loaded_config.name == config.name
        
        print("  ✓ Loaded configurations successfully")
        
    return True


def main():
    """Run core persistence test."""
    print("="*50)
    print("Advanced Folders - Core Persistence Test")
    print("="*50)
    
    try:
        if test_core_persistence():
            print("\n✓ CORE PERSISTENCE TEST PASSED!")
            return True
        else:
            print("\n✗ Core persistence test failed")
            return False
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)