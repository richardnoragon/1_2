#!/usr/bin/env python3
"""
Dependency Verification Script for RFU Project

This script checks that all required dependencies are properly installed
and can be imported.
"""

import sys
from typing import List, Tuple

def check_dependencies() -> List[Tuple[str, str, bool]]:
    """
    Check if all required dependencies can be imported.
    
    Returns:
        List of tuples containing (package_name, import_name, success)
    """
    dependencies = [
        # GUI Framework
        ("PyQt5", "PyQt5.QtWidgets", "QApplication"),
        ("PyQt5", "PyQt5.QtCore", "Qt"),
        
        # PDF Processing
        ("PyMuPDF", "fitz", "Document"),
        ("PyPDF2", "PyPDF2", "PdfReader"),
        ("PyPDF4", "PyPDF4", "PdfFileReader"),
        ("pikepdf", "pikepdf", "Pdf"),
        ("pdf2docx", "pdf2docx", "Converter"),
        ("reportlab", "reportlab.pdfgen.canvas", "Canvas"),
        
        # Image Processing
        ("Pillow", "PIL.Image", "Image"),
        ("opencv-python-headless", "cv2", "imread"),
        ("piexif", "piexif", "load"),
        
        # Data Processing
        ("pandas", "pandas", "DataFrame"),
        ("numpy", "numpy", "array"),
        ("lxml", "lxml", "etree"),
        
        # Office Documents
        ("openpyxl", "openpyxl", "Workbook"),
        ("python-docx", "docx", "Document"),
        
        # Compression & Archives
        ("py7zr", "py7zr", "SevenZipFile"),
        ("Brotli", "brotli", "compress"),
        ("pyzstd", "pyzstd", "compress"),
        
        # Security & Encryption
        ("cryptography", "cryptography.fernet", "Fernet"),
        ("pyAesCrypt", "pyAesCrypt", "encrypt"),
        ("pyOpenSSL", "OpenSSL", "SSL"),
        
        # System & Utilities
        ("psutil", "psutil", "Process"),
        ("Send2Trash", "send2trash", "send2trash"),
        ("watchdog", "watchdog.observers", "Observer"),
        ("chardet", "chardet", "detect"),
        ("filetype", "filetype", "guess"),
        ("mutagen", "mutagen", "File"),
        
        # Testing Framework
        ("pytest", "pytest", "main"),
        ("pytest-qt", "pytestqt", "qtbot"),
        ("pytest-cov", "pytest_cov", "plugin"),
        
        # Development Tools
        ("black", "black", "format_str"),
        ("flake8", "flake8", "api"),
        ("mypy", "mypy", "api"),
        
        # Web & Network
        ("pytesseract", "pytesseract", "image_to_string"),
        
        # Date & Time
        ("python-dateutil", "dateutil", "parser"),
        ("pytz", "pytz", "UTC"),
        
        # Misc Utilities
        ("PyYAML", "yaml", "load"),
        ("termcolor", "termcolor", "colored"),
        ("fire", "fire", "Fire"),
        ("click", "click", "command"),
    ]
    
    results = []
    
    for package_name, import_path, test_attr in dependencies:
        try:
            module = __import__(import_path, fromlist=[test_attr])
            if hasattr(module, test_attr):
                results.append((package_name, import_path, True))
                print(f"✓ {package_name} ({import_path}) - OK")
            else:
                results.append((package_name, import_path, False))
                print(f"✗ {package_name} ({import_path}) - Missing attribute: {test_attr}")
        except ImportError as e:
            results.append((package_name, import_path, False))
            print(f"✗ {package_name} ({import_path}) - Import Error: {e}")
        except Exception as e:
            results.append((package_name, import_path, False))
            print(f"✗ {package_name} ({import_path}) - Error: {e}")
    
    return results

def main():
    """Main function to run dependency checks."""
    print("=" * 60)
    print("RFU Project Dependency Verification")
    print("=" * 60)
    
    results = check_dependencies()
    
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"Summary: {successful}/{total} dependencies successfully imported")
    
    if successful == total:
        print("🎉 All dependencies are properly installed!")
        return 0
    else:
        failed = total - successful
        print(f"❌ {failed} dependencies failed to import")
        print("\nFailed dependencies:")
        for package_name, import_path, success in results:
            if not success:
                print(f"  - {package_name} ({import_path})")
        return 1

if __name__ == "__main__":
    sys.exit(main())