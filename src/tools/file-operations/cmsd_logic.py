"""
CMSD Core Logic Module

This module contains the business logic for the Content Management System
Directory tool. Extracted from the original cmsd.py for better separation
of concerns.
"""

import os
import shutil
from typing import List, Tuple, NamedTuple


class DirectoryComparison(NamedTuple):
    """Results of directory comparison."""
    only_left: List[str]
    only_right: List[str]
    common: List[str]
    total_left: int
    total_right: int


class OperationResult(NamedTuple):
    """Result of file operation."""
    success: bool
    processed_files: List[str]
    failed_files: List[Tuple[str, str]]  # (file, error)
    total_bytes: int


class CMSDLogic:
    """Core business logic for CMSD operations."""
    
    def __init__(self):
        """Initialize CMSD logic."""
        self.left_directory: str = "."
        self.right_directory: str = "."
        self.selected_files: List[str] = []
    
    def load_directory_contents(self, directory: str) -> List[str]:
        """Load files from a directory.
        
        Args:
            directory: Path to directory to scan
            
        Returns:
            List of file paths in the directory
        """
        files = []
        if not os.path.isdir(directory):
            return files
        
        try:
            for item in sorted(os.listdir(directory)):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    files.append(full_path)
        except OSError:
            # Handle permission errors, etc.
            pass
        
        return files
    
    def compare_directories(self) -> DirectoryComparison:
        """Compare contents of left and right directories.
        
        Returns:
            DirectoryComparison with analysis results
        """
        left_files = set(os.path.basename(f) for f in self.get_left_files())
        right_files = set(os.path.basename(f) for f in self.get_right_files())
        
        only_left = sorted(left_files - right_files)
        only_right = sorted(right_files - left_files)
        common = sorted(left_files & right_files)
        
        return DirectoryComparison(
            only_left=only_left,
            only_right=only_right,
            common=common,
            total_left=len(left_files),
            total_right=len(right_files)
        )
    
    def get_left_files(self) -> List[str]:
        """Get files in left directory."""
        return self.load_directory_contents(self.left_directory)
    
    def get_right_files(self) -> List[str]:
        """Get files in right directory."""
        return self.load_directory_contents(self.right_directory)
    
    def add_to_selection(self, file_path: str) -> None:
        """Add file to selection."""
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
    
    def remove_from_selection(self, file_path: str) -> None:
        """Remove file from selection."""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
    
    def clear_selection(self) -> None:
        """Clear all selected files."""
        self.selected_files.clear()
    
    def get_selected_files(self) -> List[str]:
        """Get copy of selected files list."""
        return self.selected_files.copy()
    
    def copy_files(self, source_files: List[str],
                   destination_dir: str) -> OperationResult:
        """Copy files to destination directory.
        
        Args:
            source_files: List of source file paths
            destination_dir: Destination directory path
            
        Returns:
            OperationResult with operation details
        """
        processed = []
        failed = []
        total_bytes = 0
        
        if not os.path.isdir(destination_dir):
            return OperationResult(
                False, [], [("", "Destination directory does not exist")], 0
            )
        
        for file_path in source_files:
            if not os.path.isfile(file_path):
                failed.append((file_path, "Source file does not exist"))
                continue
            
            try:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(destination_dir, file_name)
                
                # Get file size before copying
                file_size = os.path.getsize(file_path)
                
                shutil.copy2(file_path, dest_path)
                processed.append(file_path)
                total_bytes += file_size
                
            except OSError as e:
                failed.append((file_path, str(e)))
        
        success = len(failed) == 0
        return OperationResult(success, processed, failed, total_bytes)
    
    def delete_files(self, files: List[str]) -> OperationResult:
        """Delete specified files.
        
        Args:
            files: List of file paths to delete
            
        Returns:
            OperationResult with operation details
        """
        processed = []
        failed = []
        total_bytes = 0
        
        for file_path in files:
            if not os.path.isfile(file_path):
                failed.append((file_path, "File does not exist"))
                continue
            
            try:
                # Get file size before deletion
                file_size = os.path.getsize(file_path)
                
                os.remove(file_path)
                processed.append(file_path)
                total_bytes += file_size
                
            except OSError as e:
                failed.append((file_path, str(e)))
        
        success = len(failed) == 0
        return OperationResult(success, processed, failed, total_bytes)
    
    def copy_selected_to_right(self) -> OperationResult:
        """Copy selected files from left to right directory."""
        if not self.selected_files:
            return OperationResult(True, [], [], 0)
        
        result = self.copy_files(self.selected_files, self.right_directory)
        if result.success:
            self.clear_selection()
        return result
    
    def copy_selected_to_left(self) -> OperationResult:
        """Copy selected files from right to left directory."""
        if not self.selected_files:
            return OperationResult(True, [], [], 0)
        
        result = self.copy_files(self.selected_files, self.left_directory)
        if result.success:
            self.clear_selection()
        return result
    
    def delete_selected_files(self) -> OperationResult:
        """Delete selected files from their respective directories."""
        if not self.selected_files:
            return OperationResult(True, [], [], 0)
        
        result = self.delete_files(self.selected_files)
        if result.success:
            self.clear_selection()
        return result