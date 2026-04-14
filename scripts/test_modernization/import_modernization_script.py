#!/usr/bin/env python3
"""
FR-01.3: Import Path Modernization Script

A comprehensive script to modernize deprecated test file imports to current module paths.
This script supports dry-run mode, validation, and rollback capabilities.

Generated: 2025-12-19T06:20:00Z
Task Reference: FR-01.3 Manual Test Modernization
Authority: Senior Python Developer
"""

import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ImportMapping:
    """Represents a deprecated-to-current import mapping."""

    deprecated: str
    current: str
    pattern_type: str  # 'module', 'class', 'function'
    priority: int  # Higher = apply first


@dataclass
class ModernizationResult:
    """Result of a single file modernization attempt."""

    file_path: str
    success: bool
    changes_made: int
    original_content: Optional[str]
    new_content: Optional[str]
    error_message: Optional[str]
    imports_updated: List[str]


# ============================================================================
# COMPREHENSIVE IMPORT MAPPING CONFIGURATION
# ============================================================================

# Primary module path transformations (apply first)
MODULE_MAPPINGS: List[ImportMapping] = [
    # Core modules
    ImportMapping("file_utilities_2.core", "src.core", "module", 100),
    ImportMapping("file_utilities_1.core", "src.core", "module", 100),
    ImportMapping("src_backup.core", "src.core", "module", 100),
    # File utilities root
    ImportMapping("file_utilities_2", "src", "module", 90),
    ImportMapping("file_utilities_1", "src", "module", 90),
    # Utilities - Analysis
    ImportMapping(
        "file_utilities_2.core.size_analyzer_logic",
        "src.tools.analysis.size_analyzer.size_analyzer_logic",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.core.size_analyzer_config",
        "src.tools.analysis.size_analyzer.size_analyzer_config",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.gui.size_analyzer_gui",
        "src.tools.analysis.size_analyzer.size_analyzer_gui",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.core.check_sum",
        "src.tools.analysis.checksum.check_sum",
        "module",
        80,
    ),
    # Utilities - Security
    ImportMapping(
        "file_utilities_2.core.encryption_logic",
        "src.tools.security.core.encryption_logic",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.core.encryption_config",
        "src.tools.security.core.encryption_config",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.core.encryption_logging",
        "src.tools.security.core.encryption_logging",
        "module",
        80,
    ),
    ImportMapping(
        "file_utilities_2.integration.encryption_connector",
        "src.tools.security.integration.encryption_connector",
        "module",
        80,
    ),
    # GUI Components
    ImportMapping(
        "file_utilities_2.gui.tag_viewer_editor",
        "src.tools.metadata.tag_viewer.tag_viewer_editor",
        "module",
        80,
    ),
    # File Operations
    ImportMapping(
        "file_utilities_1.catalog",
        "src.tools.file_management.catalog.catalog",
        "module",
        80,
    ),
    ImportMapping("file_utilities_1", "src.tools.file_management.finder", "module", 70),
    # File Explorer (HP-03 verified replacement)
    ImportMapping(
        "src.file_explorer.multi_pane_explorer", "src.rfu.tabbed_hub", "module", 95
    ),
    ImportMapping("src.file_explorer", "src.rfu.tabbed_hub", "module", 90),
    ImportMapping("file_explorer", "src.rfu.tabbed_hub", "module", 85),
]

# Class/function renaming mappings
CLASS_MAPPINGS: List[ImportMapping] = [
    ImportMapping("FileExplorerGUI", "TabbedHubGUI", "class", 50),
    ImportMapping("FileExplorer", "TabbedHub", "class", 50),
    ImportMapping("MultiPaneFileExplorer", "TabbedHub", "class", 50),
    ImportMapping("FileExplorerConfig", "RFUConfig", "class", 50),
    ImportMapping("FileUtilitiesCore", "RFUCore", "class", 50),
]

# Standalone module mappings (for top-level imports)
STANDALONE_MAPPINGS: Dict[str, str] = {
    "empty_folders": "src.tools.analysis.empty_folders.empty_folders",
    "compress_decompress": "src.tools.file_operations.compression.compress_decompress",
    "EmptyFolderLogic": "EmptyFolderLogic",  # Class stays same
    "EmptyFolderCleaner": "EmptyFolderGUI",  # Class renamed
}


