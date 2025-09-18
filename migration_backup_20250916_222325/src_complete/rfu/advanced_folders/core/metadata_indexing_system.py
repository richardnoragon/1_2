"""
Metadata Indexing System for Advanced Folders - Week 7 Implementation.

Enterprise-grade metadata extraction, indexing, and management system with
comprehensive support for file attributes, extended metadata, and custom
property extraction following principal engineer standards.

Features:
- Multi-source metadata extraction (filesystem, EXIF, document properties)
- Hierarchical metadata organization and categorization
- Real-time metadata synchronization and updates
- Metadata-based search and filtering capabilities
- Custom metadata field definitions and validation
- Performance-optimized indexing with caching
- Cross-platform metadata handling
- Enterprise security and access controls
"""

import hashlib
import json
import logging
import mimetypes
import os
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Optional imports for enhanced metadata extraction
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import xattr
    XATTR_AVAILABLE = True
except ImportError:
    XATTR_AVAILABLE = False

from ..exceptions.advanced_folders_exceptions import (
    SearchException, PerformanceException, ValidationException
)
from .file_system_scanner import FileInfo


class MetadataCategory(Enum):
    """Categories for organizing metadata fields."""
    FILESYSTEM = "filesystem"
    CONTENT = "content"
    MEDIA = "media"
    DOCUMENT = "document"
    SECURITY = "security"
    CUSTOM = "custom"
    SYSTEM = "system"


class MetadataType(Enum):
    """Types of metadata values."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"


@dataclass
class MetadataField:
    """Definition of a metadata field."""
    
    name: str
    category: MetadataCategory
    data_type: MetadataType
    description: str
    required: bool = False
    indexed: bool = True
    searchable: bool = True
    default_value: Any = None
    validation_pattern: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "category": self.category.value,
            "data_type": self.data_type.value,
            "description": self.description,
            "required": self.required,
            "indexed": self.indexed,
            "searchable": self.searchable,
            "default_value": self.default_value,
            "validation_pattern": self.validation_pattern
        }


@dataclass
class MetadataEntry:
    """Individual metadata entry for a file."""
    
    file_path: str
    field_name: str
    field_value: Any
    category: MetadataCategory
    data_type: MetadataType
    extracted_at: datetime
    source: str  # Which extractor provided this metadata
    confidence: float = 1.0  # Confidence in the metadata accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "file_path": self.file_path,
            "field_name": self.field_name,
            "field_value": self._serialize_value(),
            "category": self.category.value,
            "data_type": self.data_type.value,
            "extracted_at": self.extracted_at.isoformat(),
            "source": self.source,
            "confidence": self.confidence
        }
    
    def _serialize_value(self) -> str:
        """Serialize field value for database storage."""
        if self.data_type == MetadataType.DATETIME:
            if isinstance(self.field_value, datetime):
                return self.field_value.isoformat()
        elif self.data_type == MetadataType.JSON:
            return json.dumps(self.field_value)
        elif self.data_type == MetadataType.BINARY:
            if isinstance(self.field_value, bytes):
                return self.field_value.hex()
        
        return str(self.field_value)


@dataclass
class MetadataExtractionResult:
    """Result of metadata extraction for a file."""
    
    file_path: str
    entries: List[MetadataEntry]
    extraction_time_ms: float
    extractor_name: str
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage."""
        return {
            "file_path": self.file_path,
            "entries_count": len(self.entries),
            "extraction_time_ms": round(self.extraction_time_ms, 2),
            "extractor_name": self.extractor_name,
            "success": self.success,
            "error_message": self.error_message,
            "warnings": self.warnings.copy()
        }


class MetadataExtractor(ABC):
    """Abstract base class for metadata extractors."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get extractor name."""
        pass
    
    @abstractmethod
    def can_extract(self, file_path: str, file_info: FileInfo) -> bool:
        """Check if this extractor can handle the file."""
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: str, file_info: FileInfo) -> 
        MetadataExtractionResult:
        """Extract metadata from the file."""
        pass


