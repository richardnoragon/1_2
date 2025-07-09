"""Script to automate GUI migration process with proper path handling."""
import os
import sys
from pathlib import Path
import re
import ast
import shutil
import logging
from typing import Dict, List, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GUIMigrationAutomator:
    """Automates the migration of GUI files to use common utilities."""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.migration_dir = workspace_path / "tools" / "gui_migration" / "scripts"
        self.gui_files: List[Path] = []
        self.migration_plans: Dict[Path, dict] = {}
        
    def find_gui_files(self) -> List[Path]:
        """Find all Python files containing GUI code."""
        patterns = [
            r'QMainWindow',
            r'QDialog',
            r'QWidget',
            r'uic\.loadUi',
            r'PyQt5',
            r'\.ui',
            r'QMessageBox',
            r'QFileDialog'
        ]
        
        # Reset gui_files list
        self.gui_files = []
        
        # Ensure workspace path is absolute
        workspace = Path(self.workspace_path).resolve()
        
        # Find all Python files
        for py_file in workspace.rglob('*.py'):
            # Skip test files and migration scripts (but not in test mode)
            if not hasattr(self, '_test_mode'):
                if ('test_' in py_file.name or 
                    'tests' in py_file.parts or
                    'migration' in py_file.parts):
                    continue
                    
            try:
                content = py_file.read_text(encoding='utf-8')
                if any(re.search(p, content) for p in patterns):
                    self.gui_files.append(py_file)
                    logger.info(f"Found GUI file: {py_file}")
            except Exception as e:
                logger.error(f"Error reading {py_file}: {e}")
                
        return self.gui_files
        
    def analyze_gui_file(self, file_path: Path) -> Optional[dict]:
        """Analyze a GUI file and create a migration plan."""
        try:
            content = file_path.read_text(encoding='utf-8')
            plan = {
                'file': file_path,
                'changes': []
            }
            
            # Check for QMainWindow/QDialog inheritance
            class_match = re.search(
                r'class\s+(\w+)\s*\(\s*(QMainWindow|QDialog)\s*\)',
                content
            )
            if class_match:
                plan['changes'].append({
                    'type': 'inheritance',
                    'class_name': class_match.group(1),
                    'original_parent': class_match.group(2)
                })
                
            # Check for QMessageBox usage
            if re.search(r'QMessageBox\.(warning|information|critical)', content):
                plan['changes'].append({'type': 'dialog'})
                
            # Check for QFileDialog usage
            if re.search(
                r'QFileDialog\.(getOpenFileName|getSaveFileName|'
                r'getExistingDirectory)',
                content
            ):
                plan['changes'].append({'type': 'file_dialog'})
                
            return plan if plan['changes'] else None
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
            
    def create_migration_scripts(self):
        """Create migration scripts for all GUI files."""
        self.migration_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.gui_files:
            plan = self.analyze_gui_file(file_path)
            if plan:
                self.migration_plans[file_path] = plan
                self.create_migration_script(file_path, plan)
                
    def create_migration_script(self, file_path: Path, plan: dict):
        """Create a migration script for a specific file."""
        script_name = f"migrate_{file_path.stem}.py"
        script_path = self.migration_dir / script_name
        
        try:
            content = [
                "from pathlib import Path",
                "import re",
                "",
                "def migrate():",
                f"    file_path = Path(r'{file_path}')",
                "    content = file_path.read_text(encoding='utf-8')",
                ""
            ]
            
            for change in plan['changes']:
                if change['type'] == 'inheritance':
                    content.extend([
                        "    # Update class inheritance",
                        "    content = re.sub(",
                        f"        r'class\\s+{change['class_name']}\\s*\\("
                        f"\\s*{change['original_parent']}\\s*\\)',",
                        f"        'class {change['class_name']}(BaseWindow)',",
                        "        content",
                        "    )",
                        ""
                    ])
                    
                elif change['type'] == 'dialog':
                    content.extend([
                        "    # Update dialog usage",
                        "    dialog_replacements = {",
                        "        r'QMessageBox\\.warning\\(([^)]+)\\)': "
                        "r'show_error_dialog\\1',",
                        "        r'QMessageBox\\.information\\(([^)]+)\\)': "
                        "r'show_info_dialog\\1',",
                        "        r'QMessageBox\\.critical\\(([^)]+)\\)': "
                        "r'show_error_dialog\\1'",
                        "    }",
                        "    for pattern, repl in dialog_replacements.items():",
                        "        content = re.sub(pattern, repl, content)",
                        ""
                    ])
                    
                elif change['type'] == 'file_dialog':
                    content.extend([
                        "    # Update file dialog usage",
                        "    file_dialog_replacements = {",
                        "        r'QFileDialog\\.getOpenFileName': "
                        "'get_open_file_name',",
                        "        r'QFileDialog\\.getSaveFileName': "
                        "'get_save_file_name',",
                        "        r'QFileDialog\\.getExistingDirectory': "
                        "'get_existing_directory'",
                        "    }",
                        "    for pattern, repl in file_dialog_replacements.items():",
                        "        content = re.sub(pattern, repl, content)",
                        ""
                    ])
                    
            content.extend([
                "    # Write updated content",
                "    file_path.write_text(content, encoding='utf-8')",
                ""
            ])
            
            script_path.write_text("\n".join(content), encoding='utf-8')
            logger.info(f"Created migration script: {script_path}")
            
        except Exception as e:
            logger.error(f"Error creating migration script for {file_path}: {e}")
            
    def backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file."""
        try:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up {file_path}: {e}")
            return None
            
    def restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a file from backup."""
        try:
            shutil.copy2(backup_path, original_path)
            return True
        except Exception as e:
            logger.error(f"Error restoring {original_path} from backup: {e}")
            return False
            
    def apply_migrations(self, create_backups: bool = True):
        """Apply all migrations."""
        success_count = 0
        
        for file_path, plan in self.migration_plans.items():
            logger.info(f"Migrating {file_path}")
            
            # Create backup if requested
            backup_path = None
            if create_backups:
                backup_path = self.backup_file(file_path)
                if not backup_path:
                    logger.error(f"Failed to create backup for {file_path}")
                    continue
                    
            try:
                # Import and run migration script
                script_path = (
                    self.migration_dir / f"migrate_{file_path.stem}.py"
                )
                if not script_path.exists():
                    logger.error(f"Migration script not found: {script_path}")
                    continue
                    
                # Load and execute migration
                namespace = {}
                exec(script_path.read_text(encoding='utf-8'), namespace)
                namespace['migrate']()
                
                success_count += 1
                logger.info(f"Successfully migrated {file_path}")
                
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
                if backup_path:
                    self.restore_backup(backup_path, file_path)
                    
        logger.info(
            f"Migration complete: {success_count} of "
            f"{len(self.migration_plans)} files migrated"
        )


def main():
    if len(sys.argv) != 2:
        print("Usage: python gui_migrator.py <workspace_path>")
        sys.exit(1)
        
    workspace_path = Path(sys.argv[1])
    if not workspace_path.is_dir():
        print(f"Error: {workspace_path} is not a valid directory")
        sys.exit(1)
        
    automator = GUIMigrationAutomator(workspace_path)
    
    # Find GUI files
    gui_files = automator.find_gui_files()
    logger.info(f"Found {len(gui_files)} GUI files to migrate")
    
    # Create migration scripts
    automator.create_migration_scripts()
    
    # Apply migrations with backups
    automator.apply_migrations(create_backups=True)


if __name__ == '__main__':
    main()
