# RFU Hub Security Menu - User Guide

## Overview

The RFU Hub Security Menu provides comprehensive access to all security features implemented in the RFU Hub Preferences Security System. This menu system offers both tabbed interface access and a dedicated menu bar for quick navigation to security features.

## Accessing Security Features

### Method 1: Security Tab
1. Launch RFU Hub: `python main.py`
2. Click on the **"Security"** tab in the main window
3. Click **"Security Preferences"** to open the comprehensive security dialog

### Method 2: Menu Bar Access
1. Launch RFU Hub: `python main.py`
2. Use the **"Security"** menu in the menu bar
3. Select **"Security Preferences..."** or use keyboard shortcut `Ctrl+Shift+S`

### Method 3: Quick Access Menu Items
The Security menu provides direct access to specific features:
- **Security Features** → **Database Migration**, **Theme Security**, **Directory Security**
- **Security Tools** → **Test Security Features**, **Security Audit**, **Export/Import Config**
- **Emergency** → **Security Lockdown**, **Disable All Security**, **Force Backup**

## Security Preferences Dialog

### Tab 1: 🔄 Database Migration
**Purpose**: Manage database schema migrations with rollback capabilities

**Features**:
- **Current Version Display**: Shows current database schema version
- **Target Version Selection**: Choose migration target (001, 002, 003, Latest)
- **Migration Options**:
  - ✅ Create backup before migration
  - ✅ Validate migration integrity
  - ✅ Auto-rollback on failure
- **Actions**:
  - **Execute Migration**: Run migration to target version
  - **Rollback Migration**: Revert to previous version
  - **Validate Schema**: Check database integrity
- **Migration History**: View past migration attempts and results
- **Progress Monitoring**: Real-time migration status and progress

### Tab 2: 🎨 Theme Security
**Purpose**: Encrypt and protect theme data with corruption detection

**Features**:
- **Encryption Settings**:
  - Enable/disable theme data encryption
  - Algorithm selection (AES-256-GCM recommended)
  - Key derivation method (PBKDF2-SHA256 recommended)
  - KDF iterations configuration (default: 100,000)
- **Corruption Detection**:
  - Automatic corruption scanning
  - Check frequency configuration
  - Recovery strategy selection
- **Actions**:
  - **Encrypt All Themes**: Apply encryption to theme data
  - **Decrypt All Themes**: Remove encryption from themes
  - **Test Encryption**: Verify encryption functionality
  - **Scan for Corruption**: Check theme data integrity
  - **Repair Corruption**: Fix detected corruption issues

### Tab 3: 📁 Directory Security
**Purpose**: Control and monitor directory access

**Features**:
- **Access Control**:
  - Enable directory access control system
  - Protected directories management
  - Access level configuration
- **Directory Management**:
  - **Add Directory**: Protect new directories
  - **Remove Directory**: Remove protection
  - **Edit Permissions**: Modify access levels
- **Monitoring**:
  - Real-time directory change monitoring
  - Sensitivity level adjustment
  - Unauthorized access alerts
  - Complete access logging
- **Security Log**: View and export directory security events

### Tab 4: 📋 Security Audit
**Purpose**: Comprehensive security event logging and analysis

