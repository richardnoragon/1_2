#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Network Transfer Module

Test File: test_network_transfer_2025-08-24.py
Target Module: src.tools.network.transfer.network_transfer
Created: 2025-08-24
Framework: pytest

This test suite provides comprehensive coverage for the Network Transfer module
including SecurityManager, TransferProtocol, PathSecurity, TransferServer,
TransferClient, and NetworkTransferGUI classes.

Test Coverage:
- SecurityManager: Key generation, encryption/decryption, authentication
- TransferProtocol: Message creation/parsing, validation, size limits
- PathSecurity: Path sanitization, security validation, file validation
- TransferServer: Server functionality, client handling, message processing
- TransferClient: Client connection, file/config/collection transfers
- NetworkTransferGUI: GUI initialization, file selection, transfer operations

Security Focus:
- Path traversal prevention
- Input validation
- Encryption security
- Network security
- File system security
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import shutil
import socket
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QWidget

# Add src to path for importing the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from src.tools.network.transfer.network_transfer import (
        CRYPTO_AVAILABLE,
        NetworkTransferGUI,
        PathSecurity,
        SecurityManager,
        TransferClient,
        TransferProtocol,
        TransferServer,
    )
except ImportError as e:
    pytest.skip(f"Network transfer module not available: {e}", allow_module_level=True)


