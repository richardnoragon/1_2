"""
OCR Module Pandas API Compatibility Fix
ocr_pandas_fix_2025-09-01.py
Purpose: Fix pandas API compatibility issues in the OCR module
"""

import pandas as pd


def save_page_content_fixed(pdfContent, page_id, page_data):
    """
    Fixed version: Appends the content of a scanned page, line by line, to a pandas DataFrame.
    Uses pd.concat() instead of deprecated append() method.
    """
    if page_data:
        new_rows = []
        for idx, line in enumerate(page_data, 1):
            line_text = ' '.join(line)
            new_rows.append({
                'page': page_id, 
                'line_id': idx, 
                'line': line_text
            })
        
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            pdfContent = pd.concat([pdfContent, new_df], ignore_index=True)
    
    return pdfContent


def apply_pandas_fix_to_ocr_module():
    """Apply the pandas compatibility fix to the OCR module"""
    import os
    import sys

    # Import the OCR module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    
    try:
        from src.utilities.pdf_tools.pdf_enhancements import ocr

        # Replace the problematic function with the fixed version
        ocr.save_page_content_fixed = save_page_content_fixed
        
        print("✅ Pandas compatibility fix applied to OCR module")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import OCR module: {e}")
        return False


if __name__ == "__main__":
    apply_pandas_fix_to_ocr_module()