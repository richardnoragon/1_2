# PDF Tools Phase 2.2 - Technical Specification

## 📋 Overview

This document provides detailed technical specifications for integrating PDF extraction tools into the RFU hub following the exact patterns established in Phase 2.1. Each component mirrors the architecture, naming conventions, and implementation patterns used for split, merge, and sign operations.

## 🏗️ Core Components Architecture

### 1. PDF Extraction Engine (`pdf_extraction_engine.py`)

#### Class Structure (mirroring `pdf_operation_engine.py`)

```python
class PDFExtractionEngine:
    """
    Main PDF extraction engine with unified interface for all extraction operations.
    Mirrors the structure and patterns of PDFOperationEngine from Phase 2.1.
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.validator = PDFExtractionValidator()
        self.progress_manager = get_progress_manager()
        self.error_manager = get_error_manager()
    
    # Core extraction methods (mirroring Phase 2.1 operation methods)
    def extract_images(self, input_file: str, output_dir: str, options: Dict[str, Any], 
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Extract images from PDF file with size filtering and format options"""
        
    def extract_links(self, input_file: str, output_file: str, options: Dict[str, Any],
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Extract hyperlinks and URLs from PDF file"""
        
    def extract_metadata(self, input_file: str, options: Dict[str, Any],
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Extract document metadata and properties"""
        
    def extract_tables(self, input_file: str, output_dir: str, options: Dict[str, Any],
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Extract tabular data using Camelot with advanced configuration"""
        
    def extract_text(self, input_file: str, output_file: str, options: Dict[str, Any],
                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Extract text content with layout preservation options"""
    
    # Batch processing (following Phase 2.1 patterns)
    def extract_batch(self, input_files: List[str], extraction_types: List[str],
                     output_dir: str, options: Dict[str, Any],
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform batch extraction operations across multiple files"""

class PDFExtractionValidator:
    """
    PDF extraction validation class mirroring PDFValidator from Phase 2.1
    """
    
    def validate_extraction_input(self, input_file: str, extraction_type: str) -> bool:
        """Validate input file for specific extraction type"""
        
    def validate_extraction_options(self, extraction_type: str, options: Dict) -> bool:
        """Validate extraction options for specific type"""
        
    def check_extraction_dependencies(self, extraction_type: str) -> bool:
        """Check if required dependencies are available for extraction type"""
```

#### API Specifications

**Image Extraction Options:**
```python
image_options = {
    'min_width': int,           # Minimum image width (default: 100)
    'min_height': int,          # Minimum image height (default: 100)
    'output_format': str,       # Output format: 'png', 'jpg', 'bmp' (default: 'png')
    'preserve_transparency': bool,  # Preserve alpha channel (default: True)
    'quality': int,             # JPEG quality 1-100 (default: 95)
    'pages': str               # Page range: 'all', '1-5', '1,3,5' (default: 'all')
}
```

**Link Extraction Options:**
```python
link_options = {
    'include_internal': bool,   # Include internal PDF links (default: True)
    'include_external': bool,   # Include external URLs (default: True)
    'output_format': str,       # 'txt', 'csv', 'json' (default: 'txt')
    'organize_by_page': bool,   # Organize links by page (default: False)
    'validate_urls': bool       # Validate URL accessibility (default: False)
}
```

**Metadata Extraction Options:**
```python
metadata_options = {
    'include_system': bool,     # Include system metadata (default: True)
    'include_custom': bool,     # Include custom properties (default: True)
    'date_format': str,         # Date format string (default: 'ISO')
    'output_format': str,       # 'txt', 'json', 'xml' (default: 'txt')
    'filter_empty': bool        # Filter empty metadata fields (default: True)
}
```

**Table Extraction Options:**
```python
table_options = {
    'flavor': str,              # 'lattice', 'stream' (default: 'lattice')
    'pages': str,               # Page range (default: 'all')
    'line_scale': int,          # Line scale factor (default: 15)
    'edge_tol': int,            # Edge tolerance (default: 50)
    'row_tol': int,             # Row tolerance (default: 2)
    'column_tol': int,          # Column tolerance (default: 2)
    'process_background': bool, # Process background (default: False)
    'output_format': str        # 'csv', 'excel', 'json' (default: 'csv')
}
```

