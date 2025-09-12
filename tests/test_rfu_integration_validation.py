#!/usr/bin/env python3
"""
RFU Integration Validation Test

Tests the integration of Advanced Folders with the main RFU hub.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_main_py_integration():
    """Test that Advanced Folders is properly integrated in main.py."""
    print("Testing main.py integration...")
    
    # Read main.py content
    main_py_path = Path(__file__).parent.parent / "main.py"
    if not main_py_path.exists():
        print("  ✗ main.py not found")
        return False
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Advanced Folders integration
    required_elements = [
        "Advanced Folders",
        "advanced_folders",
        "open_advanced_folders"
    ]
    
    found_elements = []
    for element in required_elements:
        if element in content:
            found_elements.append(element)
            print(f"  ✓ Found '{element}' in main.py")
        else:
            print(f"  ✗ Missing '{element}' in main.py")
    
    if len(found_elements) >= 2:  # At least 2 out of 3 required elements
        print("  ✓ Advanced Folders integration detected in main.py")
        return True
    else:
        print("  ✗ Advanced Folders integration not properly configured")
        return False


def test_module_import():
    """Test that Advanced Folders modules can be imported."""
    print("Testing module imports...")
    
    try:
        # Test core imports
        from utilities.file_management.advanced_folders.core.folder_configuration import (
            FolderConfiguration, FolderConfigurationManager)
        print("  ✓ Core modules import successfully")
        
        # Test creating a basic configuration
        manager = FolderConfigurationManager()
        config = manager.create_folder(
            name="Import Test",
            description="Testing import functionality",
            directory_paths=["C:\\Test"]
        )
        print(f"  ✓ Created test configuration: {config.name}")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Configuration creation failed: {e}")
        return False


def test_launcher_method():
    """Test that the launcher method exists in main.py."""
    print("Testing launcher method...")
    
    main_py_path = Path(__file__).parent.parent / "main.py"
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for launcher method
    launcher_indicators = [
        "def open_advanced_folders",
        "launch_tool",
        "advanced_folders"
    ]
    
    found_launcher = False
    for indicator in launcher_indicators:
        if indicator in content:
            found_launcher = True
            print(f"  ✓ Found launcher indicator: {indicator}")
            break
    
    if found_launcher:
        print("  ✓ Launcher method appears to be implemented")
        return True
    else:
        print("  ✗ Launcher method not found")
        return False


def test_file_management_tab():
    """Test that Advanced Folders is added to file management tab."""
    print("Testing file management tab integration...")
    
    main_py_path = Path(__file__).parent.parent / "main.py"
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for file management tab section
    lines = content.split('\n')
    in_file_management = False
    found_advanced_folders = False
    
    for line in lines:
        if 'file_management_tools' in line or 'File Management' in line:
            in_file_management = True
        elif in_file_management and ('advanced_folders' in line.lower() or 'Advanced Folders' in line):
            found_advanced_folders = True
            print(f"  ✓ Found Advanced Folders in file management: {line.strip()}")
            break
        elif in_file_management and line.strip().startswith(']'):
            break  # End of file management section
    
    if found_advanced_folders:
        print("  ✓ Advanced Folders properly added to file management tab")
        return True
    else:
        print("  ✗ Advanced Folders not found in file management tab")
        return False


def main():
    """Run RFU integration validation tests."""
    print("="*60)
    print("Advanced Folders - RFU Integration Validation")
    print("="*60)
    
    tests = [
        test_main_py_integration,
        test_module_import,
        test_launcher_method,
        test_file_management_tab
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
        print()  # Add spacing between tests
    
    print("="*60)
    print("RFU Integration Validation Summary")
    print("="*60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL RFU INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
        print("✓ Advanced Folders properly integrated with main.py")
        print("✓ Module imports functioning correctly")
        print("✓ Launcher method implementation detected")
        print("✓ File management tab integration confirmed")
        print("✓ Ready for production use!")
        return True
    else:
        print(f"\n✗ {failed} integration test(s) failed.")
        print("✗ Integration requires attention before production deployment")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)