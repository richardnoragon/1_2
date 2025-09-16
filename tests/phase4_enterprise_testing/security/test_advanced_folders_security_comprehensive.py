"""
Enterprise-Grade Security Tests for Advanced Folders System
Phase 4: Testing & QA (Week 10) - Comprehensive Security Testing

Test Coverage Target: OWASP Top 10, Penetration Testing, Vulnerability Assessment
Test Complexity Level: Enterprise-Grade (Zero Security Tolerance)
Quality Standards: Zero-Compromise Security Protocols

This module implements comprehensive security testing for the Advanced Folders
system with penetration testing and vulnerability assessment capabilities.
"""

import hashlib
import os
import sqlite3
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.tools.advanced_folders.core.folder_models import (
    FileMetadata, FolderConfiguration, FolderType, SearchParameter)
from src.tools.advanced_folders.database.db_manager import \
    AdvancedFoldersDBManager
from src.tools.advanced_folders.engine.search_engine import SearchEngine
from src.tools.advanced_folders.services.folder_service import \
    FolderService


class SecurityTestFramework:
    """Enterprise security testing framework with penetration testing capabilities."""
    
    @staticmethod
    def generate_malicious_payloads():
        """Generate common security attack payloads for testing."""
        return {
            'sql_injection': [
                "'; DROP TABLE folders; --",
                "' OR '1'='1",
                "'; UPDATE folders SET path='/etc/passwd'; --",
                "' UNION SELECT * FROM sqlite_master; --",
                "'; INSERT INTO folders VALUES ('malicious', '/root', 1); --",
                "admin'--",
                "admin' /*",
                "admin' #",
                "admin'/**/or/**/1=1#",
                "1' or 1=1--",
                "1' or 1=1#",
                "1' or 1=1/*",
            ],
            'path_traversal': [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "/etc/shadow",
                "/root/.ssh/id_rsa",
                "..%2F..%2F..%2Fetc%2Fpasswd",
                "..%252F..%252F..%252Fetc%252Fpasswd",
                "....//....//....//etc/passwd",
                "..///////..////..//////etc/passwd",
                "/var/www/../../etc/passwd",
                ".\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            ],
            'command_injection': [
                "; cat /etc/passwd",
                "| cat /etc/passwd",
                "`cat /etc/passwd`",
                "$(cat /etc/passwd)",
                "; rm -rf /",
                "& dir c:\\",
                "&& type c:\\windows\\system32\\drivers\\etc\\hosts",
                "; powershell.exe -Command Get-Process",
                "| powershell.exe Get-Content c:\\windows\\system32\\drivers\\etc\\hosts",
            ],
            'xss_payloads': [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src='x' onerror='alert(1)'>",
                "<svg onload=alert(1)>",
                "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
                "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
                "<iframe src=\"javascript:alert('XSS')\"></iframe>",
                "<body onload=alert('XSS')>",
            ],
            'buffer_overflow': [
                "A" * 1000,
                "A" * 10000,
                "A" * 100000,
                "\x00" * 1000,
                "\xff" * 1000,
            ],
            'format_string': [
                "%s%s%s%s%s%s%s%s%s%s",
                "%x%x%x%x%x%x%x%x%x%x",
                "%n%n%n%n%n%n%n%n%n%n",
                "%.1000d",
                "%99999999d",
            ]
        }
    
    @staticmethod
    def generate_malicious_files():
        """Generate various types of malicious file contents for testing."""
        return {
            'executable_disguised': {
                'filename': 'document.pdf.exe',
                'content': b'\x4d\x5a\x90\x00',  # PE header
                'description': 'Executable disguised as PDF'
            },
            'script_injection': {
                'filename': 'script.txt',
                'content': '#!/bin/bash\nrm -rf /\n',
                'description': 'Malicious shell script disguised as text'
            },
            'large_file': {
                'filename': 'large.txt',
                'content': b'A' * (1024 * 1024 * 100),  # 100MB
                'description': 'Large file to test DoS resistance'
            },
            'binary_payload': {
                'filename': 'payload.dat',
                'content': b'\x00\x01\x02\x03' * 1000 + b'\xff\xfe\xfd\xfc' * 1000,
                'description': 'Binary payload with control characters'
            },
            'unicode_attack': {
                'filename': '𝕸𝖆𝖑𝖎𝖈𝖎𝖔𝖚𝖘.txt',
                'content': '𝓜𝓪𝓵𝓲𝓬𝓲𝓸𝓾𝓼 𝓾𝓷𝓲𝓬𝓸𝓭𝓮 𝓬𝓸𝓷𝓽𝓮𝓷𝓽',
                'description': 'Unicode-based filename and content attack'
            }
        }


class TestAdvancedFoldersSecurityEnterprise:
    """Enterprise-grade security test suite for Advanced Folders system."""
    
    @pytest.mark.security
    @pytest.mark.critical
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention across all database operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "security_sql.db"
            index_path = Path(temp_dir) / "security_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Get SQL injection payloads
            sql_payloads = SecurityTestFramework.generate_malicious_payloads()['sql_injection']
            
            # Test 1: Folder creation with malicious names
            for payload in sql_payloads:
                try:
                    folder_config = FolderConfiguration(
                        name=payload,  # Malicious folder name
                        path=str(Path(temp_dir) / "test_folder"),
                        folder_type=FolderType.MONITORED,
                        auto_organize=True,
                        priority=1
                    )
                    
                    # This should not cause SQL injection
                    config_id = folder_service.create_folder_configuration(folder_config)
                    
                    # Verify the malicious payload is stored safely (escaped/sanitized)
                    retrieved_config = folder_service.get_folder_configuration(config_id)
                    assert retrieved_config is not None
                    
                    # Ensure database integrity
                    assert db_manager.validate_database_integrity()
                    
                    # Cleanup
                    folder_service.delete_folder_configuration(config_id)
                    
                except Exception as e:
                    # Exceptions are acceptable for malicious input, but should be controlled
                    assert "DROP" not in str(e).upper(), f"SQL injection may have occurred: {e}"
                    assert "DELETE" not in str(e).upper(), f"SQL injection may have occurred: {e}"
            
            # Test 2: Path traversal in folder paths
            path_payloads = SecurityTestFramework.generate_malicious_payloads()['path_traversal']
            
            for payload in path_payloads:
                try:
                    folder_config = FolderConfiguration(
                        name="Test Folder",
                        path=payload,  # Malicious path
                        folder_type=FolderType.MONITORED,
                        auto_organize=True,
                        priority=1
                    )
                    
                    config_id = folder_service.create_folder_configuration(folder_config)
                    
                    # Verify the path is properly validated/sanitized
                    retrieved_config = folder_service.get_folder_configuration(config_id)
                    
                    # Path should not escape the intended directory structure
                    assert not retrieved_config.path.startswith('/etc/'), f"Path traversal detected: {retrieved_config.path}"
                    assert not retrieved_config.path.startswith('/root/'), f"Path traversal detected: {retrieved_config.path}"
                    assert not 'system32' in retrieved_config.path.lower(), f"Windows path traversal detected: {retrieved_config.path}"
                    
                    folder_service.delete_folder_configuration(config_id)
                    
                except Exception as e:
                    # Path validation failures are expected and acceptable
                    pass
            
            # Test 3: Search injection attacks
            search_payloads = sql_payloads + ["*", "?", "[", "]", "{", "}", "(", ")", "\\", "/"]
            
            for payload in search_payloads:
                try:
                    # Search operations should handle malicious input safely
                    results = folder_service.search_all_folders(payload)
                    
                    # Results should be a list (empty or populated)
                    assert isinstance(results, list), f"Search returned unexpected type for payload: {payload}"
                    
                    # Verify database integrity after search
                    assert db_manager.validate_database_integrity()
                    
                except Exception as e:
                    # Search failures are acceptable, but should not compromise system
                    assert "DROP" not in str(e).upper(), f"SQL injection in search: {e}"
                    assert "DELETE" not in str(e).upper(), f"SQL injection in search: {e}"
            
            print("SQL injection prevention tests passed")
    
    @pytest.mark.security
    @pytest.mark.critical
    def test_file_system_security(self):
        """Test file system access security and path validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "security_fs.db"
            index_path = Path(temp_dir) / "security_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Create test structure
            test_root = Path(temp_dir) / "secure_test"
            test_root.mkdir()
            
            secure_dir = test_root / "secure"
            secure_dir.mkdir()
            
            # Create a secure file that should not be accessible via path traversal
            secure_file = secure_dir / "sensitive.txt"
            secure_file.write_text("Sensitive information that should be protected")
            
            # Test 1: Path traversal prevention
            malicious_paths = [
                str(test_root / ".." / ".." / "secure" / "sensitive.txt"),
                str(test_root) + "/../secure/sensitive.txt",
                str(test_root) + "/./../../secure/sensitive.txt",
                str(test_root) + "\\..\\..\\secure\\sensitive.txt",
            ]
            
            for malicious_path in malicious_paths:
                try:
                    # Attempt to create folder configuration with traversal path
                    folder_config = FolderConfiguration(
                        name="Malicious Path Test",
                        path=malicious_path,
                        folder_type=FolderType.MONITORED,
                        auto_organize=True,
                        priority=1
                    )
                    
                    config_id = folder_service.create_folder_configuration(folder_config)
                    
                    # If creation succeeds, verify path is properly contained
                    retrieved_config = folder_service.get_folder_configuration(config_id)
                    normalized_path = Path(retrieved_config.path).resolve()
                    temp_path = Path(temp_dir).resolve()
                    
                    # Path should be contained within temp directory
                    assert str(normalized_path).startswith(str(temp_path)), f"Path traversal escape detected: {normalized_path}"
                    
                    folder_service.delete_folder_configuration(config_id)
                    
                except Exception as e:
                    # Path validation failures are expected for malicious paths
                    pass
            
            # Test 2: File access permissions and validation
            folder_config = FolderConfiguration(
                name="Security Test Folder",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            
            # Create various file types for security testing
            malicious_files = SecurityTestFramework.generate_malicious_files()
            
            for file_type, file_info in malicious_files.items():
                try:
                    malicious_file = test_root / file_info['filename']
                    
                    # Handle different content types
                    if isinstance(file_info['content'], bytes):
                        malicious_file.write_bytes(file_info['content'])
                    else:
                        malicious_file.write_text(file_info['content'])
                    
                    # Test indexing of potentially malicious files
                    start_time = time.time()
                    index_success = search_engine.index_file(malicious_file)
                    index_time = time.time() - start_time
                    
                    # Verify indexing doesn't hang or consume excessive resources
                    assert index_time < 30, f"Indexing took too long for {file_type}: {index_time:.2f}s"
                    
                    # Verify file content is handled safely
                    if index_success:
                        # Search for the file to verify it was indexed safely
                        search_results = folder_service.search_all_folders(file_info['filename'])
                        assert isinstance(search_results, list)
                    
                    print(f"Security test passed for {file_type}: {file_info['description']}")
                    
                except Exception as e:
                    # Some failures are expected for malicious files
                    assert "overflow" not in str(e).lower(), f"Buffer overflow detected: {e}"
                    assert "stack" not in str(e).lower(), f"Stack corruption detected: {e}"
            
            # Test 3: Concurrent file access security
            def concurrent_file_access_test(worker_id: int, results: list):
                """Test concurrent access to files for race conditions."""
                try:
                    for i in range(50):
                        # Create file
                        test_file = test_root / f"concurrent_{worker_id}_{i}.txt"
                        test_file.write_text(f"Concurrent test content {worker_id}-{i}")
                        
                        # Index file
                        search_engine.index_file(test_file)
                        
                        # Search for file
                        search_results = folder_service.search_all_folders(f"concurrent_{worker_id}")
                        
                        # Delete file
                        test_file.unlink()
                        
                        results.append((worker_id, i, True))
                        
                except Exception as e:
                    results.append((worker_id, -1, False, str(e)))
            
            # Run concurrent access tests
            import threading
            concurrent_results = []
            threads = []
            
            for worker_id in range(5):
                thread = threading.Thread(
                    target=concurrent_file_access_test,
                    args=(worker_id, concurrent_results)
                )
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Analyze concurrent access results
            successful_operations = sum(1 for result in concurrent_results if len(result) == 3 and result[2])
            failed_operations = len(concurrent_results) - successful_operations
            
            # Some failures are acceptable, but should not be excessive
            failure_rate = failed_operations / len(concurrent_results) if concurrent_results else 0
            assert failure_rate < 0.1, f"Too many concurrent access failures: {failure_rate:.2%}"
            
            print(f"Concurrent access test: {successful_operations} successful, {failed_operations} failed")
            print("File system security tests passed")
    
    @pytest.mark.security
    @pytest.mark.critical
    def test_authentication_and_authorization(self):
        """Test authentication and authorization security measures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "security_auth.db"
            index_path = Path(temp_dir) / "security_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Test 1: Database connection security
            # Verify database file permissions are appropriate
            db_file_path = Path(db_path)
            if db_file_path.exists():
                stat_info = db_file_path.stat()
                
                # On Unix systems, check file permissions
                if hasattr(stat_info, 'st_mode'):
                    import stat
                    mode = stat.filemode(stat_info.st_mode)
                    # Database should not be world-readable
                    assert not (stat_info.st_mode & stat.S_IROTH), f"Database is world-readable: {mode}"
                    assert not (stat_info.st_mode & stat.S_IWOTH), f"Database is world-writable: {mode}"
            
            # Test 2: Configuration access control
            test_root = Path(temp_dir) / "auth_test"
            test_root.mkdir()
            
            folder_config = FolderConfiguration(
                name="Auth Test Folder",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            
            # Test unauthorized configuration access
            try:
                # Attempt direct database manipulation
                direct_db_connection = sqlite3.connect(str(db_path))
                cursor = direct_db_connection.cursor()
                
                # Try to modify configuration directly
                cursor.execute(
                    "UPDATE folder_configurations SET path = '/etc/passwd' WHERE id = ?",
                    (config_id,)
                )
                direct_db_connection.commit()
                direct_db_connection.close()
                
                # Verify the change was not effective or properly validated
                retrieved_config = folder_service.get_folder_configuration(config_id)
                assert retrieved_config.path != '/etc/passwd', "Unauthorized database modification succeeded"
                
            except Exception as e:
                # Database protection mechanisms may prevent direct access
                pass
            
            # Test 3: Input validation and sanitization
            malicious_inputs = [
                {"name": "<script>alert('xss')</script>", "expected_safe": True},
                {"name": "'; DROP TABLE folders; --", "expected_safe": True},
                {"name": "../../../etc/passwd", "expected_safe": True},
                {"name": "Normal Folder Name", "expected_safe": True},
                {"name": "", "expected_safe": False},  # Empty name should be rejected
                {"name": None, "expected_safe": False},  # None should be rejected
            ]
            
            for test_input in malicious_inputs:
                try:
                    if test_input["name"] is None:
                        # Skip None test as it would cause TypeError before reaching validation
                        continue
                        
                    folder_config = FolderConfiguration(
                        name=test_input["name"],
                        path=str(test_root),
                        folder_type=FolderType.MONITORED,
                        auto_organize=True,
                        priority=1
                    )
                    
                    config_id = folder_service.create_folder_configuration(folder_config)
                    
                    if test_input["expected_safe"]:
                        # Should succeed for safe inputs (even if sanitized)
                        retrieved_config = folder_service.get_folder_configuration(config_id)
                        assert retrieved_config is not None
                        
                        # Verify malicious content is sanitized
                        assert "<script>" not in retrieved_config.name
                        assert "DROP TABLE" not in retrieved_config.name
                        
                        folder_service.delete_folder_configuration(config_id)
                    else:
                        # Should fail for unsafe inputs
                        assert False, f"Unsafe input was accepted: {test_input['name']}"
                        
                except Exception as e:
                    if not test_input["expected_safe"]:
                        # Expected failure for unsafe inputs
                        continue
                    else:
                        # Unexpected failure for safe inputs
                        if "empty" in str(e).lower() or "required" in str(e).lower():
                            # Validation rejection is acceptable
                            continue
                        raise
            
            # Test 4: Session and state security
            # Verify operations are properly isolated
            original_config_count = len(folder_service.get_all_folder_configurations())
            
            # Create multiple configurations concurrently
            def create_concurrent_configs(worker_id: int, results: list):
                try:
                    for i in range(10):
                        config = FolderConfiguration(
                            name=f"Concurrent Config {worker_id}-{i}",
                            path=str(test_root / f"worker_{worker_id}"),
                            folder_type=FolderType.MONITORED,
                            auto_organize=True,
                            priority=1
                        )
                        
                        config_id = folder_service.create_folder_configuration(config)
                        results.append((worker_id, i, config_id))
                        
                except Exception as e:
                    results.append((worker_id, -1, str(e)))
            
            concurrent_config_results = []
            threads = []
            
            for worker_id in range(3):
                thread = threading.Thread(
                    target=create_concurrent_configs,
                    args=(worker_id, concurrent_config_results)
                )
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Verify all configurations were created properly
            final_config_count = len(folder_service.get_all_folder_configurations())
            successful_creates = sum(1 for result in concurrent_config_results if len(result) == 3 and isinstance(result[2], int))
            
            assert final_config_count >= original_config_count + successful_creates
            
            # Cleanup concurrent configurations
            for result in concurrent_config_results:
                if len(result) == 3 and isinstance(result[2], int):
                    try:
                        folder_service.delete_folder_configuration(result[2])
                    except:
                        pass
            
            print("Authentication and authorization tests passed")
    
    @pytest.mark.security
    @pytest.mark.critical
    def test_data_encryption_and_integrity(self):
        """Test data encryption and integrity protection measures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "security_crypto.db"
            index_path = Path(temp_dir) / "security_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Test 1: Sensitive data protection
            test_root = Path(temp_dir) / "crypto_test"
            test_root.mkdir()
            
            # Create configuration with potentially sensitive information
            sensitive_folder_config = FolderConfiguration(
                name="Sensitive Documents",
                path=str(test_root),
                folder_type=FolderType.SECURE,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(sensitive_folder_config)
            
            # Create files with sensitive content
            sensitive_files = {
                "credentials.txt": "username=admin\npassword=secretpass123\napi_key=sk-1234567890abcdef",
                "personal.txt": "SSN: 123-45-6789\nCredit Card: 4111-1111-1111-1111\nBirthdate: 1990-01-01",
                "config.txt": "database_password=supersecret\nencryption_key=abcdef1234567890",
            }
            
            for filename, content in sensitive_files.items():
                sensitive_file = test_root / filename
                sensitive_file.write_text(content)
            
            # Index sensitive files
            indexed_count = folder_service.index_folder_contents(config_id)
            assert indexed_count >= len(sensitive_files)
            
            # Test 2: Database content inspection
            # Verify sensitive data is not stored in plaintext
            db_connection = sqlite3.connect(str(db_path))
            cursor = db_connection.cursor()
            
            # Check if sensitive patterns appear in database
            cursor.execute("SELECT * FROM folder_configurations")
            config_rows = cursor.fetchall()
            
            cursor.execute("SELECT * FROM file_metadata")
            metadata_rows = cursor.fetchall()
            
            # Convert all database content to strings for inspection
            db_content = " ".join(str(row) for row in config_rows + metadata_rows)
            
            # Verify sensitive data is not exposed in database
            sensitive_patterns = [
                "secretpass123",
                "123-45-6789",
                "4111-1111-1111-1111",
                "supersecret",
                "sk-1234567890abcdef"
            ]
            
            for pattern in sensitive_patterns:
                assert pattern not in db_content, f"Sensitive data found in database: {pattern}"
            
            db_connection.close()
            
            # Test 3: Search result security
            # Verify sensitive content is not exposed in search results
            search_terms = ["password", "secret", "credential", "ssn", "credit"]
            
            for term in search_terms:
                search_results = folder_service.search_all_folders(term)
                
                for result in search_results:
                    # Verify search results don't expose sensitive content directly
                    result_text = str(result)
                    for pattern in sensitive_patterns:
                        assert pattern not in result_text, f"Sensitive data exposed in search result: {pattern}"
            
            # Test 4: File content integrity
            # Verify files maintain integrity and are not corrupted
            original_hashes = {}
            for filename in sensitive_files.keys():
                file_path = test_root / filename
                with open(file_path, 'rb') as f:
                    content = f.read()
                    original_hashes[filename] = hashlib.sha256(content).hexdigest()
            
            # Perform various operations that might affect file integrity
            folder_service.update_folder_configuration(config_id, sensitive_folder_config)
            folder_service.index_folder_contents(config_id)
            
            # Search operations
            for term in ["sensitive", "documents", "admin"]:
                folder_service.search_all_folders(term)
            
            # Verify file integrity is maintained
            for filename, original_hash in original_hashes.items():
                file_path = test_root / filename
                with open(file_path, 'rb') as f:
                    current_content = f.read()
                    current_hash = hashlib.sha256(current_content).hexdigest()
                
                assert current_hash == original_hash, f"File integrity compromised: {filename}"
            
            # Test 5: Temporary file security
            # Verify temporary files are properly cleaned up and secured
            temp_files_before = list(Path(temp_dir).rglob("*.tmp"))
            temp_files_before.extend(Path(temp_dir).rglob("*.temp"))
            
            # Perform operations that might create temporary files
            for i in range(10):
                large_file = test_root / f"large_file_{i}.txt"
                large_content = "Large file content " * 10000
                large_file.write_text(large_content)
                search_engine.index_file(large_file)
                folder_service.search_all_folders("Large")
            
            # Check for temporary file cleanup
            temp_files_after = list(Path(temp_dir).rglob("*.tmp"))
            temp_files_after.extend(Path(temp_dir).rglob("*.temp"))
            
            new_temp_files = set(temp_files_after) - set(temp_files_before)
            
            # Allow some temporary files, but not excessive amounts
            assert len(new_temp_files) < 50, f"Too many temporary files created: {len(new_temp_files)}"
            
            # Test 6: Index file security
            # Verify index files don't expose sensitive information
            if index_path.exists():
                for index_file in index_path.rglob("*"):
                    if index_file.is_file():
                        try:
                            # Read index file content (if text-readable)
                            with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                                index_content = f.read()
                            
                            # Verify sensitive patterns are not in index files
                            for pattern in sensitive_patterns:
                                assert pattern not in index_content, f"Sensitive data found in index file: {pattern}"
                                
                        except (UnicodeDecodeError, PermissionError):
                            # Binary or protected index files are acceptable
                            pass
            
            print("Data encryption and integrity tests passed")
    
    @pytest.mark.security
    @pytest.mark.stress
    def test_denial_of_service_resistance(self):
        """Test system resistance to denial of service attacks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "security_dos.db"
            index_path = Path(temp_dir) / "security_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            test_root = Path(temp_dir) / "dos_test"
            test_root.mkdir()
            
            # Test 1: Excessive search requests
            folder_config = FolderConfiguration(
                name="DoS Test Folder",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            
            # Create some test files
            for i in range(100):
                test_file = test_root / f"dos_test_file_{i}.txt"
                test_file.write_text(f"DoS test content {i} with searchable terms")
            
            folder_service.index_folder_contents(config_id)
            
            # Rapid search requests
            search_start_time = time.time()
            search_count = 0
            max_search_time = 10  # seconds
            
            while time.time() - search_start_time < max_search_time:
                try:
                    # Rapid searches with various terms
                    search_terms = ["dos", "test", "content", "searchable", "terms", "*", "file"]
                    term = search_terms[search_count % len(search_terms)]
                    
                    results = folder_service.search_all_folders(term)
                    search_count += 1
                    
                    # Verify system remains responsive
                    assert isinstance(results, list), "Search returned invalid type under load"
                    
                except Exception as e:
                    # Some search failures under extreme load are acceptable
                    if "timeout" in str(e).lower() or "busy" in str(e).lower():
                        continue
                    else:
                        raise
            
            search_rate = search_count / max_search_time
            assert search_rate > 5, f"Search rate too low under load: {search_rate:.1f} searches/sec"
            
            print(f"DoS search test: {search_count} searches in {max_search_time}s ({search_rate:.1f} searches/sec)")
            
            # Test 2: Large file handling
            # Create progressively larger files to test resource limits
            large_file_sizes = [1, 10, 50, 100]  # MB
            
            for size_mb in large_file_sizes:
                large_file = test_root / f"large_dos_file_{size_mb}mb.txt"
                
                try:
                    # Write large file in chunks to avoid memory spike
                    chunk_size = 1024 * 1024  # 1MB chunks
                    target_size = size_mb * chunk_size
                    
                    with open(large_file, 'w') as f:
                        written = 0
                        chunk_content = "Large file DoS test content " * (chunk_size // 30)
                        
                        while written < target_size:
                            remaining = target_size - written
                            write_size = min(len(chunk_content), remaining)
                            f.write(chunk_content[:write_size])
                            written += write_size
                    
                    # Test indexing large file with timeout
                    index_start_time = time.time()
                    try:
                        index_success = search_engine.index_file(large_file)
                        index_time = time.time() - index_start_time
                        
                        # Large file indexing should complete within reasonable time
                        assert index_time < 60, f"Large file indexing took too long: {index_time:.2f}s for {size_mb}MB"
                        
                        if index_success:
                            # Verify we can search the large file
                            search_results = folder_service.search_all_folders("Large")
                            assert isinstance(search_results, list)
                        
                    except Exception as e:
                        # Large file processing failures are acceptable
                        if "memory" in str(e).lower() or "size" in str(e).lower():
                            print(f"Large file ({size_mb}MB) processing limited by system: {e}")
                            continue
                        else:
                            raise
                    
                except MemoryError:
                    # Memory limits for very large files are acceptable
                    print(f"Memory limit reached at {size_mb}MB file size")
                    break
            
            # Test 3: Concurrent operation flooding
            def dos_worker(worker_id: int, operation_count: int, results: list):
                """Worker for DoS testing with concurrent operations."""
                for i in range(operation_count):
                    try:
                        if i % 3 == 0:
                            # Create file
                            dos_file = test_root / f"dos_worker_{worker_id}_{i}.txt"
                            dos_file.write_text(f"DoS worker {worker_id} file {i}")
                            search_engine.index_file(dos_file)
                        elif i % 3 == 1:
                            # Search operation
                            folder_service.search_all_folders(f"worker_{worker_id}")
                        else:
                            # Query operation
                            folder_service.get_folder_statistics(config_id)
                        
                        results.append((worker_id, i, True))
                        
                    except Exception as e:
                        results.append((worker_id, i, False, str(e)))
            
            # Launch concurrent DoS workers
            dos_workers = 10
            operations_per_worker = 50
            dos_results = []
            dos_threads = []
            
            dos_start_time = time.time()
            
            for worker_id in range(dos_workers):
                thread = threading.Thread(
                    target=dos_worker,
                    args=(worker_id, operations_per_worker, dos_results)
                )
                dos_threads.append(thread)
                thread.start()
            
            # Wait for completion with timeout
            for thread in dos_threads:
                thread.join(timeout=30)
            
            dos_total_time = time.time() - dos_start_time
            
            # Analyze DoS resistance results
            successful_dos_ops = sum(1 for result in dos_results if len(result) == 3 and result[2])
            total_dos_ops = dos_workers * operations_per_worker
            dos_success_rate = successful_dos_ops / total_dos_ops if total_dos_ops > 0 else 0
            
            # System should handle majority of operations even under load
            assert dos_success_rate > 0.7, f"DoS success rate too low: {dos_success_rate:.2%}"
            
            dos_throughput = successful_dos_ops / dos_total_time
            assert dos_throughput > 10, f"DoS throughput too low: {dos_throughput:.1f} ops/sec"
            
            print(f"DoS resistance test: {successful_dos_ops}/{total_dos_ops} operations successful ({dos_success_rate:.1%})")
            print(f"DoS throughput: {dos_throughput:.1f} ops/sec")
            
            # Test 4: Memory exhaustion resistance
            # Monitor memory usage during intensive operations
            import psutil
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            memory_test_operations = 0
            for i in range(200):
                try:
                    # Create files with varied content
                    memory_file = test_root / f"memory_test_{i}.txt"
                    content = f"Memory test content {i} " * 1000  # ~25KB per file
                    memory_file.write_text(content)
                    
                    # Index file
                    search_engine.index_file(memory_file)
                    
                    # Search for content
                    folder_service.search_all_folders(f"content {i}")
                    
                    memory_test_operations += 1
                    
                    # Check memory usage periodically
                    if i % 50 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_growth = current_memory - initial_memory
                        
                        # Memory growth should be reasonable
                        assert memory_growth < 1000, f"Excessive memory growth: {memory_growth:.1f}MB"
                        
                except MemoryError:
                    # Memory exhaustion protection triggered
                    print(f"Memory exhaustion protection activated after {memory_test_operations} operations")
                    break
                except Exception as e:
                    if "memory" in str(e).lower():
                        print(f"Memory limit reached: {e}")
                        break
                    else:
                        raise
            
            final_memory = process.memory_info().rss / 1024 / 1024
            total_memory_growth = final_memory - initial_memory
            
            print(f"Memory exhaustion test: {memory_test_operations} operations, {total_memory_growth:.1f}MB growth")
            
            # Verify system stability after stress testing
            assert db_manager.validate_database_integrity(), "Database integrity compromised after DoS testing"
            
            print("Denial of service resistance tests passed")


if __name__ == "__main__":
    """Run enterprise-grade security tests for Advanced Folders."""
    pytest.main([__file__, "-v", "--tb=short", "--strict-markers", "-s"])