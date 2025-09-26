"""
Directory Security Manager for RFU Hub

Central manager for directory security operations including path validation,
PII protection, access control, and comprehensive audit logging.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import os
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import secrets
import json
from datetime import datetime

from ..database.database_manager import DatabaseManager
from .directory_validator import DirectoryPathValidator, PathValidationResult
from .path_sanitizer import PathSanitizer
from .pii_detector import PIIDetector, PIIAnalysisResult
from .directory_encryption import (
    DirectoryPathEncryption,
    DirectoryEncryptionResult,
    DirectoryDecryptionResult,
)
from .directory_permissions import (
    DirectoryPermissionManager,
    PermissionCheckResult,
)
from .directory_audit import DirectoryAuditLogger


@dataclass
class DirectoryStorageResult:
    """Result of directory storage operation"""

    success: bool
    path_hash: Optional[str] = None
    pii_sensitive: bool = False
    sensitivity_level: int = 0
    error: Optional[str] = None
    security_violation: bool = False
    storage_id: Optional[str] = None


@dataclass
class DirectoryRetrievalResult:
    """Result of directory retrieval operation"""

    success: bool
    directory_path: Optional[str] = None
    tool_name: Optional[str] = None
    directory_type: Optional[str] = None
    pii_sensitive: bool = False
    sensitivity_level: int = 0
    error: Optional[str] = None
    security_violation: bool = False
    path_inaccessible: bool = False
    storage_id: Optional[str] = None


class DirectorySecurityManager:
    """
    Central manager for directory security operations including path validation,
    PII protection, access control, and comprehensive audit logging.
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize DirectorySecurityManager

        Args:
            database_manager: Database manager instance
        """
        self.db_manager = database_manager
        self.path_validator = DirectoryPathValidator()
        self.pii_detector = PIIDetector()
        self.permission_manager = DirectoryPermissionManager(database_manager)
        self.audit_logger = DirectoryAuditLogger(database_manager)
        self.encryption = DirectoryPathEncryption()
        self.sanitizer = PathSanitizer()
        self.logger = logging.getLogger("RFU.DirectorySecurityManager")

        # Security configuration
        self.max_storage_attempts = 3
        self.security_level_threshold = 3
        self.enable_path_encryption = True

        self.logger.info("DirectorySecurityManager initialized successfully")

    def store_directory_preference(
        self,
        user_id: str,
        tool_name: str,
        directory_type: str,
        directory_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DirectoryStorageResult:
        """
        Store directory preference with comprehensive security validation

        Args:
            user_id: User identifier
            tool_name: Tool requesting directory storage
            directory_type: Type of directory ('favorite', 'recent', 'default')
            directory_path: Directory path to store
            metadata: Optional metadata for the directory

        Returns:
            DirectoryStorageResult with storage outcome and security metadata
        """
        try:
            self.logger.info(
                f"Storing directory preference for user {user_id[:8]}... tool {tool_name}"
            )

            # Sanitize and validate path
            sanitized_path = self.sanitizer.sanitize_path(directory_path)
            validation_result = self.path_validator.validate_directory_path(
                sanitized_path, user_id
            )

            if not validation_result.valid:
                self.audit_logger.log_security_violation(
                    user_id,
                    "invalid_path",
                    {
                        "reason": validation_result.reason,
                        "tool_name": tool_name,
                        "original_path_hash": self._create_path_hash(
                            directory_path
                        ),
                    },
                )
                return DirectoryStorageResult(
                    success=False,
                    error=f"Path validation failed: {validation_result.reason}",
                    security_violation=True,
                )

            # Check permissions
            permission_result = (
                self.permission_manager.check_directory_permission(
                    user_id, sanitized_path, "write"
                )
            )

            if not permission_result.authorized:
                self.audit_logger.log_access_denied(
                    user_id,
                    self._create_path_hash(sanitized_path),
                    "write",
                    permission_result.reason,
                )
                return DirectoryStorageResult(
                    success=False,
                    error=f"Access denied: {permission_result.reason}",
                    security_violation=True,
                )

            # Detect PII sensitivity
            pii_result = self.pii_detector.analyze_directory_path(
                sanitized_path
            )

            # Create path hash for indexing
            path_hash = self._create_secure_path_hash(sanitized_path, user_id)

            # Encrypt path if PII sensitive or above threshold
            encrypted_path = sanitized_path.encode("utf-8")
            encryption_metadata = None

            if (
                pii_result.contains_pii
                or pii_result.sensitivity_level
                >= self.security_level_threshold
                or self.enable_path_encryption
            ):

                encryption_result = self.encryption.encrypt_directory_path(
                    sanitized_path, user_id
                )

                if not encryption_result.success:
                    self.logger.error(
                        "Failed to encrypt sensitive directory path"
                    )
                    return DirectoryStorageResult(
                        success=False,
                        error="Failed to encrypt sensitive directory path",
                    )

                encrypted_path = encryption_result.encrypted_data
                encryption_metadata = {
                    "salt": encryption_result.salt.hex(),
                    "nonce": encryption_result.nonce.hex(),
                    "integrity_hash": encryption_result.integrity_hash,
                    "encryption_version": encryption_result.encryption_version,
                }

            # Store in database
            storage_id = self._store_encrypted_directory(
                user_id=user_id,
                tool_name=tool_name,
                directory_type=directory_type,
                encrypted_path=encrypted_path,
                path_hash=path_hash,
                is_pii_sensitive=pii_result.contains_pii,
                sensitivity_level=pii_result.sensitivity_level,
                encryption_metadata=encryption_metadata,
                pii_indicators=pii_result.pii_indicators,
                metadata=metadata or {},
            )

            if not storage_id:
                return DirectoryStorageResult(
                    success=False,
                    error="Failed to store directory in database",
                )

            # Log successful storage
            self.audit_logger.log_directory_operation(
                user_id,
                path_hash,
                "store",
                True,
                {
                    "tool_name": tool_name,
                    "directory_type": directory_type,
                    "pii_sensitive": pii_result.contains_pii,
                    "sensitivity_level": pii_result.sensitivity_level,
                    "encrypted": encryption_metadata is not None,
                    "storage_id": storage_id,
                },
            )

            self.logger.info(
                f"Directory preference stored successfully with ID {storage_id}"
            )

            return DirectoryStorageResult(
                success=True,
                path_hash=path_hash,
                pii_sensitive=pii_result.contains_pii,
                sensitivity_level=pii_result.sensitivity_level,
                storage_id=storage_id,
            )

        except Exception as e:
            self.logger.error(f"Directory storage failed: {e}")
            self.audit_logger.log_security_violation(
                user_id,
                "storage_error",
                {"error": str(e), "tool_name": tool_name},
            )
            return DirectoryStorageResult(
                success=False, error=f"Storage system error: {e}"
            )

    def retrieve_directory_preference(
        self, user_id: str, path_hash: str
    ) -> DirectoryRetrievalResult:
        """
        Retrieve directory preference with security validation and decryption

        Args:
            user_id: User identifier
            path_hash: Hashed directory identifier

        Returns:
            DirectoryRetrievalResult with decrypted path or error
        """
        try:
            self.logger.info(
                f"Retrieving directory preference for user {user_id[:8]}..."
            )

            # Check read permissions
            permission_result = (
                self.permission_manager.check_directory_permission(
                    user_id, path_hash, "read"
                )
            )

            if not permission_result.authorized:
                self.audit_logger.log_access_denied(
                    user_id, path_hash, "read", permission_result.reason
                )
                return DirectoryRetrievalResult(
                    success=False,
                    error=f"Access denied: {permission_result.reason}",
                    security_violation=True,
                )

            # Retrieve encrypted directory data
            directory_data = self._get_encrypted_directory(user_id, path_hash)

            if not directory_data:
                return DirectoryRetrievalResult(
                    success=False, error="Directory preference not found"
                )

            # Decrypt path if encrypted
            directory_path = None
            if directory_data["encryption_metadata"]:
                # Path is encrypted
                encryption_metadata = directory_data["encryption_metadata"]

                decryption_result = self.encryption.decrypt_directory_path(
                    encrypted_data=directory_data["encrypted_path"],
                    salt=bytes.fromhex(encryption_metadata["salt"]),
                    nonce=bytes.fromhex(encryption_metadata["nonce"]),
                    user_id=user_id,
                    integrity_hash=encryption_metadata["integrity_hash"],
                )

                if not decryption_result.success:
                    self.audit_logger.log_security_violation(
                        user_id,
                        "decryption_failed",
                        {
                            "path_hash": path_hash,
                            "error": decryption_result.error,
                        },
                    )
                    return DirectoryRetrievalResult(
                        success=False, error="Failed to decrypt directory path"
                    )

                directory_path = decryption_result.directory_path
            else:
                # Path is not encrypted
                directory_path = directory_data["encrypted_path"].decode(
                    "utf-8"
                )

            # Validate path still exists and is accessible
            if not self.path_validator.validate_path_accessibility(
                directory_path
            ):
                self.audit_logger.log_directory_operation(
                    user_id,
                    path_hash,
                    "access_validation_failed",
                    False,
                    {"reason": "Path no longer accessible"},
                )
                return DirectoryRetrievalResult(
                    success=False,
                    error="Directory path is no longer accessible",
                    path_inaccessible=True,
                )

            # Log successful retrieval
            self.audit_logger.log_directory_operation(
                user_id,
                path_hash,
                "retrieve",
                True,
                {
                    "tool_name": directory_data["tool_name"],
                    "directory_type": directory_data["directory_type"],
                    "storage_id": directory_data["storage_id"],
                },
            )

            self.logger.info(f"Directory preference retrieved successfully")

            return DirectoryRetrievalResult(
                success=True,
                directory_path=directory_path,
                tool_name=directory_data["tool_name"],
                directory_type=directory_data["directory_type"],
                pii_sensitive=directory_data["is_pii_sensitive"],
                sensitivity_level=directory_data["sensitivity_level"],
                storage_id=directory_data["storage_id"],
            )

        except Exception as e:
            self.logger.error(f"Directory retrieval failed: {e}")
            self.audit_logger.log_security_violation(
                user_id,
                "retrieval_error",
                {"error": str(e), "path_hash": path_hash},
            )
            return DirectoryRetrievalResult(
                success=False, error=f"Retrieval system error: {e}"
            )

    def list_user_directories(
        self,
        user_id: str,
        tool_name: Optional[str] = None,
        directory_type: Optional[str] = None,
    ) -> List[DirectoryRetrievalResult]:
        """
        List user's stored directory preferences with security filtering

        Args:
            user_id: User identifier
            tool_name: Optional tool name filter
            directory_type: Optional directory type filter

        Returns:
            List of DirectoryRetrievalResult objects
        """
        try:
            self.logger.info(f"Listing directories for user {user_id[:8]}...")

            # Get directory list from database
            directories = self._get_user_directories(
                user_id, tool_name, directory_type
            )

            results = []
            for directory_data in directories:
                # Check read permissions for each directory
                permission_result = (
                    self.permission_manager.check_directory_permission(
                        user_id, directory_data["path_hash"], "read"
                    )
                )

                if not permission_result.authorized:
                    continue  # Skip directories user can't access

                # Create sanitized result (don't decrypt paths for listing)
                result = DirectoryRetrievalResult(
                    success=True,
                    directory_path=None,  # Don't decrypt for listing
                    tool_name=directory_data["tool_name"],
                    directory_type=directory_data["directory_type"],
                    pii_sensitive=directory_data["is_pii_sensitive"],
                    sensitivity_level=directory_data["sensitivity_level"],
                    storage_id=directory_data["storage_id"],
                )
                results.append(result)

            self.audit_logger.log_directory_operation(
                user_id,
                "list_operation",
                "list",
                True,
                {
                    "count": len(results),
                    "tool_filter": tool_name,
                    "type_filter": directory_type,
                },
            )

            return results

        except Exception as e:
            self.logger.error(f"Directory listing failed: {e}")
            return []

    def delete_directory_preference(
        self, user_id: str, path_hash: str
    ) -> bool:
        """
        Delete directory preference with security validation

        Args:
            user_id: User identifier
            path_hash: Hashed directory identifier

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Check delete permissions
            permission_result = (
                self.permission_manager.check_directory_permission(
                    user_id, path_hash, "delete"
                )
            )

            if not permission_result.authorized:
                self.audit_logger.log_access_denied(
                    user_id, path_hash, "delete", permission_result.reason
                )
                return False

            # Delete from database
            success = self._delete_encrypted_directory(user_id, path_hash)

            # Log operation
            self.audit_logger.log_directory_operation(
                user_id, path_hash, "delete", success, {}
            )

            return success

        except Exception as e:
            self.logger.error(f"Directory deletion failed: {e}")
            return False

    def _store_encrypted_directory(
        self,
        user_id: str,
        tool_name: str,
        directory_type: str,
        encrypted_path: bytes,
        path_hash: str,
        is_pii_sensitive: bool,
        sensitivity_level: int,
        encryption_metadata: Optional[Dict],
        pii_indicators: List[str],
        metadata: Dict[str, Any],
    ) -> Optional[str]:
        """Store encrypted directory in database"""
        try:
            storage_id = secrets.token_urlsafe(32)

            # Convert metadata to JSON
            encryption_json = (
                json.dumps(encryption_metadata)
                if encryption_metadata
                else None
            )
            pii_json = json.dumps(pii_indicators)
            metadata_json = json.dumps(metadata)

            query = """
            INSERT INTO secure_directories 
            (storage_id, user_id, tool_name, directory_type, encrypted_path, path_hash,
             is_pii_sensitive, sensitivity_level, encryption_metadata, pii_indicators,
             metadata, created_at, last_accessed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            now = datetime.utcnow().isoformat()

            self.db_manager.execute_query(
                query,
                (
                    storage_id,
                    user_id,
                    tool_name,
                    directory_type,
                    encrypted_path,
                    path_hash,
                    is_pii_sensitive,
                    sensitivity_level,
                    encryption_json,
                    pii_json,
                    metadata_json,
                    now,
                    now,
                ),
            )

            return storage_id

        except Exception as e:
            self.logger.error(f"Failed to store encrypted directory: {e}")
            return None

    def _get_encrypted_directory(
        self, user_id: str, path_hash: str
    ) -> Optional[Dict]:
        """Retrieve encrypted directory from database"""
        try:
            query = """
            SELECT storage_id, tool_name, directory_type, encrypted_path, is_pii_sensitive,
                   sensitivity_level, encryption_metadata, pii_indicators, metadata,
                   created_at, last_accessed_at
            FROM secure_directories
            WHERE user_id = ? AND path_hash = ?
            """

            result = self.db_manager.fetch_one(query, (user_id, path_hash))

            if result:
                # Update last accessed time
                update_query = "UPDATE secure_directories SET last_accessed_at = ? WHERE storage_id = ?"
                self.db_manager.execute_query(
                    update_query, (datetime.utcnow().isoformat(), result[0])
                )

                return {
                    "storage_id": result[0],
                    "tool_name": result[1],
                    "directory_type": result[2],
                    "encrypted_path": result[3],
                    "is_pii_sensitive": result[4],
                    "sensitivity_level": result[5],
                    "encryption_metadata": (
                        json.loads(result[6]) if result[6] else None
                    ),
                    "pii_indicators": json.loads(result[7]),
                    "metadata": json.loads(result[8]),
                    "created_at": result[9],
                    "last_accessed_at": result[10],
                }

            return None

        except Exception as e:
            self.logger.error(f"Failed to get encrypted directory: {e}")
            return None

    def _get_user_directories(
        self,
        user_id: str,
        tool_name: Optional[str] = None,
        directory_type: Optional[str] = None,
    ) -> List[Dict]:
        """Get list of user's directories with optional filtering"""
        try:
            query = """
            SELECT storage_id, tool_name, directory_type, path_hash, is_pii_sensitive,
                   sensitivity_level, created_at, last_accessed_at
            FROM secure_directories
            WHERE user_id = ?
            """
            params = [user_id]

            if tool_name:
                query += " AND tool_name = ?"
                params.append(tool_name)

            if directory_type:
                query += " AND directory_type = ?"
                params.append(directory_type)

            query += " ORDER BY last_accessed_at DESC"

            results = self.db_manager.fetch_all(query, params)

            directories = []
            for result in results:
                directories.append(
                    {
                        "storage_id": result[0],
                        "tool_name": result[1],
                        "directory_type": result[2],
                        "path_hash": result[3],
                        "is_pii_sensitive": result[4],
                        "sensitivity_level": result[5],
                        "created_at": result[6],
                        "last_accessed_at": result[7],
                    }
                )

            return directories

        except Exception as e:
            self.logger.error(f"Failed to get user directories: {e}")
            return []

    def _delete_encrypted_directory(
        self, user_id: str, path_hash: str
    ) -> bool:
        """Delete encrypted directory from database"""
        try:
            query = "DELETE FROM secure_directories WHERE user_id = ? AND path_hash = ?"
            self.db_manager.execute_query(query, (user_id, path_hash))
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete encrypted directory: {e}")
            return False

    def _create_path_hash(self, path: str) -> str:
        """Create simple hash of path for basic indexing"""
        return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]

    def _create_secure_path_hash(self, path: str, user_id: str) -> str:
        """Create secure hash of path with user salt"""
        combined = f"{user_id}:{path}:{secrets.token_hex(16)}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]
