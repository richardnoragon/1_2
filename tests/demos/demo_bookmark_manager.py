#!/usr/bin/env python3
"""
Bookmark Manager Demo

This script demonstrates the bookmark manager functionality by creating sample data.
"""

import sys
from pathlib import Path

# Add src directory to Python path using absolute path resolution
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def create_sample_bookmarks():
    """Create sample bookmarks for demonstration"""
    try:
        from src.tools.network.bookmark_manager import BookmarkModel
        
        model = BookmarkModel()
        
        # Sample bookmarks to add
        sample_bookmarks = [
            {
                "title": "GitHub",
                "url": "https://github.com",
                "description": "GitHub is where developers build, ship, and maintain software",
                "tags": "development, git, programming, collaboration",
                "folder": "Development"
            },
            {
                "title": "Stack Overflow", 
                "url": "https://stackoverflow.com",
                "description": "Q&A platform for programmers",
                "tags": "programming, help, community, q&a",
                "folder": "Development"
            },
            {
                "title": "Python Documentation",
                "url": "https://docs.python.org",
                "description": "Official Python language documentation",
                "tags": "python, documentation, reference",
                "folder": "Documentation"
            },
            {
                "title": "MDN Web Docs",
                "url": "https://developer.mozilla.org",
                "description": "Web development resources and documentation",
                "tags": "web, html, css, javascript, documentation",
                "folder": "Documentation"
            },
            {
                "title": "Visual Studio Code",
                "url": "https://code.visualstudio.com",
                "description": "Free source code editor with debugging support",
                "tags": "editor, ide, development, microsoft",
                "folder": "Tools"
            },
            {
                "title": "RegExr",
                "url": "https://regexr.com",
                "description": "Online regular expression tester and debugger",
                "tags": "regex, testing, development, tools",
                "folder": "Tools"
            },
            {
                "title": "Can I Use",
                "url": "https://caniuse.com",
                "description": "Browser support tables for web technologies",
                "tags": "web, compatibility, browser, reference",
                "folder": "Reference"
            },
            {
                "title": "Lorem Ipsum Generator",
                "url": "https://www.lipsum.com",
                "description": "Generate placeholder text for designs",
                "tags": "design, placeholder, text, lorem",
                "folder": "Tools"
            }
        ]
        
        added_count = 0
        for bookmark in sample_bookmarks:
            if model.add_bookmark(**bookmark):
                added_count += 1
                print(f"✅ Added: {bookmark['title']}")
            else:
                print(f"❌ Failed to add: {bookmark['title']}")
        
        print(f"\n🎉 Successfully added {added_count}/{len(sample_bookmarks)} sample bookmarks!")
        
        # Show summary
        all_bookmarks = model.get_all_bookmarks()
        folders = model.get_all_folders()
        tags = model.get_all_tags()
        
        print(f"\n📊 Bookmark Database Summary:")
        print(f"   Total bookmarks: {len(all_bookmarks)}")
        print(f"   Folders: {len(folders)} ({', '.join(folders)})")
        print(f"   Unique tags: {len(tags)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample bookmarks: {e}")
        return False

def launch_bookmark_manager():
    """Launch the bookmark manager GUI"""
    try:
        from PyQt5.QtWidgets import QApplication
        from src.tools.network.bookmark_manager import BookmarkManagerGUI
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show bookmark manager
        bookmark_manager = BookmarkManagerGUI()
        bookmark_manager.show()
        
        print("🚀 Bookmark Manager launched!")
        print("   The GUI window should now be visible.")
        print("   Close the window to end the demo.")
        
        # Run the application
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching bookmark manager: {e}")
        return 1

def main():
    """Main demo function"""
    print("🧭 Bookmark Manager Demo")
    print("=" * 50)
    
    print("\n1️⃣ Creating sample bookmarks...")
    if create_sample_bookmarks():
        print("✅ Sample data created successfully!")
    else:
        print("❌ Failed to create sample data")
        return 1
    
    print("\n2️⃣ Launching Bookmark Manager GUI...")
    return launch_bookmark_manager()

if __name__ == '__main__':
    sys.exit(main())
