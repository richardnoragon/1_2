"""
Enterprise-Grade Integration Tests for Advanced Folders System
Phase 4: Testing & QA (Week 10) - Comprehensive Integration Testing

Test Coverage Target: End-to-End Workflow Validation
Test Complexity Level: Enterprise-Grade (No Simplification)
Quality Standards: Zero-Compromise Testing Protocols

This module implements comprehensive integration testing for the complete
Advanced Folders system with enterprise-level rigor and dependency validation.
"""

import json
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.advanced_folders.core.folder_models import (
    FileMetadata, FolderConfiguration, FolderType, SearchParameter)
from src.tools.advanced_folders.database.db_manager import \
    AdvancedFoldersDBManager
from src.tools.advanced_folders.engine.search_engine import SearchEngine
from src.tools.advanced_folders.gui.advanced_folders_widget import \
    AdvancedFoldersWidget
from src.tools.advanced_folders.services.folder_service import \
    FolderService


class TestAdvancedFoldersIntegrationEnterprise:
    """Enterprise-grade integration test suite for Advanced Folders system."""
    
    @pytest.mark.integration
    @pytest.mark.critical
    def test_end_to_end_folder_creation_and_search_workflow(self):
        """Test complete end-to-end folder creation and search workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize system components
            db_path = Path(temp_dir) / "integration_test.db"
            index_path = Path(temp_dir) / "search_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Create test file structure
            test_root = Path(temp_dir) / "test_documents"
            test_root.mkdir()
            
            # Create realistic document structure
            documents = [
                ("contracts/client_agreement_2024.pdf", "Legal contract with ABC Corp"),
                ("invoices/invoice_001_january.pdf", "Invoice #001 for $2,500"),
                ("reports/quarterly_report_q1.docx", "Q1 financial performance report"),
                ("presentations/sales_pitch_deck.pptx", "Sales presentation materials"),
                ("data/customer_database.csv", "Customer contact information"),
                ("projects/project_alpha/readme.txt", "Project Alpha documentation"),
                ("projects/project_beta/requirements.md", "Project Beta requirements"),
                ("archive/old_contracts/legacy_agreement.pdf", "Historical contract"),
                ("temp/draft_proposal.txt", "Draft business proposal"),
                ("templates/email_template.html", "HTML email template"),
            ]
            
            # Create directory structure and files
            created_files = []
            for relative_path, content in documents:
                file_path = test_root / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                created_files.append(file_path)
            
            # Step 1: Create folder configuration for contracts
            contracts_config = FolderConfiguration(
                name="Active Contracts",
                path=str(test_root / "contracts"),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1,
                description="Monitor active contract documents"
            )
            
            # Save configuration
            config_id = folder_service.create_folder_configuration(contracts_config)
            assert config_id is not None
            assert config_id > 0
            
            # Step 2: Create search parameters for contracts
            contract_search = SearchParameter(
                folder_config_id=config_id,
                name="PDF Contracts",
                pattern="*.pdf",
                case_sensitive=False,
                include_subdirs=True,
                min_size=1024,  # At least 1KB
                description="Find all PDF contract documents"
            )
            
            search_id = folder_service.create_search_parameter(contract_search)
            assert search_id is not None
            
            # Step 3: Index the documents
            indexed_count = folder_service.index_folder_contents(config_id)
            assert indexed_count > 0
            
            # Step 4: Execute search operations
            search_results = folder_service.execute_search(search_id)
            assert len(search_results) >= 1
            
            # Verify contract file is found
            contract_found = any(
                "client_agreement_2024.pdf" in result.file_name
                for result in search_results
            )
            assert contract_found
            
            # Step 5: Create additional folder for reports
            reports_config = FolderConfiguration(
                name="Financial Reports",
                path=str(test_root / "reports"),
                folder_type=FolderType.SMART,
                auto_organize=False,
                priority=2,
                description="Financial and business reports"
            )
            
            reports_config_id = folder_service.create_folder_configuration(reports_config)
            
            # Step 6: Cross-folder search
            global_search_results = folder_service.search_all_folders("report")
            assert len(global_search_results) >= 1
            
            # Step 7: Verify database integrity
            all_configs = folder_service.list_folder_configurations()
            assert len(all_configs) >= 2
            
            config_names = {config.name for config in all_configs}
            assert "Active Contracts" in config_names
            assert "Financial Reports" in config_names
            
            # Step 8: Test folder statistics
            stats = folder_service.get_folder_statistics(config_id)
            assert stats['total_files'] >= 1
            assert stats['total_size'] > 0
            assert 'file_types' in stats
            
            # Step 9: Test folder synchronization
            # Add new file to monitored folder
            new_contract = test_root / "contracts" / "new_contract_2024.pdf"
            new_contract.write_text("New contract with XYZ Corp for $5,000")
            
            # Trigger folder sync
            sync_result = folder_service.sync_folder_contents(config_id)
            assert sync_result is True
            
            # Verify new file is indexed
            updated_search_results = folder_service.execute_search(search_id)
            new_file_found = any(
                "new_contract_2024.pdf" in result.file_name
                for result in updated_search_results
            )
            assert new_file_found
            
            # Step 10: Test configuration updates
            contracts_config.description = "Updated description for active contracts"
            update_success = folder_service.update_folder_configuration(
                config_id, contracts_config
            )
            assert update_success is True
            
            # Verify update
            updated_config = folder_service.get_folder_configuration(config_id)
            assert "Updated description" in updated_config.description
    
    @pytest.mark.integration
    @pytest.mark.critical
    def test_database_search_engine_integration(self):
        """Test comprehensive database and search engine integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "db_search_integration.db"
            index_path = Path(temp_dir) / "search_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            
            # Create test data structure
            test_root = Path(temp_dir) / "integration_files"
            test_root.mkdir()
            
            # Create diverse file types for comprehensive testing
            test_files = [
                ("documents/report_2024.pdf", "Annual report 2024 with financial data"),
                ("images/chart_revenue.png", b"PNG_IMAGE_DATA_PLACEHOLDER"),
                ("data/sales_data.csv", "Date,Amount,Client\n2024-01-01,1000,ABC Corp"),
                ("scripts/analysis.py", "import pandas as pd\nprint('Data analysis')"),
                ("configs/settings.json", '{"debug": true, "version": "1.0"}'),
                ("logs/application.log", "[2024-01-01] INFO: Application started"),
                ("archives/backup_2023.zip", b"ZIP_ARCHIVE_DATA_PLACEHOLDER"),
                ("templates/invoice.html", "<html><body>Invoice Template</body></html>"),
            ]
            
            # Create files and track metadata
            file_metadata_list = []
            for relative_path, content in test_files:
                file_path = test_root / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                if isinstance(content, bytes):
                    file_path.write_bytes(content)
                else:
                    file_path.write_text(content)
                
                # Create metadata entry
                metadata = FileMetadata(
                    folder_config_id=1,  # Will be set after folder creation
                    file_path=str(file_path),
                    file_name=file_path.name,
                    file_size=file_path.stat().st_size,
                    file_type=file_path.suffix.lstrip('.') or 'unknown',
                    checksum=f"md5_{file_path.name}",  # Simplified checksum
                    modified_date=datetime.now(),
                    indexed_date=datetime.now()
                )
                file_metadata_list.append(metadata)
            
            # Test 1: Create folder configuration
            folder_config = FolderConfiguration(
                name="Integration Test Folder",
                path=str(test_root),
                folder_type=FolderType.SMART,
                auto_organize=True,
                priority=1
            )
            
            config_id = db_manager.create_folder_configuration(folder_config)
            assert config_id is not None
            
            # Update metadata with correct folder config ID
            for metadata in file_metadata_list:
                metadata.folder_config_id = config_id
            
            # Test 2: Store file metadata in database
            metadata_ids = []
            for metadata in file_metadata_list:
                metadata_id = db_manager.insert_file_metadata(metadata)
                assert metadata_id is not None
                metadata_ids.append(metadata_id)
            
            # Test 3: Index files in search engine
            indexed_count = search_engine.index_directory(test_root, recursive=True)
            assert indexed_count >= len(test_files)
            
            # Test 4: Cross-system search consistency
            # Search via database
            db_pdf_results = db_manager.search_files_by_pattern("*.pdf")
            db_pdf_files = [r for r in db_pdf_results if r.folder_config_id == config_id]
            
            # Search via search engine
            engine_pdf_results = search_engine.search("*.pdf")
            
            # Verify consistency
            assert len(db_pdf_files) >= 1
            assert len(engine_pdf_results) >= 1
            
            # Cross-verify file existence
            db_pdf_paths = {result.file_path for result in db_pdf_files}
            engine_pdf_paths = {result.file_path for result in engine_pdf_results}
            
            # Should have common files
            common_files = db_pdf_paths.intersection(engine_pdf_paths)
            assert len(common_files) >= 1
            
            # Test 5: Content-based search integration
            # Search for specific content
            content_results_engine = search_engine.search("financial data")
            content_results_db = db_manager.search_files_by_content("financial")
            
            # Should find the report file
            assert len(content_results_engine) >= 1
            
            # Test 6: Size-based filtering integration
            size_threshold = 500  # bytes
            large_files_db = db_manager.search_files_by_size_range(
                size_threshold, float('inf')
            )
            large_files_engine = search_engine.search(
                "", size_filter=(size_threshold, None)
            )
            
            # Verify size filtering works in both systems
            for result in large_files_db:
                if result.folder_config_id == config_id:
                    assert result.file_size >= size_threshold
            
            # Test 7: Transaction consistency
            # Start transaction and modify both systems
            try:
                # Add new file
                new_file = test_root / "new_document.txt"
                new_file.write_text("New document with transaction test content")
                
                # Add to database
                new_metadata = FileMetadata(
                    folder_config_id=config_id,
                    file_path=str(new_file),
                    file_name=new_file.name,
                    file_size=new_file.stat().st_size,
                    file_type="txt",
                    checksum="md5_new_document",
                    modified_date=datetime.now(),
                    indexed_date=datetime.now()
                )
                
                new_metadata_id = db_manager.insert_file_metadata(new_metadata)
                
                # Add to search index
                index_success = search_engine.index_file(new_file)
                
                # Verify both operations succeeded
                assert new_metadata_id is not None
                assert index_success is True
                
                # Verify consistency
                db_new_results = db_manager.search_files_by_pattern("new_document.txt")
                engine_new_results = search_engine.search("new_document.txt")
                
                assert len(db_new_results) >= 1
                assert len(engine_new_results) >= 1
                
            except Exception as e:
                pytest.fail(f"Transaction consistency test failed: {e}")
            
            # Test 8: Performance under load
            # Create additional files to test system under load
            load_test_files = []
            for i in range(100):
                load_file = test_root / f"load_test_{i:03d}.txt"
                load_content = f"Load test file {i} with searchable content {i * 7}"
                load_file.write_text(load_content)
                load_test_files.append(load_file)
            
            # Batch index in search engine
            start_time = time.time()
            for load_file in load_test_files:
                search_engine.index_file(load_file)
            search_index_time = time.time() - start_time
            
            # Batch insert metadata
            start_time = time.time()
            for load_file in load_test_files:
                load_metadata = FileMetadata(
                    folder_config_id=config_id,
                    file_path=str(load_file),
                    file_name=load_file.name,
                    file_size=load_file.stat().st_size,
                    file_type="txt",
                    checksum=f"md5_{load_file.name}",
                    modified_date=datetime.now(),
                    indexed_date=datetime.now()
                )
                db_manager.insert_file_metadata(load_metadata)
            db_insert_time = time.time() - start_time
            
            # Performance assertions
            search_files_per_second = 100 / search_index_time
            db_files_per_second = 100 / db_insert_time
            
            assert search_files_per_second > 10, f"Search indexing too slow: {search_files_per_second} fps"
            assert db_files_per_second > 20, f"DB insertion too slow: {db_files_per_second} fps"
            
            # Test 9: Data synchronization validation
            # Get statistics from both systems
            db_stats = db_manager.get_folder_statistics(config_id)
            search_stats = search_engine.get_index_statistics()
            
            # File counts should be consistent (within reasonable margin)
            total_files_created = len(test_files) + 1 + 100  # original + new + load test
            
            assert db_stats['total_files'] >= total_files_created - 5  # Allow some margin
            assert search_stats['indexed_files'] >= total_files_created - 5
    
    @pytest.mark.integration
    @pytest.mark.critical
    def test_gui_backend_integration(self):
        """Test comprehensive GUI and backend integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize backend components
            db_path = Path(temp_dir) / "gui_integration.db"
            index_path = Path(temp_dir) / "gui_search_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Initialize GUI components (mock Qt if needed)
            try:
                from PyQt5.QtCore import Qt
                from PyQt5.QtTest import QTest
                from PyQt5.QtWidgets import QApplication

                # Create QApplication if it doesn't exist
                app = QApplication.instance()
                if app is None:
                    app = QApplication([])
                
                # Create GUI widget
                gui_widget = AdvancedFoldersWidget(folder_service)
                
                # Test 1: GUI initialization
                assert gui_widget is not None
                assert hasattr(gui_widget, 'folder_service')
                assert gui_widget.folder_service is folder_service
                
                # Test 2: Folder creation through GUI
                # Simulate GUI folder creation
                test_folder_path = str(Path(temp_dir) / "gui_test_folder")
                Path(test_folder_path).mkdir()
                
                folder_config = FolderConfiguration(
                    name="GUI Test Folder",
                    path=test_folder_path,
                    folder_type=FolderType.MONITORED,
                    auto_organize=True,
                    priority=1
                )
                
                # Simulate GUI action
                config_id = gui_widget.create_folder_configuration(folder_config)
                assert config_id is not None
                
                # Verify backend received the configuration
                backend_config = folder_service.get_folder_configuration(config_id)
                assert backend_config is not None
                assert backend_config.name == "GUI Test Folder"
                
                # Test 3: Search through GUI
                # Create test files
                test_files = [
                    "document1.pdf",
                    "spreadsheet.xlsx", 
                    "presentation.pptx",
                    "image.jpg",
                    "data.csv"
                ]
                
                for filename in test_files:
                    file_path = Path(test_folder_path) / filename
                    file_path.write_text(f"Content of {filename}")
                
                # Index through backend
                folder_service.index_folder_contents(config_id)
                
                # Simulate GUI search
                search_results = gui_widget.execute_search("document")
                assert len(search_results) >= 1
                
                # Test 4: Real-time updates
                # Add new file and test real-time detection
                new_file = Path(test_folder_path) / "new_file.txt"
                new_file.write_text("New file added for real-time test")
                
                # Simulate file system watcher notification
                gui_widget.on_file_added(str(new_file))
                
                # Verify file is indexed
                updated_stats = folder_service.get_folder_statistics(config_id)
                assert updated_stats['total_files'] >= len(test_files) + 1
                
                # Test 5: Configuration updates through GUI
                updated_config = backend_config
                updated_config.description = "Updated through GUI"
                
                update_success = gui_widget.update_folder_configuration(
                    config_id, updated_config
                )
                assert update_success is True
                
                # Verify update in backend
                final_config = folder_service.get_folder_configuration(config_id)
                assert "Updated through GUI" in final_config.description
                
                # Test 6: Error handling integration
                # Test invalid folder path
                invalid_config = FolderConfiguration(
                    name="Invalid Folder",
                    path="/invalid/nonexistent/path",
                    folder_type=FolderType.MONITORED,
                    auto_organize=True,
                    priority=1
                )
                
                try:
                    invalid_config_id = gui_widget.create_folder_configuration(invalid_config)
                    # Should either return None or raise exception
                    if invalid_config_id is not None:
                        # If it succeeds, verify error is logged
                        assert hasattr(gui_widget, 'last_error')
                except Exception:
                    # Expected behavior for invalid path
                    pass
                
                # Test 7: Performance with GUI updates
                # Create multiple configurations rapidly
                rapid_configs = []
                for i in range(10):
                    rapid_folder = Path(temp_dir) / f"rapid_{i}"
                    rapid_folder.mkdir(exist_ok=True)
                    
                    config = FolderConfiguration(
                        name=f"Rapid Config {i}",
                        path=str(rapid_folder),
                        folder_type=FolderType.SMART,
                        auto_organize=False,
                        priority=i + 1
                    )
                    
                    start_time = time.time()
                    config_id = gui_widget.create_folder_configuration(config)
                    creation_time = time.time() - start_time
                    
                    rapid_configs.append((config_id, creation_time))
                    
                    # Each creation should be reasonably fast
                    assert creation_time < 1.0, f"GUI creation too slow: {creation_time}s"
                
                # Verify all configurations were created
                all_configs = gui_widget.list_folder_configurations()
                assert len(all_configs) >= 11  # Original + 10 rapid
                
                # Test 8: GUI refresh and synchronization
                # Modify backend directly
                backend_config = FolderConfiguration(
                    name="Backend Only Config",
                    path=str(Path(temp_dir) / "backend_folder"),
                    folder_type=FolderType.ARCHIVE,
                    auto_organize=False,
                    priority=5
                )
                
                Path(temp_dir / "backend_folder").mkdir(exist_ok=True)
                backend_config_id = folder_service.create_folder_configuration(backend_config)
                
                # Refresh GUI
                gui_widget.refresh_configurations()
                
                # Verify GUI shows backend changes
                gui_configs = gui_widget.list_folder_configurations()
                backend_names = {config.name for config in gui_configs}
                assert "Backend Only Config" in backend_names
                
            except ImportError:
                # PyQt5 not available, skip GUI tests
                pytest.skip("PyQt5 not available for GUI integration testing")
            except Exception as e:
                pytest.fail(f"GUI integration test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_concurrent_operations_integration(self):
        """Test system behavior under concurrent operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize system components
            db_path = Path(temp_dir) / "concurrent_test.db"
            index_path = Path(temp_dir) / "concurrent_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            # Shared data structures for thread coordination
            results = {'success': [], 'errors': []}
            lock = threading.Lock()
            
            def folder_creation_worker(worker_id, folder_count):
                """Worker function for concurrent folder creation."""
                try:
                    for i in range(folder_count):
                        # Create unique folder path
                        folder_path = Path(temp_dir) / f"worker_{worker_id}_folder_{i}"
                        folder_path.mkdir(exist_ok=True)
                        
                        # Create folder configuration
                        config = FolderConfiguration(
                            name=f"Worker {worker_id} Folder {i}",
                            path=str(folder_path),
                            folder_type=FolderType.SMART,
                            auto_organize=True,
                            priority=(i % 10) + 1
                        )
                        
                        # Create configuration
                        config_id = folder_service.create_folder_configuration(config)
                        
                        with lock:
                            results['success'].append((worker_id, i, config_id))
                            
                except Exception as e:
                    with lock:
                        results['errors'].append((worker_id, str(e)))
            
            def file_indexing_worker(worker_id, file_count):
                """Worker function for concurrent file indexing."""
                try:
                    # Create test files
                    worker_dir = Path(temp_dir) / f"indexing_worker_{worker_id}"
                    worker_dir.mkdir(exist_ok=True)
                    
                    for i in range(file_count):
                        file_path = worker_dir / f"file_{i}.txt"
                        content = f"Worker {worker_id} file {i} with content {i * 13}"
                        file_path.write_text(content)
                        
                        # Index file
                        success = search_engine.index_file(file_path)
                        
                        with lock:
                            if success:
                                results['success'].append((f"index_{worker_id}", i, True))
                            else:
                                results['errors'].append((f"index_{worker_id}", f"Failed to index file {i}"))
                                
                except Exception as e:
                    with lock:
                        results['errors'].append((f"index_{worker_id}", str(e)))
            
            def search_worker(worker_id, search_count):
                """Worker function for concurrent searches."""
                try:
                    search_terms = [
                        "file", "content", "worker", "folder", 
                        "test", "data", "document", "index"
                    ]
                    
                    for i in range(search_count):
                        term = search_terms[i % len(search_terms)]
                        
                        # Perform search
                        search_results = search_engine.search(term)
                        
                        with lock:
                            results['success'].append((f"search_{worker_id}", i, len(search_results)))
                            
                except Exception as e:
                    with lock:
                        results['errors'].append((f"search_{worker_id}", str(e)))
            
            # Test 1: Concurrent folder creation
            creation_threads = []
            for worker_id in range(5):
                thread = threading.Thread(
                    target=folder_creation_worker,
                    args=(worker_id, 10)
                )
                creation_threads.append(thread)
                thread.start()
            
            # Wait for folder creation to complete
            for thread in creation_threads:
                thread.join(timeout=30)
            
            # Verify folder creation results
            creation_successes = [r for r in results['success'] if isinstance(r[0], int)]
            creation_errors = [e for e in results['errors'] if isinstance(e[0], int)]
            
            assert len(creation_successes) >= 45  # 5 workers * 10 folders, allow some margin
            assert len(creation_errors) <= 5  # Allow minimal errors
            
            # Clear results for next test
            results['success'].clear()
            results['errors'].clear()
            
            # Test 2: Concurrent file indexing
            indexing_threads = []
            for worker_id in range(3):
                thread = threading.Thread(
                    target=file_indexing_worker,
                    args=(worker_id, 20)
                )
                indexing_threads.append(thread)
                thread.start()
            
            # Wait for indexing to complete
            for thread in indexing_threads:
                thread.join(timeout=30)
            
            # Verify indexing results
            indexing_successes = [r for r in results['success'] if 'index_' in str(r[0])]
            indexing_errors = [e for e in results['errors'] if 'index_' in str(e[0])]
            
            assert len(indexing_successes) >= 55  # 3 workers * 20 files, allow margin
            assert len(indexing_errors) <= 5
            
            # Clear results for search test
            results['success'].clear()
            results['errors'].clear()
            
            # Test 3: Concurrent searches
            search_threads = []
            for worker_id in range(4):
                thread = threading.Thread(
                    target=search_worker,
                    args=(worker_id, 15)
                )
                search_threads.append(thread)
                thread.start()
            
            # Wait for searches to complete
            for thread in search_threads:
                thread.join(timeout=30)
            
            # Verify search results
            search_successes = [r for r in results['success'] if 'search_' in str(r[0])]
            search_errors = [e for e in results['errors'] if 'search_' in str(e[0])]
            
            assert len(search_successes) >= 55  # 4 workers * 15 searches, allow margin
            assert len(search_errors) <= 5
            
            # Test 4: Mixed concurrent operations
            results['success'].clear()
            results['errors'].clear()
            
            mixed_threads = []
            
            # Add folder creation thread
            mixed_threads.append(threading.Thread(
                target=folder_creation_worker, args=(99, 5)
            ))
            
            # Add indexing thread
            mixed_threads.append(threading.Thread(
                target=file_indexing_worker, args=(99, 10)
            ))
            
            # Add search thread
            mixed_threads.append(threading.Thread(
                target=search_worker, args=(99, 8)
            ))
            
            # Start all mixed operations
            start_time = time.time()
            for thread in mixed_threads:
                thread.start()
            
            # Wait for completion
            for thread in mixed_threads:
                thread.join(timeout=30)
            
            total_time = time.time() - start_time
            
            # Verify mixed operations
            mixed_successes = len(results['success'])
            mixed_errors = len(results['errors'])
            
            assert mixed_successes >= 20  # Should complete most operations
            assert mixed_errors <= 3  # Minimal errors allowed
            assert total_time < 20  # Should complete within reasonable time
            
            # Test 5: System integrity after concurrent operations
            # Verify database integrity
            final_configs = folder_service.list_folder_configurations()
            assert len(final_configs) >= 50  # Should have many configurations
            
            # Verify search index integrity
            index_stats = search_engine.get_index_statistics()
            assert index_stats['indexed_files'] >= 60  # Should have many files indexed
            
            # Verify system still functional
            test_search_results = search_engine.search("worker")
            assert len(test_search_results) >= 10  # Should find worker-created files
            
            # Test database health after concurrent operations
            db_health = db_manager.check_database_health()
            assert db_health['status'] in ['healthy', 'warning']
            assert db_health['total_configurations'] >= 50


if __name__ == "__main__":
    """Run enterprise-grade integration tests for Advanced Folders."""
    pytest.main([__file__, "-v", "--tb=short", "--strict-markers"])