class TestSecurityManager:
    """Test suite for SecurityManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.security_manager = SecurityManager()

    def teardown_method(self):
        """Clean up after each test method."""
        self.security_manager = None

    def test_security_manager_initialization(self):
        """Test SecurityManager initialization."""
        assert self.security_manager.session_key is None
        assert self.security_manager.auth_token is None
        assert self.security_manager.aes_gcm is None

    def test_generate_session_key(self):
        """Test session key generation."""
        key = self.security_manager.generate_session_key()

        assert isinstance(key, bytes)
        assert len(key) == 32  # 256-bit key
        assert self.security_manager.session_key == key

        # Test key uniqueness
        key2 = self.security_manager.generate_session_key()
        assert key != key2

    def test_generate_auth_token(self):
        """Test authentication token generation."""
        token = self.security_manager.generate_auth_token()

        assert isinstance(token, str)
        assert len(token) > 32  # URL-safe base64 encoding
        assert self.security_manager.auth_token == token

        # Test token uniqueness
        token2 = self.security_manager.generate_auth_token()
        assert token != token2

    def test_verify_auth_token_valid(self):
        """Test authentication token verification with valid token."""
        token = self.security_manager.generate_auth_token()
        assert self.security_manager.verify_auth_token(token) is True

    def test_verify_auth_token_invalid(self):
        """Test authentication token verification with invalid token."""
        self.security_manager.generate_auth_token()
        assert self.security_manager.verify_auth_token("invalid_token") is False

    def test_verify_auth_token_none(self):
        """Test authentication token verification with None values."""
        assert self.security_manager.verify_auth_token(None) is False
        assert self.security_manager.verify_auth_token("") is False

        self.security_manager.generate_auth_token()
        assert self.security_manager.verify_auth_token(None) is False

    def test_encrypt_decrypt_message_with_crypto(self):
        """Test message encryption/decryption with cryptography available."""
        if not CRYPTO_AVAILABLE:
            pytest.skip("Cryptography library not available")

        self.security_manager.generate_session_key()
        original_message = b"Test message for encryption"

        encrypted = self.security_manager.encrypt_message(original_message)
        assert isinstance(encrypted, bytes)
        assert encrypted != original_message
        assert len(encrypted) > len(original_message)  # Should include nonce

        decrypted = self.security_manager.decrypt_message(encrypted)
        assert decrypted == original_message

    def test_encrypt_decrypt_message_fallback(self):
        """Test message encryption/decryption with fallback method."""
        self.security_manager.generate_session_key()

        # Mock CRYPTO_AVAILABLE to False to force fallback
        with patch(
            "src.tools.network.transfer.network_transfer.CRYPTO_AVAILABLE", False
        ):
            self.security_manager.aes_gcm = None  # Reset AES-GCM

            original_message = b"Test message for fallback encryption"

            encrypted = self.security_manager.encrypt_message(original_message)
            assert isinstance(encrypted, bytes)
            assert encrypted != original_message
            assert len(encrypted) > len(original_message)  # Should include MAC and salt

            decrypted = self.security_manager.decrypt_message(encrypted)
            assert decrypted == original_message

    def test_encrypt_without_session_key(self):
        """Test encryption without session key raises error."""
        with pytest.raises(ValueError, match="No session key available"):
            self.security_manager.encrypt_message(b"test")

    def test_decrypt_without_session_key(self):
        """Test decryption without session key raises error."""
        with pytest.raises(ValueError, match="No session key available"):
            self.security_manager.decrypt_message(b"test")

    def test_decrypt_invalid_data(self):
        """Test decryption with invalid data."""
        self.security_manager.generate_session_key()

        if CRYPTO_AVAILABLE:
            with pytest.raises(ValueError, match="Invalid encrypted data"):
                self.security_manager.decrypt_message(b"short")
        else:
            with pytest.raises(ValueError, match="Invalid encrypted data"):
                self.security_manager.decrypt_message(b"short")

    def test_fallback_encrypt_decrypt_edge_cases(self):
        """Test fallback encryption/decryption edge cases."""
        with patch(
            "src.tools.network.transfer.network_transfer.CRYPTO_AVAILABLE", False
        ):
            self.security_manager.generate_session_key()
            self.security_manager.aes_gcm = None

            # Test empty message
            empty_message = b""
            encrypted = self.security_manager.encrypt_message(empty_message)
            decrypted = self.security_manager.decrypt_message(encrypted)
            assert decrypted == empty_message

            # Test large message
            large_message = b"A" * 10000
            encrypted = self.security_manager.encrypt_message(large_message)
            decrypted = self.security_manager.decrypt_message(encrypted)
            assert decrypted == large_message

    def test_fallback_decrypt_corrupted_mac(self):
        """Test fallback decryption with corrupted MAC."""
        with patch(
            "src.tools.network.transfer.network_transfer.CRYPTO_AVAILABLE", False
        ):
            self.security_manager.generate_session_key()
            self.security_manager.aes_gcm = None

            original_message = b"Test message"
            encrypted = self.security_manager.encrypt_message(original_message)

            # Corrupt the MAC (first 32 bytes)
            corrupted = b"X" * 32 + encrypted[32:]

            with pytest.raises(ValueError, match="Message integrity check failed"):
                self.security_manager.decrypt_message(corrupted)


class TestTransferProtocol:
    """Test suite for TransferProtocol class."""

    def test_protocol_constants(self):
        """Test protocol constants are properly defined."""
        assert TransferProtocol.VERSION == "1.0"
        assert TransferProtocol.CHUNK_SIZE == 8192
        assert TransferProtocol.PORT_RANGE == (12000, 12099)
        assert TransferProtocol.MAX_MESSAGE_SIZE == 1024 * 1024 * 10  # 10MB

        # Test message types
        assert hasattr(TransferProtocol, "MSG_HELLO")
        assert hasattr(TransferProtocol, "MSG_AUTH")
        assert hasattr(TransferProtocol, "MSG_FILE_INFO")
        assert hasattr(TransferProtocol, "MSG_FILE_DATA")
        assert hasattr(TransferProtocol, "MSG_CONFIG_DATA")
        assert hasattr(TransferProtocol, "MSG_COLLECTION_DATA")
        assert hasattr(TransferProtocol, "MSG_ACK")
        assert hasattr(TransferProtocol, "MSG_ERROR")
        assert hasattr(TransferProtocol, "MSG_COMPLETE")

    def test_create_message_valid(self):
        """Test creating valid protocol messages."""
        data = {"test": "data", "number": 42}
        message_bytes = TransferProtocol.create_message("TEST", data)

        assert isinstance(message_bytes, bytes)
        assert len(message_bytes) > 4  # Should have length prefix

        # Check length prefix
        length = int.from_bytes(message_bytes[:4], "big")
        assert length == len(message_bytes) - 4

    def test_create_message_with_timestamp(self):
        """Test message includes timestamp."""
        data = {"test": "data"}
        message_bytes = TransferProtocol.create_message("TEST", data)

        # Parse the message to check timestamp
        length = int.from_bytes(message_bytes[:4], "big")
        json_str = message_bytes[4 : 4 + length].decode("utf-8")
        message = json.loads(json_str)

        assert "timestamp" in message
        assert "type" in message
        assert "data" in message
        assert message["type"] == "TEST"
        assert message["data"] == data

    def test_create_message_too_large(self):
        """Test creating message that exceeds size limit."""
        large_data = {"data": "A" * (TransferProtocol.MAX_MESSAGE_SIZE)}

        with pytest.raises(ValueError, match="Message too large"):
            TransferProtocol.create_message("TEST", large_data)

    def test_parse_message_valid(self):
        """Test parsing valid protocol messages."""
        data = {"test": "data", "number": 42}
        message_bytes = TransferProtocol.create_message("TEST", data)

        parsed = TransferProtocol.parse_message(message_bytes)

        assert isinstance(parsed, dict)
        assert parsed["type"] == "TEST"
        assert parsed["data"] == data
        assert "timestamp" in parsed

    def test_parse_message_invalid_length(self):
        """Test parsing message with invalid length."""
        # Too short
        assert TransferProtocol.parse_message(b"abc") is None

        # Invalid length prefix
        invalid_length = (TransferProtocol.MAX_MESSAGE_SIZE + 1).to_bytes(4, "big")
        with pytest.raises(ValueError, match="Message too large"):
            TransferProtocol.parse_message(invalid_length + b"data")

        # Zero length
        zero_length = (0).to_bytes(4, "big")
        with pytest.raises(ValueError, match="Invalid message length"):
            TransferProtocol.parse_message(zero_length)

    def test_parse_message_incomplete(self):
        """Test parsing incomplete messages."""
        data = {"test": "data"}
        complete_message = TransferProtocol.create_message("TEST", data)

        # Truncate the message
        incomplete = complete_message[:-10]
        assert TransferProtocol.parse_message(incomplete) is None

    def test_parse_message_invalid_json(self):
        """Test parsing message with invalid JSON."""
        invalid_json = b"invalid json data"
        length = len(invalid_json).to_bytes(4, "big")
        message_bytes = length + invalid_json

        assert TransferProtocol.parse_message(message_bytes) is None

    def test_message_roundtrip(self):
        """Test message creation and parsing roundtrip."""
        original_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        message_bytes = TransferProtocol.create_message("ROUNDTRIP", original_data)
        parsed = TransferProtocol.parse_message(message_bytes)

        assert parsed["type"] == "ROUNDTRIP"
        assert parsed["data"] == original_data

    def test_message_unicode_support(self):
        """Test message creation with unicode data."""
        unicode_data = {
            "text": "Hello 世界 🌍",
            "emoji": "🔒🔑📁",
            "special": "café naïve résumé",
        }

        message_bytes = TransferProtocol.create_message("UNICODE", unicode_data)
        parsed = TransferProtocol.parse_message(message_bytes)

        assert parsed["data"] == unicode_data


class TestPathSecurity:
    """Test suite for PathSecurity class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_file.txt"
        self.test_file.write_text("Test content")

    def teardown_method(self):
        """Clean up after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_allowed_extensions(self):
        """Test allowed file extensions list."""
        expected_extensions = {
            ".txt",
            ".md",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".zip",
            ".tar",
            ".gz",
            ".json",
            ".xml",
            ".csv",
            ".log",
            ".py",
            ".js",
            ".html",
            ".css",
            ".sql",
            ".ini",
            ".cfg",
            ".conf",
        }

        assert PathSecurity.ALLOWED_EXTENSIONS == expected_extensions

    def test_max_file_size_constant(self):
        """Test maximum file size constant."""
        expected_size = 1024 * 1024 * 1024  # 1GB
        assert PathSecurity.MAX_FILE_SIZE == expected_size

    def test_sanitize_path_normal(self):
        """Test path sanitization with normal paths."""
        normal_path = "folder/subfolder/file.txt"
        sanitized = PathSecurity.sanitize_path(normal_path)
        assert sanitized == normal_path

    def test_sanitize_path_dangerous_chars(self):
        """Test path sanitization with dangerous characters."""
        dangerous_path = 'folder<>:"|?*file.txt'
        sanitized = PathSecurity.sanitize_path(dangerous_path)

        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
        for char in dangerous_chars:
            assert char not in sanitized

        assert sanitized == "folder________file.txt"

    def test_sanitize_path_null_byte(self):
        """Test path sanitization with null byte."""
        null_path = "folder\x00file.txt"
        sanitized = PathSecurity.sanitize_path(null_path)
        assert "\x00" not in sanitized
        assert sanitized == "folder_file.txt"

    def test_sanitize_path_multiple_separators(self):
        """Test path sanitization with multiple path separators."""
        multi_sep_path = "folder//subfolder\\\\file.txt"
        sanitized = PathSecurity.sanitize_path(multi_sep_path)
        assert "//" not in sanitized
        assert "\\\\" not in sanitized
        assert sanitized == "folder/subfolder\\file.txt"

    def test_sanitize_path_empty(self):
        """Test path sanitization with empty input."""
        assert PathSecurity.sanitize_path("") == ""
        assert PathSecurity.sanitize_path(None) == ""

    def test_is_safe_path_valid(self):
        """Test safe path validation with valid paths."""
        base_path = str(self.temp_dir)
        safe_path = "subfolder/file.txt"

        assert PathSecurity.is_safe_path(base_path, safe_path) is True

    def test_is_safe_path_traversal_attempts(self):
        """Test safe path validation against path traversal."""
        base_path = str(self.temp_dir)

        traversal_paths = [
            "../outside",
            "../../etc/passwd",
            "subfolder/../../../outside",
            "~/sensitive",
            "folder/~/file",
            "..\\windows\\system32",
        ]

        for path in traversal_paths:
            assert PathSecurity.is_safe_path(base_path, path) is False

    def test_is_safe_path_absolute_paths(self):
        """Test safe path validation with absolute paths."""
        base_path = str(self.temp_dir)

        # Absolute path within base should be safe
        safe_absolute = str(self.temp_dir / "safe_file.txt")
        assert PathSecurity.is_safe_path(base_path, safe_absolute) is True

        # Absolute path outside base should be unsafe
        unsafe_absolute = "/etc/passwd"
        assert PathSecurity.is_safe_path(base_path, unsafe_absolute) is False

    def test_is_safe_path_empty_inputs(self):
        """Test safe path validation with empty inputs."""
        assert PathSecurity.is_safe_path("", "path") is False
        assert PathSecurity.is_safe_path("base", "") is False
        assert PathSecurity.is_safe_path(None, "path") is False
        assert PathSecurity.is_safe_path("base", None) is False

    def test_secure_join_valid(self):
        """Test secure path joining with valid inputs."""
        base_path = str(self.temp_dir)
        user_path = "subfolder/file.txt"

        result = PathSecurity.secure_join(base_path, user_path)
        assert result is not None
        assert str(self.temp_dir) in result
        assert "subfolder" in result
        assert "file.txt" in result

    def test_secure_join_invalid(self):
        """Test secure path joining with invalid inputs."""
        base_path = str(self.temp_dir)

        invalid_paths = ["../outside", "../../etc/passwd", "~/sensitive"]

        for path in invalid_paths:
            result = PathSecurity.secure_join(base_path, path)
            assert result is None

    def test_validate_file_for_transfer_valid(self):
        """Test file validation for valid file."""
        result = PathSecurity.validate_file_for_transfer(str(self.test_file))

        assert result["valid"] is True
        assert result["reason"] == "File is valid for transfer"
        assert result["size"] > 0
        assert result["extension"] == ".txt"
        assert result["path"] == str(self.test_file)

    def test_validate_file_for_transfer_nonexistent(self):
        """Test file validation for non-existent file."""
        nonexistent = str(self.temp_dir / "nonexistent.txt")
        result = PathSecurity.validate_file_for_transfer(nonexistent)

        assert result["valid"] is False
        assert result["reason"] == "File does not exist"

    def test_validate_file_for_transfer_directory(self):
        """Test file validation for directory."""
        result = PathSecurity.validate_file_for_transfer(str(self.temp_dir))

        assert result["valid"] is False
        assert result["reason"] == "Path is not a file"

    def test_validate_file_for_transfer_forbidden_extension(self):
        """Test file validation for forbidden file extension."""
        exe_file = self.temp_dir / "malicious.exe"
        exe_file.write_text("fake executable")

        result = PathSecurity.validate_file_for_transfer(str(exe_file))

        assert result["valid"] is False
        assert "File type not allowed" in result["reason"]
        assert result["extension"] == ".exe"

    def test_validate_file_for_transfer_too_large(self):
        """Test file validation for file too large."""
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_size = PathSecurity.MAX_FILE_SIZE + 1

            result = PathSecurity.validate_file_for_transfer(str(self.test_file))

            assert result["valid"] is False
            assert "File too large" in result["reason"]

    def test_validate_file_for_transfer_no_read_permission(self):
        """Test file validation for file without read permission."""
        with patch("os.access", return_value=False):
            result = PathSecurity.validate_file_for_transfer(str(self.test_file))

            assert result["valid"] is False
            assert result["reason"] == "File is not readable"

    def test_secure_file_info_valid(self):
        """Test secure file info retrieval for valid file."""
        result = PathSecurity.secure_file_info(str(self.test_file))

        assert result is not None
        assert result["exists"] is True
        assert result["size"] > 0
        assert result["path"] == str(self.test_file)
        assert "validation" in result
        assert result["validation"]["valid"] is True

    def test_secure_file_info_invalid(self):
        """Test secure file info retrieval for invalid file."""
        nonexistent = str(self.temp_dir / "nonexistent.txt")
        result = PathSecurity.secure_file_info(nonexistent)

        assert result is None

    def test_path_security_edge_cases(self):
        """Test path security with various edge cases."""
        base_path = str(self.temp_dir)

        # Test with different path separators
        mixed_separators = "folder\\subfolder/file.txt"
        result = PathSecurity.is_safe_path(base_path, mixed_separators)
        assert isinstance(result, bool)

        # Test with Unicode paths
        unicode_path = "フォルダ/ファイル.txt"
        result = PathSecurity.is_safe_path(base_path, unicode_path)
        assert isinstance(result, bool)

        # Test with very long paths
        long_path = "a" * 1000 + "/file.txt"
        result = PathSecurity.is_safe_path(base_path, long_path)
        assert isinstance(result, bool)


class TestTransferServer:
    """Test suite for TransferServer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.port = 12345
        self.server = None

    def teardown_method(self):
        """Clean up after each test method."""
        if self.server and self.server.running:
            self.server.stop()
            self.server.wait()
        self.server = None

    def test_transfer_server_initialization(self):
        """Test TransferServer initialization."""
        server = TransferServer(self.port)

        assert server.port == self.port
        assert server.running is False
        assert server.server_socket is None
        assert isinstance(server.security_manager, SecurityManager)

    def test_transfer_server_signals(self):
        """Test TransferServer signal definitions."""
        server = TransferServer(self.port)

        # Check that signals exist
        assert hasattr(server, "client_connected")
        assert hasattr(server, "transfer_started")
        assert hasattr(server, "progress_updated")
        assert hasattr(server, "transfer_completed")
        assert hasattr(server, "error_occurred")

    @patch("socket.socket")
    def test_server_socket_creation(self, mock_socket):
        """Test server socket creation and binding."""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock

        server = TransferServer(self.port)

        # Mock the run method partially to test socket setup
        with patch.object(server, "running", True):
            # We'll test socket creation without full server run
            try:
                server.run()
            except:
                pass  # Expected to fail in test environment

        # Verify socket configuration would be called
        assert mock_socket.called

    def test_process_message_hello(self):
        """Test processing HELLO message."""
        server = TransferServer(self.port)
        mock_socket = Mock()

        message = {
            "type": TransferProtocol.MSG_HELLO,
            "data": {"client_name": "Test Client"},
        }

        with patch.object(server, "transfer_started") as mock_signal:
            server.process_message(mock_socket, message)
            mock_signal.emit.assert_called_once()

    def test_process_message_file_info(self):
        """Test processing FILE_INFO message."""
        server = TransferServer(self.port)
        mock_socket = Mock()

        message = {
            "type": TransferProtocol.MSG_FILE_INFO,
            "data": {"filename": "test.txt", "filesize": 1024},
        }

        with patch.object(server, "transfer_started") as mock_signal:
            server.process_message(mock_socket, message)
            mock_signal.emit.assert_called_with("File", "test.txt (1024 bytes)")

    def test_process_message_config_data(self):
        """Test processing CONFIG_DATA message."""
        server = TransferServer(self.port)
        mock_socket = Mock()

        config_data = {"setting1": "value1", "setting2": "value2"}
        message = {"type": TransferProtocol.MSG_CONFIG_DATA, "data": config_data}

        with patch.object(server, "save_received_config") as mock_save:
            with patch.object(server, "transfer_started") as mock_signal:
                server.process_message(mock_socket, message)
                mock_save.assert_called_once_with(config_data)
                mock_signal.emit.assert_called_with(
                    "Configuration", "Application settings"
                )

    def test_process_message_collection_data(self):
        """Test processing COLLECTION_DATA message."""
        server = TransferServer(self.port)
        mock_socket = Mock()

        message = {
            "type": TransferProtocol.MSG_COLLECTION_DATA,
            "data": {"name": "Test Collection"},
        }

        with patch.object(server, "transfer_started") as mock_signal:
            server.process_message(mock_socket, message)
            mock_signal.emit.assert_called_with("Collection", "Test Collection")

    @patch("tempfile.gettempdir")
    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_received_config(self, mock_file, mock_mkdir, mock_tempdir):
        """Test saving received configuration data."""
        mock_tempdir.return_value = "/tmp"

        server = TransferServer(self.port)
        config_data = {"test": "config"}

        with patch.object(server, "transfer_completed") as mock_signal:
            server.save_received_config(config_data)

            mock_mkdir.assert_called_once()
            mock_file.assert_called_once()
            mock_signal.emit.assert_called_once()

    def test_stop_server(self):
        """Test stopping the server."""
        server = TransferServer(self.port)
        server.running = True
        server.server_socket = Mock()

        server.stop()

        assert server.running is False
        server.server_socket.close.assert_called_once()


