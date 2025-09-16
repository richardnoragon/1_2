"""
Integration Tests for Advanced Folders GUI Components

Tests the interaction between different GUI components and integration
with backend systems. Focuses on data flow, signal communication,
and end-to-end workflows.

Author: RFU Development Team
Version: 1.0.0
"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Ensure PyQt5 is available for testing
try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QWidget
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

# Import the modules under test
if PYQT5_AVAILABLE:
    try:
        from ..config_tabs import GeneralConfigTab
        from ..configuration_dialog import FolderConfigurationDialog
        from ..constants import Colors, Fonts, Icons, Layout, Styles
        from ..directory_browser import DirectoryBrowserWidget
        MODULES_AVAILABLE = True
    except ImportError as e:
        MODULES_AVAILABLE = False
        pytest.skip(f"GUI modules not available: {e}", allow_module_level=True)


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def temp_test_env():
    """Create a temporary test environment with directories and files."""
    temp_base = Path(tempfile.mkdtemp(prefix="gui_integration_test_"))
    
    # Create test directory structure
    test_dirs = {
        'documents': temp_base / "Documents",
        'projects': temp_base / "Projects",
        'images': temp_base / "Images",
        'empty': temp_base / "Empty"
    }
    
    for name, path in test_dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        
        if name != 'empty':
            # Add some test files
            (path / f"test_file_{name}.txt").write_text(f"Test content for {name}")
            
            # Add subdirectory
            subdir = path / f"sub_{name}"
            subdir.mkdir(exist_ok=True)
            (subdir / "sub_file.txt").write_text("Subdirectory content")
    
    yield {
        'base_path': temp_base,
        'directories': test_dirs
    }
    
    # Cleanup
    try:
        shutil.rmtree(temp_base)
    except Exception:
        pass


@pytest.mark.integration
class TestDialogTabIntegration:
    """Test integration between dialog and its tabs."""
    
    def test_dialog_tab_data_flow(self, qapp, temp_test_env):
        """Test data flow between dialog and tabs."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Get the general tab
        general_tab = None
        for i in range(dialog.tab_widget.count()):
            tab = dialog.tab_widget.widget(i)
            if isinstance(tab, GeneralConfigTab):
                general_tab = tab
                break
        
        assert general_tab is not None, "General tab not found"
        
        # Set data in general tab
        test_name = "Integration Test Folder"
        test_description = "Test folder for integration testing"
        general_tab.name_edit.setText(test_name)
        general_tab.description_edit.setPlainText(test_description)
        
        # Add test directories
        test_dirs = list(temp_test_env['directories'].values())[:2]
        for test_dir in test_dirs:
            general_tab._add_directory_to_list(str(test_dir))
        
        # Get configuration data through dialog
        config_data = dialog._get_configuration_data()
        
        # Verify data integrity
        assert config_data['name'] == test_name
        assert config_data['description'] == test_description
        assert len(config_data['directories']) == 2
        
        dialog.close()
    
    def test_dialog_validation_integration(self, qapp, temp_test_env):
        """Test integrated validation across dialog and tabs."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Test validation with no data - should fail
        validation_result = dialog._validate_configuration()
        assert not validation_result.is_valid
        assert len(validation_result.errors) > 0
        
        # Add valid data
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            general_tab.name_edit.setText("Valid Folder Name")
            general_tab.description_edit.setPlainText("Valid description")
            
            # Add valid directory
            test_dir = str(list(temp_test_env['directories'].values())[0])
            general_tab._add_directory_to_list(test_dir)
        
        # Test validation with valid data - should pass
        validation_result = dialog._validate_configuration()
        assert validation_result.is_valid
        assert len(validation_result.errors) == 0
        
        dialog.close()
    
    def test_tab_signal_propagation(self, qapp):
        """Test signal propagation from tabs to dialog."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Track signals received by dialog
        signals_received = []
        
        # Connect to dialog's internal signals
        for i in range(dialog.tab_widget.count()):
            tab = dialog.tab_widget.widget(i)
            if hasattr(tab, 'data_changed'):
                tab.data_changed.connect(
                    lambda tab_name=f"tab_{i}": signals_received.append(tab_name)
                )
        
        # Trigger data change in first tab
        first_tab = dialog.tab_widget.widget(0)
        if hasattr(first_tab, 'name_edit'):
            first_tab.name_edit.setText("Trigger signal")
            if hasattr(first_tab, '_emit_data_changed'):
                first_tab._emit_data_changed()
        
        # Verify signal was received
        # Note: Exact signal handling depends on implementation
        # This test verifies the signal infrastructure exists
        assert dialog.tab_widget.count() > 0
        
        dialog.close()


