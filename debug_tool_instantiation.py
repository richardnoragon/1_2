#!/usr/bin/env python3
"""
Direct test of tool instantiation to debug the 'title' parameter issue.
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def debug_tool_instantiation():
    """Debug tool instantiation to understand the 'title' parameter issue."""
    print("🔍 Debugging Tool Instantiation Issue...")
    print("=" * 60)
    
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Test the File Finder tool specifically
        print("\n🔧 Testing File Finder tool...")
        
        # Import the module
        from src.tools.file_management.file_finder import FileFinderGUI
        
        print("✅ Import successful")
        print(f"📋 Class: {FileFinderGUI}")
        print(f"📋 MRO: {FileFinderGUI.__mro__}")
        
        # Check the __init__ signature
        import inspect
        sig = inspect.signature(FileFinderGUI.__init__)
        print(f"📋 Constructor signature: {sig}")
        
        # Try to instantiate
        print("\n🚀 Attempting instantiation...")
        try:
            instance = FileFinderGUI()
            print("✅ Instantiation successful!")
            instance.hide()  # Hide immediately
            instance.close()
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
            print(f"❌ Error type: {type(e)}")
            
            # Try to understand the error better
            if hasattr(e, 'args'):
                print(f"❌ Error args: {e.args}")
        
        # Also test the StandardWindow base class
        print(f"\n🔧 Testing StandardWindow base class...")
        try:
            from src.gui.standard_window import StandardWindow
            print(f"📋 StandardWindow: {StandardWindow}")
            
            sig = inspect.signature(StandardWindow.__init__)
            print(f"📋 StandardWindow constructor signature: {sig}")
            
        except Exception as e:
            print(f"❌ StandardWindow import/check failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tool_instantiation()