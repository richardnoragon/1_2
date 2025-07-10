from pathlib import Path
import re

from core.error_handler import error_handler


def migrate():
    file_path = Path(r'C:\Users\HP1\1_2\en_and_decrypt.py')
    content = file_path.read_text(encoding='utf-8')

    # Update class inheritance
    content = re.sub(
        r'class\s+en_and_decryptGUI\s*\(\s*QMainWindow\s*\)',
        'class en_and_decryptGUI(BaseWindow)',
        content
    )

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
