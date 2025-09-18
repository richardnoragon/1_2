"""Windows-specific performance monitoring implementation.

This module provides Windows-specific optimizations for performance monitoring
including WMI integration, Performance Counters, and Windows API access.
"""

import logging
import time
from typing import Dict, Any, Optional, List
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
    import win32process
    import win32pdh
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from core.error_handler import error_handler


class WindowsPerformanceImpl:
    """Windows-specific performance monitoring implementation.
    
    Provides enhanced performance monitoring using Windows Management
    Instrumentation (WMI), Performance Counters, and Windows APIs.
    """
    
    def __init__(self):
        """Initialize Windows performance implementation."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.WindowsPerformance'
        )
        
        # WMI connection
        self._wmi_conn = None
        self._wmi_available = WMI_AVAILABLE
        
        # Performance counters
        self._perf_counters = {}
        self._counter_handles = {}
        
        # Windows API availability
        self._win32_available = WIN32_AVAILABLE
        
        # Initialize connections
        self._initialize_wmi()
        self._initialize_performance_counters()
        
        self.logger.info("Windows performance implementation initialized")
    
    def _initialize_wmi(self) -> None:
        """Initialize WMI connection."""
        if not self._wmi_available:
            self.logger.warning("WMI not available")
            return
            
        try:
            self._wmi_conn = wmi.WMI()
            self.logger.debug("WMI connection established")
        except Exception as e:
            self.logger.error(f"Failed to initialize WMI: {e}")
            self._wmi_available = False
            error_handler.handle_error(e, "WindowsPerformanceImpl._initialize_wmi")
    
    def _initialize_performance_counters(self) -> None:
        """Initialize Windows Performance Counters."""
        if not self._win32_available:
            self.logger.warning("Win32 APIs not available")
            return
            
        try:
            # Initialize performance counter paths
            counter_paths = {
                'cpu_usage': r'\Processor(_Total)\% Processor Time',
                'memory_available': r'\Memory\Available MBytes',
                'memory_committed': r'\Memory\Committed Bytes',
                'memory_cache': r'\Memory\Cache Bytes',
                'memory_pool_paged': r'\Memory\Pool Paged Bytes',
                'memory_pool_nonpaged': r'\Memory\Pool Nonpaged Bytes',
                'system_calls': r'\System\System Calls/sec',
                'context_switches': r'\System\Context Switches/sec',
                'processes': r'\System\Processes',
                'threads': r'\System\Threads'
            }
            
            # Create performance counter handles
            for name, path in counter_paths.items():
                try:
                    handle = win32pdh.OpenQuery()
                    counter = win32pdh.AddCounter(handle, path)
                    self._counter_handles[name] = (handle, counter)
                    self.logger.debug(f"Initialized counter: {name}")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize counter {name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize performance counters: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl._initialize_performance_counters")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get Windows-specific CPU information.
        
        Returns:
            Dict containing CPU information
        """
        cpu_info = {}
        
        try:
            if self._wmi_available and self._wmi_conn:
                # Get CPU information from WMI
                processors = self._wmi_conn.Win32_Processor()
                
                if processors:
                    processor = processors[0]
                    cpu_info.update({
                        'vendor': processor.Manufacturer,
                        'brand': processor.Name,
                        'architecture': processor.Architecture,
                        'family': processor.Family,
                        'model': processor.Model,
                        'stepping': processor.Stepping,
                        'max_clock_speed': processor.MaxClockSpeed,
                        'current_clock_speed': processor.CurrentClockSpeed,
                        'voltage': processor.CurrentVoltage,
                        'socket_designation': processor.SocketDesignation,
                        'l2_cache_size': processor.L2CacheSize,
                        'l3_cache_size': processor.L3CacheSize
                    })
                    
                    # Get additional processor features
                    if hasattr(processor, 'ProcessorId'):
                        cpu_info['processor_id'] = processor.ProcessorId
                    if hasattr(processor, 'Characteristics'):
                        cpu_info['characteristics'] = processor.Characteristics
                        
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.get_cpu_info")
            
        return cpu_info
    
    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get Windows-specific CPU metrics.
        
        Returns:
            Dict containing CPU metrics
        """
        metrics = {}
        
        try:
            # Get CPU usage from performance counters
            if 'cpu_usage' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['cpu_usage']
                    win32pdh.CollectQueryData(handle)
                    time.sleep(0.1)  # Brief pause for accurate measurement
                    win32pdh.CollectQueryData(handle)
                    
                    _, cpu_usage = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    metrics['cpu_usage_perfcounter'] = round(cpu_usage, 2)
                    
                except Exception as e:
                    self.logger.debug(f"Performance counter CPU usage failed: {e}")
            
            # Get system performance metrics
            if 'system_calls' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['system_calls']
                    win32pdh.CollectQueryData(handle)
                    _, calls_per_sec = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    metrics['system_calls_per_sec'] = round(calls_per_sec, 2)
                except Exception as e:
                    self.logger.debug(f"System calls counter failed: {e}")
            
            if 'context_switches' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['context_switches']
                    win32pdh.CollectQueryData(handle)
                    _, switches_per_sec = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    metrics['context_switches_per_sec'] = round(switches_per_sec, 2)
                except Exception as e:
                    self.logger.debug(f"Context switches counter failed: {e}")
            
            # Get CPU temperature from WMI if available
            temperature_info = self._get_cpu_temperature_wmi()
            metrics.update(temperature_info)
            
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.get_cpu_metrics")
            
        return metrics
    
    def get_memory_details(self) -> Dict[str, Any]:
        """Get Windows-specific memory details.
        
        Returns:
            Dict containing memory information
        """
        memory_info = {}
        
        try:
            # Get memory information from performance counters
            if 'memory_available' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['memory_available']
                    win32pdh.CollectQueryData(handle)
                    _, available_mb = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    memory_info['available_mb_perfcounter'] = round(available_mb, 2)
                except Exception as e:
                    self.logger.debug(f"Available memory counter failed: {e}")
            
            if 'memory_committed' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['memory_committed']
                    win32pdh.CollectQueryData(handle)
                    _, committed_bytes = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    memory_info['committed_bytes'] = int(committed_bytes)
                    memory_info['committed_gb'] = round(committed_bytes / (1024**3), 2)
                except Exception as e:
                    self.logger.debug(f"Committed memory counter failed: {e}")
            
            # Get memory pool information
            pool_info = self._get_memory_pool_info()
            memory_info.update(pool_info)
            
            # Get memory information from WMI
            wmi_memory_info = self._get_memory_info_wmi()
            memory_info.update(wmi_memory_info)
            
        except Exception as e:
            self.logger.error(f"Error getting memory details: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.get_memory_details")
            
        return memory_info
    
    def _get_memory_pool_info(self) -> Dict[str, Any]:
        """Get Windows memory pool information.
        
        Returns:
            Dict containing memory pool information
        """
        pool_info = {}
        
        try:
            if 'memory_pool_paged' in self._counter_handles:
                handle, counter = self._counter_handles['memory_pool_paged']
                win32pdh.CollectQueryData(handle)
                _, paged_pool = win32pdh.GetFormattedCounterValue(
                    counter, win32pdh.PDH_FMT_DOUBLE
                )
                pool_info['paged_pool_bytes'] = int(paged_pool)
                pool_info['paged_pool_mb'] = round(paged_pool / (1024**2), 2)
            
            if 'memory_pool_nonpaged' in self._counter_handles:
                handle, counter = self._counter_handles['memory_pool_nonpaged']
                win32pdh.CollectQueryData(handle)
                _, nonpaged_pool = win32pdh.GetFormattedCounterValue(
                    counter, win32pdh.PDH_FMT_DOUBLE
                )
                pool_info['nonpaged_pool_bytes'] = int(nonpaged_pool)
                pool_info['nonpaged_pool_mb'] = round(nonpaged_pool / (1024**2), 2)
                
        except Exception as e:
            self.logger.debug(f"Memory pool info failed: {e}")
            
        return pool_info
    
    def _get_memory_info_wmi(self) -> Dict[str, Any]:
        """Get memory information from WMI.
        
        Returns:
            Dict containing WMI memory information
        """
        memory_info = {}
        
        try:
            if self._wmi_available and self._wmi_conn:
                # Get physical memory information
                memory_modules = self._wmi_conn.Win32_PhysicalMemory()
                
                total_capacity = 0
                module_count = 0
                speeds = []
                
                for module in memory_modules:
                    if module.Capacity:
                        total_capacity += int(module.Capacity)
                        module_count += 1
                    if module.Speed:
                        speeds.append(int(module.Speed))
                
                if total_capacity > 0:
                    memory_info.update({
                        'physical_memory_total': total_capacity,
                        'physical_memory_total_gb': round(total_capacity / (1024**3), 2),
                        'memory_module_count': module_count
                    })
                
                if speeds:
                    memory_info['memory_speed_mhz'] = max(speeds)
                
                # Get operating system memory information
                os_info = self._wmi_conn.Win32_OperatingSystem()
                if os_info:
                    os = os_info[0]
                    if hasattr(os, 'TotalVisibleMemorySize'):
                        visible_memory = int(os.TotalVisibleMemorySize) * 1024
                        memory_info['visible_memory_bytes'] = visible_memory
                        memory_info['visible_memory_gb'] = round(visible_memory / (1024**3), 2)
                    
                    if hasattr(os, 'FreePhysicalMemory'):
                        free_memory = int(os.FreePhysicalMemory) * 1024
                        memory_info['free_physical_memory'] = free_memory
                        memory_info['free_physical_memory_gb'] = round(free_memory / (1024**3), 2)
                        
        except Exception as e:
            self.logger.debug(f"WMI memory info failed: {e}")
            
        return memory_info
    
    def _get_cpu_temperature_wmi(self) -> Dict[str, Any]:
        """Get CPU temperature from WMI.
        
        Returns:
            Dict containing temperature information
        """
        temp_info = {}
        
        try:
            if self._wmi_available and self._wmi_conn:
                # Try to get temperature from thermal zone
                thermal_zones = self._wmi_conn.Win32_PerfRawData_Counters_ThermalZoneInformation()
                
                temperatures = []
                for zone in thermal_zones:
                    if hasattr(zone, 'Temperature') and zone.Temperature:
                        # Convert from tenths of Kelvin to Celsius
                        temp_celsius = (int(zone.Temperature) / 10) - 273.15
                        if 0 < temp_celsius < 150:  # Reasonable temperature range
                            temperatures.append(temp_celsius)
                
                if temperatures:
                    temp_info.update({
                        'cpu_temperature_wmi': round(sum(temperatures) / len(temperatures), 1),
                        'cpu_temperature_zones': [round(temp, 1) for temp in temperatures],
                        'cpu_temperature_max_wmi': round(max(temperatures), 1),
                        'cpu_temperature_min_wmi': round(min(temperatures), 1)
                    })
                    
        except Exception as e:
            self.logger.debug(f"WMI temperature failed: {e}")
            
        return temp_info
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get Windows-specific process metrics.
        
        Returns:
            Dict containing process metrics
        """
        metrics = {}
        
        try:
            # Get process and thread counts from performance counters
            if 'processes' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['processes']
                    win32pdh.CollectQueryData(handle)
                    _, process_count = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_LONG
                    )
                    metrics['total_processes_perfcounter'] = process_count
                except Exception as e:
                    self.logger.debug(f"Process count counter failed: {e}")
            
            if 'threads' in self._counter_handles:
                try:
                    handle, counter = self._counter_handles['threads']
                    win32pdh.CollectQueryData(handle)
                    _, thread_count = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_LONG
                    )
                    metrics['total_threads_perfcounter'] = thread_count
                except Exception as e:
                    self.logger.debug(f"Thread count counter failed: {e}")
            
            # Get Windows-specific process information
            if self._wmi_available and self._wmi_conn:
                wmi_process_info = self._get_process_info_wmi()
                metrics.update(wmi_process_info)
                
        except Exception as e:
            self.logger.error(f"Error getting process metrics: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.get_process_metrics")
            
        return metrics
    
    def _get_process_info_wmi(self) -> Dict[str, Any]:
        """Get process information from WMI.
        
        Returns:
            Dict containing WMI process information
        """
        process_info = {}
        
        try:
            # Get process performance data
            processes = self._wmi_conn.Win32_PerfRawData_PerfProc_Process()
            
            total_handles = 0
            total_page_faults = 0
            process_count = 0
            
            for process in processes:
                if process.Name and process.Name != '_Total':
                    process_count += 1
                    
                    if hasattr(process, 'HandleCount') and process.HandleCount:
                        total_handles += int(process.HandleCount)
                    
                    if hasattr(process, 'PageFaultsPersec') and process.PageFaultsPersec:
                        total_page_faults += int(process.PageFaultsPersec)
            
            if process_count > 0:
                process_info.update({
                    'total_handles': total_handles,
                    'avg_handles_per_process': round(total_handles / process_count, 2),
                    'total_page_faults_per_sec': total_page_faults
                })
                
        except Exception as e:
            self.logger.debug(f"WMI process info failed: {e}")
            
        return process_info
    
    def get_additional_metrics(self) -> Dict[str, Any]:
        """Get additional Windows-specific metrics.
        
        Returns:
            Dict containing additional metrics
        """
        metrics = {}
        
        try:
            # Get system uptime
            if self._wmi_available and self._wmi_conn:
                os_info = self._wmi_conn.Win32_OperatingSystem()
                if os_info:
                    os = os_info[0]
                    if hasattr(os, 'LastBootUpTime'):
                        boot_time = os.LastBootUpTime
                        # Parse WMI datetime format
                        if boot_time:
                            try:
                                boot_datetime = datetime.strptime(
                                    boot_time.split('.')[0], '%Y%m%d%H%M%S'
                                )
                                uptime_seconds = (datetime.now() - boot_datetime).total_seconds()
                                metrics.update({
                                    'uptime_seconds_wmi': uptime_seconds,
                                    'uptime_hours_wmi': round(uptime_seconds / 3600, 2),
                                    'boot_time_wmi': boot_datetime.isoformat()
                                })
                            except ValueError:
                                pass
            
            # Get Windows version information
            version_info = self._get_windows_version_info()
            metrics.update(version_info)
            
        except Exception as e:
            self.logger.error(f"Error getting additional metrics: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.get_additional_metrics")
            
        return metrics
    
    def _get_windows_version_info(self) -> Dict[str, Any]:
        """Get Windows version information.
        
        Returns:
            Dict containing Windows version information
        """
        version_info = {}
        
        try:
            if self._wmi_available and self._wmi_conn:
                os_info = self._wmi_conn.Win32_OperatingSystem()
                if os_info:
                    os = os_info[0]
                    version_info.update({
                        'windows_version': os.Version,
                        'windows_caption': os.Caption,
                        'windows_build_number': os.BuildNumber,
                        'windows_service_pack': os.ServicePackMajorVersion,
                        'windows_architecture': os.OSArchitecture
                    })
                    
        except Exception as e:
            self.logger.debug(f"Windows version info failed: {e}")
            
        return version_info
    
    def get_cpu_temperature(self) -> Dict[str, Any]:
        """Get CPU temperature using Windows-specific methods.
        
        Returns:
            Dict containing temperature information
        """
        return self._get_cpu_temperature_wmi()
    
    def get_fallback_cpu_info(self) -> Dict[str, Any]:
        """Get fallback CPU information when psutil is not available.
        
        Returns:
            Dict containing basic CPU information
        """
        fallback_info = {}
        
        try:
            if self._win32_available:
                # Get basic system information
                system_info = win32api.GetSystemInfo()
                fallback_info.update({
                    'cpu_logical_cores': system_info[5],  # Number of processors
                    'processor_architecture': system_info[0]
                })
                
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
            if self._win32_available:
                # Get memory status
                memory_status = win32api.GlobalMemoryStatus()
                fallback_info.update({
                    'memory_total': memory_status['TotalPhys'],
                    'memory_available': memory_status['AvailPhys'],
                    'memory_percent': round(
                        ((memory_status['TotalPhys'] - memory_status['AvailPhys']) / 
                         memory_status['TotalPhys']) * 100, 2
                    )
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
            # Use performance counters if available
            if 'processes' in self._counter_handles:
                handle, counter = self._counter_handles['processes']
                win32pdh.CollectQueryData(handle)
                _, process_count = win32pdh.GetFormattedCounterValue(
                    counter, win32pdh.PDH_FMT_LONG
                )
                fallback_info['total_processes'] = process_count
                
        except Exception as e:
            self.logger.debug(f"Fallback process info failed: {e}")
            
        return fallback_info
    
    def cleanup(self) -> None:
        """Clean up Windows-specific resources."""
        try:
            # Close performance counter handles
            for name, (handle, counter) in self._counter_handles.items():
                try:
                    win32pdh.CloseQuery(handle)
                except Exception as e:
                    self.logger.debug(f"Error closing counter {name}: {e}")
            
            self._counter_handles.clear()
            
            # Close WMI connection
            if self._wmi_conn:
                self._wmi_conn = None
                
            self.logger.debug("Windows performance implementation cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            error_handler.handle_error(e, "WindowsPerformanceImpl.cleanup")