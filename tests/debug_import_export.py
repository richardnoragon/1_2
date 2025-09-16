#!/usr/bin/env python3
"""
Debug Import/Export Issues

Simple test to identify and fix the import/export problems.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.file_management.advanced_folders.core.folder_configuration import (
    FolderConfiguration, FolderConfigurationManager)
from tools.file_management.advanced_folders.core.import_export import \
    ImportExportManager


def debug_export_issue():
    """Debug the export counting issue."""
    print("Debugging export issue...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create manager and configurations
        manager = FolderConfigurationManager()
        manager._config_file = temp_path / "debug_config.json"
        
        # Create test configurations
        config1 = manager.create_folder(
            name="Debug Test 1",
            description="First debug test",
            directory_paths=["C:\\Debug\\Test1"]
        )
        
        config2 = manager.create_folder(
            name="Debug Test 2",
            description="Second debug test",
            directory_paths=["C:\\Debug\\Test2"]
        )
        
        print(f"  Created {len(manager.list_folders())} configurations")
        
        # Check what's in the manager
        all_configs = manager.list_folders()
        print("  Configurations in manager:")
        for config in all_configs:
            print(f"    - {config.name} (ID: {config.folder_id})")
        
        # Try export
        ie_manager = ImportExportManager(manager)
        export_path = temp_path / "debug_export.json"
        
        print(f"  Attempting export to: {export_path}")
        export_success = ie_manager.export_configurations(export_path)
        
        if export_success and export_path.exists():
            print("  ✓ Export file created successfully")
            
            # Read and analyze export content
            with open(export_path, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            print("  Export data structure:")
            print(f"    - Root keys: {list(export_data.keys())}")
            
            if 'advanced_folders_export' in export_data:
                export_section = export_data['advanced_folders_export']
                print(f"    - Export section keys: {list(export_section.keys())}")
                
                if 'configurations' in export_section:
                    configs = export_section['configurations']
                    print(f"    - Configurations count: {len(configs)}")
                    
                    for i, config in enumerate(configs):
                        print(f"      {i+1}. {config.get('name', 'Unknown')} (ID: {config.get('folder_id', 'Unknown')})")
                else:
                    print("    - No 'configurations' key found")
            else:
                print("    - No 'advanced_folders_export' key found")
        else:
            print("  ✗ Export failed or file not created")
            return False
        
    return True


def debug_import_issue():
    """Debug the import issue."""
    print("Debugging import issue...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create original manager with one config
        original_manager = FolderConfigurationManager()
        original_manager._config_file = temp_path / "original.json"
        
        original_config = original_manager.create_folder(
            name="Original Config",
            description="Original configuration",
            directory_paths=["C:\\Original\\Test"]
        )
        
        print(f"  Created original config: {original_config.name}")
        
        # Export it
        ie_manager = ImportExportManager(original_manager)
        export_path = temp_path / "test_export.json"
        ie_manager.export_configurations(export_path)
        
        # Create new manager with conflicting config
        import_manager = FolderConfigurationManager()
        import_manager._config_file = temp_path / "import.json"
        
        conflicting_config = import_manager.create_folder(
            name="Original Config",  # Same name
            description="Conflicting config",
            directory_paths=["C:\\Conflict\\Test"]
        )
        
        print(f"  Created conflicting config: {conflicting_config.name}")
        print(f"  Configs before import: {len(import_manager.list_folders())}")
        
        # Try import with skip strategy
        import_ie_manager = ImportExportManager(import_manager)
        success, messages = import_ie_manager.import_configurations(
            export_path,
            conflict_resolution='skip'
        )
        
        print(f"  Import success: {success}")
        print(f"  Import messages: {messages}")
        print(f"  Configs after import: {len(import_manager.list_folders())}")
        
        # List all configurations
        for config in import_manager.list_folders():
            print(f"    - {config.name} (ID: {config.folder_id})")
        
    return True


def main():
    """Run debug tests."""
    print("="*50)
    print("Debug Import/Export Issues")
    print("="*50)
    
    try:
        debug_export_issue()
        print()
        debug_import_issue()
        return True
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()