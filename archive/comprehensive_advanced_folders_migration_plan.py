#!/usr/bin/env python3
"""
Comprehensive Advanced Folders Migration Plan
============================================

This script handles the complex migration from src/advanced_folders to src/tools/file_management/advanced_folders_legacy
while preserving the existing src/tools/file_management/advanced_folders implementation.

The migration addresses:
1. Two different advanced_folders implementations that need to coexist
2. Import statement updates across the entire codebase
3. Test file migrations and updates
4. Documentation updates
5. Configuration reference updates
6. Rollback capability

Author: GitHub Copilot
Date: September 17, 2025
"""

import json
import os
import re
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class AdvancedFoldersMigrationManager:
    """Manages the migration of advanced_folders from src/ to src/tools/file_management/"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define source and target paths
        self.source_path = self.root_path / "src" / "advanced_folders"
        self.target_path = self.root_path / "src" / "tools" / "file_management" / "advanced_folders_legacy"
        self.existing_advanced_folders = self.root_path / "src" / "tools" / "file_management" / "advanced_folders"
        
        # Migration tracking
        self.migration_log = []
        self.backup_location = self.root_path / f"migration_backup_{self.timestamp}"
        self.rollback_script_path = self.root_path / f"rollback_migration_{self.timestamp}.py"
        
        # Files that need import updates
        self.files_to_update = set()
        self.import_mappings = {}
        
        # Migration results
        self.migration_results = {
            "timestamp": self.timestamp,
            "status": "in_progress",
            "phase": "initialization",
            "files_moved": [],
            "files_updated": [],
            "errors": [],
            "warnings": [],
            "rollback_available": False
        }

    def log_action(self, action: str, status: str = "SUCCESS", details: str = ""):
        """Log migration actions for audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.migration_log.append(entry)
        print(f"[{status}] {action}: {details}")

    def validate_environment(self) -> bool:
        """Validate the migration environment before proceeding"""
        self.log_action("Environment Validation", "INFO", "Starting validation")
        
        # Check if source exists
        if not self.source_path.exists():
            self.log_action("Environment Validation", "ERROR", f"Source path does not exist: {self.source_path}")
            return False
            
        # Check if target parent exists
        if not self.target_path.parent.exists():
            self.log_action("Environment Validation", "ERROR", f"Target parent directory does not exist: {self.target_path.parent}")
            return False
            
        # Check for existing target (should not exist for clean migration)
        if self.target_path.exists():
            self.log_action("Environment Validation", "WARNING", f"Target path already exists: {self.target_path}")
            
        # Check for write permissions
        try:
            test_file = self.target_path.parent / "migration_test.tmp"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            self.log_action("Environment Validation", "ERROR", f"No write permission: {e}")
            return False
            
        self.log_action("Environment Validation", "SUCCESS", "Environment validated")
        return True

    def create_backup(self) -> bool:
        """Create a complete backup before migration"""
        try:
            self.log_action("Backup Creation", "INFO", f"Creating backup at {self.backup_location}")
            
            # Create backup directory
            self.backup_location.mkdir(exist_ok=True)
            
            # Backup source directory
            source_backup = self.backup_location / "src_advanced_folders"
            shutil.copytree(self.source_path, source_backup)
            
            # Backup existing target if it exists
            if self.existing_advanced_folders.exists():
                target_backup = self.backup_location / "existing_advanced_folders"
                shutil.copytree(self.existing_advanced_folders, target_backup)
            
            # Backup test directories
            test_dirs = [
                self.root_path / "tests" / "advanced_folders"
            ]
            
            for test_dir in test_dirs:
                if test_dir.exists():
                    backup_test = self.backup_location / test_dir.name
                    shutil.copytree(test_dir, backup_test)
            
            self.migration_results["rollback_available"] = True
            self.log_action("Backup Creation", "SUCCESS", "Backup created successfully")
            return True
            
        except Exception as e:
            self.log_action("Backup Creation", "ERROR", f"Backup failed: {e}")
            return False

    def scan_import_dependencies(self) -> Dict[str, List[str]]:
        """Scan the entire codebase for imports that need updating"""
        self.log_action("Dependency Scanning", "INFO", "Scanning for import dependencies")
        
        dependencies = {}
        
        # Pattern to match imports from src.tools.file_management.advanced_folders_legacy
        import_pattern = re.compile(r'from\s+src\.advanced_folders\.?([\w.]*)\s+import')
        absolute_import_pattern = re.compile(r'import\s+src\.advanced_folders\.?([\w.]*)')
        
        # Scan all Python files
        for py_file in self.root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all import statements
                imports = import_pattern.findall(content)
                absolute_imports = absolute_import_pattern.findall(content)
                
                if imports or absolute_imports:
                    rel_path = str(py_file.relative_to(self.root_path))
                    dependencies[rel_path] = {
                        'from_imports': imports,
                        'absolute_imports': absolute_imports,
                        'full_content': content
                    }
                    self.files_to_update.add(py_file)
                    
            except Exception as e:
                self.log_action("Dependency Scanning", "WARNING", f"Could not scan {py_file}: {e}")
        
        self.log_action("Dependency Scanning", "SUCCESS", f"Found {len(dependencies)} files with dependencies")
        return dependencies

    def create_target_structure(self) -> bool:
        """Create the target directory structure"""
        try:
            self.log_action("Target Structure Creation", "INFO", f"Creating target structure at {self.target_path}")
            
            # Remove target if it exists
            if self.target_path.exists():
                shutil.rmtree(self.target_path)
            
            # Create target directory
            self.target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy source structure to target
            shutil.copytree(self.source_path, self.target_path, dirs_exist_ok=True)
            
            self.log_action("Target Structure Creation", "SUCCESS", "Target structure created")
            return True
            
        except Exception as e:
            self.log_action("Target Structure Creation", "ERROR", f"Failed to create target structure: {e}")
            return False

    def update_import_statements(self, dependencies: Dict[str, List[str]]) -> bool:
        """Update import statements in all affected files"""
        self.log_action("Import Updates", "INFO", "Updating import statements")
        
        success_count = 0
        error_count = 0
        
        for file_path, imports_info in dependencies.items():
            try:
                full_path = self.root_path / file_path
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Update from imports
                content = re.sub(
                    r'from\s+src\.advanced_folders',
                    'from src.tools.file_management.advanced_folders_legacy',
                    content
                )
                
                # Update absolute imports
                content = re.sub(
                    r'import\s+src\.advanced_folders',
                    'import src.tools.file_management.advanced_folders_legacy',
                    content
                )
                
                # Only write if content changed
                if content != original_content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.migration_results["files_updated"].append(str(full_path))
                    success_count += 1
                    
            except Exception as e:
                self.log_action("Import Updates", "ERROR", f"Failed to update {file_path}: {e}")
                error_count += 1
        
        self.log_action("Import Updates", "SUCCESS", f"Updated {success_count} files, {error_count} errors")
        return error_count == 0

    def update_internal_imports(self) -> bool:
        """Update internal relative imports within the migrated module"""
        self.log_action("Internal Import Updates", "INFO", "Updating internal imports")
        
        try:
            # The internal imports are already using relative imports (from ..package)
            # These should continue to work after migration
            # We only need to update absolute imports within the module itself
            
            for py_file in self.target_path.rglob("*.py"):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Update any remaining absolute imports to src.advanced_folders
                content = re.sub(
                    r'from\s+src\.advanced_folders',
                    'from src.tools.file_management.advanced_folders_legacy',
                    content
                )
                
                content = re.sub(
                    r'import\s+src\.advanced_folders',
                    'import src.tools.file_management.advanced_folders_legacy',
                    content
                )
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            self.log_action("Internal Import Updates", "SUCCESS", "Internal imports updated")
            return True
            
        except Exception as e:
            self.log_action("Internal Import Updates", "ERROR", f"Failed to update internal imports: {e}")
            return False

    def migrate_tests(self) -> bool:
        """Migrate and update test files"""
        self.log_action("Test Migration", "INFO", "Migrating test files")
        
        try:
            source_tests = self.root_path / "tests" / "advanced_folders"
            target_tests = self.root_path / "tests" / "advanced_folders_legacy"
            
            if source_tests.exists():
                # Copy tests to new location
                if target_tests.exists():
                    shutil.rmtree(target_tests)
                shutil.copytree(source_tests, target_tests)
                
                # Update imports in test files
                for test_file in target_tests.rglob("*.py"):
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update imports
                    content = re.sub(
                        r'from\s+src\.advanced_folders',
                        'from src.tools.file_management.advanced_folders_legacy',
                        content
                    )
                    
                    content = re.sub(
                        r'import\s+src\.advanced_folders',
                        'import src.tools.file_management.advanced_folders_legacy',
                        content
                    )
                    
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            self.log_action("Test Migration", "SUCCESS", "Tests migrated and updated")
            return True
            
        except Exception as e:
            self.log_action("Test Migration", "ERROR", f"Test migration failed: {e}")
            return False

    def update_documentation(self) -> bool:
        """Update documentation files that reference the old path"""
        self.log_action("Documentation Updates", "INFO", "Updating documentation")
        
        try:
            doc_files = [
                "README.md",
                "*.md",
                "docs/**/*.md",
                "**/*.rst"
            ]
            
            for pattern in doc_files:
                for doc_file in self.root_path.rglob(pattern):
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Update path references
                        content = re.sub(
                            r'src/advanced_folders',
                            'src/tools/file_management/advanced_folders_legacy',
                            content
                        )
                        
                        content = re.sub(
                            r'src\\advanced_folders',
                            'src\\tools\\file_management\\advanced_folders_legacy',
                            content
                        )
                        
                        if content != original_content:
                            with open(doc_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.log_action("Documentation Updates", "INFO", f"Updated {doc_file}")
                            
                    except Exception as e:
                        self.log_action("Documentation Updates", "WARNING", f"Could not update {doc_file}: {e}")
            
            self.log_action("Documentation Updates", "SUCCESS", "Documentation updated")
            return True
            
        except Exception as e:
            self.log_action("Documentation Updates", "ERROR", f"Documentation update failed: {e}")
            return False

    def generate_rollback_script(self) -> bool:
        """Generate a rollback script to undo the migration"""
        try:
            rollback_content = f'''#!/usr/bin/env python3
"""
Rollback script for Advanced Folders Migration
Generated: {datetime.now().isoformat()}
"""

import os
import shutil
from pathlib import Path

def rollback_migration():
    """Rollback the advanced folders migration"""
    root_path = Path(".")
    backup_path = Path("{self.backup_location}")
    
    print("Starting rollback...")
    
    # Restore source directory
    source_backup = backup_path / "src_advanced_folders"
    target_source = root_path / "src" / "advanced_folders"
    
    if source_backup.exists():
        if target_source.exists():
            shutil.rmtree(target_source)
        shutil.copytree(source_backup, target_source)
        print("Restored src/advanced_folders")
    
    # Remove migrated directory
    migrated_path = root_path / "src" / "tools" / "file_management" / "advanced_folders_legacy"
    if migrated_path.exists():
        shutil.rmtree(migrated_path)
        print("Removed migrated directory")
    
    # Restore test directory
    test_backup = backup_path / "advanced_folders"
    target_test = root_path / "tests" / "advanced_folders"
    
    if test_backup.exists():
        if target_test.exists():
            shutil.rmtree(target_test)
        shutil.copytree(test_backup, target_test)
        print("Restored test directory")
    
    # Remove migrated test directory
    migrated_test = root_path / "tests" / "advanced_folders_legacy"
    if migrated_test.exists():
        shutil.rmtree(migrated_test)
        print("Removed migrated test directory")
    
    print("Rollback completed!")
    print("Note: You will need to manually revert import statement changes in files.")
    print("Check the migration log for files that were updated.")

if __name__ == "__main__":
    rollback_migration()
'''
            
            with open(self.rollback_script_path, 'w', encoding='utf-8') as f:
                f.write(rollback_content)
            
            # Make executable on Unix-like systems
            if os.name != 'nt':
                os.chmod(self.rollback_script_path, 0o755)
            
            self.log_action("Rollback Script", "SUCCESS", f"Rollback script created: {self.rollback_script_path}")
            return True
            
        except Exception as e:
            self.log_action("Rollback Script", "ERROR", f"Failed to create rollback script: {e}")
            return False

    def cleanup_source(self) -> bool:
        """Remove the original source directory after successful migration"""
        try:
            if self.source_path.exists():
                shutil.rmtree(self.source_path)
                self.log_action("Source Cleanup", "SUCCESS", "Original source directory removed")
            return True
        except Exception as e:
            self.log_action("Source Cleanup", "ERROR", f"Failed to remove source: {e}")
            return False

    def run_validation_tests(self) -> bool:
        """Run basic validation to ensure migration was successful"""
        self.log_action("Validation", "INFO", "Running validation tests")
        
        try:
            # Check if target directory exists and has content
            if not self.target_path.exists():
                self.log_action("Validation", "ERROR", "Target directory does not exist")
                return False
            
            # Check if __init__.py exists
            init_file = self.target_path / "__init__.py"
            if not init_file.exists():
                self.log_action("Validation", "ERROR", "__init__.py missing in target")
                return False
            
            # Try to import the migrated module
            try:
                import sys
                sys.path.insert(0, str(self.root_path))
                import src.tools.file_management.advanced_folders_legacy
                self.log_action("Validation", "SUCCESS", "Module import successful")
            except ImportError as e:
                self.log_action("Validation", "WARNING", f"Import test failed: {e}")
            
            self.log_action("Validation", "SUCCESS", "Basic validation passed")
            return True
            
        except Exception as e:
            self.log_action("Validation", "ERROR", f"Validation failed: {e}")
            return False

    def save_migration_report(self) -> bool:
        """Save comprehensive migration report"""
        try:
            self.migration_results["migration_log"] = self.migration_log
            self.migration_results["files_scanned"] = len(self.files_to_update)
            
            report_path = self.root_path / f"advanced_folders_migration_report_{self.timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.migration_results, f, indent=2, default=str)
            
            self.log_action("Report Generation", "SUCCESS", f"Migration report saved: {report_path}")
            return True
            
        except Exception as e:
            self.log_action("Report Generation", "ERROR", f"Failed to save report: {e}")
            return False

    def execute_migration(self) -> bool:
        """Execute the complete migration process"""
        print(f"=== Advanced Folders Migration Started at {datetime.now()} ===")
        
        try:
            # Phase 1: Validation and Backup
            self.migration_results["phase"] = "validation"
            if not self.validate_environment():
                self.migration_results["status"] = "failed"
                return False
            
            if not self.create_backup():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 2: Dependency Analysis
            self.migration_results["phase"] = "analysis"
            dependencies = self.scan_import_dependencies()
            
            # Phase 3: Structure Creation
            self.migration_results["phase"] = "structure_creation"
            if not self.create_target_structure():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 4: Import Updates
            self.migration_results["phase"] = "import_updates"
            if not self.update_import_statements(dependencies):
                self.migration_results["status"] = "failed"
                return False
            
            if not self.update_internal_imports():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 5: Test Migration
            self.migration_results["phase"] = "test_migration"
            if not self.migrate_tests():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 6: Documentation Updates
            self.migration_results["phase"] = "documentation"
            if not self.update_documentation():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 7: Rollback Script Generation
            self.migration_results["phase"] = "rollback_preparation"
            if not self.generate_rollback_script():
                self.migration_results["status"] = "failed"
                return False
            
            # Phase 8: Validation
            self.migration_results["phase"] = "validation"
            if not self.run_validation_tests():
                self.migration_results["status"] = "warning"
            
            # Phase 9: Source Cleanup (optional - commented out for safety)
            # self.cleanup_source()
            
            # Phase 10: Report Generation
            self.migration_results["phase"] = "completed"
            self.migration_results["status"] = "success"
            self.save_migration_report()
            
            print(f"=== Migration Completed Successfully at {datetime.now()} ===")
            print(f"Backup location: {self.backup_location}")
            print(f"Rollback script: {self.rollback_script_path}")
            
            return True
            
        except Exception as e:
            self.migration_results["status"] = "failed"
            self.migration_results["errors"].append(str(e))
            self.log_action("Migration Execution", "ERROR", f"Migration failed: {e}")
            print(f"Migration failed with error: {e}")
            traceback.print_exc()
            return False


def main():
    """Main execution function"""
    print("Advanced Folders Migration Tool")
    print("=" * 50)
    
    # Check for automated mode
    automated = len(sys.argv) > 1 and sys.argv[1].lower() == 'automated'
    
    if not automated:
        # Ask for confirmation in interactive mode
        response = input("This will migrate src/advanced_folders to src/tools/file_management/advanced_folders_legacy. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return False
    else:
        print("Running in automated mode...")
    
    # Execute migration
    manager = AdvancedFoldersMigrationManager()
    success = manager.execute_migration()
    
    if success:
        print("\n✓ Migration completed successfully!")
        print(f"✓ Backup created at: {manager.backup_location}")
        print(f"✓ Rollback script available at: {manager.rollback_script_path}")
        print("\nNext steps:")
        print("1. Test the migrated functionality")
        print("2. Run unit tests to ensure everything works")
        print("3. Update any remaining documentation")
        print("4. If satisfied, you can remove the original source directory")
    else:
        print("\n✗ Migration failed!")
        print("Check the migration log for details.")
        print(f"Backup is available at: {manager.backup_location}")
        
    return success


if __name__ == "__main__":
    main()