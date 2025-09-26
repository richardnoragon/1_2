# Python Virtual Environment Setup Guide

## Overview

This guide provides comprehensive instructions for setting up a Python virtual environment for this project, including automatic handling of corrupted requirements.txt files, cross-platform support, and thorough verification.

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the comprehensive setup script
python scripts/setup_venv.py

# Activate the environment (Windows)
scripts\activation_helpers\activate.bat

# Activate the environment (PowerShell)
scripts\activation_helpers\activate.ps1

# Activate the environment (Unix/Linux/macOS)
source scripts/activation_helpers/activate.sh

# Activate the environment (Fish shell)
source scripts/activation_helpers/activate.fish
```

### Manual Verification

```bash
# Verify the environment setup
python scripts/verify_environment.py

# Check installed packages
python -m pip list

# Test critical imports
python -c "import PyQt5, numpy, pandas, cryptography; print('All critical packages working!')"
```

## Detailed Setup Process

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **pip** (latest version)
- **Internet connection** for package downloads
- **Sufficient disk space** (at least 2GB for all dependencies)

#### Platform-Specific Requirements

**Windows:**
- Visual C++ Redistributable (for compiled packages)
- PowerShell 5.1+ (for PowerShell activation script)

**macOS:**
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (recommended): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3-dev python3-venv build-essential
```

**Linux (CentOS/RHEL/Fedora):**
```bash
sudo yum install python3-devel python3-venv gcc gcc-c++ make
# or for newer versions:
sudo dnf install python3-devel python3-venv gcc gcc-c++ make
```

### Step-by-Step Setup

#### 1. Check Python Installation

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip version
python -m pip --version
```

#### 2. Run Enhanced Setup Script

The enhanced setup script automatically handles:
- **System Requirements Validation**: Checks disk space, memory, build tools
- **Platform Detection**: Comprehensive Windows/macOS/Linux support
- **Network Connectivity**: Validates PyPI access before installation
- **Requirements Analysis**: Detects dependency conflicts before installation
- **Requirements.txt cleaning**: Fixes encoding issues automatically
- **Advanced Virtual Environment Creation**: Enhanced isolation and validation
- **Dependency Installation**: Progressive installation with conflict resolution
- **Environment Verification**: Comprehensive testing of all components
- **Cross-platform Activation Scripts**: Including Fish shell support

```bash
# Basic setup
python scripts/setup_venv.py

# Verbose output
python scripts/setup_venv.py --verbose

# Force recreation of existing environment
python scripts/setup_venv.py --force-recreate

# Only clean requirements.txt
python scripts/setup_venv.py --clean-only

# Only verify existing environment
python scripts/setup_venv.py --verify-only
```

#### 3. Activate Virtual Environment

Choose the appropriate activation method for your platform:

**Windows Command Prompt:**
```cmd
scripts\activation_helpers\activate.bat
```

**Windows PowerShell:**
```powershell
scripts\activation_helpers\activate.ps1
```

**Unix/Linux/macOS:**
```bash
source scripts/activation_helpers/activate.sh
```

**Fish Shell:**
```fish
source scripts/activation_helpers/activate.fish
```

**Manual Activation (if helpers don't work):**
```bash
# Windows
venv\Scripts\activate

# Unix/Linux/macOS
source venv/bin/activate
```

#### 4. Verify Installation

```bash
# Run comprehensive verification
python scripts/verify_environment.py

