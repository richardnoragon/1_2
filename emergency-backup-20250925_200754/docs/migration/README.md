# Richard's File Utilities (RFU) Hub

## Overview
A comprehensive file management suite with multiple tools for file operations, analysis, and metadata management.

## Main Components

### 1. File Management Tools
- **File Catalog Generator** (`file_utilities_1/catalog.py`)
  - Creates HTML catalogs of directory contents
  - Features:
    - Recursive directory scanning
    - File size and modification date display
    - Duplicate file identification
    - Sorting options by name, file type, etc.

- **File Finder** (`file_finder.py`)
  - Advanced file search utility
  - Features:
    - Date-based filtering (creation/modification)
    - File type filtering
    - Metadata search capabilities

### 2. Organization Tools
- **File Organizer** (`organize.py`)
  - Helps organize files in directories
  - Supports recursive operations

- **File Renamer** (`rename.py`)
  - Batch file renaming capabilities
  - Features:
    - Prefix/suffix addition/removal
    - Case conversion
    - Date-based naming
    - Pattern-based renaming

### 3. File Analysis
- **Size Analyzer** (`size_analyzer.py`)
  - Analyzes directory and file sizes
  - Visual representation of storage usage

- **Duplicate Finder** (`find_duplicate_files.py`)
  - Identifies duplicate files in directories

### 4. File Operations
- **Sync Tool** (`sync.py`)
  - Directory synchronization utility
  - Compare and sync file changes

- **Compression Tools** (`compress_decompress.py`)
  - File compression and decompression

- **Encryption** (`file_utilities_2/gui/encryption_gui.py`)
  - Advanced file encryption and decryption capabilities
  - Features:
    - Fernet-based symmetric encryption
    - File and directory batch processing
    - Real-time progress tracking with cancellation support
    - Comprehensive audit trails and logging
    - Hub integration with resource coordination
    - Persistent configuration management
    - Modern StandardWindow-based interface

### 5. Metadata Management
- **Office Metadata Editor** (`office_meta_data_editor.py`)
  - Edit metadata of Office documents
  - Supports various Office file formats

- **Tag Viewer/Editor** (`tag_viewer_editor.py`)
  - View and edit audio/video file tags

### 6. PDF Tools Suite
- **PDF Processing Hub** (`pdf_utilities/main.py`)
  - Comprehensive PDF utilities integrated into RFU Hub
  - Access via "PDF Tools" button in main interface
  - 23 specialized PDF processing modules

#### PDF Basic Operations
- **PDF Splitting** (`pdf_utilities/split.py`) - Split PDFs by pages or ranges
- **PDF Merging** (`pdf_utilities/merg.py`) - Combine multiple PDFs into one
- **PDF Viewing** (`pdf_utilities/view.py`) - View and navigate PDF documents
- **Page Administration** (`pdf_utilities/page_administration.py`) - Advanced page management

#### PDF Content Extraction
- **Text Extraction** (`pdf_utilities/extract_text.py`) - Extract text content from PDFs
- **Image Extraction** (`pdf_utilities/extract_image_cli.py`) - Extract images from PDFs
- **Table Extraction** (`pdf_utilities/extract_tables_camelot.py`) - Extract tables using Camelot
- **Link Extraction** (`pdf_utilities/extract_links.py`) - Extract hyperlinks from PDFs
- **Metadata Extraction** (`pdf_utilities/extract_metadata.py`) - Extract document metadata

#### PDF Enhancement Tools
- **OCR Processing** (`pdf_utilities/ocr.py`) - Optical Character Recognition for scanned PDFs
- **Watermarking** (`pdf_utilities/watermark.py`) - Add text/image watermarks to PDFs
- **Text Highlighting** (`pdf_utilities/highlight.py`) - Highlight text in PDF documents

#### PDF Conversion Tools
- **DOCX Conversion** (`pdf_utilities/convert_to_docx.py`) - Convert PDFs to Word format
- **Image Conversion** (`pdf_utilities/convert_to_image.py`) - Convert PDF pages to images
- **HTML to PDF** (`pdf_utilities/convert_html_to_pdf.py`) - Convert HTML content to PDF

