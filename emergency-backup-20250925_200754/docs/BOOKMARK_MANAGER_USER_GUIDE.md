# 🧭 Bookmark Manager - User Guide

## Overview
The Bookmark Manager is a comprehensive cross-platform bookmark management tool integrated into Richard's File Utilities. It provides a complete solution for organizing, importing, exporting, and managing web bookmarks with advanced features like tagging, search, and folder organization.

## 🚀 How to Access
1. Open Richard's File Utilities (`python main.py`)
2. Click on the **"Network Tools"** tab
3. Click the **"Bookmark Manager"** button

## 📋 Key Features

### ✨ Core Functionality
- **Add Bookmarks**: Create new bookmarks with title, URL, description, tags, and folder
- **Edit Bookmarks**: Modify existing bookmark information
- **Delete Bookmarks**: Remove unwanted bookmarks
- **Search & Filter**: Advanced search by title, URL, tags, or description
- **Organization**: Tag-based categorization and folder grouping

### 📥 Import Capabilities
- **Browser HTML Exports**: Import from Chrome, Firefox, Edge, Safari exports
- **JSON Format**: Import structured bookmark data
- **CSV Files**: Import from spreadsheet-formatted bookmark lists
- **Multiple Format Support**: Automatic format detection

### 📤 Export Options
- **HTML Format**: Export for browser import (compatible with all major browsers)
- **JSON Format**: Structured data export for backup or sharing
- **CSV Format**: Spreadsheet-compatible export for analysis

### 🔍 Advanced Features
- **Cross-Platform Storage**: SQLite database for reliable local storage
- **Tag Management**: Organize bookmarks with multiple tags
- **Folder Hierarchy**: Group bookmarks into logical folders
- **Search Filters**: Filter by specific fields or search all content
- **Date Tracking**: Automatic creation and modification timestamps

## 🛠️ Usage Instructions

### Adding a New Bookmark
1. Click the **"Add Bookmark"** button
2. Fill in the required information:
   - **Title**: Descriptive name for the bookmark
   - **URL**: Complete web address (https://example.com)
   - **Description**: Optional detailed description
   - **Tags**: Comma-separated tags (programming, reference, tools)
   - **Folder**: Organization folder (Default, Work, Personal, etc.)
3. Click **"OK"** to save

### Editing Bookmarks
1. Select a bookmark from the list
2. Click **"Edit"** button or double-click the bookmark
3. Modify the information as needed
4. Click **"OK"** to save changes

### Searching and Filtering
1. Use the **search box** in the toolbar for quick searches
2. Select search scope from dropdown:
   - All Fields (default)
   - Title only
   - URL only
   - Tags only
   - Description only
3. Use the **Folders** panel to filter by specific folders
4. Use the **Tags** panel to filter by specific tags

### Importing Bookmarks

#### From Browser HTML Export
1. Export bookmarks from your browser:
   - **Chrome**: Menu → Bookmarks → Bookmark Manager → Export bookmarks
   - **Firefox**: Menu → Library → Bookmarks → Show All Bookmarks → Import and Backup → Export Bookmarks to HTML
   - **Edge**: Menu → Favorites → Manage favorites → Export favorites
2. In Bookmark Manager, click **"Import"**
3. Select the HTML file
4. Bookmarks will be organized by their original folder structure

#### From JSON/CSV Files
1. Click **"Import"** button
2. Select your JSON or CSV file
3. Review imported bookmarks
4. Organize as needed

### Exporting Bookmarks
1. Click **"Export"** button
2. Choose format:
   - **HTML**: For importing into browsers
   - **JSON**: For backup or sharing with other tools
   - **CSV**: For spreadsheet analysis
3. Select save location
4. File will be created with all your bookmarks

## 📁 Data Storage
- **Location**: `~/.rfu_bookmarks/bookmarks.db` (SQLite database)
- **Backup**: Regular exports recommended
- **Portability**: Database file can be copied between systems
- **Security**: Local storage only, no cloud dependency

## 🔧 Technical Details

### Database Schema
- **Bookmarks Table**: id, title, url, description, tags, folder, created_date, modified_date, visit_count, favorite
- **Tags Table**: tag management and organization
- **Folders Table**: hierarchical folder structure

### Supported Import Formats
- **HTML**: Standard browser bookmark export format
- **JSON**: Structured bookmark data with full metadata
- **CSV**: Simple comma-separated values with standard columns

### Export Compatibility
- **HTML exports** work with all major browsers
- **JSON exports** maintain full metadata and can be re-imported
- **CSV exports** are compatible with Excel, Google Sheets, and other tools

## 🚨 Tips & Best Practices

### Organization
- Use descriptive **titles** for easy identification
- Apply relevant **tags** for flexible categorization
- Create logical **folder** structures
- Add **descriptions** for complex or technical bookmarks

### Maintenance
- Regular exports for backup
- Periodic cleanup of outdated bookmarks
- Consistent tagging conventions
- Use search to identify duplicates

### Import/Export
- Export before major changes as backup
- Use HTML format for browser compatibility
- Use JSON format for complete data preservation
- Tag imported bookmarks for easier identification

## ⚠️ Troubleshooting

### Common Issues
1. **Import fails**: Check file format and encoding (UTF-8 recommended)
2. **Database errors**: Ensure write permissions in user directory
3. **Missing bookmarks**: Check folder filters and search terms
4. **Export issues**: Verify destination folder write permissions

### Error Resolution
- Restart the application if database locks occur
- Check file permissions for import/export operations
- Verify URL formats include proper protocol (http:// or https://)
- Ensure sufficient disk space for database operations

## 🔮 Future Enhancements
- Cloud synchronization options
- Duplicate detection and removal
- Dead link checking
- Website preview thumbnails
- Bookmark sharing and collaboration
- Browser extension integration
- Automated backup scheduling

## 📞 Support
For issues or questions about the Bookmark Manager:
1. Check this documentation first
2. Run the integration test: `python test_bookmark_simple.py`
3. Review application logs for error details
4. Report issues with specific error messages and steps to reproduce

---

*Bookmark Manager v1.0 - Part of Richard's File Utilities*
*Integrated into Network Tools tab for convenient access*
