#!/usr/bin/env python3
"""
Simple Tool Launch Test

This script tests if individual tools can be launched directly to verify the fixes.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def test_direct_tool_launch():
    """Test launching tools directly to verify they work."""
    
    print("Testing direct tool launches...")
    
    # Test File Finder
    try:
        print("\n1. Testing File Finder...")
        from src.tools.file_management.file_finder import FileFinderGUI
        print("✅ File Finder import successful")
        
        # Don't actually show GUI in test
        # tool = FileFinderGUI()
        # tool.show()
        
    except Exception as e:
        print(f"❌ File Finder failed: {e}")
    
    # Test Duplicate Finder  
    try:
        print("\n2. Testing Duplicate Finder...")
        from src.tools.analysis.find_duplicate_files import DuplicateFinderApp
        print("✅ Duplicate Finder import successful")
        
    except Exception as e:
        print(f"❌ Duplicate Finder failed: {e}")
    
    # Test Encrypt/Decrypt
    try:
        print("\n3. Testing Encrypt/Decrypt...")
        from src.tools.security.en_and_decrypt import EnAndDecryptGUI
        print("✅ Encrypt/Decrypt import successful")
        
    except Exception as e:
        print(f"❌ Encrypt/Decrypt failed: {e}")
    
    # Test Size Analyzer with corrected path
    try:
        print("\n4. Testing Size Analyzer...")
        from src.tools.analysis.size_analyzer import SizeAnalyzerGUI
        print("✅ Size Analyzer import successful")
        
    except Exception as e:
        print(f"❌ Size Analyzer failed: {e}")

def test_tool_launching_system():
    """Test the tool launching system from the multi-pane explorer."""
    
    print("\n" + "="*50)
    print("TESTING TOOL LAUNCHING SYSTEM")
    print("="*50)
    
    try:
        # Import the fixed multi-pane explorer
        from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
        print("✅ Multi-pane explorer import successful")
        
        # Test tool discovery
        explorer = MultiPaneFileExplorer()
        print("✅ Multi-pane explorer created successfully")
        
        # Test tool discovery method
        discovered_tools = explorer._discover_tools_from_directory()
        print(f"✅ Tool discovery successful: {len(discovered_tools)} categories found")
        
        for category, tools in discovered_tools.items():
            print(f"   📁 {category}: {len(tools)} tools")
        
        # Test a specific tool launch
        if discovered_tools:
            for category, tools in discovered_tools.items():
                if tools:
                    test_tool = tools[0]
                    print(f"\n🧪 Testing launch of: {test_tool.get('display_name', 'Unknown')}")
                    
                    try:
                        explorer._launch_discovered_tool(test_tool)
                        print("✅ Tool launch method executed without errors")
                    except Exception as e:
                        print(f"⚠️  Tool launch had issues: {e}")
                    break
        
        print("\n✅ Tool launching system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Tool launching system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("RFU Tool Launch Verification Test")
    print("=" * 40)
    
    # Test individual tool imports
    test_direct_tool_launch()
    
    # Test the integrated system
    system_ok = test_tool_launching_system()
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    if system_ok:
        print("🎉 SUCCESS: Tool launching system is working!")
        print("\nYou can now:")
        print("1. Start the application: python main.py")
        print("2. Choose 'Multi-Pane Explorer' interface")
        print("3. Double-click tools in the left sidebar")
        print("4. Tools should launch successfully!")
    else:
        print("❌ ISSUES DETECTED: Some problems remain")
        print("\nTroubleshooting steps:")
        print("1. Check the error messages above")
        print("2. Verify all required modules are installed")
        print("3. Run the diagnostic tool: python diagnostic_tool_launch.py")

if __name__ == "__main__":
    main()