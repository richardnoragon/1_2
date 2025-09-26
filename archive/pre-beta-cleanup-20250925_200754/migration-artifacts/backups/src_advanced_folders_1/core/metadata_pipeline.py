"""
Advanced Folders - Metadata Extraction Pipeline

Extensible pipeline supporting 50+ file formats with EXIF, document properties,
and custom attribute extraction for comprehensive file analysis and search.

Features:
- Multi-format support (images, documents, audio, video, archives)
- EXIF data extraction for images
- Document properties extraction (Office, PDF, etc.)
- Audio/video metadata extraction
- Archive content analysis
- Custom attribute extraction framework
- Asynchronous processing with threading
- Caching of extracted metadata
- Error handling and fallback strategies
- Extensible plugin architecture

Author: RFU Development Team
Version: 1.0.0
"""

import hashlib
import json
import logging
import mimetypes
import os
import sqlite3
import threading
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# Third-party imports with fallback handling
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from ..exceptions.advanced_folders_exceptions import (MetadataException,
                                                      ValidationException)


@dataclass
class MetadataEntry:
    """Represents extracted metadata for a file."""
    file_path: str
    file_size: int
    mime_type: str
    extracted_time: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_method: str = ""
    extraction_duration_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'extracted_time': self.extracted_time.isoformat(),
            'metadata': self.metadata,
            'extraction_method': self.extraction_method,
            'extraction_duration_ms': self.extraction_duration_ms,
            'errors': self.errors
        }


@dataclass
class ExtractionStatistics:
    """Statistics for metadata extraction operations."""
    total_files_processed: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    total_processing_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0
    formats_processed: Dict[str, int] = field(default_factory=dict)
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    def update_stats(self, success: bool, processing_time_ms: float, 
                    file_format: str, error_type: Optional[str] = None):
        """Update extraction statistics."""
        self.total_files_processed += 1
        self.total_processing_time_ms += processing_time_ms
        
        if success:
            self.successful_extractions += 1
        else:
            self.failed_extractions += 1
            if error_type:
                self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        
        self.formats_processed[file_format] = self.formats_processed.get(file_format, 0) + 1
        
        if self.total_files_processed > 0:
            self.average_processing_time_ms = (
                self.total_processing_time_ms / self.total_files_processed
            )


class MetadataExtractor(ABC):
    """Abstract base class for metadata extractors."""
    
    @abstractmethod
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if extractor can handle the file."""
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported file formats."""
        pass
    
    @property
    @abstractmethod
    def extractor_name(self) -> str:
        """Return name of the extractor."""
        pass


class ImageMetadataExtractor(MetadataExtractor):
    """Extractor for image metadata including EXIF data."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if file is a supported image format."""
        if not HAS_PIL:
            return False
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif'}
        return Path(file_path).suffix.lower() in image_extensions
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata including EXIF data."""
        if not HAS_PIL:
            raise MetadataException("PIL not available for image metadata extraction")
        
        metadata = {}
        
        try:
            with Image.open(file_path) as image:
                # Basic image properties
                metadata.update({
                    'width': image.width,
                    'height': image.height,
                    'format': image.format,
                    'mode': image.mode,
                    'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
                })
                
                # EXIF data
                if hasattr(image, '_getexif') and image._getexif():
                    exif_data = {}
                    for tag_id, value in image._getexif().items():
                        tag = TAGS.get(tag_id, tag_id)
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = str(value)
                        exif_data[tag] = value
                    
                    metadata['exif'] = exif_data
                
                # Additional image info
                if image.info:
                    info_data = {}
                    for key, value in image.info.items():
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = str(value)
                        info_data[key] = value
                    metadata['image_info'] = info_data
                    
        except Exception as e:
            raise MetadataException(f"Error extracting image metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return supported image formats."""
        return ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp', 'gif']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "ImageMetadataExtractor"


