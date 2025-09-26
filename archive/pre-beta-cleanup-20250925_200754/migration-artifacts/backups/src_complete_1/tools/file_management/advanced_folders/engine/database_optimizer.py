"""Database Query Optimization Module.

Enterprise-grade database optimization with connection pooling,
intelligent indexing strategies, query plan analysis, and performance monitoring.

Features:
- Advanced connection pooling with health monitoring
- Intelligent query optimization and caching
- Comprehensive indexing strategies
- Real-time performance monitoring
- Query plan analysis and recommendations
- Database maintenance automation
"""

import logging
import queue
import sqlite3
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class QueryType(Enum):
    """Types of database queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    INDEX = "INDEX"


class ConnectionState(Enum):
    """States of database connections."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    FAILED = "failed"
    CLOSED = "closed"


@dataclass
class ConnectionPoolConfig:
    """Configuration for database connection pool."""
    
    # Pool sizing
    min_connections: int = 2
    max_connections: int = 10
    initial_connections: int = 3
    
    # Connection behavior
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    max_connection_age: float = 3600.0  # 1 hour
    
    # Health monitoring
    health_check_interval: float = 60.0  # 1 minute
    health_check_timeout: float = 5.0
    
    # Performance tuning
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True
    cache_size_pages: int = 2000
    page_size: int = 4096
    temp_store: str = "memory"
    
    # Query optimization
    enable_query_cache: bool = True
    query_cache_size: int = 1000
    enable_query_plan_cache: bool = True
    query_plan_cache_size: int = 500


@dataclass
class QueryMetrics:
    """Metrics for database query performance."""
    
    query_hash: str
    query_type: QueryType
    execution_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    rows_affected_total: int = 0
    error_count: int = 0
    last_execution: Optional[float] = None
    query_plan: Optional[str] = None
    
    def update_execution(self, execution_time: float, rows_affected: int = 0,
                        had_error: bool = False):
        """Update metrics after query execution."""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.average_execution_time = self.total_execution_time / self.execution_count
        self.min_execution_time = min(self.min_execution_time, execution_time)
        self.max_execution_time = max(self.max_execution_time, execution_time)
        self.rows_affected_total += rows_affected
        self.last_execution = time.time()
        
        if had_error:
            self.error_count += 1


@dataclass
class ConnectionInfo:
    """Information about a database connection."""
    
    connection_id: str
    connection: sqlite3.Connection
    state: ConnectionState
    created_at: float
    last_used: float
    total_queries: int = 0
    total_query_time: float = 0.0
    
    @property
    def age(self) -> float:
        """Get connection age in seconds."""
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        """Get connection idle time in seconds."""
        return time.time() - self.last_used
    
    def update_usage(self, query_time: float = 0.0):
        """Update connection usage statistics."""
        self.last_used = time.time()
        self.total_queries += 1
        self.total_query_time += query_time


