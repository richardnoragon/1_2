#!/usr/bin/env python3
"""
Automated Migration Script: src/utilities to src/tools
=====================================================

This script handles the complete automated migration of all contents
from src/utilities to src/tools directory structure.

Usage:
    python migration_automation.py [--dry-run] [--backup-dir PATH]

Features:
- Complete backup creation
- Automated file migration
- Import statement updates
- Configuration file updates
- Comprehensive logging
- Rollback capabilities
"""

import argparse
import importlib.util
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MigrationAutomation:
    """Main class for handling the complete migration process."""
    
    def __init__(self, dry_run: bool = False, backup_dir: Optional[str] = None):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent
        self.backup_dir = backup_dir or self._create_backup_dir()
        self.migration_log = []
        
        # Setup logging
        self._setup_logging()
        
        # Migration mapping configuration
        self.migration_mapping = {
            "src/utilities/advanced_folders": "src/tools/file_management/advanced_folders",
            "src/utilities/file_management": "src/tools/file_management",
            "src/utilities/office_metadata": "src/tools/metadata/office_metadata",
            "src/utilities/pdf_tools": "src/tools/pdf_tools",
            "src/utilities/logs": "src/tools/system/logs"
        }
        
        # Import update patterns
        self.import_patterns = [
            (r'from\s+src\.utilities\.([^\s\.\,]+)', r'from src.tools.\1'),
            (r'import\s+src\.utilities\.([^\s\.\,]+)', r'import src.tools.\1'),
            (r'from\s+utilities\.([^\s\.\,]+)', r'from tools.\1'),
            (r'import\s+utilities\.([^\s\.\,]+)', r'import tools.\1'),
            (r'"src\.utilities\.([^"]+)"', r'"src.tools.\1"'),
            (r"'src\.utilities\.([^']+)'", r"'src.tools.\1'"),
        ]
    
    def _create_backup_dir(self) -> str:
        """Create timestamped backup directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.project_root / f"migration_backup_{timestamp}"
        return str(backup_path)
    
    def _setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = self.project_root / "migration_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migration_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Migration automation started - Dry run: {self.dry_run}")
    
    def create_complete_backup(self) -> bool:
        """Create complete backup of current state."""
        try:
            backup_path = Path(self.backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup critical directories
            backup_items = [
                ("src", "src_original"),
                ("tests", "tests_original"),
                ("config", "config_original"),
                ("main.py", "main_backup.py"),
                ("requirements.txt", "requirements_backup.txt")
            ]
            
            for source, target in backup_items:
                source_path = self.project_root / source
                target_path = backup_path / target
                
                if source_path.exists():
                    if not self.dry_run:
                        if source_path.is_dir():
                            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source_path, target_path)
                    
                    self.logger.info(f"Backed up {source} to {target}")
                    self._log_action("backup_created", str(source_path), str(target_path), "success")
            
            # Create backup manifest
            manifest = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_directory": str(backup_path),
                "items_backed_up": [item[0] for item in backup_items if (self.project_root / item[0]).exists()],
                "dry_run": self.dry_run
            }
            
            if not self.dry_run:
                with open(backup_path / "backup_manifest.json", "w") as f:
                    json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Complete backup created at: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            self._log_action("backup_failed", "", "", "failed", str(e))
            return False
    
    def validate_source_structure(self) -> bool:
        """Validate that source utilities directory exists and is accessible."""
        utilities_path = self.project_root / "src" / "utilities"
        
        if not utilities_path.exists():
            self.logger.error("Source utilities directory does not exist")
            return False
        
        # Count files and directories
        py_files = list(utilities_path.rglob("*.py"))
        ui_files = list(utilities_path.rglob("*.ui"))
        all_files = list(utilities_path.rglob("*"))
        
        self.logger.info(f"Source validation - Python files: {len(py_files)}, UI files: {len(ui_files)}, Total files: {len(all_files)}")
        
        # Test import capability for key modules
        test_imports = [
            "src.tools.advanced_folders",
            "src.tools.pdf_tools"
        ]
        
        import_issues = []
        for module in test_imports:
            try:
                # Add project root to path temporarily
                sys.path.insert(0, str(self.project_root))
                spec = importlib.util.find_spec(module)
                if spec is None:
                    import_issues.append(f"Module {module} not found")
                sys.path.remove(str(self.project_root))
            except Exception as e:
                import_issues.append(f"Module {module} import error: {e}")
        
        if import_issues:
            self.logger.warning(f"Import issues detected: {import_issues}")
        
        return True
    
    def create_target_structure(self) -> bool:
        """Create target directory structure in src/tools."""
        try:
            tools_base = self.project_root / "src" / "tools"
            
            # Directories to create
            new_directories = [
                "pdf_tools",
                "file_management/advanced_folders", 
                "metadata/office_metadata",
                "system/logs"
            ]
            
            for dir_path in new_directories:
                full_path = tools_base / dir_path
                
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                
                self.logger.info(f"Created directory: {full_path}")
                self._log_action("directory_created", "", str(full_path), "success")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Target structure creation failed: {e}")
            self._log_action("structure_creation_failed", "", "", "failed", str(e))
            return False
    
    def migrate_directory_contents(self, source_dir: str, target_dir: str) -> bool:
        """Migrate contents of a directory to new location."""
        source_path = Path(source_dir.replace('/', os.sep))
        target_path = Path(target_dir.replace('/', os.sep))
        
        # Make paths absolute
        if not source_path.is_absolute():
            source_path = self.project_root / source_path
        if not target_path.is_absolute():
            target_path = self.project_root / target_path
        
        try:
            if source_path.exists():
                if not self.dry_run:
                    # Ensure target parent directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy directory tree
                    if target_path.exists():
                        # Merge with existing directory
                        for item in source_path.rglob("*"):
                            if item.is_file():
                                relative_path = item.relative_to(source_path)
                                target_item = target_path / relative_path
                                target_item.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(item, target_item)
                    else:
                        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                
                self.logger.info(f"Migrated {source_path} to {target_path}")
                self._log_action("directory_migrated", str(source_path), str(target_path), "success")
                return True
            else:
                self.logger.warning(f"Source directory does not exist: {source_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Directory migration failed: {source_path} -> {target_path}: {e}")
            self._log_action("directory_migration_failed", str(source_path), str(target_path), "failed", str(e))
            return False
    
    def update_imports_in_file(self, file_path: Path) -> bool:
        """Update import statements in a single file."""
        try:
            # Skip non-text files
            if file_path.suffix not in ['.py', '.md', '.txt', '.json', '.yaml', '.yml']:
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            updated_content = original_content
            changes_made = False
            
            # Apply all import update patterns
            for pattern, replacement in self.import_patterns:
                new_content = re.sub(pattern, replacement, updated_content)
                if new_content != updated_content:
                    changes_made = True
                    updated_content = new_content
            
            # Write updated content if changes were made
            if changes_made and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
            
            if changes_made:
                self.logger.info(f"Updated imports in: {file_path}")
                self._log_action("imports_updated", str(file_path), "", "success")
            
            return changes_made
            
        except Exception as e:
            self.logger.error(f"Failed to update imports in {file_path}: {e}")
            self._log_action("import_update_failed", str(file_path), "", "failed", str(e))
            return False
    
    def update_all_imports(self) -> int:
        """Update imports in all relevant files."""
        files_to_update = []
        
        # Find all relevant files
        for pattern in ["src/**/*.py", "tests/**/*.py", "*.py", "**/*.md", "config/**/*"]:
            files_to_update.extend(self.project_root.glob(pattern))
        
        # Remove duplicates and non-files
        files_to_update = list(set([f for f in files_to_update if f.is_file()]))
        
        updated_count = 0
        for file_path in files_to_update:
            if self.update_imports_in_file(file_path):
                updated_count += 1
        
        self.logger.info(f"Updated imports in {updated_count} files")
        return updated_count
    
    def validate_migration(self) -> Dict[str, bool]:
        """Validate that migration was successful."""
        validation_results = {}
        
        # Check that target directories exist
        for source, target in self.migration_mapping.items():
            target_path = self.project_root / target.replace('/', os.sep)
            validation_results[f"target_exists_{target}"] = target_path.exists()
        
        # Test import capabilities
        test_modules = [
            "src.tools.pdf_tools",
            "src.tools.file_management", 
            "src.tools.metadata"
        ]
        
        for module in test_modules:
            try:
                sys.path.insert(0, str(self.project_root))
                spec = importlib.util.find_spec(module)
                validation_results[f"import_{module}"] = spec is not None
                if str(self.project_root) in sys.path:
                    sys.path.remove(str(self.project_root))
            except Exception:
                validation_results[f"import_{module}"] = False
        
        # Log validation results
        for test, result in validation_results.items():
            if result:
                self.logger.info(f"Validation passed: {test}")
            else:
                self.logger.error(f"Validation failed: {test}")
        
        return validation_results
    
    def _log_action(self, action: str, source: str, target: str, status: str, error: str = ""):
        """Log an action to the migration log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": source,
            "target": target,
            "status": status,
            "error": error
        }
        self.migration_log.append(log_entry)
    
    def generate_migration_report(self) -> str:
        """Generate comprehensive migration report."""
        report = {
            "migration_summary": {
                "start_time": self.migration_log[0]["timestamp"] if self.migration_log else "unknown",
                "end_time": datetime.now().isoformat(),
                "total_actions": len(self.migration_log),
                "successful_actions": len([l for l in self.migration_log if l["status"] == "success"]),
                "failed_actions": len([l for l in self.migration_log if l["status"] == "failed"]),
                "dry_run": self.dry_run,
                "backup_directory": self.backup_dir
            },
            "migration_mapping": self.migration_mapping,
            "detailed_log": self.migration_log
        }
        
        report_file = self.project_root / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not self.dry_run:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        
        self.logger.info(f"Migration report generated: {report_file}")
        return str(report_file)
    
    def execute_complete_migration(self) -> bool:
        """Execute the complete migration process."""
        self.logger.info("=== Starting Complete Migration Process ===")
        
        # Phase 1: Preparation
        self.logger.info("Phase 1: Preparation and Backup")
        if not self.create_complete_backup():
            self.logger.error("Backup creation failed - aborting migration")
            return False
        
        if not self.validate_source_structure():
            self.logger.error("Source validation failed - aborting migration")
            return False
        
        # Phase 2: Target Preparation
        self.logger.info("Phase 2: Target Structure Creation")
        if not self.create_target_structure():
            self.logger.error("Target structure creation failed - aborting migration")
            return False
        
        # Phase 3: File Migration
        self.logger.info("Phase 3: File Migration")
        migration_success = True
        for source, target in self.migration_mapping.items():
            if not self.migrate_directory_contents(source, target):
                migration_success = False
                self.logger.error(f"Failed to migrate {source} to {target}")
        
        if not migration_success:
            self.logger.error("File migration had failures - check logs")
        
        # Phase 4: Import Updates
        self.logger.info("Phase 4: Import Statement Updates")
        updated_files = self.update_all_imports()
        self.logger.info(f"Updated imports in {updated_files} files")
        
        # Phase 5: Validation
        self.logger.info("Phase 5: Migration Validation")
        validation_results = self.validate_migration()
        validation_passed = all(validation_results.values())
        
        if validation_passed:
            self.logger.info("Migration validation PASSED")
        else:
            self.logger.error("Migration validation FAILED")
            self.logger.error(f"Failed validations: {[k for k, v in validation_results.items() if not v]}")
        
        # Generate final report
        report_file = self.generate_migration_report()
        
        self.logger.info("=== Migration Process Complete ===")
        self.logger.info(f"Final report: {report_file}")
        self.logger.info(f"Backup directory: {self.backup_dir}")
        
        return validation_passed