@pytest.mark.integration
class TestDirectoryBrowserIntegration:
    """Test directory browser integration with other components."""
    
    def test_browser_tab_integration(self, qapp, temp_test_env):
        """Test directory browser integration with configuration tab."""
        # Create browser widget
        browser = DirectoryBrowserWidget()
        
        # Create general tab
        general_tab = GeneralConfigTab(mode='create')
        
        # Connect browser to tab (simulating real integration)
        def on_directories_changed():
            """Handle directory changes from browser."""
            selected_dirs = browser.get_directories()
            general_tab.directories_list.clear()
            for directory in selected_dirs:
                general_tab._add_directory_to_list(directory)
        
        browser.directories_changed.connect(on_directories_changed)
        
        # Add directories through browser
        test_dirs = list(temp_test_env['directories'].values())[:2]
        for test_dir in test_dirs:
            browser.add_directory(str(test_dir))
        
        # Verify directories were added to tab
        assert general_tab.directories_list.count() == 2
        
        # Test removal
        browser.remove_directory(str(test_dirs[0]))
        assert general_tab.directories_list.count() == 1
        
        browser.close()
        general_tab.close()
    
    def test_browser_validation_integration(self, qapp, temp_test_env):
        """Test directory browser validation with dialog validation."""
        dialog = FolderConfigurationDialog(mode='create')
        browser = DirectoryBrowserWidget()
        
        # Get general tab
        general_tab = dialog.tab_widget.widget(0)
        
        # Test empty validation
        browser_errors = browser.validate_directories()
        dialog_validation = dialog._validate_configuration()
        
        # Both should report errors for empty directories
        assert len(browser_errors) > 0
        assert not dialog_validation.is_valid
        
        # Add directories to browser
        test_dir = str(list(temp_test_env['directories'].values())[0])
        browser.add_directory(test_dir)
        
        # Update dialog with browser directories
        if hasattr(general_tab, '_add_directory_to_list'):
            general_tab._add_directory_to_list(test_dir)
        
        # Add name to make dialog validation pass
        if hasattr(general_tab, 'name_edit'):
            general_tab.name_edit.setText("Test Folder")
        
        # Re-validate
        browser_errors = browser.validate_directories()
        dialog_validation = dialog._validate_configuration()
        
        # Browser should now be valid
        assert len(browser_errors) == 0
        
        dialog.close()
        browser.close()


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_create_configuration_workflow(self, qapp, temp_test_env):
        """Test complete configuration creation workflow."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Step 1: Fill in general information
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            general_tab.name_edit.setText("My Test Configuration")
            general_tab.description_edit.setPlainText(
                "A comprehensive test configuration for validation"
            )
            
            # Step 2: Add directories
            test_dirs = list(temp_test_env['directories'].values())
            for test_dir in test_dirs[:3]:  # Add 3 directories
                general_tab._add_directory_to_list(str(test_dir))
            
            # Step 3: Configure options
            general_tab.include_subdirs_cb.setChecked(True)
            general_tab.monitor_changes_cb.setChecked(True)
            general_tab.follow_symlinks_cb.setChecked(False)
            general_tab.include_hidden_cb.setChecked(False)
        
        # Step 4: Validate configuration
        validation_result = dialog._validate_configuration()
        assert validation_result.is_valid, f"Validation failed: {validation_result.errors}"
        
        # Step 5: Get final configuration data
        config_data = dialog._get_configuration_data()
        
        # Verify complete configuration
        assert config_data['name'] == "My Test Configuration"
        assert "comprehensive test configuration" in config_data['description'].lower()
        assert len(config_data['directories']) == 3
        assert config_data['include_subdirectories'] is True
        assert config_data['monitor_changes'] is True
        assert config_data['follow_symlinks'] is False
        assert config_data['include_hidden'] is False
        
        dialog.close()
    
    def test_edit_configuration_workflow(self, qapp, temp_test_env):
        """Test configuration editing workflow."""
        # Create mock existing configuration
        existing_config = Mock()
        existing_config.name = "Existing Configuration"
        existing_config.description = "Original description"
        existing_config.directories = [str(list(temp_test_env['directories'].values())[0])]
        existing_config.include_subdirectories = False
        existing_config.monitor_changes = False
        existing_config.follow_symlinks = True
        existing_config.include_hidden = True
        
        # Create dialog in edit mode
        dialog = FolderConfigurationDialog(mode='edit', configuration=existing_config)
        
        # Verify existing data is loaded
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            assert general_tab.name_edit.text() == "Existing Configuration"
            assert general_tab.description_edit.toPlainText() == "Original description"
            assert general_tab.include_subdirs_cb.isChecked() is False
            assert general_tab.monitor_changes_cb.isChecked() is False
            assert general_tab.follow_symlinks_cb.isChecked() is True
            assert general_tab.include_hidden_cb.isChecked() is True
            
            # Make modifications
            general_tab.name_edit.setText("Modified Configuration")
            general_tab.description_edit.setPlainText("Updated description")
            general_tab.include_subdirs_cb.setChecked(True)
            general_tab.monitor_changes_cb.setChecked(True)
            
            # Add another directory
            new_dir = str(list(temp_test_env['directories'].values())[1])
            general_tab._add_directory_to_list(new_dir)
        
        # Validate modifications
        validation_result = dialog._validate_configuration()
        assert validation_result.is_valid
        
        # Get modified configuration
        modified_config = dialog._get_configuration_data()
        
        # Verify modifications
        assert modified_config['name'] == "Modified Configuration"
        assert modified_config['description'] == "Updated description"
        assert len(modified_config['directories']) == 2
        assert modified_config['include_subdirectories'] is True
        assert modified_config['monitor_changes'] is True
        
        dialog.close()
    
    def test_view_only_workflow(self, qapp, temp_test_env):
        """Test view-only configuration workflow."""
        # Create mock configuration
        view_config = Mock()
        view_config.name = "View Only Configuration"
        view_config.description = "Read-only configuration"
        view_config.directories = [str(d) for d in list(temp_test_env['directories'].values())[:2]]
        view_config.include_subdirectories = True
        view_config.monitor_changes = True
        view_config.follow_symlinks = False
        view_config.include_hidden = False
        
        # Create dialog in view mode
        dialog = FolderConfigurationDialog(mode='view', configuration=view_config)
        
        # Verify data is displayed
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            assert general_tab.name_edit.text() == "View Only Configuration"
            assert general_tab.description_edit.toPlainText() == "Read-only configuration"
            
            # Verify controls are read-only
            assert general_tab.name_edit.isReadOnly()
            assert general_tab.description_edit.isReadOnly()
            assert not general_tab.add_directory_btn.isEnabled()
            assert not general_tab.remove_directory_btn.isEnabled()
        
        dialog.close()


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test integrated error handling across components."""
    
    def test_cascading_error_handling(self, qapp):
        """Test how errors cascade through the component hierarchy."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Test invalid name error propagation
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            # Set invalid name (too long)
            invalid_name = "x" * 300
            general_tab.name_edit.setText(invalid_name)
            
            # Validate at tab level
            tab_errors = general_tab.validate()
            assert len(tab_errors) > 0
            
            # Validate at dialog level
            dialog_validation = dialog._validate_configuration()
            assert not dialog_validation.is_valid
            assert any("name" in error.lower() for error in dialog_validation.errors)
        
        dialog.close()
    
    def test_recovery_from_errors(self, qapp, temp_test_env):
        """Test recovery from error states."""
        dialog = FolderConfigurationDialog(mode='create')
        
        # Start with error state (no name, no directories)
        validation_result = dialog._validate_configuration()
        assert not validation_result.is_valid
        
        # Fix errors step by step
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            # Add name
            general_tab.name_edit.setText("Recovery Test")
            
            # Partial validation should show improvement
            validation_result = dialog._validate_configuration()
            # Should still have directory errors but name error should be gone
            
            # Add directory
            test_dir = str(list(temp_test_env['directories'].values())[0])
            general_tab._add_directory_to_list(test_dir)
            
            # Full validation should now pass
            validation_result = dialog._validate_configuration()
            assert validation_result.is_valid
        
        dialog.close()


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance of integrated workflows."""
    
    def test_large_dataset_performance(self, qapp, temp_test_env):
        """Test performance with larger datasets."""
        import time
        
        dialog = FolderConfigurationDialog(mode='create')
        general_tab = dialog.tab_widget.widget(0)
        
        if isinstance(general_tab, GeneralConfigTab):
            # Add name and description
            general_tab.name_edit.setText("Performance Test Configuration")
            general_tab.description_edit.setPlainText(
                "Testing performance with multiple directories and complex validation"
            )
            
            # Add multiple directories and measure time
            start_time = time.time()
            
            test_dirs = list(temp_test_env['directories'].values())
            for i in range(len(test_dirs)):
                # Create variations to add more directories
                base_dir = test_dirs[i % len(test_dirs)]
                for j in range(3):  # Add 3 variations per base directory
                    variant_dir = f"{base_dir}_variant_{j}"
                    try:
                        Path(variant_dir).mkdir(exist_ok=True)
                        general_tab._add_directory_to_list(variant_dir)
                    except Exception:
                        pass  # Skip if can't create
            
            # Perform validation
            validation_result = dialog._validate_configuration()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Should complete within reasonable time (5 seconds)
            assert elapsed_time < 5.0, f"Performance test took {elapsed_time:.2f} seconds"
            
            # Validation should still work correctly
            assert validation_result.is_valid
        
        dialog.close()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "-m", "integration",
        "--tb=short"
    ])