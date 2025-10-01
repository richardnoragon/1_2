#!/usr/bin/env python3
"""
Layout Manager for Multi-Pane File Explorer

Handles layout calculation, application, and responsive behavior
for multi-pane configurations with enterprise-grade reliability.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import logging
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtWidgets import QSplitter, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QObject = object


class LayoutMode(Enum):
    """Layout mode enumeration."""

    SINGLE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    GRID = auto()


class LayoutManager(QObject if QT_AVAILABLE else object):
    """
    Manager for pane layout and responsive behavior.

    Responsibilities:
    - Calculate optimal layouts for pane configurations
    - Apply layouts to container widgets
    - Handle responsive behavior and mobile adaptations
    - Manage layout transitions and animations
    """

    # Signals
    layoutChanged = pyqtSignal(str) if QT_AVAILABLE else None
    modeChanged = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, controller):
        """Initialize layout manager."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.LayoutManager")
        self.controller = controller

        # Layout state
        self.current_mode = LayoutMode.HORIZONTAL
        self.container_widget = None
        self.main_splitter = None

        # Responsive configuration
        self.mobile_threshold = (1024, 768)
        self.is_mobile_viewport = False
        self.grid_columns = {2: 2, 3: 2, 4: 2}

        # Available layouts by pane count
        self.available_layouts = {
            1: [LayoutMode.SINGLE],
            2: [LayoutMode.HORIZONTAL, LayoutMode.VERTICAL],
            3: [LayoutMode.HORIZONTAL, LayoutMode.VERTICAL, LayoutMode.GRID],
            4: [LayoutMode.HORIZONTAL, LayoutMode.VERTICAL, LayoutMode.GRID],
        }

        self.logger.info("Layout manager initialized")

    def setup(self, container: QWidget) -> bool:
        """
        Setup layout management for container.

        Args:
            container: Container widget for layouts

        Returns:
            bool: True if successful
        """
        try:
            self.container_widget = container

            # Create main splitter
            success = self._create_main_splitter()
            if not success:
                return False

            # Detect viewport characteristics
            self._detect_viewport()

            # Apply initial layout
            self._apply_layout()

            self.logger.info("Layout manager setup completed")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up layout manager: {e}")
            return False

    def _create_main_splitter(self) -> bool:
        """Create main splitter for pane layout."""
        try:
            if not QT_AVAILABLE:
                return True

            from PyQt5.QtWidgets import QHBoxLayout

            # Create layout in container
            layout = QHBoxLayout(self.container_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)

            # Create main splitter
            self.main_splitter = QSplitter(Qt.Horizontal)
            layout.addWidget(self.main_splitter)

            # Store reference in container for access
            self.container_widget._main_splitter = self.main_splitter

            self.logger.debug("Main splitter created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating main splitter: {e}")
            return False

    def _detect_viewport(self):
        """Detect viewport characteristics for responsive behavior."""
        try:
            if not QT_AVAILABLE:
                return

            from PyQt5.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    geometry = screen.geometry()
                    screen_size = (geometry.width(), geometry.height())

                    # Check mobile threshold
                    self.is_mobile_viewport = (
                        screen_size[0] < self.mobile_threshold[0]
                        or screen_size[1] < self.mobile_threshold[1]
                    )

                    # Adjust grid columns for smaller screens
                    if screen_size[0] < 800:
                        self.grid_columns = {2: 1, 3: 1, 4: 2}
                    elif screen_size[0] < 1200:
                        self.grid_columns = {2: 1, 3: 2, 4: 2}
                    else:
                        self.grid_columns = {2: 2, 3: 3, 4: 2}

                    msg = f"Detected viewport: {screen_size}, mobile: {self.is_mobile_viewport}"
                    self.logger.info(msg)

        except Exception as e:
            self.logger.warning(f"Error detecting viewport: {e}")
            self.is_mobile_viewport = False

    def set_mode(self, mode: str) -> bool:
        """
        Set layout mode.

        Args:
            mode: Layout mode string

        Returns:
            bool: True if successful
        """
        try:
            # Convert string to enum
            mode_map = {
                "single": LayoutMode.SINGLE,
                "horizontal": LayoutMode.HORIZONTAL,
                "vertical": LayoutMode.VERTICAL,
                "grid": LayoutMode.GRID,
            }

            if mode not in mode_map:
                self.logger.warning(f"Invalid layout mode: {mode}")
                return False

            new_mode = mode_map[mode]

            # Validate mode for current pane count
            pane_count = len(self.controller._pane_manager._panes)
            available = self.available_layouts.get(pane_count, [])

            if new_mode not in available:
                self.logger.warning(f"Mode {mode} not available for {pane_count} panes")
                return False

            old_mode = self.current_mode
            self.current_mode = new_mode

            # Apply new layout
            self._apply_layout()

            # Emit signals
            if self.modeChanged:
                self.modeChanged.emit(mode)
            if self.layoutChanged:
                self.layoutChanged.emit(f"{old_mode.name} -> {new_mode.name}")

            self.logger.info(f"Layout mode changed to {mode}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting layout mode: {e}")
            return False

    def _apply_layout(self):
        """Apply current layout mode to panes."""
        try:
            if not self.main_splitter:
                self.logger.warning("No main splitter available")
                return

            # Get panes from controller
            if not hasattr(self.controller, "_pane_manager"):
                return

            pane_manager = self.controller._pane_manager
            if not hasattr(pane_manager, "_panes"):
                return

            panes = list(pane_manager._panes.values())
            if not panes:
                return

            # Clear existing layout
            self._clear_splitter()

            # Apply layout based on mode
            if self.current_mode == LayoutMode.SINGLE:
                self._apply_single_layout(panes)
            elif self.current_mode == LayoutMode.HORIZONTAL:
                self._apply_horizontal_layout(panes)
            elif self.current_mode == LayoutMode.VERTICAL:
                self._apply_vertical_layout(panes)
            elif self.current_mode == LayoutMode.GRID:
                self._apply_grid_layout(panes)

            self.logger.debug(
                f"Applied {self.current_mode.name} layout to {len(panes)} panes"
            )

        except Exception as e:
            self.logger.error(f"Error applying layout: {e}")

    def _clear_splitter(self):
        """Clear all widgets from splitter."""
        try:
            if not self.main_splitter:
                return

            # Remove all widgets
            while self.main_splitter.count() > 0:
                widget = self.main_splitter.widget(0)
                if widget:
                    widget.setParent(None)

            self.logger.debug("Splitter cleared")

        except Exception as e:
            self.logger.error(f"Error clearing splitter: {e}")

    def _apply_single_layout(self, panes: List[QWidget]):
        """Apply single pane layout."""
        try:
            if panes and self.main_splitter:
                self.main_splitter.setOrientation(Qt.Horizontal)
                self.main_splitter.addWidget(panes[0])

        except Exception as e:
            self.logger.error(f"Error applying single layout: {e}")

    def _apply_horizontal_layout(self, panes: List[QWidget]):
        """Apply horizontal layout."""
        try:
            if not self.main_splitter:
                return

            self.main_splitter.setOrientation(Qt.Horizontal)

            for pane in panes:
                self.main_splitter.addWidget(pane)

            # Set equal sizes
            if panes:
                sizes = [100] * len(panes)
                self.main_splitter.setSizes(sizes)

        except Exception as e:
            self.logger.error(f"Error applying horizontal layout: {e}")

    def _apply_vertical_layout(self, panes: List[QWidget]):
        """Apply vertical layout."""
        try:
            if not self.main_splitter:
                return

            self.main_splitter.setOrientation(Qt.Vertical)

            for pane in panes:
                self.main_splitter.addWidget(pane)

            # Set equal sizes
            if panes:
                sizes = [100] * len(panes)
                self.main_splitter.setSizes(sizes)

        except Exception as e:
            self.logger.error(f"Error applying vertical layout: {e}")

    def _apply_grid_layout(self, panes: List[QWidget]):
        """Apply grid layout."""
        try:
            if not self.main_splitter or len(panes) < 3:
                # Fallback to horizontal for insufficient panes
                self._apply_horizontal_layout(panes)
                return

            # Calculate grid dimensions
            pane_count = len(panes)
            cols = self.grid_columns.get(pane_count, 2)
            rows = (pane_count + cols - 1) // cols  # Ceiling division

            self.main_splitter.setOrientation(Qt.Vertical)

            # Create row splitters
            for row in range(rows):
                row_splitter = QSplitter(Qt.Horizontal)

                # Add panes to this row
                start_idx = row * cols
                end_idx = min(start_idx + cols, pane_count)

                for pane_idx in range(start_idx, end_idx):
                    if pane_idx < len(panes):
                        row_splitter.addWidget(panes[pane_idx])

                self.main_splitter.addWidget(row_splitter)

                # Set equal column sizes
                if row_splitter.count() > 0:
                    col_sizes = [100] * row_splitter.count()
                    row_splitter.setSizes(col_sizes)

            # Set equal row sizes
            if self.main_splitter.count() > 0:
                row_sizes = [100] * self.main_splitter.count()
                self.main_splitter.setSizes(row_sizes)

        except Exception as e:
            self.logger.error(f"Error applying grid layout: {e}")
            # Fallback to horizontal
            self._apply_horizontal_layout(panes)

    def get_available_modes(self, pane_count: int) -> List[str]:
        """Get available layout modes for given pane count."""
        try:
            modes = self.available_layouts.get(pane_count, [])
            return [mode.name.lower() for mode in modes]
        except Exception as e:
            self.logger.error(f"Error getting available modes: {e}")
            return ["horizontal"]

    def is_mode_available(self, mode: str, pane_count: int) -> bool:
        """Check if layout mode is available for pane count."""
        try:
            available_modes = self.get_available_modes(pane_count)
            return mode.lower() in available_modes
        except Exception as e:
            self.logger.error(f"Error checking mode availability: {e}")
            return False

    def get_optimal_mode(self, pane_count: int) -> str:
        """Get optimal layout mode for pane count."""
        try:
            if pane_count == 1:
                return "single"
            elif pane_count == 2:
                return "horizontal"
            elif pane_count >= 3:
                return "grid" if not self.is_mobile_viewport else "vertical"
            else:
                return "horizontal"
        except Exception as e:
            self.logger.error(f"Error getting optimal mode: {e}")
            return "horizontal"

    def calculate_layout_metrics(self) -> Dict[str, Any]:
        """Calculate layout metrics and efficiency."""
        try:
            if not self.main_splitter:
                return {}

            splitter_count = self.main_splitter.count()
            splitter_sizes = self.main_splitter.sizes()

            return {
                "mode": self.current_mode.name,
                "pane_count": splitter_count,
                "sizes": splitter_sizes,
                "is_mobile": self.is_mobile_viewport,
                "efficiency": self._calculate_space_efficiency(splitter_sizes),
            }

        except Exception as e:
            self.logger.error(f"Error calculating layout metrics: {e}")
            return {}

    def _calculate_space_efficiency(self, sizes: List[int]) -> float:
        """Calculate space utilization efficiency."""
        try:
            if not sizes:
                return 0.0

            total_space = sum(sizes)
            if total_space == 0:
                return 0.0

            # Calculate variance in pane sizes
            avg_size = total_space / len(sizes)
            variance = sum((size - avg_size) ** 2 for size in sizes) / len(sizes)

            # Lower variance = higher efficiency
            efficiency = max(0.0, 1.0 - (variance / (avg_size**2)))
            return efficiency

        except Exception as e:
            self.logger.error(f"Error calculating space efficiency: {e}")
            return 0.0

    def optimize_layout_for_content(self, pane_metrics: Dict[str, Any]) -> bool:
        """
        Optimize layout based on pane content metrics.

        Args:
            pane_metrics: Metrics about pane content and usage

        Returns:
            bool: True if optimization was applied
        """
        try:
            if not self.main_splitter or not pane_metrics:
                return False

            # Calculate optimal sizes based on content
            optimal_sizes = self._calculate_optimal_sizes(pane_metrics)

            if optimal_sizes:
                self.main_splitter.setSizes(optimal_sizes)
                self.logger.info("Layout optimized for content")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error optimizing layout: {e}")
            return False

    def _calculate_optimal_sizes(self, metrics: Dict[str, Any]) -> List[int]:
        """Calculate optimal pane sizes based on metrics."""
        try:
            # Simple implementation - equal sizes with content-based adjustments
            pane_count = self.main_splitter.count() if self.main_splitter else 0
            if pane_count == 0:
                return []

            base_size = 100
            sizes = [base_size] * pane_count

            # Apply content-based adjustments (placeholder for future enhancement)
            # This could be enhanced to consider file counts, types, etc.

            return sizes

        except Exception as e:
            self.logger.error(f"Error calculating optimal sizes: {e}")
            return []

    def handle_resize(self, new_size: Tuple[int, int]):
        """Handle container resize for responsive behavior."""
        try:
            old_mobile = self.is_mobile_viewport

            # Re-detect viewport
            self.is_mobile_viewport = (
                new_size[0] < self.mobile_threshold[0]
                or new_size[1] < self.mobile_threshold[1]
            )

            # If viewport type changed, update layout
            if old_mobile != self.is_mobile_viewport:
                self.logger.info(f"Viewport changed: mobile={self.is_mobile_viewport}")
                self._apply_mobile_adaptations()
                self._apply_layout()

        except Exception as e:
            self.logger.error(f"Error handling resize: {e}")

    def _apply_mobile_adaptations(self):
        """Apply mobile-specific layout adaptations."""
        try:
            if not self.is_mobile_viewport:
                return

            # Force vertical layout for mobile with > 2 panes
            pane_count = len(self.controller._pane_manager._panes)
            if pane_count > 2 and self.current_mode == LayoutMode.HORIZONTAL:
                self.current_mode = LayoutMode.VERTICAL
                self.logger.info("Switched to vertical layout for mobile")

        except Exception as e:
            self.logger.warning(f"Mobile adaptation failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get layout manager status."""
        try:
            splitter_info = {}
            if self.main_splitter:
                splitter_info = {
                    "count": self.main_splitter.count(),
                    "sizes": self.main_splitter.sizes(),
                    "orientation": (
                        "Horizontal"
                        if self.main_splitter.orientation() == Qt.Horizontal
                        else "Vertical"
                    ),
                }

            return {
                "current_mode": self.current_mode.name,
                "is_mobile_viewport": self.is_mobile_viewport,
                "mobile_threshold": self.mobile_threshold,
                "grid_columns": self.grid_columns,
                "splitter_info": splitter_info,
                "available_layouts": {
                    count: [mode.name for mode in modes]
                    for count, modes in self.available_layouts.items()
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting layout status: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """Clean up layout manager."""
        try:
            self.logger.info("Cleaning up layout manager")

            if self.main_splitter:
                self._clear_splitter()
                self.main_splitter = None

            self.container_widget = None
            self.current_mode = LayoutMode.HORIZONTAL

            self.logger.info("Layout manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during layout manager cleanup: {e}")
