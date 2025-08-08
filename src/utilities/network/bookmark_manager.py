#!/usr/bin/env python3
"""
Bookmark Manager - Cross-platform bookmark keeper/editor/importer

A comprehensive bookmark management tool that supports:
- Add, edit, delete bookmarks
- Search and filter functionality
- Import/export from browsers (HTML, JSON)
- Tag-based organization
- Cross-platform storage with SQLite
"""

import sys
import os
import json
import sqlite3
import csv
import html
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
        QWidget, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
        QLabel, QComboBox, QDateEdit, QGroupBox, QTabWidget, QSplitter,
        QFileDialog, QMessageBox, QInputDialog, QHeaderView, QMenu,
        QTreeWidget, QTreeWidgetItem, QCheckBox, QSpinBox, QProgressBar,
        QFrame, QScrollArea, QToolBar, QStatusBar, QDialog, QDialogButtonBox,
        QListWidget, QListWidgetItem
    )
    from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap, QStandardItemModel, QStandardItem
except ImportError as e:
    print(f"PyQt5 import error: {e}")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow


class BookmarkModel:
    """Data model for bookmark storage and management"""
    
    def __init__(self, db_path: str = None):
        """Initialize bookmark model with SQLite database"""
        if db_path is None:
            # Use application data directory
            app_data = Path.home() / ".rfu_bookmarks"
            app_data.mkdir(exist_ok=True)
            db_path = app_data / "bookmarks.db"
        
        self.db_path = str(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with bookmark tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    tags TEXT,
                    folder TEXT,
                    created_date TEXT,
                    modified_date TEXT,
                    visit_count INTEGER DEFAULT 0,
                    favorite INTEGER DEFAULT 0
                )
            ''')
            
            # Create tags table for better organization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT,
                    created_date TEXT
                )
            ''')
            
            # Create folders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_id INTEGER,
                    created_date TEXT,
                    FOREIGN KEY (parent_id) REFERENCES folders (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error during database initialization: {e}")
            raise
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format and basic structure."""
        try:
            # Strip whitespace
            url = url.strip()
            
            # Check for empty URL
            if not url:
                return False
            
            # Add protocol if missing
            protocols = ('http://', 'https://', 'ftp://', 'file://')
            if not url.startswith(protocols):
                url = 'https://' + url
            
            # Parse URL
            parsed = urlparse(url)
            
            # Validate required components
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for valid characters in netloc
            if any(char in parsed.netloc for char in [' ', '\t', '\n', '\r']):
                return False
            
            # Basic length validation
            if len(url) > 2048:  # Common URL length limit
                return False
            
            return True
            
        except Exception:
            return False
    
    def add_bookmark(self, title: str, url: str, description: str = "",
                     tags: str = "", folder: str = "Default") -> bool:
        """Add a new bookmark with URL validation"""
        try:
            # Validate URL format
            if not self._validate_url(url):
                raise ValueError(f"Invalid URL format: {url}")
            
            # Validate required fields
            if not title.strip():
                raise ValueError("Title cannot be empty")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO bookmarks (title, url, description, tags,
                                     folder, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title.strip(), url.strip(), description, tags,
                  folder, current_time, current_time))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            return False
    
    def update_bookmark(self, bookmark_id: int, title: str, url: str, 
                       description: str = "", tags: str = "", folder: str = "Default") -> bool:
        """Update an existing bookmark"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            cursor.execute('''
                UPDATE bookmarks 
                SET title=?, url=?, description=?, tags=?, folder=?, modified_date=?
                WHERE id=?
            ''', (title, url, description, tags, folder, current_time, bookmark_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating bookmark: {e}")
            return False
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM bookmarks WHERE id=?', (bookmark_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            return False
    
    def get_all_bookmarks(self) -> List[Dict]:
        """Get all bookmarks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, url, description, tags, folder, created_date, modified_date, visit_count, favorite
                FROM bookmarks ORDER BY created_date DESC
            ''')
            
            bookmarks = []
            for row in cursor.fetchall():
                bookmarks.append({
                    'id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'description': row[3],
                    'tags': row[4],
                    'folder': row[5],
                    'created_date': row[6],
                    'modified_date': row[7],
                    'visit_count': row[8],
                    'favorite': row[9]
                })
            
            conn.close()
            return bookmarks
        except Exception as e:
            print(f"Error getting bookmarks: {e}")
            return []
    
    def search_bookmarks(self, query: str, field: str = "all") -> List[Dict]:
        """Search bookmarks by various criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"%{query}%"
            
            if field == "title":
                cursor.execute('SELECT * FROM bookmarks WHERE title LIKE ?', (query,))
            elif field == "url":
                cursor.execute('SELECT * FROM bookmarks WHERE url LIKE ?', (query,))
            elif field == "tags":
                cursor.execute('SELECT * FROM bookmarks WHERE tags LIKE ?', (query,))
            elif field == "description":
                cursor.execute('SELECT * FROM bookmarks WHERE description LIKE ?', (query,))
            else:  # search all fields
                cursor.execute('''
                    SELECT * FROM bookmarks 
                    WHERE title LIKE ? OR url LIKE ? OR tags LIKE ? OR description LIKE ?
                ''', (query, query, query, query))
            
            bookmarks = []
            for row in cursor.fetchall():
                bookmarks.append({
                    'id': row[0], 'title': row[1], 'url': row[2],
                    'description': row[3], 'tags': row[4], 'folder': row[5],
                    'created_date': row[6], 'modified_date': row[7],
                    'visit_count': row[8], 'favorite': row[9]
                })
            
            conn.close()
            return bookmarks
        except Exception as e:
            print(f"Error searching bookmarks: {e}")
            return []
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        try:
            bookmarks = self.get_all_bookmarks()
            all_tags = set()
            for bookmark in bookmarks:
                if bookmark['tags']:
                    tags = [tag.strip() for tag in bookmark['tags'].split(',')]
                    all_tags.update(tags)
            return sorted(list(all_tags))
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
    
    def get_all_folders(self) -> List[str]:
        """Get all unique folders"""
        try:
            bookmarks = self.get_all_bookmarks()
            folders = set()
            for bookmark in bookmarks:
                if bookmark['folder']:
                    folders.add(bookmark['folder'])
            return sorted(list(folders))
        except Exception as e:
            print(f"Error getting folders: {e}")
            return []


class BookmarkImporter:
    """Handle bookmark import from various formats"""
    
    @staticmethod
    def import_from_html(file_path: str) -> List[Dict]:
        """Import bookmarks from HTML file (browser export)"""
        bookmarks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse HTML bookmark structure
            link_pattern = r'<A HREF="([^"]*)"[^>]*>([^<]*)</A>'
            folder_pattern = r'<H3[^>]*>([^<]*)</H3>'
            
            current_folder = "Imported"
            lines = content.split('\n')
            
            for line in lines:
                # Check for folder
                folder_match = re.search(folder_pattern, line, re.IGNORECASE)
                if folder_match:
                    current_folder = folder_match.group(1).strip()
                    continue
                
                # Check for bookmark
                link_match = re.search(link_pattern, line, re.IGNORECASE)
                if link_match:
                    url = link_match.group(1)
                    title = html.unescape(link_match.group(2))
                    
                    bookmarks.append({
                        'title': title,
                        'url': url,
                        'description': '',
                        'tags': '',
                        'folder': current_folder
                    })
        
        except Exception as e:
            print(f"Error importing HTML bookmarks: {e}")
        
        return bookmarks
    
    @staticmethod
    def import_from_json(file_path: str) -> List[Dict]:
        """Import bookmarks from JSON file"""
        bookmarks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Handle different JSON structures
            if isinstance(data, list):
                for item in data:
                    if 'url' in item and 'title' in item:
                        bookmarks.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'description': item.get('description', ''),
                            'tags': item.get('tags', ''),
                            'folder': item.get('folder', 'Imported')
                        })
            elif isinstance(data, dict):
                # Handle nested bookmark structure
                def extract_bookmarks(obj, folder="Imported"):
                    if isinstance(obj, dict):
                        if 'url' in obj and 'title' in obj:
                            bookmarks.append({
                                'title': obj.get('title', ''),
                                'url': obj.get('url', ''),
                                'description': obj.get('description', ''),
                                'tags': obj.get('tags', ''),
                                'folder': folder
                            })
                        else:
                            for key, value in obj.items():
                                if isinstance(value, (dict, list)):
                                    extract_bookmarks(value, key)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_bookmarks(item, folder)
                
                extract_bookmarks(data)
        
        except Exception as e:
            print(f"Error importing JSON bookmarks: {e}")
        
        return bookmarks
    
    @staticmethod
    def import_from_csv(file_path: str) -> List[Dict]:
        """Import bookmarks from CSV file"""
        bookmarks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    bookmarks.append({
                        'title': row.get('title', row.get('Title', '')),
                        'url': row.get('url', row.get('URL', '')),
                        'description': row.get('description', row.get('Description', '')),
                        'tags': row.get('tags', row.get('Tags', '')),
                        'folder': row.get('folder', row.get('Folder', 'Imported'))
                    })
        except Exception as e:
            print(f"Error importing CSV bookmarks: {e}")
        
        return bookmarks


class BookmarkExporter:
    """Handle bookmark export to various formats"""
    
    @staticmethod
    def export_to_html(bookmarks: List[Dict], file_path: str) -> bool:
        """Export bookmarks to HTML format"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                file.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                file.write('<TITLE>Bookmarks</TITLE>\n')
                file.write('<H1>Bookmarks Menu</H1>\n\n')
                file.write('<DL><p>\n')
                
                # Group by folder
                folders = {}
                for bookmark in bookmarks:
                    folder = bookmark.get('folder', 'Default')
                    if folder not in folders:
                        folders[folder] = []
                    folders[folder].append(bookmark)
                
                for folder, folder_bookmarks in folders.items():
                    if folder != 'Default':
                        file.write(f'    <DT><H3>{html.escape(folder)}</H3>\n')
                        file.write('    <DL><p>\n')
                    
                    for bookmark in folder_bookmarks:
                        title = html.escape(bookmark['title'])
                        url = html.escape(bookmark['url'])
                        file.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                    
                    if folder != 'Default':
                        file.write('    </DL><p>\n')
                
                file.write('</DL><p>\n')
            
            return True
        except (IOError, OSError) as e:
            print(f"File operation error exporting to HTML: {e}")
            return False
        except (UnicodeError, UnicodeEncodeError) as e:
            print(f"Encoding error exporting to HTML: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error exporting to HTML: {e}")
            return False
    
    @staticmethod
    def export_to_json(bookmarks: List[Dict], file_path: str) -> bool:
        """Export bookmarks to JSON format"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(bookmarks, file, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            print(f"File operation error exporting to JSON: {e}")
            return False
        except (TypeError, ValueError) as e:
            print(f"JSON serialization error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(bookmarks: List[Dict], file_path: str) -> bool:
        """Export bookmarks to CSV format"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['title', 'url', 'description', 'tags', 'folder', 'created_date']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for bookmark in bookmarks:
                    writer.writerow(bookmark)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False


