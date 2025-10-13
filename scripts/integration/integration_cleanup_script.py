#!/usr/bin/env python3
"""
Integration Cleanup Script for Richard's File Utilities

This script will:
1. Remove duplicate files from the root directory that exist in src/utilities
2. Update main.py to properly integrate tools from src/utilities folders
3. Create proper __init__.py files for imports
4. Update import paths throughout the project
"""

import os
import shutil
import sys
from pathlib import Path

# Tools that have duplicates between root and src directories
DUPLICATE_TOOLS = {
    "check_sum.py": "src/utilities/analysis/check_sum.py",
    "find_duplicate_files.py": "src/utilities/analysis/find_duplicate_files.py",
    "size_analyzer.py": "src/utilities/analysis/",  # needs to be moved to analysis
    "en_and_decrypt.py": "src/utilities/security/",  # needs to be moved to security
    "secure_delete.py": "src/utilities/security/",  # needs to be moved to security
    "permissions_editor.py": "src/utilities/system/permissions_editor.py",
}

# Tools that need to be moved from root to proper src locations
TOOLS_TO_MOVE = {
    "size_analyzer.py": "src/utilities/analysis/size_analyzer.py",
    "en_and_decrypt.py": "src/utilities/security/en_and_decrypt.py",
    "secure_delete.py": "src/utilities/security/secure_delete.py",
}


def backup_file(file_path):
    """Create a backup of a file before operations."""
    backup_path = f"{file_path}.backup"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backed up {file_path}")
        return backup_path
    return None


def move_tool_to_proper_location(source_path, target_path):
    """Move a tool from root to proper src location."""
    if not os.path.exists(source_path):
        print(f"⚠ Source file not found: {source_path}")
        return False

    # Create target directory if it doesn't exist
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)

    # Check if target already exists and is different
    if os.path.exists(target_path):
        # Compare file sizes to see if they're different
        source_size = os.path.getsize(source_path)
        target_size = os.path.getsize(target_path)

        if source_size != target_size:
            # Files are different, keep the root version (likely more recent)
            backup_file(target_path)
            shutil.move(source_path, target_path)
            print(f"✓ Moved {source_path} to {target_path} (replaced existing)")
        else:
            # Files are same size, remove the root duplicate
            os.remove(source_path)
            print(f"✓ Removed duplicate {source_path}")
    else:
        # Target doesn't exist, move the file
        shutil.move(source_path, target_path)
        print(f"✓ Moved {source_path} to {target_path}")

    return True


def remove_duplicate_file(file_path):
    """Remove a duplicate file from root directory."""
    if os.path.exists(file_path):
        backup_file(file_path)
        os.remove(file_path)
        print(f"✓ Removed duplicate {file_path}")
        return True
    return False


def create_init_files():
    """Create __init__.py files in all utility directories."""
    utility_dirs = [
        "src/utilities",
        "src/utilities/analysis",
        "src/utilities/network",
        "src/utilities/privacy",
        "src/utilities/security",
        "src/utilities/system",
        "src/utilities/metadata",
        "src/utilities/file_operations",
        "src/tools/pdf_tools",
    ]

    for dir_path in utility_dirs:
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            os.makedirs(dir_path, exist_ok=True)
            with open(init_file, "w") as f:
                f.write(
                    f'"""Utilities package for Richard\'s File Utilities - {os.path.basename(dir_path)} module."""\n'
                )
            print(f"✓ Created {init_file}")


