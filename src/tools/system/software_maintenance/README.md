# Software Maintenance Toolkit

A comprehensive software management solution for Richard's File Utilities, providing intelligent software updating and powerful uninstallation capabilities with advanced automation, safety features, and seamless integration.

## Features

### 🔄 Intelligent Software Updater
- **Automatic Software Scanning**: Detects installed applications across multiple platforms (Windows, macOS, Linux)
- **Multi-Source Update Checking**: Integrates with Chocolatey, Winget, Homebrew, APT, and other package managers
- **Detailed Changelog Information**: Retrieves and displays comprehensive update information
- **Selective Updating**: Choose which software to update with granular control
- **Rollback Capabilities**: Safe update process with automatic backup and restore functionality
- **Scheduling & Automation**: Set up automatic update checks and installations
- **Update History Logging**: Complete audit trail of all update activities

### 🗑️ Powerful Software De-Installer
- **Deep System Scanning**: Comprehensive detection of installed applications and components
- **Complete Uninstallation**: Removes software along with leftover files and registry entries
- **Batch Uninstallation**: Remove multiple applications efficiently
- **Restore Points**: Automatic system restore point creation before removal
- **Disk Space Analysis**: Calculate and track space recovery from uninstallations
- **Leftover Cleanup**: Intelligent detection and removal of orphaned files and settings
- **Uninstallation History**: Detailed logging and reporting of removal activities

### 🛡️ Advanced Safety Features
- **Backup & Restore**: Comprehensive backup system with rollback capabilities
- **Administrative Privilege Management**: Secure UAC integration and privilege elevation
- **Security Protocols**: Encrypted communication and audit logging
- **Cross-Platform Compatibility**: Native support for Windows, macOS, and Linux
- **Progress Tracking**: Real-time progress indicators and status reporting

## Architecture

### Core Components

#### `core/` - Foundation Infrastructure
- **`maintenance_base.py`**: Base class providing common functionality for all tools
- **`software_detector.py`**: Cross-platform software detection and management
- **`security_manager.py`**: Security, backup, and restore point management
- **`update_sources.py`**: Multi-source update checking and management
- **`platform_support.py`**: Cross-platform compatibility utilities

#### `tools/` - Main Applications
- **`software_updater.py`**: Intelligent software updater with scheduling
- **`software_deinstaller.py`**: Powerful software removal with deep scanning

#### `gui/` - User Interface
- **`maintenance_hub.py`**: Unified GUI with tabbed interface and progress tracking

### Data Management
- **Configuration**: JSON-based settings and preferences
- **Logging**: Comprehensive activity logging with multiple levels
- **Reports**: Detailed analysis and operation reports
- **Backups**: Automated backup creation and management
- **History**: Complete audit trail of all operations

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt5 for GUI functionality
- Administrative privileges for system-level operations

### Required Dependencies
```bash
pip install PyQt5 requests schedule
```

### Platform-Specific Requirements

#### Windows
- Windows 10 or higher
- PowerShell 5.0+ (for system restore points)
- Optional: Chocolatey, Winget, or Scoop package managers

#### macOS
- macOS 10.14 or higher
- Optional: Homebrew or MacPorts package managers

#### Linux
- Modern Linux distribution
- Package manager (APT, YUM, DNF, Pacman, etc.)
- Optional: Snap, Flatpak support

## Usage

### Quick Start
1. Launch the Software Maintenance Toolkit from the RFU Hub
2. Click "Quick Scan" to detect installed software and check for updates
3. Use the Software Updater tab to manage updates
4. Use the Software De-Installer tab to remove unwanted software

### Software Updater Workflow
1. **Scan Software**: Detect all installed applications
2. **Check Updates**: Query multiple sources for available updates
3. **Review Changes**: View changelogs and update details
4. **Select Updates**: Choose which software to update
5. **Execute Updates**: Perform updates with automatic backup
6. **Monitor Progress**: Track update status and completion

