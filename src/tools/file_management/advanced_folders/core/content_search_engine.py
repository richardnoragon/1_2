"""
Content-Based Search Engine for Advanced Folders - Week 7 Implementation.

This module provides comprehensive content-based search capabilities with
full-text indexing, metadata extraction, and advanced query processing
following enterprise principal engineer standards.

Features:
- Full-text content indexing with multiple engines
- Binary file metadata extraction
- Content type detection and handling
- Incremental content updates
- Memory-efficient streaming
- Search result highlighting
- Content relevance scoring
- Enterprise security compliance
"""

import hashlib
import logging
import mimetypes
import re
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

try:
    import chardet

    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from whoosh import fields, index
    from whoosh.analysis import StandardAnalyzer
    from whoosh.qparser import QueryParser
    from whoosh.query import And, Or, Term

    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

from config.config_manager import get_config_manager
from file_validator import detect_file_type, validate_file_type
from file_validator.models import ValidationResult
from file_validator.utils import canonicalise_allowed_types
from rfu.hub import dispatch_validator_result

from ..exceptions.advanced_folders_exceptions import (
    PerformanceException,
    SearchException,
)
from .file_system_scanner import FileInfo


VALIDATOR_WORKFLOW_NAME = "advanced_folders.content_index"

DEFAULT_VALIDATOR_ALLOWED_TYPES = {
    "pdf",
    "docx",
    "pptx",
    "xlsx",
    "epub",
    "zip",
    "text",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "json",
    "xml",
    "csv",
    "html",
    "css",
    "javascript",
    "markdown",
    "application/json",
    "application/xml",
    "application/pdf",
    "application/zip",
    "application/epub+zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/html",
    "text/xml",
    "text/csv",
    "text/markdown",
    "text/x-python",
    "text/x-c",
    "application/javascript",
    "image/png",
    "image/jpeg",
    "image/gif",
}


class ContentIndexingStrategy(Enum):
    """Content indexing strategies for different use cases."""

    FULL_TEXT = "full_text"  # Index complete file contents
    METADATA_ONLY = "metadata_only"  # Index file metadata only
    SELECTIVE = "selective"  # Index based on file type/size rules
    HYBRID = "hybrid"  # Combination of strategies


class ContentExtractionMode(Enum):
    """Content extraction modes for different file types."""

    TEXT_ONLY = "text_only"  # Extract plain text content
    METADATA_ONLY = "metadata_only"  # Extract metadata only
    STRUCTURED = "structured"  # Extract structured data
    BINARY_SAFE = "binary_safe"  # Safe extraction for binary files


@dataclass
class ContentExtractorConfig:
    """Configuration for content extraction operations."""

    max_file_size_mb: float = 50.0
    max_text_length: int = 1000000
    timeout_seconds: float = 30.0
    encoding_detection: bool = True
    fallback_encoding: str = "utf-8"
    extract_metadata: bool = True
    chunk_size_kb: int = 64
    supported_mime_types: Set[str] = field(
        default_factory=lambda: {
            "text/plain",
            "text/html",
            "text/xml",
            "text/csv",
            "application/json",
            "application/xml",
            "text/markdown",
            "text/x-python",
            "text/x-c",
            "application/javascript",
            "text/css",
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "max_file_size_mb": self.max_file_size_mb,
            "max_text_length": self.max_text_length,
            "timeout_seconds": self.timeout_seconds,
            "encoding_detection": self.encoding_detection,
            "fallback_encoding": self.fallback_encoding,
            "extract_metadata": self.extract_metadata,
            "chunk_size_kb": self.chunk_size_kb,
            "supported_mime_types": list(self.supported_mime_types),
        }


@dataclass
class ContentExtractionResult:
    """Result of content extraction operation."""

    file_path: str
    content_type: str
    encoding: Optional[str]
    text_content: str
    metadata: Dict[str, Any]
    extraction_time_ms: float
    content_hash: str
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "file_path": self.file_path,
            "content_type": self.content_type,
            "encoding": self.encoding,
            "text_content": (
                self.text_content[:10000] + "..."
                if len(self.text_content) > 10000
                else self.text_content
            ),
            "metadata": self.metadata,
            "extraction_time_ms": round(self.extraction_time_ms, 2),
            "content_hash": self.content_hash,
            "error_message": self.error_message,
            "warnings": self.warnings.copy(),
        }


