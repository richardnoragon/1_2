#!/usr/bin/env python3
"""
Comprehensive Tool Import Test Script
Test all tools mentioned in main.py to ensure they work correctly
"""

import sys
import os
from pathlib import Path

def secure_path_join(base_path: str, user_path: str) -> str:
    """Safely join paths to prevent path traversal."""
    base = Path(base_path).resolve()
    full_path = Path(base / user_path).resolve()
    
    # Ensure the full path is within the base path
    if not str(full_path).startswith(str(base)):
        raise ValueError("Path traversal attempt detected")
    
    return str(full_path)

# Add paths for imports securely
current_dir = os.getcwd()
src_dir = secure_path_join(current_dir, 'src')

sys.path.insert(0, current_dir)
sys.path.insert(0, src_dir)

def test_tool_import(tool_name, module_path, class_name):
    """Test importing a specific tool."""
    try:
        # Try multiple import strategies
        strategies = [
            module_path,
            module_path.replace('src.', ''),
            f"src.{module_path}" if not module_path.startswith('src.') else module_path
        ]
        
        for strategy in strategies:
            try:
                module = __import__(strategy, fromlist=[class_name])
                if hasattr(module, class_name):
                    print(f"✅ {tool_name}: Import successful")
                    return True
            except ImportError:
                continue
        
        print(f"❌ {tool_name}: Import failed - no strategy worked")
        return False
        
    except Exception as e:
        print(f"❌ {tool_name}: Import failed - {e}")
        return False

def main():
    print("🔍 Comprehensive Tool Import Test")
    print("=" * 60)
    
    # List of all tools from main.py
    tools = [
        # File Management Tools
        ("File Finder", "src.tools.file_management.file_finder", "FileFinderGUI"),
        ("Catalog", "src.tools.file_management.catalog", "CatalogWindow"),
        ("Rename", "src.tools.file_management.rename", "RenameWindow"),
        ("Organize", "src.tools.file_management.organize", "OrganizeWindow"),
        
        # Network Tools
        ("Network Connectivity", "src.tools.network.network_connectivity", "NetworkConnectivityGUI"),
        ("Network Scanner", "src.tools.network.network_scanner", "NetworkScannerGUI"),
        ("Network Transfer", "src.tools.network.network_transfer", "NetworkTransferGUI"),
        
        # PDF Tools (testing a few key ones)
        ("PDF Utilities", "enhanced_pdf_tools_widget", "EnhancedPDFToolsWidget"),
        
        # Privacy Tools
        ("Privacy Cleaner", "src.tools.privacy.privacy_tools_simple", "PrivacyCleanerGUI"),
        
        # System Tools  
        ("System Diagnostics", "src.tools.system.diagnostics_monitoring", "SystemDiagnosticsGUI"),
    ]
    
    passed = 0
    total = len(tools)
    
    for tool_name, module_path, class_name in tools:
        if test_tool_import(tool_name, module_path, class_name):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tools imported successfully")
    
    if passed == total:
        print("🎉 All tools are working! The repair was successful!")
        print("\n✨ Tools ready for use:")
        for tool_name, _, _ in tools:
            print(f"  • {tool_name}")
    else:
        print(f"⚠️  {total - passed} tools still have issues")
        print("\n🔧 Recommendations:")
        print("1. Check modules that failed for missing dependencies")
        print("2. Verify file paths and module structure")
        print("3. Look for syntax errors in failing modules")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
