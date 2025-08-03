"""Main battery health monitoring class."""

import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ...core.monitor_base import MonitorBase, AlertLevel
from ...core.data_collector import get_data_collector
from .health_analyzer import BatteryHealthAnalyzer
from .cycle_tracker import ChargeCycleTracker
from core.error_handler import error_handler


class BatteryMonitor(MonitorBase):
    """Monitors battery health including charge cycles and power consumption."""
    
    def __init__(self, update_interval: float = 60.0):
        """Initialize the battery monitor.
        
        Args:
            update_interval: Update interval in seconds (default 60s for battery)
        """
        super().__init__("BatteryHealth", update_interval)
        
        # Initialize components
        self.health_analyzer = BatteryHealthAnalyzer()
        self.cycle_tracker = ChargeCycleTracker()
        self.data_collector = get_data_collector()
        
        # Battery tracking
        self._monitored_batteries: List[str] = []
        self._battery_info_cache: Dict[str, Dict[str, Any]] = {}
        self._last_charge_state: Dict[str, bool] = {}
        self._charging_sessions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Thresholds (configurable via alert manager)
        self.capacity_warning_threshold = 80.0  # 80% of design capacity
        self.capacity_critical_threshold = 60.0  # 60% of design capacity
        self.cycle_warning_threshold = 800  # 800 cycles warning
        self.cycle_critical_threshold = 1000  # 1000 cycles critical
        self.temperature_warning_threshold = 35.0  # 35°C warning
        self.temperature_critical_threshold = 45.0  # 45°C critical
        
        # Power consumption tracking
        self._power_history: List[Dict[str, Any]] = []
        self._max_power_history = 1000
        
        self.logger.info("Battery health monitor initialized")
    
    def _initialize_platform_specific(self) -> None:
        """Initialize platform-specific battery monitoring."""
        try:
            # Discover available batteries
            self._discover_batteries()
            
            # Initialize health analyzer
            self.health_analyzer.initialize(self.platform_detector.platform)
            
            # Initialize cycle tracker
            self.cycle_tracker.initialize()
            
            battery_count = len(self._monitored_batteries)
            self.logger.info(
                f"Initialized battery monitoring for {battery_count} batteries"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize battery monitoring: {e}")
            error_handler.handle_error(e, "BatteryMonitor.initialize")
            raise
    
    def _discover_batteries(self) -> None:
        """Discover available batteries for monitoring."""
        try:
            self._monitored_batteries.clear()
            self._battery_info_cache.clear()
            self._last_charge_state.clear()
            
            # Get battery information using psutil
            battery = psutil.sensors_battery()
            if battery is not None:
                battery_id = "main_battery"
                
                battery_info = {
                    'id': battery_id,
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'secsleft': battery.secsleft if hasattr(battery, 'secsleft') else None
                }
                
                self._monitored_batteries.append(battery_id)
                self._battery_info_cache[battery_id] = battery_info
                self._last_charge_state[battery_id] = battery.power_plugged
                self._charging_sessions[battery_id] = []
                
                self.logger.debug(
                    f"Added battery for monitoring: {battery_id} "
                    f"({battery_info['percent']:.1f}% charged)"
                )
            
            # Try to get additional platform-specific battery information
            self._discover_platform_batteries()
                
        except Exception as e:
            self.logger.error(f"Error discovering batteries: {e}")
            error_handler.handle_error(e, "BatteryMonitor.discover_batteries")
    
    def _discover_platform_batteries(self) -> None:
        """Discover platform-specific battery information."""
        try:
            from .platform_impl import get_platform_battery_monitor
            
            platform_monitor_class = get_platform_battery_monitor()
            if platform_monitor_class:
                # Get additional battery details from platform-specific monitor
                platform_monitor = platform_monitor_class()
                platform_batteries = platform_monitor.get_battery_details()
                
                for battery_id, battery_info in platform_batteries.items():
                    if battery_id not in self._battery_info_cache:
                        self._monitored_batteries.append(battery_id)
                        self._battery_info_cache[battery_id] = battery_info
                        self._last_charge_state[battery_id] = battery_info.get(
                            'power_plugged', False
                        )
                        self._charging_sessions[battery_id] = []
                    else:
                        # Enrich existing battery info
                        self._battery_info_cache[battery_id].update(battery_info)
                        
        except Exception as e:
            self.logger.warning(f"Could not get platform-specific battery info: {e}")
    
    def _collect_data(self) -> Dict[str, Any]:
        """Collect battery health and power data.
        
        Returns:
            Dict containing battery monitoring data
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'batteries': [],
                'power_consumption': {},
                'summary': {
                    'total_batteries': 0,
                    'healthy_batteries': 0,
                    'warning_batteries': 0,
                    'critical_batteries': 0,
                    'charging_batteries': 0,
                    'average_health': 0.0,
                    'total_capacity_wh': 0.0,
                    'current_capacity_wh': 0.0
                }
            }
            
            total_health = 0.0
            total_capacity = 0.0
            current_capacity = 0.0
            
            for battery_id in self._monitored_batteries:
                try:
                    battery_data = self._collect_battery_data(battery_id)
                    if battery_data:
                        data['batteries'].append(battery_data)
                        
                        # Update summary
                        health_percent = battery_data.get('health_percent', 100.0)
                        total_health += health_percent
                        
                        design_capacity = battery_data.get('design_capacity_wh', 0.0)
                        current_cap = battery_data.get('current_capacity_wh', 0.0)
                        total_capacity += design_capacity
                        current_capacity += current_cap
                        
                        # Count battery status
                        health_status = battery_data.get('health_status', 'unknown')
                        if health_status == 'healthy':
                            data['summary']['healthy_batteries'] += 1
                        elif health_status == 'warning':
                            data['summary']['warning_batteries'] += 1
                        elif health_status == 'critical':
                            data['summary']['critical_batteries'] += 1
                        
                        if battery_data.get('power_plugged', False):
                            data['summary']['charging_batteries'] += 1
                        
                except Exception as e:
                    self.logger.error(
                        f"Error collecting data for battery {battery_id}: {e}"
                    )
                    continue
            
            # Update summary totals
            battery_count = len(data['batteries'])
            data['summary']['total_batteries'] = battery_count
            data['summary']['average_health'] = (
                total_health / battery_count if battery_count > 0 else 0.0
            )
            data['summary']['total_capacity_wh'] = total_capacity
            data['summary']['current_capacity_wh'] = current_capacity
            
            # Collect power consumption data
            data['power_consumption'] = self._collect_power_consumption()
            
            # Store power history
            self._store_power_history(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting battery data: {e}")
            error_handler.handle_error(e, "BatteryMonitor.collect_data")
            return {}
    
    def _collect_battery_data(self, battery_id: str) -> Optional[Dict[str, Any]]:
        """Collect data for a specific battery.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Dict containing battery data or None if error
        """
        try:
            # Get cached basic info
            battery_info = self._battery_info_cache.get(battery_id, {})
            if not battery_info:
                return None
            
            # Update current battery status
            current_battery = psutil.sensors_battery()
            if current_battery and battery_id == "main_battery":
                battery_info.update({
                    'percent': current_battery.percent,
                    'power_plugged': current_battery.power_plugged,
                    'secsleft': getattr(current_battery, 'secsleft', None)
                })
            
            # Get health analysis
            health_data = self.health_analyzer.analyze_battery_health(
                battery_id, battery_info
            )
            if health_data:
                battery_info.update(health_data)
            
            # Get cycle tracking data
            cycle_data = self.cycle_tracker.get_cycle_data(battery_id)
            if cycle_data:
                battery_info.update(cycle_data)
            
            # Track charging state changes
            current_charging = battery_info.get('power_plugged', False)
            last_charging = self._last_charge_state.get(battery_id, False)
            
            if current_charging != last_charging:
                self._track_charging_state_change(
                    battery_id, current_charging, battery_info
                )
                self._last_charge_state[battery_id] = current_charging
            
            # Determine health status
            battery_info['health_status'] = self._determine_health_status(
                battery_info
            )
            
            # Add power consumption estimates
            power_data = self._estimate_power_consumption(battery_info)
            if power_data:
                battery_info['power_consumption'] = power_data
            
            return battery_info
            
        except Exception as e:
            self.logger.error(f"Error collecting data for battery {battery_id}: {e}")
            return None
    
    def _track_charging_state_change(
        self, 
        battery_id: str, 
        is_charging: bool, 
        battery_info: Dict[str, Any]
    ) -> None:
        """Track charging state changes for cycle analysis.
        
        Args:
            battery_id: Battery identifier
            is_charging: Current charging state
            battery_info: Current battery information
        """
        try:
            timestamp = datetime.now()
            charge_percent = battery_info.get('percent', 0.0)
            
            session_data = {
                'timestamp': timestamp.isoformat(),
                'is_charging': is_charging,
                'charge_percent': charge_percent,
                'temperature': battery_info.get('temperature'),
                'voltage': battery_info.get('voltage'),
                'current': battery_info.get('current')
            }
            
            if battery_id not in self._charging_sessions:
                self._charging_sessions[battery_id] = []
            
            self._charging_sessions[battery_id].append(session_data)
            
            # Limit session history
            if len(self._charging_sessions[battery_id]) > 1000:
                self._charging_sessions[battery_id] = (
                    self._charging_sessions[battery_id][-1000:]
                )
            
            # Update cycle tracker
            self.cycle_tracker.track_charging_event(
                battery_id, is_charging, charge_percent, timestamp
            )
            
            self.logger.debug(
                f"Battery {battery_id} charging state changed: "
                f"{'charging' if is_charging else 'discharging'} at {charge_percent}%"
            )
            
        except Exception as e:
            self.logger.error(f"Error tracking charging state change: {e}")
    
    def _collect_power_consumption(self) -> Dict[str, Any]:
        """Collect system power consumption data.
        
        Returns:
            Dict containing power consumption information
        """
        try:
            power_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_power_estimate': 0.0,
                'system_load': 0.0,
                'active_processes': 0
            }
            
            # Get CPU usage for power estimation
            cpu_percent = psutil.cpu_percent(interval=1)
            power_data['cpu_usage_percent'] = cpu_percent
            
            # Estimate CPU power consumption (rough calculation)
            # Typical laptop CPU: 15-45W, scale by usage
            base_cpu_power = 15.0  # Base power in watts
            max_cpu_power = 45.0   # Max power in watts
            power_data['cpu_power_estimate'] = (
                base_cpu_power + (max_cpu_power - base_cpu_power) * (cpu_percent / 100.0)
            )
            
            # Get system load
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            power_data['system_load'] = load_avg[0] if load_avg else 0.0
            
            # Count active processes
            power_data['active_processes'] = len(psutil.pids())
            
            # Get memory usage (affects power consumption)
            memory = psutil.virtual_memory()
            power_data['memory_usage_percent'] = memory.percent
            
            return power_data
            
        except Exception as e:
            self.logger.error(f"Error collecting power consumption data: {e}")
            return {}
    
    def _estimate_power_consumption(self, battery_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Estimate power consumption for a specific battery.
        
        Args:
            battery_info: Battery information
            
        Returns:
            Dict containing power consumption estimates or None
        """
        try:
            power_data = {}
            
            # Calculate discharge rate if available
            current_percent = battery_info.get('percent', 0.0)
            secsleft = battery_info.get('secsleft')
            
            if secsleft and secsleft > 0:
                # Estimate power consumption based on remaining time
                hours_left = secsleft / 3600.0
                capacity_wh = battery_info.get('current_capacity_wh', 0.0)
                
                if capacity_wh > 0 and hours_left > 0:
                    power_consumption_w = (capacity_wh * current_percent / 100.0) / hours_left
                    power_data['estimated_consumption_w'] = power_consumption_w
                    power_data['estimated_runtime_hours'] = hours_left
            
            # Add voltage and current if available
            voltage = battery_info.get('voltage')
            current = battery_info.get('current')
            
            if voltage and current:
                power_data['actual_power_w'] = abs(voltage * current / 1000.0)  # Convert mA to A
            
            return power_data if power_data else None
            
        except Exception as e:
            self.logger.error(f"Error estimating power consumption: {e}")
            return None
    
    def _store_power_history(self, data: Dict[str, Any]) -> None:
        """Store power consumption history.
        
        Args:
            data: Current monitoring data
        """
        try:
            power_entry = {
                'timestamp': data['timestamp'],
                'power_consumption': data.get('power_consumption', {}),
                'battery_summary': data.get('summary', {})
            }
            
            self._power_history.append(power_entry)
            
            # Limit history size
            if len(self._power_history) > self._max_power_history:
                self._power_history = self._power_history[-self._max_power_history:]
                
        except Exception as e:
            self.logger.error(f"Error storing power history: {e}")
    
    def _determine_health_status(self, battery_info: Dict[str, Any]) -> str:
        """Determine the health status of a battery.
        
        Args:
            battery_info: Battery information dictionary
            
        Returns:
            Health status: 'healthy', 'warning', or 'critical'
        """
        try:
            # Check capacity health
            health_percent = battery_info.get('health_percent', 100.0)
            if health_percent <= self.capacity_critical_threshold:
                return 'critical'
            elif health_percent <= self.capacity_warning_threshold:
                return 'warning'
            
            # Check cycle count
            cycle_count = battery_info.get('cycle_count', 0)
            if cycle_count >= self.cycle_critical_threshold:
                return 'critical'
            elif cycle_count >= self.cycle_warning_threshold:
                return 'warning'
            
            # Check temperature
            temperature = battery_info.get('temperature')
            if temperature is not None:
                if temperature >= self.temperature_critical_threshold:
                    return 'critical'
                elif temperature >= self.temperature_warning_threshold:
                    return 'warning'
            
            # Check charge level (very low battery)
            charge_percent = battery_info.get('percent', 100.0)
            if charge_percent <= 5.0 and not battery_info.get('power_plugged', False):
                return 'critical'
            elif charge_percent <= 15.0 and not battery_info.get('power_plugged', False):
                return 'warning'
            
            return 'healthy'
            
        except Exception as e:
            self.logger.error(f"Error determining battery health status: {e}")
            return 'unknown'
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected battery data.
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if data is valid
        """
        if not isinstance(data, dict):
            return False
        
        if 'batteries' not in data or not isinstance(data['batteries'], list):
            return False
        
        if 'summary' not in data or not isinstance(data['summary'], dict):
            return False
        
        # Validate each battery entry
        for battery in data['batteries']:
            if not isinstance(battery, dict):
                return False
            
            required_fields = ['id', 'percent']
            if not all(field in battery for field in required_fields):
                return False
            
            # Validate percentage
            percent = battery.get('percent', 0)
            if not (0 <= percent <= 100):
                return False
        
        return True
    
    def _check_alerts(self, data: Dict[str, Any]) -> None:
        """Check for battery-related alert conditions.
        
        Args:
            data: Current battery monitoring data
        """
        try:
            for battery in data.get('batteries', []):
                battery_id = battery.get('id', 'unknown')
                
                # Check capacity health alerts
                health_percent = battery.get('health_percent', 100.0)
                if health_percent <= self.capacity_critical_threshold:
                    self._notify_alert_callbacks(
                        f"battery_health_critical_{battery_id}",
                        AlertLevel.CRITICAL,
                        f"Critical: Battery {battery_id} health is "
                        f"{health_percent:.1f}% of original capacity"
                    )
                elif health_percent <= self.capacity_warning_threshold:
                    self._notify_alert_callbacks(
                        f"battery_health_warning_{battery_id}",
                        AlertLevel.WARNING,
                        f"Warning: Battery {battery_id} health is "
                        f"{health_percent:.1f}% of original capacity"
                    )
                
                # Check cycle count alerts
                cycle_count = battery.get('cycle_count', 0)
                if cycle_count >= self.cycle_critical_threshold:
                    self._notify_alert_callbacks(
                        f"battery_cycles_critical_{battery_id}",
                        AlertLevel.CRITICAL,
                        f"Critical: Battery {battery_id} has {cycle_count} charge cycles"
                    )
                elif cycle_count >= self.cycle_warning_threshold:
                    self._notify_alert_callbacks(
                        f"battery_cycles_warning_{battery_id}",
                        AlertLevel.WARNING,
                        f"Warning: Battery {battery_id} has {cycle_count} charge cycles"
                    )
                
                # Check temperature alerts
                temperature = battery.get('temperature')
                if temperature is not None:
                    if temperature >= self.temperature_critical_threshold:
                        self._notify_alert_callbacks(
                            f"battery_temp_critical_{battery_id}",
                            AlertLevel.CRITICAL,
                            f"Critical: Battery {battery_id} temperature is "
                            f"{temperature}°C"
                        )
                    elif temperature >= self.temperature_warning_threshold:
                        self._notify_alert_callbacks(
                            f"battery_temp_warning_{battery_id}",
                            AlertLevel.WARNING,
                            f"Warning: Battery {battery_id} temperature is "
                            f"{temperature}°C"
                        )
                
                # Check low battery alerts
                charge_percent = battery.get('percent', 100.0)
                is_plugged = battery.get('power_plugged', False)
                
                if not is_plugged:
                    if charge_percent <= 5.0:
                        self._notify_alert_callbacks(
                            f"battery_low_critical_{battery_id}",
                            AlertLevel.CRITICAL,
                            f"Critical: Battery {battery_id} charge is very low "
                            f"({charge_percent:.1f}%)"
                        )
                    elif charge_percent <= 15.0:
                        self._notify_alert_callbacks(
                            f"battery_low_warning_{battery_id}",
                            AlertLevel.WARNING,
                            f"Warning: Battery {battery_id} charge is low "
                            f"({charge_percent:.1f}%)"
                        )
                        
        except Exception as e:
            self.logger.error(f"Error checking battery alerts: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current battery health status.
        
        Returns:
            Dict containing health status information
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return {
                    'status': 'unknown',
                    'message': 'No battery data available',
                    'batteries': []
                }
            
            summary = current_data.get('summary', {})
            batteries = current_data.get('batteries', [])
            
            # Determine overall status
            critical_batteries = summary.get('critical_batteries', 0)
            warning_batteries = summary.get('warning_batteries', 0)
            
            if critical_batteries > 0:
                overall_status = 'critical'
                message = f"{critical_batteries} battery(ies) in critical state"
            elif warning_batteries > 0:
                overall_status = 'warning'
                message = f"{warning_batteries} battery(ies) need attention"
            else:
                overall_status = 'healthy'
                message = "All batteries are healthy"
            
            return {
                'status': overall_status,
                'message': message,
                'summary': summary,
                'batteries': [
                    {
                        'id': battery.get('id'),
                        'health_status': battery.get('health_status'),
                        'percent': battery.get('percent'),
                        'health_percent': battery.get('health_percent'),
                        'cycle_count': battery.get('cycle_count'),
                        'temperature': battery.get('temperature')
                    }
                    for battery in batteries
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting battery health status: {e}")
            return {
                'status': 'error',
                'message': f'Error retrieving battery health: {str(e)}',
                'batteries': []
            }
    
    def get_battery_details(self, battery_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific battery.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Detailed battery information or None if not found
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return None
            
            for battery in current_data.get('batteries', []):
                if battery.get('id') == battery_id:
                    return battery
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting battery details for {battery_id}: {e}")
            return None
    
    def get_power_consumption_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get power consumption history.
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            List of power consumption data points
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_history = []
            for entry in self._power_history:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if timestamp > cutoff_time:
                    filtered_history.append(entry)
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"Error getting power consumption history: {e}")
            return []
    
    def get_charging_sessions(self, battery_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get charging session history for a battery.
        
        Args:
            battery_id: Battery identifier
            hours: Number of hours of history to retrieve
            
        Returns:
            List of charging session data
        """
        try:
            if battery_id not in self._charging_sessions:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_sessions = []
            for session in self._charging_sessions[battery_id]:
                timestamp = datetime.fromisoformat(session['timestamp'])
                if timestamp > cutoff_time:
                    filtered_sessions.append(session)
            
            return filtered_sessions
            
        except Exception as e:
            self.logger.error(f"Error getting charging sessions for {battery_id}: {e}")
            return []
    
    def refresh_battery_list(self) -> bool:
        """Refresh the list of monitored batteries.
        
        Returns:
            bool: True if refresh was successful
        """
        try:
            self._discover_batteries()
            self.logger.info("Battery list refreshed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing battery list: {e}")
            error_handler.handle_error(e, "BatteryMonitor.refresh_battery_list")
            return False
    
    def set_thresholds(
        self,
        capacity_warning: Optional[float] = None,
        capacity_critical: Optional[float] = None,
        cycle_warning: Optional[int] = None,
        cycle_critical: Optional[int] = None,
        temp_warning: Optional[float] = None,
        temp_critical: Optional[float] = None
    ) -> None:
        """Set alert thresholds.
        
        Args:
            capacity_warning: Warning threshold for battery capacity percentage
            capacity_critical: Critical threshold for battery capacity percentage
            cycle_warning: Warning threshold for charge cycles
            cycle_critical: Critical threshold for charge cycles
            temp_warning: Warning threshold for temperature (°C)
            temp_critical: Critical threshold for temperature (°C)
        """
        if capacity_warning is not None:
            self.capacity_warning_threshold = capacity_warning
        if capacity_critical is not None:
            self.capacity_critical_threshold = capacity_critical
        if cycle_warning is not None:
            self.cycle_warning_threshold = cycle_warning
        if cycle_critical is not None:
            self.cycle_critical_threshold = cycle_critical
        if temp_warning is not None:
            self.temperature_warning_threshold = temp_warning
        if temp_critical is not None:
            self.temperature_critical_threshold = temp_critical
        
        self.logger.info("Updated battery monitoring thresholds")