### Software De-Installer Workflow
1. **Scan for Removal**: Analyze installed software for removal
2. **Select Software**: Choose applications to uninstall
3. **Analyze Impact**: Review disk space recovery and dependencies
4. **Create Backups**: Automatic backup and restore point creation
5. **Execute Removal**: Perform uninstallation with leftover cleanup
6. **Verify Results**: Confirm successful removal and space recovery

### Advanced Features

#### Scheduling Updates
- Set up automatic update checks (daily, weekly, monthly)
- Configure security-only updates for automatic installation
- Customize update filters and software selection

#### Batch Operations
- Update multiple software packages simultaneously
- Uninstall multiple applications in one operation
- Progress tracking for batch operations

#### Safety & Recovery
- Automatic backup creation before any changes
- System restore point integration
- Rollback capabilities for failed operations
- Comprehensive audit logging

## Configuration

### Settings Management
The toolkit uses JSON configuration files stored in `software_maintenance/config/`:

- **`updater_config.json`**: Software updater preferences
- **`deinstaller_config.json`**: De-installer settings
- **`backup_registry.json`**: Backup management
- **`update_schedules.json`**: Scheduled update configurations
- **`update_history.json`**: Update operation history
- **`uninstall_history.json`**: Uninstallation operation history

### Customization Options
- Update check intervals and automation
- Backup retention policies
- Security and safety settings
- GUI preferences and themes
- Logging levels and output formats

## Security Considerations

### Administrative Privileges
- Secure UAC integration on Windows
- Sudo authentication on Unix-like systems
- Graceful degradation when privileges unavailable

### Data Protection
- Encrypted backup storage
- Secure temporary file handling
- Audit trail maintenance
- Privacy-conscious operation logging

### Safety Protocols
- Pre-operation validation
- Automatic backup creation
- System restore point integration
- Rollback capabilities
- Operation confirmation dialogs

## Troubleshooting

### Common Issues

#### Permission Errors
- Ensure administrative privileges are available
- Check UAC settings on Windows
- Verify sudo access on Unix-like systems

#### Package Manager Integration
- Verify package managers are installed and accessible
- Check PATH environment variables
- Ensure package manager credentials are configured

#### GUI Issues
- Verify PyQt5 installation
- Check display settings and scaling
- Ensure sufficient system resources

### Logging and Diagnostics
- Check log files in `software_maintenance/logs/`
- Review operation history in configuration files
- Use verbose logging for detailed diagnostics

## Integration with RFU Hub

The Software Maintenance Toolkit is fully integrated with Richard's File Utilities Hub:

- **Unified Access**: Launch from the main RFU Hub interface
- **Consistent Theming**: Matches RFU design standards
- **Shared Resources**: Utilizes common RFU infrastructure
- **Seamless Navigation**: Easy switching between utilities

## Development

### Architecture Principles
- **Modular Design**: Separate concerns with clear interfaces
- **Cross-Platform**: Native support for multiple operating systems
- **Safety First**: Comprehensive backup and validation systems
- **User-Friendly**: Intuitive interface with clear progress indication
- **Extensible**: Plugin architecture for additional functionality

### Code Organization
```
software_maintenance/
├── core/                 # Core infrastructure
├── tools/                # Main applications
├── gui/                  # User interface
├── logs/                 # Operation logs
├── backups/              # Backup storage
├── temp/                 # Temporary files
├── reports/              # Analysis reports
├── config/               # Configuration files
└── tests/                # Test suite
```

### Contributing
1. Follow existing code style and patterns
2. Implement comprehensive error handling
3. Add appropriate logging and progress tracking
4. Include safety validation and backup creation
5. Test across multiple platforms
6. Update documentation for new features

## License

This software is part of Richard's File Utilities and follows the same licensing terms.

## Support

For support, issues, or feature requests, please refer to the main RFU documentation and support channels.

---

**Software Maintenance Toolkit** - Intelligent software management for the modern user.