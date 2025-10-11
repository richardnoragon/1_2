"""
Base chart component for Size Analyzer visualizations.

Provides common functionality and styling for all chart types.
"""

import sys
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FigureCanvas = QWidget
    NavigationToolbar = QWidget
    Figure = object

from file_utilities_2.gui.themes import ThemeManager, Colors, Fonts


class ChartBase(QWidget):
    """
    Base class for all chart components with matplotlib integration.
    
    Provides common functionality including:
    - Matplotlib canvas setup
    - Theme integration
    - Interactive features
    - Export capabilities
    - Error handling
    """
    
    # Signals for chart interactions
    chart_clicked = pyqtSignal(dict)  # Chart element clicked
    chart_updated = pyqtSignal()      # Chart data updated
    export_requested = pyqtSignal(str)  # Export format requested
    
    def __init__(self, title: str = "Chart", parent=None):
        """Initialize the base chart component."""
        super().__init__(parent)
        self.title = title
        self.chart_data: Optional[Dict[str, Any]] = None
        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvas] = None
        self.toolbar: Optional[NavigationToolbar] = None
        self.axes = None
        
        # Chart configuration
        self.chart_config = {
            'background_color': Colors.WINDOW_BACKGROUND,
            'text_color': Colors.TEXT_PRIMARY,
            'accent_color': Colors.ACCENT,
            'font_family': Fonts.DEFAULT_FAMILY,
            'font_size': Fonts.BODY_SIZE,
            'dpi': 100,
            'interactive': True,
            'show_toolbar': True
        }
        
        self._setup_ui()
        self._setup_matplotlib()
        self._apply_theme()
    
    def _setup_ui(self):
        """Setup the basic UI structure."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)
        
        # Header section
        self.header_layout = QHBoxLayout()
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont(Fonts.DEFAULT_FAMILY, Fonts.HEADER_SIZE, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.setMaximumWidth(80)
        ThemeManager.style_secondary_button(self.export_button)
        self.export_button.clicked.connect(self._show_export_menu)
        self.header_layout.addWidget(self.export_button)
        
        self.main_layout.addLayout(self.header_layout)
        
        # Chart container
        self.chart_container = QFrame()
        self.chart_container.setFrameStyle(QFrame.StyledPanel)
        self.chart_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
            }}
        """)
        
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(5, 5, 5, 5)
        
        self.main_layout.addWidget(self.chart_container)
    
    def _setup_matplotlib(self):
        """Setup matplotlib components if available."""
        if not MATPLOTLIB_AVAILABLE:
            self._show_matplotlib_error()
            return
        
        try:
            # Create figure with theme-appropriate settings
            self.figure = Figure(
                figsize=(8, 6),
                dpi=self.chart_config['dpi'],
                facecolor=self.chart_config['background_color'],
                edgecolor='none'
            )
            
            # Create canvas
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setParent(self.chart_container)
            
            # Setup interactive features
            if self.chart_config['interactive']:
                self.canvas.mpl_connect('button_press_event', self._on_chart_click)
                self.canvas.mpl_connect('motion_notify_event', self._on_chart_hover)
            
            # Create navigation toolbar if requested
            if self.chart_config['show_toolbar']:
                self.toolbar = NavigationToolbar(self.canvas, self.chart_container)
                self.toolbar.setStyleSheet(f"""
                    QToolBar {{
                        background-color: {Colors.DIALOG_BACKGROUND};
                        border: none;
                        spacing: 2px;
                    }}
                    QToolButton {{
                        background-color: transparent;
                        border: 1px solid transparent;
                        border-radius: 3px;
                        padding: 2px;
                    }}
                    QToolButton:hover {{
                        background-color: {Colors.ACCENT};
                        border-color: {Colors.ACCENT};
                    }}
                """)
                self.chart_layout.addWidget(self.toolbar)
            
            self.chart_layout.addWidget(self.canvas)
            
            # Create initial axes
            self.axes = self.figure.add_subplot(111)
            self._configure_axes()
            
        except Exception as e:
            self._show_matplotlib_error(str(e))
    
    def _show_matplotlib_error(self, error_msg: str = None):
        """Show error message when matplotlib is not available."""
        error_label = QLabel(
            f"Matplotlib not available: {error_msg}" if error_msg 
            else "Matplotlib is required for chart visualization.\n"
                 "Please install matplotlib: pip install matplotlib"
        )
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.ERROR};
                font-size: {Fonts.BODY_SIZE}px;
                padding: 20px;
                background-color: {Colors.DIALOG_BACKGROUND};
                border: 1px solid {Colors.ERROR};
                border-radius: 4px;
            }}
        """)
        self.chart_layout.addWidget(error_label)
    
    def _configure_axes(self):
        """Configure axes with theme-appropriate styling."""
        if not self.axes:
            return
        
        # Set background colors
        self.axes.set_facecolor(self.chart_config['background_color'])
        
        # Configure text colors
        self.axes.tick_params(
            colors=self.chart_config['text_color'],
            labelsize=self.chart_config['font_size'] - 1
        )
        
        # Configure spines
        for spine in self.axes.spines.values():
            spine.set_color(Colors.TEXT_DISABLED)
            spine.set_linewidth(0.5)
        
        # Configure grid
        self.axes.grid(True, alpha=0.3, color=Colors.TEXT_DISABLED)
    
    def _apply_theme(self):
        """Apply current theme to chart components."""
        if self.figure:
            self.figure.patch.set_facecolor(self.chart_config['background_color'])
        
        # Update title color
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        
        # Update container styling
        self.chart_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WINDOW_BACKGROUND};
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
            }}
        """)
    
    def _on_chart_click(self, event):
        """Handle chart click events."""
        if event.inaxes != self.axes:
            return
        
        # Emit signal with click information
        click_data = {
            'x': event.xdata,
            'y': event.ydata,
            'button': event.button,
            'axes': event.inaxes
        }
        self.chart_clicked.emit(click_data)
    
    def _on_chart_hover(self, event):
        """Handle chart hover events for tooltips."""
        # Override in subclasses for specific hover behavior
        pass
    
    def _show_export_menu(self):
        """Show export options menu."""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # Add export format options
        formats = [
            ('PNG Image', 'png'),
            ('PDF Document', 'pdf'),
            ('SVG Vector', 'svg'),
            ('JPEG Image', 'jpg')
        ]
        
        for name, format_ext in formats:
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, fmt=format_ext: self.export_requested.emit(fmt))
        
        # Show menu at button position
        menu.exec_(self.export_button.mapToGlobal(self.export_button.rect().bottomLeft()))
    
    def set_data(self, data: Dict[str, Any]):
        """Set chart data and trigger update."""
        self.chart_data = data
        self.update_chart()
    
    def update_chart(self):
        """Update chart with current data. Override in subclasses."""
        if not self.chart_data or not self.axes:
            return
        
        # Clear previous chart
        self.axes.clear()
        self._configure_axes()
        
        # Emit update signal
        self.chart_updated.emit()
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
    
    def clear_chart(self):
        """Clear the chart."""
        if self.axes:
            self.axes.clear()
            self._configure_axes()
        
        if self.canvas:
            self.canvas.draw()
    
    def export_chart(self, file_path: str, format_type: str = 'png', dpi: int = 300):
        """Export chart to file."""
        if not self.figure:
            return False
        
        try:
            self.figure.savefig(
                file_path,
                format=format_type,
                dpi=dpi,
                bbox_inches='tight',
                facecolor=self.chart_config['background_color'],
                edgecolor='none'
            )
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def set_title(self, title: str):
        """Set chart title."""
        self.title = title
        self.title_label.setText(title)
        
        if self.axes:
            self.axes.set_title(title, 
                              color=self.chart_config['text_color'],
                              fontsize=self.chart_config['font_size'] + 1,
                              fontweight='bold')
    
    def get_chart_config(self) -> Dict[str, Any]:
        """Get current chart configuration."""
        return self.chart_config.copy()
    
    def update_chart_config(self, config: Dict[str, Any]):
        """Update chart configuration."""
        self.chart_config.update(config)
        self._apply_theme()
        self.update_chart()
    
    def is_matplotlib_available(self) -> bool:
        """Check if matplotlib is available."""
        return MATPLOTLIB_AVAILABLE