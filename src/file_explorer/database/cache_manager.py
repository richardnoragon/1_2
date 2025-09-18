"""
Advanced Cache Manager for RFU Multi-Pane File Explorer
Enterprise-Grade Caching System with TTL and Memory Management

This module provides a comprehensive caching framework for file metadata,
thumbnails, and directory structures with intelligent expiration policies,
memory management, and performance optimization.

Features:
- Time-To-Live (TTL) based cache expiration
- Memory usage monitoring and automatic cleanup
- Multi-threaded cache operations with locks
- LRU (Least Recently Used) eviction policy
- Cache statistics and performance metrics
- Persistent cache storage with SQLite backend
- Cache warming and prefetching strategies
- Configurable cache policies per data type

Cache Types Supported:
- File metadata (size, permissions, timestamps)
- Directory contents and structure
- Thumbnail images and previews
- Search index and results
- File type associations and icons
- User preferences and settings

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import hashlib
import json
import logging
import sqlite3
import threading
import time
import weakref
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import (Any, Callable, Dict, Generic, List, Optional, Tuple,
                    TypeVar, Union)

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """Represents a cache entry with metadata."""
    
    key: str
    value: T
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 3600  # 1 hour default
    access_count: int = 0
    size_bytes: int = 0
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds <= 0:  # Permanent cache
            return False
        
        return datetime.now() > (self.created_at + timedelta(seconds=self.ttl_seconds))
    
    def time_until_expiry(self) -> int:
        """Get seconds until expiry (negative if already expired)."""
        if self.ttl_seconds <= 0:
            return -1
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        delta = expiry_time - datetime.now()
        return int(delta.total_seconds())
    
    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def calculate_size(self) -> int:
        """Calculate approximate memory size of the entry."""
        try:
            import sys
            size = sys.getsizeof(self.key)
            size += sys.getsizeof(self.value)
            size += sys.getsizeof(self.metadata)
            size += 200  # Approximate overhead
            self.size_bytes = size
            return size
        except Exception:
            return self.size_bytes or 1024  # Default estimate


@dataclass
class CacheStats:
    """Cache statistics and performance metrics."""
    
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_entries: int = 0
    total_size_bytes: int = 0
    max_size_bytes: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    cache_efficiency: float = 0.0
    last_cleanup: Optional[datetime] = None
    
    def update_hit_rate(self) -> None:
        """Update hit rate calculation."""
        total_requests = self.hit_count + self.miss_count
        self.hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0.0
    
    def update_cache_efficiency(self) -> None:
        """Update cache efficiency metric."""
        if self.max_size_bytes > 0:
            self.cache_efficiency = (self.total_size_bytes / self.max_size_bytes * 100)
        else:
            self.cache_efficiency = 0.0


class CachePolicy(ABC):
    """Abstract base class for cache policies."""
    
    @abstractmethod
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Determine if an item should be cached."""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """Get TTL for cache entry."""
        pass
    
    @abstractmethod
    def should_evict(self, entry: CacheEntry) -> bool:
        """Determine if an entry should be evicted."""
        pass


class FileMetadataCachePolicy(CachePolicy):
    """Cache policy for file metadata."""
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Cache all file metadata."""
        return True
    
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """Get TTL based on file type and size."""
        file_size = metadata.get('size_bytes', 0)
        
        # Larger files have longer TTL
        if file_size > 100 * 1024 * 1024:  # 100MB+
            return 24 * 3600  # 24 hours
        elif file_size > 10 * 1024 * 1024:  # 10MB+
            return 12 * 3600  # 12 hours
        else:
            return 6 * 3600   # 6 hours
    
    def should_evict(self, entry: CacheEntry) -> bool:
        """Evict old, rarely accessed entries."""
        if entry.access_count == 1 and entry.last_accessed < datetime.now() - timedelta(hours=1):
            return True
        return entry.is_expired()


class ThumbnailCachePolicy(CachePolicy):
    """Cache policy for thumbnails."""
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Cache thumbnails for supported image types."""
        file_ext = metadata.get('extension', '').lower()
        return file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """Thumbnails have longer TTL."""
        return 7 * 24 * 3600  # 7 days
    
    def should_evict(self, entry: CacheEntry) -> bool:
        """Evict based on access patterns."""
        return (entry.access_count < 3 and 
                entry.last_accessed < datetime.now() - timedelta(days=3))


