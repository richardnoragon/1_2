#!/usr/bin/env python3
"""
Test script for the consolidated RFU Hub to verify basic functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hub_import():
    """Test if the hub can be imported successfully."""
    try:
        # Test PyQt5 availability
        try:
            from PyQt5 import QtWidgets, QtCore, QtGui
            print("✓ PyQt5 is available")
            pyqt_available = True
        except ImportError:
            print("✗ PyQt5 is not available")
            pyqt_available = False
            return False
        
        # Test hub import
        try:
            # Direct import approach
            exec(open("src/rfu/hub.py.new").read(), globals())
            print("✓ Hub module loaded successfully")
            
            # Test class instantiation
            if pyqt_available:
                app = QtWidgets.QApplication.instance()
                if app is None:
                    app = QtWidgets.QApplication(sys.argv)
                
                hub = hub_module.RFUHub()
                print("✓ RFUHub class instantiated successfully")
                print(f"✓ Hub window title: {hub.windowTitle()}")
                print(f"✓ Hub has {hub.tab_widget.count()} tabs")
                
                # Test tab names
                tab_names = []
                for i in range(hub.tab_widget.count()):
                    tab_names.append(hub.tab_widget.tabText(i))
                print(f"✓ Tab names: {', '.join(tab_names)}")
                
                # Clean up
                hub.close()
                app.quit() if app else None
                
            return True
            
        except Exception as e:
            print(f"✗ Error loading hub module: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_menu_system():
    """Test the menu system functionality."""
    try:
        print("\n--- Testing Menu System ---")
        import importlib.util
        spec = importlib.util.spec_from_file_location("hub", "src/rfu/hub.py.new")
        hub_module = importlib.util.module_from_spec(spec)
        sys.modules["hub"] = hub_module
        spec.loader.exec_module(hub_module)
        
        # Test SimpleMenuManager
        menu_manager = hub_module.SimpleMenuManager()
        print("✓ SimpleMenuManager created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing menu system: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=== RFU Hub Consolidation Test ===\n")
    
    # Test basic functionality
    print("--- Testing Basic Functionality ---")
    basic_test = test_hub_import()
    
    # Test menu system
    menu_test = test_menu_system()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Basic functionality: {'PASS' if basic_test else 'FAIL'}")
    print(f"Menu system: {'PASS' if menu_test else 'FAIL'}")
    
    if basic_test and menu_test:
        print("\n✓ All tests passed! The consolidated hub is working correctly.")
        return True
    else:
        print("\n✗ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)