def create_rollback_script(backup_dir: str):
    """Create a rollback script for the migration."""
    rollback_script = f'''#!/usr/bin/env python3
"""
Rollback Script for Migration: {backup_dir}
"""

import shutil
import os
from pathlib import Path

def rollback_migration():
    """Rollback the migration to previous state."""
    backup_path = Path("{backup_dir}")
    project_root = Path(__file__).parent
    
    if not backup_path.exists():
        print(f"ERROR: Backup directory not found: {{backup_path}}")
        return False
    
    print("Rolling back migration...")
    
    # Remove current tools directory
    tools_path = project_root / "src" / "tools"
    if tools_path.exists():
        shutil.rmtree(tools_path)
        print("Removed current tools directory")
    
    # Restore original directories
    restore_items = [
        ("src_original", "src"),
        ("tests_original", "tests"), 
        ("config_original", "config"),
        ("main_backup.py", "main.py"),
        ("requirements_backup.txt", "requirements.txt")
    ]
    
    for backup_item, target_item in restore_items:
        backup_item_path = backup_path / backup_item
        target_item_path = project_root / target_item
        
        if backup_item_path.exists():
            if target_item_path.exists():
                if target_item_path.is_dir():
                    shutil.rmtree(target_item_path)
                else:
                    target_item_path.unlink()
            
            if backup_item_path.is_dir():
                shutil.copytree(backup_item_path, target_item_path)
            else:
                shutil.copy2(backup_item_path, target_item_path)
            
            print(f"Restored {{backup_item}} to {{target_item}}")
    
    print("Rollback completed successfully")
    return True

if __name__ == "__main__":
    rollback_migration()
'''
    
    rollback_file = Path(__file__).parent / f"rollback_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(rollback_file, "w") as f:
        f.write(rollback_script)
    
    return str(rollback_file)


def main():
    """Main entry point for migration automation."""
    parser = argparse.ArgumentParser(description="Automated migration from src/utilities to src/tools")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--backup-dir", help="Custom backup directory path")
    
    args = parser.parse_args()
    
    # Create migration manager
    migration = MigrationAutomation(dry_run=args.dry_run, backup_dir=args.backup_dir)
    
    # Create rollback script
    rollback_script = create_rollback_script(migration.backup_dir)
    print(f"Rollback script created: {rollback_script}")
    
    # Execute migration
    success = migration.execute_complete_migration()
    
    if success:
        print("Migration completed successfully!")
        if not args.dry_run:
            print(f"Backup available at: {migration.backup_dir}")
            print(f"Rollback script: {rollback_script}")
    else:
        print("Migration failed - check logs for details")
        print(f"Backup available at: {migration.backup_dir}")
        print(f"Use rollback script if needed: {rollback_script}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())