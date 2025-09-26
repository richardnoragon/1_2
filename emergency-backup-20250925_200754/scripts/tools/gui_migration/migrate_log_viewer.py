# Migration script for log_viewer.py
from pathlib import Path
import re

from core.error_handler import error_handler



def migrate():
    """migrate."""
    file_path = Path('gui\log_viewer.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+LogViewerWindow\s*\(\s*QMainWindow\s*\)',
        f'class LogViewerWindow(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)