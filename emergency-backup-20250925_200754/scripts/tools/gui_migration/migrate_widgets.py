# Migration script for widgets.py
from pathlib import Path
import re

from core.error_handler import error_handler



def migrate():
    """migrate."""
    file_path = Path('gui\common\widgets.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()




    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)