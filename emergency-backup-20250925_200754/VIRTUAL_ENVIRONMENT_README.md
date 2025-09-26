# Virtual Environment Setup - README

## Overview

A virtual Python environment has been successfully set up for the Richard's File Utilities (RFU) project.

## Environment Details

- **Python Version**: 3.13.5
- **Environment Type**: venv
- **Location**: `C:\Users\HP1\1_2\venv\`
- **Python Executable**: `C:\Users\HP1\1_2\venv\Scripts\python.exe`

## Packages Installed

All packages from `requirements.txt` have been installed except for `inflate64==1.0.1` which had compilation issues requiring Microsoft Visual C++ Build Tools. However, `inflate64-1.0.3` was automatically installed as a dependency and is working correctly.

### Key Packages

- **PyQt5 5.15.11** - GUI framework
- **pandas 2.2.3** - Data manipulation
- **numpy 2.2.4** - Numerical computing
- **PyMuPDF 1.25.4** - PDF processing
- **pikepdf 9.5.2** - PDF toolkit
- **PyPDF2 3.0.1** - PDF utilities
- **pytest 8.3.5** - Testing framework
- **cryptography 44.0.2** - Security operations
- **psutil 7.0.0** - System monitoring

## Activation Methods

### Option 1: PowerShell Script (Recommended)

```powershell
.\activate_env.ps1
```

### Option 2: Batch File (Command Prompt)

```cmd
activate_env.bat
```

### Option 3: Manual Activation

```powershell
.\venv\Scripts\Activate.ps1
```

## Running the Application

After activating the environment:

```bash
python main.py
```

## Running Tests

```bash
python -m pytest
```

## Environment Verification

Run the verification script to ensure everything is working:

```bash
python verify_environment.py
```

## Development Commands

With the environment activated, you can use:

- `python main.py` - Run the main application
- `python -m pytest` - Run all tests
- `python -m pytest tests/unit/` - Run unit tests only
- `black .` - Format code
- `flake8 .` - Lint code
- `mypy .` - Type checking

## Deactivation

To deactivate the virtual environment:

```bash
deactivate
```

## Notes

- The virtual environment is self-contained in the `venv` directory
- All dependencies are isolated from the system Python
- The environment can be recreated by running `python -m venv venv` and installing from `requirements.txt`
- If you encounter issues with `inflate64`, you may need to install Microsoft Visual C++ Build Tools

## File Structure

```
1_2/
├── venv/                   # Virtual environment
├── requirements.txt        # Package dependencies
├── requirements_no_inflate64.txt  # Modified requirements (used for installation)
├── activate_env.ps1       # PowerShell activation script
├── activate_env.bat       # Batch activation script
├── verify_environment.py  # Environment verification script
└── main.py                # Main application entry point
```
