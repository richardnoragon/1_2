#!/usr/bin/env python3
"""
Automatic Type Error Fixer

This script fixes common type errors in the codebase:
1. Path | None type annotations (use Optional[Path] instead)
2. Missing type imports
3. Common Union type issues
4. Missing Optional imports
"""

import os
import re
from pathlib import Path
from typing import Dict, List


def fix_file_type_errors(file_path: str) -> bool:
    """Fix type errors in a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        return False

    original_content = content
    lines = content.split("\n")

    # Track what imports we need to add
    needs_optional = False
    needs_union = False
    needs_typing_imports = set()
    has_typing_import = False
    has_pathlib_import = False

    # Check existing imports
    for line in lines[:50]:  # Check first 50 lines for imports
        if "from typing import" in line or "import typing" in line:
            has_typing_import = True
            if "Optional" in line:
                needs_optional = False
            if "Union" in line:
                needs_union = False
        if "from pathlib import" in line or "import pathlib" in line:
            has_pathlib_import = True

    # Fix Path | None patterns
    path_none_pattern = re.compile(r"\bPath\s*\|\s*None\b")
    if path_none_pattern.search(content):
        content = path_none_pattern.sub("Optional[Path]", content)
        needs_optional = True

    # Fix str | None patterns
    str_none_pattern = re.compile(r"\bstr\s*\|\s*None\b")
    if str_none_pattern.search(content):
        content = str_none_pattern.sub("Optional[str]", content)
        needs_optional = True

    # Fix int | None patterns
    int_none_pattern = re.compile(r"\bint\s*\|\s*None\b")
    if int_none_pattern.search(content):
        content = int_none_pattern.sub("Optional[int]", content)
        needs_optional = True

    # Fix bool | None patterns
    bool_none_pattern = re.compile(r"\bbool\s*\|\s*None\b")
    if bool_none_pattern.search(content):
        content = bool_none_pattern.sub("Optional[bool]", content)
        needs_optional = True

    # Fix Dict[str, str] | None patterns
    dict_none_pattern = re.compile(r"\bDict\[[^\]]+\]\s*\|\s*None\b")
    matches = dict_none_pattern.findall(content)
    if matches:
        for match in matches:
            dict_part = match.replace(" | None", "")
            content = content.replace(match, f"Optional[{dict_part}]")
        needs_optional = True

    # Fix List[...] | None patterns
    list_none_pattern = re.compile(r"\bList\[[^\]]+\]\s*\|\s*None\b")
    matches = list_none_pattern.findall(content)
    if matches:
        for match in matches:
            list_part = match.replace(" | None", "")
            content = content.replace(match, f"Optional[{list_part}]")
        needs_optional = True

    # Add missing imports
    lines = content.split("\n")
    import_line_idx = -1

    # Find where to insert imports
    for i, line in enumerate(lines):
        if line.startswith("from typing import") or line.startswith(
            "import typing"
        ):
            import_line_idx = i
            break
        elif line.startswith("from ") or line.startswith("import "):
            import_line_idx = i

    # Add Optional import if needed
    if needs_optional and not any(
        "Optional" in line for line in lines if "typing" in line
    ):
        if import_line_idx >= 0:
            # Try to add to existing typing import
            typing_line = None
            for i, line in enumerate(lines):
                if line.startswith("from typing import"):
                    typing_line = i
                    break

            if typing_line is not None:
                current_imports = lines[typing_line]
                if "Optional" not in current_imports:
                    # Add Optional to existing import
                    if current_imports.endswith(")"):
                        lines[typing_line] = (
                            current_imports[:-1] + ", Optional)"
                        )
                    else:
                        lines[typing_line] = current_imports + ", Optional"
            else:
                # Add new typing import
                lines.insert(
                    import_line_idx + 1, "from typing import Optional"
                )
        else:
            # Add at the top
            lines.insert(0, "from typing import Optional")

    # Reconstruct content
    content = "\n".join(lines)

    # Only write if content changed
    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        except (PermissionError, OSError) as e:
            print(f"Error writing {file_path}: {e}")
            return False

    return False


def fix_type_errors_in_directory(
    directory: str, extensions: List[str] = [".py"]
) -> Dict[str, int]:
    """Fix type errors in all Python files in a directory."""
    results = {"fixed": 0, "skipped": 0, "errors": 0}

    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"Directory does not exist: {directory}")
        return results

    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
        }
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)

                try:
                    if fix_file_type_errors(file_path):
                        results["fixed"] += 1
                    else:
                        results["skipped"] += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    results["errors"] += 1

    return results


def main():
    """Main function to fix type errors."""
    print("🔧 Fixing type errors in Python files...")
    print("=" * 50)

    # Fix source files
    src_results = fix_type_errors_in_directory("src")
    print(
        f"Source files - Fixed: {src_results['fixed']}, Skipped: {src_results['skipped']}, Errors: {src_results['errors']}"
    )

    # Fix test files
    test_results = fix_type_errors_in_directory("tests")
    print(
        f"Test files - Fixed: {test_results['fixed']}, Skipped: {test_results['skipped']}, Errors: {test_results['errors']}"
    )

    total_fixed = src_results["fixed"] + test_results["fixed"]
    print(f"\n✅ Total files fixed: {total_fixed}")
    print("🎉 Type error fixing complete!")


if __name__ == "__main__":
    main()
