# Privacy Tools for Richard's File Utilities

## Overview

The Privacy Tools module provides comprehensive privacy cleaning capabilities for Richard's File Utilities. It offers cross-platform support for Windows, macOS, and Linux, with multi-browser compatibility for all major web browsers.

## Features

### ✅ Implemented Tools

1. **Secure Empty Trash**
   - Securely empties system trash/recycle bin
   - Optional secure deletion with multiple overwrite passes
   - Cross-platform support (Windows, macOS, Linux)
   - Progress tracking and status updates

2. **Delete Browser Cookies**
   - Multi-browser support (Chrome, Firefox, Edge, Safari)
   - Selective deletion by domain and date range
   - Backup options before deletion
   - Real-time cookie counting and preview

3. **Privacy Tools GUI Hub**
   - Unified interface for all privacy tools
   - Tabbed interface for easy navigation
   - Browser detection and status monitoring
   - Quick actions and batch operations

### 🚧 Planned Tools (Future Implementation)

4. **Delete Internet History**
   - Browser history deletion across all supported browsers
   - Date range filtering and selective deletion
   - Download history inclusion

5. **Delete File History**
   - Windows: Recent files, jump lists, thumbnail cache
   - macOS: Recent items, Spotlight index
   - Linux: Recent files in various file managers

6. **Delete Browser Downloads**
   - Download history from browsers
   - Option to delete actual downloaded files
   - Selective deletion by date/type

## Supported Platforms

- **Windows 10/11**: Full support with Windows API integration
- **macOS**: Native support for all macOS versions
- **Linux**: Support for major distributions with XDG compliance

## Supported Browsers

- **Google Chrome**: Full support across all platforms
- **Mozilla Firefox**: Full support across all platforms
- **Microsoft Edge**: Full support on Windows and macOS
- **Safari**: macOS support (limited on other platforms)
- **Opera**: Planned support
- **Brave**: Planned support

## Architecture

### Core Components

```
privacy_tools/
├── core/                    # Core utilities and base classes
│   ├── privacy_base.py      # Base class for all privacy tools
│   ├── platform_utils.py    # Cross-platform utilities
│   ├── browser_detector.py  # Browser detection and management
│   └── data_locations.py    # Browser data location mappings
├── tools/                   # Individual privacy tools
│   ├── secure_empty_trash.py
│   ├── delete_cookies.py
│   └── [future tools...]
├── gui/                     # GUI components
│   └── privacy_hub.py       # Main privacy tools interface
└── tests/                   # Test suite
```

### Key Design Principles

1. **Cross-Platform Compatibility**: All tools work consistently across Windows, macOS, and Linux
2. **Browser Agnostic**: Support for multiple browsers with unified interfaces
3. **Safety First**: Backup options, confirmation dialogs, and preview capabilities
4. **Extensible Architecture**: Easy to add new privacy tools and browser support
5. **User-Friendly**: Intuitive GUI with clear progress indicators and status updates

## Usage

### From Main RFU Hub

1. Launch Richard's File Utilities
2. Click the "Privacy Tools" button in the main hub
3. Select the desired privacy tool from the tabbed interface
4. Configure options and preview operations
5. Execute the privacy cleaning operation

### Standalone Usage

```python
from privacy_tools.gui.privacy_hub import PrivacyToolsHub
from PyQt5.QtWidgets import QApplication

app = QApplication([])
privacy_hub = PrivacyToolsHub()
privacy_hub.show()
app.exec_()
```

### Programmatic Usage

```python
from privacy_tools.tools.secure_empty_trash import SecureEmptyTrashTool
from privacy_tools.tools.delete_cookies import DeleteCookiesTool

# Secure empty trash
trash_tool = SecureEmptyTrashTool()
result = trash_tool.execute_operation(secure_delete=True)

# Delete cookies
cookies_tool = DeleteCookiesTool()
result = cookies_tool.execute_operation(
    browsers=['chrome', 'firefox'],
    domain_filter='google.com',
    days_old=30
)
```

## Configuration

### Browser Detection

The system automatically detects installed browsers by checking:

- **Windows**: Registry entries and standard installation paths
- **macOS**: Applications folder and user library
- **Linux**: Package manager installations and config directories

### Data Locations

Browser data is located using platform-specific paths:

