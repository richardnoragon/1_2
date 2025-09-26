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

import sys
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
        QPushButton, QDialogButtonBox, QLabel, QWidget,
        QApplication, QMessageBox, QSizePolicy, QFrame,
        QSplitter, QTextEdit, QGroupBox
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Provide fallback base classes
    QDialog = object
    pyqtSignal = None

# Import constants and styling
try:
    from .constants import (
        Colors, Fonts, Layout, Icons, Styles, Accessibility,
        DIALOG_MIN_WIDTH, DIALOG_MIN_HEIGHT, DIALOG_PREFERRED_WIDTH,
        DIALOG_PREFERRED_HEIGHT, TITLE
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
        GeneralConfigTab, SearchConfigTab,
        FiltersConfigTab, DisplayConfigTab
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
    logger = get_log_manager().get_logger('AdvancedFolders.ConfigDialog')
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
    
    def __init__(self, parent=None, configuration=None, mode='create'):
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
            Layout.CONTENT_MARGIN, Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN, Layout.CONTENT_MARGIN
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
            'create': 'Create New Configuration',
            'edit': 'Edit Configuration', 
            'view': 'View Configuration'
        }.get(self.mode, 'Configuration')
        
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
        
        # Create tabs if available
        if TABS_AVAILABLE:
            self._create_tabs()
        else:
            # Fallback placeholder
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.addWidget(
                QLabel("Configuration tabs are loading...")
            )
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
                configuration=self.configuration,
                mode=self.mode
            )
            self.tab_widget.addTab(self.general_tab, f"{Icons.SETTINGS} General")
            
            # Search configuration tab
            self.search_tab = SearchConfigTab(
                configuration=self.configuration,
                mode=self.mode
            )
            self.tab_widget.addTab(self.search_tab, f"{Icons.SEARCH} Search")
            
            # Filters configuration tab
            self.filters_tab = FiltersConfigTab(
                configuration=self.configuration,
                mode=self.mode
            )
            self.tab_widget.addTab(self.filters_tab, f"{Icons.FILE} Filters")
            
            # Display configuration tab
            self.display_tab = DisplayConfigTab(
                configuration=self.configuration,
                mode=self.mode
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
        self.help_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                padding: 8px;
                font-size: 9pt;
            }}
        """)
        
        # Set initial help text
        self._update_help_content("general")
        
        # Help buttons
        help_buttons_layout = QHBoxLayout()
        
        help_button = QPushButton(f"{Icons.INFO} More Help")
        help_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)
        help_button.clicked.connect(lambda: self.help_requested.emit("main"))
        
        help_layout.addWidget(self.help_text)
        help_layout.addLayout(help_buttons_layout)
        help_buttons_layout.addWidget(help_button)
        help_buttons_layout.addStretch()\n        \n        return help_group\n    \n    def _create_status_section(self):\n        \"\"\"Create the status information section.\"\"\"\n        status_frame = QFrame()\n        status_frame.setFrameStyle(QFrame.StyledPanel)\n        status_frame.setLineWidth(1)\n        status_frame.setFixedHeight(Layout.STATUS_BAR_HEIGHT + 10)\n        \n        status_layout = QHBoxLayout(status_frame)\n        status_layout.setContentsMargins(10, 5, 10, 5)\n        \n        # Status label\n        self.status_label = QLabel(\"Ready\")\n        self.status_label.setFont(Fonts.label_font())\n        self.status_label.setStyleSheet(f\"color: {Colors.TEXT_SECONDARY};\")\n        \n        status_layout.addWidget(self.status_label)\n        status_layout.addStretch()\n        \n        return status_frame\n    \n    def _create_button_section(self):\n        \"\"\"Create the dialog button section.\"\"\"\n        # Create custom button box for better control\n        button_frame = QFrame()\n        button_layout = QHBoxLayout(button_frame)\n        button_layout.setContentsMargins(0, 10, 0, 0)\n        button_layout.setSpacing(Layout.BUTTON_SPACING)\n        \n        # Help button (left-aligned)\n        help_button = QPushButton(f\"{Icons.INFO} Help\")\n        help_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        help_button.clicked.connect(lambda: self.help_requested.emit(\"dialog\"))\n        \n        # Spacer\n        button_layout.addWidget(help_button)\n        button_layout.addStretch()\n        \n        # Action buttons (right-aligned)\n        if self.mode != 'view':\n            # Save button\n            save_button = QPushButton(f\"{Icons.SAVE} Save\")\n            save_button.setStyleSheet(Styles.BUTTON_PRIMARY_STYLE)\n            save_button.setDefault(True)\n            save_button.clicked.connect(self._save_configuration)\n            \n            # Apply button (for immediate application without closing)\n            apply_button = QPushButton(\"Apply\")\n            apply_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n            apply_button.clicked.connect(self._apply_configuration)\n            \n            button_layout.addWidget(apply_button)\n            button_layout.addWidget(save_button)\n        \n        # Cancel/Close button\n        cancel_text = \"Close\" if self.mode == 'view' else f\"{Icons.CANCEL} Cancel\"\n        cancel_button = QPushButton(cancel_text)\n        cancel_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        cancel_button.clicked.connect(self._cancel_dialog)\n        \n        button_layout.addWidget(cancel_button)\n        \n        return button_frame\n    \n    def _setup_connections(self):\n        \"\"\"Setup signal connections between components.\"\"\"\n        # Tab change signals\n        if self.tab_widget:\n            self.tab_widget.currentChanged.connect(self._on_tab_changed)\n        \n        # Tab modification signals\n        if hasattr(self, 'general_tab') and self.general_tab:\n            self.general_tab.data_changed.connect(self._on_data_changed)\n        \n        if hasattr(self, 'search_tab') and self.search_tab:\n            self.search_tab.data_changed.connect(self._on_data_changed)\n        \n        if hasattr(self, 'filters_tab') and self.filters_tab:\n            self.filters_tab.data_changed.connect(self._on_data_changed)\n        \n        if hasattr(self, 'display_tab') and self.display_tab:\n            self.display_tab.data_changed.connect(self._on_data_changed)\n    \n    def _setup_validation(self):\n        \"\"\"Setup real-time validation system.\"\"\"\n        # Create validation timer for debounced validation\n        self.validation_timer = QTimer()\n        self.validation_timer.setSingleShot(True)\n        self.validation_timer.timeout.connect(self._validate_configuration)\n        \n        # Initial validation\n        QTimer.singleShot(100, self._validate_configuration)\n    \n    def _setup_accessibility(self):\n        \"\"\"Setup accessibility features and keyboard navigation.\"\"\"\n        # Set accessible names and descriptions\n        self.setAccessibleName(\"Advanced Folders Configuration Dialog\")\n        self.setAccessibleDescription(\n            \"Configure advanced folder settings including directories, \"\n            \"search parameters, file filters, and display options\"\n        )\n        \n        # Setup keyboard shortcuts\n        try:\n            from PyQt5.QtWidgets import QShortcut\n            from PyQt5.QtGui import QKeySequence\n            \n            # Save shortcut\n            save_shortcut = QShortcut(QKeySequence(\"Ctrl+S\"), self)\n            save_shortcut.activated.connect(self._save_configuration)\n            \n            # Cancel shortcut\n            cancel_shortcut = QShortcut(QKeySequence(\"Escape\"), self)\n            cancel_shortcut.activated.connect(self._cancel_dialog)\n            \n            # Help shortcut\n            help_shortcut = QShortcut(QKeySequence(\"F1\"), self)\n            help_shortcut.activated.connect(lambda: self.help_requested.emit(\"dialog\"))\n            \n        except ImportError:\n            pass\n    \n    def _load_configuration(self):\n        \"\"\"Load existing configuration into the interface.\"\"\"\n        if not self.configuration:\n            return\n        \n        try:\n            # Load data into each tab\n            if self.general_tab:\n                self.general_tab.load_configuration(self.configuration)\n            \n            if self.search_tab:\n                self.search_tab.load_configuration(self.configuration)\n            \n            if self.filters_tab:\n                self.filters_tab.load_configuration(self.configuration)\n            \n            if self.display_tab:\n                self.display_tab.load_configuration(self.configuration)\n            \n            self._update_status(\"Configuration loaded successfully\")\n            logger.debug(\"Configuration loaded into dialog\")\n            \n        except Exception as e:\n            error_msg = f\"Error loading configuration: {str(e)}\"\n            logger.error(error_msg)\n            self._update_status(error_msg, is_error=True)\n    \n    def _save_configuration(self):\n        \"\"\"Save the current configuration.\"\"\"\n        try:\n            # Validate configuration\n            validation_result = self._validate_configuration()\n            if not validation_result.is_valid:\n                self._show_validation_errors(validation_result.errors)\n                return\n            \n            # Collect data from all tabs\n            config_data = self._collect_configuration_data()\n            \n            # Create or update configuration object\n            if self.mode == 'create':\n                configuration = FolderConfiguration(**config_data)\n            else:\n                configuration = self.configuration\n                for key, value in config_data.items():\n                    setattr(configuration, key, value)\n            \n            # Save to database if backend is available\n            if BACKEND_AVAILABLE:\n                repository = FolderConfigurationRepository()\n                if self.mode == 'create':\n                    repository.create(configuration)\n                else:\n                    repository.update(configuration)\n            \n            # Emit success signal\n            self.configuration_saved.emit(configuration)\n            self._update_status(\"Configuration saved successfully\")\n            \n            # Close dialog\n            self.accept()\n            \n            logger.info(f\"Configuration saved successfully in {self.mode} mode\")\n            \n        except Exception as e:\n            error_msg = f\"Error saving configuration: {str(e)}\"\n            logger.error(error_msg)\n            self._update_status(error_msg, is_error=True)\n            QMessageBox.critical(self, \"Save Error\", error_msg)\n    \n    def _apply_configuration(self):\n        \"\"\"Apply configuration without closing dialog.\"\"\"\n        try:\n            # Validate and collect data\n            validation_result = self._validate_configuration()\n            if not validation_result.is_valid:\n                self._show_validation_errors(validation_result.errors)\n                return\n            \n            config_data = self._collect_configuration_data()\n            \n            # Update configuration object\n            for key, value in config_data.items():\n                setattr(self.configuration, key, value)\n            \n            # Emit signal for immediate application\n            self.configuration_saved.emit(self.configuration)\n            self._update_status(\"Configuration applied\")\n            \n            logger.debug(\"Configuration applied successfully\")\n            \n        except Exception as e:\n            error_msg = f\"Error applying configuration: {str(e)}\"\n            logger.error(error_msg)\n            self._update_status(error_msg, is_error=True)\n    \n    def _cancel_dialog(self):\n        \"\"\"Cancel the dialog and check for unsaved changes.\"\"\"\n        if self.is_modified and self.mode != 'view':\n            reply = QMessageBox.question(\n                self,\n                \"Unsaved Changes\",\n                \"You have unsaved changes. Are you sure you want to cancel?\",\n                QMessageBox.Yes | QMessageBox.No,\n                QMessageBox.No\n            )\n            \n            if reply != QMessageBox.Yes:\n                return\n        \n        self.configuration_cancelled.emit()\n        self.reject()\n        logger.debug(\"Configuration dialog cancelled\")\n    \n    def _validate_configuration(self):\n        \"\"\"Validate the current configuration.\"\"\"\n        errors = []\n        \n        try:\n            # Validate each tab\n            if self.general_tab:\n                tab_errors = self.general_tab.validate()\n                errors.extend(tab_errors)\n            \n            if self.search_tab:\n                tab_errors = self.search_tab.validate()\n                errors.extend(tab_errors)\n            \n            if self.filters_tab:\n                tab_errors = self.filters_tab.validate()\n                errors.extend(tab_errors)\n            \n            if self.display_tab:\n                tab_errors = self.display_tab.validate()\n                errors.extend(tab_errors)\n            \n            # Create validation result\n            is_valid = len(errors) == 0\n            validation_result = ValidationResult(is_valid, errors)\n            \n            # Update UI based on validation\n            if is_valid:\n                self._update_status(\"Configuration is valid\")\n            else:\n                self._update_status(f\"Validation errors: {len(errors)}\", is_error=True)\n            \n            return validation_result\n            \n        except Exception as e:\n            logger.error(f\"Error during validation: {str(e)}\")\n            return ValidationResult(False, [f\"Validation error: {str(e)}\"])\n    \n    def _collect_configuration_data(self):\n        \"\"\"Collect configuration data from all tabs.\"\"\"\n        config_data = {}\n        \n        try:\n            if self.general_tab:\n                config_data.update(self.general_tab.get_data())\n            \n            if self.search_tab:\n                config_data.update(self.search_tab.get_data())\n            \n            if self.filters_tab:\n                config_data.update(self.filters_tab.get_data())\n            \n            if self.display_tab:\n                config_data.update(self.display_tab.get_data())\n            \n            logger.debug(f\"Collected configuration data: {list(config_data.keys())}\")\n            return config_data\n            \n        except Exception as e:\n            logger.error(f\"Error collecting configuration data: {str(e)}\")\n            raise\n    \n    def _show_validation_errors(self, errors):\n        \"\"\"Show validation errors to the user.\"\"\"\n        if not errors:\n            return\n        \n        error_text = \"\\n\".join([f\"• {error}\" for error in errors])\n        QMessageBox.warning(\n            self,\n            \"Validation Errors\",\n            f\"Please correct the following errors:\\n\\n{error_text}\"\n        )\n        \n        self.validation_error.emit(error_text)\n    \n    def _update_status(self, message, is_error=False):\n        \"\"\"Update the status bar message.\"\"\"\n        if self.status_label:\n            self.status_label.setText(message)\n            if is_error:\n                self.status_label.setStyleSheet(f\"color: {Colors.TEXT_ERROR};\")\n            else:\n                self.status_label.setStyleSheet(f\"color: {Colors.TEXT_SECONDARY};\")\n    \n    def _update_help_content(self, topic):\n        \"\"\"Update the help panel content based on current context.\"\"\"\n        help_content = {\n            \"general\": \"\"\"\n                <h4>General Configuration</h4>\n                <p>Configure basic folder settings including name, description, and target directories.</p>\n                <ul>\n                    <li><b>Name:</b> Unique identifier for this folder configuration</li>\n                    <li><b>Description:</b> Optional description for documentation</li>\n                    <li><b>Directories:</b> Target directories to include in this configuration</li>\n                </ul>\n            \"\"\",\n            \"search\": \"\"\"\n                <h4>Search Configuration</h4>\n                <p>Configure advanced search parameters and indexing options.</p>\n                <ul>\n                    <li><b>Content Search:</b> Enable searching within file contents</li>\n                    <li><b>Metadata:</b> Include file metadata in search operations</li>\n                    <li><b>Indexing:</b> Configure automatic indexing for faster searches</li>\n                </ul>\n            \"\"\",\n            \"filters\": \"\"\"\n                <h4>File Type Filters</h4>\n                <p>Configure which file types to include or exclude from this folder.</p>\n                <ul>\n                    <li><b>Categories:</b> Predefined file type categories</li>\n                    <li><b>Extensions:</b> Custom file extensions to include</li>\n                    <li><b>Exclusions:</b> Patterns to exclude from results</li>\n                </ul>\n            \"\"\",\n            \"display\": \"\"\"\n                <h4>Display Options</h4>\n                <p>Configure how files and folders are displayed in the interface.</p>\n                <ul>\n                    <li><b>View Mode:</b> List, grid, or detailed view</li>\n                    <li><b>Sorting:</b> Default sort order and criteria</li>\n                    <li><b>Columns:</b> Which information columns to display</li>\n                </ul>\n            \"\"\"\n        }\n        \n        if self.help_text:\n            content = help_content.get(topic, help_content[\"general\"])\n            self.help_text.setHtml(content)\n    \n    def _on_tab_changed(self, index):\n        \"\"\"Handle tab change events.\"\"\"\n        if not self.tab_widget:\n            return\n        \n        # Update help content based on current tab\n        tab_names = [\"general\", \"search\", \"filters\", \"display\"]\n        if 0 <= index < len(tab_names):\n            self._update_help_content(tab_names[index])\n        \n        # Focus the new tab\n        current_widget = self.tab_widget.currentWidget()\n        if current_widget:\n            current_widget.setFocus()\n        \n        logger.debug(f\"Tab changed to index {index}\")\n    \n    def _on_data_changed(self):\n        \"\"\"Handle data change events from tabs.\"\"\"\n        self.is_modified = True\n        \n        # Trigger delayed validation\n        if self.validation_timer:\n            self.validation_timer.start(500)  # 500ms delay\n    \n    def closeEvent(self, event):\n        \"\"\"Handle dialog close event.\"\"\"\n        if self.is_modified and self.mode != 'view':\n            reply = QMessageBox.question(\n                self,\n                \"Unsaved Changes\",\n                \"You have unsaved changes. Save before closing?\",\n                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,\n                QMessageBox.Save\n            )\n            \n            if reply == QMessageBox.Save:\n                self._save_configuration()\n                event.accept()\n            elif reply == QMessageBox.Discard:\n                event.accept()\n            else:\n                event.ignore()\n        else:\n            event.accept()\n    \n    def get_configuration(self):\n        \"\"\"Get the current configuration object.\"\"\"\n        return self.configuration\n    \n    def set_configuration(self, configuration):\n        \"\"\"Set a new configuration object.\"\"\"\n        self.configuration = configuration\n        self._load_configuration()\n    \n    def get_mode(self):\n        \"\"\"Get the current dialog mode.\"\"\"\n        return self.mode\n    \n    def set_read_only(self, read_only=True):\n        \"\"\"Set the dialog to read-only mode.\"\"\"\n        self.mode = 'view' if read_only else 'edit'\n        \n        # Update all tabs\n        for tab in [self.general_tab, self.search_tab, self.filters_tab, self.display_tab]:\n            if tab and hasattr(tab, 'set_read_only'):\n                tab.set_read_only(read_only)\n\n\n# Convenience functions for dialog usage\ndef create_folder_configuration(parent=None):\n    \"\"\"Create a new folder configuration using the dialog.\"\"\"\n    dialog = FolderConfigurationDialog(parent=parent, mode='create')\n    \n    if dialog.exec_() == QDialog.Accepted:\n        return dialog.get_configuration()\n    return None\n\n\ndef edit_folder_configuration(configuration, parent=None):\n    \"\"\"Edit an existing folder configuration using the dialog.\"\"\"\n    dialog = FolderConfigurationDialog(\n        parent=parent, \n        configuration=configuration, \n        mode='edit'\n    )\n    \n    if dialog.exec_() == QDialog.Accepted:\n        return dialog.get_configuration()\n    return None\n\n\ndef view_folder_configuration(configuration, parent=None):\n    \"\"\"View a folder configuration in read-only mode.\"\"\"\n    dialog = FolderConfigurationDialog(\n        parent=parent,\n        configuration=configuration,\n        mode='view'\n    )\n    \n    dialog.exec_()\n\n\n# Testing and development support\nif __name__ == \"__main__\":\n    # Create test application\n    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()\n    \n    # Create test dialog\n    dialog = FolderConfigurationDialog(mode='create')\n    \n    # Show dialog\n    result = dialog.exec_()\n    print(f\"Dialog result: {result}\")\n    \n    if result == QDialog.Accepted:\n        config = dialog.get_configuration()\n        print(f\"Configuration created: {config}\")\n    \n    # Clean up\n    if not QApplication.instance():\n        sys.exit(app.exec_())