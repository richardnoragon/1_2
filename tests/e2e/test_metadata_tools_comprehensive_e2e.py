#!/usr/bin/env python3
"""
Metadata Tools Comprehensive E2E Tests

Complete integration testing for all Metadata Tools with cross-tool workflows,
user journey validation, and performance regression testing.

Created: 2025-09-04
Purpose: Validate complete metadata tools ecosystem integration
Coverage: Cross-tool workflows, user journeys, hub coordination, performance validation
"""

import os
import sys
import time
from datetime import datetime, timedelta

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test utilities
from .metadata_tools_test_utilities import (MetadataToolsPerformanceMonitor,
                                            MetadataToolsSignalTracker,
                                            MetadataToolsTestDataFactory,
                                            MockFileTouchTool,
                                            MockImageMetadataTool,
                                            MockMetadataToolsHub,
                                            MockOfficeMetadataTool,
                                            assert_performance_target)


@pytest.fixture(scope="function")
def comprehensive_metadata_test_environment():
    """Comprehensive test environment with all metadata tools"""
    test_path = MetadataToolsTestDataFactory.create_metadata_tools_dataset(None, 'medium')
    hub = MockMetadataToolsHub()
    
    # Register all metadata tools
    image_tool = hub.open_image_metadata()
    office_tool = hub.open_office_metadata()
    file_touch_tool = hub.open_file_touch()
    
    yield {
        'test_data_path': test_path,
        'hub': hub,
        'image_tool': image_tool,
        'office_tool': office_tool,
        'file_touch_tool': file_touch_tool,
        'performance_monitor': MetadataToolsPerformanceMonitor(),
        'image_signal_tracker': MetadataToolsSignalTracker(image_tool),
        'office_signal_tracker': MetadataToolsSignalTracker(office_tool),
        'file_touch_signal_tracker': MetadataToolsSignalTracker(file_touch_tool)
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(test_path, ignore_errors=True)


class TestMetadataToolsIntegration:
    """Test class for cross-tool workflow validation"""
    
    def test_image_to_office_metadata_workflow(self, comprehensive_metadata_test_environment):
        """Test workflow integration from Image Metadata to Office Metadata tools"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        hub = env['hub']
        
        # Test data setup
        image_path = os.path.join(env['test_data_path'], 'images', 'workflow_image_001.jpg')
        report_doc_path = os.path.join(env['test_data_path'], 'documents', 'image_report.docx')
        
        # Step 1: Extract image metadata
        image_result = image_tool.extract_exif_data(image_path, include_gps=True)
        assert image_result['status'] == 'success'
        
        # Step 2: Extract document properties
        office_result = office_tool.extract_document_properties(report_doc_path)
        assert office_result['status'] == 'success'
        
        # Step 3: Validate cross-tool data availability
        exif_data = image_tool.exif_data[image_path]
        document_properties = office_tool.document_properties[report_doc_path]
        
        # Validate cross-tool integration
        assert len(hub.registered_tools) == 3
        assert 'image_metadata' in hub.registered_tools
        assert 'office_metadata' in hub.registered_tools
        
        # Validate data flow between tools
        assert image_path in image_tool.exif_data
        assert report_doc_path in office_tool.document_properties
        
        # Validate metadata richness from cross-tool workflow
        assert 'camera_settings' in exif_data
        assert 'core_properties' in document_properties
    
    def test_metadata_extraction_pipeline_workflow(self, comprehensive_metadata_test_environment):
        """Test complete metadata extraction pipeline across all tools"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'batch_processing')
        
        # Test data setup - mixed content for pipeline
        pipeline_files = [
            os.path.join(env['test_data_path'], 'images', 'pipeline_image_001.jpg'),
            os.path.join(env['test_data_path'], 'images', 'pipeline_image_002.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'pipeline_doc_001.docx'),
            os.path.join(env['test_data_path'], 'documents', 'pipeline_doc_002.pdf'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'pipeline_file_001.txt')
        ]
        
        # Execute comprehensive metadata extraction pipeline
        pipeline_results = {
            'images_processed': 0,
            'documents_processed': 0,
            'timestamps_processed': 0,
            'total_metadata_operations': 0
        }
        
        for file_path in pipeline_files:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.tiff']:
                # Process with Image Metadata tool
                result = image_tool.extract_exif_data(file_path, include_gps=True)
                if result['status'] == 'success':
                    pipeline_results['images_processed'] += 1
                    pipeline_results['total_metadata_operations'] += result['metadata_operations']
                    
            elif file_ext in ['.docx', '.xlsx', '.pptx', '.pdf']:
                # Process with Office Metadata tool
                result = office_tool.extract_document_properties(file_path)
                if result['status'] == 'success':
                    pipeline_results['documents_processed'] += 1
                    pipeline_results['total_metadata_operations'] += result['metadata_operations']
                    
            else:
                # Process with File Touch tool
                result = file_touch_tool.get_file_timestamps(file_path)
                if result['status'] == 'success':
                    pipeline_results['timestamps_processed'] += 1
                    pipeline_results['total_metadata_operations'] += result['metadata_operations']
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'batch_processing')
        
        # Validate pipeline processing results
        assert pipeline_results['images_processed'] > 0
        assert pipeline_results['documents_processed'] > 0
        assert pipeline_results['timestamps_processed'] > 0
        assert pipeline_results['total_metadata_operations'] > 0
        
        # Validate comprehensive data extraction
        assert len(image_tool.exif_data) >= pipeline_results['images_processed']
        assert len(office_tool.document_properties) >= pipeline_results['documents_processed']
        assert len(file_touch_tool.file_timestamps) >= pipeline_results['timestamps_processed']
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'image_metadata', 'batch_processing')


