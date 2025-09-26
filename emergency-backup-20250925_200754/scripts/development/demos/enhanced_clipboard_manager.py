"""
Enhanced Clipboard Manager - Comprehensive clipboard management system with multi-panel interface,
searchable database, cloud sync, advanced features, and System Tools integration.

Author: Richard's File Utilities
Version: 1.0.0
Date: August 7, 2025
"""

import sys
import os
import json
import sqlite3
import hashlib
import threading
import time
import base64
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
import tempfile
import subprocess
import shutil
from urllib.parse import urlparse
from io import BytesIO

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image, ImageQt
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ClipboardItem:
    """Represents a single clipboard item with metadata and content."""
    
    def __init__(self, content: str, item_type: str = "text", source_app: str = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.item_type = item_type  # text, image, file, url, html, etc.
        self.preview = self._generate_preview(content, item_type)
        self.timestamp = datetime.now()
        self.pinned = False
        self.source_app = source_app or "Unknown"
        self.meta = {}
        self.tags = []
        self.category = "General"
        self.rating = 0
        self.access_count = 0
        self.last_accessed = None
        self.encrypted = False
        self.size = len(content.encode('utf-8')) if isinstance(content, str) else len(content)
        
    def _generate_preview(self, content: str, item_type: str) -> str:
        """Generate a preview string for the clipboard item."""
        if item_type == "text":
            return content[:100] + "..." if len(content) > 100 else content
        elif item_type == "image":
            return f"Image ({self._get_image_info(content)})"
        elif item_type == "file":
            return f"File: {os.path.basename(content)}"
        elif item_type == "url":
            return f"URL: {content}"
        elif item_type == "html":
            # Strip HTML tags for preview
            import re
            clean = re.compile('<.*?>')
            text = re.sub(clean, '', content)
            return text[:100] + "..." if len(text) > 100 else text
        else:
            return str(content)[:100] + "..." if len(str(content)) > 100 else str(content)
    
    def _get_image_info(self, content: str) -> str:
        """Get image information for preview."""
        try:
            if PIL_AVAILABLE and content.startswith('data:image'):
                # Handle base64 encoded images
                header, data = content.split(',', 1)
                image_data = base64.b64decode(data)
                image = Image.open(BytesIO(image_data))
                return f"{image.width}x{image.height}"
            return "Unknown size"
        except:
            return "Unknown"
    
    def to_dict(self) -> Dict:
        """Convert clipboard item to dictionary for serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'item_type': self.item_type,
            'preview': self.preview,
            'timestamp': self.timestamp.isoformat(),
            'pinned': self.pinned,
            'source_app': self.source_app,
            'meta': self.meta,
            'tags': self.tags,
            'category': self.category,
            'rating': self.rating,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'encrypted': self.encrypted,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClipboardItem':
        """Create clipboard item from dictionary."""
        item = cls(data['content'], data['item_type'], data.get('source_app'))
        item.id = data['id']
        item.preview = data['preview']
        item.timestamp = datetime.fromisoformat(data['timestamp'])
        item.pinned = data['pinned']
        item.meta = data.get('meta', {})
        item.tags = data.get('tags', [])
        item.category = data.get('category', 'General')
        item.rating = data.get('rating', 0)
        item.access_count = data.get('access_count', 0)
        item.last_accessed = datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None
        item.encrypted = data.get('encrypted', False)
        item.size = data.get('size', 0)
        return item


class ClipboardDatabase:
    """SQLite database manager for clipboard items."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists and has correct schema."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    preview TEXT,
                    timestamp TEXT NOT NULL,
                    pinned BOOLEAN DEFAULT FALSE,
                    source_app TEXT,
                    meta TEXT,
                    tags TEXT,
                    category TEXT DEFAULT 'General',
                    rating INTEGER DEFAULT 0,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    encrypted BOOLEAN DEFAULT FALSE,
                    size INTEGER DEFAULT 0
                )
            ''')
            
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    variables TEXT,
                    category TEXT DEFAULT 'General',
                    created_at TEXT NOT NULL,
                    last_used TEXT
                )
            ''')
            
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create indexes for better performance
            self.connection.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON clipboard_items(timestamp)')
            self.connection.execute('CREATE INDEX IF NOT EXISTS idx_pinned ON clipboard_items(pinned)')
            self.connection.execute('CREATE INDEX IF NOT EXISTS idx_category ON clipboard_items(category)')
            self.connection.execute('CREATE INDEX IF NOT EXISTS idx_item_type ON clipboard_items(item_type)')
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def add_item(self, item: ClipboardItem) -> bool:
        """Add clipboard item to database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO clipboard_items 
                (id, content, item_type, preview, timestamp, pinned, source_app, 
                 meta, tags, category, rating, access_count, last_accessed, encrypted, size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.id, item.content, item.item_type, item.preview,
                item.timestamp.isoformat(), item.pinned, item.source_app,
                json.dumps(item.meta), json.dumps(item.tags), item.category,
                item.rating, item.access_count,
                item.last_accessed.isoformat() if item.last_accessed else None,
                item.encrypted, item.size
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding item to database: {e}")
            return False
    
    def get_items(self, limit: int = None, pinned_only: bool = False, 
                  category: str = None, item_type: str = None) -> List[ClipboardItem]:
        """Retrieve clipboard items from database."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM clipboard_items WHERE 1=1"
            params = []
            
            if pinned_only:
                query += " AND pinned = ?"
                params.append(True)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if item_type:
                query += " AND item_type = ?"
                params.append(item_type)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                item_data = {
                    'id': row[0], 'content': row[1], 'item_type': row[2],
                    'preview': row[3], 'timestamp': row[4], 'pinned': row[5],
                    'source_app': row[6], 'meta': json.loads(row[7] or '{}'),
                    'tags': json.loads(row[8] or '[]'), 'category': row[9],
                    'rating': row[10], 'access_count': row[11], 
                    'last_accessed': row[12], 'encrypted': row[13], 'size': row[14]
                }
                items.append(ClipboardItem.from_dict(item_data))
            
            return items
            
        except Exception as e:
            print(f"Error retrieving items from database: {e}")
            return []
    
    def update_item(self, item: ClipboardItem) -> bool:
        """Update existing clipboard item."""
        return self.add_item(item)  # INSERT OR REPLACE handles updates
    
    def delete_item(self, item_id: str) -> bool:
        """Delete clipboard item from database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting item from database: {e}")
            return False
    
    def search_items(self, query: str, item_type: str = None) -> List[ClipboardItem]:
        """Search clipboard items by content."""
        try:
            cursor = self.connection.cursor()
            sql = """
                SELECT * FROM clipboard_items 
                WHERE (content LIKE ? OR preview LIKE ? OR tags LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if item_type:
                sql += " AND item_type = ?"
                params.append(item_type)
            
            sql += " ORDER BY timestamp DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                item_data = {
                    'id': row[0], 'content': row[1], 'item_type': row[2],
                    'preview': row[3], 'timestamp': row[4], 'pinned': row[5],
                    'source_app': row[6], 'meta': json.loads(row[7] or '{}'),
                    'tags': json.loads(row[8] or '[]'), 'category': row[9],
                    'rating': row[10], 'access_count': row[11], 
                    'last_accessed': row[12], 'encrypted': row[13], 'size': row[14]
                }
                items.append(ClipboardItem.from_dict(item_data))
            
            return items
            
        except Exception as e:
            print(f"Error searching items: {e}")
            return []
    
    def cleanup_expired(self, days: int = 30) -> int:
        """Clean up expired clipboard items."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM clipboard_items 
                WHERE pinned = FALSE AND timestamp < ?
            """, (cutoff_date.isoformat(),))
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error cleaning up expired items: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """Get clipboard usage statistics."""
        try:
            cursor = self.connection.cursor()
            stats = {}
            
            # Total items
            cursor.execute("SELECT COUNT(*) FROM clipboard_items")
            stats['total_items'] = cursor.fetchone()[0]
            
            # Pinned items
            cursor.execute("SELECT COUNT(*) FROM clipboard_items WHERE pinned = TRUE")
            stats['pinned_items'] = cursor.fetchone()[0]
            
            # Items by type
            cursor.execute("SELECT item_type, COUNT(*) FROM clipboard_items GROUP BY item_type")
            stats['by_type'] = dict(cursor.fetchall())
            
            # Items by category
            cursor.execute("SELECT category, COUNT(*) FROM clipboard_items GROUP BY category")
            stats['by_category'] = dict(cursor.fetchall())
            
            # Most accessed items
            cursor.execute("""
                SELECT content, access_count FROM clipboard_items 
                ORDER BY access_count DESC LIMIT 10
            """)
            stats['most_accessed'] = cursor.fetchall()
            
            # Storage usage
            cursor.execute("SELECT SUM(size) FROM clipboard_items")
            stats['total_size'] = cursor.fetchone()[0] or 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


