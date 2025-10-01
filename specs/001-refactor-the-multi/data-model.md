# Data Model: Multi-Pane Explorer

**Feature**: Multi-Pane Explorer Hub Interface Refactor
**Date**: October 1, 2025

## Entity Definitions

### 1. HubInterfaceMode (Enumeration)

**Purpose**: Represents the top-level user experience mode

```python
from enum import Enum

class HubInterfaceMode(Enum):
    MULTI_PANE = "multi_pane"
    TABBED = "tabbed"
```

**Attributes**:

- `MULTI_PANE`: Multi-pane explorer interface (4-pane layout with configurable center)
- `TABBED`: Traditional tabbed interface (existing RFU hub)

**Validation Rules**:

- Must be one of the two defined values
- Default: `MULTI_PANE`

**State Transitions**:

- `MULTI_PANE` ↔ `TABBED` (via quick-toggle button)
- Transitions preserve user context (paths, selections)

**Relationships**:

- One active mode per application session
- Persisted in configuration

---

### 2. PaneConfiguration

**Purpose**: Defines the active pane count and layout arrangement

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class LayoutType(Enum):
    DISABLED = "disabled"      # 1 pane only
    HORIZONTAL = "horizontal"  # Side-by-side
    VERTICAL = "vertical"      # Top-to-bottom
    GRID = "grid"             # 2x2 grid

@dataclass
class PaneConfiguration:
    pane_count: int  # 1, 2, 3, or 4
    layout_type: LayoutType
    splitter_states: dict[str, bytes]  # QSplitter saved states
```

**Attributes**:

- `pane_count`: Number of active center panes (1-4)
- `layout_type`: Arrangement pattern for center panes
- `splitter_states`: Serialized splitter positions for each layout

**Validation Rules**:

- `pane_count` must be in range [1, 4]
- When `pane_count == 1`, `layout_type` must be `DISABLED`
- When `pane_count == 2`, `layout_type` must be `HORIZONTAL` or `VERTICAL`
- When `pane_count >= 3`, `layout_type` can be any except `DISABLED`
- `splitter_states` keys must match active layout components

**State Transitions**:

- User selects pane count → layout options update
- User changes layout → splitter widgets reorganize
- Window resize → splitter positions adjust (saved on change)

**Relationships**:

- One configuration per Multi-Pane Explorer session
- Persisted in user preferences
- Applies only to center panes (left and right panes always visible)

---

### 3. LeftPaneTab (Enumeration)

**Purpose**: Identifies the active tab in the left pane

```python
class LeftPaneTab(Enum):
    BOOKMARKS = "bookmarks"
    RECENT = "recent"
    TOOLS = "tools"
```

**Attributes**:

- `BOOKMARKS`: Shows bookmarked tools (top) and locations (bottom)
- `RECENT`: Shows recent tools (top) and recent locations (bottom)
- `TOOLS`: Shows all executable RFU tools

**Validation Rules**:

- Must be one of the three defined values
- Default: `RECENT`

**Relationships**:

- One active tab per left pane
- User preference stored in configuration

---

### 4. RightPaneTab (Enumeration)

**Purpose**: Identifies the active tab in the right pane

```python
class RightPaneTab(Enum):
    PREVIEW = "preview"
    PROPERTIES = "properties"
```

**Attributes**:

- `PREVIEW`: File preview display
- `PROPERTIES`: File metadata and properties

**Validation Rules**:

- Must be one of the two defined values
- Default: `PREVIEW`

**Relationships**:

- One active tab per right pane
- User preference stored in configuration
- Content updates based on center pane selection

---

### 5. Bookmark

**Purpose**: User-saved reference to a tool or file system location

```python
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

class BookmarkType(Enum):
    TOOL = "tool"
    DRIVE = "drive"
    FOLDER = "folder"
    NETWORK_LOCATION = "network"

@dataclass
class Bookmark:
    id: str                    # UUID
    type: BookmarkType
    name: str                  # Display name
    target: str                # Tool name or file path
    created_at: datetime
    metadata: dict             # Type-specific data (icon, description, etc.)
