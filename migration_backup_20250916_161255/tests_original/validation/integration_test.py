#!/usr/bin/env python3
"""
PDF Utilities Integration Test Suite
Validates the integration of PDF utilities with the main RFU Hub
"""

import sys
import os
import traceback
from pathlib import Path


def test_configuration_integration():
    """Test configuration system integration"""
    print("🔧 Testing Configuration Integration...")
    try:
        # Test main configuration system
        sys.path.insert(0, 'core')
        from config_manager import ConfigManager
        main_config = ConfigManager()
        print("  ✅ Main configuration system loaded")
        
        # Test PDF configuration bridge
        sys.path.insert(0, 'pdf_utilities')
        from config_manager import ConfigManager as PDFConfigManager
        pdf_config = PDFConfigManager()
        print("  ✅ PDF configuration bridge loaded")
        
        # Test configuration access
        pdf_settings = main_config.get_setting('pdf_tools', {})
        print(f"  ✅ PDF settings accessible: {len(pdf_settings)} sections")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration integration failed: {e}")
        return False


def test_logging_integration():
    """Test logging system integration"""
    print("📝 Testing Logging Integration...")
    try:
        # Test main logging system
        sys.path.insert(0, 'core')
        from logging_manager import LoggingManager
        main_logger = LoggingManager()
        print("  ✅ Main logging system loaded")
        
        # Test PDF logging bridge
        sys.path.insert(0, 'pdf_utilities')
        from log_config import setup_logger
        pdf_logger = setup_logger('integration_test')
        print("  ✅ PDF logging bridge loaded")
        
        # Test logging functionality
        pdf_logger.info("Integration test log message")
        print("  ✅ PDF logging functionality working")
        
        return True
    except Exception as e:
        print(f"  ❌ Logging integration failed: {e}")
        return False


def test_pdf_modules_import():
    """Test PDF modules can be imported"""
    print("📦 Testing PDF Modules Import...")
    
    # List of critical PDF modules to test
    critical_modules = [
        'main',
        'extract_text', 
        'split',
        'merg',
        'view',
        'page_administration'
    ]
    
    success_count = 0
    total_count = len(critical_modules)
    
    # Add pdf_utilities to path for imports
    sys.path.insert(0, 'pdf_utilities')
    
    for module_name in critical_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module_name} import failed: {e}")
    
    print(f"  📊 Import Success Rate: {success_count}/{total_count}")
    return success_count == total_count


def test_hub_integration():
    """Test RFU Hub integration"""
    print("🏠 Testing Hub Integration...")
    try:
        # Test main hub can be imported
        import rfuhub
        print("  ✅ RFU Hub imported successfully")
        
        # Test RFUHub class exists
        hub_class = getattr(rfuhub, 'RFUHub', None)
        if hub_class:
            print("  ✅ RFUHub class found")
        else:
            print("  ❌ RFUHub class not found")
            return False
        
        # Test open_pdf_tools method exists
        if hasattr(hub_class, 'open_pdf_tools'):
            print("  ✅ open_pdf_tools method found")
        else:
            print("  ❌ open_pdf_tools method not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Hub integration test failed: {e}")
        return False


def test_file_structure():
    """Test file structure integrity"""
    print("📁 Testing File Structure...")
    
    required_files = [
        'rfuhub.py',
        'configuration.json',
        'pdf_utilities/main.py',
        'pdf_utilities/config_manager.py',
        'pdf_utilities/log_config.py',
        'pdf_utilities/extract_text_migrated.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"  ❌ Missing: {file_path}")
        else:
            print(f"  ✅ Found: {file_path}")
    
    if missing_files:
        print(f"  ❌ {len(missing_files)} required files missing")
        return False
    else:
        print("  ✅ All required files present")
        return True


def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting PDF Utilities Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration Integration", test_configuration_integration),
        ("Logging Integration", test_logging_integration),
        ("PDF Modules Import", test_pdf_modules_import),
        ("Hub Integration", test_hub_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print("⚠️  Some integration tests failed. Review output above.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)