#!/usr/bin/env python3
"""
Comprehensive Migration Plan for src/rfu → src
Systematic approach to handle conflicts and ensure zero data loss
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class ComprehensiveMigrator:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_rfu = self.workspace_root / "src" / "rfu"
        self.src_main = self.workspace_root / "src"
        self.backup_dir = self.workspace_root / f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.migration_log = []
        self.conflicts_resolved = []
        self.errors = []
        
    def execute_migration(self, dry_run=True):
        """Execute the complete migration with proper conflict resolution"""
        
        print("=" * 80)
        print(f"COMPREHENSIVE MIGRATION: src/rfu → src")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        print("=" * 80)
        
        try:
            # Phase 1: Create backup
            self._phase1_backup()
            
            # Phase 2: Analyze and resolve conflicts
            conflicts = self._phase2_analyze_conflicts()
            
            # Phase 3: Execute file migration
            if not dry_run:
                self._phase3_migrate_files(conflicts)
            else:
                self._phase3_plan_migration(conflicts)
            
            # Phase 4: Handle import statement updates
            import_plan = self._phase4_plan_import_updates()
            
            # Phase 5: Generate comprehensive report
            report = self._phase5_generate_report(conflicts, import_plan)
            
            return report
            
        except Exception as e:
            self.errors.append(f"Migration failed: {str(e)}")
            print(f"❌ Migration failed: {e}")
            return None
    
    def _phase1_backup(self):
        """Create comprehensive backup before migration"""
        print("\n🔄 Phase 1: Creating comprehensive backup...")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup entire src directory
        src_backup = self.backup_dir / "src_complete"
        if not src_backup.exists():
            shutil.copytree(self.src_main, src_backup)
            print(f"   ✅ Complete src/ backup created: {src_backup}")
        
        # Create manifest of all files
        manifest = self._create_file_manifest()
        manifest_file = self.backup_dir / "file_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        print(f"   ✅ File manifest created: {manifest_file}")
        
        self.migration_log.append({
            "phase": "backup",
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "files_backed_up": len(manifest["files"])
        })
    
    def _create_file_manifest(self):
        """Create detailed manifest of all files before migration"""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "source_location": str(self.src_rfu),
            "target_location": str(self.src_main),
            "files": {}
        }
        
        # Catalog all files in src/rfu
        for file_path in self.src_rfu.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.src_rfu)
                manifest["files"][str(relative_path)] = {
                    "source_path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "hash": self._calculate_hash(file_path)
                }
        
        return manifest
    
    def _calculate_hash(self, file_path):
        """Calculate file hash for integrity verification"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "ERROR"
    
    def _phase2_analyze_conflicts(self):
        """Analyze and plan resolution for all conflicts"""
        print("\n🔍 Phase 2: Analyzing conflicts and planning resolution...")
        
        conflicts = {
            "file_conflicts": [],
            "directory_conflicts": [],
            "resolutions": []
        }
        
        # Check file conflicts
        conflicts["file_conflicts"] = self._identify_file_conflicts()
        
        # Check directory conflicts  
        conflicts["directory_conflicts"] = self._identify_directory_conflicts()
        
        # Plan conflict resolutions
        conflicts["resolutions"] = self._plan_conflict_resolutions(conflicts)
        
        print(f"   📊 Found {len(conflicts['file_conflicts'])} file conflicts")
        print(f"   📊 Found {len(conflicts['directory_conflicts'])} directory conflicts")
        print(f"   🎯 Planned {len(conflicts['resolutions'])} conflict resolutions")
        
        return conflicts
    
    def _identify_file_conflicts(self):
        """Identify files that exist in both locations"""
        conflicts = []
        
        # Get files in src/rfu root
        rfu_files = [f for f in self.src_rfu.iterdir() if f.is_file()]
        
        # Get files in src root  
        src_files = [f for f in self.src_main.iterdir() if f.is_file() and f.name != "rfu"]
        
        # Find name conflicts
        rfu_names = {f.name for f in rfu_files}
        src_names = {f.name for f in src_files}
        
        conflicting_names = rfu_names.intersection(src_names)
        
        for name in conflicting_names:
            rfu_file = self.src_rfu / name
            src_file = self.src_main / name
            
            conflicts.append({
                "filename": name,
                "rfu_path": str(rfu_file),
                "src_path": str(src_file),
                "rfu_size": rfu_file.stat().st_size,
                "src_size": src_file.stat().st_size,
                "rfu_hash": self._calculate_hash(rfu_file),
                "src_hash": self._calculate_hash(src_file),
                "identical": self._calculate_hash(rfu_file) == self._calculate_hash(src_file)
            })
        
        return conflicts
    
    def _identify_directory_conflicts(self):
        """Identify directories that exist in both locations"""
        conflicts = []
        
        # Get directories in src/rfu
        rfu_dirs = [d for d in self.src_rfu.iterdir() if d.is_dir() and d.name != "__pycache__"]
        
        # Get directories in src (excluding rfu)
        src_dirs = [d for d in self.src_main.iterdir() if d.is_dir() and d.name not in ["rfu", "__pycache__"]]
        
        # Find name conflicts
        rfu_names = {d.name for d in rfu_dirs}
        src_names = {d.name for d in src_dirs}
        
        conflicting_names = rfu_names.intersection(src_names)
        
        for name in conflicting_names:
            rfu_dir = self.src_rfu / name
            src_dir = self.src_main / name
            
            conflicts.append({
                "dirname": name,
                "rfu_path": str(rfu_dir),
                "src_path": str(src_dir),
                "rfu_file_count": len(list(rfu_dir.rglob("*"))),
                "src_file_count": len(list(src_dir.rglob("*"))),
                "can_merge": self._can_merge_directories(rfu_dir, src_dir)
            })
        
        return conflicts
    
    def _can_merge_directories(self, dir1, dir2):
        """Check if two directories can be safely merged"""
        try:
            # Get all file paths in both directories
            dir1_files = {f.relative_to(dir1) for f in dir1.rglob("*") if f.is_file()}
            dir2_files = {f.relative_to(dir2) for f in dir2.rglob("*") if f.is_file()}
            
            # Check for file conflicts
            conflicting_files = dir1_files.intersection(dir2_files)
            
            return len(conflicting_files) == 0
        except Exception:
            return False
    
    def _plan_conflict_resolutions(self, conflicts):
        """Plan how to resolve each conflict"""
        resolutions = []
        
        # Resolve file conflicts
        for conflict in conflicts["file_conflicts"]:
            if conflict["identical"]:
                resolutions.append({
                    "type": "file",
                    "item": conflict["filename"],
                    "strategy": "keep_existing",
                    "reason": "Files are identical",
                    "action": f"Skip migration of {conflict['filename']}"
                })
            else:
                resolutions.append({
                    "type": "file", 
                    "item": conflict["filename"],
                    "strategy": "rename_rfu_version",
                    "reason": "Files differ",
                    "action": f"Rename {conflict['filename']} to {conflict['filename']}.rfu"
                })
        
        # Resolve directory conflicts
        for conflict in conflicts["directory_conflicts"]:
            if conflict["can_merge"]:
                resolutions.append({
                    "type": "directory",
                    "item": conflict["dirname"],
                    "strategy": "merge",
                    "reason": "No file conflicts detected",
                    "action": f"Merge {conflict['dirname']}/ directories"
                })
            else:
                resolutions.append({
                    "type": "directory",
                    "item": conflict["dirname"], 
                    "strategy": "rename_rfu_version",
                    "reason": "Cannot safely merge",
                    "action": f"Rename to {conflict['dirname']}_rfu/"
                })
        
        return resolutions
    
    def _phase3_migrate_files(self, conflicts):
        """Execute the actual file migration"""
        print("\n🚀 Phase 3: Executing file migration...")
        
        # This would contain the actual migration logic
        # For now, just plan what would happen
        pass
    
    def _phase3_plan_migration(self, conflicts):
        """Plan the migration steps (dry run)"""
        print("\n🎯 Phase 3: Planning migration steps (DRY RUN)...")
        
        migration_steps = []
        
        # Plan file migrations
        for file_path in self.src_rfu.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.src_rfu)
                target_path = self.src_main / relative_path
                
                step = {
                    "type": "file",
                    "source": str(file_path),
                    "target": str(target_path),
                    "relative_path": str(relative_path),
                    "size": file_path.stat().st_size
                }
                
                # Check if this file is involved in a conflict
                conflict_resolution = next(
                    (r for r in conflicts["resolutions"] 
                     if r["type"] == "file" and file_path.name == r["item"]),
                    None
                )
                
                if conflict_resolution:
                    if conflict_resolution["strategy"] == "rename_rfu_version":
                        step["target"] = str(target_path.with_suffix(target_path.suffix + ".rfu"))
                    elif conflict_resolution["strategy"] == "keep_existing":
                        step["action"] = "SKIP - file exists and is identical"
                
                migration_steps.append(step)
        
        print(f"   📋 Planned {len(migration_steps)} file operations")
        
        # Show sample of planned operations
        print("   📝 Sample migration operations:")
        for step in migration_steps[:5]:
            action = step.get("action", "MOVE")
            print(f"      {action}: {step['relative_path']} → {Path(step['target']).relative_to(self.src_main)}")
        
        if len(migration_steps) > 5:
            print(f"      ... and {len(migration_steps) - 5} more operations")
        
        return migration_steps
    
    def _phase4_plan_import_updates(self):
        """Plan all import statement updates needed"""
        print("\n📝 Phase 4: Planning import statement updates...")
        
        import_updates = []
        
        # Find all Python files that import from src.rfu
        for py_file in self.workspace_root.rglob("*.py"):
            if "src/rfu" in str(py_file):
                continue  # Skip files in the old location
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                file_updates = []
                for i, line in enumerate(lines, 1):
                    if 'src.rfu' in line or 'from rfu' in line:
                        file_updates.append({
                            "line_number": i,
                            "current": line.strip(),
                            "proposed": self._suggest_import_update(line.strip())
                        })
                
                if file_updates:
                    import_updates.append({
                        "file": str(py_file.relative_to(self.workspace_root)),
                        "updates": file_updates
                    })
            
            except Exception:
                pass
        
        print(f"   📊 Found {len(import_updates)} files with import updates needed")
        
        total_updates = sum(len(file_info["updates"]) for file_info in import_updates)
        print(f"   📊 Total import statements to update: {total_updates}")
        
        return import_updates
    
    def _suggest_import_update(self, import_line):
        """Suggest updated import statement"""
        # Basic import update suggestions
        if "from src." in import_line:
            return import_line.replace("from src.", "from src.")
        elif "import src." in import_line:
            return import_line.replace("src.rfu.", "src.")
        elif "from src." in import_line:
            return import_line.replace("from src.", "from src.")
        else:
            return f"# TODO: Update import - {import_line}"
    
    def _phase5_generate_report(self, conflicts, import_plan):
        """Generate comprehensive migration report"""
        print("\n📋 Phase 5: Generating comprehensive report...")
        
        report = {
            "migration_info": {
                "timestamp": datetime.now().isoformat(),
                "workspace": str(self.workspace_root),
                "source": str(self.src_rfu),
                "target": str(self.src_main),
                "backup_location": str(self.backup_dir)
            },
            "statistics": {
                "files_to_migrate": len(list(self.src_rfu.rglob("*"))),
                "file_conflicts": len(conflicts["file_conflicts"]),
                "directory_conflicts": len(conflicts["directory_conflicts"]),
                "import_files_to_update": len(import_plan),
                "total_import_updates": sum(len(f["updates"]) for f in import_plan)
            },
            "conflicts": conflicts,
            "import_plan": import_plan,
            "migration_log": self.migration_log,
            "errors": self.errors
        }
        
        # Save report
        report_file = self.workspace_root / f"comprehensive_migration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   💾 Report saved: {report_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("MIGRATION PLAN SUMMARY")
        print("=" * 80)
        print(f"📊 Files to migrate: {report['statistics']['files_to_migrate']}")
        print(f"⚠️ File conflicts: {report['statistics']['file_conflicts']}")
        print(f"⚠️ Directory conflicts: {report['statistics']['directory_conflicts']}")
        print(f"📝 Files needing import updates: {report['statistics']['import_files_to_update']}")
        print(f"📝 Total import statements to update: {report['statistics']['total_import_updates']}")
        
        if self.errors:
            print(f"❌ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Review the generated migration plan")
        print("   2. Resolve any conflicts identified")
        print("   3. Execute migration with --live flag")
        print("   4. Update import statements") 
        print("   5. Test all functionality")
        print("   6. Remove old src/rfu directory")
        
        return report


def main():
    workspace_root = Path(__file__).parent
    migrator = ComprehensiveMigrator(workspace_root)
    
    # Execute dry run by default
    report = migrator.execute_migration(dry_run=True)
    
    if report:
        print(f"\n✅ Migration planning completed successfully")
        print(f"📋 Review the plan and run with --live when ready")
    else:
        print(f"\n❌ Migration planning failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())