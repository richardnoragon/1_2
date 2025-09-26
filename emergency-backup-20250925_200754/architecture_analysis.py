#!/usr/bin/env python3
"""
Migration Architecture Analysis Tool
Analyze current structure and plan the src/rfu → src migration
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ArchitectureAnalyzer:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_rfu = self.workspace_root / "src" / "rfu"
        self.src_main = self.workspace_root / "src"
        
    def analyze_current_structure(self):
        """Analyze current directory structure and identify migration patterns"""
        
        print("=" * 80)
        print("ARCHITECTURE ANALYSIS - src/rfu → src Migration")
        print("=" * 80)
        
        # Analyze src/rfu structure
        print(f"\n📁 CURRENT src/rfu STRUCTURE:")
        print(f"   Location: {self.src_rfu}")
        rfu_structure = self._analyze_directory(self.src_rfu, max_depth=3)
        
        # Analyze src structure (excluding rfu)
        print(f"\n📁 CURRENT src STRUCTURE (excluding rfu):")
        print(f"   Location: {self.src_main}")
        src_structure = self._analyze_directory(self.src_main, max_depth=3, exclude_dirs=["rfu"])
        
        # Identify conflicts and overlaps
        print(f"\n⚠️ POTENTIAL CONFLICTS:")
        conflicts = self._identify_conflicts(rfu_structure, src_structure)
        
        # Propose target structure
        print(f"\n🎯 PROPOSED TARGET STRUCTURE:")
        target_structure = self._propose_target_structure(rfu_structure, src_structure)
        
        return {
            "current_rfu": rfu_structure,
            "current_src": src_structure,
            "conflicts": conflicts,
            "proposed_target": target_structure
        }
    
    def _analyze_directory(self, directory, max_depth=3, current_depth=0, exclude_dirs=None):
        """Recursively analyze directory structure"""
        if exclude_dirs is None:
            exclude_dirs = []
            
        structure = {
            "files": [],
            "directories": {},
            "total_files": 0,
            "total_dirs": 0
        }
        
        if not directory.exists() or current_depth >= max_depth:
            return structure
        
        try:
            for item in directory.iterdir():
                if item.name.startswith('.'):
                    continue
                    
                if item.is_file():
                    structure["files"].append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "ext": item.suffix
                    })
                    structure["total_files"] += 1
                elif item.is_dir() and item.name not in exclude_dirs:
                    subdir_info = self._analyze_directory(
                        item, max_depth, current_depth + 1, exclude_dirs
                    )
                    structure["directories"][item.name] = subdir_info
                    structure["total_dirs"] += 1 + subdir_info["total_dirs"]
                    structure["total_files"] += subdir_info["total_files"]
        except PermissionError:
            pass
        
        # Print structure at root level
        if current_depth == 0:
            self._print_structure(structure, directory.name)
        
        return structure
    
    def _print_structure(self, structure, root_name, indent=""):
        """Print directory structure in a readable format"""
        
        print(f"{indent}📁 {root_name}/ ({structure['total_dirs']} dirs, {structure['total_files']} files)")
        
        # Print files in root
        if structure["files"]:
            print(f"{indent}   📄 Files ({len(structure['files'])}):")
            sorted_files = sorted(structure["files"], key=lambda x: x['name'])
            for file in sorted_files[:10]:  # Show first 10
                print(f"{indent}      • {file['name']} ({file['size']} bytes)")
            if len(structure["files"]) > 10:
                print(f"{indent}      ... and {len(structure['files']) - 10} more files")
        
        # Print subdirectories
        if structure["directories"]:
            print(f"{indent}   📁 Subdirectories ({len(structure['directories'])}):")
            for dir_name, dir_info in sorted(structure["directories"].items()):
                print(f"{indent}      📁 {dir_name}/ ({dir_info['total_dirs']} dirs, {dir_info['total_files']} files)")
                
                # Show key files in important directories
                if dir_info["files"] and len(dir_info["files"]) <= 5:
                    sorted_files = sorted(dir_info["files"], key=lambda x: x['name'])
                    for file in sorted_files:
                        print(f"{indent}         • {file['name']}")
    
    def _identify_conflicts(self, rfu_structure, src_structure):
        """Identify potential conflicts when moving rfu to src"""
        conflicts = []
        
        # Check for name conflicts at root level
        rfu_files = {f["name"] for f in rfu_structure["files"]}
        src_files = {f["name"] for f in src_structure["files"]}
        
        file_conflicts = rfu_files.intersection(src_files)
        if file_conflicts:
            conflicts.append({
                "type": "FILE_NAME_CONFLICT",
                "items": list(file_conflicts),
                "description": "Files with same names exist in both locations"
            })
        
        # Check for directory conflicts
        rfu_dirs = set(rfu_structure["directories"].keys())
        src_dirs = set(src_structure["directories"].keys())
        
        dir_conflicts = rfu_dirs.intersection(src_dirs)
        if dir_conflicts:
            conflicts.append({
                "type": "DIRECTORY_NAME_CONFLICT", 
                "items": list(dir_conflicts),
                "description": "Directories with same names exist in both locations"
            })
        
        # Print conflicts
        if conflicts:
            for conflict in conflicts:
                print(f"   ⚠️ {conflict['type']}: {conflict['items']}")
                print(f"      {conflict['description']}")
        else:
            print("   ✅ No naming conflicts detected")
        
        return conflicts
    
    def _propose_target_structure(self, rfu_structure, src_structure):
        """Propose the target structure after migration"""
        
        print("   After migration, src/ will contain:")
        
        # Core RFU files will move to src root
        core_files = [f["name"] for f in rfu_structure["files"]]
        if core_files:
            print(f"   📄 Core application files ({len(core_files)}):")
            for file in sorted(core_files):
                print(f"      • {file}")
        
        # RFU directories will move to src root
        rfu_dirs = list(rfu_structure["directories"].keys())
        existing_src_dirs = list(src_structure["directories"].keys())
        
        print(f"   📁 Directories from src/rfu ({len(rfu_dirs)}):")
        for dir_name in sorted(rfu_dirs):
            status = " (CONFLICT)" if dir_name in existing_src_dirs else ""
            print(f"      • {dir_name}/{status}")
        
        print(f"   📁 Existing src directories ({len(existing_src_dirs)}):")
        for dir_name in sorted(existing_src_dirs):
            print(f"      • {dir_name}/")
        
        return {
            "core_files": core_files,
            "rfu_directories": rfu_dirs,
            "existing_directories": existing_src_dirs,
            "total_estimated_files": rfu_structure["total_files"] + src_structure["total_files"],
            "total_estimated_dirs": len(rfu_dirs) + len(existing_src_dirs)
        }
    
    def generate_migration_plan(self):
        """Generate detailed migration plan"""
        analysis = self.analyze_current_structure()
        
        print(f"\n🚀 MIGRATION EXECUTION PLAN:")
        print("   Phase 1: Backup current state")
        print("   Phase 2: Handle conflicts")
        print("   Phase 3: Move files and directories")
        print("   Phase 4: Update import statements")
        print("   Phase 5: Update configuration files")
        print("   Phase 6: Test functionality")
        print("   Phase 7: Clean up old structure")
        
        # Estimate migration complexity
        complexity_score = self._calculate_complexity(analysis)
        print(f"\n📊 MIGRATION COMPLEXITY: {complexity_score['level']} ({complexity_score['score']}/100)")
        print(f"   • Files to migrate: {analysis['current_rfu']['total_files']}")
        print(f"   • Directories to migrate: {analysis['current_rfu']['total_dirs']}")
        print(f"   • Potential conflicts: {len(analysis['conflicts'])}")
        
        return analysis
    
    def _calculate_complexity(self, analysis):
        """Calculate migration complexity score"""
        score = 0
        
        # Base complexity from file count
        score += min(analysis['current_rfu']['total_files'] / 10, 30)
        
        # Directory complexity
        score += min(analysis['current_rfu']['total_dirs'] / 5, 20)
        
        # Conflict complexity
        score += len(analysis['conflicts']) * 15
        
        # If high file count, add extra complexity
        if analysis['current_rfu']['total_files'] > 100:
            score += 20
        
        # Determine level
        if score < 30:
            level = "LOW"
        elif score < 60:
            level = "MEDIUM"
        elif score < 80:
            level = "HIGH"
        else:
            level = "VERY HIGH"
        
        return {"score": min(int(score), 100), "level": level}


def main():
    workspace_root = Path(__file__).parent
    analyzer = ArchitectureAnalyzer(workspace_root)
    
    analysis = analyzer.generate_migration_plan()
    
    # Save analysis to file
    report_file = workspace_root / f"architecture_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n📋 Analysis saved to: {report_file}")
    
    return analysis


if __name__ == "__main__":
    main()