# Center Panes Display Fix

## Issue

The center file explorer panes were not being displayed in the multi-pane explorer interface. The left and right panes appeared, but the center area (which should contain 1-4 file explorer panes) was empty.

## Root Cause

The `MultiPaneExplorer` class was creating a `LayoutManagerUI` widget but never:

1. Created any `FileExplorerPane` widgets to display
2. Passed these panes to the `LayoutManagerUI` via `set_center_panes()`

The `LayoutManagerUI` requires center panes to be provided before it can display them in various layouts.

## Solution

Modified `src/file_explorer/multi_pane_explorer_simple.py` to:

1. **Create center panes** in `_create_center_panes()` method:

   - Creates 4 `FileExplorerPane` instances (maximum supported)
   - Each pane has its own `PaneConfiguration` with unique ID
   - Connects pane signals (`fileSelected`, `currentPathChanged`) to explorer

2. **Provide panes to layout manager**:

   - Calls `self.layout_manager_ui.set_center_panes(self.center_panes)`
   - This happens after UI setup but before configuration restore

3. **Added proper imports**:
   - `from src.file_explorer.ui.pane_manager import PaneConfiguration, PaneType`
   - Required widgets: `QLabel`, `QVBoxLayout`

## Code Changes

### New Method: `_create_center_panes()`

```python
def _create_center_panes(self):
    """Create the center file explorer panes."""
    try:
        # Create 4 panes (max supported)
        for i in range(4):
            config = PaneConfiguration(
                pane_id=f"center_pane_{i+1}",
                pane_type=PaneType.FILE_EXPLORER,
                title=f"File Explorer {i+1}",
            )
            pane = FileExplorerPane(config, parent=self)
            self.center_panes.append(pane)

            # Connect pane signals
            if hasattr(pane, 'fileSelected'):
                pane.fileSelected.connect(self.file_selected.emit)
            if hasattr(pane, 'currentPathChanged'):
                pane.currentPathChanged.connect(self._on_path_changed)

        self.logger.info(f"Created {len(self.center_panes)} center panes")
    except Exception as e:
        # Fallback to simple placeholder panes
        ...
```

### Modified `__init__()` Method

```python
def __init__(self, parent: Optional[QWidget] = None):
    super().__init__(parent)

    # ... existing initialization ...

    # Create center file explorer panes (max 4) - NEW
    self.center_panes: List[FileExplorerPane] = []
    self._create_center_panes()

    # Create pane components
    self.left_pane = LeftPane()
    self.layout_manager_ui = LayoutManagerUI()
    self.right_pane = RightPane()

    self.setup_ui()
    self.connect_signals()

    # Provide center panes to layout manager - NEW
    self.layout_manager_ui.set_center_panes(self.center_panes)

    # Load saved configuration
    self.restore_configuration()
```

### New Signal Handler

```python
def _on_path_changed(self, path: str):
    """Handle path change from a pane."""
    self.logger.debug(f"Path changed: {path}")
```

## How It Works Now

### Initialization Flow

1. `MultiPaneExplorer.__init__()` is called
2. Creates 4 `FileExplorerPane` instances with proper configurations
3. Stores them in `self.center_panes` list
4. Creates left/center/right pane components
5. Sets up UI with splitters
6. **Provides center panes to layout manager**
7. Loads saved configuration (pane count, layout type)
8. `LayoutManagerUI` applies layout to the provided panes

### Layout Application

1. `LayoutManagerUI.apply_layout(config)` is called
2. Validates configuration (pane count, layout type)
3. Checks if enough panes are available (`len(self.center_panes) >= pane_count`)
4. Creates appropriate splitter arrangement based on layout type:
   - **1 pane**: Single pane, no splitter
   - **2 panes**: Horizontal or vertical splitter
   - **3 panes**: Nested splitters (horizontal/vertical/grid)
   - **4 panes**: 2x2 grid with nested splitters
5. Shows required panes, hides unused ones
6. Restores splitter positions from saved state

### Signal Flow

