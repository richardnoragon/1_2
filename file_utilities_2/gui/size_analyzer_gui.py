"""
Size Analyzer GUI Module

This module contains the modern PyQt5 GUI for the Size Analyzer utility,
inheriting from StandardWindow and integrating with ThemeManager and Hub.
"""

import os
import sys
from typing import Any, Dict, Optional

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import Colors, Fonts, ThemeManager
from file_utilities_2.integration.hub_connector import HubConnector


class SizeAnalyzerGUI(StandardWindow):
    """
    Modern GUI for Size Analyzer utility with comprehensive hub integration.

    Inherits from StandardWindow and provides:
    - Modern PyQt5 interface with progress visualization
    - Integration with ThemeManager for consistent styling
    - Connection to core logic via signals/slots
    - Export functionality and user interaction handling
    - Comprehensive hub communication and integration
    """

    # Hub notification signals
    tool_started = pyqtSignal(str)  # tool name
    tool_completed = pyqtSignal(str, dict)  # tool name, results
    tool_error = pyqtSignal(str, str)  # tool name, error message
    tool_progress = pyqtSignal(str, int, str)  # tool name, percentage, message
    tool_status_changed = pyqtSignal(str, str)  # tool name, status

    # Hub integration events
    hub_connection_changed = pyqtSignal(bool)  # connection status
    hub_resource_granted = pyqtSignal(str, dict)  # resource type, details
    hub_event_received = pyqtSignal(str, dict)  # event type, data

    def __init__(self, hub_instance=None):
        """Initialize the Size Analyzer GUI with hub integration."""
        super().__init__(title="Size Analyzer", icon_path=self._get_icon_path())

        # Initialize core components
        self.analyzer = SizeAnalyzer()
        self.worker_thread: Optional[SizeAnalyzerWorker] = None
        self.current_analysis: Optional[Dict[str, Any]] = None
        self.selected_directory: Optional[str] = None

        # Initialize hub integration
        self.hub_connector = HubConnector("Size Analyzer", hub_instance)
        self.hub_instance = hub_instance
        self._setup_hub_integration()

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        # Register with hub and show ready status
        self.register_with_hub(hub_instance)
        self.show_status_message("Ready to analyze directories")
        self.report_status_to_hub("ready", {"initialization_complete": True})

    def _get_icon_path(self) -> str:
        """Get the icon path for the application."""
        # Try multiple possible icon locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "icons", "size_analyzer.png"),
            os.path.join(
                os.path.dirname(__file__), "..", "..", "icons", "size_analyzer.png"
            ),
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "file_utilities_1",
                "icons",
                "size_analyzer.png",
            ),
            os.path.join(os.path.dirname(__file__), "icons", "size_analyzer.png"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Return default icon if none found
        return os.path.join(os.path.dirname(__file__), "..", "icons", "app_icon.png")

    def _setup_hub_integration(self):
        """Setup hub integration components."""
        # Connect hub connector signals
        self.hub_connector.hub_connection_status.connect(
            self.hub_connection_changed.emit
        )
        self.hub_connector.hub_resource_available.connect(
            self.hub_resource_granted.emit
        )
        self.hub_connector.hub_broadcast_received.connect(self.hub_event_received.emit)
        self.hub_connector.tool_status_changed.connect(self.tool_status_changed.emit)

        # Register event handlers
        self.hub_connector.register_event_handler(
            "resource_request", self._handle_resource_request
        )
        self.hub_connector.register_event_handler(
            "tool_coordination", self._handle_tool_coordination
        )
        self.hub_connector.register_event_handler(
            "configuration_update", self._handle_configuration_update
        )

    def register_with_hub(self, hub_instance):
        """Register tool with central hub for communication."""
        try:
            success = self.hub_connector.register_with_hub(hub_instance)
            if success:
                self.hub_instance = hub_instance
                self.tool_started.emit("Size Analyzer")
                return True
            return False
        except Exception as e:
            self.show_error_dialog(
                "Hub Registration Error", f"Failed to register with hub: {e}"
            )
            return False

    def report_status_to_hub(self, status: str, details: Dict[str, Any] = None):
        """Report current status to hub."""
        try:
            self.hub_connector.report_status_to_hub(status, details)
        except Exception as e:
            self.show_error_dialog(
                "Hub Communication Error", f"Failed to report status: {e}"
            )

    def request_hub_resources(
        self, resource_type: str, requirements: Dict[str, Any] = None
    ) -> bool:
        """Request shared resources from hub."""
        try:
            return self.hub_connector.request_hub_resources(resource_type, requirements)
        except Exception as e:
            self.show_error_dialog(
                "Hub Resource Error", f"Failed to request resources: {e}"
            )
            return False

    def broadcast_hub_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast event to other tools through hub."""
        try:
            self.hub_connector.broadcast_event(event_type, event_data)
        except Exception as e:
            self.show_error_dialog(
                "Hub Broadcast Error", f"Failed to broadcast event: {e}"
            )

    def _handle_resource_request(self, message):
        """Handle resource request from hub."""
        # Implement resource sharing logic
        pass

    def _handle_tool_coordination(self, message):
        """Handle tool coordination messages."""
        # Implement tool coordination logic
        pass

    def _handle_configuration_update(self, message):
        """Handle configuration updates from hub."""
        try:
            config_data = message.data.get("configuration", {})
            # Apply configuration updates
            self._apply_hub_configuration(config_data)
        except Exception as e:
            self.show_error_dialog(
                "Configuration Error", f"Failed to apply configuration: {e}"
            )

    def _apply_hub_configuration(self, config: Dict[str, Any]):
        """Apply configuration received from hub."""
        # Update tool settings based on hub configuration
        if "theme" in config:
            # Apply theme changes
            pass
        if "performance" in config:
            # Apply performance settings
            pass

    def _setup_ui(self):
        """Setup the user interface components with comprehensive theming."""
        # Load UI from file if it exists, otherwise create programmatically
        ui_file = os.path.join(os.path.dirname(__file__), "size_analyzer.ui")

        if os.path.exists(ui_file):
            self._load_ui_file(ui_file)
        else:
            self._create_ui_programmatically()

        # Apply comprehensive theming after UI setup
        self._setup_themed_components()

    def _load_ui_file(self, ui_file: str):
        """Load UI from the .ui file with theme integration."""
        try:
            # Load UI directly into this window
            uic.loadUi(ui_file, self)

            # Extract and reference UI components
            self.directory_line_edit = self.directoryLineEdit
            self.browse_button = self.browseButton
            self.analyze_button = self.size_analyzer_button
            self.output_list_view = self.output_ListView

            # Reference new UI components from updated .ui file
            self.progress_bar = self.progressBar
            self.progress_label = self.progressLabel
            self.details_text = self.detailsText
            self.export_button = self.exportButton
            self.cancel_button = self.cancelButton
            self.progress_group = self.progressGroup
            self.results_group = self.resultsGroup

        except Exception as e:
            self.show_error_dialog("UI Loading Error", f"Failed to load UI file: {e}")
            self._create_ui_programmatically()

    def _setup_themed_components(self):
        """Setup all UI components with consistent theming and responsiveness."""
        # Apply theme to main window with responsive design
        ThemeManager.apply_utility_window_theme(self)

        # Register for theme change notifications
        ThemeManager.register_theme_callback(self._on_theme_changed)

        # Style header label
        if hasattr(self, "headerLabel"):
            ThemeManager.style_label(self.headerLabel, is_header=True)

        # Style directory selection components
        if hasattr(self, "directoryLabel"):
            ThemeManager.style_label(self.directoryLabel, is_header=True)

        ThemeManager.style_input_field(self.directory_line_edit)
        ThemeManager.style_primary_button(self.browse_button)

        # Style progress components
        if hasattr(self, "progress_group"):
            ThemeManager.style_group_box(self.progress_group)

        if hasattr(self, "progress_label"):
            ThemeManager.style_label(self.progress_label)

        if hasattr(self, "progress_bar"):
            ThemeManager.style_progress_bar(self.progress_bar)

        # Style results components
        if hasattr(self, "results_group"):
            ThemeManager.style_group_box(self.results_group)

        # Style action buttons
        ThemeManager.style_primary_button(self.analyze_button)

        if hasattr(self, "export_button"):
            ThemeManager.style_secondary_button(self.export_button)

        if hasattr(self, "cancel_button"):
            ThemeManager.style_secondary_button(self.cancel_button)

        # Apply responsive styling to components
        self._apply_responsive_styling()

    def _apply_responsive_styling(self):
        """Apply responsive styling to UI components."""
        # Style details text area with monospace font for better readability
        if hasattr(self, "details_text"):
            self.details_text.setStyleSheet(
                f"""
                QTextEdit {{
                    background-color: {Colors.WINDOW_BACKGROUND};
                    border: 1px solid {Colors.TEXT_DISABLED};
                    border-radius: 4px;
                    padding: 8px;
                    font-family: {Fonts.MONOSPACE_FAMILY};
                    font-size: {Fonts.SMALL_SIZE}px;
                    color: {Colors.TEXT_PRIMARY};
                }}
                QTextEdit:focus {{
                    border: 2px solid {Colors.ACCENT};
                }}
            """
            )

        # Style list view with consistent appearance
        if hasattr(self, "output_list_view"):
            self.output_list_view.setStyleSheet(
                f"""
                QListView {{
                    background-color: {Colors.WINDOW_BACKGROUND};
                    border: 1px solid {Colors.TEXT_DISABLED};
                    border-radius: 4px;
                    padding: 4px;
                    color: {Colors.TEXT_PRIMARY};
                    selection-background-color: {Colors.ACCENT};
                    selection-color: white;
                }}
                QListView::item {{
                    padding: 4px;
                    border-bottom: 1px solid {Colors.DIALOG_BACKGROUND};
                }}
                QListView::item:selected {{
                    background-color: {Colors.ACCENT};
                    color: white;
                }}
                QListView::item:hover {{
                    background-color: {Colors.DIALOG_BACKGROUND};
                }}
            """
            )

        # Setup responsive splitter behavior
        if hasattr(self, "resultsSplitter"):
            self.resultsSplitter.setStretchFactor(0, 1)
            self.resultsSplitter.setStretchFactor(1, 2)
            self.resultsSplitter.setSizes([300, 500])

    def _on_theme_changed(self, theme_name):
        """Handle theme change notifications."""
        # Reapply styling when theme changes
        self._apply_responsive_styling()

        # Update window styling
        ThemeManager.apply_utility_window_theme(self)

    def _create_ui_programmatically(self):
        """Create UI programmatically if .ui file is not available."""
        # Header
        header = self.create_header("Size Analyzer")
        self.main_layout.addWidget(header)

        # Directory selection section
        dir_group = self.create_group_box("Directory Selection")
        dir_layout = QHBoxLayout()

        self.directory_line_edit = QLineEdit()
        self.directory_line_edit.setPlaceholderText("No directory selected")
        self.directory_line_edit.setReadOnly(True)
        ThemeManager.style_input_field(self.directory_line_edit)

        self.browse_button = self.create_button("Browse", self._browse_directory)

        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.directory_line_edit)
        dir_layout.addWidget(self.browse_button)
        dir_group.setLayout(dir_layout)
        self.main_layout.addWidget(dir_group)

        # Progress section
        progress_group = self.create_group_box("Analysis Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = self.create_progress_bar()
        self.progress_label = QLabel("Ready")
        ThemeManager.style_label(self.progress_label)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)

        # Results section
        results_group = self.create_group_box("Analysis Results")
        results_layout = QVBoxLayout()

        # Create splitter for results
        splitter = QSplitter(Qt.Horizontal)

        # Summary view
        self.output_list_view = QListView()
        self.output_list_view.setMinimumHeight(200)

        # Detailed view
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumHeight(200)

        splitter.addWidget(self.output_list_view)
        splitter.addWidget(self.details_text)
        splitter.setSizes([300, 400])

        results_layout.addWidget(splitter)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.analyze_button = self.create_button(
            "Analyze Directory Size", self._start_analysis
        )
        self.export_button = self.create_button(
            "Export Results", self._export_results, primary=False
        )
        self.cancel_button = self.create_button(
            "Cancel", self._cancel_analysis, primary=False
        )

        # Initially disable export and cancel buttons
        self.export_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        self.main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect signals to their handlers."""
        # Connect UI component signals
        self.browse_button.clicked.connect(self._browse_directory)
        self.analyze_button.clicked.connect(self._start_analysis)

        if hasattr(self, "export_button"):
            self.export_button.clicked.connect(self._export_results)

        if hasattr(self, "cancel_button"):
            self.cancel_button.clicked.connect(self._cancel_analysis)

        # Connect menu actions if they exist
        if hasattr(self, "actionselect"):
            self.actionselect.triggered.connect(self._browse_directory)

        if hasattr(self, "actionexport_results"):
            self.actionexport_results.triggered.connect(self._export_results)

        if hasattr(self, "actionexit"):
            self.actionexit.triggered.connect(self.close)

        if hasattr(self, "actionabout"):
            self.actionabout.triggered.connect(self._show_about)

        # Connect analyzer signals
        self.analyzer.progress_percentage.connect(self._update_progress)
        self.analyzer.progress_message.connect(self._update_status)
        self.analyzer.milestone_reached.connect(self._milestone_reached)
        self.analyzer.analysis_complete.connect(self._analysis_complete)
        self.analyzer.error_occurred.connect(self._handle_error)
        self.analyzer.operation_cancelled.connect(self._operation_cancelled)

        # Connect hub integration signals
        self.tool_progress.connect(self._on_tool_progress)
        self.tool_error.connect(self._on_tool_error)
        self.tool_completed.connect(self._on_tool_completed)
        self.hub_connection_changed.connect(self._on_hub_connection_changed)

    def _on_tool_progress(self, tool_name: str, percentage: int, message: str):
        """Handle tool progress updates for hub integration."""
        self.hub_connector.report_progress_to_hub(percentage, message)

    def _on_tool_error(self, tool_name: str, error_message: str):
        """Handle tool error reports for hub integration."""
        self.hub_connector.report_error_to_hub(error_message)

    def _on_tool_completed(self, tool_name: str, results: Dict[str, Any]):
        """Handle tool completion for hub integration."""
        self.hub_connector.report_status_to_hub("completed", results)

    def _on_hub_connection_changed(self, connected: bool):
        """Handle hub connection status changes."""
        status = "Connected to Hub" if connected else "Disconnected from Hub"
        self.show_status_message(status)

    def _show_about(self):
        """Show about dialog."""
        self.show_info_dialog(
            "About Size Analyzer",
            "Size Analyzer v2.0\n\n"
            "Part of Richard's File Utilities 2\n"
            "Analyze directory sizes and file distributions\n\n"
            "Features:\n"
            "• Comprehensive directory analysis\n"
            "• File type breakdown\n"
            "• Largest files identification\n"
            "• Export results to JSON\n"
            "• Hub integration for resource management",
        )

    @pyqtSlot()
    def _browse_directory(self):
        """Handle directory browsing."""
        directory = self.get_directory_path("Select Directory to Analyze")

        if directory:
            self.selected_directory = directory
            self.directory_line_edit.setText(directory)
            self.analyze_button.setEnabled(True)
            self.show_status_message(f"Selected: {directory}")

    @pyqtSlot()
    def _start_analysis(self):
        """Start the directory analysis."""
        if not self.selected_directory:
            # If the user jumps straight to Analyze, prompt for a directory
            self._browse_directory()

        if not self.selected_directory:
            self.show_status_message("Analysis cancelled: no directory selected")
            return

        if not os.path.exists(self.selected_directory):
            self.show_error_dialog(
                "Directory Not Found", "The selected directory no longer exists."
            )
            return

        # Request resources from hub
        resource_granted = self.request_hub_resources(
            "cpu", {"operation": "directory_analysis", "priority": "normal"}
        )

        if not resource_granted:
            self.show_warning_dialog(
                "Resource Unavailable",
                "System resources are currently busy. " "Please try again later.",
            )
            return

        # Report analysis start to hub
        self.report_status_to_hub(
            "analyzing",
            {
                "directory": self.selected_directory,
                "start_time": self.hub_connector.tool_state[
                    "last_activity"
                ].isoformat(),
            },
        )
        self.tool_started.emit("Size Analyzer")

        # Disable UI during analysis
        self._set_analysis_state(True)

        # Create and start worker thread
        self.worker_thread = SizeAnalyzerWorker(
            self.analyzer, self.selected_directory, top_files_count=20
        )

        # Connect worker signals
        self.worker_thread.analysis_finished.connect(self._analysis_complete)
        self.worker_thread.analysis_error.connect(self._handle_error)
        self.worker_thread.progress_update.connect(self._update_progress)
        self.worker_thread.status_update.connect(self._update_status)

        # Start analysis
        self.worker_thread.start()
        self.show_status_message("Starting directory analysis...")

        # Broadcast analysis start event
        self.broadcast_hub_event(
            "analysis_started",
            {"tool": "Size Analyzer", "directory": self.selected_directory},
        )

    @pyqtSlot()
    def _cancel_analysis(self):
        """Cancel the current analysis."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.show_status_message("Cancelling analysis...")

    @pyqtSlot()
    def _export_results(self):
        """Export analysis results to a file."""
        if not self.current_analysis:
            self.show_warning_dialog("No Results", "No analysis results to export.")
            return

        file_path = self.get_save_file_path(
            "Export Analysis Results", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                self.analyzer.export_analysis(self.current_analysis, file_path)
                self.show_info_dialog(
                    "Export Successful", f"Results exported to:\n{file_path}"
                )
            except Exception as e:
                self.show_error_dialog(
                    "Export Failed", f"Failed to export results:\n{str(e)}"
                )

    def _set_analysis_state(self, analyzing: bool):
        """Set UI state while keeping progress feedback clear."""
        # Update button states
        self.analyze_button.setEnabled(not analyzing)
        self.browse_button.setEnabled(not analyzing)

        if hasattr(self, "cancel_button"):
            self.cancel_button.setEnabled(analyzing)

        if hasattr(self, "export_button"):
            self.export_button.setEnabled(
                not analyzing and self.current_analysis is not None
            )

        # Update progress visualization
        if hasattr(self, "progress_bar"):
            self.progress_bar.setVisible(analyzing)
            if analyzing:
                self.progress_bar.setValue(0)
                self.progress_bar.setFormat("Starting analysis...")
            else:
                self.progress_bar.setFormat("Ready")

        # Update progress group visibility
        if hasattr(self, "progress_group"):
            self.progress_group.setVisible(
                analyzing or self.current_analysis is not None
            )

        # Update status message
        if analyzing:
            self.show_status_message("Analysis in progress...")
        else:
            if self.current_analysis:
                self.show_status_message("Analysis completed")
            else:
                self.show_status_message("Ready")

    @pyqtSlot(int)
    def _update_progress(self, percentage: int):
        """Update progress bar and report to hub."""
        self.progress_bar.setValue(percentage)
        # Report progress to hub
        self.tool_progress.emit(
            "Size Analyzer", percentage, f"Analysis {percentage}% complete"
        )

    @pyqtSlot(str)
    def _update_status(self, message: str):
        """Update status message and report to hub."""
        if hasattr(self, "progress_label"):
            self.progress_label.setText(message)
        self.show_status_message(message)
        # Report status to hub
        self.report_status_to_hub("running", {"current_operation": message})

    @pyqtSlot(str, int)
    def _milestone_reached(self, milestone: str, percentage: int):
        """Handle milestone notifications and report to hub."""
        self.show_status_message(f"{milestone} ({percentage}%)")
        # Report milestone to hub
        self.broadcast_hub_event(
            "milestone_reached",
            {"tool": "Size Analyzer", "milestone": milestone, "percentage": percentage},
        )

    @pyqtSlot(dict)
    def _analysis_complete(self, analysis: Dict[str, Any]):
        """Handle completed analysis and report to hub."""
        self.current_analysis = analysis
        self._set_analysis_state(False)
        self.export_button.setEnabled(True)

        # Display results
        self._display_results(analysis)

        # Show completion message
        total_size = self.analyzer.format_size(analysis.get("total_size", 0))
        file_count = analysis.get("file_count", 0)

        completion_message = f"Analysis complete: {file_count} files, {total_size}"
        self.show_status_message(completion_message)

        # Report completion to hub
        completion_data = {
            "total_size": analysis.get("total_size", 0),
            "file_count": file_count,
            "directory_count": analysis.get("directory_count", 0),
            "completion_time": self.hub_connector.tool_state[
                "last_activity"
            ].isoformat(),
        }
        self.tool_completed.emit("Size Analyzer", completion_data)
        self.report_status_to_hub("completed", completion_data)

        # Broadcast completion event
        self.broadcast_hub_event(
            "analysis_completed",
            {
                "tool": "Size Analyzer",
                "directory": analysis.get("path", ""),
                "results": completion_data,
            },
        )

        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    @pyqtSlot(str)
    def _handle_error(self, error_message: str):
        """Handle analysis errors and report to hub."""
        self._set_analysis_state(False)
        self.show_error_dialog("Analysis Error", error_message)

        # Report error to hub
        self.tool_error.emit("Size Analyzer", error_message)
        self.report_status_to_hub("error", {"error_message": error_message})

        # Broadcast error event
        self.broadcast_hub_event(
            "analysis_error", {"tool": "Size Analyzer", "error": error_message}
        )

        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    @pyqtSlot()
    def _operation_cancelled(self):
        """Handle operation cancellation and report to hub."""
        self._set_analysis_state(False)
        self.show_status_message("Analysis cancelled")

        # Report cancellation to hub
        self.report_status_to_hub("cancelled", {"reason": "user_requested"})

        # Broadcast cancellation event
        self.broadcast_hub_event(
            "analysis_cancelled", {"tool": "Size Analyzer", "reason": "user_requested"}
        )

        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    def _display_results(self, analysis: Dict[str, Any]):
        """Display analysis results in the UI."""
        # Create summary model
        model = QStandardItemModel()

        # Add summary items
        summary_items = [
            f"Directory: {analysis.get('path', 'Unknown')}",
            f"Total Files: {analysis.get('file_count', 0):,}",
            f"Total Directories: {analysis.get('directory_count', 0):,}",
            f"Total Size: "
            f"{self.analyzer.format_size(analysis.get('total_size', 0))}",
        ]

        for item_text in summary_items:
            item = QStandardItem(item_text)
            item.setEditable(False)
            model.appendRow(item)

        # Add file type summary
        file_types = analysis.get("file_types", {})
        if file_types:
            model.appendRow(QStandardItem(""))  # Separator
            type_header = QStandardItem("File Types:")
            type_header.setFont(
                QFont(Fonts.DEFAULT_FAMILY, Fonts.BODY_SIZE, QFont.Bold)
            )
            model.appendRow(type_header)

            for ext, stats in sorted(file_types.items()):
                count = stats.get("count", 0)
                size = self.analyzer.format_size(stats.get("total_size", 0))
                type_item = QStandardItem(f"  {ext}: {count} files, {size}")
                model.appendRow(type_item)

        self.output_list_view.setModel(model)

        # Display detailed information
        if hasattr(self, "details_text"):
            self._display_detailed_results(analysis)

    def _display_detailed_results(self, analysis: Dict[str, Any]):
        """Display detailed results in the text area."""
        details = []

        # Largest files
        largest_files = analysis.get("largest_files", [])
        if largest_files:
            details.append("LARGEST FILES:")
            details.append("=" * 50)

            for i, file_info in enumerate(largest_files[:10], 1):
                size = self.analyzer.format_size(file_info.get("size", 0))
                name = file_info.get("name", "Unknown")
                details.append(f"{i:2d}. {name} ({size})")

            details.append("")

        # File type details
        file_types = analysis.get("file_types", {})
        if file_types:
            details.append("FILE TYPE ANALYSIS:")
            details.append("=" * 50)

            for ext, stats in sorted(
                file_types.items(),
                key=lambda x: x[1].get("total_size", 0),
                reverse=True,
            ):
                count = stats.get("count", 0)
                total_size = self.analyzer.format_size(stats.get("total_size", 0))
                avg_size = self.analyzer.format_size(stats.get("average_size", 0))

                details.append(f"{ext}:")
                details.append(f"  Files: {count:,}")
                details.append(f"  Total Size: {total_size}")
                details.append(f"  Average Size: {avg_size}")
                details.append("")

        self.details_text.setPlainText("\n".join(details))

    def closeEvent(self, event):
        """Handle window close event with hub cleanup."""
        # Cancel any running analysis
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait()

        # Report tool shutdown to hub
        self.report_status_to_hub(
            "shutting_down",
            {
                "shutdown_time": self.hub_connector.tool_state[
                    "last_activity"
                ].isoformat()
            },
        )

        # Broadcast shutdown event
        self.broadcast_hub_event(
            "tool_shutdown", {"tool": "Size Analyzer", "reason": "user_closed"}
        )

        # Cleanup hub integration
        self.hub_connector.cleanup()

        super().closeEvent(event)


def main():
    """Main entry point for the Size Analyzer GUI."""
    app = QApplication(sys.argv)

    try:
        window = SizeAnalyzerGUI()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(
            None, "Fatal Error", f"Failed to start Size Analyzer:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
