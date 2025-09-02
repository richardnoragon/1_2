"""
Enhanced File Splitter Logic Module

This module provides the core business logic for file splitting and joining
operations, enhanced with file_utilities_2 framework integration including
hub connectivity, shared logging, and configuration management.

Preserves all original functionality while adding:
- Hub connector integration for progress reporting
- Shared logging system integration
- Configuration management
- Enhanced error handling and reporting
- Resource usage monitoring
"""

import json
import logging
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PyQt5.QtCore import QObject, QThread, pyqtSignal

# Constants (preserved from original)
CHUNK_RW_SIZE = 1024 * 1024  # 1MB read/write buffer
METADATA_FILENAME = "_metadata.json"
PART_EXTENSION = ".part001"  # Extension for first chunk file


class FileSplitterError(Exception):
    """Base exception for file splitter operations."""
    pass


class FileSplitterValidationError(FileSplitterError):
    """Validation error in file splitter operations."""
    pass


class FileSplitterIOError(FileSplitterError):
    """I/O error in file splitter operations."""
    pass


class FileSplitterSecurityError(FileSplitterError):
    """Security validation error in file splitter operations."""
    pass


def _validate_and_sanitize_path(path: str, base_dir: Optional[str] = None, operation_type: str = "read") -> str:
    """
    Validate and sanitize file paths to prevent path traversal attacks.
    
    This function implements defense-in-depth security measures including:
    - Path normalization and canonicalization
    - Directory traversal pattern detection
    - Boundary enforcement within safe directories
    - OWASP A03 (Injection) compliance
    
    Args:
        path: The file path to validate
        base_dir: Optional base directory for boundary checking
        operation_type: Type of operation ('read', 'write', 'create')
    
    Returns:
        Validated and sanitized absolute path
        
    Raises:
        FileSplitterSecurityError: If path fails security validation
    """
    if not path or not isinstance(path, str):
        raise FileSplitterSecurityError("Invalid path: path must be a non-empty string")
    
    # Log security-relevant path operations
    logger = logging.getLogger('file_splitter.security')
    logger.debug(f"Validating path for {operation_type}: {path}")
    
    # Phase 1: Detect obvious traversal patterns
    dangerous_patterns = [
        '../', '..\\',
        '/../', '\\..\\',
        '%2e%2e%2f', '%2e%2e%5c',  # URL encoded
        '..%2f', '..%5c',
        '....///', '....\\\\\\',  # Double encoding attempts
    ]
    
    # Decode URL encoded patterns for detection
    import urllib.parse
    try:
        decoded_path = urllib.parse.unquote(path)
        paths_to_check = [path.lower(), decoded_path.lower()]
    except:
        paths_to_check = [path.lower()]
    
    for check_path in paths_to_check:
        for pattern in dangerous_patterns:
            if pattern in check_path:
                logger.warning(f"Path traversal attempt detected: {path}")
                raise FileSplitterSecurityError(f"Path contains suspicious traversal pattern: {pattern}")
    
    # Phase 2: Normalize and canonicalize path
    try:
        # Convert to Path object for proper handling
        path_obj = Path(path)
        
        # Resolve to absolute path and follow symlinks
        normalized_path = path_obj.resolve()
        
        # Convert back to string for further processing
        canonical_path = str(normalized_path)
        
    except (OSError, ValueError) as e:
        raise FileSplitterSecurityError(f"Path normalization failed: {e}")
    
    # Phase 3: Boundary enforcement
    if base_dir:
        try:
            base_canonical = str(Path(base_dir).resolve())
            
            # Ensure the canonical path stays within the base directory
            if not canonical_path.startswith(base_canonical):
                logger.warning(f"Path outside boundary detected: {canonical_path} not in {base_canonical}")
                raise FileSplitterSecurityError(
                    f"Path outside allowed directory boundary: {canonical_path}"
                )
        except (OSError, ValueError) as e:
            raise FileSplitterSecurityError(f"Base directory validation failed: {e}")
    
    # Phase 4: Additional security checks
    if operation_type == "write":
        # Prevent writing to absolute paths outside allowed areas
        if os.path.isabs(path) and not base_dir:
            # Check if absolute path points to sensitive areas
            sensitive_roots = ["/etc", "/sys", "/proc", "/dev", "/boot", "/usr", "/var",
                              "/System", "/Applications", "/Library"]
            drive_roots = ["C:\\", "D:\\", "E:\\"]  # Windows drive roots
            
            path_upper = canonical_path.upper()
            for root in drive_roots:
                if path_upper.startswith(root.upper()):
                    # Only allow in temp or user directories
                    allowed_paths = [
                        tempfile.gettempdir().upper(),
                        os.path.expanduser("~").upper(),
                        "C:\\TEMP", "C:\\TMP"
                    ]
                    is_allowed = any(path_upper.startswith(allowed) for allowed in allowed_paths)
                    if not is_allowed:
                        logger.warning(f"Absolute path write blocked: {canonical_path}")
                        raise FileSplitterSecurityError(
                            f"Absolute path write not allowed: {canonical_path}"
                        )
        
        # Prevent writing to system directories
        system_dirs = [
            "/etc", "/sys", "/proc", "/dev", "/boot", "/usr/bin", "/usr/sbin",
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "/System", "/Applications", "/Library"
        ]
        
        for sys_dir in system_dirs:
            try:
                sys_canonical = str(Path(sys_dir).resolve()) if os.path.exists(sys_dir) else sys_dir
                if canonical_path.startswith(sys_canonical):
                    logger.warning(f"Attempted write to system directory: {canonical_path}")
                    raise FileSplitterSecurityError(
                        f"Write operation to system directory not allowed: {sys_dir}"
                    )
            except (OSError, ValueError):
                continue  # Skip if system directory doesn't exist
    
    logger.debug(f"Path validation successful: {canonical_path}")
    return canonical_path


