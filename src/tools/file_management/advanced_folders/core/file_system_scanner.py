"""
Enterprise-grade File System Scanner for Advanced Folders.

This module provides comprehensive file system scanning capabilities with
recursive directory traversal, symbolic link handling, permission validation,
and concurrent processing for enterprise-scale operations.

Features:
- Multi-threaded concurrent processing
- Symbolic link detection and handling
- Permission validation and access control
- Memory-efficient scanning for large directories
- Real-time progress reporting and cancellation
- Comprehensive error handling and recovery
- Support for network drives and remote filesystems
"""

import hashlib
import logging
import mimetypes
import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

try:
    PYTHON_MAGIC_AVAILABLE = True
except ImportError:
    PYTHON_MAGIC_AVAILABLE = False

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from ..exceptions import (
    FileSystemException,
    PermissionException,
    ValidationException,
)
from ..models.folder_configuration import DirectoryTarget, SecuritySettings


@dataclass
class ScanStatistics:
    """Statistics collected during file system scanning."""

    # Counts
    files_scanned: int = 0
    directories_scanned: int = 0
    symlinks_found: int = 0
    permission_errors: int = 0
    access_errors: int = 0

    # Size information
    total_size_bytes: int = 0
    largest_file_size: int = 0
    average_file_size: float = 0.0

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    elapsed_seconds: float = 0.0
    files_per_second: float = 0.0

    # Memory usage
    peak_memory_mb: float = 0.0
    current_memory_mb: float = 0.0

    # Error tracking
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(self, error_type: str, path: str, message: str):
        """Add error to statistics."""
        self.errors.append(
            {
                "type": error_type,
                "path": path,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def add_warning(self, warning_type: str, path: str, message: str):
        """Add warning to statistics."""
        self.warnings.append(
            {
                "type": warning_type,
                "path": path,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def update_memory_usage(self):
        """Update memory usage statistics if psutil is available."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                self.current_memory_mb = memory_info.rss / (1024 * 1024)
                self.peak_memory_mb = max(
                    self.peak_memory_mb, self.current_memory_mb
                )
            except Exception:
                pass  # Ignore memory monitoring errors

    def finalize(self):
        """Finalize statistics after scan completion."""
        self.end_time = datetime.now(timezone.utc)
        if self.start_time:
            self.elapsed_seconds = (
                self.end_time - self.start_time
            ).total_seconds()
            if self.elapsed_seconds > 0:
                self.files_per_second = (
                    self.files_scanned / self.elapsed_seconds
                )

        if self.files_scanned > 0:
            self.average_file_size = self.total_size_bytes / self.files_scanned

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return {
            "files_scanned": self.files_scanned,
            "directories_scanned": self.directories_scanned,
            "symlinks_found": self.symlinks_found,
            "permission_errors": self.permission_errors,
            "access_errors": self.access_errors,
            "total_size_bytes": self.total_size_bytes,
            "total_size_mb": round(self.total_size_bytes / (1024 * 1024), 2),
            "largest_file_size": self.largest_file_size,
            "average_file_size": round(self.average_file_size, 2),
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "files_per_second": round(self.files_per_second, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class FileInfo:
    """Comprehensive file information structure."""

    # Basic file information
    path: str
    name: str
    extension: str
    size_bytes: int

    # Timestamps
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime

    # File type and attributes
    is_file: bool
    is_directory: bool
    is_symlink: bool
    is_hidden: bool
    is_system: bool

    # Permissions and security
    permissions: str
    owner: str
    group: str
    readable: bool
    writable: bool
    executable: bool

    # Content information
    mime_type: str
    encoding: Optional[str] = None

    # Computed attributes
    path_hash: str = field(init=False)
    relative_path: str = ""
    depth: int = 0

    def __post_init__(self):
        """Compute derived attributes."""
        self.path_hash = hashlib.md5(self.path.encode("utf-8")).hexdigest()

    @classmethod
    def from_path(
        cls,
        path: Path,
        base_path: Optional[Path] = None,
        include_metadata: bool = True,
    ) -> "FileInfo":
        """
        Create FileInfo from filesystem path.

        Args:
            path: Path to analyze
            base_path: Base path for relative path calculation
            include_metadata: Whether to include extended metadata

        Returns:
            FileInfo instance

        Raises:
            FileSystemException: If path cannot be accessed
        """
        try:
            path = Path(path).resolve()
            stat_info = path.stat()

            # Basic information
            name = path.name
            extension = path.suffix.lower().lstrip(".") if path.suffix else ""
            size_bytes = stat_info.st_size if path.is_file() else 0

            # Timestamps
            created_time = datetime.fromtimestamp(
                stat_info.st_ctime, timezone.utc
            )
            modified_time = datetime.fromtimestamp(
                stat_info.st_mtime, timezone.utc
            )
            accessed_time = datetime.fromtimestamp(
                stat_info.st_atime, timezone.utc
            )

            # File type detection
            is_file = path.is_file()
            is_directory = path.is_dir()
            is_symlink = path.is_symlink()

            # Hidden and system file detection (platform-specific)
            is_hidden = cls._is_hidden_file(path)
            is_system = cls._is_system_file(path)

            # Permissions
            permissions = cls._get_permissions_string(stat_info.st_mode)
            owner = cls._get_owner(path)
            group = cls._get_group(path)

            readable = os.access(path, os.R_OK)
            writable = os.access(path, os.W_OK)
            executable = os.access(path, os.X_OK)

            # MIME type detection
            mime_type = (
                cls._detect_mime_type(path) if is_file else "inode/directory"
            )
            encoding = (
                cls._detect_encoding(path)
                if is_file and include_metadata
                else None
            )

            # Relative path calculation
            relative_path = ""
            depth = 0
            if base_path:
                try:
                    relative_path = str(path.relative_to(base_path))
                    depth = len(Path(relative_path).parts) - 1
                except ValueError:
                    relative_path = str(path)

            return cls(
                path=str(path),
                name=name,
                extension=extension,
                size_bytes=size_bytes,
                created_time=created_time,
                modified_time=modified_time,
                accessed_time=accessed_time,
                is_file=is_file,
                is_directory=is_directory,
                is_symlink=is_symlink,
                is_hidden=is_hidden,
                is_system=is_system,
                permissions=permissions,
                owner=owner,
                group=group,
                readable=readable,
                writable=writable,
                executable=executable,
                mime_type=mime_type,
                encoding=encoding,
                relative_path=relative_path,
                depth=depth,
            )

        except PermissionError as e:
            raise PermissionException(
                f"Permission denied accessing path: {path}",
                error_code="SCANNER_PERMISSION_DENIED",
                context={"path": str(path)},
                suggestion=(
                    "Check file permissions and run with appropriate privileges"
                ),
                cause=e,
            )
        except OSError as e:
            raise FileSystemException(
                f"Filesystem error accessing path: {path}",
                error_code="SCANNER_FILESYSTEM_ERROR",
                context={"path": str(path), "os_error": str(e)},
                cause=e,
            )
        except Exception as e:
            raise FileSystemException(
                f"Unexpected error processing path: {path}",
                error_code="SCANNER_UNEXPECTED_ERROR",
                context={"path": str(path)},
                cause=e,
            )

    @staticmethod
    def _is_hidden_file(path: Path) -> bool:
        """Detect if file is hidden (platform-specific)."""
        if os.name == "nt":  # Windows
            try:
                attrs = os.stat(path).st_file_attributes
                return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                return path.name.startswith(".")
        else:  # Unix-like systems
            return path.name.startswith(".")

    @staticmethod
    def _is_system_file(path: Path) -> bool:
        """Detect if file is a system file (platform-specific)."""
        if os.name == "nt":  # Windows
            try:
                attrs = os.stat(path).st_file_attributes
                return bool(attrs & stat.FILE_ATTRIBUTE_SYSTEM)
            except (AttributeError, OSError):
                return False
        else:  # Unix-like systems
            # Common system directories
            system_paths = {
                "/bin",
                "/sbin",
                "/usr",
                "/etc",
                "/var",
                "/sys",
                "/proc",
                "/dev",
            }
            return any(
                str(path).startswith(sys_path) for sys_path in system_paths
            )

    @staticmethod
    def _get_permissions_string(mode: int) -> str:
        """Convert file mode to permissions string."""
        permissions = []

        # Owner permissions
        permissions.append("r" if mode & stat.S_IRUSR else "-")
        permissions.append("w" if mode & stat.S_IWUSR else "-")
        permissions.append("x" if mode & stat.S_IXUSR else "-")

        # Group permissions
        permissions.append("r" if mode & stat.S_IRGRP else "-")
        permissions.append("w" if mode & stat.S_IWGRP else "-")
        permissions.append("x" if mode & stat.S_IXGRP else "-")

        # Other permissions
        permissions.append("r" if mode & stat.S_IROTH else "-")
        permissions.append("w" if mode & stat.S_IWOTH else "-")
        permissions.append("x" if mode & stat.S_IXOTH else "-")

        return "".join(permissions)

    @staticmethod
    def _get_owner(path: Path) -> str:
        """Get file owner (Unix-like systems)."""
        try:
            if hasattr(os, "getpwuid"):
                import pwd

                return pwd.getpwuid(path.stat().st_uid).pw_name
        except (ImportError, KeyError, OSError):
            pass
        return "unknown"

    @staticmethod
    def _get_group(path: Path) -> str:
        """Get file group (Unix-like systems)."""
        try:
            if hasattr(os, "getgrgid"):
                import grp

                return grp.getgrgid(path.stat().st_gid).gr_name
        except (ImportError, KeyError, OSError):
            pass
        return "unknown"

    @staticmethod
    def _detect_mime_type(path: Path) -> str:
        """Detect MIME type using multiple methods."""
        if not path.is_file():
            return "inode/directory"

        # Try python-magic first (most accurate)
        if PYTHON_MAGIC_AVAILABLE:
            try:
                import magic as magic_lib

                mime = magic_lib.Magic(mime=True)
                return mime.from_file(str(path))
            except Exception:
                pass

        # Fallback to mimetypes module
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type or "application/octet-stream"

    @staticmethod
    def _detect_encoding(path: Path) -> Optional[str]:
        """Detect text file encoding."""
        if not path.is_file() or path.stat().st_size == 0:
            return None

        try:
            # Read first few KB to detect encoding
            with open(path, "rb") as f:
                raw_data = f.read(8192)

            if not raw_data:
                return None

            # Try chardet if available
            try:
                import chardet

                result = chardet.detect(raw_data)
                if result and result.get("confidence", 0) > 0.7:
                    return result.get("encoding")
            except (ImportError, AttributeError):
                pass

            # Simple UTF-8 detection
            try:
                raw_data.decode("utf-8")
                return "utf-8"
            except UnicodeDecodeError:
                pass

            # Try common encodings
            for encoding in ["ascii", "latin-1", "cp1252"]:
                try:
                    raw_data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue

            return "binary"

        except Exception:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert FileInfo to dictionary."""
        return {
            "path": self.path,
            "name": self.name,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_bytes / (1024 * 1024), 2),
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
            "accessed_time": self.accessed_time.isoformat(),
            "is_file": self.is_file,
            "is_directory": self.is_directory,
            "is_symlink": self.is_symlink,
            "is_hidden": self.is_hidden,
            "is_system": self.is_system,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group,
            "readable": self.readable,
            "writable": self.writable,
            "executable": self.executable,
            "mime_type": self.mime_type,
            "encoding": self.encoding,
            "path_hash": self.path_hash,
            "relative_path": self.relative_path,
            "depth": self.depth,
        }


class FileSystemScanner:
    """
    Enterprise-grade file system scanner with concurrent processing.

    Provides comprehensive file system scanning capabilities including:
    - Multi-threaded concurrent processing
    - Symbolic link detection and handling
    - Permission validation and access control
    - Memory-efficient scanning for large directories
    - Real-time progress reporting and cancellation
    - Comprehensive error handling and recovery
    """

    def __init__(
        self,
        max_workers: int = 4,
        batch_size: int = 1000,
        memory_limit_mb: int = 500,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        error_callback: Optional[Callable[[Exception, str], None]] = None,
    ):
        """
        Initialize file system scanner.

        Args:
            max_workers: Maximum number of worker threads
            batch_size: Number of files to process in each batch
            memory_limit_mb: Memory limit in MB (0 = no limit)
            progress_callback: Callback for progress reporting (current, total)
            error_callback: Callback for error reporting (error, path)
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.memory_limit_mb = memory_limit_mb
        self.progress_callback = progress_callback
        self.error_callback = error_callback

        # State management
        self._cancel_requested = threading.Event()
        self._scanning = threading.Event()
        self._lock = threading.RLock()

        # Statistics and monitoring
        self.statistics = ScanStatistics()
        self._files_processed = 0
        self._directories_queued = 0

        # Logging
        self.logger = logging.getLogger("RFU.FileSystemScanner")

        # Validation
        if self.max_workers < 1:
            raise ValidationException(
                "Maximum workers must be at least 1",
                field_name="max_workers",
                field_value=max_workers,
            )

        if self.batch_size < 1:
            raise ValidationException(
                "Batch size must be at least 1",
                field_name="batch_size",
                field_value=batch_size,
            )

    def scan_directory(
        self,
        target: DirectoryTarget,
        security_settings: Optional[SecuritySettings] = None,
        include_metadata: bool = True,
    ) -> Iterator[FileInfo]:
        """
        Scan directory with specified configuration.

        Args:
            target: Directory target configuration
            security_settings: Security settings to apply
            include_metadata: Whether to include extended metadata

        Yields:
            FileInfo objects for discovered files

        Raises:
            FileSystemException: If scanning fails
            PermissionException: If access is denied
        """
        try:
            # Validate target directory
            base_path = Path(target.path)
            if not base_path.exists():
                raise FileSystemException(
                    f"Target directory does not exist: {target.path}",
                    error_code="SCANNER_DIRECTORY_NOT_FOUND",
                    context={"path": target.path},
                )

            if not base_path.is_dir():
                raise FileSystemException(
                    f"Target path is not a directory: {target.path}",
                    error_code="SCANNER_NOT_DIRECTORY",
                    context={"path": target.path},
                )

            # Initialize scanning state
            self._cancel_requested.clear()
            self._scanning.set()
            self.statistics = ScanStatistics()
            self.statistics.start_time = datetime.now(timezone.utc)

            # Apply security settings
            security = security_settings or SecuritySettings()

            self.logger.info(f"Starting scan of directory: {target.path}")

            # Perform scan based on configuration
            if self.max_workers == 1:
                # Single-threaded scan
                yield from self._scan_single_threaded(
                    base_path, target, security, include_metadata
                )
            else:
                # Multi-threaded scan
                yield from self._scan_multi_threaded(
                    base_path, target, security, include_metadata
                )

        except Exception as e:
            self.logger.error(f"Scan failed for {target.path}: {str(e)}")
            if isinstance(e, (FileSystemException, PermissionException)):
                raise
            raise FileSystemException(
                f"Unexpected error during scan: {str(e)}",
                error_code="SCANNER_UNEXPECTED_ERROR",
                context={"path": target.path},
                cause=e,
            )
        finally:
            self._scanning.clear()
            self.statistics.finalize()
            self.logger.info(
                f"Scan completed. Statistics: {self.statistics.to_dict()}"
            )

    def _scan_single_threaded(
        self,
        base_path: Path,
        target: DirectoryTarget,
        security: SecuritySettings,
        include_metadata: bool,
    ) -> Iterator[FileInfo]:
        """Single-threaded directory scanning."""
        try:
            for file_info in self._walk_directory(
                base_path, base_path, target, security, include_metadata, 0
            ):
                if self._cancel_requested.is_set():
                    break

                # Memory monitoring
                if self.memory_limit_mb > 0:
                    self.statistics.update_memory_usage()
                    if (
                        self.statistics.current_memory_mb
                        > self.memory_limit_mb
                    ):
                        raise FileSystemException(
                            f"Memory limit exceeded: {self.statistics.current_memory_mb:.1f}MB",
                            error_code="SCANNER_MEMORY_LIMIT_EXCEEDED",
                            context={
                                "current_memory_mb": self.statistics.current_memory_mb,
                                "limit_mb": self.memory_limit_mb,
                            },
                        )

                yield file_info

                # Progress reporting
                self._files_processed += 1
                if self.progress_callback and self._files_processed % 100 == 0:
                    self.progress_callback(
                        self._files_processed, -1
                    )  # Unknown total

        except Exception as e:
            self.logger.error(f"Single-threaded scan error: {str(e)}")
            raise

    def _scan_multi_threaded(
        self,
        base_path: Path,
        target: DirectoryTarget,
        security: SecuritySettings,
        include_metadata: bool,
    ) -> Iterator[FileInfo]:
        """Multi-threaded directory scanning using ThreadPoolExecutor."""

        # Directory queue for processing
        directory_queue = Queue()
        directory_queue.put((base_path, 0))  # (path, depth)

        # Results queue
        results_queue = Queue()

        # Worker function for processing directories
        def process_directory_batch(
            directories: List[Tuple[Path, int]],
        ) -> List[FileInfo]:
            """Process a batch of directories."""
            batch_results = []

            for directory, depth in directories:
                if self._cancel_requested.is_set():
                    break

                try:
                    for file_info in self._scan_directory_contents(
                        directory,
                        base_path,
                        target,
                        security,
                        include_metadata,
                        depth,
                    ):
                        batch_results.append(file_info)

                        # Add subdirectories to queue
                        if (
                            file_info.is_directory
                            and target.include_subdirectories
                            and (
                                target.max_depth is None
                                or depth < target.max_depth
                            )
                            and self._should_process_path(
                                Path(file_info.path), target, security
                            )
                        ):

                            directory_queue.put(
                                (Path(file_info.path), depth + 1)
                            )

                except Exception as e:
                    self.logger.error(
                        f"Error processing directory {directory}: {str(e)}"
                    )
                    self.statistics.add_error(
                        "directory_processing", str(directory), str(e)
                    )
                    if self.error_callback:
                        self.error_callback(e, str(directory))

            return batch_results

        # Process directories with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            active_futures = set()

            while not directory_queue.empty() or active_futures:
                if self._cancel_requested.is_set():
                    break

                # Submit new batches if under worker limit
                while (
                    len(active_futures) < self.max_workers
                    and not directory_queue.empty()
                ):

                    # Collect batch of directories
                    batch = []
                    for _ in range(self.batch_size):
                        if directory_queue.empty():
                            break
                        batch.append(directory_queue.get())

                    if batch:
                        future = executor.submit(
                            process_directory_batch, batch
                        )
                        active_futures.add(future)

                # Process completed futures
                for future in as_completed(active_futures, timeout=0.1):
                    active_futures.remove(future)

                    try:
                        batch_results = future.result()
                        for file_info in batch_results:
                            yield file_info

                            self._files_processed += 1
                            if (
                                self.progress_callback
                                and self._files_processed % 100 == 0
                            ):
                                self.progress_callback(
                                    self._files_processed, -1
                                )

                        # Memory monitoring
                        if self.memory_limit_mb > 0:
                            self.statistics.update_memory_usage()
                            if (
                                self.statistics.current_memory_mb
                                > self.memory_limit_mb
                            ):
                                self._cancel_requested.set()
                                raise FileSystemException(
                                    f"Memory limit exceeded: {self.statistics.current_memory_mb:.1f}MB",
                                    error_code="SCANNER_MEMORY_LIMIT_EXCEEDED",
                                )

                    except Exception as e:
                        self.logger.error(f"Future processing error: {str(e)}")
                        self.statistics.add_error(
                            "future_processing", "batch", str(e)
                        )
                        if self.error_callback:
                            self.error_callback(e, "batch_processing")

                    break  # Process one future at a time

    def _walk_directory(
        self,
        directory: Path,
        base_path: Path,
        target: DirectoryTarget,
        security: SecuritySettings,
        include_metadata: bool,
        depth: int,
    ) -> Iterator[FileInfo]:
        """Recursively walk directory structure."""
        try:
            # Check if we should process this directory
            if not self._should_process_path(directory, target, security):
                return

            # Check depth limit
            if target.max_depth is not None and depth > target.max_depth:
                return

            # Scan directory contents
            yield from self._scan_directory_contents(
                directory, base_path, target, security, include_metadata, depth
            )

            # Recurse into subdirectories if enabled
            if target.include_subdirectories:
                try:
                    for item in directory.iterdir():
                        if self._cancel_requested.is_set():
                            break

                        if item.is_dir() and self._should_process_path(
                            item, target, security
                        ):
                            yield from self._walk_directory(
                                item,
                                base_path,
                                target,
                                security,
                                include_metadata,
                                depth + 1,
                            )

                except PermissionError as e:
                    self.statistics.permission_errors += 1
                    self.statistics.add_error(
                        "permission", str(directory), str(e)
                    )
                    if self.error_callback:
                        self.error_callback(e, str(directory))
                except OSError as e:
                    self.statistics.access_errors += 1
                    self.statistics.add_error("access", str(directory), str(e))
                    if self.error_callback:
                        self.error_callback(e, str(directory))

        except Exception as e:
            self.logger.error(f"Error walking directory {directory}: {str(e)}")
            self.statistics.add_error("walk", str(directory), str(e))

    def _scan_directory_contents(
        self,
        directory: Path,
        base_path: Path,
        target: DirectoryTarget,
        security: SecuritySettings,
        include_metadata: bool,
        depth: int,
    ) -> Iterator[FileInfo]:
        """Scan contents of a single directory."""
        try:
            self.statistics.directories_scanned += 1

            for item in directory.iterdir():
                if self._cancel_requested.is_set():
                    break

                try:
                    # Check if we should process this item
                    if not self._should_process_path(item, target, security):
                        continue

                    # Handle symbolic links
                    if item.is_symlink():
                        self.statistics.symlinks_found += 1
                        if not target.follow_symlinks:
                            # Create FileInfo for symlink itself
                            file_info = FileInfo.from_path(
                                item, base_path, include_metadata
                            )
                            yield file_info
                            continue

                    # Create FileInfo for the item
                    file_info = FileInfo.from_path(
                        item, base_path, include_metadata
                    )

                    # Update statistics
                    if file_info.is_file:
                        self.statistics.files_scanned += 1
                        self.statistics.total_size_bytes += (
                            file_info.size_bytes
                        )
                        self.statistics.largest_file_size = max(
                            self.statistics.largest_file_size,
                            file_info.size_bytes,
                        )

                    yield file_info

                except PermissionError as e:
                    self.statistics.permission_errors += 1
                    self.statistics.add_error("permission", str(item), str(e))
                    if self.error_callback:
                        self.error_callback(e, str(item))
                except OSError as e:
                    self.statistics.access_errors += 1
                    self.statistics.add_error("access", str(item), str(e))
                    if self.error_callback:
                        self.error_callback(e, str(item))
                except Exception as e:
                    self.statistics.add_error("processing", str(item), str(e))
                    if self.error_callback:
                        self.error_callback(e, str(item))

        except PermissionError as e:
            self.statistics.permission_errors += 1
            self.statistics.add_error(
                "directory_permission", str(directory), str(e)
            )
            if self.error_callback:
                self.error_callback(e, str(directory))
        except OSError as e:
            self.statistics.access_errors += 1
            self.statistics.add_error(
                "directory_access", str(directory), str(e)
            )
            if self.error_callback:
                self.error_callback(e, str(directory))

    def _should_process_path(
        self, path: Path, target: DirectoryTarget, security: SecuritySettings
    ) -> bool:
        """Determine if path should be processed based on configuration."""
        try:
            # Check exclude patterns
            for pattern in target.exclude_patterns:
                if path.match(pattern):
                    return False

            # Security settings checks
            if not security.include_hidden_files and self._is_hidden(path):
                return False

            if not security.include_system_files and self._is_system_file(
                path
            ):
                return False

            # Permission checks
            if security.respect_file_permissions:
                if not os.access(path, os.R_OK):
                    return False

            return True

        except Exception as e:
            self.logger.warning(f"Error checking path {path}: {str(e)}")
            return False

    def _is_hidden(self, path: Path) -> bool:
        """Check if path is hidden."""
        return FileInfo._is_hidden_file(path)

    def _is_system_file(self, path: Path) -> bool:
        """Check if path is a system file."""
        return FileInfo._is_system_file(path)

    def cancel_scan(self) -> None:
        """Cancel ongoing scan operation."""
        self.logger.info("Scan cancellation requested")
        self._cancel_requested.set()

    def is_scanning(self) -> bool:
        """Check if scan is currently in progress."""
        return self._scanning.is_set()

    def get_statistics(self) -> ScanStatistics:
        """Get current scan statistics."""
        return self.statistics

    def reset_statistics(self) -> None:
        """Reset scan statistics."""
        self.statistics = ScanStatistics()
        self._files_processed = 0
        self._directories_queued = 0


class BatchFileSystemScanner:
    """
    Batch scanner for processing multiple directory targets efficiently.

    Optimizes scanning of multiple directories by sharing thread pools
    and coordinating resource usage across targets.
    """

    def __init__(
        self,
        max_workers: int = 4,
        batch_size: int = 1000,
        memory_limit_mb: int = 500,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        error_callback: Optional[Callable[[Exception, str, str], None]] = None,
    ):
        """
        Initialize batch scanner.

        Args:
            max_workers: Maximum number of worker threads across all scans
            batch_size: Number of files to process in each batch
            memory_limit_mb: Memory limit in MB (0 = no limit)
            progress_callback: Callback for progress reporting (target_id, current, total)
            error_callback: Callback for error reporting (error, target_id, path)
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.memory_limit_mb = memory_limit_mb
        self.progress_callback = progress_callback
        self.error_callback = error_callback

        # State management
        self._cancel_requested = threading.Event()
        self._scanning = threading.Event()

        # Combined statistics
        self.combined_statistics = ScanStatistics()
        self.target_statistics: Dict[str, ScanStatistics] = {}

        # Logging
        self.logger = logging.getLogger("RFU.BatchFileSystemScanner")

    def scan_multiple_targets(
        self,
        targets: List[Tuple[str, DirectoryTarget]],  # (target_id, target)
        security_settings: Optional[SecuritySettings] = None,
        include_metadata: bool = True,
    ) -> Iterator[Tuple[str, FileInfo]]:
        """
        Scan multiple directory targets.

        Args:
            targets: List of (target_id, DirectoryTarget) tuples
            security_settings: Security settings to apply
            include_metadata: Whether to include extended metadata

        Yields:
            Tuple of (target_id, FileInfo) for discovered files
        """
        try:
            self._cancel_requested.clear()
            self._scanning.set()
            self.combined_statistics = ScanStatistics()
            self.combined_statistics.start_time = datetime.now(timezone.utc)

            # Distribute workers across targets
            workers_per_target = max(1, self.max_workers // len(targets))

            # Create scanners for each target
            scanners = {}
            for target_id, target in targets:
                scanner = FileSystemScanner(
                    max_workers=workers_per_target,
                    batch_size=self.batch_size,
                    memory_limit_mb=self.memory_limit_mb // len(targets),
                    progress_callback=lambda c, t, tid=target_id: self._target_progress(
                        tid, c, t
                    ),
                    error_callback=lambda e, p, tid=target_id: self._target_error(
                        tid, e, p
                    ),
                )
                scanners[target_id] = scanner
                self.target_statistics[target_id] = scanner.statistics

            # Use ThreadPoolExecutor to scan targets concurrently
            with ThreadPoolExecutor(max_workers=len(targets)) as executor:
                # Submit all scan tasks
                future_to_target = {}
                for target_id, target in targets:
                    scanner = scanners[target_id]
                    future = executor.submit(
                        self._scan_target_to_list,
                        scanner,
                        target,
                        security_settings,
                        include_metadata,
                    )
                    future_to_target[future] = target_id

                # Process results as they complete
                for future in as_completed(future_to_target):
                    if self._cancel_requested.is_set():
                        break

                    target_id = future_to_target[future]

                    try:
                        file_infos = future.result()
                        for file_info in file_infos:
                            yield (target_id, file_info)

                            # Update combined statistics
                            if file_info.is_file:
                                self.combined_statistics.files_scanned += 1
                                self.combined_statistics.total_size_bytes += (
                                    file_info.size_bytes
                                )
                            elif file_info.is_directory:
                                self.combined_statistics.directories_scanned += (
                                    1
                                )

                            if file_info.is_symlink:
                                self.combined_statistics.symlinks_found += 1

                    except Exception as e:
                        self.logger.error(
                            f"Error processing target {target_id}: {str(e)}"
                        )
                        if self.error_callback:
                            self.error_callback(
                                e, target_id, "target_processing"
                            )

        finally:
            self._scanning.clear()
            self.combined_statistics.finalize()

    def _scan_target_to_list(
        self,
        scanner: FileSystemScanner,
        target: DirectoryTarget,
        security_settings: Optional[SecuritySettings],
        include_metadata: bool,
    ) -> List[FileInfo]:
        """Scan single target and return results as list."""
        results = []
        for file_info in scanner.scan_directory(
            target, security_settings, include_metadata
        ):
            if self._cancel_requested.is_set():
                break
            results.append(file_info)
        return results

    def _target_progress(self, target_id: str, current: int, total: int):
        """Handle progress from individual target scanner."""
        if self.progress_callback:
            self.progress_callback(target_id, current, total)

    def _target_error(self, target_id: str, error: Exception, path: str):
        """Handle error from individual target scanner."""
        if self.error_callback:
            self.error_callback(error, target_id, path)

    def cancel_scan(self) -> None:
        """Cancel all ongoing scan operations."""
        self.logger.info("Batch scan cancellation requested")
        self._cancel_requested.set()

    def is_scanning(self) -> bool:
        """Check if any scan is currently in progress."""
        return self._scanning.is_set()

    def get_combined_statistics(self) -> ScanStatistics:
        """Get combined statistics across all targets."""
        return self.combined_statistics

    def get_target_statistics(
        self, target_id: str
    ) -> Optional[ScanStatistics]:
        """Get statistics for specific target."""
        return self.target_statistics.get(target_id)

    def get_all_target_statistics(self) -> Dict[str, ScanStatistics]:
        """Get statistics for all targets."""
        return self.target_statistics.copy()
