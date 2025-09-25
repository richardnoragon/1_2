"""
Update Sources Manager for Software Maintenance Toolkit

This module provides comprehensive update source management including
integration with multiple package managers, update checking, changelog
retrieval, and update execution across different platforms.
"""

import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

from .maintenance_base import MaintenanceToolBase


@dataclass
class UpdateInfo:
    """Data class representing available update information."""

    software_name: str
    current_version: str
    available_version: str
    update_source: str
    changelog_url: str = ""
    changelog_text: str = ""
    download_url: str = ""
    size_mb: Optional[float] = None
    release_date: Optional[datetime] = None
    is_security_update: bool = False
    is_critical: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "software_name": self.software_name,
            "current_version": self.current_version,
            "available_version": self.available_version,
            "update_source": self.update_source,
            "changelog_url": self.changelog_url,
            "changelog_text": self.changelog_text,
            "download_url": self.download_url,
            "size_mb": self.size_mb,
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
            "is_security_update": self.is_security_update,
            "is_critical": self.is_critical,
        }


class UpdateSource(ABC):
    """Abstract base class for update sources."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def check_updates(self, software_list: List[str]) -> List[UpdateInfo]:
        """Check for updates for the given software list."""
        pass

    @abstractmethod
    def get_changelog(self, software_name: str, version: str) -> str:
        """Get changelog for a specific software version."""
        pass

    @abstractmethod
    def execute_update(self, software_name: str) -> bool:
        """Execute update for specific software."""
        pass


class ChocolateySource(UpdateSource):
    """Chocolatey package manager update source."""

    def __init__(self):
        super().__init__("Chocolatey")

    def check_updates(self, software_list: List[str]) -> List[UpdateInfo]:
        """Check for updates using Chocolatey."""
        updates = []

        try:
            # Get outdated packages
            result = subprocess.run(
                ["choco", "outdated", "--limit-output"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            current = parts[1].strip()
                            available = parts[2].strip()

                            if name in software_list or not software_list:
                                update_info = UpdateInfo(
                                    software_name=name,
                                    current_version=current,
                                    available_version=available,
                                    update_source="chocolatey",
                                )
                                updates.append(update_info)

        except Exception as e:
            print(f"Error checking Chocolatey updates: {e}")

        return updates

    def get_changelog(self, software_name: str, version: str) -> str:
        """Get changelog from Chocolatey community repository."""
        try:
            # Try to get package info from Chocolatey API
            url = f"https://chocolatey.org/api/v2/Packages?$filter=Id eq '{software_name}'"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Parse XML response for release notes
                # This is a simplified implementation
                return f"Changelog for {software_name} {version} available at chocolatey.org"

        except Exception as e:
            print(f"Error getting Chocolatey changelog: {e}")

        return f"Changelog not available for {software_name}"

    def execute_update(self, software_name: str) -> bool:
        """Execute update using Chocolatey."""
        try:
            result = subprocess.run(
                ["choco", "upgrade", software_name, "-y"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error updating {software_name} with Chocolatey: {e}")
            return False


class WingetSource(UpdateSource):
    """Windows Package Manager update source."""

    def __init__(self):
        super().__init__("Winget")

    def check_updates(self, software_list: List[str]) -> List[UpdateInfo]:
        """Check for updates using Winget."""
        updates = []

        try:
            # Get available upgrades
            result = subprocess.run(
                ["winget", "upgrade", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Skip header lines
                for line in lines[2:]:
                    if line.strip() and not line.startswith("-"):
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            current = parts[1]
                            available = parts[2]

                            if name in software_list or not software_list:
                                update_info = UpdateInfo(
                                    software_name=name,
                                    current_version=current,
                                    available_version=available,
                                    update_source="winget",
                                )
                                updates.append(update_info)

        except Exception as e:
            print(f"Error checking Winget updates: {e}")

        return updates

    def get_changelog(self, software_name: str, version: str) -> str:
        """Get changelog from Winget manifest."""
        try:
            # Get package info
            result = subprocess.run(
                ["winget", "show", software_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse output for release notes
                lines = result.stdout.split("\n")
                changelog_section = False
                changelog_lines = []

                for line in lines:
                    if "Release Notes" in line or "Description" in line:
                        changelog_section = True
                        continue
                    elif changelog_section and line.strip():
                        if line.startswith(" "):
                            changelog_lines.append(line.strip())
                        else:
                            break

                if changelog_lines:
                    return "\n".join(changelog_lines)

        except Exception as e:
            print(f"Error getting Winget changelog: {e}")

        return f"Changelog not available for {software_name}"

    def execute_update(self, software_name: str) -> bool:
        """Execute update using Winget."""
        try:
            result = subprocess.run(
                [
                    "winget",
                    "upgrade",
                    software_name,
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error updating {software_name} with Winget: {e}")
            return False


class HomebrewSource(UpdateSource):
    """Homebrew package manager update source."""

    def __init__(self):
        super().__init__("Homebrew")

    def check_updates(self, software_list: List[str]) -> List[UpdateInfo]:
        """Check for updates using Homebrew."""
        updates = []

        try:
            # Update Homebrew first
            subprocess.run(["brew", "update"], capture_output=True, timeout=60)

            # Get outdated packages
            result = subprocess.run(
                ["brew", "outdated", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                outdated_data = json.loads(result.stdout)

                for package in outdated_data:
                    name = package.get("name", "")
                    current = package.get("installed_versions", [""])[0]
                    available = package.get("current_version", "")

                    if name in software_list or not software_list:
                        update_info = UpdateInfo(
                            software_name=name,
                            current_version=current,
                            available_version=available,
                            update_source="homebrew",
                        )
                        updates.append(update_info)

        except Exception as e:
            print(f"Error checking Homebrew updates: {e}")

        return updates

    def get_changelog(self, software_name: str, version: str) -> str:
        """Get changelog from Homebrew formula."""
        try:
            # Get formula info
            result = subprocess.run(
                ["brew", "info", software_name, "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                info_data = json.loads(result.stdout)
                if info_data and len(info_data) > 0:
                    formula = info_data[0]
                    desc = formula.get("desc", "")
                    homepage = formula.get("homepage", "")

                    changelog = f"Description: {desc}\n"
                    if homepage:
                        changelog += f"Homepage: {homepage}\n"

                    return changelog

        except Exception as e:
            print(f"Error getting Homebrew changelog: {e}")

        return f"Changelog not available for {software_name}"

    def execute_update(self, software_name: str) -> bool:
        """Execute update using Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "upgrade", software_name],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error updating {software_name} with Homebrew: {e}")
            return False


