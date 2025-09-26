# RFU Multi-Pane File Explorer - User Guide

## Overview

The RFU Multi-Pane File Explorer is a comprehensive, enterprise-grade file management application built with Python and PyQt5/PyQt6. It provides advanced features for efficient file organization, cross-platform compatibility, and extensible architecture.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Interface Overview](#interface-overview)
4. [Features](#features)
5. [Configuration](#configuration)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt5 or PyQt6 (automatically detected)
- SQLite 3.8+ (included with Python)

### Required Dependencies

```bash
pip install PyQt5 >= 5.15  # or PyQt6 >= 6.0
pip install watchdog >= 2.0
pip install sqlalchemy >= 1.4
```

### Optional Dependencies

```bash
# Windows drive detection
pip install pywin32

# Enhanced image preview
pip install Pillow

# Performance monitoring
pip install psutil
```

### Installation Steps

1. Clone or download the RFU File Explorer source code
2. Install dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python -m src.rfu.file_explorer.main_application
   ```

## Getting Started

### First Launch

1. **Initial Setup**: The application will create its configuration directory and database on first launch
2. **Default Layout**: Two file explorer panes (left and right) will be created automatically
3. **Drive Detection**: Available drives will be detected and shown in the navigation panel

### Basic Navigation

- **Opening Directories**: Double-click folders or use the navigation breadcrumb
- **Changing Drives**: Click on drive icons in the toolbar or navigation panel
- **Going Back/Forward**: Use navigation buttons or keyboard shortcuts
- **Going Up**: Click the "Up" button or press Alt+Up

### Creating Panes

1. **Menu Method**: File → New Pane → File Explorer
2. **Keyboard**: Ctrl+N
3. **Context Menu**: Right-click in empty space → New Pane

## Interface Overview

### Main Components

#### Menu Bar
- **File**: New pane, close pane, exit
- **Edit**: Copy, cut, paste, select all
- **View**: View modes, layout options, zoom
- **Tools**: Search, preferences, batch operations
- **Help**: User guide, about

#### Toolbar
- **Navigation**: Back, forward, up, refresh
- **View Mode**: List, grid, tree, details, thumbnails
- **Layout**: Split horizontal/vertical, grid, tabbed
- **Search**: Quick search and advanced search

#### Pane Area
- **File Explorer Panes**: Main file browsing interface
- **Property Panel**: File/folder details and metadata
- **Preview Panel**: Quick preview of selected files

#### Status Bar
- **File Count**: Number of files and total size
- **Selection Info**: Selected items count and size
- **Progress**: Operation progress indicator
- **Path**: Current directory path

### Pane Types

#### File Explorer Pane
- **Purpose**: Browse and manage files and directories
- **Features**: Multiple view modes, sorting, filtering, file operations
- **Navigation**: Breadcrumb navigation, address bar

#### Property Panel
- **Purpose**: Display detailed information about selected files
- **Features**: File metadata, permissions, preview thumbnails
- **Actions**: Quick property editing

#### Preview Panel
- **Purpose**: Quick preview of file contents
- **Features**: Text preview, image preview, metadata display
- **Supported Types**: Text files, images, PDF (if available)

## Features

### Multi-Pane Management

#### Layout Options
- **Split Horizontal**: Panes arranged side by side
- **Split Vertical**: Panes arranged top and bottom
- **Grid**: Panes arranged in a grid pattern
- **Tabbed**: Panes organized as tabs
- **Floating**: Independent floating panes

#### Pane Operations
- **Create**: Add new panes for different directories
- **Clone**: Duplicate current pane with same path
- **Close**: Remove panes (minimum of one required)
- **Resize**: Drag splitters to adjust pane sizes

### File Operations

#### Basic Operations
- **Copy**: Ctrl+C or context menu
- **Cut**: Ctrl+X or context menu
- **Paste**: Ctrl+V or context menu
- **Delete**: Delete key or context menu
- **Rename**: F2 or context menu

#### Advanced Operations
- **Batch Operations**: Select multiple files for bulk operations
- **Move Between Panes**: Drag and drop between panes
- **Compare Directories**: Use multiple panes to compare contents
- **Synchronization**: Tools → Synchronize Directories

### View Modes

#### List View
- **Layout**: Vertical list with icons and names
- **Sorting**: Click column headers to sort
- **Selection**: Click to select, Ctrl+click for multiple

#### Grid View
- **Layout**: Grid of large icons with names
- **Icon Size**: Adjustable via zoom controls
- **Preview**: Thumbnail generation for images

#### Tree View
- **Layout**: Hierarchical directory tree
- **Navigation**: Expand/collapse directory nodes
- **Focus**: Shows directory structure with file list

#### Details View
- **Layout**: Detailed list with multiple columns
- **Columns**: Name, size, type, modified date, permissions
- **Customization**: Add/remove columns via context menu

#### Thumbnail View
- **Layout**: Large thumbnails for images and documents
- **Preview**: Quick preview generation
- **Performance**: Lazy loading for large directories

### Search and Filtering

#### Quick Search
- **Access**: Ctrl+F or search box in toolbar
- **Scope**: Current directory only
- **Features**: Real-time filtering as you type

#### Advanced Search
- **Access**: Tools → Advanced Search
- **Scope**: Recursive directory search
- **Criteria**: Name patterns, file types, size, date ranges
- **Results**: Dedicated results pane

#### Filtering
- **File Type Filter**: Show only specific file types
- **Size Filter**: Filter by file size ranges
- **Date Filter**: Filter by modification date
- **Custom Patterns**: Use wildcards and regex patterns

### Session Management

#### Auto-Save
- **Pane Layout**: Automatically saved on exit
- **Paths**: Current directories in each pane
- **Settings**: View preferences and window state

#### Manual Sessions
- **Save Session**: File → Save Session
- **Load Session**: File → Load Session
- **Default Session**: Restored on startup

## Configuration

### Preferences Access
- **Menu**: Tools → Preferences
- **Keyboard**: Ctrl+,

### General Settings
- **Startup Behavior**: Default session, last session, custom
- **File Operations**: Confirmation dialogs, default actions
- **Performance**: Cache size, thumbnail generation

### Appearance Settings
- **Theme**: Light, dark, system default
- **Font**: Interface font family and size
- **Icons**: Icon size and style
- **Colors**: Custom color schemes

### Pane Settings
- **Default Layout**: Preferred layout for new sessions
- **Default View Mode**: Preferred view mode for new panes
- **Navigation**: Breadcrumb style, address bar visibility

### Performance Settings
- **Cache Size**: Database cache size limit
- **Thumbnails**: Enable/disable thumbnail generation
- **Monitoring**: File system change monitoring
- **Memory**: Memory usage limits

## Keyboard Shortcuts

### Navigation
- **Ctrl+N**: New pane
- **Ctrl+W**: Close current pane
- **Alt+Left**: Back
- **Alt+Right**: Forward
- **Alt+Up**: Up one level
- **F5**: Refresh current pane

### File Operations
- **Ctrl+C**: Copy selected files
- **Ctrl+X**: Cut selected files
- **Ctrl+V**: Paste files
- **Delete**: Delete selected files
- **F2**: Rename selected file
- **Ctrl+A**: Select all files

### View Controls
- **Ctrl+1**: List view
- **Ctrl+2**: Grid view
- **Ctrl+3**: Tree view
- **Ctrl+4**: Details view
- **Ctrl+5**: Thumbnail view
- **Ctrl++**: Zoom in
- **Ctrl+-**: Zoom out

### Search and Filter
- **Ctrl+F**: Quick search
- **Ctrl+Shift+F**: Advanced search
- **Escape**: Clear search/filter
- **Ctrl+L**: Focus address bar

### Layout Management
- **F11**: Toggle fullscreen
- **Ctrl+Shift+H**: Split horizontal
- **Ctrl+Shift+V**: Split vertical
- **Ctrl+Shift+G**: Grid layout
- **Ctrl+Shift+T**: Tabbed layout

## Troubleshooting

### Common Issues

#### Application Won't Start
**Symptoms**: Error messages during startup, crashes on launch
**Solutions**:
1. Check Python version (3.9+ required)
2. Verify PyQt5/PyQt6 installation: `python -c "import PyQt5.QtWidgets"`
3. Check permissions on configuration directory
4. Try running with `--debug` flag for detailed error information

#### Slow Performance
**Symptoms**: Sluggish interface, slow directory loading
**Solutions**:
1. Reduce cache size in preferences
2. Disable thumbnail generation for large directories
3. Close unnecessary panes
4. Check available system memory

#### File Operations Fail
**Symptoms**: Copy/move operations don't work, permission errors
**Solutions**:
1. Check file permissions
2. Verify destination has sufficient space
3. Close files that may be in use by other applications
4. Run application as administrator (Windows) if needed

#### Database Errors
**Symptoms**: Cache not working, settings not saved
**Solutions**:
1. Check write permissions on configuration directory
2. Delete corrupted database file (will reset cache)
3. Verify SQLite version: `python -c "import sqlite3; print(sqlite3.sqlite_version)"`

### Performance Optimization

#### For Large Directories
- Disable thumbnail generation
- Use list view instead of grid/thumbnail views
- Increase cache size if you have sufficient RAM
- Enable lazy loading in preferences

#### For Slow Systems
- Reduce number of open panes
- Disable file system monitoring
- Use minimal theme
- Disable animations and effects

### Configuration Reset

#### Reset All Settings
1. Close the application
2. Delete the configuration directory:
   - Windows: `%APPDATA%\RFU\FileExplorer`
   - macOS: `~/Library/Application Support/RFU/FileExplorer`
   - Linux: `~/.config/RFU/FileExplorer`
3. Restart the application

#### Reset Database Only
1. Close the application
2. Delete `cache.db` from the configuration directory
3. Restart the application

### Log Files

#### Location
- Windows: `%APPDATA%\RFU\FileExplorer\logs`
- macOS: `~/Library/Logs/RFU/FileExplorer`
- Linux: `~/.local/share/RFU/FileExplorer/logs`

#### Log Levels
- **ERROR**: Critical errors and exceptions
- **WARNING**: Non-critical issues and warnings
- **INFO**: General operation information
- **DEBUG**: Detailed diagnostic information

### Getting Help

#### Documentation
- User Guide: This document
- API Documentation: See `docs/api_documentation.md`
- Developer Guide: See `docs/developer_guide.md`

#### Support
- Issue Tracker: Report bugs and feature requests
- User Forum: Community support and tips
- Email Support: For enterprise users

#### Version Information
Check your version with Help → About or run:
```bash
python -m src.rfu.file_explorer.main_application --version
```

---

**Last Updated**: 2025-09-12  
**Version**: 1.0.0  
**Compatibility**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)