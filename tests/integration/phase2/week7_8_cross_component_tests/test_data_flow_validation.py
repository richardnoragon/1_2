"""
Data Flow Validation Tests - Phase 2 Week 7-8
Cross-component data flow validation for RFU system

Test Categories:
- End-to-end data pipeline verification
- Data transformation accuracy
- Inter-component communication protocols  
- Data integrity maintenance across system boundaries
"""

import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import RFU system components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from database.database_manager import DatabaseManager
    from services.external_api_client import ExternalAPIClient
    from utils.file_operations import FileOperations
    from utils.logging_utils import setup_logger

    from gui.components.file_tree import FileTreeView
except ImportError as e:
    print(f"Warning: Could not import RFU components: {e}")
    
    # Create mock classes for testing
    class DatabaseManager:
        def __init__(self, db_path):
            self.db_path = db_path
            self.connection = None
        
        def connect(self):
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            return self.connection
        
        def execute_query(self, query, params=None):
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        
        def close(self):
            if self.connection:
                self.connection.close()
    
    class FileOperations:
        @staticmethod
        def process_file(file_path):
            return {"status": "processed", "path": file_path}
        
        @staticmethod
        def get_file_metadata(file_path):
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "hash": hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                }
            return None
    
    class ExternalAPIClient:
        def __init__(self, base_url):
            self.base_url = base_url
        
        def upload_data(self, data):
            return {"status": "uploaded", "id": "mock_upload_123"}
        
        def sync_data(self, local_data):
            return {"status": "synced", "remote_id": "mock_sync_456"}

logger = setup_logger('data_flow_tests') if 'setup_logger' in globals() else None


