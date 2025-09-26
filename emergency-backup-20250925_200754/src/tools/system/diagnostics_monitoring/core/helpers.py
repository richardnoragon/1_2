"""
General helper functions for the diagnostics monitoring system.

This module provides utility functions and helper methods that are used
across multiple components of the diagnostics monitoring system.
"""

import os
import sys
import time
import logging
import platform
import subprocess
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime


# Configure logging
logger = logging.getLogger("RFU.DiagnosticsMonitoring.Helpers")


def format_bytes(bytes_value: Union[int, float]) -> str:
    """
    Format bytes value to human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB", "234 MB")
    """
    if bytes_value < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(bytes_value)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_frequency(hz_value: Union[int, float]) -> str:
    """
    Format frequency value to human-readable string.

    Args:
        hz_value: Frequency in Hz

    Returns:
        Formatted string (e.g., "2.4 GHz", "1500 MHz")
    """
    if hz_value < 0:
        return "0 Hz"

    units = ["Hz", "KHz", "MHz", "GHz", "THz"]
    unit_index = 0
    freq = float(hz_value)

    while freq >= 1000 and unit_index < len(units) - 1:
        freq /= 1000
        unit_index += 1

    if unit_index == 0:
        return f"{int(freq)} {units[unit_index]}"
    else:
        return f"{freq:.1f} {units[unit_index]}"


