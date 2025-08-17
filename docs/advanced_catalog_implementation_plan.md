# Advanced File Catalog Generator - Implementation Plan

## Project Structure

```
src/rfu/tools/file_management/advanced_catalog/
├── __init__.py                         # Package initialization
├── advanced_catalog_window.py          # Main UI window class
├── catalog_data_model.py               # Core data structures
├── sorting_engine.py                   # Sorting algorithms
├── color_coding_engine.py              # Color management system
├── export_engine/
│   ├── __init__.py
│   ├── base_exporter.py               # Abstract base exporter
│   ├── html_exporter.py               # HTML export with CSS
│   ├── pdf_exporter.py                # PDF export with reportlab
│   ├── csv_exporter.py                # CSV with color metadata
│   ├── json_exporter.py               # JSON structured export
│   ├── xml_exporter.py                # XML export with attributes
│   └── excel_exporter.py              # Excel with formatting
├── ui/
│   ├── advanced_catalog.ui            # Main window layout
│   ├── sort_config_dialog.ui          # Sort configuration dialog
│   └── export_config_dialog.ui        # Export settings dialog
└── resources/
    ├── icons/                          # UI icons and patterns
    ├── color_schemes/                  # Predefined color schemes
    └── templates/                      # Export templates
```

## Core Classes and Methods

### 1. FileEntry Data Model
```python
@dataclass
class FileEntry:
    """Represents a single file with all metadata."""
    path: Path
    name: str
    size: int
    created_date: datetime
    modified_date: datetime
    accessed_date: datetime
    file_type: FileType
    extension: str
    color_category: Optional[ColorCategory] = None
    sort_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_size_category(self) -> SizeCategory
    def get_date_category(self) -> DateCategory
    def get_type_category(self) -> TypeCategory
    def get_alphabetical_category(self) -> AlphabeticalCategory
```

### 2. CatalogData Container
```python
class CatalogData:
    """Main container for catalog data and operations."""
    def __init__(self):
        self.entries: List[FileEntry] = []
        self.sort_criteria: SortCriteria = SortCriteria.ALPHABETICAL
        self.color_scheme: ColorScheme = ColorScheme.DEFAULT
        self.filters: FilterSettings = FilterSettings()
        self.statistics: CatalogStatistics = CatalogStatistics()
    
    def add_entry(self, entry: FileEntry) -> None
    def remove_entry(self, path: Path) -> bool
    def clear(self) -> None
    def get_filtered_entries(self) -> List[FileEntry]
    def update_statistics(self) -> None
```

### 3. SortingEngine
```python
class SortingEngine:
    """Handles all sorting operations with color assignment."""
    
    @staticmethod
    def sort_alphabetical(entries: List[FileEntry]) -> List[FileEntry]:
        """Sort by name with A-Z color ranges."""
        
    @staticmethod
    def sort_by_size(entries: List[FileEntry]) -> List[FileEntry]:
        """Sort by size with small/medium/large categories."""
        
    @staticmethod
    def sort_by_type(entries: List[FileEntry]) -> List[FileEntry]:
        """Sort by file type with category colors."""
        
    @staticmethod
    def sort_by_date(entries: List[FileEntry], date_type: DateType) -> List[FileEntry]:
        """Sort by date with recent/moderate/old categories."""
        
    @staticmethod
    def sort_multi_criteria(entries: List[FileEntry], criteria: List[SortCriteria]) -> List[FileEntry]:
        """Sort by multiple criteria with priority."""
```

### 4. ColorCodingEngine
```python
class ColorCodingEngine:
    """Manages color assignment and accessibility features."""
    
    def __init__(self, scheme: ColorScheme = ColorScheme.DEFAULT):
        self.scheme = scheme
        self.accessibility_mode = False
        self.high_contrast_mode = False
    
    def assign_colors(self, entries: List[FileEntry], sort_criteria: SortCriteria) -> None
    def get_color_for_category(self, category: Any) -> ColorInfo
    def generate_legend(self, sort_criteria: SortCriteria) -> Dict[str, ColorInfo]
    def enable_accessibility_mode(self) -> None
    def get_pattern_for_category(self, category: Any) -> PatternInfo
```

