#!/usr/bin/env python3
"""
Pane Manager for Multi-Pane File Explorer

Handles creation, lifecycle, and coordination of file explorer panes
with comprehensive error handling and recovery capabilities.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import QObject, pyqtSignal
    from PyQt5.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QObject = object


class PaneManager(QObject if QT_AVAILABLE else object):
    """
    Manager for file explorer panes with enterprise-grade reliability.

    Responsibilities:
    - Create and destroy panes
    - Track pane state and health
    - Coordinate pane interactions
    - Handle pane navigation
    """

    # Signals
    paneAdded = pyqtSignal(str) if QT_AVAILABLE else None
    paneRemoved = pyqtSignal(str) if QT_AVAILABLE else None
    paneActivated = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, controller):
        """Initialize pane manager."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.PaneManager")
        self.controller = controller

        # Pane registry
        self._panes: Dict[str, QWidget] = {}
        self._pane_paths: Dict[str, str] = {}
        self._pane_counter = 0

        # State tracking
        self.active_pane_id = ""
        self.max_panes = 4

        # Component protection
        from ...gui.component_guardian import get_component_guardian

        self.guardian = get_component_guardian()

        self.logger.info("Pane manager initialized")

    def create_panes(self, count: int) -> bool:
        """
        Create specified number of panes.

        Args:
            count: Number of panes to create (1-4)

        Returns:
            bool: True if successful
        """
        try:
            if not 1 <= count <= self.max_panes:
                self.logger.error(f"Invalid pane count: {count}")
                return False

            # Clear existing panes
            self._clear_all_panes()

            # Create new panes
            success_count = 0
            for i in range(count):
                pane_id = f"pane_{i + 1}"
                if self._create_single_pane(pane_id, i + 1):
                    success_count += 1
                else:
                    self.logger.error(f"Failed to create pane {pane_id}")

            if success_count > 0:
                # Set first pane as active
                pane_ids = list(self._panes.keys())
                if pane_ids:
                    self.set_active_pane(pane_ids[0])

                self.logger.info(f"Created {success_count}/{count} panes")
                return True
            else:
                self.logger.error("Failed to create any panes")
                return False

        except Exception as e:
            self.logger.error(f"Error creating panes: {e}")
            return False

    def _create_single_pane(self, pane_id: str, pane_number: int) -> bool:
        """Create a single file explorer pane."""
        try:
            # Try to create enhanced pane first
            pane = self._create_enhanced_pane(pane_id, pane_number)

            if not pane:
                # Fallback to simple pane
                pane = self._create_simple_pane(pane_id, pane_number)

            if pane:
                # Register with guardian
                comp_id = self.guardian.register_component(
                    pane,
                    f"FileExplorerPane_{pane_number}",
                    lambda: self._recover_pane(pane_id),
                )

                # Store pane
                self._panes[pane_id] = pane
                self._pane_paths[pane_id] = str(Path.home())

                # Emit signal
                if self.paneAdded:
                    self.paneAdded.emit(pane_id)

                self.logger.info(f"Created pane {pane_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error creating pane {pane_id}: {e}")
            return False

    def _create_enhanced_pane(
        self, pane_id: str, pane_number: int
    ) -> Optional[QWidget]:
        """Create enhanced file explorer pane."""
        try:
            from ..ui.file_explorer_pane import FileExplorerPane
            from ..ui.pane_manager import PaneConfiguration, PaneType

            config = PaneConfiguration(
                pane_id=pane_id,
                pane_type=PaneType.FILE_EXPLORER,
                title=f"File Explorer {pane_number}",
            )

            pane = FileExplorerPane(config)
            pane.navigate_to(str(Path.home()))

            return pane

        except ImportError:
            self.logger.debug("Enhanced pane not available, using fallback")
            return None
        except Exception as e:
            self.logger.warning(f"Error creating enhanced pane: {e}")
            return None

    def _create_simple_pane(self, pane_id: str, pane_number: int) -> Optional[QWidget]:
        """Create simple fallback pane."""
        try:
            from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

            pane = QFrame()
            layout = QVBoxLayout(pane)

            title_label = QLabel(f"File Explorer Pane {pane_number}")
            title_label.setStyleSheet(
                "font-weight: bold; padding: 10px; "
                "background-color: #f0f0f0; border: 1px solid #ccc;"
            )
            layout.addWidget(title_label)

            # Store pane properties
            pane._pane_id = pane_id
            pane._pane_number = pane_number
            pane._current_path = Path.home()

            return pane

        except Exception as e:
            self.logger.error(f"Error creating simple pane: {e}")
            return None

    def _recover_pane(self, pane_id: str) -> bool:
        """Recovery callback for panes."""
        try:
            self.logger.info(f"Attempting to recover pane {pane_id}")

            if pane_id not in self._panes:
                return False

            # Get pane number for recreation
            old_pane = self._panes[pane_id]
            pane_number = getattr(old_pane, "_pane_number", 1)

            # Remove old pane
            self._remove_pane_internal(pane_id)

            # Recreate pane
            return self._create_single_pane(pane_id, pane_number)

        except Exception as e:
            self.logger.error(f"Pane recovery failed for {pane_id}: {e}")
            return False

    def _clear_all_panes(self):
        """Clear all existing panes."""
        try:
            pane_ids = list(self._panes.keys())
            for pane_id in pane_ids:
                self._remove_pane_internal(pane_id)

            self.logger.info("Cleared all panes")

        except Exception as e:
            self.logger.error(f"Error clearing panes: {e}")

    def _remove_pane_internal(self, pane_id: str):
        """Remove pane from internal tracking."""
        try:
            if pane_id in self._panes:
                pane = self._panes[pane_id]

                # Cleanup widget
                if hasattr(pane, "setParent"):
                    pane.setParent(None)
                if hasattr(pane, "deleteLater"):
                    pane.deleteLater()

                # Remove from tracking
                del self._panes[pane_id]
                if pane_id in self._pane_paths:
                    del self._pane_paths[pane_id]

                # Emit signal
                if self.paneRemoved:
                    self.paneRemoved.emit(pane_id)

                self.logger.debug(f"Removed pane {pane_id}")

        except Exception as e:
            self.logger.error(f"Error removing pane {pane_id}: {e}")

    def set_active_pane(self, pane_id: str) -> bool:
        """Set active pane."""
        try:
            if pane_id not in self._panes:
                self.logger.warning(f"Pane {pane_id} not found")
                return False

            old_active = self.active_pane_id
            self.active_pane_id = pane_id

            if self.paneActivated:
                self.paneActivated.emit(pane_id)

            self.logger.debug(f"Active pane changed from {old_active} to {pane_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting active pane: {e}")
            return False

    def navigate(self, pane_id: str, path: str) -> bool:
        """Navigate pane to specified path."""
        try:
            if pane_id not in self._panes:
                return False

            if not Path(path).exists():
                self.logger.warning(f"Path does not exist: {path}")
                return False

            pane = self._panes[pane_id]

            # Update pane path
            if hasattr(pane, "navigate_to"):
                pane.navigate_to(path)
            elif hasattr(pane, "_current_path"):
                pane._current_path = Path(path)

            # Track path
            self._pane_paths[pane_id] = path

            self.logger.debug(f"Pane {pane_id} navigated to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error navigating pane {pane_id}: {e}")
            return False

    def get_path(self, pane_id: str) -> Optional[str]:
        """Get current path of pane."""
        return self._pane_paths.get(pane_id)

    def get_selected(self, pane_id: str) -> List[str]:
        """Get selected files from pane."""
        try:
            if pane_id not in self._panes:
                return []

            pane = self._panes[pane_id]

            # Try to get selection from pane
            if hasattr(pane, "get_selected_files"):
                return pane.get_selected_files()
            elif hasattr(pane, "_get_selected_files"):
                return pane._get_selected_files()
            else:
                return []

        except Exception as e:
            self.logger.error(f"Error getting selected files from {pane_id}: {e}")
            return []

    def refresh(self, pane_id: str) -> bool:
        """Refresh specified pane."""
        try:
            if pane_id not in self._panes:
                return False

            current_path = self.get_path(pane_id)
            if current_path:
                return self.navigate(pane_id, current_path)

            return True

        except Exception as e:
            self.logger.error(f"Error refreshing pane {pane_id}: {e}")
            return False

    def get_pane_ids(self) -> List[str]:
        """Get list of all pane IDs."""
        return list(self._panes.keys())

    def get_pane_widget(self, pane_id: str) -> Optional[QWidget]:
        """Get pane widget by ID."""
        return self._panes.get(pane_id)

    def get_status(self) -> Dict[str, Any]:
        """Get pane manager status."""
        return {
            "total_panes": len(self._panes),
            "active_pane_id": self.active_pane_id,
            "pane_ids": list(self._panes.keys()),
            "pane_paths": dict(self._pane_paths),
        }

    def cleanup(self):
        """Clean up pane manager."""
        try:
            self.logger.info("Cleaning up pane manager")
            self._clear_all_panes()
            self.active_pane_id = ""
            self.logger.info("Pane manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during pane manager cleanup: {e}")
