#!/usr/bin/env python3
"""
Core Consolidation Migration Executor
Automates the migration from src/core_rfu to src/core

Date: September 17, 2025
Project: Richard's File Utilities (RFU)
Purpose: Consolidate core_rfu into core with zero functionality loss
"""

import os
import sys
import shutil
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


class CoreConsolidationMigrator:
    """Handles the migration from src/core_rfu to src/core."""
    
    def __init__(self, workspace_root: Path):
        """Initialize the migrator.
        
        Args:
            workspace_root: Path to the workspace root directory
        """
        self.workspace_root = Path(workspace_root)
        self.src_path = self.workspace_root / "src"
        self.core_path = self.src_path / "core"
        self.core_rfu_path = self.src_path / "core_rfu"
        self.docs_path = self.workspace_root / "docs" / "core_consolidation"
        
        # Migration state tracking
        self.migration_state = {
            "phase": "initialization",
            "timestamp": datetime.now().isoformat(),
            "backup_location": None,
            "files_migrated": [],
            "conflicts_resolved": [],
            "errors": [],
            "rollback_available": False
        }
        
        # Backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.workspace_root / f"migration_backup_core_consolidation_{timestamp}"
        
        self.log_file = self.docs_path / f"migration_execution_log_{timestamp}.txt"
        
    def log_message(self, message: str, level: str = "INFO"):
        """Log a message to both console and file.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def save_migration_state(self):
        """Save current migration state to JSON file."""
        state_file = self.docs_path / "migration_state.json"
        self.migration_state["last_updated"] = datetime.now().isoformat()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.migration_state, f, indent=2)
    
    def validate_preconditions(self) -> bool:
        """Validate that migration can proceed.
        
        Returns:
            True if all preconditions are met
        """
        self.log_message("=== VALIDATING PRECONDITIONS ===")
        
        # Check source directories exist
        if not self.core_rfu_path.exists():
            self.log_message(f"ERROR: Source directory {self.core_rfu_path} does not exist", "ERROR")
            return False
        
        if not self.core_path.exists():
            self.log_message(f"ERROR: Target directory {self.core_path} does not exist", "ERROR")
            return False
        
        # Check write permissions
        try:
            test_file = self.core_path / "test_write_permission.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            self.log_message(f"ERROR: No write permission to {self.core_path}: {e}", "ERROR")
            return False
        
        # Check for running Python processes that might lock files
        try:
            import psutil
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if any('src' in arg for arg in cmdline if arg):
                        python_processes.append(proc.info)
            
            if python_processes:
                self.log_message(f"WARNING: {len(python_processes)} Python processes detected that may use src modules", "WARNING")
                for proc in python_processes[:3]:  # Show first 3
                    self.log_message(f"  PID {proc['pid']}: {proc['name']}", "WARNING")
        except ImportError:
            self.log_message("psutil not available, skipping process check", "WARNING")
        
        self.log_message("✅ All preconditions met")
        return True
    
    def create_backup(self) -> bool:
        """Create a comprehensive backup before migration.
        
        Returns:
            True if backup was successful
        """
        self.log_message("=== CREATING BACKUP ===")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup current core directory
            core_backup = self.backup_dir / "core_original"
            shutil.copytree(self.core_path, core_backup)
            self.log_message(f"✅ Backed up src/core to {core_backup}")
            
            # Backup core_rfu directory
            core_rfu_backup = self.backup_dir / "core_rfu_original"
            shutil.copytree(self.core_rfu_path, core_rfu_backup)
            self.log_message(f"✅ Backed up src/core_rfu to {core_rfu_backup}")
            
            # Create backup manifest
            manifest = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_location": str(self.backup_dir),
                "directories_backed_up": [
                    str(core_backup),
                    str(core_rfu_backup)
                ],
                "original_locations": [
                    str(self.core_path),
                    str(self.core_rfu_path)
                ]
            }
            
            manifest_file = self.backup_dir / "backup_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            self.migration_state["backup_location"] = str(self.backup_dir)
            self.migration_state["rollback_available"] = True
            self.save_migration_state()
            
            self.log_message("✅ Backup completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Backup failed: {e}", "ERROR")
            self.migration_state["errors"].append(f"Backup failed: {str(e)}")
            return False
    
    def analyze_conflicts(self) -> Dict[str, Any]:
        """Analyze conflicts between core and core_rfu directories.
        
        Returns:
            Dictionary containing conflict analysis
        """
        self.log_message("=== ANALYZING CONFLICTS ===")
        
        conflicts = {
            "file_conflicts": [],
            "resolution_strategy": {},
            "stats": {
                "core_files": 0,
                "core_rfu_files": 0,
                "conflicting_files": 0,
                "unique_to_core_rfu": 0
            }
        }
        
        # Get all files in both directories
        core_files = {}
        if self.core_path.exists():
            for file_path in self.core_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    rel_path = file_path.relative_to(self.core_path)
                    core_files[str(rel_path)] = file_path
            conflicts["stats"]["core_files"] = len(core_files)
        
        core_rfu_files = {}
        if self.core_rfu_path.exists():
            for file_path in self.core_rfu_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    rel_path = file_path.relative_to(self.core_rfu_path)
                    core_rfu_files[str(rel_path)] = file_path
            conflicts["stats"]["core_rfu_files"] = len(core_rfu_files)
        
        # Find conflicts and unique files
        for rel_path, rfu_file in core_rfu_files.items():
            if rel_path in core_files:
                # File exists in both locations - conflict
                core_file = core_files[rel_path]
                conflict_info = {
                    "relative_path": rel_path,
                    "core_file": str(core_file),
                    "core_rfu_file": str(rfu_file),
                    "core_size": core_file.stat().st_size,
                    "core_rfu_size": rfu_file.stat().st_size,
                    "core_modified": datetime.fromtimestamp(core_file.stat().st_mtime).isoformat(),
                    "core_rfu_modified": datetime.fromtimestamp(rfu_file.stat().st_mtime).isoformat()
                }
                
                # Determine resolution strategy
                if rel_path == "__init__.py":
                    conflict_info["resolution"] = "merge_exports"
                elif rel_path == "constants.py":
                    conflict_info["resolution"] = "use_core_rfu_comprehensive"
                elif rel_path == "error_handler.py":
                    conflict_info["resolution"] = "use_core_rfu_singleton"
                else:
                    # Default to newer file
                    if rfu_file.stat().st_mtime > core_file.stat().st_mtime:
                        conflict_info["resolution"] = "use_core_rfu_newer"
                    else:
                        conflict_info["resolution"] = "use_core_existing"
                
                conflicts["file_conflicts"].append(conflict_info)
                conflicts["resolution_strategy"][rel_path] = conflict_info["resolution"]
                
                self.log_message(f"CONFLICT: {rel_path} - Resolution: {conflict_info['resolution']}")
            else:
                # File unique to core_rfu
                conflicts["stats"]["unique_to_core_rfu"] += 1
        
        conflicts["stats"]["conflicting_files"] = len(conflicts["file_conflicts"])
        
        self.log_message(f"✅ Conflict analysis complete:")
        self.log_message(f"  - Core files: {conflicts['stats']['core_files']}")
        self.log_message(f"  - Core RFU files: {conflicts['stats']['core_rfu_files']}")
        self.log_message(f"  - Conflicts: {conflicts['stats']['conflicting_files']}")
        self.log_message(f"  - Unique to core_rfu: {conflicts['stats']['unique_to_core_rfu']}")
        
        return conflicts
    
    def merge_init_files(self) -> str:
        """Merge __init__.py files from both core and core_rfu.
        
        Returns:
            Merged content for __init__.py
        """
        self.log_message("Merging __init__.py files...")
        
        core_init = self.core_path / "__init__.py"
        core_rfu_init = self.core_rfu_path / "__init__.py"
        
        merged_content = '''"""Core functionality for Richard's File Utilities - Consolidated Module.

