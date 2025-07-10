from pathlib import Path
import re

from core.error_handler import error_handler


def migrate():
    file_path = Path(r'C:\Users\HP1\1_2\edit_image_metadata.py')
    content = file_path.read_text(encoding='utf-8')

    # Update class inheritance
    content = re.sub(
        r'class\s+ImageMetadataEditor\s*\(\s*QMainWindow\s*\)',
        'class ImageMetadataEditor(BaseWindow)',
        content
    )

    # Update dialog usage
    dialog_replacements = {
        r'QMessageBox\.warning\(([^)]+)\)': r'show_error_dialog\1',
        r'QMessageBox\.information\(([^)]+)\)': r'show_info_dialog\1',
        r'QMessageBox\.critical\(([^)]+)\)': r'show_error_dialog\1'
    }
    for pattern, repl in dialog_replacements.items():
        content = re.sub(pattern, repl, content)

    # Update file dialog usage
    file_dialog_replacements = {
        r'QFileDialog\.getOpenFileName': 'get_open_file_name',
        r'QFileDialog\.getSaveFileName': 'get_save_file_name',
        r'QFileDialog\.getExistingDirectory': 'get_existing_directory'
    }
    for pattern, repl in file_dialog_replacements.items():
        content = re.sub(pattern, repl, content)

    # Write updated content
    file_path.write_text(content, encoding='utf-8')
