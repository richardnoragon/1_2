#!/usr/bin/env python3
"""
Richard's File Utilities - Main Entry Point with Dual Interface System

This is the main entry point for the Richard's File Utilities application.
It provides a comprehensive GUI interface with dual interface modes:
- Dialog-Based Hub Interface (tabbed)
- Multi-Pane Explorer Layout

Enhanced with interface mode switching, workflow analysis, and accessibility features.
"""

import importlib
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "scripts", "maintenance"))
sys.path.insert(0, os.path.join(project_root, "scripts", "development", "demos"))

# Import constants for string literals
from src.core.constants import (
    APP_NAME,
    IMPORT_ERROR,
    JSON_FILES_FILTER,
    SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER,
)
from src.core.application_state import build_application_state
from src.core.tool_lifecycle import resolve_tool_launch_request

# PDF tool constants
PDF_UTILITIES = "PDF Utilities"
EXTRACT_LINKS = "Extract Links"
PAGE_ADMINISTRATION = "Page Administration"

# Tool launch constants
TOOL_LAUNCH_ERROR = "Tool Launch Error"
INTERFACE_SELECTION = "Interface Selection"
DEFAULT_INTERFACE = "Use Default Interface"
USE_DEFAULT_INTERFACE = "Use Default Interface"


# Interface mode definitions
class InterfaceMode(Enum):
    """Enumeration for interface modes.

    NOTE: MULTI_PANE mode has been removed. Only DIALOG_HUB (tabbed) is available.
    """

    DIALOG_HUB = "dialog_hub"
    # MULTI_PANE removed - file_explorer module has been deleted


class WorkflowPattern(Enum):
    """Enumeration for detected workflow patterns."""

    FILE_MANAGEMENT = "file_management"
    BATCH_OPERATIONS = "batch_operations"
    DEVELOPMENT = "development"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    SYSTEM_MAINTENANCE = "system_maintenance"


class AuthenticationCancelledError(RuntimeError):
    """Raised when the user dismisses the login gate without authenticating."""

    pass


# Startup-performance optimization: defer expensive optional services until they are actually needed.
DATABASE_AVAILABLE = False
_ENHANCED_PDF_TOOLS_AVAILABLE = None
_DATABASE_INITIALIZATION_ATTEMPTED = False


def initialize_database_system():
    """Compatibility wrapper for legacy callers.

    Startup work is lazy and should be requested by the main window or a tool that
    explicitly needs database-backed features. The default import path is intentionally
    fast and does not initialize this subsystem.
    """
    return ensure_database_initialized(force=True)


def ensure_database_initialized(*, force: bool = False):
    """Initialize the database only when the app actually needs it."""
    global DATABASE_AVAILABLE, _DATABASE_INITIALIZATION_ATTEMPTED

    if not force and _DATABASE_INITIALIZATION_ATTEMPTED:
        return DATABASE_AVAILABLE

    _DATABASE_INITIALIZATION_ATTEMPTED = True
    logger = logging.getLogger("RFU.Main")
    db_manager = None

    try:
        logger.info("Attempting database initialization on demand")
        from scripts.maintenance.standalone_database_manager import get_database_manager

        db_manager = get_database_manager()
        if db_manager is None:
            logger.warning("Database manager initialization returned None")
            DATABASE_AVAILABLE = False
            return False

        db_info = db_manager.get_database_info()
        if not db_info or "database_file" not in db_info:
            logger.error("Database connectivity test failed")
            DATABASE_AVAILABLE = False
            return False

        DATABASE_AVAILABLE = True
        logger.info("Database system initialized successfully")
        logger.info("Database: %s", db_info.get("database_file"))
        return True
    except ImportError as exc:
        logger.warning("Database module import failed: %s", exc)
    except (RuntimeError, OSError, AttributeError) as exc:
        logger.warning("Database manager initialization failed: %s", exc)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("Database system initialization failed unexpectedly: %s", exc)

    DATABASE_AVAILABLE = False
    return False


def is_enhanced_pdf_tools_available(*, force: bool = False):
    """Create the enhanced PDF widget lazily so launch cost is paid only on demand."""
    global _ENHANCED_PDF_TOOLS_AVAILABLE

    if _ENHANCED_PDF_TOOLS_AVAILABLE is not None and not force:
        return _ENHANCED_PDF_TOOLS_AVAILABLE

    try:
        from scripts.development.demos.enhanced_pdf_tools_widget import (
            EnhancedPDFToolsWidget,
        )
        _ENHANCED_PDF_TOOLS_AVAILABLE = bool(EnhancedPDFToolsWidget)
        return True
    except Exception as exc:  # pragma: no cover - optional feature
        print(f"Enhanced PDF Tools not available: {exc}")
        _ENHANCED_PDF_TOOLS_AVAILABLE = False
        return False


def load_enhanced_pdf_tools_widget():
    """Return the optional PDF widget class when the subsystem is actually requested."""
    from scripts.development.demos.enhanced_pdf_tools_widget import EnhancedPDFToolsWidget

    return EnhancedPDFToolsWidget


MULTI_PANE_EXPLORER_AVAILABLE = False