class AudioMetadataExtractor(MetadataExtractor):
    """Extractor for audio metadata including ID3 tags."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if file is a supported audio format."""
        if not HAS_MUTAGEN:
            return False
        
        audio_extensions = {'.mp3', '.flac', '.ogg', '.m4a', '.wma', '.wav'}
        return Path(file_path).suffix.lower() in audio_extensions
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio metadata including tags."""
        if not HAS_MUTAGEN:
            raise MetadataException("Mutagen not available for audio metadata extraction")
        
        metadata = {}
        
        try:
            audio_file = mutagen.File(file_path)
            if audio_file is None:
                return metadata
            
            # Basic audio properties
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata.update({
                    'duration_seconds': getattr(info, 'length', 0),
                    'bitrate': getattr(info, 'bitrate', 0),
                    'sample_rate': getattr(info, 'sample_rate', 0),
                    'channels': getattr(info, 'channels', 0),
                })
            
            # Audio tags
            if audio_file.tags:
                tags = {}
                for key, value in audio_file.tags.items():
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                    elif isinstance(value, list):
                        value = [str(v) for v in value]
                    tags[key] = str(value)
                
                metadata['tags'] = tags
                
                # Extract common tag fields
                common_tags = {
                    'title': ['TIT2', 'TITLE', 'Title'],
                    'artist': ['TPE1', 'ARTIST', 'Artist'],
                    'album': ['TALB', 'ALBUM', 'Album'],
                    'date': ['TDRC', 'DATE', 'Date'],
                    'genre': ['TCON', 'GENRE', 'Genre'],
                    'track': ['TRCK', 'TRACKNUMBER', 'TrackNumber']
                }
                
                for common_key, possible_keys in common_tags.items():
                    for key in possible_keys:
                        if key in tags:
                            metadata[common_key] = tags[key]
                            break
                            
        except ID3NoHeaderError:
            # No ID3 header, but file might still be valid
            pass
        except Exception as e:
            raise MetadataException(f"Error extracting audio metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return supported audio formats."""
        return ['mp3', 'flac', 'ogg', 'm4a', 'wma', 'wav']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "AudioMetadataExtractor"


