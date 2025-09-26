#!/usr/bin/env python3
"""
Team Coordination Tool
Manages team communication and coordination during workspace cleanup
"""

import json
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional


class TeamCoordinator:
    """Manages team coordination during workspace cleanup"""

    def __init__(self, workspace_root: str, config_file: Optional[str] = None):
        self.workspace_root = Path(workspace_root)
        self.config_file = config_file or (
            self.workspace_root / "config" / "team-coordination.json"
        )

        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        """Setup logging for coordination activities"""
        log_dir = self.workspace_root / "logs"
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"team-coordination-{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load team coordination configuration"""
        default_config = {
            "team_members": [
                {
                    "name": "Project Lead",
                    "email": "lead@company.com",
                    "role": "project_lead",
                    "notifications": ["all"],
                },
                {
                    "name": "Tech Lead",
                    "email": "tech@company.com",
                    "role": "tech_lead",
                    "notifications": ["technical", "issues"],
                },
                {
                    "name": "QA Lead",
                    "email": "qa@company.com",
                    "role": "qa_lead",
                    "notifications": ["testing", "validation"],
                },
            ],
            "notification_settings": {
                "pre_cleanup": {"lead_time_hours": 48},
                "during_cleanup": {"update_interval_minutes": 30},
                "post_cleanup": {"summary_delay_hours": 2},
            },
            "communication_channels": {
                "email": {"enabled": False, "smtp_config": {}},
                "slack": {"enabled": False, "webhook": ""},
                "teams": {"enabled": False, "webhook": ""},
            },
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.warning(
                    f"Failed to load config, using defaults: {e}"
                )
                self.config = default_config
        else:
            self.config = default_config
            # Create config file for future use
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)

    def get_team_members_by_role(self, roles: List[str]) -> List[Dict]:
        """Get team members with specific roles"""
        return [
            member
            for member in self.config["team_members"]
            if member["role"] in roles
        ]

    def get_notification_recipients(
        self, notification_type: str
    ) -> List[Dict]:
        """Get recipients for specific notification type"""
        recipients = []
        for member in self.config["team_members"]:
            notifications = member.get("notifications", [])
            if "all" in notifications or notification_type in notifications:
                recipients.append(member)
        return recipients

    def send_pre_cleanup_notification(self, cleanup_plan: Dict) -> Dict:
        """Send pre-cleanup notification to team"""
        self.logger.info("Sending pre-cleanup notification...")

        recipients = self.get_notification_recipients("pre_cleanup")

        # Calculate cleanup schedule
        cleanup_start = datetime.now() + timedelta(hours=48)
        cleanup_end = cleanup_start + timedelta(hours=8)

        message_content = f"""
🚀 WORKSPACE CLEANUP NOTIFICATION

Team,

We will begin comprehensive workspace cleanup for pre-beta preparation:

📅 SCHEDULE:
   Start: {cleanup_start.strftime('%Y-%m-%d %H:%M')}
   End:   {cleanup_end.strftime('%Y-%m-%d %H:%M')} (estimated)

🎯 OBJECTIVES:
   • Remove obsolete migration artifacts ({cleanup_plan.get('migration_count', 0)} files)
   • Archive debug scripts ({cleanup_plan.get('debug_count', 0)} files) 
   • Consolidate legacy backups ({cleanup_plan.get('backup_count', 0)} items)
   • Update documentation structure

⚠️ REQUIRED ACTIONS (by {(cleanup_start - timedelta(hours=24)).strftime('%Y-%m-%d')}):
   1. Commit all pending work
   2. Update local repositories: `git pull origin master`
   3. Backup personal configurations
   4. Review cleanup plan: {cleanup_plan.get('plan_url', 'See shared documentation')}

🔄 BACKUP & RECOVERY:
   • Complete git backup will be created
   • Individual file recovery available
   • Full rollback capability maintained

📞 SUPPORT:
   • Primary: {self.get_team_members_by_role(['tech_lead'])[0]['name'] if self.get_team_members_by_role(['tech_lead']) else 'Tech Lead'}
   • Secondary: {self.get_team_members_by_role(['project_lead'])[0]['name'] if self.get_team_members_by_role(['project_lead']) else 'Project Lead'}

Questions? Reply to this message or contact the tech lead directly.

Best regards,
Workspace Cleanup Automation
"""

        results = {
            "sent_count": 0,
            "failed_count": 0,
            "recipients": [r["name"] for r in recipients],
            "errors": [],
        }

        for recipient in recipients:
            try:
                if self.send_message(
                    recipient,
                    "Workspace Cleanup - Action Required",
                    message_content,
                ):
                    results["sent_count"] += 1
                else:
                    results["failed_count"] += 1
            except Exception as e:
                results["failed_count"] += 1
                results["errors"].append(f"{recipient['name']}: {str(e)}")

        return results

    def send_cleanup_progress_update(self, progress: Dict) -> Dict:
        """Send progress update during cleanup"""
        recipients = self.get_notification_recipients("progress")

        message_content = f"""
🔄 CLEANUP PROGRESS UPDATE

Current Status: {progress.get('phase', 'Unknown')}
Progress: {progress.get('percentage', 0)}% complete

Completed:
• Migration artifacts: {progress.get('migration_completed', 0)}/{progress.get('migration_total', 0)}
• Debug scripts: {progress.get('debug_completed', 0)}/{progress.get('debug_total', 0)}  
• Legacy backups: {progress.get('backup_completed', 0)}/{progress.get('backup_total', 0)}

Next: {progress.get('next_phase', 'Finalizing')}
ETA: {progress.get('eta', 'Unknown')}

All systems operational. No intervention required.
"""

        results = {"sent_count": 0, "failed_count": 0}

        for recipient in recipients:
            try:
                if self.send_message(
                    recipient, "Cleanup Progress Update", message_content
                ):
                    results["sent_count"] += 1
                else:
                    results["failed_count"] += 1
            except Exception as e:
                results["failed_count"] += 1

        return results

    def send_cleanup_completion_notification(self, results: Dict) -> Dict:
        """Send cleanup completion notification"""
        recipients = self.get_notification_recipients("completion")

        validation_status = (
            "✅ PASSED"
            if all(results.get("validation", {}).values())
            else "⚠️  ISSUES FOUND"
        )

        message_content = f"""
✅ WORKSPACE CLEANUP COMPLETED

Cleanup Summary:
• Files archived: {results.get('total_files_archived', 0)}
• Archive location: {results.get('archive_location', 'archive/')}
• Validation: {validation_status}

📊 BREAKDOWN:
• Migration artifacts: {results.get('migration_artifacts', 0)} files
• Debug scripts: {results.get('debug_artifacts', 0)} files  
• Legacy backups: {results.get('legacy_backups', 0)} items

🔍 VALIDATION RESULTS:
• Critical files: {'✅' if results.get('validation', {}).get('critical_files_present') else '❌'}
• Application imports: {'✅' if results.get('validation', {}).get('application_imports') else '❌'}
• Configuration loads: {'✅' if results.get('validation', {}).get('configuration_loads') else '❌'}
"""

        if results.get("validation", {}).get("issues"):
            message_content += "\n⚠️ ISSUES REQUIRING ATTENTION:\n"
            for issue in results["validation"]["issues"]:
                message_content += f"   • {issue}\n"

        message_content += f"""

🔧 IMMEDIATE ACTIONS NEEDED:
1. Run test suite: `python -m pytest tests/ -v`
2. Validate application: `python src/rfu/main.py --test-mode`
3. Update local repositories: `git pull origin master`

💾 RECOVERY INFORMATION:
• Backup tag: {results.get('backup_tag', 'N/A')}
• Recovery tool: `python scripts/workspace-cleanup/archive_recovery.py --help`
• Emergency contact: {self.get_team_members_by_role(['tech_lead'])[0]['name'] if self.get_team_members_by_role(['tech_lead']) else 'Tech Lead'}

The workspace is now ready for pre-beta testing activities!
"""

        notification_results = {"sent_count": 0, "failed_count": 0}

        for recipient in recipients:
            try:
                if self.send_message(
                    recipient, "✅ Workspace Cleanup Complete", message_content
                ):
                    notification_results["sent_count"] += 1
                else:
                    notification_results["failed_count"] += 1
            except Exception as e:
                notification_results["failed_count"] += 1

        return notification_results

    def send_emergency_notification(
        self, issue: str, severity: str = "high"
    ) -> Dict:
        """Send emergency notification for critical issues"""
        recipients = self.get_notification_recipients("emergency")
        if not recipients:
            recipients = self.config["team_members"]  # Send to everyone

        severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "ℹ️"}

        message_content = f"""
{severity_emoji.get(severity, '⚠️')} CLEANUP EMERGENCY NOTIFICATION

ISSUE: {issue}
SEVERITY: {severity.upper()}
TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This requires immediate attention. Please check the cleanup logs and take appropriate action.

Recovery options:
1. Individual file recovery: `python scripts/workspace-cleanup/archive_recovery.py`
2. Complete rollback: `git reset --hard pre-cleanup-backup-<timestamp>`
3. Contact tech lead immediately

Logs location: logs/workspace-cleanup-*.log
"""

        results = {"sent_count": 0, "failed_count": 0}

        for recipient in recipients:
            try:
                if self.send_message(
                    recipient,
                    f"🚨 EMERGENCY: Cleanup Issue ({severity})",
                    message_content,
                ):
                    results["sent_count"] += 1
                else:
                    results["failed_count"] += 1
            except Exception as e:
                results["failed_count"] += 1

        return results

    def send_message(
        self, recipient: Dict, subject: str, content: str
    ) -> bool:
        """Send message via configured channels"""

        # For this implementation, we'll log the message
        # In production, you'd implement actual email/Slack/Teams sending

        self.logger.info(
            f"MESSAGE TO {recipient['name']} ({recipient['email']}):"
        )
        self.logger.info(f"SUBJECT: {subject}")
        self.logger.info(f"CONTENT:\n{content}")
        self.logger.info("-" * 80)

        # Save to file for manual sending if needed
        messages_dir = self.workspace_root / "logs" / "team-messages"
        messages_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_file = (
            messages_dir
            / f"message_{timestamp}_{recipient['name'].replace(' ', '_')}.txt"
        )

        with open(message_file, "w") as f:
            f.write(f"TO: {recipient['name']} <{recipient['email']}>\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write(f"DATE: {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            f.write(content)

        return True  # Assume success for logging-based implementation

    def create_cleanup_dashboard(self, status: Dict) -> str:
        """Create HTML dashboard for cleanup status"""

        dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Workspace Cleanup Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .status {{ padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .active {{ background-color: #e3f2fd; border: 2px solid #2196f3; }}
        .completed {{ background-color: #e8f5e8; border: 2px solid #4caf50; }}
        .pending {{ background-color: #fff3e0; border: 2px solid #ff9800; }}
        .progress {{ width: 100%; background-color: #f0f0f0; border-radius: 4px; }}
        .progress-bar {{ height: 20px; background-color: #4caf50; border-radius: 4px; }}
    </style>
    <script>
        function refreshPage() {{ location.reload(); }}
        setTimeout(refreshPage, 30000); // Auto-refresh every 30 seconds
    </script>
</head>
<body>
    <h1>🧹 Workspace Cleanup Dashboard</h1>
    
    <div class="status {'active' if status.get('active') else 'completed'}">
        <h2>Overall Status: {status.get('phase', 'Unknown')}</h2>
        <div class="progress">
            <div class="progress-bar" style="width: {status.get('percentage', 0)}%"></div>
        </div>
        <p>{status.get('percentage', 0)}% Complete</p>
    </div>
    
    <div class="status completed">
        <h3>✅ Migration Artifacts</h3>
        <p>Processed: {status.get('migration_completed', 0)}/{status.get('migration_total', 0)}</p>
    </div>
    
    <div class="status {'active' if status.get('current_phase') == 'debug' else 'completed'}">
        <h3>🔧 Debug Scripts</h3>
        <p>Processed: {status.get('debug_completed', 0)}/{status.get('debug_total', 0)}</p>
    </div>
    
    <div class="status {'active' if status.get('current_phase') == 'backup' else 'pending'}">
        <h3>💾 Legacy Backups</h3>
        <p>Processed: {status.get('backup_completed', 0)}/{status.get('backup_total', 0)}</p>
    </div>
    
    <div class="status">
        <h3>📊 Statistics</h3>
        <ul>
            <li>Total Files Processed: {status.get('total_processed', 0)}</li>
            <li>Archive Size: {status.get('archive_size', '0 MB')}</li>
            <li>Start Time: {status.get('start_time', 'Unknown')}</li>
            <li>ETA: {status.get('eta', 'Calculating...')}</li>
        </ul>
    </div>
    
    <div class="status">
        <h3>🔗 Quick Actions</h3>
        <ul>
            <li><a href="logs/">View Logs</a></li>
            <li><a href="archive/">Browse Archive</a></li>
            <li><a href="mailto:tech@company.com">Contact Tech Lead</a></li>
        </ul>
    </div>
    
    <p><em>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    <p><em>Auto-refresh in 30 seconds</em></p>
</body>
</html>
"""

        dashboard_file = self.workspace_root / "cleanup-dashboard.html"
        with open(dashboard_file, "w") as f:
            f.write(dashboard_html)

        return str(dashboard_file)

    def generate_team_checklist(self) -> Dict:
        """Generate role-specific checklists for team members"""

        checklists = {
            "project_lead": [
                "Review and approve cleanup plan",
                "Ensure all team members are notified",
                "Monitor cleanup progress",
                "Validate completion results",
                "Authorize any rollback if needed",
            ],
            "tech_lead": [
                "Create comprehensive backup",
                "Execute cleanup procedures",
                "Monitor technical validation",
                "Resolve any technical issues",
                "Update architecture documentation",
            ],
            "qa_lead": [
                "Validate test suite preservation",
                "Execute post-cleanup testing",
                "Verify application functionality",
                "Document any issues found",
                "Approve pre-beta readiness",
            ],
            "developers": [
                "Commit all pending work",
                "Update local repositories",
                "Backup personal configurations",
                "Test application after cleanup",
                "Report any issues immediately",
            ],
        }

        # Save checklists to files
        checklist_dir = self.workspace_root / "checklists"
        checklist_dir.mkdir(exist_ok=True)

        saved_files = {}

        for role, items in checklists.items():
            checklist_content = f"# {role.title()} Cleanup Checklist\n\n"
            for i, item in enumerate(items, 1):
                checklist_content += f"- [ ] {item}\n"

            checklist_content += f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

            checklist_file = checklist_dir / f"{role}_checklist.md"
            with open(checklist_file, "w") as f:
                f.write(checklist_content)

            saved_files[role] = str(
                checklist_file.relative_to(self.workspace_root)
            )

        return saved_files


def main():
    """Main CLI interface for team coordination"""
    import argparse

    parser = argparse.ArgumentParser(description="Team Coordination Tool")
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--pre-cleanup",
        action="store_true",
        help="Send pre-cleanup notification",
    )
    parser.add_argument("--progress", help="Send progress update (JSON file)")
    parser.add_argument(
        "--completion", help="Send completion notification (JSON file)"
    )
    parser.add_argument("--emergency", help="Send emergency notification")
    parser.add_argument(
        "--dashboard", help="Create dashboard (JSON status file)"
    )
    parser.add_argument(
        "--checklists", action="store_true", help="Generate team checklists"
    )

    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    coordinator = TeamCoordinator(workspace_root, args.config)

    if args.pre_cleanup:
        # Mock cleanup plan for demo
        cleanup_plan = {
            "migration_count": 25,
            "debug_count": 15,
            "backup_count": 8,
            "plan_url": "COMPREHENSIVE_WORKSPACE_ORGANIZATION_STRATEGY.md",
        }

        result = coordinator.send_pre_cleanup_notification(cleanup_plan)
        print(
            f"Pre-cleanup notification sent to {result['sent_count']} recipients"
        )

    elif args.progress:
        try:
            with open(args.progress, "r") as f:
                progress = json.load(f)

            result = coordinator.send_cleanup_progress_update(progress)
            print(f"Progress update sent to {result['sent_count']} recipients")

        except Exception as e:
            print(f"Failed to send progress update: {e}")

    elif args.completion:
        try:
            with open(args.completion, "r") as f:
                results = json.load(f)

            result = coordinator.send_cleanup_completion_notification(results)
            print(
                f"Completion notification sent to {result['sent_count']} recipients"
            )

        except Exception as e:
            print(f"Failed to send completion notification: {e}")

    elif args.emergency:
        result = coordinator.send_emergency_notification(
            args.emergency, "high"
        )
        print(
            f"Emergency notification sent to {result['sent_count']} recipients"
        )

    elif args.dashboard:
        try:
            with open(args.dashboard, "r") as f:
                status = json.load(f)

            dashboard_file = coordinator.create_cleanup_dashboard(status)
            print(f"Dashboard created: {dashboard_file}")

        except Exception as e:
            print(f"Failed to create dashboard: {e}")

    elif args.checklists:
        checklists = coordinator.generate_team_checklist()
        print("Team checklists generated:")
        for role, file_path in checklists.items():
            print(f"  {role}: {file_path}")

    else:
        print("Team Coordination Tool")
        print("Use --help to see available commands")
        print("\nExample usage:")
        print(
            "  --pre-cleanup                 # Send pre-cleanup notification"
        )
        print("  --progress status.json        # Send progress update")
        print("  --completion results.json     # Send completion notification")
        print(
            "  --checklists                  # Generate role-specific checklists"
        )


if __name__ == "__main__":
    main()
