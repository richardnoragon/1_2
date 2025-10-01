# Richard's File Utilities - Technology Stack

**Last Updated:** September 26, 2025
**Tech Stack Version:** 3.1.0
**Environment:** Python 3.7+ with PyQt5 and Dual Interface System

---

## Core Technology Stack

### Primary Development Technologies

#### Programming Language

- **Python 3.7+**: Primary development language
  - **Rationale**: Cross-platform compatibility, rich ecosystem, rapid development
  - **Version Requirements**: 3.7+ for compatibility with PyQt5 and modern libraries
  - **Performance**: Adequate for file operations with C extensions for heavy lifting

#### GUI Framework

- **PyQt5 5.15.11**: Cross-platform desktop GUI framework
  - **Components Used**: QtWidgets, QtCore, QtGui
  - **Architecture**: Event-driven with signal/slot pattern with dual interface support
  - **Interface Modes**: Dialog hub (tabbed) and multi-pane explorer
  - **Customization**: Extensive CSS-like styling capabilities
  - **Integration**: Native OS integration for file operations

#### Database System

- **SQLite 3.35+**: Embedded relational database
  - **Use Cases**: Configuration storage, tool usage tracking, interface preferences
  - **Features**: ACID compliance, concurrent access, migration state tracking
  - **Performance**: Optimized for read-heavy workloads with indexing
  - **Integration**: Standalone database manager with fallback handling

---

## Development Environment Setup

### Prerequisites Installation

#### Python Environment Setup

```bash
# Verify Python version
python --version  # Must be 3.7+

# Create virtual environment
python -m venv rfu_env

# Activate virtual environment
# Windows:
rfu_env\Scripts\activate
# Linux/macOS:
source rfu_env/bin/activate
```

#### Dependency Installation

```bash
# Install all required packages
pip install -r requirements.txt

# Verify PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"

# Verify core modules
python -c "import src.rfu.core; print('Core modules validated')"
```

### Development Tools Configuration

#### IDE Setup (VS Code Recommended)

```json
{
  "python.defaultInterpreterPath": "./rfu_env/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "./rfu_env/Scripts/pytest",
  "files.associations": {
    "*.ui": "xml"
  }
}
```

#### Testing Environment

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run E2E tests only
pytest tests/e2e/ -v