**Features**:
- **Audit Configuration**:
  - Enable comprehensive audit logging
  - Log level selection (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Category filtering (Database, Theme, Directory, Authentication, etc.)
  - Log rotation settings (size limits and backup count)
- **Log Viewer**:
  - Filter by category, level, and date range
  - Real-time log display
  - Search and navigation capabilities
- **Actions**:
  - **Refresh**: Update log display
  - **Export Log**: Save audit log to file
  - **Clear Log**: Remove old log entries

### Tab 5: 📊 Status Monitor
**Purpose**: Real-time security system monitoring

**Features**:
- **Component Status Dashboard**:
  - 🔄 Database Migration: Status indicator and details
  - 🎨 Theme Security: Encryption status and health
  - 📁 Directory Security: Access control status
  - 📋 Audit Logging: Logging system status
- **Security Metrics**:
  - Overall Security Score (0-100)
  - Last migration timestamp
  - Encrypted themes count
  - Protected directories count
  - Audit log entries count
- **Security Alerts**:
  - Real-time security issue notifications
  - Alert severity levels
  - Alert dismissal and management

### Tab 6: ⚙️ Advanced Settings
**Purpose**: Advanced security configuration and emergency procedures

**Features**:
- **Security Profiles**:
  - **Minimal**: Basic protection (low overhead)
  - **Standard**: Recommended settings (balanced)
  - **Enhanced**: High security (increased protection)
  - **Maximum**: Paranoid mode (maximum security)
  - **Custom**: User-defined configuration
- **Advanced Configuration**:
  - Session timeout settings
  - Security validation frequency
  - Secure memory wiping
  - Debug mode controls
- **Emergency Procedures**:
  - **🔒 Security Lockdown**: Lock all security features
  - **💾 Force Backup**: Create immediate security backup
  - **🔄 Reset Security**: Reset to default settings
  - **🔍 Security Audit**: Run comprehensive audit

## Menu Bar Security Features

### Security Menu Structure
```
Security
├── 🔒 Security Preferences...          [Ctrl+Shift+S]
├── ────────────────────────────────
├── 🛡️ Security Features
│   ├── 🔄 Database Migration
│   │   ├── Execute Migration...
│   │   ├── Rollback Migration...
│   │   └── Validate Schema...
│   ├── 🎨 Theme Security
│   │   ├── Encrypt Themes...
│   │   ├── Decrypt Themes...
│   │   └── Scan for Corruption...
│   └── 📁 Directory Security
│       ├── Manage Protected Directories...
│       └── Security Monitor...
├── ────────────────────────────────
├── 🔧 Security Tools
│   ├── Test Security Features...
│   ├── Security Audit...
│   ├── Export Security Config...
│   └── Import Security Config...
├── ────────────────────────────────
└── 🚨 Emergency
    ├── Security Lockdown...
    ├── Disable All Security...
    └── Force Security Backup...
```

## Quick Actions Guide

### Daily Security Tasks
1. **Check Security Status**: Security → Security Preferences → Status Monitor
2. **Review Audit Log**: Security → Security Preferences → Security Audit
3. **Monitor Alerts**: Check Status Monitor tab for new alerts

### Configuration Tasks
1. **Enable Theme Encryption**: Security → Security Features → Theme Security → Encrypt Themes
2. **Protect Directory**: Security → Security Features → Directory Security → Manage Protected Directories
3. **Configure Audit Logging**: Security → Security Preferences → Security Audit

### Maintenance Tasks
1. **Test Security**: Security → Security Tools → Test Security Features
2. **Run Migration**: Security → Security Features → Database Migration → Execute Migration
3. **Backup Config**: Security → Security Tools → Export Security Config

### Emergency Procedures
1. **Security Issue**: Security → Emergency → Security Lockdown
2. **Data Corruption**: Security → Security Features → Theme Security → Scan for Corruption
3. **System Recovery**: Security → Emergency → Force Security Backup

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+S` | Open Security Preferences |
| `Alt+S` | Open Security Menu |

## Testing Security Features

### Built-in Security Test
1. Navigate to: Security → Security Tools → Test Security Features
2. This runs the comprehensive security demonstration
3. Verifies all 4 security components:
   - Database Migration System
   - Theme Security Framework
   - Directory Security Framework
   - Integrated Security Features

### Manual Testing
1. **Migration Test**: Create test migration → Execute → Rollback
2. **Theme Encryption Test**: Enable encryption → Test with sample theme → Verify integrity
3. **Directory Protection Test**: Add protected directory → Test access controls
4. **Audit Test**: Perform security actions → Verify logging

## Configuration Management

### Export Security Configuration
1. Security → Security Tools → Export Security Config
2. Saves all security settings to JSON file
3. Includes: migration settings, theme security, directory controls, audit configuration

### Import Security Configuration
1. Security → Security Tools → Import Security Config
2. Loads security settings from JSON file
3. Applies configuration across all security components
4. Requires application restart for full effect

## Troubleshooting

### Common Issues

1. **Security Preferences Won't Open**
   - Check PyQt5 installation: `pip install PyQt5`
   - Verify imports in security_preferences_dialog.py
   - Check console for import errors

2. **Migration Fails**
   - Check database permissions
   - Verify backup directory exists
   - Review migration logs in Security Audit

3. **Theme Encryption Issues**
   - Verify cryptography library: `pip install cryptography`
   - Check keyring availability
   - Test with demo encryption script

4. **Directory Protection Not Working**
   - Check directory exists and is accessible
   - Verify permissions on target directory
   - Review directory security logs

### Getting Help
1. **Security Help**: Help → Security Help
2. **About Security**: Help → About Security Features
3. **Documentation**: Review `RFU_Hub_Security_Implementation_COMPLETE.md`
4. **Logs**: Check `rfu_errors.log` for detailed error information

## Best Practices

### Security Configuration
1. **Use Standard Profile**: Recommended for most users
2. **Enable Audit Logging**: Essential for security monitoring
3. **Regular Backups**: Export configuration regularly
4. **Test Migrations**: Always test on non-production data first

### Monitoring
1. **Check Status Daily**: Review security status indicators
2. **Monitor Alerts**: Address security alerts promptly
3. **Review Audit Logs**: Weekly audit log review
4. **Update Security Settings**: Adjust based on usage patterns

### Emergency Preparedness
1. **Know Emergency Procedures**: Familiarize with emergency menu
2. **Keep Backups Current**: Regular configuration exports
3. **Test Recovery**: Periodically test rollback procedures
4. **Document Changes**: Log any security configuration changes

## Integration with Other Tools

The security menu integrates seamlessly with other RFU Hub tools:
- **File Operations**: Directory protection applies to all file operations
- **PDF Tools**: Theme encryption protects PDF processing themes
- **Network Tools**: Security audit logs network operations
- **Database Tools**: Migration system protects all database operations

## Support and Resources

- **Documentation**: `RFU_Hub_Security_Implementation_COMPLETE.md`
- **Implementation Plan**: `Implementation Plan Preferences Menu for RFU Hub.md`
- **Test Scripts**: `test_security_menu_integration.py`, `demo_security_implementation.py`
- **Configuration**: Security settings stored in `config/rfu_config.json`
- **Logs**: Security events logged to `rfu_errors.log` and dedicated audit logs
