#!/usr/bin/env python3
"""
Simple Bookmark Manager Integration Test

Tests bookmark manager functionality without GUI interference.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import():
    """Test importing bookmark manager components"""
    try:
        from src.tools.network.bookmark_manager import (
            BookmarkModel, BookmarkImporter, BookmarkExporter, BookmarkDialog
        )
        print("✅ Successfully imported all bookmark manager components")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic bookmark model operations"""
    try:
        from src.tools.network.bookmark_manager import BookmarkModel
        
        # Create test database
        model = BookmarkModel("test_bookmarks.db")
        
        # Add a test bookmark
        success = model.add_bookmark(
            title="GitHub",
            url="https://github.com",
            description="GitHub homepage",
            tags="development, git",
            folder="Development"
        )
        
        if not success:
            print("❌ Failed to add bookmark")
            return False
        
        # Get all bookmarks
        bookmarks = model.get_all_bookmarks()
        if not bookmarks or len(bookmarks) == 0:
            print("❌ No bookmarks retrieved")
            return False
        
        print(f"✅ Successfully added and retrieved {len(bookmarks)} bookmark(s)")
        
        # Test search
        search_results = model.search_bookmarks("GitHub", "title")
        if search_results:
            print(f"✅ Search working - found {len(search_results)} results")
        else:
            print("❌ Search failed")
            return False
        
        # Clean up
        try:
            os.remove("test_bookmarks.db")
        except OSError:
            # File may not exist or permission issue, continue
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_import_export():
    """Test import/export functionality"""
    try:
        from src.tools.network.bookmark_manager import BookmarkImporter, BookmarkExporter
        
        # Sample data
        bookmarks = [
            {
                'title': 'Python.org',
                'url': 'https://python.org',
                'description': 'Python official website',
                'tags': 'python, programming',
                'folder': 'Programming',
                'created_date': '2025-01-01',
                'modified_date': '2025-01-01',
                'visit_count': 0,
                'favorite': 0
            }
        ]
        
        # Test JSON export/import
        success = BookmarkExporter.export_to_json(bookmarks, "test.json")
        if success:
            print("✅ JSON export successful")
        else:
            print("❌ JSON export failed")
            return False
        
        imported = BookmarkImporter.import_from_json("test.json")
        if imported and len(imported) > 0:
            print("✅ JSON import successful")
        else:
            print("❌ JSON import failed")
            return False
        
        # Clean up
        try:
            os.remove("test.json")
        except OSError:
            # File may not exist or permission issue, continue
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ Import/export test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Bookmark Manager Integration")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_import),
        ("Basic Functionality", test_basic_functionality),
        ("Import/Export", test_import_export),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            break  # Stop on first failure for debugging
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Bookmark Manager integration SUCCESSFUL!")
        print("✅ Ready to use in Network Tools tab")
        
        # Show usage instructions
        print("\n📋 Usage Instructions:")
        print("1. Open Richard's File Utilities (python main.py)")
        print("2. Click on the 'Network Tools' tab")
        print("3. Click the 'Bookmark Manager' button")
        print("4. Add, edit, organize your bookmarks")
        print("5. Import from browser exports (HTML/JSON)")
        print("6. Export to various formats")
        
    else:
        print("❌ Integration has issues - check errors above")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