**Text Extraction Options:**
```python
text_options = {
    'pages': str,               # Page range (default: 'all')
    'preserve_layout': bool,    # Preserve text layout (default: True)
    'include_page_numbers': bool, # Include page numbers (default: True)
    'output_format': str,       # 'txt', 'rtf', 'html' (default: 'txt')
    'encoding': str,            # Text encoding (default: 'utf-8')
    'line_separator': str       # Line separator (default: '\n')
}
```

### 2. Parameter Dialog System (`pdf_extraction_dialogs.py`)

#### Dialog Classes (mirroring `pdf_parameter_dialogs.py`)

```python
class PDFExtractionDialogBase(QDialog):
    """
    Base class for all extraction parameter dialogs.
    Mirrors the styling and behavior patterns from Phase 2.1 dialogs.
    """
    
    def __init__(self, parent=None, title="PDF Extraction"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.result_data = {}
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup base UI components"""
        
    def apply_styling(self):
        """Apply consistent RFU hub styling"""
        
    def validate_inputs(self) -> bool:
        """Validate user inputs"""
        
    def get_extraction_options(self) -> Dict[str, Any]:
        """Get extraction options from dialog"""

class PDFExtractImagesDialog(PDFExtractionDialogBase):
    """Image extraction parameter dialog with filtering and format options"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Extract Images from PDF")
        self.setup_image_specific_ui()
    
    def setup_image_specific_ui(self):
        """Setup image extraction specific UI components"""
        # Size filtering controls
        # Format selection
        # Quality settings
        # Page range selection
        # Preview capabilities

class PDFExtractLinksDialog(PDFExtractionDialogBase):
    """Link extraction parameter dialog with organization options"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Extract Links from PDF")
        self.setup_link_specific_ui()
    
    def setup_link_specific_ui(self):
        """Setup link extraction specific UI components"""
        # Link type selection
        # Output format options
        # Organization settings
        # Validation options

class PDFExtractMetadataDialog(PDFExtractionDialogBase):
    """Metadata extraction parameter dialog with formatting options"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Extract Metadata from PDF")
        self.setup_metadata_specific_ui()
    
    def setup_metadata_specific_ui(self):
        """Setup metadata extraction specific UI components"""
        # Metadata type selection
        # Date formatting options
        # Output format selection
        # Filtering options

class PDFExtractTablesDialog(PDFExtractionDialogBase):
    """Table extraction parameter dialog with Camelot configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Extract Tables from PDF")
        self.setup_table_specific_ui()
    
    def setup_table_specific_ui(self):
        """Setup table extraction specific UI components"""
        # Camelot flavor selection
        # Tolerance settings
        # Page range selection
        # Output format options
        # Advanced configuration

class PDFExtractTextDialog(PDFExtractionDialogBase):
    """Text extraction parameter dialog with layout options"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Extract Text from PDF")
        self.setup_text_specific_ui()
    
    def setup_text_specific_ui(self):
        """Setup text extraction specific UI components"""
        # Page range selection
        # Layout preservation options
        # Format selection
        # Encoding options
        # Preview capabilities

class PDFBatchExtractionDialog(PDFExtractionDialogBase):
    """Unified batch extraction dialog for multiple extraction types"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Batch PDF Extraction")
        self.setup_batch_specific_ui()
    
    def setup_batch_specific_ui(self):
        """Setup batch extraction specific UI components"""
        # File selection with drag-and-drop
        # Extraction type selection (checkboxes)
        # Output directory selection
        # Progress tracking
        # Batch configuration options
```

### 3. Functional Integration Layer (`pdf_extraction_integration.py`)

#### Integration Class (mirroring `pdf_functional_integration.py`)

