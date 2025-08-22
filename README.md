# Richard's File Utilities

A comprehensive Python GUI application for file management, analysis, and operations built with PyQt5.

## Project Structure

This project has been reorganized for better maintainability and scalability:

```
Richards_File_Utilities/
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Test configuration
├── .gitignore                      # Git ignore rules
├── Richards_Rile_Utilities.code-workspace  # VS Code workspace
├── README.md                       # This file
│
├── src/                            # All source code
│   ├── rfu/                        # Main application package
│   │   ├── __init__.py
│   │   ├── main.py                 # Application entry point
│   │   ├── hub.py                  # Main hub functionality
│   │   ├── core/                   # Core system components
│   │   │   ├── __init__.py
│   │   │   ├── config_manager.py
│   │   │   ├── log_manager.py
│   │   │   └── file_ops/           # File operation utilities
│   │   ├── gui/                    # GUI components
│   │   │   ├── __init__.py
│   │   │   ├── common/             # Shared GUI components
│   │   │   ├── dialogs/            # Dialog windows
│   │   │   ├── widgets/            # Custom widgets
│   │   │   └── windows/            # Main windows
│   │   └── tools/                  # Individual tool modules
│   │       ├── __init__.py
│   │       ├── file_management/    # File management tools
│   │       │   ├── __init__.py
│   │       │   ├── catalog.py
│   │       │   ├── file_finder.py
│   │       │   ├── organize.py
│   │       │   └── rename.py
│   │       ├── file_operations/    # File operation tools
│   │       │   ├── __init__.py
│   │       │   ├── cmsd.py
│   │       │   ├── compress_decompress.py
│   │       │   ├── file_splitter_joiner.py
│   │       │   └── sync.py
│   │       ├── analysis/           # Analysis tools
│   │       │   ├── __init__.py
│   │       │   └── empty_folders.py
│   │       ├── metadata/           # Metadata tools
│   │       │   ├── __init__.py
│   │       │   ├── edit_image_metadata.py
│   │       │   ├── file_touch.py
│   │       │   └── office_meta_data_editor.py
│   │       └── pdf/                # PDF tools
│   │           ├── __init__.py
│   │           ├── engines/        # PDF processing engines
│   │           │   ├── __init__.py
│   │           │   ├── analysis_engine.py
│   │           │   ├── conversion_engine.py
│   │           │   ├── enhancement_engine.py
│   │           │   ├── extraction_engine.py
│   │           │   ├── operation_engine.py
│   │           │   └── security_engine.py
│   │           ├── dialogs/        # PDF parameter dialogs
│   │           │   ├── __init__.py
│   │           │   ├── extraction_parameter_dialogs.py
│   │           │   ├── parameter_dialogs.py
│   │           │   └── security_parameter_dialogs.py
│   │           └── widgets/        # PDF widgets
│   │               ├── __init__.py
│   │               └── enhanced_pdf_tools_widget.py
│   └── utilities/                  # Existing utilities (preserved structure)
│
├── assets/                         # Static assets
│   ├── ui/                        # UI definition files
│   │   ├── catalog.ui
│   │   ├── compress_decompress.ui
│   │   ├── empty_folders.ui
│   │   ├── file_finder.ui
│   │   ├── file_touch.ui
│   │   └── organize.ui
│   ├── images/                    # Image assets
│   │   ├── screenshots/
│   │   └── test_signature.png
│   └── icons/                     # Application icons
│
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── default_settings.json
│   └── tool_configurations/
│
├── docs/                          # Documentation
│   ├── README.md                  # Main documentation
│   ├── user_guide/               # User documentation
│   ├── developer/                # Developer documentation
│   ├── api/                      # API documentation
│   ├── migration/                # Migration guides
│   ├── reports/                  # Status and progress reports
│   └── changelog/                # Version history
│
├── tests/                         # Test files
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── fixtures/                 # Test fixtures and data
│   └── test_*.py                 # All test files
│
├── scripts/                       # Utility and maintenance scripts
│   ├── __init__.py
│   ├── development/              # Development tools
│   │   ├── analyze_deps.py
│   │   ├── check_venv.py
│   │   ├── comprehensive_test_suite.py
│   │   └── verify_integration.py
│   ├── maintenance/              # Maintenance scripts
│   │   ├── automated_tool_corrector.py
│   │   ├── diagnostic_repair_script.py
│   │   ├── system_cleanup_diagnostic.py
│   │   └── organize_src_folder.py
│   ├── integration/              # Integration scripts
│   │   ├── integrate_tools.py
│   │   ├── integration_cleanup_script.py
│   │   ├── quick_integrate.py
│   │   └── enhanced_pdf_tools_integration.py
│   ├── tools/                    # Tool creation scripts
│   │   ├── create_simple_tools.py
│   │   └── launch_system_diagnostics.py
│   └── deployment/               # Deployment scripts
│
├── data/                          # Data files and logs
│   ├── logs/                     # Log files
│   ├── cache/                    # Cache files
│   ├── temp/                     # Temporary files
│   └── exports/                  # Export data
│
├── build/                         # Build outputs (created when needed)
├── dist/                          # Distribution files (created when needed)
│
├── archive/                       # Existing archive (preserved)
├── backups/                       # Existing backups (preserved)
├── core/                          # Existing core (preserved)
├── gui/                           # Existing gui (preserved)
├── resources/                     # Existing resources (preserved)
├── rfuvenv/                       # Python virtual environment (preserved)
├── src_backup/                    # Existing backup (preserved)
├── .github/                       # GitHub workflows (preserved)
└── .roo/                          # Roo configuration (preserved)
```

