"""
Software Detection and Management for Software Maintenance Toolkit

This module provides comprehensive software detection capabilities across
Windows, macOS, and Linux platforms, including registry scanning, package
manager integration, and application discovery.
"""

import os
import sys
import json
import subprocess
import winreg
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

from .maintenance_base import MaintenanceToolBase


@dataclass
class SoftwareInfo:
    """Data class representing installed software information."""
    name: str
    version: str
    publisher: str = ""
    install_date: Optional[datetime] = None
    install_location: str = ""
    uninstall_string: str = ""
    size_mb: Optional[float] = None
    registry_key: str = ""
    package_manager: str = ""
    architecture: str = ""
    is_system_component: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'publisher': self.publisher,
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'install_location': self.install_location,
            'uninstall_string': self.uninstall_string,
            'size_mb': self.size_mb,
            'registry_key': self.registry_key,
            'package_manager': self.package_manager,
            'architecture': self.architecture,
            'is_system_component': self.is_system_component
        }


class SoftwareDetector(MaintenanceToolBase):
    """
    Comprehensive software detection and management system supporting
    multiple platforms and package managers.
    """
    
    def __init__(self):
        super().__init__("Software Detector")
        
        self.detected_software: Dict[str, SoftwareInfo] = {}
        self.package_managers = self._detect_package_managers()
        self.platform = sys.platform
        
        # Registry paths for Windows software detection
        self.registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, 
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, 
             r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, 
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        # System components to potentially filter out
        self.system_components = {
            'Microsoft Visual C++',
            'Microsoft .NET Framework',
            'Windows SDK',
            'Microsoft Office',
            'Internet Explorer',
            'Windows Media Player',
            'Windows Defender'
        }
    
    def _detect_package_managers(self) -> List[str]:
        """Detect available package managers on the system."""
        managers = []
        
        if sys.platform == "win32":
            # Check for Windows package managers
            if self._command_exists("choco"):
                managers.append("chocolatey")
            if self._command_exists("winget"):
                managers.append("winget")
            if self._command_exists("scoop"):
                managers.append("scoop")
        
        elif sys.platform == "darwin":
            # Check for macOS package managers
            if self._command_exists("brew"):
                managers.append("homebrew")
            if self._command_exists("port"):
                managers.append("macports")
        
        else:
            # Check for Linux package managers
            if self._command_exists("apt"):
                managers.append("apt")
            if self._command_exists("yum"):
                managers.append("yum")
            if self._command_exists("dnf"):
                managers.append("dnf")
            if self._command_exists("pacman"):
                managers.append("pacman")
            if self._command_exists("zypper"):
                managers.append("zypper")
            if self._command_exists("snap"):
                managers.append("snap")
            if self._command_exists("flatpak"):
                managers.append("flatpak")
        
        self.log_info(f"Detected package managers: {', '.join(managers)}")
        return managers
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, 
                         check=False, 
                         timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def scan_registry_software(self) -> Dict[str, SoftwareInfo]:
        """Scan Windows registry for installed software."""
        if sys.platform != "win32":
            return {}
        
        software_dict = {}
        self.update_status("Scanning Windows registry for installed software...")
        
        for hive, subkey in self.registry_paths:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            software_info = self._read_registry_entry(hive, 
                                                                    f"{subkey}\\{subkey_name}")
                            
                            if software_info and software_info.name:
                                # Use name + version as unique key
                                unique_key = f"{software_info.name}_{software_info.version}"
                                software_dict[unique_key] = software_info
                            
                            i += 1
                            
                        except OSError:
                            break
                            
            except Exception as e:
                self.log_warning(f"Error scanning registry path {subkey}: {e}")
        
        self.log_info(f"Found {len(software_dict)} applications in registry")
        return software_dict
    
    def _read_registry_entry(self, hive, subkey_path: str) -> Optional[SoftwareInfo]:
        """Read a single registry entry for software information."""
        try:
            with winreg.OpenKey(hive, subkey_path) as key:
                # Read common registry values
                values = {}
                for value_name in ['DisplayName', 'DisplayVersion', 'Publisher',
                                 'InstallDate', 'InstallLocation', 'UninstallString',
                                 'EstimatedSize', 'SystemComponent']:
                    try:
                        values[value_name] = winreg.QueryValueEx(key, value_name)[0]
                    except FileNotFoundError:
                        values[value_name] = None
                
                # Skip if no display name
                if not values.get('DisplayName'):
                    return None
                
                # Parse install date
                install_date = None
                if values.get('InstallDate'):
                    try:
                        date_str = str(values['InstallDate'])
                        if len(date_str) == 8:  # YYYYMMDD format
                            install_date = datetime.strptime(date_str, '%Y%m%d')
                    except ValueError:
                        pass
                
                # Calculate size in MB
                size_mb = None
                if values.get('EstimatedSize'):
                    try:
                        size_mb = float(values['EstimatedSize']) / 1024  # KB to MB
                    except (ValueError, TypeError):
                        pass
                
                # Check if system component
                is_system = bool(values.get('SystemComponent', 0))
                
                return SoftwareInfo(
                    name=values['DisplayName'],
                    version=values.get('DisplayVersion', 'Unknown'),
                    publisher=values.get('Publisher', ''),
                    install_date=install_date,
                    install_location=values.get('InstallLocation', ''),
                    uninstall_string=values.get('UninstallString', ''),
                    size_mb=size_mb,
                    registry_key=subkey_path,
                    package_manager='registry',
                    is_system_component=is_system
                )
                
        except Exception as e:
            self.log_warning(f"Error reading registry entry {subkey_path}: {e}")
            return None
    
    def scan_package_manager_software(self, manager: str) -> Dict[str, SoftwareInfo]:
        """Scan a specific package manager for installed software."""
        software_dict = {}
        
        try:
            if manager == "chocolatey":
                software_dict = self._scan_chocolatey()
            elif manager == "winget":
                software_dict = self._scan_winget()
            elif manager == "scoop":
                software_dict = self._scan_scoop()
            elif manager == "homebrew":
                software_dict = self._scan_homebrew()
            elif manager == "apt":
                software_dict = self._scan_apt()
            # Add more package managers as needed
            
        except Exception as e:
            self.log_error(f"Error scanning {manager}: {e}")
        
        return software_dict
    
    def _scan_chocolatey(self) -> Dict[str, SoftwareInfo]:
        """Scan Chocolatey for installed packages."""
        software_dict = {}
        
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", "--limit-output"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        name, version = line.split('|', 1)
                        software_info = SoftwareInfo(
                            name=name.strip(),
                            version=version.strip(),
                            package_manager='chocolatey'
                        )
                        unique_key = f"{software_info.name}_{software_info.version}"
                        software_dict[unique_key] = software_info
                        
        except Exception as e:
            self.log_warning(f"Error scanning Chocolatey: {e}")
        
        return software_dict
    
    def _scan_winget(self) -> Dict[str, SoftwareInfo]:
        """Scan Windows Package Manager for installed packages."""
        software_dict = {}
        
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Skip header lines
                for line in lines[2:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1] if len(parts) > 1 else "Unknown"
                            
                            software_info = SoftwareInfo(
                                name=name,
                                version=version,
                                package_manager='winget'
                            )
                            unique_key = f"{software_info.name}_{software_info.version}"
                            software_dict[unique_key] = software_info
                            
        except Exception as e:
            self.log_warning(f"Error scanning Winget: {e}")
        
        return software_dict
    
    def _scan_scoop(self) -> Dict[str, SoftwareInfo]:
        """Scan Scoop for installed packages."""
        software_dict = {}
        
        try:
            result = subprocess.run(
                ["scoop", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            
                            software_info = SoftwareInfo(
                                name=name,
                                version=version,
                                package_manager='scoop'
                            )
                            unique_key = f"{software_info.name}_{software_info.version}"
                            software_dict[unique_key] = software_info
                            
        except Exception as e:
            self.log_warning(f"Error scanning Scoop: {e}")
        
        return software_dict
    
    def _scan_homebrew(self) -> Dict[str, SoftwareInfo]:
        """Scan Homebrew for installed packages."""
        software_dict = {}
        
        try:
            result = subprocess.run(
                ["brew", "list", "--versions"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            
                            software_info = SoftwareInfo(
                                name=name,
                                version=version,
                                package_manager='homebrew'
                            )
                            unique_key = f"{software_info.name}_{software_info.version}"
                            software_dict[unique_key] = software_info
                            
        except Exception as e:
            self.log_warning(f"Error scanning Homebrew: {e}")
        
        return software_dict
    
    def _scan_apt(self) -> Dict[str, SoftwareInfo]:
        """Scan APT for installed packages."""
        software_dict = {}
        
        try:
            result = subprocess.run(
                ["dpkg", "-l"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('ii'):  # Installed packages
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[1]
                            version = parts[2]
                            
                            software_info = SoftwareInfo(
                                name=name,
                                version=version,
                                package_manager='apt'
                            )
                            unique_key = f"{software_info.name}_{software_info.version}"
                            software_dict[unique_key] = software_info
                            
        except Exception as e:
            self.log_warning(f"Error scanning APT: {e}")
        
        return software_dict
    
    def filter_system_components(self, software_dict: Dict[str, SoftwareInfo], 
                               include_system: bool = False) -> Dict[str, SoftwareInfo]:
        """Filter out system components if requested."""
        if include_system:
            return software_dict
        
        filtered = {}
        for key, software in software_dict.items():
            if software.is_system_component:
                continue
            
            # Check if name contains system component keywords
            is_system = any(component.lower() in software.name.lower() 
                          for component in self.system_components)
            
            if not is_system:
                filtered[key] = software
        
        return filtered
    
    def save_software_list(self, filename: str = None) -> str:
        """Save the detected software list to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"software_list_{timestamp}.json"
        
        filepath = Path("software_maintenance/reports") / filename
        
        try:
            software_data = {
                'scan_date': datetime.now().isoformat(),
                'platform': self.platform,
                'package_managers': self.package_managers,
                'total_software': len(self.detected_software),
                'software': {key: software.to_dict() 
                           for key, software in self.detected_software.items()}
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(software_data, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"Software list saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.log_error(f"Failed to save software list: {e}")
            return ""
    
    def execute(self, include_system: bool = False, 
                save_results: bool = True) -> bool:
        """
        Execute comprehensive software detection.
        
        Args:
            include_system: Include system components in results
            save_results: Save results to JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.detected_software.clear()
            
            # Set up progress tracking
            steps = ["Registry Scan"] + [f"{pm.title()} Scan" 
                                       for pm in self.package_managers]
            if save_results:
                steps.append("Save Results")
            
            self.set_progress_steps(steps)
            
            # Scan Windows registry if on Windows
            if sys.platform == "win32":
                self.next_step("Scanning Windows Registry")
                registry_software = self.scan_registry_software()
                self.detected_software.update(registry_software)
            else:
                self.next_step("Registry Scan (Skipped - Not Windows)")
            
            # Scan each package manager
            for manager in self.package_managers:
                self.next_step(f"Scanning {manager.title()}")
                pm_software = self.scan_package_manager_software(manager)
                self.detected_software.update(pm_software)
            
            # Filter system components if requested
            if not include_system:
                self.detected_software = self.filter_system_components(
                    self.detected_software, include_system)
            
            # Save results if requested
            if save_results:
                self.next_step("Saving Results")
                self.save_software_list()
            
            self.log_info(f"Software detection completed. Found {len(self.detected_software)} applications")
            return True
            
        except Exception as e:
            self.log_error(f"Software detection failed: {e}")
            return False
    
    def get_software_by_name(self, name: str) -> List[SoftwareInfo]:
        """Get all software entries matching a name (case-insensitive)."""
        matches = []
        name_lower = name.lower()
        
        for software in self.detected_software.values():
            if name_lower in software.name.lower():
                matches.append(software)
        
        return matches
    
    def get_software_by_publisher(self, publisher: str) -> List[SoftwareInfo]:
        """Get all software entries from a specific publisher."""
        matches = []
        publisher_lower = publisher.lower()
        
        for software in self.detected_software.values():
            if publisher_lower in software.publisher.lower():
                matches.append(software)
        
        return matches
    
    def get_software_statistics(self) -> Dict[str, any]:
        """Get statistics about detected software."""
        total_size = sum(s.size_mb for s in self.detected_software.values() 
                        if s.size_mb)
        
        package_manager_counts = {}
        for software in self.detected_software.values():
            pm = software.package_manager
            package_manager_counts[pm] = package_manager_counts.get(pm, 0) + 1
        
        return {
            'total_applications': len(self.detected_software),
            'total_size_mb': total_size,
            'total_size_gb': total_size / 1024 if total_size else 0,
            'package_manager_breakdown': package_manager_counts,
            'system_components': sum(1 for s in self.detected_software.values() 
                                   if s.is_system_component)
        }