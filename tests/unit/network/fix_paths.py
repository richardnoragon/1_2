#!/usr/bin/env python3
"""
Fix import paths in test file
"""

def fix_test_file():
    """Fix all src.utilities.network.gui references to utilities.network.gui"""
    file_path = "test_network_gui_2025-08-28.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences
    content = content.replace('src.tools.network.gui', 'utilities.network.gui')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed all module path references")

if __name__ == "__main__":
    fix_test_file()