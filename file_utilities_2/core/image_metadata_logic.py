"""
Image Metadata Core Logic Module

This module contains the core business logic for image metadata operations,
separated from GUI components for better maintainability and testability.
Enhanced with comprehensive hub integration capabilities.
"""

import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional, cast

from PIL import Image
from PIL.ExifTags import TAGS as PIL_TAGS
from PyQt5.QtCore import QObject, QThread, pyqtSignal

try:
    import piexif
    import piexif.helper
except ImportError:  # pragma: no cover - optional dependency
    piexif = None  # type: ignore[assignment]


def _require_piexif() -> None:
    """Ensure the optional piexif dependency is available."""

    if piexif is None:
        raise RuntimeError(
            "piexif is required for image metadata operations. "
            "Install it with 'pip install piexif'."
        )


if piexif is not None:
    # Combine piexif's tags with PIL's for better name resolution
    ALL_KNOWN_TAGS = {
        ifd: {
            code: piexif.TAGS[ifd][code].get("name", f"UnknownTag_{code}")
            for code in piexif.TAGS[ifd]
        }
        for ifd in piexif.TAGS
    }
else:
    ALL_KNOWN_TAGS = {"0th": {}, "Exif": {}}

# Add PIL tags if missing (might be duplicates, piexif takes precedence)
for code, name in PIL_TAGS.items():
    found = False
    for ifd_tags in ALL_KNOWN_TAGS.values():
        if code in ifd_tags:
            found = True
            break
    if not found:
        # Add to a default IFD like '0th' if not found anywhere
        if 0xFFFE < code:  # Treat higher codes generally
            ALL_KNOWN_TAGS.setdefault("Exif", {})
            ALL_KNOWN_TAGS["Exif"].setdefault(code, name)
        else:
            ALL_KNOWN_TAGS.setdefault("0th", {})
            ALL_KNOWN_TAGS["0th"].setdefault(code, name)


def get_tag_name(ifd_name: str, tag_code: int) -> str:
    """Gets a human-readable tag name."""
    if ifd_name in ALL_KNOWN_TAGS and tag_code in ALL_KNOWN_TAGS[ifd_name]:
        return ALL_KNOWN_TAGS[ifd_name][tag_code]
    # Fallback using PIL tags directly by code
    return PIL_TAGS.get(tag_code, f"UnknownTag_{tag_code}")


def format_exif_value(value: Any) -> str:
    """Formats EXIF value for display, handling bytes."""
    if isinstance(value, bytes):
        try:
            # Try decoding common text encodings
            # Strip null terminators and potential whitespace padding
            return value.decode("utf-8").strip("\x00 ")
        except UnicodeDecodeError:
            # Handle specific known byte structures or return hex/repr
            if len(value) > 16:  # Avoid huge hex strings
                return f"{value[:16].hex()}... (bytes)"
            else:
                return f"{value.hex()} (bytes)"
    elif isinstance(value, tuple) and all(isinstance(x, int) for x in value):
        # Often represents rational (num, den), display as fraction or float
        if len(value) == 2 and value[1] != 0:
            # Heuristic: If den is 1 or num/den is simple float, show float
            if value[1] == 1:
                return str(value[0])
            # Show as fraction for typical EXIF rationals (exposure, aperture)
            return f"{value[0]}/{value[1]}"
        else:
            # Other tuples just show as string representation
            return str(value)
    # Handle other types like int, float, str directly
    return str(value)


