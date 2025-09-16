"""Unit tests for Advanced Folders database components."""

import sqlite3
from unittest.mock import MagicMock, patch

import pytest
from conftest import (assert_file_metadata_equal, assert_folder_config_equal,
                      assert_search_param_equal)

from src.tools.advanced_folders.core import (FileMetadata,
                                                 FolderConfiguration,
                                                 FolderType, SearchParameter)
from src.tools.advanced_folders.database import (AdvancedFoldersDBManager,
                                                     AdvancedFoldersSchema)


class TestAdvancedFoldersSchema:
    """Test cases for AdvancedFoldersSchema."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_schema_creation(self, temp_db):
        """Test database schema creation."""
        conn = sqlite3.connect(temp_db)
        schema = AdvancedFoldersSchema(conn)
        
        # Create schema
        schema.create_advanced_folders_schema()
        
        # Verify tables exist
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'af_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'af_folder_configurations',
            'af_search_parameters',
            'af_file_metadata',
            'af_folder_hierarchies',
            'af_operation_logs',
            'af_performance_metrics',
            'af_user_preferences',
            'af_system_settings'
        ]
        
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_indexes_creation(self, temp_db):
        """Test database indexes creation."""
        conn = sqlite3.connect(temp_db)
        schema = AdvancedFoldersSchema(conn)
        
        # Create schema and indexes
        schema.create_advanced_folders_schema()
        schema.create_advanced_folders_indexes()
        
        # Verify indexes exist
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_af_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Should have multiple indexes
        assert len(indexes) > 0
        
        conn.close()
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_triggers_creation(self, temp_db):
        """Test database triggers creation."""
        conn = sqlite3.connect(temp_db)
        schema = AdvancedFoldersSchema(conn)
        
        # Create schema and triggers
        schema.create_advanced_folders_schema()
        schema.create_advanced_folders_triggers()
        
        # Verify triggers exist
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='trigger' AND name LIKE 'tr_af_%'
        """)
        triggers = [row[0] for row in cursor.fetchall()]
        
        # Should have update timestamp triggers
        assert len(triggers) > 0
        
        conn.close()


