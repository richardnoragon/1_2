"""
Intelligent Software Updater for Software Maintenance Toolkit

This module provides comprehensive software update management including
automatic scanning, multi-source update checking, changelog retrieval,
selective updating with rollback capabilities, scheduling, and history logging.
"""

import json
import schedule
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..core.maintenance_base import MaintenanceToolBase
from ..core.software_detector import SoftwareDetector, SoftwareInfo
from ..core.update_sources import UpdateSourceManager, UpdateInfo
from ..core.security_manager import SecurityManager


@dataclass
class UpdateSession:
    """Data class representing an update session."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_updates: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    skipped_updates: int = 0
    updates_performed: List[str] = None

    def __post_init__(self):
        if self.updates_performed is None:
            self.updates_performed = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_updates": self.total_updates,
            "successful_updates": self.successful_updates,
            "failed_updates": self.failed_updates,
            "skipped_updates": self.skipped_updates,
            "updates_performed": self.updates_performed,
        }


@dataclass
class UpdateSchedule:
    """Data class representing an update schedule."""

    schedule_id: str
    name: str
    frequency: str  # 'daily', 'weekly', 'monthly'
    time: str  # HH:MM format
    enabled: bool = True
    include_security_only: bool = False
    auto_install: bool = False
    software_filter: List[str] = None

    def __post_init__(self):
        if self.software_filter is None:
            self.software_filter = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "schedule_id": self.schedule_id,
            "name": self.name,
            "frequency": self.frequency,
            "time": self.time,
            "enabled": self.enabled,
            "include_security_only": self.include_security_only,
            "auto_install": self.auto_install,
            "software_filter": self.software_filter,
        }


class SoftwareUpdater(MaintenanceToolBase):
    """
    Intelligent Software Updater providing comprehensive update management
    with automatic scanning, multi-source checking, and advanced features.
    """

    def __init__(self):
        super().__init__("Software Updater")

        # Initialize core components
        self.software_detector = SoftwareDetector()
        self.update_manager = UpdateSourceManager()
        self.security_manager = SecurityManager()

        # Update management
        self.detected_software: Dict[str, SoftwareInfo] = {}
        self.available_updates: Dict[str, UpdateInfo] = {}
        self.update_history: List[UpdateSession] = []
        self.update_schedules: Dict[str, UpdateSchedule] = {}

        # Settings
        self.auto_check_enabled = True
        self.check_interval_hours = 24
        self.auto_install_security = False
        self.create_restore_points = True
        self.backup_before_update = True

        # Scheduler
        self.scheduler_thread = None
        self.scheduler_running = False

        # Load configuration and history
        self._load_configuration()
        self._load_update_history()
        self._load_schedules()

        self.require_admin = True

    def _load_configuration(self):
        """Load updater configuration from file."""
        config_file = Path("software_maintenance/config/updater_config.json")

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                self.auto_check_enabled = config.get(
                    "auto_check_enabled", True
                )
                self.check_interval_hours = config.get(
                    "check_interval_hours", 24
                )
                self.auto_install_security = config.get(
                    "auto_install_security", False
                )
                self.create_restore_points = config.get(
                    "create_restore_points", True
                )
                self.backup_before_update = config.get(
                    "backup_before_update", True
                )

                self.log_info("Configuration loaded successfully")

            except Exception as e:
                self.log_warning(f"Failed to load configuration: {e}")

    def _save_configuration(self):
        """Save updater configuration to file."""
        config_file = Path("software_maintenance/config/updater_config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            config = {
                "auto_check_enabled": self.auto_check_enabled,
                "check_interval_hours": self.check_interval_hours,
                "auto_install_security": self.auto_install_security,
                "create_restore_points": self.create_restore_points,
                "backup_before_update": self.backup_before_update,
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save configuration: {e}")

    def _load_update_history(self):
        """Load update history from file."""
        history_file = Path("software_maintenance/config/update_history.json")

        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history_data = json.load(f)

                self.update_history = []
                for session_data in history_data:
                    session = UpdateSession(
                        session_id=session_data["session_id"],
                        start_time=datetime.fromisoformat(
                            session_data["start_time"]
                        ),
                        end_time=(
                            datetime.fromisoformat(session_data["end_time"])
                            if session_data.get("end_time")
                            else None
                        ),
                        total_updates=session_data["total_updates"],
                        successful_updates=session_data["successful_updates"],
                        failed_updates=session_data["failed_updates"],
                        skipped_updates=session_data["skipped_updates"],
                        updates_performed=session_data["updates_performed"],
                    )
                    self.update_history.append(session)

                self.log_info(
                    f"Loaded {len(self.update_history)} update sessions"
                )

            except Exception as e:
                self.log_warning(f"Failed to load update history: {e}")

    def _save_update_history(self):
        """Save update history to file."""
        history_file = Path("software_maintenance/config/update_history.json")
        history_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            history_data = [
                session.to_dict() for session in self.update_history
            ]

            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save update history: {e}")

    def _load_schedules(self):
        """Load update schedules from file."""
        schedules_file = Path(
            "software_maintenance/config/update_schedules.json"
        )

        if schedules_file.exists():
            try:
                with open(schedules_file, "r", encoding="utf-8") as f:
                    schedules_data = json.load(f)

                self.update_schedules = {}
                for schedule_id, schedule_data in schedules_data.items():
                    schedule = UpdateSchedule(
                        schedule_id=schedule_data["schedule_id"],
                        name=schedule_data["name"],
                        frequency=schedule_data["frequency"],
                        time=schedule_data["time"],
                        enabled=schedule_data["enabled"],
                        include_security_only=schedule_data[
                            "include_security_only"
                        ],
                        auto_install=schedule_data["auto_install"],
                        software_filter=schedule_data["software_filter"],
                    )
                    self.update_schedules[schedule_id] = schedule

                self.log_info(f"Loaded {len(self.update_schedules)} schedules")

            except Exception as e:
                self.log_warning(f"Failed to load schedules: {e}")

    def _save_schedules(self):
        """Save update schedules to file."""
        schedules_file = Path(
            "software_maintenance/config/update_schedules.json"
        )
        schedules_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            schedules_data = {
                schedule_id: schedule.to_dict()
                for schedule_id, schedule in self.update_schedules.items()
            }

            with open(schedules_file, "w", encoding="utf-8") as f:
                json.dump(schedules_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"Failed to save schedules: {e}")

    def scan_installed_software(
        self, include_system: bool = False
    ) -> Dict[str, SoftwareInfo]:
        """
        Scan for installed software using the software detector.

        Args:
            include_system: Include system components in scan

        Returns:
            Dictionary of detected software
        """
        self.update_status("Scanning installed software...")

        try:
            success = self.software_detector.run(
                include_system=include_system, save_results=True
            )

            if success:
                self.detected_software = (
                    self.software_detector.detected_software
                )
                self.log_info(
                    f"Found {len(self.detected_software)} installed applications"
                )
                return self.detected_software
            else:
                self.log_error("Software scan failed")
                return {}

        except Exception as e:
            self.log_error(f"Error scanning software: {e}")
            return {}

    def check_for_updates(
        self, software_list: List[str] = None
    ) -> Dict[str, UpdateInfo]:
        """
        Check for available updates using the update source manager.

        Args:
            software_list: Optional list of specific software to check

        Returns:
            Dictionary of available updates
        """
        self.update_status("Checking for available updates...")

        try:
            # If no specific list provided, check all detected software
            if software_list is None:
                software_list = list(self.detected_software.keys())

            success = self.update_manager.run(
                software_list=software_list, save_report=True
            )

            if success:
                self.available_updates = self.update_manager.available_updates
                self.log_info(
                    f"Found {len(self.available_updates)} available updates"
                )
                return self.available_updates
            else:
                self.log_error("Update check failed")
                return {}

        except Exception as e:
            self.log_error(f"Error checking updates: {e}")
            return {}

    def get_changelog(self, software_name: str) -> str:
        """
        Get changelog for a specific software update.

        Args:
            software_name: Name of the software

        Returns:
            Changelog text
        """
        try:
            if software_name in self.available_updates:
                changelog = self.update_manager.get_changelog(software_name)
                self.log_info(f"Retrieved changelog for {software_name}")
                return changelog
            else:
                return f"No update available for {software_name}"

        except Exception as e:
            self.log_error(f"Error getting changelog for {software_name}: {e}")
            return f"Error retrieving changelog: {e}"

    def create_pre_update_backup(self, software_name: str) -> Optional[str]:
        """
        Create backup before updating software.

        Args:
            software_name: Name of the software to backup

        Returns:
            Backup ID if successful, None otherwise
        """
        if not self.backup_before_update:
            return None

        try:
            # Find software installation location
            if software_name in self.detected_software:
                software_info = self.detected_software[software_name]
                install_location = software_info.install_location

                if install_location and Path(install_location).exists():
                    backup_id = self.security_manager.create_directory_backup(
                        install_location, f"{software_name}_pre_update"
                    )

                    if backup_id:
                        self.log_info(
                            f"Created backup for {software_name}: {backup_id}"
                        )
                        return backup_id

            # Fallback: create registry backup if available
            if software_name in self.detected_software:
                software_info = self.detected_software[software_name]
                if software_info.registry_key:
                    backup_id = self.security_manager.create_registry_backup(
                        software_info.registry_key
                    )

                    if backup_id:
                        self.log_info(
                            f"Created registry backup for {software_name}: {backup_id}"
                        )
                        return backup_id

            self.log_warning(f"Could not create backup for {software_name}")
            return None

        except Exception as e:
            self.log_error(f"Error creating backup for {software_name}: {e}")
            return None

    def update_software(
        self, software_name: str, create_backup: bool = None
    ) -> bool:
        """
        Update a specific software package.

        Args:
            software_name: Name of the software to update
            create_backup: Override backup setting for this update

        Returns:
            True if successful, False otherwise
        """
        if software_name not in self.available_updates:
            self.log_error(f"No update available for {software_name}")
            return False

        try:
            self.update_status(f"Updating {software_name}...")

            # Create restore point if enabled
            restore_point_id = None
            if self.create_restore_points:
                restore_point_id = (
                    self.security_manager.create_system_restore_point(
                        f"Before updating {software_name}",
                        f"Automatic restore point created by Software Updater",
                    )
                )

            # Create backup if enabled
            backup_id = None
            if create_backup or (
                create_backup is None and self.backup_before_update
            ):
                backup_id = self.create_pre_update_backup(software_name)

            # Perform the update
            success = self.update_manager.execute_update(software_name)

            if success:
                self.log_info(f"Successfully updated {software_name}")

                # Remove from available updates
                if software_name in self.available_updates:
                    del self.available_updates[software_name]

                return True
            else:
                self.log_error(f"Failed to update {software_name}")

                # Offer to restore backup if update failed
                if backup_id:
                    self.log_info(
                        f"Backup available for rollback: {backup_id}"
                    )

                return False

        except Exception as e:
            self.log_error(f"Error updating {software_name}: {e}")
            return False

    def update_multiple_software(
        self, software_list: List[str], create_backups: bool = None
    ) -> Dict[str, bool]:
        """
        Update multiple software packages.

        Args:
            software_list: List of software names to update
            create_backups: Override backup setting for these updates

        Returns:
            Dictionary mapping software names to success status
        """
        results = {}
        total_updates = len(software_list)

        # Create update session
        session = UpdateSession(
            session_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(),
            total_updates=total_updates,
        )

        try:
            for i, software_name in enumerate(software_list):
                if self.is_cancelled:
                    break

                progress = int(((i + 1) / total_updates) * 100)
                self.update_progress(percentage=progress)

                success = self.update_software(software_name, create_backups)
                results[software_name] = success

                if success:
                    session.successful_updates += 1
                    session.updates_performed.append(software_name)
                else:
                    session.failed_updates += 1

            # Complete session
            session.end_time = datetime.now()
            self.update_history.append(session)
            self._save_update_history()

            self.log_info(
                f"Batch update completed: {session.successful_updates}/{total_updates} successful"
            )

        except Exception as e:
            self.log_error(f"Error in batch update: {e}")
            session.end_time = datetime.now()
            self.update_history.append(session)
            self._save_update_history()

        return results

    def rollback_update(self, software_name: str, backup_id: str) -> bool:
        """
        Rollback a software update using a backup.

        Args:
            software_name: Name of the software to rollback
            backup_id: ID of the backup to restore

        Returns:
            True if successful, False otherwise
        """
        try:
            self.update_status(f"Rolling back {software_name}...")

            success = self.security_manager.restore_backup(backup_id)

            if success:
                self.log_info(f"Successfully rolled back {software_name}")
                return True
            else:
                self.log_error(f"Failed to rollback {software_name}")
                return False

        except Exception as e:
            self.log_error(f"Error rolling back {software_name}: {e}")
            return False

    def create_update_schedule(
        self,
        name: str,
        frequency: str,
        time: str,
        include_security_only: bool = False,
        auto_install: bool = False,
        software_filter: List[str] = None,
    ) -> str:
        """
        Create a new update schedule.

        Args:
            name: Name for the schedule
            frequency: 'daily', 'weekly', or 'monthly'
            time: Time in HH:MM format
            include_security_only: Only check for security updates
            auto_install: Automatically install updates
            software_filter: List of specific software to include

        Returns:
            Schedule ID
        """
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        schedule = UpdateSchedule(
            schedule_id=schedule_id,
            name=name,
            frequency=frequency,
            time=time,
            include_security_only=include_security_only,
            auto_install=auto_install,
            software_filter=software_filter or [],
        )

        self.update_schedules[schedule_id] = schedule
        self._save_schedules()

        # Update scheduler
        self._update_scheduler()

        self.log_info(f"Created update schedule: {name}")
        return schedule_id

    def _update_scheduler(self):
        """Update the task scheduler with current schedules."""
        # Clear existing scheduled jobs
        schedule.clear()

        for schedule_obj in self.update_schedules.values():
            if not schedule_obj.enabled:
                continue

            if schedule_obj.frequency == "daily":
                schedule.every().day.at(schedule_obj.time).do(
                    self._scheduled_update_check, schedule_obj
                )
            elif schedule_obj.frequency == "weekly":
                schedule.every().week.at(schedule_obj.time).do(
                    self._scheduled_update_check, schedule_obj
                )
            elif schedule_obj.frequency == "monthly":
                # Approximate monthly scheduling
                schedule.every(30).days.at(schedule_obj.time).do(
                    self._scheduled_update_check, schedule_obj
                )

        self.log_info(
            f"Updated scheduler with {len(self.update_schedules)} schedules"
        )

    def _scheduled_update_check(self, schedule_obj: UpdateSchedule):
        """Perform a scheduled update check."""
        try:
            self.log_info(
                f"Running scheduled update check: {schedule_obj.name}"
            )

            # Scan for software
            self.scan_installed_software()

            # Check for updates
            software_list = (
                schedule_obj.software_filter
                if schedule_obj.software_filter
                else None
            )
            self.check_for_updates(software_list)

            # Filter for security updates if requested
            updates_to_process = self.available_updates
            if schedule_obj.include_security_only:
                updates_to_process = {
                    name: update
                    for name, update in self.available_updates.items()
                    if update.is_security_update
                }

            # Auto-install if enabled
            if schedule_obj.auto_install and updates_to_process:
                software_names = list(updates_to_process.keys())
                self.update_multiple_software(software_names)

        except Exception as e:
            self.log_error(f"Error in scheduled update check: {e}")

    def start_scheduler(self):
        """Start the update scheduler."""
        if self.scheduler_running:
            return

        self.scheduler_running = True
        self._update_scheduler()

        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                threading.Event().wait(60)  # Check every minute

        self.scheduler_thread = threading.Thread(
            target=run_scheduler, daemon=True
        )
        self.scheduler_thread.start()

        self.log_info("Update scheduler started")

    def stop_scheduler(self):
        """Stop the update scheduler."""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        self.log_info("Update scheduler stopped")

    def get_update_statistics(self) -> Dict[str, any]:
        """Get comprehensive update statistics."""
        total_sessions = len(self.update_history)
        total_updates = sum(
            session.successful_updates for session in self.update_history
        )
        total_failures = sum(
            session.failed_updates for session in self.update_history
        )

        # Recent activity (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_sessions = [
            s for s in self.update_history if s.start_time >= recent_cutoff
        ]
        recent_updates = sum(
            session.successful_updates for session in recent_sessions
        )

        return {
            "total_sessions": total_sessions,
            "total_successful_updates": total_updates,
            "total_failed_updates": total_failures,
            "recent_updates_30_days": recent_updates,
            "available_updates": len(self.available_updates),
            "detected_software": len(self.detected_software),
            "active_schedules": len(
                [s for s in self.update_schedules.values() if s.enabled]
            ),
            "security_updates_available": len(
                [
                    u
                    for u in self.available_updates.values()
                    if u.is_security_update
                ]
            ),
        }

    def execute(
        self,
        scan_software: bool = True,
        check_updates: bool = True,
        include_system: bool = False,
        save_reports: bool = True,
    ) -> bool:
        """
        Execute comprehensive software update checking.

        Args:
            scan_software: Perform software scanning
            check_updates: Check for available updates
            include_system: Include system components
            save_reports: Save scan and update reports

        Returns:
            True if successful, False otherwise
        """
        try:
            steps = []
            if scan_software:
                steps.append("Software Scan")
            if check_updates:
                steps.append("Update Check")
            if save_reports:
                steps.append("Save Reports")

            self.set_progress_steps(steps)

            # Scan installed software
            if scan_software:
                self.next_step("Scanning installed software")
                self.scan_installed_software(include_system)

            # Check for updates
            if check_updates:
                self.next_step("Checking for updates")
                self.check_for_updates()

            # Save reports
            if save_reports:
                self.next_step("Saving reports")
                if self.available_updates:
                    self.update_manager.save_update_report()
                if self.detected_software:
                    self.software_detector.save_software_list()

            self.log_info("Software update check completed successfully")
            return True

        except Exception as e:
            self.log_error(f"Software update check failed: {e}")
            return False