# Quick verification
python -c "import sys; print('Python:', sys.executable)"
python -c "import PyQt5; print('PyQt5: OK')"
python -c "import numpy; print('NumPy: OK')"
python -c "import pandas; print('Pandas: OK')"
```

## Enhanced Phase 2 Features

### Advanced System Detection

The enhanced setup system now includes comprehensive system detection and validation:

#### Platform Detection
- **Windows**: Detects Windows version, build number, and Visual Studio tools
- **macOS**: Identifies macOS version and Xcode Command Line Tools
- **Linux**: Determines distribution and available build tools

#### System Requirements Validation
- **Disk Space**: Checks available disk space (requires psutil if available)
- **Memory**: Validates available system memory
- **Network Connectivity**: Tests PyPI and package repository access
- **Build Tools**: Detects platform-specific compilation requirements

#### Dependency Analysis
- **Conflict Detection**: Identifies version conflicts before installation
- **Resolution Suggestions**: Provides automated conflict resolution recommendations
- **Package Validation**: Verifies package availability on PyPI
- **Installation Order**: Optimizes package installation sequence

### New Modules

#### [`venv_manager.py`](scripts/venv_manager.py:1)
Advanced virtual environment management with features:
- Environment snapshots and backups
- Enhanced isolation verification
- Performance monitoring
- Cross-platform path handling

#### [`platform_utils.py`](scripts/platform_utils.py:1)
Cross-platform utilities providing:
- Comprehensive platform detection
- System requirements validation
- Build tools detection
- Network connectivity testing

#### [`dependency_resolver.py`](scripts/dependency_resolver.py:1)
Dependency conflict resolution with:
- Version conflict detection
- Compatibility analysis
- Resolution suggestions
- Dependency tree visualization

### Enhanced Activation Scripts

The system now supports all major shells:
- **Windows**: Batch (`.bat`) and PowerShell (`.ps1`)
- **Unix/Linux**: Bash (`.sh`) and Fish (`.fish`)
- **Cross-platform**: Automatic detection and appropriate script selection

### Usage Examples

#### Verbose Setup with Analysis
```bash
python scripts/setup_venv.py --verbose
```

#### Dependency Analysis Only
```bash
python -c "
import sys; sys.path.append('scripts')
from dependency_resolver import DependencyResolver
import logging
resolver = DependencyResolver(logging.getLogger())
report = resolver.generate_resolution_report('requirements.txt')
print(report)
"
```

#### Platform Report
```bash
python -c "
import sys; sys.path.append('scripts')
from platform_utils import PlatformUtils
import logging
utils = PlatformUtils(logging.getLogger())
print(utils.create_platform_report())
"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Requirements.txt Encoding Issues

**Problem:** Extra spaces between characters in requirements.txt
```
b l a c k = = 2 5 . 1 . 0
```

**Solution:** The setup script automatically fixes this
```bash
python scripts/setup_venv.py --clean-only
```

#### 2. Python Version Compatibility

**Problem:** `Python version not compatible`

**Solution:**
- Install Python 3.7 or higher
- Use specific Python version: `python3.8 scripts/setup_venv.py --python-path python3.8`

#### 3. Permission Errors

**Problem:** `Permission denied during installation`

**Solutions:**
```bash
# Use user installation
python -m pip install --user -r requirements.txt

# Fix directory permissions (Unix/Linux)
sudo chown -R $USER:$USER ~/.local/lib/python*/site-packages/

# Run as administrator (Windows)
# Right-click Command Prompt -> "Run as administrator"
```

#### 4. Network/Download Issues

**Problem:** `Failed to download packages`

**Solutions:**
```bash
# Use different index
python -m pip install -r requirements.txt -i https://pypi.org/simple/

# Increase timeout
python -m pip install -r requirements.txt --timeout 300

# Use proxy (if behind corporate firewall)
python -m pip install -r requirements.txt --proxy http://proxy.company.com:8080
```

#### 5. Compilation Errors

**Problem:** `Failed building wheel for [package]`

**Windows Solutions:**
- Install Visual C++ Build Tools
- Use pre-compiled wheels: `python -m pip install --only-binary=all -r requirements.txt`

**macOS Solutions:**
- Install Xcode Command Line Tools: `xcode-select --install`
- Update macOS if needed

**Linux Solutions:**
- Install development packages: `sudo apt install python3-dev build-essential`

#### 6. PyQt5 Installation Issues

**Problem:** PyQt5 fails to install or import

**Solutions:**
```bash
# Try different PyQt5 version
python -m pip install PyQt5==5.15.7

# Use conda instead
conda install pyqt

# Install system PyQt5 (Linux)
sudo apt install python3-pyqt5
```

#### 7. Virtual Environment Activation Issues

**Problem:** Activation scripts don't work

**Solutions:**

**Windows PowerShell Execution Policy:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Unix/Linux Permissions:**
```bash
# Make script executable
chmod +x scripts/activation_helpers/activate.sh

# Use bash explicitly
bash scripts/activation_helpers/activate.sh
```

### Environment Verification Failures

If verification fails, check these common issues:

#### 1. Python Path Not Isolated
```bash
# Check Python path
python -c "import sys; print(sys.executable)"
# Should point to venv/Scripts/python.exe (Windows) or venv/bin/python (Unix)
```

