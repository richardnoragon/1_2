"""
File operations module with integrated error handling.
"""

from pathlib import Path
from typing import Union, List, Optional
from ..error_handler import error_handler


class FileHandler:
    """Handles common file operations with error handling."""

    @staticmethod
    def read_file(
        file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Read a file with error handling.

        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)

        Returns:
            str: File contents if successful, None if error occurred
        """
        try:
            file_path = Path(file_path)
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return error_handler.handle_error(
                error=e,
                operation=f"reading file {file_path}",
                context={"path": str(file_path), "encoding": encoding},
            )

    @staticmethod
    def write_file(
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        backup: bool = True,
    ) -> bool:
        """
        Write to a file with error handling and backup.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding (default: utf-8)
            backup: Whether to create a backup before writing (default: True)

        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            file_path = Path(file_path)

            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                file_path.rename(backup_path)

            # Write new content
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            return True

        except Exception as e:
            return error_handler.handle_error(
                error=e,
                operation=f"writing to file {file_path}",
                context={"path": str(file_path), "encoding": encoding},
            )

    @staticmethod
    def delete_file(file_path: Union[str, Path], backup: bool = True) -> bool:
        """
        Delete a file with error handling and optional backup.

        Args:
            file_path: Path to the file
            backup: Whether to create backup before deletion (default: True)

        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                return True

            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                file_path.rename(backup_path)
            else:
                file_path.unlink()
            return True

        except Exception as e:
            return error_handler.handle_error(
                error=e,
                operation=f"deleting file {file_path}",
                context={"path": str(file_path), "backup": backup},
            )
