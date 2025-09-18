"""macOS-specific battery monitoring with IOKit and system_profiler."""

import subprocess
import json
import plistlib
from typing import Dict, Any, Optional
from datetime import datetime

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class MacOSBatteryMonitor(MonitorBase):
    """macOS-specific battery monitoring with enhanced capabilities."""
    
    def __init__(self, update_interval: float = 60.0):
        """Initialize macOS battery monitor.
        
        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("MacOSBatteryHealth", update_interval)
        
        # macOS-specific components
        self.iokit_available = True
        self.system_profiler_available = True
        self.pmset_available = True
        
        # Battery tracking
        self._batteries: Dict[str, Dict[str, Any]] = {}
        self._power_settings: Dict[str, Any] = {}
        
        self.logger.info("macOS battery monitor initialized")
    
    def _initialize_platform_specific(self) -> None:
        """Initialize macOS-specific battery monitoring."""
        try:
            # Check tool availability
            self._check_tool_availability()
            
            # Get power management settings
            self._get_power_management_settings()
            
            # Discover batteries using macOS-specific methods
            self._discover_macos_batteries()
            
            battery_count = len(self._batteries)
            self.logger.info(
                f"Initialized macOS battery monitoring for {battery_count} batteries"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize macOS battery monitoring: {e}")
            error_handler.handle_error(e, "MacOSBatteryMonitor.initialize")
            raise
    
    def _check_tool_availability(self) -> None:
        """Check availability of macOS battery monitoring tools."""
        try:
            # Check system_profiler
            try:
                result = subprocess.run(
                    ['system_profiler', '-help'],
                    capture_output=True,
                    timeout=5
                )
                self.system_profiler_available = result.returncode == 0
            except Exception:
                self.system_profiler_available = False
            
            # Check pmset
            try:
                result = subprocess.run(
                    ['pmset', '-g'],
                    capture_output=True,
                    timeout=5
                )
                self.pmset_available = result.returncode == 0
            except Exception:
                self.pmset_available = False
            
            # Check ioreg (IOKit registry)
            try:
                result = subprocess.run(
                    ['ioreg', '-l'],
                    capture_output=True,
                    timeout=5
                )
                self.iokit_available = result.returncode == 0
            except Exception:
                self.iokit_available = False
            
            self.logger.info(
                f"Tool availability - system_profiler: {self.system_profiler_available}, "
                f"pmset: {self.pmset_available}, ioreg: {self.iokit_available}"
            )
            
        except Exception as e:
            self.logger.error(f"Error checking tool availability: {e}")
    
    def _get_power_management_settings(self) -> None:
        """Get macOS power management settings."""
        try:
            if not self.pmset_available:
                return
            
            # Get current power settings
            result = subprocess.run(
                ['pmset', '-g', 'custom'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self._parse_pmset_settings(result.stdout)
            
            # Get power adapter information
            result = subprocess.run(
                ['pmset', '-g', 'adapter'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self._power_settings['adapter_info'] = result.stdout.strip()
            
        except Exception as e:
            self.logger.error(f"Error getting power management settings: {e}")
    
    def _parse_pmset_settings(self, pmset_output: str) -> None:
        """Parse pmset output for power settings.
        
        Args:
            pmset_output: Output from pmset command
        """
        try:
            settings = {}
            current_profile = None
            
            for line in pmset_output.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.endswith(':'):
                    current_profile = line.rstrip(':')
                    settings[current_profile] = {}
                elif current_profile and ' ' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0]
                        value = ' '.join(parts[1:])
                        settings[current_profile][key] = value
            
            self._power_settings['profiles'] = settings
            
        except Exception as e:
            self.logger.error(f"Error parsing pmset settings: {e}")
    
    def _discover_macos_batteries(self) -> None:
        """Discover macOS batteries using system tools."""
        try:
            self._batteries.clear()
            
            # Discover batteries via system_profiler
            if self.system_profiler_available:
                self._discover_batteries_system_profiler()
            
            # Discover batteries via IOKit registry
            if self.iokit_available:
                self._discover_batteries_ioreg()
            
            # Get additional battery information via pmset
            if self.pmset_available:
                self._discover_batteries_pmset()
            
        except Exception as e:
            self.logger.error(f"Error discovering macOS batteries: {e}")
            error_handler.handle_error(e, "MacOSBatteryMonitor.discover_batteries")
    
    def _discover_batteries_system_profiler(self) -> None:
        """Discover batteries using system_profiler."""
        try:
            result = subprocess.run(
                ['system_profiler', 'SPPowerDataType', '-json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                self._parse_system_profiler_data(data)
            
        except Exception as e:
            self.logger.error(f"Error discovering batteries via system_profiler: {e}")
    
    def _parse_system_profiler_data(self, data: Dict[str, Any]) -> None:
        """Parse system_profiler power data.
        
        Args:
            data: JSON data from system_profiler
        """
        try:
            power_data = data.get('SPPowerDataType', [])
            
            for item in power_data:
                if 'sppower_battery_health_info' in item:
                    battery_info = item['sppower_battery_health_info']
                    battery_id = f"battery_{len(self._batteries)}"
                    
                    battery_data = {
                        'device_id': battery_id,
                        'name': 'Internal Battery',
                        'health_info': battery_info,
                        'source': 'system_profiler'
                    }
                    
                    # Extract specific health metrics
                    if isinstance(battery_info, dict):
                        battery_data.update({
                            'cycle_count': battery_info.get('sppower_battery_cycle_count'),
                            'condition': battery_info.get('sppower_battery_health'),
                            'max_capacity': battery_info.get('sppower_battery_max_capacity'),
                            'charge_remaining': battery_info.get('sppower_battery_charge_remaining')
                        })
                    
                    self._batteries[battery_id] = battery_data
                    
                    self.logger.debug(f"Added battery via system_profiler: {battery_id}")
                
                # Check for AC power adapter information
                if 'sppower_ac_charger_info' in item:
                    charger_info = item['sppower_ac_charger_info']
                    self._power_settings['ac_charger'] = charger_info
                
        except Exception as e:
            self.logger.error(f"Error parsing system_profiler data: {e}")
    
    def _discover_batteries_ioreg(self) -> None:
        """Discover batteries using IOKit registry."""
        try:
            # Get battery information from IOKit
            result = subprocess.run(
                ['ioreg', '-rc', 'AppleSmartBattery'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and result.stdout:
                self._parse_ioreg_battery_data(result.stdout)
            
        except Exception as e:
            self.logger.error(f"Error discovering batteries via ioreg: {e}")
    
    def _parse_ioreg_battery_data(self, ioreg_output: str) -> None:
        """Parse ioreg battery data.
        
        Args:
            ioreg_output: Output from ioreg command
        """
        try:
            # Parse the ioreg output (simplified parsing)
            lines = ioreg_output.split('\n')
            current_battery = None
            battery_data = {}
            
            for line in lines:
                line = line.strip()
                if 'AppleSmartBattery' in line:
                    if current_battery and battery_data:
                        # Store previous battery
                        self._store_ioreg_battery(current_battery, battery_data)
                    
                    # Start new battery
                    current_battery = f"ioreg_battery_{len(self._batteries)}"
                    battery_data = {
                        'device_id': current_battery,
                        'source': 'ioreg',
                        'name': 'Smart Battery'
                    }
                
                elif current_battery and '=' in line:
                    # Parse key-value pairs
                    try:
                        key_part, value_part = line.split('=', 1)
                        key = key_part.strip().strip('"')
                        value = value_part.strip()
                        
                        # Clean up value
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.isdigit():
                            value = int(value)
                        
                        battery_data[key] = value
                        
                    except Exception:
                        continue
            
            # Store last battery
            if current_battery and battery_data:
                self._store_ioreg_battery(current_battery, battery_data)
            
        except Exception as e:
            self.logger.error(f"Error parsing ioreg battery data: {e}")
    
    def _store_ioreg_battery(self, battery_id: str, battery_data: Dict[str, Any]) -> None:
        """Store battery data from ioreg.
        
        Args:
            battery_id: Battery identifier
            battery_data: Battery data from ioreg
        """
        try:
            # Map common IOKit battery properties
            mapped_data = battery_data.copy()
            
            # Map key properties to standard names
            property_map = {
                'DesignCapacity': 'design_capacity',
                'MaxCapacity': 'max_capacity',
                'CurrentCapacity': 'current_capacity',
                'CycleCount': 'cycle_count',
                'Temperature': 'temperature',
                'Voltage': 'voltage',
                'Amperage': 'current',
                'TimeRemaining': 'time_remaining',
                'IsCharging': 'is_charging',
                'ExternalConnected': 'external_connected',
                'FullyCharged': 'fully_charged',
                'BatteryInstalled': 'battery_installed'
            }
            
            for ioreg_key, standard_key in property_map.items():
                if ioreg_key in battery_data:
                    mapped_data[standard_key] = battery_data[ioreg_key]
            
            # Calculate health percentage if possible
            if 'design_capacity' in mapped_data and 'max_capacity' in mapped_data:
                design_cap = mapped_data['design_capacity']
                max_cap = mapped_data['max_capacity']
                if design_cap > 0:
                    health_percent = (max_cap / design_cap) * 100.0
                    mapped_data['health_percent'] = min(100.0, max(0.0, health_percent))
            
            # Convert temperature from decidegrees Celsius to Celsius
            if 'temperature' in mapped_data:
                temp = mapped_data['temperature']
                if isinstance(temp, (int, float)) and temp > 100:
                    mapped_data['temperature'] = temp / 100.0
            
            self._batteries[battery_id] = mapped_data
            
            self.logger.debug(f"Stored ioreg battery: {battery_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing ioreg battery data: {e}")
    
    def _discover_batteries_pmset(self) -> None:
        """Discover batteries using pmset."""
        try:
            # Get battery information
            result = subprocess.run(
                ['pmset', '-g', 'batt'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                self._parse_pmset_battery_data(result.stdout)
            
        except Exception as e:
            self.logger.error(f"Error discovering batteries via pmset: {e}")
    
    def _parse_pmset_battery_data(self, pmset_output: str) -> None:
        """Parse pmset battery data.
        
        Args:
            pmset_output: Output from pmset -g batt
        """
        try:
            lines = pmset_output.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'InternalBattery' in line or 'Battery' in line:
                    # Parse battery status line
                    # Example: "InternalBattery-0 (id=1234567)	100%; charged; 0:00 remaining"
                    
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        battery_name = parts[0].split('(')[0].strip()
                        status_part = parts[1]
                        
                        battery_id = f"pmset_{battery_name.lower().replace('-', '_')}"
                        
                        # Extract battery ID from parentheses
                        if '(id=' in parts[0]:
                            id_part = parts[0].split('(id=')[1].split(')')[0]
                            battery_id = f"pmset_battery_{id_part}"
                        
                        battery_data = {
                            'device_id': battery_id,
                            'name': battery_name,
                            'source': 'pmset'
                        }
                        
                        # Parse status information
                        if ';' in status_part:
                            status_parts = status_part.split(';')
                            
                            # Parse charge percentage
                            if status_parts[0].strip().endswith('%'):
                                charge_str = status_parts[0].strip().rstrip('%')
                                try:
                                    battery_data['charge_percent'] = float(charge_str)
                                except ValueError:
                                    pass
                            
                            # Parse charging status
                            if len(status_parts) > 1:
                                charge_status = status_parts[1].strip()
                                battery_data['charging_status'] = charge_status
                                battery_data['is_charging'] = 'charging' in charge_status.lower()
                            
                            # Parse time remaining
                            if len(status_parts) > 2:
                                time_remaining = status_parts[2].strip()
                                battery_data['time_remaining_str'] = time_remaining
                                
                                # Convert time to minutes
                                if ':' in time_remaining and 'remaining' in time_remaining:
                                    time_part = time_remaining.split('remaining')[0].strip()
                                    if ':' in time_part:
                                        try:
                                            hours, minutes = time_part.split(':')
                                            total_minutes = int(hours) * 60 + int(minutes)
                                            battery_data['time_remaining_minutes'] = total_minutes
                                        except ValueError:
                                            pass
                        
                        # Update existing battery or add new one
                        if battery_id in self._batteries:
                            self._batteries[battery_id].update(battery_data)
                        else:
                            self._batteries[battery_id] = battery_data
                        
                        self.logger.debug(f"Updated battery via pmset: {battery_id}")
            
        except Exception as e:
            self.logger.error(f"Error parsing pmset battery data: {e}")
    
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
                
                # Add macOS-specific metrics
                macos_metrics = self._get_macos_specific_metrics(battery_id)
                detailed_info.update(macos_metrics)
                
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
            
            # Get current status via pmset
            if self.pmset_available:
                result = subprocess.run(
                    ['pmset', '-g', 'batt'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Parse current battery status
                    self._parse_pmset_battery_data(result.stdout)
                    
                    # Get updated info for this battery
                    if battery_id in self._batteries:
                        battery_info = self._batteries[battery_id]
                        status.update({
                            'current_charge_percent': battery_info.get('charge_percent'),
                            'is_charging': battery_info.get('is_charging', False),
                            'charging_status': battery_info.get('charging_status'),
                            'time_remaining_minutes': battery_info.get('time_remaining_minutes')
                        })
            
            # Get additional status via ioreg
            if self.iokit_available:
                ioreg_status = self._get_ioreg_battery_status(battery_id)
                status.update(ioreg_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting current battery status: {e}")
            return {}
    
    def _get_ioreg_battery_status(self, battery_id: str) -> Dict[str, Any]:
        """Get current battery status via ioreg.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing ioreg battery status
        """
        try:
            result = subprocess.run(
                ['ioreg', '-rc', 'AppleSmartBattery'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse current ioreg data
                self._parse_ioreg_battery_data(result.stdout)
                
                # Return current data for this battery
                if battery_id in self._batteries:
                    battery_data = self._batteries[battery_id]
                    return {
                        'current_capacity': battery_data.get('current_capacity'),
                        'max_capacity': battery_data.get('max_capacity'),
                        'design_capacity': battery_data.get('design_capacity'),
                        'cycle_count': battery_data.get('cycle_count'),
                        'temperature': battery_data.get('temperature'),
                        'voltage': battery_data.get('voltage'),
                        'current': battery_data.get('current'),
                        'external_connected': battery_data.get('external_connected'),
                        'fully_charged': battery_data.get('fully_charged')
                    }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting ioreg battery status: {e}")
            return {}
    
    def _get_macos_specific_metrics(self, battery_id: str) -> Dict[str, Any]:
        """Get macOS-specific battery metrics.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing macOS-specific metrics
        """
        try:
            metrics = {}
            
            # Get power management metrics
            metrics.update(self._get_power_management_metrics())
            
            # Get thermal information
            metrics.update(self._get_thermal_metrics())
            
            # Get system power metrics
            metrics.update(self._get_system_power_metrics())
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting macOS-specific metrics: {e}")
            return {}
    
    def _get_power_management_metrics(self) -> Dict[str, Any]:
        """Get power management metrics.
        
        Returns:
            Dict containing power management data
        """
        try:
            metrics = {}
            
            # Get current power assertions
            if self.pmset_available:
                try:
                    result = subprocess.run(
                        ['pmset', '-g', 'assertions'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        metrics['power_assertions'] = result.stdout.strip()
                        
                except Exception:
                    pass
            
            # Add stored power settings
            metrics.update(self._power_settings)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting power management metrics: {e}")
            return {}
    
    def _get_thermal_metrics(self) -> Dict[str, Any]:
        """Get thermal-related metrics.
        
        Returns:
            Dict containing thermal data
        """
        try:
            metrics = {}
            
            # Get thermal state
            try:
                result = subprocess.run(
                    ['pmset', '-g', 'thermlog'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    metrics['thermal_log'] = result.stdout.strip()
                    
            except Exception:
                pass
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting thermal metrics: {e}")
            return {}
    
    def _get_system_power_metrics(self) -> Dict[str, Any]:
        """Get system power metrics.
        
        Returns:
            Dict containing system power data
        """
        try:
            metrics = {}
            
            # Get system power events
            if self.pmset_available:
                try:
                    result = subprocess.run(
                        ['pmset', '-g', 'log'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        # Parse recent power events
                        log_lines = result.stdout.split('\n')[-10:]  # Last 10 lines
                        metrics['recent_power_events'] = log_lines
                        
                except Exception:
                    pass
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system power metrics: {e}")
            return {}
    
    def _collect_data(self) -> Dict[str, Any]:
        """Collect macOS-specific battery data.
        
        Returns:
            Dict containing comprehensive battery monitoring data
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'platform': 'macos',
                'batteries': [],
                'power_management': self._power_settings.copy(),
                'tool_availability': {
                    'system_profiler': self.system_profiler_available,
                    'pmset': self.pmset_available,
                    'ioreg': self.iokit_available
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
            self.logger.error(f"Error collecting macOS battery data: {e}")
            error_handler.handle_error(e, "MacOSBatteryMonitor.collect_data")
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
            
            # Get macOS-specific metrics
            macos_metrics = self._get_macos_specific_metrics(battery_id)
            data.update(macos_metrics)
            
            # Calculate health metrics if not already present
            if 'health_percent' not in data:
                if data.get('design_capacity') and data.get('max_capacity'):
                    design_cap = data['design_capacity']
                    max_cap = data['max_capacity']
                    if design_cap > 0:
                        health_percent = (max_cap / design_cap) * 100.0
                        data['health_percent'] = min(100.0, max(0.0, health_percent))
            
            # Add platform identifier
            data['platform'] = 'macos'
            data['battery_id'] = battery_id
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting data for battery {battery_id}: {e}")
            return None
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected macOS battery data.
        
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
            
            if data['platform'] != 'macos':
                return False
            
            if not isinstance(data['batteries'], list):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating macOS battery data: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current macOS battery health status.
        
        Returns:
            Dict containing health status information
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return {
                    'status': 'unknown',
                    'message': 'No macOS battery data available',
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
                
                # macOS-specific health assessment
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
                        'charge_percent': battery.get('current_charge_percent'),
                        'cycle_count': battery.get('cycle_count'),
                        'condition': battery.get('condition')
                    }
                    for battery in batteries
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting macOS battery health status: {e}")
            return {
                'status': 'error',
                'message': f'Error retrieving battery health: {str(e)}',
                'batteries': []
            }