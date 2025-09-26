#!/usr/bin/env python3
"""
Simple test for the consolidated RFU Hub.
"""

import sys
import os

def test_syntax():
    """Test if the hub file has valid Python syntax."""
    try:
        with open("src/rfu/hub_consolidated.py", 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, "src/rfu/hub_consolidated.py", "exec")
        print("✓ Hub file has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in hub file: {e}")
        return False
    except FileNotFoundError:
        print("✗ Hub file not found")
        return False
    except UnicodeDecodeError as e:
        print(f"✗ Encoding error in hub file: {e}")
        return False

def test_pyqt5():
    """Test PyQt5 availability."""
    try:
        from PyQt5 import QtWidgets
        print("✓ PyQt5 is available")
        return True
    except ImportError:
        print("✗ PyQt5 is not available")
        return False

def main():
    """Run basic tests."""
    print("=== Basic Hub Validation ===\n")
    
    syntax_ok = test_syntax()
    pyqt_ok = test_pyqt5()
    
    print("\n=== Test Results ===")
    print(f"Syntax validation: {'PASS' if syntax_ok else 'FAIL'}")
    print(f"PyQt5 availability: {'PASS' if pyqt_ok else 'FAIL'}")
    
    if syntax_ok and pyqt_ok:
        print("\n✓ Basic validation passed!")
        print("The consolidated hub has valid syntax and dependencies are available.")
        return True
    else:
        print("\n✗ Validation failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)