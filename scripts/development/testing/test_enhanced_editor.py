#!/usr/bin/env python3
"""
Test script for Enhanced Editor integration with RFU
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication

def test_enhanced_editor_import():
    """Test importing the Enhanced Editor module."""
    try:
        from src.utilities.file_operations.enhanced_editor.enhanced_editor import EnhancedEditor
        print("✓ Successfully imported EnhancedEditor class")
        return EnhancedEditor
    except ImportError as e:
        print(f"✗ Failed to import EnhancedEditor: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error importing EnhancedEditor: {e}")
        return None

def test_enhanced_editor_instantiation(EnhancedEditor):
    """Test creating an instance of Enhanced Editor."""
    try:
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        editor = EnhancedEditor()
        print("✓ Successfully created EnhancedEditor instance")
        return editor
    except Exception as e:
        print(f"✗ Failed to create EnhancedEditor instance: {e}")
        return None

def test_enhanced_editor_functionality(editor):
    """Test basic Enhanced Editor functionality."""
    try:
        # Test creating a new document
        doc_id = editor.new_document("Test content", None)
        print(f"✓ Successfully created new document: {doc_id}")
        
        # Test document manager
        document = editor.document_manager.get_document(doc_id)
        if document:
            print("✓ Document manager working correctly")
        else:
            print("✗ Document manager not working")
            
        # Test current editor
        current_editor = editor.get_current_editor()
        if current_editor:
            print("✓ Text editor widget working correctly")
        else:
            print("✗ Text editor widget not working")
            
        # Test setting content
        current_editor.setPlainText("Hello, Enhanced Editor!")
        content = current_editor.toPlainText()
        if "Hello, Enhanced Editor!" in content:
            print("✓ Text editing functionality working")
        else:
            print("✗ Text editing functionality not working")
            
        return True
    except Exception as e:
        print(f"✗ Error testing Enhanced Editor functionality: {e}")
        return False

def test_enhanced_editor_window(editor):
    """Test Enhanced Editor window display."""
    try:
        editor.show()
        print("✓ Enhanced Editor window displayed successfully")
        
        # Test window properties
        title = editor.windowTitle()
        if "Enhanced Editor" in title:
            print(f"✓ Window title correct: {title}")
        else:
            print(f"✗ Window title incorrect: {title}")
            
        return True
    except Exception as e:
        print(f"✗ Error displaying Enhanced Editor window: {e}")
        return False

def main():
    """Main test function."""
    print("Testing Enhanced Editor Integration...")
    print("=" * 50)
    
    # Test import
    EnhancedEditor = test_enhanced_editor_import()
    if not EnhancedEditor:
        print("Import test failed. Cannot continue.")
        return False
    
    print()
    
    # Test instantiation
    editor = test_enhanced_editor_instantiation(EnhancedEditor)
    if not editor:
        print("Instantiation test failed. Cannot continue.")
        return False
    
    print()
    
    # Test functionality
    func_test = test_enhanced_editor_functionality(editor)
    if not func_test:
        print("Functionality test failed.")
    
    print()
    
    # Test window display
    window_test = test_enhanced_editor_window(editor)
    if not window_test:
        print("Window display test failed.")
    
    print()
    print("=" * 50)
    if func_test and window_test:
        print("✓ All tests passed! Enhanced Editor integration successful.")
        return True
    else:
        print("✗ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    # Keep the window open for visual inspection
    app = QApplication.instance()
    if app:
        print("\nPress Ctrl+C to exit or close the window.")
        try:
            sys.exit(app.exec_())
        except KeyboardInterrupt:
            print("\nTest completed.")