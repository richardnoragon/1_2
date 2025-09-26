"""Automated file system scanning engine."""

import os
import hashlib
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Set
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class ScanMode(Enum):
    """File scanning modes."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    CHECKSUM = "checksum"


class FileType(Enum):
    """File type categories."""
    REGULAR = "regular"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    SPECIAL = "special"
    UNKNOWN = "unknown"


class ScannerEngine:
    """Automated file system scanning engine.
    
    Provides comprehensive file system scanning capabilities with:
    - Configurable scan depth and filters
    - Parallel scanning for performance
    - Checksum verification
    - Permission and timestamp checking
    - Progress tracking and cancellation
    """
    
    def __init__(self):
        """Initialize the scanner engine."""
        self.platform_detector = get_platform_detector()
        
        # Scan state
        self._is_scanning = False
        self._scan_cancelled = False
        self._scan_lock = threading.Lock()
        
        # Progress tracking
        self._progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._scan_stats = {
            'files_scanned': 0,
            'directories_scanned': 0,
            'errors_encountered': 0,
            'bytes_scanned': 0,
            'start_time': None,
            'current_path': '',
            'estimated_total': 0,
            'progress_percent': 0.0
        }
        
        # Default configuration
        self.default_config = {
            'max_depth': 10,
            'follow_symlinks': False,
            'include_hidden': False,
            'file_filters': ['*'],
            'exclude_patterns': [
                '*.tmp', '*.temp', '*.log', '*.cache',
                'System Volume Information', '$RECYCLE.BIN',
                '.Trash*', '.DS_Store', 'Thumbs.db'
            ],
            'max_file_size': 1024 * 1024 * 1024,  # 1GB
            'checksum_algorithm': 'sha256',
            'verify_permissions': True,
            'verify_timestamps': True,
            'parallel_workers': 4,
            'chunk_size': 8192
        }
        
    def run_scan(
        self,
        config: Dict[str, Any],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Run a file system scan.
        
        Args:
            config: Scan configuration
            progress_callback: Progress update callback
            
        Returns:
            Dict containing scan results
        """
        with self._scan_lock:
            if self._is_scanning:
                raise RuntimeError("Scan already in progress")
            
            self._is_scanning = True
            self._scan_cancelled = False
            self._progress_callback = progress_callback
        
        try:
            # Merge configuration
            scan_config = self.default_config.copy()
            scan_config.update(config)
            
            # Initialize scan
            self._reset_scan_stats()
            self._scan_stats['start_time'] = datetime.now()
            
            # Get scan paths
            scan_paths = scan_config.get('scan_paths', [])
            if not scan_paths:
                scan_paths = self._get_default_scan_paths()
            
            # Estimate total files for progress tracking
            if scan_config.get('estimate_progress', True):
                self._estimate_total_files(scan_paths, scan_config)
            
            # Run the scan
            scan_results = self._execute_scan(scan_paths, scan_config)
            
            # Finalize results
            end_time = datetime.now()
            duration = (end_time - self._scan_stats['start_time']).total_seconds()
            
            final_results = {
                'scan_id': scan_config.get('scan_id', 'unknown'),
                'scan_type': scan_config.get('scan_type', 'standard'),
                'start_time': self._scan_stats['start_time'].isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'scan_paths': scan_paths,
                'config': scan_config,
                'statistics': self._scan_stats.copy(),
                'results': scan_results,
                'cancelled': self._scan_cancelled,
                'success': not self._scan_cancelled
            }
            
            return final_results
            
        except Exception as e:
            error_handler.handle_error(e, "ScannerEngine.run_scan")
            return {
                'error': str(e),
                'success': False,
                'cancelled': self._scan_cancelled,
                'statistics': self._scan_stats.copy()
            }
        finally:
            with self._scan_lock:
                self._is_scanning = False
                self._progress_callback = None
    
    def stop_scan(self) -> None:
        """Stop the current scan."""
        with self._scan_lock:
            if self._is_scanning:
                self._scan_cancelled = True
    
    def is_scanning(self) -> bool:
        """Check if a scan is currently running.
        
        Returns:
            bool: True if scanning, False otherwise
        """
        with self._scan_lock:
            return self._is_scanning
    
    def _reset_scan_stats(self) -> None:
        """Reset scan statistics."""
        self._scan_stats = {
            'files_scanned': 0,
            'directories_scanned': 0,
            'errors_encountered': 0,
            'bytes_scanned': 0,
            'start_time': None,
            'current_path': '',
            'estimated_total': 0,
            'progress_percent': 0.0
        }
    
    def _get_default_scan_paths(self) -> List[str]:
        """Get default scan paths for the current platform.
        
        Returns:
            List of default paths to scan
        """
        if self.platform_detector.is_windows():
            return ['C:\\']
        elif self.platform_detector.is_macos():
            return ['/Users', '/Applications', '/System/Library']
        elif self.platform_detector.is_linux():
            return ['/home', '/etc', '/var', '/usr']
        else:
            return ['/']
    
    def _estimate_total_files(
        self, 
        scan_paths: List[str], 
        config: Dict[str, Any]
    ) -> None:
        """Estimate total number of files for progress tracking.
        
        Args:
            scan_paths: Paths to scan
            config: Scan configuration
        """
        try:
            total_estimate = 0
            max_depth = config.get('max_depth', 10)
            
            for path in scan_paths:
                if os.path.exists(path):
                    # Quick estimation by sampling directories
                    estimate = self._estimate_path_files(path, max_depth, 0)
                    total_estimate += estimate
            
            self._scan_stats['estimated_total'] = total_estimate
            
        except Exception as e:
            # If estimation fails, continue without progress tracking
            self._scan_stats['estimated_total'] = 0
    
    def _estimate_path_files(
        self, 
        path: str, 
        max_depth: int, 
        current_depth: int
    ) -> int:
        """Estimate files in a path (quick sampling).
        
        Args:
            path: Path to estimate
            max_depth: Maximum scan depth
            current_depth: Current depth level
            
        Returns:
            int: Estimated file count
        """
        if current_depth >= max_depth or self._scan_cancelled:
            return 0
        
        try:
            if not os.path.isdir(path):
                return 1
            
            # Sample first few entries for estimation
            entries = list(os.listdir(path))[:20]  # Sample first 20 entries
            file_count = 0
            dir_count = 0
            
            for entry in entries:
                entry_path = os.path.join(path, entry)
                if os.path.isfile(entry_path):
                    file_count += 1
                elif os.path.isdir(entry_path):
                    dir_count += 1
            
            # Estimate based on sample
            total_entries = len(os.listdir(path))
            if len(entries) > 0:
                estimated_files = (file_count * total_entries) // len(entries)
                estimated_dirs = (dir_count * total_entries) // len(entries)
            else:
                estimated_files = 0
                estimated_dirs = 0
            
            # Recursively estimate subdirectories (limited sampling)
            subdir_files = 0
            if current_depth < max_depth - 1 and estimated_dirs > 0:
                # Sample a few subdirectories
                sample_dirs = [
                    os.path.join(path, entry) for entry in entries[:5]
                    if os.path.isdir(os.path.join(path, entry))
                ]
                
                for subdir in sample_dirs:
                    subdir_files += self._estimate_path_files(
                        subdir, max_depth, current_depth + 1
                    )
                
                # Scale up based on total directories
                if len(sample_dirs) > 0:
                    subdir_files = (subdir_files * estimated_dirs) // len(sample_dirs)
            
            return estimated_files + subdir_files
            
        except (OSError, PermissionError):
            return 0
    
    def _execute_scan(
        self, 
        scan_paths: List[str], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the file system scan.
        
        Args:
            scan_paths: Paths to scan
            config: Scan configuration
            
        Returns:
            Dict containing scan results
        """
        scan_results = {
            'files': [],
            'directories': [],
            'errors': [],
            'checksums': {},
            'permissions': {},
            'timestamps': {},
            'symlinks': [],
            'special_files': []
        }
        
        # Determine scan mode
        scan_mode = config.get('scan_mode', ScanMode.STANDARD)
        parallel_workers = config.get('parallel_workers', 4)
        
        if parallel_workers > 1 and len(scan_paths) > 1:
            # Parallel scanning for multiple paths
            scan_results = self._parallel_scan(scan_paths, config, scan_results)
        else:
            # Sequential scanning
            for path in scan_paths:
                if self._scan_cancelled:
                    break
                self._scan_path(path, config, scan_results, 0)
        
        return scan_results
    
    def _parallel_scan(
        self,
        scan_paths: List[str],
        config: Dict[str, Any],
        scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute parallel scanning of multiple paths.
        
        Args:
            scan_paths: Paths to scan
            config: Scan configuration
            scan_results: Results dictionary to populate
            
        Returns:
            Updated scan results
        """
        max_workers = config.get('parallel_workers', 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scan tasks
            future_to_path = {
                executor.submit(
                    self._scan_path_isolated, path, config
                ): path for path in scan_paths
            }
            
            # Collect results
            for future in as_completed(future_to_path):
                if self._scan_cancelled:
                    break
                
                path = future_to_path[future]
                try:
                    path_results = future.result()
                    self._merge_scan_results(scan_results, path_results)
                except Exception as e:
                    error_msg = f"Error scanning {path}: {e}"
                    scan_results['errors'].append({
                        'path': path,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return scan_results
    
    def _scan_path_isolated(
        self, 
        path: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Scan a single path in isolation (for parallel execution).
        
        Args:
            path: Path to scan
            config: Scan configuration
            
        Returns:
            Scan results for this path
        """
        isolated_results = {
            'files': [],
            'directories': [],
            'errors': [],
            'checksums': {},
            'permissions': {},
            'timestamps': {},
            'symlinks': [],
            'special_files': []
        }
        
        self._scan_path(path, config, isolated_results, 0)
        return isolated_results
    
    def _scan_path(
        self,
        path: str,
        config: Dict[str, Any],
        results: Dict[str, Any],
        depth: int
    ) -> None:
        """Recursively scan a file system path.
        
        Args:
            path: Path to scan
            config: Scan configuration
            results: Results dictionary to populate
            depth: Current recursion depth
        """
        if self._scan_cancelled:
            return
        
        if depth > config.get('max_depth', 10):
            return
        
        try:
            # Update progress
            self._scan_stats['current_path'] = path
            self._update_progress()
            
            # Check if path exists
            if not os.path.exists(path):
                results['errors'].append({
                    'path': path,
                    'error': 'Path does not exist',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Get path information
            path_info = self._get_path_info(path, config)
            
            if path_info['type'] == FileType.DIRECTORY:
                self._scan_directory(path, config, results, depth)
            elif path_info['type'] == FileType.REGULAR:
                self._scan_file(path, config, results)
            elif path_info['type'] == FileType.SYMLINK:
                self._scan_symlink(path, config, results)
            else:
                results['special_files'].append(path_info)
            
        except PermissionError as e:
            results['errors'].append({
                'path': path,
                'error': f'Permission denied: {e}',
                'timestamp': datetime.now().isoformat()
            })
            self._scan_stats['errors_encountered'] += 1
        except Exception as e:
            results['errors'].append({
                'path': path,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            self._scan_stats['errors_encountered'] += 1
    
    def _scan_directory(
        self,
        dir_path: str,
        config: Dict[str, Any],
        results: Dict[str, Any],
        depth: int
    ) -> None:
        """Scan a directory.
        
        Args:
            dir_path: Directory path to scan
            config: Scan configuration
            results: Results dictionary to populate
            depth: Current recursion depth
        """
        try:
            # Add directory to results
            dir_info = self._get_path_info(dir_path, config)
            results['directories'].append(dir_info)
            self._scan_stats['directories_scanned'] += 1
            
            # List directory contents
            entries = os.listdir(dir_path)
            
            # Apply filters
            filtered_entries = self._apply_filters(entries, config)
            
            # Scan each entry
            for entry in filtered_entries:
                if self._scan_cancelled:
                    break
                
                entry_path = os.path.join(dir_path, entry)
                self._scan_path(entry_path, config, results, depth + 1)
                
        except PermissionError as e:
            results['errors'].append({
                'path': dir_path,
                'error': f'Permission denied accessing directory: {e}',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            results['errors'].append({
                'path': dir_path,
                'error': f'Error scanning directory: {e}',
                'timestamp': datetime.now().isoformat()
            })
    
    def _scan_file(
        self,
        file_path: str,
        config: Dict[str, Any],
        results: Dict[str, Any]
    ) -> None:
        """Scan a regular file.
        
        Args:
            file_path: File path to scan
            config: Scan configuration
            results: Results dictionary to populate
        """
        try:
            # Get file information
            file_info = self._get_path_info(file_path, config)
            
            # Check file size limits
            max_size = config.get('max_file_size', 1024 * 1024 * 1024)
            if file_info.get('size', 0) > max_size:
                results['errors'].append({
                    'path': file_path,
                    'error': f'File too large: {file_info.get("size", 0)} bytes',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Add file to results
            results['files'].append(file_info)
            self._scan_stats['files_scanned'] += 1
            self._scan_stats['bytes_scanned'] += file_info.get('size', 0)
            
            # Calculate checksum if requested
            if config.get('check_checksums', False):
                checksum = self._calculate_checksum(file_path, config)
                if checksum:
                    results['checksums'][file_path] = checksum
            
            # Verify permissions if requested
            if config.get('verify_permissions', False):
                permissions = self._get_permissions(file_path)
                results['permissions'][file_path] = permissions
            
            # Verify timestamps if requested
            if config.get('verify_timestamps', False):
                timestamps = self._get_timestamps(file_path)
                results['timestamps'][file_path] = timestamps
                
        except Exception as e:
            results['errors'].append({
                'path': file_path,
                'error': f'Error scanning file: {e}',
                'timestamp': datetime.now().isoformat()
            })
    
    def _scan_symlink(
        self,
        link_path: str,
        config: Dict[str, Any],
        results: Dict[str, Any]
    ) -> None:
        """Scan a symbolic link.
        
        Args:
            link_path: Symlink path to scan
            config: Scan configuration
            results: Results dictionary to populate
        """
        try:
            link_info = self._get_path_info(link_path, config)
            
            # Get link target
            try:
                target = os.readlink(link_path)
                link_info['target'] = target
                link_info['target_exists'] = os.path.exists(target)
            except OSError as e:
                link_info['target_error'] = str(e)
            
            results['symlinks'].append(link_info)
            
            # Follow symlinks if configured
            if config.get('follow_symlinks', False) and link_info.get('target_exists'):
                target_path = link_info.get('target')
                if target_path and not self._is_circular_link(link_path, target_path):
                    self._scan_path(target_path, config, results, 0)
                    
        except Exception as e:
            results['errors'].append({
                'path': link_path,
                'error': f'Error scanning symlink: {e}',
                'timestamp': datetime.now().isoformat()
            })
    
    def _get_path_info(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive information about a path.
        
        Args:
            path: Path to analyze
            config: Scan configuration
            
        Returns:
            Dict containing path information
        """
        try:
            stat_info = os.lstat(path)  # Use lstat to not follow symlinks
            
            # Determine file type
            if os.path.islink(path):
                file_type = FileType.SYMLINK
            elif os.path.isdir(path):
                file_type = FileType.DIRECTORY
            elif os.path.isfile(path):
                file_type = FileType.REGULAR
            else:
                file_type = FileType.SPECIAL
            
            path_info = {
                'path': path,
                'type': file_type.value,
                'size': stat_info.st_size,
                'mode': stat_info.st_mode,
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid,
                'atime': stat_info.st_atime,
                'mtime': stat_info.st_mtime,
                'ctime': stat_info.st_ctime,
                'inode': stat_info.st_ino,
                'device': stat_info.st_dev,
                'nlinks': stat_info.st_nlink
            }
            
            # Add platform-specific information
            if hasattr(stat_info, 'st_blocks'):
                path_info['blocks'] = stat_info.st_blocks
            if hasattr(stat_info, 'st_blksize'):
                path_info['block_size'] = stat_info.st_blksize
            
            return path_info
            
        except Exception as e:
            return {
                'path': path,
                'type': FileType.UNKNOWN.value,
                'error': str(e)
            }
    
    def _apply_filters(
        self, 
        entries: List[str], 
        config: Dict[str, Any]
    ) -> List[str]:
        """Apply file filters to directory entries.
        
        Args:
            entries: Directory entries to filter
            config: Scan configuration
            
        Returns:
            Filtered list of entries
        """
        filtered = []
        
        include_hidden = config.get('include_hidden', False)
        exclude_patterns = config.get('exclude_patterns', [])
        
        for entry in entries:
            # Skip hidden files if not included
            if not include_hidden and entry.startswith('.'):
                continue
            
            # Check exclude patterns
            excluded = False
            for pattern in exclude_patterns:
                if self._matches_pattern(entry, pattern):
                    excluded = True
                    break
            
            if not excluded:
                filtered.append(entry)
        
        return filtered
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern.
        
        Args:
            filename: Filename to check
            pattern: Pattern to match against
            
        Returns:
            bool: True if matches, False otherwise
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def _calculate_checksum(
        self, 
        file_path: str, 
        config: Dict[str, Any]
    ) -> Optional[str]:
        """Calculate file checksum.
        
        Args:
            file_path: Path to file
            config: Scan configuration
            
        Returns:
            Checksum string or None if error
        """
        try:
            algorithm = config.get('checksum_algorithm', 'sha256')
            chunk_size = config.get('chunk_size', 8192)
            
            if algorithm == 'md5':
                hasher = hashlib.md5()
            elif algorithm == 'sha1':
                hasher = hashlib.sha1()
            elif algorithm == 'sha256':
                hasher = hashlib.sha256()
            else:
                return None
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    if self._scan_cancelled:
                        return None
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception:
            return None
    
    def _get_permissions(self, path: str) -> Dict[str, Any]:
        """Get file permissions information.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dict containing permission information
        """
        try:
            stat_info = os.stat(path)
            mode = stat_info.st_mode
            
            return {
                'mode_octal': oct(mode)[-3:],
                'mode_decimal': mode,
                'owner_read': bool(mode & 0o400),
                'owner_write': bool(mode & 0o200),
                'owner_execute': bool(mode & 0o100),
                'group_read': bool(mode & 0o040),
                'group_write': bool(mode & 0o020),
                'group_execute': bool(mode & 0o010),
                'other_read': bool(mode & 0o004),
                'other_write': bool(mode & 0o002),
                'other_execute': bool(mode & 0o001)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_timestamps(self, path: str) -> Dict[str, Any]:
        """Get file timestamp information.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dict containing timestamp information
        """
        try:
            stat_info = os.stat(path)
            
            return {
                'access_time': stat_info.st_atime,
                'modify_time': stat_info.st_mtime,
                'change_time': stat_info.st_ctime,
                'access_time_iso': datetime.fromtimestamp(
                    stat_info.st_atime
                ).isoformat(),
                'modify_time_iso': datetime.fromtimestamp(
                    stat_info.st_mtime
                ).isoformat(),
                'change_time_iso': datetime.fromtimestamp(
                    stat_info.st_ctime
                ).isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _is_circular_link(self, link_path: str, target_path: str) -> bool:
        """Check if following a symlink would create a circular reference.
        
        Args:
            link_path: Path of the symlink
            target_path: Target path of the symlink
            
        Returns:
            bool: True if circular, False otherwise
        """
        try:
            # Simple check: if target is a parent of link
            link_abs = os.path.abspath(link_path)
            target_abs = os.path.abspath(target_path)
            
            return link_abs.startswith(target_abs)
        except Exception:
            return True  # Assume circular if we can't determine
    
    def _merge_scan_results(
        self, 
        main_results: Dict[str, Any], 
        path_results: Dict[str, Any]
    ) -> None:
        """Merge scan results from parallel scanning.
        
        Args:
            main_results: Main results dictionary
            path_results: Results from a single path scan
        """
        # Merge lists
        for key in ['files', 'directories', 'errors', 'symlinks', 'special_files']:
            main_results[key].extend(path_results.get(key, []))
        
        # Merge dictionaries
        for key in ['checksums', 'permissions', 'timestamps']:
            main_results[key].update(path_results.get(key, {}))
    
    def _update_progress(self) -> None:
        """Update scan progress and notify callback."""
        try:
            # Calculate progress percentage
            if self._scan_stats['estimated_total'] > 0:
                scanned = (self._scan_stats['files_scanned'] + 
                          self._scan_stats['directories_scanned'])
                progress = min(100.0, (scanned / self._scan_stats['estimated_total']) * 100)
                self._scan_stats['progress_percent'] = progress
            
            # Call progress callback if available
            if self._progress_callback:
                progress_data = self._scan_stats.copy()
                progress_data['timestamp'] = datetime.now().isoformat()
                self._progress_callback(progress_data)
                
        except Exception:
            # Don't let progress updates break the scan
            pass