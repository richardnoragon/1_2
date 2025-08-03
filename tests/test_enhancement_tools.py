#!/usr/bin/env python3
"""
Test enhancement tools directly
"""

import sys
import os

# Add the enhancement tools to path
sys.path.append(
    os.path.join(os.path.dirname(__file__), 
                'src', 'utilities', 'pdf_tools', 'pdf_enhancements')
)

def test_watermark_import():
    try:
        from watermark import add_watermark
        print("✓ Watermark module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import watermark: {e}")
        return False

def test_ocr_import():
    try:
        from ocr import ocr_file
        print("✓ OCR module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import OCR: {e}")
        return False

def test_highlight_import():
    try:
        from highlight import process_data, remove_highlght
        print("✓ Highlight module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import highlight: {e}")
        return False

if __name__ == "__main__":
    print("Testing enhancement tool imports:")
    print("-" * 40)
    
    watermark_ok = test_watermark_import()
    ocr_ok = test_ocr_import()
    highlight_ok = test_highlight_import()
    
    print("-" * 40)
    if watermark_ok and ocr_ok and highlight_ok:
        print("✓ All enhancement tools available!")
        print("\nThe functional implementations should now work in the RFU hub.")
    else:
        print("✗ Some enhancement tools are not available")
        print("Check the file paths and dependencies.")