```

**Attributes**:

- `id`: Unique identifier (UUID4)
- `type`: Category of bookmark (tool, drive, folder, network)
- `name`: User-friendly display text
- `target`:
  - For tools: Tool name (matches RFU tool registry)
  - For locations: Absolute file path or UNC path
- `created_at`: Timestamp of bookmark creation
- `metadata`: Additional data
  - Tools: `{icon: str, category: str, description: str}`
  - Locations: `{icon: str, disk_usage: Optional[int]}`

**Validation Rules**:

- `id` must be unique across all bookmarks
- `name` required, max length 100 characters
- `target` required:
  - Tools: Must exist in RFU tool registry
  - Drives: Must be valid drive letter (Windows) or mount point (Unix)
  - Folders: Must be absolute path
  - Network: Must be valid UNC path (\\\\server\\share) or network URL
- `created_at` cannot be in the future

**State Transitions**:

- Created: User bookmarks item → Added to bookmark list
- Deleted: User removes bookmark → Removed from list
- No modification state (bookmarks are immutable after creation)

**Relationships**:

- Multiple bookmarks per user (no limit)
- Tools displayed in top half of Bookmarks tab
- Locations displayed in bottom half of Bookmarks tab
- Stored in configuration as list

---

### 6. RecentItem

**Purpose**: Automatically tracked recently accessed tool or location

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class RecentItemType(Enum):
    TOOL = "tool"
    LOCATION = "location"

@dataclass
class RecentItem:
    type: RecentItemType
    name: str                  # Tool name or path
    timestamp: datetime
    metadata: dict             # Type-specific data
```

**Attributes**:

- `type`: Category (tool or location)
- `name`:
  - For tools: Tool display name
  - For locations: File path
- `timestamp`: Last access time
- `metadata`:
  - Tools: `{category: str, icon: str}`
  - Locations: `{is_directory: bool, size: Optional[int]}`

**Validation Rules**:

- `name` required
- `timestamp` cannot be in the future
- Maximum 10 tools in recent list
- Maximum 10 locations in recent list
- Oldest items evicted when limit reached (LRU)

**State Transitions**:

- Created: User accesses tool/location → Added to recent list
- Updated: User re-accesses item → Timestamp updated, moved to top
- Evicted: New item exceeds limit → Oldest item removed

**Lifecycle**:

- Ephemeral (cleared on app restart optional via config)
- No explicit deletion by user (auto-managed)

**Relationships**:

- Two separate lists (tools, locations)
- Tools displayed in top half of Recent tab
- Locations displayed in bottom half of Recent tab
- Stored in configuration as ordered list

---

### 7. Tool

**Purpose**: Represents an executable RFU utility program

```python
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Tool:
    name: str                      # Display name
    description: str               # Short description
    category: str                  # Tool category (e.g., "File Operations")
    launcher: Callable[[], None]   # Function to launch tool
    icon: Optional[str]            # Icon path or resource name
    executable_path: str           # Python module path
```

**Attributes**:

- `name`: User-facing tool name (e.g., "Duplicate Finder")
- `description`: Brief purpose statement
- `category`: Organizational group
- `launcher`: Callable that opens the tool window
- `icon`: Visual identifier (optional)
- `executable_path`: Module path for metadata

**Validation Rules**:

- `name` required, max 50 characters
- `description` required, max 200 characters
- `category` required
- `launcher` must be callable
- `executable_path` must reference existing module

**Relationships**:

- Discovered from RFU tool registry (main.py)
- Displayed in Tools tab (left pane)
- Can be bookmarked (→ Bookmark entity)
- Tracked in recent items (→ RecentItem entity)

---

### 8. CenterPane

**Purpose**: File/directory navigation view instance

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

@dataclass
class CenterPane:
    id: str                        # Unique identifier
    current_path: Path             # Active directory
    history: List[Path]            # Navigation history (back/forward)
    history_index: int             # Current position in history
    selected_items: List[Path]     # User selections
    view_mode: str                 # "list", "grid", "detail"
```

**Attributes**:

- `id`: Unique pane identifier (UUID4)
- `current_path`: Currently displayed directory
- `history`: Stack of visited paths
- `history_index`: Position in history (for back/forward nav)
- `selected_items`: Files/folders currently selected
- `view_mode`: Display style

**Validation Rules**:

- `id` must be unique among active panes
- `current_path` must be valid directory path
- `history` cannot be empty (contains at least current_path)
- `history_index` must be valid index in history list
- `selected_items` elements must exist within current_path

**State Transitions**:

- Created: Pane added to layout → Initialized with default root drive
- Navigate: User opens folder → current_path updates, history appends
- Back/Forward: User navigates history → current_path and history_index update
- Select: User clicks items → selected_items updates
- Destroyed: Pane removed from layout → State optionally saved

**Relationships**:

- 1-4 active instances in Multi-Pane Explorer
- Emits selection events → Right pane reacts (preview/properties)
- Shares QFileSystemModel for performance
- Independent state per instance

---

### 9. UserPreferences

**Purpose**: Consolidated user configuration for Multi-Pane Explorer

```python
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class UserPreferences:
    # Hub mode
    active_hub_mode: HubInterfaceMode

    # Pane configuration
    pane_config: PaneConfiguration

    # Left pane
    left_default_tab: LeftPaneTab
    bookmarks: List[Bookmark]

    # Center panes
    center_default_root: Path
    center_last_paths: List[Optional[Path]]  # One per pane

    # Right pane
    right_default_tab: RightPaneTab

    # Recent items
    recent_tools: List[RecentItem]
    recent_locations: List[RecentItem]
    recent_max_per_section: int