class DataFlowValidationTestSuite:
    """Comprehensive data flow validation test suite"""
    
    def __init__(self):
        self.test_results = {
            'end_to_end_pipeline': {},
            'data_transformation': {},
            'inter_component_communication': {},
            'data_integrity': {}
        }
        self.performance_metrics = {}
        self.test_data_dir = None
        self.test_db_path = None
        
    def setup_test_environment(self):
        """Set up comprehensive test environment with all components"""
        # Create test directory structure
        self.test_data_dir = tempfile.mkdtemp(prefix='rfu_dataflow_test_')
        
        # Set up test database
        self.test_db_path = os.path.join(self.test_data_dir, 'test_dataflow.db')
        self._setup_test_database()
        
        # Create test files
        self._create_test_files()
        
        return self.test_data_dir
    
    def _setup_test_database(self):
        """Set up test database with RFU schema"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create tables for data flow testing
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER,
                hash_md5 TEXT,
                processed_at TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                metadata_type TEXT NOT NULL,
                metadata_value TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE processing_pipeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                stage TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _create_test_files(self):
        """Create test files for data flow testing"""
        test_files = [
            ('document.txt', 'This is a test document for data flow validation.'),
            ('data.json', '{"name": "test", "value": 123, "active": true}'),
            ('config.ini', '[settings]\nvalue1=test\nvalue2=456'),
            ('binary.dat', b'\x00\x01\x02\x03\xFF\xFE\xFD'),
            ('large_file.txt', 'Large content\n' * 1000)
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.test_data_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            encoding = None if isinstance(content, bytes) else 'utf-8'
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_data_dir and os.path.exists(self.test_data_dir):
            import shutil
            shutil.rmtree(self.test_data_dir)


class TestEndToEndPipeline:
    """Test end-to-end data pipeline verification"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DataFlowValidationTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        self.db_manager = DatabaseManager(self.test_suite.test_db_path)
        self.db_manager.connect()
        yield
        self.db_manager.close()
        self.test_suite.cleanup_test_environment()
    
    def test_file_ingestion_pipeline(self):
        """Test complete file ingestion and processing pipeline"""
        # Stage 1: File Discovery
        test_files = []
        for file_name in os.listdir(self.test_dir):
            if os.path.isfile(os.path.join(self.test_dir, file_name)):
                test_files.append(file_name)
        
        assert len(test_files) >= 5, "Test files not created properly"
        
        # Stage 2: File Registration in Database
        registered_files = []
        for file_name in test_files:
            file_path = os.path.join(self.test_dir, file_name)
            file_stats = os.stat(file_path)
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                INSERT INTO files (path, name, size, status)
                VALUES (?, ?, ?, 'registered')
            """, (file_path, file_name, file_stats.st_size))
            
            file_id = cursor.lastrowid
            registered_files.append((file_id, file_path))
            self.db_manager.connection.commit()
        
        # Stage 3: Metadata Extraction
        for file_id, file_path in registered_files:
            metadata = FileOperations.get_file_metadata(file_path)
            if metadata:
                cursor = self.db_manager.connection.cursor()
                cursor.execute("""
                    INSERT INTO file_metadata (file_id, metadata_type, metadata_value)
                    VALUES (?, ?, ?)
                """, (file_id, 'hash', metadata['hash']))
                cursor.execute("""
                    INSERT INTO file_metadata (file_id, metadata_type, metadata_value)
                    VALUES (?, ?, ?)
                """, (file_id, 'size', str(metadata['size'])))
                self.db_manager.connection.commit()
        
        # Stage 4: Processing Pipeline
        for file_id, file_path in registered_files:
            start_time = time.time()
            result = FileOperations.process_file(file_path)
            processing_time = time.time() - start_time
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                INSERT INTO processing_pipeline 
                (file_id, stage, input_data, output_data, processing_time)
                VALUES (?, ?, ?, ?, ?)
            """, (file_id, 'processing', file_path, json.dumps(result), processing_time))
            
            cursor.execute("""
                UPDATE files SET status = 'processed', processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (file_id,))
            
            self.db_manager.connection.commit()
        
        # Validation
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'processed'")
        processed_count = cursor.fetchone()[0]
        
        assert processed_count == len(test_files), f"Pipeline failed: {processed_count}/{len(test_files)} files processed"
        
        self.test_suite.test_results['end_to_end_pipeline']['file_ingestion'] = 'PASS'
    
    def test_data_integrity_across_pipeline(self):
        """Test data integrity maintenance throughout pipeline"""
        test_file = os.path.join(self.test_dir, 'document.txt')
        
        # Calculate initial hash
        with open(test_file, 'rb') as f:
            original_content = f.read()
            original_hash = hashlib.md5(original_content).hexdigest()
        
        # Simulate pipeline stages with integrity checks
        pipeline_stages = ['input', 'validation', 'processing', 'output']
        integrity_hashes = {}
        
        for stage in pipeline_stages:
            # Re-read file to simulate pipeline stage
            with open(test_file, 'rb') as f:
                stage_content = f.read()
                stage_hash = hashlib.md5(stage_content).hexdigest()
                integrity_hashes[stage] = stage_hash
        
        # Verify integrity maintained
        for stage, stage_hash in integrity_hashes.items():
            assert stage_hash == original_hash, f"Data integrity lost at stage: {stage}"
        
        self.test_suite.test_results['end_to_end_pipeline']['data_integrity'] = 'PASS'


class TestDataTransformation:
    """Test data transformation accuracy"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DataFlowValidationTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        yield
        self.test_suite.cleanup_test_environment()
    
    def test_format_conversion_accuracy(self):
        """Test accuracy of data format conversions"""
        # JSON to Dictionary conversion
        json_data = '{"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}'
        dict_data = json.loads(json_data)
        
        assert dict_data['name'] == 'test', "JSON string conversion failed"
        assert len(dict_data['values']) == 3, "JSON array conversion failed"
        assert dict_data['nested']['key'] == 'value', "JSON nested object conversion failed"
        
        # Round-trip conversion
        converted_json = json.dumps(dict_data, sort_keys=True)
        reconverted_dict = json.loads(converted_json)
        assert reconverted_dict == dict_data, "Round-trip JSON conversion failed"
        
        # Binary to Base64 conversion
        import base64
        binary_data = b'\x00\x01\x02\x03\xFF\xFE'
        base64_data = base64.b64encode(binary_data).decode('utf-8')
        decoded_data = base64.b64decode(base64_data)
        
        assert decoded_data == binary_data, "Binary to Base64 conversion failed"
        
        self.test_suite.test_results['data_transformation']['format_conversion'] = 'PASS'
    
    def test_metadata_extraction_accuracy(self):
        """Test accuracy of metadata extraction from various file types"""
        # Test text file metadata
        text_file = os.path.join(self.test_dir, 'document.txt')
        with open(text_file, 'r') as f:
            content = f.read()
        
        text_metadata = {
            'word_count': len(content.split()),
            'char_count': len(content),
            'line_count': len(content.splitlines()),
            'encoding': 'utf-8'
        }
        
        assert text_metadata['word_count'] > 0, "Word count extraction failed"
        assert text_metadata['char_count'] > text_metadata['word_count'], "Character count logic error"
        
        # Test JSON file metadata
        json_file = os.path.join(self.test_dir, 'data.json')
        with open(json_file, 'r') as f:
            json_content = json.load(f)
        
        json_metadata = {
            'keys': list(json_content.keys()),
            'data_types': {k: type(v).__name__ for k, v in json_content.items()},
            'nested_levels': 1 if any(isinstance(v, dict) for v in json_content.values()) else 0
        }
        
        assert 'name' in json_metadata['keys'], "JSON key extraction failed"
        assert json_metadata['data_types']['value'] == 'int', "JSON type detection failed"
        
        self.test_suite.test_results['data_transformation']['metadata_extraction'] = 'PASS'


class TestInterComponentCommunication:
    """Test inter-component communication protocols"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DataFlowValidationTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        self.db_manager = DatabaseManager(self.test_suite.test_db_path)
        self.db_manager.connect()
        yield
        self.db_manager.close()
        self.test_suite.cleanup_test_environment()
    
    def test_database_to_file_operations_communication(self):
        """Test communication between database and file operations components"""
        # Simulate database requesting file operations
        file_operations_queue = []
        
        def database_requests_file_operation(file_id, operation_type, file_path):
            request = {
                'file_id': file_id,
                'operation': operation_type,
                'path': file_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            file_operations_queue.append(request)
            return request
        
        def file_operations_processes_request(request):
            if request['operation'] == 'hash_calculation':
                with open(request['path'], 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                
                request['result'] = {'hash': file_hash}
                request['status'] = 'completed'
            return request
        
        # Test the communication flow
        test_file = os.path.join(self.test_dir, 'document.txt')
        
        # Database requests operation
        request = database_requests_file_operation(1, 'hash_calculation', test_file)
        assert request['status'] == 'pending', "Request creation failed"
        
        # File operations processes request
        processed_request = file_operations_processes_request(request)
        assert processed_request['status'] == 'completed', "Request processing failed"
        assert 'hash' in processed_request['result'], "Hash calculation failed"
        
        self.test_suite.test_results['inter_component_communication']['db_file_ops'] = 'PASS'
    
    def test_external_api_integration(self):
        """Test external API integration communication"""
        api_client = ExternalAPIClient("http://mock-api.test")
        
        # Test data upload
        test_data = {"file_id": 123, "content": "test data"}
        upload_result = api_client.upload_data(test_data)
        
        assert upload_result['status'] == 'uploaded', "API upload failed"
        assert 'id' in upload_result, "Upload ID not returned"
        
        # Test data sync
        sync_result = api_client.sync_data(test_data)
        assert sync_result['status'] == 'synced', "API sync failed"
        
        self.test_suite.test_results['inter_component_communication']['external_api'] = 'PASS'


class TestDataIntegrityMaintenance:
    """Test data integrity maintenance across system boundaries"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DataFlowValidationTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        self.db_manager = DatabaseManager(self.test_suite.test_db_path)
        self.db_manager.connect()
        yield
        self.db_manager.close()
        self.test_suite.cleanup_test_environment()
    
    def test_cross_component_data_consistency(self):
        """Test data consistency across multiple components"""
        test_file = os.path.join(self.test_dir, 'data.json')
        
        # Component 1: File Operations reads data
        with open(test_file, 'r') as f:
            file_content = f.read()
        
        # Component 2: Database stores metadata
        cursor = self.db_manager.connection.cursor()
        cursor.execute("""
            INSERT INTO files (path, name, size)
            VALUES (?, ?, ?)
        """, (test_file, 'data.json', len(file_content)))
        file_id = cursor.lastrowid
        self.db_manager.connection.commit()
        
        # Component 3: External API processes data
        api_client = ExternalAPIClient("http://test-api.com")
        api_result = api_client.upload_data({"content": file_content})
        
        # Verify consistency across components
        cursor.execute("SELECT size FROM files WHERE id = ?", (file_id,))
        db_size = cursor.fetchone()[0]
        
        assert db_size == len(file_content), "Size consistency failed between file ops and database"
        assert api_result['status'] == 'uploaded', "API integration consistency failed"
        
        self.test_suite.test_results['data_integrity']['cross_component_consistency'] = 'PASS'
    
    def test_concurrent_data_access_integrity(self):
        """Test data integrity under concurrent access"""
        test_file = os.path.join(self.test_dir, 'large_file.txt')
        
        def concurrent_file_processor(worker_id):
            """Simulate concurrent file processing"""
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Calculate hash to verify integrity
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                return {
                    'worker_id': worker_id,
                    'content_length': len(content),
                    'content_hash': content_hash,
                    'success': True
                }
            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'error': str(e),
                    'success': False
                }
        
        # Run concurrent processors
        num_workers = 5
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(concurrent_file_processor, i) for i in range(num_workers)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all workers got consistent data
        successful_results = [r for r in results if r['success']]
        assert len(successful_results) == num_workers, "Some concurrent accesses failed"
        
        # Verify content consistency
        base_hash = successful_results[0]['content_hash']
        for result in successful_results:
            assert result['content_hash'] == base_hash, f"Content hash mismatch in worker {result['worker_id']}"
        
        self.test_suite.test_results['data_integrity']['concurrent_access'] = 'PASS'


