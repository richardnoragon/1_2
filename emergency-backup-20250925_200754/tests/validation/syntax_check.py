"""Simple syntax validation for catalog.py"""

import ast
import sys


def check_syntax(filename):
    """Check if a Python file has valid syntax."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

        # Parse the AST to check syntax
        ast.parse(source)
        print(f"✓ {filename} has valid syntax")
        return True

    except SyntaxError as e:
        print(f"✗ Syntax error in {filename}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filename}: {e}")
        return False


def main():
    """Check syntax of key files."""
    files_to_check = ["file_utilities_1/catalog.py", "tests/test_catalog.py"]

    print("Syntax Validation")
    print("=" * 40)

    all_valid = True
    for filename in files_to_check:
        if not check_syntax(filename):
            all_valid = False

    print("=" * 40)
    if all_valid:
        print("✓ All files have valid syntax")
    else:
        print("✗ Some files have syntax errors")

    return all_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
