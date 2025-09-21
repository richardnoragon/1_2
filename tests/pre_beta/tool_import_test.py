#!/usr/bin/env python3
"""
Standalone Tool Import Test

Tests the import of all the fixed tools to verify they can be loaded correctly.
This test runs independently of the main application.
"""

import os
import sys

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels from tests/pre_beta
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)

def test_tool_imports():
    """Test importing all the fixed tools."""
    print("RFU Tool Import Test Suite")
    print("=" * 50)
    
    # List of tools to test
    tools = [
        ("Network Connectivity", "src.tools.network.connectivity", "NetworkConnectivityGUI"),
        ("Network Scanner", "src.tools.network.network_scanner", "NetworkScannerGUI"),
        ("Network Transfer", "src.tools.network.network_transfer", "NetworkTransferGUI"),
        ("Bookmark Manager", "src.tools.network.bookmarks", "BookmarkManagerGUI"),
        ("Privacy Cleaner", "src.tools.privacy.privacy_cleaner", "PrivacyCleanerGUI"),
        ("Enhanced Clipboard", "src.tools.system.enhanced_clipboard", "EnhancedClipboardGUI"),
        ("System Diagnostics", "src.tools.system.system_diagnostics", "SystemDiagnosticsGUI"),
    ]
    
    results = []
    
    for tool_name, module_path, class_name in tools:
        print(f"\n=== Testing {tool_name} ===")
        print(f"Module: {module_path}")
        print(f"Class: {class_name}")
        
        try:
            # Import the module
            module = __import__(module_path, fromlist=[class_name])
            print(f"✓ Successfully imported module: {module_path}")
            
            # Get the class
            tool_class = getattr(module, class_name)
            print(f"✓ Successfully found class: {class_name}")
            print(f"✓ Class {class_name} is ready for instantiation")
            
            results.append((tool_name, True))
            
        except ImportError as e:
            print(f"✗ Import error: {e}")
            results.append((tool_name, False))
        except AttributeError as e:
            print(f"✗ Class not found: {e}")
            results.append((tool_name, False))
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append((tool_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("IMPORT TEST SUMMARY")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for tool_name, success in results:
        if success:
            print(f"✓ {tool_name}")
            successful += 1
        else:
            print(f"✗ {tool_name}")
            failed += 1
    
    print(f"\nResults: {successful} successful, {failed} failed out of {len(results)} total")
    
    if failed == 0:
        print("\n🎉 All tools imported successfully!")
        print("The startup issues documented in nice_todo_list.md should now be resolved.")
    else:
        print(f"\n⚠ {failed} tools still have import issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = test_tool_imports()
    print(f"\nTest completed with {'SUCCESS' if success else 'FAILURES'}")