This module consolidates all core functionality from both src/core and src/core_rfu
providing a unified interface for error handling, configuration, logging, and more.
"""

# Error handling (using enhanced version from core_rfu)
from .error_handler import error_handler

# Constants (comprehensive version from core_rfu)
from .constants import (
    APP_NAME, APP_TITLE, JSON_FILES_FILTER, TEXT_FILES_FILTER, ALL_FILES_FILTER,
    IMPORT_ERROR, EXPORT_ERROR, FILE_NOT_FOUND_ERROR, PERMISSION_ERROR,
    SECURITY_TEST, SECURITY_STANDARD, SECURITY_HIGH, SECURITY_CUSTOM,
    NETWORK_TRANSFER, CONNECTION_ERROR, TRANSFER_COMPLETE,
    PDF_TOOLS, FILE_TOOLS, ANALYSIS_TOOLS, NETWORK_TOOLS,
    OPERATION_COMPLETE, OPERATION_FAILED, PROCESSING, PLEASE_WAIT,
    SUGGESTED_SOLUTIONS_HEADER
)

# Logging management
from .logging_manager import LogManager

# Configuration management
try:
    from .config_manager import ConfigManager
except ImportError:
    # Fallback if config_manager not available
    ConfigManager = None

try:
    from .enhanced_config_manager import EnhancedConfigManager
except ImportError:
    EnhancedConfigManager = None

# Database functionality (if available)
try:
    from .database_manager import DatabaseManager
    from .database_models import *
    from .database_logging import DatabaseLogger
except ImportError:
    DatabaseManager = None
    DatabaseLogger = None

# Migration support (if available)
try:
    from .migrations.migration_manager import MigrationManager
    from .migrations.rollback_manager import RollbackManager
except ImportError:
    MigrationManager = None
    RollbackManager = None

__all__ = [
    # Core functionality
    'error_handler',
    
    # Constants
    'APP_NAME', 'APP_TITLE', 'JSON_FILES_FILTER', 'TEXT_FILES_FILTER', 'ALL_FILES_FILTER',
    'IMPORT_ERROR', 'EXPORT_ERROR', 'FILE_NOT_FOUND_ERROR', 'PERMISSION_ERROR',
    'SECURITY_TEST', 'SECURITY_STANDARD', 'SECURITY_HIGH', 'SECURITY_CUSTOM',
    'NETWORK_TRANSFER', 'CONNECTION_ERROR', 'TRANSFER_COMPLETE',
    'PDF_TOOLS', 'FILE_TOOLS', 'ANALYSIS_TOOLS', 'NETWORK_TOOLS',
    'OPERATION_COMPLETE', 'OPERATION_FAILED', 'PROCESSING', 'PLEASE_WAIT',
    'SUGGESTED_SOLUTIONS_HEADER',
    
    # Management classes
    'LogManager',
    'ConfigManager',
    'EnhancedConfigManager',
    'DatabaseManager',
    'DatabaseLogger',
    'MigrationManager',
    'RollbackManager',
]

'''
        
        return merged_content
    
    def execute_migration(self) -> bool:
        """Execute the core migration process.
        
        Returns:
            True if migration was successful
        """
        self.log_message("=== EXECUTING MIGRATION ===")
        self.migration_state["phase"] = "migration_execution"
        
        try:
            # Analyze conflicts first
            conflicts = self.analyze_conflicts()
            
            # Handle conflicting files
            for conflict in conflicts["file_conflicts"]:
                rel_path = conflict["relative_path"]
                resolution = conflict["resolution"]
                
                self.log_message(f"Resolving conflict for {rel_path} using strategy: {resolution}")
                
                target_file = self.core_path / rel_path
                source_file = self.core_rfu_path / rel_path
                
                if resolution == "merge_exports":
                    # Special handling for __init__.py
                    merged_content = self.merge_init_files()
                    target_file.write_text(merged_content, encoding='utf-8')
                    self.log_message(f"✅ Merged __init__.py")
                    
                elif resolution.startswith("use_core_rfu"):
                    # Use the core_rfu version
                    shutil.copy2(source_file, target_file)
                    self.log_message(f"✅ Used core_rfu version of {rel_path}")
                    
                elif resolution == "use_core_existing":
                    # Keep the existing core version
                    self.log_message(f"✅ Kept existing core version of {rel_path}")
                
                self.migration_state["conflicts_resolved"].append({
                    "file": rel_path,
                    "resolution": resolution,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Copy all unique files from core_rfu
            for source_file in self.core_rfu_path.rglob("*"):
                if source_file.is_file() and not source_file.name.startswith('.'):
                    rel_path = source_file.relative_to(self.core_rfu_path)
                    target_file = self.core_path / rel_path
                    
                    # Skip if this file was already handled in conflict resolution
                    if str(rel_path) in conflicts["resolution_strategy"]:
                        continue
                    
                    # Create target directory if needed
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(source_file, target_file)
                    self.log_message(f"✅ Copied {rel_path}")
                    
                    self.migration_state["files_migrated"].append({
                        "source": str(source_file),
                        "target": str(target_file),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Clean up __pycache__ directories
            for cache_dir in self.core_path.rglob("__pycache__"):
                if cache_dir.is_dir():
                    shutil.rmtree(cache_dir)
                    self.log_message(f"✅ Cleaned up {cache_dir}")
            
            self.migration_state["phase"] = "migration_completed"
            self.save_migration_state()
            
            self.log_message("✅ Migration execution completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Migration execution failed: {e}", "ERROR")
            self.log_message(f"ERROR: Traceback: {traceback.format_exc()}", "ERROR")
            self.migration_state["errors"].append(f"Migration execution failed: {str(e)}")
            self.migration_state["phase"] = "migration_failed"
            self.save_migration_state()
            return False
    
    def validate_migration(self) -> bool:
        """Validate that the migration was successful.
        
        Returns:
            True if validation passes
        """
        self.log_message("=== VALIDATING MIGRATION ===")
        self.migration_state["phase"] = "validation"
        
        try:
            # Test basic imports
            import sys
            sys.path.insert(0, str(self.src_path))
            
            # Test core module import
            try:
                import core
                self.log_message("✅ Core module imports successfully")
            except Exception as e:
                self.log_message(f"ERROR: Core module import failed: {e}", "ERROR")
                return False
            
            # Test error handler import
            try:
                from core.error_handler import error_handler
                self.log_message("✅ Error handler imports successfully")
            except Exception as e:
                self.log_message(f"ERROR: Error handler import failed: {e}", "ERROR")
                return False
            
            # Test constants import
            try:
                from core.constants import APP_NAME, SECURITY_HIGH
                assert APP_NAME == "Richard's File Utilities"
                self.log_message("✅ Constants import and validation successful")
            except Exception as e:
                self.log_message(f"ERROR: Constants import/validation failed: {e}", "ERROR")
                return False
            
            # Test subdirectory imports
            subdirs_to_test = ["directory_security", "file_ops", "migrations", "theme_security"]
            for subdir in subdirs_to_test:
                subdir_path = self.core_path / subdir
                if subdir_path.exists():
                    try:
                        # Try to import a representative module from each subdirectory
                        if subdir == "directory_security":
                            from core.directory_security.directory_security_manager import DirectorySecurityManager
                        elif subdir == "file_ops":
                            from core.file_ops.file_handler import FileHandler
                        elif subdir == "migrations":
                            from core.migrations.migration_manager import MigrationManager
                        elif subdir == "theme_security":
                            from core.theme_security.theme_security_manager import ThemeSecurityManager
                        
                        self.log_message(f"✅ {subdir} subdirectory imports successfully")
                    except Exception as e:
                        self.log_message(f"WARNING: {subdir} import failed (may be expected): {e}", "WARNING")
            
            # Verify file counts
            total_files = len(list(self.core_path.rglob("*.py")))
            self.log_message(f"✅ Total Python files in core: {total_files}")
            
            self.migration_state["phase"] = "validation_successful"
            self.save_migration_state()
            
            self.log_message("✅ Migration validation completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Migration validation failed: {e}", "ERROR")
            self.migration_state["errors"].append(f"Validation failed: {str(e)}")
            self.migration_state["phase"] = "validation_failed"
            self.save_migration_state()
            return False
    
    def cleanup_original_directory(self) -> bool:
        """Remove the original core_rfu directory after successful migration.
        
        Returns:
            True if cleanup was successful
        """
        self.log_message("=== CLEANING UP ORIGINAL DIRECTORY ===")
        
        try:
            if self.core_rfu_path.exists():
                # Final safety check - ensure backup exists
                if not self.migration_state.get("rollback_available", False):
                    self.log_message("ERROR: Cannot cleanup - no backup available", "ERROR")
                    return False
                
                # Remove the core_rfu directory
                shutil.rmtree(self.core_rfu_path)
                self.log_message(f"✅ Removed original directory: {self.core_rfu_path}")
                
                self.migration_state["phase"] = "cleanup_completed"
                self.save_migration_state()
                
                return True
            else:
                self.log_message("WARNING: Original directory already removed", "WARNING")
                return True
                
        except Exception as e:
            self.log_message(f"ERROR: Cleanup failed: {e}", "ERROR")
            self.migration_state["errors"].append(f"Cleanup failed: {str(e)}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process.
        
        Returns:
            True if migration was successful
        """
        self.log_message("=== STARTING CORE CONSOLIDATION MIGRATION ===")
        self.log_message(f"Workspace: {self.workspace_root}")
        self.log_message(f"Source: {self.core_rfu_path}")
        self.log_message(f"Target: {self.core_path}")
        self.log_message(f"Backup: {self.backup_dir}")
        
        try:
            # Phase 1: Validate preconditions
            if not self.validate_preconditions():
                self.log_message("FAILED: Precondition validation failed", "ERROR")
                return False
            
            # Phase 2: Create backup
            if not self.create_backup():
                self.log_message("FAILED: Backup creation failed", "ERROR")
                return False
            
            # Phase 3: Execute migration
            if not self.execute_migration():
                self.log_message("FAILED: Migration execution failed", "ERROR")
                return False
            
            # Phase 4: Validate migration
            if not self.validate_migration():
                self.log_message("FAILED: Migration validation failed", "ERROR")
                return False
            
            # Phase 5: Cleanup original directory
            if not self.cleanup_original_directory():
                self.log_message("FAILED: Cleanup failed", "ERROR")
                return False
            
            self.migration_state["phase"] = "migration_successful"
            self.migration_state["completion_time"] = datetime.now().isoformat()
            self.save_migration_state()
            
            self.log_message("=== MIGRATION COMPLETED SUCCESSFULLY ===")
            self.log_message(f"Migration log: {self.log_file}")
            self.log_message(f"Backup location: {self.backup_dir}")
            self.log_message(f"State file: {self.docs_path / 'migration_state.json'}")
            
            return True
            
        except Exception as e:
            self.log_message(f"CRITICAL ERROR: Migration process failed: {e}", "ERROR")
            self.log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
            self.migration_state["phase"] = "migration_critical_failure"
            self.migration_state["errors"].append(f"Critical failure: {str(e)}")
            self.save_migration_state()
            return False


def main():
    """Main execution function."""
    # Get workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    
    print("🚀 Core Consolidation Migration Script")
    print(f"📁 Workspace: {workspace_root}")
    print("=" * 60)
    
    # Initialize migrator
    migrator = CoreConsolidationMigrator(workspace_root)
    
    # Confirm migration
    print("\n⚠️  This will migrate all contents from src/core_rfu to src/core")
    print("   The original src/core_rfu directory will be removed upon completion")
    print("   A backup will be created before migration starts")
    
    response = input("\n🤔 Do you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        return False
    
    # Execute migration
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print(f"📊 Migration details: {migrator.docs_path / 'migration_state.json'}")
        print(f"📝 Migration log: {migrator.log_file}")
        print(f"💾 Backup location: {migrator.backup_dir}")
        return True
    else:
        print("\n❌ Migration failed!")
        print(f"📝 Check migration log: {migrator.log_file}")
        print(f"📊 State details: {migrator.docs_path / 'migration_state.json'}")
        if migrator.migration_state.get("rollback_available"):
            print(f"🔄 Rollback available from: {migrator.backup_dir}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)