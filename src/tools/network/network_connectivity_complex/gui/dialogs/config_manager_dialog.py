"""Configuration manager dialog for network connectivity tools."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton
from src.gui.components.inputs import TextInput
from src.gui.components.loading_indicator import LoadingIndicator

from ...config.config_profiles import get_profile_manager
from ...config.config_validator import ValidationSeverity, get_config_validator
from ...core.config_service import ConfigurationEvent, get_config_service
from ...core.notification_service import get_notification_service


class ConfigValidationWorker(QThread):
    """Worker thread for configuration validation."""

    validation_complete = pyqtSignal(list)  # List of validation results

    def __init__(self, config_data: Dict[str, Any]):
        super().__init__()
        self.config_data = config_data

    def run(self):
        """Run validation in background thread."""
        try:
            validator = get_config_validator()
            results = validator.validate_configuration(self.config_data)
            self.validation_complete.emit(results)
        except Exception as e:
            # Emit empty list on error
            self.validation_complete.emit([])


class ProfileSelectionWidget(QWidget):
    """Widget for selecting and managing configuration profiles."""

    profile_selected = pyqtSignal(str)  # Profile name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_service = get_config_service()
        self.profile_manager = get_profile_manager()
        self._setup_ui()
        self._load_profiles()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Profile selection
        profile_group = QGroupBox("Configuration Profiles")
        profile_layout = QVBoxLayout(profile_group)

        self.profile_list = QListWidget()
        self.profile_list.setAccessibleName("Configuration profiles list")
        self.profile_list.itemClicked.connect(self._on_profile_selected)
        profile_layout.addWidget(self.profile_list)

        # Profile actions
        actions_layout = QHBoxLayout()

        self.create_btn = PrimaryButton("Create from Template")
        self.create_btn.setAccessibleName("Create profile from template")
        self.create_btn.clicked.connect(self._create_from_template)
        actions_layout.addWidget(self.create_btn)

        self.switch_btn = SecondaryButton("Switch Profile")
        self.switch_btn.setAccessibleName("Switch to selected profile")
        self.switch_btn.clicked.connect(self._switch_profile)
        self.switch_btn.setEnabled(False)
        actions_layout.addWidget(self.switch_btn)

        self.delete_btn = SecondaryButton("Delete")
        self.delete_btn.setAccessibleName("Delete selected profile")
        self.delete_btn.clicked.connect(self._delete_profile)
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)

        profile_layout.addLayout(actions_layout)
        layout.addWidget(profile_group)

        # Profile details
        details_group = QGroupBox("Profile Details")
        details_layout = QFormLayout(details_group)

        self.name_label = QLabel("No profile selected")
        self.description_label = QLabel("")
        self.use_case_label = QLabel("")
        self.created_label = QLabel("")
        self.updated_label = QLabel("")

        details_layout.addRow("Name:", self.name_label)
        details_layout.addRow("Description:", self.description_label)
        details_layout.addRow("Use Case:", self.use_case_label)
        details_layout.addRow("Created:", self.created_label)
        details_layout.addRow("Updated:", self.updated_label)

        layout.addWidget(details_group)

    def _load_profiles(self):
        """Load available profiles."""
        self.profile_list.clear()

        profiles = self.config_service.get_profiles()
        active_profile = self.config_service.get_active_profile()

        for profile in profiles:
            item = QListWidgetItem(profile.name)
            item.setData(Qt.UserRole, profile)

            if profile.is_active:
                item.setText(f"● {profile.name} (Active)")
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.profile_list.addItem(item)

    def _on_profile_selected(self, item: QListWidgetItem):
        """Handle profile selection."""
        profile = item.data(Qt.UserRole)
        if profile:
            self._update_profile_details(profile)
            self.switch_btn.setEnabled(not profile.is_active)
            self.delete_btn.setEnabled(not profile.is_active and not profile.is_default)
            self.profile_selected.emit(profile.name)

    def _update_profile_details(self, profile):
        """Update profile details display."""
        self.name_label.setText(profile.name)
        self.description_label.setText(profile.description)
        self.use_case_label.setText(profile.use_case.title())
        self.created_label.setText(profile.created_at.strftime("%Y-%m-%d %H:%M"))
        self.updated_label.setText(profile.updated_at.strftime("%Y-%m-%d %H:%M"))

    def _create_from_template(self):
        """Create a new profile from template."""
        from .profile_creation_dialog import ProfileCreationDialog

        dialog = ProfileCreationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_profiles()

    def _switch_profile(self):
        """Switch to selected profile."""
        current_item = self.profile_list.currentItem()
        if current_item:
            profile = current_item.data(Qt.UserRole)
            if profile and not profile.is_active:
                success = self.config_service.switch_profile(profile.name)
                if success:
                    QMessageBox.information(
                        self, "Success", f"Switched to profile: {profile.name}"
                    )
                    self._load_profiles()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to switch to profile: {profile.name}",
                    )

    def _delete_profile(self):
        """Delete selected profile."""
        current_item = self.profile_list.currentItem()
        if current_item:
            profile = current_item.data(Qt.UserRole)
            if profile and not profile.is_active and not profile.is_default:
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete profile '{profile.name}'?",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    success = self.config_service.delete_profile(profile.name)
                    if success:
                        QMessageBox.information(
                            self, "Success", f"Deleted profile: {profile.name}"
                        )
                        self._load_profiles()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Failed to delete profile: {profile.name}",
                        )


class ConfigurationTreeWidget(QTreeWidget):
    """Tree widget for displaying and editing configuration."""

    value_changed = pyqtSignal(str, object)  # path, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Setting", "Value", "Description"])
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 150)
        self.setAlternatingRowColors(True)

        # Track original values for change detection
        self._original_values = {}
        self._current_config = {}

    def load_configuration(self, config: Dict[str, Any]):
        """Load configuration into the tree."""
        self.clear()
        self._original_values = {}
        self._current_config = config.copy()

        if "network_connectivity" in config:
            self._build_tree(config["network_connectivity"], None)
        else:
            self._build_tree(config, None)

    def _build_tree(self, data: Dict[str, Any], parent_item: QTreeWidgetItem):
        """Recursively build the configuration tree."""
        for key, value in data.items():
            if isinstance(value, dict):
                # Create section item
                item = QTreeWidgetItem([key.replace("_", " ").title(), "", ""])
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.addTopLevelItem(item)

                item.setExpanded(True)
                self._build_tree(value, item)
            else:
                # Create value item
                item = QTreeWidgetItem(
                    [
                        key.replace("_", " ").title(),
                        str(value),
                        self._get_setting_description(key),
                    ]
                )

                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.addTopLevelItem(item)

                # Store path and original value
                path = self._get_item_path(item)
                self._original_values[path] = value

                # Make value column editable
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    def _get_item_path(self, item: QTreeWidgetItem) -> str:
        """Get the configuration path for an item."""
        path_parts = []
        current = item

        while current:
            if current.text(1):  # Has a value, so it's a setting
                path_parts.append(current.text(0).lower().replace(" ", "_"))
            current = current.parent()

        return ".".join(reversed(path_parts))

    def _get_setting_description(self, key: str) -> str:
        """Get description for a setting."""
        descriptions = {
            "default_timeout": "Default timeout for network operations (ms)",
            "max_concurrent_operations": "Maximum concurrent network operations",
            "enable_logging": "Enable logging for network tools",
            "log_level": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            "monitoring_interval": "Monitoring interval in milliseconds",
            "alert_threshold_mbps": "Alert threshold in Mbps",
            "scan_interval": "Scan interval in milliseconds",
            "scan_timeout": "Scan timeout in milliseconds",
            "max_threads": "Maximum number of threads",
            "security_level": "Security level (strict, moderate, permissive)",
            "max_memory_usage_mb": "Maximum memory usage in MB",
            "max_cpu_usage_percent": "Maximum CPU usage percentage",
        }
        return descriptions.get(key, "")

    def get_modified_values(self) -> Dict[str, Any]:
        """Get values that have been modified."""
        modified = {}

        def check_item(item: QTreeWidgetItem):
            if item.text(1):  # Has a value
                path = self._get_item_path(item)
                current_value = self._parse_value(item.text(1))
                original_value = self._original_values.get(path)

                if current_value != original_value:
                    modified[path] = current_value

            for i in range(item.childCount()):
                check_item(item.child(i))

        for i in range(self.topLevelItemCount()):
            check_item(self.topLevelItem(i))

        return modified

    def _parse_value(self, text: str) -> Any:
        """Parse text value to appropriate type."""
        text = text.strip()

        # Boolean values
        if text.lower() in ("true", "false"):
            return text.lower() == "true"

        # Numeric values
        try:
            if "." in text:
                return float(text)
            else:
                return int(text)
        except ValueError:
            pass

        # String values
        return text


class ValidationResultsWidget(QWidget):
    """Widget for displaying configuration validation results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Summary
        self.summary_label = QLabel("No validation results")
        layout.addWidget(self.summary_label)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setAccessibleName("Validation results list")
        layout.addWidget(self.results_list)

        # Validation button
        self.validate_btn = PrimaryButton("Validate Configuration")
        self.validate_btn.setAccessibleName("Validate configuration")
        self.validate_btn.clicked.connect(self.validate_requested)
        layout.addWidget(self.validate_btn)

        # Progress bar
        self.progress_bar = LoadingIndicator(parent=self, message="Validating...")
        layout.addWidget(self.progress_bar)

    validate_requested = pyqtSignal()

    def show_validation_results(self, results: List):
        """Show validation results."""
        self.results_list.clear()

        if not results:
            self.summary_label.setText("✓ Configuration is valid")
            self.summary_label.setStyleSheet("color: green; font-weight: bold;")
            return

        # Count by severity
        counts = {"info": 0, "warning": 0, "error": 0, "critical": 0}
        for result in results:
            counts[result.severity.value] += 1

        # Update summary
        summary_parts = []
        if counts["critical"]:
            summary_parts.append(f"{counts['critical']} critical")
        if counts["error"]:
            summary_parts.append(f"{counts['error']} errors")
        if counts["warning"]:
            summary_parts.append(f"{counts['warning']} warnings")
        if counts["info"]:
            summary_parts.append(f"{counts['info']} info")

        self.summary_label.setText(f"Issues found: {', '.join(summary_parts)}")

        # Set color based on severity
        if counts["critical"] or counts["error"]:
            self.summary_label.setStyleSheet("color: red; font-weight: bold;")
        elif counts["warning"]:
            self.summary_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.summary_label.setStyleSheet("color: blue; font-weight: bold;")

        # Add results to list
        for result in results:
            item = QListWidgetItem()

            # Format message
            severity_icon = {
                ValidationSeverity.INFO: "ℹ",
                ValidationSeverity.WARNING: "⚠",
                ValidationSeverity.ERROR: "✗",
                ValidationSeverity.CRITICAL: "🔥",
            }

            icon = severity_icon.get(result.severity, "•")
            text = f"{icon} {result.path}: {result.message}"

            if result.suggestion:
                text += f"\n   💡 {result.suggestion}"

            item.setText(text)

            # Set color based on severity
            if result.severity == ValidationSeverity.CRITICAL:
                item.setForeground(Qt.red)
            elif result.severity == ValidationSeverity.ERROR:
                item.setForeground(Qt.darkRed)
            elif result.severity == ValidationSeverity.WARNING:
                item.setForeground(Qt.darkYellow)
            else:
                item.setForeground(Qt.blue)

            self.results_list.addItem(item)

    def show_validation_progress(self, show: bool):
        """Show or hide validation progress."""
        if show:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()


