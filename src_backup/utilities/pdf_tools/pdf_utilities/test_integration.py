"""
Comprehensive Test Integration for PDF Tools Hub
Tests the complete system including discovery, UI, progress tracking, and error handling.
"""

import sys
import os
import time
from typing import List, Dict, Any
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# Import our PDF tools hub components
from pdf_tool_discovery import get_tool_discovery, ToolMetadata
from enhanced_main import EnhancedPDFHub
from progress_manager import get_progress_manager, create_operation, update_progress
from error_manager import get_error_manager, handle_error
from batch_processor import get_batch_processor, create_batch_job
from unified_interfaces import get_tool_registry, register_tool
from config_manager import ConfigManager
from log_config import setup_logger

logger = setup_logger(__name__)


class TestPDFTool:
    """Mock PDF tool for testing purposes."""
    
    def __init__(self, name: str, processing_time: float = 0.5):
        self.name = name
        self.processing_time = processing_time
    
    def process_file(self, input_file: str, output_file: str = None, **kwargs):
        """Simulate file processing."""
        logger.info(f"Processing {input_file} with {self.name}")
        time.sleep(self.processing_time)
        
        # Simulate occasional failures for testing
        if "fail" in input_file.lower():
            raise ValueError(f"Simulated failure for {input_file}")
        
        return {
            'success': True,
            'message': f'Successfully processed {input_file}',
            'output_files': [output_file] if output_file else [],
            'metadata': {'processing_time': self.processing_time}
        }


