"""
import time

Keyboard Shortcuts System - Phase 4 Implementation
Comprehensive keyboard shortcuts with customizable bindings and conflict resolution

This module provides enterprise-grade keyboard shortcut management with:
- Customizable key bindings with user preference management
- Intelligent conflict resolution and validation
- Context-aware shortcut activation
- Cross-platform compatibility and accessibility
- Dynamic shortcut registration and management
- Performance optimization and caching

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: September 13, 2025
"""

import json
import logging
import platform
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtWidgets import QAction, QApplication, QShortcut

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QObject = object
    Qt = None
    QKeySequence = None
    pyqtSignal = lambda *args: None

try:
    from src.config_manager import ConfigManager
    from src.log_manager import get_log_manager
except ImportError:
    ConfigManager = None

    def get_log_manager():
        return logging


class ShortcutContext(Enum):
    """Context enumeration for shortcut activation."""

    GLOBAL = "global"
    FILE_EXPLORER = "file_explorer"
    TOOL_SPECIFIC = "tool_specific"
    PANE_FOCUSED = "pane_focused"
    DIALOG = "dialog"
    MENU = "menu"
    EDIT_MODE = "edit_mode"


class ShortcutCategory(Enum):
    """Category classification for shortcuts."""

    NAVIGATION = "navigation"
    FILE_OPERATIONS = "file_operations"
    TOOL_LAUNCH = "tool_launch"
    VIEW_CONTROL = "view_control"
    SELECTION = "selection"
    EDIT = "edit"
    SYSTEM = "system"
    CUSTOM = "custom"


class ShortcutPriority(Enum):
    """Priority levels for shortcut resolution."""

    SYSTEM = 1  # Highest priority - system shortcuts
    APPLICATION = 2  # Application-level shortcuts
    CONTEXT = 3  # Context-specific shortcuts
    TOOL = 4  # Tool-specific shortcuts
    USER = 5  # User-defined shortcuts
    DEFAULT = 6  # Default/fallback shortcuts


@dataclass
class ShortcutDefinition:
    """Comprehensive shortcut definition."""

    id: str
    name: str
    description: str
    key_sequence: str
    callback: Optional[Callable] = None
    context: ShortcutContext = ShortcutContext.GLOBAL
    category: ShortcutCategory = ShortcutCategory.CUSTOM
    priority: ShortcutPriority = ShortcutPriority.DEFAULT
    enabled: bool = True
    visible: bool = True
    tooltip: str = ""
    icon: Optional[str] = None
    alternate_sequences: List[str] = field(default_factory=list)
    platform_specific: Dict[str, str] = field(default_factory=dict)
    requires_confirmation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_platform_sequence(self) -> str:
        """Get platform-specific key sequence."""
        current_platform = platform.system().lower()
        return self.platform_specific.get(current_platform, self.key_sequence)


@dataclass
class ShortcutConflict:
    """Information about shortcut conflicts."""

    key_sequence: str
    conflicting_shortcuts: List[ShortcutDefinition]
    resolution_strategy: str = "priority"  # priority, context, manual
    resolved_shortcut: Optional[ShortcutDefinition] = None
    timestamp: float = 0.0
    auto_resolved: bool = False


