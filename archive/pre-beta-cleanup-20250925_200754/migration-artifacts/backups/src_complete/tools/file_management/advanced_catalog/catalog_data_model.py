"""Core data model for the Advanced File Catalog Generator.

This module defines the data structures used throughout the catalog system,
including file entries, catalog containers, and configuration enums.
"""

import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SortCriteria(Enum):
    """Enumeration of available sorting criteria."""
    ALPHABETICAL = "alphabetical"
    SIZE = "size"
    TYPE = "type"
    CREATED_DATE = "created_date"
    MODIFIED_DATE = "modified_date"
    ACCESSED_DATE = "accessed_date"


class ColorScheme(Enum):
    """Enumeration of available color schemes."""
    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND_FRIENDLY = "colorblind_friendly"
    MONOCHROME = "monochrome"
    CUSTOM = "custom"


class FileType(Enum):
    """Enumeration of file type categories."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    CODE = "code"
    DATA = "data"
    OTHER = "other"


class SizeCategory(Enum):
    """Enumeration of file size categories."""
    SMALL = "small"      # < 1MB
    MEDIUM = "medium"    # 1MB - 100MB
    LARGE = "large"      # > 100MB


class DateCategory(Enum):
    """Enumeration of file date categories."""
    RECENT = "recent"        # < 30 days
    MODERATE = "moderate"    # 30-365 days
    OLD = "old"             # > 365 days


class AlphabeticalCategory(Enum):
    """Enumeration of alphabetical ranges."""
    A_E = "a_e"
    F_J = "f_j"
    K_O = "k_o"
    P_T = "p_t"
    U_Z = "u_z"


@dataclass
class ColorInfo:
    """Information about color coding for a category."""
    color_hex: str
    color_rgb: tuple
    pattern_type: str
    icon: str
    accessibility_label: str
    category_name: str


@dataclass
class FileEntry:
    """Represents a single file with all metadata and categorization."""
    path: Path
    name: str
    size: int
    created_date: datetime
    modified_date: datetime
    accessed_date: datetime
    file_type: FileType
    extension: str
    color_category: Optional[ColorInfo] = None
    sort_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize computed properties after object creation."""
        if not self.name:
            self.name = self.path.name
        if not self.extension:
            self.extension = self.path.suffix.lower()
        if self.file_type == FileType.OTHER:
            self.file_type = self._detect_file_type()
        
        # Add MIME type to metadata
        mime_type, _ = mimetypes.guess_type(str(self.path))
        if mime_type:
            self.metadata['mime_type'] = mime_type

    def _detect_file_type(self) -> FileType:
        """Detect file type based on extension."""
        ext = self.extension.lower()
        
        # Document types
        if ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages']:
            return FileType.DOCUMENT
        
        # Image types
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', 
                     '.webp', '.ico', '.raw']:
            return FileType.IMAGE
        
        # Video types
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', 
                     '.m4v', '.3gp']:
            return FileType.VIDEO
        
        # Audio types
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
            return FileType.AUDIO
        
        # Archive types
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', 
                     '.dmg', '.iso']:
            return FileType.ARCHIVE
        
        # Executable types
        elif ext in ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg', '.pkg']:
            return FileType.EXECUTABLE
        
        # Code types
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', 
                     '.php', '.rb', '.go', '.rs', '.swift']:
            return FileType.CODE
        
        # Data types
        elif ext in ['.json', '.xml', '.csv', '.sql', '.db', '.sqlite', 
                     '.yaml', '.yml']:
            return FileType.DATA
        
        return FileType.OTHER

    def get_size_category(self) -> SizeCategory:
        """Get size category for this file."""
        if self.size < 1024 * 1024:  # < 1MB
            return SizeCategory.SMALL
        elif self.size < 100 * 1024 * 1024:  # < 100MB
            return SizeCategory.MEDIUM
        else:
            return SizeCategory.LARGE

    def get_date_category(self, date_type: str = 'modified') -> DateCategory:
        """Get date category for this file."""
        if date_type == 'created':
            target_date = self.created_date
        elif date_type == 'accessed':
            target_date = self.accessed_date
        else:
            target_date = self.modified_date
        
        days_old = (datetime.now() - target_date).days
        
        if days_old < 30:
            return DateCategory.RECENT
        elif days_old < 365:
            return DateCategory.MODERATE
        else:
            return DateCategory.OLD

    def get_alphabetical_category(self) -> AlphabeticalCategory:
        """Get alphabetical category for this file."""
        first_char = self.name[0].lower() if self.name else 'z'
        
        if 'a' <= first_char <= 'e':
            return AlphabeticalCategory.A_E
        elif 'f' <= first_char <= 'j':
            return AlphabeticalCategory.F_J
        elif 'k' <= first_char <= 'o':
            return AlphabeticalCategory.K_O
        elif 'p' <= first_char <= 't':
            return AlphabeticalCategory.P_T
        else:
            return AlphabeticalCategory.U_Z

    def format_size(self) -> str:
        """Format file size to human readable format."""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        
        for unit in units:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        
        return f"{size:.1f} {units[-1]}"

    @classmethod
    def from_path(cls, file_path: Path) -> 'FileEntry':
        """Create FileEntry from a file path."""
        try:
            stat = file_path.stat()
            return cls(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                created_date=datetime.fromtimestamp(stat.st_ctime),
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                accessed_date=datetime.fromtimestamp(stat.st_atime),
                file_type=FileType.OTHER,  # Will be detected in __post_init__
                extension=file_path.suffix.lower()
            )
        except (OSError, ValueError) as e:
            # Handle files that can't be accessed
            return cls(
                path=file_path,
                name=file_path.name,
                size=0,
                created_date=datetime.now(),
                modified_date=datetime.now(),
                accessed_date=datetime.now(),
                file_type=FileType.OTHER,
                extension=file_path.suffix.lower(),
                metadata={'error': str(e)}
            )


