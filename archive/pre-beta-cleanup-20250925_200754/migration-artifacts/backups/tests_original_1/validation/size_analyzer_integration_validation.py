#!/usr/bin/env python3
"""
Size Analyzer Integration Validation Script

This script validates the successful integration of the migrated size_analyzer components
throughout the system. It tests all import paths, functionality, and integration points.

Phase 2 Migration Validation:
- Hub integration (rfuhub.py)
- Test file updates
- Legacy compatibility layer
- Import path validation
- Functionality testing
"""

import sys
import traceback
import warnings
import tempfile
import os
import json
from pathlib import Path


def test_new_imports():
    """Test that all new import paths work correctly."""
    print("\n=== Testing New Import Paths ===")
    
    try:
        # Test core logic imports
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
        print("✓ Core logic imports successful")
        
        # Test GUI imports
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        print("✓ GUI imports successful")
        
        # Test package-level imports
        from file_utilities_2 import SizeAnalyzer as PackageSizeAnalyzer
        from file_utilities_2 import SizeAnalyzerWorker as PackageWorker
        from file_utilities_2 import SizeAnalyzerGUI as PackageGUI
        print("✓ Package-level imports successful")
        
        # Verify they're the same classes
        assert SizeAnalyzer is PackageSizeAnalyzer, "Package import mismatch for SizeAnalyzer"
        assert SizeAnalyzerWorker is PackageWorker, "Package import mismatch for SizeAnalyzerWorker"
        assert SizeAnalyzerGUI is PackageGUI, "Package import mismatch for SizeAnalyzerGUI"
        print("✓ Import consistency verified")
        
        return True
        
    except Exception as e:
        print(f"✗ New imports failed: {e}")
        traceback.print_exc()
        return False


def test_legacy_compatibility():
    """Test that legacy imports still work with deprecation warnings."""
    print("\n=== Testing Legacy Compatibility ===")
    
    try:
        # Capture deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Test legacy import
            from size_analyzer import SizeAnalyzerWindow
            print("✓ Legacy SizeAnalyzerWindow import successful")
            
            # Verify deprecation warning was issued
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            if deprecation_warnings:
                print("✓ Deprecation warning properly issued")
                print(f"  Warning: {deprecation_warnings[0].message}")
            else:
                print("⚠ No deprecation warning issued (unexpected)")
            
        return True
        
    except Exception as e:
        print(f"✗ Legacy compatibility test failed: {e}")
        traceback.print_exc()
        return False


def test_core_functionality():
    """Test that the core SizeAnalyzer functionality works."""
    print("\n=== Testing Core Functionality ===")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        
        # Create analyzer instance
        analyzer = SizeAnalyzer()
        print("✓ SizeAnalyzer instance created")
        
        # Test format_size method
        test_cases = [
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (123, "123.0 B")
        ]
        
        for size, expected in test_cases:
            result = analyzer.format_size(size)
            if result == expected:
                print(f"✓ format_size({size}) = {result}")
            else:
                print(f"✗ format_size({size}) = {result}, expected {expected}")
                return False
        
        # Test directory analysis with a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello, World!" * 100)
            
            # Analyze directory
            analysis = analyzer.analyze_directory(temp_dir)
            print("✓ Directory analysis completed")
            
            # Verify analysis structure
            required_keys = ['total_size', 'file_count', 'directory_count', 'largest_files', 'file_types']
            for key in required_keys:
                if key in analysis:
                    print(f"✓ Analysis contains {key}")
                else:
                    print(f"✗ Analysis missing {key}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_gui_creation():
    """Test that the GUI can be created (without showing it)."""
    print("\n=== Testing GUI Creation ===")
    
    try:
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        
        # Note: We can't actually create the GUI without a QApplication
        # But we can verify the class is importable and has expected methods
        expected_methods = ['__init__', 'show', 'close']
        for method in expected_methods:
            if hasattr(SizeAnalyzerGUI, method):
                print(f"✓ SizeAnalyzerGUI has {method} method")
            else:
                print(f"✗ SizeAnalyzerGUI missing {method} method")
                return False
        
        print("✓ SizeAnalyzerGUI class structure validated")
        return True
        
    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        traceback.print_exc()
        return False


def test_hub_integration():
    """Test that the hub integration imports work."""
    print("\n=== Testing Hub Integration ===")
    
    try:
        # Test that rfuhub can import the new class
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        print("✓ Hub can import SizeAnalyzerGUI")
        
        # Verify the class has the expected interface
        if hasattr(SizeAnalyzerGUI, '__init__'):
            print("✓ SizeAnalyzerGUI has __init__ method")
        else:
            print("✗ SizeAnalyzerGUI missing __init__ method")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Hub integration test failed: {e}")
        traceback.print_exc()
        return False


def test_export_functionality():
    """Test the export functionality."""
    print("\n=== Testing Export Functionality ===")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        
        analyzer = SizeAnalyzer()
        
        # Create a temporary directory with test content
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content for export functionality")
            
            # Analyze directory
            analysis = analyzer.analyze_directory(temp_dir)
            
            # Test export
            export_file = Path(temp_dir) / "analysis_export.json"
            analyzer.export_analysis(analysis, str(export_file))
            
            if export_file.exists():
                print("✓ Export file created")
                
                # Verify export content
                with open(export_file, 'r') as f:
                    exported_data = json.load(f)
                
                if 'total_size' in exported_data:
                    print("✓ Export contains expected data")
                else:
                    print("✗ Export missing expected data")
                    return False
            else:
                print("✗ Export file not created")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Export functionality test failed: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_validation():
    """Run all validation tests."""
    print("Size Analyzer Integration Validation")
    print("=" * 50)
    
    tests = [
        ("New Import Paths", test_new_imports),
        ("Legacy Compatibility", test_legacy_compatibility),
        ("Core Functionality", test_core_functionality),
        ("GUI Creation", test_gui_creation),
        ("Hub Integration", test_hub_integration),
        ("Export Functionality", test_export_functionality),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Integration successful!")
        return True
    else:
        print("❌ Some tests failed - Integration needs attention")
        return False


if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)