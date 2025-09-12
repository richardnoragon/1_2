# VS Code File Opener - Updated for VS Code Insiders

The `open_files_clean.py` script has been updated to support **VS Code Insiders**.

## New Usage Examples:

### For VS Code Insiders Users:
```bash
# Open files in VS Code Insiders (prioritizes code-insiders command)
python open_files_clean.py --insiders

# Open specific directory in VS Code Insiders
python open_files_clean.py src --insiders --max-files 20

# List files without opening (great for testing)
python open_files_clean.py --insiders --list --max-files 10
```

### For Regular VS Code Users:
```bash
# Open files in regular VS Code (default behavior)
python open_files_clean.py

# Open with custom limits
python open_files_clean.py --max-files 15
```

## How It Works:

1. **With `--insiders` flag**: 
   - First tries `code-insiders` command
   - Falls back to `code` if Insiders not found

2. **Without `--insiders` flag** (default):
   - First tries `code` command  
   - Falls back to `code-insiders` if regular VS Code not found

3. **Smart Fallback**: Always tries both commands so it works regardless of which version you have installed

## Command Options:

- `--insiders` - Prefer VS Code Insiders over regular VS Code
- `--max-files N` - Limit number of files (default: 50)
- `--list` - Show files that would be opened without actually opening them

## Examples:

```bash
# Test what files would be opened in VS Code Insiders
python open_files_clean.py . --insiders --list

# Open all Python files in src folder using VS Code Insiders
python open_files_clean.py src --insiders --max-files 25

# Quick test with just 5 files
python open_files_clean.py --insiders --max-files 5
```

The script will automatically detect which version of VS Code you have installed and use the appropriate command!