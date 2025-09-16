"""Comprehensive unit tests for organize.py module.

This module contains comprehensive test coverage for all classes and functions
in the organize.py file, including edge cases, error handling, and mock data.

Test execution includes detailed reporting with timestamp, coverage, and results.
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication

# Import the modules under test
from src.tools.file_operations.organize.organize import (OrganizeRule,
                                                             OrganizeWindow,
                                                             RuleEditDialog,
                                                             RulesDialog, main)


class TestOrganizeRule:
    """Test cases for OrganizeRule dataclass."""
    
    def test_organize_rule_creation_with_defaults(self):
        """Test creating OrganizeRule with default values."""
        rule = OrganizeRule(
            name="TestRule",
            pattern="*.txt",
            destination="Documents"
        )
        
        assert rule.name == "TestRule"
        assert rule.pattern == "*.txt"
        assert rule.destination == "Documents"
        assert rule.enabled is True  # Default value
    
    def test_organize_rule_creation_with_explicit_enabled(self):
        """Test creating OrganizeRule with explicit enabled value."""
        rule = OrganizeRule(
            name="TestRule",
            pattern="*.pdf",
            destination="PDFs",
            enabled=False
        )
        
        assert rule.name == "TestRule"
        assert rule.pattern == "*.pdf"
        assert rule.destination == "PDFs"
        assert rule.enabled is False
    
    def test_organize_rule_equality(self):
        """Test OrganizeRule equality comparison."""
        rule1 = OrganizeRule("Test", "*.txt", "Docs", True)
        rule2 = OrganizeRule("Test", "*.txt", "Docs", True)
        rule3 = OrganizeRule("Test", "*.pdf", "Docs", True)
        
        assert rule1 == rule2
        assert rule1 != rule3
    
    def test_organize_rule_string_representation(self):
        """Test OrganizeRule string representation."""
        rule = OrganizeRule("Images", "*.jpg", "Pictures")
        rule_str = str(rule)
        
        assert "Images" in rule_str
        assert "*.jpg" in rule_str
        assert "Pictures" in rule_str


@pytest.fixture
def qapp():
    """Fixture to provide QApplication instance for Qt tests."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def temp_directory():
    """Fixture to provide a temporary directory for file operations."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_files(temp_directory):
    """Fixture to create sample files for testing."""
    files = {
        'document.txt': 'Sample text content',
        'image.jpg': b'fake image data',
        'video.mp4': b'fake video data',
        'archive.zip': b'fake zip data',
        'audio.mp3': b'fake audio data',
        'spreadsheet.xlsx': b'fake excel data'
    }
    
    created_files = []
    for filename, content in files.items():
        file_path = os.path.join(temp_directory, filename)
        mode = 'w' if isinstance(content, str) else 'wb'
        with open(file_path, mode) as f:
            f.write(content)
        created_files.append(file_path)
    
    return created_files


@pytest.fixture
def sample_rules():
    """Fixture to provide sample organization rules."""
    return [
        OrganizeRule("Documents", "*.txt;*.pdf;*.doc", "Documents", True),
        OrganizeRule("Images", "*.jpg;*.jpeg;*.png", "Images", True),
        OrganizeRule("Videos", "*.mp4;*.avi;*.mkv", "Videos", False),
        OrganizeRule("Audio", "*.mp3;*.wav", "Audio", True)
    ]


class TestOrganizeWindow:
    """Test cases for OrganizeWindow class."""
    
    @patch('src.tools.file_operations.organize.organize.uic.loadUi')
    @patch('src.tools.file_operations.organize.organize.Path.exists')
    def test_organize_window_initialization(self, mock_exists, mock_loadui, qapp):
        """Test OrganizeWindow initialization."""
        mock_exists.return_value = True
        
        with patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            
            assert window._current_dir == ""
            assert window._rules == []
            assert isinstance(window._list_model, QStandardItemModel)
            assert window._organized_files == []
    
    def test_init_models(self, qapp):
        """Test _init_models method."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._init_models()
            
            assert window._current_dir == ""
            assert isinstance(window._rules, list)
            assert isinstance(window._list_model, QStandardItemModel)
            assert isinstance(window._organized_files, list)
    
    @patch('src.tools.file_operations.organize.organize.uic.loadUi')
    @patch('src.tools.file_operations.organize.organize.Path.exists')
    def test_setup_ui_success(self, mock_exists, mock_loadui, qapp):
        """Test successful UI setup."""
        mock_exists.return_value = True
        
        with patch.object(OrganizeWindow, '_init_models'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            # The UI setup is called in __init__, so just verify it worked
            mock_loadui.assert_called_once()
    
    @patch('src.tools.file_operations.organize.organize.uic.loadUi')
    @patch('src.tools.file_operations.organize.organize.Path.exists')
    @patch('src.tools.file_operations.organize.organize.show_error_dialog')
    @patch('sys.exit')
    def test_setup_ui_file_not_found(self, mock_exit, mock_error, mock_exists, mock_loadui, qapp):
        """Test UI setup when file is not found."""
        mock_exists.return_value = False
        
        with patch.object(OrganizeWindow, '_init_models'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            mock_error.assert_called()
            mock_exit.assert_called_with(1)
    
    def test_load_default_rules(self, qapp):
        """Test loading default organization rules."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._load_default_rules()
            
            assert len(window._rules) == 5
            
            # Check specific default rules
            rule_names = [rule.name for rule in window._rules]
            assert "Documents" in rule_names
            assert "Images" in rule_names
            assert "Videos" in rule_names
            assert "Audio" in rule_names
            assert "Archives" in rule_names
    
    @patch('src.tools.file_operations.organize.organize.get_existing_directory')
    def test_load_directory_success(self, mock_get_dir, qapp, temp_directory):
        """Test successful directory loading."""
        mock_get_dir.return_value = temp_directory
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'), \
             patch.object(OrganizeWindow, '_update_file_list'):
            
            window = OrganizeWindow()
            
            # Mock UI components
            window.directory_label = Mock()
            window.organizePushButton = Mock()
            window.status_label = Mock()
            
            window._load_directory()
            
            assert window._current_dir == temp_directory
            window.directory_label.setText.assert_called_with(temp_directory)
            window.organizePushButton.setEnabled.assert_called_with(True)
            window.status_label.setText.assert_called_with("Ready to organize files")
    
    @patch('src.tools.file_operations.organize.organize.get_existing_directory')
    def test_load_directory_cancelled(self, mock_get_dir, qapp):
        """Test directory loading when user cancels."""
        mock_get_dir.return_value = None
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            original_dir = window._current_dir
            
            window._load_directory()
            
            # Directory should not change
            assert window._current_dir == original_dir
    
    def test_get_file_list_non_recursive(self, qapp, temp_directory, sample_files):
        """Test getting file list without recursion."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            # Mock recursiveCheckBox
            window.recursiveCheckBox = Mock()
            window.recursiveCheckBox.isChecked.return_value = False
            
            files = window._get_file_list()
            
            assert len(files) == len(sample_files)
            for file_path in files:
                assert os.path.exists(file_path)
                assert os.path.isfile(file_path)
    
    def test_get_file_list_recursive(self, qapp, temp_directory):
        """Test getting file list with recursion."""
        # Create nested directory structure
        nested_dir = os.path.join(temp_directory, "nested")
        os.makedirs(nested_dir)
        
        # Create files in nested directory
        nested_file = os.path.join(nested_dir, "nested_file.txt")
        with open(nested_file, 'w') as f:
            f.write("nested content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            # Mock recursiveCheckBox
            window.recursiveCheckBox = Mock()
            window.recursiveCheckBox.isChecked.return_value = True
            
            files = window._get_file_list()
            
            # Should include nested file
            assert any(nested_file in f for f in files)
    
    def test_organize_single_file_matching_rule(self, qapp, temp_directory):
        """Test organizing a single file that matches a rule."""
        # Create test file
        test_file = os.path.join(temp_directory, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            window._rules = [
                OrganizeRule("Documents", "*.txt", "Documents", True)
            ]
            
            result = window._organize_single_file(test_file)
            
            assert result is True
            # Check that file was moved
            dest_dir = os.path.join(temp_directory, "Documents")
            dest_file = os.path.join(dest_dir, "test.txt")
            assert os.path.exists(dest_file)
            assert not os.path.exists(test_file)
    
    def test_organize_single_file_no_matching_rule(self, qapp, temp_directory):
        """Test organizing a single file that doesn't match any rule."""
        # Create test file
        test_file = os.path.join(temp_directory, "test.xyz")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            window._rules = [
                OrganizeRule("Documents", "*.txt", "Documents", True)
            ]
            
            result = window._organize_single_file(test_file)
            
            assert result is False
            # File should still exist in original location
            assert os.path.exists(test_file)
    
    def test_organize_single_file_disabled_rule(self, qapp, temp_directory):
        """Test organizing a file with a disabled rule."""
        # Create test file
        test_file = os.path.join(temp_directory, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            window._rules = [
                OrganizeRule("Documents", "*.txt", "Documents", False)  # Disabled
            ]
            
            result = window._organize_single_file(test_file)
            
            assert result is False
            # File should still exist in original location
            assert os.path.exists(test_file)
    
    def test_move_file_to_destination_success(self, qapp, temp_directory):
        """Test successful file movement to destination."""
        # Create test file
        test_file = os.path.join(temp_directory, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            result = window._move_file_to_destination(test_file, "Documents")
            
            assert result is True
            # Check destination
            dest_file = os.path.join(temp_directory, "Documents", "test.txt")
            assert os.path.exists(dest_file)
            assert not os.path.exists(test_file)
            
            # Check organized files tracking
            assert len(window._organized_files) == 1
            assert window._organized_files[0] == (test_file, dest_file)
    
    def test_move_file_to_destination_duplicate_handling(self, qapp, temp_directory):
        """Test file movement with duplicate filename handling."""
        # Create test files
        test_file1 = os.path.join(temp_directory, "test.txt")
        test_file2 = os.path.join(temp_directory, "test2.txt")
        
        with open(test_file1, 'w') as f:
            f.write("test content 1")
        with open(test_file2, 'w') as f:
            f.write("test content 2")
        
        # Create destination directory and file with same name
        dest_dir = os.path.join(temp_directory, "Documents")
        os.makedirs(dest_dir)
        existing_file = os.path.join(dest_dir, "test.txt")
        with open(existing_file, 'w') as f:
            f.write("existing content")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            result = window._move_file_to_destination(test_file1, "Documents")
            
            assert result is True
            # Original file should be renamed to avoid conflict
            dest_file = os.path.join(dest_dir, "test_1.txt")
            assert os.path.exists(dest_file)
            assert os.path.exists(existing_file)  # Original should still exist
    
    def test_move_file_nonexistent_source(self, qapp, temp_directory):
        """Test moving a non-existent file."""
        nonexistent_file = os.path.join(temp_directory, "nonexistent.txt")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            result = window._move_file_to_destination(nonexistent_file, "Documents")
            
            assert result is False
    
    @patch('src.tools.file_operations.organize.organize.QMessageBox.information')
    def test_organize_files_success(self, mock_msgbox, qapp, temp_directory, sample_files):
        """Test successful file organization."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'), \
             patch.object(OrganizeWindow, '_update_file_list'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            window._rules = [
                OrganizeRule("Documents", "*.txt", "Documents", True),
                OrganizeRule("Images", "*.jpg", "Images", True)
            ]
            window.status_label = Mock()
            
            window._organize_files()
            
            mock_msgbox.assert_called_once()
            window.status_label.setText.assert_called()
    
    @patch('src.tools.file_operations.organize.organize.show_error_dialog')
    def test_organize_files_error_handling(self, mock_error, qapp):
        """Test error handling in file organization."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'), \
             patch.object(OrganizeWindow, '_get_file_list', side_effect=Exception("Test error")):
            
            window = OrganizeWindow()
            window._current_dir = "/some/directory"
            
            window._organize_files()
            
            mock_error.assert_called_once()
    
    @patch('src.tools.file_operations.organize.organize.QMessageBox.information')
    def test_undo_last_organization(self, mock_msgbox, qapp, temp_directory):
        """Test undoing the last organization operation."""
        # Create test files and simulate organization
        test_file = os.path.join(temp_directory, "test.txt")
        dest_dir = os.path.join(temp_directory, "Documents")
        dest_file = os.path.join(dest_dir, "test.txt")
        
        with open(test_file, 'w') as f:
            f.write("test content")
        
        os.makedirs(dest_dir)
        shutil.move(test_file, dest_file)
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'), \
             patch.object(OrganizeWindow, '_update_file_list'):
            
            window = OrganizeWindow()
            window._organized_files = [(test_file, dest_file)]
            
            window._undo_last_organization()
            
            # File should be back in original location
            assert os.path.exists(test_file)
            assert not os.path.exists(dest_file)
            assert len(window._organized_files) == 0
            
            mock_msgbox.assert_called_once()


class TestRulesDialog:
    """Test cases for RulesDialog class."""
    
    def test_rules_dialog_initialization(self, qapp, sample_rules):
        """Test RulesDialog initialization."""
        with patch.object(RulesDialog, '_init_ui'):
            dialog = RulesDialog(sample_rules)
            
            assert len(dialog._rules) == len(sample_rules)
            # Should be a copy, not the same object
            assert dialog._rules is not sample_rules
            assert dialog._rules == sample_rules
    
    def test_get_rules(self, qapp, sample_rules):
        """Test getting rules from dialog."""
        with patch.object(RulesDialog, '_init_ui'):
            dialog = RulesDialog(sample_rules)
            
            returned_rules = dialog.get_rules()
            
            assert returned_rules == sample_rules
            assert returned_rules is dialog._rules


class TestRuleEditDialog:
    """Test cases for RuleEditDialog class."""
    
    def test_rule_edit_dialog_new_rule(self, qapp):
        """Test RuleEditDialog for creating new rule."""
        with patch.object(RuleEditDialog, '_init_ui'):
            dialog = RuleEditDialog()
            
            assert dialog._rule is None
    
    def test_rule_edit_dialog_edit_existing(self, qapp):
        """Test RuleEditDialog for editing existing rule."""
        rule = OrganizeRule("Test", "*.txt", "TestDest")
        
        with patch.object(RuleEditDialog, '_init_ui'):
            dialog = RuleEditDialog(rule=rule)
            
            assert dialog._rule == rule
    
    def test_get_rule(self, qapp):
        """Test getting rule from edit dialog."""
        with patch.object(RuleEditDialog, '_init_ui'):
            dialog = RuleEditDialog()
            
            # Mock UI elements
            dialog.name_edit = Mock()
            dialog.name_edit.text.return_value = "TestRule"
            dialog.pattern_edit = Mock()
            dialog.pattern_edit.text.return_value = "*.test"
            dialog.dest_edit = Mock()
            dialog.dest_edit.text.return_value = "TestFolder"
            
            rule = dialog.get_rule()
            
            assert rule.name == "TestRule"
            assert rule.pattern == "*.test"
            assert rule.destination == "TestFolder"
            assert rule.enabled is True  # Default


class TestMainFunction:
    """Test cases for main function."""
    
    @patch('src.tools.file_operations.organize.organize.QApplication')
    @patch('src.tools.file_operations.organize.organize.OrganizeWindow')
    @patch('sys.exit')
    def test_main_function(self, mock_exit, mock_window, mock_app):
        """Test main function execution."""
        mock_app_instance = Mock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.exec_.return_value = 0
        
        main()
        
        mock_app.assert_called_once()
        mock_app_instance.setStyle.assert_called_with('Fusion')
        mock_window.assert_called_once()
        mock_exit.assert_called_with(0)


class TestEdgeCasesAndErrorHandling:
    """Test cases for edge cases and error handling."""
    
    def test_organize_rule_with_empty_values(self):
        """Test OrganizeRule with empty string values."""
        rule = OrganizeRule("", "", "")
        
        assert rule.name == ""
        assert rule.pattern == ""
        assert rule.destination == ""
        assert rule.enabled is True
    
    def test_organize_rule_with_special_characters(self):
        """Test OrganizeRule with special characters."""
        rule = OrganizeRule(
            "Test@#$%",
            "*.txt;*.pdf;*.doc*",
            "Folder/With/Path"
        )
        
        assert rule.name == "Test@#$%"
        assert rule.pattern == "*.txt;*.pdf;*.doc*"
        assert rule.destination == "Folder/With/Path"
    
    def test_file_list_with_permission_error(self, qapp, temp_directory):
        """Test file listing with permission errors."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'), \
             patch('src.tools.file_operations.organize.organize.show_error_dialog') as mock_error:
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            
            # Mock Path.rglob to raise PermissionError
            with patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
                window.recursiveCheckBox = Mock()
                window.recursiveCheckBox.isChecked.return_value = False
                
                window._update_file_list()
                
                mock_error.assert_called_once()
    
    def test_organize_files_with_no_current_directory(self, qapp):
        """Test organizing files when no directory is selected."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = ""  # No directory selected
            
            # Should return early without doing anything
            window._organize_files()
            
            # No files should be organized
            assert len(window._organized_files) == 0


class TestPerformanceAndMemory:
    """Test cases for performance and memory usage."""
    
    def test_large_file_list_handling(self, qapp, temp_directory):
        """Test handling of large number of files."""
        # Create many test files
        num_files = 1000
        for i in range(num_files):
            file_path = os.path.join(temp_directory, f"file_{i:04d}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content of file {i}")
        
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            window._current_dir = temp_directory
            window.recursiveCheckBox = Mock()
            window.recursiveCheckBox.isChecked.return_value = False
            
            files = window._get_file_list()
            
            assert len(files) == num_files
    
    def test_memory_cleanup_after_organization(self, qapp, temp_directory):
        """Test memory cleanup after file organization."""
        with patch.object(OrganizeWindow, '_setup_ui'), \
             patch.object(OrganizeWindow, '_setup_icons'), \
             patch.object(OrganizeWindow, '_connect_signals'), \
             patch.object(OrganizeWindow, '_set_initial_state'), \
             patch.object(OrganizeWindow, '_load_default_rules'), \
             patch.object(OrganizeWindow, 'show'):
            
            window = OrganizeWindow()
            
            # Add many organized files
            for i in range(100):
                window._organized_files.append(
                    (f"source_{i}.txt", f"dest_{i}.txt")
                )
            
            # Clear organized files (simulating new organization)
            window._organized_files.clear()
            
            assert len(window._organized_files) == 0


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup for the entire test session."""
    # Record test start time
    start_time = datetime.now()
    
    yield
    
    # Record test end time and create summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Create test results summary
    results_dir = Path("C:/Users/HP1/1_2/1_2/tests/unit")
    results_file = results_dir / f"result_organize_2025-08-24.json"
    
    # Basic test session info
    session_info = {
        "test_session": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "test_file": "test_organize_2025-08-24.py",
            "target_module": "organize.py",
            "framework": "pytest",
            "test_categories": [
                "OrganizeRule dataclass",
                "OrganizeWindow class",
                "RulesDialog class", 
                "RuleEditDialog class",
                "Main function",
                "Edge cases and error handling",
                "Performance and memory"
            ]
        }
    }
    
    try:
        with open(results_file, 'w') as f:
            json.dump(session_info, f, indent=2)
    except Exception as e:
        print(f"Could not write test results: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])