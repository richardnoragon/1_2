# PDF Tools Troubleshooting Guide
**Richard's File Utilities Hub - PDF Tools Integration**  
**Version:** 1.0  
**Last Updated:** 2025-07-25

## Quick Diagnosis

### Integration Status Check

If PDF Tools are not working properly, first verify the integration status:

1. **Check PDF Tools Button:** Ensure "PDF Tools" button appears in main RFU Hub
2. **Test Button Click:** Click PDF Tools button - should open PDF utilities window
3. **Verify Error Messages:** Check for any error dialogs or console messages
4. **Review Log Files:** Check application logs for integration errors

## Common Integration Issues

### Issue: PDF Tools Button Missing

**Symptoms:**
- No "PDF Tools" button in main RFU Hub interface
- Main application loads normally otherwise

**Causes:**
- Integration code not properly added to `rfuhub.py`
- UI layout issues
- Button creation errors

**Solutions:**
1. Verify `rfuhub.py` contains PDF Tools button code
2. Check for syntax errors in button creation
3. Restart application to reload interface
4. Review application startup logs

### Issue: PDF Tools Button Present but Non-Functional

**Symptoms:**
- PDF Tools button visible but clicking does nothing
- No error messages displayed
- Button appears grayed out or disabled

**Causes:**
- `open_pdf_tools()` method not implemented
- Import errors for PDF modules
- Path configuration issues

**Solutions:**
1. Verify `open_pdf_tools()` method exists in RFUHub class
2. Check Python path includes `pdf_utilities` directory
3. Test PDF module imports manually
4. Review error handling in button click method

### Issue: PDF Tools Window Fails to Open

**Symptoms:**
- Error message when clicking PDF Tools button
- "Import Error" or "Module Not Found" messages
- Application crashes when accessing PDF Tools

**Causes:**
- Missing `pdf_utilities/main.py` file
- Import path configuration errors
- Missing dependencies in PDF modules

**Solutions:**
1. Verify `pdf_utilities/main.py` exists and contains `MainWindow` class
2. Check `sys.path` includes correct directory
3. Test individual PDF module imports
4. Install missing dependencies

## Configuration Issues

### Issue: Configuration System Errors

**Symptoms:**
- "ConfigManager not found" errors
- PDF settings not saving
- Default settings not loading

**Causes:**
- Missing `pdf_utilities/config_manager.py` bridge file
- Configuration file corruption
- Bridge implementation errors

**Solutions:**
1. Verify `pdf_utilities/config_manager.py` exists
2. Check bridge class implementation
3. Validate `configuration.json` syntax
4. Reset configuration to defaults

**Bridge File Check:**
```python
# Verify this file exists: pdf_utilities/config_manager.py
# Should contain ConfigManager class with bridge functionality
```

### Issue: Settings Not Persisting

**Symptoms:**
- PDF tool settings reset on restart
- Configuration changes not saved
- Default values always loaded

**Causes:**
- File permission issues
- Configuration file path errors
- Bridge save method not working

**Solutions:**
1. Check file permissions on configuration files
2. Verify configuration file paths
3. Test configuration save/load manually
4. Review bridge implementation

## Logging Issues

### Issue: No PDF Tool Logs Generated

**Symptoms:**
- PDF operations not appearing in logs
- Empty log files
- Missing log entries

**Causes:**
- Logging bridge not configured
- Log file permission issues
- Logger initialization errors

**Solutions:**
1. Verify `pdf_utilities/log_config.py` bridge exists
2. Check log file permissions
3. Test logger initialization
4. Review logging configuration

**Logging Bridge Check:**
```python
# Verify this file exists: pdf_utilities/log_config.py
# Should contain setup_logger function
```

### Issue: Duplicate Log Entries

**Symptoms:**
- Same log messages appearing multiple times
- Log file size growing rapidly
- Performance issues

**Causes:**
- Multiple logger instances
- Incorrect logger hierarchy
- Bridge configuration errors

**Solutions:**
1. Check for duplicate logger creation
2. Verify logger hierarchy configuration
3. Review bridge implementation
4. Restart application to reset loggers

## Module-Specific Issues

### Issue: Individual PDF Modules Not Working

**Symptoms:**
- Specific PDF tools fail to launch
- "Module not found" errors for individual tools
- Some tools work, others don't

**Causes:**
- Missing module files
- Import dependency errors
- Module-specific configuration issues

**Solutions:**
1. Verify all required module files exist
2. Check module-specific dependencies
3. Test module imports individually
4. Review module error logs