# Run specific test suite
pytest tests/e2e/test_file_finder_e2e.py -v
```

---

## Dependencies Architecture

### Core Dependencies (79 total packages)

#### GUI and Application Framework

```python
# Essential GUI Dependencies (from requirements.txt)
{
    "PyQt5": "5.15.11",           # Main GUI framework
    "PyQt5-Qt5": "5.15.2",       # Qt runtime
    "PyQt5_sip": "12.17.0"       # Python-Qt bridge
}
```

#### Testing Infrastructure

```python
# Comprehensive Testing Stack
{
    "pytest": "8.3.5",              # Core testing framework
    "pytest-qt": "4.4.0",           # PyQt5 testing support
    "pytest-cov": "6.1.0",          # Coverage reporting
    "pytest-timeout": "2.3.1",      # Test timeout protection
    "pytest-randomly": "3.16.0",    # Test order randomization
    "pytest-xvfb": "3.1.1",         # GUI testing on Linux
    "pytest-asyncio": "0.26.0"      # Async testing support
}
```

#### Security and Cryptography

```python
# Security Stack
{
    "cryptography": "44.0.2",       # Modern cryptographic library
    "pyAesCrypt": "6.1.1",         # AES file encryption
    "pycryptodomex": "3.22.0",     # Additional crypto algorithms
    "pyOpenSSL": "25.0.0"          # SSL/TLS support
}
```

#### File and Data Processing

```python
# File Processing Dependencies
{
    "pandas": "2.2.3",             # Data analysis and manipulation
    "Pillow": "11.1.0",            # Image processing and metadata
    "PyMuPDF": "1.25.4",          # PDF processing
    "python-docx": "1.1.2",       # Word document processing
    "openpyxl": "3.1.5",          # Excel file processing
    "PyPDF2": "3.0.1",            # PDF manipulation
    "PyPDF4": "1.27.0",           # Additional PDF support
    "pikepdf": "9.5.2"            # PDF processing library
}
```

#### Compression and Archive Handling

```python
# Archive Processing Stack
{
    "py7zr": "1.0.0",             # 7-Zip format support
    "pyzstd": "0.16.2",           # Zstandard compression
    "multivolumefile": "0.2.3",   # Multi-volume archive support
    "Brotli": "1.1.0",            # Brotli compression
    "inflate64": "1.0.1"          # Enhanced ZIP support
}
```

#### System Integration and Monitoring

```python
# System Integration Stack
{
    "psutil": "7.0.0",            # System and process monitoring
    "watchdog": "6.0.0",          # File system event monitoring
    "Send2Trash": "1.8.3",        # Safe file deletion
    "python-magic": "0.4.27",     # File type detection
    "pytesseract": "0.3.13"       # OCR functionality
}
```

#### Development and Quality Assurance

```python
# Development Tools
{
    "black": "25.1.0",            # Code formatting
    "flake8": "7.2.0",            # Linting and style checking
    "mypy": "1.15.0",             # Static type checking
    "coverage": "7.8.0",          # Code coverage analysis
    "setuptools": "68.2.2",       # Package management
    "wheel": "0.41.2"             # Distribution building
}
```

#### Additional Specialized Dependencies

```python
# Specialized Libraries
{
    "opencv-python-headless": "4.11.0.86",  # Computer vision
    "numpy": "2.2.4",                       # Numerical computing
    "lxml": "5.3.1",                        # XML processing
    "mutagen": "1.47.0",                     # Audio metadata
    "piexif": "1.1.3",                      # EXIF data handling
    "fire": "0.7.0",                        # CLI generation
    "termcolor": "2.5.0",                   # Colored terminal output
    "PyVirtualDisplay": "3.0"               # Virtual display for testing
}
```

---

## Technical Constraints and Limitations

### Platform Compatibility

#### Operating System Support

```python
# Platform Requirements
{
    "windows": {
        "versions": "Windows 10, Windows 11",
        "limitations": "Some network tools require elevated privileges",
        "file_systems": "NTFS primary, FAT32/exFAT supported"
    },
    "linux": {
        "distributions": "Ubuntu 20.04+, CentOS 8+, Fedora 35+",
        "limitations": "GUI requires X11 or Wayland",
        "file_systems": "ext4, XFS, Btrfs with ACL support"
    },
    "macos": {
        "versions": "macOS 10.15+",
        "limitations": "Code signing required for distribution",
        "file_systems": "APFS, HFS+ supported"
    }
}
```

#### Hardware Requirements

```python
# Minimum System Requirements
{
    "cpu": "Dual-core 2.0GHz (Recommended: Quad-core 3.0GHz+)",
    "memory": "4GB RAM (Recommended: 8GB+ for large datasets)",
    "storage": "2GB available space (Additional for processing large files)",
    "display": "1024x768 resolution (Recommended: 1920x1080+)",
    "network": "Optional for network tools and cloud features"
}
```

### Performance Constraints

#### Memory Usage Limits

- **Base Application**: < 100MB at startup
- **File Operations**: < 500MB for datasets up to 50,000 files
- **Large File Processing**: Streaming algorithms for files > 1GB
- **Memory Monitoring**: Automatic cleanup when usage > 2GB

#### Processing Limitations

```python
# Performance Boundaries
{
    "file_count_limits": {
        "optimal": "< 10,000 files for best performance",
        "good": "10,000 - 50,000 files with progress tracking",
        "maximum": "200,000+ files with streaming algorithms"
    },
    "file_size_limits": {
        "direct_processing": "< 1GB files loaded into memory",
        "streaming_processing": "1GB+ files processed in chunks",
        "maximum_tested": "100GB+ files with chunked processing"
    }
}
```

### Security Constraints

- **Encryption Standards**: AES-256-GCM minimum for all sensitive data
- **Key Management**: PBKDF2 key derivation with minimum 100,000 iterations
- **Audit Requirements**: All file operations must be logged
- **Access Controls**: Directory-level permissions enforcement

---

## Development Workflow and Tooling

### Version Control Configuration

#### Git Workflow

```bash
# Repository Configuration
git config --local core.autocrlf input
git config --local pull.rebase true
git config --local branch.autosetupmerge always

# Pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

#### Branch Protection

- **Main branch**: Protected with required reviews
- **Development workflow**: Feature branches with PR reviews
- **Release process**: Semantic versioning with automated tagging

### Code Quality Standards

#### Linting Configuration

```python
# flake8 configuration (.flake8)
{
    "max-line-length": 88,
    "extend-ignore": ["E203", "W503"],
    "exclude": [".git", "__pycache__", "build", "dist"],
    "per-file-ignores": {
        "__init__.py": "F401"
    }
}
```

#### Type Checking

```python
# mypy configuration (mypy.ini)
{
    "python_version": "3.7",
    "warn_return_any": true,
    "warn_unused_configs": true,
    "disallow_untyped_defs": true,
    "ignore_missing_imports": true
}
```

#### Code Formatting

```python
# black configuration (pyproject.toml)
{
    "line-length": 88,
    "target-version": ["py37", "py38", "py39"],
    "include": "\\.pyi?$",
    "exclude": "/(build|dist|venv)/"
}
```

---

## Testing Framework Configuration

### Pytest Configuration

**File:** [`pytest.ini`](pytest.ini) - Comprehensive testing setup

```ini
# Core Testing Configuration
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test markers
markers =
    gui: GUI component tests
    integration: Integration tests
    slow: Tests that take longer to run
    unit: Unit tests
    functional: Functional tests
    error: Error handling tests
    performance: Performance tests
```

### E2E Testing Infrastructure

#### Mock Framework Architecture

```python
# E2E Test Utilities Structure
{
    "base_classes": {
        "MockFileManagementTool": "Base mock for all file management tools",
        "FileManagementTestDataFactory": "Test data generation",
        "FileManagementPerformanceMonitor": "Performance validation"
    },
    "test_data_management": {
        "small_dataset": "100 files, 50MB, depth 3",
        "medium_dataset": "5,000 files, 500MB, depth 5",
        "large_dataset": "50,000 files, 5GB, depth 8",
        "enterprise_dataset": "200,000 files, 20GB, depth 12"
    }
}
```

#### Performance Testing Configuration

```python
# Performance Benchmark Configuration
{
    "targets": {
        "file_finder_text_search": "< 15 seconds for 10,000 files",
        "catalog_html_generation": "< 30 seconds for 5,000 files",
        "batch_rename_operations": "< 20 seconds for 2,000 files",
        "rule_based_organization": "< 35 seconds for 3,000 files"
    },
    "memory_limits": {
        "file_finder": "< 100MB peak usage",
        "catalog_generation": "< 150MB peak usage",
        "batch_operations": "< 50MB peak usage"
    }
}
```

---

## Deployment and Packaging

### Build System Configuration

#### PyInstaller Configuration

```python
# Executable Build Configuration
{
    "build_command": "pyinstaller --onefile --windowed main.py",
    "additional_data": [
        "--add-data 'assets;assets'",
        "--add-data 'config;config'",
        "--add-data 'src;src'"
    ],
    "hidden_imports": [
        "src.rfu.core",
        "src.tools.file_management",
        "PyQt5.sip"
    ],
    "exclude_modules": ["matplotlib", "numpy.testing"]
}
```

#### Distribution Packaging

