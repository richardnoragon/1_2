#!/usr/bin/env python3
"""
Tool Import Test Script
Test individual tool imports to identify issues
"""

import importlib
import os
import sys
from typing import Tuple

# Add current directory to path
sys.path.insert(0, os.getcwd())


def _attempt_import(target: Tuple[str, str], label: str) -> bool:
    """Attempt to import a module and access an attribute.

    Args:
        target: Tuple of module path and attribute name to verify.
        label: Human readable label for status output.

    Returns:
        bool: True when import succeeds, False otherwise.
    """

    module_path, attr_name = target
    try:
        module = importlib.import_module(module_path)
        getattr(module, attr_name)
        print(f"✅ {label} import successful")
        return True
    except Exception as exc:  # noqa: BLE001 - diagnostic helper
        print(f"❌ {label} import failed: {exc}")
        return False


def test_file_finder() -> bool:
    """Test File Finder import."""

    return _attempt_import(
        ("src.tools.file_management.finder.file_finder", "FileFinderWindow"),
        "File Finder",
    )


def test_network_transfer() -> bool:
    """Test Network Transfer import."""

    return _attempt_import(
        (
            "src.tools.network.transfer.network_transfer",
            "NetworkTransferGUI",
        ),
        "Network Transfer",
    )


def test_network_connectivity() -> bool:
    """Test Network Connectivity import."""

    return _attempt_import(
        (
            "src.tools.network.network_connectivity",
            "NetworkConnectivityGUI",
        ),
        "Network Connectivity",
    )


def test_organize() -> bool:
    """Test Organize tool import."""

    return _attempt_import(
        (
            "src.tools.file_management.organizer.organize",
            "OrganizeWindow",
        ),
        "Organize",
    )


def test_basic_import() -> bool:
    """Test basic import without path issues."""

    # Add src to path if not already there
    src_path = os.path.join(os.getcwd(), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    return test_file_finder()


def main() -> None:
    print("🔍 Tool Import Diagnostic Test")
    print("=" * 50)

    tests = [
        test_basic_import,
        test_file_finder,
        test_organize,
        test_network_transfer,
        test_network_connectivity,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed < len(tests):
        print("\n🔧 Suggested fixes:")
        print("1. Check if all required __init__.py files exist")
        print("2. Verify module structure is correct")
        print("3. Ensure no circular imports")
        print("4. Check for syntax errors in modules")


if __name__ == "__main__":
    main()