class ContentExtractor(ABC):
    """Abstract base class for content extractors."""

    @abstractmethod
    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if this extractor can handle the file."""
        pass

    @abstractmethod
    def extract_content(
        self, file_path: str, config: ContentExtractorConfig
    ) -> ContentExtractionResult:
        """Extract content from the file."""
        pass


class TextContentExtractor(ContentExtractor):
    """Extractor for plain text and text-based files."""

    def __init__(self):
        """Initialize text extractor."""
        self.logger = logging.getLogger("RFU.TextContentExtractor")
        self.supported_types = {
            "text/plain",
            "text/html",
            "text/xml",
            "text/csv",
            "text/markdown",
            "text/x-python",
            "text/x-c",
            "application/javascript",
            "text/css",
            "application/json",
            "application/xml",
        }

    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Check if we can extract text from this file."""
        return mime_type in self.supported_types

    def extract_content(
        self, file_path: str, config: ContentExtractorConfig
    ) -> ContentExtractionResult:
        """Extract text content from file."""
        start_time = time.time()
        file_path_obj = Path(file_path)

        try:
            # Check file size
            file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            if file_size_mb > config.max_file_size_mb:
                raise PerformanceException(
                    f"File too large for extraction: {file_size_mb:.2f}MB",
                    error_code="CONTENT_FILE_TOO_LARGE",
                    context={"file_path": file_path, "size_mb": file_size_mb},
                )

            # Detect encoding
            encoding = self._detect_encoding(file_path_obj, config)

            # Read content
            content = self._read_text_content(file_path_obj, encoding, config)

            # Extract metadata
            metadata = (
                self._extract_text_metadata(content, file_path_obj)
                if config.extract_metadata
                else {}
            )

            # Generate content hash
            content_hash = hashlib.sha256(
                content.encode(encoding or "utf-8")
            ).hexdigest()[:16]

            # Determine content type
            content_type = mimetypes.guess_type(file_path)[0] or "text/plain"

            extraction_time = (time.time() - start_time) * 1000

            return ContentExtractionResult(
                file_path=file_path,
                content_type=content_type,
                encoding=encoding,
                text_content=content,
                metadata=metadata,
                extraction_time_ms=extraction_time,
                content_hash=content_hash,
            )

        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Content extraction failed for {file_path}: {str(e)}"
            )

            return ContentExtractionResult(
                file_path=file_path,
                content_type="unknown",
                encoding=None,
                text_content="",
                metadata={},
                extraction_time_ms=extraction_time,
                content_hash="",
                error_message=str(e),
            )

    def _detect_encoding(
        self, file_path: Path, config: ContentExtractorConfig
    ) -> str:
        """Detect file encoding."""
        if not config.encoding_detection or not CHARDET_AVAILABLE:
            return config.fallback_encoding

        try:
            # Read sample for encoding detection
            with open(file_path, "rb") as f:
                sample = f.read(min(8192, file_path.stat().st_size))

            detection = chardet.detect(sample)
            detected_encoding = detection.get(
                "encoding", config.fallback_encoding
            )
            confidence = detection.get("confidence", 0.0)

            # Use detected encoding if confidence is high enough
            if confidence > 0.7 and detected_encoding:
                return detected_encoding
            else:
                return config.fallback_encoding

        except Exception as e:
            self.logger.warning(
                f"Encoding detection failed for {file_path}: {str(e)}"
            )
            return config.fallback_encoding

    def _read_text_content(
        self, file_path: Path, encoding: str, config: ContentExtractorConfig
    ) -> str:
        """Read text content from file."""
        try:
            with open(
                file_path, "r", encoding=encoding, errors="replace"
            ) as f:
                content = f.read(config.max_text_length)

            # Truncate if necessary
            if len(content) >= config.max_text_length:
                content = content[: config.max_text_length]
                self.logger.warning(f"Content truncated for {file_path}")

            return content

        except UnicodeDecodeError:
            # Fallback to binary mode with error replacement
            with open(file_path, "rb") as f:
                raw_content = f.read(config.max_text_length)

            try:
                return raw_content.decode(encoding, errors="replace")
            except Exception:
                return raw_content.decode(
                    config.fallback_encoding, errors="replace"
                )

    def _extract_text_metadata(
        self, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Extract metadata from text content."""
        metadata = {}

        # Basic statistics
        metadata["character_count"] = len(content)
        metadata["line_count"] = content.count("\n") + 1
        metadata["word_count"] = len(content.split())

        # Language hints (basic)
        if content:
            # Check for common programming language patterns
            if file_path.suffix.lower() in [".py", ".pyw"]:
                metadata["language"] = "python"
                metadata["imports"] = self._extract_python_imports(content)
            elif file_path.suffix.lower() in [".js", ".jsx"]:
                metadata["language"] = "javascript"
            elif file_path.suffix.lower() in [".html", ".htm"]:
                metadata["language"] = "html"
                metadata["title"] = self._extract_html_title(content)
            elif file_path.suffix.lower() in [".css"]:
                metadata["language"] = "css"
            elif file_path.suffix.lower() in [".json"]:
                metadata["language"] = "json"
                metadata["valid_json"] = self._validate_json(content)

        return metadata

    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python import statements."""
        imports = []
        for line in content.split("\n")[:100]:  # Check first 100 lines
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        return imports

    def _extract_html_title(self, content: str) -> Optional[str]:
        """Extract HTML title."""
        try:
            match = re.search(
                r"<title[^>]*>(.*?)</title>",
                content,
                re.IGNORECASE | re.DOTALL,
            )
            return match.group(1).strip() if match else None
        except Exception:
            return None

    def _validate_json(self, content: str) -> bool:
        """Check if content is valid JSON."""
        try:
            import json

            json.loads(content)
            return True
        except Exception:
            return False


class BinaryContentExtractor(ContentExtractor):
    """Extractor for binary files - metadata only."""

    def __init__(self):
        """Initialize binary extractor."""
        self.logger = logging.getLogger("RFU.BinaryContentExtractor")

    def can_extract(self, file_path: str, mime_type: str) -> bool:
        """Binary extractor handles all files as fallback."""
        return True

    def extract_content(
        self, file_path: str, config: ContentExtractorConfig
    ) -> ContentExtractionResult:
        """Extract metadata from binary file."""
        start_time = time.time()
        file_path_obj = Path(file_path)

        try:
            # Extract file metadata
            metadata = self._extract_file_metadata(file_path_obj)

            # Generate file hash for binary files
            content_hash = self._calculate_file_hash(file_path_obj)

            # Determine content type
            content_type = (
                mimetypes.guess_type(file_path)[0]
                or "application/octet-stream"
            )

            extraction_time = (time.time() - start_time) * 1000

            return ContentExtractionResult(
                file_path=file_path,
                content_type=content_type,
                encoding=None,
                text_content="",  # No text content for binary files
                metadata=metadata,
                extraction_time_ms=extraction_time,
                content_hash=content_hash,
            )

        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Binary metadata extraction failed for {file_path}: {str(e)}"
            )

            return ContentExtractionResult(
                file_path=file_path,
                content_type="unknown",
                encoding=None,
                text_content="",
                metadata={},
                extraction_time_ms=extraction_time,
                content_hash="",
                error_message=str(e),
            )

    def _extract_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file system."""
        try:
            stat = file_path.stat()
            metadata = {
                "file_size_bytes": stat.st_size,
                "created_time": datetime.fromtimestamp(
                    stat.st_ctime, tz=timezone.utc
                ).isoformat(),
                "modified_time": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
                "file_extension": file_path.suffix.lower(),
                "file_name": file_path.name,
            }

            # Add magic number detection if available
            if MAGIC_AVAILABLE:
                try:
                    file_type = magic.from_file(str(file_path))
                    metadata["magic_type"] = file_type
                except Exception as e:
                    metadata["magic_error"] = str(e)

            return metadata

        except Exception as e:
            return {"metadata_error": str(e)}

    def _calculate_file_hash(
        self, file_path: Path, chunk_size: int = 8192
    ) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]  # Truncated for storage efficiency
        except Exception:
            return ""


class ContentIndexManager:
    """Manages content indexing with multiple storage backends."""

    def __init__(
        self,
        index_path: str,
        indexing_strategy: ContentIndexingStrategy = ContentIndexingStrategy.HYBRID,
        extractor_config: Optional[ContentExtractorConfig] = None,
        validator_allowed_types: Optional[Iterable[str]] = None,
        validator_mode: Optional[str] = None,
    ):
        """
        Initialize content index manager.

        Args:
            index_path: Path for storing index files
            indexing_strategy: Strategy for content indexing
            extractor_config: Configuration for content extraction
        """
        self.index_path = Path(index_path)
        self.indexing_strategy = indexing_strategy
        self.extractor_config = extractor_config or ContentExtractorConfig()

        policy: Optional[Dict[str, Any]] = None
        try:
            policy = get_config_manager().get_validator_policy(
                VALIDATOR_WORKFLOW_NAME
            )
        except Exception:
            policy = None

        if validator_allowed_types is None:
            allowed_types = (
                policy.get("allowed_types")
                if policy and policy.get("allowed_types")
                else DEFAULT_VALIDATOR_ALLOWED_TYPES
            )
        else:
            allowed_types = validator_allowed_types

        self.validator_allowed_types = canonicalise_allowed_types(
            allowed_types
        )

        if validator_mode is None:
            resolved_mode = (
                policy.get("mode")
                if policy and policy.get("mode")
                else "auto"
            )
        else:
            resolved_mode = validator_mode

        self.validator_mode = resolved_mode
        self.validator_workflow = (
            policy.get("workflow")
            if policy and policy.get("workflow")
            else VALIDATOR_WORKFLOW_NAME
        )

        # Create index directory
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize extractors
        self.extractors: List[ContentExtractor] = [
            TextContentExtractor(),
            BinaryContentExtractor(),  # Fallback extractor
        ]

        # Initialize storage backends
        self._init_storage_backends()

        # Threading for concurrent operations
        self._index_lock = threading.RLock()
        self.max_workers = 4

        # Performance tracking
        self.extraction_stats = {
            "total_files": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_extraction_time_ms": 0.0,
            "blocked_by_validator": 0,
            "validator_warnings": 0,
        }

        self.logger = logging.getLogger("RFU.ContentIndexManager")
        self.logger.info(
            "Content index manager initialized with strategy %s and validator mode %s",
            indexing_strategy.value,
            self.validator_mode,
        )
        self.logger.debug(
            "Validator allowed types for content indexing: %s",
            sorted(self.validator_allowed_types),
        )

    def _init_storage_backends(self) -> None:
        """Initialize storage backends based on availability."""
        # SQLite backend (always available)
        self.db_path = self.index_path / "content_index.db"
        self._init_sqlite_backend()

        # Whoosh backend (if available)
        self.whoosh_index = None
        if WHOOSH_AVAILABLE:
            self._init_whoosh_backend()

    def _init_sqlite_backend(self) -> None:
        """Initialize SQLite storage backend."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_index (
                file_path TEXT PRIMARY KEY,
                content_type TEXT,
                encoding TEXT,
                text_content TEXT,
                metadata_json TEXT,
                content_hash TEXT,
                extraction_time_ms REAL,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_content_type ON content_index(content_type)
        """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_content_hash ON content_index(content_hash)
        """
        )

        # Full-text search table
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
                file_path,
                text_content,
                content_type,
                tokenize=porter
            )
        """
        )

        conn.commit()
        conn.close()

    def _init_whoosh_backend(self) -> None:
        """Initialize Whoosh search backend."""
        try:
            whoosh_dir = self.index_path / "whoosh"
            whoosh_dir.mkdir(exist_ok=True)

            # Define schema
            schema = fields.Schema(
                file_path=fields.ID(stored=True, unique=True),
                text_content=fields.TEXT(
                    analyzer=StandardAnalyzer(), stored=True
                ),
                content_type=fields.TEXT(stored=True),
                metadata=fields.TEXT(stored=True),
                content_hash=fields.ID(stored=True),
            )

            # Create or open index
            if not index.exists_in(str(whoosh_dir)):
                self.whoosh_index = index.create_in(str(whoosh_dir), schema)
            else:
                self.whoosh_index = index.open_dir(str(whoosh_dir))

            self.logger.info("Whoosh backend initialized successfully")

        except Exception as e:
            self.logger.warning(
                f"Failed to initialize Whoosh backend: {str(e)}"
            )
            self.whoosh_index = None

    def _validate_for_index(self, file_path: str) -> Optional[ValidationResult]:
        """Run centralized validator for the supplied file."""
        try:
            return validate_file_type(
                file_path,
                allowed_types=self.validator_allowed_types,
                mode=self.validator_mode,
                workflow=self.validator_workflow,
            )
        except Exception as exc:
            self.logger.error(
                "Validator execution failed for %s: %s",
                file_path,
                exc,
                exc_info=True,
            )
            return None

    def _increment_validator_stats(self, validation: ValidationResult) -> None:
        """Update validator-related statistics."""
        if validation.action == "reject":
            self.extraction_stats["blocked_by_validator"] += 1
        elif validation.action == "warn":
            self.extraction_stats["validator_warnings"] += 1

    def index_file(self, file_info: FileInfo) -> ContentExtractionResult:
        """
        Index a single file's content.

        Args:
            file_info: File information object

        Returns:
            ContentExtractionResult with extraction details
        """
        with self._index_lock:
            # Determine if file should be indexed
            if not self._should_index_file(file_info):
                return ContentExtractionResult(
                    file_path=file_info.path,
                    content_type="skipped",
                    encoding=None,
                    text_content="",
                    metadata={},
                    extraction_time_ms=0.0,
                    content_hash="",
                    warnings=["File skipped due to indexing strategy"],
                )

            validation: Optional[ValidationResult] = None
            validator_metadata: Optional[Dict[str, Any]] = None
            validator_warnings: List[str] = []

            if file_info.is_file:
                validation = self._validate_for_index(file_info.path)
                if validation:
                    validator_metadata = validation.to_dict()
                    if validation.action == "reject":
                        dispatch_validator_result(
                            validation, workflow=self.validator_workflow
                        )
                        self.logger.warning(
                            "File %s rejected by validator (detected=%s, confidence=%s)",
                            file_info.path,
                            validation.detection.detected_type,
                            validation.detection.confidence,
                        )
                        blocked_result = ContentExtractionResult(
                            file_path=file_info.path,
                            content_type="blocked",
                            encoding=None,
                            text_content="",
                            metadata={"validator": validator_metadata},
                            extraction_time_ms=0.0,
                            content_hash="",
                            error_message="Rejected by file validator",
                            warnings=[
                                f"Validator rejection: {validation.reason}"
                            ],
                        )
                        self._increment_validator_stats(validation)
                        self._update_extraction_stats(blocked_result)
                        return blocked_result

                    if validation.action == "warn":
                        validator_warnings.append(
                            "Validator warning (%s): %s"
                            % (
                                validation.detection.detected_type,
                                validation.reason,
                            )
                        )
                        dispatch_validator_result(
                            validation, workflow=self.validator_workflow
                        )
                else:
                    self.logger.debug(
                        "Validator returned no decision for %s; proceeding with indexing",
                        file_info.path,
                    )

            # Find appropriate extractor
            extractor = self._find_extractor(
                file_info.path, file_info.mime_type
            )

            # Extract content
            result = extractor.extract_content(
                file_info.path, self.extractor_config
            )

            if validator_metadata:
                result.metadata["validator"] = validator_metadata
            if validator_warnings:
                result.warnings.extend(validator_warnings)
            if validation:
                self._increment_validator_stats(validation)

            # Store in backends
            self._store_content_result(result)

            # Update statistics
            self._update_extraction_stats(result)

            return result

    def index_files_batch(
        self, file_infos: List[FileInfo]
    ) -> List[ContentExtractionResult]:
        """
        Index multiple files concurrently.

        Args:
            file_infos: List of file information objects

        Returns:
            List of ContentExtractionResult objects
        """
        results = []

        # Filter files that should be indexed
        files_to_index = [f for f in file_infos if self._should_index_file(f)]

        if not files_to_index:
            return []

        # Process files concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.index_file, file_info): file_info
                for file_info in files_to_index
            }

            # Collect results
            for future in as_completed(future_to_file):
                try:
                    result = future.result(
                        timeout=self.extractor_config.timeout_seconds
                    )
                    results.append(result)
                except Exception as e:
                    file_info = future_to_file[future]
                    self.logger.error(
                        f"Failed to index {file_info.path}: {str(e)}"
                    )

                    error_result = ContentExtractionResult(
                        file_path=file_info.path,
                        content_type="error",
                        encoding=None,
                        text_content="",
                        metadata={},
                        extraction_time_ms=0.0,
                        content_hash="",
                        error_message=str(e),
                    )
                    results.append(error_result)

        return results

    def search_content(
        self,
        query: str,
        content_types: Optional[List[str]] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Search indexed content.

        Args:
            query: Search query
            content_types: Optional filter by content types
            max_results: Maximum number of results

        Returns:
            List of search results with relevance scores
        """
        # Try Whoosh first (better full-text search)
        if self.whoosh_index:
            try:
                return self._search_whoosh(query, content_types, max_results)
            except Exception as e:
                self.logger.warning(
                    f"Whoosh search failed, falling back to SQLite: {str(e)}"
                )

        # Fallback to SQLite FTS
        return self._search_sqlite_fts(query, content_types, max_results)

    def _should_index_file(self, file_info: FileInfo) -> bool:
        """Determine if file should be indexed based on strategy."""
        if self.indexing_strategy == ContentIndexingStrategy.METADATA_ONLY:
            # Only index metadata for all files
            return True
        elif self.indexing_strategy == ContentIndexingStrategy.SELECTIVE:
            # Index based on file type and size
            return (
                file_info.mime_type
                in self.extractor_config.supported_mime_types
                and file_info.size_bytes
                < self.extractor_config.max_file_size_mb * 1024 * 1024
            )
        elif self.indexing_strategy == ContentIndexingStrategy.FULL_TEXT:
            # Index all files with content extraction
            return True
        else:  # HYBRID
            # Smart decision based on file characteristics
            if (
                file_info.size_bytes
                > self.extractor_config.max_file_size_mb * 1024 * 1024
            ):
                return False  # Skip very large files

            # Always index text files
            if (
                file_info.mime_type
                in self.extractor_config.supported_mime_types
            ):
                return True

            # Index metadata for other files
            return True

    def _find_extractor(
        self, file_path: str, mime_type: str
    ) -> ContentExtractor:
        """Find appropriate content extractor for file."""
        for extractor in self.extractors:
            if extractor.can_extract(file_path, mime_type):
                return extractor

        # Return last extractor as fallback
        return self.extractors[-1]

    def _store_content_result(self, result: ContentExtractionResult) -> None:
        """Store extraction result in backends."""
        # Store in SQLite
        self._store_sqlite(result)

        # Store in Whoosh if available and content exists
        if self.whoosh_index and result.text_content:
            self._store_whoosh(result)

    def _store_sqlite(self, result: ContentExtractionResult) -> None:
        """Store result in SQLite backend."""
        try:
            import json

            conn = sqlite3.connect(str(self.db_path))

            # Store in main table
            conn.execute(
                """
                INSERT OR REPLACE INTO content_index 
                (file_path, content_type, encoding, text_content, metadata_json, 
                 content_hash, extraction_time_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.file_path,
                    result.content_type,
                    result.encoding,
                    result.text_content,
                    json.dumps(result.metadata),
                    result.content_hash,
                    result.extraction_time_ms,
                    result.error_message,
                ),
            )

            # Store in FTS table if content exists
            if result.text_content and not result.error_message:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO content_fts 
                    (file_path, text_content, content_type)
                    VALUES (?, ?, ?)
                """,
                    (
                        result.file_path,
                        result.text_content,
                        result.content_type,
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to store content in SQLite: {str(e)}")

    def _store_whoosh(self, result: ContentExtractionResult) -> None:
        """Store result in Whoosh backend."""
        try:
            import json

            writer = self.whoosh_index.writer()

            writer.update_document(
                file_path=result.file_path,
                text_content=result.text_content,
                content_type=result.content_type,
                metadata=json.dumps(result.metadata),
                content_hash=result.content_hash,
            )

            writer.commit()

        except Exception as e:
            self.logger.error(f"Failed to store content in Whoosh: {str(e)}")

    def _search_whoosh(
        self, query: str, content_types: Optional[List[str]], max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using Whoosh backend."""
        results = []

        try:
            searcher = self.whoosh_index.searcher()
            parser = QueryParser("text_content", self.whoosh_index.schema)

            # Parse query
            parsed_query = parser.parse(query)

            # Add content type filter if specified
            if content_types:
                type_queries = [
                    Term("content_type", ct) for ct in content_types
                ]
                type_query = Or(type_queries)
                parsed_query = And([parsed_query, type_query])

            # Execute search
            search_results = searcher.search(parsed_query, limit=max_results)

            for hit in search_results:
                results.append(
                    {
                        "file_path": hit["file_path"],
                        "content_type": hit["content_type"],
                        "relevance_score": hit.score,
                        "highlights": hit.highlights("text_content"),
                        "metadata": hit.get("metadata", "{}"),
                    }
                )

            searcher.close()

        except Exception as e:
            self.logger.error(f"Whoosh search error: {str(e)}")
            raise SearchException(
                f"Content search failed: {str(e)}",
                search_query=query,
                error_code="CONTENT_SEARCH_ERROR",
            )

        return results

    def _search_sqlite_fts(
        self, query: str, content_types: Optional[List[str]], max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using SQLite FTS backend."""
        results = []

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            # Build query
            sql_query = "SELECT * FROM content_fts WHERE content_fts MATCH ?"
            params = [query]

            if content_types:
                placeholders = ",".join("?" * len(content_types))
                sql_query += f" AND content_type IN ({placeholders})"
                params.extend(content_types)

            sql_query += " LIMIT ?"
            params.append(max_results)

            # Execute search
            cursor = conn.execute(sql_query, params)

            for row in cursor:
                results.append(
                    {
                        "file_path": row["file_path"],
                        "content_type": row["content_type"],
                        "relevance_score": 1.0,  # SQLite FTS doesn't provide scores
                        "highlights": [],  # Basic FTS doesn't provide highlighting
                        "metadata": "{}",
                    }
                )

            conn.close()

        except Exception as e:
            self.logger.error(f"SQLite FTS search error: {str(e)}")
            raise SearchException(
                f"Content search failed: {str(e)}",
                search_query=query,
                error_code="CONTENT_SEARCH_ERROR",
            )

        return results

    def _update_extraction_stats(
        self, result: ContentExtractionResult
    ) -> None:
        """Update extraction statistics."""
        self.extraction_stats["total_files"] += 1

        if result.error_message:
            self.extraction_stats["failed_extractions"] += 1
        else:
            self.extraction_stats["successful_extractions"] += 1

        self.extraction_stats[
            "total_extraction_time_ms"
        ] += result.extraction_time_ms

    def get_statistics(self) -> Dict[str, Any]:
        """Get content indexing statistics."""
        stats = self.extraction_stats.copy()

        # Add database statistics
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM content_index")
            stats["indexed_files"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM content_fts")
            stats["searchable_files"] = cursor.fetchone()[0]

            # Database size
            db_size_mb = (
                self.db_path.stat().st_size / (1024 * 1024)
                if self.db_path.exists()
                else 0
            )
            stats["database_size_mb"] = round(db_size_mb, 2)

            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")

        # Average extraction time
        if stats["total_files"] > 0:
            stats["avg_extraction_time_ms"] = round(
                stats["total_extraction_time_ms"] / stats["total_files"], 2
            )

        return stats

    def optimize_index(self) -> None:
        """Optimize search indices for better performance."""
        try:
            # Optimize SQLite
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("VACUUM")
            conn.execute("REINDEX")
            conn.commit()
            conn.close()

            # Optimize Whoosh
            if self.whoosh_index:
                self.whoosh_index.optimize()

            self.logger.info("Content index optimization completed")

        except Exception as e:
            self.logger.error(f"Index optimization failed: {str(e)}")

    def clear_index(self) -> None:
        """Clear all indexed content."""
        with self._index_lock:
            try:
                # Clear SQLite
                conn = sqlite3.connect(str(self.db_path))
                conn.execute("DELETE FROM content_index")
                conn.execute("DELETE FROM content_fts")
                conn.commit()
                conn.close()

                # Clear Whoosh
                if self.whoosh_index:
                    writer = self.whoosh_index.writer()
                    writer.commit(mergetype=index.CLEAR)

                # Reset statistics
                self.extraction_stats = {
                    "total_files": 0,
                    "successful_extractions": 0,
                    "failed_extractions": 0,
                    "total_extraction_time_ms": 0.0,
                    "blocked_by_validator": 0,
                    "validator_warnings": 0,
                }

                self.logger.info("Content index cleared successfully")

            except Exception as e:
                self.logger.error(f"Failed to clear content index: {str(e)}")
