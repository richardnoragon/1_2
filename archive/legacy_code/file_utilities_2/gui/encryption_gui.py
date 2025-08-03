"""
Encryption/Decryption GUI using StandardWindow base class.

This module provides a modern, user-friendly interface for encryption and
decryption operations with progress tracking and hub integration.
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTextEdit, QProgressBar, 
                             QGroupBox, QRadioButton, QCheckBox, QTabWidget,
                             QFileDialog, QMessageBox, QSplitter, QFrame,
                             QScrollArea, QGridLayout, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.core.encryption_logic import EncryptionLogic
from file_utilities_2.core.encryption_config import EncryptionConfig
from file_utilities_2.core.encryption_logging import EncryptionLogger


class EncryptionWorkerThread(QThread):
    """Worker thread for encryption/decryption operations."""
    
    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(dict)  # results
    operation_failed = pyqtSignal(str)  # error message
    operation_cancelled = pyqtSignal(str)  # cancellation message
    
    def __init__(self, encryption_logic: EncryptionLogic):
        super().__init__()
        self.encryption_logic = encryption_logic
        self.operation_type = None
        self.operation_params = {}
        
        # Connect encryption logic signals
        self.encryption_logic.progress_updated.connect(self.progress_updated)
        self.encryption_logic.operation_completed.connect(
            self.operation_completed)
        self.encryption_logic.operation_failed.connect(self.operation_failed)
        self.encryption_logic.operation_cancelled.connect(
            self.operation_cancelled)
    
    def set_operation(self, operation_type: str, **params):
        """Set the operation to perform."""
        self.operation_type = operation_type
        self.operation_params = params
    
    def run(self):
        """Execute the operation."""
        try:
            if self.operation_type == "encrypt_file":
                self.encryption_logic.encrypt_file(**self.operation_params)
            elif self.operation_type == "decrypt_file":
                self.encryption_logic.decrypt_file(**self.operation_params)
            elif self.operation_type == "encrypt_directory":
                self.encryption_logic.encrypt_directory(**self.operation_params)
            elif self.operation_type == "decrypt_directory":
                self.encryption_logic.decrypt_directory(**self.operation_params)
        except Exception as e:
            self.operation_failed.emit(str(e))


class EncryptionGUI(StandardWindow):
    """
    Modern encryption/decryption GUI with StandardWindow base.
    
    Provides comprehensive encryption functionality with progress tracking,
    configuration management, and hub integration.
    """
    
    def __init__(self, hub_instance=None):
        """
        Initialize encryption GUI.
        
        Args:
            hub_instance: Optional hub instance for integration
        """
        self.hub_instance = hub_instance
        
        # Initialize core components
        self.config = EncryptionConfig(hub_instance=hub_instance)
        self.logger = EncryptionLogger(hub_instance=hub_instance)
        self.encryption_logic = EncryptionLogic(
            config=self.config, 
            logger=self.logger,
            hub_instance=hub_instance
        )
        
        # Worker thread for operations
        self.worker_thread = EncryptionWorkerThread(self.encryption_logic)
        self._connect_worker_signals()
        
        # UI state
        self.current_key = None
        self.operation_in_progress = False
        
        super().__init__(title="Encryption/Decryption Tool")
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_file_operations_tab()
        self._create_directory_operations_tab()
        self._create_key_management_tab()
        self._create_settings_tab()
        self._create_logs_tab()
        
        # Create status and progress area
        self._create_status_area()
        
        # Apply initial styling
        self._apply_custom_styling()
    
    def _create_file_operations_tab(self):
        """Create file operations tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = self.create_header("File Encryption/Decryption")
        layout.addWidget(header)
        
        # File selection group
        file_group = self.create_group_box("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Input file selection
        input_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select file to encrypt/decrypt...")
        input_browse_btn = self.create_button("Browse", 
                                             self._browse_input_file, 
                                             primary=False)
        input_layout.addWidget(QLabel("Input File:"))
        input_layout.addWidget(self.input_file_edit)
        input_layout.addWidget(input_browse_btn)
        file_layout.addLayout(input_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Output file path (optional)...")
        output_browse_btn = self.create_button("Browse", 
                                              self._browse_output_file, 
                                              primary=False)
        output_layout.addWidget(QLabel("Output File:"))
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(output_browse_btn)
        file_layout.addLayout(output_layout)
        
        layout.addWidget(file_group)
        
        # Key management group
        key_group = self.create_group_box("Key Management")
        key_layout = QVBoxLayout(key_group)
        
        # Key file selection
        key_file_layout = QHBoxLayout()
        self.key_file_edit = QLineEdit()
        self.key_file_edit.setPlaceholderText("Select encryption key file...")
        key_browse_btn = self.create_button("Browse", 
                                           self._browse_key_file, 
                                           primary=False)
        generate_key_btn = self.create_button("Generate New Key", 
                                            self._generate_new_key, 
                                            primary=False)
        
        key_file_layout.addWidget(QLabel("Key File:"))
        key_file_layout.addWidget(self.key_file_edit)
        key_file_layout.addWidget(key_browse_btn)
        key_file_layout.addWidget(generate_key_btn)
        key_layout.addLayout(key_file_layout)
        
        # Key status
        self.key_status_label = QLabel("No key loaded")
        self.key_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        key_layout.addWidget(self.key_status_label)
        
        layout.addWidget(key_group)
        
        # Operation buttons
        button_layout = QHBoxLayout()
        self.encrypt_file_btn = self.create_button("Encrypt File", 
                                                  self._encrypt_file)
        self.decrypt_file_btn = self.create_button("Decrypt File", 
                                                  self._decrypt_file)
        
        button_layout.addWidget(self.encrypt_file_btn)
        button_layout.addWidget(self.decrypt_file_btn)
        layout.addLayout(button_layout)
        
        # Add stretch
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "File Operations")
    
    def _create_directory_operations_tab(self):
        """Create directory operations tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = self.create_header("Directory Encryption/Decryption")
        layout.addWidget(header)
        
        # Directory selection group
        dir_group = self.create_group_box("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)
        
        # Input directory
        input_dir_layout = QHBoxLayout()
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("Select directory to process...")
        input_dir_browse_btn = self.create_button("Browse", 
                                                 self._browse_input_directory, 
                                                 primary=False)
        
        input_dir_layout.addWidget(QLabel("Input Directory:"))
        input_dir_layout.addWidget(self.input_dir_edit)
        input_dir_layout.addWidget(input_dir_browse_btn)
        dir_layout.addLayout(input_dir_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.recursive_checkbox = QCheckBox("Process subdirectories recursively")
        self.recursive_checkbox.setChecked(True)
        options_layout.addWidget(self.recursive_checkbox)
        dir_layout.addLayout(options_layout)
        
        layout.addWidget(dir_group)
        
        # Key management (reuse from file tab)
        key_group = self.create_group_box("Key Management")
        key_layout = QVBoxLayout(key_group)
        
        key_info_label = QLabel("Use the same key management as File Operations tab")
        key_info_label.setStyleSheet("color: #666; font-style: italic;")
        key_layout.addWidget(key_info_label)
        
        layout.addWidget(key_group)
        
        # Operation buttons
        button_layout = QHBoxLayout()
        self.encrypt_dir_btn = self.create_button("Encrypt Directory", 
                                                 self._encrypt_directory)
        self.decrypt_dir_btn = self.create_button("Decrypt Directory", 
                                                 self._decrypt_directory)
        
        button_layout.addWidget(self.encrypt_dir_btn)
        button_layout.addWidget(self.decrypt_dir_btn)
        layout.addLayout(button_layout)
        
        # Add stretch
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Directory Operations")
    
    def _create_key_management_tab(self):
        """Create key management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = self.create_header("Key Management")
        layout.addWidget(header)
        
        # Key generation group
        gen_group = self.create_group_box("Generate New Key")
        gen_layout = QVBoxLayout(gen_group)
        
        # Key file path
        key_path_layout = QHBoxLayout()
        self.new_key_path_edit = QLineEdit()
        self.new_key_path_edit.setPlaceholderText("Enter path for new key file...")
        new_key_browse_btn = self.create_button("Browse", 
                                               self._browse_new_key_path, 
                                               primary=False)
        
        key_path_layout.addWidget(QLabel("Key File Path:"))
        key_path_layout.addWidget(self.new_key_path_edit)
        key_path_layout.addWidget(new_key_browse_btn)
        gen_layout.addLayout(key_path_layout)
        
        # Generate button
        generate_btn = self.create_button("Generate Key", self._generate_key)
        gen_layout.addWidget(generate_btn)
        
        layout.addWidget(gen_group)
        
        # Key information group
        info_group = self.create_group_box("Current Key Information")
        info_layout = QVBoxLayout(info_group)
        
        self.key_info_text = QTextEdit()
        self.key_info_text.setReadOnly(True)
        self.key_info_text.setMaximumHeight(150)
        self.key_info_text.setPlainText("No key loaded")
        info_layout.addWidget(self.key_info_text)
        
        layout.addWidget(info_group)
        
        # Key operations group
        ops_group = self.create_group_box("Key Operations")
        ops_layout = QHBoxLayout(ops_group)
        
        load_key_btn = self.create_button("Load Key", self._load_key, 
                                         primary=False)
        clear_key_btn = self.create_button("Clear Key", self._clear_key, 
                                          primary=False)
        
        ops_layout.addWidget(load_key_btn)
        ops_layout.addWidget(clear_key_btn)
        
        layout.addWidget(ops_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Key Management")
    
    def _create_settings_tab(self):
        """Create settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = self.create_header("Settings")
        layout.addWidget(header)
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Performance settings
        perf_group = self.create_group_box("Performance Settings")
        perf_layout = QGridLayout(perf_group)
        
        # Buffer size
        perf_layout.addWidget(QLabel("Buffer Size (KB):"), 0, 0)
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1, 1024)
        self.buffer_size_spin.setValue(8)
        self.buffer_size_spin.setSuffix(" KB")
        perf_layout.addWidget(self.buffer_size_spin, 0, 1)
        
        # Progress update frequency
        perf_layout.addWidget(QLabel("Progress Update Frequency:"), 1, 0)
        self.progress_freq_spin = QSpinBox()
        self.progress_freq_spin.setRange(10, 1000)
        self.progress_freq_spin.setValue(100)
        perf_layout.addWidget(self.progress_freq_spin, 1, 1)
        
        scroll_layout.addWidget(perf_group)
        
        # Security settings
        sec_group = self.create_group_box("Security Settings")
        sec_layout = QVBoxLayout(sec_group)
        
        self.secure_delete_checkbox = QCheckBox("Secure delete temporary files")
        self.secure_delete_checkbox.setChecked(True)
        sec_layout.addWidget(self.secure_delete_checkbox)
        
        self.audit_operations_checkbox = QCheckBox("Audit all operations")
        self.audit_operations_checkbox.setChecked(True)
        sec_layout.addWidget(self.audit_operations_checkbox)
        
        scroll_layout.addWidget(sec_group)
        
        # UI settings
        ui_group = self.create_group_box("User Interface")
        ui_layout = QVBoxLayout(ui_group)
        
        self.show_progress_details_checkbox = QCheckBox("Show detailed progress")
        self.show_progress_details_checkbox.setChecked(True)
        ui_layout.addWidget(self.show_progress_details_checkbox)
        
        self.confirm_overwrite_checkbox = QCheckBox("Confirm file overwrite")
        self.confirm_overwrite_checkbox.setChecked(True)
        ui_layout.addWidget(self.confirm_overwrite_checkbox)
        
        scroll_layout.addWidget(ui_group)
        
        # Hub integration settings
        hub_group = self.create_group_box("Hub Integration")
        hub_layout = QVBoxLayout(hub_group)
        
        self.hub_communication_checkbox = QCheckBox("Enable hub communication")
        self.hub_communication_checkbox.setChecked(True)
        hub_layout.addWidget(self.hub_communication_checkbox)
        
        self.hub_progress_checkbox = QCheckBox("Report progress to hub")
        self.hub_progress_checkbox.setChecked(True)
        hub_layout.addWidget(self.hub_progress_checkbox)
        
        scroll_layout.addWidget(hub_group)
        
        # Settings buttons
        settings_button_layout = QHBoxLayout()
        save_settings_btn = self.create_button("Save Settings", 
                                              self._save_settings)
        reset_settings_btn = self.create_button("Reset to Defaults", 
                                               self._reset_settings, 
                                               primary=False)
        
        settings_button_layout.addWidget(save_settings_btn)
        settings_button_layout.addWidget(reset_settings_btn)
        scroll_layout.addLayout(settings_button_layout)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Settings")
    
    def _create_logs_tab(self):
        """Create logs tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = self.create_header("Operation Logs")
        layout.addWidget(header)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_display)
        
        # Log controls
        log_controls_layout = QHBoxLayout()
        
        clear_logs_btn = self.create_button("Clear Logs", self._clear_logs, 
                                           primary=False)
        export_logs_btn = self.create_button("Export Logs", self._export_logs, 
                                            primary=False)
        
        log_controls_layout.addWidget(clear_logs_btn)
        log_controls_layout.addWidget(export_logs_btn)
        log_controls_layout.addStretch()
        
        layout.addLayout(log_controls_layout)
        
        self.tab_widget.addTab(tab, "Logs")
    
    def _create_status_area(self):
        """Create status and progress area."""
        # Progress group
        progress_group = self.create_group_box("Operation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = self.create_progress_bar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        # Cancel button
        self.cancel_btn = self.create_button("Cancel Operation", 
                                           self._cancel_operation, 
                                           primary=False)
        self.cancel_btn.setVisible(False)
        progress_layout.addWidget(self.cancel_btn)
        
        self.main_layout.addWidget(progress_group)
    
    def _apply_custom_styling(self):
        """Apply custom styling to the encryption GUI."""
        # Custom styles for encryption-specific elements
        self.setStyleSheet(self.styleSheet() + """
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007acc;
            }
            
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
    
    def _connect_worker_signals(self):
        """Connect worker thread signals."""
        self.worker_thread.progress_updated.connect(self._update_progress)
        self.worker_thread.operation_completed.connect(
            self._operation_completed)
        self.worker_thread.operation_failed.connect(self._operation_failed)
        self.worker_thread.operation_cancelled.connect(
            self._operation_cancelled)
    
    def _load_settings(self):
        """Load settings from configuration."""
        # Load performance settings
        perf_settings = self.config.get_performance_settings()
        self.buffer_size_spin.setValue(
            perf_settings.get('buffer_size', 8192) // 1024)
        self.progress_freq_spin.setValue(
            perf_settings.get('progress_update_frequency', 100))
        
        # Load security settings
        sec_settings = self.config.get_security_settings()
        self.secure_delete_checkbox.setChecked(
            sec_settings.get('secure_delete_temp_files', True))
        self.audit_operations_checkbox.setChecked(
            sec_settings.get('audit_all_operations', True))
        
        # Load UI settings
        ui_settings = self.config.get_ui_settings()
        self.show_progress_details_checkbox.setChecked(
            ui_settings.get('show_advanced_options', False))
        self.confirm_overwrite_checkbox.setChecked(
            self.config.get_setting('user_preferences.confirm_overwrite', True))
        
        # Load hub settings
        hub_settings = self.config.get_hub_settings()
        self.hub_communication_checkbox.setChecked(
            hub_settings.get('enable_hub_communication', True))
        self.hub_progress_checkbox.setChecked(
            hub_settings.get('report_progress_to_hub', True))
    
    def _save_settings(self):
        """Save current settings to configuration."""
        try:
            # Save performance settings
            self.config.set_setting('performance_settings.buffer_size', 
                                   self.buffer_size_spin.value() * 1024)
            self.config.set_setting('performance_settings.progress_update_frequency', 
                                   self.progress_freq_spin.value())
            
            # Save security settings
            self.config.set_setting('security_settings.secure_delete_temp_files', 
                                   self.secure_delete_checkbox.isChecked())
            self.config.set_setting('security_settings.audit_all_operations', 
                                   self.audit_operations_checkbox.isChecked())
            
            # Save UI settings
            self.config.set_setting('ui_settings.show_advanced_options', 
                                   self.show_progress_details_checkbox.isChecked())
            self.config.set_setting('user_preferences.confirm_overwrite', 
                                   self.confirm_overwrite_checkbox.isChecked())
            
            # Save hub settings
            self.config.set_setting('hub_integration.enable_hub_communication', 
                                   self.hub_communication_checkbox.isChecked())
            self.config.set_setting('hub_integration.report_progress_to_hub', 
                                   self.hub_progress_checkbox.isChecked())
            
            self.show_status_message("Settings saved successfully")
            
        except Exception as e:
            self.show_error_dialog("Settings Error", 
                                 f"Failed to save settings: {str(e)}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        try:
            self.config.reset_to_defaults()
            self._load_settings()
            self.show_status_message("Settings reset to defaults")
        except Exception as e:
            self.show_error_dialog("Settings Error", 
                                 f"Failed to reset settings: {str(e)}")
    
    # File operation methods
    def _browse_input_file(self):
        """Browse for input file."""
        file_path = self.get_file_path("Select File to Encrypt/Decrypt")
        if file_path:
            self.input_file_edit.setText(file_path)
    
    def _browse_output_file(self):
        """Browse for output file."""
        file_path = self.get_save_file_path("Select Output File")
        if file_path:
            self.output_file_edit.setText(file_path)
    
    def _browse_input_directory(self):
        """Browse for input directory."""
        dir_path = self.get_directory_path("Select Directory to Process")
        if dir_path:
            self.input_dir_edit.setText(dir_path)
    
    def _browse_key_file(self):
        """Browse for key file."""
        file_path = self.get_file_path("Select Encryption Key File", 
                                     "Key Files (*.key);;All Files (*)")
        if file_path:
            self.key_file_edit.setText(file_path)
            self._load_key_from_file(file_path)
    
    def _browse_new_key_path(self):
        """Browse for new key file path."""
        file_path = self.get_save_file_path("Save New Key File", 
                                          "Key Files (*.key);;All Files (*)")
        if file_path:
            if not file_path.endswith('.key'):
                file_path += '.key'
            self.new_key_path_edit.setText(file_path)
    
    def _generate_new_key(self):
        """Generate new key for current operation."""
        try:
            key = self.encryption_logic.generate_key()
            self.current_key = key
            self._update_key_status("New key generated (not saved)")
            self.logger.log_key_operation("generate")
        except Exception as e:
            self.show_error_dialog("Key Generation Error", str(e))
    
    def _generate_key(self):
        """Generate and save new key."""
        key_path = self.new_key_path_edit.text().strip()
        if not key_path:
            self.show_error_dialog("Key Generation Error", 
                                 "Please specify a path for the new key file")
            return
        
        try:
            key = self.encryption_logic.generate_key()
            if self.encryption_logic.save_key(key, key_path):
                self.current_key = key
                self.key_file_edit.setText(key_path)
                self._update_key_status(f"Key saved to: {os.path.basename(key_path)}")
                self.show_status_message("Key generated and saved successfully")
                self.logger.log_key_operation("generate", key_path)
            else:
                self.show_error_dialog("Key Generation Error", 
                                     "Failed to save key file")
        except Exception as e:
            self.show_error_dialog("Key Generation Error", str(e))
    
    def _load_key(self):
        """Load key from file."""
        key_path = self.key_file_edit.text().strip()
        if not key_path:
            self.show_error_dialog("Key Loading Error", 
                                 "Please specify a key file path")
            return
        
        self._load_key_from_file(key_path)
    
    def _load_key_from_file(self, key_path: str):
        """Load key from specified file."""
        try:
            key = self.encryption_logic.load_key(key_path)
            if key:
                self.current_key = key
                self._update_key_status(f"Key loaded: {os.path.basename(key_path)}")
                self.logger.log_key_operation("load", key_path)
            else:
                self.show_error_dialog("Key Loading Error", 
                                     "Failed to load key file")
        except Exception as e:
            self.show_error_dialog("Key Loading Error", str(e))
    
    def _clear_key(self):
        """Clear current key."""
        self.current_key = None
        self.key_file_edit.clear()
        self._update_key_status("No key loaded")
    
    def _update_key_status(self, status: str):
        """Update key status display."""
        self.key_status_label.setText(status)
        if "loaded" in status.lower() or "generated" in status.lower():
            self.key_status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
        else:
            self.key_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        # Update key info
        if self.current_key:
            key_info = f"Key loaded successfully\nKey length: {len(self.current_key)} bytes"
        else:
            key_info = "No key loaded"
        
        self.key_info_text.setPlainText(key_info)
    
    def _encrypt_file(self):
        """Start file encryption."""
        if not self._validate_file_operation():
            return
        
        input_path = self.input_file_edit.text().strip()
        output_path = self.output_file_edit.text().strip() or None
        
        self._start_operation("encrypt_file", 
                            file_path=input_path, 
                            key=self.current_key, 
                            output_path=output_path)
    
    def _decrypt_file(self):
        """Start file decryption."""
        if not self._validate_file_operation():
            return
        
        input_path = self.input_file_edit.text().strip()
        output_path = self.output_file_edit.text().strip() or None
        
        self._start_operation("decrypt_file", 
                            file_path=input_path, 
                            key=self.current_key, 
                            output_path=output_path)
    
    def _encrypt_directory(self):
        """Start directory encryption."""
        if not self._validate_directory_operation():
            return
        
        dir_path = self.input_dir_edit.text().strip()
        recursive = self.recursive_checkbox.isChecked()
        
        self._start_operation("encrypt_directory", 
                            directory_path=dir_path, 
                            key=self.current_key, 
                            recursive=recursive)
    
    def _decrypt_directory(self):
        """Start directory decryption."""
        if not self._validate_directory_operation():
            return
        
        dir_path = self.input_dir_edit.text().strip()
        recursive = self.recursive_checkbox.isChecked()
        
        self._start_operation("decrypt_directory", 
                            directory_path=dir_path, 
                            key=self.current_key, 
                            recursive=recursive)
    
    def _validate_file_operation(self) -> bool:
        """Validate file operation inputs."""
        if not self.current_key:
            self.show_error_dialog("Validation Error",
                                 "Please load or generate an encryption key first")
            return False
        
        input_path = self.input_file_edit.text().strip()
        if not input_path:
            self.show_error_dialog("Validation Error",
                                 "Please select an input file")
            return False
        
        if not os.path.exists(input_path):
            self.show_error_dialog("Validation Error",
                                 "Input file does not exist")
            return False
        
        return True
    
    def _validate_directory_operation(self) -> bool:
        """Validate directory operation inputs."""
        if not self.current_key:
            self.show_error_dialog("Validation Error",
                                 "Please load or generate an encryption key first")
            return False
        
        dir_path = self.input_dir_edit.text().strip()
        if not dir_path:
            self.show_error_dialog("Validation Error",
                                 "Please select an input directory")
            return False
        
        if not os.path.exists(dir_path):
            self.show_error_dialog("Validation Error",
                                 "Input directory does not exist")
            return False
        
        return True
    
    def _start_operation(self, operation_type: str, **params):
        """Start an encryption/decryption operation."""
        if self.operation_in_progress:
            self.show_warning_dialog("Operation in Progress",
                                    "Another operation is already running")
            return
        
        try:
            self.operation_in_progress = True
            self._update_ui_for_operation(True)
            
            # Setup worker thread
            self.worker_thread.set_operation(operation_type, **params)
            self.worker_thread.start()
            
            self.show_status_message(f"Starting {operation_type}...")
            
        except Exception as e:
            self.operation_in_progress = False
            self._update_ui_for_operation(False)
            self.show_error_dialog("Operation Error", str(e))
    
    def _update_ui_for_operation(self, in_progress: bool):
        """Update UI state for operation progress."""
        # Disable/enable operation buttons
        self.encrypt_file_btn.setEnabled(not in_progress)
        self.decrypt_file_btn.setEnabled(not in_progress)
        self.encrypt_dir_btn.setEnabled(not in_progress)
        self.decrypt_dir_btn.setEnabled(not in_progress)
        
        # Show/hide progress elements
        self.progress_bar.setVisible(in_progress)
        self.cancel_btn.setVisible(in_progress)
        
        if not in_progress:
            self.progress_bar.setValue(0)
            self.progress_label.setText("Ready")
    
    def _update_progress(self, current: int, total: int, message: str):
        """Update progress display."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        
        self.progress_label.setText(message)
        self.show_status_message(message)
        
        # Add to log display
        self._add_log_message(f"Progress: {message}")
    
    def _operation_completed(self, results: Dict[str, Any]):
        """Handle operation completion."""
        self.operation_in_progress = False
        self._update_ui_for_operation(False)
        
        # Show completion message
        success_count = results.get('success_count', 0)
        error_count = results.get('error_count', 0)
        
        if error_count == 0:
            self.show_info_dialog("Operation Complete",
                                f"Operation completed successfully!\n"
                                f"Files processed: {success_count}")
        else:
            self.show_warning_dialog("Operation Complete with Errors",
                                    f"Operation completed with some errors.\n"
                                    f"Successful: {success_count}\n"
                                    f"Errors: {error_count}")
        
        self._add_log_message(f"Operation completed: {results}")
    
    def _operation_failed(self, error_message: str):
        """Handle operation failure."""
        self.operation_in_progress = False
        self._update_ui_for_operation(False)
        
        self.show_error_dialog("Operation Failed", error_message)
        self._add_log_message(f"Operation failed: {error_message}")
    
    def _operation_cancelled(self, message: str):
        """Handle operation cancellation."""
        self.operation_in_progress = False
        self._update_ui_for_operation(False)
        
        self.show_info_dialog("Operation Cancelled", message)
        self._add_log_message(f"Operation cancelled: {message}")
    
    def _cancel_operation(self):
        """Cancel current operation."""
        if self.operation_in_progress:
            self.encryption_logic.cancel_operation()
    
    def _add_log_message(self, message: str):
        """Add message to log display."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_display.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.End)
        self.log_display.setTextCursor(cursor)
    
    def _clear_logs(self):
        """Clear log display."""
        self.log_display.clear()
    
    def _export_logs(self):
        """Export logs to file."""
        file_path = self.get_save_file_path("Export Logs",
                                          "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.show_status_message("Logs exported successfully")
            except Exception as e:
                self.show_error_dialog("Export Error",
                                     f"Failed to export logs: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.operation_in_progress:
            reply = QMessageBox.question(
                self, 'Close Application',
                'An operation is in progress. Do you want to cancel it and exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.encryption_logic.cancel_operation()
                self.worker_thread.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            # Save window state
            ui_settings = self.config.get_ui_settings()
            ui_settings['window_size'] = (self.width(), self.height())
            ui_settings['window_position'] = (self.x(), self.y())
            
            self.config.set_setting('ui_settings.window_size',
                                   ui_settings['window_size'])
            self.config.set_setting('ui_settings.window_position',
                                   ui_settings['window_position'])
            
            # Close logger
            self.logger.close()
            
            event.accept()


def main():
    """Main function for standalone execution."""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = EncryptionGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()