@dataclass
class CatalogStatistics:
    """Statistics about the catalog contents."""
    total_files: int = 0
    total_size: int = 0
    file_type_counts: Dict[FileType, int] = field(default_factory=dict)
    size_distribution: Dict[SizeCategory, int] = field(default_factory=dict)
    date_distribution: Dict[DateCategory, int] = field(default_factory=dict)
    largest_file: Optional[FileEntry] = None
    smallest_file: Optional[FileEntry] = None
    newest_file: Optional[FileEntry] = None
    oldest_file: Optional[FileEntry] = None


class CatalogData:
    """Main container for catalog data and operations."""
    
    def __init__(self, source_directory: Optional[Path] = None):
        self.source_directory = source_directory
        self.entries: List[FileEntry] = []
        self.sort_criteria = SortCriteria.ALPHABETICAL
        self.color_scheme = ColorScheme.DEFAULT
        self.statistics = CatalogStatistics()
        self.color_legend: Dict[str, List[ColorInfo]] = {}
        self.generation_time = datetime.now()

    def add_entry(self, entry: FileEntry) -> None:
        """Add a file entry to the catalog."""
        self.entries.append(entry)
        self._update_statistics_for_entry(entry)

    def remove_entry(self, path: Path) -> bool:
        """Remove a file entry from the catalog."""
        for i, entry in enumerate(self.entries):
            if entry.path == path:
                del self.entries[i]
                self._recalculate_statistics()
                return True
        return False

    def clear(self) -> None:
        """Clear all entries from the catalog."""
        self.entries.clear()
        self.statistics = CatalogStatistics()
        self.color_legend.clear()

    def get_filtered_entries(self, 
                           file_types: Optional[List[FileType]] = None,
                           size_range: Optional[tuple] = None,
                           date_range: Optional[tuple] = None) -> List[FileEntry]:
        """Get filtered list of entries based on criteria."""
        filtered = self.entries
        
        if file_types:
            filtered = [e for e in filtered if e.file_type in file_types]
        
        if size_range:
            min_size, max_size = size_range
            filtered = [e for e in filtered 
                       if min_size <= e.size <= max_size]
        
        if date_range:
            start_date, end_date = date_range
            filtered = [e for e in filtered 
                       if start_date <= e.modified_date <= end_date]
        
        return filtered

    def _update_statistics_for_entry(self, entry: FileEntry) -> None:
        """Update statistics when adding a new entry."""
        stats = self.statistics
        stats.total_files += 1
        stats.total_size += entry.size
        
        # Update type counts
        if entry.file_type not in stats.file_type_counts:
            stats.file_type_counts[entry.file_type] = 0
        stats.file_type_counts[entry.file_type] += 1
        
        # Update size distribution
        size_cat = entry.get_size_category()
        if size_cat not in stats.size_distribution:
            stats.size_distribution[size_cat] = 0
        stats.size_distribution[size_cat] += 1
        
        # Update date distribution
        date_cat = entry.get_date_category()
        if date_cat not in stats.date_distribution:
            stats.date_distribution[date_cat] = 0
        stats.date_distribution[date_cat] += 1
        
        # Update extremes
        if not stats.largest_file or entry.size > stats.largest_file.size:
            stats.largest_file = entry
        
        if not stats.smallest_file or entry.size < stats.smallest_file.size:
            stats.smallest_file = entry
        
        if not stats.newest_file or entry.modified_date > stats.newest_file.modified_date:
            stats.newest_file = entry
        
        if not stats.oldest_file or entry.modified_date < stats.oldest_file.modified_date:
            stats.oldest_file = entry

    def _recalculate_statistics(self) -> None:
        """Recalculate all statistics from scratch."""
        self.statistics = CatalogStatistics()
        for entry in self.entries:
            self._update_statistics_for_entry(entry)

    def scan_directory(self, directory: Path, recursive: bool = False) -> None:
        """Scan a directory and populate the catalog."""
        self.source_directory = directory
        self.clear()
        
        try:
            if recursive:
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        entry = FileEntry.from_path(file_path)
                        self.add_entry(entry)
            else:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        entry = FileEntry.from_path(file_path)
                        self.add_entry(entry)
        except (OSError, PermissionError) as e:
            print(f"Error scanning directory {directory}: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the catalog contents."""
        return {
            'source_directory': str(self.source_directory) if self.source_directory else None,
            'total_files': self.statistics.total_files,
            'total_size': self.statistics.total_size,
            'total_size_formatted': self._format_size(self.statistics.total_size),
            'file_types': {ft.value: count for ft, count in self.statistics.file_type_counts.items()},
            'size_distribution': {sc.value: count for sc, count in self.statistics.size_distribution.items()},
            'date_distribution': {dc.value: count for dc, count in self.statistics.date_distribution.items()},
            'generation_time': self.generation_time.isoformat(),
            'sort_criteria': self.sort_criteria.value,
            'color_scheme': self.color_scheme.value
        }

    def _format_size(self, size: int) -> str:
        """Format size in bytes to human readable format."""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size_float = float(size)
        
        for unit in units:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        
        return f"{size_float:.1f} {units[-1]}"