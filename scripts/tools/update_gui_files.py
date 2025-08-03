"""Script to identify GUI files that need to be updated with common utilities."""
import os
import sys
from pathlib import Path

from core.error_handler import error_handler


def find_gui_files(workspace_path):
    """Find all Python files that might contain GUI code."""
    gui_files = []
    
    # Patterns that indicate GUI usage
    gui_patterns = [
        'QMainWindow',
        'QDialog',
        'QWidget',
        'uic.loadUi',
        'PyQt5',
        '.ui'
    ]
    
    for py_file in Path(workspace_path).rglob('*.py'):
        if 'test_' in py_file.name or py_file.parent.name == 'tests':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if file contains GUI-related code
            if any(pattern in content for pattern in gui_patterns):
                gui_files.append(py_file)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return gui_files

def print_update_plan(gui_files):
    """Print a plan for updating GUI files."""
    print("\nGUI Files Update Plan:")
    print("=====================")
    
    for file in gui_files:
        print(f"\n{file}:")
        print("  Updates needed:")
        print("  - Replace QMainWindow/QDialog with BaseWindow")
        print("  - Use common dialog utilities")
        print("  - Add progress indicators for long operations")
        print("  - Standardize error handling")
        print("  - Update to use common widgets")

def main():
    """main."""
    if len(sys.argv) != 2:
        print("Usage: python update_gui_files.py <workspace_path>")
        sys.exit(1)
        
    workspace_path = sys.argv[1]
    if not os.path.isdir(workspace_path):
        print(f"Error: {workspace_path} is not a valid directory")
        sys.exit(1)
        
    gui_files = find_gui_files(workspace_path)
    print(f"\nFound {len(gui_files)} GUI files that need updates.")
    print_update_plan(gui_files)

if __name__ == '__main__':
    main()
