"""
System location mappings for Windows cleanup operations.

This module contains the paths and patterns for locating system files,
cache directories, log files, and other cleanup targets across Windows.
"""

from pathlib import Path
from typing import Dict, List

from .windows_utils import WindowsUtils


class SystemLocations:
    """Centralized system location mappings for cleanup operations."""

    @classmethod
    def get_temp_directories(cls) -> List[Path]:
        """Get all temporary file directories."""
        return WindowsUtils.get_temp_directories()

    @classmethod
    def get_cache_directories(cls) -> List[Path]:
        """Get all cache directories."""
        return WindowsUtils.get_cache_directories()

    @classmethod
    def get_log_directories(cls) -> List[Path]:
        """Get Windows log file directories."""
        log_dirs = []

        windows_dir = WindowsUtils.get_windows_directory()
        system_drive = WindowsUtils.get_system_drive()

        # Windows Event Logs
        log_dirs.append(windows_dir / "System32" / "winevt" / "Logs")

        # Windows Setup Logs
        log_dirs.append(windows_dir / "Panther")
        log_dirs.append(windows_dir / "inf")

        # Windows Update Logs
        log_dirs.append(windows_dir / "SoftwareDistribution" / "DataStore" / "Logs")
        log_dirs.append(windows_dir / "WindowsUpdate.log")

        # System Logs
        log_dirs.append(Path(system_drive) / "Windows" / "Logs")

        # User-specific logs
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_logs = user_dir / "AppData" / "Local" / "Microsoft" / "Windows"
            if user_logs.exists():
                log_dirs.append(user_logs)

        return [d for d in log_dirs if d.exists()]

    @classmethod
    def get_windows_cache_directories(cls) -> List[Path]:
        """Get Windows system cache directories."""
        cache_dirs = []

        windows_dir = WindowsUtils.get_windows_directory()

        # Prefetch files
        prefetch_dir = windows_dir / "Prefetch"
        if prefetch_dir.exists():
            cache_dirs.append(prefetch_dir)

        # DNS Cache (handled by service, not files)

        # Icon Cache
        for user_dir in WindowsUtils.get_user_profile_directories():
            icon_cache = user_dir / "AppData" / "Local" / "IconCache.db"
            if icon_cache.exists():
                cache_dirs.append(icon_cache.parent)

        # Font Cache
        font_cache = (
            windows_dir
            / "ServiceProfiles"
            / "LocalService"
            / "AppData"
            / "Local"
            / "FontCache"
        )
        if font_cache.exists():
            cache_dirs.append(font_cache)

        # Thumbnail Cache
        for user_dir in WindowsUtils.get_user_profile_directories():
            thumb_cache = (
                user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer"
            )
            if thumb_cache.exists():
                cache_dirs.append(thumb_cache)

        # Windows Update Cache
        wu_cache = windows_dir / "SoftwareDistribution" / "Download"
        if wu_cache.exists():
            cache_dirs.append(wu_cache)

        return cache_dirs

    @classmethod
    def get_program_cache_directories(cls) -> List[Path]:
        """Get program-specific cache directories."""
        cache_dirs = []

        for user_dir in WindowsUtils.get_user_profile_directories():
            # Common application cache locations
            app_cache_bases = [
                user_dir / "AppData" / "Local",
                user_dir / "AppData" / "Roaming",
            ]

            for cache_base in app_cache_bases:
                if cache_base.exists():
                    # Look for common cache folder patterns
                    for item in cache_base.iterdir():
                        if item.is_dir():
                            # Check for cache subdirectories
                            cache_subdirs = [
                                item / "Cache",
                                item / "cache",
                                item / "Caches",
                                item / "CachedData",
                                item / "Temp",
                                item / "temp",
                            ]

                            for cache_subdir in cache_subdirs:
                                if cache_subdir.exists():
                                    cache_dirs.append(cache_subdir)

        return cache_dirs

    @classmethod
    def get_backup_directories(cls) -> List[Path]:
        """Get common backup file directories."""
        system_drive = WindowsUtils.get_system_drive()

        # System backup locations
        backup_locations = [
            Path(system_drive) / "Windows.old",
            Path(system_drive) / "Windows" / "System32" / "config" / "RegBack",
            Path(system_drive) / "System Volume Information",
        ]

        # User backup locations
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_backups = [
                user_dir
                / "AppData"
                / "Local"
                / "Microsoft"
                / "Windows"
                / "FileHistory",
                user_dir / "Documents" / "Backup",
                user_dir / "Desktop" / "Backup",
            ]
            backup_locations.extend(user_backups)

        return [d for d in backup_locations if d.exists()]

    @classmethod
    def get_download_directories(cls) -> List[Path]:
        """Get program download directories."""
        download_dirs = []

        windows_dir = WindowsUtils.get_windows_directory()

        # Windows Update downloads
        wu_download = windows_dir / "SoftwareDistribution" / "Download"
        if wu_download.exists():
            download_dirs.append(wu_download)

        # Driver downloads
        driver_store = windows_dir / "System32" / "DriverStore" / "FileRepository"
        if driver_store.exists():
            download_dirs.append(driver_store)

        # Installer cache
        installer_cache = windows_dir / "Installer"
        if installer_cache.exists():
            download_dirs.append(installer_cache)

        # User download folders
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_downloads = user_dir / "Downloads"
            if user_downloads.exists():
                download_dirs.append(user_downloads)

        return download_dirs

    @classmethod
    def get_memory_dump_directories(cls) -> List[Path]:
        """Get memory dump and crash dump directories."""
        system_drive = WindowsUtils.get_system_drive()
        windows_dir = WindowsUtils.get_windows_directory()

        # System memory dumps
        dump_locations = [
            Path(system_drive) / "Windows" / "MEMORY.DMP",
            Path(system_drive) / "Windows" / "Minidump",
            windows_dir / "LiveKernelReports",
            windows_dir / "System32" / "LogFiles" / "WMI",
        ]

        # User crash dumps
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_dumps = [
                user_dir / "AppData" / "Local" / "CrashDumps",
                user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "WER",
            ]
            dump_locations.extend(user_dumps)

        return [d for d in dump_locations if d.exists()]

    @classmethod
    def get_history_directories(cls) -> List[Path]:
        """Get Windows history and recent item directories."""
        history_dirs = []

        for user_dir in WindowsUtils.get_user_profile_directories():
            history_locations = [
                # Recent documents
                user_dir / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent",
                # Jump lists
                user_dir
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Recent"
                / "AutomaticDestinations",
                user_dir
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Recent"
                / "CustomDestinations",
                # Run dialog history (in registry)
                # Search history
                user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "History",
                # File Explorer history
                user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer",
            ]

            history_dirs.extend([d for d in history_locations if d.exists()])

        return history_dirs

    @classmethod
    def get_shortcut_directories(cls) -> List[Path]:
        """Get Start Menu and shortcut directories."""
        shortcut_dirs = []

        system_drive = WindowsUtils.get_system_drive()

        # System-wide Start Menu
        system_start_menu = (
            Path(system_drive) / "ProgramData" / "Microsoft" / "Windows" / "Start Menu"
        )
        if system_start_menu.exists():
            shortcut_dirs.append(system_start_menu)

        # User-specific Start Menus
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_start_menu = (
                user_dir
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Start Menu"
            )
            if user_start_menu.exists():
                shortcut_dirs.append(user_start_menu)

            # Desktop shortcuts
            desktop = user_dir / "Desktop"
            if desktop.exists():
                shortcut_dirs.append(desktop)

            # Quick Launch
            quick_launch = (
                user_dir
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Internet Explorer"
                / "Quick Launch"
            )
            if quick_launch.exists():
                shortcut_dirs.append(quick_launch)

        return shortcut_dirs

    @classmethod
    def get_registry_cleanup_keys(cls) -> Dict[str, List[str]]:
        """Get registry keys commonly needing cleanup."""
        return {
            "uninstall_entries": [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",  # noqa: E501
            ],
            "startup_entries": [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce",  # noqa: E501
            ],
            "file_associations": [
                r"SOFTWARE\Classes",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts",
            ],
            "shared_dlls": [r"SOFTWARE\Microsoft\Windows\CurrentVersion\SharedDLLs"],
            "mru_lists": [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",  # noqa: E501
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",  # noqa: E501
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
            ],
        }

    @classmethod
    def get_restore_point_locations(cls) -> List[Path]:
        """Get system restore point locations."""
        system_drive = WindowsUtils.get_system_drive()

        restore_locations = [Path(system_drive) / "System Volume Information"]

        return [d for d in restore_locations if d.exists()]

    @classmethod
    def get_common_file_patterns(cls) -> Dict[str, List[str]]:
        """Get common file patterns for cleanup operations."""
        return {
            "temp_files": [
                "*.tmp",
                "*.temp",
                "*.bak",
                "*.old",
                "*.log",
                "*.dmp",
                "*.chk",
                "*.gid",
                "*.ftg",
                "*.fts",
            ],
            "cache_files": [
                "*.cache",
                "thumbs.db",
                "desktop.ini",
                "*.db-wal",
                "*.db-shm",
                "iconcache*.db",
            ],
            "backup_files": ["*.backup", "*.bak", "*.old", "*.orig", "*.save"],
            "log_files": ["*.log", "*.etl", "*.evtx", "*.evt"],
        }
