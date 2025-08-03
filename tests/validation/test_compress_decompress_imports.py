#!/usr/bin/env python3
"""
Test script for compress_decompress package import validation
"""

import sys
import traceback
from pathlib import Path

def test_compress_decompress_imports():
    """Test all compress_decompress import scenarios"""
    print('🔍 COMPRESS_DECOMPRESS PACKAGE IMPORT VALIDATION')
    print('=' * 60)
    
    # Add current directory to path
    sys.path.insert(0, '.')
    
    # Test 1: Direct module import
    print('📦 Testing direct module import...')
    try:
        from file_utilities_1.compress_decompress import CompressDecompressWindow
        print('✅ Direct module import: SUCCESS')
        print(f'   Class: {CompressDecompressWindow.__name__}')
        print(f'   Module: {CompressDecompressWindow.__module__}')
    except ImportError as e:
        print(f'❌ Direct module import: FAILED - {e}')
        traceback.print_exc()
    
    print()
    
    # Test 2: Package-level import
    print('📦 Testing package-level import...')
    try:
        from file_utilities_1 import CompressDecompressWindow
        print('✅ Package-level import: SUCCESS')
        print(f'   Class: {CompressDecompressWindow.__name__}')
        print(f'   Module: {CompressDecompressWindow.__module__}')
    except ImportError as e:
        print(f'❌ Package-level import: FAILED - {e}')
        traceback.print_exc()
    
    print()
    
    # Test 3: All package exports
    print('📦 Testing all package exports...')
    try:
        from file_utilities_1 import CatalogWindow, FileFinderWindow, EmptyFoldersWindow, CompressDecompressWindow
        print('✅ All package exports: SUCCESS')
        print(f'   CatalogWindow: {CatalogWindow.__name__}')
        print(f'   FileFinderWindow: {FileFinderWindow.__name__}')
        print(f'   EmptyFoldersWindow: {EmptyFoldersWindow.__name__}')
        print(f'   CompressDecompressWindow: {CompressDecompressWindow.__name__}')
    except ImportError as e:
        print(f'❌ All package exports: FAILED - {e}')
        traceback.print_exc()
    
    print()
    
    # Test 4: Class inheritance verification
    print('📦 Testing class inheritance...')
    try:
        from file_utilities_1 import CompressDecompressWindow
        from gui.common.base_window import BaseWindow
        
        if issubclass(CompressDecompressWindow, BaseWindow):
            print('✅ BaseWindow inheritance: CONFIRMED')
            print(f'   MRO: {[cls.__name__ for cls in CompressDecompressWindow.__mro__]}')
        else:
            print('❌ BaseWindow inheritance: MISSING')
            
    except Exception as e:
        print(f'❌ Inheritance verification: FAILED - {e}')
    
    print()
    
    # Test 5: UI path resolution verification
    print('📦 Testing UI path resolution...')
    try:
        # Check if UI file exists in the expected location
        expected_ui_path = Path('file_utilities_1') / 'compress_decompress.ui'
        if expected_ui_path.exists():
            print('✅ UI file location: CORRECT')
            print(f'   Path: {expected_ui_path}')
            print(f'   Size: {expected_ui_path.stat().st_size} bytes')
        else:
            print('❌ UI file location: MISSING')
            print(f'   Expected: {expected_ui_path}')
            
    except Exception as e:
        print(f'❌ UI path verification: FAILED - {e}')
    
    print()
    print('🎯 Package import validation completed!')

if __name__ == '__main__':
    test_compress_decompress_imports()