class DatabaseConnection:
    """Wrapper for database connection with optimization features."""
    
    def __init__(self, connection: sqlite3.Connection, connection_id: str,
                 config: ConnectionPoolConfig):
        """Initialize database connection wrapper.
        
        Args:
            connection: SQLite connection
            connection_id: Unique connection identifier
            config: Pool configuration
        """
        self.connection = connection
        self.connection_id = connection_id
        self.config = config
        self.logger = logging.getLogger(f'DBConnection.{connection_id}')
        
        # Optimize connection settings
        self._optimize_connection()
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        self.query_plan_cache: Dict[str, str] = {}
    
    def _optimize_connection(self):
        """Apply optimization settings to connection."""
        try:
            cursor = self.connection.cursor()
            
            # Enable WAL mode for better concurrency
            if self.config.enable_wal_mode:
                cursor.execute("PRAGMA journal_mode=WAL")
            
            # Enable foreign key constraints
            if self.config.enable_foreign_keys:
                cursor.execute("PRAGMA foreign_keys=ON")
            
            # Set cache size
            cursor.execute(f"PRAGMA cache_size={self.config.cache_size_pages}")
            
            # Set page size (only effective for new databases)
            cursor.execute(f"PRAGMA page_size={self.config.page_size}")
            
            # Set temp store location
            cursor.execute(f"PRAGMA temp_store={self.config.temp_store.upper()}")
            
            # Additional optimizations
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/performance
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping
            cursor.execute("PRAGMA optimize")  # Analyze and optimize
            
            cursor.close()
            self.logger.debug("Connection optimizations applied")
            
        except Exception as e:
            self.logger.error(f"Failed to optimize connection: {e}")
    
    def execute_query(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute a query with optimization.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Database cursor with results
        """
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            execution_time = time.time() - start_time
            self.logger.debug(f"Query executed in {execution_time:.4f}s")
            
            return cursor
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Query failed after {execution_time:.4f}s: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            
            affected_rows = cursor.rowcount
            execution_time = time.time() - start_time
            
            self.logger.debug(f"Batch query executed {len(params_list)} operations "
                            f"affecting {affected_rows} rows in {execution_time:.4f}s")
            
            cursor.close()
            return affected_rows
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Batch query failed after {execution_time:.4f}s: {e}")
            raise
    
    def get_query_plan(self, query: str, params: Tuple = ()) -> str:
        """Get query execution plan.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query execution plan
        """
        # Check cache first
        query_key = f"{query}:{params}"
        if query_key in self.query_plan_cache:
            return self.query_plan_cache[query_key]
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {query}", params)
            plan_rows = cursor.fetchall()
            
            plan = "\n".join([" | ".join(map(str, row)) for row in plan_rows])
            
            # Cache the plan
            if len(self.query_plan_cache) < self.config.query_plan_cache_size:
                self.query_plan_cache[query_key] = plan
            
            cursor.close()
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to get query plan: {e}")
            return ""
    
    def commit(self):
        """Commit transaction."""
        self.connection.commit()
    
    def rollback(self):
        """Rollback transaction."""
        self.connection.rollback()
    
    def close(self):
        """Close connection."""
        try:
            self.connection.close()
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")


class ConnectionPool:
    """Enterprise-grade database connection pool."""
    
    def __init__(self, database_path: str, config: ConnectionPoolConfig):
        """Initialize connection pool.
        
        Args:
            database_path: Path to SQLite database
            config: Pool configuration
        """
        self.database_path = database_path
        self.config = config
        self.logger = logging.getLogger('DatabaseConnectionPool')
        
        # Connection management
        self.connections: Dict[str, ConnectionInfo] = {}
        self.available_connections: queue.Queue = queue.Queue()
        self.pool_lock = RLock()
        
        # Monitoring
        self.is_running = False
        self.health_monitor_thread: Optional[threading.Thread] = None
        
        # Metrics
        self.total_connections_created = 0
        self.total_connections_closed = 0
        self.total_checkout_requests = 0
        self.total_checkout_time = 0.0
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        try:
            # Ensure database directory exists
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create initial connections
            for i in range(self.config.initial_connections):
                connection = self._create_connection()
                if connection:
                    self.available_connections.put(connection.connection_id)
            
            # Start health monitoring
            self.is_running = True
            self.health_monitor_thread = threading.Thread(
                target=self._health_monitor_loop,
                daemon=True
            )
            self.health_monitor_thread.start()
            
            self.logger.info(f"Connection pool initialized with "
                           f"{len(self.connections)} connections")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _create_connection(self) -> Optional[ConnectionInfo]:
        """Create a new database connection.
        
        Returns:
            ConnectionInfo instance or None if creation failed
        """
        if len(self.connections) >= self.config.max_connections:
            self.logger.warning("Maximum connections reached")
            return None
        
        try:
            connection_id = f"conn_{self.total_connections_created:04d}"
            
            # Create SQLite connection
            sqlite_conn = sqlite3.connect(
                self.database_path,
                timeout=self.config.connection_timeout,
                check_same_thread=False
            )
            
            # Create wrapper
            db_connection = DatabaseConnection(sqlite_conn, connection_id, self.config)
            
            # Create connection info
            conn_info = ConnectionInfo(
                connection_id=connection_id,
                connection=sqlite_conn,
                state=ConnectionState.AVAILABLE,
                created_at=time.time(),
                last_used=time.time()
            )
            
            with self.pool_lock:
                self.connections[connection_id] = conn_info
                self.total_connections_created += 1
            
            self.logger.debug(f"Created connection {connection_id}")
            return conn_info
            
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self) -> Generator[DatabaseConnection, None, None]:
        """Get a connection from the pool.
        
        Yields:
            DatabaseConnection instance
        """
        start_time = time.time()
        connection_id = None
        
        try:
            # Get connection from pool
            connection_id = self._checkout_connection()
            
            if not connection_id:
                raise RuntimeError("No connections available")
            
            # Get connection info
            with self.pool_lock:
                conn_info = self.connections[connection_id]
                conn_info.state = ConnectionState.IN_USE
                self.total_checkout_requests += 1
                self.total_checkout_time += time.time() - start_time
            
            # Create wrapper
            db_connection = DatabaseConnection(
                conn_info.connection, connection_id, self.config
            )
            
            yield db_connection
            
        except Exception as e:
            self.logger.error(f"Error with connection {connection_id}: {e}")
            # Mark connection as failed if it exists
            if connection_id and connection_id in self.connections:
                with self.pool_lock:
                    self.connections[connection_id].state = ConnectionState.FAILED
            raise
            
        finally:
            # Return connection to pool
            if connection_id:
                self._checkin_connection(connection_id)
    
    def _checkout_connection(self) -> Optional[str]:
        """Check out a connection from the pool.
        
        Returns:
            Connection ID or None if no connections available
        """
        try:
            # Try to get available connection
            connection_id = self.available_connections.get(timeout=5.0)
            
            with self.pool_lock:
                if connection_id in self.connections:
                    conn_info = self.connections[connection_id]
                    
                    # Validate connection health
                    if self._is_connection_healthy(conn_info):
                        return connection_id
                    else:
                        # Remove unhealthy connection
                        self._remove_connection(connection_id)
            
        except queue.Empty:
            # No available connections, try to create one
            if len(self.connections) < self.config.max_connections:
                conn_info = self._create_connection()
                if conn_info:
                    return conn_info.connection_id
        
        return None
    
    def _checkin_connection(self, connection_id: str):
        """Return a connection to the pool.
        
        Args:
            connection_id: ID of connection to return
        """
        with self.pool_lock:
            if connection_id in self.connections:
                conn_info = self.connections[connection_id]
                
                if conn_info.state == ConnectionState.FAILED:
                    # Remove failed connection
                    self._remove_connection(connection_id)
                else:
                    # Return healthy connection to pool
                    conn_info.state = ConnectionState.AVAILABLE
                    conn_info.update_usage()
                    self.available_connections.put(connection_id)
    
    def _is_connection_healthy(self, conn_info: ConnectionInfo) -> bool:
        """Check if connection is healthy.
        
        Args:
            conn_info: Connection information
            
        Returns:
            True if connection is healthy
        """
        try:
            # Check connection age
            if conn_info.age > self.config.max_connection_age:
                self.logger.debug(f"Connection {conn_info.connection_id} too old")
                return False
            
            # Check if connection is responsive
            cursor = conn_info.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            return result is not None
            
        except Exception as e:
            self.logger.warning(f"Connection {conn_info.connection_id} "
                              f"health check failed: {e}")
            return False
    
    def _remove_connection(self, connection_id: str):
        """Remove connection from pool.
        
        Args:
            connection_id: ID of connection to remove
        """
        try:
            conn_info = self.connections.pop(connection_id, None)
            if conn_info:
                conn_info.connection.close()
                conn_info.state = ConnectionState.CLOSED
                self.total_connections_closed += 1
                
                self.logger.debug(f"Removed connection {connection_id}")
                
        except Exception as e:
            self.logger.error(f"Error removing connection {connection_id}: {e}")
    
    def _health_monitor_loop(self):
        """Health monitoring loop for connections."""
        while self.is_running:
            try:
                time.sleep(self.config.health_check_interval)
                
                with self.pool_lock:
                    # Check all connections
                    unhealthy_connections = []
                    
                    for conn_id, conn_info in self.connections.items():
                        if (conn_info.state == ConnectionState.AVAILABLE and
                            conn_info.idle_time > self.config.idle_timeout):
                            
                            if not self._is_connection_healthy(conn_info):
                                unhealthy_connections.append(conn_id)
                    
                    # Remove unhealthy connections
                    for conn_id in unhealthy_connections:
                        self._remove_connection(conn_id)
                    
                    # Ensure minimum connections
                    while (len(self.connections) < self.config.min_connections and
                           len(self.connections) < self.config.max_connections):
                        
                        conn_info = self._create_connection()
                        if conn_info:
                            self.available_connections.put(conn_info.connection_id)
                        else:
                            break
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics.
        
        Returns:
            Dictionary of pool statistics
        """
        with self.pool_lock:
            active_connections = sum(
                1 for conn in self.connections.values()
                if conn.state == ConnectionState.IN_USE
            )
            
            available_connections = sum(
                1 for conn in self.connections.values()
                if conn.state == ConnectionState.AVAILABLE
            )
            
            avg_checkout_time = (
                self.total_checkout_time / max(self.total_checkout_requests, 1)
            )
            
            return {
                'total_connections': len(self.connections),
                'active_connections': active_connections,
                'available_connections': available_connections,
                'connections_created': self.total_connections_created,
                'connections_closed': self.total_connections_closed,
                'checkout_requests': self.total_checkout_requests,
                'average_checkout_time': avg_checkout_time,
                'pool_utilization': active_connections / max(len(self.connections), 1)
            }
    
    def close_pool(self):
        """Close the connection pool."""
        self.is_running = False
        
        # Wait for health monitor to stop
        if self.health_monitor_thread and self.health_monitor_thread.is_alive():
            self.health_monitor_thread.join(timeout=5.0)
        
        # Close all connections
        with self.pool_lock:
            for connection_id in list(self.connections.keys()):
                self._remove_connection(connection_id)
        
        self.logger.info("Connection pool closed")


class QueryOptimizer:
    """Advanced query optimization and analysis."""
    
    def __init__(self, connection_pool: ConnectionPool):
        """Initialize query optimizer.
        
        Args:
            connection_pool: Database connection pool
        """
        self.connection_pool = connection_pool
        self.logger = logging.getLogger('QueryOptimizer')
        
        # Query metrics
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.metrics_lock = Lock()
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        self.cache_lock = Lock()
        
    def execute_optimized_query(self, query: str, params: Tuple = (),
                               cache_key: Optional[str] = None) -> Any:
        """Execute query with optimization and caching.
        
        Args:
            query: SQL query string
            params: Query parameters
            cache_key: Optional cache key for results
            
        Returns:
            Query results
        """
        start_time = time.time()
        query_hash = self._get_query_hash(query, params)
        
        # Check cache first for SELECT queries
        if cache_key and query.strip().upper().startswith('SELECT'):
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                self.logger.debug(f"Cache hit for query: {cache_key}")
                return cached_result
        
        try:
            with self.connection_pool.get_connection() as db_conn:
                # Get query plan for analysis
                query_plan = db_conn.get_query_plan(query, params)
                
                # Execute query
                cursor = db_conn.execute_query(query, params)
                
                # Fetch results based on query type
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                else:
                    results = cursor.rowcount
                    db_conn.commit()
                
                execution_time = time.time() - start_time
                
                # Update metrics
                self._update_query_metrics(
                    query_hash, query, execution_time,
                    getattr(cursor, 'rowcount', 0), query_plan
                )
                
                # Cache results if requested
                if cache_key and query.strip().upper().startswith('SELECT'):
                    self._cache_result(cache_key, results)
                
                cursor.close()
                return results
                
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_query_metrics(
                query_hash, query, execution_time, 0, None, had_error=True
            )
            raise
    
    def execute_batch_optimized(self, query: str, 
                               params_list: List[Tuple]) -> int:
        """Execute batch query with optimization.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        start_time = time.time()
        query_hash = self._get_query_hash(query, tuple())
        
        try:
            with self.connection_pool.get_connection() as db_conn:
                affected_rows = db_conn.execute_many(query, params_list)
                db_conn.commit()
                
                execution_time = time.time() - start_time
                
                # Update metrics
                self._update_query_metrics(
                    query_hash, query, execution_time, affected_rows
                )
                
                return affected_rows
                
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_query_metrics(
                query_hash, query, execution_time, 0, None, had_error=True
            )
            raise
    
    def analyze_slow_queries(self, threshold_seconds: float = 1.0) -> List[QueryMetrics]:
        """Analyze slow-performing queries.
        
        Args:
            threshold_seconds: Threshold for slow queries
            
        Returns:
            List of slow query metrics
        """
        slow_queries = []
        
        with self.metrics_lock:
            for metrics in self.query_metrics.values():
                if metrics.average_execution_time > threshold_seconds:
                    slow_queries.append(metrics)
        
        # Sort by average execution time
        slow_queries.sort(key=lambda x: x.average_execution_time, reverse=True)
        
        return slow_queries
    
    def get_query_recommendations(self, query: str) -> List[str]:
        """Get optimization recommendations for a query.
        
        Args:
            query: SQL query string
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        query_upper = query.upper()
        
        # Check for missing WHERE clauses
        if ('SELECT' in query_upper and 'FROM' in query_upper and
            'WHERE' not in query_upper and 'LIMIT' not in query_upper):
            recommendations.append(
                "Consider adding WHERE clause to limit results"
            )
        
        # Check for SELECT *
        if 'SELECT *' in query_upper:
            recommendations.append(
                "Avoid SELECT * - specify only needed columns"
            )
        
        # Check for missing LIMIT on potentially large results
        if ('SELECT' in query_upper and 'LIMIT' not in query_upper and
            'COUNT(' not in query_upper):
            recommendations.append(
                "Consider adding LIMIT clause for large result sets"
            )
        
        # Check for inefficient JOINs
        if 'JOIN' in query_upper and 'ON' not in query_upper:
            recommendations.append(
                "Ensure JOINs have proper ON conditions"
            )
        
        # Check for subqueries that could be JOINs
        if query_upper.count('SELECT') > 1:
            recommendations.append(
                "Consider converting subqueries to JOINs for better performance"
            )
        
        return recommendations
    
    def create_indexes_for_query(self, query: str, table_name: str) -> List[str]:
        """Generate index creation statements for query optimization.
        
        Args:
            query: SQL query string
            table_name: Primary table name
            
        Returns:
            List of CREATE INDEX statements
        """
        indexes = []
        query_upper = query.upper()
        
        # Extract WHERE conditions (simplified)
        if 'WHERE' in query_upper:
            where_part = query.split('WHERE', 1)[1].split('ORDER BY')[0]
            where_part = where_part.split('GROUP BY')[0].split('HAVING')[0]
            
            # Look for equality conditions (simplified pattern matching)
            import re
            patterns = [
                r'(\w+)\s*=',  # column = value
                r'(\w+)\s*IN',  # column IN (...)
                r'(\w+)\s*LIKE',  # column LIKE pattern
            ]
            
            columns = set()
            for pattern in patterns:
                matches = re.findall(pattern, where_part, re.IGNORECASE)
                columns.update(matches)
            
            # Create single-column indexes
            for column in columns:
                index_name = f"idx_{table_name}_{column.lower()}"
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column})"
                indexes.append(index_sql)
        
        # Extract ORDER BY columns
        if 'ORDER BY' in query_upper:
            order_part = query.split('ORDER BY', 1)[1].split('LIMIT')[0]
            order_columns = [col.strip().split()[0] for col in order_part.split(',')]
            
            for column in order_columns:
                if column and column.replace('`', '').replace('"', '').isalnum():
                    index_name = f"idx_{table_name}_{column.lower()}_order"
                    index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column})"
                    indexes.append(index_sql)
        
        return indexes
    
    def _get_query_hash(self, query: str, params: Tuple) -> str:
        """Generate hash for query and parameters.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Hash string
        """
        import hashlib
        query_str = f"{query}:{params}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _update_query_metrics(self, query_hash: str, query: str,
                             execution_time: float, rows_affected: int = 0,
                             query_plan: Optional[str] = None,
                             had_error: bool = False):
        """Update query performance metrics.
        
        Args:
            query_hash: Query hash identifier
            query: Original query string
            execution_time: Query execution time
            rows_affected: Number of rows affected
            query_plan: Query execution plan
            had_error: Whether query had an error
        """
        with self.metrics_lock:
            if query_hash not in self.query_metrics:
                # Determine query type
                query_type = QueryType.SELECT  # Default
                query_upper = query.strip().upper()
                for qtype in QueryType:
                    if query_upper.startswith(qtype.value):
                        query_type = qtype
                        break
                
                self.query_metrics[query_hash] = QueryMetrics(
                    query_hash=query_hash,
                    query_type=query_type,
                    query_plan=query_plan
                )
            
            metrics = self.query_metrics[query_hash]
            metrics.update_execution(execution_time, rows_affected, had_error)
    
    def _get_cached_result(self, cache_key: str) -> Any:
        """Get cached query result.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None
        """
        with self.cache_lock:
            return self.query_cache.get(cache_key)
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache query result.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        with self.cache_lock:
            # Simple LRU eviction
            if len(self.query_cache) >= 1000:
                # Remove oldest entry (simplified)
                oldest_key = next(iter(self.query_cache))
                del self.query_cache[oldest_key]
            
            self.query_cache[cache_key] = result
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance analysis report.
        
        Returns:
            Performance report dictionary
        """
        with self.metrics_lock:
            if not self.query_metrics:
                return {'message': 'No query metrics available'}
            
            # Aggregate statistics
            total_queries = sum(m.execution_count for m in self.query_metrics.values())
            total_time = sum(m.total_execution_time for m in self.query_metrics.values())
            total_errors = sum(m.error_count for m in self.query_metrics.values())
            
            # Query type breakdown
            type_stats = defaultdict(lambda: {'count': 0, 'time': 0.0})
            for metrics in self.query_metrics.values():
                type_stats[metrics.query_type.value]['count'] += metrics.execution_count
                type_stats[metrics.query_type.value]['time'] += metrics.total_execution_time
            
            # Slowest queries
            slowest_queries = sorted(
                self.query_metrics.values(),
                key=lambda x: x.average_execution_time,
                reverse=True
            )[:10]
            
            return {
                'summary': {
                    'total_queries': total_queries,
                    'total_execution_time': total_time,
                    'average_query_time': total_time / max(total_queries, 1),
                    'error_rate': total_errors / max(total_queries, 1),
                },
                'query_types': dict(type_stats),
                'slowest_queries': [
                    {
                        'query_hash': m.query_hash,
                        'query_type': m.query_type.value,
                        'execution_count': m.execution_count,
                        'average_time': m.average_execution_time,
                        'max_time': m.max_execution_time,
                        'error_count': m.error_count
                    }
                    for m in slowest_queries
                ],
                'pool_stats': self.connection_pool.get_pool_stats()
            }


class DatabaseOptimizationManager:
    """Main manager for database optimization features."""
    
    def __init__(self, database_path: str, 
                 config: Optional[ConnectionPoolConfig] = None):
        """Initialize database optimization manager.
        
        Args:
            database_path: Path to SQLite database
            config: Pool configuration
        """
        self.database_path = database_path
        self.config = config or ConnectionPoolConfig()
        self.logger = logging.getLogger('DatabaseOptimizationManager')
        
        # Initialize components
        self.connection_pool = ConnectionPool(database_path, self.config)
        self.query_optimizer = QueryOptimizer(self.connection_pool)
        
        self.logger.info("Database optimization manager initialized")
    
    def execute_query(self, query: str, params: Tuple = (),
                     cache_key: Optional[str] = None) -> Any:
        """Execute optimized query.
        
        Args:
            query: SQL query string
            params: Query parameters
            cache_key: Optional cache key
            
        Returns:
            Query results
        """
        return self.query_optimizer.execute_optimized_query(
            query, params, cache_key
        )
    
    def execute_batch(self, query: str, params_list: List[Tuple]) -> int:
        """Execute batch query.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        return self.query_optimizer.execute_batch_optimized(query, params_list)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report.
        
        Returns:
            Performance report
        """
        return self.query_optimizer.get_performance_report()
    
    def optimize_database(self) -> List[str]:
        """Run database optimization procedures.
        
        Returns:
            List of optimization actions performed
        """
        actions = []
        
        try:
            with self.connection_pool.get_connection() as db_conn:
                # Analyze database
                db_conn.execute_query("ANALYZE")
                actions.append("Executed ANALYZE command")
                
                # Optimize database
                db_conn.execute_query("PRAGMA optimize")
                actions.append("Executed PRAGMA optimize")
                
                # Vacuum if needed
                cursor = db_conn.execute_query("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.close()
                
                cursor = db_conn.execute_query("PRAGMA freelist_count")
                free_pages = cursor.fetchone()[0]
                cursor.close()
                
                if free_pages > page_count * 0.1:  # More than 10% free pages
                    db_conn.execute_query("VACUUM")
                    actions.append("Executed VACUUM to reclaim space")
                
                db_conn.commit()
                
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            actions.append(f"Optimization failed: {e}")
        
        return actions
    
    def close(self):
        """Close the optimization manager."""
        self.connection_pool.close_pool()
        self.logger.info("Database optimization manager closed")