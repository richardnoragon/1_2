#!/usr/bin/env python3
"""
FR-01.7: Quality Validation and Testing Pipeline

Implements validation pipeline for test modernization:
- Modernize -> Test -> Coverage comparison workflow
- Automated rollback on test failures
- Before/after coverage metrics reports

Generated: 2025-12-19T16:50:00Z
Task Reference: FR-01.7 Manual Test Modernization
Authority: Quality Assurance Engineer
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage metrics for a test file."""

    file_path: str
    statements_total: int = 0
    statements_covered: int = 0
    statements_missing: int = 0
    coverage_percent: float = 0.0
    branches_total: int = 0
    branches_covered: int = 0
    branch_coverage_percent: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "statements": {
                "total": self.statements_total,
                "covered": self.statements_covered,
                "missing": self.statements_missing,
            },
            "coverage_percent": round(self.coverage_percent, 2),
            "branches": {
                "total": self.branches_total,
                "covered": self.branches_covered,
            },
            "branch_coverage_percent": round(self.branch_coverage_percent, 2),
        }


@dataclass
class ValidationResult:
    """Result of validating a modernized test."""

    test_file: str
    status: str = "pending"  # 'pending', 'passed', 'failed', 'skipped', 'error'
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_total: int = 0
    coverage_before: Optional[CoverageMetrics] = None
    coverage_after: Optional[CoverageMetrics] = None
    coverage_improvement: float = 0.0
    error_message: Optional[str] = None
    rollback_performed: bool = False
    validation_time_ms: float = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "test_file": self.test_file,
            "status": self.status,
            "tests": {
                "passed": self.tests_passed,
                "failed": self.tests_failed,
                "skipped": self.tests_skipped,
                "total": self.tests_total,
            },
            "coverage_before": (
                self.coverage_before.to_dict() if self.coverage_before else None
            ),
            "coverage_after": (
                self.coverage_after.to_dict() if self.coverage_after else None
            ),
            "coverage_improvement": round(self.coverage_improvement, 2),
            "error_message": self.error_message,
            "rollback_performed": self.rollback_performed,
            "validation_time_ms": round(self.validation_time_ms, 2),
        }