#### 2. Missing Packages
```bash
# List installed packages
python -m pip list

# Install missing packages
python -m pip install [package_name]
```

#### 3. Import Errors
```bash
# Test specific imports
python -c "import numpy; print('NumPy version:', numpy.__version__)"
python -c "import PyQt5.QtWidgets; print('PyQt5 GUI: OK')"
```

## Advanced Configuration

### Custom Python Interpreter

```bash
# Use specific Python version
python scripts/setup_venv.py --python-path /usr/bin/python3.9

# Use Python from specific location
python scripts/setup_venv.py --python-path C:\Python39\python.exe
```

### Environment Variables

Set these environment variables for customization:

```bash
# Custom virtual environment name
export VENV_NAME=my_custom_venv

# Custom requirements file
export REQUIREMENTS_FILE=requirements-dev.txt

# Disable GUI tests during verification
export NO_GUI_TESTS=1
```

### Development Setup

For development work, you might want additional packages:

```bash
# Activate environment first
source venv/bin/activate  # Unix
# or
venv\Scripts\activate  # Windows

# Install development dependencies
python -m pip install pytest pytest-qt black flake8 mypy

# Install package in development mode (if setup.py exists)
python -m pip install -e .
```

## File Structure

After successful setup, your project structure will include:

```
project_root/
├── venv/                           # Virtual environment
│   ├── Scripts/                    # Windows executables
│   ├── bin/                        # Unix executables
│   ├── lib/                        # Installed packages
│   └── pyvenv.cfg                  # Environment configuration
├── scripts/
│   ├── setup_venv.py              # Enhanced main setup script
│   ├── venv_manager.py            # Advanced virtual environment operations
│   ├── platform_utils.py          # Cross-platform utilities
│   ├── dependency_resolver.py     # Dependency conflict detection
│   ├── requirements_cleaner.py    # Requirements file processor
│   ├── verify_environment.py      # Environment verification
│   └── activation_helpers/
│       ├── activate.bat           # Windows batch activation
│       ├── activate.ps1           # PowerShell activation
│       ├── activate.sh            # Unix shell activation
│       └── activate.fish          # Fish shell activation
├── requirements.txt               # Package dependencies
├── requirements.txt.backup       # Original requirements backup
└── venv_setup.log                # Setup process log
```

## Package Overview

The requirements.txt includes these major package categories:

### Development Tools
- **black**: Code formatter
- **flake8**: Linting tool
- **mypy**: Type checker
- **pytest**: Testing framework

### GUI Framework
- **PyQt5**: Cross-platform GUI toolkit
- **PyQt5-Qt5**: Qt5 binaries
- **PyQt5_sip**: SIP bindings

### Data Processing
- **numpy**: Numerical computing
- **pandas**: Data analysis
- **openpyxl**: Excel file handling

### File Operations
- **cryptography**: Encryption/decryption
- **lxml**: XML processing
- **Pillow**: Image processing
- **psutil**: System utilities

### PDF Tools
- **PyMuPDF**: PDF manipulation
- **PyPDF2/PyPDF4**: PDF processing
- **pdfkit**: PDF generation

### Compression
- **py7zr**: 7-Zip archives
- **pyzstd**: Zstandard compression
- **Brotli**: Brotli compression

## Maintenance

### Updating Dependencies

```bash
# Activate environment
source venv/bin/activate

# Update all packages
python -m pip list --outdated
python -m pip install --upgrade [package_name]

# Update requirements.txt
python -m pip freeze > requirements.txt
```

### Cleaning Environment

```bash
# Remove virtual environment
rm -rf venv  # Unix
rmdir /s venv  # Windows

# Recreate environment
python scripts/setup_venv.py --force-recreate
```

### Backup and Restore

```bash
# Backup current environment
python -m pip freeze > requirements-backup.txt

# Restore from backup
python -m pip install -r requirements-backup.txt
```

## Support

If you encounter issues not covered in this guide:

1. Check the setup log: `venv_setup.log`
2. Run verification with verbose output: `python scripts/verify_environment.py --verbose`
3. Check Python and pip versions: `python --version && python -m pip --version`
4. Ensure internet connectivity and proxy settings
5. Try recreating the environment: `python scripts/setup_venv.py --force-recreate`

For platform-specific issues, refer to the official Python documentation:
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)