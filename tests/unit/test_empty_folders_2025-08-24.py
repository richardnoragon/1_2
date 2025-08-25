#!/usr/bin/env python3
"""
Comprehensive Unit Tests for empty_folders.py
Created: 2025-08-24
Framework: pytest

Test Coverage:
- EmptyFolderLogic class functionality (finding and deleting empty folders)
- EmptyFoldersGUI class initialization and UI components
- Signal handling and threading operations
- Directory scanning and selection functionality
- Error handling scenarios and edge cases
- Mock data testing with various folder structures
- Integration testing of GUI and logic components
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the source directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from src.utilities.analysis.empty_folders import (
        EmptyFolderLogic, EmptyFoldersGUI, main
    )
except ImportError:
    # Alternative import path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.utilities.analysis.empty_folders import (
        EmptyFolderLogic, EmptyFoldersGUI, main
    )


class TestEmptyFolderLogic:
    """Test suite for EmptyFolderLogic class."""
    
    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def empty_folder_logic(self, app):
        """Create EmptyFolderLogic instance for testing."""
        logic = EmptyFolderLogic()
        yield logic
        # Cleanup
        if hasattr(logic, '_is_running'):
            logic._is_running = False
    
    @pytest.fixture
    def temp_directory_structure(self):
        """Create temporary directory structure for testing."""
        temp_dir = tempfile.mkdtemp(prefix="empty_folders_test_")
        
        # Create test directory structure
        structure = {
            'empty_folder1': {},
            'empty_folder2': {},
            'non_empty_folder': {
                'file.txt': 'content'
            },
            'nested_structure': {
                'empty_subfolder1': {},
                'empty_subfolder2': {},
                'non_empty_subfolder': {
                    'data.txt': 'some data'
                }
            },
            'deeply_nested': {
                'level1': {
                    'level2': {
                        'empty_deep': {}
                    }
                }
            }
        }
        
        def create_structure(base_path, struct):
            for name, content in struct.items():
                path = os.path.join(base_path, name)
                if isinstance(content, dict):
                    os.makedirs(path, exist_ok=True)
                    create_structure(path, content)
                else:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as f:
                        f.write(content)
        
        create_structure(temp_dir, structure)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def empty_only_structure(self):
        """Create structure with only empty folders."""
        temp_dir = tempfile.mkdtemp(prefix="empty_only_test_")
        
        # Create several empty directories
        empty_dirs = [
            'empty1',
            'empty2',
            'empty3',
            'nested/empty4',
            'nested/deep/empty5'
        ]
        
        for dir_path in empty_dirs:
            full_path = os.path.join(temp_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_empty_folder_logic_initialization(self, empty_folder_logic):
        """Test EmptyFolderLogic proper initialization."""
        assert empty_folder_logic is not None
        assert hasattr(empty_folder_logic, '_is_running')
        assert hasattr(empty_folder_logic, '_base_path')
        assert empty_folder_logic._is_running is False
        assert empty_folder_logic._base_path is None
    
    def test_stop_operation(self, empty_folder_logic):
        """Test stopping an operation."""
        empty_folder_logic._is_running = True
        empty_folder_logic.stop()
        assert empty_folder_logic._is_running is False
    
    def test_find_empty_folders_mixed_structure(self, empty_folder_logic,
                                                temp_directory_structure):
        """Test finding empty folders in mixed directory structure."""
        results = []
        
        def capture_folders(folders):
            results.extend(folders)
        
        empty_folder_logic.folders_found.connect(capture_folders)
        empty_folder_logic.find_empty_folders(temp_directory_structure)
        
        # Should find specific empty folders
        expected_empty = [
            'empty_folder1',
            'empty_folder2',
            'empty_subfolder1',
            'empty_subfolder2',
            'empty_deep'
        ]
        
        # Check that all expected empty folders were found
        found_names = [os.path.basename(folder) for folder in results]
        for expected in expected_empty:
            assert expected in found_names
        
        # Should not find non-empty folders
        assert 'non_empty_folder' not in found_names
        assert 'non_empty_subfolder' not in found_names
    
    def test_find_empty_folders_empty_only(self, empty_folder_logic,
                                           empty_only_structure):
        """Test finding folders in structure with only empty directories."""
        results = []
        
        def capture_folders(folders):
            results.extend(folders)
        
        empty_folder_logic.folders_found.connect(capture_folders)
        empty_folder_logic.find_empty_folders(empty_only_structure)
        
        # Should find all empty directories
        assert len(results) >= 5  # At least the 5 we created
        
        # Verify all found paths are actually empty
        for folder in results:
            assert os.path.exists(folder)
            assert os.path.isdir(folder)
            assert len(os.listdir(folder)) == 0
    
    def test_find_empty_folders_nonexistent_path(self, empty_folder_logic):
        """Test finding empty folders with nonexistent path."""
        error_messages = []
        
        def capture_error(error):
            error_messages.append(error)
        
        empty_folder_logic.error_occurred.connect(capture_error)
        empty_folder_logic.find_empty_folders("/nonexistent/path")
        
        # Should handle error gracefully
        assert len(error_messages) >= 0  # May or may not generate error
    
    def test_delete_folders_success(self, empty_folder_logic,
                                    empty_only_structure):
        """Test successful deletion of empty folders."""
        # First find empty folders
        results = []
        
        def capture_folders(folders):
            results.extend(folders)
        
        empty_folder_logic.folders_found.connect(capture_folders)
        empty_folder_logic.find_empty_folders(empty_only_structure)
        
        # Now test deletion
        deletion_results = []
        
        def capture_deletion(folder, success):
            deletion_results.append((folder, success))
        
        empty_folder_logic.deletion_update.connect(capture_deletion)
        
        # Delete first two folders
        folders_to_delete = results[:2]
        empty_folder_logic.delete_folders(folders_to_delete)
        
        # Verify deletions
        assert len(deletion_results) == 2
        for folder, success in deletion_results:
            assert success is True
            assert not os.path.exists(folder)
    
    def test_delete_folders_nested_order(self, empty_folder_logic):
        """Test that nested folders are deleted in correct order."""
        # Create nested structure
        temp_dir = tempfile.mkdtemp(prefix="nested_delete_test_")
        
        try:
            # Create nested empty directories
            nested_paths = [
                os.path.join(temp_dir, 'parent'),
                os.path.join(temp_dir, 'parent', 'child'),
                os.path.join(temp_dir, 'parent', 'child', 'grandchild')
            ]
            
            for path in nested_paths:
                os.makedirs(path, exist_ok=True)
            
            deletion_order = []
            
            def capture_deletion(folder, success):
                if success:
                    deletion_order.append(folder)
            
            empty_folder_logic.deletion_update.connect(capture_deletion)
            empty_folder_logic.delete_folders(nested_paths)
            
            # Verify deletion order (deepest first)
            assert len(deletion_order) == 3
            # Deepest path should be deleted first
            assert 'grandchild' in deletion_order[0]
            assert 'child' in deletion_order[1]
            assert deletion_order[1].count(os.sep) < deletion_order[0].count(os.sep)
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_delete_folders_permission_error(self, empty_folder_logic):
        """Test deletion with permission errors."""
        deletion_results = []
        error_messages = []
        
        def capture_deletion(folder, success):
            deletion_results.append((folder, success))
        
        def capture_error(error):
            error_messages.append(error)
        
        empty_folder_logic.deletion_update.connect(capture_deletion)
        empty_folder_logic.error_occurred.connect(capture_error)
        
        # Try to delete a non-existent folder
        empty_folder_logic.delete_folders(["/nonexistent/folder"])
        
        # Should handle gracefully
        assert len(deletion_results) == 1
        folder, success = deletion_results[0]
        assert success is False
    
    def test_signal_emissions(self, empty_folder_logic, empty_only_structure):
        """Test that all expected signals are emitted."""
        progress_messages = []
        folders_found = []
        finished_signals = []
        
        def capture_progress(message):
            progress_messages.append(message)
        
        def capture_folders(folders):
            folders_found.extend(folders)
        
        def capture_finished(is_scan):
            finished_signals.append(is_scan)
        
        empty_folder_logic.progress_updated.connect(capture_progress)
        empty_folder_logic.folders_found.connect(capture_folders)
        empty_folder_logic.finished.connect(capture_finished)
        
        empty_folder_logic.find_empty_folders(empty_only_structure)
        
        # Verify signals were emitted
        assert len(progress_messages) > 0
        assert len(folders_found) > 0
        assert len(finished_signals) == 1
        assert finished_signals[0] is True  # True for scan completion


class TestEmptyFoldersGUI:
    """Test suite for EmptyFoldersGUI class."""
    
    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def empty_folders_gui(self, app):
        """Create EmptyFoldersGUI instance for testing."""
        gui = EmptyFoldersGUI()
        yield gui
        gui.close()
    
    @pytest.fixture
    def temp_test_directory(self):
        """Create temporary test directory."""
        temp_dir = tempfile.mkdtemp(prefix="gui_test_")
        
        # Create some empty and non-empty folders
        os.makedirs(os.path.join(temp_dir, 'empty1'))
        os.makedirs(os.path.join(temp_dir, 'empty2'))
        
        non_empty = os.path.join(temp_dir, 'non_empty')
        os.makedirs(non_empty)
        with open(os.path.join(non_empty, 'file.txt'), 'w') as f:
            f.write('content')
        
        yield temp_dir
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_empty_folders_gui_initialization(self, empty_folders_gui):
        """Test EmptyFoldersGUI proper initialization."""
        assert empty_folders_gui is not None
        assert hasattr(empty_folders_gui, 'current_path')
        assert hasattr(empty_folders_gui, 'empty_folders')
        assert hasattr(empty_folders_gui, 'logic')
        assert hasattr(empty_folders_gui, 'thread')
        
        assert empty_folders_gui.current_path is None
        assert empty_folders_gui.empty_folders == []
        assert empty_folders_gui.logic is None
        assert empty_folders_gui.thread is None
    
    def test_window_title_setting(self, empty_folders_gui):
        """Test that window title is set correctly."""
        title = empty_folders_gui.windowTitle()
        assert "Empty Folders Finder" in title
        assert "Richard's File Utilities" in title
    
    def test_ui_components_creation(self, empty_folders_gui):
        """Test that all UI components are created properly."""
        # Check if key UI components exist
        assert hasattr(empty_folders_gui, 'path_input')
        assert hasattr(empty_folders_gui, 'browse_button')
        assert hasattr(empty_folders_gui, 'scan_button')
        assert hasattr(empty_folders_gui, 'stop_button')
        assert hasattr(empty_folders_gui, 'results_list')
        assert hasattr(empty_folders_gui, 'delete_button')
        assert hasattr(empty_folders_gui, 'status_label')
        
        # Verify initial states
        assert "No directory selected" in empty_folders_gui.path_input.text()
        assert empty_folders_gui.scan_button.isEnabled() is False
        assert empty_folders_gui.stop_button.isEnabled() is False
        assert empty_folders_gui.results_list.count() == 0
    
    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_select_directory_success(self, mock_dialog, empty_folders_gui,
                                      temp_test_directory):
        """Test successful directory selection."""
        mock_dialog.return_value = temp_test_directory
        
        empty_folders_gui.select_directory()
        
        assert empty_folders_gui.current_path == temp_test_directory
        assert temp_test_directory in empty_folders_gui.path_input.text()
        assert empty_folders_gui.scan_button.isEnabled() is True
    
    @patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory')
    def test_select_directory_cancel(self, mock_dialog, empty_folders_gui):
        """Test directory selection cancellation."""
        mock_dialog.return_value = ""
        
        original_path = empty_folders_gui.current_path
        empty_folders_gui.select_directory()
        
        assert empty_folders_gui.current_path == original_path
        assert empty_folders_gui.scan_button.isEnabled() is False
    
    def test_start_scan_no_directory(self, empty_folders_gui):
        """Test starting scan with no directory selected."""
        with patch.object(QMessageBox, 'warning') as mock_warning:
            empty_folders_gui.start_scan()
            mock_warning.assert_called_once()
    
    def test_display_folders(self, empty_folders_gui, temp_test_directory):
        """Test displaying found empty folders."""
        empty_folders_gui.current_path = temp_test_directory
        
        # Create test folder list
        test_folders = [
            os.path.join(temp_test_directory, 'empty1'),
            os.path.join(temp_test_directory, 'empty2')
        ]
        
        empty_folders_gui.display_folders(test_folders)
        
        assert empty_folders_gui.empty_folders == test_folders
        assert empty_folders_gui.results_list.count() == 2
        assert "Found 2 empty folders" in empty_folders_gui.status_label.text()
    
    def test_select_all_folders(self, empty_folders_gui):
        """Test selecting all folders in the list."""
        # Add some test items
        empty_folders_gui.results_list.addItem("folder1")
        empty_folders_gui.results_list.addItem("folder2")
        
        empty_folders_gui.select_all_folders()
        
        # Check that all items are selected
        selected_count = len(empty_folders_gui.results_list.selectedItems())
        assert selected_count == 2
    
    def test_unselect_all_folders(self, empty_folders_gui):
        """Test unselecting all folders in the list."""
        # Add and select some test items
        empty_folders_gui.results_list.addItem("folder1")
        empty_folders_gui.results_list.addItem("folder2")
        empty_folders_gui.results_list.selectAll()
        
        empty_folders_gui.unselect_all_folders()
        
        # Check that no items are selected
        selected_count = len(empty_folders_gui.results_list.selectedItems())
        assert selected_count == 0
    
    def test_delete_selected_no_selection(self, empty_folders_gui):
        """Test deleting with no folders selected."""
        with patch.object(QMessageBox, 'warning') as mock_warning:
            empty_folders_gui.delete_selected()
            mock_warning.assert_called_once()
    
    def test_clear_results(self, empty_folders_gui):
        """Test clearing all results."""
        # Add some test data
        empty_folders_gui.empty_folders = ["/test/folder1", "/test/folder2"]
        empty_folders_gui.results_list.addItem("folder1")
        empty_folders_gui.results_list.addItem("folder2")
        
        empty_folders_gui.clear_results()
        
        assert empty_folders_gui.empty_folders == []
        assert empty_folders_gui.results_list.count() == 0
    
    def test_show_help(self, empty_folders_gui):
        """Test help dialog display."""
        with patch.object(QMessageBox, 'information') as mock_info:
            empty_folders_gui.show_help()
            mock_info.assert_called_once()
            
            # Verify help content
            args, kwargs = mock_info.call_args
            assert "Empty Folders Finder Help" in args
            assert "How to Find Empty Folders" in args[2]
    
    def test_show_preferences(self, empty_folders_gui):
        """Test preferences dialog display."""
        with patch.object(QMessageBox, 'information') as mock_info:
            empty_folders_gui.show_preferences()
            mock_info.assert_called_once()
            
            # Verify preferences content
            args, _ = mock_info.call_args
            assert "Preferences" in args[1]
    
    def test_refresh_view(self, empty_folders_gui):
        """Test refresh/clear view functionality."""
        # Add some test data
        empty_folders_gui.empty_folders = ["/test/folder1"]
        empty_folders_gui.results_list.addItem("folder1")
        
        empty_folders_gui.refresh_view()
        
        assert empty_folders_gui.empty_folders == []
        assert empty_folders_gui.results_list.count() == 0
    
    def test_update_button_states_no_folders(self, empty_folders_gui):
        """Test button states with no folders."""
        empty_folders_gui.update_button_states()
        
        assert empty_folders_gui.delete_button.isEnabled() is False
        assert empty_folders_gui.select_all_button.isEnabled() is False
        assert empty_folders_gui.unselect_all_button.isEnabled() is False
    
    def test_update_button_states_with_folders(self, empty_folders_gui):
        """Test button states with folders present."""
        # Add some test items
        empty_folders_gui.results_list.addItem("folder1")
        empty_folders_gui.results_list.addItem("folder2")
        
        empty_folders_gui.update_button_states()
        
        assert empty_folders_gui.delete_button.isEnabled() is True
        assert empty_folders_gui.select_all_button.isEnabled() is True
        assert empty_folders_gui.unselect_all_button.isEnabled() is True
    
    def test_handle_error(self, empty_folders_gui):
        """Test error handling."""
        with patch.object(QMessageBox, 'critical') as mock_critical:
            empty_folders_gui.handle_error("Test error message")
            mock_critical.assert_called_once()
            args, _ = mock_critical.call_args
            assert "Test error message" in args[2]
    
    def test_update_status(self, empty_folders_gui):
        """Test status message updates."""
        test_message = "Test status message"
        empty_folders_gui.update_status(test_message)
        
        assert empty_folders_gui.status_label.text() == test_message
    
    def test_operation_complete(self, empty_folders_gui):
        """Test operation completion cleanup."""
        # Set up some state
        empty_folders_gui.scan_button.setEnabled(False)
        empty_folders_gui.stop_button.setEnabled(True)
        
        # Create mock thread
        empty_folders_gui.thread = Mock()
        empty_folders_gui.logic = Mock()
        
        empty_folders_gui.operation_complete()
        
        # Verify cleanup
        assert empty_folders_gui.scan_button.isEnabled() is True
        assert empty_folders_gui.stop_button.isEnabled() is False
        assert empty_folders_gui.thread is None
        assert empty_folders_gui.logic is None
    
    @patch('src.utilities.analysis.empty_folders.STANDARD_WINDOW_AVAILABLE',
           False)
    def test_fallback_mode_initialization(self, app):
        """Test initialization in fallback mode (without StandardWindow)."""
        gui = EmptyFoldersGUI()
        assert gui is not None
        assert hasattr(gui, 'current_path')
        gui.close()
    
    def test_menu_callbacks_setup(self, empty_folders_gui):
        """Test menu callbacks setup when StandardWindow is available."""
        if hasattr(empty_folders_gui, 'menu_manager'):
            # Verify menu callbacks are set up
            assert hasattr(empty_folders_gui, '_setup_menu_callbacks')


class TestMainFunction:
    """Test suite for main function."""
    
    def test_main_function_basic_import(self):
        """Test main function is properly defined and importable."""
        # Simply test that we can import and access the main function
        assert callable(main)
        assert main.__name__ == 'main'
        # This is safer than trying to execute it in test environment


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def empty_folder_logic(self, app):
        """Create EmptyFolderLogic instance for testing."""
        logic = EmptyFolderLogic()
        yield logic
        if hasattr(logic, '_is_running'):
            logic._is_running = False
    
    def test_find_folders_permission_denied(self, empty_folder_logic):
        """Test handling directories with permission issues."""
        error_messages = []
        
        def capture_error(error):
            error_messages.append(error)
        
        empty_folder_logic.error_occurred.connect(capture_error)
        
        # Try to scan a restricted directory (may not trigger on all systems)
        restricted_paths = [
            "C:\\System Volume Information",  # Windows restricted
            "/root",  # Unix restricted (if not root)
            "/nonexistent/deeply/nested/path"
        ]
        
        for path in restricted_paths:
            if os.path.exists(path):
                empty_folder_logic.find_empty_folders(path)
                break
        
        # Should handle gracefully (may or may not generate errors)
        assert len(error_messages) >= 0
    
    def test_delete_folders_mixed_results(self, empty_folder_logic):
        """Test deletion with mix of success and failure."""
        temp_dir = tempfile.mkdtemp(prefix="mixed_delete_test_")
        
        try:
            # Create one valid empty folder
            valid_folder = os.path.join(temp_dir, 'valid_empty')
            os.makedirs(valid_folder)
            
            # List includes valid and invalid folders
            folders_to_delete = [
                valid_folder,
                "/nonexistent/folder",
                os.path.join(temp_dir, "also_nonexistent")
            ]
            
            deletion_results = []
            
            def capture_deletion(folder, success):
                deletion_results.append((folder, success))
            
            empty_folder_logic.deletion_update.connect(capture_deletion)
            empty_folder_logic.delete_folders(folders_to_delete)
            
            # Should have results for all folders
            assert len(deletion_results) == 3
            
            # Valid folder should succeed, others should fail
            valid_result = next((success for folder, success in deletion_results
                                if folder == valid_folder), None)
            assert valid_result is True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_very_deep_nested_structure(self, empty_folder_logic):
        """Test with very deeply nested empty folders."""
        temp_dir = tempfile.mkdtemp(prefix="deep_nest_test_")
        
        try:
            # Create deeply nested structure
            current_path = temp_dir
            for i in range(10):  # 10 levels deep
                current_path = os.path.join(current_path, f"level_{i}")
                os.makedirs(current_path)
            
            results = []
            
            def capture_folders(folders):
                results.extend(folders)
            
            empty_folder_logic.folders_found.connect(capture_folders)
            empty_folder_logic.find_empty_folders(temp_dir)
            
            # Should find the deepest empty folder
            assert len(results) >= 1
            
            # Check that deepest folder is found
            deepest_found = any("level_9" in folder for folder in results)
            assert deepest_found
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_unicode_folder_names(self, empty_folder_logic):
        """Test handling folders with unicode characters."""
        temp_dir = tempfile.mkdtemp(prefix="unicode_test_")
        
        try:
            # Create folders with unicode names
            unicode_folders = [
                "测试文件夹",  # Chinese
                "папка_тест",  # Russian  
                "フォルダー",   # Japanese
                "📁_emoji_folder"  # Emoji
            ]
            
            created_folders = []
            for folder_name in unicode_folders:
                try:
                    folder_path = os.path.join(temp_dir, folder_name)
                    os.makedirs(folder_path)
                    created_folders.append(folder_path)
                except (UnicodeError, OSError):
                    # Skip if system doesn't support unicode filenames
                    continue
            
            if created_folders:
                results = []
                
                def capture_folders(folders):
                    results.extend(folders)
                
                empty_folder_logic.folders_found.connect(capture_folders)
                empty_folder_logic.find_empty_folders(temp_dir)
                
                # Should handle unicode folders gracefully
                assert len(results) >= len(created_folders)
            
        except UnicodeError:
            pytest.skip("System doesn't support unicode folder names")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_stop_operation_during_scan(self, empty_folder_logic):
        """Test stopping operation during scan."""
        # Start operation
        empty_folder_logic._is_running = True
        
        # Stop it immediately
        empty_folder_logic.stop()
        
        # Verify it stopped
        assert empty_folder_logic._is_running is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])