```python
# Platform-Specific Packaging
{
    "windows": {
        "msi_installer": "cx_Freeze with WiX toolset",
        "portable_exe": "PyInstaller with --onefile",
        "requirements": "Windows 10+ with Visual C++ Redistributable"
    },
    "linux": {
        "deb_package": "stdeb with proper dependencies",
        "rpm_package": "bdist_rpm with spec file",
        "appimage": "Standalone portable application"
    },
    "macos": {
        "app_bundle": "py2app with proper signing",
        "dmg_installer": "create-dmg with background image",
        "homebrew_formula": "Formula for package manager"
    }
}
```

### Dependency Management

#### Virtual Environment Best Practices

```bash
# Virtual Environment Setup
python -m venv rfu_env
source rfu_env/bin/activate  # Linux/macOS
rfu_env\Scripts\activate     # Windows

# Dependency management
pip install -r requirements.txt
pip freeze > requirements-lock.txt  # Pin exact versions

# Development dependencies
pip install -r requirements-dev.txt  # Additional dev tools
```

#### Dependency Security

```python
# Security Scanning Configuration
{
    "tools": {
        "safety": "pip install safety; safety check",
        "bandit": "pip install bandit; bandit -r src/",
        "pip_audit": "pip install pip-audit; pip-audit"
    },
    "schedule": "Weekly dependency security scans",
    "automation": "GitHub Dependabot for automated updates"
}
```

---

## Configuration Management

### Environment Configuration

#### Configuration File Structure

```json
{
  "development": {
    "database_path": "dev.db",
    "logging_level": "DEBUG",
    "security_mode": "permissive",
    "performance_monitoring": true
  },
  "testing": {
    "database_path": ":memory:",
    "logging_level": "INFO",
    "security_mode": "strict",
    "mock_external_services": true
  },
  "production": {
    "database_path": "rfu_production.db",
    "logging_level": "WARNING",
    "security_mode": "enterprise",
    "audit_all_operations": true
  }
}
```

#### Environment Variables

```bash
# Development Environment Variables
export RFU_ENV=development
export RFU_DEBUG=1
export RFU_LOG_LEVEL=DEBUG
export RFU_ENABLE_PROFILING=1

# Testing Environment
export RFU_ENV=testing
export RFU_TEST_DATA_DIR=./test_data
export RFU_MOCK_MODE=1

# Production Environment
export RFU_ENV=production
export RFU_LOG_LEVEL=WARNING
export RFU_AUDIT_MODE=1
```

### Configuration Manager Integration

**File:** [`src/config_manager.py`](src/config_manager.py) - Configuration management with JSON persistence

**Key Features:**

- **Singleton Pattern**: Single configuration instance across application
- **Hierarchical Settings**: Nested configuration sections for organization
- **Atomic Updates**: UPSERT operations prevent race conditions
- **Backup/Restore**: Automatic backup before configuration changes
- **Profile Management**: User-defined configuration profiles

---

## Security Technology Implementation

### Encryption Technology Stack

#### Cryptographic Libraries

```python
# Security Technology Stack
{
    "primary_crypto": "cryptography==44.0.2",
    "file_encryption": "pyAesCrypt==6.1.1",
    "additional_algorithms": "pycryptodomex==3.22.0",
    "ssl_support": "pyOpenSSL==25.0.0"
}
```

#### Encryption Implementation

```python
# AES-256-GCM Configuration
{
    "algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2-SHA256",
    "iterations": 100000,
    "salt_length": 16,
    "nonce_length": 12,
    "tag_length": 16
}
```

### Security Framework Architecture

**File:** [`src/rfu/gui/security_preferences_dialog.py`](src/rfu/gui/security_preferences_dialog.py) - 1,292 lines

**Implementation Features:**

- **6 Security Tabs**: Migration, Theme, Directory, Audit, Monitoring, Advanced
- **Real-time Status**: 5-second refresh cycle for component health
- **Emergency Protocols**: Lockdown and recovery procedures
- **Configuration Export/Import**: Backup and restore security settings

---

## Performance Optimization Technologies

### Memory Management