class ShortcutValidator:
    """Validates shortcut definitions and key sequences."""

    def __init__(self):
        self.logger = get_log_manager().get_logger("ShortcutValidator")
        self.reserved_sequences = self._get_reserved_sequences()
        self.invalid_patterns = self._get_invalid_patterns()

    def validate_shortcut(
        self, shortcut: ShortcutDefinition
    ) -> Tuple[bool, List[str]]:
        """Validate a shortcut definition."""
        errors = []

        # Validate ID
        if not shortcut.id or not shortcut.id.strip():
            errors.append("Shortcut ID cannot be empty")

        # Validate name
        if not shortcut.name or not shortcut.name.strip():
            errors.append("Shortcut name cannot be empty")

        # Validate key sequence
        sequence_valid, sequence_errors = self._validate_key_sequence(
            shortcut.key_sequence
        )
        if not sequence_valid:
            errors.extend(sequence_errors)

        # Validate callback
        if shortcut.callback and not callable(shortcut.callback):
            errors.append("Callback must be callable")

        # Validate platform-specific sequences
        for platform_name, sequence in shortcut.platform_specific.items():
            seq_valid, seq_errors = self._validate_key_sequence(sequence)
            if not seq_valid:
                errors.extend(
                    [
                        f"Platform {platform_name}: {error}"
                        for error in seq_errors
                    ]
                )

        return len(errors) == 0, errors

    def _validate_key_sequence(self, sequence: str) -> Tuple[bool, List[str]]:
        """Validate a key sequence string."""
        errors = []

        if not sequence or not sequence.strip():
            errors.append("Key sequence cannot be empty")
            return False, errors

        # Check for reserved sequences
        if sequence.lower() in self.reserved_sequences:
            errors.append(f"Key sequence '{sequence}' is reserved")

        # Check for invalid patterns
        for pattern in self.invalid_patterns:
            if pattern in sequence.lower():
                errors.append(
                    f"Key sequence contains invalid pattern: {pattern}"
                )

        # Validate with Qt if available
        if PYQT_AVAILABLE:
            try:
                qt_sequence = QKeySequence(sequence)
                if qt_sequence.isEmpty():
                    errors.append(f"Invalid key sequence format: {sequence}")
            except Exception as e:
                errors.append(f"Qt validation failed: {e}")

        return len(errors) == 0, errors

    def _get_reserved_sequences(self) -> Set[str]:
        """Get platform-specific reserved key sequences."""
        common_reserved = {
            "ctrl+c",
            "ctrl+v",
            "ctrl+x",
            "ctrl+z",
            "ctrl+y",
            "alt+f4",
            "ctrl+alt+del",
            "windows",
            "alt+tab",
        }

        system = platform.system().lower()
        if system == "darwin":  # macOS
            mac_reserved = {
                "cmd+c",
                "cmd+v",
                "cmd+x",
                "cmd+z",
                "cmd+y",
                "cmd+q",
                "cmd+w",
                "cmd+m",
                "cmd+h",
            }
            return common_reserved.union(mac_reserved)
        elif system == "linux":
            linux_reserved = {"ctrl+alt+t", "ctrl+alt+l", "super"}
            return common_reserved.union(linux_reserved)

        return common_reserved

    def _get_invalid_patterns(self) -> List[str]:
        """Get invalid key sequence patterns."""
        return [
            "ctrl+alt+del",  # System reserved
            "printscreen",  # May not be interceptable
            "scroll lock",  # Hardware specific
            "num lock",  # Hardware specific
        ]


class ConflictResolver:
    """Resolves shortcut conflicts using various strategies."""

    def __init__(self):
        self.logger = get_log_manager().get_logger("ConflictResolver")
        self.resolution_strategies = {
            "priority": self._resolve_by_priority,
            "context": self._resolve_by_context,
            "frequency": self._resolve_by_frequency,
            "manual": self._resolve_manually,
        }

    def resolve_conflict(self, conflict: ShortcutConflict) -> ShortcutConflict:
        """Resolve a shortcut conflict."""
        try:
            strategy = conflict.resolution_strategy
            if strategy in self.resolution_strategies:
                resolver = self.resolution_strategies[strategy]
                conflict = resolver(conflict)
                conflict.auto_resolved = True
            else:
                self.logger.warning(f"Unknown resolution strategy: {strategy}")
                conflict = self._resolve_by_priority(conflict)

            return conflict

        except Exception as e:
            self.logger.error(f"Conflict resolution failed: {e}")
            return conflict

    def _resolve_by_priority(
        self, conflict: ShortcutConflict
    ) -> ShortcutConflict:
        """Resolve conflict by priority level."""
        if conflict.conflicting_shortcuts:
            # Sort by priority (lower enum value = higher priority)
            sorted_shortcuts = sorted(
                conflict.conflicting_shortcuts, key=lambda x: x.priority.value
            )
            conflict.resolved_shortcut = sorted_shortcuts[0]

        return conflict

    def _resolve_by_context(
        self, conflict: ShortcutConflict
    ) -> ShortcutConflict:
        """Resolve conflict by context specificity."""
        if conflict.conflicting_shortcuts:
            # Prefer more specific contexts
            context_priority = {
                ShortcutContext.TOOL_SPECIFIC: 1,
                ShortcutContext.DIALOG: 2,
                ShortcutContext.EDIT_MODE: 3,
                ShortcutContext.PANE_FOCUSED: 4,
                ShortcutContext.FILE_EXPLORER: 5,
                ShortcutContext.MENU: 6,
                ShortcutContext.GLOBAL: 7,
            }

            sorted_shortcuts = sorted(
                conflict.conflicting_shortcuts,
                key=lambda x: context_priority.get(x.context, 99),
            )
            conflict.resolved_shortcut = sorted_shortcuts[0]

        return conflict

    def _resolve_by_frequency(
        self, conflict: ShortcutConflict
    ) -> ShortcutConflict:
        """Resolve conflict by usage frequency (placeholder)."""
        # This would integrate with usage statistics
        return self._resolve_by_priority(conflict)

    def _resolve_manually(
        self, conflict: ShortcutConflict
    ) -> ShortcutConflict:
        """Mark conflict for manual resolution."""
        conflict.auto_resolved = False
        return conflict