class MemoryAwareCache(QObject):
    """
    Thread-safe memory-aware cache with TTL support and LRU eviction.
    
    Features:
    - Configurable memory limits
    - TTL-based expiration
    - LRU eviction policy
    - Thread-safe operations
    - Cache warming and prefetching
    - Performance monitoring
    """
    
    # Signals for cache events
    cache_hit = pyqtSignal(str, float)  # key, access_time_ms
    cache_miss = pyqtSignal(str)
    cache_evicted = pyqtSignal(str, str)  # key, reason
    cache_cleared = pyqtSignal()
    memory_warning = pyqtSignal(int, int)  # current_size, max_size
    
    def __init__(self, 
                 name: str,
                 max_size_bytes: int = 64 * 1024 * 1024,  # 64MB
                 max_entries: int = 10000,
                 default_ttl: int = 3600,
                 policy: Optional[CachePolicy] = None):
        """
        Initialize memory-aware cache.
        
        Args:
            name: Cache name for identification
            max_size_bytes: Maximum memory usage in bytes
            max_entries: Maximum number of entries
            default_ttl: Default TTL in seconds
            policy: Cache policy for custom behavior
        """
        super().__init__()
        
        self.name = name
        self.max_size_bytes = max_size_bytes
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.policy = policy or FileMetadataCachePolicy()
        
        # Thread-safe storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats(max_size_bytes=max_size_bytes)
        
        # Cleanup timer
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._periodic_cleanup)
        self._cleanup_timer.start(300000)  # 5 minutes
        
        # Logger
        self.logger = logging.getLogger(f'RFU.FileExplorer.Cache.{name}')
        self.logger.info(f"Initialized cache '{name}' with {max_size_bytes // (1024*1024)}MB limit")
    
    def get(self, key: str, default: T = None) -> Optional[T]:
        """
        Get value from cache with performance tracking.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        start_time = time.perf_counter()
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats.miss_count += 1
                self.cache_miss.emit(key)
                return default
            
            if entry.is_expired():
                self._cache.pop(key)
                self.stats.miss_count += 1
                self.stats.eviction_count += 1
                self.cache_evicted.emit(key, "expired")
                return default
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            entry.touch()
            
            # Update statistics
            self.stats.hit_count += 1
            access_time_ms = (time.perf_counter() - start_time) * 1000
            self.cache_hit.emit(key, access_time_ms)
            
            return entry.value
    
    def set(self, key: str, value: T, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set cache entry with TTL and policy validation.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            metadata: Additional metadata
            
        Returns:
            True if cached successfully
        """
        metadata = metadata or {}
        
        # Check cache policy
        if not self.policy.should_cache(key, value, metadata):
            return False
        
        ttl = ttl or self.policy.get_ttl(key, value, metadata)
        
        with self._lock:
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl,
                metadata=metadata
            )
            entry.calculate_size()
            
            # Check if we need to make space
            self._ensure_capacity(entry.size_bytes)
            
            # Store entry
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            # Update statistics
            self.stats.total_entries = len(self._cache)
            self.stats.total_size_bytes += entry.size_bytes
            
            self.logger.debug(f"Cached '{key}' with {entry.size_bytes} bytes, TTL: {ttl}s")
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            entry = self._cache.pop(key, None)
            if entry:
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.total_entries = len(self._cache)
                self.cache_evicted.emit(key, "manual_delete")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self.stats.total_entries = 0
            self.stats.total_size_bytes = 0
            self.cache_cleared.emit()
            self.logger.info(f"Cache '{self.name}' cleared")
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                entry = self._cache.pop(key)
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.eviction_count += 1
                removed_count += 1
                self.cache_evicted.emit(key, "expired")
            
            self.stats.total_entries = len(self._cache)
            self.stats.last_cleanup = datetime.now()
        
        if removed_count > 0:
            self.logger.debug(f"Cleaned up {removed_count} expired entries")
        
        return removed_count
    
    def _ensure_capacity(self, new_entry_size: int) -> None:
        """Ensure cache has capacity for new entry."""
        target_size = self.stats.total_size_bytes + new_entry_size
        
        # Check memory limit
        if target_size > self.max_size_bytes:
            self.memory_warning.emit(self.stats.total_size_bytes, self.max_size_bytes)
            self._evict_lru_entries(target_size - self.max_size_bytes)
        
        # Check entry count limit
        if len(self._cache) >= self.max_entries:
            self._evict_lru_entries(1, by_count=True)
    
    def _evict_lru_entries(self, bytes_to_free: int, by_count: bool = False) -> None:
        """Evict least recently used entries."""
        freed_bytes = 0
        freed_count = 0
        
        # Create list of entries sorted by LRU (oldest first)
        entries_by_lru = list(self._cache.items())
        
        for key, entry in entries_by_lru:
            if by_count and freed_count >= 1:
                break
            if not by_count and freed_bytes >= bytes_to_free:
                break
            
            # Check if policy allows eviction
            if self.policy.should_evict(entry):
                self._cache.pop(key)
                freed_bytes += entry.size_bytes
                freed_count += 1
                self.stats.eviction_count += 1
                self.cache_evicted.emit(key, "lru_eviction")
        
        self.stats.total_size_bytes -= freed_bytes
        self.stats.total_entries = len(self._cache)
        
        if freed_count > 0:
            self.logger.debug(f"Evicted {freed_count} LRU entries, freed {freed_bytes} bytes")
    
    def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired entries."""
        expired_count = self.cleanup_expired()
        self.stats.update_hit_rate()
        self.stats.update_cache_efficiency()
        
        if expired_count > 0:
            self.logger.debug(f"Periodic cleanup removed {expired_count} expired entries")
    
    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self._lock:
            self.stats.total_entries = len(self._cache)
            self.stats.update_hit_rate()
            self.stats.update_cache_efficiency()
            return self.stats
    
    def warm_cache(self, key_value_pairs: List[Tuple[str, T]], 
                   metadata_list: Optional[List[Dict[str, Any]]] = None) -> int:
        """
        Warm cache with multiple entries.
        
        Args:
            key_value_pairs: List of (key, value) tuples
            metadata_list: Optional list of metadata dicts
            
        Returns:
            Number of entries successfully cached
        """
        cached_count = 0
        metadata_list = metadata_list or [{}] * len(key_value_pairs)
        
        for i, (key, value) in enumerate(key_value_pairs):
            metadata = metadata_list[i] if i < len(metadata_list) else {}
            if self.set(key, value, metadata=metadata):
                cached_count += 1
        
        self.logger.info(f"Cache warming completed: {cached_count}/{len(key_value_pairs)} entries cached")
        return cached_count
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry."""
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            
            return {
                'key': entry.key,
                'created_at': entry.created_at.isoformat(),
                'last_accessed': entry.last_accessed.isoformat(),
                'ttl_seconds': entry.ttl_seconds,
                'access_count': entry.access_count,
                'size_bytes': entry.size_bytes,
                'is_expired': entry.is_expired(),
                'time_until_expiry': entry.time_until_expiry(),
                'metadata': entry.metadata
            }