class DocumentMetadataExtractor(MetadataExtractor):
    """Extractor for document metadata (PDF, Office docs)."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if file is a supported document format."""
        doc_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.rtf'}
        return Path(file_path).suffix.lower() in doc_extensions
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract document metadata."""
        metadata = {}
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf' and HAS_PYPDF2:
                metadata.update(self._extract_pdf_metadata(file_path))
            elif file_ext == '.docx' and HAS_DOCX:
                metadata.update(self._extract_docx_metadata(file_path))
            elif file_ext in {'.txt', '.rtf'}:
                metadata.update(self._extract_text_metadata(file_path))
                
        except Exception as e:
            raise MetadataException(f"Error extracting document metadata: {str(e)}")
        
        return metadata
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Basic PDF properties
                metadata.update({
                    'page_count': len(pdf_reader.pages),
                    'encrypted': pdf_reader.is_encrypted
                })
                
                # PDF metadata
                if pdf_reader.metadata:
                    pdf_meta = {}
                    for key, value in pdf_reader.metadata.items():
                        if key.startswith('/'):
                            key = key[1:]  # Remove leading slash
                        pdf_meta[key] = str(value) if value else ""
                    metadata['pdf_metadata'] = pdf_meta
                    
                # Extract text from first page for preview
                if pdf_reader.pages:
                    try:
                        first_page_text = pdf_reader.pages[0].extract_text()
                        if first_page_text:
                            metadata['preview_text'] = first_page_text[:500]
                    except Exception:
                        pass
                        
        except Exception as e:
            raise MetadataException(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def _extract_docx_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract DOCX metadata."""
        metadata = {}
        
        try:
            doc = DocxDocument(file_path)
            
            # Document properties
            if hasattr(doc, 'core_properties'):
                props = doc.core_properties
                metadata.update({
                    'title': props.title or "",
                    'author': props.author or "",
                    'subject': props.subject or "",
                    'created': props.created.isoformat() if props.created else "",
                    'modified': props.modified.isoformat() if props.modified else "",
                    'keywords': props.keywords or "",
                    'comments': props.comments or ""
                })
            
            # Document statistics
            paragraphs = len(doc.paragraphs)
            tables = len(doc.tables)
            
            # Extract text content for word count
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    full_text.append(paragraph.text)
            
            text_content = ' '.join(full_text)
            word_count = len(text_content.split()) if text_content else 0
            
            metadata.update({
                'paragraph_count': paragraphs,
                'table_count': tables,
                'word_count': word_count,
                'character_count': len(text_content)
            })
            
            # Preview text
            if text_content:
                metadata['preview_text'] = text_content[:500]
                
        except Exception as e:
            raise MetadataException(f"Error extracting DOCX metadata: {str(e)}")
        
        return metadata
    
    def _extract_text_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract text file metadata."""
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
                lines = content.split('\n')
                words = content.split()
                
                metadata.update({
                    'line_count': len(lines),
                    'word_count': len(words),
                    'character_count': len(content),
                    'encoding': 'utf-8'
                })
                
                # Preview text
                if content:
                    metadata['preview_text'] = content[:500]
                    
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    content = file.read()
                    metadata.update({
                        'character_count': len(content),
                        'encoding': 'latin1'
                    })
            except Exception:
                metadata['encoding'] = 'unknown'
        except Exception as e:
            raise MetadataException(f"Error extracting text metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return supported document formats."""
        return ['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'rtf']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "DocumentMetadataExtractor"


class ArchiveMetadataExtractor(MetadataExtractor):
    """Extractor for archive metadata (ZIP, RAR, etc.)."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if file is a supported archive format."""
        archive_extensions = {'.zip', '.7z', '.rar', '.tar', '.gz'}
        return Path(file_path).suffix.lower() in archive_extensions
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract archive metadata."""
        metadata = {}
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.zip':
                metadata.update(self._extract_zip_metadata(file_path))
            else:
                # Basic archive info
                metadata.update({
                    'archive_type': file_ext[1:],  # Remove dot
                    'compressed': True
                })
                
        except Exception as e:
            raise MetadataException(f"Error extracting archive metadata: {str(e)}")
        
        return metadata
    
    def _extract_zip_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract ZIP archive metadata."""
        metadata = {}
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.filelist
                
                total_files = len(file_list)
                total_compressed_size = sum(info.compress_size for info in file_list)
                total_uncompressed_size = sum(info.file_size for info in file_list)
                
                # File type distribution
                file_types = {}
                for info in file_list:
                    if not info.is_dir():
                        ext = Path(info.filename).suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                
                metadata.update({
                    'archive_type': 'zip',
                    'total_files': total_files,
                    'total_compressed_size': total_compressed_size,
                    'total_uncompressed_size': total_uncompressed_size,
                    'compression_ratio': (
                        (total_uncompressed_size - total_compressed_size) / 
                        total_uncompressed_size * 100
                        if total_uncompressed_size > 0 else 0
                    ),
                    'file_types': file_types
                })
                
                # List first few files as preview
                preview_files = [
                    info.filename for info in file_list[:10] 
                    if not info.is_dir()
                ]
                if preview_files:
                    metadata['preview_files'] = preview_files
                    
        except Exception as e:
            raise MetadataException(f"Error extracting ZIP metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return supported archive formats."""
        return ['zip', '7z', 'rar', 'tar', 'gz']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "ArchiveMetadataExtractor"


class VideoMetadataExtractor(MetadataExtractor):
    """Extractor for video metadata."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if file is a supported video format."""
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        return Path(file_path).suffix.lower() in video_extensions
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video metadata."""
        metadata = {}
        
        try:
            # Basic video file info
            file_stat = os.stat(file_path)
            metadata.update({
                'video_format': Path(file_path).suffix[1:].upper(),
                'file_size_mb': file_stat.st_size / (1024 * 1024)
            })
            
            # If mutagen is available, try to extract video metadata
            if HAS_MUTAGEN:
                try:
                    video_file = mutagen.File(file_path)
                    if video_file and hasattr(video_file, 'info'):
                        info = video_file.info
                        metadata.update({
                            'duration_seconds': getattr(info, 'length', 0),
                            'bitrate': getattr(info, 'bitrate', 0)
                        })
                except Exception:
                    pass
                    
        except Exception as e:
            raise MetadataException(f"Error extracting video metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return supported video formats."""
        return ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "VideoMetadataExtractor"


class BasicFileMetadataExtractor(MetadataExtractor):
    """Fallback extractor for basic file metadata."""
    
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Can extract metadata from any file."""
        return True
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata."""
        metadata = {}
        
        try:
            file_path_obj = Path(file_path)
            file_stat = file_path_obj.stat()
            
            metadata.update({
                'file_name': file_path_obj.name,
                'file_extension': file_path_obj.suffix.lower(),
                'file_size': file_stat.st_size,
                'created_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(file_stat.st_atime).isoformat(),
                'is_directory': file_path_obj.is_dir(),
                'is_file': file_path_obj.is_file(),
                'is_symlink': file_path_obj.is_symlink()
            })
            
            # MIME type detection
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                metadata['mime_type'] = mime_type
                
        except Exception as e:
            raise MetadataException(f"Error extracting basic metadata: {str(e)}")
        
        return metadata
    
    @property
    def supported_formats(self) -> List[str]:
        """Return all formats (fallback)."""
        return ['*']
    
    @property
    def extractor_name(self) -> str:
        """Return extractor name."""
        return "BasicFileMetadataExtractor"


class MetadataExtractionPipeline:
    """
    Main metadata extraction pipeline that coordinates multiple extractors.
    
    Provides extensible framework for metadata extraction with caching,
    error handling, and performance monitoring.
    """
    
    def __init__(
        self,
        cache_db_path: Optional[str] = None,
        max_cache_entries: int = 10000,
        enable_async_processing: bool = True,
        max_worker_threads: int = 4
    ):
        """
        Initialize metadata extraction pipeline.
        
        Args:
            cache_db_path: Path to cache database
            max_cache_entries: Maximum cached entries
            enable_async_processing: Enable asynchronous processing
            max_worker_threads: Maximum worker threads
        """
        self.cache_db_path = cache_db_path
        self.max_cache_entries = max_cache_entries
        self.enable_async_processing = enable_async_processing
        self.max_worker_threads = max_worker_threads
        
        # Initialize extractors
        self.extractors: List[MetadataExtractor] = [
            ImageMetadataExtractor(),
            AudioMetadataExtractor(),
            DocumentMetadataExtractor(),
            ArchiveMetadataExtractor(),
            VideoMetadataExtractor(),
            BasicFileMetadataExtractor()  # Fallback - must be last
        ]
        
        # Statistics and monitoring
        self.statistics = ExtractionStatistics()
        self._lock = threading.RLock()
        
        # Cache initialization
        if self.cache_db_path:
            self._init_cache_database()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, file_path: str, force_refresh: bool = False) -> MetadataEntry:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to file
            force_refresh: Force extraction even if cached
            
        Returns:
            MetadataEntry with extracted metadata
        """
        start_time = datetime.now()
        
        # Check cache first (if not forcing refresh)
        if not force_refresh and self.cache_db_path:
            cached_entry = self._get_cached_metadata(file_path)
            if cached_entry:
                return cached_entry
        
        # Get file info
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise MetadataException(f"File not found: {file_path}")
            
            file_size = file_path_obj.stat().st_size
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            
        except Exception as e:
            raise MetadataException(f"Error accessing file: {str(e)}")
        
        # Find appropriate extractor
        extractor = self._find_extractor(file_path, mime_type)
        
        # Extract metadata
        metadata = {}
        extraction_method = ""
        errors = []
        
        try:
            metadata = extractor.extract_metadata(file_path)
            extraction_method = extractor.extractor_name
            success = True
            
        except Exception as e:
            errors.append(str(e))
            extraction_method = f"{extractor.extractor_name} (failed)"
            success = False
            self.logger.warning(f"Metadata extraction failed for {file_path}: {str(e)}")
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Create metadata entry
        entry = MetadataEntry(
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            extracted_time=end_time,
            metadata=metadata,
            extraction_method=extraction_method,
            extraction_duration_ms=processing_time_ms,
            errors=errors
        )
        
        # Update statistics
        file_format = Path(file_path).suffix.lower() or 'unknown'
        error_type = type(errors[0]).__name__ if errors else None
        
        with self._lock:
            self.statistics.update_stats(
                success, processing_time_ms, file_format, error_type
            )
        
        # Cache the result
        if self.cache_db_path:
            self._cache_metadata(entry)
        
        return entry
    
    def extract_batch_metadata(
        self, 
        file_paths: List[str], 
        progress_callback: Optional[callable] = None
    ) -> List[MetadataEntry]:
        """
        Extract metadata from multiple files.
        
        Args:
            file_paths: List of file paths
            progress_callback: Optional progress callback function
            
        Returns:
            List of MetadataEntry objects
        """
        results = []
        
        if self.enable_async_processing and len(file_paths) > 1:
            # Use threading for batch processing
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_worker_threads
            ) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self.extract_metadata, path): path 
                    for path in file_paths
                }
                
                # Collect results
                completed = 0
                for future in concurrent.futures.as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error processing {path}: {str(e)}")
                        # Create error entry
                        error_entry = MetadataEntry(
                            file_path=path,
                            file_size=0,
                            mime_type="unknown",
                            extracted_time=datetime.now(),
                            metadata={},
                            extraction_method="BatchProcessing (failed)",
                            extraction_duration_ms=0,
                            errors=[str(e)]
                        )
                        results.append(error_entry)
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, len(file_paths))
        else:
            # Sequential processing
            for i, path in enumerate(file_paths):
                try:
                    result = self.extract_metadata(path)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {path}: {str(e)}")
                    error_entry = MetadataEntry(
                        file_path=path,
                        file_size=0,
                        mime_type="unknown",
                        extracted_time=datetime.now(),
                        metadata={},
                        extraction_method="SequentialProcessing (failed)",
                        extraction_duration_ms=0,
                        errors=[str(e)]
                    )
                    results.append(error_entry)
                
                if progress_callback:
                    progress_callback(i + 1, len(file_paths))
        
        return results
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get all supported formats by extractor."""
        formats = {}
        for extractor in self.extractors:
            formats[extractor.extractor_name] = extractor.supported_formats
        return formats
    
    def get_statistics(self) -> ExtractionStatistics:
        """Get extraction statistics."""
        with self._lock:
            return self.statistics
    
    def clear_cache(self) -> int:
        """Clear metadata cache and return number of entries removed."""
        if not self.cache_db_path:
            return 0
        
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM metadata_cache")
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM metadata_cache")
                return count
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return 0
    
    def _find_extractor(self, file_path: str, mime_type: str) -> MetadataExtractor:
        """Find appropriate extractor for file."""
        for extractor in self.extractors:
            if extractor.can_extract(file_path, mime_type):
                return extractor
        
        # Should never reach here since BasicFileMetadataExtractor handles all files
        return self.extractors[-1]  # Fallback to basic extractor
    
    def _get_cached_metadata(self, file_path: str) -> Optional[MetadataEntry]:
        """Get cached metadata entry."""
        if not self.cache_db_path:
            return None
        
        try:
            # Get file modification time for cache validation
            file_mtime = os.path.getmtime(file_path)
            
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM metadata_cache 
                    WHERE file_path = ? AND file_mtime = ?
                    """,
                    (file_path, file_mtime)
                )
                row = cursor.fetchone()
                
                if row:
                    # Update access time
                    conn.execute(
                        """
                        UPDATE metadata_cache 
                        SET last_accessed = CURRENT_TIMESTAMP 
                        WHERE file_path = ?
                        """,
                        (file_path,)
                    )
                    
                    # Reconstruct MetadataEntry
                    return MetadataEntry(
                        file_path=row['file_path'],
                        file_size=row['file_size'],
                        mime_type=row['mime_type'],
                        extracted_time=datetime.fromisoformat(row['extracted_time']),
                        metadata=json.loads(row['metadata_json']),
                        extraction_method=row['extraction_method'],
                        extraction_duration_ms=row['extraction_duration_ms'],
                        errors=json.loads(row['errors_json']) if row['errors_json'] else []
                    )
                    
        except Exception as e:
            self.logger.warning(f"Error retrieving cached metadata: {str(e)}")
        
        return None
    
    def _cache_metadata(self, entry: MetadataEntry) -> None:
        """Cache metadata entry."""
        if not self.cache_db_path:
            return
        
        try:
            file_mtime = os.path.getmtime(entry.file_path)
            
            with sqlite3.connect(self.cache_db_path) as conn:
                # Check cache size and clean if necessary
                cursor = conn.execute("SELECT COUNT(*) FROM metadata_cache")
                cache_size = cursor.fetchone()[0]
                
                if cache_size >= self.max_cache_entries:
                    # Remove oldest entries
                    entries_to_remove = cache_size - self.max_cache_entries + 1
                    conn.execute(
                        """
                        DELETE FROM metadata_cache 
                        WHERE file_path IN (
                            SELECT file_path FROM metadata_cache 
                            ORDER BY last_accessed ASC 
                            LIMIT ?
                        )
                        """,
                        (entries_to_remove,)
                    )
                
                # Insert or replace entry
                conn.execute(
                    """
                    INSERT OR REPLACE INTO metadata_cache
                    (file_path, file_size, file_mtime, mime_type, extracted_time,
                     metadata_json, extraction_method, extraction_duration_ms,
                     errors_json, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        entry.file_path,
                        entry.file_size,
                        file_mtime,
                        entry.mime_type,
                        entry.extracted_time.isoformat(),
                        json.dumps(entry.metadata, default=str),
                        entry.extraction_method,
                        entry.extraction_duration_ms,
                        json.dumps(entry.errors) if entry.errors else None
                    )
                )
                
        except Exception as e:
            self.logger.warning(f"Error caching metadata: {str(e)}")
    
    def _init_cache_database(self) -> None:
        """Initialize cache database schema."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS metadata_cache (
                        file_path TEXT PRIMARY KEY,
                        file_size INTEGER NOT NULL,
                        file_mtime REAL NOT NULL,
                        mime_type TEXT NOT NULL,
                        extracted_time TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        extraction_method TEXT NOT NULL,
                        extraction_duration_ms REAL NOT NULL,
                        errors_json TEXT,
                        last_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
                        created_time TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_metadata_cache_mtime 
                        ON metadata_cache(file_mtime);
                    CREATE INDEX IF NOT EXISTS idx_metadata_cache_accessed 
                        ON metadata_cache(last_accessed);
                    CREATE INDEX IF NOT EXISTS idx_metadata_cache_mime 
                        ON metadata_cache(mime_type);
                    """
                )
        except Exception as e:
            raise MetadataException(
                f"Error initializing cache database: {str(e)}",
                context={'db_path': self.cache_db_path}
            )


