"""
Bar chart component for largest files visualization.

Displays the largest files in a horizontal bar chart with interactive features.
"""

from typing import Dict, Any, List
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


class LargestFilesBarChart(ChartBase):
    """
    Horizontal bar chart for visualizing largest files.
    
    Features:
    - Interactive bars with hover tooltips
    - Click-to-open file location
    - Customizable number of files to display
    - Size-based color coding
    - File type indicators
    """
    
    # Additional signals specific to bar chart
    file_clicked = pyqtSignal(str, int)  # file path, size
    file_hovered = pyqtSignal(str, int)  # file path, size
    
    def __init__(self, parent=None):
        """Initialize the bar chart component."""
        super().__init__("Largest Files", parent)
        
        # Bar chart specific configuration
        self.bar_config = {
            'max_files': 20,  # Maximum number of files to show
            'min_files': 5,   # Minimum number of files to show
            'bar_height': 0.8,  # Height of bars (0-1)
            'show_values': True,  # Show size values on bars
            'show_file_types': True,  # Color code by file type
            'truncate_names': True,  # Truncate long file names
            'max_name_length': 30,  # Maximum characters in file name
            'horizontal': True,  # Use horizontal bars
            'color_scheme': 'size_based'  # 'size_based' or 'type_based'
        }
        
        # Data for interaction
        self.file_data: List[Dict[str, Any]] = []
        self.bars = []  # Store bar objects for interaction
        
        # Setup color schemes
        self._setup_color_schemes()
    
    def _setup_color_schemes(self):
        """Setup color schemes for different visualization modes."""
        # Size-based color scheme (gradient from small to large)
        self.size_colors = {
            'small': '#95A5A6',    # Gray
            'medium': '#F39C12',   # Orange
            'large': '#E74C3C',    # Red
            'huge': '#8E44AD'      # Purple
        }
        
        # File type color scheme
        self.type_colors = {
            '.txt': '#3498DB',     # Blue
            '.pdf': '#E74C3C',     # Red
            '.doc': '#2980B9',     # Dark Blue
            '.docx': '#2980B9',    # Dark Blue
            '.xls': '#27AE60',     # Green
            '.xlsx': '#27AE60',    # Green
            '.jpg': '#F39C12',     # Orange
            '.jpeg': '#F39C12',    # Orange
            '.png': '#E67E22',     # Carrot
            '.gif': '#D35400',     # Pumpkin
            '.mp4': '#9B59B6',     # Purple
            '.avi': '#8E44AD',     # Violet
            '.mp3': '#1ABC9C',     # Turquoise
            '.wav': '#16A085',     # Green Sea
            '.zip': '#34495E',     # Wet Asphalt
            '.rar': '#2C3E50',     # Midnight Blue
            'default': '#95A5A6'   # Concrete
        }
    
    def set_data(self, data: Dict[str, Any]):
        """Set largest files data for the bar chart."""
        if not data or 'largest_files' not in data:
            return
        
        largest_files = data.get('largest_files', [])
        
        if not largest_files:
            return
        
        # Limit number of files to display
        max_files = min(len(largest_files), self.bar_config['max_files'])
        files_to_show = largest_files[:max_files]
        
        # Process file data
        self.file_data = []
        total_size = sum(f.get('size', 0) for f in files_to_show)
        
        for i, file_info in enumerate(files_to_show):
            file_path = file_info.get('path', file_info.get('name', 'Unknown'))
            file_name = file_info.get('name', 'Unknown')
            file_size = file_info.get('size', 0)
            file_ext = file_info.get('extension', '').lower()
            
            # Truncate file name if needed
            display_name = file_name
            if (self.bar_config['truncate_names'] and 
                len(display_name) > self.bar_config['max_name_length']):
                display_name = (display_name[:self.bar_config['max_name_length']-3] + 
                               '...')
            
            # Determine color based on scheme
            if self.bar_config['color_scheme'] == 'size_based':
                color = self._get_size_based_color(file_size, total_size)
            else:
                color = self._get_type_based_color(file_ext)
            
            self.file_data.append({
                'name': file_name,
                'display_name': display_name,
                'path': file_path,
                'size': file_size,
                'extension': file_ext,
                'color': color,
                'rank': i + 1
            })
        
        # Update the chart
        super().set_data(data)
    
    def _get_size_based_color(self, file_size: int, total_size: int) -> str:
        """Get color based on file size relative to total."""
        if total_size == 0:
            return self.size_colors['small']
        
        percentage = (file_size / total_size) * 100
        
        if percentage >= 20:
            return self.size_colors['huge']
        elif percentage >= 10:
            return self.size_colors['large']
        elif percentage >= 5:
            return self.size_colors['medium']
        else:
            return self.size_colors['small']
    
    def _get_type_based_color(self, file_ext: str) -> str:
        """Get color based on file type."""
        return self.type_colors.get(file_ext, self.type_colors['default'])
    
    def update_chart(self):
        """Update the bar chart with current data."""
        if not self.file_data or not self.axes:
            return
        
        # Clear previous chart
        self.axes.clear()
        self._configure_axes()
        
        # Prepare data for matplotlib
        sizes = [item['size'] for item in self.file_data]
        names = [item['display_name'] for item in self.file_data]
        colors = [item['color'] for item in self.file_data]
        
        # Create positions for bars
        y_pos = np.arange(len(names))
        
        # Create horizontal bar chart
        if self.bar_config['horizontal']:
            bars = self.axes.barh(
                y_pos,
                sizes,
                height=self.bar_config['bar_height'],
                color=colors,
                alpha=0.8,
                edgecolor='white',
                linewidth=0.5
            )
            
            # Set labels
            self.axes.set_yticks(y_pos)
            self.axes.set_yticklabels(names)
            self.axes.set_xlabel('File Size')
            
            # Invert y-axis to show largest at top
            self.axes.invert_yaxis()
            
            # Add value labels on bars if requested
            if self.bar_config['show_values']:
                for i, (bar, size) in enumerate(zip(bars, sizes)):
                    width = bar.get_width()
                    self.axes.text(
                        width + max(sizes) * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        self._format_size(size),
                        ha='left',
                        va='center',
                        fontsize=self.chart_config['font_size'] - 2,
                        color=self.chart_config['text_color']
                    )
        else:
            # Vertical bar chart
            bars = self.axes.bar(
                y_pos,
                sizes,
                width=self.bar_config['bar_height'],
                color=colors,
                alpha=0.8,
                edgecolor='white',
                linewidth=0.5
            )
            
            # Set labels
            self.axes.set_xticks(y_pos)
            self.axes.set_xticklabels(names, rotation=45, ha='right')
            self.axes.set_ylabel('File Size')
            
            # Add value labels on bars if requested
            if self.bar_config['show_values']:
                for i, (bar, size) in enumerate(zip(bars, sizes)):
                    height = bar.get_height()
                    self.axes.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + max(sizes) * 0.01,
                        self._format_size(size),
                        ha='center',
                        va='bottom',
                        fontsize=self.chart_config['font_size'] - 2,
                        color=self.chart_config['text_color'],
                        rotation=90
                    )
        
        # Store bars for interaction
        self.bars = bars
        
        # Set title
        file_count = len(self.file_data)
        total_size = sum(item['size'] for item in self.file_data)
        title = (f"Top {file_count} Largest Files\n"
                f"Combined Size: {self._format_size(total_size)}")
        
        self.axes.set_title(
            title,
            fontsize=self.chart_config['font_size'] + 1,
            color=self.chart_config['text_color'],
            pad=20
        )
        
        # Format size labels on axes
        if self.bar_config['horizontal']:
            self.axes.xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: self._format_size(int(x)))
            )
        else:
            self.axes.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: self._format_size(int(x)))
            )
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Setup interactive features
        self._setup_interactivity()
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
        
        # Emit update signal
        self.chart_updated.emit()
    
    def _setup_interactivity(self):
        """Setup interactive features for bar chart."""
        if not MATPLOTLIB_AVAILABLE or not self.bars:
            return
        
        # Connect hover events to bars
        for i, bar in enumerate(self.bars):
            bar.set_picker(True)
            bar.set_pickradius(5)
    
    def _on_chart_click(self, event):
        """Handle bar chart click events."""
        if not event.inaxes or not self.bars:
            return
        
        # Find which bar was clicked
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                file_info = self.file_data[i]
                
                # Emit file clicked signal
                self.file_clicked.emit(file_info['path'], file_info['size'])
                
                # Emit general chart clicked signal
                click_data = {
                    'file_index': i,
                    'name': file_info['name'],
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'extension': file_info['extension'],
                    'rank': file_info['rank']
                }
                self.chart_clicked.emit(click_data)
                break
    
    def _on_chart_hover(self, event):
        """Handle bar chart hover events for tooltips."""
        if not event.inaxes or not self.bars:
            return
        
        # Check if hovering over a bar
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                file_info = self.file_data[i]
                
                # Create tooltip text
                tooltip_text = (
                    f"#{file_info['rank']}: {file_info['name']}\n"
                    f"Size: {self._format_size(file_info['size'])}\n"
                    f"Type: {file_info['extension'] or 'No extension'}\n"
                    f"Path: {file_info['path']}"
                )
                
                # Show tooltip
                QToolTip.showText(
                    QCursor.pos(),
                    tooltip_text
                )
                
                # Emit hover signal
                self.file_hovered.emit(file_info['path'], file_info['size'])
                return
        
        # Hide tooltip if not over any bar
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
    
    def get_file_data(self) -> List[Dict[str, Any]]:
        """Get current file data."""
        return self.file_data.copy()
    
    def highlight_bar(self, bar_index: int, highlight: bool = True):
        """Highlight or unhighlight a specific bar."""
        if (not self.bars or bar_index < 0 or 
            bar_index >= len(self.bars)):
            return
        
        bar = self.bars[bar_index]
        
        if highlight:
            # Increase alpha and add border
            bar.set_alpha(1.0)
            bar.set_edgecolor('yellow')
            bar.set_linewidth(3)
        else:
            # Reset to normal appearance
            bar.set_alpha(0.8)
            bar.set_edgecolor('white')
            bar.set_linewidth(0.5)
        
        if self.canvas:
            self.canvas.draw()
    
    def set_color_scheme(self, scheme: str):
        """Set color scheme ('size_based' or 'type_based')."""
        if scheme in ['size_based', 'type_based']:
            self.bar_config['color_scheme'] = scheme
            # Reprocess colors for current data
            if self.file_data:
                total_size = sum(item['size'] for item in self.file_data)
                for item in self.file_data:
                    if scheme == 'size_based':
                        item['color'] = self._get_size_based_color(
                            item['size'], total_size)
                    else:
                        item['color'] = self._get_type_based_color(
                            item['extension'])
                self.update_chart()
    
    def update_bar_config(self, config: Dict[str, Any]):
        """Update bar chart specific configuration."""
        self.bar_config.update(config)
        self.update_chart()