### 5. AdvancedCatalogWindow
```python
class AdvancedCatalogWindow(StandardWindow):
    """Main window for advanced catalog generation."""
    
    def __init__(self):
        super().__init__(title="Advanced File Catalog Generator", window_type="file_operations")
        self.catalog_data = CatalogData()
        self.sorting_engine = SortingEngine()
        self.color_engine = ColorCodingEngine()
        self.export_engine = ExportEngine()
        
    def _setup_ui(self) -> None
    def _connect_signals(self) -> None
    def _load_directory(self) -> None
    def _scan_files(self, directory: Path, recursive: bool = False) -> None
    def _apply_sort(self, criteria: SortCriteria) -> None
    def _update_preview(self) -> None
    def _show_sort_config_dialog(self) -> None
    def _show_export_config_dialog(self) -> None
    def _export_catalog(self, format_type: ExportFormat) -> None
```

## UI Component Specifications

### Main Window Layout
```xml
<!-- advanced_catalog.ui structure -->
<QMainWindow>
    <QWidget name="centralwidget">
        <QVBoxLayout>
            <!-- Directory Selection -->
            <QHBoxLayout name="directoryLayout">
                <QPushButton name="selectDirectoryBtn">Select Directory</QPushButton>
                <QLabel name="directoryLabel">No directory selected</QLabel>
                <QCheckBox name="recursiveCheckBox">Include Subdirectories</QCheckBox>
            </QHBoxLayout>
            
            <!-- Sort Configuration Panel -->
            <QGroupBox name="sortConfigGroup" title="Sorting Configuration">
                <QHBoxLayout>
                    <QComboBox name="sortCriteriaCombo">
                        <item>Alphabetical (A-Z)</item>
                        <item>File Size</item>
                        <item>File Type</item>
                        <item>Creation Date</item>
                        <item>Modification Date</item>
                        <item>Access Date</item>
                    </QComboBox>
                    <QPushButton name="advancedSortBtn">Advanced Sort...</QPushButton>
                    <QPushButton name="applySortBtn">Apply Sort</QPushButton>
                </QHBoxLayout>
            </QGroupBox>
            
            <!-- Preview and Legend -->
            <QHBoxLayout>
                <!-- File Preview List -->
                <QVBoxLayout>
                    <QLabel>File Preview (Color-Coded)</QLabel>
                    <QListWidget name="filePreviewList" />
                    <QLabel name="fileCountLabel">0 files</QLabel>
                </QVBoxLayout>
                
                <!-- Color Legend -->
                <QVBoxLayout>
                    <QLabel>Color Legend</QLabel>
                    <QScrollArea>
                        <QWidget name="legendWidget" />
                    </QScrollArea>
                </QVBoxLayout>
            </QHBoxLayout>
            
            <!-- Export Configuration -->
            <QGroupBox name="exportConfigGroup" title="Export Configuration">
                <QHBoxLayout>
                    <QLabel>Export Format:</QLabel>
                    <QComboBox name="exportFormatCombo">
                        <item>HTML (with CSS)</item>
                        <item>PDF (with colors)</item>
                        <item>CSV (with metadata)</item>
                        <item>JSON (structured)</item>
                        <item>XML (with attributes)</item>
                        <item>Excel (with formatting)</item>
                    </QComboBox>
                    <QPushButton name="exportConfigBtn">Export Settings...</QPushButton>
                    <QPushButton name="exportBtn">Export Catalog</QPushButton>
                </QHBoxLayout>
            </QGroupBox>
            
            <!-- Status and Progress -->
            <QHBoxLayout>
                <QLabel name="statusLabel">Ready</QLabel>
                <QProgressBar name="progressBar" />
            </QHBoxLayout>
        </QVBoxLayout>
    </QWidget>
    
    <!-- Menu Bar -->
    <QMenuBar>
        <QMenu title="File">
            <QAction name="actionNew">New Catalog</QAction>
            <QAction name="actionOpen">Open Directory</QAction>
            <QAction name="actionSave">Save Settings</QAction>
            <QAction name="actionExit">Exit</QAction>
        </QMenu>
        <QMenu title="View">
            <QAction name="actionToggleAccessibility">Accessibility Mode</QAction>
            <QAction name="actionHighContrast">High Contrast</QAction>
            <QAction name="actionShowPatterns">Show Patterns</QAction>
        </QMenu>
        <QMenu title="Tools">
            <QAction name="actionBatchProcess">Batch Process</QAction>
            <QAction name="actionPreferences">Preferences</QAction>
        </QMenu>
    </QMenuBar>
</QMainWindow>
```