class ValidationPipeline:
    """
    Validation pipeline for test modernization.

    Pipeline stages:
    1. Backup original test file
    2. Run modernization script
    3. Execute tests with coverage
    4. Compare coverage metrics
    5. Rollback if tests fail
    6. Generate comprehensive report
    """

    def __init__(
        self,
        project_root: str,
        reports_dir: Optional[str] = None,
        rollback_on_failure: bool = True,
        collect_coverage: bool = True,
        python_executable: Optional[str] = None,
    ):
        """
        Initialize validation pipeline.

        Args:
            project_root: Root directory of the project
            reports_dir: Directory for validation reports
            rollback_on_failure: Auto-rollback if tests fail
            collect_coverage: Collect coverage metrics
            python_executable: Python executable path
        """
        self.project_root = Path(project_root)
        self.reports_dir = (
            Path(reports_dir)
            if reports_dir
            else self.project_root / "reports" / "test_modernization"
        )
        self.rollback_on_failure = rollback_on_failure
        self.collect_coverage = collect_coverage

        # Find Python executable
        if python_executable:
            self.python = python_executable
        else:
            # Look for venv Python
            venv_python = self.project_root / ".venv312" / "Scripts" / "python.exe"
            if venv_python.exists():
                self.python = str(venv_python)
            else:
                venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
                if venv_python.exists():
                    self.python = str(venv_python)
                else:
                    self.python = sys.executable

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results: List[ValidationResult] = []
        self.backup_dir = (
            self.project_root / "temp" / "validation_backups" / self.session_id
        )

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _backup_file(self, file_path: Path) -> Path:
        """Create backup of test file."""
        backup_path = self.backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up: {file_path.name} -> {backup_path}")
        return backup_path

    def _restore_backup(self, original_path: Path, backup_path: Path) -> bool:
        """Restore test file from backup."""
        try:
            shutil.copy2(backup_path, original_path)
            logger.info(f"Restored: {backup_path.name} -> {original_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def _run_modernization(
        self, test_file: Path, dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Run modernization script on test file.

        Returns:
            Tuple of (success, message)
        """
        script_path = (
            self.project_root
            / "scripts"
            / "test_modernization"
            / "import_modernization_script.py"
        )

        if not script_path.exists():
            return False, f"Modernization script not found: {script_path}"

        cmd = [
            self.python,
            str(script_path),
            str(test_file),  # Positional argument for file
        ]

        if dry_run:
            cmd.append("--dry-run")
        else:
            cmd.append("--execute")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, "Modernization timed out"
        except Exception as e:
            return False, str(e)

    def _run_pytest(
        self,
        test_file: Path,
        with_coverage: bool = False,
        coverage_source: Optional[str] = None,
    ) -> Tuple[int, int, int, Optional[CoverageMetrics], str]:
        """
        Run pytest on test file.

        Returns:
            Tuple of (passed, failed, skipped, coverage_metrics, output)
        """
        cmd = [self.python, "-m", "pytest", str(test_file), "-v", "--tb=short"]

        if with_coverage:
            coverage_src = coverage_source or "src"
            cmd.extend(
                [f"--cov={coverage_src}", "--cov-report=json", "--cov-report=term"]
            )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=120,
            )

            output = result.stdout + result.stderr

            # Parse test results from output
            passed = failed = skipped = 0

            # Look for pytest summary line like "5 passed, 2 skipped in 1.23s"
            for line in output.split("\n"):
                if "passed" in line or "failed" in line or "skipped" in line:
                    import re

                    # Match patterns like "9 passed" or "2 failed"
                    passed_match = re.search(r"(\d+)\s+passed", line)
                    failed_match = re.search(r"(\d+)\s+failed", line)
                    skipped_match = re.search(r"(\d+)\s+skipped", line)

                    if passed_match:
                        passed = int(passed_match.group(1))
                    if failed_match:
                        failed = int(failed_match.group(1))
                    if skipped_match:
                        skipped = int(skipped_match.group(1))

            # Parse coverage if requested
            coverage = None
            if with_coverage:
                coverage_json = self.project_root / "coverage.json"
                if coverage_json.exists():
                    coverage = self._parse_coverage_json(test_file, coverage_json)

            return passed, failed, skipped, coverage, output

        except subprocess.TimeoutExpired:
            return 0, 0, 0, None, "Test execution timed out"
        except Exception as e:
            return 0, 0, 0, None, str(e)

    def _parse_coverage_json(
        self, test_file: Path, coverage_json: Path
    ) -> CoverageMetrics:
        """Parse coverage.json for metrics."""
        metrics = CoverageMetrics(file_path=str(test_file))

        try:
            with open(coverage_json, "r") as f:
                data = json.load(f)

            totals = data.get("totals", {})

            metrics.statements_total = totals.get("num_statements", 0)
            metrics.statements_covered = totals.get("covered_lines", 0)
            metrics.statements_missing = totals.get("missing_lines", 0)
            metrics.coverage_percent = totals.get("percent_covered", 0.0)
            metrics.branches_total = totals.get("num_branches", 0)
            metrics.branches_covered = totals.get("covered_branches", 0)

            if metrics.branches_total > 0:
                metrics.branch_coverage_percent = (
                    metrics.branches_covered / metrics.branches_total
                ) * 100

        except Exception as e:
            logger.warning(f"Failed to parse coverage: {e}")

        return metrics

    def validate_single(
        self, test_file: Path, dry_run: bool = False
    ) -> ValidationResult:
        """
        Validate a single test file through the full pipeline.

        Pipeline:
        1. Backup original
        2. Run baseline tests (if coverage enabled)
        3. Modernize test file
        4. Run tests again
        5. Compare coverage
        6. Rollback if failed

        Args:
            test_file: Path to test file
            dry_run: If True, don't actually modify files

        Returns:
            ValidationResult
        """
        import time

        start_time = time.time()

        result = ValidationResult(test_file=str(test_file))
        logger.info(f"Validating: {test_file.name}")

        # Step 1: Backup
        backup_path = None
        if not dry_run:
            backup_path = self._backup_file(test_file)

        # Step 2: Run baseline tests (before modernization)
        if self.collect_coverage:
            logger.info(f"  Running baseline tests...")
            _, _, _, coverage_before, _ = self._run_pytest(
                test_file, with_coverage=True
            )
            result.coverage_before = coverage_before

        # Step 3: Modernize
        logger.info(f"  Running modernization...")
        mod_success, mod_message = self._run_modernization(test_file, dry_run=dry_run)

        if not mod_success:
            result.status = "error"
            result.error_message = f"Modernization failed: {mod_message}"
            result.validation_time_ms = (time.time() - start_time) * 1000
            return result

        # Step 4: Run tests after modernization
        logger.info(f"  Running tests after modernization...")
        passed, failed, skipped, coverage_after, output = self._run_pytest(
            test_file, with_coverage=self.collect_coverage
        )

        result.tests_passed = passed
        result.tests_failed = failed
        result.tests_skipped = skipped
        result.tests_total = passed + failed + skipped
        result.coverage_after = coverage_after

        # Step 5: Calculate coverage improvement
        if result.coverage_before and result.coverage_after:
            result.coverage_improvement = (
                result.coverage_after.coverage_percent
                - result.coverage_before.coverage_percent
            )

        # Step 6: Determine status and rollback if needed
        if failed > 0:
            result.status = "failed"
            result.error_message = f"{failed} test(s) failed"

            if self.rollback_on_failure and backup_path and not dry_run:
                logger.warning(f"  Rolling back due to test failures...")
                if self._restore_backup(test_file, backup_path):
                    result.rollback_performed = True

        elif passed == 0 and skipped == 0:
            result.status = "error"
            result.error_message = "No tests executed"
        else:
            result.status = "passed"

        result.validation_time_ms = (time.time() - start_time) * 1000

        # Log summary
        status_icon = (
            "PASS"
            if result.status == "passed"
            else "FAIL" if result.status == "failed" else "ERROR"
        )
        logger.info(
            f"  Result: [{status_icon}] {passed} passed, {failed} failed, {skipped} skipped"
        )

        return result

    def validate_batch(self, test_files: List[Path], dry_run: bool = False) -> Dict:
        """
        Validate multiple test files.

        Args:
            test_files: List of test file paths
            dry_run: If True, don't actually modify files

        Returns:
            Batch validation report
        """
        logger.info(f"Starting batch validation of {len(test_files)} files")

        for test_file in test_files:
            result = self.validate_single(test_file, dry_run)
            self.results.append(result)

        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report."""
        passed = [r for r in self.results if r.status == "passed"]
        failed = [r for r in self.results if r.status == "failed"]
        errors = [r for r in self.results if r.status == "error"]

        total_tests = sum(r.tests_total for r in self.results)
        total_passed = sum(r.tests_passed for r in self.results)
        total_failed = sum(r.tests_failed for r in self.results)

        avg_coverage_improvement = 0.0
        coverage_results = [
            r for r in self.results if r.coverage_before and r.coverage_after
        ]
        if coverage_results:
            avg_coverage_improvement = sum(
                r.coverage_improvement for r in coverage_results
            ) / len(coverage_results)

        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "files_validated": len(self.results),
                "files_passed": len(passed),
                "files_failed": len(failed),
                "files_error": len(errors),
                "total_tests": total_tests,
                "tests_passed": total_passed,
                "tests_failed": total_failed,
                "rollbacks_performed": sum(
                    1 for r in self.results if r.rollback_performed
                ),
                "avg_coverage_improvement": round(avg_coverage_improvement, 2),
            },
            "results": [r.to_dict() for r in self.results],
            "passed_files": [r.test_file for r in passed],
            "failed_files": [
                {"file": r.test_file, "error": r.error_message} for r in failed
            ],
            "error_files": [
                {"file": r.test_file, "error": r.error_message} for r in errors
            ],
            "configuration": {
                "rollback_on_failure": self.rollback_on_failure,
                "collect_coverage": self.collect_coverage,
            },
        }

        # Save report
        report_path = self.reports_dir / f"validation_report_{self.session_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {report_path}")

        return report