class ClipboardEncryption:
    """Handle encryption/decryption of sensitive clipboard content."""
    
    def __init__(self):
        self.key = None
    
    def set_password(self, password: str) -> bool:
        """Set encryption password and derive key."""
        try:
            if not CRYPTO_AVAILABLE:
                return False
            
            # Derive key from password
            salt = b'clipboard_salt_2025'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self.key = Fernet(key)
            return True
        except Exception as e:
            print(f"Error setting encryption password: {e}")
            return False
    
    def encrypt_content(self, content: str) -> str:
        """Encrypt clipboard content."""
        try:
            if not self.key:
                return content
            
            encrypted_bytes = self.key.encrypt(content.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            print(f"Error encrypting content: {e}")
            return content
    
    def decrypt_content(self, encrypted_content: str) -> str:
        """Decrypt clipboard content."""
        try:
            if not self.key:
                return encrypted_content
            
            encrypted_bytes = base64.b64decode(encrypted_content.encode())
            decrypted_bytes = self.key.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"Error decrypting content: {e}")
            return encrypted_content


class ClipboardCloudSync:
    """Handle cloud synchronization of clipboard data."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.sync_enabled = config.get('sync_enabled', False)
        self.sync_url = config.get('sync_url', '')
        self.api_key = config.get('api_key', '')
        self.device_id = config.get('device_id', str(uuid.uuid4()))
    
    def sync_to_cloud(self, items: List[ClipboardItem]) -> bool:
        """Sync clipboard items to cloud storage."""
        if not self.sync_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            data = {
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'items': [item.to_dict() for item in items if item.pinned]
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.sync_url}/sync",
                json=data,
                headers=headers,
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error syncing to cloud: {e}")
            return False
    
    def sync_from_cloud(self) -> List[ClipboardItem]:
        """Sync clipboard items from cloud storage."""
        if not self.sync_enabled or not REQUESTS_AVAILABLE:
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.sync_url}/sync/{self.device_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return [ClipboardItem.from_dict(item_data) for item_data in data.get('items', [])]
            
            return []
            
        except Exception as e:
            print(f"Error syncing from cloud: {e}")
            return []


class ClipboardTextProcessor:
    """Advanced text processing features for clipboard content."""
    
    @staticmethod
    def convert_case(text: str, case_type: str) -> str:
        """Convert text case."""
        if case_type == "upper":
            return text.upper()
        elif case_type == "lower":
            return text.lower()
        elif case_type == "title":
            return text.title()
        elif case_type == "sentence":
            return text.capitalize()
        elif case_type == "camel":
            words = text.split()
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        elif case_type == "pascal":
            return ''.join(word.capitalize() for word in text.split())
        elif case_type == "snake":
            return '_'.join(text.lower().split())
        elif case_type == "kebab":
            return '-'.join(text.lower().split())
        else:
            return text
    
    @staticmethod
    def format_convert(text: str, format_type: str) -> str:
        """Convert text format."""
        if format_type == "markdown_to_html":
            # Basic markdown to HTML conversion
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
            return text
        elif format_type == "html_to_text":
            # Strip HTML tags
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)
        elif format_type == "url_encode":
            from urllib.parse import quote
            return quote(text)
        elif format_type == "url_decode":
            from urllib.parse import unquote
            return unquote(text)
        elif format_type == "base64_encode":
            return base64.b64encode(text.encode()).decode()
        elif format_type == "base64_decode":
            try:
                return base64.b64decode(text.encode()).decode()
            except:
                return text
        else:
            return text
    
    @staticmethod
    def regex_replace(text: str, pattern: str, replacement: str, flags: int = 0) -> str:
        """Perform regex find and replace."""
        try:
            return re.sub(pattern, replacement, text, flags=flags)
        except Exception as e:
            print(f"Regex error: {e}")
            return text
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers from text."""
        phone_pattern = r'(\+?1?\s?)?(\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4})'
        return [match[0] + match[1] for match in re.findall(phone_pattern, text)]