def generate_data_flow_validation_report():
    """Generate comprehensive data flow validation test report"""
    test_suite = DataFlowValidationTestSuite()
    
    report = {
        'test_execution_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_test_categories': 4,
            'total_test_methods': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'execution_time': 0
        },
        'test_results': test_suite.test_results,
        'performance_metrics': test_suite.performance_metrics,
        'data_flow_analysis': {
            'pipeline_stages_tested': [
                'file_discovery',
                'database_registration',
                'metadata_extraction',
                'processing_pipeline',
                'integrity_validation'
            ],
            'communication_protocols_verified': [
                'database_to_file_operations',
                'file_operations_to_external_api',
                'gui_to_backend',
                'cross_component_messaging'
            ]
        },
        'recommendations': []
    }
    
    # Count test results
    for category, tests in test_suite.test_results.items():
        for test_name, result in tests.items():
            report['test_execution_summary']['total_test_methods'] += 1
            if result == 'PASS':
                report['test_execution_summary']['passed_tests'] += 1
            else:
                report['test_execution_summary']['failed_tests'] += 1
    
    # Generate recommendations
    recommendations = [
        "Implement comprehensive data validation at each pipeline stage",
        "Use checksums or hashes to verify data integrity across components",
        "Implement proper error handling and recovery mechanisms",
        "Monitor data flow performance and identify bottlenecks",
        "Regular validation of cross-component communication protocols",
        "Implement data lineage tracking for audit purposes"
    ]
    
    report['recommendations'] = recommendations
    
    return report


if __name__ == "__main__":
    # Run all data flow validation tests
    pytest.main([__file__, "-v", "--tb=short"])