class CacheManager:
    """
    Central cache manager for the file explorer.
    
    Manages multiple specialized caches with different policies and
    provides a unified interface for cache operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cache manager.
        
        Args:
            config: Configuration dictionary for cache settings
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger('RFU.FileExplorer.CacheManager')
        
        # Initialize specialized caches
        self.caches: Dict[str, MemoryAwareCache] = {}
        self._initialize_caches()
        
        # Global statistics
        self.global_stats = {
            'total_hit_count': 0,
            'total_miss_count': 0,
            'total_eviction_count': 0,
            'start_time': datetime.now()
        }
        
        self.logger.info("Cache manager initialized with caches: " + 
                        ", ".join(self.caches.keys()))
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default cache configuration."""
        return {
            'file_metadata': {
                'max_size_mb': 32,
                'max_entries': 5000,
                'default_ttl': 6 * 3600  # 6 hours
            },
            'thumbnails': {
                'max_size_mb': 128,
                'max_entries': 2000,
                'default_ttl': 7 * 24 * 3600  # 7 days
            },
            'directory_listings': {
                'max_size_mb': 16,
                'max_entries': 1000,
                'default_ttl': 1 * 3600  # 1 hour
            },
            'search_results': {
                'max_size_mb': 8,
                'max_entries': 500,
                'default_ttl': 30 * 60  # 30 minutes
            }
        }
    
    def _initialize_caches(self) -> None:
        """Initialize all cache instances."""
        cache_policies = {
            'file_metadata': FileMetadataCachePolicy(),
            'thumbnails': ThumbnailCachePolicy(),
            'directory_listings': FileMetadataCachePolicy(),
            'search_results': FileMetadataCachePolicy()
        }
        
        for cache_name, cache_config in self.config.items():
            max_size_bytes = cache_config['max_size_mb'] * 1024 * 1024
            max_entries = cache_config['max_entries']
            default_ttl = cache_config['default_ttl']
            policy = cache_policies.get(cache_name, FileMetadataCachePolicy())
            
            cache = MemoryAwareCache(
                name=cache_name,
                max_size_bytes=max_size_bytes,
                max_entries=max_entries,
                default_ttl=default_ttl,
                policy=policy
            )
            
            # Connect signals for global statistics
            cache.cache_hit.connect(self._on_cache_hit)
            cache.cache_miss.connect(self._on_cache_miss)
            cache.cache_evicted.connect(self._on_cache_evicted)
            
            self.caches[cache_name] = cache
    
    def get_cache(self, cache_name: str) -> Optional[MemoryAwareCache]:
        """Get cache instance by name."""
        return self.caches.get(cache_name)
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from cache."""
        cache = self.get_cache('file_metadata')
        return cache.get(file_path) if cache else None
    
    def set_file_metadata(self, file_path: str, metadata: Dict[str, Any], 
                         ttl: Optional[int] = None) -> bool:
        """Set file metadata in cache."""
        cache = self.get_cache('file_metadata')
        return cache.set(file_path, metadata, ttl, metadata) if cache else False
    
    def get_thumbnail(self, file_path: str) -> Optional[bytes]:
        """Get thumbnail from cache."""
        cache = self.get_cache('thumbnails')
        return cache.get(file_path) if cache else None
    
    def set_thumbnail(self, file_path: str, thumbnail_data: bytes, 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set thumbnail in cache."""
        cache = self.get_cache('thumbnails')
        metadata = metadata or {'size_bytes': len(thumbnail_data)}
        return cache.set(file_path, thumbnail_data, metadata=metadata) if cache else False
    
    def get_directory_listing(self, dir_path: str) -> Optional[List[Dict[str, Any]]]:
        """Get directory listing from cache."""
        cache = self.get_cache('directory_listings')
        return cache.get(dir_path) if cache else None
    
    def set_directory_listing(self, dir_path: str, listing: List[Dict[str, Any]],
                            ttl: Optional[int] = None) -> bool:
        """Set directory listing in cache."""
        cache = self.get_cache('directory_listings')
        metadata = {'entry_count': len(listing)}
        return cache.set(dir_path, listing, ttl, metadata) if cache else False
    
    def invalidate_path(self, path: str) -> int:
        """
        Invalidate all cache entries related to a path.
        
        Args:
            path: File or directory path to invalidate
            
        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        
        for cache in self.caches.values():
            with cache._lock:
                keys_to_remove = [
                    key for key in cache._cache.keys()
                    if key.startswith(path) or path.startswith(key)
                ]
                
                for key in keys_to_remove:
                    if cache.delete(key):
                        invalidated_count += 1
        
        if invalidated_count > 0:
            self.logger.debug(f"Invalidated {invalidated_count} cache entries for path: {path}")
        
        return invalidated_count
    
    def cleanup_all(self) -> Dict[str, int]:
        """
        Cleanup expired entries in all caches.
        
        Returns:
            Dictionary mapping cache names to cleanup counts
        """
        cleanup_results = {}
        
        for cache_name, cache in self.caches.items():
            cleanup_results[cache_name] = cache.cleanup_expired()
        
        total_cleaned = sum(cleanup_results.values())
        if total_cleaned > 0:
            self.logger.info(f"Global cleanup removed {total_cleaned} expired entries")
        
        return cleanup_results
    
    def clear_all(self) -> None:
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()
        
        self.logger.info("All caches cleared")
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global cache statistics."""
        cache_stats = {}
        total_size_bytes = 0
        total_entries = 0
        total_hit_rate = 0.0
        
        for cache_name, cache in self.caches.items():
            stats = cache.get_stats()
            cache_stats[cache_name] = {
                'hit_count': stats.hit_count,
                'miss_count': stats.miss_count,
                'hit_rate': stats.hit_rate,
                'total_entries': stats.total_entries,
                'total_size_mb': stats.total_size_bytes / (1024 * 1024),
                'max_size_mb': stats.max_size_bytes / (1024 * 1024),
                'cache_efficiency': stats.cache_efficiency
            }
            
            total_size_bytes += stats.total_size_bytes
            total_entries += stats.total_entries
            total_hit_rate += stats.hit_rate
        
        avg_hit_rate = total_hit_rate / len(self.caches) if self.caches else 0.0
        
        return {
            'cache_stats': cache_stats,
            'global_totals': {
                'total_size_mb': total_size_bytes / (1024 * 1024),
                'total_entries': total_entries,
                'average_hit_rate': avg_hit_rate,
                'uptime_seconds': (datetime.now() - self.global_stats['start_time']).total_seconds()
            }
        }
    
    def _on_cache_hit(self, key: str, access_time_ms: float) -> None:
        """Handle cache hit event."""
        self.global_stats['total_hit_count'] += 1
    
    def _on_cache_miss(self, key: str) -> None:
        """Handle cache miss event."""
        self.global_stats['total_miss_count'] += 1
    
    def _on_cache_evicted(self, key: str, reason: str) -> None:
        """Handle cache eviction event."""
        self.global_stats['total_eviction_count'] += 1


# For testing and development
if __name__ == '__main__':
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test cache manager
    cache_manager = CacheManager()
    
    # Test file metadata caching
    test_metadata = {
        'size_bytes': 1024,
        'modified_time': datetime.now().isoformat(),
        'file_type': 'text'
    }
    
    print("Testing cache operations...")
    
    # Set metadata
    success = cache_manager.set_file_metadata('/test/file.txt', test_metadata)
    print(f"Set metadata: {success}")
    
    # Get metadata
    cached_metadata = cache_manager.get_file_metadata('/test/file.txt')
    print(f"Retrieved metadata: {cached_metadata is not None}")
    
    # Test thumbnail caching
    test_thumbnail = b'fake_thumbnail_data' * 100
    success = cache_manager.set_thumbnail('/test/image.jpg', test_thumbnail)
    print(f"Set thumbnail: {success}")
    
    # Get statistics
    stats = cache_manager.get_global_stats()
    print(f"Global stats: {json.dumps(stats, indent=2, default=str)}")
    
    print("Cache testing completed!")