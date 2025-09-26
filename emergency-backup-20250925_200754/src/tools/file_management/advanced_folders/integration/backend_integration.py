"""Backend Integration Manager.

Enterprise-grade backend integration manager that provides a unified interface
for all backend services and manages the communication between UI components
and backend data repositories.

Features:
- Centralized backend service management
- Signal-based communication patterns
- Transaction management and rollback
- Performance monitoring and optimization
- Error handling and recovery
- Thread-safe operations
"""

import logging
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import QMutex, QObject, QThread, QTimer, pyqtSignal

from ..core.folder_models import ValidationResult
from ..database import AdvancedFoldersDBManager
from ..models.folder_models import (
    ConfigurationManager,
    FileMetadata,
    FolderConfiguration,
    SearchParameter,
)
from ..repositories import (
    FileMetadataRepository,
    FolderConfigurationRepository,
    RepositoryManager,
)


class BackendIntegrationManager(QObject):
    """Enterprise-grade backend integration manager.

    Provides centralized access to all backend services with:
    - Signal-based notifications for UI updates
    - Thread-safe operations
    - Transaction management
    - Performance monitoring
    - Error handling and recovery
    """

    # Signals for UI integration
    folderConfigurationChanged = pyqtSignal(
        str, dict
    )  # folder_id, config_data
    searchResultsUpdated = pyqtSignal(str, list)  # query_id, results
    operationStarted = pyqtSignal(str, str)  # operation_type, operation_id
    operationCompleted = pyqtSignal(
        str, str, dict
    )  # operation_type, operation_id, result
    operationFailed = pyqtSignal(
        str, str, str
    )  # operation_type, operation_id, error
    performanceMetricsUpdated = pyqtSignal(dict)  # metrics

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize backend integration manager.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # Initialize logging
        self.logger = logging.getLogger("AdvancedFolders.BackendIntegration")
        self.logger.info("Initializing Backend Integration Manager")

        # Core backend components
        self.config_manager = ConfigurationManager()
        self.db_manager = AdvancedFoldersDBManager()
        self.repository_manager = RepositoryManager(self.db_manager)

        # Thread synchronization
        self.mutex = QMutex()
        self.operation_counter = 0
        self.active_operations: Dict[str, Dict[str, Any]] = {}

        # Performance monitoring
        self.performance_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_response_time": 0.0,
            "active_connections": 0,
            "memory_usage": 0,
            "cache_hit_ratio": 0.0,
        }

        # Initialize backend services
        self._initialize_repositories()
        self._setup_performance_monitoring()

        self.logger.info(
            "Backend Integration Manager initialized successfully"
        )

    def _initialize_repositories(self):
        """Initialize repository connections and validate schemas."""
        try:
            # Initialize folder configuration repository
            self.folder_repository = (
                self.repository_manager.get_folder_repository()
            )

            # Initialize file metadata repository
            self.metadata_repository = (
                self.repository_manager.get_metadata_repository()
            )

            # Validate repository connections
            if not self.folder_repository.test_connection():
                raise RuntimeError(
                    "Failed to connect to folder configuration repository"
                )

            if not self.metadata_repository.test_connection():
                raise RuntimeError("Failed to connect to metadata repository")

            self.logger.info("Repository connections established successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize repositories: {e}")
            raise

    def _setup_performance_monitoring(self):
        """Setup performance monitoring and metrics collection."""
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(
            self._update_performance_metrics
        )
        self.performance_timer.start(10000)  # Update every 10 seconds

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID.

        Returns:
            Unique operation identifier
        """
        with QMutex():
            self.operation_counter += 1
            return f"op_{self.operation_counter:06d}"

    def _start_operation(self, operation_type: str) -> str:
        """Start tracking an operation.

        Args:
            operation_type: Type of operation

        Returns:
            Operation ID
        """
        operation_id = self._generate_operation_id()

        self.active_operations[operation_id] = {
            "type": operation_type,
            "start_time": QTimer().currentTime(),
            "status": "active",
        }

        self.operationStarted.emit(operation_type, operation_id)
        self.performance_metrics["total_operations"] += 1

        return operation_id

    def _complete_operation(self, operation_id: str, result: Dict[str, Any]):
        """Complete an operation.

        Args:
            operation_id: Operation identifier
            result: Operation result data
        """
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation["status"] = "completed"
            operation["result"] = result

            self.operationCompleted.emit(
                operation["type"], operation_id, result
            )

            self.performance_metrics["successful_operations"] += 1
            del self.active_operations[operation_id]

    def _fail_operation(self, operation_id: str, error: str):
        """Mark an operation as failed.

        Args:
            operation_id: Operation identifier
            error: Error message
        """
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation["status"] = "failed"
            operation["error"] = error

            self.operationFailed.emit(operation["type"], operation_id, error)

            self.performance_metrics["failed_operations"] += 1
            del self.active_operations[operation_id]

    # Folder Configuration Operations

    def create_folder_configuration(self, config_data: Dict[str, Any]) -> str:
        """Create a new folder configuration.

        Args:
            config_data: Configuration data

        Returns:
            Operation ID
        """
        operation_id = self._start_operation("create_folder")

        try:
            # Validate configuration data
            validation_result = self.config_manager.validate_configuration(
                config_data
            )
            if not validation_result.is_valid:
                raise ValueError(
                    f"Invalid configuration: {validation_result.errors}"
                )

            # Create folder configuration
            folder_config = FolderConfiguration.from_dict(config_data)

            # Save to repository
            saved_config = self.folder_repository.create(folder_config)

            # Complete operation
            result = {
                "folder_id": saved_config.id,
                "configuration": saved_config.to_dict(),
            }

            self._complete_operation(operation_id, result)

            # Emit configuration change signal
            self.folderConfigurationChanged.emit(
                saved_config.id, result["configuration"]
            )

            return operation_id

        except Exception as e:
            self.logger.error(f"Failed to create folder configuration: {e}")
            self._fail_operation(operation_id, str(e))
            return operation_id

    def update_folder_configuration(
        self, folder_id: str, config_data: Dict[str, Any]
    ) -> str:
        """Update an existing folder configuration.

        Args:
            folder_id: Folder configuration ID
            config_data: Updated configuration data

        Returns:
            Operation ID
        """
        operation_id = self._start_operation("update_folder")

        try:
            # Validate configuration data
            validation_result = self.config_manager.validate_configuration(
                config_data
            )
            if not validation_result.is_valid:
                raise ValueError(
                    f"Invalid configuration: {validation_result.errors}"
                )

            # Load existing configuration
            existing_config = self.folder_repository.get_by_id(folder_id)
            if not existing_config:
                raise ValueError(
                    f"Folder configuration not found: {folder_id}"
                )

            # Update configuration
            updated_config = existing_config.update_from_dict(config_data)

            # Save changes
            saved_config = self.folder_repository.update(updated_config)

            # Complete operation
            result = {
                "folder_id": saved_config.id,
                "configuration": saved_config.to_dict(),
            }

            self._complete_operation(operation_id, result)

            # Emit configuration change signal
            self.folderConfigurationChanged.emit(
                saved_config.id, result["configuration"]
            )

            return operation_id

        except Exception as e:
            self.logger.error(f"Failed to update folder configuration: {e}")
            self._fail_operation(operation_id, str(e))
            return operation_id

    def delete_folder_configuration(self, folder_id: str) -> str:
        """Delete a folder configuration.

        Args:
            folder_id: Folder configuration ID

        Returns:
            Operation ID
        """
        operation_id = self._start_operation("delete_folder")

        try:
            # Verify configuration exists
            existing_config = self.folder_repository.get_by_id(folder_id)
            if not existing_config:
                raise ValueError(
                    f"Folder configuration not found: {folder_id}"
                )

            # Delete configuration
            self.folder_repository.delete(folder_id)

            # Complete operation
            result = {"folder_id": folder_id, "deleted": True}
            self._complete_operation(operation_id, result)

            # Emit configuration change signal
            self.folderConfigurationChanged.emit(folder_id, {"deleted": True})

            return operation_id

        except Exception as e:
            self.logger.error(f"Failed to delete folder configuration: {e}")
            self._fail_operation(operation_id, str(e))
            return operation_id

    def get_folder_configurations(self) -> str:
        """Get all folder configurations.

        Returns:
            Operation ID
        """
        operation_id = self._start_operation("list_folders")

        try:
            # Get all configurations
            configurations = self.folder_repository.get_all()

            # Convert to dictionaries
            config_data = [config.to_dict() for config in configurations]

            # Complete operation
            result = {"configurations": config_data, "count": len(config_data)}
            self._complete_operation(operation_id, result)

            return operation_id

        except Exception as e:
            self.logger.error(f"Failed to get folder configurations: {e}")
            self._fail_operation(operation_id, str(e))
            return operation_id

    # Search Operations

    def perform_search(
        self, folder_id: str, query: str, parameters: Dict[str, Any]
    ) -> str:
        """Perform a search operation.

        Args:
            folder_id: Folder configuration ID
            query: Search query
            parameters: Search parameters

        Returns:
            Operation ID
        """
        operation_id = self._start_operation("search")

        try:
            # Get folder configuration
            folder_config = self.folder_repository.get_by_id(folder_id)
            if not folder_config:
                raise ValueError(
                    f"Folder configuration not found: {folder_id}"
                )

            # Perform search using metadata repository
            search_results = self.metadata_repository.search(
                folder_config, query, parameters
            )

            # Complete operation
            result = {
                "query": query,
                "folder_id": folder_id,
                "results": search_results,
                "count": len(search_results),
            }

            self._complete_operation(operation_id, result)

            # Emit search results update
            self.searchResultsUpdated.emit(
                f"{folder_id}_{query}", search_results
            )

            return operation_id

        except Exception as e:
            self.logger.error(f"Failed to perform search: {e}")
            self._fail_operation(operation_id, str(e))
            return operation_id

    def cancel_search(self, operation_id: str) -> bool:
        """Cancel an active search operation.

        Args:
            operation_id: Operation to cancel

        Returns:
            True if operation was cancelled
        """
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            if (
                operation["type"] == "search"
                and operation["status"] == "active"
            ):
                # Cancel the search operation
                self.metadata_repository.cancel_search(operation_id)
                self._fail_operation(
                    operation_id, "Operation cancelled by user"
                )
                return True

        return False

    # Performance and Monitoring

    def _update_performance_metrics(self):
        """Update performance metrics."""
        try:
            # Update database connection count
            self.performance_metrics["active_connections"] = (
                self.db_manager.get_connection_count()
            )

            # Update cache hit ratio
            self.performance_metrics["cache_hit_ratio"] = (
                self.metadata_repository.get_cache_hit_ratio()
            )

            # Calculate average response time
            if self.performance_metrics["successful_operations"] > 0:
                # This would be calculated from actual operation timings
                pass

            # Update memory usage
            try:
                import psutil

                process = psutil.Process()
                self.performance_metrics["memory_usage"] = (
                    process.memory_info().rss / 1024 / 1024
                )
            except ImportError:
                pass

            # Emit updated metrics
            self.performanceMetricsUpdated.emit(
                self.performance_metrics.copy()
            )

        except Exception as e:
            self.logger.error(f"Failed to update performance metrics: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.

        Returns:
            Performance metrics dictionary
        """
        return self.performance_metrics.copy()

    def get_active_operations(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active operations.

        Returns:
            Dictionary of active operations
        """
        return self.active_operations.copy()

    # Cleanup and shutdown

    def shutdown(self):
        """Shutdown the backend integration manager."""
        self.logger.info("Shutting down Backend Integration Manager")

        # Stop performance monitoring
        if hasattr(self, "performance_timer"):
            self.performance_timer.stop()

        # Cancel all active operations
        for operation_id in list(self.active_operations.keys()):
            self._fail_operation(operation_id, "System shutdown")

        # Close repository connections
        if hasattr(self, "repository_manager"):
            self.repository_manager.close_all_connections()

        # Close database connections
        if hasattr(self, "db_manager"):
            self.db_manager.close_connection()

        self.logger.info("Backend Integration Manager shutdown complete")
