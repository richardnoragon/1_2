# Service Contracts: Multi-Pane Explorer

**Feature**: Multi-Pane Explorer Hub Interface Refactor
**Date**: October 1, 2025

This document defines the service interfaces (contracts) for the Multi-Pane Explorer feature.

## 1. PreferenceService

**Purpose**: Manage user preferences persistence

### Methods

#### `load_preferences() -> UserPreferences`

**Description**: Load user preferences from configuration storage

**Inputs**: None

**Outputs**:

- `UserPreferences`: Loaded preferences or defaults if none exist

**Behavior**:

- Read from ConfigManager under `multi_pane_explorer` key
- Validate schema version
- Apply migrations if needed
- Return defaults if file corrupted or missing

**Errors**:

- `ConfigurationError`: If validation fails after migration attempts

---

#### `save_preferences(prefs: UserPreferences) -> None`

**Description**: Persist user preferences to configuration storage

**Inputs**:

- `prefs`: UserPreferences object to save

**Outputs**: None

**Behavior**:

- Validate preferences object
- Serialize to JSON
- Write atomically via ConfigManager
- Log success/failure

**Errors**:

- `ValidationError`: If preferences validation fails
- `IOError`: If write fails

---

#### `reset_to_defaults() -> UserPreferences`

**Description**: Reset all preferences to factory defaults

**Inputs**: None

**Outputs**:

- `UserPreferences`: Default preferences

**Behavior**:

- Create new UserPreferences with default values
- Save to configuration
- Return defaults

---

## 2. BookmarkService

**Purpose**: Manage bookmark creation, retrieval, and deletion

### Methods

#### `create_bookmark(type: BookmarkType, name: str, target: str, metadata: dict = None) -> Bookmark`

**Description**: Create a new bookmark

**Inputs**:

- `type`: Bookmark type (tool/drive/folder/network)
- `name`: Display name
- `target`: Tool name or file path
- `metadata`: Optional type-specific data

**Outputs**:

- `Bookmark`: Newly created bookmark

**Behavior**:

- Generate unique ID (UUID4)
- Validate target based on type
- Set created_at timestamp
- Add to preferences
- Persist immediately
- Return bookmark

**Errors**:

- `ValidationError`: If target invalid for type
- `DuplicateError`: If bookmark already exists

---

#### `get_bookmarks(bookmark_type: BookmarkType = None) -> List[Bookmark]`

**Description**: Retrieve bookmarks, optionally filtered by type

**Inputs**:

- `bookmark_type`: Optional filter (None returns all)

**Outputs**:

- `List[Bookmark]`: Matching bookmarks

**Behavior**:

- Load preferences
- Filter by type if specified
- Return list ordered by created_at (newest first)

---

#### `delete_bookmark(bookmark_id: str) -> bool`

**Description**: Delete a bookmark by ID

**Inputs**:

- `bookmark_id`: UUID of bookmark to delete

**Outputs**:

- `bool`: True if deleted, False if not found

**Behavior**:

- Find bookmark by ID
- Remove from preferences
- Persist immediately
- Return success status

---

## 3. RecentItemsService

**Purpose**: Track recently accessed tools and locations

### Methods

#### `add_tool(tool_name: str) -> None`

**Description**: Record a tool access

**Inputs**:

- `tool_name`: Name of the tool

**Outputs**: None

**Behavior**:

- Check if tool already in recent list
- If exists, update timestamp and move to front
- If new, add to front
- If exceeds limit (10), evict oldest
- Persist immediately

---

#### `add_location(path: Path) -> None`

**Description**: Record a location access

**Inputs**:

- `path`: File system path

**Outputs**: None

**Behavior**:

- Convert path to string
- Check if location already in recent list
- If exists, update timestamp and move to front
- If new, add to front
- If exceeds limit (10), evict oldest
- Persist immediately

---

#### `get_recent_tools() -> List[RecentItem]`

**Description**: Retrieve recent tools list

**Outputs**:

