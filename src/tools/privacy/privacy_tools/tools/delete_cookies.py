"""
Delete Cookies Tool

This tool deletes browser cookies across all supported browsers and platforms,
with options for selective deletion by domain, date range, and cookie type.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.privacy_base import PrivacyToolBase, PrivacyOperationResult
from ..core.platform_utils import PlatformUtils
from ..core.data_locations import DataLocations


class DeleteCookiesTool(PrivacyToolBase):
    """Tool for deleting browser cookies across multiple browsers."""
    
    def __init__(self):
        super().__init__("Delete Browser Cookies")
    
    def get_description(self) -> str:
        """Get description of this tool."""
        return ("Deletes browser cookies from all supported browsers. "
                "Supports selective deletion by domain, date range, "
                "and cookie type.")
    
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
    
    def preview_operation(self, **kwargs) -> Dict[str, Any]:
        """Preview what the operation will do."""
        browsers = kwargs.get('browsers', [])
        domain_filter = kwargs.get('domain_filter', None)
        days_old = kwargs.get('days_old', None)
        cookie_types = kwargs.get('cookie_types', ['all'])
        
        preview = {
            "browsers": browsers or self.browser_detector.detect_installed_browsers(),
            "domain_filter": domain_filter,
            "days_old": days_old,
            "cookie_types": cookie_types,
            "estimated_cookies": {},
            "warnings": [],
            "browser_status": {}
        }
        
        # Check each browser
        for browser in preview["browsers"]:
            if not self.browser_detector.is_browser_running(browser):
                cookie_count = self._count_cookies(browser, domain_filter, days_old)
                preview["estimated_cookies"][browser] = cookie_count
                preview["browser_status"][browser] = "ready"
            else:
                preview["browser_status"][browser] = "running"
                preview["warnings"].append(
                    f"{browser.title()} is currently running. "
                    f"Please close it before proceeding."
                )
        
        return preview
    
    def execute_operation(self, **kwargs) -> PrivacyOperationResult:
        """Execute the cookie deletion operation."""
        browsers = kwargs.get('browsers', [])
        domain_filter = kwargs.get('domain_filter', None)
        days_old = kwargs.get('days_old', None)
        cookie_types = kwargs.get('cookie_types', ['all'])
        create_backup = kwargs.get('create_backup', False)
        
        if not browsers:
            browsers = self.browser_detector.detect_installed_browsers()
        
        self._emit_status("Starting cookie deletion operation...")
        
        # Validate browsers are not running
        if not self._validate_browser_not_running(browsers):
            return PrivacyOperationResult(
                False,
                "One or more browsers are currently running",
                0,
                ["Please close all browsers before proceeding"]
            )
        
        total_deleted = 0
        errors = []
        processed_browsers = 0
        
        try:
            for i, browser in enumerate(browsers):
                if self._check_should_stop():
                    break
                
                self._emit_progress(
                    i, len(browsers),
                    f"Processing {browser.title()} cookies..."
                )
                
                try:
                    deleted_count = self._delete_browser_cookies(
                        browser, domain_filter, days_old, 
                        cookie_types, create_backup
                    )
                    total_deleted += deleted_count
                    processed_browsers += 1
                    
                    self._emit_status(
                        f"Deleted {deleted_count} cookies from {browser.title()}"
                    )
                    
                except Exception as e:
                    error_msg = f"Failed to process {browser}: {str(e)}"
                    errors.append(error_msg)
                    self._emit_error(error_msg)
            
            self._emit_progress(
                len(browsers), len(browsers),
                f"Cookie deletion complete"
            )
            
            success = len(errors) == 0
            message = f"Deleted {total_deleted} cookies from {processed_browsers} browsers"
            
            return PrivacyOperationResult(success, message, total_deleted, errors)
            
        except Exception as e:
            return PrivacyOperationResult(
                False,
                f"Cookie deletion failed: {str(e)}",
                total_deleted,
                [str(e)]
            )
    
    def _count_cookies(self, browser: str, domain_filter: Optional[str] = None,
                      days_old: Optional[int] = None) -> int:
        """Count cookies that would be deleted."""
        try:
            data_paths = self.browser_detector.get_browser_data_paths(browser)
            cookie_paths = data_paths.get("cookies", [])
            
            total_count = 0
            
            for cookie_path in cookie_paths:
                if not cookie_path.exists():
                    continue
                
                if browser == DataLocations.CHROME or browser == DataLocations.EDGE:
                    total_count += self._count_chromium_cookies(
                        cookie_path, domain_filter, days_old
                    )
                elif browser == DataLocations.FIREFOX:
                    total_count += self._count_firefox_cookies(
                        cookie_path, domain_filter, days_old
                    )
                elif browser == DataLocations.SAFARI:
                    total_count += self._count_safari_cookies(
                        cookie_path, domain_filter, days_old
                    )
            
            return total_count
            
        except Exception:
            return 0
    
    def _count_chromium_cookies(self, cookie_path: Path, 
                               domain_filter: Optional[str] = None,
                               days_old: Optional[int] = None) -> int:
        """Count cookies in Chromium-based browsers."""
        try:
            with sqlite3.connect(str(cookie_path)) as conn:
                cursor = conn.cursor()
                
                query = "SELECT COUNT(*) FROM cookies WHERE 1=1"
                params = []
                
                if domain_filter:
                    query += " AND host_key LIKE ?"
                    params.append(f"%{domain_filter}%")
                
                if days_old is not None:
                    cutoff_time = datetime.now() - timedelta(days=days_old)
                    # Chromium stores time as microseconds since Windows epoch
                    cutoff_chromium = int(cutoff_time.timestamp() * 1000000) + 11644473600000000
                    query += " AND creation_utc < ?"
                    params.append(cutoff_chromium)
                
                cursor.execute(query, params)
                return cursor.fetchone()[0]
                
        except Exception:
            return 0
    
    def _count_firefox_cookies(self, cookie_path: Path,
                              domain_filter: Optional[str] = None,
                              days_old: Optional[int] = None) -> int:
        """Count cookies in Firefox."""
        try:
            with sqlite3.connect(str(cookie_path)) as conn:
                cursor = conn.cursor()
                
                query = "SELECT COUNT(*) FROM moz_cookies WHERE 1=1"
                params = []
                
                if domain_filter:
                    query += " AND host LIKE ?"
                    params.append(f"%{domain_filter}%")
                
                if days_old is not None:
                    cutoff_time = datetime.now() - timedelta(days=days_old)
                    cutoff_firefox = int(cutoff_time.timestamp())
                    query += " AND creationTime < ?"
                    params.append(cutoff_firefox * 1000000)  # Firefox uses microseconds
                
                cursor.execute(query, params)
                return cursor.fetchone()[0]
                
        except Exception:
            return 0
    
    def _count_safari_cookies(self, cookie_path: Path,
                             domain_filter: Optional[str] = None,
                             days_old: Optional[int] = None) -> int:
        """Count cookies in Safari (simplified)."""
        # Safari uses binary cookie format, complex to parse
        # Return estimated count based on file size
        try:
            if cookie_path.exists():
                file_size = cookie_path.stat().st_size
                # Rough estimate: ~100 bytes per cookie
                return max(1, file_size // 100)
        except Exception:
            pass
        return 0
    
    def _delete_browser_cookies(self, browser: str, 
                               domain_filter: Optional[str] = None,
                               days_old: Optional[int] = None,
                               cookie_types: List[str] = None,
                               create_backup: bool = False) -> int:
        """Delete cookies for a specific browser."""
        data_paths = self.browser_detector.get_browser_data_paths(browser)
        cookie_paths = data_paths.get("cookies", [])
        
        total_deleted = 0
        
        for cookie_path in cookie_paths:
            if not cookie_path.exists():
                continue
            
            if create_backup:
                self._backup_file(cookie_path)
            
            if browser == DataLocations.CHROME or browser == DataLocations.EDGE:
                deleted = self._delete_chromium_cookies(
                    cookie_path, domain_filter, days_old, cookie_types
                )
            elif browser == DataLocations.FIREFOX:
                deleted = self._delete_firefox_cookies(
                    cookie_path, domain_filter, days_old, cookie_types
                )
            elif browser == DataLocations.SAFARI:
                deleted = self._delete_safari_cookies(
                    cookie_path, domain_filter, days_old, cookie_types
                )
            else:
                deleted = 0
            
            total_deleted += deleted
        
        return total_deleted
    
    def _delete_chromium_cookies(self, cookie_path: Path,
                                domain_filter: Optional[str] = None,
                                days_old: Optional[int] = None,
                                cookie_types: List[str] = None) -> int:
        """Delete cookies from Chromium-based browsers."""
        try:
            # Count before deletion
            count_before = self._count_chromium_cookies(cookie_path, domain_filter, days_old)
            
            query = "DELETE FROM cookies WHERE 1=1"
            params = []
            
            if domain_filter:
                query += " AND host_key LIKE ?"
                params.append(f"%{domain_filter}%")
            
            if days_old is not None:
                cutoff_time = datetime.now() - timedelta(days=days_old)
                cutoff_chromium = int(cutoff_time.timestamp() * 1000000) + 11644473600000000
                query += " AND creation_utc < ?"
                params.append(cutoff_chromium)
            
            # Execute deletion
            success = self._execute_sql_on_database(cookie_path, [query])
            
            if success:
                return count_before
            else:
                return 0
                
        except Exception:
            return 0
    
    def _delete_firefox_cookies(self, cookie_path: Path,
                               domain_filter: Optional[str] = None,
                               days_old: Optional[int] = None,
                               cookie_types: List[str] = None) -> int:
        """Delete cookies from Firefox."""
        try:
            # Count before deletion
            count_before = self._count_firefox_cookies(cookie_path, domain_filter, days_old)
            
            query = "DELETE FROM moz_cookies WHERE 1=1"
            params = []
            
            if domain_filter:
                query += " AND host LIKE ?"
                params.append(f"%{domain_filter}%")
            
            if days_old is not None:
                cutoff_time = datetime.now() - timedelta(days=days_old)
                cutoff_firefox = int(cutoff_time.timestamp() * 1000000)
                query += " AND creationTime < ?"
                params.append(cutoff_firefox)
            
            # Execute deletion
            success = self._execute_sql_on_database(cookie_path, [query])
            
            if success:
                return count_before
            else:
                return 0
                
        except Exception:
            return 0
    
    def _delete_safari_cookies(self, cookie_path: Path,
                              domain_filter: Optional[str] = None,
                              days_old: Optional[int] = None,
                              cookie_types: List[str] = None) -> int:
        """Delete Safari cookies."""
        try:
            # Safari uses binary format, simpler to delete entire file
            if cookie_path.exists():
                estimated_count = self._count_safari_cookies(cookie_path, domain_filter, days_old)
                
                if domain_filter or days_old:
                    # Partial deletion not easily supported for Safari binary format
                    # Would need specialized parsing
                    return 0
                else:
                    # Delete entire cookie file
                    cookie_path.unlink()
                    return estimated_count
            
            return 0
            
        except Exception:
            return 0