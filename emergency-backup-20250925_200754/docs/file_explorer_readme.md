# RFU Multi-Pane File Explorer - README

## Overview

RFU Multi-Pane File Explorer is a comprehensive, enterprise-grade file management application built with Python and PyQt5/PyQt6. It provides advanced features for efficient file organization, cross-platform compatibility, and extensible architecture.

## Key Features

- **Multi-Pane Interface**: Multiple file explorer panes with flexible layouts
- **Cross-Platform**: Windows, macOS, and Linux support
- **High Performance**: Optimized for large directories with caching
- **Extensible**: Plugin architecture for custom functionality
- **Modern UI**: Clean, responsive interface with multiple themes
- **Advanced Search**: Powerful search and filtering capabilities
- **File Operations**: Comprehensive file management operations

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd rfu-file-explorer

# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.rfu.file_explorer.main_application
```

### Basic Usage

1. **Navigate**: Use the file explorer panes to browse directories
2. **Create Panes**: Add new panes using Ctrl+N or File menu
3. **File Operations**: Copy, move, delete files between panes
4. **Search**: Use Ctrl+F for quick search or Ctrl+Shift+F for advanced search
5. **Customize**: Configure layouts, themes, and preferences in Tools menu

## Architecture

### Core Components

- **Database Layer**: SQLite with caching and migrations
- **Models**: File system abstraction and business logic
- **UI Layer**: PyQt-based interface with custom widgets
- **Utilities**: Cross-platform helpers and monitoring

### Technology Stack

- **Python 3.9+**: Core language with type hints
- **PyQt5/PyQt6**: GUI framework with fallback support
- **SQLite**: Database backend with WAL mode
- **Watchdog**: File system monitoring
- **Threading**: Concurrent operations and UI responsiveness

## Documentation

- [User Guide](docs/file_explorer_user_guide.md) - Complete user documentation
- [API Documentation](docs/file_explorer_api_documentation.md) - Developer API reference
- [Developer Guide](docs/file_explorer_developer_guide.md) - Contributing and extension guide

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/rfu/file_explorer

# Run specific test categories
pytest -m "not slow"     # Skip slow tests
pytest -m gui            # GUI tests only
pytest -m performance    # Performance tests
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes following the coding standards
4. Add tests for new functionality
5. Submit a pull request

See [Developer Guide](docs/file_explorer_developer_guide.md) for detailed contributing guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Documentation: See docs/ directory
- Issues: Use GitHub issue tracker
- Development: See developer guide for setup instructions

---

**Version**: 1.0.0  
**Python**: 3.9+  
**License**: MIT  
**Platform**: Windows, macOS, Linux