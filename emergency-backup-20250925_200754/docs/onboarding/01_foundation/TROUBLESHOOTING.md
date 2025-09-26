# Troubleshooting - Quick Solutions

> **Navigation**: [Main Hub](README.md) → **Troubleshooting**
> **Persona Fit**: All Users | **Complexity**: Beginner | **Time**: 1-3 minutes per issue
> **Prerequisites**: RFU installed

Quick solutions to the most common issues you might encounter with RFU. Most problems have simple fixes that take under 2 minutes.

## 🚀 **Installation Issues**

### RFU Won't Install

**Windows: "Windows protected your PC"**

- **Solution**: Click "More info" → "Run anyway"
- **Why**: Windows Defender doesn't recognize the publisher yet

**macOS: "Cannot be opened because it is from an unidentified developer"**

- **Solution**: Right-click RFU.app → "Open" → "Open" again
- **Alternative**: System Preferences → Security & Privacy → "Allow"

**Linux: "Permission denied"**

- **Solution**: `chmod +x RFU-v3.0.0.AppImage`
- **Why**: Downloaded files aren't executable by default

### RFU Won't Launch

**Nothing happens when clicking RFU icon**

- **Solution**: Right-click → "Run as Administrator" (Windows) or "Open" (macOS)
- **Check**: Available RAM (need 4GB+)

**Error message on startup**

- **Solution**: Check system requirements in [Getting Started](GETTING_STARTED.md#system-requirements)
- **Common fix**: Update graphics drivers (Windows)

## ⚡ **Performance Issues**

### Tools Are Slow

**File operations take forever**

- **Quick fix**: Start with smaller directories (< 1,000 files)
- **Add filters**: File type, date range, size limits
- **Avoid**: Network drives for learning/testing

**Interface is sluggish**

- **Check**: Close other applications (Chrome, video editors)
- **Setting**: File → Preferences → Performance → Reduce concurrent operations
- **Quick fix**: Restart RFU

### Out of Memory Errors

**"Insufficient memory" message**

- **Solution**: Process smaller batches (< 5,000 files at once)
- **Setting**: File → Preferences → Performance → Set memory limit
- **System**: Close browser tabs and other apps

## 🔧 **Operation Issues**

### Search Doesn't Find Files

**File Finder returns no results**

- **Check**: File permissions (can you open the folder in Explorer/Finder?)
- **Verify**: Search directory is correct
- **Try**: Different file type filter
- **Common**: Case-sensitive search terms

**Content search fails**

- **Limitation**: Only works with text-based files (Word, PDF, TXT)
- **Not supported**: Image files, encrypted files, system files
- **Solution**: Use filename search instead

### File Operations Fail

**"Access denied" or permission errors**

- **Solution**: Run RFU as Administrator (Windows) or use sudo (Linux)
- **Check**: File isn't open in another program
- **Verify**: You have write permission to destination folder

**Organization rules don't work**

- **Must do**: Use "Preview Changes" first
- **Check**: Pattern syntax (use %YEAR%, %MONTH%, etc.)
- **Verify**: Destination folder exists and is writable

### Tools Won't Launch

**Tool card shows ❌ error**

- **Quick fix**: Click the tool card → Check error message
- **Common**: Missing dependencies (restart RFU)
- **Reset**: Help → Reset Tool Status

**Green checkmark but nothing happens**

- **Solution**: Close tool window if already open
- **Check**: Windows taskbar for hidden window
- **Last resort**: File → Preferences → Reset Interface

## 📁 **File Access Issues**

### Can't Access Network Drives

**Network locations don't appear**

- **Windows**: Map network drive first (This PC → Map network drive)
- **macOS**: Connect to server first (Finder → Go → Connect to Server)
- **Linux**: Mount drive first (`sudo mount`)

**Network operations are slow**

- **Expected**: Network operations take 5-10x longer
- **Solution**: Copy files locally first, then process
- **Alternative**: Use RFU on the network server directly

### Files Disappear After Operations

**Organized files seem missing**

- **Check**: Tool created new folder structure (look for "Organized_" folders)
- **Review**: Operation log (Help → Show Recent Operations)
- **Solution**: Use File Finder to locate moved files

**Renamed files not where expected**

- **Common**: Pattern created subdirectories you didn't expect
- **Check**: Use File Finder to search for new names
- **Recovery**: Use Undo function if available

## 🔍 **Quick Diagnostic Steps**

### 1-Minute Health Check

1. **Check System Resources**:
   - Task Manager (Windows) / Activity Monitor (macOS)
   - Need: 4GB+ RAM available, < 80% CPU

2. **Verify RFU Status**:
   - Status bar should show "Ready"
   - All tool cards should show ✅

3. **Test Basic Operation**:
   - File Management → File Finder
   - Browse to Documents folder
   - Start simple search

### When Nothing Works

**Complete Reset Procedure** (2 minutes):

1. Close RFU completely
2. File → Preferences → Reset All Settings
3. Restart RFU
4. Try basic operation

**Still broken?**

- **Report**: Help → Report Issue (includes system info)
- **Community**: [GitHub Discussions](https://github.com/your-org/rfu/discussions)
- **Backup plan**: [Run from source](GETTING_STARTED.md#option-b-run-from-source-advanced)

## 💡 **Prevention Tips**

### Avoid Common Problems

- **Start small**: Test with 10-50 files before processing thousands
- **Use Preview**: Always preview changes before applying
- **Check space**: Ensure adequate disk space for operations
- **Backup important data**: Before major reorganization
- **Update regularly**: Check for RFU updates monthly

### Performance Best Practices

- **Close unused tools**: Don't keep 5+ tools open simultaneously
- **Process locally**: Avoid network drives for large operations
- **Filter smartly**: Use file type and date filters to reduce scope
- **Monitor resources**: Watch memory usage in status bar

---

## Next Steps

- **Continue Learning**: [Hub Overview](HUB_OVERVIEW.md)
- **Practice**: [Quick Wins](QUICK_WINS.md)
- **Get Help**: [Community Support](https://github.com/your-org/rfu/discussions)

## Related Documentation

- **See Also**: [Getting Started](GETTING_STARTED.md) | [Quick Wins](QUICK_WINS.md)
- **Deep Dive**: [System Requirements](GETTING_STARTED.md#system-requirements)

---

*Most issues have simple solutions. When in doubt, restart RFU and try a smaller test case first.*
