"""
Advanced Folders - Search Result Caching System

Enterprise-grade distributed caching layer with TTL management,
cache invalidation policies, and memory optimization strategies
for search performance enhancement.

Features:
- Multi-tier caching (memory + database)
- TTL-based expiration with automatic cleanup
- LRU eviction for memory cache
- Cache invalidation policies
- Cache warming and prefetching
- Performance metrics and monitoring
- Thread-safe operations
- Configurable cache sizes and policies

Author: RFU Development Team
Version: 1.0.0
"""

import hashlib
import json
import sqlite3
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from ..exceptions.advanced_folders_exceptions import (
    CacheException,
    ValidationException,
)
from ..models.folder_configuration import SearchParameters


@dataclass
class CacheEntry:
    """Represents a cached search result entry."""

    key: str
    data: Any
    created_time: datetime
    expires_time: datetime
    access_count: int = 0
    last_access_time: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    folder_id: Optional[UUID] = None
    search_hash: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > self.expires_time

    def is_valid(self) -> bool:
        """Check if cache entry is valid (not expired)."""
        return not self.is_expired()

    def update_access(self) -> None:
        """Update access statistics."""
        self.access_count += 1
        self.last_access_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "created_time": self.created_time.isoformat(),
            "expires_time": self.expires_time.isoformat(),
            "access_count": self.access_count,
            "last_access_time": self.last_access_time.isoformat(),
            "size_bytes": self.size_bytes,
            "folder_id": str(self.folder_id) if self.folder_id else None,
            "search_hash": self.search_hash,
        }


