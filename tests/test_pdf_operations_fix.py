#!/usr/bin/env python3
"""
Test script to verify PDF operations are working correctly
"""

import sys
import os

def test_pymupdf_import():
    """Test that PyMuPDF can be imported"""
    try:
        import fitz
        print("✓ PyMuPDF (fitz) imported successfully")
        print(f"  Version: {fitz.version}")
        return True
    except ImportError as e:
        print(f"✗ PyMuPDF import failed: {e}")
        return False

def test_pdf_operations():
    """Test that our PDF operations work"""
    try:
        import fitz
        
        # Test creating a simple PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Test PDF for operations")
        
        test_file = "test_operations.pdf"
        doc.save(test_file)
        doc.close()
        
        print(f"✓ Created test PDF: {test_file}")
        
        # Test opening and reading the PDF
        doc = fitz.open(test_file)
        print(f"✓ Opened PDF successfully - {len(doc)} pages")
        doc.close()
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"✗ PDF operations test failed: {e}")
        return False

def test_enhanced_pdf_widget():
    """Test that the enhanced PDF widget can be imported"""
    try:
        from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
        print("✓ Enhanced PDF Tools Widget imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Enhanced PDF Tools Widget import failed: {e}")
        return False

def main():
    print("Testing PDF Operations Fix...")
    print("=" * 50)
    
    tests = [
        test_pymupdf_import,
        test_pdf_operations,
        test_enhanced_pdf_widget
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("PDF operations should now work correctly!")
    else:
        print(f"✗ Some tests failed ({passed}/{total})")
        print("There may still be issues with PDF operations.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
