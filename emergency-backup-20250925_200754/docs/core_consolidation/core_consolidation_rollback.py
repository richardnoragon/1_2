#!/usr/bin/env python3
"""
Core Consolidation Migration Rollback Script
Provides rollback functionality for the core consolidation migration

Date: September 17, 2025
Project: Richard's File Utilities (RFU)
Purpose: Rollback core consolidation migration if issues arise
"""

import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class CoreConsolidationRollback:
    """Handles rollback of the core consolidation migration."""
    
    def __init__(self, workspace_root: Path):
        """Initialize the rollback handler.
        
        Args:
            workspace_root: Path to the workspace root directory
        """
        self.workspace_root = Path(workspace_root)
        self.src_path = self.workspace_root / "src"
        self.core_path = self.src_path / "core"
        self.core_rfu_path = self.src_path / "core_rfu"
        self.docs_path = self.workspace_root / "docs" / "core_consolidation"
        
        # Rollback state tracking
        self.rollback_state = {
            "phase": "initialization",
            "timestamp": datetime.now().isoformat(),
            "source_backup": None,
            "files_restored": [],
            "errors": []
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.docs_path / f"rollback_log_{timestamp}.txt"
    
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
    
    def find_migration_backup(self) -> Path:
        """Find the most recent migration backup.
        
        Returns:
            Path to the backup directory, or None if not found
        """
        self.log_message("=== LOCATING MIGRATION BACKUP ===")
        
        # Check migration state file first
        state_file = self.docs_path / "migration_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                backup_location = state.get("backup_location")
                if backup_location and Path(backup_location).exists():
                    self.log_message(f"✅ Found backup from state file: {backup_location}")
                    return Path(backup_location)
            except Exception as e:
                self.log_message(f"WARNING: Could not read state file: {e}", "WARNING")
        
        # Search for backup directories
        backup_pattern = "migration_backup_core_consolidation_*"
        backup_dirs = list(self.workspace_root.glob(backup_pattern))
        
        if not backup_dirs:
            self.log_message("ERROR: No migration backup directories found", "ERROR")
            return None
        
        # Use the most recent backup
        most_recent = max(backup_dirs, key=lambda p: p.stat().st_mtime)
        self.log_message(f"✅ Found most recent backup: {most_recent}")
        return most_recent
    
    def validate_backup(self, backup_dir: Path) -> bool:
        """Validate that the backup contains required files.
        
        Args:
            backup_dir: Path to the backup directory
            
        Returns:
            True if backup is valid
        """
        self.log_message("=== VALIDATING BACKUP ===")
        
        required_dirs = ["core_original", "core_rfu_original"]
        
        for req_dir in required_dirs:
            backup_subdir = backup_dir / req_dir
            if not backup_subdir.exists():
                self.log_message(f"ERROR: Missing required backup: {backup_subdir}", "ERROR")
                return False
            
            # Check that backup contains Python files
            py_files = list(backup_subdir.glob("*.py"))
            if not py_files:
                self.log_message(f"WARNING: No Python files in {backup_subdir}", "WARNING")
            else:
                self.log_message(f"✅ Found {len(py_files)} Python files in {backup_subdir}")
        
        # Check for backup manifest
        manifest_file = backup_dir / "backup_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                self.log_message("✅ Backup manifest validated")
                return True
            except Exception as e:
                self.log_message(f"WARNING: Could not read manifest: {e}", "WARNING")
        
        self.log_message("✅ Backup validation completed")
        return True
    
    def execute_rollback(self, backup_dir: Path) -> bool:
        """Execute the rollback process.
        
        Args:
            backup_dir: Path to the backup directory
            
        Returns:
            True if rollback was successful
        """
        self.log_message("=== EXECUTING ROLLBACK ===")
        self.rollback_state["phase"] = "rollback_execution"
        self.rollback_state["source_backup"] = str(backup_dir)
        
        try:
            # Remove current core directory if it exists
            if self.core_path.exists():
                self.log_message(f"Removing current core directory: {self.core_path}")
                shutil.rmtree(self.core_path)
                self.log_message("✅ Current core directory removed")
            
            # Restore original core directory
            core_backup = backup_dir / "core_original"
            if core_backup.exists():
                shutil.copytree(core_backup, self.core_path)
                self.log_message(f"✅ Restored core directory from {core_backup}")
                
                # Count restored files
                restored_files = list(self.core_path.rglob("*.py"))
                self.rollback_state["files_restored"].extend([str(f) for f in restored_files])
                self.log_message(f"✅ Restored {len(restored_files)} Python files to core")
            
            # Restore core_rfu directory
            core_rfu_backup = backup_dir / "core_rfu_original"
            if core_rfu_backup.exists():
                if self.core_rfu_path.exists():
                    shutil.rmtree(self.core_rfu_path)
                
                shutil.copytree(core_rfu_backup, self.core_rfu_path)
                self.log_message(f"✅ Restored core_rfu directory from {core_rfu_backup}")
                
                # Count restored files
                restored_files = list(self.core_rfu_path.rglob("*.py"))
                self.rollback_state["files_restored"].extend([str(f) for f in restored_files])
                self.log_message(f"✅ Restored {len(restored_files)} Python files to core_rfu")
            
            # Clean up any __pycache__ directories
            for cache_dir in self.src_path.rglob("__pycache__"):
                if cache_dir.is_dir():
                    shutil.rmtree(cache_dir)
                    self.log_message(f"✅ Cleaned up {cache_dir}")
            
            self.rollback_state["phase"] = "rollback_completed"
            self.log_message("✅ Rollback execution completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Rollback execution failed: {e}", "ERROR")
            self.rollback_state["errors"].append(f"Rollback execution failed: {str(e)}")
            self.rollback_state["phase"] = "rollback_failed"
            return False
    
    def validate_rollback(self) -> bool:
        """Validate that the rollback was successful.
        
        Returns:
            True if validation passes
        """
        self.log_message("=== VALIDATING ROLLBACK ===")
        
        try:
            # Check that both directories exist
            if not self.core_path.exists():
                self.log_message("ERROR: Core directory not restored", "ERROR")
                return False
            
            if not self.core_rfu_path.exists():
                self.log_message("ERROR: Core RFU directory not restored", "ERROR")
                return False
            
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
            
            # Test core_rfu availability (should exist as directory)
            core_rfu_files = list(self.core_rfu_path.glob("*.py"))
            if core_rfu_files:
                self.log_message(f"✅ Core RFU directory contains {len(core_rfu_files)} Python files")
            else:
                self.log_message("WARNING: Core RFU directory is empty", "WARNING")
            
            self.log_message("✅ Rollback validation completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Rollback validation failed: {e}", "ERROR")
            self.rollback_state["errors"].append(f"Validation failed: {str(e)}")
            return False
    
    def save_rollback_state(self):
        """Save rollback state to JSON file."""
        state_file = self.docs_path / "rollback_state.json"
        self.rollback_state["last_updated"] = datetime.now().isoformat()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.rollback_state, f, indent=2)
    
    def run_rollback(self, backup_dir: Path = None) -> bool:
        """Run the complete rollback process.
        
        Args:
            backup_dir: Optional specific backup directory to use
            
        Returns:
            True if rollback was successful
        """
        self.log_message("=== STARTING CORE CONSOLIDATION ROLLBACK ===")
        self.log_message(f"Workspace: {self.workspace_root}")
        
        try:
            # Find backup if not provided
            if backup_dir is None:
                backup_dir = self.find_migration_backup()
                if backup_dir is None:
                    self.log_message("FAILED: No backup found for rollback", "ERROR")
                    return False
            
            # Validate backup
            if not self.validate_backup(backup_dir):
                self.log_message("FAILED: Backup validation failed", "ERROR")
                return False
            
            # Execute rollback
            if not self.execute_rollback(backup_dir):
                self.log_message("FAILED: Rollback execution failed", "ERROR")
                return False
            
            # Validate rollback
            if not self.validate_rollback():
                self.log_message("FAILED: Rollback validation failed", "ERROR")
                return False
            
            self.rollback_state["phase"] = "rollback_successful"
            self.rollback_state["completion_time"] = datetime.now().isoformat()
            self.save_rollback_state()
            
            self.log_message("=== ROLLBACK COMPLETED SUCCESSFULLY ===")
            self.log_message(f"Rollback log: {self.log_file}")
            self.log_message(f"State file: {self.docs_path / 'rollback_state.json'}")
            
            return True
            
        except Exception as e:
            self.log_message(f"CRITICAL ERROR: Rollback process failed: {e}", "ERROR")
            self.rollback_state["phase"] = "rollback_critical_failure"
            self.rollback_state["errors"].append(f"Critical failure: {str(e)}")
            self.save_rollback_state()
            return False


def main():
    """Main execution function."""
    # Get workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    
    print("🔄 Core Consolidation Migration Rollback Script")
    print(f"📁 Workspace: {workspace_root}")
    print("=" * 60)
    
    # Initialize rollback handler
    rollback_handler = CoreConsolidationRollback(workspace_root)
    
    # Find available backups
    backup_dir = rollback_handler.find_migration_backup()
    if backup_dir is None:
        print("❌ No migration backup found. Cannot proceed with rollback.")
        return False
    
    print(f"📦 Found backup: {backup_dir}")
    
    # Confirm rollback
    print("\n⚠️  This will restore the original src/core and src/core_rfu directories")
    print("   Any changes made after the migration will be lost")
    
    response = input("\n🤔 Do you want to proceed with rollback? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Rollback cancelled by user")
        return False
    
    # Execute rollback
    success = rollback_handler.run_rollback(backup_dir)
    
    if success:
        print("\n🎉 Rollback completed successfully!")
        print("📊 Original directory structure has been restored")
        print(f"📝 Rollback log: {rollback_handler.log_file}")
        return True
    else:
        print("\n❌ Rollback failed!")
        print(f"📝 Check rollback log: {rollback_handler.log_file}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)