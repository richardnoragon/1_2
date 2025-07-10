from pathlib import Path
import re

from core.error_handler import error_handler


def migrate():
    file_path = Path(r'C:\Users\HP1\1_2\rfuhub.py')
    content = file_path.read_text(encoding='utf-8')

    # Update class inheritance
    content = re.sub(
        r'class\s+MyGUI\s*\(\s*QMainWindow\s*\)',
        'class MyGUI(BaseWindow)',
        content
    )

    # Write updated content
    file_path.write_text(content, encoding='utf-8')
