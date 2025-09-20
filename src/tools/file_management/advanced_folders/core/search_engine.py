"""
Search engine for Advanced Folders feature.

This module provides comprehensive file search functionality including:
- Multi-criteria search operations
- Content-based search with indexing
- Real-time file system monitoring
- Performance optimization and caching
"""

import hashlib
import logging
import mimetypes
import os
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Callable, Dict, Generator, List, Optional, Set

from .folder_configuration import FolderConfiguration, SearchParameters


@dataclass
class FileResult:
    """Result of a file search operation."""
    
    file_path: Path
    file_name: str
    file_size: int
    file_type: str
    mime_type: Optional[str]
    created_date: datetime
    modified_date: datetime
    accessed_date: datetime
    is_directory: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_preview: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'accessed_date': self.accessed_date.isoformat(),
            'is_directory': self.is_directory,
            'metadata': self.metadata,
            'content_preview': self.content_preview
        }


@dataclass
class SearchProgress:
    """Progress information for search operations."""
    
    current_file: str = ""
    files_processed: int = 0
    total_files: int = 0
    directories_processed: int = 0
    matches_found: int = 0
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    is_complete: bool = False
    error_message: str = ""


class SearchCache:
    """Cache for search results with TTL."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """Initialize cache.
        
        Args:
            max_size: Maximum number of cached results
            ttl_seconds: Time to live for cached results
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def _generate_cache_key(self, params: SearchParameters,
                           directories: List[str]) -> str:
        """Generate cache key from search parameters."""
        key_data = {
            'params': params.to_dict(),
            'directories': sorted(directories)
        }
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, params: SearchParameters,
            directories: List[str]) -> Optional[List[FileResult]]:
        """Get cached results if available and not expired."""
        cache_key = self._generate_cache_key(params, directories)
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                # Check if expired
                if time.time() - entry['timestamp'] > self.ttl_seconds:
                    del self._cache[cache_key]
                    return None
                
                return entry['results']
        
        return None
    
    def put(self, params: SearchParameters, directories: List[str],
            results: List[FileResult]):
        """Cache search results."""
        cache_key = self._generate_cache_key(params, directories)
        
        with self._lock:
            # Remove oldest entries if cache is full
            while len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k]['timestamp']
                )
                del self._cache[oldest_key]
            
            self._cache[cache_key] = {
                'results': results,
                'timestamp': time.time()
            }
    
    def clear(self):
        """Clear all cached results."""
        with self._lock:
            self._cache.clear()