## Features

### File Management Tools
- **File Finder**: Search and find files based on various criteria
- **Catalog Files**: Create and manage file catalogs
- **Rename Files**: Batch rename files and folders
- **Organize Files**: Automatically organize files by type/date

### File Operations Tools
- **Copy/Move/Sync/Delete**: Advanced file operations
- **Compress/Decompress**: Archive and extract files
- **Split/Join Files**: Split large files or join parts
- **Synchronize**: Synchronize directories

### Analysis Tools
- **Size Analyzer**: Analyze disk space usage
- **Duplicate Finder**: Find and remove duplicate files
- **File Checksum**: Calculate and verify checksums
- **Empty Folders**: Find and clean empty folders

### Security Tools
- **Encrypt/Decrypt**: Secure file encryption and decryption
- **Secure Delete**: Permanently delete sensitive files
- **Permissions Editor**: Manage file and folder permissions

### Metadata Tools
- **Edit Image Metadata**: View and edit image metadata
- **Office Metadata Editor**: Edit document metadata
- **File Touch**: Modify file timestamps

### PDF Tools
- **Comprehensive PDF Suite**: Analysis, conversion, enhancement, extraction, operations, and security
- **Enhanced PDF Widget**: Tabbed interface for all PDF operations

### Network Tools
- **Network Connectivity**: Check network connectivity and diagnostics
- **Network Scanner**: Scan network for devices and services

### Privacy Tools
- **Privacy Cleaner**: Clean privacy-sensitive data
- **Data Anonymizer**: Anonymize sensitive file data

### System Tools
- **System Diagnostics**: Run system diagnostics and monitoring
- **System Cleanup**: Clean system temporary files
- **Software Maintenance**: Maintain and update software

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Richards_File_Utilities
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv rfuvenv
   # On Windows:
   rfuvenv\Scripts\activate
   # On Linux/Mac:
   source rfuvenv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Development

#### Running Tests
```bash
pytest
```

#### Development Scripts
- **Analyze Dependencies**: `python scripts/development/analyze_deps.py`
- **Check Virtual Environment**: `python scripts/development/check_venv.py`
- **Comprehensive Test Suite**: `python scripts/development/comprehensive_test_suite.py`
- **Verify Integration**: `python scripts/development/verify_integration.py`

#### Maintenance Scripts
- **Automated Tool Corrector**: `python scripts/maintenance/automated_tool_corrector.py`
- **Diagnostic Repair**: `python scripts/maintenance/diagnostic_repair_script.py`
- **System Cleanup Diagnostic**: `python scripts/maintenance/system_cleanup_diagnostic.py`

## Architecture

### Import Structure
The application uses a hierarchical import structure:
- `src.utilities.file_management.*` - File management tools
- `src.rfu.tools.file_operations.*` - File operation tools
- `src.rfu.tools.analysis.*` - Analysis tools
- `src.rfu.tools.metadata.*` - Metadata tools
- `src.rfu.tools.pdf.*` - PDF tools and engines
- `src.rfu.gui.*` - GUI components
- `src.rfu.core.*` - Core system components

### Tool Integration
Each tool is designed as a modular component that can be:
- Launched independently
- Integrated into the main hub
- Tested in isolation
- Extended with additional functionality

## Contributing

1. Follow the established directory structure
2. Add new tools to appropriate categories in `src/rfu/tools/`
3. Update import paths in `main.py` for new tools
4. Add tests in the `tests/` directory
5. Update documentation as needed

## Requirements

- Python 3.7+
- PyQt5
- See `requirements.txt` for complete list

## License

[Add your license information here]

## Version History

See `docs/changelog/` for detailed version history and changes.

---

**Note**: This project has been comprehensively reorganized for better maintainability, scalability, and developer experience. All functionality has been preserved while improving the overall structure and reducing root directory clutter.