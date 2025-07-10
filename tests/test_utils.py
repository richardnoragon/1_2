import unittest
import sys
import os
import shutil
import tempfile
from PyQt5.QtWidgets import QApplication

from core.error_handler import error_handler


class TestUtils:
    _app = None  # Class variable to hold the QApplication instance
    
    @classmethod
    def get_test_app(cls):
        """Get or create a QApplication instance for testing"""
        if cls._app is None:
            # Create QApplication if it doesn't exist
            cls._app = QApplication.instance()
            if cls._app is None:
                cls._app = QApplication(sys.argv)
        return cls._app

    @staticmethod
    def create_temp_dir():
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp(prefix='rfu_test_')
        return temp_dir

    @staticmethod
    def cleanup_temp_dir(temp_dir):
        """Clean up a temporary test directory"""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def create_test_file(directory, name, content=None, size=None):
        """Create a test file with specified content or size
        
        Args:
            directory (str): Directory to create the file in
            name (str): Name of the file
            content (str or bytes, optional): Content to write to the file
            size (int, optional): Size in bytes for random content
        
        Returns:
            str: Path to the created file
        """
        file_path = os.path.join(directory, name)
        
        if content is not None:
            # Write specified content
            mode = 'w' if isinstance(content, str) else 'wb'
            with open(file_path, mode) as f:
                f.write(content)
        elif size is not None:
            # Create file of specified size with random content
            with open(file_path, 'wb') as f:
                f.write(os.urandom(size))
        else:
            # Create empty file
            open(file_path, 'w').close()
        
        return file_path

    @staticmethod
    def create_nested_directory(base_dir, structure):
        """Create a nested directory structure for testing
        
        Args:
            base_dir (str): Base directory to create structure in
            structure (dict): Directory structure specification
                            Keys are names, values are either None for files
                            or dict for subdirectories
        
        Example:
            create_nested_directory('/tmp/test', {
                'dir1': {
                    'file1.txt': None,
                    'subdir': {
                        'file2.txt': None
                    }
                },
                'file3.txt': None
            })
        """
        for name, content in structure.items():
            path = os.path.join(base_dir, name)
            if content is None:
                # Create file
                open(path, 'w').close()
            else:
                # Create directory and recurse
                os.makedirs(path, exist_ok=True)
                TestUtils.create_nested_directory(path, content)

    @staticmethod
    def compare_directories(dir1, dir2):
        """Compare two directories recursively
        
        Args:
            dir1 (str): First directory path
            dir2 (str): Second directory path
        
        Returns:
            bool: True if directories are identical
        """
        def get_relative_paths(directory):
            paths = set()
            for root, _, files in os.walk(directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, directory)
                    paths.add(rel_path)
            return paths
        
        # Get relative paths in both directories
        paths1 = get_relative_paths(dir1)
        paths2 = get_relative_paths(dir2)
        
        # Compare file sets
        if paths1 != paths2:
            return False
        
        # Compare file contents
        for rel_path in paths1:
            path1 = os.path.join(dir1, rel_path)
            path2 = os.path.join(dir2, rel_path)
            
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                if f1.read() != f2.read():
                    return False
        
        return True

    @staticmethod
    def get_file_tree(directory):
        """Get a dictionary representation of a directory tree
        
        Args:
            directory (str): Directory path
        
        Returns:
            dict: Directory structure as nested dictionary
        """
        result = {}
        for entry in os.scandir(directory):
            if entry.is_file():
                result[entry.name] = {
                    'type': 'file',
                    'size': entry.stat().st_size
                }
            elif entry.is_dir():
                result[entry.name] = {
                    'type': 'directory',
                    'contents': TestUtils.get_file_tree(entry.path)
                }
        return result

    @staticmethod
    def verify_file_permissions(path, mode):
        """Verify file permissions
        
        Args:
            path (str): Path to file
            mode (int): Expected permissions mode (octal)
        
        Returns:
            bool: True if permissions match
        """
        return os.stat(path).st_mode & 0o777 == mode

    @staticmethod
    def get_file_checksum(path, algorithm='sha256'):
        """Calculate file checksum
        
        Args:
            path (str): Path to file
            algorithm (str): Hash algorithm to use
        
        Returns:
            str: Hexadecimal checksum
        """
        import hashlib
        h = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def verify_file_type(path, mime_type):
        """Verify file MIME type
        
        Args:
            path (str): Path to file
            mime_type (str): Expected MIME type
        
        Returns:
            bool: True if file type matches
        """
        import magic
        detected_type = magic.from_file(path, mime=True)
        return detected_type == mime_type