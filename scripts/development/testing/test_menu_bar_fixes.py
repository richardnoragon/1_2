#!/usr/bin/env python3
"""
Test script to verify menu bar fixes for Richard's File Utilities tools.
This script will test the tools that were reported as missing menu bars.
"""

import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox


def test_tool_menu_bars():
    """Test menu bars for various tools."""
    app = QApplication(sys.argv)

    # List of tools to test with their modules
    tools_to_test = [
        (
            "Image Metadata Editor",
            "enhanced_image_metadata_editor_with_menu",
            "EnhancedImageMetadataEditorGUI",
        ),
        (
            "Office Metadata Editor",
            "enhanced_office_metadata_editor_with_menu",
            "EnhancedOfficeMetadataEditorGUI",
        ),
        ("File Touch", "enhanced_file_touch_with_menu", "EnhancedFileTouchGUI"),
        (
            "Security Preferences",
            "enhanced_security_preferences_with_menu",
            "EnhancedSecurityPreferencesGUI",
        ),
        # Analysis tools from src/utilities/analysis/
        ("Size Analyzer", "src.utilities.analysis.size_analyzer", "SizeAnalyzerGUI"),
        (
            "Duplicate Finder",
            "src.utilities.analysis.find_duplicate_files",
            "DuplicateFinderApp",
        ),
        ("Empty Folders", "src.utilities.analysis.empty_folders", "EmptyFoldersGUI"),
        (
            "Checksum Calculator",
            "src.tools.analysis.checksum.check_sum",
            "ChecksumGUI",
        ),
        # System maintenance tool
        (
            "Software Maintenance",
            "src.utilities.system.software_maintenance.gui.maintenance_hub",
            "SoftwareMaintenanceHub",
        ),
    ]

    results = []

    for tool_name, module_name, class_name in tools_to_test:
        try:
            print(f"Testing {tool_name}...")

            # Import the module dynamically
            module = __import__(module_name)

            # Get the class from the module
            tool_class = getattr(module, class_name)

            # Create an instance
            tool_instance = tool_class()

            # Check if menu bar exists and has items
            menu_bar = tool_instance.menuBar()
            if menu_bar and menu_bar.actions():
                menu_count = len(menu_bar.actions())
                results.append(
                    f"✅ {tool_name}: Menu bar present with {menu_count} menus"
                )

                # List the menu names
                menu_names = [action.text() for action in menu_bar.actions()]
                results.append(f"   Menus: {', '.join(menu_names)}")
            else:
                results.append(f"❌ {tool_name}: Menu bar missing or empty")

            # Show the window briefly to verify it works
            tool_instance.show()
            tool_instance.hide()

            # Clean up
            tool_instance.close()

        except Exception as e:
            results.append(f"❌ {tool_name}: Failed to test - {str(e)}")

    # Display results
    results_text = "\n".join(results)
    print("\n" + "=" * 60)
    print("MENU BAR TEST RESULTS")
    print("=" * 60)
    print(results_text)

    # Show results in message box
    QMessageBox.information(None, "Menu Bar Test Results", results_text)

    return results


def main():
    """Main function."""
    print("Menu Bar Fix Test - Richard's File Utilities")
    print("=" * 60)

    results = test_tool_menu_bars()

    # Count successes and failures
    successes = len([r for r in results if "✅" in r and "Menu bar present" in r])
    failures = len([r for r in results if "❌" in r])

    print(f"\nSummary: {successes} successes, {failures} failures")

    if failures == 0:
        print("🎉 All tested tools now have menu bars!")
    else:
        print("⚠️ Some tools still need menu bar fixes.")


if __name__ == "__main__":
    main()
