"""Common dialog utilities for the application."""
from typing import Optional, Union, List, Tuple
from pathlib import Path
from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog, QDialog, QWidget, QInputDialog
)
from PyQt5.QtCore import Qt


def show_error_dialog(
    message: str,
    title: str = "Error",
    parent: Optional[QWidget] = None
) -> None:
    """Show an error message dialog.
    
    Args:
        message: Error message to display
        title: Dialog title
        parent: Parent widget
    """
    show_error_dialogparent, title, message


def show_info_dialog(
    message: str,
    title: str = "Information",
    parent: Optional[QWidget] = None
) -> None:
    """Show an information message dialog.
    
    Args:
        message: Information message to display
        title: Dialog title
        parent: Parent widget
    """
    show_info_dialogparent, title, message


def show_warning_dialog(
    message: str,
    title: str = "Warning",
    parent: Optional[QWidget] = None
) -> None:
    """Show a warning message dialog.
    
    Args:
        message: Warning message to display
        title: Dialog title
        parent: Parent widget
    """
    show_error_dialogparent, title, message


def show_question_dialog(
    message: str,
    title: str = "Question",
    parent: Optional[QWidget] = None,
    default_no: bool = True
) -> bool:
    """Show a yes/no question dialog.
    
    Args:
        message: Question to display
        title: Dialog title
        parent: Parent widget
        default_no: True to make No the default button
        
    Returns:
        True if Yes was clicked, False otherwise
    """
    default = QMessageBox.No if default_no else QMessageBox.Yes
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        default
    )
    return reply == QMessageBox.Yes


def get_open_file_name(
    caption: str,
    directory: Union[str, Path] = "",
    file_filter: str = "All Files (*.*)",
    parent: Optional[QWidget] = None
) -> Optional[Path]:
    """Get a file name for opening.
    
    Args:
        caption: Dialog title
        directory: Starting directory
        file_filter: File type filter
        parent: Parent widget
        
    Returns:
        Selected file path or None if cancelled
    """
    file_name, _ = get_open_file_name(
        parent,
        caption,
        str(directory),
        file_filter
    )
    return Path(file_name) if file_name else None


def get_save_file_name(
    caption: str,
    directory: Union[str, Path] = "",
    file_filter: str = "All Files (*.*)",
    parent: Optional[QWidget] = None
) -> Optional[Path]:
    """Get a file name for saving.
    
    Args:
        caption: Dialog title
        directory: Starting directory
        file_filter: File type filter
        parent: Parent widget
        
    Returns:
        Selected file path or None if cancelled
    """
    file_name, _ = get_save_file_name(
        parent,
        caption,
        str(directory),
        file_filter
    )
    return Path(file_name) if file_name else None


def get_existing_directory(
    caption: str,
    directory: Union[str, Path] = "",
    parent: Optional[QWidget] = None
) -> Optional[Path]:
    """Get an existing directory path.
    
    Args:
        caption: Dialog title
        directory: Starting directory
        parent: Parent widget
        
    Returns:
        Selected directory path or None if cancelled
    """
    dir_name = get_existing_directory(
        parent,
        caption,
        str(directory),
        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    )
    return Path(dir_name) if dir_name else None


def get_open_file_names(
    caption: str,
    directory: Union[str, Path] = "",
    file_filter: str = "All Files (*.*)",
    parent: Optional[QWidget] = None
) -> List[Path]:
    """Get multiple file names for opening.
    
    Args:
        caption: Dialog title
        directory: Starting directory
        file_filter: File type filter
        parent: Parent widget
        
    Returns:
        List of selected file paths (empty if cancelled)
    """
    file_names, _ = get_open_file_names(
        parent,
        caption,
        str(directory),
        file_filter
    )
    return [Path(f) for f in file_names]


def get_text_input(
    prompt: str,
    title: str = "Input",
    default: str = "",
    parent: Optional[QWidget] = None
) -> Tuple[str, bool]:
    """Show a text input dialog.
    
    Args:
        prompt: Text prompt to display
        title: Dialog title
        default: Default input text
        parent: Parent widget
        
    Returns:
        Tuple of (entered_text, ok_pressed)
    """
    return QInputDialog.getText(
        parent,
        title,
        prompt,
        text=default
    )


def get_item_input(
    prompt: str,
    items: List[str],
    title: str = "Select Item",
    current: int = 0,
    editable: bool = False,
    parent: Optional[QWidget] = None
) -> Tuple[str, bool]:
    """Show an item selection dialog.
    
    Args:
        prompt: Text prompt to display
        items: List of items to choose from
        title: Dialog title
        current: Index of current item
        editable: Whether text is editable
        parent: Parent widget
        
    Returns:
        Tuple of (selected_item, ok_pressed)
    """
    return QInputDialog.getItem(
        parent,
        title,
        prompt,
        items,
        current,
        editable
    )


def get_int_input(
    prompt: str,
    title: str = "Input",
    default: int = 0,
    min_val: int = -2147483647,
    max_val: int = 2147483647,
    step: int = 1,
    parent: Optional[QWidget] = None
) -> Tuple[int, bool]:
    """Show an integer input dialog.
    
    Args:
        prompt: Text prompt to display
        title: Dialog title
        default: Default value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        step: Step size for spinbox
        parent: Parent widget
        
    Returns:
        Tuple of (entered_value, ok_pressed)
    """
    return QInputDialog.getInt(
        parent,
        title,
        prompt,
        default,
        min_val,
        max_val,
        step
    )


def get_double_input(
    prompt: str,
    title: str = "Input",
    default: float = 0.0,
    min_val: float = -2147483647.0,
    max_val: float = 2147483647.0,
    decimals: int = 2,
    parent: Optional[QWidget] = None
) -> Tuple[float, bool]:
    """Show a float input dialog.
    
    Args:
        prompt: Text prompt to display
        title: Dialog title
        default: Default value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        decimals: Number of decimal places
        parent: Parent widget
        
    Returns:
        Tuple of (entered_value, ok_pressed)
    """
    return QInputDialog.getDouble(
        parent,
        title,
        prompt,
        default,
        min_val,
        max_val,
        decimals
    )
