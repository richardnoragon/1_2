#!/usr/bin/env python3
"""
Phase 1: Migration Executor - Backup and Conflict Resolution
Safely execute the src/rfu → src migration with comprehensive error handling
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class MigrationExecutor:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_rfu = self.workspace_root / "src" / "rfu"
        self.src_main = self.workspace_root / "src"
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.workspace_root / f"MIGRATION_BACKUP_{timestamp}"
        
        self.migration_log = []
        self.errors = []
        
    def execute_phase1_backup_and_conflicts(self):
        """Phase 1: Create backups and resolve conflicts"""
        print("=" * 80)
        print("MIGRATION PHASE 1: BACKUP AND CONFLICT RESOLUTION")
        print("=" * 80)
        
        try:
            # Step 1: Create comprehensive backup
            self._create_comprehensive_backup()
            
            # Step 2: Analyze conflicts in detail
            conflicts = self._analyze_conflicts_detailed()
            
            # Step 3: Resolve conflicts safely
            self._resolve_conflicts_safely(conflicts)
            
            # Step 4: Verify backup integrity
            self._verify_backup_integrity()
            
            print("\n✅ Phase 1 completed successfully!")
            print(f"📁 Backup location: {self.backup_dir}")
            
            return True
            
        except Exception as e:
            self.errors.append(f"Phase 1 failed: {str(e)}")
            print(f"❌ Phase 1 failed: {e}")
            return False
    
    def _create_comprehensive_backup(self):
        """Create comprehensive backup of entire src directory"""
        print("\n🔄 Step 1: Creating comprehensive backup...")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup entire src directory
        src_backup = self.backup_dir / "src_complete_backup"
        print(f"   📦 Backing up entire src/ directory...")
        shutil.copytree(self.src_main, src_backup)
        print(f"   ✅ Backup created: {src_backup}")
        
        # Create backup of main project files that reference src.rfu
        project_backup = self.backup_dir / "project_files_backup"
        project_backup.mkdir(exist_ok=True)
        
        critical_files = ["main.py", "main_dual_interface.py", "main_corrected_dual_interface.py"]
        for file_name in critical_files:
            source_file = self.workspace_root / file_name
            if source_file.exists():
                shutil.copy2(source_file, project_backup / file_name)
                print(f"   ✅ Backed up: {file_name}")
        
        # Create migration metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "source_directory": str(self.src_rfu),
            "target_directory": str(self.src_main),
            "files_in_source": len(list(self.src_rfu.rglob("*"))),
            "purpose": "Pre-migration backup for src/rfu → src migration"
        }
        
        with open(self.backup_dir / "migration_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.migration_log.append({
            "phase": "backup",
            "timestamp": datetime.now().isoformat(),
            "action": "comprehensive_backup_created",
            "location": str(self.backup_dir)
        })
    
    def _analyze_conflicts_detailed(self):
        """Detailed analysis of conflicts"""
        print("\n🔍 Step 2: Analyzing conflicts in detail...")
        
        conflicts = {
            "file_conflicts": [],
            "directory_conflicts": [],
            "safe_to_proceed": True
        }
        
        # Check __init__.py conflict
        rfu_init = self.src_rfu / "__init__.py"
        src_init = self.src_main / "__init__.py"
        
        if rfu_init.exists() and src_init.exists():
            print("   ⚠️ __init__.py conflict detected")
            
            # Read both files to understand the conflict
            with open(rfu_init, 'r', encoding='utf-8') as f:
                rfu_content = f.read()
            with open(src_init, 'r', encoding='utf-8') as f:
                src_content = f.read()
            
            conflicts["file_conflicts"].append({
                "filename": "__init__.py",
                "rfu_size": rfu_init.stat().st_size,
                "src_size": src_init.stat().st_size,
                "rfu_lines": len(rfu_content.split('\n')),
                "src_lines": len(src_content.split('\n')),
                "resolution": "rename_rfu_to_init_rfu.py"
            })
            
            print(f"      RFU version: {rfu_init.stat().st_size} bytes, {len(rfu_content.split('\n'))} lines")
            print(f"      SRC version: {src_init.stat().st_size} bytes, {len(src_content.split('\n'))} lines")
            print("      Resolution: Will rename rfu version to __init___rfu.py")
        
        # Check core/ directory conflict
        rfu_core = self.src_rfu / "core"
        src_core = self.src_main / "core"
        
        if rfu_core.exists() and src_core.exists():
            print("   ⚠️ core/ directory conflict detected")
            
            rfu_files = set(f.name for f in rfu_core.rglob("*") if f.is_file())
            src_files = set(f.name for f in src_core.rglob("*") if f.is_file())
            
            overlapping_files = rfu_files.intersection(src_files)
            
            conflicts["directory_conflicts"].append({
                "dirname": "core",
                "rfu_file_count": len(rfu_files),
                "src_file_count": len(src_files),
                "overlapping_files": list(overlapping_files),
                "resolution": "rename_rfu_to_core_rfu"
            })
            
            print(f"      RFU core/: {len(rfu_files)} files")
            print(f"      SRC core/: {len(src_files)} files")
            print(f"      Overlapping: {len(overlapping_files)} files")
            print("      Resolution: Will rename rfu version to core_rfu/")
            
            if len(overlapping_files) > 0:
                print(f"         Overlapping files: {', '.join(list(overlapping_files)[:5])}...")
        
        return conflicts
    
    def _resolve_conflicts_safely(self, conflicts):
        """Resolve conflicts by renaming conflicting items"""
        print("\n🔧 Step 3: Resolving conflicts safely...")
        
        # Resolve __init__.py conflict
        for conflict in conflicts["file_conflicts"]:
            if conflict["filename"] == "__init__.py":
                rfu_init = self.src_rfu / "__init__.py"
                backup_name = "__init___rfu.py"
                
                # Create backup of rfu version in backup directory
                backup_file = self.backup_dir / backup_name
                shutil.copy2(rfu_init, backup_file)
                
                print(f"   ✅ Backed up {conflict['filename']} as {backup_name}")
                
                # The rfu version will be renamed during migration
                self.migration_log.append({
                    "phase": "conflict_resolution",
                    "timestamp": datetime.now().isoformat(),
                    "action": "file_conflict_prepared",
                    "file": "__init__.py",
                    "backup_location": str(backup_file)
                })
        
        # Resolve core/ directory conflict
        for conflict in conflicts["directory_conflicts"]:
            if conflict["dirname"] == "core":
                rfu_core = self.src_rfu / "core"
                backup_name = "core_rfu"
                
                # Create backup of rfu core directory
                backup_dir = self.backup_dir / backup_name
                shutil.copytree(rfu_core, backup_dir)
                
                print(f"   ✅ Backed up {conflict['dirname']}/ as {backup_name}/")
                
                self.migration_log.append({
                    "phase": "conflict_resolution",
                    "timestamp": datetime.now().isoformat(),
                    "action": "directory_conflict_prepared",
                    "directory": "core",
                    "backup_location": str(backup_dir)
                })
    
    def _verify_backup_integrity(self):
        """Verify backup integrity"""
        print("\n✅ Step 4: Verifying backup integrity...")
        
        src_backup = self.backup_dir / "src_complete_backup"
        
        # Count files in original and backup
        original_files = list(self.src_main.rglob("*"))
        backup_files = list(src_backup.rglob("*"))
        
        print(f"   📊 Original files: {len([f for f in original_files if f.is_file()])}")
        print(f"   📊 Backup files: {len([f for f in backup_files if f.is_file()])}")
        
        # Verify critical files exist in backup
        critical_paths = [
            "rfu/__init__.py",
            "rfu/main.py", 
            "rfu/hub.py",
            "rfu/config_manager.py",
            "rfu/core",
            "tools"
        ]
        
        missing_critical = []
        for path in critical_paths:
            if not (src_backup / path).exists():
                missing_critical.append(path)
        
        if missing_critical:
            raise Exception(f"Critical files missing from backup: {missing_critical}")
        
        print("   ✅ All critical files verified in backup")
        
        # Save verification report
        verification_report = {
            "timestamp": datetime.now().isoformat(),
            "backup_verified": True,
            "original_file_count": len([f for f in original_files if f.is_file()]),
            "backup_file_count": len([f for f in backup_files if f.is_file()]),
            "critical_files_verified": critical_paths,
            "missing_files": missing_critical
        }
        
        with open(self.backup_dir / "backup_verification.json", 'w') as f:
            json.dump(verification_report, f, indent=2)


def main():
    workspace_root = Path(__file__).parent
    executor = MigrationExecutor(workspace_root)
    
    print("🚀 Starting Migration Phase 1...")
    print("⚠️  This will create comprehensive backups before any changes")
    print("⚠️  Estimated time: 2-3 minutes")
    
    success = executor.execute_phase1_backup_and_conflicts()
    
    if success:
        print("\n" + "="*80)
        print("✅ PHASE 1 COMPLETED SUCCESSFULLY")
        print("="*80)
        print("📋 Next Steps:")
        print("   1. Phase 2: Execute file migration")
        print("   2. Phase 3: Update import statements")
        print("   3. Phase 4: Test functionality")
        print("   4. Phase 5: Final cleanup")
        print(f"\n📁 All backups saved to: {executor.backup_dir}")
        
    else:
        print("\n" + "="*80)
        print("❌ PHASE 1 FAILED")
        print("="*80)
        print("Migration aborted. No changes were made to your code.")
        if executor.errors:
            for error in executor.errors:
                print(f"   • {error}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())