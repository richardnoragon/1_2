"""
Size Analyzer Core Logic Module

This module contains the core business logic for directory size analysis,
separated from GUI components for better maintainability and testability.
Enhanced with comprehensive hub integration capabilities.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime


class SizeAnalyzer(QObject):
    """
    Core logic class for analyzing directory contents and calculating
    size statistics.

    This class provides the missing SizeAnalyzer that tests expect, with
    comprehensive PyQt5 progress tracking signals following file_utilities_2
    patterns.

    Features:
    - Directory scanning with progress tracking
    - File type analysis and statistics
    - Size calculations and formatting
    - Export functionality
    - Thread-safe operations with cancellation support
    """

    # Progress tracking signals following file_utilities_2 patterns
    progress_updated = pyqtSignal(int, int)  # current, total
    progress_percentage = pyqtSignal(int)  # percentage (0-100)
    progress_message = pyqtSignal(str)  # detailed status message
    milestone_reached = pyqtSignal(str, int)  # milestone desc, percentage
    time_estimate = pyqtSignal(str)  # estimated time remaining
    analysis_complete = pyqtSignal(dict)  # complete analysis results
    error_occurred = pyqtSignal(str)  # error messages
    operation_cancelled = pyqtSignal()  # cancellation notification

    def __init__(self, hub_connector=None):
        """Initialize the SizeAnalyzer with optional hub integration."""
        super().__init__()
        self._is_running = False
        self._should_cancel = False
        self._current_analysis = None
        self._hub_connector = hub_connector
        self._performance_metrics = {
            "start_time": None,
            "end_time": None,
            "files_per_second": 0,
            "bytes_per_second": 0,
            "peak_memory_usage": 0,
        }
        self._resource_usage = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_io": 0,
        }

    def analyze_directory(
        self,
        directory_path: str,
        top_files_count: int = 10,
        include_extensions: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a directory and return comprehensive statistics.

        This is the main method that tests expect, providing complete
        directory analysis with progress tracking and filtering capabilities.

        Args:
            directory_path: Path to directory to analyze
            top_files_count: Number of largest files to include in results
            include_extensions: List of file extensions to include (None=all)
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary containing comprehensive analysis results

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If directory cannot be accessed
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not os.path.isdir(directory_path):
            raise NotADirectoryError(
                f"Path is not a directory: {directory_path}"
            )

        self._is_running = True
        self._should_cancel = False

        # Initialize performance tracking
        self._performance_metrics["start_time"] = datetime.now()

        # Report to hub if connected
        if self._hub_connector:
            self._hub_connector.report_status_to_hub(
                "analyzing",
                {
                    "directory": directory_path,
                    "start_time": self._performance_metrics[
                        "start_time"
                    ].isoformat(),
                },
            )

        try:
            self.progress_message.emit("Starting directory analysis...")
            self.milestone_reached.emit("Analysis Started", 0)

            # Initialize analysis results
            analysis = {
                "path": directory_path,
                "total_size": 0,
                "file_count": 0,
                "directory_count": 0,
                "files": [],
                "file_types": {},
                "largest_files": [],
                "directory_tree": {},
            }

            # Phase 1: Count items for progress tracking
            self.progress_message.emit("Counting items...")
            total_items = self._count_items(directory_path)
            self.milestone_reached.emit("Item Count Complete", 10)

            # Phase 2: Scan directory structure
            self.progress_message.emit("Scanning directory structure...")
            items_processed = 0

            for root, dirs, files in os.walk(directory_path):
                if self._should_cancel:
                    self.operation_cancelled.emit()
                    return analysis

                # Count directories
                analysis["directory_count"] += len(dirs)

                # Process files
                for file_name in files:
                    if self._should_cancel:
                        self.operation_cancelled.emit()
                        return analysis

                    file_path = os.path.join(root, file_name)

                    # Apply extension filter if specified
                    if include_extensions:
                        file_ext = os.path.splitext(file_name)[1].lower()
                        if file_ext not in include_extensions:
                            continue

                    try:
                        file_info = self._analyze_file(file_path)
                        analysis["files"].append(file_info)
                        analysis["total_size"] += file_info["size"]
                        analysis["file_count"] += 1

                        # Update file type statistics
                        self._update_file_type_stats(
                            file_info, analysis["file_types"]
                        )

                    except (OSError, PermissionError):
                        # Skip inaccessible files
                        continue

                    items_processed += 1

                    # Update progress
                    if total_items > 0:
                        percentage = min(
                            int((items_processed / total_items) * 70) + 10, 80
                        )
                        self.progress_percentage.emit(percentage)
                        self.progress_updated.emit(
                            items_processed, total_items
                        )

                        if progress_callback:
                            progress_callback(percentage)

                    # Update progress message periodically
                    if items_processed % 100 == 0:
                        self.progress_message.emit(
                            f"Processed {items_processed} items..."
                        )

            self.milestone_reached.emit("File Scanning Complete", 80)

            # Phase 3: Generate additional analysis
            self.progress_message.emit("Generating analysis results...")

            # Find largest files
            analysis["largest_files"] = self._find_largest_files(
                analysis["files"], top_files_count
            )

            # Generate directory tree
            analysis["directory_tree"] = self._generate_directory_tree(
                directory_path
            )

            self.milestone_reached.emit("Analysis Processing Complete", 95)

            # Phase 4: Finalize results
            self.progress_message.emit("Finalizing results...")
            self.progress_percentage.emit(100)

            if progress_callback:
                progress_callback(100)

            # Calculate performance metrics
            self._performance_metrics["end_time"] = datetime.now()
            duration = (
                self._performance_metrics["end_time"]
                - self._performance_metrics["start_time"]
            ).total_seconds()

            if duration > 0:
                self._performance_metrics["files_per_second"] = (
                    analysis.get("file_count", 0) / duration
                )
                self._performance_metrics["bytes_per_second"] = (
                    analysis.get("total_size", 0) / duration
                )

            # Add performance metrics to analysis
            analysis["performance_metrics"] = self._performance_metrics.copy()

            self.milestone_reached.emit("Analysis Complete", 100)
            self.analysis_complete.emit(analysis)

            # Report completion to hub if connected
            if self._hub_connector:
                self._hub_connector.report_status_to_hub(
                    "completed",
                    {
                        "analysis_results": {
                            "file_count": analysis.get("file_count", 0),
                            "total_size": analysis.get("total_size", 0),
                            "duration_seconds": duration,
                        },
                        "performance_metrics": self._performance_metrics,
                    },
                )

            return analysis

        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.error_occurred.emit(error_msg)

            # Report error to hub if connected
            if self._hub_connector:
                self._hub_connector.report_error_to_hub(
                    error_msg,
                    {
                        "directory": directory_path,
                        "error_type": type(e).__name__,
                    },
                )

            raise
        finally:
            self._is_running = False

    def _count_items(self, directory_path: str) -> int:
        """Count total items in directory for progress tracking."""
        total = 0
        try:
            for root, dirs, files in os.walk(directory_path):
                total += len(files)
                if self._should_cancel:
                    break
        except (OSError, PermissionError):
            pass
        return total

    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file and return its information."""
        stat_info = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        return {
            "name": file_name,
            "path": file_path,
            "size": stat_info.st_size,
            "extension": file_ext,
            "modified": stat_info.st_mtime,
        }

    def _update_file_type_stats(
        self, file_info: Dict[str, Any], file_types: Dict[str, Dict[str, Any]]
    ) -> None:
        """Update file type statistics."""
        ext = file_info["extension"] or "no_extension"

        if ext not in file_types:
            file_types[ext] = {"count": 0, "total_size": 0, "average_size": 0}

        file_types[ext]["count"] += 1
        file_types[ext]["total_size"] += file_info["size"]
        file_types[ext]["average_size"] = (
            file_types[ext]["total_size"] / file_types[ext]["count"]
        )

    def _find_largest_files(
        self, files: List[Dict[str, Any]], count: int
    ) -> List[Dict[str, Any]]:
        """Find the largest files in the analysis."""
        return sorted(files, key=lambda x: x["size"], reverse=True)[:count]

    def _generate_directory_tree(self, directory_path: str) -> Dict[str, Any]:
        """Generate a directory tree structure."""
        tree = {
            "name": os.path.basename(directory_path) or directory_path,
            "path": directory_path,
            "size": 0,
            "children": {},
        }

        try:
            for item in os.listdir(directory_path):
                if self._should_cancel:
                    break

                item_path = os.path.join(directory_path, item)

                if os.path.isdir(item_path):
                    subtree = self._generate_directory_tree(item_path)
                    tree["children"][item] = subtree
                    tree["size"] += subtree["size"]
                else:
                    try:
                        file_size = os.path.getsize(item_path)
                        tree["children"][item] = {
                            "name": item,
                            "path": item_path,
                            "size": file_size,
                            "type": "file",
                        }
                        tree["size"] += file_size
                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        return tree

    def format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB", "2.3 GB")
        """
        if size_bytes == 0:
            return "0.0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.1f} {units[unit_index]}"

    def export_analysis(
        self, analysis: Dict[str, Any], export_path: str
    ) -> None:
        """
        Export analysis results to a JSON file.

        Args:
            analysis: Analysis results dictionary
            export_path: Path where to save the export file

        Raises:
            IOError: If file cannot be written
        """
        try:
            # Prepare analysis for JSON serialization
            exportable_analysis = self._prepare_for_export(analysis)

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(exportable_analysis, f, indent=2, ensure_ascii=False)

            self.progress_message.emit(f"Analysis exported to {export_path}")

        except Exception as e:
            error_msg = f"Failed to export analysis: {str(e)}"
            self.error_occurred.emit(error_msg)
            raise IOError(error_msg)

    def _prepare_for_export(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare analysis data for JSON export."""
        exportable = analysis.copy()

        # Convert file info to serializable format
        if "files" in exportable:
            for file_info in exportable["files"]:
                if "modified" in file_info:
                    # Convert timestamp to ISO format
                    import datetime

                    file_info["modified"] = datetime.datetime.fromtimestamp(
                        file_info["modified"]
                    ).isoformat()

        # Add metadata
        exportable["export_metadata"] = {
            "export_time": datetime.datetime.now().isoformat(),
            "analyzer_version": "2.0.0",
            "total_files_analyzed": len(exportable.get("files", [])),
            "formatted_total_size": self.format_size(
                exportable.get("total_size", 0)
            ),
        }

        return exportable

    def cancel_operation(self) -> None:
        """Cancel the current analysis operation."""
        self._should_cancel = True
        self.progress_message.emit("Cancelling operation...")

        # Report cancellation to hub if connected
        if self._hub_connector:
            self._hub_connector.report_status_to_hub(
                "cancelled",
                {
                    "reason": "user_requested",
                    "cancelled_at": datetime.now().isoformat(),
                },
            )

    def is_running(self) -> bool:
        """Check if an analysis operation is currently running."""
        return self._is_running

    def set_hub_connector(self, hub_connector):
        """Set the hub connector for this analyzer."""
        self._hub_connector = hub_connector

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self._performance_metrics.copy()

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        return self._resource_usage.copy()

    def update_resource_usage(
        self, cpu_usage: float = 0, memory_usage: float = 0, disk_io: float = 0
    ):
        """Update resource usage statistics."""
        self._resource_usage.update(
            {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_io": disk_io,
                "last_updated": datetime.now().isoformat(),
            }
        )

        # Report resource usage to hub if connected
        if self._hub_connector:
            self._hub_connector.report_status_to_hub(
                "resource_update", self._resource_usage
            )

    def request_hub_coordination(
        self, coordination_type: str, data: Dict[str, Any] = None
    ) -> bool:
        """Request coordination with other tools through hub."""
        if not self._hub_connector:
            return False

        try:
            self._hub_connector.broadcast_event(
                coordination_type,
                {
                    "tool": "Size Analyzer",
                    "request_data": data or {},
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return True
        except Exception:
            return False


class SizeAnalyzerWorker(QThread):
    """
    Worker thread for running size analysis operations without blocking
    the GUI.

    This class provides thread-safe execution of directory analysis
    operations with proper signal handling and cancellation support.
    """

    # Signals for communicating with the main thread
    analysis_finished = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)

    def __init__(
        self,
        analyzer: SizeAnalyzer,
        directory_path: str,
        hub_connector=None,
        **kwargs,
    ):
        """
        Initialize the worker thread with hub integration.

        Args:
            analyzer: SizeAnalyzer instance to use
            directory_path: Directory to analyze
            hub_connector: Hub connector for integration
            **kwargs: Additional arguments for analyze_directory
        """
        super().__init__()
        self.analyzer = analyzer
        self.directory_path = directory_path
        self.kwargs = kwargs
        self.hub_connector = hub_connector

        # Set hub connector on analyzer if provided
        if hub_connector:
            self.analyzer.set_hub_connector(hub_connector)

        # Connect analyzer signals to worker signals
        self.analyzer.progress_percentage.connect(self.progress_update.emit)
        self.analyzer.progress_message.connect(self.status_update.emit)
        self.analyzer.analysis_complete.connect(self.analysis_finished.emit)
        self.analyzer.error_occurred.connect(self.analysis_error.emit)

    def run(self):
        """Run the analysis in the worker thread."""
        try:
            # Add progress callback to kwargs
            self.kwargs["progress_callback"] = self.progress_update.emit

            # Perform analysis
            result = self.analyzer.analyze_directory(
                self.directory_path, **self.kwargs
            )

            if not self.analyzer._should_cancel:
                self.analysis_finished.emit(result)

        except Exception as e:
            self.analysis_error.emit(str(e))

    def cancel(self):
        """Cancel the analysis operation."""
        self.analyzer.cancel_operation()
        self.quit()
        self.wait()
