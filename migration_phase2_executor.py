#!/usr/bin/env python3
"""
Phase 2: Migration Executor - File Migration
Execute the actual file migration from src/rfu to src with conflict resolution
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class MigrationPhase2:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_rfu = self.workspace_root / "src" / "rfu"
        self.src_main = self.workspace_root / "src"
        
        self.migration_log = []
        self.errors = []
        self.migrated_files = []
        self.skipped_files = []
        self.renamed_items = []
        
    def execute_phase2_file_migration(self):
        """Phase 2: Execute the actual file migration"""
        print("=" * 80)
        print("MIGRATION PHASE 2: FILE MIGRATION")
        print("=" * 80)
        
        try:
            # Step 1: Migrate individual files from src/rfu root
            self._migrate_root_files()
            
            # Step 2: Migrate directories with conflict resolution  
            self._migrate_directories()
            
            # Step 3: Verify migration completeness
            self._verify_migration()
            
            # Step 4: Generate migration report
            self._generate_migration_report()
            
            print("\n✅ Phase 2 completed successfully!")
            print(f"📊 Files migrated: {len(self.migrated_files)}")
            print(f"📊 Files skipped: {len(self.skipped_files)}")
            print(f"📊 Items renamed: {len(self.renamed_items)}")
            
            return True
            
        except Exception as e:
            self.errors.append(f"Phase 2 failed: {str(e)}")
            print(f"❌ Phase 2 failed: {e}")
            return False
    
    def _migrate_root_files(self):
        """Migrate files from src/rfu root to src root"""
        print("\n📁 Step 1: Migrating root files...")
        
        # Get all files in src/rfu root (not subdirectories)
        root_files = [f for f in self.src_rfu.iterdir() if f.is_file()]
        
        for file_path in root_files:
            target_path = self.src_main / file_path.name
            
            # Handle __init__.py conflict
            if file_path.name == "__init__.py":
                # Target already exists and is different, rename rfu version
                target_path = self.src_main / "__init___rfu.py"
                print(f"   🔄 {file_path.name} → {target_path.name} (conflict resolution)")
                self.renamed_items.append({
                    "original": str(file_path),
                    "new": str(target_path),
                    "reason": "init_conflict"
                })
            
            # Check if target already exists
            elif target_path.exists():
                print(f"   ⚠️ Skipping {file_path.name} (target exists)")
                self.skipped_files.append({
                    "file": str(file_path),
                    "reason": "target_exists",
                    "target": str(target_path)
                })
                continue
            
            # Perform the move
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"   ✅ Moved: {file_path.name}")
                self.migrated_files.append({
                    "source": str(file_path),
                    "target": str(target_path),
                    "size": target_path.stat().st_size if target_path.exists() else 0
                })
            except Exception as e:
                self.errors.append(f"Failed to move {file_path.name}: {str(e)}")
                print(f"   ❌ Failed to move {file_path.name}: {e}")
    
    def _migrate_directories(self):
        """Migrate directories from src/rfu to src with conflict resolution"""
        print("\n📁 Step 2: Migrating directories...")
        
        # Get all directories in src/rfu
        directories = [d for d in self.src_rfu.iterdir() if d.is_dir() and d.name != "__pycache__"]
        
        for dir_path in directories:
            target_path = self.src_main / dir_path.name
            
            # Handle core/ directory conflict
            if dir_path.name == "core":
                # Target already exists and conflicts, rename rfu version
                target_path = self.src_main / "core_rfu"
                print(f"   🔄 {dir_path.name}/ → {target_path.name}/ (conflict resolution)")
                self.renamed_items.append({
                    "original": str(dir_path),
                    "new": str(target_path),
                    "reason": "core_conflict"
                })
            
            # Handle other potential conflicts
            elif target_path.exists():
                # Check if we can merge or need to rename
                if self._can_merge_directories(dir_path, target_path):
                    print(f"   🔄 Merging {dir_path.name}/ with existing directory")
                    self._merge_directories(dir_path, target_path)
                    continue
                else:
                    # Rename to avoid conflict
                    target_path = self.src_main / f"{dir_path.name}_rfu"
                    print(f"   🔄 {dir_path.name}/ → {target_path.name}/ (conflict resolution)")
                    self.renamed_items.append({
                        "original": str(dir_path),
                        "new": str(target_path),
                        "reason": "merge_conflict"
                    })
            
            # Perform the move
            try:
                shutil.move(str(dir_path), str(target_path))
                print(f"   ✅ Moved: {dir_path.name}/")
                
                # Count files in moved directory
                file_count = len([f for f in target_path.rglob("*") if f.is_file()])
                self.migrated_files.append({
                    "source": str(dir_path),
                    "target": str(target_path),
                    "type": "directory",
                    "file_count": file_count
                })
                
            except Exception as e:
                self.errors.append(f"Failed to move {dir_path.name}/: {str(e)}")
                print(f"   ❌ Failed to move {dir_path.name}/: {e}")
    
    def _can_merge_directories(self, source_dir, target_dir):
        """Check if two directories can be safely merged"""
        try:
            # Get all file paths in both directories
            source_files = {f.relative_to(source_dir) for f in source_dir.rglob("*") if f.is_file()}
            target_files = {f.relative_to(target_dir) for f in target_dir.rglob("*") if f.is_file()}
            
            # Check for file conflicts
            conflicting_files = source_files.intersection(target_files)
            
            # Can merge if no file conflicts
            return len(conflicting_files) == 0
        except Exception:
            return False
    
    def _merge_directories(self, source_dir, target_dir):
        """Merge source directory into target directory"""
        print(f"      Merging {source_dir.name}/ into existing {target_dir.name}/")
        
        for item in source_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(source_dir)
                target_file = target_dir / relative_path
                
                # Create parent directories if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(item), str(target_file))
        
        # Remove empty source directory
        try:
            shutil.rmtree(source_dir)
        except Exception:
            pass  # Directory might not be empty due to __pycache__ etc.
    
    def _verify_migration(self):
        """Verify migration completeness"""
        print("\n✅ Step 3: Verifying migration...")
        
        # Check if src/rfu is now empty or only contains cache files
        remaining_items = list(self.src_rfu.rglob("*"))
        significant_remaining = [
            item for item in remaining_items 
            if item.is_file() and not any(part.startswith("__pycache__") for part in item.parts)
        ]
        
        print(f"   📊 Items remaining in src/rfu: {len(remaining_items)}")
        print(f"   📊 Significant items remaining: {len(significant_remaining)}")
        
        if significant_remaining:
            print("   ⚠️ Significant files still in src/rfu:")
            for item in significant_remaining[:5]:
                rel_path = item.relative_to(self.src_rfu)
                print(f"      • {rel_path}")
            if len(significant_remaining) > 5:
                print(f"      ... and {len(significant_remaining) - 5} more")
        
        # Verify key files are now in src
        key_files = ["config_manager.py", "hub.py", "log_manager.py"]
        for file_name in key_files:
            src_file = self.src_main / file_name
            if src_file.exists():
                print(f"   ✅ Verified: {file_name} is now in src/")
            else:
                print(f"   ❌ Missing: {file_name} not found in src/")
                self.errors.append(f"Key file {file_name} not found in target location")
        
        # Verify key directories
        key_dirs = ["file_explorer", "gui", "database"]
        for dir_name in key_dirs:
            src_dir = self.src_main / dir_name
            rfu_dir = self.src_main / f"{dir_name}_rfu"
            
            if src_dir.exists():
                print(f"   ✅ Verified: {dir_name}/ is now in src/")
            elif rfu_dir.exists():
                print(f"   ✅ Verified: {dir_name}/ is now in src/ as {dir_name}_rfu/")
            else:
                print(f"   ❌ Missing: {dir_name}/ not found in src/")
    
    def _generate_migration_report(self):
        """Generate comprehensive migration report"""
        print("\n📋 Step 4: Generating migration report...")
        
        report = {
            "phase": "file_migration",
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "statistics": {
                "files_migrated": len(self.migrated_files),
                "files_skipped": len(self.skipped_files),
                "items_renamed": len(self.renamed_items),
                "errors": len(self.errors)
            },
            "migrated_files": self.migrated_files,
            "skipped_files": self.skipped_files,
            "renamed_items": self.renamed_items,
            "errors": self.errors,
            "migration_log": self.migration_log
        }
        
        # Save report
        report_file = self.workspace_root / f"migration_phase2_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   💾 Report saved: {report_file}")


def main():
    workspace_root = Path(__file__).parent
    phase2 = MigrationPhase2(workspace_root)
    
    print("🚀 Starting Migration Phase 2...")
    print("⚠️  This will move files from src/rfu to src")
    print("⚠️  Conflicts will be resolved by renaming")
    
    # Check if backup exists
    backup_dirs = list(workspace_root.glob("MIGRATION_BACKUP_*"))
    if backup_dirs:
        latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)
        print(f"✅ Backup available: {latest_backup.name}")
    else:
        print("⚠️ No backup found - consider running Phase 1 first")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration aborted.")
            return 1
    
    success = phase2.execute_phase2_file_migration()
    
    if success:
        print("\n" + "="*80)
        print("✅ PHASE 2 COMPLETED SUCCESSFULLY")
        print("="*80)
        print("📋 Next Steps:")
        print("   1. Phase 3: Update import statements")
        print("   2. Phase 4: Test functionality")
        print("   3. Phase 5: Final cleanup")
        
        print("\n📊 Migration Summary:")
        print(f"   • Files migrated: {len(phase2.migrated_files)}")
        print(f"   • Files skipped: {len(phase2.skipped_files)}")
        print(f"   • Items renamed: {len(phase2.renamed_items)}")
        
        if phase2.renamed_items:
            print("\n📝 Renamed items:")
            for item in phase2.renamed_items:
                old_name = Path(item['original']).name
                new_name = Path(item['new']).name
                print(f"   • {old_name} → {new_name} ({item['reason']})")
        
    else:
        print("\n" + "="*80)
        print("❌ PHASE 2 FAILED")
        print("="*80)
        print("Some files may have been moved. Check backup for restore.")
        if phase2.errors:
            for error in phase2.errors:
                print(f"   • {error}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())