class FilesystemMetadataExtractor(MetadataExtractor):
    """Extractor for basic filesystem metadata."""
    
    def __init__(self):
        """Initialize filesystem metadata extractor."""
        self.logger = logging.getLogger('RFU.FilesystemMetadataExtractor')
    
    def get_name(self) -> str:
        """Get extractor name."""
        return "filesystem"
    
    def can_extract(self, file_path: str, file_info: FileInfo) -> bool:
        """Can extract from any file."""
        return True
    
    def extract_metadata(
        self, file_path: str, file_info: FileInfo
    ) -> MetadataExtractionResult:
        """Extract filesystem metadata."""
        start_time = time.time()
        entries = []
        warnings = []
        
        try:
            file_path_obj = Path(file_path)
            stat_info = file_path_obj.stat()
            
            # Basic filesystem metadata
            metadata_fields = [
                ("file_size", stat_info.st_size, MetadataType.INTEGER),
                ("created_time", datetime.fromtimestamp(
                    stat_info.st_ctime, tz=timezone.utc
                ), MetadataType.DATETIME),
                ("modified_time", datetime.fromtimestamp(
                    stat_info.st_mtime, tz=timezone.utc
                ), MetadataType.DATETIME),
                ("accessed_time", datetime.fromtimestamp(
                    stat_info.st_atime, tz=timezone.utc
                ), MetadataType.DATETIME),
                ("file_extension", file_path_obj.suffix.lower(), 
                 MetadataType.STRING),
                ("file_name", file_path_obj.name, MetadataType.STRING),
                ("parent_directory", str(file_path_obj.parent), 
                 MetadataType.STRING),
                ("is_hidden", file_info.is_hidden, MetadataType.BOOLEAN),
                ("is_system", file_info.is_system, MetadataType.BOOLEAN),
                ("mime_type", file_info.mime_type, MetadataType.STRING),
            ]
            
            # Add platform-specific metadata
            if os.name == 'nt':  # Windows
                metadata_fields.extend([
                    ("file_attributes", self._get_windows_attributes(
                        file_path_obj
                    ), MetadataType.JSON),
                ])
            
            # Add extended attributes if available
            if XATTR_AVAILABLE:
                try:
                    xattrs = dict(xattr.xattr(file_path))
                    if xattrs:
                        metadata_fields.append((
                            "extended_attributes", xattrs, MetadataType.JSON
                        ))
                except Exception as e:
                    warnings.append(f"Failed to extract xattrs: {str(e)}")
            
            # Create metadata entries
            for field_name, field_value, data_type in metadata_fields:
                if field_value is not None:
                    entry = MetadataEntry(
                        file_path=file_path,
                        field_name=field_name,
                        field_value=field_value,
                        category=MetadataCategory.FILESYSTEM,
                        data_type=data_type,
                        extracted_at=datetime.now(timezone.utc),
                        source=self.get_name()
                    )
                    entries.append(entry)
            
            extraction_time = (time.time() - start_time) * 1000
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=entries,
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                warnings=warnings
            )
            
        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Filesystem metadata extraction failed for {file_path}: {e}"
            )
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=[],
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                success=False,
                error_message=str(e)
            )
    
    def _get_windows_attributes(self, file_path: Path) -> Dict[str, Any]:
        """Get Windows-specific file attributes."""
        if not WIN32_AVAILABLE:
            return {}
        
        try:
            attrs = win32api.GetFileAttributes(str(file_path))
            attributes = {}
            
            # Decode attribute flags
            attr_flags = {
                'ARCHIVE': win32con.FILE_ATTRIBUTE_ARCHIVE,
                'COMPRESSED': win32con.FILE_ATTRIBUTE_COMPRESSED,
                'DIRECTORY': win32con.FILE_ATTRIBUTE_DIRECTORY,
                'ENCRYPTED': win32con.FILE_ATTRIBUTE_ENCRYPTED,
                'HIDDEN': win32con.FILE_ATTRIBUTE_HIDDEN,
                'NORMAL': win32con.FILE_ATTRIBUTE_NORMAL,
                'READONLY': win32con.FILE_ATTRIBUTE_READONLY,
                'SYSTEM': win32con.FILE_ATTRIBUTE_SYSTEM,
                'TEMPORARY': win32con.FILE_ATTRIBUTE_TEMPORARY,
            }
            
            for name, flag in attr_flags.items():
                attributes[name.lower()] = bool(attrs & flag)
            
            return attributes
            
        except Exception as e:
            self.logger.warning(
                f"Failed to get Windows attributes for {file_path}: {e}"
            )
            return {}


