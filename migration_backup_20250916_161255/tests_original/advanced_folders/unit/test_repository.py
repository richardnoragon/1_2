"""
Unit tests for Advanced Folders repository layer.

Tests the repository pattern implementation with database abstraction,
connection pooling, and transaction management.
"""

import sqlite3
import tempfile
import threading
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.rfu.advanced_folders.exceptions.advanced_folders_exceptions import (
    RepositoryException, ValidationException)
from src.rfu.advanced_folders.models.folder_configuration import (
    DirectoryTarget, FolderConfiguration)
from src.rfu.advanced_folders.repository.folder_repository import (
    BaseRepository, DatabaseConnectionManager, FolderRepository)
from src.rfu.advanced_folders.validation.validator_framework import \
    ValidationFramework


class TestDatabaseConnectionManager:
    """Test DatabaseConnectionManager class."""
    
    def test_basic_creation(self):
        """Test basic connection manager creation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            assert manager.db_path == db_path
            assert manager.pool_size == 5  # Default pool size
        finally:
            Path(db_path).unlink()
    
    def test_get_connection(self):
        """Test getting database connection."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            
            with manager.get_connection() as conn:
                assert isinstance(conn, sqlite3.Connection)
                
                # Test basic functionality
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1
        finally:
            Path(db_path).unlink()
    
    def test_connection_pooling(self):
        """Test connection pooling functionality."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path, pool_size=2)
            
            # Get multiple connections
            connections = []
            for _ in range(3):
                conn = manager.get_connection()
                connections.append(conn.__enter__())
            
            # Should have created connections
            assert len(connections) == 3
            
            # Clean up
            for conn in connections:
                conn.close()
        finally:
            Path(db_path).unlink()
    
    def test_transaction_context(self):
        """Test transaction context manager."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            
            # Create test table
            with manager.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        value TEXT
                    )
                """)
            
            # Test successful transaction
            with manager.transaction() as (conn, cursor):
                cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test",))
            
            # Verify data was committed
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_table")
                count = cursor.fetchone()[0]
                assert count == 1
        finally:
            Path(db_path).unlink()
    
    def test_transaction_rollback(self):
        """Test transaction rollback on exception."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            
            # Create test table
            with manager.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        value TEXT
                    )
                """)
            
            # Test failed transaction
            with pytest.raises(ValueError):
                with manager.transaction() as (conn, cursor):
                    cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test",))
                    raise ValueError("Test error")
            
            # Verify data was rolled back
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_table")
                count = cursor.fetchone()[0]
                assert count == 0
        finally:
            Path(db_path).unlink()
    
    def test_close_connections(self):
        """Test closing all connections."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            
            # Get some connections
            with manager.get_connection() as conn:
                pass
            
            # Close all connections
            manager.close_all()
            
            # Should still be able to get new connections
            with manager.get_connection() as conn:
                assert isinstance(conn, sqlite3.Connection)
        finally:
            Path(db_path).unlink()
    
    def test_concurrent_access(self):
        """Test concurrent database access."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = DatabaseConnectionManager(db_path)
            
            # Create test table
            with manager.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        thread_id TEXT
                    )
                """)
            
            results = []
            threads = []
            
            def worker(thread_id):
                try:
                    with manager.transaction() as (conn, cursor):
                        cursor.execute(
                            "INSERT INTO test_table (thread_id) VALUES (?)",
                            (thread_id,)
                        )
                    results.append(f"success_{thread_id}")
                except Exception as e:
                    results.append(f"error_{thread_id}_{str(e)}")
            
            # Start multiple threads
            for i in range(5):
                thread = threading.Thread(target=worker, args=(f"thread_{i}",))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            success_count = len([r for r in results if r.startswith("success")])
            assert success_count == 5
            
            # Verify data in database
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_table")
                count = cursor.fetchone()[0]
                assert count == 5
        finally:
            Path(db_path).unlink()


