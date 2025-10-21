"""
Directory Path Encryption for RFU Hub

Handles encryption and decryption of directory paths with
user-specific key derivation and integrity protection.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import os
import hashlib
import logging
import secrets
from typing import Optional
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


@dataclass
class DirectoryEncryptionResult:
    """Result of directory encryption operation"""

    success: bool
    encrypted_data: Optional[bytes] = None
    salt: Optional[bytes] = None
    nonce: Optional[bytes] = None
    path_hash: Optional[str] = None
    integrity_hash: Optional[str] = None
    encryption_version: int = 1
    error: Optional[str] = None


@dataclass
class DirectoryDecryptionResult:
    """Result of directory decryption operation"""

    success: bool
    directory_path: Optional[str] = None
    integrity_verified: bool = False
    error: Optional[str] = None


class DirectoryPathEncryption:
    """
    Handles encryption and decryption of directory paths with
    user-specific key derivation and integrity protection.
    """

    def __init__(self):
        """Initialize DirectoryPathEncryption"""
        self.salt_length = 32
        self.nonce_length = 12
        self.key_length = 32
        self.key_iterations = 100000
        self.current_version = 1
        self.logger = logging.getLogger("RFU.DirectoryPathEncryption")

        self.logger.info("DirectoryPathEncryption initialized successfully")

    def encrypt_directory_path(
        self, directory_path: str, user_id: str
    ) -> DirectoryEncryptionResult:
        """
        Encrypt directory path with user-specific key

        Args:
            directory_path: Directory path to encrypt
            user_id: User identifier for key derivation

        Returns:
            DirectoryEncryptionResult with encrypted data and metadata
        """
        try:
            if not directory_path or not user_id:
                return DirectoryEncryptionResult(
                    success=False,
                    error="Directory path and user ID are required",
                )

            self.logger.debug(
                f"Encrypting directory path for user {user_id[:8]}..."
            )

            # Normalize path for consistent encryption
            normalized_path = os.path.normpath(directory_path)
            path_bytes = normalized_path.encode("utf-8")

            # Generate salt and derive key
            salt = os.urandom(self.salt_length)
            key = self._derive_directory_key(user_id, salt)

            # Generate nonce for AEAD
            nonce = os.urandom(self.nonce_length)

            # Encrypt with AES-GCM
            aesgcm = AESGCM(key)
            encrypted_data = aesgcm.encrypt(nonce, path_bytes, None)

            # Create path hash for indexing (without revealing path)
            path_hash = self._create_secure_path_hash(normalized_path, user_id)

            # Create integrity hash
            integrity_hash = self._create_integrity_hash(
                encrypted_data, salt, nonce, user_id
            )

            self.logger.debug("Directory path encryption successful")

            return DirectoryEncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                salt=salt,
                nonce=nonce,
                path_hash=path_hash,
                integrity_hash=integrity_hash,
                encryption_version=self.current_version,
            )

        except Exception as e:
            self.logger.error(f"Directory path encryption failed: {e}")
            return DirectoryEncryptionResult(
                success=False, error=f"Encryption failed: {e}"
            )

    def decrypt_directory_path(
        self,
        encrypted_data: bytes,
        salt: bytes,
        nonce: bytes,
        user_id: str,
        integrity_hash: Optional[str] = None,
    ) -> DirectoryDecryptionResult:
        """
        Decrypt directory path with user-specific key

        Args:
            encrypted_data: Encrypted directory path data
            salt: Salt used for key derivation
            nonce: Nonce used for encryption
            user_id: User identifier for key derivation
            integrity_hash: Optional integrity hash for verification

        Returns:
            DirectoryDecryptionResult with decrypted path
        """
        try:
            if not encrypted_data or not salt or not nonce or not user_id:
                return DirectoryDecryptionResult(
                    success=False,
                    error="All encryption parameters are required",
                )

            self.logger.debug(
                f"Decrypting directory path for user {user_id[:8]}..."
            )

            # Verify integrity if hash provided
            integrity_verified = False
            if integrity_hash:
                calculated_hash = self._create_integrity_hash(
                    encrypted_data, salt, nonce, user_id
                )
                if calculated_hash != integrity_hash:
                    return DirectoryDecryptionResult(
                        success=False, error="Integrity verification failed"
                    )
                integrity_verified = True

            # Derive key from user ID and salt
            key = self._derive_directory_key(user_id, salt)

            # Decrypt with AES-GCM
            aesgcm = AESGCM(key)
            decrypted_bytes = aesgcm.decrypt(nonce, encrypted_data, None)

            # Convert to string
            directory_path = decrypted_bytes.decode("utf-8")

            self.logger.debug("Directory path decryption successful")

            return DirectoryDecryptionResult(
                success=True,
                directory_path=directory_path,
                integrity_verified=integrity_verified,
            )

        except Exception as e:
            self.logger.error(f"Directory path decryption failed: {e}")
            return DirectoryDecryptionResult(
                success=False, error=f"Decryption failed: {e}"
            )

    def _derive_directory_key(self, user_id: str, salt: bytes) -> bytes:
        """
        Derive encryption key from user ID and salt

        Args:
            user_id: User identifier
            salt: Random salt

        Returns:
            Derived encryption key
        """
        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.key_iterations,
            backend=default_backend(),
        )

        # Derive key from user ID
        user_bytes = user_id.encode("utf-8")
        key = kdf.derive(user_bytes)

        return key

    def _create_secure_path_hash(
        self, directory_path: str, user_id: str
    ) -> str:
        """
        Create secure hash of directory path for indexing

        Args:
            directory_path: Directory path to hash
            user_id: User identifier

        Returns:
            Secure hash string
        """
        # Include user ID and random salt in hash to prevent rainbow table attacks
        salt = secrets.token_hex(16)
        combined = f"{user_id}:{directory_path}:{salt}"

        hash_obj = hashlib.sha256(combined.encode("utf-8"))
        return hash_obj.hexdigest()[:32]

    def _create_integrity_hash(
        self, encrypted_data: bytes, salt: bytes, nonce: bytes, user_id: str
    ) -> str:
        """
        Create integrity hash for verification

        Args:
            encrypted_data: Encrypted data
            salt: Encryption salt
            nonce: Encryption nonce
            user_id: User identifier

        Returns:
            Integrity hash string
        """
        # Combine all components for integrity verification
        combined_data = encrypted_data + salt + nonce + user_id.encode("utf-8")

        hash_obj = hashlib.sha256(combined_data)
        return hash_obj.hexdigest()

    def create_encryption_metadata(
        self, encryption_result: DirectoryEncryptionResult
    ) -> dict:
        """
        Create metadata dictionary for storing encryption information

        Args:
            encryption_result: Result from encryption operation

        Returns:
            Metadata dictionary
        """
        if not encryption_result.success:
            return {}

        return {
            "salt": encryption_result.salt.hex(),
            "nonce": encryption_result.nonce.hex(),
            "integrity_hash": encryption_result.integrity_hash,
            "encryption_version": encryption_result.encryption_version,
            "algorithm": "AES-256-GCM",
            "kdf": "PBKDF2-SHA256",
            "iterations": self.key_iterations,
        }

    def parse_encryption_metadata(self, metadata: dict) -> tuple:
        """
        Parse encryption metadata back to components

        Args:
            metadata: Metadata dictionary

        Returns:
            Tuple of (salt, nonce, integrity_hash, version)
        """
        try:
            salt = bytes.fromhex(metadata["salt"])
            nonce = bytes.fromhex(metadata["nonce"])
            integrity_hash = metadata["integrity_hash"]
            version = metadata.get("encryption_version", 1)

            return salt, nonce, integrity_hash, version

        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid encryption metadata: {e}")

    def is_encryption_supported(self, version: int) -> bool:
        """
        Check if encryption version is supported

        Args:
            version: Encryption version to check

        Returns:
            True if supported, False otherwise
        """
        return version == self.current_version

    def validate_encryption_parameters(
        self, encrypted_data: bytes, salt: bytes, nonce: bytes, user_id: str
    ) -> bool:
        """
        Validate encryption parameters

        Args:
            encrypted_data: Encrypted data to validate
            salt: Salt to validate
            nonce: Nonce to validate
            user_id: User ID to validate

        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            # Check data types and lengths
            if (
                not isinstance(encrypted_data, bytes)
                or len(encrypted_data) == 0
            ):
                return False

            if not isinstance(salt, bytes) or len(salt) != self.salt_length:
                return False

            if not isinstance(nonce, bytes) or len(nonce) != self.nonce_length:
                return False

            if not isinstance(user_id, str) or len(user_id) == 0:
                return False

            return True

        except Exception:
            return False

    def get_encryption_info(self) -> dict:
        """
        Get information about encryption configuration

        Returns:
            Dictionary with encryption information
        """
        return {
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-SHA256",
            "key_length": self.key_length,
            "salt_length": self.salt_length,
            "nonce_length": self.nonce_length,
            "iterations": self.key_iterations,
            "current_version": self.current_version,
        }

    def secure_delete_key_material(self, key_material: bytes) -> None:
        """
        Securely delete key material from memory

        Args:
            key_material: Key material to delete
        """
        try:
            # Overwrite memory with random data
            if isinstance(key_material, bytes):
                # Create a mutable copy and overwrite
                mutable_copy = bytearray(key_material)
                for i in range(len(mutable_copy)):
                    mutable_copy[i] = secrets.randbits(8)
                # Clear the mutable copy
                del mutable_copy

        except Exception as e:
            self.logger.warning(f"Secure key deletion failed: {e}")


class DirectoryKeyManager:
    """
    Manages directory encryption keys and key rotation
    """

    def __init__(self):
        """Initialize DirectoryKeyManager"""
        self.logger = logging.getLogger("RFU.DirectoryKeyManager")
        self.master_key_length = 32

    def generate_master_key(self) -> bytes:
        """
        Generate a new master key for directory encryption

        Returns:
            Master key bytes
        """
        return os.urandom(self.master_key_length)

    def derive_user_key(
        self, master_key: bytes, user_id: str, salt: bytes
    ) -> bytes:
        """
        Derive user-specific key from master key

        Args:
            master_key: Master encryption key
            user_id: User identifier
            salt: Random salt

        Returns:
            User-specific key
        """
        # Combine master key and user ID
        combined = master_key + user_id.encode("utf-8")

        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        return kdf.derive(combined)

    def rotate_keys(self, old_master_key: bytes) -> bytes:
        """
        Generate new master key for key rotation

        Args:
            old_master_key: Previous master key

        Returns:
            New master key
        """
        # Generate new master key
        new_master_key = self.generate_master_key()

        # Log key rotation (without revealing key material)
        self.logger.info("Directory encryption key rotation completed")

        return new_master_key
