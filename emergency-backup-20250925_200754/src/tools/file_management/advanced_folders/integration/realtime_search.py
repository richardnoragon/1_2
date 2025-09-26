"""Real-time Search Manager.

Enterprise-grade real-time search manager that provides live search updates,
incremental search results, and responsive search user interface.

Features:
- Incremental search with live results
- Search result caching and optimization
- Thread-safe search operations
- Search suggestion and auto-completion
- Performance monitoring and optimization
- Debounced search to prevent excessive queries
"""

import logging
import time
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from ..core.folder_models import SearchFilter
from ..models.folder_models import (
    FileMetadata,
    FolderConfiguration,
    SearchParameter,
)
from .backend_integration import BackendIntegrationManager


class RealtimeSearchManager(QObject):
    """Enterprise-grade real-time search manager.

    Provides live search functionality with:
    - Incremental search results
    - Debounced query execution
    - Search result caching
    - Performance optimization
    - Thread-safe operations
    """

    # Signals for UI updates
    searchResultsChanged = pyqtSignal(
        str, list, dict
    )  # query, results, metadata
    searchSuggestionsUpdated = pyqtSignal(str, list)  # query, suggestions
    searchStatusChanged = pyqtSignal(str, str)  # status_type, message
    searchPerformanceUpdated = pyqtSignal(dict)  # performance_metrics

    def __init__(
        self,
        backend_manager: BackendIntegrationManager,
        parent: Optional[QObject] = None,
    ):
        """Initialize real-time search manager.

        Args:
            backend_manager: Backend integration manager
            parent: Parent QObject
        """
        super().__init__(parent)

        # Initialize logging
        self.logger = logging.getLogger("AdvancedFolders.RealtimeSearch")
        self.logger.info("Initializing Real-time Search Manager")

        # Backend integration
        self.backend_manager = backend_manager

        # Search state management
        self.current_query = ""
        self.current_folder_id = ""
        self.current_parameters: Dict[str, Any] = {}
        self.active_search_operation = None

        # Debounce timer for search queries
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._execute_search)
        self.search_delay_ms = 300  # 300ms delay for debouncing

        # Search result cache
        self.search_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_max_size = 100
        self.cache_ttl_seconds = 300  # 5 minutes

        # Search suggestions cache
        self.suggestions_cache: Dict[str, List[str]] = {}

        # Performance metrics
        self.performance_metrics = {
            "total_searches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_search_time": 0.0,
            "last_search_time": 0.0,
            "active_searches": 0,
        }

        # Connect backend signals
        self._connect_backend_signals()

        self.logger.info("Real-time Search Manager initialized successfully")

    def _connect_backend_signals(self):
        """Connect to backend manager signals."""
        self.backend_manager.searchResultsUpdated.connect(
            self._handle_search_results_updated
        )
        self.backend_manager.operationCompleted.connect(
            self._handle_operation_completed
        )
        self.backend_manager.operationFailed.connect(
            self._handle_operation_failed
        )

    def set_search_parameters(
        self, folder_id: str, parameters: Dict[str, Any]
    ):
        """Set search parameters for subsequent searches.

        Args:
            folder_id: Folder configuration ID
            parameters: Search parameters
        """
        self.current_folder_id = folder_id
        self.current_parameters = parameters.copy()

        # Clear cache if folder changed
        if folder_id != getattr(self, "_last_folder_id", None):
            self.clear_search_cache()
            self._last_folder_id = folder_id

    def perform_incremental_search(self, query: str):
        """Perform incremental search with debouncing.

        Args:
            query: Search query string
        """
        self.current_query = query

        # Cancel previous search timer
        self.search_timer.stop()

        # Handle empty query
        if not query.strip():
            self.searchResultsChanged.emit(query, [], {})
            self.searchStatusChanged.emit("ready", "Ready to search")
            return

        # Check cache first
        cache_key = self._generate_cache_key(
            query, self.current_folder_id, self.current_parameters
        )

        if self._is_cache_valid(cache_key):
            cached_result = self.search_cache[cache_key]
            self.searchResultsChanged.emit(
                query, cached_result["results"], cached_result["metadata"]
            )
            self.performance_metrics["cache_hits"] += 1
            self.searchStatusChanged.emit(
                "cached",
                f"Found {len(cached_result['results'])} cached results",
            )
            return

        # Update search suggestions
        self._update_search_suggestions(query)

        # Start debounced search
        self.searchStatusChanged.emit("searching", "Searching...")
        self.search_timer.start(self.search_delay_ms)

    def _execute_search(self):
        """Execute the actual search operation."""
        if not self.current_query.strip() or not self.current_folder_id:
            return

        # Cancel any active search
        if self.active_search_operation:
            self.backend_manager.cancel_search(self.active_search_operation)

        # Start new search
        start_time = time.time()
        self.performance_metrics["active_searches"] += 1

        self.active_search_operation = self.backend_manager.perform_search(
            self.current_folder_id, self.current_query, self.current_parameters
        )

        self.performance_metrics["total_searches"] += 1
        self.performance_metrics["cache_misses"] += 1

        self.logger.debug(
            f"Started search operation: {self.active_search_operation}"
        )

    def _handle_search_results_updated(
        self, query_id: str, results: List[Any]
    ):
        """Handle search results update from backend.

        Args:
            query_id: Query identifier
            results: Search results
        """
        if query_id.startswith(
            f"{self.current_folder_id}_{self.current_query}"
        ):
            # Calculate search time
            search_time = time.time() - getattr(
                self, "_search_start_time", time.time()
            )
            self.performance_metrics["last_search_time"] = search_time
            self._update_average_search_time(search_time)

            # Prepare metadata
            metadata = {
                "query": self.current_query,
                "folder_id": self.current_folder_id,
                "result_count": len(results),
                "search_time": search_time,
                "timestamp": time.time(),
                "cached": False,
            }

            # Cache results
            cache_key = self._generate_cache_key(
                self.current_query,
                self.current_folder_id,
                self.current_parameters,
            )
            self._cache_search_results(cache_key, results, metadata)

            # Emit results
            self.searchResultsChanged.emit(
                self.current_query, results, metadata
            )

            # Update status
            result_count = len(results)
            if result_count == 0:
                status_msg = "No results found"
            elif result_count == 1:
                status_msg = f"Found 1 result in {search_time:.2f}s"
            else:
                status_msg = (
                    f"Found {result_count:,} results in {search_time:.2f}s"
                )

            self.searchStatusChanged.emit("completed", status_msg)

            self.performance_metrics["active_searches"] -= 1
            self.active_search_operation = None

    def _handle_operation_completed(
        self, operation_type: str, operation_id: str, result: Dict[str, Any]
    ):
        """Handle operation completion from backend.

        Args:
            operation_type: Type of operation
            operation_id: Operation identifier
            result: Operation result
        """
        if (
            operation_type == "search"
            and operation_id == self.active_search_operation
        ):
            # Search operation completed successfully
            self.logger.debug(
                f"Search operation {operation_id} completed successfully"
            )

    def _handle_operation_failed(
        self, operation_type: str, operation_id: str, error: str
    ):
        """Handle operation failure from backend.

        Args:
            operation_type: Type of operation
            operation_id: Operation identifier
            error: Error message
        """
        if (
            operation_type == "search"
            and operation_id == self.active_search_operation
        ):
            self.logger.error(
                f"Search operation {operation_id} failed: {error}"
            )
            self.searchStatusChanged.emit("error", f"Search failed: {error}")
            self.performance_metrics["active_searches"] -= 1
            self.active_search_operation = None

    def _generate_cache_key(
        self, query: str, folder_id: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate cache key for search results.

        Args:
            query: Search query
            folder_id: Folder ID
            parameters: Search parameters

        Returns:
            Cache key string
        """
        # Create a deterministic key from query, folder, and parameters
        param_str = str(sorted(parameters.items()))
        return f"{folder_id}:{query}:{hash(param_str)}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is valid.

        Args:
            cache_key: Cache key to check

        Returns:
            True if cache entry is valid
        """
        if cache_key not in self.search_cache:
            return False

        cache_entry = self.search_cache[cache_key]
        age = time.time() - cache_entry["timestamp"]

        return age < self.cache_ttl_seconds

    def _cache_search_results(
        self, cache_key: str, results: List[Any], metadata: Dict[str, Any]
    ):
        """Cache search results.

        Args:
            cache_key: Cache key
            results: Search results
            metadata: Result metadata
        """
        # Implement LRU eviction if cache is full
        if len(self.search_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = min(
                self.search_cache.keys(),
                key=lambda k: self.search_cache[k]["timestamp"],
            )
            del self.search_cache[oldest_key]

        # Cache the results
        self.search_cache[cache_key] = {
            "results": results,
            "metadata": metadata,
            "timestamp": time.time(),
        }

    def _update_search_suggestions(self, query: str):
        """Update search suggestions based on current query.

        Args:
            query: Current search query
        """
        # Generate suggestions based on query
        suggestions = []

        # Get suggestions from cache if available
        if query in self.suggestions_cache:
            suggestions = self.suggestions_cache[query]
        else:
            # Generate basic suggestions (this could be enhanced with ML)
            suggestions = self._generate_basic_suggestions(query)
            self.suggestions_cache[query] = suggestions

        # Emit suggestions
        self.searchSuggestionsUpdated.emit(query, suggestions)

    def _generate_basic_suggestions(self, query: str) -> List[str]:
        """Generate basic search suggestions.

        Args:
            query: Search query

        Returns:
            List of suggestions
        """
        suggestions = []

        # Add common file extension suggestions
        if "." not in query:
            file_extensions = [
                ".pdf",
                ".docx",
                ".xlsx",
                ".png",
                ".jpg",
                ".txt",
            ]
            for ext in file_extensions:
                suggestions.append(f"{query}*{ext}")

        # Add wildcard suggestions
        if "*" not in query and "?" not in query:
            suggestions.extend([f"*{query}*", f"{query}*", f"*{query}"])

        return suggestions[:5]  # Limit to 5 suggestions

    def _update_average_search_time(self, search_time: float):
        """Update average search time metric.

        Args:
            search_time: Latest search time
        """
        current_avg = self.performance_metrics["average_search_time"]
        total_searches = self.performance_metrics["total_searches"]

        if total_searches > 1:
            # Calculate running average
            new_avg = (
                (current_avg * (total_searches - 1)) + search_time
            ) / total_searches
            self.performance_metrics["average_search_time"] = new_avg
        else:
            self.performance_metrics["average_search_time"] = search_time

    def clear_search_cache(self):
        """Clear the search result cache."""
        self.search_cache.clear()
        self.suggestions_cache.clear()
        self.logger.debug("Search cache cleared")

    def set_search_delay(self, delay_ms: int):
        """Set the search debounce delay.

        Args:
            delay_ms: Delay in milliseconds
        """
        self.search_delay_ms = max(
            100, min(1000, delay_ms)
        )  # Clamp between 100-1000ms

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get search performance metrics.

        Returns:
            Performance metrics dictionary
        """
        metrics = self.performance_metrics.copy()

        # Add cache statistics
        metrics["cache_size"] = len(self.search_cache)
        metrics["cache_hit_ratio"] = metrics["cache_hits"] / max(
            1, metrics["cache_hits"] + metrics["cache_misses"]
        )

        return metrics

    def cancel_current_search(self):
        """Cancel the current search operation."""
        if self.active_search_operation:
            self.backend_manager.cancel_search(self.active_search_operation)
            self.active_search_operation = None
            self.performance_metrics["active_searches"] = 0
            self.searchStatusChanged.emit("cancelled", "Search cancelled")

    def shutdown(self):
        """Shutdown the real-time search manager."""
        self.logger.info("Shutting down Real-time Search Manager")

        # Cancel any active searches
        self.cancel_current_search()

        # Stop timers
        if hasattr(self, "search_timer"):
            self.search_timer.stop()

        # Clear caches
        self.clear_search_cache()

        self.logger.info("Real-time Search Manager shutdown complete")
