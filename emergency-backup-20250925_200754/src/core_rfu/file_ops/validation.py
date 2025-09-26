"""File operation validation utilities."""

import os
from pathlib import Path
from typing import Union, List, Optional

from src.core.error_handler import error_handler


class FileValidationError(Exception):
    """Custom exception for file validation errors."""

    pass


def validate_file_exists(path: Union[str, Path], throw: bool = True) -> bool:
    """
    Validate that a file exists.

    Args:
        path: Path to the file
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if file exists, False otherwise

    Raises:
        FileValidationError: If file doesn't exist and throw=True
    """
    path = Path(path)
    exists = path.is_file()
    if not exists and throw:
        raise FileValidationError(f"File does not exist: {path}")
    return exists


def validate_dir_exists(path: Union[str, Path], throw: bool = True) -> bool:
    """
    Validate that a directory exists.

    Args:
        path: Path to the directory
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if directory exists, False otherwise

    Raises:
        FileValidationError: If directory doesn't exist and throw=True
    """
    path = Path(path)
    exists = path.is_dir()
    if not exists and throw:
        raise FileValidationError(f"Directory does not exist: {path}")
    return exists


def validate_path_writeable(
    path: Union[str, Path], throw: bool = True
) -> bool:
    """
    Validate that a path is writeable.

    Args:
        path: Path to check
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if path is writeable, False otherwise

    Raises:
        FileValidationError: If path isn't writeable and throw=True
    """
    path = Path(path)
    if path.exists():
        writeable = os.access(path, os.W_OK)
    else:
        # Check if parent directory is writeable
        writeable = os.access(path.parent, os.W_OK)

    if not writeable and throw:
        raise FileValidationError(f"Path is not writeable: {path}")
    return writeable


def validate_path_readable(path: Union[str, Path], throw: bool = True) -> bool:
    """
    Validate that a path is readable.

    Args:
        path: Path to check
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if path is readable, False otherwise

    Raises:
        FileValidationError: If path isn't readable and throw=True
    """
    path = Path(path)
    readable = os.access(path, os.R_OK)
    if not readable and throw:
        raise FileValidationError(f"Path is not readable: {path}")
    return readable


def validate_path_executable(
    path: Union[str, Path], throw: bool = True
) -> bool:
    """
    Validate that a path is executable.

    Args:
        path: Path to check
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if path is executable, False otherwise

    Raises:
        FileValidationError: If path isn't executable and throw=True
    """
    path = Path(path)
    executable = os.access(path, os.X_OK)
    if not executable and throw:
        raise FileValidationError(f"Path is not executable: {path}")
    return executable


def validate_file_extension(
    path: Union[str, Path], allowed_extensions: List[str], throw: bool = True
) -> bool:
    """
    Validate that a file has an allowed extension.

    Args:
        path: Path to the file
        allowed_extensions: List of allowed extensions (e.g. ['.txt', '.doc'])
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if extension is allowed, False otherwise

    Raises:
        FileValidationError: If extension isn't allowed and throw=True
    """
    path = Path(path)
    valid = path.suffix.lower() in [ext.lower() for ext in allowed_extensions]
    if not valid and throw:
        msg = (
            f"File has invalid extension: {path.suffix}. "
            f"Allowed: {', '.join(allowed_extensions)}"
        )
        raise FileValidationError(msg)
    return valid


def validate_file_size(
    path: Union[str, Path],
    max_size: Optional[int] = None,
    min_size: Optional[int] = None,
    throw: bool = True,
) -> bool:
    """
    Validate that a file's size is within allowed limits.

    Args:
        path: Path to the file
        max_size: Maximum allowed size in bytes (None for no limit)
        min_size: Minimum allowed size in bytes (None for no limit)
        throw: Whether to raise an exception if validation fails

    Returns:
        bool: True if size is within limits, False otherwise

    Raises:
        FileValidationError: If size isn't within limits and throw=True
    """
    path = Path(path)
    size = path.stat().st_size

    if max_size is not None and size > max_size:
        if throw:
            msg = f"File is too large: {size} bytes (max {max_size})"
            raise FileValidationError(msg)
        return False

    if min_size is not None and size < min_size:
        if throw:
            msg = f"File is too small: {size} bytes (min {min_size})"
            raise FileValidationError(msg)
        return False

    return True
