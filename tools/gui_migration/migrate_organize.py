# Migration script for organize.py
from pathlib import Path
import re


def migrate():
    file_path = Path('organize.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+RuleDialog\s*\(\s*QDialog\s*\)',
        f'class RuleDialog(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)