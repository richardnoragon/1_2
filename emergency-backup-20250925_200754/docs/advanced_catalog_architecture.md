# Advanced File Catalog Generator - Technical Architecture

## System Overview
Building upon the existing `catalog.py` foundation, we'll create a modern, feature-rich catalog generator with:

- **Multi-criteria sorting** (alphabetical, size, type, dates)
- **Dynamic color-coding** with accessibility support
- **Real-time re-sorting** capabilities
- **Multi-format export** (HTML, PDF, CSV, JSON, XML, Excel)
- **RFU Hub integration** for progress tracking

## Core Architecture Components

### 1. Data Model Layer
```python
# Core data structures for file catalog management
class FileEntry:
    - path: Path
    - size: int
    - created_date: datetime
    - modified_date: datetime
    - accessed_date: datetime
    - file_type: FileType
    - color_category: ColorCategory
    - metadata: Dict[str, Any]

class CatalogData:
    - entries: List[FileEntry]
    - sort_criteria: SortCriteria
    - color_scheme: ColorScheme
    - filters: FilterSettings
```

### 2. Sorting Engine
```python
class SortingEngine:
    - alphabetical_sort()
    - size_sort() # with small/medium/large categories
    - type_sort() # documents/images/videos/executables
    - date_sort() # recent/moderate/old timeframes
    - multi_criteria_sort()
```

### 3. Color-Coding System
```python
class ColorCodingEngine:
    - generate_color_scheme()
    - apply_category_colors()
    - create_accessibility_patterns()
    - generate_legend()
```

### 4. Export Engine
```python
class ExportEngine:
    - HTMLExporter: Enhanced CSS styling with color preservation
    - PDFExporter: Using reportlab with color support
    - CSVExporter: Color metadata in additional columns
    - JSONExporter: Structured data with color information
    - XMLExporter: Color attributes in XML elements
    - ExcelExporter: Cell formatting and conditional formatting
```

### 5. UI Components
- **Pre-generation Configuration Panel**: Sort criteria selection
- **Dynamic Re-sorting Controls**: Real-time sort switching
- **Color Legend Display**: Visual guide for color categories
- **Export Format Selection**: Multi-format export options
- **Progress Tracking**: Integration with RFU Hub

## Integration Strategy

### Extending Legacy Catalog
- Inherit from existing `CatalogWindow` base class
- Reuse proven file scanning logic from `_get_file_list()`
- Enhance HTML generation from `_HTML_HEADER` template
- Extend duplicate detection from `_check_duplicate()`

### RFU Hub Integration
- Follow pattern from `organize.py` for StandardWindow inheritance
- Implement hub registration similar to `hub.py` tool registration
- Add progress reporting for long-running operations
- Support menu callbacks like `_setup_menu_callbacks()`

## File Structure Plan
```
src/rfu/tools/file_management/
├── advanced_catalog/
│   ├── __init__.py
│   ├── advanced_catalog_window.py      # Main UI window
│   ├── catalog_data_model.py           # Data structures
│   ├── sorting_engine.py               # Sorting algorithms
│   ├── color_coding_engine.py          # Color management
│   ├── export_engine/
│   │   ├── __init__.py
│   │   ├── base_exporter.py
│   │   ├── html_exporter.py
│   │   ├── pdf_exporter.py
│   │   ├── csv_exporter.py
│   │   ├── json_exporter.py
│   │   ├── xml_exporter.py
│   │   └── excel_exporter.py
│   ├── ui/
│   │   ├── advanced_catalog.ui         # Main UI layout
│   │   ├── sort_config_dialog.ui       # Sort configuration
│   │   └── export_config_dialog.ui     # Export settings
│   └── resources/
│       ├── icons/
│       ├── color_schemes/
│       └── templates/
```

## Key Features Implementation

### 1. Comprehensive Sorting System
- **Alphabetical**: A-Z ranges with color gradients
- **Size-based**: Small (<1MB), Medium (1MB-100MB), Large (>100MB)
- **Type-based**: Documents (blue), Images (green), Videos (red), Audio (purple), Archives (orange), Executables (gray)
- **Date-based**: Recent (<30 days), Moderate (30-365 days), Old (>365 days)

### 2. Color-Coding Categories

#### Size-Based Colors
- **Small files (<1MB)**: Light Green (#E8F5E8)
- **Medium files (1MB-100MB)**: Light Blue (#E3F2FD)
- **Large files (>100MB)**: Light Orange (#FFF3E0)

#### Type-Based Colors
- **Documents**: Blue (#2196F3)
- **Images**: Green (#4CAF50)
- **Videos**: Red (#F44336)
- **Audio**: Purple (#9C27B0)
- **Archives**: Orange (#FF9800)
- **Executables**: Gray (#607D8B)
- **Other**: Light Gray (#E0E0E0)

#### Date-Based Colors
- **Recent (<30 days)**: Bright Green (#8BC34A)
- **Moderate (30-365 days)**: Yellow (#FFEB3B)
- **Old (>365 days)**: Light Red (#FFCDD2)

#### Alphabetical Colors
- **A-E**: Light Red (#FFEBEE)
- **F-J**: Light Orange (#FFF3E0)
- **K-O**: Light Yellow (#FFFDE7)
- **P-T**: Light Green (#E8F5E8)
- **U-Z**: Light Blue (#E3F2FD)

### 3. Accessibility Features
- **Color-blind support**: Patterns and icons alongside colors
- **High contrast mode**: Enhanced visibility options
- **Text indicators**: Written labels for all color categories
- **Keyboard navigation**: Full keyboard accessibility

### 4. Export Capabilities
- **HTML**: Enhanced CSS with responsive design and print styles
- **PDF**: Professional layout with color preservation and bookmarks
- **CSV**: Structured data with color metadata columns
- **JSON**: Machine-readable format with full metadata
- **XML**: Standards-compliant with color attributes
- **Excel**: Native formatting with conditional formatting rules

## Development Phases

### Phase 1: Core Foundation
1. Create data model and basic UI structure
2. Implement file scanning and basic sorting
3. Set up RFU Hub integration

### Phase 2: Sorting & Color-Coding
1. Develop comprehensive sorting algorithms
2. Implement color-coding engine
3. Create dynamic re-sorting interface

### Phase 3: Export System
1. Build export engine framework
2. Implement HTML and CSV exporters
3. Add PDF and Excel export capabilities

### Phase 4: Advanced Features
1. Add JSON and XML export support
2. Implement accessibility features
3. Create batch processing capabilities

### Phase 5: Polish & Documentation
1. Comprehensive testing and bug fixes
2. Performance optimization
3. User documentation and help system

## Technical Requirements

### Dependencies
- **PyQt5**: UI framework (already in use)
- **reportlab**: PDF generation with color support
- **openpyxl**: Excel file creation with formatting
- **Pillow**: Image processing for icons and patterns
- **colorama**: Terminal color support for debugging

### Performance Considerations
- **Lazy loading**: Load file metadata on demand
- **Chunked processing**: Process large directories in batches
- **Background threading**: Non-blocking UI during operations
- **Caching**: Cache sort results and color assignments
- **Memory management**: Efficient handling of large file lists

### Error Handling
- **Graceful degradation**: Continue processing when individual files fail
- **User feedback**: Clear error messages and recovery suggestions
- **Logging**: Comprehensive logging for debugging
- **Validation**: Input validation for all user configurations

This architecture provides a solid foundation for creating a powerful, extensible file catalog generator that significantly enhances the existing functionality while maintaining compatibility with the RFU ecosystem.