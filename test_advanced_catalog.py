#!/usr/bin/env python3
"""Test script for the Advanced File Catalog Generator.

This script tests the basic functionality of the advanced catalog generator
to ensure all components work together correctly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.rfu.tools.file_management.advanced_catalog.catalog_data_model import (
            FileEntry, CatalogData, SortCriteria, ColorScheme, FileType
        )
        print("✓ Data model imports successful")
        
        from src.rfu.tools.file_management.advanced_catalog.sorting_engine import SortingEngine
        print("✓ Sorting engine import successful")
        
        from src.rfu.tools.file_management.advanced_catalog.color_coding_engine import ColorCodingEngine
        print("✓ Color coding engine import successful")
        
        from src.rfu.tools.file_management.advanced_catalog.export_engine import (
            HTMLExporter, CSVExporter, JSONExporter
        )
        print("✓ Export engine imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_data_model():
    """Test the data model functionality."""
    print("\nTesting data model...")
    
    try:
        from src.rfu.tools.file_management.advanced_catalog.catalog_data_model import (
            FileEntry, CatalogData, SortCriteria, FileType
        )
        
        # Create a test file entry
        test_file = Path(__file__)
        entry = FileEntry.from_path(test_file)
        
        print(f"✓ Created file entry: {entry.name}")
        print(f"  Size: {entry.format_size()}")
        print(f"  Type: {entry.file_type.value}")
        print(f"  Size category: {entry.get_size_category().value}")
        print(f"  Date category: {entry.get_date_category().value}")
        print(f"  Alphabetical category: {entry.get_alphabetical_category().value}")
        
        # Create catalog data
        catalog = CatalogData()
        catalog.add_entry(entry)
        
        print(f"✓ Created catalog with {len(catalog.entries)} entries")
        print(f"  Total size: {catalog._format_size(catalog.statistics.total_size)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data model test failed: {e}")
        return False

def test_sorting():
    """Test the sorting functionality."""
    print("\nTesting sorting engine...")
    
    try:
        from src.rfu.tools.file_management.advanced_catalog.catalog_data_model import (
            FileEntry, SortCriteria, FileType
        )
        from src.rfu.tools.file_management.advanced_catalog.sorting_engine import SortingEngine
        from datetime import datetime
        
        # Create test entries
        entries = []
        test_files = [
            ("zebra.txt", 1000),
            ("apple.py", 5000),
            ("banana.jpg", 2000),
            ("cherry.mp4", 10000)
        ]
        
        for name, size in test_files:
            entry = FileEntry(
                path=Path(name),
                name=name,
                size=size,
                created_date=datetime.now(),
                modified_date=datetime.now(),
                accessed_date=datetime.now(),
                file_type=FileType.OTHER,
                extension=Path(name).suffix
            )
            entries.append(entry)
        
        # Test alphabetical sorting
        sorted_entries = SortingEngine.sort_alphabetical(entries)
        print(f"✓ Alphabetical sort: {[e.name for e in sorted_entries]}")
        
        # Test size sorting
        sorted_entries = SortingEngine.sort_by_size(entries)
        print(f"✓ Size sort: {[(e.name, e.size) for e in sorted_entries]}")
        
        # Test type sorting
        sorted_entries = SortingEngine.sort_by_type(entries)
        print(f"✓ Type sort: {[(e.name, e.file_type.value) for e in sorted_entries]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sorting test failed: {e}")
        return False

def test_color_coding():
    """Test the color coding functionality."""
    print("\nTesting color coding engine...")
    
    try:
        from src.rfu.tools.file_management.advanced_catalog.catalog_data_model import (
            FileEntry, SortCriteria, ColorScheme
        )
        from src.rfu.tools.file_management.advanced_catalog.color_coding_engine import ColorCodingEngine
        
        # Create test entry
        entry = FileEntry.from_path(Path(__file__))
        
        # Create color engine
        color_engine = ColorCodingEngine(ColorScheme.DEFAULT)
        
        # Assign colors
        color_engine.assign_colors([entry], SortCriteria.ALPHABETICAL)
        
        if entry.color_category:
            print(f"✓ Color assigned: {entry.color_category.color_hex}")
            print(f"  Category: {entry.color_category.category_name}")
            print(f"  Icon: {entry.color_category.icon}")
        else:
            print("✓ Color coding completed (no color assigned)")
        
        # Generate legend
        legend = color_engine.generate_legend(SortCriteria.ALPHABETICAL)
        print(f"✓ Generated legend with {len(legend)} categories")
        
        return True
        
    except Exception as e:
        print(f"✗ Color coding test failed: {e}")
        return False

def test_export():
    """Test the export functionality."""
    print("\nTesting export engines...")
    
    try:
        from src.rfu.tools.file_management.advanced_catalog.catalog_data_model import CatalogData
        from src.rfu.tools.file_management.advanced_catalog.export_engine import (
            HTMLExporter, CSVExporter, JSONExporter
        )
        
        # Create test catalog
        catalog = CatalogData()
        catalog.scan_directory(Path(__file__).parent, recursive=False)
        
        print(f"✓ Created test catalog with {len(catalog.entries)} files")
        
        # Test HTML export validation
        html_exporter = HTMLExporter()
        if html_exporter.validate_options():
            print("✓ HTML exporter validation passed")
        
        # Test CSV export validation
        csv_exporter = CSVExporter()
        if csv_exporter.validate_options():
            print("✓ CSV exporter validation passed")
        
        # Test JSON export validation
        json_exporter = JSONExporter()
        if json_exporter.validate_options():
            print("✓ JSON exporter validation passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Export test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Advanced File Catalog Generator - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_model,
        test_sorting,
        test_color_coding,
        test_export
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Advanced File Catalog Generator is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())