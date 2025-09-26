"""
Platform-specific utilities for privacy tools.

Provides cross-platform functionality for detecting OS, handling paths,
and managing platform-specific operations.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess
import shutil


class PlatformUtils:
    """Utility class for cross-platform operations."""
    
    # Platform constants
    WINDOWS = "windows"
    MACOS = "darwin"
    LINUX = "linux"
    
    @classmethod
    def get_platform(cls) -> str:
        """Get the current platform name."""
        return platform.system().lower()
    
    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        return cls.get_platform() == cls.WINDOWS
    
    @classmethod
    def is_macos(cls) -> bool:
        """Check if running on macOS."""
        return cls.get_platform() == cls.MACOS
    
    @classmethod
    def is_linux(cls) -> bool:
        """Check if running on Linux."""
        return cls.get_platform() == cls.LINUX
    
    @classmethod
    def get_home_directory(cls) -> Path:
        """Get the user's home directory."""
        return Path.home()
    
    @classmethod
    def get_appdata_directory(cls) -> Optional[Path]:
        """Get the application data directory for the current platform."""
        if cls.is_windows():
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata)
        elif cls.is_macos():
            return cls.get_home_directory() / "Library" / "Application Support"
        elif cls.is_linux():
            return cls.get_home_directory() / ".config"
        return None
    
    @classmethod
    def get_local_appdata_directory(cls) -> Optional[Path]:
        """Get the local application data directory (Windows only)."""
        if cls.is_windows():
            local_appdata = os.environ.get('LOCALAPPDATA')
            if local_appdata:
                return Path(local_appdata)
        return cls.get_appdata_directory()
    
    @classmethod
    def get_temp_directory(cls) -> Path:
        """Get the system temporary directory."""
        return Path.cwd() / "temp" if not hasattr(Path, 'temp') else Path.temp()
    
    @classmethod
    def get_trash_directory(cls) -> Optional[Path]:
        """Get the system trash/recycle bin directory."""
        if cls.is_windows():
            # Windows Recycle Bin is complex, use shell operations
            return None
        elif cls.is_macos():
            return cls.get_home_directory() / ".Trash"
        elif cls.is_linux():
            # XDG Trash specification
            trash_dir = cls.get_home_directory() / ".local" / "share" / "Trash"
            if trash_dir.exists():
                return trash_dir
            # Fallback to common locations
            for path in ["/tmp/.Trash-1000", "/tmp/.Trash"]:
                if Path(path).exists():
                    return Path(path)
        return None
    
    @classmethod
    def expand_environment_variables(cls, path: str) -> str:
        """Expand environment variables in a path string."""
        return os.path.expandvars(os.path.expanduser(path))
    
    @classmethod
    def safe_path_join(cls, *parts) -> Path:
        """Safely join path components."""
        return Path(*parts)
    
    @classmethod
    def is_admin(cls) -> bool:
        """Check if running with administrator/root privileges."""
        try:
            if cls.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    @classmethod
    def request_admin_privileges(cls) -> bool:
        """Request administrator privileges (Windows only)."""
        if not cls.is_windows():
            return False
        
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
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
    def secure_delete_file(cls, file_path: Path, passes: int = 3) -> bool:
        """Securely delete a file by overwriting it multiple times."""
        try:
            if not file_path.exists():
                return True
            
            file_size = file_path.stat().st_size
            
            # Overwrite with random data
            with open(file_path, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    # Write random data
                    remaining = file_size
                    while remaining > 0:
                        chunk_size = min(8192, remaining)
                        f.write(os.urandom(chunk_size))
                        remaining -= chunk_size
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove the file
            file_path.unlink()
            return True
            
        except Exception:
            return False
    
    @classmethod
    def empty_trash(cls) -> bool:
        """Empty the system trash/recycle bin."""
        try:
            if cls.is_windows():
                # Use Windows API to empty recycle bin
                import ctypes
                from ctypes import wintypes
                
                SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
                SHEmptyRecycleBin.argtypes = [
                    wintypes.HWND, wintypes.LPCWSTR, wintypes.DWORD
                ]
                SHEmptyRecycleBin.restype = wintypes.HRESULT
                
                # SHERB_NOCONFIRMATION = 0x00000001
                # SHERB_NOPROGRESSUI = 0x00000002
                result = SHEmptyRecycleBin(None, None, 0x00000001 | 0x00000002)
                return result == 0
                
            elif cls.is_macos():
                # Empty macOS Trash
                trash_dir = cls.get_trash_directory()
                if trash_dir and trash_dir.exists():
                    for item in trash_dir.iterdir():
                        if item.is_file():
                            cls.secure_delete_file(item)
                        elif item.is_dir():
                            shutil.rmtree(item)
                    return True
                    
            elif cls.is_linux():
                # Empty Linux trash
                trash_dir = cls.get_trash_directory()
                if trash_dir and trash_dir.exists():
                    files_dir = trash_dir / "files"
                    info_dir = trash_dir / "info"
                    
                    # Clear files
                    if files_dir.exists():
                        for item in files_dir.iterdir():
                            if item.is_file():
                                cls.secure_delete_file(item)
                            elif item.is_dir():
                                shutil.rmtree(item)
                    
                    # Clear info files
                    if info_dir.exists():
                        for item in info_dir.iterdir():
                            if item.is_file():
                                item.unlink()
                    
                    return True
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def get_running_processes(cls) -> List[str]:
        """Get list of currently running process names."""
        try:
            if cls.is_windows():
                result = subprocess.run(
                    ['tasklist', '/fo', 'csv'], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    return [line.split(',')[0].strip('"') for line in lines]
            else:
                result = subprocess.run(
                    ['ps', '-eo', 'comm'], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[1:]  # Skip header
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
        """Attempt to kill a process by name."""
        try:
            if cls.is_windows():
                result = subprocess.run(
                    ['taskkill', '/f', '/im', process_name], 
                    capture_output=True
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    ['pkill', '-f', process_name], 
                    capture_output=True
                )
                return result.returncode == 0
        except Exception:
            return False