#### Optimization Strategies

```python
# Memory Optimization Techniques
{
    "streaming_io": {
        "library": "Built-in file operations with chunking",
        "chunk_size": "64KB - 1MB depending on operation",
        "use_cases": "Large file processing, directory scanning"
    },
    "garbage_collection": {
        "strategy": "Explicit gc.collect() after large operations",
        "monitoring": "psutil for real-time memory tracking",
        "thresholds": "Automatic cleanup at 80% memory usage"
    },
    "object_pools": {
        "implementation": "Reusable objects for frequent allocations",
        "use_cases": "File metadata objects, search result items",
        "benefits": "Reduced allocation overhead"
    }
}
```

#### Threading and Concurrency

```python
# Concurrency Architecture
{
    "thread_pools": {
        "io_operations": "ThreadPoolExecutor for file I/O",
        "cpu_operations": "ProcessPoolExecutor for CPU-intensive tasks",
        "max_workers": "min(32, cpu_count + 4) for optimal performance"
    },
    "gui_threading": {
        "pattern": "QThread for long-running operations",
        "signals": "Progress updates via pyqtSignal",
        "safety": "All GUI updates from main thread only"
    }
}
```

### Caching Implementation

```python
# Caching Strategy
{
    "memory_cache": {
        "implementation": "LRU cache with size limits",
        "use_cases": "File metadata, search results, configuration",
        "size_limits": "256MB default, configurable"
    },
    "disk_cache": {
        "implementation": "SQLite-based persistent cache",
        "use_cases": "Directory scans, file checksums, thumbnails",
        "cleanup": "Automatic cleanup of stale entries"
    }
}
```

---

## Integration Technologies

### Database Integration

#### SQLite Configuration

```python
# SQLite Optimization Settings
{
    "pragma_settings": {
        "journal_mode": "WAL",      # Write-Ahead Logging
        "synchronous": "NORMAL",    # Balance safety/performance
        "cache_size": "-64000",     # 64MB cache
        "temp_store": "MEMORY",     # Memory-based temp tables
        "foreign_keys": "ON"        # Referential integrity
    },
    "connection_pooling": {
        "max_connections": 10,
        "connection_timeout": 30,
        "retry_logic": "Exponential backoff"
    }
}
```

#### Migration System

```python
# Database Migration Architecture
{
    "migration_files": "src/rfu/core/migrations/",
    "versioning": "Sequential numbered migrations",
    "rollback": "Down migration support for all versions",
    "validation": "Schema integrity checks after migrations"
}
```

### External System Integration

#### File System Integration

```python
# Cross-Platform File Operations
{
    "path_handling": {
        "library": "pathlib.Path for cross-platform compatibility",
        "normalization": "Automatic path separator conversion",
        "encoding": "UTF-8 for all path operations"
    },
    "file_operations": {
        "windows": "os.startfile() for system integration",
        "linux": "xdg-open for desktop integration",
        "macos": "open command for Finder integration"
    },
    "permissions": {
        "unix": "os.chmod() with ACL support",
        "windows": "Windows ACL API through win32security"
    }
}
```

#### Network Integration

```python
# Network Technology Stack
{
    "protocols": ["HTTP/HTTPS", "FTP/SFTP", "SMB/CIFS"],
    "security": "TLS 1.3 minimum for all connections",
    "monitoring": "Built-in connectivity diagnostics",
    "transfer": "Resumable transfers with integrity checking"
}
```

---

## Tool Usage Patterns and Development Conventions

### Code Organization Patterns

#### Module Structure Convention

```python
# Standard Tool Module Structure
{
    "tool_module": {
        "imports": "Standard imports at top",
        "constants": "Tool-specific constants",
        "main_class": "Inherits from StandardWindow",
        "helper_methods": "Private methods with underscore prefix",
        "main_function": "Standalone execution support"
    }
}
```

#### Naming Conventions

