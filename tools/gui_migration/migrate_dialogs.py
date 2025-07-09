# Migration script for dialogs.py
from pathlib import Path
import re


def migrate():
    file_path = Path('gui\common\dialogs.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()




    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)