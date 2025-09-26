#!/usr/bin/env python3
"""
Script to open all files from a folder and its subfolders in VS Code editor.
"""

import os
import subprocess
import sys
from pathlib import Path
import argparse


def is_binary_file(file_path):
    """
    Check if a file is binary by reading the first few bytes.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
        return False
    except (IOError, OSError):
        return True


def should_skip_file(file_path, skip_extensions=None, skip_directories=None):
    """
    Determine if a file should be skipped based on extension or directory.
    """
    if skip_extensions is None:
        skip_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o',
            '.pyc', '.pyo', '.class', '.jar', '.war', '.ear',
            '.zip', '.tar', '.gz', '.7z', '.rar', '.iso',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        }
    
    if skip_directories is None:
        skip_directories = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.tox', 'venv', '.venv',
            'env', '.env', 'build', 'dist', '.idea', '.vscode'
        }
    
    # Check if file is in a directory we should skip
    parts = Path(file_path).parts
    for part in parts:
        if part in skip_directories:
            return True
    
    # Check file extension
    file_extension = Path(file_path).suffix.lower()
    if file_extension in skip_extensions:
        return True
    
    # Check if it's a binary file
    if is_binary_file(file_path):
        return True
    
    return False


def get_all_files(directory, max_files=50):
    """
    Get all text files from directory and subdirectories.
    """
    files = []
    directory = Path(directory).resolve()
    
    try:
        for root, dirs, filenames in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs 
                      if not should_skip_file(os.path.join(root, d))]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # Skip files we don't want to open
                if should_skip_file(file_path):
                    continue
                
                # Check if file exists and is readable
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    files.append(file_path)
                    
                    # Safety limit to prevent opening too many files
                    if len(files) >= max_files:
                        print(f"Warning: Reached maximum file limit of {max_files}. Stopping search.")
                        return files
    
    except PermissionError as e:
        print(f"Permission denied accessing directory: {e}")
    except Exception as e:
        print(f"Error walking directory: {e}")
    
    return files


def open_files_in_vscode(files, batch_size=10):
    """
    Open files in VS Code editor in batches.
    """
    if not files:
        print("No files to open.")
        return
    
    print(f"Found {len(files)} files to open.")
    
    # Ask for confirmation if many files
    if len(files) > 20:
        response = input(f"This will open {len(files)} files. Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            return
    
    # Open files in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        try:
            # Use 'code' command to open files in VS Code
            subprocess.run(['code'] + batch, check=True)
            print(f"Opened batch {i//batch_size + 1}: {len(batch)} files")
        except subprocess.CalledProcessError as e:
            print(f"Error opening batch {i//batch_size + 1}: {e}")
        except FileNotFoundError:
            print("VS Code 'code' command not found. Make sure VS Code is installed and added to PATH.")
            print("Alternative: Opening files one by one...")
            for file_path in batch:
                try:
                    subprocess.run(['code', file_path], check=True)
                except Exception as e:
                    print(f"Error opening {file_path}: {e}")


def main():
    """
    Main function to handle command line arguments and execute the script.
    """
    parser = argparse.ArgumentParser(description='Open all files from a folder and subfolders in VS Code')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to scan (default: current directory)')
    parser.add_argument('--max-files', type=int, default=50,
                       help='Maximum number of files to open (default: 50)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of files to open in each batch (default: 10)')
    parser.add_argument('--list-only', action='store_true',
                       help='Only list files that would be opened, don\'t actually open them')
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory.")
        sys.exit(1)
    
    print(f"Scanning directory: {os.path.abspath(args.directory)}")
    
    # Get all files
    files = get_all_files(args.directory, args.max_files)
    
    if not files:
        print("No suitable files found to open.")
        return
    
    # Sort files for consistent ordering
    files.sort()
    
    if args.list_only:
        print(f"\nFiles that would be opened ({len(files)}):")
        for i, file_path in enumerate(files, 1):
            print(f"{i:3d}. {file_path}")
    else:
        # Open files in VS Code
        open_files_in_vscode(files, args.batch_size)


if __name__ == "__main__":
    main()