def format_percentage(
    value: Union[int, float], decimal_places: int = 1
) -> str:
    """
    Format percentage value.

    Args:
        value: Percentage value (0-100)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2h 30m", "45s")
    """
    if seconds < 0:
        return "0s"

    total_seconds = int(seconds)
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_timestamp(
    timestamp: Optional[float] = None, format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format timestamp to string.

    Args:
        timestamp: Unix timestamp (defaults to current time)
        format_string: Format string for datetime formatting

    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_string)


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: Union[int, float] = 0,
) -> Union[int, float]:
    """
    Safely divide two numbers, returning default if division by zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero

    Returns:
        Division result or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def get_platform_info() -> Dict[str, str]:
    """
    Get comprehensive platform information.

    Returns:
        Dictionary with platform details
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "platform": platform.platform(),
        "node": platform.node(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def is_process_running(pid: int) -> bool:
    """
    Check if a process with given PID is running.

    Args:
        pid: Process ID

    Returns:
        True if process is running, False otherwise
    """
    try:
        if sys.platform.startswith("win"):
            # Windows
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        else:
            # Unix-like systems
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def get_file_age(file_path: Union[str, Path]) -> float:
    """
    Get the age of a file in seconds.

    Args:
        file_path: Path to the file

    Returns:
        File age in seconds
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return 0

        stat_info = path.stat()
        return time.time() - stat_info.st_mtime
    except (OSError, ValueError):
        return 0


def ensure_directory(directory_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, ValueError):
        logger.error(f"Failed to create directory: {directory_path}")
        return False


def clamp(
    value: Union[int, float],
    min_value: Union[int, float],
    max_value: Union[int, float],
) -> Union[int, float]:
    """
    Clamp a value between minimum and maximum bounds.

    Args:
        value: Value to clamp
        min_value: Minimum bound
        max_value: Maximum bound

    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def moving_average(
    values: List[Union[int, float]], window_size: int
) -> List[float]:
    """
    Calculate moving average of a list of values.

    Args:
        values: List of numeric values
        window_size: Size of the moving window

    Returns:
        List of moving averages
    """
    if not values or window_size <= 0:
        return []

    if window_size > len(values):
        window_size = len(values)

    averages = []
    for i in range(len(values) - window_size + 1):
        window = values[i : i + window_size]
        average = sum(window) / len(window)
        averages.append(average)

    return averages


def calculate_percentile(
    values: List[Union[int, float]], percentile: float
) -> Optional[float]:
    """
    Calculate the specified percentile of a list of values.

    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)

    Returns:
        Percentile value or None if invalid input
    """
    if not values or not (0 <= percentile <= 100):
        return None

    sorted_values = sorted(values)
    index = (percentile / 100) * (len(sorted_values) - 1)

    if index.is_integer():
        return float(sorted_values[int(index)])
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index

        if upper_index >= len(sorted_values):
            return float(sorted_values[lower_index])

        return (
            sorted_values[lower_index] * (1 - weight)
            + sorted_values[upper_index] * weight
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Characters not allowed in filenames on Windows
    invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "/", "\\"]

    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"

    return sanitized


def validate_config_value(
    value: Any, expected_type: type, default: Any = None
) -> Any:
    """
    Validate and convert configuration value to expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        default: Default value if validation fails

    Returns:
        Validated value or default
    """
    try:
        if isinstance(value, expected_type):
            return value

        # Try to convert to expected type
        if expected_type == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        elif expected_type in (int, float):
            return expected_type(value)
        elif expected_type == str:
            return str(value)
        else:
            return expected_type(value)

    except (ValueError, TypeError):
        logger.warning(
            f"Invalid config value {value}, using default {default}"
        )
        return default


def throttle_calls(func):
    """
    Decorator to throttle function calls to prevent excessive execution.

    Args:
        func: Function to throttle

    Returns:
        Throttled function
    """
    last_called = {"time": 0}
    min_interval = 0.1  # Minimum 100ms between calls

    def wrapper(*args, **kwargs):
        current_time = time.time()
        if current_time - last_called["time"] >= min_interval:
            last_called["time"] = current_time
            return func(*args, **kwargs)
        return None

    return wrapper


def retry_on_exception(
    max_retries: int = 3, delay: float = 1.0, exceptions: Tuple = (Exception,)
):
    """
    Decorator to retry function calls on specific exceptions.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exception types to catch

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    else:
                        logger.warning(
                            f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {e}"
                        )
                        time.sleep(delay)
            return None

        return wrapper

    return decorator


class CircularBuffer:
    """Circular buffer for storing fixed-size data history."""

    def __init__(self, size: int):
        """
        Initialize circular buffer.

        Args:
            size: Maximum buffer size
        """
        self.size = max(1, size)
        self.buffer = []
        self.index = 0

    def append(self, value: Any) -> None:
        """
        Add value to buffer.

        Args:
            value: Value to add
        """
        if len(self.buffer) < self.size:
            self.buffer.append(value)
        else:
            self.buffer[self.index] = value
            self.index = (self.index + 1) % self.size

    def get_all(self) -> List[Any]:
        """
        Get all values in chronological order.

        Returns:
            List of values
        """
        if len(self.buffer) < self.size:
            return self.buffer.copy()
        else:
            return self.buffer[self.index :] + self.buffer[: self.index]

    def get_latest(self, count: int = 1) -> List[Any]:
        """
        Get the latest N values.

        Args:
            count: Number of latest values to get

        Returns:
            List of latest values
        """
        all_values = self.get_all()
        return all_values[-count:] if count <= len(all_values) else all_values

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.index = 0

    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) == self.size

    def __len__(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)


# Helper constants
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024
BYTES_PER_TB = 1024 * 1024 * 1024 * 1024

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

DEFAULT_UPDATE_INTERVAL = 2.0  # seconds
DEFAULT_HISTORY_SIZE = 60  # data points
DEFAULT_CHART_POINTS = 100  # chart data points


# Export all helper functions and classes
__all__ = [
    "format_bytes",
    "format_frequency",
    "format_percentage",
    "format_duration",
    "format_timestamp",
    "safe_divide",
    "get_platform_info",
    "is_process_running",
    "get_file_age",
    "ensure_directory",
    "clamp",
    "moving_average",
    "calculate_percentile",
    "sanitize_filename",
    "validate_config_value",
    "throttle_calls",
    "retry_on_exception",
    "CircularBuffer",
    "BYTES_PER_KB",
    "BYTES_PER_MB",
    "BYTES_PER_GB",
    "BYTES_PER_TB",
    "SECONDS_PER_MINUTE",
    "SECONDS_PER_HOUR",
    "SECONDS_PER_DAY",
    "DEFAULT_UPDATE_INTERVAL",
    "DEFAULT_HISTORY_SIZE",
    "DEFAULT_CHART_POINTS",
]
