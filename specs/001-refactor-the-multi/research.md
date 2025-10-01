# Phase 0: Research & Technical Decisions

**Feature**: Multi-Pane Explorer Hub Interface Refactor
**Date**: October 1, 2025

## Research Areas

### 1. PyQt5 Dynamic Layout Management

**Decision**: Use `QSplitter` for resizable pane layouts with `QStackedWidget` for tab management

**Rationale**:

- `QSplitter` provides native resizable dividers between panes
- Supports both horizontal and vertical orientations
- Can be nested for grid layouts (2x2 configuration)
- Maintains user-adjusted sizes automatically
- `QStackedWidget` efficiently manages tab switching without destroying/recreating widgets

**Alternatives Considered**:

- `QGridLayout`: Static, requires manual size management, less user control
- `QDockWidget`: Designed for toolbars/panels, not file browsing panes
- Custom layout manager: Unnecessary complexity, reinvents Qt wheel

**Implementation Pattern**:

```python
# Horizontal 2-pane example
main_splitter = QSplitter(Qt.Horizontal)
main_splitter.addWidget(left_pane)
main_splitter.addWidget(center_container)
main_splitter.addWidget(right_pane)

# Grid 4-pane example (nested splitters)
center_splitter_top = QSplitter(Qt.Horizontal)
center_splitter_top.addWidget(pane1)
center_splitter_top.addWidget(pane2)

center_splitter_bottom = QSplitter(Qt.Horizontal)
center_splitter_bottom.addWidget(pane3)
center_splitter_bottom.addWidget(pane4)

center_container = QSplitter(Qt.Vertical)
center_container.addWidget(center_splitter_top)
center_container.addWidget(center_splitter_bottom)
```

**Best Practices**:

- Save/restore splitter sizes via `saveState()`/`restoreState()`
- Set minimum pane sizes to prevent accidental collapse
- Use stretch factors for proportional sizing on resize

---

### 2. Configuration Persistence Strategy

**Decision**: Extend existing ConfigManager with new section: `multi_pane_explorer`

**Rationale**:

- RFU already uses ConfigManager singleton pattern with JSON persistence
- Atomic writes prevent corruption
- Centralized configuration reduces coupling
- Easy migration/versioning support

**Configuration Schema**:

```json
{
  "multi_pane_explorer": {
    "default_hub_mode": "multi_pane", // or "tabbed"
    "pane_count": 4,
    "layout_type": "grid", // horizontal, vertical, grid, disabled
    "left_pane": {
      "default_tab": "Recent", // Bookmarks, Recent, Tools
      "bookmarks": {
        "tools": ["Duplicate Finder", "Secure Delete"],
        "locations": ["C:\\Projects", "D:\\Backup", "\\\\server\\share"]
      }
    },
    "center_panes": {
      "default_root_drive": "C:\\",
      "last_paths": ["C:\\Projects", "D:\\", "C:\\Users", "C:\\"]
    },
    "right_pane": {
      "default_tab": "Preview" // or "Properties"
    },
    "recent_items": {
      "tools": [
        { "name": "File Finder", "timestamp": "2025-10-01T10:30:00" },
        { "name": "Size Analyzer", "timestamp": "2025-10-01T09:15:00" }
      ],
      "locations": [
        { "path": "C:\\Projects\\RFU", "timestamp": "2025-10-01T11:00:00" },
        { "path": "D:\\Documents", "timestamp": "2025-10-01T10:45:00" }
      ],
      "max_items_per_section": 10
    },
    "splitter_states": {
      "main_horizontal": "<base64_qbytearray>",
      "center_grid_vertical": "<base64_qbytearray>"
    }
  }
}
```

**Alternatives Considered**:

- SQLite database: Overkill for simple key-value preferences
- Separate JSON file: Fragments configuration, harder to backup
- Windows Registry / macOS Preferences: Not cross-platform

**Best Practices**:

- Validate configuration on load with schema
- Provide migration functions for version upgrades
- Fall back to sensible defaults on corruption
- Write configuration changes immediately (not on exit) to prevent loss

---

### 3. Recent Items Tracking

**Decision**: In-memory LRU cache (max 10 per section) with JSON persistence

**Rationale**:

- Small dataset (20 items total) doesn't justify database overhead
- LRU (Least Recently Used) eviction is natural for "recent" semantics
- JSON serialization is simple for timestamps and paths
- ConfigManager handles persistence

**Implementation Approach**:

```python
from collections import OrderedDict
from datetime import datetime

class RecentItemsService:
    def __init__(self, max_tools=10, max_locations=10):
        self.tools = OrderedDict()  # {name: timestamp}
        self.locations = OrderedDict()  # {path: timestamp}
        self.max_tools = max_tools
        self.max_locations = max_locations

    def add_tool(self, tool_name):
        # Move to end (most recent)
        if tool_name in self.tools:
            del self.tools[tool_name]
        self.tools[tool_name] = datetime.now()
        # Evict oldest if over limit
        if len(self.tools) > self.max_tools:
            self.tools.popitem(last=False)
        self._save_to_config()

    def get_recent_tools(self):
        # Return newest first
        return list(reversed(self.tools.keys()))
```

