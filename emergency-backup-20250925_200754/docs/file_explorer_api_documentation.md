# RFU Multi-Pane File Explorer - API Documentation

## Overview

This document provides comprehensive API documentation for the RFU Multi-Pane File Explorer. The API is designed for extensibility, allowing developers to create custom panes, integrate new file operations, and extend functionality.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Database API](#database-api)
4. [Cache Management API](#cache-management-api)
5. [UI Components API](#ui-components-api)
6. [Extension Points](#extension-points)
7. [Configuration API](#configuration-api)
8. [Event System](#event-system)

## Architecture Overview

The RFU File Explorer follows a modular architecture with clear separation of concerns:

```
src/rfu/file_explorer/
├── database/           # Data persistence layer
├── models/            # Data models and business logic
├── ui/               # User interface components
├── utils/            # Utility functions and helpers
└── main_application.py # Application entry point
```

### Key Design Principles

- **Modularity**: Components are loosely coupled and highly cohesive
- **Extensibility**: Plugin architecture for custom functionality
- **Thread Safety**: Safe concurrent access to shared resources
- **Cross-Platform**: Consistent behavior across operating systems
- **Performance**: Optimized for large directory structures

## Core Components

### DatabaseSchema

The main database interface for persistent storage.

```python
from src.rfu.file_explorer.database.schema import DatabaseSchema

class DatabaseSchema:
    """Main database interface for the file explorer."""
    
    def __init__(self, db_path: str):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file or ":memory:"
        """
    
    def initialize(self) -> bool:
        """Initialize database schema and apply migrations.
        
        Returns:
            True if successful, False otherwise
        """
    
    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
    
    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query.
        
        Args:
            sql: SQL statement
            params: Statement parameters
            
        Returns:
            Number of affected rows
        """
    
    def get_schema_version(self) -> int:
        """Get current schema version.
        
        Returns:
            Schema version number
        """
```

### CacheManager

High-performance caching system with TTL and LRU eviction.

```python
from src.rfu.file_explorer.database.cache_manager import CacheManager

class CacheManager:
    """High-performance cache with TTL and LRU eviction."""
    
    def __init__(self, database: DatabaseSchema, max_cache_size: int = 10000):
        """Initialize cache manager.
        
        Args:
            database: Database instance for persistence
            max_cache_size: Maximum number of cached items
        """
    
    def get(self, key: str) -> Optional[Dict]:
        """Retrieve item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
    
    def put(self, key: str, data: Dict, ttl: Optional[float] = None) -> bool:
        """Store item in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful
        """
    
    def invalidate(self, key: str) -> bool:
        """Remove item from cache.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if item was removed
        """
    
    def clear(self) -> None:
        """Clear all cached items."""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics.
        
        Returns:
            Dictionary with hits, misses, size, etc.
        """
```

### DriveManager

Cross-platform drive detection and monitoring.

```python
from src.rfu.file_explorer.models.drive_manager import DriveManager, DriveInfo

class DriveInfo:
    """Information about a detected drive."""
    
    def __init__(self, path: str, label: str, file_system: str, 
                 total_space: int, free_space: int):
        self.path = path
        self.label = label
        self.file_system = file_system
        self.total_space = total_space
        self.free_space = free_space

class DriveManager:
    """Cross-platform drive detection and monitoring."""
    
    def get_available_drives(self) -> List[DriveInfo]:
        """Get list of available drives.
        
        Returns:
            List of DriveInfo objects
        """
    
    def start_monitoring(self) -> None:
        """Start monitoring for drive changes."""
    
    def stop_monitoring(self) -> None:
        """Stop drive monitoring."""
    
    # Signals (PyQt)
    drive_added = pyqtSignal(DriveInfo)
    drive_removed = pyqtSignal(str)  # drive path
```

### PaneManager

Advanced pane layout and management system.

```python
from src.rfu.file_explorer.ui.pane_manager import (
    PaneManager, PaneConfiguration, PaneType, LayoutType
)

class PaneConfiguration:
    """Configuration for a pane instance."""
    
    def __init__(self, pane_id: str, pane_type: PaneType, title: str,
                 position: Tuple[int, int] = (0, 0), size: Tuple[int, int] = (400, 300)):
        self.pane_id = pane_id
        self.pane_type = pane_type
        self.title = title
        self.position = position
        self.size = size

class PaneManager(QWidget):
    """Advanced pane layout and management."""
    
    def add_pane(self, config: PaneConfiguration) -> QWidget:
        """Add a new pane.
        
        Args:
            config: Pane configuration
            
        Returns:
            Created pane widget
        """
    
    def remove_pane(self, pane_id: str) -> bool:
        """Remove a pane.
        
        Args:
            pane_id: ID of pane to remove
            
        Returns:
            True if pane was removed
        """
    
    def get_pane(self, pane_id: str) -> Optional[QWidget]:
        """Get pane by ID.
        
        Args:
            pane_id: Pane identifier
            
        Returns:
            Pane widget or None
        """
    
    def set_layout(self, layout_type: LayoutType) -> None:
        """Change pane layout.
        
        Args:
            layout_type: New layout type
        """
    
    def save_configuration(self) -> Dict[str, Any]:
        """Save current pane configuration.
        
        Returns:
            Configuration dictionary
        """
    
    def load_configuration(self, config: Dict[str, Any]) -> None:
        """Load pane configuration.
        
        Args:
            config: Configuration dictionary
        """
```

## Database API

### Schema Tables

The database schema includes the following main tables:

#### files
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    size INTEGER,
    modified_time REAL,
    created_time REAL,
    file_type TEXT,
    checksum TEXT,
    INDEX(path),
    INDEX(name),
    INDEX(modified_time)
);
```

#### directories
```sql
CREATE TABLE directories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    modified_time REAL,
    created_time REAL,
    file_count INTEGER DEFAULT 0,
    INDEX(path),
    INDEX(name)
);
```

#### cache_entries
```sql
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL NOT NULL,
    expires_at REAL,
    access_count INTEGER DEFAULT 0,
    last_accessed REAL,
    INDEX(expires_at),
    INDEX(last_accessed)
);
```

### Database Operations

#### File Operations
```python
# Add file to database
db.execute_update(
    "INSERT OR REPLACE INTO files (path, name, size, modified_time) VALUES (?, ?, ?, ?)",
    (file_path, file_name, file_size, modification_time)
)

# Get file information
files = db.execute_query(
    "SELECT * FROM files WHERE path LIKE ? ORDER BY name",
    (f"{directory_path}/%",)
)

# Update file metadata
db.execute_update(
    "UPDATE files SET size = ?, modified_time = ? WHERE path = ?",
    (new_size, new_mtime, file_path)
)
```

#### Search Operations
```python
# Search files by name pattern
results = db.execute_query(
    "SELECT * FROM files WHERE name LIKE ? ORDER BY modified_time DESC",
    (f"%{search_pattern}%",)
)

# Search with multiple criteria
results = db.execute_query(
    """SELECT * FROM files 
       WHERE name LIKE ? 
       AND size BETWEEN ? AND ? 
       AND modified_time > ?""",
    (name_pattern, min_size, max_size, date_threshold)
)
```

## Cache Management API

### Cache Configuration

```python
# Initialize cache with custom settings
cache = CacheManager(
    database=db,
    max_cache_size=50000,  # Maximum items
    default_ttl=3600,      # 1 hour default TTL
    cleanup_interval=300   # Cleanup every 5 minutes
)
```

### Cache Operations

```python
# Store file metadata
file_info = {
    'name': 'document.pdf',
    'size': 1024000,
    'modified': time.time(),
    'type': 'application/pdf'
}
cache.put(f"file://{file_path}", file_info, ttl=7200)  # 2 hour TTL

# Retrieve cached data
cached_info = cache.get(f"file://{file_path}")
if cached_info:
    print(f"File size: {cached_info['size']} bytes")

# Cache directory listing
directory_contents = [
    {'name': 'file1.txt', 'size': 1024},
    {'name': 'file2.png', 'size': 2048}
]
cache.put(f"dir://{directory_path}", directory_contents, ttl=1800)  # 30 minutes
```

### Cache Patterns

```python
# Cache with fallback pattern
def get_file_info(file_path: str) -> Dict:
    cache_key = f"file://{file_path}"
    
    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Fallback to filesystem
    try:
        stat_info = Path(file_path).stat()
        file_info = {
            'size': stat_info.st_size,
            'modified': stat_info.st_mtime,
            'created': stat_info.st_ctime
        }
        
        # Cache for future use
        cache.put(cache_key, file_info, ttl=3600)
        return file_info
        
    except OSError:
        return {}
```

## UI Components API

### Custom Pane Development

To create a custom pane type:

```python
from src.rfu.file_explorer.ui.pane_manager import PaneConfiguration, PaneType
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class CustomPaneType(PaneType):
    CUSTOM_VIEWER = "custom_viewer"

class CustomPane(QWidget):
    """Example custom pane implementation."""
    
    def __init__(self, config: PaneConfiguration):
        super().__init__()
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the pane UI."""
        layout = QVBoxLayout()
        self.label = QLabel(f"Custom Pane: {self.config.title}")
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def set_data(self, data: Any):
        """Set data for the pane to display."""
        self.label.setText(f"Data: {data}")
    
    def cleanup(self):
        """Clean up resources when pane is closed."""
        pass

# Register custom pane type
def create_custom_pane(config: PaneConfiguration) -> QWidget:
    return CustomPane(config)

# Add to pane factory
pane_manager.register_pane_type(CustomPaneType.CUSTOM_VIEWER, create_custom_pane)
```

### Widget Customization

```python
from src.rfu.file_explorer.ui.custom_widgets import EnhancedToolbar, ThemeColors

# Create custom toolbar
toolbar = EnhancedToolbar()

# Add custom actions
toolbar.add_action_button(
    action_id="my_action",
    text="My Action",
    icon_path="path/to/icon.png",
    tooltip="Custom action tooltip",
    callback=lambda: print("Action triggered")
)

# Apply custom theme
custom_theme = {
    'background': '#2d2d2d',
    'text': '#ffffff',
    'accent': '#4a9eff',
    'border': '#555555'
}
toolbar.apply_theme(custom_theme)

# Handle action state
toolbar.set_action_enabled("my_action", False)
toolbar.set_action_visible("my_action", True)
```

### File Operation Integration

```python
from src.rfu.file_explorer.ui.file_explorer_pane import FileExplorerPane

class CustomFileOperation:
    """Example custom file operation."""
    
    def __init__(self, pane: FileExplorerPane):
        self.pane = pane
    
    def execute(self, file_paths: List[str]):
        """Execute custom operation on selected files."""
        for file_path in file_paths:
            # Custom processing logic
            self.process_file(file_path)
        
        # Refresh pane to show changes
        self.pane.refresh()
    
    def process_file(self, file_path: str):
        """Process individual file."""
        # Implementation specific logic
        pass

# Add to context menu
def add_custom_operation(pane: FileExplorerPane):
    operation = CustomFileOperation(pane)
    pane.add_context_menu_action(
        "Custom Operation",
        lambda: operation.execute(pane.get_selected_files())
    )
```

## Extension Points

### Plugin Architecture

```python
from src.rfu.file_explorer.core.plugin_manager import PluginManager, Plugin

class ExamplePlugin(Plugin):
    """Example plugin implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "Example plugin for demonstration"
    
    def initialize(self, application):
        """Initialize plugin with application context."""
        self.application = application
        
        # Add menu items
        application.add_menu_action(
            "Tools",
            "Example Action",
            self.execute_action
        )
    
    def execute_action(self):
        """Execute plugin action."""
        print("Example plugin action executed")
    
    def cleanup(self):
        """Clean up plugin resources."""
        pass

# Register plugin
plugin_manager = PluginManager()
plugin_manager.register_plugin(ExamplePlugin())
```

### Custom File Types

```python
from src.rfu.file_explorer.models.file_type_manager import FileTypeManager, FileTypeHandler

class CustomFileTypeHandler(FileTypeHandler):
    """Handler for custom file types."""
    
    def can_handle(self, file_path: str) -> bool:
        """Check if this handler can process the file."""
        return file_path.endswith('.custom')
    
    def get_preview(self, file_path: str) -> str:
        """Generate preview text for the file."""
        with open(file_path, 'r') as f:
            return f"Custom file preview: {f.read()[:100]}..."
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the file."""
        return {
            'type': 'Custom File',
            'handler': 'CustomFileTypeHandler'
        }

# Register custom handler
file_type_manager = FileTypeManager()
file_type_manager.register_handler(CustomFileTypeHandler())
```

## Configuration API

### Settings Management

```python
from src.rfu.file_explorer.core.config_manager import ConfigManager

# Get configuration manager instance
config = ConfigManager.get_instance()

# Get settings
theme = config.get_setting('appearance', 'theme', default='light')
cache_size = config.get_setting('performance', 'cache_size', default=10000)

# Set settings
config.set_setting('appearance', 'theme', 'dark')
config.set_setting('performance', 'cache_size', 50000)

# Save configuration
config.save_configuration()

# Reset to defaults
config.reset_section('appearance')
config.reset_all()
```

### Configuration Schema

```python
DEFAULT_CONFIG = {
    'appearance': {
        'theme': 'light',
        'font_family': 'Arial',
        'font_size': 10,
        'icon_size': 24
    },
    'performance': {
        'cache_size': 10000,
        'thumbnail_generation': True,
        'lazy_loading': True,
        'memory_limit_mb': 512
    },
    'behavior': {
        'confirm_deletions': True,
        'auto_refresh': True,
        'double_click_action': 'open',
        'default_view_mode': 'list'
    },
    'panes': {
        'default_layout': 'split_horizontal',
        'min_pane_count': 1,
        'max_pane_count': 8
    }
}
```

## Event System

### Signal Definitions

```python
from PyQt5.QtCore import pyqtSignal, QObject

class FileExplorerSignals(QObject):
    """Central signal definitions for file explorer events."""
    
    # File operations
    file_selected = pyqtSignal(str)  # file_path
    files_copied = pyqtSignal(list)  # file_paths
    files_moved = pyqtSignal(list, str)  # file_paths, destination
    files_deleted = pyqtSignal(list)  # file_paths
    
    # Directory operations
    directory_changed = pyqtSignal(str)  # directory_path
    directory_refreshed = pyqtSignal(str)  # directory_path
    
    # Pane operations
    pane_created = pyqtSignal(str)  # pane_id
    pane_closed = pyqtSignal(str)  # pane_id
    pane_focused = pyqtSignal(str)  # pane_id
    
    # Application events
    theme_changed = pyqtSignal(str)  # theme_name
    settings_changed = pyqtSignal(str, str)  # section, key
```

### Event Handling

```python
# Connect to events
signals = FileExplorerSignals()

def on_file_selected(file_path: str):
    print(f"File selected: {file_path}")

def on_directory_changed(directory_path: str):
    print(f"Directory changed to: {directory_path}")

# Connect signals
signals.file_selected.connect(on_file_selected)
signals.directory_changed.connect(on_directory_changed)

# Emit events
signals.file_selected.emit("/path/to/file.txt")
signals.directory_changed.emit("/path/to/directory")
```

### Custom Event Handling

```python
class CustomEventHandler:
    """Custom event handler for specific functionality."""
    
    def __init__(self, application):
        self.application = application
        self.setup_connections()
    
    def setup_connections(self):
        """Set up signal connections."""
        signals = self.application.signals
        
        signals.file_selected.connect(self.handle_file_selection)
        signals.files_copied.connect(self.handle_file_copy)
        signals.pane_created.connect(self.handle_pane_creation)
    
    def handle_file_selection(self, file_path: str):
        """Handle file selection events."""
        # Custom logic for file selection
        pass
    
    def handle_file_copy(self, file_paths: List[str]):
        """Handle file copy events."""
        # Custom logic for file copying
        pass
    
    def handle_pane_creation(self, pane_id: str):
        """Handle pane creation events."""
        # Custom logic for new panes
        pass
```

---

**API Version**: 1.0.0  
**Last Updated**: 2025-09-12  
**Compatibility**: Python 3.9+, PyQt5/PyQt6