```python
# Naming Standards
{
    "classes": "PascalCase (e.g., FileFinderGUI)",
    "methods": "snake_case (e.g., start_search)",
    "constants": "UPPER_SNAKE_CASE (e.g., DEFAULT_CHUNK_SIZE)",
    "files": "snake_case (e.g., file_finder.py)",
    "directories": "snake_case (e.g., file_management)"
}
```

### Error Handling Patterns

#### Exception Handling Strategy

```python
# Standardized Error Handling
{
    "pattern": "Try-catch with specific exception types",
    "logging": "Comprehensive error logging with context",
    "user_feedback": "User-friendly error messages",
    "recovery": "Automatic recovery where possible",
    "fallback": "Graceful degradation for non-critical failures"
}
```

#### Logging Configuration

```python
# Logging Architecture
{
    "levels": {
        "DEBUG": "Detailed diagnostic information",
        "INFO": "General operational messages",
        "WARNING": "Potential issues that don't stop operation",
        "ERROR": "Errors that affect specific operations",
        "CRITICAL": "Serious errors that may halt application"
    },
    "handlers": {
        "console": "Real-time output during development",
        "file": "Persistent logging to rfu_errors.log",
        "rotating": "Log rotation to prevent disk filling"
    }
}
```

---

## Automation and Maintenance Technologies

### Automated Tool Correction

**File:** [`scripts/maintenance/automated_tool_corrector.py`](scripts/maintenance/automated_tool_corrector.py) - 940 lines

**Technology Features:**

```python
# Automation Technology Stack
{
    "tool_generation": {
        "template_engine": "String templating with parameter substitution",
        "code_analysis": "AST parsing for existing tool analysis",
        "validation": "Import testing and integration verification"
    },
    "error_recovery": {
        "backup_system": "Automatic backup before modifications",
        "rollback": "Complete restoration from backup on failure",
        "validation": "Multi-stage validation before deployment"
    },
    "monitoring": {
        "status_tracking": "JSON-based progress and status tracking",
        "metrics": "Success rates, processing time, error patterns",
        "reporting": "Comprehensive correction session reports"
    }
}
```

### Development Automation

#### Build Automation

```python
# Build Pipeline Technologies
{
    "dependency_management": {
        "tool": "pip-tools for dependency resolution",
        "lock_files": "requirements-lock.txt for reproducible builds",
        "vulnerability_scanning": "safety check for known vulnerabilities"
    },
    "code_quality": {
        "formatting": "black for consistent code style",
        "linting": "flake8 for style and error checking",
        "type_checking": "mypy for static type validation"
    },
    "testing": {
        "unit_tests": "pytest with coverage reporting",
        "integration_tests": "pytest with mock frameworks",
        "e2e_tests": "pytest-qt for GUI testing"
    }
}
```

#### CI/CD Integration

```yaml
# GitHub Actions Configuration
{
  "triggers": ["push", "pull_request"],
  "jobs":
    {
      "test":
        {
          "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
          "python": ["3.7", "3.8", "3.9", "3.10"],
          "steps": ["setup", "install", "lint", "test", "coverage"],
        },
      "build":
        {
          "condition": "tags",
          "outputs": ["executable", "installer", "source_dist"],
        },
    },
}
```

---

## Future Technology Evolution

### Planned Technology Upgrades (2026-2027)

#### Framework Modernization

```python
# Technology Roadmap
{
    "gui_framework": {
        "current": "PyQt5 5.15.11",
        "future": "PyQt6 or PySide6 migration for better performance",
        "timeline": "Q2 2026",
        "benefits": "Improved performance, better theming, modern features"
    },
    "python_version": {
        "current": "3.7+ compatibility",
        "future": "3.10+ minimum for performance improvements",
        "timeline": "Q4 2025",
        "benefits": "Pattern matching, improved error messages, speed"
    }
}
```

#### Cloud Technology Integration

