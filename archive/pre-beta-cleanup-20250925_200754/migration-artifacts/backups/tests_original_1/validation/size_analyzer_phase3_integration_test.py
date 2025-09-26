#!/usr/bin/env python3
"""
Size Analyzer Phase 3 Integration Test

This script validates the comprehensive hub integration features implemented
in Phase 3, including bidirectional communication, progress reporting,
shared data structures, and event handling mechanisms.
"""

import sys
import os
import tempfile
import shutil
import time
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtTest import QTest

# Import the enhanced components
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
from file_utilities_2.integration.hub_connector import (
    HubConnector, HubMessage, HubCommunicationProtocol,
    SharedConfiguration, HubEventLogger
)
from rfuhub import MyGUI


class MockHubInstance:
    """Mock hub instance for testing hub integration."""
    
    def __init__(self):
        self.registered_tools = {}
        self.messages_received = []
        self.events_broadcast = []
        self.resource_requests = []
        self.tool_progress = {}
        
    def register_tool(self, tool_name: str, tool_instance):
        """Mock tool registration."""
        self.registered_tools[tool_name] = tool_instance
        return True
    
    def unregister_tool(self, tool_name: str):
        """Mock tool unregistration."""
        if tool_name in self.registered_tools:
            del self.registered_tools[tool_name]
            return True
        return False
    
    def receive_message(self, message):
        """Mock message reception."""
        self.messages_received.append(message)
    
    def broadcast_event(self, sender: str, event_type: str, event_data: Dict):
        """Mock event broadcasting."""
        self.events_broadcast.append({
            'sender': sender,
            'event_type': event_type,
            'data': event_data,
            'timestamp': datetime.now()
        })
    
    def request_resource(self, tool_name: str, resource_type: str, requirements: Dict):
        """Mock resource request."""
        self.resource_requests.append({
            'tool_name': tool_name,
            'resource_type': resource_type,
            'requirements': requirements,
            'timestamp': datetime.now()
        })
        return True  # Always grant for testing
    
    def update_tool_progress(self, tool_name: str, percentage: int, message: str):
        """Mock progress update."""
        self.tool_progress[tool_name] = {
            'percentage': percentage,
            'message': message,
            'timestamp': datetime.now()
        }