### Sort Configuration Dialog
```xml
<!-- sort_config_dialog.ui structure -->
<QDialog name="SortConfigDialog">
    <QVBoxLayout>
        <QLabel>Configure Multi-Criteria Sorting</QLabel>
        
        <!-- Primary Sort -->
        <QGroupBox title="Primary Sort Criteria">
            <QHBoxLayout>
                <QComboBox name="primarySortCombo" />
                <QRadioButton name="primaryAscBtn" text="Ascending" checked="true" />
                <QRadioButton name="primaryDescBtn" text="Descending" />
            </QHBoxLayout>
        </QGroupBox>
        
        <!-- Secondary Sort -->
        <QGroupBox title="Secondary Sort Criteria">
            <QCheckBox name="enableSecondarySort" text="Enable Secondary Sort" />
            <QHBoxLayout>
                <QComboBox name="secondarySortCombo" />
                <QRadioButton name="secondaryAscBtn" text="Ascending" checked="true" />
                <QRadioButton name="secondaryDescBtn" text="Descending" />
            </QHBoxLayout>
        </QGroupBox>
        
        <!-- Color Scheme Selection -->
        <QGroupBox title="Color Scheme">
            <QComboBox name="colorSchemeCombo">
                <item>Default</item>
                <item>High Contrast</item>
                <item>Colorblind Friendly</item>
                <item>Monochrome</item>
                <item>Custom</item>
            </QComboBox>
        </QGroupBox>
        
        <!-- Dialog Buttons -->
        <QDialogButtonBox>
            <QPushButton text="OK" />
            <QPushButton text="Cancel" />
            <QPushButton text="Reset to Defaults" />
        </QDialogButtonBox>
    </QVBoxLayout>
</QDialog>
```

### Export Configuration Dialog
```xml
<!-- export_config_dialog.ui structure -->
<QDialog name="ExportConfigDialog">
    <QVBoxLayout>
        <QLabel>Export Configuration</QLabel>
        
        <!-- Format-Specific Options -->
        <QTabWidget name="formatTabs">
            <QWidget title="HTML Options">
                <QVBoxLayout>
                    <QCheckBox name="htmlIncludeCss" text="Include embedded CSS" checked="true" />
                    <QCheckBox name="htmlResponsive" text="Responsive design" checked="true" />
                    <QCheckBox name="htmlPrintStyles" text="Print-friendly styles" />
                    <QCheckBox name="htmlJavaScript" text="Interactive features" />
                </QVBoxLayout>
            </QWidget>
            
            <QWidget title="PDF Options">
                <QVBoxLayout>
                    <QComboBox name="pdfPageSize">
                        <item>A4</item>
                        <item>Letter</item>
                        <item>Legal</item>
                    </QComboBox>
                    <QCheckBox name="pdfBookmarks" text="Include bookmarks" checked="true" />
                    <QCheckBox name="pdfColorPreservation" text="Preserve colors" checked="true" />
                    <QSpinBox name="pdfDpi" minimum="72" maximum="300" value="150" />
                </QVBoxLayout>
            </QWidget>
            
            <QWidget title="Excel Options">
                <QVBoxLayout>
                    <QCheckBox name="excelConditionalFormatting" text="Conditional formatting" checked="true" />
                    <QCheckBox name="excelAutoFilter" text="Auto-filter headers" checked="true" />
                    <QCheckBox name="excelFreezeHeaders" text="Freeze header row" checked="true" />
                    <QComboBox name="excelWorksheetName" editable="true" />
                </QVBoxLayout>
            </QWidget>
        </QTabWidget>
        
        <!-- Output Options -->
        <QGroupBox title="Output Options">
            <QVBoxLayout>
                <QHBoxLayout>
                    <QLabel>Output Directory:</QLabel>
                    <QLineEdit name="outputDirEdit" />
                    <QPushButton name="browseOutputBtn">Browse...</QPushButton>
                </QHBoxLayout>
                <QHBoxLayout>
                    <QLabel>Filename:</QLabel>
                    <QLineEdit name="filenameEdit" text="catalog" />
                </QHBoxLayout>
                <QCheckBox name="openAfterExport" text="Open file after export" checked="true" />
            </QVBoxLayout>
        </QGroupBox>
        
        <!-- Dialog Buttons -->
        <QDialogButtonBox>
            <QPushButton text="Export" />
            <QPushButton text="Cancel" />
            <QPushButton text="Preview" />
        </QDialogButtonBox>
    </QVBoxLayout>
</QDialog>
```