def discover_high_value_tests(project_root: Path) -> List[Path]:
    """
    Discover high-value test files for validation.

    Based on FR-01.2 high-value test identification.
    """
    tests_dir = project_root / "tests"

    # High-value test patterns from FR-01.2 analysis
    high_value_patterns = [
        "test_empty_folders.py",
        "test_compression_logic.py",
        "test_secure_delete.py",
        "test_checksum.py",
        "test_encryption.py",
        "test_file_operations.py",
        "test_file_touch.py",
    ]

    discovered = []
    for pattern in high_value_patterns:
        test_path = tests_dir / pattern
        if test_path.exists():
            discovered.append(test_path)
        else:
            # Try in archive
            archive_path = project_root / "archive" / pattern
            if archive_path.exists():
                discovered.append(archive_path)

    return discovered


def print_report_summary(report: Dict):
    """Print formatted report summary."""
    summary = report["summary"]

    print("\n" + "=" * 60)
    print("VALIDATION PIPELINE REPORT")
    print("=" * 60)
    print(f"Session ID: {report['session_id']}")
    print(f"Timestamp: {report['timestamp']}")
    print("-" * 60)
    print(f"Files Validated: {summary['files_validated']}")
    print(f"  - Passed:  {summary['files_passed']}")
    print(f"  - Failed:  {summary['files_failed']}")
    print(f"  - Errors:  {summary['files_error']}")
    print("-" * 60)
    print(f"Total Tests Run: {summary['total_tests']}")
    print(f"  - Passed:  {summary['tests_passed']}")
    print(f"  - Failed:  {summary['tests_failed']}")
    print("-" * 60)
    print(f"Rollbacks Performed: {summary['rollbacks_performed']}")
    print(f"Avg Coverage Change: {summary['avg_coverage_improvement']:+.2f}%")
    print("=" * 60)

    if report["failed_files"]:
        print("\nFailed Files:")
        for item in report["failed_files"]:
            print(f"  - {Path(item['file']).name}: {item['error']}")

    if report["error_files"]:
        print("\nError Files:")
        for item in report["error_files"]:
            print(f"  - {Path(item['file']).name}: {item['error']}")


