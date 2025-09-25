"""
from PyQt5.QtCore import Qt
import os

Concrete Layout Implementations for Responsive Layout System

This module provides concrete implementations for all layout types,
handling the actual Qt widget arrangements and positioning.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .responsive_layout_manager import LayoutConfiguration, LayoutType


class SinglePaneLayoutImplementor:
    """Implements single pane layouts with unrestricted flexibility."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def implement_full_width(
        self, container: QWidget, pane: QWidget, config: LayoutConfiguration
    ) -> bool:
        """Full width single pane implementation."""
        try:
            self._clear_container(container)

            # Use horizontal layout for full width
            layout = QHBoxLayout(container)
            layout.setContentsMargins(*config.margins)
            layout.setSpacing(config.spacing)
            layout.addWidget(pane)

            self.logger.debug("Applied full width layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement full width layout: {e}")
            return False

    def implement_centered(
        self, container: QWidget, pane: QWidget, config: LayoutConfiguration
    ) -> bool:
        """Centered single pane implementation."""
        try:
            self._clear_container(container)

            # Use horizontal layout with stretches for centering
            layout = QHBoxLayout(container)
            layout.setContentsMargins(*config.margins)
            layout.setSpacing(config.spacing)

            # Add stretches on both sides for centering
            layout.addStretch(1)
            layout.addWidget(pane, 2)  # Give pane more weight
            layout.addStretch(1)

            self.logger.debug("Applied centered layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement centered layout: {e}")
            return False

    def implement_sidebar(
        self,
        container: QWidget,
        pane: QWidget,
        config: LayoutConfiguration,
        side: str = "left",
    ) -> bool:
        """Sidebar implementation (left or right)."""
        try:
            self._clear_container(container)

            layout = QHBoxLayout(container)
            layout.setContentsMargins(*config.margins)
            layout.setSpacing(config.spacing)

            if side == "left":
                # Pane on left, stretch on right
                layout.addWidget(pane, 1)
                layout.addStretch(2)
            else:
                # Stretch on left, pane on right
                layout.addStretch(2)
                layout.addWidget(pane, 1)

            self.logger.debug(f"Applied {side} sidebar layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement {side} sidebar: {e}")
            return False

    def implement_custom_position(
        self, container: QWidget, pane: QWidget, config: LayoutConfiguration
    ) -> bool:
        """Custom position implementation with free positioning."""
        try:
            self._clear_container(container)

            # Remove any layout to allow free positioning
            if container.layout():
                container.layout().deleteLater()

            # Set pane as child and allow manual positioning
            pane.setParent(container)
            pane.setGeometry(50, 50, 400, 300)  # Default position
            pane.show()

            # Enable drag and resize capabilities
            self._enable_custom_positioning(pane)

            self.logger.debug("Applied custom position layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement custom position: {e}")
            return False

    def _enable_custom_positioning(self, pane: QWidget):
        """Enable drag and resize for custom positioned panes."""
        # This would enable drag and resize functionality
        # For now, just ensure the pane is movable
        try:
            pane.setAttribute(Qt.WA_Hover, True)
            # Additional custom positioning logic would go here
        except Exception as e:
            self.logger.warning(f"Could not enable custom positioning: {e}")

    def _clear_container(self, container: QWidget):
        """Clear container layout and widgets."""
        try:
            if container.layout():
                layout = container.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                layout.deleteLater()
        except Exception as e:
            self.logger.warning(f"Error clearing container: {e}")


