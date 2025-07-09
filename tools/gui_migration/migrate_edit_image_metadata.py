# Migration script for edit_image_metadata.py
from pathlib import Path
import re


def migrate():
    file_path = Path('edit_image_metadata.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+ImageMetadataEditor\s*\(\s*QMainWindow\s*\)',
        f'class ImageMetadataEditor(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)