"""
Treemap chart component for hierarchical directory visualization.

Displays directory structure as nested rectangles with sizes proportional
to directory/file sizes.
"""

from typing import Dict, Any, List, Tuple, Optional
import math
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .chart_base import ChartBase


class DirectoryTreemapChart(ChartBase):
    """
    Treemap visualization for hierarchical directory structure.
    
    Features:
    - Nested rectangles representing directory hierarchy
    - Size-proportional visualization
    - Interactive drill-down capability
    - Color coding by depth or file type
    - Hover tooltips with detailed information
    """
    
    # Additional signals specific to treemap
    directory_clicked = pyqtSignal(str, int)  # directory path, size
    directory_hovered = pyqtSignal(str, int)  # directory path, size
    drill_down_requested = pyqtSignal(str)    # directory path
    
    def __init__(self, parent=None):
        """Initialize the treemap chart component."""
        super().__init__("Directory Structure Treemap", parent)
        
        # Treemap specific configuration
        self.treemap_config = {
            'max_depth': 3,        # Maximum depth to display
            'min_area': 0.01,      # Minimum area percentage to show
            'padding': 0.02,       # Padding between rectangles
            'color_scheme': 'depth',  # 'depth', 'type', or 'size'
            'show_labels': True,   # Show directory names
            'label_threshold': 0.05,  # Min area to show labels
            'font_scale': 1.0,     # Font size scaling
            'border_width': 1.0,   # Border width for rectangles
            'highlight_on_hover': True  # Highlight on hover
        }
        
        # Data structures for treemap
        self.tree_data: Optional[Dict[str, Any]] = None
        self.rectangles: List[Dict[str, Any]] = []
        self.patches_list: List[patches.Rectangle] = []
        self.current_root: str = ""
        
        # Color schemes
        self._setup_color_schemes()
    
    def _setup_color_schemes(self):
        """Setup color schemes for different visualization modes."""
        # Depth-based colors (lighter as depth increases)
        self.depth_colors = [
            '#2C3E50',  # Level 0 - Dark
            '#34495E',  # Level 1
            '#5D6D7E',  # Level 2
            '#85929E',  # Level 3
            '#AEB6BF',  # Level 4
            '#D5DBDB'   # Level 5+
        ]
        
        # Size-based color scheme
        self.size_colors = {
            'huge': '#E74C3C',     # Red
            'large': '#F39C12',    # Orange
            'medium': '#F1C40F',   # Yellow
            'small': '#2ECC71',    # Green
            'tiny': '#95A5A6'      # Gray
        }
        
        # File type color scheme
        self.type_colors = {
            'documents': '#3498DB',  # Blue
            'images': '#E67E22',     # Orange
            'videos': '#9B59B6',     # Purple
            'audio': '#1ABC9C',      # Turquoise
            'archives': '#34495E',   # Dark Gray
            'code': '#27AE60',       # Green
            'other': '#95A5A6'       # Gray
        }
    
    def set_data(self, data: Dict[str, Any]):
        """Set directory tree data for the treemap."""
        if not data or 'directory_tree' not in data:
            return
        
        self.tree_data = data.get('directory_tree', {})
        self.current_root = data.get('path', '')
        
        if not self.tree_data:
            return
        
        # Process tree data for treemap layout
        self._process_tree_data()
        
        # Update the chart
        super().set_data(data)
    
    def _process_tree_data(self):
        """Process tree data and calculate treemap layout."""
        if not self.tree_data:
            return
        
        # Calculate treemap rectangles
        self.rectangles = []
        total_size = self.tree_data.get('size', 0)
        
        if total_size > 0:
            # Start recursive layout calculation
            self._calculate_treemap_layout(
                self.tree_data,
                x=0, y=0, width=1, height=1,
                depth=0, path=self.current_root
            )
    
    def _calculate_treemap_layout(self, node: Dict[str, Any], 
                                 x: float, y: float, 
                                 width: float, height: float,
                                 depth: int, path: str):
        """Calculate treemap layout using squarified algorithm."""
        if depth > self.treemap_config['max_depth']:
            return
        
        children = node.get('children', {})
        if not children:
            return
        
        # Filter children by minimum area
        total_size = node.get('size', 0)
        min_size = total_size * self.treemap_config['min_area']
        
        valid_children = []
        for name, child in children.items():
            child_size = child.get('size', 0)
            if child_size >= min_size:
                valid_children.append((name, child, child_size))
        
        if not valid_children:
            return
        
        # Sort by size (descending)
        valid_children.sort(key=lambda x: x[2], reverse=True)
        
        # Calculate layout using simplified squarified algorithm
        self._squarify_layout(
            valid_children, x, y, width, height, depth, path
        )
    
    def _squarify_layout(self, children: List[Tuple[str, Dict, int]],
                        x: float, y: float, width: float, height: float,
                        depth: int, parent_path: str):
        """Implement squarified treemap layout algorithm."""
        if not children:
            return
        
        total_size = sum(child[2] for child in children)
        if total_size == 0:
            return
        
        # Apply padding
        padding = self.treemap_config['padding']
        padded_x = x + padding
        padded_y = y + padding
        padded_width = width - 2 * padding
        padded_height = height - 2 * padding
        
        # Simple row-based layout for now
        current_y = padded_y
        
        for name, child, size in children:
            # Calculate rectangle dimensions
            area_ratio = size / total_size
            rect_height = padded_height * area_ratio
            
            # Create rectangle data
            child_path = f"{parent_path}/{name}" if parent_path else name
            
            # Determine color based on scheme
            color = self._get_rectangle_color(child, depth, size, total_size)
            
            rect_data = {
                'name': name,
                'path': child_path,
                'x': padded_x,
                'y': current_y,
                'width': padded_width,
                'height': rect_height,
                'size': size,
                'depth': depth,
                'color': color,
                'is_directory': 'children' in child,
                'area_ratio': area_ratio
            }
            
            self.rectangles.append(rect_data)
            
            # Recursively process subdirectories
            if 'children' in child and rect_height > 0.05:  # Min height for subdivision
                self._calculate_treemap_layout(
                    child,
                    padded_x, current_y, padded_width, rect_height,
                    depth + 1, child_path
                )
            
            current_y += rect_height
    
    def _get_rectangle_color(self, node: Dict[str, Any], depth: int, 
                           size: int, total_size: int) -> str:
        """Get color for rectangle based on current color scheme."""
        scheme = self.treemap_config['color_scheme']
        
        if scheme == 'depth':
            return self.depth_colors[min(depth, len(self.depth_colors) - 1)]
        
        elif scheme == 'size':
            if total_size == 0:
                return self.size_colors['tiny']
            
            percentage = (size / total_size) * 100
            if percentage >= 25:
                return self.size_colors['huge']
            elif percentage >= 10:
                return self.size_colors['large']
            elif percentage >= 5:
                return self.size_colors['medium']
            elif percentage >= 1:
                return self.size_colors['small']
            else:
                return self.size_colors['tiny']
        
        elif scheme == 'type':
            # Determine type based on children or file extension
            if 'children' in node:
                return self.type_colors['other']  # Directory
            else:
                # File - determine type by extension
                name = node.get('name', '')
                ext = name.split('.')[-1].lower() if '.' in name else ''
                
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
                    return self.type_colors['images']
                elif ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv']:
                    return self.type_colors['videos']
                elif ext in ['mp3', 'wav', 'flac', 'aac']:
                    return self.type_colors['audio']
                elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
                    return self.type_colors['archives']
                elif ext in ['py', 'js', 'html', 'css', 'cpp', 'java']:
                    return self.type_colors['code']
                elif ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
                    return self.type_colors['documents']
                else:
                    return self.type_colors['other']
        
        return self.depth_colors[0]  # Default
    
    def update_chart(self):
        """Update the treemap chart with current data."""
        if not self.rectangles or not self.axes:
            return
        
        # Clear previous chart
        self.axes.clear()
        self.patches_list = []
        
        # Set up axes
        self.axes.set_xlim(0, 1)
        self.axes.set_ylim(0, 1)
        self.axes.set_aspect('equal')
        self.axes.axis('off')  # Hide axes for treemap
        
        # Draw rectangles
        for rect_data in self.rectangles:
            # Create rectangle patch
            rect_patch = patches.Rectangle(
                (rect_data['x'], rect_data['y']),
                rect_data['width'],
                rect_data['height'],
                facecolor=rect_data['color'],
                edgecolor='white',
                linewidth=self.treemap_config['border_width'],
                alpha=0.8,
                picker=True
            )
            
            self.axes.add_patch(rect_patch)
            self.patches_list.append(rect_patch)
            
            # Add label if rectangle is large enough
            if (self.treemap_config['show_labels'] and 
                rect_data['area_ratio'] >= self.treemap_config['label_threshold']):
                
                # Calculate font size based on rectangle size
                font_size = max(
                    6,
                    int(self.chart_config['font_size'] * 
                        self.treemap_config['font_scale'] * 
                        math.sqrt(rect_data['area_ratio']))
                )
                
                # Add text label
                label_text = rect_data['name']
                if len(label_text) > 15:
                    label_text = label_text[:12] + '...'
                
                self.axes.text(
                    rect_data['x'] + rect_data['width'] / 2,
                    rect_data['y'] + rect_data['height'] / 2,
                    label_text,
                    ha='center',
                    va='center',
                    fontsize=font_size,
                    color='white',
                    weight='bold',
                    wrap=True
                )
        
        # Set title
        title = f"Directory Structure: {self.current_root}"
        if len(title) > 50:
            title = "..." + title[-47:]
        
        self.axes.set_title(
            title,
            fontsize=self.chart_config['font_size'] + 1,
            color=self.chart_config['text_color'],
            pad=20
        )
        
        # Setup interactive features
        self._setup_interactivity()
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
        
        # Emit update signal
        self.chart_updated.emit()
    
    def _setup_interactivity(self):
        """Setup interactive features for treemap."""
        if not MATPLOTLIB_AVAILABLE or not self.patches_list:
            return
        
        # Connect events to patches
        for patch in self.patches_list:
            patch.set_picker(True)
    
    def _on_chart_click(self, event):
        """Handle treemap click events."""
        if not event.inaxes or not self.rectangles:
            return
        
        # Find which rectangle was clicked
        for i, rect_data in enumerate(self.rectangles):
            if (rect_data['x'] <= event.xdata <= rect_data['x'] + rect_data['width'] and
                rect_data['y'] <= event.ydata <= rect_data['y'] + rect_data['height']):
                
                # Emit directory clicked signal
                self.directory_clicked.emit(rect_data['path'], rect_data['size'])
                
                # Emit drill down signal for directories
                if rect_data['is_directory']:
                    self.drill_down_requested.emit(rect_data['path'])
                
                # Emit general chart clicked signal
                click_data = {
                    'name': rect_data['name'],
                    'path': rect_data['path'],
                    'size': rect_data['size'],
                    'depth': rect_data['depth'],
                    'is_directory': rect_data['is_directory']
                }
                self.chart_clicked.emit(click_data)
                break
    
    def _on_chart_hover(self, event):
        """Handle treemap hover events for tooltips."""
        if not event.inaxes or not self.rectangles:
            return
        
        # Find which rectangle is being hovered
        for rect_data in self.rectangles:
            if (rect_data['x'] <= event.xdata <= rect_data['x'] + rect_data['width'] and
                rect_data['y'] <= event.ydata <= rect_data['y'] + rect_data['height']):
                
                # Create tooltip text
                tooltip_text = (
                    f"{rect_data['name']}\n"
                    f"Size: {self._format_size(rect_data['size'])}\n"
                    f"Type: {'Directory' if rect_data['is_directory'] else 'File'}\n"
                    f"Depth: {rect_data['depth']}\n"
                    f"Path: {rect_data['path']}"
                )
                
                # Show tooltip
                QToolTip.showText(
                    QCursor.pos(),
                    tooltip_text
                )
                
                # Highlight rectangle if enabled
                if self.treemap_config['highlight_on_hover']:
                    self._highlight_rectangle(rect_data, True)
                
                # Emit hover signal
                self.directory_hovered.emit(rect_data['path'], rect_data['size'])
                return
        
        # Hide tooltip and remove highlights if not over any rectangle
        QToolTip.hideText()
        if self.treemap_config['highlight_on_hover']:
            self._clear_highlights()
    
    def _highlight_rectangle(self, rect_data: Dict[str, Any], highlight: bool):
        """Highlight a specific rectangle."""
        # Find corresponding patch and highlight it
        for i, patch in enumerate(self.patches_list):
            if i < len(self.rectangles) and self.rectangles[i] == rect_data:
                if highlight:
                    patch.set_alpha(1.0)
                    patch.set_edgecolor('yellow')
                    patch.set_linewidth(3)
                else:
                    patch.set_alpha(0.8)
                    patch.set_edgecolor('white')
                    patch.set_linewidth(self.treemap_config['border_width'])
                break
        
        if self.canvas:
            self.canvas.draw_idle()
    
    def _clear_highlights(self):
        """Clear all rectangle highlights."""
        for patch in self.patches_list:
            patch.set_alpha(0.8)
            patch.set_edgecolor('white')
            patch.set_linewidth(self.treemap_config['border_width'])
        
        if self.canvas:
            self.canvas.draw_idle()
    
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
    
    def drill_down(self, directory_path: str):
        """Drill down into a specific directory."""
        # This would need to be implemented with new data
        # For now, emit signal for parent to handle
        self.drill_down_requested.emit(directory_path)
    
    def set_color_scheme(self, scheme: str):
        """Set color scheme ('depth', 'size', or 'type')."""
        if scheme in ['depth', 'size', 'type']:
            self.treemap_config['color_scheme'] = scheme
            # Reprocess colors for current rectangles
            if self.rectangles and self.tree_data:
                total_size = self.tree_data.get('size', 0)
                for rect_data in self.rectangles:
                    # Find corresponding node (simplified)
                    rect_data['color'] = self._get_rectangle_color(
                        {'name': rect_data['name']}, 
                        rect_data['depth'], 
                        rect_data['size'], 
                        total_size
                    )
                self.update_chart()
    
    def update_treemap_config(self, config: Dict[str, Any]):
        """Update treemap specific configuration."""
        self.treemap_config.update(config)
        if self.tree_data:
            self._process_tree_data()
        self.update_chart()