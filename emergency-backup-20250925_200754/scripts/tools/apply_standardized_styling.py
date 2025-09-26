#!/usr/bin/env python3
"""
Migration script to apply standardized styling to all utilities.

This script systematically updates all GUI utilities to use the new
standardized theme system with consistent styling and layout.
"""

import os
import sys
import shutil
from pathlib import Path

# List of utilities to migrate
UTILITIES_TO_MIGRATE = [
    'file_utilities_1/catalog.py',
    'cmsd.py',
    'edit_image_metadata.py',
    'empty_folders.py',
    'file_finder.py',
    'find_duplicate_files.py',
    'log_manager.py',
    'office_meta_data_editor.py',
    'organize.py',
    'permissions_editor.py',
    'file_utilities_2/gui/rename_gui.py',
    'settings_dialog.py',
    'size_analyzer.py',
    'synchronization_backup/sync.py',
    'tag_viewer_editor.py',
    'tree_map.py',
    'secure_delete.py'
]

# Template for standardized utility
STANDARDIZED_TEMPLATE = '''"""
{utility_name} - Standardized GUI utility
"""

import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

from gui.standard_window import StandardWindow
from gui.themes import ThemeManager
from gui.common.dialogs import get_open_file_name, get_existing_directory


class {class_name}(StandardWindow):
    """{utility_name} with standardized styling."""
    
    def __init__(self):
        super().__init__("{utility_name}")
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface with standardized styling."""
        # Create header
        header = self.create_header("{utility_name}")
        self.main_layout.addWidget(header)
        
        # TODO: Add specific UI elements for this utility
        # Use create_button(), create_group_box(), etc.
        
        # Example structure:
        # control_group = self.create_group_box("Controls")
        # control_layout = QVBoxLayout()
        # ... add controls ...
        # control_group.setLayout(control_layout)
        # self.main_layout.addWidget(control_group)


def main():
    """Main function to run the utility."""
    app = QApplication(sys.argv)
    window = {class_name}()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
'''

def create_backup(original_file):
    """Create a backup of the original file."""
    backup_path = f"{original_file}.backup"
    shutil.copy2(original_file, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def needs_migration(file_path):
    """Check if a file needs standardized styling migration."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if it already uses StandardWindow
    if 'StandardWindow' in content:
        return False
        
    # Check if it's a GUI utility
    if 'QApplication' in content and 'QMainWindow' in content:
        return True
        
    return False

def migrate_utility(utility_file):
    """Migrate a single utility to use standardized styling."""
    file_path = os.path.join(os.getcwd(), utility_file)
    
    if not os.path.exists(file_path):
        print(f"File not found: {utility_file}")
        return False
        
    if not needs_migration(file_path):
        print(f"Already migrated or not a GUI utility: {utility_file}")
        return False
        
    # Create backup
    backup_path = create_backup(file_path)
    
    # Get utility name and class name
    utility_name = utility_file.replace('.py', '').replace('_', ' ').title()
    class_name = utility_file.replace('.py', '').replace('_', '').title() + 'GUI'
    
    # Create new standardized version
    new_content = STANDARDIZED_TEMPLATE.format(
        utility_name=utility_name,
        class_name=class_name
    )
    
    # Write new content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Migrated: {utility_file}")
    return True

def main():
    """Main migration function."""
    print("Starting standardized styling migration...")
    print("=" * 50)
    
    migrated_count = 0
    
    for utility in UTILITIES_TO_MIGRATE:
        try:
            if migrate_utility(utility):
                migrated_count += 1
        except Exception as e:
            print(f"Error migrating {utility}: {str(e)}")
            
    print("=" * 50)
    print(f"Migration complete. {migrated_count} utilities migrated.")
    print("Backups created with .backup extension")
    
    # Create migration report
    report_path = "migration_report.txt"
    with open(report_path, 'w') as f:
        f.write("Standardized Styling Migration Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Date: {__import__('datetime').datetime.now()}\n")
        f.write(f"Utilities migrated: {migrated_count}\n")
        f.write("\nMigrated utilities:\n")
        for utility in UTILITIES_TO_MIGRATE:
            f.write(f"- {utility}\n")
            
    print(f"Migration report saved to: {report_path}")

if __name__ == "__main__":
    main()