#### PDF Security Tools
- **PDF Encryption** (`pdf_utilities/encrypt.py`) - Encrypt and decrypt PDF documents
- **Digital Signing** (`pdf_utilities/sign.py`) - Add digital signatures to PDFs

#### PDF Administration
- **Settings Manager** (`pdf_utilities/settings_manager.py`) - Configure PDF tool preferences
- **Log Manager** (`pdf_utilities/log_manager.py`) - View and manage PDF processing logs
- **PDF Miner** (`pdf_utilities/miner.py`) - Advanced PDF analysis and data mining

### 7. System Integration
- **Permissions Editor** (`permissions_editor.py`)
  - Modify file permissions
  - Access control management

## Technical Details
- Built with Python and PyQt5
- Uses Qt Designer UI files (.ui) for interface layouts
- Comprehensive test suite available in tests directory
- Modular architecture with separate modules for each tool
- **PDF Tools Integration**: Bridge architecture connecting PDF utilities with main RFU systems
  - Unified configuration management via `core/config_manager.py`
  - Centralized logging through `core/logging_manager.py`
  - Consistent UI theming using `gui/common/base_window.py`
  - Error handling integration with main application systems

## Getting Started

### Installation
1. Clone the repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python main.py
   ```

### Using PDF Tools
1. **Access PDF Tools**: Click the "PDF Tools" button in the main RFU Hub interface
2. **Select Operation**: Choose from 23 available PDF utilities organized by category
3. **Process Files**: Use drag-and-drop or file selection for PDF operations
4. **View Results**: Check output directories and review operation logs

### PDF Tools Quick Start
- **Text Extraction**: Drop a PDF file → Select "Extract Text" → Choose output format
- **PDF Splitting**: Open Split tool → Select PDF → Choose split method → Process
- **PDF Merging**: Open Merge tool → Add multiple PDFs → Arrange order → Merge
- **OCR Processing**: Select OCR tool → Choose language → Process scanned PDFs

For detailed PDF Tools usage, see [`PDF_TOOLS_USER_GUIDE.md`](PDF_TOOLS_USER_GUIDE.md)

### Troubleshooting
If you encounter issues with PDF Tools integration, refer to [`PDF_TOOLS_TROUBLESHOOTING.md`](PDF_TOOLS_TROUBLESHOOTING.md)

## Testing
Test files are organized in the tests directory:
- `test_utils.py`: Utility test functions
- `test_file_operations.py`: File operation tests
- `test_gui_components.py`: GUI testing
- `test_encryption.py`: Encryption feature tests

RFU includes a comprehensive test suite that covers unit tests, integration tests, and GUI tests. The test suite is built using pytest and includes tools for measuring code coverage and automating test execution.

### Quick Start

Run all tests:
```bash
python run_tests.py
```

Run with coverage report:
```bash
python run_tests.py --coverage
```

Skip GUI tests (useful for CI environments):
```bash
python run_tests.py --no-gui
```

Run tests in parallel:
```bash
python run_tests.py --parallel
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **GUI Tests**: Test user interface components
- **Functional Tests**: Test complete user workflows

### Test Markers

Use pytest markers to categorize tests:
```python
@pytest.mark.gui  # GUI tests
@pytest.mark.slow  # Time-consuming tests
@pytest.mark.integration  # Integration tests
```

### Running Specific Tests

Run only unit tests:
```bash
pytest -v -m "not gui and not integration and not slow"
```

Run only GUI tests:
```bash
pytest -v -m "gui"
```

Run only integration tests:
```bash
pytest -v -m "integration"
```

### Continuous Integration

Tests are automatically run on:
- Every push to main branch
- Every pull request
- Daily scheduled runs

The CI pipeline runs on:
- Ubuntu Linux
- Windows
- macOS

### Contributing Tests

1. Create test files in the `tests/` directory
2. Follow the existing test patterns
3. Include docstrings and comments
4. Add appropriate markers
5. Update test documentation if needed

### Code Coverage

Coverage reports are generated in HTML format. Open `htmlcov/index.html` to view the report after running tests with coverage.
