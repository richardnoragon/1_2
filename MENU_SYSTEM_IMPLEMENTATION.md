# Comprehensive Menu System for Richard's File Utilities

This document describes the implementation of a standardized menu system for all tool interfaces in Richard's File Utilities, providing consistent navigation, keyboard shortcuts, and platform-specific design.

## Overview

The menu system consists of several key components:

1. **MenuManager** - Central menu management class
2. **StandardWindow** - Enhanced base window class with menu integration
3. **Theme Integration** - Consistent styling across all menus
4. **Keyboard Shortcuts** - Platform-specific shortcuts for all actions
5. **Callback System** - Flexible event handling for menu actions

## Features

### Standardized Menu Structure

All tool windows include the following menu structure:

#### File Menu
- **New Project** (Ctrl+N) - Create new project/document
- **Open** (Ctrl+O) - Open file or project
- **Recent Files** - Submenu with recently accessed files
- **Save** (Ctrl+S) - Save current work
- **Save As** (Ctrl+Shift+S) - Save with new name
- **Export** (Ctrl+E) - Export data
- **Import** (Ctrl+I) - Import data
- **Print** (Ctrl+P) - Print current document
- **Preferences** (Ctrl+,) - Open application preferences
- **Exit** (Ctrl+Q) - Close application with confirmation

#### Edit Menu
- **Undo** (Ctrl+Z) - Undo last action
- **Redo** (Ctrl+Y) - Redo last undone action
- **Cut** (Ctrl+X) - Cut selection to clipboard
- **Copy** (Ctrl+C) - Copy selection to clipboard
- **Paste** (Ctrl+V) - Paste from clipboard
- **Select All** (Ctrl+A) - Select all items
- **Find** (Ctrl+F) - Find text or items
- **Replace** (Ctrl+H) - Find and replace text

#### View Menu
- **Zoom In** (Ctrl++) - Increase zoom level
- **Zoom Out** (Ctrl+-) - Decrease zoom level
- **Reset Zoom** (Ctrl+0) - Reset zoom to default
- **Theme** - Light/Dark theme selection
- **Fullscreen** (F11) - Toggle fullscreen mode
- **Always on Top** - Keep window on top
- **Refresh** (F5) - Refresh current view

#### Tools Menu
- **Options** - Tool-specific options
- **Log Viewer** - View application logs
- **Performance Monitor** - Monitor performance
- **Reset Settings** - Reset to defaults

#### Help Menu
- **User Guide** (F1) - Open documentation
- **Keyboard Shortcuts** (Ctrl+?) - Show shortcuts
- **Visit Website** - Open project website
- **Report Bug** - Report issues
- **System Information** - Show system info
- **Check for Updates** - Check for updates
- **About** - About dialog

## Implementation

### 1. MenuManager Class

The `MenuManager` class (`gui/menu_manager.py`) provides centralized menu creation and management:

```python
from gui.menu_manager import MenuManager

class YourToolWindow(StandardWindow):
    def __init__(self):
        super().__init__(
            title="Your Tool Name",
            enable_menu=True,
            window_type="utility"
        )
        
        # Menu is automatically created
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Register tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            self.menu_manager.register_callback('save_file', self.save_data)
            self.menu_manager.register_callback('open_file', self.load_data)
            self.menu_manager.register_callback('export_data', self.export_data)
```

### 2. StandardWindow Integration

The enhanced `StandardWindow` class automatically creates menus:

```python
from src.rfu.gui.standard_window import StandardWindow

class MyTool(StandardWindow):
    def __init__(self):
        super().__init__(
            title="My Tool",
            enable_menu=True,      # Enable menu system
            window_type="utility"  # Window type: "main", "utility", "dialog"
        )
```

### 3. Menu Callbacks

Tools can register custom callbacks for menu actions:

```python
def _setup_menu_callbacks(self):
    """Setup tool-specific menu callbacks."""
    self.menu_manager.register_callback('save_file', self.save_current_data)
    self.menu_manager.register_callback('open_file', self.load_file_data)
    self.menu_manager.register_callback('export_data', self.export_current_data)
    self.menu_manager.register_callback('import_data', self.import_file_data)
    self.menu_manager.register_callback('show_options', self.show_tool_options)
    self.menu_manager.register_callback('refresh', self.refresh_tool_view)

def save_current_data(self):
    """Handle save action."""
    # Your save implementation
    pass
```

## Styling and Themes

### Platform-Specific Design

The menu system follows platform-specific design guidelines:

- **Windows**: Standard Windows menu styling with proper spacing
- **Theme Support**: Light and dark themes with consistent colors
- **Hover Effects**: Visual feedback on menu item interaction
- **Keyboard Navigation**: Full keyboard navigation support

### CSS Styling

Menus are styled using CSS-like stylesheets:

```python
menubar.setStyleSheet(f"""
    QMenuBar {{
        background-color: {Colors.BACKGROUND_LIGHT.name()};
        color: {Colors.TEXT_PRIMARY.name()};
        border-bottom: 1px solid {Colors.BORDER_LIGHT.name()};
        padding: 2px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {Colors.PRIMARY.name()};
        color: {Colors.TEXT_LIGHT.name()};
    }}
    
    QMenu {{
        background-color: {Colors.BACKGROUND_LIGHT.name()};
        border: 1px solid {Colors.BORDER_LIGHT.name()};
        border-radius: 4px;
    }}
""")
```

## Keyboard Shortcuts

