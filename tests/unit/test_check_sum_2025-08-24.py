#!/usr/bin/env python3
"""
Comprehensive Unit Tests for check_sum.py
Created: 2025-08-24
Framework: pytest

Test Coverage:
- ChecksumGUI class initialization
- File selection functionality
- Checksum calculation (MD5)
- UI component creation and behavior
- Error handling scenarios
- Menu integration features
- Mock data testing with edge cases
"""

import hashlib
import os
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the source directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    from tools.analysis.checksum.check_sum import ChecksumGUI, main
except ImportError:
    # Alternative import path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from tools.analysis.checksum.check_sum import ChecksumGUI, main


class TestChecksumGUI:
    """Test suite for ChecksumGUI class."""

    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        # No need to quit here as it might affect other tests

    @pytest.fixture
    def checksum_gui(self, app):
        """Create ChecksumGUI instance for testing."""
        gui = ChecksumGUI()
        yield gui
        gui.close()

    @pytest.fixture
    def temp_test_file(self):
        """Create temporary test file with known content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            test_content = "This is a test file for checksum calculation."
            f.write(test_content)
            temp_path = f.name

        yield temp_path, test_content

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def large_test_file(self):
        """Create large temporary test file for performance testing."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Create 1MB test file
            test_data = b"A" * (1024 * 1024)
            f.write(test_data)
            temp_path = f.name

        yield temp_path, test_data

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def empty_test_file(self):
        """Create empty temporary test file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_checksum_gui_initialization(self, checksum_gui):
        """Test ChecksumGUI proper initialization."""
        assert checksum_gui is not None
        assert hasattr(checksum_gui, "selected_file")
        assert hasattr(checksum_gui, "file_label")
        assert hasattr(checksum_gui, "results_list")
        assert checksum_gui.selected_file is None

    def test_window_title_setting(self, checksum_gui):
        """Test that window title is set correctly."""
        title = checksum_gui.windowTitle()
        assert "Checksum Calculator" in title
        assert "Richard's File Utilities" in title

    def test_ui_components_creation(self, checksum_gui):
        """Test that all UI components are created properly."""
        # Check if key UI components exist
        assert hasattr(checksum_gui, "file_label")
        assert hasattr(checksum_gui, "results_list")

        # Verify initial states
        assert "No file selected" in checksum_gui.file_label.text()
        assert checksum_gui.results_list.count() == 0

    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_select_file_success(self, mock_file_dialog, checksum_gui, temp_test_file):
        """Test successful file selection."""
        temp_path, _ = temp_test_file
        mock_file_dialog.return_value = (temp_path, "All Files (*.*)")

        checksum_gui.select_file()

        assert checksum_gui.selected_file == temp_path
        assert os.path.basename(temp_path) in checksum_gui.file_label.text()

    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_select_file_cancel(self, mock_file_dialog, checksum_gui):
        """Test file selection cancellation."""
        mock_file_dialog.return_value = ("", "")

        original_file = checksum_gui.selected_file
        checksum_gui.select_file()

        assert checksum_gui.selected_file == original_file

    def test_calculate_checksum_no_file_selected(self, checksum_gui):
        """Test checksum calculation with no file selected."""
        with patch.object(QMessageBox, "warning") as mock_warning:
            checksum_gui.calculate_checksum()
            mock_warning.assert_called_once()

    def test_calculate_checksum_success(self, checksum_gui, temp_test_file):
        """Test successful checksum calculation."""
        temp_path, test_content = temp_test_file
        checksum_gui.selected_file = temp_path

        # Calculate expected MD5
        expected_md5 = hashlib.md5(test_content.encode()).hexdigest()

        checksum_gui.calculate_checksum()

        # Check if result was added to the list
        assert checksum_gui.results_list.count() == 1
        result_text = checksum_gui.results_list.item(0).text()
        assert "MD5:" in result_text
        assert expected_md5 in result_text

    def test_calculate_checksum_empty_file(self, checksum_gui, empty_test_file):
        """Test checksum calculation for empty file."""
        checksum_gui.selected_file = empty_test_file

        # Expected MD5 for empty file
        expected_md5 = hashlib.md5(b"").hexdigest()

        checksum_gui.calculate_checksum()

        assert checksum_gui.results_list.count() == 1
        result_text = checksum_gui.results_list.item(0).text()
        assert expected_md5 in result_text

    def test_calculate_checksum_large_file(self, checksum_gui, large_test_file):
        """Test checksum calculation for large file."""
        temp_path, test_data = large_test_file
        checksum_gui.selected_file = temp_path

        # Calculate expected MD5
        expected_md5 = hashlib.md5(test_data).hexdigest()

        checksum_gui.calculate_checksum()

        assert checksum_gui.results_list.count() == 1
        result_text = checksum_gui.results_list.item(0).text()
        assert expected_md5 in result_text

    def test_calculate_checksum_nonexistent_file(self, checksum_gui):
        """Test checksum calculation for nonexistent file."""
        checksum_gui.selected_file = "/nonexistent/file/path.txt"

        with patch.object(QMessageBox, "critical") as mock_critical:
            checksum_gui.calculate_checksum()
            mock_critical.assert_called_once()

    def test_calculate_checksum_permission_error(self, checksum_gui):
        """Test checksum calculation with permission error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            checksum_gui.selected_file = temp_path

            # Mock file open to raise PermissionError
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                with patch.object(QMessageBox, "critical") as mock_critical:
                    checksum_gui.calculate_checksum()
                    mock_critical.assert_called_once()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_clear_results(self, checksum_gui, temp_test_file):
        """Test clearing calculation results."""
        temp_path, _ = temp_test_file
        checksum_gui.selected_file = temp_path

        # Add some results first
        checksum_gui.calculate_checksum()
        assert checksum_gui.results_list.count() == 1

        # Clear results
        checksum_gui.clear_results()
        assert checksum_gui.results_list.count() == 0

    def test_show_help(self, checksum_gui):
        """Test help dialog display."""
        with patch.object(QMessageBox, "information") as mock_info:
            checksum_gui.show_help()
            mock_info.assert_called_once()

            # Verify help content
            args, _ = mock_info.call_args
            assert "Checksum Calculator Help" in args
            assert "How to Calculate Checksums" in args[2]

    def test_show_preferences(self, checksum_gui):
        """Test preferences dialog display."""
        with patch.object(QMessageBox, "information") as mock_info:
            checksum_gui.show_preferences()
            mock_info.assert_called_once()

            # Verify preferences content
            args, _ = mock_info.call_args
            assert "Preferences" in args[1]

    def test_refresh_view(self, checksum_gui, temp_test_file):
        """Test refresh/clear view functionality."""
        temp_path, _ = temp_test_file
        checksum_gui.selected_file = temp_path

        # Add some results first
        checksum_gui.calculate_checksum()
        assert checksum_gui.results_list.count() == 1

        # Refresh view
        checksum_gui.refresh_view()
        assert checksum_gui.results_list.count() == 0

    def test_multiple_checksum_calculations(self, checksum_gui, temp_test_file):
        """Test multiple consecutive checksum calculations."""
        temp_path, test_content = temp_test_file
        checksum_gui.selected_file = temp_path

        # Calculate checksum multiple times
        for i in range(3):
            checksum_gui.calculate_checksum()

        # Should have 3 results
        assert checksum_gui.results_list.count() == 3

        # All results should be identical
        expected_md5 = hashlib.md5(test_content.encode()).hexdigest()
        for i in range(3):
            result_text = checksum_gui.results_list.item(i).text()
            assert expected_md5 in result_text

    @patch("src.tools.analysis.checksum.check_sum.STANDARD_WINDOW_AVAILABLE", False)
    def test_fallback_mode_initialization(self, app):
        """Test initialization in fallback mode (without StandardWindow)."""
        gui = ChecksumGUI()
        assert gui is not None
        assert hasattr(gui, "selected_file")
        gui.close()

    def test_menu_callbacks_setup(self, checksum_gui):
        """Test menu callbacks setup when StandardWindow is available."""
        if hasattr(checksum_gui, "menu_manager"):
            # Verify menu callbacks are set up
            assert hasattr(checksum_gui, "_setup_menu_callbacks")

    def test_checksum_accuracy_verification(self, checksum_gui):
        """Test checksum calculation accuracy with known values."""
        # Create file with known content and expected MD5
        test_cases = [
            ("hello", "5d41402abc4b2a76b9719d911017c592"),
            ("world", "7d793037a0760186574b0282f2f435e7"),
            ("", "d41d8cd98f00b204e9800998ecf8427e"),  # empty string
            (
                "The quick brown fox jumps over the lazy dog",
                "9e107d9d372bb6826bd81d3542a419d6",
            ),
        ]

        for content, expected_md5 in test_cases:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write(content)
                temp_path = f.name

            try:
                checksum_gui.selected_file = temp_path
                checksum_gui.clear_results()
                checksum_gui.calculate_checksum()

                result_text = checksum_gui.results_list.item(0).text()
                assert expected_md5 in result_text

            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class TestMainFunction:
    """Test suite for main function."""

    @patch("sys.exit")
    @patch("PyQt5.QtWidgets.QApplication.exec_")
    def test_main_function_execution(self, mock_exec, mock_exit):
        """Test main function creates application and window."""
        with patch("PyQt5.QtWidgets.QApplication") as mock_app:
            mock_app_instance = Mock()
            mock_app.return_value = mock_app_instance

            main()

            mock_app.assert_called_once()
            mock_app_instance.exec_.assert_called_once()
            mock_exit.assert_called_once()


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
    def checksum_gui(self, app):
        """Create ChecksumGUI instance for testing."""
        gui = ChecksumGUI()
        yield gui
        gui.close()

    def test_binary_file_checksum(self, checksum_gui):
        """Test checksum calculation for binary files."""
        # Create binary test file
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            binary_data = bytes(range(256))  # All possible byte values
            f.write(binary_data)
            temp_path = f.name

        try:
            checksum_gui.selected_file = temp_path
            checksum_gui.calculate_checksum()

            # Verify result was calculated
            assert checksum_gui.results_list.count() == 1
            result_text = checksum_gui.results_list.item(0).text()
            assert "MD5:" in result_text
            assert len(result_text.split("MD5: ")[1]) == 32  # MD5 is 32 hex chars

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_unicode_filename_handling(self, checksum_gui):
        """Test handling of files with unicode characters in filename."""
        # Create file with unicode name
        unicode_name = "测试文件_ñáméwith特殊chars.txt"

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix=unicode_name
        ) as f:
            f.write("Unicode filename test")
            temp_path = f.name

        try:
            checksum_gui.selected_file = temp_path
            checksum_gui.calculate_checksum()

            # Should handle unicode filenames gracefully
            assert checksum_gui.results_list.count() == 1

        except UnicodeError:
            pytest.skip("System doesn't support unicode filenames")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_very_long_filename(self, checksum_gui):
        """Test handling of very long filenames."""
        # Create file with very long name (within OS limits)
        long_name = "a" * 100 + ".txt"

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=long_name
            ) as f:
                f.write("Long filename test")
                temp_path = f.name

            checksum_gui.selected_file = temp_path
            checksum_gui.calculate_checksum()

            assert checksum_gui.results_list.count() == 1

        except OSError:
            pytest.skip("System doesn't support very long filenames")
        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_rapid_file_selection_changes(self, checksum_gui):
        """Test rapid file selection changes."""
        # Create multiple temp files
        temp_files = []
        try:
            for i in range(3):
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                    f.write(f"Test file {i}")
                    temp_files.append(f.name)

            # Rapidly change selected file
            for temp_path in temp_files:
                checksum_gui.selected_file = temp_path
                checksum_gui.calculate_checksum()

            # Should have results for all files
            assert checksum_gui.results_list.count() == 3

        finally:
            for temp_path in temp_files:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