@dataclass
class CacheStatistics:
    """Cache performance statistics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0
    database_entries: int = 0
    average_access_time_ms: float = 0.0
    hit_rate: float = 0.0
    memory_hit_rate: float = 0.0
    database_hit_rate: float = 0.0

    def calculate_hit_rate(self) -> None:
        """Calculate cache hit rate."""
        if self.total_requests > 0:
            self.hit_rate = (self.cache_hits / self.total_requests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "evictions": self.evictions,
            "memory_usage_bytes": self.memory_usage_bytes,
            "database_entries": self.database_entries,
            "average_access_time_ms": self.average_access_time_ms,
            "hit_rate": self.hit_rate,
            "memory_hit_rate": self.memory_hit_rate,
            "database_hit_rate": self.database_hit_rate,
        }


class LRUCache:
    """Thread-safe LRU cache implementation."""

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._current_memory_bytes = 0

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_valid():
                    # Move to end (most recently used)
                    self._cache.move_to_end(key)
                    entry.update_access()
                    return entry
                else:
                    # Remove expired entry
                    self._remove_entry(key)
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Put entry in cache."""
        with self._lock:
            # Calculate entry size
            entry_size = self._calculate_entry_size(entry)
            entry.size_bytes = entry_size

            # Check memory constraints
            if entry_size > self.max_memory_bytes:
                return False

            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)

            # Ensure we have space
            while len(self._cache) >= self.max_size or (
                self._current_memory_bytes + entry_size > self.max_memory_bytes
            ):
                if not self._evict_least_recently_used():
                    return False

            # Add new entry
            self._cache[key] = entry
            self._current_memory_bytes += entry_size
            return True

    def remove(self, key: str) -> bool:
        """Remove entry from cache."""
        with self._lock:
            return self._remove_entry(key)

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._cache.clear()
            self._current_memory_bytes = 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_bytes": self._current_memory_bytes,
                "max_memory_bytes": self.max_memory_bytes,
                "memory_usage_percent": (
                    (self._current_memory_bytes / self.max_memory_bytes) * 100
                    if self.max_memory_bytes > 0
                    else 0
                ),
            }

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                self._remove_entry(key)
            return len(expired_keys)

    def _remove_entry(self, key: str) -> bool:
        """Remove entry and update memory usage."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_memory_bytes -= entry.size_bytes
            return True
        return False

    def _evict_least_recently_used(self) -> bool:
        """Evict least recently used entry."""
        if self._cache:
            key, _ = self._cache.popitem(last=False)
            return True
        return False

    def _calculate_entry_size(self, entry: CacheEntry) -> int:
        """Calculate approximate memory size of entry."""
        try:
            # Serialize data to estimate size
            data_size = len(json.dumps(entry.data, default=str).encode("utf-8"))
            # Add overhead for metadata
            metadata_size = 200  # Approximate overhead
            return data_size + metadata_size
        except Exception:
            # Fallback size estimation
            return 1024  # 1KB default


class DatabaseCache:
    """Database-backed cache implementation."""

    def __init__(self, db_path: str):
        """
        Initialize database cache.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._init_database()

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from database cache."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute(
                        """
                        SELECT cache_key, folder_id, search_hash, results_data,
                               created_date, expires_date, hit_count
                        FROM search_results_cache
                        WHERE cache_key = ?
                        AND expires_date > CURRENT_TIMESTAMP
                        """,
                        (key,),
                    )
                    row = cursor.fetchone()
                    if row:
                        # Update hit count
                        conn.execute(
                            """
                            UPDATE search_results_cache
                            SET hit_count = hit_count + 1
                            WHERE cache_key = ?
                            """,
                            (key,),
                        )

                        # Convert to CacheEntry
                        data = json.loads(row["results_data"])
                        return CacheEntry(
                            key=row["cache_key"],
                            data=data,
                            created_time=datetime.fromisoformat(row["created_date"]),
                            expires_time=datetime.fromisoformat(row["expires_date"]),
                            access_count=row["hit_count"] + 1,
                            folder_id=(
                                UUID(row["folder_id"]) if row["folder_id"] else None
                            ),
                            search_hash=row["search_hash"],
                        )
            except Exception as e:
                raise CacheException(
                    f"Error retrieving cache entry: {str(e)}",
                    context={"key": key, "db_path": str(self.db_path)},
                )
        return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Put entry in database cache."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Serialize data
                    data_json = json.dumps(entry.data, default=str)

                    # Insert or replace entry
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO search_results_cache
                        (cache_key, folder_id, search_hash, results_data,
                         created_date, expires_date, hit_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            entry.key,
                            str(entry.folder_id) if entry.folder_id else None,
                            entry.search_hash,
                            data_json,
                            entry.created_time.isoformat(),
                            entry.expires_time.isoformat(),
                            entry.access_count,
                        ),
                    )
                    return True
            except Exception as e:
                raise CacheException(
                    f"Error storing cache entry: {str(e)}",
                    context={"key": key, "db_path": str(self.db_path)},
                )
        return False

    def remove(self, key: str) -> bool:
        """Remove entry from database cache."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM search_results_cache WHERE cache_key = ?", (key,)
                    )
                    return cursor.rowcount > 0
            except Exception as e:
                raise CacheException(
                    f"Error removing cache entry: {str(e)}", context={"key": key}
                )

    def cleanup_expired(self) -> int:
        """Remove expired entries from database."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM search_results_cache WHERE expires_date <= CURRENT_TIMESTAMP"
                    )
                    return cursor.rowcount
            except Exception as e:
                raise CacheException(f"Error cleaning up expired entries: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get database cache statistics."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Total entries
                    cursor = conn.execute(
                        "SELECT COUNT(*) as total FROM search_results_cache"
                    )
                    total_entries = cursor.fetchone()[0]

                    # Active entries (not expired)
                    cursor = conn.execute(
                        """
                        SELECT COUNT(*) as active
                        FROM search_results_cache
                        WHERE expires_date > CURRENT_TIMESTAMP
                        """
                    )
                    active_entries = cursor.fetchone()[0]

                    # Database size
                    db_size = (
                        self.db_path.stat().st_size if self.db_path.exists() else 0
                    )

                    return {
                        "total_entries": total_entries,
                        "active_entries": active_entries,
                        "expired_entries": total_entries - active_entries,
                        "database_size_bytes": db_size,
                    }
            except Exception as e:
                raise CacheException(f"Error getting cache statistics: {str(e)}")

    def invalidate_folder_cache(self, folder_id: UUID) -> int:
        """Invalidate all cache entries for a specific folder."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM search_results_cache WHERE folder_id = ?",
                        (str(folder_id),),
                    )
                    return cursor.rowcount
            except Exception as e:
                raise CacheException(
                    f"Error invalidating folder cache: {str(e)}",
                    context={"folder_id": str(folder_id)},
                )

    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS search_results_cache (
                        cache_key VARCHAR(255) PRIMARY KEY,
                        folder_id VARCHAR(36),
                        search_hash VARCHAR(64) NOT NULL,
                        results_data TEXT NOT NULL,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        expires_date TEXT NOT NULL,
                        hit_count INTEGER DEFAULT 0
                    );

                    CREATE INDEX IF NOT EXISTS idx_cache_folder
                        ON search_results_cache(folder_id);
                    CREATE INDEX IF NOT EXISTS idx_cache_expires
                        ON search_results_cache(expires_date);
                    CREATE INDEX IF NOT EXISTS idx_cache_hash
                        ON search_results_cache(search_hash);
                    """
                )
        except Exception as e:
            raise CacheException(
                f"Error initializing cache database: {str(e)}",
                context={"db_path": str(self.db_path)},
            )


