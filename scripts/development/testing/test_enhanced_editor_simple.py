#!/usr/bin/env python3
"""
Simple test for Enhanced Editor integration
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication

def main():
    """Test Enhanced Editor integration."""
    try:
        # Create QApplication first
        app = QApplication(sys.argv)
        
        # Import and create Enhanced Editor
        from src.utilities.file_operations.enhanced_editor.enhanced_editor import EnhancedEditor
        editor = EnhancedEditor()
        
        print("✓ Enhanced Editor created successfully!")
        print(f"✓ Window title: {editor.windowTitle()}")
        
        # Test creating a document
        doc_id = editor.new_document("Hello, Enhanced Editor!")
        print(f"✓ Document created: {doc_id}")
        
        # Show the editor
        editor.show()
        print("✓ Enhanced Editor window displayed!")
        
        # For automated testing, close immediately
        editor.close()
        print("✓ Integration test successful!")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)