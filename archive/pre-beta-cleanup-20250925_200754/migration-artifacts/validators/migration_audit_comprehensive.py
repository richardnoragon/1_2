#!/usr/bin/env python3
"""
Comprehensive Migration Audit Tool
Performs detailed comparison between src/rfu and src directories
to ensure complete migration verification
"""

import difflib
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


class MigrationAudit:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_rfu = self.workspace_root / "src" / "rfu"
        self.src_main = self.workspace_root / "src"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(workspace_root),
            "audit_results": {},
            "issues": [],
            "recommendations": []
        }
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def scan_directory(self, directory, relative_to=None):
        """Recursively scan directory and return file information"""
        if relative_to is None:
            relative_to = directory
        
        files_info = {}
        
        if not directory.exists():
            return files_info
            
        for item in directory.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(relative_to)
                files_info[str(relative_path)] = {
                    "absolute_path": str(item),
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "hash": self.calculate_file_hash(item)
                }
        
        return files_info
    
    def compare_directories(self):
        """Compare src/rfu with expected locations in src"""
        print("Scanning src/rfu directory...")
        rfu_files = self.scan_directory(self.src_rfu, self.src_rfu)
        
        print("Scanning src directory...")
        src_files = self.scan_directory(self.src_main, self.src_main)
        
        # Remove rfu subdirectory from src scan to avoid confusion
        src_files_filtered = {k: v for k, v in src_files.items() if not k.startswith("rfu/")}
        
        self.report["audit_results"]["rfu_files_count"] = len(rfu_files)
        self.report["audit_results"]["src_files_count"] = len(src_files_filtered)
        
        print(f"Found {len(rfu_files)} files in src/rfu")
        print(f"Found {len(src_files_filtered)} files in src (excluding rfu subdirectory)")
        
        # Check for files that should have been migrated
        missing_migrations = []
        successful_migrations = []
        
        for rfu_file_path, rfu_info in rfu_files.items():
            # Look for corresponding file in new structure
            potential_new_paths = self._get_potential_migration_paths(rfu_file_path)
            
            found_match = False
            for potential_path in potential_new_paths:
                if potential_path in src_files_filtered:
                    # Compare hashes to verify content integrity
                    if src_files_filtered[potential_path]["hash"] == rfu_info["hash"]:
                        successful_migrations.append({
                            "old_path": rfu_file_path,
                            "new_path": potential_path,
                            "status": "VERIFIED"
                        })
                        found_match = True
                        break
                    else:
                        self.report["issues"].append({
                            "type": "CONTENT_MISMATCH",
                            "old_path": rfu_file_path,
                            "new_path": potential_path,
                            "description": "File exists but content differs"
                        })
            
            if not found_match:
                missing_migrations.append({
                    "path": rfu_file_path,
                    "info": rfu_info
                })
        
        self.report["audit_results"]["successful_migrations"] = successful_migrations
        self.report["audit_results"]["missing_migrations"] = missing_migrations
        
        return rfu_files, src_files_filtered
    
    def _get_potential_migration_paths(self, rfu_file_path):
        """Get potential new locations for a file from src/rfu"""
        potential_paths = []
        
        # Common migration patterns based on the project structure
        migration_mappings = {
            # Core files that moved to root src
            "config_manager.py": ["config/config_manager.py", "config_manager.py"],
            "log_manager.py": ["log_manager.py", "core/log_manager.py"],
            "hub.py": ["hub.py", "main.py"],
            "main.py": ["main.py", "rfu_main.py"],
            
            # Files that moved to tools
            "advanced_folders/": ["tools/file_management/"],
            "file_explorer/": ["tools/file_management/"],
            "gui/": ["tools/"],
            
            # Core functionality
            "core/": ["core/", "tools/core/"],
            "utils/": ["tools/", "core/"],
            "database/": ["tools/system/", "core/"]
        }
        
        # Direct mapping check
        for old_pattern, new_patterns in migration_mappings.items():
            if rfu_file_path.startswith(old_pattern):
                for new_pattern in new_patterns:
                    new_path = rfu_file_path.replace(old_pattern, new_pattern, 1)
                    potential_paths.append(new_path)
        
        # Also check if file exists in similar directory structure
        parts = Path(rfu_file_path).parts
        if len(parts) > 1:
            # Try moving to tools subdirectory
            tools_path = "tools/" + "/".join(parts)
            potential_paths.append(tools_path)
            
            # Try moving up one level
            upper_path = "/".join(parts[1:])
            potential_paths.append(upper_path)
        
        return potential_paths
    
    def search_for_rfu_references(self):
        """Search for references to src/rfu in the codebase"""
        print("Searching for src/rfu references...")
        
        search_patterns = [
            "src.rfu",
            "src/rfu",
            "src\\rfu",
            "from rfu",
            "import rfu",
            "rfu.",
            '"rfu"',
            "'rfu'",
            "rfu/",
            "rfu\\"
        ]
        
        references = []
        
        # Search in Python files
        for py_file in self.workspace_root.rglob("*.py"):
            if "rfu" in str(py_file) and "src/rfu" in str(py_file):
                continue  # Skip files in the old location
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern in search_patterns:
                            if pattern in line:
                                references.append({
                                    "file": str(py_file.relative_to(self.workspace_root)),
                                    "line": i,
                                    "content": line.strip(),
                                    "pattern": pattern
                                })
            except Exception as e:
                self.report["issues"].append({
                    "type": "FILE_READ_ERROR",
                    "file": str(py_file),
                    "error": str(e)
                })
        
        # Search in configuration files
        config_files = [
            "*.json", "*.yaml", "*.yml", "*.toml", "*.cfg", "*.ini", 
            "*.txt", "*.md", "requirements*.txt"
        ]
        
        for pattern in config_files:
            for config_file in self.workspace_root.rglob(pattern):
                if "rfu" in str(config_file) and "src/rfu" in str(config_file):
                    continue
                    
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for search_pattern in search_patterns:
                                if search_pattern in line:
                                    references.append({
                                        "file": str(config_file.relative_to(self.workspace_root)),
                                        "line": i,
                                        "content": line.strip(),
                                        "pattern": search_pattern
                                    })
                except Exception:
                    pass  # Skip binary or unreadable files
        
        self.report["audit_results"]["rfu_references"] = references
        return references
    
    def check_import_statements(self):
        """Specifically check for import statements that need updating"""
        print("Analyzing import statements...")
        
        import_issues = []
        
        for py_file in self.workspace_root.rglob("*.py"):
            if "src/rfu" in str(py_file):
                continue  # Skip old location files
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        stripped_line = line.strip()
                        if (stripped_line.startswith('from ') or stripped_line.startswith('import ')) and 'rfu' in stripped_line:
                            import_issues.append({
                                "file": str(py_file.relative_to(self.workspace_root)),
                                "line": i,
                                "statement": stripped_line,
                                "type": "IMPORT"
                            })
            except Exception:
                pass
        
        self.report["audit_results"]["import_issues"] = import_issues
        return import_issues
    
    def generate_recommendations(self):
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Check migration completeness
        missing_count = len(self.report["audit_results"].get("missing_migrations", []))
        if missing_count > 0:
            recommendations.append(
                f"CRITICAL: {missing_count} files from src/rfu appear to not have been migrated. "
                "Review and complete migration before deletion."
            )
        
        # Check references
        ref_count = len(self.report["audit_results"].get("rfu_references", []))
        if ref_count > 0:
            recommendations.append(
                f"WARNING: {ref_count} references to src/rfu found in codebase. "
                "Update all references before deletion."
            )
        
        # Check imports
        import_count = len(self.report["audit_results"].get("import_issues", []))
        if import_count > 0:
            recommendations.append(
                f"WARNING: {import_count} import statements referencing rfu found. "
                "Update all import statements before deletion."
            )
        
        if missing_count == 0 and ref_count == 0 and import_count == 0:
            recommendations.append(
                "✅ Migration appears complete. Safe to proceed with src/rfu deletion after testing."
            )
        
        self.report["recommendations"] = recommendations
        return recommendations
    
    def run_full_audit(self):
        """Run complete migration audit"""
        print("=" * 60)
        print("COMPREHENSIVE MIGRATION AUDIT")
        print("=" * 60)
        
        # Compare directories
        rfu_files, src_files = self.compare_directories()
        
        # Search for references
        references = self.search_for_rfu_references()
        
        # Check imports
        imports = self.check_import_statements()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Save report
        report_file = self.workspace_root / f"migration_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
        
        return self.report


def main():
    workspace_root = Path(__file__).parent
    auditor = MigrationAudit(workspace_root)
    
    try:
        report = auditor.run_full_audit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("AUDIT SUMMARY")
        print("=" * 60)
        
        results = report["audit_results"]
        
        print(f"📁 Files in src/rfu: {results.get('rfu_files_count', 0)}")
        print(f"📁 Files in src: {results.get('src_files_count', 0)}")
        print(f"✅ Successful migrations: {len(results.get('successful_migrations', []))}")
        print(f"❌ Missing migrations: {len(results.get('missing_migrations', []))}")
        print(f"🔗 RFU references found: {len(results.get('rfu_references', []))}")
        print(f"📥 Import issues: {len(results.get('import_issues', []))}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        
        if report["issues"]:
            print(f"\n⚠️ ISSUES FOUND: {len(report['issues'])}")
            for issue in report["issues"][:5]:  # Show first 5
                print(f"  • {issue['type']}: {issue.get('description', 'See detailed report')}")
    
    except Exception as e:
        print(f"❌ Audit failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())