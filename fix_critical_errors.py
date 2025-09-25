#!/usr/bin/env python3
"""
Fix Critical Import and Syntax Errors

This script fixes the specific errors found by Flake8:
1. Missing PyQt5 imports
2. Missing standard library imports
3. Syntax errors from incomplete function definitions
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


def fix_missing_imports(file_path: str) -> Tuple[bool, List[str]]:
    """Fix missing imports in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
        return False, [f"Could not read file: {e}"]

    original_content = content
    changes = []
    lines = content.split("\n")

    # Track what imports we need to add
    imports_needed = set()

    # Check for undefined names and determine needed imports
    if (
        "QtWidgets." in content
        and "from PyQt5 import QtWidgets" not in content
        and "import PyQt5.QtWidgets" not in content
    ):
        imports_needed.add("from PyQt5 import QtWidgets")

    if (
        "QtCore." in content
        and "from PyQt5 import QtCore" not in content
        and "import PyQt5.QtCore" not in content
    ):
        imports_needed.add("from PyQt5 import QtCore")

    if (
        "QtGui." in content
        and "from PyQt5 import QtGui" not in content
        and "import PyQt5.QtGui" not in content
    ):
        imports_needed.add("from PyQt5 import QtGui")

    if "Qt." in content and "from PyQt5.QtCore import Qt" not in content:
        imports_needed.add("from PyQt5.QtCore import Qt")

    if (
        "datetime." in content
        and "import datetime" not in content
        and "from datetime import" not in content
    ):
        imports_needed.add("import datetime")

    if "os." in content and "import os" not in content:
        imports_needed.add("import os")

    if "time." in content and "import time" not in content:
        imports_needed.add("import time")

    if "io." in content and "import io" not in content:
        imports_needed.add("import io")

    if "fitz." in content and "import fitz" not in content:
        imports_needed.add("import fitz  # PyMuPDF")

    # Check for typing imports
    typing_patterns = [
        (r"\bTuple\[", "Tuple"),
        (r"\bList\[", "List"),
        (r"\bDict\[", "Dict"),
        (r"\bOptional\[", "Optional"),
        (r"\bUnion\[", "Union"),
        (r"\bAny\b", "Any"),
    ]

    typing_imports_needed = set()
    for pattern, import_name in typing_patterns:
        if re.search(pattern, content):
            typing_imports_needed.add(import_name)

    # Check if typing imports already exist
    existing_typing = set()
    for line in lines:
        if "from typing import" in line:
            imports = line.replace("from typing import", "").strip()
            for imp in imports.split(","):
                existing_typing.add(imp.strip())

    typing_imports_needed -= existing_typing

    if typing_imports_needed:
        if existing_typing:
            # Add to existing typing import
            for i, line in enumerate(lines):
                if "from typing import" in line:
                    current_imports = (
                        line.replace("from typing import", "")
                        .strip()
                        .rstrip(",")
                    )
                    new_imports = ", ".join(
                        sorted(
                            list(existing_typing) + list(typing_imports_needed)
                        )
                    )
                    lines[i] = f"from typing import {new_imports}"
                    changes.append(
                        f"Line {i+1}: Added {', '.join(typing_imports_needed)} to typing imports"
                    )
                    break
        else:
            imports_needed.add(
                f'from typing import {", ".join(sorted(typing_imports_needed))}'
            )

    # Find where to insert imports
    insert_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped.startswith("#!")
            or stripped.startswith("# -")
            or stripped.startswith('"""')
            or stripped.startswith("'''")
        ):
            continue
        if stripped.startswith('"""') and '"""' in stripped[3:]:
            # Single-line docstring
            insert_idx = i + 1
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            # Multi-line docstring - find the end
            quote = '"""' if stripped.startswith('"""') else "'''"
            for j in range(i + 1, len(lines)):
                if quote in lines[j]:
                    insert_idx = j + 1
                    break
        elif stripped and not stripped.startswith("#"):
            insert_idx = i
            break

    # Add missing imports
    if imports_needed:
        new_imports = sorted(list(imports_needed))
        for imp in reversed(
            new_imports
        ):  # Insert in reverse order so line numbers don't shift
            lines.insert(insert_idx, imp)
            changes.append(f"Line {insert_idx + 1}: Added import: {imp}")

        # Add a blank line after imports if not present
        if (
            insert_idx + len(new_imports) < len(lines)
            and lines[insert_idx + len(new_imports)].strip()
        ):
            lines.insert(insert_idx + len(new_imports), "")

    # Write changes if any
    modified = original_content != "\n".join(lines)

    if modified:
        new_content = "\n".join(lines)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True, changes
        except (PermissionError, OSError) as e:
            return False, [f"Error writing file: {e}"]

    return False, []


