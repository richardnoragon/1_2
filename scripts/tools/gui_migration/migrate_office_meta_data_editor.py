# Migration script for office_meta_data_editor.py
import re
from pathlib import Path

from core.error_handler import error_handler


def migrate():
    """migrate."""
    file_path = Path("src/tools/metadata/office_metadata/office_meta_data_editor.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update class inheritance
    content = re.sub(
        r"class\s+OfficeMetaDataEditorGUI\s*\(\s*QMainWindow\s*\)",
        f"class OfficeMetaDataEditorGUI(BaseWindow)",
        content,
    )

    # Write updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
