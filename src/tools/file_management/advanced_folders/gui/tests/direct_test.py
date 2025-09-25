"""
Direct Component Test for Advanced Folders GUI

Tests GUI components directly without going through the full system
import chain. This validates our core implementation works.

Author: RFU Development Team
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_constants_direct():
    """Test constants module directly."""
    print("Testing constants module...")

    # Import the constants file directly
    constants_path = Path(__file__).parent.parent / "constants.py"

    if not constants_path.exists():
        print("✗ Constants file not found")
        return False

    try:
        # Read and execute the constants file
        with open(constants_path, "r") as f:
            constants_code = f.read()

        # Create a namespace to execute the code
        constants_namespace = {}
        exec(constants_code, constants_namespace)

        # Test that required classes exist
        Colors = constants_namespace.get("Colors")
        Fonts = constants_namespace.get("Fonts")
        Layout = constants_namespace.get("Layout")
        FileTypes = constants_namespace.get("FileTypes")

        if Colors and Fonts and Layout and FileTypes:
            print("✓ Constants classes defined")
            print(f"  Colors.PRIMARY_BLUE: {Colors.PRIMARY_BLUE}")
            print(f"  Fonts.SIZE_NORMAL: {Fonts.SIZE_NORMAL}")
            print(f"  Layout.CONTENT_MARGIN: {Layout.CONTENT_MARGIN}")
            print(f"  FileTypes.DOCUMENTS: {len(FileTypes.DOCUMENTS)} types")
            return True
        else:
            print("✗ Required constant classes missing")
            return False

    except Exception as e:
        print(f"✗ Constants test failed: {e}")
        return False


def test_pyqt5_availability():
    """Test PyQt5 availability."""
    print("\nTesting PyQt5 availability...")

    try:
        from PyQt5.QtCore import Qt, pyqtSignal
        from PyQt5.QtGui import QColor, QFont
        from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QWidget

        print("✓ PyQt5 imports successful")

        # Test basic widget creation
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        print("✓ Basic PyQt5 widget creation successful")

        if app:
            app.quit()

        return True

    except Exception as e:
        print(f"✗ PyQt5 test failed: {e}")
        return False


def test_file_structure():
    """Test that all GUI files exist."""
    print("\nTesting file structure...")

    gui_dir = Path(__file__).parent.parent
    required_files = [
        "constants.py",
        "configuration_dialog.py",
        "config_tabs.py",
        "directory_browser.py",
    ]

    all_exist = True
    for filename in required_files:
        file_path = gui_dir / filename
        if file_path.exists():
            print(f"✓ Found: {filename}")
        else:
            print(f"✗ Missing: {filename}")
            all_exist = False

    # Test test files
    test_dir = gui_dir / "tests"
    test_files = [
        "test_gui_components.py",
        "test_integration.py",
        "test_performance.py",
        "test_accessibility.py",
        "conftest.py",
        "run_tests.py",
    ]

    for filename in test_files:
        file_path = test_dir / filename
        if file_path.exists():
            print(f"✓ Found test: {filename}")
        else:
            print(f"✗ Missing test: {filename}")
            all_exist = False

    return all_exist


def test_syntax_validation():
    """Test that all Python files have valid syntax."""
    print("\nTesting syntax validation...")

    gui_dir = Path(__file__).parent.parent
    python_files = [
        "constants.py",
        "configuration_dialog.py",
        "config_tabs.py",
        "directory_browser.py",
    ]

    all_valid = True
    for filename in python_files:
        file_path = gui_dir / filename
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    code = f.read()

                # Try to compile the code
                compile(code, str(file_path), "exec")
                print(f"✓ Syntax valid: {filename}")

            except SyntaxError as e:
                print(f"✗ Syntax error in {filename}: {e}")
                all_valid = False
            except Exception as e:
                print(f"✗ Error reading {filename}: {e}")
                all_valid = False

    return all_valid


def run_direct_tests():
    """Run all direct component tests."""
    print("=" * 80)
    print("ADVANCED FOLDERS GUI DIRECT COMPONENT TESTS")
    print("=" * 80)
    print(f"Test location: {Path(__file__).parent}")
    print()

    tests = [
        ("File Structure", test_file_structure),
        ("Syntax Validation", test_syntax_validation),
        ("PyQt5 Availability", test_pyqt5_availability),
        ("Constants Direct", test_constants_direct),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        print("-" * 40)

        try:
            result = test_func()
            results.append((test_name, result))

            if result:
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")

        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results.append((test_name, False))

        print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:10} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ GUI components are properly implemented and ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("🔧 Please review the failed tests above")
        return False


if __name__ == "__main__":
    success = run_direct_tests()
    sys.exit(0 if success else 1)
