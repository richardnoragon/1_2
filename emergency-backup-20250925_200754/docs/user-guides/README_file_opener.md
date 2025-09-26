# How to Use the File Opening Scripts

## Python Script (open_files_clean.py)

### Basic Usage:
```bash
# Open files from current directory
python open_files_clean.py

# Open files from specific directory
python open_files_clean.py "C:\path\to\directory"

# List files without opening them
python open_files_clean.py --list

# Set maximum number of files
python open_files_clean.py --max-files 30
```

## PowerShell Script (open_files.ps1)

### Basic Usage:
```powershell
# Open files from current directory
.\open_files.ps1

# Open files from specific directory
.\open_files.ps1 -Directory "C:\path\to\directory"

# List files without opening them
.\open_files.ps1 -ListOnly

# Set maximum number of files
.\open_files.ps1 -MaxFiles 30

# Combine options
.\open_files.ps1 -Directory ".\src" -MaxFiles 20 -ListOnly
```

## Features:

1. **Smart File Detection**: Only opens text files (based on extension and content analysis)
2. **Directory Filtering**: Skips common build/cache directories (.git, node_modules, __pycache__, etc.)
3. **Safety Limits**: Default maximum of 50 files to prevent overwhelming VS Code
4. **Confirmation**: Asks for confirmation when opening many files
5. **Preview Mode**: Use --list or -ListOnly to see what files would be opened

## Requirements:

- VS Code installed with 'code' command available in PATH
- Python 3.6+ (for Python script)
- PowerShell 5.0+ (for PowerShell script)