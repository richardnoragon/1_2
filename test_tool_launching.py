#!/usr/bin/env python3
"""
Test script to verify that tool launching works properly in the dialog hub interface.
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_tool_imports():
    """Test importing the key tools to verify they can be launched."""
    print("🧪 Testing Tool Import Capabilities...")
    print("=" * 60)
    
    tools_to_test = [
        # File Management Tools
        ("File Finder", "src.tools.file_management.file_finder", "FileFinderGUI"),
        ("Catalog Files", "src.tools.file_management.catalog_tool", "CatalogWindow"),
        ("Rename Files", "src.tools.file_management.rename", "RenameWindow"),
        ("Organize Files", "src.tools.file_management.organize", "OrganizeWindow"),
        
        # Analysis Tools
        ("Size Analyzer", "src.tools.analysis.size_analyzer", "SizeAnalyzerGUI"),
        ("Duplicate Finder", "src.tools.analysis.find_duplicate_files", "DuplicateFinderApp"),
        ("File Checksum", "src.tools.analysis.check_sum", "ChecksumGUI"),
        ("Empty Folders", "src.tools.analysis.empty_folders", "EmptyFoldersGUI"),
    ]
    
    successful_imports = 0
    failed_imports = 0
    
    for tool_name, module_path, class_name in tools_to_test:
        try:
            # Test direct import
            try:
                module = __import__(module_path, fromlist=[class_name])
                if hasattr(module, class_name):
                    print(f"✅ {tool_name}: Import successful ({module_path}.{class_name})")
                    successful_imports += 1
                else:
                    print(f"❌ {tool_name}: Class {class_name} not found in {module_path}")
                    failed_imports += 1
            except ImportError:
                # Try without src prefix
                alt_module_path = module_path.replace('src.', '')
                try:
                    module = __import__(alt_module_path, fromlist=[class_name])
                    if hasattr(module, class_name):
                        print(f"✅ {tool_name}: Import successful ({alt_module_path}.{class_name})")
                        successful_imports += 1
                    else:
                        print(f"❌ {tool_name}: Class {class_name} not found in {alt_module_path}")
                        failed_imports += 1
                except ImportError as e:
                    print(f"❌ {tool_name}: Import failed - {e}")
                    failed_imports += 1
                    
        except Exception as e:
            print(f"❌ {tool_name}: Unexpected error - {e}")
            failed_imports += 1
    
    print("\n" + "=" * 60)
    print(f"📊 IMPORT TEST RESULTS:")
    print(f"  ✅ Successful imports: {successful_imports}")
    print(f"  ❌ Failed imports: {failed_imports}")
    print(f"  📈 Success rate: {(successful_imports/(successful_imports+failed_imports)*100):.1f}%")
    
    if successful_imports > 0:
        print(f"\n🎉 SUCCESS: {successful_imports} tools can be launched from the dialog hub!")
        print("\n📋 USAGE INSTRUCTIONS:")
        print("1. Run 'python main.py' to start the application")
        print("2. Choose 'Dialog-Based Hub Interface' in the startup dialog")
        print("3. Navigate to the File Management or Analysis tabs")
        print("4. Click the 'Launch' button on any of the successfully imported tools")
        print("5. The tools should now open in their own windows")
        
        if failed_imports > 0:
            print(f"\n⚠️  NOTE: {failed_imports} tools have import issues and may not launch properly")
            print("   These tools may need their module paths or class names corrected")
    else:
        print(f"\n❌ ISSUE: No tools could be imported successfully")
        print("   This indicates a structural problem with the tool organization")
    
    return successful_imports > 0

def test_pyqt5_availability():
    """Test PyQt5 availability for GUI tools."""
    print(f"\n🖥️  Testing PyQt5 Availability...")
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        print("✅ PyQt5 is available and ready for GUI tools")
        return True
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        print("   Install PyQt5 with: pip install PyQt5")
        return False

if __name__ == "__main__":
    print("Tool Launch Capability Test")
    print("=" * 60)
    
    pyqt5_ok = test_pyqt5_availability()
    import_ok = test_tool_imports()
    
    print(f"\n" + "=" * 60)
    if pyqt5_ok and import_ok:
        print("🎉 OVERALL RESULT: Tool launching should work properly!")
        print("   You can now launch tools from the dialog hub interface.")
    else:
        print("❌ OVERALL RESULT: There are issues that need to be resolved.")
        if not pyqt5_ok:
            print("   - PyQt5 needs to be installed")
        if not import_ok:
            print("   - Tool import paths need to be corrected")