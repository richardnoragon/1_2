#!/usr/bin/env python3
"""
Enhanced Type Error Fixer

This script specifically targets the type errors shown in VS Code:
- reportAssignmentType errors
- Missing Optional imports
- Path | None -> Optional[Path] conversions
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple


def fix_type_assignment_errors(file_path: str) -> Tuple[bool, List[str]]:
    """Fix type assignment errors in a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
        return False, [f"Could not read file: {e}"]

    original_content = content
    changes = []
    lines = content.split("\n")

    # Check if we need Optional import
    needs_optional = False
    has_optional_import = False

    # Check existing imports
    for line in lines:
        if "from typing import" in line and "Optional" in line:
            has_optional_import = True
        elif line.strip().startswith("from typing import"):
            if "Optional" in line:
                has_optional_import = True

    modified = False

    # Process each line
    for i, line in enumerate(lines):
        original_line = line

        # Fix function return type annotations: def func() -> Path | None:
        func_return_pattern = r"(\w+\([^)]*\)\s*->\s*)Path\s*\|\s*None(\s*:)"
        if re.search(func_return_pattern, line):
            line = re.sub(func_return_pattern, r"\1Optional[Path]\2", line)
            needs_optional = True
            changes.append(
                f"Line {i+1}: Fixed function return type Path | None -> Optional[Path]"
            )

        # Fix variable type annotations: var: Path | None = ...
        var_annotation_pattern = r"(\w+\s*:\s*)Path\s*\|\s*None(\s*=)"
        if re.search(var_annotation_pattern, line):
            line = re.sub(var_annotation_pattern, r"\1Optional[Path]\2", line)
            needs_optional = True
            changes.append(
                f"Line {i+1}: Fixed variable annotation Path | None -> Optional[Path]"
            )

        # Fix parameter type annotations: def func(param: Path | None):
        param_pattern = r"(\w+\s*:\s*)Path\s*\|\s*None(\s*[,)])"
        if re.search(param_pattern, line):
            line = re.sub(param_pattern, r"\1Optional[Path]\2", line)
            needs_optional = True
            changes.append(
                f"Line {i+1}: Fixed parameter annotation Path | None -> Optional[Path]"
            )

        # Fix str | None patterns
        str_patterns = [
            (
                r"(\w+\([^)]*\)\s*->\s*)str\s*\|\s*None(\s*:)",
                "function return",
            ),
            (r"(\w+\s*:\s*)str\s*\|\s*None(\s*=)", "variable annotation"),
            (r"(\w+\s*:\s*)str\s*\|\s*None(\s*[,)])", "parameter annotation"),
        ]

        for pattern, desc in str_patterns:
            if re.search(pattern, line):
                line = re.sub(pattern, r"\1Optional[str]\2", line)
                needs_optional = True
                changes.append(
                    f"Line {i+1}: Fixed {desc} str | None -> Optional[str]"
                )

        if line != original_line:
            lines[i] = line
            modified = True

    # Add Optional import if needed
    if needs_optional and not has_optional_import:
        # Find the best place to add the import
        import_added = False

        # Look for existing typing imports to extend
        for i, line in enumerate(lines):
            if line.strip().startswith("from typing import"):
                # Extend existing import
                import_items = line.replace("from typing import", "").strip()
                if not import_items.endswith(","):
                    import_items += ","
                lines[i] = f"from typing import {import_items} Optional"
                changes.append(
                    f"Line {i+1}: Added Optional to existing typing import"
                )
                import_added = True
                break

        if not import_added:
            # Find first non-comment, non-docstring line to insert import
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (
                    stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith('"""')
                    and not stripped.startswith("'''")
                ):
                    insert_idx = i
                    break

            lines.insert(insert_idx, "from typing import Optional")
            changes.append(
                f"Line {insert_idx+1}: Added 'from typing import Optional'"
            )
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


def fix_specific_files():
    """Fix specific files that we know have errors."""

    # List of files with errors from VS Code output
    error_files = [
        "src/cross_platform/network_validator.py",
        "src/tools/file_management/advanced_folders_legacy/core/file_system_scanner.py",
        "src/tools/file_management/advanced_folders_legacy/core/metadata_pipeline.py",
        "src/tools/file_management/advanced_folders_legacy/core/search_cache.py",
        "src/tools/file_management/advanced_folders_legacy/core/search_engine.py",
    ]

    total_fixed = 0

    for rel_path in error_files:
        file_path = Path(rel_path)
        if file_path.exists():
            print(f"\nProcessing: {file_path}")
            fixed, changes = fix_type_assignment_errors(str(file_path))

            if fixed:
                total_fixed += 1
                print(f"  ✅ Fixed with {len(changes)} changes:")
                for change in changes[:5]:  # Show first 5 changes
                    print(f"    - {change}")
                if len(changes) > 5:
                    print(f"    ... and {len(changes) - 5} more changes")
            else:
                print(f"  ⚪ No changes needed")
        else:
            print(f"  ❌ File not found: {file_path}")

    return total_fixed


def scan_and_fix_all():
    """Scan all Python files and fix type errors."""

    src_path = Path("src")
    if not src_path.exists():
        print("Source directory not found!")
        return 0

    total_fixed = 0
    total_scanned = 0

    print("Scanning all Python files for type errors...")

    for py_file in src_path.rglob("*.py"):
        # Skip certain directories
        if any(
            part.startswith(".") or part in ["__pycache__", "migrations"]
            for part in py_file.parts
        ):
            continue

        total_scanned += 1

        try:
            fixed, changes = fix_type_assignment_errors(str(py_file))
            if fixed:
                total_fixed += 1
                rel_path = py_file.relative_to(Path.cwd())
                print(f"✅ Fixed {rel_path} ({len(changes)} changes)")

        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")

    print(f"\nScanned {total_scanned} files, fixed {total_fixed} files")
    return total_fixed


def main():
    """Main function."""
    print("🔧 Enhanced Type Error Fixer")
    print("=" * 40)

    # First try to fix specific known problematic files
    print("1. Fixing specific known problematic files...")
    fixed_specific = fix_specific_files()

    # Then scan and fix all files
    print("\n2. Scanning all Python files...")
    fixed_all = scan_and_fix_all()

    total_fixed = fixed_specific + fixed_all

    print(f"\n🎉 Complete! Fixed {total_fixed} files total.")
    print("\nNext steps:")
    print("- Run your linter/type checker to verify fixes")
    print("- Test the application to ensure functionality is preserved")


if __name__ == "__main__":
    main()
