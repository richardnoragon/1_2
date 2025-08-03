#!/usr/bin/env python3
"""
Cross-Platform Utilities
========================

This module provides cross-platform utilities for virtual environment setup,
including platform detection, system requirements validation, and
platform-specific operations.

Features:
- Comprehensive platform detection and validation
- System requirements checking (disk space, memory, etc.)
- Build tools and compiler detection
- Network connectivity validation
- Platform-specific path handling
- System dependency verification
"""

import sys
import platform
import subprocess
import shutil
import socket
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None


class PlatformUtils:
    """Cross-platform utilities for system operations and validation."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize platform utilities.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.platform_info = self._detect_platform()
        
    def _detect_platform(self) -> Dict[str, Union[str, bool]]:
        """Detect comprehensive platform information.
        
        Returns:
            Dictionary with platform details
        """
        system = platform.system().lower()
        
        info = {
            'system': system,
            'is_windows': system == 'windows',
            'is_macos': system == 'darwin',
            'is_linux': system == 'linux',
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'release': platform.release(),
            'version': platform.version(),
            'node': platform.node(),
            'platform_string': platform.platform(),
        }
        
        # Add Windows-specific information
        if info['is_windows']:
            info.update(self._get_windows_info())
        
        # Add macOS-specific information
        elif info['is_macos']:
            info.update(self._get_macos_info())
        
        # Add Linux-specific information
        elif info['is_linux']:
            info.update(self._get_linux_info())
        
        return info
    
    def _get_windows_info(self) -> Dict[str, str]:
        """Get Windows-specific information."""
        info = {}
        try:
            import winreg
            
            # Get Windows version from registry
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                try:
                    info['windows_version'] = winreg.QueryValueEx(
                        key, "ProductName")[0]
                except FileNotFoundError:
                    info['windows_version'] = "Unknown"
                
                try:
                    info['windows_build'] = winreg.QueryValueEx(
                        key, "CurrentBuild")[0]
                except FileNotFoundError:
                    info['windows_build'] = "Unknown"
        
        except ImportError:
            info['windows_version'] = "Unknown"
            info['windows_build'] = "Unknown"
        
        return info
    
    def _get_macos_info(self) -> Dict[str, str]:
        """Get macOS-specific information."""
        info = {}
        try:
            # Get macOS version
            mac_version = platform.mac_ver()[0]
            info['macos_version'] = mac_version
            
            # Get Xcode version if available
            try:
                result = subprocess.run(['xcodebuild', '-version'],
                                        capture_output=True, text=True,
                                        timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        info['xcode_version'] = lines[0]
                else:
                    info['xcode_version'] = "Not installed"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                info['xcode_version'] = "Not installed"
        
        except Exception:
            info['macos_version'] = "Unknown"
            info['xcode_version'] = "Unknown"
        
        return info
    
    def _get_linux_info(self) -> Dict[str, str]:
        """Get Linux-specific information."""
        info = {}
        
        # Try to get distribution information
        try:
            if hasattr(platform, 'freedesktop_os_release'):
                os_release = platform.freedesktop_os_release()
                info['linux_distribution'] = os_release.get('NAME', 'Unknown')
                info['linux_version'] = os_release.get('VERSION', 'Unknown')
            else:
                # Fallback for older Python versions
                info['linux_distribution'] = "Unknown"
                info['linux_version'] = "Unknown"
        except Exception:
            info['linux_distribution'] = "Unknown"
            info['linux_version'] = "Unknown"
        
        return info
    
    def get_platform_info(self) -> Dict[str, Union[str, bool]]:
        """Get platform information.
        
        Returns:
            Dictionary with platform details
        """
        return self.platform_info.copy()
    
    def check_system_requirements(self,
                                  min_disk_space_gb: float = 2.0,
                                  min_memory_gb: float = 1.0
                                  ) -> Dict[str, bool]:
        """Check system requirements for virtual environment setup.
        
        Args:
            min_disk_space_gb: Minimum required disk space in GB
            min_memory_gb: Minimum required memory in GB
            
        Returns:
            Dictionary with requirement check results
        """
        self.logger.info("Checking system requirements...")
        
        results = {
            'disk_space': False,
            'memory': False,
            'python_version': False,
            'network': False,
            'build_tools': False
        }
        
        # Check disk space
        if HAS_PSUTIL and psutil:
            try:
                disk_usage = psutil.disk_usage('.')
                free_gb = disk_usage.free / (1024**3)
                results['disk_space'] = free_gb >= min_disk_space_gb
                self.logger.info(f"Available disk space: {free_gb:.2f} GB "
                                 f"(required: {min_disk_space_gb} GB)")
            except Exception as e:
                self.logger.error(f"Failed to check disk space: {e}")
        else:
            self.logger.warning("psutil not available, "
                                "skipping disk space check")
            results['disk_space'] = True  # Assume sufficient
        
        # Check memory
        if HAS_PSUTIL and psutil:
            try:
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                results['memory'] = available_gb >= min_memory_gb
                self.logger.info(f"Available memory: {available_gb:.2f} GB "
                                 f"(required: {min_memory_gb} GB)")
            except Exception as e:
                self.logger.error(f"Failed to check memory: {e}")
        else:
            self.logger.warning("psutil not available, skipping memory check")
            results['memory'] = True  # Assume sufficient
        
        # Check Python version
        try:
            version_info = sys.version_info
            results['python_version'] = (version_info.major == 3 and
                                         version_info.minor >= 7)
            self.logger.info(f"Python version: {sys.version}")
        except Exception as e:
            self.logger.error(f"Failed to check Python version: {e}")
        
        # Check network connectivity
        results['network'] = self.check_network_connectivity()
        
        # Check build tools
        results['build_tools'] = self.check_build_tools()
        
        return results
    
    def check_network_connectivity(self,
                                   test_urls: Optional[List[str]] = None,
                                   timeout: int = 10) -> bool:
        """Check network connectivity to PyPI and other services.
        
        Args:
            test_urls: List of URLs to test (defaults to PyPI)
            timeout: Connection timeout in seconds
            
        Returns:
            True if network is accessible, False otherwise
        """
        if test_urls is None:
            test_urls = [
                'https://pypi.org',
                'https://files.pythonhosted.org',
                'https://www.python.org'
            ]
        
        self.logger.info("Checking network connectivity...")
        
        for url in test_urls:
            try:
                with urllib.request.urlopen(url, timeout=timeout) as response:
                    if response.getcode() == 200:
                        self.logger.info(f"Network connectivity OK: {url}")
                        return True
            except (urllib.error.URLError, socket.timeout) as e:
                self.logger.debug(f"Failed to connect to {url}: {e}")
                continue
        
        self.logger.warning("Network connectivity check failed")
        return False
    
    def check_build_tools(self) -> bool:
        """Check for required build tools on the current platform.
        
        Returns:
            True if build tools are available, False otherwise
        """
        self.logger.info("Checking build tools...")
        
        if self.platform_info['is_windows']:
            return self._check_windows_build_tools()
        elif self.platform_info['is_macos']:
            return self._check_macos_build_tools()
        elif self.platform_info['is_linux']:
            return self._check_linux_build_tools()
        else:
            self.logger.warning("Unknown platform for build tools check")
            return False
    
    def _check_windows_build_tools(self) -> bool:
        """Check Windows build tools (Visual C++ Build Tools)."""
        # Check for Visual Studio Build Tools
        vs_paths = [
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools",
            r"C:\Program Files\Microsoft Visual Studio\2019\Community",
            r"C:\Program Files\Microsoft Visual Studio\2022\Community",
            r"C:\Program Files (x86)\Microsoft Visual Studio 14.0",
        ]
        
        for vs_path in vs_paths:
            if Path(vs_path).exists():
                self.logger.info(f"Found Visual Studio tools: {vs_path}")
                return True
        
        # Check for cl.exe in PATH
        if shutil.which('cl'):
            self.logger.info("Found cl.exe in PATH")
            return True
        
        # Check for Windows SDK
        sdk_paths = [
            r"C:\Program Files (x86)\Windows Kits\10",
            r"C:\Program Files (x86)\Windows Kits\8.1",
        ]
        
        for sdk_path in sdk_paths:
            if Path(sdk_path).exists():
                self.logger.info(f"Found Windows SDK: {sdk_path}")
                return True
        
        self.logger.warning("No Visual C++ build tools found")
        return False
    
    def _check_macos_build_tools(self) -> bool:
        """Check macOS build tools (Xcode Command Line Tools)."""
        # Check for xcode-select
        try:
            result = subprocess.run(['xcode-select', '--print-path'],
                                    capture_output=True, text=True,
                                    timeout=10)
            if result.returncode == 0:
                path = result.stdout.strip()
                self.logger.info(f"Found Xcode tools: {path}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for common build tools
        tools = ['gcc', 'clang', 'make']
        found_tools = []
        
        for tool in tools:
            if shutil.which(tool):
                found_tools.append(tool)
        
        if found_tools:
            self.logger.info(f"Found build tools: {', '.join(found_tools)}")
            return True
        
        self.logger.warning("No build tools found")
        return False
    
    def _check_linux_build_tools(self) -> bool:
        """Check Linux build tools (build-essential, gcc, etc.)."""
        # Check for common build tools
        essential_tools = ['gcc', 'g++', 'make']
        python_dev_tools = ['python3-dev', 'python3-config']
        
        found_tools = []
        
        # Check for essential build tools
        for tool in essential_tools:
            if shutil.which(tool):
                found_tools.append(tool)
        
        # Check for Python development headers
        for tool in python_dev_tools:
            if shutil.which(tool):
                found_tools.append(tool)
        
        # Check for pkg-config
        if shutil.which('pkg-config'):
            found_tools.append('pkg-config')
        
        if len(found_tools) >= 3:  # At least gcc, g++, make
            self.logger.info(f"Found build tools: {', '.join(found_tools)}")
            return True
        
        self.logger.warning(f"Insufficient build tools found: "
                            f"{', '.join(found_tools)}")
        return False
    
    def get_platform_specific_requirements(self) -> List[str]:
        """Get platform-specific requirements and recommendations.
        
        Returns:
            List of requirement messages
        """
        requirements = []
        
        if self.platform_info['is_windows']:
            requirements.extend([
                "Visual C++ Build Tools or Visual Studio Community",
                "Windows SDK (usually included with Visual Studio)",
                "PowerShell 5.1+ for activation scripts"
            ])
            
            if not self._check_windows_build_tools():
                requirements.append(
                    "Install Visual C++ Build Tools from: "
                    "https://visualstudio.microsoft.com/"
                    "visual-cpp-build-tools/"
                )
        
        elif self.platform_info['is_macos']:
            requirements.extend([
                "Xcode Command Line Tools",
                "Homebrew (recommended for package management)"
            ])
            
            if not self._check_macos_build_tools():
                requirements.append(
                    "Install Xcode Command Line Tools: xcode-select --install"
                )
        
        elif self.platform_info['is_linux']:
            requirements.extend([
                "build-essential package (gcc, g++, make)",
                "python3-dev package",
                "pkg-config"
            ])
            
            if not self._check_linux_build_tools():
                # Detect package manager and provide specific instructions
                if shutil.which('apt'):
                    requirements.append(
                        "Install build tools: "
                        "sudo apt install build-essential python3-dev"
                    )
                elif shutil.which('yum'):
                    requirements.append(
                        "Install build tools: "
                        "sudo yum groupinstall 'Development Tools' && "
                        "sudo yum install python3-devel"
                    )
                elif shutil.which('dnf'):
                    requirements.append(
                        "Install build tools: "
                        "sudo dnf groupinstall 'Development Tools' && "
                        "sudo dnf install python3-devel"
                    )
                else:
                    requirements.append(
                        "Install build tools using your distribution's "
                        "package manager"
                    )
        
        return requirements
    
    def validate_python_installation(self) -> Dict[str, Union[bool, str]]:
        """Validate Python installation completeness.
        
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating Python installation...")
        
        results = {
            'python_executable': False,
            'pip_available': False,
            'venv_module': False,
            'ssl_support': False,
            'tkinter_support': False,
            'python_path': '',
            'pip_version': '',
            'issues': []
        }
        
        # Check Python executable
        try:
            results['python_path'] = sys.executable
            results['python_executable'] = True
            self.logger.info(f"Python executable: {sys.executable}")
        except Exception as e:
            results['issues'].append(f"Python executable issue: {e}")
        
        # Check pip availability
        try:
            import pip
            results['pip_available'] = True
            results['pip_version'] = pip.__version__
            self.logger.info(f"pip version: {pip.__version__}")
        except ImportError:
            results['issues'].append("pip not available")
        
        # Check venv module
        try:
            import venv  # noqa: F401
            results['venv_module'] = True
            self.logger.info("venv module available")
        except ImportError:
            results['issues'].append("venv module not available")
        
        # Check SSL support
        try:
            import ssl  # noqa: F401
            results['ssl_support'] = True
            self.logger.info("SSL support available")
        except ImportError:
            results['issues'].append("SSL support not available")
        
        # Check tkinter support (for GUI applications)
        try:
            import tkinter  # noqa: F401
            results['tkinter_support'] = True
            self.logger.info("tkinter support available")
        except ImportError:
            results['issues'].append("tkinter support not available")
        
        return results
    
    def get_recommended_python_path(self) -> Optional[str]:
        """Get recommended Python executable path for the current platform.
        
        Returns:
            Path to recommended Python executable or None
        """
        if self.platform_info['is_windows']:
            # On Windows, prefer py launcher, then python, then python3
            candidates = ['py', 'python', 'python3']
        else:
            # On Unix-like systems, prefer python3, then python
            candidates = ['python3', 'python']
        
        for candidate in candidates:
            path = shutil.which(candidate)
            if path:
                try:
                    # Verify it's Python 3.7+
                    result = subprocess.run([path, '--version'],
                                            capture_output=True, text=True,
                                            timeout=5)
                    if 'Python 3.' in result.stdout:
                        version_parts = result.stdout.split()[1].split('.')
                        major = int(version_parts[0])
                        minor = int(version_parts[1])
                        if major == 3 and minor >= 7:
                            self.logger.info(f"Recommended Python: {path}")
                            return path
                except (subprocess.TimeoutExpired, ValueError, IndexError):
                    continue
        
        return None
    
    def create_platform_report(self) -> str:
        """Create a comprehensive platform report.
        
        Returns:
            Formatted platform report string
        """
        report_lines = [
            "=" * 60,
            "PLATFORM REPORT",
            "=" * 60,
            "",
            "System Information:",
            f"  Operating System: {str(self.platform_info['system']).title()}",
            f"  Architecture: {self.platform_info['architecture']}",
            f"  Processor: {self.platform_info['processor']}",
            f"  Platform: {self.platform_info['platform_string']}",
            "",
            "Python Information:",
            f"  Version: {self.platform_info['python_version']}",
            f"  Implementation: {self.platform_info['python_implementation']}",
            f"  Executable: {sys.executable}",
            "",
        ]
        
        # Add platform-specific information
        if self.platform_info['is_windows']:
            report_lines.extend([
                "Windows Specific:",
                f"  Version: "
                f"{self.platform_info.get('windows_version', 'Unknown')}",
                f"  Build: "
                f"{self.platform_info.get('windows_build', 'Unknown')}",
                "",
            ])
        elif self.platform_info['is_macos']:
            report_lines.extend([
                "macOS Specific:",
                f"  Version: "
                f"{self.platform_info.get('macos_version', 'Unknown')}",
                f"  Xcode: "
                f"{self.platform_info.get('xcode_version', 'Unknown')}",
                "",
            ])
        elif self.platform_info['is_linux']:
            report_lines.extend([
                "Linux Specific:",
                f"  Distribution: "
                f"{self.platform_info.get('linux_distribution', 'Unknown')}",
                f"  Version: "
                f"{self.platform_info.get('linux_version', 'Unknown')}",
                "",
            ])
        
        # Add system requirements check
        requirements = self.check_system_requirements()
        report_lines.extend([
            "System Requirements:",
            f"  Disk Space: {'✅' if requirements['disk_space'] else '❌'}",
            f"  Memory: {'✅' if requirements['memory'] else '❌'}",
            f"  Python Version: "
            f"{'✅' if requirements['python_version'] else '❌'}",
            f"  Network: {'✅' if requirements['network'] else '❌'}",
            f"  Build Tools: {'✅' if requirements['build_tools'] else '❌'}",
            "",
        ])
        
        # Add platform-specific requirements
        platform_reqs = self.get_platform_specific_requirements()
        if platform_reqs:
            report_lines.extend([
                "Platform Requirements:",
            ])
            for req in platform_reqs:
                report_lines.append(f"  - {req}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)