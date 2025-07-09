# Migration script for permissions_editor.py
from pathlib import Path
import re


def migrate():
    file_path = Path('permissions_editor.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+FilePermissionsGUI\s*\(\s*QMainWindow\s*\)',
        f'class FilePermissionsGUI(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)