**Alternatives Considered**:

- SQLite with timestamps: Over-engineered for 20 items
- Simple list append: No automatic eviction, requires manual trimming
- Cache expiration (time-based): User study shows item count limit more intuitive

**Best Practices**:

- Thread-safe access (Qt signals/slots from UI thread)
- Atomic updates to prevent race conditions
- Validate paths still exist before displaying (graceful handling of deleted items)

---

### 4. Tool Discovery Integration

**Decision**: Leverage existing RFU tool discovery in `main.py` with filter for executables

**Rationale**:

- RFU already has a tool registration system in `main.py` (`launch_tool()` pattern)
- Tools are organized by category with metadata (name, description, launcher function)
- No need to reinvent discovery mechanism

**Integration Pattern**:

```python
class ToolsDiscoveryService:
    def __init__(self, main_app):
        self.main_app = main_app  # Reference to RFU main application

    def get_all_executable_tools(self):
        """Extract tool list from main app's tool registry"""
        tools = []
        # Scan main_app's tool tabs/categories
        for category_widget in self.main_app.tool_categories:
            for tool_button in category_widget.tool_buttons:
                tools.append({
                    'name': tool_button.name,
                    'description': tool_button.description,
                    'category': category_widget.category_name,
                    'launcher': tool_button.launch_function,
                    'icon': tool_button.icon
                })
        return tools
```

**Alternatives Considered**:

- File system scan for .py files: Brittle, requires naming conventions
- Hardcoded tool list: Breaks on new tool additions
- Separate tool registry: Duplicates existing infrastructure

**Best Practices**:

- Cache tool list on startup (expensive discovery)
- Refresh only when tools are added/removed (signal-based invalidation)
- Provide search/filter functionality for large tool counts

---

### 5. Preview Widget Implementation

**Decision**: Protocol-based preview system with type registration

**Rationale**:

- Extensible: new file types can register preview handlers
- Graceful degradation: unsupported types show informative message
- Separation of concerns: preview logic separate from UI widget

**Architecture**:

```python
# Protocol for preview handlers
class PreviewHandler(Protocol):
    def can_preview(self, file_path: Path) -> bool: ...
    def generate_preview(self, file_path: Path) -> QWidget: ...

# Built-in handlers
class TextPreviewHandler:
    SUPPORTED_EXTENSIONS = {'.txt', '.py', '.md', '.json', '.xml', '.log'}

    def can_preview(self, file_path):
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def generate_preview(self, file_path):
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text_widget.setPlainText(f.read(100_000))  # Limit 100KB preview
        return text_widget

class ImagePreviewHandler:
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'}
    # ...similar pattern

class PreviewWidget:
    def __init__(self):
        self.handlers = [
            TextPreviewHandler(),
            ImagePreviewHandler(),
            PDFPreviewHandler(),  # If PyMuPDF available
        ]

    def preview_file(self, file_path):
        for handler in self.handlers:
            if handler.can_preview(file_path):
                return handler.generate_preview(file_path)
        return self._create_unsupported_message(file_path)
```

**Alternatives Considered**:

- Monolithic preview widget: Unmaintainable, violates single responsibility
- External viewer launch: Breaks in-app preview UX
- Web view with HTML rendering: Heavy dependency, overkill

**Best Practices**:

- Async loading for large files (worker thread)
- Size limits to prevent memory exhaustion (100KB text, scaled images)
- Error handling with user-friendly messages
- Fallback to icon + basic metadata for unsupported types

---

### 6. Empty State UX Patterns

**Decision**: Centered icon + text + action button layout

**Rationale**:

- Industry standard (GitHub, VS Code, Figma all use this pattern)
- Guides user to first action
- Visually distinct from errors
- Accessible (screenreader-friendly structure)

**Implementation Template**:

```python
class EmptyStateWidget(QWidget):
    def __init__(self, icon, title, description, action_text=None, action_callback=None):
        self.layout = QVBoxLayout()

        # Center content vertically and horizontally
        spacer_top = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addItem(spacer_top)

        # Icon (48x48 or 64x64)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(icon_label)

        # Title (larger, bold)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Description (muted color)
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #666;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)

        # Action button (if provided)
        if action_text and action_callback:
            action_btn = QPushButton(action_text)
            action_btn.clicked.connect(action_callback)
            self.layout.addWidget(action_btn, alignment=Qt.AlignCenter)

        spacer_bottom = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addItem(spacer_bottom)
```

**Messages**:

