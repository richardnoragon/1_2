#!/usr/bin/env python3
"""
Integration Verification Script

This script tests that all integrated tools can be imported and launched properly.
"""

import sys
import os
import importlib

def test_import(module_path, class_name):
    """Test if a module and class can be imported successfully."""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, class_name):
            print(f"✅ {module_path}.{class_name} - Import successful")
            return True
        else:
            print(f"❌ {module_path}.{class_name} - Class not found")
            return False
    except ImportError as e:
        print(f"❌ {module_path}.{class_name} - Import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ {module_path}.{class_name} - Error: {e}")
        return False

def main():
    """Test all integrated tools."""
    print("=" * 60)
    print("Richard's File Utilities - Integration Verification")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add src to path
    sys.path.insert(0, os.path.join(script_dir, 'src'))
    
    # Test tools that were reorganized
    tools_to_test = [
        # Analysis tools (moved/cleaned)
        ("src.utilities.analysis.check_sum", "ChecksumGUI"),
        ("src.utilities.analysis.find_duplicate_files", "DuplicateFinderApp"), 
        ("src.utilities.analysis.size_analyzer", "SizeAnalyzerGUI"),
        
        # Security tools (moved)
        ("src.utilities.security.en_and_decrypt", "EnAndDecryptGUI"),
        ("src.utilities.security.secure_delete", "SecureDeleteGUI"),
        
        # System tools (existing)
        ("src.utilities.system.permissions_editor", "PermissionsEditorGUI"),
        
        # New network tools
        ("src.utilities.network.network_connectivity", "NetworkConnectivityGUI"),
        ("src.utilities.network.network_scanner", "NetworkScannerGUI"),
        
        # New privacy tools
        ("src.utilities.privacy.privacy_tools", "PrivacyCleanerGUI"),
        ("src.utilities.privacy.data_anonymizer", "DataAnonymizerGUI"),
        
        # New system tools
        ("src.utilities.system.diagnostics_monitoring", "SystemDiagnosticsGUI"),
        ("src.utilities.system.system_cleanup", "SystemCleanupGUI"),
        ("src.utilities.system.software_maintenance", "SoftwareMaintenanceGUI"),
    ]
    
    print("\nTesting tool imports...")
    print("-" * 40)
    
    success_count = 0
    total_count = len(tools_to_test)
    
    for module_path, class_name in tools_to_test:
        if test_import(module_path, class_name):
            success_count += 1
    
    print("\n" + "-" * 40)
    print(f"Import Test Results: {success_count}/{total_count} successful")
    
    # Test that duplicate files were removed
    print("\nChecking for removed duplicate files...")
    print("-" * 40)
    
    duplicate_files = [
        "check_sum.py",
        "find_duplicate_files.py", 
        "permissions_editor.py",
        "size_analyzer.py",
        "en_and_decrypt.py",
        "secure_delete.py"
    ]
    
    removed_count = 0
    for file_name in duplicate_files:
        if not os.path.exists(file_name):
            print(f"✅ {file_name} - Successfully removed from root")
            removed_count += 1
        else:
            print(f"⚠️ {file_name} - Still exists in root directory")
    
    print(f"\nDuplicate Removal: {removed_count}/{len(duplicate_files)} files removed")
    
    # Test that __init__.py files were created
    print("\nChecking for __init__.py files...")
    print("-" * 40)
    
    init_dirs = [
        "src/utilities",
        "src/utilities/analysis",
        "src/utilities/network", 
        "src/utilities/privacy",
        "src/utilities/security",
        "src/utilities/system"
    ]
    
    init_count = 0
    for dir_path in init_dirs:
        init_file = os.path.join(dir_path, "__init__.py")
        if os.path.exists(init_file):
            print(f"✅ {init_file} - Exists")
            init_count += 1
        else:
            print(f"❌ {init_file} - Missing")
    
    print(f"\n__init__.py files: {init_count}/{len(init_dirs)} created")
    
    # Overall summary
    print("\n" + "=" * 60)
    print("INTEGRATION VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"✅ Tool Imports: {success_count}/{total_count}")
    print(f"✅ Duplicates Removed: {removed_count}/{len(duplicate_files)}")
    print(f"✅ Init Files Created: {init_count}/{len(init_dirs)}")
    
    overall_success = (success_count == total_count and 
                      removed_count == len(duplicate_files) and
                      init_count == len(init_dirs))
    
    if overall_success:
        print("\n🎉 INTEGRATION SUCCESSFUL! All tools properly integrated.")
    else:
        print("\n⚠️ INTEGRATION PARTIALLY SUCCESSFUL. Check individual items above.")
    
    print("\nNext steps:")
    print("1. Test the main application: python main.py")
    print("2. Test individual tool functionality")
    print("3. Remove .backup files after verification")

if __name__ == "__main__":
    main()