def parse_exif_value(value_str: str, original_type: type, tag_code: int) -> Any:
    """Attempts to parse string input back to appropriate EXIF type."""
    # Simple heuristic based on original type
    if isinstance(original_type, bytes):
        # Try encoding back to UTF-8, common for text tags stored as bytes
        if piexif is not None and tag_code == piexif.ExifIFD.UserComment:
            # Needs encoding preamble - let piexif.helper handle it
            return value_str
        try:
            # Assume UTF-8 is the most likely intended encoding
            return value_str.encode("utf-8")
        except Exception:
            raise ValueError(f"Cannot encode '{value_str}' back to bytes for this tag.")
    elif isinstance(original_type, int):
        try:
            return int(value_str)
        except ValueError:
            raise ValueError(f"Invalid integer value: '{value_str}'")
    elif (
        isinstance(original_type, tuple)
        and len(original_type) == 2
        and all(isinstance(x, int) for x in original_type)
    ):
        # Handle rational (fraction or float input)
        try:
            if "/" in value_str:
                num, den = map(int, value_str.split("/", 1))
                if den == 0:
                    raise ValueError("Denominator cannot be zero")
                return (num, den)
            else:
                # Try converting float to rational
                f_val = float(value_str)
                # Simple conversion for basic floats
                if f_val == int(f_val):
                    return (int(f_val), 1)
                else:
                    raise ValueError(
                        "Use fraction format (e.g., 1/100) for "
                        "non-integer rational values."
                    )
        except ValueError as e:
            raise ValueError(
                f"Invalid rational value format: '{value_str}'. "
                f"Use 'num/den'. Error: {e}"
            )
    elif original_type is str:
        return value_str
    else:
        # Default to string if original type wasn't bytes, int, or tuple
        return value_str


