"""Linux-specific performance monitoring implementation.

This module provides Linux-specific optimizations for performance monitoring
including proc filesystem, sysfs integration, and Linux system tools.
"""

import logging
import os
import re
import subprocess
from typing import Dict, Any, List
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from core.error_handler import error_handler


class LinuxPerformanceImpl:
    """Linux-specific performance monitoring implementation.
    
    Provides enhanced performance monitoring using Linux proc filesystem,
    sysfs, and system tools for comprehensive system analysis.
    """
    
    def __init__(self):
        """Initialize Linux performance implementation."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.LinuxPerformance'
        )
        
        # Filesystem paths
        self.proc_path = '/proc'
        self.sys_path = '/sys'
        
        # Tool availability
        self._tools_available = self._check_tool_availability()
        
        # Cache for expensive operations
        self._cpu_info_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 30  # Cache for 30 seconds
        
        self.logger.info("Linux performance implementation initialized")
    
    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check availability of Linux system tools.
        
        Returns:
            Dict indicating which tools are available
        """
        tools = {
            'lscpu': False,
            'free': False,
            'vmstat': False,
            'iostat': False,
            'top': False,
            'htop': False,
            'sensors': False,
            'cpufreq-info': False
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
                
        # Check proc and sys filesystem availability
        tools['proc_available'] = os.path.exists(self.proc_path)
        tools['sys_available'] = os.path.exists(self.sys_path)
        
        self.logger.debug(f"Tool availability: {tools}")
        return tools
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get Linux-specific CPU information.
        
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
            # Get CPU information from /proc/cpuinfo
            if self._tools_available['proc_available']:
                proc_info = self._get_cpu_info_proc()
                cpu_info.update(proc_info)
            
            # Get CPU information from lscpu
            if self._tools_available['lscpu']:
                lscpu_info = self._get_cpu_info_lscpu()
                cpu_info.update(lscpu_info)
            
            # Get CPU frequency information
            freq_info = self._get_cpu_frequency_info()
            cpu_info.update(freq_info)
            
            # Cache the result
            self._cpu_info_cache = cpu_info.copy()
            self._cache_timestamp = current_time
            
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.get_cpu_info")
            
        return cpu_info
    
    def _get_cpu_info_proc(self) -> Dict[str, Any]:
        """Get CPU information from /proc/cpuinfo.
        
        Returns:
            Dict containing proc cpuinfo information
        """
        cpu_info = {}
        
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
            
            # Parse cpuinfo
            processors = []
            current_processor = {}
            
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    current_processor[key] = value
                elif line.strip() == '' and current_processor:
                    processors.append(current_processor)
                    current_processor = {}
            
            if current_processor:
                processors.append(current_processor)
            
            if processors:
                # Get information from first processor
                first_proc = processors[0]
                
                cpu_info.update({
                    'processor_count': len(processors),
                    'vendor_id': first_proc.get('vendor_id', ''),
                    'model_name': first_proc.get('model name', ''),
                    'cpu_family': first_proc.get('cpu family', ''),
                    'model': first_proc.get('model', ''),
                    'stepping': first_proc.get('stepping', ''),
                    'microcode': first_proc.get('microcode', ''),
                    'cpu_mhz': first_proc.get('cpu MHz', ''),
                    'cache_size': first_proc.get('cache size', ''),
                    'physical_id': first_proc.get('physical id', ''),
                    'siblings': first_proc.get('siblings', ''),
                    'core_id': first_proc.get('core id', ''),
                    'cpu_cores': first_proc.get('cpu cores', ''),
                    'flags': first_proc.get('flags', '').split()
                })
                
                # Convert numeric fields
                for field in ['cpu_family', 'model', 'stepping', 'siblings', 'cpu_cores']:
                    if field in cpu_info and cpu_info[field]:
                        try:
                            cpu_info[field] = int(cpu_info[field])
                        except ValueError:
                            pass
                
                if 'cpu_mhz' in cpu_info and cpu_info['cpu_mhz']:
                    try:
                        cpu_info['cpu_mhz'] = float(cpu_info['cpu_mhz'])
                    except ValueError:
                        pass
                        
        except Exception as e:
            self.logger.debug(f"proc cpuinfo failed: {e}")
            
        return cpu_info
    
    def _get_cpu_info_lscpu(self) -> Dict[str, Any]:
        """Get CPU information from lscpu.
        
        Returns:
            Dict containing lscpu information
        """
        cpu_info = {}
        
        try:
            result = subprocess.run(
                ['lscpu'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
                        value = value.strip()
                        
                        if value:
                            cpu_info[f'lscpu_{key}'] = value
                            
                            # Try to convert numeric values
                            if key in ['cpus', 'threads_per_core', 'cores_per_socket', 'sockets']:
                                try:
                                    cpu_info[f'lscpu_{key}'] = int(value)
                                except ValueError:
                                    pass
                                    
        except Exception as e:
            self.logger.debug(f"lscpu failed: {e}")
            
        return cpu_info
    
    def _get_cpu_frequency_info(self) -> Dict[str, Any]:
        """Get CPU frequency information from various sources.
        
        Returns:
            Dict containing frequency information
        """
        freq_info = {}
        
        try:
            # Try cpufreq-info
            if self._tools_available['cpufreq-info']:
                freq_cpufreq = self._get_frequency_cpufreq()
                freq_info.update(freq_cpufreq)
            
            # Try sysfs cpufreq
            if self._tools_available['sys_available']:
                freq_sysfs = self._get_frequency_sysfs()
                freq_info.update(freq_sysfs)
                
        except Exception as e:
            self.logger.debug(f"CPU frequency info failed: {e}")
            
        return freq_info
    
    def _get_frequency_cpufreq(self) -> Dict[str, Any]:
        """Get frequency information from cpufreq-info.
        
        Returns:
            Dict containing cpufreq information
        """
        freq_info = {}
        
        try:
            result = subprocess.run(
                ['cpufreq-info', '-f'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                freq_hz = int(result.stdout.strip())
                freq_mhz = freq_hz / 1000000
                freq_info['current_frequency_mhz'] = round(freq_mhz, 2)
                
        except Exception as e:
            self.logger.debug(f"cpufreq-info failed: {e}")
            
        return freq_info
    
    def _get_frequency_sysfs(self) -> Dict[str, Any]:
        """Get frequency information from sysfs.
        
        Returns:
            Dict containing sysfs frequency information
        """
        freq_info = {}
        
        try:
            cpufreq_path = '/sys/devices/system/cpu/cpu0/cpufreq'
            
            if os.path.exists(cpufreq_path):
                # Get current frequency
                current_freq_path = os.path.join(cpufreq_path, 'scaling_cur_freq')
                if os.path.exists(current_freq_path):
                    with open(current_freq_path, 'r') as f:
                        freq_khz = int(f.read().strip())
                        freq_info['scaling_cur_freq_mhz'] = round(freq_khz / 1000, 2)
                
                # Get min frequency
                min_freq_path = os.path.join(cpufreq_path, 'scaling_min_freq')
                if os.path.exists(min_freq_path):
                    with open(min_freq_path, 'r') as f:
                        freq_khz = int(f.read().strip())
                        freq_info['scaling_min_freq_mhz'] = round(freq_khz / 1000, 2)
                
                # Get max frequency
                max_freq_path = os.path.join(cpufreq_path, 'scaling_max_freq')
                if os.path.exists(max_freq_path):
                    with open(max_freq_path, 'r') as f:
                        freq_khz = int(f.read().strip())
                        freq_info['scaling_max_freq_mhz'] = round(freq_khz / 1000, 2)
                
                # Get governor
                governor_path = os.path.join(cpufreq_path, 'scaling_governor')
                if os.path.exists(governor_path):
                    with open(governor_path, 'r') as f:
                        freq_info['scaling_governor'] = f.read().strip()
                        
        except Exception as e:
            self.logger.debug(f"sysfs frequency failed: {e}")
            
        return freq_info
    
    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get Linux-specific CPU metrics.
        
        Returns:
            Dict containing CPU metrics
        """
        metrics = {}
        
        try:
            # Get CPU statistics from /proc/stat
            if self._tools_available['proc_available']:
                proc_stat_metrics = self._get_cpu_metrics_proc_stat()
                metrics.update(proc_stat_metrics)
            
            # Get load average from /proc/loadavg
            if self._tools_available['proc_available']:
                loadavg_metrics = self._get_loadavg_metrics()
                metrics.update(loadavg_metrics)
            
            # Get CPU temperature
            temperature_metrics = self._get_cpu_temperature()
            metrics.update(temperature_metrics)
            
            # Get CPU usage from vmstat
            if self._tools_available['vmstat']:
                vmstat_metrics = self._get_cpu_metrics_vmstat()
                metrics.update(vmstat_metrics)
                
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.get_cpu_metrics")
            
        return metrics
    
    def _get_cpu_metrics_proc_stat(self) -> Dict[str, Any]:
        """Get CPU metrics from /proc/stat.
        
        Returns:
            Dict containing proc stat CPU metrics
        """
        metrics = {}
        
        try:
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
            
            # Parse CPU line
            for line in lines:
                if line.startswith('cpu '):
                    parts = line.split()
                    if len(parts) >= 8:
                        user = int(parts[1])
                        nice = int(parts[2])
                        system = int(parts[3])
                        idle = int(parts[4])
                        iowait = int(parts[5])
                        irq = int(parts[6])
                        softirq = int(parts[7])
                        
                        total = user + nice + system + idle + iowait + irq + softirq
                        
                        if total > 0:
                            metrics.update({
                                'cpu_user_proc': round((user / total) * 100, 2),
                                'cpu_nice_proc': round((nice / total) * 100, 2),
                                'cpu_system_proc': round((system / total) * 100, 2),
                                'cpu_idle_proc': round((idle / total) * 100, 2),
                                'cpu_iowait_proc': round((iowait / total) * 100, 2),
                                'cpu_irq_proc': round((irq / total) * 100, 2),
                                'cpu_softirq_proc': round((softirq / total) * 100, 2),
                                'cpu_usage_proc': round(((total - idle) / total) * 100, 2)
                            })
                    break
                    
        except Exception as e:
            self.logger.debug(f"proc stat CPU metrics failed: {e}")
            
        return metrics
    
    def _get_loadavg_metrics(self) -> Dict[str, Any]:
        """Get load average metrics from /proc/loadavg.
        
        Returns:
            Dict containing load average metrics
        """
        metrics = {}
        
        try:
            with open('/proc/loadavg', 'r') as f:
                content = f.read().strip()
            
            parts = content.split()
            if len(parts) >= 3:
                metrics.update({
                    'load_1min_proc': float(parts[0]),
                    'load_5min_proc': float(parts[1]),
                    'load_15min_proc': float(parts[2])
                })
                
                # Parse running/total processes
                if len(parts) >= 4 and '/' in parts[3]:
                    running, total = parts[3].split('/')
                    metrics.update({
                        'running_processes_proc': int(running),
                        'total_processes_proc': int(total)
                    })
                    
        except Exception as e:
            self.logger.debug(f"proc loadavg failed: {e}")
            
        return metrics
    
    def _get_cpu_metrics_vmstat(self) -> Dict[str, Any]:
        """Get CPU metrics from vmstat.
        
        Returns:
            Dict containing vmstat CPU metrics
        """
        metrics = {}
        
        try:
            result = subprocess.run(
                ['vmstat', '1', '2'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # Get the last line (second sample)
                if len(lines) >= 3:
                    data_line = lines[-1]
                    parts = data_line.split()
                    
                    if len(parts) >= 15:
                        # vmstat columns: us sy id wa st
                        us_idx = 12  # user time
                        sy_idx = 13  # system time
                        id_idx = 14  # idle time
                        wa_idx = 15  # wait time
                        
                        if len(parts) > wa_idx:
                            metrics.update({
                                'cpu_user_vmstat': int(parts[us_idx]),
                                'cpu_system_vmstat': int(parts[sy_idx]),
                                'cpu_idle_vmstat': int(parts[id_idx]),
                                'cpu_wait_vmstat': int(parts[wa_idx])
                            })
                            
        except Exception as e:
            self.logger.debug(f"vmstat CPU metrics failed: {e}")
            
        return metrics
    
    def _get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature using Linux-specific methods.
        
        Returns:
            Dict containing temperature information
        """
        temp_info = {}
        
        try:
            # Try sensors command
            if self._tools_available['sensors']:
                sensors_temp = self._get_temperature_sensors()
                temp_info.update(sensors_temp)
            
            # Try thermal zones in sysfs
            if self._tools_available['sys_available']:
                thermal_temp = self._get_temperature_thermal_zones()
                temp_info.update(thermal_temp)
                
        except Exception as e:
            self.logger.debug(f"CPU temperature failed: {e}")
            
        return temp_info
    
    def _get_temperature_sensors(self) -> Dict[str, Any]:
        """Get temperature from sensors command.
        
        Returns:
            Dict containing sensors temperature information
        """
        temp_info = {}
        
        try:
            result = subprocess.run(
                ['sensors', '-A'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                temperatures = []
                
                for line in result.stdout.split('\n'):
                    # Look for temperature readings
                    if 'Core' in line or 'temp' in line.lower():
                        match = re.search(r'([+-]?\d+\.?\d*)\s*°C', line)
                        if match:
                            temp = float(match.group(1))
                            if 0 < temp < 150:  # Reasonable range
                                temperatures.append(temp)
                
                if temperatures:
                    temp_info.update({
                        'cpu_temperature_sensors': round(sum(temperatures) / len(temperatures), 1),
                        'cpu_temperature_cores': [round(temp, 1) for temp in temperatures],
                        'cpu_temperature_max_sensors': round(max(temperatures), 1),
                        'cpu_temperature_min_sensors': round(min(temperatures), 1)
                    })
                    
        except Exception as e:
            self.logger.debug(f"sensors temperature failed: {e}")
            
        return temp_info
    
    def _get_temperature_thermal_zones(self) -> Dict[str, Any]:
        """Get temperature from thermal zones.
        
        Returns:
            Dict containing thermal zone temperature information
        """
        temp_info = {}
        
        try:
            thermal_path = '/sys/class/thermal'
            
            if os.path.exists(thermal_path):
                temperatures = []
                
                for zone_dir in os.listdir(thermal_path):
                    if zone_dir.startswith('thermal_zone'):
                        zone_path = os.path.join(thermal_path, zone_dir)
                        temp_file = os.path.join(zone_path, 'temp')
                        type_file = os.path.join(zone_path, 'type')
                        
                        if os.path.exists(temp_file):
                            try:
                                with open(temp_file, 'r') as f:
                                    temp_millidegrees = int(f.read().strip())
                                    temp_celsius = temp_millidegrees / 1000.0
                                
                                # Check if this is a CPU-related thermal zone
                                zone_type = ''
                                if os.path.exists(type_file):
                                    with open(type_file, 'r') as f:
                                        zone_type = f.read().strip().lower()
                                
                                if any(keyword in zone_type for keyword in ['cpu', 'core', 'processor']):
                                    if 0 < temp_celsius < 150:
                                        temperatures.append(temp_celsius)
                                        
                            except (ValueError, IOError):
                                continue
                
                if temperatures:
                    temp_info.update({
                        'cpu_temperature_thermal': round(sum(temperatures) / len(temperatures), 1),
                        'cpu_temperature_zones': [round(temp, 1) for temp in temperatures]
                    })
                    
        except Exception as e:
            self.logger.debug(f"thermal zones temperature failed: {e}")
            
        return temp_info
    
    def get_memory_details(self) -> Dict[str, Any]:
        """Get Linux-specific memory details.
        
        Returns:
            Dict containing memory information
        """
        memory_info = {}
        
        try:
            # Get memory information from /proc/meminfo
            if self._tools_available['proc_available']:
                meminfo = self._get_memory_proc_meminfo()
                memory_info.update(meminfo)
            
            # Get memory information from free command
            if self._tools_available['free']:
                free_info = self._get_memory_free()
                memory_info.update(free_info)
            
            # Get memory information from vmstat
            if self._tools_available['vmstat']:
                vmstat_memory = self._get_memory_vmstat()
                memory_info.update(vmstat_memory)
                
        except Exception as e:
            self.logger.error(f"Error getting memory details: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.get_memory_details")
            
        return memory_info
    
    def _get_memory_proc_meminfo(self) -> Dict[str, Any]:
        """Get memory information from /proc/meminfo.
        
        Returns:
            Dict containing proc meminfo information
        """
        memory_info = {}
        
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace('(', '').replace(')', '')
                    value = value.strip()
                    
                    # Extract numeric value (usually in kB)
                    match = re.search(r'(\d+)', value)
                    if match:
                        value_kb = int(match.group(1))
                        memory_info[f'meminfo_{key}_kb'] = value_kb
                        memory_info[f'meminfo_{key}_mb'] = round(value_kb / 1024, 2)
                        memory_info[f'meminfo_{key}_gb'] = round(value_kb / (1024**2), 2)
                        
        except Exception as e:
            self.logger.debug(f"proc meminfo failed: {e}")
            
        return memory_info
    
    def _get_memory_free(self) -> Dict[str, Any]:
        """Get memory information from free command.
        
        Returns:
            Dict containing free command information
        """
        memory_info = {}
        
        try:
            result = subprocess.run(
                ['free', '-b'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if line.startswith('Mem:'):
                        parts = line.split()
                        if len(parts) >= 7:
                            memory_info.update({
                                'free_total_bytes': int(parts[1]),
                                'free_used_bytes': int(parts[2]),
                                'free_available_bytes': int(parts[6]),
                                'free_total_gb': round(int(parts[1]) / (1024**3), 2),
                                'free_used_gb': round(int(parts[2]) / (1024**3), 2),
                                'free_available_gb': round(int(parts[6]) / (1024**3), 2)
                            })
                    elif line.startswith('Swap:'):
                        parts = line.split()
                        if len(parts) >= 4:
                            memory_info.update({
                                'free_swap_total_bytes': int(parts[1]),
                                'free_swap_used_bytes': int(parts[2]),
                                'free_swap_free_bytes': int(parts[3]),
                                'free_swap_total_gb': round(int(parts[1]) / (1024**3), 2),
                                'free_swap_used_gb': round(int(parts[2]) / (1024**3), 2),
                                'free_swap_free_gb': round(int(parts[3]) / (1024**3), 2)
                            })
                            
        except Exception as e:
            self.logger.debug(f"free command failed: {e}")
            
        return memory_info
    
    def _get_memory_vmstat(self) -> Dict[str, Any]:
        """Get memory information from vmstat.
        
        Returns:
            Dict containing vmstat memory information
        """
        memory_info = {}
        
        try:
            result = subprocess.run(
                ['vmstat', '1', '2'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # Get the last line (second sample)
                if len(lines) >= 3:
                    data_line = lines[-1]
                    parts = data_line.split()
                    
                    if len(parts) >= 6:
                        # vmstat memory columns: swpd free buff cache
                        memory_info.update({
                            'vmstat_swpd_kb': int(parts[2]),  # swap used
                            'vmstat_free_kb': int(parts[3]),  # free memory
                            'vmstat_buff_kb': int(parts[4]),  # buffer memory
                            'vmstat_cache_kb': int(parts[5])  # cache memory
                        })
                        
                        # Convert to MB
                        for key in ['vmstat_swpd_kb', 'vmstat_free_kb', 'vmstat_buff_kb', 'vmstat_cache_kb']:
                            if key in memory_info:
                                mb_key = key.replace('_kb', '_mb')
                                memory_info[mb_key] = round(memory_info[key] / 1024, 2)
                                
        except Exception as e:
            self.logger.debug(f"vmstat memory failed: {e}")
            
        return memory_info
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get Linux-specific process metrics.
        
        Returns:
            Dict containing process metrics
        """
        metrics = {}
        
        try:
            # Get process information from /proc
            if self._tools_available['proc_available']:
                proc_process_info = self._get_process_info_proc()
                metrics.update(proc_process_info)
                
        except Exception as e:
            self.logger.error(f"Error getting process metrics: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.get_process_metrics")
            
        return metrics
    
    def _get_process_info_proc(self) -> Dict[str, Any]:
        """Get process information from /proc.
        
        Returns:
            Dict containing proc process information
        """
        process_info = {}
        
        try:
            # Count processes by reading /proc
            process_count = 0
            zombie_count = 0
            
            for item in os.listdir('/proc'):
                if item.isdigit():
                    process_count += 1
                    
                    # Check if process is zombie
                    try:
                        stat_file = f'/proc/{item}/stat'
                        if os.path.exists(stat_file):
                            with open(stat_file, 'r') as f:
                                stat_line = f.read().strip()
                                parts = stat_line.split()
                                if len(parts) >= 3 and parts[2] == 'Z':
                                    zombie_count += 1
                    except (IOError, IndexError):
                        continue
            
            process_info.update({
                'total_processes_proc_count': process_count,
                'zombie_processes_proc': zombie_count,
                'active_processes_proc': process_count - zombie_count
            })
            
        except Exception as e:
            self.logger.debug(f"proc process info failed: {e}")
            
        return process_info
    
    def get_additional_metrics(self) -> Dict[str, Any]:
        """Get additional Linux-specific metrics.
        
        Returns:
            Dict containing additional metrics
        """
        metrics = {}
        
        try:
            # Get system uptime
            uptime_info = self._get_uptime_info()
            metrics.update(uptime_info)
            
            # Get Linux distribution information
            distro_info = self._get_distro_info()
            metrics.update(distro_info)
            
            # Get kernel information
            kernel_info = self._get_kernel_info()
            metrics.update(kernel_info)
            
        except Exception as e:
            self.logger.error(f"Error getting additional metrics: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.get_additional_metrics")
            
        return metrics
    
    def _get_uptime_info(self) -> Dict[str, Any]:
        """Get system uptime information.
        
        Returns:
            Dict containing uptime information
        """
        uptime_info = {}
        
        try:
            with open('/proc/uptime', 'r') as f:
                content = f.read().strip()
            
            parts = content.split()
            if len(parts) >= 2:
                uptime_seconds = float(parts[0])
                idle_seconds = float(parts[1])
                
                uptime_info.update({
                    'uptime_seconds_proc': uptime_seconds,
                    'uptime_hours_proc': round(uptime_seconds / 3600, 2),
                    'idle_seconds_proc': idle_seconds,
                    'idle_hours_proc': round(idle_seconds / 3600, 2)
                })
                
        except Exception as e:
            self.logger.debug(f"Uptime info failed: {e}")
            
        return uptime_info
    
    def _get_distro_info(self) -> Dict[str, Any]:
        """Get Linux distribution information.
        
        Returns:
            Dict containing distribution information
        """
        distro_info = {}
        
        try:
            # Try /etc/os-release
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            key = key.lower()
                            value = value.strip('"')
                            distro_info[f'distro_{key}'] = value
            
            # Try lsb_release
            try:
                result = subprocess.run(
                    ['lsb_release', '-a'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace(' ', '_')
                            value = value.strip()
                            if value and value != 'n/a':
                                distro_info[f'lsb_{key}'] = value
                                
            except FileNotFoundError:
                pass
                
        except Exception as e:
            self.logger.debug(f"Distro info failed: {e}")
            
        return distro_info
    
    def _get_kernel_info(self) -> Dict[str, Any]:
        """Get kernel information.
        
        Returns:
            Dict containing kernel information
        """
        kernel_info = {}
        
        try:
            # Get kernel version from /proc/version
            if os.path.exists('/proc/version'):
                with open('/proc/version', 'r') as f:
                    version_line = f.read().strip()
                    kernel_info['kernel_version_proc'] = version_line
            
            # Get kernel release from uname
            try:
                result = subprocess.run(
                    ['uname', '-r'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    kernel_info['kernel_release'] = result.stdout.strip()
                    
            except FileNotFoundError:
                pass
                
        except Exception as e:
            self.logger.debug(f"Kernel info failed: {e}")
            
        return kernel_info
    
    def get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature using Linux-specific methods.
        
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
            # Try /proc/cpuinfo
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    content = f.read()
                
                processor_count = content.count('processor\t:')
                fallback_info['cpu_logical_cores'] = processor_count
                
                # Try to get model name
                for line in content.split('\n'):
                    if line.startswith('model name'):
                        _, model = line.split(':', 1)
                        fallback_info['cpu_model'] = model.strip()
                        break
                        
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
            # Try /proc/meminfo
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith('MemTotal:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            total_kb = int(match.group(1))
                            fallback_info.update({
                                'memory_total': total_kb * 1024,
                                'memory_total_gb': round(total_kb / (1024**2), 2)
                            })
                    elif line.startswith('MemAvailable:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            available_kb = int(match.group(1))
                            fallback_info.update({
                                'memory_available': available_kb * 1024,
                                'memory_available_gb': round(available_kb / (1024**2), 2)
                            })
                            
                            # Calculate percentage if we have total
                            if 'memory_total' in fallback_info:
                                total = fallback_info['memory_total']
                                used = total - (available_kb * 1024)
                                fallback_info['memory_percent'] = round((used / total) * 100, 2)
                            break
                            
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
            # Count processes in /proc
            if os.path.exists('/proc'):
                process_count = 0
                for item in os.listdir('/proc'):
                    if item.isdigit():
                        process_count += 1
                
                fallback_info['total_processes'] = process_count
                
        except Exception as e:
            self.logger.debug(f"Fallback process info failed: {e}")
            
        return fallback_info
    
    def cleanup(self) -> None:
        """Clean up Linux-specific resources."""
        try:
            # Clear caches
            self._cpu_info_cache = None
            self._cache_timestamp = 0
            
            self.logger.debug("Linux performance implementation cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            error_handler.handle_error(e, "LinuxPerformanceImpl.cleanup")