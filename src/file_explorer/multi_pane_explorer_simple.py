"""
MultiPaneExplorer: Simplified multi-pane interface for hub integration.

Integrates left pane (bookmarks/recent/tools), center panes (file navigation),
and right pane (preview/properties) as specified in refactor-the-multi.
"""

import logging
from typing import List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.file_explorer.services.preference_service import (
    get_preference_service,
)
from src.file_explorer.ui.file_explorer_pane import FileExplorerPane
from src.file_explorer.ui.layout_manager_ui import LayoutManagerUI
from src.file_explorer.ui.left_pane import LeftPane
from src.file_explorer.ui.pane_manager import PaneConfiguration, PaneType
from src.file_explorer.ui.right_pane import RightPane


class MultiPaneExplorer(QWidget):
    """
    Simplified multi-pane explorer widget for hub integration.

    Three-section interface:
    - Left pane: Bookmarks/Recent/Tools tabs (fixed)
    - Center panes: 1-4 file explorer panes (configurable via LayoutManagerUI)
    - Right pane: Preview/Properties tabs (fixed)
    """

    # Signal emitted when a file is selected in any center pane
    file_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the multi-pane explorer.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.MultiPaneExplorer")
        self.preference_service = get_preference_service()

        # Create center file explorer panes (max 4)
        self.center_panes: List[FileExplorerPane] = []
        self._create_center_panes()

        # Create pane components
        self.left_pane = LeftPane()
        self.layout_manager_ui = LayoutManagerUI()
        self.right_pane = RightPane()

        self.setup_ui()
        self.connect_signals()

        # Provide center panes to layout manager
        self.layout_manager_ui.set_center_panes(self.center_panes)

        # Load saved configuration
        self.restore_configuration()

        self.logger.info("MultiPaneExplorer initialized")

    def _create_center_panes(self):
        """Create the center file explorer panes."""
        try:
            # Create 4 panes (max supported)
            for i in range(4):
                config = PaneConfiguration(
                    pane_id=f"center_pane_{i+1}",
                    pane_type=PaneType.FILE_EXPLORER,
                    title=f"File Explorer {i+1}",
                )
                pane = FileExplorerPane(config, parent=self)
                self.center_panes.append(pane)

                # Connect pane signals
                if hasattr(pane, "fileSelected"):
                    pane.fileSelected.connect(self.file_selected.emit)
                if hasattr(pane, "currentPathChanged"):
                    pane.currentPathChanged.connect(self._on_path_changed)

            self.logger.info(f"Created {len(self.center_panes)} center panes")

        except Exception as e:
            self.logger.error(f"Error creating center panes: {e}")
            # Create minimal fallback panes
            for i in range(4):
                fallback = QWidget()
                layout = QVBoxLayout(fallback)
                label = QLabel(f"File Explorer Pane {i+1}\n" f"(Initialization Error)")
                label.setAlignment(Qt.AlignCenter)
                layout.addWidget(label)
                self.center_panes.append(fallback)

    def _on_path_changed(self, path: str):
        """Handle path change from a pane."""
        self.logger.debug(f"Path changed: {path}")

    def setup_ui(self):
        """Set up the main UI structure."""
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # Create main splitter (3-way: left | center | right)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Add panes to splitter
        self.main_splitter.addWidget(self.left_pane)
        self.main_splitter.addWidget(self.layout_manager_ui)
        self.main_splitter.addWidget(self.right_pane)

        # Set initial sizes (20% left, 60% center, 20% right)
        self.main_splitter.setSizes([200, 600, 200])

        # Set stretch factors (left and right don't stretch much)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setStretchFactor(2, 1)

        main_layout.addWidget(self.main_splitter)

    def connect_signals(self):
        """Connect internal signals."""
        # Connect file selection from center panes to right pane
        # Will be wired up when center panes are created
        pass

    def restore_configuration(self):
        """Restore saved pane configuration from preferences."""
        try:
            prefs = self.preference_service.load_preferences()

            # Restore left pane default tab
            self.left_pane.restore_default_tab()

            # Restore center pane configuration
            self.layout_manager_ui.apply_layout(prefs.pane_config)

            # Restore right pane default tab
            self.right_pane.restore_default_tab()

            # Restore splitter state
            self._restore_splitter_state()

            self.logger.info("Configuration restored from preferences")

        except Exception as e:
            self.logger.error(f"Error restoring configuration: {e}")
            # Use defaults

    def _restore_splitter_state(self):
        """Restore main splitter state from preferences."""
        try:
            prefs = self.preference_service.load_preferences()
            splitter_states = prefs.pane_config.splitter_states

            if "main_explorer" in splitter_states:
                state_bytes = splitter_states["main_explorer"]
                self.main_splitter.restoreState(state_bytes)
                self.logger.debug("Main splitter state restored")

        except Exception as e:
            self.logger.error(f"Error restoring splitter state: {e}")

    def save_configuration(self):
        """Save current pane configuration to preferences."""
        try:
            prefs = self.preference_service.load_preferences()

            # Save splitter state
            prefs.pane_config.splitter_states["main_explorer"] = (
                self.main_splitter.saveState()
            )

            # Save layout manager state
            self.layout_manager_ui.save_splitter_states()

            # Save preferences
            self.preference_service.save_preferences(prefs)

            self.logger.info("Configuration saved to preferences")

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")

    def closeEvent(self, event):
        """Handle widget close event."""
        # Save configuration before closing
        self.save_configuration()
        super().closeEvent(event)
