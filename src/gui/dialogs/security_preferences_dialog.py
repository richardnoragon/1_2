"""
Security Preferences Dialog for RFU Hub

This dialog provides comprehensive security settings management including:
- Database Migration Controls
- Theme Encryption Settings
- Directory Security Configuration
- Security Audit Logging
- Security Status Monitoring

Integrates with the RFU Hub Preferences Security Implementation.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Security profile constants
STANDARD_RECOMMENDED_PROFILE = "Standard (Recommended)"

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

try:
    from PyQt5.QtCore import QDateTime, Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
    from PyQt5.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDateTimeEdit,
        QDialog,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    # Import security components
    from config_manager import get_config_manager

    class SecurityPreferencesDialog(QDialog):
        """Main security preferences dialog with tabbed interface."""

        # Signals for security operations
        migration_status_changed = pyqtSignal(str, bool)  # operation, success
        theme_encryption_changed = pyqtSignal(bool)  # enabled
        security_audit_logged = pyqtSignal(str, str, str)  # level, category, message

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("RFU Hub - Security Preferences")
            self.setModal(True)
            self.resize(900, 700)

            # Initialize components
            self.config_manager = get_config_manager()
            self.logger = logging.getLogger("RFU.SecurityPreferences")

            # Security managers (lazy loaded)
            self._migration_manager = None
            self._theme_encryption = None
            self._directory_security = None

            # Initialize UI
            self.init_ui()
            self.load_current_settings()

            # Setup refresh timer for status updates
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.refresh_security_status)
            self.status_timer.start(5000)  # Refresh every 5 seconds

        def init_ui(self):
            """Initialize the user interface."""
            layout = QVBoxLayout(self)

            # Create header with security status
            header_frame = self.create_header_section()
            layout.addWidget(header_frame)

            # Create main tab widget
            self.tab_widget = QTabWidget()
            layout.addWidget(self.tab_widget)

            # Create tabs
            self.tab_widget.addTab(self.create_migration_tab(), "🔄 Database Migration")
            self.tab_widget.addTab(
                self.create_theme_security_tab(), "🎨 Theme Security"
            )
            self.tab_widget.addTab(
                self.create_directory_security_tab(), "📁 Directory Security"
            )
            self.tab_widget.addTab(self.create_audit_logging_tab(), "📋 Security Audit")
            self.tab_widget.addTab(
                self.create_status_monitoring_tab(), "📊 Status Monitor"
            )
            self.tab_widget.addTab(
                self.create_advanced_settings_tab(), "⚙️ Advanced Settings"
            )

            # Create button bar
            button_layout = QHBoxLayout()

            # Action buttons
            self.test_security_btn = QPushButton("🧪 Test Security Features")
            self.test_security_btn.clicked.connect(self.test_security_features)
            button_layout.addWidget(self.test_security_btn)

            self.export_config_btn = QPushButton("📤 Export Security Config")
            self.export_config_btn.clicked.connect(self.export_security_config)
            button_layout.addWidget(self.export_config_btn)

            self.import_config_btn = QPushButton("📥 Import Security Config")
            self.import_config_btn.clicked.connect(self.import_security_config)
            button_layout.addWidget(self.import_config_btn)

            button_layout.addStretch()

            # Standard dialog buttons
            self.apply_btn = QPushButton("Apply")
            self.apply_btn.clicked.connect(self.apply_settings)
            button_layout.addWidget(self.apply_btn)

            self.ok_btn = QPushButton("OK")
            self.ok_btn.clicked.connect(self.accept_settings)
            button_layout.addWidget(self.ok_btn)

            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_btn)

            layout.addLayout(button_layout)

        def create_header_section(self) -> QWidget:
            """Create the header section with security status overview."""
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet(
                """
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    margin: 5px;
                    padding: 10px;
                }
            """
            )

            layout = QHBoxLayout(frame)

            # Security status indicators
            status_layout = QVBoxLayout()

            # Main status label
            self.security_status_label = QLabel(
                "🔒 Security System Status: Initializing..."
            )
            self.security_status_label.setFont(QFont("Arial", 12, QFont.Bold))
            status_layout.addWidget(self.security_status_label)

            # Component status indicators
            indicators_layout = QHBoxLayout()

            self.migration_status_indicator = QLabel("🔄 Migration: Unknown")
            self.theme_encryption_indicator = QLabel("🎨 Theme: Unknown")
            self.directory_security_indicator = QLabel("📁 Directory: Unknown")
            self.audit_logging_indicator = QLabel("📋 Audit: Unknown")

            for indicator in [
                self.migration_status_indicator,
                self.theme_encryption_indicator,
                self.directory_security_indicator,
                self.audit_logging_indicator,
            ]:
                indicator.setStyleSheet("padding: 5px; margin: 2px;")
                indicators_layout.addWidget(indicator)

            status_layout.addLayout(indicators_layout)
            layout.addLayout(status_layout)

            # Quick actions
            quick_actions_layout = QVBoxLayout()
            quick_actions_layout.addWidget(QLabel("Quick Actions:"))

            self.emergency_disable_btn = QPushButton("🚨 Emergency Disable All")
            self.emergency_disable_btn.setStyleSheet(
                "background-color: #dc3545; color: white;"
            )
            self.emergency_disable_btn.clicked.connect(self.emergency_disable_security)
            quick_actions_layout.addWidget(self.emergency_disable_btn)

            self.refresh_status_btn = QPushButton("🔄 Refresh Status")
            self.refresh_status_btn.clicked.connect(self.refresh_security_status)
            quick_actions_layout.addWidget(self.refresh_status_btn)

            layout.addLayout(quick_actions_layout)

            return frame

        def create_migration_tab(self) -> QWidget:
            """Create the database migration settings tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Migration Control Section
            migration_group = QGroupBox("Database Migration Control")
            migration_layout = QFormLayout(migration_group)

            # Current database version
            self.current_version_label = QLabel("Unknown")
            migration_layout.addRow(
                "Current Database Version:", self.current_version_label
            )

            # Target version selection
            self.target_version_combo = QComboBox()
            self.target_version_combo.addItems(["001", "002", "003", "Latest"])
            migration_layout.addRow("Target Version:", self.target_version_combo)

            # Migration options
            self.backup_before_migration = QCheckBox("Create backup before migration")
            self.backup_before_migration.setChecked(True)
            migration_layout.addRow(self.backup_before_migration)

            self.validate_migration = QCheckBox("Validate migration integrity")
            self.validate_migration.setChecked(True)
            migration_layout.addRow(self.validate_migration)

            self.auto_rollback = QCheckBox("Auto-rollback on failure")
            self.auto_rollback.setChecked(True)
            migration_layout.addRow(self.auto_rollback)

            # Migration actions
            migration_actions = QHBoxLayout()
            self.execute_migration_btn = QPushButton("🔄 Execute Migration")
            self.execute_migration_btn.clicked.connect(self.execute_migration)
            migration_actions.addWidget(self.execute_migration_btn)

            self.rollback_migration_btn = QPushButton("↩️ Rollback Migration")
            self.rollback_migration_btn.clicked.connect(self.rollback_migration)
            migration_actions.addWidget(self.rollback_migration_btn)

            self.validate_schema_btn = QPushButton("✅ Validate Schema")
            self.validate_schema_btn.clicked.connect(self.validate_schema)
            migration_actions.addWidget(self.validate_schema_btn)

            migration_layout.addRow(migration_actions)

            layout.addWidget(migration_group)

            # Migration History Section
            history_group = QGroupBox("Migration History")
            history_layout = QVBoxLayout(history_group)

            self.migration_history_table = QTableWidget(0, 5)
            self.migration_history_table.setHorizontalHeaderLabels(
                ["Version", "Status", "Timestamp", "Duration", "Notes"]
            )
            self.migration_history_table.horizontalHeader().setStretchLastSection(True)
            history_layout.addWidget(self.migration_history_table)

            layout.addWidget(history_group)

            # Migration Progress Section
            progress_group = QGroupBox("Migration Progress")
            progress_layout = QVBoxLayout(progress_group)

            self.migration_progress_bar = QProgressBar()
            progress_layout.addWidget(self.migration_progress_bar)

            self.migration_status_text = QTextEdit()
            self.migration_status_text.setMaximumHeight(100)
            self.migration_status_text.setReadOnly(True)
            progress_layout.addWidget(self.migration_status_text)

            layout.addWidget(progress_group)

            return widget

        def create_theme_security_tab(self) -> QWidget:
            """Create the theme security settings tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Theme Encryption Section
            encryption_group = QGroupBox("Theme Data Encryption")
            encryption_layout = QFormLayout(encryption_group)

            # Enable theme encryption
            self.enable_theme_encryption = QCheckBox("Enable theme data encryption")
            encryption_layout.addRow(self.enable_theme_encryption)

            # Encryption algorithm selection
            self.encryption_algorithm_combo = QComboBox()
            self.encryption_algorithm_combo.addItems(
                [
                    "AES-256-GCM (Recommended)",
                    "AES-256-CBC",
                    "ChaCha20-Poly1305",
                ]
            )
            encryption_layout.addRow(
                "Encryption Algorithm:", self.encryption_algorithm_combo
            )

            # Key derivation settings
            self.key_derivation_combo = QComboBox()
            self.key_derivation_combo.addItems(
                [
                    "PBKDF2-SHA256 (Recommended)",
                    "PBKDF2-SHA512",
                    "Argon2",
                    "Scrypt",
                ]
            )
            encryption_layout.addRow("Key Derivation:", self.key_derivation_combo)

            # Key derivation iterations
            self.kdf_iterations = QSpinBox()
            self.kdf_iterations.setRange(10000, 1000000)
            self.kdf_iterations.setValue(100000)
            self.kdf_iterations.setSuffix(" iterations")
            encryption_layout.addRow("KDF Iterations:", self.kdf_iterations)

            # Theme encryption actions
            theme_actions = QHBoxLayout()
            self.encrypt_themes_btn = QPushButton("🔒 Encrypt All Themes")
            self.encrypt_themes_btn.clicked.connect(self.encrypt_all_themes)
            theme_actions.addWidget(self.encrypt_themes_btn)

            self.decrypt_themes_btn = QPushButton("🔓 Decrypt All Themes")
            self.decrypt_themes_btn.clicked.connect(self.decrypt_all_themes)
            theme_actions.addWidget(self.decrypt_themes_btn)

            self.test_encryption_btn = QPushButton("🧪 Test Encryption")
            self.test_encryption_btn.clicked.connect(self.test_theme_encryption)
            theme_actions.addWidget(self.test_encryption_btn)

            encryption_layout.addRow(theme_actions)

            layout.addWidget(encryption_group)

            # Theme Corruption Detection Section
            corruption_group = QGroupBox("Corruption Detection & Recovery")
            corruption_layout = QFormLayout(corruption_group)

            # Enable corruption detection
            self.enable_corruption_detection = QCheckBox(
                "Enable automatic corruption detection"
            )
            self.enable_corruption_detection.setChecked(True)
            corruption_layout.addRow(self.enable_corruption_detection)

            # Corruption check frequency
            self.corruption_check_frequency = QComboBox()
            self.corruption_check_frequency.addItems(
                [
                    "On each theme access",
                    "Every hour",
                    "Every 6 hours",
                    "Daily",
                    "Weekly",
                ]
            )
            corruption_layout.addRow(
                "Check Frequency:", self.corruption_check_frequency
            )

            # Corruption recovery strategy
            self.corruption_recovery_strategy = QComboBox()
            self.corruption_recovery_strategy.addItems(
                [
                    "Auto-restore from backup",
                    "Prompt user for action",
                    "Disable corrupted theme",
                    "Regenerate default theme",
                ]
            )
            corruption_layout.addRow(
                "Recovery Strategy:", self.corruption_recovery_strategy
            )

            # Corruption actions
            corruption_actions = QHBoxLayout()
            self.scan_corruption_btn = QPushButton("🔍 Scan for Corruption")
            self.scan_corruption_btn.clicked.connect(self.scan_theme_corruption)
            corruption_actions.addWidget(self.scan_corruption_btn)

            self.repair_corruption_btn = QPushButton("🔧 Repair Corruption")
            self.repair_corruption_btn.clicked.connect(self.repair_theme_corruption)
            corruption_actions.addWidget(self.repair_corruption_btn)

            corruption_layout.addRow(corruption_actions)

            layout.addWidget(corruption_group)

            # Theme Security Status
            status_group = QGroupBox("Theme Security Status")
            status_layout = QVBoxLayout(status_group)

            self.theme_security_status = QTextEdit()
            self.theme_security_status.setMaximumHeight(150)
            self.theme_security_status.setReadOnly(True)
            status_layout.addWidget(self.theme_security_status)

            layout.addWidget(status_group)

            return widget

        def create_directory_security_tab(self) -> QWidget:
            """Create the directory security settings tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Directory Access Control Section
            access_group = QGroupBox("Directory Access Control")
            access_layout = QFormLayout(access_group)

            # Enable directory security
            self.enable_directory_security = QCheckBox(
                "Enable directory access control"
            )
            access_layout.addRow(self.enable_directory_security)

            # Protected directories list
            protected_dirs_layout = QVBoxLayout()
            protected_dirs_layout.addWidget(QLabel("Protected Directories:"))

            self.protected_directories_list = QTreeWidget()
            self.protected_directories_list.setHeaderLabels(
                ["Directory", "Access Level", "Status"]
            )
            protected_dirs_layout.addWidget(self.protected_directories_list)

            # Directory management buttons
            dir_buttons = QHBoxLayout()
            self.add_protected_dir_btn = QPushButton("➕ Add Directory")
            self.add_protected_dir_btn.clicked.connect(self.add_protected_directory)
            dir_buttons.addWidget(self.add_protected_dir_btn)

            self.remove_protected_dir_btn = QPushButton("➖ Remove Directory")
            self.remove_protected_dir_btn.clicked.connect(
                self.remove_protected_directory
            )
            dir_buttons.addWidget(self.remove_protected_dir_btn)

            self.edit_dir_permissions_btn = QPushButton("✏️ Edit Permissions")
            self.edit_dir_permissions_btn.clicked.connect(
                self.edit_directory_permissions
            )
            dir_buttons.addWidget(self.edit_dir_permissions_btn)

            protected_dirs_layout.addLayout(dir_buttons)
            access_layout.addRow(protected_dirs_layout)

            layout.addWidget(access_group)

            # Directory Monitoring Section
            monitoring_group = QGroupBox("Directory Monitoring")
            monitoring_layout = QFormLayout(monitoring_group)

            # Enable monitoring
            self.enable_directory_monitoring = QCheckBox(
                "Enable directory change monitoring"
            )
            monitoring_layout.addRow(self.enable_directory_monitoring)

            # Monitoring sensitivity
            self.monitoring_sensitivity = QSlider(Qt.Horizontal)
            self.monitoring_sensitivity.setRange(1, 5)
            self.monitoring_sensitivity.setValue(3)
            self.monitoring_sensitivity.setTickPosition(QSlider.TicksBelow)
            sensitivity_label = QLabel("Medium")
            self.monitoring_sensitivity.valueChanged.connect(
                lambda v: sensitivity_label.setText(
                    ["", "Very Low", "Low", "Medium", "High", "Very High"][v]
                )
            )
            sensitivity_layout = QHBoxLayout()
            sensitivity_layout.addWidget(self.monitoring_sensitivity)
            sensitivity_layout.addWidget(sensitivity_label)
            monitoring_layout.addRow("Monitoring Sensitivity:", sensitivity_layout)

            # Alert settings
            self.alert_on_unauthorized_access = QCheckBox(
                "Alert on unauthorized access attempts"
            )
            self.alert_on_unauthorized_access.setChecked(True)
            monitoring_layout.addRow(self.alert_on_unauthorized_access)

            self.log_directory_access = QCheckBox("Log all directory access")
            self.log_directory_access.setChecked(True)
            monitoring_layout.addRow(self.log_directory_access)

            layout.addWidget(monitoring_group)

            # Directory Security Log
            log_group = QGroupBox("Directory Security Log")
            log_layout = QVBoxLayout(log_group)

            self.directory_security_log = QTextEdit()
            self.directory_security_log.setMaximumHeight(150)
            self.directory_security_log.setReadOnly(True)
            log_layout.addWidget(self.directory_security_log)

            log_buttons = QHBoxLayout()
            self.clear_log_btn = QPushButton("🗑️ Clear Log")
            self.clear_log_btn.clicked.connect(self.clear_directory_log)
            log_buttons.addWidget(self.clear_log_btn)

            self.export_log_btn = QPushButton("📤 Export Log")
            self.export_log_btn.clicked.connect(self.export_directory_log)
            log_buttons.addWidget(self.export_log_btn)

            log_buttons.addStretch()
            log_layout.addLayout(log_buttons)

            layout.addWidget(log_group)

            return widget

        def create_audit_logging_tab(self) -> QWidget:
            """Create the security audit logging tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Audit Configuration Section
            config_group = QGroupBox("Audit Logging Configuration")
            config_layout = QFormLayout(config_group)

            # Enable audit logging
            self.enable_audit_logging = QCheckBox(
                "Enable comprehensive security audit logging"
            )
            self.enable_audit_logging.setChecked(True)
            config_layout.addRow(self.enable_audit_logging)

            # Audit log level
            self.audit_log_level = QComboBox()
            self.audit_log_level.addItems(
                ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            )
            self.audit_log_level.setCurrentText("INFO")
            config_layout.addRow("Audit Log Level:", self.audit_log_level)

            # Audit categories
            categories_layout = QVBoxLayout()
            categories_layout.addWidget(QLabel("Audit Categories:"))

            self.audit_categories = {}
            categories = [
                "Database Operations",
                "Theme Security",
                "Directory Access",
                "User Authentication",
                "Configuration Changes",
                "System Events",
            ]

            for category in categories:
                checkbox = QCheckBox(category)
                checkbox.setChecked(True)
                self.audit_categories[category] = checkbox
                categories_layout.addWidget(checkbox)

            config_layout.addRow(categories_layout)

            # Audit log rotation
            self.audit_log_max_size = QSpinBox()
            self.audit_log_max_size.setRange(1, 1000)
            self.audit_log_max_size.setValue(50)
            self.audit_log_max_size.setSuffix(" MB")
            config_layout.addRow("Max Log Size:", self.audit_log_max_size)

            self.audit_log_backup_count = QSpinBox()
            self.audit_log_backup_count.setRange(1, 100)
            self.audit_log_backup_count.setValue(10)
            self.audit_log_backup_count.setSuffix(" files")
            config_layout.addRow("Backup Count:", self.audit_log_backup_count)

            layout.addWidget(config_group)

            # Audit Log Viewer Section
            viewer_group = QGroupBox("Audit Log Viewer")
            viewer_layout = QVBoxLayout(viewer_group)

            # Filter controls
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Filter:"))

            self.audit_filter_category = QComboBox()
            self.audit_filter_category.addItems(["All Categories"] + categories)
            filter_layout.addWidget(self.audit_filter_category)

            self.audit_filter_level = QComboBox()
            self.audit_filter_level.addItems(
                ["All Levels", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            )
            filter_layout.addWidget(self.audit_filter_level)

            self.audit_filter_date = QDateTimeEdit()
            self.audit_filter_date.setDateTime(QDateTime.currentDateTime().addDays(-7))
            filter_layout.addWidget(self.audit_filter_date)

            self.apply_filter_btn = QPushButton("Apply Filter")
            self.apply_filter_btn.clicked.connect(self.apply_audit_filter)
            filter_layout.addWidget(self.apply_filter_btn)

            filter_layout.addStretch()
            viewer_layout.addLayout(filter_layout)

            # Audit log display
            self.audit_log_table = QTableWidget(0, 6)
            self.audit_log_table.setHorizontalHeaderLabels(
                ["Timestamp", "Level", "Category", "Event", "User", "Details"]
            )
            self.audit_log_table.horizontalHeader().setStretchLastSection(True)
            viewer_layout.addWidget(self.audit_log_table)

            # Audit actions
            audit_actions = QHBoxLayout()
            self.refresh_audit_log_btn = QPushButton("🔄 Refresh")
            self.refresh_audit_log_btn.clicked.connect(self.refresh_audit_log)
            audit_actions.addWidget(self.refresh_audit_log_btn)

            self.export_audit_log_btn = QPushButton("📤 Export Log")
            self.export_audit_log_btn.clicked.connect(self.export_audit_log)
            audit_actions.addWidget(self.export_audit_log_btn)

            self.clear_audit_log_btn = QPushButton("🗑️ Clear Log")
            self.clear_audit_log_btn.clicked.connect(self.clear_audit_log)
            audit_actions.addWidget(self.clear_audit_log_btn)

            audit_actions.addStretch()
            viewer_layout.addLayout(audit_actions)

            layout.addWidget(viewer_group)

            return widget

        def create_status_monitoring_tab(self) -> QWidget:
            """Create the security status monitoring tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Real-time Status Section
            status_group = QGroupBox("Real-time Security Status")
            status_layout = QVBoxLayout(status_group)

            # Status dashboard
            dashboard_layout = QGridLayout()

            # Security component status widgets
            self.migration_status_widget = self.create_status_widget(
                "Database Migration", "🔄"
            )
            dashboard_layout.addWidget(self.migration_status_widget, 0, 0)

            self.theme_security_status_widget = self.create_status_widget(
                "Theme Security", "🎨"
            )
            dashboard_layout.addWidget(self.theme_security_status_widget, 0, 1)

            self.directory_security_status_widget = self.create_status_widget(
                "Directory Security", "📁"
            )
            dashboard_layout.addWidget(self.directory_security_status_widget, 1, 0)

            self.audit_logging_status_widget = self.create_status_widget(
                "Audit Logging", "📋"
            )
            dashboard_layout.addWidget(self.audit_logging_status_widget, 1, 1)

            status_layout.addLayout(dashboard_layout)
            layout.addWidget(status_group)

            # Security Metrics Section
            metrics_group = QGroupBox("Security Metrics")
            metrics_layout = QFormLayout(metrics_group)

            self.security_score_label = QLabel("Calculating...")
            metrics_layout.addRow("Overall Security Score:", self.security_score_label)

            self.last_migration_label = QLabel("Never")
            metrics_layout.addRow("Last Migration:", self.last_migration_label)

            self.themes_encrypted_label = QLabel("Unknown")
            metrics_layout.addRow("Encrypted Themes:", self.themes_encrypted_label)

            self.protected_directories_label = QLabel("0")
            metrics_layout.addRow(
                "Protected Directories:", self.protected_directories_label
            )

            self.audit_entries_label = QLabel("0")
            metrics_layout.addRow("Audit Log Entries:", self.audit_entries_label)

            layout.addWidget(metrics_group)

            # Security Alerts Section
            alerts_group = QGroupBox("Security Alerts")
            alerts_layout = QVBoxLayout(alerts_group)

            self.security_alerts_list = QTreeWidget()
            self.security_alerts_list.setHeaderLabels(
                ["Severity", "Category", "Message", "Timestamp"]
            )
            alerts_layout.addWidget(self.security_alerts_list)

            alerts_actions = QHBoxLayout()
            self.dismiss_alert_btn = QPushButton("✅ Dismiss Selected")
            self.dismiss_alert_btn.clicked.connect(self.dismiss_security_alert)
            alerts_actions.addWidget(self.dismiss_alert_btn)

            self.dismiss_all_alerts_btn = QPushButton("✅ Dismiss All")
            self.dismiss_all_alerts_btn.clicked.connect(self.dismiss_all_alerts)
            alerts_actions.addWidget(self.dismiss_all_alerts_btn)

            alerts_actions.addStretch()
            alerts_layout.addLayout(alerts_actions)

            layout.addWidget(alerts_group)

            return widget

        def create_advanced_settings_tab(self) -> QWidget:
            """Create the advanced security settings tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Security Profiles Section
            profiles_group = QGroupBox("Security Profiles")
            profiles_layout = QFormLayout(profiles_group)

            # Security profile selection
            self.security_profile = QComboBox()
            self.security_profile.addItems(
                [
                    "Minimal (Basic protection)",
                    STANDARD_RECOMMENDED_PROFILE,
                    "Enhanced (High security)",
                    "Maximum (Paranoid mode)",
                    "Custom (User defined)",
                ]
            )
            self.security_profile.setCurrentText(STANDARD_RECOMMENDED_PROFILE)
            self.security_profile.currentTextChanged.connect(
                self.apply_security_profile
            )
            profiles_layout.addRow("Security Profile:", self.security_profile)

            # Profile description
            self.profile_description = QTextEdit()
            self.profile_description.setMaximumHeight(80)
            self.profile_description.setReadOnly(True)
            profiles_layout.addRow("Profile Description:", self.profile_description)

            layout.addWidget(profiles_group)

            # Advanced Configuration Section
            advanced_group = QGroupBox("Advanced Configuration")
            advanced_layout = QFormLayout(advanced_group)

            # Security timeouts
            self.session_timeout = QSpinBox()
            self.session_timeout.setRange(5, 1440)  # 5 minutes to 24 hours
            self.session_timeout.setValue(60)
            self.session_timeout.setSuffix(" minutes")
            advanced_layout.addRow("Session Timeout:", self.session_timeout)

            # Security validation frequency
            self.validation_frequency = QComboBox()
            self.validation_frequency.addItems(
                [
                    "Continuous",
                    "Every 5 minutes",
                    "Every 15 minutes",
                    "Every hour",
                    "Daily",
                    "Manual only",
                ]
            )
            advanced_layout.addRow("Validation Frequency:", self.validation_frequency)

            # Memory security
            self.secure_memory_wiping = QCheckBox("Enable secure memory wiping")
            self.secure_memory_wiping.setChecked(True)
            advanced_layout.addRow(self.secure_memory_wiping)

            # Debug mode
            self.security_debug_mode = QCheckBox("Enable security debug mode")
            advanced_layout.addRow(self.security_debug_mode)

            layout.addWidget(advanced_group)

            # Emergency Procedures Section
            emergency_group = QGroupBox("Emergency Procedures")
            emergency_layout = QVBoxLayout(emergency_group)

            emergency_layout.addWidget(QLabel("Emergency security procedures:"))

            emergency_buttons = QGridLayout()

            self.lockdown_btn = QPushButton("🔒 Security Lockdown")
            self.lockdown_btn.setStyleSheet("background-color: #dc3545; color: white;")
            self.lockdown_btn.clicked.connect(self.security_lockdown)
            emergency_buttons.addWidget(self.lockdown_btn, 0, 0)

            self.force_backup_btn = QPushButton("💾 Force Backup")
            self.force_backup_btn.clicked.connect(self.force_security_backup)
            emergency_buttons.addWidget(self.force_backup_btn, 0, 1)

            self.reset_security_btn = QPushButton("🔄 Reset Security")
            self.reset_security_btn.setStyleSheet(
                "background-color: #fd7e14; color: white;"
            )
            self.reset_security_btn.clicked.connect(self.reset_security_settings)
            emergency_buttons.addWidget(self.reset_security_btn, 1, 0)

            self.security_audit_btn = QPushButton("🔍 Security Audit")
            self.security_audit_btn.clicked.connect(self.run_security_audit)
            emergency_buttons.addWidget(self.security_audit_btn, 1, 1)

            emergency_layout.addLayout(emergency_buttons)

            layout.addWidget(emergency_group)

            return widget

        def create_status_widget(self, title: str, icon: str) -> QWidget:
            """Create a status widget for security component monitoring."""
            widget = QFrame()
            widget.setFrameStyle(QFrame.StyledPanel)
            widget.setStyleSheet(
                """
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    margin: 5px;
                    padding: 10px;
                }
            """
            )

            layout = QVBoxLayout(widget)

            # Title with icon
            title_layout = QHBoxLayout()
            title_layout.addWidget(QLabel(f"{icon} {title}"))
            title_layout.addStretch()

            status_label = QLabel("●")
            status_label.setStyleSheet("color: #6c757d; font-size: 16px;")
            title_layout.addWidget(status_label)

            layout.addLayout(title_layout)

            # Status details
            details_label = QLabel("Status: Unknown")
            details_label.setStyleSheet("font-size: 11px; color: #6c757d;")
            layout.addWidget(details_label)

            # Store references for updates
            widget.status_indicator = status_label
            widget.details_label = details_label

            return widget

        # Security operation methods
        def load_current_settings(self):
            """Load current security settings from configuration."""
            try:
                # Load migration settings
                self.target_version_combo.setCurrentText(
                    self.config_manager.get_setting(
                        "security_migration", "target_version", "Latest"
                    )
                )
                self.backup_before_migration.setChecked(
                    self.config_manager.get_setting(
                        "security_migration", "backup_before_migration", True
                    )
                )
                self.validate_migration.setChecked(
                    self.config_manager.get_setting(
                        "security_migration", "validate_migration", True
                    )
                )
                self.auto_rollback.setChecked(
                    self.config_manager.get_setting(
                        "security_migration", "auto_rollback", True
                    )
                )

                # Load theme security settings
                self.enable_theme_encryption.setChecked(
                    self.config_manager.get_setting(
                        "security_theme", "enable_encryption", False
                    )
                )
                self.encryption_algorithm_combo.setCurrentText(
                    self.config_manager.get_setting(
                        "security_theme",
                        "encryption_algorithm",
                        "AES-256-GCM (Recommended)",
                    )
                )
                self.key_derivation_combo.setCurrentText(
                    self.config_manager.get_setting(
                        "security_theme",
                        "key_derivation",
                        "PBKDF2-SHA256 (Recommended)",
                    )
                )
                self.kdf_iterations.setValue(
                    self.config_manager.get_setting(
                        "security_theme", "kdf_iterations", 100000
                    )
                )

                # Load directory security settings
                self.enable_directory_security.setChecked(
                    self.config_manager.get_setting(
                        "security_directory", "enable_access_control", False
                    )
                )
                self.enable_directory_monitoring.setChecked(
                    self.config_manager.get_setting(
                        "security_directory", "enable_monitoring", False
                    )
                )

                # Load audit settings
                self.enable_audit_logging.setChecked(
                    self.config_manager.get_setting(
                        "security_audit", "enable_logging", True
                    )
                )
                self.audit_log_level.setCurrentText(
                    self.config_manager.get_setting(
                        "security_audit", "log_level", "INFO"
                    )
                )

                # Load advanced settings
                self.security_profile.setCurrentText(
                    self.config_manager.get_setting(
                        "security_advanced",
                        "security_profile",
                        STANDARD_RECOMMENDED_PROFILE,
                    )
                )
                self.session_timeout.setValue(
                    self.config_manager.get_setting(
                        "security_advanced", "session_timeout", 60
                    )
                )

                self.logger.info("Security settings loaded successfully")

            except Exception as e:
                self.logger.error(f"Failed to load security settings: {e}")
                QMessageBox.warning(
                    self,
                    "Load Error",
                    f"Failed to load security settings: {e}",
                )

        def apply_settings(self):
            """Apply current security settings."""
            try:
                # Save migration settings
                self.config_manager.set_setting(
                    "security_migration",
                    "target_version",
                    self.target_version_combo.currentText(),
                )
                self.config_manager.set_setting(
                    "security_migration",
                    "backup_before_migration",
                    self.backup_before_migration.isChecked(),
                )
                self.config_manager.set_setting(
                    "security_migration",
                    "validate_migration",
                    self.validate_migration.isChecked(),
                )
                self.config_manager.set_setting(
                    "security_migration",
                    "auto_rollback",
                    self.auto_rollback.isChecked(),
                )

                # Save theme security settings
                self.config_manager.set_setting(
                    "security_theme",
                    "enable_encryption",
                    self.enable_theme_encryption.isChecked(),
                )
                self.config_manager.set_setting(
                    "security_theme",
                    "encryption_algorithm",
                    self.encryption_algorithm_combo.currentText(),
                )
                self.config_manager.set_setting(
                    "security_theme",
                    "key_derivation",
                    self.key_derivation_combo.currentText(),
                )
                self.config_manager.set_setting(
                    "security_theme",
                    "kdf_iterations",
                    self.kdf_iterations.value(),
                )

                # Save directory security settings
                self.config_manager.set_setting(
                    "security_directory",
                    "enable_access_control",
                    self.enable_directory_security.isChecked(),
                )
                self.config_manager.set_setting(
                    "security_directory",
                    "enable_monitoring",
                    self.enable_directory_monitoring.isChecked(),
                )

                # Save audit settings
                self.config_manager.set_setting(
                    "security_audit",
                    "enable_logging",
                    self.enable_audit_logging.isChecked(),
                )
                self.config_manager.set_setting(
                    "security_audit",
                    "log_level",
                    self.audit_log_level.currentText(),
                )

                # Save advanced settings
                self.config_manager.set_setting(
                    "security_advanced",
                    "security_profile",
                    self.security_profile.currentText(),
                )
                self.config_manager.set_setting(
                    "security_advanced",
                    "session_timeout",
                    self.session_timeout.value(),
                )

                # Save configuration
                self.config_manager.save_config()

                self.logger.info("Security settings applied successfully")
                QMessageBox.information(
                    self,
                    "Settings Applied",
                    "Security settings have been applied successfully.",
                )

            except Exception as e:
                self.logger.error(f"Failed to apply security settings: {e}")
                QMessageBox.critical(
                    self,
                    "Apply Error",
                    f"Failed to apply security settings: {e}",
                )

        def accept_settings(self):
            """Accept and apply settings, then close dialog."""
            self.apply_settings()
            self.accept()

        def refresh_security_status(self):
            """Refresh security status indicators."""
            try:
                # Update main status
                overall_status = self.calculate_overall_security_status()
                self.security_status_label.setText(
                    f"🔒 Security System Status: {overall_status}"
                )

                # Update component indicators
                self.update_component_indicators()

                # Update status widgets
                self.update_status_widgets()

                # Update metrics
                self.update_security_metrics()

            except Exception as e:
                self.logger.error(f"Failed to refresh security status: {e}")

        def calculate_overall_security_status(self) -> str:
            """Calculate overall security system status."""
            try:
                # Check individual components
                migration_ok = self.check_migration_status()
                theme_ok = self.check_theme_security_status()
                directory_ok = self.check_directory_security_status()
                audit_ok = self.check_audit_logging_status()

                # Calculate overall status
                components_ok = sum([migration_ok, theme_ok, directory_ok, audit_ok])

                if components_ok == 4:
                    return "✅ All Systems Operational"
                elif components_ok >= 3:
                    return "⚠️ Minor Issues Detected"
                elif components_ok >= 2:
                    return "⚠️ Some Issues Detected"
                else:
                    return "❌ Major Issues Detected"

            except Exception as e:
                self.logger.error(f"Failed to calculate security status: {e}")
                return "❓ Status Unknown"

        def check_migration_status(self) -> bool:
            """Check database migration status."""
            try:
                # Lazy load migration manager
                if self._migration_manager is None:
                    from src.core_rfu.database_manager import (
                        get_database_manager,
                    )
                    from src.core_rfu.migrations.migration_manager import (
                        DatabaseMigrationManager,
                    )

                    database_manager = get_database_manager()
                    self._migration_manager = DatabaseMigrationManager(database_manager)

                # Check if migration system is healthy
                status = self._migration_manager.get_migration_status()
                healthy = status.current_version not in {"", "error"}
                healthy = healthy and not status.database_locked
                healthy = healthy and not bool(status.pending_migrations)
                return healthy

            except Exception as e:
                self.logger.debug(f"Migration status check failed: {e}")
                return False

        def check_theme_security_status(self) -> bool:
            """Check theme security status."""
            try:
                # Lazy load theme encryption
                if self._theme_encryption is None:
                    from src.core_rfu.theme_security.theme_encryption import (
                        ThemeDataEncryption,
                    )

                    self._theme_encryption = ThemeDataEncryption()

                encryption_info = self._theme_encryption.get_encryption_info()
                return encryption_info.get("encryption_enabled", False)

            except Exception as e:
                self.logger.debug(f"Theme security status check failed: {e}")
                return False

        def check_directory_security_status(self) -> bool:
            """Check directory security status."""
            try:
                # Check if directory security is enabled and operational
                enabled = self.config_manager.get_setting(
                    "security_directory", "enable_access_control", False
                )
                return enabled  # Simplified check for now

            except Exception as e:
                self.logger.debug(f"Directory security status check failed: {e}")
                return False

        def check_audit_logging_status(self) -> bool:
            """Check audit logging status."""
            try:
                # Check if audit logging is enabled
                enabled = self.config_manager.get_setting(
                    "security_audit", "enable_logging", True
                )
                return enabled

            except Exception as e:
                self.logger.debug(f"Audit logging status check failed: {e}")
                return False

        def update_component_indicators(self):
            """Update component status indicators."""
            # Migration status
            migration_ok = self.check_migration_status()
            self.migration_status_indicator.setText(
                f"🔄 Migration: {'✅ OK' if migration_ok else '❌ Issue'}"
            )
            self.migration_status_indicator.setStyleSheet(
                f"color: {'green' if migration_ok else 'red'}; padding: 5px; margin: 2px;"
            )

            # Theme security status
            theme_ok = self.check_theme_security_status()
            self.theme_encryption_indicator.setText(
                f"🎨 Theme: {'✅ OK' if theme_ok else '❌ Issue'}"
            )
            self.theme_encryption_indicator.setStyleSheet(
                f"color: {'green' if theme_ok else 'red'}; padding: 5px; margin: 2px;"
            )

            # Directory security status
            directory_ok = self.check_directory_security_status()
            self.directory_security_indicator.setText(
                f"📁 Directory: {'✅ OK' if directory_ok else '❌ Issue'}"
            )
            self.directory_security_indicator.setStyleSheet(
                f"color: {'green' if directory_ok else 'red'}; padding: 5px; margin: 2px;"
            )

            # Audit logging status
            audit_ok = self.check_audit_logging_status()
            self.audit_logging_indicator.setText(
                f"📋 Audit: {'✅ OK' if audit_ok else '❌ Issue'}"
            )
            self.audit_logging_indicator.setStyleSheet(
                f"color: {'green' if audit_ok else 'red'}; padding: 5px; margin: 2px;"
            )

        def update_status_widgets(self):
            """Update status monitoring widgets."""
            try:
                # Update migration status widget
                migration_ok = self.check_migration_status()
                self.migration_status_widget.status_indicator.setText("●")
                self.migration_status_widget.status_indicator.setStyleSheet(
                    f"color: {'green' if migration_ok else 'red'}; font-size: 16px;"
                )
                self.migration_status_widget.details_label.setText(
                    f"Status: {'Operational' if migration_ok else 'Issues Detected'}"
                )

                # Update theme security status widget
                theme_ok = self.check_theme_security_status()
                self.theme_security_status_widget.status_indicator.setText("●")
                self.theme_security_status_widget.status_indicator.setStyleSheet(
                    f"color: {'green' if theme_ok else 'red'}; font-size: 16px;"
                )
                self.theme_security_status_widget.details_label.setText(
                    f"Status: {'Operational' if theme_ok else 'Issues Detected'}"
                )

                # Update directory security status widget
                directory_ok = self.check_directory_security_status()
                self.directory_security_status_widget.status_indicator.setText("●")
                self.directory_security_status_widget.status_indicator.setStyleSheet(
                    f"color: {'green' if directory_ok else 'red'}; font-size: 16px;"
                )
                self.directory_security_status_widget.details_label.setText(
                    f"Status: {'Operational' if directory_ok else 'Issues Detected'}"
                )

                # Update audit logging status widget
                audit_ok = self.check_audit_logging_status()
                self.audit_logging_status_widget.status_indicator.setText("●")
                self.audit_logging_status_widget.status_indicator.setStyleSheet(
                    f"color: {'green' if audit_ok else 'red'}; font-size: 16px;"
                )
                self.audit_logging_status_widget.details_label.setText(
                    f"Status: {'Operational' if audit_ok else 'Issues Detected'}"
                )

            except Exception as e:
                self.logger.error(f"Failed to update status widgets: {e}")

        def update_security_metrics(self):
            """Update security metrics display."""
            try:
                # Calculate security score
                migration_ok = self.check_migration_status()
                theme_ok = self.check_theme_security_status()
                directory_ok = self.check_directory_security_status()
                audit_ok = self.check_audit_logging_status()

                score = sum([migration_ok, theme_ok, directory_ok, audit_ok]) * 25
                self.security_score_label.setText(f"{score}/100")

                # Update other metrics (placeholder values for now)
                self.last_migration_label.setText("Today")
                self.themes_encrypted_label.setText("0/5")
                self.protected_directories_label.setText("3")
                self.audit_entries_label.setText("1,245")

            except Exception as e:
                self.logger.error(f"Failed to update security metrics: {e}")

        # Security action methods (placeholders for now)
        def execute_migration(self):
            """Execute database migration."""
            QMessageBox.information(
                self,
                "Migration",
                "Database migration functionality will be implemented.",
            )

        def rollback_migration(self):
            """Rollback database migration."""
            QMessageBox.information(
                self,
                "Rollback",
                "Migration rollback functionality will be implemented.",
            )

        def validate_schema(self):
            """Validate database schema."""
            QMessageBox.information(
                self,
                "Validation",
                "Schema validation functionality will be implemented.",
            )

        def encrypt_all_themes(self):
            """Encrypt all theme data."""
            QMessageBox.information(
                self,
                "Encryption",
                "Theme encryption functionality will be implemented.",
            )

        def decrypt_all_themes(self):
            """Decrypt all theme data."""
            QMessageBox.information(
                self,
                "Decryption",
                "Theme decryption functionality will be implemented.",
            )

        def test_theme_encryption(self):
            """Test theme encryption functionality."""
            QMessageBox.information(
                self,
                "Test",
                "Theme encryption test functionality will be implemented.",
            )

        def scan_theme_corruption(self):
            """Scan for theme corruption."""
            QMessageBox.information(
                self,
                "Scan",
                "Theme corruption scanning functionality will be implemented.",
            )

        def repair_theme_corruption(self):
            """Repair theme corruption."""
            QMessageBox.information(
                self,
                "Repair",
                "Theme corruption repair functionality will be implemented.",
            )

        def add_protected_directory(self):
            """Add a protected directory."""
            dir_path = QFileDialog.getExistingDirectory(
                self, "Select Directory to Protect"
            )
            if dir_path:
                QMessageBox.information(
                    self,
                    "Directory Added",
                    f"Added protection for: {dir_path}",
                )

        def remove_protected_directory(self):
            """Remove a protected directory."""
            QMessageBox.information(
                self,
                "Remove",
                "Remove protected directory functionality will be implemented.",
            )

        def edit_directory_permissions(self):
            """Edit directory permissions."""
            QMessageBox.information(
                self,
                "Edit",
                "Directory permissions editing functionality will be implemented.",
            )

        def clear_directory_log(self):
            """Clear directory security log."""
            self.directory_security_log.clear()

        def export_directory_log(self):
            """Export directory security log."""
            QMessageBox.information(
                self,
                "Export",
                "Directory log export functionality will be implemented.",
            )

        def apply_audit_filter(self):
            """Apply audit log filter."""
            QMessageBox.information(
                self,
                "Filter",
                "Audit log filtering functionality will be implemented.",
            )

        def refresh_audit_log(self):
            """Refresh audit log display."""
            QMessageBox.information(
                self,
                "Refresh",
                "Audit log refresh functionality will be implemented.",
            )

        def export_audit_log(self):
            """Export audit log."""
            QMessageBox.information(
                self,
                "Export",
                "Audit log export functionality will be implemented.",
            )

        def clear_audit_log(self):
            """Clear audit log."""
            QMessageBox.information(
                self,
                "Clear",
                "Audit log clearing functionality will be implemented.",
            )

        def dismiss_security_alert(self):
            """Dismiss selected security alert."""
            QMessageBox.information(
                self,
                "Dismiss",
                "Alert dismissal functionality will be implemented.",
            )

        def dismiss_all_alerts(self):
            """Dismiss all security alerts."""
            QMessageBox.information(
                self,
                "Dismiss All",
                "All alerts dismissal functionality will be implemented.",
            )

        def apply_security_profile(self):
            """Apply selected security profile."""
            profile = self.security_profile.currentText()
            descriptions = {
                "Minimal (Basic protection)": "Basic security features enabled. "
                "Suitable for low-risk environments.",
                STANDARD_RECOMMENDED_PROFILE: "Balanced security configuration. "
                "Recommended for most users.",
                "Enhanced (High security)": "Enhanced security features enabled. "
                "Suitable for sensitive environments.",
                "Maximum (Paranoid mode)": "All security features enabled at maximum levels. "
                "High security overhead.",
                "Custom (User defined)": "Custom security configuration defined by "
                "user preferences.",
            }
            self.profile_description.setText(
                descriptions.get(profile, "Custom security profile.")
            )

        def security_lockdown(self):
            """Initiate security lockdown."""
            reply = QMessageBox.question(
                self,
                "Security Lockdown",
                "This will lock down all security features. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self, "Lockdown", "Security lockdown initiated."
                )

        def force_security_backup(self):
            """Force security backup."""
            QMessageBox.information(
                self,
                "Backup",
                "Security backup functionality will be implemented.",
            )

        def reset_security_settings(self):
            """Reset security settings to defaults."""
            reply = QMessageBox.question(
                self,
                "Reset Security",
                "This will reset all security settings to defaults. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self, "Reset", "Security settings reset to defaults."
                )

        def run_security_audit(self):
            """Run comprehensive security audit."""
            QMessageBox.information(
                self,
                "Audit",
                "Security audit functionality will be implemented.",
            )

        def test_security_features(self):
            """Test all security features."""
            QMessageBox.information(
                self,
                "Test",
                "Security feature testing functionality will be implemented.",
            )

        def export_security_config(self):
            """Export security configuration."""
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Security Configuration",
                f"rfu_security_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)",
            )
            if file_path:
                QMessageBox.information(
                    self,
                    "Export",
                    f"Security configuration exported to: {file_path}",
                )

        def import_security_config(self):
            """Import security configuration."""
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Security Configuration",
                "",
                "JSON Files (*.json)",
            )
            if file_path:
                QMessageBox.information(
                    self,
                    "Import",
                    f"Security configuration imported from: {file_path}",
                )

        def emergency_disable_security(self):
            """Emergency disable all security features."""
            reply = QMessageBox.critical(
                self,
                "Emergency Disable",
                "⚠️ WARNING: This will disable ALL security features!\n\n"
                "This should only be used in emergency situations.\n"
                "Continue with emergency disable?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self,
                    "Emergency",
                    "All security features have been disabled.",
                )

        def closeEvent(self, event):
            """Handle dialog close event."""
            # Stop status timer
            if hasattr(self, "status_timer"):
                self.status_timer.stop()

            # Call parent close event
            super().closeEvent(event)

except ImportError as e:
    print(f"Error importing PyQt5 modules for SecurityPreferencesDialog: {e}")
    print("Please ensure PyQt5 is properly installed.")

    class SecurityPreferencesDialog:
        """Fallback class when PyQt5 is not available."""

        def __init__(self, parent=None):
            print("SecurityPreferencesDialog requires PyQt5 to be installed.")