class FileIndexer:
    """File indexer for content-based searching."""
    
    def __init__(self):
        """Initialize the file indexer."""
        self.logger = logging.getLogger('AdvancedFolders.FileIndexer')
        self._content_index: Dict[str, Set[str]] = {}
        self._index_lock = threading.Lock()
        
        # Supported text file extensions for content indexing
        self.text_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.html', '.htm',
            '.css', '.xml', '.json', '.yaml', '.yml', '.ini',
            '.cfg', '.conf', '.log'
        }
    
    def should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed for content search."""
        return file_path.suffix.lower() in self.text_extensions
    
    def extract_content(self, file_path: Path,
                       max_size: int = 1024 * 1024) -> str:
        """Extract text content from file for indexing.
        
        Args:
            file_path: Path to file
            max_size: Maximum file size to index (bytes)
            
        Returns:
            Extracted text content
        """
        try:
            if file_path.stat().st_size > max_size:
                return ""
            
            # Try to read as text with common encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            return ""
            
        except Exception as e:
            self.logger.debug(f"Failed to extract content from {file_path}: {e}")
            return ""
    
    def index_file(self, file_path: Path) -> bool:
        """Index a file for content search.
        
        Args:
            file_path: Path to file to index
            
        Returns:
            bool: True if file was indexed successfully
        """
        if not self.should_index_file(file_path):
            return False
        
        try:
            content = self.extract_content(file_path)
            if content:
                # Tokenize content
                words = set(re.findall(r'\b\w+\b', content.lower()))
                
                with self._index_lock:
                    file_str = str(file_path)
                    for word in words:
                        if word not in self._content_index:
                            self._content_index[word] = set()
                        self._content_index[word].add(file_str)
                
                return True
            
        except Exception as e:
            self.logger.debug(f"Failed to index {file_path}: {e}")
        
        return False
    
    def search_content(self, search_term: str) -> Set[str]:
        """Search for files containing the specified term.
        
        Args:
            search_term: Term to search for
            
        Returns:
            Set of file paths containing the term
        """
        search_term = search_term.lower()
        
        with self._index_lock:
            return self._content_index.get(search_term, set())
    
    def remove_file(self, file_path: Path):
        """Remove file from index.
        
        Args:
            file_path: Path to file to remove
        """
        file_str = str(file_path)
        
        with self._index_lock:
            # Remove file from all word sets
            for word_set in self._content_index.values():
                word_set.discard(file_str)
            
            # Clean up empty word entries
            empty_words = [
                word for word, files in self._content_index.items()
                if not files
            ]
            for word in empty_words:
                del self._content_index[word]


class SearchEngine:
    """Main search engine for Advanced Folders."""
    
    def __init__(self, enable_caching: bool = True):
        """Initialize the search engine.
        
        Args:
            enable_caching: Whether to enable result caching
        """
        self.logger = logging.getLogger('AdvancedFolders.SearchEngine')
        self.enable_caching = enable_caching
        self.cache = SearchCache() if enable_caching else None
        self.indexer = FileIndexer()
        self._cancel_flag = threading.Event()
        self._search_lock = threading.Lock()
        
        # Progress tracking
        self.progress_callback: Optional[Callable[[SearchProgress], None]] = None
    
    def set_progress_callback(self,
                            callback: Callable[[SearchProgress], None]):
        """Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def cancel_search(self):
        """Cancel current search operation."""
        self._cancel_flag.set()
    
    def _update_progress(self, progress: SearchProgress):
        """Update search progress.
        
        Args:
            progress: Progress information
        """
        if self.progress_callback:
            self.progress_callback(progress)
    
    def _matches_pattern(self, filename: str, pattern: str,
                        use_regex: bool, case_sensitive: bool) -> bool:
        """Check if filename matches pattern.
        
        Args:
            filename: Filename to check
            pattern: Pattern to match against
            use_regex: Whether pattern is a regular expression
            case_sensitive: Whether matching is case sensitive
            
        Returns:
            bool: True if filename matches pattern
        """
        if not pattern:
            return True
        
        if not case_sensitive:
            filename = filename.lower()
            pattern = pattern.lower()
        
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, filename, flags))
            except re.error:
                # Fallback to literal match if regex is invalid
                return pattern in filename
        else:
            return pattern in filename
    
    def _matches_size_filter(self, file_size: int,
                           size_min: Optional[int],
                           size_max: Optional[int]) -> bool:
        """Check if file size matches filter criteria.
        
        Args:
            file_size: File size in bytes
            size_min: Minimum size filter
            size_max: Maximum size filter
            
        Returns:
            bool: True if file size matches filter
        """
        if size_min is not None and file_size < size_min:
            return False
        if size_max is not None and file_size > size_max:
            return False
        return True
    
    def _matches_date_filter(self, file_stat: os.stat_result,
                           params: SearchParameters) -> bool:
        """Check if file dates match filter criteria.
        
        Args:
            file_stat: File stat object
            params: Search parameters
            
        Returns:
            bool: True if file dates match filter
        """
        if params.date_from is None and params.date_to is None:
            return True
        
        # Get relevant timestamp
        if params.date_criteria == "created":
            file_time = datetime.fromtimestamp(file_stat.st_ctime)
        elif params.date_criteria == "accessed":
            file_time = datetime.fromtimestamp(file_stat.st_atime)
        else:  # modified (default)
            file_time = datetime.fromtimestamp(file_stat.st_mtime)
        
        if params.date_from and file_time < params.date_from:
            return False
        if params.date_to and file_time > params.date_to:
            return False
        
        return True
    
    def _matches_type_filter(self, file_path: Path,
                           params: SearchParameters) -> bool:
        """Check if file type matches filter criteria.
        
        Args:
            file_path: Path to file
            params: Search parameters
            
        Returns:
            bool: True if file type matches filter
        """
        file_ext = file_path.suffix.lower()
        
        # Check exclude list first
        if file_ext in params.exclude_extensions:
            return False
        
        # Check include list
        if params.include_extensions and file_ext not in params.include_extensions:
            return False
        
        # Check MIME types if specified
        if params.include_mime_types:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type not in params.include_mime_types:
                return False
        
        return True
    
    def _search_directory(self, directory: Path, params: SearchParameters,
                         progress: SearchProgress) -> Generator[FileResult, None, None]:
        """Search a single directory.
        
        Args:
            directory: Directory to search
            params: Search parameters
            progress: Progress tracker
            
        Yields:
            FileResult: Matching files
        """
        try:
            if not directory.exists():
                self.logger.warning(f"Directory does not exist: {directory}")
                return
            
            # Use os.walk for efficient traversal
            for root, dirs, files in os.walk(directory):
                if self._cancel_flag.is_set():
                    break
                
                root_path = Path(root)
                progress.current_file = str(root_path)
                progress.directories_processed += 1
                
                # Check search depth
                if params.search_depth >= 0:
                    depth = len(root_path.parts) - len(directory.parts)
                    if depth > params.search_depth:
                        dirs.clear()  # Don't descend further
                        continue
                
                # Filter hidden directories if not requested
                if not params.include_hidden_files:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Process files
                for filename in files:
                    if self._cancel_flag.is_set():
                        break
                    
                    if progress.matches_found >= params.max_results:
                        return
                    
                    file_path = root_path / filename
                    progress.files_processed += 1
                    
                    # Skip hidden files if not requested
                    if not params.include_hidden_files and filename.startswith('.'):
                        continue
                    
                    try:
                        file_stat = file_path.stat()
                        
                        # Apply filters
                        if not self._matches_pattern(
                            filename, params.filename_pattern,
                            params.use_regex, params.case_sensitive
                        ):
                            continue
                        
                        if not self._matches_size_filter(
                            file_stat.st_size, params.size_min, params.size_max
                        ):
                            continue
                        
                        if not self._matches_date_filter(file_stat, params):
                            continue
                        
                        if not self._matches_type_filter(file_path, params):
                            continue
                        
                        # Content search if specified
                        if params.content_search:
                            if not self._search_file_content(file_path, params):
                                continue
                        
                        # Create result
                        mime_type, _ = mimetypes.guess_type(str(file_path))
                        
                        result = FileResult(
                            file_path=file_path,
                            file_name=filename,
                            file_size=file_stat.st_size,
                            file_type=file_path.suffix.lower(),
                            mime_type=mime_type,
                            created_date=datetime.fromtimestamp(file_stat.st_ctime),
                            modified_date=datetime.fromtimestamp(file_stat.st_mtime),
                            accessed_date=datetime.fromtimestamp(file_stat.st_atime),
                            is_directory=False
                        )
                        
                        progress.matches_found += 1
                        yield result
                        
                    except (OSError, PermissionError) as e:
                        self.logger.debug(f"Cannot access file {file_path}: {e}")
                        continue
                
                self._update_progress(progress)
                
        except Exception as e:
            self.logger.error(f"Error searching directory {directory}: {e}")
            progress.error_message = str(e)
    
    def _search_file_content(self, file_path: Path,
                           params: SearchParameters) -> bool:
        """Search file content for specified term.
        
        Args:
            file_path: Path to file
            params: Search parameters
            
        Returns:
            bool: True if file contains search term
        """
        if not params.content_search:
            return True
        
        # Use index if available
        if params.index_content:
            matching_files = self.indexer.search_content(params.content_search)
            return str(file_path) in matching_files
        
        # Direct content search
        if not self.indexer.should_index_file(file_path):
            return False
        
        try:
            content = self.indexer.extract_content(file_path)
            if not params.case_sensitive:
                content = content.lower()
                search_term = params.content_search.lower()
            else:
                search_term = params.content_search
            
            return search_term in content
            
        except Exception as e:
            self.logger.debug(f"Failed to search content in {file_path}: {e}")
            return False
    
    def search(self, config: FolderConfiguration) -> List[FileResult]:
        """Execute search based on folder configuration.
        
        Args:
            config: Folder configuration with search parameters
            
        Returns:
            List of FileResult objects
        """
        with self._search_lock:
            self._cancel_flag.clear()
            
            # Check cache first
            if self.enable_caching and self.cache:
                cached_results = self.cache.get(
                    config.search_parameters, config.directory_paths
                )
                if cached_results is not None:
                    self.logger.debug("Returning cached search results")
                    return cached_results
            
            # Initialize progress
            progress = SearchProgress()
            start_time = time.time()
            
            # Collect results
            results = []
            
            try:
                for directory_path in config.directory_paths:
                    if self._cancel_flag.is_set():
                        break
                    
                    directory = Path(directory_path)
                    
                    for result in self._search_directory(
                        directory, config.search_parameters, progress
                    ):
                        results.append(result)
                        
                        if len(results) >= config.search_parameters.max_results:
                            break
                    
                    if len(results) >= config.search_parameters.max_results:
                        break
                
                # Final progress update
                progress.elapsed_time = time.time() - start_time
                progress.is_complete = True
                self._update_progress(progress)
                
                # Cache results
                if self.enable_caching and self.cache and not self._cancel_flag.is_set():
                    self.cache.put(
                        config.search_parameters, config.directory_paths, results
                    )
                
                self.logger.info(
                    f"Search completed: {len(results)} results in "
                    f"{progress.elapsed_time:.2f} seconds"
                )
                
                return results
                
            except Exception as e:
                self.logger.error(f"Search failed: {e}")
                progress.error_message = str(e)
                progress.is_complete = True
                self._update_progress(progress)
                return []
    
    def async_search(self, config: FolderConfiguration,
                    result_callback: Callable[[List[FileResult]], None],
                    progress_callback: Optional[Callable[[SearchProgress], None]] = None):
        """Execute search asynchronously.
        
        Args:
            config: Folder configuration
            result_callback: Callback for search results
            progress_callback: Optional progress callback
        """
        if progress_callback:
            self.set_progress_callback(progress_callback)
        
        def search_worker():
            """Worker function for async search."""
            results = self.search(config)
            result_callback(results)
        
        thread = threading.Thread(target=search_worker, daemon=True)
        thread.start()
    
    def index_directories(self, directories: List[str]):
        """Index directories for content search.
        
        Args:
            directories: List of directory paths to index
        """
        self.logger.info(f"Starting indexing of {len(directories)} directories")
        
        for directory_path in directories:
            directory = Path(directory_path)
            
            if not directory.exists():
                continue
            
            for root, _, files in os.walk(directory):
                for filename in files:
                    file_path = Path(root) / filename
                    
                    if self.indexer.should_index_file(file_path):
                        self.indexer.index_file(file_path)
        
        self.logger.info("Directory indexing completed")
    
    def clear_cache(self):
        """Clear search result cache."""
        if self.cache:
            self.cache.clear()
            self.logger.info("Search cache cleared")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache:
            return {}
        
        with self.cache._lock:
            return {
                'cache_size': len(self.cache._cache),
                'max_cache_size': self.cache.max_size,
                'cache_ttl': self.cache.ttl_seconds,
                'cached_searches': list(self.cache._cache.keys())
            }