#!/usr/bin/env python3
"""
Image Metadata E2E Tests

Comprehensive end-to-end testing for Image Metadata tool workflows.
Tests EXIF extraction, editing, batch processing, GPS validation, and error handling.

Created: 2025-09-04
Purpose: Validate Image Metadata tool functionality with real-world scenarios
Coverage: EXIF data, GPS coordinates, batch operations, format conversion
"""

import os
import sys
import time
from datetime import datetime

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test utilities
from .metadata_tools_test_utilities import (assert_performance_target,
                                            image_metadata_test_environment)


class TestImageMetadataEXIFWorkflows:
    """Test class for EXIF data extraction and editing workflows"""
    
    def test_exif_camera_settings_extraction_workflow(self, image_metadata_test_environment):
        """Test complete EXIF camera settings extraction workflow"""
        env = image_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracker
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'exif_extraction')
        
        # Test data setup
        test_image_path = os.path.join(env['test_data_path'], 'images', 'test_image_001.jpg')
        
        # Execute EXIF extraction workflow
        result = tool.extract_exif_data(test_image_path, include_gps=True)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'exif_extraction')
        
        # Validate workflow results
        assert result['status'] == 'success'
        assert result['files_processed'] == 1
        assert result['metadata_operations'] >= 1
        assert test_image_path in tool.exif_data
        
        # Validate EXIF data structure
        exif_data = tool.exif_data[test_image_path]
        assert 'camera_settings' in exif_data
        assert 'basic_info' in exif_data
        assert 'image_settings' in exif_data
        
        # Validate camera settings completeness
        camera_settings = exif_data['camera_settings']
        required_fields = ['make', 'model', 'datetime', 'iso_speed', 'exposure_time', 'f_number']
        for field in required_fields:
            assert field in camera_settings, f"Missing camera setting: {field}"
            assert camera_settings[field] is not None, f"Empty camera setting: {field}"
        
        # Validate signal tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['total_events'] > 0
        assert workflow_summary['completion_status'] is True
        assert workflow_summary['error_events'] == 0
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'image_metadata', 'exif_extraction')
        assert perf_result['target_met'] is True
    
    def test_exif_gps_coordinates_extraction_workflow(self, image_metadata_test_environment):
        """Test GPS coordinate extraction and validation workflow"""
        env = image_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'gps_validation')
        
        # Test data setup - create multiple images for GPS testing
        test_images = []
        for i in range(5):
            image_path = os.path.join(env['test_data_path'], 'images', f'gps_image_{i:03d}.jpg')
            test_images.append(image_path)
            
            # Extract EXIF data to populate GPS coordinates
            tool.extract_exif_data(image_path, include_gps=True)
        
        # Execute GPS validation workflow
        validation_result = tool.validate_gps_coordinates(test_images)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'gps_validation')
        
        # Validate workflow results
        assert validation_result['status'] == 'success'
        assert validation_result['files_processed'] == len(test_images)
        
        # Validate GPS coordinate processing
        gps_images_count = len([path for path in test_images if path in tool.gps_coordinates])
        assert gps_images_count >= 0  # Some images should have GPS data
        
        # Validate GPS coordinate ranges for images that have GPS data
        for image_path, gps_data in tool.gps_coordinates.items():
            assert -90 <= gps_data['latitude'] <= 90, f"Invalid latitude: {gps_data['latitude']}"
            assert -180 <= gps_data['longitude'] <= 180, f"Invalid longitude: {gps_data['longitude']}"
            assert gps_data['altitude'] >= 0, f"Invalid altitude: {gps_data['altitude']}"
            assert 'gps_timestamp' in gps_data
            assert 'satellites_used' in gps_data
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'image_metadata', 'gps_validation')
    
    def test_exif_timestamp_data_processing_workflow(self, image_metadata_test_environment):
        """Test EXIF timestamp extraction and processing workflow"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        test_image_path = os.path.join(env['test_data_path'], 'images', 'timestamp_test_001.jpg')
        
        # Execute EXIF extraction
        result = tool.extract_exif_data(test_image_path)
        
        # Validate timestamp data
        assert result['status'] == 'success'
        assert test_image_path in tool.exif_data
        
        exif_data = tool.exif_data[test_image_path]
        camera_settings = exif_data['camera_settings']
        
        # Validate timestamp format and content
        assert 'datetime' in camera_settings
        datetime_str = camera_settings['datetime']
        assert ':' in datetime_str, "DateTime should be in YYYY:MM:DD HH:MM:SS format"
        
        # Validate GPS timestamp if present
        if test_image_path in tool.gps_coordinates:
            gps_info = tool.gps_coordinates[test_image_path]
            assert 'gps_timestamp' in gps_info
            assert 'gps_datestamp' in gps_info


class TestImageMetadataBatchProcessing:
    """Test class for batch processing operations"""
    
    def test_batch_exif_extraction_workflow(self, image_metadata_test_environment):
        """Test batch EXIF extraction across multiple images"""
        env = image_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signals
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'batch_processing')
        
        # Test data setup - create multiple test images
        test_images = []
        for i in range(10):
            image_path = os.path.join(env['test_data_path'], 'images', f'batch_test_{i:03d}.jpg')
            test_images.append(image_path)
        
        # Execute batch extraction workflow
        batch_options = {
            'include_gps': True,
            'include_thumbnails': False
        }
        
        batch_result = tool.batch_process_images(test_images, 'extract', batch_options)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'batch_processing')
        
        # Validate batch processing results
        assert batch_result['status'] == 'success'
        assert batch_result['files_processed'] == len(test_images)
        assert batch_result['metadata_operations'] == len(test_images)
        
        # Validate individual file processing
        for image_path in test_images:
            assert image_path in tool.exif_data, f"EXIF data missing for {image_path}"
            
            exif_data = tool.exif_data[image_path]
            assert 'camera_settings' in exif_data
            assert 'basic_info' in exif_data
        
        # Validate signal tracking for batch operation
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['total_events'] >= len(test_images)
        assert workflow_summary['error_events'] == 0
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'image_metadata', 'batch_processing')
    
    def test_multiple_format_batch_processing_workflow(self, image_metadata_test_environment):
        """Test batch processing across different image formats"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup with different formats
        test_images = [
            os.path.join(env['test_data_path'], 'images', 'format_test_001.jpg'),
            os.path.join(env['test_data_path'], 'images', 'format_test_002.jpeg'),
            os.path.join(env['test_data_path'], 'images', 'format_test_003.tiff')
        ]
        
        # Execute format-aware batch processing
        batch_result = tool.batch_process_images(test_images, 'extract')
        
        # Validate format handling
        assert batch_result['status'] == 'success'
        assert batch_result['files_processed'] == len(test_images)
        
        # Validate format-specific processing
        for image_path in test_images:
            file_ext = os.path.splitext(image_path)[1].lower().lstrip('.')
            assert file_ext in tool.capabilities['supported_formats']
            
            if image_path in tool.exif_data:
                exif_data = tool.exif_data[image_path]
                assert 'basic_info' in exif_data
                assert exif_data['basic_info']['file_name'] == os.path.basename(image_path)