class DualPaneLayoutImplementor:
    """Implements dual pane layouts with horizontal/vertical optimization."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def implement_horizontal_split(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
    ) -> bool:
        """Horizontal split implementation for dual panes."""
        if len(panes) != 2:
            return False

        try:
            self._clear_container(container)

            # Create horizontal splitter
            if hasattr(container, "addWidget"):
                # Container is already a splitter
                container.setOrientation(Qt.Horizontal)
                self._add_panes_to_splitter(container, panes)
            else:
                # Container needs a splitter layout
                splitter = QSplitter(Qt.Horizontal, container)
                self._add_panes_to_splitter(splitter, panes)

                # Add splitter to container
                layout = QVBoxLayout(container)
                layout.setContentsMargins(*config.margins)
                layout.addWidget(splitter)

            # Set equal split
            self._set_equal_sizes(container, len(panes))

            self.logger.debug("Applied horizontal split layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement horizontal split: {e}")
            return False

    def implement_vertical_split(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
    ) -> bool:
        """Vertical split implementation for dual panes."""
        if len(panes) != 2:
            return False

        try:
            self._clear_container(container)

            # Create vertical splitter
            if hasattr(container, "addWidget"):
                # Container is already a splitter
                container.setOrientation(Qt.Vertical)
                self._add_panes_to_splitter(container, panes)
            else:
                # Container needs a splitter layout
                splitter = QSplitter(Qt.Vertical, container)
                self._add_panes_to_splitter(splitter, panes)

                # Add splitter to container
                layout = QVBoxLayout(container)
                layout.setContentsMargins(*config.margins)
                layout.addWidget(splitter)

            # Set equal split
            self._set_equal_sizes(container, len(panes))

            self.logger.debug("Applied vertical split layout")
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement vertical split: {e}")
            return False

    def _add_panes_to_splitter(self, splitter, panes: List[QWidget]):
        """Add panes to splitter widget."""
        for pane in panes:
            if hasattr(splitter, "addWidget"):
                splitter.addWidget(pane)

    def _set_equal_sizes(self, container, pane_count: int):
        """Set equal sizes for splitter."""
        try:
            if hasattr(container, "setSizes"):
                equal_size = 100 // pane_count
                sizes = [equal_size] * pane_count
                container.setSizes(sizes)
        except Exception as e:
            self.logger.warning(f"Could not set equal sizes: {e}")

    def _clear_container(self, container: QWidget):
        """Clear container for new layout."""
        try:
            if hasattr(container, "count") and hasattr(container, "widget"):
                # Splitter container
                for i in reversed(range(container.count())):
                    widget = container.widget(i)
                    if widget:
                        widget.setParent(None)
            elif container.layout():
                # Widget with layout
                layout = container.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                layout.deleteLater()
        except Exception as e:
            self.logger.warning(f"Error clearing container: {e}")


class MultiPaneLayoutImplementor:
    """Implements multi-pane layouts with comprehensive grid and row options."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def implement_horizontal_row(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
    ) -> bool:
        """Horizontal row implementation for 3+ panes."""
        try:
            self._clear_container(container)

            # Create horizontal splitter for row arrangement
            if hasattr(container, "addWidget"):
                container.setOrientation(Qt.Horizontal)
                splitter = container
            else:
                splitter = QSplitter(Qt.Horizontal, container)
                layout = QVBoxLayout(container)
                layout.setContentsMargins(*config.margins)
                layout.addWidget(splitter)

            # Add all panes horizontally
            for pane in panes:
                splitter.addWidget(pane)

            # Set equal sizes
            equal_size = 100 // len(panes)
            sizes = [equal_size] * len(panes)
            splitter.setSizes(sizes)

            self.logger.debug(
                f"Applied horizontal row layout for {len(panes)} panes"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement horizontal row: {e}")
            return False

    def implement_vertical_column(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
    ) -> bool:
        """Vertical column implementation for 3+ panes."""
        try:
            self._clear_container(container)

            # Create vertical splitter for column arrangement
            if hasattr(container, "addWidget"):
                container.setOrientation(Qt.Vertical)
                splitter = container
            else:
                splitter = QSplitter(Qt.Vertical, container)
                layout = QVBoxLayout(container)
                layout.setContentsMargins(*config.margins)
                layout.addWidget(splitter)

            # Add all panes vertically
            for pane in panes:
                splitter.addWidget(pane)

            # Set equal sizes
            equal_size = 100 // len(panes)
            sizes = [equal_size] * len(panes)
            splitter.setSizes(sizes)

            self.logger.debug(
                f"Applied vertical column layout for {len(panes)} panes"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement vertical column: {e}")
            return False

    def implement_grid_layout(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
        rows: int,
        cols: int,
    ) -> bool:
        """Generic grid layout implementation."""
        try:
            self._clear_container(container)

            # Create grid layout
            grid_layout = QGridLayout(container)
            grid_layout.setContentsMargins(*config.margins)
            grid_layout.setSpacing(config.spacing)

            # Add panes to grid
            for i, pane in enumerate(panes):
                row = i // cols
                col = i % cols

                if row < rows and col < cols:
                    grid_layout.addWidget(pane, row, col)
                else:
                    # Extra panes, add to last available position
                    grid_layout.addWidget(pane, rows - 1, cols - 1)

            # Set equal row and column stretches
            for row in range(rows):
                grid_layout.setRowStretch(row, 1)
            for col in range(cols):
                grid_layout.setColumnStretch(col, 1)

            self.logger.debug(
                f"Applied {rows}×{cols} grid layout for {len(panes)} panes"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to implement grid layout: {e}")
            return False

    def implement_adaptive_grid(
        self,
        container: QWidget,
        panes: List[QWidget],
        config: LayoutConfiguration,
        viewport_width: int,
    ) -> bool:
        """Adaptive grid implementation based on pane count and viewport."""
        try:
            pane_count = len(panes)

            # Calculate optimal grid dimensions based on viewport and pane count
            if viewport_width < 800:
                # Narrow viewport - prefer vertical arrangement
                if pane_count <= 2:
                    rows, cols = 2, 1
                elif pane_count == 3:
                    rows, cols = 3, 1
                else:  # 4 panes
                    rows, cols = 2, 2
            elif viewport_width < 1200:
                # Medium viewport - balanced arrangement
                if pane_count <= 2:
                    rows, cols = 1, 2
                elif pane_count == 3:
                    rows, cols = 2, 2  # 3 panes in 2×2 (one empty)
                else:  # 4 panes
                    rows, cols = 2, 2
            else:
                # Wide viewport - prefer horizontal arrangement
                if pane_count <= 2:
                    rows, cols = 1, 2
                elif pane_count == 3:
                    rows, cols = 1, 3
                else:  # 4 panes
                    rows, cols = 2, 2

            return self.implement_grid_layout(
                container, panes, config, rows, cols
            )

        except Exception as e:
            self.logger.error(f"Failed to implement adaptive grid: {e}")
            return False

    def _clear_container(self, container: QWidget):
        """Clear container for new layout."""
        try:
            if hasattr(container, "count") and hasattr(container, "widget"):
                # Splitter container
                for i in reversed(range(container.count())):
                    widget = container.widget(i)
                    if widget:
                        widget.setParent(None)
            elif container.layout():
                # Widget with layout
                layout = container.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                layout.deleteLater()
        except Exception as e:
            self.logger.warning(f"Error clearing container: {e}")


class LayoutTransitionManager:
    """Manages smooth transitions between different layout arrangements."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.active_animations: List[QPropertyAnimation] = []
        self.transition_duration = 300  # milliseconds

    def create_smooth_transition(
        self,
        panes: List[QWidget],
        from_layout: LayoutType,
        to_layout: LayoutType,
        container: QWidget,
    ) -> bool:
        """Create smooth animated transition between layouts."""
        try:
            # Capture current positions
            current_positions = self._capture_pane_positions(panes)

            # Calculate target positions for new layout
            target_positions = self._calculate_target_positions(
                panes, to_layout, container
            )

            # Create animations for each pane
            animations = []
            for i, pane in enumerate(panes):
                if i < len(target_positions):
                    animation = self._create_position_animation(
                        pane, current_positions[i], target_positions[i]
                    )
                    if animation:
                        animations.append(animation)

            # Start all animations
            for animation in animations:
                animation.start()

            self.active_animations.extend(animations)

            self.logger.debug(
                f"Created transition from {from_layout.value} to {to_layout.value}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to create smooth transition: {e}")
            return False

    def _capture_pane_positions(self, panes: List[QWidget]) -> List[QRect]:
        """Capture current positions of all panes."""
        positions = []
        for pane in panes:
            try:
                positions.append(pane.geometry())
            except Exception:
                positions.append(QRect(0, 0, 100, 100))  # Default
        return positions

    def _calculate_target_positions(
        self, panes: List[QWidget], layout_type: LayoutType, container: QWidget
    ) -> List[QRect]:
        """Calculate target positions for new layout."""
        target_positions = []
        container_rect = container.geometry()

        try:
            if layout_type == LayoutType.HORIZONTAL_SPLIT and len(panes) == 2:
                # Two panes side by side
                width = container_rect.width() // 2
                height = container_rect.height()

                target_positions.append(QRect(0, 0, width, height))
                target_positions.append(QRect(width, 0, width, height))

            elif layout_type == LayoutType.VERTICAL_SPLIT and len(panes) == 2:
                # Two panes stacked
                width = container_rect.width()
                height = container_rect.height() // 2

                target_positions.append(QRect(0, 0, width, height))
                target_positions.append(QRect(0, height, width, height))

            elif layout_type == LayoutType.GRID_2X2 and len(panes) == 4:
                # 2×2 grid
                width = container_rect.width() // 2
                height = container_rect.height() // 2

                target_positions.append(QRect(0, 0, width, height))  # Top-left
                target_positions.append(
                    QRect(width, 0, width, height)
                )  # Top-right
                target_positions.append(
                    QRect(0, height, width, height)
                )  # Bottom-left
                target_positions.append(
                    QRect(width, height, width, height)
                )  # Bottom-right

            else:
                # Fallback to equal distribution
                width = container_rect.width() // len(panes)
                height = container_rect.height()

                for i in range(len(panes)):
                    x = i * width
                    target_positions.append(QRect(x, 0, width, height))

        except Exception as e:
            self.logger.error(f"Error calculating target positions: {e}")
            # Fallback to current positions
            return self._capture_pane_positions(panes)

        return target_positions

    def _create_position_animation(
        self, pane: QWidget, from_rect: QRect, to_rect: QRect
    ) -> Optional[QPropertyAnimation]:
        """Create position animation for a single pane."""
        try:
            animation = QPropertyAnimation(pane, b"geometry")
            animation.setDuration(self.transition_duration)
            animation.setStartValue(from_rect)
            animation.setEndValue(to_rect)
            animation.setEasingCurve(QEasingCurve.OutCubic)

            return animation

        except Exception as e:
            self.logger.error(f"Failed to create position animation: {e}")
            return None

    def stop_all_animations(self):
        """Stop all active animations."""
        for animation in self.active_animations:
            try:
                if animation.state() == QPropertyAnimation.Running:
                    animation.stop()
            except Exception:
                pass

        self.active_animations.clear()
        self.logger.debug("Stopped all layout animations")


class ResponsiveBreakpointHandler:
    """Handles responsive breakpoint detection and adaptation."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.breakpoints = {
            "mobile": (0, 767),
            "tablet": (768, 1023),
            "desktop": (1024, 1439),
            "large_desktop": (1440, 9999),
        }
        self.grid_configurations = {
            "mobile": {2: (2, 1), 3: (3, 1), 4: (2, 2)},
            "tablet": {2: (1, 2), 3: (2, 2), 4: (2, 2)},
            "desktop": {2: (1, 2), 3: (1, 3), 4: (2, 2)},
            "large_desktop": {2: (1, 2), 3: (1, 3), 4: (1, 4)},
        }

    def detect_breakpoint(self, width: int, height: int) -> str:
        """Detect current responsive breakpoint."""
        for breakpoint, (min_w, max_w) in self.breakpoints.items():
            if min_w <= width <= max_w:
                return breakpoint
        return "desktop"

    def get_optimal_grid_configuration(
        self, pane_count: int, breakpoint: str
    ) -> Tuple[int, int]:
        """Get optimal grid configuration for breakpoint and pane count."""
        configs = self.grid_configurations.get(breakpoint, {})
        return configs.get(pane_count, (2, 2))  # Default to 2×2

    def should_force_layout_change(
        self, current_layout: LayoutType, pane_count: int, breakpoint: str
    ) -> Optional[LayoutType]:
        """Determine if layout should be forced due to breakpoint constraints."""

        # Mobile-specific constraints
        if breakpoint == "mobile":
            if (
                current_layout == LayoutType.HORIZONTAL_SPLIT
                and pane_count == 2
            ):
                return LayoutType.VERTICAL_SPLIT
            elif (
                current_layout in [LayoutType.GRID_2X2, LayoutType.GRID_2X3]
                and pane_count > 2
            ):
                return LayoutType.VERTICAL_COLUMN

        # Tablet-specific constraints
        elif breakpoint == "tablet":
            if current_layout == LayoutType.HORIZONTAL_ROW and pane_count > 3:
                return LayoutType.ADAPTIVE_GRID

        return None

    def get_responsive_layout_recommendations(
        self, pane_count: int, breakpoint: str
    ) -> List[LayoutType]:
        """Get layout recommendations for specific breakpoint."""
        recommendations = []

        if pane_count == 1:
            if breakpoint in ["mobile", "tablet"]:
                recommendations = [LayoutType.FULL_WIDTH, LayoutType.CENTERED]
            else:
                recommendations = [
                    LayoutType.FULL_WIDTH,
                    LayoutType.CENTERED,
                    LayoutType.LEFT_SIDEBAR,
                    LayoutType.RIGHT_SIDEBAR,
                    LayoutType.CUSTOM_POSITION,
                ]

        elif pane_count == 2:
            if breakpoint == "mobile":
                recommendations = [LayoutType.VERTICAL_SPLIT]
            else:
                recommendations = [
                    LayoutType.HORIZONTAL_SPLIT,
                    LayoutType.VERTICAL_SPLIT,
                ]

        else:  # 3+ panes
            if breakpoint == "mobile":
                recommendations = [LayoutType.VERTICAL_COLUMN]
            elif breakpoint == "tablet":
                recommendations = [
                    LayoutType.ADAPTIVE_GRID,
                    LayoutType.VERTICAL_COLUMN,
                ]
            else:
                recommendations = [
                    LayoutType.HORIZONTAL_ROW,
                    LayoutType.VERTICAL_COLUMN,
                    LayoutType.GRID_2X2,
                    LayoutType.ADAPTIVE_GRID,
                ]

        return recommendations


class ContentHierarchyPreserver:
    """Preserves content hierarchy and user context during layout transitions."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.snapshots: Dict[str, Dict] = {}

    def capture_hierarchy_state(
        self, panes: List[QWidget], layout_id: str
    ) -> str:
        """Capture current hierarchy state before transition."""
        try:
            snapshot = {
                "layout_id": layout_id,
                "pane_count": len(panes),
                "pane_states": [],
            }

            for i, pane in enumerate(panes):
                pane_state = {
                    "index": i,
                    "visible": pane.isVisible() if pane else False,
                    "current_path": getattr(pane, "_current_path", None),
                    "selection": self._capture_selection_state(pane),
                    "scroll_position": self._capture_scroll_position(pane),
                }
                snapshot["pane_states"].append(pane_state)

            snapshot_id = f"hierarchy_{layout_id}_{len(panes)}_{id(panes[0])}"
            self.snapshots[snapshot_id] = snapshot

            self.logger.debug(f"Captured hierarchy state: {snapshot_id}")
            return snapshot_id

        except Exception as e:
            self.logger.error(f"Failed to capture hierarchy state: {e}")
            return ""

    def restore_hierarchy_state(
        self, snapshot_id: str, panes: List[QWidget]
    ) -> bool:
        """Restore hierarchy state after transition."""
        try:
            if snapshot_id not in self.snapshots:
                return False

            snapshot = self.snapshots[snapshot_id]
            pane_states = snapshot["pane_states"]

            for i, pane in enumerate(panes):
                if i < len(pane_states):
                    state = pane_states[i]
                    self._restore_pane_state(pane, state)

            # Clean up snapshot
            del self.snapshots[snapshot_id]

            self.logger.debug(f"Restored hierarchy state: {snapshot_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restore hierarchy state: {e}")
            return False

    def _capture_selection_state(self, pane: QWidget) -> Dict:
        """Capture selection state from pane."""
        try:
            if hasattr(pane, "_file_list"):
                file_list = pane._file_list
                selected_items = file_list.selectedItems()
                return {
                    "selected_files": [
                        item.text(0) for item in selected_items
                    ],
                    "current_item": (
                        file_list.currentItem().text(0)
                        if file_list.currentItem()
                        else None
                    ),
                }
        except Exception:
            pass

        return {"selected_files": [], "current_item": None}

    def _capture_scroll_position(self, pane: QWidget) -> Dict:
        """Capture scroll position from pane."""
        try:
            if hasattr(pane, "_file_list"):
                file_list = pane._file_list
                v_scrollbar = file_list.verticalScrollBar()
                h_scrollbar = file_list.horizontalScrollBar()

                return {
                    "v_scroll": v_scrollbar.value() if v_scrollbar else 0,
                    "h_scroll": h_scrollbar.value() if h_scrollbar else 0,
                }
        except Exception:
            pass

        return {"v_scroll": 0, "h_scroll": 0}

    def _restore_pane_state(self, pane: QWidget, state: Dict):
        """Restore state to a specific pane."""
        try:
            # Restore path
            if "current_path" in state and state["current_path"]:
                if hasattr(pane, "set_path"):
                    pane.set_path(str(state["current_path"]))
                elif hasattr(pane, "_current_path"):
                    pane._current_path = state["current_path"]

            # Restore selection
            if hasattr(pane, "_file_list") and "selection" in state:
                file_list = pane._file_list
                selection = state["selection"]

                # Clear current selection
                file_list.clearSelection()

                # Restore selected files
                for filename in selection.get("selected_files", []):
                    items = file_list.findItems(filename, Qt.MatchExactly, 0)
                    for item in items:
                        item.setSelected(True)

                # Restore current item
                current_item = selection.get("current_item")
                if current_item:
                    items = file_list.findItems(
                        current_item, Qt.MatchExactly, 0
                    )
                    if items:
                        file_list.setCurrentItem(items[0])

            # Restore scroll position
            if hasattr(pane, "_file_list") and "scroll_position" in state:
                file_list = pane._file_list
                scroll_pos = state["scroll_position"]

                v_scrollbar = file_list.verticalScrollBar()
                h_scrollbar = file_list.horizontalScrollBar()

                if v_scrollbar:
                    v_scrollbar.setValue(scroll_pos.get("v_scroll", 0))
                if h_scrollbar:
                    h_scrollbar.setValue(scroll_pos.get("h_scroll", 0))

        except Exception as e:
            self.logger.warning(f"Error restoring pane state: {e}")

    def clear_snapshots(self):
        """Clear all hierarchy snapshots."""
        self.snapshots.clear()
        self.logger.debug("Cleared all hierarchy snapshots")


class LayoutValidationEngine:
    """Validates layout configurations and constraints."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def validate_layout_application(
        self,
        layout_type: LayoutType,
        pane_count: int,
        viewport_size: Tuple[int, int],
        container: QWidget,
    ) -> Tuple[bool, str]:
        """
        Validate if a layout can be applied under current conditions.

        Returns:
            (is_valid, error_message)
        """
        try:
            # Basic validations
            if not container:
                return False, "No container widget available"

            if pane_count < 1:
                return False, "Invalid pane count"

            width, height = viewport_size

            # Layout-specific validations
            if layout_type in [
                LayoutType.LEFT_SIDEBAR,
                LayoutType.RIGHT_SIDEBAR,
            ]:
                if pane_count != 1:
                    return False, "Sidebar layouts require exactly 1 pane"
                if width < 800:
                    return False, "Sidebar layouts require minimum 800px width"

            elif layout_type in [
                LayoutType.HORIZONTAL_SPLIT,
                LayoutType.VERTICAL_SPLIT,
            ]:
                if pane_count != 2:
                    return False, "Split layouts require exactly 2 panes"
                if layout_type == LayoutType.HORIZONTAL_SPLIT and width < 600:
                    return (
                        False,
                        "Horizontal split requires minimum 600px width",
                    )
                if layout_type == LayoutType.VERTICAL_SPLIT and height < 600:
                    return (
                        False,
                        "Vertical split requires minimum 600px height",
                    )

            elif layout_type == LayoutType.GRID_2X2:
                if pane_count != 4:
                    return False, "2×2 grid requires exactly 4 panes"
                if width < 800 or height < 600:
                    return False, "2×2 grid requires minimum 800×600 viewport"

            elif layout_type in [
                LayoutType.HORIZONTAL_ROW,
                LayoutType.VERTICAL_COLUMN,
            ]:
                if pane_count < 3:
                    return False, "Row/column layouts require 3+ panes"
                if layout_type == LayoutType.HORIZONTAL_ROW and width < 900:
                    return False, "Horizontal row requires minimum 900px width"
                if layout_type == LayoutType.VERTICAL_COLUMN and height < 800:
                    return (
                        False,
                        "Vertical column requires minimum 800px height",
                    )

            return True, ""

        except Exception as e:
            error_msg = f"Validation error: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def get_layout_constraints_summary(
        self, layout_type: LayoutType
    ) -> Dict[str, Any]:
        """Get summary of constraints for a specific layout type."""
        constraints = {
            LayoutType.FULL_WIDTH: {
                "panes": "1",
                "min_width": "0px",
                "min_height": "0px",
                "description": "No restrictions",
            },
            LayoutType.CENTERED: {
                "panes": "1",
                "min_width": "600px",
                "min_height": "0px",
                "description": "Requires sufficient width for margins",
            },
            LayoutType.LEFT_SIDEBAR: {
                "panes": "1",
                "min_width": "800px",
                "min_height": "0px",
                "description": "Needs space for sidebar and content",
            },
            LayoutType.RIGHT_SIDEBAR: {
                "panes": "1",
                "min_width": "800px",
                "min_height": "0px",
                "description": "Needs space for content and sidebar",
            },
            LayoutType.HORIZONTAL_SPLIT: {
                "panes": "2",
                "min_width": "600px",
                "min_height": "0px",
                "description": "Two panes side by side",
            },
            LayoutType.VERTICAL_SPLIT: {
                "panes": "2",
                "min_width": "0px",
                "min_height": "600px",
                "description": "Two panes stacked vertically",
            },
            LayoutType.GRID_2X2: {
                "panes": "4",
                "min_width": "800px",
                "min_height": "600px",
                "description": "Four panes in 2×2 grid",
            },
            LayoutType.HORIZONTAL_ROW: {
                "panes": "3-4",
                "min_width": "900px",
                "min_height": "0px",
                "description": "All panes in horizontal row",
            },
            LayoutType.VERTICAL_COLUMN: {
                "panes": "3-4",
                "min_width": "0px",
                "min_height": "800px",
                "description": "All panes in vertical column",
            },
            LayoutType.ADAPTIVE_GRID: {
                "panes": "3-4",
                "min_width": "600px",
                "min_height": "400px",
                "description": "Adaptive grid based on viewport",
            },
        }

        return constraints.get(
            layout_type,
            {
                "panes": "Unknown",
                "min_width": "0px",
                "min_height": "0px",
                "description": "No constraint information available",
            },
        )
