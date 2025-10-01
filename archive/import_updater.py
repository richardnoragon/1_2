#!/usr/bin/env python3
"""
Import Statement Updater for Advanced Folders Migration
Updates all import statements to reflect the new structure.
"""

import fileinput
import os
import re
from pathlib import Path


class ImportUpdater:
    def __init__(self):
        self.updated_files = []
        self.update_count = 0
        
        # Define import mapping patterns
        self.import_mappings = [
            # Update old src.advanced_folders to new location
            (r'from src\.advanced_folders', 'from src.tools.file_management.advanced_folders'),
            (r'import src\.advanced_folders', 'import src.tools.file_management.advanced_folders'),
            
            # Update relative imports within advanced_folders if they exist
            (r'from \.\.advanced_folders', 'from src.tools.file_management.advanced_folders'),
            
            # Keep legacy imports as they are - they're intentionally pointing to legacy
            # (no changes to advanced_folders_legacy imports)
        ]
    
    def find_python_files(self, directory):
        """Find all Python files in directory recursively."""
        python_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def update_imports_in_file(self, file_path):
        """Update import statements in a single file."""
        updated = False
        original_content = ""
        new_content = ""
        
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            new_content = original_content
            
            # Apply each mapping pattern
            for old_pattern, new_replacement in self.import_mappings:
                if re.search(old_pattern, new_content):
                    new_content = re.sub(old_pattern, new_replacement, new_content)
                    updated = True
            
            # Write updated content if changes were made
            if updated and new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.updated_files.append(file_path)
                changes = new_content.count('src.tools.file_management.advanced_folders') - original_content.count('src.tools.file_management.advanced_folders')
                self.update_count += changes
                
                print(f"[UPDATE] {file_path} ({changes} imports updated)")
                
        except Exception as e:
            print(f"[ERROR] Failed to update {file_path}: {str(e)}")
    
    def update_all_imports(self, base_directories=None):
        """Update imports in all relevant directories."""
        if base_directories is None:
            base_directories = ['src/', 'tests/', '.']
        
        print("[START] Updating import statements...")
        print(f"[SCAN] Scanning directories: {', '.join(base_directories)}")
        
        all_files = []
        for directory in base_directories:
            if os.path.exists(directory):
                all_files.extend(self.find_python_files(directory))
        
        print(f"[FOUND] {len(all_files)} Python files to process")
        
        # Process each file
        for file_path in all_files:
            # Skip backup directories and __pycache__
            if any(skip in file_path for skip in ['migration_backup', '__pycache__', '.git']):
                continue
                
            self.update_imports_in_file(file_path)
        
        print(f"\n[COMPLETE] Import update completed:")
        print(f"[STATS] Files updated: {len(self.updated_files)}")
        print(f"[STATS] Total import changes: {self.update_count}")
        
        return {
            "updated_files": self.updated_files,
            "total_changes": self.update_count,
            "summary": f"Updated {len(self.updated_files)} files with {self.update_count} import changes"
        }
    
    def validate_imports(self):
        """Validate that import updates were successful."""
        print("[VALIDATE] Validating import updates...")
        
        # Check for remaining old imports
        remaining_old_imports = 0
        for file_path in self.updated_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count any remaining src.advanced_folders references (excluding legacy)
                    old_refs = len(re.findall(r'from src\.advanced_folders[^_]', content))
                    remaining_old_imports += old_refs
            except Exception as e:
                print(f"[ERROR] Validation error for {file_path}: {str(e)}")
        
        if remaining_old_imports == 0:
            print("[SUCCESS] All import statements updated successfully")
        else:
            print(f"[WARNING] {remaining_old_imports} old import statements remain")
        
        return remaining_old_imports == 0

if __name__ == "__main__":
    updater = ImportUpdater()
    
    # Update all imports
    results = updater.update_all_imports()
    
    # Validate updates
    validation_success = updater.validate_imports()
    
    print(f"\n[FINAL] Import update summary:")
    print(f"Files processed: {len(updater.updated_files)}")
    print(f"Import changes: {updater.update_count}")
    print(f"Validation: {'PASSED' if validation_success else 'NEEDS REVIEW'}")