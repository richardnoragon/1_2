"""Core file operations functionality."""

import os

from core.error_handler import error_handler
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as MutagenFile


class FileRenamer:
    """Core file renaming functionality."""

    @staticmethod
    def get_file_metadata_date(filepath: Union[str, Path]) -> datetime:
        """Extract date from file metadata based on file type."""
        try:
            filepath = str(filepath)
            # Image files (JPEG, PNG, etc.)
            if filepath.lower().endswith(
                (".jpg", ".jpeg", ".png", ".tiff", ".bmp")
            ):
                with Image.open(filepath) as img:
                    exif = img.getexif()
                    if exif:
                        for tag_id in exif:
                            tag = TAGS.get(tag_id, tag_id)
                            if tag in ("DateTimeOriginal", "DateTime"):
                                date_str = exif[tag_id]
                                return datetime.strptime(
                                    date_str, "%Y:%m:%d %H:%M:%S"
                                )

            # Audio files (MP3, FLAC, etc.)
            elif filepath.lower().endswith((".mp3", ".flac", ".m4a", ".wav")):
                audio = MutagenFile(filepath)
                if audio:
                    if hasattr(audio, "tags"):
                        # Try common metadata date tags
                        for tag in ("date", "TDRC", "year"):
                            if tag in audio.tags:
                                date_str = str(audio.tags[tag][0])
                                try:
                                    return datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    )
                                except ValueError:
                                    try:
                                        return datetime.strptime(
                                            date_str, "%Y"
                                        )
                                    except ValueError:
                                        continue

            # Fallback to file modification time
            return datetime.fromtimestamp(os.path.getmtime(filepath))
        except Exception:
            return datetime.fromtimestamp(os.path.getmtime(filepath))

    @staticmethod
    def format_date(date: datetime, format_str: str) -> str:
        """Format date according to selected format."""
        formats = {
            "YYYY-MM-DD_HHMMSS": "%Y-%m-%d_%H%M%S",
            "YYYYMMDD_HHMMSS": "%Y%m%d_%H%M%S",
            "DD-MM-YYYY_HHMMSS": "%d-%m-%Y_%H%M%S",
            "YYYY-MM-DD": "%Y-%m-%d",
            "YYYYMMDD": "%Y%m%d",
        }
        return date.strftime(formats.get(format_str, "%Y-%m-%d_%H%M%S"))

    @staticmethod
    def split_filename(filename: str) -> Tuple[str, str]:
        """Split a filename into name and extension."""
        return os.path.splitext(filename)

    @staticmethod
    def get_new_name(
        filename: str,
        mode: str,
        text: str = "",
        date_format: Optional[str] = None,
        filepath: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Generate a new filename based on the specified mode and parameters.

        Args:
            filename: Original filename
            mode: Renaming mode ('prefix', 'suffix', 'remove_prefix', 'remove_suffix',
                  'new_name', 'lower', 'upper', 'date_prefix', 'date_suffix', 'metadata')
            text: Text to add/remove/replace
            date_format: Format string for date-based renaming
            filepath: Full path to the file (needed for metadata and date operations)

        Returns:
            New filename
        """
        name, ext = FileRenamer.split_filename(filename)

        if mode == "metadata" and filepath:
            date = FileRenamer.get_file_metadata_date(filepath)
            if not date_format:
                date_format = "YYYY-MM-DD_HHMMSS"
            return FileRenamer.format_date(date, date_format) + ext

        new_name = name
        if mode == "prefix":
            new_name = f"{text}{name}"
        elif mode == "remove_prefix" and name.startswith(text):
            new_name = name[len(text) :]
        elif mode == "suffix":
            new_name = f"{name}{text}"
        elif mode == "remove_suffix" and name.endswith(text):
            new_name = name[: -len(text)]
        elif mode == "new_name":
            new_name = text
        elif mode == "lower":
            new_name = name.lower()
        elif mode == "upper":
            new_name = name.upper()
        elif mode in ("date_prefix", "date_suffix") and filepath:
            date = datetime.fromtimestamp(os.path.getmtime(filepath))
            date_str = date.strftime("%Y%m%d")
            new_name = (
                f"{date_str}_{name}"
                if mode == "date_prefix"
                else f"{name}_{date_str}"
            )

        return new_name + ext

    @staticmethod
    def rename_file(old_path: Union[str, Path], new_name: str) -> bool:
        """
        Rename a file.

        Args:
            old_path: Current path to the file
            new_name: New filename (not path)

        Returns:
            True if successful, False otherwise
        """
        try:
            old_path = Path(old_path)
            new_path = old_path.parent / new_name
            if old_path != new_path:
                shutil.move(str(old_path), str(new_path))
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def rename_files(
        files: List[Union[str, Path]],
        mode: str,
        text: str = "",
        date_format: Optional[str] = None,
    ) -> List[bool]:
        """
        Rename multiple files.

        Args:
            files: List of file paths
            mode: Renaming mode
            text: Text to add/remove/replace
            date_format: Format string for date-based renaming

        Returns:
            List of booleans indicating success/failure for each file
        """
        results = []
        for filepath in files:
            filepath = Path(filepath)
            new_name = FileRenamer.get_new_name(
                filepath.name, mode, text, date_format, filepath
            )
            results.append(FileRenamer.rename_file(filepath, new_name))
        return results
