# Migration script for compress_decompress.py
from pathlib import Path
import re


def migrate():
    file_path = Path('compress_decompress.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()


    # Update class inheritance
    content = re.sub(
        r'class\s+CompressDecompressApp\s*\(\s*QMainWindow\s*\)',
        f'class CompressDecompressApp(BaseWindow)',
        content
    )


    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)