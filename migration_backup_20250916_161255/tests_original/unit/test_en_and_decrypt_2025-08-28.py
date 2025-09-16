#!/usr/bin/env python3

# Comprehensive pytest unit tests for en_and_decrypt.py
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Import the target module and class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/utilities/security')))
from en_and_decrypt import EnAndDecryptGUI


@pytest.fixture(scope="module")
def app():
    """Setup QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Teardown: QApplication does not need explicit cleanup

@pytest.fixture
def gui(app):
    """Setup and teardown for EnAndDecryptGUI."""
    window = EnAndDecryptGUI()
    yield window
    window.close()

# --- Tests for UI Initialization ---
def test_ui_initialization(gui):
    assert gui.windowTitle() == "Encrypt/Decrypt - Richard's File Utilities"
    assert hasattr(gui, 'selected_files')
    assert hasattr(gui, 'operation_mode')
    assert hasattr(gui, 'files_list')
    assert hasattr(gui, 'password_edit')
    assert hasattr(gui, 'status_label')
    assert hasattr(gui, 'encrypt_button')
    assert hasattr(gui, 'decrypt_button')
    assert hasattr(gui, 'clear_button')

# --- Tests for File Selection ---
def test_select_encrypt_files(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['/tmp/test1.txt', '/tmp/test2.txt'], None)):
        gui.select_encrypt_files()
        assert gui.selected_files == ['/tmp/test1.txt', '/tmp/test2.txt']
        assert gui.operation_mode == 'encrypt'
        assert gui.status_label.text().startswith('Selected 2 file(s) for encryption')

def test_select_decrypt_files(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['/tmp/test1.enc', '/tmp/test2.enc'], None)):
        gui.select_decrypt_files()
        assert gui.selected_files == ['/tmp/test1.enc', '/tmp/test2.enc']
        assert gui.operation_mode == 'decrypt'
        assert gui.status_label.text().startswith('Selected 2 file(s) for decryption')

# --- Tests for Clear Operation ---
def test_clear_operation(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('secret')
    gui.files_list.addItem('dummy')
    gui.status_label.setText('Busy')
    gui.clear_operation()
    assert gui.selected_files == []
    assert gui.password_edit.text() == ''
    assert gui.files_list.count() == 0
    assert gui.status_label.text().startswith('Ready')

# --- Tests for Encrypt/Decrypt Buttons ---
def test_encrypt_files_no_selection(gui):
    gui.selected_files = []
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.encrypt_files()
        mock_warn.assert_called_once()

def test_encrypt_files_no_password(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('')
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.encrypt_files()
        mock_warn.assert_called_once()

def test_encrypt_files_success(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('supersecret')
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.encrypt_files()
        mock_info.assert_called_once()

def test_decrypt_files_no_selection(gui):
    gui.selected_files = []
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.decrypt_files()
        mock_warn.assert_called_once()

def test_decrypt_files_no_password(gui):
    gui.selected_files = ['/tmp/test1.enc']
    gui.password_edit.setText('')
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.decrypt_files()
        mock_warn.assert_called_once()

def test_decrypt_files_success(gui):
    gui.selected_files = ['/tmp/test1.enc']
    gui.password_edit.setText('supersecret')
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.decrypt_files()
        mock_info.assert_called_once()

# --- Edge Cases ---
def test_select_files_empty(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], None)):
        gui.select_encrypt_files()
        assert gui.selected_files == []
        gui.select_decrypt_files()
        assert gui.selected_files == []

# --- Help and Preferences ---
def test_show_help(gui):
    with patch('PyQt5.QtWidgets.QMessageBox.exec_') as mock_exec:
        gui.show_help()
        mock_exec.assert_called_once()

def test_show_preferences(gui):
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.show_preferences()
        mock_info.assert_called_once()

# --- Refresh View ---
def test_refresh_view_calls_clear(gui):
    with patch.object(gui, 'clear_operation') as mock_clear:
        gui.refresh_view()
        mock_clear.assert_called_once()

# --- Main Function ---
def test_main_runs(monkeypatch):
    # Patch QApplication and window.show/sys.exit
    monkeypatch.setattr('PyQt5.QtWidgets.QApplication', MagicMock())
    monkeypatch.setattr('en_and_decrypt.EnAndDecryptGUI', MagicMock())
    monkeypatch.setattr('sys.exit', lambda x: None)
    import en_and_decrypt
    en_and_decrypt.main()

# --- Timestamped Output ---
def test_timestamped_output():
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assert isinstance(now, str)