class ShortcutRegistry:
    """Central registry for managing shortcuts."""

    def __init__(self):
        self.shortcuts: Dict[str, ShortcutDefinition] = {}
        self.conflicts: List[ShortcutConflict] = []
        self.context_shortcuts: Dict[ShortcutContext, List[str]] = {}
        self.category_shortcuts: Dict[ShortcutCategory, List[str]] = {}
        self.key_sequence_map: Dict[str, List[str]] = (
            {}
        )  # sequence -> shortcut_ids

        self.validator = ShortcutValidator()
        self.conflict_resolver = ConflictResolver()
        self.logger = get_log_manager().get_logger("ShortcutRegistry")
        self._lock = threading.RLock()

    def register_shortcut(self, shortcut: ShortcutDefinition) -> bool:
        """Register a new shortcut."""
        with self._lock:
            try:
                # Validate shortcut
                is_valid, errors = self.validator.validate_shortcut(shortcut)
                if not is_valid:
                    self.logger.error(
                        f"Invalid shortcut {shortcut.id}: {errors}"
                    )
                    return False

                # Check for conflicts
                conflicts = self._check_conflicts(shortcut)
                if conflicts:
                    self._handle_conflicts(shortcut, conflicts)

                # Register shortcut
                self.shortcuts[shortcut.id] = shortcut

                # Update indices
                self._update_indices(shortcut)

                self.logger.info(
                    f"Registered shortcut: {shortcut.id} ({shortcut.key_sequence})"
                )
                return True

            except Exception as e:
                self.logger.error(
                    f"Failed to register shortcut {shortcut.id}: {e}"
                )
                return False

    def unregister_shortcut(self, shortcut_id: str) -> bool:
        """Unregister a shortcut."""
        with self._lock:
            try:
                if shortcut_id in self.shortcuts:
                    shortcut = self.shortcuts[shortcut_id]
                    del self.shortcuts[shortcut_id]

                    # Update indices
                    self._remove_from_indices(shortcut)

                    self.logger.info(f"Unregistered shortcut: {shortcut_id}")
                    return True

                return False

            except Exception as e:
                self.logger.error(
                    f"Failed to unregister shortcut {shortcut_id}: {e}"
                )
                return False

    def get_shortcut(self, shortcut_id: str) -> Optional[ShortcutDefinition]:
        """Get a shortcut by ID."""
        return self.shortcuts.get(shortcut_id)

    def get_shortcuts_by_context(
        self, context: ShortcutContext
    ) -> List[ShortcutDefinition]:
        """Get all shortcuts for a specific context."""
        shortcut_ids = self.context_shortcuts.get(context, [])
        return [
            self.shortcuts[sid]
            for sid in shortcut_ids
            if sid in self.shortcuts
        ]

    def get_shortcuts_by_category(
        self, category: ShortcutCategory
    ) -> List[ShortcutDefinition]:
        """Get all shortcuts for a specific category."""
        shortcut_ids = self.category_shortcuts.get(category, [])
        return [
            self.shortcuts[sid]
            for sid in shortcut_ids
            if sid in self.shortcuts
        ]

    def get_shortcuts_by_sequence(
        self, key_sequence: str
    ) -> List[ShortcutDefinition]:
        """Get all shortcuts using a specific key sequence."""
        shortcut_ids = self.key_sequence_map.get(key_sequence.lower(), [])
        return [
            self.shortcuts[sid]
            for sid in shortcut_ids
            if sid in self.shortcuts
        ]

    def search_shortcuts(self, query: str) -> List[ShortcutDefinition]:
        """Search shortcuts by name, description, or key sequence."""
        query_lower = query.lower()
        results = []

        for shortcut in self.shortcuts.values():
            if (
                query_lower in shortcut.name.lower()
                or query_lower in shortcut.description.lower()
                or query_lower in shortcut.key_sequence.lower()
            ):
                results.append(shortcut)

        return results

    def _check_conflicts(
        self, new_shortcut: ShortcutDefinition
    ) -> List[ShortcutDefinition]:
        """Check for conflicts with existing shortcuts."""
        conflicts = []

        # Check main sequence
        sequence = new_shortcut.get_platform_sequence().lower()
        existing_shortcuts = self.get_shortcuts_by_sequence(sequence)

        for existing in existing_shortcuts:
            if (
                existing.context == new_shortcut.context
                or existing.context == ShortcutContext.GLOBAL
                or new_shortcut.context == ShortcutContext.GLOBAL
            ):
                conflicts.append(existing)

        # Check alternate sequences
        for alt_sequence in new_shortcut.alternate_sequences:
            alt_shortcuts = self.get_shortcuts_by_sequence(
                alt_sequence.lower()
            )
            conflicts.extend(alt_shortcuts)

        return conflicts

    def _handle_conflicts(
        self,
        new_shortcut: ShortcutDefinition,
        conflicting_shortcuts: List[ShortcutDefinition],
    ) -> None:
        """Handle shortcut conflicts."""
        conflict = ShortcutConflict(
            key_sequence=new_shortcut.get_platform_sequence(),
            conflicting_shortcuts=conflicting_shortcuts + [new_shortcut],
            timestamp=time.time(),
        )

        # Resolve conflict
        resolved_conflict = self.conflict_resolver.resolve_conflict(conflict)
        self.conflicts.append(resolved_conflict)

        # Disable conflicting shortcuts if needed
        if resolved_conflict.resolved_shortcut == new_shortcut:
            for conflicting in conflicting_shortcuts:
                conflicting.enabled = False
                self.logger.warning(
                    f"Disabled conflicting shortcut: {conflicting.id}"
                )

    def _update_indices(self, shortcut: ShortcutDefinition) -> None:
        """Update internal indices."""
        # Context index
        context = shortcut.context
        if context not in self.context_shortcuts:
            self.context_shortcuts[context] = []
        self.context_shortcuts[context].append(shortcut.id)

        # Category index
        category = shortcut.category
        if category not in self.category_shortcuts:
            self.category_shortcuts[category] = []
        self.category_shortcuts[category].append(shortcut.id)

        # Key sequence index
        sequence = shortcut.get_platform_sequence().lower()
        if sequence not in self.key_sequence_map:
            self.key_sequence_map[sequence] = []
        self.key_sequence_map[sequence].append(shortcut.id)

        # Add alternate sequences
        for alt_sequence in shortcut.alternate_sequences:
            alt_lower = alt_sequence.lower()
            if alt_lower not in self.key_sequence_map:
                self.key_sequence_map[alt_lower] = []
            self.key_sequence_map[alt_lower].append(shortcut.id)

    def _remove_from_indices(self, shortcut: ShortcutDefinition) -> None:
        """Remove shortcut from internal indices."""
        # Context index
        if shortcut.context in self.context_shortcuts:
            if shortcut.id in self.context_shortcuts[shortcut.context]:
                self.context_shortcuts[shortcut.context].remove(shortcut.id)

        # Category index
        if shortcut.category in self.category_shortcuts:
            if shortcut.id in self.category_shortcuts[shortcut.category]:
                self.category_shortcuts[shortcut.category].remove(shortcut.id)

        # Key sequence index
        sequence = shortcut.get_platform_sequence().lower()
        if sequence in self.key_sequence_map:
            if shortcut.id in self.key_sequence_map[sequence]:
                self.key_sequence_map[sequence].remove(shortcut.id)
            if not self.key_sequence_map[sequence]:
                del self.key_sequence_map[sequence]

        # Remove alternate sequences
        for alt_sequence in shortcut.alternate_sequences:
            alt_lower = alt_sequence.lower()
            if alt_lower in self.key_sequence_map:
                if shortcut.id in self.key_sequence_map[alt_lower]:
                    self.key_sequence_map[alt_lower].remove(shortcut.id)
                if not self.key_sequence_map[alt_lower]:
                    del self.key_sequence_map[alt_lower]

    def get_conflicts(self) -> List[ShortcutConflict]:
        """Get all shortcut conflicts."""
        return self.conflicts.copy()

    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics."""
        return {
            "total_shortcuts": len(self.shortcuts),
            "enabled_shortcuts": len(
                [s for s in self.shortcuts.values() if s.enabled]
            ),
            "contexts": {
                ctx.value: len(shortcuts)
                for ctx, shortcuts in self.context_shortcuts.items()
            },
            "categories": {
                cat.value: len(shortcuts)
                for cat, shortcuts in self.category_shortcuts.items()
            },
            "conflicts": len(self.conflicts),
            "unresolved_conflicts": len(
                [c for c in self.conflicts if not c.auto_resolved]
            ),
            "unique_sequences": len(self.key_sequence_map),
        }


class ShortcutManager(QObject if PYQT_AVAILABLE else object):
    """Main shortcut management system."""

    if PYQT_AVAILABLE:
        shortcut_activated = pyqtSignal(str, str)  # shortcut_id, key_sequence
        shortcut_registered = pyqtSignal(str)  # shortcut_id
        shortcut_unregistered = pyqtSignal(str)  # shortcut_id
        conflict_detected = pyqtSignal(
            str, list
        )  # key_sequence, conflicting_ids

    def __init__(self):
        if PYQT_AVAILABLE:
            super().__init__()

        self.registry = ShortcutRegistry()
        self.logger = get_log_manager().get_logger("ShortcutManager")

        # Qt integration
        self.qt_shortcuts: Dict[str, QShortcut] = {}
        self.qt_actions: Dict[str, QAction] = {}

        # Configuration
        self.config = self._load_configuration()

        # Context tracking
        self.current_context = ShortcutContext.GLOBAL
        self.context_stack: List[ShortcutContext] = []

        # Initialize default shortcuts
        self._initialize_default_shortcuts()

        # Load user shortcuts
        self._load_user_shortcuts()

    def _load_configuration(self) -> Dict[str, Any]:
        """Load shortcut configuration."""
        default_config = {
            "enabled": True,
            "enable_tooltips": True,
            "enable_conflicts_auto_resolution": True,
            "save_user_shortcuts": True,
            "backup_shortcuts": True,
            "default_context": ShortcutContext.GLOBAL.value,
            "conflict_resolution_strategy": "priority",
        }

        if ConfigManager:
            try:
                config_manager = ConfigManager()
                user_config = config_manager.get_setting(
                    "shortcuts", "configuration", {}
                )
                return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(
                    f"Failed to load shortcut configuration: {e}"
                )

        return default_config

    def register_shortcut(
        self,
        shortcut_id: str,
        name: str,
        key_sequence: str,
        callback: Callable,
        **kwargs,
    ) -> bool:
        """Register a new shortcut."""
        try:
            # Create shortcut definition
            shortcut = ShortcutDefinition(
                id=shortcut_id,
                name=name,
                description=kwargs.get("description", name),
                key_sequence=key_sequence,
                callback=callback,
                context=kwargs.get("context", ShortcutContext.GLOBAL),
                category=kwargs.get("category", ShortcutCategory.CUSTOM),
                priority=kwargs.get("priority", ShortcutPriority.DEFAULT),
                enabled=kwargs.get("enabled", True),
                visible=kwargs.get("visible", True),
                tooltip=kwargs.get("tooltip", ""),
                icon=kwargs.get("icon"),
                alternate_sequences=kwargs.get("alternate_sequences", []),
                platform_specific=kwargs.get("platform_specific", {}),
                requires_confirmation=kwargs.get(
                    "requires_confirmation", False
                ),
                metadata=kwargs.get("metadata", {}),
            )

            # Register in registry
            if not self.registry.register_shortcut(shortcut):
                return False

            # Create Qt shortcut if available
            if PYQT_AVAILABLE and callback:
                self._create_qt_shortcut(shortcut)

            # Emit signal
            if PYQT_AVAILABLE:
                self.shortcut_registered.emit(shortcut_id)

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to register shortcut {shortcut_id}: {e}"
            )
            return False

    def unregister_shortcut(self, shortcut_id: str) -> bool:
        """Unregister a shortcut."""
        try:
            # Remove Qt shortcut
            if shortcut_id in self.qt_shortcuts:
                self.qt_shortcuts[shortcut_id].setEnabled(False)
                del self.qt_shortcuts[shortcut_id]

            if shortcut_id in self.qt_actions:
                del self.qt_actions[shortcut_id]

            # Unregister from registry
            success = self.registry.unregister_shortcut(shortcut_id)

            # Emit signal
            if PYQT_AVAILABLE and success:
                self.shortcut_unregistered.emit(shortcut_id)

            return success

        except Exception as e:
            self.logger.error(
                f"Failed to unregister shortcut {shortcut_id}: {e}"
            )
            return False

    def _create_qt_shortcut(self, shortcut: ShortcutDefinition) -> None:
        """Create Qt shortcut widget."""
        if not PYQT_AVAILABLE:
            return

        try:
            # Get parent widget
            app = QApplication.instance()
            if not app:
                return

            parent = app.activeWindow() or app.focusWidget()
            if not parent:
                return

            # Create QShortcut
            qt_shortcut = QShortcut(
                QKeySequence(shortcut.get_platform_sequence()), parent
            )

            # Connect to callback
            def shortcut_activated():
                try:
                    if shortcut.enabled and shortcut.callback:
                        # Handle confirmation if required
                        if shortcut.requires_confirmation:
                            if not self._confirm_shortcut_execution(shortcut):
                                return

                        # Execute callback
                        shortcut.callback()

                        # Emit signal
                        self.shortcut_activated.emit(
                            shortcut.id, shortcut.get_platform_sequence()
                        )

                except Exception as e:
                    self.logger.error(
                        f"Shortcut execution failed {shortcut.id}: {e}"
                    )

            qt_shortcut.activated.connect(shortcut_activated)
            qt_shortcut.setEnabled(shortcut.enabled)

            # Store reference
            self.qt_shortcuts[shortcut.id] = qt_shortcut

            # Create QAction for menu integration
            action = QAction(shortcut.name, parent)
            action.setShortcut(QKeySequence(shortcut.get_platform_sequence()))
            action.setToolTip(shortcut.tooltip or shortcut.description)
            action.setEnabled(shortcut.enabled)
            action.setVisible(shortcut.visible)

            if shortcut.icon:
                # Set icon if available
                icon_path = Path(shortcut.icon)
                if icon_path.exists():
                    from PyQt5.QtGui import QIcon

                    action.setIcon(QIcon(str(icon_path)))

            action.triggered.connect(shortcut_activated)
            self.qt_actions[shortcut.id] = action

        except Exception as e:
            self.logger.error(
                f"Failed to create Qt shortcut for {shortcut.id}: {e}"
            )

    def _confirm_shortcut_execution(
        self, shortcut: ShortcutDefinition
    ) -> bool:
        """Show confirmation dialog for shortcut execution."""
        if not PYQT_AVAILABLE:
            return True

        try:
            from PyQt5.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                None,
                "Confirm Action",
                f"Execute {shortcut.name}?\n\n{shortcut.description}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            return reply == QMessageBox.Yes

        except Exception as e:
            self.logger.error(f"Confirmation dialog failed: {e}")
            return False

    def set_context(self, context: ShortcutContext) -> None:
        """Set current shortcut context."""
        self.current_context = context
        self.logger.debug(f"Context changed to: {context.value}")

    def push_context(self, context: ShortcutContext) -> None:
        """Push context onto stack."""
        self.context_stack.append(self.current_context)
        self.current_context = context
        self.logger.debug(f"Context pushed: {context.value}")

    def pop_context(self) -> None:
        """Pop context from stack."""
        if self.context_stack:
            self.current_context = self.context_stack.pop()
            self.logger.debug(
                f"Context popped to: {self.current_context.value}"
            )

    def get_shortcuts_for_current_context(self) -> List[ShortcutDefinition]:
        """Get shortcuts applicable to current context."""
        context_shortcuts = self.registry.get_shortcuts_by_context(
            self.current_context
        )
        global_shortcuts = self.registry.get_shortcuts_by_context(
            ShortcutContext.GLOBAL
        )

        # Combine and deduplicate
        all_shortcuts = context_shortcuts + global_shortcuts
        unique_shortcuts = {s.id: s for s in all_shortcuts}

        return list(unique_shortcuts.values())

    def _initialize_default_shortcuts(self) -> None:
        """Initialize default application shortcuts."""
        default_shortcuts = [
            # Navigation shortcuts
            {
                "id": "nav_back",
                "name": "Go Back",
                "key_sequence": "Alt+Left",
                "callback": lambda: self.logger.info("Go back"),
                "category": ShortcutCategory.NAVIGATION,
                "description": "Navigate back in history",
            },
            {
                "id": "nav_forward",
                "name": "Go Forward",
                "key_sequence": "Alt+Right",
                "callback": lambda: self.logger.info("Go forward"),
                "category": ShortcutCategory.NAVIGATION,
                "description": "Navigate forward in history",
            },
            {
                "id": "nav_up",
                "name": "Go Up",
                "key_sequence": "Alt+Up",
                "callback": lambda: self.logger.info("Go up"),
                "category": ShortcutCategory.NAVIGATION,
                "description": "Navigate to parent directory",
            },
            # File operation shortcuts
            {
                "id": "file_copy",
                "name": "Copy Files",
                "key_sequence": "Ctrl+C",
                "callback": lambda: self.logger.info("Copy files"),
                "category": ShortcutCategory.FILE_OPERATIONS,
                "description": "Copy selected files",
            },
            {
                "id": "file_cut",
                "name": "Cut Files",
                "key_sequence": "Ctrl+X",
                "callback": lambda: self.logger.info("Cut files"),
                "category": ShortcutCategory.FILE_OPERATIONS,
                "description": "Cut selected files",
            },
            {
                "id": "file_paste",
                "name": "Paste Files",
                "key_sequence": "Ctrl+V",
                "callback": lambda: self.logger.info("Paste files"),
                "category": ShortcutCategory.FILE_OPERATIONS,
                "description": "Paste files from clipboard",
            },
            {
                "id": "file_delete",
                "name": "Delete Files",
                "key_sequence": "Delete",
                "callback": lambda: self.logger.info("Delete files"),
                "category": ShortcutCategory.FILE_OPERATIONS,
                "description": "Delete selected files",
                "requires_confirmation": True,
            },
            # Tool launch shortcuts
            {
                "id": "tool_file_finder",
                "name": "File Finder",
                "key_sequence": "Ctrl+F",
                "callback": lambda: self.logger.info("Launch File Finder"),
                "category": ShortcutCategory.TOOL_LAUNCH,
                "description": "Launch File Finder tool",
            },
            {
                "id": "tool_duplicate_finder",
                "name": "Duplicate Finder",
                "key_sequence": "Ctrl+D",
                "callback": lambda: self.logger.info(
                    "Launch Duplicate Finder"
                ),
                "category": ShortcutCategory.TOOL_LAUNCH,
                "description": "Launch Duplicate Finder tool",
            },
            # View control shortcuts
            {
                "id": "view_refresh",
                "name": "Refresh",
                "key_sequence": "F5",
                "callback": lambda: self.logger.info("Refresh view"),
                "category": ShortcutCategory.VIEW_CONTROL,
                "description": "Refresh current view",
            },
            {
                "id": "view_toggle_pane_count",
                "name": "Toggle Pane Count",
                "key_sequence": "Ctrl+1",
                "callback": lambda: self.logger.info("Toggle pane count"),
                "category": ShortcutCategory.VIEW_CONTROL,
                "description": "Cycle through pane configurations",
            },
        ]

        for shortcut_def in default_shortcuts:
            try:
                self.register_shortcut(**shortcut_def)
            except Exception as e:
                self.logger.error(f"Failed to register default shortcut: {e}")

    def _load_user_shortcuts(self) -> None:
        """Load user-defined shortcuts from configuration."""
        if not self.config.get("save_user_shortcuts", True):
            return

        try:
            if ConfigManager:
                config_manager = ConfigManager()
                user_shortcuts = config_manager.get_setting(
                    "shortcuts", "user_shortcuts", {}
                )

                for shortcut_id, shortcut_data in user_shortcuts.items():
                    try:
                        # Reconstruct shortcut definition
                        shortcut = ShortcutDefinition(
                            id=shortcut_id,
                            name=shortcut_data["name"],
                            description=shortcut_data.get("description", ""),
                            key_sequence=shortcut_data["key_sequence"],
                            context=ShortcutContext(
                                shortcut_data.get("context", "global")
                            ),
                            category=ShortcutCategory(
                                shortcut_data.get("category", "custom")
                            ),
                            priority=ShortcutPriority(
                                shortcut_data.get("priority", "default")
                            ),
                            enabled=shortcut_data.get("enabled", True),
                            visible=shortcut_data.get("visible", True),
                            tooltip=shortcut_data.get("tooltip", ""),
                            alternate_sequences=shortcut_data.get(
                                "alternate_sequences", []
                            ),
                            platform_specific=shortcut_data.get(
                                "platform_specific", {}
                            ),
                            requires_confirmation=shortcut_data.get(
                                "requires_confirmation", False
                            ),
                            metadata=shortcut_data.get("metadata", {}),
                        )

                        self.registry.register_shortcut(shortcut)

                    except Exception as e:
                        self.logger.error(
                            f"Failed to load user shortcut {shortcut_id}: {e}"
                        )

        except Exception as e:
            self.logger.error(f"Failed to load user shortcuts: {e}")

    def save_user_shortcuts(self) -> bool:
        """Save user-defined shortcuts to configuration."""
        if not self.config.get("save_user_shortcuts", True):
            return True

        try:
            # Filter user-defined shortcuts
            user_shortcuts = {}
            for shortcut_id, shortcut in self.registry.shortcuts.items():
                if (
                    shortcut.priority == ShortcutPriority.USER
                    or shortcut.category == ShortcutCategory.CUSTOM
                ):

                    user_shortcuts[shortcut_id] = {
                        "name": shortcut.name,
                        "description": shortcut.description,
                        "key_sequence": shortcut.key_sequence,
                        "context": shortcut.context.value,
                        "category": shortcut.category.value,
                        "priority": shortcut.priority.value,
                        "enabled": shortcut.enabled,
                        "visible": shortcut.visible,
                        "tooltip": shortcut.tooltip,
                        "alternate_sequences": shortcut.alternate_sequences,
                        "platform_specific": shortcut.platform_specific,
                        "requires_confirmation": shortcut.requires_confirmation,
                        "metadata": shortcut.metadata,
                    }

            # Save to configuration
            if ConfigManager:
                config_manager = ConfigManager()
                config_manager.set_setting(
                    "shortcuts", "user_shortcuts", user_shortcuts
                )
                config_manager.save_config()

                self.logger.info(f"Saved {len(user_shortcuts)} user shortcuts")
                return True

        except Exception as e:
            self.logger.error(f"Failed to save user shortcuts: {e}")

        return False

    def export_shortcuts(self, file_path: Path) -> bool:
        """Export shortcuts to JSON file."""
        try:
            export_data = {
                "version": "1.0.0",
                "exported_at": time.time(),
                "shortcuts": {},
            }

            for shortcut_id, shortcut in self.registry.shortcuts.items():
                export_data["shortcuts"][shortcut_id] = {
                    "name": shortcut.name,
                    "description": shortcut.description,
                    "key_sequence": shortcut.key_sequence,
                    "context": shortcut.context.value,
                    "category": shortcut.category.value,
                    "priority": shortcut.priority.value,
                    "enabled": shortcut.enabled,
                    "visible": shortcut.visible,
                    "tooltip": shortcut.tooltip,
                    "alternate_sequences": shortcut.alternate_sequences,
                    "platform_specific": shortcut.platform_specific,
                    "requires_confirmation": shortcut.requires_confirmation,
                    "metadata": shortcut.metadata,
                }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Exported shortcuts to: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export shortcuts: {e}")
            return False

    def import_shortcuts(self, file_path: Path, merge: bool = True) -> bool:
        """Import shortcuts from JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            if not merge:
                # Clear existing shortcuts
                for shortcut_id in list(self.registry.shortcuts.keys()):
                    self.unregister_shortcut(shortcut_id)

            imported_count = 0
            for shortcut_id, shortcut_data in import_data.get(
                "shortcuts", {}
            ).items():
                try:
                    # Create shortcut definition
                    shortcut = ShortcutDefinition(
                        id=shortcut_id,
                        name=shortcut_data["name"],
                        description=shortcut_data.get("description", ""),
                        key_sequence=shortcut_data["key_sequence"],
                        context=ShortcutContext(
                            shortcut_data.get("context", "global")
                        ),
                        category=ShortcutCategory(
                            shortcut_data.get("category", "custom")
                        ),
                        priority=ShortcutPriority(
                            shortcut_data.get("priority", "user")
                        ),
                        enabled=shortcut_data.get("enabled", True),
                        visible=shortcut_data.get("visible", True),
                        tooltip=shortcut_data.get("tooltip", ""),
                        alternate_sequences=shortcut_data.get(
                            "alternate_sequences", []
                        ),
                        platform_specific=shortcut_data.get(
                            "platform_specific", {}
                        ),
                        requires_confirmation=shortcut_data.get(
                            "requires_confirmation", False
                        ),
                        metadata=shortcut_data.get("metadata", {}),
                    )

                    if self.registry.register_shortcut(shortcut):
                        imported_count += 1

                except Exception as e:
                    self.logger.error(
                        f"Failed to import shortcut {shortcut_id}: {e}"
                    )

            self.logger.info(
                f"Imported {imported_count} shortcuts from: {file_path}"
            )
            return imported_count > 0

        except Exception as e:
            self.logger.error(f"Failed to import shortcuts: {e}")
            return False

    def get_shortcut_statistics(self) -> Dict[str, Any]:
        """Get comprehensive shortcut statistics."""
        stats = self.registry.get_registry_statistics()

        # Add manager-specific statistics
        stats.update(
            {
                "qt_shortcuts": len(self.qt_shortcuts),
                "qt_actions": len(self.qt_actions),
                "current_context": self.current_context.value,
                "context_stack_depth": len(self.context_stack),
                "configuration": self.config.copy(),
            }
        )

        return stats

    def shutdown(self) -> None:
        """Shutdown the shortcut manager."""
        try:
            # Save user shortcuts
            self.save_user_shortcuts()

            # Cleanup Qt shortcuts
            for qt_shortcut in self.qt_shortcuts.values():
                qt_shortcut.setEnabled(False)

            self.qt_shortcuts.clear()
            self.qt_actions.clear()

            self.logger.info("Shortcut manager shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shortcut manager shutdown: {e}")


# Global instance for application-wide access
_shortcut_manager = None


def get_shortcut_manager() -> ShortcutManager:
    """Get the global shortcut manager instance."""
    global _shortcut_manager
    if _shortcut_manager is None:
        _shortcut_manager = ShortcutManager()
    return _shortcut_manager