- Bookmarks (tools): "No bookmarked tools yet. Right-click a tool in the Tools tab to bookmark it."
- Bookmarks (locations): "No bookmarked locations yet. Right-click a folder in the file explorer to bookmark it."
- Recent (tools): "No recently used tools. Launch a tool to see it here."
- Recent (locations): "No recent locations. Open folders to see them here."

**Alternatives Considered**:

- Blank pane: Confusing, looks broken
- Just text: Less engaging, harder to scan
- Animated illustrations: Overkill for utility app, increases bundle size

---

### 7. Notification System for Fallback Scenarios

**Decision**: Non-modal toast notifications (bottom-right corner, 5 second timeout)

**Rationale**:

- Non-blocking: user can continue working
- Consistent with modern UX (VS Code, Slack)
- Auto-dismiss reduces cognitive load
- Persistent log for review

**Implementation**:

```python
class NotificationWidget(QWidget):
    def __init__(self, message, notification_type='info'):
        # Types: info, warning, error, success
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout()
        icon = self._get_icon_for_type(notification_type)
        layout.addWidget(QLabel(icon))
        layout.addWidget(QLabel(message))

        # Position in bottom-right corner
        screen = QApplication.desktop().availableGeometry()
        self.move(screen.width() - 350, screen.height() - 100)

        # Auto-dismiss timer
        QTimer.singleShot(5000, self.close)

        # Fade-out animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
```

**Notification Scenarios**:

- "Drive E:\\ is unavailable. Defaulted to C:\\ instead." (warning)
- "Network location \\\\server\\share cannot be reached." (error)
- "Layout preference saved." (success, only on explicit save action)

**Alternatives Considered**:

- Modal dialogs: Disruptive, blocks workflow
- Status bar messages: Easy to miss, no visual emphasis
- Logging only: User unaware of important events

---

## Technology Dependencies Summary

### Core Dependencies (Existing)

- Python 3.8+
- PyQt5 (GUI framework)
- ConfigManager (RFU singleton)
- LogManager (RFU logging)

### New Dependencies

- None required (all functionality achievable with PyQt5 + Python stdlib)

### Testing Dependencies (Existing)

- pytest
- pytest-qt (PyQt5 test fixtures)
- pytest-cov (coverage reporting)

---

## Performance Considerations

### Large Directory Handling

- **Approach**: Lazy loading + virtual scrolling (QAbstractItemModel)
- **Existing pattern**: `file_explorer_pane.py` already implements this
- **Test**: 10,000 files in single directory must load in <2 seconds

### Layout Switching Speed

- **Approach**: Widget reuse (hide/show instead of destroy/create)
- **Target**: <200ms perceived latency
- **Measurement**: QElapsedTimer in layout_manager.py

### Bookmark/Recent Lookup

- **Approach**: In-memory OrderedDict (O(1) access)
- **Target**: <50ms to populate list
- **Max size**: 20 items (negligible memory footprint)

---

## Cross-Platform Validation

### Platform-Specific Considerations

**Windows**:

- Drive letter format (C:\, D:\)
- UNC paths for network locations (\\\\server\\share)
- Qt handles path separators automatically

**macOS**:

- Mount points (/Volumes/DriveName)
- No concept of "drives" - use root filesystem tabs
- Special folders (~/Desktop, ~/Documents)

**Linux**:

- Mount points (/mnt/_, /media/_)
- Filesystem roots (/, /home, /tmp)
- Permission-based access control

**Strategy**: Abstract drive discovery behind platform-agnostic service

```python
class StorageDeviceService:
    def get_available_drives(self):
        if sys.platform == 'win32':
            return self._get_windows_drives()
        elif sys.platform == 'darwin':
            return self._get_macos_volumes()
        else:
            return self._get_linux_mounts()
```

---

## Risk Mitigation

### Risk 1: Configuration Corruption

**Mitigation**: Atomic writes + backup + schema validation

- ConfigManager already implements atomic writes (write to temp, rename)
- Add schema validation on load (pydantic or jsonschema)
- Keep last-known-good backup

### Risk 2: Performance Degradation with 4 Panes

**Mitigation**: Shared model instances + lazy rendering

- Multiple FileExplorerPane instances share same QFileSystemModel
- Only visible panes trigger directory scans
- Defer thumbnail generation until pane gains focus

### Risk 3: Quick-Toggle State Loss

**Mitigation**: Snapshot current state before switching

- Save splitter sizes, scroll positions, selections
- Restore on toggle back
- Maximum state size: ~1KB (negligible)

---

## Open Questions (Resolved via Clarification)

All technical unknowns have been resolved via specification clarifications:

1. ✅ Recent tab bottom half content: files/folders/drives/locations combined
2. ✅ Right pane default: Preview tab
3. ✅ Recent items limit: 10 per section (20 total)
4. ✅ Empty state handling: Helpful placeholder text with action prompts
5. ✅ Unavailable drive fallback: System root + notification

---

## Conclusion

All technical decisions documented. No blocking unknowns remain. Ready to proceed to Phase 1 (Design & Contracts).
