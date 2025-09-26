"""
File Rename Operations Logic

Enhanced file renaming logic with comprehensive functionality,
progress tracking, and error handling.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union, NamedTuple, Callable

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Image metadata features disabled.")

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("Warning: Mutagen not available. Audio metadata features disabled.")

from PyQt5.QtCore import QObject, pyqtSignal


class RenameOperation(NamedTuple):
    """Result of a rename operation."""
    success: bool
    original_path: str
    new_path: str
    error_message: Optional[str] = None


class FileRenamer(QObject):
    """Enhanced file renaming functionality with progress tracking."""
    
    # Progress signals
    progress_updated = pyqtSignal(int, int)  # current, total
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    file_renamed = pyqtSignal(str, str, bool)  # old_name, new_name, success
    operation_completed = pyqtSignal(list)   # List[RenameOperation]
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self):
        """Initialize the file renamer."""
        super().__init__()
        self._should_cancel = False
    
    def cancel_operation(self):
        """Cancel the current operation."""
        self._should_cancel = True
    
    def get_file_metadata_date(self, filepath: Union[str, Path]) -> datetime:
        """Extract date from file metadata based on file type.
        
        Args:
            filepath: Path to the file
            
        Returns:
            datetime object from metadata or file modification time
        """
        try:
            filepath = str(filepath)
            
            # Try image metadata first
            image_date = self._extract_image_metadata_date(filepath)
            if image_date:
                return image_date
            
            # Try audio metadata
            audio_date = self._extract_audio_metadata_date(filepath)
            if audio_date:
                return audio_date

            # Fallback to file modification time
            return datetime.fromtimestamp(os.path.getmtime(filepath))
        except Exception:
            # Ultimate fallback to current time
            return datetime.now()
    
    def _extract_image_metadata_date(
        self, filepath: str
    ) -> Optional[datetime]:
        """Extract date from image metadata."""
        if not PIL_AVAILABLE or not filepath.lower().endswith(
            ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
        ):
            return None
        
        try:
            with Image.open(filepath) as img:
                exif = img.getexif()
                if exif:
                    for tag_id in exif:
                        tag = TAGS.get(tag_id, tag_id)
                        if tag in ('DateTimeOriginal', 'DateTime'):
                            date_str = exif[tag_id]
                            return datetime.strptime(
                                date_str, '%Y:%m:%d %H:%M:%S'
                            )
        except Exception:
            pass
        return None
    
    def _extract_audio_metadata_date(
        self, filepath: str
    ) -> Optional[datetime]:
        """Extract date from audio metadata."""
        if not MUTAGEN_AVAILABLE or not filepath.lower().endswith(
            ('.mp3', '.flac', '.m4a', '.wav')
        ):
            return None
        
        try:
            audio = MutagenFile(filepath)
            if audio and hasattr(audio, 'tags'):
                # Try common metadata date tags
                for tag in ('date', 'TDRC', 'year'):
                    if tag in audio.tags:
                        date_str = str(audio.tags[tag][0])
                        date_result = self._parse_audio_date(date_str)
                        if date_result:
                            return date_result
        except Exception:
            pass
        return None
    
    def _parse_audio_date(self, date_str: str) -> Optional[datetime]:
        """Parse audio metadata date string."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y')
            except ValueError:
                return None
    
    def format_date(self, date: datetime, format_str: str) -> str:
        """Format date according to selected format.
        
        Args:
            date: datetime object to format
            format_str: Format specification
            
        Returns:
            Formatted date string
        """
        formats = {
            "YYYY-MM-DD_HHMMSS": "%Y-%m-%d_%H%M%S",
            "YYYYMMDD_HHMMSS": "%Y%m%d_%H%M%S",
            "DD-MM-YYYY_HHMMSS": "%d-%m-%Y_%H%M%S",
            "YYYY-MM-DD": "%Y-%m-%d",
            "YYYYMMDD": "%Y%m%d",
            "MM-DD-YYYY": "%m-%d-%Y",
            "DD-MM-YYYY": "%d-%m-%Y",
            "YYYY_MM_DD": "%Y_%m_%d",
            "Custom": "%Y-%m-%d_%H%M%S"  # Default for custom
        }
        return date.strftime(formats.get(format_str, "%Y-%m-%d_%H%M%S"))
    
    def split_filename(self, filename: str) -> Tuple[str, str]:
        """Split a filename into name and extension.
        
        Args:
            filename: Filename to split
            
        Returns:
            Tuple of (name, extension)
        """
        return os.path.splitext(filename)
    
    def generate_new_name(
        self,
        filename: str,
        mode: str,
        text: str = "",
        date_format: Optional[str] = None,
        filepath: Optional[Union[str, Path]] = None,
        counter: Optional[int] = None
    ) -> str:
        """Generate a new filename based on the specified mode and parameters.
        
        Args:
            filename: Original filename
            mode: Renaming mode
            text: Text to add/remove/replace
            date_format: Format string for date-based renaming
            filepath: Full path to the file (needed for metadata operations)
            counter: Counter for batch operations
            
        Returns:
            New filename
        """
        name, ext = self.split_filename(filename)
        
        # Handle metadata date mode separately
        if mode == "metadata" and filepath:
            return self._generate_metadata_mode_name(
                filepath, ext, date_format
            )
        
        # Handle other modes
        new_name = self._generate_mode_specific_name(
            name, mode, text, date_format, filepath, counter
        )
        
        return f"{new_name}{ext}"
    
    def _generate_metadata_mode_name(
        self, filepath: Union[str, Path], ext: str,
        date_format: Optional[str]
    ) -> str:
        """Generate name for metadata mode."""
        date = self.get_file_metadata_date(filepath)
        if not date_format:
            date_format = "YYYY-MM-DD_HHMMSS"
        formatted_date = self.format_date(date, date_format)
        return f"{formatted_date}{ext}"
    
    def _generate_mode_specific_name(
        self,
        name: str,
        mode: str,
        text: str = "",
        date_format: Optional[str] = None,
        filepath: Optional[Union[str, Path]] = None,
        counter: Optional[int] = None
    ) -> str:
        """Generate name based on specific mode."""
        if mode in ("prefix", "remove_prefix", "suffix", "remove_suffix"):
            return self._handle_prefix_suffix_modes(name, mode, text)
        elif mode in ("new_name", "lower", "upper", "title"):
            return self._handle_text_transform_modes(name, mode, text)
        elif mode == "replace":
            return self._handle_replace_mode(name, text)
        elif mode == "sequential":
            return self._handle_sequential_mode(text, counter)
        elif mode in ("date_prefix", "date_suffix"):
            return self._handle_date_modes(name, mode, filepath, date_format)
        elif mode in ("remove_extension", "change_extension"):
            return self._handle_extension_modes(name, mode, text)
        else:
            return name
    
    def _handle_prefix_suffix_modes(
        self, name: str, mode: str, text: str
    ) -> str:
        """Handle prefix and suffix operations."""
        if mode == "prefix":
            return f"{text}{name}"
        elif mode == "remove_prefix" and name.startswith(text):
            return name[len(text):]
        elif mode == "suffix":
            return f"{name}{text}"
        elif mode == "remove_suffix" and name.endswith(text):
            return name[:-len(text)]
        return name
    
    def _handle_text_transform_modes(
        self, name: str, mode: str, text: str
    ) -> str:
        """Handle text transformation operations."""
        if mode == "new_name":
            return text
        elif mode == "lower":
            return name.lower()
        elif mode == "upper":
            return name.upper()
        elif mode == "title":
            return name.title()
        return name
    
    def _handle_replace_mode(self, name: str, text: str) -> str:
        """Handle text replacement."""
        if "|" in text:
            old_text, new_text = text.split("|", 1)
            return name.replace(old_text, new_text)
        return name
    
    def _handle_sequential_mode(
        self, text: str, counter: Optional[int]
    ) -> str:
        """Handle sequential numbering."""
        if counter is not None:
            return f"{text}_{counter:03d}"
        else:
            return f"{text}_001"
    
    def _handle_date_modes(
        self, name: str, mode: str, filepath: Optional[Union[str, Path]],
        date_format: Optional[str]
    ) -> str:
        """Handle date prefix/suffix operations."""
        if filepath:
            date = datetime.fromtimestamp(os.path.getmtime(filepath))
            date_str = self.format_date(date, date_format or "YYYYMMDD")
            return (
                f"{date_str}_{name}" if mode == "date_prefix"
                else f"{name}_{date_str}"
            )
        return name
    
    def _handle_extension_modes(
        self, name: str, mode: str, text: str
    ) -> str:
        """Handle extension operations."""
        if mode == "remove_extension":
            return name  # Return without extension
        elif mode == "change_extension":
            # Handled at parent level since we need extension handling
            return f"{name}.{text.lstrip('.')}"
        return name
    
    def validate_rename(
        self, old_path: Union[str, Path],
        new_name: str
    ) -> Tuple[bool, str]:
        """Validate a rename operation.
        
        Args:
            old_path: Current path to the file
            new_name: New filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            old_path = Path(old_path)
            
            # Check if file exists
            if not old_path.exists():
                return False, "Source file does not exist"
            
            # Check for valid filename characters
            invalid_chars = '<>:"/\\|?*'
            if any(char in new_name for char in invalid_chars):
                return False, (
                    f"Filename contains invalid characters: {invalid_chars}"
                )
            
            # Check filename length
            if len(new_name) > 255:
                return False, "Filename is too long (max 255 characters)"
            
            # Check if new name is different
            if old_path.name == new_name:
                return False, "New name is the same as current name"
            
            # Check if target already exists
            new_path = old_path.parent / new_name
            if new_path.exists():
                return False, "A file with this name already exists"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def rename_file(
        self, old_path: Union[str, Path],
        new_name: str
    ) -> RenameOperation:
        """Rename a single file.
        
        Args:
            old_path: Current path to the file
            new_name: New filename (not full path)
            
        Returns:
            RenameOperation result
        """
        try:
            old_path = Path(old_path)
            new_path = old_path.parent / new_name
            
            # Validate the operation
            is_valid, error_msg = self.validate_rename(old_path, new_name)
            if not is_valid:
                return RenameOperation(
                    False, str(old_path), str(new_path), error_msg
                )
            
            # Perform the rename
            shutil.move(str(old_path), str(new_path))
            
            return RenameOperation(
                True, str(old_path), str(new_path), None
            )
            
        except Exception as e:
            return RenameOperation(
                False, str(old_path), str(new_path), str(e)
            )
    
    def rename_files_batch(
        self,
        files: List[Union[str, Path]],
        mode: str,
        text: str = "",
        date_format: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[RenameOperation]:
        """Rename multiple files with progress tracking.
        
        Args:
            files: List of file paths
            mode: Renaming mode
            text: Text to add/remove/replace
            date_format: Format string for date-based renaming
            progress_callback: Optional progress callback function
            
        Returns:
            List of RenameOperation results
        """
        results = []
        total_files = len(files)
        self._should_cancel = False
        
        for i, filepath in enumerate(files):
            if self._should_cancel:
                break
            
            # Update progress
            self.progress_updated.emit(i + 1, total_files)
            percentage = int((i + 1) / total_files * 100)
            self.progress_percentage.emit(percentage)
            
            if progress_callback:
                progress_callback(i + 1, total_files)
            
            try:
                filepath = Path(filepath)
                
                # Generate new name
                new_name = self.generate_new_name(
                    filepath.name, mode, text, date_format, 
                    filepath, counter=i + 1
                )
                
                # Perform rename
                result = self.rename_file(filepath, new_name)
                results.append(result)
                
                # Emit signal
                self.file_renamed.emit(
                    filepath.name, new_name, result.success
                )
                
                if not result.success:
                    self.error_occurred.emit(
                        f"Failed to rename {filepath.name}: {result.error_message}"
                    )
                    
            except Exception as e:
                error_result = RenameOperation(
                    False, str(filepath), "", str(e)
                )
                results.append(error_result)
                self.error_occurred.emit(
                    f"Error processing {filepath}: {str(e)}"
                )
        
        self.operation_completed.emit(results)
        return results
    
    def get_rename_preview(
        self,
        files: List[Union[str, Path]],
        mode: str,
        text: str = "",
        date_format: Optional[str] = None
    ) -> List[Tuple[str, str, bool]]:
        """Generate a preview of rename operations without executing them.
        
        Args:
            files: List of file paths
            mode: Renaming mode
            text: Text to add/remove/replace
            date_format: Format string for date-based renaming
            
        Returns:
            List of tuples (old_name, new_name, is_valid)
        """
        preview = []
        
        for i, filepath in enumerate(files):
            try:
                filepath = Path(filepath)
                
                # Generate new name
                new_name = self.generate_new_name(
                    filepath.name, mode, text, date_format,
                    filepath, counter=i + 1
                )
                
                # Validate operation
                is_valid, _ = self.validate_rename(filepath, new_name)
                
                preview.append((filepath.name, new_name, is_valid))
                
            except Exception:
                preview.append((str(filepath), "ERROR", False))
        
        return preview