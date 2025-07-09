# Migration script for settings_dialog.py
from pathlib import Path
import re


def migrate():
    file_path = Path('gui\settings_dialog.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+SettingsDialog\s*\(\s*QDialog\s*\)',
        f'class SettingsDialog(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)