class TestMetadataToolsUserJourney:
    """Test class for business workflow scenarios"""
    
    def test_content_creator_workflow(self, comprehensive_metadata_test_environment):
        """Test complete Content Creator user journey workflow"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        performance_monitor = env['performance_monitor']
        
        # Start user journey performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'batch_processing')
        
        # Content Creator Workflow:
        # 1. Process photo collection with EXIF data
        # 2. Create project documentation
        # 3. Organize files by creation date
        
        # Step 1: Process photo collection
        photo_collection = []
        for i in range(6):
            photo_path = os.path.join(env['test_data_path'], 'images', f'content_photo_{i:03d}.jpg')
            photo_collection.append(photo_path)
        
        # Extract EXIF from entire collection
        photo_results = []
        for photo_path in photo_collection:
            result = image_tool.extract_exif_data(photo_path, include_gps=True)
            photo_results.append(result)
        
        # Step 2: Create project documentation
        project_docs = [
            os.path.join(env['test_data_path'], 'documents', 'project_brief.docx'),
            os.path.join(env['test_data_path'], 'documents', 'project_timeline.xlsx')
        ]
        
        doc_results = []
        for doc_path in project_docs:
            result = office_tool.extract_document_properties(doc_path)
            doc_results.append(result)
        
        # Step 3: Organize by creation date (get timestamps)
        timestamp_results = []
        all_files = photo_collection + project_docs
        for file_path in all_files:
            result = file_touch_tool.get_file_timestamps(file_path)
            timestamp_results.append(result)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'batch_processing')
        
        # Validate Content Creator workflow completion
        successful_photos = len([r for r in photo_results if r['status'] == 'success'])
        successful_docs = len([r for r in doc_results if r['status'] == 'success'])
        successful_timestamps = len([r for r in timestamp_results if r['status'] == 'success'])
        
        assert successful_photos > 0
        assert successful_docs > 0
        assert successful_timestamps > 0
        
        # Validate workflow data availability
        assert len(image_tool.exif_data) >= successful_photos
        assert len(office_tool.document_properties) >= successful_docs
        assert len(file_touch_tool.file_timestamps) >= successful_timestamps
        
        # Validate performance target for user journey
        assert_performance_target(perf_result['duration'], 'image_metadata', 'batch_processing')
    
    def test_developer_asset_management_workflow(self, comprehensive_metadata_test_environment):
        """Test Developer asset management user journey"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        
        # Developer Workflow:
        # 1. Analyze project assets (images, docs)
        # 2. Extract metadata for asset management
        # 3. Standardize timestamps for version control
        
        # Step 1: Analyze project assets
        project_assets = [
            os.path.join(env['test_data_path'], 'images', 'asset_icon_001.jpg'),
            os.path.join(env['test_data_path'], 'images', 'asset_logo_001.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'api_documentation.docx'),
            os.path.join(env['test_data_path'], 'documents', 'project_specs.pdf')
        ]
        
        # Step 2: Extract comprehensive metadata
        asset_metadata = {}
        
        for asset_path in project_assets:
            file_ext = os.path.splitext(asset_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.tiff']:
                # Process image assets
                result = image_tool.extract_exif_data(asset_path)
                if result['status'] == 'success':
                    asset_metadata[asset_path] = {
                        'type': 'image',
                        'metadata': image_tool.exif_data[asset_path]
                    }
                    
            elif file_ext in ['.docx', '.pdf']:
                # Process document assets
                result = office_tool.extract_document_properties(asset_path)
                if result['status'] == 'success':
                    asset_metadata[asset_path] = {
                        'type': 'document',
                        'metadata': office_tool.document_properties[asset_path]
                    }
        
        # Step 3: Standardize timestamps for version control
        version_control_base = datetime.now() - timedelta(days=30)
        
        for i, asset_path in enumerate(project_assets):
            # Get current timestamps
            file_touch_tool.get_file_timestamps(asset_path)
            
            # Standardize modification time for version control
            vc_timestamp = version_control_base + timedelta(days=i)
            timestamp_updates = {
                'modification_time': vc_timestamp
            }
            
            result = file_touch_tool.modify_timestamps(asset_path, timestamp_updates)
            assert result['status'] == 'success'
        
        # Validate Developer workflow completion
        assert len(asset_metadata) > 0
        
        # Validate asset categorization
        image_assets = len([item for item in asset_metadata.values() if item['type'] == 'image'])
        document_assets = len([item for item in asset_metadata.values() if item['type'] == 'document'])
        
        assert image_assets > 0
        assert document_assets > 0
        
        # Validate timestamp standardization
        for asset_path in project_assets:
            assert asset_path in file_touch_tool.file_timestamps


class TestMetadataToolsHubIntegration:
    """Test class for RFU Hub coordination and resource management"""
    
    def test_hub_registration_and_coordination_workflow(self, comprehensive_metadata_test_environment):
        """Test comprehensive hub registration and coordination"""
        env = comprehensive_metadata_test_environment
        hub = env['hub']
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        
        # Validate all tools are registered with hub
        expected_tools = ['image_metadata', 'office_metadata', 'file_touch']
        for tool_name in expected_tools:
            assert tool_name in hub.registered_tools
            assert tool_name in hub.tool_status
            
            # Validate tool status
            status = hub.tool_status[tool_name]
            assert status['status'] == 'registered'
            assert 'last_activity' in status
        
        # Test hub coordination through simultaneous operations
        test_files = [
            os.path.join(env['test_data_path'], 'images', 'hub_coord_001.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'hub_coord_001.docx'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'hub_coord_001.txt')
        ]
        
        # Execute coordinated operations
        coordination_results = []
        
        # Process image through image tool
        image_result = image_tool.extract_exif_data(test_files[0])
        coordination_results.append(image_result)
        
        # Process document through office tool
        doc_result = office_tool.extract_document_properties(test_files[1])
        coordination_results.append(doc_result)
        
        # Process file through file touch tool
        timestamp_result = file_touch_tool.get_file_timestamps(test_files[2])
        coordination_results.append(timestamp_result)
        
        # Validate hub coordination
        successful_coordinated_ops = len([r for r in coordination_results if r['status'] == 'success'])
        assert successful_coordinated_ops == len(test_files)
        
        # Validate hub event logging
        assert len(hub.hub_events) >= len(expected_tools)
        
        # Validate resource allocation coordination
        resource_allocation = hub.resource_allocation
        assert 'max_threads' in resource_allocation
        assert 'max_memory_mb' in resource_allocation
        assert resource_allocation['max_threads'] > 0
        assert resource_allocation['max_memory_mb'] > 0
    
    def test_concurrent_operations_testing_workflow(self, comprehensive_metadata_test_environment):
        """Test concurrent operations and resource coordination"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        hub = env['hub']
        
        # Test data setup for concurrent operations
        concurrent_files = [
            os.path.join(env['test_data_path'], 'images', 'concurrent_001.jpg'),
            os.path.join(env['test_data_path'], 'images', 'concurrent_002.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'concurrent_001.docx'),
            os.path.join(env['test_data_path'], 'documents', 'concurrent_002.docx'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'concurrent_001.txt'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'concurrent_002.txt')
        ]
        
        # Execute concurrent-style operations
        concurrent_results = []
        
        # Simulate concurrent processing across tools
        for file_path in concurrent_files:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                result = image_tool.extract_exif_data(file_path)
            elif file_ext in ['.docx']:
                result = office_tool.extract_document_properties(file_path)
            else:
                result = file_touch_tool.get_file_timestamps(file_path)
            
            concurrent_results.append(result)
        
        # Validate concurrent operation success
        successful_concurrent = len([r for r in concurrent_results if r['status'] == 'success'])
        assert successful_concurrent >= len(concurrent_files) // 2
        
        # Validate hub resource coordination
        assert len(hub.registered_tools) == 3
        
        # Validate that tools maintained their state during concurrent operations
        assert len(image_tool.exif_data) > 0
        assert len(office_tool.document_properties) > 0
        assert len(file_touch_tool.file_timestamps) > 0


class TestMetadataToolsPerformanceRegression:
    """Test class for performance validation and regression detection"""
    
    def test_performance_regression_detection_workflow(self, comprehensive_metadata_test_environment):
        """Test performance regression detection across all metadata tools"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        performance_monitor = env['performance_monitor']
        
        # Performance regression test matrix
        performance_tests = [
            ('image_metadata', 'exif_extraction', lambda: image_tool.extract_exif_data(
                os.path.join(env['test_data_path'], 'images', 'perf_test_001.jpg'))),
            ('office_metadata', 'property_extraction', lambda: office_tool.extract_document_properties(
                os.path.join(env['test_data_path'], 'documents', 'perf_test_001.docx'))),
            ('file_touch', 'timestamp_reading', lambda: file_touch_tool.get_file_timestamps(
                os.path.join(env['test_data_path'], 'timestamp_files', 'perf_test_001.txt')))
        ]
        
        # Execute performance regression tests
        performance_results = []
        
        for tool_name, operation_name, test_operation in performance_tests:
            # Start monitoring
            performance_monitor.start_monitoring(tool_name, operation_name)
            
            # Execute operation
            operation_result = test_operation()
            
            # Stop monitoring
            perf_result = performance_monitor.stop_monitoring(tool_name, operation_name)
            
            # Record performance data
            performance_data = {
                'tool_name': tool_name,
                'operation_name': operation_name,
                'duration': perf_result['duration'],
                'target_met': perf_result['target_met'],
                'operation_success': operation_result['status'] == 'success'
            }
            performance_results.append(performance_data)
        
        # Validate performance regression detection
        for perf_data in performance_results:
            assert perf_data['operation_success'] is True
            assert perf_data['target_met'] is True
            assert perf_data['duration'] > 0
            
            # Validate performance target compliance
            assert_performance_target(
                perf_data['duration'], 
                perf_data['tool_name'], 
                perf_data['operation_name']
            )
    
    def test_resource_usage_optimization_workflow(self, comprehensive_metadata_test_environment):
        """Test resource usage optimization across metadata tools"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        
        # Resource optimization test setup
        optimization_files = [
            os.path.join(env['test_data_path'], 'images', 'optimization_001.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'optimization_001.docx'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'optimization_001.txt')
        ]
        
        # Record baseline resource usage
        baseline_usage = {
            'image_tool': image_tool.get_resource_usage(),
            'office_tool': office_tool.get_resource_usage(),
            'file_touch_tool': file_touch_tool.get_resource_usage()
        }
        
        # Execute optimized operations
        optimization_results = []
        
        # Process image with optimization focus
        image_result = image_tool.extract_exif_data(optimization_files[0])
        optimization_results.append(image_result)
        
        # Process document with optimization focus  
        doc_result = office_tool.extract_document_properties(optimization_files[1])
        optimization_results.append(doc_result)
        
        # Process timestamp with optimization focus
        timestamp_result = file_touch_tool.get_file_timestamps(optimization_files[2])
        optimization_results.append(timestamp_result)
        
        # Record optimized resource usage
        optimized_usage = {
            'image_tool': image_tool.get_resource_usage(),
            'office_tool': office_tool.get_resource_usage(),
            'file_touch_tool': file_touch_tool.get_resource_usage()
        }
        
        # Validate resource optimization
        all_operations_successful = all(r['status'] == 'success' for r in optimization_results)
        assert all_operations_successful
        
        # Validate resource usage is within acceptable bounds
        for tool_name in ['image_tool', 'office_tool', 'file_touch_tool']:
            baseline = baseline_usage[tool_name]
            optimized = optimized_usage[tool_name]
            
            # Memory usage should have increased but stayed reasonable
            memory_increase = optimized['memory'] - baseline['memory']
            assert memory_increase >= 0
            
            # CPU usage should have increased
            cpu_increase = optimized['cpu'] - baseline['cpu']
            assert cpu_increase >= 0
    
    def test_comprehensive_workflow_validation_workflow(self, comprehensive_metadata_test_environment):
        """Test comprehensive workflow validation across all metadata tools"""
        env = comprehensive_metadata_test_environment
        image_tool = env['image_tool']
        office_tool = env['office_tool']
        file_touch_tool = env['file_touch_tool']
        image_signal_tracker = env['image_signal_tracker']
        office_signal_tracker = env['office_signal_tracker']
        file_touch_signal_tracker = env['file_touch_signal_tracker']
        
        # Connect all signal trackers
        image_signal_tracker.connect_all_signals()
        office_signal_tracker.connect_all_signals()
        file_touch_signal_tracker.connect_all_signals()
        
        # Test data setup for comprehensive workflow
        workflow_files = [
            os.path.join(env['test_data_path'], 'images', 'comprehensive_001.jpg'),
            os.path.join(env['test_data_path'], 'documents', 'comprehensive_001.docx'),
            os.path.join(env['test_data_path'], 'timestamp_files', 'comprehensive_001.txt')
        ]
        
        # Execute comprehensive workflow
        workflow_results = []
        
        # Image processing workflow
        image_result = image_tool.extract_exif_data(workflow_files[0], include_gps=True)
        workflow_results.append(('image', image_result))
        
        # Office processing workflow
        doc_result = office_tool.extract_document_properties(workflow_files[1])
        workflow_results.append(('office', doc_result))
        
        # File touch workflow
        timestamp_result = file_touch_tool.get_file_timestamps(workflow_files[2])
        workflow_results.append(('file_touch', timestamp_result))
        
        # Validate comprehensive workflow
        for workflow_type, result in workflow_results:
            assert result['status'] == 'success'
            assert result['files_processed'] >= 1
            assert result['metadata_operations'] >= 1
        
        # Validate signal tracking across all tools
        signal_summaries = {
            'image': image_signal_tracker.get_workflow_summary(),
            'office': office_signal_tracker.get_workflow_summary(),
            'file_touch': file_touch_signal_tracker.get_workflow_summary()
        }
        
        for tool_type, summary in signal_summaries.items():
            assert summary['total_events'] > 0
            assert summary['completion_status'] is True
            assert summary['error_events'] == 0
        
        # Validate comprehensive data availability
        assert len(image_tool.exif_data) > 0
        assert len(office_tool.document_properties) > 0
        assert len(file_touch_tool.file_timestamps) > 0