def _is_safe_path(path: str, allowed_base: str) -> bool:
    """
    Check if a path is safe within the allowed base directory.
    
    Args:
        path: The path to check
        allowed_base: The allowed base directory
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        canonical_path = str(Path(path).resolve())
        canonical_base = str(Path(allowed_base).resolve())
        return canonical_path.startswith(canonical_base)
    except (OSError, ValueError):
        return False


def _create_secure_temp_dir() -> str:
    """
    Create a secure temporary directory for file operations.
    
    Returns:
        Path to secure temporary directory
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix="file_splitter_", suffix="_secure")
        os.chmod(temp_dir, 0o700)  # Owner read/write/execute only
        return temp_dir
    except OSError as e:
        raise FileSplitterSecurityError(f"Failed to create secure temporary directory: {e}")


class FileSplitterLogic(QObject):
    """
    Enhanced core logic for file splitting and joining operations.
    
    Integrates with file_utilities_2 framework while preserving all original
    functionality. Adds hub connectivity, shared logging, and enhanced
    error handling.
    """
    
    # Signals for UI communication (preserved from original)
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(str)  # success message
    error_occurred = pyqtSignal(str)  # error message
    finished = pyqtSignal()  # operation finished
    
    def __init__(self, config_manager=None, logger=None):
        """
        Initialize the FileSplitterLogic.
        
        Args:
            config_manager: Configuration manager instance (optional)
            logger: Logger instance (optional)
        """
        super().__init__()
        
        # Configuration and logging
        self.config = config_manager or self._get_default_config()
        self.logger = logger or self._setup_logger()
        
        # Hub integration
        self.hub_connector = None
        
        # Operation state
        self._is_running = False
        
        # Enhanced operation statistics
        self.operation_stats = {
            'start_time': None,
            'end_time': None,
            'bytes_processed': 0,
            'chunks_processed': 0,
            'errors_count': 0,
            'operation_type': None,
            'input_file_size': 0,
            'output_files_count': 0
        }
        
        self.logger.info("FileSplitterLogic initialized with file_utilities_2 integration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'default_chunk_size': 1024 * 1024,  # 1MB
            'max_chunks': 9999,
            'buffer_size': CHUNK_RW_SIZE,
            'verify_integrity': True,
            'enable_hub_reporting': True,
            'auto_cleanup_on_error': True
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger."""
        logger = logging.getLogger('file_splitter')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def set_hub_connector(self, connector):
        """
        Set hub connector for progress reporting.
        
        Args:
            connector: HubConnector instance
        """
        self.hub_connector = connector
        if connector:
            self.logger.info("Hub connector attached to file splitter logic")
    
    def stop(self) -> None:
        """Stop the current operation."""
        self.logger.info("Stop operation requested")
        self.progress_updated.emit(0, 1, "Stopping operation...")
        self._is_running = False
        
        if self.hub_connector:
            self.hub_connector.report_status_to_hub(
                "stopped", 
                {"stop_time": datetime.now().isoformat()}
            )
    
    def _report_progress_to_hub(self, current: int, total: int, message: str):
        """
        Report progress to hub with enhanced details.
        
        Args:
            current: Current progress value
            total: Total progress value
            message: Progress message
        """
        if self.hub_connector and self.config.get('enable_hub_reporting', True):
            percentage = int((current / total) * 100) if total > 0 else 0
            
            self.hub_connector.report_progress_to_hub(
                percentage, 
                f"File Splitter: {message}"
            )
            
            # Report detailed status
            self.hub_connector.report_status_to_hub(
                "processing",
                {
                    'current_item': current,
                    'total_items': total,
                    'operation': message,
                    'bytes_processed': self.operation_stats['bytes_processed'],
                    'chunks_processed': self.operation_stats['chunks_processed'],
                    'start_time': self.operation_stats['start_time'],
                    'operation_type': self.operation_stats['operation_type']
                }
            )
    
    def _report_error_to_hub(self, error_message: str, error_details: Optional[Dict[str, Any]] = None):
        """
        Report error to hub.
        
        Args:
            error_message: Error message
            error_details: Additional error details
        """
        if self.hub_connector:
            self.hub_connector.report_error_to_hub(error_message, error_details)
        
        self.operation_stats['errors_count'] += 1
        self.logger.error(f"File splitter error: {error_message}")
    
    def _calculate_split_params(
        self, file_size: int, split_mode: str, value: float,
        unit_multiplier: int = 1
    ) -> Tuple[int, int]:
        """
        Calculate chunk size and number of chunks based on user input.
        
        Args:
            file_size: The total size of the file to be split
            split_mode: Either 'size' or 'parts'
            value: The size value or the number of parts
            unit_multiplier: Multiplier for size units (e.g., 1024 for KB)
        
        Returns:
            A tuple containing (chunk_size, num_chunks)
        
        Raises:
            FileSplitterValidationError: If input parameters are invalid
        """
        if file_size == 0:
            return 0, 0  # No chunks needed for an empty file
        
        try:
            if split_mode == 'size':
                chunk_size = int(value * unit_multiplier)
                if chunk_size <= 0:
                    raise FileSplitterValidationError("Chunk size must be positive.")
                
                # If chunk size >= file size, create only one chunk
                if chunk_size >= file_size:
                    num_chunks = 1
                    chunk_size = file_size
                else:
                    num_chunks = math.ceil(file_size / chunk_size)
                    
            elif split_mode == 'parts':
                num_chunks = int(value)
                if num_chunks <= 0:
                    raise FileSplitterValidationError("Number of parts must be positive.")
                
                # Calculate chunk size, ensure last chunk handles remainder
                chunk_size = math.ceil(file_size / num_chunks)
            else:
                raise FileSplitterValidationError(f"Invalid split mode: {split_mode}")
            
            # Check maximum chunks limit
            max_chunks = self.config.get('max_chunks', 9999)
            if num_chunks > max_chunks:
                raise FileSplitterValidationError(
                    f"Too many chunks requested (max {max_chunks})."
                )
            
            return chunk_size, num_chunks
            
        except (ValueError, TypeError) as e:
            raise FileSplitterValidationError(f"Invalid parameters: {e}") from e
    
    def split_file(
        self, input_filepath: str, output_dir: str, split_mode: str,
        value: float, unit_multiplier: int = 1
    ) -> None:
        """
        Split the input file into smaller chunks based on specified mode.
        
        Enhanced version with hub integration and improved error handling.
        
        Args:
            input_filepath: Path to the file to be split
            output_dir: Directory where chunks will be saved
            split_mode: Either 'size' or 'parts'
            value: The size value or the number of parts
            unit_multiplier: Multiplier for size units
        """
        self._is_running = True
        self.operation_stats.update({
            'start_time': datetime.now().isoformat(),
            'operation_type': 'split',
            'bytes_processed': 0,
            'chunks_processed': 0,
            'errors_count': 0
        })
        
        try:
            self.logger.info(f"Starting file split operation: {input_filepath}")
            
            # SECURITY: Validate input file path
            try:
                validated_input = _validate_and_sanitize_path(input_filepath, operation_type="read")
            except FileSplitterSecurityError as e:
                raise FileSplitterIOError(f"Input file path validation failed: {e}") from e
            
            if not os.path.exists(validated_input):
                raise FileSplitterIOError(f"Input file not found: {validated_input}")
            
            # SECURITY: Validate and sanitize output directory
            try:
                validated_output_dir = _validate_and_sanitize_path(output_dir, operation_type="write")
            except FileSplitterSecurityError as e:
                raise FileSplitterIOError(f"Output directory path validation failed: {e}") from e
            
            # Ensure output directory exists or can be created
            try:
                if not os.path.exists(validated_output_dir):
                    os.makedirs(validated_output_dir, mode=0o755)  # Secure permissions
            except OSError as e:
                raise FileSplitterIOError(f"Cannot create output directory: {e}") from e
            
            # Use validated paths for the rest of the operation
            input_filepath = validated_input
            output_dir = validated_output_dir
            
            file_size = os.path.getsize(input_filepath)
            self.operation_stats['input_file_size'] = file_size
            base_filename = os.path.basename(input_filepath)
            
            # Report operation start to hub
            if self.hub_connector:
                self.hub_connector.report_status_to_hub(
                    "started",
                    {
                        'operation': 'split_file',
                        'input_file': input_filepath,
                        'output_dir': output_dir,
                        'split_mode': split_mode,
                        'value': value,
                        'file_size': file_size
                    }
                )
            
            # Handle empty file
            if file_size == 0:
                self.operation_complete.emit(
                    "Input file is empty. No chunks created."
                )
                self._is_running = False
                self.finished.emit()
                return
            
            # Calculate parameters
            chunk_size, num_chunks = self._calculate_split_params(
                file_size, split_mode, value, unit_multiplier
            )
            
            if num_chunks == 0:
                self.operation_complete.emit(
                    "No chunks needed (likely zero-byte file)."
                )
                self._is_running = False
                self.finished.emit()
                return
            
            # Determine padding length
            padding = max(3, len(str(num_chunks)))
            chunk_pattern = f"{base_filename}.part{{:0{padding}d}}"
            
            progress_msg = (
                f"Starting split: {num_chunks} chunks, "
                f"approx size {chunk_size} bytes..."
            )
            self.progress_updated.emit(0, num_chunks, progress_msg)
            self._report_progress_to_hub(0, num_chunks, progress_msg)
            
            # Perform splitting
            bytes_written_total = 0
            chunks_created = 0
            
            with open(input_filepath, 'rb') as infile:
                for i in range(num_chunks):
                    if not self._is_running:
                        break
                    
                    chunk_num = i + 1
                    chunk_filename = chunk_pattern.format(chunk_num)
                    
                    # SECURITY: Validate chunk file path to prevent path traversal
                    chunk_filepath = os.path.join(output_dir, chunk_filename)
                    try:
                        validated_chunk_path = _validate_and_sanitize_path(
                            chunk_filepath, base_dir=output_dir, operation_type="write"
                        )
                        chunk_filepath = validated_chunk_path
                    except FileSplitterSecurityError as e:
                        error_msg = f"Chunk file path validation failed: {e}"
                        self._report_error_to_hub(error_msg, {
                            'chunk_file': chunk_filepath,
                            'security_error': str(e)
                        })
                        raise FileSplitterIOError(error_msg) from e
                    
                    progress_msg = (
                        f"Writing chunk {chunk_num}/{num_chunks}: "
                        f"{chunk_filename}"
                    )
                    self.progress_updated.emit(
                        chunks_created, num_chunks, progress_msg
                    )
                    self._report_progress_to_hub(
                        chunks_created, num_chunks, progress_msg
                    )
                    
                    bytes_written_this_chunk = 0
                    try:
                        with open(chunk_filepath, 'wb') as outfile:
                            # Read and write in smaller blocks
                            buffer_size = self.config.get('buffer_size', CHUNK_RW_SIZE)
                            while bytes_written_this_chunk < chunk_size:
                                if not self._is_running:
                                    break
                                
                                # Calculate remaining for this chunk
                                this_chunk = (
                                    chunk_size - bytes_written_this_chunk
                                )
                                total = (
                                    file_size - bytes_written_total
                                )
                                
                                # Determine read size
                                read_size = min(
                                    buffer_size,
                                    this_chunk,
                                    total
                                )
                                
                                if read_size <= 0:
                                    break  # No more data or chunk is full
                                
                                data = infile.read(read_size)
                                if not data:
                                    break  # End of input file
                                
                                outfile.write(data)
                                bytes_written_this_chunk += len(data)
                                bytes_written_total += len(data)
                                self.operation_stats['bytes_processed'] = bytes_written_total
                    
                    except OSError as write_error:
                        # Clean up partial chunk on error
                        if os.path.exists(chunk_filepath):
                            try:
                                os.remove(chunk_filepath)
                            except OSError:
                                pass  # Ignore cleanup errors
                        
                        error_msg = f"Error writing chunk {chunk_filename}: {write_error}"
                        self._report_error_to_hub(error_msg, {
                            'chunk_file': chunk_filepath,
                            'bytes_written': bytes_written_this_chunk
                        })
                        raise FileSplitterIOError(error_msg) from write_error
                    
                    if not self._is_running:
                        # Clean up chunk if cancelled
                        if os.path.exists(chunk_filepath):
                            try:
                                os.remove(chunk_filepath)
                            except OSError:
                                pass  # Ignore cleanup error
                        break
                    
                    chunks_created += 1
                    self.operation_stats['chunks_processed'] = chunks_created
                    
                    # Emit progress after chunk write
                    msg = f"Finished chunk {chunk_num}/{num_chunks}"
                    self.progress_updated.emit(
                        chunks_created, num_chunks, msg
                    )
                    self._report_progress_to_hub(
                        chunks_created, num_chunks, msg
                    )
            
            # Finalization
            if not self._is_running:
                self.error_occurred.emit("Split operation cancelled.")
                self._report_error_to_hub("Split operation cancelled by user")
            else:
                # Create metadata file
                metadata: Dict[str, Any] = {
                    'original_filename': base_filename,
                    'total_size': file_size,
                    'num_chunks': num_chunks,
                    'chunk_size': chunk_size,
                    'chunk_pattern': chunk_pattern,
                    'padding': padding,
                    'created_timestamp': datetime.now().isoformat(),
                    'splitter_version': '2.0_file_utilities_2'
                }
                
                meta_filepath = os.path.join(output_dir, METADATA_FILENAME)
                try:
                    with open(meta_filepath, 'w') as metafile:
                        json.dump(metadata, metafile, indent=4)
                except Exception as e:
                    # Warning only, split succeeded
                    warn_msg = f"Warning: Could not write metadata file: {e}"
                    self.error_occurred.emit(warn_msg)
                    self.logger.warning(warn_msg)
                
                complete_msg = (
                    f"File successfully split into {chunks_created} "
                    f"chunks in {output_dir}."
                )
                self.operation_complete.emit(complete_msg)
                
                # Report completion to hub
                if self.hub_connector:
                    self.hub_connector.report_status_to_hub(
                        "completed",
                        {
                            'chunks_created': chunks_created,
                            'bytes_processed': bytes_written_total,
                            'output_directory': output_dir,
                            'completion_time': datetime.now().isoformat()
                        }
                    )
                
                self.operation_stats['output_files_count'] = chunks_created
                self.logger.info(f"Split operation completed: {chunks_created} chunks created")
        
        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"An unexpected error occurred during split: {e}"
            self.error_occurred.emit(error_msg)
            self._report_error_to_hub(error_msg, {
                'exception_type': type(e).__name__,
                'input_file': input_filepath,
                'output_dir': output_dir
            })
            
        finally:
            # Reset state and emit completion signal
            self.operation_stats['end_time'] = datetime.now().isoformat()
            self._is_running = False
            self.finished.emit()
    
    def join_files(
        self,
        first_chunk_path: str,
        output_filepath: str
    ) -> None:
        """
        Join file chunks back into a single file.
        
        Enhanced version with hub integration and improved error handling.
        
        Args:
            first_chunk_path: Path to first chunk (e.g., file.part001)
            output_filepath: Path where joined file will be saved
        """
        self._is_running = True
        self.operation_stats.update({
            'start_time': datetime.now().isoformat(),
            'operation_type': 'join',
            'bytes_processed': 0,
            'chunks_processed': 0,
            'errors_count': 0
        })
        
        try:
            self.logger.info(f"Starting file join operation: {first_chunk_path}")
            
            # SECURITY: Validate first chunk path
            try:
                validated_chunk_path = _validate_and_sanitize_path(first_chunk_path, operation_type="read")
            except FileSplitterSecurityError as e:
                raise FileSplitterIOError(f"First chunk path validation failed: {e}") from e
            
            if not os.path.exists(validated_chunk_path):
                raise FileSplitterIOError(f"Input file not found: {validated_chunk_path}")
            
            # SECURITY: Validate output file path
            try:
                validated_output_path = _validate_and_sanitize_path(output_filepath, operation_type="write")
            except FileSplitterSecurityError as e:
                raise FileSplitterIOError(f"Output file path validation failed: {e}") from e
            
            # Ensure output directory exists
            output_dir = os.path.dirname(validated_output_path)
            if output_dir:
                try:
                    # SECURITY: Validate output directory path
                    validated_output_dir = _validate_and_sanitize_path(output_dir, operation_type="write")
                    os.makedirs(validated_output_dir, mode=0o755, exist_ok=True)
                except OSError as e:
                    raise FileSplitterIOError(f"Cannot create output directory: {e}") from e
                except FileSplitterSecurityError as e:
                    raise FileSplitterIOError(f"Output directory validation failed: {e}") from e
            
            # Use validated paths for the rest of the operation
            first_chunk_path = validated_chunk_path
            output_filepath = validated_output_path
            
            chunk_dir = os.path.dirname(first_chunk_path)
            chunk_basename = os.path.basename(first_chunk_path)
            
            # Report operation start to hub
            if self.hub_connector:
                self.hub_connector.report_status_to_hub(
                    "started",
                    {
                        'operation': 'join_files',
                        'first_chunk': first_chunk_path,
                        'output_file': output_filepath
                    }
                )
            
            # Load or infer parameters
            metadata: Optional[Dict[str, Any]] = None
            num_chunks = 0
            chunk_pattern = ""
            padding = 0
            expected_total_size: Optional[int] = None
            original_filename: Optional[str] = None
            
            meta_filepath = os.path.join(chunk_dir, METADATA_FILENAME)
            if os.path.exists(meta_filepath):
                try:
                    with open(meta_filepath, 'r') as f:
                        metadata = json.load(f)
                    if metadata is not None:
                        num_chunks = metadata['num_chunks']
                        chunk_pattern = metadata['chunk_pattern']
                        padding = metadata['padding']
                        expected_total_size = metadata.get('total_size')
                        original_filename = metadata.get('original_filename')
                        self.progress_updated.emit(
                            0, 1, f"Loaded metadata for '{original_filename or 'file'}'"
                        )
                        self.logger.info(f"Loaded metadata: {num_chunks} chunks expected")
                except (json.JSONDecodeError, KeyError) as e:
                    self.progress_updated.emit(
                        0, 1, f"Warning: Metadata file invalid ({e}), "
                        "attempting manual join."
                    )
                    self.logger.warning(f"Invalid metadata file: {e}")
                    metadata = None
            else:
                self.progress_updated.emit(
                    0, 1, "Metadata file not found, attempting manual join."
                )
                self.logger.info("No metadata file found, using manual detection")
            
            # Infer parameters if metadata failed/missing
            if not metadata:
                # Infer from first chunk name (e.g., file.part001)
                parts = chunk_basename.rsplit('.part', 1)
                if len(parts) != 2 or not parts[1].isdigit():
                    raise FileSplitterValidationError(
                        "Cannot infer chunk sequence from filename. "
                        "Expected format like 'filename.partXXX'."
                    )
                
                base_filename_inferred = parts[0]
                padding = len(parts[1])
                
                # Ensure first part number matches inference logic (should be 1)
                try:
                    if int(parts[1]) != 1:
                        raise FileSplitterValidationError(
                            f"Expected first chunk number to be 1, "
                            f"found {int(parts[1])} in '{chunk_basename}'."
                        )
                except ValueError as e:
                    raise FileSplitterValidationError(
                        "Chunk number suffix is not a valid integer."
                    ) from e
                
                chunk_pattern = f"{base_filename_inferred}.part{{:0{padding}d}}"
                
                # Count chunks manually
                num_chunks = 0
                for i in range(1, 10000):  # Check up to 9999 chunks
                    check_path = os.path.join(chunk_dir, chunk_pattern.format(i))
                    if os.path.exists(check_path):
                        num_chunks += 1
                    else:
                        break
                
                if num_chunks == 0:
                    raise FileSplitterValidationError(
                        "Could not find any valid sequential chunks to join "
                        "starting from the provided file."
                    )
                
                expected_total_size = None
                original_filename = base_filename_inferred
                self.progress_updated.emit(
                    0, num_chunks, f"Found {num_chunks} potential chunks based on pattern."
                )
                self.logger.info(f"Detected {num_chunks} chunks using pattern matching")
            
            # Prepare output
            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except OSError as e:
                    raise FileSplitterIOError(
                        f"Could not create output directory '{output_dir}': {e}"
                    ) from e
            
            # Perform joining
            self.progress_updated.emit(
                0, num_chunks, f"Starting join operation for {num_chunks} chunks..."
            )
            self._report_progress_to_hub(
                0, num_chunks, f"Starting join operation for {num_chunks} chunks..."
            )
            
            chunks_processed = 0
            total_bytes_written = 0
            
            try:
                with open(output_filepath, 'wb') as outfile:
                    for i in range(num_chunks):
                        if not self._is_running:
                            break
                        
                        chunk_num = i + 1
                        chunk_filename = chunk_pattern.format(chunk_num)
                        chunk_filepath = os.path.join(chunk_dir, chunk_filename)
                        
                        # SECURITY: Validate chunk file path to prevent path traversal
                        try:
                            validated_chunk_path = _validate_and_sanitize_path(
                                chunk_filepath, base_dir=chunk_dir, operation_type="read"
                            )
                            chunk_filepath = validated_chunk_path
                        except FileSplitterSecurityError as e:
                            error_msg = f"Chunk file path validation failed: {e}"
                            self._report_error_to_hub(error_msg, {
                                'chunk_file': chunk_filepath,
                                'security_error': str(e)
                            })
                            raise FileSplitterIOError(error_msg) from e
                        
                        if not os.path.exists(chunk_filepath):
                            raise FileSplitterIOError(
                                f"Missing chunk required for join: {chunk_filename}"
                            )
                        
                        self.progress_updated.emit(
                            chunks_processed, num_chunks,
                            f"Reading chunk {chunk_num}/{num_chunks}: {chunk_filename}"
                        )
                        self._report_progress_to_hub(
                            chunks_processed, num_chunks,
                            f"Processing chunk {chunk_num}/{num_chunks}"
                        )
                        
                        try:
                            with open(chunk_filepath, 'rb') as infile:
                                buffer_size = self.config.get('buffer_size', CHUNK_RW_SIZE)
                                while self._is_running:
                                    data = infile.read(buffer_size)
                                    if not data:
                                        break
                                    outfile.write(data)
                                    total_bytes_written += len(data)
                                    self.operation_stats['bytes_processed'] = total_bytes_written
                        except IOError as read_error:
                            raise FileSplitterIOError(
                                f"Error reading chunk {chunk_filename}: {read_error}"
                            ) from read_error
                        except Exception as e:
                            raise FileSplitterIOError(
                                f"Unexpected error processing chunk {chunk_filename}: {e}"
                            ) from e
                        
                        if not self._is_running:
                            break
                        
                        chunks_processed += 1
                        self.operation_stats['chunks_processed'] = chunks_processed
                        self.progress_updated.emit(
                            chunks_processed, num_chunks,
                            f"Finished processing chunk {chunk_num}/{num_chunks}"
                        )
                        self._report_progress_to_hub(
                            chunks_processed, num_chunks,
                            f"Completed chunk {chunk_num}/{num_chunks}"
                        )
            
            except OSError as write_error:
                # Clean up the partially written output file on write error
                if os.path.exists(output_filepath):
                    try:
                        os.remove(output_filepath)
                    except OSError:
                        pass
                raise FileSplitterIOError(
                    f"Error writing to output file '{output_filepath}': {write_error}"
                ) from write_error
            
            # Finalization
            if not self._is_running:
                # Clean up partially written output file if cancelled
                if os.path.exists(output_filepath):
                    try:
                        os.remove(output_filepath)
                    except OSError:
                        pass
                self.error_occurred.emit("Join operation cancelled.")
                self._report_error_to_hub("Join operation cancelled by user")
            else:
                # Final verification
                try:
                    final_size = os.path.getsize(output_filepath)
                except OSError:
                    final_size = -1
                
                verification_msg = ""
                if expected_total_size is not None and final_size >= 0:
                    if final_size == expected_total_size:
                        verification_msg = (
                            f" Final size ({final_size} bytes) matches expected size."
                        )
                        self.logger.info("File size verification passed")
                    else:
                        verification_msg = (
                            f" WARNING: Final size ({final_size} bytes) does NOT "
                            f"match expected size ({expected_total_size} bytes)!"
                        )
                        self.logger.warning("File size verification failed")
                
                complete_msg = (
                    f"File successfully joined to '{output_filepath}'. "
                    f"Processed {chunks_processed} chunks.{verification_msg}"
                )
                self.operation_complete.emit(complete_msg)
                
                # Report completion to hub
                if self.hub_connector:
                    self.hub_connector.report_status_to_hub(
                        "completed",
                        {
                            'chunks_processed': chunks_processed,
                            'bytes_processed': total_bytes_written,
                            'output_file': output_filepath,
                            'final_size': final_size,
                            'size_verification': final_size == expected_total_size if expected_total_size else None,
                            'completion_time': datetime.now().isoformat()
                        }
                    )
                
                self.operation_stats['output_files_count'] = 1
                self.logger.info(f"Join operation completed: {output_filepath}")
        
        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"An unexpected error occurred during join: {e}"
            self.error_occurred.emit(error_msg)
            self._report_error_to_hub(error_msg, {
                'exception_type': type(e).__name__,
                'first_chunk': first_chunk_path,
                'output_file': output_filepath
            })
            
        finally:
            # Reset state and emit completion signal
            self.operation_stats['end_time'] = datetime.now().isoformat()
            self._is_running = False
            self.finished.emit()


class FileSplitterWorkerThread(QThread):
    """
    Enhanced worker thread for file operations to prevent UI blocking.
    
    Integrates with file_utilities_2 patterns and provides better resource
    management and error handling.
    """
    
    def __init__(self, operation_logic, operation_type, *args):
        """
        Initialize worker thread.
        
        Args:
            operation_logic: FileSplitterLogic instance
            operation_type: 'split' or 'join'
            *args: Arguments for the operation
        """
        super().__init__()
        self.operation_logic = operation_logic
        self.operation_type = operation_type
        self.args = args
        self.logger = logging.getLogger('file_splitter.worker')
    
    def run(self):
        """Run the operation in the thread."""
        try:
            self.logger.info(f"Starting {self.operation_type} operation in worker thread")
            
            if self.operation_type == 'split':
                self.operation_logic.split_file(*self.args)
            elif self.operation_type == 'join':
                self.operation_logic.join_files(*self.args)
            else:
                self.logger.error(f"Unknown operation type: {self.operation_type}")
                
        except Exception as e:
            self.logger.error(f"Worker thread error: {e}")
            # Error will be handled by the operation_logic
        finally:
            self.logger.info(f"Worker thread completed: {self.operation_type}")