"""
LayoutManagerUI: Orchestrate center pane layouts with QSplitters.

Manages dynamic layouts for 1-4 center panes with horizontal, vertical,
and grid arrangements. Handles splitter state persistence.
"""

import logging
from typing import List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QWidget

from src.file_explorer.models.pane_configuration import (
    LayoutType,
    PaneConfiguration,
)
from src.file_explorer.services.layout_manager import get_layout_manager


class LayoutManagerUI(QWidget):
    """UI widget managing center pane layouts with QSplitters."""

    # Signal emitted when layout changes
    layout_changed = pyqtSignal(PaneConfiguration)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the layout manager UI.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.LayoutManagerUI")
        self.layout_manager = get_layout_manager()

        # Current center pane widgets (will be provided externally)
        self.center_panes: List[QWidget] = []

        # Current splitters
        self.main_splitter: Optional[QSplitter] = None

        self.setup_ui()

        # Connect to service signals
        self.layout_manager.layout_changed.connect(self.on_layout_changed)

        self.logger.info("LayoutManagerUI initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def set_center_panes(self, panes: List[QWidget]):
        """
        Set the center pane widgets to be managed.

        Args:
            panes: List of center pane widgets
        """
        self.center_panes = panes
        self.logger.debug(f"Set {len(panes)} center panes")

        # Apply current configuration
        current_config = self.layout_manager.get_current_configuration()
        self.apply_layout(current_config)

    def apply_layout(self, config: PaneConfiguration):
        """
        Apply a pane configuration layout.

        Args:
            config: Pane configuration to apply
        """
        try:
            # Clear existing layout
            self.clear_layout()

            # Validate configuration
            config.validate()

            pane_count = config.pane_count
            layout_type = config.layout_type

            # Ensure we have enough panes
            if len(self.center_panes) < pane_count:
                self.logger.warning(
                    f"Not enough panes: need {pane_count}, "
                    f"have {len(self.center_panes)}"
                )
                return

            # Get panes to display
            panes_to_show = self.center_panes[:pane_count]

            # Create layout based on configuration
            if pane_count == 1:
                # Single pane - no splitter needed
                self.main_layout.addWidget(panes_to_show[0])
                panes_to_show[0].show()

            elif pane_count == 2:
                # Two panes - single splitter
                if layout_type == LayoutType.HORIZONTAL:
                    orientation = Qt.Orientation.Horizontal
                else:  # VERTICAL
                    orientation = Qt.Orientation.Vertical

                self.main_splitter = QSplitter(orientation)
                for pane in panes_to_show:
                    self.main_splitter.addWidget(pane)
                    pane.show()

                # Restore splitter state if available
                state_key = f"main_{layout_type.value}"
                if state_key in config.splitter_states:
                    self.main_splitter.restoreState(config.splitter_states[state_key])

                self.main_layout.addWidget(self.main_splitter)

            elif pane_count == 3:
                # Three panes - nested splitters
                if layout_type == LayoutType.HORIZONTAL:
                    # All horizontal
                    self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
                    for pane in panes_to_show:
                        self.main_splitter.addWidget(pane)
                        pane.show()

                elif layout_type == LayoutType.VERTICAL:
                    # All vertical
                    self.main_splitter = QSplitter(Qt.Orientation.Vertical)
                    for pane in panes_to_show:
                        self.main_splitter.addWidget(pane)
                        pane.show()

                else:  # GRID - 2 top, 1 bottom
                    outer = QSplitter(Qt.Orientation.Vertical)
                    top = QSplitter(Qt.Orientation.Horizontal)
                    top.addWidget(panes_to_show[0])
                    top.addWidget(panes_to_show[1])
                    panes_to_show[0].show()
                    panes_to_show[1].show()
                    outer.addWidget(top)
                    outer.addWidget(panes_to_show[2])
                    panes_to_show[2].show()
                    self.main_splitter = outer

                # Restore splitter state if available
                state_key = f"main_{layout_type.value}"
                if state_key in config.splitter_states:
                    self.main_splitter.restoreState(config.splitter_states[state_key])

                self.main_layout.addWidget(self.main_splitter)

            elif pane_count == 4:
                # Four panes - 2x2 grid
                outer = QSplitter(Qt.Orientation.Vertical)

                # Top row
                top_splitter = QSplitter(Qt.Orientation.Horizontal)
                top_splitter.addWidget(panes_to_show[0])
                top_splitter.addWidget(panes_to_show[1])
                panes_to_show[0].show()
                panes_to_show[1].show()

                # Bottom row
                bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
                bottom_splitter.addWidget(panes_to_show[2])
                bottom_splitter.addWidget(panes_to_show[3])
                panes_to_show[2].show()
                panes_to_show[3].show()

                outer.addWidget(top_splitter)
                outer.addWidget(bottom_splitter)

                self.main_splitter = outer

                # Restore splitter states if available
                if "main_grid" in config.splitter_states:
                    outer.restoreState(config.splitter_states["main_grid"])
                if "top_grid" in config.splitter_states:
                    top_splitter.restoreState(config.splitter_states["top_grid"])
                if "bottom_grid" in config.splitter_states:
                    bottom_splitter.restoreState(config.splitter_states["bottom_grid"])

                self.main_layout.addWidget(self.main_splitter)

            # Hide unused panes
            for i in range(pane_count, len(self.center_panes)):
                self.center_panes[i].hide()

            self.logger.info(
                f"Applied layout: {pane_count} panes, " f"{layout_type.value}"
            )

            # Notify service
            self.layout_manager.apply_configuration(config)

        except Exception as e:
            self.logger.error(f"Error applying layout: {e}")

    def clear_layout(self):
        """Clear the current layout."""
        # Remove all widgets from layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        self.main_splitter = None

    def save_splitter_states(self):
        """Save current splitter positions to configuration."""
        try:
            if not self.main_splitter:
                return

            states = {}
            current_config = self.layout_manager.get_current_configuration()

            # Save state based on layout type
            if current_config.pane_count <= 3:
                state_key = f"main_{current_config.layout_type.value}"
                states[state_key] = bytes(self.main_splitter.saveState())

            elif current_config.pane_count == 4:
                # Save outer splitter
                states["main_grid"] = bytes(self.main_splitter.saveState())

                # Save inner splitters if they exist
                if self.main_splitter.count() >= 2:
                    top_splitter = self.main_splitter.widget(0)
                    bottom_splitter = self.main_splitter.widget(1)

                    if isinstance(top_splitter, QSplitter):
                        states["top_grid"] = bytes(top_splitter.saveState())
                    if isinstance(bottom_splitter, QSplitter):
                        states["bottom_grid"] = bytes(bottom_splitter.saveState())

            # Save to service
            self.layout_manager.save_splitter_states(states)

            self.logger.debug(f"Saved {len(states)} splitter states")

        except Exception as e:
            self.logger.error(f"Error saving splitter states: {e}")

    def on_layout_changed(self, config: PaneConfiguration):
        """
        Handle layout change from service.

        Args:
            config: New configuration
        """
        self.apply_layout(config)
        self.layout_changed.emit(config)

    def change_pane_count(self, count: int):
        """
        Change the number of panes.

        Args:
            count: New pane count (1-4)
        """
        try:
            # Save current splitter states before changing
            self.save_splitter_states()

            current_config = self.layout_manager.get_current_configuration()

            # Determine appropriate layout type for new count
            if count == 1:
                layout_type = LayoutType.DISABLED
            elif count == 2:
                layout_type = LayoutType.HORIZONTAL
            elif count == 3:
                layout_type = LayoutType.VERTICAL
            else:  # count == 4
                layout_type = LayoutType.GRID

            # Create new configuration
            new_config = PaneConfiguration(
                count,
                layout_type,
                current_config.splitter_states,
            )

            # Apply it
            self.apply_layout(new_config)

        except Exception as e:
            self.logger.error(f"Error changing pane count: {e}")

    def change_layout_type(self, layout_type: LayoutType):
        """
        Change the layout arrangement type.

        Args:
            layout_type: New layout type
        """
        try:
            # Save current splitter states before changing
            self.save_splitter_states()

            current_config = self.layout_manager.get_current_configuration()

            # Create new configuration
            new_config = PaneConfiguration(
                current_config.pane_count,
                layout_type,
                current_config.splitter_states,
            )

            # Apply it
            self.apply_layout(new_config)

        except Exception as e:
            self.logger.error(f"Error changing layout type: {e}")
