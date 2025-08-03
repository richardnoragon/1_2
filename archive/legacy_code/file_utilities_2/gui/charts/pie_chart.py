"""
Pie chart component for directory size distribution visualization.

Displays directory sizes as interactive pie chart with hover tooltips
and click-to-drill-down functionality.
"""

from typing import Dict, Any, List, Optional
import math
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor

try:
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .chart_base import ChartBase
from file_utilities_2.gui.themes import Colors


class SizeDistributionPieChart(ChartBase):
    """
    Pie chart for visualizing directory size distribution.
    
    Features:
    - Interactive pie slices with hover effects
    - Click-to-drill-down functionality
    - Customizable color schemes
    - Percentage and size labels
    - Legend with size information
    """
    
    # Additional signals specific to pie chart
    slice_clicked = pyqtSignal(str, int)  # directory name, size
    slice_hovered = pyqtSignal(str, int)  # directory name, size
    
    def __init__(self, parent=None):
        """Initialize the pie chart component."""
        super().__init__("Directory Size Distribution", parent)
        
        # Pie chart specific configuration
        self.pie_config = {
            'min_slice_percentage': 2.0,  # Minimum slice size to show
            'max_slices': 10,  # Maximum number of slices
            'explode_largest': True,  # Explode the largest slice
            'show_percentages': True,  # Show percentage labels
            'show_legend': True,  # Show legend
            'autopct_format': '%1.1f%%',  # Percentage format
            'startangle': 90,  # Starting angle for first slice
            'colors': None  # Will use default color scheme
        }
        
        # Data for hover tooltips
        self.slice_data: List[Dict[str, Any]] = []
        self.wedges = []  # Store wedge objects for interaction
        
        # Setup custom colors
        self._setup_color_scheme()
    
    def _setup_color_scheme(self):
        """Setup color scheme for pie chart slices."""
        # Create a visually appealing color palette
        base_colors = [
            '#3498DB',  # Blue
            '#E74C3C',  # Red
            '#2ECC71',  # Green
            '#F39C12',  # Orange
            '#9B59B6',  # Purple
            '#1ABC9C',  # Turquoise
            '#E67E22',  # Carrot
            '#34495E',  # Wet Asphalt
            '#F1C40F',  # Yellow
            '#95A5A6',  # Concrete
        ]
        
        # Extend colors if needed
        extended_colors = []
        for i in range(20):  # Support up to 20 slices
            base_idx = i % len(base_colors)
            color = base_colors[base_idx]
            
            # Vary brightness for additional colors
            if i >= len(base_colors):
                # Make colors slightly darker for variety
                color = self._adjust_color_brightness(color, 0.8)
            
            extended_colors.append(color)
        
        self.pie_config['colors'] = extended_colors
    
    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust color brightness by a factor."""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust brightness
        adjusted_rgb = tuple(int(c * factor) for c in rgb)
        
        # Convert back to hex
        return f"#{adjusted_rgb[0]:02x}{adjusted_rgb[1]:02x}{adjusted_rgb[2]:02x}"
    
    def set_data(self, data: Dict[str, Any]):
        """Set directory size data for the pie chart."""
        if not data or 'file_types' not in data:
            return
        
        # Process file type data for pie chart
        file_types = data.get('file_types', {})
        total_size = data.get('total_size', 0)
        
        if not file_types or total_size == 0:
            return
        
        # Prepare slice data
        self.slice_data = []
        
        # Sort by size (descending)
        sorted_types = sorted(
            file_types.items(),
            key=lambda x: x[1].get('total_size', 0),
            reverse=True
        )
        
        # Group small slices into "Others"
        others_size = 0
        others_count = 0
        
        for ext, stats in sorted_types:
            size = stats.get('total_size', 0)
            percentage = (size / total_size) * 100
            
            if (percentage >= self.pie_config['min_slice_percentage'] and 
                len(self.slice_data) < self.pie_config['max_slices'] - 1):
                
                self.slice_data.append({
                    'label': ext if ext else 'No Extension',
                    'size': size,
                    'percentage': percentage,
                    'count': stats.get('count', 0),
                    'color': self.pie_config['colors'][len(self.slice_data)]
                })
            else:
                others_size += size
                others_count += stats.get('count', 0)
        
        # Add "Others" slice if there are small slices
        if others_size > 0:
            others_percentage = (others_size / total_size) * 100
            self.slice_data.append({
                'label': 'Others',
                'size': others_size,
                'percentage': others_percentage,
                'count': others_count,
                'color': self.pie_config['colors'][len(self.slice_data)]
            })
        
        # Store total size for formatting
        self.total_size = total_size
        
        # Update the chart
        super().set_data(data)
    
    def update_chart(self):
        """Update the pie chart with current data."""
        if not self.slice_data or not self.axes:
            return
        
        # Clear previous chart
        self.axes.clear()
        
        # Prepare data for matplotlib
        sizes = [item['size'] for item in self.slice_data]
        labels = [item['label'] for item in self.slice_data]
        colors = [item['color'] for item in self.slice_data]
        
        # Setup explode (emphasize largest slice)
        explode = None
        if self.pie_config['explode_largest'] and len(sizes) > 1:
            explode = [0.1 if i == 0 else 0 for i in range(len(sizes))]
        
        # Create pie chart
        wedges, texts, autotexts = self.axes.pie(
            sizes,
            labels=labels if not self.pie_config['show_legend'] else None,
            colors=colors,
            autopct=self.pie_config['autopct_format'] if self.pie_config['show_percentages'] else None,
            startangle=self.pie_config['startangle'],
            explode=explode,
            shadow=True,
            textprops={
                'fontsize': self.chart_config['font_size'] - 1,
                'color': self.chart_config['text_color']
            }
        )
        
        # Store wedges for interaction
        self.wedges = wedges
        
        # Setup legend if requested
        if self.pie_config['show_legend']:
            legend_labels = []
            for item in self.slice_data:
                size_str = self._format_size(item['size'])
                legend_labels.append(f"{item['label']} ({size_str})")
            
            self.axes.legend(
                wedges,
                legend_labels,
                title="File Types",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=self.chart_config['font_size'] - 2
            )
        
        # Set title
        self.axes.set_title(
            f"Directory Size Distribution\nTotal: {self._format_size(self.total_size)}",
            fontsize=self.chart_config['font_size'] + 1,
            color=self.chart_config['text_color'],
            pad=20
        )
        
        # Ensure equal aspect ratio for circular pie
        self.axes.axis('equal')
        
        # Setup interactive features
        self._setup_interactivity()
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
        
        # Emit update signal
        self.chart_updated.emit()
    
    def _setup_interactivity(self):
        """Setup interactive features for pie chart."""
        if not MATPLOTLIB_AVAILABLE or not self.wedges:
            return
        
        # Connect hover events to wedges
        for i, wedge in enumerate(self.wedges):
            wedge.set_picker(True)
            wedge.set_pickradius(5)
    
    def _on_chart_click(self, event):
        """Handle pie chart click events."""
        if not event.inaxes or not self.wedges:
            return
        
        # Find which wedge was clicked
        for i, wedge in enumerate(self.wedges):
            if wedge.contains(event)[0]:
                slice_info = self.slice_data[i]
                
                # Emit slice clicked signal
                self.slice_clicked.emit(slice_info['label'], slice_info['size'])
                
                # Emit general chart clicked signal
                click_data = {
                    'slice_index': i,
                    'label': slice_info['label'],
                    'size': slice_info['size'],
                    'percentage': slice_info['percentage'],
                    'count': slice_info['count']
                }
                self.chart_clicked.emit(click_data)
                break
    
    def _on_chart_hover(self, event):
        """Handle pie chart hover events for tooltips."""
        if not event.inaxes or not self.wedges:
            return
        
        # Check if hovering over a wedge
        for i, wedge in enumerate(self.wedges):
            if wedge.contains(event)[0]:
                slice_info = self.slice_data[i]
                
                # Create tooltip text
                tooltip_text = (
                    f"{slice_info['label']}\n"
                    f"Size: {self._format_size(slice_info['size'])}\n"
                    f"Files: {slice_info['count']:,}\n"
                    f"Percentage: {slice_info['percentage']:.1f}%"
                )
                
                # Show tooltip
                QToolTip.showText(
                    QCursor.pos(),
                    tooltip_text
                )
                
                # Emit hover signal
                self.slice_hovered.emit(slice_info['label'], slice_info['size'])
                return
        
        # Hide tooltip if not over any wedge
        QToolTip.hideText()
    
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
    
    def get_slice_data(self) -> List[Dict[str, Any]]:
        """Get current slice data."""
        return self.slice_data.copy()
    
    def highlight_slice(self, slice_index: int, highlight: bool = True):
        """Highlight or unhighlight a specific slice."""
        if (not self.wedges or slice_index < 0 or 
            slice_index >= len(self.wedges)):
            return
        
        wedge = self.wedges[slice_index]
        
        if highlight:
            # Increase alpha and add border
            wedge.set_alpha(0.8)
            wedge.set_edgecolor('white')
            wedge.set_linewidth(2)
        else:
            # Reset to normal appearance
            wedge.set_alpha(1.0)
            wedge.set_edgecolor('none')
            wedge.set_linewidth(0)
        
        if self.canvas:
            self.canvas.draw()
    
    def update_pie_config(self, config: Dict[str, Any]):
        """Update pie chart specific configuration."""
        self.pie_config.update(config)
        self.update_chart()