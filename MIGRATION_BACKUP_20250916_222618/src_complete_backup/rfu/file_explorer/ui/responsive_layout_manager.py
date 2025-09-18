
"""
Responsive Layout Manager for Multi-Pane File Explorer

This module provides a sophisticated responsive layout system that dynamically
adjusts available layout options based on the number of content panes, with
intelligent constraint management and smooth transitions.

Features:
- Single pane: Unrestricted layout flexibility (full-width, centered,
  sidebar, custom)
- Dual pane: Optimized horizontal/vertical arrangements  
- 3+ panes: Comprehensive layouts (column, row, grid) with responsive
  breakpoints
- Seamless transitions with content hierarchy preservation
- Automatic responsive breakpoint detection and adaptation
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QObject, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QScreen
from PyQt5.QtWidgets import QApplication, QWidget


class LayoutType(Enum):
    """Available layout types with specific use cases."""
    # Single pane layouts
    FULL_WIDTH = "full_width"
    CENTERED = "centered"
    LEFT_SIDEBAR = "left_sidebar"
    RIGHT_SIDEBAR = "right_sidebar"
    CUSTOM_POSITION = "custom_position"
    
    # Dual pane layouts
    HORIZONTAL_SPLIT = "horizontal_split"
    VERTICAL_SPLIT = "vertical_split"
    
    # Multi-pane layouts
    HORIZONTAL_ROW = "horizontal_row"
    VERTICAL_COLUMN = "vertical_column"
    GRID_2X2 = "grid_2x2"
    GRID_2X3 = "grid_2x3"
    GRID_3X2 = "grid_3x2"
    ADAPTIVE_GRID = "adaptive_grid"


class ViewportType(Enum):
    """Viewport categories for responsive behavior."""
    MOBILE = "mobile"          # < 768px width
    TABLET = "tablet"          # 768px - 1024px width
    DESKTOP = "desktop"        # 1024px - 1440px width
    LARGE_DESKTOP = "large"    # > 1440px width


@dataclass
class LayoutConstraint:
    """Defines constraints for layout availability."""
    min_panes: int = 1
    max_panes: int = 4
    min_viewport_width: int = 0
    min_viewport_height: int = 0
    viewport_types: List[ViewportType] = field(default_factory=list)
    requires_features: List[str] = field(default_factory=list)


@dataclass
class LayoutConfiguration:
    """Complete configuration for a specific layout."""
    layout_type: LayoutType
    display_name: str
    description: str
    constraint: LayoutConstraint
    grid_dimensions: Optional[Tuple[int, int]] = None
    spacing: int = 2
    margins: Tuple[int, int, int, int] = (0, 0, 0, 0)  # top,right,bottom,left
    animation_duration: int = 300
    priority: int = 0  # Higher priority layouts are preferred


@dataclass
class ResponsiveBreakpoint:
    """Responsive breakpoint configuration."""
    name: str
    min_width: int
    max_width: int
    viewport_type: ViewportType
    grid_columns: Dict[int, int]  # pane_count -> column_count
    preferred_layouts: List[LayoutType]
    layout_overrides: Dict[LayoutType, LayoutType] = field(
        default_factory=dict
    )


class ResponsiveLayoutManager(QObject):
    """
    Sophisticated responsive layout manager with dynamic constraint evaluation.
    
    Manages layout options and transitions based on pane count, viewport size,
    and user preferences while maintaining content hierarchy and smooth
    transitions.
    """
    
    # Signals
    layout_changed = pyqtSignal(LayoutType, dict)
    viewport_changed = pyqtSignal(ViewportType, tuple)
    constraint_updated = pyqtSignal(int, list)  # pane_count, available_layouts
    transition_started = pyqtSignal(LayoutType, LayoutType)
    transition_completed = pyqtSignal(LayoutType)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger('RFU.ResponsiveLayoutManager')
        
        # Current state
        self.current_layout: Optional[LayoutType] = None
        self.current_viewport: ViewportType = ViewportType.DESKTOP
        self.viewport_size: Tuple[int, int] = (1920, 1080)
        self.pane_count: int = 1
        self.container_widget: Optional[QWidget] = None
        
        # Configuration
        self.layout_configs: Dict[LayoutType, LayoutConfiguration] = {}
        self.responsive_breakpoints: List[ResponsiveBreakpoint] = []
        self.transition_animations: List[QPropertyAnimation] = []
        self.content_hierarchy_enabled: bool = True
        
        # Performance optimization
        self.layout_cache: Dict[str, List[LayoutType]] = {}
        self.constraint_cache: Dict[
            Tuple[int, ViewportType], List[LayoutType]
        ] = {}
        
        # Initialize configurations
        self._initialize_layout_configurations()
        self._initialize_responsive_breakpoints()
        
        # Setup viewport monitoring
        self._setup_viewport_monitoring()
        
        msg = "ResponsiveLayoutManager initialized with comprehensive layout"
        self.logger.info(f"{msg} support")
    
    def _initialize_layout_configurations(self):
        """Initialize all available layout configurations."""
        
        # Single pane layouts - unrestricted flexibility
        self.layout_configs[LayoutType.FULL_WIDTH] = LayoutConfiguration(
            layout_type=LayoutType.FULL_WIDTH,
            display_name="Full Width",
            description="Content spans the entire available width",
            constraint=LayoutConstraint(
                min_panes=1, max_panes=1,
                viewport_types=[
                    ViewportType.MOBILE, ViewportType.TABLET,
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=10
        )
        
        self.layout_configs[LayoutType.CENTERED] = LayoutConfiguration(
            layout_type=LayoutType.CENTERED,
            display_name="Centered",
            description="Content centered with margins on both sides",
            constraint=LayoutConstraint(
                min_panes=1, max_panes=1,
                min_viewport_width=600,
                viewport_types=[
                    ViewportType.TABLET, ViewportType.DESKTOP,
                    ViewportType.LARGE_DESKTOP
                ]
            ),
            margins=(0, 100, 0, 100),
            priority=8
        )
        
        self.layout_configs[LayoutType.LEFT_SIDEBAR] = LayoutConfiguration(
            layout_type=LayoutType.LEFT_SIDEBAR,
            display_name="Left Sidebar",
            description="Content positioned as left sidebar with remaining space",
            constraint=LayoutConstraint(
                min_panes=1, max_panes=1,
                min_viewport_width=800,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=6
        )
        
        self.layout_configs[LayoutType.RIGHT_SIDEBAR] = LayoutConfiguration(
            layout_type=LayoutType.RIGHT_SIDEBAR,
            display_name="Right Sidebar",
            description="Content positioned as right sidebar with remaining space",
            constraint=LayoutConstraint(
                min_panes=1, max_panes=1,
                min_viewport_width=800,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=6
        )
        
        self.layout_configs[LayoutType.CUSTOM_POSITION] = LayoutConfiguration(
            layout_type=LayoutType.CUSTOM_POSITION,
            display_name="Custom Position",
            description="User-defined positioning with drag and resize",
            constraint=LayoutConstraint(
                min_panes=1, max_panes=1,
                min_viewport_width=1024,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ],
                requires_features=["advanced_positioning"]
            ),
            priority=4
        )
        
        # Dual pane layouts - horizontal/vertical optimization
        self.layout_configs[LayoutType.HORIZONTAL_SPLIT] = LayoutConfiguration(
            layout_type=LayoutType.HORIZONTAL_SPLIT,
            display_name="Horizontal Split",
            description="Two panes side by side horizontally",
            constraint=LayoutConstraint(
                min_panes=2, max_panes=2,
                min_viewport_width=600,
                viewport_types=[
                    ViewportType.TABLET, ViewportType.DESKTOP,
                    ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=10
        )
        
        self.layout_configs[LayoutType.VERTICAL_SPLIT] = LayoutConfiguration(
            layout_type=LayoutType.VERTICAL_SPLIT,
            display_name="Vertical Split",
            description="Two panes stacked vertically",
            constraint=LayoutConstraint(
                min_panes=2, max_panes=2,
                min_viewport_height=600,
                viewport_types=[
                    ViewportType.MOBILE, ViewportType.TABLET,
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=8
        )
        
        # Multi-pane layouts - comprehensive options
        self.layout_configs[LayoutType.HORIZONTAL_ROW] = LayoutConfiguration(
            layout_type=LayoutType.HORIZONTAL_ROW,
            display_name="Horizontal Row",
            description="All panes arranged in a horizontal row",
            constraint=LayoutConstraint(
                min_panes=3, max_panes=4,
                min_viewport_width=900,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=9
        )
        
        self.layout_configs[LayoutType.VERTICAL_COLUMN] = LayoutConfiguration(
            layout_type=LayoutType.VERTICAL_COLUMN,
            display_name="Vertical Column",
            description="All panes arranged in a vertical column",
            constraint=LayoutConstraint(
                min_panes=3, max_panes=4,
                min_viewport_height=800,
                viewport_types=[
                    ViewportType.TABLET, ViewportType.DESKTOP,
                    ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=7
        )
        
        self.layout_configs[LayoutType.GRID_2X2] = LayoutConfiguration(
            layout_type=LayoutType.GRID_2X2,
            display_name="2×2 Grid",
            description="Four panes arranged in a 2×2 grid",
            constraint=LayoutConstraint(
                min_panes=4, max_panes=4,
                min_viewport_width=800,
                min_viewport_height=600,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            grid_dimensions=(2, 2),
            priority=8
        )
        
        self.layout_configs[LayoutType.GRID_2X3] = LayoutConfiguration(
            layout_type=LayoutType.GRID_2X3,
            display_name="2×3 Grid",
            description="Panes arranged in a 2×3 grid layout",
            constraint=LayoutConstraint(
                min_panes=3, max_panes=4,
                min_viewport_width=1000,
                min_viewport_height=700,
                viewport_types=[
                    ViewportType.DESKTOP, ViewportType.LARGE_DESKTOP
                ]
            ),
            grid_dimensions=(2, 3),
            priority=6
        )
        
        self.layout_configs[LayoutType.ADAPTIVE_GRID] = LayoutConfiguration(
            layout_type=LayoutType.ADAPTIVE_GRID,
            display_name="Adaptive Grid",
            description="Adapts grid layout based on pane count and viewport",
            constraint=LayoutConstraint(
                min_panes=3, max_panes=4,
                min_viewport_width=600,
                viewport_types=[
                    ViewportType.TABLET, ViewportType.DESKTOP,
                    ViewportType.LARGE_DESKTOP
                ]
            ),
            priority=5
        )
    
    def _initialize_responsive_breakpoints(self):
        """Initialize responsive breakpoints for adaptive behavior."""
        
        self.responsive_breakpoints = [
            ResponsiveBreakpoint(
                name="Mobile",
                min_width=0,
                max_width=767,
                viewport_type=ViewportType.MOBILE,
                grid_columns={2: 1, 3: 1, 4: 2},
                preferred_layouts=[
                    LayoutType.FULL_WIDTH,
                    LayoutType.VERTICAL_SPLIT,
                    LayoutType.VERTICAL_COLUMN
                ],
                layout_overrides={
                    LayoutType.HORIZONTAL_SPLIT: LayoutType.VERTICAL_SPLIT,
                    LayoutType.GRID_2X2: LayoutType.VERTICAL_COLUMN
                }
            ),
            
            ResponsiveBreakpoint(
                name="Tablet",
                min_width=768,
                max_width=1023,
                viewport_type=ViewportType.TABLET,
                grid_columns={2: 2, 3: 2, 4: 2},
                preferred_layouts=[
                    LayoutType.FULL_WIDTH,
                    LayoutType.CENTERED,
                    LayoutType.HORIZONTAL_SPLIT,
                    LayoutType.VERTICAL_SPLIT,
                    LayoutType.ADAPTIVE_GRID
                ]
            ),
            
            ResponsiveBreakpoint(
                name="Desktop",
                min_width=1024,
                max_width=1439,
                viewport_type=ViewportType.DESKTOP,
                grid_columns={2: 2, 3: 3, 4: 2},
                preferred_layouts=[
                    LayoutType.FULL_WIDTH,
                    LayoutType.CENTERED,
                    LayoutType.LEFT_SIDEBAR,
                    LayoutType.RIGHT_SIDEBAR,
                    LayoutType.HORIZONTAL_SPLIT,
                    LayoutType.VERTICAL_SPLIT,
                    LayoutType.HORIZONTAL_ROW,
                    LayoutType.VERTICAL_COLUMN,
                    LayoutType.GRID_2X2,
                    LayoutType.ADAPTIVE_GRID
                ]
            ),
            
            ResponsiveBreakpoint(
                name="Large Desktop",
                min_width=1440,
                max_width=9999,
                viewport_type=ViewportType.LARGE_DESKTOP,
                grid_columns={2: 2, 3: 3, 4: 4},
                preferred_layouts=[
                    LayoutType.FULL_WIDTH,
                    LayoutType.CENTERED,
                    LayoutType.LEFT_SIDEBAR,
                    LayoutType.RIGHT_SIDEBAR,
                    LayoutType.CUSTOM_POSITION,
                    LayoutType.HORIZONTAL_SPLIT,
                    LayoutType.VERTICAL_SPLIT,
                    LayoutType.HORIZONTAL_ROW,
                    LayoutType.VERTICAL_COLUMN,
                    LayoutType.GRID_2X2,
                    LayoutType.GRID_2X3,
                    LayoutType.ADAPTIVE_GRID
                ]
            )
        ]
    
    def _setup_viewport_monitoring(self):
        """Setup viewport size monitoring for responsive behavior."""
        try:
            app = QApplication.instance()
            if app:
                # Monitor primary screen changes
                primary_screen = app.primaryScreen()
                if primary_screen:
                    primary_screen.geometryChanged.connect(
                        self._on_screen_geometry_changed
                    )
                    self._update_viewport_info(primary_screen)
        except Exception as e:
            self.logger.warning(f"Failed to setup viewport monitoring: {e}")
    
    def _on_screen_geometry_changed(self, geometry: QRect):
        """Handle screen geometry changes."""
        self._update_viewport_info_from_geometry(
            geometry.width(), geometry.height()
        )
    
    def _update_viewport_info(self, screen: QScreen):
        """Update viewport information from screen object."""
        geometry = screen.geometry()
        self._update_viewport_info_from_geometry(
            geometry.width(), geometry.height()
        )
    
    def _update_viewport_info_from_geometry(self, width: int, height: int):
        """Update viewport information from width and height."""
        old_viewport = self.current_viewport
        old_size = self.viewport_size
        
        self.viewport_size = (width, height)
        self.current_viewport = self._determine_viewport_type(width)
        
        if (old_viewport != self.current_viewport or 
                old_size != self.viewport_size):
            self.viewport_changed.emit(self.current_viewport, self.viewport_size)
            self._clear_constraint_cache()
            viewport_val = self.current_viewport.value
            self.logger.info(f"Viewport changed: {viewport_val} ({width}×{height})")
    
    def _determine_viewport_type(self, width: int) -> ViewportType:
        """Determine viewport type based on width."""
        for breakpoint in self.responsive_breakpoints:
            if breakpoint.min_width <= width <= breakpoint.max_width:
                return breakpoint.viewport_type
        return ViewportType.DESKTOP
    
    def get_available_layouts(
            self, pane_count: int, 
            viewport_type: Optional[ViewportType] = None
    ) -> List[LayoutType]:
        """
        Get available layouts for the given pane count and viewport.
        
        Args:
            pane_count: Number of content panes
            viewport_type: Viewport type (uses current if None)
            
        Returns:
            List of available layout types sorted by priority
        """
        if viewport_type is None:
            viewport_type = self.current_viewport
        
        # Check cache first
        cache_key = (pane_count, viewport_type)
        if cache_key in self.constraint_cache:
            return self.constraint_cache[cache_key]
        
        available_layouts = []
        current_breakpoint = self._get_current_breakpoint(viewport_type)
        
        for layout_type, config in self.layout_configs.items():
            if self._is_layout_available(
                    config, pane_count, viewport_type, current_breakpoint
            ):
                available_layouts.append(layout_type)
        
        # Sort by priority (higher priority first)
        available_layouts.sort(
            key=lambda lt: self.layout_configs[lt].priority, reverse=True
        )
        
        # Apply viewport-specific preferences
        if current_breakpoint:
            preferred = [
                lt for lt in current_breakpoint.preferred_layouts 
                if lt in available_layouts
            ]
            other = [lt for lt in available_layouts if lt not in preferred]
            available_layouts = preferred + other
        
        # Cache result
        self.constraint_cache[cache_key] = available_layouts
        
        return available_layouts
    
    def _is_layout_available(
            self, config: LayoutConfiguration, pane_count: int,
            viewport_type: ViewportType, 
            breakpoint: Optional[ResponsiveBreakpoint]
    ) -> bool:
        """Check if a layout is available under current conditions."""
        constraint = config.constraint
        
        # Check pane count constraint
        if not (constraint.min_panes <= pane_count <= constraint.max_panes):
            return False
        
        # Check viewport type constraint
        if (constraint.viewport_types and 
                viewport_type not in constraint.viewport_types):
            return False
        
        # Check viewport size constraints
        width, height = self.viewport_size
        if (width < constraint.min_viewport_width or 
                height < constraint.min_viewport_height):
            return False
        
        # Check feature requirements (would be implemented based on features)
        if constraint.requires_features:
            # TODO: Implement feature checking
            pass
        
        return True
    
    def _get_current_breakpoint(
            self, viewport_type: ViewportType
    ) -> Optional[ResponsiveBreakpoint]:
        """Get the current responsive breakpoint."""
        for breakpoint in self.responsive_breakpoints:
            if breakpoint.viewport_type == viewport_type:
                return breakpoint
        return None
    
    def set_pane_count(self, pane_count: int):
        """Update the pane count and refresh available layouts."""
        if self.pane_count != pane_count:
            old_count = self.pane_count
            self.pane_count = pane_count
            
            # Clear cache since constraints have changed
            self._clear_constraint_cache()
            
            # Get new available layouts
            available = self.get_available_layouts(pane_count)
            self.constraint_updated.emit(pane_count, available)
            
            # Check if current layout is still valid
            if self.current_layout and self.current_layout not in available:
                # Automatically switch to best available layout
                if available:
                    self.apply_layout(available[0])
            
            self.logger.info(f"Pane count changed from {old_count} to {pane_count}")
    
    def apply_layout(self, layout_type: LayoutType, 
                    container: Optional[QWidget] = None,
                    animate: bool = True) -> bool:
        """
        Apply the specified layout to the container.
        
        Args:
            layout_type: Layout type to apply
            container: Container widget (uses stored if None)
            animate: Whether to animate the transition
            
        Returns:
            True if layout was applied successfully
        """
        if container:
            self.container_widget = container
        
        if not self.container_widget:
            self.logger.error(
                "No container widget available for layout application"
            )
            return False
        
        if layout_type not in self.layout_configs:
            self.logger.error(f"Unknown layout type: {layout_type}")
            return False
        
        # Check if layout is available
        available = self.get_available_layouts(self.pane_count)
        if layout_type not in available:
            self.logger.warning(
                f"Layout {layout_type.value} not available for current conditions"
            )
            return False
        
        old_layout = self.current_layout
        
        try:
            if animate and old_layout != layout_type:
                self.transition_started.emit(old_layout, layout_type)
                self._apply_layout_with_animation(layout_type, old_layout)
            else:
                self._apply_layout_immediately(layout_type)
            
            self.current_layout = layout_type
            self.layout_changed.emit(
                layout_type, self._get_layout_info(layout_type)
            )
            
            if animate and old_layout != layout_type:
                self.transition_completed.emit(layout_type)
            
            self.logger.info(f"Applied layout: {layout_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply layout {layout_type.value}: {e}")
            return False
    
    def _apply_layout_immediately(self, layout_type: LayoutType):
        """Apply layout immediately without animation."""
        config = self.layout_configs[layout_type]
        
        single_pane_layouts = [
            LayoutType.FULL_WIDTH, LayoutType.CENTERED, 
            LayoutType.LEFT_SIDEBAR, LayoutType.RIGHT_SIDEBAR,
            LayoutType.CUSTOM_POSITION
        ]
        dual_pane_layouts = [
            LayoutType.HORIZONTAL_SPLIT, LayoutType.VERTICAL_SPLIT
        ]
        
        if layout_type in single_pane_layouts:
            self._apply_single_pane_layout(layout_type, config)
        elif layout_type in dual_pane_layouts:
            self._apply_dual_pane_layout(layout_type, config)
        else:
            self._apply_multi_pane_layout(layout_type, config)
    
    def _apply_layout_with_animation(self, layout_type: LayoutType, 
                                   old_layout: Optional[LayoutType]):
        """Apply layout with smooth animation transition."""
        # For now, apply immediately (animation implementation would be complex)
        self._apply_layout_immediately(layout_type)
        
        # TODO: Implement sophisticated animation system
        # This would involve:
        # 1. Capturing current widget positions
        # 2. Calculating target positions
        # 3. Creating smooth transition animations
        # 4. Maintaining content hierarchy during transition
    
    def _apply_single_pane_layout(self, layout_type: LayoutType, 
                                 config: LayoutConfiguration):
        """Apply single pane layout with unrestricted flexibility."""
        # Implementation would depend on the container widget type
        # This is a placeholder for the actual layout application logic
        self.logger.debug(f"Applying single pane layout: {layout_type.value}")
    
    def _apply_dual_pane_layout(self, layout_type: LayoutType, 
                               config: LayoutConfiguration):
        """Apply dual pane layout with horizontal/vertical optimization."""
        self.logger.debug(f"Applying dual pane layout: {layout_type.value}")
    
    def _apply_multi_pane_layout(self, layout_type: LayoutType, 
                                config: LayoutConfiguration):
        """Apply multi-pane layout with comprehensive options."""
        self.logger.debug(f"Applying multi-pane layout: {layout_type.value}")
    
    def _get_layout_info(self, layout_type: LayoutType) -> Dict[str, Any]:
        """Get layout information dictionary."""
        config = self.layout_configs[layout_type]
        return {
            'type': layout_type.value,
            'display_name': config.display_name,
            'description': config.description,
            'grid_dimensions': config.grid_dimensions,
            'spacing': config.spacing,
            'margins': config.margins
        }
    
    def get_layout_display_names(
            self, pane_count: int
    ) -> List[Tuple[LayoutType, str]]:
        """Get layout types and their display names for UI."""
        available = self.get_available_layouts(pane_count)
        return [(layout_type, self.layout_configs[layout_type].display_name) 
                for layout_type in available]
    
    def get_recommended_layout(self, pane_count: int) -> Optional[LayoutType]:
        """Get the recommended layout for the given pane count."""
        available = self.get_available_layouts(pane_count)
        return available[0] if available else None
    
    def _clear_constraint_cache(self):
        """Clear the constraint cache when conditions change."""
        self.constraint_cache.clear()
    
    def is_layout_available(self, layout_type: LayoutType, 
                           pane_count: Optional[int] = None) -> bool:
        """Check if a specific layout is currently available."""
        if pane_count is None:
            pane_count = self.pane_count
        
        available = self.get_available_layouts(pane_count)
        return layout_type in available
    
    def get_current_layout_info(self) -> Dict[str, Any]:
        """Get information about the current layout."""
        if self.current_layout:
            return self._get_layout_info(self.current_layout)
        return {}
    
    def enable_content_hierarchy(self, enabled: bool = True):
        """Enable or disable content hierarchy maintenance during transitions."""
        self.content_hierarchy_enabled = enabled
        status = 'enabled' if enabled else 'disabled'
        self.logger.info(f"Content hierarchy {status}")
    
    def get_viewport_info(self) -> Dict[str, Any]:
        """Get current viewport information."""
        current_bp = self._get_current_breakpoint(self.current_viewport)
        return {
            'type': self.current_viewport.value,
            'size': self.viewport_size,
            'breakpoint': current_bp.name if current_bp else None
        }


class LayoutImplementor:
    """
    Handles the actual implementation of layout configurations.
    
    This class provides concrete layout implementation methods that work
    with Qt widgets and splitters to create the desired arrangements.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def implement_single_pane_layout(
            self, container: QWidget, panes: List[QWidget],
            layout_type: LayoutType, config: LayoutConfiguration
    ) -> bool:
        """Implement single pane layout configurations."""
        if not panes:
            return False
        
        pane = panes[0]
        
        try:
            if layout_type == LayoutType.FULL_WIDTH:
                self._implement_full_width(container, pane, config)
            elif layout_type == LayoutType.CENTERED:
                self._implement_centered(container, pane, config)
            elif layout_type == LayoutType.LEFT_SIDEBAR:
                self._implement_left_sidebar(container, pane, config)
            elif layout_type == LayoutType.RIGHT_SIDEBAR:
                self._implement_right_sidebar(container, pane, config)
            elif layout_type == LayoutType.CUSTOM_POSITION:
                self._implement_custom_position(container, pane, config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to implement single pane layout: {e}")
            return False
    
    def implement_dual_pane_layout(
            self, container: QWidget, panes: List[QWidget],
            layout_type: LayoutType, config: LayoutConfiguration
    ) -> bool:
        """Implement dual pane layout configurations."""
        if len(panes) != 2:
            return False
        
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import QSplitter

            # Clear existing layout
            self._clear_container_layout(container)
            
            if layout_type == LayoutType.HORIZONTAL_SPLIT:
                splitter = QSplitter(Qt.Horizontal, container)
            else:  # VERTICAL_SPLIT
                splitter = QSplitter(Qt.Vertical, container)
            
            # Add panes to splitter
            for pane in panes:
                splitter.addWidget(pane)
            
            # Set equal sizes
            splitter.setSizes([50, 50])
            
            # Apply margins and spacing
            self._apply_container_layout(container, [splitter], config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to implement dual pane layout: {e}")
            return False
    
    def implement_multi_pane_layout(
            self, container: QWidget, panes: List[QWidget],
            layout_type: LayoutType, config: LayoutConfiguration
    ) -> bool:
        """Implement multi-pane layout configurations."""
        if len(panes) < 3:
            return False
        
        try:
            if layout_type == LayoutType.HORIZONTAL_ROW:
                return self._implement_horizontal_row(container, panes, config)
            elif layout_type == LayoutType.VERTICAL_COLUMN:
                return self._implement_vertical_column(container, panes, config)
            elif layout_type == LayoutType.GRID_2X2:
                return self._implement_grid_2x2(container, panes, config)
            elif layout_type == LayoutType.GRID_2X3:
                return self._implement_grid_2x3(container, panes, config)
            elif layout_type == LayoutType.ADAPTIVE_GRID:
                return self._implement_adaptive_grid(container, panes, config)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to implement multi-pane layout: {e}")
            return False
    
    def _implement_full_width(self, container: QWidget, pane: QWidget,
                             config: LayoutConfiguration):
        """Implement full width single pane layout."""
        from PyQt5.QtWidgets import QHBoxLayout
        
        self._clear_container_layout(container)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        layout.addWidget(pane)
    
    def _implement_centered(self, container: QWidget, pane: QWidget,
                           config: LayoutConfiguration):
        """Implement centered single pane layout."""
        from PyQt5.QtWidgets import QHBoxLayout
        
        self._clear_container_layout(container)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        layout.addStretch()
        layout.addWidget(pane)
        layout.addStretch()
    
    def _implement_left_sidebar(self, container: QWidget, pane: QWidget,
                               config: LayoutConfiguration):
        """Implement left sidebar single pane layout."""
        from PyQt5.QtWidgets import QHBoxLayout
        
        self._clear_container_layout(container)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        layout.addWidget(pane, stretch=1)
        layout.addStretch(stretch=2)
    
    def _implement_right_sidebar(self, container: QWidget, pane: QWidget,
                                config: LayoutConfiguration):
        """Implement right sidebar single pane layout."""
        from PyQt5.QtWidgets import QHBoxLayout
        
        self._clear_container_layout(container)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        layout.addStretch(stretch=2)
        layout.addWidget(pane, stretch=1)
    
    def _implement_custom_position(self, container: QWidget, pane: QWidget,
                                  config: LayoutConfiguration):
        """Implement custom position single pane layout."""
        # For custom positioning, we don't use a layout
        # The pane can be freely positioned and resized
        self._clear_container_layout(container)
        pane.setParent(container)
        # Position would be set by user interaction
    
    def _implement_horizontal_row(self, container: QWidget, panes: List[QWidget],
                                 config: LayoutConfiguration) -> bool:
        """Implement horizontal row multi-pane layout."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QSplitter
        
        self._clear_container_layout(container)
        splitter = QSplitter(Qt.Horizontal, container)
        
        for pane in panes:
            splitter.addWidget(pane)
        
        # Set equal sizes
        equal_size = 100 // len(panes)
        splitter.setSizes([equal_size] * len(panes))
        
        self._apply_container_layout(container, [splitter], config)
        return True
    
    def _implement_vertical_column(self, container: QWidget, panes: List[QWidget],
                                  config: LayoutConfiguration) -> bool:
        """Implement vertical column multi-pane layout."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QSplitter
        
        self._clear_container_layout(container)
        splitter = QSplitter(Qt.Vertical, container)
        
        for pane in panes:
            splitter.addWidget(pane)
        
        # Set equal sizes
        equal_size = 100 // len(panes)
        splitter.setSizes([equal_size] * len(panes))
        
        self._apply_container_layout(container, [splitter], config)
        return True
    
    def _implement_grid_2x2(self, container: QWidget, panes: List[QWidget],
                           config: LayoutConfiguration) -> bool:
        """Implement 2x2 grid layout for exactly 4 panes."""
        if len(panes) != 4:
            return False
        
        from PyQt5.QtWidgets import QGridLayout
        
        self._clear_container_layout(container)
        layout = QGridLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        
        # Arrange panes in 2x2 grid
        layout.addWidget(panes[0], 0, 0)  # Top-left
        layout.addWidget(panes[1], 0, 1)  # Top-right
        layout.addWidget(panes[2], 1, 0)  # Bottom-left
        layout.addWidget(panes[3], 1, 1)  # Bottom-right
        
        return True
    
    def _implement_grid_2x3(self, container: QWidget, panes: List[QWidget],
                           config: LayoutConfiguration) -> bool:
        """Implement 2x3 grid layout."""
        from PyQt5.QtWidgets import QGridLayout
        
        self._clear_container_layout(container)
        layout = QGridLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        
        # Arrange panes in 2x3 grid
        for i, pane in enumerate(panes):
            row = i // 3
            col = i % 3
            layout.addWidget(pane, row, col)
        
        return True
    
    def _implement_adaptive_grid(self, container: QWidget, panes: List[QWidget],
                                config: LayoutConfiguration) -> bool:
        """Implement adaptive grid layout based on pane count."""
        from PyQt5.QtWidgets import QGridLayout
        
        pane_count = len(panes)
        
        # Calculate optimal grid dimensions
        if pane_count == 3:
            rows, cols = 2, 2  # 3 panes in 2x2 grid (one empty)
        elif pane_count == 4:
            rows, cols = 2, 2  # 4 panes in 2x2 grid
        else:
            # Fallback to horizontal row
            return self._implement_horizontal_row(container, panes, config)
        
        self._clear_container_layout(container)
        layout = QGridLayout(container)
        layout.setContentsMargins(*config.margins)
        layout.setSpacing(config.spacing)
        
        # Arrange panes in calculated grid
        for i, pane in enumerate(panes):
            row = i // cols
            col = i % cols
            layout.addWidget(pane, row, col)
        
        return True
    
    def _clear_container_layout(self, container: QWidget):
        """Clear existing layout from container."""
        try:
            if container.layout():
                # Remove all widgets from layout
                layout = container.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                
                # Delete the layout
                layout.deleteLater()
        except Exception as e:
            self.logger.warning(f"Error clearing container layout: {e}")
    
    def _apply_container_layout(self, container: QWidget, widgets: List[QWidget],
                               config: LayoutConfiguration):
        """Apply layout to container with configuration."""
        from PyQt5.QtWidgets import QVBoxLayout
        
        try:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(*config.margins)
            layout.setSpacing(config.spacing)
            
            for widget in widgets:
                layout.addWidget(widget)
                
        except Exception as e:
            self.logger.error(f"Error applying container layout: {e}")


class ContentHierarchyManager:
    """
    Manages content hierarchy preservation during layout transitions.
    
    Ensures that content organization and user context is maintained
    when switching between different layout configurations.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.content_snapshots: Dict[str, Dict[str, Any]] = {}
        self.hierarchy_enabled: bool = True
    
    def capture_content_hierarchy(
            self, panes: List[QWidget], layout_type: LayoutType
    ) -> str:
        """
        Capture current content hierarchy state.
        
        Returns:
            Snapshot ID for later restoration
        """
        if not self.hierarchy_enabled:
            return ""
        
        try:
            snapshot_id = f"{layout_type.value}_{len(panes)}_{id(panes[0])}"
            
            snapshot = {
                'pane_count': len(panes),
                'layout_type': layout_type.value,
                'pane_states': []
            }
            
            for i, pane in enumerate(panes):
                pane_state = {
                    'index': i,
                    'visible': pane.isVisible() if pane else False,
                    'geometry': pane.geometry() if pane else None,
                    'current_path': getattr(pane, '_current_path', None),
                    'selection_state': self._capture_selection_state(pane)
                }
                snapshot['pane_states'].append(pane_state)
            
            self.content_snapshots[snapshot_id] = snapshot
            
            self.logger.debug(f"Captured content hierarchy: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            self.logger.error(f"Error capturing content hierarchy: {e}")
            return ""
    
    def restore_content_hierarchy(
            self, snapshot_id: str, panes: List[QWidget],
            new_layout_type: LayoutType
    ) -> bool:
        """
        Restore content hierarchy from snapshot.
        
        Args:
            snapshot_id: ID of snapshot to restore
            panes: Current pane widgets
            new_layout_type: New layout being applied
            
        Returns:
            True if restoration was successful
        """
        if not self.hierarchy_enabled or not snapshot_id:
            return True
        
        try:
            if snapshot_id not in self.content_snapshots:
                self.logger.warning(f"Snapshot not found: {snapshot_id}")
                return False
            
            snapshot = self.content_snapshots[snapshot_id]
            pane_states = snapshot['pane_states']
            
            # Restore pane states based on new layout
            for i, pane in enumerate(panes):
                if i < len(pane_states):
                    old_state = pane_states[i]
                    self._restore_pane_state(pane, old_state, new_layout_type)
            
            self.logger.debug(f"Restored content hierarchy: {snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring content hierarchy: {e}")
            return False
    
    def _capture_selection_state(self, pane: QWidget) -> Dict[str, Any]:
        """Capture selection state from a pane."""
        try:
            if hasattr(pane, '_file_list'):
                file_list = pane._file_list
                selected_items = file_list.selectedItems()
                return {
                    'selected_count': len(selected_items),
                    'selected_files': [
                        item.text(0) for item in selected_items
                    ] if selected_items else []
                }
        except Exception:
            pass
        
        return {'selected_count': 0, 'selected_files': []}
    
    def _restore_pane_state(self, pane: QWidget, state: Dict[str, Any],
                           layout_type: LayoutType):
        """Restore state to a specific pane."""
        try:
            # Restore path if available
            if 'current_path' in state and state['current_path']:
                if hasattr(pane, 'set_path'):
                    pane.set_path(str(state['current_path']))
                elif hasattr(pane, '_current_path'):
                    pane._current_path = state['current_path']
            
            # Restore selection if possible
            if hasattr(pane, '_file_list') and 'selection_state' in state:
                selection_state = state['selection_state']
                selected_files = selection_state.get('selected_files', [])
                
                if selected_files:
                    file_list = pane._file_list
                    file_list.clearSelection()
                    
                    for selected_file in selected_files:
                        items = file_list.findItems(
                            selected_file, Qt.MatchExactly, 0
                        )
                        for item in items:
                            item.setSelected(True)
        
        except Exception as e:
            self.logger.warning(f"Error restoring pane state: {e}")
    
    def clear_snapshots(self):
        """Clear all content hierarchy snapshots."""
        self.content_snapshots.clear()
        self.logger.debug("Content hierarchy snapshots cleared")
    
    def enable_hierarchy_preservation(self, enabled: bool = True):
        """Enable or disable content hierarchy preservation."""
        self.hierarchy_enabled = enabled
        status = 'enabled' if enabled else 'disabled'
        self.logger.info(f"Content hierarchy preservation {status}")


class ResponsiveLayoutController:
    """
    High-level controller that integrates ResponsiveLayoutManager with
    the actual UI implementation and content hierarchy management.
    """
    
    def __init__(self, container_widget: QWidget):
        self.logger = logging.getLogger('RFU.ResponsiveLayoutController')
        self.container_widget = container_widget
        self.panes: List[QWidget] = []
        
        # Initialize components
        self.layout_manager = ResponsiveLayoutManager()
        self.layout_implementor = LayoutImplementor(self.logger)
        self.hierarchy_manager = ContentHierarchyManager(self.logger)
        
        # Connect signals
        self._connect_signals()
        
        self.logger.info("ResponsiveLayoutController initialized")
    
    def _connect_signals(self):
        """Connect signals between components."""
        self.layout_manager.layout_changed.connect(self._on_layout_changed)
        self.layout_manager.viewport_changed.connect(self._on_viewport_changed)
        self.layout_manager.transition_started.connect(
            self._on_transition_started
        )
        self.layout_manager.transition_completed.connect(
            self._on_transition_completed
        )
    
    def set_panes(self, panes: List[QWidget]):
        """Set the list of panes to be managed."""
        self.panes = panes
        self.layout_manager.set_pane_count(len(panes))
    
    def apply_layout(self, layout_type: LayoutType, animate: bool = True) -> bool:
        """Apply layout with full integration."""
        # Capture content hierarchy before transition
        snapshot_id = ""
        if animate and self.hierarchy_manager.hierarchy_enabled:
            snapshot_id = self.hierarchy_manager.capture_content_hierarchy(
                self.panes, self.layout_manager.current_layout or layout_type
            )
        
        # Apply the layout
        success = self.layout_manager.apply_layout(
            layout_type, self.container_widget, animate
        )
        
        if success:
            # Implement the actual layout
            config = self.layout_manager.layout_configs[layout_type]
            
            if len(self.panes) == 1:
                self.layout_implementor.implement_single_pane_layout(
                    self.container_widget, self.panes, layout_type, config
                )
            elif len(self.panes) == 2:
                self.layout_implementor.implement_dual_pane_layout(
                    self.container_widget, self.panes, layout_type, config
                )
            else:
                self.layout_implementor.implement_multi_pane_layout(
                    self.container_widget, self.panes, layout_type, config
                )
            
            # Restore content hierarchy
            if snapshot_id:
                self.hierarchy_manager.restore_content_hierarchy(
                    snapshot_id, self.panes, layout_type
                )
        
        return success
    
    def get_available_layouts(self) -> List[Tuple[LayoutType, str]]:
        """Get available layouts with display names."""
        return self.layout_manager.get_layout_display_names(len(self.panes))
    
    def _on_layout_changed(self, layout_type: LayoutType, info: Dict[str, Any]):
        """Handle layout change event."""
        self.logger.info(f"Layout changed to: {info['display_name']}")
    
    def _on_viewport_changed(self, viewport_type: ViewportType, size: Tuple[int, int]):
        """Handle viewport change event."""
        self.logger.info(f"Viewport changed: {viewport_type.value} {size}")
    
    def _on_transition_started(self, old_layout: LayoutType, new_layout: LayoutType):
        """Handle transition start event."""
        old_name = old_layout.value if old_layout else "None"
        self.logger.debug(f"Transition started: {old_name} -> {new_layout.value}")
    
    def _on_transition_completed(self, layout_type: LayoutType):
        """Handle transition completion event."""
        self.logger.debug(f"Transition completed: {layout_type.value}")