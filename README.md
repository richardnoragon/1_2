# Richard's File Utilities (RFU) Hub

## Overview
A comprehensive file management suite with multiple tools for file operations, analysis, and metadata management.

## Main Components

### 1. File Management Tools
- **File Catalog Generator** (`catalog.py`)
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

- **Encryption** (`en_and_decrypt.py`)
  - File encryption and decryption capabilities

### 5. Metadata Management
- **Office Metadata Editor** (`office_meta_data_editor.py`)
  - Edit metadata of Office documents
  - Supports various Office file formats

- **Tag Viewer/Editor** (`tag_viewer_editor.py`)
  - View and edit audio/video file tags

### 6. System Integration
- **Permissions Editor** (`permissions_editor.py`)
  - Modify file permissions
  - Access control management

## Technical Details
- Built with Python and PyQt5
- Uses Qt Designer UI files (.ui) for interface layouts
- Comprehensive test suite available in tests directory
- Modular architecture with separate modules for each tool

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
