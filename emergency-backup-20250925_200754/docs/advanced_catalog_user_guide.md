# Advanced File Catalog Generator - User Guide

## Overview

The Advanced File Catalog Generator is a comprehensive tool for creating detailed, color-coded catalogs of file directories with multiple sorting options and export formats. It extends the existing RFU catalog functionality with advanced features including:

- **Multi-criteria sorting** (alphabetical, size, type, dates)
- **Dynamic color-coding** with accessibility support
- **Real-time re-sorting** capabilities
- **Multi-format export** (HTML, PDF, CSV, JSON, XML, Excel)
- **Accessibility features** for color-blind users
- **Batch processing** for multiple directories

## Getting Started

### Launching the Tool

1. **From RFU Hub**: Click the "Advanced File Catalog" button in the main hub interface
2. **Standalone**: Run the tool directly from the command line or file explorer

### Basic Workflow

1. **Select Directory**: Choose the folder you want to catalog
2. **Configure Sorting**: Select your preferred sorting method and color scheme
3. **Preview Results**: Review the color-coded file list
4. **Export Catalog**: Choose your desired export format and generate the catalog

## Interface Overview

### Main Window Components

#### Directory Selection Panel
- **Select Directory Button**: Browse and choose the target directory
- **Directory Path Display**: Shows the currently selected directory path
- **Include Subdirectories**: Toggle recursive directory scanning

#### Sorting Configuration Panel
- **Sort Criteria Dropdown**: Choose primary sorting method
  - Alphabetical (A-Z)
  - File Size (Small to Large)
  - File Type (Documents, Images, Videos, etc.)
  - Creation Date (Recent to Old)
  - Modification Date (Recent to Old)
  - Access Date (Recent to Old)
- **Advanced Sort Button**: Configure multi-criteria sorting
- **Apply Sort Button**: Apply the selected sorting method

#### Preview and Legend Section
- **File Preview List**: Color-coded list of files with icons
- **Color Legend**: Visual guide explaining the color scheme
- **File Count Display**: Shows total number of files found

#### Export Configuration Panel
- **Export Format Dropdown**: Choose output format
- **Export Settings Button**: Configure format-specific options
- **Export Button**: Generate and save the catalog

## Sorting Methods

### Alphabetical Sorting

Files are sorted by name and grouped into color-coded alphabetical ranges:

- **A-E Range**: Light Red background
- **F-J Range**: Light Orange background
- **K-O Range**: Light Yellow background
- **P-T Range**: Light Green background
- **U-Z Range**: Light Blue background

### Size-Based Sorting

Files are categorized by size with distinct colors:

- **Small Files (<1MB)**: Light Green background
- **Medium Files (1MB-100MB)**: Light Blue background
- **Large Files (>100MB)**: Light Orange background

### Type-Based Sorting

Files are grouped by type with category-specific colors:

- **Documents** (.pdf, .doc, .docx, .txt): Blue border
- **Images** (.jpg, .png, .gif, .bmp): Green border
- **Videos** (.mp4, .avi, .mkv, .mov): Red border
- **Audio** (.mp3, .wav, .flac, .aac): Purple border
- **Archives** (.zip, .rar, .7z, .tar): Orange border
- **Executables** (.exe, .msi, .app): Gray border
- **Other/Unknown**: Light Gray border

### Date-Based Sorting

Files are categorized by age with time-based colors:

- **Recent (<30 days)**: Bright Green gradient
- **Moderate (30-365 days)**: Yellow gradient
- **Old (>365 days)**: Light Red gradient

## Advanced Features

### Multi-Criteria Sorting

Access the Advanced Sort dialog to configure complex sorting:

1. Click "Advanced Sort..." button
2. Select primary sort criteria
3. Enable secondary sort criteria if needed
4. Choose ascending or descending order for each
5. Select color scheme preference
6. Click "OK" to apply

### Color Schemes

Choose from multiple color schemes to suit your needs:

- **Default**: Standard color palette with good contrast
- **High Contrast**: Black and white with bold colors for accessibility
- **Colorblind Friendly**: Colors selected for color vision deficiency
- **Monochrome**: Grayscale variations for printing
- **Custom**: User-defined color combinations

### Accessibility Features

#### For Color-Blind Users
- **Pattern Overlays**: Geometric patterns distinguish categories
- **Icon Indicators**: Unicode symbols for each file type
- **Text Labels**: Written category names alongside colors
- **High Contrast Mode**: Enhanced visibility options

#### Keyboard Navigation
- **Tab Navigation**: Move between interface elements
- **Arrow Keys**: Navigate file lists
- **Enter/Space**: Activate buttons and selections
- **Ctrl+O**: Open directory selection dialog
- **Ctrl+S**: Quick export to default format
- **F5**: Refresh file list

## Export Formats

### HTML Export

Creates a web page with embedded CSS and interactive features:

**Features:**
- Responsive design for mobile devices
- Print-friendly styles
- Interactive sorting (if enabled)
- Embedded color legend
- Clickable file links

**Options:**
- Include embedded CSS
- Enable responsive design
- Add print styles
- Include JavaScript features

### PDF Export

Generates a professional document with color preservation:

**Features:**
- Color-coded file entries
- Formatted tables
- Page headers and footers
- Bookmarks for navigation
- Print-ready layout

**Options:**
- Page size (A4, Letter, Legal)
- Include bookmarks
- Color preservation
- DPI setting (72-300)

### CSV Export

Creates a spreadsheet-compatible file with metadata:

**Features:**
- Color information in separate columns
- Full file metadata
- Accessibility labels
- Custom delimiters