#### Windows
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\`
- Firefox: `%APPDATA%\Mozilla\Firefox\Profiles\`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\`

#### macOS
- Chrome: `~/Library/Application Support/Google/Chrome/`
- Firefox: `~/Library/Application Support/Firefox/Profiles/`
- Safari: `~/Library/Safari/`

#### Linux
- Chrome: `~/.config/google-chrome/`
- Firefox: `~/.mozilla/firefox/`
- Edge: `~/.config/microsoft-edge/`

## Security Features

### Secure Deletion

- **Multiple Overwrite Passes**: Configurable number of overwrite passes (1, 3, 7, or 35)
- **Random Data**: Uses cryptographically secure random data for overwriting
- **File Renaming**: Multiple random renames before deletion
- **Metadata Clearing**: Ensures file metadata is properly cleared

### Safety Measures

- **Browser Running Detection**: Prevents operations while browsers are active
- **Backup Creation**: Optional backup before deletion operations
- **Preview Mode**: Shows what will be deleted before execution
- **Confirmation Dialogs**: Multiple confirmation steps for destructive operations
- **Progress Tracking**: Real-time progress updates with ability to cancel

### Permission Handling

- **Privilege Detection**: Automatically detects administrator/root privileges
- **Graceful Degradation**: Continues with available permissions when possible
- **Clear Messaging**: Informs users about permission requirements

## Error Handling

### Comprehensive Error Management

- **Exception Catching**: All operations wrapped in try-catch blocks
- **User-Friendly Messages**: Technical errors translated to user-friendly language
- **Logging Integration**: Full integration with RFU logging system
- **Recovery Options**: Suggests solutions for common error scenarios

### Common Error Scenarios

1. **Browser Running**: Clear instructions to close browsers
2. **Permission Denied**: Guidance on running with appropriate privileges
3. **File Access Issues**: Alternative approaches when files are locked
4. **Database Corruption**: Safe handling of corrupted browser databases

## Performance Considerations

### Optimization Features

- **Threaded Operations**: All long-running operations run in separate threads
- **Progress Reporting**: Real-time progress updates prevent UI freezing
- **Memory Management**: Efficient handling of large files and databases
- **Batch Processing**: Optimized batch operations for multiple items

### Resource Usage

- **Low Memory Footprint**: Streaming operations for large files
- **CPU Efficiency**: Optimized algorithms for file operations
- **Disk I/O**: Minimized disk operations through smart caching

## Integration with RFU Hub

### Seamless Integration

- **Consistent Styling**: Uses RFU's standard window and theme system
- **Unified Error Handling**: Integrates with RFU's error handling framework
- **Shared Configuration**: Uses RFU's configuration management system
- **Logging Integration**: Full integration with RFU's logging system

### Theme Support

- **Standard Themes**: Supports all RFU themes and color schemes
- **Responsive Design**: Adapts to different window sizes and resolutions
- **Accessibility**: Follows RFU's accessibility guidelines

## Testing

### Test Coverage

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality testing
- **Platform Tests**: Platform-specific functionality verification
- **Browser Tests**: Multi-browser compatibility testing

### Test Execution

```bash
# Run all privacy tools tests
python -m pytest privacy_tools/tests/

# Run specific test categories
python -m pytest privacy_tools/tests/test_secure_trash.py
python -m pytest privacy_tools/tests/test_cookies.py
```

## Troubleshooting

### Common Issues

1. **"Browser is running" Error**
   - Solution: Close all browser windows and try again
   - Note: Some browsers run background processes

2. **"Permission denied" Error**
   - Solution: Run RFU as administrator (Windows) or with sudo (Linux/macOS)
   - Alternative: Use non-secure deletion mode

3. **"No browsers detected" Message**
   - Solution: Ensure browsers are properly installed
   - Check: Browser installation paths and permissions

4. **Database Access Errors**
   - Solution: Ensure browsers are completely closed
   - Alternative: Restart the system if browsers won't close

### Debug Mode

Enable debug logging in RFU settings for detailed operation logs:

```python
from log_manager import LogManager
LogManager().set_level('DEBUG')
```

## Future Enhancements

### Planned Features

1. **Additional Browser Support**: Opera, Brave, Vivaldi
2. **Cloud Sync Cleaning**: Clear cloud synchronization data
3. **Plugin Data**: Clear browser extension/plugin data
4. **Scheduled Cleaning**: Automated privacy cleaning schedules
5. **Custom Rules**: User-defined cleaning rules and filters

### Performance Improvements

1. **Parallel Processing**: Multi-threaded operations for faster cleaning
2. **Smart Caching**: Intelligent caching for repeated operations
3. **Incremental Updates**: Only process changed data
4. **Background Operations**: Non-blocking background cleaning

## Contributing

### Development Guidelines

1. **Follow RFU Patterns**: Use existing RFU coding standards and patterns
2. **Cross-Platform Testing**: Test on all supported platforms
3. **Documentation**: Update documentation for new features
4. **Error Handling**: Implement comprehensive error handling
5. **User Experience**: Maintain consistent user experience

### Adding New Tools

1. Inherit from `PrivacyToolBase`
2. Implement required abstract methods
3. Add GUI integration to `PrivacyToolsHub`
4. Create comprehensive tests
5. Update documentation

## License

This module is part of Richard's File Utilities and follows the same licensing terms as the main project.

## Support

For support, bug reports, or feature requests, please use the main RFU support channels or create issues in the project repository.