```python
class PDFExtractionIntegration:
    """
    Integration layer connecting extraction operations with enhanced PDF tools widget.
    Mirrors the structure and patterns of PDFFunctionalIntegration from Phase 2.1.
    """
    
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.extraction_engine = PDFExtractionEngine()
        self.logger = setup_logger(__name__)
        self.progress_manager = get_progress_manager()
        self.error_manager = get_error_manager()
    
    # Functional extraction methods (mirroring Phase 2.1 functional methods)
    def extract_images_functional(self) -> bool:
        """Complete image extraction workflow with dialog, processing, and result handling"""
        
    def extract_links_functional(self) -> bool:
        """Complete link extraction workflow with dialog, processing, and result handling"""
        
    def extract_metadata_functional(self) -> bool:
        """Complete metadata extraction workflow with dialog, processing, and result handling"""
        
    def extract_tables_functional(self) -> bool:
        """Complete table extraction workflow with dialog, processing, and result handling"""
        
    def extract_text_functional(self) -> bool:
        """Complete text extraction workflow with dialog, processing, and result handling"""
        
    def extract_batch_functional(self) -> bool:
        """Complete batch extraction workflow with dialog, processing, and result handling"""
    
    # Helper methods (mirroring Phase 2.1 helper patterns)
    def _show_extraction_dialog(self, dialog_class, title: str) -> Optional[Dict]:
        """Show extraction parameter dialog and return options"""
        
    def _execute_extraction_operation(self, operation_name: str, operation_func: Callable,
                                    *args, **kwargs) -> bool:
        """Execute extraction operation with progress tracking and error handling"""
        
    def _handle_extraction_result(self, operation_name: str, result: Dict,
                                output_path: str) -> None:
        """Handle extraction operation result with user feedback"""
        
    def _show_extraction_progress(self, operation_name: str, total_items: int) -> QProgressDialog:
        """Show progress dialog for extraction operation"""

# Integration function (mirroring Phase 2.1 integration pattern)
def integrate_extraction_pdf_operations(widget) -> bool:
    """
    Integrate extraction operations with enhanced PDF tools widget.
    Mirrors integrate_functional_pdf_operations from Phase 2.1.
    """
    try:
        # Check if extraction components are available
        if not _check_extraction_dependencies():
            return False
        
        # Create integration instance
        integration = PDFExtractionIntegration(widget)
        
        # Replace placeholder methods with functional implementations
        widget.extract_images = integration.extract_images_functional
        widget.extract_links = integration.extract_links_functional
        widget.extract_metadata = integration.extract_metadata_functional
        widget.extract_tables = integration.extract_tables_functional
        widget.extract_text = integration.extract_text_functional
        widget.extract_batch = integration.extract_batch_functional
        
        # Store integration instance
        widget.extraction_integration = integration
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to integrate extraction operations: {e}")
        return False
```

### 4. Enhanced Widget Updates (`enhanced_pdf_tools_widget.py`)

#### Widget Integration Updates

```python
class EnhancedPDFToolsWidget(QWidget):
    """Enhanced PDF tools widget with extraction operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... existing initialization ...
        self.init_extraction_integration()
    
    def init_extraction_integration(self):
        """Initialize extraction operations integration"""
        try:
            from pdf_extraction_integration import integrate_extraction_pdf_operations
            success = integrate_extraction_pdf_operations(self)
            if success:
                self.extraction_functional_available = True
                self.logger.info("Extraction operations integrated successfully")
            else:
                self.extraction_functional_available = False
                self.logger.warning("Extraction operations integration failed - using placeholders")
        except ImportError:
            self.extraction_functional_available = False
            self.logger.warning("Extraction integration not available - using placeholders")
    
    # Updated extraction methods (replacing placeholders with functional implementations)
    def extract_images(self):
        """Extract images from PDF using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_images_functional()
        else:
            return self._extract_images_placeholder()
    
    def extract_links(self):
        """Extract links from PDF using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_links_functional()
        else:
            return self._extract_links_placeholder()
    
    def extract_metadata(self):
        """Extract metadata from PDF using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_metadata_functional()
        else:
            return self._extract_metadata_placeholder()
    
    def extract_tables(self):
        """Extract tables from PDF using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_tables_functional()
        else:
            return self._extract_tables_placeholder()
    
    def extract_text(self):
        """Extract text from PDF using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_text_functional()
        else:
            return self._extract_text_placeholder()
    
    def extract_batch(self):
        """Perform batch extraction using functional implementation"""
        if hasattr(self, 'extraction_integration'):
            return self.extraction_integration.extract_batch_functional()
        else:
            return self._extract_batch_placeholder()
    
    # Content Extraction Tab Updates
    def create_content_extraction_tab(self):
        """Create content extraction tab with functional operations"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Content Extraction Tools")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font: bold 16pt; color: #2c3e50; margin: 10px;")
        layout.addWidget(header)
        
        # Extraction tools grid (updated with batch extraction)
        tools = [
            ("Extract Text", "Extract textual content", "#607D8B", self.extract_text),
            ("Extract Images", "Extract embedded images", "#00BCD4", self.extract_images),
            ("Extract Tables", "Extract tabular data", "#009688", self.extract_tables),
            ("Extract Links", "Extract hyperlinks and URLs", "#3F51B5", self.extract_links),
            ("Extract Metadata", "Extract document metadata", "#673AB7", self.extract_metadata),
            ("Batch Extract", "Extract multiple types at once", "#FF5722", self.extract_batch)
        ]
        
        grid_layout = QGridLayout()
        for i, (name, desc, color, func) in enumerate(tools):
            btn = self.create_tool_button(name, desc, color, func)
            grid_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(grid_layout)
        return tab
```

