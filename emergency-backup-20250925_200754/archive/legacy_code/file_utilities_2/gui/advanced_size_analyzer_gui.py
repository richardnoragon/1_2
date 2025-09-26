"""
Advanced Size Analyzer GUI with comprehensive visualization capabilities.

This module provides a modern, feature-rich interface with tabbed views,
interactive charts, and advanced analysis tools.
"""

import os
import sys
from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QSplitter, QGroupBox, QLabel, QPushButton, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QProgressBar, QStatusBar,
    QMenuBar, QMenu, QAction, QFileDialog, QMessageBox, QFrame,
    QScrollArea, QGridLayout, QComboBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QThread
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager, Colors, Fonts
from file_utilities_2.core.size_analyzer_logic import (
    SizeAnalyzer, SizeAnalyzerWorker
)
from file_utilities_2.integration.hub_connector import HubConnector

# Import chart components
try:
    from file_utilities_2.gui.charts import (
        SizeDistributionPieChart,
        LargestFilesBarChart,
        DirectoryTreemapChart,
        SizeTimelineChart
    )
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False


class AdvancedSizeAnalyzerGUI(StandardWindow):
    """
    Advanced GUI for Size Analyzer with comprehensive visualization.
    
    Features:
    - Tabbed interface with multiple analysis views
    - Interactive charts (pie, bar, treemap, timeline)
    - Modern file tree with size visualization
    - Real-time statistics and progress tracking
    - Drag-and-drop directory selection
    - Export capabilities for charts and data
    - Responsive design for different screen sizes
    """
    
    # Hub notification signals
    tool_started = pyqtSignal(str)
    tool_completed = pyqtSignal(str, dict)
    tool_error = pyqtSignal(str, str)
    tool_progress = pyqtSignal(str, int, str)
    tool_status_changed = pyqtSignal(str, str)
    
    # Analysis signals
    analysis_started = pyqtSignal()
    analysis_completed = pyqtSignal(dict)
    analysis_cancelled = pyqtSignal()
    
    def __init__(self, hub_instance=None):
        """Initialize the advanced Size Analyzer GUI."""
        super().__init__(
            title="Advanced Size Analyzer",
            icon_path=self._get_icon_path()
        )
        
        # Core components
        self.analyzer = SizeAnalyzer()
        self.worker_thread: Optional[SizeAnalyzerWorker] = None
        self.current_analysis: Optional[Dict[str, Any]] = None
        self.selected_directory: Optional[str] = ""
        
        # Hub integration
        self.hub_connector = HubConnector("Advanced Size Analyzer", hub_instance)
        self.hub_instance = hub_instance
        
        # UI components
        self.main_tabs: Optional[QTabWidget] = None
        self.charts_available = CHARTS_AVAILABLE
        
        # Chart components
        self.pie_chart: Optional[SizeDistributionPieChart] = None
        self.bar_chart: Optional[LargestFilesBarChart] = None
        self.treemap_chart: Optional[DirectoryTreemapChart] = None
        self.timeline_chart: Optional[SizeTimelineChart] = None
        
        # Setup UI and connections
        self._setup_advanced_ui()
        self._setup_hub_integration()
        self._connect_signals()
        
        # Initialize with hub
        self.register_with_hub(hub_instance)
        self.show_status_message("Advanced Size Analyzer ready")
    
    def _get_icon_path(self) -> str:
        """Get the icon path for the application."""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'icons', 'size_analyzer.png'),
            os.path.join(os.path.dirname(__file__), '..', 'icons', 'size_analyzer.png'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'icons', 'size_analyzer.png')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    def _setup_advanced_ui(self):
        """Setup the advanced tabbed user interface."""
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create toolbar
        self._create_toolbar(main_layout)
        
        # Create directory selection section
        self._create_directory_selection(main_layout)
        
        # Create main tabbed interface
        self._create_tabbed_interface(main_layout)
        
        # Create status section
        self._create_status_section(main_layout)
        
        # Apply theme
        ThemeManager.apply_utility_window_theme(self)
    
    def _create_toolbar(self, parent_layout: QVBoxLayout):
        """Create modern toolbar with action buttons."""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel)
        toolbar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.DIALOG_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Action buttons
        self.scan_button = QPushButton("🔍 Scan Directory")
        self.export_button = QPushButton("📊 Export Results")
        self.settings_button = QPushButton("⚙️ Settings")
        self.help_button = QPushButton("❓ Help")
        
        # Style buttons
        for button in [self.scan_button, self.export_button, 
                      self.settings_button, self.help_button]:
            ThemeManager.style_primary_button(button)
            button.setMinimumHeight(35)
            toolbar_layout.addWidget(button)
        
        toolbar_layout.addStretch()
        
        # Add other tools button
        self.other_tools_button = QPushButton("🔧 Other Tools")
        ThemeManager.style_secondary_button(self.other_tools_button)
        self.other_tools_button.setMinimumHeight(35)
        toolbar_layout.addWidget(self.other_tools_button)
        
        parent_layout.addWidget(toolbar_frame)
    
    def _create_directory_selection(self, parent_layout: QVBoxLayout):
        """Create directory selection section with drag-and-drop."""
        dir_group = QGroupBox("Directory Selection")
        ThemeManager.style_group_box(dir_group)
        dir_layout = QHBoxLayout(dir_group)
        
        # Directory path input
        self.directory_input = QLineEdit()
        self.directory_input.setPlaceholderText("Select or drag a directory here...")
        self.directory_input.setReadOnly(True)
        ThemeManager.style_input_field(self.directory_input)
        
        # Browse button
        self.browse_button = QPushButton("📁 Browse")
        ThemeManager.style_primary_button(self.browse_button)
        self.browse_button.setMinimumWidth(100)
        
        # Recent directories dropdown
        self.recent_combo = QComboBox()
        self.recent_combo.setMinimumWidth(150)
        self.recent_combo.addItem("Recent ▼")
        ThemeManager.style_input_field(self.recent_combo)
        
        dir_layout.addWidget(QLabel("Path:"))
        dir_layout.addWidget(self.directory_input, 1)
        dir_layout.addWidget(self.browse_button)
        dir_layout.addWidget(self.recent_combo)
        
        parent_layout.addWidget(dir_group)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def _create_tabbed_interface(self, parent_layout: QVBoxLayout):
        """Create the main tabbed interface."""
        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.North)
        self.main_tabs.setMovable(True)
        self.main_tabs.setTabsClosable(False)
        
        # Style tabs
        self.main_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.TEXT_DISABLED};
                background-color: {Colors.WINDOW_BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: {Colors.DIALOG_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.ACCENT};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {Colors.BUTTON_SECONDARY_HOVER};
            }}
        """)
        
        # Create tab pages
        self._create_overview_tab()
        self._create_charts_tab()
        self._create_file_list_tab()
        self._create_statistics_tab()
        self._create_export_tab()
        
        parent_layout.addWidget(self.main_tabs, 1)
    
    def _create_overview_tab(self):
        """Create overview tab with summary information."""
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Quick stats
        stats_frame = self._create_quick_stats_frame()
        splitter.addWidget(stats_frame)
        
        # Right side - Directory tree preview
        tree_frame = self._create_directory_tree_frame()
        splitter.addWidget(tree_frame)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        overview_layout.addWidget(splitter)
        
        self.main_tabs.addTab(overview_widget, "📋 Overview")
    
    def _create_charts_tab(self):
        """Create charts tab with visualization options."""
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        
        if not self.charts_available:
            # Show message about missing matplotlib
            error_label = QLabel(
                "📊 Chart visualization requires matplotlib\n\n"
                "Please install matplotlib to enable charts:\n"
                "pip install matplotlib"
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.ERROR};
                    font-size: 14px;
                    padding: 40px;
                    background-color: {Colors.DIALOG_BACKGROUND};
                    border: 2px dashed {Colors.ERROR};
                    border-radius: 8px;
                }}
            """)
            charts_layout.addWidget(error_label)
        else:
            # Create chart controls
            self._create_chart_controls(charts_layout)
            
            # Create chart container
            self._create_chart_container(charts_layout)
        
        self.main_tabs.addTab(charts_widget, "📊 Charts")
    
    def _create_chart_controls(self, parent_layout: QVBoxLayout):
        """Create chart control panel."""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_frame.setMaximumHeight(80)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Chart type selection
        controls_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "📊 Size Distribution (Pie)",
            "📈 Largest Files (Bar)",
            "🗂️ Directory Structure (Treemap)",
            "📅 Modification Timeline"
        ])
        controls_layout.addWidget(self.chart_type_combo)
        
        controls_layout.addStretch()
        
        # Chart options
        self.chart_options_button = QPushButton("⚙️ Options")
        ThemeManager.style_secondary_button(self.chart_options_button)
        controls_layout.addWidget(self.chart_options_button)
        
        # Export chart button
        self.export_chart_button = QPushButton("💾 Export Chart")
        ThemeManager.style_secondary_button(self.export_chart_button)
        controls_layout.addWidget(self.export_chart_button)
        
        parent_layout.addWidget(controls_frame)
    
    def _create_chart_container(self, parent_layout: QVBoxLayout):
        """Create container for chart widgets."""
        self.chart_container = QWidget()
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(5, 5, 5, 5)
        
        if self.charts_available:
            # Initialize chart components
            self.pie_chart = SizeDistributionPieChart()
            self.bar_chart = LargestFilesBarChart()
            self.treemap_chart = DirectoryTreemapChart()
            self.timeline_chart = SizeTimelineChart()
            
            # Add charts to layout (initially hidden)
            chart_layout.addWidget(self.pie_chart)
            chart_layout.addWidget(self.bar_chart)
            chart_layout.addWidget(self.treemap_chart)
            chart_layout.addWidget(self.timeline_chart)
            
            # Show only pie chart initially
            self.bar_chart.hide()
            self.treemap_chart.hide()
            self.timeline_chart.hide()
        
        parent_layout.addWidget(self.chart_container, 1)
    
    def _create_file_list_tab(self):
        """Create file list tab with detailed file information."""
        file_list_widget = QWidget()
        file_list_layout = QVBoxLayout(file_list_widget)
        
        # Create file tree widget
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels([
            "Name", "Size", "Type", "Modified", "Path"
        ])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSortingEnabled(True)
        
        # Style file tree
        self.file_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                selection-background-color: {Colors.ACCENT};
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {Colors.DIALOG_BACKGROUND};
            }}
            QTreeWidget::item:selected {{
                background-color: {Colors.ACCENT};
                color: white;
            }}
        """)
        
        file_list_layout.addWidget(self.file_tree)
        
        self.main_tabs.addTab(file_list_widget, "📄 File List")
    
    def _create_statistics_tab(self):
        """Create statistics tab with detailed analysis."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Create statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont(Fonts.MONOSPACE_FAMILY, Fonts.BODY_SIZE))
        
        # Style statistics text
        self.stats_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                padding: 10px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        stats_layout.addWidget(self.stats_text)
        
        self.main_tabs.addTab(stats_widget, "📈 Statistics")
    
    def _create_export_tab(self):
        """Create export tab with various export options."""
        export_widget = QWidget()
        export_layout = QVBoxLayout(export_widget)
        
        # Export options
        export_group = QGroupBox("Export Options")
        ThemeManager.style_group_box(export_group)
        export_group_layout = QGridLayout(export_group)
        
        # Export format options
        export_group_layout.addWidget(QLabel("Format:"), 0, 0)
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems([
            "JSON (Complete Data)",
            "CSV (File List)",
            "HTML (Report)",
            "PDF (Summary)"
        ])
        export_group_layout.addWidget(self.export_format_combo, 0, 1)
        
        # Export options checkboxes
        self.include_charts_check = QCheckBox("Include Charts")
        self.include_stats_check = QCheckBox("Include Statistics")
        self.include_tree_check = QCheckBox("Include Directory Tree")
        
        export_group_layout.addWidget(self.include_charts_check, 1, 0)
        export_group_layout.addWidget(self.include_stats_check, 1, 1)
        export_group_layout.addWidget(self.include_tree_check, 2, 0)
        
        # Export button
        self.export_data_button = QPushButton("💾 Export Data")
        ThemeManager.style_primary_button(self.export_data_button)
        export_group_layout.addWidget(self.export_data_button, 3, 0, 1, 2)
        
        export_layout.addWidget(export_group)
        export_layout.addStretch()
        
        self.main_tabs.addTab(export_widget, "💾 Export")
    
    def _create_quick_stats_frame(self) -> QFrame:
        """Create quick statistics frame."""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel)
        stats_layout = QVBoxLayout(stats_frame)
        
        # Title
        title_label = QLabel("📊 Quick Statistics")
        title_label.setFont(QFont(Fonts.DEFAULT_FAMILY, Fonts.HEADER_SIZE, QFont.Bold))
        stats_layout.addWidget(title_label)
        
        # Statistics labels
        self.total_size_label = QLabel("Total Size: Not analyzed")
        self.file_count_label = QLabel("Files: Not analyzed")
        self.dir_count_label = QLabel("Directories: Not analyzed")
        self.largest_file_label = QLabel("Largest File: Not analyzed")
        
        for label in [self.total_size_label, self.file_count_label, 
                     self.dir_count_label, self.largest_file_label]:
            label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; padding: 5px;")
            stats_layout.addWidget(label)
        
        stats_layout.addStretch()
        
        return stats_frame
    
    def _create_directory_tree_frame(self) -> QFrame:
        """Create directory tree preview frame."""
        tree_frame = QFrame()
        tree_frame.setFrameStyle(QFrame.StyledPanel)
        tree_layout = QVBoxLayout(tree_frame)
        
        # Title
        title_label = QLabel("🗂️ Directory Structure")
        title_label.setFont(QFont(Fonts.DEFAULT_FAMILY, Fonts.HEADER_SIZE, QFont.Bold))
        tree_layout.addWidget(title_label)
        
        # Directory tree
        self.directory_tree = QTreeWidget()
        self.directory_tree.setHeaderLabels(["Name", "Size"])
        self.directory_tree.setAlternatingRowColors(True)
        
        # Style directory tree
        self.directory_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
            }}
        """)
        
        tree_layout.addWidget(self.directory_tree)
        
        return tree_frame
    
    def _create_status_section(self, parent_layout: QVBoxLayout):
        """Create status section with progress tracking."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setMaximumHeight(80)
        status_layout = QVBoxLayout(status_frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        ThemeManager.style_progress_bar(self.progress_bar)
        status_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to analyze directories")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; padding: 5px;")
        status_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(status_frame)
    
    def _setup_hub_integration(self):
        """Setup hub integration components."""
        # Connect hub connector signals
        self.hub_connector.hub_connection_status.connect(
            self._on_hub_connection_changed
        )
        self.hub_connector.tool_status_changed.connect(
            self.tool_status_changed.emit
        )
    
    def _connect_signals(self):
        """Connect all UI signals to their handlers."""
        # Toolbar buttons
        self.scan_button.clicked.connect(self._start_analysis)
        self.export_button.clicked.connect(self._export_results)
        self.browse_button.clicked.connect(self._browse_directory)
        
        # Chart controls
        if self.charts_available:
            self.chart_type_combo.currentIndexChanged.connect(
                self._switch_chart_type
            )
        
        # Analyzer signals
        self.analyzer.progress_percentage.connect(self._update_progress)
        self.analyzer.progress_message.connect(self._update_status)
        self.analyzer.analysis_complete.connect(self._analysis_complete)
        self.analyzer.error_occurred.connect(self._handle_error)
    
    def register_with_hub(self, hub_instance):
        """Register tool with central hub."""
        try:
            success = self.hub_connector.register_with_hub(hub_instance)
            if success:
                self.hub_instance = hub_instance
                self.tool_started.emit("Advanced Size Analyzer")
                return True
            return False
        except Exception as e:
            self.show_error_dialog("Hub Registration Error", 
                                  f"Failed to register with hub: {e}")
            return False
    
    @pyqtSlot()
    def _browse_directory(self):
        """Handle directory browsing."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Analyze"
        )
        
        if directory:
            self.selected_directory = directory
            self.directory_input.setText(directory)
            self.scan_button.setEnabled(True)
            self.show_status_message(f"Selected: {directory}")
    
    @pyqtSlot()
    def _start_analysis(self):
        """Start directory analysis."""
        if not self.selected_directory:
            self.show_warning_dialog("No Directory Selected",
                                    "Please select a directory to analyze.")
            return
        
        if not os.path.exists(self.selected_directory):
            self.show_error_dialog("Directory Not Found",
                                  "The selected directory no longer exists.")
            return
        
        # Start analysis
        self._set_analysis_state(True)
        
        # Create and start worker thread
        self.worker_thread = SizeAnalyzerWorker(
            self.analyzer,
            self.selected_directory,
            top_files_count=50
        )
        
        # Connect worker signals
        self.worker_thread.analysis_finished.connect(self._analysis_complete)
        self.worker_thread.analysis_error.connect(self._handle_error)
        self.worker_thread.progress_update.connect(self._update_progress)
        self.worker_thread.status_update.connect(self._update_status)
        
        # Start analysis
        self.worker_thread.start()
        self.analysis_started.emit()
    
    def _set_analysis_state(self, analyzing: bool):
        """Set UI state during analysis."""
        self.scan_button.setEnabled(not analyzing)
        self.browse_button.setEnabled(not analyzing)
        self.progress_bar.setVisible(analyzing)
        
        if analyzing:
            self.progress_bar.setValue(0)
            self.status_label.setText("Analysis in progress...")
        else:
            self.status_label.setText("Analysis completed" if self.current_analysis 
                                    else "Ready")
    
    @pyqtSlot(int)
    def _update_progress(self, percentage: int):
        """Update progress bar."""
        self.progress_bar.setValue(percentage)
        self.tool_progress.emit("Advanced Size Analyzer", percentage,
                               f"Analysis {percentage}% complete")
    
    @pyqtSlot(str)
    def _update_status(self, message: str):
        """Update status message."""
        self.status_label.setText(message)
    
    @pyqtSlot(dict)
    def _analysis_complete(self, analysis: Dict[str, Any]):
        """Handle completed analysis."""
        self.current_analysis = analysis
        self._set_analysis_state(False)
        
        # Update all UI components with results
        self._update_quick_stats(analysis)
        self._update_directory_tree(analysis)
        self._update_file_list(analysis)
        self._update_statistics(analysis)
        self._update_charts(analysis)
        
        # Show completion message
        total_size = self._format_size(analysis.get('total_size', 0))
        file_count = analysis.get('file_count', 0)
        
        self.show_status_message(
            f"Analysis complete: {file_count:,} files, {total_size}"
        )
        
        # Enable export
        self.export_button.setEnabled(True)
        
        # Emit completion signal
        self.analysis_completed.emit(analysis)
        self.tool_completed.emit("Advanced Size Analyzer", {
            "total_size": analysis.get('total_size', 0),
            "file_count": file_count,
            "directory_count": analysis.get('directory_count', 0)
        })
    
    def _update_quick_stats(self, analysis: Dict[str, Any]):
        """Update quick statistics display."""
        total_size = self._format_size(analysis.get('total_size', 0))
        file_count = analysis.get('file_count', 0)
        dir_count = analysis.get('directory_count', 0)
        
        largest_files = analysis.get('largest_files', [])
        largest_file = "None"
        if largest_files:
            largest_info = largest_files[0]
            largest_file = f"{largest_info.get('name', 'Unknown')} ({self._format_size(largest_info.get('size', 0))})"
        
        self.total_size_label.setText(f"Total Size: {total_size}")
        self.file_count_label.setText(f"Files: {file_count:,}")
        self.dir_count_label.setText(f"Directories: {dir_count:,}")
        self.largest_file_label.setText(f"Largest File: {largest_file}")
    
    def _update_charts(self, analysis: Dict[str, Any]):
        """Update all chart components with analysis data."""
        if not self.charts_available:
            return
        
        # Update all charts with data
        if self.pie_chart:
            self.pie_chart.set_data(analysis)
        if self.bar_chart:
            self.bar_chart.set_data(analysis)
        if self.treemap_chart:
            self.treemap_chart.set_data(analysis)
        if self.timeline_chart:
            self.timeline_chart.set_data(analysis)
    
    @pyqtSlot(int)
    def _switch_chart_type(self, index: int):
        """Switch between different chart types."""
        if not self.charts_available:
            return
        
        # Hide all charts
        charts = [self.pie_chart, self.bar_chart, 
                 self.treemap_chart, self.timeline_chart]
        
        for chart in charts:
            if chart:
                chart.hide()
        
        # Show selected chart
        if index < len(charts) and charts[index]:
            charts[index].show()
    
    def _update_directory_tree(self, analysis: Dict[str, Any]):
        """Update directory tree display."""
        self.directory_tree.clear()
        
        # Add root directory
        root_item = QTreeWidgetItem(self.directory_tree)
        root_item.setText(0, os.path.basename(self.selected_directory) or self.selected_directory)
        root_item.setText(1, self._format_size(analysis.get('total_size', 0)))
        
        # Add subdirectories (simplified)
        file_types = analysis.get('file_types', {})
        for ext, stats in sorted(file_types.items(), 
                               key=lambda x: x[1].get('total_size', 0), 
                               reverse=True)[:10]:
            type_item = QTreeWidgetItem(root_item)
            type_item.setText(0, f"{ext} files")
            type_item.setText(1, self._format_size(stats.get('total_size', 0)))
        
        self.directory_tree.expandAll()
    
    def _update_file_list(self, analysis: Dict[str, Any]):
        """Update file list display."""
        self.file_tree.clear()
        
        largest_files = analysis.get('largest_files', [])
        for file_info in largest_files[:100]:  # Show top 100 files
            item = QTreeWidgetItem(self.file_tree)
            item.setText(0, file_info.get('name', 'Unknown'))
            item.setText(1, self._format_size(file_info.get('size', 0)))
            item.setText(2, file_info.get('extension', 'Unknown'))
            
            # Format modification date
            mod_time = file_info.get('modified', 0)
            if isinstance(mod_time, (int, float)):
                import datetime
                mod_date = datetime.datetime.fromtimestamp(mod_time)
                item.setText(3, mod_date.strftime('%Y-%m-%d %H:%M'))
            else:
                item.setText(3, 'Unknown')
            
            item.setText(4, file_info.get('path', 'Unknown'))
        
        # Resize columns to content
        for i in range(5):
            self.file_tree.resizeColumnToContents(i)
    
    def _update_statistics(self, analysis: Dict[str, Any]):
        """Update detailed statistics display."""
        stats_text = []
        
        # Basic statistics
        stats_text.append("=== DIRECTORY ANALYSIS SUMMARY ===")
        stats_text.append(f"Directory: {analysis.get('path', 'Unknown')}")
        stats_text.append(f"Total Size: {self._format_size(analysis.get('total_size', 0))}")
        stats_text.append(f"Total Files: {analysis.get('file_count', 0):,}")
        stats_text.append(f"Total Directories: {analysis.get('directory_count', 0):,}")
        stats_text.append("")
        
        # File type breakdown
        file_types = analysis.get('file_types', {})
        if file_types:
            stats_text.append("=== FILE TYPE BREAKDOWN ===")
            sorted_types = sorted(file_types.items(),
                                key=lambda x: x[1].get('total_size', 0),
                                reverse=True)
            
            for ext, stats in sorted_types[:20]:  # Top 20 types
                count = stats.get('count', 0)
                size = self._format_size(stats.get('total_size', 0))
                avg_size = self._format_size(stats.get('average_size', 0))
                
                stats_text.append(f"{ext or 'No Extension'}:")
                stats_text.append(f"  Files: {count:,}")
                stats_text.append(f"  Total Size: {size}")
                stats_text.append(f"  Average Size: {avg_size}")
                stats_text.append("")
        
        # Largest files
        largest_files = analysis.get('largest_files', [])
        if largest_files:
            stats_text.append("=== LARGEST FILES ===")
            for i, file_info in enumerate(largest_files[:20], 1):
                name = file_info.get('name', 'Unknown')
                size = self._format_size(file_info.get('size', 0))
                stats_text.append(f"{i:2d}. {name} ({size})")
            stats_text.append("")
        
        # Performance metrics
        perf_metrics = analysis.get('performance_metrics', {})
        if perf_metrics:
            stats_text.append("=== PERFORMANCE METRICS ===")
            
            start_time = perf_metrics.get('start_time')
            end_time = perf_metrics.get('end_time')
            if start_time and end_time:
                import datetime
                if isinstance(start_time, str):
                    start_time = datetime.datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.datetime.fromisoformat(end_time)
                
                duration = (end_time - start_time).total_seconds()
                stats_text.append(f"Analysis Duration: {duration:.2f} seconds")
            
            files_per_sec = perf_metrics.get('files_per_second', 0)
            if files_per_sec > 0:
                stats_text.append(f"Files Processed per Second: {files_per_sec:.1f}")
            
            bytes_per_sec = perf_metrics.get('bytes_per_second', 0)
            if bytes_per_sec > 0:
                stats_text.append(f"Bytes Processed per Second: {self._format_size(int(bytes_per_sec))}")
        
        self.stats_text.setPlainText('\n'.join(stats_text))
    
    @pyqtSlot(str)
    def _handle_error(self, error_message: str):
        """Handle analysis errors."""
        self._set_analysis_state(False)
        self.show_error_dialog("Analysis Error", error_message)
        self.tool_error.emit("Advanced Size Analyzer", error_message)
    
    @pyqtSlot()
    def _export_results(self):
        """Export analysis results."""
        if not self.current_analysis:
            self.show_warning_dialog("No Results",
                                    "No analysis results to export.")
            return
        
        # Get export format
        format_text = self.export_format_combo.currentText()
        
        if "JSON" in format_text:
            self._export_json()
        elif "CSV" in format_text:
            self._export_csv()
        elif "HTML" in format_text:
            self._export_html()
        elif "PDF" in format_text:
            self._export_pdf()
    
    def _export_json(self):
        """Export results as JSON."""
        file_path = QFileDialog.getSaveFileName(
            self, "Export JSON Results",
            f"size_analysis_{self._get_timestamp()}.json",
            "JSON Files (*.json);;All Files (*)"
        )[0]
        
        if file_path:
            try:
                self.analyzer.export_analysis(self.current_analysis, file_path)
                self.show_info_dialog("Export Successful",
                                     f"Results exported to:\n{file_path}")
            except Exception as e:
                self.show_error_dialog("Export Failed",
                                      f"Failed to export results:\n{str(e)}")
    
    def _export_csv(self):
        """Export file list as CSV."""
        file_path = QFileDialog.getSaveFileName(
            self, "Export CSV File List",
            f"file_list_{self._get_timestamp()}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )[0]
        
        if file_path:
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Name', 'Size', 'Size (Bytes)', 'Extension', 'Path'])
                    
                    files = self.current_analysis.get('files', [])
                    for file_info in files:
                        writer.writerow([
                            file_info.get('name', ''),
                            self._format_size(file_info.get('size', 0)),
                            file_info.get('size', 0),
                            file_info.get('extension', ''),
                            file_info.get('path', '')
                        ])
                
                self.show_info_dialog("Export Successful",
                                     f"File list exported to:\n{file_path}")
            except Exception as e:
                self.show_error_dialog("Export Failed",
                                      f"Failed to export CSV:\n{str(e)}")
    
    def _export_html(self):
        """Export results as HTML report."""
        file_path = QFileDialog.getSaveFileName(
            self, "Export HTML Report",
            f"size_report_{self._get_timestamp()}.html",
            "HTML Files (*.html);;All Files (*)"
        )[0]
        
        if file_path:
            try:
                self._generate_html_report(file_path)
                self.show_info_dialog("Export Successful",
                                     f"HTML report exported to:\n{file_path}")
            except Exception as e:
                self.show_error_dialog("Export Failed",
                                      f"Failed to export HTML:\n{str(e)}")
    
    def _export_pdf(self):
        """Export results as PDF summary."""
        self.show_info_dialog("PDF Export",
                             "PDF export functionality would require additional dependencies.\n"
                             "Please use HTML export for now.")
    
    def _generate_html_report(self, file_path: str):
        """Generate HTML report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Size Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .chart-placeholder {{
                    background-color: #f9f9f9;
                    border: 2px dashed #ccc;
                    padding: 40px;
                    text-align: center;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Directory Size Analysis Report</h1>
                <p><strong>Directory:</strong> {self.current_analysis.get('path', 'Unknown')}</p>
                <p><strong>Generated:</strong> {self._get_timestamp()}</p>
            </div>
            
            <div class="section">
                <h2>Summary Statistics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Size</td><td>{self._format_size(self.current_analysis.get('total_size', 0))}</td></tr>
                    <tr><td>Total Files</td><td>{self.current_analysis.get('file_count', 0):,}</td></tr>
                    <tr><td>Total Directories</td><td>{self.current_analysis.get('directory_count', 0):,}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Largest Files</h2>
                <table>
                    <tr><th>Rank</th><th>File Name</th><th>Size</th></tr>
        """
        
        # Add largest files
        largest_files = self.current_analysis.get('largest_files', [])
        for i, file_info in enumerate(largest_files[:20], 1):
            html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{file_info.get('name', 'Unknown')}</td>
                        <td>{self._format_size(file_info.get('size', 0))}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>File Type Distribution</h2>
                <table>
                    <tr><th>Extension</th><th>Files</th><th>Total Size</th><th>Average Size</th></tr>
        """
        
        # Add file types
        file_types = self.current_analysis.get('file_types', {})
        sorted_types = sorted(file_types.items(),
                            key=lambda x: x[1].get('total_size', 0),
                            reverse=True)
        
        for ext, stats in sorted_types[:15]:
            html_content += f"""
                    <tr>
                        <td>{ext or 'No Extension'}</td>
                        <td>{stats.get('count', 0):,}</td>
                        <td>{self._format_size(stats.get('total_size', 0))}</td>
                        <td>{self._format_size(stats.get('average_size', 0))}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        import datetime
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _on_hub_connection_changed(self, connected: bool):
        """Handle hub connection status changes."""
        status = "Connected to Hub" if connected else "Disconnected from Hub"
        self.show_status_message(status)
    
    def dragEnterEvent(self, event):
        """Handle drag enter events for directory drop."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop events for directory selection."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isdir(file_path):
                self.selected_directory = file_path
                self.directory_input.setText(file_path)
                self.scan_button.setEnabled(True)
                self.show_status_message(f"Dropped directory: {file_path}")
            else:
                self.show_warning_dialog("Invalid Drop",
                                        "Please drop a directory, not a file.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any running analysis
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        # Cleanup hub integration
        if self.hub_connector:
            self.hub_connector.cleanup()
        
        super().closeEvent(event)


def main():
    """Main entry point for the Advanced Size Analyzer GUI."""
    app = QApplication(sys.argv)
    
    try:
        window = AdvancedSizeAnalyzerGUI()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error",
                           f"Failed to start Advanced Size Analyzer:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()