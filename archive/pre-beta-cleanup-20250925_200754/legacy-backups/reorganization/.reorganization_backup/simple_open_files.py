#!/usr/bin/env python3
"""
Simple script to open all text files from a folder and subfolders in VS Code.
Usage: python simple_open_files.py [directory] [--max-files N]
"""

import os
import subprocess
import sys
from pathlib import Path


def is_text_file(file_path):
    """Check if a file is likely a text file."""
    # Common text file extensions
    text_extensions = {
        '.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
        '.md', '.rst', '.yml', '.yaml', '.toml', '.cfg', '.ini',
        '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.r', '.m', '.pl', '.lua', '.vim', '.tex', '.log'
    }
    
    extension = Path(file_path).suffix.lower()
    if extension in text_extensions:
        return True
    
    # Check if file has no extension (might be text)
    if not extension:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)
                # Check if it contains mostly printable characters
                printable_chars = sum(1 for byte in chunk 
                                    if 32 <= byte <= 126 or byte in [9, 10, 13])
                printable_ratio = printable_chars / len(chunk)
                return printable_ratio > 0.7
        except (IOError, OSError, ZeroDivisionError):
            return False
    
    return False


def should_skip_directory(dir_name):
    """Check if a directory should be skipped."""
    skip_dirs = {
        '.git', '.svn', '.hg', '__pycache__', 'node_modules',
        '.pytest_cache', '.mypy_cache', '.tox', 'venv', '.venv',
        'env', '.env', 'build', 'dist', '.idea', '.vscode'
    }
    return dir_name in skip_dirs


def find_text_files(directory, max_files=50):
    """Find all text files in directory and subdirectories."""
    files = []
    
    for root, dirs, filenames in os.walk(directory):
        # Remove directories we want to skip
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]
        
        for filename in filenames:
            file_path = os.path.join(root, filename)
            
            if is_text_file(file_path) and os.access(file_path, os.R_OK):
                files.append(file_path)
                
                if len(files) >= max_files:
                    print(f"Reached maximum of {max_files} files.")
                    return files
    
    return files


def open_in_vscode(files):
    """Open files in VS Code."""
    if not files:
        print("No text files found.")
        return
    
    print(f"Found {len(files)} text files.")
    
    if len(files) > 15:
        response = input(f"Open {len(files)} files? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    try:
        subprocess.run(['code'] + files, check=True)
        print(f"Opened {len(files)} files in VS Code.")
    except FileNotFoundError:
        print("VS Code not found. Install VS Code and add to PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error opening files: {e}")


def main():
    """Main function."""
    # Get directory from command line or use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # Get max files limit
    max_files = 50
    if '--max-files' in sys.argv:
        try:
            idx = sys.argv.index('--max-files')
            max_files = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Invalid --max-files value. Using default 50.")
    
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory.")
        return
    
    print(f"Scanning: {os.path.abspath(directory)}")
    
    files = find_text_files(directory, max_files)
    files.sort()  # Sort for consistent order
    
    if '--list' in sys.argv:
        print(f"\nText files found ({len(files)}):")
        for i, file_path in enumerate(files, 1):
            print(f"{i:3d}. {file_path}")
    else:
        open_in_vscode(files)


if __name__ == "__main__":
    main()