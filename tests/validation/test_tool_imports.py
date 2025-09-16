#!/usr/bin/env python3
"""
Tool Import Test Script
Test individual tool imports to identify issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_file_finder():
    """Test File Finder import."""
    try:
        from src.tools.file_management.file_finder import FileFinderGUI
        print("✅ File Finder import successful")
        return True
    except Exception as e:
        print(f"❌ File Finder import failed: {e}")
        return False

def test_network_transfer():
    """Test Network Transfer import."""
    try:
        from src.tools.network.network_transfer import NetworkTransferGUI
        print("✅ Network Transfer import successful")
        return True
    except Exception as e:
        print(f"❌ Network Transfer import failed: {e}")
        return False

def test_network_connectivity():
    """Test Network Connectivity import."""
    try:
        from src.tools.network.network_connectivity import NetworkConnectivityGUI
        print("✅ Network Connectivity import successful")
        return True
    except Exception as e:
        print(f"❌ Network Connectivity import failed: {e}")
        return False

def test_organize():
    """Test Organize tool import."""
    try:
        from src.tools.file_operations.organize.organize import OrganizeWindow
        print("✅ Organize tool import successful")
        return True
    except Exception as e:
        print(f"❌ Organize tool import failed: {e}")
        return False

def test_basic_import():
    """Test basic import without path issues."""
    try:
        # Add src to path if not already there
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        from src.tools.file_management.file_finder import FileFinderGUI
        print("✅ Basic File Finder import (from utilities) successful")
        return True
    except Exception as e:
        print(f"❌ Basic File Finder import failed: {e}")
        return False

def main():
    print("🔍 Tool Import Diagnostic Test")
    print("=" * 50)
    
    tests = [
        test_basic_import,
        test_file_finder,
        test_organize,
        test_network_transfer,
        test_network_connectivity
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed < len(tests):
        print("\n🔧 Suggested fixes:")
        print("1. Check if all required __init__.py files exist")
        print("2. Verify module structure is correct")
        print("3. Ensure no circular imports")
        print("4. Check for syntax errors in modules")

if __name__ == "__main__":
    main()
