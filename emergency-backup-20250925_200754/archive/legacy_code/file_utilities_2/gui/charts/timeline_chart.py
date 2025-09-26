"""
Timeline chart component for file modification date analysis.

Displays file sizes vs modification dates to show growth patterns
and identify recent activity.
"""

from typing import Dict, Any, List, Tuple
import datetime
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    from matplotlib.collections import LineCollection
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .chart_base import ChartBase


class SizeTimelineChart(ChartBase):
    """
    Timeline chart for analyzing file modification patterns.
    
    Features:
    - Scatter plot of file sizes vs modification dates
    - Trend lines showing growth patterns
    - Interactive data points with file information
    - Configurable time ranges and aggregation
    - Color coding by file type or size
    """
    
    # Additional signals specific to timeline chart
    point_clicked = pyqtSignal(str, int, str)  # file path, size, date
    point_hovered = pyqtSignal(str, int, str)  # file path, size, date
    time_range_changed = pyqtSignal(str, str)  # start_date, end_date
    
    def __init__(self, parent=None):
        """Initialize the timeline chart component."""
        super().__init__("File Modification Timeline", parent)
        
        # Timeline specific configuration
        self.timeline_config = {
            'max_points': 1000,     # Maximum points to display
            'time_range': 'auto',   # 'auto', 'year', 'month', 'week'
            'aggregation': 'none',  # 'none', 'daily', 'weekly', 'monthly'
            'show_trend': True,     # Show trend line
            'color_scheme': 'type', # 'type', 'size', 'age'
            'point_size': 'proportional',  # 'fixed', 'proportional'
            'show_grid': True,      # Show grid lines
            'date_format': 'auto',  # Date format for x-axis
            'size_scale': 'log'     # 'linear' or 'log' for y-axis
        }
        
        # Data for timeline
        self.timeline_data: List[Dict[str, Any]] = []
        self.scatter_points = None
        self.trend_line = None
        
        # Setup color schemes
        self._setup_color_schemes()
    
    def _setup_color_schemes(self):
        """Setup color schemes for timeline visualization."""
        # File type colors
        self.type_colors = {
            'documents': '#3498DB',  # Blue
            'images': '#E67E22',     # Orange
            'videos': '#9B59B6',     # Purple
            'audio': '#1ABC9C',      # Turquoise
            'archives': '#34495E',   # Dark Gray
            'code': '#27AE60',       # Green
            'executables': '#E74C3C', # Red
            'other': '#95A5A6'       # Gray
        }
        
        # Size-based colors
        self.size_colors = {
            'tiny': '#95A5A6',      # Gray
            'small': '#2ECC71',     # Green
            'medium': '#F1C40F',    # Yellow
            'large': '#F39C12',     # Orange
            'huge': '#E74C3C'       # Red
        }
        
        # Age-based colors (newer = warmer colors)
        self.age_colors = {
            'very_new': '#E74C3C',   # Red (< 1 week)
            'new': '#F39C12',        # Orange (< 1 month)
            'recent': '#F1C40F',     # Yellow (< 6 months)
            'old': '#2ECC71',        # Green (< 1 year)
            'very_old': '#95A5A6'    # Gray (> 1 year)
        }
    
    def set_data(self, data: Dict[str, Any]):
        """Set file data for timeline analysis."""
        if not data or 'files' not in data:
            return
        
        files = data.get('files', [])
        
        if not files:
            return
        
        # Process file data for timeline
        self.timeline_data = []
        current_time = datetime.datetime.now()
        
        # Filter and process files
        valid_files = []
        for file_info in files:
            if 'modified' in file_info and 'size' in file_info:
                try:
                    # Convert timestamp to datetime
                    if isinstance(file_info['modified'], (int, float)):
                        mod_date = datetime.datetime.fromtimestamp(
                            file_info['modified'])
                    else:
                        # Assume it's already a datetime or string
                        mod_date = file_info['modified']
                        if isinstance(mod_date, str):
                            mod_date = datetime.datetime.fromisoformat(
                                mod_date.replace('Z', '+00:00'))
                    
                    valid_files.append((file_info, mod_date))
                except (ValueError, TypeError, OSError):
                    continue
        
        # Sort by modification date
        valid_files.sort(key=lambda x: x[1])
        
        # Limit number of points if needed
        if len(valid_files) > self.timeline_config['max_points']:
            # Sample evenly across the dataset
            step = len(valid_files) // self.timeline_config['max_points']
            valid_files = valid_files[::step]
        
        # Process each file
        for file_info, mod_date in valid_files:
            file_path = file_info.get('path', file_info.get('name', 'Unknown'))
            file_name = file_info.get('name', 'Unknown')
            file_size = file_info.get('size', 0)
            file_ext = file_info.get('extension', '').lower()
            
            # Calculate age
            age_days = (current_time - mod_date).days
            
            # Determine colors based on scheme
            if self.timeline_config['color_scheme'] == 'type':
                color = self._get_type_color(file_ext)
            elif self.timeline_config['color_scheme'] == 'size':
                color = self._get_size_color(file_size)
            else:  # age
                color = self._get_age_color(age_days)
            
            # Determine point size
            if self.timeline_config['point_size'] == 'proportional':
                # Scale point size based on file size (log scale)
                point_size = max(10, min(100, 20 + np.log10(max(1, file_size))))
            else:
                point_size = 30  # Fixed size
            
            self.timeline_data.append({
                'name': file_name,
                'path': file_path,
                'size': file_size,
                'date': mod_date,
                'extension': file_ext,
                'age_days': age_days,
                'color': color,
                'point_size': point_size
            })
        
        # Update the chart
        super().set_data(data)
    
    def _get_type_color(self, file_ext: str) -> str:
        """Get color based on file type."""
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return self.type_colors['images']
        elif file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
            return self.type_colors['videos']
        elif file_ext in ['.mp3', '.wav', '.flac', '.aac']:
            return self.type_colors['audio']
        elif file_ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return self.type_colors['archives']
        elif file_ext in ['.py', '.js', '.html', '.css', '.cpp', '.java']:
            return self.type_colors['code']
        elif file_ext in ['.exe', '.msi', '.app', '.deb']:
            return self.type_colors['executables']
        elif file_ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return self.type_colors['documents']
        else:
            return self.type_colors['other']
    
    def _get_size_color(self, file_size: int) -> str:
        """Get color based on file size."""
        if file_size >= 1024**3:  # >= 1 GB
            return self.size_colors['huge']
        elif file_size >= 100 * 1024**2:  # >= 100 MB
            return self.size_colors['large']
        elif file_size >= 10 * 1024**2:  # >= 10 MB
            return self.size_colors['medium']
        elif file_size >= 1024**2:  # >= 1 MB
            return self.size_colors['small']
        else:
            return self.size_colors['tiny']
    
    def _get_age_color(self, age_days: int) -> str:
        """Get color based on file age."""
        if age_days <= 7:
            return self.age_colors['very_new']
        elif age_days <= 30:
            return self.age_colors['new']
        elif age_days <= 180:
            return self.age_colors['recent']
        elif age_days <= 365:
            return self.age_colors['old']
        else:
            return self.age_colors['very_old']
    
    def update_chart(self):
        """Update the timeline chart with current data."""
        if not self.timeline_data or not self.axes:
            return
        
        # Clear previous chart
        self.axes.clear()
        self._configure_axes()
        
        # Prepare data for plotting
        dates = [item['date'] for item in self.timeline_data]
        sizes = [item['size'] for item in self.timeline_data]
        colors = [item['color'] for item in self.timeline_data]
        point_sizes = [item['point_size'] for item in self.timeline_data]
        
        # Create scatter plot
        self.scatter_points = self.axes.scatter(
            dates, sizes,
            c=colors,
            s=point_sizes,
            alpha=0.7,
            edgecolors='white',
            linewidth=0.5,
            picker=True
        )
        
        # Set y-axis scale
        if self.timeline_config['size_scale'] == 'log':
            self.axes.set_yscale('log')
            self.axes.set_ylabel('File Size (bytes, log scale)')
        else:
            self.axes.set_ylabel('File Size (bytes)')
        
        # Format y-axis labels
        self.axes.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: self._format_size(int(x)))
        )
        
        # Format x-axis (dates)
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        
        # Rotate date labels for better readability
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45)
        
        # Add trend line if requested
        if self.timeline_config['show_trend'] and len(dates) > 1:
            self._add_trend_line(dates, sizes)
        
        # Configure grid
        if self.timeline_config['show_grid']:
            self.axes.grid(True, alpha=0.3)
        
        # Set labels and title
        self.axes.set_xlabel('Modification Date')
        
        file_count = len(self.timeline_data)
        date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}"
        title = f"File Modification Timeline ({file_count} files)\n{date_range}"
        
        self.axes.set_title(
            title,
            fontsize=self.chart_config['font_size'] + 1,
            color=self.chart_config['text_color'],
            pad=20
        )
        
        # Add legend for color scheme
        self._add_legend()
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Setup interactive features
        self._setup_interactivity()
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
        
        # Emit update signal
        self.chart_updated.emit()
    
    def _add_trend_line(self, dates: List[datetime.datetime], sizes: List[int]):
        """Add trend line to the chart."""
        try:
            # Convert dates to numerical values for trend calculation
            date_nums = mdates.date2num(dates)
            
            # Calculate trend line using numpy polyfit
            if self.timeline_config['size_scale'] == 'log':
                # Use log sizes for log scale
                log_sizes = np.log10(np.maximum(sizes, 1))
                z = np.polyfit(date_nums, log_sizes, 1)
                trend_sizes = 10 ** np.polyval(z, date_nums)
            else:
                z = np.polyfit(date_nums, sizes, 1)
                trend_sizes = np.polyval(z, date_nums)
            
            # Plot trend line
            self.trend_line = self.axes.plot(
                dates, trend_sizes,
                color='red',
                linewidth=2,
                alpha=0.8,
                linestyle='--',
                label='Trend'
            )[0]
            
        except Exception:
            # Skip trend line if calculation fails
            pass
    
    def _add_legend(self):
        """Add legend based on current color scheme."""
        scheme = self.timeline_config['color_scheme']
        
        if scheme == 'type':
            legend_elements = []
            for type_name, color in self.type_colors.items():
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w',
                              markerfacecolor=color, markersize=8,
                              label=type_name.title())
                )
        elif scheme == 'size':
            legend_elements = []
            size_labels = {
                'tiny': '< 1 MB',
                'small': '1-10 MB',
                'medium': '10-100 MB',
                'large': '100 MB-1 GB',
                'huge': '> 1 GB'
            }
            for size_name, color in self.size_colors.items():
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w',
                              markerfacecolor=color, markersize=8,
                              label=size_labels[size_name])
                )
        else:  # age
            legend_elements = []
            age_labels = {
                'very_new': '< 1 week',
                'new': '< 1 month',
                'recent': '< 6 months',
                'old': '< 1 year',
                'very_old': '> 1 year'
            }
            for age_name, color in self.age_colors.items():
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w',
                              markerfacecolor=color, markersize=8,
                              label=age_labels[age_name])
                )
        
        if 'legend_elements' in locals():
            self.axes.legend(
                handles=legend_elements,
                title=scheme.title(),
                loc='upper left',
                bbox_to_anchor=(1, 1),
                fontsize=self.chart_config['font_size'] - 2
            )
    
    def _setup_interactivity(self):
        """Setup interactive features for timeline chart."""
        if not MATPLOTLIB_AVAILABLE or not self.scatter_points:
            return
        
        # Enable picking on scatter points
        self.scatter_points.set_picker(True)
    
    def _on_chart_click(self, event):
        """Handle timeline chart click events."""
        if not event.inaxes or not self.timeline_data:
            return
        
        # Find closest point to click
        if hasattr(event, 'ind') and event.ind is not None:
            # Matplotlib picker event
            indices = event.ind
            if indices:
                idx = indices[0]
                if idx < len(self.timeline_data):
                    file_info = self.timeline_data[idx]
                    
                    # Emit signals
                    date_str = file_info['date'].strftime('%Y-%m-%d %H:%M:%S')
                    self.point_clicked.emit(
                        file_info['path'], file_info['size'], date_str)
                    
                    click_data = {
                        'name': file_info['name'],
                        'path': file_info['path'],
                        'size': file_info['size'],
                        'date': date_str,
                        'age_days': file_info['age_days']
                    }
                    self.chart_clicked.emit(click_data)
    
    def _on_chart_hover(self, event):
        """Handle timeline chart hover events for tooltips."""
        if not event.inaxes or not self.timeline_data:
            return
        
        # Find closest point to cursor (simplified approach)
        min_distance = float('inf')
        closest_point = None
        
        for i, item in enumerate(self.timeline_data):
            # Convert to display coordinates for distance calculation
            try:
                x_display, y_display = self.axes.transData.transform(
                    (mdates.date2num(item['date']), item['size']))
                cursor_x, cursor_y = event.x, event.y
                
                distance = ((x_display - cursor_x) ** 2 + 
                           (y_display - cursor_y) ** 2) ** 0.5
                
                if distance < min_distance and distance < 20:  # 20 pixel threshold
                    min_distance = distance
                    closest_point = item
            except Exception:
                continue
        
        if closest_point:
            # Create tooltip text
            tooltip_text = (
                f"{closest_point['name']}\n"
                f"Size: {self._format_size(closest_point['size'])}\n"
                f"Modified: {closest_point['date'].strftime('%Y-%m-%d %H:%M')}\n"
                f"Age: {closest_point['age_days']} days\n"
                f"Type: {closest_point['extension'] or 'No extension'}"
            )
            
            # Show tooltip
            QToolTip.showText(QCursor.pos(), tooltip_text)
            
            # Emit hover signal
            date_str = closest_point['date'].strftime('%Y-%m-%d %H:%M:%S')
            self.point_hovered.emit(
                closest_point['path'], closest_point['size'], date_str)
        else:
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
    
    def set_time_range(self, start_date: str, end_date: str):
        """Set specific time range for the chart."""
        try:
            start = datetime.datetime.fromisoformat(start_date)
            end = datetime.datetime.fromisoformat(end_date)
            
            if self.axes:
                self.axes.set_xlim(start, end)
                if self.canvas:
                    self.canvas.draw()
            
            self.time_range_changed.emit(start_date, end_date)
        except ValueError:
            pass  # Invalid date format
    
    def set_color_scheme(self, scheme: str):
        """Set color scheme ('type', 'size', or 'age')."""
        if scheme in ['type', 'size', 'age']:
            self.timeline_config['color_scheme'] = scheme
            # Reprocess colors for current data
            if self.timeline_data:
                for item in self.timeline_data:
                    if scheme == 'type':
                        item['color'] = self._get_type_color(item['extension'])
                    elif scheme == 'size':
                        item['color'] = self._get_size_color(item['size'])
                    else:  # age
                        item['color'] = self._get_age_color(item['age_days'])
                self.update_chart()
    
    def update_timeline_config(self, config: Dict[str, Any]):
        """Update timeline specific configuration."""
        self.timeline_config.update(config)
        self.update_chart()