class SearchResultCache:
    """
    Enterprise-grade search result caching system.

    Provides multi-tier caching with memory and database backends,
    TTL management, cache invalidation policies, and performance optimization.
    """

    def __init__(
        self,
        memory_cache_size: int = 1000,
        memory_cache_mb: int = 100,
        db_cache_path: Optional[str] = None,
        default_ttl_minutes: int = 30,
        cleanup_interval_minutes: int = 15,
        enable_prefetching: bool = True,
        max_entry_size_mb: int = 10,
    ):
        """
        Initialize search result cache.

        Args:
            memory_cache_size: Maximum entries in memory cache
            memory_cache_mb: Maximum memory cache size in MB
            db_cache_path: Path to database cache file
            default_ttl_minutes: Default TTL for cache entries
            cleanup_interval_minutes: Interval for cleanup operations
            enable_prefetching: Enable cache prefetching
            max_entry_size_mb: Maximum size for a single entry
        """
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        self.enable_prefetching = enable_prefetching
        self.max_entry_size_bytes = max_entry_size_mb * 1024 * 1024

        # Initialize caches
        self.memory_cache = LRUCache(memory_cache_size, memory_cache_mb)
        self.database_cache = DatabaseCache(db_cache_path) if db_cache_path else None

        # Statistics
        self.statistics = CacheStatistics()
        self._access_times: List[float] = []
        self._lock = threading.RLock()

        # Background cleanup
        self._last_cleanup = datetime.now()
        self._cleanup_thread = None
        self._shutdown_event = threading.Event()

        # Cache warming sets
        self._warm_cache_keys: Set[str] = set()

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached result by key.

        Args:
            key: Cache key

        Returns:
            Cached data if found and valid, None otherwise
        """
        start_time = time.time()

        with self._lock:
            self.statistics.total_requests += 1

            # Try memory cache first
            entry = self.memory_cache.get(key)
            if entry:
                self.statistics.cache_hits += 1
                self.statistics.memory_hit_rate += 1
                self._record_access_time(start_time)
                return entry.data

            # Try database cache if available
            if self.database_cache:
                entry = self.database_cache.get(key)
                if entry:
                    self.statistics.cache_hits += 1
                    self.statistics.database_hit_rate += 1

                    # Promote to memory cache
                    self.memory_cache.put(key, entry)

                    self._record_access_time(start_time)
                    return entry.data

            # Cache miss
            self.statistics.cache_misses += 1
            self._record_access_time(start_time)
            return None

    def put(
        self,
        key: str,
        data: Any,
        ttl: Optional[timedelta] = None,
        folder_id: Optional[UUID] = None,
        search_parameters: Optional[SearchParameters] = None,
    ) -> bool:
        """
        Cache search result.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live (uses default if None)
            folder_id: Associated folder ID
            search_parameters: Search parameters for hash generation

        Returns:
            True if successfully cached, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl

        # Create cache entry
        now = datetime.now()
        entry = CacheEntry(
            key=key,
            data=data,
            created_time=now,
            expires_time=now + ttl,
            folder_id=folder_id,
            search_hash=(
                self._generate_search_hash(search_parameters)
                if search_parameters
                else None
            ),
        )

        # Check entry size
        estimated_size = len(json.dumps(data, default=str).encode("utf-8"))
        if estimated_size > self.max_entry_size_bytes:
            return False

        with self._lock:
            # Store in memory cache
            memory_success = self.memory_cache.put(key, entry)

            # Store in database cache if available
            db_success = True
            if self.database_cache:
                try:
                    db_success = self.database_cache.put(key, entry)
                except Exception:
                    db_success = False

            # Update statistics
            if memory_success or db_success:
                self.statistics.memory_usage_bytes = self.memory_cache.get_statistics()[
                    "memory_usage_bytes"
                ]

            return memory_success or db_success

    def invalidate(self, key: str) -> bool:
        """
        Invalidate specific cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was removed, False otherwise
        """
        with self._lock:
            memory_removed = self.memory_cache.remove(key)
            db_removed = (
                self.database_cache.remove(key) if self.database_cache else False
            )
            return memory_removed or db_removed

    def invalidate_folder(self, folder_id: UUID) -> int:
        """
        Invalidate all cache entries for a folder.

        Args:
            folder_id: Folder ID to invalidate

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            invalidated_count = 0

            # Invalidate from memory cache
            # Note: This is inefficient for large caches,
            # but memory cache is typically small
            keys_to_remove = []
            for key, entry in self.memory_cache._cache.items():
                if entry.folder_id == folder_id:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                if self.memory_cache.remove(key):
                    invalidated_count += 1

            # Invalidate from database cache
            if self.database_cache:
                invalidated_count += self.database_cache.invalidate_folder_cache(
                    folder_id
                )

            return invalidated_count

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.memory_cache.clear()
            if self.database_cache:
                # Clear database by removing expired entries with past date
                try:
                    with sqlite3.connect(self.database_cache.db_path) as conn:
                        conn.execute("DELETE FROM search_results_cache")
                except Exception:
                    pass

    def cleanup(self) -> Dict[str, int]:
        """
        Perform cache cleanup operations.

        Returns:
            Dictionary with cleanup statistics
        """
        with self._lock:
            results = {"memory_expired": 0, "database_expired": 0, "memory_evicted": 0}

            # Clean up expired entries
            results["memory_expired"] = self.memory_cache.cleanup_expired()

            if self.database_cache:
                results["database_expired"] = self.database_cache.cleanup_expired()

            # Update cleanup time
            self._last_cleanup = datetime.now()

            return results

    def warm_cache(self, keys: List[str]) -> None:
        """
        Mark keys for cache warming.

        Args:
            keys: List of cache keys to warm
        """
        if self.enable_prefetching:
            with self._lock:
                self._warm_cache_keys.update(keys)

    def get_statistics(self) -> CacheStatistics:
        """Get comprehensive cache statistics."""
        with self._lock:
            # Update statistics
            self.statistics.calculate_hit_rate()

            # Calculate average access time
            if self._access_times:
                self.statistics.average_access_time_ms = (
                    sum(self._access_times) / len(self._access_times)
                ) * 1000

            # Update memory usage
            memory_stats = self.memory_cache.get_statistics()
            self.statistics.memory_usage_bytes = memory_stats["memory_usage_bytes"]

            # Update database entries count
            if self.database_cache:
                db_stats = self.database_cache.get_statistics()
                self.statistics.database_entries = db_stats["active_entries"]

            return self.statistics

    def _generate_search_hash(self, parameters: SearchParameters) -> str:
        """Generate hash for search parameters."""
        try:
            # Create a stable representation of search parameters
            param_dict = {
                "query": parameters.query,
                "search_type": (
                    parameters.search_type.value if parameters.search_type else None
                ),
                "root_paths": (
                    sorted(parameters.root_paths) if parameters.root_paths else []
                ),
                "case_sensitive": parameters.case_sensitive,
                "include_subdirectories": parameters.include_subdirectories,
                "file_type_filter": (
                    {
                        "include_extensions": (
                            sorted(parameters.file_type_filter.include_extensions)
                            if parameters.file_type_filter.include_extensions
                            else []
                        ),
                        "exclude_extensions": (
                            sorted(parameters.file_type_filter.exclude_extensions)
                            if parameters.file_type_filter.exclude_extensions
                            else []
                        ),
                        "mime_types": (
                            sorted(parameters.file_type_filter.mime_types)
                            if parameters.file_type_filter.mime_types
                            else []
                        ),
                    }
                    if parameters.file_type_filter
                    else None
                ),
            }
            key_json = json.dumps(param_dict, sort_keys=True, default=str)
            return hashlib.sha256(key_json.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(str(parameters).encode()).hexdigest()[:16]

    def start_background_cleanup(self) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup_worker, daemon=True
        )
        self._cleanup_thread.start()

    def stop_background_cleanup(self) -> None:
        """Stop background cleanup thread."""
        self._shutdown_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)

    def _background_cleanup_worker(self) -> None:
        """Background worker for periodic cleanup."""
        while not self._shutdown_event.is_set():
            try:
                # Check if cleanup is needed
                if datetime.now() - self._last_cleanup >= self.cleanup_interval:
                    self.cleanup()

                # Sleep for a short interval
                self._shutdown_event.wait(timeout=60.0)  # Check every minute

            except Exception:
                # Continue running even if cleanup fails
                self._shutdown_event.wait(timeout=60.0)


def create_cache_key(
    search_parameters: SearchParameters,
    additional_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create standardized cache key for search parameters.

    Args:
        search_parameters: Search parameters
        additional_context: Additional context for key generation

    Returns:
        Generated cache key
    """
    try:
        # Base parameters
        key_components = {
            "query": search_parameters.query or "",
            "search_type": (
                search_parameters.search_type.value
                if search_parameters.search_type
                else None
            ),
            "root_paths": (
                sorted(search_parameters.root_paths)
                if search_parameters.root_paths
                else []
            ),
            "case_sensitive": search_parameters.case_sensitive,
            "include_subdirs": search_parameters.include_subdirectories,
        }

        # File type filter
        if search_parameters.file_type_filter:
            key_components["file_filter"] = {
                "include_ext": search_parameters.file_type_filter.include_extensions
                or [],
                "exclude_ext": search_parameters.file_type_filter.exclude_extensions
                or [],
                "mime_types": search_parameters.file_type_filter.mime_types or [],
            }

        # Size filter
        if search_parameters.size_filter:
            key_components["size_filter"] = {
                "min_size": search_parameters.size_filter.min_size_bytes,
                "max_size": search_parameters.size_filter.max_size_bytes,
            }

        # Date filter
        if search_parameters.date_filter:
            key_components["date_filter"] = {
                "start_date": (
                    search_parameters.date_filter.start_date.isoformat()
                    if search_parameters.date_filter.start_date
                    else None
                ),
                "end_date": (
                    search_parameters.date_filter.end_date.isoformat()
                    if search_parameters.date_filter.end_date
                    else None
                ),
                "filter_type": (
                    search_parameters.date_filter.filter_type.value
                    if search_parameters.date_filter.filter_type
                    else None
                ),
            }

        # Additional context
        if additional_context:
            key_components["context"] = additional_context

        # Generate key
        key_json = json.dumps(key_components, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f"search_{key_hash[:16]}"

    except Exception as e:
        raise ValidationException(
            f"Error creating cache key: {str(e)}",
            context={"search_parameters": str(search_parameters)},
        )
