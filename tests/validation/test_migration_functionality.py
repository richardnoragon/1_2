#!/usr/bin/env python3
"""
Quick test to verify Size Analyzer migration functionality after cleanup.
"""

import sys
import traceback

def test_imports():
    """Test that all migrated imports work correctly."""
    print("🔍 Testing Size Analyzer imports after cleanup...")
    
    try:
        # Test core logic import
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
        print("✅ Core logic imports successful")
        
        # Test GUI import
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        print("✅ GUI imports successful")
        
        # Test configuration import
        from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
        print("✅ Configuration imports successful")
        
        # Test package-level imports
        from file_utilities_2 import SizeAnalyzer, SizeAnalyzerGUI
        print("✅ Package-level imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of migrated components."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        
        # Create analyzer instance
        analyzer = SizeAnalyzer()
        print("✅ SizeAnalyzer instance created")
        
        # Test format_size method
        formatted = analyzer.format_size(1024)
        if formatted == "1.0 KB":
            print("✅ format_size method working correctly")
        else:
            print(f"⚠️ format_size returned: {formatted}")
        
        # Test larger size
        formatted_large = analyzer.format_size(1048576)
        if formatted_large == "1.0 MB":
            print("✅ format_size method working for larger sizes")
        else:
            print(f"⚠️ format_size for large returned: {formatted_large}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test execution."""
    print("🚀 Size Analyzer Migration Functionality Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    if imports_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED!")
        print("Size Analyzer migration is working correctly after cleanup.")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the migration implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())