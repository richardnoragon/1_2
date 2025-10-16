"""
Test Data Setup for Hub.py Unit Tests
Created: 2025-08-28
Target: src/rfu/hub.py

This module provides test data, fixtures, and mock objects
for comprehensive testing of the hub.py module.
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock


class MockLogger:
    """Mock logger for testing purposes."""

    def __init__(self):
        self.messages = []
        self.handlers = []

    def info(self, message):
        self.messages.append(("INFO", message))

    def warning(self, message):
        self.messages.append(("WARNING", message))

    def error(self, message):
        self.messages.append(("ERROR", message))

    def debug(self, message):
        self.messages.append(("DEBUG", message))

    def get_logger(self, name):
        return self


class MockConfigManager:
    """Mock configuration manager for testing."""

    def __init__(self):
        self.config_data = {
            "gui_theme": "default",
            "log_level": "INFO",
            "max_log_size": 1000000,
            "auto_save": True,
            "backup_count": 5,
            "update_check": True,
            "default_directory": str(Path.home()),
            "show_tooltips": True,
            "enable_animations": True,
            "window_geometry": "800x600+100+100",
        }

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value

    def save(self):
        pass


class MockQtObjects:
    """Mock PyQt5 objects for testing GUI components."""

    @staticmethod
    def create_mock_widget():
        """Create a mock Qt widget."""
        widget = Mock()
        widget.show = Mock()
        widget.hide = Mock()
        widget.close = Mock()
        widget.setWindowTitle = Mock()
        widget.setGeometry = Mock()
        widget.resize = Mock()
        widget.move = Mock()
        return widget

    @staticmethod
    def create_mock_button():
        """Create a mock QPushButton."""
        button = Mock()
        button.setText = Mock()
        button.setToolTip = Mock()
        button.clicked = Mock()
        button.clicked.connect = Mock()
        button.setStyleSheet = Mock()
        button.setMinimumSize = Mock()
        button.setMaximumSize = Mock()
        button.setSizePolicy = Mock()
        return button

    @staticmethod
    def create_mock_menu_bar():
        """Create a mock menu bar."""
        menu_bar = Mock()
        menu_bar.addMenu = Mock()
        menu_bar.addAction = Mock()
        return menu_bar

    @staticmethod
    def create_mock_status_bar():
        """Create a mock status bar."""
        status_bar = Mock()
        status_bar.showMessage = Mock()
        status_bar.clearMessage = Mock()
        return status_bar


class HubTestData:
    """Test data provider for hub.py testing."""

    def __init__(self):
        self.temp_dir = None
        self.setup_temp_environment()

    def setup_temp_environment(self):
        """Setup temporary test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="hub_test_")

        # Create mock log files
        self.create_mock_log_files()

        # Create mock config files
        self.create_mock_config_files()

    def create_mock_log_files(self):
        """Create mock log files for testing."""
        log_dir = Path(self.temp_dir) / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create sample log entries
        log_entries = [
            "2025-08-28 10:00:00 - INFO - RFU Hub initialized successfully",
            "2025-08-28 10:01:00 - INFO - Tool registered: file_catalog",
            "2025-08-28 10:02:00 - WARNING - PyQt5 not available - GUI functionality limited",
            "2025-08-28 10:03:00 - ERROR - Failed to load tool: network_scanner",
            "2025-08-28 10:04:00 - INFO - Tool unregistered: file_catalog",
        ]

        log_file = log_dir / "rfu_hub.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(log_entries))

        return log_file

    def create_mock_config_files(self):
        """Create mock configuration files."""
        config_dir = Path(self.temp_dir) / "config"
        config_dir.mkdir(exist_ok=True)

        config_data = {
            "version": "1.0.0",
            "settings": {
                "theme": "default",
                "language": "en",
                "auto_update": True,
                "debug_mode": False,
            },
            "paths": {
                "data_directory": str(self.temp_dir / "data"),
                "temp_directory": str(self.temp_dir / "temp"),
                "backup_directory": str(self.temp_dir / "backups"),
            },
        }

        config_file = config_dir / "settings.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        return config_file

    def get_sample_tool_registry(self) -> Dict[str, Any]:
        """Get sample tool registry data."""
        return {
            "file_catalog": {
                "class": "FileCatalogGUI",
                "module": "utilities.file_operations.file_catalog",
                "status": "registered",
                "last_used": datetime.now() - timedelta(hours=1),
            },
            "network_scanner": {
                "class": "NetworkScannerGUI",
                "module": "utilities.network.network_scanner",
                "status": "error",
                "last_used": datetime.now() - timedelta(days=1),
            },
            "secure_delete": {
                "class": "SecureDeleteGUI",
                "module": "utilities.file_operations.secure_delete",
                "status": "available",
                "last_used": None,
            },
        }

    def get_sample_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get sample tool status data."""
        base_time = datetime.now()
        return {
            "file_catalog": {
                "status": "active",
                "last_activity": base_time - timedelta(minutes=5),
                "progress": 75,
                "current_operation": "Scanning directories",
            },
            "network_scanner": {
                "status": "idle",
                "last_activity": base_time - timedelta(hours=2),
                "progress": 0,
                "current_operation": None,
            },
            "secure_delete": {
                "status": "processing",
                "last_activity": base_time - timedelta(seconds=30),
                "progress": 45,
                "current_operation": "Wiping file data",
            },
        }

    def get_sample_resource_manager(self) -> Dict[str, Dict[str, Any]]:
        """Get sample resource manager data."""
        return {
            "cpu": {
                "available": False,
                "allocated_to": "file_catalog",
                "allocated_at": datetime.now() - timedelta(minutes=10),
            },
            "memory": {"available": True, "allocated_to": None, "allocated_at": None},
            "disk": {
                "available": False,
                "allocated_to": "secure_delete",
                "allocated_at": datetime.now() - timedelta(minutes=2),
            },
        }

    def get_sample_menu_callbacks(self) -> List[str]:
        """Get list of sample menu callback names."""
        return [
            "new_project",
            "open_file",
            "save_file",
            "save_as_file",
            "export_data",
            "import_data",
            "print_document",
            "show_preferences",
            "undo",
            "redo",
            "cut",
            "copy",
            "paste",
            "select_all",
            "find",
            "replace",
            "zoom_in",
            "zoom_out",
            "zoom_reset",
            "refresh",
            "show_options",
            "show_documentation",
            "show_shortcuts",
            "show_about",
        ]

    def get_sample_tool_methods(self) -> List[str]:
        """Get list of sample tool opening method names."""
        return [
            "open_file_catalog",
            "open_file_touch",
            "open_file_splitter",
            "open_secure_delete",
            "open_compression_tools",
            "open_duplicate_finder",
            "open_image_metadata",
            "open_office_metadata",
            "open_pdf_tools",
            "open_network_transfer",
            "open_network_scan",
            "open_port_scanner",
            "open_network_monitor",
            "open_bandwidth_test",
            "open_wake_on_lan",
            "open_encrypt_decrypt",
            "open_hash_calculator",
            "open_password_generator",
            "open_security_preferences",
            "open_key_manager",
            "open_secure_notes",
            "open_clipboard_manager",
            "open_system_monitor",
            "open_registry_tools",
            "open_disk_tools",
            "open_process_manager",
            "open_service_manager",
        ]

    def create_mock_tool_instance(self, tool_name: str = "test_tool"):
        """Create a mock tool instance for testing."""
        tool = Mock()
        tool.name = tool_name
        tool.show = Mock()
        tool.hide = Mock()
        tool.close = Mock()
        tool.status_changed = Mock()
        tool.progress_updated = Mock()
        tool.error_occurred = Mock()
        return tool

    def cleanup(self):
        """Clean up temporary test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestFixtures:
    """Test fixtures for hub.py testing."""

    @staticmethod
    def hub_with_mocks():
        """Create hub instance with all dependencies mocked."""
        with patch("rfu.hub.get_log_manager") as mock_log_mgr, patch(
            "rfu.hub.get_config_manager"
        ) as mock_config_mgr, patch("rfu.hub.PYQT5_AVAILABLE", False):

            mock_log_mgr.return_value.get_logger.return_value = MockLogger()
            mock_config_mgr.return_value = MockConfigManager()

            from tabbed_hub import RFUHub

            return RFUHub()

    @staticmethod
    def mock_pyqt5_environment():
        """Create mock PyQt5 environment for GUI testing."""
        return {
            "QMainWindow": Mock,
            "QWidget": Mock,
            "QPushButton": MockQtObjects.create_mock_button,
            "QLabel": Mock,
            "QTabWidget": Mock,
            "QStatusBar": MockQtObjects.create_mock_status_bar,
            "QVBoxLayout": Mock,
            "QHBoxLayout": Mock,
            "QGridLayout": Mock,
            "QTextEdit": Mock,
            "QFont": Mock,
            "QIcon": Mock,
            "Qt": Mock,
        }


# Test data instance for use in tests
test_data = HubTestData()

# Mock objects for common use
mock_logger = MockLogger()
mock_config = MockConfigManager()
mock_qt_objects = MockQtObjects()


def setup_module():
    """Module-level setup for tests."""
    test_data.setup_temp_environment()


def teardown_module():
    """Module-level teardown for tests."""
    test_data.cleanup()


if __name__ == "__main__":
    # Quick test of mock objects
    print("Testing mock objects...")

    logger = MockLogger()
    logger.info("Test message")
    print(f"Logger messages: {logger.messages}")

    config = MockConfigManager()
    print(f"Config value: {config.get('gui_theme')}")

    button = MockQtObjects.create_mock_button()
    button.setText("Test Button")
    print("Mock Qt objects created successfully")

    print("Test data setup complete!")
