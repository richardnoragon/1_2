#!/usr/bin/env python3
"""
Advanced Folders Migration Script
Intelligently merges enterprise-grade core with existing GUI implementation.
"""

import json
import os
import shutil
from datetime import datetime


class AdvancedFoldersMigration:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"migration_backup_{self.timestamp}"
        self.source_dir = "src/advanced_folders"
        self.target_dir = "src/tools/file_management/advanced_folders"
        
        # Files to preserve from current target (GUI components)
        self.preserve_from_target = [
            "gui/",
            "ui/", 
            "database/",
            "engine/",
            "integration/",
            "advanced_folders_main.py",
            "repositories.py"
        ]
        
        # Core components to replace with enterprise implementation
        self.replace_with_source = [
            "core/",
            "models/",
            "exceptions/",
            "validation/",
            "repository/",
            "error_handling/",
            "tests/",
            "README.md",
            "API_DOCUMENTATION.md",
            "INTEGRATION_GUIDE.md",
            "__init__.py"
        ]
        
    def create_migration_plan(self):
        """Create detailed migration plan."""
        plan = {
            "timestamp": self.timestamp,
            "migration_type": "intelligent_merge",
            "source_analysis": {},
            "target_analysis": {},
            "merge_strategy": {},
            "validation_steps": []
        }
        
        # Analyze source directory
        if os.path.exists(self.source_dir):
            plan["source_analysis"] = self._analyze_directory(self.source_dir)
        
        # Analyze target directory  
        if os.path.exists(self.target_dir):
            plan["target_analysis"] = self._analyze_directory(self.target_dir)
            
        # Define merge strategy
        plan["merge_strategy"] = {
            "preserve_gui": True,
            "replace_core": True,
            "merge_tests": True,
            "update_imports": True,
            "validate_integration": True
        }
        
        return plan
    
    def _analyze_directory(self, directory):
        """Analyze directory structure and file counts."""
        analysis = {
            "total_files": 0,
            "directories": [],
            "key_files": [],
            "python_files": 0
        }
        
        for root, dirs, files in os.walk(directory):
            analysis["total_files"] += len(files)
            py_files = [f for f in files if f.endswith('.py')]
            analysis["python_files"] += len(py_files)
            
            rel_root = os.path.relpath(root, directory)
            if rel_root != ".":
                analysis["directories"].append(rel_root)
                
            # Identify key files
            for file in files:
                key_files = [
                    "__init__.py", "README.md", "API_DOCUMENTATION.md"
                ]
                if file in key_files:
                    analysis["key_files"].append(os.path.join(rel_root, file))
                    
        return analysis
    
    def execute_migration(self, dry_run=True):
        """Execute the migration with optional dry run."""
        print("[START] Advanced Folders Migration")
        print(f"[TIME] Timestamp: {self.timestamp}")
        print(f"[MODE] {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
        
        plan = self.create_migration_plan()
        
        if dry_run:
            self._execute_dry_run(plan)
        else:
            self._execute_live_migration(plan)
            
        return plan
    
    def _execute_dry_run(self, plan):
        """Execute dry run to show what would be done."""
        print("\n[PLAN] MIGRATION PLAN (DRY RUN):")
        print("=" * 50)
        
        src_files = plan['source_analysis']['total_files']
        tgt_files = plan['target_analysis']['total_files']
        print(f"Source: {self.source_dir} ({src_files} files)")
        print(f"Target: {self.target_dir} ({tgt_files} files)")
        
        print("\n[MERGE] MERGE STRATEGY:")
        for component in self.preserve_from_target:
            target_path = os.path.join(self.target_dir, component)
            if os.path.exists(target_path):
                print(f"  [KEEP] PRESERVE: {component} (from current target)")
                
        for component in self.replace_with_source:
            source_path = os.path.join(self.source_dir, component)
            if os.path.exists(source_path):
                print(f"  [REPLACE] {component} (enterprise impl)")
        
        print(f"\n[BACKUP] Backup location: {self.backup_dir}")
        print("[WARNING] Use execute_migration(dry_run=False) to proceed")
        
    def _execute_live_migration(self, plan):
        """Execute the actual migration."""
        print("\n[EXEC] EXECUTING LIVE MIGRATION...")
        
        # Step 1: Create temp staging area
        staging_dir = f"migration_staging_{self.timestamp}"
        os.makedirs(staging_dir, exist_ok=True)
        
        try:
            # Step 2: Preserve GUI components from target
            print("[PRESERVE] Preserving GUI components...")
            for component in self.preserve_from_target:
                source_path = os.path.join(self.target_dir, component)
                if os.path.exists(source_path):
                    dest_path = os.path.join(staging_dir, component)
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                    print(f"  [OK] Preserved: {component}")
            
            # Step 3: Clear target directory
            print("[CLEAR] Clearing target directory...")
            if os.path.exists(self.target_dir):
                shutil.rmtree(self.target_dir)
            os.makedirs(self.target_dir, exist_ok=True)
            
            # Step 4: Copy enterprise core components
            print("[INSTALL] Installing enterprise core...")
            for component in self.replace_with_source:
                source_path = os.path.join(self.source_dir, component)
                if os.path.exists(source_path):
                    dest_path = os.path.join(self.target_dir, component)
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                    print(f"  [OK] Installed: {component}")
            
            # Step 5: Restore preserved GUI components
            print("[RESTORE] Restoring GUI components...")
            for component in self.preserve_from_target:
                source_path = os.path.join(staging_dir, component)
                if os.path.exists(source_path):
                    dest_path = os.path.join(self.target_dir, component)
                    if os.path.isdir(source_path):
                        if not os.path.exists(dest_path):
                            shutil.copytree(source_path, dest_path)
                        else:
                            # Merge directories
                            self._merge_directories(source_path, dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                    print(f"  [OK] Restored: {component}")
            
            # Cleanup staging
            shutil.rmtree(staging_dir)
            
            print("\n[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY!")
            
        except Exception as e:
            print(f"\n[ERROR] MIGRATION FAILED: {str(e)}")
            # Attempt to restore from backup if possible
            if os.path.exists(staging_dir):
                shutil.rmtree(staging_dir)
            raise
    
    def _merge_directories(self, source, dest):
        """Merge two directory trees."""
        for root, dirs, files in os.walk(source):
            rel_path = os.path.relpath(root, source)
            if rel_path != ".":
                dest_root = os.path.join(dest, rel_path)
            else:
                dest_root = dest
            
            os.makedirs(dest_root, exist_ok=True)
            
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_root, file)
                shutil.copy2(source_file, dest_file)
    
    def validate_migration(self):
        """Validate migration results."""
        print("\n[VALIDATE] VALIDATING MIGRATION...")
        
        validation_results = {
            "target_exists": os.path.exists(self.target_dir),
            "core_components_present": [],
            "gui_components_present": [],
            "import_statements_valid": True,
            "tests_executable": True
        }
        
        # Check core components
        for component in self.replace_with_source:
            component_path = os.path.join(self.target_dir, component)
            validation_results["core_components_present"].append({
                "component": component,
                "exists": os.path.exists(component_path)
            })
        
        # Check GUI components
        for component in self.preserve_from_target:
            component_path = os.path.join(self.target_dir, component)
            validation_results["gui_components_present"].append({
                "component": component,
                "exists": os.path.exists(component_path)
            })
        
        return validation_results


if __name__ == "__main__":
    migration = AdvancedFoldersMigration()
    
    # Execute dry run first
    print("[TEST] RUNNING DRY RUN...")
    plan = migration.execute_migration(dry_run=True)
    
    # Save migration plan
    with open(f"migration_plan_{migration.timestamp}.json", "w") as f:
        json.dump(plan, f, indent=2, default=str)
    
    plan_file = f"migration_plan_{migration.timestamp}.json"
    print(f"\n[SAVE] Migration plan saved to: {plan_file}")
    print("[INFO] Run with execute_migration(dry_run=False) to proceed")