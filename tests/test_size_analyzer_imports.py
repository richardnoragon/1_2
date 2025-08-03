#!/usr/bin/env python3
"""
Test Script for Size Analyzer Import Fixes

This script validates that all the import and execution issues for the 
size_analyzer.py file have been resolved when called from main.py.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path (same as main.py does)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic import functionality."""
    print("Testing basic imports...")
    
    try:
        # Test importing the main size analyzer module
        from src.utilities.analysis.size_analyzer import SizeAnalyzerGUI
        print("✓ Successfully imported SizeAnalyzerGUI from src.utilities.analysis.size_analyzer")
        
        # Test importing through the package structure
        from src.utilities.analysis import SizeAnalyzerGUI as SizeAnalyzerGUI2
        print("✓ Successfully imported SizeAnalyzerGUI through package structure")
        
        # Test importing core logic
        from src.utilities.analysis.core.size_analyzer_logic import SizeAnalyzer
        print("✓ Successfully imported SizeAnalyzer from core logic")
        
        # Test importing configuration
        from src.utilities.analysis.config.size_analyzer_config import SizeAnalyzerConfig
        print("✓ Successfully imported SizeAnalyzerConfig")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False

def test_class_instantiation():
    """Test that classes can be instantiated."""
    print("\nTesting class instantiation...")
    
    try:
        # Import PyQt5 first to ensure it's available
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test SizeAnalyzerGUI instantiation
        from src.utilities.analysis.size_analyzer import SizeAnalyzerGUI
        gui_instance = SizeAnalyzerGUI()
        print("✓ Successfully instantiated SizeAnalyzerGUI")
        
        # Test SizeAnalyzer core logic instantiation
        from src.utilities.analysis.core.size_analyzer_logic import SizeAnalyzer
        analyzer_instance = SizeAnalyzer()
        print("✓ Successfully instantiated SizeAnalyzer")
        
        # Test SizeAnalyzerConfig instantiation
        from src.utilities.analysis.config.size_analyzer_config import SizeAnalyzerConfig
        config_instance = SizeAnalyzerConfig()
        print("✓ Successfully instantiated SizeAnalyzerConfig")
        
        # Clean up
        if hasattr(gui_instance, 'close'):
            gui_instance.close()
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed during instantiation test: {e}")
        return False
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        return False

def test_main_py_import_strategies():
    """Test the import strategies used in main.py."""
    print("\nTesting main.py import strategies...")
    
    # Simulate the import strategies from main.py
    module_name = "src.utilities.analysis.size_analyzer"
    class_name = "SizeAnalyzerGUI"
    
    strategies_tested = 0
    successful_strategies = 0
    
    # Strategy 1: Direct module import
    try:
        module = __import__(module_name, fromlist=[class_name])
        tool_class = getattr(module, class_name)
        if tool_class:
            print("✓ Strategy 1 (Direct import) successful")
            successful_strategies += 1
        strategies_tested += 1
    except Exception as e:
        print(f"✗ Strategy 1 (Direct import) failed: {e}")
        strategies_tested += 1
    
    # Strategy 2: Absolute path import
    try:
        clean_module = module_name[4:] if module_name.startswith('src.') else module_name
        module = __import__(clean_module, fromlist=[class_name])
        tool_class = getattr(module, class_name)
        if tool_class:
            print("✓ Strategy 2 (Absolute path import) successful")
            successful_strategies += 1
        strategies_tested += 1
    except Exception as e:
        print(f"✗ Strategy 2 (Absolute path import) failed: {e}")
        strategies_tested += 1
    
    # Strategy 3: Dynamic import using importlib
    try:
        import importlib
        module_variations = [
            module_name,
            module_name.replace('src.', ''),
            f"src.{module_name}" if not module_name.startswith('src.') else module_name
        ]
        
        for module_path in module_variations:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, class_name):
                    tool_class = getattr(module, class_name)
                    if tool_class:
                        print("✓ Strategy 3 (Dynamic import) successful")
                        successful_strategies += 1
                        break
            except ImportError:
                continue
        strategies_tested += 1
    except Exception as e:
        print(f"✗ Strategy 3 (Dynamic import) failed: {e}")
        strategies_tested += 1
    
    print(f"Import strategies: {successful_strategies}/{strategies_tested} successful")
    return successful_strategies > 0

def test_package_structure():
    """Test that the package structure is properly set up."""
    print("\nTesting package structure...")
    
    try:
        # Test that __init__.py files are working
        import src
        print("✓ src package imports correctly")
        
        import src.utilities
        print("✓ src.utilities package imports correctly")
        
        import src.utilities.analysis
        print("✓ src.utilities.analysis package imports correctly")
        
        # Test that classes are exposed through __init__.py
        from src.utilities.analysis import get_available_classes
        available = get_available_classes()
        print(f"✓ Available classes: {available}")
        
        # Test validation function
        from src.utilities.analysis import validate_imports
        validation_result = validate_imports()
        print(f"✓ Import validation result: {validation_result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Package structure test failed: {e}")
        return False

def test_import_validator():
    """Test the import validator utility."""
    print("\nTesting import validator utility...")
    
    try:
        from src.utilities.analysis.import_validator import ImportValidator
        
        validator = ImportValidator()
        results = validator.validate_size_analyzer_imports()
        
        print(f"✓ Import validator created successfully")
        print(f"✓ Validation results: {results['success']}")
        
        if not results['success']:
            print("Validation errors found:")
            for error in results['errors']:
                print(f"  - {error}")
        
        # Test diagnostic report generation
        report = validator.generate_diagnostic_report()
        print("✓ Diagnostic report generated successfully")
        
        return results['success']
        
    except Exception as e:
        print(f"✗ Import validator test failed: {e}")
        return False

def test_circular_import_resolution():
    """Test that circular import issues have been resolved."""
    print("\nTesting circular import resolution...")
    
    try:
        # Test importing config without circular dependencies
        from src.utilities.analysis.config.size_analyzer_config import SizeAnalyzerConfig
        config = SizeAnalyzerConfig()
        print("✓ SizeAnalyzerConfig imports without circular dependency issues")
        
        # Test that the dynamic import functions work
        from src.utilities.analysis.config.size_analyzer_config import get_config_manager, get_log_manager
        
        config_manager_class = get_config_manager()
        log_manager_class = get_log_manager()
        
        print(f"✓ Dynamic config manager import: {config_manager_class is not None}")
        print(f"✓ Dynamic log manager import: {log_manager_class is not None}")
        
        return True
        
    except Exception as e:
        print(f"✗ Circular import resolution test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("=" * 60)
    print("COMPREHENSIVE SIZE ANALYZER IMPORT TEST")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Class Instantiation", test_class_instantiation),
        ("Main.py Import Strategies", test_main_py_import_strategies),
        ("Package Structure", test_package_structure),
        ("Import Validator", test_import_validator),
        ("Circular Import Resolution", test_circular_import_resolution)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Final report
    print("\n" + "=" * 60)
    print("FINAL TEST REPORT")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Size Analyzer import issues have been resolved.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Some issues may remain.")
        return False

def main():
    """Main function."""
    success = run_comprehensive_test()
    
    if success:
        print("\n✓ The Size Analyzer should now work correctly from main.py")
        print("✓ All import and execution issues have been resolved")
    else:
        print("\n✗ Some issues remain. Check the test output above for details.")
        print("✗ You may need to run additional fixes or check dependencies.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())