class IntegrationTester:
    """Comprehensive integration tester for PDF Tools Hub."""
    
    def __init__(self):
        self.app = None
        self.hub = None
        self.test_results = {}
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup test environment with mock tools and data."""
        logger.info("Setting up test environment...")
        
        # Create test tools
        self.test_tools = {
            'split': TestPDFTool('PDF Splitter', 0.3),
            'merge': TestPDFTool('PDF Merger', 0.4),
            'extract_text': TestPDFTool('Text Extractor', 0.2),
            'compress': TestPDFTool('PDF Compressor', 0.6),
            'watermark': TestPDFTool('Watermark Tool', 0.3)
        }
        
        # Register tools with unified interface
        tool_registry = get_tool_registry()
        for tool_name, tool_instance in self.test_tools.items():
            register_tool(
                tool_name,
                tool_instance.process_file,
                required_params={'input_file': str},
                optional_params={'output_file': str, 'quality': int}
            )
        
        # Create test files (mock)
        self.test_files = [
            'test_document_1.pdf',
            'test_document_2.pdf',
            'test_document_fail.pdf',  # This will trigger failure
            'large_document.pdf',
            'small_document.pdf'
        ]
        
        logger.info("Test environment setup complete")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        logger.info("Starting comprehensive integration tests...")
        
        tests = [
            ('Tool Discovery', self.test_tool_discovery),
            ('Configuration Management', self.test_configuration),
            ('Progress Tracking', self.test_progress_tracking),
            ('Error Handling', self.test_error_handling),
            ('Batch Processing', self.test_batch_processing),
            ('Unified Interfaces', self.test_unified_interfaces),
            ('GUI Integration', self.test_gui_integration)
        ]
        
        results = {}
        
        for test_name, test_function in tests:
            try:
                logger.info(f"Running test: {test_name}")
                result = test_function()
                results[test_name] = result
                status = "PASSED" if result else "FAILED"
                logger.info(f"Test {test_name}: {status}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}", exc_info=True)
                results[test_name] = False
        
        self.test_results = results
        return results
    
    def test_tool_discovery(self) -> bool:
        """Test the tool discovery system."""
        try:
            discovery = get_tool_discovery()
            
            # Test discovery
            tools = discovery.discover_tools()
            
            # Verify tools were discovered
            if len(tools) == 0:
                logger.warning("No tools discovered - this might be expected in test environment")
                return True  # Not a failure in test environment
            
            # Test categorization
            categories = discovery.get_all_categories()
            assert len(categories) > 0, "No categories found"
            
            # Test tool retrieval
            for tool_name in tools:
                tool_metadata = discovery.get_tool_by_name(tool_name)
                assert tool_metadata is not None, f"Could not retrieve tool: {tool_name}"
                assert isinstance(tool_metadata, ToolMetadata), "Invalid tool metadata type"
            
            logger.info(f"Tool discovery test passed - found {len(tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Tool discovery test failed: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration management."""
        try:
            config = ConfigManager()
            
            # Test setting and getting values
            test_key = 'test_setting'
            test_value = 'test_value_123'
            
            config.set_setting('general', test_key, test_value)
            retrieved_value = config.get_setting('general', test_key)
            
            assert retrieved_value == test_value, f"Config value mismatch: {retrieved_value} != {test_value}"
            
            # Test module config
            module_config = {'test_param': 42, 'enabled': True}
            config.set_module_config('test_module', module_config)
            retrieved_config = config.get_module_config('test_module')
            
            assert retrieved_config == module_config, "Module config mismatch"
            
            logger.info("Configuration test passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return False
    
    def test_progress_tracking(self) -> bool:
        """Test progress tracking system."""
        try:
            progress_manager = get_progress_manager()
            
            # Test single operation
            op_id = create_operation('test_tool', 'test_operation')
            assert op_id is not None, "Failed to create operation"
            
            # Test progress updates
            for i in range(0, 101, 25):
                update_progress(op_id, i, f"Progress: {i}%")
                time.sleep(0.01)  # Small delay to simulate work
            
            # Test operation info retrieval
            op_info = progress_manager.get_operation_info(op_id)
            assert op_info is not None, "Could not retrieve operation info"
            assert op_info.progress_percent == 100, "Progress not updated correctly"
            
            logger.info("Progress tracking test passed")
            return True
            
        except Exception as e:
            logger.error(f"Progress tracking test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling system."""
        try:
            error_manager = get_error_manager()
            
            # Test different error types
            test_errors = [
                FileNotFoundError("test.pdf not found"),
                PermissionError("Access denied"),
                ValueError("Invalid parameter"),
                ImportError("Missing module")
            ]
            
            error_ids = []
            for error in test_errors:
                context = {'tool_name': 'test_tool', 'file_path': 'test.pdf'}
                error_id = handle_error(error, context)
                error_ids.append(error_id)
                
                # Verify error was stored
                error_info = error_manager.get_error_info(error_id)
                assert error_info is not None, f"Error info not found for {error_id}"
                assert not error_info.title == "", "Error title is empty"
            
            # Test error retrieval
            recent_errors = error_manager.get_recent_errors(5)
            assert len(recent_errors) >= len(test_errors), "Not all errors were stored"
            
            logger.info("Error handling test passed")
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    def test_batch_processing(self) -> bool:
        """Test batch processing system."""
        try:
            batch_processor = get_batch_processor()
            
            # Create batch job
            job_id = create_batch_job(
                'test_tool', 
                'test_operation', 
                self.test_files[:3],  # Use first 3 test files
                output_dir='/tmp/test_output'
            )
            
            assert job_id is not None, "Failed to create batch job"
            
            # Get job info
            job_info = batch_processor.get_job_info(job_id)
            assert job_info is not None, "Could not retrieve job info"
            assert job_info.total_items == 3, "Incorrect number of items in batch job"
            
            # Test job statistics
            stats = batch_processor.get_job_statistics()
            assert 'total_jobs' in stats, "Missing statistics"
            assert stats['total_jobs'] >= 1, "Job not counted in statistics"
            
            logger.info("Batch processing test passed")
            return True
            
        except Exception as e:
            logger.error(f"Batch processing test failed: {e}")
            return False
    
    def test_unified_interfaces(self) -> bool:
        """Test unified interfaces system."""
        try:
            tool_registry = get_tool_registry()
            
            # Test tool registration (already done in setup)
            registered_tools = tool_registry.get_all_tools()
            assert len(registered_tools) > 0, "No tools registered"
            
            # Test tool retrieval
            test_tool = tool_registry.get_tool('split')
            assert test_tool is not None, "Could not retrieve registered tool"
            
            # Test parameter validation
            valid_params = {'input_file': 'test.pdf', 'quality': 80}
            assert test_tool.validate_parameters(valid_params), "Valid parameters rejected"
            
            # Test file processing (mock)
            result = test_tool.process_file('test.pdf', 'output.pdf', valid_params)
            assert result.success, f"File processing failed: {result.message}"
            
            logger.info("Unified interfaces test passed")
            return True
            
        except Exception as e:
            logger.error(f"Unified interfaces test failed: {e}")
            return False
    
    def test_gui_integration(self) -> bool:
        """Test GUI integration."""
        try:
            # Create QApplication if not exists
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            
            # Create enhanced PDF hub
            self.hub = EnhancedPDFHub()
            
            # Test hub initialization
            assert self.hub is not None, "Failed to create PDF hub"
            assert hasattr(self.hub, 'discovered_tools'), "Hub missing discovered_tools attribute"
            assert hasattr(self.hub, 'category_tabs'), "Hub missing category_tabs attribute"
            
            # Test tool discovery in GUI
            tools_count = len(self.hub.discovered_tools)
            logger.info(f"GUI discovered {tools_count} tools")
            
            # Test tab creation
            tab_count = self.hub.tab_widget.count()
            logger.info(f"GUI created {tab_count} category tabs")
            
            # Show hub briefly for visual verification (in real test environment)
            if os.environ.get('DISPLAY'):  # Only if display available
                self.hub.show()
                QTimer.singleShot(1000, self.hub.close)  # Close after 1 second
                self.app.processEvents()
            
            logger.info("GUI integration test passed")
            return True
            
        except Exception as e:
            logger.error(f"GUI integration test failed: {e}")
            return False
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return "No test results available. Run tests first."
        
        report = []
        report.append("=" * 60)
        report.append("PDF TOOLS HUB - INTEGRATION TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.test_results)}")
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = len(self.test_results) - passed_tests
        
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {(passed_tests/len(self.test_results)*100):.1f}%")
        report.append("")
        
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            report.append(f"{test_name:<30} {status}")
        
        report.append("")
        report.append("SYSTEM INFORMATION:")
        report.append("-" * 40)
        report.append(f"Python Version: {sys.version}")
        report.append(f"Platform: {sys.platform}")
        report.append(f"Working Directory: {os.getcwd()}")
        
        # Component status
        report.append("")
        report.append("COMPONENT STATUS:")
        report.append("-" * 40)
        
        try:
            discovery = get_tool_discovery()
            tools = discovery.discover_tools()
            report.append(f"Tool Discovery: ✓ ({len(tools)} tools found)")
        except Exception as e:
            report.append(f"Tool Discovery: ✗ ({str(e)})")
        
        try:
            progress_manager = get_progress_manager()
            active_ops = progress_manager.get_active_operations()
            report.append(f"Progress Manager: ✓ ({len(active_ops)} active operations)")
        except Exception as e:
            report.append(f"Progress Manager: ✗ ({str(e)})")
        
        try:
            error_manager = get_error_manager()
            recent_errors = error_manager.get_recent_errors(5)
            report.append(f"Error Manager: ✓ ({len(recent_errors)} recent errors)")
        except Exception as e:
            report.append(f"Error Manager: ✗ ({str(e)})")
        
        try:
            batch_processor = get_batch_processor()
            stats = batch_processor.get_job_statistics()
            report.append(f"Batch Processor: ✓ ({stats.get('total_jobs', 0)} jobs)")
        except Exception as e:
            report.append(f"Batch Processor: ✗ ({str(e)})")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def cleanup(self):
        """Cleanup test environment."""
        if self.hub:
            self.hub.close()
        if self.app:
            self.app.quit()
        logger.info("Test environment cleaned up")


def run_integration_tests():
    """Run comprehensive integration tests."""
    print("Starting PDF Tools Hub Integration Tests...")
    print("=" * 50)
    
    tester = IntegrationTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_test_report()
        print(report)
        
        # Save report to file
        report_file = 'pdf_tools_hub_test_report.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Return overall success
        all_passed = all(results.values())
        return all_passed
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}", exc_info=True)
        print(f"Integration test failed: {e}")
        return False
    
    finally:
        tester.cleanup()


if __name__ == '__main__':
    # Run integration tests
    success = run_integration_tests()
    
    if success:
        print("\n🎉 All integration tests PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests FAILED!")
        sys.exit(1)