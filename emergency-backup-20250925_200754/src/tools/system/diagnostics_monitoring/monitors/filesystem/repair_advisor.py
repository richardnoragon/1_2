"""Intelligent file system repair recommendations."""

import os
import shutil
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum
from pathlib import Path

from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class RepairPriority(Enum):
    """Repair priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RepairAction(Enum):
    """Types of repair actions."""

    BACKUP_FILE = "backup_file"
    DELETE_FILE = "delete_file"
    RESTORE_PERMISSIONS = "restore_permissions"
    FIX_TIMESTAMPS = "fix_timestamps"
    REPAIR_SYMLINK = "repair_symlink"
    RUN_FSCK = "run_fsck"
    RUN_CHKDSK = "run_chkdsk"
    QUARANTINE_FILE = "quarantine_file"
    RECREATE_FILE = "recreate_file"
    MANUAL_INSPECTION = "manual_inspection"


class RepairAdvisor:
    """Intelligent file system repair advisor.

    Provides comprehensive repair recommendations including:
    - Automated repair suggestions
    - Risk assessment for repair actions
    - Platform-specific repair tools
    - Backup and recovery strategies
    - Step-by-step repair procedures
    """

    def __init__(self):
        """Initialize the repair advisor."""
        self.platform_detector = get_platform_detector()

        # Repair strategies by corruption type
        self.repair_strategies = {
            "checksum_mismatch": {
                "actions": [
                    RepairAction.BACKUP_FILE,
                    RepairAction.QUARANTINE_FILE,
                    RepairAction.MANUAL_INSPECTION,
                ],
                "priority": RepairPriority.HIGH,
                "risk_level": "medium",
                "description": "File content corruption detected",
            },
            "size_anomaly": {
                "actions": [
                    RepairAction.BACKUP_FILE,
                    RepairAction.DELETE_FILE,
                ],
                "priority": RepairPriority.MEDIUM,
                "risk_level": "low",
                "description": "Unusual file size detected",
            },
            "timestamp_anomaly": {
                "actions": [RepairAction.FIX_TIMESTAMPS],
                "priority": RepairPriority.LOW,
                "risk_level": "very_low",
                "description": "Invalid file timestamps",
            },
            "permission_corruption": {
                "actions": [RepairAction.RESTORE_PERMISSIONS],
                "priority": RepairPriority.MEDIUM,
                "risk_level": "low",
                "description": "Incorrect file permissions",
            },
            "symlink_corruption": {
                "actions": [
                    RepairAction.REPAIR_SYMLINK,
                    RepairAction.DELETE_FILE,
                ],
                "priority": RepairPriority.LOW,
                "risk_level": "very_low",
                "description": "Broken symbolic link",
            },
            "filesystem_inconsistency": {
                "actions": [RepairAction.RUN_FSCK, RepairAction.RUN_CHKDSK],
                "priority": RepairPriority.CRITICAL,
                "risk_level": "high",
                "description": "Filesystem structure corruption",
            },
        }

        # Platform-specific repair tools
        self.platform_tools = {
            "windows": {
                "filesystem_check": "chkdsk",
                "permission_fix": "icacls",
                "system_file_check": "sfc",
            },
            "macos": {
                "filesystem_check": "fsck",
                "permission_fix": "chmod",
                "disk_utility": "diskutil",
            },
            "linux": {
                "filesystem_check": "fsck",
                "permission_fix": "chmod",
                "ext_tools": "e2fsck",
            },
        }

    def analyze_issues(
        self, scan_results: Dict[str, Any], corruption_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze issues and generate repair recommendations.

        Args:
            scan_results: Results from filesystem scan
            corruption_analysis: Results from corruption analysis

        Returns:
            Dict containing repair recommendations
        """
        try:
            recommendations = {
                "timestamp": datetime.now().isoformat(),
                "recommendations": [],
                "summary": {
                    "total_issues": 0,
                    "critical_repairs": 0,
                    "high_priority": 0,
                    "medium_priority": 0,
                    "low_priority": 0,
                    "estimated_time": "0 minutes",
                    "risk_assessment": "low",
                },
                "repair_plan": {
                    "immediate_actions": [],
                    "scheduled_actions": [],
                    "manual_actions": [],
                },
                "backup_recommendations": [],
                "prevention_tips": [],
            }

            # Analyze corruptions and generate recommendations
            corruptions = corruption_analysis.get("corruptions", [])
            for corruption in corruptions:
                self._generate_corruption_recommendation(
                    corruption, recommendations
                )

            # Analyze scan errors
            errors = scan_results.get("errors", [])
            for error in errors:
                self._generate_error_recommendation(error, recommendations)

            # Generate summary and plan
            self._generate_repair_summary(recommendations)
            self._generate_repair_plan(recommendations)
            self._generate_backup_recommendations(
                scan_results, corruption_analysis, recommendations
            )
            self._generate_prevention_tips(recommendations)

            return recommendations

        except Exception as e:
            error_handler.handle_error(e, "RepairAdvisor.analyze_issues")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "recommendations": [],
            }

    def _generate_corruption_recommendation(
        self, corruption: Dict[str, Any], recommendations: Dict[str, Any]
    ) -> None:
        """Generate recommendation for a specific corruption.

        Args:
            corruption: Corruption information
            recommendations: Recommendations to update
        """
        corruption_type = corruption.get("type", "unknown")
        severity = corruption.get("severity", "low")
        path = corruption.get("path", "")
        description = corruption.get("description", "")

        # Get repair strategy
        strategy = self.repair_strategies.get(
            corruption_type,
            {
                "actions": [RepairAction.MANUAL_INSPECTION],
                "priority": RepairPriority.MEDIUM,
                "risk_level": "medium",
                "description": "Unknown corruption type",
            },
        )

        # Create recommendation
        recommendation = {
            "id": f"repair_{len(recommendations['recommendations']) + 1}",
            "corruption_type": corruption_type,
            "severity": severity,
            "priority": strategy["priority"].value,
            "risk_level": strategy["risk_level"],
            "path": path,
            "description": description,
            "strategy_description": strategy["description"],
            "recommended_actions": [
                action.value for action in strategy["actions"]
            ],
            "detailed_steps": self._generate_detailed_steps(
                corruption_type, path, strategy["actions"]
            ),
            "estimated_time": self._estimate_repair_time(strategy["actions"]),
            "backup_required": self._requires_backup(strategy["actions"]),
            "automation_possible": self._can_automate(strategy["actions"]),
            "platform_specific": self._get_platform_specific_advice(
                corruption_type, path
            ),
        }

        recommendations["recommendations"].append(recommendation)

    def _generate_error_recommendation(
        self, error: Dict[str, Any], recommendations: Dict[str, Any]
    ) -> None:
        """Generate recommendation for a scan error.

        Args:
            error: Error information
            recommendations: Recommendations to update
        """
        error_msg = error.get("error", "").lower()
        path = error.get("path", "")

        # Categorize error and suggest action
        if "permission" in error_msg:
            action = RepairAction.RESTORE_PERMISSIONS
            priority = RepairPriority.MEDIUM
            risk = "low"
        elif "not found" in error_msg or "no such file" in error_msg:
            action = RepairAction.DELETE_FILE
            priority = RepairPriority.LOW
            risk = "very_low"
        else:
            action = RepairAction.MANUAL_INSPECTION
            priority = RepairPriority.MEDIUM
            risk = "medium"

        recommendation = {
            "id": f"error_{len(recommendations['recommendations']) + 1}",
            "corruption_type": "scan_error",
            "severity": "medium",
            "priority": priority.value,
            "risk_level": risk,
            "path": path,
            "description": error.get("error", ""),
            "strategy_description": "Scan error resolution",
            "recommended_actions": [action.value],
            "detailed_steps": self._generate_detailed_steps(
                "scan_error", path, [action]
            ),
            "estimated_time": self._estimate_repair_time([action]),
            "backup_required": self._requires_backup([action]),
            "automation_possible": self._can_automate([action]),
            "platform_specific": self._get_platform_specific_advice(
                "scan_error", path
            ),
        }

        recommendations["recommendations"].append(recommendation)

    def _generate_detailed_steps(
        self, corruption_type: str, path: str, actions: List[RepairAction]
    ) -> List[str]:
        """Generate detailed repair steps.

        Args:
            corruption_type: Type of corruption
            path: Path to affected file/directory
            actions: Recommended actions

        Returns:
            List of detailed step descriptions
        """
        steps = []

        for action in actions:
            if action == RepairAction.BACKUP_FILE:
                steps.extend(
                    [
                        f"1. Create backup of {path}",
                        f"   cp '{path}' '{path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}'",
                        "2. Verify backup integrity",
                    ]
                )

            elif action == RepairAction.DELETE_FILE:
                steps.extend(
                    [
                        f"1. Confirm file is safe to delete: {path}",
                        f"2. Remove file: rm '{path}'",
                        "3. Verify removal completed successfully",
                    ]
                )

            elif action == RepairAction.RESTORE_PERMISSIONS:
                if self.platform_detector.is_windows():
                    steps.extend(
                        [
                            f"1. Reset permissions on {path}",
                            f"   icacls '{path}' /reset",
                            "2. Verify permissions are correct",
                        ]
                    )
                else:
                    steps.extend(
                        [
                            f"1. Fix permissions on {path}",
                            f"   chmod 644 '{path}' (for files)",
                            f"   chmod 755 '{path}' (for directories)",
                            "2. Verify permissions are correct",
                        ]
                    )

            elif action == RepairAction.FIX_TIMESTAMPS:
                steps.extend(
                    [
                        f"1. Update timestamps on {path}",
                        f"   touch '{path}'",
                        "2. Verify timestamps are reasonable",
                    ]
                )

            elif action == RepairAction.REPAIR_SYMLINK:
                steps.extend(
                    [
                        f"1. Check symlink target for {path}",
                        f"   ls -la '{path}'",
                        "2. Remove broken symlink if target doesn't exist",
                        f"   rm '{path}'",
                        "3. Recreate symlink if target is available",
                    ]
                )

            elif action == RepairAction.RUN_FSCK:
                if (
                    self.platform_detector.is_linux()
                    or self.platform_detector.is_macos()
                ):
                    steps.extend(
                        [
                            "1. Unmount filesystem (if possible)",
                            "2. Run filesystem check:",
                            "   fsck -f /dev/device",
                            "3. Review and apply suggested fixes",
                            "4. Remount filesystem",
                        ]
                    )

            elif action == RepairAction.RUN_CHKDSK:
                if self.platform_detector.is_windows():
                    steps.extend(
                        [
                            "1. Open Command Prompt as Administrator",
                            "2. Run disk check:",
                            "   chkdsk C: /f /r",
                            "3. Schedule check for next reboot if needed",
                            "4. Restart system to complete check",
                        ]
                    )

            elif action == RepairAction.QUARANTINE_FILE:
                quarantine_dir = self._get_quarantine_directory()
                steps.extend(
                    [
                        f"1. Create quarantine directory: {quarantine_dir}",
                        f"2. Move suspicious file to quarantine:",
                        f"   mv '{path}' '{quarantine_dir}/'",
                        "3. Document quarantine action",
                        "4. Schedule for further analysis",
                    ]
                )

            elif action == RepairAction.MANUAL_INSPECTION:
                steps.extend(
                    [
                        f"1. Manually inspect {path}",
                        "2. Determine if file is critical",
                        "3. Check for alternative sources",
                        "4. Decide on appropriate action",
                        "5. Document findings and actions taken",
                    ]
                )

        return steps

    def _estimate_repair_time(self, actions: List[RepairAction]) -> str:
        """Estimate time required for repair actions.

        Args:
            actions: List of repair actions

        Returns:
            Estimated time as string
        """
        time_estimates = {
            RepairAction.BACKUP_FILE: 2,
            RepairAction.DELETE_FILE: 1,
            RepairAction.RESTORE_PERMISSIONS: 1,
            RepairAction.FIX_TIMESTAMPS: 1,
            RepairAction.REPAIR_SYMLINK: 3,
            RepairAction.RUN_FSCK: 30,
            RepairAction.RUN_CHKDSK: 45,
            RepairAction.QUARANTINE_FILE: 2,
            RepairAction.RECREATE_FILE: 10,
            RepairAction.MANUAL_INSPECTION: 15,
        }

        total_minutes = sum(
            time_estimates.get(action, 5) for action in actions
        )

        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"

    def _requires_backup(self, actions: List[RepairAction]) -> bool:
        """Check if actions require backup.

        Args:
            actions: List of repair actions

        Returns:
            True if backup is required
        """
        risky_actions = {
            RepairAction.DELETE_FILE,
            RepairAction.RUN_FSCK,
            RepairAction.RUN_CHKDSK,
            RepairAction.RECREATE_FILE,
        }

        return any(action in risky_actions for action in actions)

    def _can_automate(self, actions: List[RepairAction]) -> bool:
        """Check if actions can be automated.

        Args:
            actions: List of repair actions

        Returns:
            True if actions can be automated
        """
        manual_actions = {
            RepairAction.MANUAL_INSPECTION,
            RepairAction.RUN_FSCK,
            RepairAction.RUN_CHKDSK,
        }

        return not any(action in manual_actions for action in actions)

    def _get_platform_specific_advice(
        self, corruption_type: str, path: str
    ) -> Dict[str, Any]:
        """Get platform-specific repair advice.

        Args:
            corruption_type: Type of corruption
            path: Path to affected item

        Returns:
            Platform-specific advice
        """
        advice = {"tools": [], "commands": [], "considerations": []}

        if self.platform_detector.is_windows():
            advice["tools"] = ["chkdsk", "sfc", "icacls"]
            if corruption_type == "filesystem_inconsistency":
                advice["commands"] = ["chkdsk C: /f /r", "sfc /scannow"]
                advice["considerations"] = [
                    "May require system restart",
                    "Run as Administrator",
                    "Schedule during maintenance window",
                ]

        elif self.platform_detector.is_macos():
            advice["tools"] = ["fsck", "diskutil", "chmod"]
            if corruption_type == "filesystem_inconsistency":
                advice["commands"] = [
                    "diskutil verifyVolume /",
                    "diskutil repairVolume /",
                ]
                advice["considerations"] = [
                    "May require single-user mode",
                    "Use Disk Utility GUI for safety",
                    "Consider Time Machine backup first",
                ]

        elif self.platform_detector.is_linux():
            advice["tools"] = ["fsck", "e2fsck", "chmod"]
            if corruption_type == "filesystem_inconsistency":
                advice["commands"] = [
                    "fsck -f /dev/device",
                    "e2fsck -f /dev/device",
                ]
                advice["considerations"] = [
                    "Unmount filesystem first",
                    "Use live CD/USB if root filesystem",
                    "Have backup available",
                ]

        return advice

    def _get_quarantine_directory(self) -> str:
        """Get platform-appropriate quarantine directory.

        Returns:
            Path to quarantine directory
        """
        if self.platform_detector.is_windows():
            return os.path.expandvars(r"%TEMP%\RFU_Quarantine")
        else:
            return os.path.expanduser("~/.rfu_quarantine")

    def _generate_repair_summary(
        self, recommendations: Dict[str, Any]
    ) -> None:
        """Generate repair summary statistics.

        Args:
            recommendations: Recommendations to update
        """
        recs = recommendations["recommendations"]
        summary = recommendations["summary"]

        summary["total_issues"] = len(recs)

        # Count by priority
        for rec in recs:
            priority = rec.get("priority", "low")
            if priority == "critical":
                summary["critical_repairs"] += 1
            elif priority == "high":
                summary["high_priority"] += 1
            elif priority == "medium":
                summary["medium_priority"] += 1
            else:
                summary["low_priority"] += 1

        # Estimate total time
        total_minutes = 0
        for rec in recs:
            time_str = rec.get("estimated_time", "0 minutes")
            if "h" in time_str:
                hours = int(time_str.split("h")[0])
                minutes = (
                    int(time_str.split("h")[1].split("m")[0])
                    if "m" in time_str
                    else 0
                )
                total_minutes += hours * 60 + minutes
            else:
                total_minutes += int(time_str.split(" ")[0])

        if total_minutes < 60:
            summary["estimated_time"] = f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            summary["estimated_time"] = f"{hours}h {minutes}m"

        # Assess overall risk
        risk_levels = [rec.get("risk_level", "low") for rec in recs]
        if "high" in risk_levels:
            summary["risk_assessment"] = "high"
        elif "medium" in risk_levels:
            summary["risk_assessment"] = "medium"
        else:
            summary["risk_assessment"] = "low"

    def _generate_repair_plan(self, recommendations: Dict[str, Any]) -> None:
        """Generate structured repair plan.

        Args:
            recommendations: Recommendations to update
        """
        recs = recommendations["recommendations"]
        plan = recommendations["repair_plan"]

        for rec in recs:
            priority = rec.get("priority", "low")
            automation = rec.get("automation_possible", False)

            if priority == "critical":
                plan["immediate_actions"].append(rec)
            elif automation:
                plan["scheduled_actions"].append(rec)
            else:
                plan["manual_actions"].append(rec)

    def _generate_backup_recommendations(
        self,
        scan_results: Dict[str, Any],
        corruption_analysis: Dict[str, Any],
        recommendations: Dict[str, Any],
    ) -> None:
        """Generate backup recommendations.

        Args:
            scan_results: Scan results
            corruption_analysis: Corruption analysis
            recommendations: Recommendations to update
        """
        backup_recs = []

        # Check corruption severity
        stats = corruption_analysis.get("statistics", {})
        critical_issues = stats.get("critical_issues", 0)
        high_severity = stats.get("high_severity", 0)

        if critical_issues > 0:
            backup_recs.append(
                "URGENT: Create full system backup before any repair attempts"
            )
        elif high_severity > 0:
            backup_recs.append("Create backup of affected files before repair")

        # General backup recommendations
        backup_recs.extend(
            [
                "Verify existing backups are current and accessible",
                "Test backup restoration process",
                "Consider incremental backup schedule",
                "Document backup locations and procedures",
            ]
        )

        recommendations["backup_recommendations"] = backup_recs

    def _generate_prevention_tips(
        self, recommendations: Dict[str, Any]
    ) -> None:
        """Generate prevention tips.

        Args:
            recommendations: Recommendations to update
        """
        tips = [
            "Schedule regular filesystem integrity checks",
            "Implement automated backup solutions",
            "Monitor disk health and replace aging drives",
            "Use UPS to prevent power-related corruption",
            "Keep filesystem drivers and OS updated",
            "Avoid forceful shutdowns when possible",
            "Monitor system logs for early warning signs",
            "Implement file integrity monitoring",
            "Use checksums for critical files",
            "Regular system maintenance and cleanup",
        ]

        # Add platform-specific tips
        if self.platform_detector.is_windows():
            tips.extend(
                [
                    "Run Windows Update regularly",
                    "Use Windows Defender or antivirus",
                    "Schedule chkdsk during maintenance windows",
                ]
            )
        elif self.platform_detector.is_linux():
            tips.extend(
                [
                    "Keep package manager updated",
                    "Monitor system logs with journalctl",
                    "Use SMART monitoring tools",
                ]
            )
        elif self.platform_detector.is_macos():
            tips.extend(
                [
                    "Use Time Machine for regular backups",
                    "Run First Aid in Disk Utility periodically",
                    "Keep macOS updated",
                ]
            )

        recommendations["prevention_tips"] = tips

    def get_repair_script(self, recommendation: Dict[str, Any]) -> str:
        """Generate automated repair script.

        Args:
            recommendation: Repair recommendation

        Returns:
            Repair script content
        """
        if not recommendation.get("automation_possible", False):
            return "# Manual intervention required - no script available"

        script_lines = [
            (
                "#!/bin/bash"
                if not self.platform_detector.is_windows()
                else "@echo off"
            ),
            f"# Automated repair script for {recommendation.get('path', 'unknown')}",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Corruption type: {recommendation.get('corruption_type', 'unknown')}",
            "",
            "# Safety check",
            "echo 'Starting automated repair...'",
            "",
        ]

        # Add detailed steps as script commands
        steps = recommendation.get("detailed_steps", [])
        for step in steps:
            if step.strip().startswith(
                ("cp ", "mv ", "rm ", "chmod ", "touch ")
            ):
                script_lines.append(step.strip())
            else:
                script_lines.append(f"# {step}")

        script_lines.extend(
            [
                "",
                "echo 'Repair completed.'",
                "echo 'Please verify results manually.'",
            ]
        )

        return "\n".join(script_lines)

    def update_strategies(self, new_strategies: Dict[str, Any]) -> None:
        """Update repair strategies.

        Args:
            new_strategies: New strategy definitions
        """
        self.repair_strategies.update(new_strategies)
