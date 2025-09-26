#!/usr/bin/env python3
"""
Master Cleanup Orchestrator
Coordinates the complete workspace cleanup process with all safety measures
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Import our cleanup modules
sys.path.append(str(Path(__file__).parent))
from archive_recovery import ArchiveRecoveryTool
from documentation_updater import DocumentationUpdater
from pre_beta_cleanup import PreBetaCleanup
from team_coordinator import TeamCoordinator
from workspace_maintenance import WorkspaceMaintenance


class CleanupOrchestrator:
    """Master orchestrator for complete workspace cleanup process"""

    def __init__(self, workspace_root: str, dry_run: bool = True):
        self.workspace_root = Path(workspace_root)
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.setup_logging()
        self.initialize_components()

    def setup_logging(self):
        """Setup comprehensive logging for orchestration"""
        log_dir = self.workspace_root / "logs" / "cleanup"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"cleanup-orchestrator-{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def initialize_components(self):
        """Initialize all cleanup components"""
        self.logger.info("Initializing cleanup components...")

        self.cleanup_engine = PreBetaCleanup(self.workspace_root, self.dry_run)
        self.recovery_tool = ArchiveRecoveryTool(self.workspace_root)
        self.doc_updater = DocumentationUpdater(self.workspace_root)
        self.team_coordinator = TeamCoordinator(self.workspace_root)
        self.maintenance = WorkspaceMaintenance(self.workspace_root)

    def run_pre_cleanup_phase(self) -> Dict:
        """Execute pre-cleanup preparation phase"""
        self.logger.info("=== PRE-CLEANUP PHASE ===")

        phase_results = {
            "phase": "pre_cleanup",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
        }

        # Step 1: Analyze current workspace
        self.logger.info("Step 1: Analyzing workspace...")
        analysis = self.cleanup_engine.analyze_workspace()
        phase_results["steps"]["analysis"] = {
            "success": True,
            "migration_artifacts": len(
                analysis.get("migration_artifacts", [])
            ),
            "debug_artifacts": len(analysis.get("debug_artifacts", [])),
            "legacy_backups": len(analysis.get("legacy_backups", [])),
        }

        # Step 2: Create safety backup
        self.logger.info("Step 2: Creating safety backup...")
        backup_success = self.cleanup_engine.create_safety_backup()
        phase_results["steps"]["backup"] = {
            "success": backup_success,
            "backup_tag": (
                f"pre-cleanup-backup-{self.timestamp}"
                if backup_success
                else None
            ),
        }

        if not backup_success and not self.dry_run:
            self.logger.error("Safety backup failed! Aborting cleanup.")
            phase_results["abort_reason"] = "Safety backup failed"
            return phase_results

        # Step 3: Team notification
        self.logger.info("Step 3: Sending team notifications...")
        cleanup_plan = {
            "migration_count": phase_results["steps"]["analysis"][
                "migration_artifacts"
            ],
            "debug_count": phase_results["steps"]["analysis"][
                "debug_artifacts"
            ],
            "backup_count": phase_results["steps"]["analysis"][
                "legacy_backups"
            ],
            "plan_url": "COMPREHENSIVE_WORKSPACE_ORGANIZATION_STRATEGY.md",
        }

        notification_result = (
            self.team_coordinator.send_pre_cleanup_notification(cleanup_plan)
        )
        phase_results["steps"]["notification"] = notification_result

        # Step 4: Generate team checklists
        self.logger.info("Step 4: Generating team checklists...")
        checklists = self.team_coordinator.generate_team_checklist()
        phase_results["steps"]["checklists"] = {
            "success": len(checklists) > 0,
            "files_created": list(checklists.values()),
        }

        self.logger.info("Pre-cleanup phase completed!")
        return phase_results

    def run_cleanup_phase(self) -> Dict:
        """Execute main cleanup phase"""
        self.logger.info("=== MAIN CLEANUP PHASE ===")

        phase_results = {
            "phase": "cleanup",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
        }

        # Step 1: Execute main cleanup
        self.logger.info("Step 1: Executing workspace cleanup...")
        cleanup_result = self.cleanup_engine.run_cleanup()
        phase_results["steps"]["cleanup"] = cleanup_result

        if not cleanup_result.get("success"):
            self.logger.error("Main cleanup failed!")
            # Send emergency notification
            self.team_coordinator.send_emergency_notification(
                f"Cleanup failed: {cleanup_result.get('error', 'Unknown error')}"
            )
            return phase_results

        # Step 2: Progress updates (simulate)
        progress_updates = [
            {"phase": "Migration cleanup", "percentage": 33},
            {"phase": "Debug script cleanup", "percentage": 66},
            {"phase": "Legacy backup cleanup", "percentage": 100},
        ]

        for progress in progress_updates:
            self.team_coordinator.send_cleanup_progress_update(progress)

        self.logger.info("Main cleanup phase completed!")
        return phase_results

    def run_post_cleanup_phase(self, cleanup_result: Dict) -> Dict:
        """Execute post-cleanup finalization phase"""
        self.logger.info("=== POST-CLEANUP PHASE ===")

        phase_results = {
            "phase": "post_cleanup",
            "timestamp": datetime.now().isoformat(),
            "steps": {},
        }

        # Step 1: Update documentation
        self.logger.info("Step 1: Updating documentation...")
        doc_result = self.doc_updater.run_full_update(
            cleanup_result.get("report", {}), self.dry_run
        )
        phase_results["steps"]["documentation"] = doc_result

        # Step 2: Generate cleanup summary
        self.logger.info("Step 2: Generating cleanup summary...")
        summary_result = self.doc_updater.generate_cleanup_summary(
            cleanup_result.get("report", {}), self.dry_run
        )
        phase_results["steps"]["summary"] = summary_result

        # Step 3: Create status dashboard
        self.logger.info("Step 3: Creating status dashboard...")
        dashboard_status = {
            "phase": "Completed",
            "percentage": 100,
            "active": False,
            "total_processed": cleanup_result.get("archived_files", 0),
            "archive_size": "Calculating...",
            "start_time": self.timestamp,
        }
        dashboard_file = self.team_coordinator.create_cleanup_dashboard(
            dashboard_status
        )
        phase_results["steps"]["dashboard"] = {
            "success": True,
            "file": dashboard_file,
        }

        # Step 4: Final validation
        self.logger.info("Step 4: Running final validation...")
        validation = cleanup_result.get("validation", {})
        phase_results["steps"]["validation"] = validation

        # Step 5: Send completion notification
        self.logger.info("Step 5: Sending completion notification...")
        completion_result = (
            self.team_coordinator.send_cleanup_completion_notification(
                cleanup_result.get("report", {})
            )
        )
        phase_results["steps"]["completion_notification"] = completion_result

        self.logger.info("Post-cleanup phase completed!")
        return phase_results

    def run_complete_cleanup(self) -> Dict:
        """Execute complete cleanup process with all phases"""
        self.logger.info("🚀 Starting complete workspace cleanup process...")
        self.logger.info(
            f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}"
        )
        self.logger.info(f"Workspace: {self.workspace_root}")

        complete_results = {
            "orchestrator_version": "1.0",
            "start_time": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "workspace": str(self.workspace_root),
            "phases": {},
        }

        try:
            # Phase 1: Pre-cleanup preparation
            pre_cleanup_result = self.run_pre_cleanup_phase()
            complete_results["phases"]["pre_cleanup"] = pre_cleanup_result

            if pre_cleanup_result.get("abort_reason"):
                complete_results["status"] = "aborted"
                complete_results["abort_reason"] = pre_cleanup_result[
                    "abort_reason"
                ]
                return complete_results

            # Phase 2: Main cleanup execution
            cleanup_result = self.run_cleanup_phase()
            complete_results["phases"]["cleanup"] = cleanup_result

            if (
                not cleanup_result.get("steps", {})
                .get("cleanup", {})
                .get("success")
            ):
                complete_results["status"] = "failed"
                complete_results["error"] = "Main cleanup phase failed"
                return complete_results

            # Phase 3: Post-cleanup finalization
            post_cleanup_result = self.run_post_cleanup_phase(
                cleanup_result["steps"]["cleanup"]
            )
            complete_results["phases"]["post_cleanup"] = post_cleanup_result

            # Success!
            complete_results["status"] = "completed"
            complete_results["end_time"] = datetime.now().isoformat()

        except Exception as e:
            self.logger.error(f"Cleanup orchestration failed: {e}")
            complete_results["status"] = "error"
            complete_results["error"] = str(e)

            # Send emergency notification
            try:
                self.team_coordinator.send_emergency_notification(
                    f"Cleanup orchestration failed: {e}", "critical"
                )
            except Exception:
                pass  # Don't let notification failure block error reporting

        finally:
            # Save complete results
            self.save_orchestration_results(complete_results)

        return complete_results

    def save_orchestration_results(self, results: Dict):
        """Save complete orchestration results"""
        results_dir = self.workspace_root / "reports" / "cleanup"
        results_dir.mkdir(parents=True, exist_ok=True)

        results_file = (
            results_dir / f"cleanup-orchestration-{self.timestamp}.json"
        )

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Orchestration results saved: {results_file}")

    def print_cleanup_summary(self, results: Dict):
        """Print human-readable cleanup summary"""
        print("\n" + "=" * 80)
        print("🧹 WORKSPACE CLEANUP ORCHESTRATION SUMMARY")
        print("=" * 80)

        print(f"Status: {results.get('status', 'unknown').upper()}")
        print(
            f"Mode: {'DRY RUN' if results.get('dry_run') else 'LIVE EXECUTION'}"
        )
        print(f"Workspace: {results.get('workspace', 'unknown')}")
        print(f"Duration: {self.calculate_duration(results)}")

        if results.get("status") == "completed":
            cleanup_phase = results.get("phases", {}).get("cleanup", {})
            cleanup_steps = cleanup_phase.get("steps", {}).get("cleanup", {})

            if cleanup_steps:
                print(f"\n📊 CLEANUP STATISTICS:")
                print(
                    f"   Files archived: {cleanup_steps.get('archived_files', 0)}"
                )

                report = cleanup_steps.get("report", {}).get("summary", {})
                print(
                    f"   Migration artifacts: {report.get('migration_artifacts', 0)}"
                )
                print(
                    f"   Debug artifacts: {report.get('debug_artifacts', 0)}"
                )
                print(f"   Legacy backups: {report.get('legacy_backups', 0)}")

        # Show validation results
        validation = (
            results.get("phases", {})
            .get("post_cleanup", {})
            .get("steps", {})
            .get("validation", {})
        )
        if validation:
            print(f"\n🔍 VALIDATION RESULTS:")
            print(
                f"   Critical files: {'✅' if validation.get('critical_files_present') else '❌'}"
            )
            print(
                f"   Application imports: {'✅' if validation.get('application_imports') else '❌'}"
            )
            print(
                f"   Configuration loads: {'✅' if validation.get('configuration_loads') else '❌'}"
            )

        # Show errors/issues
        if results.get("status") in ["failed", "error", "aborted"]:
            print(f"\n❌ ISSUES:")
            if results.get("abort_reason"):
                print(f"   Aborted: {results['abort_reason']}")
            if results.get("error"):
                print(f"   Error: {results['error']}")

        # Next steps
        print(f"\n🔧 NEXT STEPS:")
        if results.get("status") == "completed":
            print("   1. Run comprehensive test suite")
            print("   2. Validate application functionality")
            print("   3. Review team checklists")
            print("   4. Monitor for issues over next 48 hours")
        else:
            print("   1. Check logs for detailed error information")
            print("   2. Use recovery tools if needed")
            print("   3. Contact technical team")

        print("\n" + "=" * 80)

    def calculate_duration(self, results: Dict) -> str:
        """Calculate cleanup duration"""
        try:
            start = datetime.fromisoformat(results.get("start_time", ""))
            end = datetime.fromisoformat(
                results.get("end_time", datetime.now().isoformat())
            )
            duration = end - start

            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            return f"{minutes}m {seconds}s"
        except Exception:
            return "Unknown"


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workspace Cleanup Orchestrator"
    )
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument(
        "--live-run",
        action="store_true",
        help="Execute actual cleanup (default is dry run)",
    )
    parser.add_argument(
        "--phase",
        choices=["pre", "cleanup", "post", "all"],
        default="all",
        help="Execute specific phase only",
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

    print("🧹 WORKSPACE CLEANUP ORCHESTRATOR")
    print("=" * 50)
    print(f"Workspace: {workspace_root}")
    print(
        f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE RUN (files will be moved/deleted)'}"
    )
    print(f"Phase: {args.phase}")
    print()

    if not dry_run:
        print("⚠️  WARNING: This will make actual changes to your workspace!")
        print("   - Files will be archived and removed")
        print("   - Directory structure will be modified")
        print("   - Git history will be modified")
        print()

        confirmation = input(
            "Are you absolutely sure you want to proceed? (type 'YES' to continue): "
        )
        if confirmation != "YES":
            print("Cleanup cancelled.")
            return 1

    # Execute cleanup
    orchestrator = CleanupOrchestrator(workspace_root, dry_run)

    try:
        if args.phase == "all":
            results = orchestrator.run_complete_cleanup()
        elif args.phase == "pre":
            results = orchestrator.run_pre_cleanup_phase()
        elif args.phase == "cleanup":
            results = orchestrator.run_cleanup_phase()
        elif args.phase == "post":
            # For post phase, we need cleanup results
            print(
                "Post-cleanup phase requires cleanup results. Running complete process..."
            )
            results = orchestrator.run_complete_cleanup()

        # Print summary
        orchestrator.print_cleanup_summary(results)

        # Return appropriate exit code
        if results.get("status") in ["completed", "success"]:
            if dry_run:
                print("\n✅ Dry run completed successfully!")
                print("   Use --live-run to execute actual cleanup.")
            else:
                print("\n✅ Cleanup completed successfully!")
            return 0
        else:
            print("\n❌ Cleanup failed or was aborted.")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Cleanup interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
