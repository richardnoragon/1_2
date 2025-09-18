"""
Directory Path Validator for RFU Hub

Validates directory paths for security vulnerabilities including
path traversal attacks, symbolic link exploitation, and access violations.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import os
import re
import logging
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathValidationResult:
    """Result of path validation operation"""
    valid: bool
    reason: Optional[str] = None
    normalized_path: Optional[str] = None
    security_level: int = 0


class DirectoryPathValidator:
    """
    Validates directory paths for security vulnerabilities including
    path traversal attacks, symbolic link exploitation, and access violations.
    """
    
    def __init__(self):
        """Initialize DirectoryPathValidator"""
        self.allowed_path_patterns = self._load_allowed_patterns()
        self.blocked_path_patterns = self._load_blocked_patterns()
        self.max_path_length = 4096
        self.max_depth = 50
        self.logger = logging.getLogger('RFU.DirectoryPathValidator')
        
        self.logger.info("DirectoryPathValidator initialized successfully")
    
    def validate_directory_path(self, directory_path: str, 
                               user_id: str) -> PathValidationResult:
        """
        Comprehensive directory path validation
        
        Args:
            directory_path: Directory path to validate
            user_id: User identifier for context-specific validation
            
        Returns:
            PathValidationResult with validation outcome and details
        """
        try:
            self.logger.debug(f"Validating directory path for user {user_id[:8]}...")
            
            # Basic format validation
            format_result = self._validate_path_format(directory_path)
            if not format_result.valid:
                return format_result
            
            # Path traversal validation
            traversal_result = self._validate_path_traversal(directory_path)
            if not traversal_result.valid:
                return traversal_result
            
            # Symbolic link validation
            symlink_result = self._validate_symbolic_links(directory_path)
            if not symlink_result.valid:
                return symlink_result
            
            # Network path validation
            network_result = self._validate_network_paths(directory_path)
            if not network_result.valid:
                return network_result
            
            # User-specific validation
            user_result = self._validate_user_access_rights(directory_path, user_id)
            if not user_result.valid:
                return user_result
            
            # Whitelist/blacklist validation
            pattern_result = self._validate_against_patterns(directory_path)
            if not pattern_result.valid:
                return pattern_result
            
            # Calculate security level
            security_level = self._calculate_security_level(directory_path)
            
            self.logger.debug("Directory path validation successful")
            
            return PathValidationResult(
                valid=True,
                normalized_path=os.path.normpath(directory_path),
                security_level=security_level
            )
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return PathValidationResult(
                valid=False,
                reason=f"Validation system error: {e}"
            )
    
    def validate_path_accessibility(self, directory_path: str) -> bool:
        """
        Validate that path exists and is accessible
        
        Args:
            directory_path: Directory path to check
            
        Returns:
            True if path is accessible, False otherwise
        """
        try:
            path_obj = Path(directory_path)
            
            # Check if path exists
            if not path_obj.exists():
                return False
            
            # Check if it's a directory
            if not path_obj.is_dir():
                return False
            
            # Check basic access
            if not os.access(directory_path, os.R_OK):
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Path accessibility check failed: {e}")
            return False
    
    def _validate_path_format(self, directory_path: str) -> PathValidationResult:
        """Validate basic path format and constraints"""
        
        # Check path length
        if len(directory_path) > self.max_path_length:
            return PathValidationResult(
                valid=False,
                reason=(f"Path exceeds maximum length of "
                       f"{self.max_path_length} characters")
            )
        
        # Check for null bytes
        if '\x00' in directory_path:
            return PathValidationResult(
                valid=False,
                reason="Path contains null bytes"
            )
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '|', '*', '?']
        if any(char in directory_path for char in invalid_chars):
            return PathValidationResult(
                valid=False,
                reason=f"Path contains invalid characters: {invalid_chars}"
            )
        
        # Check path depth
        try:
            path_depth = len(Path(directory_path).parts)
            if path_depth > self.max_depth:
                return PathValidationResult(
                    valid=False,
                    reason=(f"Path depth exceeds maximum of "
                           f"{self.max_depth} levels")
                )
        except Exception:
            return PathValidationResult(
                valid=False,
                reason="Invalid path format"
            )
        
        return PathValidationResult(valid=True)
    
    def _validate_path_traversal(self, 
                                directory_path: str) -> PathValidationResult:
        """Validate against path traversal attacks"""
        
        # Normalize path and check for traversal patterns
        try:
            normalized = os.path.normpath(directory_path)
        except Exception:
            return PathValidationResult(
                valid=False,
                reason="Path normalization failed"
            )
        
        # Check for malicious patterns using centralized logic
        has_malicious, pattern_type = self._contains_malicious_patterns(directory_path)
        if has_malicious:
            if pattern_type == "directory_traversal":
                reason = "Path contains directory traversal sequences"
            elif pattern_type == "encoded_traversal":
                reason = "Path contains encoded traversal sequences"
            else:
                reason = "Path contains malicious patterns"
            
            return PathValidationResult(valid=False, reason=reason)
        
        # Check if normalized path goes outside allowed boundaries
        if normalized.startswith('..'):
            return PathValidationResult(
                valid=False,
                reason="Path attempts to access parent directories"
            )
        
        return PathValidationResult(valid=True)
    
    def _validate_symbolic_links(self, 
                                directory_path: str) -> PathValidationResult:
        """Validate symbolic links for security risks"""
        
        try:
            path_obj = Path(directory_path)
            
            # Check if path exists and resolve symbolic links
            if path_obj.exists():
                resolved_path = path_obj.resolve()
                
                # Check if resolved path is different (indicates symlink)
                if str(resolved_path) != str(path_obj.absolute()):
                    # Validate that symlink target is safe
                    if not self._is_symlink_target_safe(resolved_path):
                        return PathValidationResult(
                            valid=False,
                            reason="Symbolic link target is not safe"
                        )
            
            return PathValidationResult(valid=True)
            
        except (OSError, RuntimeError) as e:
            return PathValidationResult(
                valid=False,
                reason=f"Symbolic link validation failed: {e}"
            )
    
    def _validate_network_paths(self, 
                               directory_path: str) -> PathValidationResult:
        """Validate network paths for security"""
        
        is_network, protocol = self._is_network_path(directory_path)
        if is_network:
            if protocol == "UNC":
                reason = "UNC network paths are not allowed"
            else:
                reason = f"Network protocol paths are not allowed: {protocol}"
            
            return PathValidationResult(valid=False, reason=reason)
        
        return PathValidationResult(valid=True)
    
    def _validate_user_access_rights(self, directory_path: str, 
                                   user_id: str) -> PathValidationResult:
        """Validate user has appropriate access rights"""
        
        try:
            path_obj = Path(directory_path)
            
            # Check if path exists
            if not path_obj.exists():
                # Allow non-existent paths for creation
                return PathValidationResult(valid=True)
            
            # Check read access
            if not os.access(directory_path, os.R_OK):
                return PathValidationResult(
                    valid=False,
                    reason="User lacks read access to directory"
                )
            
            # Check if path is within user's allowed directories
            if not self._is_path_in_user_scope(directory_path, user_id):
                return PathValidationResult(
                    valid=False,
                    reason="Directory is outside user's allowed scope"
                )
            
            return PathValidationResult(valid=True)
            
        except Exception as e:
            return PathValidationResult(
                valid=False,
                reason=f"Access rights validation failed: {e}"
            )
    
    def _validate_against_patterns(self, 
                                  directory_path: str) -> PathValidationResult:
        """Validate path against allowed/blocked patterns"""
        
        # Check against blocked patterns first
        if self._matches_any_pattern(directory_path, self.blocked_path_patterns):
            return PathValidationResult(
                valid=False,
                reason="Path matches blocked pattern"
            )
        
        # Check against allowed patterns
        if self._matches_any_pattern(directory_path, self.allowed_path_patterns):
            return PathValidationResult(valid=True)
        
        # If no allowed pattern matches, it's still valid
        # (patterns are restrictive, not exclusive)
        return PathValidationResult(valid=True)
    
    def _matches_any_pattern(self, path: str, patterns: List[str]) -> bool:
        """
        Centralized pattern matching logic.
        
        Args:
            path: Path to check against patterns
            patterns: List of regex patterns to match against
            
        Returns:
            bool: True if path matches any pattern
        """
        for pattern in patterns:
            if re.match(pattern, path, re.IGNORECASE):
                return True
        return False
    
    def _is_system_directory(self, path: str) -> bool:
        """
        Centralized system directory detection.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path appears to be a system directory
        """
        path_lower = path.lower()
        
        # System directory indicators for different platforms
        system_indicators = [
            # Windows system directories
            'system', 'windows', 'program files', 'system32',
            # Unix/Linux system directories  
            '/etc', '/sys', '/proc', '/boot', '/root'
        ]
        
        return any(indicator in path_lower for indicator in system_indicators)
    
    def _is_user_directory(self, path: str) -> bool:
        """
        Centralized user directory detection.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path appears to be a user directory
        """
        path_lower = path.lower()
        
        # User directory indicators
        user_indicators = ['users', 'home', 'documents', 'desktop']
        
        return any(indicator in path_lower for indicator in user_indicators)
    
    def _is_network_path(self, path: str) -> tuple[bool, str]:
        """
        Centralized network path detection.
        
        Args:
            path: Path to check
            
        Returns:
            tuple: (is_network_path, protocol_or_reason)
        """
        # Check for UNC paths (Windows)
        if path.startswith('\\\\'):
            return True, "UNC"
        
        # Check for network protocols
        network_protocols = ['ftp://', 'http://', 'https://', 
                           'smb://', 'nfs://']
        path_lower = path.lower()
        for protocol in network_protocols:
            if path_lower.startswith(protocol):
                return True, protocol
        
        return False, ""
    
    def _contains_malicious_patterns(self, path: str) -> tuple[bool, str]:
        """
        Centralized detection of malicious path patterns.
        
        Args:
            path: Path to check for malicious patterns
            
        Returns:
            tuple: (contains_malicious, pattern_type)
        """
        # Check for directory traversal sequences
        traversal_patterns = ['../', '..\\', '../', '..\\\\']
        for pattern in traversal_patterns:
            if pattern in path:
                return True, "directory_traversal"
        
        # Check for encoded traversal attempts
        encoded_patterns = ['%2e%2e', '%2E%2E', '..%2f', '..%5c']
        path_lower = path.lower()
        for pattern in encoded_patterns:
            if pattern.lower() in path_lower:
                return True, "encoded_traversal"
        
        return False, ""
    
    def _calculate_security_level(self, directory_path: str) -> int:
        """Calculate security level of directory path (1-5)"""
        
        security_level = 1
        
        # Increase level for system directories
        if self._is_system_directory(directory_path):
            security_level = max(security_level, 4)
        
        # Increase level for user-specific directories
        if self._is_user_directory(directory_path):
            security_level = max(security_level, 3)
        
        # Increase level for hidden directories
        if any(part.startswith('.') for part in Path(directory_path).parts):
            security_level = max(security_level, 3)
        
        # Increase level for deep paths
        if len(Path(directory_path).parts) > 10:
            security_level = max(security_level, 2)
        
        return security_level
    
    def _is_symlink_target_safe(self, resolved_path: Path) -> bool:
        """Check if symbolic link target is safe"""
        
        # Convert to string for pattern matching
        target_str = str(resolved_path)
        
        # Check against blocked patterns using centralized logic
        if self._matches_any_pattern(target_str, self.blocked_path_patterns):
            return False
        
        # Check if target is a system directory using centralized logic
        if self._is_system_directory(target_str):
            return False
        
        return True
    
    def _is_path_in_user_scope(self, directory_path: str, user_id: str) -> bool:
        """Check if path is within user's allowed scope"""
        
        # For now, allow all paths (can be restricted based on requirements)
        # This could be enhanced to check against user-specific allowed directories
        
        path_lower = directory_path.lower()
        
        # Block obvious system directories
        system_dirs = [
            'system32', 'syswow64', 'windows/system',
            '/etc/shadow', '/etc/passwd', '/root',
            '/sys', '/proc', '/dev'
        ]
        
        for sys_dir in system_dirs:
            if sys_dir in path_lower:
                return False
        
        return True
    
    def _load_allowed_patterns(self) -> List[str]:
        """Load allowed directory path patterns"""
        return [
            r'^[A-Za-z]:\\Users\\[^\\]+\\.*',  # Windows user directories
            r'^/home/[^/]+/.*',                # Linux user directories
            r'^/Users/[^/]+/.*',               # macOS user directories
            r'^[A-Za-z]:\\Program Files\\.*',  # Windows program files
            r'^/opt/.*',                       # Linux optional software
            r'^/usr/local/.*',                 # Linux local software
            r'^[A-Za-z]:\\.*',                 # Any Windows drive
            r'^/.*',                           # Any Unix path
        ]
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked directory path patterns"""
        return [
            # Windows system directories
            r'^[A-Za-z]:\\Windows\\System32\\.*',
            r'^[A-Za-z]:\\Windows\\SysWOW64\\.*',
            r'^[A-Za-z]:\\System Volume Information\\.*',
            
            # Linux/Unix system directories
            r'^/etc/shadow.*',
            r'^/etc/passwd.*',
            r'^/root/.*',
            r'^/sys/.*',
            r'^/proc/.*',
            r'^/dev/.*',
            
            # Common sensitive directories
            r'.*/\.ssh/.*',
            r'.*/\.gnupg/.*',
        ]