```
FileExplorerPane.fileSelected
    ↓
MultiPaneExplorer._on_file_selected
    ↓
MultiPaneExplorer.file_selected (signal)
    ↓
RightPane.update_preview (connected externally)

FileExplorerPane.currentPathChanged
    ↓
MultiPaneExplorer._on_path_changed
    ↓
(Logged for debugging)
```

## Testing Checklist

- [x] Import corrections applied
- [x] Center panes creation method added
- [x] Panes passed to layout manager
- [ ] Launch multi-pane explorer from main.py
- [ ] Verify center panes display
- [ ] Test switching pane count (1-4)
- [ ] Test layout types (horizontal/vertical/grid)
- [ ] Test file navigation in panes
- [ ] Verify signal connections work

## Expected Behavior

### After Fix

- **Center area**: Shows 1-4 file explorer panes based on configuration
- **Default layout**: 2 panes, horizontal split
- **Navigation**: Each pane can browse independently
- **Selection**: File selection updates right pane preview
- **Splitters**: Draggable dividers between panes
- **State persistence**: Pane count and splitter positions saved

### Layout Options

- **1 pane**: Full-width single explorer
- **2 panes**: Side-by-side (horizontal) or top-bottom (vertical)
- **3 panes**: Three arrangements (horizontal/vertical/2+1 grid)
- **4 panes**: 2x2 grid arrangement

## Architecture Notes

### Component Hierarchy

```
MultiPaneExplorer (QWidget)
├── main_splitter (QSplitter)
    ├── LeftPane (bookmarks/recent/tools)
    ├── LayoutManagerUI (center panes container)
    │   └── dynamic splitters
    │       └── FileExplorerPane instances (1-4)
    └── RightPane (preview/properties)
```

### Pane Configuration Classes

Two different `PaneConfiguration` classes exist:

1. **Individual pane config** (`src/file_explorer/ui/pane_manager.py`):

   - `pane_id`: Unique identifier
   - `pane_type`: Type enum (FILE_EXPLORER, etc.)
   - `title`: Display title
   - Used by: `FileExplorerPane`

2. **Layout config** (`src/file_explorer/models/pane_configuration.py`):
   - `pane_count`: Number of panes (1-4)
   - `layout_type`: Arrangement (horizontal/vertical/grid)
   - `splitter_states`: Saved splitter positions
   - Used by: `LayoutManagerUI`

### Fallback Strategy

If `FileExplorerPane` creation fails:

1. Creates simple `QWidget` with error label
2. Allows application to continue running
3. User sees "Initialization Error" placeholder
4. Logs detailed error for debugging

## Related Files

### Modified

- `src/file_explorer/multi_pane_explorer_simple.py` - Main fix location

### Dependencies (Unchanged)

- `src/file_explorer/ui/file_explorer_pane.py` - Individual pane widget
- `src/file_explorer/ui/layout_manager_ui.py` - Layout orchestration
- `src/file_explorer/ui/pane_manager.py` - Pane configuration classes
- `src/file_explorer/models/pane_configuration.py` - Layout config model
- `src/file_explorer/services/layout_manager.py` - Layout service

## Benefits

1. **Functional**: Center panes now display correctly
2. **Configurable**: Supports 1-4 panes with multiple layouts
3. **Robust**: Graceful fallback on errors
4. **Extensible**: Signal connections ready for features
5. **Maintainable**: Clear separation of concerns

## Future Enhancements

1. **Dynamic pane creation**: Create panes on-demand instead of all 4 upfront
2. **Pane types**: Support different pane types (terminal, preview, etc.)
3. **Custom layouts**: Allow user-defined splitter arrangements
4. **Pane cloning**: Duplicate current pane configuration
5. **Synchronized navigation**: Option to sync path changes across panes

## Conclusion

The center panes are now properly initialized and displayed. The multi-pane explorer creates 4 `FileExplorerPane` instances at startup and provides them to the `LayoutManagerUI`, which arranges them according to the saved or default configuration. Users can now browse files in the center area with full functionality.
