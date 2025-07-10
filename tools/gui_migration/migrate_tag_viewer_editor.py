# Migration script for tag_viewer_editor.py
from pathlib import Path
import re

from core.error_handler import error_handler



def migrate():
    file_path = Path('tag_viewer_editor.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+TagViewerEditor\s*\(\s*QMainWindow\s*\)',
        f'class TagViewerEditor(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)