- `List[RecentItem]`: Recent tools, newest first (max 10)

---

#### `get_recent_locations() -> List[RecentItem]`

**Description**: Retrieve recent locations list

**Outputs**:

- `List[RecentItem]`: Recent locations, newest first (max 10)

---

#### `clear_recent(item_type: RecentItemType = None) -> None`

**Description**: Clear recent items

**Inputs**:

- `item_type`: Optional filter (None clears both tools and locations)

**Outputs**: None

**Behavior**:

- Clear specified lists
- Persist immediately

---

## 4. ToolsDiscoveryService

**Purpose**: Discover and retrieve RFU executable tools

### Methods

#### `get_all_tools() -> List[Tool]`

**Description**: Retrieve all executable RFU tools

**Outputs**:

- `List[Tool]`: All registered tools

**Behavior**:

- Query RFU tool registry (main.py)
- Extract metadata (name, description, category, launcher)
- Filter out non-executable items (folders, separators)
- Cache result for performance
- Return list ordered by category, then name

---

#### `search_tools(query: str) -> List[Tool]`

**Description**: Search tools by name or description

**Inputs**:

- `query`: Search string (case-insensitive)

**Outputs**:

- `List[Tool]`: Matching tools

**Behavior**:

- Get all tools
- Filter by name or description contains query
- Return matching tools

---

#### `get_tool_by_name(name: str) -> Optional[Tool]`

**Description**: Retrieve a specific tool by name

**Inputs**:

- `name`: Tool name

**Outputs**:

- `Optional[Tool]`: Tool if found, None otherwise

---

## 5. LayoutManager

**Purpose**: Orchestrate pane layout configuration

### Methods

#### `apply_configuration(config: PaneConfiguration) -> None`

**Description**: Apply a pane configuration to the UI

**Inputs**:

- `config`: Pane configuration to apply

**Outputs**: None

**Behavior**:

- Validate configuration
- Hide/show center panes based on count
- Rearrange splitters based on layout type
- Restore splitter states if available
- Emit layout_changed signal
- Persist configuration

**Errors**:

- `ValidationError`: If configuration invalid

---

#### `get_current_configuration() -> PaneConfiguration`

**Description**: Get the active pane configuration

**Outputs**:

- `PaneConfiguration`: Current configuration

---

#### `save_splitter_states() -> None`

**Description**: Capture current splitter positions

**Behavior**:

- Iterate all splitters
- Call saveState() on each
- Store in configuration
- Persist immediately

---

## 6. StorageDeviceService

**Purpose**: Discover available storage devices (cross-platform)

### Methods

#### `get_available_drives() -> List[StorageDevice]`

**Description**: Retrieve all available storage devices

**Outputs**:

- `List[StorageDevice]`: Available drives/mount points

**Behavior**:

- Platform-specific discovery:
  - Windows: Query drive letters (A-Z)
  - macOS: Scan /Volumes/
  - Linux: Parse /proc/mounts or /etc/mtab
- For each device, get:
  - Path/mount point
  - Label/name
  - Free space
  - Total space
- Return sorted list (system drive first)

---

#### `is_available(path: Path) -> bool`

**Description**: Check if a path is currently accessible

**Inputs**:

- `path`: Path to check

**Outputs**:

- `bool`: True if accessible, False otherwise

**Behavior**:

- Attempt os.path.exists(path)
- Catch permission errors
- Return result

---

## 7. NotificationService

**Purpose**: Display user notifications (toasts)

### Methods

#### `show_info(message: str, duration: int = 5000) -> None`

**Description**: Show informational notification

**Inputs**:

- `message`: Notification text
- `duration`: Display time in milliseconds

---

#### `show_warning(message: str, duration: int = 5000) -> None`

**Description**: Show warning notification

---

#### `show_error(message: str, duration: int = 5000) -> None`

**Description**: Show error notification

---

## Contract Test Skeleton

The following test files will be created in `tests/file_explorer/contract/`:

### `test_preference_service_contract.py`