# Factory functions and utilities

def create_metadata_pipeline(
    cache_enabled: bool = True,
    cache_path: Optional[str] = None,
    **kwargs
) -> MetadataExtractionPipeline:
    """
    Create a configured metadata extraction pipeline.
    
    Args:
        cache_enabled: Enable metadata caching
        cache_path: Custom cache database path
        **kwargs: Additional pipeline configuration
        
    Returns:
        Configured MetadataExtractionPipeline
    """
    if cache_enabled and not cache_path:
        cache_path = "metadata_cache.db"
    elif not cache_enabled:
        cache_path = None
    
    return MetadataExtractionPipeline(cache_db_path=cache_path, **kwargs)


def get_file_metadata_summary(metadata_entry: MetadataEntry) -> Dict[str, Any]:
    """
    Get a summarized view of file metadata for display purposes.
    
    Args:
        metadata_entry: MetadataEntry to summarize
        
    Returns:
        Summarized metadata dictionary
    """
    summary = {
        'file_path': metadata_entry.file_path,
        'file_size': metadata_entry.file_size,
        'mime_type': metadata_entry.mime_type,
        'extraction_method': metadata_entry.extraction_method,
        'has_errors': bool(metadata_entry.errors)
    }
    
    # Extract key metadata fields
    metadata = metadata_entry.metadata
    
    # Image metadata
    if 'width' in metadata and 'height' in metadata:
        summary['dimensions'] = f"{metadata['width']}x{metadata['height']}"
    
    # Audio/Video duration
    if 'duration_seconds' in metadata:
        duration = metadata['duration_seconds']
        if duration > 0:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            summary['duration'] = f"{minutes}:{seconds:02d}"
    
    # Document page count
    if 'page_count' in metadata:
        summary['pages'] = metadata['page_count']
    
    # Word count for documents
    if 'word_count' in metadata:
        summary['words'] = metadata['word_count']
    
    # Archive file count
    if 'total_files' in metadata:
        summary['archive_files'] = metadata['total_files']
    
    # EXIF data preview
    if 'exif' in metadata and metadata['exif']:
        exif_summary = {}
        exif_data = metadata['exif']
        
        # Common EXIF fields
        for field in ['Make', 'Model', 'DateTime', 'Flash', 'FocalLength']:
            if field in exif_data:
                exif_summary[field] = exif_data[field]
        
        if exif_summary:
            summary['exif_preview'] = exif_summary
    
    return summary