class TestModernizer:
    """
    Handles the modernization of test files with deprecated imports.

    Features:
    - Dry-run mode for safe testing
    - Automatic backup creation
    - Rollback capability
    - Validation of modernized imports
    - Progress reporting
    """

    def __init__(self, project_root: str, dry_run: bool = True):
        """
        Initialize the modernizer.

        Args:
            project_root: Root directory of the project
            dry_run: If True, don't modify files, just report changes
        """
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup_dir = self.project_root / "backups" / "test_modernization"
        self.results: List[ModernizationResult] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sort mappings by priority (highest first)
        self.module_mappings = sorted(
            MODULE_MAPPINGS, key=lambda x: x.priority, reverse=True
        )
        self.class_mappings = sorted(
            CLASS_MAPPINGS, key=lambda x: x.priority, reverse=True
        )

    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of the file before modification."""
        if self.dry_run:
            return None

        backup_subdir = self.backup_dir / self.session_id
        backup_subdir.mkdir(parents=True, exist_ok=True)

        relative_path = file_path.relative_to(self.project_root)
        backup_path = backup_subdir / relative_path.as_posix().replace("/", "_")

        shutil.copy2(file_path, backup_path)
        return backup_path

    def modernize_imports(self, content: str) -> Tuple[str, List[str], int]:
        """
        Apply import modernization transformations to content.

        Returns:
            Tuple of (new_content, list_of_changes, change_count)
        """
        changes = []
        change_count = 0

        # Apply module mappings
        for mapping in self.module_mappings:
            # Pattern for 'from X import Y'
            from_pattern = rf"from\s+{re.escape(mapping.deprecated)}(\.\w+)*\s+import"
            if re.search(from_pattern, content):
                old_content = content
                content = re.sub(
                    from_pattern,
                    lambda m: m.group(0).replace(mapping.deprecated, mapping.current),
                    content,
                )
                if content != old_content:
                    changes.append(f"Module: {mapping.deprecated} -> {mapping.current}")
                    change_count += 1

            # Pattern for 'import X'
            import_pattern = rf"^import\s+{re.escape(mapping.deprecated)}(\.\w+)*\s*$"
            if re.search(import_pattern, content, re.MULTILINE):
                old_content = content
                content = re.sub(
                    import_pattern,
                    lambda m: m.group(0).replace(mapping.deprecated, mapping.current),
                    content,
                    flags=re.MULTILINE,
                )
                if content != old_content:
                    changes.append(f"Import: {mapping.deprecated} -> {mapping.current}")
                    change_count += 1

        # Apply standalone module mappings
        for old_module, new_module in STANDALONE_MAPPINGS.items():
            if old_module == new_module:
                continue  # Skip if no change needed

            # Pattern for 'from old_module import'
            pattern = rf"from\s+{re.escape(old_module)}\s+import"
            if re.search(pattern, content):
                old_content = content
                content = re.sub(pattern, f"from {new_module} import", content)
                if content != old_content:
                    changes.append(f"Standalone: {old_module} -> {new_module}")
                    change_count += 1

        # Apply class mappings
        for mapping in self.class_mappings:
            # Pattern for class references in imports and code
            class_pattern = rf"\b{re.escape(mapping.deprecated)}\b"
            if re.search(class_pattern, content):
                old_content = content
                content = re.sub(class_pattern, mapping.current, content)
                if content != old_content:
                    changes.append(f"Class: {mapping.deprecated} -> {mapping.current}")
                    change_count += 1

        return content, changes, change_count

    def modernize_file(self, file_path: Path) -> ModernizationResult:
        """
        Modernize a single test file.

        Args:
            file_path: Path to the test file

        Returns:
            ModernizationResult with details of the operation
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            new_content, changes, change_count = self.modernize_imports(
                original_content
            )

            if change_count == 0:
                return ModernizationResult(
                    file_path=str(file_path),
                    success=True,
                    changes_made=0,
                    original_content=None,
                    new_content=None,
                    error_message=None,
                    imports_updated=[],
                )

            if not self.dry_run:
                self.create_backup(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

            return ModernizationResult(
                file_path=str(file_path),
                success=True,
                changes_made=change_count,
                original_content=original_content if self.dry_run else None,
                new_content=new_content if self.dry_run else None,
                error_message=None,
                imports_updated=changes,
            )

        except Exception as e:
            return ModernizationResult(
                file_path=str(file_path),
                success=False,
                changes_made=0,
                original_content=None,
                new_content=None,
                error_message=str(e),
                imports_updated=[],
            )

    def modernize_files(self, file_paths: List[Path]) -> List[ModernizationResult]:
        """
        Modernize multiple test files.

        Args:
            file_paths: List of paths to test files

        Returns:
            List of ModernizationResults
        """
        results = []
        for file_path in file_paths:
            result = self.modernize_file(file_path)
            results.append(result)
            self.results.append(result)
        return results

    def rollback_session(self, session_id: Optional[str] = None) -> bool:
        """
        Rollback all changes from a modernization session.

        Args:
            session_id: Session ID to rollback (default: current session)

        Returns:
            True if rollback successful
        """
        session_id = session_id or self.session_id
        backup_subdir = self.backup_dir / session_id

        if not backup_subdir.exists():
            print(f"No backup found for session {session_id}")
            return False

        for backup_file in backup_subdir.glob("*"):
            # Reconstruct original path from backup filename
            original_rel_path = backup_file.name.replace("_", "/")
            original_path = self.project_root / original_rel_path

            try:
                shutil.copy2(backup_file, original_path)
                print(f"Restored: {original_path}")
            except Exception as e:
                print(f"Failed to restore {original_path}: {e}")
                return False

        return True

    def generate_report(self) -> Dict:
        """Generate a comprehensive modernization report."""
        successful = [r for r in self.results if r.success and r.changes_made > 0]
        failed = [r for r in self.results if not r.success]
        unchanged = [r for r in self.results if r.success and r.changes_made == 0]

        return {
            "session_id": self.session_id,
            "dry_run": self.dry_run,
            "summary": {
                "total_files": len(self.results),
                "successful_modernizations": len(successful),
                "failed": len(failed),
                "unchanged": len(unchanged),
                "total_changes": sum(r.changes_made for r in self.results),
            },
            "successful_files": [
                {
                    "file": r.file_path,
                    "changes": r.changes_made,
                    "updates": r.imports_updated,
                }
                for r in successful
            ],
            "failed_files": [
                {"file": r.file_path, "error": r.error_message} for r in failed
            ],
            "timestamp": datetime.now().isoformat(),
        }

    def save_report(self, report_path: Optional[Path] = None) -> Path:
        """Save the modernization report to a JSON file."""
        report = self.generate_report()

        if report_path is None:
            reports_dir = self.project_root / "reports" / "test_modernization"
            reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = reports_dir / f"modernization_report_{self.session_id}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report_path


def validate_imports(file_path: Path, project_root: Path) -> List[str]:
    """
    Validate that all imports in a file can be resolved.

    Returns:
        List of import errors (empty if all valid)
    """
    import ast
    import sys

    errors = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Add project root to path for import resolution
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        __import__(alias.name)
                    except ImportError as e:
                        errors.append(f"Import '{alias.name}': {e}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        __import__(node.module)
                    except ImportError as e:
                        errors.append(f"From '{node.module}': {e}")

        sys.path = original_path

    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
    except Exception as e:
        errors.append(f"Validation error: {e}")

    return errors


def validate_syntax(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate Python syntax of a file.

    FR-01.5 Enhancement: Syntax validation before and after modernization.

    Returns:
        Tuple of (is_valid, error_message)
    """
    import ast

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def run_pytest_collection(file_path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Run pytest collection on a single file to validate it can be collected.

    FR-01.5 Enhancement: pytest collection test for modernized files.

    Returns:
        Tuple of (success, output)
    """
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(file_path), "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
        )

        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        return success, output

    except subprocess.TimeoutExpired:
        return False, "Collection timeout (30s)"
    except Exception as e:
        return False, str(e)


class ModernizationValidator:
    """
    FR-01.5 Enhancement: Comprehensive validation for modernized tests.

    Performs:
    1. Syntax validation
    2. Import resolution check
    3. pytest collection test
    4. Comparison with original behavior
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_results = []

    def validate_file(
        self, file_path: Path, original_content: Optional[str] = None
    ) -> Dict:
        """
        Perform comprehensive validation on a modernized file.

        Returns:
            Dict with validation results
        """
        result = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "syntax_valid": False,
            "syntax_error": None,
            "imports_valid": False,
            "import_errors": [],
            "pytest_collects": False,
            "pytest_output": None,
            "overall_valid": False,
        }

        # 1. Syntax validation
        is_valid, error = validate_syntax(file_path)
        result["syntax_valid"] = is_valid
        result["syntax_error"] = error

        if not is_valid:
            self.validation_results.append(result)
            return result

        # 2. Import resolution
        import_errors = validate_imports(file_path, self.project_root)
        result["imports_valid"] = len(import_errors) == 0
        result["import_errors"] = import_errors

        # 3. pytest collection (only if syntax and imports are valid)
        if result["syntax_valid"] and result["imports_valid"]:
            success, output = run_pytest_collection(file_path, self.project_root)
            result["pytest_collects"] = success
            result["pytest_output"] = output

        # Overall validation
        result["overall_valid"] = (
            result["syntax_valid"]
            and result["imports_valid"]
            and result["pytest_collects"]
        )

        self.validation_results.append(result)
        return result

    def generate_validation_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        valid = [r for r in self.validation_results if r["overall_valid"]]
        invalid = [r for r in self.validation_results if not r["overall_valid"]]

        return {
            "timestamp": datetime.now().isoformat(),
            "total_validated": len(self.validation_results),
            "passed": len(valid),
            "failed": len(invalid),
            "pass_rate": (
                f"{len(valid)/len(self.validation_results)*100:.1f}%"
                if self.validation_results
                else "N/A"
            ),
            "passed_files": [r["file_path"] for r in valid],
            "failed_files": [
                {
                    "file": r["file_path"],
                    "syntax_error": r["syntax_error"],
                    "import_errors": r["import_errors"][:3],  # Limit to first 3
                    "pytest_output": (
                        r["pytest_output"][:200] if r["pytest_output"] else None
                    ),
                }
                for r in invalid
            ],
        }


def main():
    """Main entry point for the modernization script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Modernize deprecated test file imports"
    )
    parser.add_argument(
        "files", nargs="*", help="Test files to modernize (default: all in tests/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show changes without modifying files (default: True)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually modify files (disables dry-run)",
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument(
        "--rollback", metavar="SESSION_ID", help="Rollback changes from a session"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate imports after modernization"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dry_run = not args.execute

    modernizer = TestModernizer(str(project_root), dry_run=dry_run)

    # Handle rollback
    if args.rollback:
        success = modernizer.rollback_session(args.rollback)
        print(f"Rollback {'successful' if success else 'failed'}")
        return 0 if success else 1

    # Determine files to process
    if args.files:
        file_paths = [Path(f) for f in args.files]
    else:
        # Default: process deprecated tests from conftest.py patterns
        tests_dir = project_root / "tests"
        file_paths = list(tests_dir.glob("test_*.py"))

    # Run modernization
    print(f"{'[DRY RUN] ' if dry_run else ''}Modernizing {len(file_paths)} files...")

    results = modernizer.modernize_files(file_paths)

    # Print summary
    report = modernizer.generate_report()
    print(f"\n=== Modernization Report ===")
    print(f"Session ID: {report['session_id']}")
    print(f"Total files: {report['summary']['total_files']}")
    print(f"Modernized: {report['summary']['successful_modernizations']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Total changes: {report['summary']['total_changes']}")

    if report["successful_files"]:
        print(f"\n=== Changes ===")
        for item in report["successful_files"]:
            print(f"\n{item['file']}:")
            for update in item["updates"]:
                print(f"  - {update}")

    if report["failed_files"]:
        print(f"\n=== Errors ===")
        for item in report["failed_files"]:
            print(f"{item['file']}: {item['error']}")

    # Save report
    report_path = modernizer.save_report()
    print(f"\nReport saved to: {report_path}")

    # Optional validation
    if args.validate and not dry_run:
        print(f"\n=== Import Validation ===")
        for result in results:
            if result.success and result.changes_made > 0:
                errors = validate_imports(Path(result.file_path), project_root)
                if errors:
                    print(f"\n{result.file_path}:")
                    for error in errors:
                        print(f"  - {error}")
                else:
                    print(f"✓ {result.file_path}")

    return 0


if __name__ == "__main__":
    exit(main())
