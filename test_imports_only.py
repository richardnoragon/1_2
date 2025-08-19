#!/usr/bin/env python3
"""Simple test script to verify File Operations imports.

This script tests the basic imports without creating GUI components.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all file operations tools can be imported."""
    print("Testing File Operations tool imports...")
    results = {}
    
    # Test File Splitter
    try:
        from src.rfu.tools.file_operations.file_splitter_joiner import FileSplitJoinGUI
        print("✓ File Splitter import successful")
        results['file_splitter'] = True
    except Exception as e:
        print(f"✗ File Splitter import failed: {e}")
        results['file_splitter'] = False
    
    # Test CMSD (Copy/Move/Sync/Delete)
    try:
        from src.rfu.tools.file_operations.cmsd import CopyMoveSyncDeleteWindow
        print("✓ Copy/Move/Sync/Delete import successful")
        results['cmsd'] = True
    except Exception as e:
        print(f"✗ Copy/Move/Sync/Delete import failed: {e}")
        results['cmsd'] = False
    
    # Test Organize Files
    try:
        from src.rfu.tools.file_management.organize import OrganizeWindow
        print("✓ Organize Files import successful")
        results['organize'] = True
    except Exception as e:
        print(f"✗ Organize Files import failed: {e}")
        results['organize'] = False
    
    # Test Batch Rename
    try:
        from src.rfu.tools.file_management.rename import RenameWindow
        print("✓ Batch Rename import successful")
        results['rename'] = True
    except Exception as e:
        print(f"✗ Batch Rename import failed: {e}")
        results['rename'] = False
    
    return results


def main():
    """Run import tests."""
    print("File Operations Button Fix - Import Test")
    print("=" * 50)
    
    # Test imports
    results = test_imports()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for tool, result in results.items():
        status = "PASS" if result else "FAIL"
        tool_name = tool.replace('_', ' ').title()
        print(f"  {tool_name:<25} {status}")
    
    print(f"\nSUMMARY: {success_count}/{total_count} imports successful")
    
    if success_count >= 4:  # File Splitter, CMSD, Organize, Rename
        print("\n✅ Most critical tools imported successfully!")
        print("\nTo test the buttons:")
        print("1. Run: python -m src.rfu.simple_hub")
        print("2. Go to the File Operations tab")
        print("3. Click each button to verify it opens the correct tool")
        print("\nButtons that should work:")
        if results.get('file_splitter'): print("   • 📂 File Splitter")
        if results.get('cmsd'): print("   • 📋 Copy/Move/Sync")
        if results.get('organize'): print("   • 📁 Organize Files")
        if results.get('rename'): print("   • 🗂️ Batch Rename")
        
        return 0
    else:
        print("\n❌ Too many import failures. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())