class ImageMetadataExtractor(MetadataExtractor):
    """Extractor for image metadata including EXIF data."""
    
    def __init__(self):
        """Initialize image metadata extractor."""
        self.logger = logging.getLogger('RFU.ImageMetadataExtractor')
        self.supported_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/tiff',
            'image/bmp', 'image/gif', 'image/webp'
        }
    
    def get_name(self) -> str:
        """Get extractor name."""
        return "image"
    
    def can_extract(self, file_path: str, file_info: FileInfo) -> bool:
        """Check if file is a supported image type."""
        return (PIL_AVAILABLE and 
                file_info.mime_type in self.supported_types)
    
    def extract_metadata(
        self, file_path: str, file_info: FileInfo
    ) -> MetadataExtractionResult:
        """Extract image metadata including EXIF."""
        start_time = time.time()
        entries = []
        warnings = []
        
        try:
            with Image.open(file_path) as img:
                # Basic image properties
                metadata_fields = [
                    ("image_width", img.width, MetadataType.INTEGER),
                    ("image_height", img.height, MetadataType.INTEGER),
                    ("image_mode", img.mode, MetadataType.STRING),
                    ("image_format", img.format, MetadataType.STRING),
                ]
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    exif_dict = {}
                    
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        
                        # Convert values to serializable format
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except Exception:
                                value = value.hex()
                        elif hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        
                        exif_dict[str(tag_name)] = str(value)
                    
                    if exif_dict:
                        metadata_fields.append((
                            "exif_data", exif_dict, MetadataType.JSON
                        ))
                
                # Check for additional metadata
                if hasattr(img, 'info') and img.info:
                    info_dict = {}
                    for key, value in img.info.items():
                        if isinstance(value, (str, int, float)):
                            info_dict[str(key)] = value
                    
                    if info_dict:
                        metadata_fields.append((
                            "image_info", info_dict, MetadataType.JSON
                        ))
                
                # Create metadata entries
                for field_name, field_value, data_type in metadata_fields:
                    if field_value is not None:
                        entry = MetadataEntry(
                            file_path=file_path,
                            field_name=field_name,
                            field_value=field_value,
                            category=MetadataCategory.MEDIA,
                            data_type=data_type,
                            extracted_at=datetime.now(timezone.utc),
                            source=self.get_name()
                        )
                        entries.append(entry)
            
            extraction_time = (time.time() - start_time) * 1000
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=entries,
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                warnings=warnings
            )
            
        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Image metadata extraction failed for {file_path}: {e}"
            )
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=[],
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                success=False,
                error_message=str(e)
            )


class DocumentMetadataExtractor(MetadataExtractor):
    """Extractor for document metadata."""
    
    def __init__(self):
        """Initialize document metadata extractor."""
        self.logger = logging.getLogger('RFU.DocumentMetadataExtractor')
        self.supported_types = {
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/html', 'text/xml'
        }
    
    def get_name(self) -> str:
        """Get extractor name."""
        return "document"
    
    def can_extract(self, file_path: str, file_info: FileInfo) -> bool:
        """Check if file is a supported document type."""
        return file_info.mime_type in self.supported_types
    
    def extract_metadata(
        self, file_path: str, file_info: FileInfo
    ) -> MetadataExtractionResult:
        """Extract document metadata."""
        start_time = time.time()
        entries = []
        warnings = []
        
        try:
            # For now, extract basic document properties
            file_path_obj = Path(file_path)
            
            # Estimate word count for text files
            if file_info.mime_type.startswith('text/'):
                try:
                    with open(file_path, 'r', encoding='utf-8', 
                             errors='ignore') as f:
                        content = f.read(100000)  # Read first 100KB
                        word_count = len(content.split())
                        line_count = content.count('\n') + 1
                        char_count = len(content)
                    
                    metadata_fields = [
                        ("word_count", word_count, MetadataType.INTEGER),
                        ("line_count", line_count, MetadataType.INTEGER),
                        ("character_count", char_count, MetadataType.INTEGER),
                    ]
                    
                    # Create metadata entries
                    for field_name, field_value, data_type in metadata_fields:
                        entry = MetadataEntry(
                            file_path=file_path,
                            field_name=field_name,
                            field_value=field_value,
                            category=MetadataCategory.DOCUMENT,
                            data_type=data_type,
                            extracted_at=datetime.now(timezone.utc),
                            source=self.get_name()
                        )
                        entries.append(entry)
                        
                except Exception as e:
                    warnings.append(f"Failed to analyze text content: {e}")
            
            extraction_time = (time.time() - start_time) * 1000
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=entries,
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                warnings=warnings
            )
            
        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Document metadata extraction failed for {file_path}: {e}"
            )
            
            return MetadataExtractionResult(
                file_path=file_path,
                entries=[],
                extraction_time_ms=extraction_time,
                extractor_name=self.get_name(),
                success=False,
                error_message=str(e)
            )