### Standard Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| Ctrl+N | New | Create new project/document |
| Ctrl+O | Open | Open file or project |
| Ctrl+S | Save | Save current work |
| Ctrl+Shift+S | Save As | Save with new name |
| Ctrl+P | Print | Print current document |
| Ctrl+Q | Exit | Close application |
| Ctrl+Z | Undo | Undo last action |
| Ctrl+Y | Redo | Redo last action |
| Ctrl+X | Cut | Cut to clipboard |
| Ctrl+C | Copy | Copy to clipboard |
| Ctrl+V | Paste | Paste from clipboard |
| Ctrl+A | Select All | Select all items |
| Ctrl+F | Find | Find text/items |
| Ctrl+H | Replace | Find and replace |
| Ctrl++ | Zoom In | Increase zoom |
| Ctrl+- | Zoom Out | Decrease zoom |
| Ctrl+0 | Reset Zoom | Reset zoom level |
| F11 | Fullscreen | Toggle fullscreen |
| F5 | Refresh | Refresh view |
| F1 | Help | Open user guide |
| Ctrl+? | Shortcuts | Show shortcuts |

### Custom Shortcuts

Tools can add custom shortcuts:

```python
custom_action = self.menu_manager._create_action(
    'Custom Action',
    'Ctrl+Shift+C',
    'Perform custom action',
    callback=self.custom_function
)
tools_menu.addAction(custom_action)
```

## Dialog Integration

### Built-in Dialogs

The menu system includes several built-in dialogs:

- **LogViewerDialog** - View application logs
- **HelpDialog** - User documentation
- **KeyboardShortcutsDialog** - Shortcut reference
- **SystemInfoDialog** - System information
- **AboutDialog** - Application information

### Custom Dialogs

Tools can add custom dialogs:

```python
def show_preferences(self):
    """Show tool-specific preferences."""
    dialog = MyPreferencesDialog(self)
    dialog.exec_()
```

## Advanced Features

### Recent Files Management

The menu system automatically manages recent files:

```python
# Files are automatically added to recent list when opened
self.menu_manager._add_to_recent_files(file_path)

# Recent files appear in File > Recent Files submenu
```

### Window State Management

Window geometry and state are automatically saved/restored:

```python
# Automatically saves window state on exit
self.menu_manager._save_window_state()

# Automatically restores on startup
self.menu_manager.restore_window_state()
```

### Theme Switching

Users can switch themes through the View menu:

```python
# Themes are applied automatically
# Theme preference is saved in settings
```

## Usage Examples

### Basic Tool Integration

```python
from src.rfu.gui.standard_window import StandardWindow

class MyFileTool(StandardWindow):
    def __init__(self):
        super().__init__(
            title="File Processing Tool",
            enable_menu=True,
            window_type="utility"
        )
        
        self.data = []
        self._setup_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        self.menu_manager.register_callback('save_file', self.save_data)
        self.menu_manager.register_callback('open_file', self.load_data)
        self.menu_manager.register_callback('export_data', self.export_results)
    
    def save_data(self):
        """Save current data to file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Data")
        if file_path:
            # Save implementation
            pass
    
    def load_data(self, file_path=None):
        """Load data from file."""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Data")
        if file_path:
            # Load implementation
            pass
```

### Enhanced Tool with Custom Menus

```python
class AdvancedTool(StandardWindow):
    def __init__(self):
        super().__init__(
            title="Advanced Processing Tool",
            enable_menu=True,
            window_type="utility"
        )
        
        self._setup_ui()
        self._setup_menu_callbacks()
        self._add_custom_menus()
    
    def _add_custom_menus(self):
        """Add tool-specific menu items."""
        if hasattr(self, 'menu_manager') and self.menu_manager.tools_menu:
            # Add custom submenu
            custom_menu = self.menu_manager.tools_menu.addMenu('Advanced &Options')
            
            # Add custom actions
            process_action = custom_menu.addAction('&Process Files')
            process_action.setShortcut('Ctrl+Shift+P')
            process_action.triggered.connect(self.process_files)
            
            analyze_action = custom_menu.addAction('&Analyze Data')
            analyze_action.setShortcut('Ctrl+Shift+A')
            analyze_action.triggered.connect(self.analyze_data)
```

## Testing

### Demo Application

Run the menu system demo to see all features:

```bash
python menu_system_demo.py
```

### Individual Tool Testing

Test menu integration in specific tools:

```bash
python enhanced_secure_delete_with_menu.py
```

## Best Practices

1. **Always use StandardWindow** as the base class for tools
2. **Register callbacks** for all menu actions your tool supports
3. **Use standard shortcuts** where possible
4. **Provide tool-specific options** in the Tools menu
5. **Handle menu actions gracefully** with proper error handling
6. **Save user preferences** through the menu system
7. **Test keyboard shortcuts** thoroughly
8. **Provide meaningful status messages** for menu actions

## Troubleshooting

### Common Issues

1. **Menu not appearing**: Ensure `enable_menu=True` in StandardWindow constructor
2. **Shortcuts not working**: Check for conflicts with system shortcuts
3. **Styling issues**: Verify theme manager is properly imported
4. **Callback errors**: Ensure all registered callbacks are valid functions

### Debug Information

Enable debug logging to troubleshoot menu issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MenuManager')
```

## Future Enhancements

- Context menu support
- Toolbar integration
- Plugin system for menu extensions
- Customizable keyboard shortcuts
- Menu item icons
- Dynamic menu generation
- Multi-language support

## Files Modified/Created

1. `gui/menu_manager.py` - Main menu management system
2. `src/rfu/gui/standard_window.py` - Enhanced with menu support
3. `gui/themes.py` - Updated with menu styling constants
4. `main.py` - Updated to use new menu system
5. `enhanced_secure_delete_with_menu.py` - Example implementation
6. `menu_system_demo.py` - Demonstration application

## Conclusion

The comprehensive menu system provides a consistent, professional interface across all RFU tools while maintaining flexibility for tool-specific customizations. The system follows platform conventions, supports full keyboard navigation, and integrates seamlessly with the existing theme system.
