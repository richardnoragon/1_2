"""SMART data analysis for disk health monitoring."""

import logging
import subprocess
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...core.platform_detector import SupportedPlatform
from core.error_handler import error_handler


class SmartAnalyzer:
    """Analyzes SMART data from storage devices."""

    def __init__(self):
        """Initialize the SMART analyzer."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.SmartAnalyzer"
        )
        self.platform = None
        self.smartctl_path = None
        self.initialized = False

        # SMART attribute mappings
        self.smart_attributes = {
            1: "raw_read_error_rate",
            3: "spin_up_time",
            4: "start_stop_count",
            5: "reallocated_sectors",
            7: "seek_error_rate",
            9: "power_on_hours",
            10: "spin_retry_count",
            11: "recalibration_retries",
            12: "power_cycle_count",
            184: "end_to_end_error",
            187: "reported_uncorrectable_errors",
            188: "command_timeout",
            189: "high_fly_writes",
            190: "airflow_temperature",
            194: "temperature",
            195: "hardware_ecc_recovered",
            196: "reallocation_event_count",
            197: "current_pending_sectors",
            198: "offline_uncorrectable",
            199: "udma_crc_error_count",
            200: "multi_zone_error_rate",
            240: "head_flying_hours",
            241: "total_lbas_written",
            242: "total_lbas_read",
        }

        self.logger.info("SMART analyzer initialized")

    def initialize(self, platform: SupportedPlatform) -> bool:
        """Initialize platform-specific SMART monitoring.

        Args:
            platform: Target platform

        Returns:
            bool: True if initialization successful
        """
        try:
            self.platform = platform

            # Find smartctl executable
            self.smartctl_path = self._find_smartctl()

            if not self.smartctl_path:
                self.logger.warning(
                    "smartctl not found - SMART monitoring disabled"
                )
                return False

            # Test smartctl functionality
            if not self._test_smartctl():
                self.logger.warning(
                    "smartctl test failed - SMART monitoring disabled"
                )
                return False

            self.initialized = True
            self.logger.info(
                f"SMART monitoring initialized for {platform.value}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize SMART monitoring: {e}")
            error_handler.handle_error(e, "SmartAnalyzer.initialize")
            return False

    def _find_smartctl(self) -> Optional[str]:
        """Find the smartctl executable.

        Returns:
            Path to smartctl or None if not found
        """
        try:
            # Common paths for smartctl
            if self.platform == SupportedPlatform.WINDOWS:
                possible_paths = [
                    r"C:\Program Files\smartmontools\bin\smartctl.exe",
                    r"C:\Program Files (x86)\smartmontools\bin\smartctl.exe",
                    "smartctl.exe",  # If in PATH
                ]
            else:
                possible_paths = [
                    "/usr/sbin/smartctl",
                    "/usr/bin/smartctl",
                    "/sbin/smartctl",
                    "/bin/smartctl",
                    "smartctl",  # If in PATH
                ]

            # Check each possible path
            for path in possible_paths:
                if self._check_executable(path):
                    self.logger.debug(f"Found smartctl at: {path}")
                    return path

            # Try to find in PATH
            try:
                result = subprocess.run(
                    (
                        ["which", "smartctl"]
                        if self.platform != SupportedPlatform.WINDOWS
                        else ["where", "smartctl"]
                    ),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip().split("\n")[0]
                    self.logger.debug(f"Found smartctl in PATH: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            return None

        except Exception as e:
            self.logger.error(f"Error finding smartctl: {e}")
            return None

    def _check_executable(self, path: str) -> bool:
        """Check if a file is an executable.

        Args:
            path: Path to check

        Returns:
            bool: True if executable exists and is runnable
        """
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return False

            # Try to run with --version to test
            result = subprocess.run(
                [str(path_obj), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0

        except Exception:
            return False

    def _test_smartctl(self) -> bool:
        """Test smartctl functionality.

        Returns:
            bool: True if smartctl is working
        """
        try:
            if not self.smartctl_path:
                return False

            # Test with --scan option
            result = subprocess.run(
                [self.smartctl_path, "--scan"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # smartctl returns 0 for success, but may return other codes
            # for various conditions that are not necessarily errors
            return result.returncode in [0, 1, 2, 4]

        except Exception as e:
            self.logger.error(f"Error testing smartctl: {e}")
            return False

    def get_smart_data(self, device: str) -> Optional[Dict[str, Any]]:
        """Get SMART data for a device.

        Args:
            device: Device identifier

        Returns:
            Dict containing SMART data or None if unavailable
        """
        if not self.initialized or not self.smartctl_path:
            return None

        try:
            # Convert device path for platform
            device_path = self._convert_device_path(device)
            if not device_path:
                return None

            # Get SMART data in JSON format
            smart_data = self._get_smart_json(device_path)
            if smart_data:
                return self._parse_smart_data(smart_data)

            # Fallback to text format if JSON not available
            return self._get_smart_text(device_path)

        except Exception as e:
            self.logger.error(f"Error getting SMART data for {device}: {e}")
            return None

    def _convert_device_path(self, device: str) -> Optional[str]:
        """Convert device identifier to platform-specific path.

        Args:
            device: Device identifier

        Returns:
            Platform-specific device path or None
        """
        try:
            if self.platform == SupportedPlatform.WINDOWS:
                # Windows device paths
                if device.startswith("/dev/"):
                    # Convert Linux-style to Windows
                    return None
                elif ":" in device:
                    # Drive letter format (C:, D:, etc.)
                    drive_letter = device.split(":")[0]
                    drive_index = ord(drive_letter.upper()) - ord("A")
                    return f"/dev/sd{chr(ord('a') + drive_index)}"
                else:
                    return device
            else:
                # Unix-like systems
                if device.startswith("/dev/"):
                    return device
                elif ":" in device and len(device) == 2:
                    # Convert Windows drive letter to Unix device
                    drive_letter = device[0].upper()
                    drive_index = ord(drive_letter) - ord("A")
                    return f"/dev/sd{chr(ord('a') + drive_index)}"
                else:
                    # Try to find the actual device
                    return self._find_device_path(device)

        except Exception as e:
            self.logger.error(f"Error converting device path {device}: {e}")
            return None

    def _find_device_path(self, device: str) -> Optional[str]:
        """Find the actual device path for a given device identifier.

        Args:
            device: Device identifier

        Returns:
            Device path or None if not found
        """
        try:
            # Use smartctl --scan to find devices
            result = subprocess.run(
                [self.smartctl_path, "--scan"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode not in [0, 1, 2, 4]:
                return None

            # Parse scan output
            for line in result.stdout.split("\n"):
                if device in line or device.replace("/", "") in line:
                    parts = line.split()
                    if parts:
                        return parts[0]

            return None

        except Exception as e:
            self.logger.error(f"Error finding device path for {device}: {e}")
            return None

    def _get_smart_json(self, device_path: str) -> Optional[Dict[str, Any]]:
        """Get SMART data in JSON format.

        Args:
            device_path: Device path

        Returns:
            Parsed JSON data or None
        """
        try:
            result = subprocess.run(
                [self.smartctl_path, "-a", "-j", device_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                return json.loads(result.stdout)

            return None

        except (
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
            Exception,
        ) as e:
            self.logger.debug(
                f"JSON SMART data not available for {device_path}: {e}"
            )
            return None

    def _get_smart_text(self, device_path: str) -> Optional[Dict[str, Any]]:
        """Get SMART data in text format and parse it.

        Args:
            device_path: Device path

        Returns:
            Parsed SMART data or None
        """
        try:
            result = subprocess.run(
                [self.smartctl_path, "-a", device_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                return self._parse_smart_text(result.stdout)

            return None

        except subprocess.TimeoutExpired as e:
            self.logger.error(
                f"Timeout getting SMART data for {device_path}: {e}"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting SMART text for {device_path}: {e}"
            )
            return None

    def _parse_smart_data(self, smart_json: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON SMART data.

        Args:
            smart_json: Raw JSON SMART data

        Returns:
            Parsed SMART data
        """
        try:
            parsed_data = {
                "overall_health": "unknown",
                "temperature": None,
                "power_on_hours": None,
                "reallocated_sectors": None,
                "pending_sectors": None,
                "uncorrectable_sectors": None,
                "attributes": {},
            }

            # Overall health
            smart_status = smart_json.get("smart_status", {})
            if smart_status.get("passed"):
                parsed_data["overall_health"] = "passed"
            else:
                parsed_data["overall_health"] = "failed"

            # Parse attributes
            ata_smart_attributes = smart_json.get("ata_smart_attributes", {})
            table = ata_smart_attributes.get("table", [])

            for attr in table:
                attr_id = attr.get("id")
                attr_name = self.smart_attributes.get(
                    attr_id, f"attr_{attr_id}"
                )
                raw_value = attr.get("raw", {}).get("value", 0)

                parsed_data["attributes"][attr_name] = {
                    "id": attr_id,
                    "name": attr.get("name", ""),
                    "value": attr.get("value", 0),
                    "raw_value": raw_value,
                    "threshold": attr.get("thresh", 0),
                    "worst": attr.get("worst", 0),
                }

                # Extract key metrics
                if attr_id == 194:  # Temperature
                    parsed_data["temperature"] = raw_value
                elif attr_id == 9:  # Power on hours
                    parsed_data["power_on_hours"] = raw_value
                elif attr_id == 5:  # Reallocated sectors
                    parsed_data["reallocated_sectors"] = raw_value
                elif attr_id == 197:  # Current pending sectors
                    parsed_data["pending_sectors"] = raw_value
                elif attr_id == 198:  # Offline uncorrectable
                    parsed_data["uncorrectable_sectors"] = raw_value

            return parsed_data

        except Exception as e:
            self.logger.error(f"Error parsing SMART JSON data: {e}")
            return {}

    def _parse_smart_text(self, smart_text: str) -> Dict[str, Any]:
        """Parse text SMART data.

        Args:
            smart_text: Raw text SMART data

        Returns:
            Parsed SMART data
        """
        try:
            parsed_data = {
                "overall_health": "unknown",
                "temperature": None,
                "power_on_hours": None,
                "reallocated_sectors": None,
                "attributes": {},
            }

            lines = smart_text.split("\n")

            # Parse overall health
            for line in lines:
                line_lower = line.lower()
                if (
                    "overall-health" in line_lower
                    or "health status" in line_lower
                ):
                    if "passed" in line.lower() or "ok" in line.lower():
                        parsed_data["overall_health"] = "passed"
                    elif "failed" in line.lower() or "failing" in line.lower():
                        parsed_data["overall_health"] = "failed"
                    break

            # Parse attributes table
            in_attributes = False
            for line in lines:
                line = line.strip()

                if "id#" in line.lower() and "attribute_name" in line.lower():
                    in_attributes = True
                    continue

                if in_attributes and line:
                    # Parse attribute line
                    parts = line.split()
                    if len(parts) >= 10 and parts[0].isdigit():
                        try:
                            attr_id = int(parts[0])
                            attr_name = parts[1]
                            value = int(parts[3])
                            worst = int(parts[4])
                            threshold = int(parts[5])
                            raw_value = int(parts[9])

                            parsed_data["attributes"][attr_name.lower()] = {
                                "id": attr_id,
                                "name": attr_name,
                                "value": value,
                                "raw_value": raw_value,
                                "threshold": threshold,
                                "worst": worst,
                            }

                            # Extract key metrics
                            if attr_id == 194:  # Temperature
                                parsed_data["temperature"] = raw_value
                            elif attr_id == 9:  # Power on hours
                                parsed_data["power_on_hours"] = raw_value
                            elif attr_id == 5:  # Reallocated sectors
                                parsed_data["reallocated_sectors"] = raw_value

                        except (ValueError, IndexError):
                            continue

            return parsed_data

        except Exception as e:
            self.logger.error(f"Error parsing SMART text data: {e}")
            return {}

    def get_device_list(self) -> List[str]:
        """Get list of SMART-capable devices.

        Returns:
            List of device paths
        """
        if not self.initialized or not self.smartctl_path:
            return []

        try:
            result = subprocess.run(
                [self.smartctl_path, "--scan"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            devices = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if parts:
                        devices.append(parts[0])

            return devices

        except Exception as e:
            self.logger.error(f"Error getting device list: {e}")
            return []

    def is_smart_supported(self, device: str) -> bool:
        """Check if SMART is supported for a device.

        Args:
            device: Device identifier

        Returns:
            bool: True if SMART is supported
        """
        if not self.initialized or not self.smartctl_path:
            return False

        try:
            device_path = self._convert_device_path(device)
            if not device_path:
                return False

            result = subprocess.run(
                [self.smartctl_path, "-i", device_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Check if SMART is available and enabled
            output = result.stdout.lower()
            return (
                "smart support is: available" in output
                or "smart support is: enabled" in output
            )

        except Exception as e:
            self.logger.error(
                f"Error checking SMART support for {device}: {e}"
            )
            return False
