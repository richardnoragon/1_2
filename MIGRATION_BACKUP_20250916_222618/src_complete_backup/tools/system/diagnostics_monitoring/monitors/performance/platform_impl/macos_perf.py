"""macOS-specific performance monitoring implementation.

This module provides macOS-specific optimizations for performance monitoring
including IOKit framework integration, system_profiler, and macOS system APIs.
"""

import logging
import subprocess
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from core.error_handler import error_handler


class MacOSPerformanceImpl:
    """macOS-specific performance monitoring implementation.
    
    Provides enhanced performance monitoring using macOS system tools,
    IOKit framework (when available), and system APIs.
    """
    
    def __init__(self):
        """Initialize macOS performance implementation."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.MacOSPerformance'
        )
        
        # Tool availability
        self._tools_available = self._check_tool_availability()
        
        # Cache for expensive operations
        self._cpu_info_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 30  # Cache for 30 seconds
        
        self.logger.info("macOS performance implementation initialized")
    
    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check availability of macOS system tools.
        
        Returns:
            Dict indicating which tools are available
        """
        tools = {
            'system_profiler': False,
            'sysctl': False,
            'vm_stat': False,
            'top': False,
            'ioreg': False,
            'powermetrics': False
        }
        
        for tool in tools.keys():
            try:
                result = subprocess.run(
                    ['which', tool], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                tools[tool] = result.returncode == 0
            except Exception:
                tools[tool] = False
                
        self.logger.debug(f"Tool availability: {tools}")
        return tools
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get macOS-specific CPU information.
        
        Returns:
            Dict containing CPU information
        """
        import time
        current_time = time.time()
        
        # Check cache
        if (self._cpu_info_cache and 
            current_time - self._cache_timestamp < self._cache_duration):
            return self._cpu_info_cache.copy()
        
        cpu_info = {}
        
        try:
            # Get CPU information from system_profiler
            if self._tools_available['system_profiler']:
                profiler_info = self._get_cpu_info_system_profiler()
                cpu_info.update(profiler_info)
            
            # Get CPU information from sysctl
            if self._tools_available['sysctl']:
                sysctl_info = self._get_cpu_info_sysctl()
                cpu_info.update(sysctl_info)
            
            # Cache the result
            self._cpu_info_cache = cpu_info.copy()
            self._cache_timestamp = current_time
            
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.get_cpu_info")
            
        return cpu_info
    
    def _get_cpu_info_system_profiler(self) -> Dict[str, Any]:
        """Get CPU information from system_profiler.
        
        Returns:
            Dict containing system_profiler CPU information
        """
        cpu_info = {}
        
        try:
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType', '-json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                hardware_info = data.get('SPHardwareDataType', [])
                
                if hardware_info:
                    hw = hardware_info[0]
                    
                    # Extract CPU information
                    if 'chip_type' in hw:
                        cpu_info['chip_type'] = hw['chip_type']
                    if 'cpu_type' in hw:
                        cpu_info['cpu_type'] = hw['cpu_type']
                    if 'current_processor_speed' in hw:
                        cpu_info['processor_speed'] = hw['current_processor_speed']
                    if 'number_processors' in hw:
                        cpu_info['number_processors'] = hw['number_processors']
                    if 'packages' in hw:
                        cpu_info['packages'] = hw['packages']
                    if 'platform_UUID' in hw:
                        cpu_info['platform_uuid'] = hw['platform_UUID']
                        
        except Exception as e:
            self.logger.debug(f"system_profiler CPU info failed: {e}")
            
        return cpu_info
    
    def _get_cpu_info_sysctl(self) -> Dict[str, Any]:
        """Get CPU information from sysctl.
        
        Returns:
            Dict containing sysctl CPU information
        """
        cpu_info = {}
        
        try:
            # Get various CPU-related sysctl values
            sysctl_queries = {
                'brand_string': 'machdep.cpu.brand_string',
                'vendor': 'machdep.cpu.vendor',
                'family': 'machdep.cpu.family',
                'model': 'machdep.cpu.model',
                'stepping': 'machdep.cpu.stepping',
                'features': 'machdep.cpu.features',
                'leaf7_features': 'machdep.cpu.leaf7_features',
                'logical_per_package': 'machdep.cpu.logical_per_package',
                'cores_per_package': 'machdep.cpu.cores_per_package',
                'thread_count': 'machdep.cpu.thread_count',
                'core_count': 'machdep.cpu.core_count'
            }
            
            for key, sysctl_key in sysctl_queries.items():
                try:
                    result = subprocess.run(
                        ['sysctl', '-n', sysctl_key],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        if value:
                            # Try to convert to int if possible
                            try:
                                cpu_info[key] = int(value)
                            except ValueError:
                                cpu_info[key] = value
                                
                except Exception as e:
                    self.logger.debug(f"sysctl {sysctl_key} failed: {e}")
                    
        except Exception as e:
            self.logger.debug(f"sysctl CPU info failed: {e}")
            
        return cpu_info
    
    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get macOS-specific CPU metrics.
        
        Returns:
            Dict containing CPU metrics
        """
        metrics = {}
        
        try:
            # Get CPU usage from top command
            if self._tools_available['top']:
                top_metrics = self._get_cpu_metrics_top()
                metrics.update(top_metrics)
            
            # Get load average from sysctl
            if self._tools_available['sysctl']:
                load_metrics = self._get_load_metrics_sysctl()
                metrics.update(load_metrics)
            
            # Get CPU temperature if available
            temperature_metrics = self._get_cpu_temperature()
            metrics.update(temperature_metrics)
            
            # Get CPU frequency information
            frequency_metrics = self._get_cpu_frequency()
            metrics.update(frequency_metrics)
            
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.get_cpu_metrics")
            
        return metrics
    
    def _get_cpu_metrics_top(self) -> Dict[str, Any]:
        """Get CPU metrics from top command.
        
        Returns:
            Dict containing top CPU metrics
        """
        metrics = {}
        
        try:
            result = subprocess.run(
                ['top', '-l', '1', '-n', '0'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if 'CPU usage:' in line:
                        # Parse CPU usage line
                        # Example: "CPU usage: 12.5% user, 25.0% sys, 62.5% idle"
                        match = re.search(
                            r'CPU usage:\s*([\d.]+)%\s*user,\s*([\d.]+)%\s*sys,\s*([\d.]+)%\s*idle',
                            line
                        )
                        if match:
                            user_pct = float(match.group(1))
                            sys_pct = float(match.group(2))
                            idle_pct = float(match.group(3))
                            
                            metrics.update({
                                'cpu_user_top': user_pct,
                                'cpu_system_top': sys_pct,
                                'cpu_idle_top': idle_pct,
                                'cpu_usage_top': round(user_pct + sys_pct, 2)
                            })
                        break
                        
        except Exception as e:
            self.logger.debug(f"top CPU metrics failed: {e}")
            
        return metrics
    
    def _get_load_metrics_sysctl(self) -> Dict[str, Any]:
        """Get load metrics from sysctl.
        
        Returns:
            Dict containing load metrics
        """
        metrics = {}
        
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'vm.loadavg'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse load average output
                # Example: "{ 1.23 1.45 1.67 }"
                load_str = result.stdout.strip()
                match = re.search(r'\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}', load_str)
                
                if match:
                    metrics.update({
                        'load_1min_sysctl': float(match.group(1)),
                        'load_5min_sysctl': float(match.group(2)),
                        'load_15min_sysctl': float(match.group(3))
                    })
                    
        except Exception as e:
            self.logger.debug(f"sysctl load metrics failed: {e}")
            
        return metrics
    
    def _get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature using macOS-specific methods.
        
        Returns:
            Dict containing temperature information
        """
        temp_info = {}
        
        try:
            # Try powermetrics for temperature (requires sudo)
            if self._tools_available['powermetrics']:
                temp_powermetrics = self._get_temperature_powermetrics()
                temp_info.update(temp_powermetrics)
            
            # Try ioreg for temperature sensors
            if self._tools_available['ioreg']:
                temp_ioreg = self._get_temperature_ioreg()
                temp_info.update(temp_ioreg)
                
        except Exception as e:
            self.logger.debug(f"CPU temperature failed: {e}")
            
        return temp_info
    
    def _get_temperature_powermetrics(self) -> Dict[str, Any]:
        """Get temperature from powermetrics (if available).
        
        Returns:
            Dict containing powermetrics temperature information
        """
        temp_info = {}
        
        try:
            # Note: powermetrics typically requires sudo, so this may fail
            result = subprocess.run(
                ['powermetrics', '--samplers', 'smc', '-n', '1', '--show-initial-usage'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse powermetrics output for temperature
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'CPU die temperature' in line:
                        match = re.search(r'([\d.]+)\s*C', line)
                        if match:
                            temp_info['cpu_temperature_powermetrics'] = float(match.group(1))
                            
        except Exception as e:
            self.logger.debug(f"powermetrics temperature failed: {e}")
            
        return temp_info
    
    def _get_temperature_ioreg(self) -> Dict[str, Any]:
        """Get temperature from ioreg.
        
        Returns:
            Dict containing ioreg temperature information
        """
        temp_info = {}
        
        try:
            result = subprocess.run(
                ['ioreg', '-r', '-k', 'temperature'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse ioreg output for temperature sensors
                temperatures = []
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if 'temperature' in line.lower():
                        # Look for temperature values
                        match = re.search(r'(\d+)', line)
                        if match:
                            # ioreg temperatures are often in different units
                            temp_raw = int(match.group(1))
                            # Convert based on typical ioreg temperature formats
                            if temp_raw > 1000:  # Likely in millidegrees
                                temp_celsius = temp_raw / 1000.0
                            elif temp_raw > 100:  # Likely in decidegrees
                                temp_celsius = temp_raw / 10.0
                            else:
                                temp_celsius = float(temp_raw)
                            
                            if 0 < temp_celsius < 150:  # Reasonable range
                                temperatures.append(temp_celsius)
                
                if temperatures:
                    temp_info.update({
                        'cpu_temperature_ioreg': round(sum(temperatures) / len(temperatures), 1),
                        'cpu_temperature_sensors': [round(temp, 1) for temp in temperatures]
                    })
                    
        except Exception as e:
            self.logger.debug(f"ioreg temperature failed: {e}")
            
        return temp_info
    
    def _get_cpu_frequency(self) -> Dict[str, Any]:
        """Get CPU frequency information.
        
        Returns:
            Dict containing frequency information
        """
        freq_info = {}
        
        try:
            # Get frequency from sysctl
            freq_queries = {
                'freq_max': 'hw.cpufrequency_max',
                'freq_min': 'hw.cpufrequency_min',
                'freq_current': 'hw.cpufrequency'
            }
            
            for key, sysctl_key in freq_queries.items():
                try:
                    result = subprocess.run(
                        ['sysctl', '-n', sysctl_key],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        freq_hz = int(result.stdout.strip())
                        freq_mhz = freq_hz / 1000000  # Convert to MHz
                        freq_info[key] = round(freq_mhz, 2)
                        
                except Exception as e:
                    self.logger.debug(f"sysctl {sysctl_key} failed: {e}")
                    
        except Exception as e:
            self.logger.debug(f"CPU frequency failed: {e}")
            
        return freq_info
    
    def get_memory_details(self) -> Dict[str, Any]:
        """Get macOS-specific memory details.
        
        Returns:
            Dict containing memory information
        """
        memory_info = {}
        
        try:
            # Get memory information from vm_stat
            if self._tools_available['vm_stat']:
                vm_stat_info = self._get_memory_vm_stat()
                memory_info.update(vm_stat_info)
            
            # Get memory information from sysctl
            if self._tools_available['sysctl']:
                sysctl_memory_info = self._get_memory_sysctl()
                memory_info.update(sysctl_memory_info)
            
            # Get memory pressure information
            memory_pressure = self._get_memory_pressure()
            memory_info.update(memory_pressure)
            
        except Exception as e:
            self.logger.error(f"Error getting memory details: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.get_memory_details")
            
        return memory_info
    
    def _get_memory_vm_stat(self) -> Dict[str, Any]:
        """Get memory information from vm_stat.
        
        Returns:
            Dict containing vm_stat memory information
        """
        memory_info = {}
        
        try:
            result = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                # Parse vm_stat output
                for line in lines:
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            key = parts[0].strip().replace(' ', '_').lower()
                            value_str = parts[1].strip().rstrip('.')
                            
                            try:
                                value = int(value_str)
                                memory_info[f'vm_stat_{key}'] = value
                                
                                # Convert pages to bytes (assuming 4KB pages)
                                if 'pages' in key:
                                    bytes_value = value * 4096
                                    memory_info[f'vm_stat_{key}_bytes'] = bytes_value
                                    memory_info[f'vm_stat_{key}_mb'] = round(bytes_value / (1024**2), 2)
                                    
                            except ValueError:
                                memory_info[f'vm_stat_{key}'] = value_str
                                
        except Exception as e:
            self.logger.debug(f"vm_stat failed: {e}")
            
        return memory_info
    
    def _get_memory_sysctl(self) -> Dict[str, Any]:
        """Get memory information from sysctl.
        
        Returns:
            Dict containing sysctl memory information
        """
        memory_info = {}
        
        try:
            memory_queries = {
                'physical_memory': 'hw.memsize',
                'page_size': 'hw.pagesize',
                'usable_memory': 'hw.usermem'
            }
            
            for key, sysctl_key in memory_queries.items():
                try:
                    result = subprocess.run(
                        ['sysctl', '-n', sysctl_key],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        value = int(result.stdout.strip())
                        memory_info[key] = value
                        
                        if 'memory' in key:
                            memory_info[f'{key}_gb'] = round(value / (1024**3), 2)
                            
                except Exception as e:
                    self.logger.debug(f"sysctl {sysctl_key} failed: {e}")
                    
        except Exception as e:
            self.logger.debug(f"sysctl memory info failed: {e}")
            
        return memory_info
    
    def _get_memory_pressure(self) -> Dict[str, Any]:
        """Get memory pressure information.
        
        Returns:
            Dict containing memory pressure information
        """
        pressure_info = {}
        
        try:
            # Try to get memory pressure from sysctl
            result = subprocess.run(
                ['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                pressure_level = int(result.stdout.strip())
                pressure_info['memory_pressure_level'] = pressure_level
                
                # Interpret pressure level
                pressure_labels = {
                    0: 'normal',
                    1: 'warning',
                    2: 'urgent',
                    3: 'critical'
                }
                pressure_info['memory_pressure_status'] = pressure_labels.get(
                    pressure_level, 'unknown'
                )
                
        except Exception as e:
            self.logger.debug(f"Memory pressure failed: {e}")
            
        return pressure_info
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get macOS-specific process metrics.
        
        Returns:
            Dict containing process metrics
        """
        metrics = {}
        
        try:
            # Get process information from top
            if self._tools_available['top']:
                top_process_info = self._get_process_info_top()
                metrics.update(top_process_info)
            
            # Get process information from sysctl
            if self._tools_available['sysctl']:
                sysctl_process_info = self._get_process_info_sysctl()
                metrics.update(sysctl_process_info)
                
        except Exception as e:
            self.logger.error(f"Error getting process metrics: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.get_process_metrics")
            
        return metrics
    
    def _get_process_info_top(self) -> Dict[str, Any]:
        """Get process information from top.
        
        Returns:
            Dict containing top process information
        """
        process_info = {}
        
        try:
            result = subprocess.run(
                ['top', '-l', '1', '-n', '5', '-o', 'cpu'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                # Find processes line
                for i, line in enumerate(lines):
                    if 'Processes:' in line:
                        # Parse processes summary
                        # Example: "Processes: 123 total, 2 running, 121 sleeping, ..."
                        match = re.search(
                            r'Processes:\s*(\d+)\s*total,\s*(\d+)\s*running,\s*(\d+)\s*sleeping',
                            line
                        )
                        if match:
                            process_info.update({
                                'total_processes_top': int(match.group(1)),
                                'running_processes_top': int(match.group(2)),
                                'sleeping_processes_top': int(match.group(3))
                            })
                        break
                        
        except Exception as e:
            self.logger.debug(f"top process info failed: {e}")
            
        return process_info
    
    def _get_process_info_sysctl(self) -> Dict[str, Any]:
        """Get process information from sysctl.
        
        Returns:
            Dict containing sysctl process information
        """
        process_info = {}
        
        try:
            process_queries = {
                'max_processes': 'kern.maxproc',
                'max_processes_per_uid': 'kern.maxprocperuid'
            }
            
            for key, sysctl_key in process_queries.items():
                try:
                    result = subprocess.run(
                        ['sysctl', '-n', sysctl_key],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        process_info[key] = int(result.stdout.strip())
                        
                except Exception as e:
                    self.logger.debug(f"sysctl {sysctl_key} failed: {e}")
                    
        except Exception as e:
            self.logger.debug(f"sysctl process info failed: {e}")
            
        return process_info
    
    def get_additional_metrics(self) -> Dict[str, Any]:
        """Get additional macOS-specific metrics.
        
        Returns:
            Dict containing additional metrics
        """
        metrics = {}
        
        try:
            # Get system uptime
            uptime_info = self._get_uptime_info()
            metrics.update(uptime_info)
            
            # Get macOS version information
            version_info = self._get_macos_version_info()
            metrics.update(version_info)
            
        except Exception as e:
            self.logger.error(f"Error getting additional metrics: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.get_additional_metrics")
            
        return metrics
    
    def _get_uptime_info(self) -> Dict[str, Any]:
        """Get system uptime information.
        
        Returns:
            Dict containing uptime information
        """
        uptime_info = {}
        
        try:
            if self._tools_available['sysctl']:
                result = subprocess.run(
                    ['sysctl', '-n', 'kern.boottime'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Parse boot time
                    # Example: "{ sec = 1234567890, usec = 123456 } ..."
                    match = re.search(r'sec\s*=\s*(\d+)', result.stdout)
                    if match:
                        boot_timestamp = int(match.group(1))
                        boot_datetime = datetime.fromtimestamp(boot_timestamp)
                        uptime_seconds = (datetime.now() - boot_datetime).total_seconds()
                        
                        uptime_info.update({
                            'boot_time_sysctl': boot_datetime.isoformat(),
                            'uptime_seconds_sysctl': uptime_seconds,
                            'uptime_hours_sysctl': round(uptime_seconds / 3600, 2)
                        })
                        
        except Exception as e:
            self.logger.debug(f"Uptime info failed: {e}")
            
        return uptime_info
    
    def _get_macos_version_info(self) -> Dict[str, Any]:
        """Get macOS version information.
        
        Returns:
            Dict containing macOS version information
        """
        version_info = {}
        
        try:
            if self._tools_available['system_profiler']:
                result = subprocess.run(
                    ['system_profiler', 'SPSoftwareDataType', '-json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    software_info = data.get('SPSoftwareDataType', [])
                    
                    if software_info:
                        sw = software_info[0]
                        version_info.update({
                            'macos_version': sw.get('os_version', ''),
                            'macos_build': sw.get('system_version', ''),
                            'kernel_version': sw.get('kernel_version', ''),
                            'system_integrity': sw.get('system_integrity', ''),
                            'secure_boot': sw.get('secure_boot', '')
                        })
                        
        except Exception as e:
            self.logger.debug(f"macOS version info failed: {e}")
            
        return version_info
    
    def get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature using macOS-specific methods.
        
        Returns:
            Dict containing temperature information
        """
        return self._get_cpu_temperature()
    
    def get_fallback_cpu_info(self) -> Dict[str, Any]:
        """Get fallback CPU information when psutil is not available.
        
        Returns:
            Dict containing basic CPU information
        """
        fallback_info = {}
        
        try:
            if self._tools_available['sysctl']:
                result = subprocess.run(
                    ['sysctl', '-n', 'hw.ncpu'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    fallback_info['cpu_logical_cores'] = int(result.stdout.strip())
                    
        except Exception as e:
            self.logger.debug(f"Fallback CPU info failed: {e}")
            
        return fallback_info
    
    def get_fallback_memory_info(self) -> Dict[str, Any]:
        """Get fallback memory information when psutil is not available.
        
        Returns:
            Dict containing basic memory information
        """
        fallback_info = {}
        
        try:
            if self._tools_available['sysctl']:
                result = subprocess.run(
                    ['sysctl', '-n', 'hw.memsize'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    total_memory = int(result.stdout.strip())
                    fallback_info.update({
                        'memory_total': total_memory,
                        'memory_total_gb': round(total_memory / (1024**3), 2)
                    })
                    
        except Exception as e:
            self.logger.debug(f"Fallback memory info failed: {e}")
            
        return fallback_info
    
    def get_fallback_process_info(self) -> Dict[str, Any]:
        """Get fallback process information when psutil is not available.
        
        Returns:
            Dict containing basic process information
        """
        fallback_info = {}
        
        try:
            if self._tools_available['top']:
                result = subprocess.run(
                    ['top', '-l', '1', '-n', '0'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if 'Processes:' in line:
                            match = re.search(r'Processes:\s*(\d+)\s*total', line)
                            if match:
                                fallback_info['total_processes'] = int(match.group(1))
                            break
                            
        except Exception as e:
            self.logger.debug(f"Fallback process info failed: {e}")
            
        return fallback_info
    
    def cleanup(self) -> None:
        """Clean up macOS-specific resources."""
        try:
            # Clear caches
            self._cpu_info_cache = None
            self._cache_timestamp = 0
            
            self.logger.debug("macOS performance implementation cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            error_handler.handle_error(e, "MacOSPerformanceImpl.cleanup")
            