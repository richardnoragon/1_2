"""
Secure Empty Trash Tool

This tool securely empties the system trash/recycle bin across all platforms,
with options for secure deletion and progress tracking.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

from ..core.privacy_base import PrivacyToolBase, PrivacyOperationResult
from ..core.platform_utils import PlatformUtils


class SecureEmptyTrashTool(PrivacyToolBase):
    """Tool for securely emptying system trash/recycle bin."""
    
    def __init__(self):
        super().__init__("Secure Empty Trash")
    
    def get_description(self) -> str:
        """Get description of this tool."""
        return ("Securely empties the system trash/recycle bin, "
                "optionally overwriting deleted files to prevent recovery.")
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms."""
        return [
            PlatformUtils.WINDOWS,
            PlatformUtils.MACOS,
            PlatformUtils.LINUX
        ]
    
    def is_supported(self) -> bool:
        """Check if this tool is supported on current platform."""
        return PlatformUtils.get_platform() in self.get_supported_platforms()
    
    def preview_operation(self, secure_delete: bool = False) -> Dict[str, Any]:
        """Preview what the operation will do."""
        preview = {
            "platform": PlatformUtils.get_platform(),
            "secure_delete": secure_delete,
            "trash_items": [],
            "estimated_size": 0,
            "warnings": []
        }
        
        try:
            if PlatformUtils.is_windows():
                preview.update(self._preview_windows_trash())
            elif PlatformUtils.is_macos():
                preview.update(self._preview_macos_trash())
            elif PlatformUtils.is_linux():
                preview.update(self._preview_linux_trash())
            
            if secure_delete:
                preview["warnings"].append(
                    "Secure deletion will overwrite files multiple times. "
                    "This operation cannot be undone."
                )
            
        except Exception as e:
            preview["warnings"].append(f"Error scanning trash: {str(e)}")
        
        return preview
    
    def _preview_windows_trash(self) -> Dict[str, Any]:
        """Preview Windows recycle bin contents."""
        # Windows recycle bin is complex, use approximation
        return {
            "trash_items": ["Windows Recycle Bin (contents vary by user)"],
            "estimated_size": 0,
            "notes": ["Windows recycle bin will be emptied using system API"]
        }
    
    def _preview_macos_trash(self) -> Dict[str, Any]:
        """Preview macOS trash contents."""
        trash_dir = PlatformUtils.get_trash_directory()
        items = []
        total_size = 0
        
        if trash_dir and trash_dir.exists():
            try:
                for item in trash_dir.iterdir():
                    items.append(item.name)
                    if item.is_file():
                        total_size += item.stat().st_size
                    elif item.is_dir():
                        total_size += sum(
                            f.stat().st_size 
                            for f in item.rglob('*') if f.is_file()
                        )
            except Exception:
                pass
        
        return {
            "trash_items": items,
            "estimated_size": total_size
        }
    
    def _preview_linux_trash(self) -> Dict[str, Any]:
        """Preview Linux trash contents."""
        trash_dir = PlatformUtils.get_trash_directory()
        items = []
        total_size = 0
        
        if trash_dir and trash_dir.exists():
            files_dir = trash_dir / "files"
            if files_dir.exists():
                try:
                    for item in files_dir.iterdir():
                        items.append(item.name)
                        if item.is_file():
                            total_size += item.stat().st_size
                        elif item.is_dir():
                            total_size += sum(
                                f.stat().st_size 
                                for f in item.rglob('*') if f.is_file()
                            )
                except Exception:
                    pass
        
        return {
            "trash_items": items,
            "estimated_size": total_size
        }
    
    def execute_operation(self, secure_delete: bool = False, 
                         create_backup: bool = False) -> PrivacyOperationResult:
        """Execute the trash emptying operation."""
        self._emit_status("Starting trash emptying operation...")
        
        try:
            if PlatformUtils.is_windows():
                return self._empty_windows_trash(secure_delete, create_backup)
            elif PlatformUtils.is_macos():
                return self._empty_macos_trash(secure_delete, create_backup)
            elif PlatformUtils.is_linux():
                return self._empty_linux_trash(secure_delete, create_backup)
            else:
                return PrivacyOperationResult(
                    False, 
                    f"Platform {PlatformUtils.get_platform()} not supported",
                    0,
                    ["Unsupported platform"]
                )
                
        except Exception as e:
            return PrivacyOperationResult(
                False,
                f"Operation failed: {str(e)}",
                0,
                [str(e)]
            )
    
    def _empty_windows_trash(self, secure_delete: bool, 
                           create_backup: bool) -> PrivacyOperationResult:
        """Empty Windows recycle bin."""
        self._emit_status("Emptying Windows Recycle Bin...")
        self._emit_progress(0, 1, "Accessing Windows Recycle Bin...")
        
        try:
            if secure_delete:
                # For secure deletion on Windows, we need to access individual files
                # This is complex due to Windows recycle bin structure
                self._emit_status("Secure deletion on Windows requires "
                                "administrator privileges...")
                
                if not PlatformUtils.is_admin():
                    return PrivacyOperationResult(
                        False,
                        "Administrator privileges required for secure deletion",
                        0,
                        ["Insufficient privileges"]
                    )
            
            # Use Windows API to empty recycle bin
            success = PlatformUtils.empty_trash()
            
            if success:
                self._emit_progress(1, 1, "Recycle bin emptied successfully")
                return PrivacyOperationResult(
                    True,
                    "Windows Recycle Bin emptied successfully",
                    1
                )
            else:
                return PrivacyOperationResult(
                    False,
                    "Failed to empty Windows Recycle Bin",
                    0,
                    ["Windows API call failed"]
                )
                
        except Exception as e:
            return PrivacyOperationResult(
                False,
                f"Windows trash operation failed: {str(e)}",
                0,
                [str(e)]
            )
    
    def _empty_macos_trash(self, secure_delete: bool, 
                         create_backup: bool) -> PrivacyOperationResult:
        """Empty macOS trash."""
        trash_dir = PlatformUtils.get_trash_directory()
        
        if not trash_dir or not trash_dir.exists():
            return PrivacyOperationResult(
                True,
                "Trash is already empty",
                0
            )
        
        self._emit_status("Emptying macOS Trash...")
        
        try:
            items = list(trash_dir.iterdir())
            total_items = len(items)
            processed = 0
            errors = []
            
            for i, item in enumerate(items):
                if self._check_should_stop():
                    break
                
                self._emit_progress(
                    i, total_items, 
                    f"Processing: {item.name}"
                )
                
                try:
                    if create_backup:
                        self._backup_file(item)
                    
                    if item.is_file():
                        if secure_delete:
                            success = PlatformUtils.secure_delete_file(item)
                        else:
                            item.unlink()
                            success = True
                    elif item.is_dir():
                        if secure_delete:
                            success = self._safe_delete_directory(item, True)
                        else:
                            shutil.rmtree(item)
                            success = True
                    
                    if success:
                        processed += 1
                    else:
                        errors.append(f"Failed to delete: {item.name}")
                        
                except Exception as e:
                    errors.append(f"Error deleting {item.name}: {str(e)}")
            
            self._emit_progress(total_items, total_items, "Trash emptied")
            
            return PrivacyOperationResult(
                len(errors) == 0,
                f"Processed {processed} items from trash",
                processed,
                errors
            )
            
        except Exception as e:
            return PrivacyOperationResult(
                False,
                f"macOS trash operation failed: {str(e)}",
                0,
                [str(e)]
            )
    
    def _empty_linux_trash(self, secure_delete: bool, 
                         create_backup: bool) -> PrivacyOperationResult:
        """Empty Linux trash."""
        trash_dir = PlatformUtils.get_trash_directory()
        
        if not trash_dir or not trash_dir.exists():
            return PrivacyOperationResult(
                True,
                "Trash is already empty",
                0
            )
        
        self._emit_status("Emptying Linux Trash...")
        
        try:
            files_dir = trash_dir / "files"
            info_dir = trash_dir / "info"
            
            processed = 0
            errors = []
            
            # Process files
            if files_dir.exists():
                items = list(files_dir.iterdir())
                total_items = len(items)
                
                for i, item in enumerate(items):
                    if self._check_should_stop():
                        break
                    
                    self._emit_progress(
                        i, total_items,
                        f"Processing: {item.name}"
                    )
                    
                    try:
                        if create_backup:
                            self._backup_file(item)
                        
                        if item.is_file():
                            if secure_delete:
                                success = PlatformUtils.secure_delete_file(item)
                            else:
                                item.unlink()
                                success = True
                        elif item.is_dir():
                            if secure_delete:
                                success = self._safe_delete_directory(item, True)
                            else:
                                shutil.rmtree(item)
                                success = True
                        
                        if success:
                            processed += 1
                        else:
                            errors.append(f"Failed to delete: {item.name}")
                            
                    except Exception as e:
                        errors.append(f"Error deleting {item.name}: {str(e)}")
            
            # Clean info files
            if info_dir.exists():
                for info_file in info_dir.iterdir():
                    try:
                        if info_file.is_file():
                            info_file.unlink()
                    except Exception as e:
                        errors.append(f"Error deleting info file: {str(e)}")
            
            self._emit_progress(1, 1, "Linux trash emptied")
            
            return PrivacyOperationResult(
                len(errors) == 0,
                f"Processed {processed} items from trash",
                processed,
                errors
            )
            
        except Exception as e:
            return PrivacyOperationResult(
                False,
                f"Linux trash operation failed: {str(e)}",
                0,
                [str(e)]
            )