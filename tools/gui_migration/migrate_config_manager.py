# Migration script for config_manager.py
from pathlib import Path
import re


def migrate():
    file_path = Path('config_manager.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()




    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)