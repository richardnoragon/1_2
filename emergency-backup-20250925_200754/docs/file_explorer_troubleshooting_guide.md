# RFU Multi-Pane File Explorer - Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide helps users and developers diagnose and resolve issues with the RFU Multi-Pane File Explorer. The guide covers common problems, diagnostic procedures, and step-by-step solutions.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Startup Problems](#startup-problems)
4. [Performance Issues](#performance-issues)
5. [File Operation Failures](#file-operation-failures)
6. [Tool Integration Problems](#tool-integration-problems)
7. [Database Issues](#database-issues)
8. [Configuration Problems](#configuration-problems)
9. [UI and Display Issues](#ui-and-display-issues)
10. [Network and Permissions](#network-and-permissions)
11. [Diagnostic Tools](#diagnostic-tools)
12. [Log Analysis](#log-analysis)
13. [Recovery Procedures](#recovery-procedures)

## Quick Diagnostics

### First Steps for Any Issue

1. **Check System Requirements**:
   - Python 3.8+ installed
   - PyQt5 5.15+ available
   - Minimum 4GB RAM
   - 100MB+ free disk space

2. **Verify Installation**:
   ```bash
   python -c "import PyQt5; print('PyQt5 available')"
   python -c "import sqlite3; print('SQLite available')"
   ```

3. **Check Log Files**:
   - Application log: `logs/application.log`
   - Error log: `logs/error.log`
   - Debug log: `logs/debug.log` (if enabled)

4. **Test Basic Functionality**:
   ```bash
   python src/rfu/file_explorer/multi_pane_explorer.py --test-mode
   ```

### Common Problem Indicators

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Application won't start | Missing dependencies | `pip install -r requirements.txt` |
| Slow performance | High memory usage | Reduce pane count, clear cache |
| File operations fail | Permission issues | Run as administrator |
| Tools don't launch | Tool path misconfiguration | Check tool settings |
| Database errors | Corrupted database | Restore from backup |
| UI elements missing | Configuration corruption | Reset to defaults |

## Installation Issues

### Dependency Problems

**Missing PyQt5**:
```bash
# Solution 1: Install via pip
pip install PyQt5

# Solution 2: Install via conda
conda install pyqt

# Solution 3: System package manager (Linux)
sudo apt-get install python3-pyqt5
```

**Missing Required Modules**:
```bash
# Check missing modules
python -c "
import sys
required = ['PyQt5', 'sqlite3', 'json', 'pathlib', 'logging']
missing = []
for module in required:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)
if missing:
    print(f'Missing modules: {missing}')
else:
    print('All required modules available')
"

# Install missing modules
pip install -r requirements.txt
```

**Permission Errors During Installation**:
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo or virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Path and Environment Issues

**Python Path Problems**:
```python
# Add to PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Or set environment variable
export PYTHONPATH="${PYTHONPATH}:/path/to/rfu/project"
```

**Configuration Directory Creation**:
```bash
# Manually create required directories
mkdir -p config data logs build/temp
chmod 755 config data logs build/temp
```

## Startup Problems

### Application Won't Start

**Diagnostic Steps**:
1. Run with verbose logging:
   ```bash
   python src/rfu/file_explorer/multi_pane_explorer.py --verbose --debug
   ```

2. Check for import errors:
   ```bash
   python -c "from src.rfu.file_explorer.multi_pane_explorer import MultiPaneFileExplorer; print('Import successful')"
   ```

3. Test PyQt5 separately:
   ```python
   from PyQt5.QtWidgets import QApplication, QWidget
   import sys
   app = QApplication(sys.argv)
   widget = QWidget()
   widget.show()
   print("PyQt5 working correctly")
   ```

**Common Solutions**:

**Missing Display Server (Linux)**:
```bash
# Install X11 forwarding
export DISPLAY=:0.0

# Or use virtual display
sudo apt-get install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

**Qt Plugin Loading Issues**:
```bash
# Set Qt plugin path
export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins

# Or copy plugins to application directory
cp -r /usr/lib/x86_64-linux-gnu/qt5/plugins ./qt_plugins
export QT_PLUGIN_PATH=./qt_plugins
```

### Configuration Loading Failures

**Reset Configuration**:
```bash
# Backup current config
cp config/rfu_config.json config/rfu_config.json.backup

# Reset to defaults
python scripts/reset_configuration.py

# Or manually delete config
rm config/rfu_config.json
```

**Configuration Migration Issues**:
```bash
# Check config format
python -c "
import json
with open('config/rfu_config.json', 'r') as f:
    config = json.load(f)
print('Configuration valid')
"

# Migrate old configuration
python scripts/migrate_configuration.py --from-version 1.0 --to-version 2.0
```

## Performance Issues

### High Memory Usage

**Memory Monitoring**:
```bash
# Check memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f'Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB')
"
```

**Memory Optimization Steps**:

1. **Reduce Pane Count**:
   - Limit to 2 panes for systems with <8GB RAM
   - Close unused panes

2. **Disable Heavy Features**:
   ```python
   # In configuration
   {
     "file_explorer": {
       "enable_thumbnails": false,
       "enable_preview": false,
       "cache_size_mb": 50
     }
   }
   ```

3. **Clear Cache**:
   ```bash
   # Clear application cache
   rm -rf build/temp/*
   rm -rf __pycache__
   
   # Clear database cache
   python scripts/clear_database_cache.py
   ```

### Slow Directory Loading

**Large Directory Optimization**:
```python
# Configure directory loading limits
{
  "file_explorer": {
    "max_files_per_directory": 5000,
    "enable_lazy_loading": true,
    "directory_scan_timeout": 30
  }
}
```

**Network Drive Issues**:
```python
# Configure network timeout
{
  "file_explorer": {
    "network_timeout": 10,
    "cache_network_paths": true,
    "offline_mode": false
  }
}
```

### UI Responsiveness

**Background Threading**:
```python
# Ensure operations run in background
{
  "file_explorer": {
    "async_file_operations": true,
    "ui_update_interval": 100,
    "max_concurrent_operations": 3
  }
}
```

**Display Optimization**:
```python
# Reduce UI updates
{
  "ui": {
    "reduce_animations": true,
    "disable_transparency": true,
    "simple_icons": true
  }
}
```

## File Operation Failures

### Permission Errors

**Diagnostic Commands**:
```bash
# Check file permissions
ls -la /path/to/file

# Check directory permissions
ls -ld /path/to/directory

# Test write access
touch /path/to/directory/test_file && rm /path/to/directory/test_file
```

**Windows Permission Issues**:
1. Run as Administrator
2. Check UAC settings
3. Verify NTFS permissions
4. Disable antivirus temporarily

**Linux/macOS Permission Issues**:
```bash
# Change ownership
sudo chown -R $USER:$GROUP /path/to/directory

# Change permissions
chmod -R 755 /path/to/directory

# Add to sudoers for specific operations
sudo visudo
```

### File Lock Issues

**Detect Locked Files**:
```bash
# Windows
handle.exe filename

# Linux
lsof filename

# macOS
lsof filename
```

**Solutions**:
1. Close applications using the files
2. Restart explorer process
3. Reboot system if necessary
4. Use force operations (with caution)

### Disk Space Problems

**Check Available Space**:
```bash
# Cross-platform disk usage check
python -c "
import shutil
total, used, free = shutil.disk_usage('.')
print(f'Total: {total // (1024**3)} GB')
print(f'Used: {used // (1024**3)} GB')
print(f'Free: {free // (1024**3)} GB')
"
```

**Free Up Space**:
1. Clear temporary files
2. Empty recycle bin
3. Clear application logs
4. Remove old backups

## Tool Integration Problems

### Tool Not Found

**Check Tool Registration**:
```python
# List registered tools
python -c "
from src.rfu.file_explorer.tool_integration import ToolIntegrationManager
manager = ToolIntegrationManager(None)
tools = manager.get_available_tools()
for tool in tools:
    print(f'{tool[\"name\"]}: {tool[\"executable\"]}')
"
```

**Re-register Tools**:
```bash
# Scan for tools
python scripts/scan_tools.py

# Manually register tool
python scripts/register_tool.py --name "Tool Name" --path "/path/to/tool"
```

### Tool Launch Failures

**Check Tool Permissions**:
```bash
# Make tool executable
chmod +x /path/to/tool

# Test tool independently
/path/to/tool --version
```

**Debug Tool Launch**:
```python
# Enable tool debugging
{
  "tools": {
    "debug_mode": true,
    "log_tool_output": true,
    "timeout_seconds": 30
  }
}
```

## Database Issues

### Database Corruption

**Check Database Integrity**:
```bash
# SQLite integrity check
sqlite3 database.db "PRAGMA integrity_check;"
```

**Repair Database**:
```bash
# Dump and restore database
sqlite3 database.db ".dump" | sqlite3 database_new.db
mv database.db database_corrupt.db
mv database_new.db database.db
```

### Connection Problems

**Test Database Connection**:
```python
import sqlite3
try:
    conn = sqlite3.connect('database.db')
    conn.execute("SELECT 1")
    conn.close()
    print("Database connection successful")
except Exception as e:
    print(f"Database error: {e}")
```

**Fix Connection Issues**:
1. Check file permissions
2. Verify disk space
3. Test with new database
4. Restore from backup

### Migration Failures

**Safe Migration Recovery**:
```bash
# Restore from backup
cp data/migration_backups/latest/database.db ./database.db

# Check migration status
python scripts/check_migration_status.py

# Retry migration
python scripts/migrate_database.py --force
```

## Configuration Problems

### Invalid Configuration

**Validate Configuration**:
```python
import json
try:
    with open('config/rfu_config.json', 'r') as f:
        config = json.load(f)
    print("Configuration is valid JSON")
except json.JSONDecodeError as e:
    print(f"Configuration JSON error: {e}")
```

**Fix Configuration**:
```bash
# Backup current config
cp config/rfu_config.json config/rfu_config.json.backup

# Use default configuration
cp config/default_config.json config/rfu_config.json

# Or reset completely
python scripts/reset_configuration.py
```

### Settings Not Saving

**Check Write Permissions**:
```bash
# Test write access
touch config/test_write && rm config/test_write
```

**Debug Save Process**:
```python
# Enable configuration debugging
{
  "debug": {
    "log_config_changes": true,
    "backup_before_save": true,
    "validate_before_save": true
  }
}
```

## UI and Display Issues

### Layout Problems

**Reset Layout**:
```bash
# Reset window layout
python -c "
from src.rfu.file_explorer.config_manager import ConfigurationManager
config = ConfigurationManager()
config.reset_section('ui_layout')
config.save_configuration()
"
```

**Force Layout Refresh**:
```python
# In application
explorer.refresh_layout()
explorer.update_pane_layout()
```

### Missing UI Elements

**Check Theme Issues**:
```python
# Switch to default theme
{
  "ui": {
    "theme": "default",
    "use_native_styling": true
  }
}
```

**Font Problems**:
```python
# Reset fonts
{
  "ui": {
    "font_family": "default",
    "font_size": 10,
    "use_system_fonts": true
  }
}
```

### High DPI Issues

**Configure High DPI**:
```python
# Enable high DPI support
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
```

## Network and Permissions

### Network Drive Access

**Test Network Connectivity**:
```bash
# Test network path
net use \\server\share

# Or mount network drive
sudo mount -t cifs //server/share /mnt/share
```

**Configure Network Timeouts**:
```python
{
  "network": {
    "connection_timeout": 30,
    "read_timeout": 60,
    "retry_attempts": 3,
    "use_credentials": true
  }
}
```

### Antivirus Interference

**Add Exclusions**:
1. Application directory
2. Configuration directory
3. Database files
4. Temporary directories

**Test Without Antivirus**:
1. Temporarily disable real-time protection
2. Test application functionality
3. Re-enable protection with exclusions

## Diagnostic Tools

### Built-in Diagnostics

**Run System Check**:
```bash
python scripts/system_check.py --verbose
```

**Generate Diagnostic Report**:
```bash
python scripts/generate_diagnostic_report.py --output diagnostic_report.txt
```

### External Tools

**Memory Profiling**:
```bash
# Install memory profiler
pip install memory-profiler

# Profile application
python -m memory_profiler src/rfu/file_explorer/multi_pane_explorer.py
```

**Performance Profiling**:
```bash
# Install profiling tools
pip install cProfile

# Profile application
python -m cProfile -o profile_output.prof src/rfu/file_explorer/multi_pane_explorer.py
```

## Log Analysis

### Enable Debug Logging

**Configure Logging**:
```python
{
  "logging": {
    "level": "DEBUG",
    "enable_file_logging": true,
    "log_file": "logs/debug.log",
    "max_log_size_mb": 50,
    "backup_count": 5
  }
}
```

**Analyze Logs**:
```bash
# Search for errors
grep -i error logs/application.log

# Filter by component
grep "PaneManager" logs/debug.log

# Show recent errors
tail -n 100 logs/error.log
```

### Log Patterns

**Common Error Patterns**:
- `ImportError`: Missing dependencies
- `PermissionError`: File/directory access issues
- `OSError`: System-level problems
- `DatabaseError`: Database connection/corruption
- `ConfigurationError`: Configuration problems

## Recovery Procedures

### Emergency Recovery

**Safe Mode Launch**:
```bash
python src/rfu/file_explorer/multi_pane_explorer.py --safe-mode
```

**Reset Everything**:
```bash
# Backup current state
mkdir backup_$(date +%Y%m%d_%H%M%S)
cp -r config data logs backup_*/

# Reset to defaults
rm -rf config/* data/* logs/*
python scripts/initialize_application.py
```

### Data Recovery

**Restore from Backup**:
```bash
# List available backups
ls -la data/migration_backups/

# Restore specific backup
cp -r data/migration_backups/20250913_143022/* .
```

**Database Recovery**:
```bash
# Attempt automatic repair
python scripts/repair_database.py

# Manual recovery
sqlite3 database.db ".recover" | sqlite3 database_recovered.db
```

### Rollback Procedures

**Configuration Rollback**:
```bash
# Find backup
ls config/*.backup

# Restore backup
cp config/rfu_config.json.backup config/rfu_config.json
```

**Application Rollback**:
```bash
# Use git to rollback
git checkout HEAD~1

# Or restore from archive
tar -xzf rfu_backup.tar.gz
```

## Prevention Strategies

### Regular Maintenance

**Weekly Tasks**:
1. Check log files for errors
2. Clear temporary files
3. Verify database integrity
4. Update configuration backup

**Monthly Tasks**:
1. Run full system diagnostics
2. Update dependencies
3. Clean old log files
4. Performance optimization review

### Monitoring Setup

**Automated Monitoring**:
```bash
# Create monitoring script
#!/bin/bash
python scripts/health_check.py
if [ $? -ne 0 ]; then
    echo "Health check failed" | mail -s "RFU Explorer Alert" admin@example.com
fi
```

**Performance Baseline**:
```bash
# Establish performance baseline
python scripts/performance_benchmark.py --save-baseline
```

## Getting Additional Help

### Support Channels

1. **GitHub Issues**: Bug reports and feature requests
2. **Documentation Wiki**: Community-maintained guides
3. **Discussion Forum**: Questions and community support
4. **Email Support**: Critical issues and enterprise support

### Information to Include

When reporting issues, include:

1. **System Information**:
   - Operating system and version
   - Python version
   - PyQt5 version
   - Available memory and disk space

2. **Error Details**:
   - Complete error messages
   - Steps to reproduce
   - Expected vs. actual behavior
   - Relevant log excerpts

3. **Configuration**:
   - Configuration file contents (sanitized)
   - Custom settings and modifications
   - Plugin information

4. **Diagnostic Output**:
   - System check results
   - Diagnostic report
   - Performance metrics

---

*This troubleshooting guide is part of the RFU Multi-Pane File Explorer documentation suite. For additional support, consult the User Guide and API Documentation.*