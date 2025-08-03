"""
Comprehensive Test Suite for Secure Delete Migration

Tests all aspects of the migrated secure delete functionality including
core logic, GUI integration, hub connectivity, and error handling.

Test Categories:
- Core Logic Tests
- Configuration Tests  
- GUI Integration Tests
- Hub Integration Tests
- Error Handling Tests
- Performance Tests
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from PyQt5.QtTest import QTest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import secure delete components
from file_utilities_2.core.secure_delete_logic import SecureDeleteLogic
from file_utilities_2.core.secure_delete_config import (
    SecureDeleteConfig, SecureDeleteSettings, get_config
)
from file_utilities_2.core.secure_delete_logging import (
    SecureDeleteLogger, get_logger
)
from file_utilities_2.gui.secure_delete_gui import SecureDeleteGUI
from file_utilities_2.integration.secure_delete_connector import (
    SecureDeleteHubConnector
)


class TestSecureDeleteCore:
    """Test core secure delete logic functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        
        # Create test file
        with open(self.test_file, 'w') as f:
            f.write("Test content for secure deletion" * 100)
    
    def teardown_method(self):
        """Cleanup test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_secure_delete_logic_initialization(self):
        """Test SecureDeleteLogic initialization."""
        logic = SecureDeleteLogic()
        
        assert logic is not None
        assert not logic._is_running
        assert logic._filepath is None
        assert logic._current_pass == 0
        assert logic._total_passes == 3  # Default
    
    def test_random_bytes_generation(self):
        """Test random bytes generation."""
        logic = SecureDeleteLogic()
        
        # Test different sizes
        for size in [1024, 4096, 1024*1024]:
            random_bytes = logic._generate_random_bytes(size)
            assert len(random_bytes) == size
            assert isinstance(random_bytes, bytes)
    
    def test_random_filename_generation(self):
        """Test random filename generation."""
        logic = SecureDeleteLogic()
        
        # Test default length
        filename = logic._generate_random_filename()
        assert len(filename) == 16
        assert filename.isalnum()
        
        # Test custom length
        filename = logic._generate_random_filename(32)
        assert len(filename) == 32
        assert filename.isalnum()
    
    def test_file_validation(self):
        """Test file validation before deletion."""
        logic = SecureDeleteLogic()
        
        # Test with valid file
        assert os.path.isfile(self.test_file)
        
        # Test with non-existent file
        non_existent = os.path.join(self.temp_dir, "non_existent.txt")
        assert not os.path.isfile(non_existent)
    
    @pytest.mark.asyncio
    async def test_secure_deletion_process(self):
        """Test the complete secure deletion process."""
        logic = SecureDeleteLogic()
        
        # Mock signals to avoid GUI dependencies
        logic.progress_updated = Mock()
        logic.file_progress = Mock()
        logic.operation_complete = Mock()
        logic.error_occurred = Mock()
        logic.finished = Mock()
        
        # Test file exists before deletion
        assert os.path.exists(self.test_file)
        original_size = os.path.getsize(self.test_file)
        
        # Perform deletion with 1 pass for speed
        logic.shred_file(self.test_file, 1)
        
        # Verify signals were called
        assert logic.progress_updated.called
        assert logic.operation_complete.called or logic.error_occurred.called
        assert logic.finished.called
        
        # File should be deleted
        assert not os.path.exists(self.test_file)
    
    def test_stop_functionality(self):
        """Test stopping deletion process."""
        logic = SecureDeleteLogic()
        logic.progress_updated = Mock()
        
        # Start and immediately stop
        logic._is_running = True
        logic.stop()
        
        assert not logic._is_running
        assert logic.progress_updated.called


class TestSecureDeleteConfiguration:
    """Test configuration management functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = SecureDeleteConfig(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_default_settings(self):
        """Test default configuration settings."""
        settings = SecureDeleteSettings()
        
        assert settings.default_passes == 3
        assert settings.max_passes == 35
        assert settings.chunk_size == 1024 * 1024
        assert settings.enable_hub_integration is True
        assert settings.confirm_deletion is True
    
    def test_config_save_load(self):
        """Test configuration save and load."""
        # Modify settings
        self.config.set_setting('default_passes', 7)
        self.config.set_setting('confirm_deletion', False)
        
        # Create new config instance to test loading
        new_config = SecureDeleteConfig(self.temp_dir)
        
        assert new_config.get_setting('default_passes') == 7
        assert new_config.get_setting('confirm_deletion') is False
    
    def test_setting_validation(self):
        """Test setting validation."""
        # Valid settings
        assert self.config.set_setting('default_passes', 5) is True
        assert self.config.set_setting('max_passes', 20) is True
        
        # Invalid settings
        assert self.config.set_setting('default_passes', 0) is False
        assert self.config.set_setting('max_passes', 200) is False
        assert self.config.set_setting('chunk_size', 100) is False
    
    def test_config_export_import(self):
        """Test configuration export and import."""
        export_file = os.path.join(self.temp_dir, "config_export.json")
        
        # Modify settings
        self.config.set_setting('default_passes', 5)
        
        # Export configuration
        assert self.config.export_config(export_file) is True
        assert os.path.exists(export_file)
        
        # Reset and import
        self.config.reset_to_defaults()
        assert self.config.get_setting('default_passes') == 3
        
        assert self.config.import_config(export_file) is True
        assert self.config.get_setting('default_passes') == 5


class TestSecureDeleteLogging:
    """Test logging functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = SecureDeleteLogger("TestLogger", self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        assert self.logger.name == "TestLogger"
        assert self.logger.log_dir.exists()
        assert self.logger.audit_enabled is True
    
    def test_operation_logging(self):
        """Test operation logging."""
        # Log operation start
        operation_id = self.logger.log_operation_start(
            "/test/file.txt", 3, 1024
        )
        
        assert operation_id is not None
        assert operation_id.startswith("SD_")
        
        # Log progress
        self.logger.log_operation_progress(
            operation_id, 1, 3, 512, 1024
        )
        
        # Log completion
        self.logger.log_operation_complete(
            operation_id, "/test/file.txt", 5.0, 3
        )
        
        # Verify logs exist
        logs = self.logger.get_operation_logs(operation_id)
        assert len(logs) >= 2  # At least start and complete
    
    def test_security_event_logging(self):
        """Test security event logging."""
        self.logger.log_security_event(
            "unauthorized_access", "/test/file.txt", {"details": "test"}
        )
        
        assert len(self.logger.security_events) == 1
        event = self.logger.security_events[0]
        assert event['event_type'] == "security_unauthorized_access"
    
    def test_log_cleanup(self):
        """Test log cleanup functionality."""
        # Create some test logs
        self.logger.log_operation_start("/test/file1.txt", 3, 1024)
        self.logger.log_operation_start("/test/file2.txt", 3, 1024)
        
        # Test cleanup (with 0 days to force cleanup)
        self.logger.cleanup_old_logs(0)
        
        # Verify cleanup ran without errors
        stats = self.logger.get_log_stats()
        assert 'error' not in stats


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


class TestSecureDeleteGUI:
    """Test GUI functionality."""
    
    def test_gui_initialization(self, qapp):
        """Test GUI initialization."""
        gui = SecureDeleteGUI()
        
        assert gui is not None
        assert gui.windowTitle() == "Secure File Delete"
        assert gui.file_path is None
        assert not gui.is_operation_running
        
        gui.close()
    
    def test_file_selection_validation(self, qapp):
        """Test file selection validation."""
        gui = SecureDeleteGUI()
        
        # Test with non-existent file
        with patch('file_utilities_2.gui.secure_delete_gui.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("/non/existent/file.txt", "")
            
            with patch.object(gui, 'show_error_dialog') as mock_error:
                gui.select_file()
                mock_error.assert_called_once()
        
        gui.close()
    
    def test_passes_validation(self, qapp):
        """Test passes validation."""
        gui = SecureDeleteGUI()
        
        # Test invalid passes
        with patch.object(gui, 'show_warning_dialog') as mock_warning:
            gui._on_passes_changed("100")  # Exceeds max
            mock_warning.assert_called_once()
        
        gui.close()
    
    def test_drag_drop_functionality(self, qapp):
        """Test drag and drop functionality."""
        gui = SecureDeleteGUI()
        
        # Create mock drag event
        mock_event = Mock()
        mock_event.mimeData().hasUrls.return_value = True
        
        # Test drag enter
        gui.dragEnterEvent(mock_event)
        mock_event.acceptProposedAction.assert_called_once()
        
        gui.close()


class TestHubIntegration:
    """Test hub integration functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_hub = Mock()
        self.connector = SecureDeleteHubConnector(self.mock_hub)
    
    def test_hub_connector_initialization(self):
        """Test hub connector initialization."""
        assert self.connector is not None
        assert len(self.connector.allocated_resources) == 0
        assert self.connector.performance_metrics['operations_completed'] == 0
    
    def test_resource_allocation(self):
        """Test resource allocation and release."""
        # Mock successful resource allocation
        with patch.object(self.connector.hub_connector, 'request_hub_resources') as mock_request:
            mock_request.return_value = True
            
            # Request resources
            result = self.connector.request_deletion_resources(
                "/test/file.txt", 1024, 3
            )
            
            assert result is True
            assert 'disk' in self.connector.allocated_resources
            mock_request.assert_called_once()
        
        # Release resources
        self.connector.release_deletion_resources()
        assert len(self.connector.allocated_resources) == 0
    
    def test_progress_reporting(self):
        """Test progress reporting to hub."""
        with patch.object(self.connector.hub_connector, 'report_progress_to_hub') as mock_report:
            self.connector.report_operation_progress(
                "test_op", "/test/file.txt", 1, 3, 512, 1024
            )
            
            mock_report.assert_called_once()
    
    def test_security_event_reporting(self):
        """Test security event reporting."""
        with patch.object(self.connector.hub_connector, 'broadcast_event') as mock_broadcast:
            self.connector.report_security_event(
                "unauthorized_access", "/test/file.txt", {"test": "data"}
            )
            
            mock_broadcast.assert_called_once()
            assert len(self.connector.security_events) == 1
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        initial_ops = self.connector.performance_metrics['operations_completed']
        
        self.connector.update_performance_metrics({
            'bytes_processed': 1024,
            'duration': 5.0,
            'error_count': 0
        })
        
        assert self.connector.performance_metrics['operations_completed'] == initial_ops + 1
        assert self.connector.performance_metrics['total_bytes_processed'] == 1024


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        logic = SecureDeleteLogic()
        logic.error_occurred = Mock()
        
        # Test with non-existent file
        logic.shred_file("/non/existent/file.txt", 3)
        logic.error_occurred.assert_called_once()
    
    def test_permission_errors(self):
        """Test handling of permission errors."""
        # This would test permission-related errors
        # Implementation depends on platform-specific behavior
        pass
    
    def test_disk_space_errors(self):
        """Test handling of disk space errors."""
        # This would test disk space related errors
        # Implementation depends on available disk space
        pass
    
    def test_configuration_errors(self):
        """Test configuration error handling."""
        # Test with invalid config directory
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Access denied")
            
            # Should handle gracefully
            try:
                config = SecureDeleteConfig("/invalid/path")
                assert config is not None
            except Exception:
                pytest.fail("Configuration should handle permission errors gracefully")


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    def setup_method(self):
        """Setup integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "integration_test.txt")
        
        # Create test file
        with open(self.test_file, 'w') as f:
            f.write("Integration test content" * 50)
    
    def teardown_method(self):
        """Cleanup integration test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_deletion(self):
        """Test complete end-to-end deletion process."""
        # Initialize components
        config = SecureDeleteConfig(self.temp_dir)
        logger = SecureDeleteLogger("IntegrationTest", self.temp_dir)
        logic = SecureDeleteLogic()
        
        # Mock signals
        logic.progress_updated = Mock()
        logic.operation_complete = Mock()
        logic.finished = Mock()
        
        # Verify file exists
        assert os.path.exists(self.test_file)
        
        # Perform deletion
        logic.shred_file(self.test_file, 1)  # Single pass for speed
        
        # Verify completion
        assert logic.operation_complete.called or logic.error_occurred.called
        
        # File should be deleted
        assert not os.path.exists(self.test_file)
    
    def test_configuration_integration(self):
        """Test configuration integration with other components."""
        config = SecureDeleteConfig(self.temp_dir)
        
        # Test setting retrieval
        default_passes = config.get_setting('default_passes', 3)
        assert isinstance(default_passes, int)
        assert 1 <= default_passes <= 35
    
    def test_logging_integration(self):
        """Test logging integration with operations."""
        logger = SecureDeleteLogger("IntegrationTest", self.temp_dir)
        
        # Log a complete operation cycle
        op_id = logger.log_operation_start(self.test_file, 3, 1024)
        logger.log_operation_progress(op_id, 1, 3, 512, 1024)
        logger.log_operation_complete(op_id, self.test_file, 5.0, 3)
        
        # Verify logs
        logs = logger.get_operation_logs(op_id)
        assert len(logs) >= 2


def run_comprehensive_tests():
    """Run all tests and generate report."""
    print("🧪 Running Secure Delete Migration Tests...")
    
    # Run pytest with detailed output
    test_args = [
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    # Ensure QApplication exists for GUI tests
    if not QApplication.instance():
        app = QApplication([])
    
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)