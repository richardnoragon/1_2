"""Script to automate the migration of GUI files to use common utilities."""
import os
import sys
from pathlib import Path
import re
import ast
import logging
from typing import List, Dict, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GUIFileMigrator:
    """Class to handle migration of GUI files to use common utilities."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.gui_files: List[Path] = []
        self.qt_imports: Dict[Path, Set[str]] = {}
        
    def find_gui_files(self) -> List[Path]:
        """Find all Python files that contain GUI code."""
        gui_patterns = [
            r'QMainWindow',
            r'QDialog',
            r'QWidget',
            r'uic\.loadUi',
            r'PyQt5',
            r'\.ui',
            r'QMessageBox',
            r'QFileDialog'
        ]
        
        for py_file in self.workspace_path.rglob('*.py'):
            if 'test_' in py_file.name or 'tests' in py_file.parts:
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                if any(re.search(pattern, content) for pattern in gui_patterns):
                    self.gui_files.append(py_file)
                    logger.info(f"Found GUI file: {py_file}")
            except Exception as e:
                logger.error(f"Error reading {py_file}: {e}")
                
        return self.gui_files
        
    def analyze_imports(self, file_path: Path) -> Set[str]:
        """Analyze imports in a Python file to identify Qt components used."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            qt_imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and 'PyQt5' in node.module:
                    for name in node.names:
                        qt_imports.add(name.name)
                        
            self.qt_imports[file_path] = qt_imports
            return qt_imports
            
        except Exception as e:
            logger.error(f"Error analyzing imports in {file_path}: {e}")
            return set()
            
    def generate_import_updates(self, file_path: Path) -> str:
        """Generate updated import statements for a file."""
        qt_imports = self.qt_imports.get(file_path, set())
        
        # Map Qt widgets to our common utilities
        common_imports = {
            'QMainWindow': 'BaseWindow',
            'QMessageBox': ['show_error_dialog', 'show_info_dialog', 'show_warning_dialog'],
            'QFileDialog': ['get_open_file_name', 'get_save_file_name', 'get_existing_directory'],
            'QProgressBar': ['ProgressWidget']
        }
        
        needed_imports = set()
        for qt_import in qt_imports:
            if qt_import in common_imports:
                if isinstance(common_imports[qt_import], list):
                    needed_imports.update(common_imports[qt_import])
                else:
                    needed_imports.add(common_imports[qt_import])
                    
        if needed_imports:
            imports = sorted(list(needed_imports))
            return (
                f"from gui.common import (\n"
                f"    {','.join(imports)}\n"
                f")"
            )
        return ""
        
    def generate_migration_plan(self, file_path: Path) -> Dict:
        """Generate a migration plan for a specific file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
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
                'original_parent': class_match.group(2),
                'new_parent': 'BaseWindow'
            })
            
        # Check for QMessageBox usage
        if re.search(r'QMessageBox\.(warning|information|critical)', content):
            plan['changes'].append({
                'type': 'dialog',
                'patterns': [
                    (r'QMessageBox\.warning\((.*?)\)', 'show_error_dialog'),
                    (r'QMessageBox\.information\((.*?)\)', 'show_info_dialog'),
                    (r'QMessageBox\.critical\((.*?)\)', 'show_error_dialog')
                ]
            })
            
        # Check for QFileDialog usage
        if re.search(r'QFileDialog\.(getOpenFileName|getSaveFileName|getExistingDirectory)', content):
            plan['changes'].append({
                'type': 'file_dialog',
                'patterns': [
                    (r'QFileDialog\.getOpenFileName', 'get_open_file_name'),
                    (r'QFileDialog\.getSaveFileName', 'get_save_file_name'),
                    (r'QFileDialog\.getExistingDirectory', 'get_existing_directory')
                ]
            })
            
        return plan
        
    def generate_migration_script(self, file_path: Path) -> str:
        """Generate a Python script to perform the migration."""
        plan = self.generate_migration_plan(file_path)
        script_content = []
        script_content.append(f"# Migration script for {file_path.name}")
        script_content.append("from pathlib import Path")
        script_content.append("import re")
        script_content.append("\n")
        script_content.append("def migrate():")
        script_content.append(f"    file_path = Path('{file_path}')")
        script_content.append("    with open(file_path, 'r', encoding='utf-8') as f:")
        script_content.append("        content = f.read()")
        script_content.append("\n")
        
        for change in plan['changes']:
            if change['type'] == 'inheritance':
                script_content.append("    # Update class inheritance")
                script_content.append(f"    content = re.sub(")
                script_content.append(f"        r'class\\s+{change['class_name']}\\s*\\(\\s*{change['original_parent']}\\s*\\)',")
                script_content.append(f"        f'class {change['class_name']}(BaseWindow)',")
                script_content.append(f"        content")
                script_content.append(f"    )")
                
        script_content.append("\n")
        script_content.append("    # Write updated content")
        script_content.append("    with open(file_path, 'w', encoding='utf-8') as f:")
        script_content.append("        f.write(content)")
        
        return "\n".join(script_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python gui_migrator.py <workspace_path>")
        sys.exit(1)
        
    workspace_path = sys.argv[1]
    migrator = GUIFileMigrator(workspace_path)
    
    # Find GUI files
    gui_files = migrator.find_gui_files()
    logger.info(f"Found {len(gui_files)} GUI files to migrate")
    
    # Process each file
    for file_path in gui_files:
        logger.info(f"\nProcessing {file_path}")
        
        # Analyze imports
        imports = migrator.analyze_imports(file_path)
        logger.info(f"Found Qt imports: {imports}")
        
        # Generate migration plan
        plan = migrator.generate_migration_plan(file_path)
        logger.info(f"Migration plan generated with {len(plan['changes'])} changes")
        
        # Generate and save migration script
        script_content = migrator.generate_migration_script(file_path)
        script_path = Path('tools/gui_migration') / f"migrate_{file_path.stem}.py"
        
        try:
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(script_content, encoding='utf-8')
            logger.info(f"Migration script written to {script_path}")
        except Exception as e:
            logger.error(f"Error writing migration script: {e}")

if __name__ == '__main__':
    main()