### 5. Batch Processing Integration (`batch_processor.py` updates)

#### Extraction Batch Processing

```python
class BatchProcessor(QObject):
    """Updated batch processor with extraction operations support"""
    
    def create_extraction_batch_job(self, extraction_types: List[str], input_files: List[str],
                                   output_dir: str, options: Dict[str, Any] = None,
                                   priority: BatchJobPriority = BatchJobPriority.NORMAL) -> str:
        """Create a batch job for PDF extraction operations"""
        
    def _process_extraction_item(self, job: BatchJob, item: BatchJobItem) -> bool:
        """Process a single extraction item in a batch job"""
        try:
            extraction_engine = PDFExtractionEngine()
            extraction_type = job.operation_type
            
            # Route to appropriate extraction method
            if extraction_type == "extract_images":
                result = extraction_engine.extract_images(
                    item.input_file, item.output_file, item.parameters
                )
            elif extraction_type == "extract_links":
                result = extraction_engine.extract_links(
                    item.input_file, item.output_file, item.parameters
                )
            elif extraction_type == "extract_metadata":
                result = extraction_engine.extract_metadata(
                    item.input_file, item.parameters
                )
            elif extraction_type == "extract_tables":
                result = extraction_engine.extract_tables(
                    item.input_file, item.output_file, item.parameters
                )
            elif extraction_type == "extract_text":
                result = extraction_engine.extract_text(
                    item.input_file, item.output_file, item.parameters
                )
            else:
                raise ValueError(f"Unknown extraction type: {extraction_type}")
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Error processing extraction item {item.input_file}: {e}")
            return False
```

## 🧪 Testing Framework (`test_pdf_extraction_implementation.py`)

### Test Suite Structure (mirroring Phase 2.1)

```python
class PDFExtractionTestSuite:
    """
    Comprehensive test suite for PDF extraction implementation.
    Mirrors the structure and patterns of PDFFunctionalTestSuite from Phase 2.1.
    """
    
    def __init__(self):
        self.test_results = {}
        self.test_files = self._create_test_files()
        self.logger = setup_logger(__name__)
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Execute complete test suite"""
        tests = [
            ("PDF Extraction Engine", self.test_pdf_extraction_engine),
            ("Extract Images Operation", self.test_extract_images_operation),
            ("Extract Links Operation", self.test_extract_links_operation),
            ("Extract Metadata Operation", self.test_extract_metadata_operation),
            ("Extract Tables Operation", self.test_extract_tables_operation),
            ("Extract Text Operation", self.test_extract_text_operation),
            ("Batch Extraction Operation", self.test_batch_extraction_operation),
            ("Extraction Dialog Creation", self.test_extraction_dialog_creation),
            ("Widget Integration", self.test_widget_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "PASS" if result else "FAIL"
                self.logger.info(f"{test_name}: {status}")
            except Exception as e:
                self.test_results[test_name] = False
                self.logger.error(f"{test_name}: FAIL - {e}")
        
        return self.test_results
    
    def test_pdf_extraction_engine(self) -> bool:
        """Test PDF extraction engine functionality"""
        
    def test_extract_images_operation(self) -> bool:
        """Test image extraction operation"""
        
    def test_extract_links_operation(self) -> bool:
        """Test link extraction operation"""
        
    def test_extract_metadata_operation(self) -> bool:
        """Test metadata extraction operation"""
        
    def test_extract_tables_operation(self) -> bool:
        """Test table extraction operation"""
        
    def test_extract_text_operation(self) -> bool:
        """Test text extraction operation"""
        
    def test_batch_extraction_operation(self) -> bool:
        """Test batch extraction operation"""
        
    def test_extraction_dialog_creation(self) -> bool:
        """Test extraction parameter dialog creation"""
        
    def test_widget_integration(self) -> bool:
        """Test enhanced widget integration"""
```

