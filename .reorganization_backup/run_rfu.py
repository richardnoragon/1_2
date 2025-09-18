#!/usr/bin/env python3
"""
RFU Application Launcher

This script properly configures the Python path and launches the RFU application.
It also creates missing core structure if needed.
"""

import sys
import os
from pathlib import Path

# Create missing src/core structure if it doesn't exist
def create_core_structure():
    """Create the missing src/core structure"""
    core_dir = Path("src/core")
    if not core_dir.exists():
        print("Creating missing src/core structure...")
        core_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = core_dir / "__init__.py"
        init_content = '''"""
Core constants and configuration for Richard's File Utilities.
"""

from .constants import (
    APP_NAME, JSON_FILES_FILTER, IMPORT_ERROR, SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER
)

__all__ = [
    "APP_NAME", "JSON_FILES_FILTER", "IMPORT_ERROR", "SECURITY_TEST",
    "SUGGESTED_SOLUTIONS_HEADER"
]
'''
        init_file.write_text(init_content, encoding='utf-8')
        
        # Create constants.py
        constants_file = core_dir / "constants.py"
        constants_content = '''"""
Constants for Richard's File Utilities Main Application.
"""

# Application Identity
APP_NAME = "Richard's File Utilities"

# File Dialog Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"

# Error Messages
IMPORT_ERROR = "Import Error"
SECURITY_TEST = "Security Test"

# UI Headers
SUGGESTED_SOLUTIONS_HEADER = "Suggested Solutions"

# Version Information
APP_VERSION = "3.0.0"
APP_ORGANIZATION = "Richard's File Utilities"
'''
        constants_file.write_text(constants_content, encoding='utf-8')
        print(f"✓ Created {core_dir}")
        print(f"✓ Created {init_file}")
        print(f"✓ Created {constants_file}")
        return True
    return False

# Create core structure before importing
created = create_core_structure()

# Get the project root directory
project_root = Path(__file__).parent
src_dir = project_root / "src"

# Add src directory to Python path
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now import and run the main application
if __name__ == "__main__":
    try:
        # Import the main function from src.main
        from src.main import main
        
        # Run the application
        exit_code = main()
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Src directory exists: {src_dir.exists()}")
        print(f"RFU module exists: {(src_dir / 'rfu').exists()}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)