class BookmarkDialog(QDialog):
    """Dialog for adding/editing bookmarks"""
    
    def __init__(self, parent=None, bookmark=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Bookmark" if not self.bookmark else "Edit Bookmark")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form fields
        form_layout = QGridLayout()
        
        # Title
        form_layout.addWidget(QLabel("Title:"), 0, 0)
        self.title_edit = QLineEdit()
        form_layout.addWidget(self.title_edit, 0, 1)
        
        # URL
        form_layout.addWidget(QLabel("URL:"), 1, 0)
        self.url_edit = QLineEdit()
        form_layout.addWidget(self.url_edit, 1, 1)
        
        # Description
        form_layout.addWidget(QLabel("Description:"), 2, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addWidget(self.description_edit, 2, 1)
        
        # Tags
        form_layout.addWidget(QLabel("Tags:"), 3, 0)
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas")
        form_layout.addWidget(self.tags_edit, 3, 1)
        
        # Folder
        form_layout.addWidget(QLabel("Folder:"), 4, 0)
        self.folder_edit = QLineEdit()
        self.folder_edit.setText("Default")
        form_layout.addWidget(self.folder_edit, 4, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Populate fields if editing
        if self.bookmark:
            self.title_edit.setText(self.bookmark.get('title', ''))
            self.url_edit.setText(self.bookmark.get('url', ''))
            self.description_edit.setPlainText(self.bookmark.get('description', ''))
            self.tags_edit.setText(self.bookmark.get('tags', ''))
            self.folder_edit.setText(self.bookmark.get('folder', 'Default'))
    
    def get_bookmark_data(self):
        """Get bookmark data from form"""
        return {
            'title': self.title_edit.text().strip(),
            'url': self.url_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip(),
            'folder': self.folder_edit.text().strip() or 'Default'
        }


class BookmarkManagerGUI(StandardWindow):
    """Main Bookmark Manager GUI"""
    
    def __init__(self):
        super().__init__(
            title="Bookmark Manager - Richard's File Utilities",
            window_type="utility"
        )
        self.model = BookmarkModel()
        self.current_bookmarks = []
        self.init_ui()
        self.load_bookmarks()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('show_preferences',
                                               self.show_preferences)
            self.menu_manager.register_callback('refresh', self.refresh_view)
            self.menu_manager.register_callback('export_data',
                                               self.export_bookmarks)
            self.menu_manager.register_callback('import_data',
                                               self.import_bookmarks)
    
    def show_preferences(self):
        """Show Bookmark Manager preferences."""
        QMessageBox.information(
            self, "Bookmark Manager Preferences",
            "Bookmark Manager preferences:\n\n"
            "• Default bookmark folders\n"
            "• Import/export formats\n"
            "• Search and filter options\n"
            "• Database backup settings\n\n"
            "Advanced preferences coming soon!"
        )
        
    def refresh_view(self):
        """Refresh the bookmark manager interface."""
        self.load_bookmarks()
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Interface refreshed", 3000)
        QMessageBox.information(self, "Refresh",
                               "Bookmark interface refreshed successfully.")
    
    def init_ui(self):
        """Initialize the user interface"""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Create toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Create main content area
        content_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(content_splitter)
        
        # Left panel - Filters and Categories
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Bookmark list and details
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([250, 750])
        
        # Create status bar
        if not hasattr(self, 'status_bar'):
            self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def create_toolbar(self):
        """Create toolbar with main actions"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        
        # Add bookmark button
        add_btn = QPushButton("Add Bookmark")
        add_btn.clicked.connect(self.add_bookmark)
        toolbar_layout.addWidget(add_btn)
        
        # Edit bookmark button
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_bookmark)
        toolbar_layout.addWidget(edit_btn)
        
        # Delete bookmark button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_bookmark)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addWidget(QFrame())  # Separator
        
        # Import button
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_bookmarks)
        toolbar_layout.addWidget(import_btn)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_bookmarks)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        
        # Search box
        search_label = QLabel("Search:")
        toolbar_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search bookmarks...")
        self.search_box.textChanged.connect(self.search_bookmarks)
        toolbar_layout.addWidget(self.search_box)
        
        return toolbar_widget
    
    def create_left_panel(self):
        """Create left panel with filters and categories"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search filters
        filter_group = QGroupBox("Search Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        self.search_field_combo = QComboBox()
        self.search_field_combo.addItems(["All Fields", "Title", "URL", "Tags", "Description"])
        filter_layout.addWidget(QLabel("Search in:"))
        filter_layout.addWidget(self.search_field_combo)
        
        layout.addWidget(filter_group)
        
        # Folders
        folders_group = QGroupBox("Folders")
        folders_layout = QVBoxLayout(folders_group)
        
        self.folders_list = QListWidget()
        self.folders_list.itemClicked.connect(self.filter_by_folder)
        folders_layout.addWidget(self.folders_list)
        
        layout.addWidget(folders_group)
        
        # Tags
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_list = QListWidget()
        self.tags_list.itemClicked.connect(self.filter_by_tag)
        tags_layout.addWidget(self.tags_list)
        
        layout.addWidget(tags_group)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with bookmark list and details"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Bookmark table
        self.bookmark_table = QTableWidget()
        self.bookmark_table.setColumnCount(6)
        self.bookmark_table.setHorizontalHeaderLabels([
            "Title", "URL", "Tags", "Folder", "Created", "Actions"
        ])
        
        # Configure table
        header = self.bookmark_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # URL column
        
        self.bookmark_table.itemDoubleClicked.connect(self.edit_bookmark)
        layout.addWidget(self.bookmark_table)
        
        return panel
    
    def load_bookmarks(self):
        """Load all bookmarks into the table"""
        self.current_bookmarks = self.model.get_all_bookmarks()
        self.populate_table(self.current_bookmarks)
        self.update_filters()
        self.status_bar.showMessage(f"Loaded {len(self.current_bookmarks)} bookmarks")
    
    def populate_table(self, bookmarks):
        """Populate the bookmark table with data"""
        self.bookmark_table.setRowCount(len(bookmarks))
        
        for row, bookmark in enumerate(bookmarks):
            # Title
            title_item = QTableWidgetItem(bookmark['title'])
            title_item.setData(Qt.UserRole, bookmark['id'])
            self.bookmark_table.setItem(row, 0, title_item)
            
            # URL
            self.bookmark_table.setItem(row, 1, QTableWidgetItem(bookmark['url']))
            
            # Tags
            self.bookmark_table.setItem(row, 2, QTableWidgetItem(bookmark['tags']))
            
            # Folder
            self.bookmark_table.setItem(row, 3, QTableWidgetItem(bookmark['folder']))
            
            # Created date
            created_date = bookmark['created_date'][:10] if bookmark['created_date'] else ''
            self.bookmark_table.setItem(row, 4, QTableWidgetItem(created_date))
            
            # Actions (placeholder)
            self.bookmark_table.setItem(row, 5, QTableWidgetItem(""))
    
    def update_filters(self):
        """Update filter lists with current data"""
        # Update folders list
        self.folders_list.clear()
        folders = self.model.get_all_folders()
        self.folders_list.addItem("All Folders")
        for folder in folders:
            self.folders_list.addItem(folder)
        
        # Update tags list
        self.tags_list.clear()
        tags = self.model.get_all_tags()
        self.tags_list.addItem("All Tags")
        for tag in tags:
            self.tags_list.addItem(tag)
    
    def add_bookmark(self):
        """Add a new bookmark"""
        dialog = BookmarkDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_bookmark_data()
            if data['title'] and data['url']:
                if self.model.add_bookmark(**data):
                    self.load_bookmarks()
                    self.status_bar.showMessage("Bookmark added successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to add bookmark")
            else:
                QMessageBox.warning(self, "Error", "Title and URL are required")
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        current_row = self.bookmark_table.currentRow()
        if current_row >= 0:
            bookmark_id = self.bookmark_table.item(current_row, 0).data(Qt.UserRole)
            bookmark = next((b for b in self.current_bookmarks if b['id'] == bookmark_id), None)
            
            if bookmark:
                dialog = BookmarkDialog(self, bookmark)
                if dialog.exec_() == QDialog.Accepted:
                    data = dialog.get_bookmark_data()
                    if data['title'] and data['url']:
                        if self.model.update_bookmark(bookmark_id, **data):
                            self.load_bookmarks()
                            self.status_bar.showMessage("Bookmark updated successfully")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to update bookmark")
                    else:
                        QMessageBox.warning(self, "Error", "Title and URL are required")
    
    def delete_bookmark(self):
        """Delete selected bookmark"""
        current_row = self.bookmark_table.currentRow()
        if current_row >= 0:
            bookmark_id = self.bookmark_table.item(current_row, 0).data(Qt.UserRole)
            bookmark_title = self.bookmark_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete the bookmark '{bookmark_title}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.model.delete_bookmark(bookmark_id):
                    self.load_bookmarks()
                    self.status_bar.showMessage("Bookmark deleted successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete bookmark")
    
    def search_bookmarks(self):
        """Search bookmarks based on search box input"""
        query = self.search_box.text().strip()
        if query:
            field_map = {
                "All Fields": "all",
                "Title": "title",
                "URL": "url",
                "Tags": "tags",
                "Description": "description"
            }
            field = field_map.get(self.search_field_combo.currentText(), "all")
            bookmarks = self.model.search_bookmarks(query, field)
            self.populate_table(bookmarks)
            self.status_bar.showMessage(f"Found {len(bookmarks)} matching bookmarks")
        else:
            self.load_bookmarks()
    
    def filter_by_folder(self, item):
        """Filter bookmarks by selected folder"""
        folder = item.text()
        if folder == "All Folders":
            self.load_bookmarks()
        else:
            bookmarks = [b for b in self.current_bookmarks if b['folder'] == folder]
            self.populate_table(bookmarks)
            self.status_bar.showMessage(f"Showing {len(bookmarks)} bookmarks in '{folder}'")
    
    def filter_by_tag(self, item):
        """Filter bookmarks by selected tag"""
        tag = item.text()
        if tag == "All Tags":
            self.load_bookmarks()
        else:
            bookmarks = [b for b in self.current_bookmarks 
                        if tag in (b['tags'] or '').split(',')]
            self.populate_table(bookmarks)
            self.status_bar.showMessage(f"Showing {len(bookmarks)} bookmarks with tag '{tag}'")
    
    def import_bookmarks(self):
        """Import bookmarks from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Bookmarks",
            "", "HTML Files (*.html);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.html'):
                    bookmarks = BookmarkImporter.import_from_html(file_path)
                elif file_path.endswith('.json'):
                    bookmarks = BookmarkImporter.import_from_json(file_path)
                elif file_path.endswith('.csv'):
                    bookmarks = BookmarkImporter.import_from_csv(file_path)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format")
                    return
                
                # Add imported bookmarks
                imported_count = 0
                for bookmark in bookmarks:
                    if bookmark['title'] and bookmark['url']:
                        if self.model.add_bookmark(**bookmark):
                            imported_count += 1
                
                self.load_bookmarks()
                self.status_bar.showMessage(f"Imported {imported_count} bookmarks")
                QMessageBox.information(self, "Import Complete", 
                                      f"Successfully imported {imported_count} bookmarks")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import bookmarks: {str(e)}")
    
    def export_bookmarks(self):
        """Export bookmarks to file"""
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "Export Bookmarks",
            "", "HTML Files (*.html);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                bookmarks = self.model.get_all_bookmarks()
                
                success = False
                if file_type.startswith("HTML"):
                    success = BookmarkExporter.export_to_html(bookmarks, file_path)
                elif file_type.startswith("JSON"):
                    success = BookmarkExporter.export_to_json(bookmarks, file_path)
                elif file_type.startswith("CSV"):
                    success = BookmarkExporter.export_to_csv(bookmarks, file_path)
                
                if success:
                    self.status_bar.showMessage(f"Exported {len(bookmarks)} bookmarks")
                    QMessageBox.information(self, "Export Complete", 
                                          f"Successfully exported {len(bookmarks)} bookmarks")
                else:
                    QMessageBox.warning(self, "Export Error", "Failed to export bookmarks")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export bookmarks: {str(e)}")


def main():
    """Main entry point for testing"""
    app = QApplication(sys.argv)
    window = BookmarkManagerGUI()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
