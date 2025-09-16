"""Integration tests for Advanced Folders system."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.utilities.advanced_folders.core import (ConfigurationManager,
                                                 FileMetadata,
                                                 FolderConfiguration,
                                                 FolderType, LogLevel,
                                                 SearchParameter)
from src.utilities.advanced_folders.database import AdvancedFoldersDBManager


class TestAdvancedFoldersIntegration:
    """Integration tests for the complete Advanced Folders system."""
    
    @pytest.mark.integration
    def test_end_to_end_folder_management(self, db_manager, configuration_manager):
        """Test complete folder management workflow."""
        # Step 1: Create folder configuration
        folder_config = FolderConfiguration(
            name="Integration Test Folder",
            path="/test/integration",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1,
            description="End-to-end integration test folder"
        )
        
        # Step 2: Save to database
        config_id = db_manager.create_folder_configuration(folder_config)
        assert config_id is not None
        
        # Step 3: Create search parameters
        search_params = [
            SearchParameter(
                folder_config_id=config_id,
                name="PDF Documents",
                pattern="*.pdf",
                case_sensitive=False,
                include_subdirs=True
            ),
            SearchParameter(
                folder_config_id=config_id,
                name="Large Files",
                min_size=10 * 1024 * 1024,  # 10MB
                case_sensitive=False,
                include_subdirs=True
            )
        ]
        
        search_ids = []
        for param in search_params:
            search_id = db_manager.create_search_parameter(param)
            search_ids.append(search_id)
        
        # Step 4: Simulate file discovery and metadata insertion
        file_metadata_list = [
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/integration/document1.pdf",
                file_name="document1.pdf",
                file_size=2 * 1024 * 1024,  # 2MB
                file_type="pdf",
                checksum="abc123"
            ),
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/integration/archive.zip",
                file_name="archive.zip",
                file_size=50 * 1024 * 1024,  # 50MB
                file_type="zip",
                checksum="def456"
            ),
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/integration/presentation.pdf",
                file_name="presentation.pdf",
                file_size=5 * 1024 * 1024,  # 5MB
                file_type="pdf",
                checksum="ghi789"
            )
        ]
        
        metadata_ids = []
        for metadata in file_metadata_list:
            metadata_id = db_manager.insert_file_metadata(metadata)
            metadata_ids.append(metadata_id)
        
        # Step 5: Test search functionality
        # Search for PDF files
        pdf_results = db_manager.search_files_by_pattern("*.pdf")
        pdf_files = [f for f in pdf_results if f.folder_config_id == config_id]
        assert len(pdf_files) == 2  # document1.pdf and presentation.pdf
        
        # Search for large files
        large_files = db_manager.search_files_by_size_range(
            10 * 1024 * 1024,  # 10MB minimum
            100 * 1024 * 1024  # 100MB maximum
        )
        large_files_in_folder = [f for f in large_files if f.folder_config_id == config_id]
        assert len(large_files_in_folder) == 1  # archive.zip
        
        # Step 6: Get folder statistics
        stats = db_manager.get_folder_statistics(config_id)
        assert stats['total_files'] == 3
        assert stats['total_size'] == (2 + 50 + 5) * 1024 * 1024  # Total size in bytes
        
        # Step 7: Test configuration updates
        folder_config.description = "Updated description"
        update_success = db_manager.update_folder_configuration(config_id, folder_config)
        assert update_success is True
        
        # Verify update
        updated_config = db_manager.get_folder_configuration(config_id)
        assert updated_config.description == "Updated description"
        
        # Step 8: Store configuration in ConfigurationManager
        configuration_manager.set_setting(
            "advanced_folders",
            f"folder_{config_id}",
            folder_config.to_dict()
        )
        
        # Verify storage
        stored_config_dict = configuration_manager.get_setting(
            "advanced_folders",
            f"folder_{config_id}"
        )
        assert stored_config_dict is not None
        assert stored_config_dict['name'] == "Integration Test Folder"
    
    @pytest.mark.integration
    def test_configuration_sync(self, db_manager, configuration_manager):
        """Test synchronization between database and configuration manager."""
        # Create configuration in database
        folder_config = FolderConfiguration(
            name="Sync Test Folder",
            path="/test/sync",
            folder_type=FolderType.MONITORED,
            auto_organize=False,
            priority=2
        )
        
        config_id = db_manager.create_folder_configuration(folder_config)
        
        # Store reference in configuration manager
        configuration_manager.set_setting(
            "advanced_folders",
            "active_folders",
            [config_id]
        )
        
        # Retrieve and verify
        active_folders = configuration_manager.get_setting(
            "advanced_folders",
            "active_folders",
            []
        )
        assert config_id in active_folders
        
        # Retrieve from database and verify consistency
        db_config = db_manager.get_folder_configuration(config_id)
        assert db_config.name == folder_config.name
        assert db_config.path == folder_config.path
        assert db_config.folder_type == folder_config.folder_type
    
    @pytest.mark.integration
    def test_search_parameter_execution(self, db_manager):
        """Test execution of search parameters against file metadata."""
        # Create folder configuration
        folder_config = FolderConfiguration(
            name="Search Test Folder",
            path="/test/search",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        config_id = db_manager.create_folder_configuration(folder_config)
        
        # Create diverse search parameters
        search_params = [
            SearchParameter(
                folder_config_id=config_id,
                name="Image Files",
                pattern="*.{jpg,png,gif}",
                case_sensitive=False,
                include_subdirs=True
            ),
            SearchParameter(
                folder_config_id=config_id,
                name="Recent Large Files",
                min_size=1024 * 1024,  # 1MB
                case_sensitive=False,
                include_subdirs=True
            ),
            SearchParameter(
                folder_config_id=config_id,
                name="Document Files",
                pattern="*.{doc,docx,pdf,txt}",
                case_sensitive=False,
                include_subdirs=True
            )
        ]
        
        search_ids = []
        for param in search_params:
            search_id = db_manager.create_search_parameter(param)
            search_ids.append(search_id)
        
        # Insert diverse file metadata
        test_files = [
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/search/image.jpg",
                file_name="image.jpg",
                file_size=500 * 1024,  # 500KB
                file_type="jpg",
                checksum="img123"
            ),
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/search/large_image.png",
                file_name="large_image.png",
                file_size=5 * 1024 * 1024,  # 5MB
                file_type="png",
                checksum="img456"
            ),
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/search/document.pdf",
                file_name="document.pdf",
                file_size=2 * 1024 * 1024,  # 2MB
                file_type="pdf",
                checksum="doc789"
            ),
            FileMetadata(
                folder_config_id=config_id,
                file_path="/test/search/text.txt",
                file_name="text.txt",
                file_size=10 * 1024,  # 10KB
                file_type="txt",
                checksum="txt012"
            )
        ]
        
        for metadata in test_files:
            db_manager.insert_file_metadata(metadata)
        
        # Test image search (should find .jpg and .png files)
        image_results = db_manager.search_files_by_pattern("*.jpg")
        image_results.extend(db_manager.search_files_by_pattern("*.png"))
        folder_images = [f for f in image_results if f.folder_config_id == config_id]
        assert len(folder_images) >= 2
        
        # Test large file search (should find files > 1MB)
        large_file_results = db_manager.search_files_by_size_range(
            1024 * 1024,  # 1MB minimum
            100 * 1024 * 1024  # 100MB maximum
        )
        folder_large_files = [f for f in large_file_results if f.folder_config_id == config_id]
        assert len(folder_large_files) >= 2  # large_image.png and document.pdf
        
        # Test document search
        doc_results = db_manager.search_files_by_pattern("*.pdf")
        doc_results.extend(db_manager.search_files_by_pattern("*.txt"))
        folder_docs = [f for f in doc_results if f.folder_config_id == config_id]
        assert len(folder_docs) >= 2  # document.pdf and text.txt
    
    @pytest.mark.integration
    def test_performance_monitoring(self, db_manager):
        """Test performance monitoring across operations."""
        import time

        # Create test data
        folder_config = FolderConfiguration(
            name="Performance Test",
            path="/test/performance",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        # Monitor folder creation performance
        start_time = time.time()
        config_id = db_manager.create_folder_configuration(folder_config)
        creation_duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log performance metric
        db_manager.log_performance_metric(
            operation_type="folder_creation",
            duration_ms=creation_duration,
            records_processed=1,
            memory_usage_mb=0.0  # Would be calculated in real implementation
        )
        
        # Create multiple files to test batch operations
        file_metadata_list = []
        for i in range(20):
            metadata = FileMetadata(
                folder_config_id=config_id,
                file_path=f"/test/performance/file_{i}.txt",
                file_name=f"file_{i}.txt",
                file_size=1024 * (i + 1),
                file_type="txt",
                checksum=f"hash_{i}"
            )
            file_metadata_list.append(metadata)
        
        # Monitor batch insertion performance
        start_time = time.time()
        for metadata in file_metadata_list:
            db_manager.insert_file_metadata(metadata)
        batch_duration = (time.time() - start_time) * 1000
        
        # Log batch performance
        db_manager.log_performance_metric(
            operation_type="batch_file_insertion",
            duration_ms=batch_duration,
            records_processed=len(file_metadata_list),
            memory_usage_mb=0.0
        )
        
        # Monitor search performance
        start_time = time.time()
        search_results = db_manager.search_files_by_pattern("*.txt")
        search_duration = (time.time() - start_time) * 1000
        
        # Log search performance
        db_manager.log_performance_metric(
            operation_type="file_search",
            duration_ms=search_duration,
            records_processed=len(search_results),
            memory_usage_mb=0.0
        )
        
        # Retrieve and verify performance metrics
        metrics = db_manager.get_performance_metrics(limit=10)
        assert len(metrics) >= 3
        
        # Verify metric types
        operation_types = [m['operation_type'] for m in metrics]
        assert "folder_creation" in operation_types
        assert "batch_file_insertion" in operation_types
        assert "file_search" in operation_types
    
    @pytest.mark.integration
    def test_error_recovery(self, db_manager, configuration_manager):
        """Test system behavior during error conditions."""
        # Test database connection error recovery
        original_config = FolderConfiguration(
            name="Error Recovery Test",
            path="/test/error",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        
        # This should succeed
        config_id = db_manager.create_folder_configuration(original_config)
        assert config_id is not None
        
        # Test invalid data handling
        invalid_config = FolderConfiguration(
            name="",  # Invalid: empty name
            path="",  # Invalid: empty path
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=0  # Invalid: priority out of range
        )
        
        # Validation should catch these errors
        validation_result = invalid_config.validate()
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        
        # Test configuration manager error handling
        # Try to store invalid JSON-serializable data
        try:
            configuration_manager.set_setting(
                "test_section",
                "invalid_data",
                lambda x: x  # Functions are not JSON serializable
            )
            # Should not reach here if error handling works
            assert False, "Expected exception for non-serializable data"
        except (TypeError, ValueError):
            # Expected behavior
            pass
        
        # Test database transaction rollback
        # This would be tested with a mock that simulates database errors
        with patch.object(db_manager, '_get_connection') as mock_conn:
            mock_conn.side_effect = Exception("Simulated database error")
            
            # This should handle the error gracefully
            result = db_manager.get_folder_configuration(config_id)
            # With proper error handling, this should return None rather than raise
            assert result is None or isinstance(result, FolderConfiguration)
    
    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_filesystem_integration(self, db_manager, tmp_path):
        """Test integration with actual filesystem operations."""
        # Create temporary directory structure
        test_folder = tmp_path / "filesystem_test"
        test_folder.mkdir()
        
        # Create test files
        (test_folder / "document.pdf").write_text("PDF content")
        (test_folder / "image.jpg").write_bytes(b"JPG content")
        (test_folder / "data.csv").write_text("CSV,content")
        
        subdirr = test_folder / "subdir"
        subdirr.mkdir()
        (subdirr / "nested.txt").write_text("Nested file content")
        
        # Create folder configuration for the test directory
        folder_config = FolderConfiguration(
            name="Filesystem Test",
            path=str(test_folder),
            folder_type=FolderType.MONITORED,
            auto_organize=False,
            priority=1
        )
        
        config_id = db_manager.create_folder_configuration(folder_config)
        
        # Simulate file discovery and metadata creation
        discovered_files = []
        for file_path in test_folder.rglob("*"):
            if file_path.is_file():
                file_metadata = FileMetadata(
                    folder_config_id=config_id,
                    file_path=str(file_path),
                    file_name=file_path.name,
                    file_size=file_path.stat().st_size,
                    file_type=file_path.suffix.lstrip('.') or 'unknown',
                    checksum=f"checksum_{file_path.name}"  # Simplified checksum
                )
                discovered_files.append(file_metadata)
                db_manager.insert_file_metadata(file_metadata)
        
        # Verify all files were discovered
        assert len(discovered_files) == 4  # 4 files created
        
        # Test search operations
        pdf_files = db_manager.search_files_by_pattern("*.pdf")
        folder_pdfs = [f for f in pdf_files if f.folder_config_id == config_id]
        assert len(folder_pdfs) == 1
        assert "document.pdf" in folder_pdfs[0].file_name
        
        # Test subdirectory inclusion
        txt_files = db_manager.search_files_by_pattern("*.txt")
        folder_txts = [f for f in txt_files if f.folder_config_id == config_id]
        assert len(folder_txts) == 1
        assert "nested.txt" in folder_txts[0].file_name
        
        # Get statistics
        stats = db_manager.get_folder_statistics(config_id)
        assert stats['total_files'] == 4
        assert stats['total_size'] > 0
        
        # Test file type breakdown
        file_types = stats.get('file_types', {})
        assert 'pdf' in file_types
        assert 'jpg' in file_types
        assert 'csv' in file_types
        assert 'txt' in file_types
    
    @pytest.mark.integration
    def test_concurrent_operations(self, db_manager):
        """Test system behavior under concurrent operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_folder_configs(thread_id):
            """Create folder configurations in a separate thread."""
            try:
                for i in range(5):
                    config = FolderConfiguration(
                        name=f"Thread_{thread_id}_Folder_{i}",
                        path=f"/test/thread_{thread_id}/folder_{i}",
                        folder_type=FolderType.SMART,
                        auto_organize=True,
                        priority=(i % 10) + 1
                    )
                    config_id = db_manager.create_folder_configuration(config)
                    results.append((thread_id, i, config_id))
                    time.sleep(0.01)  # Small delay to increase concurrency
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        def insert_file_metadata(thread_id):
            """Insert file metadata in a separate thread."""
            try:
                for i in range(5):
                    metadata = FileMetadata(
                        folder_config_id=1,  # Assume folder 1 exists
                        file_path=f"/test/thread_{thread_id}/file_{i}.txt",
                        file_name=f"file_{i}.txt",
                        file_size=1024 * (i + 1),
                        file_type="txt",
                        checksum=f"thread_{thread_id}_hash_{i}"
                    )
                    metadata_id = db_manager.insert_file_metadata(metadata)
                    results.append((f"metadata_{thread_id}", i, metadata_id))
                    time.sleep(0.01)
            except Exception as e:
                errors.append((f"metadata_{thread_id}", str(e)))
        
        # Create test folder first
        initial_config = FolderConfiguration(
            name="Concurrent Test Base",
            path="/test/concurrent",
            folder_type=FolderType.SMART,
            auto_organize=True,
            priority=1
        )
        base_config_id = db_manager.create_folder_configuration(initial_config)
        assert base_config_id is not None
        
        # Start multiple threads
        threads = []
        
        # Create folder configuration threads
        for i in range(3):
            thread = threading.Thread(target=create_folder_configs, args=(i,))
            threads.append(thread)
        
        # Create metadata insertion threads
        for i in range(2):
            thread = threading.Thread(target=insert_file_metadata, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) > 0, "No results from concurrent operations"
        
        # Verify data integrity
        all_configs = db_manager.list_folder_configurations()
        assert len(all_configs) >= 16  # 1 initial + 3*5 from threads
        
        # Verify all results have valid IDs
        for result in results:
            thread_id, item_id, db_id = result
            assert db_id is not None and db_id > 0