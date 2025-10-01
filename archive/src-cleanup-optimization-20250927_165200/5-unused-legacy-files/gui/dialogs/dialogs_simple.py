"""
Simple dialog utilities for legacy tools.
"""

from PyQt5.QtWidgets import QMessageBox, QFileDialog
from pathlib import Path


def show_error_dialog(message, title="Error", parent=None):
    """Show an error dialog."""
    QMessageBox.critical(parent, title, message)


def show_info_dialog(message, title="Information", parent=None):
    """Show an info dialog."""
    QMessageBox.information(parent, title, message)


def show_warning_dialog(message, title="Warning", parent=None):
    """Show a warning dialog."""
    QMessageBox.warning(parent, title, message)


def get_existing_directory(
    caption="Select Directory", directory="", parent=None
):
    """Get an existing directory from user."""
    result = QFileDialog.getExistingDirectory(parent, caption, directory)
    return Path(result) if result else None


def get_open_file_name(
    caption="Open File",
    directory="",
    file_filter="All Files (*.*)",
    parent=None,
):
    """Get a file to open from user."""
    result, _ = QFileDialog.getOpenFileName(
        parent, caption, directory, file_filter
    )
    return Path(result) if result else None


def get_save_file_name(
    caption="Save File",
    directory="",
    file_filter="All Files (*.*)",
    parent=None,
):
    """Get a file to save from user."""
    result, _ = QFileDialog.getSaveFileName(
        parent, caption, directory, file_filter
    )
    return Path(result) if result else None
