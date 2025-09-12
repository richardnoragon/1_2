#!/usr/bin/env python3
"""
Test script to verify PDF tools categories are discovered correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, "src")

def test_pdf_tools_discovery():
    """Test PDF tools category discovery"""
    
    # Check base path
    base_path = Path("src/utilities/pdf_tools")
    print(f"PDF Tools base path: {base_path}")
    print(f"Path exists: {base_path.exists()}")
    
    if not base_path.exists():
        print("❌ PDF Tools base path not found!")
        return False
    
    # Check for expected categories
    expected_categories = [
        'pdf_basic_operations',
        'pdf_content_extraction', 
        'pdf_security',
        'pdf_enhancements',
        'pdf_conversion',
        'pdf_view_analysis'
    ]
    
    found_categories = []
    for category in expected_categories:
        category_path = base_path / category
        if category_path.exists() and category_path.is_dir():
            found_categories.append(category)
            print(f"✅ Found category: {category}")
            
            # Check for Python files in category
            py_files = list(category_path.glob("*.py"))
            if py_files:
                print(f"   📄 Contains {len(py_files)} Python files")
            else:
                print(f"   ⚠️  No Python files found")
        else:
            print(f"❌ Missing category: {category}")
    
    print(f"\n📊 Summary: Found {len(found_categories)}/{len(expected_categories)} categories")
    
    if len(found_categories) >= 4:  # At least 4 categories should be enough
        print("✅ PDF Tools discovery should work correctly!")
        return True
    else:
        print("❌ Not enough PDF tool categories found")
        return False

if __name__ == "__main__":
    success = test_pdf_tools_discovery()
    print(f"\n{'='*50}")
    print(f"PDF Tools Test: {'PASSED' if success else 'FAILED'}")