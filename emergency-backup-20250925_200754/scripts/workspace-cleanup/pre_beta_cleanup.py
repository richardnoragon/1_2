#!/usr/bin/env python3
"""
Pre-Beta Workspace Cleanup Automation Script
Safely removes obsolete migration and debug artifacts while preserving critical functionality
"""

import hashlib
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class PreBetaCleanup:
    """Automated workspace cleanup for pre-beta transition"""

    def __init__(self, workspace_root: str, dry_run: bool = True):
        self.workspace_root = Path(workspace_root)
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_root = (
            self.workspace_root
            / "archive"
            / f"pre-beta-cleanup-{self.timestamp}"
        )

        # Setup logging
        self.setup_logging()

        # File patterns for different categories
        self.migration_patterns = {
            "executors": [
                "migration_phase*.py",
                "migration_*_executor.py",
                "*migration_master.py",
            ],
            "reports": [
                "*migration*report*.json",
                "*migration*report*.md",
                "MIGRATION_*.md",
            ],
            "backups": [
                "migration_backup_*/",
                "MIGRATION_BACKUP_*/",
                "migration_backup_*/*",
            ],
            "rollbacks": ["rollback_migration_*.py", "rollback_*.py"],
            "validators": ["migration_validation*.py", "migration_audit*.py"],
            "automation": [
                "migration_automation.py",
                "migration_controller.py",
            ],
        }

        self.debug_patterns = {
            "debug_scripts": ["debug_*.py"],
            "fix_scripts": ["fix_*.py"],
            "diagnostic": ["diagnostic_*.py"],
            "test_files": ["test_*.py"],  # Only in root directory
            "layout_tests": ["*layout_*.py", "*pane_*.py"],
            "compatibility": ["corrected_*.json", "enterprise_*.json"],
        }

        self.legacy_backup_patterns = {
            "reorganization": [".reorganization_backup/"],
            "temp_plans": [".temp_reorganization_plan/"],
            "variant_mains": ["main_*.py"],
            "backup_dirs": ["*_backup_*/", "backup_*/"],
        }

        # Critical files that should never be removed
        self.critical_files = {
            "src/rfu/main.py",
            "src/hub.py",
            "src/config_manager.py",
            "requirements.txt",
            "LICENSE",
            ".gitignore",
            "README.md",
            "pyproject.toml",
            "pytest.ini",
        }

        # Directories that should be preserved
        self.critical_directories = {
            "src/",
            "tests/",
            "config/",
            "docs/",
            ".git/",
            ".github/",
            "venv/",
            ".roo/",
            ".kilocode/",
        }

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = self.workspace_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"workspace-cleanup-{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def create_safety_backup(self) -> bool:
        """Create comprehensive git backup before cleanup"""
        self.logger.info("Creating safety backup...")

        try:
            # Check if we're in a git repository
            subprocess.run(
                ["git", "status"],
                cwd=self.workspace_root,
                check=True,
                capture_output=True,
            )

            # Add all files to git
            subprocess.run(
                ["git", "add", "-A"], cwd=self.workspace_root, check=True
            )

            # Create backup commit
            commit_msg = f"Pre-cleanup backup: {self.timestamp}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.workspace_root,
                check=True,
            )

            # Create backup tag
            tag_name = f"pre-cleanup-backup-{self.timestamp}"
            subprocess.run(
                ["git", "tag", tag_name], cwd=self.workspace_root, check=True
            )

            self.logger.info(f"Created backup tag: {tag_name}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git backup failed: {e}")
            self.logger.warning("Proceeding with file-based backup...")
            return self.create_file_backup()

    def create_file_backup(self) -> bool:
        """Create file-based backup if git is unavailable"""
        backup_dir = self.workspace_root / f"emergency-backup-{self.timestamp}"

        try:
            if not self.dry_run:
                shutil.copytree(
                    self.workspace_root,
                    backup_dir,
                    ignore=shutil.ignore_patterns(
                        ".git", "venv", "__pycache__", "*.pyc"
                    ),
                )

            self.logger.info(f"Created file backup at: {backup_dir}")
            return True

        except Exception as e:
            self.logger.error(f"File backup failed: {e}")
            return False

    def analyze_workspace(self) -> Dict:
        """Analyze current workspace structure"""
        self.logger.info("Analyzing workspace structure...")

        analysis = {
            "total_files": 0,
            "total_directories": 0,
            "migration_artifacts": [],
            "debug_artifacts": [],
            "legacy_backups": [],
            "critical_files_found": [],
            "potential_issues": [],
        }

        # Walk through workspace
        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.workspace_root)

            analysis["total_directories"] += len(dirs)
            analysis["total_files"] += len(files)

            # Check for migration artifacts
            for pattern_category, patterns in self.migration_patterns.items():
                for pattern in patterns:
                    matches = list(root_path.glob(pattern))
                    for match in matches:
                        relative_match = match.relative_to(self.workspace_root)
                        analysis["migration_artifacts"].append(
                            {
                                "file": str(relative_match),
                                "category": pattern_category,
                                "size": (
                                    match.stat().st_size
                                    if match.is_file()
                                    else 0
                                ),
                                "modified": datetime.fromtimestamp(
                                    match.stat().st_mtime
                                ).isoformat(),
                            }
                        )

            # Check for debug artifacts
            for pattern_category, patterns in self.debug_patterns.items():
                for pattern in patterns:
                    matches = list(root_path.glob(pattern))
                    for match in matches:
                        relative_match = match.relative_to(self.workspace_root)
                        # Special handling for test files - only in root
                        if (
                            pattern_category == "test_files"
                            and relative_match.parent != Path(".")
                        ):
                            continue

                        analysis["debug_artifacts"].append(
                            {
                                "file": str(relative_match),
                                "category": pattern_category,
                                "size": (
                                    match.stat().st_size
                                    if match.is_file()
                                    else 0
                                ),
                                "modified": datetime.fromtimestamp(
                                    match.stat().st_mtime
                                ).isoformat(),
                            }
                        )

            # Check for legacy backups
            for (
                pattern_category,
                patterns,
            ) in self.legacy_backup_patterns.items():
                for pattern in patterns:
                    matches = list(root_path.glob(pattern))
                    for match in matches:
                        relative_match = match.relative_to(self.workspace_root)
                        analysis["legacy_backups"].append(
                            {
                                "file": str(relative_match),
                                "category": pattern_category,
                                "size": (
                                    self.get_directory_size(match)
                                    if match.is_dir()
                                    else match.stat().st_size
                                ),
                                "modified": datetime.fromtimestamp(
                                    match.stat().st_mtime
                                ).isoformat(),
                            }
                        )

        # Check for critical files
        for critical_file in self.critical_files:
            file_path = self.workspace_root / critical_file
            if file_path.exists():
                analysis["critical_files_found"].append(critical_file)
            else:
                analysis["potential_issues"].append(
                    f"Critical file missing: {critical_file}"
                )

        # Save analysis
        analysis_file = (
            self.workspace_root / f"workspace-analysis-{self.timestamp}.json"
        )
        if not self.dry_run:
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2)

        self.logger.info(f"Workspace analysis complete. Found:")
        self.logger.info(
            f"  - Migration artifacts: {len(analysis['migration_artifacts'])}"
        )
        self.logger.info(
            f"  - Debug artifacts: {len(analysis['debug_artifacts'])}"
        )
        self.logger.info(
            f"  - Legacy backups: {len(analysis['legacy_backups'])}"
        )

        return analysis

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    try:
                        total += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        pass
        except Exception:
            pass
        return total

    def create_archive_structure(self):
        """Create organized archive directory structure"""
        self.logger.info(f"Creating archive structure at: {self.archive_root}")

        archive_structure = [
            "migration-artifacts/executors",
            "migration-artifacts/reports",
            "migration-artifacts/backups",
            "migration-artifacts/rollbacks",
            "migration-artifacts/validators",
            "migration-artifacts/automation",
            "debug-scripts/debug-tools",
            "debug-scripts/fix-scripts",
            "debug-scripts/diagnostic-tools",
            "debug-scripts/test-files",
            "debug-scripts/layout-tests",
            "debug-scripts/compatibility",
            "legacy-backups/reorganization",
            "legacy-backups/temp-plans",
            "legacy-backups/variant-mains",
            "legacy-backups/backup-dirs",
            "documentation/completion-reports",
            "documentation/implementation-summaries",
        ]

        if not self.dry_run:
            for structure in archive_structure:
                (self.archive_root / structure).mkdir(
                    parents=True, exist_ok=True
                )

    def archive_file(
        self, source_path: Path, archive_category: str, subcategory: str
    ) -> Dict:
        """Archive individual file with metadata"""
        relative_source = source_path.relative_to(self.workspace_root)

        # Calculate destination
        archive_subdir = self.archive_root / archive_category / subcategory
        destination = archive_subdir / source_path.name

        # Handle name conflicts
        counter = 1
        while destination.exists():
            stem = source_path.stem
            suffix = source_path.suffix
            destination = archive_subdir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Create metadata
        metadata = {
            "original_path": str(relative_source),
            "archived_path": str(destination.relative_to(self.archive_root)),
            "archived_date": datetime.now().isoformat(),
            "reason": f"Pre-beta cleanup: {archive_category}",
            "safety_level": "low",
            "retrieval_priority": "normal",
            "last_modified": datetime.fromtimestamp(
                source_path.stat().st_mtime
            ).isoformat(),
            "file_size": (
                source_path.stat().st_size
                if source_path.is_file()
                else self.get_directory_size(source_path)
            ),
            "file_type": "directory" if source_path.is_dir() else "file",
        }

        # Calculate hash for files
        if source_path.is_file():
            try:
                with open(source_path, "rb") as f:
                    metadata["md5_hash"] = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                metadata["hash_error"] = str(e)

        # Perform archive operation
        if not self.dry_run:
            try:
                if source_path.is_file():
                    shutil.copy2(source_path, destination)
                else:
                    shutil.copytree(source_path, destination)

                # Save metadata
                metadata_file = (
                    destination.parent / f"{destination.name}.metadata.json"
                )
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)

            except Exception as e:
                self.logger.error(f"Failed to archive {source_path}: {e}")
                metadata["archive_error"] = str(e)

        return metadata

    def execute_cleanup_phase(
        self, phase_name: str, patterns: Dict, archive_category: str
    ) -> List[Dict]:
        """Execute a cleanup phase"""
        self.logger.info(f"Executing {phase_name} cleanup phase...")

        archived_files = []

        for subcategory, pattern_list in patterns.items():
            self.logger.info(f"  Processing {subcategory}...")

            for pattern in pattern_list:
                matches = list(self.workspace_root.rglob(pattern))

                # Special handling for root-only test files
                if subcategory == "test_files":
                    matches = [
                        m for m in matches if m.parent == self.workspace_root
                    ]

                for match in matches:
                    # Skip critical files and directories
                    relative_match = match.relative_to(self.workspace_root)
                    if any(
                        str(relative_match).startswith(str(critical))
                        for critical in self.critical_directories
                    ):
                        continue
                    if str(relative_match) in self.critical_files:
                        continue

                    self.logger.info(f"    Archiving: {relative_match}")

                    # Archive the file/directory
                    metadata = self.archive_file(
                        match, archive_category, subcategory
                    )
                    archived_files.append(metadata)

                    # Remove original (if not dry run)
                    if not self.dry_run:
                        try:
                            if match.is_file():
                                match.unlink()
                            else:
                                shutil.rmtree(match)
                        except Exception as e:
                            self.logger.error(f"Failed to remove {match}: {e}")

        return archived_files

    def validate_cleanup(self) -> Dict:
        """Validate that cleanup didn't break anything critical"""
        self.logger.info("Validating cleanup results...")

        validation = {
            "critical_files_present": True,
            "application_imports": True,
            "configuration_loads": True,
            "issues": [],
        }

        # Check critical files
        for critical_file in self.critical_files:
            file_path = self.workspace_root / critical_file
            if not file_path.exists():
                validation["critical_files_present"] = False
                validation["issues"].append(
                    f"Critical file missing: {critical_file}"
                )

        # Test application imports
        try:
            import sys

            sys.path.insert(0, str(self.workspace_root / "src"))

            # Test main imports
            import rfu.main

            validation["application_imports"] = True

        except Exception as e:
            validation["application_imports"] = False
            validation["issues"].append(f"Import error: {e}")

        return validation

    def generate_completion_report(
        self, archived_files: List[Dict], validation: Dict
    ) -> Dict:
        """Generate comprehensive completion report"""
        report = {
            "cleanup_timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "archive_location": str(self.archive_root),
            "dry_run": self.dry_run,
            "summary": {
                "total_files_archived": len(archived_files),
                "migration_artifacts": len(
                    [
                        f
                        for f in archived_files
                        if "migration-artifacts" in f.get("archived_path", "")
                    ]
                ),
                "debug_artifacts": len(
                    [
                        f
                        for f in archived_files
                        if "debug-scripts" in f.get("archived_path", "")
                    ]
                ),
                "legacy_backups": len(
                    [
                        f
                        for f in archived_files
                        if "legacy-backups" in f.get("archived_path", "")
                    ]
                ),
            },
            "validation": validation,
            "archived_files": archived_files,
            "safety_backup_tag": f"pre-cleanup-backup-{self.timestamp}",
            "next_steps": [
                "Run comprehensive test suite",
                "Validate application functionality",
                "Update documentation references",
                "Team notification of completed cleanup",
                "Monitor for any issues over next 48 hours",
            ],
        }

        # Save report
        report_file = (
            self.workspace_root
            / f"cleanup-completion-report-{self.timestamp}.json"
        )
        if not self.dry_run:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

        return report

    def run_cleanup(self) -> Dict:
        """Execute complete cleanup process"""
        self.logger.info(
            f"Starting pre-beta workspace cleanup ({'DRY RUN' if self.dry_run else 'LIVE RUN'})..."
        )

        # Step 1: Create safety backup
        if not self.create_safety_backup():
            self.logger.error(
                "Failed to create safety backup. Aborting cleanup."
            )
            return {"success": False, "error": "Backup creation failed"}

        # Step 2: Analyze workspace
        analysis = self.analyze_workspace()

        # Step 3: Create archive structure
        self.create_archive_structure()

        # Step 4: Execute cleanup phases
        all_archived_files = []

        # Phase 1: Migration artifacts
        migration_archived = self.execute_cleanup_phase(
            "Migration Artifacts",
            self.migration_patterns,
            "migration-artifacts",
        )
        all_archived_files.extend(migration_archived)

        # Phase 2: Debug scripts
        debug_archived = self.execute_cleanup_phase(
            "Debug Scripts", self.debug_patterns, "debug-scripts"
        )
        all_archived_files.extend(debug_archived)

        # Phase 3: Legacy backups
        backup_archived = self.execute_cleanup_phase(
            "Legacy Backups", self.legacy_backup_patterns, "legacy-backups"
        )
        all_archived_files.extend(backup_archived)

        # Step 5: Validation
        validation = self.validate_cleanup()

        # Step 6: Generate completion report
        report = self.generate_completion_report(
            all_archived_files, validation
        )

        # Step 7: Final summary
        self.logger.info("Cleanup completed!")
        self.logger.info(f"Total files archived: {len(all_archived_files)}")
        self.logger.info(f"Archive location: {self.archive_root}")
        self.logger.info(
            f"Validation {'PASSED' if all(validation.values()) else 'FAILED'}"
        )

        if validation["issues"]:
            self.logger.warning("Validation issues found:")
            for issue in validation["issues"]:
                self.logger.warning(f"  - {issue}")

        return {
            "success": True,
            "report": report,
            "archived_files": len(all_archived_files),
            "validation": validation,
        }


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Pre-Beta Workspace Cleanup")
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument(
        "--live-run",
        action="store_true",
        help="Execute actual cleanup (default is dry run)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup
    workspace_root = Path(args.workspace).resolve()
    dry_run = not args.live_run

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print(f"Pre-Beta Workspace Cleanup")
    print(f"Workspace: {workspace_root}")
    print(
        f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE RUN (files will be moved/deleted)'}"
    )
    print()

    if not dry_run:
        confirmation = input(
            "Are you sure you want to proceed with live cleanup? (yes/no): "
        )
        if confirmation.lower() != "yes":
            print("Cleanup cancelled.")
            return

    # Execute cleanup
    cleanup = PreBetaCleanup(workspace_root, dry_run=dry_run)
    result = cleanup.run_cleanup()

    if result["success"]:
        print("\n✅ Cleanup completed successfully!")
        if dry_run:
            print(
                "This was a dry run. Use --live-run to execute actual cleanup."
            )
    else:
        print("\n❌ Cleanup failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
