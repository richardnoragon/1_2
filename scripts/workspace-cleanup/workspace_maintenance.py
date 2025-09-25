#!/usr/bin/env python3
"""
Workspace Maintenance Tool
Ongoing maintenance procedures to prevent future accumulation of outdated artifacts
"""

import json
import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set


class WorkspaceMaintenance:
    """Automated workspace maintenance system"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.setup_logging()
        self.load_maintenance_config()

    def setup_logging(self):
        """Setup logging for maintenance operations"""
        log_dir = self.workspace_root / "logs" / "maintenance"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"maintenance-{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_maintenance_config(self):
        """Load maintenance configuration"""
        config_file = self.workspace_root / "config" / "maintenance.json"

        default_config = {
            "daily_tasks": {
                "temp_file_cleanup": {
                    "enabled": True,
                    "max_age_hours": 24,
                    "directories": ["temp/", "data/temp/", ".cache/"],
                },
                "log_rotation": {
                    "enabled": True,
                    "max_size_mb": 50,
                    "max_files": 10,
                },
            },
            "weekly_tasks": {
                "branch_cleanup": {
                    "enabled": True,
                    "max_age_days": 14,
                    "exclude_branches": ["master", "main", "develop"],
                },
                "documentation_check": {
                    "enabled": True,
                    "patterns": ["*.md", "docs/**/*"],
                },
            },
            "monthly_tasks": {
                "dependency_audit": {
                    "enabled": True,
                    "check_outdated": True,
                    "security_scan": True,
                },
                "performance_baseline": {
                    "enabled": True,
                    "test_suites": ["unit", "integration"],
                },
            },
            "quality_thresholds": {
                "max_root_files": 25,
                "max_directory_depth": 6,
                "max_duplicate_files": 5,
                "min_test_coverage": 80,
                "max_log_size_mb": 100,
            },
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)

    def run_daily_maintenance(self) -> Dict:
        """Execute daily maintenance tasks"""
        self.logger.info("Starting daily maintenance...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
            "metrics": {},
        }

        # Temp file cleanup
        if self.config["daily_tasks"]["temp_file_cleanup"]["enabled"]:
            temp_result = self.cleanup_temporary_files()
            results["tasks"]["temp_cleanup"] = temp_result

        # Log rotation
        if self.config["daily_tasks"]["log_rotation"]["enabled"]:
            log_result = self.rotate_logs()
            results["tasks"]["log_rotation"] = log_result

        # Quality metrics
        results["metrics"] = self.calculate_workspace_metrics()

        # Check quality thresholds
        results["threshold_violations"] = self.check_quality_thresholds(
            results["metrics"]
        )

        self.save_maintenance_report("daily", results)
        return results

    def cleanup_temporary_files(self) -> Dict:
        """Clean up temporary files older than specified age"""
        config = self.config["daily_tasks"]["temp_file_cleanup"]
        max_age_hours = config["max_age_hours"]
        directories = config["directories"]

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed_mb": 0,
            "errors": [],
        }

        for dir_pattern in directories:
            temp_dirs = list(self.workspace_root.glob(dir_pattern))

            for temp_dir in temp_dirs:
                if not temp_dir.exists():
                    continue

                try:
                    for item in temp_dir.rglob("*"):
                        if item.is_file():
                            modified_time = datetime.fromtimestamp(
                                item.stat().st_mtime
                            )

                            if modified_time < cutoff_time:
                                size_mb = item.stat().st_size / (1024 * 1024)
                                item.unlink()
                                cleanup_stats["files_removed"] += 1
                                cleanup_stats["space_freed_mb"] += size_mb

                    # Remove empty directories
                    for item in sorted(temp_dir.rglob("*"), reverse=True):
                        if item.is_dir() and not list(item.iterdir()):
                            item.rmdir()
                            cleanup_stats["directories_removed"] += 1

                except Exception as e:
                    cleanup_stats["errors"].append(f"{temp_dir}: {str(e)}")

        self.logger.info(
            f"Temp cleanup: {cleanup_stats['files_removed']} files, "
            f"{cleanup_stats['space_freed_mb']:.1f}MB freed"
        )

        return cleanup_stats

    def rotate_logs(self) -> Dict:
        """Rotate large log files"""
        config = self.config["daily_tasks"]["log_rotation"]
        max_size_mb = config["max_size_mb"]
        max_files = config["max_files"]

        log_dirs = [
            self.workspace_root / "logs",
            self.workspace_root / "logs" / "maintenance",
        ]

        rotation_stats = {
            "files_rotated": 0,
            "files_archived": 0,
            "errors": [],
        }

        for log_dir in log_dirs:
            if not log_dir.exists():
                continue

            for log_file in log_dir.glob("*.log"):
                try:
                    size_mb = log_file.stat().st_size / (1024 * 1024)

                    if size_mb > max_size_mb:
                        # Rotate the file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        rotated_name = f"{log_file.stem}_{timestamp}.log"
                        rotated_file = log_dir / rotated_name

                        shutil.move(log_file, rotated_file)
                        rotation_stats["files_rotated"] += 1

                        # Create new empty log file
                        log_file.touch()

                    # Clean up old rotated files
                    rotated_files = sorted(
                        log_dir.glob(f"{log_file.stem}_*.log")
                    )
                    if len(rotated_files) > max_files:
                        for old_file in rotated_files[:-max_files]:
                            old_file.unlink()
                            rotation_stats["files_archived"] += 1

                except Exception as e:
                    rotation_stats["errors"].append(f"{log_file}: {str(e)}")

        return rotation_stats

    def run_weekly_maintenance(self) -> Dict:
        """Execute weekly maintenance tasks"""
        self.logger.info("Starting weekly maintenance...")

        results = {"timestamp": datetime.now().isoformat(), "tasks": {}}

        # Branch cleanup
        if self.config["weekly_tasks"]["branch_cleanup"]["enabled"]:
            branch_result = self.cleanup_old_branches()
            results["tasks"]["branch_cleanup"] = branch_result

        # Documentation check
        if self.config["weekly_tasks"]["documentation_check"]["enabled"]:
            doc_result = self.check_documentation_health()
            results["tasks"]["documentation_check"] = doc_result

        self.save_maintenance_report("weekly", results)
        return results

    def cleanup_old_branches(self) -> Dict:
        """Clean up old merged branches"""
        config = self.config["weekly_tasks"]["branch_cleanup"]
        max_age_days = config["max_age_days"]
        exclude_branches = set(config["exclude_branches"])

        cleanup_stats = {
            "branches_removed": 0,
            "branches_archived": 0,
            "errors": [],
        }

        try:
            # Get list of branches
            result = subprocess.run(
                ["git", "branch", "-r", "--merged"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )

            merged_branches = [
                branch.strip().replace("origin/", "")
                for branch in result.stdout.split("\n")
                if branch.strip()
                and not branch.strip().startswith("origin/HEAD")
            ]

            cutoff_date = datetime.now() - timedelta(days=max_age_days)

            for branch in merged_branches:
                if branch in exclude_branches:
                    continue

                try:
                    # Get last commit date
                    result = subprocess.run(
                        [
                            "git",
                            "log",
                            "-1",
                            "--format=%ct",
                            f"origin/{branch}",
                        ],
                        cwd=self.workspace_root,
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    last_commit = datetime.fromtimestamp(
                        int(result.stdout.strip())
                    )

                    if last_commit < cutoff_date:
                        # Archive branch info before deletion
                        self.archive_branch_info(branch, last_commit)
                        cleanup_stats["branches_archived"] += 1

                        # Delete remote branch (commented out for safety)
                        # subprocess.run(["git", "push", "origin", "--delete", branch],
                        #               cwd=self.workspace_root, check=True)
                        # cleanup_stats["branches_removed"] += 1

                        self.logger.info(
                            f"Would remove old branch: {branch} (last commit: {last_commit})"
                        )

                except Exception as e:
                    cleanup_stats["errors"].append(f"{branch}: {str(e)}")

        except Exception as e:
            cleanup_stats["errors"].append(f"Git operation failed: {str(e)}")

        return cleanup_stats

    def archive_branch_info(self, branch: str, last_commit: datetime):
        """Archive information about branch before deletion"""
        archive_dir = self.workspace_root / "archive" / "branches"
        archive_dir.mkdir(parents=True, exist_ok=True)

        branch_info = {
            "branch_name": branch,
            "last_commit_date": last_commit.isoformat(),
            "archived_date": datetime.now().isoformat(),
            "reason": "Automated cleanup - old merged branch",
        }

        # Get additional branch information
        try:
            # Get commit hash
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", f"origin/{branch}"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            branch_info["last_commit_hash"] = result.stdout.strip()

            # Get commit message
            result = subprocess.run(
                ["git", "log", "-1", "--format=%s", f"origin/{branch}"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            branch_info["last_commit_message"] = result.stdout.strip()

        except Exception as e:
            branch_info["archive_error"] = str(e)

        # Save branch info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        info_file = archive_dir / f"{branch}_{timestamp}.json"

        with open(info_file, "w") as f:
            json.dump(branch_info, f, indent=2)

    def check_documentation_health(self) -> Dict:
        """Check documentation for outdated content and broken links"""
        config = self.config["weekly_tasks"]["documentation_check"]
        patterns = config["patterns"]

        health_stats = {
            "files_checked": 0,
            "outdated_files": [],
            "broken_links": [],
            "missing_sections": [],
            "suggestions": [],
        }

        for pattern in patterns:
            doc_files = list(self.workspace_root.rglob(pattern))

            for doc_file in doc_files:
                if not doc_file.is_file() or doc_file.suffix not in [
                    ".md",
                    ".rst",
                    ".txt",
                ]:
                    continue

                health_stats["files_checked"] += 1

                try:
                    with open(doc_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check for outdated references
                    outdated_patterns = [
                        "migration_phase",
                        "debug_",
                        "fix_",
                        ".reorganization_backup",
                    ]

                    for pattern in outdated_patterns:
                        if pattern in content:
                            health_stats["outdated_files"].append(
                                {
                                    "file": str(
                                        doc_file.relative_to(
                                            self.workspace_root
                                        )
                                    ),
                                    "pattern": pattern,
                                }
                            )

                    # Check for common missing sections in README files
                    if doc_file.name.lower().startswith("readme"):
                        required_sections = [
                            "installation",
                            "usage",
                            "testing",
                        ]
                        for section in required_sections:
                            if section.lower() not in content.lower():
                                health_stats["missing_sections"].append(
                                    {
                                        "file": str(
                                            doc_file.relative_to(
                                                self.workspace_root
                                            )
                                        ),
                                        "missing_section": section,
                                    }
                                )

                except Exception as e:
                    health_stats["suggestions"].append(
                        f"Could not check {doc_file}: {e}"
                    )

        return health_stats

    def calculate_workspace_metrics(self) -> Dict:
        """Calculate current workspace quality metrics"""
        metrics = {
            "total_files": 0,
            "total_directories": 0,
            "root_files": 0,
            "max_directory_depth": 0,
            "duplicate_files": 0,
            "log_size_mb": 0,
            "test_files": 0,
            "source_files": 0,
        }

        # Count files in root directory
        metrics["root_files"] = len(
            [f for f in self.workspace_root.iterdir() if f.is_file()]
        )

        # Walk through workspace
        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)

            # Skip certain directories
            if any(
                skip in root_path.parts
                for skip in [
                    ".git",
                    "venv",
                    "__pycache__",
                    ".pytest_cache",
                    ".roo",
                    ".kilocode",
                ]
            ):
                continue

            metrics["total_directories"] += len(dirs)
            metrics["total_files"] += len(files)

            # Calculate directory depth
            depth = len(root_path.relative_to(self.workspace_root).parts)
            metrics["max_directory_depth"] = max(
                metrics["max_directory_depth"], depth
            )

            # Count file types
            for file in files:
                file_path = root_path / file

                if file.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
                    metrics["source_files"] += 1

                if file.startswith("test_") or file.endswith("_test.py"):
                    metrics["test_files"] += 1

        # Calculate log directory size
        log_dir = self.workspace_root / "logs"
        if log_dir.exists():
            log_size = sum(
                f.stat().st_size for f in log_dir.rglob("*") if f.is_file()
            )
            metrics["log_size_mb"] = log_size / (1024 * 1024)

        # Find duplicate files (simplified check by size and name)
        file_signatures = {}
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file():
                signature = (file_path.name, file_path.stat().st_size)
                if signature in file_signatures:
                    metrics["duplicate_files"] += 1
                else:
                    file_signatures[signature] = file_path

        return metrics

    def check_quality_thresholds(self, metrics: Dict) -> List[Dict]:
        """Check if metrics exceed quality thresholds"""
        thresholds = self.config["quality_thresholds"]
        violations = []

        threshold_checks = [
            (
                "root_files",
                "max_root_files",
                "Too many files in root directory",
            ),
            (
                "max_directory_depth",
                "max_directory_depth",
                "Directory structure too deep",
            ),
            (
                "duplicate_files",
                "max_duplicate_files",
                "Too many duplicate files",
            ),
            ("log_size_mb", "max_log_size_mb", "Log files too large"),
        ]

        for metric_key, threshold_key, message in threshold_checks:
            if metric_key in metrics and threshold_key in thresholds:
                if metrics[metric_key] > thresholds[threshold_key]:
                    violations.append(
                        {
                            "metric": metric_key,
                            "current": metrics[metric_key],
                            "threshold": thresholds[threshold_key],
                            "message": message,
                        }
                    )

        return violations

    def run_monthly_maintenance(self) -> Dict:
        """Execute monthly maintenance tasks"""
        self.logger.info("Starting monthly maintenance...")

        results = {"timestamp": datetime.now().isoformat(), "tasks": {}}

        # Dependency audit
        if self.config["monthly_tasks"]["dependency_audit"]["enabled"]:
            deps_result = self.audit_dependencies()
            results["tasks"]["dependency_audit"] = deps_result

        # Performance baseline
        if self.config["monthly_tasks"]["performance_baseline"]["enabled"]:
            perf_result = self.run_performance_baseline()
            results["tasks"]["performance_baseline"] = perf_result

        self.save_maintenance_report("monthly", results)
        return results

    def audit_dependencies(self) -> Dict:
        """Audit project dependencies for updates and security issues"""
        audit_stats = {
            "outdated_packages": [],
            "security_issues": [],
            "suggestions": [],
            "errors": [],
        }

        try:
            # Check for outdated packages
            result = subprocess.run(
                [
                    str(
                        self.workspace_root / "venv" / "Scripts" / "python.exe"
                    ),
                    "-m",
                    "pip",
                    "list",
                    "--outdated",
                ],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")[2:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            audit_stats["outdated_packages"].append(
                                {
                                    "package": parts[0],
                                    "current": parts[1],
                                    "latest": parts[2],
                                }
                            )

            # Security audit (if safety is available)
            try:
                result = subprocess.run(
                    [
                        str(
                            self.workspace_root
                            / "venv"
                            / "Scripts"
                            / "python.exe"
                        ),
                        "-m",
                        "safety",
                        "check",
                    ],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0 and result.stdout:
                    audit_stats["security_issues"].append(result.stdout)

            except FileNotFoundError:
                audit_stats["suggestions"].append(
                    "Install 'safety' package for security auditing"
                )

        except Exception as e:
            audit_stats["errors"].append(f"Dependency audit failed: {str(e)}")

        return audit_stats

    def run_performance_baseline(self) -> Dict:
        """Run performance tests to establish baseline metrics"""
        perf_stats = {
            "test_results": {},
            "baseline_established": False,
            "errors": [],
        }

        test_suites = self.config["monthly_tasks"]["performance_baseline"][
            "test_suites"
        ]

        for suite in test_suites:
            try:
                start_time = datetime.now()

                result = subprocess.run(
                    [
                        str(
                            self.workspace_root
                            / "venv"
                            / "Scripts"
                            / "python.exe"
                        ),
                        "-m",
                        "pytest",
                        f"tests/{suite}/",
                        "--tb=short",
                    ],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                )

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                perf_stats["test_results"][suite] = {
                    "duration_seconds": duration,
                    "exit_code": result.returncode,
                    "passed": result.returncode == 0,
                }

                if result.returncode == 0:
                    perf_stats["baseline_established"] = True

            except Exception as e:
                perf_stats["errors"].append(f"{suite}: {str(e)}")

        return perf_stats

    def save_maintenance_report(self, report_type: str, results: Dict):
        """Save maintenance report to file"""
        reports_dir = self.workspace_root / "reports" / "maintenance"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = (
            reports_dir / f"{report_type}_maintenance_{timestamp}.json"
        )

        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Maintenance report saved: {report_file}")

    def generate_maintenance_summary(self) -> str:
        """Generate summary of all maintenance activities"""
        reports_dir = self.workspace_root / "reports" / "maintenance"

        if not reports_dir.exists():
            return "No maintenance reports found."

        summary = "# Workspace Maintenance Summary\n\n"

        # Get recent reports
        report_files = sorted(reports_dir.glob("*.json"), reverse=True)[:10]

        for report_file in report_files:
            try:
                with open(report_file, "r") as f:
                    report = json.load(f)

                report_type = report_file.name.split("_")[0]
                timestamp = report.get("timestamp", "Unknown")

                summary += (
                    f"## {report_type.title()} Maintenance - {timestamp}\n\n"
                )

                # Summarize tasks
                for task_name, task_result in report.get("tasks", {}).items():
                    summary += f"### {task_name}\n"

                    if isinstance(task_result, dict):
                        for key, value in task_result.items():
                            if isinstance(value, (int, float)):
                                summary += f"- {key}: {value}\n"
                            elif isinstance(value, list) and len(value) > 0:
                                summary += f"- {key}: {len(value)} items\n"

                    summary += "\n"

                # Include threshold violations
                violations = report.get("threshold_violations", [])
                if violations:
                    summary += "### Quality Threshold Violations\n"
                    for violation in violations:
                        summary += f"- {violation.get('message', 'Unknown')}: {violation.get('current', 'N/A')}\n"
                    summary += "\n"

            except Exception as e:
                summary += f"Error reading report {report_file.name}: {e}\n\n"

        return summary


def main():
    """Main CLI interface for workspace maintenance"""
    import argparse

    parser = argparse.ArgumentParser(description="Workspace Maintenance Tool")
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument(
        "--daily", action="store_true", help="Run daily maintenance"
    )
    parser.add_argument(
        "--weekly", action="store_true", help="Run weekly maintenance"
    )
    parser.add_argument(
        "--monthly", action="store_true", help="Run monthly maintenance"
    )
    parser.add_argument(
        "--metrics", action="store_true", help="Show current metrics"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Generate maintenance summary"
    )

    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    maintenance = WorkspaceMaintenance(workspace_root)

    if args.daily:
        results = maintenance.run_daily_maintenance()
        print("Daily maintenance completed:")
        print(
            f"  Files cleaned: {results['tasks'].get('temp_cleanup', {}).get('files_removed', 0)}"
        )
        print(
            f"  Logs rotated: {results['tasks'].get('log_rotation', {}).get('files_rotated', 0)}"
        )

        if results.get("threshold_violations"):
            print("\nQuality threshold violations:")
            for violation in results["threshold_violations"]:
                print(f"  ⚠️ {violation['message']}")

    elif args.weekly:
        results = maintenance.run_weekly_maintenance()
        print("Weekly maintenance completed:")
        print(
            f"  Branches archived: {results['tasks'].get('branch_cleanup', {}).get('branches_archived', 0)}"
        )
        print(
            f"  Docs checked: {results['tasks'].get('documentation_check', {}).get('files_checked', 0)}"
        )

    elif args.monthly:
        results = maintenance.run_monthly_maintenance()
        print("Monthly maintenance completed:")
        print(
            f"  Outdated packages: {len(results['tasks'].get('dependency_audit', {}).get('outdated_packages', []))}"
        )
        print(
            f"  Performance tests: {'✅' if results['tasks'].get('performance_baseline', {}).get('baseline_established') else '❌'}"
        )

    elif args.metrics:
        metrics = maintenance.calculate_workspace_metrics()
        print("Current workspace metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

        violations = maintenance.check_quality_thresholds(metrics)
        if violations:
            print("\nQuality threshold violations:")
            for violation in violations:
                print(f"  ⚠️ {violation['message']}: {violation['current']}")

    elif args.summary:
        summary = maintenance.generate_maintenance_summary()
        print(summary)

    else:
        print("Workspace Maintenance Tool")
        print("Use --help to see available commands")
        print("\nExample usage:")
        print("  --daily     # Run daily maintenance tasks")
        print("  --weekly    # Run weekly maintenance tasks")
        print("  --monthly   # Run monthly maintenance tasks")
        print("  --metrics   # Show current workspace metrics")


if __name__ == "__main__":
    main()
