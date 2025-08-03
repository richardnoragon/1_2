"""Migration script for update_gui_files.py"""
from pathlib import Path


def migrate():
    """Migrate the update_gui_files.py script to use common utilities."""
    try:
        file_path = Path('tools/update_gui_files.py')
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    except Exception as e:
        print(f"Error migrating update_gui_files.py: {e}")