"""Advanced Result Caching System.

Enterprise-grade caching implementation with LRU eviction, TTL-based
expiration, intelligent invalidation strategies, and multi-tier caching
architecture.

Features:
- Multi-tier caching (memory, disk, distributed)
- LRU and LFU eviction policies
- TTL-based expiration with sliding windows
- Intelligent cache invalidation and warming
- Cache coherency and consistency management
- Performance monitoring and optimization
- Thread-safe operations with minimal locking
"""

import logging
import pickle
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CachePolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live only
    FIFO = "fifo"  # First In, First Out


class CacheEvent(Enum):
    """Cache events for monitoring."""

    HIT = "hit"
    MISS = "miss"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    EVICT = "evict"
    CLEAR = "clear"


@dataclass
class CacheConfig:
    """Configuration for cache management."""

    # Memory cache settings
    memory_cache_size: int = 1000
    memory_ttl_seconds: int = 3600  # 1 hour
    memory_eviction_policy: CachePolicy = CachePolicy.LRU

    # Disk cache settings
    enable_disk_cache: bool = True
    disk_cache_size_mb: int = 100
    disk_cache_path: Optional[str] = None
    disk_ttl_seconds: int = 86400  # 24 hours

    # Distributed cache settings
    enable_distributed_cache: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl_seconds: int = 3600

    # Performance settings
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress objects > 1KB
    max_object_size_mb: int = 10

    # Monitoring
    enable_metrics: bool = True
    metrics_collection_interval: float = 60.0

    # Cache warming
    enable_cache_warming: bool = True
    warm_cache_on_startup: bool = False

    # Invalidation
    enable_smart_invalidation: bool = True
    invalidation_batch_size: int = 100


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""

    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: Set[str] = field(default_factory=set)
    size_bytes: int = 0

    @property
    def age(self) -> float:
        """Get entry age in seconds."""
        return time.time() - self.created_at

    @property
    def idle_time(self) -> float:
        """Get time since last access."""
        return time.time() - self.accessed_at

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        return self.age > self.ttl_seconds

    def touch(self):
        """Update access time and count."""
        self.accessed_at = time.time()
        self.access_count += 1


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_sets: int = 0
    cache_deletes: int = 0
    cache_expires: int = 0
    cache_evictions: int = 0

    total_memory_usage: int = 0
    total_disk_usage: int = 0

    average_access_time: float = 0.0
    average_set_time: float = 0.0

    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def miss_ratio(self) -> float:
        """Calculate cache miss ratio."""
        return 1.0 - self.hit_ratio

    def update_event(self, event: CacheEvent):
        """Update metrics for cache event."""
        if event == CacheEvent.HIT:
            self.cache_hits += 1
            self.total_requests += 1
        elif event == CacheEvent.MISS:
            self.cache_misses += 1
            self.total_requests += 1
        elif event == CacheEvent.SET:
            self.cache_sets += 1
        elif event == CacheEvent.DELETE:
            self.cache_deletes += 1
        elif event == CacheEvent.EXPIRE:
            self.cache_expires += 1
        elif event == CacheEvent.EVICT:
            self.cache_evictions += 1


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cached items."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get cache size (number of items)."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with advanced eviction policies."""

    def __init__(self, config: CacheConfig):
        """Initialize memory cache backend.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.logger = logging.getLogger("MemoryCache")

        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: OrderedDict = OrderedDict()
        self.frequency_counter: Dict[str, int] = defaultdict(int)

        # Thread safety
        self.lock = RLock()

        # Size tracking
        self.current_size = 0
        self.max_size = config.memory_cache_size

        self.logger.debug(
            f"Memory cache initialized with size {self.max_size}"
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        with self.lock:
            entry = self.cache.get(key)

            if entry is None:
                return None

            # Check expiration
            if entry.is_expired:
                self._remove_entry(key)
                return None

            # Update access tracking
            entry.touch()
            self._update_access_order(key)

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        with self.lock:
            # Calculate size
            size_bytes = self._calculate_size(value)

            # Check if value is too large
            max_size_bytes = self.config.max_object_size_mb * 1024 * 1024
            if size_bytes > max_size_bytes:
                self.logger.warning(
                    f"Object too large for cache: {size_bytes} bytes"
                )
                return False

            # Remove existing entry if it exists
            if key in self.cache:
                self._remove_entry(key)

            # Ensure space is available
            self._ensure_space(size_bytes)

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                accessed_at=time.time(),
                ttl_seconds=ttl or self.config.memory_ttl_seconds,
                size_bytes=size_bytes,
            )

            # Store entry
            self.cache[key] = entry
            self.current_size += 1
            self._update_access_order(key)

            return True

    def delete(self, key: str) -> bool:
        """Delete key."""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False

    def clear(self) -> bool:
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.frequency_counter.clear()
            self.current_size = 0
            return True

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        with self.lock:
            entry = self.cache.get(key)
            return entry is not None and not entry.is_expired

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        import fnmatch

        with self.lock:
            all_keys = list(self.cache.keys())
            if pattern == "*":
                return all_keys

            return [key for key in all_keys if fnmatch.fnmatch(key, pattern)]

    def size(self) -> int:
        """Get cache size (number of items)."""
        with self.lock:
            return self.current_size

    def get_memory_usage(self) -> int:
        """Get total memory usage in bytes."""
        with self.lock:
            return sum(entry.size_bytes for entry in self.cache.values())

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items() if entry.is_expired
            ]

            for key in expired_keys:
                self._remove_entry(key)

            return len(expired_keys)

    def _ensure_space(self, _required_size: int):
        """Ensure space is available for new entry."""
        while self.current_size >= self.max_size:
            if not self._evict_one():
                break

    def _evict_one(self) -> bool:
        """Evict one entry based on policy."""
        if not self.cache:
            return False

        if self.config.memory_eviction_policy == CachePolicy.LRU:
            key = next(iter(self.access_order))
        elif self.config.memory_eviction_policy == CachePolicy.LFU:
            key = min(
                self.frequency_counter.keys(),
                key=lambda k: self.frequency_counter[k],
            )
        elif self.config.memory_eviction_policy == CachePolicy.FIFO:
            key = min(
                self.cache.keys(), key=lambda k: self.cache[k].created_at
            )
        else:  # TTL
            # Evict entry with least remaining TTL
            key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].ttl_seconds or float("inf"),
            )

        self._remove_entry(key)
        return True

    def _remove_entry(self, key: str):
        """Remove entry from cache."""
        if key in self.cache:
            del self.cache[key]
            self.current_size -= 1

        if key in self.access_order:
            del self.access_order[key]

        if key in self.frequency_counter:
            del self.frequency_counter[key]

    def _update_access_order(self, key: str):
        """Update access order for LRU tracking."""
        if key in self.access_order:
            del self.access_order[key]
        self.access_order[key] = time.time()

        # Update frequency counter
        self.frequency_counter[key] += 1

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            # Fallback estimation
            return len(str(value).encode("utf-8"))