def main():
    """Main entry point for validation pipeline."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FR-01.7: Quality Validation Pipeline for Test Modernization"
    )
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).parent.parent.parent),
        help="Project root directory",
    )
    parser.add_argument("--files", nargs="+", help="Specific test files to validate")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't actually modify files"
    )
    parser.add_argument(
        "--no-rollback", action="store_true", help="Don't rollback on test failures"
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Don't collect coverage metrics"
    )
    parser.add_argument(
        "--discover", action="store_true", help="Auto-discover high-value tests"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    # Determine test files
    if args.files:
        test_files = [Path(f) for f in args.files]
    elif args.discover:
        test_files = discover_high_value_tests(project_root)
        if not test_files:
            print("No high-value test files discovered")
            return 1
    else:
        print("Please specify --files or --discover")
        return 1

    print(f"\nValidation Pipeline - FR-01.7")
    print(f"Project: {project_root}")
    print(f"Files: {len(test_files)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Create pipeline
    pipeline = ValidationPipeline(
        project_root=str(project_root),
        rollback_on_failure=not args.no_rollback,
        collect_coverage=not args.no_coverage,
    )

    # Run validation
    report = pipeline.validate_batch(test_files, dry_run=args.dry_run)

    # Print summary
    print_report_summary(report)

    # Return exit code based on results
    if report["summary"]["files_failed"] > 0 or report["summary"]["files_error"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
