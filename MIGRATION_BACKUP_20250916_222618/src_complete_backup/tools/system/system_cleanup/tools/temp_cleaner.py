"""
Temporary Files Cleaner Tool

This tool removes temporary files from various system locations to free disk space
and improve system performance. It safely handles files in use and provides
comprehensive filtering options.
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.cleanup_base import CleanupToolBase, CleanupOperationResult
from ..core.system_locations import SystemLocations
from ..core.windows_utils import WindowsUtils


class TempFilesCleaner(CleanupToolBase):
    """Tool for cleaning temporary files from system locations."""
    
    def __init__(self):
        super().__init__("Delete Temp Files")
    
    def get_description(self) -> str:
        """Get description of this tool."""
        return ("Removes temporary files from Windows temp directories, "
                "user temp folders, and application temp locations to "
                "free disk space and improve performance.")
    
    def requires_admin(self) -> bool:
        """Check if this tool requires administrator privileges."""
        return False  # Can clean user temp files without admin
    
    def is_supported(self) -> bool:
        """Check if this tool is supported on current system."""
        return WindowsUtils.is_windows()
    
    def estimate_cleanup_size(self, **kwargs) -> int:
        """Estimate the amount of space that can be freed."""
        max_age_days = kwargs.get('max_age_days', 0)
        min_size_bytes = kwargs.get('min_size_bytes', 0)
        file_extensions = kwargs.get('file_extensions', [])
        include_system_temp = kwargs.get('include_system_temp', True)
        
        total_size = 0
        temp_dirs = self._get_temp_directories(include_system_temp)
        
        for temp_dir in temp_dirs:
            try:
                files = self._scan_temp_files(temp_dir)
                files = self._apply_filters(files, max_age_days, min_size_bytes, file_extensions)
                
                for file_path in files:
                    try:
                        total_size += file_path.stat().st_size
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return total_size
    
    def preview_operation(self, **kwargs) -> Dict[str, Any]:
        """Preview what the operation will do."""
        max_age_days = kwargs.get('max_age_days', 0)
        min_size_bytes = kwargs.get('min_size_bytes', 0)
        file_extensions = kwargs.get('file_extensions', [])
        include_system_temp = kwargs.get('include_system_temp', True)
        
        preview = {
            "max_age_days": max_age_days,
            "min_size_bytes": min_size_bytes,
            "file_extensions": file_extensions,
            "include_system_temp": include_system_temp,
            "temp_directories": [],
            "estimated_files": 0,
            "estimated_size": 0,
            "warnings": []
        }
        
        temp_dirs = self._get_temp_directories(include_system_temp)
        
        for temp_dir in temp_dirs:
            try:
                files = self._scan_temp_files(temp_dir)
                files = self._apply_filters(files, max_age_days, min_size_bytes, file_extensions)
                
                dir_size = sum(f.stat().st_size for f in files if f.exists())
                
                preview["temp_directories"].append({
                    "path": str(temp_dir),
                    "file_count": len(files),
                    "size": dir_size,
                    "accessible": temp_dir.exists()
                })
                
                preview["estimated_files"] += len(files)
                preview["estimated_size"] += dir_size
                
            except Exception as e:
                preview["warnings"].append(f"Error scanning {temp_dir}: {str(e)}")
        
        # Add warnings for system temp if not admin
        if include_system_temp and not WindowsUtils.is_admin():
            preview["warnings"].append(
                "Some system temp files may require administrator privileges"
            )
        
        return preview
    
    def execute_operation(self, **kwargs) -> CleanupOperationResult:
        """Execute the temp files cleanup operation."""
        max_age_days = kwargs.get('max_age_days', 0)
        min_size_bytes = kwargs.get('min_size_bytes', 0)
        file_extensions = kwargs.get('file_extensions', [])
        include_system_temp = kwargs.get('include_system_temp', True)
        create_backup = kwargs.get('create_backup', False)
        secure_delete = kwargs.get('secure_delete', False)
        
        self._emit_status("Starting temporary files cleanup...")
        
        temp_dirs = self._get_temp_directories(include_system_temp)
        total_deleted = 0
        total_space_freed = 0
        errors = []
        
        try:
            for i, temp_dir in enumerate(temp_dirs):
                if self._check_should_stop():
                    break
                
                self._emit_progress(
                    i, len(temp_dirs),
                    f"Cleaning {temp_dir.name}..."
                )
                
                try:
                    deleted, space_freed = self._clean_temp_directory(
                        temp_dir, max_age_days, min_size_bytes, 
                        file_extensions, create_backup, secure_delete
                    )
                    
                    total_deleted += deleted
                    total_space_freed += space_freed
                    
                    self._emit_status(
                        f"Cleaned {deleted} files from {temp_dir.name} "
                        f"({self._format_size(space_freed)} freed)"
                    )
                    
                except Exception as e:
                    error_msg = f"Failed to clean {temp_dir}: {str(e)}"
                    errors.append(error_msg)
                    self._emit_error(error_msg)
            
            self._emit_progress(
                len(temp_dirs), len(temp_dirs),
                "Temporary files cleanup complete"
            )
            
            success = len(errors) == 0
            message = (f"Deleted {total_deleted} temporary files, "
                      f"freed {self._format_size(total_space_freed)}")
            
            return CleanupOperationResult(
                success, message, total_deleted, total_space_freed, errors
            )
            
        except Exception as e:
            return CleanupOperationResult(
                False,
                f"Temp files cleanup failed: {str(e)}",
                total_deleted,
                total_space_freed,
                [str(e)]
            )
    
    def _get_temp_directories(self, include_system_temp: bool) -> List[Path]:
        """Get list of temp directories to clean."""
        temp_dirs = []
        
        # Always include user temp directories
        user_temp_dirs = []
        for user_dir in WindowsUtils.get_user_profile_directories():
            user_temp = user_dir / "AppData" / "Local" / "Temp"
            if user_temp.exists():
                user_temp_dirs.append(user_temp)
        
        temp_dirs.extend(user_temp_dirs)
        
        # Include system temp if requested and accessible
        if include_system_temp:
            system_temp_dirs = SystemLocations.get_temp_directories()
            for temp_dir in system_temp_dirs:
                if temp_dir not in user_temp_dirs:  # Avoid duplicates
                    temp_dirs.append(temp_dir)
        
        return temp_dirs
    
    def _scan_temp_files(self, temp_dir: Path) -> List[Path]:
        """Scan a temp directory for files."""
        files = []
        
        try:
            # Get common temp file patterns
            patterns = SystemLocations.get_common_file_patterns()["temp_files"]
            
            for pattern in patterns:
                files.extend(self._scan_directory(temp_dir, True, pattern))
            
            # Also scan for any files older than 1 day
            all_files = self._scan_directory(temp_dir, True, "*")
            for file_path in all_files:
                if file_path not in files and self._get_file_age_days(file_path) >= 1:
                    files.append(file_path)
            
        except Exception:
            pass
        
        return files
    
    def _apply_filters(self, files: List[Path], max_age_days: int,
                      min_size_bytes: int, file_extensions: List[str]) -> List[Path]:
        """Apply filtering criteria to file list."""
        filtered_files = files
        
        # Filter by age
        if max_age_days > 0:
            filtered_files = self._filter_files_by_age(filtered_files, max_age_days)
        
        # Filter by size
        if min_size_bytes > 0:
            filtered_files = self._filter_files_by_size(filtered_files, min_size_bytes)
        
        # Filter by extension
        if file_extensions:
            filtered_files = self._filter_files_by_extension(filtered_files, file_extensions)
        
        return filtered_files
    
    def _clean_temp_directory(self, temp_dir: Path, max_age_days: int,
                             min_size_bytes: int, file_extensions: List[str],
                             create_backup: bool, secure_delete: bool) -> tuple:
        """Clean a specific temp directory."""
        deleted_count = 0
        space_freed = 0
        
        try:
            files = self._scan_temp_files(temp_dir)
            files = self._apply_filters(files, max_age_days, min_size_bytes, file_extensions)
            
            for file_path in files:
                if self._check_should_stop():
                    break
                
                try:
                    # Skip files that are in use
                    if WindowsUtils.is_file_in_use(file_path):
                        continue
                    
                    # Get file size before deletion
                    file_size = file_path.stat().st_size
                    
                    # Create backup if requested
                    if create_backup:
                        self._backup_file(file_path)
                    
                    # Delete the file
                    if self._safe_delete_file(file_path, secure_delete):
                        deleted_count += 1
                        space_freed += file_size
                    
                except Exception:
                    # Skip files that can't be deleted
                    continue
            
            # Clean empty directories
            self._clean_empty_directories(temp_dir)
            
        except Exception:
            pass
        
        return deleted_count, space_freed
    
    def _clean_empty_directories(self, base_dir: Path) -> None:
        """Remove empty directories within the temp directory."""
        try:
            # Get all subdirectories, sorted by depth (deepest first)
            subdirs = [d for d in base_dir.rglob('*') if d.is_dir()]
            subdirs.sort(key=lambda x: len(x.parts), reverse=True)
            
            for subdir in subdirs:
                try:
                    # Only remove if empty and not the base directory
                    if subdir != base_dir and not any(subdir.iterdir()):
                        subdir.rmdir()
                except Exception:
                    continue
                    
        except Exception:
            pass
    
    def _validate_operation_parameters(self, **kwargs) -> bool:
        """Validate operation parameters."""
        max_age_days = kwargs.get('max_age_days', 0)
        min_size_bytes = kwargs.get('min_size_bytes', 0)
        
        if max_age_days < 0:
            self._emit_error("Maximum age days must be non-negative")
            return False
        
        if min_size_bytes < 0:
            self._emit_error("Minimum size bytes must be non-negative")
            return False
        
        return True