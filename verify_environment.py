#!/usr/bin/env python3
"""
Environment Verification Script for Richard's File Utilities
Tests that all required packages are properly installed and functional.
"""

import importlib
import sys
from pathlib import Path


def test_imports():
    """Test critical package imports."""
    print("Testing critical package imports...")
    
    # Core packages
    try:
        import PyQt5
        from PyQt5.QtCore import PYQT_VERSION_STR
        print(f"✓ PyQt5 {PYQT_VERSION_STR}")
    except ImportError as e:
        print(f"✗ PyQt5: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✓ Pandas {pd.__version__}")
    except ImportError as e:
        print(f"✗ Pandas: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    # PDF processing packages
    try:
        import PyPDF2
        print("✓ PyPDF2")
    except ImportError as e:
        print(f"✗ PyPDF2: {e}")
    
    try:
        import pikepdf
        print("✓ pikepdf")
    except ImportError as e:
        print(f"✗ pikepdf: {e}")
    
    try:
        import pymupdf
        print("✓ PyMuPDF")
    except ImportError as e:
        print(f"✗ PyMuPDF: {e}")
    
    # Testing framework
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__}")
    except ImportError as e:
        print(f"✗ pytest: {e}")
    
    # Other important packages
    try:
        import cryptography
        print("✓ cryptography")
    except ImportError as e:
        print(f"✗ cryptography: {e}")
    
    try:
        import psutil
        print("✓ psutil")
    except ImportError as e:
        print(f"✗ psutil: {e}")
    
    return True

def test_project_structure():
    """Test that project structure is accessible."""
    print("\nTesting project structure...")
    
    # Add project paths
    project_root = Path(__file__).parent
    src_path = project_root / 'src'
    
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        print(f"✓ src directory found: {src_path}")
    else:
        print(f"✗ src directory not found: {src_path}")
        return False
    
    # Test main components
    try:
        from src.core.constants import APP_NAME
        print(f"✓ Core constants accessible")
    except ImportError as e:
        print(f"⚠ Core constants not accessible: {e}")
    
    return True

def main():
    """Main verification function."""
    print("=" * 60)
    print("Richard's File Utilities - Environment Verification")
    print("=" * 60)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test project structure
    structure_ok = test_project_structure()
    
    print("\n" + "=" * 60)
    if imports_ok and structure_ok:
        print("✓ Environment verification completed successfully!")
        print("The virtual environment is ready for development.")
    else:
        print("⚠ Some issues were found in the environment setup.")
        print("Please review the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()