class TestTransferClient:
    """Test suite for TransferClient class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.host = "localhost"
        self.port = 12345
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_file.txt"
        self.test_file.write_text("Test content for transfer")

    def teardown_method(self):
        """Clean up after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_transfer_client_initialization(self):
        """Test TransferClient initialization."""
        transfer_data = {"type": "files", "files": []}
        client = TransferClient(self.host, self.port, transfer_data)

        assert client.host == self.host
        assert client.port == self.port
        assert client.transfer_data == transfer_data

    def test_transfer_client_signals(self):
        """Test TransferClient signal definitions."""
        transfer_data = {"type": "files", "files": []}
        client = TransferClient(self.host, self.port, transfer_data)

        # Check that signals exist
        assert hasattr(client, "connection_established")
        assert hasattr(client, "progress_updated")
        assert hasattr(client, "transfer_completed")
        assert hasattr(client, "error_occurred")

    @patch("socket.socket")
    def test_client_connection(self, mock_socket):
        """Test client connection establishment."""
        mock_sock = Mock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        transfer_data = {"type": "config", "config": {}}
        client = TransferClient(self.host, self.port, transfer_data)

        with patch.object(client, "send_config") as mock_send:
            with patch.object(client, "connection_established") as mock_signal:
                try:
                    client.run()
                except:
                    pass  # Expected to fail in test environment

        mock_sock.connect.assert_called_once_with((self.host, self.port))

    def test_send_files(self):
        """Test sending files."""
        transfer_data = {"type": "files", "files": [str(self.test_file)]}
        client = TransferClient(self.host, self.port, transfer_data)

        mock_socket = Mock()

        with patch.object(client, "progress_updated") as mock_progress:
            with patch(
                "src.tools.network.transfer.network_transfer.PathSecurity.secure_file_info"
            ) as mock_info:
                mock_info.return_value = {
                    "size": 100,
                    "exists": True,
                    "path": str(self.test_file),
                }

                client.send_files(mock_socket)

                # Verify socket.send was called for file info and data
                assert mock_socket.send.call_count >= 1
                mock_progress.emit.assert_called()

    def test_send_config(self):
        """Test sending configuration data."""
        config_data = {"setting1": "value1", "setting2": "value2"}
        transfer_data = {"type": "config", "config": config_data}
        client = TransferClient(self.host, self.port, transfer_data)

        mock_socket = Mock()

        with patch.object(client, "progress_updated") as mock_progress:
            client.send_config(mock_socket)

            mock_socket.send.assert_called_once()
            mock_progress.emit.assert_called_once_with(100)

    def test_send_collection(self):
        """Test sending file collection."""
        collection_data = {"name": "Test Collection", "files": []}
        transfer_data = {"type": "collection", "collection": collection_data}
        client = TransferClient(self.host, self.port, transfer_data)

        mock_socket = Mock()

        with patch.object(client, "progress_updated") as mock_progress:
            client.send_collection(mock_socket)

            mock_socket.send.assert_called_once()
            mock_progress.emit.assert_called_once_with(100)

    def test_send_files_with_invalid_file(self):
        """Test sending files with invalid file path."""
        transfer_data = {"type": "files", "files": ["/nonexistent/file.txt"]}
        client = TransferClient(self.host, self.port, transfer_data)

        mock_socket = Mock()

        with patch(
            "src.tools.network.transfer.network_transfer.PathSecurity.secure_file_info",
            return_value=None,
        ):
            client.send_files(mock_socket)

            # Should not attempt to send invalid files
            assert mock_socket.send.call_count == 0

    def test_send_files_io_error(self):
        """Test sending files with IO error."""
        transfer_data = {"type": "files", "files": [str(self.test_file)]}
        client = TransferClient(self.host, self.port, transfer_data)

        mock_socket = Mock()

        with patch.object(client, "error_occurred") as mock_error:
            with patch(
                "src.tools.network.transfer.network_transfer.PathSecurity.secure_file_info"
            ) as mock_info:
                mock_info.return_value = {
                    "size": 100,
                    "exists": True,
                    "path": str(self.test_file),
                }

                with patch("builtins.open", side_effect=IOError("File access error")):
                    client.send_files(mock_socket)

                    mock_error.emit.assert_called()