class AptSource(UpdateSource):
    """APT package manager update source."""

    def __init__(self):
        super().__init__("APT")

    def check_updates(self, software_list: List[str]) -> List[UpdateInfo]:
        """Check for updates using APT."""
        updates = []

        try:
            # Update package lists
            subprocess.run(
                ["sudo", "apt", "update"], capture_output=True, timeout=60
            )

            # Get upgradable packages
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n")[
                    1:
                ]:  # Skip header
                    if "/" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            name_arch = parts[0].split("/")[0]
                            version_info = parts[1]

                            # Parse version info
                            if "[upgradable from:" in line:
                                available = version_info
                                current_start = (
                                    line.find("[upgradable from: ") + 18
                                )
                                current_end = line.find("]", current_start)
                                current = line[current_start:current_end]

                                if (
                                    name_arch in software_list
                                    or not software_list
                                ):
                                    update_info = UpdateInfo(
                                        software_name=name_arch,
                                        current_version=current,
                                        available_version=available,
                                        update_source="apt",
                                    )
                                    updates.append(update_info)

        except Exception as e:
            print(f"Error checking APT updates: {e}")

        return updates

    def get_changelog(self, software_name: str, version: str) -> str:
        """Get changelog from APT."""
        try:
            # Get package information
            result = subprocess.run(
                ["apt", "show", software_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                description_lines = []
                in_description = False

                for line in lines:
                    if line.startswith("Description:"):
                        in_description = True
                        description_lines.append(line[12:].strip())
                    elif in_description and line.startswith(" "):
                        description_lines.append(line.strip())
                    elif in_description and not line.startswith(" "):
                        break

                if description_lines:
                    return "\n".join(description_lines)

        except Exception as e:
            print(f"Error getting APT changelog: {e}")

        return f"Changelog not available for {software_name}"

    def execute_update(self, software_name: str) -> bool:
        """Execute update using APT."""
        try:
            result = subprocess.run(
                ["sudo", "apt", "upgrade", software_name, "-y"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error updating {software_name} with APT: {e}")
            return False


class UpdateSourceManager(MaintenanceToolBase):
    """
    Manager for multiple update sources providing unified update checking
    and execution across different package managers.
    """

    def __init__(self):
        super().__init__("Update Source Manager")

        self.sources: Dict[str, UpdateSource] = {}
        self.available_updates: Dict[str, UpdateInfo] = {}

        # Initialize available sources based on platform
        self._initialize_sources()

    def _initialize_sources(self):
        """Initialize available update sources based on the platform."""
        import sys

        if sys.platform == "win32":
            # Windows sources
            if self._command_exists("choco"):
                self.sources["chocolatey"] = ChocolateySource()
            if self._command_exists("winget"):
                self.sources["winget"] = WingetSource()

        elif sys.platform == "darwin":
            # macOS sources
            if self._command_exists("brew"):
                self.sources["homebrew"] = HomebrewSource()

        else:
            # Linux sources
            if self._command_exists("apt"):
                self.sources["apt"] = AptSource()

        self.log_info(
            f"Initialized update sources: {list(self.sources.keys())}"
        )

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(
                [command, "--version"],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def check_all_updates(
        self, software_list: List[str] = None
    ) -> Dict[str, UpdateInfo]:
        """
        Check for updates across all available sources.

        Args:
            software_list: Optional list of specific software to check

        Returns:
            Dictionary of available updates
        """
        self.available_updates.clear()

        if not software_list:
            software_list = []

        total_sources = len(self.sources)
        current_source = 0

        for source_name, source in self.sources.items():
            current_source += 1
            progress = int((current_source / total_sources) * 100)

            self.update_status(f"Checking updates from {source_name}...")
            self.update_progress(percentage=progress)

            try:
                updates = source.check_updates(software_list)

                for update in updates:
                    # Use software name as key, preferring newer versions
                    key = update.software_name
                    if key not in self.available_updates:
                        self.available_updates[key] = update
                    else:
                        # Compare versions and keep the newer one
                        existing = self.available_updates[key]
                        if (
                            self._compare_versions(
                                update.available_version,
                                existing.available_version,
                            )
                            > 0
                        ):
                            self.available_updates[key] = update

                self.log_info(
                    f"Found {len(updates)} updates from {source_name}"
                )

            except Exception as e:
                self.log_error(
                    f"Error checking updates from {source_name}: {e}"
                )

        self.log_info(
            f"Total available updates: {len(self.available_updates)}"
        )
        return self.available_updates

    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Returns:
            1 if version1 > version2
            0 if version1 == version2
            -1 if version1 < version2
        """
        try:
            # Simple version comparison - split by dots and compare numerically
            v1_parts = [int(x) for x in version1.split(".") if x.isdigit()]
            v2_parts = [int(x) for x in version2.split(".") if x.isdigit()]

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1

            return 0

        except (ValueError, AttributeError):
            # Fallback to string comparison
            if version1 > version2:
                return 1
            elif version1 < version2:
                return -1
            else:
                return 0

    def get_changelog(self, software_name: str) -> str:
        """Get changelog for a specific software."""
        if software_name not in self.available_updates:
            return f"No update information available for {software_name}"

        update_info = self.available_updates[software_name]
        source_name = update_info.update_source

        if source_name in self.sources:
            source = self.sources[source_name]
            changelog = source.get_changelog(
                software_name, update_info.available_version
            )

            # Cache the changelog
            update_info.changelog_text = changelog
            return changelog

        return f"Update source {source_name} not available"

    def execute_update(self, software_name: str) -> bool:
        """Execute update for specific software."""
        if software_name not in self.available_updates:
            self.log_error(f"No update available for {software_name}")
            return False

        update_info = self.available_updates[software_name]
        source_name = update_info.update_source

        if source_name not in self.sources:
            self.log_error(f"Update source {source_name} not available")
            return False

        self.update_status(f"Updating {software_name}...")

        try:
            source = self.sources[source_name]
            success = source.execute_update(software_name)

            if success:
                self.log_info(f"Successfully updated {software_name}")
                # Remove from available updates
                del self.available_updates[software_name]
            else:
                self.log_error(f"Failed to update {software_name}")

            return success

        except Exception as e:
            self.log_error(f"Error updating {software_name}: {e}")
            return False

    def execute_batch_update(
        self, software_list: List[str]
    ) -> Dict[str, bool]:
        """Execute updates for multiple software packages."""
        results = {}

        total_updates = len(software_list)

        for i, software_name in enumerate(software_list):
            progress = int(((i + 1) / total_updates) * 100)
            self.update_progress(percentage=progress)

            results[software_name] = self.execute_update(software_name)

        return results

    def save_update_report(self, filename: str = None) -> str:
        """Save available updates to a report file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"update_report_{timestamp}.json"

        filepath = Path("software_maintenance/reports") / filename

        try:
            report_data = {
                "scan_date": datetime.now().isoformat(),
                "total_updates": len(self.available_updates),
                "update_sources": list(self.sources.keys()),
                "updates": {
                    name: update.to_dict()
                    for name, update in self.available_updates.items()
                },
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            self.log_info(f"Update report saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.log_error(f"Failed to save update report: {e}")
            return ""

    def execute(
        self, software_list: List[str] = None, save_report: bool = True
    ) -> bool:
        """
        Execute update checking across all sources.

        Args:
            software_list: Optional list of specific software to check
            save_report: Whether to save the update report

        Returns:
            True if successful, False otherwise
        """
        try:
            self.update_status("Initializing update check...")

            # Check for updates
            updates = self.check_all_updates(software_list)

            # Save report if requested
            if save_report and updates:
                self.update_status("Saving update report...")
                self.save_update_report()

            self.update_status(
                f"Update check completed. Found {len(updates)} updates"
            )
            return True

        except Exception as e:
            self.log_error(f"Update check failed: {e}")
            return False

    def get_update_statistics(self) -> Dict[str, any]:
        """Get statistics about available updates."""
        source_counts = {}
        security_updates = 0
        critical_updates = 0

        for update in self.available_updates.values():
            source = update.update_source
            source_counts[source] = source_counts.get(source, 0) + 1

            if update.is_security_update:
                security_updates += 1
            if update.is_critical:
                critical_updates += 1

        return {
            "total_updates": len(self.available_updates),
            "source_breakdown": source_counts,
            "security_updates": security_updates,
            "critical_updates": critical_updates,
            "available_sources": list(self.sources.keys()),
        }
