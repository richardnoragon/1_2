"""
Rename Migration Validation Script
=================================

This script validates the consolidated rename implementation by testing:
1. Import functionality
2. Basic class instantiation
3. Core method availability
4. UI file accessibility
5. Integration with file_utilities_2 architecture
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test core imports
        from file_utilities_2.gui.rename_gui import RenameGUI
        print("✓ RenameGUI import successful")
        
        # Test StandardWindow inheritance
        from file_utilities_2.gui.standard_window import StandardWindow
        print("✓ StandardWindow import successful")
        
        # Test core dependencies
        from core.file_ops.renamer import FileRenamer
        print("✓ FileRenamer import successful")
        
        from core.logging_manager import LogManager
        print("✓ LogManager import successful")
        
        from core.error_handler import error_handler
        print("✓ error_handler import successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_ui_file_exists():
    """Test that the UI file exists in the correct location."""
    print("\nTesting UI file accessibility...")
    
    ui_file = Path("file_utilities_2/gui/rename.ui")
    if ui_file.exists():
        print(f"✓ UI file found at: {ui_file}")
        
        # Check file size
        size = ui_file.stat().st_size
        if size > 0:
            print(f"✓ UI file has content ({size} bytes)")
            return True
        else:
            print("✗ UI file is empty")
            return False
    else:
        print(f"✗ UI file not found at: {ui_file}")
        return False

def test_class_structure():
    """Test the class structure and key methods."""
    print("\nTesting class structure...")
    
    try:
        from file_utilities_2.gui.rename_gui import RenameGUI
        
        # Check class inheritance
        from file_utilities_2.gui.standard_window import StandardWindow
        if issubclass(RenameGUI, StandardWindow):
            print("✓ RenameGUI properly inherits from StandardWindow")
        else:
            print("✗ RenameGUI inheritance issue")
            return False
        
        # Check key methods exist
        required_methods = [
            '_get_rename_icon',
            '_setup_ui',
            '_setup_models',
            '_setup_metadata_formats',
            '_connect_signals',
            'load_directory',
            'filter_list',
            'choose_selection',
            'remove_selection',
            'rename_files',
            '_get_rename_mode_and_params',
            '_validate_rename_params',
            '_perform_rename_operation'
        ]
        
        for method_name in required_methods:
            if hasattr(RenameGUI, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False
        
        # Check constants
        if hasattr(RenameGUI, 'DATE_FORMATS'):
            print("✓ DATE_FORMATS constant exists")
            if len(RenameGUI.DATE_FORMATS) == 5:
                print("✓ DATE_FORMATS has correct number of formats")
            else:
                print("✗ DATE_FORMATS has incorrect number of formats")
                return False
        else:
            print("✗ DATE_FORMATS constant missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Class structure test failed: {e}")
        return False

def test_module_integration():
    """Test integration with file_utilities_2 module structure."""
    print("\nTesting module integration...")
    
    try:
        # Test __init__.py integration
        from file_utilities_2.gui import RenameGUI
        print("✓ RenameGUI available through module __init__.py")
        
        # Test that it's in __all__
        import file_utilities_2.gui as gui_module
        if hasattr(gui_module, '__all__') and 'RenameGUI' in gui_module.__all__:
            print("✓ RenameGUI properly exported in __all__")
        else:
            print("✗ RenameGUI not in __all__ export list")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Module integration failed: {e}")
        return False

def test_backup_files():
    """Test that backup files were created properly."""
    print("\nTesting backup files...")
    
    backup_dir = Path("backup/rename_migration/2025-07-28_18-05-00")
    if backup_dir.exists():
        print(f"✓ Backup directory exists: {backup_dir}")
        
        required_backups = [
            "rename.py",
            "rename.ui", 
            "rename_window_original.py",
            "backup_manifest.txt"
        ]
        
        all_exist = True
        for backup_file in required_backups:
            backup_path = backup_dir / backup_file
            if backup_path.exists():
                print(f"✓ Backup file exists: {backup_file}")
            else:
                print(f"✗ Backup file missing: {backup_file}")
                all_exist = False
        
        return all_exist
    else:
        print(f"✗ Backup directory not found: {backup_dir}")
        return False

def test_original_files_still_exist():
    """Test that original files still exist (before cleanup)."""
    print("\nTesting original files...")
    
    original_files = [
        "rename.py",
        "rename.ui",
        "gui/file_ops/rename_window.py"
    ]
    
    all_exist = True
    for file_path in original_files:
        if Path(file_path).exists():
            print(f"✓ Original file exists: {file_path}")
        else:
            print(f"✗ Original file missing: {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """Run all validation tests."""
    print("Rename Migration Validation")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("UI File Tests", test_ui_file_exists),
        ("Class Structure Tests", test_class_structure),
        ("Module Integration Tests", test_module_integration),
        ("Backup Files Tests", test_backup_files),
        ("Original Files Tests", test_original_files_still_exist)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Migration is ready for testing.")
        return 0
    else:
        print("❌ Some validation tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())