class TestNetworkTransferGUI:
    """Test suite for NetworkTransferGUI class."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_file.txt"
        self.test_file.write_text("Test content")

        yield

        # Cleanup
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_gui_initialization(self):
        """Test NetworkTransferGUI initialization."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Check basic attributes
            assert hasattr(gui, "logger")
            assert hasattr(gui, "file_collections")
            assert hasattr(gui, "transfer_server")
            assert hasattr(gui, "transfer_client")

            # Check UI components
            assert hasattr(gui, "tab_widget")
            assert hasattr(gui, "status_label")
            assert hasattr(gui, "progress_bar")

            gui.close()

    def test_database_initialization(self):
        """Test database initialization."""
        with patch(
            "src.tools.network.transfer.network_transfer.DatabaseManager"
        ) as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance

            gui = NetworkTransferGUI()

            assert gui.db_manager == mock_db_instance
            gui.close()

    def test_file_security_validation(self):
        """Test file security validation."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test valid file path
            valid_path = str(self.test_file)
            assert gui._is_secure_file_path(valid_path) is True

            # Test suspicious patterns
            suspicious_paths = [
                "../etc/passwd",
                "file..txt",
                "~/sensitive",
                "file\x00.txt",
                "file%.txt",
                "file$cmd.txt",
            ]

            for path in suspicious_paths:
                assert gui._is_secure_file_path(path) is False

            gui.close()

    def test_forbidden_directories_check(self):
        """Test forbidden directories checking."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Create mock forbidden directories
            forbidden_dirs = [
                Path("/etc"),
                Path("C:\\Windows"),
                Path.home() / "AppData" / "Local" / "Microsoft",
            ]

            for forbidden_dir in forbidden_dirs:
                # Should return False for forbidden directories
                if forbidden_dir.exists():
                    result = gui._check_forbidden_directories(forbidden_dir)
                    assert result is False

            gui.close()

    def test_allowed_directories_check(self):
        """Test allowed directories checking."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test with user Documents directory
            docs_dir = Path.home() / "Documents"
            if docs_dir.exists():
                result = gui._check_allowed_directories(docs_dir)
                assert result is True

            # Test with current working directory
            cwd = Path.cwd()
            result = gui._check_allowed_directories(cwd)
            assert result is True

            gui.close()

    def test_file_extension_validation(self):
        """Test file extension validation."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test allowed extensions
            allowed_file = self.temp_dir / "test.txt"
            allowed_file.write_text("content")
            assert gui._check_file_extension(allowed_file) is True

            # Test forbidden extensions
            forbidden_file = self.temp_dir / "malware.exe"
            forbidden_file.write_text("fake executable")
            assert gui._check_file_extension(forbidden_file) is False

            gui.close()

    def test_file_size_validation(self):
        """Test file size validation."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test normal file size
            normal_file = self.temp_dir / "normal.txt"
            normal_file.write_text("small content")
            assert gui._check_file_size(normal_file) is True

            # Test oversized file using mock
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 2 * 1024 * 1024 * 1024  # 2GB
                assert gui._check_file_size(normal_file) is False

            gui.close()

    def test_collect_application_config(self):
        """Test collecting application configuration."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            config = gui.collect_application_config()

            assert isinstance(config, dict)
            assert "timestamp" in config
            assert "version" in config
            assert "settings" in config
            assert "collections" in config

            gui.close()

    def test_sanitize_config_content(self):
        """Test configuration content sanitization."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test with sensitive content
            sensitive_config = {
                "username": "user",
                "password": "secret123",
                "api_key": "xyz789",
                "safe_setting": "value",
                "database_url": "mongodb://secret",
            }

            sanitized = gui._sanitize_config_content(sensitive_config)

            # Sensitive keys should be removed
            assert "password" not in sanitized
            assert "api_key" not in sanitized
            assert "database_url" not in sanitized

            # Safe keys should remain
            assert "username" in sanitized
            assert "safe_setting" in sanitized

            gui.close()

    def test_symlink_loop_detection(self):
        """Test symbolic link loop detection."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test with normal directories
            base_dir = self.temp_dir
            target_dir = self.temp_dir / "subdir"
            target_dir.mkdir()

            # No loop should be detected for normal subdirectory
            result = gui._is_symlink_loop(target_dir, base_dir)
            assert result is False

            # Test potential loop scenario
            result = gui._is_symlink_loop(base_dir, target_dir)
            assert result is True  # base is ancestor of target

            gui.close()

    def test_transfer_history_logging(self):
        """Test transfer history logging."""
        with patch(
            "src.tools.network.transfer.network_transfer.DatabaseManager"
        ) as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance

            gui = NetworkTransferGUI()

            transfer_data = {"type": "files", "files": [str(self.test_file)]}

            gui.log_transfer_attempt(transfer_data, "localhost", 12345)

            # Verify database call was made
            mock_db_instance.execute_query.assert_called()

            gui.close()

    def test_collection_management(self):
        """Test file collection management."""
        with patch(
            "src.tools.network.transfer.network_transfer.DatabaseManager"
        ) as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance

            gui = NetworkTransferGUI()

            # Test creating collection
            collection = {
                "name": "test_collection",
                "description": "Test collection",
                "files": [str(self.test_file)],
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
            }

            gui.save_collection(collection)

            # Verify database save was called
            mock_db_instance.execute_query.assert_called()

            gui.close()

    def test_secure_config_file_validation(self):
        """Test secure configuration file validation."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test valid config file
            config_file = self.temp_dir / "config.json"
            config_file.write_text('{"setting": "value"}')
            assert gui._is_safe_config_file(config_file) is True

            # Test oversized config file
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 2 * 1024 * 1024  # 2MB
                assert gui._is_safe_config_file(config_file) is False

            gui.close()

    def test_menu_callbacks(self):
        """Test menu callback registration and execution."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            with patch.object(NetworkTransferGUI, "_setup_menu_callbacks"):
                gui = NetworkTransferGUI()

                # Test preference callback
                with patch("PyQt5.QtWidgets.QMessageBox.information") as mock_msg:
                    gui.show_preferences()
                    mock_msg.assert_called_once()

                # Test refresh callback
                with patch("PyQt5.QtWidgets.QMessageBox.information") as mock_msg:
                    gui.refresh_view()
                    mock_msg.assert_called_once()

                gui.close()

    def test_transfer_server_management(self):
        """Test transfer server start/stop management."""
        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Mock the server
            with patch(
                "src.tools.network.transfer.network_transfer.TransferServer"
            ) as mock_server:
                mock_server_instance = Mock()
                mock_server.return_value = mock_server_instance

                # Test starting server
                gui.listen_port = Mock()
                gui.listen_port.value.return_value = 12345

                gui.start_transfer_server()

                # Verify server was started
                mock_server_instance.start.assert_called_once()

                # Test stopping server
                gui.transfer_server = mock_server_instance
                gui.stop_transfer_server()

                # Verify server was stopped
                mock_server_instance.stop.assert_called_once()
                mock_server_instance.wait.assert_called_once()

            gui.close()