## Export Engine Specifications

### HTML Exporter
```python
class HTMLExporter(BaseExporter):
    """Export catalog as HTML with embedded CSS and color preservation."""
    
    def export(self, catalog_data: CatalogData, options: HTMLExportOptions) -> str:
        """Generate HTML catalog with color-coding."""
        
    def _generate_css(self, color_scheme: ColorScheme) -> str:
        """Generate CSS with color definitions."""
        
    def _generate_legend(self, legend_data: Dict[str, ColorInfo]) -> str:
        """Generate HTML legend with color samples."""
        
    def _generate_file_list(self, entries: List[FileEntry]) -> str:
        """Generate HTML file list with color classes."""
```

### PDF Exporter
```python
class PDFExporter(BaseExporter):
    """Export catalog as PDF with color preservation using reportlab."""
    
    def export(self, catalog_data: CatalogData, options: PDFExportOptions) -> str:
        """Generate PDF catalog with colors and formatting."""
        
    def _create_color_legend(self, canvas, legend_data: Dict[str, ColorInfo]) -> None:
        """Draw color legend on PDF."""
        
    def _draw_file_entry(self, canvas, entry: FileEntry, y_position: float) -> float:
        """Draw single file entry with color background."""
```

### Excel Exporter
```python
class ExcelExporter(BaseExporter):
    """Export catalog as Excel with conditional formatting and colors."""
    
    def export(self, catalog_data: CatalogData, options: ExcelExportOptions) -> str:
        """Generate Excel workbook with formatting."""
        
    def _apply_conditional_formatting(self, worksheet, entries: List[FileEntry]) -> None:
        """Apply color-based conditional formatting."""
        
    def _create_legend_sheet(self, workbook, legend_data: Dict[str, ColorInfo]) -> None:
        """Create separate legend worksheet."""
```

## Integration Points

### RFU Hub Integration
```python
# In advanced_catalog_window.py
class AdvancedCatalogWindow(StandardWindow):
    def __init__(self, hub_instance=None):
        super().__init__(title="Advanced File Catalog Generator", window_type="file_operations")
        self.hub_instance = hub_instance
        if hub_instance:
            hub_instance.register_tool("Advanced Catalog Generator", self)
    
    def _report_progress(self, percentage: int, message: str):
        """Report progress to hub."""
        if self.hub_instance:
            self.hub_instance.update_tool_progress("Advanced Catalog Generator", percentage, message)
```

### Menu System Integration
```python
# In hub.py - add to utilities list
("Advanced File Catalog", self.open_advanced_catalog, True),

def open_advanced_catalog(self) -> None:
    """Open advanced catalog generator."""
    try:
        from .tools.file_management.advanced_catalog import AdvancedCatalogWindow
        self.advanced_catalog_window = AdvancedCatalogWindow(hub_instance=self)
        self.advanced_catalog_window.show()
        self.register_tool("Advanced Catalog Generator", self.advanced_catalog_window)
    except ImportError as e:
        self._update_status_bar(f"Failed to load Advanced Catalog Generator: {e}")
```

This implementation plan provides a comprehensive blueprint for creating the advanced file catalog generator with all requested features while maintaining compatibility with the existing RFU ecosystem.