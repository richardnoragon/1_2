"""Platform detection utilities for cross-platform monitoring."""

import platform
import sys
from enum import Enum
from typing import Dict, Any, Optional
import logging


class SupportedPlatform(Enum):
    """Enumeration of supported platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class PlatformDetector:
    """Detects the current platform and provides platform-specific utils."""
    
    def __init__(self):
        """Initialize the platform detector."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.PlatformDetector'
        )
        self._platform = self._detect_platform()
        self._platform_info = self._gather_platform_info()
        
    def _detect_platform(self) -> SupportedPlatform:
        """Detect the current platform.
        
        Returns:
            SupportedPlatform: The detected platform
        """
        system = platform.system().lower()
        
        if system == "windows":
            return SupportedPlatform.WINDOWS
        elif system == "darwin":
            return SupportedPlatform.MACOS
        elif system == "linux":
            return SupportedPlatform.LINUX
        else:
            self.logger.warning(f"Unknown platform detected: {system}")
            return SupportedPlatform.UNKNOWN
    
    def _gather_platform_info(self) -> Dict[str, Any]:
        """Gather detailed platform information.
        
        Returns:
            Dict containing platform details
        """
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'python_implementation': platform.python_implementation()
        }
        
        # Add platform-specific information
        if self._platform == SupportedPlatform.WINDOWS:
            info.update(self._get_windows_info())
        elif self._platform == SupportedPlatform.MACOS:
            info.update(self._get_macos_info())
        elif self._platform == SupportedPlatform.LINUX:
            info.update(self._get_linux_info())
            
        return info
    
    def _get_windows_info(self) -> Dict[str, Any]:
        """Get Windows-specific information.
        
        Returns:
            Dict containing Windows-specific details
        """
        info = {}
        try:
            import winreg
            
            # Get Windows version from registry
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                try:
                    info['windows_version'] = winreg.QueryValueEx(
                        key, "ProductName"
                    )[0]
                    info['build_number'] = winreg.QueryValueEx(
                        key, "CurrentBuild"
                    )[0]
                    info['display_version'] = winreg.QueryValueEx(
                        key, "DisplayVersion"
                    )[0]
                except FileNotFoundError:
                    pass
                    
        except ImportError:
            self.logger.warning("Windows registry access not available")
        except Exception as e:
            self.logger.error(f"Error getting Windows info: {e}")
            
        return info
    
    def _get_macos_info(self) -> Dict[str, Any]:
        """Get macOS-specific information.
        
        Returns:
            Dict containing macOS-specific details
        """
        info = {}
        try:
            import subprocess
            
            # Get macOS version
            result = subprocess.run(
                ['sw_vers'], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        clean_key = key.strip().lower().replace(' ', '_')
                        info[f"macos_{clean_key}"] = value.strip()
                        
        except Exception as e:
            self.logger.error(f"Error getting macOS info: {e}")
            
        return info
    
    def _get_linux_info(self) -> Dict[str, Any]:
        """Get Linux-specific information.
        
        Returns:
            Dict containing Linux-specific details
        """
        info = {}
        try:
            # Try to read distribution information
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            info[f"linux_{key.lower()}"] = value.strip('"')
            except FileNotFoundError:
                pass
                
            # Get kernel information
            info['kernel_version'] = platform.release()
            
        except Exception as e:
            self.logger.error(f"Error getting Linux info: {e}")
            
        return info
    
    @property
    def platform(self) -> SupportedPlatform:
        """Get the detected platform.
        
        Returns:
            SupportedPlatform: The current platform
        """
        return self._platform
    
    @property
    def platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information.
        
        Returns:
            Dict containing platform details
        """
        return self._platform_info.copy()
    
    def is_windows(self) -> bool:
        """Check if running on Windows.
        
        Returns:
            bool: True if Windows, False otherwise
        """
        return self._platform == SupportedPlatform.WINDOWS
    
    def is_macos(self) -> bool:
        """Check if running on macOS.
        
        Returns:
            bool: True if macOS, False otherwise
        """
        return self._platform == SupportedPlatform.MACOS
    
    def is_linux(self) -> bool:
        """Check if running on Linux.
        
        Returns:
            bool: True if Linux, False otherwise
        """
        return self._platform == SupportedPlatform.LINUX
    
    def is_supported(self) -> bool:
        """Check if the current platform is supported.
        
        Returns:
            bool: True if supported, False otherwise
        """
        return self._platform != SupportedPlatform.UNKNOWN
    
    def get_platform_module_name(self, base_name: str) -> str:
        """Get the platform-specific module name.
        
        Args:
            base_name: Base module name
            
        Returns:
            str: Platform-specific module name
        """
        platform_map = {
            SupportedPlatform.WINDOWS: "windows",
            SupportedPlatform.MACOS: "macos", 
            SupportedPlatform.LINUX: "linux"
        }
        
        platform_suffix = platform_map.get(self._platform, "unknown")
        return f"{platform_suffix}_{base_name}"
    
    def requires_admin_privileges(self) -> bool:
        """Check if admin privileges are required for system monitoring.
        
        Returns:
            bool: True if admin privileges needed
        """
        if self.is_windows():
            try:
                import ctypes
                return not ctypes.windll.shell32.IsUserAnAdmin()
            except Exception:
                return True
        elif self.is_linux() or self.is_macos():
            import os
            return os.geteuid() != 0
        else:
            return True
    
    def get_temp_directory(self) -> str:
        """Get the platform-appropriate temporary directory.
        
        Returns:
            str: Path to temporary directory
        """
        import tempfile
        return tempfile.gettempdir()
    
    def get_config_directory(self) -> str:
        """Get the platform-appropriate configuration directory.
        
        Returns:
            str: Path to configuration directory
        """
        import os
        
        if self.is_windows():
            return os.path.expandvars(r"%APPDATA%\RFU\DiagnosticsMonitoring")
        elif self.is_macos():
            return os.path.expanduser(
                "~/Library/Application Support/RFU/DiagnosticsMonitoring"
            )
        elif self.is_linux():
            return os.path.expanduser("~/.config/rfu/diagnostics_monitoring")
        else:
            return os.path.expanduser("~/.rfu_diagnostics")


# Global platform detector instance
_platform_detector: Optional[PlatformDetector] = None


def get_platform_detector() -> PlatformDetector:
    """Get the global platform detector instance.
    
    Returns:
        PlatformDetector: The platform detector instance
    """
    global _platform_detector
    if _platform_detector is None:
        _platform_detector = PlatformDetector()
    return _platform_detector