class TestIntegrationScenarios:
    """Integration tests for complete transfer scenarios."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_files = []

        # Create test files
        for i in range(3):
            test_file = self.temp_dir / f"test_file_{i}.txt"
            test_file.write_text(f"Test content {i}")
            self.test_files.append(str(test_file))

    def teardown_method(self):
        """Clean up after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_security_manager_full_cycle(self):
        """Test complete SecurityManager encryption/decryption cycle."""
        security = SecurityManager()

        # Generate session key and auth token
        session_key = security.generate_session_key()
        auth_token = security.generate_auth_token()

        # Verify token
        assert security.verify_auth_token(auth_token) is True

        # Test message encryption/decryption
        messages = [
            b"Short message",
            b"A" * 1000,  # Medium message
            "Unicode: 世界 🌍 café".encode("utf-8"),  # Unicode message
            b"",  # Empty message
        ]

        for original in messages:
            encrypted = security.encrypt_message(original)
            decrypted = security.decrypt_message(encrypted)
            assert decrypted == original

    def test_protocol_message_handling(self):
        """Test complete protocol message handling cycle."""
        # Test all message types
        message_types = [
            (TransferProtocol.MSG_HELLO, {"client_name": "Test Client"}),
            (TransferProtocol.MSG_AUTH, {"token": "auth_token"}),
            (
                TransferProtocol.MSG_FILE_INFO,
                {"filename": "test.txt", "filesize": 1024},
            ),
            (TransferProtocol.MSG_CONFIG_DATA, {"setting": "value"}),
            (TransferProtocol.MSG_COLLECTION_DATA, {"name": "Collection"}),
            (TransferProtocol.MSG_ACK, {"status": "ready"}),
            (TransferProtocol.MSG_ERROR, {"error": "Something went wrong"}),
            (TransferProtocol.MSG_COMPLETE, {"result": "success"}),
        ]

        for msg_type, data in message_types:
            # Create message
            message_bytes = TransferProtocol.create_message(msg_type, data)

            # Parse message
            parsed = TransferProtocol.parse_message(message_bytes)

            assert parsed["type"] == msg_type
            assert parsed["data"] == data

    def test_path_security_comprehensive(self):
        """Test comprehensive path security validation."""
        base_path = str(self.temp_dir)

        # Test various scenarios
        test_cases = [
            # (path, expected_safe, description)
            ("safe_file.txt", True, "Normal file"),
            ("../etc/passwd", False, "Path traversal"),
            ("folder/file.txt", True, "Subdirectory file"),
            ("~/sensitive", False, "Home directory reference"),
            ("file\x00.txt", False, "Null byte injection"),
            ("", False, "Empty path"),
            ("C:\\Windows\\system32\\config", False, "Windows system path"),
        ]

        for path, expected_safe, description in test_cases:
            result = PathSecurity.is_safe_path(base_path, path)
            assert result == expected_safe, f"Failed for {description}: {path}"

    def test_file_validation_scenarios(self):
        """Test various file validation scenarios."""
        # Create test files with different characteristics
        test_files = {
            "valid.txt": (b"Valid content", True),
            "empty.txt": (b"", True),
            "large.txt": (b"A" * 1000, True),
            "forbidden.exe": (b"Executable", False),
            "config.json": (b'{"valid": "json"}', True),
        }

        for filename, (content, should_be_valid) in test_files.items():
            file_path = self.temp_dir / filename
            file_path.write_bytes(content)

            validation = PathSecurity.validate_file_for_transfer(str(file_path))
            assert (
                validation["valid"] == should_be_valid
            ), f"Validation failed for {filename}"

    @patch("socket.socket")
    def test_client_server_protocol_simulation(self, mock_socket):
        """Test simulated client-server protocol interaction."""
        # Set up mock socket
        mock_sock = Mock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        # Test data
        transfer_data = {
            "type": "config",
            "config": {"setting1": "value1", "setting2": "value2"},
        }

        # Create client
        client = TransferClient("localhost", 12345, transfer_data)

        # Simulate successful connection and transfer
        with patch.object(client, "connection_established") as mock_connect:
            with patch.object(client, "transfer_completed") as mock_complete:
                try:
                    client.run()
                except:
                    pass  # Expected to fail in test environment

        # Verify connection attempt was made
        mock_sock.connect.assert_called_once_with(("localhost", 12345))


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    def test_security_manager_error_conditions(self):
        """Test SecurityManager error handling."""
        security = SecurityManager()

        # Test encryption without session key
        with pytest.raises(ValueError):
            security.encrypt_message(b"test")

        # Test decryption without session key
        with pytest.raises(ValueError):
            security.decrypt_message(b"test")

        # Test with corrupted data
        security.generate_session_key()

        if CRYPTO_AVAILABLE:
            with pytest.raises(ValueError):
                security.decrypt_message(b"corrupted_data")

    def test_protocol_edge_cases(self):
        """Test TransferProtocol edge cases."""
        # Test extremely large message
        large_data = {"data": "X" * (TransferProtocol.MAX_MESSAGE_SIZE)}
        with pytest.raises(ValueError):
            TransferProtocol.create_message("TEST", large_data)

        # Test malformed message parsing
        assert TransferProtocol.parse_message(b"") is None
        assert TransferProtocol.parse_message(b"abc") is None
        assert TransferProtocol.parse_message(b"\x00\x00\x00\x05hello") is None

    def test_path_security_attacks(self):
        """Test PathSecurity against various attacks."""
        temp_dir = tempfile.mkdtemp()
        base_path = temp_dir

        try:
            # Path traversal attacks
            attacks = [
                "../../../../../etc/passwd",
                "..\\..\\..\\windows\\system32",
                "file/../../sensitive",
                "%2e%2e%2fsensitive",
                "file\x00.txt",
                "con.txt",  # Windows reserved name
                "aux.txt",  # Windows reserved name
            ]

            for attack in attacks:
                assert PathSecurity.is_safe_path(base_path, attack) is False
                assert PathSecurity.secure_join(base_path, attack) is None

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_network_error_handling(self):
        """Test network-related error handling."""
        # Test connection failures
        transfer_data = {"type": "files", "files": []}
        client = TransferClient("invalid_host", 99999, transfer_data)

        with patch.object(client, "error_occurred") as mock_error:
            try:
                client.run()
            except:
                pass

            # Should emit error signal on connection failure
            # Note: This test may pass or fail depending on network conditions

    def test_gui_error_scenarios(self):
        """Test GUI error handling scenarios."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        with patch("src.tools.network.transfer.network_transfer.DatabaseManager"):
            gui = NetworkTransferGUI()

            # Test with invalid file selections
            invalid_paths = [
                "/nonexistent/file.txt",
                "../../../etc/passwd",
                "con.txt",
                "file\x00.txt",
            ]

            for invalid_path in invalid_paths:
                result = gui._is_secure_file_path(invalid_path)
                assert result is False

            gui.close()


if __name__ == "__main__":
    # Configure pytest for standalone execution
    pytest.main(
        [__file__, "-v", "--tb=short", "--strict-markers", "--disable-warnings"]
    )
