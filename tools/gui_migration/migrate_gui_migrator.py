# Migration script for gui_migrator.py
from pathlib import Path
import re


def migrate():
    file_path = Path('tools\gui_migration\gui_migrator.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()




    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)