**Options:**
- Include color data
- Include metadata
- Custom delimiter
- Encoding selection

### JSON Export

Produces structured data for programmatic use:

**Features:**
- Hierarchical data structure
- Complete metadata
- Color scheme information
- Schema validation

**Options:**
- Pretty printing
- Include JSON schema
- Compression options
- Custom field selection

### XML Export

Generates standards-compliant XML with attributes:

**Features:**
- Color attributes
- Nested structure
- DTD validation
- Namespace support

**Options:**
- Pretty printing
- Include DTD
- Custom namespace
- Attribute vs. element preference

### Excel Export

Creates a formatted spreadsheet with conditional formatting:

**Features:**
- Color-coded cells
- Auto-filtering
- Frozen headers
- Multiple worksheets
- Conditional formatting rules

**Options:**
- Conditional formatting
- Auto-filter headers
- Freeze header row
- Custom worksheet names

## Batch Processing

Process multiple directories efficiently:

1. **Access Batch Mode**: Tools → Batch Process
2. **Add Directories**: Select multiple source directories
3. **Configure Settings**: Apply same settings to all directories
4. **Set Output Options**: Choose output directory and naming scheme
5. **Start Processing**: Monitor progress for each directory

### Batch Configuration Options

- **Consistent Sorting**: Apply same sort criteria to all directories
- **Unified Color Scheme**: Use same colors across all catalogs
- **Output Naming**: Automatic naming based on directory names
- **Progress Tracking**: Real-time progress for each directory
- **Error Handling**: Continue processing if individual directories fail

## Tips and Best Practices

### Performance Optimization

- **Large Directories**: Use non-recursive mode for faster scanning
- **Network Drives**: Copy directories locally before cataloging
- **Memory Usage**: Close other applications when processing large directories
- **Export Size**: Choose appropriate formats for large file lists

### Color Scheme Selection

- **Printing**: Use monochrome scheme for black and white printers
- **Presentations**: High contrast scheme for projectors
- **Accessibility**: Colorblind-friendly scheme for inclusive sharing
- **Branding**: Custom schemes to match organizational colors

### Export Format Guidelines

- **Web Sharing**: HTML format for online viewing
- **Documentation**: PDF format for formal reports
- **Data Analysis**: CSV or JSON for further processing
- **Archival**: XML format for long-term storage
- **Collaboration**: Excel format for team editing

## Troubleshooting

### Common Issues

#### "Permission Denied" Errors
- **Cause**: Insufficient access rights to directory
- **Solution**: Run as administrator or choose accessible directory

#### "Out of Memory" Errors
- **Cause**: Directory contains too many files
- **Solution**: Use non-recursive mode or process subdirectories separately

#### "Export Failed" Errors
- **Cause**: Insufficient disk space or write permissions
- **Solution**: Check available space and output directory permissions

#### Color Display Issues
- **Cause**: Graphics driver or display settings
- **Solution**: Update graphics drivers or use high contrast mode

### Performance Issues

#### Slow Directory Scanning
- **Check**: Network connectivity for remote directories
- **Solution**: Copy to local drive or use faster network connection

#### Large Export Files
- **Check**: Number of files and selected export options
- **Solution**: Reduce metadata inclusion or split into multiple catalogs

#### Memory Usage
- **Check**: Available system RAM
- **Solution**: Close other applications or process smaller directories

## Integration with RFU Hub

### Hub Features

- **Progress Reporting**: Real-time progress updates in hub status bar
- **Resource Management**: Automatic resource allocation and cleanup
- **Tool Registration**: Seamless integration with other RFU tools
- **Settings Synchronization**: Shared preferences across RFU tools

### Menu Integration

Access catalog functions through RFU Hub menus:

- **File Menu**: New catalog, open directory, save settings
- **View Menu**: Toggle accessibility mode, change color schemes
- **Tools Menu**: Batch processing, preferences, help

## Keyboard Shortcuts

### Global Shortcuts
- **Ctrl+N**: New catalog
- **Ctrl+O**: Open directory
- **Ctrl+S**: Save/Export catalog
- **Ctrl+P**: Print preview
- **Ctrl+Q**: Exit application
- **F1**: Show help
- **F5**: Refresh file list
- **F11**: Toggle fullscreen

### Navigation Shortcuts
- **Tab**: Next control
- **Shift+Tab**: Previous control
- **Arrow Keys**: Navigate lists
- **Enter**: Activate selection
- **Space**: Toggle checkboxes
- **Escape**: Cancel dialog

### Sorting Shortcuts
- **Ctrl+1**: Alphabetical sort
- **Ctrl+2**: Size sort
- **Ctrl+3**: Type sort
- **Ctrl+4**: Date sort
- **Ctrl+Shift+S**: Advanced sort dialog

## Support and Resources

### Documentation
- **Architecture Guide**: Technical implementation details
- **Color Scheme Reference**: Complete color definitions
- **Export Specifications**: Format-specific documentation
- **API Reference**: Programmatic access documentation

### Getting Help
- **Built-in Help**: Press F1 for context-sensitive help
- **User Manual**: Complete documentation in Help menu
- **Online Resources**: Visit project website for updates
- **Community Support**: User forums and discussion groups

### Reporting Issues
- **Bug Reports**: Use built-in error reporting
- **Feature Requests**: Submit through project website
- **Performance Issues**: Include system specifications
- **Export Problems**: Provide sample files and settings

This user guide provides comprehensive information for effectively using the Advanced File Catalog Generator to create professional, accessible, and informative file catalogs.