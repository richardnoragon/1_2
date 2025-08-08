#!/usr/bin/env python3
"""
Test script for Bookmark Manager Integration

This script tests the bookmark manager functionality to ensure it's properly integrated.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path using absolute path resolution
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_bookmark_manager_import():
    """Test importing the bookmark manager module"""
    try:
        from src.utilities.network.bookmark_manager import BookmarkManagerGUI, BookmarkModel
        print("✅ Successfully imported BookmarkManagerGUI and BookmarkModel")
        return True
    except ImportError as e:
        print(f"❌ Failed to import bookmark manager: {e}")
        return False

def test_bookmark_model_functionality():
    """Test basic bookmark model functionality"""
    try:
        from src.utilities.network.bookmark_manager import BookmarkModel
        
        # Create test database
        model = BookmarkModel("test_bookmarks.db")
        print("✅ BookmarkModel created successfully")
        
        # Test adding a bookmark
        success = model.add_bookmark(
            title="Test Bookmark",
            url="https://example.com",
            description="Test description",
            tags="test, example",
            folder="Test Folder"
        )
        
        if success:
            print("✅ Successfully added test bookmark")
        else:
            print("❌ Failed to add test bookmark")
            return False
        
        # Test retrieving bookmarks
        bookmarks = model.get_all_bookmarks()
        if bookmarks:
            print(f"✅ Successfully retrieved {len(bookmarks)} bookmarks")
            print(f"   First bookmark: {bookmarks[0]['title']}")
        else:
            print("❌ Failed to retrieve bookmarks")
            return False
        
        # Test searching
        search_results = model.search_bookmarks("Test", "title")
        if search_results:
            print(f"✅ Search functionality working - found {len(search_results)} results")
        else:
            print("❌ Search functionality failed")
            return False
        
        # Clean up test database
        try:
            os.remove("test_bookmarks.db")
            print("✅ Cleaned up test database")
        except OSError:
            # File may not exist or permission issue, continue cleanup
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Bookmark model test failed: {e}")
        return False

def test_bookmark_gui_creation():
    """Test creating the bookmark manager GUI"""
    try:
        from PyQt5.QtWidgets import QApplication
        from src.utilities.network.bookmark_manager import BookmarkManagerGUI
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create bookmark manager GUI
        bookmark_gui = BookmarkManagerGUI()
        print("✅ BookmarkManagerGUI created successfully")
        
        # Test that it has the expected attributes
        if hasattr(bookmark_gui, 'model'):
            print("✅ BookmarkManagerGUI has model attribute")
        else:
            print("❌ BookmarkManagerGUI missing model attribute")
            return False
        
        if hasattr(bookmark_gui, 'bookmark_table'):
            print("✅ BookmarkManagerGUI has bookmark_table attribute")
        else:
            print("❌ BookmarkManagerGUI missing bookmark_table attribute")
            return False
        
        # Close the GUI
        bookmark_gui.close()
        print("✅ BookmarkManagerGUI closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bookmark GUI test failed: {e}")
        return False

def test_import_export_functionality():
    """Test bookmark import/export functionality"""
    try:
        from src.utilities.network.bookmark_manager import BookmarkImporter, BookmarkExporter
        
        # Test creating sample data
        sample_bookmarks = [
            {
                'title': 'Test Bookmark 1',
                'url': 'https://example1.com',
                'description': 'Test description 1',
                'tags': 'test, sample',
                'folder': 'Test Folder'
            },
            {
                'title': 'Test Bookmark 2',
                'url': 'https://example2.com',
                'description': 'Test description 2',
                'tags': 'test, example',
                'folder': 'Test Folder'
            }
        ]
        
        # Test JSON export
        success = BookmarkExporter.export_to_json(sample_bookmarks, "test_export.json")
        if success:
            print("✅ JSON export functionality working")
        else:
            print("❌ JSON export failed")
            return False
        
        # Test JSON import
        imported_bookmarks = BookmarkImporter.import_from_json("test_export.json")
        if imported_bookmarks and len(imported_bookmarks) == 2:
            print(f"✅ JSON import functionality working - imported {len(imported_bookmarks)} bookmarks")
        else:
            print("❌ JSON import failed")
            return False
        
        # Test CSV export
        success = BookmarkExporter.export_to_csv(sample_bookmarks, "test_export.csv")
        if success:
            print("✅ CSV export functionality working")
        else:
            print("❌ CSV export failed")
            return False
        
        # Test CSV import
        imported_bookmarks = BookmarkImporter.import_from_csv("test_export.csv")
        if imported_bookmarks and len(imported_bookmarks) == 2:
            print(f"✅ CSV import functionality working - imported {len(imported_bookmarks)} bookmarks")
        else:
            print("❌ CSV import failed")
            return False
        
        # Clean up test files
        try:
            os.remove("test_export.json")
            os.remove("test_export.csv")
            print("✅ Cleaned up test files")
        except OSError:
            # Files may not exist or permission issue, continue cleanup
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Import/Export test failed: {e}")
        return False

def main():
    """Run all bookmark manager tests"""
    print("🧪 Testing Bookmark Manager Integration")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_bookmark_manager_import),
        ("Model Functionality Test", test_bookmark_model_functionality),
        ("GUI Creation Test", test_bookmark_gui_creation),
        ("Import/Export Test", test_import_export_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Bookmark Manager tests PASSED!")
        print("✅ Bookmark Manager is ready for use in the Network Tools tab")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