```

**Attributes**:

- All user-configurable settings in one structure
- See individual entities above for attribute details

**Validation Rules**:

- `active_hub_mode` required
- `pane_config` required
- `bookmarks` can be empty list
- `center_default_root` must be valid path
- `center_last_paths` length must equal `pane_config.pane_count`
- `recent_tools` max length = `recent_max_per_section`
- `recent_locations` max length = `recent_max_per_section`
- `recent_max_per_section` default 10, min 5, max 50

**Persistence**:

- Saved to `config/rfu_config.json` under `multi_pane_explorer` key
- Atomic writes via ConfigManager
- Loaded on application startup
- Written on preference change (immediate persistence)

**Relationships**:

- Root configuration entity
- References all other entities
- Single instance per application

---

## Entity Relationship Diagram

```
UserPreferences (1)
├── active_hub_mode: HubInterfaceMode (1)
├── pane_config: PaneConfiguration (1)
│   └── layout_type: LayoutType (1)
├── left_default_tab: LeftPaneTab (1)
├── bookmarks: Bookmark (0..*)
│   └── type: BookmarkType (1)
├── center_default_root: Path
├── center_last_paths: Path (1..4)
├── right_default_tab: RightPaneTab (1)
├── recent_tools: RecentItem (0..10)
│   └── type: RecentItemType
└── recent_locations: RecentItem (0..10)
    └── type: RecentItemType

Tool (discovered from RFU registry)
└── Can be referenced by Bookmark or RecentItem

CenterPane (runtime instances, 1-4 active)
├── current_path: Path
└── selected_items: Path (0..*)
```

---

## Data Access Patterns

### 1. Application Startup

```python
# Load preferences from ConfigManager
prefs = preference_service.load_preferences()

# Restore hub mode
hub.set_mode(prefs.active_hub_mode)

# If multi-pane mode, restore layout
if prefs.active_hub_mode == HubInterfaceMode.MULTI_PANE:
    layout_manager.configure_panes(prefs.pane_config)
    left_pane.set_default_tab(prefs.left_default_tab)
    right_pane.set_default_tab(prefs.right_default_tab)

    # Restore center pane paths
    for i, pane in enumerate(center_panes):
        pane.navigate_to(prefs.center_last_paths[i])
```

### 2. Adding a Bookmark

```python
# User action: Right-click → Bookmark
bookmark = bookmark_service.create_bookmark(
    type=BookmarkType.FOLDER,
    name="Projects",
    target="C:\\Projects"
)

# Service adds to preferences
prefs.bookmarks.append(bookmark)
preference_service.save_preferences(prefs)

# UI updates
bookmarks_widget.refresh()
```

### 3. Tracking Recent Item

```python
# User action: Launch tool
recent_items_service.add_tool("Duplicate Finder")

# Service updates LRU cache
prefs.recent_tools = recent_items_service.get_recent_tools()
preference_service.save_preferences(prefs)

# UI updates (if Recent tab active)
recent_widget.refresh()
```

### 4. Changing Layout

```python
# User action: Select 2 panes, horizontal layout
new_config = PaneConfiguration(
    pane_count=2,
    layout_type=LayoutType.HORIZONTAL,
    splitter_states={}
)

layout_manager.apply_configuration(new_config)
prefs.pane_config = new_config
preference_service.save_preferences(prefs)
```

### 5. Fallback Handling

```python
# Unavailable default drive
try:
    center_pane.navigate_to(prefs.center_default_root)
except FileNotFoundError:
    # Fallback to system root
    system_root = Path("C:\\") if sys.platform == "win32" else Path("/")
    center_pane.navigate_to(system_root)

    # Notify user
    notification_service.show_warning(
        f"Drive {prefs.center_default_root} unavailable. Defaulted to {system_root}."
    )
```

---

## Schema Versioning

**Current Version**: 1.0.0

**Migration Strategy**:

- `schema_version` field in configuration
- Migration functions for version upgrades
- Backward compatibility for one minor version

**Example Migration** (future):

```python
def migrate_1_0_to_1_1(config_data):
    # Hypothetical: Add 'favorite' flag to bookmarks
    if 'bookmarks' in config_data:
        for bookmark in config_data['bookmarks']:
            if 'favorite' not in bookmark:
                bookmark['favorite'] = False
    config_data['schema_version'] = '1.1.0'
    return config_data
```

---

## Conclusion

All entities defined with clear attributes, validation rules, relationships, and access patterns. Ready for contract generation and implementation.
