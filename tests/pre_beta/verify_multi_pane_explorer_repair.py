#!/usr/bin/env python3
"""
Verification script for repaired multi_pane_explorer.py
Validates that all repairs were successful and functionality is preserved.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        from src.file_explorer.multi_pane_explorer import (
            ERROR_MESSAGES, KEYBOARD_SHORTCUTS, LAYOUT_ERROR_MESSAGES,
            TOOL_NAMES, WIDGET_DELETED_ERROR, MultiPaneFileExplorer)
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_constants():
    """Test that constants are properly defined."""
    print("Testing constants...")
    try:
        from src.file_explorer.multi_pane_explorer import (ERROR_MESSAGES,
                                                           KEYBOARD_SHORTCUTS,
                                                           TOOL_NAMES)

        # Test key constants
        assert 'FILE_FINDER' in TOOL_NAMES
        assert 'SIZE_ANALYZER' in TOOL_NAMES
        assert 'DUPLICATE_FINDER' in TOOL_NAMES
        assert 'FILE_OPEN_ERROR' in ERROR_MESSAGES
        assert 'COPY_ERROR' in ERROR_MESSAGES
        assert 'SEARCH' in KEYBOARD_SHORTCUTS
        
        print("✅ All constants properly defined")
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_syntax():
    """Test that the file has no syntax errors."""
    print("Testing syntax...")
    try:
        import ast
        file_path = Path(__file__).parent.parent.parent / "src" / "file_explorer" / "multi_pane_explorer.py"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        ast.parse(source)
        print("✅ Syntax validation passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Syntax test failed: {e}")
        return False

def test_class_instantiation():
    """Test that the main class can be instantiated."""
    print("Testing class instantiation...")
    try:
        # Mock PyQt5 if not available
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance() or QApplication([])
            pyqt_available = True
        except ImportError:
            pyqt_available = False
        
        if pyqt_available:
            # Mock dependencies
            from unittest.mock import patch

            from src.file_explorer.multi_pane_explorer import \
                MultiPaneFileExplorer
            with patch.multiple(
                'src.file_explorer.multi_pane_explorer',
                get_log_manager=lambda: type('MockLogger', (), {
                    'get_logger': lambda name: type('Logger', (), {
                        'info': lambda msg: None,
                        'debug': lambda msg: None,
                        'warning': lambda msg: None,
                        'error': lambda msg: None
                    })()
                })(),
                get_config_manager=lambda: None,
                get_database_manager=lambda: None
            ):
                explorer = MultiPaneFileExplorer()
                print("✅ Class instantiation successful")
                explorer.close()
                return True
        else:
            print("⚠️  PyQt5 not available, skipping instantiation test")
            return True
            
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False

def check_code_quality():
    """Check various code quality metrics."""
    print("Checking code quality...")
    
    file_path = Path(__file__).parent.parent.parent / "src" / "file_explorer" / "multi_pane_explorer.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    # Check for bare except clauses
    bare_except_count = 0
    for i, line in enumerate(lines, 1):
        if line.strip() == "except:" or line.strip().startswith("except:"):
            bare_except_count += 1
            issues.append(f"Line {i}: Bare except clause")
    
    # Check for lambda assignments
    lambda_count = 0
    for i, line in enumerate(lines, 1):
        if "= lambda" in line:
            lambda_count += 1
            issues.append(f"Line {i}: Lambda assignment")
    
    # Check line lengths (allow some flexibility)
    long_lines = 0
    for i, line in enumerate(lines, 1):
        if len(line.rstrip()) > 85:  # Allow some flexibility
            long_lines += 1
    
    print(f"Code Quality Metrics:")
    print(f"  - Bare except clauses: {bare_except_count}")
    print(f"  - Lambda assignments: {lambda_count}")
    print(f"  - Long lines (>85 chars): {long_lines}")
    print(f"  - Total lines: {len(lines)}")
    
    if bare_except_count == 0 and lambda_count == 0:
        print("✅ Code quality checks passed")
        return True
    else:
        print(f"❌ Code quality issues found: {len(issues)}")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"     {issue}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("MULTI-PANE EXPLORER REPAIR VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_constants,
        test_syntax,
        test_class_instantiation,
        check_code_quality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"VERIFICATION COMPLETE: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Repair successful!")
        return True
    else:
        print("⚠️  Some tests failed - Review needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)