class ClipboardTemplateManager:
    """Manage clipboard templates with variable substitution."""
    
    def __init__(self, database: ClipboardDatabase):
        self.database = database
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load templates from database."""
        try:
            cursor = self.database.connection.cursor()
            cursor.execute("SELECT * FROM clipboard_templates ORDER BY name")
            rows = cursor.fetchall()
            
            for row in rows:
                template_id, name, content, variables, category, created_at, last_used = row
                self.templates[template_id] = {
                    'id': template_id,
                    'name': name,
                    'content': content,
                    'variables': json.loads(variables or '[]'),
                    'category': category,
                    'created_at': created_at,
                    'last_used': last_used
                }
        except Exception as e:
            print(f"Error loading templates: {e}")
    
    def add_template(self, name: str, content: str, variables: List[str] = None, category: str = "General") -> str:
        """Add new template."""
        template_id = str(uuid.uuid4())
        variables = variables or []
        
        try:
            cursor = self.database.connection.cursor()
            cursor.execute("""
                INSERT INTO clipboard_templates 
                (id, name, content, variables, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                template_id, name, content, json.dumps(variables),
                category, datetime.now().isoformat()
            ))
            self.database.connection.commit()
            
            self.templates[template_id] = {
                'id': template_id,
                'name': name,
                'content': content,
                'variables': variables,
                'category': category,
                'created_at': datetime.now().isoformat(),
                'last_used': None
            }
            
            return template_id
            
        except Exception as e:
            print(f"Error adding template: {e}")
            return None
    
    def expand_template(self, template_id: str, variable_values: Dict[str, str]) -> str:
        """Expand template with variable substitution."""
        if template_id not in self.templates:
            return ""
        
        template = self.templates[template_id]
        content = template['content']
        
        # Replace variables
        for var_name, var_value in variable_values.items():
            content = content.replace(f"{{{var_name}}}", var_value)
        
        # Update last used
        self.update_template_last_used(template_id)
        
        return content
    
    def update_template_last_used(self, template_id: str):
        """Update template last used timestamp."""
        try:
            cursor = self.database.connection.cursor()
            cursor.execute("""
                UPDATE clipboard_templates 
                SET last_used = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), template_id))
            self.database.connection.commit()
        except Exception as e:
            print(f"Error updating template last used: {e}")
    
    def get_template_variables(self, content: str) -> List[str]:
        """Extract variables from template content."""
        import re
        return re.findall(r'\{(\w+)\}', content)


if __name__ == "__main__":
    # Testing code
    print("Enhanced Clipboard Manager - Core components loaded successfully")
    
    # Test database
    db = ClipboardDatabase(":memory:")
    item = ClipboardItem("Test content", "text", "Test App")
    db.add_item(item)
    items = db.get_items()
    print(f"Database test: {len(items)} items")
    
    # Test encryption
    encryption = ClipboardEncryption()
    if encryption.set_password("test123"):
        encrypted = encryption.encrypt_content("Secret data")
        decrypted = encryption.decrypt_content(encrypted)
        print(f"Encryption test: {'PASS' if decrypted == 'Secret data' else 'FAIL'}")
    
    # Test text processing
    processor = ClipboardTextProcessor()
    result = processor.convert_case("hello world", "pascal")
    print(f"Text processing test: {result}")