## 📊 Error Handling and Logging

### Error Handling Strategy (following Phase 2.1)

```python
class PDFExtractionErrorHandler:
    """Comprehensive error handling for PDF extraction operations"""
    
    error_recovery_strategies = {
        'FileNotFoundError': 'handle_file_not_found',
        'PermissionError': 'handle_permission_error',
        'PDFReadError': 'handle_pdf_read_error',
        'ExtractionError': 'handle_extraction_error',
        'DependencyError': 'handle_dependency_error',
        'MemoryError': 'handle_memory_error',
        'ImportError': 'handle_import_error'
    }
    
    def handle_extraction_error(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """Handle extraction-specific errors with recovery suggestions"""
        
    def suggest_recovery_actions(self, error_type: str, context: Dict) -> List[str]:
        """Suggest recovery actions based on error type and context"""
```

### Logging Configuration

```python
# Extraction-specific logging configuration
EXTRACTION_LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'extraction_formatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [EXTRACTION] %(message)s'
        }
    },
    'handlers': {
        'extraction_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'pdf_extraction.log',
            'formatter': 'extraction_formatter'
        }
    },
    'loggers': {
        'pdf_extraction': {
            'handlers': ['extraction_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
```

## 🔧 Configuration Management

### Extraction Configuration (following RFU hub patterns)

```python
# Default extraction configuration
EXTRACTION_CONFIG = {
    'image_extraction': {
        'default_min_width': 100,
        'default_min_height': 100,
        'default_format': 'png',
        'default_quality': 95,
        'supported_formats': ['png', 'jpg', 'bmp', 'tiff']
    },
    'link_extraction': {
        'default_output_format': 'txt',
        'validate_urls_default': False,
        'include_internal_default': True,
        'include_external_default': True
    },
    'metadata_extraction': {
        'default_date_format': 'ISO',
        'default_output_format': 'txt',
        'filter_empty_default': True
    },
    'table_extraction': {
        'default_flavor': 'lattice',
        'default_line_scale': 15,
        'default_edge_tol': 50,
        'default_row_tol': 2,
        'default_column_tol': 2
    },
    'text_extraction': {
        'default_preserve_layout': True,
        'default_include_page_numbers': True,
        'default_encoding': 'utf-8',
        'default_output_format': 'txt'
    },
    'batch_extraction': {
        'max_concurrent_extractions': 3,
        'default_output_organization': 'by_type',
        'progress_update_interval': 100
    }
}
```

## 🚀 Performance Optimization

### Memory Management

```python
class ExtractionMemoryManager:
    """Memory management for extraction operations"""
    
    def __init__(self):
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.cleanup_interval = 60  # seconds
    
    def monitor_memory_usage(self):
        """Monitor memory usage during extraction operations"""
        
    def cleanup_extraction_cache(self):
        """Clean up extraction operation cache"""
        
    def optimize_large_file_processing(self, file_size: int):
        """Optimize processing for large PDF files"""
```

### Caching Strategy

```python
class ExtractionCacheManager:
    """Cache management for extraction operations"""
    
    def __init__(self):
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'rfu_extraction_cache')
        self.max_cache_size = 1024 * 1024 * 1024  # 1GB
    
    def cache_extraction_result(self, file_hash: str, extraction_type: str, result: Any):
        """Cache extraction result for reuse"""
        
    def get_cached_result(self, file_hash: str, extraction_type: str) -> Optional[Any]:
        """Retrieve cached extraction result"""
        
    def cleanup_cache(self):
        """Clean up old cache entries"""
```

---

**🎯 This technical specification provides the detailed implementation blueprint for Phase 2.2, ensuring exact adherence to Phase 2.1 patterns while delivering comprehensive PDF extraction capabilities integrated seamlessly into the RFU hub infrastructure.**