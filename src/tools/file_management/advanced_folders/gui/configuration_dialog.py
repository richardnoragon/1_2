"""
Advanced Folders Configuration Dialog

Enterprise-grade configuration dialog for advanced folder management.
Provides comprehensive configuration interface with tabbed organization,
professional styling, and full accessibility support.

Features:
- Tabbed interface for organized configuration sections
- Real-time validation and error handling
- Professional styling with enterprise design patterns
- Full keyboard navigation and accessibility support
- Integration with existing RFU backend systems
- Comprehensive help system and tooltips

Author: RFU Development Team
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
    from PyQt5.QtWidgets import (
        QApplication,
        QDialog,
        QDialogButtonBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Provide fallback base classes
    QDialog = object
    pyqtSignal = None
    PrimaryButton = None
    SecondaryButton = None

try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None

try:
    from src.gui.components.toast import ToastNotification
except ImportError:
    ToastNotification = None

# Import constants and styling
try:
    from .constants import (
        DIALOG_MIN_HEIGHT,
        DIALOG_MIN_WIDTH,
        DIALOG_PREFERRED_HEIGHT,
        DIALOG_PREFERRED_WIDTH,
        TITLE,
        Accessibility,
        Colors,
        Fonts,
        Icons,
        Layout,
        Styles,
    )
except ImportError:
    # Fallback constants if import fails
    class Colors:
        PRIMARY_BLUE = "#3498db"
        BACKGROUND_MAIN = "#ffffff"
        TEXT_PRIMARY = "#2c3e50"

    class Fonts:
        @staticmethod
        def title_font():
            return None

    class Layout:
        CONTENT_MARGIN = 20
        SECTION_SPACING = 15

    DIALOG_MIN_WIDTH = 900
    DIALOG_MIN_HEIGHT = 700
    TITLE = "Advanced Folders Configuration"

# Import configuration tabs
try:
    from .config_tabs import (
        DisplayConfigTab,
        FiltersConfigTab,
        GeneralConfigTab,
        SearchConfigTab,
    )

    TABS_AVAILABLE = True
except ImportError:
    TABS_AVAILABLE = False

# Import backend integration
try:
    from ..core import FolderConfiguration, ValidationResult
    from ..repositories import FolderConfigurationRepository

    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

    # Fallback classes
    class FolderConfiguration:
        def __init__(self, **kwargs):
            pass

    class ValidationResult:
        def __init__(self, is_valid=True, errors=None):
            self.is_valid = is_valid
            self.errors = errors or []


# Import logging
try:
    from src.log_manager import get_log_manager

    logger = get_log_manager().get_logger("AdvancedFolders.ConfigDialog")
except ImportError:
    logger = logging.getLogger(__name__)


class FolderConfigurationDialog(QDialog):
    """
    Enterprise-grade folder configuration dialog.

    Provides comprehensive interface for configuring advanced folder settings
    including directory selection, search parameters, file filters, and display
    options. Implements professional UI patterns with full accessibility support.

    Signals:
        configuration_saved: Emitted when configuration is successfully saved
        configuration_cancelled: Emitted when dialog is cancelled
        validation_error: Emitted when validation fails
        help_requested: Emitted when help is requested
    """

    # Signals for external integration
    configuration_saved = pyqtSignal(object)  # FolderConfiguration object
    configuration_cancelled = pyqtSignal()
    validation_error = pyqtSignal(str)  # Error message
    help_requested = pyqtSignal(str)  # Help topic

    def __init__(self, parent=None, configuration=None, mode="create"):
        """
        Initialize the configuration dialog.

        Args:
            parent: Parent widget
            configuration: Existing FolderConfiguration to edit (optional)
            mode: Dialog mode - 'create', 'edit', or 'view'
        """
        super().__init__(parent)

        # Store configuration and mode
        self.configuration = configuration or FolderConfiguration()
        self.mode = mode
        self.is_modified = False
        self.validation_timer = None

        # Initialize UI components
        self.tab_widget = None
        self.button_box = None
        self.status_label = None
        self._toast = None
        self.help_text = None

        # Tab instances
        self.general_tab = None
        self.search_tab = None
        self.filters_tab = None
        self.display_tab = None

        # Initialize the dialog
        self._setup_ui()
        self._setup_connections()
        self._setup_validation()
        self._load_configuration()
        self._setup_accessibility()

        logger.info(f"FolderConfigurationDialog initialized in {mode} mode")

    def _setup_ui(self):
        """Setup the main user interface."""
        if not PYQT5_AVAILABLE:
            return

        # Configure dialog properties
        self.setWindowTitle(TITLE)
        self.setMinimumSize(DIALOG_MIN_WIDTH, DIALOG_MIN_HEIGHT)
        self.resize(DIALOG_PREFERRED_WIDTH, DIALOG_PREFERRED_HEIGHT)
        self.setModal(True)

        # Apply styling
        self.setStyleSheet(Styles.DIALOG_STYLE)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
        )
        main_layout.setSpacing(Layout.SECTION_SPACING)

        # Create header section
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)

        # Create main content area with splitter
        content_splitter = self._create_content_area()
        main_layout.addWidget(content_splitter, 1)

        # Create status section
        status_widget = self._create_status_section()
        main_layout.addWidget(status_widget)

        # Create button section
        button_widget = self._create_button_section()
        main_layout.addWidget(button_widget)

        # Set focus to first tab
        if self.tab_widget and self.tab_widget.count() > 0:
            self.tab_widget.setCurrentIndex(0)
            self.tab_widget.currentWidget().setFocus()

    def _create_header(self):
        """Create the dialog header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.NoFrame)
        header_frame.setFixedHeight(Layout.HEADER_HEIGHT)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        title_label = QLabel(TITLE)
        title_label.setFont(Fonts.title_font())
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")

        # Mode indicator
        mode_text = {
            "create": "Create New Configuration",
            "edit": "Edit Configuration",
            "view": "View Configuration",
        }.get(self.mode, "Configuration")

        mode_label = QLabel(f"• {mode_text}")
        mode_label.setFont(Fonts.label_font())
        mode_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(mode_label)

        return header_frame

    def _create_content_area(self):
        """Create the main content area with tabs and help panel."""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(Styles.TAB_WIDGET_STYLE)
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setAccessibleName("Folder configuration sections")
        self.tab_widget.setAccessibleName("Folder configuration sections")

        # Create tabs if available
        if TABS_AVAILABLE:
            self._create_tabs()
        else:
            # Fallback placeholder
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.addWidget(QLabel("Configuration tabs are loading..."))
            self.tab_widget.addTab(placeholder, "Configuration")

        # Create help panel
        help_panel = self._create_help_panel()

        # Add to splitter
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(help_panel)

        # Set splitter proportions (75% tabs, 25% help)
        splitter.setSizes([600, 200])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        return splitter

    def _create_tabs(self):
        """Create and configure all configuration tabs."""
        try:
            # General configuration tab
            self.general_tab = GeneralConfigTab(
                configuration=self.configuration, mode=self.mode
            )
            self.tab_widget.addTab(self.general_tab, f"{Icons.SETTINGS} General")

            # Search configuration tab
            self.search_tab = SearchConfigTab(
                configuration=self.configuration, mode=self.mode
            )
            self.tab_widget.addTab(self.search_tab, f"{Icons.SEARCH} Search")

            # Filters configuration tab
            self.filters_tab = FiltersConfigTab(
                configuration=self.configuration, mode=self.mode
            )
            self.tab_widget.addTab(self.filters_tab, f"{Icons.FILE} Filters")

            # Display configuration tab
            self.display_tab = DisplayConfigTab(
                configuration=self.configuration, mode=self.mode
            )
            self.tab_widget.addTab(self.display_tab, f"{Icons.IMAGE} Display")

            logger.debug("All configuration tabs created successfully")

        except Exception as e:
            logger.error(f"Error creating configuration tabs: {str(e)}")
            # Create fallback single tab
            fallback_tab = QWidget()
            fallback_layout = QVBoxLayout(fallback_tab)
            fallback_layout.addWidget(
                QLabel(f"Error loading configuration interface: {str(e)}")
            )
            self.tab_widget.addTab(fallback_tab, "Configuration")

    def _create_help_panel(self):
        """Create the contextual help panel."""
        help_group = QGroupBox("Help & Information")
        help_group.setStyleSheet(Styles.GROUP_BOX_STYLE)
        help_group.setMaximumWidth(300)
        help_group.setMinimumWidth(250)

        help_layout = QVBoxLayout(help_group)
        help_layout.setContentsMargins(10, 15, 10, 10)
        help_layout.setSpacing(10)

        # Help text area
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setMaximumHeight(200)
        self.help_text.setAccessibleName("Contextual help text")
        self.help_text.setStyleSheet(
            f"""
            QTextEdit {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                padding: 8px;
                font-size: 9pt;
            }}
        """
        )

        # Set initial help text
        self._update_help_content("general")

        # Help buttons
        help_buttons_layout = QHBoxLayout()

        help_button = SecondaryButton(f"{Icons.INFO} More Help")
        help_button.clicked.connect(lambda: self.help_requested.emit("main"))

        help_layout.addWidget(self.help_text)
        help_layout.addLayout(help_buttons_layout)
        help_buttons_layout.addWidget(help_button)
        help_buttons_layout.addStretch()

        return help_group

    def _create_status_section(self):
        """Create the status information section."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setLineWidth(1)
        status_frame.setFixedHeight(Layout.STATUS_BAR_HEIGHT + 10)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(Fonts.label_font())
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.status_label.setVisible(False)  # replaced by ToastNotification
        self._toast = (
            ToastNotification(self, role="info") if ToastNotification else None
        )

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        return status_frame

    def _create_button_section(self):
        """Create the dialog button section."""
        # Create custom button box for better control
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(Layout.BUTTON_SPACING)

        # Help button (left-aligned)
        help_button = SecondaryButton(f"{Icons.INFO} Help")
        help_button.clicked.connect(lambda: self.help_requested.emit("dialog"))

        # Spacer
        button_layout.addWidget(help_button)
        button_layout.addStretch()

        # Action buttons (right-aligned)
        if self.mode != "view":
            # Save button
            save_button = PrimaryButton(f"{Icons.SAVE} Save")
            save_button.setDefault(True)
            save_button.clicked.connect(self._save_configuration)

            # Apply button (for immediate application without closing)
            apply_button = SecondaryButton("Apply")
            apply_button.clicked.connect(self._apply_configuration)

            button_layout.addWidget(apply_button)
            button_layout.addWidget(save_button)

        # Cancel/Close button
        cancel_text = "Close" if self.mode == "view" else f"{Icons.CANCEL} Cancel"
        cancel_button = SecondaryButton(cancel_text)
        cancel_button.clicked.connect(self._cancel_dialog)

        button_layout.addWidget(cancel_button)

        return button_frame

    def _setup_connections(self):
        """Setup signal connections between components."""
        # Tab change signals
        if self.tab_widget:
            self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Tab modification signals
        if hasattr(self, "general_tab") and self.general_tab:
            self.general_tab.data_changed.connect(self._on_data_changed)

        if hasattr(self, "search_tab") and self.search_tab:
            self.search_tab.data_changed.connect(self._on_data_changed)

        if hasattr(self, "filters_tab") and self.filters_tab:
            self.filters_tab.data_changed.connect(self._on_data_changed)

        if hasattr(self, "display_tab") and self.display_tab:
            self.display_tab.data_changed.connect(self._on_data_changed)

    def _setup_validation(self):
        """Setup real-time validation system."""
        # Create validation timer for debounced validation
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_configuration)

        # Initial validation
        QTimer.singleShot(100, self._validate_configuration)

    def _setup_accessibility(self):
        """Setup accessibility features and keyboard navigation."""
        # Set accessible names and descriptions
        self.setAccessibleName("Advanced Folders Configuration Dialog")
        self.setAccessibleDescription(
            "Configure advanced folder settings including directories, "
            "search parameters, file filters, and display options"
        )

        # Setup keyboard shortcuts
        try:
            from PyQt5.QtGui import QKeySequence
            from PyQt5.QtWidgets import QShortcut

            # Save shortcut
            save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            save_shortcut.activated.connect(self._save_configuration)

            # Cancel shortcut
            cancel_shortcut = QShortcut(QKeySequence("Escape"), self)
            cancel_shortcut.activated.connect(self._cancel_dialog)

            # Help shortcut
            help_shortcut = QShortcut(QKeySequence("F1"), self)
            help_shortcut.activated.connect(lambda: self.help_requested.emit("dialog"))

        except ImportError:
            pass

    def _load_configuration(self):
        """Load existing configuration into the interface."""
        if not self.configuration:
            return

        try:
            # Load data into each tab
            if self.general_tab:
                self.general_tab.load_configuration(self.configuration)

            if self.search_tab:
                self.search_tab.load_configuration(self.configuration)

            if self.filters_tab:
                self.filters_tab.load_configuration(self.configuration)

            if self.display_tab:
                self.display_tab.load_configuration(self.configuration)

            self._update_status("Configuration loaded successfully")
            logger.debug("Configuration loaded into dialog")

        except Exception as e:
            error_msg = f"Error loading configuration: {str(e)}"
            logger.error(error_msg)
            self._update_status(error_msg, is_error=True)

    def _save_configuration(self):
        """Save the current configuration."""
        try:
            # Validate configuration
            validation_result = self._validate_configuration()
            if not validation_result.is_valid:
                self._show_validation_errors(validation_result.errors)
                return

            # Collect data from all tabs
            config_data = self._collect_configuration_data()

            # Create or update configuration object
            if self.mode == "create":
                configuration = FolderConfiguration(**config_data)
            else:
                configuration = self.configuration
                for key, value in config_data.items():
                    setattr(configuration, key, value)

            # Save to database if backend is available
            if BACKEND_AVAILABLE:
                repository = FolderConfigurationRepository()
                if self.mode == "create":
                    repository.create(configuration)
                else:
                    repository.update(configuration)

            # Emit success signal
            self.configuration_saved.emit(configuration)
            self._update_status("Configuration saved successfully")

            # Close dialog
            self.accept()

            logger.info(f"Configuration saved successfully in {self.mode} mode")

        except Exception as e:
            error_msg = f"Error saving configuration: {str(e)}"
            logger.error(error_msg)
            self._update_status(error_msg, is_error=True)
            Modal("Save Error", error_msg, ["OK"], self).exec_()

    def _apply_configuration(self):
        """Apply configuration without closing dialog."""
        try:
            # Validate and collect data
            validation_result = self._validate_configuration()
            if not validation_result.is_valid:
                self._show_validation_errors(validation_result.errors)
                return

            config_data = self._collect_configuration_data()

            # Update configuration object
            for key, value in config_data.items():
                setattr(self.configuration, key, value)

            # Emit signal for immediate application
            self.configuration_saved.emit(self.configuration)
            self._update_status("Configuration applied")

            logger.debug("Configuration applied successfully")

        except Exception as e:
            error_msg = f"Error applying configuration: {str(e)}"
            logger.error(error_msg)
            self._update_status(error_msg, is_error=True)

    def _cancel_dialog(self):
        """Cancel the dialog and check for unsaved changes."""
        if self.is_modified and self.mode != "view":
            if (
                Modal(
                    "Unsaved Changes",
                    "You have unsaved changes. Are you sure you want to cancel?",
                    ["Yes", "No"],
                    self,
                ).exec_()
                != QDialog.Accepted
            ):
                return

        self.configuration_cancelled.emit()
        self.reject()
        logger.debug("Configuration dialog cancelled")

    def _validate_configuration(self):
        """Validate the current configuration."""
        errors = []

        try:
            # Validate each tab
            if self.general_tab:
                tab_errors = self.general_tab.validate()
                errors.extend(tab_errors)

            if self.search_tab:
                tab_errors = self.search_tab.validate()
                errors.extend(tab_errors)

            if self.filters_tab:
                tab_errors = self.filters_tab.validate()
                errors.extend(tab_errors)

            if self.display_tab:
                tab_errors = self.display_tab.validate()
                errors.extend(tab_errors)

            # Create validation result
            is_valid = len(errors) == 0
            validation_result = ValidationResult(is_valid, errors)

            # Update UI based on validation
            if is_valid:
                self._update_status("Configuration is valid")
            else:
                self._update_status(f"Validation errors: {len(errors)}", is_error=True)

            return validation_result

        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            return ValidationResult(False, [f"Validation error: {str(e)}"])

    def _collect_configuration_data(self):
        """Collect configuration data from all tabs."""
        config_data = {}

        try:
            if self.general_tab:
                config_data.update(self.general_tab.get_data())

            if self.search_tab:
                config_data.update(self.search_tab.get_data())

            if self.filters_tab:
                config_data.update(self.filters_tab.get_data())

            if self.display_tab:
                config_data.update(self.display_tab.get_data())

            logger.debug(f"Collected configuration data: {list(config_data.keys())}")
            return config_data

        except Exception as e:
            logger.error(f"Error collecting configuration data: {str(e)}")
            raise

    def _show_validation_errors(self, errors):
        """Show validation errors to the user."""
        if not errors:
            return

        error_text = "\
".join(
            [f"• {error}" for error in errors]
        )
        Modal(
            "Validation Errors",
            f"Please correct the following errors:\
\
{error_text}",
            ["OK"],
            self,
        ).exec_()

        self.validation_error.emit(error_text)

    def _update_status(self, message, is_error=False):
        """Update the status bar message."""
        if self._toast:
            self._toast.show_message(message, "error" if is_error else "info")

    def _update_help_content(self, topic):
        """Update the help panel content based on current context."""
        help_content = {
            "general": """
                <h4>General Configuration</h4>
                <p>Configure basic folder settings including name, description, and target directories.</p>
                <ul>
                    <li><b>Name:</b> Unique identifier for this folder configuration</li>
                    <li><b>Description:</b> Optional description for documentation</li>
                    <li><b>Directories:</b> Target directories to include in this configuration</li>
                </ul>
            """,
            "search": """
                <h4>Search Configuration</h4>
                <p>Configure advanced search parameters and indexing options.</p>
                <ul>
                    <li><b>Content Search:</b> Enable searching within file contents</li>
                    <li><b>Metadata:</b> Include file metadata in search operations</li>
                    <li><b>Indexing:</b> Configure automatic indexing for faster searches</li>
                </ul>
            """,
            "filters": """
                <h4>File Type Filters</h4>
                <p>Configure which file types to include or exclude from this folder.</p>
                <ul>
                    <li><b>Categories:</b> Predefined file type categories</li>
                    <li><b>Extensions:</b> Custom file extensions to include</li>
                    <li><b>Exclusions:</b> Patterns to exclude from results</li>
                </ul>
            """,
            "display": """
                <h4>Display Options</h4>
                <p>Configure how files and folders are displayed in the interface.</p>
                <ul>
                    <li><b>View Mode:</b> List, grid, or detailed view</li>
                    <li><b>Sorting:</b> Default sort order and criteria</li>
                    <li><b>Columns:</b> Which information columns to display</li>
                </ul>
            """,
        }

        if self.help_text:
            content = help_content.get(topic, help_content["general"])
            self.help_text.setHtml(content)

    def _on_tab_changed(self, index):
        """Handle tab change events."""
        if not self.tab_widget:
            return

        # Update help content based on current tab
        tab_names = ["general", "search", "filters", "display"]
        if 0 <= index < len(tab_names):
            self._update_help_content(tab_names[index])

        # Focus the new tab
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.setFocus()

        logger.debug(f"Tab changed to index {index}")

    def _on_data_changed(self):
        """Handle data change events from tabs."""
        self.is_modified = True

        # Trigger delayed validation
        if self.validation_timer:
            self.validation_timer.start(500)  # 500ms delay

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.is_modified and self.mode != "view":
            if Modal:
                dlg = Modal(
                    "Unsaved Changes",
                    "You have unsaved changes. Save before closing?",
                    ["Save", "Discard", "Cancel"],
                    self,
                )
                dlg.exec_()
                label = dlg._clicked_label
                if label == "Save":
                    self._save_configuration()
                    event.accept()
                elif label == "Discard":
                    event.accept()
                else:  # "Cancel" or window-X close
                    event.ignore()
            else:
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "You have unsaved changes. Save before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save,
                )
                if reply == QMessageBox.Save:
                    self._save_configuration()
                    event.accept()
                elif reply == QMessageBox.Discard:
                    event.accept()
                else:
                    event.ignore()
        else:
            event.accept()

    def get_configuration(self):
        """Get the current configuration object."""
        return self.configuration

    def set_configuration(self, configuration):
        """Set a new configuration object."""
        self.configuration = configuration
        self._load_configuration()

    def get_mode(self):
        """Get the current dialog mode."""
        return self.mode

    def set_read_only(self, read_only=True):
        """Set the dialog to read-only mode."""
        self.mode = "view" if read_only else "edit"

        # Update all tabs
        for tab in [
            self.general_tab,
            self.search_tab,
            self.filters_tab,
            self.display_tab,
        ]:
            if tab and hasattr(tab, "set_read_only"):
                tab.set_read_only(read_only)


# Convenience functions for dialog usage
def create_folder_configuration(parent=None):
    """Create a new folder configuration using the dialog."""
    dialog = FolderConfigurationDialog(parent=parent, mode="create")

    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_configuration()
    return None


def edit_folder_configuration(configuration, parent=None):
    """Edit an existing folder configuration using the dialog."""
    dialog = FolderConfigurationDialog(
        parent=parent, configuration=configuration, mode="edit"
    )

    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_configuration()
    return None


def view_folder_configuration(configuration, parent=None):
    """View a folder configuration in read-only mode."""
    dialog = FolderConfigurationDialog(
        parent=parent, configuration=configuration, mode="view"
    )

    dialog.exec_()


# Testing and development support
if __name__ == "__main__":
    # Create test application
    app = (
        QApplication(sys.argv)
        if not QApplication.instance()
        else QApplication.instance()
    )

    # Create test dialog
    dialog = FolderConfigurationDialog(mode="create")

    # Show dialog
    result = dialog.exec_()
    print(f"Dialog result: {result}")

    if result == QDialog.Accepted:
        config = dialog.get_configuration()
        print(f"Configuration created: {config}")

    # Clean up