class TestBaseRepository:
    """Test BaseRepository abstract class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRepository(None, None)


class TestFolderRepository:
    """Test FolderRepository implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.validation_framework = ValidationFramework()
        self.repository = FolderRepository(self.db_manager, self.validation_framework)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.db_manager.close_all()
        Path(self.db_path).unlink()
    
    def test_initialization(self):
        """Test repository initialization."""
        assert self.repository.db_manager == self.db_manager
        assert self.repository.validation_framework == self.validation_framework
        
        # Tables should be created
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='folder_configurations'
            """)
            result = cursor.fetchone()
            assert result is not None
    
    def test_create_folder_configuration(self):
        """Test creating folder configuration."""
        target = DirectoryTarget(
            path=Path("/test/path"),
            name="Test Target"
        )
        
        config = FolderConfiguration(
            name="Test Config",
            directory_targets=[target],
            description="Test description"
        )
        
        # Create configuration
        config_id = self.repository.create(config)
        
        assert config_id is not None
        assert isinstance(config_id, str)  # UUID string
    
    def test_get_folder_configuration(self):
        """Test getting folder configuration by ID."""
        # Create test configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        
        config_id = self.repository.create(config)
        
        # Retrieve configuration
        retrieved_config = self.repository.get_by_id(config_id)
        
        assert retrieved_config is not None
        assert retrieved_config.name == "Test Config"
        assert len(retrieved_config.directory_targets) == 1
        assert retrieved_config.directory_targets[0].name == "Test"
    
    def test_get_nonexistent_configuration(self):
        """Test getting non-existent configuration."""
        result = self.repository.get_by_id("nonexistent-id")
        assert result is None
    
    def test_update_folder_configuration(self):
        """Test updating folder configuration."""
        # Create initial configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Original Name", directory_targets=[target])
        
        config_id = self.repository.create(config)
        
        # Update configuration
        config.name = "Updated Name"
        config.description = "Updated description"
        
        success = self.repository.update(config_id, config)
        assert success is True
        
        # Verify update
        updated_config = self.repository.get_by_id(config_id)
        assert updated_config.name == "Updated Name"
        assert updated_config.description == "Updated description"
    
    def test_update_nonexistent_configuration(self):
        """Test updating non-existent configuration."""
        config = FolderConfiguration(name="Test", directory_targets=[])
        
        success = self.repository.update("nonexistent-id", config)
        assert success is False
    
    def test_delete_folder_configuration(self):
        """Test deleting folder configuration."""
        # Create test configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        
        config_id = self.repository.create(config)
        
        # Delete configuration
        success = self.repository.delete(config_id)
        assert success is True
        
        # Verify deletion
        deleted_config = self.repository.get_by_id(config_id)
        assert deleted_config is None
    
    def test_delete_nonexistent_configuration(self):
        """Test deleting non-existent configuration."""
        success = self.repository.delete("nonexistent-id")
        assert success is False
    
    def test_get_all_configurations(self):
        """Test getting all configurations."""
        # Create multiple configurations
        configs = []
        for i in range(3):
            target = DirectoryTarget(path=Path(f"/test{i}"), name=f"Test{i}")
            config = FolderConfiguration(name=f"Config {i}", directory_targets=[target])
            config_id = self.repository.create(config)
            configs.append((config_id, config))
        
        # Get all configurations
        all_configs = self.repository.get_all()
        
        assert len(all_configs) == 3
        
        # Verify all configurations are present
        config_names = [config.name for config in all_configs]
        assert "Config 0" in config_names
        assert "Config 1" in config_names
        assert "Config 2" in config_names
    
    def test_get_configurations_by_criteria(self):
        """Test getting configurations by criteria."""
        # Create test configurations
        target1 = DirectoryTarget(path=Path("/enabled"), name="Enabled")
        config1 = FolderConfiguration(
            name="Enabled Config",
            directory_targets=[target1],
            enabled=True
        )
        
        target2 = DirectoryTarget(path=Path("/disabled"), name="Disabled")
        config2 = FolderConfiguration(
            name="Disabled Config",
            directory_targets=[target2],
            enabled=False
        )
        
        self.repository.create(config1)
        self.repository.create(config2)
        
        # Get enabled configurations
        enabled_configs = self.repository.get_by_criteria({"enabled": True})
        
        assert len(enabled_configs) == 1
        assert enabled_configs[0].name == "Enabled Config"
    
    def test_count_configurations(self):
        """Test counting configurations."""
        # Initially should be empty
        assert self.repository.count() == 0
        
        # Create some configurations
        for i in range(5):
            target = DirectoryTarget(path=Path(f"/test{i}"), name=f"Test{i}")
            config = FolderConfiguration(name=f"Config {i}", directory_targets=[target])
            self.repository.create(config)
        
        # Count should match
        assert self.repository.count() == 5
    
    def test_exists_configuration(self):
        """Test checking if configuration exists."""
        # Create test configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        
        config_id = self.repository.create(config)
        
        # Should exist
        assert self.repository.exists(config_id) is True
        
        # Non-existent should not exist
        assert self.repository.exists("nonexistent-id") is False
    
    def test_validation_on_create(self):
        """Test validation during create operation."""
        # Mock validation framework to fail
        mock_framework = Mock()
        mock_framework.validate.return_value = {
            "name": Mock(is_valid=False, errors=[Mock(message="Name is required")])
        }
        mock_framework.is_valid.return_value = False
        
        repository = FolderRepository(self.db_manager, mock_framework)
        
        # Should raise ValidationException
        config = FolderConfiguration(name="", directory_targets=[])
        
        with pytest.raises(ValidationException):
            repository.create(config)
    
    def test_database_error_handling(self):
        """Test database error handling."""
        # Mock database manager to raise exception
        mock_db_manager = Mock()
        mock_db_manager.transaction.side_effect = sqlite3.Error("Database error")
        
        repository = FolderRepository(mock_db_manager, self.validation_framework)
        
        # Should raise RepositoryException
        config = FolderConfiguration(name="Test", directory_targets=[])
        
        with pytest.raises(RepositoryException):
            repository.create(config)
    
    def test_transaction_rollback_on_error(self):
        """Test transaction rollback on error."""
        # Create initial state
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        
        config_id = self.repository.create(config)
        initial_count = self.repository.count()
        
        # Mock to cause error during update
        with patch.object(self.repository, '_serialize_config') as mock_serialize:
            mock_serialize.side_effect = Exception("Serialization error")
            
            # Update should fail and rollback
            with pytest.raises(RepositoryException):
                config.name = "Updated Name"
                self.repository.update(config_id, config)
        
        # Count should remain the same
        assert self.repository.count() == initial_count
        
        # Original configuration should be unchanged
        original_config = self.repository.get_by_id(config_id)
        assert original_config.name == "Test Config"
    
    def test_concurrent_repository_access(self):
        """Test concurrent repository access."""
        results = []
        threads = []
        
        def worker(thread_id):
            try:
                target = DirectoryTarget(
                    path=Path(f"/test{thread_id}"),
                    name=f"Test{thread_id}"
                )
                config = FolderConfiguration(
                    name=f"Config {thread_id}",
                    directory_targets=[target]
                )
                
                config_id = self.repository.create(config)
                results.append(f"success_{thread_id}_{config_id}")
            except Exception as e:
                results.append(f"error_{thread_id}_{str(e)}")
        
        # Start multiple threads
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = len([r for r in results if r.startswith("success")])
        assert success_count == 3
        
        # Verify all configurations were created
        assert self.repository.count() == 3


class TestRepositoryEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.validation_framework = ValidationFramework()
        self.repository = FolderRepository(self.db_manager, self.validation_framework)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.db_manager.close_all()
        Path(self.db_path).unlink()
    
    def test_large_configuration_serialization(self):
        """Test handling of large configurations."""
        # Create configuration with many targets
        targets = [
            DirectoryTarget(
                path=Path(f"/test/path_{i}"),
                name=f"Target {i}",
                description=f"Description for target {i}"
            )
            for i in range(100)
        ]
        
        config = FolderConfiguration(
            name="Large Config",
            directory_targets=targets,
            description="A configuration with many targets"
        )
        
        # Should handle large configuration
        config_id = self.repository.create(config)
        assert config_id is not None
        
        # Should be able to retrieve it
        retrieved_config = self.repository.get_by_id(config_id)
        assert len(retrieved_config.directory_targets) == 100
    
    def test_unicode_configuration_handling(self):
        """Test handling of Unicode configurations."""
        target = DirectoryTarget(
            path=Path("/测试/路径"),
            name="测试目标",
            description="这是一个测试配置"
        )
        
        config = FolderConfiguration(
            name="測試配置",
            directory_targets=[target],
            description="Unicode configuration test"
        )
        
        # Should handle Unicode
        config_id = self.repository.create(config)
        retrieved_config = self.repository.get_by_id(config_id)
        
        assert retrieved_config.name == "測試配置"
        assert retrieved_config.directory_targets[0].name == "测试目标"
    
    def test_empty_search_criteria(self):
        """Test search with empty criteria."""
        # Create test configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        self.repository.create(config)
        
        # Empty criteria should return all
        results = self.repository.get_by_criteria({})
        assert len(results) == 1
    
    def test_invalid_search_criteria(self):
        """Test search with invalid criteria."""
        # Create test configuration
        target = DirectoryTarget(path=Path("/test"), name="Test")
        config = FolderConfiguration(name="Test Config", directory_targets=[target])
        self.repository.create(config)
        
        # Invalid criteria should return empty results
        results = self.repository.get_by_criteria({"nonexistent_field": "value"})
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__])