#!/usr/bin/env python3
"""
Simple script to open all text files from a folder and subfolders in VS Code.
Usage: python open_files_clean.py [directory] [options]

Options:
  --max-files N    Maximum number of files to open (default: 50)
  --list          Only list files that would be opened, don't open them
  --insiders      Use VS Code Insiders instead of regular VS Code
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
                if not chunk:
                    return True
                # Check if it contains mostly printable characters
                printable_chars = sum(1 for byte in chunk
                                      if (32 <= byte <= 126 or
                                          byte in [9, 10, 13]))
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


def get_vscode_paths():
    """Get possible VS Code installation paths for Windows."""
    import platform
    
    vscode_paths = {
        'code': [],
        'code-insiders': []
    }
    
    if platform.system() == 'Windows':
        # Common Windows installation paths
        localappdata = os.environ.get('LOCALAPPDATA', '')
        programfiles = os.environ.get('PROGRAMFILES', '')
        programfiles_x86 = os.environ.get('PROGRAMFILES(X86)', '')
        
        # VS Code paths
        paths = [
            (localappdata, 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
            (programfiles, 'Microsoft VS Code', 'bin', 'code.cmd'),
            (programfiles_x86, 'Microsoft VS Code', 'bin', 'code.cmd'),
        ]
        vscode_paths['code'].extend([os.path.join(*path) for path in paths])
        
        # VS Code Insiders paths
        insiders_paths = [
            (localappdata, 'Programs', 'Microsoft VS Code Insiders', 
             'bin', 'code-insiders.cmd'),
            (programfiles, 'Microsoft VS Code Insiders', 
             'bin', 'code-insiders.cmd'),
            (programfiles_x86, 'Microsoft VS Code Insiders', 
             'bin', 'code-insiders.cmd'),
        ]
        vscode_paths['code-insiders'].extend([os.path.join(*path) 
                                             for path in insiders_paths])
    
    return vscode_paths


def open_in_vscode(files, use_insiders=False):
    """Open files in VS Code or VS Code Insiders."""
    if not files:
        print("No text files found.")
        return
    
    print(f"Found {len(files)} text files.")
    
    if len(files) > 15:
        response = input(f"Open {len(files)} files? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    # Choose which VS Code command to use
    if use_insiders:
        commands_to_try = ['code-insiders', 'code']
        editor_name = "VS Code Insiders"
    else:
        commands_to_try = ['code', 'code-insiders']
        editor_name = "VS Code"
    
    # Get Windows-specific paths
    vscode_paths = get_vscode_paths()
    
    # Try each command until one works
    for cmd in commands_to_try:
        # First try the command from PATH
        try:
            subprocess.run([cmd] + files, check=True)
            if cmd == 'code-insiders':
                actual_editor = "VS Code Insiders"
            else:
                actual_editor = "VS Code"
            print(f"Opened {len(files)} files in {actual_editor}.")
            return
        except FileNotFoundError:
            # If not in PATH, try Windows installation paths
            for path in vscode_paths.get(cmd, []):
                if os.path.exists(path):
                    try:
                        subprocess.run([path] + files, check=True)
                        if cmd == 'code-insiders':
                            actual_editor = "VS Code Insiders"
                        else:
                            actual_editor = "VS Code"
                        print(f"Opened {len(files)} files in {actual_editor}.")
                        return
                    except subprocess.CalledProcessError as e:
                        print(f"Error opening files with {path}: {e}")
                        continue
        except subprocess.CalledProcessError as e:
            print(f"Error opening files with {cmd}: {e}")
            continue
    
    # If we get here, none of the commands worked
    msg = f"{editor_name} not found. Please install VS Code/VS Code Insiders"
    print(f"{msg} and add to PATH.")
    print("Tried commands:", ", ".join(commands_to_try))


def main():
    """Main function."""
    # Parse command line arguments
    directory = '.'
    max_files = 50
    list_only = False
    use_insiders = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--max-files' and i + 1 < len(args):
            try:
                max_files = int(args[i + 1])
                i += 2
            except ValueError:
                print("Invalid --max-files value. Using default 50.")
                i += 1
        elif args[i] == '--list':
            list_only = True
            i += 1
        elif args[i] == '--insiders':
            use_insiders = True
            i += 1
        elif not args[i].startswith('--'):
            directory = args[i]
            i += 1
        else:
            i += 1
    
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory.")
        return
    
    print(f"Scanning: {os.path.abspath(directory)}")
    
    files = find_text_files(directory, max_files)
    files.sort()  # Sort for consistent order
    
    if list_only:
        print(f"\nText files found ({len(files)}):")
        for i, file_path in enumerate(files, 1):
            print(f"{i:3d}. {file_path}")
    else:
        open_in_vscode(files, use_insiders)


if __name__ == "__main__":
    main()