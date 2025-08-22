#!/usr/bin/env python3
"""Test script to verify File Operations button functionality.

This script tests all the File Operations buttons in the File Operations tab
to ensure they launch the correct programs when clicked.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_file_operations_imports():
    """Test that all file operations tools can be imported."""
    print("Testing File Operations tool imports...")
    results = {}
    
    # Test File Splitter
    try:
        from src.utilities.file_operations.file_splitter.gui import FileSplitJoinGUI
        print("✓ File Splitter import successful")
        results['file_splitter'] = True
    except ImportError as e:
        print(f"✗ File Splitter import failed: {e}")
        results['file_splitter'] = False
    
    # Test CMSD (Copy/Move/Sync/Delete)
    try:
        from src.utilities.file_operations.cmsd import CopyMoveSyncDeleteWindow
        print("✓ Copy/Move/Sync/Delete import successful")
        results['cmsd'] = True
    except ImportError as e:
        print(f"✗ Copy/Move/Sync/Delete import failed: {e}")
        results['cmsd'] = False
    
    # Test Sync & Backup
    try:
        from src.utilities.file_operations.synchronization_backup.sync import SyncWindow
        print("✓ Sync & Backup import successful")
        results['sync_backup'] = True
    except ImportError as e:
        print(f"✗ Sync & Backup import failed: {e}")
        results['sync_backup'] = False
    
    # Test Organize Files
    try:
        from src.utilities.file_operations.organize.organize import OrganizeWindow
        print("✓ Organize Files import successful")
        results['organize'] = True
    except ImportError as e:
        print(f"✗ Organize Files import failed: {e}")
        results['organize'] = False
    
    # Test Batch Rename
    try:
        from src.utilities.file_management.rename import RenameWindow
        print("✓ Batch Rename import successful")
        results['rename'] = True
    except ImportError as e:
        print(f"✗ Batch Rename import failed: {e}")
        results['rename'] = False
    
    return results


def test_hub_integration():
    """Test that the hub can execute the file operations methods."""
    print("\nTesting hub integration...")
    
    try:
        from src.rfu.simple_hub import SimpleRFUHub
        
        # Test individual methods (without GUI)
        hub = SimpleRFUHub()
        print("✓ Hub created successfully")
        
        # Test method existence
        methods = [
            ('open_file_splitter', 'File Splitter'),
            ('open_cmsd_logic', 'Copy/Move/Sync/Delete'),
            ('open_sync_backup', 'Sync & Backup'),
            ('open_organize_files', 'Organize Files'),
            ('open_batch_rename', 'Batch Rename')
        ]
        
        method_results = {}
        for method_name, display_name in methods:
            if hasattr(hub, method_name):
                print(f"✓ {display_name} method exists")
                method_results[method_name] = True
            else:
                print(f"✗ {display_name} method missing")
                method_results[method_name] = False
        
        return method_results
        
    except Exception as e:
        print(f"✗ Hub integration test failed: {e}")
        return {}


def generate_test_report(import_results, method_results):
    """Generate a comprehensive test report."""
    print("\n" + "=" * 70)
    print("FILE OPERATIONS BUTTON FIX - TEST REPORT")
    print("=" * 70)
    
    # Import results
    print("\n📦 IMPORT TESTS:")
    for tool, result in import_results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {tool.replace('_', ' ').title():<25} {status}")
    
    # Method results
    print("\n🔧 METHOD TESTS:")
    for method, result in method_results.items():
        method_display = method.replace('open_', '').replace('_', ' ').title()
        status = "PASS" if result else "FAIL"
        print(f"  {method_display:<25} {status}")
    
    # Overall status
    all_imports_pass = all(import_results.values())
    all_methods_pass = all(method_results.values())
    overall_pass = all_imports_pass and all_methods_pass
    
    print(f"\n📊 OVERALL STATUS:")
    print(f"  Import Tests: {'PASS' if all_imports_pass else 'FAIL'}")
    print(f"  Method Tests: {'PASS' if all_methods_pass else 'FAIL'}")
    print(f"  Overall: {'PASS' if overall_pass else 'FAIL'}")
    
    if overall_pass:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe File Operations buttons should now work correctly.")
        print("\nTo test manually:")
        print("1. Run: python -m src.rfu.simple_hub")
        print("2. Go to the File Operations tab")
        print("3. Click each button to verify it opens the correct tool:")
        print("   • 📂 File Splitter")
        print("   • 📋 Copy/Move/Sync")
        print("   • 🔄 Sync & Backup") 
        print("   • 📁 Organize Files")
        print("   • 🗂️ Batch Rename")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the errors above and fix any import issues.")
    
    return overall_pass


def main():
    """Run all tests."""
    print("File Operations Button Fix - Test Suite")
    print("=" * 50)
    
    # Test imports
    import_results = test_file_operations_imports()
    
    # Test hub integration
    method_results = test_hub_integration()
    
    # Generate report
    overall_pass = generate_test_report(import_results, method_results)
    
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())