"""
Pane Manager for RFU Multi-Pane File Explorer
Advanced Pane Management and Layout System

This module provides comprehensive pane management capabilities including:
- Pane creation and lifecycle management
- Layout engine for responsive pane arrangements
- Pane configuration and type management
- Factory pattern for extensible pane types
- Advanced layout algorithms for optimal space utilization

Components:
- PaneManager: Central pane coordination and management
- LayoutEngine: Responsive layout calculation and application
- PaneFactory: Extensible pane creation system
- PaneConfiguration: Pane settings and preferences
- BasePaneWidget: Base class for all pane implementations

Author: RFU Development Team
Created: 2025-09-27
Version: 1.0.0
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, Union

try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Fallback definitions
    class QObject:
        pass

    class QWidget:
        pass

    class QFrame:
        pass

    def pyqtSignal(*args):
        def dummy_signal(*signal_args):
            pass

        return dummy_signal


class PaneType(Enum):
    """Enumeration of supported pane types."""

    FILE_EXPLORER = "file_explorer"
    PREVIEW = "preview"
    PROPERTIES = "properties"
    TERMINAL = "terminal"
    SEARCH_RESULTS = "search_results"
    BOOKMARKS = "bookmarks"
    TOOLS = "tools"
    CUSTOM = "custom"


class LayoutType(Enum):
    """Enumeration of layout types."""

    SINGLE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    GRID = auto()
    TABS = auto()
    CUSTOM = auto()


class PaneConfiguration:
    """Configuration settings for a pane."""

    def __init__(
        self,
        pane_id: str,
        pane_type: Union[PaneType, str] = PaneType.FILE_EXPLORER,
        title: str = "Pane",
        resizable: bool = True,
        closable: bool = True,
        min_width: int = 100,
        min_height: int = 100,
        preferred_width: int = 300,
        preferred_height: int = 200,
        **kwargs,
    ):
        """
        Initialize pane configuration.

        Args:
            pane_id: Unique identifier for the pane
            pane_type: Type of pane (PaneType enum or string)
            title: Display title for the pane
            resizable: Whether pane can be resized
            closable: Whether pane can be closed
            min_width: Minimum width in pixels
            min_height: Minimum height in pixels
            preferred_width: Preferred width in pixels
            preferred_height: Preferred height in pixels
            **kwargs: Additional configuration options
        """
        self.pane_id = pane_id
        self.pane_type = (
            pane_type if isinstance(pane_type, PaneType) else PaneType(pane_type)
        )
        self.title = title
        self.resizable = resizable
        self.closable = closable
        self.min_width = min_width
        self.min_height = min_height
        self.preferred_width = preferred_width
        self.preferred_height = preferred_height

        # Store additional configuration
        self.extra_config = kwargs

        # Creation metadata
        self.created_at = datetime.now()
        self.last_modified = datetime.now()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.extra_config.get(key, default)

    def set_config_value(self, key: str, value: Any):
        """Set configuration value."""
        self.extra_config[key] = value
        self.last_modified = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "pane_id": self.pane_id,
            "pane_type": self.pane_type.value,
            "title": self.title,
            "resizable": self.resizable,
            "closable": self.closable,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "preferred_width": self.preferred_width,
            "preferred_height": self.preferred_height,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            **self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaneConfiguration":
        """Create configuration from dictionary."""
        config = cls(
            pane_id=data["pane_id"],
            pane_type=data.get("pane_type", PaneType.FILE_EXPLORER),
            title=data.get("title", "Pane"),
            resizable=data.get("resizable", True),
            closable=data.get("closable", True),
            min_width=data.get("min_width", 100),
            min_height=data.get("min_height", 100),
            preferred_width=data.get("preferred_width", 300),
            preferred_height=data.get("preferred_height", 200),
        )

        # Restore timestamps
        if "created_at" in data:
            try:
                config.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        if "last_modified" in data:
            try:
                config.last_modified = datetime.fromisoformat(data["last_modified"])
            except (ValueError, TypeError):
                pass

        # Add extra configuration
        excluded_keys = {
            "pane_id",
            "pane_type",
            "title",
            "resizable",
            "closable",
            "min_width",
            "min_height",
            "preferred_width",
            "preferred_height",
            "created_at",
            "last_modified",
        }

        for key, value in data.items():
            if key not in excluded_keys:
                config.extra_config[key] = value

        return config


class BasePaneWidget(QFrame if QT_AVAILABLE else object):
    """Base class for all pane widgets."""

    # Signals
    paneActivated = pyqtSignal(str) if QT_AVAILABLE else None
    paneModified = pyqtSignal(str, bool) if QT_AVAILABLE else None
    paneClosing = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, config: PaneConfiguration, parent=None):
        """
        Initialize base pane widget.

        Args:
            config: Pane configuration
            parent: Parent widget
        """
        if QT_AVAILABLE:
            super().__init__(parent)

        self.config = config
        self.logger = logging.getLogger(f"RFU.FileExplorer.Pane.{config.pane_id}")

        # Pane state
        self._is_active = False
        self._is_modified = False
        self._creation_time = datetime.now()
        self._last_access_time = datetime.now()

        # UI setup
        if QT_AVAILABLE:
            self._setup_ui()

    def _setup_ui(self):
        """Setup the pane user interface."""
        if not QT_AVAILABLE:
            return

        # Set basic properties
        self.setObjectName(f"pane_{self.config.pane_id}")
        self.setWindowTitle(self.config.title)

        # Set size constraints
        self.setMinimumSize(self.config.min_width, self.config.min_height)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create content area
        self._content_widget = self._create_content_widget()
        if self._content_widget:
            layout.addWidget(self._content_widget, 1)

    def _create_content_widget(self) -> QWidget:
        """Create content widget. Override in subclasses."""
        if not QT_AVAILABLE:
            return None

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        return content

    def set_active(self, active: bool = True):
        """Set pane active state."""
        if self._is_active != active:
            self._is_active = active
            self._last_access_time = datetime.now()

            if active and self.paneActivated:
                self.paneActivated.emit(self.config.pane_id)

    def set_modified(self, modified: bool = True):
        """Set pane modified state."""
        if self._is_modified != modified:
            self._is_modified = modified

            if self.paneModified:
                self.paneModified.emit(self.config.pane_id, modified)

    def is_active(self) -> bool:
        """Check if pane is active."""
        return self._is_active

    def is_modified(self) -> bool:
        """Check if pane is modified."""
        return self._is_modified

    def get_state_data(self) -> Dict[str, Any]:
        """Get pane state data for persistence."""
        return {
            "pane_id": self.config.pane_id,
            "pane_type": self.config.pane_type.value,
            "title": self.config.title,
            "is_active": self._is_active,
            "is_modified": self._is_modified,
            "creation_time": self._creation_time.isoformat(),
            "last_access_time": self._last_access_time.isoformat(),
        }

    def restore_state_data(self, data: Dict[str, Any]):
        """Restore pane state data from persistence."""
        self._is_active = data.get("is_active", False)
        self._is_modified = data.get("is_modified", False)

        # Restore timestamps
        if "creation_time" in data:
            try:
                self._creation_time = datetime.fromisoformat(data["creation_time"])
            except (ValueError, TypeError):
                pass

        if "last_access_time" in data:
            try:
                self._last_access_time = datetime.fromisoformat(
                    data["last_access_time"]
                )
            except (ValueError, TypeError):
                pass

    def cleanup(self):
        """Clean up pane resources. Override in subclasses."""
        try:
            if self.paneClosing:
                self.paneClosing.emit(self.config.pane_id)

            self.logger.debug(f"Pane {self.config.pane_id} cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during pane cleanup: {e}")


class LayoutEngine:
    """Engine for calculating and applying pane layouts."""

    def __init__(self):
        """Initialize layout engine."""
        self.logger = logging.getLogger("RFU.FileExplorer.LayoutEngine")

    def calculate_layout(
        self,
        panes: List[BasePaneWidget],
        layout_type: LayoutType,
        container_size: tuple = (800, 600),
    ) -> Dict[str, Any]:
        """
        Calculate optimal layout for panes.

        Args:
            panes: List of panes to layout
            layout_type: Type of layout to apply
            container_size: Available container size (width, height)

        Returns:
            Layout configuration dictionary
        """
        try:
            if not panes:
                return {}

            layout_config = {
                "layout_type": layout_type,
                "container_size": container_size,
                "pane_configs": [],
            }

            if layout_type == LayoutType.SINGLE:
                layout_config = self._calculate_single_layout(panes, container_size)
            elif layout_type == LayoutType.HORIZONTAL:
                layout_config = self._calculate_horizontal_layout(panes, container_size)
            elif layout_type == LayoutType.VERTICAL:
                layout_config = self._calculate_vertical_layout(panes, container_size)
            elif layout_type == LayoutType.GRID:
                layout_config = self._calculate_grid_layout(panes, container_size)
            elif layout_type == LayoutType.TABS:
                layout_config = self._calculate_tabs_layout(panes, container_size)

            self.logger.debug(
                f"Calculated {layout_type.name} layout for {len(panes)} panes"
            )
            return layout_config

        except Exception as e:
            self.logger.error(f"Error calculating layout: {e}")
            return {}

    def _calculate_single_layout(
        self, panes: List[BasePaneWidget], container_size: tuple
    ) -> Dict[str, Any]:
        """Calculate single pane layout."""
        return {
            "layout_type": LayoutType.SINGLE,
            "container_size": container_size,
            "pane_configs": (
                [
                    {
                        "pane_id": panes[0].config.pane_id,
                        "x": 0,
                        "y": 0,
                        "width": container_size[0],
                        "height": container_size[1],
                    }
                ]
                if panes
                else []
            ),
        }

    def _calculate_horizontal_layout(
        self, panes: List[BasePaneWidget], container_size: tuple
    ) -> Dict[str, Any]:
        """Calculate horizontal split layout."""
        width, height = container_size
        pane_width = width // len(panes)

        configs = []
        for i, pane in enumerate(panes):
            configs.append(
                {
                    "pane_id": pane.config.pane_id,
                    "x": i * pane_width,
                    "y": 0,
                    "width": pane_width,
                    "height": height,
                }
            )

        return {
            "layout_type": LayoutType.HORIZONTAL,
            "container_size": container_size,
            "pane_configs": configs,
        }

    def _calculate_vertical_layout(
        self, panes: List[BasePaneWidget], container_size: tuple
    ) -> Dict[str, Any]:
        """Calculate vertical split layout."""
        width, height = container_size
        pane_height = height // len(panes)

        configs = []
        for i, pane in enumerate(panes):
            configs.append(
                {
                    "pane_id": pane.config.pane_id,
                    "x": 0,
                    "y": i * pane_height,
                    "width": width,
                    "height": pane_height,
                }
            )

        return {
            "layout_type": LayoutType.VERTICAL,
            "container_size": container_size,
            "pane_configs": configs,
        }

    def _calculate_grid_layout(
        self, panes: List[BasePaneWidget], container_size: tuple
    ) -> Dict[str, Any]:
        """Calculate grid layout."""
        import math

        width, height = container_size
        pane_count = len(panes)

        # Calculate optimal grid dimensions
        cols = math.ceil(math.sqrt(pane_count))
        rows = math.ceil(pane_count / cols)

        pane_width = width // cols
        pane_height = height // rows

        configs = []
        for i, pane in enumerate(panes):
            row = i // cols
            col = i % cols

            configs.append(
                {
                    "pane_id": pane.config.pane_id,
                    "x": col * pane_width,
                    "y": row * pane_height,
                    "width": pane_width,
                    "height": pane_height,
                }
            )

        return {
            "layout_type": LayoutType.GRID,
            "container_size": container_size,
            "pane_configs": configs,
        }

    def _calculate_tabs_layout(
        self, panes: List[BasePaneWidget], container_size: tuple
    ) -> Dict[str, Any]:
        """Calculate tabbed layout."""
        width, height = container_size

        configs = []
        for pane in panes:
            configs.append(
                {
                    "pane_id": pane.config.pane_id,
                    "x": 0,
                    "y": 0,
                    "width": width,
                    "height": height,
                    "tab": True,
                }
            )

        return {
            "layout_type": LayoutType.TABS,
            "container_size": container_size,
            "pane_configs": configs,
        }


class PaneFactory:
    """Factory for creating pane instances."""

    _pane_classes: Dict[PaneType, Type[BasePaneWidget]] = {}

    @classmethod
    def register_pane_class(cls, pane_type: PaneType, pane_class: Type[BasePaneWidget]):
        """
        Register a pane class for a specific type.

        Args:
            pane_type: Type of pane
            pane_class: Class to use for creating panes of this type
        """
        cls._pane_classes[pane_type] = pane_class
        # Handle both enum and string types for pane_type
        pane_type_str = (
            pane_type.value if hasattr(pane_type, "value") else str(pane_type)
        )
        logging.getLogger("RFU.FileExplorer.PaneFactory").info(
            f"Registered pane class {pane_class.__name__} for type {pane_type_str}"
        )

    @classmethod
    def create_pane(
        cls, config: PaneConfiguration, parent=None
    ) -> Optional[BasePaneWidget]:
        """
        Create a pane instance based on configuration.

        Args:
            config: Pane configuration
            parent: Parent widget

        Returns:
            Created pane instance or None if creation failed
        """
        logger = logging.getLogger("RFU.FileExplorer.PaneFactory")

        try:
            pane_class = cls._pane_classes.get(config.pane_type)

            if not pane_class:
                pane_type_str = (
                    config.pane_type.value
                    if hasattr(config.pane_type, "value")
                    else str(config.pane_type)
                )
                logger.warning(f"No pane class registered for type {pane_type_str}")
                # Try to create a basic fallback pane
                return cls._create_fallback_pane(config, parent)

            # Create pane instance
            pane = pane_class(config, parent)
            pane_type_str = (
                config.pane_type.value
                if hasattr(config.pane_type, "value")
                else str(config.pane_type)
            )
            logger.info(f"Created pane {config.pane_id} of type {pane_type_str}")
            return pane

        except Exception as e:
            logger.error(f"Error creating pane {config.pane_id}: {e}")
            return cls._create_fallback_pane(config, parent)

    @classmethod
    def _create_fallback_pane(
        cls, config: PaneConfiguration, parent=None
    ) -> Optional[BasePaneWidget]:
        """Create a fallback pane when specific type creation fails."""
        try:
            # Create basic pane
            pane = BasePaneWidget(config, parent)
            logging.getLogger("RFU.FileExplorer.PaneFactory").info(
                f"Created fallback pane {config.pane_id}"
            )
            return pane
        except Exception as e:
            logging.getLogger("RFU.FileExplorer.PaneFactory").error(
                f"Failed to create fallback pane: {e}"
            )
            return None

    @classmethod
    def get_registered_types(cls) -> List[PaneType]:
        """Get list of registered pane types."""
        return list(cls._pane_classes.keys())


class PaneManager(QObject if QT_AVAILABLE else object):
    """Central manager for pane creation, layout, and coordination."""

    # Signals
    paneAdded = pyqtSignal(str) if QT_AVAILABLE else None
    paneRemoved = pyqtSignal(str) if QT_AVAILABLE else None
    layoutChanged = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, parent=None):
        """Initialize pane manager."""
        if QT_AVAILABLE:
            super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.PaneManager")

        # Pane registry
        self._panes: Dict[str, BasePaneWidget] = {}
        self._pane_configs: Dict[str, PaneConfiguration] = {}

        # Layout management
        self.layout_engine = LayoutEngine()
        self.current_layout_type = LayoutType.HORIZONTAL
        self.container_widget = None

        # State management
        self.active_pane_id = ""
        self.layout_history = []
        self.max_history = 10

    def set_container_widget(self, container: QWidget):
        """
        Set the container widget for panes.

        Args:
            container: Widget that will contain the panes
        """
        self.container_widget = container
        self.logger.debug(f"Container widget set: {type(container).__name__}")

    def add_pane(self, config: PaneConfiguration) -> Optional[BasePaneWidget]:
        """
        Add a new pane.

        Args:
            config: Pane configuration

        Returns:
            Created pane widget or None if creation failed
        """
        try:
            if config.pane_id in self._panes:
                self.logger.warning(f"Pane {config.pane_id} already exists")
                return self._panes[config.pane_id]

            # Create pane using factory
            pane = PaneFactory.create_pane(config, self.container_widget)
            if not pane:
                self.logger.error(f"Failed to create pane {config.pane_id}")
                return None

            # Register pane
            self._panes[config.pane_id] = pane
            self._pane_configs[config.pane_id] = config

            # Connect signals
            if hasattr(pane, "paneActivated"):
                pane.paneActivated.connect(self._on_pane_activated)
            if hasattr(pane, "paneModified"):
                pane.paneModified.connect(self._on_pane_modified)
            if hasattr(pane, "paneClosing"):
                pane.paneClosing.connect(self._on_pane_closing)

            # Emit signal
            if self.paneAdded:
                self.paneAdded.emit(config.pane_id)

            self.logger.info(
                f"Added pane {config.pane_id} of type {config.pane_type.value}"
            )
            return pane

        except Exception as e:
            self.logger.error(f"Error adding pane {config.pane_id}: {e}")
            return None

    def remove_pane(self, pane_id: str) -> bool:
        """
        Remove a pane.

        Args:
            pane_id: ID of pane to remove

        Returns:
            True if pane was removed successfully
        """
        try:
            if pane_id not in self._panes:
                self.logger.warning(f"Pane {pane_id} not found")
                return False

            pane = self._panes[pane_id]

            # Cleanup pane
            if hasattr(pane, "cleanup"):
                pane.cleanup()

            # Remove from container
            if hasattr(pane, "setParent"):
                pane.setParent(None)

            # Remove from registry
            del self._panes[pane_id]
            del self._pane_configs[pane_id]

            # Update active pane if necessary
            if self.active_pane_id == pane_id:
                remaining_panes = list(self._panes.keys())
                self.active_pane_id = remaining_panes[0] if remaining_panes else ""

            # Emit signal
            if self.paneRemoved:
                self.paneRemoved.emit(pane_id)

            self.logger.info(f"Removed pane {pane_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error removing pane {pane_id}: {e}")
            return False

    def get_pane(self, pane_id: str) -> Optional[BasePaneWidget]:
        """Get pane by ID."""
        return self._panes.get(pane_id)

    def get_all_panes(self) -> List[BasePaneWidget]:
        """Get list of all panes."""
        return list(self._panes.values())

    def get_pane_config(self, pane_id: str) -> Optional[PaneConfiguration]:
        """Get pane configuration by ID."""
        return self._pane_configs.get(pane_id)

    def set_layout_type(self, layout_type: LayoutType):
        """
        Set layout type and update layout.

        Args:
            layout_type: New layout type
        """
        if self.current_layout_type != layout_type:
            # Save current layout to history
            self._save_layout_to_history()

            self.current_layout_type = layout_type
            self._apply_layout()

            if self.layoutChanged:
                self.layoutChanged.emit(layout_type.name)

            self.logger.info(f"Layout type changed to {layout_type.name}")

    def _apply_layout(self):
        """Apply current layout to panes."""
        try:
            if not self.container_widget or not self._panes:
                return

            panes = list(self._panes.values())
            container_size = (
                self.container_widget.width(),
                self.container_widget.height(),
            )

            layout_config = self.layout_engine.calculate_layout(
                panes, self.current_layout_type, container_size
            )

            if layout_config:
                self._apply_layout_config(layout_config)

        except Exception as e:
            self.logger.error(f"Error applying layout: {e}")

    def _apply_layout_config(self, layout_config: Dict[str, Any]):
        """Apply layout configuration to panes."""
        try:
            layout_type = layout_config.get("layout_type")
            pane_configs = layout_config.get("pane_configs", [])

            if layout_type == LayoutType.TABS:
                self._apply_tabs_layout(pane_configs)
            else:
                self._apply_geometric_layout(pane_configs)

        except Exception as e:
            self.logger.error(f"Error applying layout config: {e}")

    def _apply_geometric_layout(self, pane_configs: List[Dict[str, Any]]):
        """Apply geometric layout to panes."""
        for config in pane_configs:
            pane_id = config["pane_id"]
            pane = self._panes.get(pane_id)

            if pane and hasattr(pane, "setGeometry"):
                pane.setGeometry(
                    config["x"], config["y"], config["width"], config["height"]
                )

    def _apply_tabs_layout(self, pane_configs: List[Dict[str, Any]]):
        """Apply tabbed layout to panes."""
        # Implementation would require QTabWidget integration
        # For now, fallback to horizontal layout
        self.current_layout_type = LayoutType.HORIZONTAL
        self._apply_layout()

    def _save_layout_to_history(self):
        """Save current layout to history."""
        if len(self.layout_history) >= self.max_history:
            self.layout_history.pop(0)

        layout_state = {
            "layout_type": self.current_layout_type,
            "timestamp": datetime.now().isoformat(),
            "pane_count": len(self._panes),
        }

        self.layout_history.append(layout_state)

    def _on_pane_activated(self, pane_id: str):
        """Handle pane activation."""
        self.active_pane_id = pane_id
        self.logger.debug(f"Pane activated: {pane_id}")

    def _on_pane_modified(self, pane_id: str, modified: bool):
        """Handle pane modification state change."""
        self.logger.debug(f"Pane {pane_id} modified state: {modified}")

    def _on_pane_closing(self, pane_id: str):
        """Handle pane closing request."""
        self.remove_pane(pane_id)

    def get_state_data(self) -> Dict[str, Any]:
        """Get pane manager state for persistence."""
        return {
            "layout_type": self.current_layout_type.name,
            "active_pane_id": self.active_pane_id,
            "pane_configs": {
                pane_id: config.to_dict()
                for pane_id, config in self._pane_configs.items()
            },
            "pane_states": {
                pane_id: pane.get_state_data()
                for pane_id, pane in self._panes.items()
                if hasattr(pane, "get_state_data")
            },
        }

    def restore_state_data(self, data: Dict[str, Any]):
        """Restore pane manager state from persistence."""
        try:
            # Restore layout type
            if "layout_type" in data:
                try:
                    self.current_layout_type = LayoutType[data["layout_type"]]
                except (KeyError, ValueError):
                    pass

            # Restore active pane
            self.active_pane_id = data.get("active_pane_id", "")

            # Restore pane configurations
            pane_configs = data.get("pane_configs", {})
            for pane_id, config_data in pane_configs.items():
                try:
                    config = PaneConfiguration.from_dict(config_data)
                    pane = self.add_pane(config)

                    # Restore pane state
                    pane_states = data.get("pane_states", {})
                    if (
                        pane_id in pane_states
                        and pane
                        and hasattr(pane, "restore_state_data")
                    ):
                        pane.restore_state_data(pane_states[pane_id])

                except Exception as e:
                    self.logger.warning(f"Error restoring pane {pane_id}: {e}")

            # Apply layout
            self._apply_layout()

            self.logger.info("Pane manager state restored successfully")

        except Exception as e:
            self.logger.error(f"Error restoring pane manager state: {e}")

    def cleanup(self):
        """Clean up all panes and resources."""
        try:
            pane_ids = list(self._panes.keys())
            for pane_id in pane_ids:
                self.remove_pane(pane_id)

            self.logger.info("Pane manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during pane manager cleanup: {e}")


# Register default pane types
def _register_default_pane_types():
    """Register default pane types with the factory."""
    try:
        # Import and register file explorer pane
        try:
            from .file_explorer_pane import FileExplorerPane

            PaneFactory.register_pane_class(PaneType.FILE_EXPLORER, FileExplorerPane)
        except ImportError:
            pass

        # Additional pane types can be registered here

    except Exception as e:
        logging.getLogger("RFU.FileExplorer.PaneManager").warning(
            f"Error registering default pane types: {e}"
        )


# Register default types on module import
_register_default_pane_types()


# Export main classes
__all__ = [
    "PaneType",
    "LayoutType",
    "PaneConfiguration",
    "BasePaneWidget",
    "LayoutEngine",
    "PaneFactory",
    "PaneManager",
]