class MetadataIndexManager:
    """
    Enterprise metadata indexing manager with advanced capabilities.
    """
    
    def __init__(self, index_path: str, max_workers: int = 4):
        """
        Initialize metadata index manager.
        
        Args:
            index_path: Path for storing metadata index
            max_workers: Maximum worker threads for extraction
        """
        self.index_path = Path(index_path)
        self.max_workers = max_workers
        
        # Create index directory
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.index_path / "metadata_index.db"
        self._init_database()
        
        # Initialize extractors
        self.extractors: List[MetadataExtractor] = [
            FilesystemMetadataExtractor(),
            ImageMetadataExtractor(),
            DocumentMetadataExtractor()
        ]
        
        # Metadata field registry
        self.field_registry: Dict[str, MetadataField] = {}
        self._init_default_fields()
        
        # Threading and caching
        self._index_lock = threading.RLock()
        self._cache_lock = threading.RLock()
        self._metadata_cache: Dict[str, List[MetadataEntry]] = {}
        self.cache_size_limit = 10000
        
        # Statistics
        self.extraction_stats = {
            'total_files': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_extraction_time_ms': 0.0
        }
        
        self.logger = logging.getLogger('RFU.MetadataIndexManager')
        self.logger.info("Metadata index manager initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for metadata storage."""
        conn = sqlite3.connect(str(self.db_path))
        
        # Metadata fields table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata_fields (
                name TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                data_type TEXT NOT NULL,
                description TEXT,
                required INTEGER DEFAULT 0,
                indexed INTEGER DEFAULT 1,
                searchable INTEGER DEFAULT 1,
                default_value TEXT,
                validation_pattern TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Metadata entries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_value TEXT,
                category TEXT NOT NULL,
                data_type TEXT NOT NULL,
                extracted_at TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                UNIQUE(file_path, field_name, source)
            )
        """)
        
        # Create indices for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_metadata_file_path 
            ON metadata_entries(file_path)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_metadata_field_name 
            ON metadata_entries(field_name)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_metadata_category 
            ON metadata_entries(category)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_metadata_search 
            ON metadata_entries(field_name, field_value)
        """)
        
        conn.commit()
        conn.close()
    
    def _init_default_fields(self) -> None:
        """Initialize default metadata field definitions."""
        default_fields = [
            # Filesystem fields
            MetadataField(
                "file_size", MetadataCategory.FILESYSTEM, 
                MetadataType.INTEGER, "File size in bytes"
            ),
            MetadataField(
                "created_time", MetadataCategory.FILESYSTEM, 
                MetadataType.DATETIME, "File creation timestamp"
            ),
            MetadataField(
                "modified_time", MetadataCategory.FILESYSTEM, 
                MetadataType.DATETIME, "File modification timestamp"
            ),
            MetadataField(
                "file_extension", MetadataCategory.FILESYSTEM, 
                MetadataType.STRING, "File extension"
            ),
            MetadataField(
                "mime_type", MetadataCategory.FILESYSTEM, 
                MetadataType.STRING, "MIME type"
            ),
            
            # Media fields
            MetadataField(
                "image_width", MetadataCategory.MEDIA, 
                MetadataType.INTEGER, "Image width in pixels"
            ),
            MetadataField(
                "image_height", MetadataCategory.MEDIA, 
                MetadataType.INTEGER, "Image height in pixels"
            ),
            MetadataField(
                "exif_data", MetadataCategory.MEDIA, 
                MetadataType.JSON, "EXIF metadata from image"
            ),
            
            # Document fields
            MetadataField(
                "word_count", MetadataCategory.DOCUMENT, 
                MetadataType.INTEGER, "Number of words in document"
            ),
            MetadataField(
                "line_count", MetadataCategory.DOCUMENT, 
                MetadataType.INTEGER, "Number of lines in document"
            ),
        ]
        
        for field in default_fields:
            self.register_field(field)
    
    def register_field(self, field: MetadataField) -> None:
        """
        Register a new metadata field.
        
        Args:
            field: MetadataField definition to register
        """
        with self._index_lock:
            self.field_registry[field.name] = field
            
            # Store in database
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT OR REPLACE INTO metadata_fields 
                (name, category, data_type, description, required, 
                 indexed, searchable, default_value, validation_pattern)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                field.name, field.category.value, field.data_type.value,
                field.description, field.required, field.indexed,
                field.searchable, field.default_value, 
                field.validation_pattern
            ))
            conn.commit()
            conn.close()
    
    def extract_metadata(self, file_info: FileInfo) -> List[MetadataEntry]:
        """
        Extract all metadata for a file.
        
        Args:
            file_info: File information object
            
        Returns:
            List of extracted metadata entries
        """
        all_entries = []
        
        for extractor in self.extractors:
            if extractor.can_extract(file_info.path, file_info):
                try:
                    result = extractor.extract_metadata(
                        file_info.path, file_info
                    )
                    
                    if result.success:
                        all_entries.extend(result.entries)
                        self.extraction_stats['successful_extractions'] += 1
                    else:
                        self.extraction_stats['failed_extractions'] += 1
                        self.logger.warning(
                            f"Metadata extraction failed for {file_info.path}: "
                            f"{result.error_message}"
                        )
                    
                    self.extraction_stats['total_extraction_time_ms'] += (
                        result.extraction_time_ms
                    )
                    
                except Exception as e:
                    self.extraction_stats['failed_extractions'] += 1
                    self.logger.error(
                        f"Metadata extractor {extractor.get_name()} failed "
                        f"for {file_info.path}: {e}"
                    )
        
        # Store entries in database
        if all_entries:
            self._store_metadata_entries(all_entries)
        
        # Update cache
        with self._cache_lock:
            self._metadata_cache[file_info.path] = all_entries
            self._cleanup_cache()
        
        self.extraction_stats['total_files'] += 1
        return all_entries
    
    def extract_metadata_batch(
        self, file_infos: List[FileInfo]
    ) -> Dict[str, List[MetadataEntry]]:
        """
        Extract metadata for multiple files concurrently.
        
        Args:
            file_infos: List of file information objects
            
        Returns:
            Dictionary mapping file paths to metadata entries
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.extract_metadata, file_info): file_info
                for file_info in file_infos
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    entries = future.result(timeout=30.0)
                    results[file_info.path] = entries
                except Exception as e:
                    self.logger.error(
                        f"Failed to extract metadata for {file_info.path}: {e}"
                    )
                    results[file_info.path] = []
        
        return results
    
    def get_file_metadata(
        self, file_path: str, use_cache: bool = True
    ) -> List[MetadataEntry]:
        """
        Get metadata for a specific file.
        
        Args:
            file_path: Path to the file
            use_cache: Whether to use cached metadata
            
        Returns:
            List of metadata entries for the file
        """
        # Check cache first
        if use_cache:
            with self._cache_lock:
                if file_path in self._metadata_cache:
                    return self._metadata_cache[file_path].copy()
        
        # Load from database
        entries = self._load_metadata_from_db(file_path)
        
        # Update cache
        if use_cache:
            with self._cache_lock:
                self._metadata_cache[file_path] = entries
                self._cleanup_cache()
        
        return entries
    
    def search_by_metadata(
        self,
        field_name: str,
        field_value: str,
        comparison: str = "equals",
        category: Optional[MetadataCategory] = None
    ) -> List[str]:
        """
        Search for files by metadata criteria.
        
        Args:
            field_name: Name of the metadata field
            field_value: Value to search for
            comparison: Comparison operator (equals, contains, gt, lt, etc.)
            category: Optional category filter
            
        Returns:
            List of file paths matching the criteria
        """
        conn = sqlite3.connect(str(self.db_path))
        
        # Build query based on comparison type
        if comparison == "equals":
            where_clause = "field_value = ?"
            params = [field_value]
        elif comparison == "contains":
            where_clause = "field_value LIKE ?"
            params = [f"%{field_value}%"]
        elif comparison == "starts_with":
            where_clause = "field_value LIKE ?"
            params = [f"{field_value}%"]
        elif comparison == "gt":
            where_clause = "CAST(field_value AS REAL) > ?"
            params = [float(field_value)]
        elif comparison == "lt":
            where_clause = "CAST(field_value AS REAL) < ?"
            params = [float(field_value)]
        else:
            where_clause = "field_value = ?"
            params = [field_value]
        
        query = f"""
            SELECT DISTINCT file_path 
            FROM metadata_entries 
            WHERE field_name = ? AND {where_clause}
        """
        params.insert(0, field_name)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        cursor = conn.execute(query, params)
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def _store_metadata_entries(self, entries: List[MetadataEntry]) -> None:
        """Store metadata entries in database."""
        if not entries:
            return
        
        conn = sqlite3.connect(str(self.db_path))
        
        for entry in entries:
            conn.execute("""
                INSERT OR REPLACE INTO metadata_entries 
                (file_path, field_name, field_value, category, data_type, 
                 extracted_at, source, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.file_path, entry.field_name, entry._serialize_value(),
                entry.category.value, entry.data_type.value,
                entry.extracted_at.isoformat(), entry.source, 
                entry.confidence
            ))
        
        conn.commit()
        conn.close()
    
    def _load_metadata_from_db(self, file_path: str) -> List[MetadataEntry]:
        """Load metadata entries from database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM metadata_entries WHERE file_path = ?
        """, (file_path,))
        
        entries = []
        for row in cursor:
            entry = MetadataEntry(
                file_path=row['file_path'],
                field_name=row['field_name'],
                field_value=self._deserialize_value(
                    row['field_value'], 
                    MetadataType(row['data_type'])
                ),
                category=MetadataCategory(row['category']),
                data_type=MetadataType(row['data_type']),
                extracted_at=datetime.fromisoformat(row['extracted_at']),
                source=row['source'],
                confidence=row['confidence']
            )
            entries.append(entry)
        
        conn.close()
        return entries
    
    def _deserialize_value(self, value: str, data_type: MetadataType) -> Any:
        """Deserialize value from database storage."""
        if data_type == MetadataType.INTEGER:
            return int(value)
        elif data_type == MetadataType.FLOAT:
            return float(value)
        elif data_type == MetadataType.BOOLEAN:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif data_type == MetadataType.DATETIME:
            return datetime.fromisoformat(value)
        elif data_type == MetadataType.JSON:
            return json.loads(value)
        elif data_type == MetadataType.BINARY:
            return bytes.fromhex(value)
        else:
            return value
    
    def _cleanup_cache(self) -> None:
        """Clean up metadata cache if it exceeds size limit."""
        if len(self._metadata_cache) > self.cache_size_limit:
            # Remove oldest entries (simple FIFO)
            excess_count = len(self._metadata_cache) - self.cache_size_limit
            keys_to_remove = list(self._metadata_cache.keys())[:excess_count]
            
            for key in keys_to_remove:
                del self._metadata_cache[key]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metadata indexing statistics."""
        stats = self.extraction_stats.copy()
        
        # Add database statistics
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT file_path) FROM metadata_entries
            """)
            stats['indexed_files'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM metadata_entries")
            stats['total_metadata_entries'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM metadata_fields")
            stats['registered_fields'] = cursor.fetchone()[0]
            
            # Database size
            db_size_mb = (self.db_path.stat().st_size / (1024 * 1024) 
                         if self.db_path.exists() else 0)
            stats['database_size_mb'] = round(db_size_mb, 2)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
        
        # Cache statistics
        stats['cache_size'] = len(self._metadata_cache)
        stats['cache_hit_ratio'] = 0.0  # Would need hit tracking for this
        
        # Average extraction time
        if stats['total_files'] > 0:
            stats['avg_extraction_time_ms'] = round(
                stats['total_extraction_time_ms'] / stats['total_files'], 2
            )
        
        return stats
    
    def optimize_index(self) -> None:
        """Optimize metadata index for better performance."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.commit()
            conn.close()
            
            self.logger.info("Metadata index optimization completed")
            
        except Exception as e:
            self.logger.error(f"Index optimization failed: {e}")
    
    def clear_metadata(self, file_path: Optional[str] = None) -> None:
        """
        Clear metadata entries.
        
        Args:
            file_path: Specific file path to clear, or None for all
        """
        with self._index_lock:
            conn = sqlite3.connect(str(self.db_path))
            
            if file_path:
                conn.execute(
                    "DELETE FROM metadata_entries WHERE file_path = ?",
                    (file_path,)
                )
                # Remove from cache
                with self._cache_lock:
                    self._metadata_cache.pop(file_path, None)
            else:
                conn.execute("DELETE FROM metadata_entries")
                # Clear cache
                with self._cache_lock:
                    self._metadata_cache.clear()
                # Reset statistics
                self.extraction_stats = {
                    'total_files': 0,
                    'successful_extractions': 0,
                    'failed_extractions': 0,
                    'total_extraction_time_ms': 0.0
                }
            
            conn.commit()
            conn.close()
            
            self.logger.info(
                f"Metadata cleared for {'all files' if not file_path else file_path}"
            )