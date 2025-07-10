# Migration script for rename_ui.py
from pathlib import Path
import re

from core.error_handler import error_handler



def migrate():
    file_path = Path('rename_ui.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()




    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)