```python
def test_load_preferences_returns_defaults_when_missing():
    # Given: No configuration file exists
    # When: load_preferences() called
    # Then: Returns UserPreferences with defaults
    pass

def test_save_preferences_persists_to_config():
    # Given: Modified UserPreferences
    # When: save_preferences() called
    # Then: Configuration file updated
    pass

def test_reset_to_defaults_restores_factory_settings():
    # Given: Modified preferences
    # When: reset_to_defaults() called
    # Then: Defaults restored and persisted
    pass
```

### `test_bookmark_service_contract.py`

```python
def test_create_bookmark_generates_unique_id():
    # Given: Bookmark parameters
    # When: create_bookmark() called
    # Then: Returns bookmark with UUID
    pass

def test_create_bookmark_rejects_invalid_target():
    # Given: Invalid target path
    # When: create_bookmark() called
    # Then: Raises ValidationError
    pass

def test_get_bookmarks_filters_by_type():
    # Given: Mixed bookmark types
    # When: get_bookmarks(BookmarkType.TOOL) called
    # Then: Returns only tool bookmarks
    pass

def test_delete_bookmark_removes_from_preferences():
    # Given: Existing bookmark
    # When: delete_bookmark(id) called
    # Then: Bookmark no longer in preferences
    pass
```

### `test_recent_items_service_contract.py`

```python
def test_add_tool_enforces_lru_limit():
    # Given: 10 existing recent tools
    # When: add_tool() called with 11th tool
    # Then: Oldest tool evicted
    pass

def test_add_tool_updates_timestamp_for_existing():
    # Given: Tool already in recent list
    # When: add_tool() called again
    # Then: Tool moved to front with new timestamp
    pass

def test_get_recent_tools_returns_newest_first():
    # Given: Multiple recent tools
    # When: get_recent_tools() called
    # Then: List sorted by timestamp descending
    pass
```

### `test_tools_discovery_service_contract.py`

```python
def test_get_all_tools_returns_registered_tools():
    # Given: RFU application with registered tools
    # When: get_all_tools() called
    # Then: Returns list of Tool objects
    pass

def test_get_all_tools_excludes_non_executables():
    # Given: Tool registry contains folders
    # When: get_all_tools() called
    # Then: Only executable tools returned
    pass

def test_search_tools_matches_name_and_description():
    # Given: Tools with various names
    # When: search_tools("duplicate") called
    # Then: Returns tools with "duplicate" in name/description
    pass
```

### `test_layout_manager_contract.py`

```python
def test_apply_configuration_with_1_pane_disables_layout():
    # Given: Configuration with pane_count=1
    # When: apply_configuration() called
    # Then: Layout type set to DISABLED
    pass

def test_apply_configuration_rearranges_splitters():
    # Given: Configuration with layout=VERTICAL
    # When: apply_configuration() called
    # Then: Splitters arranged top-to-bottom
    pass

def test_save_splitter_states_captures_positions():
    # Given: Splitters with user-adjusted sizes
    # When: save_splitter_states() called
    # Then: States saved to configuration
    pass
```

### `test_storage_device_service_contract.py`

```python
def test_get_available_drives_returns_platform_specific():
    # Given: Platform (Windows/macOS/Linux)
    # When: get_available_drives() called
    # Then: Returns appropriate drives/mount points
    pass

def test_is_available_returns_false_for_missing_path():
    # Given: Non-existent path
    # When: is_available() called
    # Then: Returns False
    pass
```

---

## Contract Implementation Order

1. **PreferenceService** (foundation for all others)
2. **BookmarkService** (simple CRUD, no external dependencies)
3. **RecentItemsService** (similar to BookmarkService)
4. **StorageDeviceService** (needed by center panes)
5. **ToolsDiscoveryService** (integrates with existing RFU)
6. **LayoutManager** (orchestrates UI, depends on above services)
7. **NotificationService** (UI feedback, standalone)

Each service will have failing contract tests written first (TDD), then implementation to make tests pass.
