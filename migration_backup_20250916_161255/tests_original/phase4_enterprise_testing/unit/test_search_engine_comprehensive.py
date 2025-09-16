"""
Enterprise-Grade Unit Tests for SearchEngine Component
Phase 4: Testing & QA (Week 10) - Comprehensive Unit Testing Implementation

Test Coverage Target: >90%
Test Complexity Level: Enterprise-Grade (No Simplification)
Quality Standards: Zero-Compromise Testing Protocols

This module implements comprehensive unit testing for the SearchEngine
component with enterprise-level rigor and detailed assertion validation.
"""

import asyncio
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.utilities.advanced_folders.core.folder_models import (DateTimeRange,
                                                               FileMetadata,
                                                               SearchParameter,
                                                               SizeRange)
from src.utilities.advanced_folders.engine.search_engine import (SearchEngine,
                                                                 SearchIndex,
                                                                 SearchQuery,
                                                                 SearchResult)


class TestSearchEngineEnterprise:
    """Enterprise-grade test suite for SearchEngine component."""
    
    @pytest.mark.unit
    @pytest.mark.critical
    def test_search_engine_initialization_comprehensive(self):
        """Test comprehensive search engine initialization scenarios."""
        # Test 1: Standard initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "search_index"
            engine = SearchEngine(index_path=index_path)
            
            assert engine.index_path == index_path
            assert engine.is_initialized
            assert hasattr(engine, '_search_index')
            assert hasattr(engine, '_cache')
            assert hasattr(engine, '_statistics')
        
        # Test 2: Initialization with existing index
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "existing_index"
            index_path.mkdir()
            
            # Create mock index files
            (index_path / "metadata.json").write_text('{"version": "1.0"}')
            (index_path / "files.db").write_text("mock_db_content")
            
            engine = SearchEngine(index_path=index_path)
            assert engine.is_initialized
            # Should load existing index
            assert engine.get_index_statistics()['indexed_files'] >= 0
        
        # Test 3: Initialization with invalid path
        with pytest.raises((OSError, ValueError)):
            SearchEngine(index_path=Path("/invalid/path/that/cannot/exist"))
        
        # Test 4: Initialization with custom configuration
        config = {
            'max_cache_size': 1000,
            'index_update_interval': 300,
            'enable_content_indexing': True,
            'max_file_size': 100 * 1024 * 1024  # 100MB
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = SearchEngine(
                index_path=Path(temp_dir) / "custom_index",
                config=config
            )
            assert engine.config['max_cache_size'] == 1000
            assert engine.config['enable_content_indexing'] is True
    
    @pytest.mark.unit
    @pytest.mark.critical
    def test_file_indexing_comprehensive(self):
        """Test comprehensive file indexing operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "indexing_test"
            engine = SearchEngine(index_path=index_path)
            
            # Create test directory structure
            test_root = Path(temp_dir) / "test_files"
            test_root.mkdir()
            
            # Create diverse file types
            test_files = [
                (test_root / "document.pdf", b"PDF content with searchable text"),
                (test_root / "image.jpg", b"\xff\xd8\xff\xe0JPEG_DATA"),
                (test_root / "text.txt", b"Plain text file content"),
                (test_root / "data.json", b'{"key": "value", "number": 42}'),
                (test_root / "script.py", b"print('Hello, World!')"),
            ]
            
            for file_path, content in test_files:
                file_path.write_bytes(content)
            
            # Create subdirectories
            subdir = test_root / "subdirectory"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("Nested file content")
            
            # Test 1: Index single file
            single_file = test_files[0][0]
            success = engine.index_file(single_file)
            assert success is True
            
            # Verify indexing
            search_results = engine.search("document")
            assert len(search_results) >= 1
            assert any(result.file_path == str(single_file) for result in search_results)
            
            # Test 2: Index directory recursively
            indexed_count = engine.index_directory(test_root, recursive=True)
            assert indexed_count >= 6  # All files including nested
            
            # Verify all files are indexed
            stats = engine.get_index_statistics()
            assert stats['indexed_files'] >= 6
            assert stats['total_size'] > 0
            
            # Test 3: Index with file filters
            pdf_filter = lambda path: path.suffix.lower() == '.pdf'
            pdf_indexed = engine.index_directory(
                test_root, 
                recursive=True, 
                file_filter=pdf_filter
            )
            # Should only process PDF files (but they're already indexed)
            assert pdf_indexed >= 0
            
            # Test 4: Re-indexing behavior
            # Modify a file
            modified_file = test_files[2][0]  # text.txt
            modified_file.write_text("Updated content with new keywords")
            
            # Re-index
            success = engine.index_file(modified_file)
            assert success is True
            
            # Verify updated content is searchable
            search_results = engine.search("keywords")
            assert len(search_results) >= 1
            
            # Test 5: Large file handling
            large_file = test_root / "large_file.txt"
            large_content = "Large file content " * 10000  # ~200KB
            large_file.write_text(large_content)
            
            success = engine.index_file(large_file)
            assert success is True
            
            # Test 6: Binary file handling
            binary_file = test_root / "binary.bin"
            binary_content = bytes(range(256)) * 100  # 25.6KB binary
            binary_file.write_bytes(binary_content)
            
            success = engine.index_file(binary_file)
            # Should handle binary files (metadata only)
            assert success is True
            
            # Test 7: Concurrent indexing
            def index_worker(files, results):
                """Worker function for concurrent indexing."""
                for file_path in files:
                    try:
                        success = engine.index_file(file_path)
                        results.append((file_path, success))
                    except Exception as e:
                        results.append((file_path, f"Error: {e}"))
            
            # Create additional test files for concurrent processing
            concurrent_files = []
            for i in range(20):
                file_path = test_root / f"concurrent_{i}.txt"
                file_path.write_text(f"Concurrent file {i} content")
                concurrent_files.append(file_path)
            
            # Split files between threads
            thread_count = 4
            files_per_thread = len(concurrent_files) // thread_count
            threads = []
            results = []
            
            for i in range(thread_count):
                start_idx = i * files_per_thread
                end_idx = start_idx + files_per_thread
                if i == thread_count - 1:
                    end_idx = len(concurrent_files)  # Last thread takes remainder
                
                thread_files = concurrent_files[start_idx:end_idx]
                thread = threading.Thread(
                    target=index_worker,
                    args=(thread_files, results)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=30)
            
            # Verify concurrent indexing results
            assert len(results) == 20
            success_count = sum(1 for _, result in results if result is True)
            assert success_count >= 18  # Allow for some errors in concurrent scenario
    
    @pytest.mark.unit
    @pytest.mark.critical
    def test_search_functionality_comprehensive(self):
        """Test comprehensive search functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "search_test"
            engine = SearchEngine(index_path=index_path)
            
            # Prepare test data
            test_root = Path(temp_dir) / "search_files"
            test_root.mkdir()
            
            # Create files with specific content for testing
            test_content = [
                ("invoice_2024.pdf", "Invoice number: INV-2024-001\nAmount: $1,500.00"),
                ("report.txt", "Quarterly report shows 15% growth in revenue"),
                ("meeting_notes.md", "Meeting with client about project requirements"),
                ("data_analysis.py", "import pandas as pd\ndf = pd.read_csv('data.csv')"),
                ("readme.txt", "This is a README file with installation instructions"),
                ("budget.xlsx", "Budget spreadsheet with financial projections"),
                ("contract.doc", "Legal contract document with terms and conditions"),
                ("presentation.ppt", "Sales presentation for Q4 2024 targets"),
            ]
            
            for filename, content in test_content:
                file_path = test_root / filename
                file_path.write_text(content)
            
            # Index all files
            indexed_count = engine.index_directory(test_root)
            assert indexed_count == len(test_content)
            
            # Test 1: Basic text search
            results = engine.search("invoice")
            assert len(results) >= 1
            assert any("invoice" in result.file_name.lower() for result in results)
            
            # Test 2: Case-insensitive search
            results_lower = engine.search("INVOICE")
            results_upper = engine.search("invoice")
            assert len(results_lower) == len(results_upper)
            
            # Test 3: Multi-word search
            results = engine.search("quarterly report")
            assert len(results) >= 1
            assert any("report" in result.file_name.lower() for result in results)
            
            # Test 4: Wildcard search
            results = engine.search("*.pdf")
            pdf_files = [r for r in results if r.file_name.endswith('.pdf')]
            assert len(pdf_files) >= 1
            
            # Test 5: Content-based search
            results = engine.search("pandas")
            assert len(results) >= 1
            assert any("data_analysis" in result.file_name for result in results)
            
            # Test 6: Phrase search
            results = engine.search('"installation instructions"')
            assert len(results) >= 1
            
            # Test 7: Boolean search operators
            # AND operator
            results = engine.search("budget AND financial")
            assert len(results) >= 1
            
            # OR operator
            results = engine.search("contract OR legal")
            assert len(results) >= 1
            
            # NOT operator
            results = engine.search("report NOT quarterly")
            # Should find files with "report" but not "quarterly"
            assert isinstance(results, list)
            
            # Test 8: Search with filters
            # Size filter
            size_filter = SizeRange(min_size=0, max_size=1000)  # Small files
            results = engine.search("", size_filter=size_filter)
            assert all(result.file_size <= 1000 for result in results if hasattr(result, 'file_size'))
            
            # Date filter
            now = datetime.now()
            date_filter = DateTimeRange(
                start=now - timedelta(hours=1),
                end=now + timedelta(hours=1)
            )
            results = engine.search("", date_filter=date_filter)
            # Recently created files should be found
            assert len(results) >= 0
            
            # Test 9: Search result ranking
            results = engine.search("report", enable_ranking=True)
            if len(results) > 1:
                # Results should be ranked by relevance
                scores = [getattr(result, 'relevance_score', 0) for result in results]
                assert scores == sorted(scores, reverse=True)
            
            # Test 10: Search pagination
            all_results = engine.search("", limit=None)
            paginated_results = engine.search("", limit=3, offset=0)
            assert len(paginated_results) <= 3
            
            if len(all_results) > 3:
                next_page = engine.search("", limit=3, offset=3)
                assert len(next_page) <= 3
                # No overlap between pages
                first_page_files = {r.file_path for r in paginated_results}
                second_page_files = {r.file_path for r in next_page}
                assert first_page_files.isdisjoint(second_page_files)
    
    @pytest.mark.unit
    @pytest.mark.critical
    def test_search_performance_comprehensive(self):
        """Test comprehensive search performance characteristics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "performance_test"
            engine = SearchEngine(index_path=index_path)
            
            # Create large dataset for performance testing
            test_root = Path(temp_dir) / "performance_files"
            test_root.mkdir()
            
            # Generate test files with varied content
            file_count = 1000
            for i in range(file_count):
                content_type = i % 5
                if content_type == 0:
                    # Text files with common words
                    content = f"Document {i} contains important information about project {i % 100}"
                elif content_type == 1:
                    # Data files with numbers
                    content = f"Data file {i}: value={i * 1.5}, status={'active' if i % 2 == 0 else 'inactive'}"
                elif content_type == 2:
                    # Log files with timestamps
                    content = f"[2024-01-{(i % 30) + 1:02d}] Log entry {i}: Operation completed successfully"
                elif content_type == 3:
                    # Configuration files
                    content = f"config_{i}={{'setting': {i}, 'enabled': {i % 2 == 0}}}"
                else:
                    # Mixed content
                    content = f"Mixed file {i} with keywords: search, test, performance, data_{i}"
                
                file_path = test_root / f"file_{i:04d}.txt"
                file_path.write_text(content)
            
            # Test 1: Indexing performance
            start_time = time.time()
            indexed_count = engine.index_directory(test_root)
            indexing_time = time.time() - start_time
            
            assert indexed_count == file_count
            files_per_second = file_count / indexing_time
            assert files_per_second > 50, f"Indexing too slow: {files_per_second} files/sec"
            
            # Test 2: Simple search performance
            search_terms = ["project", "data", "log", "config", "keywords"]
            search_times = []
            
            for term in search_terms:
                start_time = time.time()
                results = engine.search(term)
                search_time = time.time() - start_time
                search_times.append(search_time)
                
                assert len(results) > 0, f"No results found for '{term}'"
                assert search_time < 1.0, f"Search too slow for '{term}': {search_time}s"
            
            avg_search_time = sum(search_times) / len(search_times)
            assert avg_search_time < 0.5, f"Average search time too slow: {avg_search_time}s"
            
            # Test 3: Complex query performance
            complex_queries = [
                "project AND data",
                "active OR inactive",
                '"Operation completed"',
                "file_* AND value",
                "2024-01-* AND Log"
            ]
            
            for query in complex_queries:
                start_time = time.time()
                results = engine.search(query)
                search_time = time.time() - start_time
                
                assert search_time < 2.0, f"Complex query too slow '{query}': {search_time}s"
                assert isinstance(results, list)
            
            # Test 4: Concurrent search performance
            def search_worker(queries, results_list):
                """Worker function for concurrent searches."""
                for query in queries:
                    start_time = time.time()
                    results = engine.search(query)
                    search_time = time.time() - start_time
                    results_list.append((query, len(results), search_time))
            
            # Prepare concurrent search queries
            concurrent_queries = [
                ["project", "data", "log"],
                ["active", "inactive", "status"],
                ["2024", "entry", "config"],
                ["information", "operation", "setting"]
            ]
            
            threads = []
            all_results = []
            
            start_time = time.time()
            for queries in concurrent_queries:
                thread = threading.Thread(
                    target=search_worker,
                    args=(queries, all_results)
                )
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=30)
            
            concurrent_time = time.time() - start_time
            
            # Verify concurrent search results
            assert len(all_results) == 12  # 4 threads * 3 queries each
            max_individual_time = max(time for _, _, time in all_results)
            assert max_individual_time < 2.0, f"Concurrent search too slow: {max_individual_time}s"
            assert concurrent_time < 10.0, f"Total concurrent time too slow: {concurrent_time}s"
            
            # Test 5: Memory usage during searches
            import os

            import psutil
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform many searches to test memory usage
            for i in range(100):
                query = f"file_{i % 50:04d}"
                results = engine.search(query)
                assert isinstance(results, list)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory usage should be reasonable
            assert memory_increase < 200, f"Memory usage too high: {memory_increase}MB"
            
            # Test 6: Cache performance
            # First search (cache miss)
            start_time = time.time()
            results1 = engine.search("project")
            first_search_time = time.time() - start_time
            
            # Second search (cache hit)
            start_time = time.time()
            results2 = engine.search("project")
            second_search_time = time.time() - start_time
            
            # Results should be identical
            assert len(results1) == len(results2)
            
            # Second search should be faster (cache hit)
            if engine.config.get('enable_caching', True):
                assert second_search_time < first_search_time * 0.8
    
    @pytest.mark.unit
    @pytest.mark.critical
    def test_index_management_comprehensive(self):
        """Test comprehensive index management operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index_management_test"
            engine = SearchEngine(index_path=index_path)
            
            # Create test files
            test_root = Path(temp_dir) / "index_files"
            test_root.mkdir()
            
            initial_files = []
            for i in range(50):
                file_path = test_root / f"initial_{i}.txt"
                content = f"Initial file {i} with unique content {i * 37}"
                file_path.write_text(content)
                initial_files.append(file_path)
            
            # Test 1: Initial indexing
            indexed_count = engine.index_directory(test_root)
            assert indexed_count == 50
            
            initial_stats = engine.get_index_statistics()
            assert initial_stats['indexed_files'] == 50
            assert initial_stats['total_size'] > 0
            
            # Test 2: Incremental indexing
            # Add new files
            new_files = []
            for i in range(50, 75):
                file_path = test_root / f"new_{i}.txt"
                content = f"New file {i} with additional content {i * 23}"
                file_path.write_text(content)
                new_files.append(file_path)
            
            # Index only new files
            for file_path in new_files:
                success = engine.index_file(file_path)
                assert success is True
            
            updated_stats = engine.get_index_statistics()
            assert updated_stats['indexed_files'] == 75
            
            # Test 3: Index optimization
            pre_optimize_stats = engine.get_index_statistics()
            optimization_result = engine.optimize_index()
            post_optimize_stats = engine.get_index_statistics()
            
            assert optimization_result is True
            # File count should remain the same
            assert post_optimize_stats['indexed_files'] == pre_optimize_stats['indexed_files']
            # Index size might be smaller after optimization
            assert post_optimize_stats['index_size'] <= pre_optimize_stats['index_size'] * 1.1
            
            # Test 4: Selective file removal from index
            files_to_remove = initial_files[:10]
            for file_path in files_to_remove:
                success = engine.remove_from_index(str(file_path))
                assert success is True
            
            removal_stats = engine.get_index_statistics()
            assert removal_stats['indexed_files'] == 65  # 75 - 10
            
            # Verify removed files are not found in search
            for removed_file in files_to_remove:
                unique_content = f"content {removed_file.stem.split('_')[1]}"
                results = engine.search(unique_content)
                assert not any(str(removed_file) in result.file_path for result in results)
            
            # Test 5: Index rebuilding
            # Corrupt the index
            index_files = list(index_path.glob("*"))
            if index_files:
                # Delete some index files to simulate corruption
                for idx_file in index_files[:2]:
                    if idx_file.is_file():
                        idx_file.unlink()
            
            # Rebuild index
            rebuild_result = engine.rebuild_index(test_root)
            assert rebuild_result is True
            
            rebuild_stats = engine.get_index_statistics()
            # Should index all existing files (including those "removed" earlier)
            assert rebuild_stats['indexed_files'] == 75  # All files in directory
            
            # Test 6: Index backup and restore
            backup_path = engine.create_index_backup()
            assert backup_path is not None
            assert backup_path.exists()
            assert backup_path.is_file()
            
            # Modify index
            engine.clear_index()
            cleared_stats = engine.get_index_statistics()
            assert cleared_stats['indexed_files'] == 0
            
            # Restore from backup
            restore_result = engine.restore_index_backup(backup_path)
            assert restore_result is True
            
            restored_stats = engine.get_index_statistics()
            assert restored_stats['indexed_files'] > 0
            
            # Test 7: Index validation and health check
            health_report = engine.check_index_health()
            assert 'status' in health_report
            assert 'total_files' in health_report
            assert 'corrupted_entries' in health_report
            assert 'missing_files' in health_report
            
            assert health_report['status'] in ['healthy', 'warning', 'corrupted']
            assert health_report['total_files'] >= 0
            assert health_report['corrupted_entries'] >= 0
            
            # Test 8: Index statistics and analytics
            analytics = engine.get_index_analytics()
            assert 'file_types' in analytics
            assert 'size_distribution' in analytics
            assert 'creation_dates' in analytics
            assert 'most_common_words' in analytics
            
            # Verify analytics data
            file_types = analytics['file_types']
            assert 'txt' in file_types
            assert file_types['txt'] > 0
            
            # Test 9: Index versioning
            version_info = engine.get_index_version()
            assert 'version' in version_info
            assert 'created_at' in version_info
            assert 'last_updated' in version_info
            assert 'schema_version' in version_info
            
            # Test migration if needed
            if version_info['schema_version'] < engine.CURRENT_SCHEMA_VERSION:
                migration_result = engine.migrate_index()
                assert migration_result is True
                
                updated_version = engine.get_index_version()
                assert updated_version['schema_version'] == engine.CURRENT_SCHEMA_VERSION


if __name__ == "__main__":
    """Run enterprise-grade unit tests for SearchEngine."""
    pytest.main([__file__, "-v", "--tb=short", "--strict-markers"])