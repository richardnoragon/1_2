#!/usr/bin/env python3
"""
Test script to verify tool imports work correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tool_import(module_name, class_name):
    """Test importing a specific tool."""
    try:
        print(f"Testing {module_name}.{class_name}...")
        
        # Try different import paths
        import_paths = [
            module_name,  # Root directory
            f"src.utilities.file_operations.catalog.{module_name}",  # Catalog tools
            f"src.utilities.file_operations.file_touch.{module_name}",  # File touch tools
            f"src.utilities.file_operations.organize.{module_name}",  # Organize tools
            f"src.utilities.file_operations.file_finder.{module_name}",  # File finder tools
            f"src.utilities.file_operations.compression.{module_name}",  # Compression tools
            f"src.legacy.file_utilities_1.{module_name}",  # Legacy tools (fallback)
            f"src.utilities.{module_name}",  # Other utilities
        ]
        
        for import_path in import_paths:
            try:
                if '.' in import_path:
                    # Handle nested imports
                    parts = import_path.split('.')
                    module = __import__(import_path, fromlist=[parts[-1]])
                else:
                    module = __import__(import_path)
                
                tool_class = getattr(module, class_name)
                print(f"✅ Successfully imported {class_name} from {import_path}")
                return True
            except (ImportError, AttributeError) as e:
                print(f"❌ Failed to import from {import_path}: {e}")
                continue
        
        print(f"❌ Could not import {class_name} from any path")
        return False
        
    except Exception as e:
        print(f"❌ Error testing {module_name}.{class_name}: {e}")
        return False

def main():
    """Test importing various tools."""
    print("Testing tool imports...")
    print("=" * 50)
    
    # Test some known tools
    tools_to_test = [
        ("file_finder", "FileFinderGUI"),
        ("compress_decompress", "CompressDecompressApp"),
        ("empty_folders", "EmptyFoldersGUI"),
        ("catalog", "CatalogWindow"),
        ("organize", "OrganizeWindow"),
    ]
    
    successful_imports = 0
    total_tests = len(tools_to_test)
    
    for module_name, class_name in tools_to_test:
        if test_tool_import(module_name, class_name):
            successful_imports += 1
        print()
    
    print("=" * 50)
    print(f"Results: {successful_imports}/{total_tests} tools imported successfully")
    
    if successful_imports > 0:
        print("✅ Some tools are available and should work in the main application!")
    else:
        print("❌ No tools could be imported. Check the file structure and imports.")

if __name__ == '__main__':
    main()
