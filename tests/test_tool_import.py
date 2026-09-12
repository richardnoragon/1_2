#!/usr/bin/env python3
"""
Test script to verify tool imports work correctly.
"""

import os
import sys

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


@pytest.mark.parametrize(
    ("module_name", "class_name"),
    [
        ("file_finder", "FileFinderWindow"),
        ("compress_decompress", "CompressDecompressApp"),
        ("empty_folders", "EmptyFoldersGUI"),
        ("catalog", "CatalogWindow"),
        ("organize", "OrganizeWindow"),
    ],
)
def test_tool_import(module_name, class_name):
    """Test importing a specific tool."""
    try:
        print(f"Testing {module_name}.{class_name}...")

        import_paths = {
            "file_finder": [
                "src.tools.file_operations.file_finder",
                "src.tools.file_management.finder.file_finder",
                "file_finder",
            ],
            "compress_decompress": [
                "src.tools.file_operations.compression.compress_decompress",
                "compress_decompress",
            ],
            "empty_folders": [
                "src.tools.analysis.empty_folders.empty_folders",
                "src.tools.analysis.empty_folders",
                "empty_folders",
            ],
            "catalog": [
                "src.tools.file_operations.catalog",
                "src.tools.file_management.advanced_catalog.catalog_tool",
                "src.tools.file_management.advanced_catalog.catalog.catalog",
                "catalog",
            ],
            "organize": [
                "src.tools.file_operations.organize",
                "src.tools.file_management.organizer.organize",
                "organize",
            ],
        }

        for import_path in import_paths.get(module_name, [module_name]):
            try:
                module = __import__(import_path, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ Successfully imported {class_name} from {import_path}")
                return
            except (ImportError, AttributeError, ModuleNotFoundError) as e:
                print(f"❌ Failed to import from {import_path}: {e}")
                continue

        pytest.fail(f"Could not import {class_name} from any path for {module_name}")
    except Exception as e:
        pytest.fail(f"Error testing {module_name}.{class_name}: {e}")
