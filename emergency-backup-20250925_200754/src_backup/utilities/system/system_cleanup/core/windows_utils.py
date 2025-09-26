"""
Windows-specific utilities for system cleanup operations.

Provides Windows-specific functionality for system operations, registry access,
service management, and system information retrieval.
"""

import os
import sys
import subprocess
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import winreg
import tempfile
import shutil


class WindowsUtils:
    """Utility class for Windows-specific operations."""
    
    # Windows version constants
    WINDOWS_7 = "7"
    WINDOWS_8 = "8"
    WINDOWS_10 = "10"
    WINDOWS_11 = "11"
    
    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        return sys.platform.startswith('win')
    
    @classmethod
    def get_windows_version(cls) -> str:
        """Get Windows version."""
        try:
            import platform
            version = platform.version()
            if version.startswith('10.0.22'):
                return cls.WINDOWS_11
            elif version.startswith('10.0'):
                return cls.WINDOWS_10
            elif version.startswith('6.3'):
                return cls.WINDOWS_8
            elif version.startswith('6.1'):
                return cls.WINDOWS_7
            else:
                return "Unknown"
        except Exception:
            return "Unknown"
    
    @classmethod
    def is_admin(cls) -> bool:
        """Check if running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    @classmethod
    def request_admin_privileges(cls) -> bool:
        """Request administrator privileges."""
        try:
            if cls.is_admin():
                return True
            else:
                # Re-run the program with admin rights
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return False
        except Exception:
            return False
    
    @classmethod
    def get_system_drive(cls) -> str:
        """Get the system drive (usually C:)."""
        return os.environ.get('SYSTEMDRIVE', 'C:')
    
    @classmethod
    def get_windows_directory(cls) -> Path:
        """Get the Windows directory."""
        return Path(os.environ.get('WINDIR', 'C:\\Windows'))
    
    @classmethod
    def get_program_files_directories(cls) -> List[Path]:
        """Get Program Files directories."""
        dirs = []
        
        # Program Files
        pf = os.environ.get('PROGRAMFILES')
        if pf:
            dirs.append(Path(pf))
        
        # Program Files (x86)
        pf_x86 = os.environ.get('PROGRAMFILES(X86)')
        if pf_x86:
            dirs.append(Path(pf_x86))
        
        return dirs
    
    @classmethod
    def get_user_profile_directories(cls) -> List[Path]:
        """Get all user profile directories."""
        try:
            users_dir = Path(cls.get_system_drive()) / "Users"
            if users_dir.exists():
                return [d for d in users_dir.iterdir() 
                       if d.is_dir() and not d.name.startswith('.')]
        except Exception:
            pass
        return []
    
    @classmethod
    def get_temp_directories(cls) -> List[Path]:
        """Get all temporary directories."""
        temp_dirs = []
        
        # System temp
        system_temp = os.environ.get('TEMP')
        if system_temp:
            temp_dirs.append(Path(system_temp))
        
        # Windows temp
        windows_temp = cls.get_windows_directory() / "Temp"
        if windows_temp.exists():
            temp_dirs.append(windows_temp)
        
        # User temp directories
        for user_dir in cls.get_user_profile_directories():
            user_temp = user_dir / "AppData" / "Local" / "Temp"
            if user_temp.exists():
                temp_dirs.append(user_temp)
        
        return temp_dirs
    
    @classmethod
    def get_cache_directories(cls) -> List[Path]:
        """Get common cache directories."""
        cache_dirs = []
        
        for user_dir in cls.get_user_profile_directories():
            # Local cache
            local_cache = user_dir / "AppData" / "Local"
            if local_cache.exists():
                cache_dirs.append(local_cache)
            
            # Roaming cache
            roaming_cache = user_dir / "AppData" / "Roaming"
            if roaming_cache.exists():
                cache_dirs.append(roaming_cache)
        
        return cache_dirs
    
    @classmethod
    def run_command(cls, command: str, admin_required: bool = False) -> Tuple[bool, str]:
        """Run a Windows command."""
        try:
            if admin_required and not cls.is_admin():
                return False, "Administrator privileges required"
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0, result.stdout + result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    @classmethod
    def clear_dns_cache(cls) -> bool:
        """Clear DNS cache."""
        success, _ = cls.run_command("ipconfig /flushdns", admin_required=True)
        return success
    
    @classmethod
    def clear_icon_cache(cls) -> bool:
        """Clear icon cache."""
        try:
            # Kill explorer to release icon cache
            cls.run_command("taskkill /f /im explorer.exe")
            
            # Delete icon cache files
            for user_dir in cls.get_user_profile_directories():
                icon_cache_dir = user_dir / "AppData" / "Local" / "IconCache.db"
                if icon_cache_dir.exists():
                    try:
                        icon_cache_dir.unlink()
                    except Exception:
                        pass
            
            # Restart explorer
            cls.run_command("start explorer.exe")
            return True
            
        except Exception:
            return False
    
    @classmethod
    def clear_font_cache(cls) -> bool:
        """Clear font cache."""
        try:
            font_cache_service = "FontCache"
            
            # Stop font cache service
            cls.run_command(f"net stop {font_cache_service}", admin_required=True)
            
            # Delete font cache files
            font_cache_dir = cls.get_windows_directory() / "ServiceProfiles" / "LocalService" / "AppData" / "Local" / "FontCache"
            if font_cache_dir.exists():
                try:
                    shutil.rmtree(font_cache_dir)
                except Exception:
                    pass
            
            # Start font cache service
            cls.run_command(f"net start {font_cache_service}", admin_required=True)
            return True
            
        except Exception:
            return False
    
    @classmethod
    def get_disk_usage(cls, path: Path) -> Tuple[int, int, int]:
        """Get disk usage for a path (total, used, free)."""
        try:
            if path.exists():
                total, used, free = shutil.disk_usage(path)
                return total, used, free
        except Exception:
            pass
        return 0, 0, 0
    
    @classmethod
    def get_file_size(cls, path: Path) -> int:
        """Get file size in bytes."""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        except Exception:
            pass
        return 0
    
    @classmethod
    def is_file_in_use(cls, file_path: Path) -> bool:
        """Check if a file is currently in use."""
        try:
            with open(file_path, 'r+b'):
                return False
        except (IOError, OSError):
            return True
    
    @classmethod
    def safe_delete_file(cls, file_path: Path, secure: bool = False) -> bool:
        """Safely delete a file."""
        try:
            if not file_path.exists():
                return True
            
            # Check if file is in use
            if cls.is_file_in_use(file_path):
                return False
            
            if secure:
                # Secure deletion with overwriting
                file_size = file_path.stat().st_size
                with open(file_path, 'r+b') as f:
                    # Overwrite with random data
                    for _ in range(3):
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
            
            file_path.unlink()
            return True
            
        except Exception:
            return False
    
    @classmethod
    def safe_delete_directory(cls, dir_path: Path, secure: bool = False) -> bool:
        """Safely delete a directory and its contents."""
        try:
            if not dir_path.exists():
                return True
            
            # Delete all files first
            for item in dir_path.rglob('*'):
                if item.is_file():
                    if not cls.safe_delete_file(item, secure):
                        return False
            
            # Remove empty directories
            for item in sorted(dir_path.rglob('*'), reverse=True):
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()
            
            # Remove the main directory
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def create_system_restore_point(cls, description: str) -> bool:
        """Create a system restore point."""
        try:
            command = f'powershell.exe -Command "Checkpoint-Computer -Description \\"{description}\\" -RestorePointType \\"MODIFY_SETTINGS\\""'
            success, _ = cls.run_command(command, admin_required=True)
            return success
        except Exception:
            return False
    
    @classmethod
    def get_running_processes(cls) -> List[str]:
        """Get list of running processes."""
        try:
            result = subprocess.run(
                ['tasklist', '/fo', 'csv'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                return [line.split(',')[0].strip('"') for line in lines]
        except Exception:
            pass
        return []
    
    @classmethod
    def is_process_running(cls, process_name: str) -> bool:
        """Check if a specific process is running."""
        running_processes = cls.get_running_processes()
        return any(process_name.lower() in proc.lower() 
                  for proc in running_processes)
    
    @classmethod
    def kill_process(cls, process_name: str) -> bool:
        """Kill a process by name."""
        try:
            result = subprocess.run(
                ['taskkill', '/f', '/im', process_name],
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @classmethod
    def get_installed_programs(cls) -> List[Dict[str, str]]:
        """Get list of installed programs from registry."""
        programs = []
        
        try:
            # Check both 32-bit and 64-bit program entries
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        version = ""
                                        install_location = ""
                                        
                                        try:
                                            version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        except FileNotFoundError:
                                            pass
                                        
                                        try:
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        except FileNotFoundError:
                                            pass
                                        
                                        programs.append({
                                            "name": name,
                                            "version": version,
                                            "install_location": install_location,
                                            "registry_key": subkey_name
                                        })
                                        
                                    except FileNotFoundError:
                                        # No DisplayName, skip this entry
                                        pass
                            except Exception:
                                continue
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return programs
    
    @classmethod
    def get_system_info(cls) -> Dict[str, str]:
        """Get basic system information."""
        info = {}
        
        try:
            info["windows_version"] = cls.get_windows_version()
            info["is_admin"] = str(cls.is_admin())
            info["system_drive"] = cls.get_system_drive()
            info["windows_directory"] = str(cls.get_windows_directory())
            
            # Get total/free disk space
            total, used, free = cls.get_disk_usage(Path(cls.get_system_drive()))
            info["disk_total"] = str(total)
            info["disk_used"] = str(used)
            info["disk_free"] = str(free)
            
        except Exception:
            pass
        
        return info