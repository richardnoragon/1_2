#!/usr/bin/env python3
"""
Requirements.txt Cleaner and Validator
=====================================

This module handles cleaning and validation of requirements.txt files,
particularly those with encoding issues or formatting problems.
"""

import re
import shutil
from pathlib import Path
from typing import List, Tuple
import logging


class RequirementsCleaner:
    """Handles cleaning and validation of requirements.txt files."""
    
    def __init__(self, requirements_path: Path, logger: logging.Logger):
        """Initialize the cleaner.
        
        Args:
            requirements_path: Path to requirements.txt file
            logger: Logger instance
        """
        self.requirements_path = requirements_path
        self.backup_path = requirements_path.with_suffix('.txt.backup')
        self.logger = logger
    
    def clean_requirements_file(self) -> bool:
        """Clean and validate requirements.txt file.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Starting requirements.txt cleanup...")
        
        if not self.requirements_path.exists():
            self.logger.error(f"Requirements file not found: "
                            f"{self.requirements_path}")
            return False
        
        try:
            # Create backup
            shutil.copy2(self.requirements_path, self.backup_path)
            self.logger.info(f"Created backup: {self.backup_path}")
            
            # Read and clean the file
            with open(self.requirements_path, 'r', encoding='utf-8', 
                     errors='ignore') as f:
                content = f.read()
            
            # Clean encoding issues
            cleaned_lines = self._clean_content(content)
            
            # Validate packages
            valid_lines = self._validate_packages(cleaned_lines)
            
            # Write cleaned content
            with open(self.requirements_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(valid_lines) + '\n')
            
            self.logger.info(f"Cleaned {len(valid_lines)} package requirements")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clean requirements file: {e}")
            # Restore backup if cleaning failed
            if self.backup_path.exists():
                shutil.copy2(self.backup_path, self.requirements_path)
                self.logger.info("Restored original requirements file")
            return False
    
    def _clean_content(self, content: str) -> List[str]:
        """Clean content by removing encoding issues.
        
        Args:
            content: Raw file content
            
        Returns:
            List of cleaned lines
        """
        cleaned_lines = []
        for line in content.splitlines():
            # Remove extra spaces between characters
            cleaned_line = re.sub(r'(\w)\s+(\w)', r'\1\2', line.strip())
            # Remove extra spaces around operators
            cleaned_line = re.sub(r'\s*(==|>=|<=|>|<|!=)\s*', r'\1', 
                                cleaned_line)
            
            if cleaned_line and not cleaned_line.startswith('#'):
                cleaned_lines.append(cleaned_line)
        
        return cleaned_lines
    
    def _validate_packages(self, lines: List[str]) -> List[str]:
        """Validate package specifications.
        
        Args:
            lines: List of package lines
            
        Returns:
            List of valid package lines
        """
        valid_lines = []
        package_pattern = re.compile(
            r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9])'
            r'(==|>=|<=|>|<|!=)?'
            r'([0-9]+(?:\.[0-9]+)*(?:\.[a-zA-Z0-9]+)?)?$'
        )
        
        for line in lines:
            if package_pattern.match(line):
                valid_lines.append(line)
            else:
                self.logger.warning(f"Invalid package specification: {line}")
        
        return valid_lines
    
    def get_package_list(self) -> List[Tuple[str, str]]:
        """Get list of packages and versions from requirements file.
        
        Returns:
            List of (package_name, version) tuples
        """
        packages = []
        
        if not self.requirements_path.exists():
            return packages
        
        try:
            with open(self.requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name and version
                        match = re.match(r'^([^=<>!]+)(.*)', line)
                        if match:
                            package_name = match.group(1).strip()
                            version_spec = match.group(2).strip()
                            packages.append((package_name, version_spec))
        
        except Exception as e:
            self.logger.error(f"Failed to parse requirements file: {e}")
        
        return packages