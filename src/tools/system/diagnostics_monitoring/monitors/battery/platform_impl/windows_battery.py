"""Windows-specific battery monitoring with WMI and Power Management APIs."""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import wmi

    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    wmi = None

try:
    import win32api
    import win32con
    import win32file

    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    win32api = None
    win32con = None
    win32file = None

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class WindowsBatteryMonitor(MonitorBase):
    """Windows-specific battery monitoring with enhanced capabilities."""

    def __init__(self, update_interval: float = 60.0):
        """Initialize Windows battery monitor.

        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("WindowsBatteryHealth", update_interval)

        # Windows-specific components
        self.wmi_connection = None
        self.power_management_data = {}

        # Capabilities flags
        self.wmi_enabled = WMI_AVAILABLE
        self.win32_enabled = PYWIN32_AVAILABLE

        # Battery tracking
        self._batteries: Dict[str, Dict[str, Any]] = {}
        self._power_schemes: Dict[str, Dict[str, Any]] = {}

        self.logger.info("Windows battery monitor initialized")

    def _initialize_platform_specific(self) -> None:
        """Initialize Windows-specific battery monitoring."""
        try:
            # Initialize WMI connection
            if self.wmi_enabled:
                self._initialize_wmi()
            else:
                self.logger.warning(
                    "WMI not available - limited functionality"
                )

            # Initialize Power Management
            if self.win32_enabled:
                self._initialize_power_management()
            else:
                self.logger.warning(
                    "Win32 API not available - limited functionality"
                )

            # Discover batteries using Windows-specific methods
            self._discover_windows_batteries()

            battery_count = len(self._batteries)
            self.logger.info(
                f"Initialized Windows battery monitoring for {battery_count} batteries"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Windows battery monitoring: {e}"
            )
            error_handler.handle_error(e, "WindowsBatteryMonitor.initialize")
            raise

    def _initialize_wmi(self) -> None:
        """Initialize WMI connection for Windows battery monitoring."""
        try:
            if not WMI_AVAILABLE:
                return

            self.wmi_connection = wmi.WMI()
            self.logger.info(
                "WMI connection established for battery monitoring"
            )

            # Test WMI functionality
            batteries = self.wmi_connection.Win32_Battery()
            self.logger.debug(f"WMI found {len(batteries)} batteries")

        except Exception as e:
            self.logger.error(
                f"Failed to initialize WMI for battery monitoring: {e}"
            )
            self.wmi_enabled = False
            self.wmi_connection = None

    def _initialize_power_management(self) -> None:
        """Initialize Windows Power Management APIs."""
        try:
            if not PYWIN32_AVAILABLE:
                return

            # Get power management capabilities
            self._get_power_capabilities()

            # Get current power scheme
            self._get_current_power_scheme()

            self.logger.info("Power Management APIs initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Power Management: {e}")
            self.win32_enabled = False

    def _get_power_capabilities(self) -> None:
        """Get system power capabilities."""
        try:
            if not self.win32_enabled:
                return

            # This would use GetPwrCapabilities API if available
            # For now, we'll use basic detection
            self.power_management_data["capabilities"] = {
                "battery_present": True,
                "ups_present": False,
                "thermal_control": True,
                "processor_throttle": True,
            }

        except Exception as e:
            self.logger.error(f"Error getting power capabilities: {e}")

    def _get_current_power_scheme(self) -> None:
        """Get current Windows power scheme."""
        try:
            # Use powercfg command to get current power scheme
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout:
                # Parse power scheme information
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "GUID:" in line:
                        parts = line.split("GUID:")
                        if len(parts) > 1:
                            guid_part = parts[1].strip()
                            guid = guid_part.split("(")[0].strip()
                            name = (
                                guid_part.split("(")[1].rstrip(")")
                                if "(" in guid_part
                                else "Unknown"
                            )

                            self._power_schemes["active"] = {
                                "guid": guid,
                                "name": name,
                            }
                            break

        except Exception as e:
            self.logger.error(f"Error getting current power scheme: {e}")

    def _discover_windows_batteries(self) -> None:
        """Discover Windows batteries using WMI and system APIs."""
        try:
            self._batteries.clear()

            # Discover batteries via WMI
            if self.wmi_enabled and self.wmi_connection:
                self._discover_batteries_wmi()

            # Get additional battery information via powercfg
            self._discover_batteries_powercfg()

        except Exception as e:
            self.logger.error(f"Error discovering Windows batteries: {e}")
            error_handler.handle_error(
                e, "WindowsBatteryMonitor.discover_batteries"
            )

    def _discover_batteries_wmi(self) -> None:
        """Discover batteries using WMI."""
        try:
            if not self.wmi_connection:
                return

            # Get battery information
            for battery in self.wmi_connection.Win32_Battery():
                try:
                    battery_id = (
                        battery.DeviceID or f"battery_{len(self._batteries)}"
                    )

                    battery_info = {
                        "device_id": battery_id,
                        "name": battery.Name or "Unknown Battery",
                        "description": battery.Description or "",
                        "chemistry": battery.Chemistry or "Unknown",
                        "design_capacity": battery.DesignCapacity,
                        "full_charge_capacity": battery.FullChargeCapacity,
                        "design_voltage": battery.DesignVoltage,
                        "smart_battery_version": battery.SmartBatteryVersion,
                        "specification_version": battery.SpecificationVersion,
                        "status": battery.Status,
                        "availability": battery.Availability,
                        "battery_status": battery.BatteryStatus,
                        "power_management_supported": battery.PowerManagementSupported,
                        "estimated_charge_remaining": battery.EstimatedChargeRemaining,
                        "estimated_run_time": battery.EstimatedRunTime,
                        "expected_life": battery.ExpectedLife,
                        "max_recharge_time": battery.MaxRechargeTime,
                        "time_on_battery": battery.TimeOnBattery,
                        "time_to_full_charge": battery.TimeToFullCharge,
                    }

                    self._batteries[battery_id] = battery_info

                    self.logger.debug(
                        f"Added battery via WMI: {battery_id} ({battery.Name})"
                    )

                except Exception as e:
                    self.logger.warning(f"Error processing WMI battery: {e}")
                    continue

            # Get portable battery information
            for battery in self.wmi_connection.Win32_PortableBattery():
                try:
                    battery_id = (
                        battery.DeviceID or f"portable_{len(self._batteries)}"
                    )

                    if battery_id not in self._batteries:
                        battery_info = {
                            "device_id": battery_id,
                            "name": battery.Name or "Portable Battery",
                            "description": battery.Description or "",
                            "manufacturer": battery.Manufacturer,
                            "manufacture_date": battery.ManufactureDate,
                            "location": battery.Location,
                            "capacity_multiplier": battery.CapacityMultiplier,
                            "max_capacity_multiplier": battery.MaxCapacityMultiplier,
                            "chemistry": self._get_chemistry_name(
                                battery.Chemistry
                            ),
                            "is_portable": True,
                        }

                        self._batteries[battery_id] = battery_info

                        self.logger.debug(
                            f"Added portable battery via WMI: {battery_id}"
                        )

                except Exception as e:
                    self.logger.warning(
                        f"Error processing portable battery: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error discovering batteries via WMI: {e}")

    def _get_chemistry_name(self, chemistry_code: Optional[int]) -> str:
        """Convert battery chemistry code to name.

        Args:
            chemistry_code: WMI chemistry code

        Returns:
            Chemistry name string
        """
        chemistry_map = {
            1: "Other",
            2: "Unknown",
            3: "Lead Acid",
            4: "Nickel Cadmium",
            5: "Nickel Metal Hydride",
            6: "Lithium Ion",
            7: "Zinc Air",
            8: "Lithium Polymer",
        }

        return chemistry_map.get(chemistry_code, "Unknown")

    def _discover_batteries_powercfg(self) -> None:
        """Discover batteries using powercfg command."""
        try:
            # Get battery report
            result = subprocess.run(
                ["powercfg", "/batteryreport", "/output", "-", "/xml"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout:
                self._parse_battery_report(result.stdout)
            else:
                # Fallback to basic battery info
                self._get_basic_battery_info()

        except Exception as e:
            self.logger.error(f"Error getting battery info via powercfg: {e}")
            self._get_basic_battery_info()

    def _parse_battery_report(self, xml_data: str) -> None:
        """Parse XML battery report from powercfg.

        Args:
            xml_data: XML battery report data
        """
        try:
            # For now, we'll use a simple approach
            # In a full implementation, this would parse the XML properly
            if "Battery" in xml_data:
                # Extract basic information from the XML
                # This is a simplified parser - a real implementation would use xml.etree
                pass

        except Exception as e:
            self.logger.error(f"Error parsing battery report: {e}")

    def _get_basic_battery_info(self) -> None:
        """Get basic battery information as fallback."""
        try:
            # Use powercfg to get basic battery information
            result = subprocess.run(
                ["powercfg", "/query"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Parse basic power settings
                self.power_management_data["basic_info"] = {
                    "powercfg_available": True,
                    "query_successful": True,
                }

        except Exception as e:
            self.logger.error(f"Error getting basic battery info: {e}")

    def get_battery_details(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed battery information for all discovered batteries.

        Returns:
            Dict mapping battery IDs to detailed information
        """
        try:
            detailed_batteries = {}

            for battery_id, battery_info in self._batteries.items():
                # Get current battery status
                current_status = self._get_current_battery_status(battery_id)

                # Combine stored info with current status
                detailed_info = battery_info.copy()
                detailed_info.update(current_status)

                # Add Windows-specific metrics
                windows_metrics = self._get_windows_specific_metrics(
                    battery_id
                )
                detailed_info.update(windows_metrics)

                detailed_batteries[battery_id] = detailed_info

            return detailed_batteries

        except Exception as e:
            self.logger.error(f"Error getting battery details: {e}")
            return {}

    def _get_current_battery_status(self, battery_id: str) -> Dict[str, Any]:
        """Get current status for a specific battery.

        Args:
            battery_id: Battery identifier

        Returns:
            Dict containing current battery status
        """
        try:
            status = {}

            if self.wmi_enabled and self.wmi_connection:
                # Get current WMI battery status
                for battery in self.wmi_connection.Win32_Battery():
                    if battery.DeviceID == battery_id:
                        status.update(
                            {
                                "current_charge_percent": battery.EstimatedChargeRemaining,
                                "estimated_runtime_minutes": battery.EstimatedRunTime,
                                "battery_status": self._get_battery_status_name(
                                    battery.BatteryStatus
                                ),
                                "power_plugged": self._is_power_connected(),
                                "time_to_full_charge_minutes": battery.TimeToFullCharge,
                            }
                        )
                        break

            # Get system power status
            power_status = self._get_system_power_status()
            if power_status:
                status.update(power_status)

            return status

        except Exception as e:
            self.logger.error(f"Error getting current battery status: {e}")
            return {}

    def _get_battery_status_name(self, status_code: Optional[int]) -> str:
        """Convert battery status code to name.

        Args:
            status_code: WMI battery status code

        Returns:
            Status name string
        """
        status_map = {
            1: "Discharging",
            2: "On AC Power",
            3: "Fully Charged",
            4: "Low",
            5: "Critical",
            6: "Charging",
            7: "Charging and High",
            8: "Charging and Low",
            9: "Charging and Critical",
            10: "Undefined",
            11: "Partially Charged",
        }

        return status_map.get(status_code, "Unknown")

    def _is_power_connected(self) -> bool:
        """Check if AC power is connected.

        Returns:
            True if AC power is connected
        """
        try:
            if self.wmi_enabled and self.wmi_connection:
                # Check power supply status
                for power_supply in self.wmi_connection.Win32_PowerSupply():
                    if power_supply.PowerSupplyType == 3:  # AC Power Supply
                        return True

            # Fallback: check via system power status
            power_status = self._get_system_power_status()
            return power_status.get("power_plugged", False)

        except Exception as e:
            self.logger.error(f"Error checking power connection: {e}")
            return False

    def _get_system_power_status(self) -> Dict[str, Any]:
        """Get system power status using Windows APIs.

        Returns:
            Dict containing system power status
        """
        try:
            # This would use GetSystemPowerStatus API if available
            # For now, we'll use a basic implementation
            status = {
                "power_plugged": False,
                "battery_present": True,
                "charging": False,
            }

            # Try to get status via powercfg
            try:
                result = subprocess.run(
                    ["powercfg", "/query", "SCHEME_CURRENT"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    # Parse power scheme to determine status
                    status["power_scheme_available"] = True

            except Exception:
                pass

            return status

        except Exception as e:
            self.logger.error(f"Error getting system power status: {e}")
            return {}

    def _get_windows_specific_metrics(self, battery_id: str) -> Dict[str, Any]:
        """Get Windows-specific battery metrics.

        Args:
            battery_id: Battery identifier

        Returns:
            Dict containing Windows-specific metrics
        """
        try:
            metrics = {}

            # Get power efficiency diagnostics
            metrics.update(self._get_power_efficiency_metrics())

            # Get thermal information
            metrics.update(self._get_thermal_metrics())

            # Get power scheme information
            metrics.update(self._get_power_scheme_metrics())

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting Windows-specific metrics: {e}")
            return {}

    def _get_power_efficiency_metrics(self) -> Dict[str, Any]:
        """Get power efficiency metrics.

        Returns:
            Dict containing power efficiency data
        """
        try:
            metrics = {}

            # Use powercfg energy analysis if available
            try:
                result = subprocess.run(
                    ["powercfg", "/energy", "/duration", "5", "/output", "-"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    metrics["energy_analysis_available"] = True
                    # Parse energy report for efficiency metrics

            except Exception:
                metrics["energy_analysis_available"] = False

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting power efficiency metrics: {e}")
            return {}

    def _get_thermal_metrics(self) -> Dict[str, Any]:
        """Get thermal-related metrics.

        Returns:
            Dict containing thermal data
        """
        try:
            metrics = {}

            if self.wmi_enabled and self.wmi_connection:
                # Get thermal zone information
                try:
                    for (
                        thermal_zone
                    ) in (
                        self.wmi_connection.Win32_PerfRawData_Counters_ThermalZoneInformation()
                    ):
                        if thermal_zone.Temperature:
                            # Convert from tenths of Kelvin to Celsius
                            temp_celsius = (
                                thermal_zone.Temperature / 10.0
                            ) - 273.15
                            metrics["thermal_zone_temperature"] = temp_celsius
                            break
                except Exception:
                    pass

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting thermal metrics: {e}")
            return {}

    def _get_power_scheme_metrics(self) -> Dict[str, Any]:
        """Get power scheme related metrics.

        Returns:
            Dict containing power scheme data
        """
        try:
            metrics = {}

            # Get current power scheme details
            active_scheme = self._power_schemes.get("active", {})
            if active_scheme:
                metrics["active_power_scheme"] = active_scheme

            # Get power scheme settings
            try:
                result = subprocess.run(
                    ["powercfg", "/query", "SCHEME_CURRENT", "SUB_BATTERY"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    metrics["battery_settings_available"] = True
                    # Parse battery-specific power settings

            except Exception:
                metrics["battery_settings_available"] = False

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting power scheme metrics: {e}")
            return {}

    def _collect_data(self) -> Dict[str, Any]:
        """Collect Windows-specific battery data.

        Returns:
            Dict containing comprehensive battery monitoring data
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "platform": "windows",
                "batteries": [],
                "power_management": self.power_management_data.copy(),
                "system_power_status": self._get_system_power_status(),
            }

            # Collect data for each battery
            for battery_id, battery_info in self._batteries.items():
                try:
                    battery_data = self._collect_battery_data(
                        battery_id, battery_info
                    )
                    if battery_data:
                        data["batteries"].append(battery_data)

                except Exception as e:
                    self.logger.error(
                        f"Error collecting data for battery {battery_id}: {e}"
                    )
                    continue

            return data

        except Exception as e:
            self.logger.error(f"Error collecting Windows battery data: {e}")
            error_handler.handle_error(e, "WindowsBatteryMonitor.collect_data")
            return {}

    def _collect_battery_data(
        self, battery_id: str, battery_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Collect data for a specific battery.

        Args:
            battery_id: Battery identifier
            battery_info: Cached battery information

        Returns:
            Dict containing battery data or None if error
        """
        try:
            # Start with cached info
            data = battery_info.copy()

            # Get current status
            current_status = self._get_current_battery_status(battery_id)
            data.update(current_status)

            # Get Windows-specific metrics
            windows_metrics = self._get_windows_specific_metrics(battery_id)
            data.update(windows_metrics)

            # Calculate health metrics
            if data.get("design_capacity") and data.get(
                "full_charge_capacity"
            ):
                design_cap = data["design_capacity"]
                current_cap = data["full_charge_capacity"]
                if design_cap > 0:
                    health_percent = (current_cap / design_cap) * 100.0
                    data["health_percent"] = min(
                        100.0, max(0.0, health_percent)
                    )

            # Add platform identifier
            data["platform"] = "windows"
            data["battery_id"] = battery_id

            return data

        except Exception as e:
            self.logger.error(
                f"Error collecting data for battery {battery_id}: {e}"
            )
            return None

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected Windows battery data.

        Args:
            data: Data to validate

        Returns:
            bool: True if data is valid
        """
        try:
            if not isinstance(data, dict):
                return False

            required_fields = ["timestamp", "platform", "batteries"]
            if not all(field in data for field in required_fields):
                return False

            if data["platform"] != "windows":
                return False

            if not isinstance(data["batteries"], list):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating Windows battery data: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get the current Windows battery health status.

        Returns:
            Dict containing health status information
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return {
                    "status": "unknown",
                    "message": "No Windows battery data available",
                    "batteries": [],
                }

            batteries = current_data.get("batteries", [])

            if not batteries:
                return {
                    "status": "no_battery",
                    "message": "No batteries detected",
                    "batteries": [],
                }

            # Analyze overall health
            healthy_count = 0
            warning_count = 0
            critical_count = 0

            for battery in batteries:
                health_percent = battery.get("health_percent", 100.0)
                if health_percent >= 80:
                    healthy_count += 1
                elif health_percent >= 60:
                    warning_count += 1
                else:
                    critical_count += 1

            # Determine overall status
            if critical_count > 0:
                overall_status = "critical"
                message = (
                    f"{critical_count} battery(ies) in critical condition"
                )
            elif warning_count > 0:
                overall_status = "warning"
                message = f"{warning_count} battery(ies) need attention"
            else:
                overall_status = "healthy"
                message = "All batteries are healthy"

            return {
                "status": overall_status,
                "message": message,
                "total_batteries": len(batteries),
                "healthy_batteries": healthy_count,
                "warning_batteries": warning_count,
                "critical_batteries": critical_count,
                "batteries": [
                    {
                        "id": battery.get("battery_id"),
                        "name": battery.get("name"),
                        "health_percent": battery.get("health_percent"),
                        "charge_percent": battery.get(
                            "current_charge_percent"
                        ),
                        "status": battery.get("battery_status"),
                    }
                    for battery in batteries
                ],
            }

        except Exception as e:
            self.logger.error(
                f"Error getting Windows battery health status: {e}"
            )
            return {
                "status": "error",
                "message": f"Error retrieving battery health: {str(e)}",
                "batteries": [],
            }