**Module Verification:**
```
Required files in pdf_utilities/:
- main.py (PDF Tools hub)
- extract_text.py (Text extraction)
- split.py (PDF splitting)
- merg.py (PDF merging)
- view.py (PDF viewing)
- [other module files...]
```

### Issue: UI Files Not Loading

**Symptoms:**
- PDF tool windows appear broken
- Missing UI elements
- Layout issues

**Causes:**
- Missing `.ui` files
- UI file path errors
- PyQt5 loading issues

**Solutions:**
1. Verify corresponding `.ui` files exist
2. Check UI file loading paths
3. Test PyQt5 installation
4. Review UI file syntax

## Performance Issues

### Issue: Slow PDF Tools Loading

**Symptoms:**
- Long delay when opening PDF Tools
- Application becomes unresponsive
- High memory usage

**Causes:**
- Large number of modules loading
- Import dependency chains
- Memory allocation issues

**Solutions:**
1. Implement lazy loading for modules
2. Optimize import statements
3. Monitor memory usage
4. Consider module caching

### Issue: PDF Processing Errors

**Symptoms:**
- PDF operations fail
- "Processing error" messages
- Corrupted output files

**Causes:**
- PDF file compatibility issues
- Insufficient memory
- Library version conflicts

**Solutions:**
1. Test with different PDF files
2. Check available memory
3. Verify PDF library versions
4. Review processing logs

## Dependency Issues

### Issue: Missing Python Libraries

**Symptoms:**
- "ModuleNotFoundError" messages
- Import errors for specific libraries
- PDF operations failing

**Causes:**
- Missing required dependencies
- Version incompatibilities
- Virtual environment issues

**Solutions:**
1. Install missing dependencies from `requirements.txt`
2. Check library version compatibility
3. Verify virtual environment activation
4. Update outdated packages

**Common Dependencies:**
```
PyQt5
PyMuPDF
pikepdf
pdfplumber
Pillow
reportlab
```

### Issue: Library Version Conflicts

**Symptoms:**
- Unexpected behavior in PDF operations
- Deprecation warnings
- API compatibility errors

**Causes:**
- Outdated library versions
- Conflicting library requirements
- API changes in newer versions

**Solutions:**
1. Update to compatible library versions
2. Check library documentation for changes
3. Test with known working versions
4. Consider dependency pinning

## Advanced Troubleshooting

### Debug Mode Activation

Enable debug mode for detailed troubleshooting:

1. **Logging Level:** Set logging to DEBUG level
2. **Console Output:** Enable console logging
3. **Error Details:** Capture full stack traces
4. **Module Tracing:** Track module loading

### Manual Testing Procedures

#### Test Configuration Bridge
```python
# Test configuration system
from pdf_utilities.config_manager import ConfigManager
config = ConfigManager()
# Should not raise errors
```

#### Test Logging Bridge
```python
# Test logging system
from pdf_utilities.log_config import setup_logger
logger = setup_logger('test')
logger.info('Test message')
# Should create log entry
```

#### Test PDF Module Import
```python
# Test PDF module imports
import sys
sys.path.insert(0, 'pdf_utilities')
from main import MainWindow
# Should import successfully
```

### Log Analysis

#### Key Log Patterns to Look For

**Successful Integration:**
```
INFO: PDF configuration bridge initialized
INFO: PDF logging system connected
INFO: PDF Tools button created successfully
INFO: PDF main window launched
```

**Common Error Patterns:**
```
ERROR: config_manager module not found
ERROR: Failed to import PDF main window
ERROR: Path configuration error
ERROR: Bridge initialization failed
```

### Recovery Procedures

#### Reset Integration
1. Backup current configuration
2. Remove PDF-specific settings
3. Restart application
4. Reconfigure PDF Tools

#### Rollback Integration
1. Remove PDF Tools button from main interface
2. Disable PDF module imports
3. Restore original configuration
4. Restart application

#### Clean Reinstall
1. Backup user data
2. Remove PDF integration files
3. Restore original files
4. Reapply integration step by step

## Getting Additional Help

### Log File Locations
- Main application logs: `logs/`
- PDF-specific logs: `pdf_utilities/logs/`
- Configuration files: `configuration.json`

### Diagnostic Information to Collect
- Application version
- Python version
- Operating system
- Error messages (full text)
- Log file excerpts
- Configuration file contents

### Support Resources
- Integration documentation: `integrate_pdf_utilities.md`
- User guide: `PDF_TOOLS_USER_GUIDE.md`
- File inventory: `file_inventory_analysis.md`
- Configuration analysis: `configuration_logging_analysis.md`

---

**If issues persist after following this guide, please collect diagnostic information and refer to the main project documentation for additional support options.**