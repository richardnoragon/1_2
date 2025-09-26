"""Script to generate migration scripts with proper path handling."""
import os
import re
from pathlib import Path

from core.error_handler import error_handler



def create_migration_script(file_path: Path, changes: list) -> str:
    """Create a migration script with proper path handling."""
    script = [
        "from pathlib import Path",
        "import re",
        "",
        "def migrate():",
        f"    file_path = Path(r'{str(file_path)}')"
        "    with open(file_path, 'r', encoding='utf-8') as f:",
        "        content = f.read()",
        ""
    ]

    for change in changes:
        if change['type'] == 'inheritance':
            script.extend([
                "    # Update class inheritance",
                "    content = re.sub(",
                f"        r'class\\s+{change['class_name']}\\s*\\(\\s*{change['original_parent']}\\s*\\)',",
                f"        f'class {change['class_name']}(BaseWindow)',",
                "        content",
                "    )",
                ""
            ])
            
        elif change['type'] == 'dialog':
            script.extend([
                "    # Update dialog usage",
                "    replacements = {",
                "        r'QMessageBox\\.warning\\((.*?)\\)': r'show_error_dialog\\1',",
                "        r'QMessageBox\\.information\\((.*?)\\)': r'show_info_dialog\\1',",
                "        r'QMessageBox\\.critical\\((.*?)\\)': r'show_error_dialog\\1'",
                "    }",
                "    for pattern, replacement in replacements.items():",
                "        content = re.sub(pattern, replacement, content)",
                ""
            ])
            
        elif change['type'] == 'file_dialog':
            script.extend([
                "    # Update file dialog usage",
                "    replacements = {",
                "        r'QFileDialog\\.getOpenFileName': 'get_open_file_name',",
                "        r'QFileDialog\\.getSaveFileName': 'get_save_file_name',",
                "        r'QFileDialog\\.getExistingDirectory': 'get_existing_directory'",
                "    }",
                "    for pattern, replacement in replacements.items():",
                "        content = re.sub(pattern, replacement, content)",
                ""
            ])

    script.extend([
        "    # Write updated content",
        "    with open(file_path, 'w', encoding='utf-8') as f:",
        "        f.write(content)",
        ""
    ])

    return "\n".join(script)


def create_migration_files(migration_dir: Path, migration_plans: dict):
    """Create migration script files."""
    os.makedirs(migration_dir, exist_ok=True)
    
    for file_path, plan in migration_plans.items():
        script_name = f"migrate_{file_path.stem}.py"
        script_path = migration_dir / script_name
        
        script_content = create_migration_script(file_path, plan['changes'])
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        print(f"Created migration script: {script_path}")


def main():
    """main."""
    # Example usage:
    migration_dir = Path("tools/gui_migration/scripts")
    
    # Example migration plan
    plans = {
        Path("gui/example.py"): {
            "changes": [
                {
                    "type": "inheritance",
                    "class_name": "ExampleWindow",
                    "original_parent": "QMainWindow"
                },
                {
                    "type": "dialog"
                },
                {
                    "type": "file_dialog"
                }
            ]
        }
    }
    
    create_migration_files(migration_dir, plans)


if __name__ == "__main__":
    main()