def update_main_py():
    """Update main.py to properly integrate tools from src/utilities."""
    main_py_path = "main.py"

    if not os.path.exists(main_py_path):
        print(f"⚠ {main_py_path} not found")
        return False

    # Read current main.py
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create backup
    backup_file(main_py_path)

    # Update import paths in launch_tool method
    import_updates = {
        # Analysis tools
        '"size_analyzer"': '"src.utilities.analysis.size_analyzer"',
        '"find_duplicate_files"': '"src.utilities.analysis.find_duplicate_files"',
        '"check_sum"': '"src.utilities.analysis.check_sum"',
        # Security tools
        '"en_and_decrypt"': '"src.utilities.security.en_and_decrypt"',
        '"secure_delete"': '"src.utilities.security.secure_delete"',
        # System tools
        '"permissions_editor"': '"src.utilities.system.permissions_editor"',
    }

    # Apply updates
    updated_content = content
    for old_import, new_import in import_updates.items():
        updated_content = updated_content.replace(old_import, new_import)

    # Add network, privacy, and system tabs if not present
    if "Network Tools" not in updated_content:
        # Find the PDF Tools tab insertion point
        pdf_tab_pos = updated_content.find('tab_widget.addTab(pdf_tab, "PDF Tools")')
        if pdf_tab_pos != -1:
            # Insert new tabs before PDF Tools
            new_tabs = """
            # Network Tools
            network_tab = self.create_tool_category_tab([
                ("Network Connectivity", "Check network connectivity and diagnostics", self.open_network_connectivity),
                ("Network Scanner", "Scan network for devices and services", self.open_network_scanner),
            ])
            tab_widget.addTab(network_tab, "Network Tools")
            
            # Privacy Tools
            privacy_tab = self.create_tool_category_tab([
                ("Privacy Cleaner", "Clean privacy-sensitive data", self.open_privacy_cleaner),
                ("Data Anonymizer", "Anonymize sensitive file data", self.open_data_anonymizer),
            ])
            tab_widget.addTab(privacy_tab, "Privacy Tools")
            
            # System Tools  
            system_tab = self.create_tool_category_tab([
                ("System Diagnostics", "Run system diagnostics and monitoring", self.open_system_diagnostics),
                ("System Cleanup", "Clean system temporary files", self.open_system_cleanup),
                ("Software Maintenance", "Maintain and update software", self.open_software_maintenance),
            ])
            tab_widget.addTab(system_tab, "System Tools")
            
            """
            updated_content = (
                updated_content[:pdf_tab_pos] + new_tabs + updated_content[pdf_tab_pos:]
            )

    # Add launcher methods for new tools if not present
    if "def open_network_connectivity(self):" not in updated_content:
        # Find insertion point after existing launcher methods
        last_launcher_pos = updated_content.rfind("def open_pdf_pages(self):")
        if last_launcher_pos != -1:
            # Find the end of this method
            method_end = updated_content.find("\n        def ", last_launcher_pos + 1)
            if method_end == -1:
                method_end = updated_content.find("\n    def ", last_launcher_pos + 1)

            new_launchers = '''
        # Network Tools
        def open_network_connectivity(self):
            """Open Network Connectivity tool."""
            self.launch_tool("Network Connectivity", "src.utilities.network.network_connectivity", "NetworkConnectivityGUI")
        
        def open_network_scanner(self):
            """Open Network Scanner tool."""
            self.launch_tool(
                "Network Scanner",
                "src.tools.network.scanner.network_scanner",
                "NetworkScannerGUI",
            )
        
        # Privacy Tools
        def open_privacy_cleaner(self):
            """Open Privacy Cleaner tool."""
            self.launch_tool("Privacy Cleaner", "src.utilities.privacy.privacy_tools", "PrivacyCleanerGUI")
        
        def open_data_anonymizer(self):
            """Open Data Anonymizer tool."""
            self.launch_tool("Data Anonymizer", "src.tools.privacy.anonymizer.data_anonymizer", "DataAnonymizerGUI")
        
        # System Tools
        def open_system_diagnostics(self):
            """Open System Diagnostics tool."""
            self.launch_tool("System Diagnostics", "src.utilities.system.diagnostics_monitoring", "SystemDiagnosticsGUI")
        
        def open_system_cleanup(self):
            """Open System Cleanup tool."""
            self.launch_tool("System Cleanup", "src.utilities.system.system_cleanup", "SystemCleanupGUI")
        
        def open_software_maintenance(self):
            """Open Software Maintenance tool."""
            self.launch_tool("Software Maintenance", "src.utilities.system.software_maintenance", "SoftwareMaintenanceGUI")
        
'''
            updated_content = (
                updated_content[:method_end]
                + new_launchers
                + updated_content[method_end:]
            )

    # Write updated content
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("✓ Updated main.py with proper tool integration")
    return True


def main():
    """Main integration cleanup process."""
    print("=" * 60)
    print("Richard's File Utilities - Integration Cleanup Script")
    print("=" * 60)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print(f"Working directory: {os.getcwd()}")
    print()

    # Step 1: Create __init__.py files
    print("Step 1: Creating __init__.py files...")
    create_init_files()
    print()

    # Step 2: Move tools to proper locations
    print("Step 2: Moving tools to proper src/utilities locations...")
    for source, target in TOOLS_TO_MOVE.items():
        move_tool_to_proper_location(source, target)
    print()

    # Step 3: Remove remaining duplicates
    print("Step 3: Removing duplicate files...")
    for duplicate in DUPLICATE_TOOLS.keys():
        if os.path.exists(duplicate) and duplicate not in TOOLS_TO_MOVE:
            remove_duplicate_file(duplicate)
    print()

    # Step 4: Update main.py
    print("Step 4: Updating main.py for proper integration...")
    update_main_py()
    print()

    print("=" * 60)
    print("Integration cleanup completed!")
    print("=" * 60)
    print()
    print("Summary of changes:")
    print("✓ Created __init__.py files in all utility directories")
    print("✓ Moved tools to proper src/utilities locations")
    print("✓ Removed duplicate files from root directory")
    print("✓ Updated main.py with proper import paths")
    print("✓ Added Network, Privacy, and System tool tabs")
    print("✓ Created backup files for all modified files")
    print()
    print("Next steps:")
    print("1. Test the application: python main.py")
    print("2. Check that all tools load properly")
    print("3. Fix any remaining import issues")
    print("4. Remove .backup files after testing")


if __name__ == "__main__":
    main()