class ImageMetadataLogic(QObject):
    """
    Enhanced core logic for image metadata operations.

    Features:
    - Progress tracking with hub integration
    - Batch processing capabilities
    - Enhanced error handling and reporting
    - Resource management coordination
    - Thread-safe operations
    """

    # Progress tracking signals following file_utilities_2 patterns
    progress_updated = pyqtSignal(int, int)  # current, total
    progress_percentage = pyqtSignal(int)  # percentage (0-100)
    progress_message = pyqtSignal(str)  # detailed status message
    milestone_reached = pyqtSignal(str, int)  # milestone desc, percentage
    time_estimate = pyqtSignal(str)  # estimated time remaining

    # Operation completion signals
    metadata_loaded = pyqtSignal(dict)  # loaded metadata
    metadata_saved = pyqtSignal(bool, str)  # success, message
    batch_completed = pyqtSignal(dict)  # batch results

    # Error and status signals
    error_occurred = pyqtSignal(str)  # error messages
    warning_occurred = pyqtSignal(str)  # warning messages
    operation_cancelled = pyqtSignal()  # cancellation notification
    finished = pyqtSignal()  # operation completion

    def __init__(self, hub_connector=None):
        """Initialize with optional hub integration."""
        super().__init__()
        self._hub_connector = hub_connector
        self._is_running = False
        self._should_cancel = False
        self._current_operation = None
        self._filepath = None
        self.original_exif_dict = None

        # Performance metrics
        self._performance_metrics = {
            "files_processed": 0,
            "bytes_processed": 0,
            "start_time": None,
            "end_time": None,
            "processing_rate": 0,
        }

    def load_image_metadata(
        self,
        file_path: str,
        include_thumbnails: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Load image metadata with comprehensive progress tracking.

        Args:
            file_path: Path to image file
            include_thumbnails: Whether to include thumbnail data
            progress_callback: Optional progress callback

        Returns:
            Dictionary containing processed metadata

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If file format is unsupported
            PermissionError: If file cannot be accessed
        """
        _require_piexif()
        assert piexif is not None
        piexif_module = cast(Any, piexif)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        self._is_running = True
        self._should_cancel = False
        self._filepath = file_path

        # Report to hub if connected
        if self._hub_connector:
            self._hub_connector.report_status_to_hub(
                "loading_metadata",
                {"file_path": file_path, "start_time": datetime.now().isoformat()},
            )

        try:
            self.progress_message.emit("Validating image file...")
            self.milestone_reached.emit("File Validation", 10)

            # Validate image file
            self._validate_image_file(file_path)

            self.progress_message.emit("Loading EXIF data...")
            self.milestone_reached.emit("EXIF Loading", 30)

            # Load EXIF data using piexif
            self.original_exif_dict = piexif_module.load(file_path)

            if not self.original_exif_dict or not any(self.original_exif_dict.values()):
                # Check if dict is empty or all IFDs are empty
                self.metadata_loaded.emit({})
                self.finished.emit()
                return {}

            self.progress_message.emit("Processing metadata...")
            self.milestone_reached.emit("Metadata Processing", 60)

            # Process metadata for display
            processed_metadata = self._process_metadata_for_display(
                self.original_exif_dict, include_thumbnails
            )

            self.progress_message.emit("Finalizing results...")
            self.milestone_reached.emit("Finalization", 90)

            # Add file information
            processed_metadata["file_info"] = self._get_file_info(file_path)

            self.progress_percentage.emit(100)
            self.milestone_reached.emit("Loading Complete", 100)

            # Report completion to hub
            if self._hub_connector:
                self._hub_connector.report_status_to_hub(
                    "metadata_loaded",
                    {
                        "file_path": file_path,
                        "metadata_count": len(processed_metadata),
                        "completion_time": datetime.now().isoformat(),
                    },
                )

            self.metadata_loaded.emit(processed_metadata)
            return processed_metadata

        except Exception as e:
            error_msg = f"Error loading metadata: {str(e)}"
            self.error_occurred.emit(error_msg)

            # Report error to hub
            if self._hub_connector:
                self._hub_connector.report_error_to_hub(
                    error_msg, {"file_path": file_path, "error_type": type(e).__name__}
                )

            raise
        finally:
            self._is_running = False
            self.finished.emit()

    def save_image_metadata(
        self, file_path: str, modified_data: Dict[str, Any]
    ) -> bool:
        """Persist metadata updates back to the image file."""

        _require_piexif()
        assert piexif is not None
        piexif_module = cast(Any, piexif)

        try:
            if not self.original_exif_dict:
                if os.path.exists(file_path):
                    print(
                        "Original file had no EXIF data. Attempting to add" " new EXIF."
                    )
                    self.original_exif_dict = {}
                else:
                    raise RuntimeError(
                        "Original file path not set or file missing. Cannot" " save."
                    )

            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"File not found (was it moved/deleted?): {file_path}"
                )

            new_exif_dict: Dict[str, Any] = {}

            for ifd_name, tags in modified_data.items():
                if ifd_name in {"thumbnail", "file_info"}:
                    continue

                bucket = new_exif_dict.setdefault(ifd_name, {})

                for tag_code, tag_info in tags.items():
                    original_value = tag_info.get("original_value")
                    original_type = tag_info.get("original_type", str)
                    current_value = tag_info["value"]

                    original_display = (
                        format_exif_value(original_value)
                        if original_value is not None
                        else None
                    )

                    if current_value == original_display and original_value is not None:
                        bucket[tag_code] = original_value
                        continue

                    try:
                        parsed_value = parse_exif_value(
                            current_value, original_type(), tag_code
                        )
                    except ValueError as exc:
                        tag_name = get_tag_name(ifd_name, tag_code)
                        raise ValueError(
                            "Error parsing value for tag "
                            f"'{tag_name}' ({ifd_name}/{tag_code}): {exc}"
                        ) from exc

                    if tag_code == piexif_module.ExifIFD.UserComment and isinstance(
                        parsed_value, str
                    ):
                        user_comment_bytes = piexif_module.helper.UserComment.dump(
                            parsed_value
                        )
                        bucket[tag_code] = user_comment_bytes
                    else:
                        bucket[tag_code] = parsed_value

            if (
                "thumbnail" in self.original_exif_dict
                and self.original_exif_dict["thumbnail"]
            ):
                new_exif_dict["thumbnail"] = self.original_exif_dict["thumbnail"]
            else:
                new_exif_dict["thumbnail"] = None

            empty_ifds = [
                ifd
                for ifd, tags in new_exif_dict.items()
                if not tags and ifd != "thumbnail"
            ]
            for ifd in empty_ifds:
                del new_exif_dict[ifd]

            exif_bytes = b""
            has_data = (
                any(ifd != "thumbnail" and tags for ifd, tags in new_exif_dict.items())
                or new_exif_dict.get("thumbnail") is not None
            )

            if has_data:
                try:
                    exif_bytes = piexif_module.dump(new_exif_dict)
                except Exception as exc:
                    raise ValueError(
                        f"Error converting data to EXIF format: {exc}"
                    ) from exc

            try:
                piexif_module.insert(exif_bytes, file_path)
                if not exif_bytes:
                    message = (
                        "All EXIF data removed from " f"{os.path.basename(file_path)}."
                    )
                else:
                    message = (
                        "EXIF data successfully saved to "
                        f"{os.path.basename(file_path)}."
                    )
                self.metadata_saved.emit(True, message)
                return True
            except Exception as exc:
                raise IOError(f"Error writing EXIF data to file: {exc}") from exc

        except Exception as exc:
            error_msg = f"Error saving metadata: {exc}"
            self.error_occurred.emit(error_msg)
            self.metadata_saved.emit(False, error_msg)
            return False
        finally:
            self.finished.emit()

    def _validate_image_file(self, file_path: str):
        """Validate that the file is a supported image format."""
        try:
            img = Image.open(file_path)
            img.verify()
            fmt = img.format
            img.close()
            if fmt not in ("JPEG", "TIFF"):
                raise ValueError(
                    f"Unsupported format: {fmt}. Only JPEG/TIFF supported by " "piexif."
                )
        except Exception as pil_e:
            raise ValueError(f"Cannot open or verify image file: {pil_e}")

    def _process_metadata_for_display(
        self,
        exif_dict: Dict[str, Any],
        include_thumbnails: bool = False,
    ) -> Dict[str, Any]:
        """Process the EXIF dictionary for display."""
        processed_data = {}

        for ifd_name in exif_dict:
            # Skip thumbnail binary data unless requested
            if ifd_name == "thumbnail" and not include_thumbnails:
                continue
            if not exif_dict[ifd_name]:
                continue

            processed_data[ifd_name] = {}
            for tag_code, value in exif_dict[ifd_name].items():
                tag_name = get_tag_name(ifd_name, tag_code)
                display_value = format_exif_value(value)
                processed_data[ifd_name][tag_code] = {
                    "name": tag_name,
                    "value": display_value,
                    "original_value": value,
                    "original_type": type(value),
                }

        return processed_data

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        stat_info = os.stat(file_path)
        return {
            "file_name": os.path.basename(file_path),
            "file_size": stat_info.st_size,
            "modified_time": stat_info.st_mtime,
            "file_path": file_path,
        }

    def cancel_operation(self):
        """Cancel the current operation."""
        self._should_cancel = True
        self.progress_message.emit("Cancelling operation...")

        # Report cancellation to hub if connected
        if self._hub_connector:
            self._hub_connector.report_status_to_hub(
                "cancelled",
                {
                    "reason": "user_requested",
                    "cancelled_at": datetime.now().isoformat(),
                },
            )

        self.operation_cancelled.emit()

    def is_running(self) -> bool:
        """Check if an operation is currently running."""
        return self._is_running

    def set_hub_connector(self, hub_connector):
        """Set the hub connector for this logic instance."""
        self._hub_connector = hub_connector


class ImageMetadataWorker(QThread):
    """Worker thread for image metadata operations without blocking the GUI."""

    # Signals for communicating with the main thread
    metadata_processed = pyqtSignal(dict)
    metadata_error = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)

    def __init__(
        self,
        logic: ImageMetadataLogic,
        file_path: str,
        operation: str = "load",
        **kwargs,
    ):
        """
        Initialize the worker thread.

        Args:
            logic: ImageMetadataLogic instance to use
            file_path: File path to process
            operation: Operation type ('load', 'save')
            **kwargs: Additional arguments for the operation
        """
        super().__init__()
        self.logic = logic
        self.file_path = file_path
        self.operation = operation
        self.kwargs = kwargs

        # Connect logic signals to worker signals
        self.logic.progress_percentage.connect(self.progress_update.emit)
        self.logic.progress_message.connect(self.status_update.emit)
        self.logic.metadata_loaded.connect(self.metadata_processed.emit)
        self.logic.error_occurred.connect(self.metadata_error.emit)

    def run(self):
        """Run the metadata operation in the worker thread."""
        try:
            if self.operation == "load":
                self.logic.load_image_metadata(self.file_path, **self.kwargs)
            elif self.operation == "save":
                modified_data = self.kwargs.get("modified_data", {})
                self.logic.save_image_metadata(self.file_path, modified_data)
        except Exception as e:
            self.metadata_error.emit(str(e))

    def cancel(self):
        """Cancel the operation."""
        self.logic.cancel_operation()
        self.quit()
        self.wait()