class ConfigurationManagerDialog(QDialog):
    """Main configuration manager dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Connectivity Configuration Manager")
        self.setMinimumSize(1000, 700)

        self.config_service = get_config_service()
        self.notification_service = get_notification_service()

        # Validation worker
        self.validation_worker = None

        self._setup_ui()
        self._setup_connections()
        self._load_current_configuration()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_configuration)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left panel - Profile management
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.profile_widget = ProfileSelectionWidget()
        self.profile_widget.profile_selected.connect(self._on_profile_selected)
        left_layout.addWidget(self.profile_widget)

        main_splitter.addWidget(left_panel)

        # Right panel - Configuration and validation
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Configuration manager tabs")
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)

        self.config_tree = ConfigurationTreeWidget()
        self.config_tree.value_changed.connect(self._on_value_changed)
        config_layout.addWidget(self.config_tree)

        self.tab_widget.addTab(config_tab, "Configuration")

        # Validation tab
        validation_tab = QWidget()
        validation_layout = QVBoxLayout(validation_tab)

        self.validation_widget = ValidationResultsWidget()
        self.validation_widget.validate_requested.connect(self._validate_configuration)
        validation_layout.addWidget(self.validation_widget)

        self.tab_widget.addTab(validation_tab, "Validation")

        right_layout.addWidget(self.tab_widget)
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([300, 700])

        # Button bar
        button_layout = QHBoxLayout()

        self.save_btn = PrimaryButton("Save Changes")
        self.save_btn.setAccessibleName("Save configuration changes")
        self.save_btn.clicked.connect(self._save_configuration)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)

        self.reset_btn = SecondaryButton("Reset")
        self.reset_btn.setAccessibleName("Reset configuration")
        self.reset_btn.clicked.connect(self._reset_configuration)
        button_layout.addWidget(self.reset_btn)

        self.export_btn = SecondaryButton("Export")
        self.export_btn.setAccessibleName("Export configuration")
        self.export_btn.clicked.connect(self._export_configuration)
        button_layout.addWidget(self.export_btn)

        self.import_btn = SecondaryButton("Import")
        self.import_btn.setAccessibleName("Import configuration")
        self.import_btn.clicked.connect(self._import_configuration)
        button_layout.addWidget(self.import_btn)

        button_layout.addStretch()

        self.close_btn = SecondaryButton("Close")
        self.close_btn.setAccessibleName("Close configuration manager")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _setup_connections(self):
        """Setup signal connections."""
        # Listen for configuration events
        self.config_service.add_event_callback(
            ConfigurationEvent.CONFIG_UPDATED, self._on_config_updated
        )

        self.config_service.add_event_callback(
            ConfigurationEvent.PROFILE_SWITCHED, self._on_profile_switched
        )

    def _load_current_configuration(self):
        """Load current configuration."""
        try:
            config = self.config_service.get_configuration()
            self.config_tree.load_configuration(config)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load configuration: {e}")

    def _on_profile_selected(self, profile_name: str):
        """Handle profile selection."""
        # Load profile configuration
        profile = self.config_service.get_profile(profile_name)
        if profile:
            self.config_tree.load_configuration(profile.settings)

    def _on_value_changed(self, path: str, value: Any):
        """Handle configuration value change."""
        self.save_btn.setEnabled(True)

    def _save_configuration(self):
        """Save configuration changes."""
        try:
            modified_values = self.config_tree.get_modified_values()

            if not modified_values:
                QMessageBox.information(self, "Info", "No changes to save")
                return

            # Convert flat paths to nested structure
            updates = {}
            for path, value in modified_values.items():
                self._set_nested_value(updates, path, value)

            # Update configuration
            success = self.config_service.update_configuration(updates)

            if success:
                QMessageBox.information(
                    self, "Success", "Configuration saved successfully"
                )
                self.save_btn.setEnabled(False)
                self._load_current_configuration()
            else:
                QMessageBox.warning(self, "Error", "Failed to save configuration")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configuration: {e}")

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any):
        """Set a nested value in configuration dictionary."""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _reset_configuration(self):
        """Reset configuration to original values."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all changes?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._load_current_configuration()
            self.save_btn.setEnabled(False)

    def _validate_configuration(self):
        """Validate current configuration."""
        try:
            # Get current configuration from tree
            config = self.config_service.get_configuration()

            # Show progress
            self.validation_widget.show_validation_progress(True)

            # Start validation in background thread
            self.validation_worker = ConfigValidationWorker(config)
            self.validation_worker.validation_complete.connect(
                self._on_validation_complete
            )
            self.validation_worker.start()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start validation: {e}")
            self.validation_widget.show_validation_progress(False)

    def _on_validation_complete(self, results: List):
        """Handle validation completion."""
        self.validation_widget.show_validation_progress(False)
        self.validation_widget.show_validation_results(results)

        # Switch to validation tab
        self.tab_widget.setCurrentIndex(1)

    def _export_configuration(self):
        """Export configuration to file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Configuration",
                f"network_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)",
            )

            if file_path:
                success = self.config_service.export_configuration(
                    file_path, include_profiles=True
                )

                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Configuration exported to {file_path}",
                    )
                else:
                    QMessageBox.warning(self, "Error", "Failed to export configuration")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export error: {e}")

    def _import_configuration(self):
        """Import configuration from file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Configuration",
                "",
                "JSON Files (*.json);;All Files (*)",
            )

            if file_path:
                reply = QMessageBox.question(
                    self,
                    "Confirm Import",
                    "Importing will replace current configuration. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    success = self.config_service.import_configuration(file_path)

                    if success:
                        QMessageBox.information(
                            self,
                            "Success",
                            "Configuration imported successfully",
                        )
                        self._load_current_configuration()
                        self.profile_widget._load_profiles()
                    else:
                        QMessageBox.warning(
                            self, "Error", "Failed to import configuration"
                        )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import error: {e}")

    def _on_config_updated(self, event_data: Dict[str, Any]):
        """Handle configuration update event."""
        # Refresh configuration display
        self._load_current_configuration()

    def _on_profile_switched(self, event_data: Dict[str, Any]):
        """Handle profile switch event."""
        # Refresh profile list and configuration
        self.profile_widget._load_profiles()
        self._load_current_configuration()

    def _refresh_configuration(self):
        """Refresh configuration periodically."""
        # Only refresh if no unsaved changes
        if not self.save_btn.isEnabled():
            self._load_current_configuration()

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.save_btn.isEnabled():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
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

        # Stop refresh timer
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()

        # Clean up validation worker
        if self.validation_worker and self.validation_worker.isRunning():
            self.validation_worker.terminate()
            self.validation_worker.wait()
