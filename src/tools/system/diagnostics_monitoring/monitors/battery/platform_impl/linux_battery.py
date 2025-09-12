"""Linux-specific battery monitoring with /sys/class/power_supply and upower."""

import os
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class LinuxBatteryMonitor(MonitorBase):
    """Linux-specific battery monitoring with enhanced capabilities."""
    
    def __init__(self, update_interval: float = 60.0):
        """Initialize Linux battery monitor.
        
        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("LinuxBatteryHealth", update_interval)
        
        # Linux-specific components
        self.sysfs_available = True
        self.upower_available = True
        self.acpi_available = True
        
        # Battery tracking
        self._batteries: Dict[str, Dict[str, Any]] = {}
        self._power_supplies: Dict[str, Dict[str, Any]] = {}
        
        # System paths
        self.power_supply_path = "/sys/class/power_supply"
        self.acpi_battery_path = "/proc/acpi/battery"
        
        self.logger.info("Linux battery monitor initialized")
    
    def _initialize_platform_specific(self) -> None:
        """Initialize Linux-specific battery monitoring."""
        try:
            # Check tool and interface availability
            self._check_interface_availability()
            
            # Discover batteries using Linux-specific methods
            self._discover_linux_batteries()
            
            battery_count = len(self._batteries)
            self.logger.info(
                f"Initialized Linux battery monitoring for {battery_count} batteries"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Linux battery monitoring: {e}")
            error_handler.handle_error(e, "LinuxBatteryMonitor.initialize")
            raise
    
    def _check_interface_availability(self) -> None:
        """Check availability of Linux battery monitoring interfaces."""
        try:
            # Check sysfs power_supply interface
            self.sysfs_available = os.path.exists(self.power_supply_path)
            
            # Check upower
            try:
                result = subprocess.run(
                    ['upower', '--version'],
                    capture_output=True,
                    timeout=5
                )
                self.upower_available = result.returncode == 0
            except Exception:
                self.upower_available = False
            
            # Check ACPI interface
            self.acpi_available = os.path.exists(self.acpi_battery_path)
            
            self.logger.info(
                f"Interface availability - sysfs: {self.sysfs_available}, "
                f"upower: {self.upower_available}, acpi: {self.acpi_available}"
            )
            
        except Exception as e:
            self.logger.error(f"Error checking interface availability: {e}")
    
    def _discover_linux_batteries(self) -> None:
        """Discover Linux batteries using system interfaces."""
        try:
            self._batteries.clear()
            self._power_supplies.clear()
            
            # Discover batteries via sysfs
            if self.sysfs_available:
                self._discover_batteries_sysfs()
            
            # Discover batteries via upower
            if self.upower_available:
                self._discover_batteries_upower()
            
            # Discover batteries via ACPI
            if self.acpi_available:
                self._discover_batteries_acpi()
            
        except Exception as e:
            self.logger.error(f"Error discovering Linux batteries: {e}")
            error_handler.handle_error(e, "LinuxBatteryMonitor.discover_batteries")
    
    def _discover_batteries_sysfs(self) -> None:
        """Discover batteries using sysfs interface."""
        try:
            if not os.path.exists(self.power_supply_path):
                return
            
            # Enumerate power supply devices
            for device in os.listdir(self.power_supply_path):
                device_path = os.path.join(self.power_supply_path, device)
                
                if not os.path.isdir(device_path):
                    continue
                
                # Check if this is a battery
                type_file = os.path.join(device_path, "type")
                if os.path.exists(type_file):
                    try:
                        with open(type_file, 'r') as f:
                            device_type = f.read().strip()
                        
                        if device_type.lower() == "battery":
                            battery_data = self._read_sysfs_battery_data(device, device_path)
                            if battery_data:
                                self._batteries[device] = battery_data
                                self.logger.debug(f"Added battery via sysfs: {device}")
                        else:
                            # Store other power supply info (AC adapters, etc.)
                            supply_data = self._read_sysfs_supply_data(device, device_path)
                            if supply_data:
                                self._power_supplies[device] = supply_data
                                
                    except Exception as e:
                        self.logger.warning(f"Error reading device {device}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error discovering batteries via sysfs: {e}")
    
    def _read_sysfs_battery_data(self, device: str, device_path: str) -> Optional[Dict[str, Any]]:
        """Read battery data from sysfs.
        
        Args:
            device: Device name
            device_path: Path to device in sysfs
            
        Returns:
            Dict containing battery data or None if error
        """
        try:
            battery_data = {
                'device_id': device,
                'name': device,
                'source': 'sysfs',
                'device_path': device_path
            }
            
            # Read available battery properties
            sysfs_properties = {
                'status': 'status',
                'present': 'present',
                'technology': 'technology',
                'cycle_count': 'cycle_count',
                'voltage_now': 'voltage_now',
                'voltage_min_design': 'voltage_min_design',
                'current_now': 'current_now',
                'charge_now': 'charge_now',
                'charge_full': 'charge_full',
                'charge_full_design': 'charge_full_design',
                'energy_now': 'energy_now',
                'energy_full': 'energy_full',
                'energy_full_design': 'energy_full_design',
                'power_now': 'power_now',
                'capacity': 'capacity',
                'capacity_level': 'capacity_level',
                'temp': 'temp',
                'manufacturer': 'manufacturer',
                'model_name': 'model_name',
                'serial_number': 'serial_number'
            }
            
            for prop_name, file_name in sysfs_properties.items():
                file_path = os.path.join(device_path, file_name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            value = f.read().strip()
                        
                        # Convert numeric values
                        if prop_name in ['voltage_now', 'voltage_min_design', 'current_now',
                                       'charge_now', 'charge_full', 'charge_full_design',
                                       'energy_now', 'energy_full', 'energy_full_design',
                                       'power_now', 'capacity', 'cycle_count', 'temp']:
                            try:
                                battery_data[prop_name] = int(value)
                            except ValueError:
                                battery_data[prop_name] = value
                        else:
                            battery_data[prop_name] = value
                            
                    except Exception as e:
                        self.logger.debug(f"Error reading {file_name}: {e}")
                        continue
            
            # Calculate derived values
            self._calculate_sysfs_derived_values(battery_data)
            
            return battery_data
            
        except Exception as e:
            self.logger.error(f"Error reading sysfs battery data for {device}: {e}")
            return None
    
    def _calculate_sysfs_derived_values(self, battery_data: Dict[str, Any]) -> None:
        """Calculate derived values from sysfs data.
        
        Args:
            battery_data: Battery data dictionary to update
        """
        try:
            # Calculate health percentage
            if 'charge_full' in battery_data and 'charge_full_design' in battery_data:
                charge_full = battery_data['charge_full']
                charge_full_design = battery_data['charge_full_design']
                if charge_full_design > 0:
                    health_percent = (charge_full / charge_full_design) * 100.0
                    battery_data['health_percent'] = min(100.0, max(0.0, health_percent))
            
            elif 'energy_full' in battery_data and 'energy_full_design' in battery_data:
                energy_full = battery_data['energy_full']
                energy_full_design = battery_data['energy_full_design']
                if energy_full_design > 0:
                    health_percent = (energy_full / energy_full_design) * 100.0
                    battery_data['health_percent'] = min(100.0, max(0.0, health_percent))
            
            # Convert temperature from decidegrees to Celsius
            if 'temp' in battery_data:
                temp = battery_data['temp']
                if isinstance(temp, int) and temp > 100:
                    battery_data['temperature_celsius'] = temp / 10.0
                else:
                    battery_data['temperature_celsius'] = temp
            
            # Convert voltages from microvolts to volts
            for voltage_field in ['voltage_now', 'voltage_min_design']:
                if voltage_field in battery_data:
                    voltage_uv = battery_data[voltage_field]
                    if isinstance(voltage_uv, int) and voltage_uv > 100000:
                        battery_data[f"{voltage_field}_volts"] = voltage_uv / 1000000.0
            
            # Convert current from microamps to amps
            if 'current_now' in battery_data:
                current_ua = battery_data['current_now']
                if isinstance(current_ua, int):
                    battery_data['current_now_amps'] = current_ua / 1000000.0
            
            # Convert power from microwatts to watts
            if 'power_now' in battery_data:
                power_uw = battery_data['power_now']
                if isinstance(power_uw, int):
                    battery_data['power_now_watts'] = power_uw / 1000000.0
            
            # Determine charging status
            status = battery_data.get('status', '').lower()
            battery_data['is_charging'] = status == 'charging'
            battery_data['is_discharging'] = status == 'discharging'
            battery_data['is_full'] = status == 'full'
            
        except Exception as e:
            self.logger.error(f"Error calculating derived values: {e}")
    
    def _read_sysfs_supply_data(self, device: str, device_path: str) -> Optional[Dict[str, Any]]:
        """Read power supply data from sysfs.
        
        Args:
            device: Device name
            device_path: Path to device in sysfs
            
        Returns:
            Dict containing power supply data or None if error
        """
        try:
            supply_data = {
                'device_id': device,
                'name': device,
                'source': 'sysfs',
                'device_path': device_path
            }
            
            # Read basic properties
            basic_properties = ['type', 'online', 'present']
            
            for prop in basic_properties:
                file_path = os.path.join(device_path, prop)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            value = f.read().strip()
                        
                        if prop in ['online', 'present']:
                            supply_data[prop] = value == '1'
                        else:
                            supply_data[prop] = value
                            
                    except Exception:
                        continue
            
            return supply_data
            
        except Exception as e:
            self.logger.error(f"Error reading sysfs supply data for {device}: {e}")
            return None
    
    def _discover_batteries_upower(self) -> None:
        """Discover batteries using upower."""
        try:
            if not self.upower_available:
                return
            
            # Get list of power devices
            result = subprocess.run(
                ['upower', '-e'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return
            
            devices = result.stdout.strip().split('\n')
            
            for device in devices:
                if 'BAT' in device or 'battery' in device.lower():
                    battery_data = self._get_upower_battery_data(device)
                    if battery_data:
                        device_id = f"upower_{os.path.basename(device)}"
                        
                        # Merge with existing sysfs data if available
                        sysfs_device = os.path.basename(device)
                        if sysfs_device in self._batteries:
                            self._batteries[sysfs_device].update(battery_data)
                        else:
                            self._batteries[device_id] = battery_data
                        
                        self.logger.debug(f"Added/updated battery via upower: {device_id}")
                        
        except Exception as e:
            self.logger.error(f"Error discovering batteries via upower: {e}")
    
    def _get_upower_battery_data(self, device_path: str) -> Optional[Dict[str, Any]]:
        """Get battery data from upower.
        
        Args:
            device_path: UPower device path
            
        Returns:
            Dict containing battery data or None if error
        """
        try:
            result = subprocess.run(
                ['upower', '-i', device_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            battery_data = {
                'device_path': device_path,
                'source': 'upower'
            }
            
            # Parse upower output
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_').replace('-', '_')
                    value = value.strip()
                    
                    # Convert specific values
                    if key in ['percentage']:
                        try:
                            battery_data['capacity_percent'] = float(value.rstrip('%'))
                        except ValueError:
                            pass
                    elif key in ['energy', 'energy_full', 'energy_full_design']:
                        try:
                            # Parse energy values (e.g., "50.23 Wh")
                            if 'Wh' in value:
                                energy_wh = float(value.split()[0])
                                battery_data[f"{key}_wh"] = energy_wh
                        except ValueError:
                            pass
                    elif key in ['voltage']:
                        try:
                            # Parse voltage values (e.g., "12.5 V")
                            if 'V' in value:
                                voltage_v = float(value.split()[0])
                                battery_data[f"{key}_volts"] = voltage_v
                        except ValueError:
                            pass
                    elif key in ['state']:
                        battery_data['charging_state'] = value
                        battery_data['is_charging'] = 'charging' in value.lower()
                    elif key in ['technology', 'model', 'vendor', 'serial']:
                        battery_data[key] = value
                    elif 'time' in key:
                        battery_data[key] = value
            
            return battery_data
            
        except Exception as e:
            self.logger.error(f"Error getting upower battery data: {e}")
            return None
    
    def _discover_batteries_acpi(self) -> None:
        """Discover batteries using ACPI interface."""
        try:
            if not self.acpi_available:
                return
            
            # Read ACPI battery information
            for battery_dir in os.listdir(self.acpi_battery_path):
                battery_path = os.path.join(self.acpi_battery_path, battery_dir)
                
                if os.path.isdir(battery_path):
                    battery_data = self._read_acpi_battery_data(battery_dir, battery_path)
                    if battery_data:
                        device_id = f"acpi_{battery_dir}"
                        
                        # Merge with existing data if available
                        if battery_dir in self._batteries:
                            self._batteries[battery_dir].update(battery_data)
                        else:
                            self._batteries[device_id] = battery_data
                        
                        self.logger.debug(f"Added/updated battery via ACPI: {device_id}")
                        
        except Exception as e:
            self.logger.error(f"Error discovering batteries via ACPI: {e}")
    
    def _read_acpi_battery_data(self, battery_name: str, battery_path: str) -> Optional[Dict[str, Any]]:
        """Read battery data from ACPI interface.
        
        Args:
            battery_name: Battery name
            battery_path: Path to battery in ACPI
            
        Returns:
            Dict containing battery data or None if error
        """
        try:
            battery_data = {
                'device_id': battery_name,
                'name': battery_name,
                'source': 'acpi',
                'acpi_path': battery_path
            }
            
            # Read battery info
            info_file = os.path.join(battery_path, "info")
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace(' ', '_')
                            value = value.strip()
                            
                            if key in ['design_capacity', 'last_full_capacity']:
                                try:
                                    # Parse capacity (e.g., "4400 mAh")
                                    if 'mAh' in value:
                                        capacity = int(value.split()[0])
                                        battery_data[key] = capacity
                                except ValueError:
                                    pass
                            else:
                                battery_data[key] = value
            
            # Read battery state
            state_file = os.path.join(battery_path, "state")
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace(' ', '_')
                            value = value.strip()
                            
                            if key == 'charging_state':
                                battery_data['acpi_charging_state'] = value
                                battery_data['is_charging'] = 'charging' in value.lower()
                            elif key in ['present_rate', 'remaining_capacity', 'present_voltage']:
                                try:
                                    # Parse numeric values
                                    numeric_value = int(value.split()[0])
                                    battery_data[key] = numeric_value
                                except ValueError:
                                    pass
                            else:
                                battery_data[key] = value
            
            return battery_data
            
        except Exception as e:
            self.logger.error(f"Error reading ACPI battery data: {e}")
            return None
    
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
                
                # Add Linux-specific metrics
                linux_metrics = self._get_linux_specific_metrics(battery_id)
                detailed_info.update(linux_metrics)
                
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
            
            # Update from sysfs if available
            if self.sysfs_available:
                sysfs_status = self._get_sysfs_current_status(battery_id)
                status.update(sysfs_status)
            
            # Update from upower if available
            if self.upower_available:
                upower_status = self._get_upower_current_status(battery_id)
                status.update(upower_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting current battery status: {e}")
            return {}
    
    def _get_sysfs_current_status(self, battery_id: str) -> Dict[str, Any]:
        """Get current battery status from sysfs.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing current sysfs status
        """
        try:
            # Find the actual device name
            device_name = battery_id.replace('upower_', '').replace('acpi_', '')
            device_path = os.path.join(self.power_supply_path, device_name)
            
            if not os.path.exists(device_path):
                return {}
            
            # Re-read current values
            current_data = self._read_sysfs_battery_data(device_name, device_path)
            if current_data:
                return {
                    'current_capacity_percent': current_data.get('capacity'),
                    'current_status': current_data.get('status'),
                    'current_voltage': current_data.get('voltage_now_volts'),
                    'current_power': current_data.get('power_now_watts'),
                    'current_temperature': current_data.get('temperature_celsius'),
                    'is_charging': current_data.get('is_charging', False),
                    'is_present': current_data.get('present') == '1'
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting sysfs current status: {e}")
            return {}
    
    def _get_upower_current_status(self, battery_id: str) -> Dict[str, Any]:
        """Get current battery status from upower.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing current upower status
        """
        try:
            if not self.upower_available:
                return {}
            
            # Find corresponding upower device
            battery_info = self._batteries.get(battery_id, {})
            device_path = battery_info.get('device_path')
            
            if not device_path:
                # Try to find device by name
                device_name = battery_id.replace('upower_', '')
                device_path = f"/org/freedesktop/UPower/devices/battery_{device_name}"
            
            if device_path:
                current_data = self._get_upower_battery_data(device_path)
                if current_data:
                    return {
                        'upower_capacity_percent': current_data.get('capacity_percent'),
                        'upower_charging_state': current_data.get('charging_state'),
                        'upower_energy_wh': current_data.get('energy_wh'),
                        'upower_voltage': current_data.get('voltage_volts'),
                        'is_charging': current_data.get('is_charging', False)
                    }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting upower current status: {e}")
            return {}
    
    def _get_linux_specific_metrics(self, battery_id: str) -> Dict[str, Any]:
        """Get Linux-specific battery metrics.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing Linux-specific metrics
        """
        try:
            metrics = {}
            
            # Add power supply information
            metrics['power_supplies'] = self._power_supplies
            
            # Add system power information
            metrics.update(self._get_system_power_info())
            
            # Add thermal information
            metrics.update(self._get_thermal_info())
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting Linux-specific metrics: {e}")
            return {}
    
    def _get_system_power_info(self) -> Dict[str, Any]:
        """Get system power information.
        
        Returns:
            Dict containing system power data
        """
        try:
            power_info = {}
            
            # Check for AC adapter status
            ac_online = False
            for supply_id, supply_data in self._power_supplies.items():
                if supply_data.get('type', '').lower() in ['mains', 'ac']:
                    if supply_data.get('online', False):
                        ac_online = True
                        break
            
            power_info['ac_adapter_online'] = ac_online
            
            # Get system power state information
            try:
                with open('/sys/power/state', 'r') as f:
                    power_states = f.read().strip().split()
                    power_info['available_power_states'] = power_states
            except Exception:
                pass
            
            return power_info
            
        except Exception as e:
            self.logger.error(f"Error getting system power info: {e}")
            return {}
    
    def _get_thermal_info(self) -> Dict[str, Any]:
        """Get thermal information.
        
        Returns:
            Dict containing thermal data
        """
        try:
            thermal_info = {}
            
            # Read thermal zone information
            thermal_path = "/sys/class/thermal"
            if os.path.exists(thermal_path):
                thermal_zones = []
                
                for zone in os.listdir(thermal_path):
                    if zone.startswith('thermal_zone'):
                        zone_path = os.path.join(thermal_path, zone)
                        temp_file = os.path.join(zone_path, 'temp')
                        type_file = os.path.join(zone_path, 'type')
                        
                        if os.path.exists(temp_file) and os.path.exists(type_file):
                            try:
                                with open(temp_file, 'r') as f:
                                    temp_millicelsius = int(f.read().strip())
                                with open(type_file, 'r') as f:
                                    zone_type = f.read().strip()
                                
                                thermal_zones.append({
                                    'zone': zone,
                                    'type': zone_type,
                                    'temperature_celsius': temp_millicelsius / 1000.0
                                })
                                
                            except Exception:
                                continue
                
                thermal_info['thermal_zones'] = thermal_zones
            
            return thermal_info
            
        except Exception as e:
            self.logger.error(f"Error getting thermal info: {e}")
            return {}
    
    def _collect_data(self) -> Dict[str, Any]:
        """Collect Linux-specific battery data.
        
        Returns:
            Dict containing comprehensive battery monitoring data
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'platform': 'linux',
                'batteries': [],
                'power_supplies': list(self._power_supplies.values()),
                'interface_availability': {
                    'sysfs': self.sysfs_available,
                    'upower': self.upower_available,
                    'acpi': self.acpi_available
                }
            }
            
            # Collect data for each battery
            for battery_id, battery_info in self._batteries.items():
                try:
                    battery_data = self._collect_battery_data(battery_id, battery_info)
                    if battery_data:
                        data['batteries'].append(battery_data)
                        
                except Exception as e:
                    self.logger.error(
                        f"Error collecting data for battery {battery_id}: {e}"
                    )
                    continue
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting Linux battery data: {e}")
            error_handler.handle_error(e, "LinuxBatteryMonitor.collect_data")
            return {}
    
    def _collect_battery_data(
        self, 
        battery_id: str, 
        battery_info: Dict[str, Any]
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
            
            # Get Linux-specific metrics
            linux_metrics = self._get_linux_specific_metrics(battery_id)
            data.update(linux_metrics)
            
            # Ensure health percentage is calculated
            if 'health_percent' not in data:
                # Try different capacity combinations
                if 'charge_full' in data and 'charge_full_design' in data:
                    charge_full = data['charge_full']
                    charge_full_design = data['charge_full_design']
                    if charge_full_design > 0:
                        health_percent = (charge_full / charge_full_design) * 100.0
                        data['health_percent'] = min(100.0, max(0.0, health_percent))
            
            # Add platform identifier
            data['platform'] = 'linux'
            data['battery_id'] = battery_id
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting data for battery {battery_id}: {e}")
            return None
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected Linux battery data.
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if data is valid
        """
        try:
            if not isinstance(data, dict):
                return False
            
            required_fields = ['timestamp', 'platform', 'batteries']
            if not all(field in data for field in required_fields):
                return False
            
            if data['platform'] != 'linux':
                return False
            
            if not isinstance(data['batteries'], list):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating Linux battery data: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current Linux battery health status.
        
        Returns:
            Dict containing health status information
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return {
                    'status': 'unknown',
                    'message': 'No Linux battery data available',
                    'batteries': []
                }
            
            batteries = current_data.get('batteries', [])
            
            if not batteries:
                return {
                    'status': 'no_battery',
                    'message': 'No batteries detected',
                    'batteries': []
                }
            
            # Analyze overall health
            healthy_count = 0
            warning_count = 0
            critical_count = 0
            
            for battery in batteries:
                health_percent = battery.get('health_percent', 100.0)
                cycle_count = battery.get('cycle_count', 0)
                
                # Linux-specific health assessment
                if health_percent >= 80 and cycle_count < 1000:
                    healthy_count += 1
                elif health_percent >= 60 and cycle_count < 1200:
                    warning_count += 1
                else:
                    critical_count += 1
            
            # Determine overall status
            if critical_count > 0:
                overall_status = 'critical'
                message = f"{critical_count} battery(ies) in critical condition"
            elif warning_count > 0:
                overall_status = 'warning'
                message = f"{warning_count} battery(ies) need attention"
            else:
                overall_status = 'healthy'
                message = "All batteries are healthy"
            
            return {
                'status': overall_status,
                'message': message,
                'total_batteries': len(batteries),
                'healthy_batteries': healthy_count,
                'warning_batteries': warning_count,
                'critical_batteries': critical_count,
                'batteries': [
                    {
                        'id': battery.get('battery_id'),
                        'name': battery.get('name'),
                        'health_percent': battery.get('health_percent'),
                        'charge_percent': battery.get('current_capacity_percent'),
                        'cycle_count': battery.get('cycle_count'),
                        'technology': battery.get('technology')
                    }
                    for battery in batteries
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Linux battery health status: {e}")
            return {
                'status': 'error',
                'message': f'Error retrieving battery health: {str(e)}',
                'batteries': []
            }