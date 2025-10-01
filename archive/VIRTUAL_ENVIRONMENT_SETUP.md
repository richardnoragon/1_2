# Richard's File Utilities (RFU) - Virtual Environment Setup

This document outlines the comprehensive Python virtual environment configuration for the Richard's File Utilities project, including cross-platform compatibility and development environment setup.

## Virtual Environment Overview

- **Environment Name**: `venv`
- **Python Version**: 3.13.5
- **Location**: `./venv/` (relative to project root)
- **Platform**: Cross-platform (Windows, Linux, macOS)

## Quick Start

### Windows (PowerShell)

```powershell
.\activate_env.ps1
```

### Windows (Command Prompt)

```cmd
.\activate_env.bat
```

### Unix/Linux/macOS

```bash
./activate_env.sh
```

### Cross-platform (Python)

```bash
python activate_env.py
```

## Activation Scripts

The project includes multiple activation scripts for cross-platform compatibility:

### 1. `activate_env.bat` (Windows Batch)

- Windows Command Prompt and PowerShell compatible
- Provides informative messages about environment status
- Shows Python executable path and common commands

### 2. `activate_env.ps1` (PowerShell)

- Native PowerShell script with colored output
- Enhanced error handling and user feedback
- Cross-version PowerShell compatibility

### 3. `activate_env.sh` (Unix Shell)

- Bash-compatible shell script for Unix-like systems
- Works on Linux, macOS, and WSL
- Standard shell activation with informative messages

### 4. `activate_env.py` (Cross-platform Python)

- Platform detection and automatic script selection
- Fallback to direct activation if platform scripts unavailable
- Comprehensive error handling and user guidance

## Project Configuration Files

### pyproject.toml

Modern Python project configuration with:

- Build system configuration using setuptools
- Complete project metadata and dependencies
- Development tool configurations (Black, Flake8, MyPy, Pytest)
- Virtual environment path specification
- Cross-platform compatibility settings

### setup.py

Backward-compatible setup script with:

- Virtual environment path detection
- Automatic requirements.txt integration
- Entry point configuration
- Cross-platform path handling

### requirements.txt

Core project dependencies excluding problematic packages requiring build tools.

## VS Code Integration

### Settings (.vscode/settings.json)

- Python interpreter path: `./venv/Scripts/python.exe` (Windows)
- Automatic environment activation
- Testing framework configuration (Pytest)
- Linting and formatting setup (Flake8, MyPy, Black)
- Path and environment variable configuration

### Launch Configuration (.vscode/launch.json)

- Main application debugging
- Current file debugging
- Test running configurations
- Environment variable setup

### Tasks Configuration (.vscode/tasks.json)

- Virtual environment activation
- Dependency installation
- Testing with coverage
- Code formatting and linting
- Application launching

## Environment Variables (.env)

```env
PYTHONPATH=./src
DEVELOPMENT=true
DEBUG=true
VIRTUAL_ENV=./venv
RFU_CONFIG_PATH=./config
RFU_LOG_LEVEL=INFO
RFU_DATA_PATH=./data
```

## Git Integration

### .gitignore

Comprehensive exclusion patterns for:

- Virtual environment directories (`venv/`, `.venv/`, etc.)
- Python cache files and bytecode
- IDE-specific files
- Test artifacts and coverage reports
- OS-specific temporary files
- Application-specific cache and config files

## Package Management

### Installed Core Packages

- **GUI Framework**: PyQt5 (5.15.11)
- **Development Tools**: Black, Flake8, MyPy
- **Testing**: Pytest, Pytest-cov, Pytest-qt
- **Data Processing**: Pandas, NumPy
- **File Operations**: Pillow, OpenCV, python-docx
- **Encryption**: cryptography, pyAesCrypt
- **Utilities**: watchdog, psutil, Send2Trash

### Package Installation Commands

```bash
# Install from requirements
./venv/Scripts/pip install -r requirements.txt

# Install development dependencies
./venv/Scripts/pip install -e ".[dev]"

# Install test dependencies
./venv/Scripts/pip install -e ".[test]"
```

## Development Workflow

### 1. Environment Activation

Choose the appropriate activation script for your platform:

- Windows: `.\activate_env.ps1` or `.\activate_env.bat`
- Unix: `./activate_env.sh`
- Cross-platform: `python activate_env.py`

### 2. Development Commands

```bash
# Format code
python -m black src/ tests/ --line-length=79

# Lint code
python -m flake8 src/ tests/

# Type checking
python -m mypy src/

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html -v

# Run main application
python src/rfu/main.py
```

### 3. Package Management

```bash
# Add new dependency
./venv/Scripts/pip install package_name
./venv/Scripts/pip freeze > requirements.txt

# Update dependencies
./venv/Scripts/pip install --upgrade -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **PowerShell Execution Policy**

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Missing Build Tools (for packages requiring compilation)**

   - Install Microsoft C++ Build Tools
   - Use pre-compiled wheels when available
   - Consider alternative packages

3. **Path Issues**
   - Ensure scripts have executable permissions on Unix systems
   - Use absolute paths if relative paths fail
   - Check PYTHONPATH environment variable

### Verification Commands

```bash
# Check Python executable
python -c "import sys; print(sys.executable)"

# Verify virtual environment
python -c "import sys; print('Virtual env:', sys.prefix != sys.base_prefix)"

# List installed packages
pip list

# Check package installation
python -c "import PyQt5; print('PyQt5 version:', PyQt5.Qt.PYQT_VERSION_STR)"
```

## Cross-Platform Compatibility

### Windows

- Native batch file support (`.bat`)
- PowerShell script support (`.ps1`)
- Windows-specific paths and separators
- PATH environment variable handling

### Unix/Linux/macOS

- Shell script support (`.sh`)
- Unix-style paths and permissions
- Environment variable export syntax
- Standard Unix tools integration

### Universal

- Python-based activation script
- Platform detection and adaptation
- Fallback mechanisms for missing tools
- Consistent user experience across platforms

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Monthly pip upgrade cycle
2. **Security Scanning**: Review for vulnerable packages
3. **Testing**: Ensure cross-platform functionality
4. **Documentation**: Keep setup instructions current

### Environment Recreation

```bash
# Remove existing environment
rm -rf venv/  # Unix
Remove-Item -Recurse -Force venv  # PowerShell

# Recreate environment
python -m venv venv
# Follow activation and installation steps
```

This virtual environment setup ensures robust, cross-platform development capability with comprehensive tooling integration and clear maintenance procedures.
