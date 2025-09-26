"""
Final Rename Migration Test
==========================

This script performs final validation that the rename migration is complete
and functional from the new location in file_utilities_2/gui/.
"""

import sys
from pathlib import Path

def test_original_files_removed():
    """Test that original files have been removed from root directory."""
    print("Testing original file removal...")
    
    original_files = [
        "rename.py",
        "rename.ui",
        "gui/file_ops/rename_window.py"
    ]
    
    all_removed = True
    for file_path in original_files:
        if Path(file_path).exists():
            print(f"✗ Original file still exists: {file_path}")
            all_removed = False
        else:
            print(f"✓ Original file removed: {file_path}")
    
    return all_removed

def test_new_files_exist():
    """Test that new files exist in the correct location."""
    print("\nTesting new file locations...")
    
    new_files = [
        "file_utilities_2/gui/rename_gui.py",
        "file_utilities_2/gui/rename.ui",
        "file_utilities_2/tests/test_rename_gui.py"
    ]
    
    all_exist = True
    for file_path in new_files:
        if Path(file_path).exists():
            print(f"✓ New file exists: {file_path}")
        else:
            print(f"✗ New file missing: {file_path}")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test that imports work from new location."""
    print("\nTesting imports from new location...")
    
    try:
        # Test direct import
        from file_utilities_2.gui.rename_gui import RenameGUI
        print("✓ Direct import successful: RenameGUI")
        
        # Test module import
        from file_utilities_2.gui import RenameGUI as RenameGUI2
        print("✓ Module import successful: RenameGUI")
        
        # Test that they're the same class
        if RenameGUI is RenameGUI2:
            print("✓ Import consistency verified")
        else:
            print("✗ Import inconsistency detected")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_class_functionality():
    """Test basic class functionality without UI."""
    print("\nTesting class functionality...")
    
    try:
        from file_utilities_2.gui.rename_gui import RenameGUI
        
        # Test class attributes
        if hasattr(RenameGUI, 'DATE_FORMATS'):
            print("✓ DATE_FORMATS attribute exists")
            if len(RenameGUI.DATE_FORMATS) == 5:
                print("✓ DATE_FORMATS has correct number of formats")
            else:
                print("✗ DATE_FORMATS has incorrect number of formats")
                return False
        else:
            print("✗ DATE_FORMATS attribute missing")
            return False
        
        # Test key methods exist
        required_methods = [
            '_get_rename_icon',
            '_setup_ui',
            'load_directory',
            'rename_files',
            '_get_rename_mode_and_params'
        ]
        
        for method_name in required_methods:
            if hasattr(RenameGUI, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Class functionality test failed: {e}")
        return False

def test_backup_integrity():
    """Test that backup files are intact."""
    print("\nTesting backup integrity...")
    
    backup_dir = Path("backup/rename_migration/2025-07-28_18-05-00")
    if not backup_dir.exists():
        print("✗ Backup directory not found")
        return False
    
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

def test_configuration_updates():
    """Test that configuration files have been updated."""
    print("\nTesting configuration updates...")
    
    config_files = [
        ("tools/apply_standardized_styling.py", "file_utilities_2/gui/rename_gui.py"),
        ("tools/standardize_windows.py", "file_utilities_2/gui/rename_gui.py"),
        ("test_gui_tools.py", "file_utilities_2/gui/rename_gui.py"),
        ("tests/test_main.py", "file_utilities_2/gui/rename_gui.py")
    ]
    
    all_updated = True
    for config_file, expected_reference in config_files:
        if Path(config_file).exists():
            try:
                content = Path(config_file).read_text(encoding='utf-8')
                if expected_reference in content:
                    print(f"✓ Configuration updated: {config_file}")
                else:
                    print(f"✗ Configuration not updated: {config_file}")
                    all_updated = False
            except Exception as e:
                print(f"✗ Error reading {config_file}: {e}")
                all_updated = False
        else:
            print(f"⚠ Configuration file not found: {config_file}")
    
    return all_updated

def main():
    """Run all final validation tests."""
    print("Final Rename Migration Validation")
    print("=" * 50)
    
    tests = [
        ("Original Files Removed", test_original_files_removed),
        ("New Files Exist", test_new_files_exist),
        ("Import Functionality", test_imports),
        ("Class Functionality", test_class_functionality),
        ("Backup Integrity", test_backup_integrity),
        ("Configuration Updates", test_configuration_updates)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("✅ All rename functionality has been migrated to file_utilities_2/gui/")
        print("✅ Original files removed from root directory")
        print("✅ All references updated to new location")
        print("✅ Backup system in place for rollback if needed")
        print("\nThe rename utility is now fully integrated into file_utilities_2!")
        return 0
    else:
        print(f"\n❌ Migration validation failed: {total - passed} issues found")
        print("Please review and fix the failing tests before considering migration complete.")
        return 1

if __name__ == "__main__":
    sys.exit(main())