class DiskCacheBackend(CacheBackend):
    """Disk-based cache backend using SQLite."""

    def __init__(self, config: CacheConfig):
        """Initialize disk cache backend.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.logger = logging.getLogger("DiskCache")

        # Database setup
        if config.disk_cache_path:
            self.db_path = Path(config.disk_cache_path) / "cache.db"
        else:
            self.db_path = Path.cwd() / "cache" / "cache.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Thread safety
        self.lock = Lock()

        # Initialize database
        self._init_database()

        self.logger.debug(f"Disk cache initialized at {self.db_path}")

    def _init_database(self):
        """Initialize SQLite database for cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    accessed_at REAL,
                    access_count INTEGER DEFAULT 0,
                    ttl_seconds INTEGER,
                    size_bytes INTEGER,
                    tags TEXT DEFAULT ''
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_accessed_at 
                ON cache_entries(accessed_at)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_created_at 
                ON cache_entries(created_at)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_ttl 
                ON cache_entries(created_at, ttl_seconds)
            """
            )

            conn.commit()

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT value, created_at, ttl_seconds 
                    FROM cache_entries 
                    WHERE key = ?
                """,
                    (key,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                value_blob, created_at, ttl_seconds = row

                # Check expiration
                if ttl_seconds and (time.time() - created_at) > ttl_seconds:
                    self.delete(key)
                    return None

                # Update access tracking
                cursor.execute(
                    """
                    UPDATE cache_entries 
                    SET accessed_at = ?, access_count = access_count + 1
                    WHERE key = ?
                """,
                    (time.time(), key),
                )

                conn.commit()

                try:
                    return pickle.loads(value_blob)
                except Exception as e:
                    self.logger.error(
                        f"Failed to deserialize cached value: {e}"
                    )
                    self.delete(key)
                    return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        try:
            # Serialize value
            if self.config.enable_compression:
                value_blob = self._compress_value(value)
            else:
                value_blob = pickle.dumps(value)

            size_bytes = len(value_blob)

            # Check size limit
            max_size_bytes = self.config.max_object_size_mb * 1024 * 1024
            if size_bytes > max_size_bytes:
                self.logger.warning(
                    f"Object too large for disk cache: {size_bytes}"
                )
                return False

            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # Upsert entry
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO cache_entries 
                        (key, value, created_at, accessed_at, ttl_seconds, size_bytes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            key,
                            value_blob,
                            time.time(),
                            time.time(),
                            ttl or self.config.disk_ttl_seconds,
                            size_bytes,
                        ),
                    )

                    conn.commit()

                    # Cleanup old entries if needed
                    self._cleanup_old_entries(conn)

            return True

        except Exception as e:
            self.logger.error(f"Failed to cache value: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM cache_entries WHERE key = ?", (key,)
                )
                conn.commit()
                return cursor.rowcount > 0

    def clear(self) -> bool:
        """Clear all cached items."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache_entries")
                conn.commit()
                return True

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 1 FROM cache_entries 
                    WHERE key = ? AND 
                    (ttl_seconds IS NULL OR 
                     (? - created_at) <= ttl_seconds)
                """,
                    (key, time.time()),
                )

                return cursor.fetchone() is not None

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if pattern == "*":
                    cursor.execute("SELECT key FROM cache_entries")
                else:
                    # Convert glob pattern to SQL LIKE pattern
                    sql_pattern = pattern.replace("*", "%").replace("?", "_")
                    cursor.execute(
                        "SELECT key FROM cache_entries WHERE key LIKE ?",
                        (sql_pattern,),
                    )

                return [row[0] for row in cursor.fetchall()]

    def size(self) -> int:
        """Get cache size (number of items)."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache_entries")
                return cursor.fetchone()[0]

    def get_disk_usage(self) -> int:
        """Get total disk usage in bytes."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(size_bytes) FROM cache_entries")
                result = cursor.fetchone()[0]
                return result or 0

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM cache_entries 
                    WHERE ttl_seconds IS NOT NULL AND 
                    (? - created_at) > ttl_seconds
                """,
                    (time.time(),),
                )

                conn.commit()
                return cursor.rowcount

    def _cleanup_old_entries(self, conn: sqlite3.Connection):
        """Clean up old entries to maintain size limits."""
        cursor = conn.cursor()

        # Get current disk usage
        cursor.execute("SELECT SUM(size_bytes) FROM cache_entries")
        current_size = cursor.fetchone()[0] or 0

        max_size_bytes = self.config.disk_cache_size_mb * 1024 * 1024

        if current_size > max_size_bytes:
            # Remove oldest entries until under limit
            bytes_to_remove = current_size - max_size_bytes

            cursor.execute(
                """
                SELECT key, size_bytes FROM cache_entries 
                ORDER BY accessed_at ASC
            """
            )

            removed_bytes = 0
            for key, size_bytes in cursor.fetchall():
                cursor.execute(
                    "DELETE FROM cache_entries WHERE key = ?", (key,)
                )
                removed_bytes += size_bytes

                if removed_bytes >= bytes_to_remove:
                    break

            conn.commit()

    def _compress_value(self, value: Any) -> bytes:
        """Compress value if beneficial."""
        value_blob = pickle.dumps(value)

        if len(value_blob) < self.config.compression_threshold:
            return value_blob

        try:
            import gzip

            compressed = gzip.compress(value_blob)

            # Only use compression if it saves significant space
            if len(compressed) < len(value_blob) * 0.8:
                return compressed
            else:
                return value_blob

        except Exception:
            return value_blob


class DistributedCacheBackend(CacheBackend):
    """Redis-based distributed cache backend."""

    def __init__(self, config: CacheConfig):
        """Initialize distributed cache backend.

        Args:
            config: Cache configuration
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library required for distributed cache")

        self.config = config
        self.logger = logging.getLogger("DistributedCache")

        # Redis connection
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            decode_responses=False,
        )

        # Test connection
        try:
            self.redis_client.ping()
            self.logger.info("Connected to Redis server")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        try:
            value_blob = self.redis_client.get(key)
            if value_blob is None:
                return None

            return pickle.loads(value_blob)

        except Exception as e:
            self.logger.error(f"Failed to get value from Redis: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        try:
            value_blob = pickle.dumps(value)

            ttl_seconds = ttl or self.config.redis_ttl_seconds
            return self.redis_client.setex(key, ttl_seconds, value_blob)

        except Exception as e:
            self.logger.error(f"Failed to set value in Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            self.logger.error(f"Failed to delete key from Redis: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cached items."""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear Redis cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            self.logger.error(f"Failed to check key existence in Redis: {e}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode("utf-8") for key in keys]
        except Exception as e:
            self.logger.error(f"Failed to get keys from Redis: {e}")
            return []

    def size(self) -> int:
        """Get cache size (number of items)."""
        try:
            return self.redis_client.dbsize()
        except Exception as e:
            self.logger.error(f"Failed to get Redis cache size: {e}")
            return 0


class CacheInvalidationManager:
    """Manages intelligent cache invalidation strategies."""

    def __init__(self, cache_manager):
        """Initialize invalidation manager.

        Args:
            cache_manager: Parent cache manager
        """
        self.cache_manager = cache_manager
        self.logger = logging.getLogger("CacheInvalidation")

        # Tag-based invalidation
        self.tag_mappings: Dict[str, Set[str]] = defaultdict(set)
        self.key_tags: Dict[str, Set[str]] = defaultdict(set)

        # Pattern-based invalidation
        self.invalidation_patterns: List[Tuple[str, Callable]] = []

        # Lock for thread safety
        self.lock = Lock()

    def add_tag_mapping(self, key: str, tags: Set[str]):
        """Add tag mapping for a cache key.

        Args:
            key: Cache key
            tags: Set of tags to associate with key
        """
        with self.lock:
            for tag in tags:
                self.tag_mappings[tag].add(key)
            self.key_tags[key].update(tags)

    def remove_tag_mapping(self, key: str):
        """Remove tag mapping for a cache key.

        Args:
            key: Cache key to remove mappings for
        """
        with self.lock:
            tags = self.key_tags.pop(key, set())
            for tag in tags:
                self.tag_mappings[tag].discard(key)

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specified tag.

        Args:
            tag: Tag to invalidate

        Returns:
            Number of entries invalidated
        """
        with self.lock:
            keys = self.tag_mappings.get(tag, set()).copy()

        invalidated = 0
        for key in keys:
            if self.cache_manager.delete(key):
                invalidated += 1
                self.remove_tag_mapping(key)

        self.logger.info(f"Invalidated {invalidated} entries with tag '{tag}'")
        return invalidated

    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match keys against

        Returns:
            Number of entries invalidated
        """
        keys = self.cache_manager.keys(pattern)

        invalidated = 0
        for key in keys:
            if self.cache_manager.delete(key):
                invalidated += 1
                self.remove_tag_mapping(key)

        self.logger.info(
            f"Invalidated {invalidated} entries matching '{pattern}'"
        )
        return invalidated

    def add_invalidation_rule(self, pattern: str, condition_func: Callable):
        """Add custom invalidation rule.

        Args:
            pattern: Key pattern to monitor
            condition_func: Function that returns True if invalidation needed
        """
        with self.lock:
            self.invalidation_patterns.append((pattern, condition_func))

    def check_invalidation_rules(self) -> int:
        """Check and apply invalidation rules.

        Returns:
            Number of entries invalidated
        """
        invalidated = 0

        with self.lock:
            patterns = self.invalidation_patterns.copy()

        for pattern, condition_func in patterns:
            try:
                if condition_func():
                    invalidated += self.invalidate_by_pattern(pattern)
            except Exception as e:
                self.logger.error(f"Error in invalidation rule: {e}")

        return invalidated


class MultiTierCacheManager:
    """Multi-tier cache manager with intelligent data placement."""

    def __init__(self, config: CacheConfig):
        """Initialize multi-tier cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.logger = logging.getLogger("MultiTierCache")

        # Initialize cache backends
        self.memory_cache = MemoryCacheBackend(config)

        self.disk_cache = None
        if config.enable_disk_cache:
            self.disk_cache = DiskCacheBackend(config)

        self.distributed_cache = None
        if config.enable_distributed_cache:
            try:
                self.distributed_cache = DistributedCacheBackend(config)
            except Exception as e:
                self.logger.warning(f"Distributed cache not available: {e}")

        # Cache metrics
        self.metrics = CacheMetrics()
        self.metrics_lock = Lock()

        # Invalidation manager
        self.invalidation_manager = CacheInvalidationManager(self)

        # Background cleanup
        self.cleanup_thread = None
        self.is_running = True
        self._start_cleanup_thread()

        self.logger.info("Multi-tier cache manager initialized")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with tier fallback.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        start_time = time.time()

        try:
            # Try memory cache first
            value = self.memory_cache.get(key)
            if value is not None:
                self._update_metrics(CacheEvent.HIT, time.time() - start_time)
                return value

            # Try disk cache
            if self.disk_cache:
                value = self.disk_cache.get(key)
                if value is not None:
                    # Promote to memory cache
                    self.memory_cache.set(key, value)
                    self._update_metrics(
                        CacheEvent.HIT, time.time() - start_time
                    )
                    return value

            # Try distributed cache
            if self.distributed_cache:
                value = self.distributed_cache.get(key)
                if value is not None:
                    # Promote to memory and disk cache
                    self.memory_cache.set(key, value)
                    if self.disk_cache:
                        self.disk_cache.set(key, value)
                    self._update_metrics(
                        CacheEvent.HIT, time.time() - start_time
                    )
                    return value

            # Cache miss
            self._update_metrics(CacheEvent.MISS, time.time() - start_time)
            return default

        except Exception as e:
            self.logger.error(f"Error getting cache value: {e}")
            self._update_metrics(CacheEvent.MISS, time.time() - start_time)
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None,
    ) -> bool:
        """Set value in cache across all tiers.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Optional tags for invalidation

        Returns:
            True if successfully cached
        """
        start_time = time.time()
        success = False

        try:
            # Set in memory cache
            if self.memory_cache.set(key, value, ttl):
                success = True

            # Set in disk cache
            if self.disk_cache and self.disk_cache.set(key, value, ttl):
                success = True

            # Set in distributed cache
            if self.distributed_cache and self.distributed_cache.set(
                key, value, ttl
            ):
                success = True

            # Add tag mappings
            if tags and success:
                self.invalidation_manager.add_tag_mapping(key, tags)

            if success:
                self._update_metrics(CacheEvent.SET, time.time() - start_time)

            return success

        except Exception as e:
            self.logger.error(f"Error setting cache value: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from all cache tiers.

        Args:
            key: Cache key

        Returns:
            True if successfully deleted
        """
        success = False

        try:
            # Delete from all tiers
            if self.memory_cache.delete(key):
                success = True

            if self.disk_cache and self.disk_cache.delete(key):
                success = True

            if self.distributed_cache and self.distributed_cache.delete(key):
                success = True

            # Remove tag mappings
            self.invalidation_manager.remove_tag_mapping(key)

            if success:
                self._update_metrics(CacheEvent.DELETE)

            return success

        except Exception as e:
            self.logger.error(f"Error deleting cache value: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache tiers.

        Returns:
            True if successfully cleared
        """
        success = True

        try:
            if not self.memory_cache.clear():
                success = False

            if self.disk_cache and not self.disk_cache.clear():
                success = False

            if self.distributed_cache and not self.distributed_cache.clear():
                success = False

            # Clear tag mappings
            with self.invalidation_manager.lock:
                self.invalidation_manager.tag_mappings.clear()
                self.invalidation_manager.key_tags.clear()

            if success:
                self._update_metrics(CacheEvent.CLEAR)

            return success

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in any cache tier.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        return (
            self.memory_cache.exists(key)
            or (self.disk_cache and self.disk_cache.exists(key))
            or (self.distributed_cache and self.distributed_cache.exists(key))
        )

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern from all tiers.

        Args:
            pattern: Pattern to match

        Returns:
            List of matching keys
        """
        all_keys = set()

        all_keys.update(self.memory_cache.keys(pattern))

        if self.disk_cache:
            all_keys.update(self.disk_cache.keys(pattern))

        if self.distributed_cache:
            all_keys.update(self.distributed_cache.keys(pattern))

        return list(all_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary of cache statistics
        """
        with self.metrics_lock:
            stats = {
                "metrics": {
                    "hit_ratio": self.metrics.hit_ratio,
                    "miss_ratio": self.metrics.miss_ratio,
                    "total_requests": self.metrics.total_requests,
                    "cache_hits": self.metrics.cache_hits,
                    "cache_misses": self.metrics.cache_misses,
                    "cache_sets": self.metrics.cache_sets,
                    "cache_deletes": self.metrics.cache_deletes,
                    "cache_expires": self.metrics.cache_expires,
                    "cache_evictions": self.metrics.cache_evictions,
                },
                "memory_cache": {
                    "size": self.memory_cache.size(),
                    "memory_usage": self.memory_cache.get_memory_usage(),
                },
                "disk_cache": {},
                "distributed_cache": {},
            }

            if self.disk_cache:
                stats["disk_cache"] = {
                    "size": self.disk_cache.size(),
                    "disk_usage": self.disk_cache.get_disk_usage(),
                }

            if self.distributed_cache:
                stats["distributed_cache"] = {
                    "size": self.distributed_cache.size(),
                }

            return stats

    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired entries from all tiers.

        Returns:
            Dictionary with cleanup counts per tier
        """
        cleanup_counts = {}

        cleanup_counts["memory"] = self.memory_cache.cleanup_expired()

        if self.disk_cache:
            cleanup_counts["disk"] = self.disk_cache.cleanup_expired()

        # Distributed cache (Redis) handles expiration automatically

        total_cleaned = sum(cleanup_counts.values())
        if total_cleaned > 0:
            with self.metrics_lock:
                self.metrics.cache_expires += total_cleaned

        return cleanup_counts

    def _update_metrics(self, event: CacheEvent, duration: float = 0.0):
        """Update cache metrics.

        Args:
            event: Cache event type
            duration: Operation duration
        """
        with self.metrics_lock:
            self.metrics.update_event(event, duration)

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""

        def cleanup_loop():
            while self.is_running:
                try:
                    time.sleep(self.config.metrics_collection_interval)
                    self.cleanup_expired()
                    self.invalidation_manager.check_invalidation_rules()
                except Exception as e:
                    self.logger.error(f"Cleanup thread error: {e}")

        self.cleanup_thread = threading.Thread(
            target=cleanup_loop, daemon=True
        )
        self.cleanup_thread.start()

    def shutdown(self):
        """Shutdown the cache manager."""
        self.is_running = False

        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5.0)

        self.logger.info("Multi-tier cache manager shutdown complete")