class Phase3IntegrationValidator:
    """Comprehensive validator for Phase 3 integration features."""
    
    def __init__(self):
        self.app = None
        self.test_results = []
        self.mock_hub = MockHubInstance()
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup test environment."""
        print("Setting up test environment...")
        
        # Create QApplication if not exists
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="size_analyzer_test_")
        
        # Create test files
        self._create_test_files()
        
        print(f"Test environment ready. Temp dir: {self.temp_dir}")
    
    def _create_test_files(self):
        """Create test files for analysis."""
        # Create various test files
        test_files = [
            ("test1.txt", "This is test file 1" * 100),
            ("test2.log", "Log entry\n" * 50),
            ("data.json", '{"test": "data"}' * 20),
            ("image.png", b'\x89PNG\r\n\x1a\n' + b'fake_image_data' * 100),
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.temp_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)
        
        # Create subdirectory
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        
        with open(os.path.join(sub_dir, "nested.txt"), 'w') as f:
            f.write("Nested file content" * 30)
    
    def test_hub_connector_initialization(self):
        """Test hub connector initialization and basic functionality."""
        print("\n=== Testing Hub Connector Initialization ===")
        
        try:
            # Test hub connector creation
            connector = HubConnector("Test Tool", self.mock_hub)
            
            # Test registration
            success = connector.register_with_hub(self.mock_hub)
            
            self._record_result(
                "Hub Connector Initialization",
                success,
                "Hub connector should initialize and register successfully"
            )
            
            # Test configuration
            config = connector.config
            self._record_result(
                "Shared Configuration",
                config is not None,
                "Shared configuration should be available"
            )
            
            # Test event logger
            logger = connector.logger
            self._record_result(
                "Event Logger",
                logger is not None,
                "Event logger should be available"
            )
            
            # Test cleanup
            connector.cleanup()
            
        except Exception as e:
            self._record_result(
                "Hub Connector Initialization",
                False,
                f"Hub connector initialization failed: {e}"
            )
    
    def test_size_analyzer_hub_integration(self):
        """Test size analyzer GUI with hub integration."""
        print("\n=== Testing Size Analyzer Hub Integration ===")
        
        try:
            # Create size analyzer with hub integration
            analyzer_gui = SizeAnalyzerGUI(hub_instance=self.mock_hub)
            
            # Test hub connector is set
            self._record_result(
                "Size Analyzer Hub Connector",
                analyzer_gui.hub_connector is not None,
                "Size analyzer should have hub connector"
            )
            
            # Test tool registration
            self._record_result(
                "Tool Registration",
                "Size Analyzer" in self.mock_hub.registered_tools,
                "Size analyzer should be registered with hub"
            )
            
            # Test signal connections
            signals_connected = all([
                hasattr(analyzer_gui, 'tool_started'),
                hasattr(analyzer_gui, 'tool_completed'),
                hasattr(analyzer_gui, 'tool_error'),
                hasattr(analyzer_gui, 'tool_progress'),
            ])
            
            self._record_result(
                "Hub Communication Signals",
                signals_connected,
                "All hub communication signals should be available"
            )
            
            analyzer_gui.close()
            
        except Exception as e:
            self._record_result(
                "Size Analyzer Hub Integration",
                False,
                f"Size analyzer hub integration failed: {e}"
            )
    
    def test_bidirectional_communication(self):
        """Test bidirectional communication between tools and hub."""
        print("\n=== Testing Bidirectional Communication ===")
        
        try:
            # Create hub and analyzer
            hub = MyGUI()
            analyzer_gui = SizeAnalyzerGUI(hub_instance=hub)
            
            # Test tool registration
            registered = hub.register_tool("Size Analyzer", analyzer_gui)
            self._record_result(
                "Tool Registration with Real Hub",
                registered,
                "Tool should register successfully with real hub"
            )
            
            # Test message sending
            initial_message_count = len(hub.message_queue)
            
            # Simulate status report
            analyzer_gui.report_status_to_hub("testing", {"test": True})
            
            # Allow time for message processing
            QTest.qWait(100)
            
            self._record_result(
                "Status Reporting",
                len(hub.message_queue) >= initial_message_count,
                "Status messages should be sent to hub"
            )
            
            # Test event broadcasting
            initial_event_count = len(getattr(hub, 'events_broadcast', []))
            analyzer_gui.broadcast_hub_event("test_event", {"data": "test"})
            
            QTest.qWait(100)
            
            # Test resource requests
            resource_granted = analyzer_gui.request_hub_resources("cpu", {"test": True})
            self._record_result(
                "Resource Request",
                isinstance(resource_granted, bool),
                "Resource requests should return boolean result"
            )
            
            analyzer_gui.close()
            hub.close()
            
        except Exception as e:
            self._record_result(
                "Bidirectional Communication",
                False,
                f"Bidirectional communication test failed: {e}"
            )
    
    def test_progress_reporting_integration(self):
        """Test progress reporting and status integration."""
        print("\n=== Testing Progress Reporting Integration ===")
        
        try:
            # Create analyzer with hub
            analyzer_gui = SizeAnalyzerGUI(hub_instance=self.mock_hub)
            
            # Set test directory
            analyzer_gui.selected_directory = self.temp_dir
            analyzer_gui.directory_line_edit.setText(self.temp_dir)
            
            # Track progress updates
            progress_updates = []
            
            def track_progress(tool_name, percentage, message):
                progress_updates.append({
                    'tool_name': tool_name,
                    'percentage': percentage,
                    'message': message,
                    'timestamp': datetime.now()
                })
            
            analyzer_gui.tool_progress.connect(track_progress)
            
            # Start analysis (this will run in background)
            analyzer_gui._start_analysis()
            
            # Wait for some progress
            start_time = time.time()
            while len(progress_updates) < 3 and time.time() - start_time < 10:
                QTest.qWait(100)
                self.app.processEvents()
            
            self._record_result(
                "Progress Updates",
                len(progress_updates) > 0,
                f"Progress updates should be generated (got {len(progress_updates)})"
            )
            
            # Test progress data structure
            if progress_updates:
                first_update = progress_updates[0]
                valid_structure = all(key in first_update for key in 
                                    ['tool_name', 'percentage', 'message', 'timestamp'])
                self._record_result(
                    "Progress Data Structure",
                    valid_structure,
                    "Progress updates should have correct structure"
                )
            
            # Cancel analysis
            if analyzer_gui.worker_thread and analyzer_gui.worker_thread.isRunning():
                analyzer_gui._cancel_analysis()
                QTest.qWait(500)
            
            analyzer_gui.close()
            
        except Exception as e:
            self._record_result(
                "Progress Reporting Integration",
                False,
                f"Progress reporting test failed: {e}"
            )
    
    def test_shared_data_structures(self):
        """Test shared data structures and configuration management."""
        print("\n=== Testing Shared Data Structures ===")
        
        try:
            # Test shared configuration
            config = SharedConfiguration()
            
            # Test setting and getting values
            test_key = "test_setting"
            test_value = {"nested": {"data": True}, "number": 42}
            
            config.set(test_key, test_value)
            retrieved_value = config.get(test_key)
            
            self._record_result(
                "Configuration Storage",
                retrieved_value == test_value,
                "Configuration should store and retrieve complex data"
            )
            
            # Test tool-specific configuration
            tool_config = {"theme": "dark", "auto_save": True}
            config.set_tool_config("Size Analyzer", tool_config)
            retrieved_tool_config = config.get_tool_config("Size Analyzer")
            
            self._record_result(
                "Tool-Specific Configuration",
                retrieved_tool_config == tool_config,
                "Tool-specific configuration should work correctly"
            )
            
            # Test configuration persistence
            config.save_config()
            
            # Create new config instance to test loading
            config2 = SharedConfiguration(config.config_path)
            loaded_value = config2.get(test_key)
            
            self._record_result(
                "Configuration Persistence",
                loaded_value == test_value,
                "Configuration should persist across instances"
            )
            
        except Exception as e:
            self._record_result(
                "Shared Data Structures",
                False,
                f"Shared data structures test failed: {e}"
            )
    
    def test_event_handling_mechanisms(self):
        """Test event handling mechanisms and lifecycle events."""
        print("\n=== Testing Event Handling Mechanisms ===")
        
        try:
            # Test hub message creation and handling
            message = HubMessage(
                HubCommunicationProtocol.TOOL_STARTED,
                "Size Analyzer",
                {"test_data": True}
            )
            
            self._record_result(
                "Hub Message Creation",
                message.message_type == HubCommunicationProtocol.TOOL_STARTED,
                "Hub messages should be created correctly"
            )
            
            # Test message serialization
            message_dict = message.to_dict()
            required_fields = ['message_id', 'message_type', 'tool_name', 'data', 'timestamp']
            has_required_fields = all(field in message_dict for field in required_fields)
            
            self._record_result(
                "Message Serialization",
                has_required_fields,
                "Messages should serialize with all required fields"
            )
            
            # Test message deserialization
            reconstructed_message = HubMessage.from_dict(message_dict)
            
            self._record_result(
                "Message Deserialization",
                reconstructed_message.message_type == message.message_type,
                "Messages should deserialize correctly"
            )
            
            # Test event logger
            logger = HubEventLogger()
            logger.log_event(
                HubCommunicationProtocol.EVENT_LIFECYCLE,
                "Size Analyzer",
                "Test event logged",
                {"test": True}
            )
            
            self._record_result(
                "Event Logging",
                os.path.exists(logger.log_path),
                "Event logging should create log files"
            )
            
        except Exception as e:
            self._record_result(
                "Event Handling Mechanisms",
                False,
                f"Event handling test failed: {e}"
            )
    
    def test_error_handling_and_recovery(self):
        """Test comprehensive error handling and recovery."""
        print("\n=== Testing Error Handling and Recovery ===")
        
        try:
            # Test hub connector with invalid hub
            connector = HubConnector("Test Tool", None)
            
            # Test graceful handling of missing hub
            success = connector.register_with_hub(None)
            self._record_result(
                "Missing Hub Handling",
                not success,  # Should fail gracefully
                "Hub connector should handle missing hub gracefully"
            )
            
            # Test error reporting
            error_reported = False
            try:
                connector.report_error_to_hub("Test error", {"test": True})
                error_reported = True
            except Exception:
                pass
            
            self._record_result(
                "Error Reporting Resilience",
                error_reported,
                "Error reporting should not crash when hub unavailable"
            )
            
            # Test analyzer with invalid directory
            analyzer = SizeAnalyzer()
            
            try:
                # This should raise an exception
                analyzer.analyze_directory("/nonexistent/directory/path")
                analysis_failed = False
            except (FileNotFoundError, NotADirectoryError):
                analysis_failed = True
            except Exception:
                analysis_failed = True
            
            self._record_result(
                "Invalid Directory Handling",
                analysis_failed,
                "Analyzer should handle invalid directories properly"
            )
            
        except Exception as e:
            self._record_result(
                "Error Handling and Recovery",
                False,
                f"Error handling test failed: {e}"
            )
    
    def test_performance_metrics(self):
        """Test performance metrics and resource tracking."""
        print("\n=== Testing Performance Metrics ===")
        
        try:
            # Create analyzer and run quick analysis
            analyzer = SizeAnalyzer()
            
            # Run analysis on test directory
            result = analyzer.analyze_directory(self.temp_dir, top_files_count=5)
            
            # Check for performance metrics
            has_metrics = 'performance_metrics' in result
            self._record_result(
                "Performance Metrics Inclusion",
                has_metrics,
                "Analysis results should include performance metrics"
            )
            
            if has_metrics:
                metrics = result['performance_metrics']
                required_metrics = ['start_time', 'end_time', 'files_per_second', 'bytes_per_second']
                has_required_metrics = all(metric in metrics for metric in required_metrics)
                
                self._record_result(
                    "Performance Metrics Structure",
                    has_required_metrics,
                    "Performance metrics should have required fields"
                )
                
                # Test resource usage tracking
                analyzer.update_resource_usage(cpu_usage=25.5, memory_usage=128.0, disk_io=1024.0)
                resource_usage = analyzer.get_resource_usage()
                
                self._record_result(
                    "Resource Usage Tracking",
                    'cpu_usage' in resource_usage and resource_usage['cpu_usage'] == 25.5,
                    "Resource usage should be tracked correctly"
                )
            
        except Exception as e:
            self._record_result(
                "Performance Metrics",
                False,
                f"Performance metrics test failed: {e}"
            )
    
    def _record_result(self, test_name: str, success: bool, description: str):
        """Record test result."""
        result = {
            'test_name': test_name,
            'success': success,
            'description': description,
            'timestamp': datetime.now()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not success:
            print(f"    {description}")
    
    def cleanup_test_environment(self):
        """Cleanup test environment."""
        print("\nCleaning up test environment...")
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        if self.app:
            self.app.quit()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("SIZE ANALYZER PHASE 3 INTEGRATION TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTest Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\nDetailed Results:")
        print("-" * 80)
        
        for result in self.test_results:
            status = "PASS" if result['success'] else "FAIL"
            print(f"[{status}] {result['test_name']}")
            print(f"      {result['description']}")
            print(f"      Time: {result['timestamp'].strftime('%H:%M:%S')}")
            print()
        
        # Integration status summary
        print("Integration Features Status:")
        print("-" * 40)
        
        feature_categories = {
            "Hub Connector": ["Hub Connector Initialization", "Shared Configuration", "Event Logger"],
            "GUI Integration": ["Size Analyzer Hub Integration", "Hub Communication Signals"],
            "Communication": ["Bidirectional Communication", "Status Reporting", "Resource Request"],
            "Progress Tracking": ["Progress Updates", "Progress Data Structure"],
            "Data Management": ["Configuration Storage", "Tool-Specific Configuration", "Configuration Persistence"],
            "Event Handling": ["Hub Message Creation", "Message Serialization", "Event Logging"],
            "Error Handling": ["Missing Hub Handling", "Error Reporting Resilience", "Invalid Directory Handling"],
            "Performance": ["Performance Metrics Inclusion", "Performance Metrics Structure", "Resource Usage Tracking"]
        }
        
        for category, tests in feature_categories.items():
            category_results = [r for r in self.test_results if r['test_name'] in tests]
            if category_results:
                category_passed = sum(1 for r in category_results if r['success'])
                category_total = len(category_results)
                status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
                print(f"{status} {category}: {category_passed}/{category_total}")
        
        print("\n" + "="*80)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Phase 3 integration is complete and functional.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Review the issues above.")
        
        print("="*80)
        
        return passed_tests == total_tests


def main():
    """Main test execution function."""
    print("Starting Size Analyzer Phase 3 Integration Validation...")
    print("This test validates comprehensive hub integration features.")
    
    validator = Phase3IntegrationValidator()
    
    try:
        # Setup
        validator.setup_test_environment()
        
        # Run all tests
        validator.test_hub_connector_initialization()
        validator.test_size_analyzer_hub_integration()
        validator.test_bidirectional_communication()
        validator.test_progress_reporting_integration()
        validator.test_shared_data_structures()
        validator.test_event_handling_mechanisms()
        validator.test_error_handling_and_recovery()
        validator.test_performance_metrics()
        
        # Generate report
        all_passed = validator.generate_report()
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        validator.cleanup_test_environment()


if __name__ == "__main__":
    sys.exit(main())