class TestAdvancedFoldersDBManager:
    """Test cases for AdvancedFoldersDBManager."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_db_manager_initialization(self, db_manager):
        """Test database manager initialization."""
        assert db_manager is not None
        assert hasattr(db_manager, 'main_db_manager')
        assert hasattr(db_manager, 'logger')
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_folder_configuration(self, db_manager, sample_folder_config):
        """Test creating a folder configuration."""
        # Create configuration
        config_id = db_manager.create_folder_configuration(sample_folder_config)
        assert config_id is not None
        assert config_id > 0
        
        # Verify it was created
        retrieved_config = db_manager.get_folder_configuration(config_id)
        assert retrieved_config is not None
        assert_folder_config_equal(retrieved_config, sample_folder_config)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_folder_configuration_not_found(self, db_manager):
        """Test getting non-existent folder configuration."""
        config = db_manager.get_folder_configuration(99999)
        assert config is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_update_folder_configuration(self, db_manager, sample_folder_config):
        """Test updating a folder configuration."""
        # Create configuration
        config_id = db_manager.create_folder_configuration(sample_folder_config)
        
        # Update configuration
        sample_folder_config.name = "Updated Test Folder"
        sample_folder_config.description = "Updated description"
        
        success = db_manager.update_folder_configuration(config_id, sample_folder_config)
        assert success is True
        
        # Verify update
        updated_config = db_manager.get_folder_configuration(config_id)
        assert updated_config.name == "Updated Test Folder"
        assert updated_config.description == "Updated description"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_folder_configuration(self, db_manager, sample_folder_config):
        """Test deleting a folder configuration."""
        # Create configuration
        config_id = db_manager.create_folder_configuration(sample_folder_config)
        
        # Verify it exists
        config = db_manager.get_folder_configuration(config_id)
        assert config is not None
        
        # Delete configuration
        success = db_manager.delete_folder_configuration(config_id)
        assert success is True
        
        # Verify it's gone
        config = db_manager.get_folder_configuration(config_id)
        assert config is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_list_folder_configurations(self, db_manager, test_data_setup):
        """Test listing folder configurations."""
        configs = db_manager.list_folder_configurations()
        assert len(configs) >= 3  # From test data setup
        
        # Test with limit
        limited_configs = db_manager.list_folder_configurations(limit=2)
        assert len(limited_configs) == 2
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_search_parameter(self, db_manager, test_data_setup, sample_search_parameter):
        """Test creating a search parameter."""
        # Create search parameter
        search_id = db_manager.create_search_parameter(sample_search_parameter)
        assert search_id is not None
        assert search_id > 0
        
        # Verify it was created
        retrieved_param = db_manager.get_search_parameter(search_id)
        assert retrieved_param is not None
        assert_search_param_equal(retrieved_param, sample_search_parameter)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_search_parameters_by_folder(self, db_manager, test_data_setup):
        """Test getting search parameters by folder configuration."""
        folder_ids = test_data_setup['folder_ids']
        folder_id = folder_ids[0]
        
        params = db_manager.get_search_parameters_by_folder(folder_id)
        assert len(params) > 0
        
        # All parameters should belong to the specified folder
        for param in params:
            assert param.folder_config_id == folder_id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_insert_file_metadata(self, db_manager, test_data_setup, sample_file_metadata):
        """Test inserting file metadata."""
        # Insert metadata
        metadata_id = db_manager.insert_file_metadata(sample_file_metadata)
        assert metadata_id is not None
        assert metadata_id > 0
        
        # Verify it was inserted
        retrieved_metadata = db_manager.get_file_metadata(metadata_id)
        assert retrieved_metadata is not None
        assert_file_metadata_equal(retrieved_metadata, sample_file_metadata)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_search_files_by_pattern(self, db_manager, test_data_setup):
        """Test searching files by pattern."""
        # Search for PDF files
        results = db_manager.search_files_by_pattern("*.pdf")
        assert len(results) > 0
        
        # All results should be PDF files
        for result in results:
            assert result.file_type == "pdf" or result.file_path.endswith('.pdf')
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_search_files_by_size_range(self, db_manager, test_data_setup):
        """Test searching files by size range."""
        # Search for files between 1KB and 10MB
        min_size = 1024  # 1KB
        max_size = 10 * 1024 * 1024  # 10MB
        
        results = db_manager.search_files_by_size_range(min_size, max_size)
        
        # All results should be within the size range
        for result in results:
            assert min_size <= result.file_size <= max_size
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_folder_statistics(self, db_manager, test_data_setup):
        """Test getting folder statistics."""
        folder_ids = test_data_setup['folder_ids']
        folder_id = folder_ids[0]
        
        stats = db_manager.get_folder_statistics(folder_id)
        assert stats is not None
        assert 'total_files' in stats
        assert 'total_size' in stats
        assert 'file_types' in stats
        assert stats['total_files'] >= 0
        assert stats['total_size'] >= 0
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_duplicate_files(self, db_manager, test_data_setup):
        """Test finding duplicate files."""
        duplicates = db_manager.get_duplicate_files()
        
        # Should return a list (may be empty if no duplicates)
        assert isinstance(duplicates, list)
        
        # If duplicates exist, they should have the same checksum
        for dup_group in duplicates:
            checksums = [file['checksum'] for file in dup_group]
            assert len(set(checksums)) == 1  # All checksums should be the same
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_performance_metrics(self, db_manager):
        """Test performance metrics logging."""
        # Log a performance metric
        success = db_manager.log_performance_metric(
            operation_type="test_operation",
            duration_ms=150.5,
            records_processed=100,
            memory_usage_mb=25.2
        )
        assert success is True
        
        # Retrieve metrics
        metrics = db_manager.get_performance_metrics(
            operation_type="test_operation",
            limit=10
        )
        assert len(metrics) > 0
        assert metrics[0]['operation_type'] == "test_operation"
        assert metrics[0]['duration_ms'] == 150.5
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_operation_logging(self, db_manager):
        """Test operation logging."""
        # Log an operation
        success = db_manager.log_operation(
            operation_type="test_log",
            details="Test operation details",
            success=True
        )
        assert success is True
        
        # Retrieve operation logs
        logs = db_manager.get_operation_logs(limit=10)
        assert len(logs) > 0
        
        # Find our test log
        test_logs = [log for log in logs if log['operation_type'] == "test_log"]
        assert len(test_logs) > 0
        assert test_logs[0]['details'] == "Test operation details"
        assert test_logs[0]['success'] is True
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_database_health_check(self, db_manager):
        """Test database health check."""
        health_status = db_manager.check_database_health()
        
        assert 'status' in health_status
        assert 'total_configurations' in health_status
        assert 'total_files' in health_status
        assert 'database_size' in health_status
        assert 'last_backup' in health_status
        
        assert health_status['status'] in ['healthy', 'warning', 'error']
        assert health_status['total_configurations'] >= 0
        assert health_status['total_files'] >= 0
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_batch_operations(self, db_manager):
        """Test batch operations for performance."""
        # Create multiple folder configurations
        configs = []
        for i in range(5):
            config = FolderConfiguration(
                name=f"Batch Test {i}",
                path=f"/test/batch/{i}",
                folder_type=FolderType.SMART,
                auto_organize=True,
                priority=i + 1
            )
            configs.append(config)
        
        # Batch create
        config_ids = db_manager.batch_create_folder_configurations(configs)
        assert len(config_ids) == 5
        assert all(config_id > 0 for config_id in config_ids)
        
        # Verify all were created
        for config_id in config_ids:
            config = db_manager.get_folder_configuration(config_id)
            assert config is not None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_transaction_rollback(self, db_manager):
        """Test transaction rollback on error."""
        # This test would need to simulate an error condition
        # For now, just test that the method exists and can be called
        assert hasattr(db_manager, 'execute_transaction')
        
        # Test a successful transaction
        def test_transaction(cursor):
            cursor.execute("SELECT COUNT(*) FROM af_folder_configurations")
            return cursor.fetchone()[0]
        
        result = db_manager.execute_transaction(test_transaction)
        assert result is not None
    
    @pytest.mark.performance
    @pytest.mark.database
    def test_large_dataset_performance(self, db_manager):
        """Test performance with larger datasets."""
        import time

        # Create a larger number of configurations
        configs = []
        for i in range(50):
            config = FolderConfiguration(
                name=f"Performance Test {i}",
                path=f"/test/performance/{i}",
                folder_type=FolderType.SMART,
                auto_organize=True,
                priority=(i % 10) + 1,
                description=f"Performance test configuration {i}"
            )
            configs.append(config)
        
        # Measure batch creation time
        start_time = time.time()
        config_ids = db_manager.batch_create_folder_configurations(configs)
        creation_time = time.time() - start_time
        
        assert len(config_ids) == 50
        assert creation_time < 5.0  # Should complete within 5 seconds
        
        # Measure retrieval time
        start_time = time.time()
        all_configs = db_manager.list_folder_configurations()
        retrieval_time = time.time() - start_time
        
        assert len(all_configs) >= 50
        assert retrieval_time < 2.0  # Should complete within 2 seconds
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_error_handling(self, db_manager):
        """Test error handling in database operations."""
        # Test with invalid folder configuration ID
        config = db_manager.get_folder_configuration(-1)
        assert config is None
        
        # Test updating non-existent configuration
        dummy_config = FolderConfiguration(
            name="Dummy",
            path="/dummy",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        success = db_manager.update_folder_configuration(99999, dummy_config)
        assert success is False
        
        # Test deleting non-existent configuration
        success = db_manager.delete_folder_configuration(99999)
        assert success is False