#!/usr/bin/env python3
"""
FR-02.6: Archive Cleanup Execution Script

This script executes the phased cleanup strategy defined in FR-02.4,
with full backup support from FR-02.5 and validation at each step.

Task ID: FR-02.6
Generated: 2025-12-19
Status: COMPLETE (Script Ready - Manual Execution Required)
Prerequisites: FR-02.1 through FR-02.5

IMPORTANT: This script requires explicit --execute flag to perform deletions.
Default mode is dry-run which shows what would be deleted.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from backup_system import ArchiveBackupSystem, backup_archive_directories
except ImportError:
    print("Warning: backup_system not available - backup features disabled")
    ArchiveBackupSystem = None

# Configuration
WORKSPACE_ROOT = Path(r"c:\Users\HP1\1_2")
LOG_FILE = WORKSPACE_ROOT / "reports" / "cleanup_execution_log.md"
REPORTS_DIR = WORKSPACE_ROOT / "reports"


class CleanupExecutor:
    """
    Executes phased archive cleanup with validation and logging.

    Phases:
    - Phase 1: Safe removal (venv backups, temp files)
    - Phase 2: Moderate removal (legacy projects after verification)
    - Phase 3: Selective removal (remaining archive content)
    """

    # Phase 1 targets - Very safe to remove
    PHASE_1_TARGETS = [
        "venv_backup_20251021",  # Virtual env backup - fully reproducible
        "venv_temp",  # Temporary venv artifacts
    ]

    # Phase 2 targets - Require backup verification first
    PHASE_2_TARGETS = [
        "file_utilities_2",  # Legacy project
    ]

    # Phase 3 targets - Require careful review
    PHASE_3_TARGETS = [
        # "emergency-backup-20250925_200754",  # Only after full analysis
        # "archive",  # Selective cleanup only
    ]

    def __init__(self, workspace_root: Path = WORKSPACE_ROOT):
        self.workspace_root = workspace_root
        self.log_entries: List[str] = []
        self.stats: Dict[str, int] = {
            "files_deleted": 0,
            "bytes_freed": 0,
            "directories_deleted": 0,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.log_entries.append(entry)
        print(entry)

    def save_log(self):
        """Save execution log to file."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        log_content = [
            "# FR-02.6 Cleanup Execution Log",
            f"\n**Generated**: {datetime.now().isoformat()}",
            f"\n**Files Deleted**: {self.stats['files_deleted']:,}",
            f"**Bytes Freed**: {self.stats['bytes_freed'] / (1024*1024):.2f} MB",
            f"**Directories Deleted**: {self.stats['directories_deleted']}",
            "\n---\n",
            "## Execution Log\n",
            "```",
        ]
        log_content.extend(self.log_entries)
        log_content.append("```")

        with open(LOG_FILE, "w") as f:
            f.write("\n".join(log_content))

        self.log(f"Log saved to: {LOG_FILE}")

    def get_directory_stats(self, directory: Path) -> Tuple[int, int]:
        """Get file count and total size for a directory."""
        if not directory.exists():
            return 0, 0

        file_count = 0
        total_size = 0

        for path in directory.rglob("*"):
            if path.is_file():
                try:
                    file_count += 1
                    total_size += path.stat().st_size
                except (PermissionError, OSError):
                    pass

        return file_count, total_size

    def delete_directory(self, directory: Path, dry_run: bool = True) -> bool:
        """
        Delete a directory with logging.

        Args:
            directory: Path to delete
            dry_run: If True, only log what would happen

        Returns:
            True if successful (or would be successful in dry run)
        """
        if not directory.exists():
            self.log(f"SKIP: {directory.name} (does not exist)", "WARN")
            return False

        file_count, total_size = self.get_directory_stats(directory)
        size_mb = total_size / (1024 * 1024)

        if dry_run:
            self.log(
                f"DRY RUN: Would delete {directory.name} "
                f"({file_count:,} files, {size_mb:.2f} MB)"
            )
            return True

        try:
            shutil.rmtree(directory)
            self.stats["files_deleted"] += file_count
            self.stats["bytes_freed"] += total_size
            self.stats["directories_deleted"] += 1

            self.log(
                f"DELETED: {directory.name} "
                f"({file_count:,} files, {size_mb:.2f} MB)"
            )
            return True

        except Exception as e:
            self.log(f"ERROR: Failed to delete {directory.name}: {e}", "ERROR")
            return False

    def execute_phase_1(self, dry_run: bool = True) -> bool:
        """
        Execute Phase 1: Safe removal of venv backups and temp files.

        These are fully reproducible from requirements.txt.
        """
        self.log("=" * 60)
        self.log("PHASE 1: Safe Virtual Environment Cleanup")
        self.log("=" * 60)

        success = True
        for target_name in self.PHASE_1_TARGETS:
            target_path = self.workspace_root / target_name
            if not self.delete_directory(target_path, dry_run):
                success = False

        return success

    def execute_phase_2(
        self, dry_run: bool = True, require_backup: bool = True
    ) -> bool:
        """
        Execute Phase 2: Moderate removal of legacy projects.

        Args:
            dry_run: If True, only show what would be done
            require_backup: If True, verify backup exists before deletion
        """
        self.log("=" * 60)
        self.log("PHASE 2: Legacy Project Cleanup")
        self.log("=" * 60)

        if require_backup and ArchiveBackupSystem:
            backup_system = ArchiveBackupSystem()
            backups = backup_system.list_backups()

            for target_name in self.PHASE_2_TARGETS:
                has_backup = any(target_name in b.get("source", "") for b in backups)
                if not has_backup:
                    self.log(
                        f"BLOCKED: {target_name} - No backup found. "
                        f"Run 'python backup_system.py backup --execute' first.",
                        "WARN",
                    )
                    return False

        success = True
        for target_name in self.PHASE_2_TARGETS:
            target_path = self.workspace_root / target_name
            if not self.delete_directory(target_path, dry_run):
                success = False

        return success

    def execute_phase_3(self, dry_run: bool = True) -> bool:
        """
        Execute Phase 3: Selective cleanup of remaining archive content.

        This phase requires manual review and explicit target specification.
        """
        self.log("=" * 60)
        self.log("PHASE 3: Selective Archive Cleanup")
        self.log("=" * 60)

        if not self.PHASE_3_TARGETS:
            self.log(
                "Phase 3 targets not configured. "
                "Edit PHASE_3_TARGETS list to specify directories.",
                "INFO",
            )
            return True

        success = True
        for target_name in self.PHASE_3_TARGETS:
            target_path = self.workspace_root / target_name
            if not self.delete_directory(target_path, dry_run):
                success = False

        return success

    def execute_all_phases(self, dry_run: bool = True) -> bool:
        """Execute all cleanup phases in sequence."""
        self.log("FR-02.6 Cleanup Execution Starting")
        self.log(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        self.log(f"Workspace: {self.workspace_root}")

        # Phase 1
        phase_1_ok = self.execute_phase_1(dry_run)

        # Phase 2 (only if Phase 1 succeeded)
        phase_2_ok = True
        if phase_1_ok:
            phase_2_ok = self.execute_phase_2(dry_run)

        # Phase 3 (only if Phase 2 succeeded)
        phase_3_ok = True
        if phase_2_ok:
            phase_3_ok = self.execute_phase_3(dry_run)

        # Summary
        self.log("=" * 60)
        self.log("EXECUTION SUMMARY")
        self.log("=" * 60)
        self.log(f"Phase 1: {'COMPLETE' if phase_1_ok else 'FAILED'}")
        self.log(f"Phase 2: {'COMPLETE' if phase_2_ok else 'FAILED/BLOCKED'}")
        self.log(f"Phase 3: {'COMPLETE' if phase_3_ok else 'FAILED/SKIPPED'}")

        if not dry_run:
            self.log(f"Total files deleted: {self.stats['files_deleted']:,}")
            self.log(
                f"Total space freed: {self.stats['bytes_freed'] / (1024*1024):.2f} MB"
            )

        self.save_log()

        return phase_1_ok and phase_2_ok and phase_3_ok

    def run_validation(self) -> bool:
        """
        Run post-cleanup validation to ensure development environment is intact.
        """
        self.log("=" * 60)
        self.log("POST-CLEANUP VALIDATION")
        self.log("=" * 60)

        checks_passed = True

        # Check main.py exists
        main_py = self.workspace_root / "src" / "rfu" / "main.py"
        if main_py.exists():
            self.log("✓ Main application entry point exists")
        else:
            self.log("✗ Main application entry point MISSING", "ERROR")
            checks_passed = False

        # Check requirements.txt exists
        requirements = self.workspace_root / "requirements.txt"
        if requirements.exists():
            self.log("✓ requirements.txt exists")
        else:
            self.log("✗ requirements.txt MISSING", "ERROR")
            checks_passed = False

        # Check tests directory
        tests_dir = self.workspace_root / "tests"
        if tests_dir.exists():
            test_count = len(list(tests_dir.rglob("test_*.py")))
            self.log(f"✓ Tests directory exists ({test_count} test files)")
        else:
            self.log("✗ Tests directory MISSING", "ERROR")
            checks_passed = False

        # Check src directory
        src_dir = self.workspace_root / "src"
        if src_dir.exists():
            self.log("✓ Source directory exists")
        else:
            self.log("✗ Source directory MISSING", "ERROR")
            checks_passed = False

        # Final result
        if checks_passed:
            self.log("VALIDATION: PASSED - Development environment intact")
        else:
            self.log("VALIDATION: FAILED - Critical files missing!", "ERROR")

        return checks_passed


def main():
    """Main entry point for cleanup execution."""
    print("FR-02.6: Archive Cleanup Execution")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python cleanup_execution.py phase1 [--execute]")
        print("  python cleanup_execution.py phase2 [--execute]")
        print("  python cleanup_execution.py phase3 [--execute]")
        print("  python cleanup_execution.py all [--execute]")
        print("  python cleanup_execution.py validate")
        print("\nOptions:")
        print("  --execute    Actually perform deletions (default is dry-run)")
        print("\nNOTE: Always run without --execute first to preview changes!")
        return

    command = sys.argv[1]
    dry_run = "--execute" not in sys.argv

    executor = CleanupExecutor()

    if command == "phase1":
        executor.execute_phase_1(dry_run)
        executor.save_log()

    elif command == "phase2":
        executor.execute_phase_2(dry_run)
        executor.save_log()

    elif command == "phase3":
        executor.execute_phase_3(dry_run)
        executor.save_log()

    elif command == "all":
        executor.execute_all_phases(dry_run)

    elif command == "validate":
        executor.run_validation()

    else:
        print(f"Unknown command: {command}")
        print("Use: phase1, phase2, phase3, all, or validate")


if __name__ == "__main__":
    main()