def fix_syntax_errors(file_path: str) -> Tuple[bool, List[str]]:
    """Fix basic syntax errors in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
        return False, [f"Could not read file: {e}"]

    original_content = content
    changes = []
    lines = content.split("\n")

    modified = False

    for i, line in enumerate(lines):
        original_line = line

        # Fix incomplete function definitions ending with ->
        if re.search(r"def\s+\w+.*->\s*$", line):
            # Function definition without return type, add None
            line = line.rstrip() + " None:"
            changes.append(f"Line {i+1}: Fixed incomplete function definition")

        # Fix incomplete function definitions ending with -> and whitespace
        elif re.search(r"def\s+\w+.*->\s*$", line.rstrip()):
            line = line.rstrip() + " None:"
            changes.append(f"Line {i+1}: Fixed incomplete function definition")

        if line != original_line:
            lines[i] = line
            modified = True

    # Write changes if any
    if modified:
        new_content = "\n".join(lines)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True, changes
        except (PermissionError, OSError) as e:
            return False, [f"Error writing file: {e}"]

    return False, []


def fix_files_with_errors():
    """Fix specific files that have known errors."""

    # Files with F821 (undefined name) errors - need import fixes
    import_error_files = [
        "src/archive_20250823_191555/hub_consolidated.py",
        "src/core_rfu/theme_security/theme_encryption.py",
        "src/cross_platform/network_validator.py",
        "src/file_explorer/core/pane_manager.py",
        "src/file_explorer/integration/keyboard_shortcuts_system.py",
        "src/file_explorer/integration/plugin_system_foundation.py",
        "src/file_explorer/ui/layout_implementations.py",
        "src/gui/common/standard_window.py",
        "src/gui/common/widgets.py",
        "src/hub.py",
        "src/tools/file_management/advanced_folders/engine/performance_benchmarks.py",
        "src/tools/file_management/advanced_folders/gui/accessibility_manager.py",
        "src/tools/network/network_connectivity_complex/gui/hub.py",
        "src/tools/pdf_tools/engines/conversion_engine.py",
        "src/tools/pdf_tools/pdf_basic_operations/split.py",
        "src/tools/pdf_tools/pdf_content_extraction/extract_metadata.py",
        "src/tools/pdf_tools/pdf_content_extraction/extract_tables_camelot.py",
        "src/tools/pdf_tools/pdf_security/encrypt.py",
        "src/tools/pdf_tools/pdf_view_analysis/view.py",
    ]

    # Files with E999 (syntax error) errors
    syntax_error_files = [
        "src/tools/file_management/advanced_folders/core/metadata_indexing_system.py",
        "src/tools/file_management/advanced_folders/core/search_cache.py",
        "src/tools/file_management/advanced_folders/gui/configuration_dialog.py",
        "src/tools/file_management/advanced_folders/gui/directory_browser.py",
        "src/tools/file_management/advanced_folders_legacy/core/metadata_indexing_system.py",
        "src/tools/file_management/advanced_folders_legacy/core/search_cache.py",
        "src/tools/file_management/advanced_folders_legacy/core/search_engine.py",
        "src/tools/system/system_cleanup_gui.py",
    ]

    total_fixed = 0

    print("Fixing import errors...")
    for file_path in import_error_files:
        if Path(file_path).exists():
            print(f"  Processing: {file_path}")
            fixed, changes = fix_missing_imports(file_path)
            if fixed:
                total_fixed += 1
                print(f"    ✅ Fixed with {len(changes)} changes")
                for change in changes[:3]:  # Show first 3 changes
                    print(f"      - {change}")
                if len(changes) > 3:
                    print(f"      ... and {len(changes) - 3} more changes")
            else:
                print(f"    ⚪ No changes needed")
        else:
            print(f"  ❌ File not found: {file_path}")

    print(f"\nFixing syntax errors...")
    for file_path in syntax_error_files:
        if Path(file_path).exists():
            print(f"  Processing: {file_path}")
            fixed, changes = fix_syntax_errors(file_path)
            if fixed:
                total_fixed += 1
                print(f"    ✅ Fixed with {len(changes)} changes")
                for change in changes:
                    print(f"      - {change}")
            else:
                print(f"    ⚪ No changes needed")
        else:
            print(f"  ❌ File not found: {file_path}")

    return total_fixed


def main():
    """Main function."""
    print("🔧 Fixing Critical Import and Syntax Errors")
    print("=" * 50)

    total_fixed = fix_files_with_errors()

    print(f"\n🎉 Complete! Fixed {total_fixed} files total.")
    print("\nNext steps:")
    print("- Run flake8 again to check for remaining errors")
    print("- Run your type checker to verify fixes")


if __name__ == "__main__":
    main()
