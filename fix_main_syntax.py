#!/usr/bin/env python3
"""
Fix syntax errors in main.py caused by incorrectly escaped docstrings.
"""

import re


def fix_main_syntax():
    """Fix syntax errors in main.py."""
    
    # Read the file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all types of incorrectly escaped strings
    # Fix docstrings first
    content = re.sub(r'\\"\\"\\"([^"]*?)\\"\\"\\"', r'"""\1"""', content, flags=re.DOTALL)
    
    # Fix regular strings with escaped quotes
    content = re.sub(r'f\\"([^"]*?)\\"', r'f"\1"', content)
    content = re.sub(r'\\"([^"]*?)\\"', r'"\1"', content)
    
    # Fix specific problematic patterns
    content = content.replace('\\n\\n', '\\n\\n')
    content = content.replace('\\"', '"')
    
    # Write the fixed content
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax errors in main.py")


if __name__ == '__main__':
    fix_main_syntax()