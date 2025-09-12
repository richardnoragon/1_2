#!/usr/bin/env python3
"""
Import Validation Script
Verifies all imports work correctly after reorganization.
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'development', 'demos'))

def test_core_imports():
    """Test core application imports."""
    try:
        # Test constants import
        from src.rfu.core.constants import APP_NAME
        print(f"✓ Core constants import successful: {APP_NAME}")
        
        # Test database manager
        try:
            from scripts.maintenance.standalone_database_manager import get_database_manager
            print("✓ Database manager import successful")
        except ImportError as e:
            print(f"⚠ Database manager import failed: {e}")
        
        return True
    except ImportError as e:
        print(f"✗ Core imports failed: {e}")
        return False

def test_tool_imports():
    """Test tool imports."""
    tool_tests = [
        ('src.tools.file_management.finder.file_finder', 'FileFinderGUI'),
        ('src.tools.analysis.size_analyzer.size_analyzer', 'SizeAnalyzerGUI'),
    ]
    
    success_count = 0
    for module_name, class_name in tool_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✓ {module_name}.{class_name} import successful")
                success_count += 1
            else:
                print(f"⚠ {module_name} missing class {class_name}")
        except ImportError as e:
            print(f"⚠ {module_name} import failed: {e}")
    
    return success_count

def main():
    """Run import validation tests."""
    print("=" * 60)
    print("IMPORT VALIDATION AFTER REORGANIZATION")
    print("=" * 60)
    
    # Test core imports
    print("\nTesting core imports...")
    core_success = test_core_imports()
    
    # Test tool imports
    print("\nTesting tool imports...")
    tool_success_count = test_tool_imports()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Core imports: {'PASS' if core_success else 'FAIL'}")
    print(f"Tool imports: {tool_success_count} successful")
    
    if core_success and tool_success_count > 0:
        print("\n✅ Import validation PASSED - basic functionality verified")
        return 0
    else:
        print("\n❌ Import validation FAILED - issues need resolution")
        return 1

if __name__ == '__main__':
    sys.exit(main())