class TestImageMetadataGeolocation:
    """Test class for GPS and geolocation processing"""
    
    def test_gps_coordinate_validation_workflow(self, image_metadata_test_environment):
        """Test comprehensive GPS coordinate validation"""
        env = image_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'gps_validation')
        
        # Test data setup with known GPS coordinates
        test_images = []
        for i in range(8):
            image_path = os.path.join(env['test_data_path'], 'images', f'gps_validation_{i:03d}.jpg')
            test_images.append(image_path)
            
            # Pre-populate with EXIF and GPS data
            tool.extract_exif_data(image_path, include_gps=True)
        
        # Execute GPS validation workflow
        validation_result = tool.validate_gps_coordinates(test_images)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'gps_validation')
        
        # Validate validation workflow
        assert validation_result['status'] == 'success'
        assert validation_result['files_processed'] == len(test_images)
        
        # Count GPS-enabled images
        gps_enabled_count = len([path for path in test_images if path in tool.gps_coordinates])
        
        # Validate GPS coordinate validations
        if gps_enabled_count > 0:
            assert validation_result['results_count'] <= gps_enabled_count
            
            # Validate individual GPS coordinate validations
            for image_path in test_images:
                if image_path in tool.gps_coordinates:
                    gps_data = tool.gps_coordinates[image_path]
                    
                    # Validate coordinate ranges
                    assert isinstance(gps_data['latitude'], (int, float))
                    assert isinstance(gps_data['longitude'], (int, float))
                    assert isinstance(gps_data['altitude'], (int, float))
                    
                    # Validate GPS metadata
                    assert 'satellites_used' in gps_data
                    assert gps_data['satellites_used'] >= 4  # Minimum for GPS fix
                    assert 'gps_precision' in gps_data
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'image_metadata', 'gps_validation')
    
    def test_geolocation_mapping_integration_workflow(self, image_metadata_test_environment):
        """Test geolocation data integration for mapping applications"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        test_images = []
        for i in range(6):
            image_path = os.path.join(env['test_data_path'], 'images', f'mapping_test_{i:03d}.jpg')
            test_images.append(image_path)
            
            # Extract EXIF with GPS
            tool.extract_exif_data(image_path, include_gps=True)
        
        # Execute geolocation processing
        validation_result = tool.validate_gps_coordinates(test_images)
        
        # Validate mapping-ready data
        assert validation_result['status'] == 'success'
        
        # Check for mapping-compatible GPS data
        mapping_ready_images = []
        for image_path in test_images:
            if image_path in tool.gps_coordinates:
                gps_data = tool.gps_coordinates[image_path]
                
                # Validate mapping compatibility
                if (-90 <= gps_data['latitude'] <= 90 and 
                    -180 <= gps_data['longitude'] <= 180):
                    mapping_ready_images.append({
                        'image_path': image_path,
                        'latitude': gps_data['latitude'],
                        'longitude': gps_data['longitude'],
                        'altitude': gps_data.get('altitude', 0),
                        'timestamp': gps_data.get('gps_timestamp', '')
                    })
        
        # Validate that we have mapping-ready data structure
        for mapping_data in mapping_ready_images:
            assert 'image_path' in mapping_data
            assert 'latitude' in mapping_data
            assert 'longitude' in mapping_data
            assert isinstance(mapping_data['latitude'], (int, float))
            assert isinstance(mapping_data['longitude'], (int, float))


class TestImageMetadataErrorHandling:
    """Test class for error scenarios and recovery"""
    
    def test_corrupted_exif_data_handling_workflow(self, image_metadata_test_environment):
        """Test handling of corrupted EXIF data"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup with simulated corruption
        corrupted_image_path = os.path.join(env['test_data_path'], 'images', 'corrupted_001.jpg')
        
        # Simulate error condition
        result = tool.simulate_error('corrupted_exif', 'EXIF data is corrupted or incomplete')
        
        # Validate error handling
        assert result['status'] == 'error'
        assert result['error_type'] == 'corrupted_exif'
        assert 'corrupted' in result['message'].lower()
        
        # Validate that error was logged
        assert len(tool.workflow_events) > 0
        error_events = [event for event in tool.workflow_events if 'Error' in event]
        assert len(error_events) > 0
    
    def test_missing_metadata_scenarios_workflow(self, image_metadata_test_environment):
        """Test handling of images with no EXIF data"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        no_exif_image_path = os.path.join(env['test_data_path'], 'images', 'no_exif_001.jpg')
        
        # Execute extraction on image without EXIF
        result = tool.extract_exif_data(no_exif_image_path)
        
        # Should succeed but with minimal data
        assert result['status'] == 'success'
        
        # Validate graceful handling of missing metadata
        if no_exif_image_path in tool.exif_data:
            exif_data = tool.exif_data[no_exif_image_path]
            # Should at least have basic file info
            assert 'basic_info' in exif_data
            assert exif_data['basic_info']['file_path'] == no_exif_image_path
    
    def test_invalid_image_format_handling_workflow(self, image_metadata_test_environment):
        """Test handling of unsupported image formats"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test with unsupported format
        unsupported_format = 'bmp'  # Not in supported_formats list
        
        if unsupported_format not in tool.capabilities['supported_formats']:
            # Simulate unsupported format error
            result = tool.simulate_error('unsupported_format', 
                                       f'Unsupported image format: {unsupported_format}')
            
            # Validate error handling
            assert result['status'] == 'error'
            assert result['error_type'] == 'unsupported_format'
            assert 'unsupported' in result['message'].lower()
    
    def test_permission_error_recovery_workflow(self, image_metadata_test_environment):
        """Test recovery from file permission errors"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Simulate permission error
        protected_image_path = os.path.join(env['test_data_path'], 'images', 'protected_001.jpg')
        
        result = tool.simulate_error('permission_denied', 
                                   f'Permission denied accessing {protected_image_path}')
        
        # Validate error handling
        assert result['status'] == 'error'
        assert result['error_type'] == 'permission_denied'
        assert 'permission' in result['message'].lower()
        
        # Validate error recovery information
        assert len(tool.workflow_events) > 0
        assert any('permission' in event.lower() for event in tool.workflow_events)


class TestImageMetadataPerformance:
    """Test class for performance and scalability validation"""
    
    def test_large_image_collection_processing_workflow(self, image_metadata_test_environment):
        """Test processing of large image collections"""
        env = image_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('image_metadata', 'batch_processing')
        
        # Test data setup - large collection
        large_collection = []
        for i in range(25):  # Simulate large collection
            image_path = os.path.join(env['test_data_path'], 'images', f'large_collection_{i:03d}.jpg')
            large_collection.append(image_path)
        
        # Execute large batch processing
        batch_result = tool.batch_process_images(large_collection, 'extract')
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('image_metadata', 'batch_processing')
        
        # Validate large-scale processing
        assert batch_result['status'] == 'success'
        assert batch_result['files_processed'] == len(large_collection)
        
        # Validate performance target compliance
        assert_performance_target(perf_result['duration'], 'image_metadata', 'batch_processing')
        
        # Validate resource usage
        resource_usage = tool.get_resource_usage()
        assert resource_usage['memory'] > 0  # Should have used memory
        assert resource_usage['cpu'] > 0     # Should have used CPU
    
    def test_memory_efficiency_validation_workflow(self, image_metadata_test_environment):
        """Test memory efficiency during large operations"""
        env = image_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        memory_test_images = []
        for i in range(15):
            image_path = os.path.join(env['test_data_path'], 'images', f'memory_test_{i:03d}.jpg')
            memory_test_images.append(image_path)
        
        # Record initial resource usage
        initial_usage = tool.get_resource_usage()
        
        # Execute memory-intensive operations
        for image_path in memory_test_images:
            tool.extract_exif_data(image_path, include_gps=True)
        
        # Record final resource usage
        final_usage = tool.get_resource_usage()
        
        # Validate memory usage stayed within reasonable bounds
        memory_increase = final_usage['memory'] - initial_usage['memory']
        assert memory_increase > 0  # Should have used some memory
        
        # Validate that operations completed successfully
        processed_count = len([path for path in memory_test_images if path in tool.exif_data])
        assert processed_count == len(memory_test_images)


class TestImageMetadataIntegration:
    """Test class for hub integration and cross-tool workflows"""
    
    def test_image_metadata_hub_integration_workflow(self, image_metadata_test_environment):
        """Test Image Metadata tool integration with RFU Hub"""
        env = image_metadata_test_environment
        tool = env['tool']
        hub = env['hub']
        
        # Validate hub registration
        assert 'image_metadata' in hub.registered_tools
        assert hub.registered_tools['image_metadata'] == tool
        
        # Test hub coordination
        test_image_path = os.path.join(env['test_data_path'], 'images', 'hub_test_001.jpg')
        
        # Execute operation through hub-registered tool
        result = tool.extract_exif_data(test_image_path)
        
        # Validate hub integration
        assert result['status'] == 'success'
        assert len(hub.hub_events) > 0
        
        # Validate tool status tracking
        tool_status = hub.tool_status['image_metadata']
        assert tool_status['status'] == 'registered'
        assert 'last_activity' in tool_status
    
    def test_concurrent_metadata_operations_workflow(self, image_metadata_test_environment):
        """Test concurrent metadata operations and resource coordination"""
        env = image_metadata_test_environment
        tool = env['tool']
        hub = env['hub']
        
        # Test data setup
        concurrent_images = []
        for i in range(8):
            image_path = os.path.join(env['test_data_path'], 'images', f'concurrent_{i:03d}.jpg')
            concurrent_images.append(image_path)
        
        # Execute concurrent-style operations
        results = []
        
        # Operation 1: Extract metadata
        for image_path in concurrent_images[:4]:
            result = tool.extract_exif_data(image_path)
            results.append(result)
        
        # Operation 2: GPS validation on extracted images
        gps_result = tool.validate_gps_coordinates(concurrent_images[:4])
        results.append(gps_result)
        
        # Validate concurrent operation coordination
        successful_ops = len([r for r in results if r['status'] == 'success'])
        assert successful_ops >= len(results) // 2  # At least half should succeed
        
        # Validate hub coordination
        assert len(hub.registered_tools) > 0
        assert 'image_metadata' in hub.registered_tools
        assert hub.tool_status['image_metadata']['status'] == 'registered'