# Enhanced Interface selection dialog with comprehensive startup functionality
class InterfaceSelectionDialog:
    """Enhanced modal dialog for selecting interface mode on startup with comprehensive styling and error handling."""

    def __init__(self, parent=None):
        self.parent = parent
        self.selected_mode = InterfaceMode.DIALOG_HUB
        self.remember_choice = False
        self.workflow_detected = None
        self.dialog = None
        self.dialog_radio = None
        self.pane_radio = None
        self.remember_checkbox = None

        # Initialize logging for dialog operations
        self.logger = logging.getLogger("RFU.InterfaceDialog")

    def show_selection_dialog(self):
        """Show comprehensive modal interface selection dialog with enhanced styling and error handling."""
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
            from PyQt5.QtWidgets import (
                QButtonGroup,
                QCheckBox,
                QDialog,
                QFrame,
                QGroupBox,
                QHBoxLayout,
                QLabel,
                QPushButton,
                QRadioButton,
                QSizePolicy,
                QSpacerItem,
                QTextEdit,
                QVBoxLayout,
            )

            # Create modal dialog with enhanced properties
            self.dialog = QDialog(self.parent)
            self.dialog.setWindowTitle(
                "Choose Your Workspace Interface - Richard's File Utilities"
            )
            self.dialog.setModal(True)
            self.dialog.setWindowFlags(
                Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
            )

            # Prevent closing without selection
            self.dialog.closeEvent = self._handle_close_event

            # Apply comprehensive styling first
            self._apply_dialog_styling()

            # Create main layout for dialog
            main_layout = QVBoxLayout(self.dialog)
            main_layout.setContentsMargins(10, 10, 10, 10)

            # Create scroll area for content
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import QScrollArea

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # Create content widget
            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)
            layout.setSpacing(10)
            layout.setContentsMargins(15, 15, 15, 15)

            # Enhanced title section with branding
            title_frame = self._create_title_section()
            layout.addWidget(title_frame)

            # Workflow detection and recommendation section
            recommendation_frame = self._create_recommendation_section()
            layout.addWidget(recommendation_frame)

            # Interface selection section with enhanced styling
            selection_frame = self._create_selection_section()
            layout.addWidget(selection_frame)

            # Settings and preferences section
            preferences_frame = self._create_preferences_section()
            layout.addWidget(preferences_frame)

            # Enhanced button section
            button_frame = self._create_button_section()
            layout.addWidget(button_frame)

            # Set content widget to scroll area and add to main layout
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)

            # Get screen geometry for proper sizing
            from PyQt5.QtWidgets import QApplication, QDesktopWidget

            desktop = QApplication.desktop()
            screen_geometry = desktop.screenGeometry()

            # Calculate appropriate dialog size (35% of screen width, max 600px)
            dialog_width = min(600, int(screen_geometry.width() * 0.35))
            dialog_height = min(500, int(screen_geometry.height() * 0.5))

            # Ensure minimum readable size but keep it smaller
            dialog_width = max(dialog_width, 480)
            dialog_height = max(dialog_height, 420)

            # Set dialog size but allow proper resizing
            self.dialog.resize(dialog_width, dialog_height)
            self.dialog.adjustSize()

            # Center dialog on screen
            if self.parent:
                parent_center_x = self.parent.x() + (self.parent.width() // 2)
                parent_center_y = self.parent.y() + (self.parent.height() // 2)
                self.dialog.move(
                    parent_center_x - (dialog_width // 2),
                    parent_center_y - (dialog_height // 2),
                )
            else:
                # Center on screen if no parent
                screen_center_x = screen_geometry.width() // 2
                screen_center_y = screen_geometry.height() // 2
                self.dialog.move(
                    screen_center_x - (dialog_width // 2),
                    screen_center_y - (dialog_height // 2),
                )

            # Show dialog and handle result with comprehensive error handling
            return self._execute_dialog()

        except Exception as e:
            self.logger.error(f"Error creating interface selection dialog: {e}")
            self._show_fallback_dialog()
            return True  # Default to continuing with fallback

    def _apply_dialog_styling(self):
        """Apply token-based shared styling for accessibility consistency."""
        try:
            from src.gui.common.settings import AppearanceSettings
            from src.gui.common.styles import get_base_styles, get_theme_tokens

            appearance = AppearanceSettings()
            colors = get_theme_tokens(appearance.theme)
            base = get_base_styles(
                theme=appearance.theme,
                font_size=appearance.font_size,
            )
            self.dialog.setStyleSheet(
                base
                + f"""
                QDialog {{
                    border: 1px solid {colors['border']};
                    border-radius: 12px;
                }}
                QFrame#hero_section {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors['primary']}, stop:1 {colors['primary_hover']});
                    border-radius: 10px;
                }}
                QLabel#hero_title {{
                    color: {colors['text_on_primary']};
                    font-size: {appearance.font_size + 4}pt;
                    font-weight: 700;
                    margin: 8px;
                }}
                QLabel#hero_subtitle {{
                    color: {colors['text_on_primary']};
                    font-size: {max(10, appearance.font_size - 1)}pt;
                    margin: 4px;
                }}
                QFrame#interface_option {{
                    border: 1px solid {colors['border']};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 3px;
                    background-color: {colors['widget_bg']};
                }}
                QFrame#interface_option:hover {{
                    border-color: {colors['primary']};
                    background-color: {colors['surface_subtle']};
                }}
                QLabel#option_description {{
                    margin-left: 20px;
                    color: {colors['text_secondary']};
                    font-size: {max(9, appearance.font_size - 2)}pt;
                    line-height: 1.3;
                    padding-top: 2px;
                }}
                QLabel#recommendation_title {{
                    color: {colors['success']};
                    font-size: {appearance.font_size}pt;
                    font-weight: 700;
                    margin: 4px;
                }}
                QLabel#recommendation_fallback {{
                    color: {colors['warning']};
                    font-size: {appearance.font_size}pt;
                    font-weight: 600;
                    margin: 4px;
                }}
                QPushButton#secondary {{
                    background-color: {colors['surface_subtle']};
                    border-color: {colors['border']};
                    color: {colors['text']};
                }}
                QPushButton#secondary:hover {{
                    background-color: {colors['highlight']};
                }}
                """
            )
            self.dialog.setAccessibleName("Interface selection dialog")
            self.dialog.setAccessibleDescription(
                "Choose the startup interface mode and confirm preferences"
            )
        except Exception as e:
            self.logger.warning(f"Failed to apply dialog styling: {e}")

    def _create_title_section(self):
        """Create enhanced title section with branding."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

        frame = QFrame()
        frame.setObjectName("hero_section")

        layout = QVBoxLayout(frame)

        # Main title
        title = QLabel("Welcome to Richard's File Utilities")
        title.setObjectName("hero_title")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAccessibleName("Welcome title")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Choose your preferred interface mode to get started")
        subtitle.setObjectName("hero_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setAccessibleName("Welcome subtitle")
        layout.addWidget(subtitle)

        return frame

    def _create_recommendation_section(self):
        """Create workflow detection and recommendation section."""
        from PyQt5.QtWidgets import QGroupBox, QLabel, QTextEdit, QVBoxLayout

        workflow_group = QGroupBox("📊 Intelligent Interface Recommendation")
        workflow_layout = QVBoxLayout(workflow_group)

        try:
            detected_workflow = self._detect_initial_workflow()
            recommendation = self._get_interface_recommendation(detected_workflow)

            recommendation_label = QLabel(f"🎯 Recommended: {recommendation['name']}")
            recommendation_label.setObjectName("recommendation_title")
            recommendation_label.setAccessibleName("Interface recommendation")
            workflow_layout.addWidget(recommendation_label)

            reason_text = QTextEdit()
            reason_text.setPlainText(recommendation["reason"])
            reason_text.setMaximumHeight(60)
            reason_text.setReadOnly(True)
            reason_text.setAccessibleName("Recommendation reasoning")
            workflow_layout.addWidget(reason_text)

        except Exception as e:
            self.logger.warning(f"Error creating recommendation section: {e}")
            fallback_label = QLabel(
                "💡 Both interfaces are powerful - choose based on your workflow preference"
            )
            fallback_label.setObjectName("recommendation_fallback")
            fallback_label.setAccessibleName("Recommendation fallback")
            workflow_layout.addWidget(fallback_label)

        return workflow_group

    def _create_selection_section(self):
        """Create interface selection section.

        NOTE: Multi-pane option has been removed. Only tabbed interface
        is now available after login.
        """
        from PyQt5.QtWidgets import (
            QButtonGroup,
            QFrame,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QRadioButton,
            QVBoxLayout,
        )

        selection_group = QGroupBox("🖥️ Interface Mode")
        selection_layout = QVBoxLayout(selection_group)

        # Create button group for mutual exclusion
        self.button_group = QButtonGroup()

        # Only Dialog Hub (tabbed) option available
        dialog_frame = self._create_interface_option(
            "dialog_hub",
            "📋 Tabbed Hub Interface",
            "• Comprehensive tabbed interface\n"
            "• All tools organized by category\n"
            "• Professional workflow design",
            "#3498db",
        )
        selection_layout.addWidget(dialog_frame)

        # Multi-pane removed - no longer available
        self.pane_radio = None

        return selection_group

    def _create_interface_option(self, option_id, title, description, color):
        """Create a styled interface option frame."""
        from PyQt5.QtWidgets import QFrame, QLabel, QRadioButton, QVBoxLayout

        frame = QFrame()
        frame.setObjectName("interface_option")

        layout = QVBoxLayout(frame)

        # Radio button with enhanced styling
        radio = QRadioButton(title)

        # Ensure text is set and visible
        radio.setText(title)
        radio.setAccessibleName(f"Interface option {title}")
        radio.setAccessibleDescription(
            f"Preferred accent {color} for this interface option"
        )

        if option_id == "dialog_hub":
            self.dialog_radio = radio
            radio.setChecked(True)  # Default selection
        else:
            self.pane_radio = radio

        self.button_group.addButton(radio)
        layout.addWidget(radio)

        # Description with better spacing
        desc_label = QLabel(description)
        desc_label.setObjectName("option_description")
        desc_label.setWordWrap(True)
        desc_label.setAccessibleName("Interface option description")
        layout.addWidget(desc_label)

        return frame

    def _create_preferences_section(self):
        """Create preferences and settings section."""
        from PyQt5.QtWidgets import QCheckBox, QFrame, QLabel, QVBoxLayout

        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Remember choice checkbox
        self.remember_checkbox = QCheckBox("🔒 Remember my choice for future sessions")
        self.remember_checkbox.setChecked(True)
        self.remember_checkbox.setAccessibleName("Remember interface choice")
        layout.addWidget(self.remember_checkbox)

        # Additional info
        info_label = QLabel(
            "💡 You can always change your interface mode from the Interface menu"
        )
        info_label.setObjectName("option_description")
        info_label.setAccessibleName("Interface menu hint")
        layout.addWidget(info_label)

        return frame

    def _create_button_section(self):
        """Create enhanced button section with proper styling."""
        from PyQt5.QtWidgets import (
            QFrame,
            QHBoxLayout,
            QPushButton,
            QSizePolicy,
            QSpacerItem,
        )

        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Add spacer
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("secondary")
        cancel_button.setText("Cancel")
        cancel_button.setMinimumSize(80, 30)
        cancel_button.setAccessibleName("Cancel interface selection")
        cancel_button.clicked.connect(self._handle_cancel)
        layout.addWidget(cancel_button)

        # Continue button
        continue_button = QPushButton("Continue")
        continue_button.setObjectName("primary")
        continue_button.setText("Continue")
        continue_button.setMinimumSize(80, 30)
        continue_button.setAccessibleName("Confirm interface selection")
        continue_button.setDefault(True)
        continue_button.clicked.connect(self._handle_continue)
        layout.addWidget(continue_button)

        return frame

    def _execute_dialog(self):
        """Execute the dialog with comprehensive error handling."""
        try:
            # Ensure proper layout before showing
            self.dialog.updateGeometry()
            self.dialog.update()
            self.dialog.repaint()

            # Process events to ensure proper rendering
            from PyQt5.QtWidgets import QApplication

            QApplication.processEvents()

            result = self.dialog.exec_()

            if result == self.dialog.Accepted:
                # Process user selection - only tabbed interface available
                self.selected_mode = InterfaceMode.DIALOG_HUB

                if self.remember_checkbox:
                    self.remember_choice = self.remember_checkbox.isChecked()
                else:
                    self.remember_choice = False

                self.logger.info(
                    f"User selected interface mode: {self.selected_mode.value}"
                )
                return True
            else:
                # User cancelled - still use tabbed interface
                self.logger.info("User cancelled, using default tabbed interface")
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                return False  # User cancelled

        except Exception as e:
            self.logger.error(f"Error executing interface selection dialog: {e}")
            self._show_fallback_dialog()
            return False  # Error occurred

    def _handle_continue(self):
        """Handle continue button click."""
        try:
            # Only tabbed interface available - always accept
            self.dialog.accept()

        except Exception as e:
            self.logger.error(f"Error handling continue action: {e}")
            self.dialog.accept()  # Continue anyway

    def _handle_cancel(self):
        """Handle cancel button click - still uses tabbed interface."""
        try:
            from PyQt5.QtWidgets import QMessageBox

            result = QMessageBox.question(
                self.dialog,
                USE_DEFAULT_INTERFACE,
                "Continue with the Tabbed Hub interface?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if result == QMessageBox.Yes:
                self.logger.info("User chose default interface mode")
                # Set default values and accept dialog
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                if self.dialog_radio:
                    self.dialog_radio.setChecked(True)
                if self.remember_checkbox:
                    self.remember_checkbox.setChecked(False)
                self.dialog.accept()
            else:
                # User chose not to use default, stay in dialog
                self.logger.info("User declined default interface, staying in dialog")

        except Exception as e:
            self.logger.error(f"Error handling cancel action: {e}")
            # Fallback to default interface and continue
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
            self.dialog.accept()

    def _handle_close_event(self, event):
        """Handle dialog close event to prevent accidental closure."""
        try:
            from PyQt5.QtWidgets import QMessageBox

            result = QMessageBox.question(
                self.dialog,
                USE_DEFAULT_INTERFACE,
                "Would you like to use the default Dialog Hub interface?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if result == QMessageBox.Yes:
                self.logger.info("User chose default interface from close event")
                # Set default values and accept dialog
                self.selected_mode = InterfaceMode.DIALOG_HUB
                self.remember_choice = False
                if self.dialog_radio:
                    self.dialog_radio.setChecked(True)
                if self.remember_checkbox:
                    self.remember_checkbox.setChecked(False)
                event.accept()
                self.dialog.accept()
            else:
                # User chose not to use default, prevent close
                self.logger.info(
                    "User declined default interface, preventing dialog close"
                )
                event.ignore()

        except Exception as e:
            self.logger.error(f"Error handling close event: {e}")
            # Fallback to default interface and continue
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False
            event.accept()
            self.dialog.accept()

    def _show_fallback_dialog(self):
        """Show simple fallback dialog if main dialog fails."""
        try:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.information(
                self.parent,
                "Interface Selection",
                "Starting with Dialog-Based Hub Interface.\n\n"
                "You can switch to Multi-Pane Explorer from the Interface menu.",
            )

            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False

        except Exception as e:
            self.logger.error(f"Error showing fallback dialog: {e}")
            # Ultimate fallback - just set defaults
            self.selected_mode = InterfaceMode.DIALOG_HUB
            self.remember_choice = False

    def _detect_initial_workflow(self):
        """Detect initial workflow pattern based on system state."""
        development_indicators = 0

        # Check for development environment indicators
        home_dir = Path.home()
        dev_dirs = ["src", "projects", "code", "development", "workspace"]
        for dev_dir in dev_dirs:
            if (home_dir / dev_dir).exists():
                development_indicators += 1

        # Check for common development tools
        common_tools = ["git", "python", "npm", "code"]
        for tool in common_tools:
            if self._command_exists(tool):
                development_indicators += 1

        # Default to file management for general users
        if development_indicators >= 3:
            return WorkflowPattern.DEVELOPMENT
        else:
            return WorkflowPattern.FILE_MANAGEMENT

    def _command_exists(self, command):
        """Check if a command exists in the system."""
        try:
            subprocess.check_output(
                ["where" if os.name == "nt" else "which", command],
                stderr=subprocess.STDOUT,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_interface_recommendation(self, workflow):
        """Get interface recommendation based on workflow pattern.

        NOTE: Multi-pane has been removed. Always returns tabbed interface.
        """
        # All workflows now use the tabbed Dialog Hub interface
        return {
            "mode": InterfaceMode.DIALOG_HUB,
            "name": "Tabbed Hub Interface",
            "reason": "Professional tabbed interface with all tools "
            "organized by category for efficient workflow management.",
        }


try:
    from PyQt5.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        Qt,
        pyqtSignal,
        pyqtSlot,
    )
    from PyQt5.QtGui import QFont, QIcon
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QFrame,
        QGraphicsOpacityEffect,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    class AlphabeticalTabWidget(QTabWidget):
        """QTabWidget that keeps tabs sorted while honoring pinned tabs."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self._sorting = False

        def addTab(self, widget, label):
            index = super().addTab(widget, label)
            self._register_widget(widget)
            return index

        def insertTab(self, index, widget, label):
            index = super().insertTab(index, widget, label)
            self._register_widget(widget)
            return index

        def removeTab(self, index):
            super().removeTab(index)
            self.sort_tabs()

        def setTabText(self, index, label):
            super().setTabText(index, label)
            self.sort_tabs()

        def pin_tab(self, widget, order=None):
            if order is None:
                order = self.count()
            widget.setProperty("rfuPinnedTab", True)
            widget.setProperty("rfuPinnedOrder", order)
            self.sort_tabs()

        def unpin_tab(self, widget):
            widget.setProperty("rfuPinnedTab", False)
            widget.setProperty("rfuPinnedOrder", None)
            self.sort_tabs()

        def sort_tabs(self):
            if self._sorting or self.count() < 2:
                return

            tab_bar = self.tabBar()
            if not hasattr(tab_bar, "moveTab"):
                return

            self._sorting = True
            try:
                current_widget = self.currentWidget()
                current_widgets = [self.widget(i) for i in range(self.count())]

                pinned_entries = []
                movable = []
                for position, widget in enumerate(current_widgets):
                    label = self.tabText(self.indexOf(widget))
                    if bool(widget.property("rfuPinnedTab")):
                        order = widget.property("rfuPinnedOrder")
                        if order is None:
                            order = self.count() + position
                        pinned_entries.append((order, position, widget))
                    else:
                        movable.append((label.casefold(), label, widget))

                pinned_entries.sort(key=lambda item: (item[0], item[1]))
                movable.sort(key=lambda entry: entry[0])

                desired_widgets = [entry[2] for entry in pinned_entries]
                desired_widgets.extend(entry[2] for entry in movable)

                for target_index, widget in enumerate(desired_widgets):
                    current_index = self.indexOf(widget)
                    if current_index != -1 and current_index != target_index:
                        tab_bar.moveTab(current_index, target_index)

                if current_widget is not None:
                    restored_index = self.indexOf(current_widget)
                    if restored_index != -1:
                        self.setCurrentIndex(restored_index)
            finally:
                self._sorting = False

        def _register_widget(self, widget):
            if (
                bool(widget.property("rfuPinnedTab"))
                and widget.property("rfuPinnedOrder") is None
            ):
                widget.setProperty("rfuPinnedOrder", self.count() - 1)
            self.sort_tabs()

    class RFUMainWindow(QMainWindow):
        # Signals for communication
        interface_switched = pyqtSignal(str)
        tool_launched = pyqtSignal(str)
        PINNED_TAB_TITLES = ("File Management", "File Operations")

        def __init__(self):
            super().__init__()

            # Initialize logging system first
            self.logger = logging.getLogger("RFU.MainWindow")
            self.logger.info("Initializing RFU Main Window with dual interface system")

            # Set basic window properties with proper sizing
            self.setWindowTitle(APP_NAME)

            # Ensure maximize button and proper window behavior
            self.setWindowFlags(
                Qt.Window
                | Qt.WindowCloseButtonHint
                | Qt.WindowMinimizeButtonHint
                | Qt.WindowMaximizeButtonHint
            )

            # Configure window size and positioning
            self._configure_window_geometry()

            # Initialize core systems
            self._initialize_core_systems()

            # Enforce authentication before any interface work begins
            self.logger.info("Enforcing authentication gate prior to UI setup")
            if not self._enforce_login_gate():
                self.logger.warning("Authentication not completed; aborting startup")
                raise AuthenticationCancelledError(
                    "Authentication dialog was dismissed"
                )

            # Show startup dialog and determine interface mode BEFORE UI initialization
            self.logger.info("Determining interface mode through startup dialog")
            self._determine_interface_mode()

            # Initialize the selected interface
            self.logger.info(
                f"Initializing {self.current_interface_mode.value} interface"
            )
            self._initialize_interface()

            # Log successful initialization
            self.logger.info(
                f"RFU Main Window initialized successfully with {self.current_interface_mode.value} interface"
            )

        def _configure_window_geometry(self):
            """Configure window size and positioning based on screen geometry."""
            from PyQt5.QtWidgets import QApplication, QDesktopWidget

            desktop = QApplication.desktop()
            screen_geometry = desktop.screenGeometry()

            # Calculate window size (70% of screen width, 80% of screen height, with constraints)
            window_width = min(1200, int(screen_geometry.width() * 0.7))
            window_height = min(900, int(screen_geometry.height() * 0.8))

            # Ensure minimum usable size
            window_width = max(window_width, 1000)
            window_height = max(window_height, 750)

            # Allow window to be freely resized and maximized
            # Removed setMaximumSize to enable fullscreen/maximize button

            # Set minimum size for usability
            self.setMinimumSize(900, 650)

            # Set initial geometry with calculated size but allow resizing
            start_x = max(50, (screen_geometry.width() - window_width) // 2)
            start_y = max(50, (screen_geometry.height() - window_height) // 2)
            self.resize(window_width, window_height)
            self.move(start_x, start_y)

        def _initialize_core_systems(self):
            """Initialize core application systems and state management."""
            try:
                self.application_state = build_application_state(
                    "RFU.MainWindow",
                    include_config=True,
                    include_preferences=True,
                    database_available=False,
                )

                # Store references to opened windows
                self.opened_windows = {}

                # Interface mode management
                self.current_interface_mode = (
                    InterfaceMode.DIALOG_HUB
                )  # Default fallback
                self.multi_pane_explorer = None
                self.dialog_hub_widget = None
                self.interface_switching_enabled = True
                self.transition_in_progress = False
                self._session_context: Optional[Dict[str, Any]] = None
                self._last_username: str = ""
                self._authentication_verified = False

                # Workflow analysis and session tracking
                self.session_start_time = datetime.now()
                self.tool_usage_count = 0
                self.interface_switch_count = 0

                # Data synchronization
                self.shared_state = {
                    "recent_files": [],
                    "recent_directories": [],
                    "bookmarks": [],
                    "tool_preferences": {},
                    "window_states": {},
                }

                # Initialize database tracking
                self.database_available = self.application_state.database_available
                if self.database_available:
                    try:
                        from scripts.maintenance.standalone_database_manager import (
                            get_database_manager,
                        )

                        self.db_manager = get_database_manager()
                        self.logger.info("Database system initialized successfully")
                    except Exception as e:
                        self.logger.warning(f"Database initialization failed: {e}")
                        self.database_available = False
                        self.db_manager = None
                else:
                    self.db_manager = None
                    self.logger.info("Database system not available")
                    if not _DATABASE_INITIALIZATION_ATTEMPTED:
                        self.logger.info("Database initialization deferred until a concrete tool needs it")

                # Initialize configuration and preference services from the shared facade.
                self.config_manager = self.application_state.config_manager
                self.preference_manager = self.application_state.preference_manager
                if self.config_manager:
                    self._setup_interface_configuration()
                    self.logger.info("Configuration manager initialized successfully")
                else:
                    self.logger.warning("Configuration manager initialization failed")

                self.logger.info("Core systems initialized successfully")

            except Exception as e:
                self.logger.error(f"Error initializing core systems: {e}")
                # Set minimal fallback state
                self.opened_windows = {}
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.database_available = False
                self.db_manager = None
                self.config_manager = None

        def _setup_interface_configuration(self):
            """Setup interface-specific configuration sections."""
            if not self.config_manager:
                return

            # Ensure interface configuration sections exist
            interface_sections = {
                "interface_mode": {
                    "current_mode": InterfaceMode.DIALOG_HUB.value,
                    "auto_detect_enabled": True,
                    "remember_choice": True,
                    "show_startup_dialog": True,
                    "transition_animations": True,
                    "switch_confirmation": False,
                },
                "interface_usage": {
                    "mode_statistics": {},
                    "switch_count": 0,
                    "total_session_time": 0,
                    "preference_confidence": 0.5,
                },
                "workflow_analysis": {
                    "enabled": True,
                    "suggestion_threshold": 0.7,
                    "recent_sessions": [],
                    "pattern_detection": True,
                },
            }

            for section, defaults in interface_sections.items():
                for key, default_value in defaults.items():
                    try:
                        if hasattr(self.config_manager, "get_setting"):
                            current_value = self.config_manager.get_setting(
                                section, key
                            )
                            if current_value is None and hasattr(
                                self.config_manager, "set_setting"
                            ):
                                self.config_manager.set_setting(
                                    section, key, default_value
                                )
                    except (AttributeError, KeyError):
                        pass

        def _resolve_identity_database_path(self) -> Optional[Path]:
            """Locate the identity database used by the login dialog."""

            configured_value = ""
            if self.config_manager and hasattr(self.config_manager, "get_setting"):
                try:
                    configured_value = (
                        self.config_manager.get_setting("identity", "database_path", "")
                        or ""
                    ).strip()
                except Exception as exc:
                    self.logger.debug(
                        "Unable to read identity.database_path from config: %s",
                        exc,
                    )

            candidates: list[tuple[str, Path]] = []
            if configured_value:
                candidates.append(("config", Path(configured_value).expanduser()))

            env_override = (os.getenv("RFU_IDENTITY_DB_PATH") or "").strip()
            if env_override:
                candidates.append(("env", Path(env_override).expanduser()))

            candidates.append(
                (
                    "project",
                    Path(project_root) / "data" / "rfu_identity.sqlite3",
                )
            )
            candidates.append(("cwd", Path.cwd() / "data" / "rfu_identity.sqlite3"))

            normalized: list[tuple[str, Path]] = []
            seen: set[str] = set()
            for label, candidate in candidates:
                expanded = candidate.expanduser()
                key = str(expanded)
                if key in seen:
                    continue
                seen.add(key)
                normalized.append((label, expanded))

            for label, candidate in normalized:
                try:
                    if candidate.exists():
                        self.logger.debug(
                            "Identity DB candidate (%s) selected: %s",
                            label,
                            candidate,
                        )
                        return candidate
                    self.logger.debug(
                        "Identity DB candidate (%s) missing: %s",
                        label,
                        candidate,
                    )
                except OSError as exc:
                    self.logger.debug(
                        "Identity DB candidate (%s) stat error: %s",
                        label,
                        exc,
                    )

            if configured_value:
                self.logger.warning(
                    "Configured identity database not found at %s",
                    Path(configured_value).expanduser(),
                )
            else:
                missing_paths = ", ".join(str(path) for _, path in normalized)
                self.logger.warning(
                    "Identity database not found in default locations (%s)",
                    missing_paths,
                )
            return None

        def _load_login_prompt_callable(self):
            """Import the GUI login dialog without hard-coding a single path."""

            module_candidates = (
                "src.rfu.login_dialog",
                "rfu.login_dialog",
            )
            last_error: Optional[Exception] = None
            for module_name in module_candidates:
                try:
                    module = importlib.import_module(module_name)
                    prompt = getattr(module, "prompt_for_login", None)
                    if callable(prompt):
                        return prompt
                except Exception as exc:
                    last_error = exc
                    self.logger.debug(
                        "Login dialog import failed via %s: %s",
                        module_name,
                        exc,
                    )

            raise ImportError(
                "Unable to locate the login dialog prompt callable"
            ) from last_error

        def _show_authentication_error(self, title: str, message: str) -> None:
            """Display authentication errors without crashing headless tests."""

            try:
                QMessageBox.critical(self, title, message)
            except Exception:
                self.logger.error("%s: %s", title, message)

        def _enforce_login_gate(self) -> bool:
            """Prompt for login and block UI startup until authentication succeeds."""

            if self._authentication_verified:
                return True

            database_path = self._resolve_identity_database_path()
            if database_path is None:
                self.logger.warning(
                    "Identity database unavailable; skipping authentication gate"
                )
                self._authentication_verified = True
                return True

            try:
                prompt_for_login = self._load_login_prompt_callable()
            except ImportError as exc:
                self.logger.error("Login dialog unavailable: %s", exc)
                self._show_authentication_error(
                    "Authentication Unavailable",
                    "Unable to load the login dialog component.\n\n"
                    "Please reinstall or repair the RFU login dependencies.",
                )
                return False

            self.logger.debug("Launching authentication dialog for %s", database_path)
            start_time = time.perf_counter()
            try:
                session = prompt_for_login(
                    database_path=database_path,
                    parent=self,
                    initial_username=self._last_username or "",
                )
            except Exception as exc:
                self.logger.error("Login dialog crashed: %s", exc, exc_info=True)
                self._show_authentication_error(
                    "Authentication Error",
                    f"The sign-in dialog encountered an unexpected error.\n\n{exc}",
                )
                return False
            finally:
                elapsed = time.perf_counter() - start_time
                self.logger.debug("Authentication dialog closed after %.2fs", elapsed)

            if not session:
                self.logger.info("Authentication dialog dismissed without sign-in")
                return False

            self._session_context = session
            username = str(session.get("username") or "").strip()
            self._last_username = username
            role = session.get("role") or session.get("session", {}).get("role")
            self._authentication_verified = True

            try:
                status_text = f"Signed in as {username or 'unknown'}" + (
                    f" ({role})" if role else ""
                )
                self.statusBar().showMessage(status_text, 8000)
            except Exception:
                pass

            self.logger.info(
                "Authenticated GUI session for user %s (role=%s)",
                username or "unknown",
                role or "unknown",
            )
            return True

        def _determine_interface_mode(self):
            """Determine which interface mode to use with comprehensive startup dialog logic."""
            try:
                self.current_interface_mode = InterfaceMode.DIALOG_HUB

                if not self.config_manager:
                    self.logger.warning(
                        "Configuration manager not available, showing startup dialog"
                    )
                    self._show_interface_selection_dialog()
                    return

                saved_settings = self._get_saved_interface_settings()

                if self._should_use_saved_settings(saved_settings):
                    self._apply_saved_interface_mode(saved_settings["saved_mode"])
                else:
                    self._show_interface_selection_dialog()

            except Exception as e:
                self.logger.error(f"Error determining interface mode: {e}")
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.logger.info("Using fallback interface mode: DIALOG_HUB")

        def _get_saved_interface_settings(self):
            """Get saved interface settings from config manager."""
            return {
                "saved_mode": self.config_manager.get_setting(
                    "interface_mode", "current_mode"
                ),
                "show_startup": self.config_manager.get_setting(
                    "interface_mode", "show_startup_dialog", True
                ),
                "remember_choice": self.config_manager.get_setting(
                    "interface_mode", "remember_choice", False
                ),
            }

        def _should_use_saved_settings(self, settings):
            """Check if saved settings should be used instead of showing dialog."""
            return (
                settings["saved_mode"]
                and settings["remember_choice"]
                and not settings["show_startup"]
            )

        def _apply_saved_interface_mode(self, saved_mode):
            """Apply the saved interface mode."""
            try:
                self.current_interface_mode = InterfaceMode(saved_mode)
                self.logger.info(
                    f"Using saved interface mode: {self.current_interface_mode.value}"
                )
            except ValueError as e:
                self.logger.warning(f"Invalid saved interface mode '{saved_mode}': {e}")
                self._show_interface_selection_dialog()

        def _show_interface_selection_dialog(self):
            """Show enhanced interface selection dialog on startup with comprehensive error handling."""
            try:
                self.logger.info("Initializing interface selection dialog")

                if not self._validate_dialog_prerequisites():
                    return

                dialog = InterfaceSelectionDialog(self)
                dialog_result = dialog.show_selection_dialog()

                if dialog_result:
                    self._process_dialog_selection(dialog)
                else:
                    self.logger.warning(
                        "Interface selection dialog cancelled or failed"
                    )
                    self._handle_dialog_fallback()

            except ImportError as ie:
                self.logger.error(f"PyQt5 import error during dialog creation: {ie}")
                self._handle_dialog_fallback()
            except Exception as e:
                self.logger.error(
                    f"Unexpected error showing interface selection dialog: {e}"
                )
                self._handle_dialog_fallback()

        def _validate_dialog_prerequisites(self) -> bool:
            """Validate prerequisites for showing the dialog."""
            from PyQt5.QtWidgets import QApplication

            if not QApplication.instance():
                self.logger.error("QApplication not available for dialog creation")
                self._handle_dialog_fallback()
                return False
            return True

        def _process_dialog_selection(self, dialog):
            """Process user selection from interface dialog."""
            self.current_interface_mode = dialog.selected_mode
            self.logger.info(
                f"User selected interface mode: {self.current_interface_mode.value}"
            )

            if dialog.remember_choice and self.config_manager:
                self._save_interface_preferences()

            if self.database_available and self.db_manager:
                self._track_interface_selection_safe(dialog)

        def _save_interface_preferences(self):
            """Save interface preferences to config."""
            try:
                self.config_manager.set_setting(
                    "interface_mode", "current_mode", self.current_interface_mode.value
                )
                self.config_manager.set_setting(
                    "interface_mode", "remember_choice", True
                )
                self.config_manager.set_setting(
                    "interface_mode", "show_startup_dialog", False
                )
                self.logger.info("Saved user interface preferences")
            except Exception as config_error:
                self.logger.warning(
                    f"Failed to save interface preferences: {config_error}"
                )

        def _track_interface_selection_safe(self, dialog):
            """Safely track interface selection for analytics."""
            try:
                self._track_interface_selection(
                    self.current_interface_mode.value, dialog.remember_choice
                )
            except Exception as db_error:
                self.logger.warning(f"Failed to track interface selection: {db_error}")

        def _handle_dialog_fallback(self):
            """Handle fallback when dialog creation or interaction fails.

            NOTE: Multi-pane has been removed. Always defaults to Dialog Hub.
            """
            try:
                self.logger.info("Using fallback interface selection logic")

                # Always use Dialog Hub (tabbed interface) - multi-pane removed
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.logger.info("Defaulting to Tabbed Hub Interface")

                # Show simple notification if possible
                try:
                    from PyQt5.QtWidgets import QMessageBox

                    QMessageBox.information(
                        self,
                        "Interface Mode Selected",
                        "Starting with Tabbed Hub Interface.\n\n"
                        "This provides organized access to all tools by category.",
                    )
                except Exception:
                    # Ultimate fallback - just print message
                    print("Starting with Tabbed Hub Interface")

            except Exception as e:
                self.logger.error(f"Error in dialog fallback handling: {e}")
                # Ultimate fallback
                self.current_interface_mode = InterfaceMode.DIALOG_HUB

        def _detect_developer_environment(self):
            """Detect if the current environment suggests developer usage."""
            try:
                import os
                import subprocess
                from pathlib import Path

                developer_indicators = 0

                # Check for development directories
                home_dir = Path.home()
                dev_dirs = [
                    "src",
                    "projects",
                    "code",
                    "development",
                    "workspace",
                    "git",
                    "repos",
                ]
                for dev_dir in dev_dirs:
                    if (home_dir / dev_dir).exists():
                        developer_indicators += 1

                # Check for development tools
                dev_tools = ["git", "python", "node", "npm", "code", "vim", "code.exe"]
                for tool in dev_tools:
                    try:
                        subprocess.check_output(
                            ["where" if os.name == "nt" else "which", tool],
                            stderr=subprocess.STDOUT,
                        )
                        developer_indicators += 1
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        pass

                # Check current directory for project files
                current_dir = Path.cwd()
                project_files = [
                    ".git",
                    "package.json",
                    "requirements.txt",
                    "Makefile",
                    ".gitignore",
                    "src",
                ]
                for project_file in project_files:
                    if (current_dir / project_file).exists():
                        developer_indicators += 1

                # If we find 3 or more indicators, likely a developer environment
                return developer_indicators >= 3

            except Exception as e:
                self.logger.warning(f"Error detecting developer environment: {e}")
                return False

        def _track_interface_selection(self, mode, remember_choice):
            """Track interface selection for analytics and improvement."""
            try:
                if not self.database_available or not self.db_manager:
                    return

                # Record interface selection event
                query = """
                    INSERT OR REPLACE INTO interface_usage 
                    (selection_date, interface_mode, remember_choice, session_id)
                    VALUES (datetime('now'), ?, ?, ?)
                """

                session_id = f"{self.session_start_time.isoformat()}_{id(self)}"
                params = (mode, remember_choice, session_id)

                self.db_manager.execute_update(query, params)
                self.logger.debug(f"Tracked interface selection: {mode}")

            except Exception as e:
                self.logger.warning(f"Failed to track interface selection: {e}")

        def _initialize_interface(self):
            """Initialize the selected interface mode with comprehensive error handling.

            NOTE: Multi-pane interface has been removed. Only tabbed interface is supported.
            """
            try:
                self.logger.info(
                    f"Initializing interface mode: {self.current_interface_mode.value}"
                )

                # Always initialize the dialog hub (tabbed) interface
                self._initialize_dialog_hub_interface()

                # Setup interface menu (switching disabled)
                self._setup_interface_switching_menu()

                self.logger.info(
                    f"Interface initialization completed: {self.current_interface_mode.value}"
                )

            except Exception as e:
                self.logger.error(
                    f"Critical error during interface initialization: {e}"
                )
                self._handle_interface_initialization_failure()

        def _handle_interface_initialization_failure(self):
            """Handle critical interface initialization failures with emergency fallback."""
            try:
                self.logger.warning("Attempting emergency interface fallback")

                # Create minimal emergency interface
                from PyQt5.QtWidgets import (
                    QLabel,
                    QPushButton,
                    QVBoxLayout,
                    QWidget,
                )

                emergency_widget = QWidget()
                layout = QVBoxLayout(emergency_widget)

                # Error message
                error_label = QLabel(
                    "Interface initialization failed. Using emergency mode."
                )
                error_label.setStyleSheet(
                    "color: red; font-weight: bold; padding: 20px;"
                )
                layout.addWidget(error_label)

                # Retry button
                retry_button = QPushButton("Retry Interface Initialization")
                retry_button.clicked.connect(self._retry_interface_initialization)
                layout.addWidget(retry_button)

                # Exit button
                exit_button = QPushButton("Exit Application")
                exit_button.clicked.connect(self.close)
                layout.addWidget(exit_button)

                self.setCentralWidget(emergency_widget)
                self.setWindowTitle(f"{APP_NAME} - Emergency Mode")

                self.logger.info("Emergency interface fallback activated")

            except Exception as emergency_error:
                self.logger.critical(f"Emergency fallback failed: {emergency_error}")
                # Ultimate fallback - show message and exit
                try:
                    from PyQt5.QtWidgets import QMessageBox

                    QMessageBox.critical(
                        None,
                        "Critical Error",
                        f"Application failed to initialize properly.\n\nError: {emergency_error}\n\nThe application will now exit.",
                    )
                except Exception:
                    print(
                        f"CRITICAL ERROR: Application failed to initialize. Error: {emergency_error}"
                    )
                sys.exit(1)

        def _retry_interface_initialization(self):
            """Retry interface initialization after emergency fallback."""
            try:
                self.logger.info("Retrying interface initialization")

                # Reset interface state
                self.current_interface_mode = InterfaceMode.DIALOG_HUB
                self.multi_pane_explorer = None
                self.dialog_hub_widget = None

                # Try to initialize again
                self._initialize_interface()

            except Exception as e:
                self.logger.error(f"Interface retry failed: {e}")
                self._handle_interface_initialization_failure()

        def _initialize_dialog_hub_interface(self):
            """Initialize the dialog-based hub interface with full tabbed functionality."""
            # Ensure the main window is visible
            self.show()

            self.setWindowTitle(f"{APP_NAME} - Dialog Hub Interface")

            # Store reference to dialog hub widget for later restoration
            if hasattr(self, "dialog_hub_widget") and self.dialog_hub_widget:
                self.setCentralWidget(self.dialog_hub_widget)
            else:
                self.init_ui()
                self.dialog_hub_widget = self.centralWidget()

        def _initialize_multi_pane_interface(self):
            """Initialize the multi-pane explorer interface embedded in the main window.

            NOTE: The src.file_explorer module has been removed due to stability issues.
            This method now uses the built-in simple multi-pane widget fallback.
            """
            try:
                self.logger.info("Initializing multi-pane explorer interface")

                # Store current dialog hub widget if switching
                current_widget = self.centralWidget()
                if current_widget and not hasattr(self, "dialog_hub_widget"):
                    self.dialog_hub_widget = current_widget
                    self.logger.debug(
                        "Stored current dialog hub widget for future restoration"
                    )

                # Create or reuse the multi-pane explorer widget
                # NOTE: file_explorer module removed - using built-in fallback only
                if not self.multi_pane_explorer:
                    self.multi_pane_explorer = self._create_simple_multi_pane_widget()
                    self.logger.info("Using built-in simple multi-pane widget")

                # Embed the multi-pane explorer in the main window
                self.setCentralWidget(self.multi_pane_explorer)
                self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer")

                # Ensure the main window stays visible
                self.show()

                self.logger.info(
                    "Multi-pane interface initialization completed successfully"
                )
                return True

            except Exception as e:
                self.logger.error(f"Error initializing multi-pane interface: {e}")
                self._create_fallback_multi_pane()
                return False  # Return False when falling back due to error

        def _create_simple_multi_pane_widget(self):
            """Create a proper multi-pane widget that can be embedded in the main window."""
            from PyQt5.QtCore import QDir
            from PyQt5.QtWidgets import (
                QFileSystemModel,
                QFrame,
                QHBoxLayout,
                QHeaderView,
                QSplitter,
                QTreeView,
                QVBoxLayout,
            )

            # Create main container widget
            main_widget = QWidget()
            main_layout = QHBoxLayout(main_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)

            # Create horizontal splitter for multi-pane layout
            splitter = QSplitter(Qt.Horizontal)

            # Create two file browser panes
            for i in range(2):
                pane = self._create_file_browser_pane(f"Pane {i+1}")
                splitter.addWidget(pane)

            # Set equal sizes for both panes
            splitter.setSizes([400, 400])

            main_layout.addWidget(splitter)

            # Add some basic styling
            main_widget.setStyleSheet(
                """
                QWidget {
                    background-color: #f5f5f5;
                }
                QFrame {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                QTreeView {
                    border: none;
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                }
                QTreeView::item:selected {
                    background-color: #0078d4;
                    color: white;
                }
            """
            )

            return main_widget

        def _create_file_browser_pane(self, title):
            """Create a single file browser pane."""
            from PyQt5.QtCore import QDir
            from PyQt5.QtWidgets import (
                QFileSystemModel,
                QFrame,
                QHBoxLayout,
                QLabel,
                QPushButton,
                QTreeView,
                QVBoxLayout,
            )

            # Create frame for the pane
            pane_frame = QFrame()
            pane_layout = QVBoxLayout(pane_frame)
            pane_layout.setContentsMargins(5, 5, 5, 5)

            # Add title and navigation
            header_layout = QHBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
            header_layout.addWidget(title_label)

            # Add home button
            home_button = QPushButton("🏠 Home")
            home_button.setMaximumWidth(80)
            home_button.clicked.connect(lambda: self._navigate_to_home(tree_view))
            header_layout.addWidget(home_button)

            pane_layout.addLayout(header_layout)

            # Create tree view with file system model
            tree_view = QTreeView()
            file_model = QFileSystemModel()
            file_model.setRootPath(QDir.rootPath())

            tree_view.setModel(file_model)
            tree_view.setRootIndex(file_model.index(str(Path.home())))

            # Configure tree view
            tree_view.setAlternatingRowColors(True)
            tree_view.setSortingEnabled(True)
            tree_view.sortByColumn(0, Qt.AscendingOrder)

            # Adjust column widths
            header = tree_view.header()
            header.resizeSection(0, 250)  # Name column
            header.resizeSection(1, 100)  # Size column
            header.resizeSection(2, 80)  # Type column
            header.resizeSection(3, 120)  # Date column

            pane_layout.addWidget(tree_view)

            return pane_frame

        def _navigate_to_home(self, tree_view):
            """Navigate tree view to home directory."""
            if hasattr(tree_view, "model") and tree_view.model():
                home_index = tree_view.model().index(str(Path.home()))
                tree_view.setRootIndex(home_index)

        def _create_fallback_multi_pane(self):
            """Create fallback multi-pane interface when full version not available."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout(central_widget)

            # Title
            title_label = QLabel("Multi-Pane Explorer (Simplified)")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; margin: 20px;"
            )
            layout.addWidget(title_label)

            # Info message
            info_label = QLabel(
                "Full multi-pane explorer not available.\nUsing simplified interface."
            )
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #666; margin: 10px;")
            layout.addWidget(info_label)

            # Switch back button
            switch_button = QPushButton("Switch to Dialog Hub")
            switch_button.clicked.connect(
                lambda: self.switch_interface_mode(InterfaceMode.DIALOG_HUB)
            )
            layout.addWidget(switch_button)

            self.setWindowTitle(f"{APP_NAME} - Multi-Pane Explorer (Simplified)")

        def switch_interface_mode(self, new_mode, animated=True):
            """Switch between interface modes with optional animation.

            NOTE: Multi-pane interface has been removed. This method now only
            supports DIALOG_HUB mode and is kept for API compatibility.
            """
            # Only DIALOG_HUB is supported now
            if new_mode != InterfaceMode.DIALOG_HUB:
                self.logger.warning(
                    f"Unsupported interface mode: {new_mode}. Using DIALOG_HUB."
                )
                new_mode = InterfaceMode.DIALOG_HUB

            if self.current_interface_mode == new_mode or self.transition_in_progress:
                return

            self.transition_in_progress = True
            self.current_interface_mode = new_mode

            # Update configuration
            if self.config_manager:
                try:
                    self.config_manager.set_setting(
                        "interface_mode", "current_mode", new_mode.value
                    )
                except AttributeError:
                    pass

            # Track switch for analytics
            self.interface_switch_count += 1

            # Perform transition
            self._immediate_interface_transition(new_mode)

            # Emit signal
            self.interface_switched.emit(new_mode.value)

        def _immediate_interface_transition(self, new_mode):
            """Perform immediate interface transition without animation.

            NOTE: Only DIALOG_HUB is supported after multi-pane removal.
            """
            # Always use dialog hub interface
            self._initialize_dialog_hub_interface()
            self.transition_in_progress = False

        def _setup_interface_switching_menu(self):
            """Setup menu for interface options.

            NOTE: Interface switching is disabled since only tabbed mode
            is supported. Menu is kept for preferences access only.
            """
            menubar = self.menuBar()

            if not menubar:
                return

            # Remove any previously added Interface menu to avoid duplicates
            for action in menubar.actions():
                menu = action.menu() if hasattr(action, "menu") else None
                text = action.text() if hasattr(action, "text") else ""
                if menu is None:
                    continue
                if text.replace("&", "").strip().lower() == "interface":
                    menubar.removeAction(action)
                    break

            # Add interface menu
            interface_menu = menubar.addMenu("&Interface")

            # Current mode indicator (disabled, just shows status)
            current_mode_action = interface_menu.addAction(
                "✓ Tabbed Hub Interface (Active)"
            )
            current_mode_action.setEnabled(False)

            interface_menu.addSeparator()

            # Interface preferences
            preferences_action = interface_menu.addAction("Interface Preferences...")
            preferences_action.triggered.connect(self._show_interface_preferences)

        def _show_interface_preferences(self):
            """Show interface preferences dialog."""
            QMessageBox.information(
                self,
                "Interface Preferences",
                "Interface preferences dialog would be shown here.",
            )

        def closeEvent(self, event):
            """Handle application close event - ensure all windows are properly closed."""
            try:
                # Save configuration if available
                if self.config_manager:
                    try:
                        # Save current interface mode
                        self.config_manager.set_setting(
                            "interface_mode",
                            "current_mode",
                            self.current_interface_mode.value,
                        )
                    except Exception as e:
                        self.logger.warning(f"Error saving configuration: {e}")

                # Accept the close event
                event.accept()

            except Exception as e:
                self.logger.error(f"Error during application close: {e}")
                event.accept()  # Close anyway

        def launch_tool(self, tool_name, module_name=None, class_name=None):
            """Enhanced tool launch with tracking and proper instantiation."""
            try:
                self._track_tool_launch(tool_name)

                launch_request = resolve_tool_launch_request(
                    tool_name,
                    module_name,
                    class_name,
                )
                if launch_request is not None:
                    module_name = launch_request.module_name
                    class_name = launch_request.class_name

                if self._handle_existing_window(tool_name):
                    return

                if not self._validate_tool_parameters(
                    tool_name, module_name, class_name
                ):
                    return

                tool_class = self._import_tool_class(tool_name, module_name, class_name)
                if not tool_class:
                    return

                self._create_and_show_tool(tool_name, tool_class)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Critical Error",
                    f"Unexpected error launching {tool_name}:\n\n{e}",
                )
                self.logger.error(f"Critical error in launch_tool for {tool_name}: {e}")

        def _track_tool_launch(self, tool_name):
            """Track tool launch statistics."""
            self.tool_usage_count += 1
            self.tool_launched.emit(tool_name)

        def _handle_existing_window(self, tool_name):
            """Check and show existing window if already open."""
            if tool_name in self.opened_windows:
                window = self.opened_windows[tool_name]
                if window and hasattr(window, "show"):
                    window.show()
                    window.raise_()
                    window.activateWindow()
                    return True
            return False

        def _validate_tool_parameters(self, tool_name, module_name, class_name):
            """Validate tool launch parameters."""
            if not module_name or not class_name:
                QMessageBox.warning(
                    self,
                    TOOL_LAUNCH_ERROR,
                    f"Cannot launch {tool_name}: Missing module or class information.\n\n"
                    "This tool needs to be properly configured for launching.",
                )
                return False
            return True

        def _import_tool_class(self, tool_name, module_name, class_name):
            """Import tool class using multiple strategies."""
            import_strategies = [
                lambda: self._import_direct(module_name, class_name),
                lambda: self._import_direct(
                    (
                        f"src.{module_name}"
                        if not module_name.startswith("src.")
                        else module_name
                    ),
                    class_name,
                ),
                lambda: self._import_absolute(module_name, class_name),
            ]

            for strategy in import_strategies:
                try:
                    tool_class = strategy()
                    if tool_class:
                        return tool_class
                except Exception:
                    continue

            QMessageBox.warning(
                self,
                TOOL_LAUNCH_ERROR,
                f"Could not import {tool_name}.\n\n"
                f"Module: {module_name}\n"
                f"Class: {class_name}\n\n"
                "Please ensure the tool is properly installed.",
            )
            return None

        def _create_and_show_tool(self, tool_name, tool_class):
            """Create and show the tool window."""
            try:
                window = tool_class()
                self.opened_windows[tool_name] = window
                window.show()

                self._track_tool_usage_in_db(tool_name)
                self.logger.info(f"Successfully launched tool: {tool_name}")

            except TypeError as te:
                self._handle_tool_type_error(tool_name, te)
            except Exception as e:
                self._handle_tool_creation_error(tool_name, e)

        def _handle_tool_type_error(self, tool_name, error):
            """Handle TypeError during tool creation."""
            if "title" in str(error) or "keyword argument" in str(error):
                QMessageBox.warning(
                    self,
                    "Tool Configuration Issue",
                    f"The {tool_name} tool has a configuration issue.\n\n"
                    f"Error: {error}\n\n"
                    "This tool may need to be updated for compatibility.",
                )
                self.logger.error(f"Tool {tool_name} has constructor issues: {error}")
            else:
                QMessageBox.critical(
                    self,
                    TOOL_LAUNCH_ERROR,
                    f"Failed to create {tool_name} window:\n\n{error}",
                )
                self.logger.error(f"Tool instantiation failed for {tool_name}: {error}")

        def _handle_tool_creation_error(self, tool_name, error):
            """Handle general errors during tool creation."""
            QMessageBox.critical(
                self,
                TOOL_LAUNCH_ERROR,
                f"Failed to create {tool_name} window:\n\n{error}",
            )
            self.logger.error(f"Tool instantiation failed for {tool_name}: {error}")

        def _track_tool_usage_in_db(self, tool_name):
            """Track tool usage in database if available."""
            if self.database_available and self.db_manager:
                try:
                    self._track_tool_usage(tool_name)
                except Exception as e:
                    self.logger.warning(f"Failed to track tool usage: {e}")

        def _import_direct(self, module_name, class_name):
            """Import using direct module path."""
            try:
                module = __import__(module_name, fromlist=[class_name])
                if hasattr(module, class_name):
                    return getattr(module, class_name)
                return None
            except (ImportError, AttributeError):
                return None

        def _import_absolute(self, module_name, class_name):
            """Import using absolute path with importlib."""
            try:
                import importlib

                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    return getattr(module, class_name)
                return None
            except (ImportError, AttributeError):
                return None

        def _track_tool_usage(self, tool_name):
            """Track tool usage in database."""
            try:
                if not self.database_available or not self.db_manager:
                    return

                query = """
                    INSERT INTO tool_usage 
                    (tool_name, launch_time, interface_mode, session_id)
                    VALUES (?, datetime('now'), ?, ?)
                """

                session_id = f"{self.session_start_time.isoformat()}_{id(self)}"
                params = (tool_name, self.current_interface_mode.value, session_id)

                self.db_manager.execute_update(query, params)

            except Exception as e:
                self.logger.warning(f"Failed to track tool usage: {e}")

        def init_ui(self):
            """Initialize the comprehensive tabbed user interface."""
            # Create menu bar
            self.create_menu_bar()

            # Setup interface switching menu
            self._setup_interface_switching_menu()

            # Create central widget and main layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)

            # Add title
            title_label = QLabel(APP_NAME)
            title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            title_label.setStyleSheet(
                """
                font-size: 28px; 
                font-weight: bold; 
                padding: 20px;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 10px;
                margin: 10px;
            """
            )
            main_layout.addWidget(title_label)

            # Create tab widget for different tool categories
            self.tab_widget = AlphabeticalTabWidget()
            main_layout.addWidget(self.tab_widget)

            # File Management Tools
            file_mgmt_tab = self.create_tool_category_tab(
                [
                    (
                        "File Finder",
                        "Search and find files based on various criteria",
                        self.open_file_finder,
                    ),
                    (
                        "Catalog Files",
                        "Create and manage file catalogs",
                        self.open_catalog,
                    ),
                    (
                        "Rename Files",
                        "Batch rename files and folders",
                        self.open_rename,
                    ),
                    (
                        "Organize Files",
                        "Automatically organize files by type/date",
                        self.open_organize,
                    ),
                    (
                        "Advanced Folders",
                        "Configure smart folder monitoring and search",
                        self.open_advanced_folders,
                    ),
                    (
                        "Synchronize",
                        "Synchronize directories",
                        self.open_sync,
                    ),
                ]
            )
            self._register_tab(file_mgmt_tab, "File Management")

            # File Operations Tools
            file_ops_tab = self.create_tool_category_tab(
                [
                    (
                        "Compress/Decompress",
                        "Archive and extract files",
                        self.open_compress,
                    ),
                    (
                        "Split/Join Files",
                        "Split large files or join parts",
                        self.open_file_splitter,
                    ),
                    (
                        "Enhanced Editor",
                        "Advanced text editor with syntax highlighting",
                        self.open_enhanced_editor,
                    ),
                ]
            )
            self._register_tab(file_ops_tab, "File Operations")

            # Analysis Tools
            analysis_tab = self.create_tool_category_tab(
                [
                    (
                        "Size Analyzer",
                        "Analyze disk space usage",
                        self.open_size_analyzer,
                    ),
                    (
                        "Duplicate Finder",
                        "Find and remove duplicate files",
                        self.open_duplicate_finder,
                    ),
                    (
                        "File Checksum",
                        "Calculate and verify checksums",
                        self.open_checksum,
                    ),
                    (
                        "Empty Folders",
                        "Find and clean empty folders",
                        self.open_empty_folders,
                    ),
                ]
            )
            self._register_tab(analysis_tab, "Analysis")

            # Security Tools
            security_tab = self.create_tool_category_tab(
                [
                    (
                        "Security Preferences",
                        "Configure comprehensive security settings",
                        self.open_security_preferences,
                    ),
                    (
                        "Encrypt/Decrypt",
                        "Secure file encryption and decryption",
                        self.open_encrypt_decrypt,
                    ),
                    (
                        "Secure Delete",
                        "Permanently delete sensitive files",
                        self.open_secure_delete,
                    ),
                    (
                        "Permissions Editor",
                        "Manage file and folder permissions",
                        self.open_permissions,
                    ),
                ]
            )
            self._register_tab(security_tab, "Security")

            # Metadata Tools
            metadata_tab = self.create_tool_category_tab(
                [
                    (
                        "Edit Image Metadata",
                        "View and edit image metadata",
                        self.open_image_metadata,
                    ),
                    (
                        "Office Metadata Editor",
                        "Edit document metadata",
                        self.open_office_metadata,
                    ),
                    ("File Touch", "Modify file timestamps", self.open_file_touch),
                ]
            )
            self._register_tab(metadata_tab, "Metadata")

            # PDF Tools
            self._pdf_tools_tab_placeholder = self.create_pdf_tools_placeholder_tab()
            self._pdf_tools_tab_loaded = False
            pdf_tab = self._pdf_tools_tab_placeholder
            self._register_tab(pdf_tab, "PDF Tools")

            # Network Tools
            network_tab = self.create_tool_category_tab(
                [
                    (
                        "Network Connectivity",
                        "Check network connectivity and diagnostics",
                        self.open_network_connectivity,
                    ),
                    (
                        "Network Scanner",
                        "Scan network for devices and services",
                        self.open_network_scanner,
                    ),
                    (
                        "Network Transfer",
                        "Transfer files and configurations between RFU clients",
                        self.open_network_transfer,
                    ),
                    (
                        "Bookmark Manager",
                        "Cross-platform bookmark keeper/editor/importer",
                        self.open_bookmark_manager,
                    ),
                ]
            )
            self._register_tab(network_tab, "Network Tools")

            # Privacy Tools
            privacy_tab = self.create_tool_category_tab(
                [
                    (
                        "Privacy Cleaner",
                        "Clean privacy-sensitive data",
                        self.open_privacy_cleaner,
                    ),
                    (
                        "Data Anonymizer",
                        "Anonymize sensitive file data",
                        self.open_data_anonymizer,
                    ),
                ]
            )
            self._register_tab(privacy_tab, "Privacy Tools")

            # System Tools
            system_tab = self.create_tool_category_tab(
                [
                    (
                        "Enhanced Clipboard",
                        "Advanced clipboard management",
                        self.open_enhanced_clipboard,
                    ),
                    (
                        "Process Monitor",
                        "Monitor running processes and resource usage",
                        self.open_process_monitor,
                    ),
                    (
                        "System Diagnostics",
                        "Comprehensive system analysis",
                        self.open_system_diagnostics,
                    ),
                    (
                        "System Cleanup",
                        "Clean temporary and unnecessary files",
                        self.open_system_cleanup,
                    ),
                    (
                        "Software Maintenance",
                        "Update and maintain installed software",
                        self.open_software_maintenance,
                    ),
                    (
                        "Preference Portability",
                        "Export and import preference payloads",
                        self.open_preference_portability,
                    ),
                ]
            )
            self._register_tab(system_tab, "System Tools")

            self.tab_widget.currentChanged.connect(self._on_tab_changed)

        def _register_tab(self, widget, title, pinned=None):
            """Add a tab to the hub and flag it as pinned when needed."""
            if pinned is None:
                pinned = title in self.PINNED_TAB_TITLES

            order_value = None
            if pinned:
                try:
                    order_value = self.PINNED_TAB_TITLES.index(title)
                except ValueError:
                    order_value = self.tab_widget.count()

            widget.setProperty("rfuPinnedTab", bool(pinned))
            widget.setProperty("rfuPinnedOrder", order_value)
            self.tab_widget.addTab(widget, title)

        def create_tool_category_tab(self, tools):
            """Create a tab widget for a category of tools."""
            tab_widget = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab_widget)

            # Create grid layout for tools
            grid_layout = QGridLayout(tab_widget)
            grid_layout.setSpacing(15)
            grid_layout.setContentsMargins(20, 20, 20, 20)

            # Add tools to grid
            row, col = 0, 0
            max_cols = 2

            for name, description, callback in tools:
                tool_button = self.create_tool_button(name, description, callback)
                grid_layout.addWidget(tool_button, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            # Add stretch to push tools to top
            grid_layout.setRowStretch(row + 1, 1)

            return scroll_area

        def create_tool_button(self, name, description, callback):
            """Create a styled tool button."""
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            frame.setStyleSheet(
                """
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
            """
            )

            layout = QVBoxLayout(frame)

            # Tool name
            name_label = QLabel(name)
            name_label.setStyleSheet(
                "font-weight: bold; font-size: 22px; color: #495057;"
            )
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)

            # Tool description
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 18px; color: #6c757d;")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

            # Launch button
            launch_button = QPushButton("Launch")
            launch_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """
            )
            launch_button.clicked.connect(callback)
            layout.addWidget(launch_button)

            frame.setFixedHeight(160)
            return frame

        def create_enhanced_pdf_tools_tab(self):
            """Create enhanced PDF tools tab."""
            if is_enhanced_pdf_tools_available():
                try:
                    pdf_widget = load_enhanced_pdf_tools_widget()(self)
                    return pdf_widget
                except Exception as e:
                    print(f"Error creating enhanced PDF tools: {e}")

            # Fallback to simple PDF tools
            return self.create_tool_category_tab(
                [
                    (PDF_UTILITIES, "Comprehensive PDF tools", self.open_pdf_tools),
                    (
                        EXTRACT_LINKS,
                        "Extract links from PDF files",
                        self.open_pdf_links,
                    ),
                    (PAGE_ADMINISTRATION, "Manage PDF pages", self.open_pdf_pages),
                ]
            )

        def create_pdf_tools_placeholder_tab(self):
            """Create a lightweight placeholder for the optional PDF tools tab."""
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.addStretch()

            message = QLabel(
                "PDF tools load when you select this tab."
            )
            message.setAlignment(Qt.AlignCenter)
            message.setWordWrap(True)
            layout.addWidget(message)

            layout.addStretch()
            return placeholder

        def _install_pdf_tools_tab(self):
            if getattr(self, "_pdf_tools_tab_loaded", False):
                return

            placeholder = getattr(self, "_pdf_tools_tab_placeholder", None)
            if placeholder is None:
                return

            index = self.tab_widget.indexOf(placeholder)
            if index < 0:
                return

            pdf_widget = self.create_enhanced_pdf_tools_tab()
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, pdf_widget, "PDF Tools")
            self._pdf_tools_tab_placeholder = pdf_widget
            self._pdf_tools_tab_loaded = True
            self.tab_widget.setCurrentIndex(index)

        def _on_tab_changed(self, index):
            if index < 0 or getattr(self, "_pdf_tools_tab_loaded", False):
                return

            current_widget = self.tab_widget.widget(index)
            if current_widget is getattr(self, "_pdf_tools_tab_placeholder", None):
                self._install_pdf_tools_tab()

        def create_menu_bar(self):
            """Create the application menu bar."""
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("&File")
            file_menu.addAction("&New Project", self.new_project)
            file_menu.addAction("&Open...", self.open_file)
            file_menu.addSeparator()
            file_menu.addAction("&Save Project", self.save_project)
            file_menu.addAction("Save Project &As...", self.save_project_as)
            file_menu.addSeparator()
            file_menu.addAction("E&xit", self.close)

            # Tools menu
            tools_menu = menubar.addMenu("&Tools")
            tools_menu.addAction("&Preferences...", self.show_main_preferences)
            tools_menu.addAction("&Refresh Tool List", self.refresh_tool_list)

            # Help menu
            help_menu = menubar.addMenu("&Help")
            help_menu.addAction("&About", self.show_about_dialog)

        # File Management Tool Launch Methods
        def open_file_finder(self):
            self.launch_tool(
                "File Finder",
                "src.tools.file_management.finder.file_finder",
                "FileFinderWindow",
            )

        def open_catalog(self):
            self.launch_tool(
                "Catalog Files",
                "src.tools.file_management.advanced_catalog.catalog_tool",
                "CatalogWindow",
            )

        def open_rename(self):
            self.launch_tool(
                "Rename Files", "src.tools.file_operations.rename", "RenameWindow"
            )

        def open_organize(self):
            self.launch_tool(
                "Organize Files",
                "src.tools.file_management.organizer.organize",
                "OrganizeWindow",
            )

        def open_advanced_folders(self):
            self.launch_tool(
                "Advanced Folders",
                "src.tools.file_management.advanced_folders.ui.advanced_folders_widget",
                "AdvancedFoldersGUI",
            )

        # File Operations Tool Launch Methods
        def open_compress(self):
            self.launch_tool(
                "Compress/Decompress",
                "src.tools.file_operations.compression.compress_decompress",
                "CompressDecompressApp",
            )

        def open_file_splitter(self):
            self.launch_tool(
                "Split/Join Files",
                "src.tools.file_operations.file_splitter.gui",
                "FileSplitJoinGUI",
            )

        def open_sync(self):
            self.launch_tool(
                "Synchronize",
                "src.tools.file_management.synchronization_backup.sync",
                "SyncWindow",
            )

        def open_enhanced_editor(self):
            self.launch_tool(
                "Enhanced Editor",
                "src.tools.file_operations.enhanced_editor.enhanced_editor",
                "EnhancedEditor",
            )

        # Analysis Tool Launch Methods
        def open_size_analyzer(self):
            self.launch_tool(
                "Size Analyzer", "src.tools.analysis.size_analyzer", "SizeAnalyzerGUI"
            )

        def open_duplicate_finder(self):
            self.launch_tool(
                "Duplicate Finder",
                "src.tools.analysis.duplicate_finder.find_duplicate_files",
                "DuplicateFinderApp",
            )

        def open_checksum(self):
            self.launch_tool(
                "File Checksum",
                "src.tools.analysis.checksum.check_sum",
                "ChecksumGUI",
            )

        def open_empty_folders(self):
            self.launch_tool(
                "Empty Folders", "src.tools.analysis.empty_folders", "EmptyFoldersGUI"
            )

        # Security Tool Launch Methods
        def open_security_preferences(self):
            self.launch_tool(
                "Security Preferences",
                "src.tools.security.security_preferences",
                "SecurityPreferencesGUI",
            )

        def open_encrypt_decrypt(self):
            self.launch_tool(
                "Encrypt/Decrypt",
                "src.tools.security.encryption.en_and_decrypt",
                "EnAndDecryptGUI",
            )

        def open_secure_delete(self):
            self.launch_tool(
                "Secure Delete",
                "src.tools.file_operations.secure_delete.secure_delete",
                "SecureDeleteGUI",
            )

        def open_permissions(self):
            self.launch_tool(
                "Permissions Editor",
                "src.tools.system.permissions.permissions_editor",
                "PermissionsEditorGUI",
            )

        # Metadata Tool Launch Methods

        def open_image_metadata(self):
            self.launch_tool(
                "Edit Image Metadata",
                "src.tools.metadata.image_metadata.gui",
                "ImageMetadataEditorGUI",
            )

        def open_office_metadata(self):
            self.launch_tool(
                "Office Metadata Editor",
                "src.tools.metadata.office_metadata.office_meta_data_editor",
                "OfficeMetaDataEditorGUI",
            )

        def open_file_touch(self):
            self.launch_tool(
                "File Touch",
                "src.tools.metadata.file_touch.file_touch",
                "FileTouchGUI",
            )

        # PDF Tool Launch Methods

        def open_pdf_tools(self):
            self.launch_tool(
                PDF_UTILITIES,
                "src.tools.pdf_tools.pdf_utilities",
                "PDFUtilitiesGUI",
            )

        def open_pdf_links(self):
            self.launch_tool(
                EXTRACT_LINKS,
                "src.tools.pdf_tools.extract_links",
                "ExtractLinksGUI",
            )

        def open_pdf_pages(self):
            self.launch_tool(
                PAGE_ADMINISTRATION,
                "src.tools.pdf_tools.page_administration",
                "PageAdministrationGUI",
            )

        # Network Tool Launch Methods

        def open_network_connectivity(self):
            self.launch_tool(
                "Network Connectivity",
                "src.tools.network.connectivity",
                "NetworkConnectivityGUI",
            )

        def open_network_scanner(self):
            self.launch_tool(
                "Network Scanner",
                "src.tools.network.scanner.network_scanner",
                "NetworkScannerGUI",
            )

        def open_network_transfer(self):
            self.launch_tool(
                "Network Transfer",
                "src.tools.network.transfer.network_transfer",
                "NetworkTransferGUI",
            )

        def open_bookmark_manager(self):
            self.launch_tool(
                "Bookmark Manager",
                "src.tools.network.bookmarks.bookmark_manager",
                "BookmarkManagerGUI",
            )

        # Privacy Tool Launch Methods

        def open_privacy_cleaner(self):
            self.launch_tool(
                "Privacy Cleaner",
                "src.tools.privacy.privacy_cleaner",
                "PrivacyCleanerGUI",
            )

        def open_data_anonymizer(self):
            self.launch_tool(
                "Data Anonymizer",
                "src.tools.privacy.anonymizer.data_anonymizer",
                "DataAnonymizerGUI",
            )

        # System Tool Launch Methods

        def open_process_monitor(self):
            self.launch_tool(
                "Process Monitor",
                "src.tools.system.process_monitor.process_monitor",
                "ProcessMonitorGUI",
            )

        def open_enhanced_clipboard(self):
            self.launch_tool(
                "Enhanced Clipboard",
                "src.tools.system.enhanced_clipboard",
                "EnhancedClipboardGUI",
            )

        def open_system_diagnostics(self):
            self.launch_tool(
                "System Diagnostics",
                "src.tools.system.system_diagnostics",
                "SystemDiagnosticsGUI",
            )

        def open_system_cleanup(self):
            self.launch_tool(
                "System Cleanup",
                "src.tools.system.system_cleanup.system_cleanup",
                "SystemCleanupGUI",
            )

        def open_software_maintenance(self):
            self.launch_tool(
                "Software Maintenance",
                "src.tools.system.software_maintenance",
                "SoftwareMaintenanceGUI",
            )

        def open_preference_portability(self):
            self.launch_tool(
                "Preference Portability",
                "src.tools.preferences.portability_launcher",
                "PreferencePortabilityGUI",
            )

        # Menu callback implementations
        def new_project(self):
            QMessageBox.information(
                self,
                "New Project",
                "New project functionality would be implemented here.",
            )

        def open_file(self):
            QMessageBox.information(
                self,
                "Open File",
                "Open file functionality would be implemented here.",
            )

        def save_project(self):
            QMessageBox.information(
                self,
                "Save Project",
                "Save project functionality would be implemented here.",
            )

        def save_project_as(self):
            QMessageBox.information(
                self,
                "Save Project As",
                "Save project as functionality would be implemented here.",
            )

        def show_main_preferences(self):
            try:
                from PyQt5.QtWidgets import QDialog

                from src.gui.settings_dialog import SettingsDialog
            except ImportError as exc:
                QMessageBox.critical(
                    self,
                    "Preferences Error",
                    f"Unable to load the preferences dialog.\n{exc}",
                )
                self.logger.error(
                    "Failed to import SettingsDialog for main preferences: %s",
                    exc,
                    exc_info=True,
                )
                return

            try:
                dialog = SettingsDialog(self)
                result = dialog.exec_()
                if result == QDialog.Accepted:
                    self.logger.info("Main preferences saved successfully")
                    try:
                        self.statusBar().showMessage(
                            "Preferences updated",
                            4000,
                        )
                    except Exception:
                        # Status bar may be unavailable in some interface modes
                        pass
                else:
                    self.logger.debug("Main preferences dialog closed without saving")
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Preferences Error",
                    f"An error occurred while opening preferences.\n{exc}",
                )
                self.logger.error(
                    "Error displaying main preferences dialog: %s",
                    exc,
                    exc_info=True,
                )

        def refresh_tool_list(self):
            if hasattr(self, "tab_widget") and self.tab_widget is not None:
                self.tab_widget.sort_tabs()
                message = (
                    "Tabs have been refreshed and sorted alphabetically. "
                    "Pinned tabs stay in place."
                )
            else:
                message = (
                    "Tool list refresh functionality would be implemented here."
                )

            QMessageBox.information(self, "Refresh", message)

        def show_about_dialog(self):
            QMessageBox.about(
                self,
                "About RFU",
                (
                    f"<h3>{APP_NAME}</h3>"
                    "<p>Version 3.0.0 with Dual Interface System</p>"
                    "<p>A comprehensive file utility suite with intelligent "
                    "interface selection.</p>"
                ),
            )

    def main():
        """Main entry point for the application."""
        print(f"Starting {APP_NAME} with Dual Interface System...")

        # Enable HiDPI scaling (A11Y-5) — must be set before QApplication.
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName(APP_NAME)

        try:
            window = RFUMainWindow()
        except AuthenticationCancelledError:
            print("Authentication was cancelled. Exiting without launching the UI.")
            app.quit()
            return 0

        window.show()

        print("Dual-interface system initialized with tabbed hub interface.")
        return app.exec_()

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    if __name__ == "__main__":
        print(f"Error importing modules: {e}")
        print("Please ensure PyQt5 is properly installed.")
        print("To install PyQt5, run: pip install PyQt5")
        sys.exit(1)
    else:
        print(f"RFU import deferred because PyQt5 is unavailable: {e}")
except (RuntimeError, OSError, AttributeError) as e:
    if __name__ == "__main__":
        print(f"Error starting application: {e}")
        sys.exit(1)
