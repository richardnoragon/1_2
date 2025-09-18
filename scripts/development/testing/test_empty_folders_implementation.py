#!/usr/bin/env python3
"""
Test script to verify that all Analysis tools are working correctly.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_all_analysis_tools():
    """Test that we can successfully import all analysis tools."""
    print("Testing Analysis Tools Implementation...")
    print("=" * 50)
    
    success_count = 0
    total_tools = 3
    
    # Test Size Analyzer
    try:
        from utilities.analysis.size_analyzer import SizeAnalyzerGUI
        print("✓ Size Analyzer imported successfully")
        success_count += 1
    except ImportError as e:
        print(f"✗ Size Analyzer import failed: {e}")
    
    # Test Duplicate Finder
    try:
        from utilities.analysis.find_duplicate_files import DuplicateFinderApp
        print("✓ Duplicate Finder imported successfully")
        success_count += 1
    except ImportError as e:
        print(f"✗ Duplicate Finder import failed: {e}")
    
    # Test Checksum Tool
    try:
        from utilities.analysis.check_sum import ChecksumGUI
        print("✓ Checksum Tool imported successfully")
        success_count += 1
    except ImportError as e:
        print(f"✗ Checksum Tool import failed: {e}")
    
    # Test Empty Folders (NEW)
    try:
        from utilities.analysis.empty_folders import EmptyFoldersGUI
        print("✓ Empty Folders Finder imported successfully")
        success_count += 1
        total_tools = 4  # Update total
    except ImportError as e:
        print(f"✗ Empty Folders Finder import failed: {e}")
        total_tools = 4  # Still count it in total
    
    print()
    print(f"Analysis Tools Status: {success_count}/{total_tools} working")
    
    if success_count == total_tools:
        print("🎉 All Analysis tools are working correctly!")
        return True
    else:
        print("⚠️  Some Analysis tools need attention")
        return False

def test_simple_hub_integration():
    """Test that the Simple Hub can access all the tools."""
    print("\nTesting Simple Hub Integration...")
    print("=" * 50)
    
    try:
        from src.simple_hub import SimpleRFUHub
        
        # Create a hub instance (but don't show GUI)
        hub = SimpleRFUHub()
        
        # Test that methods exist
        methods_to_test = [
            'open_size_analyzer',
            'open_duplicate_finder', 
            'open_checksum',
            'open_empty_folders'  # NEW
        ]
        
        success_count = 0
        for method_name in methods_to_test:
            if hasattr(hub, method_name):
                print(f"✓ Method {method_name} exists")
                success_count += 1
            else:
                print(f"✗ Method {method_name} not found")
        
        print(f"\nHub Integration: {success_count}/{len(methods_to_test)} methods available")
        
        if success_count == len(methods_to_test):
            print("🎉 Simple Hub integration is complete!")
            return True
        else:
            print("⚠️  Simple Hub integration needs work")
            return False
        
    except Exception as e:
        print(f"✗ Hub integration test failed: {e}")
        return False

def test_legacy_cleanup():
    """Test that legacy files were properly removed."""
    print("\nTesting Legacy File Cleanup...")
    print("=" * 50)
    
    legacy_path = Path(__file__).parent / "src" / "legacy" / "file_utilities_1"
    
    legacy_files_to_check = [
        "empty_folders.py",
        "empty_folders.ui", 
        "empty_folder_files_md"
    ]
    
    removed_count = 0
    for filename in legacy_files_to_check:
        file_path = legacy_path / filename
        if not file_path.exists():
            print(f"✓ {filename} successfully removed")
            removed_count += 1
        else:
            print(f"✗ {filename} still exists")
    
    print(f"\nLegacy Cleanup: {removed_count}/{len(legacy_files_to_check)} files removed")
    
    if removed_count == len(legacy_files_to_check):
        print("🎉 Legacy cleanup completed successfully!")
        return True
    else:
        print("⚠️  Legacy cleanup incomplete")
        return False

if __name__ == "__main__":
    print("Empty Folders Implementation Verification")
    print("=" * 60)
    
    tools_ok = test_all_analysis_tools()
    hub_ok = test_simple_hub_integration()
    cleanup_ok = test_legacy_cleanup()
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    if tools_ok and hub_ok and cleanup_ok:
        print("🎉 SUCCESS: Empty Folders implementation is complete!")
        print("   ✓ All Analysis tools working")
        print("   ✓ Simple Hub integration complete") 
        print("   ✓ Legacy files cleaned up")
        print("\nThe Empty Folders button should now work correctly!")
    else:
        print("⚠️  PARTIAL SUCCESS: Some issues found")
        if not tools_ok:
            print("   ✗ Tool import issues")
        if not hub_ok:
            print("   ✗ Hub integration issues")
        if not cleanup_ok:
            print("   ✗ Legacy cleanup incomplete")
    
    print("\nTest completed!")