# Migration script for rename_window.py
from pathlib import Path
import re


def migrate():
    file_path = Path('gui\file_ops\rename_window.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+RenameWindow\s*\(\s*QMainWindow\s*\)',
        f'class RenameWindow(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)