```python
# Cloud Integration Stack
{
    "storage_apis": {
        "aws_s3": "boto3 for S3 integration",
        "azure_blob": "azure-storage-blob for Azure",
        "google_cloud": "google-cloud-storage for GCS"
    },
    "authentication": {
        "oauth2": "authlib for cloud service authentication",
        "token_management": "Secure token storage and refresh"
    },
    "sync_technologies": {
        "conflict_resolution": "Advanced merge algorithms",
        "delta_sync": "Binary diff for efficient transfers",
        "encryption": "End-to-end encryption for cloud data"
    }
}
```

### Advanced Analytics Integration

```python
# Analytics Technology Stack
{
    "machine_learning": {
        "framework": "scikit-learn for pattern recognition",
        "use_cases": ["Smart file organization", "Usage prediction"],
        "data_processing": "pandas for feature engineering"
    },
    "visualization": {
        "charts": "matplotlib for analysis charts",
        "interactive": "plotly for interactive visualizations",
        "gui_integration": "PyQt5 chart widgets"
    }
}
```

---

## Development Environment Optimization

### IDE Configuration and Extensions

#### VS Code Recommended Extensions

```json
{
  "required_extensions": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-python.mypy-type-checker"
  ],
  "helpful_extensions": [
    "alefragnani.project-manager",
    "ms-vscode.test-adapter-converter",
    "ms-python.pytest"
  ]
}
```

#### Debugging Configuration

```json
{
  "configurations": [
    {
      "name": "RFU Main Application",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "env": {
        "RFU_DEBUG": "1",
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Run E2E Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/e2e/", "-v"]
    }
  ]
}
```

### Performance Profiling Tools

#### Profiling Configuration

```python
# Performance Profiling Stack
{
    "memory_profiling": {
        "tool": "memory_profiler",
        "usage": "@profile decorator on critical methods",
        "reporting": "Line-by-line memory usage analysis"
    },
    "execution_profiling": {
        "tool": "cProfile with pstats",
        "usage": "Full application profiling for optimization",
        "visualization": "snakeviz for profile visualization"
    },
    "gui_profiling": {
        "tool": "PyQt5 built-in profiling",
        "metrics": "Paint events, signal emissions, memory usage",
        "optimization": "Widget lifecycle and update optimization"
    }
}
```

---

## Maintenance and Monitoring Technologies

### System Monitoring

#### Performance Monitoring Stack

```python
# Monitoring Technology
{
    "system_metrics": {
        "library": "psutil==7.0.0",
        "metrics": ["CPU", "Memory", "Disk I/O", "Network"],
        "frequency": "Real-time for critical operations"
    },
    "application_metrics": {
        "implementation": "Custom metrics collection",
        "storage": "SQLite database with time-series data",
        "alerting": "Threshold-based alerts for performance degradation"
    }
}
```

#### Health Check Implementation

```python
# Health Monitoring Framework
{
    "database_health": {
        "check": "PRAGMA integrity_check",
        "frequency": "Startup and periodic validation",
        "recovery": "Automatic backup restoration"
    },
    "configuration_health": {
        "validation": "JSON schema validation",
        "corruption_detection": "Checksum verification",
        "recovery": "Default configuration restoration"
    },
    "security_health": {
        "encryption_status": "Key validation and algorithm verification",
        "access_control": "Permission and policy validation",
        "audit_integrity": "Log file integrity verification"
    }
}
```

### Automated Maintenance

#### Maintenance Automation Stack

```python
# Maintenance Technology
{
    "scheduled_tasks": {
        "implementation": "Threading with schedule library",
        "tasks": ["Log rotation", "Cache cleanup", "Performance analysis"],
        "configuration": "User-configurable schedules"
    },
    "backup_automation": {
        "strategy": "Incremental backups with compression",
        "storage": "Local with optional cloud upload",
        "retention": "30-day retention with archival"
    }
}
```

This comprehensive technology documentation serves as the definitive reference for all technical decisions, development practices, and system architecture for Richard's File Utilities, ensuring consistent implementation and maintainable codebase evolution.
